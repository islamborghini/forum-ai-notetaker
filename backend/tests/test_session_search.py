import sys
import tempfile
import unittest
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from forum_ai_notetaker import db
from services.session_service import search_sessions_for_user


class SessionSearchTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.original_db_path = db.DEFAULT_DB_PATH
        db.DEFAULT_DB_PATH = Path(self.tempdir.name) / "test.sqlite3"
        db.init_db()

        with db.get_connection() as conn:
            conn.executescript(
                """
                INSERT INTO users (id, email, name, password_hash, created_at, updated_at)
                VALUES
                    (1, 'member@example.com', 'Member', 'hash', datetime('now'), datetime('now')),
                    (2, 'outsider@example.com', 'Outsider', 'hash', datetime('now'), datetime('now'));

                INSERT INTO courses (id, name, invite_code, created_at, updated_at)
                VALUES
                    (1, 'Course One', 'COURSE1', datetime('now'), datetime('now')),
                    (2, 'Course Two', 'COURSE2', datetime('now'), datetime('now'));

                INSERT INTO course_members (course_id, user_id, role, created_at, updated_at)
                VALUES (1, 1, 'student', datetime('now'), datetime('now'));

                INSERT INTO sessions (
                    id, title, original_filename, stored_path, status, course_id, created_at, updated_at
                )
                VALUES
                    (1, 'Week 1 Review', 'week1.mp3', 'uploads/week1.mp3', 'notes_generated', 1, datetime('now'), datetime('now')),
                    (2, 'Lab Recording', 'lab.mp3', 'uploads/lab.mp3', 'notes_generated', 1, datetime('now'), datetime('now')),
                    (3, 'Private Lecture', 'private.mp3', 'uploads/private.mp3', 'notes_generated', 2, datetime('now'), datetime('now'));

                INSERT INTO transcripts (session_id, content, created_at, updated_at)
                VALUES
                    (1, 'Today we cover vectors and matrices.', datetime('now'), datetime('now')),
                    (2, 'This transcript mentions reinforcement learning.', datetime('now'), datetime('now')),
                    (3, 'This private transcript also mentions reinforcement learning.', datetime('now'), datetime('now'));
                """
            )
            conn.commit()

    def tearDown(self):
        db.DEFAULT_DB_PATH = self.original_db_path
        self.tempdir.cleanup()

    def test_search_matches_titles_and_transcripts_for_user_courses(self):
        title_results = search_sessions_for_user(1, "review")
        transcript_results = search_sessions_for_user(1, "reinforcement")

        self.assertEqual([row["id"] for row in title_results], [1])
        self.assertEqual([row["id"] for row in transcript_results], [2])


if __name__ == "__main__":
    unittest.main()
