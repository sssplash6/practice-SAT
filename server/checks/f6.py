"""F6 acceptance: reports (R17, Shell §2.10 and §10, U3, V6, X10, SR19) and question sets (R18(c), P22, U28, V17, W20, X22).
Run alone with PYTHONPATH=. python3 server/checks/f6.py, or inside test_flow; add --browser for the pages
(headless Chrome against a server on port 8016 over a throwaway database)."""

from __future__ import annotations

import json
import os
import pathlib
import tempfile
from unittest.mock import patch

from fastapi import HTTPException
from fastapi.testclient import TestClient

from server import db, deps, estimate, mail, progress, reports, sets
from server.app import app

PNG = b"\x89PNG\r\n\x1a\n" + b"\0" * 64
GIF = b"GIF89a" + b"\0" * 64
WEBM = b"\x1a\x45\xdf\xa3" + b"\0" * 64
ZIP = b"PK\x03\x04" + b"\0" * 64
MB = 1 << 20
N = [0]


def fresh(tag: str) -> str:
    N[0] += 1
    return f"a:f6{tag}{N[0]:03d}"


def post(c, learner: str, data: dict, files=(), code: int = 200) -> dict:
    r = c.post("/api/report", headers={"X-Learner": learner}, data={"data": json.dumps(data)},
               files=[("files", f) for f in files] or None)
    assert r.status_code == code, (r.status_code, r.text[:300], data)
    return r.json()


def sitting(learner: str, template: str, seed: int, given=None, kind: str = "drill",
            finished: bool = True) -> tuple[str, dict]:
    """A session holding one real question, answered (and filed) as given."""
    q = reports._from_bank(template, seed)
    sid = f"f6-{kind}-{fresh('s')}"
    db.run("INSERT INTO sessions(id,kind,questions,learner,started,finished,answers,cfg) VALUES (?,?,?,?,?,?,?,?)",
           sid, kind, json.dumps([q]), learner, deps.now(), deps.now() if finished else None,
           json.dumps({q["id"]: given} if given is not None else {}), "{}")
    if given is not None and kind == "drill":
        progress.record(learner, sid, q, given)
    return sid, q


def wrong(q: dict):
    """A wrong answer: the next option, or a number no grid-in keys."""
    return ("ABCD".index(q["answer"]) + 1) % 4 if q.get("type", "mcq") == "mcq" else "-999"


def attempt(learner: str, sid: str, q: dict):
    return db.one("SELECT * FROM attempts WHERE learner=? AND session=? AND qid=?", learner, sid, q["id"])


def seed_crowd(template: str, topic: str, norm: str, strong_on: int, others_on: int) -> None:
    """20 Strong learners' first tries and 100 others', on seeds nobody reports."""
    for i in range(120):
        who = f"a:f6s{template}{i}" if i < 20 else f"a:f6o{template}{i}"
        on = i < strong_on if i < 20 else i - 20 < others_on
        db.run("INSERT INTO attempts(learner,template,seed,topic,difficulty,fmt,correct,norm,at,repeat)"
               " VALUES (?,?,?,?,?,?,?,?,?,0)", who, template, 500 + i, topic, "medium", "mcq",
               0 if on else 1, norm if on else None, deps.now())


def strong_patch():
    real = progress.topic_mastery
    return patch.object(progress, "topic_mastery",
                        lambda learner, topic: 0.95 if learner.startswith("a:f6s") else real(learner, topic))


def basics(c) -> None:
    a = fresh("page")
    got = post(c, a, {"kind": "page", "source": "page", "category": "bug", "details": "x", "page": "/plan/"})
    row = db.one("SELECT * FROM reports WHERE id=?", got["id"])
    assert isinstance(got["id"], int) and row["kind"] == "page" and got.get("thanks")
    post(c, a, {"kind": "page", "category": "bug"}, code=422)                  # Bug needs details
    post(c, a, {"kind": "page", "category": "idea", "title": "x" * 201}, code=422)
    post(c, a, {"kind": "page", "category": "key_wrong"}, code=422)
    post(c, a, {"kind": "page", "category": "Idea", "title": "a label works"})   # labels and aliases map to ids
    cats = c.get("/api/reports/categories").json()
    assert "key_wrong" not in cats["kinds"]["question"]["live"] and cats["limits"]["files"] == 10

    # files: 11 -> 400, 11 MB PNG -> 413, zip -> 415; U3 10: a 40 MB GIF and a 20 MB webm -> 200
    # at full size on disk, a 60 MB GIF -> 413 naming 50 MB
    b = fresh("files")
    base = {"kind": "page", "category": "display", "page": "/"}
    post(c, b, base, [(f"{i}.png", PNG, "image/png") for i in range(11)], code=400)
    big = post(c, b, base, [("big.png", PNG + b"\0" * (11 * MB), "image/png")], code=413)
    assert big["detail"] == {"file": "big.png", "limit": 10 * MB}, big
    post(c, b, base, [("a.zip", ZIP, "application/zip")], code=415)
    post(c, b, base, [("fake.png", ZIP, "image/png")], code=415)            # the bytes decide, not the label
    huge = post(c, b, base, [("huge.gif", GIF + b"\0" * (60 * MB), "image/gif")], code=413)
    assert huge["detail"] == {"file": "huge.gif", "limit": 50 * MB}, huge["detail"]
    ok = post(c, b, base, [("g.gif", GIF + b"\0" * (40 * MB), "image/gif"),
                           ("r.webm", WEBM + b"\0" * (20 * MB), "video/webm")])
    files = json.loads(db.one("SELECT files FROM reports WHERE id=?", ok["id"])["files"])
    assert [f["type"] for f in files] == ["image/gif", "video/webm"]
    assert (reports.FILES / str(ok["id"]) / "1.gif").stat().st_size == len(GIF) + 40 * MB
    assert (reports.FILES / str(ok["id"]) / "2.webm").stat().st_size == len(WEBM) + 20 * MB
    assert not db.one("SELECT 1 FROM reports WHERE learner=? AND id!=?", b, ok["id"]), "refused uploads left rows"

    # 10 an hour, then 429
    r = fresh("rate")
    for i in range(10):
        post(c, r, {"kind": "page", "category": "idea", "title": f"idea {i}"})
    post(c, r, {"kind": "page", "category": "idea"}, code=429)
    print("ok  F6 reports: page feedback, categories, file types and caps on disk, 10 an hour")


