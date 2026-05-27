# RAG Project

This repository contains my Retrieval-Augmented Generation (RAG) project for the GenAI Secure Coding course.

This project will be built incrementally each week.

## Week 6 — Multi-step Gemini execution

### Multi-step flow

`GET /test-gemini` now runs **two sequential Gemini calls** inside `test_gemini()` in `rag_app.py`:

| Step | Responsibility | Returned to client? |
|------|----------------|---------------------|
| **1 — Outline** | Ask Gemini for a short bullet-point outline on what a large language model is | No (stored in `outline`, logged at INFO) |
| **2 — Expand** | Ask Gemini to write one paragraph using **only** that outline | Yes — `{"response": "<paragraph>"}` |

The output of Step 1 is passed into the Step 2 prompt, so the final paragraph depends on the earlier model output.

### Why the steps are separated

- **Control:** Each step has one job (structure first, prose second).
- **Reuse:** The same pattern scales to RAG (retrieve → summarize), validation, and refinement later in the course.
- **Server-side only:** Both calls and the intermediate outline stay on the backend; clients still see the same JSON shape as Week 5.

### Run and test

Same as Week 5:

```bash
uvicorn rag_app:app --reload
```

| Endpoint | Expected result |
|----------|-----------------|
| `GET /health` | `{"status": "ok"}` |
| `GET /test-gemini` | `{"response": "<paragraph expanded from outline>"}` |

On failure, the API returns a **generic** error message (no API key in the response). Check server logs for details.

### Challenges / open questions

- **Invalid API key in local `.env`:** If `/test-gemini` returns 502, replace `GEMINI_API_KEY` with a valid key from Google AI Studio.
- **Latency:** Two calls take roughly twice as long as one; acceptable for this exercise, worth caching or streaming in production.

## Week 5 — Server-side Gemini call

### Run and test

From the project root with the venv activated:

```bash
uvicorn rag_app:app --reload
```

| Endpoint | Expected result |
|----------|-----------------|
| `GET /health` | `{"status": "ok"}` |
| `GET /test-gemini` | `{"response": "<Gemini-generated paragraph>"}` |

If `/test-gemini` fails, check `.env` for a valid `GEMINI_API_KEY`, confirm `pip install -r requirements.txt`, and read the server error (e.g. `API_KEY_INVALID` means the key is missing or placeholder).

### What `/test-gemini` does

`GET /test-gemini` sends a **hardcoded prompt** to Gemini and returns the model’s text in JSON. It does **not** accept user input, documents, chunking, embeddings, or retrieval—those come in later weeks.

Example prompt: *“Explain what a large language model is in one paragraph.”*

### Where the Gemini call lives

All Week 5 Gemini logic is in **`test_gemini()`** in `rag_app.py`:

1. `genai.configure(api_key=...)` using the existing `_require_gemini_api_key()` helper (key loaded from `.env` at startup).
2. `genai.GenerativeModel("gemini-2.0-flash")` to create the model.
3. `model.generate_content(prompt)` to send the prompt.
4. `response.text` to read the reply, returned as `{"response": ...}`.

The API key stays in **`.env`** on the server; clients never see it. This mirrors production GenAI apps: backend-only AI calls, controlled cost, and enforceable security—the same foundation RAG builds on.

### What I learned from the Gemini documentation

- The Python SDK uses **`GenerativeModel`** plus **`generate_content`**; the text answer is in **`response.text`**.
- Official docs at [ai.google.dev](https://ai.google.dev) now emphasize the newer `google-genai` package; this course uses **`google-generativeai`** per `requirements.txt`.
- Reading API docs (model names, request shape, error codes like invalid API key) is as important as writing the call.

## Setup (all weeks)

- **Python environment:** A local virtual environment (`venv/`) using **Python 3.10**, created in the project root. Dependencies are installed with `pip install -r requirements.txt`.
- **Dependencies (`requirements.txt`):** `fastapi`, `uvicorn`, `python-dotenv`, and `google-generativeai`.
- **Configuration:** A **`.env`** file in the project root holds **`GEMINI_API_KEY`**. Variables are loaded with `python-dotenv`. **`.env` is gitignored`** so it is not committed.
- **`.gitignore`:** Ignores virtualenv folders (`venv/`, `.venv/`), **`.env`**, Python bytecode caches (`__pycache__/`, `pycache/`), and common junk (e.g. `.DS_Store`).

## Purpose of `rag_app.py`

`rag_app.py` is the application entry point. It loads `.env`, validates `GEMINI_API_KEY` on startup, exposes FastAPI routes (`/health`, `/`, `/test-gemini`), and keeps Gemini calls on the server.

## Questions / uncertainties

- **`google-generativeai` deprecation:** The package warns that support is moving to `google.genai`; I will switch when the course does.
- **Model name:** Week 5 uses `gemini-2.0-flash`; if the API rejects that name for an account, I may need to try `gemini-1.5-flash` or another listed model.
- **Python version:** Local env uses **3.10**; I will move to 3.12+ if the course requires it.

## Git commands used so far

- git clone  
- git status  
- git add  
- git commit  
- git push  
- git checkout  
- git pull (including merge options when branches diverged)
