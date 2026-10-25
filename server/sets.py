"""Question sets shared by link (R18(c); v2-upgrades P22, U28, V17, W20, X22).

One table, one code (8 characters of Crockford base32), four kinds:

  set    a practice set: a drill of the owner's, explicit (template, seed)
         pairs, a slot list, or one template (U28's "Send a twin")
  test   a finished test sitting's questions, module by module
  items  exact questions from Review, with the sharer's own context when they
         ask for help (V17)
  words  a word list (W20)

A set is exact (everyone gets the owner's (template, seed) pairs) or fresh
(cfg.fresh): each taker gets their own seed per slot, same template, tier and
format, walking up to 40 seeds for one that offers the named mistake the
sharer made there. Exact pairs pass deps.access for the owner when shared and
again when served, so a live test, today's challenge or an open contest item
never goes out by link.

GET /api/sets/{code} is public and never carries a stem, a key or the
sharer's context; an item's context is released to a visitor once they have
answered it. The owner reads per-question right rates and the most common
named mistake from GET /api/sets/{code}/results; DELETE stops the link (410).

Hooks for the engines: serve(code, learner, fresh) is what a start serves
(POST /api/drill {pool:'set', ids: code}, and the tests' shared start), and
link(sid, code, show_name) marks the taker's session (sessions.shared_from),
which is how takers are found. POST /api/sets/{code}/start does both for the
/s/ landing. peers(sid, learner) is a taker's comparison
(Tests' peers, Practice's "You vs everyone who took it").
"""

from __future__ import annotations

import functools
import hashlib
import json
import math
import re
import secrets
import sqlite3
import statistics
import zlib
from collections import Counter
from typing import Literal

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from . import blueprint, db, deps, practice, progress
from .deps import now

