# Concepts for each CAPTCHA, why they work, and when they don't work

## Level 1:

### Description

The challenge involves waiting for 1 second before submitting a standard string to the /solve endpoint.

### Why it works

The simplest, most common bots do not execute Javascript. So there's no real need to inconvenience the user beyond a simple 1 second wait.

### When it doesn't work

When the bot executes Javascript.

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

Even with the execution of Javascript, it is not obvious to the bot that which button has to be pressed to solve the CAPTCHA.

### When it doesn't work

When the bot is written to look out for the correct button to click via the button label, or randomly chooses for a 50% success rate.

## Level 5:

### Description

The challenge involves writing a provided word into an input field.

### Why it works

Bots can't read English to understand what the challenge entails.

### When it doesn't work

When the bot is written to detect the provided word and enter it into the input field.

## Level 6:

### Description

The challenge involves reading a word in an image, or hearing the word, and submitting the word.

### Why it works

There is no simple programmatic way to derive words from an image or an audio clip.

### When it doesn't work

There are available OCR / Transcription libraries that can recognise text from images or audio clips.





# Anti-bot techniques common to all CAPTCHA levels

* A minimum solve time is applied as a form of rate-limiting.
* Dynamic challenge levels/CAPTCHA types make it more time-consuming for bot writers to code against
* IP blacklists