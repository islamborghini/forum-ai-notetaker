#!/usr/bin/env python3
"""
Quick verification script to check if the segments column exists
in the transcripts table.

Usage:
    cd backend
    python3 verify_migration.py
"""

import sqlite3
import sys
from pathlib import Path


def check_segments_column():
    """Check if the segments column exists in the transcripts table."""
    # Database is at PROJECT_ROOT / "data" / "forum_ai_notetaker.sqlite3"
    # This script is in PROJECT_ROOT / "backend"
    db_path = Path(__file__).resolve().parent.parent / "data" / "forum_ai_notetaker.sqlite3"

    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        print("   Run the app once to initialize the database.")
        return False

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    try:
        cursor.execute("PRAGMA table_info(transcripts)")
        columns = [row[1] for row in cursor.fetchall()]

        if "segments" in columns:
            print("✅ segments column exists in transcripts table")
            print(f"\nAll columns in transcripts table:")
            for col in columns:
                print(f"  - {col}")
            return True
        else:
            print("❌ segments column NOT found in transcripts table")
            print(f"\nColumns present: {columns}")
            return False

    except sqlite3.OperationalError as exc:
        print(f"❌ Error checking table: {exc}")
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    success = check_segments_column()
    sys.exit(0 if success else 1)
