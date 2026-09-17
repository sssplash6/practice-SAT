"""The 48 official Lines, Angles and Triangles items, as parameters.

Each record pins a template to the source item's own numbers, its own point
labels and -- through `wrongs` -- the three misconceptions College Board
actually printed, in the order they were printed. No answer is written here:
the answers live in `material/keys/lines_angles_and_triangles.json`, read from
the College Board PDF's own text layer, and the check asks whether the engine,
driven by these parameters, lands on them.
"""

from __future__ import annotations

from fractions import Fraction as Q

from ...exact import E
from ...topic import S, Source
from .families.parallels import (big_chain, eight_angles, midsegment_angle,
                                 parallel_triangle, perp_transversal,
                                 three_lines_point, three_lines_triangle,
                                 transversal, transversal_inequality,
                                 transversal_proof, two_transversals)
from .families.similar import (altitude_legs, area_range, geometric_mean,
                               parallel_cut_area, parallel_segments, ratio_match,
                               shadow, similar_angle, similar_needed,
                               similar_side, similar_sufficient, vertical_similar)
from .families.triangles import (angle_algebra, crossing_triangles, exterior_angle,
                                 isosceles, isosceles_cross, isosceles_possible,
                                 triangle_sum, vertical_isosceles)

UPPER, LOWER = "upper", "lower"

