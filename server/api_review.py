"""Review's endpoints (spec/rebuild-v2.md §3.9.5, R2, R5; spec/v2-upgrades/review.md V1-V19).

Every route is owner-only and subject-aware (?subject=, math by default).
The model -- the daily list, counts, blind spots, the ledger, calibration and
the trap sheet -- is server/review.py; this file validates at the boundary,
reads the rows and shapes them for the page:

  /mistakes/                        307 to /review/?tab=redo, keeping the query (R2)
  GET  /api/mistakes                open traps and saved questions (kept for test_flow)
  POST /api/saved, PATCH /api/saved keep a question, its note (R6) and why (V3)
  POST /api/session/{sid}/flag      mark a test question for review (R5)
  POST /api/flags                   the same for practice sets and the challenge, and the hub's Unmark
  POST /api/mistakes/dismiss | restore | reopen | add
"""

from __future__ import annotations

import datetime as dt
import csv
import io
import json
import secrets
import statistics
from collections import Counter, defaultdict
from functools import lru_cache

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from fastapi.responses import RedirectResponse, Response
from pydantic import BaseModel, Field

from . import db, deps, drill, practice, progress, review
from .api_tests import DRILLS, public, questions_of
from .deps import TEST_KINDS, learner_of, mine, now, session_or_404, tz_of, writer_of

router = APIRouter()
NOTE_MAX = 280              # a saved question's note (§5)
QID = r"^[A-Za-z0-9_.:\-]{1,64}$"
TEMPLATE = r"^[a-z0-9_.]{1,80}$"


def bad(field: str, reason: str = "invalid value"):
    raise HTTPException(422, {"field": field, "reason": reason})


def known(template: str) -> str:
    """A catalogue template, or 404: an address is never guessed at."""
    try:
        return practice.topic_of(template)
    except Exception:
        raise HTTPException(404, "no such question type")


# ------------------------------------------------------------------ the old page (R2)

@router.get("/mistakes", include_in_schema=False)
@router.get("/mistakes/", include_in_schema=False)
@router.get("/mistakes/index.html", include_in_schema=False)
def mistakes_page(request: Request) -> RedirectResponse:
    query = request.url.query
    return RedirectResponse("/review/?tab=redo" + (f"&{query}" if query else ""), status_code=307)


@router.get("/api/mistakes")
def mistakes(x_learner: str | None = Header(default=None)) -> dict:
    learner = learner_of(x_learner)
    names = progress.topics()
    saved = [{"template": r["template"], "topic": r["topic"], "name": names[r["topic"]].name,
              "at": r["at"]}
             for r in db.rows("SELECT template, topic, at FROM saved WHERE learner=? ORDER BY at DESC",
                              learner) if r["topic"] in names]
    traps = [{**t, "name": names[t["topic"]].name, "domain": names[t["topic"]].domain,
              "status": review.status(t), "of": review.of(t)}
             for t in progress.open_traps(learner) if t["topic"] in names]
    return {"traps": traps, "saved": saved}


# ------------------------------------------------------------------ saved (§5, V3, R6)

class Save(BaseModel):
    session: str | None = Field(default=None, max_length=64)
    question_id: str | None = Field(default=None, pattern=QID)
    template: str | None = Field(default=None, pattern=TEMPLATE)
    seed: int | None = Field(default=None, ge=0)
    note: str | None = Field(default=None, max_length=NOTE_MAX)
    why: str | None = Field(default=None, pattern="^(trick|hard)$")
    on: bool = True


def _pair_of_session(learner: str, sid: str, qid: str | None, on: bool) -> tuple[str, int, str]:
    """(template, seed, topic) of a question in the learner's own sitting. A
    practice set's question, an answered challenge question, and any question
    of a finished test (blanks included) can be kept; a live test's never,
    or saving would be a way to read a key before answering."""
    row = mine(session_or_404(sid), learner)
    q = None
    if row["kind"] in DRILLS:
        q = next((x for x in questions_of(row) if x["id"] == qid), None)
    elif row["kind"] in TEST_KINDS and row["finished"]:
        q = next((x for x in progress._paper(row) if x.get("id") == qid), None)
    if q is None or "key" not in q:
        raise HTTPException(404, "no such question in that session")
    if on and row["kind"] == "challenge" and qid not in db.load_answers(row):
        raise HTTPException(409, "answer it first")
    return q["key"], q["seed"], q["topic"]


def _pair(learner: str, body) -> tuple[str, int, str, str | None, str | None]:
    if body.session:
        if not body.question_id:
            bad("question_id", "required with session")
        return (*_pair_of_session(learner, body.session, body.question_id, body.on),
                body.session, body.question_id)
    if body.template is None or body.seed is None:
        bad("template", "send session and question_id, or template and seed")
    topic = known(body.template)
    if body.on and deps.access(learner, body.template, body.seed) is None:
        raise HTTPException(404, "no such question of yours")
    return body.template, body.seed, topic, None, None


def put_note(learner: str, template: str, seed: int, note: str | None) -> str | None:
    """R6's one store: the note on this exact question, its marks kept."""
    note = (note or "").strip()
    old = db.one("SELECT marks FROM notes WHERE learner=? AND template=? AND seed=?", learner, template, seed)
    marks = json.loads(old["marks"] or "[]") if old else []
    if not note and not marks:
        db.run("DELETE FROM notes WHERE learner=? AND template=? AND seed=?", learner, template, seed)
        return None
    db.run("INSERT INTO notes(learner,template,seed,note,marks,at) VALUES (?,?,?,?,?,?)"
           " ON CONFLICT(learner,template,seed) DO UPDATE SET note=excluded.note, at=excluded.at",
           learner, template, seed, note, json.dumps(marks), now())
    return note or None


@router.post("/api/saved")
def save_question(body: Save, x_learner: str | None = Header(default=None)) -> dict:
    """Keep a question for good (R5), by its sitting or, from Review, by its
    address. Unsave keeps the note (R6: it is the question's note, and undo
    re-posts it anyway)."""
    learner = writer_of(x_learner)
    template, seed, topic, session, qid = _pair(learner, body)
    if not body.on:
        db.run("DELETE FROM saved WHERE learner=? AND template=? AND seed=?", learner, template, seed)
        return {"saved": False}
    with db.atomic():
        db.ensure_learner(learner)
        db.run("INSERT INTO saved (learner, template, seed, topic, at, session, qid, why) VALUES (?,?,?,?,?,?,?,?)"
               " ON CONFLICT(learner,template,seed) DO UPDATE SET why=COALESCE(excluded.why, saved.why),"
               " session=COALESCE(saved.session, excluded.session), qid=COALESCE(saved.qid, excluded.qid)",
               learner, template, seed, topic, now(), session, qid, body.why)
        note = put_note(learner, template, seed, body.note) if body.note is not None else None
    return {"saved": True, "note": note, "why": body.why}


