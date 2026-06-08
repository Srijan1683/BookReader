import os
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from dotenv import load_dotenv


DEFAULT_OPENROUTER_MODEL = "openrouter/free"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
REQUEST_TIMEOUT_SECONDS = 60


def get_openrouter_model():
    load_dotenv()
    return os.getenv("OPENROUTER_MODEL", DEFAULT_OPENROUTER_MODEL)


def get_openrouter_api_key():
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY is missing. Add it to .env or enable local fallback."
        )
    return api_key


def get_openrouter_base_url():
    load_dotenv()
    return os.getenv("OPENROUTER_BASE_URL", OPENROUTER_BASE_URL).rstrip("/")


def chat_completion(messages, *, model=None, temperature=0.3, max_tokens=1200, response_format=None):
    payload = {
        "model": model or get_openrouter_model(),
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if response_format is not None:
        payload["response_format"] = response_format

    request = Request(
        f"{get_openrouter_base_url()}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {get_openrouter_api_key()}",
            "Content-Type": "application/json",
            "HTTP-Referer": os.getenv("OPENROUTER_HTTP_REFERER", "http://localhost:8501"),
            "X-OpenRouter-Title": os.getenv("OPENROUTER_APP_TITLE", "Book Reader"),
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            response_data = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenRouter request failed with HTTP {exc.code}: {error_body}") from exc
    except URLError as exc:
        raise RuntimeError(f"OpenRouter request failed: {exc.reason}") from exc

    try:
        return response_data["choices"][0]["message"].get("content") or ""
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Unexpected OpenRouter response: {response_data}") from exc


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
