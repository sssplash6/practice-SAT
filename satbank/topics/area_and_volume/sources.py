"""The 59 official Area and Volume items, encoded as the parameters that
reproduce them.

Each record pins a template to the source item's own numbers. No answer is
written here: the answer lives in `material/keys/area_and_volume.json`, read
from the College Board PDF's own text layer, and the check asks whether the
engine -- driven by these parameters -- lands on it. A template whose
mathematics is wrong cannot be made to pass by restating the answer.

`wrongs` names the three misconceptions the item writer reached for, in the
order they are offered, out of the pool the template keeps. The wrong answers
are as much a part of an official item as the right one, and naming them here
is what stops a well-modelled mistake from sitting fourth in a list and never
reaching the page.
"""

from __future__ import annotations

from fractions import Fraction as F

from ...shapes import UNITS
from ...topic import S, Source
from .families.coordinate import (circle_from_points, leg_from_area, square_on_axes,
                                  triangle_from_points)
from .families.measure import forward, inverse
from .families.scaling import percent_change, similar_area, similar_linear, solid_scaling
from .families.special import (circle_convert, combined_area, container_percent,
                               equal_area_square, expression_measure, formula_solve,
                               missing_side, remaining_volume, symbolic_volume)

CM, IN, M, FT, U = UNITS

