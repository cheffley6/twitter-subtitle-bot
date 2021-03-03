# twitter-subtitle-bot

## Operation:
`delete_tweets_job.py` should run every fifteen minutes. It checks if original tweets can no
longer be publicly accessed and, if so, deletes the bot tweet(s) of the subtitled video
(or transcription text, or "We couldn't find a video" message, etc). This is done to protect
users' privacy.

## Open sourcing this
This repo should remain private until we've verified that we never uploaded keys or credentials
into the git log at any point. If there was a key uploaded, we should migrate this code to
a new repository.

