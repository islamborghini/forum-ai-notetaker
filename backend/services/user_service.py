"""
User service layer — stub.

This file defines the interface that auth routes depend on.
Replace with real SQLite implementation when ready.
"""

from typing import Optional


def create_user(email: str, name: str, password_hash: str) -> dict:
    """
    Insert a new user. Returns dict with keys: id, email, name, created_at.
    Raises sqlite3.IntegrityError if email already exists.
    """
    raise NotImplementedError("user_service.create_user not implemented yet")


def get_user_by_email(email: str) -> Optional[dict]:
    """
    Returns dict with keys: id, email, name, password_hash, created_at.
    Returns None if no user with that email.
    """
    raise NotImplementedError("user_service.get_user_by_email not implemented yet")


def get_user_by_id(user_id: int) -> Optional[dict]:
    """
    Returns dict with keys: id, email, name, created_at.
    Does NOT return password_hash.
    Returns None if no user with that id.
    """
    raise NotImplementedError("user_service.get_user_by_id not implemented yet")
