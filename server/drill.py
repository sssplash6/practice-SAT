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
import hashlib
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
          "trap_true", "level", "rough", "budget_ms", "kind", "zone", "rungs", "n",
          "type_name", "about", "final", "slot_of")


class Closed(Exception):
    """The set is finished, or its clock ran out: nothing more is filed."""


class NotServed(LookupError):
    """The question id is not one this set has shown."""


def _add_ms(cfg: dict, qid: str, ms) -> None:
    """Time on a question, capped per call (progress.MS_CAP)."""
    spent = cfg.setdefault("ms", {})
    spent[qid] = spent.get(qid, 0) + min(max(0, int(ms or 0)), progress.MS_CAP)


def _cfg(row) -> dict:
    return json.loads(row["cfg"] or "{}")


def _served(row) -> list[dict]:
    return json.loads(row["questions"] or "[]")


def _save(sid: str, cfg: dict, served: list[dict]) -> None:
    db.run("UPDATE sessions SET cfg=?, questions=? WHERE id=?",
           json.dumps(cfg), json.dumps(served, ensure_ascii=False), sid)


def public(q: dict) -> dict:
    if q.get("kind") == "word":              # S9's public item, with the token /word grades
        return {k: v for k, v in q.items() if k != "served"}
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
           "official", "challenge", "rematch", "test", "result", "builder", "sprint", "gain",
          "skill", "mixup"}
INLINE = {"twin", "try", "word-example", "review", "spot"}
FIELDS = {"topics", "templates", "exclude", "want", "count", "tiers", "levels",
          "unmeasured", "formats", "spr_share", "adaptive", "order", "mix", "pool",
          "list", "ids", "exact", "each", "level", "result", "marked", "from",
          "from_session", "only", "scope", "still_open", "until_fixed", "retake",
          "again", "item", "timed", "minutes", "timing", "feedback", "repairs",
          "source", "task", "parent", "like", "word", "confusion", "contest",
          "unseen", "trap", "format", "fmt", "difficulty", "saved", "share",
          "mistakes", "recheck", "subject", "first", "drop", "run", "box",
          "habit", "topics_from", "zone", "budget_ms", "has", "item",
          # S4: the builder's and the upgrades' fields (practice.md §3.2's §2.6 row)
          "show_name", "tier_mix", "review_mix", "review_from", "final_round", "habits",
          "rematch", "clean", "words_mix", "per_q", "example", "segments", "cover",
          "hints", "worked_first", "two_passes"}
TIER_BUDGET = {"math": {"easy": 65_000, "medium": 95_000, "hard": 126_000}}   # P16, R34
ZONES = {"warm": .87, "stretch": .70, "challenge": .47}                        # P11 centres
ZONE_WORD = {"warm": "Warm-up", "stretch": "Stretch", "challenge": "Challenge"}
MUTABLE = ("repair", "end_repairs", "later_repairs", "items", "queue", "trap_queue", "turn",
           "seconds", "clock_log", "more", "review_slots", "final_queue", "slot_plan", "segments",
           "examples_done", "worked_topics", "adaptive_state", "planned_n", "word_cards",
           "slots", "words_done")                            # what a serve changes (P23's preview)
STUDY_AIDS = ("type_note", "ask_span", "slip_note", "check_anyway_ms")


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


# A client's want is a mistake's norm, bare or as '^escaped$'. Only literal text
# is accepted and the regex is rebuilt here, so no client pattern ever runs
# (a nested quantifier would hold the GIL and stall the whole server).
_LITERAL = re.compile(r"\^?((?:\\\W|[^\\.^$*+?{}\[\]()|])+)\$?", re.S)


def want_regex(value) -> str | None:
    m = _LITERAL.fullmatch(value) if isinstance(value, str) and len(value) <= 500 else None
    return "^" + re.escape(re.sub(r"\\(\W)", r"\1", m[1])) + "$" if m else None


def _source_questions(learner: str, sid: str) -> list[dict]:
    row = db.one("SELECT * FROM sessions WHERE id=?", sid)
    if not row or row["learner"] != learner:
        raise HTTPException(404, "no such session")
    if row["kind"] == "diagnostic" and not row["user_id"]:
        raise HTTPException(403, "finish and sign up before fixing this diagnostic")
    if not row["finished"]:
        _empty("finish_that_sitting_first")
    raw = json.loads(row["questions"] or "[]")
    if isinstance(raw, dict):
        raw = [q for v in raw.values() if isinstance(v, list) for q in v]
    return [q for q in raw if isinstance(q, dict) and "key" in q]


def _locked(learner: str, cfg: dict, template: str, seed: int) -> bool:
    """R19: an exact item needs access(); a set code or a permalink is its own
    grant, but never to a live test's item or today's challenge."""
    if cfg.get("granted"):
        return deps._protected(learner, template, seed)
    return deps.access(learner, template, seed) is None


def _miss_tier(learner: str, trap: dict, serve: str, level: str) -> str | None:
    """Review's level for redo and checks: the tier of the trap's latest miss,
    one up for 'harder' when the template has it, None for 'any'."""
    if level == "any":
        return None
    row = db.one("SELECT difficulty FROM attempts WHERE learner=? AND template=? AND correct=0"
                 " ORDER BY (norm=?) DESC, id DESC LIMIT 1", learner, trap["template"], trap["norm"])
    tier = row["difficulty"] if row else None
    if level == "harder" and tier in TIERS[:-1] and TIERS[TIERS.index(tier) + 1] in _tiers_of(serve):
        tier = TIERS[TIERS.index(tier) + 1]
    return tier if tier in _tiers_of(serve) else None


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
            if any(not isinstance(qid, str) for qid in only):
                _invalid("only", "expected question ids")
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
            _empty("nothing to practise")
        return queue, items, why
    if pool == "new":
        return queue, items, why
    if pool in {"redo", "checks"}:
        today = progress._local_today(learner).isoformat()
        traps = progress.open_traps(learner) if pool == "redo" else [dict(r) for r in db.rows(
            "SELECT * FROM traps WHERE learner=? AND closed IS NOT NULL AND due<=? AND checks<3",
            learner, today)]
        if ids is not None:
            allowed = set(str(x) for x in _list(ids, "ids"))
            traps = [t for t in traps if str(t["id"]) in allowed]
        for t in traps:
            # R45 rule 5: a later check-in is served on another template with the same norm
            serve = progress.checkin_template(t) if pool == "checks" else t["template"]
            queue.append(serve)
            cfg.setdefault("trap_queue", []).append({"template": serve, "norm": t["norm"],
                                                     "tier": _miss_tier(learner, t, serve, cfg["level"])})
            why[serve] = "open mistake" if pool == "redo" else "check-in due"
            if t.get("norm") and not str(t["norm"]).startswith("~"):
                cfg["want"].setdefault(serve, "^" + re.escape(t["norm"]) + "$")
        if not queue:
            _empty("no_open_mistakes" if pool == "redo" else "no_checks_due")
    elif pool == "review":
        # P12: T3's fading types (its schedule, no second one), none with an open trap
        fading = progress.warmup_candidates(learner, subject=cfg.get("subject", "math"))["fading"]
        queue = [f["template"] for f in fading]
        for f in fading:
            why[f["template"]] = _review_why({"kind": "due", **f})
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
            _source_questions(learner, body["from_session"])
            if body.get("only") is not None:
                selected_qids = _list(body["only"], "only")
                if any(not isinstance(qid, str) for qid in selected_qids):
                    _invalid("only", "expected question ids")
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
        # F6's hook: serve() re-checks the owner's access, skips removed items
        # and deals each taker their own twins of a fresh set (P22)
        from . import sets
        got = sets.serve(code, learner, True if body.get("exact") is False else None)
        if got["kind"] == "words":
            _invalid("ids", "a word list is not a question set")
        if got["kind"] == "test":
            _invalid("ids", "a shared test starts from Tests")
        cfg["granted"] = True
        cfg["share"] = got["code"]
        items = _pairs([list(x) for x in got["items"]], "ids")
        cfg["exact"] = True             # serve() already chose exact or twin seeds
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
        wanted = list(dict.fromkeys(x.strip().lower() for x in wanted))
        if any(not re.fullmatch(r"[0-9a-f]{8}", x) for x in wanted):
            _invalid("ids", "College Board ids are 8 hex characters")
        known, index = _official_map(), cb_index()
        unknown = [x for x in wanted if x not in known and x not in index]
        if unknown:
            _invalid("ids", f"not in College Board's bank: {unknown[0]}")
        # an R&W id waits for the R&W bank (P15); a Math id outside the exact
        # map resolves through the index to its skill and tier (P13)
        cfg["official_rw"] = [x for x in wanted if x not in known and index[x]["subject"] != "math"]
        cfg["official_ids"] = [x for x in wanted if x not in cfg["official_rw"]]
        if not cfg["official_ids"]:
            _empty("rw_bank_pending")
        for cbid in cfg["official_ids"]:
            t = known[cbid]["template"] if cbid in known else _index_twins(cbid, 1)[0]
            queue.append(t)
            why[t] = f"like official question {cbid}"
    if cfg.get("exact"):
        if queue and not items:
            _invalid("exact", "this pool has no exact question addresses")
        for t, seed in items:
            if _locked(learner, cfg, t, seed):
                raise HTTPException(403, {"reason": "question_not_accessible", "template": t, "seed": seed})
    else:
        queue += [t for t, _ in items]
        items = []
    if not queue and not items:
        _empty("pool_empty")
    return queue, items, why


# ------------------------------------------------------------------ S4: shaping a set

def _prefs_defaults(learner: str, source: str, subject: str) -> dict:
    """U15 / §2.7: the learner's resolved feedback, repairs and builder keys,
    for the sources the mode governs. Other sources keep their own defaults."""
    from . import prefs
    if source not in prefs.MODE_SOURCES and source not in ("map", "builder"):
        return {}
    try:
        p, _where, stage = prefs.resolve(learner)
    except Exception:
        return {}
    per = (p.get("practice") or {}).get(subject) or {}
    out = {k: p[k] for k in ("feedback", "repairs") if k in p}
    out.update({k: per[k] for k in ("zone", "review_mix", "review_from", "final_round", "hints",
                                     "two_passes", "cover", "words_mix") if k in per})
    if source == "builder" and "worked_first" in per:      # P2: the builder's own setting, default on
        out["worked_first"] = per["worked_first"]
    # U15's Test-like mode (chosen, or the stage's test rules): no study aids
    out["test_like"] = p.get("mode") == "test" or bool(
        stage and stage.get("rules") == "test" and p.get("stage_auto", True))
    return out


@functools.lru_cache(maxsize=1)
def _official_map() -> dict[str, dict]:
    """U2's exact map: every College Board ID onto the template its Source
    pins, at the key file's tier and the pinned format."""
    import random
    from satbank.topic import load_topics
    tiers = {}
    root = pathlib.Path(__file__).resolve().parent.parent / "material" / "keys"
    for path in root.glob("*.json"):
        data = json.loads(path.read_text())
        for entry in data.get("items", []):
            if entry.get("cb_id"):
                tiers[(data.get("slug", path.stem), entry["id"])] = (entry["cb_id"], entry.get("tier"))
    out = {}
    for slug, topic in load_topics().items():
        for src in topic.sources:
            got = tiers.get((slug, src.id))
            if not got:
                continue
            try:
                it = src.build(random.Random(0))
            except Exception:
                continue
            out[got[0]] = {"cb_id": got[0], "template": it.template, "tier": got[1] or it.difficulty,
                           "fmt": it.fmt, "topic": slug, "params": it.params,
                           "stem": _flat(it.stem),
                           "norms": {progress.norm(r) for r in it.reasons if r}}
    return out


BAND_MID = {1: 800, 2: 925, 3: 1037, 4: 1112, 5: 1187, 6: 1287, 7: 1400}     # P11's MID per score band
CB_SKILL = {"linear inequalities in one or two variables": "linear_inequalities",
            "nonlinear equations in one variable and systems of equations in two variables":
                "nonlinear_equations_and_systems",
            "systems of two linear equations in two variables": "systems_of_linear_equations"}


@functools.lru_cache(maxsize=1)
def cb_index() -> dict[str, dict]:
    """T-bank's capture of College Board's Question Bank listing (metadata
    only): {cb_id: {subject, domain, skill, tier, band, topic}}, where topic is
    our skill for a Math item (None for R&W)."""
    import difflib
    path = pathlib.Path(__file__).resolve().parent.parent / "material" / "cb" / "cb_index.json"
    try:
        items = json.loads(path.read_text()).get("items") or {}
    except (OSError, ValueError):
        return {}
    names = {t.name.lower().replace("centre", "center"): s for s, t in practice.catalogue()["topics"].items()}
    topic_of_skill: dict[str, str | None] = {}
    out = {}
    for cbid, x in items.items():
        skill = (x.get("skill") or "").strip()
        if skill not in topic_of_skill:
            k = skill.lower()
            topic_of_skill[skill] = None if x.get("subject") != "math" else CB_SKILL.get(k) or names.get(k) or \
                names[max(names, key=lambda n: difflib.SequenceMatcher(None, k, n).ratio())]
        out[cbid.lower()] = {**x, "skill": skill, "topic": topic_of_skill[skill]}
    return out


def _index_twins(cbid: str, each: int) -> list[str]:
    """P13: an index-only Math id's twins -- its skill's templates at its tier,
    closest in item rating to the band's midpoint, one per slot."""
    from . import ratings
    x = cb_index()[cbid]
    names = [t for t in practice.catalogue()["by_topic"].get(x["topic"], ()) if x["tier"] in _tiers_of(t)]
    if not names:
        _empty("no_twin_for_" + cbid)
    mid = BAND_MID.get(x.get("band"), 1100)
    ranked = sorted(names, key=lambda t: (abs(ratings.item(t, x["tier"])[0] - mid), t))
    return [ranked[i % min(len(ranked), max(1, each))] for i in range(each)]


def _flat(stem: str) -> str:
    return re.sub(r"\s+", " ", str(stem).lower()).strip()


@functools.lru_cache(maxsize=1)
def _pinned() -> tuple[set, set]:
    """P13: (template, frozen params) and the normalised stems of every
    official reproduction, so no practice question copies one."""
    params, stems = set(), set()
    for e in _official_map().values():
        params.add((e["template"], _frozen(e["params"])))
        stems.add(e["stem"])
    return params, stems


def _frozen(value):
    if isinstance(value, dict):
        return tuple(sorted((k, _frozen(v)) for k, v in value.items()))
    if isinstance(value, (list, tuple, set)):
        return tuple(_frozen(v) for v in value)
    try:
        hash(value)
        return value
    except TypeError:
        return repr(value)


def pinned(card) -> bool:
    """Does this card reproduce an official College Board question?"""
    params, stems = _pinned()
    it = card.item
    return (card.key, _frozen(getattr(it, "params", None) or {})) in params or _flat(it.stem) in stems


@functools.lru_cache(maxsize=4)
def _has(need: str) -> frozenset:
    if need == "official":
        return frozenset(e["template"] for e in _official_map().values())
    if need == "desmos" and not desmos_on():
        return frozenset()
    names = [t for ts in practice.catalogue()["by_topic"].values() for t in ts]
    out = set()
    for t in names:
        for seed in range(3):
            try:
                it = generate(t, seed)
            except Exception:
                continue
            if (need == "desmos" and getattr(it, "desmos", None)) or (need == "steps" and getattr(it, "steps", None)):
                out.add(t)
                break
    return frozenset(out)


def desmos_on() -> bool:
    """P3 ships dark behind DESMOS_WAY until I1 turns it on."""
    import os
    return os.environ.get("DESMOS_WAY", "") in ("1", "on", "true")


def _first_try_rate(learner: str, topics) -> float | None:
    topics = list(topics)
    if not topics:
        return None
    marks = ",".join("?" for _ in topics)
    r = db.one(f"SELECT COUNT(*) n, COALESCE(SUM(correct),0) r FROM attempts WHERE learner=?"
               f" AND topic IN ({marks}) AND {progress.COUNTED}", learner, *topics)
    return round(r["r"] / r["n"], 3) if r["n"] else None


WHY_KIND = {"open mistake": "mistake", "missed in that sitting": "mistake", "from that sitting": "replay",
            "check-in due": "check", "due for review": "due", "spaced warm-up": "due",
            "not tried": "new_type", "least answered": "least_used", "varied practice": "least_used",
            "repair of the last mistake": "repair"}


def _why_of(value, fallback: str = "least_used") -> dict:
    if isinstance(value, dict):
        return value
    text = str(value or "")
    kind = WHY_KIND.get(text) or ("official" if text.startswith("like official") else fallback)
    return {"kind": kind, "detail": text[:1].upper() + text[1:] if text else None}


def _served_questions(served: list[dict]) -> list[dict]:
    return [q for q in served if q.get("kind", "question") == "question"]


