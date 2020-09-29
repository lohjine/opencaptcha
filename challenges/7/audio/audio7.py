# -*- coding: utf-8 -*-
"""
Created on Tue Sep 29 16:11:26 2020

@author: loh.je
"""

from pydub import AudioSegment
sound1 = AudioSegment.from_file(r"labrador-barking-daniel_simon.mp3", format="mp3")
sound2 = AudioSegment.from_file(r"doberman-pincher_daniel-simion.mp3", format="mp3")

played_togther = sound1.overlay(sound2)


from pydub import AudioSegment

sound1 = AudioSegment.from_file(r"labrador-barking-daniel_simon.wav")
sound2 = AudioSegment.from_file(r"doberman-pincher_daniel-simion.wav")

played_togther = sound1.overlay(sound2)

played_togther.export("combined.wav", format='wav')