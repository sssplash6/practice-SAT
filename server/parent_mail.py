"""Emails to parents: a weekly summary (Sundays) and short alerts (a child went quiet, finished a test, exam coming up).

Run once a day by the fa-satbank-mail timer:  python -m server.parent_mail [--dry]
Each email is sent once: what was already sent is remembered in parent_mail (key per week or per event).
Without SMTP configured nothing is sent and nothing is remembered, so turning SMTP on later sends what is due.
Plain text, in the language the parent picked on their page (English, Uzbek or Russian).
"""

from __future__ import annotations

import datetime as dt
import logging
import sys

from . import api_parent, db, deps, mail

log = logging.getLogger("satf.parent_mail")

TZ = dt.timedelta(hours=5)      # ponytail: Uzbekistan time for "Sunday" and "today"; a setting if parents elsewhere matter
IDLE_DAYS = 5                   # no practice for this long is worth a message (once per quiet stretch)
EXAM_DAYS = 14                  # a heads-up once, when the SAT is this close
NEWS_DAYS = 2                   # a test older than this is not news

T = {
    "en": dict(hello="Hello,", subj_week="Weekly summary: {names}", subj_news="SAT Freshman: news about {names}", child="your child",
               q="Questions this week: {n}{delta}", up=" ({n} more than last week)", down=" ({n} fewer than last week)", d="Days practised: {n} of 7",
               acc="Accuracy this week: {a}", last="Last active: {w}", today="today", yesterday="yesterday", ago="{n} days ago", never="never",
               strong="Doing well: {s}", weak="Needs attention: {s}", quiet="No practice this week.", tests="Tests finished this week: {n}",
               idle="{name} has not practised for {n} days.", test="{name} finished a test: {score}.", score="score range {low} to {high}", score2="{right} of {asked} right",
               exam="{name}'s SAT is coming up. Days to go: {n}.", open="See the full view: {url}", off="To stop these emails, switch them off at the bottom of that page.", bye="SAT Freshman"),
    "uz": dict(hello="Assalomu alaykum,", subj_week="Haftalik xulosa: {names}", subj_news="SAT Freshman: {names} haqida yangilik", child="farzandingiz",
               q="Bu haftadagi savollar: {n}{delta}", up=" (o‘tgan haftadan {n} ta ko‘p)", down=" (o‘tgan haftadan {n} ta kam)", d="Mashq qilingan kunlar: 7 tadan {n} ta",
               acc="Bu haftadagi aniqlik: {a}", last="Oxirgi faollik: {w}", today="bugun", yesterday="kecha", ago="{n} kun oldin", never="hech qachon",
               strong="Yaxshi natijalar: {s}", weak="E’tibor kerak: {s}", quiet="Bu hafta mashq qilinmadi.", tests="Bu hafta topshirilgan testlar: {n}",
               idle="{name} {n} kundan beri mashq qilmayapti.", test="{name} testni tugatdi: {score}.", score="ball oralig‘i {low} dan {high} gacha", score2="{asked} tadan {right} tasi to‘g‘ri",
               exam="{name}ning SAT imtihoni yaqinlashmoqda. Qolgan kunlar: {n}.", open="To‘liq ma’lumotni ko‘ring: {url}", off="Bu xatlarni to‘xtatish uchun shu sahifaning pastidagi tugmani o‘chiring.", bye="SAT Freshman"),
    "ru": dict(hello="Здравствуйте,", subj_week="Итоги недели: {names}", subj_news="SAT Freshman: новости о {names}", child="ваш ребёнок",
               q="Вопросов за неделю: {n}{delta}", up=" (на {n} больше, чем на прошлой неделе)", down=" (на {n} меньше, чем на прошлой неделе)", d="Дней занятий: {n} из 7",
               acc="Точность за неделю: {a}", last="Последняя активность: {w}", today="сегодня", yesterday="вчера", ago="{n} дн. назад", never="никогда",
               strong="Получается хорошо: {s}", weak="Нужно подтянуть: {s}", quiet="На этой неделе занятий не было.", tests="Тестов пройдено за неделю: {n}",
               idle="Занятий у {name} не было уже {n} дн.", test="{name} прошёл(-ла) тест: {score}.", score="диапазон баллов от {low} до {high}", score2="верно {right} из {asked}",
               exam="Приближается SAT у {name}. Осталось дней: {n}.", open="Подробности: {url}", off="Чтобы отключить эти письма, выключите их внизу той страницы.", bye="SAT Freshman"),
}


def _t(lang: str, key: str, **v) -> str:
    return (T.get(lang) or T["en"])[key].format(**v)


def _when(lang: str, last: str | None, now: dt.datetime) -> str:
    if not last:
        return _t(lang, "never")
    n = (now - dt.datetime.fromisoformat(last)).days
    return _t(lang, "today") if n <= 0 else _t(lang, "yesterday") if n == 1 else _t(lang, "ago", n=n)


