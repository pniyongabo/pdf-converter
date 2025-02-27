#!/usr/bin/env python3
import click
import os
from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams


@click.command()
@click.argument("input_path", type=click.Path(exists=True))
def convert_pdf_to_md(input_path):
    """Convert PDF to Markdown maintaining the same filename."""
    directory = os.path.dirname(input_path)
    filename = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(directory, f"{filename}.md")

    if os.path.exists(output_path):
        os.remove(output_path)

    # Extract text with custom layout parameters
    laparams = LAParams(
        line_margin=0.5, word_margin=0.1, char_margin=2.0, boxes_flow=0.5
    )

    text = extract_text(input_path, laparams=laparams)

    # Remove the specific character (UTF-8 F0B7)
    text = text.replace("\uf0b7", "")

    # Basic markdown conversion
    lines = text.split("\n")
    markdown_lines = []
    for line in lines:
        # Remove leading line numbers and clean the line
        cleaned_line = line.strip()
        if cleaned_line and not cleaned_line[0].isdigit():
            # Convert headers
            if cleaned_line.lower().startswith(("purpose", "context", "note")):
                markdown_lines.append(f"## {cleaned_line}")
            else:
                markdown_lines.append(cleaned_line)

    # Write to markdown file
    with open(output_path, "w") as f:
        f.write("\n\n".join(markdown_lines))

    click.echo(f"Converted {input_path} to {output_path}")


if __name__ == "__main__":
    convert_pdf_to_md()
