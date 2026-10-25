"""Review's model (spec/rebuild-v2.md §3.9; spec/v2-upgrades/review.md V1-V19).

Pure functions over attempts, traps, saved, flags and trap_log, read by
api_review.py and by other sections through deps.part('review', name) (§2.9):

  due(learner, tz)            V1 / R56: today's frozen review list, its cap and what is left
  resolve_drill(learner, body) V1: {source:'due', box | count} as a drill body (R10's registry)
  saved_due(learner, tz)      V3: saved questions due today on the 1-3-7-21 ladder
  blind(learner)              V5: open traps whose latest miss was sure (rushed misses never)
  counts(learner, tz)         the stat strip, tab counts, Today, Me and the badge
  trapsheet(learner, n)       V19 / R60: the top traps, each with a worked example
  progress_part(learner, tz)  V17: the read-only Mistakes block of the progress link
  ledger(learner, tz, weeks)  V9: mistakes made against fixed, week by week, and the forecast
  calibration(learner, ...)   V5: what certainty, answer changes and flags were worth

Nothing here writes except due()'s one frozen row a day (due_days) and snooze().
"""

from __future__ import annotations

import datetime as dt
import json
import math
import re
import statistics
from collections import Counter, defaultdict

from . import blueprint, db, deps, drill, practice, prefs, progress

LETTERS = "ABCD"
FILLER_LABEL = "A near-miss number, not a named mistake"
SLIP_LABEL = "Arithmetic slip"
DUE_KINDS = ("check", "relapsed", "sure", "half", "fading", "saved", "marked", "mistake", "keep_warm")
SAVED_LADDER = (1, 3, 7, 21)            # V3: days after each counted clean right; 4 = learned
DEFAULT_S = 95                          # R34: seconds a question with too little timing
OPEN_EVENTS = ("open", "relapse", "reopened")
SHUT_EVENTS = ("fixed", "dismissed", "remarked")


# ------------------------------------------------------------------ time

def utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def local_today(tz: int) -> dt.date:
    """tz is X-Tz, JavaScript's getTimezoneOffset(): minutes behind UTC."""
    return (utcnow() - dt.timedelta(minutes=tz)).date()


def utc_of(day: dt.date, tz: int) -> str:
    """The UTC instant a local day starts, as stored timestamps are written."""
    start = dt.datetime.combine(day, dt.time(), dt.timezone.utc) + dt.timedelta(minutes=tz)
    return start.isoformat(timespec="seconds")


def local_day(at: str | None, tz: int) -> dt.date | None:
    return progress._local_day(at, tz) if at else None


def short(at: str | dt.date | None, tz: int = 0) -> str | None:
    """'Sep 21' in the learner's day."""
    if not at:
        return None
    d = at if isinstance(at, dt.date) else local_day(at, tz)
    return f"{d:%b} {d.day}"


# ------------------------------------------------------------------ the bank

def math_topics(subject: str = "math") -> dict:
    return progress.topics(subject)


def in_subject(column: str, subject: str = "math") -> tuple[str, list]:
    """`column IN (the subject's topics)`, the one subject filter (G11)."""
    slugs = list(math_topics(subject)) or [""]
    return f"{column} IN ({','.join('?' for _ in slugs)})", slugs


def item(template: str, seed: int):
    return progress._item(template, seed)


def question(template: str, seed: int, qid: str = "q") -> dict | None:
    """The stored form of one exact question, key included (never served whole)."""
    try:
        it = item(template, seed)
        card = practice.Card.of(template, seed, it, practice.topic_of(template))
    except Exception:
        return None
    q = practice.to_question(card, 1)
    q["id"] = qid
    return q


def skill_of(template: str, seed: int | None = None) -> str:
    if deps.subject_of(template) == "rw":       # an R&W item's own skill names its passage: show its type
        return progress.rw_label(template)
    if seed is not None:
        try:
            return practice._skill(template, seed)
        except Exception:
            pass
    kinds = blueprint.kinds().get(template)
    return kinds["skill"] if kinds else template


def cap(text: str | None) -> str | None:
    return text[:1].upper() + text[1:] if text else text


def given_label(fmt: str | None, given) -> str | None:
    """C for an option index, the typed value for a grid-in, None for a blank."""
    if given is None or given == "":
        return None
    if fmt == "mcq":
        try:
            return LETTERS[int(given)]
        except (ValueError, IndexError, TypeError):
            return str(given)
    return str(given)


def option_labels(q: dict) -> list[str | None]:
    """Every option's misconception: a capitalised label, None at the key, the
    filler as a near-miss number (Review §8, §3.9.5 item)."""
    if q.get("type") != "mcq":
        return []
    out = []
    key = LETTERS.index(q["answer"]) if q.get("answer") in LETTERS else None
    for i, r in enumerate(q.get("reasons") or ()):
        if i == key:
            out.append(None)
        elif not r or progress.norm(r) == progress.FILLER:
            out.append(FILLER_LABEL)
        else:
            out.append(cap(r))
    return out


def level(template: str, tier: str) -> dict:
    from . import ratings
    lv = ratings.level(template, tier)
    return {"level": lv["level"], "rough": lv["rough"]}


def budget_fn():
    """drill.budget_ms without a query a call: P16's tier budget, or the crowd's
    median right time once 20 answers are in."""
    levels = drill.levels()

    def budget(template: str, tier: str) -> int:
        default = drill.TIER_BUDGET[deps.subject_of(template)].get(tier, 95_000)
        m = levels.get((template, tier), {})
        med = m.get("median_ms_right")
        return max(round(default * .6), min(round(default * 1.6), med)) if med and m.get("n", 0) >= 20 else default
    return budget


def level_fn():
    """ratings.level for every (template, tier) from one read of item_ratings."""
    from . import ratings
    rated = {(r["template"], r["tier"]): (r["rating"], r["n"]) for r in db.rows("SELECT * FROM item_ratings")}

    def lv(template: str, tier: str) -> tuple[int, bool]:
        rating, n = rated.get((template, tier), (ratings.TIER_PRIOR.get(tier, 1100.0), 0))
        return ratings.level_of(rating), n < ratings.MEASURED
    return lv


def sql_functions() -> tuple:
    """rv_budget(template, tier) and rv_level(template, tier) for this request's
    queries, so filters on time against budget and on L1-L7 stay in SQL."""
    budget, lv = budget_fn(), level_fn()
    c = db.conn()
    c.create_function("rv_budget", 2, lambda t, d: budget(t or "", d or "medium"), deterministic=True)
    c.create_function("rv_level", 2, lambda t, d: lv(t or "", d or "medium")[0], deterministic=True)
    return budget, lv


# ------------------------------------------------------------------ sittings

KIND_LABEL = {"drill": "Practice", "challenge": "Challenge", "mock": "Section", "section": "Section",
              "module": "Module", "diagnostic": "Diagnostic", "custom": "Custom test", "paper": "Weekly module",
              "words": "Words", "spot": "Spot the trap"}
SOURCE_LABEL = {"practice": "Practice", "due": "Today's review", "section": "Section", "module": "Module",
                "diagnostic": "Diagnostic", "challenge": "Challenge", "qotd": "Question of the day",
                "review": "Review", "shared": "Shared set", "worksheet": "Worksheet", "custom": "Custom test",
                "paper": "Weekly module", "outside": "Logged by you"}
SOURCES = tuple(SOURCE_LABEL)

