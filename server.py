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
from glob import glob



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
        
        try:
            subprocess.check_output(['wget',tor_endpoint,'-O','db/torbulkexitlist','-nv'], stderr=subprocess.STDOUT)
        except Exception as e:
            logging.error(f'Failed to fetch tor IPs: {e}')
            return False                    
        
        # update database        
        with open(os.path.join('db','torbulkexitlist')) as f:
            tor_ips = set(f.read().splitlines())
        
        db_connection.set_set('tor_ips',tor_ips)
        db_connection.set_value('tor_ips_updated', str(int(time.time())))
        
        return True
    
    return False


def fetch_vpn_ips():
    """
    
    firehol_proxies, vpn-ipv4
    
    """

    vpn_ipv4_endpoint = 'https://raw.githubusercontent.com/ejrv/VPNs/master/vpn-ipv4.txt' # for commercial & datacenter, not very updated
    firehol_proxies_endpoint = 'https://iplists.firehol.org/files/firehol_proxies.netset'
    # so update once a month
    # also needs to be collated

    update = False
    
    retrieve_vpn_ipv4 = False
    if os.path.exists('db/listed_ip_7.zip'):
        modified_time = os.lstat('db/listed_ip_7.zip').st_mtime
        if time.time() - modified_time > 60 * 60 * 24 * 30.5 : # 1 month
            retrieve_vpn_ipv4 = True
    else:
        retrieve_vpn_ipv4 = True
        
    if retrieve_vpn_ipv4 == True:
        try:
            subprocess.check_output(['wget',vpn_ipv4_endpoint,'-O','db/vpn-ipv4.txt','-nv'], stderr=subprocess.STDOUT)
        except Exception as e:
            logging.error(f'Failed to fetch vpn IPs - vpn_ipv4_endpoint: {e}')
            return False                
        update = True
        
    
    retrieve_firehol_proxies = False
    if not os.path.exists('db/firehol_proxies.netset'):
        modified_time = os.lstat('db/firehol_proxies.netset').st_mtime
        if time.time() - modified_time > 60 * 60 * 24 * 30.5 : # 1 day
            retrieve_firehol_proxies = True
    else:
        retrieve_firehol_proxies = True
            
    if retrieve_firehol_proxies == True:
        try:
            subprocess.check_output(['wget',firehol_proxies_endpoint,'-O','db/firehol_proxies.netset','-nv'], stderr=subprocess.STDOUT)
        except Exception as e:
            logging.error(f'Failed to fetch vpn IPs - firehol_proxies_endpoint: {e}')
            return False                
        update = True
            

    if update:
        # update database        
        with open(os.path.join('db','vpn-ipv4.txt')) as f:
            vpn_ipv4 = f.read().splitlines()[2:]
        
        ipnets = []
        
        transformed_ipnets_1 = transform_ipnet_strings(vpn_ipv4)
    
        for i in vpn_ipv4:
            ipnets.append(ipaddress.IPv4Network(i))
            
            
        with open(os.path.join('db','firehol_proxies.netset')) as f:
            firehol_proxies = f.read().splitlines()
            
        firehol_proxies = [i for i in firehol_proxies if i[0] != '#']
                           
        transformed_ipnets_2 = transform_ipnet_strings(firehol_proxies) # 1630901
        # efficiency loss = (1630895 - 1497613) / 1497613 * 100 = 8.9%, should be fine, now takes 200mb instead of 3GB
    
        transformed_ipnets_1.update(transformed_ipnets_2)
    
        db_connection.set_set('vpn_ips',transformed_ipnets_1) 
        db_connection.set_value('vpn_ips_updated', str(int(time.time())))
        
        # just operate on txt much cheaper ffs don't use ipadress collapse_addresses even if it might be marginally better
        # unless really have many many sources?        
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
    
    
    with gzip.open('db/listed_ip_7.gz', 'rb') as f:
        file_content = f.read()

    stopforumspam_ips = [i.decode('utf-8') for i in file_content.splitlines()]

    return False



def transform_ipnets(collapsed_ipnets):

    transformed_ipnets = []

    # separate out all /32 to a single set for faster checking
#    collapsed_ipnets_32 = []
#    collapsed_ipnets_rest = []
#    for i in collapsed_ipnets:
#        if i.num_addresses == 1:
#            collapsed_ipnets_32.append(i.network_address.exploded)
#        else:
#            collapsed_ipnets_rest.append(i)

#    collapsed_ipnets_32 = set(collapsed_ipnets_32)

