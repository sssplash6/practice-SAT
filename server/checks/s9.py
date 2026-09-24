"""S9 Words server acceptance checks. Run with PYTHONPATH=. python3 server/checks/s9.py."""

from __future__ import annotations

import datetime as dt
import json
import logging
import os
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if "server.db" not in sys.modules:
    os.environ["SATF_DB"] = str(ROOT / "server" / "s9.db")
logging.disable(logging.CRITICAL)

from fastapi.testclient import TestClient  # noqa: E402
from server import db, words  # noqa: E402
from server.app import app  # noqa: E402


def code() -> str:
    return "s9:" + uuid.uuid4().hex[:20]


def ok(response, status: int = 200) -> dict:
    assert response.status_code == status, (response.status_code, response.text[:500])
    return response.json()


def use(client: TestClient, learner: str, path: str, body: dict) -> dict:
    return ok(client.post(path, json=body, headers={"X-Learner": learner}))


def test_content(client: TestClient) -> None:
    data = words.content()
    assert len(data["entries"]) >= 1_000
    assert not any(w.get("collection") == "math" for w in data["entries"].values())
    assert words.entry("qualify.limit") and words.entry("qualify.meet")
    frame = next(f for f in data["frames"].values() if f.get("reviewed") is None)
    try:
        words.item("rw.wic." + frame["id"], 77, frame["keys"][0])
    except ValueError:
        pass
    else:
        raise AssertionError("unreviewed content escaped the production gate")
    if not any(f.get("reviewed") for f in data["frames"].values()):
        assert words.choose_template("mitigate") is None
        assert ok(client.get("/api/words/today", headers={"X-Learner": code()}))["wic"] is None

    os.environ["SATF_WORDS_UNREVIEWED"] = "1"
    a = words.item("rw.wic." + frame["id"], 77, frame["keys"][0])
    assert a == words.item("rw.wic." + frame["id"], 77, frame["keys"][0])
    assert len(a["choices"]) == len(set(a["choices"])) == 4
    assert all(x and x != a["choices"][a["answer_index"]] for i, x in enumerate(a["choices"])
               if i != a["answer_index"])
    assert any(s["kind"] == "clue" for s in a["spans"])
    pairs = list(data["pairs"].values())
    for p in pairs[:20]:
        q = words.item("rw.tr." + p["id"], 19, p["fits"][0])
        assert len(set(q["option_logics"])) == 4
        assert q["logic_needed"] not in [x for i, x in enumerate(q["option_logics"])
                                           if i != q["answer_index"]]
    for i in range(60):
        q = words.item("rw.wic." + frame["id"], i, frame["keys"][0])
        assert all(choice.casefold() not in q["text"].casefold() for choice in q["choices"])


def test_core() -> None:
    learner = code()
    a, b = "qualify.limit", "qualify.meet"
    first = words.grade(learner, a, True, "cards", "card")
    assert first["box"]["after"] == 2
    assert words.state(learner, b)["box"] == 0
    s = words.state(learner, a)
    s["box"], s["due"], s["lastday"] = 3, words.local_day().isoformat(), None
    with db.atomic() as c:
        words._upsert_state(c, s)
    self_grade = words.grade(learner, a, True, "cards", "card")
    assert self_grade["box"]["after"] == 3 and "Prove" in self_grade["status"]
    s = words.state(learner, a)
    s["due"], s["lastday"] = words.local_day().isoformat(), None
    with db.atomic() as c:
        words._upsert_state(c, s)
    guess = words.grade(learner, a, True, "quiz", "incontext", conf="guess")
    assert guess["box"]["after"] == 3 and guess["guessed"]
    s = words.state(learner, a)
    s["due"], s["lastday"] = words.local_day().isoformat(), None
    with db.atomic() as c:
        words._upsert_state(c, s)
    proof = words.grade(learner, a, True, "quiz", "incontext")
    assert proof["box"]["after"] == 4 and words.state(learner, a)["proven"]
    assert words.state(learner, b)["box"] == 0
    wrong = words.grade(learner, a, False, "quiz", "incontext")
    assert wrong["box"]["after"] == 1 and wrong["due"] == words.local_day().isoformat()
    date = words.local_day()
    assert len({words._due(date, 3, learner, word=f"w{i}", reps=2) for i in range(30)}) >= 2
    words._simulate_selfcheck()
    capped = code()
    for i in range(60):
        s = words.state(capped, "mitigate")
        s["due"], s["lastday"] = words.local_day().isoformat(), None
        with db.atomic() as c:
            words._upsert_state(c, s)
        assert words.grade(capped, "mitigate", True, "cards", "card")["box"]["after"] <= 3, i
    fresh = code()
    sentences = [words.new_sentence(fresh, "mitigate") for _ in range(6)]
    assert len({q["template"] for q in sentences}) == len({q["text"] for q in sentences}) == 6
    assert all("mitigate" in q["text"].casefold() for q in sentences)
    recall_learner = code()
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    with db.atomic() as c:
        for i in range(50):
            words._review_row(c, recall_learner, "mitigate", None, "cards", "card", i != 0,
                              None, 2, (words.local_day() - dt.timedelta(days=1)).isoformat(),
                              8000, now)
    assert words.recall(recall_learner)["scale"] == 1.2
    scaled = (dt.date.fromisoformat(words._due(words.local_day(), 3, recall_learner, word="mitigate")) - words.local_day()).days
    assert 7 <= scaled <= 9


