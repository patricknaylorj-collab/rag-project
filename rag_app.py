"""RAG application entry point (GenAI Secure Coding course)."""

import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

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


class QueryRequest(BaseModel):
    question: str


def validate_user_input(text: str):
    if text is None or text.strip() == "":
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    if len(text) < 5:
        raise HTTPException(status_code=400, detail="Question is too short")

    if len(text) > 500:
        raise HTTPException(status_code=400, detail="Question is too long")


def validate_model_output(text: str):
    if text is None or text.strip() == "":
        raise HTTPException(status_code=500, detail="AI returned an empty response")

    if len(text) < 10:
        raise HTTPException(status_code=500, detail="AI response is too short")


def review_model_output(original_answer: str):
    import google.generativeai as genai

    review_prompt = f"""
You are reviewing an AI-generated response.

Your job:
- If the response is unclear, incomplete, or poorly written, improve it.
- If the response is already good, return it unchanged.

AI response to review:
{original_answer}
"""

    genai.configure(api_key=_require_gemini_api_key())
    review_model = genai.GenerativeModel("gemini-pro")
    review_response = review_model.generate_content(review_prompt)

    return review_response.text


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"status": "ok", "message": "Configuration OK: GEMINI_API_KEY is loaded."}


@app.get("/test-gemini")
def test_gemini():
    import google.generativeai as genai
    from google.api_core import exceptions as google_exceptions

    topic = "what a large language model is"
    try:
        genai.configure(api_key=_require_gemini_api_key())
        model = genai.GenerativeModel("gemini-2.0-flash")

        # Step 1: generate a short outline (intermediate; not returned to client)
        outline_prompt = (
            f"Create a short bullet-point outline (3–5 bullets) explaining {topic}. "
            "Use only the bullets, no introduction."
        )
        outline_response = model.generate_content(outline_prompt)
        outline = (outline_response.text or "").strip()
        if not outline:
            raise HTTPException(
                status_code=502,
                detail="Step 1 (outline) returned empty content.",
            )
        logger.info("Multi-step /test-gemini: outline generated (%d chars)", len(outline))

        # Step 2: expand the outline into a full paragraph (final client response)
        expand_prompt = (
            f"Using only this outline, write one clear paragraph explaining {topic}:\n\n"
            f"{outline}"
        )
        final_response = model.generate_content(expand_prompt)
        final_text = (final_response.text or "").strip()
        if not final_text:
            raise HTTPException(
                status_code=502,
                detail="Step 2 (expand) returned empty content.",
            )

        return {"response": final_text}
    except HTTPException:
        raise
    except google_exceptions.GoogleAPIError as exc:
        logger.exception("Gemini API error in /test-gemini")
        raise HTTPException(
            status_code=502,
            detail="Gemini request failed. Check server logs and API key configuration.",
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected error in /test-gemini")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while calling Gemini.",
        ) from exc


@app.post("/query")
def query_ai(request: QueryRequest):
    import google.generativeai as genai

    validate_user_input(request.question)

    genai.configure(api_key=_require_gemini_api_key())
    primary_model = genai.GenerativeModel("gemini-pro")
    primary_response = primary_model.generate_content(request.question)

    raw_answer = primary_response.text

    validate_model_output(raw_answer)

    reviewed_answer = review_model_output(raw_answer)

    return {
        "question": request.question,
        "answer": reviewed_answer
    }


def main() -> None:
    try:
        _require_gemini_api_key()
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    print("Configuration OK: GEMINI_API_KEY is loaded.")


if __name__ == "__main__":
    main()