_CFG_SOURCE = "(CASE WHEN json_valid(s.cfg) THEN json_extract(s.cfg,'$.source') END)"
SOURCE_SQL = (f"(CASE WHEN a.session LIKE 'qotd%' THEN 'qotd' WHEN s.id IS NULL THEN 'practice'"
              f" WHEN s.shared_from IS NOT NULL OR {_CFG_SOURCE}='shared' THEN 'shared'"
              f" WHEN s.kind='drill' THEN CASE {_CFG_SOURCE} WHEN 'review' THEN 'review' WHEN 'due' THEN 'due'"
              f" WHEN 'warmup' THEN 'due' WHEN 'worksheet' THEN 'worksheet' ELSE 'practice' END"
              f" WHEN s.kind IN ('mock','section') THEN 'section' ELSE s.kind END)")


def source_of(session: str | None, row=None) -> str:
    """The Source filter's value for one sitting (§3.9.5 'source is derived')."""
    if session and session.startswith("qotd"):
        return "qotd"
    row = row if row is not None else (db.one("SELECT * FROM sessions WHERE id=?", session) if session else None)
    if row is None:
        return "practice"
    cfg = json.loads(row["cfg"] or "{}") if row["cfg"] else {}
    if row["shared_from"] or cfg.get("source") == "shared":
        return "shared"
    if row["kind"] == "drill":
        return {"review": "review", "due": "due", "warmup": "due", "worksheet": "worksheet"}.get(cfg.get("source"), "practice")
    return "section" if row["kind"] in ("mock", "section") else row["kind"]


def shows_feedback(row) -> bool:
    """A sitting that showed the key after each answer (not a test, not end mode)."""
    if row is None:
        return True
    if row["kind"] in deps.TEST_KINDS:
        return False
    cfg = json.loads(row["cfg"] or "{}") if row["cfg"] else {}
    return cfg.get("feedback", "instant") != "end"


def sitting_href(row) -> str | None:
    if row is None:
        return None
    if row["kind"] in ("drill", "challenge"):
        return f"/practice/session/?id={row['id']}&summary=1"
    return f"/results/report/?id={row['id']}"


def number_of(row, qid: str) -> tuple[int | None, int | None]:
    """(module, n) of a question in its sitting: M2 Q5, or Q17."""
    if row is None or not qid:
        return None, None
    if row["kind"] in ("mock", "section", "paper"):
        m = re.match(r"^m(\d)", qid)
        num = re.search(r"(\d+)$", qid)
        return (int(m[1]) if m else None), (int(num[1]) if num else None)
    for i, q in enumerate(progress._paper(row), 1):
        if q.get("id") == qid:
            return None, i
    num = re.search(r"(\d+)$", qid)
    return None, int(num[1]) if num else None


# ------------------------------------------------------------------ traps

def of(t) -> int:
    """Clean answers a trap needs in all: 1 for an Unsure, 2 otherwise."""
    return 1 if t["norm"] == "~unsure" else progress.OWED


def latest_misses(learner: str, subject: str = "math") -> dict[tuple[str, str], dict]:
    """The newest attempt behind each (template, norm): the wrong answer, or the
    flagged right one of an Unsure."""
    where, args = in_subject("topic", subject)
    out = {}
    for r in db.rows(f"SELECT * FROM attempts WHERE learner=? AND norm IS NOT NULL AND {where}"
                     " ORDER BY id", learner, *args):
        out[(r["template"], r["norm"])] = dict(r)
    return out


def trap_kind(t, miss: dict | None) -> str:
    spr = bool(miss and miss.get("fmt") == "spr")
    return progress.trap_kind(t["norm"], (miss or {}).get("miss_kind"), spr, t["topic"])


def trap_label(t) -> str:
    """Review §0: a named mistake is the concrete text of its latest miss; an
    unnamed grid-in miss and an Unsure are the skill; the filler is 'Arithmetic slip';
    an R&W miss is its question type, one name however many passages it was missed on."""
    if t["norm"] == progress.FILLER:
        return SLIP_LABEL
    if t["norm"] == "" and deps.subject_of(t["topic"]) == "rw":
        return progress.rw_label(t["template"])
    if t["norm"] in ("", "~unsure"):
        return cap(skill_of(t["template"], t["seed"] if t["seed"] is not None else None))
    return cap(t["reason"]) or t["label"]


def is_new(miss: dict | None, sittings: dict) -> bool:
    """V2: the latest miss came from a sitting that showed no feedback, and has no
    diagnosis yet."""
    if not miss or miss.get("correct") or miss.get("diag"):
        return False
    sid = miss.get("session")
    if not sid or sid.startswith("qotd"):
        return False
    if sid not in sittings:
        sittings[sid] = db.one("SELECT * FROM sessions WHERE id=?", sid)
    row = sittings[sid]
    return row is not None and not shows_feedback(row)


def status(t) -> str:
    """Relapsed beats Stuck beats Half fixed beats Open (V11, V14's cells)."""
    if t["relapses"]:
        return "relapsed"
    if t["hits"] >= 3:
        return "stuck"
    return "half" if t["owed"] < of(t) else "open"


def stuck(t) -> bool:
    return t["hits"] >= 3 or bool(t["relapses"])


def pts_fn(learner: str, subject: str = "math"):
    """V4 / U1: a trap's points, gain(t) x share, the formula of
    estimate.trap_pts computed once for every trap (gains is one model fit)."""
    from . import estimate
    g = estimate.gains(learner, subject)
    if not g:
        return lambda template, norm, topic: None
    gains = {x["topic"]: x["gain"] for x in g["skills"]}
    since = (utcnow() - dt.timedelta(days=60)).isoformat()
    wrong: Counter = Counter()
    per_topic: Counter = Counter()
    for r in db.rows("SELECT template, norm, topic FROM attempts WHERE learner=? AND correct=0"
                     " AND repeat=0 AND disputed=0 AND void IS NULL AND at>=?", learner, since):
        wrong[(r["template"], r["norm"])] += 1
        per_topic[r["topic"]] += 1

    def pts(template: str, norm: str, topic: str) -> int | None:
        gain, total = gains.get(topic), per_topic[topic]
        if not gain or not total:
            return None
        p = round(gain * wrong[(template, norm)] / total)
        return p if p >= 1 else None
    return pts


def per_test(learner: str) -> dict[str, float]:
    from . import estimate
    g = estimate.gains(learner)
    return {x["topic"]: x["per_test"] for x in g["skills"]} if g else {}


def rules(learner: str) -> dict[str, str]:
    """P21's type rules (notes.seed = -1), by template."""
    return {r["template"]: r["note"] for r in db.rows(
        "SELECT template, note FROM notes WHERE learner=? AND seed=-1 AND note!=''", learner)}


def habit_of(norm: str) -> dict | None:
    """U6's habit family of a norm, once server/habits.py exists."""
    family = deps.part("habits", "family")
    if not family or norm in progress.UNNAMED:
        return None
    got = family(norm)
    if isinstance(got, str):
        return {"id": got, "name": got.replace("_", " ").capitalize(), "tell": None}
    return got


# ------------------------------------------------------------------ blind spots (V5)

