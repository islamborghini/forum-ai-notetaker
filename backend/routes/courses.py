"""
Course routes.

Handles course membership management endpoints.
"""

import jwt
from flask import Blueprint, request

from services.course_member_service import (
    get_course_member,
    update_course_member_role,
)
from utils.auth import verify_token
from utils.responses import error_response, success_response


courses_bp = Blueprint("courses", __name__)


@courses_bp.route("/<int:course_id>/members/<int:user_id>", methods=["PATCH"])
def update_member_role(course_id: int, user_id: int):
    """
    Update a course member role.

    Only an instructor in the same course can promote a member to TA.
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return error_response("Missing or malformed Authorization header", 401)

    token = auth_header.split(" ", 1)[1]

    try:
        payload = verify_token(token)
    except jwt.ExpiredSignatureError:
        return error_response("Token has expired", 401)
    except jwt.InvalidTokenError:
        return error_response("Invalid token", 401)

    requester_user_id = payload.get("user_id")
    if not requester_user_id:
        return error_response("Invalid token payload", 401)

    requester_member = get_course_member(course_id, requester_user_id)
    if not requester_member:
        return error_response("Requester is not a member of this course", 403)

    if requester_member.get("role") != "instructor":
        return error_response("Only instructors can change member roles", 403)

    data = request.get_json(silent=True)
    if not data:
        return error_response("Request body must be JSON", 400)

    new_role = (data.get("role") or "").strip().lower()
    if new_role != "ta":
        return error_response("Role must be 'ta' for this endpoint", 400)

    target_member = get_course_member(course_id, user_id)
    if not target_member:
        return error_response(
            "Target user is not a member of this course",
            404,
        )

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
