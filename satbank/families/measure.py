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

from ..exact import E, PI, Exact
from ..item import Item, ItemError, Mis, assemble
from ..shapes import SHAPES, UNITS, Shape, Unit, measure_phrase, unit_noun
from ..verify import check

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

def _forward_mistakes(shape_key: str, measure: str, p: dict) -> list[Mis]:
    """Wrong options a real student produces. Drawn from the source distractors."""
    g = p.get
    M: list[Mis] = []
    if shape_key == "square":
        s = g("s")
        if measure == "area":
            M += [Mis("found the perimeter instead of the area", E(4) * s),
                  Mis("doubled the side instead of squaring it", E(2) * s),
                  Mis("squared the perimeter", (E(4) * s) ** 2)]
        else:
            M += [Mis("found the area instead of the perimeter", s ** 2),
                  Mis("added only two sides", E(2) * s),
                  Mis("used three sides", E(3) * s)]
    elif shape_key == "rectangle":
        l, w = g("l"), g("w")
        if measure == "area":
            M += [Mis("added the dimensions instead of multiplying", l + w),
                  Mis("found the perimeter instead of the area", E(2) * (l + w)),
                  Mis("squared the sum of the dimensions", (l + w) ** 2),
                  Mis("doubled the product", E(2) * l * w)]
        else:
            M += [Mis("found the area instead of the perimeter", l * w),
                  Mis("added the two given sides only", l + w),
                  Mis("doubled the length only", E(2) * l),
                  Mis("treated the rectangle as a square", E(4) * l)]
    elif shape_key in ("triangle", "parallelogram"):
        b, h = g("b"), g("h")
        if shape_key == "triangle":
            M += [Mis("forgot to multiply by one half", b * h),
                  Mis("added the base and height", b + h),
                  Mis("halved twice", b * h / E(4)),
                  Mis("doubled instead of halving", E(2) * b * h)]
        else:
            M += [Mis("multiplied by one half as if it were a triangle", b * h / E(2)),
                  Mis("added the base and height", b + h),
                  Mis("found the perimeter of a rectangle with those sides", E(2) * (b + h))]
    elif shape_key == "circle":
        r = g("r")
        if measure == "area":
            M += [Mis("found the circumference instead of the area", E(2) * PI * r),
                  Mis("forgot to square the radius", PI * r),
                  Mis("used the diameter as the radius", PI * (E(2) * r) ** 2)]
        else:
            M += [Mis("found the area instead of the circumference", PI * r ** 2),
                  Mis("used pi*r instead of 2*pi*r", PI * r),
                  Mis("used the diameter as the radius", E(4) * PI * r)]
    elif shape_key == "cube":
        e = g("e")
        if measure == "volume":
            M += [Mis("found the surface area instead of the volume", E(6) * e ** 2),
                  Mis("squared the edge instead of cubing it", e ** 2),
                  Mis("multiplied the edge by 3", E(3) * e),
                  Mis("multiplied the edge by 6", E(6) * e)]
        else:
            M += [Mis("found the volume instead of the surface area", e ** 3),
                  Mis("counted four faces instead of six", E(4) * e ** 2),
                  Mis("found the area of one face only", e ** 2)]
    elif shape_key == "rect_prism":
        l, w, h = g("l"), g("w"), g("h")
        faces = l * w + l * h + w * h
        if measure == "volume":
            M += [Mis("found the area of the base only", l * w),
                  Mis("found the surface area instead of the volume", E(2) * faces),
                  Mis("added the three dimensions", l + w + h),
                  Mis("summed the three distinct face areas", faces)]
        else:
            M += [Mis("found the volume instead of the surface area", l * w * h),
                  Mis("counted each pair of faces only once", faces),
                  Mis("used one face only", l * w),
                  Mis("added the dimensions and doubled", E(2) * (l + w + h))]
    elif shape_key == "square_prism":
        s, h = g("s"), g("h")
        if measure == "volume":
            M += [Mis("did not square the base edge", s * h),
                  Mis("found the area of the base only", s ** 2),
                  Mis("squared the height instead of the base edge", s * h ** 2)]
        else:
            M += [Mis("found the volume instead of the surface area", s ** 2 * h),
                  Mis("left out the two bases", E(4) * s * h),
                  Mis("left out the lateral faces", E(2) * s ** 2)]
    elif shape_key == "cylinder":
        r, h = g("r"), g("h")
        if measure == "volume":
            M += [Mis("used the diameter in place of the radius", PI * (E(2) * r) ** 2 * h),
                  Mis("forgot to square the radius", PI * r * h),
                  Mis("found the area of the base only", PI * r ** 2),
                  Mis("found the lateral surface area", E(2) * PI * r * h),
                  Mis("swapped the radius and the height", PI * h ** 2 * r)]
        else:
            M += [Mis("found the volume instead of the surface area", PI * r ** 2 * h),
                  Mis("left out the two bases", E(2) * PI * r * h),
                  Mis("left out the lateral surface", E(2) * PI * r ** 2)]
    elif shape_key == "cone":
        r, h = g("r"), g("h")
        M += [Mis("used the cylinder formula, omitting the one third", PI * r ** 2 * h),
              Mis("halved instead of taking one third", PI * r ** 2 * h / E(2)),
              Mis("forgot to square the radius", PI * r * h / E(3)),
              Mis("used the diameter in place of the radius", PI * (E(2) * r) ** 2 * h / E(3))]
    elif shape_key == "sphere":
        r = g("r")
        if measure == "volume":
            M += [Mis("found the surface area instead of the volume", E(4) * PI * r ** 2),
                  Mis("used the hemisphere formula", E(2) * PI * r ** 3 / E(3)),
                  Mis("omitted the one third", E(4) * PI * r ** 3),
                  Mis("squared the radius instead of cubing it", E(4) * PI * r ** 2 / E(3))]
        else:
            M += [Mis("found the volume instead of the surface area", E(4) * PI * r ** 3 / E(3)),
                  Mis("used pi*r^2 for the whole surface", PI * r ** 2),
                  Mis("used the great-circle circumference", E(2) * PI * r)]
    elif shape_key == "hemisphere":
        r = g("r")
        M += [Mis("found the volume of the whole sphere", E(4) * PI * r ** 3 / E(3)),
              Mis("used one third instead of two thirds", PI * r ** 3 / E(3)),
              Mis("omitted the fraction entirely", E(2) * PI * r ** 3)]
    elif shape_key == "prism_base":
        B, h = g("B"), g("h")
        M += [Mis("added the base area and the height", B + h),
              Mis("halved the product as if it were a pyramid", B * h / E(2)),
              Mis("used the base area only", B)]
    return M


