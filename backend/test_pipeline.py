"""
Simple local test runner for Sprint 1 pipeline.

Usage:
    python3 backend/test_pipeline.py
"""

from __future__ import annotations

from pathlib import Path
import sys

# Make sure repo root is on sys.path so `backend.*` imports resolve
# whether this file is run from repo root or from inside `backend/`.
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.pipeline.process import process_recording


def main() -> None:
    """Run the Sprint 1 pipeline against one sample video file.

    Usage (from repo root):
        python3 backend/test_pipeline.py backend/uploads/Test.mp4
    """

    if len(sys.argv) != 2:
        print("Usage: python3 backend/test_pipeline.py <path-to-video-file>")
        print("Example: python3 backend/test_pipeline.py backend/uploads/Test.mp4")
        return

    video_path = sys.argv[1]

    print("[test_pipeline] Starting pipeline test...")
    print(f"[test_pipeline] Using video: {video_path}")

    try:
        transcript = process_recording(video_path)
        print("\n[test_pipeline] ✅ Pipeline completed successfully.")
        print("[test_pipeline] Transcript:\n")
        print(transcript)
    except Exception as exc:
        print("\n[test_pipeline] ❌ Pipeline failed.")
        print(f"[test_pipeline] Error: {exc}")
    print("\nDebug checklist:")
    print("1) Confirm the video path you passed in points to a real local file.")
    print("2) Run: ffmpeg -version")
    print("3) Confirm whisper is installed: python3 -m pip show openai-whisper")
    print("4) Re-run this script after fixing the issue.")


if __name__ == "__main__":
    main()
