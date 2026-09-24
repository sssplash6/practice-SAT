"""Practice with the answer shown: one question at a time, made when asked for.

A drill does not build its set up front. Each question is generated when the
student asks for the next one, so it can answer to what just happened:

* a wrong answer is followed by the same template on a fresh seed -- the same
  trap with new numbers -- and a set with a length grows by one to fit it;
* a template the student has an open mistake on is asked before the others;
* a set asked for with no length simply never runs out.

Everything the student is given is remembered against them, so nothing is
ever served twice, and every answer is filed through progress.record so the
map, the coach and the mistakes list move as they go.
"""

from __future__ import annotations

import datetime as dt
import functools
import json
import pathlib
import re
import secrets
import statistics
import zlib
from collections import Counter
from types import SimpleNamespace

from fastapi import HTTPException
from satbank.registry import generate, topic_of

from . import blueprint, db, deps, practice, progress, scoring

MAX_FIXED = 120             # the longest set with a length
GRACE = 15                  # seconds past a timed set's clock an answer may still arrive
TIERS = ("easy", "medium", "hard")
PUBLIC = ("id", "topic", "topic_name", "domain", "difficulty", "skill", "type",
          "stem", "choices", "latex", "figure", "table", "text", "seen", "why",
          "trap_true", "type_note", "ask_span", "level", "budget_ms", "odds")


class Closed(Exception):
    """The set is finished, or its clock ran out: nothing more is filed."""


def _cfg(row) -> dict:
    return json.loads(row["cfg"] or "{}")


def _served(row) -> list[dict]:
    return json.loads(row["questions"] or "[]")


def _save(sid: str, cfg: dict, served: list[dict]) -> None:
    db.run("UPDATE sessions SET cfg=?, questions=? WHERE id=?",
           json.dumps(cfg), json.dumps(served, ensure_ascii=False), sid)


def public(q: dict) -> dict:
    out = {k: q[k] for k in PUBLIC if k in q}
    out["repair"] = bool(q.get("repair"))
    return out


# One resolver is used by preview and creation. It does not write a session or
# reserve a seed; in particular, a failed request leaves no empty sitting.
POOLS = {"new", "redo", "checks", "review", "untried", "seen", "saved",
         "marked", "history", "items", "set", "related", "official"}
SOURCES = {"map", "coach", "plan", "today", "mistakes", "review", "quick",
           "palette", "outside", "twin", "try", "word-example", "words",
           "worksheet", "shared", "qotd", "spot", "start", "due", "warmup",
           "learn", "next", "prep", "probe", "habit", "gauntlet", "finish",
           "official", "challenge", "rematch", "test", "result"}
INLINE = {"twin", "try", "word-example", "review", "spot"}
FIELDS = {"topics", "templates", "exclude", "want", "count", "tiers", "levels",
          "unmeasured", "formats", "spr_share", "adaptive", "order", "mix", "pool",
          "list", "ids", "exact", "each", "level", "result", "marked", "from",
          "from_session", "only", "scope", "still_open", "until_fixed", "retake",
          "again", "item", "timed", "minutes", "timing", "feedback", "repairs",
          "source", "task", "parent", "like", "word", "confusion", "contest",
          "unseen", "trap", "format", "fmt", "difficulty", "saved", "share",
          "mistakes", "recheck", "subject", "first", "drop", "run", "box",
          "habit", "topics_from", "zone", "budget_ms", "has", "item"}


def _invalid(field: str, detail: str = "invalid value") -> None:
    raise HTTPException(422, {"field": field, "reason": detail})


def _empty(reason: str) -> None:
    raise HTTPException(409, {"reason": reason})


def _list(value, field, *, maximum=120) -> list:
    if not isinstance(value, list) or len(value) > maximum:
        _invalid(field, f"expected a list of at most {maximum}")
    return value


def _choices(value, field, choices: set[str], *, many=False):
    if many:
        value = _list(value, field)
        if not value or any(not isinstance(v, str) or v not in choices for v in value):
            _invalid(field, f"choose from {', '.join(sorted(choices))}")
        return list(dict.fromkeys(value))
    if not isinstance(value, str) or value not in choices:
        _invalid(field, f"choose from {', '.join(sorted(choices))}")
    return value


def _pairs(value, field) -> list[list]:
    rows = _list(value, field)
    if any(not isinstance(p, (list, tuple)) or len(p) != 2 or
           not isinstance(p[0], str) or not isinstance(p[1], int) or p[1] < 0
           for p in rows):
        _invalid(field, "expected [template, seed] pairs")
    return [list(p) for p in rows]


def _source_questions(learner: str, sid: str) -> list[dict]:
    row = db.one("SELECT * FROM sessions WHERE id=?", sid)
    if not row or row["learner"] != learner:
        raise HTTPException(404, "no such session")
    if not row["finished"] and row["kind"] == "diagnostic":
        raise HTTPException(403, "finish and sign up before fixing this diagnostic")
    if not row["finished"]:
        _empty("finish_that_sitting_first")
    raw = json.loads(row["questions"] or "[]")
    if isinstance(raw, dict):
        raw = [q for v in raw.values() if isinstance(v, list) for q in v]
    return [q for q in raw if isinstance(q, dict) and "key" in q]


