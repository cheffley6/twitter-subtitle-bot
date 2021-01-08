from config import misc, twitter_credentials
from urllib.request import urlretrieve
from pprint import pprint
from twython import Twython
from google.cloud import storage, speech

from Transcription import Transcription
from moviepy import editor
import librosa
import soundfile as sf
import os


twitter = Twython(
    twitter_credentials.TWITTER_CONSUMER_KEY, twitter_credentials.TWITTER_CONSUMER_SECRET,
    twitter_credentials.TWITTER_ACCESS_KEY, twitter_credentials.TWITTER_ACCESS_SECRET)

def annotate(clip, txt, back_color='black', txt_color='white', fontsize=None, font='Xolonium-Bold'):

    if fontsize == None:
        fontsize = 12 #int(clip.size[0] / 15)
    """ Writes a text at the bottom of the clip. """
    txtclip = editor.TextClip(txt, fontsize=12, size=(clip.size[0], None), font=font, bg_color=back_color, color=txt_color, method="caption", align="center")

    cvc = editor.CompositeVideoClip([clip, txtclip.set_pos(('center', 'bottom'))])
    return cvc.set_duration(clip.duration)



def generate_captioned_video(transcriptions, video_path=misc.LATEST_VIDEO_NAME):
    video = editor.VideoFileClip(video_path)
    annotated_clips = [annotate(video.subclip(t.get_start_time(), t.get_end_time()), t.get_text()) for t in transcriptions]
    final_clip = editor.concatenate_videoclips(annotated_clips)
    final_clip.write_videofile("annotated_video.mp4")
    

def handle_m3u8(video_url):

        command = "ffmpeg -i {} -bsf:a aac_adtstoasc -vcodec copy -c copy -crf 50 {} -y"
        print('executing: ')
        print(command.format(video_url, misc.LATEST_VIDEO_NAME))
        os.system(command.format(video_url, misc.LATEST_VIDEO_NAME))


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


def reply_to_tweet(text, tweet_id):
    while len(text) > 0:
        # convert into multiple tweets
        response = twitter.update_status(status=text[:280], in_reply_to_status_id=tweet_id)
        tweet_id = response['id']
        text = text[280:]

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


def transcribe_gcs(gcs_uri="gs://" + misc.BUCKET_NAME + "/" + misc.DESTINATION_BLOB_NAME):
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
    raw_transcription = "Transcript: "

    transcriptions = []

    for result in response.results:
        # The first alternative is the most likely one for this portion.
        print("result: ", result)
        print("Confidence: {}".format(result.alternatives[0].confidence))
        print("words?", result.alternatives[0].words)
        earliest, latest = 1000000000, -1
        for word in result.alternatives[0].words:
            earliest = min(earliest, word.start_time.seconds)
            latest = max(latest, word.end_time.seconds)
        raw_transcription += result.alternatives[0].transcript
        
        transcriptions.append(Transcription(result.alternatives[0].transcript, earliest, latest))
    
    generate_captioned_video(transcriptions)

    return raw_transcription

def process_one_video(tweet_id, mention_id):
    # try:
    #     download_video(tweet_id)
    # except:
    #     reply_to_tweet("Sorry, we couldn't find a video.", mention_id)
    #     return
    # write_video_to_audio_file()
    upload_blob()
    text = transcribe_gcs()
    # reply_to_tweet(text, mention_id)

process_one_video(1, 1)