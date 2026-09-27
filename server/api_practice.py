"""The map of the skills, the Practice builder's one read (/api/bank), and
practice sets answered one question at a time (/api/drill ...).

Every write goes through deps.writer_of (a sample learner is read-only, a
retired code is 401) and every body is a strict model, so an unknown field
or an out-of-range value is a 422 naming it before anything is touched.
"""

from __future__ import annotations

import datetime as dt
import functools
import json
import logging
import statistics
from collections import Counter, defaultdict
from typing import Literal

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field

from . import blueprint, db, deps, drill, practice, progress
from .api_me import per_session, profile
from .api_tests import DRILLS
from .deps import learner_of, mine, session_or_404, writer_of

log = logging.getLogger("satf")
router = APIRouter()

QID = Field(min_length=1, max_length=16)
MS = Field(default=None, ge=0, le=24 * 3600 * 1000)


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


@router.get("/api/map")
def get_map(x_learner: str | None = Header(default=None)) -> dict:
    """The 19 topics with mastery and open mistakes, and the coach's pick."""
    learner = learner_of(x_learner)
    board = progress.board(learner)
    return {"topics": list(board.values()),
            "coach": progress.coach(learner, count=per_session(profile(learner)))}


# ------------------------------------------------------------------ /api/bank

MID_TIER = ("medium", "easy", "hard")


def _mid(tiers: list[str]) -> str:
    return next(t for t in MID_TIER if t in tiers) if tiers else "medium"


@functools.lru_cache(maxsize=2)
def _catalogue(subject: str) -> dict:
    """The tree's fixed part, per process: 4 domains, 19 skills, 386 types."""
    kinds = blueprint.kinds()
    cat = practice.catalogue()
    official = Counter(e["template"] for e in drill._official_map().values())
    cb = Counter(x["topic"] for x in drill.cb_index().values() if x.get("topic"))
    has_desmos, has_steps = drill._has("desmos"), drill._has("steps")
    skills, types = {}, {}
    for slug, tp in cat["topics"].items():
        if deps.subject_of(slug) != subject:
            continue
        names = list(cat["by_topic"].get(slug, ()))
        labels: dict[str, list] = defaultdict(list)
        for t in names:
            e = kinds[t]
            tiers = [x for x in drill.TIERS if x in {d for d, _ in e["kinds"]}]
            labels[e["skill"]].append(t)
            types[t] = {"template": t, "name": drill.type_name(t), "about": drill._about(t),
                        "topic": slug, "domain": tp.domain, "skill": e["skill"],
                        "labels": sorted(e["labels"]), "tiers": tiers,
                        "formats": sorted({f for _, f in e["kinds"]}),
                        "axes": sorted(e.get("axes") or ()), "official": official.get(t, 0),
                        "desmos": t in has_desmos, "steps": t in has_steps,
                        "lookalikes": blueprint.lookalikes(t),
                        "weight": round(progress.BLUEPRINT.get(tp.domain, .15) / max(len(names), 1), 5)}
        skills[slug] = {"slug": slug, "name": tp.name, "short": tp.name.split(":")[0],
                        "domain": tp.domain, "types": names, "cb_count": cb.get(slug, 0),
                        "labels": [{"label": k, "templates": v} for k, v in labels.items()]}
    domains = [{"name": d, "weight": progress.BLUEPRINT.get(d, 0),
                "skills": [s for s, x in skills.items() if x["domain"] == d]} for d in progress.DOMAINS]
    return {"skills": skills, "types": types, "domains": [d for d in domains if d["skills"]]}


def _rw_bank(learner: str, tz: int) -> dict:
    """P15: Reading & Writing before its bank -- College Board's R&W skills
    with their counts, the Log it form's skills, and Words' drills (S9)."""
    by_domain: dict[str, dict] = defaultdict(dict)
    for x in drill.cb_index().values():
        if x.get("subject") != "rw":
            continue
        key = x["skill"].lower()
        row = by_domain[x.get("domain") or "Reading and Writing"].setdefault(
            key, {"name": x["skill"], "cb_count": 0,
                  # R57: Words in Context and Transitions are served now, by Words (S9)
                  "available": key in ("words in context", "transitions"), "via": None})
        row["cb_count"] += 1
        if row["available"]:
            row["via"] = "words"
    words = None
    summary = deps.part("words", "today_summary")
    if summary:
        try:
            words = summary(learner, tz)
        except Exception:
            log.exception("words.today_summary failed for the R&W panel")
    return {"subject": "rw", "bank": False,
            "totals": {"domains": len(by_domain), "skills": sum(len(v) for v in by_domain.values()),
                       "types": 0, "measured": 0},
            "domains": [{"name": d, "skills": sorted(v.values(), key=lambda s: s["name"])}
                        for d, v in by_domain.items()],
            "words": words,
            "note": "R&W practice questions come with the R&W bank. What you log here is waiting for it."}