def contexts(c) -> None:
    # a drill question: template and seed come from the session, not the client
    a = fresh("ctx")
    sid, q = sitting(a, "circle.convert", 40, given=wrong({"answer": reports._from_bank("circle.convert", 40)["answer"]}))
    got = post(c, a, {"kind": "question", "source": "drill", "session": sid, "question_id": q["id"],
                      "category": "explanation", "template": "lies", "seed": 1})
    ctx = json.loads(db.one("SELECT context FROM reports WHERE id=?", got["id"])["context"])
    assert (ctx["template"], ctx["seed"], ctx["marked"]) == ("circle.convert", 40, "wrong"), ctx
    assert "answer" not in json.dumps(got) and got.get("thanks")
    pv = c.get("/api/reports/context", params={"source": "drill", "session": sid, "question_id": q["id"],
                                               "category": "Answer key is wrong"}, headers={"X-Learner": a}).json()
    assert (pv["kind"], pv["box"]["marked"], pv["category"], pv["title"]) == (
        "question", "wrong", "key_wrong", f"{pv['box']['topic_name']} · Question 1"), pv
    assert pv["allowed"][0] == "key_wrong" and pv["open_disputes"] == 0
    assert (pv["similar"]["open"], pv["similar"]["mine"]) == (0, True), pv["similar"]     # the report just sent
    page = c.get("/api/reports/context", params={"page": "/plan/"}, headers={"X-Learner": a}).json()
    assert page["kind"] == "page" and page["allowed"] == list(reports.GENERAL) and page["box"] == {"page": "/plan/"}

    # the question of the day, answered
    day = c.get("/api/qotd", headers={"X-Learner": a}).json()
    from server import daily
    today = daily.today(0)
    qd = daily.question(today)
    c.post("/api/qotd", headers={"X-Learner": a}, json={"answer": 0})
    got = post(c, a, {"kind": "question", "source": "qotd", "day": today, "category": "display"})
    row = db.one("SELECT template, seed, context FROM reports WHERE id=?", got["id"])
    assert (row["template"], row["seed"]) == (qd["key"], qd["seed"]), (day, dict(row))

    # the day's challenge: live everywhere today, so no marking and no key disputes
    from server import challenge
    ch = challenge.challenge(today)
    got = post(c, a, {"kind": "question", "source": "challenge", "day": today, "question_id": ch[0]["id"],
                      "category": "figure"})
    row = db.one("SELECT template, seed, context FROM reports WHERE id=?", got["id"])
    assert (row["template"], row["seed"]) == (ch[0]["key"], ch[0]["seed"])
    assert "marked" not in json.loads(row["context"])
    post(c, a, {"kind": "question", "source": "challenge", "day": today, "question_id": ch[0]["id"],
                "category": "key_wrong"}, code=409)

    # an unfinished mock: key_wrong 409; a figure report holds its check until the end
    m = fresh("mock")
    sid, q = sitting(m, "circle.convert", 41, kind="mock", finished=False)
    db.run("UPDATE sessions SET answers=? WHERE id=?", json.dumps({q["id"]: 0}), sid)
    body = {"kind": "question", "source": "test", "session": sid, "question_id": q["id"]}
    post(c, m, {**body, "category": "key_wrong"}, code=409)
    post(c, m, {**body, "category": "key_wrong", "dispute": True}, code=409)
    # the modal's preview: the student's own answer for "Include my answer", no marking, no key, no me too
    pv = c.get("/api/reports/context", params={**body, "category": "key_wrong"}, headers={"X-Learner": m}).json()
    assert pv["box"]["given"] == "A" and pv["box"]["live"] and "marked" not in pv["box"], pv["box"]
    assert "key_wrong" not in pv["allowed"] and pv["category"] is None and pv["similar"] is None
    assert not {"answer", "correct", "rationale", "reasons"} & set(pv["box"]), pv["box"]
    held = post(c, m, {**body, "category": "figure"})
    assert "check" not in held and "marked" not in db.one("SELECT context FROM reports WHERE id=?", held["id"])["context"]
    listed = c.get("/api/reports", headers={"X-Learner": m}).json()
    assert "template" not in listed[0] and listed[0]["check"] is None, listed[0]
    db.run("UPDATE sessions SET finished=? WHERE id=?", deps.now(), sid)
    assert reports.after_finish(sid) == 1
    ctx = json.loads(db.one("SELECT context FROM reports WHERE id=?", held["id"])["context"])
    assert ctx["checked_at"] and not ctx["pending"]
    assert any(x["kind"] == "report_checked" for x in reports.feed(m))
    assert c.get("/api/reports", headers={"X-Learner": m}).json()[0]["template"] == "circle.convert"
    # someone else's session is refused; a Library example is public, an unseen seed is not
    post(c, fresh("other"), {**body, "category": "figure"}, code=403)
    ex = post(c, m, {"kind": "question", "source": "library", "template": "circle.convert", "seed": 900001,
                     "category": "key_wrong", "answer": "A"})
    assert ex["check"]["outcome"] in ("unsure", "explained"), ex
    post(c, m, {"kind": "question", "source": "review", "template": "circle.convert", "seed": 4242,
                "category": "figure"}, code=403)

    # a sitting: its kind, date and band, from the sitting itself
    db.run("UPDATE sessions SET result=? WHERE id=?", json.dumps({"estimate": {"low": 520, "high": 600}}), sid)
    pv = c.get("/api/reports/context", params={"kind": "sitting", "session": sid}, headers={"X-Learner": m}).json()
    st = pv["box"]["sitting"]
    assert (st["kind"], st["band"], st["finished"], pv["allowed"]) == ("mock", "520–600", True, list(reports.GENERAL)), pv
    got = post(c, m, {"kind": "sitting", "source": "report", "session": sid, "category": "confusing"})
    assert db.one("SELECT kind, session FROM reports WHERE id=?", got["id"])["session"] == sid
    post(c, fresh("other"), {"kind": "sitting", "session": sid, "category": "confusing"}, code=403)

    # a word (W18): "Another choice also fits" is a one-tap two_right; a key dispute isn't a word's
    w = fresh("word")
    got = post(c, w, {"kind": "word", "source": "words", "word": "mitigate", "category": "Another choice also fits"})
    row = db.one("SELECT kind, category, word FROM reports WHERE id=?", got["id"])
    assert tuple(row) == ("word", "two_right", "mitigate") and got.get("thanks"), dict(row)
    post(c, w, {"kind": "word", "word": "mitigate", "category": "key_wrong"}, code=422)
    post(c, w, {"kind": "word", "category": "definition"}, code=422)                  # say which word
    print("ok  F6 reports: context resolved on the server for drill, qotd, challenge, a live mock, a sitting, a word")


def disputes(c) -> None:
    os.environ.pop("SATF_ADMIN_TOKEN", None)
    assert c.get("/api/admin/reports").status_code == 404
    d = fresh("disp")
    rids, first = [], None
    items = [("circle.equal_area_square", 60)] + [("circle.convert", s) for s in (60, 61, 62, 65, 66)]
    for i, (template, seed) in enumerate(items):
        sid, q = sitting(d, template, seed)
        progress.record(d, sid, q, wrong(q))
        a = attempt(d, sid, q)
        body = {"kind": "question", "source": "drill", "session": sid, "question_id": q["id"],
                "category": "key_wrong", "dispute": True}
        if i == 5:
            got = post(c, d, body, code=409)
            assert "5 answers waiting" in got["detail"], got
            post(c, d, {**body, "dispute": False})          # the report itself still goes to a person
            break
        if i == 0:
            topic = lambda: next(t for t in c.get("/api/map", headers={"X-Learner": d}).json()["topics"]  # noqa: E731
                                 if t["topic"] == q["topic"])
            act = lambda: c.get("/api/me/activity", headers={"X-Learner": d}).json()                    # noqa: E731
            blank = next(t for t in c.get("/api/map", headers={"X-Learner": fresh("blank")}).json()["topics"]
                         if t["topic"] == q["topic"])
            before, minutes = topic(), act()
            assert before["answered"] == 1 and before["accuracy"] == 0, before
        got = post(c, d, body)
        if i == 0:
            # Shell 16: the topic's mastery ignores the disputed answer; the day's minutes don't move
            after = topic()
            assert (after["answered"], after["mastery"], after["accuracy"]) == (0, blank["mastery"], None), after
            assert act() == minutes
        assert got["check"]["outcome"] == "unsure" and got.get("disputed"), got      # thin: nobody strong yet
        assert db.one("SELECT disputed FROM attempts WHERE id=?", a["id"])["disputed"] == 1
        rids.append(got["id"])
        if first is None:
            first = (a, got)
            ctx = json.loads(db.one("SELECT context FROM reports WHERE id=?", got["id"])["context"])
            assert db.one("SELECT closed_how FROM traps WHERE id=?", ctx["closed_trap"])["closed_how"] == "disputed"
            assert not db.one(f"SELECT 1 FROM attempts WHERE id=? AND {progress.COUNTED}", a["id"])
    a, got = first
    ctx = json.loads(db.one("SELECT context FROM reports WHERE id=?", got["id"])["context"])

    os.environ["SATF_ADMIN_TOKEN"] = "f6-admin"
    H = {"X-Admin": "f6-admin"}
    assert c.get("/api/admin/reports", headers={"X-Admin": "nope"}).status_code == 403
    thin = c.get(f"/api/admin/reports/{rids[1]}", headers=H).json()     # U3 7: thin is never explained
    assert (thin["status"], thin["check_outcome"], thin["check"]["why"]) == ("new", "unsure", "thin"), thin
    listing = c.get("/api/admin/reports", headers=H).json()
    assert got["id"] in [x["id"] for x in listing["flagged"]] and listing["mail"] in ("smtp", "outbox")
    put = c.put(f"/api/admin/reports/{got['id']}", headers=H,
                json={"status": "no_change", "reply": "Key checked", "dispute_outcome": "key_right"})
    assert put.status_code == 200, put.text
    assert db.one("SELECT disputed FROM attempts WHERE id=?", a["id"])["disputed"] == 0
    t = db.one("SELECT * FROM traps WHERE id=?", ctx["closed_trap"])
    assert t["closed"] is None and t["owed"] == progress.OWED
    mine = {r["id"]: r for r in c.get("/api/reports", headers={"X-Learner": d}).json()}
    assert mine[got["id"]]["unread"] and mine[got["id"]]["reply"] == "Key checked"
    assert "counts again" in mine[got["id"]]["outcome_text"]
    assert reports.shell(d)["report_replies"] == 1
    c.post("/api/reports/seen", headers={"X-Learner": d})
    assert reports.shell(d)["report_replies"] == 0
    detail = c.get(f"/api/admin/reports/{got['id']}", headers=H).json()
    assert detail["question"]["answer"] and detail["question"]["audit"] == "ok"
    print("ok  F6 reports: bounded disputes, admin 404 unset, key right reopens the mistake, replies unread")


