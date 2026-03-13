# Backend Foundation

This folder contains the Sprint 1 backend foundation for the database and storage layer.

## What is included

- SQLite schema for `sessions` and `transcripts`
- Database helpers for creating sessions and storing transcripts
- Upload storage helper that writes files into `./uploads/`
- A tiny CLI entrypoint to initialize the local database

## Quick start

Initialize the local database:

```bash
python3 -m backend.forum_ai_notetaker
```

Example usage inside Flask routes or the processing pipeline:

```python
from backend.forum_ai_notetaker import (
    create_session,
    get_transcript,
    init_db,
    list_sessions,
    save_transcript,
    save_uploaded_file,
)

init_db()

stored_path = save_uploaded_file(request.files["recording"])
session = create_session(
    title="Week 3 Forum",
    original_filename=request.files["recording"].filename,
    stored_path=stored_path,
)

save_transcript(session["id"], "Raw Whisper transcript text")
sessions = list_sessions()
transcript = get_transcript(session["id"])
```
