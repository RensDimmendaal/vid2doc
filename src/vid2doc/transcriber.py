import json
from pathlib import Path
import instructor
from openai import OpenAI
from pydantic import BaseModel

class ParagraphTranscript(BaseModel):
    start_time: float
    text: str

class SectionTranscript(BaseModel):
    section_title: str
    paragraphs : list[ParagraphTranscript]

class VideoTranscript(BaseModel):
    sections : list[SectionTranscript]

def parse_transcript(raw_transcript: str) -> VideoTranscript:
    prompt = f"""
    I want you to convert the raw automatically generated transcript into a more coherent structure. 

    INSTRUCTIONS:
    - make small edits like adding capital letters, punctuation.
    - Remove filler words and uhms.
    - Rewrite a word if you're convinced it is a transcribing error
    - Create the section titles yourself, but limit them to 1-3 words.
    - Try to make each section about 2-5 paragraphs.
    - Sentence lengths may vary from short to long as needed.

    ```raw_transcript
    {raw_transcript}
    ```

    """.strip()

    # Patch the OpenAI client
    client = instructor.from_openai(OpenAI())

    # Extract structured data from natural language
    video_transcript = client.chat.completions.create(
        model="gpt-4o",
        response_model=VideoTranscript,
        messages=[{"role": "user", "content": prompt}],
    )

    return video_transcript

def convert_transcript_file(raw_transcript_fpath: Path, output_dir: Path):
    output_fpath = output_dir / "processed_transcript.json"

    if output_fpath.exists():
        return output_fpath

    raw_transcript = raw_transcript_fpath.read_text()

    video_transcript = parse_transcript(raw_transcript)

    vt_json = video_transcript.model_dump()

    output_fpath.write_text(json.dumps(vt_json))
    return output_fpath