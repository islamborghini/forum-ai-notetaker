"""
Validation helpers.

I kept validation separate so the routes stay focused on
workflow logic instead of being cluttered with repeated checks.
"""

import re

ALLOWED_EXTENSIONS = {"mp4", "mp3", "wav", "m4a"}


def allowed_file(filename: str) -> bool:
    """
    Check whether an uploaded file has a supported extension.
    """
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def safe_filename(filename: str) -> str:
    """
    Clean a filename so it is safe to store locally.

    I am not using werkzeug here just to keep this version
    simple and self-contained.
    """
    filename = filename.strip().replace(" ", "_")
    filename = re.sub(r"[^A-Za-z0-9_.-]", "", filename)
    return filename