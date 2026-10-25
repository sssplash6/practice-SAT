"""The progress report a student hands to a parent or a tutor: one A4 page, in Uzbek, English or Russian.

Built from the same numbers the Results and Me pages show (api_results.stats, api_me.scores), so the PDF never
says anything the pages do not. It is drawn, not typeset: a header band, the total and both section scales, four
stat tiles and small charts (accuracy by difficulty, questions per day, each section's score by test). DejaVu Sans carries the
Cyrillic and the Uzbek Latin letters (oʻ, gʻ).
"""
from __future__ import annotations

import datetime as dt
import io
import math
import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Flowable, SimpleDocTemplate, Spacer

from . import db

LANGS = ("uz", "en", "ru")
_FONTS = os.path.join(os.path.dirname(__file__), "data", "fonts")
# the brand's orange and graphite (brand/BRAND.md), with a warm paper tile and three oranges for easy, medium and hard
INK, SOFT, LINE, TILE = colors.HexColor("#1E1E1E"), colors.HexColor("#6B6B6B"), colors.HexColor("#E4E0D8"), colors.HexColor("#F6F3EE")
AMBER, AMBER_L, AMBER_D, GRAPHITE = colors.HexColor("#F18508"), colors.HexColor("#F7C27A"), colors.HexColor("#C25E00"), colors.HexColor("#3F3F3F")
FAINT = colors.HexColor("#CFCBC4")
BOLD = "DejaVu-Bold"

T = {
    "en": {
        "title": "Progress report", "sub": "SAT · prepared {date}", "student": "Student",
        "est": "Estimated SAT score", "none": "Not measured yet: a timed test gives the first estimate",
        "total": "Total", "rw": "Reading and Writing", "math": "Math", "yours": "own estimate",
        "half": "The total needs both sections measured",
        "target": "Target", "exam": "SAT date", "left": "{n} days left", "past": "date passed",
        "qs": "Questions", "acc": "Accuracy", "mins": "Study time", "min": "min", "week": "This week",
        "streak": "Streak", "days": "days", "best": "best", "tests": "Tests taken", "last14": "last 14 days",
        "levels": "Accuracy by difficulty", "easy": "Easy", "medium": "Medium", "hard": "Hard",
        "chart": "Questions per day, last 14 days", "trend": "{s}: score by test",
        "foot": "Made with SAT Freshman · {date}",
    },
    "uz": {
        "title": "Taraqqiyot hisoboti", "sub": "SAT · {date} sanasida tayyorlangan", "student": "Oʻquvchi",
        "est": "Taxminiy SAT bali", "none": "Hali oʻlchanmagan: birinchi baho vaqtli testdan keyin chiqadi",
        "total": "Umumiy ball", "rw": "Oʻqish va yozish", "math": "Matematika", "yours": "oʻz bahosi",
        "half": "Umumiy ball uchun ikkala boʻlim oʻlchanishi kerak",
        "target": "Maqsad", "exam": "SAT sanasi", "left": "{n} kun qoldi", "past": "sana oʻtib ketgan",
        "qs": "Savollar", "acc": "Aniqlik", "mins": "Oʻqish vaqti", "min": "daqiqa", "week": "Shu hafta",
        "streak": "Ketma-ket kunlar", "days": "kun", "best": "eng yaxshisi", "tests": "Topshirilgan testlar", "last14": "oxirgi 14 kun",
        "levels": "Qiyinlik boʻyicha aniqlik", "easy": "Oson", "medium": "Oʻrta", "hard": "Qiyin",
        "chart": "Kunlik savollar, oxirgi 14 kun", "trend": "{s}: testlar boʻyicha ball",
        "foot": "SAT Freshman bilan tayyorlangan · {date}",
    },
    "ru": {
        "title": "Отчёт о прогрессе", "sub": "SAT · подготовлено {date}", "student": "Ученик",
        "est": "Оценка балла SAT", "none": "Пока не измерено: первая оценка появится после теста на время",
        "total": "Общий балл", "rw": "Чтение и письмо", "math": "Математика", "yours": "своя оценка",
        "half": "Для общего балла нужны оба раздела",
        "target": "Цель", "exam": "Дата SAT", "left": "осталось дней: {n}", "past": "дата прошла",
        "qs": "Вопросов", "acc": "Точность", "mins": "Время занятий", "min": "мин", "week": "На этой неделе",
        "streak": "Серия дней", "days": "дн.", "best": "лучшая", "tests": "Пройдено тестов", "last14": "за 14 дней",
        "levels": "Точность по сложности", "easy": "Лёгкие", "medium": "Средние", "hard": "Сложные",
        "chart": "Вопросов в день, последние 14 дней", "trend": "{s}: баллы по тестам",
        "foot": "Сделано в SAT Freshman · {date}",
    },
}


