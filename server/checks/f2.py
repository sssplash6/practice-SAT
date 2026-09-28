"""F2 · Shell: §2.12 F2's acceptance, read with §2.13, R1, R29 and v2-decisions 5 (no classes).

check(c), run by test_flow.py: /api/shell's keys, one streak (Shell 7, 8), resume, retired
codes, the parts registry, a quick sitting never offered as Resume (Shell 12).

    PYTHONPATH=. python3 server/checks/f2.py [port]

runs the browser half against its own server (default port 8012, a scratch database) in
headless Chromium: the sidebar and section mapping, the rail, the 900px overlay, the phone
tabs and menu sheet, the Review and Today metas, the account-menu keyboard, the palette,
the quick sheet, theme, the offline, retired and storage banners, labels, the skip link and Esc (Shell 1-6, 10-12,
22, 32, 36), with no console errors on the way. Parts that need F5's drill engine (the
palette's tiers and types, the quick sheet's own sitting) run when /api/types is served.
"""

from __future__ import annotations

import datetime as dt
import json
import secrets
import sys
from unittest.mock import patch

from server import api_shell, compete, db, next as next_actions, plan, practice

KEYS = {"me", "streak", "best_streak", "today", "plan", "tested_today", "mistakes", "saved", "challenge", "resume",
        "newest_report", "report_replies", "new", "prefs", "pref_source", "stage", "next", "goals", "inbox",
        "registration", "device", "dates", "spares", "review", "words", "answered", "has", "report"}


