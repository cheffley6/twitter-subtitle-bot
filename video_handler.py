import ffmpeg
from moviepy import editor
import os
from config import misc

def annotate(clip, txt, back_color='black', txt_color='white', fontsize=None, font='Helvetica-Bold'):
    if fontsize == None:
        fontsize = int(clip.size[0] / 20)
    """ Writes a text at the bottom of the clip. """
    txtclip = editor.TextClip(txt, fontsize=fontsize, size=(clip.size[0], clip.size[1]), font=font, color=txt_color, stroke_color="black", method="caption", align="south")

    cvc = editor.CompositeVideoClip([clip, txtclip.set_pos(('center', 'bottom'))])
    return cvc.set_duration(clip.duration)



# given:
# transcriptions - a list of Transcription objects
# video_path - the path of the video to caption
# audio_path - the path of the audio to place onto the final video
# output_path - the path of the final video to return

# returns:
# the output_path if the video was annotated, else an exception is raised
def generate_captioned_video(transcriptions, video_path=misc.LATEST_VIDEO_NAME, audio_path=misc.LATEST_AUDIO_NAME, output_path="final_video.mp4"):
    video = editor.VideoFileClip(video_path)
    annotated_clips = []
    for t in transcriptions:
        # print(t.get_start_time(), t.get_end_time(), VIDEO_LENGTH)
        annotated_clip = annotate(video.subclip(t.get_start_time().total_seconds(), t.get_end_time().total_seconds()), t.get_text())
        annotated_clips.append(annotated_clip)
    final_clip = editor.concatenate_videoclips(annotated_clips)
    final_clip.write_videofile("annotated_video.mp4")
    out = os.system("ffmpeg -y -i {} -i {} -c:v copy -map 0:v:0 -map 1:a:0 {}".format("annotated_video.mp4", audio_path, output_path))
    if out == 0:
        return output_path
    else:
        raise Exception("Error encoding the video.")


