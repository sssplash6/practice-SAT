"""The learner's profile, and carrying another code's progress into this one."""

from __future__ import annotations

import datetime as dt
import json
import re

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field

from . import db, drill, prefs, progress, satdates
from .deps import (DATE_OK, DAYS_OK, HANDLE_OK, LEARNER_OK, NAME_OK, PACE, SECONDS_PER_QUESTION, TARGETS,
                   learner_of, now, part, tz_of, writer_of)

router = APIRouter()

FOCUS_STATES = ("focus", "normal", "strong")
MAX_FOCUS = 2               # of four domains, as theirs allow four of eight
RESERVED = {"admin", "administrator", "moderator", "sat", "sat freshman", "college board",
            "anonymous", "student", "support", "staff", "teacher", "system"}
COUNTRIES = set((
    "AD AE AF AG AI AL AM AO AQ AR AS AT AU AW AX AZ BA BB BD BE BF BG BH BI BJ BL BM BN BO BQ BR BS BT BV BW BY BZ "
    "CA CC CD CF CG CH CI CK CL CM CN CO CR CU CV CW CX CY CZ DE DJ DK DM DO DZ EC EE EG EH ER ES ET FI FJ FK FM FO FR "
    "GA GB GD GE GF GG GH GI GL GM GN GP GQ GR GS GT GU GW GY HK HM HN HR HT HU ID IE IL IM IN IO IQ IR IS IT JE JM "
    "JO JP KE KG KH KI KM KN KP KR KW KY KZ LA LB LC LI LK LR LS LT LU LV LY MA MC MD ME MF MG MH MK ML MM MN MO MP "
    "MQ MR MS MT MU MV MW MX MY MZ NA NC NE NF NG NI NL NO NP NR NU NZ OM PA PE PF PG PH PK PL PM PN PR PS PT PW PY "
    "QA RE RO RS RU RW SA SB SC SD SE SG SH SI SJ SK SL SM SN SO SR SS ST SV SX SY SZ TC TD TF TG TH TJ TK TL TM TN TO "
    "TR TT TV TW TZ UA UG UM US UY UZ VA VC VE VG VI VN VU WF WS YE YT ZA ZM ZW"
).split())


def account(learner: str) -> dict:
    """Shell §3.1.5: is this learner saved, under which email, since when."""
    user = db.one("SELECT email, verified, google_sub, created FROM users WHERE learner=?"
                  " ORDER BY verified DESC, created LIMIT 1", learner)
    passkey = db.one("SELECT created FROM passkeys WHERE learner=? ORDER BY created LIMIT 1", learner)
    linked = bool(passkey) or bool(user and (user["verified"] or user["google_sub"]))
    since = min([x for x in (user["created"] if user else None, passkey["created"] if passkey else None) if x],
                default=None)
    return {"linked": linked, "email": user["email"] if user and user["email"] else None,
            "since": since if linked else None}


def profile(learner: str, tz: int = 0) -> dict:
    row = db.one("SELECT * FROM learners WHERE id=?", learner)
    base = {"id": learner, "name": None, "handle": None, "exam_date": None, "target": None,
            "minutes": None, "days": None, "current": None, "tests": None, "focus": None,
            "avatar": None, "board": "name", "country": "", "rw_now": None,
            "rw_target": None, "plan": None, "plan_draft": None}
    out = {**base, **({k: row[k] for k in base} if row else {})}
    out["focus"] = json.loads(out["focus"]) if out["focus"] else {}
    out["plan_draft"] = json.loads(out["plan_draft"]) if out["plan_draft"] else None
    out["board"] = out["board"] or "name"
    out["country"] = out["country"] or ""
    out["prefs"], out["pref_source"], out["stage"] = prefs.resolve(learner, tz)
    out["account"] = account(learner)
    return out


def scores(learner: str) -> dict:
    """Total, then R&W, then Math (College Board's order), the one reader behind every page that shows
    scores side by side (Me, the plan's tile, parent, admin, the PDF, emails). Each section is
    estimate.current, the one current score Results and Tests show too (the latest up to 3 sittings
    and logged scores; a lower route's cap kept; the typed score, source "yours", only without one),
    the total estimate.total (two centres +- 10, never two ranges added). Targets: each section's own,
    the total their sum."""
    from . import estimate
    row = db.one("SELECT target, rw_target FROM learners WHERE id=?", learner)
    out = {}
    for s in ("rw", "math"):
        now = estimate.current(learner, s)
        mine = now and now["source"] != "self"
        out[s] = {"low": now["low"] if now else None, "high": now["high"] if now else None,
                  "mid": now["mid"] if now else None,
                  "source": ("yours" if now["source"] == "self" else now["source"]) if now else None,
                  "at": (now["at"] or "")[:10] or None if mine else None,
                  "target": (row["rw_target"] if s == "rw" else row["target"]) if row else None}
    total = estimate.total(learner)
    total = {k: total[k] for k in ("low", "high", "mid")} if total else {"low": None, "high": None, "mid": None}
    targets = (out["rw"]["target"], out["math"]["target"])
    out = {"total": {**total, "target": sum(targets) if all(targets) else None}, **out}
    return out