def _shape(learner: str, body: dict, cfg: dict, queue: list, items: list, why: dict):
    """Rematch, Mix-up, habit, Finish this skill, the probe, Learn this type
    and official twins: each turns into slots or a queue here."""
    kinds = blueprint.kinds()
    cat = practice.catalogue()
    source = cfg["source"]
    if body.get("rematch"):                                    # P19
        parent = db.one("SELECT * FROM sessions WHERE id=? AND learner=?", body["rematch"], learner)
        if not parent:
            raise HTTPException(404, "no such session")
        if parent["kind"] == "challenge" or parent["contest"]:
            _empty("a_challenge_has_no_rematch")
        if not parent["finished"]:
            _empty("finish_that_sitting_first")
        pcfg = json.loads(parent["cfg"] or "{}")
        answers = db.load_answers(parent)
        old = [q for q in _served_questions(json.loads(parent["questions"] or "[]")) if "key" in q]
        if body.get("scope", "all") == "misses":
            old = [q for q in old if not scoring.is_correct(q, answers.get(q["id"]))]
        if not old:
            _empty("nothing_to_rematch")
        cfg["slots"] = [{"template": q["key"], "tier": q["difficulty"], "fmt": q["type"],
                         "of": q["id"], "why": {"kind": "rematch",
                                                "detail": f"Rematch of question {int(q['id'][1:])}"}}
                        for q in old[:MAX_FIXED]]
        cfg["rematch_of"] = pcfg.get("rematch_of") or parent["id"]
        cfg["rematch_parent"] = parent["id"]
        for key in ("feedback", "timing", "timed", "seconds", "formats", "tiers"):
            if key not in body and key in pcfg:
                cfg[key] = pcfg[key]
        cfg.update({"repairs": "end", "final_round": False, "zone": "off", "review_mix": "off"})
        cfg["topics"] = list(dict.fromkeys(topic_of(s["template"]) for s in cfg["slots"]))
        cfg["count"] = cfg["total"] = len(cfg["slots"])
        cfg["source"] = "rematch"
    if cfg["pool"] == "official":                            # P13: twins at the official tier
        slots = []
        wanted = cfg.get("official_ids") or []
        for cbid in wanted:
            e = _official_map().get(cbid)
            if not e:                                  # index-only: its skill at its tier, closest by rating
                x = cb_index()[cbid]
                name = practice.catalogue()["topics"][x["topic"]].name
                detail = f"Close twin of College Board question {cbid} ({name}, {x['tier'].capitalize()})"
                ranked = _index_twins(cbid, 30)
                for t in _index_twins(cbid, cfg["each"]):
                    slots.append({"template": t, "tier": x["tier"], "cb_id": cbid, "close": True,
                                  "alts": list(dict.fromkeys(ranked)),
                                  "why": {"kind": "official", "detail": detail}})
                continue
            for _ in range(cfg["each"]):
                slots.append({"template": e["template"], "tier": e["tier"], "fmt": e["fmt"],
                              "cb_id": cbid, "norms": sorted(e["norms"]),
                              "why": {"kind": "official", "detail": f"Twin of College Board question {cbid}"}})
        cfg["slots"] = slots[:MAX_FIXED]
        cfg["official"] = wanted
        cfg["count"] = cfg["total"] = len(cfg["slots"])
        cfg["topics"] = list(dict.fromkeys(topic_of(s["template"]) for s in slots))
        queue = []
    if cfg["order"] == "mixup":                              # P17
        base = list(cfg["templates"])
        if not base and len(cfg["topics"]) == 1:
            base = list(cat["by_topic"].get(cfg["topics"][0], ()))[:6]
        if not 1 <= len(base) <= 6:
            _invalid("order", "Mix-up takes 1–6 types or one skill")
        mix = list(dict.fromkeys(base + [x for t in base for x in blueprint.lookalikes(t)]))
        if len(mix) < 2:
            _empty("no_lookalikes")
        n = cfg["count"] or 8
        salt = zlib.crc32(f"{learner}:{progress.now()}".encode())
        order: list[str] = []
        rounds = 0
        while len(order) < n and rounds < 200:
            rounds += 1
            batch = sorted(mix, key=lambda t: zlib.crc32(f"{salt}:{rounds}:{t}".encode()))
            if order and batch[0] == order[-1]:
                batch.append(batch.pop(0))
            order.extend(batch)
        queue = order[:n]
        why.update((t, {"kind": "mixup", "detail": "Mix-up: choose the method"}) for t in mix)
        cfg["templates"] = []
        cfg["pool_templates"] = mix
        cfg["hide_skill"] = True
        cfg["topics"] = list(dict.fromkeys(topic_of(t) for t in mix))
        if "cover" not in body:
            cfg["cover"] = "all"
        if "feedback" not in body:
            cfg["feedback"] = "instant"
        cfg["count"] = cfg["total"] = n
    if source == "habit" or body.get("habits"):              # P6, U6
        from . import habits
        ids = _list(body.get("habits") or ([body["habit"]] if body.get("habit") else []), "habits", maximum=11)
        known = {f["id"] for f in habits.families(cfg["subject"])}
        if not ids or any(i not in known for i in ids):
            _invalid("habits", "unknown habit family")
        pool_names = cfg["templates"] or [t for topic in (cfg["topics"] or cat["by_topic"])
                                          for t in cat["by_topic"].get(topic, ())]
        regex = "|".join(f"(?:{habits.regex_for(i)})" for i in ids)
        hits = [t for t in pool_names
                if any((habits.family(label) or {}).get("id") in ids for label in kinds.get(t, {}).get("reasons", {}).values())]
        if not hits:
            _empty("no_types_offer_that_habit")
        n = cfg["count"] or 10
        queue = [hits[i % len(hits)] for i in range(n)]
        cfg["want"].update({t: regex for t in hits})     # server-built, never a client pattern
        cfg["habits"] = ids
        why.update((t, {"kind": "habit", "detail": "A habit drill"}) for t in hits)
        cfg["templates"] = []
        cfg["pool_templates"] = hits
        cfg["topics"] = list(dict.fromkeys(topic_of(t) for t in hits))
        cfg["count"] = cfg["total"] = n
    if source == "finish":                                   # P14
        if len(cfg["topics"]) != 1:
            _invalid("topics", "Finish this skill takes one skill")
        topic = cfg["topics"][0]
        names = list(cat["by_topic"].get(topic, ()))
        traps = [t["template"] for t in progress.open_traps(learner, topic)]
        due = [f["template"] for f in progress.warmup_candidates(learner, subject=cfg["subject"])["fading"]
               if f["topic"] == topic]
        firsts: dict[str, list] = {}
        for r in db.rows(f"SELECT template, correct FROM attempts WHERE learner=? AND topic=? AND {progress.COUNTED}"
                         " ORDER BY id", learner, topic):
            firsts.setdefault(r["template"], []).append(r["correct"])
        seg: list[tuple[str, str]] = [(t, "Open mistake") for t in dict.fromkeys(traps)]
        seg += [(t, "Due for review") for t in due if t not in traps]
        for t in names:
            if t in firsts and sum(firsts[t]) < 2 and t not in traps:
                seg += [(t, "Met, not ready yet")] * (2 - sum(firsts[t]))
        seg += [(t, "Not met yet") for t in names if t not in firsts]
        seg = seg[:30]
        if not seg:
            _empty("skill_finished")
        queue = [t for t, _ in seg]
        why.update((t, {"kind": "finish", "detail": d}) for t, d in seg)
        cfg["pool_templates"] = list(dict.fromkeys(queue))
        cfg["count"] = cfg["total"] = len(queue)
        cfg["segments"] = [d for _, d in seg]
    if source == "probe" and cfg["topics"]:                  # P11's Check my level
        cfg["probe"] = {t: "medium" for t in cfg["topics"]}
        if "feedback" not in body:
            cfg["feedback"] = "end"
        cfg.update({"zone": "off", "review_mix": "off", "final_round": False, "adaptive": False})
    if source == "learn" or body.get("example"):              # T4 / P2: a worked example first
        base = cfg["templates"] or queue[:1]
        if base:
            cfg["examples"] = [base[0]]
            cfg["learn"] = source == "learn"
        if source == "learn" and base and not cfg.get("slots"):
            # with help, on your own, then a tier up (P18's sibling for a one-tier type)
            t = base[0]
            have = [x for x in TIERS if x in _tiers_of(t) and x in cfg["tiers"]] or [x for x in TIERS if x in _tiers_of(t)]
            low = have[0]
            up = TIERS[min(2, TIERS.index(low) + 1)]
            third = {"template": t, "tier": up} if up in _tiers_of(t) and up != low else None
            if third is None and up != low:
                sib = [s for s in blueprint.siblings(t, 1) if up in _tiers_of(s)]
                third = {"template": sib[0], "tier": up} if sib else None
            n = cfg["count"] or 3
            words = ["Learn this type: with help"] + ["Learn this type: on your own"] * (n - 1)
            cfg["slots"] = [{"template": t, "tier": low, "why": {"kind": "learn", "detail": w}} for w in words]
            if third and n >= 3:
                cfg["slots"][2].update(third)
                cfg["slots"][2]["why"] = {"kind": "learn", "detail": "Learn this type: on your own, a tier up"}
            cfg["count"] = cfg["total"] = n
            queue = []
    if cfg.get("zone") not in (None, "off") and (cfg.get("rematch_of") or cfg["pool"] not in ("new",)
                                                  or cfg.get("slots") or cfg["order"] == "mixup"):
        cfg["zone"] = "off"                       # zone aims fresh selections only
    return queue, items, why


