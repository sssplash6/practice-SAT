"""Official SAT Weekend dates, verified against College Board on 2026-09-23.

https://satsuite.collegeboard.org/sat/dates-deadlines
The 2027–28 dates below are marked anticipated by College Board.
"""

from __future__ import annotations

import datetime as dt

SAT_DATES = (
    "2026-10-03", "2026-11-07", "2026-12-05",
    "2027-03-06", "2027-05-01", "2027-06-05",
    "2027-08-28", "2027-09-18", "2027-10-02", "2027-11-06", "2027-12-04",
    "2028-03-04", "2028-05-06", "2028-06-03",
)


def upcoming(today: dt.date | None = None) -> list[str]:
    today = today or dt.date.today()
    return [day for day in SAT_DATES if day >= today.isoformat()]
