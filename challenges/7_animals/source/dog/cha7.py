
from glob import glob
import toml
import subprocess
import random
import shutil
import hashlib
import logging
from PIL import Image
import PIL
from collections import defaultdict
import os
import pickle
import time

###### TESTING NEW

# for each file, gen 3 other hue-ified image

import numpy as np

for image_path in glob(path/"images"/'*.jpg'):

    im = Image.open(image_path)
    im2 = im.convert('HSV')

    pixels = np.array(im2)
    pixels[:,:,0] += 42 # we can slight randomize this number in prod, give NN the best chance first
    pixels[pixels[:,:,0] >= 256, 0] -= 256
    im_out = PIL.Image.fromarray(pixels, mode='HSV')
    im_out.convert('RGB').save(os.path.split(image_path)[0] + '/ZZZ1' + os.path.split(image_path)[1])

    pixels = np.array(im2)
    pixels[:,:,0] += 128
    pixels[pixels[:,:,0] >= 256, 0] -= 256
    im_out = PIL.Image.fromarray(pixels, mode='HSV')
    im_out.convert('RGB').save(os.path.split(image_path)[0] + '/ZZZ2' + os.path.split(image_path)[1])


    pixels = np.array(im2)
    pixels[:,:,0] += 213
    pixels[pixels[:,:,0] >= 256, 0] -= 256
    im_out = PIL.Image.fromarray(pixels, mode='HSV')
    im_out.convert('RGB').save(os.path.split(image_path)[0] + '/ZZZ3' + os.path.split(image_path)[1])


## seems good


# test similarity hash


a = imagehash.dhash(im1)
b = imagehash.dhash(im2)
c = imagehash.dhash(im3)

a == b
b == c


a1 = image_similarity_hash(im1)
b1 = image_similarity_hash(im2)
c1 = image_similarity_hash(im3)

a1 == b1
b1 == c1
a1 == c1

######


#####

# okay new mode fml


# get random frames from videos, 1 every sec, or + 0.5-1.5 sec from current would be better

# do we still want to check if frame too similar?
# in case video is a still..


# get foreground, background?
# too compute intensive

# crop longer dim from random amounts from each side

# crop both dims a random amount

# resize to 150x150


# produce hue-skewed variants




####

def image_similarity_hash(im):
    """
    Calculates average hash as defined in http://www.hackerfactor.com/blog/index.php?/archives/432-Looks-Like-It.html
    """

    im = im.resize((10,10) ,resample=0) # 10x10 to be more stricter in determine similarity, as measured during testing
    im = im.convert(mode='L')

    data = list(im.getdata())

    avg = sum(data) / len(data)

    image_hash = [i>=avg for i in data]

    return image_hash


# then choose a number of frames per video

# we probably want to assume that each video is roughly the same
# - real time
# - sufficient movement
# - always in frame


## should we preprocess ALL possible images?
## doesn't make sense because video is compressed form - which is what we want

## problem of


## might want to annotate?
## probably need, because target must be a % of the image..

### preprocessing videos
## should do an automated version to make life simpler.
# use yolov4 to compute annotation
# find bounding box of dog over entire video.
# also record fps of video, total number of frames of video


# for each second, 24/30 frames, find the bounding box of dog, grab the closest available from the middle


## define metadata file here, what format?? ini, yaml, json
##  we don't need it to be human readable much, data structure-wise
# filename =
# duration =
# fps =
# video resolution =
# bounding box (per sec basis?), take the middle of each second (as an avg) = list of coords (4 points)

a = {'bb' : [((1,2),(3,4)), ((1,2),(3,5))],
     'filename': '2.mp4',
     'duration': 60.2, # seconds
     'videofps': 24,
     'resolution': (700,480)
     }
with open('new_toml_file.toml', 'w') as f:
    new_toml_string = toml.dump(a, f)

with open('new_toml_file.toml', 'r') as f:
    b = toml.load(f)


# gen toml file function


