# Book Reader

Personal project for turning documents into slide-style study decks, browsing them in a Streamlit interface, and experimenting with question-answering on top of the generated content.

## Current Goal

Build a document-to-slides workflow that feels like a small product:

- upload a PDF or text file
- extract the table of contents
- segment chapters and subtopics
- generate slide summaries
- browse slides in a deck-like interface
- keep a chatbot panel beside the slides

## Current Status

What works now:

- Streamlit UI with a slide viewer and chatbot panel
- PDF TOC extraction with PyMuPDF
- chapter segmentation based on TOC entries
- local slide generation fallback when Gemini is unavailable
- PowerPoint export for generated slides
- stable local test PDF for debugging

What is limited right now:

- Gemini quota is unavailable in the current free setup
- chatbot calls may still return Gemini quota errors
- local slide generation is heuristic, not true LLM-quality summarization

## Main Files

- `webapp.py`: main Streamlit app
- `main.py`: core slide-generation pipeline entry point
- `src/utils.py`: PDF page loading and TOC segmentation
- `src/segmentor.py`: chapter and heading segmentation
- `src/slide_generator.py`: Gemini path plus local fallback summarizer
- `scripts/generate_test_pdf.py`: generates the debugging PDF
- `test_assets/book_reader_test.pdf`: stable test input for the pipeline

## Project Structure

```text
book_reader1/
├── webapp.py
├── main.py
├── requirements.txt
├── .env.example
├── README.md
├── scripts/
│   └── generate_test_pdf.py
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── llm.py
│   ├── llm_gemini.py
│   ├── models.py
│   ├── prompts.yaml
│   ├── segmentor.py
│   ├── slide_generator.py
│   ├── utils.py
│   └── vector_db.py
├── rag/
│   ├── __init__.py
│   ├── chat_engine.py
│   ├── embed.py
│   └── retriever.py
├── test_assets/
│   └── book_reader_test.pdf
└── tests/
    ├── __init__.py
    ├── test_chapter_processor.py
    └── test_toc.py
```

## Run

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
streamlit run webapp.py
```

## Useful Commands

Run the app:

```bash
streamlit run webapp.py
```

Generate the bundled test PDF again:

```bash
python scripts/generate_test_pdf.py
```

Run the TOC tests:

```bash
pytest tests/test_toc.py -q
```

Quick syntax check:

```bash
python -m py_compile webapp.py main.py src/utils.py src/slide_generator.py
```

## Environment Variables

Defined in `.env.example`:

- `OPENAI_API_KEY`
- `GEMINI_API_KEY`
- `GEMINI_MODEL`
- `ALLOW_LOCAL_SLIDE_FALLBACK`
- `BOOK_READER_TEST_PDF`

## Notes To Self

- The app should remain usable even when Gemini fails.
- UI polish matters here because the project is part demo, part workflow tool.
- Keep the local fallback path healthy so development is not blocked by quota.
- If Gemini becomes available later, the same app should improve without a major rewrite.

## Next Good Improvements

- improve local summarization quality so slides feel less extractive
- make slide navigation even smoother
- add a clearer chat context model instead of only using the current slide block
- decide whether old optional modules in `src/` and `rag/` should stay or be removed
