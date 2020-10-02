import schedule
import logging
import time
import configparser
import os
import random
import string
from opencaptcha_lib import DBconnector, site_secret_length, site_key_length, validate_settings_ini, image_similarity_hash
import gzip
from glob import glob
import urllib.request
import shutil
import toml
from collections import defaultdict
import subprocess
import PIL
from PIL import Image
import hashlib
import pickle

# sqlite
# - no need additional service
# - hard to move to new server
# - might be slower
# tested multi access - works as expected!

# redis
# - additional service
# - easy to move to new server
# - faster?


opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', 'Wget/1.12 (linux-gnu)')]  # otherwise firehol blocks us
urllib.request.install_opener(opener)


def update_tor_ips(force=False):

    tor_endpoint = 'https://check.torproject.org/torbulkexitlist'

    update = True
    if os.path.exists('db/torbulkexitlist'):
        modified_time = os.lstat('db/torbulkexitlist').st_mtime
        if time.time() - modified_time < 60 * 60 * 24 + 60:  # 1 day, add a minute offset so that a slight miss still gets updated
            update = False

    if update or force:
        try:
            urllib.request.urlretrieve(tor_endpoint, 'db/torbulkexitlist')
        except Exception as e:
            logging.error(f'Failed to fetch tor IPs: {e}')
            return False

        # update database
        logging.debug('Updating db for tor')

        with open(os.path.join('db', 'torbulkexitlist')) as f:
            tor_ips = set(f.read().splitlines())

        db_connection.set_set('tor_ips', tor_ips)
        db_connection.set_value('tor_ips_updated', str(int(time.time())))

        return True

    return False


def update_vpn_ips(force=False):
    """
    firehol_proxies, vpn-ipv4
    """

    vpn_ipv4_endpoint = 'https://raw.githubusercontent.com/ejrv/VPNs/master/vpn-ipv4.txt'  # for commercial & datacenter, not very updated
#    firehol_proxies_endpoint = 'https://iplists.firehol.org/files/firehol_proxies.netset' # too many IPs, requires >1GB ram on server

    update = False

    retrieve_vpn_ipv4 = False
    if os.path.exists('db/vpn-ipv4.txt'):
        modified_time = os.lstat('db/vpn-ipv4.txt').st_mtime
        if time.time() - modified_time > 60 * 60 * 24 * 30.5 - 60:  # 1 month
            retrieve_vpn_ipv4 = True
    else:
        retrieve_vpn_ipv4 = True

    if retrieve_vpn_ipv4 == True:
        try:
            urllib.request.urlretrieve(vpn_ipv4_endpoint, 'db/vpn-ipv4.txt')
        except Exception as e:
            logging.error(f'Failed to fetch vpn IPs - vpn_ipv4_endpoint: {e}')
            return False
        update = True

#    retrieve_firehol_proxies = False
#    if os.path.exists('db/firehol_proxies.netset'):
#        modified_time = os.lstat('db/firehol_proxies.netset').st_mtime
#        if time.time() - modified_time > 60 * 60 * 24 - 60:  # 1 day
#            retrieve_firehol_proxies = True
#    else:
#        retrieve_firehol_proxies = True
#
#    if retrieve_firehol_proxies == True:
#        try:
#            urllib.request.urlretrieve(firehol_proxies_endpoint, 'db/firehol_proxies.netset')
#        except Exception as e:
#            logging.error(f'Failed to fetch vpn IPs - firehol_proxies_endpoint: {e}')
#            return False
#        update = True

    if update or force:
        logging.debug('Updating db for vpn')
        # update database
        with open(os.path.join('db', 'vpn-ipv4.txt')) as f:
            vpn_ipv4 = f.read().splitlines()[2:]

        transformed_ipnets = transform_ipnet_strings(vpn_ipv4)

#        with open(os.path.join('db', 'firehol_proxies.netset')) as f:
#            firehol_proxies = f.read().splitlines()
#
#        firehol_proxies = [i for i in firehol_proxies if i[0] != '#']

#        transformed_ipnets = transform_ipnet_strings(firehol_proxies, transformed_ipnets)

        db_connection.set_set('vpn_ips', transformed_ipnets)
        db_connection.set_value('vpn_ips_updated', str(int(time.time())))

        return True

    return False


