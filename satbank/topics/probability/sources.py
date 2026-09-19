"""The 36 official Probability items, as the parameters that rebuild them.

No answer appears here. Each row hands a template the numbers the College
Board printed -- the cells of its table, the counts in its stem, the surface
its options are written in -- and the check asks whether the engine lands on
the answer the key file records.

`wrongs=` names, in printed order, the three mistakes the item writer reached
for. It never says which option is right: a name that lands on the key is
dropped as a duplicate by `assemble`, and the pool entry it names is built
from the same cells as the key, so a wrong `wrongs=` list makes an item with
three options rather than an item with the wrong answer.
"""

from __future__ import annotations

from ...topic import S
from .families.derived import (cell_from_total, missing_cell, nearest_row,
                               percent_columns)
from .families.freq import freq_grouped, freq_table
from .families.simple import (bag, count_from_prob, data_set, rate_share,
                              subset, symbolic)
from .families.twoway import conditional, grouped, joint, marginal

# the cells of the two-way tables the source items print, interior only:
# every margin on the page is the sum of the cells above or beside it
GAS = [[60, 25], [35, 15]]
INTERNSHIPS = [[87, 80, 75, 76, 70], [44, 54, 65, 76, 82]]
TEENS = [[110, 146], [139, 164], [166, 74]]
DEALERSHIP = [[15, 15], [20, 85]]
CARS = [[5, 3], [2, 4]]
KITTENS = [[16, 16], [12, 4]]
PARKS = [[20, 5], [8, 4]]
RAIN = [[12, 48], [8, 16]]
PENGUINS = [[41, 59], [8, 27], [49, 54], [42, 40]]
DEGREES = [[4, 3], [2, 6]]
TILES = [[10, 20, 25], [20, 10, 15]]
CONTESTANTS = [[2, 3, 4, 6, 2, 3], [2, 3, 5, 5, 4, 1], [3, 3, 4, 5, 3, 2]]
BLOOD = [[33, 9, 3, 37], [7, 2, 1, 8]]
PARTICIPANTS_35 = [[7, 14, 9], [6, 4, 20], [17, 12, 1]]
PARTICIPANTS_38 = [[5, 17, 8], [6, 8, 16], [19, 5, 6]]
TAXES = [[39, 4], [6, 1]]
CALLS = [[48, 623], [130, 90]]
FLOWERS = [[35, 15], [31, 21]]
SPORTS_SURVEY = [[312, 220], [252, 216]]

