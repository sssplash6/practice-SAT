"""Study Plan API. All writes are learner scoped and plan arithmetic lives in plan.py."""

from __future__ import annotations

import datetime as dt
import json
import secrets

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from fastapi.responses import Response

from . import db, deps, plan, prefs, progress, satdates
from satbank.registry import generate

router = APIRouter()


def _reader(token: str | None) -> str:
    return deps.learner_of(token)


def _writer(token: str | None) -> str:
    return deps.writer_of(token)


def _active(learner: str, pid: str):
    return plan.owned_row(learner, pid, active=True)


def _skill(topic) -> bool:
    """A Math or an R&W skill the plan deals."""
    return isinstance(topic, str) and (topic in plan.TOPICS or topic in plan.topics_of("rw"))


def _mirror(c, learner: str, pid: str, cfg: dict) -> None:
    c.execute("INSERT INTO learners(id,created,updated) VALUES (?,?,?) ON CONFLICT(id) DO NOTHING",
              (learner, deps.now(), deps.now()))
    c.execute("UPDATE learners SET plan=?,current=?,target=?,exam_date=?,minutes=?,days=?,tests=?,"
              "focus=?,rw_now=?,rw_target=?,updated=? WHERE id=?",
              (pid, cfg["current"], cfg["target"], cfg["exam_date"], cfg["minutes"], cfg["days"],
               cfg["tests"], json.dumps(cfg["focus"]), cfg.get("rw_current"), cfg.get("rw_target"),
               deps.now(), learner))


def _custom(body: dict, start: dt.date, exam: dt.date) -> dict:
    if not isinstance(body, dict):
        raise HTTPException(422, "custom task must be an object")
    typ = body.get("type", "other")
    if typ not in plan.TASK_TYPES:
        raise HTTPException(422, "custom task type is invalid")
    title = body.get("title") or ("Bluebook test" if typ == "bluebook" else "")
    if not isinstance(title, str) or not title.strip() or len(title) > 60:
        raise HTTPException(422, "custom task title must be 1–60 characters")
    minutes = body.get("minutes", 134 if typ == "bluebook" else None)
    if type(minutes) is not int or not 5 <= minutes <= 240:
        raise HTTPException(422, "custom task minutes must be 5–240")
    day, repeat = body.get("day"), body.get("repeat")
    if (day is None) == (repeat is None):
        raise HTTPException(422, "custom task needs either day or repeat")
    if day is not None and not start <= plan._date(day, "custom task day") <= exam - dt.timedelta(days=2):
        raise HTTPException(422, "custom task day must be inside the study plan")
    if repeat is not None and repeat != "study_days" and repeat not in [f"weekly:{n}" for n in range(7)]:
        raise HTTPException(422, "custom task repeat must be study_days or weekly:0–6")
    subject = body.get("subject") or ("rw" if typ == "rw" else "math")
    if subject not in ("math", "rw"):
        raise HTTPException(422, "custom task subject must be math or rw")
    return {"title": title.strip(), "minutes": minutes, "day": day, "repeat": repeat,
            "type": typ, "subject": subject}


def _insert_custom(c, pid: str, task: dict) -> str:
    tid = "pt:" + secrets.token_urlsafe(12)
    c.execute("INSERT INTO plan_tasks(id,plan,day,repeat,title,minutes,created,type,subject)"
              " VALUES (?,?,?,?,?,?,?,?,?)",
              (tid, pid, task["day"], task["repeat"], task["title"], task["minutes"],
               deps.now(), task["type"], task["subject"]))
    return tid


def _days(learner: str, row, dates: list[dt.date]) -> dict:
    return {"days": [plan.day_view(learner, row, d) for d in dates]}


def _future(row, day: str, *, allow_eve: bool = False) -> dt.date:
    d = plan._date(day, "day")
    exam = dt.date.fromisoformat(plan.cfg_of(row)["exam_date"])
    latest = exam - dt.timedelta(days=1 if allow_eve else 2)
    if d < plan.today(row["tz"] or 0) or d > latest or d < dt.date.fromisoformat(row["start"]):
        raise HTTPException(422, "day must be a future date inside this plan")
    return d


