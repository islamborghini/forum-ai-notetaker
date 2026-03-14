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


def process_recording(file_path: str) -> str:
    """
    Run the end-to-end Sprint 1 processing pipeline for one recording file.

    Args:
        file_path: Path to uploaded video file.

    Returns:
        Transcript text.

    Raises:
        RuntimeError: Wraps lower-level errors with pipeline context.
    """
    try:
        audio_path = extract_audio(file_path)
        transcript = transcribe_audio(audio_path)

       
        return transcript
    except Exception as exc:
        raise RuntimeError(f"Pipeline failed for '{file_path}': {exc}") from exc
