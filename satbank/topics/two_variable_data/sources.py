"""The 39 official Two-Variable Data items, encoded as the parameters that
reproduce them.

No answer appears here. Each record pins a template to the source item's own
numbers -- the line the College Board drew, the points it plotted, the x it
asked about -- and the check drives the template and asks whether the engine
lands on the answer in `material/keys/two_variable_data.json`.

Where a record names `wrongs=`, it is naming the misconceptions the College
Board itself printed as the other three options, in the order it printed them.
That is never a statement about which answer is right: every name in the list
is a wrong answer, and which of the four is the key is decided by the material.
"""

from __future__ import annotations

from fractions import Fraction as Q

from ...topic import S, Source
from .families.describe import association, graph_statement, interpret_slope, model_type
from .families.fit import fit_equation, fit_slope, predict_from_line, residual, slope_scaled
from .families.models import best_model, growth_compare, invest_compare, nonlinear_table
from .families.read import (curve_read, interval_change, point_read, rate_of_change,
                            series_extreme)

# The Lake Tahoe scatterplot carries two official items -- a prediction and a
# description of the association -- so its line is written down once.
TAHOE = dict(m=Q(-11, 5_000), b=Q(577, 10))

# One scatterplot, two official questions: 2.11 reads the line at x = 32 and
# 2.13 reads the same line at x = 25.5.
XY = dict(m=Q(-58, 65), b=Q(2_012, 65))

COFFEE = [195, 152, 137, 123, 110, 99, 91, 85, 83, 80, 76, 75, 74, 73, 73]
MOVIES = [2, 2, 6, 8, 6, 8, 20, 26, 45]
CHIPMUNKS = [38, 38, 98, 101, 52, 158, 49, 98, 93, 52, 112]
GRADUATES = [225, 220, 232, 269, 281, 261, 275]
JUNE = [69, 60, 73, 67, 64, 62, 65]
WOLVES = ([40, 43, 47, 50, 53, 55, 60, 63, 65], [5, 5, 6, 6, 7, 6, 7, 7, 8])
NECTARINES = ([1, 2, 3, 4, 5, 6, 7, 8], [1, 10, 21, 40, 46, 60, 76, 85])
BIRD = [14, 6, 10, 15, 14.2, 7, 11, 14, 13.5, 13.2]
TREADMILL = [(0, 0), (5, 7), (10, 7), (20, 5), (25, 8), (30, 0)]

# Ten charities on an evenly spaced income axis. The residuals sum to zero and
# so does their product with the income, which is what leaves the drawn line as
# the least-squares line of these ten points; the +7 at the sixth charity is the
# gap the question asks the student to measure.
CHARITY_X = [500 + 650 * k for k in range(10)]
CHARITY_R = [0, -3, 0, 0, 0, 7, 0, 0, -4, 0]

