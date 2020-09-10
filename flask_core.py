from flask import Flask, Blueprint, redirect, render_template, send_from_directory
from flask import request, url_for, abort, make_response, jsonify
from opencaptcha_lib import DBconnector, site_secret_length, site_key_length, token_length, challenge_id_length
import random
import string
import time
import configparser
import logging
from challenges.wordlist import wordlist
import os
from PIL import Image, ImageDraw, ImageFont
import base64
from io import BytesIO
import pyttsx3
from glob import glob
import json

app = Blueprint('app', __name__)

dirname = os.path.dirname(__file__)

config = configparser.ConfigParser()
config.read(os.path.join(dirname, 'settings.ini'))
site_url = config['site']['url']

with open(os.path.join(dirname, 'static/js/opencaptcha.js'), 'r') as f:
    opencaptchajs = f.read()
opencaptchajs = opencaptchajs.replace('{{SITE_URL}}', site_url)

db_connection = DBconnector()

engine = pyttsx3.init()
engine.setProperty('rate', 145)

with open(os.path.join(dirname, 'challenges','waitchallenge.js'), 'r') as f:
    challenge1 = f.read()
with open(os.path.join(dirname, 'challenges','simplebuttonchallenge.js'), 'r') as f:
    challenge3 = f.read()
with open(os.path.join(dirname, 'challenges','hardbuttonchallenge.js'), 'r') as f:
    challenge4 = f.read()
with open(os.path.join(dirname, 'challenges','copywordchallenge.js'), 'r') as f:
    challenge5 = f.read()
with open(os.path.join(dirname, 'challenges','copywordchallenge_image.js'), 'r') as f:
    challenge6 = f.read()
with open(os.path.join(dirname, 'challenges','copywordchallenge_audio.js'), 'r') as f:
    challenge6_audio = f.read()
with open(os.path.join(dirname, 'challenges','animalchallenge.js'), 'r') as f:
    challenge7 = f.read()
challenge7_animals = os.listdir(os.path.join(dirname, 'challenges','7_animals','source'))

@app.route('/<path:text>')
def opencaptcha(text):
    """
    Returns request for any js file as our sole js file
    """
    if text[-3:] == '.js':
        return opencaptchajs  # only continue working on polymorphic track once bot authors actually code against us
    else:
        abort(404)


@app.route('/challenges/audio/<path:text>')
def audio_challenge(text):
    return send_from_directory(os.path.join(dirname, 'challenges','audio'), text)


@app.route('/request', methods=['POST'])
def requestchallenge():

    site_key = request.form.get('site_key', None)
    blind = request.form.get('blind', None)

    # retrieve base challenge level from site settings
    if site_key is not None:
        site_details = db_connection.get(site_key, None)
        if site_details is None:
            return jsonify({'success': False, 'error': 'Invalid site key'})
        challenge_level = int(site_details['challenge_level'])
        site_secret = site_details['site_secret']
    else:
        challenge_level = int(request.form.get('challenge_level', 1))
        site_secret = ''

    challenge_id = ''.join(
        random.SystemRandom().choice(
            string.ascii_lowercase +
            string.ascii_uppercase +
            string.digits) for _ in range(challenge_id_length))

    challenge_level = 6

    min_time = time.time() + 1

    try:
        # gen a challenge according to input parameters
        # https://github.com/desirepath41/visualCaptcha/issues/24
        if challenge_level <= 1:
            answer = 'a'
            challenge = challenge1.replace('{{CHALLENGE_ID}}', challenge_id).replace('{{SITE_URL}}', site_url)

        elif challenge_level == 2: # TODO: change this up, but we need something creative that is no-input, but can break bots
            # how about every x secs, do a swap or append, then submit at the end. can randomize?
            answer = 'a'
            challenge = challenge1.replace('{{CHALLENGE_ID}}', challenge_id).replace('{{SITE_URL}}', site_url)

        elif challenge_level == 3:
            answer = 'a'
            min_time = time.time() + 0.5
            challenge = challenge3.replace('{{CHALLENGE_ID}}', challenge_id).replace('{{SITE_URL}}', site_url)

        elif challenge_level == 4: # change this up. simplest is doubling the button, but this only cuts random chance by half...
            # we can create multiple invisible buttons?! -> at this point might as well roll this into 3
            # challenge level is about the inconvenience posed to users, which hopefully scales well with bot protection
            # or maybe can consider it a minor objective to slow down human-bot behaviour
            answer = random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits)
            decoy = random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits)

            min_time = time.time() + 0.5

            challenge = challenge4.replace('{{CHALLENGE_ID}}', challenge_id).replace('{{SITE_URL}}', site_url). \
                        replace('{{RIGHT}}',answer).replace('{{WRONG}}',decoy)

        elif challenge_level == 5:
            challenge = challenge5.replace('{{CHALLENGE_ID}}', challenge_id).replace('{{SITE_URL}}', site_url)

            answer = random.choice(wordlist)
            challenge = challenge.replace('{{WORD}}', answer)

        elif challenge_level >= 6:

            if blind:
                challenge = challenge6_audio.replace('{{CHALLENGE_ID}}', challenge_id).replace('{{SITE_URL}}', site_url)

                a = random.randint(0,49)
                b = random.randint(0,49)

                answer = str(a + b)

                filename = str(random.randint(0,1000)) + str(time.time())# create a unique filename
                filename = filename.replace('.','') + '.mp3'
                diskpath = os.path.join(dirname, 'challenges','audio',filename)
                webpath = 'challenges/audio/' + filename

                engine.save_to_file(f'What is {a} plus {b}', diskpath)
                engine.runAndWait()
                # pyttsx3 only allows saving to disk, we can fork the library if perf is an issue
                # NVM person might want to retrieve it again?!, or this is the best way to present the flow

                challenge = challenge.replace('{{AUDIO}}', webpath)

            else:
                challenge = challenge6.replace('{{CHALLENGE_ID}}', challenge_id).replace('{{SITE_URL}}', site_url)

                answer = random.choice(wordlist)

                image = Image.new('RGB', (80, 25), color = 'white')
                d = ImageDraw.Draw(image)
                font = ImageFont.truetype(os.path.join(dirname, 'challenges','fonts','cour.ttf'), 14)
                d.text((5,5), answer, font=font, fill=(0,0,0))
                buffered = BytesIO()
                image.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

                challenge = challenge.replace('{{IMG}}', img_str)

        elif challenge_level >= 7: # assume they will ocr/transcribe at this point
            # might want to do animal images / sounds
            # but open source how are we going to permutate this?! - maybe frames from dog videos are better!!
            # take inspiration from WAIT on how to make reversing it hard!
            # for sounds, i am not expert, but applying background music and noise should make it hard to match up to originals!

            if blind:
                pass
            else:
                # choose a random answer
                correct_animal = random.choice(challenge7_animals)
                wrong_animals = challenge7_animals.copy()
                wrong_animals.remove(correct_animal)
                number_matching = random.randint(2,8)

                answer = [0,1,2,3,4,5,6,7,8,9]
                random.shuffle(answer)
                answer = answer[:number_matching]

                # look for the latest folder to sample from
                # do it individually for each animal to prevent race conditions
                latest_folders = {}

                for i in challenge7_animals:
                    available_folders = os.listdir(os.path.join(dirname, 'challenges','7_animals','images',challenge7_animals[0]))
                    available_folders.sort()
                    latest_folders[i] = glob(os.path.join(dirname, 'challenges','7_animals','images',i,available_folders[-1],'*'))

                images = []
                for i in range(10):
                    if i in answer:
                        images.append(random.sample(latest_folders[correct_animal],1))
                    else:
                        wrong_animal = random.choice(wrong_animals)
                        images.append(random.sample(latest_folders[wrong_animal],1))

                challenge.replace({{images}}, json.dumps(images))

        elif challenge_level >= 8: # assume they will do basic ML at this point
            pass
        elif challenge_level >= 9:
            pass
        elif challenge_level >= 10:
            pass
        # record challenge to db
        db_connection.set(challenge_id, {'site_secret': site_secret,
                                         'expires': int(time.time()) + 5 * 60,
                                         'ip': request.remote_addr,
                                         'answer': answer,
                                         'min_time': min_time},
                          expire=300)
        return challenge
    except Exception as e:
        logging.error(f"Challenge generation failed: {e}")
        return abort(500)


