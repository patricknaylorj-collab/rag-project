"""RAG application entry point (GenAI Secure Coding course)."""

import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI

_ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(_ENV_PATH)


def _require_gemini_api_key() -> str:
    key = (os.getenv("GEMINI_API_KEY") or "").strip()
    if not key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing or empty. "
            "Set GEMINI_API_KEY in the project root .env file."
        )
    return key


@asynccontextmanager
async def lifespan(app: FastAPI):
    _require_gemini_api_key()
    yield


app = FastAPI(title="RAG project", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"status": "ok", "message": "Configuration OK: GEMINI_API_KEY is loaded."}


@app.get("/test-gemini")
def test_gemini():
    import google.generativeai as genai

    genai.configure(api_key=_require_gemini_api_key())
    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = "Explain what a large language model is in one paragraph."
    response = model.generate_content(prompt)
    return {"response": response.text}


def main() -> None:
    try:
        _require_gemini_api_key()
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    print("Configuration OK: GEMINI_API_KEY is loaded.")


if __name__ == "__main__":
    main()