@router.get("/api/plan")
def get_plan(x_learner: str | None = Header(default=None), x_tz: int = Depends(deps.tz_of)) -> dict:
    return plan.payload(_reader(x_learner), x_tz)


@router.get("/api/plan/progress")
def get_progress(x_learner: str | None = Header(default=None), x_tz: int = Depends(deps.tz_of)) -> dict:
    full = plan.payload(_reader(x_learner), x_tz)
    return {key: full.get(key) for key in ("active", "stats", "domains", "skills", "rw_domains", "coverage", "points",
                                          "projection", "pace", "score", "changes", "checks", "checkpoints",
                                          "bought", "causes", "calibration", "skill_pace", "split_domain",
                                          "changes_counts", "weeks", "verdict", "workload", "by_subject", "subjects")}


@router.get("/api/plan/day/{day}")
def get_day(day: str, minutes: int | None = Query(default=None),
            x_learner: str | None = Header(default=None), x_tz: int = Depends(deps.tz_of)) -> dict:
    learner = _reader(x_learner)
    row = plan.active_row(learner)
    if not row:
        raise HTTPException(404, "no active plan")
    return plan.day_view(learner, row, plan._date(day, "day"), preview_minutes=minutes)


@router.post("/api/plan/preview")
def preview(body: dict, x_learner: str | None = Header(default=None),
            x_tz: int = Depends(deps.tz_of)) -> dict:
    learner = _reader(x_learner)
    return plan.preview(learner, plan.validate(body, learner, x_tz), x_tz)


@router.put("/api/plan/draft")
def put_draft(body: dict, x_learner: str | None = Header(default=None)) -> dict:
    learner = _writer(x_learner)
    if not isinstance(body, dict) or type(body.get("step")) is not int or not 1 <= body["step"] <= 4 or not isinstance(body.get("fields"), dict):
        raise HTTPException(422, "draft needs step 1–4 and fields")
    draft = {"step": body["step"], "fields": body["fields"], "updated": deps.now()}
    packed = json.dumps(draft)
    if len(packed.encode()) > 8192:
        raise HTTPException(422, "draft must be at most 8 KB")
    with db.atomic() as c:
        c.execute("INSERT INTO learners(id,created,updated) VALUES (?,?,?) ON CONFLICT(id) DO NOTHING",
                  (learner, deps.now(), deps.now()))
        c.execute("UPDATE learners SET plan_draft=? WHERE id=?", (packed, learner))
    return {"draft": draft}


@router.delete("/api/plan/draft")
def delete_draft(x_learner: str | None = Header(default=None)) -> dict:
    learner = _writer(x_learner)
    db.run("UPDATE learners SET plan_draft=NULL WHERE id=?", learner)
    return {"draft": None}


@router.post("/api/plan")
def create(body: dict, x_learner: str | None = Header(default=None),
           x_tz: int = Depends(deps.tz_of)) -> dict:
    learner = _writer(x_learner)
    cfg = plan.validate(body, learner, x_tz)
    word_goal = plan.words_focus_goal(learner, cfg)
    name = body.get("name") or f"Plan for {cfg['exam_date']}"
    if not isinstance(name, str) or not name.strip() or len(name) > 40:
        raise HTTPException(422, "name must be 1–40 characters")
    custom_in = body.get("custom", body.get("tasks", [])) or []
    if not isinstance(custom_in, list) or len(custom_in) > 10:
        raise HTTPException(422, "custom tasks: at most 10")
    start = plan.today(x_tz)
    exam = dt.date.fromisoformat(cfg["exam_date"])
    custom = [_custom(item, start, exam) for item in custom_in]
    pid = "pl:" + secrets.token_urlsafe(12)
    board = {**progress.board(learner), **progress.board(learner, "rw")}
    mastery = {d: round(sum(v["mastery"] for v in board.values() if v["domain"] == d) /
                        max(1, sum(v["domain"] == d for v in board.values())), 3) for d in plan.DOMAINS + plan.RW_DOMAINS}
    points = plan._points(learner)
    rw_points = plan._points(learner, None, "rw")
    with db.atomic() as c:
        old = plan.active_row(learner)
        if old:
            plan.freeze(learner, old, x_tz)
            c.execute("UPDATE plans SET archived=?,updated=? WHERE id=?", (deps.now(), deps.now(), old["id"]))
        c.execute("INSERT INTO plans(id,learner,name,cfg,start,tz,start_mastery,start_points,created,updated)"
                  " VALUES (?,?,?,?,?,?,?,?,?,?)",
                  (pid, learner, name.strip(), json.dumps(cfg), start.isoformat(), x_tz,
                   json.dumps(mastery), json.dumps({**({"total": points["total"]} if points else {}),
                                                    **({"rw": {"total": rw_points["total"]}} if rw_points else {})}),
                   deps.now(), deps.now()))
        for task in custom:
            _insert_custom(c, pid, task)
        _mirror(c, learner, pid, cfg)
        if cfg["booked"]:
            prefs.put(learner, {"registered": cfg["exam_date"]})
        if word_goal is not None:
            prefs.put(learner, {"words_goal": word_goal})
        c.execute("UPDATE learners SET plan_draft=NULL WHERE id=?", (learner,))
    return plan.payload(learner, x_tz)


