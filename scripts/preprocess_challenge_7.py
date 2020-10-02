import sys
import os
# https://stackoverflow.com/a/27876800
sys.path.append( os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) ) )
from opencaptcha_lib import gen_toml_file

print('Preprocessing challenge 7 by running gen_toml_file...')

gen_toml_file()

print('Preprocessing complete!')