def update_ip_blacklists(force=False):

    stopforumspam_endpoint = 'https://www.stopforumspam.com/downloads/listed_ip_7.gz'
    firehol_abusers_endpoint = 'https://iplists.firehol.org/files/firehol_abusers_1d.netset'
    firehol_level1_endpoint = 'https://iplists.firehol.org/files/firehol_level1.netset'
    firehol_level2_endpoint = 'https://iplists.firehol.org/files/firehol_level2.netset'

    update = False

    retrieve_stopforumspam = False
    if os.path.exists('db/listed_ip_7.gz'):
        modified_time = os.lstat('db/listed_ip_7.gz').st_mtime
        if time.time() - modified_time > 60 * 60 * 24 - 60:  # 1 day
            retrieve_stopforumspam = True
    else:
        retrieve_stopforumspam = True

    if retrieve_stopforumspam == True:
        try:
            urllib.request.urlretrieve(stopforumspam_endpoint, 'db/listed_ip_7.gz')
        except Exception as e:
            logging.error(f'Failed to fetch blacklisted IPs - stopforumspam_endpoint: {e}')
            return False
        update = True

    retrieve_firehol_abusers = False
    if os.path.exists('db/firehol_abusers_1d.netset'):
        modified_time = os.lstat('db/firehol_abusers_1d.netset').st_mtime
        if time.time() - modified_time > 60 * 60 * 2 - 60:  # 2 hour
            retrieve_firehol_abusers = True
    else:
        retrieve_firehol_abusers = True

    if retrieve_firehol_abusers == True:
        try:
            urllib.request.urlretrieve(firehol_abusers_endpoint, 'db/firehol_abusers_1d.netset')
        except Exception as e:
            logging.error(f'Failed to fetch vpn IPs - firehol_abusers_endpoint: {e}')
            return False
        update = True

    retrieve_firehol_level1 = False
    if os.path.exists('db/firehol_level1.netset'):
        modified_time = os.lstat('db/firehol_level1.netset').st_mtime
        if time.time() - modified_time > 60 * 60 * 24 - 60:  # 1 day
            retrieve_firehol_level1 = True
    else:
        retrieve_firehol_level1 = True

    if retrieve_firehol_level1 == True:
        try:
            urllib.request.urlretrieve(firehol_level1_endpoint, 'db/firehol_level1.netset')
        except Exception as e:
            logging.error(f'Failed to fetch vpn IPs - firehol_level1_endpoint: {e}')
            return False
        update = True

    retrieve_firehol_level2 = False
    if os.path.exists('db/firehol_level2.netset'):
        modified_time = os.lstat('db/firehol_level2.netset').st_mtime
        if time.time() - modified_time > 60 * 60 * 12 - 60:  # 12 hour
            retrieve_firehol_level2 = True
    else:
        retrieve_firehol_level2 = True

    if retrieve_firehol_level2 == True:
        try:
            urllib.request.urlretrieve(firehol_level2_endpoint, 'db/firehol_level2.netset')
        except Exception as e:
            logging.error(f'Failed to fetch vpn IPs - firehol_level2_endpoint: {e}')
            return False
        update = True

    if update or force:

        logging.debug('Updating db for blacklist')

        with gzip.open('db/listed_ip_7.gz', 'rb') as f:
            file_content = f.read()

        transformed_ipnets = set([i.decode('utf-8') for i in file_content.splitlines()])

        with open(os.path.join('db', 'firehol_abusers_1d.netset')) as f:
            firehol_abusers_1d = f.read().splitlines()

        firehol_abusers_1d = [i for i in firehol_abusers_1d if i[0] != '#']

        transformed_ipnets = transform_ipnet_strings(firehol_abusers_1d, transformed_ipnets)

        with open(os.path.join('db', 'firehol_level1.netset')) as f:
            firehol_level1 = f.read().splitlines()

        firehol_level1 = [i for i in firehol_level1 if i[0] != '#']

        transformed_ipnets = transform_ipnet_strings(firehol_level1, transformed_ipnets)

        with open(os.path.join('db', 'firehol_level2.netset')) as f:
            firehol_level2 = f.read().splitlines()

        firehol_level2 = [i for i in firehol_level2 if i[0] != '#']

        transformed_ipnets = transform_ipnet_strings(firehol_level2, transformed_ipnets)

        db_connection.set_set('blacklist_ips', transformed_ipnets)
        db_connection.set_value('blacklist_ips_updated', str(int(time.time())))

    return False


