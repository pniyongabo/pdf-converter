#!/usr/bin/env python3
import click
from pdf2docx import Converter
import os


@click.command()
@click.argument("input_path", type=click.Path(exists=True))
def convert_pdf_to_docx(input_path):
    """Convert PDF to DOCX maintaining the same filename and location."""
    directory = os.path.dirname(input_path)
    filename = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(directory, f"{filename}.docx")

    if os.path.exists(output_path):
        os.remove(output_path)

    # Create converter object and convert
    cv = Converter(input_path)
    cv.convert(output_path)
    cv.close()

    click.echo(f"Converted {input_path} to {output_path}")


if __name__ == "__main__":
    convert_pdf_to_docx()
