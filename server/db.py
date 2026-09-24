"""Storage. SQLite, because a diagnostic is a handful of rows per student."""

from __future__ import annotations

import json
import logging
import os
import pathlib
import re
import secrets
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timezone

log = logging.getLogger("satf.db")

# SATF_DB points a worktree's server at its own file; the default is the dev database
DB_PATH = pathlib.Path(os.environ.get("SATF_DB") or pathlib.Path(__file__).resolve().parent / "satfreshman.db")

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
    ("sessions", "qstate", "TEXT DEFAULT '{}'"),
    ("sessions", "paused_at", "TEXT"), ("sessions", "paused_ms", "INTEGER DEFAULT 0"),
    ("sessions", "pauses", "INTEGER DEFAULT 0"), ("sessions", "abandoned", "TEXT"),
    ("sessions", "number", "INTEGER"), ("sessions", "note", "TEXT"),
    ("sessions", "shared_from", "TEXT"), ("sessions", "contest", "TEXT"),
    ("sessions", "ranked", "INTEGER DEFAULT 1"), ("sessions", "points", "INTEGER"),
    ("sessions", "secs", "INTEGER"), ("sessions", "unranked_why", "TEXT"),
    ("learners", "current", "INTEGER"),     # the Math score the student starts the plan from
    ("learners", "tests", "TEXT"),          # "weekly" (the default) or "daily"
    ("learners", "focus", "TEXT"),          # JSON: domain -> "focus" or "strong"; the rest are normal
    ("learners", "avatar", "TEXT"), ("learners", "prefs", "TEXT"),
    ("learners", "board", "TEXT"), ("learners", "country", "TEXT"),
    ("learners", "ach_seen", "TEXT"), ("learners", "rw_now", "INTEGER"),
    ("learners", "rw_target", "INTEGER"), ("learners", "plan", "TEXT"),
    ("learners", "plan_draft", "TEXT"), ("learners", "rating", "REAL DEFAULT 1000"),
    ("learners", "rated", "INTEGER DEFAULT 0"),
    ("users", "learner", "TEXT"), ("users", "login_token", "TEXT"),
    ("users", "login_code", "TEXT"), ("users", "login_for", "TEXT"),
    ("users", "login_sent", "TEXT"), ("users", "login_tries", "INTEGER DEFAULT 0"),
    ("users", "last_login", "TEXT"),
    ("attempts", "norm", "TEXT"), ("attempts", "repeat", "INTEGER NOT NULL DEFAULT 0"),
    ("attempts", "repair", "INTEGER NOT NULL DEFAULT 0"),
    ("attempts", "flagged", "INTEGER NOT NULL DEFAULT 0"),
    ("attempts", "guess", "INTEGER NOT NULL DEFAULT 0"),
    ("attempts", "disputed", "INTEGER NOT NULL DEFAULT 0"),
    ("attempts", "sms", "INTEGER"), ("attempts", "void", "TEXT"),
    ("attempts", "stem", "TEXT"),
    ("saved", "session", "TEXT"), ("saved", "qid", "TEXT"),
    # the upgrades (spec/v2-upgrades/*.md §3.2 rows); tables created in
    # EXTRA_SCHEMA are altered too, because it runs before this list
    ("attempts", "conf", "TEXT"),                               # sure | unsure | guess | null
    ("attempts", "hints", "INTEGER NOT NULL DEFAULT 0"),
    ("attempts", "miss_kind", "TEXT"),                          # the student's own cause (P8)
    ("attempts", "offered", "TEXT"),                            # JSON norms of the named options shown (P6)
    ("attempts", "struck", "TEXT"),                             # JSON indices struck before answering
    ("attempts", "cover", "INTEGER NOT NULL DEFAULT 0"),
    ("attempts", "calc", "INTEGER NOT NULL DEFAULT 0"),
    ("attempts", "diag", "TEXT"), ("attempts", "revealed_at", "TEXT"),
    ("attempts", "word", "TEXT"),                               # an R&W item's word (R57)
    ("attempts", "source", "TEXT"),                             # 'second' for a second look
    ("tries", "hints", "INTEGER DEFAULT 0"),
    ("pairs", "dir", "TEXT"), ("pairs", "token", "TEXT"), ("pairs", "approver", "TEXT"),
    ("pairs", "session_only", "INTEGER DEFAULT 0"),
    ("reports", "parent", "INTEGER"), ("reports", '"check"', "TEXT"),
    ("outside_scores", "misses", "TEXT"), ("outside_scores", "subject", "TEXT NOT NULL DEFAULT 'math'"),
    ("learners", "feed_seen", "TEXT"), ("learners", "handle", "TEXT"),
    ("learners", "swap_until", "TEXT"),
    ("users", "google_sub", "TEXT"),
    ("saved", "why", "TEXT"),
    ("sessions", "subject", "TEXT NOT NULL DEFAULT 'math'"),
    ("papers", "source", "TEXT"),
    ("contests", "subject", "TEXT DEFAULT 'math'"), ("contests", "series", "TEXT"),
    ("contests", "round", "INTEGER"),
    ("contest_items", "slot", "INTEGER"), ("contest_items", "qhash", "TEXT"),
    ("plans", "start_points", "TEXT"), ("plan_days", "gate", "INTEGER DEFAULT 0"),
    ("plan_overrides", "trim", "INTEGER DEFAULT 0"),
    ("plan_marks", "minutes", "INTEGER"), ("plan_marks", "note", "TEXT"),
    ("plan_tasks", "type", "TEXT DEFAULT 'other'"), ("plan_tasks", "subject", "TEXT DEFAULT 'math'"),
    ("word_state", "hook", "TEXT"), ("word_state", "proven", "INTEGER"),
    ("word_state", "placed", "INTEGER"),
    ("word_reviews", "template", "TEXT"), ("word_reviews", "seed", "INTEGER"),
    ("word_reviews", "trap", "TEXT"), ("word_reviews", "conf", "TEXT"),
    ("word_reviews", "gap", "TEXT"), ("word_reviews", "subject", "TEXT"),
    ("word_reviews", "skill", "TEXT"), ("word_reviews", "domain", "TEXT"),
    ("word_reviews", "difficulty", "TEXT"), ("word_reviews", "attempt", "INTEGER"),
    ("trap_log", "undoes", "INTEGER"),      # a discarded / restored row: the trap_log id it undoes (V13)
)

