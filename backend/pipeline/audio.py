"""Audio extraction step for the Sprint 1 pipeline.

This module takes a video path and creates a mono 16kHz WAV file using FFmpeg.
"""

from __future__ import annotations

import subprocess
from pathlib import Path


def extract_audio(video_path: str) -> str:
    """
    Extract audio from a video file and save as mono 16kHz WAV.

    Args:
        video_path: Path to the source video file.

    Returns:
        Path to the extracted WAV file as a string.

    Raises:
        FileNotFoundError: If input video does not exist.
        RuntimeError: If FFmpeg is not installed or extraction fails.
        ValueError: If video_path is empty.
    """
    if not video_path or not video_path.strip():
        raise ValueError("video_path cannot be empty.")

    video_file = Path(video_path).expanduser().resolve()

    if not video_file.exists():
        raise FileNotFoundError(f"Video file not found: {video_file}")
    if not video_file.is_file():
        raise FileNotFoundError(f"Path is not a file: {video_file}")

    # Save output in uploads/audio relative to this file's location.
    output_dir = Path(__file__).resolve().parent.parent / "uploads" / "audio"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_audio = output_dir / f"{video_file.stem}.wav"

    # FFmpeg command:
    # -y: overwrite output if exists
    # -i: input file
    # -ac 1: mono
    # -ar 16000: 16kHz sample rate
    command = [
        "ffmpeg",
        "-y",
        "-i",
    str(video_file),
        "-ac",
        "1",
        "-ar",
        "16000",
        str(output_audio),
    ]

    try:
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        # Happens if ffmpeg binary is missing
        raise RuntimeError(
            "FFmpeg not found. Please install FFmpeg and ensure it's on your PATH."
        ) from exc
    except subprocess.CalledProcessError as exc:
        error_message = exc.stderr.strip() or exc.stdout.strip() or str(exc)
        raise RuntimeError(f"FFmpeg failed to extract audio: {error_message}") from exc

    if not output_audio.exists():
        raise RuntimeError(
            "FFmpeg command completed but output audio file was not created."
        )

    return str(output_audio)
