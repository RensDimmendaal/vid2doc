import json
from pathlib import Path
import os

import json
from pathlib import Path

def generate_markdown(json_dir):
    output_file = Path(json_dir) / 'output.qmd'

    if output_file.exists():
        return output_file

    json_path = Path(json_dir) / 'processed_transcript.json'
    frames_dir = Path(json_dir) / 'frames'
    
    # Load JSON data
    with json_path.open('r') as file:
        data = json.load(file)

    # Get list of image files
    image_files = sorted([f.relative_to(json_dir) for f in frames_dir.glob('*.jpg')])

    # Function to find relevant images for a given section start time
    def find_relevant_images(start_time):
        relevant_images = []
        for image_file in image_files:
            # Extract the timestamp from the filename
            timestamp = float(image_file.stem)
            if timestamp <= start_time:
                relevant_images.append(image_file)
            else:
                break
        return relevant_images

    # Generate Markdown content
    markdown_content = []
    markdown_content.append("---\nlightbox: true\n---\n")

    for s_idx, section in enumerate(data['sections']):
        section_title = section['section_title']
        markdown_content.append(f"## {section_title}\n")

        start_time = section['paragraphs'][0]['start_time']
        try:
            end_time = data['sections'][s_idx+1]['paragraphs'][0]['start_time']
        except IndexError:
            end_time = 99999999999999999

        relevant_images = [image for image in image_files if start_time < float(image.stem) <= end_time]

        for paragraph in section['paragraphs']:
            markdown_content.append(f"{paragraph['text']}\n")
            markdown_content.append("\n")
        
        if relevant_images:
            markdown_content.append('<ul class="carousel">\n')
            for image in relevant_images:
                alt_text = image.name
                markdown_content.append(f'  <li><img src="{image}" alt="{alt_text}" class="lightbox"></li>\n')
            markdown_content.append('</ul>\n')

    # TODO: Temporary fix to trigger lightbox, but creates ugly broken img
    markdown_content.append("![](tmp-fix-to-trigger-lightbox){.lightbox}")

    # Write to Markdown file
    output_file.write_text('\n'.join(markdown_content))
    return output_file

# Function to generate HTML content
def generate_html(markdown_file, output_file):
    content = Path(markdown_file).read_text().splitlines()
    
    sections_html = ""
    current_section = ""
    images_html = ""
    text_html = ""

    for line in content:
        line = line.strip()
        if line.startswith('#'):  # Section header
            if current_section:
                if images_html:  # Only add images section if there are images
                    sections_html += f"""
                    <h2>{current_section}</h2>
                    <div class="text">
                        {text_html}
                    </div>
                    <div class="list-wrapper">
                        <ul class="list">
                            {images_html}
                        </ul>
                        <button class="button button--previous" type="button">➜</button>
                        <button class="button button--next" type="button">➜</button>
                    </div>
                    """
                else:
                    sections_html += f"""
                    <h2>{current_section}</h2>
                    <div class="text">
                        {text_html}
                    </div>
                    """
                images_html = ""
                text_html = ""
            current_section = line.strip('#').strip()
        elif line.startswith('!['):  # Image in markdown syntax
            img_src = line.split('(')[-1].strip(')')
            images_html += f'<li class="item"><img src="{img_src}" alt="Image"></li>\n'
        else:  # Text
            text_html += f'<p>{line}</p>\n'

    # Add the last section
    if current_section:
        if images_html:  # Only add images section if there are images
            sections_html += f"""
            <h2>{current_section}</h2>
            <div class="text">
                {text_html}
            </div>
            <div class="list-wrapper">
                <ul class="list">
                    {images_html}
                </ul>
                <button class="button button--previous" type="button">➜</button>
                <button class="button button--next" type="button">➜</button>
            </div>
            """
        else:
            sections_html += f"""
            <h2>{current_section}</h2>
            <div class="text">
                {text_html}
            </div>
            """

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Markdown to HTML</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 20px;
        }}
        .list-wrapper {{
            position: relative;
            margin-bottom: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        .list {{
            display: flex;
            gap: 8px;
            padding: 16px;
            list-style: none;
            overflow-x: scroll;
            scroll-snap-type: x mandatory;
        }}
        .list::-webkit-scrollbar {{
            display: none;
        }}
        .item {{
            flex-shrink: 0;
            max-height: 220px;
            scroll-snap-align: center;
        }}
        .item img {{
            max-height: 220px;
            height: auto;
            width: auto;
            cursor: pointer;
        }}
        .button {{
            position: absolute;
            top: 50%;
            width: 3rem;
            height: 3rem;
            transform: translateY(-50%);
            background: rgba(0, 0, 0, 0.5);
            color: white;
            border: none;
            cursor: pointer;
            user-select: none;
        }}
        .button--previous {{
            left: 1.5rem;
            transform: translateY(-50%) rotate(180deg);
        }}
        .button--next {{
            right: 1.5rem;
        }}
        .text {{
            margin: 20px 40px 40px 40px;
        }}
        h2 {{
            text-align: left;
            margin-top: 40px;
            font-size: 1.5em;
            color: #333;
        }}
        /* Modal styles */
        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            overflow: auto;
            background-color: rgba(0, 0, 0, 0.8);
        }}
        .modal-content {{
            position: relative;
            margin: auto;
            padding: 20px;
            max-width: 80%;
            max-height: 80%;
        }}
        .modal-content img {{
            width: 100%;
            height: auto;
        }}
        .close {{
            position: absolute;
            top: 10px;
            right: 25px;
            color: #fff;
            font-size: 35px;
            font-weight: bold;
            cursor: pointer;
        }}
    </style>
</head>
<body>
    {sections_html}
    
    <!-- Modal structure -->
    <div id="myModal" class="modal">
        <span class="close">&times;</span>
        <div class="modal-content">
            <img id="modalImage" src="" alt="Modal Image">
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            const listWrappers = document.querySelectorAll('.list-wrapper');
            const modal = document.getElementById("myModal");
            const modalImg = document.getElementById("modalImage");
            const span = document.getElementsByClassName("close")[0];

            listWrappers.forEach((wrapper) => {{
                const list = wrapper.querySelector('.list');
                const items = list.querySelectorAll('.item');
                const buttonPrevious = wrapper.querySelector('.button--previous');
                const buttonNext = wrapper.querySelector('.button--next');
                const itemWidth = items[0].offsetWidth;
                const containerWidth = wrapper.offsetWidth;

                // Center the images if there are less than 5
                if (items.length <= 5) {{
                    list.style.justifyContent = 'center';
                }}

                items.forEach(item => {{
                    item.querySelector('img').addEventListener('click', function() {{
                        modal.style.display = "block";
                        modalImg.src = this.src;
                    }});
                }});

                buttonPrevious.addEventListener('click', function() {{
                    list.scrollBy({{ left: -itemWidth, behavior: 'smooth' }});
                }});

                buttonNext.addEventListener('click', function() {{
                    list.scrollBy({{ left: itemWidth, behavior: 'smooth' }});
                }});
            }});

            // When the user clicks on <span> (x), close the modal
            span.onclick = function() {{
                modal.style.display = "none";
            }}

            // When the user clicks anywhere outside of the modal, close it
            window.onclick = function(event) {{
                if (event.target == modal) {{
                    modal.style.display = "none";
                }}
            }}
        }});
    </script>
</body>
</html>"""

    with open(output_file, 'w') as file:
        file.write(html_content)
