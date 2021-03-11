import ffmpeg
from librosa import load, resample
from moviepy import editor
import os
from config import misc
from soundfile import write as sf_write


# given:
# video_path - the path of the video to caption
# audio_path - the path of the audio to place onto the final video
# output_path - the path of the final video to return

# returns:
# the output_path if the video was annotated, else an exception is raised
def generate_captioned_video(transcription_path="data/subtitles.srt", video_path=misc.LATEST_VIDEO_NAME, audio_path=misc.LATEST_AUDIO_NAME, output_path="data/final_video.mp4"):
    # TO-DO: check output of this line like in function below
    os.system(f"ffmpeg -y -i {video_path} -vf subtitles={transcription_path} data/annotated_video.mp4")
    
    out = os.system("ffmpeg -y -i {} -i {} -c:v copy -map 0:v:0 -map 1:a:0 {}".format("data/annotated_video.mp4", audio_path, output_path))
    if out == 0:
        return output_path
    else:
        raise Exception("Error encoding the video.")


# writes video's audio to LATEST_AUDIO_NAME
def write_video_to_audio_file():
    video_path = misc.LATEST_VIDEO_NAME
    stream = ffmpeg.input(video_path)
    audio = stream.audio
    stream = ffmpeg.output(audio, misc.LATEST_AUDIO_NAME, ac=1, sample_rate=44100).overwrite_output()
    ffmpeg.run(stream)

    y, s = load(misc.LATEST_AUDIO_NAME)
    y = resample(y, s, misc.TARGET_SAMPLE_RATE)
    sf_write(misc.LATEST_AUDIO_NAME, y, misc.TARGET_SAMPLE_RATE, format='flac')

def clean_data():
    video_path = misc.LATEST_VIDEO_NAME
    os.remove(video_path)

if __name__ == "__main__":
    print("Testing video_handler")
    generate_captioned_video(
        transcription_path = "data/test/test_subtitle.srt",
        video_path = "data/test/test_video.mp4",
        audio_path = "data/test/test_audio.flac",
        output_path = "data/test/test_output_video.mp4"
    )
