"""
Session service layer.

This module handles persistence and retrieval of session records.

A session represents one uploaded recording plus the metadata needed
to track it through the processing pipeline, such as status and
course ownership.

All session-related database access is centralized here so that route
handlers do not need to work directly with SQL queries.
"""

from typing import Optional

from forum_ai_notetaker.db import get_connection


def _row_to_dict(row) -> dict:
    """
    Convert a raw database row into a plain Python dictionary.

    This helper keeps the return format consistent across the service
    layer and avoids repeating conversion logic in every function.
    """
    return dict(row)


def create_session_record(
    title: str,
    original_filename: str,
    stored_path: str,
    status: str,
    course_id: int,
) -> dict:
    """
    Create and store a new session record.

    This function is called after an uploaded file has passed
    validation and has been saved to disk. It persists the session
    metadata so the rest of the system can track processing state
    and enforce course-based access control.

    Args:
        title: Human-readable title of the session.
        original_filename: The original uploaded filename after cleaning.
        stored_path: The backend-relative path where the file is stored.
        status: The current processing state of the session.
        course_id: The course the session belongs to.

    Returns:
        A dictionary representing the newly created session.
    """
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO sessions (
                title,
                original_filename,
                stored_path,
                status,
                course_id,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))
            """,
            (title, original_filename, stored_path, status, course_id),
        )
        conn.commit()

        row = conn.execute(
            """
            SELECT *
            FROM sessions
            WHERE id = ?
            """,
            (cursor.lastrowid,),
        ).fetchone()

    return _row_to_dict(row)


def fetch_sessions_for_user(user_id: int) -> list[dict]:
    """
    Return all sessions visible to a given user.

    A session is visible only if the user belongs to the course
    associated with that session.

    Args:
        user_id: The ID of the authenticated user.

    Returns:
        A list of session dictionaries ordered by most recent first.
    """
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT s.*
            FROM sessions AS s
            JOIN course_members AS cm ON s.course_id = cm.course_id
            WHERE cm.user_id = ?
            ORDER BY s.id DESC
            """,
            (user_id,),
        ).fetchall()

    return [_row_to_dict(row) for row in rows]


def fetch_one_session(session_id: int) -> Optional[dict]:
    """
    Retrieve a single session by ID.

    Args:
        session_id: The ID of the session being requested.

    Returns:
        A session dictionary if found, otherwise None.
    """
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT *
            FROM sessions
            WHERE id = ?
            """,
            (session_id,),
        ).fetchone()

    return _row_to_dict(row) if row else None


def search_sessions_for_user(user_id: int, query: str) -> list[dict]:
    """
    Search sessions by title, transcript content, and generated notes,
    restricted to the authenticated user's courses.

    A session is included in the results if:
    - the user belongs to the session's course, and
    - the query matches at least one of:
        • session title
        • transcript content
        • notes summary
        • notes topics (stored as JSON string)
        • notes action items (stored as JSON string)

    In addition to the session fields, this query also returns the
    matching transcript and notes text so the search layer can build
    snippets for the frontend.

    Args:
        user_id: The authenticated user's ID.
        query: The search term provided by the user.

    Returns:
        A list of matching session dictionaries ordered by most recent first.
    """
    like_query = f"%{query}%"

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT DISTINCT
                s.*,
                t.content AS transcript_content,
                n.summary AS notes_summary,
                n.topics AS notes_topics,
                n.action_items AS notes_action_items
            FROM sessions AS s
            JOIN course_members AS cm ON s.course_id = cm.course_id
            LEFT JOIN transcripts AS t ON t.session_id = s.id
            LEFT JOIN notes AS n ON n.session_id = s.id
            WHERE cm.user_id = ?
              AND (
                    s.title LIKE ?
                    OR COALESCE(t.content, '') LIKE ?
                    OR COALESCE(n.summary, '') LIKE ?
                    OR COALESCE(n.topics, '') LIKE ?
                    OR COALESCE(n.action_items, '') LIKE ?
                  )
            ORDER BY s.id DESC
            """,
            (user_id, like_query, like_query, like_query, like_query, like_query),
        ).fetchall()

    return [_row_to_dict(row) for row in rows]


def update_session_status(session_id: int, new_status: str) -> None:
    """
    Update the processing status of a session.

    This is typically called by the pipeline as a recording moves
    through different stages such as uploaded, processing,
    transcribed, or notes_generated.

    Args:
        session_id: The session being updated.
        new_status: The new processing state to store.
    """
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE sessions
            SET status = ?, updated_at = datetime('now')
            WHERE id = ?
            """,
            (new_status, session_id),
        )
        conn.commit()


def recover_interrupted_processing_sessions() -> None:
    """
    Mark any sessions stuck in processing as failed on startup.
    """
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id
            FROM sessions
            WHERE status = 'processing'
            """
        ).fetchall()

        for row in rows:
            session_id = row["id"]
            conn.execute(
                """
                UPDATE sessions
                SET status = 'failed', updated_at = datetime('now')
                WHERE id = ?
                """,
                (session_id,),
            )
            print(f"[RECOVERY] Session {session_id} marked as failed")

        conn.commit()