class SavedEdit(BaseModel):
    template: str = Field(pattern=TEMPLATE)
    seed: int = Field(ge=0)
    note: str | None = Field(default=None, max_length=NOTE_MAX)
    why: str | None = Field(default=None, pattern="^(trick|hard|)$")


@router.patch("/api/saved")
def edit_saved(body: SavedEdit, x_learner: str | None = Header(default=None)) -> dict:
    """A saved question's note (280 characters, 422 above) and why tag."""
    learner = writer_of(x_learner)
    row = db.one("SELECT why FROM saved WHERE learner=? AND template=? AND seed=?", learner, body.template, body.seed)
    if not row:
        raise HTTPException(404, "that question is not saved")
    sent = body.model_fields_set
    why = row["why"]
    if "why" in sent:
        why = body.why or None
        db.run("UPDATE saved SET why=? WHERE learner=? AND template=? AND seed=?", why, learner, body.template, body.seed)
    if "note" in sent:
        note = put_note(learner, body.template, body.seed, body.note)
    else:
        n = db.one("SELECT note FROM notes WHERE learner=? AND template=? AND seed=?", learner, body.template, body.seed)
        note = n["note"] or None if n else None
    return {"note": note, "why": why}


# ------------------------------------------------------------------ marks for review (R5)

class Flag(BaseModel):
    question_id: str = Field(pattern=QID)
    on: bool = True


class HubFlag(BaseModel):
    session: str = Field(max_length=64)
    question_id: str | None = Field(default=None, pattern=QID)
    template: str | None = Field(default=None, pattern=TEMPLATE)
    seed: int | None = Field(default=None, ge=0)
    on: bool = True


def _own(sid: str, learner: str):
    """The flag endpoints check ownership outright: GET /api/session/{sid} has
    no owner check, so holding an id must not be enough to set a flag, and a
    sitting with no learner belongs to nobody."""
    row = session_or_404(sid)
    if row["learner"] != learner:
        raise HTTPException(403, "that session belongs to someone else")
    return row


def flags_of(learner: str, sid: str) -> list[str]:
    return [r["qid"] for r in db.rows("SELECT qid FROM flags WHERE learner=? AND session=? ORDER BY at",
                                      learner, sid)]


def set_flag(learner: str, row, qid: str, on: bool) -> dict:
    """Upsert or delete one flag. The qid must be on the sitting's paper; the
    row carries the (template, seed) so Review and the builder can find it."""
    q = next((x for x in progress._paper(row) if x.get("id") == qid), None)
    if q is None or "key" not in q:
        raise HTTPException(400, "that question is not on this paper")
    if on:
        db.run("INSERT OR IGNORE INTO flags(learner,session,qid,template,seed,topic,at) VALUES (?,?,?,?,?,?,?)",
               learner, row["id"], qid, q["key"], q["seed"], q["topic"], now())
    else:
        db.run("DELETE FROM flags WHERE learner=? AND session=? AND qid=?", learner, row["id"], qid)
    return {"flags": flags_of(learner, row["id"])}


@router.post("/api/session/{sid}/flag")
def flag_test(sid: str, body: Flag, x_learner: str | None = Header(default=None)) -> dict:
    """Mark for review in a section, module or diagnostic, while it is live
    and after it is finished (a flag set later reads 'flagged later')."""
    learner = writer_of(x_learner)
    row = _own(sid, learner)
    if row["kind"] not in TEST_KINDS:
        raise HTTPException(409, "a practice set or challenge is flagged through /api/flags")
    return set_flag(learner, row, body.question_id, body.on)


@router.post("/api/flags")
def flag_other(body: HubFlag, x_learner: str | None = Header(default=None)) -> dict:
    """Mark for review in a practice set or the challenge (a challenge flag
    stays hidden until that question is answered), and Review's Unmark /
    undo by {session, question_id} or {session, template, seed}."""
    learner = writer_of(x_learner)
    row = _own(body.session, learner)
    if body.question_id:
        return set_flag(learner, row, body.question_id, body.on)
    if body.template is None or body.seed is None:
        bad("question_id", "send question_id, or template and seed")
    if body.on:
        q = next((x for x in progress._paper(row) if x.get("key") == body.template and x.get("seed") == body.seed), None)
        if q is None:
            raise HTTPException(400, "that question is not on this paper")
        return set_flag(learner, row, q["id"], True)
    db.run("DELETE FROM flags WHERE learner=? AND session=? AND template=? AND seed=?",
           learner, body.session, body.template, body.seed)
    return {"flags": flags_of(learner, body.session)}


# ------------------------------------------------------------------ mistake actions (§3.9.5)

class TrapRef(BaseModel):
    id: int = Field(ge=1)


class AddRef(BaseModel):
    template: str = Field(pattern=TEMPLATE)
    seed: int = Field(ge=0)


def _trap(learner: str, tid: int):
    t = db.one("SELECT * FROM traps WHERE id=? AND learner=?", tid, learner)
    if not t:
        raise HTTPException(404, "no such mistake of yours")
    return t


def _brief(tid: int) -> dict:
    t = db.one("SELECT * FROM traps WHERE id=?", tid)
    return {"id": t["id"], "label": review.trap_label(t), "owed": t["owed"], "of": review.of(t),
            "closed": t["closed"], "closed_how": t["closed_how"], "relapses": t["relapses"],
            "status": review.status(t) if t["closed"] is None else t["closed_how"]}


@router.post("/api/mistakes/dismiss")
def dismiss(body: TrapRef, x_learner: str | None = Header(default=None)) -> dict:
    """Remove a mistake without fixing it. It stays in History and the log; a
    later miss reopens it as Open, never as a relapse."""
    learner = writer_of(x_learner)
    t = _trap(learner, body.id)
    if t["closed"] is not None:
        raise HTTPException(409, "that mistake is not open")
    stamp = now()
    with db.atomic():
        db.run("UPDATE traps SET closed=?, closed_how='dismissed', due=NULL WHERE id=?", stamp, t["id"])
        progress.log(learner, t["template"], t["norm"], "dismissed", stamp)
    return _brief(t["id"])


