"""S1 Account and Me server acceptance checks.

Run with SATF_DB=$PWD/server/s1.db PYTHONPATH=. python3 server/checks/s1.py.
"""

from __future__ import annotations

import os
import secrets

from fastapi.testclient import TestClient

from server.app import app


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


def main() -> None:
    assert os.environ.get("SATF_DB", "").endswith("/server/s1.db"), "set SATF_DB=$PWD/server/s1.db"
    with TestClient(app) as c:
        check(c)
    print("S1 checks passed")


if __name__ == "__main__":
    main()
