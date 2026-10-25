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

# the flow's learners are anonymous codes: email-only access is off here and checked on its own (checks/email_only.py)
os.environ["SATF_EMAIL_ONLY"] = "0"
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
        from server.api_tests import FORM_IDS
        assert len(FORM_IDS["math"]) == 10 and len(FORMS) == 10 + len(FORM_IDS["rw"]), f"{len(FORMS)} forms"
        seen_stems = set()
        for fid in FORM_IDS["math"]:
            qs = FORMS[fid]
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
        print(f"ok  {len(FORM_IDS['math'])} Math forms, 4 domains x (1 easy, 2 medium, 2 hard), "
              f"{len(seen_stems)} distinct questions")
        # the R&W forms: the same shape over R&W's four domains, in Bluebook's order (domain by
        # domain, skill by skill, easiest to hardest inside each), no item on two forms
        from server import blueprint
        assert len(FORM_IDS["rw"]) >= 3 and all(fid > 100 for fid in FORM_IDS["rw"])
        rw_seen = set()
        for fid in FORM_IDS["rw"]:
            qs = FORMS[fid]
            assert len(qs) == 20 and all(q["type"] == "mcq" and q["text"] for q in qs), f"R&W form {fid}"
            for d in scoring.RW_DOMAINS:
                tiers = sorted(q["difficulty"] for q in qs if q["domain"] == d)
                assert tiers == ["easy", "hard", "hard", "medium", "medium"], f"R&W form {fid} {d}: {tiers}"
            rank = {"easy": 0, "medium": 1, "hard": 2}
            order = [(blueprint.RW_ORDER.index(q["topic"]), rank[q["difficulty"]]) for q in qs]
            assert order == sorted(order), f"R&W form {fid} is out of Bluebook's order"
            for q in qs:
                assert q["text"] + q["stem"] not in rw_seen, f"R&W form {fid} repeats an item"
                rw_seen.add(q["text"] + q["stem"])
        print(f"ok  {len(FORM_IDS['rw'])} R&W forms, 4 domains x (1 easy, 2 medium, 2 hard), Bluebook's order")

        # --- starting ---------------------------------------------------------
        s = c.post("/api/session").json()
        DH = {"X-Learner": s["learner"]}        # the server minted this code (SEC-07)
        s = c.post(f"/api/session/{s['id']}/begin", headers=DH).json()
        sid, qs = s["id"], s["questions"]
        # the clock counts from the start time, so a fresh one is at or just under
        assert len(qs) == 20
        full = 20 * 95
        assert full - 20 <= s["seconds"] <= full, s["seconds"]
        assert c.get(f"/api/session/{sid}", headers=DH).json()["seconds"] <= s["seconds"], \
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
        assert c.post(f"/api/session/{sid}/answer", headers=DH,
                      json={"question_id": "nope", "answer": 0}).status_code == 400
        assert c.get("/api/session/does-not-exist").status_code == 404
        print("ok  results refused before finishing, unknown ids refused")

        # --- answering, every one right --------------------------------------
        form = FORMS[s["form"]]
        for q in form:
            right = "ABCD".index(q["answer"]) if q["type"] == "mcq" else scoring.keys(q["answer"])[0]
            r = c.post(f"/api/session/{sid}/answer", headers=DH,
                       json={"question_id": q["id"], "answer": right})
            assert r.status_code == 200, r.text

        # one is cleared again, to check a blank round-trips
        c.post(f"/api/session/{sid}/answer", headers=DH, json={"question_id": form[0]["id"], "answer": None})
        assert c.get(f"/api/session/{sid}", headers=DH).json()["answers"].get(form[0]["id"]) is None
        c.post(f"/api/session/{sid}/answer", headers=DH,
               json={"question_id": form[0]["id"],
                     "answer": "ABCD".index(form[0]["answer"]) if form[0]["type"] == "mcq"
                               else form[0]["answer"]})
        print("ok  answers save, clear and come back")

        # --- finishing --------------------------------------------------------
        done = c.post(f"/api/session/{sid}/finish", headers=DH).json()
        assert done["right"] == 20, f"a perfect paper marked {done['right']}/20"
        assert c.post(f"/api/session/{sid}/answer", headers=DH,
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
        res = c.get(f"/api/session/{sid}/results", headers=DH).json()
        assert res["right"] == 20 and res["verified"] is True
        assert [d["domain"] for d in res["domains"]] == list(DOMAINS)
        assert all(d["band"] == "Strong" and d["focus"] == [] for d in res["domains"])
        lo, hi = res["estimate"]["low"], res["estimate"]["high"]
        assert hi - lo == 20 and 200 <= lo < hi <= 800, f"band {lo}-{hi}"     # the 20-point rule (scoring.band)
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
            c.post(f"/api/session/{pid['id']}/answer", headers={"X-Learner": "u:check2"},
                   json={"question_id": q["id"], "answer": 0})
        c.post(f"/api/session/{pid['id']}/finish", headers={"X-Learner": "u:check2"})
        res = c.get(f"/api/session/{pid['id']}/results", headers={"X-Learner": "u:check2"})
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
            MH = {"X-Learner": "u:mocks"}
            st = c.post(f"/api/mock/{mock}", json={"learner": "u:mocks"}).json()
            sid = st["id"]
            st = c.post(f"/api/session/{sid}/begin", headers=MH).json()
            assert st["seconds"] > 2000, "a module is 35 minutes"
            keyed = {q["id"]: q for f in ("module1", "module2_lower", "module2_upper")
                     for q in MOCKS[mock][f]}
            def reply(qs, upto):
                for i, q in enumerate(qs):
                    k = keyed[q["id"]]
                    right = "ABCD".index(k["answer"]) if k["type"] == "mcq" else scoring.keys(k["answer"])[0]
                    wrong = ("ABCD".index(k["answer"]) + 1) % 4 if k["type"] == "mcq" else "0"
                    c.post(f"/api/session/{sid}/answer", headers=MH,
                           json={"question_id": q["id"],
                                 "answer": right if i < upto else wrong})
            reply(st["questions"], m1_right)
            gate = c.post(f"/api/session/{sid}/finish", headers=MH).json()
            assert gate["next_module"] == 2, "module 1 finished the whole test"
            two = c.post(f"/api/session/{sid}/begin", headers=MH).json()
            assert two["module"] == 2 and len(two["questions"]) == 22
            assert two["seconds"] > 2000, "module 2 did not get its own clock"
            reply(two["questions"], 22)
            c.post(f"/api/session/{sid}/finish", headers=MH)
            return gate, c.get(f"/api/session/{sid}/results", headers=MH).json()

        gate, res = sit("1.1", 22)
        assert res["estimate"]["route"] == "upper", res["estimate"]
        assert res["right"] == 44 and not res["estimate"]["capped"]
        top = res["estimate"]["high"]

        gate, res = sit("1.2", 8)
        assert res["estimate"]["route"] == "lower", res["estimate"]
        # a 20-point band only meets the ceiling when its centre is near it; the rule is never above 580
        assert res["estimate"]["high"] <= 580, res["estimate"]
        assert res["estimate"]["capped"] or res["estimate"]["high"] < 580, res["estimate"]
        print(f"ok  routing is adaptive: a strong module 1 reaches {top}, "
              f"a weak one is capped at {res['estimate']['high']}")

        # answering 22/22 on the lower module 2 still cannot reach the top
        assert res["estimate"]["high"] < top, "the route made no difference"
        print("ok  a perfect lower module 2 still scores under a strong route")

        check_learner(c)
        check_rw(c)
        check_integrity(c)
        run_checks(c)

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
    return scoring.keys(q["answer"])[0] if right else "-99999"


def check_learner(c) -> None:
    """The rebuild's half: drills, mistakes, the map, the coach, fresh sections."""
    H = {"X-Learner": "a:flowcheck01"}
    global TOPIC_DOMAIN
    TOPIC_DOMAIN = {slug: t.domain for slug, t in practice.catalogue()["topics"].items()}

    # --- identity is required and checked for shape ----------------------------
    assert c.get("/api/map").status_code == 400, "a map with no learner"
    assert c.get("/api/map", headers={"X-Learner": "<script>"}).status_code == 400
    blank = c.get("/api/map", headers=H).json()
    assert len(blank["topics"]) == 19, len(blank["topics"])
    assert all(t["mastery"] == 0 and not t["traps"] for t in blank["topics"])
    # one answer is a sliver of the bar; a long clean run nearly fills it
    assert 0.05 < progress.mastery_of([("medium", 1)]) < 0.15
    assert progress.mastery_of([("medium", 1)] * 30) > 0.9
    assert progress.mastery_of([("medium", 0)] + [("medium", 1)] * 9) < progress.mastery_of([("medium", 1)] * 10)
    assert len(blank["coach"]["topics"]) == 3 and blank["coach"]["why"] == "new"
    ahead = blank["coach"]["ahead"]
    assert ahead[0] == blank["coach"]["topics"] and sorted(t for a in ahead for t in a) == sorted(t["topic"] for t in blank["topics"])
    assert all(max(__import__("collections").Counter(TOPIC_DOMAIN[t] for t in a).values()) <= 2 for a in ahead)
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
    # R45: a clean answer counts toward closing only when the item offered the same named trap.
    m = c.get("/api/mistakes", headers=H).json()
    assert m["traps"]
    trap = m["traps"][0]["norm"]
    # an unnamed trap (a grid-in miss naming nothing) closes on any clean answer to its template
    assert trap in progress.UNNAMED or trap in progress.offered_of(again)
    assert m["traps"][0]["owed"] == 1, (m["traps"][0], progress.offered_of(again))
    fix = c.post("/api/drill", headers=H, json={"mistakes": True}).json()
    assert fix["total"] == 2
    for _ in range(2):
        cur = stored(fix["id"])[-1]
        assert trap in progress.UNNAMED or trap in progress.offered_of(cur)
        c.post(f"/api/drill/{fix['id']}/answer", headers=H,
               json={"question_id": cur["id"], "answer": keyed_answer(cur, True)})
        c.post(f"/api/drill/{fix['id']}/next", headers=H)
    left = c.get("/api/mistakes", headers=H).json()["traps"]
    assert not left, "the repair and fix drill did not close the mistake"
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
        st = c.post(f"/api/session/{mid}/begin", headers=H).json()
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
            c.post(f"/api/session/{mid}/answer", headers=H,
                   json={"question_id": q["id"], "answer": keyed_answer(q, i < m1_right)})
        gate = c.post(f"/api/session/{mid}/finish", headers=H).json()
        assert gate["next_module"] == 2
        two = c.post(f"/api/session/{mid}/begin", headers=H).json()
        kept = json.loads(db.one("SELECT questions FROM sessions WHERE id=?", mid)["questions"])
        m2 = kept["module2"]
        assert len(two["questions"]) == 22 and len(m2) == 22
        for q in m2:
            c.post(f"/api/session/{mid}/answer", headers=H,
                   json={"question_id": q["id"], "answer": keyed_answer(q, False)})
        c.post(f"/api/session/{mid}/finish", headers=H)
        res = c.get(f"/api/session/{mid}/results", headers=H).json()
        return mid, m1 + m2, res

    mid1, qs1, res1 = sit_fresh(20)
    assert res1["estimate"]["route"] == "upper" and res1["right"] == 20
    # SR3 holds a miss's mistake back until its key is seen; reveal one first.
    # An mcq miss always picks a named wrong option (keyed_answer); a grid-in
    # miss is just "-99999" and may name no misconception.
    a_miss = next(r["id"] for r in res1["review"] if r["status"] != "correct" and r["type"] == "mcq")
    c.post(f"/api/session/{mid1}/seen", headers=H, json={"qids": [a_miss]})
    res1 = c.get(f"/api/session/{mid1}/results", headers=H).json()
    assert any(r.get("mistake") for r in res1["review"]), "the review names no mistakes"
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
    db.run("UPDATE learners SET created='2020-01-01' WHERE id='a:qotdother'")   # SEC-02: the crowd counts established codes
    mine = c.get("/api/qotd", headers=H).json()["mine"]
    assert mine and (mine["crowd"]["answered"], mine["crowd"]["right"]) == (2, 1), mine
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
    s = c.post(f"/api/session/{s['id']}/begin", headers=D).json()
    grid = next(q for q in s["questions"] if q["type"] == "spr")
    c.post(f"/api/session/{s['id']}/answer", headers=D, json={"question_id": grid["id"], "answer": "12345"})
    c.post(f"/api/session/{s['id']}/finish", headers=D)
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

    # --- a timed set runs on the minutes the student set, endless ones too ------------
    C = {"X-Learner": "a:ownclock"}
    assert c.post("/api/drill", headers=C, json={"topics": ["circles"], "count": 37, "timed": True}).json()["seconds"] == 37 * 95  # R34
    assert c.post("/api/drill", headers=C, json={"topics": ["circles"], "count": 37, "timed": True,
                                                "minutes": 3}).json()["seconds"] == 180
    sprint = c.post("/api/drill", headers=C, json={"topics": ["circles"], "count": None, "timed": True, "minutes": 5}).json()
    assert sprint["seconds"] == 300 and sprint["total"] is None
    assert c.post("/api/drill", headers=C, json={"topics": ["circles"], "count": 5, "minutes": 3}).json()["seconds"] is None
    for bad in (0, 181):
        assert c.post("/api/drill", headers=C, json={"topics": ["circles"], "timed": True, "minutes": bad}).status_code == 422
    print("ok  a set of any length can run on the student's own minutes, and an endless one becomes a sprint")

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


def check_rw(c) -> None:
    """Reading and Writing through the test kinds, and the full SAT (spec/full-sat/DESIGN.md section 2)."""
    import datetime as dt
    from collections import Counter

    from server import api_tests, blueprint
    H = {"X-Learner": "a:flowrw01"}

    def live(sid):
        return api_tests.questions_of(db.one("SELECT * FROM sessions WHERE id=?", sid))

    def module(sid, right):
        """Begin the live module and hand it in: the first `right` right, the rest wrong."""
        c.post(f"/api/session/{sid}/begin", headers=H)
        for i, q in enumerate(live(sid)):
            c.post(f"/api/session/{sid}/answer", headers=H, json={"question_id": q["id"], "answer": keyed_answer(q, i < right)})
        return c.post(f"/api/session/{sid}/finish", headers=H).json()

    # --- an R&W section: 27 + 27 in Bluebook's order, 32 minutes a module, routed ----------------
    st = c.post("/api/mock/new", headers=H, json={"kind": "section", "subject": "rw"}).json()
    sid = st["id"]
    assert st["subject"] == "rw" and st["duration"] == 32 * 60 and st["calculator"] is False, st
    assert [m["questions"] for m in st["modules"]] == [27, 27] and st["holds"]["grid_ins"] == 0
    m1 = live(sid)
    assert Counter(q["domain"] for q in m1) == Counter(blueprint.RW_DOMAIN_SPLIT[1])
    assert Counter(q["difficulty"] for q in m1) == blueprint.RW_TIERS["module1"]
    assert all(q["type"] == "mcq" and q["text"] for q in m1) and len({(q["key"], q["seed"]) for q in m1}) == 27
    rank = {"easy": 0, "medium": 1, "hard": 2}
    order = [(blueprint.RW_ORDER.index(q["topic"]), rank[q["difficulty"]]) for q in m1]
    assert order == sorted(order), "an R&W module runs skill by skill, easiest first inside each"
    c.post(f"/api/session/{sid}/begin", headers=H)
    mark = {"question_id": m1[0]["id"], "marks": [{"start": 0, "end": 5, "style": "highlight", "at": "p"}]}
    assert c.post(f"/api/session/{sid}/state", headers=H, json=mark).status_code == 200, "a passage highlight"
    gate = module(sid, 20)
    assert gate["next_module"] == 2
    up = live(sid)
    assert len(up) == 27 and Counter(q["difficulty"] for q in up) == blueprint.RW_TIERS["module2_upper"]
    assert not {(q["key"], q["seed"]) for q in up} & {(q["key"], q["seed"]) for q in m1}, "a repeat in one sitting"
    done = module(sid, 0)["done"]
    res = c.get(f"/api/session/{sid}/results", headers=H).json()
    e = res["estimate"]
    assert e["route"] == "upper" and e["section"] == "Reading and Writing" and e["high"] - e["low"] == 20, e
    assert done["subject"] == "rw" and done["estimate"]["low"] == e["low"] and done["gate"]["needed"] == 17
    assert res["clock_ms"] == 2 * 32 * 60 * 1000 and res["route_rule"]["half_band"] == 10
    # an R&W sitting is measured against the R&W target, never the Math one
    db.run("UPDATE learners SET target=750, rw_target=500 WHERE id=?", H["X-Learner"])
    low = c.post("/api/mock/new", headers=H, json={"kind": "section", "subject": "rw"}).json()["id"]
    module(low, 5)
    low_done = module(low, 27)["done"]
    rep = c.get(f"/api/session/{low}/results", headers=H).json()
    lo = rep["estimate"]
    assert lo["route"] == "lower" and lo["high"] <= 580 and lo["high"] - lo["low"] == 20, lo
    assert low_done["estimate"]["target"] == 500 and rep["profile"]["target"] == 500, rep["profile"]
    assert c.get("/api/stats?subject=rw", headers=H).json()["profile"]["target"] == 500, "the R&W results chart's target"
    assert c.get("/api/tests?subject=rw", headers=H).json()["target"] == 500
    assert rep["seq"] == 2, "the second R&W section is R&W Section #2"
    assert not rep["path"] or rep["path"]["target"] == 500, rep["path"]
    # an R&W item is one passage and question: its seeds wrap, so the same item under another seed
    # must not come back (remembered by the whole question, as the builders dedupe it)
    ident = lambda q: (q["text"], q["stem"])      # noqa: E731
    seen = {ident(q) for q in m1 + up}
    both = json.loads(db.one("SELECT questions FROM sessions WHERE id=?", low)["questions"])
    assert not seen & {ident(q) for q in both["module1"] + both["module2"]}, "an R&W item came back"
    seen |= {ident(q) for q in both["module1"] + both["module2"]}
    # its twin: each slot's skill and tier, items this learner has not had
    tw = c.post("/api/mock/new", headers=H, json={"kind": "twin", "twin_of": sid}).json()
    t1 = live(tw["id"])
    assert tw["subject"] == "rw" and [(q["topic"], q["difficulty"]) for q in t1] == [(q["topic"], q["difficulty"]) for q in m1]
    assert not {ident(q) for q in t1} & seen, "an R&W twin repeated an item"
    # a drill on the same skills while an R&W section is live serves none of its items
    D = {"X-Learner": "a:flowrw02"}
    s2 = c.post("/api/mock/new", headers=D, json={"kind": "section", "subject": "rw"}).json()["id"]
    c.post(f"/api/session/{s2}/begin", headers=D)
    on = {ident(q) for q in live(s2)}
    dr = c.post("/api/drill", headers=D, json={"topics": ["rw_words_in_context", "rw_boundaries"], "count": 12}).json()
    for _ in range(12):
        cur = stored(dr["id"])[-1]
        c.post(f"/api/drill/{dr['id']}/answer", headers=D, json={"question_id": cur["id"], "answer": keyed_answer(cur, True)})
        if c.post(f"/api/drill/{dr['id']}/next", headers=D).json().get("done"):
            break
    assert len(stored(dr["id"])) >= 10 and not on & {ident(q) for q in stored(dr["id"])}, "a drill served a live test's item"
    c.post(f"/api/session/{tw['id']}/discard", headers=H)
    print(f"ok  R&W section: 27 + 27 in Bluebook's order, routed (upper {e['low']}-{e['high']}, lower capped at "
          f"{lo['high']}), passage highlights kept, a twin of new items skill by skill")

    # --- the R&W diagnostic and a custom test ------------------------------------------------------
    dg = c.post("/api/session", headers=H, json={"subject": "rw"}).json()
    assert dg["subject"] == "rw" and dg["form"] in api_tests.FORM_IDS["rw"] and dg["duration"] == 20 * 71, dg
    c.post(f"/api/session/{dg['id']}/begin", headers=H)
    for q in api_tests.FORMS[dg["form"]]:
        c.post(f"/api/session/{dg['id']}/answer", headers=H, json={"question_id": q["id"], "answer": keyed_answer(q, True)})
    assert c.post(f"/api/session/{dg['id']}/finish", headers=H).json()["right"] == 20
    # (its report waits for a saved account, as Math's does: read the marked result itself)
    res = json.loads(db.one("SELECT result FROM sessions WHERE id=?", dg["id"])["result"])
    assert {d["domain"] for d in res["domains"]} == set(scoring.RW_DOMAINS), res["domains"]
    assert res["estimate"]["section"] == "Reading and Writing" and res["estimate"]["high"] - res["estimate"]["low"] == 20
    cu = c.post("/api/mock/new", headers=H, json={"kind": "custom", "custom": {
        "topics": ["rw_boundaries", "rw_words_in_context"], "count": 10}}).json()
    qs = live(cu["id"])
    assert cu["subject"] == "rw" and len(qs) == 10 and cu["duration"] == 10 * 71, cu
    assert {q["topic"] for q in qs} == {"rw_boundaries", "rw_words_in_context"} and all(q["type"] == "mcq" for q in qs)
    assert c.post("/api/mock/new", headers=H, json={"kind": "custom", "custom": {
        "topics": ["rw_boundaries", "circles"]}}).status_code == 422, "one subject per custom test"
    c.post(f"/api/session/{cu['id']}/discard", headers=H)
    print("ok  R&W diagnostic (20, 71 s each, R&W domains) and an R&W custom test (all multiple choice)")

    # --- the full SAT: R&W, the break, Math, one total ----------------------------------------------
    def full_rw(right):
        f = c.post("/api/mock/new", headers=H, json={"kind": "full"}).json()
        assert f["kind"] == "full" and f["subject"] == "rw" and f["full"] == {"id": f["id"], "part": 1, "of": 2,
                                                                              "number": f["full"]["number"]}, f
        assert f["section"] == "Section 1, Module 1: Reading and Writing"
        module(f["id"], right)
        return f["id"], module(f["id"], right)["done"]

    fid, done = full_rw(27)
    nxt = done["next"]["id"]
    assert done["full"] == {"id": fid, "part": 1} and done["next"]["break_seconds"] == 600
    assert c.post(f"/api/session/{fid}/finish", headers=H).json()["done"]["next"]["id"] == nxt, "a repeated hand-in"
    lobby = c.get(f"/api/session/{nxt}", headers=H).json()
    assert lobby["subject"] == "math" and lobby["section"] == "Section 2, Module 1: Math" and lobby["questions"] == []
    assert lobby["full"]["break"]["seconds"] == 600 and lobby["ranked"], lobby["full"]
    assert lobby["full"]["number"] == 1, "the Math half of the first full SAT is #1 too"
    assert c.get(f"/api/full/{fid}", headers=H).json()["status"] == "break"
    module(nxt, 22)
    got = module(nxt, 22)["done"]["full"]
    full = c.get(f"/api/full/{nxt}", headers=H).json()
    rw_e, m_e = (s["estimate"] for s in full["sections"])
    assert [s["subject"] for s in full["sections"]] == ["rw", "math"] and full["status"] == "done" and full["ranked"]
    assert full["total"] == got["total"] == scoring.total_band(rw_e["mid"], m_e["mid"]), (full["total"], rw_e, m_e)
    assert full["total"]["high"] - full["total"]["low"] == 20 and full["break"]["long"] is False
    assert full["number"] == 1 and full["previous"] is None and full["ms"] is not None
    st = c.get("/api/stats", headers=H).json()
    assert st["total"], "Results' Both view has a total"
    # one current score per subject on every page (estimate.current), never one sitting's band by itself
    from server import estimate
    over = c.get("/api/tests?subject=rw", headers=H).json()["estimate"]
    cur = estimate.current(H["X-Learner"], "rw")
    assert over["current"] == cur and (over["headline_parts"]["low"], over["headline_parts"]["high"]) == (cur["low"], cur["high"])
    assert c.get("/api/stats?subject=rw", headers=H).json()["current"] == cur
    # a full SAT counts once, never also as two sections; discarded sittings not at all
    assert st["tests"] == {"mock": 2, "module": 0, "diagnostic": 1, "custom": 0, "full": 1}, st["tests"]
    assert c.get(f"/api/full/{fid}", headers={"X-Learner": "a:someoneelse"}).status_code == 403
    hist = c.get("/api/history", headers=H).json()["sessions"]
    [entry] = [h for h in hist if h["kind"] == "full"]
    assert entry["id"] == fid and [p["subject"] for p in entry["parts"]] == ["rw", "math"]
    assert entry["full"]["number"] == 1 and all(p["full"]["number"] == 1 for p in entry["parts"])
    # both halves are Full SAT #1, numbered apart from the plain sections, in history and the reports
    assert [p["seq"] for p in entry["parts"]] == [1, 1], [p["seq"] for p in entry["parts"]]
    assert c.get(f"/api/session/{nxt}/results", headers=H).json()["seq"] == 1
    assert not any(h.get("full") and h["kind"] != "full" for h in hist), "a full SAT's sections listed twice"
    assert sum(bool(h["full"]) for h in c.get("/api/history?subject=rw", headers=H).json()["sessions"]) == 1
    kinds = {k["id"]: k for k in c.get("/api/tests?subject=rw", headers=H).json()["kinds"]}
    assert kinds["full"]["yours"] == 1 and kinds["full"]["last"] == full["total"]["mid"] and kinds["section"]["yours"] == 2
    print(f"ok  full SAT: R&W then Math in its lobby, total {full['total']['low']}-{full['total']['high']}"
          " from the two centres, one history entry, its own kind")

    # stopping after R&W leaves a scored R&W section; a break over 11:00 unranks the Math section only
    stop, done = full_rw(10)
    assert c.post(f"/api/session/{done['next']['id']}/discard", headers=H).status_code == 200
    stopped = c.get(f"/api/full/{stop}", headers=H).json()
    assert stopped["status"] == "stopped" and stopped["sections"][0]["estimate"] and stopped["total"] is None
    slow, done = full_rw(27)
    late = done["next"]["id"]
    row = db.one("SELECT cfg FROM sessions WHERE id=?", late)
    cfg = json.loads(row["cfg"])
    cfg["full"]["after"] = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=12)).isoformat(timespec="seconds")
    db.run("UPDATE sessions SET cfg=?, started=? WHERE id=?", json.dumps(cfg), cfg["full"]["after"], late)
    assert c.get(f"/api/session/{late}", headers=H).json()["why"] == "long break"
    module(late, 22)
    module(late, 22)
    gone = c.get(f"/api/full/{slow}", headers=H).json()
    assert gone["break"]["long"] and not gone["ranked"] and gone["unranked_why"] == "long break" and gone["total"]
    assert gone["sections"][0]["ranked"] and not gone["sections"][1]["ranked"]
    assert gone["number"] == 3 and gone["previous"] == full["total"], "the last full SAT with a total"
    # the stopped one is its R&W section everywhere: stats, the overview's kinds, the Both list
    st = c.get("/api/stats", headers=H).json()["tests"]
    assert st["full"] == 2 and st["mock"] == 3, st
    kinds = {k["id"]: k["yours"] for k in c.get("/api/tests?subject=rw", headers=H).json()["kinds"]}
    assert kinds["full"] == 2 and kinds["section"] == 3, kinds
    hist = c.get("/api/history?limit=50", headers=H).json()["sessions"]
    [rw_only] = [h for h in hist if h["id"] == stop]
    assert rw_only["kind"] == "mock" and rw_only["full"]["complete"] is False and rw_only["estimate"]
    assert sum(h["kind"] == "full" for h in hist) == 2
    high = c.get("/api/history?limit=50&sort=highest", headers=H).json()["sessions"]
    place = [(h["estimate"]["mid"] - h["estimate"]["scale"][0]) / (h["estimate"]["scale"][1] - h["estimate"]["scale"][0])
             for h in high if h.get("estimate")]
    assert place == sorted(place, reverse=True), "highest first, each on its own scale"
    assert db.one("SELECT unranked_why FROM sessions WHERE id=?", late)["unranked_why"] == "long break"
    print("ok  full SAT: stopping after R&W keeps the R&W section; a long break unranks Math, both stay scored")


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
    mock = c.post(f"/api/session/{mock['id']}/begin", headers=S).json()
    assert c.post("/api/saved", headers=S, json={"session": mock["id"], "question_id": mock["questions"][0]["id"]}
                  ).status_code == 404, "saved a question off a live test"
    c.post(f"/api/drill/{ch['id']}/answer", headers=S, json={"question_id": cur["id"], "answer": keyed_answer(cur, True)})
    assert c.post("/api/saved", headers=S, json=body).json()["saved"] is True
    print("ok  save keeps only practice questions, a challenge's once answered, and only your own")

    # --- a practice set is not a paper, and a paper is not a practice set ---------
    assert c.post(f"/api/session/{ch['id']}/answer", headers=S, json={"question_id": cur["id"], "answer": None}).status_code == 409
    assert c.post(f"/api/session/{ch['id']}/finish", headers=S).status_code == 409
    assert c.get(f"/api/drill/{mock['id']}", headers=S).status_code == 404
    assert c.post(f"/api/drill/{mock['id']}/answer", headers=S,
                  json={"question_id": mock["questions"][0]["id"], "answer": 0}).status_code == 404
    print("ok  the test endpoints refuse a practice set and the drill endpoints refuse a test")

    # --- two answers to a test at once both land ---------------------------------
    q1, q2 = mock["questions"][0]["id"], mock["questions"][1]["id"]
    for _ in range(4):
        at_once(lambda: c.post(f"/api/session/{mock['id']}/answer", headers=S, json={"question_id": q1, "answer": 1}),
                lambda: c.post(f"/api/session/{mock['id']}/answer", headers=S, json={"question_id": q2, "answer": 2}))
        got = c.get(f"/api/session/{mock['id']}", headers=S).json()["answers"]
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

    # --- the plan's four steps are kept, checked, and steer the coach -------------
    F = {"X-Learner": "a:planfocus"}
    plain = c.get("/api/map", headers=F).json()["coach"]["topics"]
    geo = [t for t, v in TOPIC_DOMAIN.items() if v == "Geometry and Trigonometry"]
    assert not set(plain) & set(geo), "a new learner starts on the big domains"
    got = c.put("/api/me", headers=F, json={"current": 520, "target": 700, "tests": "daily", "minutes": 120,
                                           "focus": {"Geometry and Trigonometry": "focus", "Algebra": "strong",
                                                     "Advanced Math": "normal"}}).json()["profile"]
    assert got["current"] == 520 and got["tests"] == "daily" and got["minutes"] == 120
    assert got["focus"] == {"Geometry and Trigonometry": "focus", "Algebra": "strong"}, got["focus"]
    steered = c.get("/api/map", headers=F).json()["coach"]
    assert set(steered["topics"]) & set(geo), steered["topics"]
    assert steered["count"] == 76, "two hours a day is 76 questions at the test's pace"
    for bad in ({"focus": {"Algebra": "focus", "Advanced Math": "focus", "Geometry and Trigonometry": "focus"}},
                {"focus": {"Reading": "focus"}}, {"focus": {"Algebra": "maybe"}},
                {"current": 205}, {"tests": "hourly"}):
        assert c.put("/api/me", headers=F, json=bad).status_code == 422, bad
    print("ok  the plan keeps where you are, the test rhythm and focus per domain, and focus steers the coach")


def run_checks(c) -> None:
    """Every task's own checks, server/checks/<task>.py, each a check(c) (or a
    zero-arg check() that opens its own client). A standalone script (its own
    main(), no check at all) runs on its own instead.

    rw_bank.py is excluded from this import-and-discover loop: it points
    db.DB_PATH at its own scratch file as an unguarded module-level side effect
    (no check(c), run on its own per its own docstring), which would otherwise
    leak into every other check through db.conn()'s one-connection-per-thread
    cache the moment any later check's work needs a thread that has not opened
    a connection yet."""
    import importlib
    import inspect
    for f in sorted((pathlib.Path(__file__).resolve().parent / "checks").glob("*.py")):
        if f.stem not in ("__init__", "rw_bank"):
            check = getattr(importlib.import_module(f"server.checks.{f.stem}"), "check", None)
            if check:
                check(c) if inspect.signature(check).parameters else check()


if __name__ == "__main__":
    try:
        sys.exit(main())
    finally:
        _tmp.cleanup()