def transform_ipnet_strings(ipnets, transformed_ipnets=set()):
    """
    Creates a set of ip strings for ip-checking purposes.

    # Ideally, we should use ipaddress library to combine overlapping ip address ranges from multiple sources,
    # but the memory usage blows up to GBs
    # Instead, we do a naive set combination, which only takes 200MB ram.
    # Efficiency loss vs ipaddress handling for vpn_ips examples = (1630895 - 1497613) / 1497613 * 100 = 8.9%

    Converts list of ipnet strings (x.x.x.x/x) to a set of transformed ipnet strings that fulfils criteria:
        - /25 to /32 are expanded to /32 equivalents
        - /17 to /24 are expanded to /24 equivalents
        - /9 to /16 are expanded to /16 equivalents
        - /8 and below are dropped

    Assumes subnetmask-less strings to be /32


    Args:
        ipnets (list): list of ipnet strings
        transformed_ipnets (set): set to add to

    Returns:
        :set: of ipnet strings
    """

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

            elif 17 <= subnetmask <= 24:
                adds = 2**(24 - subnetmask)

                base_octet = '.'.join(ip.split('.')[:2]) + '.'
                start_octet = int(ip.split('.')[2])

                for j in range(adds):
                    if start_octet > 255 or start_octet < 0:
                        raise ValueError(f'Invalid octet {i}, {start_octet}')
                    transformed_ipnets.add(base_octet + str(start_octet))
                    start_octet += 1

            elif 9 <= subnetmask <= 16:
                adds = 2**(16 - subnetmask)

                base_octet = '.'.join(ip.split('.')[:1]) + '.'
                start_octet = int(ip.split('.')[1])

                for j in range(adds):
                    if start_octet > 255 or start_octet < 0:
                        raise ValueError(f'Invalid octet {i}, {start_octet}')
                    transformed_ipnets.add(base_octet + str(start_octet))
                    start_octet += 1
            else:
                # we skip anything that would be expanded to a x.0.0.0 check, so we only need to check IPs for 3 patterns
                # x.x.x.x, x.x.x and x.x
                # in effect, this misses ip ranges - 0.0.0.0/8, 10.0.0.0/8, 127.0.0.0/8, 224.0.0.0/3
                pass

    return transformed_ipnets


