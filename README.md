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
- OpenRouter-backed slide generation and chat
- chatbot available before and after slide generation
- local slide generation fallback when API access is unavailable
- PowerPoint export for generated slides
- stable local test PDF for debugging

What is limited right now:

- AI-generated slides and chat require a working OpenRouter key/model; the default `openrouter/free` router uses currently available free models
- local slide generation is heuristic, not true LLM-quality summarization

## Main Files

- `webapp.py`: main Streamlit app
- `main.py`: core slide-generation pipeline entry point
- `src/utils.py`: PDF page loading and TOC segmentation
- `src/segmentor.py`: chapter and heading segmentation
- `src/slide_generator.py`: OpenRouter path plus local fallback summarizer
- `src/openrouter_client.py`: shared direct OpenRouter HTTP client
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
python -m streamlit run webapp.py
```

## Useful Commands

Run the app:

```bash
python -m streamlit run webapp.py
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
python -m py_compile webapp.py main.py src/openrouter_client.py src/slide_generator.py
```

## Environment Variables

Defined in `.env.example`:

- `OPENROUTER_API_KEY`
- `OPENROUTER_MODEL`
- `OPENROUTER_BASE_URL`
- `OPENROUTER_HTTP_REFERER`
- `OPENROUTER_APP_TITLE`
- `ALLOW_LOCAL_SLIDE_FALLBACK`
- `BOOK_READER_TEST_PDF`

`OPENROUTER_MODEL` accepts any OpenRouter model ID, so switching from `openrouter/free` to a specific model is an `.env` change rather than a code change.

Example `.env`:

```bash
OPENROUTER_API_KEY=sk-or-your-openrouter-key
OPENROUTER_MODEL=openrouter/free
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_HTTP_REFERER=http://localhost:8501
OPENROUTER_APP_TITLE=Book Reader
ALLOW_LOCAL_SLIDE_FALLBACK=true
BOOK_READER_TEST_PDF=test_assets/book_reader_test.pdf
```

The app calls OpenRouter directly with Python's standard HTTP library. This avoids OpenAI SDK/httpx version conflicts such as `Client.__init__() got an unexpected keyword argument 'proxies'`.

## Notes To Self

- The app should remain usable even when API calls fail.
- UI polish matters here because the project is part demo, part workflow tool.
- Keep the local fallback path healthy so development is not blocked by quota.
- Use `OPENROUTER_MODEL` to swap models without code changes.

## Next Good Improvements

- improve local summarization quality so slides feel less extractive
- make slide navigation even smoother
- add a clearer chat context model instead of only using the current slide block
- decide whether old optional modules in `src/` and `rag/` should stay or be removed
