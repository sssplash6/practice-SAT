"""The R&W bank in practice: the builder's rw read is the real catalogue, an R&W set
serves passages with no key leaking, answers file, and Math sets stay Math.

    PYTHONPATH=. python3 server/checks/rw_bank.py
"""

from __future__ import annotations

import json
import pathlib
import secrets
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
_tmp = tempfile.TemporaryDirectory()
from server import db                                        # noqa: E402

db.DB_PATH = pathlib.Path(_tmp.name) / "test.db"

from fastapi.testclient import TestClient                    # noqa: E402

from server import deps                                      # noqa: E402
from server.app import app                                   # noqa: E402

LEAKS = ("answer", "rationale", "reasons", "key", "seed")


def call(c, method, path, learner, body=None, status=200):
    r = c.request(method, path, headers={"X-Tz": "0", "X-Learner": learner}, json=body)
    assert r.status_code == status, (method, path, r.status_code, r.text[:400])
    return r.json()


def main() -> int:
    with TestClient(app) as c:
        me = "a:rwbank" + secrets.token_hex(6)
        bank = call(c, "GET", "/api/bank?subject=rw", me)
        assert bank["bank"] is True and bank["totals"]["skills"] == 10, bank["totals"]
        assert [d["name"] for d in bank["domains"]] == ["Information and Ideas", "Craft and Structure",
                                                       "Expression of Ideas", "Standard English Conventions"]
        assert "words" in bank
        math = call(c, "GET", "/api/bank?subject=math", me)
        assert all(not s["slug"].startswith("rw_") for d in math["domains"] for s in d["skills"])
        print(f"ok  /api/bank?subject=rw: {bank['totals']['skills']} skills, {bank['totals']['types']} types")

        d = call(c, "POST", "/api/drill", me, {"subject": "rw", "topics": ["rw_inferences", "rw_boundaries"], "count": 6})
        seen = set()
        for _ in range(6):
            st = call(c, "GET", f"/api/drill/{d['id']}", me)
            q = st["question"]
            assert q["text"] and deps.subject_of(q["topic"]) == "rw", q.get("topic")
            assert not set(q) & set(LEAKS), set(q) & set(LEAKS)
            assert q["text"] not in seen, "a passage came back twice"
            seen.add(q["text"])
            stored = next(x for x in json.loads(db.one("SELECT questions FROM sessions WHERE id=?", d["id"])["questions"])
                          if x["id"] == q["id"])
            call(c, "POST", f"/api/drill/{d['id']}/answer", me, {"question_id": q["id"], "answer": "ABCD".index(stored["answer"])})
            if call(c, "POST", f"/api/drill/{d['id']}/next", me).get("done"):
                break
        n = db.one("SELECT COUNT(*) n FROM attempts WHERE learner=? AND topic LIKE 'rw_%' AND correct=1", me)["n"]
        assert n >= 5, n
        print(f"ok  an R&W set served {len(seen)} distinct passages, no key in what the student sees, {n} right answers filed")

        # a miss opens one mistake per R&W type, named by its skill, unnamed so another item can close it
        you = "a:rwmiss" + secrets.token_hex(6)
        d = call(c, "POST", "/api/drill", you, {"subject": "rw", "topics": ["rw_boundaries"], "count": 4})
        q = call(c, "GET", f"/api/drill/{d['id']}", you)["question"]
        stored = next(x for x in json.loads(db.one("SELECT questions FROM sessions WHERE id=?", d["id"])["questions"])
                      if x["id"] == q["id"])
        call(c, "POST", f"/api/drill/{d['id']}/answer", you, {"question_id": q["id"], "answer": ("ABCD".index(stored["answer"]) + 1) % 4})
        trap = db.one("SELECT * FROM traps WHERE learner=? AND closed IS NULL", you)
        assert trap and trap["norm"] == "" and trap["template"] == stored["key"], dict(trap or {})
        print(f"ok  an R&W miss opens one closable mistake on its type, labelled {trap['label']!r}")
        # Today holds both sections (DESIGN §1): the R&W mistake is on its Mistakes card, labelled rw,
        # and its Fix all starts an R&W set
        today = call(c, "GET", "/api/today", you)
        row = next(x for x in today["traps"]["top"] if x["template"] == stored["key"])
        assert row["subject"] == "rw" and today["mistakes"] == 1, row
        fix = next(f for f in today["traps"]["fixes"] if f["subject"] == "rw")
        assert fix["body"] == {"mistakes": True, "subject": "rw"} and len(today["traps"]["fixes"]) == 1, fix
        got = call(c, "POST", "/api/drill/preview", you, fix["body"])
        assert got["available"] and got["cfg"]["subject"] == "rw", got
        call(c, "POST", "/api/drill", you, {"mistakes": True, "subject": "math"}, status=409)
        redo = call(c, "POST", "/api/drill", you, {"pool": "redo", "subject": "rw", "count": 2})
        rq = call(c, "GET", f"/api/drill/{redo['id']}", you)["question"]
        assert rq["topic"] == "rw_boundaries" and rq["text"] != q["text"], "redo serves a fresh item of the type"
        rs = next(x for x in json.loads(db.one("SELECT questions FROM sessions WHERE id=?", redo["id"])["questions"])
                  if x["id"] == rq["id"])
        call(c, "POST", f"/api/drill/{redo['id']}/answer", you, {"question_id": rq["id"], "answer": "ABCD".index(rs["answer"])})
        assert db.one("SELECT owed FROM traps WHERE id=?", trap["id"])["owed"] == trap["owed"] - 1, "a clean answer pays it down"
        print("ok  Today lists it as R&W with an R&W Fix; Math mistake sets ignore it; an R&W redo set serves a fresh item of that type")

        call(c, "POST", "/api/drill", me, {"subject": "math", "topics": ["rw_inferences"], "count": 3}, status=422)
        m = call(c, "POST", "/api/drill", me, {"source": "start", "count": 8})
        st = call(c, "GET", f"/api/drill/{m['id']}", me)
        assert deps.subject_of(st["question"]["topic"]) == "math"
        print("ok  Math sets never take an R&W skill")

        # an R&W worked example is a bank question shown with its key: opt-in, and never served again as a question
        from satbank.registry import generate, templates, topic_of
        assert call(c, "GET", "/api/me", me)["profile"]["prefs"]["practice"]["rw"]["worked_first"] is False
        small = sorted((len({generate(t, s).source_id for s in range(60)}), t) for t in templates() if topic_of(t).startswith("rw_"))
        for k, tpl in small[20:60]:
            ex_me = "a:rwex" + secrets.token_hex(6)
            d = call(c, "POST", "/api/drill", ex_me, {"subject": "rw", "templates": [tpl], "count": k, "worked_first": True})
            shown, asked = set(), []
            for _ in range(k + 3):
                q = call(c, "GET", f"/api/drill/{d['id']}", ex_me).get("question")
                if not q:
                    break
                body = (q.get("text") or "") + q["stem"]
                if q.get("kind") == "example":
                    shown.add(body)
                else:
                    asked.append(body)
                    call(c, "POST", f"/api/drill/{d['id']}/answer", ex_me, {"question_id": q["id"], "answer": 0})
                if call(c, "POST", f"/api/drill/{d['id']}/next", ex_me).get("done"):
                    break
            assert not shown & set(asked), (tpl, "a worked example came back as a question")
        print("ok  R&W worked examples are off by default and never come back as a question")

        # full-sat D: a body that names R&W needs no subject; a spent type goes on with its skill's other types
        from server import progress
        sub = "a:rwsub" + secrets.token_hex(6)
        one = small[0][1]
        tw = call(c, "POST", "/api/drill", sub, {"templates": [one], "source": "twin", "count": 3})
        assert tw["subject"] == "rw", tw["subject"]
        got = []
        for _ in range(3):
            q = call(c, "GET", f"/api/drill/{tw['id']}", sub)["question"]
            got.append(q)
            full = next(x for x in json.loads(db.one("SELECT questions FROM sessions WHERE id=?", tw["id"])["questions"])
                        if x["id"] == q["id"])
            call(c, "POST", f"/api/drill/{tw['id']}/answer", sub, {"question_id": q["id"], "answer": "ABCD".index(full["answer"])})
            if call(c, "POST", f"/api/drill/{tw['id']}/next", sub).get("done"):
                break
        assert len(got) == 3 and len({q["text"] for q in got}) == 3 and {q["topic"] for q in got} == {topic_of(one)}, \
            [(q["topic"], q.get("why")) for q in got]
        assert got[-1]["why"]["kind"] == "sibling", got[-1]["why"]
        call(c, "POST", f"/api/drill/{tw['id']}/finish", sub)
        assert call(c, "POST", "/api/drill", sub, {"again": tw["id"]})["subject"] == "rw"
        share = call(c, "POST", "/api/sets", sub, {"kind": "set", "session": tw["id"]})["code"]
        taker = "a:rwtaker" + secrets.token_hex(6)
        assert call(c, "POST", "/api/drill", taker, {"share": share})["subject"] == "rw", "a shared R&W set starts as R&W"
        print("ok  an R&W twin infers its subject, outlives a one-item type on its skill, and again keeps the subject")

        # misses: kind is a wrong choice (never grid-in), one label a type however many passages; the hint's example
        # is a passage the student has not met, never the one on screen
        tpl = max(t for t in templates() if topic_of(t) == "rw_boundaries")
        lab = "a:rwlab" + secrets.token_hex(6)
        for _ in range(2):
            d = call(c, "POST", "/api/drill", lab, {"templates": [tpl], "count": 1, "hints": True})
            q = d["question"]
            full = next(x for x in json.loads(db.one("SELECT questions FROM sessions WHERE id=?", d["id"])["questions"])
                        if x["id"] == q["id"])
            hint = {}
            while hint.get("kind") != "example":
                hint = call(c, "POST", f"/api/drill/{d['id']}/hint", lab, {"question_id": q["id"]})
            ex = hint["example"]
            assert ex["text"] and ex["text"] != q["text"], "the hint's example is the question on screen"
            call(c, "POST", f"/api/drill/{d['id']}/answer", lab, {"question_id": q["id"], "answer": ("ABCD".index(full["answer"]) + 1) % 4})
        traps = db.rows("SELECT * FROM traps WHERE learner=? AND template=?", lab, tpl)
        assert len(traps) == 1 and traps[0]["hits"] == 2 and traps[0]["label"] == progress.rw_label(tpl), [dict(t) for t in traps]
        redo = call(c, "GET", "/api/review/redo?subject=rw", lab)["items"]
        assert [x["kind"] for x in redo] == ["misconception"], [x["kind"] for x in redo]
        seen = {(r["template"], r["seed"]) for r in db.rows("SELECT template, seed FROM practice_seen WHERE learner=?", lab)}
        ex = call(c, "GET", f"/api/types/{tpl}/example", lab)
        assert (ex["template"], ex["seed"]) not in seen and ex["question"]["text"], "a type's example is a passage already met"
        print("ok  R&W misses: one trap a type, labelled by the type, kind misconception; examples are unmet passages")

        # a plan's R&W tasks carry ':rw' (plan._task's suffix), a check-in task its skill: each one starts
        from server import drill
        day = "2026-10-22"
        for kind in drill.TASK_KINDS:
            for task in (f"{day}:{kind}", f"{day}:{kind}:rw", f"{day}:{kind}:rw_boundaries"):
                pv = call(c, "POST", "/api/drill/preview", lab, {"task": task, "topics": ["rw_boundaries"], "count": 3})
                assert pv["servable"] and pv["cfg"]["subject"] == "rw", (task, pv.get("reason"))
        call(c, "POST", "/api/drill/preview", lab, {"task": f"{day}:fix:RW!", "topics": ["rw_boundaries"]}, status=422)
        print("ok  every plan task id starts a set, an R&W one with its :rw suffix")

        # review 2026-10-23: an anonymous example cannot walk the written bank (each is a real item with its key)
        r = c.get(f"/api/types/{tpl}/example", params={"want": "x"})
        assert r.status_code == 409, (r.status_code, r.text[:200])
        # an exact set on a small type: the hint's worked example is never an item the set still holds
        ex_t = next(t for k, t in small if k >= 3)          # the bank grows: smallest type with 3+ items
        pairs, texts = [], set()
        for s_ in range(60):
            it = generate(ex_t, s_)
            if it.text not in texts:
                texts.add(it.text)
                pairs.append([ex_t, s_])
        owner, held = "a:rwown" + secrets.token_hex(6), "a:rwheld" + secrets.token_hex(6)
        o = call(c, "POST", "/api/drill", owner, {"templates": [ex_t], "count": len(pairs)})
        for _ in pairs:                      # the owner answers every item, then shares them exactly
            oq = call(c, "GET", f"/api/drill/{o['id']}", owner)["question"]
            ok = next(x for x in json.loads(db.one("SELECT questions FROM sessions WHERE id=?", o["id"])["questions"])
                      if x["id"] == oq["id"])["answer"]
            call(c, "POST", f"/api/drill/{o['id']}/answer", owner, {"question_id": oq["id"], "answer": "ABCD".index(ok)})
            if call(c, "POST", f"/api/drill/{o['id']}/next", owner).get("done"):
                break
        mine = [[x["key"], x["seed"]] for x in json.loads(db.one("SELECT questions FROM sessions WHERE id=?", o["id"])["questions"])
                if x.get("kind", "question") == "question" and x["key"] == ex_t]
        code = call(c, "POST", "/api/sets", owner, {"kind": "items", "items": mine})["code"]
        d = call(c, "POST", "/api/drill", held, {"share": code, "hints": True})
        q = d["question"]
        hint = {}
        while hint.get("kind") != "example":
            hint = call(c, "POST", f"/api/drill/{d['id']}/hint", held, {"question_id": q["id"]})
        assert hint.get("example") and hint["example"]["text"] not in texts, "a worked example is a question the set still holds"
        # the pace forecast reads R&W speed per skill (R&W module slots name skills, not domains)
        slow = "a:rwslow" + secrets.token_hex(6)
        d = call(c, "POST", "/api/drill", slow, {"topics": ["rw_boundaries"], "count": 6})
        for _ in range(6):
            q = call(c, "GET", f"/api/drill/{d['id']}", slow)["question"]
            full = next(x for x in json.loads(db.one("SELECT questions FROM sessions WHERE id=?", d["id"])["questions"])
                        if x["id"] == q["id"])
            call(c, "POST", f"/api/drill/{d['id']}/answer", slow, {"question_id": q["id"], "answer": "ABCD".index(full["answer"]), "ms": 200_000})
            if call(c, "POST", f"/api/drill/{d['id']}/next", slow).get("done"):
                break
        strip = progress.pace(slow, subject="rw")["forecast"]["strip"]
        assert {x["ms"] for x in strip if x["domain"] == "rw_boundaries"} == {200_000}, strip[:3]
        # each R&W skill's College Board count once (138 Central Ideas, not 276)
        cb = {}
        for x in drill.cb_index().values():
            if x["subject"] == "rw" and x.get("topic"):
                cb[x["topic"]] = cb.get(x["topic"], 0) + 1
        assert {s["slug"]: s["cb_count"] for d_ in bank["domains"] for s in d_["skills"]} == cb
        print("ok  no anonymous R&W example; examples skip what a set holds; R&W pace per skill; College Board counts once")
    return 0


if __name__ == "__main__":
    sys.exit(main())
