"""The measurement family: a shape, a measure, and a direction.

FORWARD   dimensions  -> measure        ("a cube of edge 41; find the volume")
INVERSE   measure     -> a dimension    ("volume 2,736 and a 19x8 base; find h")

The same two generators cover 40 of the 59 source items once you add the axes
the source actually varies: which quantity is given (radius / diameter /
base circumference / base area), how the sentence is framed, whether units are
spelled out or abbreviated, and multiple-choice versus grid-in.
"""

from __future__ import annotations

import random
from fractions import Fraction

from ....exact import E, PI, Exact
from ....item import Item, ItemError, Mis, assemble
from ....shapes import SHAPES, UNITS, Shape, Unit, measure_phrase, unit_noun
from ....verify import check
from ..kit import attempt, decimal_text, pick

__all__ = ["forward", "inverse", "DIM_RANGE", "GIVEN_FORMS"]

# Ranges chosen to match the magnitudes the source items actually use.
DIM_RANGE = {
    ("square", "s"): (2, 94), ("rectangle", "l"): (3, 70), ("rectangle", "w"): (2, 40),
    ("triangle", "b"): (4, 60), ("triangle", "h"): (4, 112),
    ("parallelogram", "b"): (3, 30), ("parallelogram", "h"): (3, 30),
    ("circle", "r"): (2, 30),
    ("cube", "e"): (2, 45),
    ("rect_prism", "l"): (3, 30), ("rect_prism", "w"): (2, 20), ("rect_prism", "h"): (2, 20),
    ("square_prism", "s"): (3, 20), ("square_prism", "h"): (4, 30),
    ("cylinder", "r"): (2, 20), ("cylinder", "h"): (3, 50),
    ("cone", "r"): (2, 15), ("cone", "h"): (3, 30),
    ("sphere", "r"): (2, 12), ("hemisphere", "r"): (2, 30),
    ("prism_base", "B"): (5, 60), ("prism_base", "h"): (3, 20),
}

# Alternative ways the source states a circular dimension.
GIVEN_FORMS = {
    "direct": None,
    "diameter": ("diameter", lambda r: E(2) * r),
    "base_circumference": ("circumference of the base", lambda r: E(2) * PI * r),
    "base_area": ("area of the base", lambda r: PI * r ** 2),
}
CIRCULAR = {"cylinder", "cone", "sphere", "hemisphere", "circle"}

# Everyday objects the SAT wraps a bare shape in.
OBJECTS = {
    "rectangle": ["sign", "rug", "patio", "window pane", "garden plot", "tabletop"],
    "square": ["tile", "napkin", "photograph", "tarp", "paving stone"],
    "triangle": ["sail", "pennant", "gable", "warning sign"],
    "parallelogram": ["deck panel", "tile", "banner"],
    "circle": ["mirror", "tabletop", "lid", "fountain"],
    "rect_prism": ["shipping crate", "storage bin", "aquarium", "planter box"],
    "cube": ["wooden block", "storage cube", "die", "packing box"],
    "cylinder": ["water tank", "canister", "drum", "silo"],
    "cone": ["paper cup", "funnel", "party hat"],
    "sphere": ["ball bearing", "globe", "water balloon"],
    "square_prism": ["pillar", "planter", "storage column"],
}


def _article(word: str) -> str:
    return "an" if word[0].lower() in "aeiou" else "a"


def _qty(value: Exact, unit: Unit, first: bool, style: str, power: int = 1) -> str:
    """'41 inches', '55 centimeters (cm)' on first mention, then '34 cm'."""
    noun = unit_noun(unit, {1: "perimeter", 2: "area", 3: "volume"}[power], style)
    if not unit.abbr:
        return f"{value.plain()} {noun}"
    if style == "abbr" and first and power == 1:
        return f"{value.plain()} {unit.many()} ({unit.abbr})"
    if style == "abbr" and power == 1:
        return f"{value.plain()} {unit.abbr}"
    return f"{value.plain()} {noun}"


def _join(parts: list[str]) -> str:
    if len(parts) == 1:
        return parts[0]
    if len(parts) == 2:
        return f"{parts[0]} and {parts[1]}"
    return ", ".join(parts[:-1]) + f", and {parts[-1]}"


