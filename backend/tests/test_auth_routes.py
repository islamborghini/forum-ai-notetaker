"""
Tests for authentication routes.

This module sets up an isolated Flask app and temporary database for
auth route tests covering registration, login, and token-protected
identity lookup.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

# The JWT utility reads its secret at import time, so set a stable test
# secret before importing the auth blueprint and helpers.
os.environ["JWT_SECRET_KEY"] = "test-secret-key"

from flask import Flask

from forum_ai_notetaker import db
from routes.auth import auth_bp


class AuthRouteTests(unittest.TestCase):
    """Shared scaffold for auth route tests."""

    def setUp(self):
        """
        Build an isolated app and temporary database for each test.

        The app registers only the auth blueprint so these tests stay
        focused on authentication behavior.
        """
        self.tempdir = tempfile.TemporaryDirectory()
        self.original_db_path = db.DEFAULT_DB_PATH
        db.DEFAULT_DB_PATH = Path(self.tempdir.name) / "test.sqlite3"
        db.init_db()

        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.register_blueprint(auth_bp, url_prefix="/api/auth")
        self.client = self.app.test_client()

    def tearDown(self):
        """Restore the original database path and remove temp files."""
        db.DEFAULT_DB_PATH = self.original_db_path
        self.tempdir.cleanup()

    def post_json(self, path, payload):
        """Send a JSON POST request to an auth route."""
        return self.client.post(path, json=payload)

    def get_with_token(self, path, token):
        """Send a GET request with a bearer token."""
        return self.client.get(
            path,
            headers={"Authorization": f"Bearer {token}"},
        )

    def seed_user(
        self,
        *,
        email="student@example.com",
        name="Student",
        password="strongpass123",
        user_type="student",
    ):
        """Insert a user row with a properly hashed password for login tests."""
        password_hash = generate_password_hash(password, method="pbkdf2:sha256")

        with db.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO users (email, name, password_hash, user_type, created_at, updated_at)
                VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))
                """,
                (email, name, password_hash, user_type),
            )
            conn.commit()

    def test_register_creates_user_and_returns_token(self):
        """
        A valid registration should create the user and issue a token.

        The stored password should be hashed rather than persisted in
        plain text.
        """
        response = self.post_json(
            "/api/auth/register",
            {
                "email": "newstudent@example.com",
                "name": "New Student",
                "password": "strongpass123",
                "user_type": "student",
            },
        )

        self.assertEqual(response.status_code, 201)

        payload = response.get_json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["message"], "User registered successfully")
        self.assertIn("token", payload["data"])

        user = payload["data"]["user"]
        self.assertEqual(user["email"], "newstudent@example.com")
        self.assertEqual(user["name"], "New Student")
        self.assertEqual(user["user_type"], "student")

        with db.get_connection() as conn:
            row = conn.execute(
                """
                SELECT email, name, user_type, password_hash
                FROM users
                WHERE email = ?
                """,
                ("newstudent@example.com",),
            ).fetchone()

        self.assertIsNotNone(row)
        self.assertEqual(row["email"], "newstudent@example.com")
        self.assertEqual(row["name"], "New Student")
        self.assertEqual(row["user_type"], "student")
        self.assertNotEqual(row["password_hash"], "strongpass123")
        self.assertTrue(check_password_hash(row["password_hash"], "strongpass123"))

    def test_register_requires_json_body(self):
        """Reject registration requests that do not send JSON."""
        response = self.client.post("/api/auth/register")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "Request body must be JSON")

    def test_register_rejects_invalid_email(self):
        """Reject registration when the email address is invalid."""
        response = self.post_json(
            "/api/auth/register",
            {
                "email": "not-an-email",
                "name": "New Student",
                "password": "strongpass123",
                "user_type": "student",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("A valid email is required", response.get_json()["error"])

    def test_register_rejects_blank_name(self):
        """Reject registration when the name is empty."""
        response = self.post_json(
            "/api/auth/register",
            {
                "email": "newstudent@example.com",
                "name": "",
                "password": "strongpass123",
                "user_type": "student",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "Name is required and must be under 100 characters",
            response.get_json()["error"],
        )

    def test_register_rejects_short_password(self):
        """Reject registration when the password is shorter than the minimum."""
        response = self.post_json(
            "/api/auth/register",
            {
                "email": "newstudent@example.com",
                "name": "New Student",
                "password": "short",
                "user_type": "student",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "Password must be at least 8 characters",
            response.get_json()["error"],
        )

    def test_register_rejects_invalid_user_type(self):
        """Reject registration when the account type is unsupported."""
        response = self.post_json(
            "/api/auth/register",
            {
                "email": "newstudent@example.com",
                "name": "New Student",
                "password": "strongpass123",
                "user_type": "admin",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "Account type must be 'student' or 'professor'",
            response.get_json()["error"],
        )

    def test_register_rejects_duplicate_email(self):
        """Reject registration when the email is already registered."""
        self.post_json(
            "/api/auth/register",
            {
                "email": "duplicate@example.com",
                "name": "First User",
                "password": "strongpass123",
                "user_type": "student",
            },
        )

        response = self.post_json(
            "/api/auth/register",
            {
                "email": "duplicate@example.com",
                "name": "Second User",
                "password": "strongpass123",
                "user_type": "student",
            },
        )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.get_json()["error"], "Email is already registered")

    def test_login_returns_token_and_safe_user_for_valid_credentials(self):
        """Valid credentials should return a token and omit password_hash from the response."""
        self.seed_user()

        response = self.post_json(
            "/api/auth/login",
            {
                "email": "student@example.com",
                "password": "strongpass123",
            },
        )

        self.assertEqual(response.status_code, 200)

        payload = response.get_json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["message"], "Login successful")
        self.assertIn("token", payload["data"])

        user = payload["data"]["user"]
        self.assertEqual(user["email"], "student@example.com")
        self.assertEqual(user["name"], "Student")
        self.assertEqual(user["user_type"], "student")
        self.assertNotIn("password_hash", user)

    def test_login_requires_email_and_password(self):
        """Reject login when either email or password is missing."""
        response = self.post_json(
            "/api/auth/login",
            {
                "email": "",
                "password": "",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "Email and password are required")

    def test_login_rejects_wrong_password(self):
        """Reject login when the password does not match the stored hash."""
        self.seed_user()

        response = self.post_json(
            "/api/auth/login",
            {
                "email": "student@example.com",
                "password": "wrongpass123",
            },
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json()["error"], "Invalid credentials")

    def test_login_rejects_unknown_email(self):
        """Reject login when no user exists for the submitted email."""
        response = self.post_json(
            "/api/auth/login",
            {
                "email": "missing@example.com",
                "password": "strongpass123",
            },
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json()["error"], "Invalid credentials")


if __name__ == "__main__":
    unittest.main()
