"""
Transcript routes.

These routes return transcript data for a session.

A transcript is course-related learning content, so this route should
eventually follow the same access-control model as notes and sessions.
For now, it returns transcript state safely so the frontend can render
either the transcript itself or an empty/loading state.
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
    Return the transcript for a single session.

    Requires authentication and course membership for
    course-linked sessions.
    """
    session = fetch_one_session(session_id)
    if not session:
        return error_response("Session not found", 404)

    if session.get("course_id"):
        if not is_course_member(session["course_id"], g.user["id"]):
            return error_response("You are not a member of this course", 403)

    transcript = fetch_transcript_by_session_id(session_id)

    if not transcript:
        return success_response("Transcript not ready yet", None)

    return success_response("Transcript retrieved successfully", transcript)