def test_library(client: TestClient) -> None:
    learner = code()
    headers = {"X-Learner": learner}
    lib = ok(client.get("/api/words?days=60", headers=headers))
    assert len(lib["words"]) >= 1_000 and len(lib["forecast"]) == 60
    assert all(1 <= w["freq_band"] <= 5 for w in lib["words"] if not w["own"])
    assert {"due", "new", "learning", "known", "saved", "mine", "missed", "lookedup",
            "new_today", "goal", "claimed"} <= set(lib["counts"])
    detail = ok(client.get("/api/words/qualify.limit", headers=headers))
    assert any(w["slug"] == "qualify.meet" for w in detail["other_senses"])
    assert detail["shades"]["words"] and detail["shades"]["at"] is not None
    assert detail["confusions"] and detail["roots"] is not None
    saved = use(client, learner, "/api/words/mitigate/save", {"on": True})
    assert saved["saved"]
    assert words.deck(learner, "new", n=1)[0] == "mitigate"
    ind = client.get("/api/words/index")
    assert ind.status_code == 200 and len(ind.json()["common"]) >= 10_000
    assert client.get("/api/words/index", headers={"If-None-Match": ind.headers["etag"]}).status_code == 304
    insights = ok(client.get("/api/words/insights", headers=headers))
    assert {"traps", "logic", "gaps", "calibration", "recall", "finish"} <= insights.keys()
    today = ok(client.get("/api/words/today", headers=headers))
    assert today["summary"]["start"]["path"] == "/api/words/run"