router = APIRouter()

ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"          # Crockford base32: no I, L, O, U
CODE_OK = re.compile(r"^[0-9A-HJKMNP-TV-Z]{8}$")
TYPO = str.maketrans("OIL", "011")
MAX_ITEMS = 40             # Review's exact shares
MAX_SLOTS = 120            # the longest drill
MAX_WORDS = 1000           # W19's list import cap
PER_HOUR = 30              # new sets per owner
WALK = 40                  # seeds walked for a twin that keeps the trap (V17)
SEED_TRIES = 60
SPAN = 100_000             # below the Library's example seeds (900000+)
TIERS = ("easy", "medium", "hard")
FMTS = ("mcq", "spr")
FEEDBACK = ("instant", "retry", "end")
SECONDS = deps.PACE                  # a question's seconds, per subject
MODULE_MIN = {s: v["module_seconds"] // 60 for s, v in blueprint.SPEC.items()}   # a test module, per subject
CFG_KEYS = {"fresh", "slots", "templates", "count", "context", "note", "feedback", "timed", "minutes"}
TITLE = {"set": "A set from a friend", "items": "A set from a friend",
         "test": "A test from a friend", "words": "Words from a friend"}
KIND = {"drill": "Practice", "challenge": "Challenge", "mock": "Full section", "section": "Full section",
        "module": "Module", "diagnostic": "Diagnostic", "custom": "Custom test", "paper": "Paper",
        "words": "Words"}
WORD_OK = re.compile(r"^[a-z][a-z' -]{0,40}(\.[a-z0-9_-]{1,30})?$")


def _json(text, default=None):
    try:
        return json.loads(text) if text else default
    except ValueError:
        return default


@functools.lru_cache(maxsize=4096)
def _item(template: str, seed: int):
    from satbank.registry import generate
    return generate(template, seed)


def _topic(template: str) -> str:
    from satbank.registry import topic_of
    return topic_of(template)


def _names() -> dict:
    return practice.catalogue()["topics"]


def _norms(it) -> set[str]:
    reasons = list(it.reasons) + [getattr(m, "reason", "") for m in getattr(it, "spr_mistakes", ())]
    return {progress.norm(r) for r in reasons if r}


def _code(raw: str) -> str:
    return (raw or "").strip().upper().translate(TYPO)


def _name(learner: str | None) -> str | None:
    row = db.one("SELECT name FROM learners WHERE id=?", learner) if learner else None
    return (row["name"] or None) if row else None


def _row(code: str):
    """The set, or 404 (never made, or its owner deleted their data) / 410 (stopped)."""
    code = _code(code)
    row = db.one("SELECT * FROM sets WHERE code=?", code) if CODE_OK.match(code) else None
    if row is None:
        raise HTTPException(404, {"reason": "unknown", "detail": "That link doesn't lead to anything."})
    return row


def _live(code: str):
    row = _row(code)
    if row["revoked"]:
        raise HTTPException(410, {"reason": "revoked", "detail": "Whoever shared this has stopped sharing it."})
    return row


def _mine(row, learner: str):
    if row["owner"] != learner:
        raise HTTPException(403, "only the person who shared this can see that")
    return row


# ------------------------------------------------------------------ what a set holds

def _describe(template: str, seed: int | None, tier: str | None = None, fmt: str | None = None) -> dict:
    """One slot as stored: the address (seed None for a slot-only set), where it
    sits, and what it is. A slot-only set is described from a representative seed."""
    try:
        topic = _topic(template)
    except KeyError:
        raise HTTPException(400, f"no such template: {template}") from None
    it = None
    for s in ([seed] if seed is not None else range(12)):
        try:
            cand = _item(template, s)
        except Exception:
            continue
        if seed is not None or ((not tier or cand.difficulty == tier) and (not fmt or cand.fmt == fmt)):
            it = cand
            break
        it = it or cand
    if it is None:
        raise HTTPException(400, f"{template} can't make that question")
    # a slot left open (tier or format None) stays open: any tier, any format
    return {"template": template, "seed": seed, "topic": topic,
            "tier": it.difficulty if seed is not None else tier,
            "fmt": it.fmt if seed is not None else fmt, "skill": it.skill}


def _paper(row) -> list[dict]:
    """A sitting's questions in order, each with its module; repairs left out."""
    if row["kind"] in ("drill", "challenge"):
        return [q for q in _json(row["questions"], []) if not q.get("repair")]
    if row["kind"] == "mock":
        from .api_tests import mock_module
        try:
            return ([{**q, "module": 1} for q in mock_module(row, 1)]
                    + [{**q, "module": 2} for q in (mock_module(row, 2) if row["route"] or row["module"] == 2 else [])])
        except KeyError:
            return []
    paper = deps.paper_of(row)
    if isinstance(paper, dict):
        return [{**q, "module": m} for m, key in ((1, "module1"), (2, "module2")) for q in paper.get(key, [])]
    return [{"module": 1, **q} for q in paper if isinstance(q, dict)]


def _allowed(owner: str, template: str, seed: int) -> bool:
    return deps.access(owner, template, seed) in ("reveal", "kept")


def _bad(template: str, seed: int) -> bool:
    removed = deps.part("reports", "removed")
    return bool(removed and removed(template, seed))


def _last_miss(owner: str, template: str, seed: int):
    """The owner's latest wrong answer on this item, else their latest answer."""
    return (db.one("SELECT * FROM attempts WHERE learner=? AND template=? AND seed=? AND correct=0"
                   " ORDER BY id DESC LIMIT 1", owner, template, seed)
            or db.one("SELECT * FROM attempts WHERE learner=? AND template=? AND seed=?"
                      " ORDER BY id DESC LIMIT 1", owner, template, seed))


def _context(owner: str, item: dict, note: bool) -> dict | None:
    """V17: what the sharer picked and why, built from their own attempts."""
    from .reports import _from_bank, _shown
    a = _last_miss(owner, item["template"], item["seed"])
    if a is None:
        return None
    src = db.one("SELECT kind FROM sessions WHERE id=?", a["session"]) if a["session"] else None
    fam = db.one("SELECT COUNT(*) AS n, COALESCE(SUM(correct),0) AS r FROM attempts WHERE learner=? AND template=?",
                 owner, item["template"])
    ctx = {"pick": _shown(_from_bank(item["template"], item["seed"]), a["given"]),
           "correct": bool(a["correct"]), "mistake": a["reason"] or None, "when": a["at"],
           "source": KIND.get(src["kind"], "Practice") if src else "Practice",
           "family": {"seen": fam["n"], "right": fam["r"]}}
    if note:
        got = db.one("SELECT note FROM notes WHERE learner=? AND template=? AND seed=?",
                     owner, item["template"], item["seed"])
        ctx["note"] = got["note"] if got and got["note"] else None
    return ctx


def _from_session(owner: str, sid: str, kind: str, only, fresh: bool) -> tuple[list[dict], dict]:
    row = deps.mine(deps.session_or_404(sid), owner)
    if row["kind"] == "challenge" or row["contest"]:
        raise HTTPException(409, "a challenge or contest can't be shared; race friends in Compete instead")
    if kind == "test":
        if row["kind"] not in deps.TEST_KINDS:
            raise HTTPException(422, "share a practice set as kind 'set'")
        if not row["finished"]:
            raise HTTPException(409, "finish the test first")
    elif row["kind"] != "drill":
        raise HTTPException(422, "share a test sitting as kind 'test'")
    qs = _paper(row)
    if only is not None:
        qs = [q for q in qs if q.get("id") in set(only)]
    items, dropped = [], 0
    for q in qs:
        if "key" not in q:
            continue
        if not fresh and not _allowed(owner, q["key"], q["seed"]):
            dropped += 1            # a question whose key this learner hasn't been shown
            continue
        items.append({"template": q["key"], "seed": q["seed"], "topic": q.get("topic") or _topic(q["key"]),
                      "tier": q.get("difficulty"), "fmt": q.get("type", "mcq"),
                      "skill": practice.skill_of(q), "qid": q.get("id"), "module": q.get("module", 1)})
    if kind == "test" and dropped:
        raise HTTPException(409, "some of this test's questions can't be shared yet")
    if not items:
        raise HTTPException(409, "answer a question first: only questions you've seen can be shared")
    cfg = _json(row["cfg"], {}) or {}
    keep = {"session": row["id"], "source_kind": row["kind"], "dropped": dropped}
    if kind == "test":
        keep["route"] = row["route"]
    else:
        keep.update({k: cfg[k] for k in ("feedback", "timed", "seconds") if cfg.get(k) is not None})
    return items, keep


def _pairs(owner: str, body: "SetIn", cap: int) -> list[dict]:
    raw = body.items
    if body.from_ is not None:
        resolve = deps.part("drill", "resolve")
        src = body.from_
        if resolve is None:
            raise HTTPException(501, {"reason": "list_resolver_unavailable"})
        if not isinstance(src, dict) or not isinstance(src.get("list"), str):
            raise HTTPException(422, "from is {list, ids}")
        raw = (resolve(owner, {"pool": src["list"], "ids": src.get("ids"), "exact": True}) or {}).get("items") or []
    if not isinstance(raw, list) or not raw:
        raise HTTPException(422, "items are [[template, seed], ...]")
    if len(raw) > cap:
        raise HTTPException(422, f"at most {cap} questions")
    out, seen = [], set()
    for x in raw:
        if isinstance(x, dict):
            x = [x.get("template"), x.get("seed")]
        if (not isinstance(x, (list, tuple)) or len(x) != 2 or not isinstance(x[0], str)
                or not isinstance(x[1], int) or isinstance(x[1], bool)):
            raise HTTPException(422, "items are [[template, seed], ...]")
        if tuple(x) in seen:
            continue
        seen.add(tuple(x))
        if not _allowed(owner, x[0], x[1]):
            # never shown to the sharer, or live somewhere now (a test, today's challenge, a contest)
            raise HTTPException(409, {"reason": "not_shareable", "template": x[0], "seed": x[1]})
        out.append(_describe(x[0], x[1]))
    return out


def _slots_in(cfg: dict) -> list[dict]:
    """Slots given as [[template, tier, fmt]] or {templates, count} (U28)."""
    if cfg.get("templates"):
        ts, count = cfg["templates"], cfg.get("count", 1)
        if (not isinstance(ts, list) or not all(isinstance(t, str) for t in ts)
                or not isinstance(count, int) or not 1 <= count <= MAX_SLOTS):
            raise HTTPException(422, "templates is a list of names, count 1-120")
        return [_describe(ts[i % len(ts)], None) for i in range(count)]
    slots = cfg.get("slots")
    if not isinstance(slots, list) or not 1 <= len(slots) <= MAX_SLOTS:
        raise HTTPException(422, "say what to share: a session, items, slots or templates")
    out = []
    for s in slots:
        s = list(s) + [None] * 3 if isinstance(s, list) else None
        if (not s or not isinstance(s[0], str) or s[1] not in (None, *TIERS) or s[2] not in (None, *FMTS)):
            raise HTTPException(422, "slots are [[template, tier, fmt]]")
        out.append(_describe(s[0], None, s[1], s[2]))
    return out


def _words(owner: str, raw) -> list[dict]:
    """Library slugs as they are; an own word ('own:ID') copied, so the link
    still works if the owner edits or deletes it."""
    if not isinstance(raw, list) or not 1 <= len(raw) <= MAX_WORDS:
        raise HTTPException(422, f"words are 1-{MAX_WORDS} slugs")
    out, seen = [], set()
    for w in raw:
        if not isinstance(w, str):
            raise HTTPException(422, "words are slugs")
        if w.startswith("own:"):
            r = db.one("SELECT * FROM my_words WHERE id=? AND learner=?", w[4:], owner)
            if r is None:
                raise HTTPException(404, f"no such word of yours: {w[4:]}")
            entry = {"word": r["word"], "meaning": r["meaning"], "pos": r["pos"],
                     "example": r["example"], "own": True}
            key = "own:" + (r["word"] or "").lower()
        else:
            slug = w.strip().lower()
            if not WORD_OK.match(slug):
                raise HTTPException(422, f"not a word: {w[:40]}")
            entry, key = {"slug": slug}, slug
        if key not in seen:
            seen.add(key)
            out.append(entry)
    return out


def _slot_list(items: list[dict], owner: str, fresh: bool) -> list[list]:
    """cfg.slots for the engines: [template, tier, fmt, want]. want is the norm
    of the sharer's miss on that item, so their twin offers the same trap."""
    out = []
    for it in items:
        want = None
        if fresh and it.get("seed") is not None:
            a = _last_miss(owner, it["template"], it["seed"])
            want = a["norm"] if a is not None and not a["correct"] and a["norm"] else None
        out.append([it["template"], it["tier"], it["fmt"], want])
    return out


# ------------------------------------------------------------------ POST /api/sets

class SetIn(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")
    kind: Literal["set", "test", "items", "words"] = "set"
    session: str | None = Field(default=None, max_length=80)
    only: list[str] | None = Field(default=None, max_length=MAX_SLOTS)
    items: list | None = Field(default=None, max_length=MAX_WORDS)
    from_: dict | None = Field(default=None, alias="from")
    cfg: dict = Field(default_factory=dict)
    title: str | None = Field(default=None, max_length=80)
    show_score: bool = True
    show_name: bool = True


def _new_code() -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(8))


def create(owner: str, body: SetIn) -> dict:
    cfg_in = body.cfg or {}
    unknown = set(cfg_in) - CFG_KEYS
    if unknown:
        raise HTTPException(422, f"unknown cfg field: {sorted(unknown)[0]}")
    kind, fresh = body.kind, bool(cfg_in.get("fresh"))
    cfg: dict = {}
    if kind == "words":
        items, fresh = _words(owner, body.items), False
    elif body.session:
        if kind == "items":
            raise HTTPException(422, "items are shared by address; a whole set is kind 'set'")
        items, cfg = _from_session(owner, body.session, kind, body.only, fresh)
    elif kind == "test":
        raise HTTPException(422, "a test is shared from its sitting: send session")
    elif body.items is not None or body.from_ is not None:
        items = _pairs(owner, body, MAX_ITEMS if kind == "items" else MAX_SLOTS)
    elif kind == "set":
        items, fresh = _slots_in(cfg_in), True          # only slots: nothing exact to hand out
    else:
        raise HTTPException(422, "say which questions: items or from")
    if kind != "words":
        if cfg_in.get("feedback") in FEEDBACK:
            cfg["feedback"] = cfg_in["feedback"]
        if isinstance(cfg_in.get("timed"), bool):
            cfg["timed"] = cfg_in["timed"]
        minutes = cfg_in.get("minutes")
        if isinstance(minutes, int) and 1 <= minutes <= 180:
            cfg["seconds"] = minutes * 60
        cfg["fresh"] = fresh
        if fresh:
            cfg["slots"] = _slot_list(items, owner, fresh)
    if kind == "items" and cfg_in.get("context"):
        cfg["context"], cfg["note"] = True, bool(cfg_in.get("note"))
        for it in items:
            it["ctx"] = _context(owner, it, cfg["note"])
    addr = [[i.get("template"), i.get("seed")] if "template" in i else i for i in items]
    cfg["sig"] = hashlib.sha1(json.dumps([kind, body.session, addr, fresh, cfg.get("context"),
                                          cfg.get("note")], sort_keys=True).encode()).hexdigest()[:20]
    title = (body.title or "").strip() or None
    again = db.one("SELECT * FROM sets WHERE owner=? AND revoked IS NULL AND json_extract(cfg,'$.sig')=?",
                   owner, cfg["sig"])
    if again is not None:                # sharing the same thing twice gives the same link
        db.run("UPDATE sets SET show_score=?, show_name=?, title=COALESCE(?, title) WHERE code=?",
               int(body.show_score), int(body.show_name), title, again["code"])
        return _made(again["code"], kind, items, fresh, True)
    hour = db.one("SELECT COUNT(*) AS n FROM sets WHERE owner=? AND created>=?", owner, _hour_ago())["n"]
    if hour >= PER_HOUR:
        raise HTTPException(429, "that's a lot of links in an hour; try again later")
    for _ in range(8):
        code = _new_code()
        try:
            db.run("INSERT INTO sets(code,owner,kind,session,items,cfg,title,show_score,show_name,created)"
                   " VALUES (?,?,?,?,?,?,?,?,?,?)", code, owner, kind, body.session,
                   json.dumps(items, ensure_ascii=False), json.dumps(cfg), title,
                   int(body.show_score), int(body.show_name), now())
            return _made(code, kind, items, fresh, False)
        except sqlite3.IntegrityError:
            continue
    raise HTTPException(503, "couldn't make a link; try again")


def _hour_ago() -> str:
    import datetime as dt
    return (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=1)).isoformat(timespec="seconds")