def _pick_dims(rng: random.Random, shape: Shape) -> dict[str, Exact]:
    return {d.key: E(rng.randint(*DIM_RANGE[(shape.key, d.key)])) for d in shape.dims}


# --------------------------------------------------------------- mistakes

def _forward_mistakes(shape_key: str, measure: str, p: dict) -> dict[str, Mis]:
    """The named wrong answers a real student produces for this measure.

    A dict, not a list: a source item names the three College Board printed
    (`wrongs=[...]` in sources.py) and a free draw is offered the lot. Every
    entry was read off an official option -- the key is what a teacher calls
    the error, and nothing is here to fill a fourth slot.
    """
    g = p.get
    M: dict[str, Mis] = {}
    if shape_key == "square":
        s = g("s")
        if measure == "area":
            M = {
                "perimeter": Mis("found the perimeter instead of the area", E(4) * s),
                "double_side": Mis("doubled the side instead of squaring it", E(2) * s),
                "double_then_square": Mis("doubled the side, then squared it",
                                          (E(2) * s) ** 2),
                "square_perimeter": Mis("squared the perimeter", (E(4) * s) ** 2),
            }
        else:
            M = {
                "area": Mis("found the area instead of the perimeter", s ** 2),
                "two_sides": Mis("added only two sides", E(2) * s),
                "three_sides": Mis("used three sides", E(3) * s),
            }
    elif shape_key == "rectangle":
        l, w = g("l"), g("w")
        if measure == "area":
            M = {
                "add": Mis("added the dimensions instead of multiplying", l + w),
                "perimeter": Mis("found the perimeter instead of the area", E(2) * (l + w)),
                "square_sum": Mis("squared the sum of the dimensions", (l + w) ** 2),
                "double": Mis("doubled the product", E(2) * l * w),
                "square_width": Mis("squared the width instead of multiplying it by "
                                    "the length", w ** 2),
                "square_length": Mis("squared the length instead of multiplying it by "
                                     "the width", l ** 2),
                "three_sides": Mis("added three of the four sides", E(2) * l + w),
            }
        else:
            M = {
                "area": Mis("found the area instead of the perimeter", l * w),
                "half": Mis("added the two given sides only", l + w),
                "double_length": Mis("doubled the length only", E(2) * l),
                "double_width": Mis("doubled the width only", E(2) * w),
                "square_length": Mis("treated the rectangle as a square on its length",
                                     E(4) * l),
                "square_width": Mis("treated the rectangle as a square on its width",
                                    E(4) * w),
            }
    elif shape_key in ("triangle", "parallelogram"):
        b, h = g("b"), g("h")
        if shape_key == "triangle":
            M = {
                "no_half": Mis("forgot to multiply by one half", b * h),
                "add": Mis("added the base and height", b + h),
                "quarter": Mis("halved twice", b * h / E(4)),
                "double": Mis("doubled instead of halving", E(2) * b * h),
            }
        else:
            M = {
                "half": Mis("multiplied by one half as if it were a triangle", b * h / E(2)),
                "add": Mis("added the base and height", b + h),
                "perimeter": Mis("found the perimeter of a rectangle with those sides",
                                 E(2) * (b + h)),
            }
    elif shape_key == "circle":
        r = g("r")
        if measure == "area":
            M = {
                "circumference": Mis("found the circumference instead of the area",
                                     E(2) * PI * r),
                "no_square": Mis("forgot to square the radius", PI * r),
                "diameter": Mis("used the diameter as the radius", PI * (E(2) * r) ** 2),
            }
        else:
            M = {
                "area": Mis("found the area instead of the circumference", PI * r ** 2),
                "pi_r": Mis("used pi*r instead of 2*pi*r", PI * r),
                "diameter": Mis("used the diameter as the radius", E(4) * PI * r),
                "as_diameter": Mis("gave the diameter instead of the circumference",
                                   E(2) * r),
            }
    elif shape_key == "cube":
        e = g("e")
        if measure == "volume":
            M = {
                "surface": Mis("found the surface area instead of the volume", E(6) * e ** 2),
                "square": Mis("squared the edge instead of cubing it", e ** 2),
                "times3": Mis("multiplied the edge by 3", E(3) * e),
                "times6": Mis("multiplied the edge by 6, the number of faces", E(6) * e),
                "times4": Mis("multiplied the edge by 4, the perimeter of one face",
                              E(4) * e),
                "four_faces": Mis("used the area of four faces instead of the volume",
                                  E(4) * e ** 2),
                "face_squared": Mis("multiplied the area of a face by itself instead of "
                                    "by the edge length", e ** 4),
            }
        else:
            M = {
                "volume": Mis("found the volume instead of the surface area", e ** 3),
                "four_faces": Mis("counted four faces instead of six", E(4) * e ** 2),
                "one_face": Mis("found the area of one face only", e ** 2),
            }
    elif shape_key == "rect_prism":
        l, w, h = g("l"), g("w"), g("h")
        faces = l * w + l * h + w * h
        if measure == "volume":
            M = {
                "base": Mis("found the area of the base only", l * w),
                "surface": Mis("found the surface area instead of the volume", E(2) * faces),
                "add": Mis("added the three dimensions", l + w + h),
                "faces": Mis("summed the three distinct face areas", faces),
                "sum_then_height": Mis("added the length and the width instead of "
                                       "multiplying them, then used the height",
                                       (l + w) * h),
            }
        else:
            M = {
                "volume": Mis("found the volume instead of the surface area", l * w * h),
                "faces": Mis("counted each pair of faces only once", faces),
                "one_face": Mis("used one face only", l * w),
                "one_face_wh": Mis("used the area of one side face only", w * h),
                "one_face_lh": Mis("used the area of one end face only", l * h),
                "double_sum": Mis("added the dimensions and doubled", E(2) * (l + w + h)),
            }
    elif shape_key == "square_prism":
        s, h = g("s"), g("h")
        if measure == "volume":
            M = {
                "no_square": Mis("did not square the base edge", s * h),
                "base": Mis("found the area of the base only", s ** 2),
                "square_height": Mis("squared the height instead of the base edge",
                                     s * h ** 2),
            }
        else:
            M = {
                "volume": Mis("found the volume instead of the surface area", s ** 2 * h),
                "no_bases": Mis("left out the two bases", E(4) * s * h),
                "no_lateral": Mis("left out the lateral faces", E(2) * s ** 2),
            }
    elif shape_key == "cylinder":
        r, h = g("r"), g("h")
        if measure == "volume":
            M = {
                "diameter": Mis("used the diameter in place of the radius",
                                PI * (E(2) * r) ** 2 * h),
                "no_square": Mis("forgot to square the radius", PI * r * h),
                "base": Mis("found the area of the base only", PI * r ** 2),
                "lateral": Mis("found the lateral surface area", E(2) * PI * r * h),
                "swap": Mis("swapped the radius and the height", PI * h ** 2 * r),
                "add_dims": Mis("added the radius and the height instead of "
                                "multiplying", PI * (r + h)),
                "height_only": Mis("used the height alone, leaving out the base", PI * h),
            }
        else:
            M = {
                "volume": Mis("found the volume instead of the surface area", PI * r ** 2 * h),
                "no_bases": Mis("left out the two bases", E(2) * PI * r * h),
                "no_lateral": Mis("left out the lateral surface", E(2) * PI * r ** 2),
            }
    elif shape_key == "cone":
        r, h = g("r"), g("h")
        M = {
            "cylinder": Mis("used the cylinder formula, omitting the one third",
                            PI * r ** 2 * h),
            "half": Mis("halved instead of taking one third", PI * r ** 2 * h / E(2)),
            "no_square": Mis("forgot to square the radius", PI * r * h / E(3)),
            "diameter": Mis("used the diameter in place of the radius",
                            PI * (E(2) * r) ** 2 * h / E(3)),
        }
    elif shape_key == "sphere":
        r = g("r")
        if measure == "volume":
            M = {
                "surface": Mis("found the surface area instead of the volume",
                               E(4) * PI * r ** 2),
                "hemisphere": Mis("used the hemisphere formula", E(2) * PI * r ** 3 / E(3)),
                "no_third": Mis("omitted the one third", E(4) * PI * r ** 3),
                "square_radius": Mis("squared the radius instead of cubing it",
                                     E(4) * PI * r ** 2 / E(3)),
                "no_cube": Mis("used the radius as it stands instead of cubing it",
                               E(4) * PI * r / E(3)),
                "flip_radius": Mis("turned the radius upside down and multiplied by π only",
                                   PI / r),
            }
        else:
            M = {
                "volume": Mis("found the volume instead of the surface area",
                              E(4) * PI * r ** 3 / E(3)),
                "pi_r2": Mis("used pi*r^2 for the whole surface", PI * r ** 2),
                "great_circle": Mis("used the great-circle circumference", E(2) * PI * r),
                "hemisphere": Mis("used the curved surface of a hemisphere only",
                                  E(2) * PI * r ** 2),
                "diameter": Mis("used the diameter as the radius",
                                E(4) * PI * (E(2) * r) ** 2),
            }
    elif shape_key == "hemisphere":
        r = g("r")
        M = {
            "whole_sphere": Mis("found the volume of the whole sphere",
                                E(4) * PI * r ** 3 / E(3)),
            "one_third": Mis("used one third instead of two thirds", PI * r ** 3 / E(3)),
            "no_fraction": Mis("omitted the fraction entirely", E(2) * PI * r ** 3),
            "half": Mis("halved πr³, taking 'half a sphere' to mean half of πr³",
                        PI * r ** 3 / E(2)),
            "square_radius": Mis("squared the radius instead of cubing it",
                                 E(2) * PI * r ** 2 / E(3)),
            "diameter_squared": Mis("used the diameter and squared it instead of cubing "
                                    "the radius", E(2) * PI * (E(2) * r) ** 2 / E(3)),
        }
    elif shape_key == "prism_base":
        B, h = g("B"), g("h")
        M = {
            "add": Mis("added the base area and the height", B + h),
            "half": Mis("halved the product as if it were a pyramid", B * h / E(2)),
            "base_only": Mis("used the base area only", B),
        }
    return M


