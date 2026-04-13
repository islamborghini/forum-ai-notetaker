"""
Notes routes.

These routes return generated notes for a session.

This is more of an MVP 2 feature, but I am including the route
structure now so the backend is already shaped around the final
flow of the app.
"""

from flask import Blueprint

from utils.responses import success_response, error_response
from services.session_service import fetch_one_session
from services.note_service import fetch_notes_by_session_id

notes_bp = Blueprint("notes", __name__)


@notes_bp.route("/session/<int:session_id>", methods=["GET"])
def get_notes(session_id: int):
    """
    Return generated notes for one session.

    The note viewer would use this route to display:
    - summary
    - topics
    - action items
    """
    session = fetch_one_session(session_id)
    if not session:
        return error_response("Session not found", 404)

    notes = fetch_notes_by_session_id(session_id)

    if not notes:
        return success_response("Notes not generated yet", None)

    return success_response("Notes retrieved successfully", notes)