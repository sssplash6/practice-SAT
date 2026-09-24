"""Public question-type catalogue and manually logged outside mistakes."""

from __future__ import annotations

import datetime as dt
import difflib
import json
import pathlib
import re
import zlib
from functools import lru_cache

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from satbank.registry import generate

from . import blueprint, db, deps, drill, practice, progress

router = APIRouter()


@lru_cache(maxsize=1)
def _official() -> dict[str, dict]:
    out = {}
    root = pathlib.Path(__file__).resolve().parent.parent / "material" / "keys"
    for path in root.glob("*.json"):
        data = json.loads(path.read_text())
        for item in data.get("items", []):
            if item.get("cb_id"):
                out[item["cb_id"]] = {"topic": data.get("slug", path.stem), "tier": item.get("tier")}
    return out


def _known(template: str) -> dict:
    entry = blueprint.kinds().get(template)
    if entry is None:
        raise HTTPException(404, "no such question type")
    return entry


def _name(entry: dict) -> str:
    return entry["skill"][:1].upper() + entry["skill"][1:]


def _weight(entry: dict) -> float:
    # The catalogue stays useful before the official mapping is installed.
    same = practice.catalogue()["by_topic"].get(entry["topic"], ())
    return round(progress.BLUEPRINT.get(entry["domain"], .15) / max(len(same), 1), 5)


def _type(template: str, entry: dict) -> dict:
    kinds = entry["kinds"]
    tiers = sorted({tier for tier, _ in kinds}, key=drill.TIERS.index)
    formats = sorted({fmt for _, fmt in kinds})
    lv = drill.levels()
    level_rows = {tier: lv.get((template, tier), {}) for tier in tiers}
    return {"template": template, "name": _name(entry), "about": entry["about"],
            "topic": entry["topic"], "domain": entry["domain"],
            "subject": deps.subject_of(entry["topic"]), "skill": entry["skill"],
            "formats": formats, "tiers": tiers, "weight": _weight(entry), "available": True,
            "reasons": [{"norm": norm, "label": label} for norm, label in sorted(entry["reasons"].items())],
            "levels": level_rows, "level": level_rows.get("medium", next(iter(level_rows.values()), {})).get("level"),
            "rough": all(v.get("rough", True) for v in level_rows.values()),
            "budget_ms": {tier: drill.budget_ms(template, tier) for tier in tiers},
            "variety": entry["variety"]}


@router.get("/api/types")
def types(topic: str | None = None, subject: str = "math") -> list[dict]:
    if subject not in ("math", "rw"):
        raise HTTPException(422, {"field": "subject", "reason": "math or rw"})
    return [_type(t, e) for t, e in blueprint.kinds().items()
            if (topic is None or e["topic"] == topic) and deps.subject_of(e["topic"]) == subject]


@router.get("/api/bank")
def bank(subject: str = "math") -> dict:
    if subject not in ("math", "rw"):
        raise HTTPException(422, {"field": "subject", "reason": "math or rw"})
    cat = practice.catalogue()
    topics = [{"topic": slug, "name": topic.name, "domain": topic.domain,
               "available": bool(cat["by_topic"].get(slug)),
               "types": len(cat["by_topic"].get(slug, ()))}
              for slug, topic in cat["topics"].items() if deps.subject_of(slug) == subject]
    if subject == "rw" and not topics:
        topics = [{"topic": slug, "name": name, "domain": domain, "available": False, "types": 0}
                  for slug, name, domain in (("words-in-context", "Words in Context", "Craft and Structure"),
                                             ("transitions", "Transitions", "Expression of Ideas"))]
    return {"subject": subject, "topics": topics, "types": types(subject=subject)}


def _match_id(cbid: str) -> dict | None:
    found = _official().get(cbid)
    if not found:
        return None
    names = practice.catalogue()["by_topic"].get(found["topic"], ())
    if not names:
        return None
    same_tier = [t for t in names if found.get("tier") in {tier for tier, _ in blueprint.abilities().get(t, ())}]
    template = (same_tier or names)[zlib.crc32(cbid.encode()) % len(same_tier or names)]
    return {"template": template, "topic": found["topic"],
            "skill": blueprint.kinds()[template]["skill"], "score": .4,
            "via": "id", "example": f"/api/types/{template}/example", "cb_id": cbid}


@router.get("/api/types/match")
def match_id(id: str) -> dict:
    row = _match_id(id)
    if row:
        return {"rows": [row]}
    now = progress.now()
    db.run("INSERT INTO cb_unknown(cb_id,first,last,n) VALUES (?,?,?,1)"
           " ON CONFLICT(cb_id) DO UPDATE SET last=excluded.last,n=n+1", id, now, now)
    return {"rows": [{"via": "none", "cb_id": id}]}


class MatchText(BaseModel):
    text: str = Field(min_length=3, max_length=2000)


@router.post("/api/types/match")
def match_text(body: MatchText) -> dict:
    phrase = body.text.lower()
    ranked = []
    for template, entry in blueprint.kinds().items():
        target = f"{entry['skill']} {entry['about']} {entry['topic']}".lower()
        score = difflib.SequenceMatcher(None, phrase[:160], target[:160]).ratio()
        if phrase in target:
            score += .5
        ranked.append((score, template, entry))
    return {"rows": [{"template": template, "topic": entry["topic"], "skill": entry["skill"],
                      "score": round(score, 3), "via": "text",
                      "example": f"/api/types/{template}/example"}
                     for score, template, entry in sorted(ranked, reverse=True)[:3]]}


