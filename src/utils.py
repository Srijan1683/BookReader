import re
from pathlib import Path

import fitz
from src.models import TOC, ChapterTOC, Page
from contextlib import contextmanager
import sqlite3


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

def _is_text_document(path) -> bool:
    return Path(path).suffix.lower() == ".txt"


def get_pages(document_path, page_numbers: list[int] = None) -> list[Page]:
    """Stage 1: ingest PDF or TXT content into a common, one-indexed page model."""
    if _is_text_document(document_path):
        text = Path(document_path).read_text(encoding="utf-8", errors="replace")
        # Form-feed is a useful, lossless page separator for plain-text exports.
        all_pages = text.split("\f") or [""]
        selected_numbers = page_numbers or range(1, len(all_pages) + 1)
        return [Page(number=n, content=all_pages[n - 1]) for n in selected_numbers if n <= len(all_pages)]

    doc = fitz.open(document_path)
    try:
        selected_numbers = page_numbers or range(1, doc.page_count + 1)
        return [Page(number=n, content=doc.load_page(n - 1).get_text("text")) for n in selected_numbers]
    finally:
        doc.close()

def _infer_toc(pages: list[Page]) -> list[TOC]:
    """Create a usable two-level outline when a file has no embedded PDF TOC."""
    entries = []
    numbered = re.compile(r"^(?P<number>\d+(?:\.\d+)*)[.)\s-]+(?P<title>.+)$")
    for page in pages:
        for raw_line in page.content.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith("#"):
                hashes, title = line.split(maxsplit=1) if " " in line else (line, "Untitled section")
                entries.append(TOC(level=1 if len(hashes) == 1 else 2, title=title.strip(), page_number=page.number))
                continue
            if re.match(r"^(chapter|unit|part)\b", line, re.IGNORECASE):
                entries.append(TOC(level=1, title=line, page_number=page.number))
                continue
            match = numbered.match(line)
            if match:
                level = 1 if "." not in match.group("number") else 2
                entries.append(TOC(level=level, title=line, page_number=page.number))

    if not any(entry.level == 1 for entry in entries):
        entries.insert(0, TOC(level=1, title="Document", page_number=1))
    if not any(entry.level > 1 for entry in entries):
        entries.append(TOC(level=2, title="Overview", page_number=1))
    return entries


def get_toc(document_path: str) -> list[TOC]:
    """Stage 2: extract an embedded TOC, or infer one for TXT/unstyled PDFs."""
    pages = get_pages(document_path)
    if _is_text_document(document_path):
        return _infer_toc(pages)

    doc = fitz.open(document_path)
    try:
        toc = doc.get_toc()
    finally:
        doc.close()
    return [TOC(level=l, title=t, page_number=n) for l, t, n in toc] or _infer_toc(pages)


def get_chapter_segmented_toc(toc: list[TOC], document_page_count: int | None = None):
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
            end_page = document_page_count or toc[-1].page_number
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
