from config import misc, twitter_credentials
from urllib.request import urlretrieve
from pprint import pprint
from twython import Twython
from google.cloud import storage, speech

from Transcription import Transcription
from moviepy import editor
import librosa
import soundfile as sf
import ffmpeg
import os
import datetime

twitter = Twython(
    twitter_credentials.TWITTER_CONSUMER_KEY, twitter_credentials.TWITTER_CONSUMER_SECRET,
    twitter_credentials.TWITTER_ACCESS_KEY, twitter_credentials.TWITTER_ACCESS_SECRET)

def annotate(clip, txt, back_color='black', txt_color='white', fontsize=None, font='Helvetica-Bold'):
    print("txt: ", txt)
    if fontsize == None:
        fontsize = int(clip.size[0] / 20)
    """ Writes a text at the bottom of the clip. """
    txtclip = editor.TextClip(txt, fontsize=fontsize, size=(clip.size[0], clip.size[1]), font=font, color=txt_color, stroke_color="black", method="caption", align="center")

    cvc = editor.CompositeVideoClip([clip, txtclip.set_pos(('center', 'bottom'))])
    return cvc.set_duration(clip.duration)



def generate_captioned_video(transcriptions, video_path=misc.LATEST_VIDEO_NAME):
    video = editor.VideoFileClip(video_path)
    annotated_clips = []
    for t in transcriptions:
        print(t.get_start_time(), t.get_end_time(), VIDEO_LENGTH)
        annotated_clip = annotate(video.subclip(t.get_start_time().total_seconds(), t.get_end_time().total_seconds()), t.get_text())
        annotated_clips.append(annotated_clip)
    final_clip = editor.concatenate_videoclips(annotated_clips)
    final_clip.write_videofile("annotated_video.mp4")
    os.system("ffmpeg -y -i {} -i {} -c:v copy -map 0:v:0 -map 1:a:0 final_video.mp4".format("annotated_video.mp4", "twitter_audio.flac"))

    
    
    

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
    VIDEO_LENGTH = datetime.timedelta(seconds=editor.VideoFileClip(misc.LATEST_VIDEO_NAME).duration)
    

    

# writes video's audio to LATEST_AUDIO_NAME
def write_video_to_audio_file():
    video_path = misc.LATEST_VIDEO_NAME
    stream = ffmpeg.input(video_path)
    audio = stream.audio
    stream = ffmpeg.output(audio, misc.LATEST_AUDIO_NAME, ac=1, sample_rate=44100).overwrite_output()
    ffmpeg.run(stream)

    y, s = librosa.load(misc.LATEST_AUDIO_NAME)
    y = librosa.resample(y, s, misc.TARGET_SAMPLE_RATE)
    sf.write(misc.LATEST_AUDIO_NAME, y, misc.TARGET_SAMPLE_RATE, format='flac')


def reply_to_tweet(text, tweet_id, author, use_video=False):
    if use_video:
        video = open('final_video.mp4', 'rb')
        response = twitter.upload_video(media=video, media_type='video/mp4')
        twitter.update_status(status="Transcribed video for {}.".format(author), media_ids=[response['media_id']], in_reply_to_status_id=tweet_id)
        # twitter.update_status()
        print("Reply sent.")
        return

    while len(text) > 0:
        # convert into multiple tweets
        response = twitter.update_status(status=text[:280], in_reply_to_status_id=tweet_id)
        tweet_id = response['id']
        text = text[280:]
    print("Reply sent.")

def upload_blob(bucket_name=misc.BUCKET_NAME, source_file_name=misc.LATEST_AUDIO_NAME, destination_blob_name=misc.DESTINATION_BLOB_NAME):
    '''Uploads a file to the bucket.'''


    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(
        "File {} uploaded to {}.".format(
            source_file_name, destination_blob_name
        )
    )


def transcribe_gcs(author=None, gcs_uri="gs://" + misc.BUCKET_NAME + "/" + misc.DESTINATION_BLOB_NAME):
    '''Asynchronously transcribes the audio file specified by the gcs_uri.'''

    client = speech.SpeechClient()

    audio = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
        sample_rate_hertz=44100,
        audio_channel_count=1,
        language_code="en-US",
        enable_word_time_offsets=True,
        model="video"
    )

    operation = client.long_running_recognize(config=config, audio=audio)

    print("Waiting for operation to complete...")
    response = operation.result(timeout=90)

    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    raw_transcription = "{} Video too long to re-create. Transcript: ".format(author)

    transcriptions = []

    first_time = True
    prev = datetime.timedelta(0)
    for index, result in enumerate(response.results):
        words = result.alternatives[0].words
        # The first alternative is the most likely one for this portion.
        print("Confidence: {}".format(result.alternatives[0].confidence))
        raw_transcription += result.alternatives[0].transcript
        
        
        if index == len(response.results) - 1:
            transcriptions.append(Transcription(result.alternatives[0].transcript, prev, VIDEO_LENGTH))
        else:
            if prev == None:
                if len(words) != 0:
                    prev = words[0].start_time
                    transcriptions.append(
                        Transcription(
                        result.alternatives[0].transcript,
                        prev,
                        words[-1].end_time))
                else:
                    raise Exception("Mess.")
            else:
                transcriptions.append(
                    Transcription(
                        result.alternatives[0].transcript,
                        prev,
                        words[-1].end_time))
        if len(words) > 0:
            prev = words[-1].end_time
        else:
            if index == len(response.results) - 1:
                continue
            else:
                prev = None

    print("Transcriptions:")
    for t in transcriptions:
        print(t)
    
    

    return (transcriptions, raw_transcription)

def process_one_video(tweet_id=None, mention_id=None, author=None):
    if author.lower() == "@videosubtitle":
        print("Can't transcribe video for self.")
        return
    try:
        download_video(tweet_id)
    except:
        reply_to_tweet("Sorry, we couldn't find a video.", mention_id, author)
        return
    write_video_to_audio_file()
    upload_blob()
    transcriptions, text = transcribe_gcs(author)
    if VIDEO_LENGTH.total_seconds() >= 30:
        reply_to_tweet(text, mention_id, author, False)
    else:
        generate_captioned_video(transcriptions)
        reply_to_tweet(text, mention_id, author, True)