def _habits(learner: str, rows: list, traps: list) -> tuple[list[dict], dict | None]:
    """P6: per U6 family, caught (chosen), dodged (on offer, not chosen),
    open traps and the skills it caught you in; and the top habit when one
    family is 25% or more of the last 20 misses."""
    from . import habits
    fam_of: dict = {}

    def fam(norm):
        if norm not in fam_of:
            f = habits.family(norm) if norm else None
            fam_of[norm] = f["id"] if f else None
        return fam_of[norm]
    out: dict[str, dict] = {}

    def slot(fid):
        return out.setdefault(fid, {"id": fid, "caught": 0, "dodged": 0, "offered": 0, "open": 0,
                                    "skills": [], "last": None})
    for r in rows:
        chosen = r["norm"] if not r["correct"] else None
        for norm in json.loads(r["offered"] or "[]"):
            fid = fam(norm)
            if fid:
                s = slot(fid)
                s["offered"] += 1
                s["dodged"] += norm != chosen
        fid = fam(chosen) if chosen else None
        if fid:
            s = slot(fid)
            s["caught"] += 1
            s["last"] = r["at"]
            if r["topic"] not in s["skills"]:
                s["skills"].append(r["topic"])
    for t in traps:
        fid = fam(t.get("norm"))
        if fid:
            slot(fid)["open"] += 1
    names = {f["id"]: f for f in habits.families()}
    listed = [{**v, "name": names.get(k, {}).get("name", k), "tell": names.get(k, {}).get("tell")}
              for k, v in out.items()]
    listed.sort(key=lambda h: (-h["caught"], h["id"]))
    misses = [fam(r["norm"]) for r in reversed(rows) if not r["correct"] and r["norm"]][:20]
    top = None
    if len(misses) >= 4:
        fid, n = Counter(m for m in misses if m).most_common(1)[0] if any(misses) else (None, 0)
        if fid and n / len(misses) >= .25:
            top = {"id": fid, "name": names.get(fid, {}).get("name", fid), "share": round(n / len(misses), 2)}
    return listed, top


