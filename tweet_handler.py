from config import misc
from downloader import *

def process_one_video(tweet_id):
    download(tweet_id, misc.LATEST_VIDEO_NAME)
    # audio_path = convert_to_audio(video_path)
    # google_storage_uri = upload_to_cloud(audio_path)
    # response = recognize(AUDIO_CONFIG, google_storage_uri)
    # reply(status, response)

