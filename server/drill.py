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
import json
import pathlib
import re
import secrets
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
          "trap_true", "type_note", "ask_span")


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
    if "list" in body and "pool" in body and body["list"] != body["pool"]:
        _invalid("list", "conflicts with pool")
    aliases = {"mistakes": "redo", "fixed": "checks", "templates": "new", "share": "set"}
    pool = aliases.get(body.get("pool", body.get("list", "new")), body.get("pool", body.get("list", "new")))
    if body.get("mistakes"):
        pool = "redo"
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
    levels = _list(body.get("levels", list(range(1, 8))), "levels", maximum=7)
    if not levels or any(type(n) is not int or n not in range(1, 8) for n in levels):
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
    timing = body.get("timing", "custom" if body.get("timed") and minutes else "pace" if body.get("timed") else "off")
    exact_default = pool in {"seen", "history", "saved", "marked", "items", "set"}
    cfg = {"topics": topics, "templates": templates, "count": count, "total": count,
           "tiers": tiers, "difficulty": tiers, "formats": formats, "levels": levels,
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
    if cfg["templates"]:
        queue = [t for t in queue if t in cfg["templates"]]
        items = [p for p in items if p[0] in cfg["templates"]]
    if cfg["topics"]:
        queue = [t for t in queue if topic_of(t) in cfg["topics"]]
        items = [p for p in items if topic_of(p[0]) in cfg["topics"]]
    if queue or items:
        cfg["queue"], cfg["items"] = queue, items
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
    if not selected and source in {"coach", "today", "next", "start"}:
        pick = progress.coach(learner, k=4 if source == "start" else 3, count=count or 10)
        cfg["topics"] = pick.get("topics", [])
        selected = [t for topic in cfg["topics"] for t in cat["by_topic"].get(topic, ())]
    if not selected:
        _empty("no_bank" if subject == "rw" else "no_templates")
    if not any(deps.subject_of(topic_of(t)) == subject for t in selected):
        _empty("no_bank")
    if not any(any(d in cfg["tiers"] and f in cfg["formats"] for d, f in blueprint.abilities().get(t, ())) for t in selected):
        _empty("filters_removed_all")
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

def _builder(learner: str) -> practice.Builder:
    seen, stems = db.seen_for(learner)
    b = practice.Builder(learner, seen, stems)
    # Start each template's walk past the seeds this learner has already used,
    # or one they have drilled sixty times reads as spent.
    for t, n in Counter(t for t, _ in seen).items():
        b.cursor[t] = n
    return b


def _fresh(b: practice.Builder, template: str, allowed: set[str] | None) -> practice.Card | None:
    """The next unseen item from a template, of an allowed difficulty."""
    topic = topic_of(template)
    for _ in range(12):
        card = b.draw(template, topic)
        if card is None:
            return None
        if not allowed or card.feats["difficulty"] in allowed:
            return card
        b.keep(card)              # not this one; move the template past it
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
    if rep:
        card = _fresh(b, rep, None)
        if card:
            return card, True

    # a saved question, served again exactly
    while cfg.get("items"):
        template, seed = cfg["items"].pop(0)
        try:
            return practice.Card.of(template, seed, generate(template, seed), topic_of(template)), False
        except Exception:
            continue

    # templates queued by a report or the mistakes list
    while cfg.get("queue"):
        card = _fresh(b, cfg["queue"].pop(0), None)
        if card:
            return card, True

    topics = cfg.get("topics") or []
    by_topic = practice.catalogue()["by_topic"]
    used = Counter(q["key"] for q in served)
    recent = [SimpleNamespace(feats=q["feats"]) for q in served[-practice.WINDOW:] if "feats" in q]
    last_keys = {q["key"] for q in served[-3:]}

    for _ in range(len(topics)):
        topic = topics[cfg.get("turn", 0) % len(topics)]
        cfg["turn"] = cfg.get("turn", 0) + 1
        pool = [t for t in by_topic.get(topic, []) if _tiers_of(t) & allowed] or by_topic.get(topic, [])

        # an open mistake in this topic is asked before anything new
        for trap in progress.open_traps(learner, topic):
            if trap["template"] in pool and trap["template"] not in last_keys:
                card = _fresh(b, trap["template"], allowed)
                if card:
                    return card, False

        # otherwise the least used templates, tie-broken per session so two
        # sessions do not open on the same one
        salt = row["id"]
        ranked = sorted(pool, key=lambda t: (used[t], zlib.crc32(f"{salt}:{t}".encode())))
        cards = [c for c in (_fresh(b, t, allowed) for t in ranked[:practice.CANDIDATES]) if c]
        if cards:
            return min(cards, key=lambda c: practice.penalty(c, recent, dict(used))), False
    return None, False


def _serve(row, cfg: dict, served: list[dict]) -> dict | None:
    b = _builder(row["learner"])
    card, repair = _pick(row, cfg, served, b)
    if card is None:
        return None
    q = practice.to_question(card, len(served) + 1)
    q["id"] = f"d{len(served) + 1:03d}"
    q["feats"] = card.feats
    q["repair"] = repair
    served.append(q)
    db.remember(row["learner"], [{"key": card.key, "seed": card.seed,
                                  "stem_hash": practice.stem_hash(card.item.stem)}], progress.now())
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
        return _feedback(q, given, ok, reason, [], [], None, None, cfg, answers, served)

    before = progress.topic_mastery(row["learner"], q["topic"])
    filed = progress.record(row["learner"], row["id"], q, given, ms)
    after = progress.topic_mastery(row["learner"], q["topic"])
    answers = _answers(row["id"])

    # one repair per question: a missed repair stays an open mistake for later,
    # or a student who keeps missing would never reach the end of the set
    if not filed["correct"] and not cfg.get("fixed") and not q.get("repair"):
        cfg["repair"] = q["key"]
        if cfg.get("total") is not None:
            cfg["total"] += 1                        # the set grows to fit the repair
    _save(row["id"], cfg, served)
    return _feedback(q, given, filed["correct"], filed["reason"], filed["opened"],
                     filed["closed"], before, after, cfg, answers, served)


def _feedback(q, given, ok, reason, opened, closed, before, after, cfg, answers, served) -> dict:
    run = 0
    for x in reversed([x for x in served if x["id"] in answers]):
        if not scoring.is_correct(x, answers[x["id"]]):
            break
        run += 1
    mistake = reason[:1].upper() + reason[1:] if reason else None
    return {
        "correct": ok, "given": given,
        "answer": q["answer"],
        "answer_index": "ABCD".index(q["answer"]) if q["type"] == "mcq" else None,
        "mistake": mistake,
        "rationale": q["rationale"],
        "skill": q.get("skill"),
        "opened": opened, "closed": closed,
        "mastery": None if before is None else {"topic": q["topic"], "before": before, "after": after},
        "total": cfg.get("total"), "answered": len(answers), "streak": run,
    }


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
