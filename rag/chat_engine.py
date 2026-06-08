from rag.retriever import get_top_k_docs
from src.openrouter_client import chat_completion

def build_prompt(context_chunks, question):
    context_text = "\n\n".join([f"- {chunk}" for chunk, _ in context_chunks])
    return f"""
You are an AI assistant helping with questions from a textbook.

Based on the following content from the book, answer the user's question.

Context:
{context_text}

Question: {question}

Answer:
"""

def ask_question_rag(question: str) -> str:
    context_chunks = get_top_k_docs(question)
    prompt = build_prompt(context_chunks, question)

    return chat_completion(
        [
            {
                "role": "system",
                "content": "You answer questions using the retrieved textbook context.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=900,
    ).strip()