def instant(c) -> None:
    """U3's outcomes, and the admin's fix for everyone."""
    H = {"X-Admin": "f6-admin"}
    # explained: C's norm is picked by 1 of 20 strong and 15 of 100 others
    it = reports._from_bank("circle.convert", 1)
    norm_c = progress.norm(it["reasons"][2])
    seed_crowd("circle.convert", it["topic"], norm_c, strong_on=1, others_on=15)
    e = fresh("expl")
    sid, q = sitting(e, "circle.convert", 1)
    progress.record(e, sid, q, 2)
    with strong_patch():
        got = post(c, e, {"kind": "question", "source": "drill", "session": sid, "question_id": q["id"],
                          "category": "key_wrong", "answer": "C"})
    chk = got["check"]
    assert chk["outcome"] == "explained" and chk["reason"] == it["reasons"][2], chk
    assert "numbers check out" in chk["text"] and "Checked:" not in chk["text"]
    assert attempt(e, sid, q)["disputed"] == 0
    r = c.post(f"/api/reports/{got['id']}/accept", headers={"X-Learner": e}).json()
    assert r["status"] == "no_change"
    listed = {x["id"]: x for x in c.get("/api/reports", headers={"X-Learner": e}).json()}
    assert listed[got["id"]]["status"] == "no_change" and reports.open_disputes(e) == 0   # no dispute slot used

    # the Strong-student signal: 12 of 20 strong pick D's norm
    it = reports._from_bank("circle.equal_area_square", 1)
    norm_d = progress.norm(it["reasons"][3])
    seed_crowd("circle.equal_area_square", it["topic"], norm_d, strong_on=12, others_on=15)
    s = fresh("sig")
    sid, q = sitting(s, "circle.equal_area_square", 1)
    progress.record(s, sid, q, 3)
    with strong_patch():
        got = post(c, s, {"kind": "question", "source": "drill", "session": sid, "question_id": q["id"],
                          "category": "key_wrong", "answer": "D"})
    assert got["check"]["outcome"] == "unsure" and "strong in" in got["check"]["text"], got
    row = db.one("SELECT * FROM reports WHERE id=?", got["id"])
    assert json.loads(row["check"])["signal"]["strong"] == 0.6 and row["dispute"] == 0
    assert attempt(s, sid, q)["disputed"] == 1
    flagged = c.get("/api/admin/reports", headers=H).json()["flagged"]
    assert any(x["id"] == got["id"] and x["signal"] for x in flagged)

    # broken: the item check fails on this seed; nobody is served it again
    b = fresh("brk")
    sid, q = sitting(b, "circle.convert", 7)
    progress.record(b, sid, q, wrong(q))
    with patch.object(reports, "check_item", lambda item: ["the stem asks for the diameter"]):
        got = post(c, b, {"kind": "question", "source": "drill", "session": sid, "question_id": q["id"],
                          "category": "key_wrong"})
    assert got["check"]["outcome"] == "broken" and "problems" not in got["check"]
    assert attempt(b, sid, q)["disputed"] == 1
    assert reports.quarantined("circle.convert", 7) and reports.removed("circle.convert", 7)
    assert not reports.quarantined("circle.convert", 8)

    # remarked: a grid-in marked wrong that today's rules accept
    g = fresh("rmk")
    sid, q = sitting(g, "circles.degree_radian", 25)
    db.run("INSERT INTO attempts(learner,session,qid,template,seed,topic,difficulty,fmt,correct,given,at,repeat)"
           " VALUES (?,?,?,?,?,?,?,?,0,?,?,0)", g, sid, q["id"], q["key"], q["seed"], q["topic"], q["difficulty"],
           "spr", q["answer"], deps.now())
    got = post(c, g, {"kind": "question", "source": "drill", "session": sid, "question_id": q["id"],
                      "category": "key_wrong"})
    assert got["check"]["outcome"] == "remarked" and got["status"] == "fixed", got
    assert attempt(g, sid, q)["correct"] == 1

    # forms: 0.055 for 1/18 is too short for the grid
    f = fresh("frm")
    sid, q = sitting(f, "circles.degree_radian", 25)
    progress.record(f, sid, q, ".055")
    got = post(c, f, {"kind": "question", "source": "drill", "session": sid, "question_id": q["id"],
                      "category": "key_wrong", "answer": ".055"})
    assert got["check"]["outcome"] == "forms" and ".0556" in got["check"]["text"], got

    # stem, figure and option categories: a person, no lesson
    got = post(c, f, {"kind": "question", "source": "drill", "session": sid, "question_id": q["id"],
                      "category": "figure"})
    assert "check" not in got and got["status"] == "new"

    # me too: a second learner on the same (template, seed) joins the first
    m2 = fresh("me2")
    sid2, q2 = sitting(m2, "circles.degree_radian", 25, given="7")
    sim =c.get(f"/api/reports/similar?session={sid2}&qid={q2['id']}", headers={"X-Learner": m2}).json()
    assert sim["open"] >= 1 and sim["id"], sim
    joined = post(c, m2, {"kind": "question", "source": "drill", "session": sid2, "question_id": q2["id"],
                          "parent": sim["id"]})
    assert db.one("SELECT parent FROM reports WHERE id=?", joined["id"])["parent"] == sim["id"]

    # the admin's key was wrong, every seed since a date: every learner's attempts, a correction each
    t = "circle.equal_area_square"
    x, y = fresh("fixa"), fresh("fixb")
    sx, qx = sitting(x, t, 90)
    progress.record(x, sx, qx, wrong(qx))
    sy, qy = sitting(y, t, 91)
    progress.record(y, sy, qy, wrong(qy))
    got = post(c, x, {"kind": "question", "source": "drill", "session": sx, "question_id": qx["id"],
                      "category": "figure", "email": "reporter@example.com"})
    before = len(list(mail.OUTBOX.glob("*.eml"))) if mail.OUTBOX.exists() else 0
    put = c.put(f"/api/admin/reports/{got['id']}", headers=H,
                json={"status": "fixed", "reply": "Fixed, thanks", "dispute_outcome": "key_wrong",
                      "scope": "template", "since": "2020-01-01", "fixed_note": "Figure redrawn"}).json()
    assert put["corrected"]["learners"] >= 2
    for who, sid_, q_ in ((x, sx, qx), (y, sy, qy)):
        assert attempt(who, sid_, q_)["disputed"] == 1
        assert any(i["kind"] == "correction" for i in reports.feed(who)), who
    assert len(list(mail.OUTBOX.glob("*.eml"))) == before + 1          # the reply went to the reply-to address
    fixed = c.get("/api/reports/fixed").json()
    assert any(r["change"] == "Figure redrawn" for r in fixed)
    assert "a:" not in json.dumps(fixed) and "@" not in json.dumps(fixed)
    labels = c.get("/api/admin/labels", headers=H).json()
    assert isinstance(labels, list)
    print("ok  F6 reports: instant check (explained, signal, broken, remarked, forms), me too, fix for everyone")


