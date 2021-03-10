import os
from datetime import timedelta, datetime
from pprint import pprint

from urllib.request import urlretrieve
from twython import Twython

import ffmpeg

from config import misc, twitter_credentials
from video_handler import *
from gcp_interface import upload_blob, get_gcs_transcription
from subtitle_generator import generate_subtitles

from tweet import *

twitter = Twython(
    twitter_credentials.TWITTER_CONSUMER_KEY, twitter_credentials.TWITTER_CONSUMER_SECRET,
    twitter_credentials.TWITTER_ACCESS_KEY, twitter_credentials.TWITTER_ACCESS_SECRET)

def handle_m3u8(video_url):
    command = f"ffmpeg -i {video_url} -bsf:a aac_adtstoasc -vcodec copy -c copy -crf 50 {misc.LATEST_VIDEO_NAME} -y"
    print('executing: ')
    print(command)
    os.system(command)



def download_video(id):
    source_tweet = twitter.show_status(id=id, tweet_mode="extended")

    # pprint(tweet, open("checkmeout3.txt", "w"))
    video_url = None
    try:
        video_url = source_tweet['extended_entities']['media'][0]['video_info']['variants'][0]['url']
        print("Downloading " + video_url)
        if ".m3u8" in video_url:
            handle_m3u8(video_url)
        else:
            urlretrieve(video_url, misc.LATEST_VIDEO_NAME)
    except:
        raise Exception("Couldn't find video.")

    misc.VIDEO_LENGTH = timedelta(seconds=editor.VideoFileClip(misc.LATEST_VIDEO_NAME).duration)
    

def reply_to_tweet(video_tweet, mention_tweet, use_video=False, text=None):
    if use_video:
        video = open('data/final_video.mp4', 'rb')
        response = twitter.upload_video(media=video, media_type='video/mp4',
            media_category='tweet_video', check_progress=True)
        response = twitter.update_status(status="Transcribed video for @{}.".format(mention_tweet.user_screen_name), media_ids=[response['media_id']], in_reply_to_status_id=mention_tweet.id)
        
        reply = Tweet(response['id'], "videosubtitle")
        video_tweet.insert_into_mongo([reply])

        print("Reply sent.")
        return
    else:
        replies = []
        current_tweet_id = mention_tweet.id
        while len(text) > 0:
            # convert into multiple tweets
            response = twitter.update_status(status=text[:280], in_reply_to_status_id=current_tweet_id)
            current_tweet_id = response['id']
            text = text[280:]
            replies.append(Tweet(current_tweet_id, "videosubtitle"))
        video_tweet.insert_into_mongo(replies)

    print("Reply sent.")

def handle_tweet(video_tweet, mention_tweet):
    """For now, replies with stacked tweets for videos longer than 30 seconds
    and less than 3 minutes, and replies with uploaded, captioned video for
    videos shorter than 30 seconds."""

    print(f"Received request to caption tweet https://twitter.com/fake_username/status/{video_tweet.id}")

    if video_tweet.user_screen_name.lower() == "videosubtitle":
        print("Can't transcribe video for self.")
        return
    
    if video_tweet.is_in_mongo():
        print("Tweet already has been captioned. Replying with captioned version.")
        responses = video_tweet.get_response_tweet_ids()
        reply_to_tweet(video_tweet, mention_tweet, text="@" + mention_tweet.user_screen_name + f" https://twitter.com/videosubtitle/status/{responses[0]}")
        return

    print("Tweet has not yet been captioned.")

    try:
        download_video(video_tweet.id)
    except Exception as e:
        print(e)
        reply_to_tweet(video_tweet, mention_tweet, text="@" + mention_tweet.user_screen_name + " Sorry, we couldn't find a video.")
        return
    
    # For now, don't process a tweet longer than 3 minutes
    if misc.VIDEO_LENGTH.total_seconds() > 140:
        reply_to_tweet(video_tweet, mention_tweet, text="@" + mention_tweet.user_screen_name + " Sorry, this video is too long to transcribe.")
        return

    write_video_to_audio_file()
    upload_blob()
    stt_response = get_gcs_transcription()

    text = generate_subtitles(stt_response)["text"]
    if os.stat("data/subtitles.srt").st_size == 0:
        reply_to_tweet(video_tweet, mention_tweet, False, "@" + mention_tweet.user_screen_name + " Sorry, we weren't able to parse any words from this video.")
        return
    print("Total video length is", misc.VIDEO_LENGTH.total_seconds())
    
    generate_captioned_video()
    reply_to_tweet(video_tweet, mention_tweet, True)