def check(c) -> None:
    H = {"X-Learner": "a:v2revshellA", "X-Tz": "0"}
    s = c.get("/api/shell", headers=H).json()
    assert KEYS <= set(s), KEYS - set(s)
    assert "assignments" not in s and "role" not in s["me"], "no classes (v2-decisions 5)"
    assert s["answered"] == 0 and s["resume"] is None and s["plan"] is None and s["prefs"]["theme"] == "light"
    assert len(s["me"]["domains"]["math"]) == 4 and s["me"]["avatar"]["kind"] == "mark"

    d = c.post("/api/drill", headers=H, json={"topics": ["circles"], "count": 3}).json()
    q = c.post(f"/api/drill/{d['id']}/next", headers=H).json()["question"]
    c.post(f"/api/drill/{d['id']}/answer", headers=H, json={"question_id": q["id"], "answer": 0})
    c.put("/api/me", headers=H, json={"exam_date": "2099-11-07", "minutes": 45, "days": "1111111"})
    s = c.get("/api/shell", headers=H).json()
    me = c.get("/api/me", headers=H).json()
    assert s["answered"] == 1 and s["today"]["questions"] == 1
    assert s["streak"] == me["days"]["streak"] == 1, "one streak"
    assert s["resume"]["id"] == d["id"] and s["resume"]["href"].endswith(d["id"])
    assert s["plan"]["per_session"] == 28 and s["today"]["goal"] == {"minutes": 45, "questions": 28}
    assert all(0 <= x <= 1 for x in s["me"]["domains"]["math"])

    # Shell 12: a quick sitting with an answer is never offered as Resume
    Q = {"X-Learner": "a:v2revshellquick", "X-Tz": "0"}
    qd = c.post("/api/drill", headers=Q, json={"topics": ["circles"], "count": None, "source": "quick"}).json()
    c.post(f"/api/drill/{qd['id']}/answer", headers=Q, json={"question_id": qd["question"]["id"], "answer": 0})
    assert c.get("/api/shell", headers=Q).json()["resume"] is None, "a quick sitting is never Resume"

    db.run("INSERT OR IGNORE INTO retired(code, \"into\", at) VALUES ('a:v2revshellgone', NULL, 'now')")
    assert c.get("/api/shell", headers={"X-Learner": "a:v2revshellgone"}).json() == {"retired": True}
    assert c.get("/api/shell", headers={"X-Learner": "d:" + "0" * 32}).json() == {"retired": True}

    def fake(module, name):
        if name == "shell_part" and module == "words":
            return lambda learner, tz: {"words": {"due": 12}, "new": {"achievements": [{"id": "x"}]}}
        if name == "shell_part" and module == "plan":
            return lambda learner, tz: 1 / 0
        return None
    with patch.object(api_shell, "part", fake), patch.object(api_shell.log, "exception") as logged:
        s = c.get("/api/shell", headers=H).json()
    assert s["words"] == {"due": 12} and s["new"]["achievements"] == [{"id": "x"}], "a part merges in"
    assert s["plan"]["per_session"] == 28 and logged.called, "a failing part is logged and the rest stands"
    print("ok  /api/shell: every key, one streak, resume (never a quick sitting), retired codes, and parts merged")

    # F6's reports.shell() lands as report_replies and `report`, never over newest_report
    def reports(module, name):
        if module == "reports" and name == "shell":
            return lambda learner: {"newest_report": {"id": 7, "unread": True}, "report_replies": 1}
        return None
    with patch.object(api_shell, "part", reports):
        s2 = c.get("/api/shell", headers=H).json()
    assert s2["report_replies"] == 1 and s2["report"] == {"id": 7, "unread": True}
    assert s2["newest_report"] == s["newest_report"], "the newest sitting stays Results' New dot"
    assert all(isinstance(v, bool) for v in s["has"].values()) and {"next", "pair", "match", "question"} <= set(s["has"])

    # the palette's index: every type once, reasons as [norm, label?], gzipped when asked
    r = c.get("/api/shell/catalog", headers={"Accept-Encoding": "gzip"})
    cat = r.json()
    assert r.status_code == 200 and set(cat) == {"types", "cb"}
    if api_shell.part("api_bank", "types"):           # F5's catalogue is on this branch
        tpl = [t[0] for t in cat["types"]]
        assert len(tpl) == len(set(tpl)) > 300 and all(len(t) == 5 and all(1 <= len(x) <= 2 for x in t[3]) for t in cat["types"])
    print("ok  /api/shell: F6's report hook, has, and the slim type catalogue")

    # Shell 8: plan days 1111100 and answers on the six weekdays up to today: 6 everywhere
    L = "a:v2revshellsix"
    db.ensure_learner(L)
    db.run("UPDATE learners SET plan='p1', days='1111100' WHERE id=?", L)
    day, n = dt.datetime.now(dt.timezone.utc).date(), 0
    while n < 6:
        if day.weekday() < 5:
            db.run("INSERT INTO attempts (learner, template, seed, topic, difficulty, fmt, correct, at)"
                   " VALUES (?, 'lin.evaluate', ?, 'linear_functions', 'easy', 'mcq', 1, ?)", L, 500 + n, f"{day}T12:00:00+00:00")
            n += 1
        day -= dt.timedelta(days=1)
    S = {"X-Learner": L, "X-Tz": "0"}
    got = (c.get("/api/shell", headers=S).json()["streak"], c.get("/api/me", headers=S).json()["days"]["streak"],
           c.get("/api/today", headers=S).json()["days"]["streak"])
    assert got == (6, 6, 6), got
    print("ok  /api/shell: one streak of 6 across a rest weekend in shell, me and today")

    first = "a:f2next" + secrets.token_hex(6)
    FH = {"X-Learner": first, "X-Tz": "0"}
    fresh = c.get("/api/next", headers=FH)
    assert fresh.status_code == 200, fresh.text
    assert [x["kind"] for x in fresh.json()["items"][:2]] == ["start", "diagnostic"]
    assert fresh.json()["items"][0]["start"]["body"] == {"source": "start"}
    assert c.get("/api/shell", headers=FH).json()["next"] == fresh.json()["items"]
    assert c.get("/api/shell", headers=FH).json()["has"]["next"]

    learner = "a:f2next" + secrets.token_hex(6)
    NH = {"X-Learner": learner, "X-Tz": "0"}
    now = dt.datetime.now(dt.timezone.utc)
    day = now.date().isoformat()
    template = practice.catalogue()["by_topic"]["circles"][0]
    db.ensure_learner(learner)
    db.run("INSERT INTO attempts(learner,template,seed,topic,difficulty,fmt,correct,at)"
           " VALUES (?,?,?,?,?,?,?,?)", learner, template, 1, "circles", "medium", "mcq", 1,
           now.isoformat())
    assert c.get("/api/next", headers=NH).json()["items"][0]["kind"] == "start"
    with db.transaction():
        for seed in range(2, 9):
            db.run("INSERT INTO attempts(learner,template,seed,topic,difficulty,fmt,correct,at)"
                   " VALUES (?,?,?,?,?,?,?,?)", learner, template, seed, "circles", "medium",
                   "mcq", 1, now.isoformat())
    db.run("INSERT INTO traps(learner,template,norm,reason,label,topic,hits,owed,opened,last,closed,closed_how,due)"
           " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", learner, template, "diameter", "diameter",
           "Used diameter as radius", "circles", 2, 0, now.isoformat(), now.isoformat(),
           now.isoformat(), "fixed", day)
    db.run("INSERT INTO traps(learner,template,norm,reason,label,topic,hits,owed,opened,last)"
           " VALUES (?,?,?,?,?,?,?,?,?,?)", learner, template, "radius", "radius",
           "Used radius as diameter", "circles", 3, 2, now.isoformat(), now.isoformat())
    listed = c.get("/api/next", headers=NH)
    assert listed.status_code == 200, listed.text
    assert [x["kind"] for x in listed.json()["items"][:2]] == ["checks", "redo"]
    assert listed.json()["items"][0]["pts"] is None
    assert listed.json()["items"][0]["start"]["body"]["pool"] == "checks"
    assert c.get("/api/shell", headers=NH).json()["next"] == listed.json()["items"][:3]
    with patch.object(compete, "due_today", wraps=compete.due_today) as contests_due, \
         patch.object(plan, "today_summary", wraps=plan.today_summary) as plan_today:
        assert c.get("/api/shell", headers=NH).status_code == 200
    assert contests_due.call_count == 1 and plan_today.call_count == 1, (
        contests_due.call_count, plan_today.call_count)

    original_part = next_actions.deps.part
    def with_plan(module, name):
        if (module, name) == ("plan", "today_summary"):
            return lambda *_: {"tasks": [{"id": "today:checks", "kind": "recheck", "title": "Check-ins",
                                          "counted": True, "status": "todo", "count": 2,
                                          "start": {"path": "/api/drill", "body": {"pool": "checks"}}}],
                              "tasks_done": 0, "tasks_counted": 1}
        return original_part(module, name)
    with patch.object(next_actions.deps, "part", side_effect=with_plan):
        planned = next_actions.queue(learner, 0)
    assert sum(x.get("start", {}).get("body", {}).get("pool") == "checks" for x in planned) == 1
    assert "also in today's plan" in planned[0]["reason"]
    assert next_actions.resolve_drill(learner, {"source": "next", "box": 15})["count"] is None
    assert next_actions.resolve_drill(learner, {"source": "next", "box": 15})["segments"]
    db.run("UPDATE learners SET exam_date=? WHERE id=?",
           (now.date() + dt.timedelta(days=1)).isoformat(), learner)
    assert c.get("/api/next", headers=NH).json()["items"][0]["title"].startswith("Rest")
    print("ok  /api/next: start, check-in priority, plan dedupe, time box and exam-eve rest")


