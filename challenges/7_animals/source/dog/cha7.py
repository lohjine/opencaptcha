




#

get number of frames

ffprobe -v error -select_streams v:0 -show_entries stream=nb_frames -of default=nokey=1:noprint_wrappers=1 input.mp4


# then choose a number of frames per video

# we probably want to assume that each video is roughly the same
# - real time
# - sufficient movement
# - always in frame


## might want to annotate?
## probably need, because target must be a % of the image..

## should do an automated version to make life simpler.
# use yolov4 to compute annotation
# find bounding box of dog over entire video.


# don't want to choose too many frames

# safe to assume fps is either 24/30

# we probably want 1 frame/second, so


### should we preprocess ALL possible images?
## doesn't make sense because video is compressed form - which is what we want

## problem of 



## make it hard to neural network?
# not possible, if they can neural network, they win
# challenge 8 will try to come up with something that neural networks cant win

## make it super hard for CBIR
# crop !!!
# add border !! - same as crop?
# flip is lame? - only a x2, might not bother, or if easy enough just do
# tint that shit - can't tint it too much doesn't look nice, have to experiment
# change light levels!, especially brighten it for easier recognition. ! - do non-linear





# run ffmpeg 


ffmpeg -i myVideo.mov -vf \
    select='eq(n\,1)+eq(n\,200)+eq(n\,400)+eq(n\,600)+eq(n\,800)+eq(n\,1000)' -vsync vfr -q:v 2 %d.jpg