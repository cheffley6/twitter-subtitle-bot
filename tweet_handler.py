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


def process_one_video(tweet_id):
    download(tweet_id, misc.LATEST_VIDEO_NAME)
    # audio_path = convert_to_audio(video_path)
    # google_storage_uri = upload_to_cloud(audio_path)
    # response = recognize(AUDIO_CONFIG, google_storage_uri)
    # reply(status, response)

