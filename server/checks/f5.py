"""F5 acceptance: one drill body, its pools, and the public type catalogue.

Run with PYTHONPATH=. python3 server/checks/f5.py. The database is temporary;
this check never reads or writes the developer's default database.
"""

from __future__ import annotations

import datetime as dt
import json
import pathlib
import re
import tempfile

from fastapi.testclient import TestClient

from satbank.registry import generate
from server import blueprint, db, deps, practice, progress
from server.app import app


def request(client, body, learner="a:f5pool", *, expect=200, preview=False):
    route = "/api/drill/preview" if preview else "/api/drill"
    result = client.post(route, json=body, headers={"X-Learner": learner})
    assert result.status_code == expect, (body, result.status_code, result.text)
    return result.json()


def question(template="lin.evaluate", seed=71):
    item = generate(template, seed)
    return practice.to_question(practice.Card.of(template, seed, item, practice.topic_of(template)), 1)


def fixtures():
    learner = "a:f5pool"
    now = progress.now()
    old = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=11)).isoformat()
    due = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=1)).date().isoformat()
    q = question(seed=71)
    db.run("INSERT INTO sessions(id,kind,learner,started,finished,questions,answers)"
           " VALUES (?,?,?,?,?,?,?)", "f5-fixture", "drill", learner, old, now,
           json.dumps([q]), json.dumps({q["id"]: 0}))
    db.run("INSERT INTO attempts(learner,session,qid,template,seed,topic,difficulty,fmt,correct,"
           " given,ms,at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", learner, "f5-fixture", q["id"],
           q["key"], q["seed"], q["topic"], q["difficulty"], q["type"], 0, "0", 12000, old)
    db.run("INSERT INTO saved(learner,template,seed,topic,at) VALUES (?,?,?,?,?)",
           learner, q["key"], q["seed"], q["topic"], now)
    db.run("INSERT INTO flags(learner,session,qid,template,seed,topic,at) VALUES (?,?,?,?,?,?,?)",
           learner, "f5-fixture", q["id"], q["key"], q["seed"], q["topic"], now)
    db.run("INSERT INTO sets(code,owner,kind,items,created) VALUES (?,?,?,?,?)",
           "F5SET", learner, "set", json.dumps([[q["key"], q["seed"]]]), now)
    trap = progress.record_trap(learner, q, next(r for r in q["reasons"] if r), now)
    q2 = question("pct.change", 72)
    db.run("INSERT INTO attempts(learner,qid,template,seed,topic,difficulty,fmt,correct,given,at)"
           " VALUES (?,?,?,?,?,?,?,?,?,?)", learner, "old-right", q2["key"], q2["seed"],
           q2["topic"], q2["difficulty"], q2["type"], 1, "0", old)
    check = progress.record_trap(learner, q2, progress.offered_of(q2)[0], old)
    db.run("UPDATE traps SET closed=?,closed_how='fixed',due=?,checks=0,owed=0 WHERE id=?",
           old, due, check["id"])
    return q, trap, check


def trap_true_checks(client):
    learner = "a:f5traptrue"
    headers = {"X-Learner": learner}
    first_set = request(client, {"templates": ["lin.evaluate"], "formats": ["mcq"], "count": 1},
                        learner=learner)
    sid = first_set["id"]
    first = json.loads(db.one("SELECT questions FROM sessions WHERE id=?", sid)["questions"])[0]
    wrong = next(i for i, reason in enumerate(first["reasons"])
                 if reason and i != "ABCD".index(first["answer"]))
    norm = progress.norm(first["reasons"][wrong])
    client.post(f"/api/drill/{sid}/answer", headers=headers,
                json={"question_id": first["id"], "answer": wrong}).raise_for_status()
    repair_result = client.post(f"/api/drill/{sid}/next", headers=headers)
    repair_result.raise_for_status()
    repair = json.loads(db.one("SELECT questions FROM sessions WHERE id=?", sid)["questions"])[1]
    assert repair_result.json()["question"]["repair"] and repair["seed"] != first["seed"]
    assert norm in progress.offered_of(repair), (norm, progress.offered_of(repair))
    right = "ABCD".index(repair["answer"]) if repair["type"] == "mcq" else repair["answer"]
    client.post(f"/api/drill/{sid}/answer", headers=headers,
                json={"question_id": repair["id"], "answer": right}).raise_for_status()
    assert progress.open_traps(learner)[0]["owed"] == 1

    fix = request(client, {"mistakes": True}, learner=learner)
    assert fix["total"] == 2
    for index in range(2):
        served = json.loads(db.one("SELECT questions FROM sessions WHERE id=?", fix["id"])["questions"])[-1]
        assert norm in progress.offered_of(served), (norm, progress.offered_of(served))
        right = "ABCD".index(served["answer"]) if served["type"] == "mcq" else served["answer"]
        client.post(f"/api/drill/{fix['id']}/answer", headers=headers,
                    json={"question_id": served["id"], "answer": right}).raise_for_status()
        if index == 0:
            assert not progress.open_traps(learner)
        client.post(f"/api/drill/{fix['id']}/next", headers=headers).raise_for_status()
    assert not progress.open_traps(learner)

    # An unnamed grid-in trap has no offer requirement and still owes two clean answers.
    unnamed = "a:f5unnamed"
    q = question("pct.change", 72)
    progress.record_trap(unnamed, q, "", progress.now())
    fix = request(client, {"mistakes": True}, learner=unnamed)
    assert fix["total"] == 2
    for index in range(2):
        served = json.loads(db.one("SELECT questions FROM sessions WHERE id=?", fix["id"])["questions"])[-1]
        right = "ABCD".index(served["answer"]) if served["type"] == "mcq" else served["answer"]
        client.post(f"/api/drill/{fix['id']}/answer", headers={"X-Learner": unnamed},
                    json={"question_id": served["id"], "answer": right}).raise_for_status()
        assert [t["owed"] for t in progress.open_traps(unnamed)] == ([1] if index == 0 else [])
        client.post(f"/api/drill/{fix['id']}/next", headers={"X-Learner": unnamed}).raise_for_status()


