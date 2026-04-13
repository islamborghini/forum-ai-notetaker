"""
User service layer.

Connects the auth routes to the SQLite database.
"""

from datetime import datetime, timezone
from typing import Optional

from forum_ai_notetaker.db import get_connection


def _row_to_dict(row) -> dict:
    return dict(row)


def create_user(email: str, name: str, password_hash: str) -> dict:
    """
    Insert a new user. Returns dict without password_hash.
    Raises sqlite3.IntegrityError if email already exists.
    """
    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO users (email, name, password_hash, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (email, name, password_hash, now, now),
        )
        conn.commit()
        row = conn.execute(
            "SELECT id, email, name, created_at FROM users WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()
    return _row_to_dict(row)


def get_user_by_email(email: str) -> Optional[dict]:
    """
    Returns user dict including password_hash (needed for login verification).
    Returns None if no user with that email.
    """
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, email, name, password_hash, created_at FROM users WHERE email = ?",
            (email,),
        ).fetchone()
    return _row_to_dict(row) if row else None


def get_user_by_id(user_id: int) -> Optional[dict]:
    """
    Returns user dict without password_hash.
    Returns None if no user with that id.
    """
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, email, name, created_at FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    return _row_to_dict(row) if row else None