def weekly_lines(lang: str, name: str, s: dict, now: dt.datetime) -> list[str]:
    w = s["week"]
    out = [name, "-" * len(name)]
    if not w["answers"]:
        out.append(_t(lang, "quiet"))
    else:
        diff = w["answers"] - w["prev_answers"]
        delta = _t(lang, "up", n=diff) if diff > 0 else _t(lang, "down", n=-diff) if diff < 0 else ""
        out += [_t(lang, "q", n=w["answers"], delta=delta), _t(lang, "d", n=w["active_days"]), _t(lang, "acc", a=f"{round(w['right'] / w['answers'] * 100)}%")]
    week_ago = (now - dt.timedelta(days=7)).isoformat()
    done = sum(1 for t in s["tests"] if (t["finished"] or "") >= week_ago)
    if done:
        out.append(_t(lang, "tests", n=done))
    if s["strong"]:
        out.append(_t(lang, "strong", s=", ".join(x["name"] for x in s["strong"])))
    if s["focus"]:
        out.append(_t(lang, "weak", s=", ".join(x["name"] for x in s["focus"])))
    out.append(_t(lang, "last", w=_when(lang, s["last"], now)))
    return out


def alerts(lang: str, name: str, s: dict, now: dt.datetime, local: dt.datetime) -> list[tuple[str, str]]:
    """(key, line) for what is news about one child right now."""
    out = []
    sid = s["student"]
    if s["last"] and s["totals"]["answers"]:
        quiet = (now - dt.datetime.fromisoformat(s["last"])).days
        if quiet >= IDLE_DAYS:
            out.append((f"idle:{sid}:{s['last'][:10]}", _t(lang, "idle", name=name, n=quiet)))
    recent = (now - dt.timedelta(days=NEWS_DAYS)).isoformat()
    for t in s["tests"]:
        if (t["finished"] or "") >= recent:
            score = (_t(lang, "score", low=t["low"], high=t["high"]) if t["low"] else _t(lang, "score2", right=t["right"], asked=t["asked"]) if t["asked"] else None)
            if score:
                out.append((f"test:{sid}:{t['finished']}", _t(lang, "test", name=name, score=score)))
    ex = s["goal"]["exam_date"]
    if ex:
        n = (dt.date.fromisoformat(ex) - local.date()).days
        if 0 <= n <= EXAM_DAYS:
            out.append((f"exam:{sid}:{ex}", _t(lang, "exam", name=name, n=n)))
    return out


def run(dry: bool = False, now: dt.datetime | None = None) -> dict:
    now = now or dt.datetime.now(dt.timezone.utc)
    local = now + TZ
    iso = local.isocalendar()
    week_key = f"week:{iso[0]}-{iso[1]}"
    sunday = local.weekday() == 6
    sendable = dry or mail.mode() != "outbox"
    if not sendable:
        log.warning("SATF_SMTP_HOST is unset: parent emails are not sent (and not marked as sent) until it is")
    kids: dict[str, list[str]] = {}
    for r in db.rows("SELECT parent, student FROM guardians ORDER BY created"):
        kids.setdefault(r["parent"], []).append(r["student"])
    count = {"parents": len(kids), "weekly": 0, "news": 0}
    for parent, students in kids.items():
        user = db.one("SELECT email FROM users WHERE learner=? AND email IS NOT NULL ORDER BY verified DESC LIMIT 1", parent)
        pref = api_parent.prefs_of(parent)
        if not user or not pref["mail"] or not sendable:
            continue
        lang = pref["lang"] or "en"
        sent = {r["key"] for r in db.rows("SELECT key FROM parent_mail WHERE parent=?", parent)}
        names, news, weekly = [], [], []
        for sid in students:
            s = api_parent.summary(sid)
            s["student"] = sid
            name = s["name"] or _t(lang, "child")
            names.append(name)
            news += [(k, line) for k, line in alerts(lang, name, s, now, local) if k not in sent]
            weekly += weekly_lines(lang, name, s, now) + [""]
        link = f"{mail.BASE_URL}/parent/"
        foot = ["", _t(lang, "open", url=link), _t(lang, "off"), "", _t(lang, "bye")]
        for kind, key, subject, body in (
                ("news", None, _t(lang, "subj_news", names=", ".join(names)), [x[1] for x in news]),
                ("weekly", week_key, _t(lang, "subj_week", names=", ".join(names)), weekly)):
            if not body or (kind == "weekly" and (not sunday or week_key in sent)):
                continue
            text = "\n".join([_t(lang, "hello"), ""] + body + foot)
            if dry:
                print(f"--- to {user['email']} ({kind}): {subject}\n{text}\n")
                continue
            if mail.deliver(mail._plain(user["email"], subject, text)) != "sent":
                continue
            count[kind] += 1
            for k in [key] if key else [x[0] for x in news]:
                db.run("INSERT OR IGNORE INTO parent_mail(parent,key,at) VALUES (?,?,?)", parent, k, deps.now())
    return count


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    db.init()
    print(run(dry="--dry" in sys.argv))
