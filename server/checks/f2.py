"""F2: /api/shell's shape, one streak, resume, retired codes and the parts registry."""

from __future__ import annotations

from unittest.mock import patch

from server import api_shell, db

KEYS = {"me", "streak", "best_streak", "today", "plan", "tested_today", "mistakes", "saved", "challenge", "resume",
        "newest_report", "report_replies", "new", "prefs", "pref_source", "stage", "next", "goals", "inbox",
        "registration", "device", "dates", "spares", "review", "words", "answered", "has", "report"}


def check(c) -> None:
    H = {"X-Learner": "a:v2revshellA", "X-Tz": "0"}
    s = c.get("/api/shell", headers=H).json()
    assert KEYS <= set(s), KEYS - set(s)
    assert "assignments" not in s and "role" not in s["me"], "no classes (v2-decisions 5)"
    assert s["answered"] == 0 and s["resume"] is None and s["plan"] is None and s["prefs"]["theme"] == "light"
    assert len(s["me"]["domains"]["math"]) == 4 and s["me"]["avatar"]["kind"] == "mark"

    d = c.post("/api/drill", headers=H, json={"topics": ["circles"], "count": 3}).json()
    q = c.post(f"/api/drill/{d['id']}/next", headers=H).json()["question"]
    c.post(f"/api/drill/{d['id']}/answer", headers=H, json={"question_id": q["id"], "answer": 0})
    c.put("/api/me", headers=H, json={"exam_date": "2099-11-07", "minutes": 45, "days": "1111111"})
    s = c.get("/api/shell", headers=H).json()
    me = c.get("/api/me", headers=H).json()
    assert s["answered"] == 1 and s["today"]["questions"] == 1
    assert s["streak"] == me["days"]["streak"] == 1, "one streak"
    assert s["resume"]["id"] == d["id"] and s["resume"]["href"].endswith(d["id"])
    assert s["plan"]["per_session"] == 28 and s["today"]["goal"] == {"minutes": 45, "questions": 28}
    assert all(0 <= x <= 1 for x in s["me"]["domains"]["math"])

    db.run("INSERT OR IGNORE INTO retired(code, \"into\", at) VALUES ('a:v2revshellgone', NULL, 'now')")
    assert c.get("/api/shell", headers={"X-Learner": "a:v2revshellgone"}).json() == {"retired": True}
    assert c.get("/api/shell", headers={"X-Learner": "d:" + "0" * 32}).json() == {"retired": True}

    def fake(module, name):
        if name == "shell_part" and module == "words":
            return lambda learner, tz: {"words": {"due": 12}, "new": {"achievements": [{"id": "x"}]}}
        if name == "shell_part" and module == "plan":
            return lambda learner, tz: 1 / 0
        return None
    with patch.object(api_shell, "part", fake), patch.object(api_shell.log, "exception") as logged:
        s = c.get("/api/shell", headers=H).json()
    assert s["words"] == {"due": 12} and s["new"]["achievements"] == [{"id": "x"}], "a part merges in"
    assert s["plan"]["per_session"] == 28 and logged.called, "a failing part is logged and the rest stands"
    print("ok  /api/shell: every key, one streak, resume, retired codes, and parts merged (a broken one skipped)")