def _made(code: str, kind: str, items: list, fresh: bool, reused: bool) -> dict:
    return {"code": code, "url": f"/s/?c={code}", "kind": kind, "count": len(items),
            "fresh": fresh, "reused": reused}


@router.post("/api/sets")
def post_set(body: SetIn, x_learner: str | None = Header(default=None)) -> dict:
    return create(deps.writer_of(x_learner), body)


# ------------------------------------------------------------------ takers

def _takers(code: str) -> list:
    # ponytail: sessions.shared_from has no index (db.py is F4's); add one when sets are busy.
    # The cfg match finds a POST /api/drill {pool:'set'} start the engine never link()ed.
    return db.rows("SELECT * FROM sessions WHERE (shared_from=? OR CASE WHEN json_valid(cfg) THEN"
                   " json_extract(cfg,'$.pool')='set' AND json_extract(cfg,'$.ids')=? END)"
                   " AND abandoned IS NULL AND learner NOT LIKE 'sample:%' ORDER BY started", code, code)


def _firsts(sid: str) -> dict:
    out: dict = {}
    for a in db.rows("SELECT * FROM attempts WHERE session=? ORDER BY id", sid):
        out.setdefault(a["qid"], a)
    return out


def _mark(a) -> dict | None:
    if a is None:
        return None
    return {"correct": bool(a["correct"]), "ms": a["ms"], "norm": a["norm"] or None,
            "reason": a["reason"] or None, "given": a["given"]}


