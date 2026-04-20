"""
Session routes.

A session represents one uploaded course recording.

This module defines endpoints for:
- listing sessions visible to the authenticated user
- retrieving a specific session by ID
- uploading a new recording and triggering processing
- searching sessions by title, transcript content, and notes

Because sessions are course-scoped resources, access checks are
performed before session data is returned. This ensures that users
only see sessions belonging to courses they are enrolled in.
"""

import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from flask import Blueprint, current_app, g, request

from middleware.auth import auth_required
from pipeline.trigger import run_pipeline_async
from services.course_service import get_course_by_id, is_course_member, is_ta_or_professor
from services.search_service import search
from services.session_service import (
    create_session_record,
    fetch_one_session,
    fetch_sessions_for_user,
)
from utils.responses import error_response, success_response
from utils.validators import allowed_file, safe_filename

executor = ThreadPoolExecutor(max_workers=2)

sessions_bp = Blueprint("sessions", __name__)


@sessions_bp.route("/", methods=["GET"])
@auth_required
def get_sessions():
    """
    Return all sessions visible to the authenticated user.

    Results are limited to sessions belonging to courses
    the user is a member of.
    """
    sessions = fetch_sessions_for_user(g.user["id"])
    return success_response("Sessions retrieved successfully", sessions)


@sessions_bp.route("/search", methods=["GET"])
@auth_required
def search_sessions():
    """
    Search sessions by title, transcript content, and notes.

    Results are filtered to the authenticated user's courses and
    enriched with match metadata and snippets.

    Query parameters:
        q — the search string (required, max 200 characters)

    Returns 400 if q is missing, empty, or too long.
    Returns 200 with a list of enriched matching sessions.

    Example:
        GET /api/sessions/search?q=memory+management
    """
    query = request.args.get("q", "").strip()

    if not query:
        return error_response("Search query parameter 'q' is required", 400)

    try:
        results = search(query, g.user["id"])
    except ValueError as exc:
        return error_response(str(exc), 400)

    return success_response("Search results retrieved successfully", results)


@sessions_bp.route("/<int:session_id>", methods=["GET"])
@auth_required
def get_session(session_id: int):
    """
    Return one session by ID if the user is authorized to view it.

    Returns 404 if the session does not exist.
    Returns 403 if the user is not a member of the session's course.
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
    Upload a recording and trigger the processing pipeline.

    This route performs four main steps:
    1. validates the incoming request
    2. checks that the user has upload permission for the course
    3. stores the uploaded recording with a unique filename
    4. creates a session record and starts processing

    IMPORTANT: This endpoint returns IMMEDIATELY (non-blocking).
    The pipeline runs in a background thread. The response includes
    the session_id, which can be used to poll the session status
    as the pipeline processes.

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
    print(f"[UPLOAD] Request received from user {g.user['id']}")
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
        return error_response("Only a TA or instructor can upload to this course", 403)

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

    stored_path = str(Path("uploads") / unique_filename)

    session = create_session_record(
        title=title,
        original_filename=original_filename,
        stored_path=stored_path,
        status="uploaded",
        course_id=course_id,
    )

    print(f"[UPLOAD] File saved for session {session['id']}: {original_filename}")
    print(f"[UPLOAD] Starting background pipeline thread for session {session['id']}...")

    app = current_app._get_current_object()
    executor.submit(run_pipeline_async, stored_path, session["id"], app)

    print(f"[UPLOAD] Background thread started. Returning response immediately.")
    print(f"[UPLOAD] Session {session['id']} status will update as pipeline progresses")

    return success_response("Recording uploaded successfully", session, 201)