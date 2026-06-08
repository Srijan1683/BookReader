import os

from dotenv import load_dotenv
from openai import OpenAI


DEFAULT_OPENROUTER_MODEL = "openrouter/free"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def get_openrouter_model():
    load_dotenv()
    return os.getenv("OPENROUTER_MODEL", DEFAULT_OPENROUTER_MODEL)


def get_openrouter_client():
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY is missing. Add it to .env or enable local fallback."
        )

    return OpenAI(
        api_key=api_key,
        base_url=os.getenv("OPENROUTER_BASE_URL", OPENROUTER_BASE_URL),
        default_headers={
            "HTTP-Referer": os.getenv("OPENROUTER_HTTP_REFERER", "http://localhost:8501"),
            "X-OpenRouter-Title": os.getenv("OPENROUTER_APP_TITLE", "Book Reader"),
        },
    )


def chat_completion(messages, *, model=None, temperature=0.3, max_tokens=1200, response_format=None):
    client = get_openrouter_client()
    params = {
        "model": model or get_openrouter_model(),
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if response_format is not None:
        params["response_format"] = response_format

    response = client.chat.completions.create(**params)
    return response.choices[0].message.content or ""


def is_api_availability_error(exc):
    message = str(exc).lower()
    return any(
        marker in message
        for marker in (
            "401",
            "402",
            "403",
            "429",
            "quota",
            "rate limit",
            "insufficient",
            "credits",
            "api key",
            "missing",
        )
    )
