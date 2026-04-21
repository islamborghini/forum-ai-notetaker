"""
Groq service layer.

Handles note generation from a transcript using the Groq API.
"""

import json
import logging
import os
import re
from typing import Optional

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

logger = logging.getLogger(__name__)

# Keep each Groq request well under the 12,000 TPM on_demand tier.
# Groq's tokenizer runs ~4 chars/token on English transcripts, so 20k chars
# ≈ 5k tokens of transcript plus a small scaffolding overhead per call.
_MAX_TRANSCRIPT_CHARS_PER_CHUNK = 20_000


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


def _split_transcript_into_chunks(
    transcript_text: str, max_chars: int = _MAX_TRANSCRIPT_CHARS_PER_CHUNK
) -> list[str]:
    """
    Split a transcript into chunks that each fit under the Groq TPM budget.

    Splits prefer paragraph boundaries, then sentence boundaries, so chunks
    stay semantically coherent for the per-chunk summarization step.
    """
    if len(transcript_text) <= max_chars:
        return [transcript_text]

    paragraphs = re.split(r"\n\s*\n", transcript_text.strip())
    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue

        candidate = f"{current}\n\n{paragraph}" if current else paragraph

        if len(candidate) <= max_chars:
            current = candidate
            continue

        if current:
            chunks.append(current)
            current = ""

        if len(paragraph) <= max_chars:
            current = paragraph
            continue

        # A single paragraph exceeds the budget — break it at sentence ends.
        sentences = re.split(r"(?<=[.!?])\s+", paragraph)
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            candidate = f"{current} {sentence}".strip() if current else sentence
            if len(candidate) <= max_chars:
                current = candidate
                continue

            if current:
                chunks.append(current)
            # Sentence itself may still exceed the cap; hard-split as a last resort.
            while len(sentence) > max_chars:
                chunks.append(sentence[:max_chars])
                sentence = sentence[max_chars:]
            current = sentence

    if current:
        chunks.append(current)

    return chunks


def _call_groq_for_chunk(client: Groq, chunk_text: str) -> dict:
    """
    Run one Groq completion over a single transcript chunk.
    """
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
                    f"Transcript:\n{chunk_text}"
                ),
            },
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content
    try:
        payload = json.loads(_strip_json_fences(content))
    except (json.JSONDecodeError, TypeError):
        logger.error(
            "Groq returned non-JSON content. finish_reason=%s raw=%r",
            getattr(response.choices[0], "finish_reason", None),
            content,
        )
        raise
    return _validate_notes_payload(payload)


_JSON_FENCE_RE = re.compile(r"^\s*```(?:json)?\s*|\s*```\s*$", re.IGNORECASE)


def _strip_json_fences(content: Optional[str]) -> str:
    """
    Remove ```json ... ``` fences that models sometimes wrap JSON in,
    even when asked for raw JSON.
    """
    if not content:
        return ""
    return _JSON_FENCE_RE.sub("", content).strip()


def _dedupe_preserving_order(items: list[str]) -> list[str]:
    """
    Remove case-insensitive duplicates while preserving first-seen order.
    """
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        key = item.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        result.append(item.strip())
    return result


def _merge_chunk_notes(chunk_notes: list[dict]) -> dict:
    """
    Combine per-chunk note payloads into a single notes payload.
    """
    summaries = [note["summary"].strip() for note in chunk_notes if note["summary"].strip()]
    topics: list[str] = []
    action_items: list[str] = []

    for note in chunk_notes:
        topics.extend(note["topics"])
        action_items.extend(note["action_items"])

    return {
        "summary": "\n\n".join(summaries),
        "topics": _dedupe_preserving_order(topics),
        "action_items": _dedupe_preserving_order(action_items),
    }


def generate_notes_from_transcript(transcript_text: str) -> dict:
    """
    Generate structured notes from a transcript using Groq.

    Long transcripts are split into chunks that each fit under the Groq
    per-minute token budget; per-chunk results are merged before return.
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set")

    client = Groq(api_key=api_key)
    chunks = _split_transcript_into_chunks(transcript_text)

    if len(chunks) == 1:
        return _call_groq_for_chunk(client, chunks[0])

    logger.info("Transcript too long for one Groq call; splitting into %d chunks", len(chunks))
    chunk_notes = [_call_groq_for_chunk(client, chunk) for chunk in chunks]
    return _merge_chunk_notes(chunk_notes)