#    logging.info(f'{len(collapsed_ipnets_32)} ips + {len(collapsed_ipnets_rest)} ip ranges from vpn-ipv4.txt (vpn+dc)')
#    logging.info(f'{len(stopforumspam_ips)} ips from listed_ip_7.gz (stopforumspam)')
#    logging.info(f'{len(stopforumspam_ips)} ips from torbulkexitlist (tor exit)')
#
#    logging.info(f'Total ips: {len(collapsed_ipnets_32)}')

    # update db
    
#    logging.debug('Updating database with blacklist IPs...')
#    db_connection.set('collapsed_ipnets_32', collapsed_ipnets_32)
#    db_connection.set('collapsed_ipnets', collapsed_ipnets)
#
#    db_connection.set('ip_blacklist_update',time.time())

    ## To be able to perform queries on DB layer directly, we expand the ip network ranges and do 3 exists query for
    ## different octets
    for i in collapsed_ipnets:
        if i.num_addresses == 1:
            transformed_ipnets.append(i.network_address.exploded)
        else:
            subnetmask = int(i.compressed.split('/')[1])
            if subnetmask > 24:

                adds = 2**(32 - subnetmask)

                base_octet = '.'.join(i.network_address.exploded.split('.')[:3]) + '.'
                start_octet = int(i.network_address.exploded.split('.')[3])

                for j in range(adds):
                    if start_octet > 255 or start_octet < 0:
                        raise ValueError(f'Invalid octet {i}, {start_octet}')
                    transformed_ipnets.append(base_octet + str(start_octet))
                    start_octet += 1

            elif 24 >= subnetmask >= 17:
                adds = 2**(24 - subnetmask)

                base_octet = '.'.join(i.network_address.exploded.split('.')[:2]) + '.'
                start_octet = int(i.network_address.exploded.split('.')[2])

                for j in range(adds):
                    if start_octet > 255 or start_octet < 0:
                        raise ValueError(f'Invalid octet {i}, {start_octet}')
                    transformed_ipnets.append(base_octet + str(start_octet))
                    start_octet += 1

            elif 16 >= subnetmask:
                adds = 2**(16 - subnetmask)

                base_octet = '.'.join(i.network_address.exploded.split('.')[:1]) + '.'
                start_octet = int(i.network_address.exploded.split('.')[1])

                for j in range(adds):
                    if start_octet > 255 or start_octet < 0:
                        raise ValueError(f'Invalid octet {i}, {start_octet}')
                    transformed_ipnets.append(base_octet + str(start_octet))
                    start_octet += 1

    return transformed_ipnets

def transform_ipnet_strings(ipnets):
    
    transformed_ipnets = set()

    for i in ipnets:
        if '/' not in i or i.split('/')[1] == 32:
            transformed_ipnets.add(i.split('/')[0])
        else:
            ip, subnetmask = i.split('/')
            subnetmask = int(subnetmask)
            if subnetmask > 24:

                adds = 2**(32 - subnetmask)

                base_octet = '.'.join(ip.split('.')[:3]) + '.'
                start_octet = int(ip.split('.')[3])

                for j in range(adds):
                    if start_octet > 255 or start_octet < 0:
                        raise ValueError(f'Invalid octet {i}, {start_octet}')
                    transformed_ipnets.add(base_octet + str(start_octet))
                    start_octet += 1

            elif 24 >= subnetmask >= 17:
                adds = 2**(24 - subnetmask)

                base_octet = '.'.join(ip.split('.')[:2]) + '.'
                start_octet = int(ip.split('.')[2])

                for j in range(adds):
                    if start_octet > 255 or start_octet < 0:
                        raise ValueError(f'Invalid octet {i}, {start_octet}')
                    transformed_ipnets.add(base_octet + str(start_octet))
                    start_octet += 1

            elif 16 >= subnetmask:
                adds = 2**(16 - subnetmask)

                base_octet = '.'.join(ip.split('.')[:1]) + '.'
                start_octet = int(ip.split('.')[1])

                for j in range(adds):
                    if start_octet > 255 or start_octet < 0:
                        raise ValueError(f'Invalid octet {i}, {start_octet}')
                    transformed_ipnets.add(base_octet + str(start_octet))
                    start_octet += 1

    return transformed_ipnets
    

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


    if updated:
        pass

    if updated2:
        pass

    if updated3:
        pass

    return True


def clean_up_audio_challenges():
    current_time = time.time()
    for i in glob(os.path.join('challenges','audio','*')):
        if current_time - os.lstat(i).st_mtime > 5 * 60:
            os.remove(i)

    return True


def generate_animal_images():
    # create a new tmp folder, populate it, then move to the correct folder, then delete if == 3 folders

    return True


def ip_rate_limit():

    # 1 / sec
    # 6 / min
    # 30 / hour
    # 50 / day

    return False


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
    schedule.every(10).minutes.do(clean_up_audio_challenges)

    print('Running...')

    while True:
        schedule.run_pending()
        time.sleep(1)
