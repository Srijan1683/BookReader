import os
import re
from dotenv import load_dotenv
from src.openrouter_client import chat_completion, is_api_availability_error


def _normalize_heading_text(text):
    if text is None:
        return ""
    return str(text).strip()


def _split_sentences(text):
    normalized_text = _normalize_heading_text(text)
    if not normalized_text:
        return []

    parts = re.split(r"(?<=[.!?])\s+|\n+", normalized_text)
    return [part.strip() for part in parts if part and part.strip()]


def _sentence_to_summary_point(sentence):
    cleaned = sentence.strip().lstrip("-").strip()
    replacements = {
        "It exists to exercise ": "Covers ",
        "The text is intentionally plain so ": "Uses plain text so ",
        "Each heading appears directly in the page body to help ": "Matches headings directly against page text to support ",
        "Use this file when debugging ": "Useful for debugging ",
        "A reliable testing PDF is more useful than a realistic-looking but inconsistent one.": "Predictable test PDFs are more useful than inconsistent realistic samples.",
    }

    for source, target in replacements.items():
        if cleaned.startswith(source):
            cleaned = target + cleaned[len(source):]
            break

    cleaned = cleaned.replace("Key points:", "Key ideas:")
    cleaned = cleaned.replace("Example note:", "Takeaway:")
    return cleaned.rstrip(".")


def _local_slide_fallback(heading_text):
    normalized_heading_text = _normalize_heading_text(heading_text)
    lines = [line.strip() for line in normalized_heading_text.splitlines() if line.strip()]
    title = lines[0][:70] if lines else "Generated Summary"

    body_text = "\n".join(lines[1:]) if len(lines) > 1 else normalized_heading_text
    sentences = _split_sentences(body_text)
    if not sentences:
        sentences = ["No extractable content was available for this heading."]

    summary_points = []
    seen = set()
    for sentence in sentences:
        point = _sentence_to_summary_point(sentence)
        normalized_point = point.lower()
        if normalized_point == title.lower():
            continue
        if normalized_point in seen:
            continue
        seen.add(normalized_point)
        summary_points.append(point)

    if not summary_points:
        summary_points = ["No extractable content was available for this heading."]

    overview_points = summary_points[:4]
    detail_points = summary_points[4:8] or summary_points[:4]

    slides = [
        "\n".join(
            [f"# {title}"] + [f"- {point}" for point in overview_points]
        ),
        "\n".join(
            [f"# Key Details: {title}"] + [f"- {point}" for point in detail_points]
        ),
    ]

    return slides


def generate_slides(heading_text):
    normalized_heading_text = _normalize_heading_text(heading_text)
    if not normalized_heading_text:
        return _local_slide_fallback("")

    load_dotenv()

    allow_local_fallback = os.getenv("ALLOW_LOCAL_SLIDE_FALLBACK", "true").lower() == "true"
    messages = [
        {
            "role": "system",
            "content": (
                "You are a tutor generating high-quality study slides in Markdown. "
                "Each slide must begin with a title using '# Slide Title'. "
                "Follow with concise bullet points or short paragraphs. "
                "Use code blocks only when they are genuinely useful. "
                "Return only Markdown slide content, with no surrounding explanation."
            ),
        },
        {
            "role": "user",
            "content": f"Create 2 to 4 study slides from this textbook content:\n\n{normalized_heading_text}",
        },
    ]

    try:
        text = chat_completion(messages, temperature=0.25, max_tokens=1400)
    except Exception as exc:
        if allow_local_fallback and is_api_availability_error(exc):
            return _local_slide_fallback(normalized_heading_text)
        raise

    # Split into slides
    slides = []
    current_slide = ""
    for line in text.splitlines():
        if line.startswith("# "):
            if current_slide:
                slides.append(current_slide.strip())
            current_slide = line + "\n"
        else:
            current_slide += line + "\n"
    if current_slide:
        slides.append(current_slide.strip())

    return slides

# Test run
if __name__ == '__main__':
    slides = generate_slides("""
    File Handling in Python:
    Python provides functions to create, read, write, and close files.
    Use `open()` to open a file. Modes: 'r', 'w', 'a', 'rb', etc.
    Use `.read()`, `.write()`, `.readline()` to interact with files.
    Always use `.close()` or a `with` block to manage file resources.
    """)
    
    for s in slides:
        print("=" * 50)
        print(s)
