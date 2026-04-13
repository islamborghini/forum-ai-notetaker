"""
Course service.

Handles:
- creating courses
- invite codes
- membership
- role checks (student / TA / professor)

Currently uses in-memory storage so routes can be tested
before DB integration.
"""

import random
import string
from typing import Optional

COURSES = []
COURSE_MEMBERS = []
NEXT_COURSE_ID = 1


def generate_invite_code(length: int = 6) -> str:
    """
    Generate a short invite code (e.g. AB12CD).
    """
    alphabet = string.ascii_uppercase + string.digits
    return "".join(random.choices(alphabet, k=length))


def create_course(name: str, creator: dict) -> dict:
    """
    Create a course and assign creator as professor.
    """
    global NEXT_COURSE_ID

    course = {
        "id": NEXT_COURSE_ID,
        "name": name,
        "invite_code": generate_invite_code(),
        "creator_id": creator["id"],
    }

    COURSES.append(course)

    COURSE_MEMBERS.append({
        "course_id": NEXT_COURSE_ID,
        "user_id": creator["id"],
        "role": "professor",
    })

    NEXT_COURSE_ID += 1
    return course


def get_course_by_id(course_id: int) -> Optional[dict]:
    return next((c for c in COURSES if c["id"] == course_id), None)


def get_course_by_invite_code(invite_code: str) -> Optional[dict]:
    return next((c for c in COURSES if c["invite_code"] == invite_code), None)


def get_courses_for_user(user_id: int) -> list[dict]:
    course_ids = {
        m["course_id"]
        for m in COURSE_MEMBERS
        if m["user_id"] == user_id
    }
    return [c for c in COURSES if c["id"] in course_ids]


def get_course_members(course_id: int) -> list[dict]:
    return [m for m in COURSE_MEMBERS if m["course_id"] == course_id]


def get_membership(course_id: int, user_id: int) -> Optional[dict]:
    return next(
        (m for m in COURSE_MEMBERS if m["course_id"] == course_id and m["user_id"] == user_id),
        None,
    )


def is_course_member(course_id: int, user_id: int) -> bool:
    return get_membership(course_id, user_id) is not None


def is_professor(course_id: int, user_id: int) -> bool:
    m = get_membership(course_id, user_id)
    return m is not None and m["role"] == "professor"


def is_ta_or_professor(course_id: int, user_id: int) -> bool:
    m = get_membership(course_id, user_id)
    return m is not None and m["role"] in {"ta", "professor"}


def join_course_by_invite_code(invite_code: str, user: dict):
    """
    Join a course as a student.
    """
    course = get_course_by_invite_code(invite_code)
    if not course:
        return None

    existing = get_membership(course["id"], user["id"])
    if existing:
        return existing

    membership = {
        "course_id": course["id"],
        "user_id": user["id"],
        "role": "student",
    }

    COURSE_MEMBERS.append(membership)
    return membership


def promote_member_to_ta(course_id: int, user_id: int):
    """
    Promote student → TA.
    """
    m = get_membership(course_id, user_id)
    if not m:
        return None

    m["role"] = "ta"
    return m