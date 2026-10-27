"""Section-scoped document chatbot with an offline heuristic fallback."""
import re

from src.openrouter_client import chat_completion, is_api_availability_error
from src.vector_store import retrieve_document_context


def _heuristic_answer(question: str, section_markdown: str) -> str:
    """Return a useful local answer drawn only from the active slide section."""
    lines = [line.strip().lstrip("- ").strip() for line in section_markdown.splitlines()]
    facts = [line for line in lines if line and not line.startswith("#")]
    terms = set(re.findall(r"[a-zA-Z]{3,}", question.lower()))
    ranked = sorted(facts, key=lambda line: len(terms & set(re.findall(r"[a-zA-Z]{3,}", line.lower()))), reverse=True)
    selected = [line for line in ranked if line][:3] or ["No extractable detail is available in the active slide."]
    return "Based on the active slide:\n\n" + "\n".join(f"- {line}" for line in selected)


def answer_section_question(question: str, chapter: str, section: str, section_markdown: str) -> tuple[str, bool]:
    """Answer using only active-slide context; returns (answer, used_local_fallback)."""
    messages = [
        {
            "role": "system",
            "content": "Answer briefly using only the supplied active document section. State when the section does not contain the answer.",
        },
        {
            "role": "user",
            "content": f"Chapter: {chapter}\nSection: {section}\n\nActive slide:\n{section_markdown}\n\nQuestion: {question}",
        },
    ]
    try:
        return chat_completion(messages, temperature=0.2, max_tokens=700).strip(), False
    except Exception as exc:
        # Missing credentials and network/provider failures should not disable studying.
        if is_api_availability_error(exc) or "openrouter" in str(exc).lower():
            return _heuristic_answer(question, section_markdown), True
        raise


def answer_document_question(question: str, document_id: str) -> tuple[str, bool]:
    """Answer before slides exist using ChromaDB-retrieved uploaded-document context."""
    context_chunks = retrieve_document_context(question, document_id)
    context = "\n\n".join(context_chunks)
    if not context:
        return "I could not find readable content in the uploaded document yet.", True
    messages = [
        {
            "role": "system",
            "content": "Answer briefly using only the retrieved uploaded-document context. State when it does not contain the answer.",
        },
        {"role": "user", "content": f"Document context:\n{context}\n\nQuestion: {question}"},
    ]
    try:
        return chat_completion(messages, temperature=0.2, max_tokens=700).strip(), False
    except Exception as exc:
        if is_api_availability_error(exc) or "openrouter" in str(exc).lower():
            return _heuristic_answer(question, context), True
        raise
