"""
Transcript routes.

These endpoints return transcript data for a session.
Transcripts are course-scoped resources, so access is restricted to
users who belong to the course associated with the session.
"""

from flask import Blueprint, g

from middleware.auth import auth_required
from utils.responses import success_response, error_response
from services.session_service import fetch_one_session
from services.transcript_service import fetch_transcript_by_session_id
from services.course_service import is_course_member

transcripts_bp = Blueprint("transcripts", __name__)


@transcripts_bp.route("/<int:session_id>", methods=["GET"])
@auth_required
def get_transcript(session_id: int):
    """
    Return the transcript for a session if the user is authorized.

    Returns 404 if the session does not exist.
    Returns 403 if the user is not a member of the session's course.
    Returns 200 with data: null if transcription is not yet complete.
    Returns 200 with the transcript object once available.
    """
    session = fetch_one_session(session_id)
    if not session:
        return error_response("Session not found", 404)

    if session.get("course_id"):
        if not is_course_member(session["course_id"], g.user["id"]):
            return error_response("You do not have access to this transcript", 403)

    transcript = fetch_transcript_by_session_id(session_id)
    if not transcript:
        return success_response("Transcript not ready yet", None)

    return success_response("Transcript retrieved successfully", transcript)