def gen_toml_file(full_refresh=False):
    """

    """

    all_files = glob(os.path.join('challenges','7','videos','*'))

    toml_files = set([i for i in all_files if i[-4:] == 'toml'])
    video_files = [i for i in all_files if i[-4:] != 'toml']

    files_processed = 0
    files_error = 0
    files_skipped = 0

    for video in video_files:
        if not full_refresh and os.path.split(video)[-1] in toml_files:
            files_skipped += 1
            continue
        else:

            toml_filepath = video + '.toml'

            cmd_full = 'ffprobe -v error -select_streams v:0 -show_entries stream=nb_frames -of default=nokey=1:noprint_wrappers=1' + video

            try:
                output = subprocess.check_output(cmd_full, shell=True)
            except Exception as e:
                logging.error(f"Error with ffprobe command: {cmd_full}")
                logging.error(f"{e}")
                files_error += 1

            ## format output into toml file
            video_details = {'filename': os.path.split(video)[-1],
                             'duration': 60.2, # seconds
                             'videofps': 24,
                             'resolution': (700,480)
                             }

            with open(toml_filepath, 'w') as f:
                _ = toml.dump(video_details, f)

            files_processed += 1

    logging.info('{files_processed} files processed. {files_error} files error. {files_skipped} files skipped.')

    return True

### processing images
# don't want to choose too many frames

# we probably want 1 frame/second, so -> read from metadata
#

# as we process
# also should determine that 'adjacent' frames are not too similar, which also helps to rule out slow motion


base_folder = os.path.join('tmp','challenge_7_image_gen')
raw_image_folder = os.path.join(base_folder,'raw')
completed_image_folder =  os.path.join(base_folder,'completed')
video_folder = os.path.join('challenges','7','videos')

if not os.path.exists('tmp'):
    os.mkdir('tmp')

# ensure a clean start
if os.path.exists(base_folder):
    shutil.rmtree(base_folder)
os.mkdir(base_folder)
os.mkdir(raw_image_folder)
os.mkdir(completed_image_folder)

image_grouping = []

image_debug_trace = defaultdict(list)

# == for each video

toml_files = glob('*.toml')

frame_details = []

for toml_file in toml_files:

    with open(toml_file, 'r') as f:
        video_details = toml.load(f)

    # validate video_annotation file

    # calculate the frames
    total_frames = video_details['videofps'] * video_details['duration']

    frame_to_process = []

    for i in range(int(video_details['duration'])):

        frame = random.randint(1, video_details['videofps']) + i*video_details['videofps']


        frame_to_process.append(frame)
        frame_details.append({'framenumber':frame})

# dump images using ffmpeg to a tmp folder


cmd_frames = ''
for frame in frame_to_process:
    cmd_frames += f'eq(n\,{frame})+'
cmd_frames = cmd_frames[:-1]

cmd_start = f"ffmpeg -i {os.path.join(video_folder,video_details['filename'])} -vf select='"
cmd_end =  f"' -vsync vfr -q:v 2 {raw_image_folder+os.path.sep}%d.jpg"

cmd_full = cmd_start + cmd_frames + cmd_end

try:
    subprocess.check_output(cmd_full, shell=True)
except Exception as e:
    logging.error(f"Error with ffmpeg command: {cmd_full}")
    raise

jpeg_files = glob('*.jpg') # => need to be in order! | nt rly

resolution = video_details['resolution']

