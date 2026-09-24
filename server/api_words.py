"""HTTP surface for SAT Reading & Writing Words.

All generated keys stay in a Words session until the learner answers. A sheet
sample is signed rather than making a session just to browse a word.
"""

from __future__ import annotations

import base64
import csv
import datetime as dt
import hashlib
import hmac
import io
import json
import random
import re
import secrets
import statistics
import unicodedata
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, Depends, Header, HTTPException, Response
from fastapi.responses import StreamingResponse

from . import db, words
from .deps import learner_of, part, tz_of

router = APIRouter()


def _learner(header: str | None) -> str:
    return learner_of(header)


def _row(sid: str, learner: str):
    row = db.one("SELECT * FROM sessions WHERE id=?", sid)
    if not row or row["kind"] != "words":
        raise HTTPException(404, "no such Words run")
    if row["learner"] != learner:
        raise HTTPException(403, "that Words run belongs to someone else")
    return row


def _current(row) -> tuple[list[dict], dict, dict]:
    return json.loads(row["questions"] or "[]"), json.loads(row["answers"] or "{}"), json.loads(row["cfg"] or "{}")


def _next(questions: list[dict], answers: dict) -> dict | None:
    return next((words.public_item(q, q["item_id"]) for q in questions if q["item_id"] not in answers), None)


def _run_payload(row, *, include_items: bool = False) -> dict:
    questions, answers, cfg = _current(row)
    public = [words.public_item(q, q["item_id"]) for q in questions]
    out = {"id": row["id"], "session": row["id"], "mode": cfg.get("mode"),
           "deck": cfg.get("deck"), "cfg": cfg, "total": len(questions),
           "answered": len(answers), "next": _next(questions, answers),
           "finished": bool(row["finished"]), "timer_total": cfg.get("timer_total")}
    if include_items:
        out["items"] = public
    if row["finished"]:
        out["summary"] = json.loads(row["result"] or "{}")
    return out


def _make_item(learner: str, slug: str, kind: str, seed: int,
               seen: set[str] | None = None, want_trap: str | None = None,
               strict_trap: bool = False) -> dict:
    w = words.entry(slug, learner)
    if not w:
        raise HTTPException(404, "unknown word")
    if kind == "order":
        try:
            return words.order_item(seed, w.get("class"))
        except ValueError:
            return words.order_item(seed)
    if kind in {"decode", "rootshare"}:
        roots = words.content()["index"]["words"].get(slug, {}).get("roots", [])
        for root in [*roots, None]:
            try:
                return words.root_item(seed, kind, root)
            except ValueError:
                continue
        raise HTTPException(409, "no root family can supply this item")
    if kind in {"incontext", "nearly", "transition", "precise"}:
        for offset in range(30):
            template = words.choose_template(slug, learner=learner, seed=seed + offset, seen=seen)
            if template is None:
                break
            try:
                q = words.item(template, seed + offset, slug, want_trap)
                if kind == "transition" or q["kind"] == kind or kind == "precise":
                    if (strict_trap and want_trap and want_trap not in q.get("traps", [])
                            and want_trap not in q.get("option_logics", [])):
                        continue
                    if kind == "precise":
                        q["kind"] = "precise"
                    return q
            except ValueError:
                continue
        raise HTTPException(409, "no reviewed frame is available for this word")
    if kind in {"meaning2word", "word2meaning", "cloze", "typed"}:
        try:
            q = words.quiz_item(slug, kind, random.Random(seed), learner)
        except ValueError as exc:
            raise HTTPException(409, str(exc)) from exc
        q["seed"] = seed
        return q
    if kind in {"card", "fix"}:
        state = words.state(learner, slug)
        sentence = words.new_sentence(learner, slug)
        q = {"kind": kind, "word": slug, "seed": seed, "stem": "Do you know this word?",
             "text": w["word"], "choices": [], "back": {"meaning": w["meaning"],
             "short": w["short"], "examples": w.get("examples", []),
             "sentence": sentence, "hook": state.get("hook")}}
        if kind == "fix":
            picks = db.rows("SELECT given,COUNT(*) n FROM word_reviews WHERE learner=? AND word=?"
                            " AND correct=0 AND given IS NOT NULL GROUP BY given ORDER BY n DESC LIMIT 3",
                            learner, slug)
            q["picks"] = [dict(r) for r in picks]
            q["back"]["picks"] = q["picks"]
        return q
    if kind == "learn":
        return {"kind": kind, "word": slug, "seed": seed, "stem": "Learn this word",
                "text": w["word"], "choices": [], "back": {"meaning": w["meaning"],
                "short": w["short"], "examples": w.get("examples", [])}}
    raise HTTPException(422, "unknown Words item format")


def _card_kind(learner: str, slug: str) -> str:
    s = words.state(learner, slug)
    if words._flags(learner, slug, s, words.local_day())["stubborn"] and s["due"] and s["due"] <= words.local_day().isoformat():
        return "fix"
    if int(s["box"] or 0) >= 3 or int(s.get("placed") or 0) == 2:
        return "transition" if words.entry(slug, learner)["collection"] == "transitions" else "incontext"
    return "card"


def _choose(learner: str, slugs: list[str], mode: str, formats: list[str],
            seed: int, want_trap: str | None = None, commit: bool = False) -> list[dict]:
    questions: list[dict] = []
    seen: set[str] = set()
    rng = random.Random(seed)
    adaptive = words.open_traps(learner)
    for i, slug in enumerate(slugs):
        w = words.entry(slug, learner)
        if not w:
            continue
        if mode in {"cards", "mix"}:
            kind = _card_kind(learner, slug)
            if mode == "mix" and not words.state(learner, slug)["reps"]:
                kind = "learn"
        elif mode == "sprint":
            kind = "meaning2word"
        elif mode == "check":
            kind = "precise" if i >= 10 else ("transition" if w["collection"] == "transitions" else "incontext")
        elif mode in {"quiz", "print"}:
            options = [f for f in formats if f in {"meaning2word", "word2meaning", "cloze", "typed",
                                                  "incontext", "nearly", "transition", "precise",
                                                  "order", "decode", "rootshare"}]
            if not options:
                raise HTTPException(422, "choose a question format")
            kind = options[i % len(options)]
            if w["collection"] == "transitions" and kind in {"incontext", "nearly", "precise"}:
                kind = "transition"
            if w["collection"] != "transitions" and kind == "transition":
                kind = "incontext"
        else:
            kind = "card"
        wanted = want_trap or (adaptive[0] if adaptive and i % 2 == 0 else None)
        q = _make_item(learner, slug, kind, rng.randrange(2**31), seen, wanted,
                       strict_trap=bool(want_trap))
        if commit and q["kind"] in {"card", "fix"}:
            choices = [w["short"] for w in [words.entry(slug, learner),
                       *words._distractors(slug, rng, meanings=True, learner=learner)[:2]]]
            correct_text = choices[0]
            rng.shuffle(choices)
            q["kind"] = "commit"
            q["choices"] = choices + ["No idea"]
            q["answer_index"] = choices.index(correct_text)
            q["reasons"] = ["Matches this word" if value == correct_text else
                            "That meaning belongs to a different word" for value in q["choices"]]
            q["traps"] = [None if value == correct_text else "meaning" for value in q["choices"]]
        q["item_id"] = f"w{i + 1}"
        questions.append(q)
        if q.get("template"):
            seen.add(q["template"])
    if mode == "mix":
        arranged = []
        pending = []
        for q in questions:
            arranged.append(q)
            for p in pending:
                p["gap"] += 1
            if q["kind"] == "learn":
                pending.append({"word": q["word"], "gap": 0})
            if pending and pending[0]["gap"] >= 4:
                first = pending.pop(0)
                arranged.append(_make_item(learner, first["word"], "meaning2word", rng.randrange(2**31)))
        for p in pending:
            arranged.append(_make_item(learner, p["word"], "meaning2word", rng.randrange(2**31)))
        questions = arranged
        for i, q in enumerate(questions):
            q["item_id"] = f"w{i + 1}"
    return questions