ALL = [
    # ---------------------------------------------------------------- easy
    S("1.1", lambda r: freq_table(r, 0, scenario="marbles", counts=[8, 10, 22],
                                  cats=["Red", "Blue", "Green"], idx=1,
                                  surface="ratio", total_row=True,
                                  wrongs=["not", "cat2", "not2"])),
    S("1.2", lambda r: marginal(r, 0, scenario="gas", cells=GAS, axis="row", idx=1,
                                surface="ratio",
                                wrongs=["cell11/row", "cell11/col", "cell10/row"]),
      "the printed table does not add up -- see the transcript; the engine prints "
      "the column total the cells give, 95, where the source prints 90"),
    S("1.3", lambda r: conditional(r, 0, scenario="internships", cells=INTERNSHIPS,
                                   ev_axis="row", ev_idx=1, cd_idx=2, surface="ratio",
                                   frame="of_the", margins=False, tier="easy",
                                   wrongs=["diff0", "other0", "over_other0"])),
    S("1.4", lambda r: freq_table(r, 0, scenario="singers", counts=[4, 6, 10, 5],
                                  idx=2, surface="decimal", places=2, total_row=False,
                                  wrongs=["count_as_decimal", "not", "over_others"])),
    S("1.5", lambda r: cell_from_total(r, 0, scenario="sports_survey",
                                       cells=SPORTS_SURVEY, hr=1, hc=0,
                                       wrongs=["minus_row", "minus_col",
                                               "minus_cell"])),
    S("1.6", lambda r: freq_table(r, 0, scenario="rocks", counts=[10, 33, 27], idx=0,
                                  surface="ratio", total_row=False,
                                  wrongs=["over2", "over1", "over_others"])),
    S("1.7", lambda r: subset(r, 0, scenario="planets", surface="reduced",
                              wrongs=["one_over_total", "one_over_part",
                                      "inverted"])),
    S("1.8", lambda r: marginal(r, 0, scenario="teens", cells=TEENS, axis="col",
                                idx=0, surface="ratio",
                                wrongs=["one", "/col1", "col1"])),
    S("1.9", lambda r: subset(r, 0, scenario="shipment", n=1_000, k=4,
                              surface="decimal",
                              wrongs=["shift1", "shift2", "count"])),
    S("1.10", lambda r: symbolic(r, 0, which="nonfiction books", k=12, ask_first=True,
                                 wrongs=["over_other", "inverted",
                                         "other_over_total"])),
    S("1.11", lambda r: count_from_prob(r, 0, mode="single", scenario="marbles",
                                        n=60, p="7/20",
                                        wrongs=["prob_as_count", "complement",
                                                "total_minus_digits"])),
    S("1.12", lambda r: bag(r, 0, which="buttons", counts=[8, 2, 10],
                            colors=["white", "orange", "brown"], idx=0, style="colon",
                            surface="ratio",
                            wrongs=["other1", "other2", "complement"])),
    S("1.13", lambda r: data_set(r, 0, values=[-13, 4, 23], trait="negative",
                                 wrongs=["none", "complement", "all"])),
    S("1.14", lambda r: marginal(r, 0, scenario="dealership", cells=DEALERSHIP,
                                 axis="row", idx=1, surface="ratio",
                                 wrongs=["row0", "col0", "col1"])),

    # -------------------------------------------------------------- medium
    S("2.1", lambda r: joint(r, 0, scenario="cars", cells=CARS, ri=1, cj=0,
                             surface="reduced",
                             wrongs=["over_col", "over_row", "cell11_over_col"])),
    S("2.2", lambda r: conditional(r, 0, scenario="kittens", cells=KITTENS,
                                   ev_axis="col", ev_idx=0, cd_idx=1, surface="ratio",
                                   frame="fraction_of",
                                   wrongs=["joint", "reverse", "in0"])),
    S("2.3", lambda r: joint(r, 0, scenario="parks", cells=PARKS, ri=0, cj=1,
                             surface="ratio", margins=False,
                             wrongs=["over_row", "cell10_over_col", "over_col"])),
    S("2.4", lambda r: bag(r, 0, which="cubes", counts=[7, 4, 33, 33],
                           colors=["red", "white", "blue", "yellow"], neither=(2, 3),
                           style="inline", surface="reduced",
                           wrongs=["complement", "over_subset0", "subset_over2"])),
    S("2.5", lambda r: subset(r, 0, scenario="polygon", n=14, letter="D", fmt="spr",
                              tier="medium")),
    S("2.6", lambda r: conditional(r, 0, scenario="rain", cells=RAIN, ev_axis="row",
                                   ev_idx=1, cd_idx=1, surface="reduced",
                                   frame="select_cond",
                                   wrongs=["joint", "reverse", "other0"])),
    S("2.7", lambda r: count_from_prob(r, 0, mode="third", n=275, p="11/25",
                                       p2="6/25", tier="medium")),
    S("2.8", lambda r: rate_share(r, 0, which="new accounts", rate=1_200,
                                  total=60_000, days=5,
                                  wrongs=["one_over_days", "days_over_scaled",
                                          "one_day"])),
    S("2.9", lambda r: freq_grouped(r, 0, scenario="presidents", start=40, width=5,
                                    bands=6, counts=[2, 7, 13, 11, 7, 3], cut=2,
                                    cut2=4, total_row=False,
                                    wrongs=["joint", "band", "complement_in"]),
      "option D prints 25/34; the complement inside the condition is 24/34 and the "
      "engine offers that -- see the fidelity note in OPTION-CHECK.md"),
    S("2.10", lambda r: nearest_row(r, 0, scenario="penguins", cells=PENGUINS, cj=1,
                                    frac="1/3")),
    S("2.11", lambda r: bag(r, 0, which="pens", counts=[13, 37],
                            colors=["red", "blue"], idx=0, style="contains",
                            fmt="spr", tier="medium")),
    S("2.12", lambda r: conditional(r, 0, scenario="degrees", cells=DEGREES,
                                    ev_axis="row", ev_idx=1, cd_idx=0,
                                    surface="reduced", frame="if_cond", margins=False,
                                    wrongs=["joint", "reverse",
                                            "event_over_grand"])),
    S("2.13", lambda r: marginal(r, 0, scenario="tiles", cells=TILES, axis="col",
                                 idx=0, fmt="spr", tier="medium")),

    # ---------------------------------------------------------------- hard
    S("3.1", lambda r: grouped(r, 0, scenario="contestants", cells=CONTESTANTS,
                               ev_axis="row", ev_idx=3, cd_idx=0,
                               frame="select_cond", fmt="spr")),
    S("3.2", lambda r: missing_cell(r, 0, scenario="blood", cells=BLOOD, hr=1, hc=3,
                                    ec=1)),
    S("3.3", lambda r: percent_columns(r, 0, scenario="alumni",
                                       first=[55, 20, 20, 5], second=[80, 10, 5, 5],
                                       mult=2, idx=2)),
    S("3.4", lambda r: count_from_prob(r, 0, mode="round", n=97, before=83, p="43/100",
                                       unit="million", tier="hard")),
    S("3.5", lambda r: grouped(r, 0, scenario="participants", cells=PARTICIPANTS_35,
                               ev_axis="row", ev_idx=0, cd_idx=3, frame="given",
                               fmt="spr")),
    S("3.6", lambda r: conditional(r, 0, scenario="taxes", cells=TAXES, ev_axis="row",
                                   ev_idx=1, cd_idx=0, surface="percent", places=1,
                                   margins=False, tier="hard",
                                   wrongs=["count_as_percent", "joint",
                                           "event_over_grand"])),
    S("3.7", lambda r: conditional(r, 0, scenario="calls", cells=CALLS, ev_axis="col",
                                   ev_idx=0, cd_idx=0, surface="decimal", places=2,
                                   approx=True, frame="select_cond", tier="hard",
                                   wrongs=["joint", "event_over_grand", "reverse"])),
    S("3.8", lambda r: grouped(r, 0, scenario="participants", cells=PARTICIPANTS_38,
                               ev_axis="row", ev_idx=0, cd_idx=3, surface="reduced",
                               frame="given",
                               wrongs=["joint", "single1", "reverse"])),
    S("3.9", lambda r: conditional(r, 0, scenario="flowers", cells=FLOWERS,
                                   ev_axis="col", ev_idx=0, cd_idx=0, frame="given",
                                   fmt="spr", tier="hard")),
]

EXCLUDED: dict[str, str] = {}