def checks(client):
    learner = "a:f5pool"
    q, trap, check = fixtures()
    before = db.one("SELECT COUNT(*) n FROM sessions")["n"]
    preview = request(client, {"topics": ["linear_functions"], "count": 3}, preview=True)
    assert preview["servable"] and preview["types"] > 0 and preview["questions"] is None
    assert "saved" in preview["pools"] and "marked" in preview["pools"]
    assert db.one("SELECT COUNT(*) n FROM sessions")["n"] == before
    empty = request(client, {"pool": "redo"}, learner="a:f5empty", preview=True)
    assert empty["reason"] == "no_open_mistakes" and not empty["servable"]
    request(client, {"pool": "redo"}, learner="a:f5empty", expect=409)
    assert db.one("SELECT COUNT(*) n FROM sessions WHERE learner='a:f5empty'")["n"] == 0

    # Every canonical pool resolves; aliases retain the old callers' bodies.
    cases = [
        {"pool": "new", "topics": ["linear_functions"]},
        {"pool": "redo", "ids": [trap["id"]]},
        {"pool": "checks", "ids": [check["id"]]},
        {"pool": "review"},
        {"pool": "untried", "topics": ["linear_functions"]},
        {"pool": "seen"},
        {"pool": "saved"},
        {"pool": "marked"},
        {"pool": "history", "ids": [db.one("SELECT id FROM attempts WHERE session='f5-fixture'")["id"]]},
        {"pool": "items", "ids": [[q["key"], q["seed"]]]},
        {"pool": "set", "ids": "F5SET"},
        {"pool": "official", "ids": ["84664a7c"]},
        {"list": "fixed"}, {"mistakes": True}, {"saved": True},
        {"list": "templates", "ids": ["lin.evaluate"]},
        {"unseen": True, "topics": ["linear_functions"]},
        {"recheck": True}, {"share": "F5SET"},
        {"trap": {"template": q["key"], "reason": trap["norm"]}},
    ]
    related = progress.related()
    if related:
        cases.append({"pool": "related", "ids": next(iter(related))})
    for body in cases:
        result = request(client, {**body, "count": 1})
        assert result["question"] and result["question"]["why"], body
    t_only = request(client, {"templates": ["lin.evaluate"], "count": 1})
    stored = json.loads(db.one("SELECT questions FROM sessions WHERE id=?", t_only["id"])["questions"])
    assert stored[0]["key"] == "lin.evaluate"
    assert request(client, {"again": t_only["id"], "count": 1})["question"]
    assert request(client, {"from_session": "f5-fixture", "scope": "all",
                            "only": [q["id"]], "count": 1})["question"]
    assert request(client, {"retake": "f5-fixture", "count": 1})["question"]
    assert request(client, {"item": f"{q['key']}:{q['seed']}", "count": 1})["question"]
    assert request(client, {"topics": ["linear_functions"], "difficulty": "adaptive",
                            "count": 1})["question"]
    hard = request(client, {"topics": ["linear_functions"], "tiers": ["hard"], "count": 1})
    assert hard["question"]["difficulty"] == "hard"
    spr = request(client, {"topics": ["linear_functions"], "format": "grid", "count": 1})
    assert spr["question"]["type"] == "spr"
    assert request(client, {"topics": ["linear_functions"], "fmt": "both", "count": 1})["question"]
    level = request(client, {"topics": ["linear_functions"], "levels": [1],
                             "unmeasured": False}, expect=409)
    assert "level 1" in level["detail"]["reason"]
    for bad in ({"count": 121}, {"tiers": ["impossible"]}, {"templates": ["not.real"]},
                {"formats": []}, {"want": {"lin.evaluate": "["}}, {"assignment": "abc"}):
        request(client, bad, expect=422)

    # A public set code does not grant access to an exact unshown item.
    request(client, {"pool": "items", "ids": [["lin.evaluate", 999]], "exact": True}, expect=403)
    exact = request(client, {"pool": "items", "ids": [[q["key"], q["seed"]]], "exact": True,
                             "count": 1})
    same = json.loads(db.one("SELECT questions FROM sessions WHERE id=?", exact["id"])["questions"])[0]
    assert same["seed"] == q["seed"]

    # Want walks fresh seeds and a repair retains the named norm.
    data = blueprint.kinds()["lin.evaluate"]
    norm = next(iter(data["reasons"]))
    wanted = request(client, {"templates": ["lin.evaluate"], "want": {"lin.evaluate": "^" + re.escape(norm) + "$"},
                              "count": 1}, learner="a:f5want")
    first = json.loads(db.one("SELECT questions FROM sessions WHERE id=?", wanted["id"])["questions"])[0]
    if first["trap_true"]:
        assert any(progress.norm(r or "") == norm for r in first["reasons"])

    # Inline answers count as attempts and show feedback, but not as sittings.
    inline = request(client, {"source": "twin", "templates": ["lin.evaluate"], "count": 1},
                     learner="a:f5inline")
    sid = inline["id"]
    row = db.one("SELECT cfg,questions FROM sessions WHERE id=?", sid)
    assert json.loads(row["cfg"])["inline"]
    served = json.loads(row["questions"])[0]
    answer = "ABCD".index(served["answer"]) if served["type"] == "mcq" else served["answer"]
    feedback = client.post(f"/api/drill/{sid}/answer", headers={"X-Learner": "a:f5inline"},
                           json={"question_id": served["id"], "answer": answer}).json()
    for key in ("reasons", "filler", "family", "flagged", "repeat", "opened_ids", "closed_ids"):
        assert key in feedback, (key, feedback)
    client.post(f"/api/drill/{sid}/finish", headers={"X-Learner": "a:f5inline"})
    assert db.one("SELECT COUNT(*) n FROM attempts WHERE session=?", sid)["n"] == 1
    history = client.get("/api/history", headers={"X-Learner": "a:f5inline"}).json()["sessions"]
    assert all(x["id"] != sid for x in history)

    catalogue = client.get("/api/types").json()
    assert len(catalogue) >= 386 and all("answer" not in x for x in catalogue)
    detail = client.get("/api/types/lin.evaluate").json()
    assert all(k in detail for k in ("name", "about", "subject", "weight", "siblings"))
    assert "you" not in detail
    assert "you" in client.get("/api/types/lin.evaluate", headers={"X-Learner": learner}).json()
    example = client.get("/api/types/lin.evaluate/example").json()
    assert example["seed"] >= 900_000 and "answer" in example["question"]
    assert client.get("/api/types/match?id=23c5fcce").json()["rows"][0]["topic"] == "circles"
    before = db.one("SELECT COUNT(*) n FROM attempts WHERE learner=?", "a:f5outside")["n"]
    logged = client.post("/api/mistakes/log", headers={"X-Learner": "a:f5outside"},
                         json={"template": "lin.evaluate", "reason": data["reasons"][norm],
                               "origin": "bluebook", "where_note": "From a practice test"})
    assert logged.status_code == 200, logged.text
    assert db.one("SELECT COUNT(*) n FROM attempts WHERE learner=?", "a:f5outside")["n"] == before
    tid = logged.json()["trap"]["id"]
    assert db.one("SELECT source,origin FROM traps WHERE id=?", tid)["source"] == "outside"
    assert client.post("/api/mistakes/log", headers={"X-Learner": "a:f5outside"},
                       json={"template": "bad.template"}).status_code == 422
    trap_true_checks(client)


def check(client):
    checks(client)
    print("ok  F5 pools, aliases, filters, preview, types, feedback and inline history")


if __name__ == "__main__":
    with tempfile.TemporaryDirectory(prefix="satf-f5-") as folder:
        db.DB_PATH = pathlib.Path(folder) / "f5.db"
        db.init()
        with TestClient(app) as client:
            check(client)