def test_runs(client: TestClient) -> None:
    learner = code()
    h = {"X-Learner": learner}
    run = use(client, learner, "/api/words/run", {"mode": "quiz", "deck": {"source": "words", "words": ["mitigate"]},
                                                  "formats": ["incontext"], "count": 1})
    q = run["next"]
    assert q["step"] == "predict" and len(q["predictions"]) == 3 and "choices" not in q
    assert not {"answer_index", "reasons", "traps", "template", "seed", "word", "key"} & q.keys()
    assert client.post(f"/api/words/run/{run['id']}/save", json={"item_id": q["item_id"]}, headers=h).status_code == 409
    stage = use(client, learner, f"/api/words/run/{run['id']}/answer",
                {"item_id": q["item_id"], "prediction": q["predictions"].index("to make less severe")})
    assert stage["step"] == "choices" and len(stage["item"]["choices"]) == 4
    stored = json.loads(db.one("SELECT questions FROM sessions WHERE id=?", run["id"])["questions"])[0]
    wrong_index = next(i for i in range(4) if i != stored["answer_index"])
    result = use(client, learner, f"/api/words/run/{run['id']}/answer",
                 {"item_id": q["item_id"], "answer": wrong_index, "ms": 5000})
    assert result["correct"] is False and result["gap"] == "word"
    assert len(result["reasons"]) == 4 and any(s["kind"] == "clue" for s in result["spans"])
    assert result["trap"] in words.content()["traps"]
    assert use(client, learner, f"/api/words/run/{run['id']}/answer",
               {"item_id": q["item_id"], "answer": wrong_index})["already"]
    assert client.post(f"/api/words/run/{run['id']}/another", json={"item_id": q["item_id"]}, headers=h).status_code == 409
    # A fresh two-item run permits a generated twin after the first verdict.
    twin = use(client, learner, "/api/words/run", {"mode": "quiz", "deck": {"source": "words", "words": ["mitigate", "undermine"]},
                                                   "formats": ["incontext"], "count": 2})
    first = twin["next"]
    if first.get("step"):
        use(client, learner, f"/api/words/run/{twin['id']}/answer", {"item_id": first["item_id"], "answer": 0})
    use(client, learner, f"/api/words/run/{twin['id']}/answer", {"item_id": first["item_id"], "answer": 0})
    newer = use(client, learner, f"/api/words/run/{twin['id']}/another", {"item_id": first["item_id"], "like": "word"})
    assert newer["item"]["item_id"] != first["item_id"]

    tr = use(client, learner, "/api/words/run", {"mode": "quiz", "deck": {"source": "words", "words": ["however"]},
                                                 "formats": ["transition"], "count": 1})
    assert tr["next"]["step"] == "logic" and len(tr["next"]["predictions"]) == 4
    assert "choices" not in tr["next"]
    order = use(client, learner, "/api/words/run", {"mode": "quiz", "deck": {"source": "words", "words": ["mitigate"]},
                                                    "formats": ["order"], "count": 1})
    order_q = json.loads(db.one("SELECT questions FROM sessions WHERE id=?", order["id"])["questions"])[0]
    before = {s: words.state(learner, s)["box"] for s in order_q["option_slugs"]}
    ordered = [order_q["option_slugs"].index(s) for s in order_q["answer_order"]]
    assert use(client, learner, f"/api/words/run/{order['id']}/answer",
               {"item_id": "w1", "answer": ordered})["correct"]
    assert before == {s: words.state(learner, s)["box"] for s in order_q["option_slugs"]}
    decode = use(client, learner, "/api/words/run", {"mode": "quiz", "deck": {"source": "words", "words": ["circumspect"]},
                                                     "formats": ["decode"], "count": 1})
    assert decode["next"]["kind"] == "decode"
    assert ok(client.get("/api/words/root/circum", headers=h))["words"]
    sprint = use(client, learner, "/api/words/run", {"mode": "sprint", "deck": {"source": "words", "words": ["mitigate"]}, "count": 1})
    before = words.state(learner, "mitigate")["box"]
    use(client, learner, f"/api/words/run/{sprint['id']}/answer", {"item_id": "w1", "answer": None})
    assert words.state(learner, "mitigate")["box"] == before
    assert {"best", "new_best"} <= ok(client.post(f"/api/words/run/{sprint['id']}/finish", headers=h)).keys()
    checked = use(client, learner, "/api/words/run", {"mode": "check"})
    assert checked["total"] == 12 and checked["timer_total"] == 852
    check_q = json.loads(db.one("SELECT questions FROM sessions WHERE id=?", checked["id"])["questions"])
    assert all(q["kind"] in {"incontext", "nearly"} for q in check_q[:6])
    assert [q["kind"] for q in check_q[6:10]] == ["transition"] * 4
    for q in check_q[:6]:
        filed = use(client, learner, f"/api/words/run/{checked['id']}/answer",
                    {"item_id": q["item_id"], "answer": q["answer_index"]})
        assert filed.get("filed") is True
    route = json.loads(db.one("SELECT cfg FROM sessions WHERE id=?", checked["id"])["cfg"])
    assert route["route"] == "upper"


