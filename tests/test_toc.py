import sys
import os
from pathlib import Path
import pytest
from src import utils
from src.models import TOC, ChapterTOC 

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEST_PDF = PROJECT_ROOT / "sample_toc.pdf"
pdf_path = Path(os.getenv("BOOK_READER_TEST_PDF", DEFAULT_TEST_PDF))


@pytest.fixture
def toc_data():
    """Fixture to get the TOC data for the given PDF"""
    if not pdf_path.exists():
        pytest.skip(f"Test PDF not found: {pdf_path}")
    toc = utils.get_toc(pdf_path)
    chapter_segmented_toc = utils.get_chapter_segmented_toc(toc)
    return toc, chapter_segmented_toc


def test_toc_extraction(toc_data):
    toc, _ = toc_data
    assert toc, "TOC extraction failed, should not be empty."


def test_toc_entry_types(toc_data):
    toc, _ = toc_data
    for t in toc:
        assert isinstance(t, TOC), f"TOC type mismatch, expected TOC but got {type(t)}."


def test_chapter_segmentation(toc_data):
    _, chapter_segmented_toc = toc_data
    for chapter in chapter_segmented_toc:
        assert isinstance(chapter, ChapterTOC), f"Chapter type mismatch, expected ChapterTOC but got {type(chapter)}."
        assert isinstance(chapter.number, int), f"Chapter number type mismatch, expected int but got {type(chapter.number)}."
        assert isinstance(chapter.title, str), f"Chapter title type mismatch, expected str but got {type(chapter.title)}."
        assert isinstance(chapter.start_page, int), f"Start page type mismatch, expected int but got {type(chapter.start_page)}."
        assert isinstance(chapter.end_page, int), f"End page type mismatch, expected int but got {type(chapter.end_page)}."
        assert isinstance(chapter.chapter_toc_list, list), f"Chapter TOC list type mismatch, expected list but got {type(chapter.chapter_toc_list)}."
        assert chapter.start_page <= chapter.end_page, "Chapter start page should be less than or equal to end page."
        for heading in chapter.chapter_toc_list:
            assert isinstance(heading, TOC), f"Heading type mismatch, expected TOC but got {type(heading)}."


def test_valid_page_number_in_chapter(toc_data):
    """Test that chapter page ranges are valid"""
    _, chapter_segmented_toc = toc_data
    if not chapter_segmented_toc:
        pytest.skip("No chapter-segmented TOC entries were produced for the sample PDF.")

    test_chapter = chapter_segmented_toc[0]
    assert test_chapter.start_page >= 1, "Chapter start page should be a positive page number."
    assert test_chapter.end_page >= test_chapter.start_page, "Chapter end page should not be earlier than start page."


def test_empty_toc_handling():
    """Test if the functions handle an empty TOC gracefully"""
    empty_toc = []
    chapter_segmented_toc = utils.get_chapter_segmented_toc(empty_toc)
    assert chapter_segmented_toc == [], "Chapter segmentation should return an empty list for empty TOC input."


def test_invalid_pdf_handling():
    """Test if an invalid PDF raises the expected exception"""
    invalid_pdf_path = '/invalid/path/to/pdf.pdf'
    with pytest.raises(Exception):
        utils.get_toc(invalid_pdf_path)


if __name__ == '__main__':
    pytest.main()