for idx, jpeg_file in enumerate(jpeg_files):

    previous_frame_hash = ''


    im = Image.open(jpeg_file)

    # check if frame is too similar to previous one
    # no wait can't do here, don't have the image
    if idx > 0:
        current_frame_hash = image_similarity_hash(im)
        if current_frame_hash == previous_frame_hash:
            # delete image
            os.remove(jpeg_file)
            continue

    # do the image modifications
    ## crop a random amount
    ## pad a random border (with a light pattern) | k nvm, crop should be good enough, and borders can be detected..
    ## change lighting level
    ## add a light tint

    # crop
    if resolution[0] > resolution[1]:
        crop_amount_px = resolution[0] - resolution[1]

        crop_amount_px_additional = int(random.random() * 0.15 * resolution[1])

        # add up to 15% of image
        crop_amount_px +=  crop_amount_px_additional

        # split the crop randomly from left and right
        crop_split_left = int(random.random() * crop_amount_px)
        crop_split_right = crop_amount_px - crop_split_left

        # split the crop randomly from top and bottom
        crop_split_top = int(random.random() * crop_amount_px_additional)
        crop_split_bottom = resolution[1] - (crop_amount_px_additional - crop_split_top)

        left, upper, right, lower =  crop_split_left, crop_split_top , resolution[0] - crop_split_right, crop_split_bottom

        im = im.crop((left, upper, right, lower))

    else:
        crop_amount_px = resolution[1] - resolution[0]

        crop_amount_px_additional = int(random.random() * 0.15 * resolution[0])

        # add up to 15% of image
        crop_amount_px +=  crop_amount_px_additional

        # split the crop randomly from left and right
        crop_split_top = int(random.random() * crop_amount_px)
        crop_split_bottom = crop_amount_px - crop_split_top

        # split the crop randomly from top and bottom
        crop_split_left = int(random.random() * crop_amount_px_additional)
        crop_split_right = resolution[0] - (crop_amount_px_additional - crop_split_left)

        left, upper, right, lower =  crop_split_left, crop_split_top , resolution[0] - crop_split_right, crop_split_bottom

        im = im.crop((left, upper, right, lower))


    im = im.resize((150, 150), resample=4) # do not need high quality in downscaling

    if random.random() > 0.5:
        im = im.transpose(PIL.Image.FLIP_LEFT_RIGHT) # very powerful

    filenames = []
    # write a file with the hash as the filename
    filename_ori = hashlib.md5(im.tobytes()).hexdigest()
    filenames.append(filename_ori)

    im2 = im.convert('HSV')

    pixels = list(im2.getdata())

    hue_skew = random.randint(42,72)
    im2.putdata([((x[0]+hue_skew)%256, x[1], x[2])  for x in pixels])
    im2 = im2.convert('RGB')
    filename_1 = hashlib.md5(im2.tobytes()).hexdigest()
    im2.save(filename_1 + '.jpg') # add path
    filenames.append(filename_1)

    hue_skew = random.randint(108,148)
    im2.putdata([((x[0]+hue_skew)%256, x[1], x[2])  for x in pixels])
    im2 = im2.convert('RGB')
    filename_2 = hashlib.md5(im2.tobytes()).hexdigest()
    im2.save(filename_2 + '.jpg') # add path
    filenames.append(filename_2)

    hue_skew = random.randint(184,214)
    im2.putdata([((x[0]+hue_skew)%256, x[1], x[2])  for x in pixels])
    im2 = im2.convert('RGB')
    filename_3 = hashlib.md5(im2.tobytes()).hexdigest()
    im2.save(filename_3 + '.jpg') # add path
    filenames.append(filename_3)

    # log hash -> details
    logging.debug(f"{video_details['filename']} , {frame_details[idx]['framenumber']}")

    previous_frame_hash = current_frame_hash

    # rename the image
    os.rename(jpeg_file, filename_ori + '.jpg')

    image_grouping.append(filenames)

    image_debug_trace[video_details['filename']].extend(filenames)


# move files to completed folder
for filepath in glob(os.path.join(raw_image_folder,'*.jpg')):
    path, file = os.path.split(filepath)
    shutil.move(filepath, os.path.join(completed_image_folder, file))

# finally
# dump image_grouping
with open(os.path.join(completed_image_folder,'image_grouping.pkl'),'wb') as f:
    pickle.dump(image_grouping, f)

served_dir_name = str(int(time.time()))

# dump image_debug_trace
with open(os.path.join('logs',f'challenge_7_image_debug_trace_{served_dir_name}.pkl'),'wb') as f:
    pickle.dump(image_debug_trace, f)

# and move entire folder to challenge dir for serving
shutil.move(completed_image_folder, os.path.join('challenges','7','images',served_dir_name))

# clean up directories
shutil.rmtree(base_folder)








### cropping an image
# target amount that subject bounding box is 40%-60% of overall picture

target_dimension = (125,125)
subject_percentage = (0.4, 0.6) # of each dimension. # must test

# subject has to shrink down to subject_percentage*target_dimension
# use the maximum dimension
# calculate real size