@router.patch("/api/plan/{pid}")
def patch_plan(pid: str, body: dict, x_learner: str | None = Header(default=None),
               x_tz: int = Depends(deps.tz_of)) -> dict:
    learner = _writer(x_learner)
    row = _active(learner, pid)
    plan.freeze(learner, row, x_tz)
    before = plan.cfg_of(row)
    cfg = plan.validate(body, learner, x_tz, before)
    word_goal = plan.words_focus_goal(learner, cfg, before)
    name = body.get("name", row["name"])
    if not isinstance(name, str) or not name.strip() or len(name) > 40:
        raise HTTPException(422, "name must be 1–40 characters")
    with db.atomic() as c:
        c.execute("UPDATE plans SET name=?,cfg=?,updated=? WHERE id=?",
                  (name.strip(), json.dumps(cfg), deps.now(), pid))
        _mirror(c, learner, pid, cfg)
        if "booked" in body:
            prefs.put(learner, {"registered": cfg["exam_date"] if cfg["booked"] else None})
        if word_goal is not None:
            prefs.put(learner, {"words_goal": word_goal})
        field = next(iter(body)) if len(body) == 1 else ",".join(sorted(body))
        plan.event(pid, "edit", "Plan settings changed", field=field,
                   before=before.get(field), after=cfg.get(field))
    return plan.payload(learner, x_tz)


@router.post("/api/plan/{pid}/tasks")
def add_task(pid: str, body: dict, x_learner: str | None = Header(default=None)) -> dict:
    learner = _writer(x_learner)
    row = _active(learner, pid)
    plan.freeze(learner, row)
    data = _custom(body, plan.today(row["tz"] or 0), dt.date.fromisoformat(plan.cfg_of(row)["exam_date"]))
    with db.atomic() as c:
        tid = _insert_custom(c, pid, data)
        plan.event(pid, "edit", f"Added {data['title']}", data["day"], "task")
    dates = [plan._date(data["day"], "day")] if data["day"] else [plan.today(row["tz"] or 0)]
    return {"id": tid, **_days(learner, row, dates)}