def bank(learner: str, subject: str = "math", tz: int = 0) -> dict:
    """The builder's one read: the catalogue with this learner's record on
    every skill and type, the coach, the pools' counts and the extras."""
    if subject == "rw":
        return _rw_bank(learner, tz)
    from . import estimate, ratings
    base = _catalogue(subject)
    rows = [r for r in db.rows(
        "SELECT template, topic, seed, difficulty, fmt, correct, guess, hints, conf, ms, sms, calc, cover,"
        " repeat, disputed, void, norm, offered, at FROM attempts WHERE learner=? ORDER BY id", learner)
        if r["template"] in base["types"]]
    counted = [r for r in rows if not r["repeat"] and not r["disputed"] and r["void"] is None]
    per_t: dict[str, list] = defaultdict(list)
    for r in counted:
        per_t[r["template"]].append(r)
    pairs: dict[tuple, list] = defaultdict(list)
    for r in rows:
        pairs[(r["template"], r["seed"])].append(r["correct"])
    seen = Counter(t for t, _ in pairs)
    missed = Counter(t for (t, _), marks in pairs.items() if not marks[0] and not any(marks[1:]))
    traps = progress.open_traps(learner)
    traps_t: dict[str, list] = defaultdict(list)
    for t in traps:
        traps_t[t["template"]].append({"id": t["id"], "label": t["label"], "hits": t["hits"], "owed": t["owed"],
                                       "norm": t["norm"], "source": t.get("source")})
    flagged = Counter(r["template"] for r in db.rows("SELECT template FROM flags WHERE learner=?", learner))
    saved = Counter(r["template"] for r in db.rows("SELECT template FROM saved WHERE learner=?", learner))
    rules = {}
    try:
        from . import prefs
        rules_on = prefs.get(learner, tz).get("type_rules", True)
    except Exception:
        rules_on = True
    if rules_on:
        rules = {r["template"]: {"note": r["note"], "at": r["at"]} for r in db.rows(
            "SELECT template, note, at FROM notes WHERE learner=? AND seed=-1 AND note!=''", learner)}
    clean = progress._clean_rights(learner, subject)
    due = {f["template"]: f for f in progress.warmup_candidates(learner, tz, subject)["fading"]}
    items = {(r["template"], r["tier"]): (r["rating"], r["n"])
             for r in db.rows("SELECT template, tier, rating, n FROM item_ratings")}
    skill_r = {r["topic"]: r for r in db.rows("SELECT topic, rating, n, seed FROM skill_ratings WHERE learner=?",
                                              learner)}
    seed_rating = ratings._seed_rating(learner)[0]
    crowd = drill.levels()
    board = progress.board(learner, subject)
    gains = estimate.gains(learner, subject)
    gain_of = {g["topic"]: g for g in (gains or {}).get("skills", ())}
    gain_dom = {g["domain"]: g for g in (gains or {}).get("by_domain", ())}
    today = progress._local_today(learner, tz)

    types_out: dict[str, dict] = {}
    for t, fixed in base["types"].items():
        mine_rows = per_t.get(t, [])
        tiers = fixed["tiers"]
        mid = _mid(tiers)
        rating = ratings.expected
        levels = {}
        for tier in tiers:
            r, n = items.get((t, tier), (ratings.TIER_PRIOR[tier], 0))
            levels[tier] = {"level": ratings.level_of(r), "rating": round(r), "n": n, "rough": n < ratings.MEASURED}
        sr = skill_r.get(fixed["topic"])
        skill_rating = sr["rating"] if sr else seed_rating
        odds = {tier: round(rating(items.get((t, tier), (ratings.TIER_PRIOR[tier], 0))[0], skill_rating), 3)
                for tier in tiers}
        firsts = [r["correct"] for r in mine_rows]
        cleans = [r for r in mine_rows if r["correct"] and not r["guess"] and not r["hints"] and r["conf"] != "unsure"]
        spent_right = [r["ms"] if r["ms"] is not None else r["sms"] for r in cleans]
        spent_right = [x for x in spent_right if x]
        budget = {tier: drill.budget_ms(t, tier) for tier in tiers}
        last2 = [r for r in cleans if (r["ms"] or r["sms"])][-2:]
        fluent = len(last2) == 2 and all((r["ms"] or r["sms"]) <= budget.get(r["difficulty"], budget[mid])
                                         for r in last2)
        median_right = int(statistics.median(spent_right)) if spent_right else None
        slow_right = (len(firsts) >= 3 and sum(firsts) / len(firsts) >= .8 and median_right is not None
                      and median_right > budget[mid])
        stamps = clean.get(t, [])
        k = len(stamps)
        next_return = ((progress._local_day(stamps[-1], tz) + dt.timedelta(days=progress.interval_for(k))).isoformat()
                       if stamps else None)
        open_here = traps_t.get(t, [])
        state = ("open" if open_here else "ready" if sum(firsts) >= 2 else "met" if mine_rows else "unmet")
        crowd_mid = crowd.get((t, mid), {}).get("crowd")
        types_out[t] = {
            **{k2: v for k2, v in fixed.items() if k2 != "weight"}, "weight": fixed["weight"],
            "level": levels[mid]["level"] if tiers else None, "rough": levels[mid]["rough"] if tiers else True,
            "rating": levels[mid]["rating"] if tiers else None, "measured_n": levels[mid]["n"] if tiers else 0,
            "levels": levels, "level_range": [min(v["level"] for v in levels.values()),
                                              max(v["level"] for v in levels.values())] if levels else None,
            "odds": odds.get(mid), "odds_by_tier": odds, "crowd": crowd_mid,
            "answered": len(mine_rows), "right": sum(firsts), "last": mine_rows[-1]["at"] if mine_rows else None,
            "trend": firsts[-10:],
            "traps": open_here, "marked": flagged.get(t, 0), "saved": saved.get(t, 0),
            "seen": seen.get(t, 0), "missed": missed.get(t, 0),
            "due": t in due, "k": k, "next_return": next_return, "state": state,
            "budget_ms": budget.get(mid), "budgets": budget, "median_ms": median_right,
            "best_ms": min(spent_right) if spent_right else None, "fluent": fluent, "slow_right": slow_right,
            "type_note": (rules.get(t) or {}).get("note"), "type_note_at": (rules.get(t) or {}).get("at")}

    skills_out = {}
    for slug, fixed in base["skills"].items():
        b = board.get(slug, {})
        ts = [types_out[t] for t in fixed["types"]]
        mine_rows = [r for t in fixed["types"] for r in per_t.get(t, [])]
        by_tier = {tier: [sum(r["correct"] for r in mine_rows if r["difficulty"] == tier),
                          sum(1 for r in mine_rows if r["difficulty"] == tier)] for tier in drill.TIERS}
        spent = [r["ms"] if r["ms"] is not None else r["sms"] for r in mine_rows]
        spent = [x for x in spent if x]
        sure = [r for r in mine_rows if r["conf"] == "sure"]
        with_calc = [r for r in mine_rows if r["calc"]]
        without = [r for r in mine_rows if not r["calc"]]
        covered = [r for r in mine_rows if r["cover"]]
        rated = [(c["crowd"]["rate"], c["crowd"]["n"]) for t in fixed["types"]
                 for tier in types_out[t]["tiers"] if (c := crowd.get((t, tier), {})).get("crowd")]
        g = gain_of.get(slug) or {}
        sr = skill_r.get(slug)
        skills_out[slug] = {
            **{k2: v for k2, v in fixed.items() if k2 != "types"},
            "mastery": b.get("mastery", 0.0), "answered": b.get("answered", 0), "accuracy": b.get("accuracy"),
            "right": sum(r["correct"] for r in mine_rows), "last": b.get("last"), "fading": b.get("fading", False),
            "by_tier": by_tier, "avg_ms": round(statistics.mean(spent)) if spent else None,
            "crowd_rate": round(sum(r * n for r, n in rated) / sum(n for _, n in rated), 3) if rated else None,
            "traps": [{"template": t["template"], **x} for t in ts for x in t["traps"]],
            "marked": sum(t["marked"] for t in ts), "saved": sum(t["saved"] for t in ts),
            "seen": sum(t["seen"] for t in ts), "missed": sum(t["missed"] for t in ts),
            "gain": g.get("gain"), "per_test": g.get("per_test"), "to_strong": g.get("to_strong"),
            "minutes": g.get("minutes"), "gain_accuracy": g.get("accuracy"),
            "fluent_n": sum(t["fluent"] for t in ts), "due_n": sum(t["due"] for t in ts),
            "ready_n": sum(t["state"] == "ready" for t in ts), "met_n": sum(t["state"] != "unmet" for t in ts),
            "open_n": sum(t["state"] == "open" for t in ts), "types_n": len(ts),
            "held_after": max((t["k"] for t in ts), default=0) >= 3,
            "sure_rate": {"n": len(sure), "right": sum(r["correct"] for r in sure),
                          "rate": round(sum(r["correct"] for r in sure) / len(sure), 3) if sure else None},
            "calc_split": ({"with": [sum(r["correct"] for r in with_calc), len(with_calc)],
                            "without": [sum(r["correct"] for r in without), len(without)]}
                           if len(with_calc) >= 5 and len(without) >= 5 else None),
            "solve_first": (round(sum(r["correct"] for r in covered) / len(covered), 3)
                            if len(covered) >= 5 else None),
            "rating": round(sr["rating"]) if sr else round(seed_rating), "placed": bool(
                sr and (sr["n"] >= ratings.PLACED or sr["seed"] == "probe")),
            "to_place": max(0, ratings.PLACED - (sr["n"] if sr else 0)),
            "types": ts}

    domains_out = []
    for d in base["domains"]:
        sk = [skills_out[s] for s in d["skills"]]
        domains_out.append({
            "name": d["name"], "weight": d["weight"],
            "mastery": round(statistics.mean(s["mastery"] for s in sk), 3) if sk else 0.0,
            "answered": sum(s["answered"] for s in sk), "right": sum(s["right"] for s in sk),
            "traps": sum(len(s["traps"]) for s in sk), "gain": (gain_dom.get(d["name"]) or {}).get("gain"),
            "due_n": sum(s["due_n"] for s in sk), "ready_n": sum(s["ready_n"] for s in sk),
            "types_n": sum(s["types_n"] for s in sk), "skills": sk})
    habit_rows, top = _habits(learner, counted, traps)
    counts = drill.pool_counts(learner)
    counts.update({"traps": counts["mistakes"], "due": counts["review"]})
    return {
        "subject": subject, "bank": True,
        "totals": {"domains": len(domains_out), "skills": len(skills_out), "types": len(types_out),
                   "measured": sum(1 for t in types_out.values() if any(not v["rough"] for v in t["levels"].values())),
                   "answered": len(counted)},
        "domains": domains_out,
        "coach": progress.coach(learner, count=per_session(profile(learner)), subject=subject),
        "counts": counts, "forecast": progress.due_forecast(learner, tz, 14),
        "route": estimate.route(learner, subject),
        "gains": None if not gains else {"total": gains.get("total"), "top3": gains.get("top3"),
                                         "answers": gains.get("answers")},
        "habits": habit_rows, "top_habit": top,
        "desmos_way": drill.desmos_on(), "today": today.isoformat()}