def _undismiss(learner: str, tid: int, event: str) -> dict:
    t = _trap(learner, tid)
    if t["closed_how"] != "dismissed":
        raise HTTPException(409, "that mistake was not dismissed")
    stamp = now()
    with db.atomic():
        if event == "restored":     # the undo: exactly as it was, owed and all
            db.run("UPDATE traps SET closed=NULL, closed_how=NULL WHERE id=?", t["id"])
            last = db.one("SELECT id FROM trap_log WHERE learner=? AND template=? AND norm=? AND event='dismissed'"
                          " ORDER BY id DESC LIMIT 1", learner, t["template"], t["norm"])
            progress.log(learner, t["template"], t["norm"], "restored", stamp, undoes=last["id"] if last else None)
        else:                       # Reopen on a dismissed row: open again, owing its full count
            db.run("UPDATE traps SET closed=NULL, closed_how=NULL, owed=?, last=? WHERE id=?",
                   review.of(t), stamp, t["id"])
            progress.log(learner, t["template"], t["norm"], "reopened", stamp)
    return _brief(t["id"])


@router.post("/api/mistakes/restore")
def restore(body: TrapRef, x_learner: str | None = Header(default=None)) -> dict:
    """Undo a dismiss. Relapses are unchanged."""
    return _undismiss(writer_of(x_learner), body.id, "restored")


@router.post("/api/mistakes/reopen")
def reopen(body: TrapRef, x_learner: str | None = Header(default=None)) -> dict:
    return _undismiss(writer_of(x_learner), body.id, "reopened")


@router.post("/api/mistakes/add")
def add_to_redo(body: AddRef, x_learner: str | None = Header(default=None)) -> dict:
    """Add to Redo (an answer that was right, but not for sure): an Unsure
    that one clean answer closes. The question must be one this learner may
    see revealed."""
    learner = writer_of(x_learner)
    topic = known(body.template)
    if deps.access(learner, body.template, body.seed) != "reveal":
        raise HTTPException(404, "no such question of yours")
    filed = progress.record_trap(learner, {"key": body.template, "seed": body.seed, "topic": topic},
                                 "", now(), unsure=True)
    return {"trap": {**_brief(filed["id"]), "event": filed["event"]}}


# ------------------------------------------------------------------ read endpoints

def _subject(subject: str) -> str:
    if subject not in deps.SUBJECTS:
        bad("subject", "choose math or rw")
    return subject


def _csv(value: str | None) -> set[str]:
    return {part.strip() for part in (value or "").split(",") if part.strip()}


def _matches(row: dict, *, topics: str | None = None, difficulty: str | None = None,
             fmt: str | None = None, source: str | None = None, since: str | None = None,
             until: str | None = None, q: str | None = None, at: str = "at") -> bool:
    for key, value in (("topic", topics), ("difficulty", difficulty), ("fmt", fmt), ("source", source)):
        accepted = _csv(value)
        if accepted and row.get(key) not in accepted:
            return False
    stamp = row.get(at) or ""
    if since and stamp[:10] < since:
        return False
    if until and stamp[:10] > until:
        return False
    if q and q.casefold() not in " ".join(str(row.get(k) or "") for k in
                                    ("label", "name", "skill", "stem", "template", "note", "mistake")).casefold():
        return False
    return True


def _page(items: list[dict], limit: int, cursor: int | None, key: str = "id") -> dict:
    if cursor is not None:
        items = [i for i in items if isinstance(i.get(key), int) and i[key] < cursor]
    page = items[:limit]
    return {"items": page, "total": len(items), "next": page[-1][key] if len(items) > limit and page else None}


@router.get("/api/review/counts")
def counts(subject: str = "math", x_learner: str | None = Header(default=None),
           x_tz: int = Depends(tz_of)) -> dict:
    return review.counts(learner_of(x_learner), x_tz, _subject(subject))


@router.get("/api/review/due")
def due(subject: str = "math", x_learner: str | None = Header(default=None),
        x_tz: int = Depends(tz_of)) -> dict:
    return review.due(learner_of(x_learner), x_tz, _subject(subject))


class Snooze(BaseModel):
    key: str = Field(min_length=1, max_length=160)
    undo: bool = False


@router.post("/api/review/snooze")
def snooze(body: Snooze, subject: str = "math", x_learner: str | None = Header(default=None),
           x_tz: int = Depends(tz_of)) -> dict:
    learner = writer_of(x_learner)
    subject = _subject(subject)
    available = review.due(learner, x_tz, subject)
    if body.key not in {i["key"] for i in available["items"]} and body.key not in available["waiting_keys"]:
        raise HTTPException(404, "that item is not on today's review list")
    return review.snooze(learner, x_tz, body.key, body.undo, subject)


@router.get("/api/review/redo")
def redo(subject: str = "math", topics: str | None = None, difficulty: str | None = None,
         fmt: str | None = None, kind: str | None = None, status: str | None = None,
         q: str | None = None, sort: str = "recent", group: str = "topic", cause: str | None = None,
         lens: str | None = None, x_learner: str | None = Header(default=None)) -> dict:
    learner, subject = learner_of(x_learner), _subject(subject)
    if sort not in ("recent", "hits", "near", "oldest", "topic", "stake", "blind"):
        bad("sort")
    if group not in ("topic", "domain", "norm"):
        bad("group")
    names = review.math_topics(subject)
    misses = review.latest_misses(learner, subject)
    pts = review.pts_fn(learner, subject)
    blind = review.blind(learner, subject)
    sittings = {}
    items = []
    for t in progress.open_traps(learner):
        if t["topic"] not in names:
            continue
        miss = misses.get((t["template"], t["norm"]))
        source = review.source_of(miss["session"]) if miss else t["source"] or "outside"
        entry = {**t, "label": review.trap_label(t), "kind": review.trap_kind(t, miss),
                 "skill": review.cap(review.skill_of(t["template"], t["seed"])),
                 "name": names[t["topic"]].name, "domain": names[t["topic"]].domain,
                 "clean": review.of(t) - t["owed"], "status": review.status(t),
                 "difficulty": miss["difficulty"] if miss else None,
                 "fmt": miss["fmt"] if miss else None, "source": source,
                 "given": miss["given"] if miss else None,
                 "given_label": review.given_label(miss["fmt"], miss["given"]) if miss else None,
                 "elsewhere": review.dodged_elsewhere(learner, t["template"], t["norm"])
                 if t["norm"] and t["norm"] != "~unsure" else 0,
                 "pts": pts(t["template"], t["norm"], t["topic"]),
                 "new": review.is_new(miss, sittings), "blind": t["id"] in blind,
                 "cause": miss["diag"] or miss["miss_kind"] if miss else None}
        if _csv(kind) and entry["kind"] not in _csv(kind):
            continue
        if _csv(status) and entry["status"] not in _csv(status):
            continue
        if lens == "new" and not entry["new"]:
            continue
        if lens == "blind" and not entry["blind"]:
            continue
        if cause and entry["cause"] != cause:
            continue
        if _matches(entry, topics=topics, difficulty=difficulty, fmt=fmt, q=q, at="last"):
            items.append(entry)
    orders = {"recent": lambda x: x["last"], "oldest": lambda x: x["last"],
              "hits": lambda x: x["hits"], "near": lambda x: -x["owed"],
              "topic": lambda x: x["topic"], "stake": lambda x: x["pts"] or 0,
              "blind": lambda x: int(x["blind"])}
    items.sort(key=orders[sort], reverse=sort not in ("oldest", "topic"))
    groups: dict[str, dict] = {}
    for item in items:
        key = item["topic"] if group == "topic" else item["domain"] if group == "domain" else item["norm"]
        g = groups.setdefault(key, {"key": key, "name": item["name"] if group == "topic" else
                                    item["domain"] if group == "domain" else item["label"],
                                    "domain": item["domain"], "count": 0, "questions": 0})
        g["count"] += 1
        g["questions"] += item["owed"]
    return {"subject": subject, "items": items[:500], "groups": list(groups.values()),
            "total": len(items), "questions": sum(i["owed"] for i in items)}


