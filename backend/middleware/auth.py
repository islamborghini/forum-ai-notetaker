"""
Authentication middleware.

This decorator protects routes that require a logged-in user.

It extracts the bearer token from the Authorization header,
verifies it using the auth service, and attaches the authenticated
user to Flask's request context (`g.user`).

Protected routes can then rely on `g.user` instead of handling
token parsing or validation themselves.
"""

from functools import wraps
from flask import request, g

from utils.responses import error_response
from services.auth import verify_token


def auth_required(route_function):
    """
    Decorator to enforce authentication on a route.

    Expected request header:
        Authorization: Bearer <token>

    Workflow:
    - Extract token from Authorization header
    - Verify token using auth service
    - Attach authenticated user to `g.user`
    - Allow route execution if valid

    If authentication fails at any step, the request is rejected
    with a 401 Unauthorized response.

    Args:
        route_function: The Flask route function being protected.

    Returns:
        Wrapped route function that enforces authentication.
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

        # Store the authenticated user in Flask's request context.
        # This allows downstream route handlers to access user data
        # without needing to re-verify the token.
        g.user = user

        return route_function(*args, **kwargs)

    return wrapper