"""Email-only access (2026-10-20): deps.learner_of refuses a code with no learner row (401 {signin}),
and account.beta_account is the one way in: an approved-list address (or one already linked) opens an
account, a new one after a full name, and a learner from before the switch keeps its access and may link
an address. The test flow runs with the gate off (its learners are anonymous); this check turns it on.
Run with test_flow.py, or: SATF_DB=$PWD/server/eo.db PYTHONPATH=. python3 server/checks/email_only.py"""

from __future__ import annotations

import secrets

from fastapi.testclient import TestClient

from server import db, deps


def check(c: TestClient) -> None:
    was = deps.EMAIL_ONLY
    deps.EMAIL_ONLY = True
    try:
        fresh = lambda: "a:eo" + secrets.token_hex(8)
        listed, name = f"eo.{secrets.token_hex(4)}@example.com", "Каримов Камолхон"
        db.run("INSERT INTO email_allow(email,name,grp,added) VALUES (?,?,?,?)", listed, name, "test", deps.now())
        old = "a:eoold" + secrets.token_hex(6)
        db.ensure_learner(old)

        f = fresh()
        assert c.get("/api/shell", headers={"X-Learner": f}).json() == {"signin": True}
        r = c.get("/api/me", headers={"X-Learner": f})
        assert r.status_code == 401 and r.json()["detail"] == {"signin": True}, r.text
        assert c.get("/api/me", headers={"X-Learner": old}).status_code == 200, "a learner from before keeps its access"

        r = c.post("/api/account/beta", headers={"X-Learner": fresh()}, json={"email": "nobody@example.com"})
        assert r.status_code == 403 and r.json()["detail"] == {"reason": "not_registered"}, r.text

        r = c.post("/api/account/beta", headers={"X-Learner": f}, json={"email": listed.upper()})
        assert r.json() == {"needs_name": True, "name": name}, r.text
        assert c.get("/api/shell", headers={"X-Learner": f}).json() == {"signin": True}, "asking makes no learner"
        r = c.post("/api/account/beta", headers={"X-Learner": f}, json={"email": listed, "name": "Kamol 1"})
        assert r.status_code == 422, r.text
        r = c.post("/api/account/beta", headers={"X-Learner": f}, json={"email": listed, "name": "  Kamolkhon   Karimov "})
        cred = r.json()["credential"]
        assert cred.startswith("d:") and c.get("/api/me", headers={"X-Learner": cred}).json()["profile"]["name"] == "Kamolkhon Karimov"

        r = c.post("/api/account/beta", headers={"X-Learner": fresh()}, json={"email": listed})
        other = r.json()["credential"]
        assert c.get("/api/me", headers={"X-Learner": other}).json()["profile"]["name"] == "Kamolkhon Karimov", "same learner, no name step"

        mine = f"eo.keep.{secrets.token_hex(4)}@example.com"
        r = c.post("/api/account/beta", headers={"X-Learner": old}, json={"email": mine})
        assert r.status_code == 200 and "credential" in r.json(), "a learner from before links any free address"
        r = c.post("/api/account/beta", headers={"X-Learner": fresh()}, json={"email": mine})
        assert db.one("SELECT learner FROM devices WHERE token=?", r.json()["credential"])["learner"] == old
        print("ok  email-only: new browsers sign in, unlisted refused, listed asks a name once, old learners kept")
    finally:
        deps.EMAIL_ONLY = was


if __name__ == "__main__":
    from server.app import app
    db.init()
    with TestClient(app) as client:
        check(client)
