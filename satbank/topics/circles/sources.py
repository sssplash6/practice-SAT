"""The 32 official Circles items, encoded as the parameters that reproduce them.

Each record pins a template to the source item's own numbers. No answer is
written here: the answers live in `material/keys/circles.json`, read from the
College Board PDF's own text layer, and the check asks whether the engine --
driven by these parameters -- lands on them. A template whose mathematics is
wrong cannot be made to pass by restating the answer.
"""

from __future__ import annotations

from fractions import Fraction as F

from ...shapes import UNITS
from ...topic import S, Source
from .families.angles import coterminal, degree_radian, exact_trig, unit_circle_angle
from .families.arc import arc, arc_angle, arc_fraction, arc_pair, chord_angle
from .families.equation import (equation_read, equation_write, interior, point_on,
                                tangent_slope, transform)

CM, IN, M, FT, U = UNITS

ALL: list[Source] = [
    # ---------------------------------------------------------------- set 1
    S("1.1", lambda r: arc(r, 0, mode="arc", given="circumference", theta=90, size=36,
                           unit=None, fmt="mcq", frame="figure", labels=("A", "C")),
      "the right-angle mark in the figure is what gives the 90 degree central angle"),
    S("1.2", lambda r: equation_read(r, 0, form="standard", h=6, k=3, r2=81,
                                     ask="radius", fmt="mcq", display=True)),
    S("1.3", lambda r: exact_trig(r, 0, fn="cos", num=565, den=6)),

    # ---------------------------------------------------------------- set 2
    S("2.1", lambda r: degree_radian(r, 0, mode="to_radians", deg=720,
                                     ask="coefficient", fmt="spr")),
    S("2.2", lambda r: degree_radian(r, 0, mode="to_degrees", num=9, den=20, fmt="spr")),
    S("2.3", lambda r: equation_write(r, 0, h=-8, k=6, r=5, ask="equation")),
    S("2.4", lambda r: unit_circle_angle(r, 0, a=30, b=30, ask="radians", fmt="mcq",
                                         style="front", labels=("P", "Q", "R", "T"))),
    S("2.5", lambda r: equation_write(r, 0, h=-4, k=5, on=(-8, 8), ask="equation")),
    S("2.6", lambda r: degree_radian(r, 0, mode="to_degrees", num=16, den=15, fmt="spr")),
    S("2.7", lambda r: point_on(r, 0, mode="coordinate", h=3, k=5, r=3, axis="x",
                                side=1, fmt="spr")),
    S("2.8", lambda r: degree_radian(r, 0, mode="to_radians", deg=60, ask="value",
                                     fmt="mcq", style="front")),
    S("2.9", lambda r: equation_read(r, 0, form="general", h=-29, k=0, r2=841,
                                     ask="center", display=True)),
    S("2.10", lambda r: equation_read(r, 0, form="standard", h=1, k=-7, r2=1,
                                      ask="center", display=False)),
    S("2.11", lambda r: arc_pair(r, 0, mode="sum", minor=39, ratio=5, unit=CM,
                                 fmt="mcq", labels=("M", "N", "P"))),

    # ---------------------------------------------------------------- set 3
    S("3.1", lambda r: arc_pair(r, 0, mode="other", theta=100, length=5, pi=True,
                                unit=None, fmt="mcq", labels=("A", "B", "C"),
                                style="front")),
    S("3.2", lambda r: equation_read(r, 0, form="general", h=-10, k=-8, r2=144,
                                     ask="center", display=True)),
    S("3.3", lambda r: chord_angle(r, 0, base=30, r=18, ask="arc", fmt="mcq",
                                   labels=("A", "B"), via="C")),
    S("3.4", lambda r: equation_read(r, 0, form="standard", h=-6, k=-3, r2=121,
                                     ask="radius", fmt="spr", display=False)),
    S("3.5", lambda r: tangent_slope(r, 0, h=-4, k=-6, dx=-3, dy=-1, label="k")),
    S("3.6", lambda r: equation_read(r, 0, form="scaled", lead=2, h=(3, 2), k=(-1, 2),
                                     r2=25, ask="radius", fmt="mcq", display=False)),
    S("3.7", lambda r: arc(r, 0, mode="whole", theta=45, size=3, unit=IN, fmt="mcq")),
    S("3.8", lambda r: point_on(r, 0, mode="diameter", h=6, k=-5, r=4, dx=4, dy=0,
                                labels=("P", "Q"))),
    S("3.9", lambda r: equation_write(r, 0, h=-5, k=2, r=9, ask="coefficient",
                                      coef="c", fmt="spr")),
    S("3.10", lambda r: arc_fraction(r, 0, r=1, frac=(1, 6), fmt="spr",
                                     labels=("A", "B"))),
    S("3.11", lambda r: interior(r, 0, h=-3, k=1, r=5, out=(6, 1), far=(-4, 2),
                                 sq=(3, -1))),
    S("3.12", lambda r: transform(r, 0, mode="scale", h=-5, k=5, r2=4, scale=2,
                                  fmt="spr")),
    S("3.13", lambda r: arc_angle(r, 0, theta=100, ask="angle", fmt="spr",
                                  labels=("R", "S"))),
    S("3.14", lambda r: equation_read(r, 0, form="symbolic", lead=8, u=7, v=-4, n=3,
                                      sym="p", fmt="spr")),
    S("3.15", lambda r: transform(r, 0, mode="translate", h=0, k=6, r2=7,
                                  direction="right", shift=96, ask="rhs", times=4,
                                  fmt="spr")),
    S("3.16", lambda r: equation_write(r, 0, h=16, k=17, sym="k", mult=7,
                                       ask="equation")),
    S("3.17", lambda r: transform(r, 0, mode="translate", h=7, k=-3, r2=1,
                                  direction="right", shift=4, ask="equation")),
    S("3.18", lambda r: coterminal(r, 0, spot=2, k=12,
                                   alts=(24, F(27, 2), F(29, 2)),
                                   labels=("F", "G", "H"))),
]


# Source items no template reproduces, and why. Every id in the answer key must
# appear either above or here; `satbank check` counts them.
EXCLUDED: dict[str, str] = {}
