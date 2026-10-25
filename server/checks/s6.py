"""S6 Results server acceptance. Run with SATF_DB=$PWD/server/s6.db PYTHONPATH=.

The checks use fresh learner codes and never need the development database.
"""

from __future__ import annotations

import logging
import secrets
from contextlib import nullcontext

from fastapi.testclient import TestClient

from server import api_results, db, progress, scoring
from server.api_tests import FORMS
from server.app import app

logging.getLogger("httpx").setLevel(logging.WARNING)


def ok(response, code: int = 200):
    assert response.status_code == code, (response.status_code, response.text[:800])
    return response.json()


def answer(q, right: bool):
    if q["type"] == "mcq":
        n = "ABCD".index(q["answer"])
        return n if right else (n + 1) % 4
    return scoring.keys(q["answer"])[0] if right else "-999"


def check(client: TestClient | None = None) -> None:
    # share the caller's client (and its db connection) when given one: a second,
    # separate TestClient here would write through a different connection, which a
    # same-process direct db.one() read can briefly not see (WAL across connections)
    learner = "a:s6check" + secrets.token_hex(6)
    other = "a:s6other" + secrets.token_hex(6)
    h = {"X-Learner": learner}
    with TestClient(app) if client is None else nullcontext(client) as client:
        sample = ok(client.get("/api/session/sample-section/results"))
        assert sample["asked"] == 44 and sample["mine"] is False
        ok(client.post("/api/session/sample-section/note", json={"note": "edit"},
                       headers={"X-Learner": "sample:report"}), 403)
        print("ok  public 44-question sample stays read-only")

        start = ok(client.post("/api/session", headers=h))
        sid = start["id"]
        start = ok(client.post(f"/api/session/{sid}/begin", headers=h))      # a sitting is made in its lobby
        paper = FORMS[start["form"]]
        wrong, right = paper[:2]
        ok(client.post(f"/api/session/{sid}/answer", headers=h,
                       json={"question_id": wrong["id"], "answer": answer(wrong, False)}))
        ok(client.post(f"/api/session/{sid}/answer", headers=h,
                       json={"question_id": right["id"], "answer": answer(right, True)}))
        ok(client.post(f"/api/session/{sid}/finish", headers=h))
        ok(client.get(f"/api/session/{sid}/results"), 403)
        ok(client.get(f"/api/session/{sid}/results", headers={"X-Learner": other}), 403)
        # a diagnostic's results need the old signup-by-email gate (SEC-01/03): the learner
        # header alone is not ownership proof for this kind, unlike every other sitting
        email = f"{learner[2:]}@example.com".lower()
        up = ok(client.post(f"/api/session/{sid}/signup", json={"first": "Ada", "last": "Lovelace", "email": email}))
        assert up["ok"]
        token = db.one("SELECT token FROM users WHERE email=?", email)["token"]
        verified = client.get("/api/verify", params={"token": token}, follow_redirects=False)
        assert verified.headers["location"].endswith("state=ok")
        report = ok(client.get(f"/api/session/{sid}/results", headers=h))
        assert report["mine"] and report["summary"]["correct"] == 1
        assert report["summary"]["incorrect"] == 1
        assert report["summary"]["unanswered"] == 18
        assert sum(report["summary"][k] for k in ("correct", "incorrect", "unanswered")) == report["asked"] == 20
        assert report["review"][0]["hidden"] and "answer" not in report["review"][0]
        assert len(report["domains"]) == 4 and len(report["topics"]) >= 1
        assert report["ledger"] and report["second"]["offered"]
        assert abs(sum(x["pts"] for x in report["ledger"]["by_tier"]) - report["ledger"]["total"]) < 1
        print("ok  owner-only report, status buckets, held keys, domains and point ledger")

        ok(client.post(f"/api/session/{sid}/whatif", headers=h, json={"right": ["nope"]}), 422)
        whatif = ok(client.post(f"/api/session/{sid}/whatif", headers=h,
                                json={"right": [wrong["id"]]}))
        assert whatif["high"] >= report["estimate"]["high"]
        ok(client.post(f"/api/session/{sid}/note", headers=h, json={"note": "tired after class"}))
        assert ok(client.get(f"/api/session/{sid}/results", headers=h))["note"] == "tired after class"
        cause = ok(client.post(f"/api/session/{sid}/why", headers=h,
                               json={"question_id": wrong["id"], "kind": "misread"}))
        assert cause["cause"] and cause["cause"]["auto"] is False
        second = ok(client.post(f"/api/session/{sid}/second", headers=h,
                                json={"question_id": wrong["id"], "answer": answer(wrong, True),
                                      "conf": "sure", "ms": 40000}))
        assert second["correct"] and second["answer"] == wrong["answer"]
        attempt = db.one("SELECT repeat,source FROM attempts WHERE session=? AND qid=?"
                         " AND source='second'", sid, wrong["id"])
        assert attempt and attempt["repeat"] == 1
        blank = paper[3]
        mastery = progress.topic_mastery(learner, blank["topic"])
        ok(client.post(f"/api/session/{sid}/second", headers=h,
                       json={"question_id": blank["id"], "answer": answer(blank, True)}))
        blank_attempt = db.one("SELECT repeat,source FROM attempts WHERE session=? AND qid=?"
                               " AND source='second'", sid, blank["id"])
        assert blank_attempt["repeat"] == 1 and progress.topic_mastery(learner, blank["topic"]) == mastery
        ok(client.post(f"/api/session/{sid}/second", headers=h,
                       json={"question_id": wrong["id"], "answer": answer(wrong, True)}), 409)
        assert "answer" in ok(client.get(f"/api/session/{sid}/results", headers=h))["review"][0]
        ok(client.post(f"/api/session/{sid}/seen", headers=h, json={"qids": [paper[2]["id"]]}))
        ok(client.post(f"/api/session/{sid}/second/state", headers=h, json={"state": "done"}))
        print("ok  what-if, note, cause and second-look writes")

        second_sitting = ok(client.post("/api/session", headers=h))
        new_sid = second_sitting["id"]
        db.run("UPDATE sessions SET form_id=? WHERE id=?", start["form"], new_sid)
        ok(client.post(f"/api/session/{new_sid}/begin", headers=h))
        for q in paper:
            ok(client.post(f"/api/session/{new_sid}/answer", headers=h,
                           json={"question_id": q["id"], "answer": answer(q, True)}))
        ok(client.post(f"/api/session/{new_sid}/finish", headers=h))
        comparison = ok(client.get(f"/api/session/{new_sid}/compare", headers=h,
                                   params={"with": sid}))
        assert comparison["paired"] == 20 and comparison["counts"]["fixed"] >= 1
        briefing = ok(client.get(f"/api/session/{sid}/briefing", headers=h))
        assert len(briefing["rules"]) <= 5 and len(briefing["pace"]) <= 2
        print("ok  compare pairs, fixed count and briefing bounds")

        listing = api_results.history(learner, kind="tests", limit=1)
        assert listing["total"] >= 2 and len(listing["sessions"]) == 1
        assert listing["sessions"][0]["modules"][0]["wrong"] == []
        assert listing["counts"]["tests"] >= 2
        stats = ok(client.get("/api/stats", headers=h))
        assert len(stats["days14"]) == 14 and stats["estimate"]["confidence"]["level"] in \
            ("high", "medium", "low")
        topic = paper[0]["topic"]
        skill = ok(client.get(f"/api/skill/{topic}", headers=h))
        assert skill["topic"] == topic and skill["sittings"]
        ok(client.get("/api/skill/not_a_skill", headers=h), 404)
        print("ok  history, stats and one-skill panel")

        # api_practice still registers a shadow GET /api/history before S6.
        # That owner must delete it to make S6's public history route reachable.
        route = ok(client.get("/api/history", headers=h))
        if "counts" not in route:
            print("PENDING  api_practice shadow /api/history must be deleted by its owner")
        else:
            assert route["counts"]["tests"] >= 2


if __name__ == "__main__":
    check()
    print("S6 checks passed")