def _placement(learner: str, seed: int) -> list[dict]:
    data = words.content()
    rng = random.Random(seed)
    bands: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for w in data["sat"]:
        bands[(w["tier"], w["level"])].append(w)
    chosen = []
    for band in sorted(bands):
        selected = rng.sample(bands[band], min(8, len(bands[band])))
        chosen += [{"kind": "placement", "word": w["slug"], "text": w["word"],
                    "stem": "Do you know this word?", "choices": ["Yes", "No", "Not sure"],
                    "band": ":".join(band), "foil": False} for w in selected]
    foils = words._load("foils")
    chosen += [{"kind": "placement", "word": None, "text": f["word"],
                "stem": "Do you know this word?", "choices": ["Yes", "No", "Not sure"],
                "band": None, "foil": True} for f in rng.sample(foils, 12)]
    rng.shuffle(chosen)
    for i, q in enumerate(chosen):
        q["item_id"] = f"w{i + 1}"
    return chosen


def _route_check(questions: list[dict], seed: int) -> None:
    """Raise the second half one difficulty step after a strong first six."""
    rng = random.Random(seed)
    data = words.content()
    used = {q.get("template") for q in questions}
    for q in questions[6:12]:
        target = {"easy": "medium", "medium": "hard", "hard": "hard"}.get(q.get("difficulty"), "hard")
        transition = q["kind"] == "transition"
        pool = ([p for p in data["pairs"].values() if p.get("difficulty", "medium") == target]
                if transition else [f for f in data["frames"].values() if f["difficulty"] == target])
        rng.shuffle(pool)
        for row in pool:
            template = ("rw.tr." if transition else "rw.wic.") + row["id"]
            if template in used or not words._servable(row) or words._suppressed(row["id"]):
                continue
            slug = rng.choice(row["fits"] if transition else row["keys"])
            try:
                raised = words.item(template, rng.randrange(2**31), slug)
            except ValueError:
                continue
            if q["kind"] == "precise":
                raised["kind"] = "precise"
            raised["item_id"] = q["item_id"]
            used.add(template)
            q.clear()
            q.update(raised)
            break


@router.get("/api/words")
def get_words(days: int = 14, x_learner: str | None = Header(default=None),
              x_tz: int = Depends(tz_of)) -> dict:
    return words.library(_learner(x_learner), x_tz, days)


@router.get("/api/words/insights")
def insights(x_learner: str | None = Header(default=None), x_tz: int = Depends(tz_of)) -> dict:
    learner = _learner(x_learner)
    recent = [r for r in words.word_reviews(learner) if r["at"] >=
              (words.local_day(x_tz) - dt.timedelta(days=60)).isoformat()]
    misses = [r for r in recent if r["correct"] == 0 and r["kind"] in {"incontext", "nearly", "transition"}]
    by_trap = Counter(r["trap"] for r in misses if r["trap"])
    total = max(1, len(misses))
    trap_rows = [{"id": k, "name": words.content()["traps"].get(k, {}).get("name", k),
                  "n": n, "share": round(n / total, 3), "trend": 0,
                  "last_word": next((r["word"] for r in reversed(misses) if r["trap"] == k), None)}
                 for k, n in by_trap.most_common()]
    opens = words.open_traps(learner)
    logic = words.logic_pairs(learner)
    open_logic = [f"{r['needed']}>{r['picked']}" for r in logic if r["n"] >= 2]
    gaps = Counter(r["gap"] for r in recent if r["correct"] == 0 and r["gap"] and
                   r["at"] >= (words.local_day(x_tz) - dt.timedelta(days=7)).isoformat())
    return {"traps": trap_rows, "logic": logic, "open": {"traps": opens, "logic": open_logic},
            "gaps": {"word": gaps["word"], "reading": gaps["reading"]},
            "calibration": words.calibration(learner), "recall": words.recall(learner, x_tz),
            "finish": words.finish_metrics(learner, x_tz)}


@router.get("/api/words/today")
def today(x_learner: str | None = Header(default=None), x_tz: int = Depends(tz_of)) -> dict:
    day = words.local_day(x_tz).isoformat()
    learner = _learner(x_learner)
    out = {"day": day, "summary": words.today_summary(learner, x_tz)}
    for fmt in ("wic", "transition"):
        q = words.daily_item(day, fmt)
        previous = db.one("SELECT * FROM word_reviews WHERE learner=? AND session=? ORDER BY id LIMIT 1",
                          learner, f"qotd:rw:{fmt}:{day}")
        out[fmt] = ({"item": words.public_item(q, q["item_id"]), "word": q["word"] if previous else None,
                     "mine": {"given": previous["given"], "correct": bool(previous["correct"])} if previous else None}
                    if q else None)
    return out


@router.post("/api/words/daily/{fmt}/answer")
def answer_daily(fmt: str, body: dict, x_learner: str | None = Header(default=None),
                 x_tz: int = Depends(tz_of)) -> dict:
    return words.record_daily(_learner(x_learner), words.local_day(x_tz).isoformat(), fmt,
                              body.get("answer"), body.get("ms"), body.get("conf"), x_tz)


@router.get("/api/words/index")
def get_index(response: Response, if_none_match: str | None = Header(default=None)):
    data = words.gloss_index()
    raw = json.dumps(data, sort_keys=True, ensure_ascii=False).encode()
    etag = '"' + hashlib.sha256(raw).hexdigest()[:24] + '"'
    response.headers["ETag"] = etag
    response.headers["Cache-Control"] = "public, max-age=86400"
    if if_none_match == etag:
        response.status_code = 304
        return None
    return data