def blind(learner: str, subject: str = "math") -> dict[int, dict]:
    """T9's blind spots with V5's guard: a tagged Sure always counts; an
    inferred one ('fast', 'silent') only when the miss took at least 25% of its
    budget, since a faster miss is Rushed, never certainty. Each entry carries
    assumed (not tagged) and the attempt."""
    budget = budget_fn()
    out = {}
    for tid, t in progress.blind(learner, subject).items():
        a = db.one("SELECT difficulty, COALESCE(ms, sms) AS spent FROM attempts WHERE id=?", t["attempt"])
        assumed = t["why"] != "sure"
        if assumed and a and a["spent"] is not None and a["spent"] < 0.25 * budget(t["template"], a["difficulty"]):
            continue
        out[tid] = {**t, "assumed": assumed}
    return out


# ------------------------------------------------------------------ saved as a spaced deck (V3)

def saved_schedule(learner: str, tz: int = 0, subject: str = "math") -> dict[tuple[str, int], dict]:
    """Every saved question's place on the ladder: k counted clean rights on its
    template since the later of the save and the last miss (each 20 h after
    the one before), the next due day, and learned at k >= 4."""
    where, args = in_subject("topic", subject)
    saved = db.rows(f"SELECT * FROM saved WHERE learner=? AND {where}", learner, *args)
    if not saved:
        return {}
    templates = sorted({s["template"] for s in saved})
    marks = ",".join("?" for _ in templates)
    per: dict[str, list] = defaultdict(list)
    for r in db.rows(f"SELECT template, correct, at, repeat, flagged, guess, hints, conf, void, disputed"
                     f" FROM attempts WHERE learner=? AND template IN ({marks}) ORDER BY at, id", learner, *templates):
        per[r["template"]].append(r)
    today = local_today(tz)
    out = {}
    for s in saved:
        rows = per.get(s["template"], [])
        misses = [r["at"] for r in rows if not r["correct"] and r["void"] is None]
        start = max([s["at"]] + [m for m in misses if m >= s["at"]])
        counted: list[str] = []
        for r in rows:
            if r["at"] <= start or not r["correct"] or r["repeat"] or r["flagged"] or r["guess"] or r["hints"] \
                    or r["conf"] == "unsure" or r["void"] is not None or r["disputed"]:
                continue
            if not counted or dt.datetime.fromisoformat(r["at"]) - dt.datetime.fromisoformat(counted[-1]) >= dt.timedelta(hours=20):
                counted.append(r["at"])
        k = len(counted)
        learned = k >= len(SAVED_LADDER)
        base = counted[-1] if counted else start
        nxt = None if learned else local_day(base, tz) + dt.timedelta(days=SAVED_LADDER[k])
        out[(s["template"], s["seed"])] = {
            "template": s["template"], "seed": s["seed"], "topic": s["topic"], "saved_at": s["at"],
            "k": k, "box": min(k, len(SAVED_LADDER)), "learned": learned,
            "next": nxt.isoformat() if nxt else None, "due": bool(nxt and nxt <= today),
            "missed_since": bool(misses and misses[-1] >= s["at"])}
    return out


def saved_due(learner: str, tz: int = 0, subject: str = "math") -> list[dict]:
    """V3: the saved questions due today, oldest due first; [] with saved_spaced off."""
    if not prefs.get(learner, tz).get("saved_spaced", True):
        return []
    return sorted((v for v in saved_schedule(learner, tz, subject).values() if v["due"]),
                  key=lambda v: (v["next"], v["saved_at"]))


# ------------------------------------------------------------------ the daily list (V1, R56)

def median_s(learner: str) -> int:
    """The learner's median seconds a question over 60 days, 95 under 20 timed answers."""
    since = (utcnow() - dt.timedelta(days=60)).isoformat()
    spent = [r["s"] for r in db.rows("SELECT COALESCE(ms, sms) AS s FROM attempts WHERE learner=? AND at>=?"
                                     " AND COALESCE(ms, sms) IS NOT NULL AND repeat=0 AND void IS NULL",
                                     learner, since)]
    if len(spent) < 20:
        return DEFAULT_S
    return max(10, round(statistics.median(spent) / 1000))


def cap_of(minutes: int, median: int) -> int | None:
    """The list fits the minutes on the pill: None for All."""
    if not minutes:
        return None
    return max(3, min(60, math.floor(minutes * 60 / median)))


def _candidates(learner: str, tz: int, subject: str, before: str) -> list[dict]:
    """The ordered keys as they stood at `before` (the local midnight, UTC):
    one per template, the first reason wins, in R56's order."""
    today = local_today(tz)
    out: list[dict] = []
    taken: set[str] = set()

    def add(kind: str, template: str, **extra) -> None:
        if template in taken:
            return
        taken.add(template)
        out.append({"key": f"due:{kind}:{template}", "kind": kind, "template": template, **extra})

    for c in progress.due_rechecks(learner, today.isoformat()):
        t = db.one("SELECT closed FROM traps WHERE id=?", c["trap_id"])
        if deps.subject_of(c["topic"]) == subject and t and t["closed"] and t["closed"] < before:
            add("check", c["template"], trap=c["trap_id"], topic=c["topic"], serve=c["serve"])
    opens = [t for t in progress.open_traps(learner)
             if deps.subject_of(t["topic"]) == subject and t["opened"] < before]
    for t in sorted((t for t in opens if t["relapses"]), key=lambda t: t["last"], reverse=True):
        add("relapsed", t["template"], trap=t["id"], topic=t["topic"])
    sure = blind(learner, subject)
    for t in opens:
        if t["id"] in sure:
            add("sure", t["template"], trap=t["id"], topic=t["topic"])
    for t in opens:
        if t["owed"] == 1:
            add("half", t["template"], trap=t["id"], topic=t["topic"])
    warm = progress.warmup_candidates(learner, tz, subject)
    for f in warm["fading"]:
        add("fading", f["template"], topic=f["topic"])
    for s in saved_due(learner, tz, subject):
        if s["saved_at"] < before:
            add("saved", s["template"], topic=s["topic"], saved=[s["template"], s["seed"]])
    for m in warm["marked"]:
        if m["flagged"] < before:
            add("marked", m["template"], topic=m["topic"], flag=[m["session"], m["qid"]], seed=m["seed"])
    pts = pts_fn(learner, subject)
    for t in sorted(opens, key=lambda t: (-(pts(t["template"], t["norm"], t["topic"]) or 0), -t["hits"], t["id"])):
        add("mistake", t["template"], trap=t["id"], topic=t["topic"])
    for k in warm["keep_warm"]:
        key = f"due:keep_warm:{k['topic']}"
        if key not in {x["key"] for x in out}:
            out.append({"key": key, "kind": "keep_warm", "template": None, "topic": k["topic"]})
    return out


def frozen(learner: str, tz: int, subject: str = "math") -> tuple[str, list[dict]]:
    """Today's keys, computed on the first read of the local day and kept."""
    day = local_today(tz)
    row = db.one("SELECT keys FROM due_days WHERE learner=? AND subject=? AND day=?", learner, subject, day.isoformat())
    if row:
        return day.isoformat(), json.loads(row["keys"] or "[]")
    keys = _candidates(learner, tz, subject, utc_of(day, tz))
    if not db.is_sample(learner):
        db.run("INSERT OR IGNORE INTO due_days(learner,subject,day,keys) VALUES (?,?,?,?)",
               learner, subject, day.isoformat(), json.dumps(keys))
    return day.isoformat(), keys


