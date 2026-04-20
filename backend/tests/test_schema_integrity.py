import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from forum_ai_notetaker import db


class SchemaIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.original_db_path = db.DEFAULT_DB_PATH
        db.DEFAULT_DB_PATH = Path(self.tempdir.name) / "test.sqlite3"
        db.init_db()

    def tearDown(self):
        db.DEFAULT_DB_PATH = self.original_db_path
        self.tempdir.cleanup()

    def seed_parent_rows(self, conn):
        conn.executescript(
            """
            INSERT INTO users (id, email, name, password_hash, created_at, updated_at)
            VALUES
                (1, 'owner@example.com', 'Owner', 'hash', datetime('now'), datetime('now')),
                (2, 'member@example.com', 'Member', 'hash', datetime('now'), datetime('now'));

            INSERT INTO courses (id, name, invite_code, created_at, updated_at)
            VALUES (1, 'Course One', 'COURSE1', datetime('now'), datetime('now'));

            INSERT INTO course_members (course_id, user_id, role, created_at, updated_at)
            VALUES
                (1, 1, 'instructor', datetime('now'), datetime('now')),
                (1, 2, 'student', datetime('now'), datetime('now'));

            INSERT INTO sessions (
                id, title, original_filename, stored_path, status, course_id, created_at, updated_at
            )
            VALUES (1, 'Lecture One', 'lecture.mp3', 'uploads/lecture.mp3', 'notes_generated', 1, datetime('now'), datetime('now'));

            INSERT INTO transcripts (id, session_id, content, created_at, updated_at)
            VALUES (1, 1, 'Transcript content', datetime('now'), datetime('now'));

            INSERT INTO notes (id, session_id, summary, topics, action_items, created_at, updated_at)
            VALUES (1, 1, 'Summary', '[]', '[]', datetime('now'), datetime('now'));
            """
        )
        conn.commit()

    def test_connections_enable_foreign_key_enforcement(self):
        with db.get_connection() as conn:
            enabled = conn.execute("PRAGMA foreign_keys").fetchone()[0]

        self.assertEqual(enabled, 1)

    def test_foreign_keys_reject_missing_parent_rows(self):
        with db.get_connection() as conn:
            self.seed_parent_rows(conn)

            invalid_statements = [
                (
                    """
                    INSERT INTO course_members (course_id, user_id, role, created_at, updated_at)
                    VALUES (999, 1, 'student', datetime('now'), datetime('now'))
                    """
                ),
                (
                    """
                    INSERT INTO course_members (course_id, user_id, role, created_at, updated_at)
                    VALUES (1, 999, 'student', datetime('now'), datetime('now'))
                    """
                ),
                (
                    """
                    INSERT INTO sessions (
                        title, original_filename, stored_path, status, course_id, created_at, updated_at
                    )
                    VALUES ('Bad Course', 'bad.mp3', 'uploads/bad.mp3', 'uploaded', 999, datetime('now'), datetime('now'))
                    """
                ),
                (
                    """
                    INSERT INTO transcripts (session_id, content, created_at, updated_at)
                    VALUES (999, 'Missing session', datetime('now'), datetime('now'))
                    """
                ),
                (
                    """
                    INSERT INTO notes (session_id, summary, topics, action_items, created_at, updated_at)
                    VALUES (999, 'Missing session', '[]', '[]', datetime('now'), datetime('now'))
                    """
                ),
            ]

            for statement in invalid_statements:
                with self.subTest(statement=statement):
                    with self.assertRaises(sqlite3.IntegrityError):
                        conn.execute(statement)

    def test_deleting_course_cascades_memberships_and_nulls_sessions(self):
        with db.get_connection() as conn:
            self.seed_parent_rows(conn)

            conn.execute("DELETE FROM courses WHERE id = ?", (1,))
            conn.commit()

            member_count = conn.execute("SELECT COUNT(*) FROM course_members").fetchone()[0]
            session = conn.execute(
                "SELECT course_id FROM sessions WHERE id = ?",
                (1,),
            ).fetchone()
            transcript_count = conn.execute("SELECT COUNT(*) FROM transcripts").fetchone()[0]
            notes_count = conn.execute("SELECT COUNT(*) FROM notes").fetchone()[0]

        self.assertEqual(member_count, 0)
        self.assertIsNone(session["course_id"])
        self.assertEqual(transcript_count, 1)
        self.assertEqual(notes_count, 1)

    def test_deleting_user_cascades_memberships(self):
        with db.get_connection() as conn:
            self.seed_parent_rows(conn)

            conn.execute("DELETE FROM users WHERE id = ?", (2,))
            conn.commit()

            member_rows = conn.execute(
                "SELECT user_id FROM course_members ORDER BY user_id"
            ).fetchall()
            session_count = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]

        self.assertEqual([row["user_id"] for row in member_rows], [1])
        self.assertEqual(session_count, 1)

    def test_deleting_session_cascades_transcript_and_notes(self):
        with db.get_connection() as conn:
            self.seed_parent_rows(conn)

            conn.execute("DELETE FROM sessions WHERE id = ?", (1,))
            conn.commit()

            transcript_count = conn.execute("SELECT COUNT(*) FROM transcripts").fetchone()[0]
            notes_count = conn.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
            member_count = conn.execute("SELECT COUNT(*) FROM course_members").fetchone()[0]

        self.assertEqual(transcript_count, 0)
        self.assertEqual(notes_count, 0)
        self.assertEqual(member_count, 2)


if __name__ == "__main__":
    unittest.main()
