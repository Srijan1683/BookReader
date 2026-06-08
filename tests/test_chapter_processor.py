import sys
import argparse
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.utils import *
from src.models import TOC, ChapterTOC, Page, Headings

import unicodedata
from difflib import SequenceMatcher


def normalize_unicode(text):
    return unicodedata.normalize('NFKD', text)

def normalize_whitespace(text):
    text = text.replace('\u00A0', ' ').replace('\u200B', '')
    return " ".join(text.split())

def normalize_punctuation(text):
    text = text.replace("“", '"').replace("”", '"')
    text = text.replace("‘", "'").replace("’", "'")
    text = text.replace("–", "-").replace("—", "-")
    return text

def preprocess_text(text):
    text = normalize_unicode(text)
    text = normalize_whitespace(text)
    text = normalize_punctuation(text)
    return text.lower()

def find_most_similar_heading_index(page_lines, heading):
    normalized_heading = preprocess_text(heading)
    processed_lines = [preprocess_text(line) for line in page_lines]

    best_idx = 0
    best_score = -1.0
    for idx, line in enumerate(processed_lines):
        if not line:
            continue
        score = SequenceMatcher(None, normalized_heading, line).ratio()
        if normalized_heading and normalized_heading in line:
            score = max(score, 0.98)
        if score > best_score:
            best_idx = idx
            best_score = score

    return best_idx, best_score
    

def segment_page_by_headings(page_text, headings):
    # Split page text into lines
    page_lines = page_text.split('\n')
    
    # Store the results in a dictionary
    segments = {}
    
    # Find the most similar line index for each heading
    heading_indices = []
    for heading in headings:
        idx, _ = find_most_similar_heading_index(page_lines, heading)
        heading_indices.append(idx)
    
    # Sort indices to ensure they are in order
    heading_indices.sort()
    
    # Handle text before the first heading (if any)
    if heading_indices and heading_indices[0] > 1:
        first_heading = headings[0]
        segments["pre_text"] = '\n'.join(page_lines[:heading_indices[0]]).strip()

    # Segment the text by the heading indices
    for i, heading in enumerate(headings):
        start_idx = heading_indices[i]
        
        if i + 1 < len(heading_indices):
            end_idx = heading_indices[i + 1]
        else:
            end_idx = len(page_lines)  # Last segment goes to the end of the text
        
        # Extract text between the current heading and the next
        text_segment = '\n'.join(page_lines[start_idx:end_idx]).strip()
        
        # Handle edge case when the heading is at the start or no text is available
        if text_segment:
            segments[heading] = text_segment
        else:
            segments[heading] = None

    return segments



def process_chapter(pages: list[Page], chapter: ChapterTOC):
    
    start_page = chapter.start_page
    end_page = chapter.end_page
    chapter_page_numbers = range(start_page, end_page+1, 1)

    chapter_toc_dict = {}
    chapter_toc_dict = defaultdict(list)
    for chapter_toc in chapter.chapter_toc_list:
        chapter_toc_dict[chapter_toc.page_number].append(chapter_toc.heading)

    chapter_text_dict = {}
    for page in pages:
        page_number = page.number
        page_text = page.content
        if page_number in chapter_page_numbers:
            chapter_text_dict[page_number] = page_text

    res = []
    prev_segment_text = None  # Keep track of text that doesn't belong to a heading

    for page_num in chapter_page_numbers:
        page_text = chapter_text_dict[page_num]
        if page_num in chapter_toc_dict:
            headings = chapter_toc_dict[page_num]
            segments = segment_page_by_headings(page_text, headings)

            # Handle pre-text that appears before the first heading
            if segments and 'pre_text' in segments:
                if res:  # If there's already some content, append to the previous segment
                    prev_segment_text = segments.pop('pre_text')
                else:
                    # Log the discarded pre-text on the first page
                    print(f"Page {page_num} has pre-text, but this is the first page. Discarding pre-text.")
                    _ = segments.pop('pre_text')

            # Add each heading and its corresponding text as a new entry
            for heading_name, heading_text in segments.items():
                res.append(Headings(
                    title=heading_name,
                    text=heading_text,
                    page_number=page_num
                ))

        else:
            if not res:
                # Handle case where the first page has no headings
                print(f"Page {page_num} has no headings and is the first page. Skipping this page!")
            else:
                # If it's not the first page, treat the entire page as additional content
                prev_segment_text = page_text

        # Append any leftover text from the previous page or pre-heading text to the last heading's content
        if res and prev_segment_text:
            res[-1].text += prev_segment_text
            prev_segment_text = None  # Clear after appending

    return res


