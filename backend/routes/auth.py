"""
Authentication routes.

Handles user registration, login, and token-based identity lookup.
"""

import re
import sqlite3

from flask import Blueprint, request
from werkzeug.security import generate_password_hash, check_password_hash

import jwt

from utils.responses import success_response, error_response
from utils.auth import generate_token, verify_token
from services.user_service import create_user, get_user_by_email, get_user_by_id


auth_bp = Blueprint("auth", __name__)

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LENGTH = 8
MAX_NAME_LENGTH = 100


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user and return a JWT."""
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

    password_hash = generate_password_hash(password)

    try:
        user = create_user(email=email, name=name, password_hash=password_hash)
    except sqlite3.IntegrityError:
        return error_response("Email is already registered", 409)

    token = generate_token(user["id"], user["email"])

    return success_response("User registered successfully", {
        "token": token,
        "user": user,
    }, 201)


@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticate a user and return a JWT."""
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

    safe_user = {k: v for k, v in user.items() if k != "password_hash"}

    return success_response("Login successful", {
        "token": token,
        "user": safe_user,
    })


@auth_bp.route("/me", methods=["GET"])
def me():
    """Return the current user's info from the JWT in the Authorization header."""
    auth_header = request.headers.get("Authorization", "")

    if not auth_header.startswith("Bearer "):
        return error_response("Missing or malformed Authorization header", 401)

    token = auth_header.split(" ", 1)[1]

    try:
        payload = verify_token(token)
    except jwt.ExpiredSignatureError:
        return error_response("Token has expired", 401)
    except jwt.InvalidTokenError:
        return error_response("Invalid token", 401)

    user = get_user_by_id(payload["user_id"])
    if not user:
        return error_response("User not found", 401)

    return success_response("User retrieved successfully", user)
