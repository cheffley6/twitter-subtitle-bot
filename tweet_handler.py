from config import misc
from downloader import *

def process_one_video(tweet_id):
    download(tweet_id, misc.LATEST_VIDEO_NAME)

