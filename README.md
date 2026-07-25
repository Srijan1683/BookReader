# Book Reader

Book Reader is a completed Streamlit application that turns textbook-style PDF or TXT documents into interactive study decks. It extracts a document outline, segments content by chapter and heading, generates Markdown slides with OpenRouter, lets users browse the deck, asks contextual chatbot questions, and exports the result as a PowerPoint file.

## Features

- Upload PDF or TXT documents through a Streamlit web interface.
- Extract PDF table-of-contents data with PyMuPDF.
- Segment documents into chapter-level and heading-level study chunks.
- Generate 2 to 4 concise study slides per heading with OpenRouter.
- Use a local heuristic fallback when API access is unavailable.
- Browse slides one at a time with previous and next controls.
- Jump directly to a chapter or slide from dropdown navigation.
- Display slide numbers in one continuous deck order.
- Ask chatbot questions about the active slide section.
- Export the generated deck as a downloadable `.pptx` file.

## Tech Stack

- **Python** for the application logic.
- **Streamlit** for the web UI.
- **OpenRouter** for slide generation and chatbot responses.
- **PyMuPDF** for PDF parsing and table-of-contents extraction.
- **python-pptx** for PowerPoint export.
- **python-dotenv** for environment-backed configuration.
- **pytest** for project tests.

## Application Flow

1. `webapp.py` accepts the uploaded document and starts the generation flow.
2. `src/utils.py` extracts pages and table-of-contents entries.
3. `src/segmentor.py` groups the document into chapter and heading chunks.
4. `src/slide_generator.py` generates Markdown slide content.
5. `src/deck.py` normalizes slide titles and assigns global slide numbers.
6. `webapp.py` renders the slide browser, chatbot, chapter/slide jump controls, and PowerPoint export.

## Project Structure

```text
Book-Reader-m/
├── webapp.py                         # Streamlit app and UI
├── main.py                           # Document-to-slides pipeline
├── requirements.txt                  # Python dependencies
├── README.md                         # Project documentation
├── scripts/
│   └── generate_test_pdf.py          # Test PDF generator
├── src/
│   ├── deck.py                       # Slide normalization and deck flattening
│   ├── models.py                     # Shared data models
│   ├── openrouter_client.py          # OpenRouter chat-completion client
│   ├── segmentor.py                  # Chapter and heading segmentation
│   ├── slide_generator.py            # Slide generation plus local fallback
│   ├── utils.py                      # PDF loading and TOC helpers
│   ├── llm.py                        # Prompt helper
│   ├── prompts.yaml                  # Prompt templates
│   └── vector_db.py                  # Vector search helper
├── rag/
│   ├── chat_engine.py                # Retrieval-backed chat helper
│   ├── embed.py                      # Embedding helper
│   └── retriever.py                  # Chroma retrieval helper
├── test_assets/
│   └── book_reader_test.pdf          # Stable test input
└── tests/
    ├── test_deck.py                  # Deck numbering tests
    ├── test_toc.py                   # TOC extraction tests
    └── test_chapter_processor.py     # Chapter-processing debug helpers
```

## Main Commands

Run the app:

```bash
python -m streamlit run webapp.py
```

Run tests:

```bash
pytest -q
```

Run a syntax check:

```bash
python -m py_compile webapp.py main.py src/openrouter_client.py src/slide_generator.py src/segmentor.py src/deck.py
```
