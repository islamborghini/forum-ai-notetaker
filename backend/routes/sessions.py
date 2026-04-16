"""
Session routes.

A session represents one uploaded course recording.

This file defines the entry points for:
- retrieving uploaded recordings
- handling the upload workflow

The upload route is where authentication and permission checks
are enforced before a recording enters the system. It acts as the
gateway between the frontend and the backend processing pipeline.
"""

import uuid
from pathlib import Path
from flask import Blueprint, request, current_app, g

from middleware.auth import auth_required
from utils.responses import success_response, error_response
from utils.validators import allowed_file, safe_filename
from services.session_service import (
    create_session_record,
    fetch_sessions_for_user,
    fetch_one_session,
)
from services.course_service import get_course_by_id, is_course_member, is_ta_or_professor
from pipeline.trigger import trigger_pipeline

sessions_bp = Blueprint("sessions", __name__)


@sessions_bp.route("/", methods=["GET"])
@auth_required
def get_sessions():
    """
    Return sessions for the authenticated user's courses.
    """
    sessions = fetch_sessions_for_user(g.user["id"])
    return success_response("Sessions retrieved successfully", sessions)


@sessions_bp.route("/<int:session_id>", methods=["GET"])
@auth_required
def get_session(session_id: int):
    """
    Return a single session by ID. Verifies course membership.
    """
    session = fetch_one_session(session_id)

    if not session:
        return error_response("Session not found", 404)

    if session.get("course_id"):
        if not is_course_member(session["course_id"], g.user["id"]):
            return error_response("You are not a member of this course", 403)

    return success_response("Session retrieved successfully", session)


@sessions_bp.route("/upload", methods=["POST"])
@auth_required
def upload_session():
    """
    Upload a recording and trigger processing.

    This route is responsible for validating the request,
    enforcing permissions, storing the file, and initiating
    the pipeline.

    Requirements:
    - the user must be authenticated
    - a course_id must be provided in the request
    - the user must be a TA or professor for that course

    Important:
    The current database schema does not yet link sessions to courses.
    Because of this, course_id is used only for permission validation
    at upload time and is not persisted with the session.

    This keeps the permission logic in place without introducing
    inconsistencies with the existing data model.
    """

    if "file" not in request.files:
        return error_response("No file provided", 400)

    file = request.files["file"]
    title = request.form.get("title", "").strip()
    course_id_raw = request.form.get("course_id", "").strip()

    if file.filename == "":
        return error_response("No file selected", 400)

    if not title:
        return error_response("Title is required", 400)

    if not course_id_raw:
        return error_response("course_id is required", 400)

    try:
        course_id = int(course_id_raw)
    except ValueError:
        return error_response("course_id must be an integer", 400)

    course = get_course_by_id(course_id)
    if not course:
        return error_response("Course not found", 404)

    if not is_ta_or_professor(course_id, g.user["id"]):
        return error_response("Only a TA or professor can upload to this course", 403)

    if not allowed_file(file.filename):
        return error_response("Unsupported file type", 400)

    original_filename = safe_filename(file.filename)

    file_ext = ""
    if "." in original_filename:
        file_ext = "." + original_filename.rsplit(".", 1)[1].lower()

    unique_filename = f"{uuid.uuid4().hex}{file_ext}"

    upload_folder = Path(current_app.config["UPLOAD_FOLDER"]).expanduser().resolve()
    upload_folder.mkdir(parents=True, exist_ok=True)

    file_path = upload_folder / unique_filename
    file.save(str(file_path))

    # Store a backend-relative path, not an absolute machine path.
    stored_path = str(Path("uploads") / unique_filename)

    session = create_session_record(
        title=title,
        original_filename=original_filename,
        stored_path=stored_path,
        status="uploaded",
        course_id=course_id,
    )

    trigger_pipeline(stored_path, session["id"])

    return success_response("Recording uploaded successfully", session, 201)