def due_left(learner: str, tz: int, p: dict) -> int:
    """R1 / V1: today's review items not yet done or snoozed. Review's own
    count when S10 has built it; until then, check-ins due less snoozed."""
    due = part("review", "due")
    if due:
        return due(learner, tz)["left"]
    today = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=tz)).date().isoformat()
    snoozed = {k for k, day in (p.get("snooze") or {}).items() if day == today}
    return sum(1 for c in progress.due_rechecks(learner, today)
               if f"due:check:{c['template']}" not in snoozed)


def per_session(p: dict, subject: str = "math") -> int:
    """How many questions a study day's minutes hold, at the real test's pace for the subject
    (95 s a Math question, 71 s an R&W one)."""
    if not p.get("minutes"):
        return 10
    minutes = p["minutes"]
    if p.get("prefs",{}).get("words_goal", 10):
        fn = part("words", "minutes_today")
        if fn:
            minutes = max(0,minutes-fn(p["id"],0))
    return max(5, min(drill.MAX_FIXED, round(minutes * 60 / PACE.get(subject, SECONDS_PER_QUESTION))))


@router.get("/api/me")
def get_me(x_learner: str | None = Header(default=None), x_tz: int = Depends(tz_of)) -> dict:
    learner = learner_of(x_learner)
    p = profile(learner, x_tz)
    week_ago=(dt.datetime.now(dt.timezone.utc)-dt.timedelta(days=7)).isoformat()
    today=(dt.datetime.now(dt.timezone.utc)-dt.timedelta(minutes=x_tz)).date().isoformat()
    words=db.one("SELECT SUM(box>=4) AS known, COUNT(*) AS studied, SUM(saved) AS saved,"
                 " SUM(due<=?) AS due FROM word_state WHERE learner=?",today,learner)
    reviews=db.one("SELECT COUNT(*) AS n FROM word_reviews WHERE learner=? AND at>=?",learner,week_ago)
    review=db.one("SELECT COUNT(*) AS open, SUM(owed=1) AS half FROM traps"
                  " WHERE learner=? AND closed IS NULL",learner)
    registration = satdates.registration(p["exam_date"], p["prefs"].get("registered"),
                                         dt.date.fromisoformat(today))
    return {"profile": p, "prefs": p["prefs"], "pref_source": p["pref_source"], "stage": p["stage"],
            "days": progress.days(learner, x_tz), "registration": registration,
            "review":{"open":review["open"],"half":review["half"] or 0,
                      "due_left":due_left(learner, x_tz, p["prefs"])},
            "words": {"known":words["known"] or 0,"studied":words["studied"] or 0,
                      "saved":words["saved"] or 0,"reviews_week":reviews["n"],"due":words["due"] or 0}}


@router.get("/api/me/activity")
def activity(weeks: int = Query(default=26, ge=1, le=53),
             x_learner: str | None = Header(default=None), x_tz: int = Depends(tz_of)) -> dict:
    return progress.days(learner_of(x_learner),x_tz,weeks)


