"""
Authentication service.

This module connects the middleware to the existing JWT-based
authentication system used by /api/auth routes.

It verifies bearer tokens and resolves the corresponding user
from the database so protected routes can rely on `g.user`.
"""

from typing import Optional
import jwt

from utils.auth import verify_token as decode_jwt
from services.user_service import get_user_by_id


def verify_token(token: str) -> Optional[dict]:
    """
    Verify a JWT and return the authenticated user.

    The token is decoded using the shared JWT utility. If valid,
    the corresponding user is loaded from the database.

    Args:
        token: Bearer token from the Authorization header.

    Returns:
        A user dictionary if valid, otherwise None.
    """
    try:
        payload = decode_jwt(token)
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

    user_id = payload.get("user_id")
    if not user_id:
        return None

    return get_user_by_id(user_id)