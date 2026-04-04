"""
Session service layer.

A session represents one uploaded class recording tied to a course.
Connects the backend API to the SQLite database.
"""

from datetime import datetime, timezone
from typing import Optional

from forum_ai_notetaker.db import get_connection

def create_session_record(
    title: str,
    filename: str,
    recording_path: str,
    status: str,
    course_id: int
) -> dict:
    """
    Create a session record tied to a course.
    """
    global NEXT_SESSION_ID

    session = {
        "id": NEXT_SESSION_ID,
        "title": title,
        "filename": filename,
        "recording_path": recording_path,
        "status": status,
        "course_id": course_id
    }

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


def fetch_sessions_for_course(course_id: int) -> list[dict]:
    """
    Return all sessions for one course.
    """
    return [session for session in SESSIONS if session["course_id"] == course_id]


def update_session_status(session_id: int, new_status: str) -> None:
    """
    Update the status of a session.
    """
    session = fetch_one_session(session_id)
    if session:
        session["status"] = new_status
    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        conn.execute(
            "UPDATE sessions SET status = ?, updated_at = ? WHERE id = ?",
            (new_status, now, session_id),
        )
        conn.commit()