def _done_today(learner: str, tz: int) -> tuple[set, set]:
    """Templates and topics with a counted first-try answer today (not a repeat)."""
    since = utc_of(local_today(tz), tz)
    rows = db.rows("SELECT DISTINCT template, topic FROM attempts WHERE learner=? AND at>=? AND repeat=0"
                   " AND void IS NULL AND disputed=0", learner, since)
    return {r["template"] for r in rows}, {r["topic"] for r in rows}


def _is_done(k: dict, templates: set, topics: set) -> bool:
    if k["kind"] == "keep_warm":
        return k.get("topic") in topics
    return k["template"] in templates or (k.get("serve") in templates)


def _why(learner: str, k: dict, t, tz: int, sure: dict, sched: dict, warm: dict) -> tuple[str, str | None]:
    """(the why line, since) for one due row."""
    kind = k["kind"]
    if kind == "check":
        return (f"Fixed {short(t['closed'], tz)} · checking it holds" if t and t["closed"] else "Check-in due"), \
            t["closed"] if t else None
    if kind == "relapsed" and t:
        return f"Relapsed ×{t['relapses']} · missed {short(t['last'], tz)}", t["last"]
    if kind == "sure" and t:
        b = sure.get(t["id"]) or {}
        at = b.get("at") or t["last"]
        return (f"Fast answer · assumed sure · {short(at, tz)}" if b.get("assumed") else f"You were sure · {short(at, tz)}"), at
    if kind == "half":
        return "1 clean answer closes it", t["last"] if t else None
    if kind == "fading":
        f = warm.get(k["template"]) or {}
        return f"Right {short(f.get('last'), tz)} · fading", f.get("last")
    if kind == "saved":
        s = sched.get(tuple(k["saved"])) or {}
        gap = SAVED_LADDER[min(s.get("k", 0), len(SAVED_LADDER) - 1)]
        return f"Saved {short(s.get('saved_at'), tz)} · back after {gap} day{'s' if gap != 1 else ''}", s.get("saved_at")
    if kind == "marked":
        f = db.one("SELECT at FROM flags WHERE learner=? AND session=? AND qid=?", learner, *k["flag"])
        return f"Flagged {short(f['at'], tz) if f else ''} · not right since".replace("  ", " "), f["at"] if f else None
    if kind == "mistake" and t:
        return f"Missed {t['hits']}× · last {short(t['last'], tz)}", t["last"]
    if kind == "keep_warm":
        return "Strong · kept warm", None
    return "", None


def due(learner: str, tz: int = 0, subject: str = "math", minutes: int | None = None) -> dict:
    """V1: today's list is the first `cap` frozen keys plus any later key done
    today; done items keep their place, snoozed ones go to the end; left =
    today's list - done - snoozed. `minutes` overrides prefs.review_minutes."""
    p = prefs.get(learner, tz)
    box = p.get("review_minutes", 10) if minutes is None else minutes
    median = median_s(learner)
    cut = cap_of(box, median)
    day, keys = frozen(learner, tz, subject)
    templates, topics = _done_today(learner, tz)
    snoozed = {k for k, d in (p.get("snooze") or {}).items() if d == day}
    head = keys if cut is None else keys[:cut]
    later = [] if cut is None else keys[cut:]
    listed = head + [k for k in later if _is_done(k, templates, topics)]
    waiting = [k for k in later if not _is_done(k, templates, topics)]
    listed = [k for k in listed if k["key"] not in snoozed] + [k for k in listed if k["key"] in snoozed]
    names = math_topics(subject)
    pts = pts_fn(learner, subject)
    sure = blind(learner, subject)
    sched = saved_schedule(learner, tz, subject)
    warm = {f["template"]: f for f in progress.warmup_candidates(learner, tz, subject)["fading"]}
    items = []
    for k in listed:
        t = db.one("SELECT * FROM traps WHERE id=?", k["trap"]) if k.get("trap") else None
        template = k["template"]
        topic = k.get("topic") or (practice.topic_of(template) if template else None)
        why, since = _why(learner, k, t, tz, sure, sched, warm)
        tier = None
        if t:
            last = db.one("SELECT difficulty FROM attempts WHERE learner=? AND template=? AND norm IS NOT NULL"
                          " ORDER BY (norm=?) DESC, id DESC LIMIT 1", learner, t["template"], t["norm"])
            tier = last["difficulty"] if last else None
        label = trap_label(t) if t else cap(skill_of(template)) if template else \
            (names[topic].name if topic in names else topic)
        items.append({
            "key": k["key"], "kind": k["kind"], "template": template, "trap_id": k.get("trap"),
            "saved": k.get("saved"), "flag": k.get("flag"),
            "topic": topic, "name": names[topic].name if topic in names else None,
            "domain": names[topic].domain if topic in names else None,
            "label": label, "skill": cap(skill_of(template)) if template else None, "tier": tier,
            "why": why, "since": since,
            "pts": pts(t["template"], t["norm"], t["topic"]) if t else None,
            "owed": t["owed"] if t and t["closed"] is None else None,
            "done": _is_done(k, templates, topics), "snoozed": k["key"] in snoozed})
    left = sum(1 for i in items if not i["done"] and not i["snoozed"])
    fc = {r["day"]: r["checks"] for r in progress.due_forecast(learner, tz, 7)}
    saved_on = Counter(v["next"] for v in sched.values() if v["next"] and not v["learned"])
    forecast = [{"day": d, "checks": fc.get(d, 0), "saved": saved_on.get(d, 0)}
                for d in ((local_today(tz) + dt.timedelta(days=i)).isoformat() for i in range(0, 7))]
    forecast[0]["checks"] = sum(1 for i in items if i["kind"] == "check")
    return {"subject": subject, "day": day, "cap": cut, "median_s": median, "minutes": box,
            "left": left, "done": sum(1 for i in items if i["done"]), "total": len(items),
            "waiting": len(waiting), "snoozed": sum(1 for i in items if i["snoozed"]),
            "left_minutes": round(left * median / 60),
            "kinds": dict(Counter(i["kind"] for i in items)),
            "quick_wins": sum(1 for i in items if i["kind"] == "half" and not i["done"]),
            "closes": sum(1 for i in items if not i["done"] and i["owed"] == 1),
            "items": items, "forecast": forecast, "waiting_keys": [k["key"] for k in waiting]}


def snooze(learner: str, tz: int, key: str, undo: bool = False, subject: str = "math") -> dict:
    """V1's Not today, kept in prefs.snooze {key: local day} (pruned on write)."""
    today = local_today(tz).isoformat()
    store = dict(prefs.get(learner, tz).get("snooze") or {})
    if undo:
        store.pop(key, None)
    else:
        store[key] = today
    prefs.put(learner, {"snooze": store})
    return {"left": due(learner, tz, subject)["left"], "key": key, "snoozed": not undo}


def _mixed(entries: list[dict]) -> list[dict]:
    """No two in a row from one topic when two or more topics are in play."""
    left = list(entries)
    out: list[dict] = []
    while left:
        pick = next((e for e in left if not out or e.get("topic") != out[-1].get("topic")), left[0])
        left.remove(pick)
        out.append(pick)
    return out