@router.patch("/api/plan/{pid}/tasks/{tid:path}")
def patch_task(pid: str, tid: str, body: dict,
               x_learner: str | None = Header(default=None)) -> dict:
    learner = _writer(x_learner)
    row = _active(learner, pid)
    plan.freeze(learner, row)
    if not isinstance(body, dict):
        raise HTTPException(422, "task change must be an object")
    day = _future(row, body.get("day") or tid[:10])
    current = plan.day_view(learner, row, day)
    task = next((t for t in current["tasks"] if t["id"] == tid), None)
    own = db.one("SELECT * FROM plan_tasks WHERE plan=? AND id=? AND removed IS NULL", pid, tid)
    if task is None and own is None:
        raise HTTPException(404, "task not found on day")
    if "status" in body and body["status"] not in ("done", "skipped", "todo"):
        raise HTTPException(422, "status must be done, skipped or todo")
    reason = body.get("reason")
    if reason is not None and (body.get("status") != "skipped" or reason not in ("no_time", "too_hard", "know")):
        raise HTTPException(422, "skip reason must be no_time, too_hard or know")
    if ("title" in body or "type" in body or ("minutes" in body and "status" not in body)) and own is None:
        raise HTTPException(422, "only your own task can change title or minutes")
    changes = {}
    if own and any(k in body for k in ("title", "minutes", "type")):
        revised = _custom({"title": body.get("title", own["title"]),
                           "minutes": body.get("minutes", own["minutes"]),
                           "type": body.get("type", own["type"]),
                           "day": own["day"], "repeat": own["repeat"]},
                          plan.today(row["tz"] or 0), dt.date.fromisoformat(plan.cfg_of(row)["exam_date"]))
        changes = revised
    target = None
    if "to" in body:
        target = _future(row, body["to"])
        target_kind, _, target_m = plan.kind_of(plan.cfg_of(row), dt.date.fromisoformat(row["start"]),
                                                target, plan._override(pid, target))
        if target_kind not in ("practice", "test") or (task and task["kind"] == "test" and target_m < 35):
            raise HTTPException(422, "to must be a study day with enough time")
        if task is None:
            raise HTTPException(404, "task not found on day")
    if reason == "no_time" and not target:
        for offset in range(1, 366):
            candidate = day + dt.timedelta(days=offset)
            if candidate >= dt.date.fromisoformat(plan.cfg_of(row)["exam_date"]) - dt.timedelta(days=1):
                break
            kind, _, _ = plan.kind_of(plan.cfg_of(row), dt.date.fromisoformat(row["start"]), candidate,
                                       plan._override(pid, candidate))
            if kind in ("practice", "test"):
                target = candidate
                break
        if not target:
            raise HTTPException(409, "no later study day to move this task")
    if reason == "too_hard" and task and task.get("topics"):
        topic = body.get("topic") or next((t for t in task["topics"] if
                                            plan._state(plan.cfg_of(row), t) == "focus"), task["topics"][0])
        if topic not in task["topics"]:
            raise HTTPException(422, "topic must be on this task")
        allocation = plan.allocate(learner, plan.cfg_of(row), dt.date.fromisoformat(row["start"]),
                                   dt.date.fromisoformat(plan.cfg_of(row)["exam_date"]), pid)
        follow = next((date for date in sorted(allocation) if date > day.isoformat() and
                       topic in allocation[date]), None)
        reason = f"too_hard:{topic}:{follow}" if follow else "too_hard"
    if reason == "know":
        if not task or not task.get("topics"):
            raise HTTPException(422, "test-out needs a skill task")
        subject = deps.subject_of(task["topics"][0])
        return {**_days(learner, row, [day]), "test_out": {"topics": task["topics"], "count": 8,
                "tiers": ["medium", "hard"], "timing": "pace", "task": f"{day}:check:{task['topics'][0]}",
                **({"subject": subject} if subject != "math" else {})}}
    swap = body.get("swap")
    if swap is not None:
        swap = [swap] if isinstance(swap, str) else swap
        if not isinstance(swap, list) or not 1 <= len(swap) <= 3 or any(not _skill(t) for t in swap):
            raise HTTPException(422, "swap must name up to three skills")
    with db.atomic() as c:
        if changes:
            c.execute("UPDATE plan_tasks SET title=?,minutes=?,type=?,subject=? WHERE id=?",
                      (changes["title"], changes["minutes"], changes["type"], changes["subject"], tid))
        if "status" in body:
            if body["status"] == "todo":
                c.execute("DELETE FROM plan_marks WHERE plan=? AND day=? AND task=?", (pid, day.isoformat(), tid))
            else:
                minutes = body.get("minutes") if not own else own["minutes"]
                if minutes is not None and (type(minutes) is not int or not 0 <= minutes <= 240):
                    raise HTTPException(422, "minutes must be 0–240")
                c.execute("INSERT INTO plan_marks(plan,day,task,status,to_day,at,minutes,note) VALUES (?,?,?,?,?,?,?,?)"
                          " ON CONFLICT(plan,day,task) DO UPDATE SET status=excluded.status,to_day=NULL,"
                          "at=excluded.at,minutes=excluded.minutes,note=excluded.note",
                          (pid, day.isoformat(), tid, body["status"], None, deps.now(),
                           minutes, body.get("where") or reason))
        if target:
            c.execute("INSERT INTO plan_marks(plan,day,task,status,to_day,at,note) VALUES (?,?,?,?,?,?,?)"
                      " ON CONFLICT(plan,day,task) DO UPDATE SET status=excluded.status,to_day=excluded.to_day,"
                      "at=excluded.at,note=excluded.note",
                      (pid, day.isoformat(), tid, "moved", target.isoformat(), deps.now(), json.dumps(task)))
        if swap is not None:
            c.execute("INSERT INTO plan_overrides(plan,day,topics) VALUES (?,?,?)"
                      " ON CONFLICT(plan,day) DO UPDATE SET topics=excluded.topics",
                      (pid, day.isoformat(), json.dumps(swap)))
        plan.event(pid, "edit", f"Changed {tid}", day.isoformat(), "task")
    dates = [day] + ([target] if target and target != day else [])
    answer = _days(learner, row, dates)
    if own and own["type"] == "bluebook" and body.get("status") == "done":
        answer["next"] = "score_sheet"
    return answer


