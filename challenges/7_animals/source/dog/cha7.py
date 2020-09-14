
from glob import glob
import toml
import subprocess
import random
import shutil
import hashlib
import logging

#

get number of frames

ffprobe -v error -select_streams v:0 -show_entries stream=nb_frames -of default=nokey=1:noprint_wrappers=1 input.mp4


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


### processing images
# don't want to choose too many frames

# we probably want 1 frame/second, so -> read from metadata
#

# as we process
# also should determine that 'adjacent' frames are not too similar, which also helps to rule out slow motion

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

ffmpeg -i myVideo.mov -vf \
    select='eq(n\,1)+eq(n\,200)+eq(n\,400)+eq(n\,600)+eq(n\,800)+eq(n\,1000)' -vsync vfr -q:v 2 %d.jpg

jpeg_files = glob('*.jpg') # => need to be in order!

for idx, jpeg_file in enumerate(jpeg_files):

    previous_frame_hash = ''

    # check if frame is too similar to previous one
    # no wait can't do here, don't have the image
    if i > 0:
        current_frame_hash = somehash(frame)
        if current_frame_hash == previous_frame_hash:
            # delete image
            os.remove(jpeg_file)
            continue

        # do the image modifications

        # write a file with the hash as the filename
        filename = hashlib.sha256()


        os.remove(jpeg_file)

        # log hash -> details
        logging.debug(f"{filename} - {video_details['filename']} , {frame_details[idx]['framenumber']}")

        previous_frame_hash = current_frame_hash


# now move the files elsewhere
for f in os.listdir(source):
    shutil.move(os.path.join(source, f), dist)

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