# ---------------------------------------------------------------- FORWARD

def _with_unit(unit: Unit, measure: str, on: bool):
    """Some source items print the unit on every option -- "8 cm²" -- and some
    leave it in the stem alone. Which one an item does is the item's business,
    so it is passed in rather than guessed.
    """
    if not on:
        return None
    suffix = unit_noun(unit, measure, "abbr")
    return lambda v: f"{v.plain()} {suffix}"


def forward(rng: random.Random, seed: int, *, shape_key=None, measure=None,
            unit=None, style=None, frame=None, given_form="direct",
            fmt=None, relational=False, dims=None, delta=None,
            ask_coefficient=False, approximate=False, option_units=False,
            wrongs=None) -> Item:
    shape = SHAPES[shape_key or rng.choice(list(SHAPES))]
    measure = measure or rng.choice(list(shape.measures))
    unit = unit or rng.choice(UNITS)
    style = style or rng.choice(["words", "words", "abbr"])
    fmt = fmt or ("spr" if rng.random() < 0.2 else "mcq")
    power = {"area": 2, "surface_area": 2, "volume": 3}.get(measure, 1)

    dims = {k: E(v) for k, v in dims.items()} if dims else _pick_dims(rng, shape)
    key = shape.measures[measure](dims)
    check(shape.key, measure, dims, key)          # independent numeric route

    # --- how the dimensions are stated -------------------------------------
    phrases: list[str] = []
    first = True
    extra: dict[str, Mis] = {}
    if given_form != "direct" and shape.key in CIRCULAR:
        label, xform = GIVEN_FORMS[given_form]
        shown = xform(dims["r"])
        pw = {"diameter": 1, "base_circumference": 1, "base_area": 2}[given_form]
        phrases.append(f"{_article(label)} {label} of {_qty(shown, unit, first, style, pw)}")
        first = False
        if given_form == "diameter":
            wrong = {k: v for k, v in dims.items()}
            wrong["r"] = E(2) * dims["r"]
            extra["given_as_radius"] = Mis("used the diameter as the radius",
                                           shape.measures[measure](wrong))
        elif given_form == "base_circumference":
            extra["given_as_radius"] = Mis("used the circumference as the radius",
                                           shape.measures[measure]({**dims, "r": shown}))
        for d in shape.dims:
            if d.key != "r":
                phrases.append(f"{_article(d.label)} {d.label} of {_qty(dims[d.key], unit, first, style)}")
                first = False
    elif relational and shape.key == "rectangle":
        delta = E(delta) if delta else E(rng.randint(2, 40))
        dims["l"] = dims["w"] + delta
        key = shape.measures[measure](dims)
        check(shape.key, measure, dims, key)
        phrases = [f"a width of {_qty(dims['w'], unit, True, style)}"]
        stem = (f"The width of {shape.name()} is {_qty(dims['w'], unit, True, style)}. "
                f"The length of the rectangle is {_qty(delta, unit, False, style)} longer than "
                f"the width. What is {measure_phrase(measure, unit, style)} of this rectangle?")
        extra["given_width"] = Mis("gave the width, which the stem states, rather "
                                   "than the area it asks for", dims["w"])
        extra["double_width"] = Mis("doubled the width instead of finding the area",
                                    E(2) * dims["w"])
        extra["width_as_length"] = Mis("used the width as the length as well",
                                       dims["w"] ** 2)
        extra["delta_as_length"] = Mis("used the stated difference as the length",
                                       dims["w"] * delta)
        return _finish(rng, seed, shape, measure, dims, key, stem, fmt, unit,
                       extra, "ALG.GEO.forward.relational", wrongs=wrongs)
    else:
        for d in shape.dims:
            unit_power = 2 if d.key == "B" else 1
            phrases.append(
                f"{_article(d.label)} {d.label} of {_qty(dims[d.key], unit, first, style, unit_power)}")
            first = False

    # --- sentence frame ----------------------------------------------------
    options = ["has", "with", "the_dim_is", "object"]
    if len(shape.dims) > 1 and given_form == "direct":
        options.append("dimensions")
    frame = frame or rng.choice(options)
    if frame == "the_dim_is" and len(phrases) > 1:
        frame = "has"
    if frame == "dimensions" and (len(shape.dims) < 2 or given_form != "direct"):
        frame = "has"
    if frame == "object" and shape.key not in OBJECTS:
        frame = "has"

    if frame == "dimensions":
        # "The dimensions of a right rectangular prism are 4 inches by 5 inches by 6 inches."
        sizes = " by ".join(_qty(dims[d.key], unit, i == 0, style)
                            for i, d in enumerate(shape.dims))
        stem = (f"The dimensions of {shape.name()} are {sizes}. "
                f"What is {measure_phrase(measure, unit, style)} of the {shape.short}?")
    elif frame == "object":
        obj = rng.choice(OBJECTS[shape.key])
        shaped = "in the shape of" if shape.kind == "plane" else "shaped like"
        stem = (f"{_article(obj).capitalize()} {obj} {shaped} {shape.name()} has "
                f"{_join(phrases)}. What is {measure_phrase(measure, unit, style)} "
                f"of the {obj}?")
    elif frame == "has":
        stem = (f"{shape.name(capital=True)} has {_join(phrases)}. "
                f"What is {measure_phrase(measure, unit, style)} of the {shape.short}?")
    elif frame == "with":
        stem = (f"What is {measure_phrase(measure, unit, style)} of {shape.name()} "
                f"with {_join(phrases)}?")
    else:
        d0 = shape.dims[0]
        stem = (f"The {d0.label} of {shape.name()} is {_qty(dims[d0.key], unit, True, style)}. "
                f"What is {measure_phrase(measure, unit, style)} of the {shape.short}?")

    template = (f"GEO.{shape.key}.{measure}.forward"
                + ("" if given_form == "direct" else f".{given_form}"))
    if ask_coefficient:
        stem = stem.rsplit("What is", 1)[0] + (
            f"The {measure} of this {shape.short} is nπ "
            f"{unit_noun(unit, measure, 'abbr')}. What is the value of n?")
        template += ".coefficient"
    if approximate:
        stem = stem.replace("What is the", "Which of the following is closest to the").replace(
            ", of the", ", of the")
        template += ".approx"
    return _finish(rng, seed, shape, measure, dims, key, stem, fmt, unit, extra,
                   template, ask_coefficient=ask_coefficient, approximate=approximate,
                   option_units=option_units, wrongs=wrongs)