def _marks(srow, set_row, items: list[dict], fresh: bool) -> list[dict | None]:
    """What one sitting did on each of the set's questions, in order. Exact
    questions are matched by address; twins by position (repairs left out). A
    test's module 2 only lines up when the taker earned the sharer's route."""
    qs, firsts = _paper(srow), _firsts(srow["id"])
    by_pair = {(q.get("key"), q.get("seed")): q for q in qs}
    route = _json(set_row["cfg"], {}).get("route")
    out = []
    for i, it in enumerate(items):
        if not fresh and it.get("seed") is not None:
            q = by_pair.get((it["template"], it["seed"]))
        else:
            q = qs[i] if i < len(qs) else None
            if q is not None and q.get("key") != it["template"]:
                q = None
        if q is not None and it.get("module", 1) == 2 and set_row["kind"] == "test" and srow["route"] != route:
            q = None
        out.append(_mark(firsts.get(q["id"])) if q else None)
    return out


def _owner_marks(set_row, items: list[dict], fresh: bool) -> list[dict | None] | None:
    """The sharer's own row: their sitting, or their first answer on each address."""
    if set_row["session"]:
        src = db.one("SELECT * FROM sessions WHERE id=?", set_row["session"])
        return _marks(src, set_row, items, fresh) if src else None
    if all(it.get("seed") is None for it in items):
        # U28's question link names only the template: the sharer's row is their
        # latest answer on it before sharing ("You: right in 1:12 · Sam: ...")
        if len(items) != 1:
            return None
        return [_mark(db.one("SELECT * FROM attempts WHERE learner=? AND template=? AND at<=? ORDER BY id DESC LIMIT 1",
                             set_row["owner"], items[0]["template"], set_row["created"]))]
    return [_mark(db.one("SELECT * FROM attempts WHERE learner=? AND template=? AND seed=? ORDER BY id LIMIT 1",
                         set_row["owner"], it["template"], it["seed"])) if it.get("seed") is not None else None
            for it in items]


