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
    is_instructor,
    join_course_by_invite_code,
)
from services.course_member_service import get_course_member, update_course_member_role
from utils.responses import error_response, success_response


courses_bp = Blueprint("courses", __name__)


@courses_bp.route("/", methods=["POST"])
@auth_required
def create_new_course():
    """
    Create a course.

    Expected JSON:
    {
        "name": "..."
    }
    """
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()

    if not name:
        return error_response("Course name is required", 400)

    course = create_course(name, g.user["id"])
    return success_response("Course created", course, 201)


@courses_bp.route("/", methods=["GET"])
@auth_required
def list_my_courses():
    """
    Get all courses for the authenticated user.
    """
    courses = get_courses_for_user(g.user["id"])
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

    result = join_course_by_invite_code(
        invite_code,
        {"id": g.user["id"]},
    )

    if not result:
        return error_response("Invalid invite code", 404)

    if result.get("error") == "already_member":
        return error_response("User is already a member of this course", 409)

    return success_response("Joined course successfully", result, 201)


@courses_bp.route("/<int:course_id>", methods=["GET"])
@auth_required
def get_course_details(course_id: int):
    """
    Get course info and members.

    Invite code is only returned if that user is the instructor.
    """
    course = get_course_by_id(course_id)

    if not course:
        return error_response("Course not found", 404)

    if not is_course_member(course_id, g.user["id"]):
        return error_response("Access denied", 403)

    data = {
        "id": course["id"],
        "name": course["name"],
        "members": get_course_members(course_id),
    }

    if is_instructor(course_id, g.user["id"]):
        data["invite_code"] = course["invite_code"]

    return success_response("Course retrieved", data)


@courses_bp.route("/<int:course_id>/promote-ta", methods=["POST"])
@auth_required
def promote_to_ta(course_id: int):
    """
    Promote a student to TA.

    Expected JSON:
    {
        "user_id": 2
    }
    """
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")

    if user_id is None:
        return error_response("user_id required", 400)

    try:
        user_id = int(user_id)
    except ValueError:
        return error_response("user_id must be int", 400)

    if not is_instructor(course_id, g.user["id"]):
        return error_response("Only instructors can promote", 403)

    membership = get_course_member(course_id, user_id)
    if not membership:
        return error_response("User not in course", 404)

    updated = update_course_member_role(course_id, user_id, "ta")
    if not updated:
        return error_response("No role update was applied", 400)

    membership = get_course_member(course_id, user_id)
    return success_response("Promoted to TA", membership)


@courses_bp.route("/<int:course_id>/members/<int:user_id>", methods=["PATCH"])
@auth_required
def update_member_role(course_id: int, user_id: int):
    """
    Update a course member role.

    Only an instructor in the same course can promote a member to TA.
    """
    if not is_course_member(course_id, g.user["id"]):
        return error_response("Requester is not a member of this course", 403)

    if not is_instructor(course_id, g.user["id"]):
        return error_response("Only instructors can change member roles", 403)

    data = request.get_json(silent=True)
    if data is None:
        return error_response("Request body must be JSON", 400)

    new_role = (data.get("role") or "").strip().lower()
    if new_role != "ta":
        return error_response("Role must be 'ta' for this endpoint", 400)

    target_member = get_course_member(course_id, user_id)
    if not target_member:
        return error_response("Target user is not a member of this course", 404)

    updated = update_course_member_role(course_id, user_id, new_role)
    if not updated:
        return error_response("No role update was applied", 400)

    return success_response(
        "Member role updated successfully",
        {
            "course_id": course_id,
            "user_id": user_id,
            "role": new_role,
        },
        200,
    )