def _rounder(approximate):
    """How a "closest to" item rounds its options.

    `approximate=True` keeps three significant figures, which is what most of
    the source items print. One of them -- the hemisphere, 3.14 -- rounds every
    option to the nearest hundred instead, so an item may say which unit it
    rounds to and the audit re-derives it the same way.
    """
    if approximate is True:
        return lambda v: E(v.approx(3))
    unit = int(approximate)
    return lambda v: E(round(float(v) / unit) * unit)


def _finish(rng, seed, shape, measure, dims, key, stem, fmt, unit, extra_mis, template,
            ask_coefficient=False, approximate=False, option_units=False,
            wrongs=None) -> Item:
    P = {"kind": "measure_forward", "shape": shape.key, "measure": measure,
         "dims": {k: float(v) for k, v in dims.items()},
         "ask_coefficient": ask_coefficient, "approximate": approximate}
    post = (lambda v: v / PI) if ask_coefficient else (
        _rounder(approximate) if approximate else None)
    detail = ", ".join(f"{k} = {v.plain()}" for k, v in dims.items())
    exact_key = key
    if post:
        key = post(key)
    rationale = (f"{_formula_text(shape.key, measure)} with {detail} gives "
                 + (f"{exact_key.plain()}, so n = {key.plain()}." if ask_coefficient
                    else f"{exact_key.plain()}" + (f" ~= {key.plain()}." if approximate else ".")))
    if fmt == "spr":
        if not key.is_rational:
            raise ItemError("grid-in answers must be enterable as digits")
        return Item(template, f"{shape.short} {measure.replace('_', ' ')}",
                    _difficulty(shape, measure), seed, stem, "spr", key,
                    key.gridin(), rationale, params=P)
    pool = {**extra_mis, **_forward_mistakes(shape.key, measure, dims)}
    if post:
        pool = {k: Mis(m.reason, post(m.value)) for k, m in pool.items()
                if m.value is not None and (not ask_coefficient or m.value.pi_exp >= 1)}
    mistakes = pick(pool, wrongs)
    choices, latex, reasons, letter = assemble(key, mistakes, rng,
                                               fmt_value=_with_unit(unit, measure, option_units))
    return Item(template, f"{shape.short} {measure.replace('_', ' ')}",
                _difficulty(shape, measure), seed, stem, "mcq", key, letter,
                rationale, choices, reasons, latex, params=P)


