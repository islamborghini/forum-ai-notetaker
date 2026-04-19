"""
Notes routes.

These endpoints return generated notes for a session.

Notes are course-scoped resources, so access is restricted to users
who belong to the course associated with the session.
"""

from flask import Blueprint, g

from middleware.auth import auth_required
from utils.responses import success_response, error_response
from services.session_service import fetch_one_session
from services.note_service import get_notes_by_session
from services.course_service import is_course_member

notes_bp = Blueprint("notes", __name__)


@notes_bp.route("/session/<int:session_id>", methods=["GET"])
@auth_required
def get_notes(session_id: int):
    """
    Return notes for a session if the user is authorized.

    Returns 404 if the session does not exist.
    Returns 403 if the user is not a member of the session's course.
    Returns 200 with data: null if notes are not yet generated.
    Returns 200 with the notes object once available.
    """
    session = fetch_one_session(session_id)
    if not session:
        return error_response("Session not found", 404)

    if session.get("course_id"):
        if not is_course_member(session["course_id"], g.user["id"]):
            return error_response("You do not have access to these notes", 403)

    notes = get_notes_by_session(session_id)
    if not notes:
        return success_response("Notes not generated yet", None)

    return success_response("Notes retrieved successfully", notes)