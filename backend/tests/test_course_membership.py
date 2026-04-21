"""
Tests for course membership routes.

This module sets up an isolated Flask app and temporary database for
course join and membership access tests.
"""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from flask import Flask

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from forum_ai_notetaker import db
from routes.courses import courses_bp


class CourseMembershipTests(unittest.TestCase):
    """Shared scaffold for course membership route tests."""

    def setUp(self):
        """
        Build an isolated app and seed users, courses, and memberships.

        The seed data includes:
        - one instructor
        - two student accounts
        - one course that already has an instructor and one student member
        - one separate course for non-member access checks
        """
        self.tempdir = tempfile.TemporaryDirectory()
        self.original_db_path = db.DEFAULT_DB_PATH
        db.DEFAULT_DB_PATH = Path(self.tempdir.name) / "test.sqlite3"
        db.init_db()

        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.register_blueprint(courses_bp, url_prefix="/api/courses")
        self.client = self.app.test_client()

        with db.get_connection() as conn:
            conn.executescript(
                """
                INSERT INTO users (
                    id, email, name, password_hash, user_type, created_at, updated_at
                )
                VALUES
                    (1, 'teacher@example.com', 'Teacher', 'hash', 'professor', datetime('now'), datetime('now')),
                    (2, 'student@example.com', 'Student', 'hash', 'student', datetime('now'), datetime('now')),
                    (3, 'outsider@example.com', 'Outsider', 'hash', 'student', datetime('now'), datetime('now'));

                INSERT INTO courses (id, name, invite_code, created_at, updated_at)
                VALUES
                    (1, 'Algorithms', 'ALGO01', datetime('now'), datetime('now')),
                    (2, 'Databases', 'DATA02', datetime('now'), datetime('now'));

                INSERT INTO course_members (
                    course_id, user_id, role, created_at, updated_at
                )
                VALUES
                    (1, 1, 'instructor', datetime('now'), datetime('now')),
                    (1, 2, 'student', datetime('now'), datetime('now')),
                    (2, 3, 'student', datetime('now'), datetime('now'));
                """
            )
            conn.commit()

        self.instructor_user = {
            "id": 1,
            "email": "teacher@example.com",
            "name": "Teacher",
            "user_type": "professor",
        }
        self.student_user = {
            "id": 2,
            "email": "student@example.com",
            "name": "Student",
            "user_type": "student",
        }
        self.outsider_user = {
            "id": 3,
            "email": "outsider@example.com",
            "name": "Outsider",
            "user_type": "student",
        }

    def tearDown(self):
        """Restore the original database path and remove temp files."""
        db.DEFAULT_DB_PATH = self.original_db_path
        self.tempdir.cleanup()

    def post_json(self, path, *, user, json):
        """Send an authenticated JSON POST request as the given user."""
        headers = {"Authorization": "Bearer test-token"}

        with patch("middleware.auth.verify_token", return_value=user):
            return self.client.post(path, json=json, headers=headers)

    def get_json(self, path, *, user):
        """Send an authenticated GET request as the given user."""
        headers = {"Authorization": "Bearer test-token"}

        with patch("middleware.auth.verify_token", return_value=user):
            return self.client.get(path, headers=headers)


if __name__ == "__main__":
    unittest.main()