def test_placement_and_own(client: TestClient) -> None:
    learner = code()
    h = {"X-Learner": learner}
    placement = use(client, learner, "/api/words/run", {"mode": "placement"})
    assert placement["total"] == 60
    assert not {"foil", "band", "answer_index"} & placement["next"].keys()
    stored = json.loads(db.one("SELECT questions FROM sessions WHERE id=?", placement["id"])["questions"])
    assert sum(q["foil"] for q in stored) == 12
    first = next(q for q in stored if not q["foil"])
    result = use(client, learner, f"/api/words/run/{placement['id']}/answer", {"item_id": first["item_id"], "answer": "yes"})
    assert result["box"]["after"] == 3 and words.state(learner, first["word"])["placed"] == 1
    for q in [q for q in stored if not q["foil"] and q["item_id"] != first["item_id"]][:2]:
        use(client, learner, f"/api/words/run/{placement['id']}/answer", {"item_id": q["item_id"], "answer": "yes"})
    updated = json.loads(db.one("SELECT questions FROM sessions WHERE id=?", placement["id"])["questions"])
    assert len(updated) == 61 and sum(q["kind"] == "placement_check" for q in updated) == 1
    sort = use(client, learner, "/api/words/run", {"mode": "sort", "deck": {"source": "words", "words": [first["word"], "bolster"]}, "count": 2})
    sort_q = next(q for q in json.loads(db.one("SELECT questions FROM sessions WHERE id=?", sort["id"])["questions"])
                  if q["word"] == first["word"])
    use(client, learner, f"/api/words/run/{sort['id']}/answer", {"item_id": sort_q["item_id"], "answer": "no"})
    assert ok(client.post(f"/api/words/run/{sort['id']}/undo", json={"item_id": sort_q["item_id"]}, headers=h))["undone"]
    assert words.state(learner, first["word"])["box"] == 3
    assert ok(client.post("/api/words/mine", json={"word": "fzzle"}, headers=h), 400)
    own = use(client, learner, "/api/words/mine", {"word": "Fzzle", "meaning": "a made up test word"})
    assert own["id"].startswith("u:")
    assert client.post("/api/words/mine", json={"word": "fzzle", "meaning": "again"}, headers=h).status_code == 409
    imported = use(client, learner, "/api/words/mine/import", {"text": "Brindle\tto shine\nCrezzle - to bend\ninvalid"})
    assert imported["added"] == 2 and len(imported["skipped"]) == 1
    use(client, learner, "/api/words/mine", {"word": "Grezle", "meaning": "to float"})
    edited = ok(client.put(f"/api/words/mine/{own['id']}",
                           json={"word": "Fzzle", "meaning": "a made up test word",
                                 "example": "The Fzzle looked bright."}, headers=h))
    assert edited["id"] == own["id"]
    import random
    assert "____" in words.quiz_item(own["id"], "cloze", random.Random(3), learner)["text"]
    assert client.delete(f"/api/words/mine/{own['id']}", headers={"X-Learner": code()}).status_code == 404
    assert ok(client.post("/api/words/lists/match", json={"text": "mitigate\nubiquitous\nzzqx"}))["missing"] == ["zzqx"]
    use(client, learner, "/api/words/lists", {"name": "S9", "words": ["mitigate", "bolster"]})
    assert ok(client.post("/api/words/lists/S9/share", headers=h))["available"] is False
    assert client.delete(f"/api/words/mine/{own['id']}", headers=h).status_code == 200


def test_daily_print_offline(client: TestClient) -> None:
    learner = code()
    h = {"X-Learner": learner}
    day = words.local_day().isoformat()
    q = words.daily_item(day, "wic")
    assert q == words.daily_item(day, "wic") and q["item_id"] == f"rw:wic:{day}"
    same = ok(client.get("/api/words/today", headers=h))["wic"]
    assert same["word"] is None and same["item"]["item_id"] == q["item_id"]
    first = use(client, learner, "/api/words/daily/wic/answer", {"answer": 0})
    again = use(client, learner, "/api/words/daily/wic/answer", {"answer": 1})
    assert again["already"] and first["correct"] == again["correct"]
    print_run = use(client, learner, "/api/words/run", {"mode": "print", "deck": {"source": "words", "words": ["mitigate"]},
                                                        "formats": ["incontext"], "count": 2})
    assert len(ok(client.get(f"/api/words/run/{print_run['id']}/key", headers=h))["answers"]) == 2
    newer = ok(client.post(f"/api/words/run/{print_run['id']}/new-version", headers=h))
    old_q = json.loads(db.one("SELECT questions FROM sessions WHERE id=?", print_run["id"])["questions"])
    new_q = json.loads(db.one("SELECT questions FROM sessions WHERE id=?", newer["id"])["questions"])
    assert [q["word"] for q in old_q] == [q["word"] for q in new_q]
    assert [q["seed"] for q in old_q] != [q["seed"] for q in new_q]
    assert ok(client.post(f"/api/words/run/{print_run['id']}/grade", json={"letters": "AA"}, headers=h))["asked"] == 2
    card = use(client, learner, "/api/words/run", {"mode": "cards", "deck": {"source": "words", "words": ["mitigate"]}, "count": 1})
    old = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=2)).isoformat()
    result = use(client, learner, f"/api/words/run/{card['id']}/answer", {"item_id": "w1", "answer": "know", "at": old})
    assert result["correct"]
    assert words.word_reviews(learner, "mitigate")[-1]["at"].startswith(old[:16])
    stale = use(client, code(), "/api/words/run", {"mode": "cards", "deck": {"source": "words", "words": ["bolster"]}, "count": 1})
    bad = client.post(f"/api/words/run/{stale['id']}/answer", json={"item_id": "w1", "answer": "know",
                      "at": (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=80)).isoformat()},
                      headers={"X-Learner": db.one("SELECT learner FROM sessions WHERE id=?", stale["id"])["learner"]})
    assert bad.status_code == 422


