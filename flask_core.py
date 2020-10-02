from opencaptcha_lib import DBconnector, site_secret_length, site_key_length, token_length, challenge_id_length, check_ip_in_lists
from challenges.wordlist import wordlist
from flask import Flask, Blueprint, redirect, render_template, send_from_directory
from flask import request, url_for, abort, make_response, jsonify
import random
import string
import time
import configparser
import logging
import os
from PIL import Image, ImageDraw, ImageFont
import base64
from io import BytesIO
import pyttsx3
from glob import glob
import json
import pickle
from pydub import AudioSegment

app = Blueprint('app', __name__)

dirname = os.path.dirname(__file__)

config = configparser.ConfigParser()
config.read(os.path.join(dirname, 'settings.ini'))
site_url = config['site']['url']

with open(os.path.join(dirname, 'static/js/opencaptcha.js'), 'r') as f:
    opencaptchajs = f.read()
opencaptchajs = opencaptchajs.replace('{{SITE_URL}}', site_url)

db_connection = DBconnector()


with open(os.path.join(dirname, 'challenges', 'waitchallenge.js'), 'r') as f:
    challenge1 = f.read()
with open(os.path.join(dirname, 'challenges', 'simplebuttonchallenge.js'), 'r') as f:
    challenge3 = f.read()
with open(os.path.join(dirname, 'challenges', 'hardbuttonchallenge.js'), 'r') as f:
    challenge4 = f.read()
with open(os.path.join(dirname, 'challenges', 'copywordchallenge.js'), 'r') as f:
    challenge5 = f.read()
with open(os.path.join(dirname, 'challenges', 'copywordchallenge_image.js'), 'r') as f:
    challenge6 = f.read()
with open(os.path.join(dirname, 'challenges', 'copywordchallenge_audio.js'), 'r') as f:
    challenge6_audio = f.read()
with open(os.path.join(dirname, 'challenges', 'colorchallenge.js'), 'r') as f:
    challenge7 = f.read()
with open(os.path.join(dirname, 'challenges', 'animalchallenge_audio.js'), 'r') as f:
    challenge7_audio = f.read()


def update_challenge_7_images(first_run=False, challenge_7_directory=None, challenge_7_files=None):
    """
    Prepares for serving challenge_7_images. Checks for updates to challenge_7_images and replaces current files with the newer ones.
    """

    # check whether new directory
    images = os.listdir(os.path.join(dirname, 'challenges', '7', 'images'))

    if '.gitignore' in images:
        images.remove('.gitignore')

    if len(images) == 0:
        raise ValueError('No available images for challenge 7, either set max_challenge_level = 6 in settings.ini, or run server.py to generate challenge 7 images.')

    # Move the latest challenge_7_directory to end of list
    images.sort()

    if first_run:
        with open(os.path.join(dirname, 'challenges', '7', 'images', images[-1], 'image_grouping.pkl'), 'rb') as f:
            challenge_7_files = pickle.load(f)

        challenge_7_directory = images[-1]
        return challenge_7_directory, challenge_7_files
    else:
        # Update if a newer challenge_7_directory is found
        if images[-1] > challenge_7_directory:
            with open(os.path.join(dirname, 'challenges', '7', 'images', images[-1], 'image_grouping.pkl'), 'rb') as f:
                challenge_7_files = pickle.load(f)

            challenge_7_directory = images[-1]

            return challenge_7_directory, challenge_7_files
        else:
            return None, None


if int(config['captcha']['max_challenge_level']) >= 7:
    challenge_7_directory, challenge_7_files = update_challenge_7_images(first_run=True)

    challenge_7_info = {'directory': challenge_7_directory, 'files': challenge_7_files}


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
    # send_from_directory works weirdly with nested blueprints, causing the base path to be opencaptcha_website/app
    # app.root_path is the same as dirname, except that app.root_path is absolute path
    # both points to opencaptcha_website/app/opencaptcha
    # absolute path fixes the weird behaviour of send_from_directory
    return send_from_directory(os.path.join(app.root_path, 'challenges', 'audio'), text)


@app.route('/challenges/image/<path:text>')
def image_challenge(text):
    # send_from_directory works weirdly with nested blueprints, causing the base path to be opencaptcha_website/app
    # app.root_path is the same as dirname, except that app.root_path is absolute path
    # both points to opencaptcha_website/app/opencaptcha
    # absolute path fixes the weird behaviour of send_from_directory

    directory = request.args.get('directory')

    if not directory.isdigit():
        # only allow numeric directories to prevent security violation by accepting ".." as input
        return abort(400)

    return send_from_directory(os.path.join(app.root_path, 'challenges', '7', 'images', directory), text)


