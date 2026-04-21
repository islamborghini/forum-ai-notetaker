"""
JWT token utilities.

Handles token generation and verification for user authentication.
"""

import os
from datetime import datetime, timezone, timedelta

import jwt


DEFAULT_SECRET_KEY = "forum-ai-notetaker-local-dev-jwt-secret"
EXPIRY_HOURS = int(os.environ.get("JWT_EXPIRY_HOURS", "24"))


def _get_secret_key() -> str:
    """
    Return the JWT signing key.

    For local/demo environments we allow a built-in fallback so a clean
    checkout can still sign up and log in without extra manual setup.
    Deployments can override this by setting JWT_SECRET_KEY explicitly.
    """
    return os.environ.get("JWT_SECRET_KEY") or DEFAULT_SECRET_KEY


def generate_token(user_id: int, email: str) -> str:
    """
    Create a signed JWT for the given user.

    The token contains the user_id, email, issued-at time,
    and an expiry timestamp.
    """
    now = datetime.now(timezone.utc)
    payload = {
        "user_id": user_id,
        "email": email,
        "iat": now,
        "exp": now + timedelta(hours=EXPIRY_HOURS),
    }
    return jwt.encode(payload, _get_secret_key(), algorithm="HS256")


def verify_token(token: str) -> dict:
    """
    Decode and verify a JWT. Returns the payload dict.

    Raises jwt.ExpiredSignatureError if the token has expired.
    Raises jwt.InvalidTokenError for any other validation failure.
    """
    return jwt.decode(token, _get_secret_key(), algorithms=["HS256"])