@router.post("/api/words/run")
def create_run(body: dict, x_learner: str | None = Header(default=None),
               x_tz: int = Depends(tz_of)) -> dict:
    learner = _learner(x_learner)
    mode = body.get("mode", "cards")
    if mode not in {"cards", "quiz", "mix", "placement", "sort", "sprint", "check", "print"}:
        raise HTTPException(422, "unknown Words run mode")
    requested = body.get("count")
    if requested is not None and (not isinstance(requested, int) or not 1 <= requested <= 200):
        raise HTTPException(422, "count must be 1 to 200")
    count = requested or (60 if mode == "placement" else 12 if mode == "check" else
                          200 if mode == "mix" else 20)
    deck = body.get("deck") or ({"source": "today"} if mode == "mix" else
                                 {"source": "new"} if mode == "placement" else {"source": "due"})
    source = deck.get("source", "due")
    formats = body.get("formats") or (["incontext", "transition"] if mode == "check" else
                                       ["meaning2word"] if mode in {"quiz", "print", "sprint"} else [])
    pref_get = part("prefs", "get")
    preference = pref_get(learner, x_tz) if pref_get else {}
    commit_pref = preference.get("words_commit", "auto")
    calibration = words.calibration(learner)
    commit = commit_pref == "on" or (commit_pref == "auto" and calibration["n"] >= 50
                                    and calibration["pct"] is not None and calibration["pct"] < 75)
    sid = "w:" + secrets.token_urlsafe(12)
    seed = int.from_bytes(hashlib.sha256(sid.encode()).digest()[:8], "big")
    if mode == "placement":
        questions = _placement(learner, seed)
    elif source in {"trap", "logic", "readgap"}:
        rng = random.Random(seed)
        value = str(deck.get("value") or "")
        if source == "trap" and value in {"too_strong", "too_weak"} and not any(
                words._servable(frame) and frame["need"].get("pins") == "intensity"
                for frame in words.content()["frames"].values()):
            raise HTTPException(409, "no reviewed frame pins the intensity needed for that trap")
        if source == "logic":
            needed, sep, picked = value.partition(">")
            if not sep:
                raise HTTPException(422, "logic deck needs A>B")
            candidates = [w["slug"] for w in words.content()["transitions"] if w["logic"] == needed]
            wanted, kind = picked, "transition"
        else:
            candidates = [w["slug"] for w in words.content()["sat"]]
            wanted, kind = value if source == "trap" else None, "incontext"
        rng.shuffle(candidates)
        questions = []
        used = set()
        for slug in candidates:
            if slug in used:
                continue
            try:
                q = _make_item(learner, slug, kind, rng.randrange(2**31), want_trap=wanted,
                               strict_trap=bool(wanted))
            except HTTPException:
                continue
            q["item_id"] = f"w{len(questions)+1}"
            questions.append(q)
            used.add(slug)
            if len(questions) >= count:
                break
        if len(questions) < count:
            raise HTTPException(409, "not enough reviewed items carry that trap")
    else:
        if source == "probable":
            slugs = [w["slug"] for w in words.library(learner, x_tz)["words"] if w["placed"] == 2]
        else:
            slugs = words.deck(learner, source, deck.get("value"), count, x_tz, deck.get("words"))
        if mode == "sort" and source == "probable":
            count = len(slugs)
        if mode == "check":
            sat = [w["slug"] for w in words.content()["sat"] if words.choose_template(w["slug"], seed=seed)]
            trans = [w["slug"] for w in words.content()["transitions"] if words.choose_template(w["slug"], seed=seed)]
            if len(sat) < 8 or len(trans) < 4:
                raise HTTPException(409, "not enough reviewed items for a Words check")
            rng = random.Random(seed)
            selected = rng.sample(sat, 8)
            slugs = selected[:6] + rng.sample(trans, 4) + selected[6:]
        if mode == "sprint" and not slugs:
            slugs = words.deck(learner, "new", n=count, tz=x_tz)
        if not slugs:
            raise HTTPException(409, "nothing to study")
        if mode in {"quiz", "print", "check", "sprint"} and len(slugs) < count:
            slugs = (slugs * ((count + len(slugs) - 1) // len(slugs)))[:count]
        if mode == "check":
            questions = _choose(learner, slugs[:12], mode, formats, seed, commit=commit)
        elif mode == "sort":
            questions = [{"kind": "sort", "word": slug, "text": words.entry(slug, learner)["word"],
                          "stem": "How well do you know this word?", "choices": ["Know it", "Not sure", "New to me"],
                          "item_id": f"w{i+1}"} for i, slug in enumerate(slugs[:count])]
        else:
            questions = _choose(learner, slugs[:count], mode, formats, seed, commit=commit)
    if not questions:
        raise HTTPException(409, "nothing to study")
    seen_rw = words.rw_answers(learner)
    method_pref = preference.get("words_method", "auto")
    relation_pref = preference.get("words_relation", "auto")
    method_on = method_pref == "on" or (method_pref == "auto" and
                 sum(r["skill"] == "Words in Context" for r in seen_rw) < 30)
    relation_on = relation_pref == "on" or (relation_pref == "auto" and
                   sum(r["skill"] == "Transitions" for r in seen_rw) < 20)
    needs_pool = list(dict.fromkeys(f["needs"] for f in words.content()["frames"].values()))
    stage_rng = random.Random(seed + 37)
    for q in questions:
        if mode in {"check", "print", "sprint"}:
            continue
        if q["kind"] in {"incontext", "nearly", "precise"} and method_on:
            wrong = stage_rng.sample([n for n in needs_pool if n != q["needs"]], 2)
            choices = [q["needs"], *wrong]
            stage_rng.shuffle(choices)
            q["step"] = "predict"
            q["predictions"] = choices
            q["prediction_answer"] = choices.index(q["needs"])
        elif q["kind"] == "transition" and relation_on:
            choices = list(dict.fromkeys(q["option_logics"]))
            stage_rng.shuffle(choices)
            q["step"] = "logic"
            q["predictions"] = choices
            q["prediction_answer"] = choices.index(q["logic_needed"])
    cfg = {"mode": mode, "deck": deck, "formats": formats, "count": len(questions),
           "timer": body.get("timer", 0), "direction": body.get("direction", "word"),
           "order": body.get("order", "due"), "box": body.get("box"),
           "timer_total": 852 if mode == "check" else body.get("seconds", 60) if mode == "sprint" else None,
           "started_day": words.local_day(x_tz).isoformat(), "commit": commit,
           "method": method_on, "relation": relation_on}
    db.ensure_learner(learner)
    db.run("INSERT INTO sessions(id,kind,learner,started,questions,cfg,subject) VALUES (?,?,?,?,?,?,?)",
           sid, "words", learner, dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           json.dumps(questions), json.dumps(cfg), "rw")
    return _run_payload(_row(sid, learner), include_items=True)


@router.get("/api/words/run/{sid}")
def get_run(sid: str, x_learner: str | None = Header(default=None)) -> dict:
    return _run_payload(_row(sid, _learner(x_learner)), include_items=True)


@router.post("/api/words/run/{sid}/next")
def next_run(sid: str, x_learner: str | None = Header(default=None)) -> dict:
    row = _row(sid, _learner(x_learner))
    if row["finished"]:
        raise HTTPException(409, "this Words run is finished")
    return {"next": _run_payload(row)["next"]}


@router.post("/api/words/run/{sid}/undo")
def undo_sort(sid: str, body: dict, x_learner: str | None = Header(default=None)) -> dict:
    learner = _learner(x_learner)
    with db.atomic():
        row = _row(sid, learner)
        questions, answers, cfg = _current(row)
        if row["finished"] or cfg["mode"] != "sort":
            raise HTTPException(409, "only an unfinished sort can be undone")
        qid = body.get("item_id") or next(reversed(answers), None)
        q = next((q for q in questions if q["item_id"] == qid), None)
        old = answers.get(qid)
        if not q or not old or not old.get("review_id"):
            raise HTTPException(409, "no sort answer to undo")
        words.restore_review(learner, q["word"], old["review_id"])
        db.clear_answer(sid, qid)
    return {"undone": qid, "next": words.public_item(q, qid)}


def _fold(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", text.casefold().strip())
                   if not unicodedata.combining(c))


def _one_edit(a: str, b: str) -> bool:
    if abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        diffs = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
        return len(diffs) == 1 or (len(diffs) == 2 and diffs[1] == diffs[0] + 1 and
                                   a[diffs[0]] == b[diffs[1]] and a[diffs[1]] == b[diffs[0]])
    shorter, longer = (a, b) if len(a) < len(b) else (b, a)
    return any(shorter == longer[:i] + longer[i + 1:] for i in range(len(longer)))


def _choice(q: dict, answer) -> tuple[bool, int | None, str | None]:
    if q["kind"] in {"card", "fix", "learn"}:
        if not isinstance(answer, str) or answer not in {"know", "dontknow", "gotit"}:
            raise HTTPException(422, "answer this card with know or dontknow")
        return answer in {"know", "gotit"}, None, answer
    if q["kind"] == "typed":
        given = _fold(str(answer or ""))
        expected = [_fold(q["answer"]), *(_fold(a) for a in q.get("also", []))]
        exact = given in expected
        near = bool(len(expected[0]) >= 5 and any(_one_edit(given, e) for e in expected))
        return exact or near, None, str(answer)
    if isinstance(answer, str) and len(answer) == 1 and answer.upper() in "ABCD":
        chosen = "ABCD".index(answer.upper())
    elif isinstance(answer, int):
        chosen = answer
    else:
        raise HTTPException(422, "answer must be option 0 to 3")
    if not 0 <= chosen < len(q.get("choices", [])):
        raise HTTPException(422, "answer is outside the choices")
    return chosen == q["answer_index"], chosen, q["choices"][chosen]


def _summary(row, questions: list[dict], answers: dict, cfg: dict) -> dict:
    learner = row["learner"]
    graded = [a for a in answers.values() if a.get("correct") is not None]
    right = sum(bool(a["correct"]) for a in graded)
    skips = [q["word"] for q in questions if answers.get(q["item_id"], {}).get("skipped")]
    by_kind: dict[str, dict] = defaultdict(lambda: {"right": 0, "asked": 0})
    for q in questions:
        a = answers.get(q["item_id"])
        if a and a.get("correct") is not None:
            by_kind[q["kind"]]["asked"] += 1
            by_kind[q["kind"]]["right"] += bool(a["correct"])
    states = [words.state(learner, q["word"]) for q in questions if q.get("word")]
    moved = list(dict.fromkeys(q["word"] for q in questions if q.get("word") and
                               answers.get(q["item_id"], {}).get("box", {}).get("after", 0) >= 4 and
                               answers.get(q["item_id"], {}).get("box", {}).get("before", 0) < 4))
    today = words.local_day().isoformat()
    schedule = {"tomorrow": 0, "in3": 0, "in7": 0, "later": 0}
    for s in states:
        if not s["due"]:
            continue
        left = (dt.date.fromisoformat(s["due"]) - dt.date.fromisoformat(today)).days
        schedule["tomorrow" if left <= 1 else "in3" if left <= 3 else "in7" if left <= 7 else "later"] += 1
    mixups = Counter(a.get("trap") for a in answers.values() if a.get("trap"))
    result = {"asked": len(graded), "right": right, "ms": sum(a.get("ms") or 0 for a in graded),
              "groups": [], "moved_known": moved,
              "learning": [{"slug": s["word"], "due": s["due"]} for s in states if 0 < (s["box"] or 0) < 4],
              "skipped": skips, "schedule": schedule, "by_kind": dict(by_kind),
              "mixups": [{"confusion": k, "kind": k, "n": n} for k, n in mixups.items()],
              "next": {"source": "due", "count": 10, "mode": "cards"}}
    pace = {}
    for kind in by_kind:
        times = [answers[q["item_id"]].get("ms") for q in questions if q["kind"] == kind and
                 answers.get(q["item_id"], {}).get("ms") is not None]
        pace[kind] = {"median_ms": int(statistics.median(times)) if times else None,
                      "target_ms": 71_000}
    result["pace"] = pace
    result["rushed_misses"] = [q["word"] for q in questions if
                                answers.get(q["item_id"], {}).get("correct") is False and
                                (answers[q["item_id"]].get("ms") or 10**9) < 8_000]
    if cfg["mode"] == "sprint":
        score = round(right - (len(graded) - right) / 3, 2)
        previous = db.one("SELECT MAX(json_extract(result,'$.score')) best FROM sessions"
                          " WHERE learner=? AND kind='words' AND json_extract(cfg,'$.mode')='sprint'",
                          learner)
        best = max(score, float(previous["best"] or 0))
        result.update(score=score, best=best, new_best=score > float(previous["best"] or 0))
    if cfg["mode"] == "placement":
        real = [q for q in questions if q["kind"] == "placement" and not q.get("foil")]
        false_yes = sum(answers.get(q["item_id"], {}).get("choice") == "yes" for q in questions if q.get("foil"))
        fa = false_yes / 12
        band_result = []
        n_est = 0
        variance = 0.0
        checks = [(q, answers[q["item_id"]]) for q in questions if q["kind"] == "placement_check"
                  and q["item_id"] in answers]
        overall = sum(bool(a["correct"]) for _, a in checks) / len(checks) if checks else 1.0
        for band in sorted({q["band"] for q in real}):
            sample = [q for q in real if q["band"] == band]
            hit = sum(answers.get(q["item_id"], {}).get("choice") == "yes" for q in sample) / max(1, len(sample))
            band_checks = [a for q, a in checks if q["band"] == band]
            accuracy = (sum(bool(a["correct"]) for a in band_checks) / len(band_checks)
                        if band_checks else overall)
            rate = max(0, (hit - fa) / max(.001, 1 - fa)) * accuracy
            size = sum((w["tier"] + ":" + w["level"]) == band for w in words.content()["sat"])
            band_result.append({"band": band, "rate": round(rate, 3), "n": round(size * rate),
                                "size": size, "check_accuracy": round(accuracy, 3)})
            n_est += round(size * rate)
            variance += (1.96 * (rate * (1 - rate) / max(1, len(sample))) ** .5 * size) ** 2
            if rate >= .9:
                sampled = {q["word"] for q in sample}
                for w in words.content()["sat"]:
                    if w["tier"] + ":" + w["level"] == band and w["slug"] not in sampled:
                        words.place(learner, w["slug"], "probably")
        probable = db.one("SELECT COUNT(*) n FROM word_state WHERE learner=? AND placed=2", learner)["n"]
        claimed = db.one("SELECT COUNT(*) n FROM word_state WHERE learner=? AND placed=1", learner)["n"]
        spread = round(variance ** .5)
        result.update(estimate={"n": n_est, "lo": max(0, n_est - spread), "hi": n_est + spread,
                                "bands": band_result, "caution": false_yes},
                      claimed_n=claimed, probable_n=probable,
                      caution=f"You said yes to {false_yes} of 12 made-up words, so we counted cautiously" if false_yes else None)
    return result


def _finish(row, questions: list[dict], answers: dict, cfg: dict) -> dict:
    if row["finished"]:
        return json.loads(row["result"] or "{}")
    result = _summary(row, questions, answers, cfg)
    db.run("UPDATE sessions SET finished=?,result=? WHERE id=? AND finished IS NULL",
           dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), json.dumps(result), row["id"])
    return result


@router.post("/api/words/run/{sid}/answer")
def answer_run(sid: str, body: dict, x_learner: str | None = Header(default=None),
               x_tz: int = Depends(tz_of)) -> dict:
    learner = _learner(x_learner)
    with db.atomic():
        row = _row(sid, learner)
        questions, answers, cfg = _current(row)
        qid = body.get("item_id")
        q = next((q for q in questions if q["item_id"] == qid), None)
        if q is None:
            raise HTTPException(400, "that item is not in this Words run")
        if qid in answers and not body.get("regrade"):
            return {**answers[qid], "next": _next(questions, answers), "already": True}
        if row["finished"]:
            raise HTTPException(409, "this Words run is finished")
        if q.get("step") in {"predict", "logic"} and not q.get("stage_done"):
            prediction = body.get("prediction", body.get("answer"))
            if isinstance(prediction, int) and not isinstance(prediction, bool):
                if not 0 <= prediction < len(q["predictions"]):
                    raise HTTPException(422, "prediction is outside the choices")
                prediction = q["predictions"][prediction]
            if prediction not in q["predictions"] and prediction != "skip":
                raise HTTPException(422, "choose a prediction first")
            q["prediction_correct"] = prediction == q["predictions"][q["prediction_answer"]]
            q["stage_done"] = True
            db.run("UPDATE sessions SET questions=? WHERE id=?", json.dumps(questions), sid)
            return {"item": words.public_item(q, qid), "step": "choices"}
        if body.get("regrade"):
            old = answers.get(qid)
            if not old or not old.get("review_id"):
                raise HTTPException(409, "no grade to replace")
            words.restore_review(learner, q["word"], old["review_id"])
            db.clear_answer(sid, qid)
            del answers[qid]
        answer = body.get("answer")
        ms = body.get("ms")
        if ms is not None and (not isinstance(ms, int) or ms < 0):
            raise HTTPException(422, "ms must be nonnegative")
        if answer == "skip":
            verdict = {"correct": None, "skipped": True, "word": q.get("word")}
            if q.get("word") and not q.get("skip_once"):
                clone = {**q, "item_id": f"w{len(questions)+1}", "skip_once": True}
                questions.append(clone)
        elif q["kind"] in {"placement", "sort"}:
            choice = str(answer).casefold()
            if choice in {"0", "yes", "know", "know it"}:
                choice = "yes" if q["kind"] == "placement" else "know"
            elif choice in {"1", "no", "new", "new to me"}:
                choice = "no"
            elif choice in {"2", "unsure", "not sure"}:
                choice = "unsure"
            else:
                raise HTTPException(422, "answer must be yes, no or unsure")
            if q.get("foil"):
                verdict = {"correct": None, "choice": choice, "word": None}
            else:
                placed = words.place(learner, q["word"], choice, x_tz)
                if q["kind"] == "sort" and choice == "unsure":
                    db.run("UPDATE word_state SET saved=1 WHERE learner=? AND word=?", learner, q["word"])
                verdict = {"correct": None, "choice": choice, **placed}
            if q["kind"] == "placement" and not q.get("foil") and choice == "yes":
                yes_n = 1 + sum(a.get("choice") == "yes" and
                                next((x for x in questions if x["item_id"] == aid), {}).get("kind") == "placement"
                                and not next((x for x in questions if x["item_id"] == aid), {}).get("foil")
                                for aid, a in answers.items())
                if yes_n % 3 == 0:
                    probe = words.quiz_item(q["word"], "word2meaning",
                                            random.Random(hashlib.sha256(f"{sid}:{yes_n}".encode()).digest()), learner)
                    probe.update(kind="placement_check", band=q["band"],
                                 item_id=f"w{len(questions)+1}")
                    questions.insert(questions.index(q) + 1, probe)
        elif q["kind"] == "placement_check":
            right, index, given = _choice(q, answer)
            words._review_row(db.conn(), learner, q["word"], sid, "placement", "placement_check",
                              right, given, words.state(learner, q["word"])["box"],
                              words.state(learner, q["word"])["due"], ms,
                              dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), attempt=0)
            verdict = {"correct": right, "answer_index": q["answer_index"], "given": given,
                       "reasons": q["reasons"], "band": q["band"], "word": q["word"], "ms": ms}
        elif q["kind"] == "order":
            if not isinstance(answer, list) or len(answer) != 4:
                raise HTTPException(422, "order all four words")
            if all(isinstance(x, int) for x in answer):
                if sorted(answer) != [0, 1, 2, 3]:
                    raise HTTPException(422, "order each option once")
                ordered = [q["option_slugs"][i] for i in answer]
            elif sorted(answer) == sorted(q["option_slugs"]):
                ordered = answer
            else:
                raise HTTPException(422, "order each option once")
            ok = ordered == q["answer_order"]
            stamp = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
            for slug in q["option_slugs"]:
                s = words.state(learner, slug)
                words._review_row(db.conn(), learner, slug, sid, cfg["mode"], "order", ok,
                                  str(ordered.index(slug)), s["box"], s["due"], ms, stamp,
                                  attempt=0, state_before=s)
            verdict = {"correct": ok, "answer_order": q["answer_order"],
                       "reasons": q["reasons"], "word": q["word"], "ms": ms}
        elif q["kind"] == "learn":
            if answer not in {"gotit", "know"}:
                raise HTTPException(422, "use gotit to continue")
            verdict = {"correct": None, "word": q["word"], "learned": True}
        else:
            if answer is None and q["kind"] not in {"card", "fix"}:
                ok, index, given = False, None, None
            else:
                ok, index, given = _choice(q, answer)
            trap = q.get("traps", [None] * 4)[index] if index is not None else None
            gap = None
            if q.get("needs") and not ok and q.get("stage_done"):
                gap = "word" if q.get("prediction_correct") else "reading"
            spelling = None
            if q["kind"] == "typed" and ok and _fold(given or "") != _fold(q["answer"]):
                spelling = q["answer"]
            grade_kind = "card" if q["kind"] == "commit" else q["kind"]
            verdict = words.grade(learner, q["word"], ok, cfg["mode"], grade_kind, ms, sid,
                                  trap, x_tz, given=given, conf=body.get("conf"),
                                  template=q.get("template"), seed=q.get("seed") if q.get("template") else None,
                                  gap=gap, hinted=bool(body.get("hinted")), at=body.get("at"))
            verdict.update(answer_index=q.get("answer_index"), reasons=q.get("reasons"),
                           traps=q.get("traps"), trap=trap, given=given, gap=gap,
                           spans=q.get("spans", []),
                           needs=q.get("needs"), spelling=spelling, ms=ms,
                           logic_needed=q.get("logic_needed"),
                           logic_picked=q.get("option_logics", [None] * 4)[index] if index is not None else None,
                           relation=q.get("relation"), back=q.get("back") if q["kind"] == "commit" else None)
            if q.get("template"):
                verdict["pick_split"] = words.pick_split(q["template"])
                words.crowd_guard(q["template"])
            if q["kind"] in {"card", "fix"} and not ok and not q.get("requeue_n"):
                clone = {**q, "item_id": f"w{len(questions)+1}", "requeue_n": 1}
                pos = min(len(questions), questions.index(q) + 4)
                questions.insert(pos, clone)
                verdict["requeued"] = True
        if not db.set_answer(sid, qid, verdict, only_new=True):
            raise HTTPException(409, "this item was already answered")
        answers[qid] = verdict
        if cfg["mode"] == "check" and len(answers) == 6 and all(f"w{i}" in answers for i in range(1, 7)):
            cfg["route"] = "upper" if sum(bool(answers[f"w{i}"].get("correct")) for i in range(1, 7)) >= 5 else "lower"
            if cfg["route"] == "upper":
                _route_check(questions, int.from_bytes(hashlib.sha256(sid.encode()).digest()[:8], "big") + 6)
            db.run("UPDATE sessions SET cfg=? WHERE id=?", json.dumps(cfg), sid)
        if q.get("template"):
            db.run("UPDATE sessions SET questions=? WHERE id=?", json.dumps(questions), sid)
        elif len(questions) != len(json.loads(row["questions"] or "[]")):
            db.run("UPDATE sessions SET questions=? WHERE id=?", json.dumps(questions), sid)
        remaining = _next(questions, answers)
        if cfg.get("box") and sum((a.get("ms") or 0) for a in answers.values()) >= cfg["box"] * 60_000:
            remaining = None
        if remaining is None:
            verdict["summary"] = _finish(_row(sid, learner), questions, answers, cfg)
        verdict["next"] = remaining
        if cfg["mode"] == "check" and remaining is not None:
            return {"filed": True, "next": remaining, "total": len(answers)}
        return verdict


