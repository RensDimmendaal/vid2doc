
# Vid2Doc

Vid2Doc is a tool that generates a document from a video lecture. 
It uses speech-to-text to transcribe the audio and image processing to extract slides from the video.

As an output you get:
1. A markdown file with the text and images in the right position.
2. A html file that shows the images in a gallery
3. All the images extracted from the video

# Usage

1. Clone the repo: `gh clone ...`
2. Install the project `poetry install`
3. Set your OPENAI_API_KEY in the environment `echo "export OPEN_API_KEY=..." >> .env`
4. Create a doc `vid2doc create --youtube-id=... --output=./data/`
5. Open the HTML to review the output
6. Make edits in the markdown file:
   1. Edit the text
   2. Remove images
7. `vid2doc update ...path` to update the HTML file

## Dev philosophy

We believe that a good UX/UI can compensate for a sloppy AI.
Extracting the right frames or making the correct transcription is hard.
And AI tools are not perfect. So we need to make the best out of it.

**UX: For the creator**
That's why we make a tool that's easy for the creator to correct the output: `markdown`.
You can edit the text and remove images yourself.

**UI: For the reader** 
We provide an example HTML file that shows the images in a gallery form.
This may be useful if you cannot pick that one perfect image that represents the slide or animation.
By showing all the images in a gallery the reader can get a good overview of the content, without being overwhelmed.