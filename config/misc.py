# constants that should pretty much never change
LATEST_VIDEO_NAME = "data/twitter_video.mp4"
LATEST_AUDIO_NAME = "data/twitter_audio.flac"

TARGET_SAMPLE_RATE = 44100

BUCKET_NAME = "ulti-tweet-audio-bucket"
DESTINATION_BLOB_NAME = "current_audio.flac"
GOOGLE_APPLICATION_CREDENTIALS="gcp_credentials.json"


# static variables that are subject to be updated during execution
VIDEO_LENGTH = 0.0