def gen_challenge_7_images(video_folder=os.path.join('challenges', '7', 'videos'), ffmpeg_path=''):
    """
    Generates challenge 7 images from videos


    Args:
        video_folder (str): Filepath where source videos are located
        ffmpeg_path (str): Path for ffmpeg, leave blank if already on path.

    Outputs:
        Creates a directory named with current unix time, located in opencaptcha/challenges/7/images,
        containing images derived from source videos.
    """

    base_folder = os.path.join('tmp', 'challenge_7_image_gen')
    raw_image_folder = os.path.join(base_folder, 'raw')
    completed_image_folder = os.path.join(base_folder, 'completed')

    if ffmpeg_path:
        ffmpeg_path = os.path.join(ffmpeg_path, 'ffmpeg')
    else:
        ffmpeg_path = 'ffmpeg'

    if not os.path.exists('tmp'):
        os.mkdir('tmp')

    # ensure a clean start
    if os.path.exists(base_folder):
        shutil.rmtree(base_folder)
    os.mkdir(base_folder)
    os.mkdir(raw_image_folder)
    os.mkdir(completed_image_folder)

    image_grouping = []

    image_debug_trace = {}

    # consider multiprocess this in future

    toml_files = glob(os.path.join(video_folder, '*.toml'))

    for toml_file in toml_files:

        frame_details = defaultdict(list)

        with open(toml_file, 'r') as f:
            video_details = toml.load(f)

        logging.debug(f"file: {video_details['filename']}")
        # validate video_annotation file

        # calculate the frames
        total_frames = int(video_details['videofps'] * video_details['duration'])

        frame_to_process = []

        # take a sample roughly every second, 0.5-1.5 second
        # first offset is half the duration

        lowerbound_offset = int(video_details['videofps'] / 2)
        upperbound_offset = int(video_details['videofps'] * 1.5)

        offset = random.randint(1, lowerbound_offset)

        frame_to_process.append(offset)

        while offset < total_frames:
            offset += random.randint(lowerbound_offset, upperbound_offset)
            frame_to_process.append(offset)

        logging.debug(f"frame numbers: {frame_to_process}")

        # dump images using ffmpeg to a tmp folder
        cmd_frames = ''
        for frame in frame_to_process:
            cmd_frames += rf'eq(n\,{frame})+'
        cmd_frames = cmd_frames[:-1]

        cmd_start = ffmpeg_path + f" -i {os.path.join(video_folder,video_details['filename'])} -vf select='"
        cmd_end = f"' -vsync vfr -q:v 2 {raw_image_folder+os.path.sep}%d.jpg"

        cmd_full = cmd_start + cmd_frames + cmd_end

        try:
            _ = subprocess.check_output(cmd_full, shell=True, stderr=subprocess.STDOUT)
        except Exception as e:
            logging.error(f"Error with ffmpeg command: {cmd_full}")
            logging.error(f"{e.output}")
            continue

        jpeg_files = glob(os.path.join(raw_image_folder, '*.jpg'))

        resolution = video_details['resolution']

        previous_frame_hash = ''

        for idx, jpeg_file in enumerate(jpeg_files):

            im = Image.open(jpeg_file)

            # check if frame is too similar to previous one
            current_frame_hash = image_similarity_hash(im)
            if idx > 0:
                if current_frame_hash == previous_frame_hash:
                    continue

            # do the image modifications
            # crop a random amount
            # pad a random border (with a light pattern) | NVM, crop should be good enough, and borders can be detected..
            # change lighting level
            # add a tint?

            # crop
            if resolution[0] > resolution[1]:
                crop_amount_px = resolution[0] - resolution[1]

                crop_amount_px_additional = int(random.random() * 0.15 * resolution[1])

                # add up to 15% of image
                crop_amount_px += crop_amount_px_additional

                # split the crop randomly from left and right
                crop_split_left = int(random.random() * crop_amount_px)
                crop_split_right = crop_amount_px - crop_split_left

                # split the crop randomly from top and bottom
                crop_split_top = int(random.random() * crop_amount_px_additional)
                crop_split_bottom = resolution[1] - (crop_amount_px_additional - crop_split_top)

                left, upper, right, lower = crop_split_left, crop_split_top, resolution[0] - crop_split_right, crop_split_bottom

                im = im.crop((left, upper, right, lower))

            else:
                crop_amount_px = resolution[1] - resolution[0]

                crop_amount_px_additional = int(random.random() * 0.15 * resolution[0])

                # add up to 15% of image
                crop_amount_px += crop_amount_px_additional

                # split the crop randomly from left and right
                crop_split_top = int(random.random() * crop_amount_px)
                crop_split_bottom = crop_amount_px - crop_split_top

                # split the crop randomly from top and bottom
                crop_split_left = int(random.random() * crop_amount_px_additional)
                crop_split_right = resolution[0] - (crop_amount_px_additional - crop_split_left)

                left, upper, right, lower = crop_split_left, crop_split_top, resolution[0] - crop_split_right, crop_split_bottom

                im = im.crop((left, upper, right, lower))

            im = im.resize((126, 126), resample=4)  # do not need high quality in downscaling

            if random.random() > 0.5:
                im = im.transpose(PIL.Image.FLIP_LEFT_RIGHT)  # very powerful in dodging certain CBIR, esp google image

            filenames = []
            # write a file with the hash as the filename
            filename_ori = hashlib.md5(im.tobytes()).hexdigest()
            im.save(os.path.join(completed_image_folder, filename_ori + '.jpg'))
            filenames.append(filename_ori + '.jpg')

            im2 = im.convert('HSV')

            pixels = list(im2.getdata())

            hue_skew = random.randint(62, 82)
            im2.putdata([((x[0] + hue_skew) % 256, x[1], x[2]) for x in pixels])
            im2 = im2.convert('RGB')
            filename_1 = hashlib.md5(im2.tobytes()).hexdigest()
            im2.save(os.path.join(completed_image_folder, filename_1 + '.jpg'))
            filenames.append(filename_1 + '.jpg')

            hue_skew = random.randint(108, 148)
            im2.putdata([((x[0] + hue_skew) % 256, x[1], x[2]) for x in pixels])
            im2 = im2.convert('RGB')
            filename_2 = hashlib.md5(im2.tobytes()).hexdigest()
            im2.save(os.path.join(completed_image_folder, filename_2 + '.jpg'))
            filenames.append(filename_2 + '.jpg')

            hue_skew = random.randint(184, 214)
            im2.putdata([((x[0] + hue_skew) % 256, x[1], x[2]) for x in pixels])
            im2 = im2.convert('RGB')
            filename_3 = hashlib.md5(im2.tobytes()).hexdigest()
            im2.save(os.path.join(completed_image_folder, filename_3 + '.jpg'))
            filenames.append(filename_3 + '.jpg')

            previous_frame_hash = current_frame_hash

            image_grouping.append(filenames)

            frame_details[frame_to_process[idx]].extend(filenames)

            os.remove(jpeg_file)

        image_debug_trace[video_details['filename']] = frame_details

    # finally
    # dump image_grouping
    with open(os.path.join(completed_image_folder, 'image_grouping.pkl'), 'wb') as f:
        pickle.dump(image_grouping, f)

    served_dir_name = str(int(time.time()))

    # dump image_debug_trace
    with open(os.path.join('logs', f'challenge_7_image_debug_trace_{served_dir_name}.pkl'), 'wb') as f:
        pickle.dump(image_debug_trace, f)

    # and move entire folder to challenge dir for serving
    destination_folder = os.path.join('challenges', '7', 'images', served_dir_name)
    shutil.move(completed_image_folder, destination_folder)

    # clean up directories
    shutil.rmtree(base_folder)

    logging.info(f'Completed generation of challenge 7 images at: {destination_folder}')