# ---------------------------------------------------------------- FORWARD

def forward(rng: random.Random, seed: int, *, shape_key=None, measure=None,
            unit=None, style=None, frame=None, given_form="direct",
            fmt=None, relational=False) -> Item:
    shape = SHAPES[shape_key or rng.choice(list(SHAPES))]
    measure = measure or rng.choice(list(shape.measures))
    unit = unit or rng.choice(UNITS)
    style = style or rng.choice(["words", "words", "abbr"])
    fmt = fmt or ("spr" if rng.random() < 0.2 else "mcq")
    power = {"area": 2, "surface_area": 2, "volume": 3}.get(measure, 1)

    dims = _pick_dims(rng, shape)
    key = shape.measures[measure](dims)
    check(shape.key, measure, dims, key)          # independent numeric route

    # --- how the dimensions are stated -------------------------------------
    phrases: list[str] = []
    first = True
    extra_mis: list[Mis] = []
    if given_form != "direct" and shape.key in CIRCULAR:
        label, xform = GIVEN_FORMS[given_form]
        shown = xform(dims["r"])
        pw = {"diameter": 1, "base_circumference": 1, "base_area": 2}[given_form]
        phrases.append(f"{_article(label)} {label} of {_qty(shown, unit, first, style, pw)}")
        first = False
        if given_form == "diameter":
            wrong = {k: v for k, v in dims.items()}
            wrong["r"] = E(2) * dims["r"]
            extra_mis.append(Mis("used the diameter as the radius",
                                 shape.measures[measure](wrong)))
        elif given_form == "base_circumference":
            extra_mis.append(Mis("used the circumference as the radius",
                                 shape.measures[measure]({**dims, "r": shown})))
        for d in shape.dims:
            if d.key != "r":
                phrases.append(f"{_article(d.label)} {d.label} of {_qty(dims[d.key], unit, first, style)}")
                first = False
    elif relational and shape.key == "rectangle":
        delta = E(rng.randint(2, 40))
        dims["l"] = dims["w"] + delta
        key = shape.measures[measure](dims)
        check(shape.key, measure, dims, key)
        phrases = [f"a width of {_qty(dims['w'], unit, True, style)}"]
        stem = (f"The width of {shape.name()} is {_qty(dims['w'], unit, True, style)}. "
                f"The length of the rectangle is {_qty(delta, unit, False, style)} longer than "
                f"the width. What is {measure_phrase(measure, unit, style)} of this rectangle?")
        extra_mis += [Mis("used the width as the length as well", dims["w"] ** 2),
                      Mis("added the width and the length", dims["w"] + dims["l"]),
                      Mis("used the stated difference as the length", dims["w"] * delta)]
        return _finish(rng, seed, shape, measure, dims, key, stem, fmt, unit,
                       extra_mis, "ALG.GEO.forward.relational")
    else:
        for d in shape.dims:
            unit_power = 2 if d.key == "B" else 1
            phrases.append(
                f"{_article(d.label)} {d.label} of {_qty(dims[d.key], unit, first, style, unit_power)}")
            first = False

    # --- sentence frame ----------------------------------------------------
    frame = frame or rng.choice(["has", "with", "the_dim_is"])
    if frame == "the_dim_is" and len(phrases) > 1:
        frame = "has"
    if frame == "has":
        stem = (f"{shape.name(capital=True)} has {_join(phrases)}. "
                f"What is {measure_phrase(measure, unit, style)} of the {shape.short}?")
    elif frame == "with":
        stem = (f"What is {measure_phrase(measure, unit, style)} of {shape.name()} "
                f"with {_join(phrases)}?")
    else:
        d0 = shape.dims[0]
        stem = (f"The {d0.label} of {shape.name()} is {_qty(dims[d0.key], unit, True, style)}. "
                f"What is {measure_phrase(measure, unit, style)} of the {shape.short}?")

    return _finish(rng, seed, shape, measure, dims, key, stem, fmt, unit, extra_mis,
                   f"GEO.{shape.key}.{measure}.forward"
                   + ("" if given_form == "direct" else f".{given_form}"))


