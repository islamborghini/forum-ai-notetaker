"""
Session routes.

A session represents one uploaded course recording.
This file handles the upload flow and session retrieval.
"""

import uuid
from flask import Blueprint, request, current_app, g
from pathlib import Path
from flask import Blueprint, request, current_app

from middleware.auth import auth_required
from utils.responses import success_response, error_response
from utils.validators import allowed_file, safe_filename
from services.session_service import (
    create_session_record,
    fetch_all_sessions,
    fetch_one_session,
)
from services.course_service import get_course_by_id, is_ta_or_professor
from pipeline.trigger import trigger_pipeline

sessions_bp = Blueprint("sessions", __name__)


@sessions_bp.route("/", methods=["GET"])
def get_sessions():
    """
    Return all sessions.
    """
    sessions = fetch_all_sessions()
    return success_response("Sessions retrieved successfully", sessions)


@sessions_bp.route("/<int:session_id>", methods=["GET"])
def get_session(session_id: int):
    """
    Return one session by ID.
    """
    session = fetch_one_session(session_id)

    if not session:
        return error_response("Session not found", 404)

    return success_response("Session retrieved successfully", session)


@sessions_bp.route("/upload", methods=["POST"])
@auth_required
def upload_session():
    """
    Upload a recording to a course.

    Requires:
    - authenticated user
    - course_id
    - user must be TA or professor in that course
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

    if not allowed_file(file.filename):
        return error_response("Unsupported file type", 400)

    course = get_course_by_id(course_id)
    if not course:
        return error_response("Course not found", 404)

    if not is_ta_or_professor(course_id, g.user["id"]):
        return error_response("Only a TA or professor can upload to this course", 403)

    original_filename = safe_filename(file.filename)

    file_ext = ""
    if "." in original_filename:
        file_ext = "." + original_filename.rsplit(".", 1)[1].lower()

    unique_filename = f"{uuid.uuid4().hex}{file_ext}"

    upload_folder = Path(
        current_app.config["UPLOAD_FOLDER"]
    ).expanduser().resolve()
    upload_folder.mkdir(parents=True, exist_ok=True)

    file_path = upload_folder / unique_filename

    file.save(file_path)
    # Save the uploaded recording locally.
    file.save(str(file_path))

    # Keep stored path backend-relative for portability.
    recording_path = str(Path("uploads") / unique_filename)

    session = create_session_record(
        title=title,
        filename=original_filename,
        recording_path=file_path,
        status="uploaded",
        course_id=course_id
    )

    trigger_pipeline(file_path, session["id"])
        recording_path=recording_path,
        status="uploaded"
    )

    # Trigger the processing flow.
    # The internal pipeline is still not my responsibility,
    # but the backend should still provide the entry point for it.
    trigger_pipeline(recording_path, session["id"])

    return success_response("Recording uploaded successfully", session, 201)
