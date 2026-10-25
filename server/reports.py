"""Report a problem, and the admin that answers it (R17: Shell §2.10 and §10;
U3, V6, W18, X10 and SR19 of spec/v2-upgrades).

POST /api/report is one multipart form, a `data` JSON field plus up to 10
files, from everywhere a student can report: a question (the session, the
test window, the report review, the question of the day, the challenge, the
quick sheet, Review, the Library), a sitting, a page, a word, a paper or the
tests catalog. What a question report is about -- template, seed, the answer
given and its marking -- is worked out here from the learner's own session;
nothing of it is taken from the client, and the key never goes back. Files are
written to server/reports/{id}/ (git-ignored).

A key dispute is answered at once where it can be (U3's instant check): the
item is regenerated from (template, seed) and re-derived by the bank's
independent solver, the stored answer is re-marked under today's rules, and
the pick is compared with how students who are strong in the skill answer
(pick_rate). Inside a live sitting nothing is checked until it ends. The rest
goes to a person at /admin/reports/, behind SATF_ADMIN_TOKEN.

Hooks for other sections: shell() and feed() (the shell and the inbox),
removed() and quarantined() (scoring and serving skip bad items),
after_finish() (a sitting's pending checks), delete_files() (Delete
everything), correct_key() (one fix for every student).
"""

from __future__ import annotations

import datetime as dt
import hmac
import json
import logging
import os
import pathlib
import re
import shutil
from typing import Literal

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from . import db, deps, mail, practice, progress, scoring
from .deps import now, tz_of

log = logging.getLogger("satf.reports")
router = APIRouter()

FILES = pathlib.Path(os.environ.get("SATF_REPORTS") or pathlib.Path(__file__).resolve().parent / "reports")

MB = 1 << 20
# U3's per-type caps: stills arrive downscaled in the browser; GIFs and screen
# recordings arrive as they are
CAPS = {"image/png": 10 * MB, "image/jpeg": 10 * MB, "image/webp": 10 * MB,
        "image/gif": 50 * MB, "video/webm": 50 * MB, "video/mp4": 50 * MB}
EXT = {"image/png": "png", "image/jpeg": "jpg", "image/webp": "webp", "image/gif": "gif",
       "video/webm": "webm", "video/mp4": "mp4"}
MAX_FILES = 10
MAX_TOTAL = 200 * MB
PER_HOUR, PER_DAY = 10, 20
OPEN_DISPUTES = 5
STRONG_N = 20           # strong students' answers before the signal is trusted
SIGNAL_X = 2.0          # strong students pick it this many times more than everyone
RATE_DAYS = 180
EXAMPLES = 900000       # the Library's example seeds: public, key shown, never served in practice

LABELS = {
    "key_wrong": "Answer key is wrong",
    "label": "The named mistake doesn't fit",
    "explanation": "Explanation unclear",
    "figure": "Figure or table wrong",
    "display": "Typo or display",
    "difficulty": "Difficulty label off",
    "two_right": "More than one right answer",
    "no_right": "No right answer",
    "wording": "Unclear wording",
    "definition": "Wrong or unclear definition",
    "suggest": "Suggest a better meaning or example",
    "bug": "Bug",
    "idea": "Idea",
    "confusing": "Confusing",
    "other": "Other",
}
QUESTION = ("key_wrong", "label", "explanation", "figure", "display", "difficulty",
            "two_right", "no_right", "wording", "other")
LIVE = ("two_right", "no_right", "figure", "display", "wording", "other")   # marking never shown
GENERAL = ("bug", "idea", "confusing", "display", "other")
WORD = ("definition", "two_right", "suggest", "display", "confusing", "other")
KINDS = {"question": QUESTION, "word": WORD, "sitting": GENERAL, "page": GENERAL,
         "paper": GENERAL, "catalog": GENERAL}
# about the stem, the figure or the options: always a person, never a lesson (U3)
PERSON = frozenset({"label", "figure", "display", "two_right", "no_right", "wording"})
NEEDS_DETAILS = frozenset({"bug", "other"})
ALIASES = {"wrong_key": "key_wrong", "key": "key_wrong", "wrong answer key": "key_wrong",
           "wrong mistake label": "label", "typo": "display", "general": "other",
           "general feedback": "other", "idea or request": "idea", "feature": "idea",
           "something broken": "bug", "confusing question": "confusing",
           "no right answer, or two right answers": "no_right", "figure or table is wrong": "figure",
           "another choice also fits": "two_right"}
_BY_LABEL = {v.casefold(): k for k, v in LABELS.items()}

STATUSES = {"new": "New", "checking": "Being checked", "fixed": "Fixed", "no_change": "Checked, no change"}
OPEN = ("new", "checking")
FIXED_NOTE = {"key_wrong": "Answer key corrected", "figure": "Figure or table corrected",
              "display": "Display fixed", "explanation": "Explanation rewritten",
              "label": "Mistake label rewritten", "difficulty": "Difficulty label corrected",
              "two_right": "Options corrected", "no_right": "Options corrected",
              "wording": "Wording clarified", "definition": "Definition corrected",
              "suggest": "Meaning or example improved", "bug": "Bug fixed", "confusing": "Made clearer"}

TEXT = {
    "broken": "You found a broken question. It no longer counts against you, and nobody will be served it again.",
    "unsure": "We couldn't confirm this automatically. A person will check it.",
}
OUTCOME_TEXT = {"key_wrong": "This answer no longer counts against you.",
                "key_right": "The key was right, so this answer counts again and the mistake is open."}

EMAIL_OK = re.compile(r"^[^@\s<>]+@[^@\s<>]+\.[^@\s<>]+$")
FILE_OK = re.compile(r"^\d{1,2}\.(png|jpg|webp|gif|webm|mp4)$")


# ------------------------------------------------------------------ small helpers

def _json(text) -> dict:
    try:
        return json.loads(text) if text else {}
    except ValueError:
        return {}


def _ago(**kw) -> str:
    return (dt.datetime.now(dt.timezone.utc) - dt.timedelta(**kw)).isoformat(timespec="seconds")


def _day(at: str | None) -> str:
    """'Sep 23', as every list prints a date."""
    if not at:
        return ""
    d = dt.date.fromisoformat(at[:10])
    return f"{d:%b} {d.day}"


def category_of(raw: str | None) -> str | None:
    """An id, a label or an alias ('Wrong mistake label') -> the id."""
    if raw is None:
        return None
    c = raw.strip()
    return c if c in LABELS else ALIASES.get(c.casefold()) or _BY_LABEL.get(c.casefold())


def _topic_name(slug: str | None) -> str | None:
    topics = practice.catalogue()["topics"]
    return topics[slug].name if slug in topics else slug


