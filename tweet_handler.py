from config import misc, twitter_credentials
from urllib.request import urlretrieve
from pprint import pprint
from twython import Twython
import ffmpeg


twitter = Twython(
    twitter_credentials.TWITTER_CONSUMER_KEY, twitter_credentials.TWITTER_CONSUMER_SECRET,
    twitter_credentials.TWITTER_ACCESS_KEY, twitter_credentials.TWITTER_ACCESS_SECRET)

def download_video(id):
    tweet = twitter.show_status(id=id)
    pprint(tweet['text'])

    # problem: twitter doesn't allow you to fetch the raw video for some tweets
    video_url = tweet['extended_entities']['media'][0]['video_info']['variants'][0]['url']

    urlretrieve(video_url, misc.LATEST_VIDEO_NAME)

# writes video's audio to LATEST_AUDIO_NAME
def write_video_to_audio_file():
    video_path = misc.LATEST_VIDEO_NAME
    stream = ffmpeg.input(video_path)
    audio = stream.audio
    stream = ffmpeg.output(audio, misc.LATEST_AUDIO_NAME).overwrite_output()
    ffmpeg.run(stream)   


def reply_to_tweet(text, tweet_id):
    while len(text) > 0:
        # convert into multiple tweets
        response = twitter.update_status(status=text[:280], in_reply_to_status_id=tweet_id)
        tweet_id = response['id']
        text = text[280:]

def process_one_video(tweet_id, mention_id):
    download_video(tweet_id)
    write_video_to_audio_file()

    text = "nope" # later this should be assigned to the speech-to-text result
    reply_to_tweet(text, mention_id)