EXTRA_SCHEMA = """
CREATE TABLE IF NOT EXISTS flags (learner TEXT, session TEXT, qid TEXT, template TEXT, seed INTEGER, topic TEXT, at TEXT, PRIMARY KEY(learner,session,qid));
CREATE TABLE IF NOT EXISTS notes (learner TEXT, template TEXT, seed INTEGER, note TEXT, marks TEXT, at TEXT, PRIMARY KEY(learner,template,seed));
CREATE TABLE IF NOT EXISTS links (token TEXT PRIMARY KEY, learner TEXT, kind TEXT, created TEXT, revoked TEXT, views INTEGER DEFAULT 0, last_view TEXT);
CREATE TABLE IF NOT EXISTS pairs (code TEXT PRIMARY KEY, learner TEXT, created TEXT, expires TEXT, used TEXT, req_learner TEXT, req_device TEXT, req_answers INTEGER, state TEXT DEFAULT 'open');
CREATE TABLE IF NOT EXISTS retired (code TEXT PRIMARY KEY, "into" TEXT, at TEXT);
CREATE TABLE IF NOT EXISTS reports (id INTEGER PRIMARY KEY AUTOINCREMENT, learner TEXT, kind TEXT, source TEXT, session TEXT, qid TEXT, paper TEXT, word TEXT, template TEXT, seed INTEGER, category TEXT, title TEXT, answer TEXT, given TEXT, details TEXT, context TEXT, device TEXT, email TEXT, files TEXT, dispute INTEGER DEFAULT 0, at TEXT, status TEXT DEFAULT 'new', reply TEXT, replied TEXT, seen TEXT);
CREATE TABLE IF NOT EXISTS sets (code TEXT PRIMARY KEY, owner TEXT, kind TEXT, session TEXT, items TEXT, cfg TEXT, title TEXT, show_score INTEGER DEFAULT 1, show_name INTEGER DEFAULT 0, created TEXT, revoked TEXT);
CREATE TABLE IF NOT EXISTS earned (learner TEXT, id TEXT, tier INTEGER, at TEXT, PRIMARY KEY(learner,id,tier));
CREATE TABLE IF NOT EXISTS tries (learner TEXT, session TEXT, qid TEXT, n INTEGER, given TEXT, correct INTEGER, reason TEXT, ms INTEGER, at TEXT);
CREATE TABLE IF NOT EXISTS outside_scores (id TEXT PRIMARY KEY, learner TEXT, day TEXT, math INTEGER, rw INTEGER, source TEXT, at TEXT);
CREATE TABLE IF NOT EXISTS plans (id TEXT PRIMARY KEY, learner TEXT, name TEXT, cfg TEXT, start TEXT, tz INTEGER, start_mastery TEXT, created TEXT, updated TEXT, archived TEXT, result TEXT, drift_seen TEXT);
CREATE TABLE IF NOT EXISTS plan_days (plan TEXT, day TEXT, kind TEXT, minutes INTEGER, test TEXT, phase TEXT, tasks TEXT, PRIMARY KEY(plan,day));
CREATE TABLE IF NOT EXISTS plan_overrides (plan TEXT, day TEXT, minutes INTEGER, off INTEGER DEFAULT 0, test TEXT, topics TEXT, PRIMARY KEY(plan,day));
CREATE TABLE IF NOT EXISTS plan_tasks (id TEXT PRIMARY KEY, plan TEXT, day TEXT, repeat TEXT, title TEXT, minutes INTEGER, created TEXT, removed TEXT);
CREATE TABLE IF NOT EXISTS plan_marks (plan TEXT, day TEXT, task TEXT, status TEXT, to_day TEXT, at TEXT, PRIMARY KEY(plan,day,task));
CREATE TABLE IF NOT EXISTS papers (n INTEGER PRIMARY KEY, week TEXT UNIQUE, label TEXT, built TEXT, questions TEXT);
CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY, paper INTEGER, learner TEXT, name TEXT, at TEXT, edited TEXT, parent INTEGER, about TEXT, text TEXT, helpful INTEGER DEFAULT 0, reports INTEGER DEFAULT 0, hidden INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS post_votes (post INTEGER, learner TEXT, kind TEXT, PRIMARY KEY(post,learner,kind));
CREATE TABLE IF NOT EXISTS contests (id TEXT PRIMARY KEY, kind TEXT, title TEXT, owner TEXT, code TEXT UNIQUE, opens TEXT, closes TEXT, count INTEGER, seconds INTEGER, spec TEXT, questions TEXT, created TEXT);
CREATE TABLE IF NOT EXISTS contest_items (contest TEXT, template TEXT, seed INTEGER, PRIMARY KEY(contest,template,seed));
CREATE TABLE IF NOT EXISTS contest_members (contest TEXT, learner TEXT, joined TEXT, PRIMARY KEY(contest,learner));
CREATE TABLE IF NOT EXISTS item_ratings (template TEXT, tier TEXT, rating REAL, n INTEGER, PRIMARY KEY(template,tier));
CREATE TABLE IF NOT EXISTS name_reports (target TEXT, reporter TEXT, at TEXT, PRIMARY KEY(target,reporter));
CREATE TABLE IF NOT EXISTS seasons (id TEXT PRIMARY KEY, opens TEXT, closes TEXT, standings TEXT, closed TEXT);
CREATE TABLE IF NOT EXISTS kv (k TEXT PRIMARY KEY, v TEXT);
CREATE TABLE IF NOT EXISTS word_state (learner TEXT, word TEXT, box INTEGER DEFAULT 0, due TEXT, reps INTEGER DEFAULT 0, lapses INTEGER DEFAULT 0, right INTEGER DEFAULT 0, wrong INTEGER DEFAULT 0, saved INTEGER DEFAULT 0, first TEXT, last TEXT, lastday TEXT, lastwrong TEXT, PRIMARY KEY(learner,word));
CREATE TABLE IF NOT EXISTS word_reviews (id INTEGER PRIMARY KEY, learner TEXT, word TEXT, session TEXT, mode TEXT, kind TEXT, correct INTEGER, given TEXT, confusion TEXT, box_before INTEGER, due_before TEXT, ms INTEGER, at TEXT);
CREATE TABLE IF NOT EXISTS my_words (id TEXT PRIMARY KEY, learner TEXT, word TEXT, meaning TEXT, pos TEXT, example TEXT, same TEXT, opposite TEXT, notes TEXT, list TEXT, source TEXT, created TEXT, updated TEXT);
CREATE TABLE IF NOT EXISTS skill_ratings (learner TEXT, topic TEXT, rating REAL, n INTEGER DEFAULT 0, seed TEXT, PRIMARY KEY(learner,topic));
CREATE TABLE IF NOT EXISTS trap_log (id INTEGER PRIMARY KEY, learner TEXT, template TEXT, norm TEXT, at TEXT, event TEXT, attempt INTEGER, pts INTEGER);
CREATE TABLE IF NOT EXISTS due_days (learner TEXT, subject TEXT, day TEXT, keys TEXT, PRIMARY KEY(learner,subject,day));
CREATE TABLE IF NOT EXISTS passkeys (cred_id TEXT PRIMARY KEY, learner TEXT, user_handle TEXT, spki BLOB, alg INTEGER, sign_count INTEGER, label TEXT, created TEXT, last_used TEXT);
CREATE TABLE IF NOT EXISTS webauthn_challenges (challenge TEXT PRIMARY KEY, learner TEXT, purpose TEXT, expires TEXT);
CREATE TABLE IF NOT EXISTS devices (token TEXT PRIMARY KEY, learner TEXT, label TEXT, method TEXT, created TEXT, last_seen TEXT, session_only INTEGER DEFAULT 0, expires TEXT, revoked TEXT);
CREATE TABLE IF NOT EXISTS transfers (code TEXT PRIMARY KEY, learner TEXT, expires TEXT, used TEXT);
CREATE TABLE IF NOT EXISTS quarantine (template TEXT, seed INTEGER, at TEXT, note TEXT, released TEXT, PRIMARY KEY(template,seed));
CREATE TABLE IF NOT EXISTS week_goals (learner TEXT, week TEXT, id TEXT, kind TEXT, params TEXT, target INTEGER, created TEXT, done_at TEXT, PRIMARY KEY(learner,week,id));
CREATE TABLE IF NOT EXISTS push_subs (id TEXT PRIMARY KEY, learner TEXT, endpoint TEXT UNIQUE, p256dh TEXT, auth TEXT, kinds TEXT, created TEXT, last_sent TEXT);
CREATE TABLE IF NOT EXISTS cb_unknown (cb_id TEXT PRIMARY KEY, first TEXT, last TEXT, n INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS follows (learner TEXT, target TEXT, at TEXT, auto INTEGER DEFAULT 0, week TEXT, PRIMARY KEY(learner,target));
CREATE TABLE IF NOT EXISTS rank_snapshots (day TEXT, board TEXT, learner TEXT, rank INTEGER, value REAL, PRIMARY KEY(day,board,learner));
CREATE TABLE IF NOT EXISTS nudges (sender TEXT, target TEXT, contest TEXT, round INTEGER, at TEXT, PRIMARY KEY(sender,target,contest,round));
CREATE TABLE IF NOT EXISTS champions (kind TEXT, period TEXT, board TEXT, place INTEGER, learner TEXT, value REAL, band TEXT, PRIMARY KEY(kind,period,board,place,learner));
CREATE TABLE IF NOT EXISTS plan_snapshots (plan TEXT, made_on TEXT, days TEXT, PRIMARY KEY(plan,made_on));
CREATE TABLE IF NOT EXISTS plan_events (id INTEGER PRIMARY KEY, plan TEXT, at TEXT, kind TEXT, field TEXT, from_v TEXT, to_v TEXT, text TEXT, day TEXT);
CREATE TABLE IF NOT EXISTS rw_log (id INTEGER PRIMARY KEY, learner TEXT, at TEXT, source TEXT, ref TEXT, domain TEXT, missed INTEGER, "of" INTEGER);
CREATE TABLE IF NOT EXISTS word_lists (learner TEXT, name TEXT, words TEXT, created TEXT, PRIMARY KEY(learner,name));
CREATE TABLE IF NOT EXISTS word_suppress (frame TEXT, word TEXT, why TEXT, at TEXT, PRIMARY KEY(frame,word));
CREATE TABLE IF NOT EXISTS official_done (learner TEXT, cb_id TEXT, pick TEXT, "right" INTEGER, ms INTEGER, at TEXT, PRIMARY KEY(learner,cb_id,at));
"""