# ------------------------------------------------------------------ the browser half
EXE = ("/Users/workingmyassof/Library/Caches/ms-playwright/chromium_headless_shell-1243/"
       "chrome-headless-shell-mac-arm64/chrome-headless-shell")
DARK, LIGHT = "rgb(26, 25, 23)", "rgb(255, 255, 255)"
# Shell 1 as amended (R1, §2.13): the sidebar's rows in order, Profile being R1's ninth item
SIDE = ["Search", "Quick", "Today", "Practice", "Review", "Words", "Tests", "Plan", "Results", "Compete",
        "Profile", "Help & FAQ", "Send feedback", "user"]
LIT = {"/": "today", "/practice/": "practice", "/mistakes/": "review", "/tests/": "tests", "/plan/": "plan",
       "/results/": "results", "/results/report/": "results", "/challenge/": "compete", "/diagnostic/": "tests",
       "/me/": "me"}
SHEET = ["Review", "Words", "Compete", "Settings", "Sign in", "Sign in another device", "Help & FAQ",
         "Send feedback", "Leave this device…"]


def browser(port: int = 8012) -> None:
    import os
    import pathlib
    import sqlite3
    import subprocess
    import tempfile
    import time

    import httpx
    from playwright.sync_api import sync_playwright

    root = pathlib.Path(__file__).resolve().parents[2]
    tmp = tempfile.TemporaryDirectory()
    dbf = pathlib.Path(tmp.name) / "f2.db"
    env = {**os.environ, "SATF_DB": str(dbf), "PYTHONPATH": str(root)}
    srv = subprocess.Popen([sys.executable, "-m", "uvicorn", "server.app:app", "--port", str(port), "--log-level", "warning"],
                           cwd=root, env=env)
    base = f"http://localhost:{port}"
    http = httpx.Client(base_url=base, timeout=30)
    try:
        for _ in range(120):
            try:
                if http.get("/api/shell", headers={"X-Learner": "a:f2browserping"}).status_code == 200:
                    break
            except httpx.TransportError:
                pass
            time.sleep(0.5)
        else:
            raise AssertionError("the server did not start")
        sql = sqlite3.connect(dbf, timeout=10)
        with sync_playwright() as p:
            walk(p.chromium.launch(executable_path=EXE), base, http, sql)
    finally:
        srv.terminate()
        srv.wait(10)
        tmp.cleanup()