FORMULA_TEXT = {
    ("square", "area"): "A = s²", ("square", "perimeter"): "P = 4s",
    ("rectangle", "area"): "A = lw", ("rectangle", "perimeter"): "P = 2(l + w)",
    ("triangle", "area"): "A = ½bh", ("parallelogram", "area"): "A = bh",
    ("circle", "area"): "A = πr²", ("circle", "circumference"): "C = 2πr",
    ("cube", "volume"): "V = e³", ("cube", "surface_area"): "SA = 6e²",
    ("rect_prism", "volume"): "V = lwh", ("rect_prism", "surface_area"): "SA = 2(lw + lh + wh)",
    ("square_prism", "volume"): "V = s²h", ("square_prism", "surface_area"): "SA = 2s² + 4sh",
    ("cylinder", "volume"): "V = πr²h", ("cylinder", "surface_area"): "SA = 2πr² + 2πrh",
    ("cone", "volume"): "V = ⅓πr²h", ("sphere", "volume"): "V = 4⁄3πr³",
    ("sphere", "surface_area"): "SA = 4πr²", ("hemisphere", "volume"): "V = ⅔πr³",
    ("prism_base", "volume"): "V = Bh",
}


def _formula_text(shape_key, measure) -> str:
    return FORMULA_TEXT[(shape_key, measure)]