def _person(srow, marks) -> dict:
    got = [m for m in marks if m]
    result = _json(srow["result"], {}) or {}
    return {"right": sum(m["correct"] for m in got), "asked": len(got),
            "ms": sum(m["ms"] or 0 for m in got) or None, "at": srow["started"],
            "finished": srow["finished"], "session": srow["id"],
            "band": result.get("estimate") if isinstance(result.get("estimate"), (int, float)) else None}


def _opened(code: str) -> int:
    return db.one("SELECT COUNT(*) AS n FROM kv WHERE k>=? AND k<?", f"set.open:{code}:", f"set.open:{code};")["n"]


def _open(code: str, viewer: str) -> None:
    """Count a visitor once, by a hash: the set keeps no one's id."""
    h = hashlib.sha256(f"{code}:{viewer}".encode()).hexdigest()[:16]
    db.run("INSERT OR IGNORE INTO kv(k,v) VALUES (?,?)", f"set.open:{code}:{h}", now())


def _stats(set_row) -> dict:
    """taken: finished by someone other than the sharer; tried: started and
    answered at least one; avg_right is shown from two finishers up, so one
    friend's score is never public."""
    rows = [r for r in _takers(set_row["code"]) if r["learner"] != set_row["owner"]]
    done = [r for r in rows if r["finished"]]
    tried = {r["learner"] for r in rows if db.one("SELECT 1 FROM attempts WHERE session=?", r["id"])}
    rights = [(_json(r["result"], {}) or {}).get("right") for r in done]
    rights = [x for x in rights if isinstance(x, (int, float))]
    return {"taken": len({r["learner"] for r in done}), "tried": len(tried),
            "avg_right": round(statistics.mean(rights), 1) if len(rights) >= 2 else None}


# ------------------------------------------------------------------ GET /api/sets/{code}

def _minutes(set_row, items: list[dict], cfg: dict) -> int:
    subject = deps.infer_subject([i.get("template") for i in items])
    if set_row["kind"] == "test":
        return MODULE_MIN[subject] * len({i.get("module", 1) for i in items})
    if cfg.get("timed") and cfg.get("seconds"):
        return cfg["seconds"] // 60
    return max(1, math.ceil(len(items) * SECONDS[subject] / 60))


