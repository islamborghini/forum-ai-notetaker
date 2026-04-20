import io
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

if "dotenv" not in sys.modules:
    dotenv_module = ModuleType("dotenv")
    dotenv_module.load_dotenv = lambda *args, **kwargs: None
    sys.modules["dotenv"] = dotenv_module

if "groq" not in sys.modules:
    groq_module = ModuleType("groq")

    class _Groq:
        def __init__(self, *args, **kwargs):
            pass

    groq_module.Groq = _Groq
    sys.modules["groq"] = groq_module

if "whisper" not in sys.modules:
    whisper_module = ModuleType("whisper")
    whisper_module.load_model = lambda *args, **kwargs: None
    sys.modules["whisper"] = whisper_module

from flask import Flask

from forum_ai_notetaker import db
from routes.sessions import sessions_bp


class SessionUploadTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.original_db_path = db.DEFAULT_DB_PATH
        db.DEFAULT_DB_PATH = Path(self.tempdir.name) / "test.sqlite3"
        db.init_db()

        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["UPLOAD_FOLDER"] = str(Path(self.tempdir.name) / "uploads")
        self.app.register_blueprint(sessions_bp, url_prefix="/api/sessions")
        self.client = self.app.test_client()

        with db.get_connection() as conn:
            conn.executescript(
                """
                INSERT INTO users (
                    id, email, name, password_hash, user_type, created_at, updated_at
                )
                VALUES
                    (1, 'teacher@example.com', 'Teacher', 'hash', 'professor', datetime('now'), datetime('now')),
                    (2, 'student@example.com', 'Student', 'hash', 'student', datetime('now'), datetime('now'));

                INSERT INTO courses (id, name, invite_code, created_at, updated_at)
                VALUES (1, 'Algorithms', 'ALGO01', datetime('now'), datetime('now'));

                INSERT INTO course_members (
                    course_id, user_id, role, created_at, updated_at
                )
                VALUES
                    (1, 1, 'instructor', datetime('now'), datetime('now')),
                    (1, 2, 'student', datetime('now'), datetime('now'));
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

    def tearDown(self):
        db.DEFAULT_DB_PATH = self.original_db_path
        self.tempdir.cleanup()

    def post_upload(self, *, user, title="Week 1 Lecture", course_id="1", filename="lecture.mp3"):
        data = {
            "title": title,
            "course_id": course_id,
            "file": (io.BytesIO(b"fake audio bytes"), filename),
        }
        headers = {"Authorization": "Bearer test-token"}

        with patch("middleware.auth.verify_token", return_value=user):
            return self.client.post(
                "/api/sessions/upload",
                data=data,
                headers=headers,
                content_type="multipart/form-data",
            )

    @patch("routes.sessions.trigger_pipeline")
    def test_upload_creates_session_saves_file_and_triggers_pipeline(self, mock_trigger_pipeline):
        response = self.post_upload(
            user=self.instructor_user,
            title="Week 1 Lecture",
            course_id="1",
            filename="Lecture 1!.MP3",
        )

        self.assertEqual(response.status_code, 201)

        payload = response.get_json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["message"], "Recording uploaded successfully")

        session = payload["data"]
        self.assertEqual(session["title"], "Week 1 Lecture")
        self.assertEqual(session["course_id"], 1)
        self.assertEqual(session["status"], "uploaded")
        self.assertEqual(session["original_filename"], "Lecture_1.MP3")
        self.assertTrue(session["stored_path"].startswith("uploads/"))

        stored_filename = Path(session["stored_path"]).name
        saved_file = Path(self.app.config["UPLOAD_FOLDER"]) / stored_filename
        self.assertTrue(saved_file.exists())
        self.assertEqual(saved_file.read_bytes(), b"fake audio bytes")

        with db.get_connection() as conn:
            row = conn.execute(
                """
                SELECT title, original_filename, stored_path, status, course_id
                FROM sessions
                WHERE id = ?
                """,
                (session["id"],),
            ).fetchone()

        self.assertIsNotNone(row)
        self.assertEqual(row["title"], "Week 1 Lecture")
        self.assertEqual(row["original_filename"], "Lecture_1.MP3")
        self.assertEqual(row["stored_path"], session["stored_path"])
        self.assertEqual(row["status"], "uploaded")
        self.assertEqual(row["course_id"], 1)

        mock_trigger_pipeline.assert_called_once_with(session["stored_path"], session["id"])

    def test_upload_requires_file_field(self):
        headers = {"Authorization": "Bearer test-token"}

        with patch("middleware.auth.verify_token", return_value=self.instructor_user):
            response = self.client.post(
                "/api/sessions/upload",
                data={"title": "Week 1 Lecture", "course_id": "1"},
                headers=headers,
                content_type="multipart/form-data",
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "No file provided")

    def test_upload_rejects_empty_filename(self):
        response = self.post_upload(
            user=self.instructor_user,
            filename="",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "No file selected")

    def test_upload_requires_title(self):
        response = self.post_upload(
            user=self.instructor_user,
            title="",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "Title is required")

    def test_upload_requires_course_id(self):
        response = self.post_upload(
            user=self.instructor_user,
            course_id="",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "course_id is required")


if __name__ == "__main__":
    unittest.main()
