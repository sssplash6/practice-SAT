"""F6 acceptance: reports (R17, Shell §2.10 and §10, U3, V6, X10, SR19).
Run alone with PYTHONPATH=. python3 server/checks/f6.py, or inside test_flow."""

from __future__ import annotations

import json
import os
import pathlib
import tempfile
from unittest.mock import patch

from fastapi.testclient import TestClient

from server import db, deps, mail, progress, reports
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

    # files: 11 -> 400, 11 MB PNG -> 413, a GIF -> 200 on disk, zip -> 415, 51 MB GIF -> 413 at 50 MB
    b = fresh("files")
    base = {"kind": "page", "category": "display", "page": "/"}
    post(c, b, base, [(f"{i}.png", PNG, "image/png") for i in range(11)], code=400)
    big = post(c, b, base, [("big.png", PNG + b"\0" * (11 * MB), "image/png")], code=413)
    assert big["detail"] == {"file": "big.png", "limit": 10 * MB}, big
    post(c, b, base, [("a.zip", ZIP, "application/zip")], code=415)
    post(c, b, base, [("fake.png", ZIP, "image/png")], code=415)            # the bytes decide, not the label
    huge = post(c, b, base, [("huge.gif", GIF + b"\0" * (51 * MB), "image/gif")], code=413)
    assert huge["detail"]["limit"] == 50 * MB
    ok = post(c, b, base, [("g.gif", GIF + b"\0" * (12 * MB), "image/gif"), ("r.webm", WEBM, "video/webm")])
    files = json.loads(db.one("SELECT files FROM reports WHERE id=?", ok["id"])["files"])
    assert [f["type"] for f in files] == ["image/gif", "video/webm"]
    assert (reports.FILES / str(ok["id"]) / "1.gif").stat().st_size == len(GIF) + 12 * MB
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
    print("ok  F6 reports: context resolved on the server for drill, qotd, challenge and a live mock")


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
            break
        got = post(c, d, body)
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
        finally:
            reports.FILES = keep
            os.environ.pop("SATF_ADMIN_TOKEN", None)


if __name__ == "__main__":
    os.environ.pop("SATF_SMTP_HOST", None)
    with tempfile.TemporaryDirectory(prefix="satf-f6db-") as path:
        db.DB_PATH = pathlib.Path(path) / "f6-check.db"
        mail.OUTBOX = pathlib.Path(path) / "outbox"
        with TestClient(app) as client:
            check(client)