def update_ip_lists(force=False):

    update_ip_blacklists(force=force)
    update_tor_ips(force=force)
    update_vpn_ips(force=force)

    return True


def clean_up_audio_challenges():
    """Deletes audio challenges that are more than 5 minutes old."""
    current_time = time.time()
    for i in glob(os.path.join('challenges', 'audio', '*')):
        if current_time - os.lstat(i).st_mtime > 5 * 60:
            os.remove(i)

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
    db_connection.set_dict(site_key, {'site_secret': site_secret,
                                      'challenge_level': int(config['captcha']['challenge_level']),
                                      'tor_penalty': int(config['captcha']['tor_penalty']),
                                      'vpn_penalty': int(config['captcha']['vpn_penalty']),
                                      'ip_blacklist_penalty': int(config['captcha']['ip_blacklist_penalty'])
                                      })

    if config['db']['type'] == 'sqlite':
        schedule.every().hour.at(":00").do(db_connection.delete_old_keys)

    update_ip_lists()

    schedule.every().hour.at(":00").do(update_ip_lists)
    schedule.every(10).minutes.do(clean_up_audio_challenges)

    if int(config['captcha']['max_challenge_level']) >= 7:
        schedule.every(int(config['captcha']['challenge_level_7_imagegen_interval'])).hours.do(gen_challenge_7_images)

        # checks if latest generated image folder is still valid, else generate
        challenge_7_generated_image_folders = sorted(os.listdir(os.path.join('challenges', '7', 'images')))
        if '.gitignore' in challenge_7_generated_image_folders:
            challenge_7_generated_image_folders.remove('.gitignore')
        if len(challenge_7_generated_image_folders) == 0 or \
                int(challenge_7_generated_image_folders[-1]) + int(config['captcha']['challenge_level_7_imagegen_interval']) * 60 * 60 > time.time():

            logging.info('Generating challenge 7 images...')
            gen_challenge_7_images()
            logging.info('Generated challenge 7 images')

    print('Running...')

    while True:
        schedule.run_pending()
        time.sleep(1)
