import sys
import os
# https://stackoverflow.com/a/27876800
sys.path.append( os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) ) )
from opencaptcha_lib import normalize_audio_in_directory

print('Running normalization...')

normalize_audio_in_directory(os.path.join('challenges','7','audio','animals'), target_db=-27)

normalize_audio_in_directory(os.path.join('challenges','7','audio','background'), target_db=-30)

print('Normalization complete!')