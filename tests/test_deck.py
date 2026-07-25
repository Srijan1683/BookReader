from src.deck import flatten_slide_deck, parse_slide_markdown, slides_to_plain_text


def test_parse_slide_markdown_removes_model_numbering():
    title, body_lines = parse_slide_markdown("# Slide 1: File Handling\n- Open files")

    assert title == "File Handling"
    assert body_lines == ["- Open files"]


def test_flatten_slide_deck_numbers_globally_across_sections():
    slides_dict = {
        "Chapter 1": {
            "Section A": ["# Slide 1: First\n- A", "# Slide 2: Second\n- B"],
            "Section B": ["# Slide 1: Third\n- C"],
        }
    }

    deck_items = flatten_slide_deck(slides_dict)

    assert [item["number"] for item in deck_items] == [1, 2, 3]
    assert [item["title"] for item in deck_items] == ["First", "Second", "Third"]
    assert [item["section"] for item in deck_items] == ["Section A", "Section A", "Section B"]


def test_slides_to_plain_text_can_skip_titles_for_ppt_body():
    text = slides_to_plain_text(["# Slide 1: First\n- A"], include_titles=False)

    assert text == "- A"