@router.post("/api/words/run/{sid}/also-fits")
def also_fits(sid: str, body: dict, x_learner: str | None = Header(default=None)) -> dict:
    learner = _learner(x_learner)
    row = _row(sid, learner)
    questions, answers, _ = _current(row)
    qid = body.get("item_id")
    q = next((item for item in questions if item["item_id"] == qid), None)
    if not q or qid not in answers or not q.get("template"):
        raise HTTPException(409, "answer a generated item before reporting it")
    choice = body.get("choice", answers[qid].get("given"))
    if choice not in q.get("choices", []) or choice == q["choices"][q["answer_index"]]:
        raise HTTPException(422, "report one of this item's wrong options")
    return words.report_fit(q["template"], choice, learner)


@router.post("/api/words/run/{sid}/finish")
def finish_run(sid: str, x_learner: str | None = Header(default=None)) -> dict:
    learner = _learner(x_learner)
    with db.atomic():
        row = _row(sid, learner)
        questions, answers, cfg = _current(row)
        return _finish(row, questions, answers, cfg)


@router.post("/api/words/run/{sid}/another")
def another_run(sid: str, body: dict, x_learner: str | None = Header(default=None)) -> dict:
    learner = _learner(x_learner)
    with db.atomic():
        row = _row(sid, learner)
        if row["finished"]:
            raise HTTPException(409, "this Words run is finished")
        questions, answers, cfg = _current(row)
        qid = body.get("item_id")
        old = next((q for q in questions if q["item_id"] == qid), None)
        if not old or qid not in answers:
            raise HTTPException(409, "answer the item before requesting another")
        if not old.get("template"):
            raise HTTPException(409, "this item has no generated twin")
        old = {**old, "picked_trap": answers[qid].get("trap")}
        seen = {q.get("template") for q in questions if q.get("template")}
        try:
            q = words.another(old, body.get("like", "word"), learner, seen)
        except ValueError as exc:
            raise HTTPException(409, str(exc)) from exc
        q["item_id"] = f"w{len(questions)+1}"
        questions.insert(questions.index(next(q for q in questions if q["item_id"] == qid)) + 1, q)
        db.run("UPDATE sessions SET questions=? WHERE id=?", json.dumps(questions), sid)
        return {"item": words.public_item(q, q["item_id"]), "total": len(questions)}


