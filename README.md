# twitter-subtitle-bot

## About
Account URL: https://twitter.com/videosubtitle

This bot, when mentioned in reply to a video on Twitter, replies with a captioned version of the video
if the video is less than 140 seconds.

## Data Retention
`delete_tweets_job.py` runs on our server every fifteen minutes. It checks if original tweets can no
longer be publicly accessed and, if so, deletes the bot tweet(s) of the subtitled video
(or "We couldn't find a video" message, etc). This is done to protect users' privacy.

