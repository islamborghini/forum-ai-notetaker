"""
Session routes.

A session represents one uploaded Forum class recording.

This route file matters because upload is the beginning of the
whole workflow. Once a recording enters here, the backend can
store it, create a session record, and trigger the pipeline.
"""

import uuid
from pathlib import Path
from flask import Blueprint, request, current_app

from utils.responses import success_response, error_response
from utils.validators import allowed_file, safe_filename
from services.session_service import (
    create_session_record,
    fetch_all_sessions,
    fetch_one_session,
)
from pipeline.trigger import trigger_pipeline

sessions_bp = Blueprint("sessions", __name__)


@sessions_bp.route("/", methods=["GET"])
def get_sessions():
    """
    Return all sessions.

    The dashboard uses this route to show all uploaded recordings
    and their current processing status.
    """
    sessions = fetch_all_sessions()
    return success_response("Sessions retrieved successfully", sessions)


@sessions_bp.route("/<int:session_id>", methods=["GET"])
def get_session(session_id: int):
    """
    Return one session by ID.

    This is useful when the frontend wants the details for
    a specific uploaded class recording.
    """
    session = fetch_one_session(session_id)

    if not session:
        return error_response("Session not found", 404)

    return success_response("Session retrieved successfully", session)


@sessions_bp.route("/upload", methods=["POST"])
def upload_session():
    """
    Upload a recording and start the system workflow.

    The backend does four things here:
    1. validates the request
    2. stores the uploaded file
    3. creates a session record
    4. triggers the processing pipeline
    """

    if "file" not in request.files:
        return error_response("No file provided", 400)

    file = request.files["file"]
    title = request.form.get("title", "").strip()

    if file.filename == "":
        return error_response("No file selected", 400)

    if not title:
        return error_response("Title is required", 400)

    if not allowed_file(file.filename):
        return error_response("Unsupported file type", 400)

    # Keep a cleaned version of the original filename for display.
    original_filename = safe_filename(file.filename)

    # Store the actual uploaded file using a unique generated name
    # so two uploads with the same original filename do not overwrite
    # each other.
    file_ext = ""
    if "." in original_filename:
        file_ext = "." + original_filename.rsplit(".", 1)[1].lower()

    unique_filename = f"{uuid.uuid4().hex}{file_ext}"

    upload_folder = Path(
        current_app.config["UPLOAD_FOLDER"]
    ).expanduser().resolve()
    upload_folder.mkdir(parents=True, exist_ok=True)

    file_path = upload_folder / unique_filename

    # Save the uploaded recording locally.
    file.save(str(file_path))

    # Keep stored path backend-relative for portability.
    recording_path = str(Path("uploads") / unique_filename)

    # Create a session record through the service layer.
    # We keep the original cleaned filename in the session metadata
    # for readability, while the stored path uses the unique name.
    session = create_session_record(
        title=title,
        filename=original_filename,
        recording_path=recording_path,
        status="uploaded"
    )

    # Trigger the processing flow.
    # The internal pipeline is still not my responsibility,
    # but the backend should still provide the entry point for it.
    trigger_pipeline(recording_path, session["id"])

    return success_response("Recording uploaded successfully", session, 201)
