"""
Pipeline trigger.

Entry point for the processing workflow after upload.
Extracts audio with FFmpeg, transcribes with Whisper,
generates notes with Groq, and saves the results.
"""

from pathlib import Path

from pipeline.audio import extract_audio
from pipeline.transcribe import transcribe_audio
from services.groq_service import (
    generate_fallback_notes,
    generate_notes_from_transcript,
)
from services.note_service import save_notes
from services.session_service import update_session_status
from services.transcript_service import save_transcript


def _resolve_recording_path(file_path: str) -> str:
    """Resolve a stored recording path to an absolute filesystem path."""
    path = Path(file_path).expanduser()
    if path.is_absolute():
        return str(path.resolve())

    backend_root = Path(__file__).resolve().parent.parent
    return str((backend_root / path).resolve())


def trigger_pipeline(file_path: str, session_id: int) -> None:
    """
    Trigger the processing workflow for an uploaded recording.

    Flow: upload -> extract audio -> transcribe -> save transcript
    -> generate notes -> save notes
    """

    update_session_status(session_id, "processing")

    try:
        absolute_recording_path = _resolve_recording_path(file_path)
        audio_path = extract_audio(absolute_recording_path)
        transcript_text = transcribe_audio(audio_path)
        save_transcript(session_id, transcript_text)

        try:
            notes = generate_notes_from_transcript(transcript_text)
        except Exception as exc:
            print(
                f"Groq note generation failed for session {session_id}: {exc}. "
                "Using fallback summary generation."
            )
            notes = generate_fallback_notes(transcript_text)

        save_notes(
            session_id,
            notes["summary"],
            notes["topics"],
            notes["action_items"],
        )
        update_session_status(session_id, "notes_generated")
    except Exception as exc:
        print(f"Pipeline failed for session {session_id}: {exc}")
        update_session_status(session_id, "failed")