@router.delete("/api/plan/{pid}/tasks/{tid:path}")
def delete_task(pid: str, tid: str, x_learner: str | None = Header(default=None)) -> dict:
    learner = _writer(x_learner)
    row = _active(learner, pid)
    plan.freeze(learner, row)
    own = db.one("SELECT * FROM plan_tasks WHERE id=? AND plan=? AND removed IS NULL", tid, pid)
    if not own:
        raise HTTPException(404, "own task not found")
    with db.atomic() as c:
        c.execute("UPDATE plan_tasks SET removed=? WHERE id=?", (deps.now(), tid))
        plan.event(pid, "edit", f"Removed {own['title']}", own["day"], "task")
    day = plan._date(own["day"], "day") if own["day"] else plan.today(row["tz"] or 0)
    return _days(learner, row, [day])


@router.put("/api/plan/{pid}/day/{day}")
def put_day(pid: str, day: str, body: dict, x_learner: str | None = Header(default=None)) -> dict:
    learner = _writer(x_learner)
    row = _active(learner, pid)
    plan.freeze(learner, row)
    date = _future(row, day)
    if not isinstance(body, dict) or not set(body) <= {"minutes", "off", "topics", "test", "trim"}:
        raise HTTPException(422, "day override has unknown fields")
    minutes = body.get("minutes")
    if "minutes" in body and (type(minutes) is not int or minutes not in (0, *range(5, 241))):
        raise HTTPException(422, "minutes must be 0 or 5–240")
    if "off" in body and type(body["off"]) is not bool:
        raise HTTPException(422, "off must be boolean")
    if "test" in body and body["test"] not in ("module", "section", "none"):
        raise HTTPException(422, "test must be module, section or none")
    if "topics" in body and (not isinstance(body["topics"], list) or not 1 <= len(body["topics"]) <= 3 or
                              any(not _skill(t) for t in body["topics"])):
        raise HTTPException(422, "topics must name up to three skills")
    old = plan._override(pid, date)
    merged = {"minutes": old.get("minutes"), "off": old.get("off", 0), "test": old.get("test"),
              "topics": old.get("topics"), "trim": old.get("trim", 0)}
    merged.update(body)
    if "topics" in body:
        merged["topics"] = json.dumps(body["topics"])
    with db.atomic() as c:
        c.execute("INSERT INTO plan_overrides(plan,day,minutes,off,test,topics,trim) VALUES (?,?,?,?,?,?,?)"
                  " ON CONFLICT(plan,day) DO UPDATE SET minutes=excluded.minutes,off=excluded.off,"
                  "test=excluded.test,topics=excluded.topics,trim=excluded.trim",
                  (pid, day, merged["minutes"], int(bool(merged["off"])), merged["test"],
                   merged["topics"], int(bool(merged["trim"]))))
        plan.event(pid, "edit", f"Changed {day}", day, ",".join(sorted(body)))
    return _days(learner, row, [date])