# Every learner-keyed table and how its rows are found, for S1's export and
# delete and for progress.carry: the value is a WHERE clause over :l.
# Iterating it gives the table names, as the old tuple did.
_PLAN = "plan IN (SELECT id FROM plans WHERE learner=:l)"
LEARNER_TABLES = {
    **{t: "learner=:l" for t in (
        "users", "attempts", "sessions", "practice_seen", "traps", "saved", "flags", "notes",
        "links", "reports", "earned", "tries", "outside_scores", "plans", "posts",
        "post_votes", "contest_members", "word_state", "word_reviews", "my_words",
        "skill_ratings", "trap_log", "due_days", "passkeys", "webauthn_challenges",
        "devices", "transfers", "week_goals", "push_subs", "champions", "rw_log",
        "word_lists", "official_done", "rank_snapshots")},
    "pairs": "learner=:l OR req_learner=:l",
    "follows": "learner=:l OR target=:l",
    "nudges": "sender=:l OR target=:l",
    "name_reports": "target=:l OR reporter=:l",
    "sets": "owner=:l", "contests": "owner=:l",
    "retired": 'code=:l OR "into"=:l',          # carry moves "into"; a code once retired stays retired
    **{t: _PLAN for t in ("plan_days", "plan_overrides", "plan_tasks", "plan_marks",
                          "plan_snapshots", "plan_events")},
    "learners": "id=:l",
}