def _zone(learner: str, body: dict) -> int:
    """The registry passes no X-Tz: body.zone when the caller sends it, else the
    zone whose local day is the learner's latest freeze, else UTC."""
    z = body.get("zone")
    if type(z) is int and -840 <= z <= 720:
        return z
    row = db.one("SELECT day FROM due_days WHERE learner=? AND subject='math' ORDER BY day DESC LIMIT 1", learner)
    if row:
        for z in sorted(range(-840, 721, 60), key=abs):
            if local_today(z).isoformat() == row["day"]:
                return z
    return 0


def resolve_drill(learner: str, body: dict) -> dict:
    """V1's session as an ordinary drill body (R10's registry): one fresh question
    per undone, unsnoozed item of today's list (mixed by topic), then while the
    box has time the waiting keys, other open traps by points and the
    right-but-slow types. box None (or 0) is All: every frozen key, then every
    open trap max(owed) times, at most 120. count instead of box takes that
    many in the same order (Plan's recheck, the warmup alias)."""
    tz = _zone(learner, body)
    d = due(learner, tz)
    counted = "count" in body
    box = None if counted else body.get("box", prefs.get(learner, tz).get("review_minutes", 10))
    if box is not None and (type(box) is not int or not (box == 0 or 5 <= box <= 60)):
        drill._invalid("box", "use 5–60 minutes, or null for all")
    box = box or None
    if counted and (type(body["count"]) is not int or not 1 <= body["count"] <= drill.MAX_FIXED):
        drill._invalid("count", "use 1–120")
    drop = body.get("drop") or []
    if not isinstance(drop, list) or not all(isinstance(k, str) for k in drop):
        drill._invalid("drop", "expected due keys")
    traps = {t["id"]: t for t in progress.open_traps(learner)}

    def entry(k: dict) -> dict | None:
        trap_id = k.get("trap_id", k.get("trap"))
        t = traps.get(trap_id) or (db.one("SELECT * FROM traps WHERE id=?", trap_id) if trap_id else None)
        template = k.get("template")
        if template is None and k.get("topic"):     # keep warm: the topic's least answered type
            names = practice.catalogue()["by_topic"].get(k["topic"], ())
            n = Counter(r["template"] for r in db.rows("SELECT template FROM attempts WHERE learner=? AND topic=?",
                                                       learner, k["topic"]))
            template = min(names, key=lambda x: (n[x], x)) if names else None
        if template is None:
            return None
        serve = progress.checkin_template(t) if k.get("kind") == "check" and t else template
        return {"template": serve, "topic": practice.topic_of(serve), "seed": (k.get("saved") or [None, 0])[1] or 0,
                "norm": t["norm"] if t and progress.named(t["norm"]) else None}

    listed = _mixed([e for e in (entry(i) for i in d["items"]
                                 if not i["done"] and not i["snoozed"] and i["key"] not in drop) if e])
    keys = {k["key"]: k for k in frozen(learner, tz)[1]}
    waiting = [e for e in (entry(keys[k]) for k in d["waiting_keys"] if k in keys and k not in drop) if e]
    pts = pts_fn(learner)
    ranked = sorted(traps.values(), key=lambda t: (-(pts(t["template"], t["norm"], t["topic"]) or 0), -t["hits"], t["id"]))
    queue = listed + waiting
    if box is None and not counted:
        for t in ranked:                            # All: every open trap max(owed) times
            have = sum(1 for e in queue if e["template"] == t["template"])
            queue += [{"template": t["template"], "topic": t["topic"], "seed": 0,
                       "norm": t["norm"] if progress.named(t["norm"]) else None}] * max(0, t["owed"] - have)
        limit = drill.MAX_FIXED
    else:
        have = {e["template"] for e in queue}
        for t in ranked:
            if t["template"] not in have:
                have.add(t["template"])
                queue.append({"template": t["template"], "topic": t["topic"], "seed": 0,
                              "norm": t["norm"] if progress.named(t["norm"]) else None})
        for template, f in progress.fluency(learner, drill.budget_ms).items():
            if f["slow_right"] and template not in have:
                have.add(template)
                queue.append({"template": template, "topic": practice.topic_of(template), "seed": 0, "norm": None})
        limit = body["count"] if counted else max(len(listed), math.floor(box * 60 / d["median_s"]))
    queue = queue[:limit]
    if not queue:
        drill._empty("nothing_due")
    out = {k: v for k, v in body.items() if k not in ("source", "box", "drop", "count", "zone")}
    out.update({"source": "due", "pool": "items", "exact": False, "count": len(queue),
                "ids": [[e["template"], e["seed"]] for e in queue],
                "want": {e["template"]: "^" + re.escape(e["norm"]) + "$" for e in queue if e["norm"]},
                "feedback": "instant", "repairs": "next", "order": "given"})
    if box is not None:
        out["box"] = box
    return out


# ------------------------------------------------------------------ counts

def _closing_state(t, today: dt.date) -> str:
    """V10's check-in state of a fixed trap."""
    if t["closed_how"] == "dismissed":
        return "dismissed"
    if t["checks"] >= 3 or (t["checks"] and not t["due"]):
        return "held3"
    if t["due"] and t["due"] <= today.isoformat():
        return "due"
    return f"held{t['checks']}" if t["checks"] else "unchecked"


def ledger_deltas(learner: str, subject: str | None = None) -> list[tuple[str, int, str]]:
    """(at, +1 | -1, event) for every change to the open count, from trap_log;
    a discard or restore counts as the event it undid, reversed or redone; `subject` keeps one section's."""
    rows = [r for r in db.rows("SELECT * FROM trap_log WHERE learner=? ORDER BY id", learner)
            if subject is None or deps.subject_of(r["template"]) == subject]
    by_id = {r["id"]: r for r in rows}
    out = []
    for r in rows:
        e = r["event"]
        if e in OPEN_EVENTS:
            out.append((r["at"], 1, e))
        elif e in SHUT_EVENTS:
            out.append((r["at"], -1, e))
        elif e == "restored" and r["undoes"] in by_id:
            undid = by_id[r["undoes"]]
            base = by_id.get(undid["undoes"]) if undid["event"] == "discarded" else undid
            if base is not None and base["event"] in ("open", "fixed"):
                out.append((r["at"], 1 if base["event"] == "open" else -1, "restored"))
            elif undid["event"] == "dismissed":
                out.append((r["at"], 1, "restored"))
        elif e == "discarded" and r["undoes"] in by_id:
            base = by_id[r["undoes"]]["event"]
            if base in ("open", "fixed"):
                out.append((r["at"], -1 if base == "open" else 1, "discarded"))
    return out