def _difficulty(shape: Shape, measure: str) -> str:
    if shape.key in ("sphere", "hemisphere", "cone") or measure == "surface_area":
        return "hard"
    if shape.kind == "solid" or shape.key == "circle":
        return "medium"
    return "easy"


# ---------------------------------------------------------------- INVERSE

def _exponent_of(shape: Shape, measure: str, unknown: str, dims: dict) -> int | None:
    """How the unknown enters the formula: measure = C * x**p, or None if the
    formula is not a monomial in that variable (prism surface area, say)."""
    f = shape.measures[measure]
    try:
        base = float(f({**dims, unknown: E(1)}))
        v2 = float(f({**dims, unknown: E(2)}))
        v3 = float(f({**dims, unknown: E(3)}))
    except Exception:
        return None
    if base <= 0:
        return None
    for p in (1, 2, 3):
        if abs(v2 - base * 2 ** p) < 1e-9 * max(1, abs(v2)) and \
           abs(v3 - base * 3 ** p) < 1e-9 * max(1, abs(v3)):
            return p
    return None


def _nth_root(v: Exact, n: int) -> Exact | None:
    if n == 1:
        return v
    if n == 2:
        return v.sqrt()
    if not v.is_rational or v.coef < 0:
        return None
    num = round(v.coef.numerator ** (1 / n))
    den = round(v.coef.denominator ** (1 / n))
    cand = Exact.of(Fraction(num, den))
    return cand if cand ** n == v else None


