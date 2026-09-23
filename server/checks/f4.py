"""F4 data-layer acceptance. Run with PYTHONPATH=. python3 server/checks/f4.py."""

from __future__ import annotations

import datetime as dt
import json
import pathlib
import sqlite3
import tempfile
from unittest.mock import patch

from fastapi.testclient import TestClient

from server import db, deps, estimate, progress, satdates, scoring
from server.app import app


def add(table: str, **values):
    cols = ",".join(values)
    return db.run(f"INSERT INTO {table} ({cols}) VALUES ({','.join('?' for _ in values)})",*values.values())


def q(seed: int) -> dict:
    return {"id":f"q{seed}","key":"lin.evaluate","seed":seed,"topic":"linear_functions",
            "difficulty":"easy","type":"mcq","answer":"A",
            "reasons":["","used 10 instead of 20","used 30 instead of 40","near-miss arithmetic slip"],
            "stem":f"Find x in question {seed}"}


def checks():
    for table in ("classes","members","assignments","attachments"):
        assert not db.one("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",table)
    assert "assignment" not in {r["name"] for r in db.rows("PRAGMA table_info(sessions)")}
    try:
        with db.transaction():
            db.run("INSERT INTO learners(id,created) VALUES (?,?)","a:f4rollback",progress.now())
            raise RuntimeError("simulate a failed multi-field write")
    except RuntimeError:
        pass
    assert not db.one("SELECT 1 FROM learners WHERE id=?","a:f4rollback")
    assert progress.norm("Used 10 instead of 20") == progress.norm("Used 30 instead of 40")
    p = "a:f4progress"
    start = "2026-01-01T12:00:00+00:00"
    progress.record(p,None,q(1),1,when=start)
    progress.record(p,None,q(2),2,when="2026-01-02T12:00:00+00:00")
    traps = db.rows("SELECT * FROM traps WHERE learner=?",p)
    assert len(traps)==1 and isinstance(traps[0]["id"],int) and traps[0]["hits"]==2
    assert traps[0]["reason"] == "used 30 instead of 40"
    before = progress.topic_mastery(p,"linear_functions")
    progress.record(p,None,q(2),0,when="2026-01-03T12:00:00+00:00")
    assert progress.topic_mastery(p,"linear_functions") == before
    assert db.one("SELECT repeat FROM attempts WHERE learner=? ORDER BY id DESC LIMIT 1",p)["repeat"]==1
    for seed,day in ((3,"2026-01-03"),(4,"2026-01-04")):
        progress.record(p,None,q(seed),0,when=day+"T12:00:00+00:00")
    t=db.one("SELECT * FROM traps WHERE learner=?",p)
    assert t["closed_how"]=="fixed" and t["due"]=="2026-01-07" and t["checks"]==0
    progress.record(p,None,q(40),0,when="2026-01-05T12:00:00+00:00")
    early=db.one("SELECT due,checks FROM traps WHERE learner=?",p)
    assert (early["due"],early["checks"])==("2026-01-07",0)
    for seed,day,due,stage in ((5,"2026-01-07","2026-01-14",1),
                                (6,"2026-01-14","2026-02-03",2),
                                (7,"2026-02-03",None,3)):
        progress.record(p,None,q(seed),0,when=day+"T12:00:00+00:00")
        t=db.one("SELECT * FROM traps WHERE learner=?",p)
        assert (t["due"],t["checks"])==(due,stage)
    progress.record(p,None,q(8),1,when="2026-02-17T12:00:00+00:00")
    assert db.one("SELECT relapses,closed FROM traps WHERE learner=?",p)["relapses"]==1
    progress.record(p,None,q(9),0,flagged=True)
    unsure=db.one("SELECT * FROM traps WHERE learner=? AND norm='~unsure'",p)
    assert unsure and unsure["owed"]==1
    assert scoring.accepted_forms("2/3")==[".6666",".6667"]

    legacy=sqlite3.connect(":memory:")
    legacy.row_factory=sqlite3.Row
    legacy.executescript("""
      CREATE TABLE traps(learner TEXT,template TEXT,reason TEXT,label TEXT,topic TEXT,
        hits INTEGER,owed INTEGER,opened TEXT,last TEXT,closed TEXT,
        PRIMARY KEY(learner,template,reason));
      CREATE TABLE attempts(id INTEGER PRIMARY KEY,learner TEXT,template TEXT,reason TEXT,
        correct INTEGER,seed INTEGER,session TEXT,at TEXT);
      INSERT INTO traps VALUES('old','lin.evaluate','used 10 instead of 20','First',
        'linear_functions',2,2,'2026-01-01','2026-01-02',NULL);
      INSERT INTO traps VALUES('old','lin.evaluate','used 30 instead of 40','Second',
        'linear_functions',3,1,'2026-01-02','2026-01-03','2026-01-04');
      INSERT INTO attempts VALUES(1,'old','lin.evaluate','used 30 instead of 40',0,77,'legacy','2026-01-03');
    """)
    db._rebuild_traps(legacy)
    merged=legacy.execute("SELECT * FROM traps").fetchall()
    assert len(merged)==1 and merged[0]["hits"]==5 and merged[0]["closed"] is None
    assert merged[0]["seed"]==77 and merged[0]["reason"]=="used 30 instead of 40"
    legacy.close()
    legacy=sqlite3.connect(":memory:")
    legacy.row_factory=sqlite3.Row
    legacy.executescript("""
      CREATE TABLE sessions(id TEXT PRIMARY KEY,kind TEXT,form_id INTEGER NOT NULL,
        started TEXT NOT NULL,finished TEXT,answers TEXT,result TEXT,user_id TEXT,
        qstate TEXT,mock_id TEXT);
      INSERT INTO sessions(id,kind,form_id,started,qstate,mock_id)
        VALUES('old-session','mock',2,'2026-01-01','{"q1":{"ms":3000}}','1.3');
    """)
    db._relax_form_id(legacy)
    kept=legacy.execute("SELECT qstate,mock_id FROM sessions WHERE id='old-session'").fetchone()
    assert kept["mock_id"]=="1.3" and json.loads(kept["qstate"])["q1"]["ms"]==3000
    assert not next(c for c in legacy.execute("PRAGMA table_info(sessions)") if c["name"]=="form_id")["notnull"]
    legacy.close()

    # Six study weekdays across a weekend; planned rest days preserve the run.
    learner="a:f4streak"
    db.ensure_learner(learner)
    db.run("UPDATE learners SET plan='p1',days='1111100' WHERE id=?",learner)
    active=[]
    d=dt.datetime.now(dt.timezone.utc).date()
    while len(active)<6:
        if d.weekday()<5:
            active.append(d)
        d-=dt.timedelta(days=1)
    for i,day in enumerate(active):
        add("attempts",learner=learner,template="lin.evaluate",seed=100+i,topic="linear_functions",
            difficulty="easy",fmt="mcq",correct=1,at=day.isoformat()+"T12:00:00+00:00")
    ledger=progress.days(learner,0,26)
    assert ledger["streak"]==6 and ledger["best_streak"]==6 and len(ledger["days"])==182

    learner="a:f4minutes"
    finish=dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    began=finish-dt.timedelta(minutes=10)
    add("sessions",id="module-time",kind="module",learner=learner,started=began.isoformat(),finished=finish.isoformat())
    add("attempts",learner=learner,session="module-time",template="lin.evaluate",seed=1,
        topic="linear_functions",difficulty="easy",fmt="mcq",correct=1,at=finish.isoformat())
    assert progress.days(learner)["minutes_total"]==10
    db.run("UPDATE attempts SET ms=180000 WHERE learner=?",learner)
    assert progress.days(learner)["minutes_total"]==3
    paper_learner="a:f4paper"
    add("sessions",id="paper-time",kind="paper",learner=paper_learner,
        started=(finish-dt.timedelta(minutes=100)).isoformat(),finished=finish.isoformat(),
        cfg=json.dumps({"timing":"x2"}))
    assert progress.days(paper_learner)["minutes_total"]==100


