import os
from dotenv import load_dotenv
from rag.retriever import get_top_k_docs
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-pro")

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

    response = model.generate_content(prompt)
    return response.text.strip()