def sniff(head: bytes) -> str | None:
    """The type a file really is, from its first bytes."""
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if head[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if head[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return "image/webp"
    if head[:4] == b"\x1a\x45\xdf\xa3":
        return "video/webm"
    if head[4:8] == b"ftyp" and head[8:12] not in (b"heic", b"heix", b"mif1", b"msf1", b"avif"):
        return "video/mp4"
    return None


def _letter(pick) -> int | None:
    """'C', 'c' or 2 -> 2."""
    s = str(pick if pick is not None else "").strip().upper()
    if s in ("A", "B", "C", "D"):
        return "ABCD".index(s)
    return int(s) if s in ("0", "1", "2", "3") else None


def _shown(q: dict | None, given) -> str | None:
    """An answer as the student saw it: a letter, or what they typed."""
    if given is None or given == "":
        return None
    if q and q.get("type") == "mcq":
        i = _letter(given)
        return "ABCD"[i] if i is not None else str(given)
    return str(given)


def _given(q: dict, raw):
    """A stored answer as scoring reads it: an index for MC."""
    if raw is None:
        return None
    if q.get("type") == "mcq":
        try:
            return int(raw)
        except (TypeError, ValueError):
            return None
    return str(raw)


# ------------------------------------------------------------------ quarantine (U3)

def quarantined(template: str, seed: int | None = None) -> bool:
    """Stop serving: this seed, or the whole template (seed -1), until released."""
    return bool(db.one("SELECT 1 FROM quarantine WHERE template=? AND seed IN (?, -1) AND released IS NULL",
                       template, -1 if seed is None else seed))


def quarantine(template: str, seed: int | None = None, note: str = "") -> None:
    db.run("INSERT OR REPLACE INTO quarantine(template,seed,at,note,released) VALUES (?,?,?,?,NULL)",
           template, -1 if seed is None else seed, now(), note[:300])


def release(template: str, seed: int | None = None) -> bool:
    return db.run("UPDATE quarantine SET released=? WHERE template=? AND seed=? AND released IS NULL",
                  now(), template, -1 if seed is None else seed).rowcount > 0


def removed(template: str, seed: int) -> bool:
    """X10: does this item leave both right and asked wherever it was sat? A
    quarantined item, or one whose key a report showed wrong (the solver
    disagreed, or an admin confirmed it)."""
    if quarantined(template, seed):
        return True
    return bool(db.one("""SELECT 1 FROM reports WHERE template=? AND seed=? AND kind!='correction'
                          AND (json_extract(context,'$.outcome')='key_wrong'
                               OR json_extract("check",'$.outcome')='broken')""", template, seed))


# ------------------------------------------------------------------ disputes

def _dispute(a) -> int | None:
    """attempts.disputed = 1, so mastery and accuracy ignore it, and the trap
    it opened closes when no other undisputed miss holds it open. The trap's
    id, when one closed."""
    db.run("UPDATE attempts SET disputed=1 WHERE id=?", a["id"])
    if a["correct"]:
        return None
    n = a["norm"] or ""
    t = db.one("SELECT * FROM traps WHERE learner=? AND template=? AND norm=? AND closed IS NULL",
               a["learner"], a["template"], n)
    if not t:
        return None
    if db.one("SELECT 1 FROM attempts WHERE learner=? AND template=? AND COALESCE(norm,'')=? AND correct=0"
              " AND disputed=0 AND void IS NULL", a["learner"], a["template"], n):
        return None
    stamp = now()
    db.run("UPDATE traps SET closed=?, closed_how='disputed', due=NULL WHERE id=?", stamp, t["id"])
    progress.log(a["learner"], a["template"], n, "disputed", stamp, a["id"])
    return t["id"]


def _undispute(attempt_id: int, trap_ids) -> None:
    """Key was right: the answer counts again and the mistake it closed reopens."""
    db.run("UPDATE attempts SET disputed=0 WHERE id=?", attempt_id)
    stamp = now()
    for tid in trap_ids or ():
        t = db.one("SELECT * FROM traps WHERE id=? AND closed_how='disputed'", tid)
        if t:
            db.run("UPDATE traps SET closed=NULL, closed_how=NULL, owed=?, last=? WHERE id=?",
                   progress.OWED, stamp, tid)
            progress.log(t["learner"], t["template"], t["norm"], "undisputed", stamp, attempt_id)


def open_disputes(learner: str) -> int:
    return db.one("SELECT COUNT(*) AS n FROM reports WHERE learner=? AND dispute=1 AND status IN ('new','checking')",
                  learner)["n"]


def _rescore(sid: str, qid: str, report: int | None) -> bool:
    row = db.one("SELECT result FROM sessions WHERE id=? AND finished IS NOT NULL", sid)
    if not row or qid in (_json(row["result"]).get("removed") or ()):
        return False
    from . import estimate
    return estimate.rescore_sitting(sid, qid=qid, how="removed", report=report) is not None


def correct_key(template: str, seed: int | None = None, since: str | None = None,
                report: int | None = None, reporters=(), quiet=()) -> dict:
    """U3's one fix for everyone: every learner's attempts on this seed (or on
    every seed of the template since a date) are disputed for good, the traps
    only they opened close, each finished sitting holding one is re-scored
    (SR19), and every affected learner not in `quiet` gets a correction in
    their inbox. `mine` is what it did to the reporters' own attempts."""
    sql, args = f"SELECT * FROM attempts WHERE template=? AND {db.NOT_SAMPLE}", [template]
    if seed is not None:
        sql, args = sql + " AND seed=?", args + [seed]
    if since:
        sql, args = sql + " AND at>=?", args + [since]
    rows = db.rows(sql + " ORDER BY id", *args)
    reporters, quiet = set(reporters), set(quiet)
    mine = {"disputed": [], "closed": []}
    first: dict[str, str] = {}
    stamp = now()
    with db.atomic():
        for a in rows:
            if not a["disputed"]:
                closed = _dispute(a)
                if a["learner"] in reporters:
                    mine["disputed"].append(a["id"])
                    if closed:
                        mine["closed"].append(closed)
            first.setdefault(a["learner"], a["at"])
        told = {r["learner"] for r in db.rows("SELECT learner FROM reports WHERE kind='correction' AND parent=?",
                                              report)} if report else set()
        for learner, at in first.items():
            if learner in quiet or learner in told:
                continue
            text = f"A question you answered on {_day(at)} had a wrong key. It no longer counts against you."
            db.run("INSERT INTO reports(learner,kind,source,template,seed,category,title,status,reply,replied,parent,at)"
                   " VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", learner, "correction", "admin", template, seed,
                   "key_wrong", text, "fixed", text, stamp, report, stamp)
    sittings = sum(_rescore(sid, qid, report) for sid, qid in
                   sorted({(a["session"], a["qid"]) for a in rows if a["session"] and a["qid"]}))
    log.warning("template flagged %s%s (report #%s): %d attempts of %d learners, %d sittings re-scored",
                template, "" if seed is None else f" seed {seed}", report, len(rows), len(first), sittings)
    return {"attempts": len(rows), "learners": len(first), "sittings": sittings, "mine": mine}


# ------------------------------------------------------------------ the instant check (U3)

def check_item(item) -> list[str]:
    """T-bank's satbank.check.check_item: what is wrong with the item's
    structure and prose. A module-level seam, so a fixture can replace it."""
    from satbank import check
    fn = getattr(check, "check_item", None)
    if fn is not None:
        return list(fn(item))
    # ponytail: until T-bank's public check_item lands, the two private checks it wraps
    return check._structure(item, item.template, item.seed) + check._prose(item, item.template, item.seed)


def pick_rate(template: str, normalized: str | None, exclude: str | None = None,
              days: int = RATE_DAYS) -> dict:
    """The Strong-student signal: over the last 180 days of first tries on this
    template, the share that picked an option with this misconception among
    learners who are Strong in the topic now (`strong`, over `n_strong`
    answers), against everyone (`base`, over `n`). By norm, because option
    letters move between seeds."""
    # ponytail: one topic_mastery per answering learner; a nightly table if a template gets thousands
    rows = db.rows(f"SELECT learner, topic, COALESCE(norm,'') AS norm FROM attempts WHERE template=?"
                   f" AND repeat=0 AND at>=? AND learner!=? AND {db.NOT_SAMPLE}",
                   template, _ago(days=days), exclude or "")
    strong: dict[tuple, bool] = {}
    n = hit = ns = hs = 0
    for r in rows:
        key = (r["learner"], r["topic"])
        if key not in strong:
            strong[key] = progress.topic_mastery(*key) >= progress.STRONG
        picked = bool(normalized) and r["norm"] == normalized
        n, hit = n + 1, hit + picked
        if strong[key]:
            ns, hs = ns + 1, hs + picked
    return {"strong": round(hs / ns, 4) if ns else None, "base": round(hit / n, 4) if n else None,
            "n_strong": ns, "n": n}


def _pct(x: float | None) -> str:
    return f"{round(100 * (x or 0))}%"


def _forms(key: str) -> str:
    forms = scoring.accepted_forms(str(key))[:3] or [str(key)]
    return forms[0] if len(forms) == 1 else ", ".join(forms[:-1]) + " or " + forms[-1]


def instant_check(learner: str, ctx: dict, q: dict, attempt, answer) -> dict:
    """U3's outcomes, tried in order: broken, remarked, forms, unsure (the
    Strong-student signal), unsure (too few strong answers), explained,
    unsure. The first that applies wins. Only called once the key has been
    shown, so the text may name it."""
    from satbank.audit import AuditError, audit
    from satbank.registry import generate
    t, s = ctx["template"], ctx["seed"]
    base = {"at": now()}
    try:
        item = generate(t, s, verify=False)
    except Exception as e:                          # a template renamed or retired since
        return {**base, "outcome": "unsure", "text": TEXT["unsure"], "why": f"could not regenerate: {e}"}
    problems = []
    try:
        audit(item)
    except AuditError as e:
        problems.append(str(e))
    try:
        problems += check_item(item)
    except Exception as e:
        problems.append(f"check_item raised {e!r}")
    if problems:
        return {**base, "outcome": "broken", "text": TEXT["broken"], "problems": problems[:10]}

    stored = _given(q, attempt["given"]) if attempt else None
    if attempt and not attempt["correct"] and stored is not None and scoring.is_correct(q, stored):
        return {**base, "outcome": "remarked",
                "text": f"You were right. {_shown(q, stored)} is accepted, so this now counts as right."}

    mc = item.fmt == "mcq"
    pick = _shown(q, answer if answer not in (None, "") else stored)
    if not mc and pick:
        err = scoring.entry_error(pick, str(item.answer))
        if err:
            text = (f"Your {pick} is too short. Grid-ins accept {_forms(item.answer)} (the fourth-digit rule)."
                    if err == "early" else
                    f"Your {pick} is the right value, in a form the grid refuses. Grid-ins accept {_forms(item.answer)}.")
            return {**base, "outcome": "forms", "text": text, "pick": pick, "actions": ["accept", "wording", "person"]}

    reason = ""
    if mc:
        i = _letter(pick)
        reason = item.reasons[i] if i is not None and i < len(item.reasons) else ""
    elif pick:
        reason = next((m.reason for m in getattr(item, "spr_mistakes", ())
                       if scoring.grid_equal(pick, str(m.value))), "")
        if not reason and attempt and attempt["reason"] and _shown(q, stored) == pick:
            reason = attempt["reason"]
    normalized = progress.norm(reason) if reason else ""
    named = bool(normalized) and progress.named(normalized)
    rate = pick_rate(t, normalized if named else None, exclude=learner)
    solver = (f"{item.answer} ({item.choices['ABCD'.index(item.answer)]})" if mc else str(item.answer))
    topic = _topic_name(ctx.get("topic")) or "this skill"
    found = {**base, "pick": pick, "solver": solver, "reason": reason or None, "norm": normalized or None,
             "signal": rate, "rationale": item.rationale}
    slip = f"{pick} matches a known slip: {reason}." if named and pick else ""
    if named and rate["n_strong"] >= STRONG_N and rate["strong"] > SIGNAL_X * rate["base"]:
        return {**found, "outcome": "unsure", "why": "signal",
                "text": f"Our solver gets {solver} from the numbers, but students who are strong in {topic} pick"
                        f" {pick} here far more often than usual ({_pct(rate['strong'])} against"
                        f" {_pct(rate['base'])}). That points to the wording or the options. A person will"
                        f" check it, and it doesn't count against you meanwhile."}
    if rate["n_strong"] < STRONG_N:
        return {**found, "outcome": "unsure", "why": "thin", "actions": ["accept", "wording", "person"],
                "text": " ".join(x for x in (
                    f"The numbers check out with our independent solver: it also gets {solver}.", slip,
                    "Too few strong students have answered this kind of question for us to rule out a"
                    " wording problem, so a person will check it.") if x)}
    if mc and named:
        return {**found, "outcome": "explained", "actions": ["accept", "wording", "person"],
                "text": f"The numbers check out with our independent solver: it also gets {solver}."
                        f" {pick} matches a known slip: {reason}, and students who are strong in {topic}"
                        f" rarely pick it. If the wording, the figure or the options are what's wrong,"
                        f" send it to a person."}
    return {**found, "outcome": "unsure", "why": "none", "text": TEXT["unsure"]}


# ------------------------------------------------------------------ context, from the server's own records

class ReportIn(BaseModel):
    model_config = ConfigDict(extra="ignore")
    kind: Literal["question", "sitting", "page", "word", "paper", "catalog"] | None = None
    source: str = Field("page", max_length=20, pattern=r"^[a-z_]+$")
    category: str | None = Field(None, max_length=80)
    title: str = Field("", max_length=200)
    answer: str | None = Field(None, max_length=40)
    details: str = Field("", max_length=5000)
    email: str | None = Field(None, max_length=200)
    session: str | None = Field(None, max_length=80)
    question_id: str | None = Field(None, max_length=80)
    day: str | None = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    page: str | None = Field(None, max_length=300)
    word: str | None = Field(None, max_length=80)
    paper: str | None = Field(None, max_length=40)
    template: str | None = Field(None, max_length=120)
    seed: int | None = Field(None, ge=0)
    device: dict | None = None
    dispute: bool = False
    include_answer: bool = False
    parent: int | None = None


def _revealed(learner: str, template: str, seed: int) -> bool:
    """Has this learner been shown the item's key (R19)?"""
    return seed >= EXAMPLES or deps.access(learner, template, seed) == "reveal"


def _live(row) -> bool:
    """A sitting that must not show marking: an unfinished test, challenge,
    contest or end-mode set."""
    if row is None or row["finished"] or row["abandoned"]:
        return False
    return (row["kind"] in deps.TEST_KINDS or row["kind"] == "challenge" or bool(row["contest"])
            or _json(row["cfg"]).get("feedback") == "end")


def _paper(row) -> list[dict]:
    """A sitting's questions in order; a fresh mock or a module keeps them by module."""
    p = deps.paper_of(row) if row else []
    if isinstance(p, dict):
        p = [q for k in sorted(p) if isinstance(p[k], list) for q in p[k]]
    return [q for q in p if isinstance(q, dict)]


def _from_bank(template: str, seed: int) -> dict:
    from satbank.registry import generate, topic_of
    item = generate(template, seed)
    return practice.to_question(practice.Card.of(template, seed, item, topic_of(template)), 1)


def _question(learner: str, body: ReportIn, tz: int):
    """(the stored question, its session row, the session id): a session the
    learner owns, the question of the day, the day's challenge, or an address
    this learner has been shown (a saved item, a Library example)."""
    sid, row = body.session, None
    if body.source == "qotd" or (sid or "").startswith("qotd:"):
        from . import daily
        day = body.day or (sid[5:] if sid and sid.startswith("qotd:") else daily.today(tz))
        return daily.question(day), None, f"qotd:{day}"
    if sid:
        row = deps.mine(deps.session_or_404(sid), learner)
        q = next((x for x in _paper(row) if x.get("id") == body.question_id), None)
        if q is None:
            raise HTTPException(404, "no such question in that session")
        return q, row, sid
    if body.source == "challenge" and body.day and body.question_id:
        got = db.one("SELECT questions FROM challenges WHERE day=?", body.day)
        q = next((x for x in json.loads(got["questions"]) if x.get("id") == body.question_id), None) if got else None
        if q is None:
            raise HTTPException(404, "no such challenge question")
        return q, None, None
    if body.template and body.seed is not None:
        # the Library's public examples, or an item this learner was shown
        if body.seed < EXAMPLES and deps.access(learner, body.template, body.seed) is None:
            raise HTTPException(403, "that question hasn't been shown to you")
        try:
            return _from_bank(body.template, body.seed), None, None
        except KeyError:
            raise HTTPException(404, "no such template") from None
        except Exception:
            raise HTTPException(422, "that question can't be made") from None
    raise HTTPException(422, "say which question: session and question_id, the day, or template and seed")


def _context(learner: str, kind: str, body: ReportIn, tz: int) -> tuple[dict, dict | None, object]:
    """(context, the stored question, the learner's first attempt at it)."""
    ctx: dict = {}
    q = attempt = None
    if kind in ("question", "word") and (body.session or body.template or body.source in ("qotd", "challenge")):
        q, row, sid = _question(learner, body, tz)
        t, s = q["key"], q["seed"]
        hidden = _live(row) or not _revealed(learner, t, s)      # marking not shown yet
        if sid:
            attempt = db.one("SELECT * FROM attempts WHERE learner=? AND session=? AND qid=? ORDER BY id LIMIT 1",
                             learner, sid, q["id"])
        else:
            attempt = db.one("SELECT * FROM attempts WHERE learner=? AND template=? AND seed=? ORDER BY id DESC LIMIT 1",
                             learner, t, s)
        given = db.load_answers(row).get(q["id"]) if row else None
        if given is None and attempt:
            given = _given(q, attempt["given"])
        paper = _paper(row)
        n = next((i for i, x in enumerate(paper, 1) if x.get("id") == q["id"]), None)
        ctx.update({"template": t, "seed": s, "topic": q.get("topic"), "topic_name": q.get("topic_name") or _topic_name(q.get("topic")),
                    "skill": practice.skill_of(q), "difficulty": q.get("difficulty"), "fmt": q.get("type"),
                    "subject": deps.subject_of(t), "qid": q["id"], "session": sid, "revealed": not hidden,
                    "live": bool(_live(row)), "day": body.day or (sid[5:] if sid and sid.startswith("qotd:") else None),
                    "sitting_kind": row["kind"] if row else None, "attempt": attempt["id"] if attempt else None,
                    "correct": scoring.is_correct(q, given) if given is not None else None})
        if n:
            ctx.update({"n": n, "of": len(paper)})
        if given is not None and (not hidden or body.include_answer):
            ctx["given"] = _shown(q, given)
        if not hidden and given is not None:
            ctx["marked"] = "right" if ctx["correct"] else "wrong"
        if attempt and attempt["norm"]:
            ctx["norm"] = attempt["norm"]
    if kind == "word":
        if not (body.word or q):
            raise HTTPException(422, "say which word")
        ctx["word"] = body.word
    elif kind == "question" and q is None:
        raise HTTPException(422, "say which question: session and question_id, the day, or template and seed")
    elif kind == "sitting":
        if not body.session:
            raise HTTPException(422, "say which sitting")
        row = deps.mine(deps.session_or_404(body.session), learner)
        est = _json(row["result"]).get("estimate") or {}
        ctx.update({"session": row["id"], "sitting": {
            "kind": row["kind"], "date": (row["finished"] or row["started"] or "")[:10],
            "band": f"{est['low']}–{est['high']}" if est.get("low") is not None else None,
            "number": row["number"], "finished": bool(row["finished"])}})
    elif kind == "paper":
        if not body.paper:
            raise HTTPException(422, "say which paper")
        got = db.one("SELECT label FROM papers WHERE n=?", body.paper) if body.paper.isdigit() else None
        ctx.update({"paper": body.paper, "paper_label": got["label"] if got else None})
    if kind in ("page", "catalog", "paper", "sitting"):
        ctx["page"] = body.page or ("/tests/" if kind in ("catalog", "paper") else None)
    return ctx, q, attempt


def _kind_of(body: ReportIn) -> str:
    return body.kind or ("question" if body.session and body.question_id or body.template
                         or body.source in ("qotd", "challenge") else "page")


def _chip(kind: str, ctx: dict) -> str:
    if ctx.get("template"):
        return ctx.get("skill") or ctx.get("topic_name") or ctx["template"]
    if kind == "word":
        return ctx.get("word") or "Words"
    if kind == "paper":
        return ctx.get("paper_label") or f"Paper {ctx.get('paper')}"
    if kind == "catalog":
        return "Tests"
    if kind == "sitting":
        s = ctx.get("sitting") or {}
        return " · ".join(x for x in (str(s.get("kind") or "sitting").capitalize(), s.get("date")) if x)
    return ctx.get("page") or "Feedback"


def _allowed(kind: str, ctx: dict) -> tuple:
    """The categories open now: a question's depend on whether its marking
    has been shown; a word quiz item has both lists."""
    base = () if kind == "question" else KINDS[kind]
    if ctx.get("template"):
        base = tuple(dict.fromkeys(base + (QUESTION if ctx.get("revealed") else LIVE)))
    return base


# ------------------------------------------------------------------ files

def _safe_name(name: str | None) -> str:
    return re.sub(r"[^\w.\- ]", "_", pathlib.Path(name or "file").name)[:100] or "file"


def _check_files(files) -> list[dict]:
    """Every file's real type (415) and size (413, naming the file and its
    limit), before anything is written."""
    if len(files) > MAX_FILES:
        raise HTTPException(400, f"Up to {MAX_FILES} files.")
    out, total = [], 0
    for f in files:
        fh = f.file
        fh.seek(0)
        head = fh.read(16)
        fh.seek(0, os.SEEK_END)
        size = fh.tell()
        fh.seek(0)
        name = _safe_name(f.filename)
        kind = sniff(head)
        if kind is None:
            raise HTTPException(415, {"file": name, "types": sorted(CAPS)})
        if size > CAPS[kind]:
            raise HTTPException(413, {"file": name, "limit": CAPS[kind]})
        total += size
        if total > MAX_TOTAL:
            raise HTTPException(413, {"file": name, "limit": MAX_TOTAL})
        out.append({"fh": fh, "type": kind, "size": size, "name": name})
    return out


def _store(rid: int, uploads: list[dict]) -> list[dict]:
    """Copied in 1 MB chunks to server/reports/{id}/, stopped past the cap."""
    if not uploads:
        return []
    folder = FILES / str(rid)
    folder.mkdir(parents=True, exist_ok=True)
    meta = []
    for i, u in enumerate(uploads, 1):
        path, cap, got = folder / f"{i}.{EXT[u['type']]}", CAPS[u["type"]], 0
        with path.open("wb") as out:
            while chunk := u["fh"].read(MB):
                got += len(chunk)
                if got > cap:
                    raise HTTPException(413, {"file": u["name"], "limit": cap})
                out.write(chunk)
        meta.append({"file": path.name, "name": u["name"], "type": u["type"], "size": got})
    return meta


def delete_files(learner: str) -> int:
    """Delete everything (S1): this learner's report folders go with the rows."""
    n = 0
    for r in db.rows("SELECT id FROM reports WHERE learner=?", learner):
        folder = FILES / str(r["id"])
        if folder.is_dir():
            shutil.rmtree(folder, ignore_errors=True)
            n += 1
    return n


# ------------------------------------------------------------------ POST /api/report

def _rate(learner: str) -> None:
    got = db.one("SELECT SUM(at>=?) AS hour, COUNT(*) AS day FROM reports WHERE learner=? AND kind!='correction'"
                 " AND at>=?", _ago(hours=1), learner, _ago(days=1))
    if (got["hour"] or 0) >= PER_HOUR:
        raise HTTPException(429, "That's a lot of reports in an hour. Try again later.")
    if (got["day"] or 0) >= PER_DAY:
        raise HTTPException(429, "That's a lot of reports today. Try again tomorrow.")


def _root(rid: int):
    r = db.one("SELECT * FROM reports WHERE id=? AND kind!='correction'", rid)
    if r and r["parent"]:
        r = db.one("SELECT * FROM reports WHERE id=?", r["parent"])
    return r


def _save(rid: int, **cols) -> None:
    for k in ("context", "check"):
        if k in cols and not isinstance(cols[k], (str, type(None))):
            cols[k] = json.dumps(cols[k], ensure_ascii=False)
    sets = ", ".join('"%s"=?' % k for k in cols)
    db.run(f"UPDATE reports SET {sets} WHERE id=?", *cols.values(), rid)


def create(learner: str, body: ReportIn, files, tz: int = 0) -> dict:
    uploads = _check_files(files)
    _rate(learner)
    category = category_of(body.category)
    parent = None
    if body.parent is not None:
        parent = _root(body.parent)
        if parent is None or parent["status"] not in OPEN:
            raise HTTPException(409, "that report is closed; send a new one")
        category = category or parent["category"]
    kind = _kind_of(body)
    ctx, q, attempt = _context(learner, kind, body, tz)
    if parent is not None and parent["template"] and parent["template"] != ctx.get("template"):
        raise HTTPException(409, "that report is about another question")
    allowed = _allowed(kind, ctx)
    if category not in set(KINDS[kind]) | set(QUESTION if ctx.get("template") else ()):
        raise HTTPException(422, {"category": body.category, "allowed": list(allowed)})
    if category not in allowed:
        raise HTTPException(409, "Marking isn't shown in a live sitting, so the key can't be disputed yet."
                            if category == "key_wrong" else "that category isn't open here")
    if category in NEEDS_DETAILS and not body.details.strip():
        raise HTTPException(422, "Say what happened in the details.")
    if body.dispute:
        if category != "key_wrong" or not ctx.get("revealed"):
            raise HTTPException(409, "only an answer key you have seen can be disputed")
        if open_disputes(learner) >= OPEN_DISPUTES:
            raise HTTPException(409, f"You have {OPEN_DISPUTES} answers waiting to be checked.")
    email = (body.email or "").strip() or None
    if email and not EMAIL_OK.match(email):
        raise HTTPException(422, "that email doesn't look right")
    device = json.dumps(body.device, ensure_ascii=False)[:8000] if body.device else None
    title = " ".join(body.title.split()) or (
        f"{ctx['topic_name']} · Question {ctx['n']}" if ctx.get("n") and ctx.get("topic_name") else LABELS[category])
    stamp = now()
    rid = db.run("INSERT INTO reports(learner,kind,source,session,qid,paper,word,template,seed,category,title,answer,"
                 "given,details,context,device,email,files,dispute,at,status,parent) VALUES"
                 " (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                 learner, kind, body.source, ctx.get("session"), ctx.get("qid"), ctx.get("paper"), ctx.get("word"),
                 ctx.get("template"), ctx.get("seed"), category, title, (body.answer or "").strip() or None,
                 ctx.get("given"), body.details.strip() or None, json.dumps(ctx, ensure_ascii=False), device,
                 email, "[]", 0, stamp, "new", parent["id"] if parent else None).lastrowid
    try:
        meta = _store(rid, uploads)
    except BaseException:
        shutil.rmtree(FILES / str(rid), ignore_errors=True)
        db.run("DELETE FROM reports WHERE id=?", rid)
        raise
    if meta:
        db.run("UPDATE reports SET files=? WHERE id=?", json.dumps(meta), rid)
    out = _after(learner, rid, kind, category, ctx, q, attempt, body, parent)
    log.warning("report #%d %s %s", rid, category,
                f"{ctx['template']} seed {ctx['seed']}" if ctx.get("template") else ctx.get("page") or kind)
    if kind == "word" and category == "two_right":
        hook = deps.part("words", "on_report")        # W18's auto-guard, S9's
        if hook is not None:
            hook(dict(db.one("SELECT * FROM reports WHERE id=?", rid)))
    to = os.environ.get("SATF_REPORTS_TO")
    if to:
        mail.send_report_notice(to, _full(db.one("SELECT * FROM reports WHERE id=?", rid)))
    return out


def _after(learner, rid, kind, category, ctx, q, attempt, body, parent) -> dict:
    """What the report does, once it is stored: the instant check and its
    outcome, the student's dispute, or a check held until the sitting ends."""
    out = {"id": rid, "status": "new"}
    if not ctx.get("template"):
        return {**out, "thanks": True}
    if not ctx.get("revealed"):
        ctx["pending"] = True                       # checked when the sitting ends (after_finish)
        _save(rid, context=ctx)
        return {**out, "thanks": True}
    dispute = False
    status = "new"
    if parent is not None:                          # me too: the first report's check stands for both
        chk = None
    else:
        chk = instant_check(learner, ctx, q, attempt, body.answer)
        if chk["outcome"] == "broken":
            _broken(rid, ctx, learner)
        elif category == "key_wrong" and chk["outcome"] == "remarked" and attempt:
            ctx["remarked"] = progress.remark(learner, attempt["id"])
            ctx["closed_how"] = "auto"
            status = "fixed"
        elif category == "key_wrong" and chk.get("why") == "signal" and attempt and not attempt["disputed"]:
            _hold(ctx, attempt)
        if category == "key_wrong" and chk["outcome"] in ("forms", "explained"):
            ctx["awaiting"] = True                  # the student's three buttons decide
    if body.dispute and attempt and not attempt["disputed"] and not ctx.get("disputed") \
            and not ctx.get("awaiting") and status != "fixed":
        _hold(ctx, attempt)
        dispute = True
    _save(rid, context=ctx, check=chk, status=status, dispute=int(dispute))
    out["status"] = status
    if category == "key_wrong" and chk is not None:
        out["check"] = _student_check(chk)
    else:
        out["thanks"] = True
    if dispute:
        out["disputed"] = True
    return out


def _hold(ctx: dict, attempt) -> None:
    """Don't count this answer while the report is open."""
    closed = _dispute(db.one("SELECT * FROM attempts WHERE id=?", attempt["id"]))
    ctx["disputed"] = sorted(set(ctx.get("disputed") or ()) | {attempt["id"]})
    if closed:
        ctx["closed_traps"] = sorted(set(ctx.get("closed_traps") or ()) | {closed})
        ctx["closed_trap"] = ctx["closed_traps"][0]


def _broken(rid: int, ctx: dict, learner: str) -> None:
    """The solver or the item checks disagree: nobody is served it again, and
    no one's answer to it counts (U3 outcome 1)."""
    quarantine(ctx["template"], ctx["seed"], f"report #{rid}: broken")
    res = correct_key(ctx["template"], ctx["seed"], report=rid, reporters=(learner,), quiet=(learner,))
    ctx["disputed"] = sorted(set(ctx.get("disputed") or ()) | set(res["mine"]["disputed"]))
    if res["mine"]["closed"]:
        ctx["closed_traps"] = sorted(set(ctx.get("closed_traps") or ()) | set(res["mine"]["closed"]))
        ctx["closed_trap"] = ctx["closed_traps"][0]
    ctx["rescored"] = res["sittings"]
    ctx["corrected"] = {k: res[k] for k in ("attempts", "learners", "sittings")}


def _student_check(chk: dict) -> dict:
    keep = ("outcome", "text", "pick", "solver", "reason", "rationale", "actions")
    return {k: chk[k] for k in keep if chk.get(k) is not None}


@router.post("/api/report")
async def post_report(request: Request, x_learner: str | None = Header(default=None),
                      x_tz: int = Depends(tz_of)) -> dict:
    learner = deps.writer_of(x_learner)
    _rate(learner)
    size = request.headers.get("content-length", "")
    body_limit = MAX_TOTAL + MB  # multipart boundaries and the JSON field
    if size.isdigit() and int(size) > body_limit:
        raise HTTPException(413, {"file": None, "limit": MAX_TOTAL})
    received = 0
    receive = request.receive

    async def bounded_receive():
        nonlocal received
        message = await receive()
        if message["type"] == "http.request":
            received += len(message.get("body", b""))
            if received > body_limit:
                raise HTTPException(413, {"file": None, "limit": MAX_TOTAL})
        return message

    # The parser only sees chunks after the stream gate, including when the
    # client omits Content-Length or sends a false one.
    bounded = Request(request.scope, receive=bounded_receive)
    form = await bounded.form(max_files=MAX_FILES, max_fields=50)
    try:
        raw = form.get("data") or "{}"
        if hasattr(raw, "read"):
            raw = (await raw.read()).decode("utf-8", "replace")
        try:
            body = ReportIn.model_validate_json(raw)
        except ValidationError as e:
            raise HTTPException(422, json.loads(e.json(include_url=False))) from None
        files = [f for f in form.getlist("files") + form.getlist("files[]") if hasattr(f, "file")]
        return await run_in_threadpool(create, learner, body, files, x_tz)
    finally:
        await form.close()


# ------------------------------------------------------------------ the student's side

def _visible(r, ctx: dict) -> bool:
    """May the student see the item's address now? Not while it is live."""
    if ctx.get("revealed"):
        return True
    return bool(r["template"]) and _revealed(r["learner"], r["template"], r["seed"])


def _others(rid: int) -> int:
    return db.one("SELECT COUNT(*) AS n FROM reports WHERE parent=? AND kind!='correction'", rid)["n"]


def public(r) -> dict:
    """A report as its sender sees it (Settings › Your reports, the players' tags)."""
    ctx, chk = _json(r["context"]), _json(r["check"])
    out = {"id": r["id"], "at": r["at"], "date": _day(r["at"]), "kind": r["kind"], "source": r["source"],
           "category": r["category"], "category_label": LABELS.get(r["category"], r["category"]),
           "title": r["title"], "details": r["details"], "context_chip": _chip(r["kind"], ctx),
           "status": r["status"], "status_label": STATUSES.get(r["status"], r["status"]),
           "reply": r["reply"], "replied": r["replied"], "replied_date": _day(r["replied"]),
           "unread": bool(r["replied"]) and not r["seen"], "dispute": bool(r["dispute"]),
           "parent": r["parent"], "others": _others(r["parent"] or r["id"]),
           "files": len(json.loads(r["files"] or "[]")),
           "session": r["session"], "qid": r["qid"], "word": r["word"], "paper": r["paper"],
           "page": ctx.get("page"), "day": ctx.get("day"), "outcome": ctx.get("outcome"),
           "outcome_text": None, "check": None}
    if _visible(r, ctx):
        out.update({"template": r["template"], "seed": r["seed"]})
    if ctx.get("outcome") in OUTCOME_TEXT and (r["dispute"] or ctx.get("disputed")):
        text = OUTCOME_TEXT[ctx["outcome"]]
        if ctx["outcome"] == "key_right" and not ctx.get("closed_traps"):
            text = "The key was right, so this answer counts again."
        if ctx.get("rescored"):
            n = ctx["rescored"]
            text += f" Your report re-scored {n} sitting{'s' if n != 1 else ''}."
        out["outcome_text"] = text
    elif ctx.get("rescored"):
        n = ctx["rescored"]
        out["outcome_text"] = f"Your report re-scored {n} sitting{'s' if n != 1 else ''}."
    if chk and r["category"] == "key_wrong" and ctx.get("revealed"):
        out["check"] = _student_check(chk)
    return out


def run_pending(learner: str, session: str | None = None) -> int:
    """Reports sent from a live sitting are checked once it has ended (U3); an
    inbox item 'Report #n checked' follows (feed())."""
    sql = ("SELECT * FROM reports WHERE learner=? AND json_extract(context,'$.pending')=1"
           + (" AND session=?" if session else ""))
    n = 0
    for r in db.rows(sql, learner, *([session] if session else [])):
        ctx = _json(r["context"])
        row = db.one("SELECT * FROM sessions WHERE id=?", r["session"]) if r["session"] else None
        if _live(row) or not _revealed(learner, r["template"], r["seed"]):
            continue
        q = next((x for x in _paper(row) if x.get("id") == r["qid"]), None)
        try:
            q = q or _from_bank(r["template"], r["seed"])
        except Exception:
            q = None
        attempt = db.one("SELECT * FROM attempts WHERE learner=? AND template=? AND seed=? ORDER BY id LIMIT 1",
                         learner, r["template"], r["seed"])
        chk = instant_check(learner, ctx, q, attempt, r["answer"] or r["given"]) if q else \
            {"at": now(), "outcome": "unsure", "why": "could not regenerate", "text": TEXT["unsure"]}
        ctx.update({"pending": False, "revealed": True, "checked_at": now(),
                    "attempt": attempt["id"] if attempt else ctx.get("attempt")})
        if chk["outcome"] == "broken":
            _broken(r["id"], ctx, learner)
        _save(r["id"], context=ctx, check=chk)
        n += 1
    return n


def after_finish(sid: str) -> int:
    """For the sitting's finish (S4, S5): run its reports' held checks now."""
    row = db.one("SELECT learner FROM sessions WHERE id=?", sid)
    return run_pending(row["learner"], sid) if row and row["learner"] else 0


@router.get("/api/reports")
def my_reports(x_learner: str | None = Header(default=None)) -> list[dict]:
    learner = deps.learner_of(x_learner)
    run_pending(learner)
    return [public(r) for r in db.rows("SELECT * FROM reports WHERE learner=? AND kind!='correction'"
                                       " ORDER BY id DESC LIMIT 200", learner)]


@router.post("/api/reports/seen")
def seen(x_learner: str | None = Header(default=None)) -> dict:
    learner = deps.writer_of(x_learner)
    n = db.run("UPDATE reports SET seen=? WHERE learner=? AND replied IS NOT NULL AND seen IS NULL",
               now(), learner).rowcount
    return {"seen": n}


def _own(rid: int, learner: str):
    r = db.one("SELECT * FROM reports WHERE id=? AND kind!='correction'", rid)
    if r is None or r["learner"] != learner:
        raise HTTPException(404, "no such report")
    return r


@router.post("/api/reports/{rid}/accept")
def accept(rid: int, x_learner: str | None = Header(default=None)) -> dict:
    """That makes sense: closed as Checked, no change, using no dispute slot."""
    r = _own(rid, deps.writer_of(x_learner))
    if r["status"] not in OPEN:
        raise HTTPException(409, "that report is already closed")
    ctx = _json(r["context"])
    for aid in ctx.get("disputed") or ():
        _undispute(aid, ctx.get("closed_traps"))
    ctx.update({"accepted": now(), "awaiting": False, "disputed": []})
    _save(rid, context=ctx, status="no_change", dispute=0)
    return public(db.one("SELECT * FROM reports WHERE id=?", rid))


class Escalate(BaseModel):
    category: str = Field("key_wrong", max_length=80)
    dispute: bool = False
    details: str | None = Field(None, max_length=5000)


@router.post("/api/reports/{rid}/escalate")
def escalate(rid: int, body: Escalate, x_learner: str | None = Header(default=None)) -> dict:
    """The wording or figure is wrong / Still wrong: send it to a person, with
    the check attached and, if ticked, the answer not counted meanwhile."""
    learner = deps.writer_of(x_learner)
    r = _own(rid, learner)
    ctx = _json(r["context"])
    category = category_of(body.category)
    if r["status"] not in OPEN:
        raise HTTPException(409, "that report is already closed")
    if category not in QUESTION or not ctx.get("revealed"):
        raise HTTPException(422, {"category": body.category, "allowed": list(QUESTION)})
    dispute = bool(r["dispute"])
    if body.dispute and category == "key_wrong" and not ctx.get("disputed"):
        if open_disputes(learner) >= OPEN_DISPUTES:
            raise HTTPException(409, f"You have {OPEN_DISPUTES} answers waiting to be checked.")
        attempt = db.one("SELECT * FROM attempts WHERE id=?", ctx.get("attempt") or 0)
        if attempt is None:
            raise HTTPException(409, "there is no answer of yours to set aside")
        _hold(ctx, attempt)
        dispute = True
    ctx.update({"escalated": now(), "awaiting": False})
    details = "\n\n".join(x for x in (r["details"], (body.details or "").strip()) if x) or None
    _save(rid, context=ctx, category=category, status="new", dispute=int(dispute), details=details)
    return public(db.one("SELECT * FROM reports WHERE id=?", rid))


@router.get("/api/reports/similar")
def similar(session: str | None = None, qid: str | None = None, day: str | None = None,
            source: str | None = None, template: str | None = None, seed: int | None = None,
            category: str | None = None, x_learner: str | None = Header(default=None),
            x_tz: int = Depends(tz_of)) -> dict:
    """Me too (U3): an open report on the same (template, seed), or on the same
    template and category in the last 30 days, from someone else."""
    learner = deps.learner_of(x_learner)
    try:
        body = ReportIn(session=session, question_id=qid, day=day, source=source or "page",
                        template=template, seed=seed)
    except ValidationError as e:
        raise HTTPException(422, json.loads(e.json(include_url=False))) from None
    q, _, _ = _question(learner, body, x_tz)
    return _similar(learner, q["key"], q["seed"], category_of(category))


def _similar(learner: str, t: str, s: int, cat: str | None) -> dict:
    roots = db.rows("SELECT * FROM reports WHERE parent IS NULL AND kind!='correction' AND status IN ('new','checking')"
                    " AND template=? AND (seed=? OR (category=? AND at>=?)) ORDER BY seed=? DESC, id",
                    t, s, cat or "", _ago(days=30), s)
    if not roots:
        return {"open": 0}
    top = roots[0]
    ids = [r["id"] for r in roots]
    marks = ",".join("?" for _ in ids)
    everyone = {r["learner"] for r in db.rows(f"SELECT learner FROM reports WHERE (id IN ({marks})"
                                              f" OR parent IN ({marks})) AND kind!='correction'", *ids, *ids)}
    return {"open": len(everyone - {learner}), "id": top["id"], "status": top["status"],
            "status_label": STATUSES[top["status"]], "category": top["category"],
            "category_label": LABELS.get(top["category"], top["category"]), "mine": learner in everyone}


@router.get("/api/reports/fixed")
def fixed() -> list[dict]:
    """Help › Fixed from your reports: the last 30 fixes, with no names."""
    out = []
    for r in db.rows("SELECT * FROM reports WHERE status='fixed' AND parent IS NULL AND kind!='correction'"
                     " ORDER BY COALESCE(replied, at) DESC LIMIT 30"):
        ctx = _json(r["context"])
        out.append({"date": _day(r["replied"] or r["at"]), "at": (r["replied"] or r["at"])[:10],
                    "chip": _chip(r["kind"], ctx),
                    "change": ctx.get("fixed_note") or FIXED_NOTE.get(r["category"], "Fixed"),
                    "reports": 1 + _others(r["id"])})
    return out


@router.get("/api/reports/categories")
def categories() -> dict:
    """The one list report.js draws its chips and limits from."""
    return {"labels": LABELS,
            "kinds": {k: {"revealed": list(v), "live": list(LIVE if k == "question" else v)} for k, v in KINDS.items()},
            "person": sorted(PERSON), "needs_details": sorted(NEEDS_DETAILS), "statuses": STATUSES,
            "limits": LIMITS}


LIMITS = {"files": MAX_FILES, "types": CAPS, "total": MAX_TOTAL, "per_hour": PER_HOUR, "per_day": PER_DAY,
          "disputes": OPEN_DISPUTES, "title": 200, "details": 5000, "answer": 40, "downscale": 2000,
          "record_seconds": 60}
# what the modal's "Sent with this" box may show: never the key, and marking only once shown
BOX = ("template", "seed", "topic_name", "skill", "difficulty", "fmt", "subject", "qid", "session", "revealed",
       "live", "day", "sitting_kind", "n", "of", "given", "marked", "word", "paper", "paper_label", "sitting", "page")


@router.get("/api/reports/context")
def report_context(kind: str | None = None, source: str = "page", session: str | None = None,
                   question_id: str | None = None, day: str | None = None, template: str | None = None,
                   seed: int | None = None, word: str | None = None, paper: str | None = None,
                   page: str | None = None, category: str | None = None,
                   x_learner: str | None = Header(default=None), x_tz: int = Depends(tz_of)) -> dict:
    """What a report from here would send, resolved the way POST /api/report
    resolves it (the modal's "Sent with this" box), the categories open now,
    the reply-to email on file, the open disputes and, outside a live
    sitting, me too. The student's own answer comes back so the box can offer
    "Include my answer"; the key and hidden marking never do."""
    learner = deps.learner_of(x_learner)
    try:
        body = ReportIn(kind=kind, source=source, session=session, question_id=question_id, day=day,
                        template=template, seed=seed, word=word, paper=paper, page=page, include_answer=True)
    except ValidationError as e:
        raise HTTPException(422, json.loads(e.json(include_url=False))) from None
    kind = _kind_of(body)
    ctx, _, _ = _context(learner, kind, body, x_tz)
    allowed = list(_allowed(kind, ctx))
    cat = category_of(category)
    email = (db.one("SELECT email FROM reports WHERE learner=? AND email IS NOT NULL ORDER BY id DESC LIMIT 1", learner)
             or db.one("SELECT email FROM users WHERE learner=? AND email IS NOT NULL"
                       " ORDER BY verified DESC, created LIMIT 1", learner))
    out = {"kind": kind, "chip": _chip(kind, ctx), "box": {k: ctx[k] for k in BOX if ctx.get(k) is not None},
           "allowed": allowed, "category": cat if cat in allowed else None,
           "title": f"{ctx['topic_name']} · Question {ctx['n']}" if ctx.get("n") and ctx.get("topic_name") else None,
           "email": email["email"] if email else None, "open_disputes": open_disputes(learner),
           "labels": LABELS, "person": sorted(PERSON), "needs_details": sorted(NEEDS_DETAILS), "limits": LIMITS,
           "similar": None}
    if ctx.get("template") and not ctx.get("live"):
        out["similar"] = _similar(learner, ctx["template"], ctx["seed"], out["category"])
    return out


def shell(learner: str) -> dict:
    """For /api/shell (F2): the newest report and the unread replies."""
    r = db.one("SELECT id, at, status, replied, seen FROM reports WHERE learner=? AND kind!='correction'"
               " ORDER BY id DESC LIMIT 1", learner)
    n = db.one("SELECT COUNT(*) AS n FROM reports WHERE learner=? AND kind!='correction' AND replied IS NOT NULL"
               " AND seen IS NULL", learner)["n"]
    newest = {"id": r["id"], "at": r["at"], "status": r["status"],
              "unread": bool(r["replied"]) and not r["seen"]} if r else None
    return {"newest_report": newest, "report_replies": n}


def feed(learner: str, since: str | None = None, limit: int = 50) -> list[dict]:
    """For the inbox (S1's feed, U25): replies, held checks that ran, and
    corrections from another student's report."""
    items = []
    for r in db.rows("SELECT * FROM reports WHERE learner=? AND (replied IS NOT NULL"
                     " OR json_extract(context,'$.checked_at') IS NOT NULL) ORDER BY id DESC LIMIT ?", learner, limit):
        ctx = _json(r["context"])
        if r["kind"] == "correction":
            items.append({"kind": "correction", "at": r["replied"], "id": r["id"], "title": r["title"],
                          "href": "/review/", "unread": not r["seen"]})
            continue
        if r["replied"]:
            items.append({"kind": "report_reply", "at": r["replied"], "id": r["id"],
                          "title": f"Report #{r['id']} answered", "href": "/me/settings/#reports",
                          "unread": not r["seen"]})
        if ctx.get("checked_at"):
            items.append({"kind": "report_checked", "at": ctx["checked_at"], "id": r["id"],
                          "title": f"Report #{r['id']} checked", "href": "/me/settings/#reports"})
    items = [x for x in items if not since or x["at"] > since]
    return sorted(items, key=lambda x: x["at"], reverse=True)[:limit]


# ------------------------------------------------------------------ admin (§10)

def admin(x_admin: str | None = Header(default=None)) -> None:
    want = os.environ.get("SATF_ADMIN_TOKEN")
    if not want:
        raise HTTPException(404, "Not Found")
    if not x_admin or not hmac.compare_digest(x_admin.encode(), want.encode()):
        raise HTTPException(403, "wrong admin token")


def _rank(r, ctx: dict, chk: dict) -> int | None:
    """Where an open report sorts in admin: broken, the Strong-student signal,
    then everything waiting for a person. None: not flagged."""
    if r["status"] not in OPEN or ctx.get("awaiting"):
        return None
    if chk.get("outcome") == "broken":
        return 0
    if chk.get("why") == "signal":
        return 1
    if chk.get("outcome") == "unsure" or r["dispute"] or ctx.get("escalated"):
        return 2
    return None


def _files(r) -> list[dict]:
    return [{**f, "url": f"/api/admin/files/{r['id']}/{f['file']}"} for f in json.loads(r["files"] or "[]")]


def _row(r) -> dict:
    ctx, chk = _json(r["context"]), _json(r["check"])
    sig = chk.get("signal") or {}
    return {"id": r["id"], "at": r["at"], "date": _day(r["at"]), "kind": r["kind"], "source": r["source"],
            "category": r["category"], "category_label": LABELS.get(r["category"], r["category"]),
            "summary": r["title"], "context_chip": _chip(r["kind"], ctx), "status": r["status"],
            "dispute": bool(r["dispute"]), "disputed": bool(ctx.get("disputed")), "template": r["template"],
            "seed": r["seed"], "check": chk.get("outcome"), "why": chk.get("why"),
            "signal": (f"strong {_pct(sig['strong'])} vs base {_pct(sig['base'])}, n {sig['n_strong']}"
                       if chk.get("why") == "signal" else None),
            "awaiting": bool(ctx.get("awaiting")), "pending": bool(ctx.get("pending")),
            "children": _others(r["id"]), "files": len(json.loads(r["files"] or "[]")),
            "replied": r["replied"], "rank": _rank(r, ctx, chk)}


def _full(r) -> dict:
    ctx, chk = _json(r["context"]), _json(r["check"])
    return {**_row(r), "title": r["title"], "details": r["details"], "answer": r["answer"], "given": r["given"],
            "email": r["email"], "device": _json(r["device"]), "context": ctx, "check": chk,
            "check_outcome": chk.get("outcome"), "reply": r["reply"], "seen": r["seen"], "parent": r["parent"],
            "files": _files(r), "learner": (r["learner"] or "")[-4:], "question_id": r["qid"],
            "session": r["session"], "word": r["word"], "paper": r["paper"]}


@router.get("/api/admin/reports", dependencies=[Depends(admin)])
def admin_list(status: str | None = None, category: str | None = None, kind: str | None = None,
               template: str | None = None, before: int | None = None, limit: int = 50) -> dict:
    """Newest first, children under their parents; `flagged` is every open
    report that waits for a person, broken and the signal first."""
    where, args = ["parent IS NULL", "kind!='correction'"], []
    for col, val in (("status", status), ("category", category_of(category) if category else None),
                     ("kind", kind), ("template", template)):
        if val:
            where.append(f"{col}=?")
            args.append(val)
    sql = " AND ".join(where)
    page = db.rows(f"SELECT * FROM reports WHERE {sql}{' AND id<?' if before else ''} ORDER BY id DESC LIMIT ?",
                   *args, *([before] if before else []), max(1, min(limit, 200)))
    flagged = sorted((x for x in (_row(r) for r in db.rows(
        f"SELECT * FROM reports WHERE {sql} AND status IN ('new','checking') ORDER BY id DESC LIMIT 300", *args))
        if x["rank"] is not None), key=lambda x: (x["rank"], -x["id"]))
    counts = {r["status"]: r["n"] for r in db.rows(
        "SELECT status, COUNT(*) AS n FROM reports WHERE parent IS NULL AND kind!='correction' GROUP BY status")}
    items = [_row(r) for r in page]
    return {"items": items, "flagged": flagged, "counts": counts, "mail": mail.mode(),
            "reports_to": bool(os.environ.get("SATF_REPORTS_TO")),
            "next": items[-1]["id"] if len(items) == max(1, min(limit, 200)) else None,
            "labels": LABELS, "statuses": STATUSES}


def question(template: str, seed: int) -> dict:
    """The item regenerated from its address, key and all, for the reviewer."""
    from satbank.audit import AuditError, audit
    from satbank.registry import generate, topic_of
    try:
        item = generate(template, seed, verify=False)
    except KeyError:
        raise HTTPException(404, "no such template") from None
    except Exception as e:
        raise HTTPException(422, f"can't regenerate: {e}") from None
    try:
        audit(item)
        audited = "ok"
    except AuditError as e:
        audited = str(e)
    try:
        problems = check_item(item)
    except Exception as e:
        problems = [f"check_item raised {e!r}"]
    return {"template": template, "seed": seed, "topic": topic_of(template), "skill": item.skill,
            "difficulty": item.difficulty, "fmt": item.fmt, "text": item.text, "stem": item.stem, "choices": list(item.choices),
            "latex": list(item.latex_choices), "figure": item.figure, "table": item.table,
            "answer": item.answer, "key": str(item.key), "rationale": item.rationale,
            "reasons": list(item.reasons),
            "spr_mistakes": [[m.reason, str(m.value)] for m in getattr(item, "spr_mistakes", ())],
            "audit": audited, "problems": problems, "quarantined": quarantined(template, seed),
            "source_id": item.source_id}


@router.get("/api/admin/question", dependencies=[Depends(admin)])
def admin_question(t: str, s: int) -> dict:
    return question(t, s)


@router.get("/api/admin/reports/{rid}", dependencies=[Depends(admin)])
def admin_detail(rid: int) -> dict:
    r = db.one("SELECT * FROM reports WHERE id=?", rid)
    if r is None:
        raise HTTPException(404, "no such report")
    out = _full(r)
    out["children"] = [_full(c) for c in db.rows("SELECT * FROM reports WHERE parent=? AND kind!='correction'"
                                                 " ORDER BY id", rid)]
    out["corrections"] = db.one("SELECT COUNT(*) AS n FROM reports WHERE parent=? AND kind='correction'", rid)["n"]
    if r["template"] and r["seed"] is not None:
        try:
            out["question"] = question(r["template"], r["seed"])
        except HTTPException as e:
            out["question"] = {"error": e.detail}
    return out


class AdminPut(BaseModel):
    status: Literal["new", "checking", "fixed", "no_change"] | None = None
    reply: str | None = Field(None, max_length=5000)
    dispute_outcome: Literal["key_wrong", "key_right"] | None = None
    scope: Literal["one", "template"] = "one"
    since: str | None = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    fixed_note: str | None = Field(None, max_length=200)


def resolve(rid: int, body: AdminPut) -> dict:
    """The admin's answer, applied to the report and its me-too children."""
    r = db.one("SELECT * FROM reports WHERE id=? AND kind!='correction'", rid)
    if r is None:
        raise HTTPException(404, "no such report")
    group = [r] + db.rows("SELECT * FROM reports WHERE parent=? AND kind!='correction'", rid)
    corrected = None
    if body.dispute_outcome == "key_right":
        for x in group:
            ctx = _json(x["context"])
            for aid in ctx.get("disputed") or ():
                _undispute(aid, ctx.get("closed_traps"))
            ctx["outcome"] = "key_right"
            _save(x["id"], context=ctx)
    elif body.dispute_outcome == "key_wrong":
        if not r["template"]:
            raise HTTPException(422, "this report isn't about a question")
        corrected = correct_key(r["template"], r["seed"] if body.scope == "one" else None,
                                body.since if body.scope == "template" else None, report=rid,
                                reporters={x["learner"] for x in group})
        for x in group:
            ctx = _json(x["context"])
            mine = db.rows("SELECT id FROM attempts WHERE learner=? AND template=?" +
                           (" AND seed=?" if body.scope == "one" else ""), x["learner"], r["template"],
                           *([r["seed"]] if body.scope == "one" else []))
            ctx.update({"outcome": "key_wrong", "scope": body.scope, "since": body.since,
                        "disputed": sorted(set(ctx.get("disputed") or ()) | {m["id"] for m in mine}),
                        "rescored": corrected["sittings"],
                        "corrected": {k: corrected[k] for k in ("attempts", "learners", "sittings")}})
            _save(x["id"], context=ctx)
    stamp = now()
    for x in group:
        cols = {}
        if body.status:
            cols["status"] = body.status
        if body.reply is not None and body.reply.strip():
            cols.update({"reply": body.reply.strip(), "replied": stamp, "seen": None})
        if cols:
            _save(x["id"], **cols)
        if "reply" in cols and x["email"]:
            mail.send_report_reply(x["email"], x["id"], x["title"] or "", cols["reply"])
    if body.fixed_note is not None:
        ctx = _json(db.one("SELECT context FROM reports WHERE id=?", rid)["context"])
        ctx["fixed_note"] = body.fixed_note.strip() or None
        _save(rid, context=ctx)
    out = _full(db.one("SELECT * FROM reports WHERE id=?", rid))
    if corrected:
        out["corrected"] = {k: corrected[k] for k in ("attempts", "learners", "sittings")}
    return out


@router.put("/api/admin/reports/{rid}", dependencies=[Depends(admin)])
def admin_put(rid: int, body: AdminPut) -> dict:
    return resolve(rid, body)


@router.get("/api/admin/files/{rid}/{name}", dependencies=[Depends(admin)])
def admin_file(rid: int, name: str):
    if not FILE_OK.match(name):
        raise HTTPException(404, "no such file")
    r = db.one("SELECT files FROM reports WHERE id=?", rid)
    meta = next((f for f in json.loads(r["files"] or "[]") if f["file"] == name), None) if r else None
    path = FILES / str(rid) / name
    if meta is None or not path.is_file():
        raise HTTPException(404, "no such file")
    return FileResponse(path, media_type=meta["type"], headers={"Cache-Control": "private, no-store"})


class Quarantine(BaseModel):
    template: str = Field(max_length=120)
    seed: int | None = Field(None, ge=-1)
    note: str = Field("", max_length=300)


@router.get("/api/admin/quarantine", dependencies=[Depends(admin)])
def admin_quarantine() -> list[dict]:
    return [dict(r) | {"whole": r["seed"] == -1}
            for r in db.rows("SELECT * FROM quarantine ORDER BY released IS NOT NULL, at DESC LIMIT 200")]


@router.post("/api/admin/quarantine", dependencies=[Depends(admin)])
def admin_stop(body: Quarantine) -> dict:
    """Stop serving: this seed, or every seed of the template."""
    from satbank.registry import templates
    if body.template not in templates():
        raise HTTPException(404, "no such template")
    quarantine(body.template, None if body.seed in (None, -1) else body.seed, body.note)
    return {"ok": True, "quarantined": quarantined(body.template, body.seed)}


@router.post("/api/admin/quarantine/release", dependencies=[Depends(admin)])
def admin_release(body: Quarantine) -> dict:
    return {"released": release(body.template, None if body.seed in (None, -1) else body.seed)}


@router.get("/api/admin/labels", dependencies=[Depends(admin)])
def admin_labels(min_learners: int = 20, rate: float = 0.15) -> list[dict]:
    """V6's Labels view: per (template, norm), the learners who fell for it,
    and how many said the label is wrong (a label report, or a "Not what I
    did?" correction). Rate-sorted; `flagged` past 15% of 20 or more."""
    fell = {(r["template"], r["norm"]): (r["n"], r["reason"]) for r in db.rows(
        f"SELECT template, norm, COUNT(DISTINCT learner) AS n, MAX(reason) AS reason FROM attempts"
        f" WHERE correct=0 AND COALESCE(norm,'') NOT IN ('', '~unsure') AND {db.NOT_SAMPLE}"
        f" GROUP BY template, norm")}
    said: dict[tuple, set] = {}
    for r in db.rows("SELECT learner, template, json_extract(context,'$.norm') AS norm FROM reports"
                     " WHERE category='label' AND template IS NOT NULL"):
        if r["norm"]:
            said.setdefault((r["template"], r["norm"]), set()).add(r["learner"])
    for r in db.rows(f"SELECT learner, template, norm FROM attempts WHERE correct=0 AND miss_kind IS NOT NULL"
                     f" AND miss_kind NOT IN ('trap','fell') AND norm IS NOT NULL AND {db.NOT_SAMPLE}"):
        said.setdefault((r["template"], r["norm"]), set()).add(r["learner"])
    out = []
    for (t, n), who in said.items():
        total, reason = fell.get((t, n), (0, None))
        share = len(who) / total if total else 1.0
        out.append({"template": t, "norm": n, "reason": reason, "learners": total, "disputed": len(who),
                    "rate": round(share, 3), "flagged": total >= min_learners and share >= rate})
    return sorted(out, key=lambda x: (-x["flagged"], -x["rate"], -x["disputed"]))[:200]


@router.get("/api/admin/cb_unknown", dependencies=[Depends(admin)])
def admin_cb_unknown() -> list[dict]:
    """U2: the College Board ids students typed that the bank doesn't know."""
    return [dict(r) for r in db.rows("SELECT * FROM cb_unknown ORDER BY n DESC, last DESC LIMIT 50")]


@router.get("/api/admin/words/suppressed", dependencies=[Depends(admin)])
def admin_suppressed() -> list[dict]:
    """W18's suppress queue: word distractors the crowd guard pulled."""
    return [dict(r) for r in db.rows("SELECT * FROM word_suppress ORDER BY at DESC LIMIT 200")]


class Unsuppress(BaseModel):
    frame: str = Field(max_length=200)
    word: str = Field(max_length=80)


@router.post("/api/admin/words/unsuppress", dependencies=[Depends(admin)])
def admin_unsuppress(body: Unsuppress) -> dict:
    return {"removed": db.run("DELETE FROM word_suppress WHERE frame=? AND word=?", body.frame, body.word).rowcount}
