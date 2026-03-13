from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .db import get_connection, init_db


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _row_to_dict(row: Any) -> dict[str, Any] | None:
    return dict(row) if row is not None else None


def create_session(
    title: str | None,
    original_filename: str,
    stored_path: str,
    *,
    status: str = "uploaded",
    db_path: str | Path | None = None,
) -> dict[str, Any]:
    init_db(db_path)
    now = _utc_now()
    normalized_title = title or Path(original_filename).stem or "Untitled session"

    with get_connection(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO sessions (
                title,
                original_filename,
                stored_path,
                status,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (normalized_title, original_filename, stored_path, status, now, now),
        )
        connection.commit()
        session_id = cursor.lastrowid

    session = get_session(session_id, db_path=db_path)
    if session is None:
        raise RuntimeError("Session was created but could not be loaded.")
    return session


def get_session(
    session_id: int,
    *,
    db_path: str | Path | None = None,
) -> dict[str, Any] | None:
    init_db(db_path)
    with get_connection(db_path) as connection:
        row = connection.execute(
            """
            SELECT
                sessions.id,
                sessions.title,
                sessions.original_filename,
                sessions.stored_path,
                sessions.status,
                sessions.created_at,
                sessions.updated_at,
                transcripts.id IS NOT NULL AS has_transcript
            FROM sessions
            LEFT JOIN transcripts
                ON transcripts.session_id = sessions.id
            WHERE sessions.id = ?
            """,
            (session_id,),
        ).fetchone()
    return _row_to_dict(row)


def save_transcript(
    session_id: int,
    content: str,
    *,
    db_path: str | Path | None = None,
) -> dict[str, Any]:
    init_db(db_path)
    now = _utc_now()

    with get_connection(db_path) as connection:
        session_exists = connection.execute(
            "SELECT 1 FROM sessions WHERE id = ?",
            (session_id,),
        ).fetchone()
        if session_exists is None:
            raise ValueError(f"Session {session_id} does not exist.")

        connection.execute(
            """
            INSERT INTO transcripts (
                session_id,
                content,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?)
            ON CONFLICT(session_id) DO UPDATE SET
                content = excluded.content,
                updated_at = excluded.updated_at
            """,
            (session_id, content, now, now),
        )
        connection.execute(
            """
            UPDATE sessions
            SET status = ?, updated_at = ?
            WHERE id = ?
            """,
            ("transcribed", now, session_id),
        )
        connection.commit()

    transcript = get_transcript(session_id, db_path=db_path)
    if transcript is None:
        raise RuntimeError("Transcript was saved but could not be loaded.")
    return transcript


def get_transcript(
    session_id: int,
    *,
    db_path: str | Path | None = None,
) -> dict[str, Any] | None:
    init_db(db_path)
    with get_connection(db_path) as connection:
        row = connection.execute(
            """
            SELECT
                sessions.id AS session_id,
                sessions.title,
                sessions.original_filename,
                sessions.stored_path,
                sessions.status,
                sessions.created_at AS session_created_at,
                sessions.updated_at AS session_updated_at,
                transcripts.id AS transcript_id,
                transcripts.content,
                transcripts.created_at AS transcript_created_at,
                transcripts.updated_at AS transcript_updated_at
            FROM sessions
            LEFT JOIN transcripts
                ON transcripts.session_id = sessions.id
            WHERE sessions.id = ?
            """,
            (session_id,),
        ).fetchone()
    return _row_to_dict(row)


def list_sessions(
    *,
    db_path: str | Path | None = None,
) -> list[dict[str, Any]]:
    init_db(db_path)
    with get_connection(db_path) as connection:
        rows = connection.execute(
            """
            SELECT
                sessions.id,
                sessions.title,
                sessions.original_filename,
                sessions.stored_path,
                sessions.status,
                sessions.created_at,
                sessions.updated_at,
                transcripts.id IS NOT NULL AS has_transcript
            FROM sessions
            LEFT JOIN transcripts
                ON transcripts.session_id = sessions.id
            ORDER BY sessions.created_at DESC, sessions.id DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]
