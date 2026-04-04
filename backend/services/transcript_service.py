"""
Transcript service layer.

Connects the backend API to the SQLite database.
"""

from datetime import datetime, timezone
from typing import Optional

from forum_ai_notetaker.db import get_connection


def save_transcript(session_id: int, transcript_text: str) -> None:
    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO transcripts (session_id, content, created_at, updated_at) "
            "VALUES (?, ?, ?, ?)",
            (session_id, transcript_text, now, now),
        )
        conn.commit()


def fetch_transcript_by_session_id(session_id: int) -> Optional[dict]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM transcripts WHERE session_id = ?", (session_id,)
        ).fetchone()
    return dict(row) if row else None