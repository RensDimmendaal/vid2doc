"""
TODO's:
1. Download the transcript
2. Parse the transcript
3. Download the video
4. Extract frames
5. Process frames
6. Organize frames per paragraph
7. Generate markdown document
"""
from pathlib import Path
import typer
from vid2doc.youtube import download_video, save_transcript
from vid2doc.transcriber import convert_transcript_file
from vid2doc.frame_extractor import extract_frames, remove_duplicates
from vid2doc.doc_creator import generate_markdown, generate_html

from dotenv import load_dotenv
load_dotenv()
app = typer.Typer()

@app.callback()
def callback():
    """
    Awesome Portal Gun
    """


@app.command()
# TODO: defaults are for testing for now...
def convert(youtube_id:str="2AYLBuwtfJo", output_dir:Path = "./data/"):
    """
    youtube_id: str: YouTube video ID
    output_dir: str: Output directory to save the results, we'll make a subdir with the youtube_id
    """
    output_dir = Path(output_dir) / youtube_id
    output_dir.mkdir(exist_ok=True, parents=True)

    video_fpath = download_video(youtube_id, output_dir)
    typer.echo(f"Downloaded video to {video_fpath}")
    raw_transcript_fpath = save_transcript(youtube_id, output_dir)
    typer.echo(f"Downloaded transcript to {raw_transcript_fpath}")

    processed_transcript_fpath = convert_transcript_file(raw_transcript_fpath, output_dir)
    typer.echo(f"Processed transcript to {processed_transcript_fpath}")

    frames_dir = output_dir / "frames"

    if not frames_dir.exists():
        frames_dir.mkdir(exist_ok=True)
        extract_frames(video_fpath, frames_dir)
        remove_duplicates(frames_dir)
        typer.echo(f"Extracted frames to {frames_dir}")
    else:
        typer.echo(f"Frames already extracted to {frames_dir}")

    markdown_fpath = generate_markdown(output_dir)
    typer.echo(f"Saved markdown to {markdown_fpath}")

    html_file = output_dir / "output.html"
    html_fpath = generate_html(markdown_fpath, html_file)
    typer.echo(f"Saved HTML to {html_fpath}")

    

@app.command()
def load():
    """
    Load the portal gun
    """
    typer.echo("Loading portal gun")