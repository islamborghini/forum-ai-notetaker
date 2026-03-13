"""
Session service layer.

This file acts as the boundary between the backend API layer
and the eventual database layer.

For now I am using in-memory placeholder storage so the backend
can actually run and be tested before full DB integration is done.
That way the routes are already stable and the DB teammate can
later replace the internals without forcing a rewrite of my API code.
"""

from typing import Optional

SESSIONS = []
NEXT_SESSION_ID = 1


def create_session_record(title: str, filename: str, recording_path: str, status: str) -> dict:
    """
    Create a new session record.

    For now this stores data in memory.
    Later this function should be replaced with real DB logic.
    """
    global NEXT_SESSION_ID

    session = {
        "id": NEXT_SESSION_ID,
        "title": title,
        "filename": filename,
        "recording_path": recording_path,
        "status": status
    }

    SESSIONS.append(session)
    NEXT_SESSION_ID += 1
    return session


def fetch_all_sessions() -> list[dict]:
    """
    Return all sessions.
    """
    return SESSIONS


def fetch_one_session(session_id: int) -> Optional[dict]:
    """
    Return one session by ID.
    """
    return next((session for session in SESSIONS if session["id"] == session_id), None)


def update_session_status(session_id: int, new_status: str) -> None:
    """
    Update the status of a session.

    This matters because the frontend dashboard needs to know
    what stage of the workflow a session is currently in.
    """
    session = fetch_one_session(session_id)
    if session:
        session["status"] = new_status