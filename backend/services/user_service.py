"""
User service layer.

This module handles persistence and retrieval of user records for
authentication-related workflows.

It is mainly used by the auth routes to:
- create new users during registration
- look up users by email during login
- retrieve user identity by ID after token verification

Keeping these queries in the service layer helps separate database
logic from route handlers.
"""

from datetime import datetime, timezone
from typing import Optional

from forum_ai_notetaker.db import get_connection


def _row_to_dict(row) -> dict:
    """
    Convert a database row into a plain dictionary.
    """
    return dict(row)


def create_user(
    email: str,
    name: str,
    password_hash: str,
    user_type: str = "student",
) -> dict:
    """
    Create a new user record.

    This function is typically called during registration after the
    password has already been hashed by the auth layer.

    Args:
        email: The user's unique email address.
        name: The user's display name.
        password_hash: The hashed password to store.
        user_type: Global account type, either 'student' or 'professor'.
            Determines which course roles the user can hold.

    Returns:
        A dictionary representing the created user, excluding the
        password hash.

    Raises:
        sqlite3.IntegrityError: If a user with the same email already exists.
    """
    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO users (email, name, password_hash, user_type, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (email, name, password_hash, user_type, now, now),
        )
        conn.commit()

        row = conn.execute(
            """
            SELECT id, email, name, user_type, created_at
            FROM users
            WHERE id = ?
            """,
            (cursor.lastrowid,),
        ).fetchone()

    return _row_to_dict(row)


def get_user_by_email(email: str) -> Optional[dict]:
    """
    Retrieve a user by email address.

    This is mainly used during login, where the auth layer needs the
    stored password hash in order to verify the submitted password.

    Args:
        email: The email address being looked up.

    Returns:
        A user dictionary including the password hash if the user
        exists, otherwise None.
    """
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT id, email, name, password_hash, user_type, created_at
            FROM users
            WHERE email = ?
            """,
            (email,),
        ).fetchone()

    return _row_to_dict(row) if row else None


def get_user_by_id(user_id: int) -> Optional[dict]:
    """
    Retrieve a user by ID.

    This is commonly used after token verification, when the backend
    needs to load the authenticated user's identity without exposing
    the password hash.

    Args:
        user_id: The ID of the user being requested.

    Returns:
        A user dictionary without the password hash if the user exists,
        otherwise None.
    """
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT id, email, name, user_type, created_at
            FROM users
            WHERE id = ?
            """,
            (user_id,),
        ).fetchone()

    return _row_to_dict(row) if row else None