from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi
import json
from pathlib import Path

def download_video(youtube_id, output_dir):

    output_fpath = Path(output_dir) / "video.mp4"
    # dont dl if it already exists
    if output_fpath.exists():
        return output_fpath

    youtube_url = f"https://www.youtube.com/watch?v={youtube_id}"
    yt = YouTube(youtube_url)
    stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    _ = stream.download(output_path=output_dir, filename="video.mp4")
    return output_fpath


def save_transcript(video_id, output_dir):
    output_fpath = (Path(output_dir) / "raw_transcript.json")

    # dont dl if it already exists
    if output_fpath.exists():
        return output_fpath

    transcript = YouTubeTranscriptApi.get_transcript(video_id)

    # we dont need the duration so we dont save it.
    for item in transcript:
        item.pop("duration")

    output_fpath.write_text(json.dumps(transcript)) 
    return output_fpath