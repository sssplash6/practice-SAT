"""The progress report a student hands to a parent or a tutor: one A4 PDF, in Uzbek, English or Russian.

Built from the same numbers the Results page shows (api_results.stats), so the PDF never says
anything the page does not. DejaVu Sans carries the Cyrillic and the Uzbek Latin letters (oʻ, gʻ).
"""
from __future__ import annotations

import datetime as dt
import io
import os

from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from . import db, progress

LANGS = ("uz", "en", "ru")
_FONTS = os.path.join(os.path.dirname(__file__), "data", "fonts")
INK, SOFT, LINE, AMBER = colors.HexColor("#1E1E1E"), colors.HexColor("#6B6B6B"), colors.HexColor("#DDDAD4"), colors.HexColor("#F18508")

T = {
    "en": {
        "title": "Progress report", "sub": "SAT Math · prepared {date}", "student": "Student",
        "score": "Score", "est": "Estimated Math score", "none": "Not measured yet: a timed test gives the first estimate",
        "target": "Target", "exam": "SAT date", "left": "{n} days left", "past": "date passed",
        "activity": "Practice so far", "answered": "Questions answered", "acc": "Accuracy", "mins": "Study time",
        "min": "min", "week": "This week", "streak": "Streak", "days": "day(s)", "best": "best", "tests": "Tests taken",
        "levels": "Accuracy by difficulty", "easy": "Easy", "medium": "Medium", "hard": "Hard",
        "right": "Right", "asked": "Asked", "chart": "Questions per day, last 14 days",
        "next": "Where the next points are", "pts": "points", "mist": "Mistakes still open",
        "mistn": "{n} open · {hits}× so far", "nomist": "No open mistakes.", "en_note": "Skill and mistake names are in English.",
        "foot": "Made with SAT Freshman · {date}", "q": "questions",
    },
    "uz": {
        "title": "Taraqqiyot hisoboti", "sub": "SAT Matematika · {date} sanasida tayyorlangan", "student": "Oʻquvchi",
        "score": "Ball", "est": "Matematikadan taxminiy ball", "none": "Hali oʻlchanmagan: birinchi baho vaqtli testdan keyin chiqadi",
        "target": "Maqsad", "exam": "SAT sanasi", "left": "{n} kun qoldi", "past": "sana oʻtib ketgan",
        "activity": "Hozirgacha mashq", "answered": "Javob berilgan savollar", "acc": "Aniqlik", "mins": "Oʻqish vaqti",
        "min": "daqiqa", "week": "Shu hafta", "streak": "Ketma-ket kunlar", "days": "kun", "best": "eng yaxshisi", "tests": "Topshirilgan testlar",
        "levels": "Qiyinlik boʻyicha aniqlik", "easy": "Oson", "medium": "Oʻrta", "hard": "Qiyin",
        "right": "Toʻgʻri", "asked": "Jami", "chart": "Kunlik savollar, oxirgi 14 kun",
        "next": "Keyingi ballar qayerda", "pts": "ball", "mist": "Hali tuzatilmagan xatolar",
        "mistn": "{n} ta ochiq · {hits} marta uchragan", "nomist": "Ochiq xatolar yoʻq.", "en_note": "Mavzu va xato nomlari inglizcha.",
        "foot": "SAT Freshman bilan tayyorlangan · {date}", "q": "savol",
    },
    "ru": {
        "title": "Отчёт о прогрессе", "sub": "SAT Математика · подготовлено {date}", "student": "Ученик",
        "score": "Балл", "est": "Оценка по математике", "none": "Пока не измерено: первая оценка появится после теста на время",
        "target": "Цель", "exam": "Дата SAT", "left": "осталось дней: {n}", "past": "дата прошла",
        "activity": "Практика на данный момент", "answered": "Отвечено на вопросов", "acc": "Точность", "mins": "Время занятий",
        "min": "мин", "week": "На этой неделе", "streak": "Серия дней", "days": "дн.", "best": "лучшая", "tests": "Пройдено тестов",
        "levels": "Точность по сложности", "easy": "Лёгкие", "medium": "Средние", "hard": "Сложные",
        "right": "Верно", "asked": "Всего", "chart": "Вопросов в день, последние 14 дней",
        "next": "Где следующие баллы", "pts": "баллов", "mist": "Ошибки, которые ещё не исправлены",
        "mistn": "открыто: {n} · встречалась {hits} раз", "nomist": "Открытых ошибок нет.", "en_note": "Названия навыков и ошибок на английском.",
        "foot": "Сделано в SAT Freshman · {date}", "q": "вопросов",
    },
}


def _fonts() -> None:
    if "DejaVu" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("DejaVu", os.path.join(_FONTS, "DejaVuSans.ttf")))
        pdfmetrics.registerFont(TTFont("DejaVu-Bold", os.path.join(_FONTS, "DejaVuSans-Bold.ttf")))
        pdfmetrics.registerFontFamily("DejaVu", normal="DejaVu", bold="DejaVu-Bold")


def _style(name: str, size: float, bold: bool = False, color=INK, lead: float | None = None, after: float = 0) -> ParagraphStyle:
    return ParagraphStyle(name, fontName="DejaVu-Bold" if bold else "DejaVu", fontSize=size, leading=lead or size * 1.35,
                          textColor=color, spaceAfter=after)