def admin_bits(c) -> None:
    H = {"X-Admin": "f6-admin"}
    a = fresh("adm")
    os.environ["SATF_REPORTS_TO"] = "staff@example.com"
    before = len(list(mail.OUTBOX.glob("*.eml"))) if mail.OUTBOX.exists() else 0
    try:
        got = post(c, a, {"kind": "page", "category": "bug", "details": "the chart is blank", "page": "/results/"},
                   [("shot.png", PNG, "image/png")])
    finally:
        os.environ.pop("SATF_REPORTS_TO", None)
    assert len(list(mail.OUTBOX.glob("*.eml"))) == before + 1
    f = c.get(f"/api/admin/files/{got['id']}/1.png", headers=H)
    assert f.status_code == 200 and f.content == PNG and f.headers["content-type"] == "image/png"
    assert c.get(f"/api/admin/files/{got['id']}/1.png").status_code == 403
    assert c.get(f"/api/admin/files/{got['id']}/..%2F..%2Fdb.py", headers=H).status_code == 404
    q = c.get("/api/admin/question?t=circle.convert&s=8", headers=H).json()
    assert q["key"] and q["reasons"] and q["audit"] == "ok"
    stop = c.post("/api/admin/quarantine", headers=H, json={"template": "circle.convert", "note": "all seeds"})
    assert stop.json()["quarantined"] and reports.quarantined("circle.convert", 12345)
    c.post("/api/admin/quarantine/release", headers=H, json={"template": "circle.convert"})
    assert not reports.quarantined("circle.convert", 12345)
    assert reports.delete_files(a) == 1 and not (reports.FILES / str(got["id"])).exists()
    os.environ.pop("SATF_ADMIN_TOKEN", None)
    print("ok  F6 reports: admin files, question, quarantine, mail notice, delete_files")


def rescoring(c) -> None:
    """SR19: a broken or remarked question re-scores the finished sitting that
    holds it; an open dispute changes nothing in the score."""
    from satbank.registry import templates
    from server import api_tests
    r = fresh("rsc")
    pool = [t for t in templates() if t.startswith("lin.")][:6]
    spr_seed = next(s for s in range(7100, 7300) if reports._from_bank("circles.degree_radian", s)["type"] == "spr")
    paper, answers = [], {}
    for i in range(44):
        t, s = ("circles.degree_radian", spr_seed) if i == 43 else (pool[i % len(pool)], 7000 + i)
        q = reports._from_bank(t, s) | {"id": f"m{'1' if i < 22 else '2l'}q{i % 22 + 1:02d}"}
        paper.append(q)
        answers[q["id"]] = pick(q, i % 3 != 0)
    sid = f"f6-mock-{fresh('m')}"
    db.run("INSERT INTO sessions(id,kind,mock_id,route,questions,learner,started,finished,answers,cfg,result)"
           " VALUES (?,?,?,?,?,?,?,?,?,?,?)", sid, "mock", "new", "lower",
           json.dumps({"module1": paper[:22], "module2": paper[22:]}), r, deps.now(), deps.now(),
           json.dumps(answers), "{}", json.dumps({}))
    progress.record_paper(r, sid, api_tests.marked_questions(deps.session_or_404(sid)), answers)
    base = estimate.rescore(sid)
    db.run("UPDATE sessions SET result=? WHERE id=?", json.dumps({"estimate": {"low": base["low"], "high": base["high"]}}), sid)
    result = lambda: json.loads(db.one("SELECT result FROM sessions WHERE id=?", sid)["result"])  # noqa: E731
    body = {"kind": "question", "source": "report", "session": sid, "category": "key_wrong"}

    # 1: broken -> removed from scoring, one rescored entry, and the reply says so
    with patch.object(reports, "check_item", lambda item: ["the stem asks for the diameter"]):
        got = post(c, r, {**body, "question_id": "m1q04"})
    assert got["check"]["outcome"] == "broken", got
    res = result()
    assert [(x["qid"], x["how"], x["report"]) for x in res["rescored"]] == [("m1q04", "removed", got["id"])], res
    assert res["removed"] == ["m1q04"] and res["estimate"]["low"] is not None
    mine = {x["id"]: x for x in c.get("/api/reports", headers={"X-Learner": r}).json()}
    assert "re-scored 1 sitting." in mine[got["id"]]["outcome_text"], mine[got["id"]]

    # 2: a grid-in marked wrong that today's rules accept counts right, and the band doesn't fall
    db.run("UPDATE attempts SET correct=0 WHERE session=? AND qid='m2lq22'", sid)
    before = result()["estimate"]
    got = post(c, r, {**body, "question_id": "m2lq22"})
    assert got["check"]["outcome"] == "remarked" and got["status"] == "fixed", got
    res = result()
    assert res["rescored"][-1]["how"] == "remarked" and res["remarked"] == ["m2lq22"], res["rescored"]
    assert res["estimate"]["low"] + res["estimate"]["high"] >= before["low"] + before["high"]

    # 3: an open dispute leaves the estimate as it was
    before = result()
    got = post(c, r, {**body, "question_id": "m1q07", "dispute": True})
    assert got.get("disputed") and got["check"]["outcome"] == "unsure", got
    assert result() == before
    print("ok  F6 reports: SR19 re-scoring (broken removed, remarked right), an open dispute leaves the score")


def labels(c) -> None:
    """V6: 'The label is wrong' files the attempt's address; the Labels view
    counts it with the 'Not what I did?' corrections, flagged at 15% of 20."""
    H = {"X-Admin": "f6-admin"}
    os.environ["SATF_ADMIN_TOKEN"] = "f6-admin"
    t = "circles.degree_radian"
    it = reports._from_bank(t, 26)
    k = pick(it, False)
    norm = progress.norm(it["reasons"][k])
    L = fresh("lbl")
    sid, q = sitting(L, t, 26, given=k)
    got = post(c, L, {"kind": "question", "source": "drill", "session": sid, "question_id": q["id"],
                      "category": "Wrong mistake label", "answer": "ABCD"[k]})
    row = db.one("SELECT category, template, seed FROM reports WHERE id=?", got["id"])
    a = attempt(L, sid, q)
    assert tuple(row) == ("label", a["template"], a["seed"]) and "check" not in got, dict(row)
    for i in range(19):                         # 19 more fell for it; 2 said it was a misread
        db.run("INSERT INTO attempts(learner,template,seed,topic,difficulty,fmt,correct,reason,norm,miss_kind,at,repeat)"
               " VALUES (?,?,?,?,?,?,0,?,?,?,?,0)", f"a:f6lbl-crowd{i}", t, 600 + i, it["topic"], it["difficulty"],
               "mcq", it["reasons"][k], norm, "misread" if i < 2 else None, deps.now())
    view = next(x for x in c.get("/api/admin/labels", headers=H).json() if (x["template"], x["norm"]) == (t, norm))
    assert (view["learners"], view["disputed"], view["rate"], view["flagged"]) == (20, 3, 0.15, True), view
    assert view["reason"] == it["reasons"][k]
    os.environ.pop("SATF_ADMIN_TOKEN", None)
    print("ok  F6 reports: V6 label reports and corrections in the admin Labels view")


