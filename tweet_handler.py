from config import misc, twitter_credentials
from urllib.request import urlretrieve
from pprint import pprint
from twython import Twython


twitter = Twython(
    twitter_credentials.TWITTER_CONSUMER_KEY, twitter_credentials.TWITTER_CONSUMER_SECRET,
    twitter_credentials.TWITTER_ACCESS_KEY, twitter_credentials.TWITTER_ACCESS_SECRET)

def download(id, filename):
    tweet = twitter.show_status(id=id)
    pprint(tweet['text'])

    # problem: twitter doesn't allow you to fetch the raw video for some tweets
    video_url = tweet['extended_entities']['media'][0]['video_info']['variants'][0]['url']

    urlretrieve(video_url, filename)

# for now, only convert one video at a time
# TO-DO: determine if speech-to-text requires wav or mp3
# TO-DO:this must write the video's audio into misc.LATEST_AUDIO_NAME
def convert_to_audio():
    video_path = misc.LATEST_VIDEO_NAME
    pass

# TO-DO: this must post a reply to the original tweet with the predicted text from the audio
def reply_to_tweet(text):
    pass

def process_one_video(tweet_id):
    download(tweet_id, misc.LATEST_VIDEO_NAME)
    # audio_path = convert_to_audio(video_path)