def walk(b, base, http, sql) -> None:
    import secrets

    def code():
        return "a:" + "".join(secrets.choice("0123456789abcdefghijklmnopqrstuvwxyz") for _ in range(24))

    def api(L, method, path, body=None):
        r = http.request(method, path, headers={"X-Learner": L, "X-Tz": "0"}, json=body)
        assert r.status_code < 400, (method, path, r.status_code, r.text[:200])
        return r.json()

    def stored(sid):
        return json.loads(sql.execute("SELECT questions FROM sessions WHERE id=?", (sid,)).fetchone()[0])

    def keyed(q, right):
        if q["type"] == "mcq":
            k = "ABCD".index(q["answer"])
            return k if right else next(i for i in range(4) if i != k and q["reasons"][i])
        return q["answer"] if right else "-99999"

    def answers(L, topic, right, wrong):
        d = api(L, "POST", "/api/drill", {"topics": [topic], "count": right + wrong})
        for i in range(right + wrong):
            cur = stored(d["id"])[-1]
            api(L, "POST", f"/api/drill/{d['id']}/answer", {"question_id": cur["id"], "answer": keyed(cur, i < right)})
            if i < right + wrong - 1:
                api(L, "POST", f"/api/drill/{d['id']}/next")
        api(L, "POST", f"/api/drill/{d['id']}/finish")

    f5 = http.get("/api/types", headers={"X-Learner": "a:f2browserping"}).status_code == 200
    errors = []

    def page(ctx):
        pg = ctx.new_page()
        pg.on("console", lambda m: m.type == "error" and "404 (Not Found)" not in m.text
              and errors.append(f"{pg.url}: {m.text} {m.location.get('url', '')}"))
        pg.on("pageerror", lambda e: errors.append(f"{pg.url}: {e}"))
        return pg

    def context(L, w=1280, hgt=900):
        ctx = b.new_context(viewport={"width": w, "height": hgt}, has_touch=w < 760, is_mobile=w < 760)
        ctx.add_init_script(f"try {{ localStorage.getItem('satf.learner') || localStorage.setItem('satf.learner', {json.dumps(L)}) }} catch (e) {{}}")
        return ctx

    def go(pg, path):
        pg.goto(base + path, wait_until="networkidle")
        pg.wait_for_function("() => !!(window.UI && UI.shellData && UI.shellData()) || !document.querySelector('.side')", timeout=10000)
        pg.wait_for_timeout(150)

    js_rows = """() => [...document.querySelectorAll('.side > .side-search, .side > .side-quick, .side-item, .side-foot > *, .side > .side-user')]
        .filter(e => e.offsetWidth).map(e => e.matches('.side-user') ? 'user' : e.querySelector('.side-text').textContent)"""
    def settle(pg):
        pg.wait_for_function("() => document.getAnimations().every(a => a.playState !== 'running')")

    meta = lambda pg, id: pg.eval_on_selector(f".side-item[data-id={id}] .side-meta", "e => e.textContent.trim()")

    # A: a 45-minute plan, 12 answered today (3 of them wrong), a finished section
    A, NEW = code(), code()
    exam = next(x["day"] for x in api(A, "GET", "/api/shell")["dates"] if x["day"] > str(dt.date.today()))
    api(A, "PUT", "/api/me", {"exam_date": exam, "minutes": 45, "days": "1111111"})
    answers(A, "circles", 5, 2)
    answers(A, "percentages", 4, 1)
    shellA = api(A, "GET", "/api/shell")
    assert shellA["today"]["questions"] == 12 and shellA["plan"]["per_session"] == 28, shellA["today"]
    opened = shellA["review"]["open"]
    assert opened >= 1

    # ---- Shell 1, 5, 6: the sidebar at 1280x900, its rows, one current item, the metas
    ctx = context(A)
    pg = page(ctx)
    for path, lit in LIT.items():
        go(pg, path)
        assert pg.eval_on_selector(".side", "e => e.getBoundingClientRect().width") == 248, path
        assert pg.evaluate(js_rows) == SIDE, (path, pg.evaluate(js_rows))
        cur = pg.eval_on_selector_all(".side [aria-current=page]", "es => es.map(e => e.dataset.id || e.textContent)")
        assert cur == [lit], (path, cur)
        assert not pg.query_selector("a[href^='/class'], a[href^='/join']") and "class" not in pg.inner_text(".side").lower(), path
    assert meta(pg, "today") == "12/28", meta(pg, "today")
    assert f"{opened} open" in meta(pg, "review"), meta(pg, "review")
    assert pg.is_visible(".now-strip") and "TODAY" in pg.inner_text(".now-strip").upper(), "medium height: the Today card is in the Now strip"
    print("ok  sidebar: 248px, R1's rows in order, no Class, one current item per page, Today 12/28, Review's open count")

    # ---- Shell 36: labels, the skip link, Esc returns focus (palette, quick sheet, ? sheet)
    go(pg, "/")
    bare = pg.evaluate("""() => [...document.querySelectorAll('#bar button, #bar a, #tabs button, #tabs a')]
        .filter(e => !e.textContent.trim() && !e.getAttribute('aria-label') && !e.getAttribute('aria-labelledby')).map(e => e.outerHTML.slice(0, 80))""")
    assert not bare, bare
    pg.keyboard.press("Tab")
    assert pg.evaluate("document.activeElement.className") == "skip" and pg.evaluate("document.activeElement.textContent") == "Skip to content"
    pg.keyboard.press("Enter")
    assert pg.evaluate("document.activeElement.id") == "main"
    for trigger, dialog in ((".side-search", "dialog.palette[open]"), (".side-quick", "dialog[open]")):
        pg.click(trigger)
        pg.wait_for_selector(dialog)
        pg.wait_for_timeout(300)
        pg.keyboard.press("Escape")
        pg.wait_for_selector("dialog[open]", state="detached", timeout=3000) if pg.query_selector("dialog[open]") else None
        pg.wait_for_timeout(200)
        assert not pg.query_selector("dialog[open]"), trigger
        assert pg.evaluate(f"document.activeElement === document.querySelector('{trigger}')"), (trigger, pg.evaluate("document.activeElement.outerHTML.slice(0, 80)"))
    pg.keyboard.press("?")
    pg.wait_for_selector("dialog[open]")
    assert "Keyboard shortcuts" in pg.inner_text("dialog[open]") and "Go to Review" in pg.inner_text("dialog[open]")
    pg.keyboard.press("Escape")
    pg.wait_for_timeout(300)
    assert not pg.query_selector("dialog[open]")
    print("ok  labels on every icon button, the skip link first and into main, Esc closes and returns focus")

    # ---- Shell 10: the account menu on the keyboard
    pg.focus(".side-user")
    pg.keyboard.press("Enter")
    pg.wait_for_selector("[role=menu]")
    assert pg.get_attribute(".side-user", "aria-expanded") == "true"
    seen = []
    for _ in range(3):
        pg.keyboard.press("ArrowDown")
        seen.append(pg.evaluate("[document.activeElement.getAttribute('role'), document.activeElement.textContent.trim()]"))
    assert all(r and r.startswith("menuitem") for r, _ in seen) and len({t for _, t in seen}) == 3, seen
    # U26 6: End reaches the last item; the header holds nothing focusable; Display is a group
    pg.keyboard.press("End")
    assert pg.evaluate("document.activeElement.textContent.trim()") == "Leave this device…"
    assert not pg.evaluate("""() => { const m = document.querySelector('[role=menu]');
        return [...m.querySelectorAll('a, button, input, [tabindex]')].some(e => !e.closest('[role^=menuitem]') && !e.matches('[role^=menuitem]')) }""")
    dark = "[role=menu] [role=group] [role=menuitemcheckbox]:has-text('Dark theme')"
    pg.focus(dark)
    with pg.expect_response(lambda r: r.url.endswith("/api/me") and r.request.method == "PUT"):
        pg.keyboard.press(" ")
    assert pg.is_visible("[role=menu]") and pg.get_attribute(dark, "aria-checked") == "true"
    with pg.expect_response(lambda r: r.url.endswith("/api/me") and r.request.method == "PUT"):
        pg.keyboard.press(" ")
    assert pg.get_attribute(dark, "aria-checked") == "false"
    pg.focus("[role=menu] [role=group] [role=menuitem]:has-text('Keyboard shortcuts')")
    pg.keyboard.press("Enter")
    pg.wait_for_selector("dialog[open]:has-text('Keyboard shortcuts')")
    pg.keyboard.press("Escape")
    pg.wait_for_timeout(300)
    pg.focus(".side-user")
    pg.keyboard.press("Enter")
    pg.wait_for_selector("[role=menu]")
    pg.keyboard.press("Escape")
    pg.wait_for_timeout(200)
    assert not pg.is_visible("[role=menu]") and pg.evaluate("document.activeElement.classList.contains('side-user')")
    print("ok  account menu: Enter opens, ArrowDown walks, End reaches Leave this device, Space toggles Dark in place,"
          " Keyboard shortcuts opens the ? sheet, Esc closes onto the user card")

    # ---- Shell 11: the palette parses a set; a type row starts that type
    mod = "Meta" if pg.evaluate("/Mac|iPhone|iPad/.test(navigator.platform)") else "Control"
    pg.keyboard.press(mod + "+k")
    pg.wait_for_selector("dialog.palette[open] input")
    pg.keyboard.type("circles hard 5")
    pg.wait_for_timeout(400)
    first = pg.inner_text("dialog.palette [role=option]")
    assert "Circles" in first and "Hard" in first and "5 questions" in first, first
    with pg.expect_navigation(url="**/practice/session/?id=*"):
        pg.keyboard.press("Enter")
    sid = pg.url.split("id=")[1]
    cfg = json.loads(sql.execute("SELECT cfg FROM sessions WHERE id=?", (sid,)).fetchone()[0])
    got = api(A, "GET", f"/api/drill/{sid}")
    assert got["topics"] == ["circles"] and got["total"] == 5, got
    if f5:
        assert cfg.get("tiers") == ["hard"], cfg
        go(pg, "/")
        pg.keyboard.press(mod + "+k")
        pg.wait_for_selector("dialog.palette[open] input")
        pg.keyboard.type("central angle")
        pg.wait_for_function("() => [...document.querySelectorAll('dialog.palette .palette-group')].some(g => g.textContent === 'Question types')")
        opt = pg.evaluate("""() => { const o = document.querySelector('dialog.palette [role=option][aria-selected=true]');
            return [o.closest('[role=group]').textContent.slice(0, 20), o.textContent] }""")
        assert opt[0].startswith("Question types"), opt
        with pg.expect_navigation(url="**/practice/session/?id=*"):
            pg.keyboard.press("Enter")
        sid = pg.url.split("id=")[1]
        pg.wait_for_timeout(300)
        keys = {q["key"] for q in stored(sid)}
        tpl = json.loads(sql.execute("SELECT cfg FROM sessions WHERE id=?", (sid,)).fetchone()[0]).get("templates")
        assert tpl and len(tpl) == 1 and keys == set(tpl), (keys, tpl)
    print(f"ok  palette: 'circles hard 5' starts that set{', a Question types row starts its type' if f5 else ' (types: F5 not here)'}")

    # the parser itself (P15)
    parsed = pg.evaluate("""() => [UI.parseSet('circles hard 5 timed').body, UI.parseSet('trig percent 10').body,
        UI.parseSet('sohcahtoa endless grid').body, UI.parseSet('15 min').body, UI.parseSet('easy medium mc').body]""")
    assert parsed[0] == {"topics": ["circles"], "tiers": ["hard"], "count": 5, "timed": True, "source": "palette"}, parsed[0]
    assert parsed[1]["topics"] == ["right_triangles_and_trigonometry", "percentages"] and parsed[1]["count"] == 10, parsed[1]
    assert parsed[2]["count"] is None and parsed[2]["formats"] == ["spr"], parsed[2]
    assert parsed[3] == {"source": "next", "box": 15}, parsed[3]
    assert parsed[4]["tiers"] == ["easy", "medium"] and parsed[4]["formats"] == ["mcq"], parsed[4]
    print("ok  UI.parseSet: skills, aliases, counts, endless, tiers, timed, formats and time boxes")

    # ---- Shell 2: collapse to the rail, kept on reload, tooltips; [ expands
    go(pg, "/")
    pg.click(".side-toggle")
    pg.wait_for_timeout(200)
    assert pg.eval_on_selector(".side", "e => e.getBoundingClientRect().width") == 68
    assert pg.evaluate("localStorage.getItem('satf.rail')") == "1"
    go(pg, "/")
    assert pg.eval_on_selector(".side", "e => e.getBoundingClientRect().width") == 68, "the rail is kept"
    pg.focus(".side-item[data-id=review]")
    pg.wait_for_selector("[role=tooltip]", state="visible")
    assert "Review" in pg.inner_text("[role=tooltip]")
    pg.evaluate("document.activeElement.blur()")
    pg.keyboard.press("[")
    pg.wait_for_timeout(300)
    assert pg.eval_on_selector(".side", "e => e.getBoundingClientRect().width") == 248 and pg.evaluate("localStorage.getItem('satf.rail')") is None
    ctx.close()

    ctx.close()
    print("ok  rail: 68px, kept in satf.rail, tooltips on focus, [ expands")

    # ---- U26 1, 2: the height budget; each fact once (no questions bar, no "28 q")
    fits = """() => { const s = document.querySelector('.side'), nav = document.querySelector('.side-nav');
        const out = [...document.querySelectorAll('.side-item')].filter(e => { const r = e.getBoundingClientRect(); return r.top < 0 || r.bottom > innerHeight; });
        return [out.map(e => e.dataset.id), s.scrollHeight === s.clientHeight, nav.scrollHeight > nav.clientHeight] }"""
    for w, hgt in ((1366, 657), (1440, 790), (1280, 900), (1280, 500), (1920, 1100), (1366, 470)):
        ctx = context(A, w, hgt)
        pg = page(ctx)
        go(pg, "/results/")
        out, whole, scrolls = pg.evaluate(fits)
        if hgt >= 480:
            assert not out and whole and not scrolls, (w, hgt, out, whole, scrolls)
        else:
            active = pg.eval_on_selector(".side-item[aria-current=page]", "e => { const r = e.getBoundingClientRect(); return r.top >= 0 && r.bottom <= innerHeight }")
            assert scrolls and active, (w, hgt, scrolls, active)
        plan = meta(pg, "plan")
        assert not plan or not plan.endswith(" q"), plan
        if hgt >= 1100:
            assert pg.is_visible(".side .side-day") and not pg.is_visible(".now-strip"), "tall: the Today card is in the sidebar"
            tall = pg.evaluate("() => [...document.querySelectorAll('.side > *')].filter(e => e.offsetWidth).map(e => e.className)")
            assert tall.index("side-day") == tall.index("side-nav") + 1, tall
        card = pg.inner_text(".side .side-day" if hgt >= 1100 else ".now-strip")
        assert "of 28 questions" not in card and meta(pg, "today") == "12/28", card
        ctx.close()
    print("ok  height budget at 1366x657, 1440x790, 1280x900, 1280x500 and 1920x1100; 1366x470 scrolls to the active item; each fact once")

    # ---- Shell 3: 900px wide is the rail; the toggle opens the sidebar over a scrim; Esc closes
    ctx = context(A, 900, 800)
    pg = page(ctx)
    go(pg, "/plan/")
    assert pg.eval_on_selector(".side", "e => e.getBoundingClientRect().width") == 68
    pg.click(".side-mark")
    pg.wait_for_timeout(250)
    assert pg.eval_on_selector(".side", "e => e.getBoundingClientRect().width") == 248 and pg.is_visible(".scrim")
    pg.keyboard.press("Escape")
    pg.wait_for_timeout(250)
    assert pg.eval_on_selector(".side", "e => e.getBoundingClientRect().width") == 68 and not pg.query_selector(".scrim")
    ctx.close()
    print("ok  900px: the rail by default, the sidebar over a scrim, Esc closes it")

    # ---- Shell 4, 5: the phone
    for L, chip in ((A, True), (NEW, False)):
        ctx = context(L, 390, 844)
        pg = page(ctx)
        for path in ("/", "/me/", "/me/settings/", "/help/", "/signin/", "/share/?t=x", "/practice/", "/results/"):
            go(pg, path)
            assert pg.evaluate("document.documentElement.scrollWidth") <= 390, path
        tabs = pg.eval_on_selector_all("#tabs a", "es => es.map(e => e.querySelector('span').textContent)")
        assert tabs == ["Today", "Practice", "Tests", "Plan", "Results"], tabs
        assert pg.is_visible(".pbar-chip") == chip and (not chip or str(opened) in pg.inner_text(".pbar-chip"))
        pg.click(".pbar-me")
        pg.wait_for_selector("dialog.more[open]")
        rows = pg.eval_on_selector_all("dialog.more .more-row > span:not(.more-meta), dialog.more .more-foot span:not(.more-meta)", "es => es.map(e => e.textContent)")
        missing = [x for x in SHEET if x not in rows]
        assert not missing and pg.query_selector("dialog.more a.more-head[href='/me/']"), (missing, rows)
        assert "class" not in pg.inner_text("dialog.more").lower()
        pg.keyboard.press("Escape")
        pg.wait_for_timeout(250)
        assert not pg.query_selector("dialog.more") and pg.evaluate("document.activeElement.classList.contains('pbar-me')")
        ctx.close()
    # U26 5: at 390 and 360 the grip opens the sheet with Review in view; hold Practice for its shortcuts
    for w, hgt in ((390, 844), (360, 740)):
        ctx = context(A, w, hgt)
        pg = page(ctx)
        go(pg, "/plan/")
        assert pg.evaluate("[document.documentElement.scrollWidth <= innerWidth, document.querySelector('.pbar').scrollWidth <= document.querySelector('.pbar').clientWidth]") == [True, True], w
        pg.click(".tabs-grip")
        pg.wait_for_selector("dialog.more[open]")
        settle(pg)                         # the sheet slides up; measure where it comes to rest
        assert pg.eval_on_selector("dialog.more .more-foot a[href='/review/']", "e => { const r = e.getBoundingClientRect(); return r.top >= 0 && r.bottom <= innerHeight && r.left >= 0 && r.right <= innerWidth }"), w
        pg.keyboard.press("Escape")
        pg.wait_for_timeout(250)
        box = pg.eval_on_selector("#tabs a[href='/practice/']", "e => { const r = e.getBoundingClientRect(); return [r.x + r.width / 2, r.y + r.height / 2] }")
        pg.mouse.move(*box)
        pg.mouse.down()
        pg.wait_for_timeout(600)
        pg.mouse.up()
        pg.wait_for_selector("[role=menu]")
        assert "Log a mistake" in pg.inner_text("[role=menu]")
        ctx.close()
    # Shell 5: once every trap closes, the sidebar's Review meta and the phone chip both leave
    sql.execute("UPDATE traps SET closed = '2026-01-01T00:00:00+00:00' WHERE learner=? AND closed IS NULL", (A,))
    sql.commit()
    for w in (1280, 390):
        ctx = context(A, w, 844)
        pg = page(ctx)
        go(pg, "/plan/")
        if w == 1280:
            assert meta(pg, "review") == "", meta(pg, "review")
        else:
            assert not pg.is_visible(".pbar-chip"), pg.inner_text(".pbar-chip")
        ctx.close()
    print("ok  phone: no sideways scroll, the five tabs, the menu sheet's rows, the Review chip only with open mistakes"
          " (both it and the Review meta leave once every trap closes); at 390 and 360 the grip's sheet shows Review, and holding Practice lists Log a mistake")

    # ---- Shell 12: the quick sheet (Q), a sitting only once answered, never Resume
    QL = code()
    ctx = context(QL)
    pg = page(ctx)
    go(pg, "/")
    if f5:
        # closed while its question is still loading, then again once it shows: no sitting either time
        slow = """on => { window._f = window._f || fetch; window.fetch = on ? (u, o) => /\\/api\\/drill$/.test(String(u))
            ? _f(u, o).then(r => new Promise(ok => setTimeout(() => ok(r), 800))) : _f(u, o) : _f }"""
        for early in (True, False):
            pg.evaluate(slow, early)       # the page sees its question 800 ms late
            with pg.expect_response(lambda r: r.url.endswith("/api/drill") and r.request.method == "POST") as drew:
                pg.keyboard.press("q")
            if early:
                pg.wait_for_selector("dialog[open] .skel")
                with pg.expect_response(lambda r: r.url.endswith("/finish")) as fin:
                    pg.keyboard.press("Escape")
            else:
                pg.wait_for_selector("dialog[open] .opts, dialog[open] .grid-in input", timeout=10000)
                with pg.expect_response(lambda r: r.url.endswith("/finish")) as fin:
                    pg.keyboard.press("Escape")
            rows = sql.execute("SELECT id, cfg FROM sessions WHERE learner=? AND json_extract(cfg, '$.source')='quick'", (QL,)).fetchall()
            assert drew.value.ok and fin.value.json() == {"deleted": True} and not rows, ("closing with no answer leaves no quick sitting", early, rows)
            pg.wait_for_timeout(300)
        pg.keyboard.press("q")
        pg.wait_for_selector("dialog[open] .opts, dialog[open] .grid-in input", timeout=10000)
        before = pg.inner_text("dialog[open]")
        if pg.query_selector("dialog[open] .grid-in input"):
            pg.fill("dialog[open] .grid-in input", "1")
            pg.keyboard.press("Enter")
        else:
            pg.keyboard.press("a")
        pg.wait_for_selector("dialog[open] button.pill:has-text('Another')", state="visible")
        assert "1 answered" in pg.inner_text("dialog[open]")
        pg.keyboard.press("Enter")
        pg.wait_for_function("t => !document.querySelector('dialog[open] .skel') && document.querySelector('dialog[open]').innerText !== t", arg=before)
        pg.keyboard.press("Escape")
        pg.wait_for_timeout(700)
        hist = api(QL, "GET", "/api/history")["sessions"]
        assert [x.get("label") for x in hist] == ["Quick questions"], hist
        assert api(QL, "GET", "/api/shell")["resume"] is None
    own = api(QL, "POST", "/api/drill", {"topics": ["circles"], "count": 3})["id"]
    for path in (f"/practice/session/?id={own}", "/test/"):
        go(pg, path)
        assert not pg.query_selector(".side, .side-quick, [aria-label^='Quick']"), path
        pg.keyboard.press("q")
        pg.wait_for_timeout(400)
        assert not pg.query_selector("dialog[open]"), f"Q does nothing on {path}"
    ctx.close()
    said = (": closed mid-load or unanswered it leaves no sitting; Q opens a question, Another loads the next,"
            " history says Quick questions, never Resume;") if f5 else " (its sitting: F5 not here);"
    print(f"ok  quick sheet{said} no Quick and no Q on the session and the test")

    # ---- Shell 22: theme; a fresh page is light; Dark from the account menu; no light flash
    ctx = context(NEW)
    pg = page(ctx)
    go(pg, "/")
    assert pg.evaluate("document.documentElement.hasAttribute('data-theme')") is False
    assert pg.evaluate("getComputedStyle(document.body).backgroundColor") == LIGHT
    pg.click(".side-user")
    with pg.expect_response(lambda r: r.url.endswith("/api/me") and r.request.method == "PUT"):
        pg.click("[role=menu] [role=menuitemcheckbox]:has-text('Dark theme')")
    assert pg.evaluate("getComputedStyle(document.body).backgroundColor") == DARK
    pg = ctx.new_page()                    # no error hooks: the page's own script needs the aborted ui.js
    pg.route("**/assets/ui.js", lambda r: r.abort())
    pg.route("**/assets/kit.js", lambda r: r.abort())
    pg.goto(base + "/practice/", wait_until="load")
    assert pg.evaluate("document.documentElement.dataset.theme") == "dark", "head.js sets the theme before first paint"
    assert pg.evaluate("getComputedStyle(document.body).backgroundColor") == DARK
    assert pg.get_attribute("meta[name=theme-color]", "content") == "#1A1917"
    assert api(NEW, "GET", "/api/me")["profile"]["prefs"]["theme"] == "dark"
    ctx.close()
    print("ok  theme: light by default, Dark from the menu is saved, and head.js paints it before ui.js runs")

    # ---- Shell 32: /api blocked -> the offline banner with Retry now; the nav still works
    ctx = context(A)
    pg = page(ctx)
    pg.route("**/api/**", lambda r: r.abort())
    pg.goto(base + "/practice/", wait_until="load")
    pg.wait_for_selector(".banner:has-text('Can’t reach SAT Freshman')", timeout=8000)
    assert pg.is_visible(".banner button:has-text('Retry now')")
    with pg.expect_navigation(url="**/plan/"):
        pg.click(".side-item[data-id=plan]")
    ctx.close()
    errors[:] = [e for e in errors if "ERR_FAILED" not in e and "Failed to fetch" not in e]
    if not f5:                             # without F5 a quick question has no topic to draw from: a 400, shown as Retry
        errors[:] = [e for e in errors if not ("400 (Bad Request)" in e and e.endswith("/api/drill"))]
    print("ok  offline: the banner and Retry now, and the nav still navigates")

    # ---- Shell 2.11: a retired code and refused localStorage get their banners; without the
    # shell's figures nothing reads as that student's (no 0-day streak, no blank user card).
    # No error hooks: the pages' own calls answer 401 to a retired code.
    GONE = code()
    sql.execute("INSERT OR IGNORE INTO retired(code, \"into\", at) VALUES (?, NULL, 'now')", (GONE,))
    sql.commit()
    for w in (1280, 390):
        ctx = context(GONE, w, 844)
        pg = ctx.new_page()
        pg.goto(base + "/practice/", wait_until="networkidle")
        pg.wait_for_selector(".banner:has-text('This device was signed out from another device.')")
        if w < 760:
            assert not pg.is_visible(".pbar .streak") and not pg.is_visible(".pbar-chip"), "no streak without figures"
        else:
            assert pg.inner_text(".side-user .side-name") == "Account" and not pg.is_visible(".now-strip")
        ctx.close()
        ctx = b.new_context(viewport={"width": w, "height": 844}, has_touch=w < 760, is_mobile=w < 760)
        ctx.add_init_script("Object.defineProperty(window, 'localStorage', { get() { throw new DOMException('no', 'SecurityError') } })")
        pg = ctx.new_page()
        pg.goto(base + "/practice/", wait_until="networkidle")
        pg.wait_for_selector(".banner:has-text('This browser is blocking site data')")
        assert "How to fix" in pg.inner_text(".banner")
        ctx.close()
    print("ok  banners: a retired code, and refused localStorage (sessionStorage keeps a tab only); no figures painted without data")

    # ---- every page at 1280 and 390, light and dark, a new and a seeded learner: the chrome is
    # there (or, on the runner, the test and the kit, absent), nothing scrolls sideways, the theme
    # holds, and no console errors
    import pathlib
    web = pathlib.Path(__file__).resolve().parents[2] / "web"
    paths = sorted("/" + "".join(x + "/" for x in f.parent.relative_to(web).parts) for f in web.glob("**/index.html"))
    paths += ["/diagnostic/signup.html", "/diagnostic/verified.html", "/dev/kit.html", "/nope/"]
    # the runner, the test window, the kit, and staff pages (F6's /admin/reports/ loads no ui.js)
    bare = {"/practice/session/", "/test/", "/dev/kit.html"} | {x for x in paths if x.startswith("/admin/")}
    for L in (NEW, A):
        own = api(L, "POST", "/api/drill", {"topics": ["circles"], "count": 3})["id"]
        for theme in ("light", "dark"):
            api(L, "PUT", "/api/me", {"prefs": {"theme": theme}})
            for w, hgt in ((1280, 900), (390, 844)):
                ctx = context(L, w, hgt)
                pg = page(ctx)
                for path in paths:
                    url = path + (f"?id={own}" if path == "/practice/session/" else "")
                    go(pg, url) if path not in bare else pg.goto(base + url, wait_until="networkidle")
                    tag = (L == A and "seeded" or "new", theme, w, path)
                    assert pg.evaluate("document.documentElement.scrollWidth <= innerWidth"), tag
                    chrome = pg.is_visible("#bar nav.side" if w > 760 else "#bar .pbar") and (w > 760 or pg.is_visible("#tabs"))
                    assert chrome != (path in bare), (tag, "the shell's chrome")
                    # ponytail: /test/ keeps its 41 hard-coded colours until its owner converts them (Shell 2.13)
                    if path != "/test/":
                        assert pg.evaluate("getComputedStyle(document.body).backgroundColor") == (DARK if theme == "dark" else LIGHT), tag
                ctx.close()
    print(f"ok  {len(paths)} pages at 1280 and 390, light and dark, new and seeded: the chrome, no sideways scroll, the theme")

    assert not errors, errors[:8]
    print("ok  no console errors on the way")


if __name__ == "__main__":
    browser(int(sys.argv[1]) if len(sys.argv) > 1 else 8012)
