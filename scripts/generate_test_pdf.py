from pathlib import Path

import fitz


OUTPUT_PATH = Path(__file__).resolve().parents[1] / "test_assets" / "book_reader_test.pdf"

PAGE_WIDTH = 595
PAGE_HEIGHT = 842
MARGIN_X = 60
TITLE_Y = 72
BODY_START_Y = 130
LINE_HEIGHT = 18


CHAPTERS = [
    {
        "title": "Chapter 1: Foundations of Reading Systems",
        "sections": [
            "1.1 What a Book Pipeline Does",
            "1.2 Pages, Text, and Structure",
        ],
    },
    {
        "title": "Chapter 2: Extracting a Table of Contents",
        "sections": [
            "2.1 Identifying Heading Levels",
            "2.2 Mapping Headings to Pages",
        ],
    },
    {
        "title": "Chapter 3: Segmenting Chapters",
        "sections": [
            "3.1 Splitting Pages by Headings",
            "3.2 Carrying Context Across Pages",
        ],
    },
    {
        "title": "Chapter 4: Generating Study Slides",
        "sections": [
            "4.1 Summaries for Each Topic",
            "4.2 Turning Notes into Slides",
        ],
    },
    {
        "title": "Chapter 5: Asking Questions About Content",
        "sections": [
            "5.1 Retrieving Relevant Notes",
            "5.2 Producing Helpful Answers",
        ],
    },
]


def add_text_block(page, lines, start_y=BODY_START_Y, font_size=12):
    y = start_y
    for line in lines:
        page.insert_text((MARGIN_X, y), line, fontsize=font_size)
        y += LINE_HEIGHT


def chapter_body(chapter_index, section_title):
    base = [
        f"{section_title}",
        "",
        f"This section belongs to chapter {chapter_index} of the generated testing book.",
        "It exists to exercise TOC extraction, heading matching, and chapter segmentation.",
        "The text is intentionally plain so PDF text extraction stays stable across runs.",
        "Each heading appears directly in the page body to help similarity-based matching.",
        "Use this file when debugging page slicing, slide generation, and question answering.",
        "",
        "Key points:",
        "- headings should match the bookmark titles",
        "- chapter pages should be easy to inspect manually",
        "- extracted text should remain simple and predictable",
        "",
        "Example note:",
        "A reliable testing PDF is more useful than a realistic-looking but inconsistent one.",
    ]
    return base


def build_pdf():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    doc = fitz.open()
    toc_entries = []

    cover = doc.new_page(width=PAGE_WIDTH, height=PAGE_HEIGHT)
    cover.insert_text((MARGIN_X, TITLE_Y), "Book Reader Testing PDF", fontsize=24)
    add_text_block(
        cover,
        [
            "Purpose:",
            "This PDF is generated specifically for testing TOC extraction and chapter processing.",
            "",
            "Contents:",
            "- a visual table of contents page",
            "- bookmark-based PDF TOC entries",
            "- five top-level chapters so the current chapter segmentation code yields four usable chapters",
            "- repeated, predictable text for stable debugging",
        ],
        start_y=140,
        font_size=13,
    )

    toc_page = doc.new_page(width=PAGE_WIDTH, height=PAGE_HEIGHT)
    toc_page.insert_text((MARGIN_X, TITLE_Y), "Table of Contents", fontsize=22)

    visible_toc_lines = []
    current_page_number = 3
    for chapter in CHAPTERS:
        visible_toc_lines.append(f"{chapter['title']} .......... {current_page_number}")
        toc_entries.append([1, chapter["title"], current_page_number])
        for section in chapter["sections"]:
            visible_toc_lines.append(f"    {section} .......... {current_page_number}")
            toc_entries.append([2, section, current_page_number])
        current_page_number += 1

    add_text_block(toc_page, visible_toc_lines, start_y=120, font_size=12)

    page_number = 3
    for idx, chapter in enumerate(CHAPTERS, start=1):
        page = doc.new_page(width=PAGE_WIDTH, height=PAGE_HEIGHT)
        page.insert_text((MARGIN_X, TITLE_Y), chapter["title"], fontsize=20)
        page.insert_text((MARGIN_X, 105), f"Page {page_number}", fontsize=11)

        lines = []
        for section in chapter["sections"]:
            lines.extend(chapter_body(idx, section))
            lines.extend(["", ""])
        add_text_block(page, lines, start_y=135, font_size=12)
        page_number += 1

    doc.set_toc(toc_entries)
    doc.save(OUTPUT_PATH)
    doc.close()


if __name__ == "__main__":
    build_pdf()
    print(OUTPUT_PATH)