def summary(set_row, viewer: str | None = None) -> dict:
    items, cfg = _json(set_row["items"], []), _json(set_row["cfg"], {}) or {}
    kind = set_row["kind"]
    out = {"code": set_row["code"], "kind": kind, "url": f"/s/?c={set_row['code']}",
           "title": set_row["title"] or TITLE[kind],
           "by": _name(set_row["owner"]) if set_row["show_name"] else None,
           "created": set_row["created"], "count": len(items), "mine": viewer == set_row["owner"]}
    if kind == "words":
        out["words"] = items
        return out
    names = _names()
    topics = Counter(i["topic"] for i in items)
    out.update({
        "fresh": bool(cfg.get("fresh")),
        "topics": [{"topic": t, "name": names[t].name if t in names else t, "n": n} for t, n in topics.items()],
        "tiers": {t: sum(i.get("tier") == t for i in items) for t in TIERS},
        "formats": {f: sum(i.get("fmt") == f for i in items) for f in FMTS},
        "minutes": _minutes(set_row, items, cfg),
        "timed": bool(cfg.get("timed")) or kind == "test",
        "feedback": "end" if kind == "test" else cfg.get("feedback", "instant"),
        "help": bool(cfg.get("context")),
        **_stats(set_row),
    })
    if kind == "test":
        src = cfg.get("source_kind")
        out["kind_label"] = KIND.get(src, "Test")
        out["modules"] = [sum(i.get("module", 1) == m for i in items) for m in (1, 2) if any(i.get("module", 1) == m for i in items)]
        out["show_score"] = bool(set_row["show_score"])
    if viewer and viewer != set_row["owner"]:
        mine = [r for r in _takers(set_row["code"]) if r["learner"] == viewer]
        if mine:
            r = mine[-1]
            p = _person(r, _marks(r, set_row, items, bool(cfg.get("fresh"))))
            out["yours"] = {"session": r["id"], "kind": r["kind"], "finished": r["finished"],
                            "right": p["right"], "asked": p["asked"]}
        if cfg.get("context"):
            # a twin (a fresh share, or "Fresh versions instead") is matched by position
            slots = [_marks(r, set_row, items, True) for r in mine]
            ctx = []
            for n, it in enumerate(items, 1):
                # released once this visitor has answered the question, or its twin, themselves
                if it.get("ctx") and (any(m[n - 1] for m in slots) or db.one(
                        "SELECT 1 FROM attempts WHERE learner=? AND template=? AND seed=?",
                        viewer, it["template"], it["seed"])):
                    ctx.append({"n": n, **it["ctx"]})
            if ctx:
                out["context"] = ctx
    return out


@router.get("/api/sets/{code}")
def get_set(code: str, x_learner: str | None = Header(default=None)) -> dict:
    row = _live(code)
    viewer = None
    if x_learner:
        try:
            viewer = deps.learner_of(x_learner)
        except HTTPException:
            viewer = None           # the summary is public; a stale code still reads it
    if viewer and viewer != row["owner"] and not db.is_sample(viewer):
        _open(row["code"], viewer)
    return summary(row, viewer)


@router.get("/api/sets")
def my_sets(x_learner: str | None = Header(default=None)) -> list[dict]:
    """The owner's links, newest first, with how far each has gone."""
    owner = deps.learner_of(x_learner)
    out = []
    for r in db.rows("SELECT * FROM sets WHERE owner=? ORDER BY created DESC LIMIT 200", owner):
        items, cfg = _json(r["items"], []), _json(r["cfg"], {}) or {}
        out.append({"code": r["code"], "kind": r["kind"], "url": f"/s/?c={r['code']}",
                    "title": r["title"] or TITLE[r["kind"]], "count": len(items),
                    "fresh": bool(cfg.get("fresh")), "session": r["session"], "created": r["created"],
                    "revoked": r["revoked"], "opened": _opened(r["code"]),
                    **({} if r["kind"] == "words" else _stats(r))})
    return out


# ------------------------------------------------------------------ results (owner)

def _table(set_row) -> tuple[list[dict], bool, list[dict | None] | None, list[tuple]]:
    items, cfg = _json(set_row["items"], []), _json(set_row["cfg"], {}) or {}
    fresh = bool(cfg.get("fresh"))
    people = [(r, _marks(r, set_row, items, fresh)) for r in _takers(set_row["code"])
              if r["learner"] != set_row["owner"]]
    return items, fresh, _owner_marks(set_row, items, fresh), people


def _top_wrong(marks: list[dict], exact: bool, item: dict) -> dict | None:
    """The most common named mistake; for exact questions, with the answer picked."""
    named = [m for m in marks if not m["correct"] and m["norm"]]
    if not named:
        return None
    norm, count = Counter(m["norm"] for m in named).most_common(1)[0]
    group = [m for m in named if m["norm"] == norm]
    out = {"reason": group[-1]["reason"], "norm": norm, "count": count}
    if exact and item.get("seed") is not None:
        from .reports import _from_bank, _shown
        given = Counter(m["given"] for m in group).most_common(1)[0][0]
        out["given"] = _shown(_from_bank(item["template"], item["seed"]), given)
    return out


def _median(xs) -> int | None:
    xs = [x for x in xs if x]
    return int(statistics.median(xs)) if xs else None


