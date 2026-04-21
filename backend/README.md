# Backend – Forum Notetaker API

## Overview

This backend provides the API for the forum notetaker application. It connects the frontend interface with the processing pipeline and the data layer.

The backend receives uploaded class recordings, validates requests, triggers the processing workflow, and exposes endpoints that allow the frontend to retrieve transcripts and generated notes.

Current pipeline flow:

```text
Upload recording -> Extract audio -> Transcribe with Whisper -> Save transcript -> Generate notes with Groq -> Save notes -> Update status to notes_generated
```

---

## Project Structure

- **app.py** - initializes the Flask server and registers routes
- **routes** - API endpoints used by the frontend
- **services** - interface between routes, Groq note generation, and the data layer
- **utils** - helpers for validation and response formatting
- **pipeline** - orchestration for transcription and note generation

---

## Backend Setup

1. Create and activate a virtual environment.
2. Install dependencies from `requirements.txt`.
3. Install `openai-whisper` if it is not already available in your environment.
4. Add environment variables in `backend/.env` if you want to override local defaults.
5. Start the Flask server.

Example:

```bash
cd backend
python -m venv ../venv
source ../venv/bin/activate
pip install -r requirements.txt
pip install openai-whisper
python app.py
```

Environment variables:

- `JWT_SECRET_KEY` - optional for local use; if omitted, auth falls back to a bundled dev secret
- `GROQ_API_KEY` - optional; if omitted, notes fall back to the local heuristic summary flow

---

## API Endpoints

- GET /api/health
- POST /api/sessions/upload
- GET /api/sessions
- GET /api/transcripts/<session_id>
- GET /api/notes/session/<session_id>
