"""Official SAT Weekend dates, verify against College Board.

Dates checked on 2026-09-23 at https://satsuite.collegeboard.org/sat/dates-deadlines;
registration, late-registration and score dates checked on 2026-09-24 there and at
https://satsuite.collegeboard.org/scores/score-release-dates. The 2027–28 dates are
marked anticipated by College Board, which has published no deadlines for them yet,
so theirs are None; spring 2027 score dates are not published either.
"""

from __future__ import annotations

import datetime as dt

CHECKED = "2026-09-24"

# test day: (register_by, late_by, scores_by)
DEADLINES: dict[str, tuple[str | None, str | None, str | None]] = {
    "2026-10-03": ("2026-09-18", "2026-09-22", "2026-10-16"),
    "2026-11-07": ("2026-10-23", "2026-10-27", "2026-11-20"),
    "2026-12-05": ("2026-11-20", "2026-11-24", "2026-12-18"),
    "2027-03-06": ("2027-02-19", "2027-02-23", None),
    "2027-05-01": ("2027-04-16", "2027-04-20", None),
    "2027-06-05": ("2027-05-21", "2027-05-25", None),
    "2027-08-28": (None, None, None),
    "2027-09-18": (None, None, None),
    "2027-10-02": (None, None, None),
    "2027-11-06": (None, None, None),
    "2027-12-04": (None, None, None),
    "2028-03-04": (None, None, None),
    "2028-05-06": (None, None, None),
    "2028-06-03": (None, None, None),
}

SAT_DATES = tuple(sorted(DEADLINES))


def upcoming(today: dt.date | None = None) -> list[str]:
    today = today or dt.date.today()
    return [day for day in SAT_DATES if day >= today.isoformat()]


def entry(day: str) -> dict:
    """One date with its deadlines (None where College Board has none yet)."""
    register_by, late_by, scores_by = DEADLINES.get(day, (None, None, None))
    return {"day": day, "register_by": register_by, "late_by": late_by, "scores_by": scores_by,
            "anticipated": day >= "2027-08-01", "checked": CHECKED}


def dates(today: dt.date | None = None) -> list[dict]:
    """Upcoming dates with their deadlines, for /api/shell.dates and every picker."""
    return [entry(day) for day in upcoming(today)]


def registration(exam_date: str | None, registered: str | None, today: dt.date) -> dict | None:
    """U17's banner: from 7 days before register_by until late_by, while the
    student has not said they registered for that date."""
    if not exam_date or registered == exam_date:
        return None
    e = entry(exam_date)
    if not e["register_by"] or not e["late_by"]:
        return None
    by = dt.date.fromisoformat(e["register_by"])
    late = dt.date.fromisoformat(e["late_by"])
    if not by - dt.timedelta(days=7) <= today <= late:
        return None
    return {**e, "days_left": max(0, (by - today).days), "late": today > by}


assert SAT_DATES == tuple(sorted(SAT_DATES))
assert all(d is None or d < day for day, (r, late, _) in DEADLINES.items() for d in (r, late))
assert registration("2026-11-07", None, dt.date(2026, 10, 18))["days_left"] == 5
assert registration("2026-11-07", "2026-11-07", dt.date(2026, 10, 18)) is None