def counts(learner: str, tz: int = 0, subject: str = "math") -> dict:
    """Every figure of the stat strip and the tab counts, from SQL (§3.9.5 and
    override 30); subject-aware."""
    where, args = in_subject("topic", subject)
    today = local_today(tz)
    week = (utcnow() - dt.timedelta(days=7)).isoformat()
    month = (utcnow() - dt.timedelta(days=30)).isoformat()
    opens = [t for t in progress.open_traps(learner) if t["topic"] in args]
    misses = latest_misses(learner, subject)
    sittings: dict = {}
    fixed = db.rows(f"SELECT * FROM traps WHERE learner=? AND closed IS NOT NULL AND closed_how IN ('fixed','transfer')"
                    f" AND {where}", learner, *args)
    days = [(dt.datetime.fromisoformat(t["closed"]) - dt.datetime.fromisoformat(t["opened"])).total_seconds() / 86400
            for t in fixed]
    flags = visible_flags(learner, subject)
    sched = saved_schedule(learner, tz, subject)
    spaced = prefs.get(learner, tz).get("saved_spaced", True)
    saved = db.rows(f"SELECT s.template, s.seed, n.note, (SELECT COUNT(*) FROM attempts a WHERE a.learner=s.learner"
                    f" AND a.template=s.template AND a.seed=s.seed) AS tries FROM saved s LEFT JOIN notes n"
                    f" ON n.learner=s.learner AND n.template=s.template AND n.seed=s.seed"
                    f" WHERE s.learner=? AND s.{where}", learner, *args)
    per_template: dict[str, int] = {}
    for t in opens:
        per_template[t["template"]] = max(per_template.get(t["template"], 0), t["owed"])
    pts = pts_fn(learner, subject)
    stakes = [pts(t["template"], t["norm"], t["topic"]) for t in opens]
    d = due(learner, tz, subject)
    diag = db.rows(f"SELECT diag, norm, reason FROM attempts WHERE learner=? AND diag IS NOT NULL AND diag!='skip' AND {where}",
                   learner, *args)
    since = (utcnow() - dt.timedelta(days=7)).isoformat()
    delta = sum(s for at, s, _ in ledger_deltas(learner, subject) if at >= since)
    b = blind(learner, subject)
    return {
        "subject": subject,
        "open": len(opens),
        "half": sum(1 for t in opens if t["owed"] < of(t)),
        "relapsed": sum(1 for t in opens if t["relapses"]),
        "unsure": sum(1 for t in opens if t["norm"] == "~unsure"),
        "new": sum(1 for t in opens if is_new(misses.get((t["template"], t["norm"])), sittings)),
        "blind": len(b), "stuck": sum(1 for t in opens if stuck(t)),
        "marked": len(flags),
        "marked_right": sum(1 for f in flags if f["correct"]),
        "marked_during": sum(1 for f in flags if f["during"]),
        "saved": len(saved), "noted": sum(1 for s in saved if s["note"]),
        "saved_unanswered": sum(1 for s in saved if not s["tries"]),
        "saved_due": sum(1 for v in sched.values() if v["due"]) if spaced else 0,
        "learned": sum(1 for v in sched.values() if v["learned"]) if spaced else 0,
        "fixed": len(fixed),
        "fixed_week": sum(1 for t in fixed if t["closed"] >= week),
        "median_days": round(statistics.median(days), 1) if days else None,
        "held": sum(1 for t in fixed if t["checks"]),
        "unchecked": sum(1 for t in fixed if not t["checks"]),
        "dismissed": db.one(f"SELECT COUNT(*) AS n FROM traps WHERE learner=? AND closed IS NOT NULL"
                            f" AND closed_how='dismissed' AND {where}", learner, *args)["n"],
        "recovered_month": sum(r["pts"] or 0 for r in db.rows(
            "SELECT template, pts FROM trap_log WHERE learner=? AND event='fixed' AND at>=?", learner, month)
            if deps.subject_of(r["template"]) == subject),
        "due": sum(1 for c in progress.due_rechecks(learner, today.isoformat()) if c["topic"] in args),
        "due_left": d["left"], "due_total": d["total"], "waiting": d["waiting"],
        "answers": db.one(f"SELECT COUNT(*) AS n FROM attempts WHERE learner=? AND void IS NULL AND {where}",
                          learner, *args)["n"],
        "redo_questions": sum(per_template.values()), "redo_templates": len(per_template),
        "stake_total": sum(x for x in stakes if x) if any(x is not None for x in stakes) else None,
        "open_week_delta": delta,
        # named right: the miss's norm, or (an R&W miss files unnamed) its picked option's reason (api_review.why)
        "diag_n": len(diag), "diag_right": sum(1 for r in diag if r["diag"] in (r["norm"], progress.norm(r["reason"] or ""))),
        "worksheets_waiting": db.one("SELECT COUNT(*) AS n FROM sessions WHERE learner=? AND kind='drill'"
                                     " AND finished IS NULL AND abandoned IS NULL AND json_valid(cfg)"
                                     " AND json_extract(cfg,'$.source')='worksheet'"
                                     " AND COALESCE(json_extract(cfg,'$.subject'),'math')=?", learner, subject)["n"],
    }


def visible_flags(learner: str, subject: str = "math") -> list[dict]:
    """Flags a student may see: a drill's, a finished sitting's, and a
    challenge's once that question is answered (§4 Hidden until finished).
    Each carries its answer (correct, given) and during (set in the sitting)."""
    where, args = in_subject("f.topic", subject)
    out = []
    for f in db.rows(f"SELECT f.*, x.kind AS skind, x.finished, x.started, x.answers, x.cfg AS scfg FROM flags f"
                     f" JOIN sessions x ON x.id=f.session WHERE f.learner=? AND {where} ORDER BY f.at DESC",
                     learner, *args):
        a = db.one("SELECT * FROM attempts WHERE learner=? AND session=? AND qid=? ORDER BY id LIMIT 1",
                   learner, f["session"], f["qid"])
        if f["skind"] == "challenge" and not a:
            continue
        if f["skind"] != "drill" and f["skind"] != "challenge" and not f["finished"]:
            continue
        during = bool(f["finished"] and f["at"] <= f["finished"]) or bool(a and f["at"] <= a["at"])
        out.append({**dict(f), "attempt": dict(a) if a else None, "correct": bool(a and a["correct"]),
                    "during": during})
    return out


# ------------------------------------------------------------------ the trap sheet (V19, R60)

def trapsheet(learner: str, n: int = 10, subject: str = "math") -> dict:
    """U6's top habits (once habits.py exists), then the top open or relapsed
    traps by points, then hits; each with a reserved example walked for the
    trap (F5's example with want), the rule and the dodge record."""
    from . import api_bank
    names = math_topics(subject)
    pts = pts_fn(learner, subject)
    rule = rules(learner)
    opens = [t for t in progress.open_traps(learner) if t["topic"] in names]
    ranked = sorted(opens, key=lambda t: (-(pts(t["template"], t["norm"], t["topic"]) or 0), -t["relapses"],
                                          -t["hits"], t["id"]))
    habits = []
    top = deps.part("habits", "top")
    if top:
        habits = list(top(learner))[:3]
    entries = []
    for t in ranked[:n]:
        kind = trap_kind(t, None)
        example = None
        try:
            if t["norm"] == "" and deps.subject_of(t["topic"]) == "rw" and t["seed"] is not None:
                # an R&W trap prints the question it was missed on: a written bank item is spent once shown,
                # and every print of the sheet would spend ten more
                card = practice.Card.of(t["template"], t["seed"], drill.generate(t["template"], t["seed"]), t["topic"])
                ex = {"seed": t["seed"], "question": practice.to_question(card, 1), "trap_index": None}
            else:
                ex = api_bank.example(t["template"], want=t["norm"] if progress.named(t["norm"]) else None, learner=learner)
            q = ex["question"]
            example = {"seed": ex["seed"], "text": q.get("text"), "stem": q["stem"], "choices": q["choices"], "latex": q.get("latex"),
                       "figure": q.get("figure"), "table": q.get("table"), "type": q["type"],
                       "answer": q["answer"], "trap_index": ex["trap_index"],
                       "rationale": (q["rationale"] or "").split(". ")[0].rstrip(".") + "." if q.get("rationale") else None}
        except Exception:
            example = None
        entries.append({"trap_id": t["id"], "template": t["template"], "norm": t["norm"],
                        "label": trap_label(t), "kind": kind, "hits": t["hits"], "relapses": t["relapses"],
                        "topic": t["topic"], "name": names[t["topic"]].name, "skill": cap(skill_of(t["template"])),
                        "pts": pts(t["template"], t["norm"], t["topic"]), "habit": habit_of(t["norm"]),
                        "rule": rule.get(t["template"]), "dodged": dodged(learner, t["template"], t["norm"]),
                        "example": example})
    day = local_today(0)
    return {"subject": subject, "title": f"Your traps · {short(day)} · {len(entries)} of {len(opens)}",
            "habits": habits, "entries": entries, "total": len(opens)}


