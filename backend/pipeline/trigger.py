"""
Pipeline trigger.

My role here is not to implement FFmpeg, Whisper, or Groq.
My role is to make sure the backend has a clean entry point
for the processing workflow after upload.

Right now this is mocked so the entire backend can still be
tested end-to-end during MVP 1.
"""

from services.session_service import update_session_status
from services.transcript_service import save_transcript
from services.note_service import save_notes


def trigger_pipeline(file_path: str, session_id: int) -> None:
    """
    Trigger the processing workflow for an uploaded recording.

    Current mocked flow:
    upload -> processing -> transcript saved -> notes saved
    """

    # As soon as the backend hands the file off, the session
    # should stop looking merely "uploaded" and start looking
    # like it is actually being worked on.
    update_session_status(session_id, "processing")

    # Placeholder transcript.
    transcript_text = f"Mock transcript generated from {file_path}"

    # Placeholder note output.
    summary = "Mock summary for this lecture."
    topics = ["Mock topic 1", "Mock topic 2"]
    action_items = ["Mock action item 1", "Mock action item 2"]

    save_transcript(session_id, transcript_text)
    save_notes(session_id, summary, topics, action_items)

    # Once everything is saved, we mark the session as done.
    update_session_status(session_id, "notes_generated")