def _fonts() -> None:
    if "DejaVu" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("DejaVu", os.path.join(_FONTS, "DejaVuSans.ttf")))
        pdfmetrics.registerFont(TTFont(BOLD, os.path.join(_FONTS, "DejaVuSans-Bold.ttf")))
        pdfmetrics.registerFontFamily("DejaVu", normal="DejaVu", bold=BOLD)


def _pct(right: int, asked: int) -> str:
    return f"{round(100 * right / asked)}%" if asked else "-"


def _text(c, x, y, text, font="DejaVu", size=9.0, color=INK, maxw=None, align="l") -> None:
    """One line, shrunk (down to 6.5pt) to fit maxw."""
    text = str(text)
    while maxw and size > 6.5 and pdfmetrics.stringWidth(text, font, size) > maxw:
        size -= 0.25
    c.setFont(font, size)
    c.setFillColor(color)
    {"l": c.drawString, "r": c.drawRightString, "c": c.drawCentredString}[align](x, y, text)


def _bg(c, w, h, title=None) -> None:
    c.setFillColor(TILE)
    c.roundRect(0, 0, w, h, 3 * mm, stroke=0, fill=1)
    if title:
        _text(c, 5 * mm, h - 8 * mm, title, BOLD, 9.5, maxw=w - 10 * mm)


class Art(Flowable):
    """A fixed-size drawing: fn(canvas, w, h) paints it with the origin at its bottom left."""

    def __init__(self, w, h, fn):
        super().__init__()
        self.w, self.h, self.fn = w, h, fn

    def wrap(self, *_):
        return self.w, self.h

    def draw(self):
        self.fn(self.canv, self.w, self.h)


def _mark(c, x, y, size, color) -> None:
    """The brand mark (web/assets/mark.svg): four rounded corner brackets, drawn as paths."""
    c.saveState()
    c.translate(x, y + size)
    c.scale(size / 100, -size / 100)
    c.setFillColor(color)
    for i in range(4):
        c.saveState()
        c.translate(50, 50)
        c.rotate(90 * i)
        c.translate(-50, -50)
        p = c.beginPath()
        p.moveTo(45, 8)
        p.lineTo(30, 8)
        p.curveTo(17.85, 8, 8, 17.85, 8, 30)
        p.lineTo(8, 45)
        p.lineTo(34, 45)
        p.lineTo(34, 41)
        p.curveTo(34, 37.13, 37.13, 34, 41, 34)
        p.lineTo(45, 34)
        p.close()
        c.drawPath(p, stroke=0, fill=1)
        c.restoreState()
    c.restoreState()


def _hero(c, w, h, t, sc, info) -> None:
    """The total big on the left; on the right three scales in College Board's order, the total on 400-1600 and each
    section on 200-800: the server's 20-point range in orange, the target as a graphite tick."""
    _bg(c, w, h)
    pad, half = 6 * mm, w * 0.5
    rng = lambda x: f'{x["low"]}–{x["high"]}' if x.get("low") is not None else "-"  # noqa: E731
    _text(c, pad, h - 8 * mm, t["est"], size=8.5, color=SOFT, maxw=half - pad)
    _text(c, pad, h - 20 * mm, rng(sc["total"]), BOLD, 28, maxw=half - pad)
    y = h - 27 * mm
    for line in [ln for s in info for ln in simpleSplit(s, "DejaVu", 8.5, half - pad)][:3]:
        _text(c, pad, y, line, size=8.5, color=SOFT)
        y -= 4.3 * mm
    x0, x1, th = w * 0.56, w - pad, 3 * mm
    for i, (key, lo, hi) in enumerate((("total", 400, 1600), ("rw", 200, 800), ("math", 200, 800))):
        x, yb = sc[key], h - 17 * mm - i * 11.5 * mm
        at = lambda v, lo=lo, hi=hi: x0 + (min(hi, max(lo, v)) - lo) / (hi - lo) * (x1 - x0)  # noqa: E731
        said = rng(x) + (f' ({t["yours"]})' if x.get("source") == "yours" else "")
        if x.get("target"):
            said += f' · {t["target"]} {x["target"]}'
        _text(c, x0, yb + th + 2 * mm, t[key], BOLD if key == "total" else "DejaVu", 8, maxw=(x1 - x0) * 0.4)
        _text(c, x1, yb + th + 2 * mm, said, size=7.5, color=SOFT, maxw=(x1 - x0) * 0.6, align="r")
        c.setFillColor(LINE)
        c.roundRect(x0, yb, x1 - x0, th, th / 2, stroke=0, fill=1)
        if x.get("low") is not None:
            bx0, bx1 = at(x["low"]), at(x["high"])
            c.setFillColor(AMBER)
            c.roundRect(bx0, yb, max(bx1 - bx0, 2.5 * mm), th, th / 2, stroke=0, fill=1)
        if x.get("target"):
            tx = at(x["target"])
            c.setStrokeColor(GRAPHITE)
            c.setLineWidth(1.5)
            c.line(tx, yb - 1.4 * mm, tx, yb + th + 1.4 * mm)


