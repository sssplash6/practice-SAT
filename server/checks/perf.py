"""Traffic prerequisites: precomputed contests, fresh Words cache, WAL writers.

Run with PYTHONPATH=. python3 server/checks/perf.py. Uses only a temp database.
"""

from __future__ import annotations

import os
import pathlib
import sqlite3
import tempfile
import threading
import time
from contextlib import nullcontext
from concurrent.futures import ThreadPoolExecutor

from fastapi.testclient import TestClient

if __name__ == "__main__":
    _tmp = tempfile.TemporaryDirectory(prefix="satf-perf-check-")
    os.environ["SATF_DB"] = str(pathlib.Path(_tmp.name) / "perf.db")

from server import compete, db, drill, words  # noqa: E402
from server.app import app  # noqa: E402


def check(client=None) -> None:
    standalone = client is None
    with TestClient(app) if client is None else nullcontext(client) as client:
        assert client.get("/api/health").status_code == 200
        today = compete.local_day().isoformat()
        assert db.one("SELECT 1 FROM contests WHERE id=?", "daily-" + today)
        assert db.one("SELECT 1 FROM challenges WHERE day=?", today)
        assert db.conn().execute("PRAGMA journal_mode").fetchone()[0] == "wal"
        assert db.conn().execute("PRAGMA busy_timeout").fetchone()[0] == 10000      # workers wait on each other's commits
        assert db.conn().execute("PRAGMA synchronous").fetchone()[0] == 1           # NORMAL, WAL's usual setting
        print("ok  current contest and challenge precomputed; WAL and busy timeout enabled")
        # test_flow invokes all checks against its shared database. The full
        # concurrency and cache exercise belongs to this check's isolated run.
        if not standalone:
            return

        family = compete.trap_families()
        assert compete.trap_families() is family  # including the empty-supply result
        assert compete.ensure(tz=0)
        print("ok  contest and trap-family requests reuse precomputed work")

        twins, next_question = compete.twin_questions, drill.next_question
        try:
            def outside_writer(*args, **kwargs):
                assert not getattr(db._local, "atomic", False), "twins generated while holding a write lock"
                return twins(*args, **kwargs)

            def first_outside_writer(*args, **kwargs):
                assert not getattr(db._local, "atomic", False), "first item generated while holding a write lock"
                return next_question(*args, **kwargs)

            compete.twin_questions = outside_writer
            drill.next_question = first_outside_writer
            start = client.post("/api/contest/daily/start", headers={"X-Learner": "a:perf-contest", "X-Tz": "0"})
            assert start.status_code == 200, start.text[:300]
            assert start.json()["question"]
        finally:
            compete.twin_questions, drill.next_question = twins, next_question
        print("ok  daily twin and first-item generation run outside writer transaction")

        who = "a:perf-cache"
        first = words.library(who)
        assert words.library(who) is first
        db.run("INSERT INTO word_state(learner,word,box) VALUES (?,?,?)", who, "mitigate", 2)
        second = words.library(who)
        assert second is not first
        assert next(w for w in second["words"] if w["slug"] == "mitigate")["state"]["box"] == 2

        with ThreadPoolExecutor(max_workers=1) as pool:
            pool.submit(db.run, "UPDATE word_state SET box=3 WHERE learner=? AND word=?",
                        who, "mitigate").result()
        third = words.library(who)
        assert third is not second
        assert next(w for w in third["words"] if w["slug"] == "mitigate")["state"]["box"] == 3
        print("ok  Words cache invalidates on same-thread and other-thread writes")

        db.run("CREATE TABLE perf_writes(n INTEGER PRIMARY KEY)")
        with ThreadPoolExecutor(max_workers=40) as pool:
            list(pool.map(lambda n: db.run("INSERT INTO perf_writes(n) VALUES (?)", n), range(400)))
        assert db.one("SELECT COUNT(*) n FROM perf_writes")["n"] == 400
        print("ok  400 concurrent writes complete without database lock errors")

        release = threading.Event()
        external = sqlite3.connect(db.DB_PATH, timeout=1, check_same_thread=False)
        external.execute("BEGIN IMMEDIATE")
        try:
            def write_after_lock() -> None:
                release.set()
                db.run("INSERT INTO perf_writes(n) VALUES (?)", 401)

            with ThreadPoolExecutor(max_workers=1) as pool:
                result = pool.submit(write_after_lock)
                assert release.wait(1)
                time.sleep(.15)
                external.commit()
                result.result(timeout=5)
        finally:
            external.close()
        assert db.one("SELECT COUNT(*) n FROM perf_writes")["n"] == 401
        print("ok  a brief external SQLite writer is waited out")
    print("perf checks passed")


if __name__ == "__main__":
    check()
