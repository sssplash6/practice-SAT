"""Task 9 security regressions. Run: PYTHONPATH=. python3 server/checks/security.py."""

from __future__ import annotations

import concurrent.futures
import datetime as dt
import os
import tempfile

if __name__ == "__main__":
    os.environ["SATF_DB"] = tempfile.mktemp(prefix="satf-sec-check-", suffix=".db")
    os.environ["SATF_REPORTS"] = tempfile.mkdtemp(prefix="satf-sec-files-")

from fastapi.testclient import TestClient

from server import api_bank, db, progress, reports
from server.app import app


def quota_and_sample(c: TestClient) -> None:
    h = {"X-Learner": "a:secquota01"}
    body = {"template": "lin.evaluate"}
    for _ in range(29):
        r = c.post("/api/mistakes/log", headers=h, json=body)
        assert r.status_code == 200, r.text
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        statuses = list(pool.map(lambda _: c.post("/api/mistakes/log", headers=h, json=body).status_code,
                                 range(10)))
    assert statuses.count(200) == 1 and statuses.count(429) == 9, statuses
    day = dt.datetime.now(dt.timezone.utc).date().isoformat()
    assert db.one("SELECT COUNT(*) n FROM trap_log WHERE learner=? AND at>=? AND event='outside_log'",
                  h["X-Learner"], day)["n"] == 30
    assert db.one("SELECT COUNT(*) n FROM trap_log WHERE learner=?", h["X-Learner"])["n"] > 30
    print("ok SEC-04 each outside request counts once, atomically, even in a burst")

    sample = "sample:audit"
    r = c.post("/api/mistakes/log", headers={"X-Learner": sample}, json=body)
    assert r.status_code == 403, r.text
    try:
        progress.record_trap(sample, {"key": "lin.evaluate", "topic": "linear_equations_in_one_variable",
                                      "seed": 1}, "wrong", progress.now())
    except ValueError:
        pass
    else:
        raise AssertionError("internal record_trap accepted a sample learner")
    assert db.one("SELECT COUNT(*) n FROM traps WHERE learner=?", sample)["n"] == 0
    print("ok SEC-09 sample learners cannot log mistakes through route or core")


def unknown_id(c: TestClient) -> None:
    before = db.one("SELECT COUNT(*) n FROM cb_unknown")["n"]
    for value in ("unknown-audit-id-" + "x" * 1000, "nothex00", "1234567", "123456789"):
        r = c.get("/api/types/match", params={"id": value})
        assert r.status_code == 422, (value, r.text)
    assert db.one("SELECT COUNT(*) n FROM cb_unknown")["n"] == before
    assert c.get("/api/types/match?id=23c5fcce").json()["rows"][0]["via"] == "id"
    r = c.get("/api/types/match?id=ffff0000")
    assert r.status_code == 200 and r.json()["rows"][0]["via"] == "none"
    assert db.one("SELECT n FROM cb_unknown WHERE cb_id='ffff0000'")["n"] == 1
    old_max, old_hour = api_bank.UNKNOWN_IDS_MAX, api_bank.UNKNOWN_PER_HOUR
    api_bank.UNKNOWN_IDS_MAX, api_bank.UNKNOWN_PER_HOUR = 2, 3
    try:
        c.get("/api/types/match?id=ffff0000")
        c.get("/api/types/match?id=ffff0001")
        c.get("/api/types/match?id=ffff0002")
        assert db.one("SELECT COUNT(*) n FROM cb_unknown")["n"] == 2
        assert db.one("SELECT n FROM cb_unknown WHERE cb_id='ffff0000'")["n"] == 2
        c.get("/api/types/match?id=ffff0000")
        assert db.one("SELECT n FROM cb_unknown WHERE cb_id='ffff0000'")["n"] == 2
    finally:
        api_bank.UNKNOWN_IDS_MAX, api_bank.UNKNOWN_PER_HOUR = old_max, old_hour
    print("ok SEC-06 invalid IDs are rejected and telemetry has row and rate caps")


def legacy(c: TestClient) -> None:
    retired = "a:sec-retired"
    db.run("INSERT INTO retired(code,\"into\",at) VALUES (?,?,?)", retired, "a:replacement", progress.now())
    for path, body in (("/api/practice", {"basket": {"probability": 1}}),
                       ("/api/mock/1.1", {})):
        for bad, expected in ((retired, 401), ("sample:audit", 403), ("bad token!", 400)):
            r = c.post(path, json={**body, "learner": bad})
            assert r.status_code == expected, (path, bad, r.text)
        r = c.post(path, json={**body, "learner": "a:valid-user"},
                   headers={"X-Learner": retired})
        assert r.status_code == 401, (path, r.text)
    assert db.one("SELECT COUNT(*) n FROM sessions WHERE learner=?", retired)["n"] == 0
    assert db.one("SELECT COUNT(*) n FROM sessions WHERE learner='sample:audit'")["n"] == 0
    print("ok SEC-07 legacy creation validates body and header learners before writes")


def upload(c: TestClient) -> None:
    old_total, old_mb = reports.MAX_TOTAL, reports.MB
    reports.MAX_TOTAL, reports.MB = 64, 1
    try:
        body = (b'--audit-boundary\r\nContent-Disposition: form-data; name="data"\r\n\r\n'
                b'{"kind":"page","category":"idea"}\r\n'
                b'--audit-boundary\r\nContent-Disposition: form-data; name="files"; filename="x.png"\r\n'
                b'Content-Type: image/png\r\n\r\n\x89PNG\r\n\x1a\n'
                + b'x' * 100 + b'\r\n--audit-boundary--\r\n')
        h = {"X-Learner": "a:secupload", "Content-Type": "multipart/form-data; boundary=audit-boundary"}
        fixed = c.post("/api/report", headers=h, content=body)
        chunked = c.post("/api/report", headers=h, content=(part for part in (body[:30], body[30:])))
        for r in (fixed, chunked):
            assert r.status_code == 413 and r.json()["detail"] == {"file": None, "limit": 64}, r.text
        assert db.one("SELECT COUNT(*) n FROM reports WHERE learner='a:secupload'")["n"] == 0
    finally:
        reports.MAX_TOTAL, reports.MB = old_total, old_mb
    print("ok SEC-05 fixed-length and chunked uploads stop before multipart parsing")


def check(client: TestClient) -> None:
    quota_and_sample(client)
    unknown_id(client)
    legacy(client)
    upload(client)
    print("security fixes good")


if __name__ == "__main__":
    with TestClient(app) as client:
        check(client)
