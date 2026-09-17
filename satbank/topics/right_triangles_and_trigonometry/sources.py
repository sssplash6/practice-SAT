"""The 33 official Right Triangles and Trigonometry items, as parameters.

Each record pins a template to the source item's own numbers, and names the
three misconceptions College Board printed with it, in printed order. No
answer is written here: the answers live in
`material/keys/right_triangles_and_trigonometry.json`, read from the College
Board PDF's own text layer, and the check asks whether the engine -- driven by
these parameters -- lands on them.
"""

from __future__ import annotations

from ...shapes import UNITS
from ...topic import S, Source
from .families.composite import altitude_special, nested_similar, parallel_similar
from .families.ratios import (cofunction_angles, cofunction_match,
                              complement_ratio, complement_tangent, ratio_to_side,
                              split_right_angle, trig_ratio)
from .families.sides import (equilateral_logo, leg_expression, pythagoras,
                             rectangle_diagonal, special_perimeter, special_triangle)
from .families.similar import similar_ratio, similar_side, similar_sides_ratio
from .kit import Surd

CM, IN, M, FT, U = UNITS
ABC_DEF = (("A", "B", "C"), ("D", "E", "F"))

ALL: list[Source] = [
    # ---------------------------------------------------------------- set 1
    S("1.1", lambda r: pythagoras(r, 0, mode="hypotenuse", a=3, b=7,
                                  approximate=True, places=1, frame="figure",
                                  layout="left", fmt="mcq", note=True,
                                  wrongs=["sqrt_sum", "average", "double_sum"]),
      "the figure carries both legs; the options are printed to one decimal place"),
    S("1.2", lambda r: special_triangle(r, 0, alpha=45, given="p", value=24, ask="q",
                                        layout="right", label="x", mark="both",
                                        fmt="mcq", note=True,
                                        wrongs=["angle_measure", "double",
                                                "sum_with_angle"])),
    S("1.3", lambda r: trig_ratio(r, 0, hyp=73, leg=63, mode="two_sides", fn="sin",
                                  at="p", letter="x", names=False, layout="left",
                                  fmt="mcq", note=True,
                                  wrongs=["unit_leg", "diff_over_hyp",
                                          "sum_over_hyp"])),
    S("1.4", lambda r: similar_ratio(r, 0, given_fn="cos", given_at="B", p=1, q=22,
                                     ask_fn="cos", ask_at="E", names=ABC_DEF,
                                     fmt="mcq",
                                     wrongs=["sum_denominator",
                                             "third_by_subtracting", "swapped_sum"]),
      "B corresponds to E, so the ratio is unchanged; the third side never enters it"),
    S("1.5", lambda r: pythagoras(r, 0, mode="hypotenuse", a=9, b=6, approximate=True,
                                  places=1, frame="figure", layout="left", label="c",
                                  fmt="mcq", note=True,
                                  wrongs=["average", "add", "half_squares"])),

    # ---------------------------------------------------------------- set 2
    S("2.1", lambda r: trig_ratio(r, 0, hyp=29, leg=21, mode="triple", fn="tan",
                                  at="q", names=("C", "B", "A"), layout="right",
                                  fmt="mcq", note=False,
                                  wrongs=["sin", "cos", "reciprocal"])),
    S("2.2", lambda r: leg_expression(r, 0, mode="leg", c=21, a=6, label="a",
                                      layout="right", note=True,
                                      wrongs=["no_root", "no_squares",
                                              "plain_difference"])),
    S("2.3", lambda r: pythagoras(r, 0, mode="hypotenuse", a=28, b=20, frame="text",
                                  unit=CM, fmt="mcq",
                                  wrongs=["difference", "add", "sum_squares"])),
    S("2.4", lambda r: altitude_special(r, 0, alpha=30, gamma=60, side=12, ask="ad",
                                        names=("A", "B", "C"), foot="D", fmt="mcq",
                                        note=False,
                                        wrongs=["ratio_one_two_three", "forty_five",
                                                "altitude"])),
    S("2.5", lambda r: rectangle_diagonal(r, 0, short=5, long=20, ask="long",
                                          fmt="mcq",
                                          wrongs=["divide", "added", "no_root"])),
    S("2.6", lambda r: special_triangle(r, 0, alpha=60, given="hyp", value=8, ask="p",
                                        layout="left", names=("P", "Q", "R"),
                                        mark="q", fmt="spr", note=False),
      "the 30 degree angle is marked at R, so the angle at Q is 60 degrees"),
    S("2.7", lambda r: special_triangle(r, 0, alpha=45, given="p", value=32,
                                        ask="angle_p", layout="right", label="x",
                                        mark="p", fmt="spr", note=True)),
    S("2.8", lambda r: ratio_to_side(r, 0, triple=(3, 4, 5), scale=34, fn="cos",
                                     given="opp", ask="adj", names=("A", "B", "C"),
                                     right=1, at=0, unit=None, fmt="mcq",
                                     wrongs=["hyp_minus_given", "given",
                                             "hypotenuse"])),
    S("2.9", lambda r: cofunction_match(r, 0, leg_p=27, leg_q=35, fn="sin", at="p",
                                        names=("X", "Y", "Z"), right=2,
                                        layout="left", note=True)),

    # ---------------------------------------------------------------- set 3
    S("3.1", lambda r: ratio_to_side(r, 0, triple=(12, 5, 13), scale=2, fn="sin",
                                     given="hyp", ask="adj", names=("A", "B", "C"),
                                     right=2, at=1, figure=True, layout="right",
                                     fmt="spr", note=False)),
    S("3.2", lambda r: trig_ratio(r, 0, hyp=23, leg=16, mode="two_sides", fn="sin",
                                  at="p", letter="x", names=False, layout="left",
                                  fmt="spr", note=True)),
    S("3.3", lambda r: equilateral_logo(r, 0, count=3, perimeter=20, shade="up",
                                        ask="shaded", unit=CM, fmt="mcq",
                                        wrongs=["half_triangle", "one_triangle",
                                                "square"])),
    S("3.4", lambda r: nested_similar(r, 0, triple=(3, 4, 5), scale=3, cut=4,
                                      ask="de", names=("A", "B", "C"), foot="D",
                                      edge="E", fmt="spr", note=False)),
    S("3.5", lambda r: split_right_angle(r, 0, leg_p=12, leg_q=5,
                                         names=("R", "S", "T"), right=1, inner="W",
                                         order="cos_sin", layout="apex", note=False),
      "the ray splits the right angle, so the two pieces are complementary "
      "wherever W lies"),
    S("3.6", lambda r: similar_side(r, 0, tan="√3", leg=125, ask="hyp",
                                    names=ABC_DEF, fmt="mcq",
                                    wrongs=["divided", "times_sine", "other_leg"])),
    S("3.7", lambda r: rectangle_diagonal(r, 0, short=3, long=12, ask="long",
                                          fmt="spr")),
    S("3.8", lambda r: similar_ratio(r, 0, given_fn="tan", given_at="A", p=21, q=20,
                                     ask_fn="sin", ask_at="D", names=ABC_DEF,
                                     scale="2.9", fmt="spr"),
      "the scale factor is a red herring: similar triangles share their angles"),
    S("3.9", lambda r: complement_tangent(r, 0, radical="√3/3", fmt="mcq",
                                          wrongs=["negative", "negative_reciprocal",
                                                  "same"])),
    S("3.10", lambda r: similar_ratio(r, 0, given_fn="tan", given_at="A", p=50, q=7,
                                      ask_fn="tan", ask_at="E", names=ABC_DEF,
                                      fmt="spr")),
    S("3.11", lambda r: parallel_similar(r, 0, base=8, height=6, factor=3, ask="ce",
                                         names=("C", "A", "E"), foot="B", edge="D",
                                         fmt="spr", note=False)),
    S("3.12", lambda r: special_perimeter(r, 0, shape="thirty_sixty",
                                          given="perimeter",
                                          value=Surd.of(18, 6, 3), ask="hyp",
                                          superlative=True, frame="has", fmt="spr")),
    S("3.13", lambda r: special_perimeter(r, 0, shape="isosceles", given="perimeter",
                                          value=Surd.of(94, 94, 2), ask="leg",
                                          unit=IN, frame="has", fmt="mcq",
                                          wrongs=["half_hyp", "hyp", "double_leg"])),
    S("3.14", lambda r: complement_ratio(r, 0, triple=(8, 15, 17), scale=3, fn="cos",
                                         ask="cos", names=("J", "K", "L"),
                                         fmt="spr"),
      "24/51 is printed unreduced; the answer 15/17 is the reduced complement"),
    S("3.15", lambda r: similar_sides_ratio(r, 0, triple=(55, 48, 73), scale=8,
                                            ask_fn="tan", ask_at="W",
                                            names=(("S", "R", "T"),
                                                   ("V", "U", "W")), fmt="mcq",
                                            wrongs=["sin", "cos", "reciprocal"])),
    S("3.16", lambda r: special_perimeter(r, 0, shape="isosceles", given="hyp",
                                          value=Surd.of(58), ask="perimeter",
                                          unit=IN, frame="has", fmt="mcq",
                                          wrongs=["leg", "double_leg",
                                                  "legs_as_hyp"])),
    S("3.17", lambda r: cofunction_angles(r, 0, m1=1, b1=61, m2=4, b2=4,
                                          names=("Q", "R"), fn="cos_sin", fmt="mcq",
                                          wrongs=["set_equal", "supplementary",
                                                  "first_right"])),
    S("3.18", lambda r: trig_ratio(r, 0, hyp=53, leg=52, mode="third_side", fn="sin",
                                   at="p", names=("S", "R", "T"), layout="right",
                                   fmt="spr", note=True)),
    S("3.19", lambda r: special_perimeter(r, 0, shape="isosceles", given="perimeter",
                                          value=Surd.of(18, 18, 2), ask="hyp",
                                          unit=IN, frame="is", fmt="mcq",
                                          wrongs=["half_hyp", "leg", "double_leg"])),
]


# Source items no template reproduces, and why. Every id in the answer key must
# appear either above or here; `satbank check` counts them.
EXCLUDED: dict[str, str] = {}