@router.get("/api/bank")
def get_bank(subject: str = Query(default="math", max_length=8), x_learner: str | None = Header(default=None),
             tz: int = Depends(deps.tz_of)) -> dict:
    """GET /api/bank?subject=math: the builder's tree, counts and coach."""
    return bank(learner_of(x_learner), deps.subject_param(subject), tz)


# ------------------------------------------------------------------ sets

def drill_row(sid: str, learner: str):
    """This learner's practice set or challenge sitting. A test is not one."""
    row = session_or_404(sid)
    if row["kind"] not in DRILLS:
        raise HTTPException(404, "no such set")
    return mine(row, learner)


def _live(sid: str, x_learner: str | None):
    """A set to write to: this learner's, not finished."""
    row = drill_row(sid, writer_of(x_learner))
    if row["finished"]:
        raise HTTPException(409, "this set is finished")
    return row


def _run(fn, *args, **kw):
    """drill's own refusals, as HTTP."""
    try:
        return fn(*args, **kw)
    except drill.NotServed:
        raise HTTPException(400, "that question is not in this set")
    except drill.Paused:
        raise HTTPException(409, {"reason": "paused"})
    except drill.Closed as e:
        raise HTTPException(409, str(e))


@router.post("/api/drill")
def new_drill(body: dict, x_learner: str | None = Header(default=None)) -> dict:
    """§2.6's body, validated in drill.resolve; the first question comes back."""
    learner = writer_of(x_learner)
    sid = drill.create(learner, body)
    first = _run(drill.next_question, session_or_404(sid))
    log.info("drill %s started for %s", sid[:8], learner[:12])
    return {**drill.state(session_or_404(sid)), **first}


