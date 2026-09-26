"""What every router needs: who is asking, their timezone, the shared
validators, and part() for the modules that are not written yet."""

from __future__ import annotations

import contextvars
import datetime as dt
import importlib
import json
import re
import secrets

from fastapi import Header, HTTPException

from . import db

# The real test gives 35 minutes to 22 math questions, so about 95 seconds each.
# Deriving the duration from the form means changing the blueprint cannot leave
# a stale clock behind.
SECONDS_PER_QUESTION = 95

# A learner is the token in their browser, sent as X-Learner: an `a:` code
# (minted on the client, checked for shape) or a `d:` device token (U21).
LEARNER_OK = re.compile(r"^[A-Za-z0-9:_\-]{4,120}$")
NAME_OK = re.compile(r"^[^\d<>@]{1,60}$")
HANDLE_OK = db.HANDLE_OK
TARGETS = range(200, 810, 10)
DATE_OK = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DAYS_OK = re.compile(r"^[01]{7}$")

SUBJECTS = ("math", "rw")
RW_TOPICS = frozenset({"words-in-context", "transitions", "rw.words_in_context", "rw.transitions",
                       "words_in_context"})

# U21's swap: learner_of puts a new device token here for the response header
# X-Learner-Swap. The app installs swap_middleware, which gives each request a
# box; without it nothing is minted, so no device row is made that no browser
# could ever pick up.
SWAP: contextvars.ContextVar[dict | None] = contextvars.ContextVar("satf_swap", default=None)
SEEN_EVERY = dt.timedelta(minutes=10)
IDLE = dt.timedelta(minutes=15)             # a shared computer's token dies after this
SHARED_MAX = dt.timedelta(hours=12)


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def _at(text: str | None) -> dt.datetime | None:
    return dt.datetime.fromisoformat(text) if text else None


def _retired() -> HTTPException:
    return HTTPException(401, {"retired": True, "into": None})


READS = ("GET", "HEAD", "OPTIONS")


def is_retired(x_learner: str | None) -> bool:
    """A code rotated away (`retired`): /api/shell answers {retired: true}."""
    return bool(db.one("SELECT 1 FROM retired WHERE code=?", (x_learner or "").strip()))


def learner_of(x_learner: str | None, write: bool | None = None) -> str:
    """The learner behind X-Learner. A `d:` token resolves through `devices`
    (revoked, expired or idle on a shared computer -> 401 retired). An `a:`
    code of a saved learner is served for 14 days after the save
    (`learners.swap_until`), each such browser getting its own device token,
    and refused after (U21: its data must not be served). A retired code
    (rotated away, Shell §3.1.5) is 401 on writes only; a read gets that old
    code's own, empty, data, and /api/shell asks is_retired(). `write`
    defaults to the request's method, which swap_middleware records; with
    no middleware a call is a read unless it came through writer_of."""
    v = (x_learner or "").strip()
    if not LEARNER_OK.match(v):
        raise HTTPException(400, "send your learner token in the X-Learner header")
    if v.startswith("d:"):
        return _device(v)
    if is_retired(v):
        if write is None:
            box = SWAP.get()
            write = bool(box) and box.get("method", "GET") not in READS
        if write:
            raise _retired()
        return v
    row = db.one("SELECT swap_until FROM learners WHERE id=?", v)
    if row and row["swap_until"]:
        if dt.datetime.now(dt.timezone.utc) >= _at(row["swap_until"]):
            raise _retired()
        box = SWAP.get()
        if box is not None:
            box["token"] = mint_device(v, "swap", box.get("label") or "Browser")
    return v


def _device(token: str) -> str:
    row = db.one("SELECT * FROM devices WHERE token=?", token)
    t = dt.datetime.now(dt.timezone.utc)
    if not row or row["revoked"] or (row["expires"] and _at(row["expires"]) <= t):
        raise _retired()
    seen = _at(row["last_seen"]) or _at(row["created"])
    if row["session_only"]:
        if t - (_at(row["created"]) or t) > SHARED_MAX or (seen and t - seen > IDLE):
            raise _retired()
    if row["session_only"] or not seen or t - seen >= SEEN_EVERY:
        db.run("UPDATE devices SET last_seen=? WHERE token=?", t.isoformat(timespec="seconds"), token)
    return row["learner"]


