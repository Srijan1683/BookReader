import argparse
import json
import os
from pathlib import Path
import tempfile

from dotenv import load_dotenv

from src.segmentor import process_chapter
from src.utils import get_pages, get_toc, get_chapter_segmented_toc
from src.slide_generator import generate_slides

load_dotenv()

def main(document_path):
    """Run the four-stage document pipeline: ingest, TOC, segment, generate."""
    if not os.path.isfile(document_path):
        raise FileNotFoundError(f"Document file not found at {document_path}")

    pages = get_pages(document_path)  # Stage 1: PDF/TXT ingestion
    toc = get_toc(document_path)  # Stage 2: embedded or inferred TOC extraction
    master_slide_dict = {}
    chapters_toc = get_chapter_segmented_toc(toc, document_page_count=len(pages))
    for chapter_toc in chapters_toc:
        chapter_headings = process_chapter(document_path, chapter_toc)  # Stage 3: chapter/heading segmentation
        master_slide_dict[chapter_toc.title] = {}

        for heading in chapter_headings:
            heading_text = (heading.text or "").strip()
            heading_slides = generate_slides(heading_text, section_title=heading.title)  # Stage 4: Markdown slide generation
            master_slide_dict[chapter_toc.title][heading.title] = heading_slides

    with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as tmp_file:
        json.dump(master_slide_dict, tmp_file, indent=4)
        tmp_file_path = tmp_file.name

    return 1, tmp_file_path

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate slide content from a PDF or TXT document.")
    parser.add_argument(
        "pdf_path",
        nargs="?",
        default=str(Path("sample_toc.pdf")),
        help="Path to the input PDF or TXT document.",
    )
    args = parser.parse_args()
    main(args.pdf_path)
