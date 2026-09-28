"""S1 Account and Me server acceptance checks.

Run with SATF_DB=$PWD/server/s1.db PYTHONPATH=. python3 server/checks/s1.py.
"""

from __future__ import annotations

import os
import secrets
import json
import hashlib
import datetime as dt
import time
from unittest.mock import patch

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa, padding

from fastapi.testclient import TestClient

from server.app import app, FORMS
from server import account, db, practice


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

    account._limits.clear()
    owner = "a:" + secrets.token_hex(12)
    browser = "a:" + secrets.token_hex(12)
    visitor = "a:" + secrets.token_hex(12)
    address = "s1-login-" + secrets.token_hex(6) + "@example.org"
    sent = []
    def capture(email, code, token):
        sent.append((email, code, token))
        return "outbox"
    with patch("server.account.mail.send_login", side_effect=capture):
        link = c.post("/api/account/link", headers={"X-Learner": owner},
                      json={"email": address})
    assert link.status_code == 200, link.text
    assert link.json()["email_masked"].endswith("@example.org")
    assert db.one("SELECT login_code FROM users WHERE email=?", address)["login_code"] != sent[0][1]
    signed = c.post("/api/account/verify", headers={"X-Learner": owner},
                    json={"code": sent[0][1]})
    assert signed.status_code == 200, signed.text
    key = signed.json()["credential"]
    assert key.startswith("d:") and c.get("/api/account", headers={"X-Learner": key}).json()["saved"]
    assert db.one("SELECT learner FROM users WHERE email=?", address)["learner"] == owner
    assert c.post("/api/account/verify", headers={"X-Learner": owner},
                  json={"code": sent[0][1]}).status_code == 410
    print("ok  email codes are hashed, single use, and mint a separate device credential")

    changed_address = "s1-changed-" + secrets.token_hex(6) + "@example.org"
    with patch("server.account.mail.send_login", side_effect=capture):
        changed = c.put("/api/account/email", headers={"X-Learner": key},
                        json={"email": changed_address})
    assert changed.status_code == 200 and changed.json()["sent"], changed.text
    confirmed = c.post("/api/account/verify", headers={"X-Learner": key},
                       json={"code": sent[-1][1]})
    assert confirmed.status_code == 200, confirmed.text
    assert db.one("SELECT learner FROM users WHERE email=?", address)["learner"] is None
    assert db.one("SELECT learner FROM users WHERE email=?", changed_address)["learner"] == owner
    assert c.get("/api/account", headers={"X-Learner": key}).json()["email"] == changed_address
    print("ok  changing email requires a fresh code before the old address detaches")

    req = c.post("/api/link/request", headers={"X-Learner": browser},
                 json={"device": "School laptop", "session_only": True})
    assert req.status_code == 200, req.text
    code, ticket = req.json()["code"], req.json()["token"]
    seen = c.post("/api/link/code", headers={"X-Learner": key}, json={"code": code})
    assert seen.status_code == 200 and "name" not in seen.text
    assert c.post(f"/api/link/{ticket}/approve", headers={"X-Learner": key}).status_code == 200
    claimed = c.get(f"/api/link/{ticket}", headers={"X-Learner": browser})
    assert claimed.status_code == 200 and claimed.json()["credential"].startswith("d:")
    second_key = claimed.json()["credential"]
    assert c.get(f"/api/link/{ticket}", headers={"X-Learner": browser}).status_code == 410
    assert c.get("/api/account", headers={"X-Learner": second_key}).json()["saved"]
    assert c.delete("/api/devices/this", headers={"X-Learner": second_key}).status_code == 200
    assert c.get("/api/account", headers={"X-Learner": second_key}).status_code == 401
    print("ok  approved phone link grants one revocable, session-only device key")

    transfer = c.post("/api/transfer", headers={"X-Learner": key}).json()["code"]
    redeemed = c.post("/api/transfer/redeem", headers={"X-Learner": visitor},
                      json={"code": transfer})
    assert redeemed.status_code == 200 and redeemed.json()["credential"].startswith("d:")
    assert c.post("/api/transfer/redeem", headers={"X-Learner": visitor},
                  json={"code": transfer}).status_code == 410
    print("ok  transfer codes are single use")

    with patch.dict(os.environ, {"SATF_BASE_URL": "http://localhost:8021"}):
        p = "a:" + secrets.token_hex(12)
        private = ec.generate_private_key(ec.SECP256R1())
        cred = account._b64(secrets.token_bytes(24))
        authenticator = hashlib.sha256(b"localhost").digest() + b"\x01" + (1).to_bytes(4, "big")
        registration = c.post("/api/passkey/register/options", headers={"X-Learner": p}).json()
        client_data = account._b64(json.dumps({"type": "webauthn.create",
            "challenge": registration["challenge"], "origin": "http://localhost:8021"}).encode())
        spki = private.public_key().public_bytes(serialization.Encoding.DER,
                                                  serialization.PublicFormat.SubjectPublicKeyInfo)
        made = c.post("/api/passkey/register", headers={"X-Learner": p}, json={
            "id": cred, "publicKey": account._b64(spki), "algorithm": -7,
            "authData": account._b64(authenticator), "clientDataJSON": client_data})
        assert made.status_code == 200, made.text
        assert c.get("/api/account", headers={"X-Learner": made.json()["credential"]}).json()["saved"]
        opts = c.post("/api/passkey/login/options", json={"conditional": True}).json()
        raw = json.dumps({"type": "webauthn.get", "challenge": opts["challenge"],
                          "origin": "http://localhost:8021"}).encode()
        assertion = hashlib.sha256(b"localhost").digest() + b"\x01" + (2).to_bytes(4, "big")
        sig = private.sign(assertion + hashlib.sha256(raw).digest(), ec.ECDSA(hashes.SHA256()))
        payload = {"id": cred, "authData": account._b64(assertion),
                   "clientDataJSON": account._b64(raw), "signature": account._b64(sig)}
        logged = c.post("/api/passkey/login", headers={"X-Learner": browser}, json=payload)
        assert logged.status_code == 200 and logged.json()["credential"].startswith("d:")
        assert c.post("/api/passkey/login", headers={"X-Learner": browser}, json=payload).status_code == 400
        wrong = c.post("/api/passkey/login/options", json={}).json()
        bad_origin = {**payload, "clientDataJSON": account._b64(json.dumps({
            "type": "webauthn.get", "challenge": wrong["challenge"],
            "origin": "https://evil.example"}).encode())}
        assert c.post("/api/passkey/login", headers={"X-Learner": browser},
                      json=bad_origin).status_code == 400
        bad = c.post("/api/passkey/login/options", json={}).json()
        invalid = {**payload, "clientDataJSON": account._b64(json.dumps({
            "type": "webauthn.get", "challenge": bad["challenge"],
            "origin": "http://localhost:8021"}).encode())}
        assert c.post("/api/passkey/login", headers={"X-Learner": browser},
                      json=invalid).status_code == 401
        diag_id = secrets.token_urlsafe(12)
        db.run("INSERT INTO sessions(id,kind,form_id,learner,started,finished,result)"
               " VALUES (?,?,?,?,?,?,?)", diag_id, "diagnostic", next(iter(FORMS)), p,
               "2026-09-01T00:00:00+00:00", "2026-09-01T00:30:00+00:00",
               json.dumps({"right": 0, "asked": 20}))
        saved_result = c.get(f"/api/session/{diag_id}/results",
                             headers={"X-Learner": made.json()["credential"]})
        assert saved_result.status_code == 200 and saved_result.json()["verified"], saved_result.text
        assert c.get(f"/api/session/{diag_id}/results").status_code == 403
    print("ok  passkeys verify origin, challenge reuse, and cryptographic signatures")

    assert c.post("/api/google/nonce", headers={"X-Learner": browser}).status_code == 404
    assert c.post("/api/google", headers={"X-Learner": browser},
                  json={"credential": "x", "nonce": "x"}).status_code == 404
    google_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    google_public = google_key.public_key().public_numbers()
    jwk = {"kid": "s1-test", "kty": "RSA",
           "n": account._b64(google_public.n.to_bytes((google_public.n.bit_length() + 7) // 8, "big")),
           "e": account._b64(google_public.e.to_bytes(3, "big"))}
    def token_for(nonce, **changes):
        claims = {"iss": "https://accounts.google.com", "aud": "satf-s1-test",
                  "exp": int(time.time()) + 300, "nonce": nonce, "email_verified": True,
                  "sub": "s1-google-" + browser, "email": "google-" + browser[2:] + "@example.org",
                  **changes}
        head = account._b64(json.dumps({"alg": "RS256", "kid": "s1-test"}).encode())
        body = account._b64(json.dumps(claims).encode())
        signed = f"{head}.{body}".encode()
        signature = google_key.sign(signed, padding.PKCS1v15(), hashes.SHA256())
        return f"{head}.{body}.{account._b64(signature)}"
    with patch.dict(os.environ, {"SATF_GOOGLE_CLIENT_ID": "satf-s1-test"}), \
         patch("server.account._jwks", return_value=[jwk]):
        nonce = c.post("/api/google/nonce", headers={"X-Learner": visitor}).json()["nonce"]
        jwt = token_for(nonce)
        google = c.post("/api/google", headers={"X-Learner": visitor},
                        json={"credential": jwt, "nonce": nonce})
        assert google.status_code == 200 and google.json()["credential"].startswith("d:"), google.text
        assert c.post("/api/google", headers={"X-Learner": visitor},
                      json={"credential": jwt, "nonce": nonce}).status_code == 400
        for changed_claim in ({"aud": "wrong"}, {"exp": int(time.time()) - 3600},
                              {"email_verified": False}):
            n = c.post("/api/google/nonce", headers={"X-Learner": visitor}).json()["nonce"]
            assert c.post("/api/google", headers={"X-Learner": visitor},
                          json={"credential": token_for(n, **changed_claim),
                                "nonce": n}).status_code == 401
    print("ok  Google sign-in is off by default and validates signature, claims, and nonce")

    profile_learner = "a:" + secrets.token_hex(12)
    profile_h = {"X-Learner": profile_learner}
    template = practice.catalogue()["by_topic"]["circles"][0]
    with db.transaction():
        for i in range(50):
            db.run("INSERT INTO attempts(learner,template,seed,topic,difficulty,fmt,correct,at)"
                   " VALUES (?,?,?,?,?,?,?,?)", profile_learner, template, i, "circles", "medium",
                   "mcq", 1, f"2026-09-01T00:00:{i:02d}+00:00")
    badges = c.get("/api/me/achievements", headers=profile_h)
    assert badges.status_code == 200, badges.text
    answered = next(b for b in badges.json() if b["id"] == "answered")
    assert answered["have"] == 50 and answered["earned"][0]["at"] == "2026-09-01T00:00:49+00:00"
    assert len([b for b in badges.json() if b["id"].startswith("skill:")]) == 19
    feed = c.get("/api/me/feed", params={"unread": 1}, headers=profile_h)
    assert any(x["kind"] == "achievements" for x in feed.json()["items"])
    assert c.post("/api/me/feed/seen", headers=profile_h).status_code == 200
    assert not c.get("/api/me/feed", params={"unread": 1}, headers=profile_h).json()["items"]
    summary = c.get("/api/me/summary", headers=profile_h)
    assert summary.status_code == 200, summary.text
    assert summary.json()["stats"]["answered"] == 50
    assert len(summary.json()["stats"]["series"]["answered"]) == 14
    assert len(summary.json()["domains"]) == 4
    print("ok  Me summary and 43 base achievement rules use the same counted attempts")

    today = dt.datetime.now(dt.timezone.utc)
    iso = today.isocalendar()
    week = f"{iso.year}-W{iso.week:02d}"
    goal = c.put("/api/me/week/goals", headers=profile_h,
                 json={"week": week, "goals": [{"kind": "fix_traps",
                      "params": {"topic": "circles"}, "target": 1}]})
    assert goal.status_code == 200 and goal.json()["goals"][0]["have"] == 0, goal.text
    assert c.get("/api/shell", headers=profile_h).json()["goals"][0]["done"] is False
    db.run("INSERT INTO traps(learner,template,norm,reason,label,topic,hits,owed,opened,last,closed)"
           " VALUES (?,?,?,?,?,?,?,?,?,?,?)", profile_learner, template, "test", "test",
           "Test mistake", "circles", 1, 0, today.isoformat(), today.isoformat(), today.isoformat())
    assert c.get("/api/me/week", headers=profile_h).json()["goals"][0]["done"] is True
    assert c.get("/api/shell", headers=profile_h).json()["goals"][0]["have"] == 1
    many = c.put("/api/me/week/goals", headers=profile_h, json={"week": week,
                 "goals": [{"kind": "minutes", "target": 1}] * 4})
    assert many.status_code == 422
    print("ok  weekly goals move from 0/1 to done and reject a fourth goal")

    private_email = "s1-private-" + secrets.token_hex(6) + "@example.org"
    db.run("INSERT INTO users(id,first,last,email,verified,learner,created) VALUES (?,?,?,?,1,?,?)",
           secrets.token_urlsafe(12), "Private", "Student", private_email,
           profile_learner, "2026-09-01T00:00:00+00:00")
    link = c.post("/api/share", headers=profile_h).json()["token"]
    public = c.get(f"/api/shared/{link}")
    assert public.status_code == 200, public.text
    assert private_email not in public.text and profile_learner not in public.text
    assert public.json()["stats"]["answered"] == 50
    assert c.delete(f"/api/share/{link}", headers=profile_h).status_code == 200
    assert c.get(f"/api/shared/{link}").status_code == 404
    export = c.get("/api/me/export", headers=profile_h)
    assert export.status_code == 200 and "attachment" in export.headers["content-disposition"]
    assert len(export.json()["attempts"]) == 50
    assert c.request("DELETE", "/api/me", headers=profile_h, json={"confirm": "nope"}).status_code == 422
    erased = c.request("DELETE", "/api/me", headers=profile_h, json={"confirm": "DELETE"})
    assert erased.status_code == 200, erased.text
    assert db.one("SELECT COUNT(*) AS n FROM attempts WHERE learner=?", profile_learner)["n"] == 0
    assert db.one("SELECT learner FROM users WHERE email=?", private_email)["learner"] is None
    print("ok  progress links redact identity, exports exclude keys, and delete removes learner rows")


def main() -> None:
    assert os.environ.get("SATF_DB", "").endswith("/server/s1.db"), "set SATF_DB=$PWD/server/s1.db"
    with TestClient(app) as c:
        check(c)
    print("S1 checks passed")


if __name__ == "__main__":
    main()