@lru_cache(maxsize=4096)
def _card(template: str, seed: int) -> dict | None:
    return review.question(template, seed)


def _meta(template: str, seed: int, topic: str, names: dict) -> dict:
    q = _card(template, seed) or {}
    name = names.get(topic)
    return {"template": template, "seed": seed, "topic": topic,
            "name": name.name if name else topic, "domain": name.domain if name else None,
            "skill": review.cap(review.skill_of(template, seed)),
            "difficulty": q.get("difficulty"), "fmt": q.get("type"),
            "stem": (q.get("stem") or "")[:160]}


def _filtered_page(items: list[dict], *, topics: str | None, difficulty: str | None,
                   fmt: str | None, source: str | None, since: str | None, until: str | None,
                   q: str | None, cursor: int | None, limit: int, at: str = "at") -> dict:
    filtered = [x for x in items if _matches(x, topics=topics, difficulty=difficulty, fmt=fmt,
                                             source=source, since=since, until=until, q=q, at=at)]
    total = len(filtered)
    page = _page(filtered, limit, cursor)
    page["total"] = total
    return page


def _latest_attempt(learner: str, template: str, seed: int):
    return db.one("SELECT * FROM attempts WHERE learner=? AND template=? AND seed=? AND void IS NULL"
                  " ORDER BY id DESC LIMIT 1", learner, template, seed)


@router.get("/api/review/marked")
def marked(subject: str = "math", topics: str | None = None, difficulty: str | None = None,
           fmt: str | None = None, source: str | None = None, since: str | None = None,
           until: str | None = None, q: str | None = None, cursor: int | None = None,
           limit: int = Query(default=50, ge=1, le=100), x_learner: str | None = Header(default=None)) -> dict:
    learner, subject = learner_of(x_learner), _subject(subject)
    names = review.math_topics(subject)
    rows = []
    for f in review.visible_flags(learner, subject):
        session = db.one("SELECT * FROM sessions WHERE id=?", f["session"])
        a = f["attempt"]
        item = {**_meta(f["template"], f["seed"], f["topic"], names),
                "id": f["rowid"] if "rowid" in f else None,
                "session": f["session"], "qid": f["qid"], "at": f["at"],
                "during": f["during"], "session_kind": session["kind"] if session else None,
                "session_at": session["finished"] or session["started"] if session else None,
                "n": review.number_of(session, f["qid"])[1],
                "answered": bool(a), "correct": f["correct"],
                "given_label": review.given_label(a["fmt"], a["given"]) if a else None,
                "answer": _card(f["template"], f["seed"]).get("answer") if a and _card(f["template"], f["seed"]) else None,
                "ms": a["ms"] if a else None,
                "source": review.source_of(f["session"], session)}
        rows.append(item)
    # flags have no integer primary key; assign their SQLite rowid for stable cursor pagination.
    ids = {(r["session"], r["qid"]): r["id"] for r in db.rows(
        "SELECT rowid AS id, session, qid FROM flags WHERE learner=?", learner)}
    for r in rows:
        r["id"] = ids.get((r["session"], r["qid"]), 0)
    rows.sort(key=lambda r: r["id"], reverse=True)
    out = _filtered_page(rows, topics=topics, difficulty=difficulty, fmt=fmt, source=source,
                         since=since, until=until, q=q, cursor=cursor, limit=limit)
    out.update({"subject": subject, "calibration": {"flagged": len(rows),
                                                     "right": sum(1 for r in rows if r["correct"])}})
    return out


@router.get("/api/review/saved")
def saved(subject: str = "math", topics: str | None = None, difficulty: str | None = None,
          fmt: str | None = None, source: str | None = None, since: str | None = None,
          until: str | None = None, q: str | None = None, cursor: int | None = None,
          limit: int = Query(default=50, ge=1, le=100), x_learner: str | None = Header(default=None),
          x_tz: int = Depends(tz_of)) -> dict:
    learner, subject = learner_of(x_learner), _subject(subject)
    names = review.math_topics(subject)
    sched = review.saved_schedule(learner, x_tz, subject)
    rows = []
    for s in db.rows("SELECT rowid AS id, * FROM saved WHERE learner=? ORDER BY rowid DESC", learner):
        if s["topic"] not in names:
            continue
        a = _latest_attempt(learner, s["template"], s["seed"])
        note = db.one("SELECT note FROM notes WHERE learner=? AND template=? AND seed=?",
                      learner, s["template"], s["seed"])
        session = db.one("SELECT * FROM sessions WHERE id=?", s["session"]) if s["session"] else None
        card = _card(s["template"], s["seed"]) or {}
        rows.append({**_meta(s["template"], s["seed"], s["topic"], names),
                     "id": s["id"], "session": s["session"], "qid": s["qid"], "at": s["at"],
                     "source": review.source_of(s["session"], session),
                     "session_kind": session["kind"] if session else None,
                     "session_at": session["finished"] or session["started"] if session else None,
                     "note": note["note"] if note else None, "why": s["why"],
                     "tries": db.one("SELECT COUNT(*) AS n FROM attempts WHERE learner=? AND template=? AND seed=?",
                                     learner, s["template"], s["seed"])["n"],
                     "last_result": "right" if a and a["correct"] else "wrong" if a else None,
                     "answered": bool(a), "correct": bool(a and a["correct"]),
                     "given_label": review.given_label(a["fmt"], a["given"]) if a else None,
                     "answer": card.get("answer") if deps.access(learner, s["template"], s["seed"]) == "reveal" else None,
                     "ms": a["ms"] if a else None, **sched.get((s["template"], s["seed"]), {})})
    out = _filtered_page(rows, topics=topics, difficulty=difficulty, fmt=fmt, source=source,
                         since=since, until=until, q=q, cursor=cursor, limit=limit)
    out["subject"] = subject
    return out


