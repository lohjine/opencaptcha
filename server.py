import schedule
import logging
import time
import configparser
import os
import random
import string
from opencaptcha_lib import DBconnector, site_secret_length, site_key_length, validate_settings_ini
import gzip
import shutil
import subprocess
import ipaddress



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
# then ip blacklist  --  # how to get flask threads to automatically refresh their blacklists?
#                       probably want to push to redis, then flask thread schedule to retrieve from redis
#                           can also have a separate updated_at so can check more often without actually retrieving same
# then ip rate limiting

## hmm, we don't care about "attacks", but rather, proxies? but attack might be defined as botnet
# probably want firehol1, 2, firehol_abusers_1d, stopforumspam7d as blacklist

# firehol_proxies, vpn-ipv4 as proxies

# tor as tor

# http://iplists.firehol.org/
# consider wiki

def fetch_tor_ips():

    tor_endpoint = 'https://check.torproject.org/torbulkexitlist'

    # update once a day
    update = True
    if os.path.exists('db/torbulkexitlist'):
        modified_time = os.lstat('db/torbulkexitlist').st_mtime
        if time.time() - modified_time < 60 * 60 * 24: # 1 day
            update = False

    if update:
        subprocess.check_output(['wget',tor_endpoint,'-O','db/torbulkexitlist','-nv'], stderr=subprocess.STDOUT)
        return True
    return False


def fetch_vpn_ips():

    vpn_ip_endpoint = 'https://github.com/ejrv/VPNs/blob/master/vpn-ipv4.txt' # for commercial & datacenter, not very updated
    # so update once a month
    # also needs to be collated

    update = True
    if os.path.exists('db/listed_ip_7.zip'):
        modified_time = os.lstat('db/listed_ip_7.zip').st_mtime
        if time.time() - modified_time < 60 * 60 * 24 * 30.5 : # 1 month
            update = False

    if update:
        subprocess.check_output(['wget',vpn_ip_endpoint,'-O','db/vpn-ipv4.txt','-nv'], stderr=subprocess.STDOUT)
        return True
    return False



def fetch_ip_blacklists():

    stopforumspam_endpoint = 'https://www.stopforumspam.com/downloads/listed_ip_7.gz' # set of IPs

    # check whether already have an updated one, in case we restart process multiple times
    update = True
    if os.path.exists('db/listed_ip_7.gz'):
        modified_time = os.lstat('db/listed_ip_7.zip').st_mtime
        if time.time() - modified_time < 60 * 60: # 1 hour
            update = False

    if update:
        subprocess.check_output(['wget',stopforumspam_endpoint,'-O','db/listed_ip_7.gz','-nv'], stderr=subprocess.STDOUT)
        return True
    return False



def consolidate_ip_blacklists():
    # NO WAIT DON'T COMBINE WE HAVE SEPARATE PENALTIES !?
    # hmm, we can apply the highest penalty applicable


    logging.debug('Consolidating blacklist IPs...')

    with open(r'db/vpn-ipv4.txt','r') as f:
        q = f.readlines()[2:]

    ipnets = []

    for i in q:
        ipnets.append(ipaddress.IPv4Network(i.strip()))

    collapsed_ipnets = [i for i in ipaddress.collapse_addresses(ipnets)]

    # separate out all /32 to a single set for faster checking
    collapsed_ipnets_32 = []
    collapsed_ipnets_rest = []
    for i in collapsed_ipnets:
        if i.num_addresses == 1:
            collapsed_ipnets_32.append(i.network_address.exploded)
        else:
            collapsed_ipnets_rest.append(i)

    collapsed_ipnets_32 = set(collapsed_ipnets_32)


    with gzip.open('db/listed_ip_7.gz', 'rb') as f:
        file_content = f.read()

    stopforumspam_ips = [i.decode('utf-8') for i in file_content.splitlines()]

    logging.info(f'{len(collapsed_ipnets_32)} ips + {len(collapsed_ipnets_rest)} ip ranges from vpn-ipv4.txt (vpn+dc)')
    logging.info(f'{len(stopforumspam_ips)} ips from listed_ip_7.gz (stopforumspam)')
    logging.info(f'{len(stopforumspam_ips)} ips from torbulkexitlist (tor exit)')

    logging.info(f'Total ips: {len(collapsed_ipnets_32)}')

    # update db
    logging.debug('Updating database with blacklist IPs...')
    db_connection.set('collapsed_ipnets_32', collapsed_ipnets_32)
    db_connection.set('collapsed_ipnets', collapsed_ipnets)

    db_connection.set('ip_blacklist_update',time.time())


    return collapsed_ipnets_32, collapsed_ipnets


def test(test='37.58.17.10'):
    # 1.27 ms ± 8.54 µs per loop (mean ± std. dev. of 7 runs, 1000 loops each)
    # might consider exploding collapsed_ipnets_rest, it could be faster. but 1ms is fast enough for now
    blacklisted = False
    if test in collapsed_ipnets_32:
        blacklisted = True
    else:
        test = ipaddress.ip_address(test)
        for i in collapsed_ipnets_rest:
            if test in i:
                blacklisted = True
                break
    return blacklisted


def update_ip_lists():

    updated = fetch_tor_ips()
    updated2 = fetch_vpn_ips()
    updated3 = fetch_ip_blacklists()

    return True

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

    schedule.every().hour.at(":00").do(update_ip_lists)
    print('Running...')

    while True:
        schedule.run_pending()
        time.sleep(1)
