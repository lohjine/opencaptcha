import configparser
import logging
import os
from ipaddress import ip_network, ip_address
import time

token_length = 11
site_key_length = 10
site_secret_length = 18
challenge_id_length = 8

dirname = os.path.dirname(__file__)


def check_ip_in_lists(ip, db_connection, tor, blacklist, vpn):

    # if tor penalty check against tor
    if tor > 0:
        pass

    if blacklist > 0:
        pass

    if vpn > 0:
        pass

    return tor_hit, blacklist_hit, vpn_hit


def validate_settings_ini():

    if not os.path.exists(os.path.join(dirname, 'settings.ini')):
        raise ValueError('settings.ini file not found')

    config = configparser.ConfigParser()
    config.read(os.path.join(dirname, 'settings.ini'))

    if 'site' not in config:
        raise ValueError('site section missing')
    if 'url' not in config['site']:
        raise ValueError('site - url missing')

    if 'db' not in config:
        raise ValueError('db section missing')

    if config['db'].get('type', None) not in ('sqlite', 'redis'):
        raise ValueError('db - type needs to be either sqlite or redis')

    if config['db']['type'] == 'redis':
        if 'redis' not in config:
            raise ValueError('redis section missing')

    if 'captcha' not in config:
        raise ValueError('captcha section missing')

    if config['captcha'].get('challenge_level', None) not in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']:
        raise ValueError('captcha - challenge_level must be from 1 to 10')

    if config['captcha'].get('tor_penalty', None) not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10']:
        raise ValueError('captcha - tor_penalty must be from 0 to 10')

    if config['captcha'].get('vpn_penalty', None) not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10']:
        raise ValueError('captcha - vpn_penalty must be from 0 to 10')

    if config['captcha'].get('ip_blacklist_penalty', None) not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10']:
        raise ValueError('captcha - ip_blacklist_penalty must be from 0 to 10')


class DBconnector:
    def __init__(self):

        config = configparser.ConfigParser()
        config.read(os.path.join(dirname, 'settings.ini'))

        self.db_type = config['db']['type']

        if self.db_type == 'sqlite':
            from sqlitedict import SqliteDict
            self.db_connection = SqliteDict(os.path.join(dirname, 'db/keyvalue.db'), autocommit=True, tablename='keyvalue')
        elif self.db_type == 'redis':
            import redis
            redis_ip = config['redis']['ip']
            redis_port = config['redis']['port']

            logging.debug('Connecting to Redis...')
            self.db_connection = redis.Redis(host=redis_ip, port=redis_port, decode_responses=True)
            try:
                self.db_connection.set(1, 2)
            except ConnectionError:
                logging.error('Cannot connect to Redis')
                print('Error: Cannot connect to Redis')
                raise
        else:
            raise ValueError(f"config db type has to be either sqlite or redis, was {config['db']['type']}")

    def set(self, key, value, expire=None):
        if self.db_type == 'sqlite':
            self.db_connection[key] = value
        elif self.db_type == 'redis':
            self.db_connection.hmset(key, value)
            if expire:
                self.db_connection.expire(key, expire)

    def get(self, key, default_return=None):
        if self.db_type == 'sqlite':
            return self.db_connection.get(key, default_return)
        elif self.db_type == 'redis':
            # different methods for different data types, we only store dicts so this is fine
            result = self.db_connection.hgetall(key)
            if len(result) == 0:
                return default_return
            else:
                return result

    def set_set(self, key, values):
        if self.db_type == 'sqlite':
            pass # really poor perf if keep passing to disk, bring it to memory, then need a flag to check if need to renew
        elif self.db_type == 'redis':
            self.db_connection.delete(key) # todo test delete blank!
            # race condition tbh..
            self.db_connection.sadd(key, values)
            # we can rewrite this as retrieve, get the diffs, do the subtract and add!!
            return True

    def set_exists(self, key, value):
        if self.db_type == 'sqlite':
            pass
        elif self.db_type == 'redis':
            return self.db_connection.sismember(key, value) # might want to combine into 1 lua call?
        # see https://stackoverflow.com/questions/31788068/redis-alternative-to-check-existence-of-multiple-values-in-a-set


    def delete_old_keys(self, time_limit):
        expire_time_limit = time.time() - 60*60 #pendulum.now().add(hours=-1)
        if self.db_type == 'sqlite':
            for token, token_details in self.db_connection.iteritems():
                if len(token) == token_length:
                    if token_details['expires'] > expire_time_limit:
                        del self.db_connection[token]
        elif self.db_type == 'redis':
            # we set keys to be expired by redis automatically
            pass

    def delete(self, key):
        if self.db_type == 'sqlite':
            del self.db_connection[key]
        elif self.db_type == 'redis':
            self.db_connection.delete(key)
