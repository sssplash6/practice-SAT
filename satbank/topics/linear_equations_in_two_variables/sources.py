"""The 81 official Linear Equations in Two Variables items, encoded as the
parameters that reproduce them.

Each record pins a template to the source item's own numbers -- and, where the
item writer's choice of distractors is itself an axis, to its own `wrongs`
family, because for an interpretation item the wrong answers are the item. No
answer is written here: the answer lives in
`material/keys/linear_equations_in_two_variables.json`, read from the College
Board PDF's own text layer, and the check asks whether the engine lands on it.
"""

from __future__ import annotations

from fractions import Fraction as F

from ...topic import S, Source
from .families.graphs import graph_combinations, line_from_graph
from .families.interpret import (interpret_coefficient, interpret_constant,
                                 interpret_point)
from .families.lines import (equivalent_system, intercepts, line_equation,
                             parallel_perpendicular, point_on_line, slope_of_line,
                             slope_two_points)
from .families.model import material_table, model_percent, model_standard
from .families.solve import context_substitute, mixture_solve, substitute
from .families.tables import table_equation, table_line, table_symbolic, which_table

ROCKS4 = [0, 1, 2, 3]            # Basalt, Granite, Limestone, Sandstone

ALL: list[Source] = [
    # ------------------------------------------------------------------ easy
    S("1.1", lambda r: interpret_coefficient(r, 0, ctx=0, a=F(548, 100), b=F(730, 100),
                                             c=F(127794, 100))),
    S("1.2", lambda r: parallel_perpendicular(r, 0, form="slope_intercept",
                                              relation="perpendicular", m=3, b=15,
                                              given="k", other="j",
                                              wrongs=["diff", "sum", "product"])),
    S("1.3", lambda r: substitute(r, 0, ctx=0, a=3, b=4, given=3, other=4)),
    S("1.4", lambda r: interpret_constant(r, 0, ctx=0, c=75)),
    S("1.5", lambda r: interpret_point(r, 0, mode="pair", a=3, b=4, px=24, py=73)),
    S("1.6", lambda r: substitute(r, 0, ctx=1, a=F(1, 10), given=30)),
    S("1.7", lambda r: line_from_graph(r, 0, ask="equation", m=F(-1, 4), b=-1,
                                       wrongs=["invm", "swapinv", "swap"])),
    S("1.8", lambda r: model_standard(r, 0, ctx=0, a=F(15, 10), b=F(19, 10),
                                      c=F(461, 10))),
    S("1.9", lambda r: graph_combinations(r, 0, ctx=0, xi=9, yi=18, total=18, x=4)),
    S("1.10", lambda r: model_standard(r, 0, ctx=5, c=201)),
    S("1.11", lambda r: interpret_constant(r, 0, ctx=1, a=4, b=3, c=24)),
    S("1.12", lambda r: model_percent(r, 0, ctx=0, pa=60, pb=40, c=240)),
    S("1.13", lambda r: line_equation(r, 0, frame=0, m=6, b=8,
                                      wrongs=["product", "swap", "swapproduct"])),
    S("1.14", lambda r: substitute(r, 0, ctx=2, a=40, b=20, given=2, other=4)),
    S("1.15", lambda r: model_standard(r, 0, ctx=1, a=F(1250, 100), b=F(150, 100),
                                       c=80)),
    S("1.16", lambda r: material_table(r, 0, ask="interpret", picks=ROCKS4, xi=2, yi=0,
                                       part=F(338580, 100), total=F(757620, 100))),
    S("1.17", lambda r: table_equation(r, 0, form="slope_intercept", m=2, b=3, x0=1,
                                       step=1, rows=4)),
    S("1.18", lambda r: context_substitute(r, 0, ctx=0, a=5, b=10, given=13, other=18)),
    S("1.19", lambda r: which_table(r, 0, form="slope_intercept", m=70, b=8,
                                    xs=[0, 2, 4])),
    S("1.20", lambda r: interpret_coefficient(r, 0, ctx=1, a=F(250, 100), b=F(700, 100),
                                              c=200)),
    S("1.21", lambda r: intercepts(r, 0, mode="graph_point", m=F(1, 5), b=8)),
    S("1.22", lambda r: substitute(r, 0, ctx=3, given=9, other=14)),
    S("1.23", lambda r: intercepts(r, 0, mode="equation_y", m=-6, b=-32)),
    S("1.24", lambda r: model_percent(r, 0, ctx=2, pa=53, pb=44, pm=49, volume=35,
                                      y0=2010, y1=2020)),
    S("1.25", lambda r: line_from_graph(r, 0, ask="equation", m=-3, b=3,
                                        wrongs=["negboth", "inv_negboth", "invm"])),
    S("1.26", lambda r: context_substitute(r, 0, ctx=4, a=F(69, 100), b=F(99, 100),
                                           times=2, other=2)),
    S("1.27", lambda r: context_substitute(r, 0, ctx=1, a=8, b=6, given=2, other=5)),
    S("1.28", lambda r: line_equation(r, 0, frame=1, m=F(-1, 2), b=3,
                                      wrongs=["negb", "negm", "negboth"])),
    S("1.29", lambda r: substitute(r, 0, ctx=4, given=8, other=15)),
    S("1.30", lambda r: model_standard(r, 0, ctx=2, a=F(4, 100), b=F(48, 100),
                                       c=F(66176, 100))),
    S("1.31", lambda r: model_standard(r, 0, ctx=3, a=1, b=3, c=70)),
    S("1.32", lambda r: substitute(r, 0, ctx=5, given=245, other=105, acres=14)),
    S("1.33", lambda r: which_table(r, 0, form="standard", A=7, B=-4, C=-84,
                                    xs=[0, 4, 8])),
    S("1.34", lambda r: model_percent(r, 0, ctx=1, pa=2, pb=96, pm=4, volume=24)),

    # ---------------------------------------------------------------- medium
    S("2.1", lambda r: parallel_perpendicular(r, 0, form="slope_intercept",
                                              relation="perpendicular", m=F(-17, 3),
                                              b=5, given="k", other="j", fmt="spr")),
    S("2.2", lambda r: context_substitute(r, 0, ctx=2, a=50, b=60, given=1, other=3)),
    S("2.3", lambda r: table_equation(r, 0, form="context", m=F(10, 3), b=-2, x0=3,
                                      step=3, rows=3)),
    S("2.4", lambda r: context_substitute(r, 0, ctx=3, a=200, b=150, given=1, other=4)),
    S("2.5", lambda r: slope_two_points(r, 0, given="intercepts", x1=-4, y2=F(86, 3),
                                        name="n", fmt="mcq")),
    S("2.6", lambda r: line_equation(r, 0, frame=2, b=-5, x2=1, y2=-1, name="k")),
    S("2.7", lambda r: material_table(r, 0, ask="equation", picks=ROCKS4, zi=1, xi=2,
                                      yi=0, total=1000, known=330)),
    S("2.8", lambda r: interpret_coefficient(r, 0, ctx=2, a=3, b=6, c=63)),
    S("2.9", lambda r: table_symbolic(r, 0, ask="slope", step=3, d=92)),
    S("2.10", lambda r: slope_of_line(r, 0, form="grouped", p=27, d=4, r=15, s=7)),
    S("2.11", lambda r: slope_two_points(r, 0, given="points", x1=4, y1=6, x2=15, y2=24,
                                         fmt="spr")),
    S("2.12", lambda r: interpret_constant(r, 0, ctx=2, c=37)),
    S("2.13", lambda r: slope_of_line(r, 0, form="fraction", p=5, d=13, c=-23)),
    S("2.14", lambda r: model_standard(r, 0, ctx=4, poly1=1, poly2=0, n1=2, n2=6,
                                       c=210)),
    S("2.15", lambda r: substitute(r, 0, ctx=6, a=F(25, 10), b=5, given=16, other=0)),
    S("2.16", lambda r: line_from_graph(r, 0, ask="equation", m=-1, b=-8,
                                        wrongs=["double", "negm", "neg_double"])),
    S("2.17", lambda r: graph_combinations(r, 0, ctx=1, xi=90, yi=35)),
    S("2.18", lambda r: parallel_perpendicular(r, 0, form="standard",
                                               relation="parallel", A=4, B=-9, C=3,
                                               layout="xy", given="r", other="s",
                                               wrongs=["invm", "negcoefx", "coefy"])),
    S("2.19", lambda r: context_substitute(r, 0, ctx=5, n1=4, n2=2, u1=276, u2=5)),
    S("2.20", lambda r: interpret_constant(r, 0, ctx=3, a=4, b=6, c=36)),
    S("2.21", lambda r: table_equation(r, 0, form="standard", m=-3, b=47, x0=-6, step=3,
                                       rows=4, scale=3)),
    S("2.22", lambda r: substitute(r, 0, ctx=7, given=71, other=49)),
    S("2.23", lambda r: interpret_coefficient(r, 0, ctx=3, a=5, b=24, c=4529)),
    S("2.24", lambda r: interpret_coefficient(r, 0, ctx=4, a=F(245, 10), b=F(2475, 100),
                                              c=641)),
    S("2.25", lambda r: interpret_point(r, 0, mode="graph", px=8, perimeter=36)),

    # ------------------------------------------------------------------ hard
    S("3.1", lambda r: point_on_line(r, 0, ask="constant", c=6, x1=-2, y1=-6, y2=-3)),
    S("3.2", lambda r: point_on_line(r, 0, ask="coordinate", mode="two_points", b=-6,
                                     x1=2, y1=2, x3=20, name="k")),
    S("3.4", lambda r: graph_combinations(r, 0, ctx=3, xi=16, yi=12, total=24)),
    S("3.5", lambda r: parallel_perpendicular(r, 0, form="axis",
                                              relation="perpendicular", c=2,
                                              first=True)),
    S("3.6", lambda r: table_symbolic(r, 0, ask="constants", m=2, x1=3, y1=7, y2=11,
                                      x3=12)),
    S("3.7", lambda r: graph_combinations(r, 0, ctx=2, xi=16, yi=8, total=10)),
    S("3.8", lambda r: intercepts(r, 0, mode="standard_x", A=F(4, 5), B=F(1, 3), C=1)),
    S("3.9", lambda r: parallel_perpendicular(r, 0, form="standard",
                                              relation="perpendicular", ask="equation",
                                              A=1, B=1, C=0, b=3, layout="xy",
                                              given="k", other="j")),
    S("3.10", lambda r: mixture_solve(r, 0, p1=25, p2=10, pm=15, volume=3)),
    S("3.11", lambda r: table_line(r, 0, ask="value", m=4, b=24, x1=-18, x2=7,
                                   x3=F(1, 7))),
    S("3.12", lambda r: line_from_graph(r, 0, ask="parameter", c=2, b=6, scale=6)),
    S("3.13", lambda r: parallel_perpendicular(r, 0, form="standard_zero",
                                               relation="perpendicular", A=F(1, 5),
                                               B=F(1, 7), C=70, given="h", other="j",
                                               wrongs=["same", "negm", "invm"])),
    S("3.14", lambda r: which_table(r, 0, form="standard", A=F(3, 5), B=F(3, 4), C=7,
                                    xs=[1, 2, 4])),
    S("3.15", lambda r: table_line(r, 0, ask="shift_intercept", m=6, b=22,
                                   xs=[18, 23, 26], k=5)),
    S("3.16", lambda r: interpret_coefficient(r, 0, ctx=5, a=5, b=45, c=380)),
    S("3.17", lambda r: point_on_line(r, 0, ask="coordinate", mode="parallel", m=8, c=2,
                                      x3=3)),
    S("3.18", lambda r: intercepts(r, 0, mode="ratio", A=7, B=2, C=-31)),
    S("3.19", lambda r: line_from_graph(r, 0, ask="shifted", m=F(-1, 4), b=2, k=14,
                                        name="f")),
    S("3.20", lambda r: equivalent_system(r, 0, a=2, b=3, c=7, k=5)),
    S("3.21", lambda r: parallel_perpendicular(r, 0, form="standard",
                                               relation="perpendicular", A=8, B=4, C=6,
                                               layout="yx", given="p", other="r",
                                               fmt="spr")),
    S("3.22", lambda r: slope_two_points(r, 0, given="graph", ask="perpendicular",
                                         x1=-6, y1=0, x2=0, y2=-5, name="k",
                                         fmt="spr")),
]


# Source items no template reproduces, and why.
EXCLUDED: dict[str, str] = {
    "3.3": "the four options are themselves coordinate grids, so the item asks the "
           "student to match a drawn line against four pictures rather than to apply a "
           "rule; the options differ only in the steepness and the sign of a slope that "
           "is never written down, and nothing in the item's text can carry the answer",
}
