# OpenCaptcha

OpenCaptcha is an open source, user-friendly, privacy-focused captcha. Currently in pre-alpha.

## Guiding Principles

* Simple to install
* Apply the minimum possible inconvenience to users (https://nearcyan.com/you-probably-dont-need-recaptcha/)
* Respect privacy

## Features

* OpenCaptcha is as easy to install as ReCaptcha/hCaptcha
* Depending on your needs, you may configure OpenCaptcha for different level of challenges. The simplest challenges do not require user input.
* ~~OpenCaptcha can automatically ramp up difficulty during suspected bot activity or traffic spikes~~ TODO
* You can self-host OpenCaptcha so that your user data remains safe with you



## Try it out

You may try out the captcha at [https://opencaptcha.lohjine.com](https://opencaptcha.lohjine.com)


## Captcha concepts

See [concepts.md](concepts.md)

## Installation (using hosted service)

Current available hosted services:
* https://opencaptcha.lohjine.com

1. Register at hosted service to obtain a SITE-KEY and SITE_SECRET, as well as configure settings.

2. Add the following two elements to the page/form that you want to protect (e.g. account creation)

```
<head>
    <script src="<URL>/opencaptcha.js"> </script>
</head>
```

```
<form>
    <div id="opencaptcha" data-site-key="<SITE-KEY>"> </div>
</form>
```

2.5. On Captcha success, OpenCaptcha adds a field "opencaptcha-response" into your form, this contains an OpenCaptcha response token.

3. In your form validation code, send a POST request to <URL>/verify with the following parameters:

* response (required): OpenCaptcha response token that was submitted
* site_secret (required): Your SITE_SECRET

The endpoint will return a JSON with the following two fields:

* success (boolean)
* error (string/null) : If success is False, then error will be a string. Possible error strings can be found in flask_core.py



## Self-hosting

```
git clone https://github.com/lohjine/opencaptcha
cd opencaptcha

# Edit settings.ini and redis.conf as necessary
vim settings.ini
vim redis.conf

# (Optional, Recommended) Set up python virtualenv and activate it
pip3 install virtualenv && virtualenv venv
source venv/bin/activate

# If Redis backend is desired:
## Set up Redis
bash scripts/setupredis.sh
## Start Redis
bash scripts/startredis.sh

# Install python requirements
pip3 install -r requirements.txt

# Start server.py
python3 server.py &

# Serve app in flask_core.py using your web application stack
# For a wsgi/nginx example, refer to https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uswgi-and-nginx-on-ubuntu-18-04
# Or in dev mode, run:
# python3 flask_core.py

# Proceed with step 2 of Installation section above
```

Additional requirements for challenge level 7

```
sudo apt install ffmpeg

# Ensure that ffmpeg is added to PATH

# Place suitable animal/background audio files in challenges/7/audio
# A small set of video files obtained from Pexels are provided.
# A small set of audio files obtained from Zapsplat and Freesound are provided.

# Pre-process challenge 7 videos/audio
python scripts/preprocess_challenge_7.py
python scripts/preprocess_audio_challenge_7.py

# Place videos in challenges/7/videos
# Allow server.py to be executed and wait for it to generate challenge 7 images, before running flask_core.py
```


## Todo

* Implement challenges for higher difficulties (>= 8)
* IP rate-limiting
* More sophisticated bot detection techniques
* Style elements to look nicer / UX


## Contributing

Discussions/feedback on the usefulness of current challenges and suggestions for improvements or more challenges are welcomed. Please open an issue for it.

If you maintain a website with sizable bot traffic and are willing to test dev changes, please do reach out!