@router.post("/api/words/run/{sid}/save")
def save_run(sid: str, body: dict, x_learner: str | None = Header(default=None)) -> dict:
    learner = _learner(x_learner)
    row = _row(sid, learner)
    questions, answers, _ = _current(row)
    qid = body.get("item_id")
    q = next((q for q in questions if q["item_id"] == qid), None)
    if not q or qid not in answers:
        raise HTTPException(409, "answer before saving this word")
    if not q.get("word"):
        raise HTTPException(409, "this item has no library word")
    s = words.state(learner, q["word"])
    s["saved"] = 1
    with db.atomic() as c:
        words._upsert_state(c, s)
    return {"saved": True}


@router.post("/api/words/run/{sid}/grade")
def grade_print(sid: str, body: dict, x_learner: str | None = Header(default=None),
                x_tz: int = Depends(tz_of)) -> dict:
    learner = _learner(x_learner)
    row = _row(sid, learner)
    _, _, cfg = _current(row)
    if cfg.get("mode") != "print":
        raise HTTPException(409, "this is not a worksheet")
    letters = str(body.get("letters", "")).strip().upper()
    questions = json.loads(row["questions"] or "[]")
    if len(letters) != len(questions) or any(c not in "ABCD" for c in letters):
        raise HTTPException(422, "send one A-D letter per item")
    for q, answer in zip(questions, letters):
        fresh = _row(sid, learner)
        if fresh["finished"]:
            break
        answer_run(sid, {"item_id": q["item_id"], "answer": answer}, x_learner, x_tz)
    return finish_run(sid, x_learner)