# Sample learners ("sample:…", the live sample report) are never compared
# with real ones: every cross-learner query adds this, and writes are refused.
NOT_SAMPLE = "learner NOT LIKE 'sample:%'"


def is_sample(learner: str | None) -> bool:
    return bool(learner) and learner.startswith("sample:")

_local = threading.local()


@contextmanager
def transaction():
    """Keep a multi-row write atomic even when helpers call run()."""
    c = conn()
    if getattr(_local, "atomic", False):
        raise RuntimeError("nested database transaction")
    c.execute("BEGIN IMMEDIATE")
    _local.atomic = True
    try:
        yield c
    except BaseException:
        c.rollback()
        raise
    else:
        c.commit()
    finally:
        _local.atomic = False


@contextmanager
def atomic():
    """transaction(), or the one already open: for helpers such as
    progress.record that callers may run inside a bigger write."""
    if getattr(_local, "atomic", False):
        yield conn()
    else:
        with transaction() as c:
            yield c


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
    c.executescript(EXTRA_SCHEMA)
    for table, column, decl in LATER_COLUMNS:
        have = {r["name"] for r in c.execute(f"PRAGMA table_info({table})")}
        if column.strip('"') not in have:
            c.execute(f"ALTER TABLE {table} ADD COLUMN {column} {decl}")
    _relax_form_id(c)
    c.commit()
    with transaction():
        _rebuild_traps(c)
    c.executescript("""
      CREATE INDEX IF NOT EXISTS attempts_at_learner ON attempts(learner,at);
      CREATE INDEX IF NOT EXISTS attempts_at ON attempts(at);
      CREATE INDEX IF NOT EXISTS attempts_pair ON attempts(learner,template,seed);
      CREATE INDEX IF NOT EXISTS attempts_qid ON attempts(session,qid);
      CREATE INDEX IF NOT EXISTS users_learner ON users(learner);
      CREATE INDEX IF NOT EXISTS users_login_token ON users(login_token);
      CREATE INDEX IF NOT EXISTS sessions_mock_finished ON sessions(mock_id,finished);
      CREATE INDEX IF NOT EXISTS sessions_abandoned ON sessions(learner,abandoned);
      CREATE INDEX IF NOT EXISTS sessions_contest_rank ON sessions(contest,ranked,points DESC,secs);
      CREATE INDEX IF NOT EXISTS sessions_learner_contest ON sessions(learner,contest);
      CREATE INDEX IF NOT EXISTS sessions_kind_day ON sessions(kind,day);
      CREATE INDEX IF NOT EXISTS sessions_kind_open ON sessions(kind,finished);
      CREATE INDEX IF NOT EXISTS sessions_open_contest ON sessions(finished,contest);
      CREATE INDEX IF NOT EXISTS contest_items_pair ON contest_items(template,seed);
      CREATE INDEX IF NOT EXISTS reports_learner_at ON reports(learner,at);
      CREATE INDEX IF NOT EXISTS posts_paper_parent ON posts(paper,parent,at);
      CREATE INDEX IF NOT EXISTS word_state_due ON word_state(learner,due);
      CREATE INDEX IF NOT EXISTS word_reviews_at ON word_reviews(learner,at);
      CREATE INDEX IF NOT EXISTS my_words_learner ON my_words(learner);
      CREATE INDEX IF NOT EXISTS flags_learner_session ON flags(learner,session);
      CREATE INDEX IF NOT EXISTS plans_learner_archived ON plans(learner,archived);
      CREATE INDEX IF NOT EXISTS word_reviews_template ON word_reviews(template);
      CREATE UNIQUE INDEX IF NOT EXISTS contest_items_slot ON contest_items(contest,slot,qhash);
      CREATE UNIQUE INDEX IF NOT EXISTS pairs_token ON pairs(token);
      CREATE UNIQUE INDEX IF NOT EXISTS users_google_sub ON users(google_sub);
      CREATE INDEX IF NOT EXISTS trap_log_at ON trap_log(learner,at);
      CREATE INDEX IF NOT EXISTS trap_log_trap ON trap_log(learner,template,norm);
      CREATE INDEX IF NOT EXISTS devices_learner ON devices(learner);
      CREATE INDEX IF NOT EXISTS official_done_learner ON official_done(learner,at);
    """)
    _backfill_attempts(c)
    c.commit()
    _once(c, "backfill:trap_log", _backfill_trap_log)
    _once(c, "backfill:handle", _backfill_handles)
    _once(c, "backfill:trap_log_undoes", _backfill_undoes)
    from . import ratings
    ratings.backfill()


