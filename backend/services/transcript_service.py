"""
Transcript service layer.

This module connects transcript-related routes and pipeline output
to the SQLite database.

A transcript belongs to a session and stores the transcribed text
generated from an uploaded recording, along with a JSON-encoded list
of timestamped segments.
"""

import json
from datetime import datetime, timezone
from typing import Optional

from forum_ai_notetaker.db import get_connection


def save_transcript(
    session_id: int,
    transcript_text: str,
    segments: Optional[list[dict]] = None,
) -> None:
    """
    Save a transcript for a session in the database.

    This is typically called by the processing pipeline after
    transcription is completed.

    Args:
        session_id: The session this transcript belongs to.
        transcript_text: The full transcript text.
        segments: Optional list of ``{start, end, text}`` dicts.
    """
    now = datetime.now(timezone.utc).isoformat()
    segments_json = json.dumps(segments or [])

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO transcripts (session_id, content, segments, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (session_id, transcript_text, segments_json, now, now),
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
        A transcript dictionary if it exists, otherwise None. The
        ``segments`` field is decoded into a list of dicts.
    """
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT * FROM transcripts
            WHERE session_id = ?
            """,
            (session_id,),
        ).fetchone()

    if not row:
        return None

    transcript = dict(row)
    raw_segments = transcript.get("segments")
    try:
        transcript["segments"] = json.loads(raw_segments) if raw_segments else []
    except (TypeError, ValueError):
        transcript["segments"] = []
    return transcript