@router.get("/api/words/run/{sid}/key")
def print_key(sid: str, x_learner: str | None = Header(default=None)) -> dict:
    row = _row(sid, _learner(x_learner))
    questions, _, cfg = _current(row)
    if cfg.get("mode") != "print":
        raise HTTPException(409, "this is not a worksheet")
    return {"id": sid, "answers": [{"item_id": q["item_id"],
            "letter": "ABCD"[q["answer_index"]] if q.get("answer_index") is not None else None,
            "reasons": q.get("reasons"), "meaning": words.entry(q["word"], row["learner"])["short"]}
            for q in questions]}


@router.post("/api/words/run/{sid}/new-version")
def new_version(sid: str, x_learner: str | None = Header(default=None),
                x_tz: int = Depends(tz_of)) -> dict:
    row = _row(sid, _learner(x_learner))
    questions, _, cfg = _current(row)
    if cfg.get("mode") != "print":
        raise HTTPException(409, "this is not a worksheet")
    return create_run({"mode": "print", "deck": {"source": "words",
                       "words": [q["word"] for q in questions]},
                       "formats": cfg["formats"], "count": len(questions)}, x_learner, x_tz)


def _normal(text: str) -> str:
    return _fold(text).replace("’", "'")


@lru_cache(maxsize=1)
def _matches() -> dict[str, str]:
    found = {}
    for w in words.content()["entries"].values():
        for form in (w["word"], *w.get("also", [])):
            found.setdefault(_normal(form), w["slug"])
    return found


def _own_payload(body: dict) -> dict:
    limits = {"word": 60, "meaning": 400, "example": 300, "notes": 1000, "list": 30}
    out = {}
    for key, limit in limits.items():
        value = str(body.get(key) or "").strip()
        if len(value) > limit or (key in {"word", "meaning"} and not value):
            raise HTTPException(400, f"{key} is required and must be at most {limit} characters")
        out[key] = value
    for key in ("same", "opposite"):
        value = body.get(key) or []
        if isinstance(value, str):
            value = [x.strip() for x in value.split(",") if x.strip()]
        if not isinstance(value, list) or len(value) > 10 or any(not isinstance(x, str) or len(x) > 60 for x in value):
            raise HTTPException(400, f"{key} must contain at most 10 words")
        out[key] = json.dumps(value)
    out["pos"] = str(body.get("pos") or "")[:30]
    out["source"] = str(body.get("source") or "")[:120]
    return out


@router.post("/api/words/mine")
def add_own(body: dict, x_learner: str | None = Header(default=None)) -> dict:
    learner = _learner(x_learner)
    data = _own_payload(body)
    duplicate = db.one("SELECT id FROM my_words WHERE learner=? AND lower(word)=lower(?)", learner, data["word"])
    if duplicate:
        raise HTTPException(409, {"existing_id": duplicate["id"]})
    hint = _matches().get(_normal(data["word"]))
    if hint:
        return {"library_slug": hint}
    slug = "u:" + secrets.token_urlsafe(10)
    stamp = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    db.ensure_learner(learner)
    db.run("INSERT INTO my_words(id,learner,word,meaning,pos,example,same,opposite,notes,list,source,created,updated)"
           " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", slug, learner, data["word"], data["meaning"],
           data["pos"], data["example"], data["same"], data["opposite"], data["notes"],
           data["list"] or "My words", data["source"], stamp, stamp)
    return {"id": slug, "word": data["word"]}


@router.put("/api/words/mine/{slug}")
def edit_own(slug: str, body: dict, x_learner: str | None = Header(default=None)) -> dict:
    learner = _learner(x_learner)
    if not db.one("SELECT 1 FROM my_words WHERE id=? AND learner=?", slug, learner):
        raise HTTPException(404, "own word not found")
    data = _own_payload(body)
    duplicate = db.one("SELECT id FROM my_words WHERE learner=? AND lower(word)=lower(?) AND id!=?",
                       learner, data["word"], slug)
    if duplicate:
        raise HTTPException(409, {"existing_id": duplicate["id"]})
    db.run("UPDATE my_words SET word=?,meaning=?,pos=?,example=?,same=?,opposite=?,notes=?,list=?,"
           "source=?,updated=? WHERE id=? AND learner=?", data["word"], data["meaning"],
           data["pos"], data["example"], data["same"], data["opposite"], data["notes"],
           data["list"] or "My words", data["source"],
           dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), slug, learner)
    return {"id": slug, "word": data["word"]}


@router.delete("/api/words/mine/{slug}")
def delete_own(slug: str, x_learner: str | None = Header(default=None)) -> dict:
    learner = _learner(x_learner)
    with db.atomic() as c:
        if not c.execute("SELECT 1 FROM my_words WHERE id=? AND learner=?", (slug, learner)).fetchone():
            raise HTTPException(404, "own word not found")
        for table, column in (("my_words", "id"), ("word_state", "word"), ("word_reviews", "word")):
            c.execute(f"DELETE FROM {table} WHERE learner=? AND {column}=?", (learner, slug))
    return {"deleted": True}


@router.post("/api/words/mine/import")
def import_own(body: dict, x_learner: str | None = Header(default=None)) -> dict:
    learner = _learner(x_learner)
    text = str(body.get("text") or "")
    if len(text.encode()) > 50_000 or len(text.splitlines()) > 500:
        raise HTTPException(422, "import exceeds 50 KB or 500 lines")
    lines = text.splitlines()
    result = {"added": 0, "skipped": []}
    for i, line in enumerate(lines, 1):
        if i == 1 and line.strip().lower() == "word,meaning":
            continue
        if not line.strip():
            continue
        pair = None
        if "\t" in line:
            pair = line.split("\t", 1)
        elif " - " in line:
            pair = line.split(" - ", 1)
        elif " — " in line:
            pair = line.split(" — ", 1)
        elif ":" in line:
            pair = line.split(":", 1)
        elif "," in line:
            parsed = next(csv.reader([line]))
            if len(parsed) >= 2:
                pair = [parsed[0], parsed[1]]
        if not pair:
            result["skipped"].append({"line": i, "why": "no meaning"})
            continue
        try:
            created = add_own({"word": pair[0], "meaning": pair[1], "list": body.get("list")}, x_learner)
            if created.get("id"):
                result["added"] += 1
            else:
                result["skipped"].append({"line": i, "why": "already in library"})
        except HTTPException as exc:
            result["skipped"].append({"line": i, "why": str(exc.detail)})
    return result


@router.get("/api/words/mine.csv")
def export_own(x_learner: str | None = Header(default=None)):
    learner = _learner(x_learner)
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(("word", "meaning", "pos", "example", "list"))
    for r in db.rows("SELECT word,meaning,pos,example,list FROM my_words WHERE learner=? ORDER BY word", learner):
        writer.writerow(tuple(r))
    return Response(out.getvalue(), media_type="text/csv",
                    headers={"Content-Disposition": 'attachment; filename="my-words.csv"'})


@router.post("/api/words/lists/match")
def match_list(body: dict) -> dict:
    text = str(body.get("text") or "")
    if len(text) > 20_000:
        raise HTTPException(422, "text exceeds 20,000 characters")
    pieces = [x.strip() for x in re.split(r"[,\n]", text) if x.strip()]
    if len(pieces) > 1_000:
        raise HTTPException(422, "list exceeds 1,000 words")
    found, missing = [], []
    lookup = _matches()
    for piece in pieces:
        slug = lookup.get(_normal(piece))
        if slug:
            if slug not in found:
                found.append(slug)
        elif piece not in missing:
            missing.append(piece)
    return {"found": found, "missing": missing}


@router.post("/api/words/lists")
def add_list(body: dict, x_learner: str | None = Header(default=None)) -> dict:
    learner = _learner(x_learner)
    name = str(body.get("name") or "").strip()
    if not name or len(name) > 30:
        raise HTTPException(422, "list name must be 1 to 30 characters")
    slugs = body.get("words") or []
    if not isinstance(slugs, list) or len(slugs) > 1_000:
        raise HTTPException(422, "list can hold at most 1,000 words")
    slugs = list(dict.fromkeys(slugs))
    if any(not words.entry(s, learner) for s in slugs):
        raise HTTPException(422, "list includes an unknown word")
    stamp = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    db.ensure_learner(learner)
    try:
        db.run("INSERT INTO word_lists(learner,name,words,created) VALUES (?,?,?,?)",
               learner, name, json.dumps(slugs), stamp)
    except Exception as exc:
        raise HTTPException(409, "a list with that name already exists") from exc
    return {"name": name, "words": slugs, "count": len(slugs)}


