"""
Groq service layer.

Handles note generation from a transcript using the Groq API.
"""

import json
import os
import re

from dotenv import load_dotenv
from groq import Groq

load_dotenv()


def _validate_notes_payload(payload: dict) -> dict:
    """
    Validate the generated notes payload before saving it.
    """
    summary = payload.get("summary")
    topics = payload.get("topics")
    action_items = payload.get("action_items")

    if not isinstance(summary, str):
        raise RuntimeError("Groq response must include a string summary")

    if not isinstance(topics, list) or not all(isinstance(item, str) for item in topics):
        raise RuntimeError("Groq response topics must be a list of strings")

    if not isinstance(action_items, list) or not all(
        isinstance(item, str) for item in action_items
    ):
        raise RuntimeError("Groq response action_items must be a list of strings")

    return {
        "summary": summary,
        "topics": topics,
        "action_items": action_items,
    }


def generate_fallback_notes(transcript_text: str) -> dict:
    """
    Generate a basic summary when Groq note generation fails.
    """
    paragraphs = [paragraph.strip() for paragraph in transcript_text.splitlines() if paragraph.strip()]
    summary_sentences = []

    for paragraph in paragraphs:
        sentence_parts = re.split(r"(?<=[.!?])\s+", paragraph, maxsplit=1)
        first_sentence = sentence_parts[0].strip()
        if first_sentence and first_sentence[-1] not in ".!?":
            first_sentence = f"{first_sentence}."
        if first_sentence:
            summary_sentences.append(first_sentence)

    summary = " ".join(summary_sentences).strip()
    if not summary:
        summary = transcript_text.strip()

    return {
        "summary": summary,
        "topics": [],
        "action_items": [],
    }


def generate_notes_from_transcript(transcript_text: str) -> dict:
    """
    Generate structured notes from a transcript using Groq.
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set")

    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "You convert lecture transcripts into structured study notes."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Return valid JSON only with this exact shape:\n"
                    "{\n"
                    '  "summary": "string",\n'
                    '  "topics": ["string"],\n'
                    '  "action_items": ["string"]\n'
                    "}\n\n"
                    f"Transcript:\n{transcript_text}"
                ),
            },
        ],
        temperature=0.2,
    )

    content = response.choices[0].message.content
    payload = json.loads(content)
    return _validate_notes_payload(payload)
