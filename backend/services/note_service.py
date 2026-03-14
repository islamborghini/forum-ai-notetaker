"""
Notes service layer.

This stores and returns generated notes. Again, this is mocked
in memory for now so the full backend flow can be tested early.
"""

from typing import Optional

NOTES = {}


def save_notes(session_id: int, summary: str, topics: list[str], action_items: list[str]) -> None:
    """
    Save generated notes for a session.
    """
    NOTES[session_id] = {
        "session_id": session_id,
        "summary": summary,
        "topics": topics,
        "action_items": action_items
    }


def fetch_notes_by_session_id(session_id: int) -> Optional[dict]:
    """
    Return generated notes for a session if they exist.
    """
    return NOTES.get(session_id)