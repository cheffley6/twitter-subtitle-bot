# twitter-subtitle-bot

## Operation:
`delete_tweets_job.py` should run every fifteen minutes. It checks if original tweets can no
longer be publicly accessed and, if so, deletes the bot tweet(s) of the subtitled video
(or transcription text, or "We couldn't find a video" message, etc). This is done to protect
users' privacy.

