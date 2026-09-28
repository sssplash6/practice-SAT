"""The ordered Up next queue shared by the shell, Today and session endings.

Rows describe an action; they never start a sitting while the queue is read.
Other sections are reached through deps.part so an unmerged section only loses
its own rows.
"""

from __future__ import annotations

import datetime as dt
import math
import re
import statistics
from collections import Counter

from . import db, deps, estimate, prefs, progress

_UNSET = object()


def _today(tz: int) -> dt.date:
    return (dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=tz)).date()


def _minutes(count: int, seconds: int) -> int:
    return max(1, math.ceil(count * seconds / 60))


def _pace(learner: str) -> int:
    rows = db.rows("SELECT COALESCE(ms,sms) AS spent FROM attempts WHERE learner=?"
                   " AND COALESCE(ms,sms)>0 AND repeat=0 AND disputed=0 AND void IS NULL"
                   " AND at>=? ORDER BY id DESC LIMIT 300", learner,
                   (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=60)).isoformat())
    return max(60, min(150, round(statistics.median(r["spent"] for r in rows) / 1000))) if rows else 95


def _item(kind: str, key: str, title: str, detail: str, reason: str, minutes: int,
          *, body: dict | None = None, href: str | None = None,
          pts: int | None = None, urgent: bool = False) -> dict:
    out = {"key": key, "kind": kind, "title": title, "detail": detail,
           "reason": reason, "minutes": minutes, "pts": pts, "urgent": urgent}
    if body is not None:
        out["start"] = {"path": "/api/drill", "body": body}
    elif href is not None:
        out["href"] = href
    return out


def due(learner: str, tz: int = 0) -> dict:
    """One Due reader for Up next. S10 owns its full, capped list."""
    reader = deps.part("review", "due")
    if reader:
        return reader(learner, tz)
    day = _today(tz).isoformat()
    checks = progress.due_rechecks(learner, day)
    snoozed = {key for key, until in (prefs.get(learner, tz).get("snooze") or {}).items()
               if until == day}
    items = [
        {"key": f"due:check:{c['template']}", "kind": "check", "trap_id": c["trap_id"],
         "template": c["template"], "topic": c["topic"], "label": c["label"],
         "due": c["due"], "done": False,
         "snoozed": f"due:check:{c['template']}" in snoozed} for c in checks]
    return {"day": day, "left": sum(not i["snoozed"] for i in items), "items": items}


def stage(learner: str, tz: int = 0) -> dict:
    """The plan phase and the exam eve, from the same preference reader as Me."""
    current = prefs.stage(learner, tz)
    left = current["days_to_exam"] if current else None
    return {"name": current["name"] if current else "learn", "days_to_exam": left,
            "final_week": left is not None and 0 <= left <= 7,
            "eve": left == 1}


def _wrong(learner: str) -> tuple[Counter, Counter, list[dict]]:
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=60)).isoformat()
    rows = [dict(r) for r in db.rows("SELECT topic,template,norm,reason,at FROM attempts WHERE learner=?"
                                     " AND correct=0 AND repeat=0 AND disputed=0 AND void IS NULL"
                                     " AND at>=? ORDER BY at DESC,id DESC", learner, since)]
    return (Counter(r["topic"] for r in rows),
            Counter((r["template"], r["norm"]) for r in rows), rows)


def _points(gains: dict | None, topic: str, share: float = 1) -> int | None:
    if not gains:
        return None
    skill = next((s for s in gains["skills"] if s["topic"] == topic), None)
    value = round(skill["gain"] * share) if skill else 0
    return value if value >= 1 else None