def terminal() -> None:
    """tools/reports.py answers from a terminal through the admin's own functions."""
    import contextlib
    import importlib.util
    import io
    spec = importlib.util.spec_from_file_location("f6_cli", pathlib.Path(__file__).resolve().parents[2] / "tools" / "reports.py")
    cli = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cli)
    rid = reports.create(fresh("cli"), reports.ReportIn(kind="page", category="idea", title="dark mode please"), [])["id"]
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        assert cli.main(["list", "--status", "new"]) == 0
        assert cli.main(["reply", str(rid), "Done, thanks", "--status", "fixed", "--note", "Dark mode"]) == 0
        assert cli.main(["item", "circle.convert", "8"]) == 0
        assert cli.main(["labels"]) == 0
    assert f"#{rid}" in out.getvalue() and '"audit": "ok"' in out.getvalue()
    row = db.one("SELECT status, reply FROM reports WHERE id=?", rid)
    assert tuple(row) == ("fixed", "Done, thanks"), dict(row)
    print("ok  F6 reports: tools/reports.py lists, replies, regenerates and prints labels")


# ------------------------------------------------------------------ sets (R18(c), P22, U28, V17, W20, X22)

SECRET = ("stem", "choices", "answer", "rationale", "reasons", "seed", "template", "ctx", "context", "pick")


def hdr(learner: str) -> dict:
    return {"X-Learner": learner}


def named(learner: str, name: str) -> str:
    db.run("INSERT OR REPLACE INTO learners(id,name,created) VALUES (?,?,?)", learner, name, deps.now())
    return learner


def pick(q: dict, right: bool, norm: str | None = None):
    """What a student would send: the key, or a wrong option that names a mistake."""
    if q["type"] != "mcq":
        return q["answer"] if right else "-999"
    k = "ABCD".index(q["answer"])
    if right:
        return k
    opts = [i for i, r in enumerate(q["reasons"]) if i != k and r]
    if norm:
        opts = [i for i in opts if progress.norm(q["reasons"][i]) == norm] or opts
    return opts[0] if opts else (k + 1) % 4


def run_drill(c, learner: str, pairs, right=(), want=None) -> str:
    """A drill of exact items answered over HTTP, then finished: right where the
    question's position (0-based) is in `right`, else a named wrong option."""
    from server import drill
    sid = f"f6-drill-{fresh('d')}"
    drill.create(learner, sid, list(dict.fromkeys(sets._topic(t) for t, _ in pairs)), len(pairs),
                 None, False, "shared", items=[list(p) for p in pairs])
    return answer_all(c, learner, sid, right, want)


def answer_all(c, learner: str, sid: str, right=(), want=None) -> str:
    n = 0
    while True:
        nxt = c.post(f"/api/drill/{sid}/next", headers=hdr(learner)).json()
        if nxt.get("done") or not nxt.get("question"):
            break
        q = json.loads(db.one("SELECT questions FROM sessions WHERE id=?", sid)["questions"])[-1]
        body = {"question_id": q["id"], "ms": 40000 + 1000 * n,
                "answer": pick(q, q.get("repair") or n in right, (want or {}).get(n))}
        assert c.post(f"/api/drill/{sid}/answer", headers=hdr(learner), json=body).status_code == 200
        n += 0 if q.get("repair") else 1
    assert c.post(f"/api/drill/{sid}/finish", headers=hdr(learner)).status_code == 200
    return sid


def take(c, learner: str, code: str, right=(), show_name: bool = False, twins=None, want=None) -> tuple[str, list]:
    """A visitor's start from the landing, over HTTP, answered and finished."""
    body = {"show_name": show_name, **({"exact": False} if twins else {})}
    r = c.post(f"/api/sets/{code}/start", headers=hdr(learner), json=body)
    assert r.status_code == 200 and r.json()["question"], (r.status_code, r.text[:300])
    sid = answer_all(c, learner, r.json()["id"], right, want)
    assert db.one("SELECT shared_from FROM sessions WHERE id=?", sid)["shared_from"] == code
    return sid, served(sid)


def served(sid: str) -> list:
    return [[q["key"], q["seed"]] for q in json.loads(db.one("SELECT questions FROM sessions WHERE id=?", sid)["questions"])
            if not q.get("repair")]


def via_drill(c, learner: str, code: str, status: int = 200) -> str | None:
    """POST /api/drill {pool:'set'}, once F5's drill serves through sets.serve() and
    link() (it takes show_name then); None before that."""
    from server import drill
    if "show_name" not in getattr(drill, "FIELDS", ()):
        return None
    r = c.post("/api/drill", headers=hdr(learner), json={"pool": "set", "ids": code, "source": "shared",
                                                          "show_name": False})
    assert r.status_code == status, (r.status_code, r.text[:300])
    if status != 200:
        return None
    sid = r.json()["id"]
    assert db.one("SELECT shared_from FROM sessions WHERE id=?", sid)["shared_from"] == code
    return answer_all(c, learner, sid)


def make(c, learner: str, body: dict, code: int = 200) -> dict:
    r = c.post("/api/sets", headers=hdr(learner), json=body)
    assert r.status_code == code, (r.status_code, r.text[:300], body)
    return r.json()


def stems(sid: str) -> list[str]:
    return [q["stem"] for q in json.loads(db.one("SELECT questions FROM sessions WHERE id=?", sid)["questions"])
            if not q.get("repair")]


def public_ok(got: dict) -> None:
    text = json.dumps(got)
    assert not any(f'"{k}"' in text for k in SECRET), text[:400]


