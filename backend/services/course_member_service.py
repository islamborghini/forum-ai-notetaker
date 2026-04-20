"""
Course member service layer.

This module handles persistence and retrieval of course membership
records.

A course_members row links a user to a course and stores the role
they hold in that course, such as student, TA, or professor. Keeping
this logic in the service layer allows routes to enforce access and
role-based permissions without working with SQL directly.
"""

import sqlite3
from datetime import datetime, timezone
from typing import Optional

from forum_ai_notetaker.db import get_connection


def get_course_member(course_id: int, user_id: int) -> Optional[dict]:
    """
    Retrieve a single course membership record.

    This is typically used for access-control checks, such as
    determining whether a user belongs to a course and what role
    they hold within it.

    Args:
        course_id: The course being checked.
        user_id: The user being checked.

    Returns:
        A membership dictionary if a matching row exists,
        otherwise None.
    """
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT *
            FROM course_members
            WHERE course_id = ? AND user_id = ?
            """,
            (course_id, user_id),
        ).fetchone()

    return dict(row) if row else None


def create_course_member(
    course_id: int,
    user_id: int,
    role: str = "student",
) -> Optional[dict]:
    """
    Create a new course membership record.

    This is used when a user joins a course or is added to it
    directly. New members default to the student role unless a
    different role is explicitly provided.

    Args:
        course_id: The course the user is joining.
        user_id: The user being added to the course.
        role: The membership role to assign.

    Returns:
        The created membership dictionary if insertion succeeds,
        otherwise None if the membership already exists.
    """
    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as conn:
        try:
            cursor = conn.execute(
                """
                INSERT INTO course_members (course_id, user_id, role, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (course_id, user_id, role, now, now),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            return None

        row = conn.execute(
            """
            SELECT *
            FROM course_members
            WHERE id = ?
            """,
            (cursor.lastrowid,),
        ).fetchone()

    return dict(row) if row else None


def update_course_member_role(course_id: int, user_id: int, role: str) -> bool:
    """
    Update the role of an existing course member.

    This is useful for workflows such as promoting a student to TA
    or changing a member's permissions within a course.

    Args:
        course_id: The course where the role is being changed.
        user_id: The user whose role is being updated.
        role: The new role to assign.

    Returns:
        True if a row was updated, otherwise False.
    """
    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as conn:
        cursor = conn.execute(
            """
            UPDATE course_members
            SET role = ?, updated_at = ?
            WHERE course_id = ? AND user_id = ?
            """,
            (role, now, course_id, user_id),
        )
        conn.commit()

    return cursor.rowcount > 0


def is_course_member(course_id: int, user_id: int) -> bool:
    """
    Check whether a user belongs to a course.

    Args:
        course_id: The course being checked.
        user_id: The user being checked.

    Returns:
        True if the user is a member of the course, otherwise False.
    """
    return get_course_member(course_id, user_id) is not None


def get_course_member_role(course_id: int, user_id: int) -> Optional[str]:
    """
    Return the role a user holds in a course.

    Args:
        course_id: The course being checked.
        user_id: The user being checked.

    Returns:
        The role string if the user is a member, otherwise None.
    """
    member = get_course_member(course_id, user_id)
    return member["role"] if member else None


def is_professor(course_id: int, user_id: int) -> bool:
    """
    Check whether a user is the professor of a course.

    Args:
        course_id: The course being checked.
        user_id: The user being checked.

    Returns:
        True if the user is the professor, otherwise False.
    """
    return get_course_member_role(course_id, user_id) == "instructor"


def is_ta_or_professor(course_id: int, user_id: int) -> bool:
    """
    Check whether a user has elevated course permissions.

    This helper is mainly used for actions like uploading recordings,
    where only instructional roles should be allowed.
    Professor = Instructor, TA = Teaching Assistant, both have elevated permissions compared to students.

    Args:
        course_id: The course being checked.
        user_id: The user being checked.

    Returns:
        True if the user is a TA or professor, otherwise False.
    """
    return get_course_member_role(course_id, user_id) in {"ta", "instructor"}