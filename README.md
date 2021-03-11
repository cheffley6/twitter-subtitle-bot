# twitter-subtitle-bot

## About
Account URL: https://twitter.com/videosubtitle

This bot, when mentioned in reply to a video on Twitter, replies with a captioned version of the video
if the video is less than 140 seconds.

## Data Retention
`delete_tweets_job.py` runs on our server every ten minutes. This script checks if original tweets
can no longer be publicly accessed and, if so, deletes tweet(s) from the bot of the subtitled video
(or the bot's "We couldn't find a video" message, etc). This ensures that no copies of a video are
retained in the case that a user changes their account to private or their original tweet is deleted.