def routes(client):
    h={"X-Learner":"a:f4prefs"}
    fresh=client.get("/api/me",headers={"X-Learner":"a:f4fresh"}).json()
    assert fresh["prefs"]["words_from"]==["sat"]
    assert client.put("/api/me",headers=h,json={"prefs":{"bogus":True}}).status_code==422
    assert client.put("/api/me",headers=h,json={"prefs":{"theme":"nope"}}).status_code==422
    a=client.put("/api/me",headers=h,json={"prefs":{"theme":"dark","words_from":["sat","transitions"]}})
    assert a.status_code==200,a.text
    b=client.put("/api/me",headers=h,json={"prefs":{"set_length":20}})
    assert b.status_code==200 and b.json()["profile"]["prefs"]["theme"]=="dark"
    stored=json.loads(db.one("SELECT prefs FROM learners WHERE id=?","a:f4prefs")["prefs"])
    assert stored=={"theme":"dark","words_from":["sat","transitions"],"set_length":20}
    assert client.put("/api/me",headers=h,json={"name":"A"}).status_code==422
    assert client.put("/api/me",headers=h,json={"country":"XX"}).status_code==422
    assert client.put("/api/me",headers=h,json={"name":"Ada F4"}).status_code==200
    assert client.put("/api/me",headers={"X-Learner":"a:f4other"},json={"name":"ada f4"}).status_code==409
    def failed_mirror(_learner, _fields):
        raise RuntimeError("plan mirror failed")
    with patch("server.api_me.part", return_value=failed_mirror):
        try:
            client.put("/api/me",headers=h,json={"target":700,"prefs":{"theme":"light"}})
            raise AssertionError("the injected mirror failure was not reached")
        except RuntimeError:
            pass
    rolled_back=client.get("/api/me",headers=h).json()["profile"]
    assert rolled_back["target"] is None and rolled_back["prefs"]["theme"]=="dark"
    me=client.get("/api/me",headers=h).json()
    assert me["review"]["open"]==0
    activity=client.get("/api/me/activity?weeks=26",headers=h)
    assert activity.status_code==200 and len(activity.json()["days"])==182
    add("sessions",id="notes-f4",kind="drill",learner="a:f4prefs",started=progress.now(),
        questions=json.dumps([q(96)]))
    note=client.post("/api/notes",headers=h,json={"session":"notes-f4","question_id":"q96",
        "note":"Remember the sign","marks":[{"style":"underline","note":"This phrase"}]})
    assert note.status_code==200,note.text
    assert db.one("SELECT note FROM notes WHERE learner=? AND template=? AND seed=?",
                  "a:f4prefs","lin.evaluate",96)["note"]=="Remember the sign"
    assert client.post("/api/notes",headers={"X-Learner":"a:f4other"},json={"session":"notes-f4","question_id":"q96"}).status_code==403


