#!/usr/bin/env python3
"""
Test the migration system by:
1. Creating a fresh database with init_db()
2. Verifying the segments column was added
"""

import sqlite3
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from forum_ai_notetaker.db import init_db


def test_migration():
    """Test the migration on a fresh database."""
    print("[test] Starting migration test...\n")

    # Step 1: Initialize fresh database (schema.sql + migrations)
    print("[test] Step 1: Initializing database...")
    db_path = init_db()
    print(f"[test] ✅ Database initialized at {db_path}\n")

    # Step 2: Verify segments column exists
    print("[test] Step 2: Verifying segments column...")
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(transcripts)")
    columns = {row[1]: row for row in cursor.fetchall()}
    conn.close()

    if "segments" in columns:
        print("[test] ✅ segments column found!")
        print(f"\n[test] Transcripts table schema:")
        for col_name, col_info in columns.items():
            col_type = col_info[2]
            print(f"  - {col_name} ({col_type})")
        print("\n[test] ✅✅✅ Migration test PASSED")
        return True
    else:
        print("[test] ❌ segments column NOT found!")
        print(f"Columns: {list(columns.keys())}")
        print("\n[test] ❌ Migration test FAILED")
        return False


if __name__ == "__main__":
    try:
        success = test_migration()
        sys.exit(0 if success else 1)
    except Exception as exc:
        print(f"[test] ❌ Unexpected error: {exc}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
