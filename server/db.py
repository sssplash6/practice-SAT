"""Storage. SQLite, because a diagnostic is a handful of rows per student."""

from __future__ import annotations

import json
import logging
import pathlib
import sqlite3
import threading

log = logging.getLogger("satf.db")

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
  id        TEXT PRIMARY KEY,
  kind      TEXT NOT NULL DEFAULT 'diagnostic',
  form_id   INTEGER,          -- diagnostics: which of the ten forms
  questions TEXT,             -- practice: the built set, key included
  learner   TEXT,             -- who this counts against for repetition
  started   TEXT NOT NULL,
  finished  TEXT,
  answers   TEXT NOT NULL DEFAULT '{}',
  result    TEXT,
  user_id   TEXT REFERENCES users(id)
);

-- Every question a learner has been given, so the next set is not the last one
-- again. The stem hash is carried as well as the seed because two seeds can
-- land on the same question.
CREATE TABLE IF NOT EXISTS practice_seen (
  learner  TEXT NOT NULL,
  template TEXT NOT NULL,
  seed     INTEGER NOT NULL,
  stem     TEXT NOT NULL,
  at       TEXT NOT NULL,
  PRIMARY KEY (learner, template, seed)
);

CREATE INDEX IF NOT EXISTS sessions_user  ON sessions(user_id);
CREATE INDEX IF NOT EXISTS users_token    ON users(token);
CREATE INDEX IF NOT EXISTS seen_learner   ON practice_seen(learner);

-- A learner is whoever holds the token in their browser. Everything below is
-- optional: a student who never opens the profile still gets a map and a coach.
CREATE TABLE IF NOT EXISTS learners (
  id         TEXT PRIMARY KEY,
  name       TEXT,
  exam_date  TEXT,            -- YYYY-MM-DD
  target     INTEGER,         -- a Math section score, 200-800
  minutes    INTEGER,         -- a study day's length
  days       TEXT,            -- which weekdays are study days, Monday first: "1111100"
  created    TEXT NOT NULL,
  updated    TEXT
);

-- Every answer, from every mode. Mastery, open mistakes, streaks and the week
-- are all derived from this, so nothing about a student is stored twice.
CREATE TABLE IF NOT EXISTS attempts (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  learner    TEXT NOT NULL,
  session    TEXT,
  qid        TEXT,
  template   TEXT NOT NULL,
  seed       INTEGER NOT NULL,
  topic      TEXT NOT NULL,
  difficulty TEXT NOT NULL,
  fmt        TEXT NOT NULL,
  correct    INTEGER NOT NULL,
  reason     TEXT,            -- the mistake the chosen option names, when wrong
  given      TEXT,
  ms         INTEGER,
  at         TEXT NOT NULL
);

-- An open mistake: a template a learner fell for, and the misconception the
-- option they picked names. It closes after `owed` clean answers on the same
-- template, which is what the repair questions are for.
CREATE TABLE IF NOT EXISTS traps (
  learner    TEXT NOT NULL,
  template   TEXT NOT NULL,
  reason     TEXT NOT NULL,   -- '' for a missed grid-in, which names no mistake
  label      TEXT NOT NULL,   -- what to call it: the reason, or the skill
  topic      TEXT NOT NULL,
  hits       INTEGER NOT NULL DEFAULT 1,
  owed       INTEGER NOT NULL,
  opened     TEXT NOT NULL,
  last       TEXT NOT NULL,
  closed     TEXT,
  PRIMARY KEY (learner, template, reason)
);

-- A question kept to see again, addressed by the triple that regenerates it.
CREATE TABLE IF NOT EXISTS saved (
  learner    TEXT NOT NULL,
  template   TEXT NOT NULL,
  seed       INTEGER NOT NULL,
  topic      TEXT NOT NULL,
  at         TEXT NOT NULL,
  PRIMARY KEY (learner, template, seed)
);

