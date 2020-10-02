import configparser
import logging
import os
from ipaddress import ip_network, ip_address
import time
from glob import glob
import subprocess
import toml
from pydub import AudioSegment

token_length = 11
site_key_length = 10
site_secret_length = 18
challenge_id_length = 8

dirname = os.path.dirname(__file__)


def image_similarity_hash(im):
    """
    Calculates average hash as defined in http://www.hackerfactor.com/blog/index.php?/archives/432-Looks-Like-It.html

    Args:
        im (pillow.Image)

    Returns:
        list: hash consisting of list of booleans
    """

    im = im.resize((10, 10), resample=0)  # 10x10 to be more stricter in determine similarity, as measured during testing
    im = im.convert(mode='L')

    data = list(im.getdata())

    avg = sum(data) / len(data)

    image_hash = [i >= avg for i in data]

    return image_hash


def gen_toml_file(directory=os.path.join('challenges', '7', 'videos'), full_refresh=False, ffprobe_path=''):
    """
    Generates toml files for video files for challenge 7

    Args:
        directory (str): path for video files for challenge 7
        full_refresh (bool): If False, skips videos which already have a toml file
        ffprobe_path (str): path of ffprobe executable, blank string if already in path

    """

    all_files = glob(os.path.join(directory, '*'))

    toml_files = set([os.path.split(i)[-1][:-5] for i in all_files if i[-4:] == 'toml'])
    video_files = [i for i in all_files if i[-4:] != 'toml']

    files_processed = 0
    files_error = 0
    files_skipped = 0

    if ffprobe_path:
        ffprobe_path = os.path.join(ffprobe_path, 'ffprobe')
    else:
        ffprobe_path = 'ffprobe'

    for video in video_files:
        if not full_refresh and os.path.split(video)[-1] in toml_files:
            files_skipped += 1
            continue
        else:

            toml_filepath = video + '.toml'

            cmd_full = ffprobe_path + ' -select_streams v:0 ' + video

            try:
                output = subprocess.check_output(cmd_full, stderr=subprocess.STDOUT, shell=True)
                output = output.decode('utf-8').splitlines()
            except Exception as e:
                logging.error(f"Error with ffprobe command: {cmd_full}")
                logging.error(f"{e.output}")
                files_error += 1
                continue

            # parse output
            duration = None
            videofps = None
            resolution = None

            for i in output:
                if 'Duration: ' in i:
                    duration = i.split(',')[0].split(' ')[-1]
                    hour, minute, second = duration.split('.')[0].split(':')
                    duration = int(hour) * 60 * 60 + int(minute) * 60 + int(second) + int(duration.split('.')[-1]) / 100

                if 'Stream' in i and 'Video' in i:
                    videofps = float(i.split(' fps,')[0].split(', ')[-1])
                    resolution = [int(j) for j in i.split(' kb/s')[0].split(', ')[-2].split('x')]

            # format output into toml file
            video_details = {'filename': os.path.split(video)[-1],
                             'duration': duration,  # seconds
                             'videofps': videofps,
                             'resolution': resolution
                             }

            with open(toml_filepath, 'w') as f:
                _ = toml.dump(video_details, f)

            files_processed += 1

    logging.info('{files_processed} files processed. {files_error} files error. {files_skipped} files skipped.')

    return True


def check_ip_in_lists(ip, db_connection, penalties):
    """
    Does an optimized ip lookup with the db_connection. Applies only the maximum penalty.

    Args:
        ip (str): ip string
        db_connection (DBconnector obj)
        penalties (dict): Contains tor_penalty, vpn_penalty, blacklist_penalty keys with integer values

    Returns:
        :int: penalty_added
    """

    penalties = {'tor': int(penalties['tor_penalty']), 'vpn': int(penalties['vpn_penalty']), 'blacklist': int(penalties['ip_blacklist_penalty'])}

    penalties = sorted(penalties.items(), key=lambda x: x[1])
    # sort by penalty value to check in that order and perform early stopping

    penalty_added = 0

    for penalty_type, penalty_value in penalties:

        if penalty_value == 0:
            continue

        if penalty_type == 'tor':
            if db_connection.set_exists('tor_ips', ip):
                penalty_added = penalty_value

        elif penalty_type == 'blacklist':
            if db_connection.set_exists('blacklist_ips', ip):
                penalty_added = penalty_value
            elif db_connection.set_exists('blacklist_ips', '.'.join(ip.split('.')[:3])):
                penalty_added = penalty_value
            elif db_connection.set_exists('blacklist_ips', '.'.join(ip.split('.')[:2])):
                penalty_added = penalty_value

        elif penalty_type == 'vpn':
            if db_connection.set_exists('vpn_ips', ip):
                penalty_added = penalty_value
            elif db_connection.set_exists('vpn_ips', '.'.join(ip.split('.')[:3])):
                penalty_added = penalty_value
            elif db_connection.set_exists('vpn_ips', '.'.join(ip.split('.')[:2])):
                penalty_added = penalty_value

        if penalty_added > 0:
            break

    return penalty_added


