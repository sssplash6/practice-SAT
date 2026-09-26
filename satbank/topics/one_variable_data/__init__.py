"""Problem-Solving and Data Analysis -> One-Variable Data: Distributions and
Measures of Centre and Spread.

Eighteen templates over the 49 official items. The topic has two halves that
need different machinery: the half that computes a number off a list, a table,
a bar graph, a dot plot or a box plot, and the half that decides which of four
sentences about centre and spread is true. Both are checked the same way --
every answer is re-derived in `audit.py` from the item's own parameters, and
for a sentence the re-derivation fills in the comparison itself.
"""

from __future__ import annotations

from ...topic import Topic
from .audit import AUDITS
from .families import basic as B
from .families import boxes as X
from .families import compare as C
from .families import freq as Q
from .families import means as M
from .families import supply as U
from .sources import ALL, EXCLUDED

TEMPLATES = {
    "ovd.shifted_mean_grid": U.shifted_mean,
    "ovd.scaled_range_grid": U.scaled_range,
    "ovd.list_stat": B.list_stat,
    "ovd.table_stat": B.table_stat,
    "ovd.bar_read": B.bar_read,
    "ovd.freq_stat": Q.freq_stat,
    "ovd.freq_order": Q.freq_order,
    "ovd.freq_two_groups": Q.freq_two_groups,
    "ovd.freq_choose": Q.freq_choose,
    "ovd.compare_sets": C.compare_sets,
    "ovd.sd_compare": C.sd_compare,
    "ovd.measure_effect": C.measure_effect,
    "ovd.odd_measure": C.odd_measure,
    "ovd.new_data_set": C.new_data_set,
    "ovd.box_read": X.box_read,
    "ovd.box_compare": X.box_compare,
    "ovd.unknown_value": M.unknown_value,
    "ovd.mean_totals": M.mean_totals,
    "ovd.mean_identity": M.mean_identity,
    "ovd.reason_center": M.reason_center,
    "ovd.must_be_true": M.must_be_true,
}

TOPIC = Topic(
    slug="one_variable_data",
    name="One-Variable Data: Distributions and Measures of Centre and Spread",
    domain="Problem-Solving and Data Analysis",
    templates=TEMPLATES,
    audits=AUDITS,
    sources=ALL,
    excluded=EXCLUDED,
)
