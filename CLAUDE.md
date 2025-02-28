# PDF Converter Tool Guide

## Commands
- Activate local dev Conda environment: `conda activate ./env/dev`
- Run PDF to DOCX converter: `python pdf-to-docx.py INPUT_PATH`
- Run PDF to Markdown converter: `python pdf-to-md.py INPUT_PATH`
- Install dependencies: `pip install click pdf2docx pdfminer.six pymupdf`

## Code Style Guidelines
- Imports: Group standard library, then third-party, then local imports with a blank line between groups
- Use Click for command-line argument handling
- File I/O: Use context managers (with open...) for file operations
- Error handling: Check if files exist before operations, use try/except for potential runtime errors
- Function naming: Use snake_case for functions and variables
- Comments: Document code with docstrings using triple quotes
- Line length: Maximum 88 characters per line
- String formatting: Prefer f-strings for string formatting
- Use descriptive variable names and avoid single-letter names except for simple counters
- For Styling, use Flake8 rules. For example, blank line should not contain whitespace (Flake8 W293)