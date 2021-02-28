import ffmpeg
from moviepy import editor
import os
from config import misc


# given:
# video_path - the path of the video to caption
# audio_path - the path of the audio to place onto the final video
# output_path - the path of the final video to return

# returns:
# the output_path if the video was annotated, else an exception is raised
def generate_captioned_video(transcription_path="subtitles.srt", video_path=misc.LATEST_VIDEO_NAME, audio_path=misc.LATEST_AUDIO_NAME, output_path="final_video.mp4"):
    # TO-DO: check output of this line like in function below
    os.system(f"ffmpeg -i {video_path} -vf subtitles={transcription_path} annotated_video.mp4")
    
    out = os.system("ffmpeg -y -i {} -i {} -c:v copy -map 0:v:0 -map 1:a:0 {}".format("annotated_video.mp4", audio_path, output_path))
    if out == 0:
        return output_path
    else:
        raise Exception("Error encoding the video.")


if __name__ == "main":
    print("Testing video_handler")