def dodged(learner: str, template: str, norm: str, last: int = 5) -> dict | None:
    """P6: of the last answers that offered this norm, how many dodged it."""
    if norm in progress.UNNAMED:
        return None
    rows = db.rows("SELECT norm, correct FROM attempts WHERE learner=? AND repeat=0 AND offered IS NOT NULL"
                   " AND EXISTS (SELECT 1 FROM json_each(attempts.offered) WHERE value=?) ORDER BY id DESC LIMIT ?",
                   learner, norm, last)
    if not rows:
        return None
    return {"dodged": sum(1 for r in rows if r["norm"] != norm), "of": len(rows)}


def dodged_elsewhere(learner: str, template: str, norm: str) -> int:
    """V7: other question types where this norm was on offer and not chosen."""
    if norm in progress.UNNAMED:
        return 0
    return db.one("SELECT COUNT(DISTINCT template) AS n FROM attempts WHERE learner=? AND template!=? AND repeat=0"
                  " AND offered IS NOT NULL AND (norm IS NULL OR norm!=?)"
                  " AND EXISTS (SELECT 1 FROM json_each(attempts.offered) WHERE value=?)",
                  learner, template, norm, norm)["n"]


# ------------------------------------------------------------------ the ledger (V9)

def _week_start(d: dt.date, start: str) -> dt.date:
    shift = d.weekday() if start == "mon" else (d.weekday() + 1) % 7
    return d - dt.timedelta(days=shift)


def ledger(learner: str, tz: int = 0, weeks: int = 12, subject: str = "math") -> dict:
    """Mistakes made (open events, relapses apart) against fixed, per local week,
    with the open count at each week's end counted back from today's; the
    4-week rate; and, with an exam date, when the list reaches zero."""
    weeks = max(1, min(52, weeks))
    p = prefs.get(learner, tz)
    today = local_today(tz)
    first = _week_start(today, p.get("week_start", "mon")) - dt.timedelta(weeks=weeks - 1)
    rows: dict[dt.date, dict] = {first + dt.timedelta(weeks=i): {"opened": 0, "relapsed": 0, "fixed": 0, "net": 0}
                                 for i in range(weeks)}
    for r in db.rows("SELECT event, at, template FROM trap_log WHERE learner=? AND at>=?", learner, utc_of(first, tz)):
        if deps.subject_of(r["template"]) != subject:
            continue
        w = _week_start(local_day(r["at"], tz), p.get("week_start", "mon"))
        if w in rows:
            if r["event"] == "open":
                rows[w]["opened"] += 1
            elif r["event"] == "relapse":
                rows[w]["relapsed"] += 1
            elif r["event"] == "fixed":
                rows[w]["fixed"] += 1
    for at, sign, _ in ledger_deltas(learner, subject):
        w = _week_start(local_day(at, tz), p.get("week_start", "mon"))
        if w in rows:
            rows[w]["net"] += sign
    open_now = len([t for t in progress.open_traps(learner) if deps.subject_of(t["topic"]) == subject])
    level = open_now
    out = []
    for w in sorted(rows, reverse=True):
        out.append({"week": w.isoformat(), "opened": rows[w]["opened"], "relapsed": rows[w]["relapsed"],
                    "fixed": rows[w]["fixed"], "open_end": max(0, level)})
        level -= rows[w]["net"]
    out.reverse()
    last4 = out[-4:]
    fixed_week = round(sum(w["fixed"] for w in last4) / len(last4), 1)
    made_week = round(sum(w["opened"] + w["relapsed"] for w in last4) / len(last4), 1)
    since = (utcnow() - dt.timedelta(days=28)).isoformat()
    fixes = db.one("SELECT COUNT(*) AS n FROM trap_log WHERE learner=? AND event='fixed' AND at>=?", learner, since)["n"]
    spent = db.one("SELECT COALESCE(SUM(MIN(COALESCE(a.ms, a.sms, 0), ?)),0) AS ms FROM attempts a"
                   " JOIN sessions s ON s.id=a.session WHERE a.learner=? AND a.at>=? AND json_valid(s.cfg)"
                   " AND (json_extract(s.cfg,'$.source') IN ('due','warmup','mistakes','review')"
                   " OR json_extract(s.cfg,'$.pool') IN ('redo','checks'))", progress.MS_CAP, learner, since)["ms"]
    per_fix = round(spent / 60_000 / fixes, 1) if fixes >= 10 and spent else None
    forecast = {"zero_on": None, "after_exam": False, "extra_minutes": None}
    net = fixed_week - made_week
    exam = db.one("SELECT exam_date FROM learners WHERE id=?", learner)
    exam = exam["exam_date"] if exam else None
    if net > 0 and exam and open_now:
        zero = today + dt.timedelta(days=math.ceil(open_now / (net / 7)))
        exam_day = dt.date.fromisoformat(exam)
        forecast = {"zero_on": zero.isoformat(), "after_exam": zero > exam_day, "extra_minutes": None,
                    "exam_date": exam, "days_before": (exam_day - zero).days}
        if zero > exam_day and per_fix and exam_day > today:
            need = open_now / (exam_day - today).days - net / 7
            forecast["extra_minutes"] = max(1, math.ceil(need * per_fix))
    return {"subject": subject, "weeks": out, "open": open_now,
            "rate": {"fixed_week": fixed_week, "made_week": made_week, "minutes_per_fix": per_fix},
            "forecast": forecast}


# ------------------------------------------------------------------ instincts (V5)

