"""Simple orchestration for the Sprint 1 recording pipeline.

Flow:
1) Extract audio from uploaded video
2) Transcribe extracted audio
3) Return transcript text

Database integration is intentionally deferred for Sprint 1.
"""

from __future__ import annotations

from .audio import extract_audio
from .transcribe import transcribe_audio


def process_recording(file_path: str) -> tuple[str, list[dict]]:
    """
    Run the end-to-end Sprint 1 processing pipeline for one recording file.

    Args:
        file_path: Path to uploaded video file.

    Returns:
        A tuple of (transcript_text, segments).

    Raises:
        ValueError: If file_path is invalid.
        FileNotFoundError: If input video does not exist.
        RuntimeError: If any pipeline step fails.
    """
    # Step 1: Extract audio
    try:
        audio_path = extract_audio(file_path)
    except (ValueError, FileNotFoundError) as exc:
        # Re-raise path validation errors as-is
        raise
    except RuntimeError as exc:
        raise RuntimeError(f"Audio extraction failed: {exc}") from exc

    # Step 2: Transcribe audio
    try:
        transcript, segments = transcribe_audio(audio_path)
    except (ValueError, FileNotFoundError) as exc:
        # Re-raise path validation errors as-is
        raise
    except RuntimeError as exc:
        raise RuntimeError(f"Transcription failed: {exc}") from exc

    return transcript, segments
