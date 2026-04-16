"""
Notes routes.

These routes return generated notes for a session.

Notes represent processed learning content derived from a recording,
such as a summary, key topics, and action items. This route allows
the frontend to retrieve that structured output once it becomes
available.
"""

from flask import Blueprint, g

from middleware.auth import auth_required
from utils.responses import success_response, error_response
from services.session_service import fetch_one_session
from services.note_service import fetch_notes_by_session_id
from services.course_service import is_course_member

notes_bp = Blueprint("notes", __name__)


@notes_bp.route("/session/<int:session_id>", methods=["GET"])
@auth_required
def get_notes(session_id: int):
    """
    Return generated notes for a single session.

    Requires authentication and course membership for
    course-linked sessions.
    """
    session = fetch_one_session(session_id)
    if not session:
        return error_response("Session not found", 404)

    if session.get("course_id"):
        if not is_course_member(session["course_id"], g.user["id"]):
            return error_response("You are not a member of this course", 403)

    notes = fetch_notes_by_session_id(session_id)

    if not notes:
        return success_response("Notes not generated yet", None)

    return success_response("Notes retrieved successfully", notes)