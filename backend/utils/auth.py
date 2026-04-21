"""
JWT token utilities.

Handles token generation and verification for user authentication.
"""

import os
from datetime import datetime, timezone, timedelta
import jwt

# Fallback ensures auth works even if .env is missing (dev only)
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-secret-key")
EXPIRY_HOURS = int(os.environ.get("JWT_EXPIRY_HOURS", "24"))


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
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def verify_token(token: str) -> dict:
    """
    Decode and verify a JWT. Returns the payload dict.

    Raises jwt.ExpiredSignatureError if the token has expired.
    Raises jwt.InvalidTokenError for any other validation failure.
    """
    return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])