ALL: list[Source] = [
    # ---------------------------------------------------------------- set 1
    S("1.1", lambda r: forward(r, 0, shape_key="square", measure="area", dims={"s": 55},
                        unit=CM, style="abbr", frame="the_dim_is", fmt="mcq",
                        wrongs=["double_side", "perimeter", "double_then_square"])),
    S("1.2", lambda r: inverse(r, 0, shape_key="square", measure="area", unknown="s",
                        dims={"s": 8}, unit=IN, fmt="mcq",
                        wrongs=["over_four", "no_root", "double_measure"])),
    S("1.3", lambda r: similar_linear(r, 0, presentation="relation", k=2, base=20, fmt="mcq",
                               wrongs=["down", "square", "three_sides"])),
    S("1.4", lambda r: forward(r, 0, shape_key="rectangle", measure="perimeter",
                        dims={"l": 13, "w": 6}, unit=U, frame="has", fmt="mcq",
                        wrongs=["double_width", "double_length", "square_length"])),
    S("1.5", lambda r: missing_side(r, 0, sides=(9, 7, 6),
                             wrongs=["given_y", "given_x", "add"])),
    S("1.6", lambda r: forward(r, 0, shape_key="rectangle", measure="area", dims={"l": 36, "w": 34},
                        unit=CM, style="words", frame="with", fmt="mcq",
                        wrongs=["add", "perimeter", "square_width"])),
    S("1.7", lambda r: inverse(r, 0, shape_key="rectangle", measure="area", unknown="w",
                        dims={"l": 70, "w": 9}, unit=IN, fmt="mcq",
                        wrongs=["given", "halve_measure", "subtract"])),
    S("1.8", lambda r: forward(r, 0, shape_key="rectangle", measure="area", dims={"l": 4, "w": 2},
                        unit=CM, style="abbr", frame="with", fmt="mcq", option_units=True,
                        wrongs=["add", "perimeter", "square_sum"])),
    S("1.9", lambda r: forward(r, 0, shape_key="rectangle", measure="area", dims={"l": 64, "w": 32},
                        unit=IN, frame="has", fmt="spr")),
    S("1.10", lambda r: forward(r, 0, shape_key="rect_prism", measure="volume",
                        dims={"l": 6, "w": 2, "h": 3}, unit=CM, frame="has", fmt="mcq",
                        wrongs=["add", "base", "sum_then_height"]), "source lists options descending"),
    S("1.11", lambda r: forward(r, 0, shape_key="triangle", measure="area", dims={"b": 40, "h": 90},
                        unit=CM, frame="has", fmt="spr")),
    S("1.12", lambda r: forward(r, 0, shape_key="rectangle", measure="area", dims={"l": 7, "w": 6},
                        unit=IN, frame="with", fmt="mcq",
                        wrongs=["add", "three_sides", "double"])),
    S("1.13", lambda r: forward(r, 0, shape_key="rectangle", measure="area", dims={"l": 17, "w": 7},
                        unit=CM, style="abbr", frame="with", fmt="mcq", option_units=True,
                        wrongs=["add", "perimeter", "square_sum"])),
    S("1.14", lambda r: forward(r, 0, shape_key="rectangle", measure="area", dims={"l": 47, "w": 7},
                        unit=CM, relational=True, delta=40, fmt="mcq",
                        wrongs=["given_width", "double_width", "add"])),
    S("1.15", lambda r: inverse(r, 0, shape_key="rect_prism", measure="volume", unknown="h",
                        dims={"l": 19, "w": 8, "h": 18}, unit=IN, fmt="mcq",
                        wrongs=["add_known", "divide_one", "multiply_known"])),
    S("1.16", lambda r: similar_linear(r, 0, presentation="table", k=3, side=6, p1=50, fmt="mcq",
                                wrongs=["down", "unchanged", "plus_perimeter"])),
    S("1.17", lambda r: expression_measure(r, 0, shape="rectangle", measure="area",
                                    dims={"l": 3, "w": 39}, unit=U,
                                    wrongs=["perimeter", "double", "add"])),
    S("1.18", lambda r: forward(r, 0, shape_key="rect_prism", measure="volume",
                        dims={"l": 11, "w": 8, "h": 10}, unit=M, frame="has", fmt="spr")),
    S("1.19", lambda r: similar_linear(r, 0, presentation="two_sides", k=9, side=15, base=36,
                                fmt="mcq",
                                wrongs=["square", "side_as_k", "side_as_k_sq"])),
    S("1.20", lambda r: combined_area(r, 0, tri_area=80, side=4,
                               wrongs=["half_sum", "half_then_side", "plus_side"])),

    # ---------------------------------------------------------------- set 2
    S("2.1", lambda r: inverse(r, 0, shape_key="cylinder", measure="volume", unknown="r",
                        dims={"r": 3, "h": 5}, unit=U, fmt="mcq",
                        wrongs=["halve", "no_root", "subtract_coef"])),
    S("2.2", lambda r: equal_area_square(r, 0, r=2, given="radius", ask="side",
                                  wrongs=["radius_as_side", "sqrt_pi_r", "pi_r"])),
    S("2.3", lambda r: forward(r, 0, shape_key="rect_prism", measure="volume",
                        dims={"l": 4, "w": 9, "h": 10}, unit=CM, frame="with", fmt="spr")),
    S("2.4", lambda r: container_percent(r, 0, rA=16, pct=25, h=50, dim="radius",
                                  up=True, ask="volume",
                                  wrongs=["vol_percent", "twice_volume", "twice_radius"])),
    S("2.5", lambda r: circle_convert(r, 0, given="circumference", ask="diameter", r=31,
                               unit=CM, fmt="spr")),
    S("2.6", lambda r: inverse(r, 0, shape_key="prism_base", measure="volume", unknown="B",
                        dims={"B": 27, "h": 8}, unit=CM, style="abbr", fmt="spr")),
    S("2.7", lambda r: remaining_volume(r, 0, base=75, h=10, filled=110,
                                 wrongs=["base_over_h", "add_filled", "whole"])),
    S("2.8", lambda r: formula_solve(r, 0, a=7, b=48, volume=473, ounces=16,
                              wrongs=["ounces_root", "cone", "cube_root_only"]),
      "the official key is D (10.11), which is what the formula gives; "
      "7.79, option C, is the cube root of 473 with the 7pi/48 coefficient dropped"),
    S("2.9", lambda r: square_on_axes(r, 0, a=5, b=5, ask="area", center=(0, 0),
                               wrongs=["added", "half_diagonals", "no_halving"])),
    S("2.10", lambda r: forward(r, 0, shape_key="sphere", measure="volume", dims={"r": F(17, 5)},
                        unit=FT, frame="has", fmt="mcq",
                        wrongs=["flip_radius", "no_cube", "square_radius"]),
      "option C, 32π/5, is the one wrong answer in the set with no derivation: it is "
      "neither a wrong power of the radius nor a wrong coefficient"),
    S("2.11", lambda r: inverse(r, 0, shape_key="prism_base", measure="volume", unknown="h",
                        dims={"B": 13, "h": 29}, unit=CM, fmt="spr")),
    S("2.12", lambda r: similar_linear(r, 0, presentation="table", k=9, side=18, p1=37, fmt="mcq",
                                wrongs=["down", "unchanged", "plus_perimeter"])),
    S("2.13", lambda r: forward(r, 0, shape_key="cylinder", measure="volume", dims={"r": 4, "h": 12},
                        unit=IN, given_form="diameter", frame="has", fmt="mcq",
                        wrongs=["base", "lateral", "diameter"])),
    S("2.14", lambda r: forward(r, 0, shape_key="cube", measure="volume", dims={"e": 41},
                        unit=IN, frame="has", fmt="mcq",
                        wrongs=["times4", "square", "surface"])),
    S("2.15", lambda r: forward(r, 0, shape_key="triangle", measure="area", dims={"b": 56, "h": 112},
                        unit=CM, frame="has", fmt="mcq",
                        wrongs=["add", "quarter", "no_half"])),
    S("2.16", lambda r: expression_measure(r, 0, shape="square", measure="area", dims={"s": 94},
                                    unit=CM,
                                    wrongs=["double_side", "perimeter", "double_area"])),
    S("2.17", lambda r: forward(r, 0, shape_key="triangle", measure="area", dims={"b": 10, "h": 70},
                        unit=CM, frame="has", fmt="mcq",
                        wrongs=["add", "quarter", "no_half"]), "source lists options descending"),
    S("2.18", lambda r: similar_linear(r, 0, presentation="rect_figure", k=F(12, 5), side=5,
                                base=12, sl=10, fmt="mcq",
                                wrongs=["unchanged", "diff", "product"])),
    S("2.19", lambda r: forward(r, 0, shape_key="cylinder", measure="volume", dims={"r": 12, "h": 8},
                        unit=M, style="abbr", frame="has", fmt="mcq",
                        wrongs=["height_only", "add_dims", "swap"])),
    S("2.20", lambda r: similar_area(r, 0, direction="ratio_from_sides", k=246, fmt="mcq",
                              wrongs=["linear", "double", "half"]), "source lists options descending"),
    S("2.21", lambda r: circle_from_points(r, 0, r=3, center=(7, 8), ask="circumference",
                                    fmt="mcq",
                                    wrongs=["radius", "centre_x", "other_measure"])),

    # ---------------------------------------------------------------- set 3
    S("3.1", lambda r: solid_scaling(r, 0, mode="which_pair", pair=(7, 8),
                              wrongs=["swapped", "square_height", "square_both"])),
    S("3.2", lambda r: forward(r, 0, shape_key="cone", measure="volume", dims={"r": 3, "h": 22},
                        unit=CM, style="abbr", given_form="diameter", frame="has",
                        fmt="spr", ask_coefficient=True)),
    S("3.3", lambda r: symbolic_volume(r, 0, c=4, relation="longer", solid="cylinder",
                                wrongs=["times", "doubled", "no_square"])),
    S("3.4", lambda r: percent_change(r, 0, pct=20, area=360, up=True, fmt="spr")),
    S("3.5", lambda r: forward(r, 0, shape_key="rect_prism", measure="surface_area",
                        dims={"l": 28, "w": 15, "h": 16}, unit=CM, style="abbr",
                        frame="has", fmt="spr")),
    S("3.6", lambda r: inverse(r, 0, shape_key="cone", measure="volume", unknown="r",
                        dims={"r": F(1, 3), "h": 9}, unit=FT, fmt="mcq",
                        wrongs=["invert_divide", "no_root", "halve"]),
      "two of the source's wrong answers, 1/√3 and √3, are printed with the radical in "
      "the denominator or on its own and have no single-step derivation from the cone "
      "formula; only 3, the division taken the wrong way round, is modelled"),
    S("3.7", lambda r: solid_scaling(r, 0, mode="volume_multiple", rf=2, hf=F(1, 2), v=22,
                              wrongs=["height_only", "linear_radius", "radius_only"]),
      "the source's fourth option, 66, is three times the volume of cylinder A; no "
      "combination of the stated factors 2 and ½ produces 3"),
    S("3.8", lambda r: triangle_from_points(r, 0, pts=[(-3, 4), (5, 3), (4, -3)], fmt="spr")),
    S("3.9", lambda r: forward(r, 0, shape_key="rect_prism", measure="surface_area",
                        dims={"l": 4, "w": 5, "h": 6}, unit=IN, frame="has", fmt="mcq",
                        wrongs=["one_face_wh", "faces", "volume"])),
    S("3.10", lambda r: similar_area(r, 0, direction="area_from_ratio", shape="triangle",
                             k=F(1, 4), area=270, fmt="spr")),
    S("3.11", lambda r: inverse(r, 0, shape_key="cube", measure="surface_area", unknown="e",
                        then_measure="volume", dims={"e": 3}, unit=M, fmt="mcq",
                        wrongs=["times6", "four_faces", "face_squared"])),
    S("3.12", lambda r: inverse(r, 0, shape_key="square_prism", measure="volume", unknown="s",
                        dims={"s": 12, "h": 14}, unit=U, fmt="spr")),
    S("3.13", lambda r: leg_from_area(r, 0, dx=9, dy=6, other=24,
                               wrongs=["no_doubling", "drawn_leg", "half_area"])),
    S("3.14", lambda r: forward(r, 0, shape_key="hemisphere", measure="volume", dims={"r": 27},
                        unit=IN, frame="has", fmt="mcq", approximate=100,
                        wrongs=["square_radius", "diameter_squared", "half"]),
      "every option in the source is rounded to the nearest hundred, not to three "
      "significant figures, so this item says so"),
    S("3.15", lambda r: similar_area(r, 0, direction="area_from_ratio", shape="parallelogram",
                              k=2, area=5, fmt="mcq",
                              wrongs=["plus_ratio", "linear", "plus_area"])),
    S("3.16", lambda r: circle_from_points(r, 0, r=4, center=(6, 6), ask="circumference",
                                  fmt="spr")),
    S("3.17", lambda r: similar_area(r, 0, direction="side_from_areas", shape="rectangle",
                              k=3, side=12, area=72, fmt="mcq",
                              wrongs=["area_ratio_as_length", "ratio_itself", "unchanged"])),
    S("3.18", lambda r: forward(r, 0, shape_key="cylinder", measure="volume", dims={"r": 10, "h": 6},
                        unit=M, given_form="base_circumference", frame="has", fmt="mcq",
                        wrongs=["no_square", "lateral", "diameter"])),
]


# Source items no template reproduces, and why. Every id in the answer key
# must appear either above or here; `satbank check` counts them.
EXCLUDED: dict[str, str] = {}