@router.get("/api/review/fixed")
def fixed(subject: str = "math", topics: str | None = None, difficulty: str | None = None,
          fmt: str | None = None, source: str | None = None, since: str | None = None,
          until: str | None = None, q: str | None = None, cursor: int | None = None,
          limit: int = Query(default=50, ge=1, le=100), x_learner: str | None = Header(default=None)) -> dict:
    learner, subject = learner_of(x_learner), _subject(subject)
    names = review.math_topics(subject)
    misses = review.latest_misses(learner, subject)
    rows = []
    for t in db.rows("SELECT * FROM traps WHERE learner=? AND closed IS NOT NULL"
                     " AND closed_how!='discarded' ORDER BY id DESC", learner):
        if t["topic"] not in names:
            continue
        miss = misses.get((t["template"], t["norm"]))
        opened = dt.datetime.fromisoformat(t["opened"])
        closed = dt.datetime.fromisoformat(t["closed"])
        rows.append({**dict(t), **_meta(t["template"], t["seed"] or 0, t["topic"], names),
                     "label": review.trap_label(t), "kind": review.trap_kind(t, miss),
                     "at": t["closed"], "days_to_fix": max(0, (closed-opened).days),
                     "source": review.source_of(miss["session"]) if miss else t["source"]})
    out = _filtered_page(rows, topics=topics, difficulty=difficulty, fmt=fmt, source=source,
                         since=since, until=until, q=q, cursor=cursor, limit=limit)
    counts = review.counts(learner, 0, subject)
    out.update({"subject": subject, "stats": {k: counts[k] for k in
                ("fixed", "fixed_week", "median_days", "relapsed", "dismissed", "recovered_month")}})
    return out


def _history_rows(learner: str, subject: str) -> list[dict]:
    names = review.math_topics(subject)
    where, args = review.in_subject("a.topic", subject)
    sessions = {}
    flagged = {(f["session"], f["qid"]) for f in db.rows(
        "SELECT session,qid FROM flags WHERE learner=?", learner)}
    out = []
    for a in db.rows(f"SELECT a.* FROM attempts a WHERE a.learner=? AND {where} ORDER BY a.id DESC",
                     learner, *args):
        sid = a["session"]
        if sid not in sessions:
            sessions[sid] = db.one("SELECT * FROM sessions WHERE id=?", sid) if sid else None
        session = sessions[sid]
        if session and session["kind"] == "spot":
            continue
        cfg = json.loads(session["cfg"] or "{}") if session and session["cfg"] else {}
        if cfg.get("inline"):
            continue
        meta = _meta(a["template"], a["seed"], a["topic"], names)
        card = _card(a["template"], a["seed"]) or {}
        result = "repeat" if a["repeat"] else "repaired" if a["repair"] else "right" if a["correct"] else "wrong"
        if a["void"]:
            result = "discarded"
        tries = db.rows("SELECT correct FROM tries WHERE learner=? AND session=? AND qid=?",
                        learner, sid, a["qid"]) if sid and a["qid"] else []
        if len(tries) > 1 and len({r["correct"] for r in tries}) > 1 and result != "discarded":
            result = "mixed"
        out.append({**meta, "id": a["id"], "at": a["at"], "correct": bool(a["correct"]),
                    "result": result, "given": a["given"], "given_label": review.given_label(a["fmt"], a["given"]),
                    "answer": card.get("answer"), "mistake": review.cap(a["reason"]),
                    "ms": a["ms"] or a["sms"], "source": review.source_of(sid, session),
                    "session": sid, "qid": a["qid"], "flagged": (sid, a["qid"]) in flagged,
                    "repeat": bool(a["repeat"]), "tries": len(tries), "void": a["void"]})
    return out


def _history_response(learner: str, subject: str, topics: str | None, difficulty: str | None,
                      fmt: str | None, source: str | None, since: str | None, until: str | None,
                      q: str | None, result: str | None, cursor: int | None, limit: int,
                      group: str | None, tz: int) -> dict:
    rows = [x for x in _history_rows(learner, subject) if
            _matches(x, topics=topics, difficulty=difficulty, fmt=fmt, source=source,
                     since=since, until=until, q=q)]
    if result:
        rows = [x for x in rows if x["result"] in _csv(result)]
    valid = [x for x in rows if x["void"] is None]
    timed = [x["ms"] for x in valid if x["ms"] is not None]
    by_diff = Counter(x["difficulty"] for x in valid)
    summary = {"answers": len(valid), "right": sum(x["correct"] for x in valid),
               "accuracy": round(sum(x["correct"] for x in valid) / len(valid), 3) if valid else None,
               "median_ms": statistics.median(timed) if timed else None,
               "timed": len(timed), "repaired": sum(x["result"] == "repaired" for x in valid),
               "repeats": sum(x["repeat"] for x in valid),
               "mixed": sum(x["result"] == "mixed" for x in valid),
               "by_difficulty": dict(by_diff)}
    days = defaultdict(lambda: {"questions": 0, "right": 0, "minutes": 0})
    for x in valid:
        day = review.local_day(x["at"], tz).isoformat()
        days[day]["questions"] += 1
        days[day]["right"] += x["correct"]
        days[day]["minutes"] += (x["ms"] or 0) / 60000
    day_rows = [{"day": k, **v} for k, v in sorted(days.items(), reverse=True)]
    page = _page(rows, limit, cursor)
    page["total"] = len(rows)
    page.update({"subject": subject, "summary": summary, "days": day_rows})
    if group == "sitting":
        by_sid = defaultdict(list)
        for x in rows:
            by_sid[x["session"]].append(x)
        sittings = []
        for sid, own in by_sid.items():
            s = db.one("SELECT * FROM sessions WHERE id=?", sid) if sid else None
            sittings.append({"session": sid, "kind": s["kind"] if s else "practice",
                             "source": own[0]["source"], "topics": sorted({x["topic"] for x in own}),
                             "at": max(x["at"] for x in own), "right": sum(x["correct"] for x in own),
                             "asked": len(own), "minutes": round(sum((x["ms"] or 0) for x in own) / 60000, 1),
                             "cells": [{"qid": x["qid"], "n": i, "result": x["result"],
                                        "flagged": x["flagged"], "blank": x["given"] in (None, "")}
                                       for i, x in enumerate(reversed(own), 1)],
                             "void": s["abandoned"] if s else None,
                             "rematch_of": s["rematch_of"] if s and "rematch_of" in s.keys() else None})
        page["sittings"] = sorted(sittings, key=lambda x: x["at"], reverse=True)
    return page


