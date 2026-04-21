"""Simple migration helper for schema updates.

This module provides idempotent migrations to safely update the database
schema without breaking existing data or requiring a full database reset.
"""

import sqlite3

from forum_ai_notetaker.db import DEFAULT_DB_PATH


def migrate_add_segments_column() -> None:
    """Add segments column to transcripts table if it doesn't exist.

    This migration is safe to run multiple times. If the column already
    exists, it does nothing. If the database doesn't exist yet, the
    schema.sql will create it with the column on first init.
    """
    db_path = DEFAULT_DB_PATH

    # If DB doesn't exist yet, schema.sql will handle it on init_db().
    if not db_path.exists():
        return

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    try:
        # Check if segments column already exists.
        cursor.execute("PRAGMA table_info(transcripts)")
        columns = [row[1] for row in cursor.fetchall()]

        if "segments" not in columns:
            print("[migration] Adding 'segments' column to transcripts table...")
            cursor.execute("ALTER TABLE transcripts ADD COLUMN segments TEXT;")
            conn.commit()
            print("[migration] ✅ 'segments' column added successfully.")
        else:
            # Column already exists; idempotent, so this is fine.
            pass

    except sqlite3.OperationalError as exc:
        # Table might not exist if DB is corrupted or very old.
        print(f"[migration] ⚠️  Could not check transcripts table: {exc}")
    finally:
        conn.close()