def debug_pages(pdf_path):
    pages = get_pages(pdf_path)
    
    for page in pages:
        print("\n")
        print(f"Page Number: {page.number}")
        print(f"Page Content:\n{page.content}")

def debug_chapter_segmented_toc(pdf_path):
    toc = get_toc(pdf_path)
    
    for chapter_toc in get_chapter_segmented_toc(toc):
        print(f"\nChapter TOC:")
        print(chapter_toc)
        for toc_list in chapter_toc.chapter_toc_list:
            print(f"SUB TOC LIST:\t{toc_list}")


from collections import defaultdict

def debug_chapter_toc_dict(pdf_path):
    toc = get_toc(pdf_path)
    
    with open('chapter_toc.out', 'w') as f:
        # Write TOC information
        f.write(f"Input TOC: {toc}\n")
        
        # Write chapter information
        chapter = next(get_chapter_segmented_toc(toc))
        f.write(f"Input Chapter: {chapter}\n")
        
        # Write page numbers and retrieve pages
        start_page = chapter.start_page
        end_page = chapter.end_page
        chapter_page_numbers = range(start_page, end_page + 1, 1)
        chapter_pages = get_pages(pdf_path, page_numbers=chapter_page_numbers)
        f.write(f"Start Page: {start_page}\n")
        f.write(f"End Page: {end_page}\n")
        f.write(f"Chapter Page Numbers: {list(chapter_page_numbers)}\n")

        # Create and write chapter TOC dictionary
        chapter_toc_dict = defaultdict(list)
        for chapter_toc in chapter.chapter_toc_list:
            chapter_toc_dict[chapter_toc.page_number].append(chapter_toc.title)
        
        for page_number, headings in chapter_toc_dict.items():
            f.write("\n\n")
            f.write(f"Chapter TOC Dict | Page Number: {page_number}\n")
            f.write(f"Chapter TOC Dict | Headings: {headings}\n")

        # Create and write chapter text dictionary
        chapter_text_dict = {page.number: page.content for page in chapter_pages}

        for page_number, page_text in chapter_text_dict.items():
            f.write("\n\n")
            f.write(f"Chapter Text Dict | Page Number: {page_number}\n")
            f.write(f"Chapter Text Dict | Text: {page_text}\n")

    return chapter_page_numbers, chapter_toc_dict, chapter_text_dict


def debug_heading_segments(pdf_path):
    chapter_page_numbers, chapter_toc_dict, chapter_text_dict = debug_chapter_toc_dict(pdf_path)
    res = []
    prev_segment_text = None  # Keep track of text that doesn't belong to a heading

    for page_num in chapter_page_numbers:
        page_text = chapter_text_dict[page_num]
        if page_num in chapter_toc_dict:
            headings = chapter_toc_dict[page_num]
            segments = segment_page_by_headings(page_text, headings)

            # Handle pre-text that appears before the first heading
            if segments and 'pre_text' in segments:
                if res:  # If there's already some content, append to the previous segment
                    prev_segment_text = segments.pop('pre_text')
                else:
                    # Log the discarded pre-text on the first page
                    print(f"Page {page_num} has pre-text, but this is the first page. Discarding pre-text.")
                    _ = segments.pop('pre_text')

            # Add each heading and its corresponding text as a new entry
            for heading_name, heading_text in segments.items():
                res.append(Headings(
                    title=heading_name,
                    text=heading_text,
                    page_number=page_num
                ))

        else:
            if not res:
                # Handle case where the first page has no headings
                print(f"Page {page_num} has no headings and is the first page. Skipping this page!")
            else:
                # If it's not the first page, treat the entire page as additional content
                prev_segment_text = page_text

        # Append any leftover text from the previous page or pre-heading text to the last heading's content
        if res and prev_segment_text:
            res[-1].text += prev_segment_text
            prev_segment_text = None  # Clear after appending

    return res


def main():
    
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf_path", type=str, help="Path to the input file")
    
    args = parser.parse_args()

    res = debug_heading_segments(args.pdf_path)
    
    with open("res.out", 'w') as f:
        for heading in res:
            f.write(f"\n--------------------------------------")
            f.write(f"\nHeading Title: {heading.title}")
            f.write(f"\nHeading Page Number: {heading.page_number}")
            f.write(f"\nHeading Text\n: {heading.text}")
    
if __name__ == '__main__':
    main()
