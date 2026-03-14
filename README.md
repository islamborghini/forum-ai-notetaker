# Forum AI Notetaker

An AI-powered web app that converts lecture and meeting recordings into structured transcripts. Upload a recording of a class, and the system automatically extracts audio, transcribes it using OpenAI Whisper, and stores the result for easy access.

## Features

- Upload video/audio recordings (mp4, mp3, wav, m4a)
- Automatic audio extraction via FFmpeg
- Speech-to-text transcription via OpenAI Whisper
- Session tracking with status updates (uploaded → processing → transcribed)
- Persistent storage with SQLite
- REST API with React frontend

## Workflow

```
Upload recording → Extract audio (FFmpeg) → Transcribe (Whisper) → Save to SQLite
```

1. User uploads a recording through the frontend or API
2. Backend saves the file and creates a session record
3. FFmpeg extracts mono 16kHz WAV audio from the file
4. Whisper (`base.en` model) transcribes the audio to text
5. Transcript is saved to SQLite and session status is updated

## Setup

### Prerequisites

- Python 3.9+
- Node.js
- FFmpeg (`brew install ffmpeg` on macOS)

### Backend

```bash
cd backend
python -m venv ../venv
source ../venv/bin/activate
pip install -r requirements.txt
pip install openai-whisper
python app.py
```

The server runs at `http://localhost:5000`. The database is auto-initialized on startup.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The dev server runs at `http://localhost:5173`.

## API Endpoints

### Health

| Method | Endpoint       | Description          |
|--------|---------------|----------------------|
| GET    | `/`           | API running message  |
| GET    | `/api/health` | Health check         |

### Sessions

| Method | Endpoint                    | Description              |
|--------|-----------------------------|--------------------------|
| GET    | `/api/sessions/`            | List all sessions        |
| GET    | `/api/sessions/<id>`        | Get session by ID        |
| POST   | `/api/sessions/upload`      | Upload a recording       |

**Upload request:**

```bash
curl -X POST http://localhost:5000/api/sessions/upload \
  -F "file=@recording.mp4" \
  -F "title=My Lecture"
```

### Transcripts

| Method | Endpoint                         | Description                    |
|--------|----------------------------------|--------------------------------|
| GET    | `/api/transcripts/<session_id>`  | Get transcript for a session   |

