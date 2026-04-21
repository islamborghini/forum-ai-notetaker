#!/usr/bin/env python3
"""
End-to-end integration test for transcript segments persistence.

This test verifies that:
1. We can save a transcript with segments as JSON
2. We can retrieve it back and parse the JSON correctly
3. The segments maintain their structure (start, end, text)

Usage:
    cd backend
    python3 test_e2e_segments.py
"""

import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from forum_ai_notetaker.db import init_db
from services.transcript_service import save_transcript, fetch_transcript_by_session_id


def test_segments_persistence():
    """Test that segments are saved and retrieved correctly."""
    print("[test] Starting end-to-end segments test...")

    # Initialize database (runs migrations)
    print("[test] Step 1: Initializing database...")
    try:
        db_path = init_db()
        print(f"[test] ✅ Database initialized at {db_path}")
    except Exception as exc:
        print(f"[test] ❌ Failed to initialize database: {exc}")
        return False

    # Create a test session (required for foreign key constraint)
    print("[test] Step 1b: Creating test session...")
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat() + "Z"
        
        # Check if test session already exists
        cursor.execute("SELECT id FROM sessions WHERE title = 'Test Session'")
        existing = cursor.fetchone()
        
        if existing:
            session_id = existing[0]
            print(f"[test] ℹ️  Using existing test session (ID: {session_id})")
        else:
            cursor.execute(
                """INSERT INTO sessions (title, original_filename, stored_path, status, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                ("Test Session", "test.mp4", "/tmp/test.wav", "uploaded", now, now),
            )
            conn.commit()
            session_id = cursor.lastrowid
            print(f"[test] ✅ Created test session (ID: {session_id})")
        
        conn.close()
    except Exception as exc:
        print(f"[test] ❌ Failed to create session: {exc}")
        return False

    # Create test data
    transcript_text = "Have you ever wondered about cloud computing?"
    segments = [
        {"start": 0.0, "end": 4.34, "text": "Have you ever wondered"},
        {"start": 4.34, "end": 8.64, "text": "about cloud computing?"},
    ]
    try:
        save_transcript(session_id, transcript_text, segments)
        print(f"[test] ✅ Saved transcript for session {session_id}")
    except Exception as exc:
        print(f"[test] ❌ Failed to save transcript: {exc}")
        return False

    # Fetch transcript back
    print("[test] Step 3: Fetching transcript with segments...")
    try:
        result = fetch_transcript_by_session_id(session_id)
        if not result:
            print(f"[test] ❌ No transcript found for session {session_id}")
            return False
        print(f"[test] ✅ Retrieved transcript for session {session_id}")
    except Exception as exc:
        print(f"[test] ❌ Failed to fetch transcript: {exc}")
        return False

    # Verify transcript text
    print("[test] Step 4: Verifying transcript content...")
    if result["content"] != transcript_text:
        print(f"[test] ❌ Text mismatch!")
        print(f"     Expected: {transcript_text}")
        print(f"     Got:      {result['content']}")
        return False
    print(f"[test] ✅ Transcript text matches")

    # Verify segments are parsed correctly
    print("[test] Step 5: Verifying segments structure...")
    retrieved_segments = result.get("segments")
    if retrieved_segments is None:
        print(f"[test] ❌ No segments found in retrieved transcript")
        return False

    if not isinstance(retrieved_segments, list):
        print(f"[test] ❌ Segments is not a list: {type(retrieved_segments)}")
        return False

    if len(retrieved_segments) != len(segments):
        print(f"[test] ❌ Segment count mismatch!")
        print(f"     Expected: {len(segments)}")
        print(f"     Got:      {len(retrieved_segments)}")
        return False

    print(f"[test] ✅ Segments count matches ({len(retrieved_segments)})")

    # Verify each segment
    print("[test] Step 6: Verifying segment data...")
    for i, (expected, retrieved) in enumerate(zip(segments, retrieved_segments)):
        # Check if retrieved segment is a dict
        if not isinstance(retrieved, dict):
            print(f"[test] ❌ Segment {i} is not a dict: {type(retrieved)}")
            return False

        # Check each field
        for key in ["start", "end", "text"]:
            if key not in retrieved:
                print(f"[test] ❌ Segment {i} missing key '{key}'")
                return False

            if retrieved[key] != expected[key]:
                print(f"[test] ❌ Segment {i} field '{key}' mismatch!")
                print(f"     Expected: {expected[key]}")
                print(f"     Got:      {retrieved[key]}")
                return False

    print(f"[test] ✅ All segments verified")

    # Print final summary
    print("\n[test] ═══════════════════════════════════════")
    print("[test] 📝 Final Summary:")
    print(f"[test] Session ID: {session_id}")
    print(f"[test] Content: {result['content']}")
    print(f"[test] Segments: {len(retrieved_segments)} segments")
    for i, seg in enumerate(retrieved_segments, 1):
        print(f"[test]   {i}. [{seg['start']:.2f}s - {seg['end']:.2f}s] {seg['text']}")
    print("[test] ═══════════════════════════════════════")
    print("[test] ✅✅✅ End-to-end test PASSED")

    return True


if __name__ == "__main__":
    success = test_segments_persistence()
    sys.exit(0 if success else 1)
