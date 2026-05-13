# RAG Project

This repository contains my Retrieval-Augmented Generation (RAG) project for the GenAI Secure Coding course.

This project will be built incrementally each week.

## This week's setup

- **Python environment:** A local virtual environment (`venv/`) using **Python 3.10**, created in the project root. Dependencies are installed with `pip install -r requirements.txt`.
- **Dependencies (`requirements.txt`):** `fastapi`, `uvicorn`, `python-dotenv`, and `google-generativeai` for a small web API and Gemini-related work later.
- **Configuration:** A **`.env`** file in the project root holds secrets and config (for example **`GEMINI_API_KEY`**). Variables are loaded with `python-dotenv`. **`.env` is gitignored** so it is not committed.
- **`.gitignore`:** Ignores virtualenv folders (`venv/`, `.venv/`), **`.env`**, Python bytecode caches (`__pycache__/`, `pycache/`), and common junk (e.g. `.DS_Store`).
- **Repository:** Cloned from GitHub; local `main` was reconciled with `origin/main` when histories diverged (merge with unrelated histories where needed).
- **Server (smoke test):** The app can be run with  
  `uvicorn rag_app:app --reload`  
  from the project root with the venv activated (default URL: http://127.0.0.1:8000/).

## Purpose of `rag_app.py`

`rag_app.py` is the **application entry point** for this phase of the project. It does **not** implement RAG retrieval or generation yet.

Right now it:

1. **Loads environment variables** from the project root **`.env`** file.
2. **Requires `GEMINI_API_KEY`** to be set and non-empty; if it is missing, the CLI exits with a clear error, and the FastAPI app fails startup with a clear error.
3. Exposes a minimal **FastAPI** `app` (with a **lifespan** hook that runs the same key check on startup) and a **`GET /`** route that confirms configuration when the key is present.
4. Supports a **CLI check** via `python rag_app.py`, which only verifies configuration and prints a success message.

Later weeks can add document loading, embeddings, retrieval, and Gemini calls while keeping configuration in one place.

## Questions / uncertainties

- **`google-generativeai` deprecation:** Installing the package may warn that support is moving to a newer SDK (`google.genai`). I am still using `google-generativeai` as specified for the course until the curriculum or assignment explicitly switches.
- **`GOOGLE_API_KEY` vs `GEMINI_API_KEY`:** The app currently **validates `GEMINI_API_KEY` only**. If the Gemini client expects `GOOGLE_API_KEY` in some examples, I may need to align naming or set both to the same value—TBD when RAG code is added.
- **Python version:** The environment uses **3.10** on this machine because **3.12** was not installed without admin rights; I will move to 3.12 if the course requires it once it is available here.

## Git commands used so far

- git clone  
- git status  
- git add  
- git commit  
- git push  
- git checkout  
- git pull (including merge options when branches diverged)
