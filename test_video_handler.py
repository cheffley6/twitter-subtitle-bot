from transcription import Transcription
from video_handler import *
from datetime import timedelta

transcriptions = [
    Transcription(
        "This is the first test caption.",
        timedelta(seconds=0),
        timedelta(seconds=2)
    ),
    Transcription(
        "This is the second test caption.",
        timedelta(seconds=2),
        timedelta(seconds=4)
    )
]

video_path = "test_video.mp4"
audio_path = "test_audio.flac"

generate_captioned_video(transcriptions, video_path=video_path, audio_path=audio_path)