def _finish(rng, seed, shape, measure, dims, key, stem, fmt, unit, extra_mis, template) -> Item:
    detail = ", ".join(f"{k} = {v.plain()}" for k, v in dims.items())
    rationale = f"{_formula_text(shape.key, measure)} with {detail} gives {key.plain()}."
    if fmt == "spr":
        if not key.is_rational:
            raise ItemError("grid-in answers must be enterable as digits")
        return Item(template, f"{shape.short} {measure.replace('_', ' ')}",
                    _difficulty(shape, measure), seed, stem, "spr", key,
                    key.gridin(), rationale)
    mistakes = extra_mis + _forward_mistakes(shape.key, measure, dims)
    choices, latex, reasons, letter = assemble(key, mistakes, rng)
    return Item(template, f"{shape.short} {measure.replace('_', ' ')}",
                _difficulty(shape, measure), seed, stem, "mcq", key, letter,
                rationale, choices, reasons, latex)


FORMULA_TEXT = {
    ("square", "area"): "A = s^2", ("square", "perimeter"): "P = 4s",
    ("rectangle", "area"): "A = lw", ("rectangle", "perimeter"): "P = 2(l + w)",
    ("triangle", "area"): "A = (1/2)bh", ("parallelogram", "area"): "A = bh",
    ("circle", "area"): "A = pi*r^2", ("circle", "circumference"): "C = 2*pi*r",
    ("cube", "volume"): "V = e^3", ("cube", "surface_area"): "SA = 6e^2",
    ("rect_prism", "volume"): "V = lwh", ("rect_prism", "surface_area"): "SA = 2(lw + lh + wh)",
    ("square_prism", "volume"): "V = s^2*h", ("square_prism", "surface_area"): "SA = 2s^2 + 4sh",
    ("cylinder", "volume"): "V = pi*r^2*h", ("cylinder", "surface_area"): "SA = 2*pi*r^2 + 2*pi*r*h",
    ("cone", "volume"): "V = (1/3)pi*r^2*h", ("sphere", "volume"): "V = (4/3)pi*r^3",
    ("sphere", "surface_area"): "SA = 4*pi*r^2", ("hemisphere", "volume"): "V = (2/3)pi*r^3",
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
            unknown=None, unit=None, style=None, fmt=None, then_measure=None) -> Item:
    shape = SHAPES[shape_key or rng.choice(list(SHAPES))]
    measure = measure or rng.choice(list(shape.measures))
    unit = unit or rng.choice(UNITS)
    style = style or rng.choice(["words", "words", "abbr"])
    fmt = fmt or ("spr" if rng.random() < 0.25 else "mcq")

    dims = _pick_dims(rng, shape)
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
        u = unit_noun(unit, "perimeter", style) if unit.abbr else "units"
        find = f"What is the {lbl}, in {u}, of the {shape.short}?"

    given = [f"{_article(shape.dim(k).label)} {shape.dim(k).label} of "
             f"{_qty(v, unit, i == 0, style, 2 if k == 'B' else 1)}"
             for i, (k, v) in enumerate(known.items())]
    m_power = {"area": 2, "surface_area": 2, "volume": 3}.get(measure, 1)
    m_noun = {"area": "an area", "surface_area": "a surface area", "volume": "a volume",
              "perimeter": "a perimeter", "circumference": "a circumference"}[measure]
    given.append(f"{m_noun} of {_qty(total, unit, not given, style, m_power)}")
    stem = f"{shape.name(capital=True)} has {_join(given)}. {find}"

    # --- misconceptions specific to running a formula backwards -------------
    mistakes: list[Mis] = []
    if not then_measure:
        mistakes += [Mis("did not take the root after dividing", total / coeff),
                     Mis("divided by only one of the known dimensions",
                         total / next(iter(known.values())) if known else None),
                     Mis("subtracted the known dimension instead of dividing",
                         total - next(iter(known.values())) if known else None),
                     Mis("reported a value that was given, not the one asked for",
                         next(iter(known.values())) if known else None),
                     Mis("divided by twice the known dimension",
                         total / (E(2) * next(iter(known.values()))) if known else None)]
        if p == 2:
            mistakes.append(Mis("halved instead of taking the square root", key * E(2)))
        if p == 3:
            mistakes.append(Mis("divided by 3 instead of taking the cube root", key ** 3 / E(3)))
    else:
        mistakes += [Mis("stopped at the edge length instead of the requested measure", dims[unknown]),
                     Mis("used the given measure unchanged", total),
                     Mis("divided the given measure by the number of faces", total / E(6))]
    mistakes = [m for m in mistakes if m.value is not None]
    mistakes += _forward_mistakes(shape.key, then_measure or measure, dims)

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
                    key, key.gridin(), rationale)
    choices, latex, reasons, letter = assemble(key, mistakes, rng)
    return Item(template, skill, _difficulty(shape, measure), seed, stem, "mcq", key,
                letter, rationale, choices, reasons, latex)