ALL: list[Source] = [
    # --------------------------------------------------------------- easy
    S("1.1", lambda r: best_model(r, 0, ctx=0, a=2, b=-11, c=20, b2=-5, c2=-3,
                                  wrongs=["c_sign", "alt", "alt_c_sign"])),
    S("1.2", lambda r: interval_change(r, 0, ctx=0, values=COFFEE, x0=0, gap=10,
                                       offer=[0, 3, 5, 9])),
    S("1.3", lambda r: predict_from_line(r, 0, ctx=0, xq=8_500, n=8,
                                         wrongs=["one_low", "one_high", "two_high"],
                                         **TAHOE)),
    S("1.4", lambda r: series_extreme(r, 0, ctx=0, values=GRADUATES, x0=2_001,
                                      ask="least", offer=[1, 3, 4, 6])),
    S("1.5", lambda r: graph_statement(r, 0, ctx=0, pts=TREADMILL)),
    S("1.6", lambda r: predict_from_line(r, 0, ctx=5, m=Q(51, 10), b=994, xq=60, n=10,
                                         wrongs=["one_low", "one_high", "two_low"])),
    S("1.7", lambda r: interval_change(r, 0, ctx=1, values=MOVIES, x0=2_003, gap=1,
                                       offer=[0, 5, 6, 7])),
    S("1.8", lambda r: fit_equation(r, 0, ctx=0, m=-1, b=6, n=10,
                                    wrongs=["intercept_sign", "swap_intercept_sign",
                                            "swap"])),
    S("1.9", lambda r: curve_read(r, 0, ctx=0, a=Q(1, 16), c=Q(5, 4), x=50, x2=30,
                                  wrongs=["one_low", "one_high", "double"])),
    S("1.10", lambda r: predict_from_line(r, 0, ctx=4, m=Q(400, 7), b=Q(-9_440, 7),
                                          xq=32, n=11, fmt="spr", round_to=10)),
    S("1.11", lambda r: interval_change(r, 0, ctx=2, values=JUNE, x0=1, gap=1,
                                        offer=[0, 1, 4, 5])),
    S("1.12", lambda r: curve_read(r, 0, ctx=1, a=Q(1, 20), c=Q(11, 10), x=55, gap=40,
                                   wrongs=["one_high", "x_value", "half"])),
    S("1.13", lambda r: association(r, 0, ctx=0, n=8, **TAHOE)),
    S("1.14", lambda r: predict_from_line(r, 0, ctx=1, m=Q(-9, 10), b=Q(142, 25),
                                          xq=Q(6, 5), n=7,
                                          wrongs=["two_low", "one_low", "point_high"])),
    S("1.15", lambda r: predict_from_line(r, 0, ctx=2, m=Q(11, 1_200), b=0, xq=1_200,
                                          n=12,
                                          wrongs=["at_end", "x_right", "half_x"]),
      "the source lists the options in descending order"),
    S("1.16", lambda r: point_read(r, 0, ctx=0, xs=WOLVES[0], ys=WOLVES[1], target=3,
                                   wrongs=["above2", "above", "below"]),
      "the source lists the options in descending order"),
    S("1.17", lambda r: point_read(r, 0, ctx=1, xs=NECTARINES[0], ys=NECTARINES[1],
                                   target=3, fmt="spr")),
    S("1.18", lambda r: series_extreme(r, 0, ctx=1, values=CHIPMUNKS, x0=1_989,
                                       ask="most", offer=[0, 5, 6, 9])),

    # ------------------------------------------------------------- medium
    S("2.1", lambda r: residual(r, 0, ctx=0, m=Q(-6, 5), b=12, xs=[0, 1, 2, 3, 4, 5],
                                resid=[-1, 1, 1, -1, 0, 0], j=1,
                                wrongs=["one_high", "point_y", "line_y"])),
    S("2.2", lambda r: fit_slope(r, 0, ctx=0, m=Q(-7, 10), b=8, n=10,
                                 wrongs=["sign_times_ten", "sign", "times_ten"])),
    S("2.3", lambda r: growth_compare(r, 0, base=2, m=2, k=2)),
    S("2.4", lambda r: fit_slope(r, 0, ctx=1, m=Q(-4, 5), b=Q(64, 5), n=10,
                                 wrongs=["sign", "two_down", "sign_two_down"])),
    S("2.5", lambda r: model_type(r, 0, scene=0)),
    S("2.6", lambda r: residual(r, 0, ctx=1, m=Q(7, 5_000), b=Q(803, 10), xs=CHARITY_X,
                                resid=CHARITY_R, j=5,
                                wrongs=["one_high", "one_low", "two_low"]),
      "the source lists the options in descending order"),
    S("2.7", lambda r: fit_equation(r, 0, ctx=1, m=Q(33, 10), b=Q(41, 50), n=20,
                                    wrongs=["swap", "b_twice", "m_twice"])),
    S("2.8", lambda r: fit_equation(r, 0, ctx=2, m=4_680, b=16_090, alt_m=9_060,
                                    year0=1_968, n=13,
                                    wrongs=["swap", "alt_slope", "alt_swap"])),
    S("2.9", lambda r: nonlinear_table(r, 0, xs=[1, 2, 3, 4], ratio=2, start=6,
                                       slopes=[3, 4, 5], bases=[8, 4, 8])),
    S("2.10", lambda r: fit_equation(r, 0, ctx=5, m=3, b=Q(4, 5), n=8,
                                     wrongs=["swap", "swap_sign", "slope_sign"])),
    S("2.11", lambda r: predict_from_line(r, 0, ctx=3, xq=32, n=10,
                                          wrongs=["x_right2", "x_right", "x_left"],
                                          **XY)),
    S("2.12", lambda r: fit_slope(r, 0, ctx=3, m=Q(9, 5), b=0, n=5,
                                  wrongs=["reciprocal", "sign", "two_up"])),
    S("2.13", lambda r: predict_from_line(r, 0, ctx=3, xq=Q(51, 2), n=10,
                                          wrongs=["x_right2", "x_right", "x_left"],
                                          **XY)),

    # --------------------------------------------------------------- hard
    S("3.1", lambda r: interpret_slope(r, 0, ctx=0, m=Q(12, 125), b=Q(-61, 125),
                                       span=70, y0=1_940,
                                       wrongs=["intercept_as_rate", "per_decade_slope",
                                               "per_decade_intercept"])),
    S("3.2", lambda r: fit_equation(r, 0, ctx=3, m=33, b=84, n=12,
                                    wrongs=["slope_reciprocal", "swap", "axis_min"])),
    S("3.3", lambda r: rate_of_change(r, 0, ctx=0, ys=BIRD, i=1, j=3)),
    S("3.4", lambda r: slope_scaled(r, 0, ctx=0, m=57, b=-1_345, k=5, n=11)),
    S("3.5", lambda r: best_model(r, 0, ctx=1, a=Q(-837, 500), b=Q(494, 25),
                                  c=Q(74_573, 100),
                                  wrongs=["ac_sign", "bc_sign", "a_sign"])),
    S("3.6", lambda r: fit_equation(r, 0, ctx=4, m=100, b=100, n=25,
                                    wrongs=["slope_double", "slope_half",
                                            "no_intercept"])),
    S("3.7", lambda r: invest_compare(r, 0, ctx=0, pa=500, rate=Q(3, 50), pb=1_000,
                                      fee=25)),
    S("3.8", lambda r: fit_slope(r, 0, ctx=2, m=Q(54, 35), b=Q(4, 7), n=8, places=1,
                                 wrongs=["two_up", "one_up", "one_down"])),
]


# Every official item is encoded above. Each of the fourteen scatterplots is
# rebuilt from its own line and its own residuals rather than reproduced as a
# fixed picture, so nothing here depends on an image a template cannot vary.
EXCLUDED: dict[str, str] = {}
