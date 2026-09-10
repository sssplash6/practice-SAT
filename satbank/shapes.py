"""Shape registry: the symbolic formulas, names and dimension labels.

`verify.py` re-implements every one of these numerically and independently;
nothing ships unless the two agree. Double-entry bookkeeping for math items.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .exact import E, PI, Exact

__all__ = ["SHAPES", "Shape", "Dim", "Unit", "UNITS", "measure_phrase", "unit_noun"]


@dataclass(frozen=True)
class Dim:
    key: str
    label: str          # "length", "radius", "edge length"
    the: str            # "the length of the prism", used in longer stems


@dataclass(frozen=True)
class Unit:
    noun: str           # "centimeter"
    abbr: str           # "cm"
    plural: str = ""    # "inches", "feet" -- never noun + "s"

    def many(self) -> str:
        return self.plural or f"{self.noun}s"


UNITS = [
    Unit("centimeter", "cm", "centimeters"),
    Unit("inch", "in", "inches"),
    Unit("meter", "m", "meters"),
    Unit("foot", "ft", "feet"),
    Unit("unit", "", "units"),
]

# measure -> (display noun, how many dimensions of length it carries)
MEASURES = {
    "area": ("area", 2),
    "perimeter": ("perimeter", 1),
    "circumference": ("circumference", 1),
    "volume": ("volume", 3),
    "surface_area": ("surface area", 2),
}


@dataclass(frozen=True)
class Shape:
    key: str
    noun: str                                   # "right circular cylinder"
    short: str                                  # "cylinder" -- used on later mention
    article: str                                # "a" / "an"
    kind: str                                   # "plane" | "solid"
    dims: tuple[Dim, ...]
    measures: dict[str, Callable[[dict], Exact]]

    def name(self, capital: bool = False) -> str:
        s = f"{self.article} {self.noun}"
        return s[0].upper() + s[1:] if capital else s

    def dim(self, key: str) -> Dim:
        return next(d for d in self.dims if d.key == key)


def _d(key, label, the=None) -> Dim:
    return Dim(key, label, the or f"the {label}")


def _shape(key, noun, kind, dims, measures, article="a", short=None) -> Shape:
    return Shape(key, noun, short or noun.split()[-1], article, kind, tuple(dims), measures)


SHAPES: dict[str, Shape] = {}


def _reg(s: Shape) -> Shape:
    SHAPES[s.key] = s
    return s


# ------------------------------------------------------------------- plane

_reg(_shape("square", "square", "plane",
            [_d("s", "side length", "the length of each side")],
            {"area": lambda p: p["s"] ** 2,
             "perimeter": lambda p: E(4) * p["s"]}))

_reg(_shape("rectangle", "rectangle", "plane",
            [_d("l", "length"), _d("w", "width")],
            {"area": lambda p: p["l"] * p["w"],
             "perimeter": lambda p: E(2) * (p["l"] + p["w"])}))

_reg(_shape("triangle", "triangle", "plane",
            [_d("b", "base length"), _d("h", "height")],
            {"area": lambda p: p["b"] * p["h"] / E(2)}))

_reg(_shape("parallelogram", "parallelogram", "plane",
            [_d("b", "base length"), _d("h", "height")],
            {"area": lambda p: p["b"] * p["h"]}))

_reg(_shape("circle", "circle", "plane",
            [_d("r", "radius")],
            {"area": lambda p: PI * p["r"] ** 2,
             "circumference": lambda p: E(2) * PI * p["r"]}))

# ------------------------------------------------------------------- solid

_reg(_shape("cube", "cube", "solid",
            [_d("e", "edge length")],
            {"volume": lambda p: p["e"] ** 3,
             "surface_area": lambda p: E(6) * p["e"] ** 2}))

_reg(_shape("rect_prism", "right rectangular prism", "solid",
            [_d("l", "length"), _d("w", "width"), _d("h", "height")],
            {"volume": lambda p: p["l"] * p["w"] * p["h"],
             "surface_area": lambda p: E(2) * (p["l"] * p["w"] + p["l"] * p["h"] + p["w"] * p["h"])}))

_reg(_shape("square_prism", "right square prism", "solid",
            [_d("s", "edge of the base", "the length of an edge of the base"), _d("h", "height")],
            {"volume": lambda p: p["s"] ** 2 * p["h"],
             "surface_area": lambda p: E(2) * p["s"] ** 2 + E(4) * p["s"] * p["h"]}))

_reg(_shape("cylinder", "right circular cylinder", "solid",
            [_d("r", "radius"), _d("h", "height")],
            {"volume": lambda p: PI * p["r"] ** 2 * p["h"],
             "surface_area": lambda p: E(2) * PI * p["r"] ** 2 + E(2) * PI * p["r"] * p["h"]}))

_reg(_shape("cone", "right circular cone", "solid",
            [_d("r", "radius"), _d("h", "height")],
            {"volume": lambda p: PI * p["r"] ** 2 * p["h"] / E(3)}))

_reg(_shape("sphere", "sphere", "solid",
            [_d("r", "radius")],
            {"volume": lambda p: E(4) * PI * p["r"] ** 3 / E(3),
             "surface_area": lambda p: E(4) * PI * p["r"] ** 2}))

_reg(_shape("hemisphere", "hemisphere", "solid",
            [_d("r", "radius")],
            {"volume": lambda p: E(2) * PI * p["r"] ** 3 / E(3)}))

# A prism whose base area is given directly (the source's triangular prism).
_reg(_shape("prism_base", "triangular prism", "solid",
            [_d("B", "base area", "the area of the base"), _d("h", "height")],
            {"volume": lambda p: p["B"] * p["h"]}))


# ---------------------------------------------------------------- phrasing

def unit_noun(unit: Unit, measure: str, style: str = "words") -> str:
    """'square centimeters' vs 'cm^2' -- both appear in the source set."""
    _, power = MEASURES[measure]
    if not unit.abbr:                       # bare "units"
        return {1: "units", 2: "square units", 3: "cubic units"}[power]
    if style == "abbr" and power > 1 and unit.abbr != "in":   # "in in^3" reads badly
        return f"{unit.abbr}{'²' if power == 2 else '³'}"
    word = {1: "", 2: "square ", 3: "cubic "}[power]
    return f"{word}{unit.many()}"


def measure_phrase(measure: str, unit: Unit, style: str = "words") -> str:
    """'the area, in square centimeters,' -- the SAT's standard construction."""
    noun, _ = MEASURES[measure]
    return f"the {noun}, in {unit_noun(unit, measure, style)},"
