"""S1 Account and Me server acceptance checks.

Run with SATF_DB=$PWD/server/s1.db PYTHONPATH=. python3 server/checks/s1.py.
"""

from __future__ import annotations

import os
import secrets
from unittest.mock import patch

from fastapi.testclient import TestClient

from server.app import app
from server import db


def check(c: TestClient) -> None:
    learner = "a:s1check" + secrets.token_hex(5)
    h = {"X-Learner": learner}
    names = "streak,open_mistakes,due_today"
    response = c.get("/api/levers", params={"keys": names}, headers=h)
    assert response.status_code == 200, response.text
    levers = response.json()["levers"]
    assert set(levers) == set(names.split(","))
    for name in names.split(","):
        fact = levers[name]
        assert fact["how"] and fact["inputs"] and "excluded" in fact and "same_on" in fact
    me = c.get("/api/me", headers=h).json()
    assert levers["streak"]["value"] == me["days"]["streak"]
    assert levers["open_mistakes"]["value"] == me["review"]["open"]
    assert levers["due_today"]["value"] == me["review"]["due_left"]
    print("ok  G6 levers explain streak, open mistakes and due today from the same readers")

    more = c.get("/api/levers", params={"keys": "skill:circles,accuracy:circles:30,pace:circles,"
                                                   "minutes:today,points,estimate,readiness"}, headers=h)
    assert more.status_code == 200, more.text
    assert all(x["how"] and x["inputs"] for x in more.json()["levers"].values())
    assert c.get("/api/levers", params={"keys": ",".join(["streak"] * 21)}, headers=h).status_code == 422
    assert c.get("/api/levers", params={"keys": "skill:not_a_topic"}, headers=h).status_code == 422
    assert c.get("/api/levers", params={"keys": "percentile:someone-elses-sitting"}, headers=h).status_code == 404
    print("ok  G6 dynamic facts are bounded and cannot read another sitting")

    # SEC-01: an unrelated completed sitting cannot alter a saved account.
    victim = "s1-victim-" + secrets.token_hex(6) + "@example.org"
    victim_id = secrets.token_urlsafe(12)
    sid = secrets.token_urlsafe(12)
    other_sid = secrets.token_urlsafe(12)
    db.run("INSERT INTO users (id,first,last,email,verified,created) VALUES (?,?,?,?,1,?)",
           victim_id, "Original", "Student", victim, "2026-09-01T00:00:00+00:00")
    for session_id in (sid, other_sid):
        db.run("INSERT INTO sessions (id,kind,started,finished) VALUES (?,?,?,?)",
               session_id, "diagnostic", "2026-09-01T00:00:00+00:00",
               "2026-09-01T00:30:00+00:00")
    with patch("server.api_account.mail.send", return_value="outbox"):
        known = c.post(f"/api/session/{sid}/signup", json={
            "first": "Changed", "last": "Name", "email": victim}).json()
        fresh = c.post(f"/api/session/{other_sid}/signup", json={
            "first": "Changed", "last": "Name", "email": "fresh-" + victim}).json()
    assert known == fresh == {"ok": True, "first": "Changed", "verified": False, "email": "outbox"}
    assert tuple(db.one("SELECT first,last FROM users WHERE id=?", victim_id)) == ("Original", "Student")
    assert db.one("SELECT user_id FROM sessions WHERE id=?", sid)["user_id"] is None
    token = db.one("SELECT token FROM signup_claims WHERE session=?", sid)["token"]
    assert c.get("/api/verify", params={"token": token}, follow_redirects=False).headers[
        "location"].endswith("state=ok")
    assert db.one("SELECT user_id FROM sessions WHERE id=?", sid)["user_id"] == victim_id
    assert c.get("/api/verify", params={"token": token}, follow_redirects=False).headers[
        "location"].endswith("state=bad")
    print("ok  SEC-01 signup requires fresh mailbox proof and does not disclose account status")


def main() -> None:
    assert os.environ.get("SATF_DB", "").endswith("/server/s1.db"), "set SATF_DB=$PWD/server/s1.db"
    with TestClient(app) as c:
        check(c)
    print("S1 checks passed")


if __name__ == "__main__":
    main()
