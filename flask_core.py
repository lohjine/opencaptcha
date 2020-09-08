from flask import Flask, Blueprint, redirect, render_template, send_from_directory
from flask import request, url_for, abort, make_response, jsonify
from opencaptcha_lib import DBconnector, site_secret_length, site_key_length, token_length, challenge_id_length
import random
import string
import pendulum
import configparser
import logging
from challenges.wordlist import wordlist
import os
from PIL import Image, ImageDraw, ImageFont
import base64
from io import BytesIO

app = Blueprint('app', __name__)

dirname = os.path.dirname(__file__)

config = configparser.ConfigParser()
config.read(os.path.join(dirname, 'settings.ini'))
site_url = config['site']['url']

with open(os.path.join(dirname, 'static/js/opencaptcha.js'), 'r') as f:
    opencaptchajs = f.read()
opencaptchajs = opencaptchajs.replace('{{SITE_URL}}', site_url)

db_connection = DBconnector()


with open(os.path.join(dirname, 'challenges/waitchallenge.js'), 'r') as f:
    challenge1 = f.read()
with open(os.path.join(dirname, 'challenges/simplebuttonchallenge.js'), 'r') as f:
    challenge3 = f.read()
with open(os.path.join(dirname, 'challenges/hardbuttonchallenge.js'), 'r') as f:
    challenge4 = f.read()
with open(os.path.join(dirname, 'challenges/copywordchallenge.js'), 'r') as f:
    challenge5 = f.read()
with open(os.path.join(dirname, 'challenges/copywordchallenge_image.js'), 'r') as f:
    challenge6 = f.read()


@app.route('/<path:text>')
def opencaptcha(text):
    """
    Returns request for any js file as our sole js file
    """
    if text[-3:] == '.js':
        return opencaptchajs  # only continue working on polymorphic track once bot authors actually code against us
    else:
        abort(404)


@app.route('/request', methods=['POST'])
def requestchallenge():

    site_key = request.form.get('site_key', None)
    ip = request.remote_addr

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

    try:
        # gen a challenge according to input parameters
        if challenge_level <= 1:
            answer = 'a'
            challenge = challenge1.replace('{{CHALLENGE_ID}}', challenge_id).replace('{{SITE_URL}}', site_url)

        elif challenge_level == 2: # TODO: change this up, but we need something creative that is no-input, but can break bots
            # how about every x secs, do a swap or append, then submit at the end. can randomize?
            answer = 'a'
            challenge = challenge1.replace('{{CHALLENGE_ID}}', challenge_id).replace('{{SITE_URL}}', site_url)

        elif challenge_level == 3:
            answer = 'a'
            challenge = challenge3.replace('{{CHALLENGE_ID}}', challenge_id).replace('{{SITE_URL}}', site_url)

        elif challenge_level == 4: # change this up. simplest is doubling the button, but this only cuts random chance by half...
            # we can create multiple invisible buttons?! -> at this point might as well roll this into 3
            # challenge level is about the inconvenience posed to users, which hopefully scales well with bot protection
            # or maybe can consider it a minor objective to slow down human-bot behaviour
            answer = random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits)
            decoy = random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits)

            challenge = challenge4.replace('{{CHALLENGE_ID}}', challenge_id).replace('{{SITE_URL}}', site_url). \
                        replace('{{RIGHT}}',answer).replace('{{WRONG}}',decoy)

        elif challenge_level == 5:
            challenge = challenge5.replace('{{CHALLENGE_ID}}', challenge_id).replace('{{SITE_URL}}', site_url)

            answer = random.choice(wordlist)
            challenge = challenge.replace('{{WORD}}', answer)

        elif challenge_level >= 6: # not blind-friendly, can do a TTS version
            challenge = challenge6.replace('{{CHALLENGE_ID}}', challenge_id).replace('{{SITE_URL}}', site_url)

            answer = random.choice(wordlist)

            image = Image.new('RGB', (80, 25), color = 'white')
            d = ImageDraw.Draw(image)
            font = ImageFont.truetype('challenges/fonts/cour.ttf', 14)
            d.text((5,5), answer, font=font, fill=(0,0,0))
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

            challenge = challenge.replace('{{IMG}}', img_str)

        elif challenge_level == 7:
            pass
        elif challenge_level == 8:
            pass
        elif challenge_level == 9:
            pass
        elif challenge_level >= 10:
            pass
        # record challenge to db
        db_connection.set(challenge_id, {'site_secret': site_secret,
                                         'expires': pendulum.now(tz=0).replace(microsecond=0).add(minutes=5).to_iso8601_string(),
                                         'ip': request.remote_addr,
                                         'answer': answer},
                          expire=3600)
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

    if answer != challenge_details['answer']:
        # TODO, delete challenge_id
        return jsonify({'success': False, 'error': 'Wrong answer'})

    # answer is correct, generate token and record in database
    site_secret = challenge_details.get('site_secret', '')

    token = ''.join(
        random.SystemRandom().choice(
            string.ascii_lowercase +
            string.ascii_uppercase +
            string.digits) for _ in range(token_length))
    db_connection.set(token, {'site_secret': site_secret,
                              'expires': pendulum.now(tz=0).replace(microsecond=0).add(minutes=2).to_iso8601_string(),
                              'ip': request.remote_addr},
                      expire=3600)

    return jsonify({'success': True, 'token': token})


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

    if pendulum.from_format(token_details['expires'], 'YYYY-MM-DDTHH:mm:ssZZ') < pendulum.now():
        return jsonify({'success': False, 'error': 'Response token expired'})

#    if token_details['used'] == True:
#        return jsonify({'success': False, 'error': 'Response token has already been used'})s

#    if ip is not None:
#        if ip != token_details['ip']:
#            return jsonify({'success':False,'error':'IP does not match'}) # TODO disable this first?

    if site_secret.strip() == token_details['site_secret']:
        #        token_details['used'] = True
        db_connection.delete(token)
        return jsonify({'success': True, 'error': None})
    else:
        return jsonify({'success': False, 'error': 'Response token is for a different site key'})


@app.route('/robots.txt')
def robots():
    return send_from_directory(os.path.join(dirname, 'static/txt'), 'robots.txt')

@app.route('/test', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        print(request.form)

    return send_from_directory(os.path.join(dirname,'static/js'), 'test.html')


if __name__ == '__main__':
    flask_app = Flask(__name__)
    flask_app.register_blueprint(app)
    flask_app.run(debug=True, port=5555)