def _plan(learner: str, cfg: dict, selected: list[str]) -> None:
    """P16 / P11 / P12: the tier each slot plans, the pace clock that sums
    their budgets, and where the review slots go."""
    count = cfg["count"]
    tiers = [t for t in TIERS if t in cfg["tiers"]]
    reachable = {d for t in selected for d, _ in blueprint.abilities().get(t, ())}
    tiers = [t for t in tiers if t in reachable] or tiers
    if cfg.get("slots"):
        cfg["plan"] = [s.get("tier") or ("medium" if "medium" in _tiers_of(s["template"]) else
                                         min(_tiers_of(s["template"]) or {"medium"}, key=TIERS.index))
                       for s in cfg["slots"]]
    elif count is None:
        cfg["plan"] = []
    else:
        mix = blueprint.TIERS.get(cfg.get("tier_mix") if cfg.get("tier_mix") != "any" else "module1")
        weights = {t: mix[t] for t in tiers}
        total = sum(weights.values()) or 1
        quotas = {t: count * weights[t] / total for t in tiers}
        base = {t: int(quotas[t]) for t in tiers}
        for t in sorted(tiers, key=lambda x: (-(quotas[x] - base[x]), TIERS.index(x)))[:count - sum(base.values())]:
            base[t] += 1
        cfg["plan"] = practice.interleave({t: n for t, n in base.items() if n})
        if cfg.get("tier_mix") not in (None, "any"):
            missing = [t for t in blueprint.TIERS[cfg["tier_mix"]] if t not in tiers]
            cfg["mix_missing"] = missing
    budgets = TIER_BUDGET.get(cfg["subject"], TIER_BUDGET["math"])
    if cfg["timing"] == "pace" and count is not None:
        millis = sum(budgets[t] for t in cfg["plan"])
        cfg["seconds"] = ((millis + 59_999) // 60_000) * 60
        cfg["clock_log"] = [{"at": progress.now(), "delta_ms": millis, "why": "plan"}]
    # review slots (P12): positions 3, 6, 9 ... on fresh seeds, from T3's schedule
    mix = cfg.get("review_mix")
    slots: list[dict] = []
    if mix not in (None, "off", 0) and cfg["pool"] == "new" and not cfg.get("slots") \
            and cfg["order"] != "mixup" and cfg["source"] not in ("probe", "finish", "learn", "challenge"):
        due = progress.warmup_candidates(learner, subject=cfg["subject"])
        picked = set(cfg["topics"]) if cfg.get("review_from") == "picked" else None
        cands = [{"template": c.get("serve", c["template"]), "kind": "check", "k": None} for c in due["checks"]]
        cands += [{"template": f["template"], "kind": "due", "k": f["k"], "age": f["age"],
                   "interval": f["interval"]} for f in due["fading"]]
        cands += [{"template": m["template"], "kind": "marked", "flagged": m["flagged"]} for m in due["marked"]]
        cands = [c for c in cands if picked is None or topic_of(c["template"]) in picked]
        cands = list({c["template"]: c for c in reversed(cands)}.values())[::-1]
        if cands:
            if count is None:
                n = len(cands)
            elif mix == 2:
                n = 2
            else:
                n = max(1, round(count * 0.2))
            n = min(n, len(cands), (count // 3) if count else len(cands))
            for i, c in enumerate(cands[:n]):
                slots.append({**c, "at": 3 * (i + 1) if count is not None else 5 * (i + 1)})
    cfg["review_slots"] = slots
    # P12: due SAT words at the set's breaks, served and graded by S9 (decision 2:
    # the EBRW list and transitions); never timed, end mode, tests or the challenge
    cfg["word_cards"] = []
    due_items = deps.part("words", "due_items")
    if cfg.get("words_mix") not in (None, "off") and due_items and not cfg.get("timed") \
            and cfg.get("feedback") != "end" and cfg["source"] not in ("challenge", "probe") \
            and not cfg.get("inline") and cfg["subject"] == "math":
        n = 2 if cfg["words_mix"] == 2 else 20
        try:
            cards = [dict(x) for x in (due_items(learner, n) or [])[:n] if isinstance(x, dict) and x.get("token")]
        except Exception:
            cards = []
        cfg["word_cards"] = cards


def resolve(learner: str, body: dict, out: dict | None = None) -> dict:
    """Validate every drill field, resolve aliases and materialize the pool.
    `out`, when given, receives the selection's types that fit the filters."""
    if not isinstance(body, dict):
        _invalid("body", "expected an object")
    unknown = set(body) - FIELDS
    if unknown:
        _invalid(sorted(unknown)[0], "unknown field")
    if "assignment" in body:
        _invalid("assignment", "classes are not part of this product")
    if "contest" in body:
        _invalid("contest", "contest is set by the server")
    body = dict(body)
    for name, module in (("like", "daily"), ("word", "words"), ("confusion", "words")):
        if name in body:
            resolver = deps.part(module, "resolve_drill")
            if resolver is None:
                raise HTTPException(501, {"reason": f"{module}_resolver_unavailable"})
            body = resolver(learner, body)
    # Up next's time box (U1): next.resolve_drill lays out its first slots (check-ins, open traps, a weak and a warm
    # skill); then the coach's pick runs until the box's clock ends
    if body.get("source") == "next" and body.get("box") is not None:
        resolver = deps.part("next", "resolve_drill")
        if resolver is not None:
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
    if body.get("again"):
        row = db.one("SELECT cfg FROM sessions WHERE id=? AND learner=?", body["again"], learner)
        if not row:
            raise HTTPException(404, "no such session")
        old = json.loads(row["cfg"] or "{}")
        for key in ("topics", "templates", "count", "tiers", "levels", "unmeasured",
                    "formats", "spr_share", "adaptive", "order", "mix", "pool", "source",
                    "timing", "feedback", "repairs", "each"):
            if key not in body and key in old:
                body[key] = old[key]
        body.setdefault("exact", False)
    aliases = {"mistakes": "redo", "fixed": "checks", "templates": "new", "share": "set"}
    if "list" in body and "pool" in body and aliases.get(body["list"], body["list"]) != aliases.get(body["pool"], body["pool"]):
        _invalid("list", "conflicts with pool")
    if body.get("list") == "templates" and body.get("ids") is not None:
        body.setdefault("templates", body["ids"])
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
                     " AND (? IS NULL OR norm=?) ORDER BY last DESC LIMIT 1", learner,
                     trap["template"], progress.norm(trap["reason"]) if trap.get("reason") else None,
                     progress.norm(trap["reason"]) if trap.get("reason") else None)
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
    if body.get("task") is not None and (not isinstance(body["task"], str) or not re.fullmatch(
            r"\d{4}-\d{2}-\d{2}:(fix|recheck|focus|extra|test)", body["task"])):
        _invalid("task", "use YYYY-MM-DD:fix|recheck|focus|extra|test")
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
        _invalid("want", "expected {template: norm}")
    names = {n for v in cat["by_topic"].values() for n in v}
    for t, pattern in list(want.items()):
        want[t] = want_regex(pattern)
        if t not in names or want[t] is None:
            _invalid("want", "unknown template, or not a mistake's norm ('^' + re.escape(norm) + '$')")
    exclude = _pairs(body.get("exclude", []), "exclude")
    # U1's segments: an ordered list of slots, each a type (and its tier and
    # format) on a fresh seed -- the summary's "Fix 2 confident misses + ..."
    segments = []
    for s in _list(body.get("segments") or [], "segments", maximum=30):
        if not isinstance(s, dict) or set(s) - {"template", "tier", "fmt", "why"} \
                or s.get("template") not in names or s.get("tier") not in (None, *TIERS) \
                or s.get("fmt") not in (None, "mcq", "spr") \
                or not isinstance(s.get("why") or "", str) or len(s.get("why") or "") > 80:
            _invalid("segments", "expected [{template, tier?, fmt?, why?}] of catalogue types")
        tier = s.get("tier") if s.get("tier") in _tiers_of(s["template"]) else None
        segments.append({"template": s["template"], "tier": tier, "fmt": s.get("fmt"),
                         "why": {"kind": "segment", "detail": s.get("why") or "From your last set"}})
    for name, options in (("level", {"as_missed", "any", "harder"}),
                          ("result", {"any", "missed", "right", "guessed"}),
                          ("from", {"both", "practice", "tests"}),
                          ("scope", {"misses", "all", "blanks"}),
                          ("order", {"mixed", "grouped", "ramp", "given", "mixup"}),
                          ("mix", {"even", "blueprint"}),
                          ("timing", {"off", "pace", "custom"}),
                          ("feedback", {"instant", "retry", "end"}),
                          ("repairs", {"next", "later", "end", "off"}),
                          ("zone", {"off", *ZONES}),
                          ("tier_mix", {"any", *blueprint.TIERS}),
                          ("review_from", {"picked", "all", "any"}),
                          ("cover", {"off", "hard", "all"})):
        if name in body:
            _choices(body[name], name, options)
    for field in ("final_round", "clean", "show_name", "hints", "worked_first", "two_passes", "example"):
        if field in body and type(body[field]) is not bool:
            _invalid(field, "expected true or false")
    if "review_mix" in body and body["review_mix"] not in ("off", 2, 20, 0):
        _invalid("review_mix", "use off, 2 or 20")
    if "words_mix" in body and body["words_mix"] not in ("off", 2, "all"):
        _invalid("words_mix", "use off, 2 or all")
    if "box" in body and body["box"] is not None and (type(body["box"]) is not int or not 5 <= body["box"] <= 60):
        _invalid("box", "use 5–60 minutes")
    if "per_q" in body and body["per_q"] is not None and (type(body["per_q"]) not in (int, float)
                                                         or not .5 <= body["per_q"] <= 1.5):
        _invalid("per_q", "use 0.5–1.5")
    has = _list(body.get("has", []), "has", maximum=3)
    if any(h not in ("desmos", "official", "steps") for h in has):
        _invalid("has", "choose from desmos, official, steps")
    timing = body.get("timing", "custom" if body.get("timed") and minutes else "legacy_pace" if body.get("timed") else "off")
    if count is None and (body.get("order") == "ramp" or timing == "pace"):
        raise HTTPException(400, {"field": "count", "reason": "an endless set has no end to ramp or pace to"})
    # a shared set serves its identical items (QBank 15)
    # P21: Seen before and Saved give fresh twins by default, Marked means "this one"
    exact_default = pool in {"history", "marked", "set"}
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
           "task": body.get("task"), "run": body.get("run"),
           # a twin counts on its parent (R24, S6's results.twins)
           "parent": body.get("parent") or (body.get("from_session") if source == "twin" else None),
           "from_session": body.get("from_session"), "only": body.get("only"),
           "scope": body.get("scope", "misses"), "still_open": body.get("still_open", False)}
    # U15: a builder-like source runs with the learner's resolved mode and
    # builder prefs for every key its body leaves out (prefs.for_source)
    mine = _prefs_defaults(learner, source, subject)
    for key in ("feedback", "repairs"):
        if key not in body and key in mine:
            cfg[key] = mine[key]
    box = body.get("box")
    cfg.update({
        "zone": body.get("zone", mine.get("zone", "off")), "tier_mix": body.get("tier_mix", "any"),
        "review_mix": body.get("review_mix", mine.get("review_mix", "off")),
        "review_from": body.get("review_from", mine.get("review_from", "picked")),
        "final_round": body.get("final_round", mine.get("final_round", True)),
        "words_mix": body.get("words_mix", mine.get("words_mix", "off")),
        "hints_on": body.get("hints", mine.get("hints", True)),
        "worked_first": body.get("worked_first", mine.get("worked_first", False)),
        "two_passes": body.get("two_passes", mine.get("two_passes", True)),
        "cover": body.get("cover", mine.get("cover", "off")),
        "has": has, "clean": body.get("clean", False), "show_name": body.get("show_name", False),
        "per_q": body.get("per_q"), "target": {}, "box": box, "test_like": bool(mine.get("test_like")),
        "ms": {}, "skipped": [], "strike": {}, "hints": {}, "calc": {}, "retry": {},
        "end_meta": {}, "more": [], "at": None, "paused_at": None, "paused_s": 0,
        "clock_log": []})
    if box:
        cfg.update({"count": None, "total": None, "timed": True, "timing": "custom", "seconds": box * 60})
        count = None
    if source == "sprint":
        cfg.update({"count": None, "total": None, "timed": True, "timing": "custom",
                    "seconds": cfg["seconds"] or 300, "repairs": "off", "final_round": False})
        count = None
    if body.get("item"):
        try:
            t, seed = body["item"].rsplit(":", 1)
            cfg["ids"] = [[t, int(seed)]]
            cfg["exact"] = True
        except (AttributeError, ValueError):
            _invalid("item", "use template:seed")
        if t not in names:
            _invalid("item", "unknown template")
        cfg["granted"] = True           # R19's permalink: any catalogue item, live ones excepted
    if body.get("retake"):
        cfg["ids"] = [[q["key"], q["seed"]] for q in _source_questions(learner, body["retake"])]
        cfg["exact"] = True
    if segments:
        cfg["slots"] = segments
        if not cfg.get("box"):                          # a time box keeps going after its slots, until the clock ends
            cfg["count"] = cfg["total"] = len(segments)
        cfg["topics"] = list(dict.fromkeys(topics + [topic_of(s["template"]) for s in segments]))
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
    queue, items, why = _shape(learner, body, cfg, queue, items, why)
    if cfg["templates"]:
        queue = [t for t in queue if t in cfg["templates"]]
        items = [p for p in items if p[0] in cfg["templates"]]
    if cfg["topics"]:
        queue = [t for t in queue if topic_of(t) in cfg["topics"]]
        items = [p for p in items if topic_of(p[0]) in cfg["topics"]]
    slot_names = [s["template"] for s in cfg.get("slots") or ()]
    if queue or items or slot_names:
        cfg["queue"], cfg["items"] = queue, items
        cfg.setdefault("pool_templates", list(dict.fromkeys(queue + [t for t, _ in items] + slot_names)))
        cfg["why"] = why
        if "count" not in body and pool != "new" and not slot_names:
            cfg["count"] = cfg["total"] = min(MAX_FIXED, (len(queue) + len(items)) * each)
        if pool in {"redo", "checks"}:
            targets = [t for t in cfg.get("trap_queue", ()) if t["template"] in queue]
            if targets and cfg["count"] is not None:
                cfg["trap_queue"] = [targets[i % len(targets)] for i in range(cfg["count"])]
                cfg["queue"] = [t["template"] for t in cfg["trap_queue"]]
    elif pool != "new":
        _empty("filters_removed_all")
    else:
        cfg["queue"], cfg["items"], cfg["why"] = [], [], why
    selected = cfg["templates"] or [t for topic in cfg["topics"] for t in cat["by_topic"].get(topic, ())]
    selected += cfg["queue"] + [t for t, _ in cfg["items"]] + slot_names
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

    def fits(t, formats):
        return any(d in cfg["tiers"] and f in formats and
                   rated.get((t, d), {}).get("level") in cfg["levels"] and
                   (cfg["unmeasured"] or not rated.get((t, d), {}).get("rough", True))
                   for d, f in blueprint.abilities().get(t, ()))
    kept = [t for t in selected if fits(t, cfg["formats"])]
    if not kept:
        if any(fits(t, ("mcq", "spr")) for t in selected):     # the format alone emptied it
            _empty("no_grid-in_questions" if cfg["formats"] == ["spr"] else "no_multiple-choice_questions")
        _empty("level " + ", ".join(map(str, cfg["levels"])) + " unavailable"
               if body.get("levels") else "filters_removed_all")
    for need in cfg["has"]:                       # P3, P13: only types that carry it
        kept = [t for t in kept if t in _has(need)]
        if not kept:
            _empty(f"no_{need}_types")
    if cfg["has"] and cfg["pool"] == "new" and not cfg["templates"]:
        cfg["templates"] = list(dict.fromkeys(kept))
    selected = kept
    if not cfg["topics"]:
        cfg["topics"] = list(dict.fromkeys(topic_of(t) for t in selected))
    cfg["before"] = {t: progress.topic_mastery(learner, t) for t in {topic_of(t) for t in selected}}
    cfg["before_accuracy"] = _first_try_rate(learner, cfg["before"])
    _plan(learner, cfg, selected)
    if out is not None:
        out["kept"] = list(dict.fromkeys(selected))
    return cfg


def preview(learner: str, body: dict) -> dict:
    """The same resolver as create, with no session or seen-item writes."""
    topics = body.get("topics") if isinstance(body, dict) and isinstance(body.get("topics"), list) else None
    try:
        kept: dict = {}
        cfg = resolve(learner, body, kept)
    except HTTPException as e:
        if e.status_code == 409:
            return {"available": False, "servable": False, "count": 0, "templates": 0,
                    "types": 0, "questions": 0, "minutes": None, "reason": e.detail["reason"],
                    "pools": pool_counts(learner, topics)}
        raise
    names = set(kept.get("kept") or ())
    count = cfg["count"]
    budgets = TIER_BUDGET.get(cfg["subject"], TIER_BUDGET["math"])
    if cfg.get("seconds"):
        minutes = round(cfg["seconds"] / 60, 1)
    elif count is None:
        minutes = None
    else:                                   # P16: the plan's own budgets, "≈ 16 min for you"
        plan = cfg.get("plan") or [TIERS[1]] * count
        minutes = round(sum(budgets.get(t, 95_000) for t in plan) / 60_000, 1)
    return {"available": True, "servable": True, "count": count, "templates": len(names),
            "types": len(names), "questions": count if cfg["exact"] else None,
            "minutes": minutes, "plan": cfg.get("plan"), "seconds": cfg.get("seconds"),
            "pools": pool_counts(learner, topics), "exact": len(cfg["items"]), "pool": cfg["pool"],
            "topics": len({topic_of(t) for t in names}), "mix_missing": cfg.get("mix_missing") or [],
            "review_slots": len(cfg.get("review_slots") or ()), "words": len(cfg.get("word_cards") or ()),
            "cfg": {k: cfg.get(k) for k in ("source", "subject", "formats", "tiers", "levels", "timing",
                                            "feedback", "repairs", "zone", "tier_mix", "final_round",
                                            "review_mix", "cover", "order")}}


def pool_counts(learner: str, topics: list | None = None) -> dict:
    """The counts beside each 'Questions from' row, within the chosen skills."""
    cat = practice.catalogue()["by_topic"]
    picked = [t for t in (topics or ()) if isinstance(t, str) and t in cat] or None
    names = [t for topic in (picked or cat) for t in cat.get(topic, ())]
    inside = (lambda topic: topic in picked) if picked else (lambda topic: True)
    traps = [t for t in progress.open_traps(learner) if inside(t["topic"])]
    sure = {r["template"] for r in db.rows(
        "SELECT a.template FROM attempts a WHERE a.learner=? AND a.correct=0 AND a.conf='sure' AND a.id ="
        " (SELECT MAX(b.id) FROM attempts b WHERE b.learner=a.learner AND b.template=a.template AND b.correct=0)",
        learner)}
    due = progress.warmup_candidates(learner)
    tried = {r["template"] for r in db.rows("SELECT DISTINCT template FROM attempts WHERE learner=?", learner)}
    rows = [r for r in db.rows("SELECT template, topic, seed, correct, guess, conf FROM attempts"
                               " WHERE learner=? ORDER BY id", learner) if inside(r["topic"])]
    firsts: dict = {}
    for r in rows:
        firsts.setdefault((r["template"], r["seed"]), r)
    flags = [r for r in db.rows("SELECT template, topic FROM flags WHERE learner=?", learner) if inside(r["topic"])]
    return {"new": len(names), "mistakes": len(traps),
            "checks": sum(1 for c in due["checks"] if inside(c.get("topic"))),
            "review": sum(1 for f in due["fading"] if inside(f["topic"])),
            "untried": sum(1 for t in names if t not in tried),
            "confident": len({t["template"] for t in traps if t["template"] in sure}),
            "outside": sum(1 for t in traps if t.get("source") == "outside"),
            "saved": sum(1 for r in db.rows("SELECT topic FROM saved WHERE learner=?", learner) if inside(r["topic"])),
            "marked": len(flags),
            "seen": {"any": len(firsts), "missed": sum(1 for r in firsts.values() if not r["correct"]),
                     "right": sum(1 for r in firsts.values() if r["correct"]),
                     "guessed": sum(1 for r in firsts.values() if r["guess"] or r["conf"] == "guess"),
                     "sure_wrong": sum(1 for r in firsts.values() if not r["correct"] and r["conf"] == "sure"),
                     "marked": len(flags)}}


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
    rows = db.rows("SELECT template,difficulty,correct,ms,reason,norm,miss_kind FROM attempts WHERE repeat=0"
                   " AND disputed=0 AND void IS NULL AND guess=0 AND hints=0 AND flagged=0"
                   f" AND {db.NOT_SAMPLE}")
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
            # the crowd's most common named mistake: slips and misreads are not
            # misconceptions (P8), and a filler or an unnamed grid-in names nothing
            misses = Counter(r["reason"] for r in sample if not r["correct"] and r["reason"]
                             and progress.norm(r["reason"]) not in progress.UNNAMED
                             and r["miss_kind"] not in ("slip", "misread"))
            rate = round(sum(r["correct"] for r in sample) / n, 3) if n >= 20 else None
            top = misses.most_common(1)[0] if misses else None
            wrong = sum(1 for r in sample if not r["correct"])
            out[(template, tier)] = {
                **rating, "n": n, "rate": rate,
                "median_ms_right": int(statistics.median(right_ms)) if right_ms else None,
                "rough": rating["rough"],
                "crowd": {"n": n, "rate": rate, "top_mistake": top[0] if top else None,
                          "share": round(top[1] / wrong, 3) if top and wrong else None} if n >= 20 else None,
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
    reasons += [x[0] for x in practice.spr_reasons(card.key, card.seed, card.item)]
    return any(pattern.search(r or "") or pattern.search(progress.norm(r or "")) for r in reasons)


def _offers_habit(card: practice.Card, ids) -> bool:
    """P6: does a named trap on offer belong to one of these U6 families?"""
    from . import habits
    return any((habits.family(n) or {}).get("id") in ids
               for n in progress.offered_of(practice.to_question(card, 1)))


def _mcq_form(card: practice.Card) -> practice.Card | None:
    """The same seed's MCQ form, only when it keeps the question's setup."""
    if card.item.fmt != "spr":
        return None
    try:
        item = generate(card.key, card.seed, fmt="mcq")
    except Exception:
        return None
    if item.fmt != "mcq" or item.key != card.item.key or item.params != card.item.params:
        return None
    return practice.Card.of(card.key, card.seed, item, card.topic)


def _fresh(b: practice.Builder, template: str, allowed: set[str] | None,
           cfg: dict | None = None, *, required_norm: str | None = None,
           prefer_mcq: bool = False) -> practice.Card | None:
    """Walk fresh seeds with every active filter; keep want on repairs too."""
    cfg = cfg or {}
    topic = topic_of(template)
    wanted = cfg.get("want", {}).get(template)
    fallback = stepped = False
    survey = levels() if cfg.get("levels") else {}
    formats = cfg.get("formats", ("mcq", "spr"))
    states = cfg.get("adaptive_state") or {}
    # R33's tier, clamped to what this template can serve under these filters
    reachable = [d for d in TIERS if (not allowed or d in allowed) and any(
        t == d and (f in formats or required_norm or prefer_mcq) for t, f in blueprint.abilities().get(template, ()))]
    # A named repair or fix walks further for a served form that offers its norm
    # (F4 only lowers owed then); failing that, the plain seed with trap_true
    # False, as for any want (G3 rule 3), so a set never stops on it.
    for _ in range(600 if required_norm else 60 if wanted else 24):
        card = b.draw(template, topic)
        if card is None:
            break
        if pinned(card) or _removed(card.key, card.seed):
            b.keep(card)                 # P13, U3: never an official copy or a quarantined seed
            continue
        alternate = _mcq_form(card) if required_norm or prefer_mcq else None
        if alternate and practice.question_hash(alternate.item) in b.seen_stems:
            alternate = None
        if required_norm and required_norm not in progress.offered_of(practice.to_question(card, 1)):
            if alternate and required_norm in progress.offered_of(practice.to_question(alternate, 1)):
                card = alternate
            else:
                b.keep(card)
                fallback = True
                continue
        elif prefer_mcq and not progress.offered_of(practice.to_question(card, 1)) and alternate:
            card = alternate
        tier = card.feats["difficulty"]
        measured = survey.get((template, tier), {})
        if allowed and tier not in allowed or (card.item.fmt not in formats
                                                  and not (required_norm or prefer_mcq)) \
                or (cfg.get("levels") and measured.get("level") not in cfg["levels"]) \
                or (cfg.get("unmeasured") is False and measured.get("rough", True)) \
                or [template, card.seed] in cfg.get("exclude", ()):
            b.keep(card)
            continue
        state = states.get(card.item.skill)
        if state and reachable and tier != min(
                reachable, key=lambda d: abs(TIERS.index(d) - TIERS.index(state["tier"]))):
            b.keep(card)
            stepped = True
            continue
        if wanted and not (_offers_habit(card, cfg["habits"]) if cfg.get("habits") else _offers(card, wanted)):
            b.keep(card)
            fallback = True
            continue
        card.trap_true = bool(wanted)
        return card
    if (wanted or required_norm) and fallback:
        # G3 rule 3: nothing offered the trap, so the plain next seed, trap_true false
        plain = {**cfg, "want": {t: v for t, v in cfg.get("want", {}).items() if t != template}}
        card = _fresh(b, template, allowed, plain, prefer_mcq=prefer_mcq)
        if card:
            card.trap_true = False
        return card
    if stepped:                     # the adaptive tier never empties the pool
        return _fresh(b, template, allowed, {**cfg, "adaptive_state": {}},
                      required_norm=required_norm, prefer_mcq=prefer_mcq)
    return None


def _removed(template: str, seed: int) -> bool:
    removed = deps.part("reports", "removed")
    try:
        return bool(removed and removed(template, seed))
    except Exception:
        return False


def _tiers_of(template: str) -> set[str]:
    return {d for d, _ in blueprint.abilities().get(template, ())}


def _more_card(b: practice.Builder, cfg: dict, ask: dict) -> practice.Card | None:
    """One /more request: the same template (or a sibling) at a tier, as a
    grid-in, with another ask, or offering a named trap -- always a fresh seed."""
    template = ask["template"]
    if ask.get("exact") is not None:              # a card chosen earlier, held behind its example
        try:
            card = practice.Card.of(template, ask["exact"], generate(template, ask["exact"]), topic_of(template))
        except Exception:
            return None
        card.trap_true = None
        return card
    walk = {**cfg, "adaptive_state": {}, "levels": None}
    if ask.get("fmt"):
        walk["formats"] = [ask["fmt"]]
    if ask.get("want"):
        walk["want"] = {**cfg.get("want", {}), template: "^" + re.escape(ask["want"]) + "$"}
    if ask.get("ask") is not None and ask.get("seed") is not None:
        try:
            item = generate(template, ask["seed"], ask=ask["ask"])
        except Exception:
            item = None
        if item is not None:
            card = practice.Card.of(template, ask["seed"], item, topic_of(template))
            card.trap_true = None
            return card
        return None
    tiers = {ask["tier"]} if ask.get("tier") else None
    card = _fresh(b, template, tiers, walk, required_norm=ask.get("want"))
    if card is None and tiers:
        card = _fresh(b, template, None, walk, required_norm=ask.get("want"))
    return card


def _slot_card(b: practice.Builder, cfg: dict, slot: dict) -> practice.Card | None:
    """A rematch, official or final-round slot: its template at its tier and
    format on a fresh seed; an official twin prefers one sharing its traps."""
    walk = {**cfg, "adaptive_state": {}, "levels": None, "formats": [slot["fmt"]] if slot.get("fmt") else cfg["formats"]}
    have = _tiers_of(slot["template"])
    if slot.get("tier") and slot["tier"] not in have and have:
        # an official item's tier its template cannot serve: the nearest one it can
        slot = {**slot, "tier": min(have, key=lambda d: (abs(TIERS.index(d) - TIERS.index(slot["tier"])), d))}
    norms = set(slot.get("norms") or ())
    if norms:
        best = None
        for _ in range(40):
            card = _fresh(b, slot["template"], {slot["tier"]} if slot.get("tier") else None, walk)
            if card is None:
                break
            b.stash.pop(card.key, None)          # the walk moves on; the cursor is past it
            shared = len(norms & set(progress.offered_of(practice.to_question(card, 1))))
            if best is None or shared > best[0]:
                best = (shared, card)
            if shared >= 2:
                break
        if best:
            return best[1]
    card = _fresh(b, slot["template"], {slot["tier"]} if slot.get("tier") else None, walk)
    for alt in slot.get("alts") or ():          # an index twin: the skill's next closest type, same tier
        if card is not None:
            break
        if alt != slot["template"]:
            card = _fresh(b, alt, {slot["tier"]}, walk)
    if card is None:
        card = _fresh(b, slot["template"], None, {**walk, "formats": ["mcq", "spr"]})
    return card


def _review_why(slot: dict) -> dict:
    if slot["kind"] == "marked":
        return {"kind": "marked", "detail": f"You marked this type {_day_word(slot.get('flagged'))}"}
    if slot["kind"] == "check":
        return {"kind": "check", "detail": "Check-in: a fixed mistake, tested after a gap"}
    k = slot.get("k") or 1
    held = f", held {k - 1} time{'s' if k - 1 != 1 else ''}" if k > 1 else ""
    back = progress.interval_for(k + 1)
    return {"kind": "due", "detail": f"Warm-up: right {slot.get('age', 0)} days ago{held}"
                                     f" · back in {back} days if right"}


def _day_word(at: str | None) -> str:
    try:
        return dt.datetime.fromisoformat(at).strftime("%b %-d")
    except Exception:
        return "earlier"


def _aim(row, cfg: dict, served: list[dict], topic: str, pool: list[str], allowed: set,
         used: Counter, fmt: str | None = None) -> dict | None:
    """The tier (and, for a placed skill in For me, the exact type) this slot
    aims at: the probe's staircase, tier_mix's plan, For me's zone by odds,
    and before placement the test's own 7 / 8 / 7 mix."""
    from . import ratings
    slot = len(_served_questions(served))
    plan = cfg.get("plan") or []
    planned = plan[slot] if slot < len(plan) else None
    if cfg.get("probe") and topic in cfg["probe"]:
        return {"tier": cfg["probe"][topic], "why": {"kind": "probe", "detail": "Checking your level"}}
    if cfg.get("tier_mix") not in (None, "any"):
        return {"tier": planned, "why": {"kind": "mix", "detail": "The tier mix of a real module"}} if planned else None
    zone = cfg.get("zone")
    if zone in (None, "off") or row["kind"] == "challenge":
        return None
    learner = row["learner"]
    if not ratings.placed(learner, topic):
        left = max(0, ratings.PLACED - ratings.skill(learner, topic)["n"])
        return {"tier": planned, "why": {"kind": "zone", "detail": f"For me starts after 8 answers here · {left} to go"},
                "cold": True} if planned else None
    centre = ZONES[zone]
    skill = ratings.skill(learner, topic)["rating"]
    rated = {(r["template"], r["tier"]): r["rating"] for r in db.rows(
        "SELECT template,tier,rating FROM item_ratings WHERE template IN (" + ",".join("?" for _ in pool) + ")", *pool)} \
        if pool else {}
    best = None
    for t in pool:
        for tier in _tiers_of(t) & allowed:
            if fmt and (tier, fmt) not in blueprint.abilities().get(t, ()):
                continue                  # a format tilt (spr_share) narrows the zone's pairs
            p = ratings.expected(rated.get((t, tier), ratings.TIER_PRIOR[tier]), skill)
            score = abs(p - centre) + 0.05 * used.get(t, 0)
            if best is None or score < best[0]:
                best = (score, t, tier, p)
    if not best:
        return None
    return {"template": best[1], "tier": best[2],
            "why": {"kind": "zone", "detail": f"{ZONE_WORD[zone]}: about {round(best[3] * 100)}% likely for you"}}


def _pick(row, cfg: dict, served: list[dict], b: practice.Builder):
    """The next card, and whether it is a repair."""
    allowed = set(cfg.get("difficulty") or TIERS)
    learner = row["learner"]
    cfg["_why"] = None

    # what the student asked for with /more (any axis, Practise this trap,
    # the ladder, Twins of these), in the order asked
    while cfg.get("more"):
        ask = cfg["more"].pop(0)
        card = _more_card(b, cfg, ask)
        if card:
            cfg["_why"] = ask.get("why")
            cfg["_more"] = ask
            return card, False

    # a repair deferred three questions (repairs 'later')
    later = cfg.get("later_repairs") or []
    ready = [r for r in later if r["at"] <= len(_served_questions(served))]
    if ready and "repair" not in cfg:
        cfg["repair"] = ready[0]["repair"]
        later.remove(ready[0])

    # the same trap with new numbers, before anything else is asked -- even the
    # next saved question -- and a difficulty filter never blocks it
    rep = cfg.pop("repair", None)
    if rep is None and cfg.get("end_repairs") and cfg.get("count") is not None \
            and len(served) >= cfg["count"]:
        rep = cfg["end_repairs"].pop(0)
    if rep:
        rep_key = rep["template"] if isinstance(rep, dict) else rep
        norm = rep.get("norm") if isinstance(rep, dict) else None
        want = rep.get("want") if isinstance(rep, dict) else None
        target_want = {t: v for t, v in cfg.get("want", {}).items() if t != rep_key}
        if want:
            target_want[rep_key] = want
        target = {**cfg, "want": target_want, "adaptive_state": {}}
        card = _fresh(b, rep_key, None, target, required_norm=norm,
                      prefer_mcq=not norm)
        if card:
            return card, True

    # slots in order: a rematch's, official twins, the final round (each a
    # template at a tier and format, on a fresh seed)
    for key in ("final_queue", "slots"):
        while cfg.get(key):
            slot = cfg[key].pop(0)
            card = _slot_card(b, cfg, slot)
            if card:
                cfg["_why"] = slot.get("why")
                cfg["_slot"] = slot
                return card, False

    # a review slot at its position (P12)
    position = len(_served_questions(served)) + 1
    slots = cfg.get("review_slots") or []
    due_now = next((s for s in slots if s["at"] <= position), None)
    if due_now:
        slots.remove(due_now)
        card = _fresh(b, due_now["template"], None, {**cfg, "adaptive_state": {}, "levels": None})
        if card:
            cfg["_why"] = _review_why(due_now)
            return card, False

    # a saved question, served again exactly
    while cfg.get("items"):
        template, seed = cfg["items"].pop(0)
        try:
            if cfg.get("exact") and row["kind"] != "challenge" and _locked(learner, cfg, template, seed):
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
        target = cfg.get("trap_queue", []).pop(0) if cfg.get("trap_queue") else None
        norm = target["norm"] if target and progress.named(target["norm"]) else None
        # a trap target asks for its own norm; otherwise the template keeps its
        # want (a habit drill's families, a sitting's missed trap)
        target_want = {t: v for t, v in cfg.get("want", {}).items() if t != template or not target}
        if norm:
            target_want[template] = "^" + re.escape(norm) + "$"
        target_cfg = {**cfg, "want": target_want}
        if target:
            target_cfg["adaptive_state"] = {}
        card = None
        if target and target.get("tier") in allowed:
            card = _fresh(b, template, {target["tier"]}, target_cfg, required_norm=norm,
                          prefer_mcq=not norm)
            if card and norm and not card.trap_true:
                card = None             # the named trap at any tier beats its tier
        card = card or _fresh(b, template, allowed, target_cfg, required_norm=norm,
                              prefer_mcq=bool(target and not norm))
        if card is not None and cfg.get("habits") and not card.trap_true:
            # P6: a habit drill's question always offers one of its families;
            # this template's walk found none, so another that has them
            for alt in sorted(cfg.get("pool_templates") or (), key=lambda t: zlib.crc32(f"{row['id']}:{t}".encode())):
                other = _fresh(b, alt, allowed, target_cfg) if alt != template else None
                if other is not None and other.trap_true:
                    card = other
                    break
        if card:
            return card, cfg.get("pool") in ("redo", "checks")

    # An endless mistakes set keeps working on its open traps after the
    # initial queue; each named question still has to offer its target.
    if cfg.get("pool") == "redo" and cfg.get("count") is None:
        for trap in progress.open_traps(learner):
            norm = trap["norm"] if progress.named(trap["norm"]) else None
            target_want = {t: v for t, v in cfg.get("want", {}).items() if t != trap["template"]}
            if norm:
                target_want[trap["template"]] = "^" + re.escape(norm) + "$"
            card = _fresh(b, trap["template"], allowed, {**cfg, "want": target_want, "adaptive_state": {}},
                          required_norm=norm, prefer_mcq=not norm)
            if card:
                return card, False

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

    base_allowed = allowed
    turn = cfg.get("turn", 0)
    ring = [topics[(turn + i) % len(topics)] for i in range(len(topics))]
    asked = _served_questions(served)
    if cfg.get("order") == "grouped" and cfg.get("count") and topics:
        block = topics[min(len(topics) - 1, len(asked) * len(topics) // cfg["count"])]
        ring = [block] + [t for t in topics if t != block]
    elif cfg.get("mix") == "blueprint" and len(topics) > 1:
        # the topic furthest below its share: domain weight over the domain's picked skills
        names = progress.topics()
        per_domain = Counter(names[t].domain for t in topics if t in names)
        share = {t: progress.BLUEPRINT.get(names[t].domain, .15) / per_domain[names[t].domain]
                 for t in topics if t in names}
        total_share = sum(share.values()) or 1
        have = Counter(q["topic"] for q in asked)
        ring = sorted(topics, key=lambda t: (have[t] - (len(asked) + 1) * share.get(t, 0) / total_share,
                                             ring.index(t)))
    for topic in ring:
        allowed = base_allowed
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
        states = cfg.get("adaptive_state") or {}
        if states:          # R33: a skill stepped past a template's tiers moves to one that has it
            kinds = blueprint.kinds()
            pool = [t for t in pool if kinds[t]["skill"] not in states
                    or states[kinds[t]["skill"]]["tier"] in _tiers_of(t)] or pool

        # an open mistake in this topic is asked before anything new
        # (offering its trap when a seed in the chosen formats does, so a clean
        # right pays it down)
        for trap in progress.open_traps(learner, topic):
            if trap["template"] in pool and trap["template"] not in last_keys:
                walk = cfg
                if progress.named(trap["norm"]) and trap["template"] not in cfg.get("want", {}):
                    walk = {**cfg, "want": {**cfg.get("want", {}),
                                            trap["template"]: "^" + re.escape(trap["norm"]) + "$"}}
                card = _fresh(b, trap["template"], allowed, walk)
                if card:
                    return card, False

        # P11: For me aims a placed skill at its zone by odds; an unplaced one
        # (and tier_mix, and the probe's staircase) serves the slot's planned tier
        wanted_share = cfg.get("spr_share")
        spr_count = sum(q.get("type") == "spr" for q in served)
        target_spr = wanted_share is not None and spr_count < round((len(served) + 1) * wanted_share)
        tilt = ("spr" if target_spr else "mcq") if wanted_share is not None and len(cfg.get("formats", ())) == 2 \
            else None
        aim = _aim(row, cfg, served, topic, pool, allowed, used, tilt)
        if aim and aim.get("template"):
            card = _fresh(b, aim["template"], {aim["tier"]}, {**cfg, "formats": [tilt]} if tilt else cfg)
            if card:
                cfg["_why"] = aim.get("why")
                return card, False
        wide = pool
        if aim and aim.get("tier") and any(aim["tier"] in _tiers_of(t) for t in pool):
            allowed = {aim["tier"]}
            pool = [t for t in pool if aim["tier"] in _tiers_of(t)]
            cfg["_why"] = aim.get("why")

        # otherwise the least used templates, tie-broken per session so two
        # sessions do not open on the same one
        salt = row["id"]

        def rank(names):
            return sorted(names, key=lambda t: (used[t], zlib.crc32(f"{salt}:{t}".encode())))
        # spr_share picks the slot's format first, so the candidates carry it; a
        # format tilt outranks the planned tier (a tier with no grid-in widens)
        walks = [(cfg, allowed, pool)]
        if tilt:
            forced = {**cfg, "formats": [tilt]}
            walks[:0] = [(forced, allowed, pool), (forced, base_allowed, wide)]
        cards = []
        for walk, allowed, names in walks:
            for template in rank(names):
                card = _fresh(b, template, allowed, walk)
                if card:
                    cards.append(card)
                if len(cards) >= practice.CANDIDATES:
                    break
            if cards:
                break
        if cards:
            return min(cards, key=lambda c: practice.penalty(c, recent, dict(used)) +
                       3 * len(blueprint.kinds()[c.key]["reasons"]) +
                       (400 if wanted_share is not None and (c.item.fmt == "spr") != target_spr else 0)), False
    return None, False


def type_name(template: str) -> str:
    """The slug after the dot, humanised (QBank's type name)."""
    slug = template.split(".", 1)[-1].replace(".", " ").replace("_", " ").strip()
    return slug[:1].upper() + slug[1:]


def _about(template: str) -> str | None:
    about = (blueprint.kinds().get(template) or {}).get("about") or ""
    first = re.split(r"(?<=[.!?])\s", about.strip(), maxsplit=1)[0] if about else ""
    return first or None


def _rungs(q: dict) -> list[str]:
    """P2: the hint rungs this item really has, in order."""
    out = []
    if q.get("type") == "mcq" and any(r and not f for r, f in zip(q.get("reasons") or (), q.get("filler") or [False] * 4)):
        out.append("strike")
    if q.get("steps"):
        out.append("step")
    out.append("example")
    return out


def _example(template: str, n: int) -> dict | None:
    """A reserved-seed worked example (900000 and up): shown with its key,
    never filed, never a slot (P2, T4)."""
    start = 900_000 + zlib.crc32(template.encode()) % 10_000
    for seed in range(start, start + 60):
        try:
            item = generate(template, seed)
        except Exception:
            continue
        q = practice.to_question(practice.Card.of(template, seed, item, topic_of(template)), n)
        q.update({"id": f"d{n:03d}", "kind": "example", "served": progress.now(),
                  "why": {"kind": "example", "detail": "A worked example: study it, then try one"},
                  "type_name": type_name(template), "about": _about(template)})
        return q
    return None


def _example_due(row, cfg: dict, served: list[dict]) -> dict | None:
    wanted = [t for t in cfg.get("examples") or () if t not in (cfg.get("examples_done") or [])]
    if not wanted or row["kind"] == "challenge":
        return None
    cfg.setdefault("examples_done", []).append(wanted[0])
    return _example(wanted[0], len(served) + 1)


def _word_due(row, cfg: dict, served: list[dict], at_end: bool = False) -> dict | None:
    """P12: a due SAT word card after questions 5, 10, 15 ... (one a break),
    and the rest after the last slot. Not a slot: never filed, counted or timed."""
    cards = cfg.get("word_cards") or []
    if not cards or _challenge(row):
        return None
    if not at_end:
        shown = sum(1 for x in served if x.get("kind") == "word")
        if (served and served[-1].get("kind") == "word") or len(_served_questions(served)) < 5 * (shown + 1):
            return None
    card = cards.pop(0)
    return {**card, "id": f"d{len(served) + 1:03d}", "kind": "word", "served": progress.now(),
            "why": {"kind": "word", "detail": "A due SAT word, reviewed between questions"}}


def _make(row, cfg: dict, served: list[dict]) -> tuple[dict | None, object]:
    """The next question, made but not committed: (q, card)."""
    wc = _word_due(row, cfg, served)
    if wc:
        return wc, None
    ex = _example_due(row, cfg, served)
    if ex:
        return ex, None
    b = _builder(row["learner"], dedupe="question" if cfg.get("whole_question", True) else "stem")
    card, repair = _pick(row, cfg, served, b)
    if card is None:
        return None, None
    learner = row["learner"]
    # P2's worked_first: a type this learner has never answered opens with its
    # example, at most once a skill a set; never timed, in end mode or the challenge
    if cfg.get("worked_first") and not cfg.get("timed") and cfg.get("feedback") != "end" \
            and row["kind"] != "challenge" and not repair \
            and card.topic not in (cfg.get("worked_topics") or []) \
            and not db.one("SELECT 1 FROM attempts WHERE learner=? AND template=?", learner, card.key):
        cfg.setdefault("worked_topics", []).append(card.topic)
        cfg.setdefault("more", []).insert(0, {"template": card.key, "exact": card.seed,
                                             "why": cfg.get("_why")})
        ex = _example(card.key, len(served) + 1)
        if ex:
            return ex, None
    n = len(served) + 1
    q = practice.to_question(card, n)
    q["id"] = f"d{n:03d}"
    q["kind"] = "question"
    q["n"] = len(_served_questions(served)) + 1
    q["served"] = progress.now()
    q["feats"] = card.feats
    q["repair"] = repair
    q["trap_true"] = getattr(card, "trap_true", None)
    open_here = any(t["template"] == card.key for t in progress.open_traps(learner, card.topic))
    if repair:
        q["why"] = {"kind": "repair", "detail": "The same trap with new numbers, right after the miss"}
    elif cfg.get("_why"):
        q["why"] = _why_of(cfg["_why"])
    else:
        q["why"] = _why_of(cfg.get("why", {}).get(card.key, "open mistake" if open_here else "varied practice"))
    if open_here and q["why"]["kind"] in ("mistake", "least_used"):
        trap = next(t for t in progress.open_traps(learner, card.topic) if t["template"] == card.key)
        sure = db.one("SELECT at FROM attempts WHERE learner=? AND template=? AND correct=0 AND conf='sure'"
                      " ORDER BY id DESC LIMIT 1", learner, card.key)
        q["why"] = {"kind": "mistake", "detail": (f"You were sure of this one and missed it ({_day_word(sure['at'])})"
                                                  if sure else f"Open mistake · {trap['owed']} clean answer"
                                                  f"{'s close' if trap['owed'] != 1 else ' closes'} it")}
    slot = cfg.pop("_slot", None)
    if slot:
        if slot.get("of"):
            q["slot_of"] = slot["of"]
        if slot.get("cb_id"):
            q["cb_id"] = slot["cb_id"]
        if slot.get("final"):
            q["final"] = True
    ask = cfg.pop("_more", None)
    if ask and ask.get("axis"):
        q["twin"] = {"axis": ask["axis"], "of": ask.get("of")}
    cfg.pop("_why", None)
    q["seen"] = db.one("SELECT COUNT(*) n FROM attempts WHERE learner=? AND template=?", learner, card.key)["n"]
    from . import ratings
    lv = ratings.level(card.key, q["difficulty"])
    q["level"], q["rough"] = lv["level"], lv["rough"]
    q["budget_ms"] = budget_ms(card.key, q["difficulty"])
    q["odds"] = round(ratings.odds(learner, card.key, q["difficulty"], card.topic), 3)
    if cfg.get("zone") not in (None, "off") and not repair:
        q["zone"] = ZONE_WORD[cfg["zone"]] if ratings.placed(learner, card.topic) else "For me starts after 8 answers here"
    q["type_name"] = type_name(card.key)
    q["about"] = _about(card.key)
    q["rungs"] = _rungs(q)
    if cfg.get("per_q"):
        factor = (cfg.get("target") or {}).get(card.key, 1.0)
        q["target_ms"] = round(q["budget_ms"] * cfg["per_q"] * factor)
    if cfg.get("timing") == "pace":
        # P16: a planned slot swaps its plan tier's budget for its own; every
        # added slot (a repair, the final round, /more) adds its whole budget,
        # and P25's replacement takes over the voided question's
        budgets = TIER_BUDGET.get(cfg.get("subject", "math"), TIER_BUDGET["math"])
        replaced = next((x for x in served if ask and x["id"] == ask.get("replaces")), None)
        if replaced:
            prior, why = replaced.get("budget_ms") or 0, "replacement"
        elif repair or q.get("final") or ask:
            prior, why = 0, "repair" if repair else "final" if q.get("final") else "more"
        else:
            i, planned = cfg.get("planned_n", 0), cfg.get("plan") or []
            prior = budgets.get(planned[i], 0) if i < len(planned) else 0
            cfg["planned_n"] = i + 1
            why = "question budget" if prior else "added"
        delta = q["budget_ms"] - prior
        if delta:
            cfg["seconds"] = (cfg.get("seconds") or 0) + (delta + 999) // 1000
            cfg.setdefault("clock_log", []).append({"at": progress.now(), "delta_ms": delta, "why": why,
                                                     "qid": q["id"]})
    return q, card


def _commit(row, served: list[dict], q: dict) -> None:
    """A question is served once the student is shown it (P23)."""
    q["served"] = progress.now()
    served.append(q)
    if q.get("kind", "question") == "question":
        db.remember(row["learner"], [{"key": q["key"], "seed": q["seed"],
                                      "stem_hash": _hash_of(q)}], q["served"])


def _hash_of(q: dict) -> str:
    data = (q["stem"], list(q["choices"]), q.get("figure"), q.get("table"))
    return hashlib.sha1(json.dumps(data, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:16]


def _serve(row, cfg: dict, served: list[dict]) -> dict | None:
    q, _card = _make(row, cfg, served)
    if q is None:
        return None
    _commit(row, served, q)
    return q


def preview_next(row, cfg: dict, served: list[dict]) -> dict | None:
    """P23: the next question with the verdict, held in cfg.pending outside
    served, total and practice_seen until it is shown."""
    trial = json.loads(json.dumps({k: cfg[k] for k in MUTABLE if k in cfg}))
    work = {**cfg, **json.loads(json.dumps(trial))}
    q, _card = _make(row, work, served)
    if q is None:
        cfg.pop("pending", None)
        return None
    cfg["pending"] = {"q": q, "cfg": {k: work[k] for k in MUTABLE if k in work},
                      "gone": [k for k in MUTABLE if k in cfg and k not in work]}
    return q


def commit_pending(row, cfg: dict, served: list[dict], qid: str | None = None) -> dict | None:
    """Commit the held preview (when qid names it, or at the frontier)."""
    pending = cfg.get("pending")
    if not pending or (qid is not None and pending["q"]["id"] != qid):
        return None
    cfg.pop("pending")
    if pending["q"]["id"] in {x["id"] for x in served}:
        return None
    cfg.update(pending["cfg"])
    for k in pending.get("gone", ()):
        cfg.pop(k, None)
    _commit(row, served, pending["q"])
    return pending["q"]


# ------------------------------------------------------------------ the session

class Paused(Exception):
    """A paused set takes no answer, next or more until it resumes."""


def _ready(learner: str, templates) -> set[str]:
    """U8's ready: answered right on the first try at least twice (R8 counting)."""
    names = list(dict.fromkeys(templates))
    if not names:
        return set()
    marks = ",".join("?" for _ in names)
    return {r["template"] for r in db.rows(
        f"SELECT template FROM attempts WHERE learner=? AND template IN ({marks}) AND correct=1 AND {progress.COUNTED}"
        " GROUP BY template HAVING COUNT(*) >= 2", learner, *names)}


def _baseline(learner: str, cfg: dict) -> None:
    """What the summary compares against (P9, P10, P14): each skill's first-try
    rate and points on the table, and the types ready, before the set."""
    from . import estimate
    cfg["before_rate"] = {t: _first_try_rate(learner, [t]) for t in cfg.get("before") or ()}
    try:
        g = estimate.gains(learner, cfg.get("subject", "math"))
    except Exception:
        g = None
    cfg["gain_before"] = {x["topic"]: x["gain"] for x in g["skills"]} if g else None
    cfg["gain_total_before"] = g.get("total") if g else None
    names = [t for topic in cfg.get("topics") or () for t in practice.catalogue()["by_topic"].get(topic, ())]
    cfg["ready_before"] = sorted(_ready(learner, names))


def create(learner: str, sid: str | dict, topics: list[str] | None = None,
           count: int | None = None, difficulty: list[str] | None = None,
           timed: bool = False, source: str = "map",
           queue: list[str] | None = None, items: list[list] | None = None,
           kind: str = "drill", fixed: bool = False, day: str | None = None,
           minutes: int | None = None) -> str | None:
    """A fixed set (the challenge) is the same for everyone, so it has no
    repairs and never grows; the answer is still shown after each question."""
    if isinstance(sid, dict):
        body = sid
        cfg = resolve(learner, body)
        _baseline(learner, cfg)
        new_sid = secrets.token_urlsafe(16)
        db.run("INSERT INTO sessions (id,kind,learner,started,cfg,questions,subject)"
               " VALUES (?,?,?,?,?,'[]',?)", new_sid, "drill", learner, progress.now(),
               json.dumps(cfg), cfg["subject"])
        # the first question is served here, so a set that cannot serve one
        # leaves no empty sitting behind (§2.6)
        try:
            first = next_question(db.one("SELECT * FROM sessions WHERE id=?", new_sid))
        except BaseException:
            db.run("DELETE FROM sessions WHERE id=?", new_sid)
            raise
        if not first.get("question"):
            db.run("DELETE FROM sessions WHERE id=?", new_sid)
            _empty("pool_empty")
        if cfg.get("share"):                      # F6's hook: the taker counts on the set
            from . import sets
            sets.link(new_sid, cfg["share"], bool(body.get("show_name")))
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
        return cfg["count"] * (blueprint.MODULE_SECONDS // blueprint.MODULE_SIZE)   # R34: 95 s each
    return None


def _at(text: str) -> dt.datetime:
    return dt.datetime.fromisoformat(text)


def _now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def paused_s(cfg: dict) -> float:
    total = float(cfg.get("paused_s") or 0)
    if cfg.get("paused_at"):
        total += max(0.0, (_now() - _at(cfg["paused_at"])).total_seconds())
    return total


def elapsed_s(row, cfg: dict) -> int:
    """Time on the set, pauses taken out, computed on the server."""
    end = _at(row["finished"]) if row["finished"] else _now()
    return max(0, round((end - _at(row["started"])).total_seconds() - paused_s(cfg)))


def seconds_left(row, cfg: dict) -> int | None:
    if row["contest"]:
        clock = deps.part("compete", "clock")
        if clock:
            try:
                return clock(row)["left"]
            except Exception:
                pass
    secs = seconds_of(cfg)
    if not secs:
        return None
    return max(0, secs - elapsed_s(row, cfg))


def overtime(row, cfg: dict) -> bool:
    secs = seconds_of(cfg)
    if not secs:
        return False
    end = _at(row["finished"]) if row["finished"] else _now()
    return (end - _at(row["started"])).total_seconds() - paused_s(cfg) > secs + GRACE


def lazy_finish(row):
    """A timed set past its clock plus GRACE is finished when read, so its
    end-mode answers are filed even if the tab was closed."""
    if row["finished"] or row["kind"] not in ("drill", "challenge"):
        return row
    if overtime(row, _cfg(row)):
        finish(row)
        row = db.one("SELECT * FROM sessions WHERE id=?", row["id"])
    return row


def _challenge(row) -> bool:
    return row["kind"] == "challenge" or bool(row["contest"])


def _day_passed(row) -> bool:
    """R19 / §2.13: a challenge's IDs show once its day is over for the learner."""
    day = row["day"] or (row["started"] or "")[:10]
    try:
        return progress._local_today(row["learner"]).isoformat() > day
    except Exception:
        return False


def _voided(row, served: list[dict]) -> set[str]:
    out = {r["qid"] for r in db.rows("SELECT qid FROM attempts WHERE session=? AND void IS NOT NULL", row["id"])}
    out |= set((_cfg(row).get("voided") or {}))
    for q in _served_questions(served):
        if "key" in q and _removed(q["key"], q["seed"]):
            out.add(q["id"])
    return out


def status_of(q: dict, answers: dict, cfg: dict, finished: bool, voided: set) -> str:
    qid = q["id"]
    if qid in voided:
        return "voided"
    given = answers.get(qid)
    if given == "_skip":
        return "skipped"
    if given in (None, ""):
        return "skipped" if qid in (cfg.get("skipped") or []) else "unanswered"
    if cfg.get("feedback") == "end" and not finished:
        return "answered"
    retry = (cfg.get("retry") or {}).get(qid)
    if retry and not retry.get("final") and not finished:
        return "unanswered"
    if scoring.is_correct(q, given):
        return "correct"
    return "mixed" if retry and retry.get("right") else "incorrect"


def revealable(row, cfg: dict, qid: str) -> bool:
    """§2 shared rule: instant mode, retry once final, any mode once finished."""
    if row["finished"]:
        return True
    fb = cfg.get("feedback", "instant")
    if fb == "end" or (row["contest"] and fb == "end"):
        return False
    if fb == "retry":
        r = (cfg.get("retry") or {}).get(qid)
        return bool(r and r.get("final")) or (qid in db.load_answers(row) and not r)
    return qid in db.load_answers(row)


def _aids_allowed(row, cfg: dict) -> bool:
    """Study aids: instant or retry practice only; never end mode before
    Finish, tests, the challenge, contests or Test-like mode."""
    if _challenge(row) or cfg.get("test_like"):
        return False
    return row["finished"] is not None or cfg.get("feedback", "instant") in ("instant", "retry")


def _aids(row, cfg: dict, q: dict) -> dict:
    if q.get("kind", "question") != "question" or not _aids_allowed(row, cfg):
        return {}
    from . import prefs
    learner = row["learner"]
    out = {}
    try:
        rules_on = prefs.get(learner).get("type_rules", True)
    except Exception:
        rules_on = True
    if rules_on:
        rule = db.one("SELECT note, at FROM notes WHERE learner=? AND template=? AND seed=-1", learner, q["key"])
        if rule and cfg.get("clean") and not row["finished"] and rule["at"] <= row["started"]:
            rule = None                  # P19: a Start clean copy hides rules from before
        if rule and rule["note"]:
            out["type_note"] = rule["note"]
            out["type_note_at"] = rule["at"]
    misses = db.rows("SELECT miss_kind, template FROM attempts WHERE learner=? AND topic=? AND correct=0"
                     " ORDER BY id DESC LIMIT 20", learner, q["topic"])
    if sum(1 for m in misses if m["miss_kind"] == "misread") >= 2:
        span = _ask_span(q.get("stem") or "")
        if span:
            out["ask_span"] = span
    last = db.one("SELECT miss_kind, id FROM attempts WHERE learner=? AND template=? AND correct=0"
                  " ORDER BY id DESC LIMIT 1", learner, q["key"])
    if last and last["miss_kind"] == "slip":
        later = db.one("SELECT COUNT(*) n FROM attempts WHERE learner=? AND template=? AND id>?",
                       learner, q["key"], last["id"])["n"]
        if later < 5:
            out["slip_note"] = "Last time: a slip. Re-check the last step."
            if q.get("difficulty") == "easy":
                out["check_anyway_ms"] = (q.get("budget_ms") or 65_000) // 2
    return out


def _ask_span(stem: str) -> list[int] | None:
    """P8: the question sentence -- the last one ending in '?', else the last."""
    text = stem.rstrip()
    ends = [m.end() for m in re.finditer(r"[.?!](?=\s|$)", text)]
    if not ends:
        return [0, len(text)] if text else None
    qs = [e for e in ends if text[e - 1] == "?"]
    end = qs[-1] if qs else ends[-1]
    start = max([e for e in ends if e < end] or [0])
    while start < end and text[start].isspace():
        start += 1
    return [start, end]


def _flags(row) -> set[str]:
    return {r["qid"] for r in db.rows("SELECT qid FROM flags WHERE learner=? AND session=?",
                                      row["learner"], row["id"])}


def _notes(row, cfg: dict, served: list[dict]) -> dict:
    """{(template, seed): (note, marks)} for the served questions; hidden on a
    Start clean copy until it is finished (P19)."""
    sql = "SELECT template, seed, note, marks FROM notes WHERE learner=? AND seed>=0"
    if cfg.get("clean") and not row["finished"]:
        # what the student adds on this copy shows; what came from before waits
        rows = db.rows(sql + " AND at>?", row["learner"], row["started"])
    else:
        rows = db.rows(sql, row["learner"])
    have = {(q.get("key"), q.get("seed")) for q in served}
    return {(r["template"], r["seed"]): (r["note"], json.loads(r["marks"] or "[]"))
            for r in rows if (r["template"], r["seed"]) in have}


def _tries_count(row) -> dict:
    return {r["qid"]: r["n"] for r in db.rows(
        "SELECT qid, COUNT(*) n FROM tries WHERE session=? AND n>0 GROUP BY qid", row["id"])}


def _attempt_rows(row) -> dict:
    return {r["qid"]: r for r in db.rows(
        "SELECT * FROM attempts WHERE id IN (SELECT MIN(id) FROM attempts WHERE session=? GROUP BY qid)", row["id"])}


def _current(row, cfg: dict, served: list[dict], answers: dict):
    """The question to show: the position the student left, else the newest
    served question still open."""
    if row["finished"]:
        return None
    open_ones = [q for q in served if q.get("kind", "question") == "question"
                 and (answers.get(q["id"]) in (None, "") or
                      ((cfg.get("retry") or {}).get(q["id"]) and not cfg["retry"][q["id"]].get("final")))]
    at = cfg.get("at")
    if at and any(q["id"] == at for q in served):
        q = next(q for q in served if q["id"] == at)
        if q in open_ones or q.get("kind") == "example":
            return q
    if served and served[-1].get("kind") == "example" and served[-1]["id"] not in (cfg.get("examples_seen") or []):
        return served[-1]
    if served and served[-1].get("kind") == "word" and served[-1]["id"] not in (cfg.get("words_done") or {}):
        return served[-1]
    fresh = [q for q in open_ones if q["id"] not in (cfg.get("skipped") or [])]
    if fresh:
        return fresh[-1]
    return None


def public_q(row, cfg: dict, q: dict) -> dict:
    out = public(q)
    if cfg.get("hide_skill") and not revealable(row, cfg, q["id"]):
        out.pop("type_name", None)
        out.pop("about", None)
        out["mixup"] = True
    out.update(_aids(row, cfg, q))
    out["strikes"] = (cfg.get("strike") or {}).get(q["id"], [])
    return out


def state(row) -> dict:
    """Where a drill stands, so a reload resumes it rather than starting over."""
    row = lazy_finish(row)
    cfg, served, answers = _cfg(row), _served(row), db.load_answers(row)
    finished = row["finished"] is not None
    voided = _voided(row, served)
    flagged = _flags(row)
    notes = _notes(row, cfg, served)
    tries = _tries_count(row)
    firsts = _attempt_rows(row)
    current = _current(row, cfg, served, answers)
    questions = _served_questions(served)
    rows = []
    for q in served:
        kind = q.get("kind", "question")
        qid = q["id"]
        meta = (cfg.get("end_meta") or {}).get(qid, {})
        a = firsts.get(qid)
        rows.append({
            "id": qid, "n": q.get("n"), "kind": kind, "topic": q.get("topic"), "skill": q.get("skill"),
            "type_name": None if cfg.get("hide_skill") and not revealable(row, cfg, qid) else q.get("type_name"),
            "difficulty": q.get("difficulty"), "level": q.get("level"), "rough": q.get("rough"),
            "why": None if _challenge(row) else q.get("why"), "repair": bool(q.get("repair")),
            "status": kind if kind != "question" else status_of(q, answers, cfg, finished, voided),
            "marked": qid in flagged, "has_note": bool(notes.get((q.get("key"), q.get("seed")), (None,))[0]),
            "strikes": (cfg.get("strike") or {}).get(qid, []), "ms": (cfg.get("ms") or {}).get(qid, 0),
            "tries": (1 if a or qid in answers else 0) + tries.get(qid, 0),
            "guess": bool((a and a["guess"]) or meta.get("guess") or meta.get("conf") == "guess"),
            "conf": (a["conf"] if a else meta.get("conf")),
            "budget_ms": q.get("budget_ms"), "final": bool(q.get("final")), "slot_of": q.get("slot_of"),
            "cb_id": q.get("cb_id"), "zone": q.get("zone"), "twin": q.get("twin"),
            "helped": bool((a and a["hints"]) or (cfg.get("hints") or {}).get(qid))})
    total = cfg.get("total")
    challenge = _challenge(row)
    closed = finished or challenge
    fb = cfg.get("feedback", "instant")
    out = {
        "id": row["id"], "mode": row["kind"], "kind": row["kind"], "subject": cfg.get("subject", "math"),
        "source": cfg.get("source"), "topics": cfg.get("topics", []), "pool": cfg.get("pool", "new"),
        "total": total, "timed": cfg.get("timed", False), "seconds": seconds_of(cfg),
        "seconds_left": seconds_left(row, cfg), "elapsed": elapsed_s(row, cfg),
        "paused": bool(cfg.get("paused_at")),
        "started": row["started"], "finished": row["finished"],
        "answered": sum(1 for q in questions if answers.get(q["id"]) not in (None, "", "_skip")),
        "marks": [scoring.is_correct(q, answers[q["id"]]) for q in questions if q["id"] in answers]
        if fb != "end" or finished else [None for q in questions if q["id"] in answers],
        "question": public_q(row, cfg, current) if current else None,
        "current": current["id"] if current else None, "at": cfg.get("at"),
        "served": rows, "feedback": fb, "repairs": cfg.get("repairs", "next"),
        "adaptive": cfg.get("adaptive", False), "order": cfg.get("order", "mixed"), "mix": cfg.get("mix", "even"),
        "zone": cfg.get("zone", "off"), "tier_mix": cfg.get("tier_mix", "any"),
        "plan": cfg.get("plan", []), "clock_log": cfg.get("clock_log", []),
        "conf_active": progress.conf_active(row["learner"]), "hide_skill": bool(cfg.get("hide_skill")),
        "clean": bool(cfg.get("clean")), "share": cfg.get("share"), "box": cfg.get("box"),
        "final": _final_offer(row, cfg, served, answers),
        "can": {"pause": not closed, "skip": not closed, "more": not closed and not cfg.get("fixed"),
                "retake": not challenge and finished, "share": not challenge,
                "guess": not challenge, "hint": not closed and fb != "end" and cfg.get("hints_on", True),
                "permalink": (not challenge) or _day_passed(row), "clean": not challenge},
    }
    if row["contest"]:
        extra = deps.part("compete", "state_extra")
        if extra:
            try:
                out.update(extra(row))
            except Exception:
                pass
    return out


def _final_offer(row, cfg: dict, served: list[dict], answers: dict) -> dict | None:
    """P12: 'Final round: the 3 you missed, new numbers' once the last slot is in."""
    if cfg.get("final_started") or not cfg.get("final_round", False) or cfg.get("count") is None \
            or cfg.get("feedback") == "end" or _challenge(row) or row["finished"]:
        return {"started": True, "n": cfg.get("final_n", 0)} if cfg.get("final_started") else None
    qs = [q for q in _served_questions(served) if not q.get("final")]
    if len(qs) < (cfg.get("total") or 0):
        return None
    if any(answers.get(q["id"]) in (None, "") for q in qs):
        return None
    missed = _first_misses(row, served)
    return {"offer": bool(missed), "n": len(missed), "templates": [m["template"] for m in missed]}


def _first_misses(row, served: list[dict]) -> list[dict]:
    firsts = _attempt_rows(row)
    out, seen = [], set()
    for q in _served_questions(served):
        a = firsts.get(q["id"])
        if a and not a["correct"] and q["key"] not in seen and not q.get("final"):
            seen.add(q["key"])
            out.append({"template": q["key"], "tier": q["difficulty"], "fmt": q["type"], "of": q["id"]})
    return out[:5]


def start_final(row) -> dict:
    cfg, served, answers = _cfg(row), _served(row), db.load_answers(row)
    offer = _final_offer(row, cfg, served, answers)
    if not offer or not offer.get("offer"):
        raise HTTPException(409, {"reason": "no_final_round"})
    missed = _first_misses(row, served)
    cfg.pop("pending", None)
    cfg["final_queue"] = [{**m, "final": True,
                           "why": {"kind": "final", "detail": f"Final round: you missed this one at question {int(m['of'][1:])}"}}
                          for m in missed]
    cfg["final_started"] = True
    cfg["final_n"] = len(missed)
    cfg["total"] = (cfg.get("total") or 0) + len(missed)
    q = _serve(row, cfg, served)
    _save(row["id"], cfg, served)
    return {"total": cfg["total"], "question": public_q(row, cfg, q) if q else None,
            "index": len(served)}


def next_question(row, skip: bool = False, ms: int | None = None) -> dict:
    cfg, served, answers = _cfg(row), _served(row), db.load_answers(row)
    if cfg.get("paused_at"):
        raise Paused()
    if skip:
        cur = _current(row, cfg, served, answers)
        if cur is not None and cur.get("kind", "question") == "question":
            if cur["id"] not in cfg.setdefault("skipped", []):
                cfg["skipped"].append(cur["id"])
            if cur["id"] not in cfg.setdefault("skipped_ever", []):
                cfg["skipped_ever"].append(cur["id"])
            if ms:
                _add_ms(cfg, cur["id"], ms)
            cfg["at"] = None
            cfg.pop("pending", None)            # a skip discards the preview (P23)
    elif served:
        last = served[-1]
        if last.get("kind") == "example" and last["id"] not in cfg.setdefault("examples_seen", []):
            cfg["examples_seen"].append(last["id"])          # Next past a worked example
        elif last.get("kind") == "word" and last["id"] not in cfg.setdefault("words_done", {}):
            cfg["words_done"][last["id"]] = {"skipped": True, "word": last.get("word")}   # Next past a word card
        else:
            cur = _current(row, cfg, served, answers)
            if cur is not None and cur["id"] not in (cfg.get("skipped") or []):
                _save(row["id"], cfg, served)
                return {"question": public_q(row, cfg, cur), "index": served.index(cur) + 1,
                        "total": cfg.get("total")}
    committed = commit_pending(row, cfg, served)
    if committed:
        cfg["at"] = committed["id"]
        _save(row["id"], cfg, served)
        return {"question": public_q(row, cfg, committed), "index": len(served), "total": cfg.get("total")}
    asked = _served_questions(served)
    total = cfg.get("total")
    if total is not None and len(asked) >= total:
        left = [q for q in asked if answers.get(q["id"]) in (None, "")]
        if left:                                   # the skipped ones come back before done
            q = left[0]
            if q["id"] in cfg.get("skipped", []):
                cfg["skipped"].remove(q["id"])
            cfg["at"] = q["id"]
            _save(row["id"], cfg, served)
            return {"question": public_q(row, cfg, q), "index": served.index(q) + 1, "total": total,
                    "revisit": True}
        wc = _word_due(row, cfg, served, at_end=True)          # P12: word cards left after the last slot
        if wc:
            _commit(row, served, wc)
            cfg["at"] = wc["id"]
            _save(row["id"], cfg, served)
            return {"question": public_q(row, cfg, wc), "index": len(served), "total": total}
        _save(row["id"], cfg, served)
        return {"done": True, "total": total, "final": _final_offer(row, cfg, served, answers)}
    q = _serve(row, cfg, served)
    if q is not None:
        cfg["at"] = q["id"]
    _save(row["id"], cfg, served)
    if q is None:
        return {"done": True, "exhausted": True, "total": cfg.get("total")}
    return {"question": public_q(row, cfg, q), "index": len(served), "total": cfg.get("total")}


def _answers(sid: str) -> dict:
    return json.loads(db.one("SELECT answers FROM sessions WHERE id=?", sid)["answers"] or "{}")


def _own(q: dict, own: str):
    """P5: a typed answer matched to the options: (index or None, how)."""
    typed = str(own).strip()
    if not typed or len(typed) > 40:
        raise HTTPException(422, {"field": "own", "reason": "type an answer"})
    from satbank.item import numeral
    for i, choice in enumerate(q.get("choices") or ()):
        value = numeral(choice)
        if value is not None and scoring.grid_equal(typed, str(choice).replace("−", "-")):
            return i
        if value is not None:
            try:
                if abs(float(typed.replace("−", "-")) - value) < 1e-9:
                    return i
            except ValueError:
                pass
    try:
        from satbank import expr
        for i, choice in enumerate(q.get("choices") or ()):
            if expr.agree(typed, choice):
                return i
    except Exception:
        pass
    return None


def _resolve_conf(learner: str, conf, guess: bool) -> str | None:
    if guess or conf == "guess":
        return "guess"
    if conf == "auto":
        return "sure" if progress.conf_active(learner) else None
    return conf if conf in ("sure", "unsure") else None


def answer(row, qid: str, given, ms: int | None, *, conf=None, guess: bool = False, own=None,
           hints: int = 0, keep_marked: bool = False) -> dict:
    cfg, served = _cfg(row), _served(row)
    learner = row["learner"]
    if cfg.get("paused_at"):
        raise Paused()
    if commit_pending(row, cfg, served, qid):
        cfg["at"] = qid
    q = next((x for x in served if x["id"] == qid), None)
    if q is None:
        raise NotServed(qid)
    if overtime(row, cfg) and not row["contest"]:
        raise Closed("time is up")
    if ms:
        _add_ms(cfg, qid, ms)
    if qid in (cfg.get("skipped") or []):
        cfg["skipped"].remove(qid)
    if q.get("kind") == "word":
        raise HTTPException(409, {"reason": "a word card is answered through /word"})
    if q.get("kind") == "example":                 # a worked example files nothing
        cfg.setdefault("examples_seen", []).append(qid)
        ok = scoring.is_correct(q, given)
        nxt = preview_next(row, cfg, served) if _save_after(row, cfg, served) else None
        _save(row["id"], cfg, served)
        return {**_reveal(q, given, ok), "correct": ok, "example": True, "filed": False,
                "question_id": qid, "next": public(nxt) if nxt else None}
    conf = _resolve_conf(learner, conf, guess)
    hints = max(int(hints or 0), (cfg.get("hints") or {}).get(qid, 0))
    cover = None
    if own is not None and q["type"] == "mcq":
        match = _own(q, own)
        if match is None:
            db.run("INSERT INTO tries(learner,session,qid,n,given,correct,reason,ms,at) VALUES (?,?,?,0,?,0,?,?,?)",
                   learner, row["id"], qid, str(own)[:40], "cover_miss", ms, progress.now())
            cfg.setdefault("uncovered", []).append(qid)
            _save(row["id"], cfg, served)
            return {"cover": "none", "correct": None, "filed": False, "own": str(own),
                    "note": f"No choice is {own}. Recheck, then pick."}
        given = match
        cover = "key" if scoring.is_correct(q, given) else "distractor"
    struck = (cfg.get("strike") or {}).get(qid) or None
    fb = cfg.get("feedback", "instant")
    files_now = fb != "end" or row["contest"]
    if not files_now:
        if db.set_answer(row["id"], qid, given) is False and row["finished"]:
            raise Closed("this set is finished")
        cfg.setdefault("end_meta", {})[qid] = {"conf": conf, "hints": hints, "guess": conf == "guess",
                                              "cover": bool(cover), "at": progress.now()}
        _probe_step(cfg, q, scoring.is_correct(q, given))
        _save(row["id"], cfg, served)
        answers = _answers(row["id"])
        nxt = None
        if q["id"] == (served[-1]["id"] if served else None):
            nxt = preview_next(row, cfg, served)
            _save(row["id"], cfg, served)
        return {"saved": True, "given": given, "question_id": qid, "skill": q.get("skill"),
                "budget_ms": q.get("budget_ms"), "total": cfg.get("total"),
                "answered": sum(1 for x in _served_questions(served) if answers.get(x["id"]) not in (None, "")),
                "next": public(nxt) if nxt else None}
    retry = (cfg.get("retry") or {}).get(qid)
    if fb == "retry" and retry and not retry.get("final"):
        return _later_try(row, cfg, served, q, given, ms)
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
        return _feedback(row, q, given, ok, reason, [], [], None, None, cfg, answers, served,
                         learner=learner)
    # ponytail: attempts.sms stays Compete's (S8 scores the client's ms today, as its check expects)
    sms = None
    before = progress.topic_mastery(learner, q["topic"])
    best_before = db.one(f"SELECT MIN(COALESCE(ms, sms)) m FROM attempts WHERE learner=? AND template=? AND correct=1"
                         f" AND guess=0 AND hints=0 AND {progress.COUNTED}", learner, q["key"])["m"]
    filed = progress.record(learner, row["id"], q, given, cfg.get("ms", {}).get(qid) or ms,
                            conf=conf, hints=hints, struck=struck, cover=bool(cover),
                            calc=bool((cfg.get("calc") or {}).get(qid)), sms=sms,
                            placement=bool(cfg.get("probe")))
    after = progress.topic_mastery(learner, q["topic"])
    answers = _answers(row["id"])
    _after_first(row, cfg, q, filed, conf, served)
    if fb == "retry" and not filed["correct"]:
        cfg.setdefault("retry", {})[qid] = {"n": 1, "final": False}
        _save(row["id"], cfg, served)
        return {"correct": False, "final": False, "given": given, "question_id": qid,
                "mistake": _cap(filed["reason"]), "filler": _chosen_filler(q, given), "tries_left": 2,
                "status": "unanswered", "rungs": q.get("rungs"), "hint": cfg.get("hints_on", True)}
    if fb == "retry":
        cfg.setdefault("retry", {})[qid] = {"n": 1, "final": True}
    nxt = preview_next(row, cfg, served) if _save_after(row, cfg, served) else None
    _save(row["id"], cfg, served)
    out = _feedback(row, q, given, filed["correct"], filed["reason"], filed["opened"],
                    filed["closed"], before, after, cfg, answers, served, filed=filed,
                    learner=learner, conf=conf, cover=cover, best_before=best_before)
    out["next"] = public(nxt) if nxt else None
    return out


def _save_after(row, cfg: dict, served: list[dict]) -> bool:
    """Is there a next question to preview? Only at the frontier of a set
    that still has room."""
    if row["finished"]:
        return False
    total = cfg.get("total")
    asked = _served_questions(served)
    return total is None or len(asked) < total or bool(cfg.get("more") or cfg.get("final_queue"))


def _chosen_filler(q: dict, given) -> bool:
    """Was the picked option a filler (a near value naming no mistake)?"""
    flags = q.get("filler") or []
    return bool(isinstance(given, int) and 0 <= given < len(flags) and flags[given])


def _cap(reason: str | None) -> str | None:
    return reason[:1].upper() + reason[1:] if reason else None


def _probe_step(cfg: dict, q: dict, ok: bool) -> None:
    """P11's staircase: up a tier after a right, down after a miss."""
    probe = cfg.get("probe")
    if not probe or q["topic"] not in probe:
        return
    at = TIERS.index(probe[q["topic"]])
    probe[q["topic"]] = TIERS[min(2, at + 1)] if ok else TIERS[max(0, at - 1)]


def _after_first(row, cfg: dict, q: dict, filed: dict, conf: str | None, served: list[dict]) -> None:
    """Adaptive steps, the probe, the fluency sprint's target and the repair
    after a first try, as before plus the upgrades."""
    _probe_step(cfg, q, filed["correct"])
    if cfg.get("per_q") and filed["correct"] and q.get("target_ms"):
        spent = (cfg.get("ms") or {}).get(q["id"], 0)
        if spent and spent <= q["target_ms"]:
            factor = (cfg.setdefault("target", {})).get(q["key"], 1.0)
            cfg["target"][q["key"]] = max(0.6, round(factor * 0.85, 3))
    # one repair per question: a missed repair stays an open mistake for later,
    # or a student who keeps missing would never reach the end of the set
    if cfg.get("adaptive") and not q.get("repair"):
        # R33 steps within the selected tiers this skill actually has here
        names = cfg.get("templates") or [t for topic in cfg.get("topics", ())
                                         for t in practice.catalogue()["by_topic"].get(topic, ())]
        have = _tiers_of(q["key"]).union(*(_tiers_of(t) for t in names
                                           if blueprint.kinds().get(t, {}).get("skill") == q["skill"]))
        options = [t for t in TIERS if t in cfg.get("tiers", TIERS) and t in have] or [q["difficulty"]]
        state_ = cfg.setdefault("adaptive_state", {}).setdefault(q["skill"],
                    {"tier": q["difficulty"], "rights": 0})
        current = state_["tier"] if state_["tier"] in options else q["difficulty"]
        at = options.index(current) if current in options else 0
        if filed["correct"] and filed.get("clean"):
            state_["rights"] += 1
            if state_["rights"] >= 2:
                state_["tier"] = options[min(at + 1, len(options) - 1)]
                state_["rights"] = 0
        else:
            state_["tier"] = options[max(at - 1, 0)]
            state_["rights"] = 0
    repairs = cfg.get("repairs", "next")
    if not filed["correct"] and not cfg.get("fixed") and not q.get("repair") and repairs != "off" \
            and not q.get("final") and row["kind"] != "challenge":
        normalized = progress.norm(filed["reason"] or "")
        named = progress.named(normalized)
        want = "^" + re.escape(normalized) + "$" if named else None
        repair = {"template": q["key"], "want": want, "norm": normalized if named else None}
        if conf == "sure":
            repairs = "next"                  # P7: a confident miss comes back first
        if repairs == "end":
            cfg.setdefault("end_repairs", []).append(repair)
        elif repairs == "later":
            cfg.setdefault("later_repairs", []).append(
                {"repair": repair, "at": len(_served_questions(served)) + 3})
        else:
            cfg["repair"] = repair
        if cfg.get("total") is not None:
            cfg["total"] += 1


def _later_try(row, cfg: dict, served: list[dict], q: dict, given, ms) -> dict:
    """Retry mode: tries 2 and 3 go into tries; a named reason files a trap
    hit; a right later try makes the question Mixed."""
    learner = row["learner"]
    r = cfg["retry"][q["id"]]
    r["n"] += 1
    ok = scoring.is_correct(q, given)
    reason = "" if ok else progress._reason_of(q, given)[0]
    db.run("INSERT INTO tries(learner,session,qid,n,given,correct,reason,ms,at,hints) VALUES (?,?,?,?,?,?,?,?,?,?)",
           learner, row["id"], q["id"], r["n"], str(given), int(ok), reason or None, ms, progress.now(),
           (cfg.get("hints") or {}).get(q["id"], 0))
    if not ok and reason and progress.named(progress.norm(reason)):
        progress.record_trap(learner, q, reason, progress.now(), row["id"])
    if ok:
        r.update({"final": True, "right": True})
    elif r["n"] >= 3:
        r["final"] = True
    if not r["final"]:
        _save(row["id"], cfg, served)
        return {"correct": False, "final": False, "given": given, "question_id": q["id"],
                "mistake": _cap(reason), "filler": _chosen_filler(q, given), "tries_left": 3 - r["n"],
                "status": "unanswered"}
    nxt = preview_next(row, cfg, served) if _save_after(row, cfg, served) else None
    _save(row["id"], cfg, served)
    answers = _answers(row["id"])
    first = db.load_answers(row).get(q["id"])
    out = _feedback(row, q, first, False, reason, [], [], None, None, cfg, answers, served, learner=learner)
    out.update({"correct": ok, "final": True, "try": r["n"], "given": given,
                "status": "mixed" if ok else "incorrect", "next": public(nxt) if nxt else None})
    return out


def reveal(row, qid: str) -> dict:
    """Retry mode's Show answer: the tries end, the question is Incorrect."""
    cfg, served = _cfg(row), _served(row)
    if cfg.get("feedback") != "retry":
        raise HTTPException(409, {"reason": "reveal is for retry mode"})
    r = (cfg.get("retry") or {}).get(qid)
    q = next((x for x in served if x["id"] == qid), None)
    if q is None:
        raise NotServed(qid)
    answers = db.load_answers(row)
    if not r and qid not in answers:
        raise HTTPException(409, {"reason": "answer it first"})
    if r and r.get("final"):
        raise HTTPException(409, {"reason": "already shown"})
    cfg.setdefault("retry", {})[qid] = {**(r or {"n": 1}), "final": True, "revealed": True}
    nxt = preview_next(row, cfg, served) if _save_after(row, cfg, served) else None
    _save(row["id"], cfg, served)
    given = answers.get(qid)
    reason = progress._reason_of(q, given)[0] if given is not None else ""
    out = _feedback(row, q, given, False, reason, [], [], None, None, cfg, _answers(row["id"]), served,
                    learner=row["learner"])
    out.update({"status": "incorrect", "final": True, "next": public(nxt) if nxt else None})
    return out


def _reveal(q: dict, given, ok: bool) -> dict:
    """The key side of a verdict, for when it can be revealed."""
    steps = q.get("steps") or []
    option = q.get("step_of") or []
    chosen = option[given] if q.get("type") == "mcq" and isinstance(given, int) and 0 <= given < len(option) else None
    out = {"answer": q["answer"], "answer_index": "ABCD".index(q["answer"]) if q["type"] == "mcq" else None,
           "rationale": q["rationale"], "reasons": [r or None for r in q.get("reasons", ())],
           "filler": q.get("filler", []), "steps": steps,
           "diverge": chosen.get("at") if isinstance(chosen, dict) else None,
           "wrong_step": chosen.get("wrong") if isinstance(chosen, dict) else None,
           "option_steps": [s.get("at") if isinstance(s, dict) else None for s in option],
           "figure_alt": q.get("figure_alt"), "type_name": q.get("type_name"), "about": q.get("about")}
    if q.get("type") == "spr":
        out["accepted"] = scoring.accepted_forms(str(q["answer"]))
        out["spr_reasons"] = q.get("spr_reasons") or []
    if desmos_on() and q.get("desmos"):
        out["desmos"] = q["desmos"]
    formula = _formula(q.get("key"))
    if formula:
        out["formula"] = formula
    return out


def _formula(template: str | None):
    """P24: the formulas a template uses, once T-bank's satbank.formulas lands."""
    try:
        from satbank import formulas
    except Exception:
        return None
    ids = getattr(formulas, "USES", {}).get(template)
    if not ids:
        return None
    sheet, know = getattr(formulas, "SHEET", {}), getattr(formulas, "KNOW", {})
    return [{"id": i, "on_sheet": i in sheet, "text": (sheet.get(i) or know.get(i) or {}).get("text")
             if isinstance(sheet.get(i) or know.get(i), dict) else str(sheet.get(i) or know.get(i) or i)}
            for i in ids]


def _fmt_ms(ms) -> str:
    s = max(0, round((ms or 0) / 1000))
    return f"{s // 60}:{s % 60:02d}"


def _feedback(row, q, given, ok, reason, opened, closed, before, after, cfg, answers, served,
              filed: dict | None = None, learner: str | None = None, conf: str | None = None,
              cover: str | None = None, best_before=None) -> dict:
    run = 0
    for x in reversed([x for x in _served_questions(served) if x["id"] in answers]):
        if not scoring.is_correct(x, answers[x["id"]]):
            break
        run += 1
    mistake = _cap(reason)
    family = {"seen": 0, "right": 0}
    if learner:
        r = db.one("SELECT COUNT(*) seen,COALESCE(SUM(correct),0) n_right FROM attempts"
                   " WHERE learner=? AND template=?", learner, q["key"])
        family = {"seen": r["seen"], "right": r["n_right"]}
    challenge = _challenge(row)
    spent = (cfg.get("ms") or {}).get(q["id"]) or 0
    budget = q.get("budget_ms") or 95_000
    out = {
        "correct": ok, "given": given, "question_id": q["id"],
        "mistake": mistake,
        "skill": q.get("skill"),
        "opened": opened, "closed": closed,
        "opened_ids": (filed or {}).get("opened_ids", []),
        "closed_ids": (filed or {}).get("closed_ids", []),
        "checked": (filed or {}).get("checked", []),
        "relapsed": (filed or {}).get("relapsed", []),
        "not_offered": (filed or {}).get("not_offered", []),
        "offered": (filed or {}).get("offered", progress.offered_of(q)),
        "family": family,
        "flagged": (filed or {}).get("flagged", False),
        "repeat": (filed or {}).get("repeat", False),
        "trap_true": q.get("trap_true"),
        "budget_ms": q.get("budget_ms"),
        "saved_note": "Saved for another look" if cfg.get("pool") == "saved" else None,
        "mastery": None if before is None else {"topic": q["topic"], "before": before, "after": after},
        "total": cfg.get("total"), "answered": sum(1 for x in _served_questions(served) if answers.get(x["id"]) not in (None, "")),
        "streak": run, "rungs": q.get("rungs"), "level": q.get("level"), "rough": q.get("rough"),
        "odds": q.get("odds"),
        "status": status_of(q, answers, cfg, row["finished"] is not None, set()),
    }
    out.update(_reveal(q, given, ok))
    struck = (cfg.get("strike") or {}).get(q["id"]) or []
    key = out["answer_index"]
    out["struck_key"] = key is not None and key in struck
    out["strikes_graded"] = [{"choice": i, "key": i == key, "reason": (q.get("reasons") or [None] * 4)[i] or None}
                             for i in struck if 0 <= i < 4]
    if cover:
        out["cover"] = cover
    # the clock (P16): fluent, slow or rushed against this question's budget
    if spent:
        out["pace"] = {"ms": spent, "budget_ms": budget,
                       "type_avg_ms": (db.one("SELECT AVG(ms) m FROM attempts WHERE learner=? AND template=?"
                                              " AND ms IS NOT NULL", learner, q["key"]) or {"m": None})["m"]
                       if learner else None}
        out["fluency"] = ("rushed" if not ok and spent < budget * .25 else
                          "fluent" if ok and spent <= budget else "slow" if spent > budget else None)
        if ok and best_before and spent < best_before and filed and filed.get("clean"):
            out["best"] = {"ms": spent, "before": best_before,
                           "text": f"New best on this type: {_fmt_ms(spent)}"}
    if not challenge and learner:
        crowd = levels().get((q["key"], q["difficulty"]), {}).get("crowd")
        out["crowd"] = crowd
    else:
        out["crowd"] = None
    if learner and filed:
        out["next_step"] = _next_step(learner, q, ok, filed, run)
        out["then"] = _then(learner, q, ok, spent, filed)
        if not ok:
            out["cause"] = _cause(learner, q, filed, cfg, given)
            twice = db.one("SELECT COUNT(*) n FROM attempts WHERE learner=? AND template=? AND correct=0"
                           " AND repeat=0 AND at>=?", learner, q["key"],
                           (_now() - dt.timedelta(days=30)).isoformat())["n"]
            clean_rights = db.one("SELECT COUNT(*) n FROM attempts WHERE learner=? AND template=? AND correct=1"
                                  " AND guess=0 AND hints=0 AND repeat=0", learner, q["key"])["n"]
            if twice >= 2 and clean_rights < 2 and not challenge:
                out["learn_offer"] = "Missed this type twice. Learn it step by step · 3 questions · ~4 min"
            if conf == "sure":
                out["confident_miss"] = ("You were sure, and it's wrong: this kind costs points on test day, "
                                         "because you wouldn't re-check it. It comes back first.")
    if row["contest"]:
        line = deps.part("compete", "field_line")
        if line:
            try:
                slot = next(i for i, x in enumerate(_served_questions(served), 1) if x["id"] == q["id"])
                out["field"] = line(q["key"], q["difficulty"], row["contest"], slot)
            except Exception:
                pass
        if cfg.get("feedback") == "end":
            out = {k: out[k] for k in ("given", "question_id", "total", "answered")}
            out["saved"] = True
    return out


def _next_step(learner: str, q: dict, ok: bool, filed: dict, run: int) -> str | None:
    """P9: one line under the verdict, the first that applies."""
    if filed.get("closed"):
        return f"That closes it: {filed['closed'][0]} is fixed · a check-in comes back in 3 days"
    trap = next((t for t in progress.open_traps(learner) if t["template"] == q["key"]), None)
    if trap:
        n = trap["owed"]
        return f"{trap['label']}: {n} more clean answer{'s close' if n != 1 else ' closes'} it"
    if (q.get("why") or {}).get("kind") == "due":
        return "Held · back in 12 days if you keep it" if ok else "Slipped · back tomorrow"
    firsts = db.rows(f"SELECT correct FROM attempts WHERE learner=? AND template=? AND {progress.COUNTED}",
                     learner, q["key"])
    if ok and sum(r["correct"] for r in firsts) == 2:
        names = practice.catalogue()["by_topic"].get(q["topic"], ())
        ready = sum(1 for t in names if db.one(f"SELECT COUNT(*) n FROM attempts WHERE learner=? AND template=?"
                                              f" AND correct=1 AND {progress.COUNTED}", learner, t)["n"] >= 2)
        return f"{q.get('type_name') or type_name(q['key'])} is now ready · {q.get('topic_name')} {ready} of {len(names)} types ready"
    k = progress.steps_to(learner, q["topic"], progress.STRONG, "medium")
    if k:
        return f"{q.get('topic_name')}: {k} more first-try right{'s' if k != 1 else ''} at Medium or Hard → Strong"
    if run >= 2:
        return f"{run} in a row in {q.get('topic_name')}"
    return None


def _then(learner: str, q: dict, ok: bool, spent: int, filed: dict) -> str | None:
    """P9: Then vs now, when this right follows an earlier first-try miss."""
    if not ok:
        return None
    old = db.one("SELECT given, reason, ms, at, fmt FROM attempts WHERE learner=? AND template=? AND correct=0"
                 " AND repeat=0 AND id<? ORDER BY id LIMIT 1", learner, q["key"], filed.get("attempt") or 1 << 62)
    if not old:
        return None
    letter = "ABCD"[int(old["given"])] if old["fmt"] == "mcq" and str(old["given"]).isdigit() \
        and int(old["given"]) < 4 else old["given"]
    # the choice then and the result now: no times, and no trap sentence (the next-step line above already names it; the user)
    return f"{_day_word(old['at'])} on this type: {letter} · today: right"


def cause_kind(learner: str, a: dict, q: dict, cfg: dict, medians: dict) -> tuple[str, dict]:
    """P8's first match (clock, entry, slip, trap, gap) over F4's cause_of,
    which reads a named distractor as a trap before the slip rules: a learner
    right on 4 of the last 5 first tries on the type, or an easy one done in
    under half the median time, slipped."""
    history = [r["correct"] for r in db.rows(
        f"SELECT correct FROM attempts WHERE learner=? AND template=? AND id<? AND {progress.COUNTED}"
        " ORDER BY id DESC LIMIT 5", learner, q["key"], a["id"])]
    kind, ev = progress.cause_of(a, {"history": history, "median_easy_ms": medians.get("easy"),
                                     "key": q["answer"], "spr_reasons": q.get("spr_reasons"),
                                     "timed": bool(cfg.get("timed"))})
    if kind == "trap" and not ev.get("set_by"):
        ms = a.get("ms") if a.get("ms") is not None else a.get("sms")
        if len(history) >= 5 and sum(history) >= 4:
            return "slip", {**ev, "usually_right": f"{sum(history)} of your last 5"}
        easy = medians.get("easy")
        if a.get("difficulty") == "easy" and easy and ms is not None and ms < easy / 2:
            return "slip", {**ev, "fast": True}
    return kind, ev


def _cause(learner: str, q: dict, filed: dict, cfg: dict, given) -> dict | None:
    """P8: T7's cause of this miss, pre-selected, with the reason shown."""
    a = db.one("SELECT * FROM attempts WHERE id=?", filed.get("attempt"))
    if not a:
        return None
    kind, ev = cause_kind(learner, dict(a), q, cfg, progress._tier_medians(learner))
    why = None
    if kind == "slip" and ev.get("usually_right"):
        why = f"You usually get this type right, and this took {_fmt_ms(ev.get('ms'))}."
    elif kind == "slip" and ev.get("fast"):
        why = f"An easy one, answered in {_fmt_ms(ev.get('ms'))}."
    return {"kind": kind, "why": why, "choices": ["trap", "slip", "misread", "clock", "gap"] +
            (["entry"] if q.get("type") == "spr" else [])}


# ------------------------------------------------------------------ S4: the session's actions

def _open(row, cfg: dict) -> None:
    if row["finished"]:
        raise HTTPException(409, {"reason": "this set is finished"})


def _no_challenge(row, what: str) -> None:
    if _challenge(row):
        raise HTTPException(409, {"reason": f"no {what} in the challenge"})


def time_on(row, qid: str, ms: int) -> dict:
    """/time: ms onto the question (capped), and the resume position."""
    cfg, served = _cfg(row), _served(row)
    _open(row, cfg)
    commit_pending(row, cfg, served, qid)
    if not any(q["id"] == qid for q in served):
        raise NotServed(qid)
    add = min(max(0, int(ms)), progress.MS_CAP)
    _add_ms(cfg, qid, add)
    cfg["at"] = qid
    _save(row["id"], cfg, served)
    return {"question_id": qid, "ms": cfg["ms"][qid], "at": qid}


def strike(row, qid: str, choice: int, on: bool, by: str | None = None) -> dict:
    cfg, served = _cfg(row), _served(row)
    _open(row, cfg)
    commit_pending(row, cfg, served, qid)
    q = next((x for x in served if x["id"] == qid), None)
    if q is None:
        raise NotServed(qid)
    if q.get("type") != "mcq" or not 0 <= choice < len(q.get("choices") or ()):
        raise HTTPException(422, {"field": "choice", "reason": "strike a choice 0–3"})
    marks = cfg.setdefault("strike", {}).setdefault(qid, [])
    if on and choice not in marks:
        marks.append(choice)
    elif not on and choice in marks:
        if (cfg.get("strike_by") or {}).get(qid, {}).get(str(choice)) == "hint":
            raise HTTPException(409, {"reason": "a hint's strike stays"})
        marks.remove(choice)
    if by == "hint":
        cfg.setdefault("strike_by", {}).setdefault(qid, {})[str(choice)] = "hint"
    marks.sort()
    _save(row["id"], cfg, served)
    return {"question_id": qid, "strikes": marks}


def more(row, qid: str, step: int = 0, axis: str | None = None, want: str | None = None,
         n: int = 1, ladder: bool = False) -> dict:
    """/more: the same template next (an adjacent tier, a sibling, a grid-in,
    another ask, a named trap, or the Learn ladder). A fixed total grows."""
    cfg, served = _cfg(row), _served(row)
    _open(row, cfg)
    _no_challenge(row, "more")
    if cfg.get("paused_at"):
        raise Paused()
    q = next((x for x in served if x["id"] == qid), None)
    if q is None or q.get("kind", "question") != "question":
        raise NotServed(qid)
    axis = axis or {-1: "easier", 0: "same", 1: "harder"}.get(step, "same")
    if axis not in ("same", "easier", "harder", "grid", "ask"):
        raise HTTPException(422, {"field": "axis", "reason": "same, easier, harder, grid or ask"})
    if not 1 <= n <= 3:
        raise HTTPException(422, {"field": "n", "reason": "1–3"})
    info = blueprint.kinds().get(q["key"], {})
    asks = []
    if ladder:
        slots = 3
        cfg.setdefault("examples", []).append(q["key"])
        cfg["examples_done"] = [t for t in cfg.get("examples_done", []) if t != q["key"]]
        asks = [{"template": q["key"], "why": {"kind": "learn", "detail": d}}
                for d in ("Learn this type: with help", "Learn this type: on your own", "Learn this type: on your own")]
        up = [s for s in blueprint.siblings(q["key"], 1)]
        if up:
            higher = TIERS[min(2, TIERS.index(q["difficulty"]) + 1)]
            asks[2].update({"template": up[0], "tier": higher if higher in _tiers_of(up[0]) else None})
    elif axis == "same":
        slots = n
        norm = progress.norm(want) if want else None
        if want and norm not in {progress.norm(r) for r in q.get("reasons") or () if r}:
            raise HTTPException(422, {"field": "want", "reason": "not a trap this question offers"})
        asks = [{"template": q["key"], "tier": q["difficulty"], "want": norm, "axis": "same", "of": qid,
                 "why": {"kind": "twin", "detail": "Next: one with this trap" if want else "Another like this"}}] * n
    elif axis in ("easier", "harder"):
        sib = blueprint.siblings(q["key"], -1 if axis == "easier" else 1)
        if not sib:
            raise HTTPException(409, {"reason": f"no {axis} version of this type"})
        tier = TIERS[TIERS.index(q["difficulty"]) + (-1 if axis == "easier" else 1)] \
            if 0 <= TIERS.index(q["difficulty"]) + (-1 if axis == "easier" else 1) < 3 else None
        target = sib[0]
        label = "" if target == q["key"] else f": another {q.get('topic_name')} type ({type_name(target)})"
        asks = [{"template": target, "tier": tier if tier in _tiers_of(target) else None, "axis": axis, "of": qid,
                 "why": {"kind": "step_up" if axis == "harder" else "step_down",
                         "detail": f"{axis.capitalize()}{label}"}}]
        slots = 1
    elif axis == "grid":
        if "grid" not in info.get("axes", set()):
            raise HTTPException(409, {"reason": "this type has no grid-in form"})
        asks = [{"template": q["key"], "fmt": "spr", "axis": "grid", "of": qid,
                 "why": {"kind": "twin", "detail": f"Twin · as grid-in · of question {q.get('n')}"}}]
        slots = 1
    else:
        values = [v for v in info.get("ask", []) if v != str((generate(q["key"], q["seed"]).params or {}).get("ask"))] \
            if "ask" in info.get("axes", set()) else []
        chosen = None
        for v in values:
            try:
                other = generate(q["key"], q["seed"], ask=v)
            except Exception:
                continue
            if other.stem != q["stem"]:
                chosen = v
                break
        if chosen is None:
            raise HTTPException(409, {"reason": "this type keeps no other question on the same setup"})
        asks = [{"template": q["key"], "seed": q["seed"], "ask": chosen, "axis": "ask", "of": qid,
                 "why": {"kind": "twin", "detail": "Same setup, a different question"}}]
        slots = 1
    cfg.pop("pending", None)                     # /more discards the preview (P23)
    voided = qid in _voided(row, served)
    if voided and axis == "same":                # P25: the replacement takes the slot, the time comes back
        asks = [{**a, "replaces": qid, "why": {"kind": "replacement",
                                               "detail": "Replaces a voided question: same type, new numbers"}}
                for a in asks[:1]]
        spent = (cfg.get("ms") or {}).get(qid, 0)
        if cfg.get("timing") == "pace" and spent and not (cfg.get("gave_back") or {}).get(qid):
            cfg["seconds"] = (cfg.get("seconds") or 0) + spent // 1000
            cfg.setdefault("gave_back", {})[qid] = spent
            cfg.setdefault("clock_log", []).append({"at": progress.now(), "delta_ms": spent, "why": "voided",
                                                     "qid": qid})
    cfg.setdefault("more", []).extend(json.loads(json.dumps(asks)))
    if cfg.get("total") is not None and not (voided and axis == "same"):
        cfg["total"] += slots
    _save(row["id"], cfg, served)
    return {"total": cfg.get("total"), "queued": len(asks)}


def set_paused(row, on: bool) -> dict:
    cfg, served = _cfg(row), _served(row)
    _open(row, cfg)
    _no_challenge(row, "pause")
    if on and not cfg.get("paused_at"):
        cfg["paused_at"] = progress.now()
    elif not on and cfg.get("paused_at"):
        cfg["paused_s"] = (cfg.get("paused_s") or 0) + (_now() - _at(cfg["paused_at"])).total_seconds()
        cfg["paused_at"] = None
    _save(row["id"], cfg, served)
    return {"paused": bool(cfg.get("paused_at")), "seconds_left": seconds_left(row, cfg),
            "elapsed": elapsed_s(row, cfg)}


def hint(row, qid: str) -> dict:
    """P2's ladder: rule out a trap, the first step, a worked twin. Never the
    key of the question on screen."""
    cfg, served = _cfg(row), _served(row)
    _open(row, cfg)
    _no_challenge(row, "hints")
    if cfg.get("feedback") == "end":
        raise HTTPException(409, {"reason": "no hints in end mode"})
    if not cfg.get("hints_on", True):
        raise HTTPException(409, {"reason": "hints are off"})
    q = next((x for x in served if x["id"] == qid), None)
    if q is None or q.get("kind", "question") != "question":
        raise NotServed(qid)
    answers = db.load_answers(row)
    retry = (cfg.get("retry") or {}).get(qid)
    if qid in answers and not (retry and not retry.get("final")):
        raise HTTPException(409, {"reason": "already answered"})
    rungs = q.get("rungs") or _rungs(q)
    used = (cfg.get("hints") or {}).get(qid, 0)
    if used >= len(rungs):
        raise HTTPException(409, {"reason": "no more hints"})
    kind = rungs[used]
    cfg.setdefault("hints", {})[qid] = used + 1
    out = {"rung": used + 1, "of": len(rungs), "kind": kind, "question_id": qid}
    if kind == "strike":
        reasons = q.get("reasons") or []
        filler = q.get("filler") or [False] * len(reasons)
        key = "ABCD".index(q["answer"])
        struck = set((cfg.get("strike") or {}).get(qid, []))
        options = [i for i, r in enumerate(reasons) if r and not filler[i] and i != key and i not in struck]
        mine = {t["norm"] for t in progress.open_traps(row["learner"]) if t["template"] == q["key"]}
        crowd = (levels().get((q["key"], q["difficulty"]), {}).get("crowd") or {}).get("top_mistake")
        pick = next((i for i in options if progress.norm(reasons[i]) in mine), None)
        if pick is None and crowd:
            pick = next((i for i in options if progress.norm(reasons[i]) == progress.norm(crowd)), None)
        if pick is None and options:
            pick = options[0]
        if pick is None:
            out["kind"] = kind = "example"
        else:
            cfg.setdefault("strike", {}).setdefault(qid, []).append(pick)
            cfg["strike"][qid].sort()
            cfg.setdefault("strike_by", {}).setdefault(qid, {})[str(pick)] = "hint"
            out.update({"choice": pick, "reason": reasons[pick],
                        "text": f"Struck {'ABCD'[pick]}: that's what you get if you {reasons[pick]}."})
    if kind == "step":
        out["step"] = (q.get("steps") or [None])[0]
    if kind == "example":
        ex = _example(q["key"], 0)
        if ex:
            out["example"] = {k: ex[k] for k in ("stem", "choices", "latex", "figure", "table", "type",
                                                  "answer", "rationale", "reasons", "steps", "seed", "difficulty")}
    _save(row["id"], cfg, served)
    return out


CAUSE_KINDS = ("trap", "slip", "misread", "clock", "entry", "gap")


def why(row, qid: str, kind: str) -> dict:
    """P8: the student's own cause of a miss, filed on the attempt."""
    if kind not in CAUSE_KINDS:
        raise HTTPException(422, {"field": "kind", "reason": ", ".join(CAUSE_KINDS)})
    a = db.one("SELECT id, correct FROM attempts WHERE session=? AND qid=? AND learner=? ORDER BY id LIMIT 1",
               row["id"], qid, row["learner"])
    if not a:
        raise HTTPException(409, {"reason": "answer it first"})
    if a["correct"]:
        raise HTTPException(409, {"reason": "a right answer has no cause"})
    db.run("UPDATE attempts SET miss_kind=? WHERE id=?", kind, a["id"])
    return {"question_id": qid, "kind": kind}


def calc(row, qid: str, exprs: list) -> dict:
    """P3: what the student typed in Desmos while this question was open."""
    cfg, served = _cfg(row), _served(row)
    _open(row, cfg)
    if not isinstance(exprs, list) or len(exprs) > 30 or any(not isinstance(e, str) or len(e) > 500 for e in exprs):
        raise HTTPException(422, {"field": "exprs", "reason": "up to 30 expressions of 500 characters"})
    if not any(q["id"] == qid for q in served):
        raise NotServed(qid)
    cfg.setdefault("calc", {})[qid] = exprs
    _save(row["id"], cfg, served)
    return {"question_id": qid, "saved": len(exprs)}


def word(row, token: str, given, ms: int | None) -> dict:
    """P12: a word card graded by S9 (one word_reviews row, the word's box
    moves), exactly as a Words run would. Nothing here is a slot or an attempt."""
    cfg, served = _cfg(row), _served(row)
    _open(row, cfg)
    card = next((x for x in served if x.get("kind") == "word" and x.get("token") == token), None)
    if card is None:
        raise NotServed(token)
    if card["id"] in (cfg.get("words_done") or {}):
        raise HTTPException(409, {"reason": "already answered"})
    grade = deps.part("words", "grade_item")
    if grade is None:
        raise HTTPException(501, {"reason": "words_unavailable"})
    verdict = grade(row["learner"], token, given, ms)
    verdict = verdict if isinstance(verdict, dict) else {"correct": bool(verdict)}
    cfg.setdefault("words_done", {})[card["id"]] = {"correct": bool(verdict.get("correct")),
                                                    "word": card.get("word")}
    _save(row["id"], cfg, served)
    return {**verdict, "question_id": card["id"], "kind": "word"}


def rematch_due(row, days: int) -> dict:
    """P19's 'Rematch in 3 days': U1's queue offers it on that day."""
    if not row["finished"]:
        raise HTTPException(409, {"reason": "finish_that_sitting_first"})
    _no_challenge(row, "rematch")
    cfg = _cfg(row)
    day = (progress._local_today(row["learner"]) + dt.timedelta(days=days)).isoformat()
    cfg["rematch_due"] = day
    db.run("UPDATE sessions SET cfg=? WHERE id=?", json.dumps(cfg), row["id"])
    return {"rematch_due": day}


def contest_skip(row, qid: str) -> dict:
    """Compete §8: a contest skip forfeits the question and shows its key."""
    cfg, served = _cfg(row), _served(row)
    _open(row, cfg)
    q = next((x for x in served if x["id"] == qid), None)
    if q is None:
        raise NotServed(qid)
    if not db.set_answer(row["id"], qid, "_skip", only_new=True):
        raise HTTPException(409, {"reason": "already answered"})
    nxt = preview_next(row, cfg, served) if _save_after(row, cfg, served) else None
    _save(row["id"], cfg, served)
    out = {"skipped": True, "question_id": qid, **{k: v for k, v in _reveal(q, None, False).items()
                                                   if k in ("answer", "answer_index", "rationale")}}
    out["next"] = public(nxt) if nxt else None
    return out


def detail(row, qid: str) -> dict:
    """GET /q/{qid}: everything the session shows for one served question."""
    row = lazy_finish(row)
    cfg, served = _cfg(row), _served(row)
    if commit_pending(row, cfg, served, qid):
        cfg["at"] = qid
        _save(row["id"], cfg, served)
    q = next((x for x in served if x["id"] == qid), None)
    if q is None:
        raise NotServed(qid)
    learner = row["learner"]
    answers = db.load_answers(row)
    finished = row["finished"] is not None
    given = answers.get(qid)
    notes = _notes(row, cfg, served)
    note, marks = notes.get((q.get("key"), q.get("seed")), (None, []))
    a = _attempt_rows(row).get(qid)
    tries = []
    if a:
        tries.append({"n": 1, "given": a["given"], "correct": bool(a["correct"]), "mistake": _cap(a["reason"]),
                      "ms": a["ms"], "at": a["at"]})
    for t in db.rows("SELECT * FROM tries WHERE session=? AND qid=? ORDER BY n, at", row["id"], qid):
        tries.append({"n": t["n"], "given": t["given"], "correct": bool(t["correct"]),
                      "mistake": _cap(t["reason"]) if t["reason"] != "cover_miss" else None,
                      "ms": t["ms"], "at": t["at"], "cover": t["reason"] == "cover_miss"})
    history = [{"at": r["at"], "correct": bool(r["correct"]), "given": r["given"], "mistake": _cap(r["reason"]),
                "ms": r["ms"], "session": r["session"], "difficulty": r["difficulty"]}
               for r in db.rows("SELECT * FROM attempts WHERE learner=? AND template=? AND repeat=0"
                                " ORDER BY id DESC LIMIT 20", learner, q["key"])] if "key" in q else []
    challenge = _challenge(row)
    out = {"question": public_q(row, cfg, q), "status": status_of(q, answers, cfg, finished, _voided(row, served)),
           "given": given if given != "_skip" else None, "ms": (cfg.get("ms") or {}).get(qid, 0),
           "marked": qid in _flags(row), "strikes": (cfg.get("strike") or {}).get(qid, []),
           "note": note or None, "marks": marks or [], "has_note": bool(note),
           "why": None if challenge else q.get("why"), "tries": tries, "type_history": history,
           "calc": (cfg.get("calc") or {}).get(qid, [])}
    if revealable(row, cfg, qid) or (q.get("kind") == "example"):
        ok = scoring.is_correct(q, given) if given not in (None, "", "_skip") else False
        out["feedback"] = {**_reveal(q, given, ok), "correct": ok}
        out["question"]["odds"] = q.get("odds")
    if (revealable(row, cfg, qid) and not challenge) or (challenge and _day_passed(row)):
        out["template"], out["seed"] = q.get("key"), q.get("seed")
    elif challenge:
        out["id_note"] = "Shown after today's challenge closes"
    return out


# ------------------------------------------------------------------ finish

def finish(row) -> dict:
    cfg = _cfg(row)
    learner = row["learner"]
    served = _served(row)
    answers = db.load_answers(row)
    if row["finished"] and row["result"]:
        return json.loads(row["result"])
    cfg.pop("pending", None)
    if cfg.get("paused_at"):
        cfg["paused_s"] = (cfg.get("paused_s") or 0) + (_now() - _at(cfg["paused_at"])).total_seconds()
        cfg["paused_at"] = None
    questions = _served_questions(served)
    # end mode files every answered question now, in order, with its time
    if cfg.get("feedback") == "end" and not row["contest"]:
        done = {r["qid"] for r in db.rows("SELECT qid FROM attempts WHERE session=?", row["id"])}
        for q in questions:
            given = answers.get(q["id"])
            if given in (None, "", "_skip") or q["id"] in done:
                continue
            meta = (cfg.get("end_meta") or {}).get(q["id"], {})
            try:
                progress.record(learner, row["id"], q, given, (cfg.get("ms") or {}).get(q["id"]),
                                conf=meta.get("conf"), hints=meta.get("hints", 0),
                                struck=(cfg.get("strike") or {}).get(q["id"]), cover=meta.get("cover", False),
                                calc=bool((cfg.get("calc") or {}).get(q["id"])),
                                placement=bool(cfg.get("probe")), revealed=True)
            except HTTPException:
                raise
    firsts = _attempt_rows(row)
    got = [firsts[q["id"]] for q in questions if q["id"] in firsts]
    names = progress.topics()
    per: dict[str, dict] = {}
    for a in got:
        d = per.setdefault(a["topic"], {"right": 0, "asked": 0})
        d["asked"] += 1
        d["right"] += a["correct"]
    topics_out = [
        {"topic": t, "name": names[t].name if t in names else t, "domain": names[t].domain if t in names else None,
         **v, "before": cfg.get("before", {}).get(t, 0.0),
         "after": progress.topic_mastery(learner, t)}
        for t, v in per.items()
    ]
    still = {(t["template"], t["label"]) for t in progress.open_traps(learner)}
    opened = []
    for t in db.rows("SELECT template, label, topic, id FROM traps WHERE learner=? AND opened>=?",
                     learner, row["started"]):
        if (t["template"], t["label"]) in still:
            opened.append({"topic": t["topic"], "label": t["label"], "id": t["id"], "template": t["template"]})
    closed = [{"topic": t["topic"], "label": t["label"], "id": t["id"]}
              for t in db.rows("SELECT label, topic, id FROM traps WHERE learner=? AND closed>=?",
                               learner, row["started"])]
    voided = _voided(row, served)
    finished_now = True
    statuses = {q["id"]: status_of(q, answers, cfg, finished_now, voided) for q in questions}
    counted = [a for a in got if a["qid"] not in voided]
    right = sum(a["correct"] for a in counted)
    ms_of = lambda q: (cfg.get("ms") or {}).get(q["id"]) or (firsts.get(q["id"]) or {"ms": None})["ms"] or 0
    flagged = _flags(row)
    notes = _notes(row, {**cfg, "clean": False}, served)
    by_tier: dict[str, dict] = {}
    by_type: dict[str, dict] = {}
    for q in questions:
        a = firsts.get(q["id"])
        if not a or q["id"] in voided:
            continue
        d = by_tier.setdefault(q["difficulty"], {"right": 0, "asked": 0, "ms": 0})
        d["right"] += a["correct"]
        d["asked"] += 1
        d["ms"] += ms_of(q)
        t = by_type.setdefault(q["key"], {"template": q["key"], "name": type_name(q["key"]), "right": 0,
                                          "asked": 0, "ms": 0, "twins": Counter()})
        t["right"] += a["correct"]
        t["asked"] += 1
        t["ms"] += ms_of(q)
        if q.get("twin"):
            t["twins"][q["twin"]["axis"]] += 1
    rows_out = []
    for q in questions:
        a = firsts.get(q["id"])
        meta = (cfg.get("end_meta") or {}).get(q["id"], {})
        rows_out.append({"id": q["id"], "n": q.get("n"), "topic": q["topic"], "skill": q.get("skill"),
                         "type_name": q.get("type_name"), "difficulty": q["difficulty"], "level": q.get("level"),
                         "status": statuses[q["id"]], "ms": ms_of(q), "budget_ms": q.get("budget_ms"),
                         "mistake": _cap(a["reason"]) if a and not a["correct"] else None,
                         "marked": q["id"] in flagged,
                         "has_note": bool(notes.get((q["key"], q["seed"]), (None,))[0]),
                         "repair": bool(q.get("repair")), "guess": bool(a and a["guess"]),
                         "conf": a["conf"] if a else meta.get("conf"), "helped": bool(a and a["hints"]),
                         "why": (q.get("why") or {}).get("kind") if isinstance(q.get("why"), dict) else None,
                         "final": bool(q.get("final")), "cb_id": q.get("cb_id"), "slot_of": q.get("slot_of"),
                         "odds": q.get("odds"), "zone": q.get("zone")})
    spent = [r["ms"] for r in rows_out if r["ms"]]
    budget_total = sum(r["budget_ms"] or 0 for r in rows_out if r["status"] not in ("unanswered", "skipped"))
    result = {
        "mode": row["kind"], "asked": len(counted), "right": right,
        "topics": topics_out, "opened": opened, "closed": closed,
        "ms": sum(ms_of(q) for q in questions),
        "mixed": sum(1 for s in statuses.values() if s == "mixed"),
        "skipped": sum(1 for s in statuses.values() if s == "skipped"),
        "unanswered": sum(1 for s in statuses.values() if s == "unanswered"),
        "voided": len([q for q in questions if q["id"] in voided]),
        "accuracy": round(right / len(counted), 3) if counted else None,
        "before_accuracy": cfg.get("before_accuracy"),
        "avg_ms": round(statistics.mean(spent)) if spent else None,
        "pace": {"budget_ms": budget_total, "spent_ms": sum(spent)},
        "by_difficulty": by_tier,
        "by_type": [{**{k: v for k, v in t.items() if k != "twins"}, "twins": dict(t["twins"])} for t in by_type.values()],
        "levels_seen": sorted({q.get("level") for q in questions if q.get("level")}),
        "measured_seen": sum(1 for q in questions if q.get("rough") is False),
        "guessed_right": sum(1 for a in counted if a["correct"] and (a["guess"] or a["conf"] == "guess")),
        "helped": sum(1 for a in counted if a["correct"] and a["hints"]),
        "questions": rows_out,
        "fix": len({a["template"] for a in counted if not a["correct"]}),
        "subject": cfg.get("subject", "math"),
    }
    try:
        result.update(_summary_extras(row, cfg, questions, firsts, statuses, voided))
    except Exception:                    # an extra never blocks a finish
        import logging
        logging.getLogger("satf").exception("summary extras failed for %s", row["id"][:8])
    if not row["finished"]:
        db.run("UPDATE sessions SET finished=?, result=?, cfg=? WHERE id=? AND finished IS NULL",
               progress.now(), json.dumps(result), json.dumps(cfg), row["id"])
    if row["contest"]:
        hook = deps.part("compete", "finish_contest")
        if hook:
            result.update({"contest": hook(db.one("SELECT * FROM sessions WHERE id=?", row["id"]))})
    return result


def _faster(counted: list) -> int | None:
    """How much faster the wrong answers came than the right ones (median ms)."""
    right = [a["ms"] for _, a in counted if a["correct"] and a["ms"]]
    wrong = [a["ms"] for _, a in counted if not a["correct"] and a["ms"]]
    if len(right) < 3 or len(wrong) < 3:
        return None
    gap = statistics.median(right) - statistics.median(wrong)
    return round(gap) if gap > 0 else None


def _next_set(cfg: dict, counted: list, sinks: set) -> dict | None:
    """The summary's primary pill: the next set built from this one, as U1's
    segments -- confident misses, then time sinks, then other misses, then
    slipped reviews, one fresh twin each."""
    groups = (("confident miss", "confident misses", lambda q, a: not a["correct"] and a["conf"] == "sure"),
              ("time sink", "time sinks", lambda q, a: q["id"] in sinks),
              ("other miss", "other misses", lambda q, a: not a["correct"]
               and (q.get("why") or {}).get("kind") not in ("due", "check", "marked")),
              ("slipped review", "slipped reviews", lambda q, a: not a["correct"]))
    segs, taken, parts = [], set(), []
    for one, many, test in groups:
        n = 0
        for q, a in counted:
            if q["key"] in taken or not test(q, a):
                continue
            taken.add(q["key"])
            n += 1
            segs.append({"template": q["key"], "tier": q["difficulty"], "fmt": q["type"], "why": one.capitalize()})
        if n:
            parts.append(f"{n} {one if n == 1 else many}")
    if not segs:
        return None
    segs = segs[:30]
    budgets = TIER_BUDGET.get(cfg.get("subject", "math"), TIER_BUDGET["math"])
    return {"title": "Fix " + " + ".join(parts), "count": len(segs),
            "minutes": round(sum(budgets.get(s["tier"], 95_000) for s in segs) / 60_000),
            "body": {"source": "result", "segments": segs, "subject": cfg.get("subject", "math")}}


def _moved(row, cfg: dict, counted: list, extras: dict) -> dict:
    """P10's What this set moved, P9's head line, P6's habits this set against
    last week, and P14's Finish this skill count."""
    from . import estimate, habits
    learner = row["learner"]
    out: dict = {}
    try:
        g = estimate.gains(learner, cfg.get("subject", "math"))
    except Exception:
        g = None
    gain_after = {x["topic"]: x["gain"] for x in g["skills"]} if g else {}
    before_gain = cfg.get("gain_before") or {}
    names = progress.topics(cfg.get("subject", "math"))
    out["moved"] = [{"topic": t, "name": names[t].name if t in names else t,
                     "rate_before": (cfg.get("before_rate") or {}).get(t), "rate_after": _first_try_rate(learner, [t]),
                     "gain_before": before_gain.get(t), "gain_after": gain_after.get(t)}
                    for t in dict.fromkeys(q["topic"] for q, _ in counted)]
    catalogue = [t for topic in cfg.get("topics") or () for t in practice.catalogue()["by_topic"].get(topic, ())]
    ready_now = _ready(learner, catalogue)
    newly = sorted(ready_now - set(cfg.get("ready_before") or ()))
    total_before, total_after = cfg.get("gain_total_before"), (g or {}).get("total")
    out["head"] = {"closed": db.one("SELECT COUNT(*) n FROM traps WHERE learner=? AND closed>=?",
                                    learner, row["started"])["n"],
                   "ready": len(newly), "ready_types": newly,
                   "held": (extras.get("retrieval") or {}).get("held", 0),
                   "points": (total_before - total_after) if total_before is not None and total_after is not None
                   else None}
    fam: dict[str, dict] = {}
    week_ago = (_at(row["started"]) - dt.timedelta(days=7)).isoformat()

    def tally(rows, key):
        for a in rows:
            chosen = a["norm"] if not a["correct"] else None
            for n in json.loads(a["offered"] or "[]"):
                f = (habits.family(n) or {}).get("id")
                if f:
                    d = fam.setdefault(f, {"id": f, "here": {"offered": 0, "dodged": 0}, "week": {"offered": 0, "dodged": 0}})
                    d[key]["offered"] += 1
                    d[key]["dodged"] += n != chosen
    tally([a for _, a in counted], "here")
    tally(db.rows(f"SELECT norm, correct, offered FROM attempts WHERE learner=? AND at>=? AND at<? AND {progress.COUNTED}",
                  learner, week_ago, row["started"]), "week")
    listed = {f["id"]: f for f in habits.families()}
    out["habits"] = sorted(({**d, "name": listed.get(k, {}).get("name", k)} for k, d in fam.items()
                            if d["here"]["offered"]), key=lambda d: -d["here"]["offered"])
    if cfg.get("source") == "finish" and cfg.get("topics"):
        out["finish"] = {"topic": cfg["topics"][0], "ready": len(ready_now), "was": len(cfg.get("ready_before") or ()),
                         "types": len(catalogue), "to_go": len(catalogue) - len(ready_now)}
    return out


def _summary_extras(row, cfg: dict, questions: list[dict], firsts: dict, statuses: dict, voided: set) -> dict:
    """The summary's blocks that read the whole set (P3, P5-P8, P11-P13, P16, P17, P19)."""
    learner = row["learner"]
    counted = [(q, firsts[q["id"]]) for q in questions if q["id"] in firsts and q["id"] not in voided]
    out: dict = {"calibration": progress.calibration(learner, row["id"])}
    causes: Counter = Counter()
    medians = progress._tier_medians(learner)
    for q, a in counted:
        if not a["correct"]:
            kind, _ = cause_kind(learner, dict(a), q, cfg, medians)
            causes[kind] += 1
    out["causes"] = dict(causes)
    offered = dodged = strikes = strike_wrong = struck_key = 0
    for q, a in counted:
        norms = json.loads(a["offered"] or "[]")
        offered += len(norms)
        chosen = a["norm"] if not a["correct"] else None
        dodged += sum(1 for n in norms if n != chosen)
        s = json.loads(a["struck"] or "[]") or []
        key = "ABCD".index(q["answer"]) if q["type"] == "mcq" else None
        strikes += len(s)
        strike_wrong += sum(1 for i in s if i != key)
        struck_key += int(key in s)
    out["dodged"] = {"offered": offered, "dodged": dodged}
    out["strikes"] = {"n": strikes, "on_wrong": strike_wrong, "struck_key": struck_key}
    reviews = [(q, a) for q, a in counted if (q.get("why") or {}).get("kind") in ("due", "check", "marked")]
    out["retrieval"] = {"reviews": len(reviews), "held": sum(a["correct"] for _, a in reviews),
                        "slipped": [q.get("type_name") for q, a in reviews if not a["correct"]]}
    finals = [(q, a) for q, a in counted if q.get("final")]
    out["final"] = {"n": len(finals), "right": sum(a["correct"] for _, a in finals),
                    "still_open": [q.get("type_name") for q, a in finals if not a["correct"]]} if finals else None
    if cfg.get("order") == "mixup":
        mix = []
        for t in dict.fromkeys(q["key"] for q, _ in counted):
            here = [a for q, a in counted if q["key"] == t]
            usual = db.one(f"SELECT COUNT(*) n, COALESCE(SUM(correct),0) r FROM attempts WHERE learner=? AND template=?"
                           f" AND COALESCE(session,'')!=? AND {progress.COUNTED}", learner, t, row["id"])
            mix.append({"template": t, "name": type_name(t), "right": sum(a["correct"] for a in here),
                        "asked": len(here), "usual": round(usual["r"] / usual["n"], 3) if usual["n"] else None})
        out["mixup"] = mix
    if cfg.get("probe"):
        probe: dict = {}
        for q, a in counted:
            p = probe.setdefault(q["topic"], {})
            cell = p.setdefault(q["difficulty"], {"right": 0, "asked": 0})
            cell["right"] += a["correct"]
            cell["asked"] += 1
        out["probe"] = probe
    with_calc = [a for _, a in counted if a["calc"]]
    without = [a for _, a in counted if not a["calc"]]
    out["calc"] = {"on": len(with_calc), "right_with": sum(a["correct"] for a in with_calc),
                   "without": len(without), "right_without": sum(a["correct"] for a in without)}
    covered = [(q, a) for q, a in counted if a["cover"]]
    out["covered"] = {"n": len(covered), "right": sum(a["correct"] for _, a in covered),
                      "matched_trap": sum(1 for _, a in covered if not a["correct"]),
                      "no_match": len(set(cfg.get("uncovered") or []))} if covered or cfg.get("uncovered") else None
    if cfg.get("official"):
        official = []
        for cbid in cfg["official"]:
            mine = [a for q, a in counted if q.get("cb_id") == cbid]
            official.append({"cb_id": cbid, "right": sum(a["correct"] for a in mine), "twins": len(mine)})
        out["official"] = official
    if cfg.get("zone") not in (None, "off"):
        odds = [q.get("odds") for q, _ in counted if q.get("odds") is not None]
        if odds:
            got = sum(a["correct"] for _, a in counted)
            out["expected"] = {"expected": round(sum(odds), 1), "got": got, "above": round(got - sum(odds), 1)}
    skipped_once = set(cfg.get("skipped_ever") or []) | {qid for qid in (cfg.get("skipped") or [])}
    if cfg.get("timed") and cfg.get("two_passes", True):
        p2 = [(q, a) for q, a in counted if q["id"] in skipped_once]
        p1 = [(q, a) for q, a in counted if q["id"] not in skipped_once]
        out["passes"] = {"one": {"answered": len(p1), "right": sum(a["correct"] for _, a in p1)},
                         "two": {"answered": len(p2), "right": sum(a["correct"] for _, a in p2)}}
    sinks = [q["id"] for q, a in counted if (a["ms"] or 0) > 2 * (q.get("budget_ms") or 95_000)]
    out["time_sinks"] = sinks
    out["time"] = {"over": sum(1 for q, a in counted if (a["ms"] or 0) > (q.get("budget_ms") or 95_000)),
                   "under": sum(1 for q, a in counted if a["ms"] and a["ms"] <= (q.get("budget_ms") or 95_000)),
                   "sink_ms": sum(a["ms"] or 0 for q, a in counted if q["id"] in sinks),
                   "sink_wrong": sum(1 for q, a in counted if q["id"] in sinks and not a["correct"]),
                   "wrong_faster_ms": _faster(counted)}
    done = cfg.get("words_done") or {}
    graded = [w for w in done.values() if not w.get("skipped")]
    out["words"] = {"reviewed": len(graded), "held": sum(1 for w in graded if w.get("correct"))} if done else None
    out["next_set"] = _next_set(cfg, counted, set(sinks))
    out.update(_moved(row, cfg, counted, out))
    if cfg.get("rematch_of"):
        parent = db.one("SELECT * FROM sessions WHERE id=?", cfg.get("rematch_parent") or cfg["rematch_of"])
        slots = []
        if parent:
            pq = {q["id"]: q for q in _served_questions(json.loads(parent["questions"] or "[]"))}
            pa = _attempt_rows(parent)
            pans = db.load_answers(parent)
            for q in questions:
                old_id = q.get("slot_of")
                if not old_id or old_id not in pq:
                    continue
                then = pa.get(old_id)
                now = firsts.get(q["id"])
                then_ok = bool(then and then["correct"]) if then else scoring.is_correct(pq[old_id], pans.get(old_id))
                now_ok = bool(now and now["correct"])
                same_trap = bool(then and now and not then["correct"] and not now["correct"]
                                 and then["norm"] and then["norm"] == now["norm"])
                change = ("same_trap" if same_trap else "fixed" if now_ok and not then_ok else
                          "slipped" if then_ok and not now_ok else "held" if now_ok else "still_missing")
                slots.append({"n": q.get("n"), "template": q["key"], "type_name": q.get("type_name"),
                              "then": {"status": "correct" if then_ok else "incorrect",
                                       "ms": then["ms"] if then else None,
                                       "mistake": _cap(then["reason"]) if then and not then_ok else None},
                              "now": {"status": statuses.get(q["id"]), "ms": now["ms"] if now else None,
                                      "mistake": _cap(now["reason"]) if now and not now_ok else None},
                              "change": change})
        out["slots"] = slots
    plan = deps.part("plan", "today_summary")
    if plan:
        try:
            out["plan"] = plan(learner)
        except Exception:
            out["plan"] = None
    words = deps.part("words", "today_summary")
    if words:
        try:
            due = (words(learner) or {}).get("due")
            out["words_due"] = due if isinstance(due, int) else None
        except Exception:
            out["words_due"] = None
    return out


# ------------------------------------------------------------------ Your sets (GET /api/drill)

def _row_of(r, cfg: dict, result: dict, answers: dict, served: list[dict]) -> dict:
    qs = _served_questions(served)
    return {"id": r["id"], "kind": r["kind"], "source": cfg.get("source"), "started": r["started"],
            "finished": r["finished"], "topics": cfg.get("topics", []), "total": cfg.get("total"),
            "answered": result.get("asked") if r["finished"] else
            sum(1 for q in qs if answers.get(q["id"]) not in (None, "", "_skip")),
            "right": result.get("right") if r["finished"] else None,
            "ms": result.get("ms") if r["finished"] else sum((cfg.get("ms") or {}).values()),
            "timed": bool(cfg.get("timed")), "seconds_left": None if r["finished"] else seconds_left(r, cfg),
            "paused": bool(cfg.get("paused_at")), "feedback": cfg.get("feedback", "instant"),
            "pool": cfg.get("pool", "new"), "share": cfg.get("share"), "subject": cfg.get("subject", "math"),
            "rematch_of": cfg.get("rematch_of"), "official": cfg.get("official")}


def listing(learner: str, topic: str | None = None, kind: str | None = None, misses: bool = False) -> dict:
    active, recent = [], []
    for r in db.rows("SELECT * FROM sessions WHERE learner=? AND kind IN ('drill','challenge')"
                     " ORDER BY started DESC LIMIT 600", learner):
        cfg = _cfg(r)
        if cfg.get("inline"):
            continue
        if not r["finished"]:
            r = lazy_finish(r)
            cfg = _cfg(r)
        answers = db.load_answers(r)
        served = _served(r)
        result = json.loads(r["result"] or "{}")
        if not r["finished"]:
            if cfg.get("source") == "quick":
                continue
            item = _row_of(r, cfg, result, answers, served)
            if item["answered"]:
                active.append(item)
            continue
        if not result.get("asked"):
            continue
        if topic and topic not in (cfg.get("topics") or []):
            continue
        if kind and r["kind"] != kind:
            continue
        if misses and result.get("right", 0) >= result.get("asked", 0):
            continue
        if len(recent) < 200:
            recent.append(_row_of(r, cfg, result, answers, served))
    shared = []
    for s in db.rows("SELECT * FROM sets WHERE owner=? AND revoked IS NULL ORDER BY created DESC LIMIT 100", learner):
        takers = db.rows("SELECT result FROM sessions WHERE shared_from=? AND finished IS NOT NULL AND learner!=?",
                         s["code"], learner)
        rights = [json.loads(t["result"] or "{}").get("right") for t in takers]
        rights = [x for x in rights if isinstance(x, int)]
        shared.append({"code": s["code"], "kind": s["kind"], "title": s["title"], "created": s["created"],
                       "session": s["session"], "taken": len(takers),
                       "avg": round(statistics.mean(rights), 1) if rights else None})
    official: dict[str, dict] = {}
    for r in db.rows("SELECT id, cfg, questions, finished FROM sessions WHERE learner=? AND kind='drill'"
                     " AND finished IS NOT NULL AND cfg LIKE '%\"official\": [%' ORDER BY finished", learner):
        cfg = _cfg(r)
        if not cfg.get("official"):
            continue
        firsts = _attempt_rows(r)
        for q in _served_questions(_served(r)):
            if not q.get("cb_id"):
                continue
            o = official.setdefault(q["cb_id"], {"cb_id": q["cb_id"], "template": q["key"], "twins": 0,
                                                 "right": 0, "last": None})
            a = firsts.get(q["id"])
            if a:
                o["twins"] += 1
                o["right"] += a["correct"]
                o["last"] = r["finished"]
    return {"active": active, "recent": recent, "shared": shared,
            "official": sorted(official.values(), key=lambda o: o["last"] or "", reverse=True)}
