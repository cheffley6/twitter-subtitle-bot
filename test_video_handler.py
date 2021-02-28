from video_handler import *
from datetime import timedelta

video_path = "test_video.mp4"
audio_path = "test_audio.flac"
transcription_path = "test_subtitle.srt"

generate_captioned_video(transcription_path=transcription_path, video_path=video_path, audio_path=audio_path)