def scores():
    today=dt.datetime.now(dt.timezone.utc).date()
    learner="a:f4estimate"
    for i,(low,high,kind) in enumerate(((500,640,"mock"),(600,700,"mock"),(400,600,"module")),start=1):
        at=(today-dt.timedelta(days=i)).isoformat()+"T12:00:00+00:00"
        add("sessions",id=f"score-f4-{i}",kind=kind,learner=learner,started=at,finished=at,
            route="upper" if kind=="mock" else None,result=json.dumps({"estimate":{"low":low,"high":high}}))
    add("outside_scores",id="outside-f4",learner=learner,day=today.isoformat(),math=650,at=progress.now())
    e=estimate.estimate(learner)
    assert e["latest"]["kind"]=="outside" and e["mean3"]==620
    assert e["combined"] and e["confidence"]["level"]=="high"
    assert estimate.percentile("score-f4-2")["why"]=="too few sittings"
    assert estimate.percentile("score-f4-1")["why"]=="repeat sitting"
    assert satdates.SAT_DATES==tuple(sorted(satdates.SAT_DATES))
    assert scoring.accepted_forms("1/8")==[]


def integrity():
    learner="a:f4access"
    live=q(91)
    add("sessions",id="live-f4",kind="module",learner=learner,started=progress.now(),
        questions=json.dumps({"module1":[live]}))
    assert deps.access(learner,live["key"],live["seed"]) is None
    today=dt.datetime.now(dt.timezone.utc).date().isoformat()
    db.run("INSERT INTO challenges(day,questions,built) VALUES (?,?,?)"
           " ON CONFLICT(day) DO UPDATE SET questions=excluded.questions",today,json.dumps([q(92)]),progress.now())
    assert deps.access(learner,"lin.evaluate",92) is None
    add("saved",learner=learner,template="lin.evaluate",seed=93,topic="linear_functions",at=progress.now())
    assert deps.access(learner,"lin.evaluate",93)=="kept"
    progress.record(learner,None,q(94),0)
    assert deps.access(learner,"lin.evaluate",94)=="reveal"
    db.run("UPDATE sessions SET finished=? WHERE id='live-f4'",progress.now())
    add("flags",learner=learner,session="live-f4",qid="q91",template="lin.evaluate",seed=91,topic="linear_functions",at=progress.now())
    assert deps.access(learner,"lin.evaluate",91)=="reveal"


