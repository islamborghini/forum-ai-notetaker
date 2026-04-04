"""Transcription step for the Sprint 1 pipeline.

This module loads Whisper base.en and returns transcript text for one audio file.
"""

from __future__ import annotations

from pathlib import Path

import whisper


def transcribe_audio(audio_path: str) -> str:
    """
    Transcribe an audio file to text using Whisper base.en.

    Args:
        audio_path: Path to input audio file (expected WAV for this pipeline).

    Returns:
        Transcript text as a string.

    Raises:
        FileNotFoundError: If input audio does not exist.
        RuntimeError: If Whisper model loading or transcription fails.
        ValueError: If audio_path is empty.
    """
    if not audio_path or not audio_path.strip():
        raise ValueError("audio_path cannot be empty.")

    audio_file = Path(audio_path).expanduser().resolve()

    if not audio_file.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_file}")
    if not audio_file.is_file():
        raise FileNotFoundError(f"Path is not a file: {audio_file}")

    try:
        # base.en is fast and good for English-only class recordings.
        model = whisper.load_model("base.en")
    except Exception as exc:
        raise RuntimeError(f"Failed to load Whisper model 'base.en': {exc}") from exc

    try:
        result = model.transcribe(str(audio_file))
    except Exception as exc:
        raise RuntimeError(f"Whisper transcription failed: {exc}") from exc

    text = (result or {}).get("text", "").strip()
    if not text:
        raise RuntimeError("Transcription completed but produced empty text.")

    return text
