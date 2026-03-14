from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import BinaryIO
from uuid import uuid4

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_UPLOAD_ROOT = PROJECT_ROOT / "uploads"


def resolve_upload_root(upload_root: str | Path | None = None) -> Path:
    root = Path(upload_root) if upload_root is not None else DEFAULT_UPLOAD_ROOT
    root.mkdir(parents=True, exist_ok=True)
    return root


def _sanitize_filename(original_filename: str) -> tuple[str, str]:
    filename = Path(original_filename or "upload").name
    stem = re.sub(r"[^A-Za-z0-9._-]+", "-", Path(filename).stem).strip("-._")
    suffix = Path(filename).suffix.lower() or ".bin"
    return (stem or "recording", suffix)


def build_upload_path(
    original_filename: str,
    *,
    session_id: int | None = None,
    upload_root: str | Path | None = None,
) -> Path:
    root = resolve_upload_root(upload_root)
    stem, suffix = _sanitize_filename(original_filename)
    folder_name = str(session_id) if session_id is not None else "pending"
    destination_dir = root / folder_name
    destination_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{stem}-{uuid4().hex[:12]}{suffix}"
    return destination_dir / filename


def save_uploaded_file(
    uploaded_file: BinaryIO | object,
    *,
    session_id: int | None = None,
    upload_root: str | Path | None = None,
) -> str:
    original_filename = getattr(uploaded_file, "filename", None) or "upload"
    destination = build_upload_path(
        original_filename,
        session_id=session_id,
        upload_root=upload_root,
    )

    if hasattr(uploaded_file, "save"):
        uploaded_file.save(destination)
    else:
        stream = getattr(uploaded_file, "stream", uploaded_file)
        if hasattr(stream, "seek"):
            stream.seek(0)
        with destination.open("wb") as target:
            shutil.copyfileobj(stream, target)

    try:
        return destination.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return destination.as_posix()