def _tiles(c, w, h, tiles) -> None:
    gap = 4 * mm
    tw = (w - gap * (len(tiles) - 1)) / len(tiles)
    for i, (label, value, unit, sub) in enumerate(tiles):
        c.saveState()
        c.translate(i * (tw + gap), 0)
        _bg(c, tw, h)
        c.setFillColor(AMBER)
        c.roundRect(4 * mm, h - 3.4 * mm, 8 * mm, 1.2 * mm, 0.6 * mm, stroke=0, fill=1)
        _text(c, 4 * mm, h - 8.5 * mm, label, size=8, color=SOFT, maxw=tw - 8 * mm)
        _text(c, 4 * mm, h - 17 * mm, value, BOLD, 20, maxw=tw - 8 * mm)
        if unit:
            vw = pdfmetrics.stringWidth(value, BOLD, 20)
            _text(c, 4 * mm + vw + 1.5 * mm, h - 17 * mm, unit, size=8.5, color=SOFT, maxw=max(tw - 8 * mm - vw - 1.5 * mm, 8 * mm))
        _text(c, 4 * mm, 4 * mm, sub, size=7.5, color=SOFT, maxw=tw - 8 * mm)
        c.restoreState()


def _levels(c, w, h, t, rows) -> None:
    _bg(c, w, h, t["levels"])
    pad = 5 * mm
    for i, (key, fill) in enumerate((("easy", AMBER_L), ("medium", AMBER), ("hard", AMBER_D))):
        r = rows.get(key) or {"right": 0, "answered": 0}
        yb = h - 21 * mm - i * 13 * mm
        _text(c, pad, yb, t[key], size=8.5, maxw=w * 0.4)
        _text(c, w - pad, yb, _pct(r["right"], r["answered"]), BOLD, 9.5, align="r")
        if r["answered"]:
            _text(c, w - pad - 12 * mm, yb, f'{r["right"]}/{r["answered"]}', size=7.5, color=SOFT, align="r")
        c.setFillColor(LINE)
        c.roundRect(pad, yb - 5 * mm, w - 2 * pad, 3.2 * mm, 1.6 * mm, stroke=0, fill=1)
        if r["answered"] and r["right"]:
            c.setFillColor(fill)
            c.roundRect(pad, yb - 5 * mm, max((w - 2 * pad) * r["right"] / r["answered"], 3.2 * mm), 3.2 * mm, 1.6 * mm, stroke=0, fill=1)


