"""
Session service layer.

Connects the backend API to the SQLite database.
"""

from datetime import datetime, timezone
from typing import Optional

from forum_ai_notetaker.db import get_connection


def _row_to_dict(row) -> dict:
    return dict(row)


def create_session_record(title: str, filename: str, recording_path: str, status: str) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO sessions (title, original_filename, stored_path, status, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (title, filename, recording_path, status, now, now),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM sessions WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return _row_to_dict(row)


def fetch_all_sessions() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM sessions ORDER BY created_at DESC").fetchall()
    return [_row_to_dict(r) for r in rows]


def fetch_one_session(session_id: int) -> Optional[dict]:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
    return _row_to_dict(row) if row else None


def update_session_status(session_id: int, new_status: str) -> None:
    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        conn.execute(
            "UPDATE sessions SET status = ?, updated_at = ? WHERE id = ?",
            (new_status, now, session_id),
        )
        conn.commit()