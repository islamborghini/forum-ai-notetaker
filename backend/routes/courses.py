"""
Course routes.

Handles:
- create course
- join course
- list courses
- course details
- promote TA

This file is intentionally scoped to course creation and membership.
Authentication and course-scoped session access are handled in
separate work so this PR can remain mergeable on its own.
"""

from flask import Blueprint, request

from utils.responses import success_response, error_response
from services.course_service import (
    create_course,
    get_courses_for_user,
    get_course_by_id,
    get_course_members,
    is_professor,
    is_course_member,
    join_course_by_invite_code,
    promote_member_to_ta,
)

courses_bp = Blueprint("courses", __name__)


@courses_bp.route("/", methods=["POST"])
def create_new_course():
    """
    Create a course.

    For now, this route expects the creator information to be provided
    in the request body so the course flow can be developed without
    depending on the separate auth middleware PR.

    Expected JSON:
    {
        "name": "...",
        "creator": {
            "id": 1,
            "name": "...",
            "email": "..."
        }
    }
    """
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    creator = data.get("creator")

    if not name:
        return error_response("Course name is required", 400)

    if not creator or "id" not in creator:
        return error_response("creator with id is required", 400)

    course = create_course(name, creator)
    return success_response("Course created", course, 201)


@courses_bp.route("/", methods=["GET"])
def list_my_courses():
    """
    Get all courses for a given user.

    Since auth middleware is not part of this PR, the user is supplied
    through a query parameter for now:

        GET /api/courses?user_id=1
    """
    user_id_raw = request.args.get("user_id", "").strip()

    if not user_id_raw:
        return error_response("user_id is required", 400)

    try:
        user_id = int(user_id_raw)
    except ValueError:
        return error_response("user_id must be int", 400)

    courses = get_courses_for_user(user_id)
    return success_response("Courses retrieved", courses)


@courses_bp.route("/join", methods=["POST"])
def join_course():
    """
    Join a course using an invite code.

    Since auth middleware is not part of this PR, the joining user is
    provided in the request body.

    Expected JSON:
    {
        "invite_code": "...",
        "user": {
            "id": 2,
            "name": "...",
            "email": "..."
        }
    }
    """
    data = request.get_json(silent=True) or {}
    invite_code = data.get("invite_code", "").strip().upper()
    user = data.get("user")

    if not invite_code:
        return error_response("Invite code required", 400)

    if not user or "id" not in user:
        return error_response("user with id is required", 400)

    membership = join_course_by_invite_code(invite_code, user)

    if not membership:
        return error_response("Invalid invite code", 404)

    return success_response("Joined course", membership, 201)


@courses_bp.route("/<int:course_id>", methods=["GET"])
def get_course_details(course_id: int):
    """
    Get course info and members.

    Access is checked using a user_id query parameter for now:

        GET /api/courses/<course_id>?user_id=1

    Invite code is only returned if that user is the professor.
    """
    user_id_raw = request.args.get("user_id", "").strip()

    if not user_id_raw:
        return error_response("user_id is required", 400)

    try:
        user_id = int(user_id_raw)
    except ValueError:
        return error_response("user_id must be int", 400)

    course = get_course_by_id(course_id)

    if not course:
        return error_response("Course not found", 404)

    if not is_course_member(course_id, user_id):
        return error_response("Access denied", 403)

    data = {
        "id": course["id"],
        "name": course["name"],
        "members": get_course_members(course_id),
    }

    if is_professor(course_id, user_id):
        data["invite_code"] = course["invite_code"]

    return success_response("Course retrieved", data)


@courses_bp.route("/<int:course_id>/promote-ta", methods=["POST"])
def promote_to_ta(course_id: int):
    """
    Promote a student to TA.

    Since auth middleware is not part of this PR, the acting professor
    is identified through `actor_user_id` in the request body.

    Expected JSON:
    {
        "actor_user_id": 1,
        "user_id": 2
    }
    """
    data = request.get_json(silent=True) or {}
    actor_user_id = data.get("actor_user_id")
    user_id = data.get("user_id")

    if actor_user_id is None:
        return error_response("actor_user_id required", 400)

    if user_id is None:
        return error_response("user_id required", 400)

    try:
        actor_user_id = int(actor_user_id)
        user_id = int(user_id)
    except ValueError:
        return error_response("actor_user_id and user_id must be int", 400)

    if not is_professor(course_id, actor_user_id):
        return error_response("Only professor can promote", 403)

    membership = promote_member_to_ta(course_id, user_id)

    if not membership:
        return error_response("User not in course", 404)

    return success_response("Promoted to TA", membership)