def mint_device(learner: str, method: str, label: str = "Browser", session_only: bool = False,
                expires: str | None = None) -> str:
    """A new `d:` token for this learner (every sign-in flow, and the swap)."""
    token = "d:" + "".join(secrets.choice("0123456789abcdefghijklmnopqrstuvwxyz") for _ in range(32))
    db.run("INSERT INTO devices(token,learner,label,method,created,session_only,expires)"
           " VALUES (?,?,?,?,?,?,?)", token, learner, label[:80], method, now(), int(session_only), expires)
    return token


async def swap_middleware(request, call_next):
    """app.middleware('http')(deps.swap_middleware): hands learner_of a box and
    turns a minted swap token into the X-Learner-Swap header."""
    box = {"label": _label(request.headers.get("user-agent", "")), "method": request.method,
           "tz_header": request.headers.get("x-tz")}
    reset = SWAP.set(box)
    try:
        response = await call_next(request)
    finally:
        SWAP.reset(reset)
    if box.get("token"):
        response.headers["X-Learner-Swap"] = box["token"]
    return response


def _label(ua: str) -> str:
    browser = next((b for b in ("Edg", "Chrome", "Firefox", "Safari") if b in ua), "Browser")
    system = next((s for k, s in (("iPhone", "iPhone"), ("iPad", "iPad"), ("Android", "Android"),
                                  ("Mac OS", "Mac"), ("Windows", "Windows"), ("Linux", "Linux")) if k in ua), "")
    return f"{'Edge' if browser == 'Edg' else browser} on {system}" if system else browser


def writer_of(x_learner: str | None) -> str:
    """learner_of for a write: a `sample:` learner (the live sample report) is
    read-only (403), and a retired code is 401."""
    learner = learner_of(x_learner, write=True)
    if db.is_sample(learner):
        raise HTTPException(403, "the sample report is read-only")
    return learner


# ------------------------------------------------------------------ subject

def subject_of(topic_or_template: str | None) -> str:
    """G11 / R51: template -> topic -> subject, no column. The 19 Math topics
    are `math`; Words in Context and Transitions (R57) are `rw`."""
    t = topic_or_template or ""
    if t in RW_TOPICS or t.startswith("rw."):
        return "rw"
    if "." in t:
        try:
            from satbank.registry import topic_of
            topic = topic_of(t)
        except Exception:
            return "math"
        return "rw" if topic in RW_TOPICS else "math"
    return "math"


def subject_param(subject: str | None) -> str:
    """?subject= on every section endpoint: default math, 422 for anything else."""
    s = subject or "math"
    if s not in SUBJECTS:
        raise HTTPException(422, f"subject must be one of {', '.join(SUBJECTS)}")
    return s


# ------------------------------------------------------------------ access (R19)

def _has_pair(value, template: str, seed: int) -> bool:
    if isinstance(value, dict):
        if value.get("key", value.get("template")) == template and value.get("seed") == seed:
            return True
        return any(_has_pair(x, template, seed) for x in value.values())
    if isinstance(value, list):
        if len(value) == 2 and value[0] == template and value[1] == seed:
            return True
        return any(_has_pair(x, template, seed) for x in value)
    return False


def live_days() -> list[str]:
    """Every date that is still today somewhere on Earth (UTC-12 to UTC+14):
    a challenge on any of them must not leak."""
    utc = dt.datetime.now(dt.timezone.utc)
    return sorted({(utc - dt.timedelta(minutes=tz)).date().isoformat() for tz in (-840, 0, 720)})


TEST_KINDS = ("mock", "module", "diagnostic", "custom", "paper", "section")


def paper_of(row) -> list:
    """What a sitting put in front of the learner, key included."""
    if row["questions"]:
        return json.loads(row["questions"])
    from .api_tests import marked_questions, questions_of
    try:
        return marked_questions(row) if row["finished"] else questions_of(row)
    except (KeyError, TypeError):
        return []


