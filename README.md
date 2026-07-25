# 📚 Book Reader

**Turning textbooks into study decks — automatically.**

Book Reader is a Streamlit application that converts textbook-style PDF or TXT documents into interactive, chapter-aware study decks. It extracts document structure, segments content by chapter and heading, generates concise Markdown slides via OpenRouter, supports contextual chatbot Q&A on the active section, and exports the final deck as a downloadable PowerPoint file.

This project was completed as a **B.Tech Computer Science and Engineering major project** at **Delhi Technical Campus, GGSIPU**.

**🔗 Live Demo:** [srijan-bookreader.streamlit.app](https://srijan-bookreader.streamlit.app)
**🔗 GitHub:** [github.com/Srijan1683/BookReader](https://github.com/Srijan1683/BookReader)

---

## 🎓 Academic Evaluation

This project was submitted and graded as the final-year major project.

| Evaluation Component            | Score        |
|----------------------------------|--------------|
| Dissertation & Viva Voce         | 93           |
| Project Progress Evaluation      | 97           |
| **Overall Percentage**           | **95%**      |
| Final Semester CGPA              | **10**       |

**Institution:** Delhi Technical Campus, GGSIPU (Guru Gobind Singh Indraprastha University)

---

## ✨ Features

- Upload PDF or TXT documents through a clean Streamlit web interface
- Extract PDF table-of-contents data with PyMuPDF
- Segment documents into chapter-level and heading-level study chunks
- Generate 2–4 concise study slides per heading using OpenRouter-hosted LLMs
- Local heuristic fallback when API access is unavailable — the app never fully breaks
- Browse the deck slide-by-slide with previous/next controls
- Jump directly to any chapter or slide via dropdown navigation
- Continuous, globally numbered slides across the whole deck
- Ask a contextual chatbot questions about the currently active section
- Export the full generated deck as a downloadable `.pptx` file

## 🛠️ Tech Stack

| Layer | Tools |
|---|---|
| UI | Streamlit |
| LLM | OpenRouter (direct HTTP client — no SDK dependency) |
| PDF Parsing | PyMuPDF |
| Slide Export | python-pptx |
| Config | python-dotenv |
| Testing | pytest |

## 🏗️ Architecture

**Application flow:**

1. `webapp.py` accepts the uploaded document and starts the generation flow
2. `src/utils.py` extracts pages and table-of-contents entries
3. `src/segmentor.py` groups the document into chapter and heading chunks
4. `src/slide_generator.py` generates Markdown slide content via OpenRouter, with a local fallback path when the API is unavailable
5. `src/deck.py` normalizes slide titles and assigns global slide numbers across the deck
6. `webapp.py` renders the slide browser, chatbot, chapter/slide jump controls, and PowerPoint export

**Key design decisions:**

- OpenRouter is called directly through Python's standard HTTP library (`src/openrouter_client.py`) rather than the OpenAI SDK, avoiding SDK/proxy compatibility issues
- The model is fully configurable via the `OPENROUTER_MODEL` environment variable — no hard-coded model IDs
- A local heuristic slide generator acts as a graceful fallback (`ALLOW_LOCAL_SLIDE_FALLBACK`) if the API is down or unreachable
- ChromaDB-backed retrieval (`rag/`) exists as an optional legacy path and is not part of the main production flow

## 📁 Project Structure

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
├── rag/                               # Optional legacy retrieval-augmented chat
│   ├── chat_engine.py
│   ├── embed.py
│   └── retriever.py
├── test_assets/
│   └── book_reader_test.pdf          # Stable test input
└── tests/
    ├── test_deck.py
    ├── test_toc.py
    └── test_chapter_processor.py
```

## 🚀 Getting Started

**1. Clone and install dependencies:**

```bash
git clone https://github.com/Srijan1683/BookReader.git
cd BookReader
pip install -r requirements.txt
```

**2. Configure environment variables** (create a `.env` file):

```
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=your_model_id
ALLOW_LOCAL_SLIDE_FALLBACK=true
```

**3. Run the app:**

```bash
python -m streamlit run webapp.py
```

## 🧪 Testing

```bash
pytest -q
```

Run a quick syntax check across core modules:

```bash
python -m py_compile webapp.py main.py src/openrouter_client.py src/slide_generator.py src/segmentor.py src/deck.py
```

---

## 👤 Author

**Srijan Banerjee**
B.Tech, Computer Science and Engineering — Delhi Technical Campus, GGSIPU

- Portfolio: [srijan-banerjee.netlify.app](https://srijan-banerjee.netlify.app)
- GitHub: [github.com/Srijan1683](https://github.com/Srijan1683)
- LinkedIn: [linkedin.com/in/banerjee-srijan](https://www.linkedin.com/in/banerjee-srijan)