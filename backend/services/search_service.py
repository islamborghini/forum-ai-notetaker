"""
Search service.

Provides search across session titles, transcript content, and
AI-generated notes, filtered to courses the authenticated user
is a member of.

This service delegates the database query to
`search_sessions_for_user` in the session service, then enriches
each result with metadata describing where the match occurred and,
when possible, short snippets from transcript or notes content.
"""

from services.session_service import search_sessions_for_user

_SNIPPET_RADIUS = 150
_MAX_QUERY_LENGTH = 200


def search(query: str, user_id: int) -> list[dict]:
    """
    Search sessions visible to the authenticated user.

    The query is matched against:
    - session title
    - transcript content
    - note summary
    - note topics
    - note action items

    Args:
        query: The search string entered by the user.
        user_id: The authenticated user's database ID.

    Returns:
        A list of enriched result dictionaries containing:
        - session_id
        - title
        - course_id
        - status
        - matched_in
        - transcript_snippet
        - notes_snippet

    Raises:
        ValueError: If the query exceeds the maximum allowed length.
    """
    query = query.strip()

    if not query:
        return []

    if len(query) > _MAX_QUERY_LENGTH:
        raise ValueError(f"Search query must be under {_MAX_QUERY_LENGTH} characters")

    sessions = search_sessions_for_user(user_id, query)
    return [_build_result(session, query) for session in sessions]


def _build_result(session: dict, query: str) -> dict:
    """
    Enrich a session dictionary with match metadata and readable snippets.

    Args:
        session: A session dictionary returned by `search_sessions_for_user`.
        query: The original search string.

    Returns:
        A dictionary describing where the match occurred and including
        transcript and notes snippets when available.
    """
    q = query.lower()
    title = session.get("title") or ""
    transcript_content = session.get("transcript_content") or ""
    notes_summary = session.get("notes_summary") or ""
    notes_topics = session.get("notes_topics") or ""
    notes_action_items = session.get("notes_action_items") or ""

    matched_in = []
    transcript_snippet = None
    notes_snippet = None

    if q in title.lower():
        matched_in.append("title")

    if q in transcript_content.lower():
        matched_in.append("transcript")
        transcript_snippet = _make_snippet(transcript_content, query)

    combined_notes = " ".join(
        part for part in [notes_summary, notes_topics, notes_action_items] if part
    )

    if combined_notes and q in combined_notes.lower():
        matched_in.append("notes")
        notes_snippet = _make_snippet(combined_notes, query)

    return {
        "id": session["id"],
        "session_id": session["id"],
        "title": title,
        "original_filename": session.get("original_filename"),
        "course_id": session.get("course_id"),
        "status": session.get("status"),
        "matched_in": matched_in,
        "transcript_snippet": transcript_snippet,
        "notes_snippet": notes_snippet,
    }


def _make_snippet(text: str, query: str) -> str:
    """
    Return a short snippet around the first match of the query.

    Args:
        text: The source text to extract a snippet from.
        query: The search string to locate.

    Returns:
        A trimmed snippet centered around the first match. If no match
        is found, returns the beginning of the text truncated to a
        reasonable length.
    """
    if not text:
        return ""

    lower_text = text.lower()
    lower_query = query.lower()
    match_index = lower_text.find(lower_query)

    if match_index == -1:
        return text[: _SNIPPET_RADIUS * 2].strip()

    start = max(0, match_index - _SNIPPET_RADIUS)
    end = min(len(text), match_index + len(query) + _SNIPPET_RADIUS)

    snippet = text[start:end].strip()

    if start > 0:
        snippet = "..." + snippet
    if end < len(text):
        snippet = snippet + "..."

    return snippet
