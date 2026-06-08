import argparse
import json
import os
from pathlib import Path
import tempfile

from dotenv import load_dotenv
import importlib

import src.slide_generator
importlib.reload(src.slide_generator)

from src.segmentor import process_chapter
from src.utils import get_toc, get_chapter_segmented_toc
from src.slide_generator import generate_slides

load_dotenv()

def main(pdf_path):
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"PDF file not found at {pdf_path}")

    toc = get_toc(pdf_path)
    master_slide_dict = {}
    chapters_toc = get_chapter_segmented_toc(toc)
    for chapter_toc in chapters_toc:
        chapter_headings = process_chapter(pdf_path, chapter_toc)
        master_slide_dict[chapter_toc.title] = {}

        for heading in chapter_headings:
            heading_text = (heading.text or "").strip()
            heading_slides = generate_slides(heading_text)
            master_slide_dict[chapter_toc.title][heading.title] = heading_slides

    with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as tmp_file:
        json.dump(master_slide_dict, tmp_file, indent=4)
        tmp_file_path = tmp_file.name

    return 1, tmp_file_path

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate slide content from a PDF.")
    parser.add_argument(
        "pdf_path",
        nargs="?",
        default=str(Path("sample_toc.pdf")),
        help="Path to the input PDF.",
    )
    args = parser.parse_args()
    main(args.pdf_path)
