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

        # Keep the shared fixture small: one target course, one outside
        # course, and just enough users to exercise join/member checks.
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

        # Patch auth at the middleware boundary so route tests stay
        # focused on course behavior instead of JWT details.
        with patch("middleware.auth.verify_token", return_value=user):
            return self.client.post(path, json=json, headers=headers)

    def get_json(self, path, *, user):
        """Send an authenticated GET request as the given user."""
        headers = {"Authorization": "Bearer test-token"}

        # Patch auth at the middleware boundary so route tests stay
        # focused on course behavior instead of JWT details.
        with patch("middleware.auth.verify_token", return_value=user):
            return self.client.get(path, headers=headers)

    def test_student_can_join_course_with_valid_invite_code(self):
        """
        A student with a valid invite code should join as a student member.

        The route should return the course and membership payload and
        persist a new course_members row in the database.
        """
        response = self.post_json(
            "/api/courses/join",
            user=self.outsider_user,
            json={"invite_code": "ALGO01"},
        )

        self.assertEqual(response.status_code, 201)

        payload = response.get_json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["message"], "Joined course successfully")

        data = payload["data"]
        self.assertEqual(data["course"]["id"], 1)
        self.assertEqual(data["course"]["name"], "Algorithms")
        self.assertEqual(data["membership"]["course_id"], 1)
        self.assertEqual(data["membership"]["user_id"], 3)
        self.assertEqual(data["membership"]["role"], "student")

        with db.get_connection() as conn:
            membership = conn.execute(
                """
                SELECT course_id, user_id, role
                FROM course_members
                WHERE course_id = ? AND user_id = ?
                """,
                (1, 3),
            ).fetchone()

        self.assertIsNotNone(membership)
        self.assertEqual(membership["course_id"], 1)
        self.assertEqual(membership["user_id"], 3)
        self.assertEqual(membership["role"], "student")

    def test_join_course_requires_json_body(self):
        """Reject join requests that do not send a JSON body."""
        headers = {"Authorization": "Bearer test-token"}

        with patch("middleware.auth.verify_token", return_value=self.outsider_user):
            response = self.client.post("/api/courses/join", headers=headers)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "Request body must be JSON")

    def test_join_course_requires_invite_code(self):
        """Reject join requests with a missing invite code."""
        response = self.post_json(
            "/api/courses/join",
            user=self.outsider_user,
            json={},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "Invite code required")

    def test_join_course_rejects_invalid_invite_code(self):
        """Return 404 when the invite code does not match any course."""
        response = self.post_json(
            "/api/courses/join",
            user=self.outsider_user,
            json={"invite_code": "NOPE99"},
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()["error"], "Invalid invite code")

    def test_join_course_rejects_existing_member(self):
        """Return 409 when the user already belongs to the course."""
        response = self.post_json(
            "/api/courses/join",
            user=self.student_user,
            json={"invite_code": "ALGO01"},
        )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(
            response.get_json()["error"],
            "User is already a member of this course",
        )

    def test_join_course_rejects_professor_accounts(self):
        """Only student accounts should be able to join via invite code."""
        response = self.post_json(
            "/api/courses/join",
            user=self.instructor_user,
            json={"invite_code": "ALGO01"},
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.get_json()["error"],
            "Only student accounts can join courses via invite code",
        )

    def test_student_member_can_view_course_details_without_invite_code(self):
        """Student members should see course details but not the invite code."""
        response = self.get_json("/api/courses/1", user=self.student_user)

        self.assertEqual(response.status_code, 200)

        payload = response.get_json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["message"], "Course retrieved")

        data = payload["data"]
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["name"], "Algorithms")
        self.assertEqual(data["your_role"], "student")
        self.assertNotIn("invite_code", data)

        member_roles = {member["user_id"]: member["role"] for member in data["members"]}
        self.assertEqual(member_roles[1], "instructor")
        self.assertEqual(member_roles[2], "student")

    def test_instructor_member_can_view_course_details_with_invite_code(self):
        """Instructors should receive the invite code in course details."""
        response = self.get_json("/api/courses/1", user=self.instructor_user)

        self.assertEqual(response.status_code, 200)

        payload = response.get_json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["message"], "Course retrieved")

        data = payload["data"]
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["name"], "Algorithms")
        self.assertEqual(data["your_role"], "instructor")
        self.assertEqual(data["invite_code"], "ALGO01")

    def test_non_member_cannot_view_course_details(self):
        """Non-members should be denied access to course detail data."""
        response = self.get_json("/api/courses/1", user=self.outsider_user)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.get_json()["error"], "Access denied")

    def test_non_member_cannot_view_course_sessions(self):
        """Non-members should be denied access to the course sessions listing."""
        response = self.get_json("/api/courses/1/sessions", user=self.outsider_user)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.get_json()["error"],
            "You are not a member of this course",
        )


if __name__ == "__main__":
    unittest.main()