def calibration(learner: str, tz: int = 0, since: str | None = None, until: str | None = None,
                subject: str = "math") -> dict:
    """V5's card: certainty against results (inferred Sure counted as assumed),
    readings per topic, answer changes in tests, and what flags caught. Repeats,
    disputed and voided rows are left out (R8)."""
    where, args = in_subject("a.topic", subject)
    extra, extra_args = "", []
    if since:
        extra += " AND a.at>=?"
        extra_args.append(utc_of(dt.date.fromisoformat(since), tz))
    if until:
        extra += " AND a.at<?"
        extra_args.append(utc_of(dt.date.fromisoformat(until) + dt.timedelta(days=1), tz))
    rows = db.rows(f"SELECT a.*, s.kind AS skind FROM attempts a LEFT JOIN sessions s ON s.id=a.session"
                   f" WHERE a.learner=? AND a.repeat=0 AND a.disputed=0 AND a.void IS NULL"
                   f" AND {where}{extra}", learner, *args, *extra_args)
    medians = progress._tier_medians(learner)
    budget = budget_fn()
    matrix = {"sure": {"right": 0, "wrong": 0, "assumed": 0}, "unsure": {"right": 0, "wrong": 0},
              "guess": {"right": 0, "wrong": 0}, "untagged": 0}
    topics: dict[str, dict] = defaultdict(lambda: {"sure": {"n": 0, "right": 0}, "unsure": {"n": 0, "right": 0}})
    for r in rows:
        spent = r["ms"] if r["ms"] is not None else r["sms"]
        bucket = "guess" if r["guess"] or r["conf"] == "guess" else r["conf"]
        assumed = False
        if bucket is None and r["difficulty"] in ("medium", "hard") and spent is not None \
                and medians.get(r["difficulty"]) and spent < 0.6 * medians[r["difficulty"]] \
                and spent >= 0.25 * budget(r["template"], r["difficulty"]):
            bucket, assumed = "sure", True
        if bucket is None:
            matrix["untagged"] += 1
            continue
        matrix[bucket]["right" if r["correct"] else "wrong"] += 1
        if assumed:
            matrix["sure"]["assumed"] += 1
        if bucket in ("sure", "unsure"):
            topics[r["topic"]][bucket]["n"] += 1
            topics[r["topic"]][bucket]["right"] += r["correct"]
    names = math_topics(subject)
    pts = pts_fn(learner, subject)
    stake = Counter()
    for t in progress.open_traps(learner):
        stake[t["topic"]] += pts(t["template"], t["norm"], t["topic"]) or 0
    readings = []
    for topic, v in topics.items():
        name = names[topic].name if topic in names else topic
        s, u = v["sure"], v["unsure"]
        if s["n"] >= 10 and s["right"] / s["n"] < 0.8:
            readings.append((stake[topic], f"{name}: {s['n'] - s['right']} sure but wrong. Check your work here before moving on."))
        if u["n"] >= 10 and u["right"] / u["n"] >= 0.7:
            readings.append((stake[topic], f"{name}: right {round(100 * u['right'] / u['n'])}% when you doubt yourself. Trust your first answer."))
    readings.sort(key=lambda r: -r[0])
    changes = {"n": 0, "wr": 0, "rw": 0, "ww": 0}
    flags = {"n": 0, "revisited": 0, "never": 0, "never_wrong": 0, "caught": 0, "misses": 0}
    by_topic: dict[str, dict] = defaultdict(lambda: {"caught": 0, "misses": 0})
    sql = (f"SELECT * FROM sessions WHERE learner=? AND finished IS NOT NULL AND abandoned IS NULL"
           f" AND kind IN ({','.join('?' for _ in deps.TEST_KINDS)})")
    params: list = [learner, *deps.TEST_KINDS]
    if since:
        sql += " AND finished>=?"
        params.append(utc_of(dt.date.fromisoformat(since), tz))
    if until:
        sql += " AND finished<?"
        params.append(utc_of(dt.date.fromisoformat(until) + dt.timedelta(days=1), tz))
    for s in db.rows(sql, *params):
        qstate = json.loads(s["qstate"] or "{}") if s["qstate"] else {}
        answers = json.loads(s["answers"] or "{}")
        paper = {q["id"]: q for q in progress._paper(s) if "key" in q}
        flagged = {r["qid"]: r["at"] for r in db.rows("SELECT qid, at FROM flags WHERE learner=? AND session=?",
                                                      learner, s["id"])}
        for qid, q in paper.items():
            if deps.subject_of(q.get("topic")) != subject:
                continue
            st = qstate.get(qid) or {}
            given = answers.get(qid)
            right = given not in (None, "") and practice_correct(q, given)
            first = st.get("first") if isinstance(st, dict) else None
            if first not in (None, "") and given not in (None, "") and str(first) != str(given):
                was = practice_correct(q, first)
                changes["n"] += 1
                if right and not was:
                    changes["wr"] += 1
                elif was and not right:
                    changes["rw"] += 1
                elif not right:
                    changes["ww"] += 1
            if not right:
                flags["misses"] += 1
                by_topic[q["topic"]]["misses"] += 1
            if qid in flagged and flagged[qid] <= s["finished"]:
                flags["n"] += 1
                visits = st.get("visits", 0) if isinstance(st, dict) else 0
                if visits > 1:
                    flags["revisited"] += 1
                else:
                    flags["never"] += 1
                    flags["never_wrong"] += int(not right)
                if not right:
                    flags["caught"] += 1
                    by_topic[q["topic"]]["caught"] += 1
    net = changes["wr"] - changes["rw"]
    per_q = deps.part("estimate", "per_question")
    changes.update({"net": net, "pts": round(net * per_q(learner) / 5) * 5 if per_q else None})
    flags["by_topic"] = sorted(({"topic": t, "name": names[t].name if t in names else t, **v}
                                for t, v in by_topic.items() if v["misses"]),
                               key=lambda x: (x["caught"] / x["misses"], -x["misses"]))
    return {"subject": subject, "matrix": matrix,
            "topics": [{"topic": t, "name": names[t].name if t in names else t, **v} for t, v in topics.items()],
            "readings": [text for _, text in readings], "changes": changes, "flags": flags}


def practice_correct(q: dict, given) -> bool:
    from . import scoring
    try:
        return bool(scoring.is_correct(q, int(given) if q.get("type") == "mcq" and str(given).lstrip("-").isdigit() else given))
    except (TypeError, ValueError):
        return False


# ------------------------------------------------------------------ the progress link (V17)

def progress_part(learner: str, tz: int = 0, subject: str = "math") -> dict:
    """The read-only Mistakes block of /share/?t= (S1): counts, the cause bar,
    the top 10 open by points with labels and causes, fixed this month, and the
    ledger. Rules and notes stay private."""
    c = counts(learner, tz, subject)
    names = math_topics(subject)
    pts = pts_fn(learner, subject)
    medians = progress._tier_medians(learner)
    cache: dict = {}
    misses = latest_misses(learner, subject)
    top = []
    opens = [t for t in progress.open_traps(learner) if t["topic"] in names]
    for t in sorted(opens, key=lambda t: (-(pts(t["template"], t["norm"], t["topic"]) or 0), -t["hits"]))[:10]:
        m = misses.get((t["template"], t["norm"]))
        cause = progress._cause(learner, m, progress._sitting(m["session"], cache), medians)[0] \
            if m and not m["correct"] else None
        kind = trap_kind(t, m)
        top.append({"label": trap_label(t), "kind": kind, "cause": cause, "hits": t["hits"],
                    "owed": t["owed"], "of": of(t), "topic": t["topic"], "name": names[t["topic"]].name,
                    "pts": pts(t["template"], t["norm"], t["topic"])})
    month = (utcnow() - dt.timedelta(days=30)).isoformat()
    keep = ("open", "half", "relapsed", "unsure", "fixed", "fixed_week", "held", "unchecked", "median_days",
            "due_left", "answers", "stake_total", "open_week_delta")
    return {"subject": subject, "counts": {k: c[k] for k in keep},
            "causes": progress.causes(learner, tz, 30, subject=subject)["by"],
            "top": top,
            "fixed_month": db.one("SELECT COUNT(*) AS n FROM trap_log WHERE learner=? AND event='fixed' AND at>=?",
                                  learner, month)["n"],
            "ledger": ledger(learner, tz, 12, subject)}


def prune(days: int = 14) -> None:
    """V1: frozen days older than two weeks are not needed again."""
    cutoff = (utcnow().date() - dt.timedelta(days=days)).isoformat()
    db.run("DELETE FROM due_days WHERE day<?", cutoff)
