"""Storage. SQLite, because a diagnostic is a handful of rows per student."""

from __future__ import annotations

import json
import pathlib
import sqlite3
import threading

DB_PATH = pathlib.Path(__file__).resolve().parent / "satfreshman.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
  id         TEXT PRIMARY KEY,
  first      TEXT NOT NULL,
  last       TEXT NOT NULL,
  email      TEXT NOT NULL UNIQUE,
  verified   INTEGER NOT NULL DEFAULT 0,
  token      TEXT,
  token_sent TEXT,
  created    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
  id       TEXT PRIMARY KEY,
  form_id  INTEGER NOT NULL,
  started  TEXT NOT NULL,
  finished TEXT,
  answers  TEXT NOT NULL DEFAULT '{}',
  result   TEXT,
  user_id  TEXT REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS sessions_user ON sessions(user_id);
CREATE INDEX IF NOT EXISTS users_token   ON users(token);
"""

_local = threading.local()


def conn() -> sqlite3.Connection:
    """One connection per thread: sqlite objects do not cross threads."""
    c = getattr(_local, "c", None)
    if c is None:
        c = sqlite3.connect(DB_PATH)
        c.row_factory = sqlite3.Row
        c.execute("PRAGMA journal_mode=WAL")
        c.execute("PRAGMA foreign_keys=ON")
        _local.c = c
    return c


def init() -> None:
    conn().executescript(SCHEMA)
    conn().commit()


def one(sql: str, *args) -> sqlite3.Row | None:
    return conn().execute(sql, args).fetchone()


def run(sql: str, *args) -> sqlite3.Cursor:
    cur = conn().execute(sql, args)
    conn().commit()
    return cur


def load_answers(row) -> dict:
    return json.loads(row["answers"] or "{}")


def save_answers(session_id: str, answers: dict) -> None:
    run("UPDATE sessions SET answers=? WHERE id=?", json.dumps(answers), session_id)
