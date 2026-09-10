"""The 59 official items this engine was built from, encoded as parameters.

Each record pins a template to the source item's own numbers. The acceptance
test then asks one question: does the engine, driven by those parameters,
produce the official answer? If a template's mathematics is wrong, the source
item catches it.

`options` holds the official answer choices in printed order, so the test can
also report how much of College Board's distractor design the misconception
library actually reproduces.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from fractions import Fraction as F
from typing import Callable

from .families.coordinate import (circle_from_points, leg_from_area, square_on_axes,
                                  triangle_from_points)
from .families.measure import forward, inverse
from .families.scaling import percent_change, similar_area, similar_linear, solid_scaling
from .families.special import (circle_convert, combined_area, container_percent,
                               equal_area_square, expression_measure, formula_solve,
                               missing_side, remaining_volume, symbolic_volume)
from .shapes import UNITS

CM, IN, M, FT, U = UNITS


@dataclass
class Source:
    id: str
    cb_id: str
    tier: str
    answer: str                       # the official answer, as printed
    build: Callable
    options: tuple = ()               # official choices, printed order ('' = grid-in)
    note: str = ""


def S(id, cb_id, tier, answer, build, options=(), note=""):
    return Source(id, cb_id, tier, answer, build, options, note)


ALL: list[Source] = [
    # ---------------------------------------------------------------- set 1
    S("1.1", "5252e606", "easy", "3,025",
      lambda r: forward(r, 0, shape_key="square", measure="area", dims={"s": 55},
                        unit=CM, style="abbr", frame="the_dim_is", fmt="mcq"),
      ("110", "220", "3,025", "12,100")),
    S("1.2", "59cb654c", "easy", "8",
      lambda r: inverse(r, 0, shape_key="square", measure="area", unknown="s",
                        dims={"s": 8}, unit=IN, fmt="mcq"),
      ("8", "16", "64", "128")),
    S("1.3", "0837c3b9", "easy", "40",
      lambda r: similar_linear(r, 0, presentation="relation", k=2, base=20, fmt="mcq"),
      ("10", "40", "80", "120")),
    S("1.4", "c88183f7", "easy", "38",
      lambda r: forward(r, 0, shape_key="rectangle", measure="perimeter",
                        dims={"l": 13, "w": 6}, unit=U, frame="has", fmt="mcq"),
      ("12", "26", "38", "52")),
    S("1.5", "29e9b28c", "easy", "6",
      lambda r: missing_side(r, 0, sides=(9, 7, 6)), ("6", "7", "9", "16")),
    S("1.6", "3453aafc", "easy", "1,224",
      lambda r: forward(r, 0, shape_key="rectangle", measure="area", dims={"l": 36, "w": 34},
                        unit=CM, style="words", frame="with", fmt="mcq"),
      ("70", "140", "1,156", "1,224")),
    S("1.7", "f60bb551", "easy", "9",
      lambda r: inverse(r, 0, shape_key="rectangle", measure="area", unknown="w",
                        dims={"l": 70, "w": 9}, unit=IN, fmt="mcq"),
      ("9", "70", "315", "560")),
    S("1.8", "4420e500", "easy", "8",
      lambda r: forward(r, 0, shape_key="rectangle", measure="area", dims={"l": 4, "w": 2},
                        unit=CM, style="abbr", frame="with", fmt="mcq"),
      ("6", "8", "12", "36")),
    S("1.9", "165c30c4", "easy", "2048",
      lambda r: forward(r, 0, shape_key="rectangle", measure="area", dims={"l": 64, "w": 32},
                        unit=IN, frame="has", fmt="spr")),
    S("1.10", "d683a9cc", "easy", "36",
      lambda r: forward(r, 0, shape_key="rect_prism", measure="volume",
                        dims={"l": 6, "w": 2, "h": 3}, unit=CM, frame="has", fmt="mcq"),
      ("36", "24", "12", "11"), "source lists options descending"),
    S("1.11", "f39f88b7", "easy", "1800",
      lambda r: forward(r, 0, shape_key="triangle", measure="area", dims={"b": 40, "h": 90},
                        unit=CM, frame="has", fmt="spr")),
    S("1.12", "93f48423", "easy", "42",
      lambda r: forward(r, 0, shape_key="rectangle", measure="area", dims={"l": 7, "w": 6},
                        unit=IN, frame="with", fmt="mcq"), ("13", "20", "42", "84")),
    S("1.13", "d2047497", "easy", "119",
      lambda r: forward(r, 0, shape_key="rectangle", measure="area", dims={"l": 17, "w": 7},
                        unit=CM, style="abbr", frame="with", fmt="mcq"),
      ("24", "48", "119", "576")),
    S("1.14", "a490003a", "easy", "329",
      lambda r: forward(r, 0, shape_key="rectangle", measure="area", dims={"l": 47, "w": 7},
                        unit=CM, relational=True, delta=40, fmt="mcq"),
      ("7", "14", "54", "329")),
    S("1.15", "50774285", "easy", "18",
      lambda r: inverse(r, 0, shape_key="rect_prism", measure="volume", unknown="h",
                        dims={"l": 19, "w": 8, "h": 18}, unit=IN, fmt="mcq"),
      ("18", "27", "144", "152")),
    S("1.16", "fc5ef8d3", "easy", "18",
      lambda r: similar_linear(r, 0, presentation="table", k=3, side=6, p1=50, fmt="mcq"),
      ("2", "6", "18", "56")),
    S("1.17", "0e40dfb0", "easy", "3 * 39",
      lambda r: expression_measure(r, 0, shape="rectangle", measure="area",
                                   dims={"l": 3, "w": 39}, unit=U),
      ("2(3 + 39)", "2(3 * 39)", "3 + 39", "3 * 39")),
    S("1.18", "2b41a4c4", "easy", "880",
      lambda r: forward(r, 0, shape_key="rect_prism", measure="volume",
                        dims={"l": 11, "w": 8, "h": 10}, unit=M, frame="has", fmt="spr")),
    S("1.19", "babd7461", "easy", "324",
      lambda r: similar_linear(r, 0, presentation="two_sides", k=9, side=15, base=36, fmt="mcq"),
      ("324", "540", "2,916", "8,100")),
    S("1.20", "bb560789", "easy", "96",
      lambda r: combined_area(r, 0, tri_area=80, side=4), ("42", "44", "84", "96")),

    # ---------------------------------------------------------------- set 2
    S("2.1", "f67e4efc", "medium", "3",
      lambda r: inverse(r, 0, shape_key="cylinder", measure="volume", unknown="r",
                        dims={"r": 3, "h": 5}, unit=U, fmt="mcq"),
      ("3", "4.5", "9", "40")),
    S("2.2", "5afbdc8e", "medium", "2√π",
      lambda r: equal_area_square(r, 0, r=2), ("2", "√(2π)", "2√π", "2π")),
    S("2.3", "ec5d4823", "medium", "360",
      lambda r: forward(r, 0, shape_key="rect_prism", measure="volume",
                        dims={"l": 4, "w": 9, "h": 10}, unit=CM, frame="with", fmt="spr")),
    S("2.4", "151eda3c", "medium", "20,000π",
      lambda r: container_percent(r, 0, rA=16, pct=25, h=50),
      ("16,000π", "20,000π", "25,000π", "31,250π")),
    S("2.5", "38517165", "medium", "31",
      lambda r: circle_convert(r, 0, given="circumference", ask="diameter", r=31,
                               unit=CM, fmt="spr")),
    S("2.6", "08b7a3f5", "medium", "27",
      lambda r: inverse(r, 0, shape_key="prism_base", measure="volume", unknown="B",
                        dims={"B": 27, "h": 8}, unit=CM, style="abbr", fmt="spr")),
    S("2.7", "a2e76b60", "medium", "640",
      lambda r: remaining_volume(r, 0, base=75, h=10, filled=110),
      ("7.5", "185", "640", "750")),
    S("2.8", "37dde49f", "medium", "10.11",
      lambda r: formula_solve(r, 0, a=7, b=48, volume=473),
      ("2.52", "7.67", "7.79", "10.11"),
      "source answer key says C (7.79); 7.79 is the cube root of 473 with the "
      "7pi/48 coefficient dropped. The formula gives 10.11, option D."),
    S("2.9", "cf53cb56", "medium", "50",
      lambda r: square_on_axes(r, 0, a=5), ("20", "25", "50", "100")),
    S("2.10", "d621cffb", "medium", "19,652π/375",
      lambda r: forward(r, 0, shape_key="sphere", measure="volume", dims={"r": F(17, 5)},
                        unit=FT, frame="has", fmt="mcq"),
      ("5π/17", "68π/15", "32π/5", "19,652π/375")),
    S("2.11", "3b931fb0", "medium", "29",
      lambda r: inverse(r, 0, shape_key="prism_base", measure="volume", unknown="h",
                        dims={"B": 13, "h": 29}, unit=CM, fmt="spr")),
    S("2.12", "e0874bc2", "medium", "162",
      lambda r: similar_linear(r, 0, presentation="table", k=9, side=18, p1=37, fmt="mcq"),
      ("2", "18", "55", "162")),
    S("2.13", "c0586eb5", "medium", "192π",
      lambda r: forward(r, 0, shape_key="cylinder", measure="volume", dims={"r": 4, "h": 12},
                        unit=IN, given_form="diameter", frame="has", fmt="mcq"),
      ("16π", "96π", "192π", "768π")),
    S("2.14", "e336a1d2", "medium", "68,921",
      lambda r: forward(r, 0, shape_key="cube", measure="volume", dims={"e": 41},
                        unit=IN, frame="has", fmt="mcq"),
      ("164", "1,681", "10,086", "68,921")),
    S("2.15", "468613c0", "medium", "3,136",
      lambda r: forward(r, 0, shape_key="triangle", measure="area", dims={"b": 56, "h": 112},
                        unit=CM, frame="has", fmt="mcq"), ("168", "1,568", "3,136", "6,272")),
    S("2.16", "aef4fd8a", "medium", "94 * 94",
      lambda r: expression_measure(r, 0, shape="square", measure="area", dims={"s": 94},
                                   unit=CM), ("2 * 94", "2 * 94 * 94", "4 * 94", "94 * 94")),
    S("2.17", "9c0a0eca", "medium", "350",
      lambda r: forward(r, 0, shape_key="triangle", measure="area", dims={"b": 10, "h": 70},
                        unit=CM, frame="has", fmt="mcq"), ("700", "350", "175", "80"),
      "source lists options descending"),
    S("2.18", "e9c5bfb2", "medium", "24",
      lambda r: similar_linear(r, 0, presentation="rect_figure", k=F(12, 5), side=5,
                               base=12, sl=10, fmt="mcq"), ("60", "24", "17", "10")),
    S("2.19", "a2659088", "medium", "1,152π",
      lambda r: forward(r, 0, shape_key="cylinder", measure="volume", dims={"r": 12, "h": 8},
                        unit=M, style="abbr", frame="has", fmt="mcq"),
      ("8π", "20π", "768π", "1,152π")),
    S("2.20", "03c6994f", "medium", "60,516",
      lambda r: similar_area(r, 0, direction="ratio_from_sides", k=246, fmt="mcq"),
      ("60,516", "492", "246", "123"), "source lists options descending"),
    S("2.21", "096c7ef5", "medium", "6",
      lambda r: circle_from_points(r, 0, r=3, center=(7, 8), ask="circumference",
                                  fmt="mcq"),
      ("3", "6", "7", "9")),

    # ---------------------------------------------------------------- set 3
    S("3.1", "a07ed090", "hard", "R = 7r and H = 8h",
      lambda r: solid_scaling(r, 0, mode="which_pair", pair=(7, 8)),
      ("R = 8r and H = 7h", "R = 8r and H = 49h", "R = 7r and H = 8h", "R = 49r and H = 8h")),
    S("3.2", "899c6042", "hard", "66",
      lambda r: forward(r, 0, shape_key="cone", measure="volume", dims={"r": 3, "h": 22},
                        unit=CM, style="abbr", given_form="diameter", frame="has",
                        fmt="spr", ask_coefficient=True)),
    S("3.3", "b0dc920d", "hard", "V = pi*r^3 + 4pi*r^2",
      lambda r: symbolic_volume(r, 0, c=4, relation="longer"),
      ("V = 4pi*r^3", "V = pi(2r)^3", "V = pi*r^2 + 4pi*r", "V = pi*r^3 + 4pi*r^2")),
    S("3.4", "5b2b8866", "hard", "518.4",
      lambda r: percent_change(r, 0, pct=20, area=360, up=True, fmt="spr")),
    S("3.5", "9f934297", "hard", "2216",
      lambda r: forward(r, 0, shape_key="rect_prism", measure="surface_area",
                        dims={"l": 28, "w": 15, "h": 16}, unit=CM, style="abbr",
                        frame="has", fmt="spr")),
    S("3.6", "dc71597b", "hard", "1/3",
      lambda r: inverse(r, 0, shape_key="cone", measure="volume", unknown="r",
                        dims={"r": F(1, 3), "h": 9}, unit=FT, fmt="mcq"),
      ("1/3", "√3/3", "√3", "3")),
    S("3.7", "93de3f84", "hard", "44",
      lambda r: solid_scaling(r, 0, mode="volume_multiple", rf=2, hf=F(1, 2), v=22),
      ("11", "22", "44", "66")),
    S("3.8", "eb70d2d0", "hard", "24.5",
      lambda r: triangle_from_points(r, 0, pts=[(-3, 4), (5, 3), (4, -3)], fmt="spr")),
    S("3.9", "f7e626b2", "hard", "148",
      lambda r: forward(r, 0, shape_key="rect_prism", measure="surface_area",
                        dims={"l": 4, "w": 5, "h": 6}, unit=IN, frame="has", fmt="mcq"),
      ("30", "74", "120", "148")),
    S("3.10", "459dd6c5", "hard", "135/8",
      lambda r: similar_area(r, 0, direction="area_from_ratio", shape="triangle",
                             k=F(1, 4), area=270, fmt="spr")),
    S("3.11", "310c87fe", "hard", "27",
      lambda r: inverse(r, 0, shape_key="cube", measure="surface_area", unknown="e",
                        then_measure="volume", dims={"e": 3}, unit=M, fmt="mcq"),
      ("18", "27", "36", "81")),
    S("3.12", "983412ea", "hard", "12",
      lambda r: inverse(r, 0, shape_key="square_prism", measure="volume", unknown="s",
                        dims={"s": 12, "h": 14}, unit=U, fmt="spr")),
    S("3.13", "099526fc", "hard", "24",
      lambda r: leg_from_area(r, 0, dx=9, dy=6, other=24),
      ("12", "24", "3√13", "18√13")),
    S("3.14", "c984f1a5", "hard", "41,200",
      lambda r: forward(r, 0, shape_key="hemisphere", measure="volume", dims={"r": 27},
                        unit=IN, frame="has", fmt="mcq", approximate=True),
      ("1,500", "6,100", "30,900", "41,200")),
    S("3.15", "6708546e", "hard", "20",
      lambda r: similar_area(r, 0, direction="area_from_ratio", shape="parallelogram",
                             k=2, area=5, fmt="mcq"), ("7", "10", "20", "25")),
    S("3.16", "b2528e6b", "hard", "8",
      lambda r: circle_from_points(r, 0, r=4, center=(6, 6), ask="circumference",
                                  fmt="spr")),
    S("3.17", "502d9690", "hard", "12",
      lambda r: similar_area(r, 0, direction="side_from_areas", shape="rectangle",
                             k=3, side=12, area=72, fmt="mcq"), ("4", "9", "12", "36")),
    S("3.18", "deff8a2f", "hard", "600π",
      lambda r: forward(r, 0, shape_key="cylinder", measure="volume", dims={"r": 10, "h": 6},
                        unit=M, given_form="base_circumference", frame="has", fmt="mcq"),
      ("60π", "120π", "600π", "2,400π")),
]
