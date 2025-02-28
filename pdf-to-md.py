#!/usr/bin/env python3
import click
import os
import fitz  # PyMuPDF
from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams
import shutil


def extract_images(pdf_path, output_dir):
    """Extract images from PDF and save them to the output directory."""
    # Create images directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Open the PDF
    pdf_document = fitz.open(pdf_path)
    image_list = []

    # Iterate through each page
    for page_num, page in enumerate(pdf_document):
        # Get images from this page
        image_dict = page.get_images(full=True)

        for img_index, img in enumerate(image_dict):
            xref = img[0]  # Get the XREF of the image
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]

            # Generate a unique filename
            image_filename = f"image_p{page_num+1}_{img_index+1}.{image_ext}"
            image_path = os.path.join(output_dir, image_filename)

            # Save the image
            with open(image_path, "wb") as img_file:
                img_file.write(image_bytes)

            # Get image position on the page
            rect = page.get_image_bbox(img)

            # Store image info including page number for later insertion
            image_list.append({
                "page": page_num,
                "filename": image_filename,
                "rect": rect,
                "y_pos": rect.y0  # Y-coordinate for positioning in the document
            })

    pdf_document.close()
    return image_list


@click.command()
@click.argument("input_path", type=click.Path(exists=True))
def convert_pdf_to_md(input_path):
    """Convert PDF to Markdown maintaining the same filename and including images."""
    input_dir = os.path.dirname(input_path)
    parent_dir = os.path.dirname(input_dir)
    filename = os.path.splitext(os.path.basename(input_path))[0]
    output_dir = os.path.join(parent_dir, "outputs")
    output_path = os.path.join(output_dir, f"{filename}.md")

    # Create images directory
    images_dir_name = f"{filename}_images"
    images_dir = os.path.join(output_dir, images_dir_name)

    # Clean up existing files
    if os.path.exists(output_path):
        os.remove(output_path)
    if os.path.exists(images_dir):
        shutil.rmtree(images_dir)

    # Extract images first
    click.echo("Extracting images...")
    image_list = extract_images(input_path, images_dir)

    # Extract text with custom layout parameters
    click.echo("Extracting text...")
    laparams = LAParams(
        line_margin=0.5, word_margin=0.1, char_margin=2.0, boxes_flow=0.5
    )

    text = extract_text(input_path, laparams=laparams)

    # Remove the specific character (UTF-8 F0B7)
    text = text.replace("\uf0b7", "")

    # Basic markdown conversion
    lines = text.split("\n")
    markdown_lines = []

    # Open PDF to get page heights for image positioning
    pdf = fitz.open(input_path)
    page_heights = [page.rect.height for page in pdf]
    pdf.close()

    # Process text and insert image references
    current_page = 0
    current_y_pos = 0
    page_images = {}

    # Group images by page
    for img in image_list:
        if img["page"] not in page_images:
            page_images[img["page"]] = []
        page_images[img["page"]].append(img)

    # Sort images by y-position on each page
    for page in page_images:
        page_images[page].sort(key=lambda x: x["y_pos"])

    # Process text line by line
    for line in lines:
        cleaned_line = line.strip()
        if cleaned_line:
            # Check if we need to insert images before this text
            if current_page in page_images:
                # Insert any images that should appear before this text
                while page_images[current_page] and page_images[current_page][0]["y_pos"] <= current_y_pos:
                    img = page_images[current_page].pop(0)
                    image_path = os.path.join(images_dir_name, img["filename"])
                    markdown_lines.append(f"![Image]({image_path})")
                    markdown_lines.append("")  # Add a blank line after the image

                # If all images on this page are processed, remove the page entry
                if not page_images[current_page]:
                    del page_images[current_page]

            # Process the text line
            if not cleaned_line[0].isdigit():
                # Convert headers
                if cleaned_line.lower().startswith(("purpose", "context", "note")):
                    markdown_lines.append(f"## {cleaned_line}")
                else:
                    markdown_lines.append(cleaned_line)

            # Update position (approximate)
            current_y_pos += 12  # Rough estimate for line height

            # Check if we've moved to the next page
            if current_y_pos > page_heights[current_page]:
                current_page += 1
                current_y_pos = 0

    # Add any remaining images
    for page in sorted(page_images.keys()):
        for img in page_images[page]:
            image_path = os.path.join(images_dir_name, img["filename"])
            markdown_lines.append(f"![Image]({image_path})")
            markdown_lines.append("")

    # Write to markdown file
    with open(output_path, "w") as f:
        f.write("\n\n".join(markdown_lines))

    # Report statistics
    click.echo(f"Converted {input_path} to {output_path}")
    click.echo(f"Extracted {len(image_list)} images to {images_dir}")


if __name__ == "__main__":
    convert_pdf_to_md()