@router.put("/api/words/lists/{name}")
def edit_list(name: str, body: dict, x_learner: str | None = Header(default=None)) -> dict:
    learner = _learner(x_learner)
    old = db.one("SELECT * FROM word_lists WHERE learner=? AND name=?", learner, name)
    if not old:
        raise HTTPException(404, "list not found")
    new_name = str(body.get("name") or name).strip()
    slugs = body.get("words", json.loads(old["words"]))
    if not new_name or len(new_name) > 30 or not isinstance(slugs, list) or len(slugs) > 1_000:
        raise HTTPException(422, "invalid list")
    if any(not words.entry(s, learner) for s in slugs):
        raise HTTPException(422, "list includes an unknown word")
    with db.atomic() as c:
        c.execute("DELETE FROM word_lists WHERE learner=? AND name=?", (learner, name))
        c.execute("INSERT INTO word_lists(learner,name,words,created) VALUES (?,?,?,?)",
                  (learner, new_name, json.dumps(list(dict.fromkeys(slugs))), old["created"]))
    return {"name": new_name, "words": slugs}


@router.delete("/api/words/lists/{name}")
def delete_list(name: str, x_learner: str | None = Header(default=None)) -> dict:
    learner = _learner(x_learner)
    with db.atomic() as c:
        if not c.execute("SELECT 1 FROM word_lists WHERE learner=? AND name=?", (learner, name)).fetchone():
            raise HTTPException(404, "list not found")
        c.execute("DELETE FROM word_lists WHERE learner=? AND name=?", (learner, name))
        c.execute("UPDATE my_words SET list='My words' WHERE learner=? AND list=?", (learner, name))
    return {"deleted": True}


@router.post("/api/words/lists/{name}/share")
def share_list(name: str, x_learner: str | None = Header(default=None)) -> dict:
    learner = _learner(x_learner)
    row = db.one("SELECT words FROM word_lists WHERE learner=? AND name=?", learner, name)
    if not row:
        raise HTTPException(404, "list not found")
    create = part("sets", "create")
    if create is None:
        return {"available": False, "code": None, "reason": "sharing is not available yet"}
    return create(learner, {"kind": "words", "items": json.loads(row["words"]), "name": name})


@router.post("/api/words/outside")
def outside(body: dict, x_learner: str | None = Header(default=None)) -> dict:
    learner = _learner(x_learner)
    choices = body.get("choices")
    if (not isinstance(choices, list) or len(choices) != 4 or
            any(not isinstance(x, str) or not x.strip() for x in choices) or
            len({_normal(x) for x in choices}) != 4):
        raise HTTPException(422, "send four distinct word choices")
    key, picked = body.get("key"), body.get("picked")
    if key not in choices or picked not in choices or key == picked:
        raise HTTPException(422, "key and picked must be different choices")
    lookup = _matches()
    found = {}
    for option in choices:
        slug = lookup.get(_normal(option))
        if not slug:
            existing = db.one("SELECT id FROM my_words WHERE learner=? AND lower(word)=lower(?)",
                              learner, option)
            slug = existing["id"] if existing else add_own(
                {"word": option, "meaning": "Add a meaning", "source": "Outside Words question"},
                x_learner).get("id")
        found[option] = slug
    key_slug, pick_slug = found[key], found[picked]
    k, p = words.entry(key_slug, learner), words.entry(pick_slug, learner)
    trap = "not_classified"
    if k and p and not (k.get("own") or p.get("own")):
        if k.get("logic") and p.get("logic") and k["logic"] != p["logic"]:
            trap = "wrong_logic"
        elif k.get("class") == p.get("class") and k.get("polarity") == p.get("polarity"):
            trap = "too_strong" if p.get("intensity", 0) > k.get("intensity", 0) else "too_weak"
        elif p.get("class") == words.content()["classes"].get(k.get("class"), {}).get("opposite"):
            trap = "reversed"
        elif any(x.get("word", "").casefold() == p["word"].casefold() for x in k.get("lookalikes", [])):
            trap = "lookalike"
        elif p.get("polarity") != k.get("polarity"):
            trap = "connotation"
        else:
            trap = "topical"
    name = str(body.get("label") or "Bluebook · missed question")[:30]
    slugs = list(dict.fromkeys(found.values()))
    old = db.one("SELECT words FROM word_lists WHERE learner=? AND name=?", learner, name)
    if old:
        slugs = list(dict.fromkeys(json.loads(old["words"]) + slugs))
        db.run("UPDATE word_lists SET words=? WHERE learner=? AND name=?", json.dumps(slugs), learner, name)
    else:
        add_list({"name": name, "words": slugs}, x_learner)
    for slug in (key_slug, pick_slug):
        s = words.state(learner, slug)
        s["saved"] = 1
        s["due"] = words.local_day().isoformat()
        with db.atomic() as c:
            words._upsert_state(c, s)
    stamp = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    with db.atomic() as c:
        words._review_row(c, learner, key_slug or pick_slug or "outside", None,
                          "outside", "outside", False, picked, 0, None, None, stamp,
                          trap=trap, attempt=0)
    run = None
    if key_slug and trap in words.content()["traps"]:
        try:
            run = create_run({"mode": "quiz", "deck": {"source": "trap", "value": trap},
                              "formats": ["incontext"], "count": 3}, x_learner, 0)
        except HTTPException:
            pass
    return {"trap": trap, "list": name, "run": run}


@router.post("/api/words/reset")
def reset_words(body: dict, x_learner: str | None = Header(default=None)) -> dict:
    learner = _learner(x_learner)
    slugs = body.get("words") or []
    if not isinstance(slugs, list) or len(slugs) > 200:
        raise HTTPException(422, "send up to 200 words")
    with db.atomic() as c:
        for slug in slugs:
            c.execute("DELETE FROM word_state WHERE learner=? AND word=?", (learner, slug))
    return {"reset": len(slugs)}


def _secret() -> bytes:
    row = db.one("SELECT v FROM kv WHERE k='words:sample-secret'")
    if row:
        return bytes.fromhex(row["v"])
    value = secrets.token_hex(32)
    db.run("INSERT OR IGNORE INTO kv(k,v) VALUES ('words:sample-secret',?)", value)
    return bytes.fromhex(db.one("SELECT v FROM kv WHERE k='words:sample-secret'")["v"])


