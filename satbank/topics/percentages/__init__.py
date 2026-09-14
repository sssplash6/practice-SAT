"""Problem-Solving and Data Analysis -> Percentages.

Fifty-two official items collapse to eighteen templates in three families:
one percent applied once (`basic`), percents applied in sequence (`chains`),
and percents read off a table (`data`).

The distinguishing feature of this topic is that its wrong answers are
already known. A student who gets a percent item wrong nearly always made one
of a short list of mistakes -- subtracted the percent as if it were a count,
put the decimal point one place out, divided by the new value instead of the
original, added two percents that should have been compounded -- and every
option in this package is one of those, named in the words a teacher would
use when handing the paper back.
"""

from __future__ import annotations

from ...topic import Topic
from .audit import AUDITS
from .families import basic as B
from .families import chains as C
from .families import data as D
from .sources import ALL, EXCLUDED

TEMPLATES = {
    "pct.of": B.percent_of,
    "pct.find_percent": B.find_percent,
    "pct.increase_decrease": B.increase_decrease,
    "pct.reverse": B.reverse,
    "pct.change": B.change,
    "pct.multiplier": B.multiplier,
    "pct.expression": B.expression,
    "pct.compound_share": C.compound_share,
    "pct.successive": C.successive,
    "pct.two_step": C.two_step,
    "pct.markup_discount": C.markup_discount,
    "pct.repeated_rate": C.repeated_rate,
    "pct.remainder_total": C.remainder_total,
    "pct.per_serving_model": C.per_serving_model,
    "pct.table_share": D.table_share,
    "pct.percent_table": D.percent_table,
    "pct.series": D.series_change,
    "pct.conclusion": D.conclusion,
}

TOPIC = Topic(
    slug="percentages",
    name="Percentages",
    domain="Problem-Solving and Data Analysis",
    templates=TEMPLATES,
    audits=AUDITS,
    sources=ALL,
    excluded=EXCLUDED,
)
