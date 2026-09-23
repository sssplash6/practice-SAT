"""The one check the serving layer has to keep passing.

    PYTHONPATH=. python3 server/test_flow.py

Walks a student through the whole thing against a scratch database: start,
answer, finish, signup, verify, results. What it is really guarding is the
answer key -- that it never appears in anything a student can fetch before
they have submitted -- plus the gates that stop results being read early and
the blueprint that makes a form a diagnostic rather than twenty questions.
"""

from __future__ import annotations

import json
import os
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

# point the store at a scratch file before anything imports it
_tmp = tempfile.TemporaryDirectory()
from server import db                                        # noqa: E402

db.DB_PATH = pathlib.Path(_tmp.name) / "test.db"
os.environ.pop("SATF_SMTP_HOST", None)                       # mail goes to the outbox

from fastapi.testclient import TestClient                    # noqa: E402

from server import mail, practice, progress, scoring         # noqa: E402
from server.app import app                                   # noqa: E402

mail.OUTBOX = pathlib.Path(_tmp.name) / "outbox"

DOMAINS = ("Algebra", "Advanced Math",
           "Problem-Solving and Data Analysis", "Geometry and Trigonometry")
LEAKS = ("answer", "rationale", "reasons", "distractor_reasons", "key", "seed")


def main() -> int:
    with TestClient(app) as c:
        # --- every form is a diagnostic, not just twenty questions -----------
        from server.app import FORMS
        assert len(FORMS) == 10, f"{len(FORMS)} forms"
        seen_stems = set()
        for fid, qs in FORMS.items():
            assert len(qs) == 20, f"form {fid} has {len(qs)}"
            for d in DOMAINS:
                tiers = sorted(q["difficulty"] for q in qs if q["domain"] == d)
                assert tiers == ["easy", "hard", "hard", "medium", "medium"], \
                    f"form {fid} {d}: {tiers}"
            # a module runs easiest to hardest, as the real one does
            rank = {"easy": 0, "medium": 1, "hard": 2}
            order = [rank[q["difficulty"]] for q in qs]
            assert order == sorted(order), f"form {fid} is out of order"
            for q in qs:
                assert q["stem"] not in seen_stems, f"form {fid} repeats a stem"
                seen_stems.add(q["stem"])
        print(f"ok  {len(FORMS)} forms, 4 domains x (1 easy, 2 medium, 2 hard), "
              f"{len(seen_stems)} distinct questions")

        # --- starting ---------------------------------------------------------
        s = c.post("/api/session").json()
        sid, qs = s["id"], s["questions"]
        # the clock counts from the start time, so a fresh one is at or just under
        assert len(qs) == 20
        full = 20 * 95
        assert full - 20 <= s["seconds"] <= full, s["seconds"]
        assert c.get(f"/api/session/{sid}").json()["seconds"] <= s["seconds"], \
            "the clock reset on reload"

        for q in qs:
            for bad in LEAKS:
                assert bad not in q, f"{bad} leaked in the question payload"
        assert s["answers"] == {}, "a fresh session is not blank"

        # the strong form: no rationale text reaches the wire, and nothing in
        # the payload would tell a reader which option is keyed
        from server.app import FORMS as _F
        blob = json.dumps(s, ensure_ascii=False)
        for q in _F[s["form"]]:
            assert q["rationale"] not in blob, f"{q['id']} shipped its rationale"
            for reason in q["reasons"]:
                assert not reason or reason not in blob, f"{q['id']} shipped a distractor reason"
        print("ok  session starts with no key, rationale or reason in the payload")

        # --- the gates --------------------------------------------------------
        assert c.get(f"/api/session/{sid}/results").status_code == 409, "results before finishing"
        assert c.post(f"/api/session/{sid}/answer",
                      json={"question_id": "nope", "answer": 0}).status_code == 400
        assert c.get("/api/session/does-not-exist").status_code == 404
        print("ok  results refused before finishing, unknown ids refused")

        # --- answering, every one right --------------------------------------
        form = FORMS[s["form"]]
        for q in form:
            right = "ABCD".index(q["answer"]) if q["type"] == "mcq" else q["answer"]
            r = c.post(f"/api/session/{sid}/answer",
                       json={"question_id": q["id"], "answer": right})
            assert r.status_code == 200, r.text

        # one is cleared again, to check a blank round-trips
        c.post(f"/api/session/{sid}/answer", json={"question_id": form[0]["id"], "answer": None})
        assert c.get(f"/api/session/{sid}").json()["answers"].get(form[0]["id"]) is None
        c.post(f"/api/session/{sid}/answer",
               json={"question_id": form[0]["id"],
                     "answer": "ABCD".index(form[0]["answer"]) if form[0]["type"] == "mcq"
                               else form[0]["answer"]})
        print("ok  answers save, clear and come back")

        # --- finishing --------------------------------------------------------
        done = c.post(f"/api/session/{sid}/finish").json()
        assert done["right"] == 20, f"a perfect paper marked {done['right']}/20"
        assert c.post(f"/api/session/{sid}/answer",
                      json={"question_id": form[1]["id"], "answer": 0}).status_code == 409
        print("ok  a perfect paper marks 20/20, and the test then closes")

        # --- signup ------------------------------------------------------------
        assert c.get(f"/api/session/{sid}/results").status_code == 403, "results before signup"
        assert c.post(f"/api/session/{sid}/signup",
                      json={"first": "Ada", "last": "L", "email": "nope"}).status_code == 422
        up = c.post(f"/api/session/{sid}/signup",
                    json={"first": "Ada", "last": "Lovelace",
                          "email": "Ada@Example.com"}).json()
        assert up["ok"] and up["verified"] is False
        assert up["email"] == "outbox", "no SMTP is configured, so it must say so"
        assert list(mail.OUTBOX.glob("*.eml")), "nothing was written to the outbox"
        print("ok  signup gates the results, and the unsent mail lands in the outbox")

        # --- verifying ----------------------------------------------------------
        row = db.one("SELECT id, token FROM users WHERE email=?", "ada@example.com")
        assert row is not None, "the email was not lower-cased"
        assert c.get("/api/verify", params={"token": row["token"]},
                     follow_redirects=False).headers["location"].endswith("state=ok")
        assert c.get("/api/verify", params={"token": row["token"]},
                     follow_redirects=False).headers["location"].endswith("state=bad"), \
            "the token is single use"
        print("ok  the link verifies once and not twice")

        # --- results -------------------------------------------------------------
        res = c.get(f"/api/session/{sid}/results").json()
        assert res["right"] == 20 and res["verified"] is True
        assert [d["domain"] for d in res["domains"]] == list(DOMAINS)
        assert all(d["band"] == "Strong" and d["focus"] == [] for d in res["domains"])
        lo, hi = res["estimate"]["low"], res["estimate"]["high"]
        assert hi - lo >= 100 and 200 <= lo < hi <= 800, f"band {lo}-{hi}"
        assert len(res["review"]) == 20 and res["review"][0]["rationale"]
        print(f"ok  results release after signup: Math {lo}-{hi}, every domain Strong")

        # --- mixed practice ------------------------------------------------
        # the point of the scheduler: sixty from one topic, and it must not
        # read as the same question sixty times
        r = c.post("/api/practice",
                   json={"basket": {"probability": 60}, "learner": "u:check"})
        assert r.status_code == 200, r.text
        first = r.json()
        qs = first["questions"]
        assert len(qs) == 60, len(qs)
        assert first["seconds"] is None, "practice is not on a clock"
        assert first["mode"] == "practice"

        for q in qs:
            for bad in LEAKS:
                assert bad not in q, f"{bad} leaked from a practice set"
        assert len({q["stem"] for q in qs}) == 60, "a stem repeated inside one set"

        # no feature that carries the feel of a question may run back to back
        from server import practice as sched
        feats = [sched.opening(q["stem"]) for q in qs]
        assert all(a != b for a, b in zip(feats, feats[1:])), "two neighbours share an opening"

        stored = json.loads(db.one("SELECT questions FROM sessions WHERE id=?",
                                   first["id"])["questions"])
        keys = [q["key"] for q in stored]
        assert all(a != b for a, b in zip(keys, keys[1:])), "a template ran twice over"
        assert len(set(keys)) == len(sched.catalogue()["by_topic"]["probability"]), \
            "the set leaned on a subset of the topic's templates"
        print(f"ok  60 from one topic: 60 distinct stems, all "
              f"{len(set(keys))} templates used, no feature repeats back to back")

        # a second sitting is not the first one again
        again = c.post("/api/practice",
                       json={"basket": {"probability": 60}, "learner": "u:check"}).json()
        overlap = {q["stem"] for q in qs} & {q["stem"] for q in again["questions"]}
        assert not overlap, f"{len(overlap)} questions came back on the second sitting"
        print("ok  a second sitting repeats none of the first")

        # topics interleave rather than arriving in blocks
        mixed = c.post("/api/practice",
                       json={"basket": {"circles": 4, "percentages": 4, "probability": 4},
                             "learner": "u:check2"}).json()["questions"]
        names = [q["topic_name"] for q in mixed]
        assert all(a != b for a, b in zip(names, names[1:])), f"topics blocked: {names}"
        print("ok  three topics interleave, never two of the same in a row")

        for label, body, want in [
            ("unknown topic", {"basket": {"nope": 3}}, 400),
            ("empty basket", {"basket": {}}, 400),
            ("over the cap", {"basket": {"circles": 500}}, 400),
        ]:
            got = c.post("/api/practice", json=body).status_code
            assert got == want, f"{label}: {got}"

        # practice results need no signup: you chose these questions
        pid = mixed and c.post("/api/practice",
                               json={"basket": {"circles": 3}, "learner": "u:check2"}).json()
        for q in pid["questions"]:
            c.post(f"/api/session/{pid['id']}/answer", json={"question_id": q["id"], "answer": 0})
        c.post(f"/api/session/{pid['id']}/finish")
        res = c.get(f"/api/session/{pid['id']}/results")
        assert res.status_code == 200, "practice results were gated behind signup"
        assert res.json()["mode"] == "practice"
        print("ok  practice guards hold, and its results need no signup")

        # --- mocks, and the adaptive second module --------------------------
        from server.app import MOCKS
        assert len(MOCKS) == 7, f"{len(MOCKS)} mocks"

        DOM_TOTAL = {"Algebra": 15, "Advanced Math": 15,
                     "Problem-Solving and Data Analysis": 7,
                     "Geometry and Trigonometry": 7}
        for mid, m in MOCKS.items():
            for form in ("module1", "module2_lower", "module2_upper"):
                qs = m[form]
                assert len(qs) == 22, f"{mid} {form}: {len(qs)}"
                rank = {"easy": 0, "medium": 1, "hard": 2}
                order = [rank[q["difficulty"]] for q in qs]
                assert order == sorted(order), f"{mid} {form} is not easiest first"
                # College Board's own answer keys put the grid-ins here
                at = tuple(i for i, q in enumerate(qs, 1) if q["type"] == "spr")
                assert at == (6, 7, 13, 14, 21, 22), f"{mid} {form}: grid-in at {at}"
            both = m["module1"] + m["module2_upper"]
            got = {d: sum(1 for q in both if q["domain"] == d) for d in DOM_TOTAL}
            assert got == DOM_TOTAL, f"{mid} section domains: {got}"
            # the two second modules must actually differ, or it is not adaptive
            lo = {q["stem"] for q in m["module2_lower"]}
            up = {q["stem"] for q in m["module2_upper"]}
            assert not (lo & up), f"{mid}: the two second modules share questions"
            hard_lo = sum(1 for q in m["module2_lower"] if q["difficulty"] == "hard")
            hard_up = sum(1 for q in m["module2_upper"] if q["difficulty"] == "hard")
            assert hard_up > hard_lo, f"{mid}: the upper module is not harder"
        print("ok  7 mocks at 15/15/7/7, easiest first, grid-in at 6/7/13/14/21/22, "
              "two distinct second modules")

        def sit(mock, m1_right):
            """Sit a mock, getting the first m1_right of module 1 correct."""
            st = c.post(f"/api/mock/{mock}", json={"learner": "u:mocks"}).json()
            sid = st["id"]
            assert st["seconds"] > 2000, "a module is 35 minutes"
            keyed = {q["id"]: q for f in ("module1", "module2_lower", "module2_upper")
                     for q in MOCKS[mock][f]}
            def reply(qs, upto):
                for i, q in enumerate(qs):
                    k = keyed[q["id"]]
                    right = "ABCD".index(k["answer"]) if k["type"] == "mcq" else k["answer"]
                    wrong = ("ABCD".index(k["answer"]) + 1) % 4 if k["type"] == "mcq" else "0"
                    c.post(f"/api/session/{sid}/answer",
                           json={"question_id": q["id"],
                                 "answer": right if i < upto else wrong})
            reply(st["questions"], m1_right)
            gate = c.post(f"/api/session/{sid}/finish").json()
            assert gate["next_module"] == 2, "module 1 finished the whole test"
            two = c.get(f"/api/session/{sid}").json()
            assert two["module"] == 2 and len(two["questions"]) == 22
            assert two["seconds"] > 2000, "module 2 did not get its own clock"
            reply(two["questions"], 22)
            c.post(f"/api/session/{sid}/finish")
            return gate, c.get(f"/api/session/{sid}/results").json()

        gate, res = sit("1.1", 22)
        assert res["estimate"]["route"] == "upper", res["estimate"]
        assert res["right"] == 44 and not res["estimate"]["capped"]
        top = res["estimate"]["high"]

        gate, res = sit("1.2", 8)
        assert res["estimate"]["route"] == "lower", res["estimate"]
        assert res["estimate"]["capped"], "a low route has no ceiling"
        assert res["estimate"]["high"] <= 580, res["estimate"]
        print(f"ok  routing is adaptive: a strong module 1 reaches {top}, "
              f"a weak one is capped at {res['estimate']['high']}")

        # answering 22/22 on the lower module 2 still cannot reach the top
        assert res["estimate"]["high"] < top, "the route made no difference"
        print("ok  a perfect lower module 2 still scores under a strong route")

        check_learner(c)
        check_integrity(c)

    # --- the marking itself, away from the wire -------------------------------
    assert scoring.is_correct({"type": "spr", "answer": "5776"}, "5,776")
    assert scoring.is_correct({"type": "mcq", "answer": "C"}, 2)
    assert not scoring.is_correct({"type": "mcq", "answer": "C"}, None)
    assert not scoring.is_correct({"type": "mcq", "answer": "C"}, "C")      # index, not letter
    assert not scoring.is_correct({"type": "spr", "answer": "12"}, "")
    print("ok  marking: commas ignored, blanks wrong, a letter is not an index")

    # a grid-in is the same number written any acceptable way, per the SAT's
    # own directions -- including a long decimal cut or rounded at the fourth digit
    for given, key, want in [
        ("0.125", "1/8", True), ("1/8", "0.125", True), ("2/4", "1/2", True),
        ("−8", "-8", True), ("-8", "−8", True), ("1,208", "1208", True),
        (".6666", "2/3", True), (".6667", "2/3", True), ("0.666", "2/3", True),
        ("0.667", "2/3", True), ("-.6666", "-2/3", True), ("45.12", "45.125", True),
        ("45.13", "45.125", True),
        ("0.66", "2/3", False), (".67", "2/3", False), ("22.6", "22.68", False),
        ("0.668", "2/3", False), ("7/2", "3.4", False), ("x", "12", False), ("12", "-12", False),
    ]:
        got = scoring.grid_equal(given, key)
        assert got is want, f"grid-in {given!r} against {key!r}: {got}, wanted {want}"
    print("ok  grid-ins: equivalent forms count, the fourth-digit rule holds, short cuts do not")

    print("\nall good")
    return 0


