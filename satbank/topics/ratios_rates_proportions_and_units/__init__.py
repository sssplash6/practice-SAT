"""Problem-Solving and Data Analysis -> Ratios, Rates, Proportional
Relationships, and Units.

Fifty-seven official items collapse to twenty-two templates in three families:
the ratio itself (`ratios`), a quantity per unit of another (`rates`), and a
measure carried from one unit to another (`units`).

One mistake runs through the whole topic, and it is the reason the family
lines fall where they do: the inverted rate. A student who divides where the
factor multiplies gets 22,032 yards out of 612 inches, 324 meters a second
out of 90 kilometers an hour, and $98,000 out of 7,500 pesos -- and College
Board prints exactly those numbers as options. So every template that applies
a factor carries the inversion as a named option, and no rationale in this
package names a conversion factor without also saying which way it goes.

The second mistake is the additive one: comparing two rows of a proportional
table by subtracting rather than by multiplying. It is what makes 36 and 28
the wrong answers beside 160, and what makes "3 ounces more than the first
batch" the wrong answer beside "1.5 times as much".
"""

from __future__ import annotations

from ...topic import Topic
from .audit import AUDITS
from .families import ratios as R
from .families import rates as T
from .families import units as U
from .sources import ALL, EXCLUDED

TEMPLATES = {
    "rr.partner": R.partner,
    "rr.equivalent": R.equivalent,
    "rr.table_constant": R.table_constant,
    "rr.simplify": R.simplify,
    "rr.similar_rect": R.similar_rect,
    "rr.dimension_shift": R.dimension_shift,
    "rr.mix_statement": R.mix_statement,
    "rr.expression": R.expression,
    "rr.multiple": R.multiple,
    "rr.chain_unknown": R.chain_unknown,
    "rr.repeated_factor": R.repeated_factor,
    "rr.unit_rate": T.unit_rate,
    "rr.rate_convert": T.rate_convert,
    "rr.rate_product": T.rate_product,
    "rr.gap": T.gap,
    "rr.growth_table": T.growth_table,
    "rr.table_unit_price": T.table_unit_price,
    "rr.exchange_fee": T.exchange_fee,
    "rr.convert": U.convert,
    "rr.convert_chain": U.convert_chain,
    "rr.pop_density": U.pop_density,
    "rr.cube_density": U.cube_density,
}

TOPIC = Topic(
    slug="ratios_rates_proportions_and_units",
    name="Ratios, Rates, Proportional Relationships, and Units",
    domain="Problem-Solving and Data Analysis",
    templates=TEMPLATES,
    audits=AUDITS,
    sources=ALL,
    excluded=EXCLUDED,
)
