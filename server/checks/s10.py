"""S10 Review server checks. Run with SATF_DB=$PWD/server/s10.db PYTHONPATH=."""

from __future__ import annotations

import json
import os
import secrets
import datetime as dt

from fastapi.testclient import TestClient

from satbank.registry import generate
from server import db, practice, progress
from server.app import app


def main() -> None:
    path = os.environ.get("SATF_DB", "")
    assert path.endswith("/server/s10.db"), "set SATF_DB=$PWD/server/s10.db"
    owner = "a:s10check" + secrets.token_hex(5)
    outsider = "a:s10other" + secrets.token_hex(5)
    h, other = {"X-Learner": owner}, {"X-Learner": outsider}
    with TestClient(app) as c:
        def call(method, path, *, headers=h, want=200, **kwargs):
            response = c.request(method, path, headers=headers, **kwargs)
            assert response.status_code == want, (path, response.status_code, response.text)
            return response.json()

        counts = call("GET", "/api/review/counts")
        assert counts["open"] == counts["saved"] == counts["marked"] == 0
        due = call("GET", "/api/review/due")
        assert due["cap"] == 6 and due["median_s"] == 95
        assert call("GET", "/api/review/ledger")["open"] == 0
        assert call("GET", "/api/review/calibration")["matrix"]["sure"]["wrong"] == 0
        assert call("GET", "/api/review/trapsheet")["entries"] == []
        assert call("GET", "/api/review/counts", params={"subject": "rw"})["open"] == 0
        call("GET", "/api/review/counts", params={"subject": "science"}, want=422)
        print("ok  empty learner has complete Review summaries")

        due_owner = "a:s10due" + secrets.token_hex(5)
        old = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=4)).isoformat()
        progress.record_trap(due_owner, {"key": "lin.evaluate", "seed": 71,
                                         "topic": "linear_functions"}, "Added instead of multiplying", old)
        due_h = {"X-Learner": due_owner}
        day = call("GET", "/api/review/due", headers=due_h)
        assert day["left"] == 1 and len(day["items"]) == 1
        key = day["items"][0]["key"]
        assert call("POST", "/api/review/snooze", headers=due_h, json={"key": key})["left"] == 0
        assert call("GET", "/api/review/counts", headers=due_h)["due_left"] == 0
        assert call("POST", "/api/review/snooze", headers=due_h,
                    json={"key": key, "undo": True})["left"] == 1
        call("POST", "/api/review/snooze", headers=due_h, json={"key": "due:wrong:key"}, want=404)
        print("ok  one frozen due item snoozes and returns for the same learner")

        blank_owner = "a:s10blank" + secrets.token_hex(5)
        blank_h = {"X-Learner": blank_owner}
        raw = generate("lin.evaluate", 71)
        blank_q = practice.to_question(practice.Card.of("lin.evaluate", 71, raw, "linear_functions"), 1)
        db.run("INSERT INTO sessions(id,kind,learner,started,finished,questions,answers)"
               " VALUES (?,?,?,?,?,?,'{}')", "s10-blank-" + blank_owner[2:], "module", blank_owner,
               progress.now(), progress.now(), json.dumps([blank_q]))
        blank_sid = "s10-blank-" + blank_owner[2:]
        blank_walk = call("POST", "/api/review/walk", headers=blank_h, json={"session": blank_sid})
        assert blank_walk["n"] == blank_walk["blanks"] == 1
        blank_cfg = json.loads(db.one("SELECT cfg FROM sessions WHERE id=?", blank_walk["id"])["cfg"])
        assert blank_cfg["walk"]["items"][0]["blank"]
        call("POST", f"/api/review/walk/{blank_walk['id']}/at", headers=blank_h,
             json={"i": 0, "step": "why", "diag": "skip"})
        assert db.one("SELECT COUNT(*) AS n FROM attempts WHERE learner=?", blank_owner)["n"] == 0
        print("ok  a finished test's blank question enters the walk without filing an attempt")

        started = call("POST", "/api/drill", json={"templates": ["lin.evaluate"], "formats": ["mcq"], "count": 1})
        sid = started["id"]
        q = json.loads(db.one("SELECT questions FROM sessions WHERE id=?", sid)["questions"])[0]
        params = {"template": q["key"], "seed": q["seed"]}
        call("GET", "/api/review/item", params=params, want=404)
        call("GET", "/api/review/item", params=params, headers=other, want=404)
        call("POST", "/api/saved", json={"session": sid, "question_id": q["id"], "note": "check signs"})
        kept = call("GET", "/api/review/item", params=params)
        assert kept["saved"] and kept["access"] == "kept" and kept["answer"] is None
        assert call("GET", "/api/review/saved")["items"][0]["note"] == "check signs"
        call("POST", "/api/flags", json={"session": sid, "question_id": q["id"]}, headers=other, want=403)
        call("POST", "/api/flags", json={"session": sid, "question_id": q["id"]})
        assert call("GET", "/api/review/marked")["items"][0]["qid"] == q["id"]
        print("ok  saved and marked keep ownership and hide an unseen key")

        wrong = next(i for i in range(4) if "ABCD"[i] != q["answer"] and q["reasons"][i])
        call("POST", f"/api/drill/{sid}/answer", json={"question_id": q["id"], "answer": wrong})
        a = db.one("SELECT * FROM attempts WHERE learner=? ORDER BY id DESC LIMIT 1", owner)
        redo = call("GET", "/api/review/redo")
        assert redo["total"] == 1 and redo["items"][0]["id"] > 0 and redo["items"][0]["owed"] == 2
        assert {"attempt", "level", "habit", "stuck", "blind", "pts", "rule"} <= redo["items"][0].keys()
        assert call("GET", "/api/review/counts")["open"] == 1
        history = call("GET", "/api/review/history")
        assert history["items"][0]["result"] == "wrong" and history["summary"]["answers"] == 1
        csv = c.get("/api/review/history.csv", headers=h)
        assert csv.status_code == 200 and q["key"] in csv.text
        item = call("GET", "/api/review/item", params=params)
        assert item["access"] == "reveal" and item["answer"] == q["answer"]
        assert {"story", "path", "summary", "level", "budget_ms", "domain", "has_steps"} <= item.keys()
        assert call("GET", "/api/review/family", params={"template": q["key"]})["summary"]["wrong"] == 1
        print("ok  a miss appears in Redo, History, the CSV and question detail")

        call("POST", "/api/review/why", json={"attempt_id": a["id"], "diag": a["norm"]}, headers=other, want=404)
        first = call("POST", "/api/review/why", json={"attempt_id": a["id"], "diag": a["norm"]})
        assert first["called"]
        second = call("POST", "/api/review/why", json={"attempt_id": a["id"], "diag": "misread"})
        assert second["diag"] == a["norm"]
        seen = call("POST", "/api/review/seen", json={"attempt_id": a["id"]})
        assert seen == call("POST", "/api/review/seen", json={"attempt_id": a["id"]})
        walk = call("POST", "/api/review/walk", json={"ids": [redo["items"][0]["id"]]})
        cfg = json.loads(db.one("SELECT cfg FROM sessions WHERE id=?", walk["id"])["cfg"])
        assert walk["n"] == 1 and cfg["inline"] and cfg["walk"]["items"][0]["attempt"] == a["id"]
        call("POST", f"/api/review/walk/{walk['id']}/at", json={"i": 0, "step": "key"}, headers=other, want=403)
        call("POST", f"/api/review/walk/{walk['id']}/at", json={"i": 0, "step": "key"})
        print("ok  diagnosis is one-time, reveal idempotent, walk is inline and owned")

        call("POST", "/api/mistakes/dismiss", json={"id": redo["items"][0]["id"]})
        assert call("GET", "/api/review/redo")["total"] == 0
        assert call("GET", "/api/review/fixed")["items"][0]["closed_how"] == "dismissed"
        call("POST", "/api/mistakes/restore", json={"id": redo["items"][0]["id"]})
        assert call("GET", "/api/review/redo")["total"] == 1
        print("ok  dismiss and restore preserve the trap")

        before_spot = db.one("SELECT COUNT(*) AS n FROM attempts WHERE learner=?", owner)["n"]
        spot = call("POST", "/api/review/spot", json={"trap_id": redo["items"][0]["id"]})
        result = call("POST", f"/api/review/spot/{spot['id']}", json={"answer": 0})
        assert spot["question"]["stem"] and result["trap_index"] is not None
        assert db.one("SELECT COUNT(*) AS n FROM attempts WHERE learner=?", owner)["n"] == before_spot
        call("POST", f"/api/review/spot/{spot['id']}", json={"answer": 0}, headers=other, want=403)
        print("ok  Spot the Trap names the option without filing an attempt")

        share = call("POST", "/api/shares", json={"items": [[q["key"], q["seed"]]], "title": "One item"})
        card = call("GET", f"/api/shares/{share['id']}")
        assert card["count"] == 1 and "stem" not in card
        twin = call("POST", "/api/drill", headers=other,
                    json={"list": "share", "ids": share["id"], "exact": True, "count": 1})
        other_q = json.loads(db.one("SELECT questions FROM sessions WHERE id=?", twin["id"])["questions"])[0]
        assert other_q["stem"] == q["stem"] and other_q["seed"] == q["seed"]
        print("ok  a share exposes no stem until its exact set starts")

        discarded = call("POST", f"/api/session/{sid}/void")
        assert discarded["answers"] == 1
        assert call("GET", "/api/review/history", params={"result": "discarded"})["total"] == 1
        assert call("GET", "/api/review/history")["summary"]["answers"] == 0
        call("POST", f"/api/session/{sid}/void", want=409)
        assert call("POST", f"/api/session/{sid}/unvoid")["answers"] == 1
        assert call("GET", "/api/review/history")["summary"]["answers"] == 1
        call("POST", f"/api/session/{sid}/void", headers=other, want=403)
        print("ok  discard and restore adjust History and require ownership")

        next_run = call("POST", "/api/drill", json={"templates": ["lin.evaluate"],
                                                    "formats": ["mcq"], "count": 1})
        next_q = json.loads(db.one("SELECT questions FROM sessions WHERE id=?", next_run["id"])["questions"])[0]
        call("POST", f"/api/drill/{next_run['id']}/answer",
             json={"question_id": next_q["id"], "answer": "ABCD".index(next_q["answer"]), "ms": 180000})
        slow = call("GET", "/api/review/history", params={"result": "slow"})
        assert slow["total"] == 1 and slow["summary"]["slow"]["over_ms"] > 0
        first_page = call("GET", "/api/review/history", params={"limit": 1})
        second_page = call("GET", "/api/review/history", params={"limit": 1, "cursor": first_page["next"]})
        assert first_page["items"][0]["id"] > second_page["items"][0]["id"]
        assert call("GET", "/api/review/history")["summary"]["answers"] == call("GET", "/api/review/counts")["answers"]
        print("ok  slow answers, cursor pages and Review counts agree")

    print("S10 checks passed")


def check(client: TestClient) -> None:
    """Entry point used by server/test_flow.py's check discovery."""
    main()


if __name__ == "__main__":
    main()