def _once(c: sqlite3.Connection, flag: str, fn) -> None:
    """A one-off data migration, remembered in kv so a restart skips it."""
    if c.execute("SELECT 1 FROM kv WHERE k=?", (flag,)).fetchone():
        return
    with transaction():
        fn(c)
        c.execute("INSERT OR REPLACE INTO kv(k,v) VALUES (?,?)",
                  (flag, datetime.now(timezone.utc).isoformat(timespec="seconds")))


def _backfill_trap_log(c: sqlite3.Connection) -> None:
    """`open` at opened and `fixed` at closed for traps made before the log."""
    for t in c.execute("SELECT * FROM traps").fetchall():
        c.execute("INSERT INTO trap_log(learner,template,norm,at,event) VALUES (?,?,?,?,?)",
                  (t["learner"], t["template"], t["norm"], t["opened"], "open"))
        if t["closed"] and t["closed_how"] in ("fixed", "transfer"):
            c.execute("INSERT INTO trap_log(learner,template,norm,at,event) VALUES (?,?,?,?,?)",
                      (t["learner"], t["template"], t["norm"], t["closed"], "fixed"))


def _backfill_undoes(c: sqlite3.Connection) -> None:
    """discard()/restore() rows once kept the id they undo in pts, which is a
    trap's points (V4); it moves to its own column."""
    c.execute("UPDATE trap_log SET undoes=pts, pts=NULL WHERE event IN ('discarded','restored')"
              " AND undoes IS NULL AND pts IS NOT NULL")


