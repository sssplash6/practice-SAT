"""A single score summary for Tests, Today, Plan and Results."""

from __future__ import annotations

import datetime as dt
import json
import math

from . import db


def _mid(item: dict) -> float:
    return (item["low"]+item["high"])/2


def _round10(value: float) -> int:
    return round(value/10)*10


def _standard(row) -> bool:
    if row["kind"] not in ("mock","section","paper"):
        return False
    cfg = json.loads(row["cfg"] or "{}")
    return (cfg.get("timing","official") == "official" and
            cfg.get("route","adaptive") == "adaptive" and
            cfg.get("m1","standard") == "standard" and
            row["route"] not in ("fixed-upper","fixed-lower") and
            cfg.get("variant") is None)


def _sittings(learner: str) -> list[dict]:
    out = []
    for row in db.rows("SELECT * FROM sessions WHERE learner=? AND finished IS NOT NULL"
                       " AND result IS NOT NULL ORDER BY finished DESC,id DESC",learner):
        res = json.loads(row["result"] or "{}")
        band = res.get("estimate") or {}
        if not isinstance(band,dict) or band.get("low") is None or band.get("high") is None:
            continue
        out.append({"id":row["id"],"kind":row["kind"],"low":band["low"],"high":band["high"],
                    "mid":(band["low"]+band["high"])/2,"at":row["finished"],
                    "route":row["route"],"standard":_standard(row),"outside":False})
    for row in db.rows("SELECT * FROM outside_scores WHERE learner=? AND math IS NOT NULL",learner):
        out.append({"id":row["id"],"kind":"outside","low":row["math"],"high":row["math"],
                    "mid":row["math"],"at":row["day"]+"T12:00:00+00:00",
                    "route":None,"standard":False,"outside":True})
    return sorted(out,key=lambda x:(x["at"],x["id"]),reverse=True)


def estimate(learner: str) -> dict:
    items = _sittings(learner)
    latest = items[0] if items else None
    previous = items[1] if len(items)>1 else None
    best = max(items,key=lambda x:x["mid"]) if items else None
    recent = [x for x in items if (dt.date.today()-dt.date.fromisoformat(x["at"][:10])).days <= 45][:3]
    mean3 = _round10(sum(x["mid"] for x in recent)/len(recent)) if recent else None
    standard = [x for x in items if x["standard"]]
    last3 = standard[:3]
    combined = None
    if len(last3)>=2:
        centre = sum(x["mid"] for x in last3)/len(last3)
        half = 70/math.sqrt(len(last3))
        combined = {"low":max(200,_round10(centre-half)),"high":min(800,_round10(centre+half)),
                    "n":len(last3)}
    last30 = [x for x in standard if (dt.date.today()-dt.date.fromisoformat(x["at"][:10])).days <= 30]
    if not standard:
        confidence = {"level":"low","reason":"Low: only a module or the diagnostic so far. One full section narrows it to about 140 points."}
    elif len(last30)>=2 and max(x["mid"] for x in last30[:3])-min(x["mid"] for x in last30[:3]) <= 100:
        confidence = {"level":"high","reason":f"High: {len(last30[:3])} sections in the last 30 days within 100 points."}
    elif len(standard)==1:
        confidence = {"level":"medium","reason":"Medium: one full section. Two within 100 points of each other make it high."}
    else:
        gap = round(abs(standard[0]["mid"]-standard[1]["mid"])/10)*10
        confidence = {"level":"medium","reason":f"Medium: your last sections are {gap} points apart."}
    delta = round(latest["mid"]-previous["mid"]) if latest and previous else None
    trend = {"direction":"steady" if delta is None or abs(delta)<=20 else ("up" if delta>0 else "down"),
             "delta":delta,"since":previous["at"] if previous else None}
    sections = [x for x in items if x["kind"] in ("mock","section","paper")]
    counted = {"sittings":len(items),"sections":len(sections),
               "modules":sum(x["kind"]=="module" for x in items),
               "diagnostics":sum(x["kind"]=="diagnostic" for x in items)}
    return {"latest":latest,"previous":previous,"best":best,
            "range":{"low":min((x["mid"] for x in items),default=None),
                     "high":max((x["mid"] for x in items),default=None)},
            "mean3":mean3,"combined":combined,"confidence":confidence,"trend":trend,
            "routed_up":{"up":sum(x["route"]=="upper" for x in sections),"sections":len(sections)},
            "counted":counted}


def percentile(sid: str) -> dict:
    row = db.one("SELECT * FROM sessions WHERE id=?",sid)
    if not row or not row["finished"] or not _standard(row):
        return {"ranked":False,"pct":None,"n":0,"why":"not standard"}
    result = json.loads(row["result"] or "{}")
    band = result.get("estimate") or {}
    if not band:
        return {"ranked":False,"pct":None,"n":0,"why":"unscored"}
    earlier = db.rows("SELECT * FROM sessions WHERE learner=? AND kind=? AND finished IS NOT NULL"
                      " AND (finished<? OR (finished=? AND id<?)) ORDER BY finished,id",
                      row["learner"],row["kind"],row["finished"],row["finished"],sid)
    if any(_standard(x) and (row["number"] is None or x["number"]==row["number"]) for x in earlier):
        return {"ranked":False,"pct":None,"n":0,"why":"repeat sitting"}
    peers = []
    for x in db.rows("SELECT * FROM sessions WHERE kind=? AND finished IS NOT NULL"
                     " AND learner IS NOT NULL ORDER BY finished,id",row["kind"]):
        if row["number"] is not None and x["number"] != row["number"]:
            continue
        if _standard(x) and x["learner"] not in {p[0] for p in peers}:
            e = (json.loads(x["result"] or "{}").get("estimate") or {})
            if e.get("low") is not None and e.get("high") is not None:
                peers.append((x["learner"],(e["low"]+e["high"])/2))
    if len(peers)<20:
        return {"ranked":False,"pct":None,"n":len(peers),"why":"too few sittings"}
    mine = (band["low"]+band["high"])/2
    return {"ranked":True,"pct":round(100*sum(score<=mine for _,score in peers)/len(peers)),"n":len(peers)}
