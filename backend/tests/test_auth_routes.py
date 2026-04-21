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


if __name__ == "__main__":
    unittest.main()