def sets_exact(c) -> None:
    owner, b = named(fresh("so"), "Maya"), named(fresh("sb"), "Sam")
    pairs = [("lin.evaluate", 40), ("circle.convert", 40), ("circle.convert", 41)]
    sid = run_drill(c, owner, pairs, right={0, 2})
    made = make(c, owner, {"kind": "set", "session": sid})
    code = made["code"]
    assert sets.CODE_OK.match(code) and made["url"] == f"/s/?c={code}" and made["count"] == 3, made
    assert make(c, owner, {"kind": "set", "session": sid})["code"] == code        # the same set, the same link
    make(c, b, {"kind": "set", "session": sid}, code=403)                         # someone else's set
    pub = c.get(f"/api/sets/{code}").json()
    public_ok(pub)
    assert (pub["count"], pub["by"], pub["fresh"], pub["mine"]) == (3, "Maya", False, False), pub
    assert {t["name"] for t in pub["topics"]} == {"Linear functions", "Circles"} or len(pub["topics"]) == 2, pub
    assert c.get(f"/api/sets/{code.lower()}").status_code == 200
    assert c.get("/api/sets/ZZZZZZZZ").status_code == 404 and c.get("/api/sets/nope").status_code == 404
    assert c.get(f"/api/sets/{code}", headers=hdr(owner)).json()["mine"] is True

    # a second learner gets identical stems, and the owner sees how they did
    c.get(f"/api/sets/{code}", headers=hdr(b))
    tb, served = take(c, b, code, right={0}, show_name=True)
    assert served == [list(p) for p in pairs] and stems(tb) == stems(sid), (served, pairs)
    mine = c.get(f"/api/sets/{code}", headers=hdr(b)).json()
    assert mine["yours"]["session"] == tb and mine["yours"]["finished"] and mine["yours"]["right"] == 1, mine
    assert c.get(f"/api/sets/{code}/results", headers=hdr(b)).status_code == 403
    assert c.get(f"/api/sets/{code}").json()["taken"] == 1                     # Practice 15, public
    res = c.get(f"/api/sets/{code}/results", headers=hdr(owner)).json()
    assert (res["taken"], res["tried"], res["opened"]) == (1, 1, 1), res
    q2 = res["questions"][1]
    assert (q2["right"], q2["asked"], q2["rate"]) == (0, 1, 0.0) and q2["type_name"], q2
    it = reports._from_bank("circle.convert", 40)
    wrong_i = pick(it, False)
    assert q2["top_wrong"] == {"reason": it["reasons"][wrong_i], "norm": progress.norm(it["reasons"][wrong_i]),
                               "count": 1, "given": "ABCD"[wrong_i]}, q2
    t0 = res["takers"][0]
    assert (t0["name"], t0["marks"], t0["right"], t0["asked"]) == ("Sam", [1, 0, 0], 1, 3), t0
    assert res["you"]["marks"] == [1, 0, 1] and res["questions"][0]["you"]["correct"] is True, res["you"]
    # the taker's comparison: labels, never a raw answer
    peers = c.get(f"/api/sets/{code}/compare", headers=hdr(b)).json()
    assert [p["name"] for p in peers["people"]] == ["Maya", "Sam"] and peers["people"][1]["you"], peers
    assert '"given"' not in json.dumps(peers) and peers["slots"][1]["you"] is False, peers
    assert peers["people"][1]["marks"][1]["mistake"] == it["reasons"][wrong_i], peers["people"][1]
    assert sets.peers(sid, owner)["people"][0]["you"] is True        # the sharer's own report lists them too
    assert c.get(f"/api/sets/{code}/compare", headers=hdr(fresh("sx"))).status_code == 403
    listed = c.get("/api/sets", headers=hdr(owner)).json()
    assert listed[0]["code"] == code and (listed[0]["opened"], listed[0]["taken"]) == (1, 1), listed[0]
    # QBank 15 through the engine itself: Practice's banner starts with POST /api/drill {pool:'set'}
    d = via_drill(c, fresh("sd"), code)
    if d:
        assert stems(d) == stems(sid) and c.get(f"/api/sets/{code}").json()["taken"] == 2

    # revoke: only the owner; then 410 everywhere public, and the owner keeps the results
    assert c.delete(f"/api/sets/{code}", headers=hdr(b)).status_code == 403
    assert c.delete(f"/api/sets/{code}", headers=hdr(owner)).json()["revoked"]
    assert c.get(f"/api/sets/{code}").status_code == 410
    assert c.get(f"/api/sets/{code}/compare", headers=hdr(b)).status_code == 410
    try:
        sets.serve(code, fresh("sy"))
        raise AssertionError("a revoked set was served")
    except HTTPException as e:
        assert e.status_code == 410
    assert c.get(f"/api/sets/{code}/results", headers=hdr(owner)).json()["revoked"]
    assert make(c, owner, {"kind": "set", "session": sid})["code"] != code      # a new link after stopping
    print("ok  F6 sets: exact share, identical stems, public summary, results, peers, revoke 410")


def sets_items(c) -> None:
    owner, v = named(fresh("io"), "Ana"), fresh("iv")
    # today's challenge is never shared, even by someone who answered it
    from server import challenge, daily
    ch = challenge.challenge(daily.today(0))[0]
    sitting(owner, ch["key"], ch["seed"], given=0)
    got = make(c, owner, {"kind": "items", "items": [[ch["key"], ch["seed"]]]}, code=409)
    assert got["detail"]["reason"] == "not_shareable", got
    make(c, owner, {"kind": "items", "items": [["circle.convert", 45]]}, code=409)       # never shown to them
    make(c, owner, {"kind": "items", "items": [["circle.convert", s] for s in range(41)]}, code=422)
    make(c, owner, {"kind": "items", "items": [["circle.convert", 45]], "cfg": {"bogus": 1}}, code=422)

    # V17: ask for help with a miss; the context waits until the visitor has answered it
    q = reports._from_bank("circle.convert", 42)
    miss = pick(q, False)
    sitting(owner, "circle.convert", 42, given=miss)
    db.run("INSERT OR REPLACE INTO notes(learner,template,seed,note,at) VALUES (?,?,?,?,?)",
           owner, "circle.convert", 42, "I mixed up radius and diameter", deps.now())
    help_ = make(c, owner, {"kind": "items", "items": [["circle.convert", 42]], "cfg": {"context": True}})
    before = c.get(f"/api/sets/{help_['code']}", headers=hdr(v)).json()
    public_ok(before)
    assert before["help"] is True and before["count"] == 1, before
    take(c, v, help_["code"], right={0})
    after = c.get(f"/api/sets/{help_['code']}", headers=hdr(v)).json()["context"][0]
    assert (after["pick"], after["mistake"], after["correct"]) == ("ABCD"[miss], q["reasons"][miss], False), after
    assert "note" not in after and after["family"]["seen"] >= 1, after
    with_note = make(c, owner, {"kind": "items", "items": [["circle.convert", 42]],
                                "cfg": {"context": True, "note": True}})
    assert with_note["code"] != help_["code"]
    take(c, v, with_note["code"], right={0})
    got = c.get(f"/api/sets/{with_note['code']}", headers=hdr(v)).json()["context"][0]
    assert got["note"] == "I mixed up radius and diameter", got
    assert "radius and diameter" not in json.dumps(c.get(f"/api/sets/{help_['code']}", headers=hdr(v)).json())
    # "Fresh versions instead": the same template on the visitor's own numbers, and the
    # sharer's context once the twin is answered; a fresh help share the same way
    w = fresh("iw")
    _, got = take(c, w, help_["code"], right={0}, twins=True)
    assert got[0][0] == "circle.convert" and got[0][1] != 42, got
    assert c.get(f"/api/sets/{help_['code']}", headers=hdr(w)).json()["context"][0]["pick"] == "ABCD"[miss]
    twin_help = make(c, owner, {"kind": "items", "items": [["circle.convert", 42]],
                                "cfg": {"context": True, "fresh": True}})
    w2 = fresh("iw2")
    assert "context" not in c.get(f"/api/sets/{twin_help['code']}", headers=hdr(w2)).json()
    _, got = take(c, w2, twin_help["code"])
    ctx = c.get(f"/api/sets/{twin_help['code']}", headers=hdr(w2)).json()["context"][0]
    assert got[0][1] != 42 and ctx["mistake"] == q["reasons"][miss], (got, ctx)
    print("ok  F6 sets: Review items through access(), today's challenge 409, help context after answering")


