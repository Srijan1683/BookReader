import fitz
from src.models import TOC, ChapterTOC, Page
from contextlib import contextmanager
import sqlite3
import os


@contextmanager
def get_session(db_path: str):
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    except sqlite3.Error as e:
        if conn:
            conn.rollback()  # Rollback changes on error
        raise Exception(f"Database operation failed: {e}")
    finally:
        if conn:
            conn.close()

def get_pages(pdf_path, page_numbers: list[int] = None) -> list[Page]:
    doc = fitz.open(pdf_path)
    if not page_numbers:
        page_count = doc.page_count
        page_numbers = range(page_count)
        page_numbers = [n+1 for n in page_numbers]

    return [Page(number=n, content=doc.load_page(n - 1).get_text("text")) for n in page_numbers]

def get_toc(pdf_path: str) -> list[tuple]:
    doc = fitz.open(pdf_path)
    toc = doc.get_toc()
    return [TOC(level=l, title=t, page_number=n) for l, t, n in toc]


def get_chapter_segmented_toc(toc: list[TOC]):
    """
    Segment the TOC into chapters (level 1 headings and their sub-headings).
    Removes any list where only one level is available.
    """
    chapter_indexes = [i for i, entry in enumerate(toc) if entry.level == 1]
    if not chapter_indexes:
        return []

    chapter_entry_ranges = []
    chapter_page_ranges = []
    chapters_toc=[]
    
    for i in range(len(chapter_indexes)):
        start_idx = chapter_indexes[i]
        end_idx = chapter_indexes[i + 1] if i + 1 < len(chapter_indexes) else len(toc)
        chapter_entry_ranges.append((start_idx, end_idx))

        start_page = toc[start_idx].page_number
        if i + 1 < len(chapter_indexes):
            end_page = toc[chapter_indexes[i + 1]].page_number - 1
        else:
            end_page = toc[-1].page_number
        chapter_page_ranges.append((start_page, end_page))

    for i, index_range in enumerate(chapter_entry_ranges):
        start_idx, end_idx = index_range
        chapters_toc.append(ChapterTOC(
            number=i + 1,
            title=toc[chapter_indexes[i]].title,
            start_page=chapter_page_ranges[i][0],
            end_page=chapter_page_ranges[i][-1],
            chapter_toc_list=[
                toc[entry]
                for entry in range(start_idx + 1, end_idx)
                if toc[entry].level > toc[chapter_indexes[i]].level
            ]
        )
    )

    return chapters_toc
