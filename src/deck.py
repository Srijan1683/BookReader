import re


SLIDE_TITLE_NUMBER_PATTERN = re.compile(
    r"^\s*(?:slide|sl\.?)\s*\d+\s*(?::|-|\.)?\s*",
    re.IGNORECASE,
)


def strip_slide_number(title):
    cleaned = str(title or "").strip()
    stripped = SLIDE_TITLE_NUMBER_PATTERN.sub("", cleaned).strip()
    return stripped or cleaned or "Untitled Slide"


def parse_slide_markdown(slide_markdown):
    lines = [line.strip() for line in str(slide_markdown or "").splitlines() if line.strip()]
    if lines and lines[0].startswith("# "):
        title = strip_slide_number(lines[0][2:])
        body_lines = lines[1:]
    else:
        title = "Untitled Slide"
        body_lines = lines

    return title, body_lines


def slides_to_plain_text(slide_markdown_list, *, include_titles=True):
    plain_lines = []
    for slide_markdown in slide_markdown_list or []:
        title, body_lines = parse_slide_markdown(slide_markdown)
        if include_titles:
            plain_lines.append(title)

        for line in body_lines:
            plain_lines.append(line)

        plain_lines.append("")

    return "\n".join(plain_lines).strip()


def flatten_slide_deck(slides_dict):
    deck_items = []
    if not slides_dict:
        return deck_items

    for chapter, sections in slides_dict.items():
        for section, slide_markdown_list in sections.items():
            for slide_markdown in slide_markdown_list or []:
                title, body_lines = parse_slide_markdown(slide_markdown)
                number = len(deck_items) + 1
                deck_items.append(
                    {
                        "number": number,
                        "chapter": chapter,
                        "section": section,
                        "title": title,
                        "body_lines": body_lines,
                        "markdown": slide_markdown,
                    }
                )

    return deck_items