def sets_twins(c) -> None:
    owner = named(fresh("to"), "Lee")
    pairs = [("circle.convert", 40), ("circle.convert", 41), ("lin.evaluate", 41)]
    norms = []
    for t, s in pairs:
        q = reports._from_bank(t, s)
        k = pick(q, False)
        sitting(owner, t, s, given=k)
        norms.append(progress.norm(q["reasons"][k]))
    made = make(c, owner, {"kind": "set", "items": [list(p) for p in pairs], "cfg": {"fresh": True}})
    slots = json.loads(db.one("SELECT cfg FROM sets WHERE code=?", made["code"])["cfg"])["slots"]
    assert [s[3] for s in slots] == norms, slots
    a, b = fresh("ta"), fresh("tb")
    got_a, got_b = sets.serve(made["code"], a), sets.serve(made["code"], b)
    assert [t for t, _ in got_a["items"]] == [t for t, _ in got_b["items"]] == [t for t, _ in pairs]
    assert all(x[1] != y[1] for x, y in zip(got_a["items"], got_b["items"])), (got_a, got_b)
    assert all(tuple(x) not in pairs for x in got_a["items"])
    for (t, s), norm, (_, s0) in zip(got_a["items"], norms, pairs):
        item = sets._item(t, s)
        assert item.difficulty == sets._item(t, s0).difficulty and norm in sets._norms(item), (t, s, norm)
    ta, _ = take(c, a, made["code"], right={0, 1}, want=dict(enumerate(norms)))
    tb, _ = take(c, b, made["code"], right={0}, want=dict(enumerate(norms)))
    res = c.get(f"/api/sets/{made['code']}/results", headers=hdr(owner)).json()
    assert [t["marks"] for t in res["takers"]] == [[1, 1, 0], [1, 0, 0]], res["takers"]
    assert [(q["right"], q["asked"]) for q in res["questions"]] == [(2, 2), (1, 2), (0, 2)], res["questions"]
    top = res["questions"][2]["top_wrong"]
    assert top["norm"] == norms[2] and top["count"] == 2 and "given" not in top, top
    assert all(t["name"] is None for t in res["takers"]), res["takers"]        # nobody chose to be named

    # U28: a question link sends a twin
    one = make(c, owner, {"kind": "set", "cfg": {"templates": ["lin.evaluate"], "count": 1, "fresh": True}})
    x, y = fresh("tx"), fresh("ty")
    sx, (px,) = take(c, x, one["code"], right={0})
    sy, (py,) = take(c, y, one["code"])
    assert px[0] == py[0] == "lin.evaluate" and px[1] != py[1]
    res = c.get(f"/api/sets/{one['code']}/results", headers=hdr(owner)).json()
    assert [(t["right"], t["asked"]) for t in res["takers"]] == [(1, 1), (0, 1)] and all(t["ms"] for t in res["takers"])
    assert (res["you"]["right"], res["you"]["asked"]) == (0, 1), res.get("you")    # the sharer's own miss on lin.evaluate
    d = via_drill(c, fresh("tz"), one["code"])                   # a slot-only set through the engine: a twin
    if d:
        assert served(d)[0][0] == "lin.evaluate" and c.get(f"/api/sets/{one['code']}").json()["taken"] == 3
    d = via_drill(c, fresh("tw"), made["code"])                  # never the sharer's own seeds
    if d:
        assert not {tuple(x) for x in served(d)} & set(pairs), served(d)
    print("ok  F6 sets: twins per slot with the sharer's trap, results per slot, a question link's twin")


def sets_test(c) -> None:
    from server import api_tests
    owner, v = named(fresh("xo"), "Ana"), fresh("xv")
    qs = [reports._from_bank("circle.convert", s) | {"id": f"m{s}"} for s in (50, 51, 52)]
    sid = f"f6-module-{fresh('m')}"
    db.run("INSERT INTO sessions(id,kind,questions,learner,started,finished,answers,cfg) VALUES (?,?,?,?,?,?,?,?)",
           sid, "module", json.dumps({"module1": qs}), owner, deps.now(), deps.now(), "{}", "{}")
    progress.record_paper(owner, sid, api_tests.marked_questions(deps.session_or_404(sid)), {})
    made = make(c, owner, {"kind": "test", "session": sid, "show_score": False})
    pub = c.get(f"/api/sets/{made['code']}").json()
    public_ok(pub)
    assert (pub["kind_label"], pub["modules"], pub["minutes"], pub["show_score"]) == ("Module", [3], 35, False), pub
    exact = sets.serve(made["code"], v)
    assert exact["items"] == [["circle.convert", s] for s in (50, 51, 52)] and exact["modules"] == [1, 1, 1]
    twins = make(c, owner, {"kind": "test", "session": sid, "cfg": {"fresh": True}})
    a, b = sets.serve(twins["code"], fresh("xa")), sets.serve(twins["code"], fresh("xb"))
    tiers = [sets._item(t, s).difficulty for t, s in exact["items"]]
    for got in (a, b):
        assert [sets._item(t, s).difficulty for t, s in got["items"]] == tiers
    assert all(x[1] != y[1] for x, y in zip(a["items"], b["items"]))
    live = f"f6-module-{fresh('m')}"
    db.run("INSERT INTO sessions(id,kind,questions,learner,started,answers,cfg) VALUES (?,?,?,?,?,?,?)",
           live, "module", json.dumps({"module1": qs}), owner, deps.now(), "{}", "{}")
    make(c, owner, {"kind": "test", "session": live}, code=409)             # not finished
    drill_sid, _ = sitting(owner, "circle.convert", 53, given=0)
    make(c, owner, {"kind": "test", "session": drill_sid}, code=422)        # a practice set is kind 'set'
    assert c.post(f"/api/sets/{made['code']}/start", headers=hdr(v), json={}).status_code == 422   # Tests starts it
    make(c, owner, {"kind": "test"}, code=422)
    ch, _ = sitting(owner, "circle.convert", 54, given=0, kind="challenge")
    make(c, owner, {"kind": "set", "session": ch}, code=409)                # challenge sets are not shared
    print("ok  F6 sets: a finished test shared exactly or as twins slot by slot, refusals")


def sets_words(c) -> None:
    owner = fresh("wo")
    made = make(c, owner, {"kind": "words", "items": ["mitigate", "bolster", "Mitigate"]})
    pub = c.get(f"/api/sets/{made['code']}").json()
    assert pub["words"] == [{"slug": "mitigate"}, {"slug": "bolster"}] and pub["count"] == 2, pub
    assert c.get(f"/api/sets/{made['code']}/results", headers=hdr(owner)).status_code == 409
    assert c.post(f"/api/sets/{made['code']}/start", headers=hdr(fresh("wv")), json={}).status_code == 422
    via_drill(c, fresh("wv"), made["code"], status=422)
    db.run("INSERT INTO my_words(id,learner,word,meaning,created) VALUES (?,?,?,?,?)",
           "w1", owner, "quixotic", "idealistic to the point of being impractical", deps.now())
    own = make(c, owner, {"kind": "words", "items": ["own:w1"]})
    assert c.get(f"/api/sets/{own['code']}").json()["words"][0]["word"] == "quixotic"
    make(c, owner, {"kind": "words", "items": ["own:nope"]}, code=404)
    make(c, owner, {"kind": "words", "items": ["<script>"]}, code=422)
    # the sample is read-only, and links are capped per hour
    make(c, "sample:f6", {"kind": "words", "items": ["mitigate"]}, code=403)
    with patch.object(sets, "PER_HOUR", 2):
        make(c, owner, {"kind": "words", "items": ["candid"]}, code=429)
    print("ok  F6 sets: word lists, own words copied, sample read-only, 30 links an hour")


def static() -> None:
    """Decision 5 (no classes) across F6's files, and R18(c)'s one navigator.share, behind a tap."""
    root = pathlib.Path(__file__).resolve().parents[2]
    files = ["server/reports.py", "server/sets.py", "server/mail.py", "tools/reports.py", "web/assets/report.js",
             "web/admin/reports/index.html", "web/s/index.html"]
    for f in files:
        text = (root / f).read_text()
        hits = [w for w in ("teacher", "assignment", "homework", "/class/", "/join/") if w in text.lower()]
        assert not hits, (f, hits)
        for i in [i for i in range(len(text)) if text.startswith("navigator.share(", i)]:
            assert "More ways to share" in text[max(0, i - 300):i] and "click" in text[max(0, i - 120):i], (f, i)
    print("ok  F6: no classes in its files; navigator.share only from a tap on More ways to share")