def results(set_row) -> dict:
    items, fresh, own, people = _table(set_row)
    kind, names = set_row["kind"], _names()
    questions = []
    for i, it in enumerate(items):
        got = [m[i] for _, m in people if m[i]]
        right = sum(m["correct"] for m in got)
        questions.append({
            "n": i + 1, "template": it["template"], "type_name": it.get("skill"), "topic": it["topic"],
            "topic_name": names[it["topic"]].name if it["topic"] in names else it["topic"],
            "difficulty": it.get("tier"), "fmt": it.get("fmt"), "module": it.get("module", 1),
            "right": right, "asked": len(got), "rate": round(right / len(got), 3) if got else None,
            "median_ms": _median(m["ms"] for m in got if m["correct"]),
            "top_wrong": _top_wrong(got, not fresh, it),
            "you": {"correct": own[i]["correct"], "ms": own[i]["ms"]} if own and own[i] else None,
        })
    takers = []
    for r, m in people:
        cfg = _json(r["cfg"], {}) or {}
        takers.append({**_person(r, m), "you": False,
                       "name": _name(r["learner"]) if cfg.get("show_name") else None,
                       "marks": [None if x is None else int(x["correct"]) for x in m]})
    stats = _stats(set_row)
    finished = [t for t in takers if t["finished"]]
    out = {"code": set_row["code"], "kind": kind, "title": set_row["title"] or TITLE[kind],
           "fresh": fresh, "created": set_row["created"], "revoked": set_row["revoked"],
           "count": len(items), "opened": _opened(set_row["code"]), **stats,
           "avg_right": round(statistics.mean(t["right"] for t in finished), 1) if finished else None,
           "median_ms": _median(t["ms"] for t in finished),
           "questions": questions, "takers": takers}
    if own:
        got = [x for x in own if x]
        out["you"] = {"right": sum(x["correct"] for x in got), "asked": len(got),
                      "ms": sum(x["ms"] or 0 for x in got) or None,
                      "marks": [None if x is None else int(x["correct"]) for x in own]}
    return out


@router.get("/api/sets/{code}/results")
def get_results(code: str, x_learner: str | None = Header(default=None)) -> dict:
    row = _mine(_row(code), deps.learner_of(x_learner))
    if row["kind"] == "words":
        raise HTTPException(409, "a word list has no results")
    return results(row)


@router.delete("/api/sets/{code}")
def delete_set(code: str, x_learner: str | None = Header(default=None)) -> dict:
    row = _mine(_row(code), deps.writer_of(x_learner))
    db.run("UPDATE sets SET revoked=? WHERE code=? AND revoked IS NULL", now(), row["code"])
    return {"code": row["code"], "revoked": db.one("SELECT revoked FROM sets WHERE code=?", row["code"])["revoked"]}


# ------------------------------------------------------------------ the engines' hooks

def _twins(code: str, learner: str, slots: list[list], avoid: set) -> list[list]:
    """A fresh seed per slot for this learner: same template, tier and format,
    unseen by them, and offering the sharer's trap when a seed within WALK has
    it. Each learner walks from their own start, so two takers never match."""
    seen, stems = db.seen_for(learner)
    taken: set = set()
    out = []
    for i, (template, tier, fmt, want, *_) in enumerate(list(s) + [None] * 4 for s in slots):
        start = zlib.crc32(f"{learner}:{code}:{i}".encode()) % SPAN
        first = fits = None
        for k in range(WALK if want else SEED_TRIES):
            seed = start + k
            if (template, seed) in seen or (template, seed) in taken or (template, seed) in avoid:
                continue
            try:
                it = _item(template, seed)
            except Exception:
                continue
            if practice.stem_hash(it.stem) in stems or _bad(template, seed):
                continue
            first = first if first is not None else seed
            if (tier and it.difficulty != tier) or (fmt and it.fmt != fmt):
                continue
            fits = fits if fits is not None else seed
            if not want or want in _norms(it):
                fits = seed
                break
        seed = fits if fits is not None else first
        if seed is None:
            raise HTTPException(409, {"reason": "no_twin", "template": template})
        taken.add((template, seed))
        out.append([template, seed])
    return out


def serve(code: str, learner: str, fresh: bool | None = None) -> dict:
    """What a start serves this learner. An exact set hands out the sharer's
    addresses, re-checked now; a visitor may ask for fresh versions of an exact
    set ("Fresh versions instead"), never for the exact questions of a twin set.
    404 / 410 as GET; 409 when nothing can be served."""
    row = _live(code)
    items, cfg = _json(row["items"], []), _json(row["cfg"], {}) or {}
    if row["kind"] == "words":
        return {"code": row["code"], "kind": "words", "words": items}
    exact = not cfg.get("fresh") and fresh is not True
    avoid = {(i["template"], i["seed"]) for i in items if i.get("seed") is not None}
    if exact:
        pairs = [[i["template"], i["seed"]] for i in items
                 if _allowed(row["owner"], i["template"], i["seed"]) and not _bad(i["template"], i["seed"])]
        if not pairs:
            raise HTTPException(409, {"reason": "set_unavailable"})
    else:
        pairs = _twins(row["code"], learner, cfg.get("slots") or _slot_list(items, row["owner"], True), avoid)
    return {"code": row["code"], "kind": row["kind"], "exact": exact, "items": pairs,
            "modules": [i.get("module", 1) for i in items] if row["kind"] == "test" else None,
            "route": cfg.get("route"), "title": row["title"] or TITLE[row["kind"]], "source": "shared",
            "cfg": {"count": len(pairs), "feedback": cfg.get("feedback", "instant"),
                    "timed": bool(cfg.get("timed")), "seconds": cfg.get("seconds")}}


