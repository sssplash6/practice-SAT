"""The 52 official Percentages items, encoded as the parameters that reproduce
them.

No answer appears here. The answers live in
`material/keys/percentages.json`, read from the College Board PDF's own text
layer, and the check drives each template with the numbers below and asks
whether the engine lands on them. A template whose arithmetic is wrong cannot
be made to pass by writing the answer down.
"""

from __future__ import annotations

from fractions import Fraction as F

from ...topic import S, Source
from .families.basic import (change, expression, find_percent, increase_decrease,
                             multiplier, percent_of, reverse)
from .families.chains import (COMMITTEES, compound_share, markup_discount,
                              per_serving_model, remainder_total, repeated_rate,
                              successive, two_step)
from .families.data import (CALLS, CLIMATE, GRAPHED, SERIES_CTX, SOLD, SURVEYS, VOTES,
                            conclusion, percent_table, series_change, table_share)

WAGES = SERIES_CTX[0]
BEADS = ("beads", "bag", "silver", True)
MARBLES = ("marbles", "group", "blue", True)

ALL: list[Source] = [
    # ------------------------------------------------------------ set 1
    S("1.1", lambda r: series_change(r, 0, ask="change", ctx=WAGES, start_year=1960,
                                     step=10, i=0, j=1, fmt="mcq",
                                     values=[1, F(8, 5), F(31, 10), F(19, 5),
                                             F(103, 20), F(29, 4)],
                                     wrongs=["halved", "earlier_of_later", "doubled"])),
    S("1.2", lambda r: increase_decrease(r, 0, frame="sales_tax", n=20, pct=5, up=True,
                                         fmt="mcq")),
    S("1.3", lambda r: percent_of(r, 0, frame="of_last_year", pct=147, n=200, fmt="mcq")),
    S("1.4", lambda r: percent_of(r, 0, frame="bare", pct=23, n=100, fmt="mcq")),
    S("1.5", lambda r: expression(r, 0, kind="of", pct=89, var="h",
                                  ctx=("parallelogram", "base", "height"),
                                  wrongs=["whole_number", "one_place_too_many",
                                          "one_place_too_few"])),
    S("1.6", lambda r: percent_table(r, 0, survey=SURVEYS[0], total=1200, picks=[0, 1],
                                     ask="two", pcts=[63, 13, 9, 6, 2, 7], fmt="mcq")),
    S("1.7", lambda r: percent_of(r, 0, frame="workday", pct=15, n=8, fmt="mcq",
                                  wrongs=["answer_in_hours", "percent_itself",
                                          "percent_of_one_hour"])),
    S("1.8", lambda r: percent_of(r, 0, frame="inventory", pct=10, n=170, fmt="spr",
                                  ctx=("blocks", "container", "green", True))),
    S("1.9", lambda r: table_share(r, 0, scenario="calls", ask="row_share", row=0, col=0,
                                   fmt="mcq",
                                   counts=[[16, 49, 72, 8], [4, 10, 22, 34],
                                           [8, 56, 45, 16], [22, 42, 84, 12]],
                                   wrongs=["grand_total", "cell_as_percent",
                                           "column_total"])),
    S("1.10", lambda r: increase_decrease(r, 0, frame="projection", n=113000, pct=29,
                                          up=True, round_to=100, fmt="mcq",
                                          wrongs=["percent_as_count_hundreds",
                                                  "percent_decimal_slip",
                                                  "percent_as_count_thousands"])),
    S("1.11", lambda r: percent_of(r, 0, frame="rate_closest", pct=15, n=F(391, 5),
                                   fmt="mcq")),
    S("1.12", lambda r: increase_decrease(r, 0, frame="discount", n=50, pct=20, up=False,
                                          fmt="mcq")),
    S("1.13", lambda r: percent_of(r, 0, frame="bare", pct=10, n=370, fmt="mcq")),
    S("1.14", lambda r: percent_of(r, 0, frame="tip_bill", pct=20, n=25, fmt="mcq")),
    S("1.15", lambda r: increase_decrease(r, 0, frame="bare", n=60, pct=20, up=True,
                                          fmt="mcq")),
    S("1.16", lambda r: reverse(r, 0, frame="is_p_of", result=21, pct=21, fmt="mcq")),
    S("1.17", lambda r: find_percent(r, 0, frame="of_n_things", part=828000,
                                     whole=900000, ctx=BEADS, fmt="mcq",
                                     wrongs=["complement", "difference_in_thousands",
                                             "halved"])),
    S("1.18", lambda r: percent_of(r, 0, frame="bare", pct=10, n=470, fmt="mcq")),
    S("1.19", lambda r: find_percent(r, 0, frame="what_percentage_of", part=75, whole=300,
                                     fmt="mcq",
                                     wrongs=["part_as_percent", "difference",
                                             "doubled"])),
    S("1.20", lambda r: percent_of(r, 0, frame="inventory", pct=4, n=350, fmt="mcq",
                                   ctx=("objects", "box", "balls", False))),

    # ------------------------------------------------------------ set 2
    S("2.1", lambda r: conclusion(r, 0, ctx=VOTES[0], turnout=10, split=30, rate_a=70,
                                  rate_b=40,
                                  wrongs=["all_had_voted", "younger",
                                          "one_channel_for_all"])),
    S("2.2", lambda r: repeated_rate(r, 0, units=1300000, pct=15, months=5,
                                     thing="smartphone", fmt="mcq")),
    S("2.3", lambda r: expression(r, 0, kind="increase", pct=9, var="x",
                                  wrongs=["increase_only", "percent_as_count",
                                          "decimal_added"])),
    S("2.4", lambda r: multiplier(r, 0, n=50, pct=36, up=True, ask="factor", fmt="mcq",
                                  wrongs=["percent_itself", "decimal_slip",
                                          "change_only"])),
    S("2.5", lambda r: multiplier(r, 0, n=100, pct=13, up=True, ask="percent", fmt="mcq",
                                  wrongs=["multiplier_ten_times", "answer_ten_times",
                                          "added_the_hundred"])),
    S("2.6", lambda r: compound_share(r, 0, pcts=(40, 30), ask="share", fmt="mcq",
                                      ctx=("red", "striped"))),
    S("2.7", lambda r: reverse(r, 0, frame="increased_to", result=318, pct=6, fmt="mcq",
                               wrongs=["decimal_multiplier", "decrease_instead",
                                       "increase_again"])),
    S("2.8", lambda r: change(r, 0, frame="bill", old=F(3787, 50), new=F(3993, 50),
                              fmt="mcq")),
    S("2.9", lambda r: reverse(r, 0, frame="is_p_of", result=432, pct=96, fmt="spr")),
    S("2.10", lambda r: increase_decrease(r, 0, frame="bare", n=115, pct=40, up=True,
                                          fmt="spr")),
    S("2.11", lambda r: successive(r, 0, frame="depreciation", start=800, pcts=(20,),
                                   years=2, fmt="mcq", places=0,
                                   wrongs=["years_added", "divided_each_year",
                                           "one_year"])),
    S("2.12", lambda r: change(r, 0, frame="percent_increase", old=9, new=90, fmt="mcq")),
    S("2.13", lambda r: find_percent(r, 0, frame="is_p_percent_of", part=13, whole=25,
                                     fmt="spr")),
    S("2.14", lambda r: table_share(r, 0, ask="ratio", rows_a=0, rows_b=2, fmt="spr",
                                    counts=[[375], [54], [690], [81]],
                                    ctx=("Group", ["A", "B", "C", "D"], "objects"))),
    S("2.15", lambda r: compound_share(r, 0, ask="count", base=1250, pcts=(72, 36),
                                       fmt="spr",
                                       ctx=("An insurance company", "information sessions",
                                            "information session"))),

    # ------------------------------------------------------------ set 3
    S("3.1", lambda r: per_serving_model(r, 0, per=5, amount=180, serving="3/4 cup",
                                         ctx=("Crunchy Grain", "cereal", "potassium",
                                              "milligrams"),
                                         wrongs=["decimal_slip", "decimal_compounded",
                                                 "growth_factor"])),
    S("3.2", lambda r: remainder_total(r, 0, pcts=(15, 45, 25), left=6, ask="difference",
                                       ctx=COMMITTEES[0], fmt="spr")),
    S("3.3", lambda r: series_change(r, 0, ask="project", values=[5600, 5880],
                                     start_year=2012, multiple=2, ctx=SOLD[0], fmt="mcq")),
    # the line graph labels (2003, 40) and (2007, 10) and nothing else; the
    # other eleven years carry no printed value in the source either
    S("3.4", lambda r: series_change(r, 0, ask="change", show="graph", ctx=GRAPHED[0],
                                     start_year=2003, step=1, i=0, j=4, fmt="spr",
                                     values=[40, 13, 13, 14, 10, 5, 8, 56, 10, 2, 3, 32,
                                             18])),
    S("3.5", lambda r: two_step(r, 0, pct1=70, up1=False, pct2=80, up2=True, ask="times",
                                fmt="spr")),
    S("3.6", lambda r: table_share(r, 0, scenario="climate", ask="group_diff",
                                   rows_a=[0, 1], rows_b=[2, 3], col=0, fmt="mcq",
                                   counts=[[295, 168, 45], [246, 123, 41],
                                           [238, 117, 48], [137, 78, 64]])),
    S("3.7", lambda r: two_step(r, 0, pct1=70, up1=False, pct2=60, up2=True, ask="times",
                                fmt="spr")),
    S("3.8", lambda r: two_step(r, 0, pct1=110, up1=True, pct2=55, up2=False, start=50,
                                ask="value", letters=("w", "z"), fmt="spr")),
    S("3.9", lambda r: percent_of(r, 0, frame="by_mass", pct=F(1, 1000), n=140, fmt="spr",
                                  ctx=("alloy", "phosphorus"))),
    S("3.10", lambda r: compound_share(r, 0, pcts=(37, 37, 42), ask="complement",
                                       ctx=("green", "rectangular", "metal"), fmt="mcq")),
    S("3.11", lambda r: two_step(r, 0, pct1=60, up1=True, pct2=45, up2=False, ask="times",
                                 fmt="spr")),
    S("3.12", lambda r: successive(r, 0, frame="two_changes", pcts=(167, 16),
                                   ups=(True, False), ask="net_percent", fmt="mcq",
                                   ctx="collectible comic book")),
    S("3.13", lambda r: change(r, 0, frame="p_greater", old=10, new=140, fmt="mcq")),
    S("3.14", lambda r: reverse(r, 0, frame="removed_remained", result=360, pct=20,
                                ask="removed", ctx=MARBLES, fmt="mcq")),
    S("3.15", lambda r: two_step(r, 0, pct1=190, up1=True, pct2=80, up2=False, start=24,
                                 ask="value", letters=("a", "b"), fmt="mcq", places=2,
                                 wrongs=["first_as_share", "percents_netted",
                                         "both_as_shares"])),
    S("3.16", lambda r: two_step(r, 0, pct1=110, up1=True, pct2=90, up2=False, start=47,
                                 ask="value", letters=("a", "b"), fmt="spr")),
    S("3.17", lambda r: markup_discount(r, 0, cost=5, markup=270, discount=70, months=4,
                                        thing="books", fmt="spr")),
]

# Every official item is encoded. 3.4 was excluded while plot.py could draw a
# line graph but not label a point on it; `plot.line_graph` now takes
# `labels={0: "(2003, 40)"}`, so the regenerated figure prints the two totals
# the question turns on and the item is answerable from the figure again.
EXCLUDED: dict[str, str] = {}