@app.route('/request', methods=['POST'])
def requestchallenge():

    site_key = request.form.get('site_key', None)
    blind = request.form.get('blind', None)

    if site_key is None:
        return abort(400)

    # retrieve base challenge level from site settings
    site_details = db_connection.get_dict(site_key, None)
    if site_details is None:
        return jsonify({'success': False, 'error': 'Invalid site key'})
    challenge_level = int(site_details['challenge_level'])
    site_secret = site_details['site_secret']

    challenge_id = ''.join(
        random.SystemRandom().choice(
            string.ascii_lowercase +
            string.ascii_uppercase +
            string.digits) for _ in range(challenge_id_length))

    penalty_added = check_ip_in_lists(request.remote_addr, db_connection, site_details)

    challenge_level += penalty_added

    if challenge_level > int(config['captcha']['max_challenge_level']):
        challenge_level = int(config['captcha']['max_challenge_level'])

    min_time = time.time() + 1

    try:
        if challenge_level <= 1:
            answer = 'a'
            challenge = challenge1.replace('{{CHALLENGE_ID}}', challenge_id).replace('{{SITE_URL}}', site_url)

        elif challenge_level == 2:  # TODO: change this up, but we need something creative that is no-input, but can break bots
            # how about every x secs, do a swap or append, then submit at the end. can randomize?
            answer = 'a'
            challenge = challenge1.replace('{{CHALLENGE_ID}}', challenge_id).replace('{{SITE_URL}}', site_url)

        elif challenge_level == 3:
            answer = 'a'
            min_time = time.time() + 0.5
            challenge = challenge3.replace('{{CHALLENGE_ID}}', challenge_id).replace('{{SITE_URL}}', site_url)

        elif challenge_level == 4:  # change this up. simplest is doubling the button, but this only cuts random chance by half...
            # we can create multiple invisible buttons?! -> at this point might as well roll this into 3
            # challenge level is about the inconvenience posed to users, which hopefully scales well with bot protection
            # or maybe can consider it a minor objective to slow down human-bot behaviour
            answer = random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits)
            decoy = random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits)

            min_time = time.time() + 0.5

            challenge = challenge4.replace('{{CHALLENGE_ID}}', challenge_id).replace('{{SITE_URL}}', site_url). \
                replace('{{RIGHT}}', answer).replace('{{WRONG}}', decoy)

        elif challenge_level == 5:
            challenge = challenge5.replace('{{CHALLENGE_ID}}', challenge_id).replace('{{SITE_URL}}', site_url)

            answer = random.choice(wordlist)
            challenge = challenge.replace('{{WORD}}', answer)

        elif challenge_level == 6:

            if blind:
                challenge = challenge6_audio.replace('{{CHALLENGE_ID}}', challenge_id).replace('{{SITE_URL}}', site_url)

                a = random.randint(0, 49)
                b = random.randint(0, 9)

                answer = str(a + b)

                filename = str(random.randint(0, 1000)) + str(time.time())  # create a unique filename
                filename = filename.replace('.', '') + '.mp3'
                diskpath = os.path.join(dirname, 'challenges', 'audio', filename)
                webpath = 'challenges/audio/' + filename

                engine = pyttsx3.init()  # not possible to hold this object for multiple threads in prod
                engine.setProperty('rate', 110)
                engine.save_to_file(f'What is {a} plus {b}', diskpath)
                engine.runAndWait()
                del engine

                challenge = challenge.replace('{{AUDIO}}', webpath)

            else:
                challenge = challenge6.replace('{{CHALLENGE_ID}}', challenge_id).replace('{{SITE_URL}}', site_url)

                answer = random.choice(wordlist)

                image = Image.new('RGB', (80, 25), color='white')
                d = ImageDraw.Draw(image)
                font = ImageFont.truetype(os.path.join(dirname, 'challenges', 'fonts', 'cour.ttf'), 14)
                d.text((5, 5), answer, font=font, fill=(0, 0, 0))
                buffered = BytesIO()
                image.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

                challenge = challenge.replace('{{IMG}}', img_str)

        elif challenge_level >= 7:

            if blind:
                challenge = challenge7_audio.replace('{{CHALLENGE_ID}}', challenge_id).replace('{{SITE_URL}}', site_url)

                # choose a random background audio file
                background = random.choice(glob(os.path.join(dirname, 'challenges', '7', 'audio', 'background', '*')))
                background = AudioSegment.from_file(background)

                # choose a random offset out of 15 seconds
                duration = background.duration_seconds
                offset = random.random() * (duration - 15)

                background_cut = background[offset * 1000:(offset + 15) * 1000]

                # choose random overlay timings

                # first timing is between 1 and 2 seconds
                timings = [random.random() + 1]

                # then subsequent timings are random between 2 sec and 3.5 seconds after the previous timing
                for i in range(4):
                    timings.append(2 + random.random() * 2 + timings[-1])

                # ensure that the last timings do not exceed the background sound
                if timings[-1] >= 14:
                    timings[-1] = 14
                    if timings[-2] >= 13:
                        timings[-2] -= 0.5

                # choose random categories for the answers
                categories = glob(os.path.join(dirname, 'challenges', '7', 'audio', 'animals', '*'))

                answers = []
                for i in range(5):
                    answers.append(random.choice(categories))

                # choose random files from the categories
                answers_files = []
                for answer in answers:
                    answers_files.append(AudioSegment.from_file(random.choice(glob(os.path.join(answer, '*')))))

                # overlay the sounds
                final = background_cut
                for idx, answer in enumerate(answers_files):
                    final = final.overlay(answer, position=timings[idx] * 1000)

                filename = '7' + str(time.time()) # append extra character so won't collide with audio from other challenges
                final.export(os.path.join(dirname, 'challenges', 'audio', f"{filename}.mp3"), format="mp3")
                answer = ' '.join([os.path.split(i)[-1] for i in answers])

                webpath = 'challenges/audio/' + filename + '.mp3'

                challenge = challenge.replace('{{AUDIO}}', webpath)

            else:
                challenge = challenge7.replace('{{CHALLENGE_ID}}', challenge_id).replace('{{SITE_URL}}', site_url)

                # check for updates
                challenge_7_directory, challenge_7_files = update_challenge_7_images(first_run=False,
                                                                                     challenge_7_directory=challenge_7_info['directory'],
                                                                                     challenge_7_files=challenge_7_info['files'])

                if challenge_7_directory:
                    challenge_7_info['directory'] = challenge_7_directory
                    challenge_7_info['files'] = challenge_7_files

                # choose 3 random questions
                questions = random.sample(challenge_7_info['files'], k=3)

                correct_answers = set([i[0] for i in questions])

                # select random options
                # but including the correct first option
                questions = [random.sample(i[1:], k=2) + [i[0]] for i in questions]

                for question in questions:
                    random.shuffle(question)

                images = []
                # choose randomly horizontal or vertical layout
                if random.random() > 0.5:
                    # horizontal
                    for question in questions:
                        images.extend(question)
                else:
                    # vertical
                    for i in range(3):
                        for question in questions:
                            images.append(question[i])

                answer = []
                for idx, i in enumerate(images):
                    if i in correct_answers:
                        answer.append(idx)

                answer = ','.join([str(i) for i in answer])  # stringify into js-like format

                challenge = challenge.replace('{{IMAGES}}', json.dumps(images)).replace('{{IMAGE_DIR}}', json.dumps(challenge_7_info['directory']))

        elif challenge_level >= 8:  # assume they will do NN-ML at this point
            pass
        elif challenge_level >= 9:
            pass
        elif challenge_level >= 10:
            pass
        # record challenge to db
        db_connection.set_dict(challenge_id, {'site_secret': site_secret,
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

    challenge_details = db_connection.get_dict(challenge_id, None)

    if challenge_details is None:
        return jsonify({'success': False, 'error': 'Invalid challenge_id'})

    if float(challenge_details['expires']) < time.time():
        return jsonify({'success': False, 'error': 'Challenge expired'})

    try:
        if float(challenge_details['min_time']) > time.time():
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
        db_connection.set_dict(token, {'site_secret': site_secret,
                                       'expires': int(time.time()) + 60 * 2,
                                       'ip': request.remote_addr},
                               expire=120)

        return jsonify({'success': True, 'token': token})
    except BaseException as e:
        logging.error(e)
        return abort(500)
    finally:
        pass  # set up for ip rate limiting


@app.route('/verify', methods=['POST'])
def verify():

    token = request.form.get('response', None)
    site_secret = request.form.get('site_secret', None)
    ip = request.form.get('ip', None)

    if token is None:
        return jsonify({'success': False, 'error': 'Response token missing'})

    if site_secret is None:
        return jsonify({'success': False, 'error': 'Site_secret missing'})

    token_details = db_connection.get_dict(token.strip())

    if token_details is None:
        return jsonify({'success': False, 'error': 'Response token is invalid'})

    if float(token_details['expires']) < time.time():
        return jsonify({'success': False, 'error': 'Response token expired'})

# We currently delete tokens immediately once they are used
#    if token_details['used'] == True:
#        return jsonify({'success': False, 'error': 'Response token has already been used'})

# We do not check IP because of dynamic IP
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
    return send_from_directory(os.path.join(app.root_path, 'static', 'txt'), 'robots.txt')


@app.route('/test', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        print(request.form)

    return send_from_directory(os.path.join(app.root_path, 'static', 'js'), 'test.html')


if __name__ == '__main__':
    flask_app = Flask(__name__)
    flask_app.register_blueprint(app)
    flask_app.run(debug=True, port=5555)