class Me(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str | None = Field(default=None, max_length=40)     # yours: private, any script (U29)
    handle: str | None = Field(default=None, max_length=24)   # your board name: public, unique
    exam_date: str | None = None
    target: int | None = None
    minutes: int | None = None
    days: str | None = None
    current: int | None = None          # where the plan starts from
    tests: str | None = None            # "weekly" or "daily"
    focus: dict[str, str] | None = None # domain -> focus / normal / strong
    avatar: str | None = None
    board: str | None = None
    country: str | None = None
    rw_now: int | None = None
    rw_target: int | None = None
    prefs: dict | None = None


def _check_handle(learner: str, handle: str) -> str:
    """U29 / R12: HANDLE_OK, not reserved or default-looking (422), unique
    case-insensitively (409), each error naming `handle`."""
    h = " ".join(handle.strip().split())
    if not HANDLE_OK.fullmatch(h) or h.casefold() in RESERVED or re.fullmatch(r"student[ ._-]*[0-9a-f]{3,}", h, re.I):
        raise HTTPException(422, "handle must be 3–24 letters, digits, spaces, _, . or - and cannot be reserved")
    if db.one("SELECT 1 FROM learners WHERE id!=? AND lower(handle)=lower(?)", learner, h):
        raise HTTPException(409, "handle: someone already has that board name")
    return h


@router.put("/api/me")
def put_me(body: Me, x_learner: str | None = Header(default=None), x_tz: int = Depends(tz_of)) -> dict:
    learner = writer_of(x_learner)
    got = body.model_dump(exclude_unset=True)
    pref_change = got.pop("prefs", None)
    if pref_change is not None:
        prefs.validate(pref_change)
    if "name" in got and got["name"] is not None:
        got["name"] = " ".join(got["name"].strip().split()) or None
        if got["name"] and (not NAME_OK.fullmatch(got["name"]) or len(got["name"]) > 40):
            raise HTTPException(422, "name: 1–40 characters, no digits, @, < or >")
    if got.get("handle") is not None:
        got["handle"] = _check_handle(learner, got["handle"])
    if got.get("exam_date") is not None:           # "" is no date: null clears it
        try:
            if not DATE_OK.match(got["exam_date"]):
                raise ValueError
            exam = dt.date.fromisoformat(got["exam_date"])
            today = (dt.datetime.now(dt.timezone.utc)-dt.timedelta(minutes=x_tz)).date()
            if exam < today:
                raise ValueError
        except ValueError:
            raise HTTPException(422, "exam_date must be today or later, YYYY-MM-DD")
    if got.get("target") is not None and got["target"] not in TARGETS:
        raise HTTPException(422, "target is a Math score, 200 to 800 in tens")
    if got.get("minutes") is not None and not 5 <= got["minutes"] <= 240:
        raise HTTPException(422, "minutes is between 5 and 240")
    if got.get("days") is not None and not DAYS_OK.match(got["days"]):
        raise HTTPException(422, "days is seven 0s and 1s, Monday first")
    if got.get("current") is not None and got["current"] not in TARGETS:
        raise HTTPException(422, "current is a Math score, 200 to 800 in tens")
    if got.get("tests") is not None and got["tests"] not in ("none", "weekly", "twice", "daily"):
        raise HTTPException(422, "tests is none, weekly, twice or daily")
    for key in ("rw_now","rw_target"):
        if got.get(key) is not None and got[key] not in TARGETS:
            raise HTTPException(422, f"{key} is a Reading and Writing score, 200 to 800 in tens")
    if got.get("board") is not None and got["board"] not in ("name","anon","hidden"):
        raise HTTPException(422, "board is name, anon or hidden")
    if got.get("avatar") is not None and got["avatar"] not in {**progress.topics("math"), **progress.topics("rw")}:
        raise HTTPException(422, "avatar must be a Math or Reading and Writing skill slug")
    if got.get("country") is not None:
        if got["country"] and got["country"] not in COUNTRIES:
            raise HTTPException(422, "country must be an ISO alpha-2 code or blank")
    if got.get("focus") is not None:
        domains = set(progress.DOMAINS)
        if any(d not in domains or v not in FOCUS_STATES for d, v in got["focus"].items()):
            raise HTTPException(422, "focus maps a domain to focus, normal or strong")
        if sum(v == "focus" for v in got["focus"].values()) > MAX_FOCUS:
            raise HTTPException(422, f"at most {MAX_FOCUS} domains on focus")
        # normal is the default and is not stored
        got["focus"] = json.dumps({d: v for d, v in got["focus"].items() if v != "normal"}) or None
    changed = {k:v for k,v in got.items() if k in ("exam_date","target","minutes","days","current","tests","focus","rw_now","rw_target")}
    if "focus" in changed:
        changed["focus"] = json.loads(changed["focus"] or "{}")
    mirror = part("plan","mirror")
    with db.transaction():
        db.ensure_learner(learner)
        for k, v in got.items():
            db.run(f"UPDATE learners SET {k}=?, updated=? WHERE id=?", v, now(), learner)
        if pref_change is not None:
            prefs.put(learner,pref_change)
        if mirror and changed:
            mirror(learner,changed)
    return {"profile": profile(learner, x_tz)}


@router.get("/api/prefs")
def prefs_registry() -> list[dict]:
    """U24: every key with its label, group, values, helper and synonyms."""
    return prefs.listing()


class Carry(BaseModel):
    learner: str = Field(max_length=120)       # the code this device held until now


@router.post("/api/me/carry")
def carry(body: Carry, x_learner: str | None = Header(default=None)) -> dict:
    """Bring another code's progress into this one, so switching a device to
    another device's code keeps what both have done."""
    to = writer_of(x_learner)
    frm = body.learner.strip()
    if not LEARNER_OK.match(frm):
        raise HTTPException(400, "that is not a learner code")
    return {"moved": 0 if frm == to else progress.carry(frm, to)}
