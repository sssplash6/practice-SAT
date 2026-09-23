"""The learner's profile, and carrying another code's progress into this one."""

from __future__ import annotations

import datetime as dt
import json
import re

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from . import db, drill, prefs, progress
from .deps import (DATE_OK, DAYS_OK, LEARNER_OK, NAME_OK, SECONDS_PER_QUESTION, TARGETS,
                   learner_of, now, part, tz_of)

router = APIRouter()

FOCUS_STATES = ("focus", "normal", "strong")
MAX_FOCUS = 2               # of four domains, as theirs allow four of eight
BOARD_NAME = re.compile(r"^[\w .-]{3,24}$", re.UNICODE)
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


def profile(learner: str) -> dict:
    row = db.one("SELECT * FROM learners WHERE id=?", learner)
    base = {"id": learner, "name": None, "exam_date": None, "target": None,
            "minutes": None, "days": None, "current": None, "tests": None, "focus": None,
            "avatar": None, "board": "name", "country": "", "rw_now": None,
            "rw_target": None, "plan": None, "plan_draft": None}
    out = {**base, **({k: row[k] for k in base} if row else {})}
    out["focus"] = json.loads(out["focus"]) if out["focus"] else {}
    out["plan_draft"] = json.loads(out["plan_draft"]) if out["plan_draft"] else None
    out["board"] = out["board"] or "name"
    out["country"] = out["country"] or ""
    out["prefs"] = prefs.get(learner)
    return out


def per_session(p: dict) -> int:
    """How many questions a study day's minutes hold, at the real test's pace."""
    if not p.get("minutes"):
        return 10
    minutes = p["minutes"]
    if p.get("prefs",{}).get("words_goal", 10):
        fn = part("words", "minutes_today")
        if fn:
            minutes = max(0,minutes-fn(p["id"],0))
    return max(5, min(drill.MAX_FIXED, round(minutes * 60 / SECONDS_PER_QUESTION)))


@router.get("/api/me")
def get_me(x_learner: str | None = Header(default=None), x_tz: int = Depends(tz_of)) -> dict:
    learner = learner_of(x_learner)
    p = profile(learner)
    week_ago=(dt.datetime.now(dt.timezone.utc)-dt.timedelta(days=7)).isoformat()
    today=(dt.datetime.now(dt.timezone.utc)-dt.timedelta(minutes=x_tz)).date().isoformat()
    words=db.one("SELECT SUM(box>=4) AS known, COUNT(*) AS studied, SUM(saved) AS saved,"
                 " SUM(due<=?) AS due FROM word_state WHERE learner=?",today,learner)
    reviews=db.one("SELECT COUNT(*) AS n FROM word_reviews WHERE learner=? AND at>=?",learner,week_ago)
    return {"profile": p, "prefs": p["prefs"], "days": progress.days(learner, x_tz),
            "words": {"known":words["known"] or 0,"studied":words["studied"] or 0,
                      "saved":words["saved"] or 0,"reviews_week":reviews["n"],"due":words["due"] or 0}}


class Me(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str | None = Field(default=None, max_length=24)
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


@router.put("/api/me")
def put_me(body: Me, x_learner: str | None = Header(default=None), x_tz: int = Depends(tz_of)) -> dict:
    learner = learner_of(x_learner)
    got = body.model_dump(exclude_unset=True)
    pref_change = got.pop("prefs", None)
    if pref_change is not None:
        prefs.validate(pref_change)
    if "name" in got and got["name"] is not None:
        got["name"] = " ".join(got["name"].strip().split()) or None
        if got["name"]:
            n = got["name"]
            # Earlier profiles accepted two-letter names. Keep them private
            # for learners with existing answers; public board names stay 3–24.
            private_short = (len(n)==2 and re.fullmatch(r"[\w.-]{2}",n) and
                             got.get("board") != "name" and
                             db.one("SELECT 1 FROM attempts WHERE learner=? LIMIT 1",learner))
            if private_short:
                got["board"]="hidden"
            if not private_short and (not BOARD_NAME.fullmatch(n) or n.casefold() in RESERVED or re.fullmatch(r"student[ ._-]*[0-9a-f]{3,}", n, re.I)):
                raise HTTPException(422, "name must be 3–24 letters, digits, spaces, _, . or - and cannot be reserved")
            if any(r["name"] and r["name"].casefold() == n.casefold() for r in db.rows("SELECT name FROM learners WHERE id!=? AND name IS NOT NULL",learner)):
                raise HTTPException(409, "that board name is taken")
    if got.get("exam_date"):
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
    if got.get("days") and not DAYS_OK.match(got["days"]):
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
    if got.get("board")=="name" and "name" not in got:
        existing=db.one("SELECT name FROM learners WHERE id=?",learner)
        if existing and existing["name"] and not BOARD_NAME.fullmatch(existing["name"]):
            raise HTTPException(422, "set a 3–24 character board name before listing it")
    if got.get("avatar") is not None and got["avatar"] not in progress.topics():
        raise HTTPException(422, "avatar must be a topic slug")
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
    db.ensure_learner(learner)
    for k, v in got.items():
        db.run(f"UPDATE learners SET {k}=?, updated=? WHERE id=?", v, now(), learner)
    if pref_change is not None:
        prefs.put(learner,pref_change)
    changed = {k:v for k,v in got.items() if k in ("exam_date","target","minutes","days","current","tests","focus","rw_now","rw_target")}
    mirror = part("plan","mirror")
    if mirror and changed:
        mirror(learner,changed)
    return {"profile": profile(learner)}


class Carry(BaseModel):
    learner: str = Field(max_length=120)       # the code this device held until now


@router.post("/api/me/carry")
def carry(body: Carry, x_learner: str | None = Header(default=None)) -> dict:
    """Bring another code's progress into this one, so switching a device to
    another device's code keeps what both have done."""
    to = learner_of(x_learner)
    frm = body.learner.strip()
    if not LEARNER_OK.match(frm):
        raise HTTPException(400, "that is not a learner code")
    return {"moved": 0 if frm == to else progress.carry(frm, to)}