@router.get("/api/review/history")
def history(subject: str = "math", topics: str | None = None, difficulty: str | None = None,
            fmt: str | None = None, source: str | None = None, since: str | None = None,
            until: str | None = None, q: str | None = None, result: str | None = None,
            group: str | None = None, cursor: int | None = None,
            limit: int = Query(default=50, ge=1, le=100), x_learner: str | None = Header(default=None),
            x_tz: int = Depends(tz_of)) -> dict:
    if group not in (None, "day", "sitting"):
        bad("group")
    return _history_response(learner_of(x_learner), _subject(subject), topics, difficulty, fmt,
                             source, since, until, q, result, cursor, limit, group, x_tz)


@router.get("/api/review/history.csv")
def history_csv(subject: str = "math", topics: str | None = None, difficulty: str | None = None,
                fmt: str | None = None, source: str | None = None, since: str | None = None,
                until: str | None = None, q: str | None = None, result: str | None = None,
                x_learner: str | None = Header(default=None), x_tz: int = Depends(tz_of)) -> Response:
    rows = _history_response(learner_of(x_learner), _subject(subject), topics, difficulty, fmt,
                             source, since, until, q, result, None, 1000000, None, x_tz)["items"]
    out = io.StringIO()
    fields = ("id", "at", "template", "seed", "topic", "difficulty", "result", "given", "answer",
              "mistake", "ms", "source", "session", "qid", "flagged", "repeat")
    w = csv.DictWriter(out, fieldnames=fields, extrasaction="ignore")
    w.writeheader()
    w.writerows(rows)
    return Response(out.getvalue(), media_type="text/csv", headers={"Content-Disposition":
                    'attachment; filename="review-history.csv"'})


def _attempts(learner: str, template: str, seed: int | None = None) -> list[dict]:
    sql = "SELECT * FROM attempts WHERE learner=? AND template=?"
    args: list = [learner, template]
    if seed is not None:
        sql += " AND seed=?"
        args.append(seed)
    return [dict(x) for x in db.rows(sql + " ORDER BY id DESC", *args)]


def _attempt_view(a: dict) -> dict:
    return {"id": a["id"], "at": a["at"], "seed": a["seed"], "correct": bool(a["correct"]),
            "given": a["given"], "given_label": review.given_label(a["fmt"], a["given"]),
            "reason": a["reason"], "norm": a["norm"], "diag": a["diag"],
            "result": "discarded" if a["void"] else "repeat" if a["repeat"] else
                      "repaired" if a["repair"] else "right" if a["correct"] else "wrong",
            "ms": a["ms"] or a["sms"], "source": review.source_of(a["session"]),
            "session": a["session"], "qid": a["qid"], "repeat": bool(a["repeat"]),
            "repair": bool(a["repair"]), "revealed": bool(a["revealed_at"]),
            "openable": bool(a["revealed_at"] or a["correct"])}


@router.get("/api/review/item")
def item(template: str, seed: int = Query(ge=0), x_learner: str | None = Header(default=None)) -> dict:
    learner = learner_of(x_learner)
    topic = known(template)
    access = deps.access(learner, template, seed)
    if access is None:
        raise HTTPException(404, "no such question of yours")
    q = _card(template, seed)
    if q is None:
        raise HTTPException(404, "no such question")
    attempts = _attempts(learner, template, seed)
    family = _attempts(learner, template)
    clean = [a for a in family if a["void"] is None]
    timed = [a["ms"] or a["sms"] for a in clean if a["ms"] or a["sms"]]
    trap_rows = db.rows("SELECT * FROM traps WHERE learner=? AND template=? AND closed IS NULL ORDER BY last DESC",
                        learner, template)
    note = db.one("SELECT note,marks FROM notes WHERE learner=? AND template=? AND seed=?",
                  learner, template, seed)
    saved = db.one("SELECT 1 FROM saved WHERE learner=? AND template=? AND seed=?",
                   learner, template, seed)
    flags = db.rows("SELECT session,qid FROM flags WHERE learner=? AND template=? AND seed=?",
                    learner, template, seed)
    last = attempts[0] if attempts else None
    fresh = bool(last and not last["correct"] and not last["diag"] and
                 review.is_new(last, {}))
    choices = []
    if fresh:
        seen = set()
        for reason in q.get("reasons") or []:
            norm = progress.norm(reason or "")
            if reason and norm not in seen:
                choices.append({"id": norm, "text": review.cap(reason)})
                seen.add(norm)
        choices.extend({"id": k, "text": v} for k, v in
                       (("misread", "I misread it"), ("slip", "Arithmetic slip"),
                        ("gap", "I did not know how to start")))
        import random
        random.Random(last["id"]).shuffle(choices)
    story = []
    for event in db.rows("SELECT * FROM trap_log WHERE learner=? AND template=? ORDER BY id",
                         learner, template):
        story.append({"at": event["at"], "event": event["event"], "attempt": event["attempt"],
                      "pts": event["pts"]})
    return {"template": template, "seed": seed, "topic": topic, "question": public(q),
            "answer": q["answer"] if access == "reveal" else None,
            "rationale": q["rationale"] if access == "reveal" else None,
            "reasons": review.option_labels(q) if access == "reveal" else None,
            "attempts": [_attempt_view(a) for a in attempts],
            "family": {"seen": len(clean), "right": sum(a["correct"] for a in clean),
                       "repaired": sum(a["repair"] for a in clean), "repeats": sum(a["repeat"] for a in clean),
                       "median_ms": statistics.median(timed) if timed else None,
                       "recent": [_attempt_view(a)["result"] for a in family[:10]]},
            "traps": [{**dict(t), "label": review.trap_label(t), "status": review.status(t)} for t in trap_rows],
            "elsewhere": [{"template": t, "skill": review.skill_of(t), "topic": known(t)}
                          for tr in trap_rows for t in progress.related(tr["norm"]) if t != template][:10],
            "saved": bool(saved), "note": note["note"] if note else None,
            "marks": json.loads(note["marks"] or "[]") if note else [],
            "flagged": bool(flags), "flags": [dict(f) for f in flags],
            "address": f"{template}:{seed}", "access": access, "new": fresh,
            "revealed": bool(last and last["revealed_at"]), "diag_choices": choices,
            "story": story, "path": {k: last[k] for k in
                                       ("struck", "ms", "conf", "given") if last} if last else {},
            "summary": {"answers": len(clean)}}


