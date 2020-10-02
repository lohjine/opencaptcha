# Concepts for each CAPTCHA, why they work, and when they don't work

### Q: Why am I giving out the secrets?!

This project is open source, so any motivated attacker can go through the repository to find out everything they need. By explaining the ideas and implementations behind the various CAPTCHAs, I hope that it can stimulate discussion regarding the effectiveness and possibly come up with improvements.


## Level 1:

### Description

The challenge involves waiting for 1 second before submitting a standard string to the /solve endpoint.

### Why it works

The simplest, most common bots do not execute Javascript. So there's no real need to inconvenience the user beyond a simple 1 second wait.

### When it doesn't work

When the bot executes Javascript.

## Level 2: (TODO)

## Level 3:

### Description

The challenge involves pressing a button.

### Why it works

Even with the execution of Javascript, it is not obvious to the bot that the button has to be pressed to solve the CAPTCHA.

### When it doesn't work

When the bot has logic to detect CAPTCHA boxes and clicks every button in it.

## Level 4:

### Description

The challenge involves pressing 1 button out of 2 available options.

### Why it works

Even with the execution of Javascript, it is not obvious to the bot as to which button has to be pressed to solve the CAPTCHA.

### When it doesn't work

When the bot is written to look for the correct button to click, or randomly chooses for a 50% success rate.

## Level 5:

### Description

The challenge involves writing a provided word into an input field.

### Why it works

Bots can't read English to understand what the challenge entails.

### When it doesn't work

When the bot is written to detect the provided word and enter it into the input field.

## Level 6:

### Description

The challenge involves reading a word in an image, or solving a simple math problem in an audio clip, and submitting the word. The visual task of copying a word is easier than solving a math problem, but the audio task of transcribing a spoken word can be very difficult depending on the word, and solving a math problem is easier.

### Why it works

There is no simple programmatic way to derive words from an image or an audio clip.

### When it doesn't work

There are available OCR / Transcription libraries that can recognise text from images or speech from audio clips.

## Level 7:

### Description

The challenge involves identifying hue-skewed images, or animal sounds in an audio clip.

Images are taken from videos to widen the input space (a 1-min video clip at 30fps contains 1800 images). Images are also modified to make reverse search even harder, using principles derived from [WAIT](https://trace.moe/faq). 

For the audio challenge, audio samples are mixed with background music and noise, to make it very hard to extract the pure animal audio sample.

### Why it works

Image classification is much harder than recognising text, and usually requires a neural network model, which makes attacks much more expensive. 

The reason for not doing an animal or object identification challenge is because there is an abundance of cloud animal/object identification services. For example, Amazon Rekognition will label images for a baseline price of $1/1000 images, and does really well on Recaptcha tasks ([link](https://news.ycombinator.com/item?id=24272858)). 

However, hue-skewed images tend to be identified with the same label and similar confidences as the original image.

Audio recognition is a less-researched field, and would take significant effort to produce a model that will work.

### When it doesn't work

When the bot author trains a neural network specifically to complete this task. Using fastai and finetuning a ResNet model for 5 epochs, an accuracy of 99% can be achieved.

For animal sounds, the only available model I can find is [this](https://lis-unicamp.github.io/current-projects/wasis/). Otherwise a neural network approach or Shazam-like method could work.

## Level 8-10: (TODO)


# Anti-bot techniques common to all CAPTCHA levels

* A minimum solve time is applied as a form of rate-limiting
* Dynamic challenge levels/CAPTCHA types make it more time-consuming for bot writers to code against
* IP blacklists
* IP rate-limiting

# WONTDO: techniques that will not be implemented

* Fingerprinting methods that have a chance of false positives, especially for users with special needs [eg](https://news.ycombinator.com/item?id=22114108).
* Minimal effort will be put into detecting fingerprints that are specific to botting behaviour, such as headless browser properties. Reason being that this is an eternal cat-and-mouse game, and being open source, we are at a huge disadvantage because bypasses can be easily written.
* Building user profiles