HANDLE_OK = re.compile(r"^[A-Za-z0-9 _.\-]{3,24}$")


def _backfill_handles(c: sqlite3.Connection) -> None:
    """U29: a name that passes the board-name rule becomes the board name; the
    first learner to hold it keeps it, and a clash leaves the handle null."""
    taken = {r["handle"].casefold() for r in c.execute("SELECT handle FROM learners WHERE handle IS NOT NULL")}
    for r in c.execute("SELECT id,name FROM learners WHERE handle IS NULL AND name IS NOT NULL"
                       " ORDER BY created,id").fetchall():
        if HANDLE_OK.fullmatch(r["name"]) and r["name"].casefold() not in taken:
            taken.add(r["name"].casefold())
            c.execute("UPDATE learners SET handle=? WHERE id=?", (r["name"], r["id"]))


def ensure_learner(code: str) -> None:
    conn().execute("INSERT OR IGNORE INTO learners(id,created) VALUES (?,?)",
                   (code, datetime.now(timezone.utc).isoformat(timespec="seconds")))
    if not getattr(_local, "atomic", False):
        conn().commit()


CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"     # A-HJ-NP-Z2-9: no I, O, 0 or 1


def new_code(length: int = 6) -> str:
    """A code from the unambiguous alphabet, unique across every code
    namespace (contest invites and U21's 8-character transfer codes), so a
    code typed in one box can never mean something in another."""
    for _ in range(100):
        code = "".join(secrets.choice(CODE_ALPHABET) for _ in range(length))
        if not one("SELECT 1 FROM contests WHERE code=? UNION ALL SELECT 1 FROM transfers WHERE code=?", code, code):
            return code
    raise RuntimeError("could not mint a unique code")