def match_target_amplitude(sound, target_dBFS):
    change_in_dBFS = target_dBFS - sound.dBFS
    return sound.apply_gain(change_in_dBFS)


def normalize_audio_in_directory(directory, recursive=True, target_db=-24):
    """
    Normalizes all audio files in directory to target dB in-place.

    """
    audio_extensions = set(['mp3', 'wav', 'aac', 'ogg'])

    files = glob(directory, recursive=recursive)

    for file in files:
        if os.path.isfile(file):

            extension = os.path.split(file)[-1].split('.')[-1].lower()

            if extension in audio_extensions:

                sound = AudioSegment.from_file(file)

                if abs(sound.dBFS - target_db) > 0.2:  # only apply operation if significantly different from target_db
                    normalized_sound = match_target_amplitude(sound, target_db)
                    normalized_sound.export(file, format=extension)


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
            self.sets = {}
            self.sets_updated = {}
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

    def set_value(self, key, value):
        if self.db_type == 'sqlite':
            self.db_connection[key] = value
        elif self.db_type == 'redis':
            # anything that enters here becomes a string
            self.db_connection.set(key, value)

    def get_value(self, key, default_return=None):
        if self.db_type == 'sqlite':
            return self.db_connection.get(key, default_return)
        elif self.db_type == 'redis':
            result = self.db_connection.get(key)
            if result is None:
                return default_return
            else:
                return result

    def set_dict(self, key, value, expire=None):
        if self.db_type == 'sqlite':
            self.db_connection[key] = value
        elif self.db_type == 'redis':
            self.db_connection.hset(key, mapping=value)
            if expire:
                self.db_connection.expire(key, expire)

    def get_dict(self, key, default_return=None):
        if self.db_type == 'sqlite':
            return self.db_connection.get(key, default_return)
        elif self.db_type == 'redis':
            result = self.db_connection.hgetall(key)  # if this retrieves non-existent key? -> empty dict
            if len(result) == 0:
                return default_return
            else:
                return result

    def set_set(self, key, values):
        if self.db_type == 'sqlite':
            self.db_connection[key] = values
        elif self.db_type == 'redis':
            p = self.db_connection.pipeline()
            p.delete(key)
            p.sadd(key, *values)
            p.execute()
            return True

    def set_exists(self, key, value):
        if self.db_type == 'sqlite':
            # really poor perf if keep retrieving from disk to check
            # cache in memory, only check to confirm that cache is updated
            if key not in self.sets:
                self.sets[key] = self.db_connection[key]
                self.sets_updated[key] = int(self.db_connection[key + '_updated'])
            else:
                # further cache for 60 seconds, reduce runtime from ~600us to ~100ns
                if time.time() - self.sets_updated[key] > 60:
                    updated_check = int(self.db_connection[key + '_updated'])
                    if updated_check > self.sets_updated[key]:
                        self.sets[key] = self.db_connection[key]
                        self.sets_updated[key] = updated_check
                    else:
                        self.sets_updated[key] = time.time() - 5

            return value in self.sets[key]
        elif self.db_type == 'redis':
            return self.db_connection.sismember(key, value)  # might want to combine into 1 lua call for ip checks?
        # see https://stackoverflow.com/questions/31788068/redis-alternative-to-check-existence-of-multiple-values-in-a-set

    def delete_old_keys(self, time_limit=60 * 60):
        expire_time_limit = time.time() - time_limit
        if self.db_type == 'sqlite':
            for token, token_details in self.db_connection.iteritems():
                if isinstance(token_details, dict) and len(token) == token_length:
                    if token_details['expires'] < expire_time_limit:
                        del self.db_connection[token]
        elif self.db_type == 'redis':
            # we set keys to be expired by redis automatically
            pass

    def delete(self, key):
        if self.db_type == 'sqlite':
            if key in self.db_connection:
                del self.db_connection[key]
        elif self.db_type == 'redis':
            self.db_connection.delete(key)

    def close(self):
        self.db_connection.close()