@router.post("/api/drill/preview")
def drill_preview(body: dict, x_learner: str | None = Header(default=None)) -> dict:
    """The same body, nothing created: counts, minutes and the reason."""
    return drill.preview(learner_of(x_learner), body)


@router.get("/api/drill")
def your_sets(topic: str | None = Query(default=None, max_length=64),
              kind: Literal["drill", "challenge"] | None = None, misses: bool = False,
              x_learner: str | None = Header(default=None)) -> dict:
    """Your sets: active, recent (200), shared, and official questions you brought."""
    return drill.listing(learner_of(x_learner), topic, kind, misses)


@router.get("/api/history")
def history_without_inline(x_learner: str | None = Header(default=None)) -> dict:
    """R24's list rule, registered before the legacy history route."""
    learner = learner_of(x_learner)
    out = []
    for row in db.rows("SELECT id,kind,mock_id,started,finished,result,cfg FROM sessions"
                       " WHERE learner=? AND finished IS NOT NULL ORDER BY finished DESC LIMIT 300", learner):
        cfg = json.loads(row["cfg"] or "{}")
        result = json.loads(row["result"] or "{}")
        if cfg.get("inline") or result.get("asked", 0) == 0:
            continue
        out.append({"id": row["id"], "kind": row["kind"], "started": row["started"],
                    "finished": row["finished"], "right": result.get("right"),
                    "asked": result.get("asked"), "estimate": result.get("estimate"),
                    "topics": [t["topic"] for t in result.get("topics", ())] or cfg.get("topics", []),
                    "label": "Quick questions" if cfg.get("source") == "quick" else None})
        if len(out) >= 200:
            break
    return {"sessions": out}


