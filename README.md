# twitter-subtitle-bot
Tentative plan for Feb 2021:
1. Move from moviepy to ffmpeg for everything
- Move to following design:
Download manager: handles downloading twitter videos
Data preparer: handles extracting audio from videos
GCP interface: uploads audio files + gets response from GCP STT
Subtitle generator: turns GCP STT responses into .srt files
Captioned Video Generator: generates new video with subtitles
Upload Manager: replies to tweets with new video (or link to new video) (or text)