def stored(sid: str) -> list[dict]:
    """A drill's served questions as the server keeps them, key included."""
    return json.loads(db.one("SELECT questions FROM sessions WHERE id=?", sid)["questions"])


def keyed_answer(q: dict, right: bool):
    if q["type"] == "mcq":
        k = "ABCD".index(q["answer"])
        if right:
            return k
        # a wrong option that names its mistake, so the trap has a label
        return next(i for i in range(4) if i != k and q["reasons"][i])
    return q["answer"] if right else "-99999"


def check_learner(c) -> None:
    """The rebuild's half: drills, mistakes, the map, the coach, fresh sections."""
    H = {"X-Learner": "a:flowcheck01"}

    # --- identity is required and checked for shape ----------------------------
    assert c.get("/api/map").status_code == 400, "a map with no learner"
    assert c.get("/api/map", headers={"X-Learner": "<script>"}).status_code == 400
    blank = c.get("/api/map", headers=H).json()
    assert len(blank["topics"]) == 19, len(blank["topics"])
    assert all(t["mastery"] == 0 and not t["traps"] for t in blank["topics"])
    assert len(blank["coach"]["topics"]) == 3 and blank["coach"]["why"] == "new"
    print("ok  a new learner has 19 empty topics and a coach pick of 3")

    # --- a drill: one question at a time, nothing given away ---------------------
    d = c.post("/api/drill", headers=H,
               json={"topics": ["percentages"], "count": 3}).json()
    sid, q = d["id"], d["question"]
    assert d["total"] == 3 and d["mode"] == "drill"
    for bad in LEAKS:
        assert bad not in q, f"{bad} leaked from a drill question"
    first = stored(sid)[0]
    assert first["rationale"] not in json.dumps(d, ensure_ascii=False)

    # wrong: the mistake is named, the key shown, and the set grows by one
    fb = c.post(f"/api/drill/{sid}/answer", headers=H,
                json={"question_id": q["id"], "answer": keyed_answer(first, False), "ms": 4000}).json()
    assert fb["correct"] is False and fb["answer"] == first["answer"]
    assert fb["rationale"] == first["rationale"]
    if first["type"] == "mcq":
        assert fb["mistake"] and fb["mistake"][0].isupper(), fb
    assert fb["total"] == 4, "a miss did not add its repair"
    assert fb["opened"], "a miss opened no mistake"

    # the repair is the same template on a fresh seed
    nx = c.post(f"/api/drill/{sid}/next", headers=H).json()
    again = stored(sid)[1]
    assert nx["question"]["repair"] is True
    assert again["key"] == first["key"] and again["seed"] != first["seed"]
    assert again["stem"] != first["stem"]
    print("ok  a miss names the mistake, shows the key, and the same trap comes back fresh")

    trap_map = {t["topic"]: t for t in c.get("/api/map", headers=H).json()["topics"]}
    assert trap_map["percentages"]["traps"], "the map does not show the open mistake"
    coach = c.get("/api/map", headers=H).json()["coach"]
    assert "percentages" in coach["topics"] and coach["why"] == "mistakes", coach

    # two clean answers on that template close it
    c.post(f"/api/drill/{sid}/answer", headers=H,
           json={"question_id": nx["question"]["id"], "answer": keyed_answer(again, True)})
    m = c.get("/api/mistakes", headers=H).json()
    assert m["traps"] and m["traps"][0]["owed"] == 1
    fix = c.post("/api/drill", headers=H, json={"mistakes": True}).json()
    assert fix["total"] == 2
    for _ in range(2):
        cur = stored(fix["id"])[-1]
        c.post(f"/api/drill/{fix['id']}/answer", headers=H,
               json={"question_id": cur["id"], "answer": keyed_answer(cur, True)})
        c.post(f"/api/drill/{fix['id']}/next", headers=H)
    assert not c.get("/api/mistakes", headers=H).json()["traps"], "two clean answers did not close it"
    print("ok  the map and coach point at the open mistake, and two clean answers close it")

    # finishing reports the topics moved and what was closed
    for _ in range(3):
        nx = c.post(f"/api/drill/{sid}/next", headers=H).json()
        if nx.get("done"):
            break
        cur = stored(sid)[-1]
        c.post(f"/api/drill/{sid}/answer", headers=H,
               json={"question_id": cur["id"], "answer": keyed_answer(cur, True)})
    assert c.post(f"/api/drill/{sid}/next", headers=H).json().get("done"), "the set did not end at 4"
    summary = c.post(f"/api/drill/{sid}/finish", headers=H).json()
    pct = next(t for t in summary["topics"] if t["topic"] == "percentages")
    assert pct["asked"] == 4 and pct["right"] == 3 and pct["after"] > pct["before"], pct
    assert summary["next"]["topics"], "no next session after finishing"
    assert c.post(f"/api/drill/{sid}/answer", headers=H,
                  json={"question_id": "d001", "answer": 0}).status_code == 409
    other = {"X-Learner": "a:someoneelse"}
    assert c.get(f"/api/drill/{sid}", headers=other).status_code == 403
    print("ok  finishing moves the topic up, suggests the next set, and closes the drill")

    # --- endless: it never runs out, and never repeats --------------------------
    e = c.post("/api/drill", headers=H, json={"topics": ["circles", "probability"], "count": None}).json()
    assert e["total"] is None
    stems = set()
    for _ in range(30):
        cur = stored(e["id"])[-1]
        stems.add(cur["stem"])
        c.post(f"/api/drill/{e['id']}/answer", headers=H,
               json={"question_id": cur["id"], "answer": keyed_answer(cur, True)})
        nx = c.post(f"/api/drill/{e['id']}/next", headers=H).json()
        assert "question" in nx, nx
    assert len(stems) == 30, "an endless set repeated itself"
    served = stored(e["id"])
    topics_seen = [q["topic"] for q in served]
    assert set(topics_seen) == {"circles", "probability"}
    print("ok  an endless set serves 30 distinct questions across its topics and keeps going")

    # difficulty is honoured
    hard = c.post("/api/drill", headers=H,
                  json={"topics": ["linear_functions"], "count": 5, "difficulty": ["hard"]}).json()
    for _ in range(5):
        cur = stored(hard["id"])[-1]
        assert cur["difficulty"] == "hard", cur["difficulty"]
        c.post(f"/api/drill/{hard['id']}/answer", headers=H,
               json={"question_id": cur["id"], "answer": keyed_answer(cur, True)})
        if c.post(f"/api/drill/{hard['id']}/next", headers=H).json().get("done"):
            break
    print("ok  a hard-only set serves only hard questions")

    # --- saved questions come back exactly --------------------------------------
    keep = stored(e["id"])[3]
    assert c.post("/api/saved", headers=H,
                  json={"session": e["id"], "question_id": keep["id"]}).json()["saved"]
    back = c.post("/api/drill", headers=H, json={"saved": True}).json()
    assert stored(back["id"])[0]["stem"] == keep["stem"], "a saved question came back different"
    print("ok  a saved question is served again exactly")

    # --- the profile ---------------------------------------------------------------
    assert c.put("/api/me", headers=H, json={"target": 755}).status_code == 422
    assert c.put("/api/me", headers=H, json={"days": "1111"}).status_code == 422
    me = c.put("/api/me", headers=H, json={"name": "Ada", "exam_date": "2026-12-05",
                                           "target": 700, "minutes": 30, "days": "1111100"}).json()
    assert me["profile"]["name"] == "Ada" and me["profile"]["minutes"] == 30
    today = c.get("/api/today", headers={**H, "X-Tz": "-300"}).json()
    assert today["exam"]["date"] == "2026-12-05" and today["coach"]["count"] == 19
    assert today["days"]["streak"] >= 1 and today["days"]["recent"][-1]["questions"] > 0
    print(f"ok  profile saves and validates; today has a streak of {today['days']['streak']}"
          f" and a {today['coach']['count']}-question coach set for 30 minutes")

    # --- a fresh section: built for the sitting, never repeated -------------------
    def sit_fresh(m1_right: int):
        st = c.post("/api/mock/new", headers=H, json={"full": True}).json()
        mid = st["id"]
        assert st["mode"] == "mock" and len(st["questions"]) == 22 and st["seconds"] > 2000
        for bad in LEAKS:
            assert all(bad not in q for q in st["questions"]), f"{bad} leaked from a fresh section"
        kept = json.loads(db.one("SELECT questions FROM sessions WHERE id=?", mid)["questions"])
        m1 = kept["module1"]
        rank = {"easy": 0, "medium": 1, "hard": 2}
        assert [rank[q["difficulty"]] for q in m1] == sorted(rank[q["difficulty"]] for q in m1)
        at = tuple(i for i, q in enumerate(m1, 1) if q["type"] == "spr")
        assert at == (6, 7, 13, 14, 21, 22), f"fresh module 1 grid-ins at {at}"
        for i, q in enumerate(m1):
            c.post(f"/api/session/{mid}/answer",
                   json={"question_id": q["id"], "answer": keyed_answer(q, i < m1_right)})
        gate = c.post(f"/api/session/{mid}/finish").json()
        assert gate["next_module"] == 2
        two = c.get(f"/api/session/{mid}").json()
        kept = json.loads(db.one("SELECT questions FROM sessions WHERE id=?", mid)["questions"])
        m2 = kept["module2"]
        assert len(two["questions"]) == 22 and len(m2) == 22
        for q in m2:
            c.post(f"/api/session/{mid}/answer",
                   json={"question_id": q["id"], "answer": keyed_answer(q, False)})
        c.post(f"/api/session/{mid}/finish")
        res = c.get(f"/api/session/{mid}/results").json()
        return mid, m1 + m2, res

    mid1, qs1, res1 = sit_fresh(20)
    assert res1["estimate"]["route"] == "upper" and res1["right"] == 20
    assert any(r["mistake"] for r in res1["review"]), "the review names no mistakes"
    mid2, qs2, res2 = sit_fresh(5)
    assert res2["estimate"]["route"] == "lower" and res2["estimate"]["high"] <= 580, res2["estimate"]
    shared = {q["stem"] for q in qs1} & {q["stem"] for q in qs2}
    assert not shared, f"two fresh sections shared {len(shared)} questions"
    print("ok  fresh sections are built to the blueprint, route, name mistakes, and share nothing")

    # the misses of a sitting become a repair set on the same templates
    fix = c.post("/api/drill", headers=H, json={"from_session": mid1}).json()
    assert fix["total"] == 44 - 20, fix["total"]
    missed_keys = [q["key"] for q in qs1[20:]]
    first_fix = stored(fix["id"])[0]
    assert first_fix["key"] == missed_keys[0] and first_fix["stem"] != qs1[20]["stem"]
    print(f"ok  'fix these' turns {fix['total']} misses into fresh questions on the same templates")

    # --- the question of the day: one question, everyone, one answer each --------
    qd = c.get("/api/qotd").json()
    for bad in LEAKS:
        assert bad not in qd["question"], f"{bad} leaked from the question of the day"
    from server import daily
    kq = daily.question(qd["day"])
    assert c.get("/api/qotd").json()["question"]["stem"] == qd["question"]["stem"], "it changed"
    wrong = keyed_answer(kq, False)
    got = c.post("/api/qotd", headers=H, json={"answer": wrong}).json()
    assert got["correct"] is False and got["mistake"] and got["crowd"]["answered"] == 1
    again = c.post("/api/qotd", headers=H, json={"answer": keyed_answer(kq, True)}).json()
    assert again["correct"] is False, "a second answer replaced the first"
    c.post("/api/qotd", headers={"X-Learner": "a:qotdother"}, json={"answer": keyed_answer(kq, True)})
    mine = c.get("/api/qotd", headers=H).json()["mine"]
    assert mine and mine["crowd"] == {"answered": 2, "right": 1}, mine
    print("ok  the question of the day is one question, one answer each, with the crowd's count")

    # --- the challenge: the same ten for everyone, ranked --------------------------
    def play(headers, right_upto):
        st = c.post("/api/challenge/start", headers=headers).json()
        sid = st["id"]
        assert st["total"] == 10 and st["mode"] == "challenge"
        for i in range(10):
            cur = stored(sid)[-1]
            fb = c.post(f"/api/drill/{sid}/answer", headers=headers,
                        json={"question_id": cur["id"], "answer": keyed_answer(cur, i < right_upto)}).json()
            assert fb["total"] == 10, "a challenge grew a repair"
            nx = c.post(f"/api/drill/{sid}/next", headers=headers).json()
            if nx.get("done"):
                break
        c.post(f"/api/drill/{sid}/finish", headers=headers)
        return sid

    a = play(H, 6)
    B = {"X-Learner": "a:challengeb"}
    b = play(B, 9)
    assert [q["stem"] for q in stored(a)] == [q["stem"] for q in stored(b)], "two students got different sets"
    again = c.post("/api/challenge/start", headers=H).json()
    assert again["id"] == a and again.get("done"), "a second start began a second sitting"
    board = c.get("/api/challenge/board", headers=H).json()
    assert board["players"] == 2 and board["entries"][0]["right"] == 9
    assert board["you"]["rank"] == 2 and board["you"]["name"] == "Ada"
    assert board["entries"][0]["name"].startswith("Student "), board["entries"][0]
    print("ok  the challenge is the same ten for everyone, one sitting each, ranked right then time")

    hist = c.get("/api/history", headers=H).json()["sessions"]
    kinds = {h["kind"] for h in hist}
    assert {"drill", "mock"} <= kinds, kinds
    today = c.get("/api/today", headers=H).json()
    assert today["score"]["kind"] == "mock" and today["tested"] is True
    assert c.get("/api/today", headers={"X-Learner": "a:nevertested"}).json()["tested"] is False
    print(f"ok  history lists {len(hist)} sittings; today carries the latest score and that a test is done")

    # --- a grid-in names no mistake, so it is filed under the bank's skill ---------
    D = {"X-Learner": "a:diaggrid"}
    s = c.post("/api/session", headers=D).json()
    grid = next(q for q in s["questions"] if q["type"] == "spr")
    c.post(f"/api/session/{s['id']}/answer", json={"question_id": grid["id"], "answer": "123456"})
    c.post(f"/api/session/{s['id']}/finish")
    form = json.loads(pathlib.Path("server/forms.json").read_text())["forms"]
    full = next(q for f in form for q in f["questions"] if q["id"] == grid["id"] and q["stem"] == grid["stem"])
    skill = practice.skill_of(full)
    [trap] = c.get("/api/mistakes", headers=D).json()["traps"]
    assert skill and "skill" not in full, "the stored forms carry no skill; this checks the lookup"
    assert trap["label"] == skill[:1].upper() + skill[1:] and trap["label"] != grid["topic_name"], trap
    print(f"ok  a diagnostic grid-in miss is filed as \"{trap['label']}\", not the topic")

    # --- missing everything still ends: one repair per question -------------------
    M = {"X-Learner": "a:missall"}
    d = c.post("/api/drill", headers=M, json={"topics": ["circles"], "count": 2}).json()
    for _ in range(6):
        cur = stored(d["id"])[-1]
        fb = c.post(f"/api/drill/{d['id']}/answer", headers=M,
                    json={"question_id": cur["id"], "answer": keyed_answer(cur, False)}).json()
        nx = c.post(f"/api/drill/{d['id']}/next", headers=M).json()
        if nx.get("done"):
            break
    assert nx.get("done") and fb["total"] == 4 and fb["answered"] == 4, (fb["total"], nx)
    print("ok  a set of 2 missed throughout ends after 4: each miss gets one repair, not a loop")

    # --- one device takes another's code, and keeps its own work too ---------------
    def miss(headers, topic):
        d = c.post("/api/drill", headers=headers, json={"topics": [topic], "count": 2}).json()
        q = stored(d["id"])[0]
        c.post(f"/api/drill/{d['id']}/answer", headers=headers,
               json={"question_id": q["id"], "answer": keyed_answer(q, False)})
        return q

    OLD, NEW = {"X-Learner": "a:carryold"}, {"X-Learner": "a:carrynew"}
    shared = miss(OLD, "circles")
    miss(OLD, "probability")
    c.put("/api/me", headers=OLD, json={"name": "Bo", "minutes": 45})
    c.put("/api/me", headers=NEW, json={"minutes": 20})
    # the same mistake, open under both codes
    progress.record("a:carrynew", None, shared, keyed_answer(shared, False))
    assert c.post("/api/me/carry", headers=NEW, json={"learner": "<script>"}).status_code == 400
    moved = c.post("/api/me/carry", headers=NEW, json={"learner": "a:carryold"}).json()["moved"]
    assert moved == 2, moved
    after = c.get("/api/me", headers=NEW).json()
    assert after["days"]["total"] == 3 and c.get("/api/me", headers=OLD).json()["days"]["total"] == 0
    assert after["profile"]["name"] == "Bo" and after["profile"]["minutes"] == 20, after["profile"]
    traps = c.get("/api/mistakes", headers=NEW).json()["traps"]
    topics = sorted(t["topic"] for t in traps)
    assert "probability" in topics and "circles" in topics, topics
    same = [t for t in traps if t["template"] == shared["key"]]
    assert len(same) == 1 and same[0]["hits"] == 2, same
    assert not c.get("/api/mistakes", headers=OLD).json()["traps"]
    print("ok  taking another device's code carries this one's answers, mistakes and profile over")