def inverse(rng: random.Random, seed: int, *, shape_key=None, measure=None,
            unknown=None, unit=None, style=None, fmt=None, then_measure=None,
            dims=None, wrongs=None) -> Item:
    shape = SHAPES[shape_key or rng.choice(list(SHAPES))]
    measure = measure or rng.choice(list(shape.measures))
    unit = unit or rng.choice(UNITS)
    style = style or rng.choice(["words", "words", "abbr"])
    fmt = fmt or ("spr" if rng.random() < 0.25 else "mcq")

    dims = {k: E(v) for k, v in dims.items()} if dims else _pick_dims(rng, shape)
    unknown = unknown or rng.choice([d.key for d in shape.dims])
    p = _exponent_of(shape, measure, unknown, dims)
    if p is None:
        raise ItemError(f"{shape.key}.{measure} is not monomial in {unknown}")

    total = shape.measures[measure](dims)
    check(shape.key, measure, dims, total)
    known = {d.key: dims[d.key] for d in shape.dims if d.key != unknown}
    coeff = shape.measures[measure]({**dims, unknown: E(1)})

    if then_measure:                                  # e.g. surface area -> volume
        key = shape.measures[then_measure](dims)
        check(shape.key, then_measure, dims, key)
        ask = measure_phrase(then_measure, unit, style)
        find = f"What is {ask} of the {shape.short}?"
    else:
        key = dims[unknown]
        lbl = shape.dim(unknown).label
        # a base area is asked for in square units, not linear ones
        pseudo = "area" if unknown == "B" else "perimeter"
        u = unit_noun(unit, pseudo, style) if unit.abbr else unit_noun(unit, pseudo, style)
        find = f"What is the {lbl}, in {u}, of the {shape.short}?"

    P = {"kind": "measure_inverse", "shape": shape.key, "measure": measure,
         "unknown": unknown, "then_measure": then_measure,
         "dims": {k: float(v) for k, v in dims.items()}}
    given = [f"{_article(shape.dim(k).label)} {shape.dim(k).label} of "
             f"{_qty(v, unit, i == 0, style, 2 if k == 'B' else 1)}"
             for i, (k, v) in enumerate(known.items())]
    m_power = {"area": 2, "surface_area": 2, "volume": 3}.get(measure, 1)
    m_noun = {"area": "an area", "surface_area": "a surface area", "volume": "a volume",
              "perimeter": "a perimeter", "circumference": "a circumference"}[measure]
    given.append(f"{m_noun} of {_qty(total, unit, not given, style, m_power)}")
    stem = f"{shape.name(capital=True)} has {_join(given)}. {find}"

    # --- misconceptions specific to running a formula backwards -------------
    first_known = next(iter(known.values())) if known else None
    measure_noun = "area" if measure in ("area", "surface_area") else measure
    flat = shape.key in ("rectangle", "parallelogram", "square")
    pool: dict[str, Mis] = {}
    if not then_measure:
        pool = {
            "no_root": Mis("did not take the root after dividing",
                           attempt(lambda: total / coeff)),
            "divide_one": Mis("divided by only one of the known dimensions",
                              attempt(lambda: total / first_known) if first_known else None),
            "subtract": Mis(f"subtracted the known dimension from the {measure_noun} "
                            "instead of dividing",
                            attempt(lambda: total - first_known) if first_known else None),
            "given": Mis("reported a value that was given, not the one asked for",
                         first_known),
            "divide_twice": Mis("divided by twice the known dimension",
                                attempt(lambda: total / (E(2) * first_known))
                                if first_known else None),
            "double_measure": Mis(f"doubled the given {measure_noun} instead of undoing "
                                  "the formula", E(2) * total),
            "halve_measure": Mis(
                f"halved the {measure_noun} as though the figure were a triangle" if
                flat and measure == "area" else
                f"halved the given {measure_noun} instead of dividing by the known "
                "dimension", total / E(2)),
            "add_known": Mis("added the known dimensions instead of dividing the "
                             f"{measure_noun} by them",
                             attempt(lambda: sum(known.values(), E(0)))
                             if len(known) > 1 else None),
            "multiply_known": Mis("multiplied the known dimensions instead of dividing "
                                  f"the {measure_noun} by them", coeff if p == 1 else None),
            "subtract_coef": Mis(f"subtracted the height from the {measure_noun}, "
                                 "leaving π out of it",
                                 attempt(lambda: E(total.coef) - first_known)
                                 if first_known is not None and not total.is_rational
                                 else None),
        }
        if p == 2:
            pool["halve"] = Mis("halved after dividing instead of taking the square root",
                                attempt(lambda: total / coeff / E(2)))
            pool["invert_divide"] = Mis(
                f"divided the coefficient by the {measure_noun} instead of the "
                f"{measure_noun} by the coefficient",
                attempt(lambda: (coeff / total).sqrt()))
            pool["over_four"] = Mis(f"divided the {measure_noun} by 4, as though it "
                                    "were a perimeter", total / E(4))
            if unknown == "r":
                pool["diameter"] = Mis("gave the diameter instead of the radius",
                                       E(2) * key)
        if p == 3:
            pool["over_three"] = Mis("divided by 3 instead of taking the cube root",
                                     key ** 3 / E(3))
    else:
        pool = {
            "stopped": Mis("stopped at the edge length instead of the requested measure",
                           dims[unknown]),
            "unchanged": Mis("used the given measure unchanged", total),
            "over_faces": Mis("divided the given measure by the number of faces",
                              attempt(lambda: total / E(6))),
        }
    pool = {k: m for k, m in pool.items() if m.value is not None}
    for k, m in _forward_mistakes(shape.key, then_measure or measure, dims).items():
        pool.setdefault(k, m)
    mistakes = pick(pool, wrongs)

    detail = ", ".join(f"{k} = {v.plain()}" for k, v in known.items())
    rationale = (f"{_formula_text(shape.key, measure)} with {detail or 'the given measure'} "
                 f"gives {unknown} = {dims[unknown].plain()}"
                 + (f", so {_formula_text(shape.key, then_measure)} = {key.plain()}." if then_measure else "."))
    template = (f"GEO.{shape.key}.{measure}.inverse.{unknown}"
                + (f".then_{then_measure}" if then_measure else ""))
    skill = f"{shape.short} {measure.replace('_', ' ')}"
    if fmt == "spr":
        if not key.is_rational:
            raise ItemError("grid-in answers must be enterable as digits")
        return Item(template, skill, _difficulty(shape, measure), seed, stem, "spr",
                    key, key.gridin(), rationale, params=P)
    choices, latex, reasons, letter = assemble(key, mistakes, rng,
                                               fmt_value=decimal_text)
    return Item(template, skill, _difficulty(shape, measure), seed, stem, "mcq", key,
                letter, rationale, choices, reasons, latex, params=P)
