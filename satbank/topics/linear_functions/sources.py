"""The 86 official Linear Functions items, encoded as the parameters that
reproduce them.

Each record pins a template to the source item's own numbers -- and, where the
item writer's choice of distractors is itself an axis, to its own `wrong`
family. No answer is written here: the answer lives in
`material/keys/linear_functions.json`, read from the College Board PDF's own
text layer, and the check asks whether the engine lands on it.
"""

from __future__ import annotations

from fractions import Fraction as F

from ...topic import S, Source
from .families.basic import coefficient, combine, evaluate, inner_scale
from .families.context import (context_two_points, model_equation, model_value,
                               per_unit_model, tiered_cost)
from .families.define import (define_line, from_points, from_table, table_facts,
                              x_intercept, y_intercept)
from .families.graph import graph_read, graph_shifted
from .families.interpret import (interpret_constant, interpret_slope,
                                 interpret_x_intercept)
from .families.symbolic import affine_conversion, parameter_intercept, unit_relation

WATER = ("The buildings of a shopping center are designed to allow water to drain from "
         "the roof into gutters on the sides of the buildings. The table shows the "
         "relationship between the area x, in square feet, of a roof and the amount of "
         "water f(x), in gallons, drained from the roof into the gutters over a certain "
         "period of time. Which equation could define f?")
CARLY = ("The table gives the average time t, in minutes, it takes Carly to travel a "
         "certain distance d, in kilometers. Which equation could represent this linear "
         "relationship?")