@router.delete("/api/plan/{pid}/day/{day}")
def clear_day(pid: str, day: str, x_learner: str | None = Header(default=None)) -> dict:
    learner = _writer(x_learner)
    row = _active(learner, pid)
    plan.freeze(learner, row)
    date = _future(row, day)
    with db.atomic() as c:
        c.execute("DELETE FROM plan_overrides WHERE plan=? AND day=?", (pid, day))
        plan.event(pid, "edit", f"Reset {day}", day, "day")
    return _days(learner, row, [date])


@router.put("/api/plan/{pid}/week/{monday}")
def put_week(pid: str, monday: str, body: dict, x_learner: str | None = Header(default=None)) -> dict:
    learner = _writer(x_learner)
    row = _active(learner, pid)
    date = _future(row, monday)
    if date.weekday() != 0 or not isinstance(body, dict) or not isinstance(body.get("days"), list):
        raise HTTPException(422, "week needs a Monday and days list")
    items = body["days"]
    if len(items) > 7:
        raise HTTPException(422, "week may have seven days")
    # Validate the whole batch before writing any override.
    for item in items:
        d = _future(row, item.get("date", ""))
        if not date <= d <= date + dt.timedelta(days=6):
            raise HTTPException(422, "week day is outside this week")
        if "minutes" in item and (type(item["minutes"]) is not int or item["minutes"] not in (0, *range(5, 241))):
            raise HTTPException(422, "minutes must be 0 or 5–240")
        if "off" in item and type(item["off"]) is not bool:
            raise HTTPException(422, "off must be boolean")
    plan.freeze(learner, row)
    with db.atomic() as c:
        for item in items:
            d = item["date"]
            old = plan._override(pid, dt.date.fromisoformat(d))
            c.execute("INSERT INTO plan_overrides(plan,day,minutes,off,test,topics,trim) VALUES (?,?,?,?,?,?,?)"
                      " ON CONFLICT(plan,day) DO UPDATE SET minutes=excluded.minutes,off=excluded.off,"
                      "test=excluded.test,topics=excluded.topics,trim=excluded.trim",
                      (pid, d, item.get("minutes", old.get("minutes")),
                       int(item.get("off", old.get("off", 0))), old.get("test"), old.get("topics"), old.get("trim", 0)))
        plan.event(pid, "edit", f"Shaped week of {monday}", monday, "week")
    return _days(learner, row, [date + dt.timedelta(days=n) for n in range(7)
                                 if date + dt.timedelta(days=n) <= dt.date.fromisoformat(plan.cfg_of(row)["exam_date"])])


@router.post("/api/plan/{pid}/activate")
def activate(pid: str, x_learner: str | None = Header(default=None),
             x_tz: int = Depends(deps.tz_of)) -> dict:
    learner = _writer(x_learner)
    row = plan.owned_row(learner, pid)
    cfg = plan.cfg_of(row)
    with db.atomic() as c:
        c.execute("UPDATE plans SET archived=?,updated=? WHERE learner=? AND archived IS NULL AND id!=?",
                  (deps.now(), deps.now(), learner, pid))
        c.execute("UPDATE plans SET archived=NULL,updated=? WHERE id=?", (deps.now(), pid))
        _mirror(c, learner, pid, cfg)
    return plan.payload(learner, x_tz)


@router.post("/api/plan/{pid}/archive")
def archive(pid: str, x_learner: str | None = Header(default=None),
            x_tz: int = Depends(deps.tz_of)) -> dict:
    learner = _writer(x_learner)
    plan.owned_row(learner, pid)
    with db.atomic() as c:
        c.execute("UPDATE plans SET archived=?,updated=? WHERE id=?", (deps.now(), deps.now(), pid))
        c.execute("UPDATE learners SET plan=NULL WHERE id=? AND plan=?", (learner, pid))
    return plan.payload(learner, x_tz)


