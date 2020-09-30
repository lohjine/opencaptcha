from opencaptcha_lib import normalize_audio_in_directory
import os

print('Running normalization...')

normalize_audio_in_directory(os.path.join('challenges','7','audio'))

print('Normalization complete!')