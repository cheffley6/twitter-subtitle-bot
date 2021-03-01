import os
from datetime import timedelta, datetime
from pprint import pprint

from urllib.request import urlretrieve
from twython import Twython
from librosa import load, resample
import soundfile as sf
import ffmpeg

from config import misc, twitter_credentials
from video_handler import *
from gcp_interface import *
from subtitle_generator import generate_subtitles

from mongo_interface import *




twitter = Twython(
    twitter_credentials.TWITTER_CONSUMER_KEY, twitter_credentials.TWITTER_CONSUMER_SECRET,
    twitter_credentials.TWITTER_ACCESS_KEY, twitter_credentials.TWITTER_ACCESS_SECRET)


    
    

def handle_m3u8(video_url):

        command = "ffmpeg -i {} -bsf:a aac_adtstoasc -vcodec copy -c copy -crf 50 {} -y"
        print('executing: ')
        print(command.format(video_url, misc.LATEST_VIDEO_NAME))
        os.system(command.format(video_url, misc.LATEST_VIDEO_NAME))

VIDEO_LENGTH = 0.0

def download_video(id):
    tweet = twitter.show_status(id=id, tweet_mode="extended")

    # problem: twitter doesn't allow you to fetch the raw video for some tweets
    # pprint(tweet, open("checkmeout3.txt", "w"))
    video_url = None
    try:
        video_url = tweet['extended_entities']['media'][0]['video_info']['variants'][0]['url']
        print("Downloading " + video_url)
        if ".m3u8" in video_url:
            handle_m3u8(video_url)
        else:
            urlretrieve(video_url, misc.LATEST_VIDEO_NAME)
    except:
        raise Exception("Couldn't find video.")

    global VIDEO_LENGTH
    VIDEO_LENGTH = timedelta(seconds=editor.VideoFileClip(misc.LATEST_VIDEO_NAME).duration)
    

    

# writes video's audio to LATEST_AUDIO_NAME
def write_video_to_audio_file():
    video_path = misc.LATEST_VIDEO_NAME
    stream = ffmpeg.input(video_path)
    audio = stream.audio
    stream = ffmpeg.output(audio, misc.LATEST_AUDIO_NAME, ac=1, sample_rate=44100).overwrite_output()
    ffmpeg.run(stream)

    y, s = load(misc.LATEST_AUDIO_NAME)
    y = resample(y, s, misc.TARGET_SAMPLE_RATE)
    sf.write(misc.LATEST_AUDIO_NAME, y, misc.TARGET_SAMPLE_RATE, format='flac')


def reply_to_tweet(tweet_id, author, use_video=False, text=None):
    if use_video:
        video = open('data/final_video.mp4', 'rb')
        response = twitter.upload_video(media=video, media_type='video/mp4')
        response = twitter.update_status(status="Transcribed video for {}.".format(author), media_ids=[response['media_id']], in_reply_to_status_id=tweet_id)
        
        tweet = Tweet(tweet_id)
        reply = Tweet(response['id'], datetime.now())
        tweet.insert_into_mongo([reply])

        print("Reply sent.")
        return
    else:
        tweet = Tweet(tweet_id)
        replies = []
        while len(text) > 0:
            # convert into multiple tweets
            print(tweet_id)
            response = twitter.update_status(status=text[:280], in_reply_to_status_id=tweet_id)
            tweet_id = response['id']
            text = text[280:]
            replies.append(tweet_id)
        tweet.insert_into_mongo(replies)

    print("Reply sent.")

def process_one_video(tweet_id=None, mention_id=None, author=None):
    """For now, replies with stacked tweets for videos longer than 30 seconds,
    and replies with uploaded, captioned video for videos shorter than 30."""

    if author.lower() == "@videosubtitle":
        print("Can't transcribe video for self.")
        return
    try:
        download_video(tweet_id)
    except Exception as e:
        print(e)
        reply_to_tweet(mention_id, author, text=author + " Sorry, we couldn't find a video.")
        return
    
    # For now, don't process a tweet longer than 3 minutes
    if VIDEO_LENGTH.total_seconds() >= 180:
        reply_to_tweet(mention_id, author, text=author + " Sorry, this video is too long to transcribe.")
        return

    write_video_to_audio_file()
    upload_blob()
    stt_response = get_gcs_transcription()

    text = generate_subtitles(stt_response)["text"]
    if os.stat("data/subtitles.srt").st_size == 0:
        reply_to_tweet(mention_id, author, False, author + " Sorry, we weren't able to parse any words from this tweet.")
        return

    if VIDEO_LENGTH.total_seconds() >= 30:
        reply_to_tweet(mention_id, author, False, author + " Video too long to upload. Transcription: " + text)
    else:
        generate_captioned_video()
        reply_to_tweet(mention_id, author, True)