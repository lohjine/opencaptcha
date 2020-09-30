# -*- coding: utf-8 -*-
"""
Created on Tue Sep 29 16:11:26 2020

@author: loh.je
"""
import random
import os
import time
from glob import glob

from pydub import AudioSegment
sound1 = AudioSegment.from_file(r"labrador-barking-daniel_simon.mp3", format="mp3")
sound2 = AudioSegment.from_file(r"doberman-pincher_daniel-simion.mp3", format="mp3")

played_togther = sound1.overlay(sound2)




from pydub import AudioSegment

sound1 = AudioSegment.from_file(r"labrador-barking-daniel_simon.wav")
sound2 = AudioSegment.from_file(r"doberman-pincher_daniel-simion.wav")

played_togther = sound1.overlay(sound2)

played_togther.export("combined.wav", format='wav')



# get a background of ~15 second


# overlay 5 animal sounds at random intervals ( on avg ~ 3 secs)

sound2_starts_after_delay = sound1.overlay(sound2, position=5000)




# need to test whether opensource libs can identify!
# ok not really available
# may not be hard but takes effort to create, just like the image version


background = r"tom_chapman_public_places_beach_summer_people_boats_cicada_40m_distance_croatia.mp3"



# choose a random background audio file
background = random.choice(glob(os.path.join('challenges','7','audio','background','*')))
background = AudioSegment.from_file(background)


# choose a random offset out of 15 seconds
duration = background.duration_seconds
offset = random.random() * (duration-15)

background_cut = background[offset*1000:(offset+15)*1000]


## choose random overlay timings

# first timing is between 1 and 2 seconds
timings = [random.random() + 1]

# then subsequent timings are random between 1.5 sec and 3.5 seconds after the previous timing
for i in range(4):
    timings.append(1.5 + random.random() * 2 + timings[-1])

# ensure that the last timings do not exceed the background sound
if timings[-1] >= 14:
    timings[-1] = 14
    if timings[-2] >= 13:
        timings[-2] -= 0.5

# choose random categories for the answers
categories = glob(os.path.join('challenges','7','audio','animals','*'))

answers = []
for i in range(5):
    answers.append(random.choice(categories))

# choose random files from the categories
answers_files = []
for answer in answers:
    answers_files.append(AudioSegment.from_file(random.choice(glob(os.path.join(answer,'*')))))

# overlay the sounds
final = background_cut
for idx, answer in enumerate(answers_files):
    final = final.overlay(answer, position=timings[idx]*1000)

filename = '7' + str(time.time())
final.export(os.path.join('challenges','audio',f"{filename}.mp3"), format="mp3")
answers = ' '.join(answers)

"""
Listen for 5 animal sounds and type the names of the animals in order, separated by spaces.

"""