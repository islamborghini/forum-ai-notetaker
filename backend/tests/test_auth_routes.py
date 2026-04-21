import os
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
from routes.auth import auth_bp
from utils.auth import verify_token


class AuthRouteTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.original_db_path = db.DEFAULT_DB_PATH
        db.DEFAULT_DB_PATH = Path(self.tempdir.name) / "test.sqlite3"
        db.init_db()

        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.register_blueprint(auth_bp, url_prefix="/api/auth")
        self.client = self.app.test_client()

    def tearDown(self):
        db.DEFAULT_DB_PATH = self.original_db_path
        self.tempdir.cleanup()

    def test_register_succeeds_without_jwt_secret_env(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("JWT_SECRET_KEY", None)

            response = self.client.post(
                "/api/auth/register",
                json={
                    "email": "student@example.com",
                    "name": "Student",
                    "password": "password123",
                    "user_type": "student",
                },
            )

        self.assertEqual(response.status_code, 201)
        payload = response.get_json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["message"], "User registered successfully")

        token = payload["data"]["token"]
        user = payload["data"]["user"]

        decoded = verify_token(token)

        self.assertEqual(user["email"], "student@example.com")
        self.assertEqual(user["user_type"], "student")
        self.assertEqual(decoded["email"], "student@example.com")
        self.assertEqual(decoded["user_id"], user["id"])


if __name__ == "__main__":
    unittest.main()