def link(sid: str, code: str, show_name: bool = False) -> None:
    """Mark a taker's session as this set's: shared_from, and whether the
    sharer may see their name (cfg.show_name, off by default)."""
    row = deps.session_or_404(sid)
    cfg = _json(row["cfg"], {}) or {}
    cfg.update({"share": _code(code), "show_name": bool(show_name)})
    db.run("UPDATE sessions SET shared_from=?, cfg=? WHERE id=?", _code(code), json.dumps(cfg), sid)


class StartIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    exact: bool | None = None           # False: "Fresh versions instead"
    show_name: bool = False


@router.post("/api/sets/{code}/start")
def start(code: str, body: StartIn, x_learner: str | None = Header(default=None)) -> dict:
    """The landing's start: serve(), a drill of exactly those questions, link().
    Answers the way POST /api/drill does. A test starts from Tests' sheet."""
    # ponytail: F6's own start until POST /api/drill {pool:'set'} calls serve() and link()
    from . import drill
    learner = deps.writer_of(x_learner)
    if _live(code)["kind"] in ("words", "test"):
        raise HTTPException(422, "a word list opens on its page, a test from Tests")
    got = serve(code, learner, True if body.exact is False else None)
    pairs, c = got["items"], got["cfg"]
    sid = secrets.token_urlsafe(16)
    drill.create(learner, sid, list(dict.fromkeys(_topic(t) for t, _ in pairs)), len(pairs), None,
                 c["timed"], "shared", items=pairs, minutes=(c["seconds"] or 0) // 60 or None)
    row = deps.session_or_404(sid)
    db.run("UPDATE sessions SET cfg=? WHERE id=?",
           json.dumps({**(_json(row["cfg"], {}) or {}), "feedback": c["feedback"]}), sid)
    link(sid, got["code"], body.show_name)
    first = drill.next_question(deps.session_or_404(sid))
    return {**drill.state(deps.session_or_404(sid)), **first}


def peers(sid: str, learner: str) -> dict | None:
    """A taker's comparison, once their sitting is finished: everyone who sat
    this set (the sharer included), named only when they allowed it, bands only
    when the sharer allowed scores, and per question only right or wrong and
    the named mistake, never a raw answer. None for a session from no set."""
    srow = deps.mine(deps.session_or_404(sid), learner)
    set_row = (_row(srow["shared_from"]) if srow["shared_from"] else
               db.one("SELECT * FROM sets WHERE session=? AND owner=? ORDER BY created DESC LIMIT 1", sid, learner))
    if set_row is None:
        return None
    if not srow["finished"]:
        return {"code": set_row["code"], "locked": True}
    items, fresh, own, people = _table(set_row)
    names, scores = _names(), bool(set_row["show_score"])
    rows = []
    if own is not None:
        src = db.one("SELECT * FROM sessions WHERE id=?", set_row["session"]) if set_row["session"] else None
        p = _person(src, own) if src else {"right": sum(x["correct"] for x in own if x),
                                           "asked": sum(1 for x in own if x), "band": None}
        rows.append((set_row["owner"], bool(set_row["show_name"]), p, own, True))
    for r, m in people:
        if r["finished"]:
            rows.append((r["learner"], bool((_json(r["cfg"], {}) or {}).get("show_name")), _person(r, m), m, False))
    everyone = []
    for who, named, p, m, owner in rows:
        everyone.append({"name": _name(who) if named or who == learner else None, "you": who == learner,
                         "owner": owner, "right": p["right"], "asked": p["asked"],
                         "band": p.get("band") if scores or who == learner else None,
                         "marks": [None if x is None else {"correct": x["correct"],
                                                           "mistake": None if x["correct"] else x["reason"]}
                                   for x in m]})
    mine = own if set_row["session"] == sid else next((m for r, m in people if r["id"] == sid), None)
    slots = []
    for i, it in enumerate(items):
        got = [e["marks"][i] for e in everyone if e["marks"][i]]
        right = sum(x["correct"] for x in got)
        top = Counter(x["mistake"] for x in got if x["mistake"]).most_common(1)
        slots.append({"n": i + 1, "type_name": it.get("skill"), "module": it.get("module", 1),
                      "topic_name": names[it["topic"]].name if it["topic"] in names else it["topic"],
                      "right": right, "asked": len(got), "rate": round(right / len(got), 3) if got else None,
                      "you": None if not mine or not mine[i] else mine[i]["correct"],
                      "top_mistake": {"label": top[0][0], "count": top[0][1]} if top else None})
    return {"code": set_row["code"], "kind": set_row["kind"], "show_score": scores,
            "slots": slots, "people": everyone}


@router.get("/api/sets/{code}/compare")
def get_compare(code: str, x_learner: str | None = Header(default=None)) -> dict:
    """The visitor's own comparison, from their latest finished sitting of it."""
    learner = deps.learner_of(x_learner)
    row = _live(code)
    done = [r for r in _takers(row["code"]) if r["learner"] == learner and r["finished"]]
    if not done:
        raise HTTPException(403, "finish it first")
    return peers(done[-1]["id"], learner)
