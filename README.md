# Book Reader

Book Reader is a Streamlit app that turns textbook-style documents into interactive study decks. Upload a PDF or text file, generate chapter-aware slides with OpenRouter, browse the deck in the web UI, chat about the current section, and export the result as a PowerPoint presentation.

The project is built as a practical study tool: part document parser, part slide generator, part lightweight learning assistant.

## Features

- Upload PDF or TXT documents through a Streamlit web app
- Extract PDF table-of-contents data with PyMuPDF
- Segment chapters and headings into study-sized chunks
- Generate Markdown slide summaries with OpenRouter
- Fall back to local heuristic slides when API access is unavailable
- Browse generated slides in a two-column study interface
- Chat with an OpenRouter-backed assistant before and after slide generation
- Use the active slide section as chat context after a deck is generated
- Export generated slides as a `.pptx` PowerPoint file
- Use a bundled test PDF for quick local debugging

## Tech Stack

- **Python**: core application language
- **Streamlit**: web UI
- **OpenRouter**: LLM-backed slide generation and chat
- **PyMuPDF**: PDF parsing and TOC extraction
- **python-pptx**: PowerPoint export
- **python-dotenv**: local environment configuration
- **ChromaDB / sentence-transformers**: optional legacy RAG/vector modules
- **pytest**: test runner

OpenRouter is called directly with Python's standard HTTP library in `src/openrouter_client.py`. This avoids OpenAI SDK/httpx compatibility issues such as `Client.__init__() got an unexpected keyword argument 'proxies'`.

## How It Works

1. The user uploads a PDF or TXT file in `webapp.py`.
2. `main.py` starts the document-to-slides pipeline.
3. `src/utils.py` reads PDF pages and extracts the table of contents.
4. `src/segmentor.py` groups page content by chapter and heading.
5. `src/slide_generator.py` asks OpenRouter to create Markdown slide content.
6. If API access fails and fallback is enabled, local heuristic slides are generated instead.
7. The Streamlit UI displays the deck, enables chat, and offers a PowerPoint download.

## Project Structure

```text
Book-Reader-m/
├── webapp.py                         # Streamlit web app and UI
├── main.py                           # Main slide-generation pipeline
├── requirements.txt                  # Python dependencies
├── README.md                         # Project documentation
├── .env.example                      # Example local environment variables
├── scripts/
│   └── generate_test_pdf.py          # Regenerates the bundled test PDF
├── src/
│   ├── config.py                     # Environment-backed configuration values
│   ├── models.py                     # Shared data models
│   ├── openrouter_client.py          # Direct OpenRouter chat-completion client
│   ├── segmentor.py                  # Chapter and heading segmentation
│   ├── slide_generator.py            # LLM slide generation plus local fallback
│   ├── utils.py                      # PDF loading, TOC extraction, TOC grouping
│   ├── llm.py                        # Legacy prompt helper using OpenRouter
│   ├── prompts.yaml                  # Prompt templates
│   └── vector_db.py                  # Optional legacy vector DB helper
├── rag/
│   ├── chat_engine.py                # Optional RAG chat path
│   ├── embed.py                      # Optional embedding helper
│   └── retriever.py                  # Optional Chroma retrieval helper
├── test_assets/
│   └── book_reader_test.pdf          # Stable test input
└── tests/
    ├── test_toc.py                   # TOC extraction tests
    └── test_chapter_processor.py     # Debug helpers for chapter processing
```

## Setup

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create your local environment file:

```bash
cp .env.example .env
```

Then add your OpenRouter API key to `.env`.

## Environment Variables

`.env.example` contains the expected local configuration:

```bash
OPENROUTER_API_KEY=sk-or-your-openrouter-key
OPENROUTER_MODEL=openrouter/free
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_HTTP_REFERER=http://localhost:8501
OPENROUTER_APP_TITLE=Book Reader

ALLOW_LOCAL_SLIDE_FALLBACK=true
BOOK_READER_TEST_PDF=test_assets/book_reader_test.pdf
```

`OPENROUTER_MODEL` can be any OpenRouter model ID. The default is `openrouter/free`, and you can switch to a specific model by changing only the `.env` value.

The real `.env` file is ignored by git so API keys do not get committed.

## Running The App

Start Streamlit:

```bash
python -m streamlit run webapp.py
```

Open the local URL shown by Streamlit, usually:

```text
http://localhost:8501
```

In the app:

1. Upload a PDF or TXT file.
2. Click **Generate Slides from Text**.
3. Browse the generated deck.
4. Ask questions in the chatbot panel.
5. Download the generated PowerPoint file.

## Useful Commands

Run the slide pipeline directly on the bundled test PDF:

```bash
python -c "from main import main; print(main('test_assets/book_reader_test.pdf'))"
```

Regenerate the bundled test PDF:

```bash
python scripts/generate_test_pdf.py
```

Run tests:

```bash
pytest -q
```

Run a quick syntax check:

```bash
python -m py_compile webapp.py main.py src/openrouter_client.py src/slide_generator.py src/segmentor.py
```

## Current Limitations

- AI-generated slides and chat require a valid OpenRouter key and a model with available capacity.
- The local fallback is useful for development, but it is not as strong as LLM summarization.
- The optional RAG/vector modules are still experimental compared with the main Streamlit workflow.
- PDF quality matters: documents with unclear TOCs or unusual formatting may segment less cleanly.

## Development Notes

- Keep `.env` private; use `.env.example` for shareable configuration.
- Prefer changing `OPENROUTER_MODEL` over hard-coding model IDs.
- The main production path is `webapp.py` -> `main.py` -> `src/segmentor.py` -> `src/slide_generator.py`.
- `test_assets/book_reader_test.pdf` is the quickest sanity-check input when working on parsing or slide generation.
