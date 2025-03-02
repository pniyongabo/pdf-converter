from pathlib import Path
import fitz  # PyMuPDF
import re
from PIL import Image  # We'll use PIL for image verification
import io

def convert_pdf_to_markdown(pdf_path: str, output_dir: str) -> str:
    """
    Convert PDF to Markdown while preserving images and layout.
    """
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    pdf_name = Path(pdf_path).stem
    images_dir = output_path / f"{pdf_name}_images"
    images_dir.mkdir(parents=True, exist_ok=True)

    # Open PDF
    pdf_document = fitz.open(pdf_path)
    markdown_content = []

    try:
        # Process each page
        for page_num, page in enumerate(pdf_document):
            # Extract text
            text = page.get_text("text")
            blocks = page.get_text("blocks")

            # Sort blocks by vertical position then horizontal
            blocks.sort(key=lambda b: (b[1], b[0]))

            # Process text blocks
            for block in blocks:
                text = block[4]
                if text.strip():
                    # Detect and format headers
                    if len(text) < 100 and text.isupper():
                        markdown_content.append(f"# {text}\n")
                    elif len(text) < 80 and text.istitle():
                        markdown_content.append(f"## {text}\n")
                    else:
                        markdown_content.append(f"{text}\n")

            # Extract images
            image_list = page.get_images()
            for img_index, img in enumerate(image_list):
                try:
                    xref = img[0]
                    base_image = pdf_document.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]

                    # Verify image data using PIL
                    try:
                        img_obj = Image.open(io.BytesIO(image_bytes))
                        # If image is valid, save it
                        image_filename = f"image_p{page_num+1}_{img_index+1}.{image_ext}"
                        img_path = images_dir / image_filename

                        with open(img_path, 'wb') as img_file:
                            img_file.write(image_bytes)

                        # Add image reference to markdown
                        rel_path = img_path.relative_to(output_path)
                        markdown_content.append(f"\n![Image]({rel_path})\n")

                    except Exception as img_err:
                        print(f"Skipping invalid image: {img_err}")

                except Exception as e:
                    print(f"Error extracting image {img_index} from page {page_num+1}: {e}")

            # Add page break
            markdown_content.append("\n---\n")

    finally:
        pdf_document.close()

    # Clean up the content
    content = clean_markdown_content('\n'.join(markdown_content))

    # Write markdown file
    markdown_path = output_path / f"{pdf_name}.md"
    markdown_path.write_text(content, encoding='utf-8')

    return str(markdown_path)

def clean_markdown_content(content: str) -> str:
    """
    Clean up the markdown content.
    """
    # Remove multiple blank lines
    content = re.sub(r'\n\s*\n', '\n\n', content)

    # Fix headers (ensure space after #)
    content = re.sub(r'#(\w)', r'# \1', content)

    # Fix lists
    content = re.sub(r'(?m)^[-•]\s*', '* ', content)

    # Fix numbered lists
    content = re.sub(r'(?m)^\d+\.\s*', lambda m: m.group().rstrip() + ' ', content)

    # Remove multiple dashes (page breaks)
    content = re.sub(r'\n-{3,}\n\n-{3,}\n', '\n---\n', content)

    # Fix image references
    content = re.sub(r'!\[(.*?)\]\s*\((.*?)\)', r'![\1](\2)', content)

    # Remove any remaining special characters
    content = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', content)

    return content.strip()

if __name__ == "__main__":
    try:
        pdf_path = "./testing_files/inputs/pdf-with-images.pdf"
        output_dir = "./testing_files/output"

        print("Starting PDF conversion...")
        print(f"Input PDF: {pdf_path}")
        print(f"Output directory: {output_dir}")

        markdown_file = convert_pdf_to_markdown(pdf_path, output_dir)
        print(f"\nSuccessfully converted PDF to Markdown: {markdown_file}")

        # Print the first few lines of the markdown file
        with open(markdown_file, 'r', encoding='utf-8') as f:
            print("\nFirst few lines of the markdown file:")
            print("=====================================")
            print('\n'.join(f.readlines()[:10]))

    except Exception as e:
        print(f"\nError: {str(e)}")
        print("\nPlease ensure all required packages are installed:")
        print("pip install pymupdf Pillow")