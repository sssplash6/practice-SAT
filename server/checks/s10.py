"""S10 Review server checks. Run with SATF_DB=$PWD/server/s10.db PYTHONPATH=."""

from __future__ import annotations

import json
import os
import secrets

from fastapi.testclient import TestClient

from server import db
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
        print("ok  empty learner has complete Review summaries")

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
        assert call("GET", "/api/review/counts")["open"] == 1
        history = call("GET", "/api/review/history")
        assert history["items"][0]["result"] == "wrong" and history["summary"]["answers"] == 1
        csv = c.get("/api/review/history.csv", headers=h)
        assert csv.status_code == 200 and q["key"] in csv.text
        item = call("GET", "/api/review/item", params=params)
        assert item["access"] == "reveal" and item["answer"] == q["answer"]
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

    print("S10 checks passed")


if __name__ == "__main__":
    main()
