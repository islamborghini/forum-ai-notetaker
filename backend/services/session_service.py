"""
Session service layer.

This module connects session routes to the SQLite database.

A session represents one uploaded recording plus the metadata
used to track its processing state through the pipeline.
"""

from typing import Optional

from forum_ai_notetaker.db import get_connection


def _row_to_dict(row) -> dict:
    """
    Convert a SQLite row object into a plain dictionary.

    Keeping this helper here avoids repeating `dict(row)` across
    the service layer and keeps the returned shape consistent.
    """
    return dict(row)


def create_session_record(
    title: str,
    original_filename: str,
    stored_path: str,
    status: str,
) -> dict:
    """
    Create and store a new session record.

    This function is called after a recording has been uploaded
    successfully. It persists the metadata needed for later
    retrieval and pipeline status tracking.

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
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))
            """,
            (title, original_filename, stored_path, status),
        )
        conn.commit()

        row = conn.execute(
            """
            SELECT id, title, original_filename, stored_path, status, created_at, updated_at
            FROM sessions
            WHERE id = ?
            """,
            (cursor.lastrowid,),
        ).fetchone()

    return _row_to_dict(row)


def fetch_all_sessions() -> list[dict]:
    """
    Return all sessions currently stored in the database.

    Sessions are ordered with the most recent first so the frontend
    can display newly uploaded recordings at the top.
    """
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, title, original_filename, stored_path, status, created_at, updated_at
            FROM sessions
            ORDER BY id DESC
            """
        ).fetchall()

    return [_row_to_dict(row) for row in rows]


def fetch_one_session(session_id: int) -> Optional[dict]:
    """
    Return one session by ID.

    Returns:
        A session dictionary if found, otherwise None.
    """
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT id, title, original_filename, stored_path, status, created_at, updated_at
            FROM sessions
            WHERE id = ?
            """,
            (session_id,),
        ).fetchone()

    return _row_to_dict(row) if row else None


def update_session_status(session_id: int, new_status: str) -> None:
    """
    Update the processing status of a session.

    This is typically called by the pipeline as the recording moves
    through different stages such as uploaded, processing,
    transcribed, or notes_generated.
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