@router.get("/api/review/family")
def family(template: str | None = None, session: str | None = None, question_id: str | None = None,
           norm: str | None = None, cursor: int | None = None,
           limit: int = Query(default=50, ge=1, le=100),
           x_learner: str | None = Header(default=None)) -> dict:
    learner = learner_of(x_learner)
    if session:
        row = _own(session, learner)
        if not question_id:
            bad("question_id", "required with session")
        if row["kind"] in TEST_KINDS and not row["finished"]:
            raise HTTPException(409, "after the test")
        match = next((x for x in progress._paper(row) if x.get("id") == question_id), None)
        if not match:
            raise HTTPException(404, "no such question in that session")
        if row["kind"] == "challenge" and question_id not in db.load_answers(row):
            raise HTTPException(409, "after the test")
        template = match["key"]
    if not template:
        bad("template", "send a template or a session and question_id")
    topic = known(template)
    attempts = _attempts(learner, template)
    if norm is not None:
        attempts = [a for a in attempts if a["norm"] == norm]
    clean = [a for a in attempts if a["void"] is None]
    out = _page([_attempt_view(a) for a in attempts], limit, cursor)
    out.update({"template": template, "topic": topic, "skill": review.cap(review.skill_of(template)),
                "summary": {"seen": len(clean), "right": sum(a["correct"] for a in clean),
                            "wrong": sum(not a["correct"] for a in clean),
                            "repaired": sum(a["repair"] for a in clean),
                            "repeats": sum(a["repeat"] for a in clean)},
                "attempts": out.pop("items"), "verdict": None})
    return out


@router.get("/api/review/ledger")
def ledger(subject: str = "math", weeks: int = Query(default=12, ge=1, le=52),
           x_learner: str | None = Header(default=None), x_tz: int = Depends(tz_of)) -> dict:
    return review.ledger(learner_of(x_learner), x_tz, weeks, _subject(subject))


@router.get("/api/review/calibration")
def calibration(subject: str = "math", since: str | None = None, until: str | None = None,
                x_learner: str | None = Header(default=None), x_tz: int = Depends(tz_of)) -> dict:
    for field, value in (("since", since), ("until", until)):
        if value:
            try:
                dt.date.fromisoformat(value)
            except ValueError:
                bad(field, "use YYYY-MM-DD")
    return review.calibration(learner_of(x_learner), x_tz, since, until, _subject(subject))


@router.get("/api/review/trapsheet")
def trapsheet(subject: str = "math", n: int = Query(default=10, ge=1, le=10),
              x_learner: str | None = Header(default=None)) -> dict:
    return review.trapsheet(learner_of(x_learner), n, _subject(subject))


class AttemptRef(BaseModel):
    attempt_id: int = Field(ge=1)


class Why(AttemptRef):
    diag: str | None = Field(default=None, max_length=200)
    kind: str | None = Field(default=None, pattern="^(misread|slip|gap|skip)$")
    guess: bool | None = None


def _own_attempt(learner: str, aid: int):
    row = db.one("SELECT * FROM attempts WHERE id=? AND learner=?", aid, learner)
    if row is None:
        raise HTTPException(404, "no such answer of yours")
    return row


@router.post("/api/review/seen")
def seen(body: AttemptRef, x_learner: str | None = Header(default=None)) -> dict:
    learner = writer_of(x_learner)
    a = _own_attempt(learner, body.attempt_id)
    if a["revealed_at"] is None:
        db.run("UPDATE attempts SET revealed_at=? WHERE id=? AND learner=? AND revealed_at IS NULL",
               now(), body.attempt_id, learner)
    return {"revealed_at": db.one("SELECT revealed_at FROM attempts WHERE id=?", body.attempt_id)["revealed_at"]}


@router.post("/api/review/why")
def why(body: Why, x_learner: str | None = Header(default=None)) -> dict:
    learner = writer_of(x_learner)
    a = _own_attempt(learner, body.attempt_id)
    if a["correct"]:
        raise HTTPException(409, "this answer was right")
    accepted = {"misread", "slip", "gap", "skip"}
    accepted.update(json.loads(a["offered"] or "[]"))
    if a["norm"]:
        accepted.add(a["norm"])
    if body.diag is not None and body.diag not in accepted:
        bad("diag", "choose a misconception offered by this question or a general cause")
    with db.atomic():
        if body.diag is not None:
            db.run("UPDATE attempts SET diag=?, miss_kind=CASE WHEN ? IN ('misread','slip','gap','skip')"
                   " THEN ? ELSE miss_kind END WHERE id=? AND learner=? AND diag IS NULL",
                   body.diag, body.diag, body.diag, body.attempt_id, learner)
        if body.kind is not None:
            db.run("UPDATE attempts SET miss_kind=? WHERE id=? AND learner=?", body.kind, body.attempt_id, learner)
        if body.guess is not None:
            db.run("UPDATE attempts SET guess=? WHERE id=? AND learner=?", int(body.guess), body.attempt_id, learner)
    a = _own_attempt(learner, body.attempt_id)
    trap = db.one("SELECT * FROM traps WHERE learner=? AND template=? AND norm=?", learner,
                  a["template"], a["norm"])
    return {"called": bool(a["diag"] and a["diag"] == a["norm"]), "norm": a["norm"],
            "label": review.trap_label(trap) if trap else review.cap(a["reason"]),
            "cause": a["miss_kind"], "diag": a["diag"], "guess": bool(a["guess"])}


class Walk(BaseModel):
    session: str | None = Field(default=None, max_length=64)
    ids: list[int] | None = None
    new: bool = False


@router.post("/api/review/walk")
def walk(body: Walk, x_learner: str | None = Header(default=None)) -> dict:
    learner = writer_of(x_learner)
    if body.session:
        s = _own(body.session, learner)
        if not s["finished"]:
            raise HTTPException(409, "after the test")
        attempts = db.rows("SELECT * FROM attempts WHERE learner=? AND session=? AND correct=0"
                           " AND void IS NULL AND repeat=0 ORDER BY id", learner, body.session)
    elif body.ids is not None:
        if len(body.ids) > 120:
            bad("ids", "at most 120 mistakes")
        attempts = []
        for tid in body.ids:
            t = _trap(learner, tid)
            a = db.one("SELECT * FROM attempts WHERE learner=? AND template=? AND norm=? AND correct=0"
                       " AND void IS NULL ORDER BY id DESC LIMIT 1", learner, t["template"], t["norm"])
            if a:
                attempts.append(a)
    else:
        attempts = db.rows("SELECT a.* FROM attempts a WHERE a.learner=? AND a.correct=0 AND a.void IS NULL"
                           " AND a.repeat=0 ORDER BY a.id DESC LIMIT 120", learner)
    if body.new:
        attempts = [a for a in attempts if review.is_new(dict(a), {})]
    entries = []
    for a in attempts:
        if deps.access(learner, a["template"], a["seed"]) != "reveal":
            continue
        entries.append({"attempt": a["id"], "template": a["template"], "seed": a["seed"],
                        "try": a["revealed_at"] is None, "diag": a["diag"]})
    if not entries:
        raise HTTPException(409, "no missed questions to walk")
    sid = drill.create(learner, {"source": "review", "pool": "items", "exact": True,
                                 "ids": [[x["template"], x["seed"]] for x in entries],
                                 "count": len(entries), "feedback": "instant"})
    row = db.one("SELECT cfg FROM sessions WHERE id=?", sid)
    cfg = json.loads(row["cfg"])
    cfg["inline"] = True
    cfg["walk"] = {"items": entries, "i": 0, "step": "try" if entries[0]["try"] else "why"}
    db.run("UPDATE sessions SET cfg=? WHERE id=? AND learner=?", json.dumps(cfg), sid, learner)
    return {"id": sid, "n": len(entries), "blanks": 0,
            "minutes": round(len(entries) * 1.5, 1)}