@router.get("/api/drill/{sid}")
def get_drill(sid: str, x_learner: str | None = Header(default=None)) -> dict:
    return drill.state(drill_row(sid, learner_of(x_learner)))


class NextIn(Strict):
    skip: bool = False
    ms: int | None = MS


@router.post("/api/drill/{sid}/next")
def drill_next(sid: str, body: NextIn | None = None, x_learner: str | None = Header(default=None)) -> dict:
    """The next question (or the next served one); {skip:true} sets the
    current one aside. A contest skip forfeits it (Compete §8); the challenge
    has no skip."""
    row = _live(sid, x_learner)
    body = body or NextIn()
    if body.skip and row["contest"]:
        cfg, served = json.loads(row["cfg"] or "{}"), json.loads(row["questions"] or "[]")
        cur = drill._current(row, cfg, served, db.load_answers(row))
        if cur is None:
            raise HTTPException(409, {"reason": "nothing to skip"})
        return _run(drill.contest_skip, row, cur["id"])
    if body.skip and row["kind"] == "challenge":
        raise HTTPException(409, {"reason": "no skip in the challenge"})
    return _run(drill.next_question, row, body.skip, body.ms)


class AnswerIn(Strict):
    question_id: str = QID
    answer: int | str | None = None
    ms: int | None = MS
    conf: Literal["sure", "unsure", "guess", "auto"] | None = None
    guess: bool = False
    own: str | None = Field(default=None, max_length=40)
    hints: int = Field(default=0, ge=0, le=5)
    keep_marked: bool = False


@router.post("/api/drill/{sid}/answer")
def drill_answer(sid: str, body: AnswerIn, x_learner: str | None = Header(default=None)) -> dict:
    """One answer: instant, retry or end mode (cfg.feedback). `own` is P5's
    typed answer with the choices covered; `conf` P7's split Check."""
    row = _live(sid, x_learner)
    if body.own is None and (body.answer is None or body.answer == ""):
        raise HTTPException(400, "no answer")
    if isinstance(body.answer, str) and len(body.answer) > 40:
        raise HTTPException(422, {"field": "answer", "reason": "at most 40 characters"})
    if isinstance(body.answer, int) and not 0 <= body.answer <= 3:
        raise HTTPException(422, {"field": "answer", "reason": "a choice is 0–3"})
    return _run(drill.answer, row, body.question_id, body.answer, body.ms, conf=body.conf, guess=body.guess,
                own=body.own, hints=body.hints, keep_marked=body.keep_marked)


class TimeIn(Strict):
    question_id: str = QID
    ms: int = Field(ge=0, le=24 * 3600 * 1000)


@router.post("/api/drill/{sid}/time")
def drill_time(sid: str, body: TimeIn, x_learner: str | None = Header(default=None)) -> dict:
    """Time on a question (capped per call) and the resume position; it
    also commits a held next-question preview (P23)."""
    return _run(drill.time_on, _live(sid, x_learner), body.question_id, body.ms)


@router.get("/api/drill/{sid}/q/{qid}")
def drill_question(sid: str, qid: str, x_learner: str | None = Header(default=None)) -> dict:
    """One served question: status, given, tries, notes, history, and the
    feedback only once it can be revealed."""
    return _run(drill.detail, drill_row(sid, learner_of(x_learner)), qid)


class StrikeIn(Strict):
    question_id: str = QID
    choice: int = Field(ge=0, le=3)
    on: bool = True


@router.post("/api/drill/{sid}/strike")
def drill_strike(sid: str, body: StrikeIn, x_learner: str | None = Header(default=None)) -> dict:
    return _run(drill.strike, _live(sid, x_learner), body.question_id, body.choice, body.on)


class MoreIn(Strict):
    question_id: str = QID
    step: int = Field(default=0, ge=-1, le=1)
    axis: Literal["same", "easier", "harder", "grid", "ask"] | None = None
    want: str | None = Field(default=None, max_length=300)
    n: int = Field(default=1, ge=1, le=3)
    ladder: bool = False


