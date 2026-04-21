#!/usr/bin/env python3
"""
Integration test for the full pipeline with database persistence.

This test verifies the complete workflow:
1. Process a video file through the pipeline (extract audio → transcribe)
2. Save the transcript with segments to the database
3. Retrieve it back and verify segments are intact

Usage:
    cd backend
    python3 test_pipeline_integration.py ../uploads/Test.mp4
    
Or with a different video:
    python3 test_pipeline_integration.py /path/to/video.mp4
"""

import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from forum_ai_notetaker.db import init_db
from pipeline import process_recording
from services.transcript_service import save_transcript, fetch_transcript_by_session_id


def test_full_pipeline_integration():
    """Test full pipeline: process video → save with segments → retrieve."""
    if len(sys.argv) != 2:
        print("Usage: python3 test_pipeline_integration.py <video_path>")
        print("Example: python3 test_pipeline_integration.py ../uploads/Test.mp4")
        return False

    video_path = sys.argv[1]
    video_file = Path(video_path)

    if not video_file.exists():
        print(f"❌ Video file not found: {video_path}")
        return False

    print("[test] Starting full pipeline integration test...")
    print(f"[test] Video: {video_file.name}")

    # Initialize database
    print("[test] Step 1: Initializing database...")
    try:
        db_path = init_db()
        print(f"[test] ✅ Database ready")
    except Exception as exc:
        print(f"[test] ❌ Failed to initialize database: {exc}")
        return False

    # Create a test session
    print("[test] Step 2: Creating test session...")
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat() + "Z"

        cursor.execute(
            """INSERT INTO sessions (title, original_filename, stored_path, status, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                f"Pipeline Test - {video_file.name}",
                video_file.name,
                str(video_file),
                "processing",
                now,
                now,
            ),
        )
        conn.commit()
        session_id = cursor.lastrowid
        print(f"[test] ✅ Created session {session_id}")
        conn.close()
    except Exception as exc:
        print(f"[test] ❌ Failed to create session: {exc}")
        return False

    # Process video through pipeline
    print("[test] Step 3: Processing video through pipeline...")
    try:
        result = process_recording(str(video_file))
        print(f"[test] ✅ Pipeline processing complete")
    except Exception as exc:
        print(f"[test] ❌ Pipeline processing failed: {exc}")
        return False

    # Verify pipeline output structure
    print("[test] Step 4: Verifying pipeline output...")
    if not isinstance(result, dict):
        print(f"[test] ❌ Pipeline output is not a dict: {type(result)}")
        return False

    if "text" not in result:
        print(f"[test] ❌ Pipeline output missing 'text' key")
        return False

    if "segments" not in result:
        print(f"[test] ❌ Pipeline output missing 'segments' key")
        return False

    transcript_text = result["text"]
    segments = result["segments"]

    print(f"[test] ✅ Pipeline output valid")
    print(f"[test]    - Text length: {len(transcript_text)} characters")
    print(f"[test]    - Segments: {len(segments)}")

    # Save to database with segments
    print("[test] Step 5: Saving transcript with segments to database...")
    try:
        save_transcript(session_id, transcript_text, segments)
        print(f"[test] ✅ Saved to database")
    except Exception as exc:
        print(f"[test] ❌ Failed to save transcript: {exc}")
        return False

    # Retrieve from database
    print("[test] Step 6: Retrieving transcript from database...")
    try:
        retrieved = fetch_transcript_by_session_id(session_id)
        if not retrieved:
            print(f"[test] ❌ No transcript found for session {session_id}")
            return False
        print(f"[test] ✅ Retrieved from database")
    except Exception as exc:
        print(f"[test] ❌ Failed to retrieve transcript: {exc}")
        return False

    # Verify round-trip integrity
    print("[test] Step 7: Verifying data integrity...")

    # Check text
    if retrieved["content"] != transcript_text:
        print(f"[test] ❌ Text mismatch after round-trip")
        return False
    print(f"[test] ✅ Text integrity verified")

    # Check segments
    retrieved_segments = retrieved.get("segments")
    if retrieved_segments is None:
        print(f"[test] ❌ Segments missing from retrieved data")
        return False

    if len(retrieved_segments) != len(segments):
        print(f"[test] ❌ Segment count mismatch")
        return False

    print(f"[test] ✅ Segments integrity verified ({len(retrieved_segments)} segments)")

    # Print summary
    print("\n[test] ═══════════════════════════════════════════════════════")
    print("[test] 📊 Pipeline Integration Test Summary:")
    print(f"[test] Video: {video_file.name}")
    print(f"[test] Session ID: {session_id}")
    print(f"[test] Transcript length: {len(transcript_text)} characters")
    print(f"[test] Segments: {len(segments)}")
    if segments:
        print(f"[test] First segment: [{segments[0]['start']:.2f}s] {segments[0]['text'][:50]}...")
        if len(segments) > 1:
            print(f"[test] Last segment:  [{segments[-1]['start']:.2f}s] {segments[-1]['text'][:50]}...")
    print("[test] ═══════════════════════════════════════════════════════")
    print("[test] ✅✅✅ Pipeline Integration Test PASSED")

    return True


if __name__ == "__main__":
    success = test_full_pipeline_integration()
    sys.exit(0 if success else 1)
