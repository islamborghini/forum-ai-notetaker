#!/usr/bin/env python3
"""
Test script for Whisper error handling improvements.

This tests various error scenarios to ensure error messages are clear and helpful.

Usage:
    python3 backend/test_whisper_errors.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add repo root to path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.pipeline.transcribe import transcribe_audio
from backend.pipeline.audio import extract_audio


def test_error_scenario(name: str, test_func) -> bool:
    """Run a test scenario and report results."""
    print(f"\n{'='*60}")
    print(f"Test: {name}")
    print('='*60)
    try:
        test_func()
        print("❌ FAILED: Expected an error but none was raised")
        return False
    except Exception as exc:
        error_type = type(exc).__name__
        error_msg = str(exc)
        print(f"✅ PASSED: Caught {error_type}")
        print(f"   Message: {error_msg}")
        return True


def test_missing_audio_file():
    """Test: Missing or invalid audio file path."""
    transcribe_audio("/nonexistent/path/audio.wav")


def test_empty_audio_path():
    """Test: Empty audio path."""
    transcribe_audio("")


def test_empty_video_path():
    """Test: Empty video path."""
    extract_audio("")


def test_missing_video_file():
    """Test: Missing video file."""
    extract_audio("/nonexistent/path/video.mp4")


def main() -> None:
    """Run all error handling tests."""
    print("\n" + "="*60)
    print("Whisper Error Handling Test Suite")
    print("="*60)

    tests = [
        ("Missing audio file", test_missing_audio_file),
        ("Empty audio path", test_empty_audio_path),
        ("Missing video file", test_missing_video_file),
        ("Empty video path", test_empty_video_path),
    ]

    results = []
    for name, test_func in tests:
        passed = test_error_scenario(name, test_func)
        results.append((name, passed))

    # Summary
    print(f"\n{'='*60}")
    print("Test Summary")
    print('='*60)
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    print(f"Passed: {passed_count}/{total_count}")
    for name, passed in results:
        status = "✅" if passed else "❌"
        print(f"  {status} {name}")

    # Notes on model loading and transcription
    print(f"\n{'='*60}")
    print("Note on Model Loading & Transcription Tests")
    print('='*60)
    print("""
These require actual files and model download:
  - Model load failure: Happens with network issues or disk space
  - Transcription failure: Happens with corrupted audio or resource limits
  - Empty transcript: Happens with silent audio

To test these manually:
  1. Run: python3 backend/test_pipeline.py <video>
  2. Observe error messages for helpful guidance
  3. Check messages mention disk space, memory, GPU issues
""")

    return 0 if passed_count == total_count else 1


if __name__ == "__main__":
    sys.exit(main())