def queue(learner: str, tz: int = 0, limit: int = 6, *, _plan=_UNSET, _closing=_UNSET,
          _board=_UNSET) -> list[dict]:
    """Return actions in priority order, keeping one row for each action key."""
    if not 1 <= limit <= 20:
        raise ValueError("limit must be 1–20")
    today = _today(tz)
    seconds = _pace(learner)
    answered = db.one("SELECT COUNT(*) AS n FROM attempts WHERE learner=?", learner)["n"]
    from . import api_shell
    resume = api_shell._resume(learner)
    phase = stage(learner, tz)
    if phase["eve"]:
        return [_item("rest", "rest:eve:math", "Rest. Nothing new today.", "Exam tomorrow",
                      "A rested mind is part of your preparation", 0, href="/plan/")]
    finished_start = db.one("SELECT 1 FROM sessions WHERE learner=? AND finished IS NOT NULL"
                            " AND json_extract(cfg,'$.source')='start' LIMIT 1", learner)
    if answered < 8 and not finished_start and not (resume and resume["kind"] in
                                                   api_shell.RESUME_TESTS):
        if resume and resume["kind"] == "drill":
            row = db.one("SELECT cfg FROM sessions WHERE id=?", resume["id"])
            import json
            cfg = json.loads(row["cfg"] or "{}") if row else {}
            if cfg.get("source") == "start":
                return [_item("resume", f"resume:start:{resume['id']}",
                              f"Resume · {resume['answered']} of 8", "Finish your first eight",
                              "Your start set is waiting", _minutes(max(1, 8 - resume["answered"]), seconds),
                              href=resume["href"], urgent=True)][:limit]
        saved = deps.part("account", "saved")
        return [
            _item("start", "start:new:math", "Start with 8 questions",
                  "One from each part of SAT Math, then four that adapt to you · about 10 min · no sign-up",
                  "Your first eight answers make the rest of Today yours", _minutes(8, seconds),
                  body={"source": "start"}),
            _item("diagnostic", "diagnostic:new:math", "Take the diagnostic · 20 q · a score range",
                  "20 questions · a score range", "Your starting band in 20 questions" if saved and saved(learner)
                  else "Asks for a name and email to show results",
                  _minutes(20, seconds), href="/diagnostic/")
        ][:limit]
    due_list = due(learner, tz)
    checks = [i for i in due_list.get("items", []) if i["kind"] == "check" and
              not i.get("done") and not i.get("snoozed")]
    open_traps = progress.open_traps(learner)
    wrong_total, wrong_norm, wrong_rows = _wrong(learner)
    gains = estimate.gains(learner) if answered >= estimate.MIN_ANSWERS else None
    board = progress.board(learner) if _board is _UNSET else _board
    names = progress.topics()
    settings = prefs.get(learner, tz)
    length = settings.get("set_length", 10) or None
    rows = []

    if resume and resume["kind"] in api_shell.RESUME_TESTS:
        remaining = resume["seconds_left"]
        if remaining is None or remaining > 0 or resume.get("paused"):
            rows.append(_item("resume", f"resume:test:{resume['id']}",
                              f"Resume {resume['kind']} · {resume['answered']}/{resume['total']}",
                              f"{resume['answered']} of {resume['total']} answered",
                              "Your clock is still running", math.ceil(remaining / 60) if remaining else 0,
                              href=resume["href"], urgent=True))

    if _closing is _UNSET:
        closing = deps.part("compete", "closing_soon")
        contests = closing(learner, tz) if closing else []
    else:
        contests = _closing or []
    for contest in contests:
        close = dt.datetime.fromisoformat(contest["closes"])
        rows.append(_item("contest", f"contest:private:{contest['id']}", contest["title"],
                          "A private contest is waiting", f"Closes {close:%b %-d, %H:%M}",
                          _minutes(10, seconds), href=f"/compete/contest/?id={contest['id']}", urgent=True))

    if _plan is _UNSET:
        plan_fn = deps.part("plan", "today_summary")
        plan = plan_fn(learner, tz) if plan_fn else None
    else:
        plan = _plan
    planned = []
    if plan:
        for task in plan["tasks"]:
            if not task.get("counted") or task.get("status") in ("done", "marked", "made_up", "skipped", "moved"):
                continue
            start = task.get("start") or {}
            body = start.get("body") or {}
            planned.append((task, start, body))
    plan_pools = {body.get("pool") for _, _, body in planned}
    plan_sources = {body.get("source") for _, _, body in planned}
    for task, start, body in planned:
        if ((body.get("pool") == "checks" and checks) or
            (body.get("pool") == "redo" and open_traps) or
            (body.get("source") == "due" and due_list.get("left"))):
            continue
        if task.get("kind") == "words" and any(r["kind"] == "words" for r in rows):
            continue
        row = _item("plan", f"plan:{task['kind']}:{task['id']}", f"Plan · {task['title']}",
                    task.get("detail") or f"{task.get('count', 0)} questions",
                    f"Today's plan: {plan['tasks_done']} of {plan['tasks_counted']} done",
                    math.ceil(task.get("minutes") or _minutes(task.get("count") or 1, seconds)),
                    body=body if start.get("path") == "/api/drill" else None,
                    href=start.get("path") if start.get("path") != "/api/drill" else None)
        if start.get("path") != "/api/drill" and start.get("path"):
            row.pop("href", None)
            row["start"] = start
        rows.append(row)

    if deps.part("review", "due") and due_list.get("left"):
        count = due_list["left"]
        rows.append(_item("review", "review:due:math", "Review what's due",
                          f"{count} due · about {_minutes(count, seconds)} min",
                          "Today's check-ins and spaced review" +
                          (" · also in today's plan" if "due" in plan_sources or "checks" in plan_pools else ""),
                          _minutes(count, seconds), body={"source": "due", "box": settings.get("review_minutes", 10)},
                          urgent=bool(checks)))
    elif checks:
        ids = [i["trap_id"] for i in checks[:3] if i.get("trap_id")]
        if ids:
            count = min(3 * len(ids), 9)
            title = f"Check-in: {checks[0]['label']}"
            if len(ids) > 1:
                title += f" (+{len(ids) - 1} more)"
            rows.append(_item("checks", "checks:checks:math", title,
                              f"{count} questions", "Checking that the fix stuck" +
                              (" · also in today's plan" if "checks" in plan_pools else ""),
                              _minutes(count, seconds), body={"pool": "checks", "ids": ids,
                                                             "count": count}, urgent=True))

    ranked_traps = sorted(open_traps, key=lambda t: (-(_points(gains, t["topic"],
                       wrong_norm[(t["template"], t["norm"])] / wrong_total[t["topic"]]
                       if wrong_total[t["topic"]] else 0) or 0), -t["hits"], t["id"]))
    for trap in ranked_traps[:3]:
        hits = wrong_norm[(trap["template"], trap["norm"])]
        pts = _points(gains, trap["topic"], hits / wrong_total[trap["topic"]]
                      if wrong_total[trap["topic"]] else 0)
        rows.append(_item("redo", f"redo:redo:{trap['id']}", f"Fix: {trap['label']}",
                          f"{trap['hits']} catches · 3 questions",
                          f"Caught you {trap['hits']} times" +
                          (" · also in today's plan" if "redo" in plan_pools else ""),
                          _minutes(3, seconds), body={"pool": "redo", "ids": [trap["id"]], "count": 3},
                          pts=pts))

    family_of = deps.part("habits", "family_of")
    if family_of and len(wrong_rows) >= 4:
        recent = wrong_rows[:20]
        families = Counter((family_of(r["reason"] or "") or {}).get("id") for r in recent)
        families.pop(None, None)
        if families:
            family, count = families.most_common(1)[0]
            if count >= math.ceil(.25 * len(recent)):
                matched = [r for r in recent if (family_of(r["reason"] or "") or {}).get("id") == family]
                by_skill = Counter(r["topic"] for r in matched)
                raw = sum(next((s["gain"] for s in (gains or {}).get("skills", []) if s["topic"] == topic), 0)
                          * n / wrong_total[topic] for topic, n in by_skill.items() if wrong_total[topic])
                points = round(raw) or None
                label = next((x["name"] for x in (deps.part("habits", "families") or (lambda: []))()
                              if x["id"] == family), family)
                rows.append(_item("habit", f"habit:habit:{family}", f"Habit: {label} · 8",
                                  f"{count} of your last {len(recent)} misses", "Work on the pattern across skills",
                                  _minutes(8, seconds), body={"source": "habit", "habit": family, "count": 8},
                                  pts=points if gains and points and points >= 1 else None))

    rough = [t for t, v in board.items() if v["evidence"] < 10]
    if not phase["final_week"] and answered < 200 and len(rough) >= 4:
        rows.append(_item("probe", "probe:new:math", "Sharpen · 12 q",
                          f"{len(rough)} skills still rough", "Measure them before choosing a focus",
                          _minutes(12, seconds), body={"source": "probe", "count": 12}))

    candidates = sorted((gains or {}).get("skills", []), key=lambda x: -x["gain"])
    topic = candidates[0]["topic"] if candidates else progress.coach(learner, k=1)["topics"][0]
    count = length or 10
    pts = _points(gains, topic)
    rows.append(_item("skill", f"skill:new:{topic}", f"{names[topic].name} · {count} q",
                      f"{count} questions", f"Most points on the table: about {pts}" if pts else
                      "Your next useful skill", _minutes(count, seconds),
                      body={"topics": [topic], "count": length}, pts=pts))

    for saved in db.rows("SELECT template,seed,topic,at FROM saved WHERE learner=? ORDER BY at", learner):
        age = (today - dt.date.fromisoformat(saved["at"][:10])).days
        if not (6 <= age <= 8 or 20 <= age <= 22):
            continue
        rows.append(_item("saved", f"saved:saved:{saved['template']}:{saved['seed']}",
                          f"Saved {saved['at'][:10]} · try a fresh one", "1 question",
                          "Saved questions come back twice", _minutes(1, seconds),
                          body={"pool": "saved", "ids": [[saved["template"], saved["seed"]]],
                                "exact": False, "each": 1, "count": 1}))

    if settings.get("keep_warm"):
        warm = [v for v in board.values() if v["fading"]]
        if warm:
            v = max(warm, key=lambda x: x["last"] or "")
            rows.append(_item("warm", f"warm:review:{v['topic']}",
                              f"Keep warm: {v['name']} · 3", "3 questions",
                              f"Strong, last practised {v['last'][:10]}", _minutes(3, seconds),
                              body={"pool": "review", "topics": [v["topic"]], "count": 3}))

    if not phase["final_week"]:
        seen = {r["template"] for r in db.rows("SELECT DISTINCT template FROM attempts WHERE learner=?", learner)}
        from . import practice
        cat = practice.catalogue()["by_topic"]
        unseen = [(t, len(set(templates) - seen)) for t, templates in cat.items()]
        unseen = [(t, n) for t, n in unseen if n]
        if unseen:
            shares = estimate.shares()
            t, n = max(unseen, key=lambda x: (x[1] * shares.get(x[0], 0), x[1]))
            rows.append(_item("untried", f"untried:untried:{t}",
                              f"{min(5, n)} new kinds of {names[t].name} question",
                              f"{n} types not met", "See a form you have not seen yet",
                              _minutes(min(5, n), seconds),
                              body={"pool": "untried", "topics": [t], "count": min(5, n)}))

    if not db.one("SELECT 1 FROM attempts WHERE learner=? AND session=?", learner,
                  f"qotd:{today.isoformat()}"):
        rows.append(_item("qotd", f"qotd:today:{today.isoformat()}", "Question of the day",
                          "1 question", "Keep your day's-questions streak", _minutes(1, seconds), href="/#qotd"))

    seen_keys = set()
    result = []
    for row in rows:
        if row["key"] not in seen_keys:
            seen_keys.add(row["key"])
            result.append(row)
    return result[:limit]


