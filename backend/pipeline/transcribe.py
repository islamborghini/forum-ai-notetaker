"""Transcription step for the Sprint 1 pipeline.

This module loads Whisper base.en and returns transcript text and
timestamped segments for one audio file.
"""

from __future__ import annotations

from pathlib import Path

import whisper


def transcribe_audio(audio_path: str) -> tuple[str, list[dict]]:
    """
    Transcribe an audio file to text using Whisper base.en.

    Args:
        audio_path: Path to input audio file (expected WAV for this pipeline).

    Returns:
        A tuple of (transcript_text, segments), where each segment is a dict
        with keys ``start`` (float seconds), ``end`` (float seconds), and
        ``text`` (str).

    Raises:
        ValueError: If audio_path is empty or invalid.
        FileNotFoundError: If input audio does not exist.
        RuntimeError: If Whisper model loading or transcription fails.
    """
    # 1. Validate audio path
    if not audio_path or not audio_path.strip():
        raise ValueError("audio_path cannot be empty.")

    audio_file = Path(audio_path).expanduser().resolve()

    if not audio_file.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_file}")
    if not audio_file.is_file():
        raise FileNotFoundError(f"Path is not a file: {audio_file}")

    # 2. Load Whisper model
    try:
        # base.en is fast and good for English-only class recordings.
        model = whisper.load_model("base.en")
    except OSError as exc:
        # Typically happens if model download fails (network, disk space, etc.)
        raise RuntimeError(
            f"Failed to load Whisper model 'base.en': {exc}. "
            "Check your internet connection and ensure sufficient disk space (~140 MB)."
        ) from exc
    except Exception as exc:
        raise RuntimeError(f"Unexpected error loading Whisper model: {exc}") from exc

    # 3. Transcribe audio
    try:
        result = model.transcribe(str(audio_file))
    except MemoryError as exc:
        raise RuntimeError(
            f"Not enough memory to transcribe audio. "
            "Try a shorter audio file or close other applications."
        ) from exc
    except Exception as exc:
        error_msg = str(exc).lower()
        # Check for common resource issues
        if "cuda" in error_msg or "gpu" in error_msg:
            raise RuntimeError(
                f"GPU/CUDA error during transcription: {exc}. "
                "Try using CPU instead."
            ) from exc
        raise RuntimeError(f"Whisper transcription failed: {exc}") from exc

    # 4. Validate transcript result
    text = (result or {}).get("text", "").strip()
    if not text:
        raise RuntimeError(
            "Transcription completed but produced empty text. "
            "Check that the audio file contains audible speech."
        )

    raw_segments = (result or {}).get("segments") or []
    segments: list[dict] = []
    for seg in raw_segments:
        seg_text = (seg.get("text") or "").strip()
        if not seg_text:
            continue
        segments.append(
            {
                "start": float(seg.get("start", 0.0)),
                "end": float(seg.get("end", 0.0)),
                "text": seg_text,
            }
        )

    return text, segments
