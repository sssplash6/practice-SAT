"""The 46 official Linear Inequalities items, encoded as the parameters that
reproduce them.

No answer is written here. The answers live in
`material/keys/linear_inequalities.json`, read from the College Board PDF's own
text layer, and the check drives these templates with each source item's own
numbers and asks whether the engine lands on them.

Every one of the 46 is encoded; nothing is excluded. Where the source prints a
distractor this engine does not model -- 1.16's 76, 2.1's 2, and the 4,332 that
2.9 prints where its own stem says 4,334 -- the note on the entry says so.
"""

from __future__ import annotations

from fractions import Fraction as F

from ...topic import S, Source
from .families.bands import band_formula, band_from_extremes, band_scale
from .families.counting import (pair_max, value_in_range, which_interval,
                                whole_number_bound)
from .families.interpret import interpret
from .families.model import model_one_var, model_system, model_two_var
from .families.points import point_solution
from .families.solve import (allowable_dimension, greatest_value, range_solve,
                             triangle_third_side, y_range_from_system)

ALL: list[Source] = [
    # ------------------------------------------------------------- easy (16)
    S("1.1", lambda r: model_two_var(r, 0, scene="beads", a=F(3, 10),
                                     b=F(7, 10), total=400, op=">=", u="x",
                                     v="y", who="Valentina", thing="beads",
                                     adj="red")),
    S("1.2", lambda r: model_two_var(r, 0, scene="drive", a=35, b=40, total=220,
                                     op="<", u="r", v="j",
                                     names=("Rhett", "Jessica"))),
    S("1.3", lambda r: value_in_range(r, 0, scene="trays", lo=50, hi=60, n=4,
                                      inside=5, thing="cookies")),
    S("1.4", lambda r: model_one_var(r, 0, shape="mean", scores=[85, 78, 98],
                                     target=90, op=">=", var="G", name="Tom",
                                     subject="history")),
    S("1.5", lambda r: value_in_range(r, 0, scene="body", lo=F(489, 5), hi=F(99),
                                      inside=F(1, 10),
                                      offsets=[F(1, 5), F(7, 10), F(9, 10)],
                                      who="Kevin")),
    S("1.6", lambda r: point_solution(r, 0, ask="roman",
                                      rows=[("lin", 5, -3, 4, "<")],
                                      pairs=[(1, 1), (2, 5), (3, 2)],
                                      picks=["abs", "negative", "swap"])),
    S("1.7", lambda r: model_two_var(r, 0, scene="store", a=15, b=25, total=120,
                                     op="<=", u="s", v="p", who="Geoff",
                                     clothes=("shirts", "shirt", "pants",
                                              "pair of pants"))),
    S("1.8", lambda r: model_system(r, 0, shape="count_cost", a=3, b=4, least=20,
                                    budget=80, u="x", v="y",
                                    items=("workbooks", "sets of flash cards",
                                           "each", "per set"))),
    S("1.9", lambda r: whole_number_bound(r, 0, scene="rental", fee=10, rate=60,
                                          limit=280, who="Maria",
                                          rental=("boat",
                                                  "water safety course"))),
    S("1.10", lambda r: whole_number_bound(r, 0, scene="packages", rate=12,
                                           limit=50, party="dinner rolls")),
    S("1.11", lambda r: band_from_extremes(r, 0, scene="migration", lo=1510,
                                           hi=4130, var="d", thing="dragonfly",
                                           picks=["lo_cap", "hi_floor",
                                                  "sum_band"])),
    S("1.12", lambda r: point_solution(r, 0, ask="system", x=8, y=2)),
    S("1.13", lambda r: interpret(r, 0, shape="pair", first=8, second=3, cap=27,
                                  op="<=",
                                  figure=("rectangle", "length", "width",
                                          "perimeter"))),
    S("1.14", lambda r: band_scale(r, 0, scene="granite", lo=F(127, 10),
                                   hi=F(157, 10), rate=165, var="x",
                                   thing="granite",
                                   picks=["subtract", "add", "divide"])),
    S("1.15", lambda r: band_from_extremes(r, 0, scene="temperature", lo=31,
                                           hi=67, var="t", thing="Illinois",
                                           weeks=3,
                                           picks=["sum_floor", "hi_floor",
                                                  "lo_cap"])),
    S("1.16", lambda r: whole_number_bound(r, 0, scene="shortfall", limit=100,
                                           fee=86, who="Julissa"),
      "the source's 76 is not reproduced: no reading of 100 and 86 this engine "
      "models lands on it"),

    # ----------------------------------------------------------- medium (16)
    S("2.1", lambda r: pair_max(r, 0, w1=100, w2=120, least=10, cap=1100,
                                thing="packages", vehicle="cargo helicopter",
                                unit="pound"),
      "the source's 2 is not reproduced: it is below every count this engine's "
      "misreadings of the two constraints produce"),
    S("2.2", lambda r: model_system(r, 0, shape="staffing", pay1=640, pay2=880,
                                    staff=10, budget=9700, min1=3, min2=1,
                                    u="x", v="y", name="Marisa",
                                    roles=("junior directors",
                                           "senior directors"))),
    S("2.3", lambda r: band_scale(r, 0, scene="parking", lo=F(15, 2), hi=9,
                                  rate=135, var="n",
                                  picks=["swapped_total", "widths",
                                         "total_top"])),
    S("2.4", lambda r: point_solution(r, 0, ask="point",
                                      rows=[("y", 1, 0, "<="),
                                            ("y", -1, 0, "<=")],
                                      cands=[(1, 0), (-1, 0), (0, 1),
                                             (0, -1)])),
    S("2.5", lambda r: point_solution(r, 0, ask="point",
                                      rows=[("y", -4, 4, "<")],
                                      cands=[(-4, 0), (0, 5), (2, 1),
                                             (2, -1)])),
    S("2.6", lambda r: band_formula(r, 0, scene="elephant", lo=2, hi=3, mult=365,
                                    off=200, var="w", thing="elephant",
                                    picks=["offset_times", "shifted",
                                           "no_offset"])),
    S("2.7", lambda r: band_formula(r, 0, scene="heart", lo=F(1, 2),
                                    hi=F(17, 20), mult=120, off=60, var="H",
                                    thing="Alice",
                                    picks=["offset_lower", "no_offset",
                                           "offset_upper"])),
    S("2.8", lambda r: band_scale(r, 0, scene="whale", lo=72, hi=77, rate=16,
                                  var="x",
                                  thing="whales from the genus Eschrichtius",
                                  picks=["add", "total_added",
                                         "band_on_total"])),
    S("2.9", lambda r: model_one_var(r, 0, shape="payback", before=4334,
                                     after=2712, install=25000, var="t",
                                     thing="a geothermal heating system"),
      "the source prints 4,332 in its last option where its own stem says "
      "4,334, so that option is not reproduced letter for letter"),
    S("2.10", lambda r: point_solution(r, 0, ask="point",
                                       rows=[("y", 3, 1, "<="),
                                             ("lin", 1, -1, 1, ">")],
                                       cands=[(-2, -1), (-1, 3), (1, 5),
                                              (2, -1)])),
    S("2.11", lambda r: model_one_var(r, 0, shape="perimeter", length=50,
                                      total=210, op="<=", var="x",
                                      unit="inches", thing="rectangle")),
    S("2.12", lambda r: whole_number_bound(r, 0, scene="trailer", fee=500,
                                           rate=120, limit=4600)),
    S("2.13", lambda r: model_system(r, 0, shape="ratio", scene="bushes", k=3,
                                     cap=164, u="a", v="b", ratio_op="<=",
                                     names=("azaleas", "boxwoods"))),
    S("2.14", lambda r: which_interval(r, 0, thr=100, key=(106, 158),
                                       wrong=[(80, 100), (42, 87), (17, 85)],
                                       var="h", unit="centimeters", word="tall",
                                       thing="plant species",
                                       measure="typical height when fully "
                                               "grown")),
    S("2.15", lambda r: point_solution(r, 0, ask="table",
                                       rows=[("y", 7, -4, ">")], xs=[3, 5, 8],
                                       key_off=[4, 4, 4],
                                       wrong_offs=[[-4, -4, -4], [0, 0, 0],
                                                   [4, -4, 0]]),
      "the source prints each option as a two-column table; the engine prints "
      "the same pairs on one line, as the transcript does"),
    S("2.16", lambda r: whole_number_bound(r, 0, scene="venue", fee=35,
                                           rate=F(41, 4), limit=300)),

    # ------------------------------------------------------------- hard (14)
    S("3.1", lambda r: model_one_var(r, 0, shape="race", walk=20, ride=5,
                                     every=30, name="Adam", var="w",
                                     travel=("walk", "bus ride", "bus"))),
    S("3.2", lambda r: model_system(r, 0, shape="ratio", scene="laundry", k=2,
                                    cap=300, u="d", v="s", ratio_op=">=",
                                    w1=F(147, 20), w2=F(31, 5),
                                    names=("detergent", "fabric softener"))),
    S("3.3", lambda r: whole_number_bound(r, 0, scene="transit", rate=F(7, 2),
                                          limit=95,
                                          prices="$1.50, $2.50, or $3.50")),
    S("3.4", lambda r: range_solve(r, 0, pct=11, k1=3, k2=4, base="x", var="s")),
    S("3.5", lambda r: greatest_value(r, 0, m=3, k=2, y=-4, op="<=",
                                      phrase="less", u="x", v="y", fmt="spr")),
    S("3.6", lambda r: model_one_var(r, 0, shape="share", half=150, first=36,
                                     pct=20, pics=5, var="p")),
    S("3.7", lambda r: triangle_third_side(r, 0, a=6, b=12, var="x")),
    S("3.8", lambda r: whole_number_bound(r, 0, scene="ohm", rate=F(3, 250),
                                          limit=F(1, 4), ohms=500, volts=6,
                                          amp="ampere")),
    S("3.9", lambda r: allowable_dimension(r, 0, cap=130, height=60,
                                           factor=F(5, 2), var="x")),
    S("3.10", lambda r: whole_number_bound(r, 0, scene="farm", fee=80, rate=10,
                                           limit=270, scale=F(9, 10),
                                           first_rate=8, first_hours=10,
                                           who="Ken")),
    S("3.11", lambda r: y_range_from_system(r, 0, m=2, c=-1, n=2, t=5, u="x",
                                            v="y")),
    S("3.12", lambda r: interpret(r, 0, shape="term", a=11, b=14, total=115,
                                  who="Anthony", piece="second",
                                  goods=("small cheese pizzas",
                                         "large cheese pizzas",
                                         "a team dinner"))),
    S("3.13", lambda r: point_solution(r, 0, ask="table",
                                       rows=[("y", 6, 2, "<")], xs=[3, 5, 7],
                                       key_off=[-4, -4, -4],
                                       wrong_offs=[[4, 4, 4], [0, 0, 0],
                                                   [-4, 4, -4]]),
      "the source prints each option as a two-column table; the engine prints "
      "the same pairs on one line, as the transcript does"),
    S("3.14", lambda r: model_one_var(r, 0, shape="two_group", n1=140, n2=220,
                                      gap=3, total=5820, op=">=", var="x",
                                      thing="new uniforms")),
]

# Every official item is encoded. An item would be excluded here only if its
# question could not be rebuilt from parameters -- none of these 46 depends on
# a picture, and the two that print their options as tables print pairs a line
# of text can carry.
EXCLUDED: dict[str, str] = {}
