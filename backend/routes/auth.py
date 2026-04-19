"""
Authentication routes.

This module handles user registration, login, and token-based identity
lookup.

These routes form the public authentication API of the backend:
- /register creates a new user account
- /login verifies credentials and issues a JWT
- /me returns the authenticated user's identity using shared auth middleware
"""

import re
import sqlite3

from flask import Blueprint, request, g
from werkzeug.security import generate_password_hash, check_password_hash

from middleware.auth import auth_required
from utils.responses import success_response, error_response
from utils.auth import generate_token
from services.user_service import create_user, get_user_by_email


auth_bp = Blueprint("auth", __name__)

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LENGTH = 8
MAX_NAME_LENGTH = 100


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Register a new user and return an authentication token.

    This route validates the request body, hashes the submitted password,
    creates the user record, and immediately returns a JWT so the user
    can begin authenticated requests without a separate login step.

    Returns:
        A success response containing the JWT and user record,
        or an error response if validation fails or the email
        is already registered.
    """
    data = request.get_json(silent=True)
    if not data:
        return error_response("Request body must be JSON", 400)

    email = (data.get("email") or "").strip().lower()
    name = (data.get("name") or "").strip()
    password = data.get("password") or ""

    errors = []
    if not email or not EMAIL_REGEX.match(email):
        errors.append("A valid email is required")
    if not name or len(name) > MAX_NAME_LENGTH:
        errors.append(f"Name is required and must be under {MAX_NAME_LENGTH} characters")
    if len(password) < MIN_PASSWORD_LENGTH:
        errors.append(f"Password must be at least {MIN_PASSWORD_LENGTH} characters")

    if errors:
        return error_response("; ".join(errors), 400)

    password_hash = generate_password_hash(password, method="pbkdf2:sha256")

    try:
        user = create_user(email=email, name=name, password_hash=password_hash)
    except sqlite3.IntegrityError:
        return error_response("Email is already registered", 409)

    token = generate_token(user["id"], user["email"])

    return success_response(
        "User registered successfully",
        {
            "token": token,
            "user": user,
        },
        201,
    )


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Authenticate a user and return a JWT.

    This route verifies the submitted credentials against the stored
    user record. If authentication succeeds, it returns a new token
    along with a safe user object that excludes the password hash.

    Returns:
        A success response containing the JWT and user record,
        or an error response if the credentials are invalid.
    """
    data = request.get_json(silent=True)
    if not data:
        return error_response("Request body must be JSON", 400)

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return error_response("Email and password are required", 400)

    user = get_user_by_email(email)
    if not user or not check_password_hash(user["password_hash"], password):
        return error_response("Invalid credentials", 401)

    token = generate_token(user["id"], user["email"])

    safe_user = {key: value for key, value in user.items() if key != "password_hash"}

    return success_response(
        "Login successful",
        {
            "token": token,
            "user": safe_user,
        },
    )


@auth_bp.route("/me", methods=["GET"])
@auth_required
def me():
    """
    Return the current authenticated user's identity.

    This route relies on the authentication middleware to:
    - validate the JWT
    - attach the authenticated user to `g.user`

    This keeps authentication behavior consistent across all protected
    routes and avoids duplicating token-parsing logic here.

    Returns:
        A success response containing the authenticated user's data.
    """
    return success_response("User retrieved successfully", g.user)