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

from server import mail, scoring                             # noqa: E402
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

    # --- the marking itself, away from the wire -------------------------------
    assert scoring.is_correct({"type": "spr", "answer": "5776"}, "5,776")
    assert scoring.is_correct({"type": "mcq", "answer": "C"}, 2)
    assert not scoring.is_correct({"type": "mcq", "answer": "C"}, None)
    assert not scoring.is_correct({"type": "mcq", "answer": "C"}, "C")      # index, not letter
    assert not scoring.is_correct({"type": "spr", "answer": "12"}, "")
    print("ok  marking: commas ignored, blanks wrong, a letter is not an index")

    print("\nall good")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    finally:
        _tmp.cleanup()