class Pick(BaseModel):
    cb_id: str | None = None
    template: str | None = None
    letter: str | None = None
    value: str | None = None


@router.post("/api/types/match/pick")
def match_pick(body: Pick) -> dict:
    matched = _match_id(body.cb_id) if body.cb_id else None
    template = body.template or (matched or {}).get("template")
    entry = blueprint.kinds().get(template)
    if entry is None:
        raise HTTPException(422, {"field": "template", "reason": "unknown question type"})
    reasons = list(entry["reasons"].values())
    if body.letter and body.letter not in "ABCD":
        raise HTTPException(422, {"field": "letter", "reason": "A–D"})
    picked = reasons[(ord(body.letter) - 65) % len(reasons)] if body.letter and reasons else None
    return {"template": template, "reason": picked,
            "reasons": reasons, "matched": bool(matched)}


@router.get("/api/types/{template}/example")
def example(template: str, want: str | None = None, tier: str | None = None) -> dict:
    entry = _known(template)
    if tier is not None and tier not in drill.TIERS:
        raise HTTPException(422, {"field": "tier", "reason": "easy, medium or hard"})
    if want is not None and len(want) > 500:
        raise HTTPException(422, {"field": "want", "reason": "too long"})
    start = 900_000 + zlib.crc32(f"{template}:{want}:{tier}".encode()) % 10_000
    nearest = None
    for seed in range(start, start + 60):
        try:
            card = practice.Card.of(template, seed, generate(template, seed), entry["topic"])
        except Exception:
            continue
        if tier and card.item.difficulty != tier:
            continue
        nearest = card
        if want and not drill._offers(card, "^" + re.escape(want) + "$"):
            continue
        break
    if nearest is None:
        raise HTTPException(409, {"reason": "no_example"})
    q = practice.to_question(nearest, 1)
    return {"template": template, "seed": nearest.seed, "question": q,
            "trap_true": not want or drill._offers(nearest, "^" + re.escape(want) + "$")}


@router.get("/api/types/{template}")
def type_detail(template: str, x_learner: str | None = Header(default=None)) -> dict:
    entry = _known(template)
    out = _type(template, entry)
    # material/keys identifies an official item's topic, not its precise
    # generated template. The type page must not claim a stronger mapping.
    out["official"] = []
    out["has"] = {"steps": False, "desmos": False}
    out["siblings"] = {"easier": blueprint.siblings(template, -1),
                       "harder": blueprint.siblings(template, 1)}
    out["related"] = blueprint.lookalikes(template)
    if x_learner:
        learner = deps.learner_of(x_learner)
        attempts = db.rows("SELECT correct,ms FROM attempts WHERE learner=? AND template=? ORDER BY id",
                           learner, template)
        traps = [t for t in progress.open_traps(learner) if t["template"] == template]
        out["you"] = {"seen": len(attempts), "right": sum(a["correct"] for a in attempts),
                      "open": [t["id"] for t in traps], "median_ms": None,
                      "budget_ms": out["budget_ms"], "rule": None}
    return out


class MistakeLog(BaseModel):
    template: str
    reason: str | None = None
    note: str | None = Field(default=None, max_length=80)
    origin: str = "other"
    where_note: str | None = Field(default=None, max_length=200)
    cb_id: str | None = None
    letter: str | None = None


@router.post("/api/mistakes/log")
def log_mistake(body: MistakeLog, x_learner: str | None = Header(default=None)) -> dict:
    learner = deps.learner_of(x_learner)
    entry = blueprint.kinds().get(body.template)
    if entry is None:
        raise HTTPException(422, {"field": "template", "reason": "unknown template"})
    if body.origin not in ("school", "bluebook", "official", "book", "other", "cb_qbank"):
        raise HTTPException(422, {"field": "origin", "reason": "unknown origin"})
    if body.reason and progress.norm(body.reason) not in entry["reasons"]:
        raise HTTPException(422, {"field": "reason", "reason": "not offered by this type"})
    today = dt.datetime.now(dt.timezone.utc).date().isoformat()
    # outside logs only: in-app misses always carry their attempt id
    n = db.one("SELECT COUNT(*) n FROM (SELECT DISTINCT template,norm,at FROM trap_log WHERE learner=?"
               " AND attempt IS NULL AND event IN ('open','miss','reopened','relapse') AND at>=?)",
               learner, today)["n"]
    if n >= 30:
        raise HTTPException(429, {"reason": "outside_mistake_limit"})
    q = {"id": "outside", "key": body.template, "seed": 900_000, "topic": entry["topic"],
         "topic_name": practice.catalogue()["topics"][entry["topic"]].name,
         "skill": entry["skill"]}
    result = progress.record_trap(learner, q, body.reason or "", progress.now(),
                                  label=body.reason or body.note or entry["skill"])
    db.run("UPDATE traps SET source='outside',origin=?,note=? WHERE id=?",
           body.origin, body.where_note or body.note, result["id"])
    return {"trap": {**result, "source": "outside", "origin": body.origin}}