def carry():
    src,dst="a:f4source","a:f4target"
    db.ensure_learner(src);db.ensure_learner(dst)
    add("users",id="carry-user",first="",last="",email="carry@example.test",created=progress.now(),learner=src)
    add("attempts",learner=src,template="lin.evaluate",seed=801,topic="linear_functions",difficulty="easy",fmt="mcq",correct=1,at=progress.now())
    add("sessions",id="carry-session",learner=src,started=progress.now())
    add("practice_seen",learner=src,template="lin.evaluate",seed=801,stem="stem",at=progress.now())
    add("traps",learner=src,template="lin.evaluate",norm="error",reason="error",label="Error",topic="linear_functions",owed=2,opened=progress.now(),last=progress.now())
    add("saved",learner=src,template="lin.evaluate",seed=801,topic="linear_functions",at=progress.now())
    add("flags",learner=src,session="carry-session",qid="q1",template="lin.evaluate",seed=801,topic="linear_functions",at=progress.now())
    add("notes",learner=src,template="lin.evaluate",seed=801,note="note",marks="[]",at=progress.now())
    add("links",token="carry-link",learner=src,kind="progress",created=progress.now())
    add("pairs",code="carry-pair",learner=src,created=progress.now())
    add("reports",learner=src,kind="question",at=progress.now())
    add("earned",learner=src,id="streak",tier=1,at=progress.now())
    add("tries",learner=src,session="carry-session",qid="q1",n=1,at=progress.now())
    add("outside_scores",id="carry-score",learner=src,day=dt.datetime.now(dt.timezone.utc).date().isoformat(),math=500,at=progress.now())
    add("plans",id="carry-plan",learner=src,created=progress.now())
    add("posts",id=991,learner=src,at=progress.now())
    add("post_votes",post=991,learner=src,kind="helpful")
    add("contest_members",contest="carry-contest",learner=src,joined=progress.now())
    add("name_reports",target=src,reporter=src,at=progress.now())
    add("word_state",learner=src,word="abate",box=2,reps=2,right=1,wrong=1)
    add("word_reviews",id=991,learner=src,word="abate",kind="review",at=progress.now())
    add("my_words",id="carry-word",learner=src,word="abate")
    assert progress.carry(src,dst)==3
    for table in db.LEARNER_TABLES:
        if table in ("learners","pairs","name_reports"):
            continue
        assert db.one(f"SELECT 1 FROM {table} WHERE learner=?",dst),table
        assert not db.one(f"SELECT 1 FROM {table} WHERE learner=?",src),table
    assert not db.one("SELECT 1 FROM pairs WHERE learner=?",src)
    assert db.one("SELECT 1 FROM name_reports WHERE target=? AND reporter=?",dst,dst)


def check(client):
    checks()
    routes(client)
    scores()
    integrity()
    carry()
    print("ok  F4 schema, traps, days, prefs, access and carry")


if __name__ == "__main__":
    with tempfile.TemporaryDirectory(prefix="satf-f4-") as path:
        db.DB_PATH=pathlib.Path(path)/"f4-check.db"
        db.init()
        with TestClient(app) as client:
            check(client)