def check(client) -> None:
    keep = reports.FILES
    with tempfile.TemporaryDirectory(prefix="satf-f6-") as path:
        reports.FILES = pathlib.Path(path) / "reports"
        try:
            basics(client)
            contexts(client)
            disputes(client)
            instant(client)
            admin_bits(client)
            rescoring(client)
            labels(client)
            terminal()
            sets_exact(client)
            sets_items(client)
            sets_twins(client)
            sets_test(client)
            sets_words(client)
            static()
        finally:
            reports.FILES = keep
            os.environ.pop("SATF_ADMIN_TOKEN", None)


# ------------------------------------------------------------------ the pages, in a browser (--browser)

CHROME = ("/Users/workingmyassof/Library/Caches/ms-playwright/chromium_headless_shell-1243/"
          "chrome-headless-shell-mac-arm64/chrome-headless-shell")
PORT = 8016


def browser() -> None:
    """Shell 15's modal in a live sitting, the /s/ landing and the admin page,
    in headless Chrome against a server on port 8016 over a throwaway database."""
    import socket
    import subprocess
    import sys
    import time

    import httpx
    from playwright.sync_api import sync_playwright

    root = pathlib.Path(__file__).resolve().parents[2]
    base = f"http://127.0.0.1:{PORT}"
    with tempfile.TemporaryDirectory(prefix="satf-f6web-") as path:
        env = {**os.environ, "SATF_DB": f"{path}/f6-web.db", "SATF_REPORTS": f"{path}/reports",
               "SATF_ADMIN_TOKEN": "f6-admin", "PYTHONPATH": str(root)}
        env.pop("SATF_SMTP_HOST", None)
        env.pop("SATF_REPORTS_TO", None)
        with socket.socket() as sock:              # someone else's server here would answer for ours
            assert sock.connect_ex(("127.0.0.1", PORT)) != 0, f"port {PORT} is in use"
        srv = subprocess.Popen([sys.executable, "-m", "uvicorn", "server.app:app", "--port", str(PORT)],
                               cwd=root, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            for _ in range(150):
                try:
                    if httpx.get(base + "/api/health").status_code == 200:
                        break
                except httpx.HTTPError:
                    pass
                time.sleep(0.1)
            else:
                raise AssertionError(f"no server on {PORT}")
            db.DB_PATH = pathlib.Path(env["SATF_DB"])
            api = httpx.Client(base_url=base + "/api")

            # the fixtures: a live mock, a finished drill miss, four sets and one report
            m, d, o, v = fresh("wm"), fresh("wd"), named(fresh("wo"), "Maya"), fresh("wv")
            live, lq = sitting(m, "circle.convert", 41, kind="mock", finished=False)
            db.run("UPDATE sessions SET answers=? WHERE id=?", json.dumps({lq["id"]: 0}), live)
            drill_sid, dq = sitting(d, "circle.convert", 40, given=wrong(reports._from_bank("circle.convert", 40)))
            q = reports._from_bank("circle.convert", 42)
            sitting(o, "circle.convert", 42, given=pick(q, False))
            new = lambda body: api.post("/sets", headers=hdr(o), json=body).json()["code"]  # noqa: E731
            words = new({"kind": "words", "items": ["mitigate", "bolster"]})
            items = new({"kind": "items", "items": [["circle.convert", 42]], "cfg": {"context": True}})
            practice_set = new({"kind": "set", "items": [["circle.convert", 42]]})
            gone = new({"kind": "items", "items": [["circle.convert", 42]], "title": "stopped"})
            assert api.delete(f"/sets/{gone}", headers=hdr(o)).status_code == 200
            rid = api.post("/report", headers=hdr(d), data={"data": json.dumps(
                {"kind": "page", "category": "idea", "title": "a browser report"})}).json()["id"]

            errors: list[str] = []
            with sync_playwright() as p:
                b = p.chromium.launch(executable_path=CHROME)

                def page_as(learner: str):
                    ctx = b.new_context(viewport={"width": 1280, "height": 900})
                    ctx.add_init_script(f"localStorage.setItem('satf.learner', {json.dumps(learner)})")
                    pg = ctx.new_page()
                    pg.on("pageerror", lambda e: errors.append(f"{pg.url}: {e}"))
                    return pg

                def modal(learner: str, rctx: dict):
                    pg = page_as(learner)
                    pg.goto(base + "/s/")
                    pg.add_script_tag(url="/assets/report.js")
                    pg.evaluate("c => { UI.report(c); }", rctx)
                    pg.wait_for_selector("dialog.rp .rp-box:not([aria-hidden])")
                    return pg.inner_text("dialog.rp .rp-box"), pg.inner_text("dialog.rp")

                # Shell 15 / X10: in the test window the box shows no marking, and "Remind me" comes first
                box, sheet = modal(m, {"source": "test", "session": live, "question_id": lq["id"]})
                assert "marked" not in box.lower(), box
                assert "Remind me after" in sheet and "Answer key is wrong" not in sheet, sheet
                assert "The clock keeps running" in sheet, sheet
                # after the verdict it does, and the key can be disputed
                box, sheet = modal(d, {"source": "drill", "session": drill_sid, "question_id": dq["id"]})
                assert "marked wrong" in box and "circle.convert" in box and "Answer key is wrong" in sheet, box

                # Send feedback the way the shell calls it (a path as the source) is a page report
                box, sheet = modal(v, {"kind": "page", "source": "/plan/?x=1"})
                assert "/s/" in box and "Send feedback" in sheet and "Bug" in sheet, (box, sheet)

                # W20: the landing lists both words
                pg = page_as(v)
                pg.goto(f"{base}/s/?c={words}")
                pg.wait_for_selector("text=bolster")
                assert "mitigate" in pg.inner_text("body")
                # V17: a help link hides the question's answers and the sharer's pick until the visitor answers
                pg.goto(f"{base}/s/?c={items}")
                pg.wait_for_selector("text=Try it")
                text = pg.inner_text("body")
                assert q["reasons"][pick(q, False)] not in text and q["rationale"][:40] not in text, text[:400]
                # ... then Try it serves it here, and answering it shows what Maya picked
                pg.get_by_role("button", name="Try it", exact=True).click()
                pg.click(f"button.opt[data-i='{pick(q, True)}']")
                pg.wait_for_selector("text=What Maya did")
                assert f"Maya picked {'ABCD'[pick(q, False)]}" in pg.inner_text("body")
                assert api.get(f"/sets/{items}").json()["tried"] == 1
                # R18(c): a practice set forwards to Practice's banner; a stopped link says so
                pg.goto(f"{base}/s/?c={practice_set}")
                pg.wait_for_url(f"**/practice/?share={practice_set}")
                pg.goto(f"{base}/s/?c={gone}")
                pg.wait_for_selector("text=Whoever shared this has stopped sharing it.")

                # §10: the admin asks for the token once, then lists the report
                pg = page_as(v)
                pg.goto(base + "/admin/reports/")
                pg.fill("input[type=password]", "f6-admin")
                pg.keyboard.press("Enter")
                pg.wait_for_selector(f"text=#{rid}")
                assert pg.evaluate("sessionStorage.length") >= 1
                b.close()
            real = [e for e in errors if "/practice/" not in e]      # Practice's page is S4's
            assert not real, real
            print("ok  F6 pages: no marking in a live report, the /s/ landing, forwards, stopped links, the admin")
        finally:
            srv.terminate()
            srv.wait(10)


if __name__ == "__main__":
    import sys
    os.environ.pop("SATF_SMTP_HOST", None)
    with tempfile.TemporaryDirectory(prefix="satf-f6db-") as path:
        db.DB_PATH = pathlib.Path(path) / "f6-check.db"
        mail.OUTBOX = pathlib.Path(path) / "outbox"
        if "--browser" in sys.argv:
            browser()
        else:
            with TestClient(app) as client:
                check(client)