def _esc(text: object) -> str:
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _pct(right: int, asked: int) -> str:
    return f"{round(100 * right / asked)}%" if asked else "-"


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
    names = progress.topics()

    h1, h2, body, small = _style("h1", 22, True, after=2), _style("h2", 12.5, True, after=6), _style("b", 10.5), _style("s", 8.5, color=SOFT)
    story: list = [Paragraph(_esc(t["title"]), h1), Paragraph(_esc(t["sub"].format(date=date)), _style("sub", 10, color=SOFT, after=4))]
    if name:
        story.append(Paragraph(f'<b>{_esc(t["student"])}:</b> {_esc(name)}', body))
    story.append(Spacer(1, 6 * mm))

    def block(title: str, rows: list[list], widths=None) -> KeepTogether:
        tbl = Table(rows, colWidths=widths or [90 * mm, 80 * mm], hAlign="LEFT")
        tbl.setStyle(TableStyle([("FONTNAME", (0, 0), (-1, -1), "DejaVu"), ("FONTSIZE", (0, 0), (-1, -1), 10.5), ("TEXTCOLOR", (0, 0), (-1, -1), INK),
                                 ("TEXTCOLOR", (0, 0), (0, -1), SOFT), ("FONTNAME", (1, 0), (1, -1), "DejaVu-Bold"),
                                 ("LINEBELOW", (0, 0), (-1, -1), 0.4, LINE), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
        return KeepTogether([Paragraph(_esc(title), h2), tbl, Spacer(1, 6 * mm)])

    # score
    est = s.get("estimate") or {}
    band = est.get("combined") or est.get("range") or {}
    if band.get("low") is not None:
        lo, hi = round(band["low"] / 10) * 10, round(band["high"] / 10) * 10
        score = f"{lo}" if lo == hi else f"{lo}-{hi}"
    else:
        score = t["none"]
    rows = [[t["est"], Paragraph(_esc(score), _style("v", 10.5, True))]]
    if profile.get("target"):
        rows.append([t["target"], str(profile["target"])])
    if profile.get("exam_date"):
        try:
            left = (dt.date.fromisoformat(profile["exam_date"]) - today).days
            rows.append([t["exam"], f'{profile["exam_date"]} · ' + (t["left"].format(n=left) if left >= 0 else t["past"])])
        except ValueError:
            pass
    story.append(block(t["score"], rows))

    # activity
    tests = sum((s.get("tests") or {}).values())
    wk = s.get("week") or {}
    story.append(block(t["activity"], [
        [t["answered"], f'{s.get("answered", 0)} · {t["acc"]} {round(100 * s.get("accuracy", 0))}%'],
        [t["mins"], f'{s.get("minutes_total", 0)} {t["min"]}'],
        [t["week"], f'{wk.get("questions", 0)} {t["q"]} · {wk.get("minutes", 0)} {t["min"]}'],
        [t["streak"], f'{s.get("streak", 0)} {t["days"]} ({t["best"]} {s.get("best_streak", 0)})'],
        [t["tests"], str(tests)]]))

    # by difficulty
    lv = {r["key"]: r for r in s.get("by_difficulty") or []}
    head = [t["levels"], t["right"], t["asked"], "%"]
    trs = [head] + [[t[k], lv[k]["right"], lv[k]["answered"], _pct(lv[k]["right"], lv[k]["answered"])] for k in ("easy", "medium", "hard") if k in lv]
    tbl = Table(trs, colWidths=[70 * mm, 30 * mm, 30 * mm, 30 * mm], hAlign="LEFT")
    tbl.setStyle(TableStyle([("FONTNAME", (0, 0), (-1, -1), "DejaVu"), ("FONTNAME", (0, 0), (-1, 0), "DejaVu-Bold"), ("FONTSIZE", (0, 0), (-1, -1), 10),
                             ("TEXTCOLOR", (0, 0), (-1, 0), SOFT), ("ALIGN", (1, 0), (-1, -1), "RIGHT"), ("LINEBELOW", (0, 0), (-1, -1), 0.4, LINE),
                             ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    story += [tbl, Spacer(1, 6 * mm)]

    # the fortnight
    days = (s.get("days14") or [])[-14:]
    if days:
        d = Drawing(170 * mm, 38 * mm)
        chart = VerticalBarChart()
        chart.x, chart.y, chart.width, chart.height = 8, 14, 165 * mm - 8, 38 * mm - 20
        chart.data = [[x["questions"] for x in days]]
        chart.categoryAxis.categoryNames = [x["day"][8:] for x in days]
        chart.categoryAxis.labels.fontName, chart.categoryAxis.labels.fontSize = "DejaVu", 7
        chart.valueAxis.labels.fontName, chart.valueAxis.labels.fontSize = "DejaVu", 7
        chart.valueAxis.valueMin = 0
        chart.bars[0].fillColor, chart.bars[0].strokeColor = AMBER, None
        chart.valueAxis.strokeColor = chart.categoryAxis.strokeColor = LINE
        d.add(chart)
        story.append(KeepTogether([Paragraph(_esc(t["chart"]), h2), d, Spacer(1, 4 * mm)]))

    # (the next-points list and the open-mistakes list are not in the report: their names are English content, and a parent
    # reads the numbers above in their own language)

    buf = io.BytesIO()

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("DejaVu", 8)
        canvas.setFillColor(SOFT)
        canvas.drawString(20 * mm, 12 * mm, t["foot"].format(date=date))
        canvas.restoreState()

    SimpleDocTemplate(buf, pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm, topMargin=18 * mm, bottomMargin=20 * mm,
                      title=t["title"], author="SAT Freshman").build(story, onFirstPage=footer, onLaterPages=footer)
    return buf.getvalue()