def at_once(*calls):
    """Run the calls from separate threads released together, as two taps or
    two retried requests arrive."""
    import threading
    gate = threading.Barrier(len(calls))
    out = [None] * len(calls)

    def run(i, fn):
        gate.wait()
        out[i] = fn()
    threads = [threading.Thread(target=run, args=(i, fn)) for i, fn in enumerate(calls)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    return out


def check_integrity(c) -> None:
    """What a determined student could do with the API, and what two requests
    at the same moment would do. Each of these was a reproduced defect."""
    from server import blueprint, daily

    # --- save cannot read a key: only practice sets, a challenge's once answered --
    S = {"X-Learner": "a:savecheck"}
    ch = c.post("/api/challenge/start", headers=S).json()
    cur = stored(ch["id"])[-1]
    body = {"session": ch["id"], "question_id": cur["id"], "on": True}
    assert c.post("/api/saved", headers=S, json=body).status_code == 409, "saved an unanswered challenge question"
    assert c.post("/api/saved", headers={"X-Learner": "a:someoneelse"}, json=body).status_code == 403
    mock = c.post("/api/mock/new", headers=S, json={"full": False}).json()
    assert c.post("/api/saved", headers=S, json={"session": mock["id"], "question_id": mock["questions"][0]["id"]}
                  ).status_code == 404, "saved a question off a live test"
    c.post(f"/api/drill/{ch['id']}/answer", headers=S, json={"question_id": cur["id"], "answer": keyed_answer(cur, True)})
    assert c.post("/api/saved", headers=S, json=body).json()["saved"] is True
    print("ok  save keeps only practice questions, a challenge's once answered, and only your own")

    # --- a practice set is not a paper, and a paper is not a practice set ---------
    assert c.post(f"/api/session/{ch['id']}/answer", json={"question_id": cur["id"], "answer": None}).status_code == 409
    assert c.post(f"/api/session/{ch['id']}/finish").status_code == 409
    assert c.get(f"/api/drill/{mock['id']}", headers=S).status_code == 404
    assert c.post(f"/api/drill/{mock['id']}/answer", headers=S,
                  json={"question_id": mock["questions"][0]["id"], "answer": 0}).status_code == 404
    print("ok  the test endpoints refuse a practice set and the drill endpoints refuse a test")

    # --- two answers to a test at once both land ---------------------------------
    q1, q2 = mock["questions"][0]["id"], mock["questions"][1]["id"]
    for _ in range(4):
        at_once(lambda: c.post(f"/api/session/{mock['id']}/answer", json={"question_id": q1, "answer": 1}),
                lambda: c.post(f"/api/session/{mock['id']}/answer", json={"question_id": q2, "answer": 2}))
        got = c.get(f"/api/session/{mock['id']}").json()["answers"]
        assert got.get(q1) == 1 and got.get(q2) == 2, got
    print("ok  two answers sent to a test at the same moment are both kept")

    # --- the same drill answer twice at once files once --------------------------
    D = {"X-Learner": "a:doubletap"}
    for _ in range(4):
        d = c.post("/api/drill", headers=D, json={"topics": ["circles"], "count": 3}).json()
        q = stored(d["id"])[0]
        one = {"question_id": q["id"], "answer": keyed_answer(q, False)}
        at_once(lambda: c.post(f"/api/drill/{d['id']}/answer", headers=D, json=one),
                lambda: c.post(f"/api/drill/{d['id']}/answer", headers=D, json=one))
        n = db.one("SELECT COUNT(*) n FROM attempts WHERE session=? AND qid=?", d["id"], q["id"])["n"]
        assert n == 1, f"one answer filed {n} times"
        assert c.post(f"/api/drill/{d['id']}/finish", headers=D).json()["asked"] == 1
    print("ok  the same answer sent twice at once is filed once")

    # --- one challenge sitting and one question-of-the-day answer, however many at once
    for i in range(4):
        L = {"X-Learner": f"a:twostarts{i}"}
        at_once(lambda: c.post("/api/challenge/start", headers=L), lambda: c.post("/api/challenge/start", headers=L))
        n = db.one("SELECT COUNT(*) n FROM sessions WHERE kind='challenge' AND learner=?", L["X-Learner"])["n"]
        assert n == 1, f"two starts made {n} sittings"
        at_once(lambda: c.post("/api/qotd", headers=L, json={"answer": 0}),
                lambda: c.post("/api/qotd", headers=L, json={"answer": 1}))
        n = db.one("SELECT COUNT(*) n FROM attempts WHERE learner=? AND session LIKE 'qotd:%'", L["X-Learner"])["n"]
        assert n == 1, f"the day's question was answered {n} times"
    print("ok  two starts make one challenge sitting, and two answers to the day's question file one")

    # --- a timed set's clock holds on the server ---------------------------------
    T = {"X-Learner": "a:overtime"}
    ch = c.post("/api/challenge/start", headers=T).json()
    db.run("UPDATE sessions SET started=? WHERE id=?", "2000-01-01T00:00:00+00:00", ch["id"])
    cur = stored(ch["id"])[-1]
    late = c.post(f"/api/drill/{ch['id']}/answer", headers=T, json={"question_id": cur["id"], "answer": 0})
    assert late.status_code == 409 and "time" in late.json()["detail"], late.text
    print("ok  a challenge answer after its clock ran out is refused")

    # --- the day's question is marked against the day it was shown ----------------
    Y = {"X-Learner": "a:yesterday"}
    shown = c.get("/api/qotd", headers=Y).json()["day"]
    assert c.post("/api/qotd", headers=Y, json={"answer": 0, "day": "2000-01-01"}).status_code == 409
    assert c.post("/api/qotd", headers=Y, json={"answer": 0, "day": shown}).status_code == 200
    print("ok  an answer to another day's question is refused rather than marked against today's")

    # --- a saved set still repairs each miss before its next saved question -------
    R = {"X-Learner": "a:savedrepair"}
    d = c.post("/api/drill", headers=R, json={"topics": ["percentages"], "count": 3}).json()
    for _ in range(3):
        cur = stored(d["id"])[-1]
        c.post("/api/saved", headers=R, json={"session": d["id"], "question_id": cur["id"], "on": True})
        c.post(f"/api/drill/{d['id']}/answer", headers=R, json={"question_id": cur["id"], "answer": keyed_answer(cur, True)})
        if c.post(f"/api/drill/{d['id']}/next", headers=R).json().get("done"):
            break
    again = c.post("/api/drill", headers=R, json={"saved": True}).json()
    first = stored(again["id"])[0]
    c.post(f"/api/drill/{again['id']}/answer", headers=R, json={"question_id": first["id"], "answer": keyed_answer(first, False)})
    c.post(f"/api/drill/{again['id']}/next", headers=R)
    second = stored(again["id"])[1]
    assert second["repair"] and second["key"] == first["key"], "a saved set served its next item before the repair"
    print("ok  in a saved set a miss is repaired before the next saved question")

    # --- inputs that crashed the server are refused --------------------------------
    B = {"X-Learner": "a:badinput"}
    assert c.put("/api/me", headers=B, json={"exam_date": "2026-02-30"}).status_code == 422
    assert c.get("/api/today", headers=B).status_code == 200
    assert c.get("/api/qotd", headers={**B, "X-Tz": "99999999999"}).status_code == 422
    assert c.get("/api/challenge", headers={**B, "X-Tz": "-9000"}).status_code == 422
    print("ok  an impossible exam date and an impossible timezone are refused, not a 500")

    # --- every domain has easy questions as well as hard ones ----------------------
    from collections import Counter
    for dom in blueprint.DOMAIN_SPLIT[1]:
        tiers = Counter(t for d, t, _ in blueprint.slots("module1", 1) if d == dom)
        assert tiers["easy"] and tiers["hard"], (dom, tiers)
    assert len({d for d, t in zip(blueprint.spread(dict(daily.MIX)), daily.LADDER) if t == "easy"}) == 3
    print("ok  module 1 gives every domain easy and hard questions, and the challenge spreads its easy ones")


if __name__ == "__main__":
    try:
        sys.exit(main())
    finally:
        _tmp.cleanup()
