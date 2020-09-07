import schedule
import logging
import time
import configparser
import os
import random
import string
from opencaptcha_lib import DBconnector, site_secret_length, site_key_length, validate_settings_ini


# ok this one does the misc stuff


# sqlite
# - no need additional service
# - hard to move to new server
# - might be slower
# tested multi access - works as expected!

# redis
# - additional service
# - easy to move to new server
# - faster?


# do challenge
# then ip rate limiting
# then ip blacklist

def fetch_tor_ips():

    tor_endpoint = 'https://check.torproject.org/torbulkexitlist'

    # hmm requests dependency or curl..
    subprocess.Popen

    pass


def fetch_vpn_ips():

    vpn_ip_endpoint = 'https://github.com/ejrv/VPNs/blob/master/vpn-ipv4.txt' # for commercial, not very updated

    pass


def fetch_ip_blacklists():

    stopforumspam_endpoint = 'https://www.stopforumspam.com/downloads/listed_ip_7.zip'

    # https://www.stopforumspam.com/downloads/listed_ip_7.gz
    # check whether already have an updated one, in case we restart process multiple times

    pass


if __name__ == "__main__":

    logging.basicConfig(filename='logs/server.log', filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.DEBUG)

    try:
        validate_settings_ini()
    except Exception as e:
        logging.error(str(e))
        raise

    config = configparser.ConfigParser()
    config.read('settings.ini')

    db_connection = DBconnector()

    if not os.path.exists('site_details.txt'):
        site_key = ''.join(
            random.SystemRandom().choice(
                string.ascii_lowercase +
                string.ascii_uppercase +
                string.digits) for _ in range(site_key_length))
        site_secret = ''.join(
            random.SystemRandom().choice(
                string.ascii_lowercase +
                string.ascii_uppercase +
                string.digits) for _ in range(site_secret_length))

        with open('site_details.txt', 'w') as f:
            f.write(f"site_key = {site_key}\n")
            f.write(f"site_secret = {site_secret}\n")

        print(f'First startup detected:')
        print(f'Your site_key is: {site_key}')
        print(f'Your site_secret is: {site_secret}')
        print(f'These have been saved in site_details.txt')
    else:
        with open('site_details.txt', 'r') as f:
            site_key = f.readline().split(' = ')[1].strip()
            site_secret = f.readline().split(' = ')[1].strip()

        print(f'Your site_key is: {site_key}')
        print(f'Your site_secret is: {site_secret}')

    # write site_key and site_secret into database
    db_connection.set(site_key, {'site_secret': site_secret,
                                 'challenge_level': int(config['captcha']['challenge_level']),
                                 'tor_penalty': int(config['captcha']['tor_penalty']),
                                 'vpn_penalty': int(config['captcha']['vpn_penalty']),
                                 'ip_blacklist_penalty': int(config['captcha']['ip_blacklist_penalty'])
                                 })

    if config['db']['type'] == 'sqlite':
        schedule.every().hour.at(":00").do(db_connection.delete_old_keys)

    print('Running...')

    while True:
        schedule.run_pending()
        time.sleep(1)