def resolve_drill(learner: str, body: dict) -> dict:
    """Prepare the U1 time box for F5's source registry.

    The first slots are due check-ins, open traps, a weak skill and a warm
    skill. F5 serves fresh seeds and owns the clock and mixed ordering.
    """
    box = body.get("box")
    if type(box) is not int or not 5 <= box <= 60:
        from fastapi import HTTPException
        raise HTTPException(422, {"field": "box", "reason": "use 5–60 minutes"})
    tz = body.get("tz", 0)
    slots = []
    want = dict(body.get("want") or {})
    used = set()
    for item in due(learner, tz)["items"]:
        if item["kind"] == "check" and not item.get("done") and not item.get("snoozed"):
            trap = db.one("SELECT * FROM traps WHERE id=? AND learner=?", item["trap_id"], learner)
            if not trap:
                continue
            template = progress.checkin_template(trap)
            if template in used:
                continue
            used.add(template)
            slots.append({"template": template, "why": "A fix is due a check-in"})
            if progress.named(trap["norm"]):
                want[template] = "^" + re.escape(trap["norm"]) + "$"
        if len(slots) == 3:
            break
    wrong_total, wrong_norm, _ = _wrong(learner)
    gains = estimate.gains(learner)
    traps = sorted(progress.open_traps(learner), key=lambda t: (
        -(_points(gains, t["topic"], wrong_norm[(t["template"], t["norm"])] /
                  wrong_total[t["topic"]] if wrong_total[t["topic"]] else 0) or 0),
        -t["hits"], t["id"]))
    for trap in traps:
        if trap["template"] in used:
            continue
        used.add(trap["template"])
        slots.append({"template": trap["template"], "why": "Fix an open mistake"})
        if progress.named(trap["norm"]):
            want[trap["template"]] = "^" + re.escape(trap["norm"]) + "$"
        if sum(x["why"] == "Fix an open mistake" for x in slots) == 4:
            break
    board = progress.board(learner)
    weak = min(board.values(), key=lambda x: (x["mastery"], x["answered"]))
    from . import practice
    for template in practice.catalogue()["by_topic"][weak["topic"]][:3]:
        if template not in used:
            used.add(template)
            slots.append({"template": template, "why": "Strengthen a weak skill"})
    warm = next((v for v in board.values() if v["fading"]), None)
    if warm:
        template = practice.catalogue()["by_topic"][warm["topic"]][0]
        if template not in used:
            slots.append({"template": template, "why": "Keep a strong skill warm"})
    mixed = []
    while slots:
        prior = practice.topic_of(mixed[-1]["template"]) if mixed else None
        index = next((i for i, slot in enumerate(slots)
                      if practice.topic_of(slot["template"]) != prior), 0)
        mixed.append(slots.pop(index))
    return {**body, "source": "next", "box": box, "count": None,
            "order": "mixed", "segments": mixed[:30], "want": want}
