"""
Transcript routes.

These routes return transcript data for a session.

This belongs in MVP 1 because even the first useful version
of the app should already let the frontend display transcript
state, even if the rest of the system is still mocked.
"""

from flask import Blueprint

from utils.responses import success_response, error_response
from services.session_service import fetch_one_session
from services.transcript_service import fetch_transcript_by_session_id

transcripts_bp = Blueprint("transcripts", __name__)


@transcripts_bp.route("/<int:session_id>", methods=["GET"])
def get_transcript(session_id: int):
    """
    Return the transcript for one session.

    If a transcript does not exist yet, this route should still
    return a safe response so the frontend can show an empty
    or loading state instead of breaking.
    """
    session = fetch_one_session(session_id)
    if not session:
        return error_response("Session not found", 404)

    transcript = fetch_transcript_by_session_id(session_id)

    if not transcript:
        return success_response("Transcript not ready yet", None)

    return success_response("Transcript retrieved successfully", transcript)