def _rebuild_traps(c: sqlite3.Connection) -> None:
    have = {r["name"] for r in c.execute("PRAGMA table_info(traps)")}
    if "id" in have:
        return
    from .progress import norm
    old = list(c.execute("SELECT * FROM traps"))
    c.execute("DROP TABLE traps")
    c.execute("""
      CREATE TABLE traps (
        id INTEGER PRIMARY KEY, learner TEXT NOT NULL, template TEXT NOT NULL,
        norm TEXT NOT NULL, reason TEXT NOT NULL, label TEXT NOT NULL, topic TEXT NOT NULL,
        hits INTEGER NOT NULL DEFAULT 1, owed INTEGER NOT NULL, opened TEXT NOT NULL,
        last TEXT NOT NULL, closed TEXT, closed_how TEXT, relapses INTEGER DEFAULT 0,
        seed INTEGER, session TEXT, due TEXT, checks INTEGER DEFAULT 0,
        source TEXT, note TEXT, origin TEXT, UNIQUE(learner,template,norm))
    """)
    c.execute("CREATE INDEX traps_open ON traps(learner,closed)")
    merged = {}
    for r in old:
        key = (r["learner"], r["template"], norm(r["reason"]))
        x = merged.get(key)
        if x is None:
            merged[key] = dict(r)
            continue
        x["hits"] += r["hits"]
        x["owed"] = max(x["owed"], r["owed"])
        x["opened"] = min(x["opened"], r["opened"])
        x["closed"] = None if x["closed"] is None or r["closed"] is None else max(x["closed"], r["closed"])
        if r["last"] >= x["last"]:
            x.update({"last": r["last"], "reason": r["reason"], "label": r["label"], "topic": r["topic"]})
    for (learner, template, normalized), x in merged.items():
        attempts = c.execute("SELECT seed,session,reason FROM attempts WHERE learner=? AND template=?"
                             " AND correct=0 ORDER BY at DESC,id DESC", (learner, template)).fetchall()
        a = next((r for r in attempts if norm(r["reason"] or "") == normalized), None)
        c.execute("INSERT INTO traps(learner,template,norm,reason,label,topic,hits,owed,opened,last,closed,closed_how,seed,session)"
                  " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                  (learner, template, normalized, x["reason"], x["label"], x["topic"],
                   x["hits"], x["owed"], x["opened"], x["last"], x["closed"],
                   "fixed" if x["closed"] else None,
                   a["seed"] if a else None, a["session"] if a else None))