def _pool(learner: str, cfg: dict, body: dict) -> tuple[list[str], list[list], dict[str, str]]:
    pool, ids = cfg["pool"], cfg.get("ids")
    queue: list[str] = []
    items: list[list] = []
    why: dict[str, str] = {}
    if body.get("from_session") and pool == "seen" and not body.get("exact"):
        source = db.one("SELECT * FROM sessions WHERE id=?", body["from_session"])
        questions = _source_questions(learner, body["from_session"])
        answers = db.load_answers(source)
        only = body.get("only")
        if only is not None:
            only = _list(only, "only")
            if any(not isinstance(qid, str) or qid not in {q["id"] for q in questions} for qid in only):
                _invalid("only", "unknown question id")
        for q in questions:
            if only is not None and q["id"] not in only:
                continue
            scope = body.get("scope", "misses")
            if scope == "misses" and scoring.is_correct(q, answers.get(q["id"])):
                continue
            if scope == "blanks" and answers.get(q["id"]) not in (None, ""):
                continue
            if body.get("still_open") and not db.one(
                    "SELECT 1 FROM traps WHERE learner=? AND template=? AND closed IS NULL",
                    learner, q["key"]):
                continue
            queue.append(q["key"])
            why[q["key"]] = "missed in that sitting" if scope == "misses" else "from that sitting"
            a = db.one("SELECT norm FROM attempts WHERE learner=? AND session=? AND qid=?"
                       " ORDER BY id DESC LIMIT 1", learner, body["from_session"], q["id"])
            if a and a["norm"] and not a["norm"].startswith("~"):
                cfg["want"].setdefault(q["key"], "^" + re.escape(a["norm"]) + "$")
        if not queue:
            _empty("nothing_was_missed" if body.get("scope", "misses") == "misses" else "pool_empty")
        return queue, items, why
    if pool == "new":
        return queue, items, why
    if pool in {"redo", "checks"}:
        today = dt.datetime.now(dt.timezone.utc).date().isoformat()
        traps = progress.open_traps(learner) if pool == "redo" else [dict(r) for r in db.rows(
            "SELECT * FROM traps WHERE learner=? AND closed IS NOT NULL AND due<=? AND checks<3",
            learner, today)]
        if ids is not None:
            allowed = set(str(x) for x in _list(ids, "ids"))
            traps = [t for t in traps if str(t["id"]) in allowed]
        for t in traps:
            queue.append(t["template"])
            why[t["template"]] = "open mistake" if pool == "redo" else "check-in due"
            if t.get("norm") and not str(t["norm"]).startswith("~"):
                cfg["want"].setdefault(t["template"], "^" + re.escape(t["norm"]) + "$")
        if not queue:
            _empty("no_open_mistakes" if pool == "redo" else "no_checks_due")
    elif pool == "review":
        cutoff = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=10)).isoformat()
        queue = [r["template"] for r in db.rows(
            "SELECT DISTINCT a.template FROM attempts a WHERE a.learner=? AND a.correct=1"
            " AND a.at<=? AND NOT EXISTS (SELECT 1 FROM traps t WHERE t.learner=a.learner"
            " AND t.template=a.template AND t.closed IS NULL)", learner, cutoff)]
        why.update((t, "due for review") for t in queue)
    elif pool == "untried":
        counts = {r["template"]: r["n"] for r in db.rows(
            "SELECT template, COUNT(*) n FROM attempts WHERE learner=? GROUP BY template", learner)}
        all_t = [t for ts in practice.catalogue()["by_topic"].values() for t in ts]
        queue = [t for t in all_t if t not in counts]
        if not queue:
            least = min(counts.values(), default=0)
            queue = [t for t in all_t if counts.get(t, 0) == least]
        why.update((t, "not tried" if t not in counts else "least answered") for t in queue)
    elif pool in {"seen", "history"}:
        sql = "SELECT * FROM attempts WHERE learner=?"
        args: list = [learner]
        if pool == "history" and ids is not None:
            wanted = _list(ids, "ids")
            if any(not isinstance(i, int) for i in wanted):
                _invalid("ids", "history uses attempt ids")
            if wanted:
                sql += " AND id IN (" + ",".join("?" for _ in wanted) + ")"
                args += wanted
        selected_qids = None
        if body.get("from_session"):
            questions = _source_questions(learner, body["from_session"])
            if body.get("only") is not None:
                selected_qids = _list(body["only"], "only")
                if any(not isinstance(qid, str) or qid not in {q["id"] for q in questions} for qid in selected_qids):
                    _invalid("only", "unknown question id")
            sql += " AND session=?"
            args.append(body["from_session"])
        if body.get("result") in {"missed", "right"}:
            sql += " AND correct=?"
            args.append(int(body["result"] == "right"))
        elif body.get("result") == "guessed":
            sql += " AND guess=1"
        if body.get("from") == "tests":
            sql += " AND session IN (SELECT id FROM sessions WHERE kind IN ('diagnostic','module','section','mock','custom'))"
        elif body.get("from") == "practice":
            sql += " AND session IN (SELECT id FROM sessions WHERE kind='drill')"
        if body.get("marked"):
            sql += " AND EXISTS (SELECT 1 FROM flags f WHERE f.learner=attempts.learner AND f.template=attempts.template AND f.seed=attempts.seed)"
        if body.get("still_open"):
            sql += " AND EXISTS (SELECT 1 FROM traps t WHERE t.learner=attempts.learner"
            " AND t.template=attempts.template AND t.closed IS NULL)"
        for r in db.rows(sql + " ORDER BY id DESC LIMIT 500", *args):
            if selected_qids is not None and r["qid"] not in selected_qids:
                continue
            if body.get("scope") == "blanks" and r["given"] not in (None, ""):
                continue
            items.append([r["template"], r["seed"]])
    elif pool == "saved":
        items = [[r["template"], r["seed"]] for r in db.rows(
            "SELECT template,seed FROM saved WHERE learner=? ORDER BY at DESC", learner)]
    elif pool == "marked":
        items = [[r["template"], r["seed"]] for r in db.rows(
            "SELECT template,seed FROM flags WHERE learner=? ORDER BY at DESC", learner)]
    elif pool == "items":
        items = _pairs(ids or [], "ids")
    elif pool == "set":
        code = ids or body.get("share")
        if not isinstance(code, str):
            _invalid("ids", "a set code is required")
        row = db.one("SELECT items,revoked FROM sets WHERE code=?", code)
        if not row or row["revoked"]:
            _empty("set_unavailable")
        raw = json.loads(row["items"] or "[]")
        items = [[x["template"], x["seed"]] if isinstance(x, dict) else list(x) for x in raw]
        _pairs(items, "ids")
    elif pool == "related":
        norm = ids if isinstance(ids, str) else None
        if not norm:
            _invalid("ids", "a mistake norm is required")
        related = progress.related(norm)
        queue = [x["template"] if isinstance(x, dict) else x for x in related]
        cfg["want"].update({t: "^" + re.escape(norm) + "$" for t in queue})
    elif pool == "official":
        wanted = _list(ids or [], "ids", maximum=50)
        if not wanted or any(not isinstance(x, str) for x in wanted):
            _invalid("ids", "use 1–50 College Board ids")
        found = {}
        root = pathlib.Path(__file__).resolve().parent.parent / "material" / "keys"
        for path in root.glob("*.json"):
            data = json.loads(path.read_text())
            for entry in data.get("items", []):
                if entry.get("cb_id") in wanted:
                    found[entry["cb_id"]] = data.get("slug", path.stem)
        if set(wanted) - set(found):
            _invalid("ids", "unknown College Board id")
        for cbid in wanted:
            names = practice.catalogue()["by_topic"].get(found[cbid], ())
            if not names:
                _empty("no_bank")
            queue.append(names[0])
            why[names[0]] = f"like official question {cbid}"
    if cfg.get("exact"):
        if queue and not items:
            _invalid("exact", "this pool has no exact question addresses")
        for t, seed in items:
            if deps.access(learner, t, seed) is None:
                raise HTTPException(403, {"reason": "question_not_accessible", "template": t, "seed": seed})
    else:
        queue += [t for t, _ in items]
        items = []
    if not queue and not items:
        _empty("pool_empty")
    return queue, items, why


