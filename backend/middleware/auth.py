"""
Authentication middleware.

This decorator protects routes that require a logged-in user.

It extracts the bearer token from the Authorization header,
verifies it using the shared auth service, and attaches the
authenticated user to Flask's request context (`g.user`).

All protected routes can then rely on `g.user` instead of
re-parsing the token themselves.
"""

from functools import wraps
from flask import request, g

from utils.responses import error_response
from services.auth import verify_token


def auth_required(route_function):
    """
    Require authentication for a route.

    Expected header:
        Authorization: Bearer <token>

    If the token is valid, the user is stored in `g.user`.
    If not, the request is rejected with a 401 response.
    """
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "").strip()

        if not auth_header:
            return error_response("Missing Authorization header", 401)

        if not auth_header.startswith("Bearer "):
            return error_response("Invalid Authorization header format", 401)

        token = auth_header.split(" ", 1)[1].strip()

        if not token:
            return error_response("Missing token", 401)

        user = verify_token(token)

        if not user:
            return error_response("Invalid or expired token", 401)

        # Attach the authenticated user to the request context
        # so downstream routes can access it easily.
        g.user = user

        return route_function(*args, **kwargs)

    return wrapper