ALL: list[Source] = [
    # ------------------------------------------------------------- set 1
    S("1.1", lambda r: isosceles(r, 0, mode="base", base=67, names=("A", "B", "C")),
      "the three printed distractors are near-misses around 46 rather than the "
      "supplement or the double, so the pool's own order is used"),
    S("1.2", lambda r: parallel_triangle(r, 0, y=20, z=60, labels=("ℓ", "m"),
                                         wrongs=["supp_z", "right", "sum"])),
    S("1.3", lambda r: triangle_sum(r, 0, frame="plain", names=("X", "Y", "Z"),
                                    ask=2, a=24, b=98, style="symbol", unit=True,
                                    wrongs=["diff", "sum", "sum_right"])),
    S("1.4", lambda r: transversal(r, 0, given=134,
                                   given_spot=(UPPER, "below", "left"),
                                   ask_spot=(LOWER, "below", "left"),
                                   labels=("m", "n"), cutter="t", unknown="w",
                                   wrongs=["lead2", "drop100", "from200"]),
      "the printed distractors are all miscopyings of 134 rather than angle work"),
    S("1.5", lambda r: shadow(r, 0, story="monument", h1=555, s1=300, s2=16,
                              closest=True, step=5,
                              tall=("the Washington Monument in Washington, DC",
                                    "the Washington Monument"),
                              short=("a nearby cherry tree", "the cherry tree"),
                              wrongs=["swap", "shadow_ratio", "height_over_shadow"])),
    S("1.6", lambda r: crossing_triangles(r, 0, a=20, x=100, e=40,
                                          wrongs=["given_x", "vertical", "sum_ax"])),
    S("1.7", lambda r: angle_algebra(r, 0, c=31, mult=2, a=45,
                                     wrongs=["unreduced", "right_c", "sum_given"])),
    S("1.8", lambda r: three_lines_point(r, 0, x=65, y=75, labels="P",
                                         wrongs=["sum", "leftover", "half"])),
    S("1.9", lambda r: transversal(r, 0, given=64,
                                   given_spot=(LOWER, "above", "right"),
                                   ask_spot=(UPPER, "above", "left"),
                                   labels=("ℓ", "k"), cutter="j", unknown="a",
                                   wrongs=["supplement", "complement", "plus90"])),
    S("1.10", lambda r: isosceles(r, 0, mode="exterior", ext=110,
                                  names=("A", "B", "C"), point="D",
                                  wrongs=["ext_itself", "base", "half_ext"])),
    S("1.11", lambda r: perp_transversal(r, 0, given=130, labels=("m", "n"),
                                         wrongs=["a_itself", "half_given", "apex"])),
    S("1.12", lambda r: triangle_sum(r, 0, frame="right", a=51,
                                     wrongs=["same", "hundred", "iso45"])),
    S("1.13", lambda r: exterior_angle(r, 0, mode="extended", p=70, q=50,
                                       wrongs=["supp_left", "supp_right",
                                               "double_big"])),
    S("1.14", lambda r: triangle_sum(r, 0, frame="right_figure", a=13,
                                     wrongs=["same", "right", "sum"])),
    S("1.15", lambda r: triangle_sum(r, 0, frame="plain", names=("A", "B", "C"),
                                     ask=0, a=52, b=17, style="word", unit=True,
                                     wrongs=["diff", "sum", "right_rest"])),
    S("1.16", lambda r: transversal(r, 0, given=133,
                                    given_spot=(UPPER, "below", "right"),
                                    ask_spot=(UPPER, "below", "left"),
                                    labels=("j", "k"), cutter="t", unknown="x",
                                    fmt="spr")),
    S("1.17", lambda r: transversal(r, 0, given=170,
                                    given_spot=(UPPER, "below", "left"),
                                    ask_spot=(LOWER, "below", "left"),
                                    labels=("m", "n"), cutter="t", unknown="w",
                                    wrongs=["lead2", "drop100", "from200"]),
      "a 170 degree angle cannot be drawn to scale between two parallel lines, so "
      "this one figure carries the source's own 'not drawn to scale' note"),
    S("1.18", lambda r: similar_angle(r, 0, mode="dilate", angle=60, k=3, side=16,
                                      shape=70, names=("A", "B", "C"),
                                      partner=("X", "Y", "Z"),
                                      wrongs=["divide", "sub", "add"])),
    S("1.19", lambda r: transversal_proof(r, 0, given=40, labels=("j", "k"),
                                          cutter="ℓ")),

    # ------------------------------------------------------------- set 2
    S("2.1", lambda r: parallel_segments(r, 0, ab=9, bc=Q(37, 2), fe=Q(17, 2),
                                         wrongs=["swapped", "inverted", "added"]),
      "two of the three printed distractors are near-misses either side of 17.5"),
    S("2.2", lambda r: shadow(r, 0, story="trees", h1=10, s1=5, s2=2,
                              wrongs=["diff_shadows", "height_minus_shadow",
                                      "invert_ratio"])),
    S("2.3", lambda r: ratio_match(r, 0, a=32, names=("A", "B", "C"),
                                   partner=("D", "E", "F"))),
    S("2.4", lambda r: transversal_inequality(r, 0, bound=65, labels=("r", "s"),
                                              cutter="m", names=("x", "y"))),
    S("2.5", lambda r: similar_side(r, 0, side=16, k=2, names=("A", "B", "C"),
                                    partner=("X", "Y", "Z"),
                                    wrongs=["sub", "same", "add"])),
    S("2.6", lambda r: triangle_sum(r, 0, frame="equal", names=("J", "K", "L"),
                                    ask=0, a=48, style="symbol", fmt="spr",
                                    note="enter")),
    S("2.7", lambda r: isosceles_possible(r, 0, a=50, names=("A", "B", "C"))),
    S("2.8", lambda r: similar_angle(r, 0, mode="ratio", angle=20, k=3, shape=110,
                                     names=("A", "B", "C"), partner=("D", "E", "F"),
                                     fmt="spr", note="grid")),
    S("2.9", lambda r: midsegment_angle(r, 0, d=58, c=62,
                                        wrongs=["given_d", "given_c", "sum"])),
    S("2.10", lambda r: triangle_sum(r, 0, frame="congruent", names=("A", "B", "C"),
                                     partner=("D", "E", "F"), a=69, fmt="spr")),
    S("2.11", lambda r: exterior_angle(r, 0, mode="extend_base", inner=132, ext=163,
                                       names=("P", "Q", "R"), extra_label="S",
                                       unit=True,
                                       wrongs=["supp_q", "inner_r", "iso_half"])),
    S("2.12", lambda r: similar_needed(r, 0, a=47, b=97, names=("D", "E", "F"),
                                       partner=("R", "S", "T"))),
    S("2.13", lambda r: similar_angle(r, 0, mode="expr", angle=57, k=26)),

    # ------------------------------------------------------------- set 3
    S("3.1", lambda r: isosceles_cross(r, 0, labels=("B", "C", "D", "A", "E"),
                                       s=45, t=104, ask="v", in_stem=True,
                                       fmt="spr", flip=True)),
    S("3.2", lambda r: big_chain(r, 0, at_q=48, at_x=86, at_w=85, at_t=162,
                                 fmt="spr")),
    S("3.3", lambda r: three_lines_triangle(r, 0, p=106, q=23, fmt="spr")),
    S("3.4", lambda r: vertical_isosceles(r, 0, apex=60, extra=70,
                                          labels=("M", "N", "Q", "R", "P"))),
    S("3.5", lambda r: altitude_legs(r, 0, triple=(3, 4, 5),
                                     labels=("M", "N", "P", "Q"),
                                     wrongs=["median", "leg_sq_short",
                                             "leg_sq_long"]),
      "two of the printed distractors are tenths either side of 2.4 rather than "
      "wrong routes"),
    S("3.6", lambda r: isosceles_cross(r, 0, labels=("S", "T", "U", "R", "V"),
                                       s=31, t=114, ask="v",
                                       wrongs=["apex_supp", "apex_half",
                                               "base_only"])),
    S("3.7", lambda r: area_range(r, 0, d1=5, d2=7, lo=48, hi=60)),
    S("3.8", lambda r: parallel_cut_area(r, 0, rt=72, lk=24, area=792)),
    S("3.9", lambda r: two_transversals(r, 0, a=43, b=122, labels=("q", "t"))),
    S("3.10", lambda r: geometric_mean(r, 0, mode="alt", ad=8, bd=6)),
    S("3.11", lambda r: vertical_similar(r, 0, wq=70, xq=120, wx=60, yq=63)),
    S("3.12", lambda r: isosceles_cross(r, 0, labels=("S", "T", "U", "R", "V"),
                                        s=29, v=41, ask="t", in_stem=True,
                                        fmt="spr", flip=True)),
    S("3.13", lambda r: similar_sufficient(r, 0, a=60, m=70, k=3, side=7, short=10,
                                           names=("L", "M", "N"),
                                           partner=("R", "S", "T"))),
    S("3.14", lambda r: geometric_mean(r, 0, mode="hyp", ad=Q(121, 3),
                                       ab=E(Q(11, 3), 0, 130))),
    S("3.15", lambda r: similar_angle(r, 0, mode="quad", angle=135, k=5, side=45,
                                      names=("P", "Q", "R", "S"),
                                      partner=("W", "X", "Y", "Z"), unit=True,
                                      wrongs=["scale", "divide", "side"])),
    S("3.16", lambda r: eight_angles(r, 0, m=7, c=250, var="x")),
]


# Source items no template reproduces, and why. Every id in the answer key must
# appear either above or here; `satbank check` counts them.
EXCLUDED: dict[str, str] = {}