def _protected(learner: str, template: str, seed: int) -> bool:
    """A live test of this learner's, a challenge that is still today anywhere
    (the shared day row and every learner's twin sitting), or an item of a
    contest that is open or sitting now."""
    days = live_days()
    marks = ",".join("?" for _ in days)
    for row in db.rows(f"SELECT questions FROM challenges WHERE day IN ({marks})", *days):
        if _has_pair(json.loads(row["questions"]), template, seed):
            return True
    # indexed narrowing first (sessions_kind_day, sessions_kind_open,
    # sessions_open_contest), so only the few live sittings are JSON-matched
    quoted = f'%"{template}"%'
    for row in db.rows(f"SELECT questions FROM sessions WHERE kind='challenge' AND day IN ({marks})"
                       " AND questions LIKE ? UNION ALL"
                       " SELECT questions FROM sessions WHERE kind='challenge' AND finished IS NULL"
                       " AND abandoned IS NULL AND questions LIKE ? UNION ALL"
                       " SELECT questions FROM sessions WHERE finished IS NULL AND contest IS NOT NULL"
                       " AND abandoned IS NULL AND questions LIKE ?", *days, quoted, quoted, quoted):
        if _has_pair(json.loads(row["questions"]), template, seed):
            return True
    stamp = now()
    if db.one("SELECT 1 FROM contest_items AS i JOIN contests AS c ON c.id=i.contest"
              " WHERE i.template=? AND i.seed=? AND (c.closes IS NULL OR c.closes>?)"
              " AND (c.opens IS NULL OR c.opens<=?)", template, seed, stamp, stamp):
        return True
    for row in db.rows("SELECT * FROM sessions WHERE learner=? AND finished IS NULL AND abandoned IS NULL"
                       f" AND kind IN ({','.join('?' for _ in TEST_KINDS)})", learner, *TEST_KINDS):
        if _has_pair(paper_of(row), template, seed):
            return True
    return False


def _finished_paper(learner: str, template: str, seed: int, exclude: str | None = None) -> bool:
    """On the paper of a finished sitting of this learner whose key it showed:
    every test kind, the challenge, and end-mode practice sets."""
    for row in db.rows("SELECT * FROM sessions WHERE learner=? AND finished IS NOT NULL AND id!=?"
                       " AND (questions IS NULL OR questions LIKE ?)", learner, exclude or "",
                       f'%"{template}"%'):
        cfg = json.loads(row["cfg"] or "{}")
        if not (row["kind"] in TEST_KINDS or row["kind"] == "challenge" or cfg.get("feedback") == "end"):
            continue
        if _has_pair(paper_of(row), template, seed):
            return True
    return False


def access(learner: str, template: str, seed: int, exclude: str | None = None) -> str | None:
    """May this exact item be revealed ('reveal'), kept for later ('kept'), or
    neither (None)? `exclude` leaves one sitting out of the finished-paper rule
    (the sitting whose answers are being filed)."""
    if _protected(learner, template, seed):
        return None
    if db.one("SELECT 1 FROM attempts WHERE learner=? AND template=? AND seed=?", learner, template, seed):
        return "reveal"
    for table in ("saved", "flags"):
        if db.one(f"SELECT 1 FROM {table} AS s JOIN sessions AS x ON x.id=s.session"
                  " WHERE s.learner=? AND s.template=? AND s.seed=? AND x.finished IS NOT NULL"
                  f" AND x.id!=? AND x.kind IN ({','.join('?' for _ in TEST_KINDS)},'challenge')",
                  learner, template, seed, exclude or "", *TEST_KINDS):
            return "reveal"
    if _finished_paper(learner, template, seed, exclude):
        return "reveal"
    if db.one("SELECT 1 FROM saved WHERE learner=? AND template=? AND seed=?", learner, template, seed):
        return "kept"
    if db.one("SELECT 1 FROM flags AS f JOIN sessions AS x ON x.id=f.session"
              " WHERE f.learner=? AND f.template=? AND f.seed=?"
              " AND (x.kind='drill' OR x.finished IS NOT NULL)", learner, template, seed):
        return "kept"
    return None


def key_printed(session: str | None, when: str) -> bool:
    """A worksheet whose key was printed before this answer (V18)."""
    if not session:
        return False
    row = db.one("SELECT cfg FROM sessions WHERE id=?", session)
    printed = json.loads(row["cfg"] or "{}").get("key_printed") if row and row["cfg"] else None
    return bool(printed) and printed <= when


def tz_of(x_tz: int = Header(default=0, ge=-840, le=720)) -> int:
    """X-Tz, JavaScript's getTimezoneOffset(): minutes behind UTC."""
    return x_tz


def session_or_404(sid: str):
    row = db.one("SELECT * FROM sessions WHERE id=?", sid)
    if row is None:
        raise HTTPException(404, "no such session")
    return row


def mine(row, learner: str):
    if row["learner"] and row["learner"] != learner:
        raise HTTPException(403, "that session belongs to someone else")
    return row


def part(module: str, name: str):
    """server.<module>.<name>, or None while that module does not exist yet.
    A module that exists and fails to import is a bug, and raises."""
    try:
        mod = importlib.import_module(f"{__package__}.{module}")
    except ModuleNotFoundError as e:
        if e.name != f"{__package__}.{module}":
            raise
        return None
    return getattr(mod, name, None)
