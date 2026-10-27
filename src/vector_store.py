"""Local ChromaDB indexing used by the document chatbot before slide generation."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Iterable

from src.models import Page

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CHROMA_DIR = PROJECT_ROOT / "backend" / "output" / "chroma_db"
COLLECTION_NAME = "uploaded_document_chunks"
EMBEDDING_DIMENSION = 256


def _embed(text: str) -> list[float]:
    """Deterministic local hashing embedding; it keeps retrieval fully offline."""
    vector = [0.0] * EMBEDDING_DIMENSION
    for token in re.findall(r"[a-zA-Z0-9]{2,}", text.lower()):
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:2], "big") % EMBEDDING_DIMENSION
        vector[index] += 1.0 if digest[2] % 2 else -1.0
    magnitude = sum(value * value for value in vector) ** 0.5
    return [value / magnitude for value in vector] if magnitude else vector


def _chunks(pages: Iterable[Page], chunk_size: int = 900) -> list[tuple[str, int]]:
    chunks = []
    for page in pages:
        text = " ".join(page.content.split())
        for start in range(0, len(text), chunk_size):
            chunk = text[start : start + chunk_size].strip()
            if chunk:
                chunks.append((chunk, page.number))
    return chunks


def _collection(storage_dir: Path | str = DEFAULT_CHROMA_DIR):
    import chromadb

    storage_dir = Path(storage_dir)
    storage_dir.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(storage_dir))
    return client.get_or_create_collection(name=COLLECTION_NAME, embedding_function=None)


def index_document(document_id: str, pages: Iterable[Page], storage_dir: Path | str = DEFAULT_CHROMA_DIR) -> int:
    """Persist uploaded source chunks in ChromaDB and return the indexed count."""
    chunks = _chunks(pages)
    if not chunks:
        return 0
    collection = _collection(storage_dir)
    collection.upsert(
        ids=[f"{document_id}:{index}" for index in range(len(chunks))],
        documents=[text for text, _ in chunks],
        embeddings=[_embed(text) for text, _ in chunks],
        metadatas=[{"document_id": document_id, "page": page} for _, page in chunks],
    )
    return len(chunks)


def retrieve_document_context(question: str, document_id: str, storage_dir: Path | str = DEFAULT_CHROMA_DIR, limit: int = 4) -> list[str]:
    """Retrieve the most relevant uploaded-document chunks for a question."""
    collection = _collection(storage_dir)
    result = collection.query(
        query_embeddings=[_embed(question)],
        n_results=limit,
        where={"document_id": document_id},
        include=["documents"],
    )
    return [document for document in result.get("documents", [[]])[0] if document]