ALL: list[Source] = [
    # ------------------------------------------------------------------ easy
    S("1.1", lambda r: model_equation(r, 0, kind="model", ctx=0, b=15, m=8)),
    S("1.2", lambda r: evaluate(r, 0, form="quotient", a=2, c=-1, d=3, x0=5, name="f",
                                frame="if_defined", fmt="mcq")),
    S("1.3", lambda r: interpret_slope(r, 0, ctx=0, m=16)),
    S("1.4", lambda r: evaluate(r, 0, m=-1, b=8, x0=0, name="g", frame="defined_by",
                                wrong="given", fmt="mcq")),
    S("1.5", lambda r: graph_read(r, 0, ctx=2, m=2, b=3)),
    S("1.6", lambda r: graph_read(r, 0, ctx=3, m=40)),
    S("1.7", lambda r: from_table(r, 0, mode="affine", m=4, b=1, xs=[1, 3, 5], name="f",
                                  var="x", frame=0, wrong_style="fit_first")),
    S("1.8", lambda r: evaluate(r, 0, m=3, b=-7, x0=-2, name="h", frame="defined_by",
                                wrong="sign", fmt="mcq")),
    S("1.9", lambda r: interpret_slope(r, 0, ctx=1, m=45)),
    S("1.10", lambda r: model_value(r, 0, direction="inverse", ctx=0, b=1000, m=18, x=32,
                                    fmt="mcq")),
    S("1.11", lambda r: coefficient(r, 0, unknown="b", ask="unknown", m=5, x1=4, b=11,
                                    name="g", fmt="mcq"),
      "source lists the options descending"),
    S("1.12", lambda r: evaluate(r, 0, m=100, b=2, x0=9, name="f", frame="equation_when",
                                 wrong="structural", fmt="mcq")),
    S("1.13", lambda r: model_equation(r, 0, kind="model", ctx=1, b=F(925, 100),
                                       m=F(50, 100))),
    S("1.14", lambda r: model_equation(r, 0, kind="model", ctx=2, b=162, m=F(48, 10))),
    S("1.15", lambda r: evaluate(r, 0, m=1, b=200, x0=50, name="h", frame="defined_by",
                                 wrong="given", fmt="mcq")),
    S("1.16", lambda r: define_line(r, 0, given="slope_intercept", phrase="slope_f0",
                                    m=F(3, 4), b=3, name="f")),
    S("1.17", lambda r: graph_read(r, 0, ctx=0, m=100, b=100, x=6)),
    S("1.18", lambda r: model_value(r, 0, ctx=0, b=20, m=F(70, 100), x=38, fmt="mcq")),
    S("1.19", lambda r: interpret_constant(r, 0, mode="point", ctx=0, b=250, m=10,
                                           y0=1990, t=30)),
    S("1.21", lambda r: define_line(r, 0, given="two_values", phrase="for_the", m=0, b=17,
                                    name="f")),
    S("1.22", lambda r: graph_read(r, 0, ctx=1, m=F(7, 500), x=500)),
    S("1.23", lambda r: y_intercept(r, 0, given="graph", m=F(2, 5), b=2, name="f")),
    S("1.24", lambda r: model_equation(r, 0, kind="model", ctx=3, b=120, m=60)),
    S("1.25", lambda r: evaluate(r, 0, form="constant_first", b=80, m=-6, x0=7, name="f",
                                 frame="defined_by", fmt="mcq")),
    S("1.26", lambda r: define_line(r, 0, given="slope_intercept", phrase="y_intercept_at",
                                    m=2, b=-5, name="f")),
    S("1.27", lambda r: interpret_constant(r, 0, mode="start", ctx=0, b=33,
                                           m=F(18, 100))),
    S("1.28", lambda r: model_value(r, 0, ctx=1, b=600, m=35, x=4, fmt="mcq")),
    S("1.29", lambda r: define_line(r, 0, given="two_values", phrase="in_the", m=-1, b=41,
                                    name="h")),
    S("1.30", lambda r: evaluate(r, 0, m=10, b=8, x0=8, name="g", frame="when_defined_by",
                                 wrong="given", fmt="mcq")),
    S("1.31", lambda r: model_equation(r, 0, kind="verbal", ctx=0, b=84)),
    S("1.32", lambda r: from_table(r, 0, mode="affine", m=3, b=29, xs=[0, 1, 2], name="f",
                                   var="x", frame=1, wrong_style="outputs")),
    S("1.33", lambda r: evaluate(r, 0, m=5, b=10, x0=8, frame="bare_y", fmt="spr")),
    S("1.34", lambda r: model_equation(r, 0, kind="rate", ctx=0, m=F(57, 10))),
    S("1.35", lambda r: define_line(r, 0, given="slope_intercept", phrase="passes_through",
                                    m=F(1, 4), b=5, name="f")),
    S("1.36", lambda r: from_table(r, 0, mode="proportional", m=F(9, 5),
                                   xs=[2520, 3780, 5040], cell="frac", coef="dec",
                                   dep="f(x)", var="x", context=WATER,
                                   labels=["Area (square feet)", "Water (gallons)"],
                                   wrong_style="outputs")),
    S("1.37", lambda r: interpret_constant(r, 0, mode="start", ctx=1, b=39,
                                           m=F(18, 100))),
    S("1.38", lambda r: evaluate(r, 0, m=1, b=F(8, 11), x0=F(3, 11), name="f",
                                 frame="given_equation", fmt="spr")),
    S("1.39", lambda r: evaluate(r, 0, m=F(7, 10), b=55, x0=20, name="f",
                                 frame="defined_by", fmt="spr")),

    # ---------------------------------------------------------------- medium
    S("2.1", lambda r: model_value(r, 0, ctx=2, b=F(6, 10), m=4, x=F(5, 10), fmt="spr")),
    S("2.2", lambda r: from_points(r, 0, x1=0, y1=3, x2=7, y2=31, name="f", frame=0)),
    S("2.3", lambda r: interpret_x_intercept(r, 0, ctx=0, b=120, m=25)),
    S("2.4", lambda r: interpret_slope(r, 0, ctx=3, m=25, b=100)),
    S("2.5", lambda r: per_unit_model(r, 0, shape="offset", ctx=0, c=212, n=550)),
    S("2.6", lambda r: combine(r, 0, mode="same_function", c=7, d=4, p=9, qv=1)),
    S("2.7", lambda r: table_facts(r, 0, ask="value", m=3, b=-2, xs=[0, 2, 6], x_ask=3,
                                   name="f", fmt="mcq")),
    S("2.8", lambda r: from_points(r, 0, x1=-2, y1=3, x2=4, y2=-5, name="f", frame=1)),
    S("2.9", lambda r: graph_read(r, 0, ctx=4, m=2)),
    S("2.10", lambda r: coefficient(r, 0, unknown="m", ask="value", m=3, b=500, x1=100,
                                    x2=1000, name="c", fmt="spr")),
    S("2.11", lambda r: context_two_points(r, 0, ask="predict", ctx=0, x1=1991, x2=2011,
                                           x3=2015, y1=57, y2=224, fmt="spr")),
    S("2.12", lambda r: coefficient(r, 0, unknown="m", ask="value", m=F(-21, 2), b=144,
                                    x1=12, x2=10, name="j", fmt="spr")),
    S("2.13", lambda r: unit_relation(r, 0, mode="ratio", cal=4, fat=9)),
    S("2.14", lambda r: combine(r, 0, mode="two_functions", c=7, d=7, p=2, af=4, bg=1)),
    S("2.15", lambda r: interpret_x_intercept(r, 0, ctx=1, b=18, m=5)),
    S("2.16", lambda r: model_value(r, 0, ctx=3, b=F(26, 10), m=F(67, 100), x=58,
                                    fmt="mcq")),
    S("2.17", lambda r: coefficient(r, 0, unknown="m", ask="unknown", b_given="two_values",
                                    m=2, b=18, x1=1, name="f", fmt="spr")),
    S("2.18", lambda r: context_two_points(r, 0, ask="model", model_ctx=0, x1=2000,
                                           x2=2010, y1=862, y2=846)),
    S("2.19", lambda r: model_value(r, 0, ctx=4, b=F(1470, 100), m=F(44, 100), x=105,
                                    fmt="mcq"), "source lists the options descending"),
    S("2.20", lambda r: graph_shifted(r, 0, m=-2, c=-4, k=11, name="f")),
    S("2.21", lambda r: model_value(r, 0, ctx=5, b=F(5520, 100), m=F(16, 100), x=326,
                                    fmt="mcq"), "source lists the options descending"),
    S("2.22", lambda r: interpret_slope(r, 0, ctx=4, m=85, b=45)),
    S("2.23", lambda r: define_line(r, 0, given="two_values", phrase="in_the", m=4, b=8,
                                    name="f")),
    S("2.24", lambda r: from_points(r, 0, x1=0, y1=2, x2=8, y2=34, name="f", frame=0)),
    S("2.25", lambda r: table_facts(r, 0, ask="intercept", m=-3, b=57, xs=[1, 2, 3, 4],
                                    name="g", fmt="mcq")),
    S("2.26", lambda r: y_intercept(r, 0, given="equation", m=-9, b=9, name="f",
                                    fmt="spr")),
    S("2.27", lambda r: from_table(r, 0, mode="proportional", m=25,
                                   xs=[F(32, 100), F(56, 100), F(68, 100)], cell="dec",
                                   coef="frac", var="d", dep="t", context=CARLY,
                                   labels=["Distance (kilometers)",
                                           "Average time (minutes)"],
                                   wrong_style="inverted")),
    S("2.28", lambda r: x_intercept(r, 0, given="slope_intercept", m=5, b=-35,
                                    fmt="spr")),

    # ------------------------------------------------------------------ hard
    S("3.1", lambda r: context_two_points(r, 0, ask="predict", ctx=1, x1=40, x2=60, x3=55,
                                          y1=20000, y2=15000, fmt="mcq")),
    S("3.2", lambda r: tiered_cost(r, 0, ctx=0, a=270, b=135)),
    S("3.3", lambda r: x_intercept(r, 0, given="sum", m=F(1, 4), b=-9, m2=F(3, 4), b2=21,
                                   fmt="spr")),
    S("3.4", lambda r: interpret_constant(r, 0, mode="shifted", ctx=0, b=F(274, 100),
                                          m=F(19, 100), k=3)),
    S("3.5", lambda r: context_two_points(r, 0, ask="model", model_ctx=1, x1=2000,
                                          x2=2013, y1=4, y2=F(19, 10))),
    S("3.6", lambda r: affine_conversion(r, 0, ask="change", delta=F(210, 100),
                                         fmt="mcq")),
    S("3.7", lambda r: x_intercept(r, 0, given="table", m=-3, b=-12, x0=-11, step=1,
                                   rows=4, name="f", fmt="mcq")),
    S("3.8", lambda r: unit_relation(r, 0, mode="solve", cal=4, fat=9, total=180)),
    S("3.9", lambda r: interpret_slope(r, 0, ctx=2, m=2, b=30)),
    S("3.10", lambda r: inner_scale(r, 0, ask="value", c=3, d=-6, k=6, fmt="mcq")),
    S("3.11", lambda r: table_facts(r, 0, ask="a_minus_b", m=64, b=-128, xs=[1, 2, 3],
                                    name="f", fmt="mcq")),
    S("3.12", lambda r: tiered_cost(r, 0, ctx=2, a=21, b=14, k=25)),
    S("3.13", lambda r: affine_conversion(r, 0, ask="change", delta=F(910, 100),
                                          fmt="mcq")),
    S("3.14", lambda r: parameter_intercept(r, 0, c=6, a=20, b=21, e=17, k=9,
                                            letter="d")),
    S("3.15", lambda r: per_unit_model(r, 0, shape="scaled", ctx=0, n=220, k=2)),
    S("3.16", lambda r: affine_conversion(r, 0, ask="inverse", target=F(46733, 100),
                                          fmt="spr")),
    S("3.17", lambda r: tiered_cost(r, 0, ctx=1, a=430, b=215)),
    S("3.18", lambda r: inner_scale(r, 0, ask="constant", d=-8, k=2, value=35,
                                    fmt="spr")),
    S("3.19", lambda r: table_facts(r, 0, ask="value", frame="point", m=5, b=15,
                                    xs=[-12, 6], x_ask=F(1, 4), fmt="spr",
                                    labels=["x", "y"])),
]


# Source items no template reproduces, and why.
EXCLUDED: dict[str, str] = {
    "1.20": "the four options are themselves coordinate grids, so the item asks the "
            "student to match a drawn line rather than to apply a rule; a template that "
            "generated four pictures would have to vary the three wrong pictures as well "
            "as the right one, and nothing in the item's text can carry the answer",
}