-- The day's challenge, built once so every student sits the same ten.
CREATE TABLE IF NOT EXISTS challenges (
  day        TEXT PRIMARY KEY,
  questions  TEXT NOT NULL,
  built      TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS attempts_learner ON attempts(learner, topic, id);
CREATE INDEX IF NOT EXISTS attempts_session ON attempts(session);
CREATE INDEX IF NOT EXISTS traps_open       ON traps(learner, closed);
"""

# Columns added after the first release. sqlite has no ADD COLUMN IF NOT EXISTS,
# so the existing shape is read and the gaps filled.
LATER_COLUMNS = (
    ("sessions", "kind", "TEXT NOT NULL DEFAULT 'diagnostic'"),
    ("sessions", "questions", "TEXT"),
    ("sessions", "learner", "TEXT"),
    ("sessions", "mock_id", "TEXT"),        # "1.3", the cassette
    ("sessions", "module", "INTEGER"),      # 1 or 2, which one is live
    ("sessions", "route", "TEXT"),          # "lower" or "upper", set after module 1
    ("sessions", "module1", "TEXT"),        # what module 1 was marked at
    ("sessions", "module_started", "TEXT"), # the live module's clock, not the session's
    ("sessions", "cfg", "TEXT"),            # a drill's settings and its moving parts
    ("sessions", "day", "TEXT"),            # a challenge's date
)

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
    c = conn()
    c.executescript(SCHEMA)
    for table, column, decl in LATER_COLUMNS:
        have = {r["name"] for r in c.execute(f"PRAGMA table_info({table})")}
        if column not in have:
            c.execute(f"ALTER TABLE {table} ADD COLUMN {column} {decl}")
    _relax_form_id(c)
    c.commit()


def _relax_form_id(c: sqlite3.Connection) -> None:
    """Practice sessions have no form, and the first schema said form_id was
    required. sqlite cannot drop a NOT NULL in place, so the table is rebuilt:
    make the new shape, copy the rows over, swap the names. Rows are kept --
    a student who sat a diagnostic should not lose it to a schema change.
    """
    cols = {r["name"]: r for r in c.execute("PRAGMA table_info(sessions)")}
    if not cols or not cols.get("form_id", {})["notnull"]:
        return
    keep = [n for n in ("id", "kind", "form_id", "questions", "learner",
                        "started", "finished", "answers", "result", "user_id")
            if n in cols]
    names = ", ".join(keep)
    c.executescript(f"""
      PRAGMA foreign_keys=OFF;
      CREATE TABLE sessions_new (
        id        TEXT PRIMARY KEY,
        kind      TEXT NOT NULL DEFAULT 'diagnostic',
        form_id   INTEGER,
        questions TEXT,
        learner   TEXT,
        started   TEXT NOT NULL,
        finished  TEXT,
        answers   TEXT NOT NULL DEFAULT '{{}}',
        result    TEXT,
        user_id   TEXT REFERENCES users(id)
      );
      INSERT INTO sessions_new ({names}) SELECT {names} FROM sessions;
      DROP TABLE sessions;
      ALTER TABLE sessions_new RENAME TO sessions;
      CREATE INDEX IF NOT EXISTS sessions_user ON sessions(user_id);
      PRAGMA foreign_keys=ON;
    """)
    log.info("rebuilt sessions so a practice set can exist without a form")


def seen_for(learner: str) -> tuple[set[tuple[str, int]], set[str]]:
    """Everything this learner has already been shown."""
    rows = conn().execute(
        "SELECT template, seed, stem FROM practice_seen WHERE learner=?", (learner,)
    ).fetchall()
    return {(r["template"], r["seed"]) for r in rows}, {r["stem"] for r in rows}


def remember(learner: str, items, when: str) -> None:
    """Record a whole set at once; a re-served set must not fail on the key."""
    conn().executemany(
        "INSERT OR IGNORE INTO practice_seen (learner, template, seed, stem, at)"
        " VALUES (?,?,?,?,?)",
        [(learner, q["key"], q["seed"], q["stem_hash"], when) for q in items],
    )
    conn().commit()


def one(sql: str, *args) -> sqlite3.Row | None:
    return conn().execute(sql, args).fetchone()


def rows(sql: str, *args) -> list[sqlite3.Row]:
    return conn().execute(sql, args).fetchall()


def run(sql: str, *args) -> sqlite3.Cursor:
    cur = conn().execute(sql, args)
    conn().commit()
    return cur


def load_answers(row) -> dict:
    return json.loads(row["answers"] or "{}")


def save_answers(session_id: str, answers: dict) -> None:
    run("UPDATE sessions SET answers=? WHERE id=?", json.dumps(answers), session_id)