class WalkAt(BaseModel):
    i: int = Field(ge=0)
    step: str = Field(max_length=24)
    diag: str | None = Field(default=None, max_length=200)


@router.post("/api/review/walk/{sid}/at")
def walk_at(sid: str, body: WalkAt, x_learner: str | None = Header(default=None)) -> dict:
    learner = writer_of(x_learner)
    row = _own(sid, learner)
    cfg = json.loads(row["cfg"] or "{}")
    data = cfg.get("walk")
    if not cfg.get("inline") or not isinstance(data, dict):
        raise HTTPException(409, "this is not a Review walk")
    if body.i >= len(data.get("items") or []):
        bad("i", "outside this walk")
    if body.step not in ("try", "why", "key", "prove", "done"):
        bad("step")
    if body.diag:
        attempt = data["items"][body.i]["attempt"]
        why(Why(attempt_id=attempt, diag=body.diag), x_learner)
    data.update({"i": body.i, "step": body.step})
    db.run("UPDATE sessions SET cfg=? WHERE id=? AND learner=?", json.dumps(cfg), sid, learner)
    return {"ok": True}


@router.post("/api/session/{sid}/void")
def void_sitting(sid: str, x_learner: str | None = Header(default=None)) -> dict:
    learner = writer_of(x_learner)
    row = _own(sid, learner)
    if row["contest"] or row["kind"] == "challenge":
        raise HTTPException(409, "contest and challenge results cannot be discarded")
    if row["kind"] != "drill" and (row["kind"] not in TEST_KINDS or not row["finished"]):
        raise HTTPException(409, "finish this test first")
    if db.one("SELECT 1 FROM attempts WHERE learner=? AND session=? AND void='discarded' LIMIT 1",
              learner, sid):
        raise HTTPException(409, "this sitting was already discarded")
    return progress.discard(learner, sid)


@router.post("/api/session/{sid}/unvoid")
def unvoid_sitting(sid: str, x_learner: str | None = Header(default=None)) -> dict:
    learner = writer_of(x_learner)
    _own(sid, learner)
    if not db.one("SELECT 1 FROM attempts WHERE learner=? AND session=? AND void='discarded' LIMIT 1",
                  learner, sid):
        raise HTTPException(409, "this sitting is not discarded")
    return progress.restore(learner, sid)


class Share(BaseModel):
    items: list[list] | None = Field(default=None, max_length=40)
    from_: dict | None = Field(default=None, alias="from")
    title: str | None = Field(default=None, max_length=80)


@router.post("/api/shares")
def share(body: Share, x_learner: str | None = Header(default=None)) -> dict:
    from . import sets
    owner = writer_of(x_learner)
    if (body.items is None) == (body.from_ is None):
        bad("items", "send items or from")
    created = sets.create(owner, sets.SetIn(kind="items", items=body.items, from_=body.from_,
                                            title=body.title))
    return {"id": created["code"], "count": created["count"], "url": created["url"]}


@router.get("/api/shares/{code}")
def shared(code: str, x_learner: str | None = Header(default=None)) -> dict:
    from . import sets
    summary = sets.get_set(code, x_learner)
    return {"id": summary["code"], "title": summary["title"], "count": summary["count"],
            "topics": summary["topics"], "difficulties": summary["tiers"],
            "minutes": summary["minutes"]}


class Spot(BaseModel):
    trap_id: int = Field(ge=1)


class SpotAnswer(BaseModel):
    answer: int | str


@router.post("/api/review/spot")
def spot(body: Spot, x_learner: str | None = Header(default=None)) -> dict:
    learner = writer_of(x_learner)
    t = _trap(learner, body.trap_id)
    if t["closed"] or t["norm"] in progress.UNNAMED:
        raise HTTPException(409, "this mistake has no fresh version with that option")
    seen = {r["seed"] for r in db.rows("SELECT seed FROM practice_seen WHERE learner=? AND template=?",
                                       learner, t["template"])}
    seen.update(r["seed"] for r in db.rows("SELECT seed FROM attempts WHERE learner=? AND template=?",
                                           learner, t["template"]))
    cursor = (max(seen) + 1) if seen else 0
    found = None
    for seed in range(cursor, cursor + 40):
        if seed in seen or deps._protected(learner, t["template"], seed):
            continue
        q = _card(t["template"], seed)
        if (q and q["type"] == "mcq" and t["norm"] in
                {progress.norm(r) for r in q.get("reasons") or [] if r}):
            found = q
            break
    if not found:
        raise HTTPException(409, "this mistake has no fresh version with that option")
    sid = secrets.token_urlsafe(16)
    with db.atomic():
        db.run("INSERT INTO sessions(id,kind,learner,started,questions,answers,cfg) VALUES (?,?,?,?,?,'{}',?)",
               sid, "spot", learner, now(), json.dumps([found]), json.dumps({"trap_id": t["id"]}))
        db.run("INSERT OR IGNORE INTO practice_seen(learner,template,seed,stem,at) VALUES (?,?,?,?,?)",
               learner, t["template"], seed, drill._hash_of(found), now())
    return {"id": sid, "question": public(found), "prompt": review.trap_label(t)}


@router.post("/api/review/spot/{sid}")
def spot_answer(sid: str, body: SpotAnswer, x_learner: str | None = Header(default=None)) -> dict:
    learner = writer_of(x_learner)
    row = _own(sid, learner)
    if row["kind"] != "spot":
        raise HTTPException(409, "this is not a spot question")
    q = json.loads(row["questions"])[0]
    cfg = json.loads(row["cfg"] or "{}")
    trap = _trap(learner, cfg["trap_id"])
    key = "ABCD".index(q["answer"])
    got = body.answer
    if isinstance(got, str) and got.upper() in "ABCD":
        got = "ABCD".index(got.upper())
    if type(got) is not int or not 0 <= got < 4:
        bad("answer", "choose an option")
    trap_index = next((i for i, r in enumerate(q["reasons"])
                       if progress.norm(r or "") == trap["norm"]), None)
    return {"correct": got == key, "trap_index": trap_index, "answer_index": key,
            "reasons": review.option_labels(q), "rationale": q["rationale"]}