@router.post("/api/plan/{pid}/duplicate")
def duplicate(pid: str, x_learner: str | None = Header(default=None)) -> dict:
    learner = _writer(x_learner)
    row = plan.owned_row(learner, pid)
    cfg = plan.cfg_of(row)
    old = dt.date.fromisoformat(cfg["exam_date"])
    if old <= plan.today(row["tz"] or 0):
        cfg["exam_date"] = next(iter(d for d in satdates.upcoming(plan.today(row["tz"] or 0))
                                         if d > plan.today(row["tz"] or 0).isoformat()),
                                (plan.today(row["tz"] or 0) + dt.timedelta(days=90)).isoformat())
    record = plan._summary(row)["record"]
    if row["result"]:
        result = json.loads(row["result"])
        cfg["current"] = result.get("math", cfg.get("current"))
        cfg["rw_current"] = result.get("rw", cfg.get("rw_current"))
    day_minutes = list(cfg.get("day_minutes") or [None] * 7)
    for weekday, pct in enumerate(record["by_dow"]):
        if pct < 50 and cfg["days"][weekday] == "1":
            day_minutes[weekday] = 15
    cfg["day_minutes"] = day_minutes
    draft = {"step": 1, "fields": cfg, "updated": deps.now(), "from": pid}
    db.run("UPDATE learners SET plan_draft=? WHERE id=?", json.dumps(draft), learner)
    return {"draft": draft}


@router.delete("/api/plan/{pid}")
def delete_plan(pid: str, x_learner: str | None = Header(default=None)) -> dict:
    learner = _writer(x_learner)
    row = plan.owned_row(learner, pid)
    if not row["archived"]:
        raise HTTPException(409, "archive the plan before deleting it")
    with db.atomic() as c:
        for table in ("plan_days", "plan_overrides", "plan_tasks", "plan_marks", "plan_snapshots", "plan_events"):
            c.execute(f"DELETE FROM {table} WHERE plan=?", (pid,))
        c.execute("DELETE FROM plans WHERE id=?", (pid,))
    return {"deleted": pid}


@router.post("/api/plan/{pid}/result")
def result(pid: str, body: dict, x_learner: str | None = Header(default=None)) -> dict:
    learner = _writer(x_learner)
    row = plan.owned_row(learner, pid)
    if plan.today(row["tz"] or 0) < dt.date.fromisoformat(plan.cfg_of(row)["exam_date"]):
        raise HTTPException(409, "result can be logged from the exam day")
    data = {"math": plan._score(body.get("math"), "math")}
    if "rw" in body:
        data["rw"] = plan._score(body["rw"], "rw")
    db.run("UPDATE plans SET result=?,updated=? WHERE id=?", json.dumps(data), deps.now(), pid)
    return {"result": data}


@router.post("/api/plan/{pid}/drift")
def drift(pid: str, body: dict, x_learner: str | None = Header(default=None)) -> dict:
    learner = _writer(x_learner)
    row = _active(learner, pid)
    if not isinstance(body.get("dismiss"), list):
        raise HTTPException(422, "dismiss must list sitting ids")
    subject = deps.subject_param(body.get("subject"))       # each section's banner is dismissed on its own
    seen = {**plan.drift_seen(row), subject: deps.now()}
    db.run("UPDATE plans SET drift_seen=? WHERE id=?", json.dumps(seen), pid)
    return {"dismissed": body["dismiss"], "subject": subject}


@router.get("/api/plan/ics")
def active_ics(x_learner: str | None = Header(default=None)) -> Response:
    learner = _reader(x_learner)
    row = plan.active_row(learner)
    if not row:
        raise HTTPException(404, "no active plan")
    return Response(plan.calendar(learner, row), media_type="text/calendar")


@router.get("/api/plan/{pid}/ics")
def plan_ics(pid: str, x_learner: str | None = Header(default=None)) -> Response:
    learner = _reader(x_learner)
    return Response(plan.calendar(learner, plan.owned_row(learner, pid)), media_type="text/calendar")