def _daily(c, w, h, t, days) -> None:
    _bg(c, w, h, t["chart"])
    x0, x1, y0, y1 = 11 * mm, w - 5 * mm, 11 * mm, h - 16 * mm
    top = max([d["questions"] for d in days] + [1])
    slot = (x1 - x0) / max(len(days), 1)
    c.setStrokeColor(LINE)
    c.setLineWidth(0.6)
    c.line(x0, y0, x1, y0)
    _text(c, x0 - 1.5 * mm, y0 - 0.8 * mm, "0", size=7, color=SOFT, align="r")
    _text(c, x0 - 1.5 * mm, y1 - 1.5 * mm, str(top), size=7, color=SOFT, align="r")
    for i, d in enumerate(days):
        bh = (y1 - y0) * d["questions"] / top
        c.setFillColor(AMBER_D if i == len(days) - 1 else AMBER if d["questions"] else LINE)
        c.roundRect(x0 + i * slot + slot * 0.19, y0, slot * 0.62, max(bh, 0.7 * mm), 0.6 * mm, stroke=0, fill=1)
        if d["questions"] == top:
            _text(c, x0 + i * slot + slot / 2, y0 + bh + 1.4 * mm, str(top), BOLD, 7, color=GRAPHITE, align="c")
        if i in (0, len(days) // 2, len(days) - 1):
            _text(c, x0 + i * slot + slot / 2, y0 - 4.6 * mm, d["day"][8:], size=7, color=SOFT, align="c")


def _trend(c, w, h, t, pts, target, title) -> None:
    _bg(c, w, h, title)
    x0, x1, y0, y1 = 16 * mm, w - 8 * mm, 11 * mm, h - 15 * mm
    lows, highs = [p[1] for p in pts], [p[2] for p in pts]
    lo, hi = min(lows + ([target] if target else [])), max(highs + ([target] if target else []))
    ymin, ymax = max(200, math.floor((lo - 30) / 50) * 50), min(800, math.ceil((hi + 30) / 50) * 50)
    if ymax - ymin < 100:
        ymax = ymin + 100
    yv = lambda v: y0 + (v - ymin) / (ymax - ymin) * (y1 - y0)  # noqa: E731
    c.setLineWidth(0.5)
    for v in (ymin, (ymin + ymax) / 2, ymax):
        c.setStrokeColor(LINE)
        c.line(x0, yv(v), x1, yv(v))
        _text(c, x0 - 2 * mm, yv(v) - 1.2 * mm, f"{round(v)}", size=7, color=SOFT, align="r")
    if target:
        c.setStrokeColor(GRAPHITE)
        c.setDash(2, 2)
        c.line(x0, yv(target), x1, yv(target))
        c.setDash()
        _text(c, x1, yv(target) + 1.4 * mm, f'{t["target"]} {target}', BOLD, 7, color=GRAPHITE, align="r")
    xs = [x0 + 8 * mm + i * (x1 - x0 - 16 * mm) / (len(pts) - 1) for i in range(len(pts))]
    c.setLineCap(1)
    for x, (_, plo, phi, _m) in zip(xs, pts):
        c.setStrokeColor(AMBER_L)
        c.setLineWidth(5)
        c.line(x, yv(plo), x, yv(phi))
    c.setStrokeColor(GRAPHITE)
    c.setLineWidth(1)
    c.setLineCap(0)
    for (xa, a), (xb, b) in zip(zip(xs, pts), zip(xs[1:], pts[1:])):
        c.line(xa, yv(a[3]), xb, yv(b[3]))
    for x, (day, plo, phi, mid) in zip(xs, pts):
        c.setFillColor(colors.white)
        c.setStrokeColor(GRAPHITE)
        c.setLineWidth(1.2)
        c.circle(x, yv(mid), 1.3 * mm, stroke=1, fill=1)
        _text(c, x, yv(phi) + 2.2 * mm, f"{round(mid / 10) * 10}", BOLD, 7.5, color=INK, align="c")
        _text(c, x, y0 - 5 * mm, day[5:], size=7, color=SOFT, align="c")


def build(learner: str, tz: int, lang: str) -> bytes:
    from . import api_results  # here, not at import: api_results is the caller

    lang = lang if lang in LANGS else "en"
    t = T[lang]
    _fonts()
    s = api_results.stats(learner, tz)
    today = dt.date.today()
    date = today.isoformat()
    row = db.one("SELECT name FROM learners WHERE id=?", learner)
    name = (row["name"] if row and row["name"] else "").strip()
    profile = s.get("profile") or {}
    from . import api_me
    sc = api_me.scores(learner)     # Total, R&W, Math: the same 20-point ranges and targets every page shows
    target = sc["total"]["target"]

    # the score card's small print: what is missing, the total target and exam date, then the tests taken
    known = [k for k in ("rw", "math") if sc[k]["low"] is not None]
    info = [] if len(known) == 2 else [t["half"]] if known else [t["none"]]
    bits = [f'{t["target"]} {target}'] if target else []
    if profile.get("exam_date"):
        try:
            left = (dt.date.fromisoformat(profile["exam_date"]) - today).days
            bits.append(f'{t["exam"]} {profile["exam_date"]} · ' + (t["left"].format(n=left) if left >= 0 else t["past"]))
        except ValueError:
            pass
    if bits:
        info.append(" · ".join(bits))
    tests = sum((s.get("tests") or {}).values())
    if tests:
        info.append(f'{t["tests"]}: {tests}')

    wk, week = s.get("week") or {}, t["week"].lower()
    recent = s.get("recent_accuracy")
    tiles = [
        (t["qs"], str(s.get("answered", 0)), "", f'{wk.get("questions", 0)} {week}'),
        (t["acc"], _pct(s.get("right", 0), s.get("answered", 0)), "", f'{t["last14"]} {round(100 * recent)}%' if recent is not None else f'{s.get("right", 0)}/{s.get("answered", 0)}'),
        (t["mins"], str(s.get("minutes_total", 0)), t["min"], f'{wk.get("minutes", 0)} {t["min"]} {week}'),
        (t["streak"], str(s.get("streak", 0)), t["days"], f'{t["best"]} {s.get("best_streak", 0)}'),
    ]
    levels = {r["key"]: r for r in s.get("by_difficulty") or []}
    days = (s.get("days14") or [])[-14:]
    # the scored tests per subject, oldest first: (day, low, high, middle); a section is never charted against the other's
    # (each subject's own list: a full SAT's two sections each land on their own chart, never as its total)
    pts = {k: [(x["finished"][:10], x["estimate"]["low"], x["estimate"]["high"], (x["estimate"]["low"] + x["estimate"]["high"]) / 2)
               for x in reversed(api_results.history(learner, kind="tests", limit=16, subject=k)["sessions"])
               if x.get("kind") != "full" and (x.get("estimate") or {}).get("low") is not None
               and x["estimate"].get("high") is not None][-8:]
           for k in ("rw", "math")}
    charts = [k for k in ("rw", "math") if len(pts[k]) >= 2]

    W, gap = A4[0] - 32 * mm, 4 * mm
    half = (W - gap) / 2

    def pair(c, w, h):
        for x, fn, a in ((0, _levels, (t, levels)), (half + gap, _daily, (t, days))):
            c.saveState()
            c.translate(x, 0)
            fn(c, half, h, *a)
            c.restoreState()

    def trends(c, w, h):
        # one subject: the full width; both: R&W then Math side by side, each with six tests at most
        each = w if len(charts) == 1 else half
        for i, k in enumerate(charts):
            c.saveState()
            c.translate(i * (half + gap), 0)
            _trend(c, each, h, t, pts[k] if len(charts) == 1 else pts[k][-6:], sc[k]["target"], t["trend"].format(s=t[k]))
            c.restoreState()

    story: list = [Art(W, 46 * mm, lambda c, w, h: _hero(c, w, h, t, sc, info)), Spacer(1, 4 * mm),
                   Art(W, 26 * mm, lambda c, w, h: _tiles(c, w, h, tiles)), Spacer(1, 4 * mm),
                   Art(W, 56 * mm, pair)]
    if charts:
        story += [Spacer(1, 4 * mm), Art(W, 56 * mm, trends)]

    def page(canvas, doc):
        pw, ph = A4
        canvas.saveState()
        if doc.page == 1:
            canvas.setFillColor(GRAPHITE)
            canvas.rect(0, ph - 34 * mm, pw, 34 * mm, stroke=0, fill=1)
            _mark(canvas, 16 * mm, ph - 24 * mm, 14 * mm, AMBER)
            _text(canvas, 35 * mm, ph - 17 * mm, t["title"], BOLD, 20, colors.white, maxw=pw - 35 * mm - 74 * mm)
            _text(canvas, 35 * mm, ph - 24 * mm, t["sub"].format(date=date), size=9, color=FAINT, maxw=pw - 35 * mm - 74 * mm)
            if name:
                _text(canvas, pw - 16 * mm, ph - 14 * mm, t["student"], size=8, color=FAINT, align="r")
                _text(canvas, pw - 16 * mm, ph - 21 * mm, name, BOLD, 13, colors.white, maxw=62 * mm, align="r")
        canvas.setStrokeColor(LINE)
        canvas.setLineWidth(0.5)
        canvas.line(16 * mm, 16 * mm, pw - 16 * mm, 16 * mm)
        _mark(canvas, 16 * mm, 9.2 * mm, 4 * mm, AMBER)
        _text(canvas, 22 * mm, 10.3 * mm, t["foot"].format(date=date), size=8, color=SOFT)
        canvas.restoreState()

    buf = io.BytesIO()
    SimpleDocTemplate(buf, pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm, topMargin=42 * mm, bottomMargin=22 * mm,
                      title=t["title"], author="SAT Freshman").build(story, onFirstPage=page, onLaterPages=page)
    return buf.getvalue()