def test_crowd_guard() -> None:
    data = words.content()
    for frame in reversed(list(data["frames"].values())):
        ident = frame["id"]
        if words._suppressed(ident) or db.one("SELECT 1 FROM word_fit_reports WHERE frame=?", ident):
            continue
        try:
            q = words.item("rw.wic." + ident, 36, frame["keys"][0])
        except ValueError:
            continue
        choice = next(value for i, value in enumerate(q["choices"]) if i != q["answer_index"])
        break
    else:
        raise AssertionError("no frame available for crowd guard check")
    try:
        assert not words.report_fit(q["template"], choice, code())["suppressed"]
        assert words.report_fit(q["template"], choice, code())["suppressed"]
        assert words._suppressed(ident)
        try:
            words.item(q["template"], 36, q["word"])
        except ValueError:
            pass
        else:
            raise AssertionError("suppressed frame generated an item")
    finally:
        db.run("DELETE FROM word_fit_reports WHERE frame=?", ident)
        db.run("DELETE FROM word_suppress WHERE frame=?", ident)


def test_study_policy(client: TestClient) -> None:
    learner = code()
    h = {"X-Learner": learner}
    sat = words.content()["sat"]
    for w in sat[:90]:
        s = words.state(learner, w["slug"])
        s["box"] = 2
        s["reps"] = 1
        s["right"] = 1
        s["due"] = (words.local_day() - dt.timedelta(days=2)).isoformat()
        with db.atomic() as c:
            words._upsert_state(c, s)
    lib = ok(client.get("/api/words", headers=h))
    assert lib["debt"]["spread"] == 23 and lib["debt"]["due"] == 90
    from server import prefs
    prefs.put(learner, {"words_spread": (words.local_day() + dt.timedelta(days=4)).isoformat()})
    today_slugs = words.deck(learner, "today", n=200)
    due_count = sum(words.state(learner, s)["due"] <= words.local_day().isoformat() for s in today_slugs
                    if words.state(learner, s)["due"])
    assert due_count <= 23 and all(words.state(learner, s)["box"] for s in today_slugs)
    db.run("UPDATE learners SET exam_date=? WHERE id=?",
           (words.local_day() + dt.timedelta(days=45)).isoformat(), learner)
    finish = ok(client.get("/api/words/insights", headers=h))["finish"]
    assert len(finish["chips"]) == 7
    expected_auto = min(40, max(5, (finish["left"]["core"] + finish["left"]["logics"] + 34) // 35))
    assert finish["chips"][-1]["daily"] == expected_auto
    mix = use(client, learner, "/api/words/run", {"mode": "mix", "deck": {"source": "today"}, "box": 5})
    stored = json.loads(db.one("SELECT questions FROM sessions WHERE id=?", mix["id"])["questions"])
    assert all(a.get("word") != b.get("word") for a, b in zip(stored, stored[1:]))
    first = mix["next"]
    if first.get("step"):
        use(client, learner, f"/api/words/run/{mix['id']}/answer", {"item_id": first["item_id"], "answer": 0})
    answer = "know" if first["kind"] in {"card", "fix"} else 0
    end = use(client, learner, f"/api/words/run/{mix['id']}/answer",
              {"item_id": first["item_id"], "answer": answer, "ms": 300_000})
    assert end["next"] is None and end["summary"]
    assert words.today_summary(learner)["done"]

    stubborn = code()
    for _ in range(4):
        words.grade(stubborn, "elusive", False, "cards", "card", given="illusory")
    assert next(w for w in words.library(stubborn)["words"] if w["slug"] == "elusive")["stubborn"]
    hooked = ok(client.put("/api/words/elusive/hook", json={"text": "e-LUSive: it gets loose"},
                           headers={"X-Learner": stubborn}))
    assert hooked["hook"]
    cards = use(client, stubborn, "/api/words/run", {"mode": "cards", "deck": {"source": "words", "words": ["elusive"]}, "count": 1})
    assert cards["next"]["kind"] == "fix" and cards["next"]["back"]["hook"] == hooked["hook"]
    assert cards["next"]["picks"]
    probable = code()
    words.place(probable, "mitigate", "probably")
    assert words.state(probable, "mitigate")["box"] == 0
    assert "mitigate" not in words.deck(probable, "new", n=200)
    assert "mitigate" in words.deck(probable, "today", n=200)
    proved = words.grade(probable, "mitigate", True, "quiz", "incontext")
    assert proved["box"]["after"] == 4 and words.state(probable, "mitigate")["proven"]
    words.place(probable, "bolster", "probably")
    failed = words.grade(probable, "bolster", False, "quiz", "incontext")
    assert failed["box"]["after"] == 0 and words.state(probable, "bolster")["placed"] == 0
    assert words.deck(probable, "new", n=1) == ["bolster"]
    trap_run = use(client, probable, "/api/words/run", {"mode": "quiz", "deck": {"source": "trap", "value": "reversed"}, "count": 2})
    trapped = json.loads(db.one("SELECT questions FROM sessions WHERE id=?", trap_run["id"])["questions"])
    assert all("reversed" in q["traps"] for q in trapped)


def test_external_words(client: TestClient) -> None:
    learner = code()
    h = {"X-Learner": learner}
    outside = ok(client.post("/api/words/outside", json={"choices": ["refute", "question", "support", "describe"],
                                                      "key": "question", "picked": "refute"}, headers=h))
    assert outside["trap"] == "too_strong" and outside["list"]
    assert words.state(learner, "refute")["saved"] and words.state(learner, "question")["saved"]
    listed = db.one("SELECT words FROM word_lists WHERE learner=? AND name=?", learner, outside["list"])
    assert len(json.loads(listed["words"])) == 4
    old_own = db.one("SELECT COUNT(*) n FROM my_words WHERE learner=?", learner)["n"]
    imported = ok(client.post("/api/words/outside", json={"choices": ["mitigate", "bolster", "fuzzleabc", "quizzleabc"],
                                                       "key": "mitigate", "picked": "fuzzleabc",
                                                       "label": "Unknown Words"}, headers=h))
    assert imported["trap"] == "not_classified"
    assert db.one("SELECT COUNT(*) n FROM my_words WHERE learner=?", learner)["n"] == old_own + 2
    if outside["run"] is None:
        assert not any(f["need"].get("pins") == "intensity" and words._servable(f)
                       for f in words.content()["frames"].values())
    else:
        twins = json.loads(db.one("SELECT questions FROM sessions WHERE id=?", outside["run"]["id"])["questions"])
        assert all("too_strong" in q["traps"] for q in twins)


def test_rw_migration() -> None:
    from server import deps
    columns = {r["name"]: r for r in db.conn().execute("PRAGMA table_info(attempts)")}
    named = words.RW_TO_ATTEMPTS.split("INSERT INTO attempts(", 1)[1].split(")", 1)[0].split(",")
    assert all(not col["notnull"] or col["dflt_value"] is not None or name in named
               for name, col in columns.items() if name != "id")
    assert deps.subject_of("rw.words_in_context") == deps.subject_of("rw.transitions") == "rw"
    expected = db.one("SELECT COUNT(*) n FROM word_reviews WHERE subject='rw' AND template IS NOT NULL"
                      " AND correct IS NOT NULL")["n"]
    with db.atomic() as c:
        c.execute("SAVEPOINT s9_migration")
        before = c.execute("SELECT COUNT(*) FROM attempts").fetchone()[0]
        c.execute(words.RW_TO_ATTEMPTS)
        after = c.execute("SELECT COUNT(*) FROM attempts").fetchone()[0]
        assert after - before == expected
        c.execute("ROLLBACK TO s9_migration")
        c.execute("RELEASE s9_migration")


def check(client: TestClient) -> None:
    previous = os.environ.pop("SATF_WORDS_UNREVIEWED", None)
    try:
        tests = (test_content, test_core, test_library, test_runs, test_placement_and_own,
                 test_daily_print_offline, test_crowd_guard, test_study_policy,
                 test_external_words, test_rw_migration)
        for test in tests:
            test(client) if test.__code__.co_argcount else test()
            print(test.__name__, "PASS")
    finally:
        if previous is None:
            os.environ.pop("SATF_WORDS_UNREVIEWED", None)
        else:
            os.environ["SATF_WORDS_UNREVIEWED"] = previous
    print("S9 server checks passed")


def main() -> None:
    with TestClient(app) as client:
        check(client)


if __name__ == "__main__":
    main()