@router.post("/api/plan/{pid}/links")
def links(pid: str, body: dict, x_learner: str | None = Header(default=None)) -> dict:
    learner = _writer(x_learner)
    row = plan.owned_row(learner, pid)
    if not isinstance(body, dict) or not body or not set(body) <= {"cal", "view"} or any(type(v) is not bool for v in body.values()):
        raise HTTPException(422, "links accepts cal and view booleans")
    values = {"cal": row["cal_token"], "view": row["view_token"]}
    with db.atomic() as c:
        for key in body:
            if values[key]:
                c.execute("UPDATE links SET revoked=? WHERE token=? AND learner=? AND kind=?"
                          " AND revoked IS NULL", (deps.now(), values[key], learner,
                                                  "cal" if key == "cal" else "progress"))
            values[key] = secrets.token_urlsafe(16) if body[key] else None
            if values[key]:
                c.execute("INSERT INTO links(token,learner,kind,created) VALUES (?,?,?,?)",
                          (values[key], learner, "cal" if key == "cal" else "progress", deps.now()))
            c.execute(f"UPDATE plans SET {'cal_token' if key == 'cal' else 'view_token'}=? WHERE id=?",
                      (values[key], pid))
    return {"cal": f"/api/cal/{values['cal']}.ics" if values["cal"] else None,
            "view": f"/api/plan/shared/{values['view']}" if values["view"] else None,
            "cal_token": values["cal"], "view_token": values["view"]}


@router.get("/cal/{token}.ics")
@router.get("/api/cal/{token}.ics")
def token_ics(token: str) -> Response:
    link = db.one("SELECT learner,revoked FROM links WHERE token=? AND kind='cal'", token)
    if link and link["revoked"]:
        raise HTTPException(404, "calendar link not found")
    row = plan.active_row(link["learner"]) if link else db.one("SELECT * FROM plans WHERE cal_token=?", token)
    if not row:
        raise HTTPException(404, "calendar link not found")
    return Response(plan.calendar(row["learner"], row), media_type="text/calendar")


@router.get("/api/plan/shared/{token}")
def shared(token: str) -> dict:
    link = db.one("SELECT learner,revoked FROM links WHERE token=? AND kind='progress'", token)
    if link and link["revoked"]:
        raise HTTPException(404, "share link not found")
    row = plan.active_row(link["learner"]) if link else db.one("SELECT * FROM plans WHERE view_token=?", token)
    if not row:
        raise HTTPException(404, "share link not found")
    out = plan.payload(row["learner"], row["tz"] or 0, row["id"], shared=True)
    out.pop("draft", None)
    out.pop("plans", None)
    return out


@router.get("/api/plan/{pid}/changes")
def changes(pid: str, before: int | None = None, x_learner: str | None = Header(default=None)) -> dict:
    learner = _reader(x_learner)
    plan.owned_row(learner, pid)
    rows = db.rows("SELECT * FROM plan_events WHERE plan=? AND id<? ORDER BY id DESC LIMIT 20", pid, before or 2**63 - 1)
    return {"events": [dict(r) for r in rows], "next": rows[-1]["id"] if len(rows) == 20 else None}


@router.get("/api/plan/{pid}/trapsheet")
def trapsheet(pid: str, x_learner: str | None = Header(default=None)) -> dict:
    learner = _reader(x_learner)
    plan.owned_row(learner, pid)
    traps = progress.open_traps(learner, subject="math")[:10]
    example = deps.part("api_bank", "example")
    entries = []
    for trap in traps:
        if not trap.get("label"):
            continue
        item = None
        if example:
            try:
                item = example(trap["template"], want=trap["norm"] or None)
                raw = generate(trap["template"], item["seed"])
                item["key"] = str(raw.answer)
                item["rationale"] = raw.rationale
            except (HTTPException, TypeError):
                pass
        entries.append({"name": trap["label"], "hits": trap["hits"], "tell": trap["label"],
                        "template": trap["template"], "example": item})
    return {"entries": entries}


@router.post("/api/plan/{pid}/rwlog")
def rwlog(pid: str, body: dict, x_learner: str | None = Header(default=None)) -> dict:
    learner = _writer(x_learner)
    _active(learner, pid)
    return {"logged": plan.log_rw(learner, body.get("rows"), source="task" if body.get("task") else "bluebook",
                                  ref=body.get("task") or pid, day=body.get("day"))}
