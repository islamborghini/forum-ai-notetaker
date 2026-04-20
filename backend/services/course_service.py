"""
Course service layer.

Provides data access helpers for courses and course membership.

This module is responsible for:
- creating courses
- managing course membership
- enforcing role-based access checks
- retrieving course-related data such as sessions and members
"""

from __future__ import annotations

import random
import string
from datetime import datetime, timezone
from typing import Optional

from forum_ai_notetaker.db import get_connection
from services.course_member_service import (
    create_course_member,
    get_course_member,
)


def _row_to_dict(row) -> dict:
    """Convert a database row to a dictionary."""
    return dict(row)


def _generate_invite_code(length: int = 6) -> str:
    """Generate a random alphanumeric invite code."""
    alphabet = string.ascii_uppercase + string.digits
    return "".join(random.choices(alphabet, k=length))


def _generate_unique_invite_code() -> str:
    """
    Generate a unique invite code that does not already exist.
    """
    while True:
        invite_code = _generate_invite_code()
        if not get_course_by_invite_code(invite_code):
            return invite_code


def create_course(name: str, creator_user_id: int) -> dict:
    """
    Create a new course and assign the creator as instructor.

    Args:
        name: The name of the course.
        creator_user_id: The user creating the course.

    Returns:
        The created course dictionary.
    """
    now = datetime.now(timezone.utc).isoformat()
    invite_code = _generate_unique_invite_code()

    with get_connection() as conn:
        try:
            cursor = conn.execute(
                """
                INSERT INTO courses (name, invite_code, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                (name, invite_code, now, now),
            )
            course_id = cursor.lastrowid

            conn.execute(
                """
                INSERT INTO course_members (course_id, user_id, role, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (course_id, creator_user_id, "instructor", now, now),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise

        row = conn.execute(
            "SELECT * FROM courses WHERE id = ?",
            (course_id,),
        ).fetchone()

    return _row_to_dict(row)


def get_course_by_id(course_id: int) -> Optional[dict]:
    """
    Retrieve a course by its ID.
    """
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM courses WHERE id = ?",
            (course_id,),
        ).fetchone()

    return _row_to_dict(row) if row else None


def get_course_by_invite_code(invite_code: str) -> Optional[dict]:
    """
    Retrieve a course using its invite code.
    """
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM courses WHERE invite_code = ?",
            (invite_code,),
        ).fetchone()

    return _row_to_dict(row) if row else None


def get_courses_for_user(user_id: int) -> list[dict]:
    """
    Return all courses a user is enrolled in.

    Includes the user's role in each course.
    """
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT c.id, c.name, c.created_at, c.updated_at, cm.role
            FROM courses c
            INNER JOIN course_members cm ON cm.course_id = c.id
            WHERE cm.user_id = ?
            ORDER BY c.created_at DESC
            """,
            (user_id,),
        ).fetchall()

    return [_row_to_dict(row) for row in rows]


def get_course_members(course_id: int) -> list[dict]:
    """
    Return all members of a course, including user details.

    Members are ordered by role priority:
    instructor → ta → student.
    """
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                cm.id,
                cm.course_id,
                cm.user_id,
                cm.role,
                cm.created_at,
                cm.updated_at,
                u.name,
                u.email
            FROM course_members cm
            INNER JOIN users u ON u.id = cm.user_id
            WHERE cm.course_id = ?
            ORDER BY
                CASE cm.role
                    WHEN 'instructor' THEN 0
                    WHEN 'ta' THEN 1
                    ELSE 2
                END,
                u.name ASC
            """,
            (course_id,),
        ).fetchall()

    return [_row_to_dict(row) for row in rows]


def is_course_member(course_id: int, user_id: int) -> bool:
    """
    Check whether a user belongs to a course.
    """
    return get_course_member(course_id, user_id) is not None


def is_instructor(course_id: int, user_id: int) -> bool:
    """
    Check whether a user is the instructor of a course.
    """
    member = get_course_member(course_id, user_id)
    return member is not None and member.get("role") == "instructor"


def is_ta_or_professor(course_id: int, user_id: int) -> bool:
    """
    Check whether a user has elevated permissions.

    Returns True for instructor or TA roles.
    """
    member = get_course_member(course_id, user_id)
    if not member:
        return False

    return member.get("role") in ("instructor", "ta")


def get_course_sessions(course_id: int) -> list[dict]:
    """
    Return all sessions belonging to a course.
    """
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM sessions
            WHERE course_id = ?
            ORDER BY created_at DESC
            """,
            (course_id,),
        ).fetchall()

    return [_row_to_dict(row) for row in rows]


def join_course_by_invite_code(invite_code: str, user: dict) -> Optional[dict]:
    """
    Join a course as a student using an invite code.

    Returns:
        dict with course and membership on success,
        None if the course is not found,
        {"error": "already_member"} if already enrolled.
    """
    course = get_course_by_invite_code(invite_code)
    if not course:
        return None

    existing_member = get_course_member(course["id"], user["id"])
    if existing_member:
        return {"error": "already_member"}

    membership = create_course_member(course["id"], user["id"], "student")
    if not membership:
        return {"error": "already_member"}

    return {
        "course": course,
        "membership": membership,
    }