@router.post("/api/drill/{sid}/more")
def drill_more(sid: str, body: MoreIn, x_learner: str | None = Header(default=None)) -> dict:
    """Another like this on any axis (P18), Practise this trap (P1, want),
    the Learn ladder (P2) or a voided question's replacement (P25)."""
    return _run(drill.more, _live(sid, x_learner), body.question_id, body.step, body.axis, body.want,
                body.n, body.ladder)


@router.post("/api/drill/{sid}/pause")
def drill_pause(sid: str, x_learner: str | None = Header(default=None)) -> dict:
    return _run(drill.set_paused, _live(sid, x_learner), True)


@router.post("/api/drill/{sid}/resume")
def drill_resume(sid: str, x_learner: str | None = Header(default=None)) -> dict:
    return _run(drill.set_paused, _live(sid, x_learner), False)


class QuestionIn(Strict):
    question_id: str = QID


@router.post("/api/drill/{sid}/reveal")
def drill_reveal(sid: str, body: QuestionIn, x_learner: str | None = Header(default=None)) -> dict:
    """Retry mode's Show answer."""
    return _run(drill.reveal, _live(sid, x_learner), body.question_id)


@router.post("/api/drill/{sid}/hint")
def drill_hint(sid: str, body: QuestionIn, x_learner: str | None = Header(default=None)) -> dict:
    """P2's next rung for this question; never its key."""
    return _run(drill.hint, _live(sid, x_learner), body.question_id)


class WhyIn(Strict):
    question_id: str = QID
    kind: Literal["trap", "slip", "misread", "clock", "entry", "gap"]


@router.post("/api/drill/{sid}/why")
def drill_why(sid: str, body: WhyIn, x_learner: str | None = Header(default=None)) -> dict:
    """P8: the student's own cause of a miss (also after Finish)."""
    return _run(drill.why, drill_row(sid, writer_of(x_learner)), body.question_id, body.kind)


class CalcIn(Strict):
    question_id: str = QID
    exprs: list[str] = Field(default_factory=list, max_length=30)


@router.post("/api/drill/{sid}/calc")
def drill_calc(sid: str, body: CalcIn, x_learner: str | None = Header(default=None)) -> dict:
    """P3: what the student typed in Desmos while this question was open."""
    return _run(drill.calc, _live(sid, x_learner), body.question_id, body.exprs)


class WordIn(Strict):
    token: str = Field(min_length=1, max_length=400)
    answer: int | str | None = None
    ms: int | None = MS


@router.post("/api/drill/{sid}/word")
def drill_word(sid: str, body: WordIn, x_learner: str | None = Header(default=None)) -> dict:
    """P12: a due SAT word card, graded by Words (S9)."""
    if isinstance(body.answer, str) and len(body.answer) > 200:
        raise HTTPException(422, {"field": "answer", "reason": "at most 200 characters"})
    return _run(drill.word, _live(sid, x_learner), body.token, body.answer, body.ms)


@router.post("/api/drill/{sid}/final")
def drill_final(sid: str, x_learner: str | None = Header(default=None)) -> dict:
    """P12: start the final round (the first-try misses, new numbers)."""
    return _run(drill.start_final, _live(sid, x_learner))


class RematchDueIn(Strict):
    days: int = Field(default=3, ge=1, le=30)


@router.post("/api/drill/{sid}/rematch-due")
def drill_rematch_due(sid: str, body: RematchDueIn | None = None,
                      x_learner: str | None = Header(default=None)) -> dict:
    """P19's Rematch in 3 days (U1's queue reads cfg.rematch_due)."""
    return drill.rematch_due(drill_row(sid, writer_of(x_learner)), (body or RematchDueIn()).days)


@router.post("/api/drill/{sid}/finish")
def drill_finish(sid: str, x_learner: str | None = Header(default=None)) -> dict:
    learner = writer_of(x_learner)
    row = drill_row(sid, learner)
    cfg = json.loads(row["cfg"] or "{}")
    if cfg.get("source") == "quick" and not db.load_answers(row):
        db.run("DELETE FROM sessions WHERE id=? AND learner=?", sid, learner)
        return {"deleted": True}
    out = drill.finish(row)
    out["next"] = progress.coach(learner, count=per_session(profile(learner)))
    return out