randomized_subject_percentage = random.randint(int(subject_percentage[0]*100), int(subject_percentage[1]*100)) / 100


subject_size_x = video_details['bb'][idx][0][1] - video_details['bb'][idx][0][0]
subject_size_y = video_details['bb'][idx][1][1] - video_details['bb'][idx][1][0]

if subject_size_x > subject_size_y:
    subject_abs_size = randomized_subject_percentage * target_dimension[0]
    resized_percentage = subject_size_x / subject_abs_size
else:
    subject_abs_size = randomized_subject_percentage * target_dimension[1]
    resized_percentage = subject_size_y / subject_abs_size

# vary the l/r crop %
    # KISS and focus on objective
    # cropping should alr destroy color layout descriptor
    # don't bother with background stuff
crop_lr_ratio = random.randint(0,100) / 100
# but we need to constrain by the available image as well...

# 150x150 is pretty damn small, so maybe don't overcrop
# randomize the shorter side first, then take the other side


crop_x = video_details['resolution'][0]




#im = Image.open(r"C:\Users\loh.je\Downloads\1.jpg")
im = Image.open(r"2.jpg")
left, upper, right, lower = 800,400,1500,1700


im = im.crop((left, upper, right, lower))

im.show()

im = im.resize((100, 150)) # must maintain aspect latio


if random.random() > 0.5:
    im = im.transpose(PIL.Image.FLIP_LEFT_RIGHT) # very powerful

# if google is using edges or whatever, then adding random objects would be really good
# for our use-case, adding random objects is okay!
# what the fuck adding random objects doesn't work
# what the fuck covering almost the whole picture doesn't work
#

# try a natural landscape picture, cropping is more effective there


# border is worthless to google

# we can see google uses overall color information as well - but identifying original image can't be using that...




## lighting level, do after cropping because slow
im2 = im.convert('HSV')

pixels = im2.load()

# seems useless
for i in range(im.size[0]): # for every pixel: # TO DO TEST AGAINST GOOGLE (with some cropping)
    # find the range, and random between that
    # min to work, max to visually same
    # actually works, but not for all images. landscape is fine, don't even need to flip ( assuming heavy resize)
    # 50,40,10 minimum
    # 2.1 1.8, 1.05 minimum
    for j in range(im.size[1]):
        if pixels[i,j][2] < 50:
            pixels[i,j] = (pixels[i,j][0], pixels[i,j][1], int((pixels[i,j][2] + 0 ) * 1.3 ))
            pass
        elif pixels[i,j][2] < 100:
            pixels[i,j] = (pixels[i,j][0], pixels[i,j][1], int((pixels[i,j][2] + 10) * 1.2))
            pass
        elif pixels[i,j][2] < 200:
            pixels[i,j] = (pixels[i,j][0], pixels[i,j][1], int(pixels[i,j][2] * 1.05))
            pass


im2.convert('RGB').save(r"C:\Users\loh.je\Downloads\2.jpg")
im2.convert('RGB').save("3.jpg")
## apply tint

im2 = im2.convert('RGB')

pixels = im2.load()

# strong tint doesn't work lol
for i in range(im.size[0]):
    for j in range(im.size[1]):
        pixels[i,j] = (pixels[i,j][0], pixels[i,j][1] + 50, pixels[i,j][2] + 50)

im2.show()




##


im2.convert('RGB').save(r"C:\Users\loh.je\Downloads\2.jpg")
# just save as is
# we done here








########## practicality

# process_videos.py creates annotation from videos
# server.py gens the images using annotations from video
# flask_core serves randomized selected images only, using glob *.txt
## image names are hashed to prevent enumeration



################## goal

## make it hard to neural network?
# not possible, if they can neural network, they win
    # - or is it? adversarial pixel attacks?
# challenge 8 will try to come up with something that neural networks cant win

## make it super hard for CBIR
# crop !!!
# add border !! - same as crop?
# flip is lame? - only a x2, might not bother, or if easy enough just do
# tint that shit - can't tint it too much doesn't look nice, have to experiment
# change light levels!, especially brighten it for easier recognition. ! - do non-linear

#### afterword
# store all images and correct/wrong statistics for QA purposes



# run ffmpeg
