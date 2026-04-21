"""
Pipeline trigger.

Entry point for the processing workflow after upload.
Extracts audio with FFmpeg, transcribes with Whisper,
generates notes with Groq, and saves the results.
"""

import logging
from pathlib import Path

from pipeline.audio import extract_audio
from pipeline.transcribe import transcribe_audio
from services.groq_service import generate_notes_from_transcript
from services.note_service import save_notes
from services.session_service import update_session_status
from services.transcript_service import save_transcript

logger = logging.getLogger(__name__)


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

    print(f"[STATUS] Session {session_id} → processing")
    update_session_status(session_id, "processing")

    try:
        absolute_recording_path = _resolve_recording_path(file_path)
        audio_path = extract_audio(absolute_recording_path)

        transcript_text, segments = transcribe_audio(audio_path)
        save_transcript(session_id, transcript_text, segments)

        print(f"[STATUS] Session {session_id} → transcribed")
        update_session_status(session_id, "transcribed")

        try:
            notes = generate_notes_from_transcript(transcript_text)
        except Exception:
            logger.exception(
                "Groq note generation failed for session %s", session_id
            )
            print(f"[STATUS] Session {session_id} → notes_failed")
            update_session_status(session_id, "notes_failed")
            return

        save_notes(
            session_id,
            notes["summary"],
            notes["topics"],
            notes["action_items"],
        )

        print(f"[STATUS] Session {session_id} → notes_generated")
        update_session_status(session_id, "notes_generated")

    except Exception:
        logger.exception("Pipeline failed for session %s", session_id)
        print(f"[STATUS] Session {session_id} → failed")
        update_session_status(session_id, "failed")


def run_pipeline_async(file_path: str, session_id: int, app) -> None:
    """
    Run the pipeline in a background thread.
    Wraps trigger_pipeline with error handling for async execution.
    """
    try:
        print(f"[PIPELINE] Running in background for session {session_id}...")
        with app.app_context():
            trigger_pipeline(file_path, session_id)
        print(f"[PIPELINE] Completed successfully for session {session_id}")
    except Exception as e:
        print(f"[ERROR] Background pipeline failed for session {session_id}: {e}")