def _sign(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    sig = hmac.new(_secret(), raw, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(raw + sig).decode().rstrip("=")


def _unsign(token: str, learner: str, tz: int) -> dict:
    try:
        blob = base64.urlsafe_b64decode(token + "=" * (-len(token) % 4))
        raw, sig = blob[:-32], blob[-32:]
        if not hmac.compare_digest(sig, hmac.new(_secret(), raw, hashlib.sha256).digest()):
            raise ValueError("signature")
        payload = json.loads(raw)
        if payload["learner"] != learner or payload["day"] != words.local_day(tz).isoformat():
            raise ValueError("owner or day")
        return payload
    except (ValueError, KeyError, TypeError, UnicodeDecodeError) as exc:
        raise HTTPException(400, "invalid or expired word sample token") from exc


def _sample(learner: str, slug: str, tz: int, extra: int = 0) -> dict | None:
    seen = {r["template"] for r in words.rw_answers(learner) if r["word"] == slug}
    seed = int.from_bytes(hashlib.sha256(f"sample:{learner}:{slug}:{words.local_day(tz)}:{extra}".encode())
                          .digest()[:4], "big")
    template = words.choose_template(slug, learner=learner, seed=seed, seen=seen)
    if not template:
        return None
    try:
        q = words.item(template, seed, slug)
    except ValueError:
        return None
    payload = {"learner": learner, "day": words.local_day(tz).isoformat(),
               "template": q["template"], "seed": q["seed"], "word": slug}
    return {"item": words.public_item(q, "sample:" + hashlib.sha256(_sign(payload).encode()).hexdigest()[:12]),
            "token": _sign(payload)}


@router.post("/api/words/sample")
def new_sample(body: dict, x_learner: str | None = Header(default=None),
               x_tz: int = Depends(tz_of)) -> dict:
    learner = _learner(x_learner)
    slug = body.get("slug")
    if not words.entry(slug, learner):
        raise HTTPException(404, "unknown word")
    existing = len([r for r in words.rw_answers(learner) if r["word"] == slug])
    sample = _sample(learner, slug, x_tz, extra=existing + 1)
    if sample is None:
        raise HTTPException(409, "no reviewed frame is available")
    return sample


@router.post("/api/words/sample/answer")
def answer_sample(body: dict, x_learner: str | None = Header(default=None),
                  x_tz: int = Depends(tz_of)) -> dict:
    learner = _learner(x_learner)
    token = str(body.get("token") or "")
    payload = _unsign(token, learner, x_tz)
    try:
        q = words.item(payload["template"], payload["seed"], payload["word"])
    except ValueError as exc:
        raise HTTPException(400, "this sample is no longer available") from exc
    session = "sample:" + hashlib.sha256(token.encode()).hexdigest()[:24]
    with db.atomic():
        old = db.one("SELECT * FROM word_reviews WHERE learner=? AND session=? ORDER BY id LIMIT 1",
                     learner, session)
        if old:
            return {"already": True, "correct": bool(old["correct"]),
                    "answer_index": q["answer_index"], "reasons": q["reasons"],
                    "traps": q["traps"], "spans": q["spans"]}
        ok, index, given = _choice(q, body.get("answer"))
        verdict = words.grade(learner, q["word"], ok, "sheet", q["kind"], body.get("ms"),
                              session, q["traps"][index], x_tz, given=given,
                              conf=body.get("conf"), template=q["template"], seed=q["seed"])
    return {**verdict, "answer_index": q["answer_index"], "reasons": q["reasons"],
            "traps": q["traps"], "trap": q["traps"][index],
            "spans": q["spans"], "needs": q["needs"]}


@router.get("/api/words/root/{root_id}")
def root_detail(root_id: str, x_learner: str | None = Header(default=None)) -> dict:
    learner = _learner(x_learner)
    root = words.content()["roots"].get(root_id)
    if not root:
        raise HTTPException(404, "unknown root")
    related = []
    for row in root["words"]:
        s = words.state(learner, row["slug"])
        related.append({**row, "word": words.entry(row["slug"])["word"], "box": s["box"],
                        "known": s["box"] >= 4 and bool(s["proven"])})
    return {**root, "words": related,
            "known": sum(w["known"] for w in related), "total": len(related)}


@router.post("/api/words/lookup")
def lookup(body: dict, x_learner: str | None = Header(default=None)) -> dict:
    learner = _learner(x_learner)
    slug = body.get("slug")
    if not words.entry(slug, learner):
        raise HTTPException(404, "unknown word")
    where, ref = body.get("where"), str(body.get("ref") or "")[:120]
    if where not in {"session", "qotd", "challenge", "report", "words"} or not ref:
        raise HTTPException(422, "lookup needs a where and ref")
    session = f"lookup:{where}:{ref}"
    if db.one("SELECT 1 FROM word_reviews WHERE learner=? AND word=? AND session=? AND mode='lookup'",
              learner, slug, session):
        return {"ok": True, "already": True}
    stamp = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    with db.atomic() as c:
        s = words.state(learner, slug)
        s["looked_at"] = stamp
        words._upsert_state(c, s)
        words._review_row(c, learner, slug, session, "lookup", "lookup", None, None,
                          s["box"], s["due"], None, stamp, attempt=0)
    return {"ok": True, "already": False}


@router.post("/api/words/{slug}/save")
def save_word(slug: str, body: dict, x_learner: str | None = Header(default=None)) -> dict:
    learner = _learner(x_learner)
    if not words.entry(slug, learner):
        raise HTTPException(404, "unknown word")
    if type(body.get("on")) is not bool:
        raise HTTPException(422, "on must be true or false")
    s = words.state(learner, slug)
    s["saved"] = int(body["on"])
    with db.atomic() as c:
        words._upsert_state(c, s)
    return {"saved": bool(s["saved"])}


@router.put("/api/words/{slug}/hook")
def hook(slug: str, body: dict, x_learner: str | None = Header(default=None)) -> dict:
    learner = _learner(x_learner)
    if not words.entry(slug, learner):
        raise HTTPException(404, "unknown word")
    value = str(body.get("text") or "")
    if len(value) > 140:
        raise HTTPException(422, "hook must be at most 140 characters")
    s = words.state(learner, slug)
    s["hook"] = value
    with db.atomic() as c:
        words._upsert_state(c, s)
    return {"hook": value}


@router.post("/api/words/{slug}/grade")
def grade_sheet(slug: str, body: dict, x_learner: str | None = Header(default=None),
                x_tz: int = Depends(tz_of)) -> dict:
    learner = _learner(x_learner)
    if type(body.get("ok")) is not bool:
        raise HTTPException(422, "ok must be true or false")
    last = db.one("SELECT id,at,mode FROM word_reviews WHERE learner=? AND word=?"
                  " ORDER BY id DESC LIMIT 1", learner, slug)
    with db.atomic():
        if last and last["mode"] == "sheet" and words.local_day(x_tz, last["at"]) == words.local_day(x_tz):
            words.restore_review(learner, slug, last["id"])
        verdict = words.grade(learner, slug, body["ok"], "sheet", "card", body.get("ms"),
                              None, None, x_tz)
    return {**verdict, "status_line": verdict["status"]}


@router.get("/api/words/{slug}")
def word_detail(slug: str, x_learner: str | None = Header(default=None),
                x_tz: int = Depends(tz_of)) -> dict:
    learner = _learner(x_learner)
    w = words.entry(slug, learner)
    if not w:
        raise HTTPException(404, "unknown word")
    data = words.content()
    s = words.state(learner, slug)
    idx = data["index"]["words"].get(slug, {"confusions": [], "roots": [], "frames": []})
    conflicts = []
    for ident in idx["confusions"]:
        c = data["confusions"][ident]
        other = next((x for x in c["words"] if x != slug), None)
        other_entry = words.entry(other)
        picked = db.rows("SELECT at FROM word_reviews WHERE learner=? AND word=? AND correct=0 AND given=?",
                         learner, slug, other_entry["word"] if other_entry else other)
        conflicts.append({"id": ident, "kind": c["kind"], "other": other,
                          "tell": c["tell"], "fell": len(picked),
                          "last": picked[-1]["at"] if picked else None, "templates": 0})
    roots = [{**data["roots"][rid], **next((r for r in data["roots"][rid]["words"] if r["slug"] == slug), {})}
             for rid in idx["roots"]]
    family = [v for v in data["sat"] if w.get("class") and v["class"] == w.get("class") and
              v["pos"] == w.get("pos")]
    family.sort(key=lambda v: (v["intensity"], v["word"]))
    shades = {"dimension": data["classes"].get(w.get("class"), {}).get("dimension"),
              "words": [{"slug": v["slug"], "word": v["word"], "intensity": v["intensity"],
                         "polarity": v["polarity"]} for v in family],
              "at": next((i for i, v in enumerate(family) if v["slug"] == slug), None)}
    reviews = words.word_reviews(learner, slug)
    by_kind = defaultdict(lambda: {"right": 0, "n": 0})
    for r in reviews:
        if r["correct"] is not None:
            by_kind[r["kind"]]["n"] += 1
            by_kind[r["kind"]]["right"] += bool(r["correct"])
    others = [{"slug": v["slug"], "word": v["word"], "sense": v.get("sense"),
               "short": v["short"], "state": words.state(learner, v["slug"])}
              for v in data["entries"].values() if v["word"].casefold() == w["word"].casefold()
              and v["slug"] != slug]
    journey = [{"at": r["at"], "kind": r["kind"], "correct": r["correct"],
                "box_before": r["box_before"], "due_before": r["due_before"],
                "given": r["given"], "trap": r["trap"]} for r in reviews]
    return {**w, "state": s, "measured": words._measured(slug) if slug in data["entries"] else None,
            "other_senses": others, "confusions": conflicts, "roots": roots, "shades": shades,
            "journey": journey, "record": {"reviews": {"n": len(reviews),
            "right": sum(r["correct"] == 1 for r in reviews), "by_kind": dict(by_kind)},
            "lookups": sum(r["mode"] == "lookup" for r in reviews), "box": s["box"],
            "due": s["due"], "first": s["first"], "last": s["last"]},
            "sample": _sample(learner, slug, x_tz) if not slug.startswith("u:") else None}
