from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "forum_ai_notetaker.sqlite3"
SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def resolve_db_path(db_path: str | Path | None = None) -> Path:
    path = Path(db_path) if db_path is not None else DEFAULT_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def init_db(db_path: str | Path | None = None) -> Path:
    path = resolve_db_path(db_path)
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    with sqlite3.connect(path) as connection:
        connection.execute("PRAGMA foreign_keys = ON;")
        connection.executescript(schema)
    return path


@contextmanager
def get_connection(db_path: str | Path | None = None) -> Iterator[sqlite3.Connection]:
    connection = sqlite3.connect(resolve_db_path(db_path))
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON;")
    try:
        yield connection
    finally:
        connection.close()
