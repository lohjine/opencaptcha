# Concepts for each CAPTCHA, why they work, and when they don't work

## Level 1:

### Description

The challenge involves waiting for 1 second before submitting a standard string to the /solve endpoint.

### Why it works

The simplest, most common bots do not execute Javascript. So there's no real need to inconvenience the user beyond a simple 1 second wait.

### When they don't work

If the bot executes Javascript.

## Level 3:

### Description