@app.route('/solve', methods=['POST'])
def solvechallenge():

    challenge_id = request.form.get('challenge_id', None)
    answer = request.form.get('answer', None)

    # check challenge completed correctly
    if challenge_id is None:
        return jsonify({'success': False, 'error': 'Missing challenge_id'})

    challenge_details = db_connection.get(challenge_id, None)

    if challenge_details is None:
        return jsonify({'success': False, 'error': 'Invalid challenge_id'})

    if challenge_details['expires'] < time.time():
        return jsonify({'success': False, 'error': 'Challenge expired'})

    try:
        if challenge_details['min_time'] > time.time():
            db_connection.delete(challenge_id)
            return jsonify({'success': False, 'error': 'Wrong answer'})

        if answer != challenge_details['answer']:
            db_connection.delete(challenge_id)
            return jsonify({'success': False, 'error': 'Wrong answer'})

        # answer is correct, generate token and record in database
        site_secret = challenge_details.get('site_secret', '')

        token = ''.join(
            random.SystemRandom().choice(
                string.ascii_lowercase +
                string.ascii_uppercase +
                string.digits) for _ in range(token_length))

        db_connection.delete(challenge_id)
        db_connection.set(token, {'site_secret': site_secret,
                                  'expires': int(time.time()) + 60*2,
                                  'ip': request.remote_addr},
                          expire=120)

        return jsonify({'success': True, 'token': token})
    except:
        return abort(500)
    finally:
        pass # set up for ip rate limiting

@app.route('/verify', methods=['POST'])
def verify():

    token = request.form.get('response', None)
    site_secret = request.form.get('site_secret', None)
    ip = request.form.get('ip', None)

    if token is None:
        return jsonify({'success': False, 'error': 'Response token missing'})

    if site_secret is None:
        return jsonify({'success': False, 'error': 'Site_secret missing'})

    token_details = db_connection.get(token.strip())

    if token_details is None:
        return jsonify({'success': False, 'error': 'Response token is invalid'})

    if token_details['expires'] < time.time():
        return jsonify({'success': False, 'error': 'Response token expired'})

# we delete tokens immediately once they are used
#    if token_details['used'] == True:
#        return jsonify({'success': False, 'error': 'Response token has already been used'})

# we do not check IP because of dynamic IP
#    if ip is not None:
#        if ip != token_details['ip']:
#            return jsonify({'success':False,'error':'IP does not match'})

    if site_secret.strip() == token_details['site_secret']:
        #        token_details['used'] = True
        db_connection.delete(token)
        return jsonify({'success': True, 'error': None})
    else:
        return jsonify({'success': False, 'error': 'Response token is for a different site key'})


@app.route('/robots.txt')
def robots():
    return send_from_directory(os.path.join(dirname, 'static','txt'), 'robots.txt')

@app.route('/test', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        print(request.form)

    return send_from_directory(os.path.join(dirname,'static','js'), 'test.html')


if __name__ == '__main__':
    flask_app = Flask(__name__)
    flask_app.register_blueprint(app)
    flask_app.run(debug=True, port=5555)
