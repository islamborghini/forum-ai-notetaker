"""
Transcript service layer.

This module connects transcript-related routes and pipeline output
to the SQLite database.

A transcript belongs to a session and stores the transcribed text
generated from an uploaded recording.
"""

from datetime import datetime, timezone
from typing import Optional

from forum_ai_notetaker.db import get_connection


def save_transcript(session_id: int, transcript_text: str) -> None:
    """
    Save a transcript for a session in the database.

    This is typically called by the processing pipeline after
    transcription is completed.

    Args:
        session_id: The session this transcript belongs to.
        transcript_text: The full transcript text.
    """
    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO transcripts (session_id, content, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            """,
            (session_id, transcript_text, now, now),
        )
        conn.commit()


def fetch_transcript_by_session_id(session_id: int) -> Optional[dict]:
    """
    Retrieve the transcript associated with a session.

    If no transcript has been generated yet, this returns None.
    The route layer can use that to return a safe empty or
    loading state instead of failing.

    Args:
        session_id: The session being requested.

    Returns:
        A transcript dictionary if it exists, otherwise None.
    """
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT * FROM transcripts
            WHERE session_id = ?
            """,
            (session_id,),
        ).fetchone()

    return dict(row) if row else None