def _backfill_attempts(c: sqlite3.Connection) -> None:
    """stem, norm and offered for rows filed before those columns (0.3 ms a
    regeneration). A template that no longer generates gets stem '' and
    offered '[]', so a restart does not try it again."""
    pending = c.execute("SELECT id,template,seed,correct,reason,flagged,conf,stem,offered FROM attempts"
                        " WHERE stem IS NULL OR offered IS NULL"
                        " OR (norm IS NULL AND (correct=0 OR flagged=1))").fetchall()
    if not pending:
        return
    from satbank.registry import generate
    from .progress import norm, offered_of
    for r in pending:
        try:
            it = generate(r["template"], r["seed"])
            stem = it.stem[:200]
            offered = json.dumps(offered_of({"type": it.fmt, "reasons": list(it.reasons),
                                             "spr_reasons": [[m.reason, str(m.value)] for m in
                                                             getattr(it, "spr_mistakes", ())]}))
        except Exception:
            stem, offered = "", "[]"
        unsure = r["correct"] and (r["flagged"] or r["conf"] == "unsure")
        normalized = "~unsure" if unsure else (norm(r["reason"] or "") if not r["correct"] else None)
        c.execute("UPDATE attempts SET stem=COALESCE(stem,?), norm=?, offered=COALESCE(offered,?) WHERE id=?",
                  (stem, normalized, offered, r["id"]))


def _relax_form_id(c: sqlite3.Connection) -> None:
    """Practice sessions have no form, and the first schema said form_id was
    required. sqlite cannot drop a NOT NULL in place, so the table is rebuilt:
    make the new shape, copy the rows over, swap the names. Rows are kept --
    a student who sat a diagnostic should not lose it to a schema change.
    """
    cols = {r["name"]: r for r in c.execute("PRAGMA table_info(sessions)")}
    if not cols or not cols.get("form_id", {})["notnull"]:
        return
    # Preserve every added column; a fixed base-column copy silently lost
    # mock routing, timers, and qstate on older installations.
    import re
    ddl = c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='sessions'").fetchone()[0]
    ddl = re.sub(r"\bform_id\s+INTEGER\s+NOT\s+NULL\b", "form_id INTEGER", ddl, flags=re.I)
    ddl = re.sub(r"^CREATE TABLE\s+(?:IF NOT EXISTS\s+)?[\"`]?sessions[\"`]?",
                 "CREATE TABLE sessions_new", ddl, count=1, flags=re.I)
    names = ", ".join(cols)
    c.commit()
    c.execute("PRAGMA foreign_keys=OFF")
    try:
        c.execute("BEGIN IMMEDIATE")
        c.execute(ddl)
        c.execute(f"INSERT INTO sessions_new ({names}) SELECT {names} FROM sessions")
        c.execute("DROP TABLE sessions")
        c.execute("ALTER TABLE sessions_new RENAME TO sessions")
        c.execute("CREATE INDEX IF NOT EXISTS sessions_user ON sessions(user_id)")
        c.commit()
    except BaseException:
        c.rollback()
        raise
    finally:
        c.execute("PRAGMA foreign_keys=ON")
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
    if not getattr(_local, "atomic", False):
        conn().commit()
    return cur


def load_answers(row) -> dict:
    return json.loads(row["answers"] or "{}")


def save_answers(session_id: str, answers: dict) -> None:
    run("UPDATE sessions SET answers=? WHERE id=?", json.dumps(answers), session_id)


# One answer written in place, in one statement, so two sent at once cannot
# overwrite each other the way reading, changing and writing the whole dict
# did. qid is always one of the session's own question ids, checked first.

def set_answer(session_id: str, qid: str, value, only_new: bool = False) -> bool:
    """False if the session has finished -- or, with only_new, if that
    question already had an answer, which is how an answer is claimed once."""
    path = f'$."{qid}"'
    sql = ("UPDATE sessions SET answers = json_set(answers, ?, json(?))"
           " WHERE id=? AND finished IS NULL")
    args = [path, json.dumps(value), session_id]
    if only_new:
        sql += " AND json_extract(answers, ?) IS NULL"
        args.append(path)
    return run(sql, *args).rowcount == 1


def clear_answer(session_id: str, qid: str) -> bool:
    return run("UPDATE sessions SET answers = json_remove(answers, ?) WHERE id=? AND finished IS NULL",
               f'$."{qid}"', session_id).rowcount == 1