def resolve(learner: str, body: dict) -> dict:
    """Validate every drill field, resolve aliases and materialize the pool."""
    if not isinstance(body, dict):
        _invalid("body", "expected an object")
    unknown = set(body) - FIELDS
    if unknown:
        _invalid(sorted(unknown)[0], "unknown field")
    if "assignment" in body:
        _invalid("assignment", "classes are not part of this product")
    body = dict(body)
    for name, module in (("like", "daily"), ("word", "words"), ("confusion", "words")):
        if name in body:
            resolver = deps.part(module, "resolve_drill")
            if resolver is None:
                raise HTTPException(501, {"reason": f"{module}_resolver_unavailable"})
            body = resolver(learner, body)
    if body.get("source") == "warmup":
        body["source"] = "due"
        body.setdefault("count", 5)
    if body.get("source") == "start":
        body.setdefault("count", 8)
        body.setdefault("adaptive", True)
        body.setdefault("feedback", "instant")
        body.setdefault("repairs", "next")
    if body.get("source") == "probe":
        body.setdefault("count", 8)
        body.setdefault("adaptive", True)
        body.setdefault("feedback", "end")
    if "list" in body and "pool" in body and body["list"] != body["pool"]:
        _invalid("list", "conflicts with pool")
    aliases = {"mistakes": "redo", "fixed": "checks", "templates": "new", "share": "set"}
    pool = aliases.get(body.get("pool", body.get("list", "new")), body.get("pool", body.get("list", "new")))
    if body.get("mistakes"):
        pool = "redo"
        body.setdefault("each", 2)
    if body.get("saved"):
        pool = "saved"
        body.setdefault("exact", True)
    if body.get("recheck"):
        pool = "checks"
    if body.get("unseen"):
        pool = "untried"
    if body.get("share"):
        pool = "set"
    if body.get("trap"):
        trap = body["trap"]
        if not isinstance(trap, dict) or not isinstance(trap.get("template"), str):
            _invalid("trap", "expected template and reason")
        row = db.one("SELECT id FROM traps WHERE learner=? AND template=? AND closed IS NULL"
                     " ORDER BY last DESC LIMIT 1", learner, trap["template"])
        pool = "redo"
        body["ids"] = [row["id"]] if row else []
    if body.get("from_session") and pool == "new":
        pool = "seen"
        body.setdefault("result", "missed" if body.get("scope", "misses") == "misses" else "any")
        body.setdefault("exact", False)
    if body.get("item") or body.get("retake"):
        pool = "items"
    pool = _choices(pool, "pool", POOLS)
    subject = _choices(body.get("subject", "math"), "subject", {"math", "rw"})
    source = _choices(body.get("source", "map"), "source", SOURCES)
    cat = practice.catalogue()
    topics = _list(body.get("topics", []), "topics")
    if any(not isinstance(t, str) for t in topics):
        _invalid("topics")
    topics = list(dict.fromkeys(topics))
    if any(t not in cat["by_topic"] for t in topics):
        _empty("no_bank") if subject == "rw" else _invalid("topics", "unknown topic")
    templates = _list(body.get("templates", []), "templates")
    if any(not isinstance(t, str) or t not in {n for v in cat["by_topic"].values() for n in v} for t in templates):
        _invalid("templates", "unknown template")
    templates = list(dict.fromkeys(templates))
    if len(templates) > 120 or any(deps.subject_of(topic_of(t)) != subject for t in templates):
        _invalid("templates", "too many templates or wrong subject")
    count = body.get("count", 10)
    if count is not None and (type(count) is not int or not 1 <= count <= MAX_FIXED):
        _invalid("count", "use 1–120 or null")
    tiers = body.get("tiers", body.get("difficulty", list(TIERS)))
    adaptive = body.get("adaptive", False)
    if tiers == "adaptive" or (isinstance(tiers, list) and "adaptive" in tiers):
        adaptive, tiers = True, [x for x in tiers if x != "adaptive"] if isinstance(tiers, list) else list(TIERS)
        tiers = tiers or list(TIERS)
    if isinstance(tiers, str):
        tiers = [tiers]
    tiers = _choices(tiers, "tiers", set(TIERS), many=True)
    fmt = body.get("formats", body.get("format", body.get("fmt", ["mcq", "spr"])))
    if isinstance(fmt, str):
        fmt = {"both": ["mcq", "spr"], "mix": ["mcq", "spr"], "grid": ["spr"],
               "mcq": ["mcq"], "spr": ["spr"]}.get(fmt, [fmt])
    formats = _choices(fmt, "formats", {"mcq", "spr"}, many=True)
    level_filter = _list(body.get("levels", list(range(1, 8))), "levels", maximum=7)
    if not level_filter or any(type(n) is not int or n not in range(1, 8) for n in level_filter):
        _invalid("levels", "use levels 1–7")
    for field in ("adaptive", "unmeasured", "exact", "timed", "marked", "still_open"):
        if field in body and type(body[field]) is not bool:
            _invalid(field, "expected true or false")
    each = body.get("each", 1)
    if type(each) is not int or not 1 <= each <= 5:
        _invalid("each", "use 1–5")
    minutes = body.get("minutes")
    if minutes is not None and (type(minutes) is not int or not 1 <= minutes <= 180):
        _invalid("minutes", "use 1–180")
    share = body.get("spr_share", .5 if body.get("format") == "mix" else None)
    if share is not None and (type(share) not in (float, int) or not 0 <= share <= 1):
        _invalid("spr_share", "use 0–1")
    if share == 0:
        formats = ["mcq"]
    elif share == 1:
        formats = ["spr"]
    want = body.get("want", {})
    if not isinstance(want, dict):
        _invalid("want", "expected {template: regex}")
    for t, pattern in want.items():
        if t not in {n for v in cat["by_topic"].values() for n in v} or not isinstance(pattern, str) or len(pattern) > 500:
            _invalid("want", "unknown template or invalid regex")
        try:
            re.compile(pattern)
        except re.error:
            _invalid("want", "invalid regex")
    exclude = _pairs(body.get("exclude", []), "exclude")
    for name, options in (("level", {"as_missed", "any", "harder"}),
                          ("result", {"any", "missed", "right", "guessed"}),
                          ("from", {"both", "practice", "tests"}),
                          ("scope", {"misses", "all", "blanks"}),
                          ("order", {"mixed", "grouped", "ramp", "given", "mixup"}),
                          ("mix", {"even", "blueprint"}),
                          ("timing", {"off", "pace", "custom"}),
                          ("feedback", {"instant", "retry", "end"}),
                          ("repairs", {"next", "end", "off"})):
        if name in body:
            _choices(body[name], name, options)
    timing = body.get("timing", "custom" if body.get("timed") and minutes else "legacy_pace" if body.get("timed") else "off")
    exact_default = pool in {"seen", "history", "saved", "marked", "items", "set"}
    cfg = {"topics": topics, "templates": templates, "count": count, "total": count,
           "tiers": tiers, "difficulty": tiers, "formats": formats, "levels": level_filter,
           "unmeasured": body.get("unmeasured", True), "adaptive": adaptive,
           "spr_share": share, "order": body.get("order", "mixed"), "mix": body.get("mix", "even"),
           "pool": pool, "ids": body.get("ids"), "exact": body.get("exact", exact_default),
           "each": each, "level": body.get("level", "as_missed"),
           "timing": timing, "timed": timing != "off", "seconds": minutes * 60 if timing == "custom" and minutes else None,
           "feedback": body.get("feedback", "instant"), "repairs": body.get("repairs", "next"),
           "source": source, "subject": subject, "inline": source in INLINE,
           "want": dict(want), "exclude": exclude, "turn": 0, "fixed": False,
           "task": body.get("task"), "parent": body.get("parent"), "run": body.get("run"),
           "from_session": body.get("from_session"), "only": body.get("only"),
           "scope": body.get("scope", "misses"), "still_open": body.get("still_open", False)}
    cfg["plan"] = _pace_plan(tiers, count)
    cfg["clock_log"] = []
    if timing == "pace" and count is not None:
        millis = sum({"easy": 65_000, "medium": 95_000, "hard": 126_000}[t] for t in cfg["plan"])
        cfg["seconds"] = ((millis + 59_999) // 60_000) * 60
    if body.get("item"):
        try:
            t, seed = body["item"].rsplit(":", 1)
            cfg["ids"] = [[t, int(seed)]]
            cfg["exact"] = True
        except (AttributeError, ValueError):
            _invalid("item", "use template:seed")
    if body.get("retake"):
        cfg["ids"] = [[q["key"], q["seed"]] for q in _source_questions(learner, body["retake"])]
        cfg["exact"] = True
    if body.get("again"):
        row = db.one("SELECT cfg FROM sessions WHERE id=? AND learner=?", body["again"], learner)
        if not row:
            raise HTTPException(404, "no such session")
        old = json.loads(row["cfg"] or "{}")
        for key in ("topics", "templates", "tiers", "formats", "pool", "source", "count"):
            if key not in body and key in old:
                cfg[key] = old[key]
    queue, items, why = _pool(learner, cfg, body)
    if source == "due" and pool == "new" and not cfg["templates"] and not cfg["topics"]:
        due = progress.warmup_candidates(learner, subject=subject)
        queue = [x.get("serve", x["template"]) for x in due["checks"]]
        queue += [x["template"] for x in due["fading"] + due["marked"]]
        for x in due["keep_warm"]:
            queue.extend(cat["by_topic"].get(x["topic"], ())[:1])
        if not queue:
            _empty("nothing_due")
        why.update((t, "spaced warm-up") for t in queue)
    if cfg["templates"]:
        queue = [t for t in queue if t in cfg["templates"]]
        items = [p for p in items if p[0] in cfg["templates"]]
    if cfg["topics"]:
        queue = [t for t in queue if topic_of(t) in cfg["topics"]]
        items = [p for p in items if topic_of(p[0]) in cfg["topics"]]
    if queue or items:
        cfg["queue"], cfg["items"] = queue, items
        cfg["pool_templates"] = list(dict.fromkeys(queue + [t for t, _ in items]))
        cfg["why"] = why
        if "count" not in body and pool != "new":
            cfg["count"] = cfg["total"] = min(MAX_FIXED, (len(queue) + len(items)) * each)
    elif pool != "new":
        _empty("filters_removed_all")
    else:
        cfg["queue"], cfg["items"], cfg["why"] = [], [], why
    selected = cfg["templates"] or [t for topic in cfg["topics"] for t in cat["by_topic"].get(topic, ())]
    selected += cfg["queue"] + [t for t, _ in cfg["items"]]
    if not selected and source == "quick":
        pick = progress.coach(learner, count=1)
        cfg["topics"] = pick.get("topics", [])[:1]
        selected = [t for topic in cfg["topics"] for t in cat["by_topic"].get(topic, ())]
    if source == "start" and not cfg["topics"] and not cfg["templates"]:
        cfg["topics"] = list(cat["by_topic"])
        selected = [t for topic in cfg["topics"] for t in cat["by_topic"][topic]]
    if not selected and source in {"coach", "today", "next"}:
        pick = progress.coach(learner, k=4 if source == "start" else 3, count=count or 10)
        cfg["topics"] = pick.get("topics", [])
        selected = [t for topic in cfg["topics"] for t in cat["by_topic"].get(topic, ())]
    if not selected:
        _empty("no_bank" if subject == "rw" else "no_templates")
    if not any(deps.subject_of(topic_of(t)) == subject for t in selected):
        _empty("no_bank")
    rated = levels()
    selected = [t for t in selected if any(
        d in cfg["tiers"] and f in cfg["formats"] and
        rated.get((t, d), {}).get("level") in cfg["levels"] and
        (cfg["unmeasured"] or not rated.get((t, d), {}).get("rough", True))
        for d, f in blueprint.abilities().get(t, ()))]
    if not selected:
        _empty("level " + ", ".join(map(str, cfg["levels"])) + " unavailable"
               if body.get("levels") else "filters_removed_all")
    if not cfg["topics"]:
        cfg["topics"] = list(dict.fromkeys(topic_of(t) for t in selected))
    cfg["before"] = {t: progress.topic_mastery(learner, t) for t in {topic_of(t) for t in selected}}
    return cfg


def preview(learner: str, body: dict) -> dict:
    """The same resolver as create, with no session or seen-item writes."""
    try:
        cfg = resolve(learner, body)
    except HTTPException as e:
        if e.status_code == 409:
            return {"available": False, "count": 0, "templates": 0, "reason": e.detail["reason"]}
        raise
    names = set(cfg["templates"] or [t for topic in cfg["topics"] for t in practice.catalogue()["by_topic"].get(topic, ())])
    names.update(cfg["queue"])
    names.update(t for t, _ in cfg["items"])
    return {"available": True, "count": cfg["count"], "templates": len(names),
            "exact": len(cfg["items"]), "pool": cfg["pool"], "topics": len({topic_of(t) for t in names}),
            "cfg": {k: cfg[k] for k in ("source", "subject", "formats", "tiers", "levels", "timing")}}


# ------------------------------------------------------------------ building

def _builder(learner: str, dedupe: str = "stem") -> practice.Builder:
    seen, stems = db.seen_for(learner)
    b = practice.Builder(learner, seen, stems, dedupe=dedupe)
    # Start each template's walk past the seeds this learner has already used,
    # or one they have drilled sixty times reads as spent.
    for t, n in Counter(t for t, _ in seen).items():
        b.cursor[t] = n
    return b


@functools.lru_cache(maxsize=8)
def _levels_at(version: tuple) -> dict[tuple[str, str], dict]:
    from . import ratings
    rows = db.rows("SELECT template,difficulty,correct,ms,reason FROM attempts WHERE repeat=0"
                   " AND disputed=0 AND void IS NULL AND guess=0 AND hints=0 AND flagged=0")
    answers: dict[tuple[str, str], list] = {}
    for r in rows:
        answers.setdefault((r["template"], r["difficulty"]), []).append(r)
    out = {}
    for template, kinds in blueprint.abilities().items():
        for tier in {t for t, _ in kinds}:
            sample = answers.get((template, tier), [])
            rating = ratings.level(template, tier)
            right_ms = sorted(r["ms"] for r in sample if r["correct"] and r["ms"] is not None)
            n = len(sample)
            out[(template, tier)] = {
                **rating, "n": n, "rate": round(sum(r["correct"] for r in sample) / n, 3) if n >= 20 else None,
                "median_ms_right": int(statistics.median(right_ms)) if right_ms else None,
                "rough": rating["rough"],
            }
    return out


def levels() -> dict[tuple[str, str], dict]:
    """Crowd result and measured level for each template and difficulty."""
    latest = db.one("SELECT MAX(id) n FROM attempts")
    return _levels_at((latest["n"] if latest else 0,))


def budget_ms(template: str, tier: str) -> int:
    default = {"easy": 65_000, "medium": 95_000, "hard": 126_000}[tier]
    measured = levels().get((template, tier), {})
    median = measured.get("median_ms_right")
    return max(round(default * .6), min(round(default * 1.6), median)) if median and measured.get("n", 0) >= 20 else default


def _pace_plan(tiers: list[str], count: int | None) -> list[str]:
    if count is None:
        return []
    weights = {"easy": 7, "medium": 8, "hard": 7}
    total = sum(weights[t] for t in tiers)
    quotas = {t: count * weights[t] / total for t in tiers}
    base = {t: int(quotas[t]) for t in tiers}
    for t in sorted(tiers, key=lambda x: (-(quotas[x] - base[x]), TIERS.index(x)))[:count - sum(base.values())]:
        base[t] += 1
    return [t for t in tiers for _ in range(base[t])]


def _offers(card: practice.Card, regex: str) -> bool:
    try:
        pattern = re.compile(regex, re.I)
    except re.error:
        return False
    reasons = list(getattr(card.item, "reasons", ()))
    reasons += [getattr(m, "reason", "") for m in getattr(card.item, "spr_mistakes", ())]
    reasons += [str(x) for x in getattr(card.item, "spr_reasons", ())]
    return any(pattern.search(r or "") or pattern.search(progress.norm(r or "")) for r in reasons)


def _fresh(b: practice.Builder, template: str, allowed: set[str] | None,
           cfg: dict | None = None) -> practice.Card | None:
    """Walk fresh seeds with every active filter; keep want on repairs too."""
    cfg = cfg or {}
    topic = topic_of(template)
    wanted = cfg.get("want", {}).get(template)
    fallback = None
    survey = levels() if cfg.get("levels") else {}
    for _ in range(60 if wanted else 24):
        card = b.draw(template, topic)
        if card is None:
            break
        tier = card.feats["difficulty"]
        measured = survey.get((template, tier), {})
        if allowed and tier not in allowed or card.item.fmt not in cfg.get("formats", ("mcq", "spr")) \
                or (cfg.get("levels") and measured.get("level") not in cfg["levels"]) \
                or (cfg.get("unmeasured") is False and measured.get("rough", True)) \
                or [template, card.seed] in cfg.get("exclude", ()):
            b.keep(card)
            continue
        adaptive = cfg.get("adaptive_state", {}).get(card.item.skill)
        if adaptive and tier != adaptive.get("tier"):
            b.keep(card)
            continue
        if wanted and not _offers(card, wanted):
            b.keep(card)
            fallback = True
            continue
        card.trap_true = bool(wanted)
        return card
    if wanted and fallback:
        plain = {**cfg, "want": {t: v for t, v in cfg.get("want", {}).items() if t != template}}
        card = _fresh(b, template, allowed, plain)
        if card:
            card.trap_true = False
        return card
    return None


def _tiers_of(template: str) -> set[str]:
    return {d for d, _ in blueprint.abilities().get(template, ())}


def _pick(row, cfg: dict, served: list[dict], b: practice.Builder):
    """The next card, and whether it is a repair."""
    allowed = set(cfg.get("difficulty") or TIERS)
    learner = row["learner"]

    # the same trap with new numbers, before anything else is asked -- even the
    # next saved question -- and a difficulty filter never blocks it
    rep = cfg.pop("repair", None)
    if rep is None and cfg.get("end_repairs") and cfg.get("count") is not None \
            and len(served) >= cfg["count"]:
        rep = cfg["end_repairs"].pop(0)
    if rep:
        rep_key = rep["template"] if isinstance(rep, dict) else rep
        if isinstance(rep, dict) and rep.get("want"):
            cfg.setdefault("want", {})[rep_key] = rep["want"]
        card = _fresh(b, rep_key, None, cfg)
        if card:
            return card, True

    # a saved question, served again exactly
    while cfg.get("items"):
        template, seed = cfg["items"].pop(0)
        try:
            if cfg.get("exact") and deps.access(learner, template, seed) is None and row["kind"] != "challenge":
                continue
            card = practice.Card.of(template, seed, generate(template, seed), topic_of(template))
            if card.item.difficulty not in allowed or card.item.fmt not in cfg.get("formats", ("mcq", "spr")):
                continue
            return card, False
        except Exception:
            continue

    # templates queued by a report or the mistakes list
    while cfg.get("queue"):
        template = cfg["queue"].pop(0)
        card = _fresh(b, template, allowed, cfg)
        if card:
            return card, cfg.get("pool") in ("redo", "checks")

    if cfg.get("source") == "start" and len(served) < 4:
        domain = ("Algebra", "Advanced Math", "Problem-Solving and Data Analysis",
                  "Geometry and Trigonometry")[len(served)]
        names = [t for t in blueprint.by_domain().get(domain, ())
                 if ("medium", "mcq") in blueprint.abilities().get(t, ())]
        ranked = sorted(names, key=lambda t: zlib.crc32(f"{row['id']}:{t}".encode()))
        for template in ranked:
            card = _fresh(b, template, {"medium"}, cfg)
            if card:
                return card, False

    topics = cfg.get("topics") or []
    by_topic = practice.catalogue()["by_topic"]
    used = Counter(q["key"] for q in served)
    recent = [SimpleNamespace(feats=q["feats"]) for q in served[-practice.WINDOW:] if "feats" in q]
    last_keys = {q["key"] for q in served[-3:]}

    for _ in range(len(topics)):
        topic = topics[cfg.get("turn", 0) % len(topics)]
        cfg["turn"] = cfg.get("turn", 0) + 1
        pool = [t for t in by_topic.get(topic, []) if _tiers_of(t) & allowed]
        if cfg.get("templates"):
            pool = [t for t in pool if t in cfg["templates"]]
        elif cfg.get("pool") not in (None, "new") and cfg.get("pool_templates"):
            pool = [t for t in pool if t in cfg["pool_templates"]]
        if cfg.get("order") == "ramp":
            index = min(len(served) * len(allowed) // max(cfg.get("count") or 10, 1), len(allowed) - 1)
            target = sorted(allowed, key=TIERS.index)[index]
            pool = [t for t in pool if target in _tiers_of(t)] or pool

        # an open mistake in this topic is asked before anything new
        for trap in progress.open_traps(learner, topic):
            if trap["template"] in pool and trap["template"] not in last_keys:
                card = _fresh(b, trap["template"], allowed, cfg)
                if card:
                    return card, False

        # otherwise the least used templates, tie-broken per session so two
        # sessions do not open on the same one
        salt = row["id"]
        ranked = sorted(pool, key=lambda t: (used[t], zlib.crc32(f"{salt}:{t}".encode())))
        cards = []
        for template in ranked:
            card = _fresh(b, template, allowed, cfg)
            if card:
                cards.append(card)
            if len(cards) >= practice.CANDIDATES:
                break
        if cards:
            wanted_share = cfg.get("spr_share")
            spr_count = sum(q.get("type") == "spr" for q in served)
            target_spr = wanted_share is not None and spr_count < round((len(served) + 1) * wanted_share)
            return min(cards, key=lambda c: practice.penalty(c, recent, dict(used)) +
                       (400 if wanted_share is not None and (c.item.fmt == "spr") != target_spr else 0)), False
    return None, False


def _serve(row, cfg: dict, served: list[dict]) -> dict | None:
    b = _builder(row["learner"], dedupe="question" if cfg.get("whole_question", True) else "stem")
    card, repair = _pick(row, cfg, served, b)
    if card is None:
        return None
    q = practice.to_question(card, len(served) + 1)
    q["id"] = f"d{len(served) + 1:03d}"
    q["feats"] = card.feats
    q["repair"] = repair
    q["trap_true"] = getattr(card, "trap_true", None)
    q["why"] = "repair of the last mistake" if repair else cfg.get("why", {}).get(card.key,
                  "open mistake" if any(t["template"] == card.key for t in progress.open_traps(row["learner"], card.topic))
                  else "varied practice")
    q["seen"] = db.one("SELECT COUNT(*) n FROM attempts WHERE learner=? AND template=?",
                       row["learner"], card.key)["n"]
    q["level"] = levels().get((card.key, q["difficulty"]), {}).get("level")
    q["budget_ms"] = budget_ms(card.key, q["difficulty"])
    from . import ratings
    q["odds"] = round(ratings.odds(row["learner"], card.key, q["difficulty"], card.topic), 3)
    if cfg.get("timing") == "pace":
        slot = len(served)
        planned = cfg.get("plan", [])
        prior = {"easy": 65_000, "medium": 95_000, "hard": 126_000}.get(
            planned[slot] if slot < len(planned) else None, 0)
        delta = q["budget_ms"] - prior
        if delta:
            cfg["seconds"] = (cfg.get("seconds") or 0) + (delta + 999) // 1000
            cfg.setdefault("clock_log", []).append({"at": progress.now(), "delta_ms": delta,
                                                     "why": "repair" if repair else "question budget"})
    served.append(q)
    db.remember(row["learner"], [{"key": card.key, "seed": card.seed,
                                  "stem_hash": practice.question_hash(card.item)}], progress.now())
    return q


# ------------------------------------------------------------------ the session

def create(learner: str, sid: str | dict, topics: list[str] | None = None,
           count: int | None = None, difficulty: list[str] | None = None,
           timed: bool = False, source: str = "map",
           queue: list[str] | None = None, items: list[list] | None = None,
           kind: str = "drill", fixed: bool = False, day: str | None = None,
           minutes: int | None = None) -> str | None:
    """A fixed set (the challenge) is the same for everyone, so it has no
    repairs and never grows; the answer is still shown after each question."""
    if isinstance(sid, dict):
        cfg = resolve(learner, sid)
        new_sid = secrets.token_urlsafe(16)
        db.run("INSERT INTO sessions (id,kind,learner,started,cfg,questions,subject)"
               " VALUES (?,?,?,?,?,'[]',?)", new_sid, "drill", learner, progress.now(),
               json.dumps(cfg), cfg["subject"])
        return new_sid
    topics = topics or []
    every = set(topics) | {topic_of(t) for t in (queue or [])} | {topic_of(t) for t, _ in (items or [])}
    cfg = {
        "topics": topics, "count": count, "total": count,
        "difficulty": [d for d in (difficulty or TIERS) if d in TIERS] or list(TIERS),
        "timed": bool(timed), "source": source, "turn": 0, "fixed": fixed,
        # the student's own clock, if they set one; otherwise the set's length decides
        "seconds": minutes * 60 if timed and minutes else None,
        "queue": list(queue or []), "items": [list(i) for i in (items or [])],
        "before": {t: progress.topic_mastery(learner, t) for t in every},
    }
    row = (sid, kind, learner, progress.now(), json.dumps(cfg), "[]", day)
    if day is None:
        db.run("INSERT INTO sessions (id, kind, learner, started, cfg, questions, day)"
               " VALUES (?,?,?,?,?,?,?)", *row)
    else:
        # A day's sitting exists once per learner. The check is inside the
        # insert, so two starts at the same moment still make one; the caller
        # reads back whichever was made.
        db.run("INSERT INTO sessions (id, kind, learner, started, cfg, questions, day)"
               " SELECT ?,?,?,?,?,?,? WHERE NOT EXISTS"
               " (SELECT 1 FROM sessions WHERE kind=? AND learner=? AND day=?)", *row, kind, learner, day)
    return None


def seconds_of(cfg: dict) -> int | None:
    """A timed set's clock: the minutes the student set, or the real test's
    pace for the set's length. An endless set is timed only by the student,
    which makes it a sprint -- as many as they can in the time."""
    if not cfg.get("timed"):
        return None
    if cfg.get("seconds"):
        return cfg["seconds"]
    if cfg.get("count"):
        return cfg["count"] * blueprint.MODULE_SECONDS // blueprint.MODULE_SIZE
    return None


def overtime(row, cfg: dict) -> bool:
    secs = seconds_of(cfg)
    if not secs:
        return False
    began = dt.datetime.fromisoformat(row["started"])
    return (dt.datetime.now(dt.timezone.utc) - began).total_seconds() > secs + GRACE


def state(row) -> dict:
    """Where a drill stands, so a reload resumes it rather than starting over."""
    cfg, served, answers = _cfg(row), _served(row), db.load_answers(row)
    current = served[-1] if served and served[-1]["id"] not in answers else None
    return {
        "id": row["id"], "mode": row["kind"], "topics": cfg.get("topics", []),
        "total": cfg.get("total"), "timed": cfg.get("timed", False),
        "seconds": seconds_of(cfg),
        "started": row["started"], "finished": row["finished"],
        "answered": len(answers),
        "marks": [scoring.is_correct(q, answers[q["id"]]) for q in served if q["id"] in answers],
        "question": public(current) if current else None,
    }


def next_question(row) -> dict:
    cfg, served, answers = _cfg(row), _served(row), db.load_answers(row)
    if served and served[-1]["id"] not in answers:
        return {"question": public(served[-1]), "index": len(served), "total": cfg.get("total")}
    if cfg.get("total") is not None and len(answers) >= cfg["total"]:
        return {"done": True, "total": cfg["total"]}
    q = _serve(row, cfg, served)
    _save(row["id"], cfg, served)
    if q is None:
        return {"done": True, "exhausted": True, "total": cfg.get("total")}
    return {"question": public(q), "index": len(served), "total": cfg.get("total")}


def _answers(sid: str) -> dict:
    return json.loads(db.one("SELECT answers FROM sessions WHERE id=?", sid)["answers"] or "{}")


def answer(row, qid: str, given, ms: int | None) -> dict:
    cfg, served = _cfg(row), _served(row)
    q = next((x for x in served if x["id"] == qid), None)
    if q is None:
        raise KeyError(qid)
    if overtime(row, cfg):
        raise Closed("time is up")
    # Claimed in one statement before anything is filed, so the same answer
    # sent twice at once -- a double tap, a retried request -- files once.
    if not db.set_answer(row["id"], qid, given, only_new=True):
        answers = _answers(row["id"])
        if qid not in answers:
            raise Closed("this set is finished")
        given = answers[qid]                          # a double tap, not a second try
        ok = scoring.is_correct(q, given)
        reason = (q.get("reasons") or [""] * 4)[given] if not ok and isinstance(given, int) and 0 <= given < 4 else ""
        return _feedback(q, given, ok, reason, [], [], None, None, cfg, answers, served,
                         learner=row["learner"])

    before = progress.topic_mastery(row["learner"], q["topic"])
    filed = progress.record(row["learner"], row["id"], q, given, ms)
    after = progress.topic_mastery(row["learner"], q["topic"])
    answers = _answers(row["id"])

    # one repair per question: a missed repair stays an open mistake for later,
    # or a student who keeps missing would never reach the end of the set
    if cfg.get("adaptive") and not q.get("repair"):
        options = [t for t in TIERS if t in cfg.get("tiers", TIERS)]
        state = cfg.setdefault("adaptive_state", {}).setdefault(q["skill"],
                   {"tier": q["difficulty"], "rights": 0})
        current = state["tier"] if state["tier"] in options else q["difficulty"]
        at = options.index(current) if current in options else 0
        if filed["correct"] and filed.get("clean"):
            state["rights"] += 1
            if state["rights"] >= 2:
                state["tier"] = options[min(at + 1, len(options) - 1)]
                state["rights"] = 0
        else:
            state["tier"] = options[max(at - 1, 0)]
            state["rights"] = 0
    if not filed["correct"] and not cfg.get("fixed") and not q.get("repair") and cfg.get("repairs", "next") != "off":
        normalized = progress.norm(filed["reason"] or "")
        want = "^" + re.escape(normalized) + "$" if normalized and not normalized.startswith("~") else None
        repair = {"template": q["key"], "want": want}
        if cfg.get("repairs") == "end":
            cfg.setdefault("end_repairs", []).append(repair)
        else:
            cfg["repair"] = repair
        if cfg.get("total") is not None:
            cfg["total"] += 1
    _save(row["id"], cfg, served)
    return _feedback(q, given, filed["correct"], filed["reason"], filed["opened"],
                     filed["closed"], before, after, cfg, answers, served, filed=filed,
                     learner=row["learner"])


def _feedback(q, given, ok, reason, opened, closed, before, after, cfg, answers, served,
              filed: dict | None = None, learner: str | None = None) -> dict:
    run = 0
    for x in reversed([x for x in served if x["id"] in answers]):
        if not scoring.is_correct(x, answers[x["id"]]):
            break
        run += 1
    mistake = reason[:1].upper() + reason[1:] if reason else None
    family = {"seen": 0, "right": 0}
    if learner:
        row = db.one("SELECT COUNT(*) seen,COALESCE(SUM(correct),0) n_right FROM attempts"
                     " WHERE learner=? AND template=?", learner, q["key"])
        family = {"seen": row["seen"], "right": row["n_right"]}
    option = q.get("step_of") or []
    chosen = option[given] if q.get("type") == "mcq" and isinstance(given, int) and 0 <= given < len(option) else None
    out = {
        "correct": ok, "given": given,
        "mistake": mistake,
        "skill": q.get("skill"),
        "opened": opened, "closed": closed,
        "opened_ids": (filed or {}).get("opened_ids", []),
        "closed_ids": (filed or {}).get("closed_ids", []),
        "checked": (filed or {}).get("checked", []),
        "relapsed": (filed or {}).get("relapsed", []),
        "not_offered": (filed or {}).get("not_offered", []),
        "reasons": [r or None for r in q.get("reasons", ())],
        "filler": q.get("filler", []),
        "family": family,
        "flagged": (filed or {}).get("flagged", False),
        "repeat": (filed or {}).get("repeat", False),
        "trap_true": q.get("trap_true"),
        "steps": q.get("steps", []),
        "diverge": chosen.get("at") if isinstance(chosen, dict) else None,
        "wrong_step": chosen.get("wrong") if isinstance(chosen, dict) else None,
        "option_steps": [s.get("at") if isinstance(s, dict) else None for s in option],
        "desmos": q.get("desmos"),
        "figure_alt": q.get("figure_alt"),
        "budget_ms": q.get("budget_ms"),
        "saved_note": "Saved for another look" if cfg.get("pool") == "saved" else None,
        "mastery": None if before is None else {"topic": q["topic"], "before": before, "after": after},
        "total": cfg.get("total"), "answered": len(answers), "streak": run,
    }
    if cfg.get("feedback", "instant") != "end":
        out["answer"] = q["answer"]
        out["answer_index"] = "ABCD".index(q["answer"]) if q["type"] == "mcq" else None
        out["rationale"] = q["rationale"]
    else:
        for key in ("reasons", "filler", "steps", "diverge", "wrong_step", "option_steps", "desmos"):
            out.pop(key, None)
    return out


def finish(row) -> dict:
    cfg = _cfg(row)
    learner = row["learner"]
    # one attempt per question, the first, whatever else reached the table
    got = db.rows("SELECT topic, correct, reason, template, ms FROM attempts WHERE id IN"
                  " (SELECT MIN(id) FROM attempts WHERE session=? GROUP BY qid) ORDER BY id", row["id"])
    names = progress.topics()
    per: dict[str, dict] = {}
    for a in got:
        d = per.setdefault(a["topic"], {"right": 0, "asked": 0})
        d["asked"] += 1
        d["right"] += a["correct"]
    topics_out = [
        {"topic": t, "name": names[t].name, "domain": names[t].domain, **v,
         "before": cfg.get("before", {}).get(t, 0.0),
         "after": progress.topic_mastery(learner, t)}
        for t, v in per.items()
    ]
    still = {(t["template"], t["label"]) for t in progress.open_traps(learner)}
    opened = []
    for t in db.rows("SELECT template, label, topic FROM traps WHERE learner=? AND opened>=?",
                     learner, row["started"]):
        if (t["template"], t["label"]) in still:
            opened.append({"topic": t["topic"], "label": t["label"]})
    closed = [{"topic": t["topic"], "label": t["label"]}
              for t in db.rows("SELECT label, topic FROM traps WHERE learner=? AND closed>=?",
                               learner, row["started"])]
    result = {
        "mode": row["kind"], "asked": len(got), "right": sum(a["correct"] for a in got),
        "topics": topics_out, "opened": opened, "closed": closed,
        "ms": sum(a["ms"] or 0 for a in got),
    }
    if not row["finished"]:
        db.run("UPDATE sessions SET finished=?, result=? WHERE id=? AND finished IS NULL",
               progress.now(), json.dumps(result), row["id"])
    return result
