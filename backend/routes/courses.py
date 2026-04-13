"""
Course routes.

Handles:
- create course
- join course
- list courses
- course details
- promote TA
- update member roles
"""

from flask import Blueprint, g, request

from middleware.auth import auth_required
from services.course_service import (
    create_course,
    get_course_by_id,
    get_course_members,
    get_courses_for_user,
    is_course_member,
    is_professor,
    join_course_by_invite_code,
    promote_member_to_ta,
)
from utils.responses import error_response, success_response


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

    Since auth middleware is not part of this flow yet, the user is supplied
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
@auth_required
def join_course():
    """
    Join a course using an invite code.

    The authenticated user is added as a student.
    """
    data = request.get_json(silent=True)
    if data is None:
        return error_response("Request body must be JSON", 400)

    invite_code = (data.get("invite_code") or "").strip().upper()
    if not invite_code:
        return error_response("Invite code required", 400)

    membership = join_course_by_invite_code(
        invite_code,
        {"id": g.user["id"]},
    )

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

    Since auth middleware is not part of this flow yet, the acting professor
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


@courses_bp.route("/<int:course_id>/members/<int:user_id>", methods=["PATCH"])
@auth_required
def update_member_role(course_id: int, user_id: int):
    """
    Update a course member role.

    Only a professor in the same course can promote a member to TA.
    """
    if not is_course_member(course_id, g.user["id"]):
        return error_response("Requester is not a member of this course", 403)

    if not is_professor(course_id, g.user["id"]):
        return error_response("Only professors can change member roles", 403)

    data = request.get_json(silent=True)
    if data is None:
        return error_response("Request body must be JSON", 400)

    new_role = (data.get("role") or "").strip().lower()
    if new_role != "ta":
        return error_response("Role must be 'ta' for this endpoint", 400)

    target_member = promote_member_to_ta(course_id, user_id)
    if not target_member:
        return error_response("Target user is not a member of this course", 404)

    return success_response(
        "Member role updated successfully",
        {
            "course_id": course_id,
            "user_id": user_id,
            "role": target_member["role"],
        },
        200,
    )
