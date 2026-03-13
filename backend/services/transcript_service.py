"""
Transcript service layer.

Like the session service, this is a placeholder interface that
keeps the backend routes stable even before full DB integration.
"""

from typing import Optional

TRANSCRIPTS = {}


def save_transcript(session_id: int, transcript_text: str) -> None:
    """
    Save transcript data for a session.
    """
    TRANSCRIPTS[session_id] = {
        "session_id": session_id,
        "text": transcript_text
    }


def fetch_transcript_by_session_id(session_id: int) -> Optional[dict]:
    """
    Return transcript data for a session if it exists.
    """
    return TRANSCRIPTS.get(session_id)