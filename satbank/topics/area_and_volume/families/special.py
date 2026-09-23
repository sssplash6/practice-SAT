"""Two smaller families that the source set nevertheless leans on.

EXPRESSION  the options are expressions, not numbers -- the item tests whether
            the student can *write* the formula, not evaluate it.
CONTEXT     a real-world wrapper: a partially filled can, two objects whose
            areas combine, a missing side, a container resized by a percent.
"""

from __future__ import annotations

import math
import random
from fractions import Fraction

from ....exact import E, PI, Exact
from ....figures import triangle_xyz
from ....item import Item, ItemError, Mis, assemble, assemble_text
from ....shapes import SHAPES, UNITS, Unit, measure_phrase, unit_noun
from ..kit import decimal_text, gridin_wrongs, pick

__all__ = ["expression_measure", "symbolic_volume", "remaining_volume",
           "combined_area", "missing_side", "container_percent"]


# ------------------------------------------------------------- EXPRESSION

def expression_measure(rng: random.Random, seed: int, *, shape=None, measure=None,
                       dims=None, unit=None, wrongs=None) -> Item:
    """'Which expression gives the area?' -- options are unevaluated products."""
    shape = shape or rng.choice(["rectangle", "square"])
    unit = unit or rng.choice(UNITS)
    measure = measure or rng.choice(["area", "perimeter"])
    if shape == "square":
        s = (dims or {}).get("s") or rng.randint(5, 99)
        stem = (f"The length of each side of a square is {s} {unit.many()}"
                f"{f' ({unit.abbr})' if unit.abbr else ''}. Which expression gives "
                f"{measure_phrase(measure, unit, 'abbr')} of the square?")
        if measure == "area":
            key, key_val = f"{s} * {s}", s * s
            wrong = {
                "double_side": (Mis("doubled the side instead of squaring it",
                                    f"2 * {s}"), 2 * s),
                "perimeter": (Mis("found the perimeter", f"4 * {s}"), 4 * s),
                "double_area": (Mis("doubled the squared side", f"2 * {s} * {s}"),
                                2 * s * s)}
        else:
            key, key_val = f"4 * {s}", 4 * s
            wrong = {
                "area": (Mis("squared the side, giving the area", f"{s} * {s}"), s * s),
                "two_sides": (Mis("used two sides only", f"2 * {s}"), 2 * s),
                "double_area": (Mis("doubled the area", f"2 * {s} * {s}"), 2 * s * s)}
    else:
        l = (dims or {}).get("l") or rng.randint(2, 60)
        w = (dims or {}).get("w") or rng.randint(2, 60)
        stem = (f"A rectangle has a length of {l} {unit.many() if unit.abbr else 'units'} and a "
                f"width of {w} {unit.many() if unit.abbr else 'units'}. Which expression gives "
                f"{measure_phrase(measure, unit, 'words')} of this rectangle?")
        if measure == "area":
            key, key_val = f"{l} * {w}", l * w
            wrong = {
                "perimeter": (Mis("found the perimeter", f"2({l} + {w})"), 2 * (l + w)),
                "double": (Mis("doubled the area", f"2({l} * {w})"), 2 * l * w),
                "add": (Mis("added the dimensions", f"{l} + {w}"), l + w)}
        else:
            key, key_val = f"2({l} + {w})", 2 * (l + w)
            wrong = {
                "area": (Mis("found the area", f"{l} * {w}"), l * w),
                "add": (Mis("added the two given sides only", f"{l} + {w}"), l + w),
                "double_area": (Mis("doubled the area", f"2({l} * {w})"), 2 * l * w)}
    P = {"kind": "expression_measure", "shape": shape, "measure": measure,
         "s": locals().get("s"), "l": locals().get("l"), "w": locals().get("w")}
    # Two options that evaluate to the same number are two answers to "which
    # expression gives the area", whatever they look like on the page: at
    # l = w = 2, "2 + 2" and "2 * 2" are both the area.
    values = [key_val] + [v for _, v in wrong.values()]
    if len(set(values)) != len(values):
        raise ItemError("two of these expressions have the same value")
    wrong = {k: m for k, (m, _) in wrong.items()}
    choices, reasons, letter = assemble_text(key, pick(wrong, wrongs), rng)
    return Item("GEO.expression.measure", f"{shape} {measure}", "easy", seed, stem, "mcq",
                E(0), letter, f"The correct expression is {key}.", choices, reasons, choices, params=P)


def symbolic_volume(rng: random.Random, seed: int, *, c=None, relation=None,
                    solid=None, wrongs=None) -> Item:
    """A solid whose height is stated in terms of another dimension; expand V.

    The tested skill is translating a sentence into an expression and
    distributing, so the solid and the relation both vary.
    """
    c = c or rng.randint(2, 16)
    solid = solid or rng.choice(["cylinder", "cylinder", "square_prism"])
    relation = relation or rng.choice(["longer", "times", "shorter", "twice_plus"])
    trade = rng.choice(["containers", "canisters", "tins", "boxes"]) if solid == "square_prism" \
        else rng.choice(["containers", "canisters", "drums", "tubes"])

    if solid == "cylinder":
        var, unit, word = "r", "cubic inches", "radius"
        forms = {
            "longer":     (f"{c} inches longer than the radius", f"V = πr³ + {c}πr²",
                           lambda r: math.pi * r * r * (r + c)),
            "times":      (f"{c} times the radius", f"V = {c}πr³",
                           lambda r: math.pi * r * r * (c * r)),
            "shorter":    (f"{c} inches shorter than twice the radius",
                           f"V = 2πr³ - {c}πr²", lambda r: math.pi * r * r * (2 * r - c)),
            "twice_plus": (f"{c} inches more than twice the radius",
                           f"V = 2πr³ + {c}πr²", lambda r: math.pi * r * r * (2 * r + c)),
        }
        wrong_pool = {
            "times": (f"V = {c}πr³", "multiplied instead of expanding the sum",
                      lambda r: c * math.pi * r ** 3),
            "no_square": (f"V = πr² + {c}πr",
                          "did not square the radius in the second term",
                          lambda r: math.pi * r * r + c * math.pi * r),
            "doubled": ("V = π(2r)³",
                        "doubled the radius instead of using the stated height",
                        lambda r: math.pi * (2 * r) ** 3),
            "minus": (f"V = πr³ - {c}πr²", "subtracted where the height was added",
                      lambda r: math.pi * r ** 3 - c * math.pi * r * r),
            "const": (f"V = πr² + {c}", "added the constant without the base area",
                      lambda r: math.pi * r * r + c),
        }
    else:
        var, unit, word = "s", "cubic centimeters", "base edge"
        forms = {
            "longer":     (f"{c} centimeters longer than an edge of the square base",
                           f"V = s³ + {c}s²", lambda x: x * x * (x + c)),
            "times":      (f"{c} times the length of an edge of the square base",
                           f"V = {c}s³", lambda x: x * x * (c * x)),
            "shorter":    (f"{c} centimeters shorter than twice an edge of the square base",
                           f"V = 2s³ - {c}s²", lambda x: x * x * (2 * x - c)),
            "twice_plus": (f"{c} centimeters more than twice an edge of the square base",
                           f"V = 2s³ + {c}s²", lambda x: x * x * (2 * x + c)),
        }
        wrong_pool = {
            "times": (f"V = {c}s³", "multiplied instead of expanding the sum",
                      lambda x: c * x ** 3),
            "no_square": (f"V = s² + {c}s", "did not square the edge in the second term",
                          lambda x: x * x + c * x),
            "cubed": (f"V = (s + {c})³", "cubed the height instead of using it once",
                      lambda x: (x + c) ** 3),
            "minus": (f"V = s³ - {c}s²", "subtracted where the height was added",
                      lambda x: x ** 3 - c * x * x),
            "surface": (f"V = 3s² + {c}s", "used the surface area rather than the volume",
                        lambda x: 3 * x * x + c * x),
        }

    phrase, key, key_fn = forms[relation]
    shape_name = ("right cylindrical" if solid == "cylinder" else "right square prism")
    stem = (f"A manufacturer determined that {shape_name} {trade} with a height that is "
            f"{phrase} offer the optimal number to be displayed on a shelf. Which of the "
            f"following expresses the volume V, in {unit}, of such {trade}, where {var} is the "
            f"{word}?")
    # An option that is a different expression but the same function is a
    # second right answer: π(2r)³ is 8πr³, which is exactly what the key says
    # when the height is stated as 8 times the radius.
    probe = (2.0, 3.0, 5.0, 7.0)
    pool = {k: Mis(why, txt) for k, (txt, why, fn) in wrong_pool.items()
            if any(abs(fn(x) - key_fn(x)) > 1e-12 * abs(key_fn(x)) for x in probe)}
    order = list(pool) if wrongs is None else list(wrongs)
    if wrongs is None:
        rng.shuffle(order)
    rationale = f"Substituting the stated height into the volume formula and expanding gives {key}."
    P = {"kind": "symbolic_volume", "c": c, "relation": relation, "solid": solid}
    choices, reasons, letter = assemble_text(key, pick(pool, order), rng)
    return Item("GEO.expression.symbolic_volume", f"{solid} volume", "hard", seed, stem, "mcq",
                E(0), letter, rationale, choices, reasons, choices, params=P)


# ---------------------------------------------------------------- CONTEXT

def remaining_volume(rng: random.Random, seed: int, *, base=None, h=None, filled=None,
                     wrongs=None) -> Item:
    """A sealed can: total volume minus the poured liquid is the solid contents."""
    base = E(base or rng.choice([40, 50, 60, 75, 80, 90, 100]))
    h = E(h or rng.randint(6, 15))
    total = base * h
    lo = max(5, int(float(total) * 0.1) // 5 * 5)
    hi = max(lo + 5, int(float(total) * 0.5))
    filled = E(filled or rng.randrange(lo, hi, 5))
    key = total - filled
    P = {"kind": "remaining_volume", "base": float(base), "h": float(h),
         "filled": float(filled)}
    contents = rng.choice([("fruit", "syrup"), ("olives", "brine"), ("beans", "sauce")])
    stem = (f"A cylindrical can containing pieces of {contents[0]} is filled to the top with "
            f"{contents[1]} before being sealed. The base of the can has an area of "
            f"{base.plain()} cm², and the height of the can is {h.plain()} cm. If "
            f"{filled.plain()} cm³ of {contents[1]} is needed to fill the can to the top, which "
            f"of the following is closest to the total volume of the pieces of {contents[0]} in "
            f"the can?")
    pool = {
        "whole": Mis("gave the volume of the whole can", total),
        "add_filled": Mis("added the base area to the poured volume", base + filled),
        "base_over_h": Mis("divided the base area by the height instead of multiplying",
                           base / h),
        "minus_base": Mis("subtracted the base area instead of the poured volume",
                          total - base),
    }
    rationale = (f"The can holds {base.plain()} × {h.plain()} = {total.plain()} cm³; the "
                 f"pieces take up {total.plain()} - {filled.plain()} = {key.plain()} cm³.")
    # the source item prints the unit on every option, and so does this
    choices, latex, reasons, letter = assemble(key, pick(pool, wrongs), rng,
                                               fmt_value=lambda v: f"{decimal_text(v)} cm³")
    return Item("GEO.context.remaining_volume", "volume in context", "medium", seed, stem,
                "mcq", key, letter, rationale, choices, reasons, latex, params=P)


def combined_area(rng: random.Random, seed: int, *, tri_area=None, side=None,
                  pair=None, wrongs=None) -> Item:
    """Two figures, one area given directly and one to be computed, then summed."""
    pair = pair or rng.choice(["triangle_square", "triangle_square",
                               "rectangle_square", "square_triangle"])
    tri = E(tri_area or rng.randrange(12, 240, 2))
    s = E(side or rng.randint(3, 20))
    first, second = {"triangle_square": ("Triangle R", "Square S"),
                     "rectangle_square": ("Rectangle R", "Square S"),
                     "square_triangle": ("Square R", "Square S")}[pair]
    key = tri + s ** 2
    P = {"kind": "combined_area", "tri": float(tri), "s": float(s)}
    lower = (lambda n: n[0].lower() + n[1:])          # "Triangle R" -> "triangle R"
    noun = first.split()[0].lower()
    stem = (f"{first} has an area of {tri.plain()} square centimeters (cm²). {second} has "
            f"side lengths of {s.plain()} cm. What is the total area of {lower(first)} and "
            f"{lower(second)}, in cm²?")
    pool = {
        "plus_side": Mis("added the side length instead of the area of the square", tri + s),
        "half_then_side": Mis("halved the given area and added the side length instead "
                              "of its square", tri / E(2) + s),
        "half_sum": Mis("halved both given measures before adding them",
                        tri / E(2) + s / E(2)),
        "half_area": Mis("halved the given area before adding", tri / E(2) + s ** 2),
        "plus_perimeter": Mis("added the perimeter of the square", tri + E(4) * s),
        "first_only": Mis(f"gave the area of the {noun} only", tri),
    }
    rationale = (f"The square has area {s.plain()}² = {(s**2).plain()}, so the total is "
                 f"{tri.plain()} + {(s**2).plain()} = {key.plain()}.")
    choices, latex, reasons, letter = assemble(key, pick(pool, wrongs), rng)
    return Item("GEO.context.combined_area", "combined area", "easy", seed, stem, "mcq", key,
                letter, rationale, choices, reasons, latex, params=P)


def missing_side(rng: random.Random, seed: int, *, sides=None, style=None,
                 wrongs=None) -> Item:
    """Perimeter and two sides given; find the third. Must close as a triangle."""
    style = style or ("labelled" if sides else
                      rng.choices(["labelled", "isosceles"], weights=[3, 1])[0])
    if sides:
        x, y, z = sides
    else:
        for _ in range(300):
            if style == "isosceles":
                x = y = rng.randint(4, 30)
                z = rng.randint(3, 2 * x - 1)
                if z != x:
                    break
            else:
                x, y, z = (rng.randint(3, 30) for _ in range(3))
                if x + y > z and x + z > y and y + z > x and len({x, y, z}) == 3:
                    break
        else:
            raise ItemError("no valid triangle")
    p = x + y + z
    P = {"kind": "missing_side", "x": x, "y": y, "z": z, "perimeter": p}
    key = E(z)
    if style == "isosceles":
        unit = rng.choice(["centimeters", "inches", "units"])
        stem = (f"An isosceles triangle has a perimeter of {p} {unit}. Each of its two "
                f"congruent sides has a length of {x} {unit}. What is the length, in {unit}, "
                f"of the third side?")
    else:
        stem = (f"The triangle shown has a perimeter of {p} units. If x = {x} units and y = {y} "
                f"units, what is the value of z, in units?")
    pool = {
        "given_y": Mis("reported one of the given sides", E(y)),
        "given_x": Mis("reported the other given side", E(x)),
        "add": Mis("added the two given sides instead of subtracting", E(x + y)),
        "minus_one": Mis("subtracted only one of the given sides", E(p - x)),
    }
    rationale = f"The third side is {p} - {x} - {y} = {z}."
    choices, latex, reasons, letter = assemble(key, pick(pool, wrongs), rng)
    fig = None if style == "isosceles" else triangle_xyz()
    return Item("GEO.context.missing_side", "triangle perimeter", "easy", seed, stem, "mcq",
                key, letter, rationale, choices, reasons, latex, figure=fig, params=P)


def container_percent(rng: random.Random, seed: int, *, rA=None, pct=None, h=None,
                      dim=None, up=None, ask=None, wrongs=None) -> Item:
    """One container's dimension differs from another's by a percent.

    Which dimension moves matters: a percent on the radius is squared into the
    volume, a percent on the height is not. That asymmetry is the item.
    """
    pct = pct or rng.choice([10, 20, 25, 30, 40, 50, 60, 75, 100])
    up = rng.random() < 0.75 if up is None else up
    dim = dim or rng.choices(["radius", "height", "both"], weights=[5, 3, 2])[0]
    ask = ask or rng.choices(["volume", "times"], weights=[4, 1])[0]
    ratio = Fraction(100 + pct, 100) if up else Fraction(100 - pct, 100)
    step = ratio.denominator
    rA = E(rA or rng.randrange(step * 2, step * 14, step))
    h = E(h or rng.randrange(step * 2, step * 24, step))

    rB = rA * E(ratio) if dim in ("radius", "both") else rA
    hB = h * E(ratio) if dim in ("height", "both") else h
    vA, vB = PI * rA ** 2 * h, PI * rB ** 2 * hB
    factor = (vB / vA).coef
    key = vB if ask == "volume" else E(factor)
    word = "longer" if up else "shorter"
    if dim == "height":
        word = "taller" if up else "shorter"

    which = {"radius": "the radius of container B is", "height": "the height of container B is",
             "both": "both the radius and the height of container B are"}[dim]
    fixed = {"radius": f"each have a height of {h.plain()} centimeters",
             "height": f"each have a radius of {rA.plain()} centimeters",
             "both": f"are similar in shape"}[dim]
    lead = (f"A manufacturing company produces two sizes of cylindrical containers that "
            f"{fixed}. "
            + (f"The radius of container A is {rA.plain()} centimeters"
               if dim != "height" else
               f"The height of container A is {h.plain()} centimeters")
            + (f" and its height is {h.plain()} centimeters" if dim == "both" else "")
            + f", and {which} {pct}% {word} than that of container A.")
    stem = lead + (" What is the volume, in cubic centimeters, of container B?" if ask == "volume"
                   else " The volume of container B is k times the volume of container A. "
                        "What is the value of k?")

    if ask == "volume":
        r2 = rA * E(ratio ** 2) if dim in ("radius", "both") else rA
        h2 = h * E(ratio ** 2) if dim in ("height", "both") else h
        pool = {
            "vol_percent": Mis("applied the percent to the volume rather than to the "
                               "dimension", vA * E(ratio)),
            "twice_volume": Mis(f"changed the volume by {pct}% as well as the {dim}",
                                vA * E(ratio ** 2) * E(ratio)),
            "twice_radius": Mis(f"applied the {pct}% change to the {dim} twice",
                                PI * r2 ** 2 * h2),
            "A_dims": Mis("used container A's dimensions", vA),
        }
    else:
        pool = {
            "linear": Mis("used the dimension ratio without squaring the radius", E(ratio)),
            "square": Mis("squared the ratio when only the height changed", E(ratio ** 2)),
            "cube": Mis("cubed the ratio as if every dimension changed", E(ratio ** 3)),
            "unchanged": Mis("left the volume unchanged", E(1)),
        }
    rationale = (f"Volume scales by {factor} here, so V_B = {vB.plain()}"
                 + (f" and k = {key.plain()}." if ask == "times" else "."))
    P = {"kind": "container_percent", "rA": float(rA), "pct": pct, "h": float(h),
         "dim": dim, "up": up, "ask": ask}
    choices, latex, reasons, letter = assemble(key, pick(pool, wrongs), rng)
    return Item("GEO.context.container_percent", "cylinder volume", "hard", seed, stem, "mcq",
                key, letter, rationale, choices, reasons, latex, params=P)


def _radical_pi(v: Exact) -> str:
    """√(2π), the way the source prints it, rather than √2√π.

    The two spell the same number; this is the only item in the topic whose
    options put a whole product under one radical, so the rendering is the
    item's, not the engine's.
    """
    if v.pi_exp == Fraction(1, 2) and v.rad != 1:
        n, d = abs(v.coef.numerator), v.coef.denominator
        body = ("" if n == 1 else f"{n:,}") + f"√({v.rad}π)"
        sign = "-" if v.coef < 0 else ""
        return f"{sign}{body}" if d == 1 else f"{sign}{body}/{d}"
    return v.plain()


def _look(text: str) -> tuple:
    """What an option looks like at a glance, from the printed string alone."""
    return ("π" in text, "√" in text, "/" in text, "." in text)


def _assemble_radicals(key: Exact, mistakes: list[Mis], rng: random.Random):
    """assemble(), but judging "the key is alone in its form" by what is printed.

    `item.assemble` compares `Exact.form`, in which 2√π and √(2π) are different
    shapes because their radicands differ. On the page they are the same shape,
    and the source item -- 2, √(2π), 2√π, 2π -- offers no c√π distractor at all,
    so the engine's proxy would throw away College Board's own option set. Every
    other rule is `assemble`'s: distinct positive values, ascending order, and
    the key never alone in the form a student can see.
    """
    seen, picked = {key}, []
    for m in mistakes:
        if m.value is None or m.value in seen or float(m.value) <= 0:
            continue
        seen.add(m.value)
        picked.append(m)
        if len(picked) == 3:
            break
    if len(picked) < 3:
        raise ItemError("could not build three distinct distractors")
    options = [(key, "")] + [(m.value, m.reason) for m in picked]
    texts = [_radical_pi(v) for v, _ in options]
    if len(set(texts)) != 4:
        raise ItemError("two options render the same way")
    if [_look(t) for t in texts].count(_look(texts[0])) == 1:
        raise ItemError("the key would be the only option of its printed form")
    order = sorted(range(4), key=lambda i: float(options[i][0]))
    return ([texts[i] for i in order], [texts[i] for i in order],
            [options[i][1] for i in order], "ABCD"[order.index(0)])


def equal_area_square(rng: random.Random, seed: int, *, r=None, given=None,
                      ask=None, wrongs=None) -> Item:
    """A square with the same area as a circle: the side is r*sqrt(pi).

    The circle can be handed over as its radius, diameter, area or
    circumference, and the question can ask for the square's side or its
    perimeter -- the underlying step is the same square root each time.
    """
    r = E(r or rng.randint(2, 30))
    given = given or rng.choice(["radius", "radius", "diameter", "area", "circumference"])
    ask = ask or rng.choice(["side", "side", "perimeter"])
    side = (PI * r ** 2).sqrt()
    if side is None:
        raise ItemError("side is not expressible exactly")
    key = side if ask == "side" else E(4) * side

    shown = {"radius": r, "diameter": E(2) * r,
             "area": PI * r ** 2, "circumference": E(2) * PI * r}[given]
    art = "an" if given == "area" else "a"
    want = "side length" if ask == "side" else "perimeter"
    stem = rng.choice([
        f"What is the {want} of a square that has the same area as a circle with "
        f"{art} {given} of {shown.plain()}?",
        f"A square and a circle have the same area. If the {given} of the circle is "
        f"{shown.plain()}, what is the {want} of the square?",
        f"A circle has {art} {given} of {shown.plain()}. What is the {want} of a square whose "
        f"area is equal to the area of this circle?",
    ])

    # Order matters for a free draw: `assemble` takes the first three that fit,
    # and at least one of them has to carry a radical, or the key is the only
    # option with a √ in it and the item is guessable.
    pool = {
        "radius_as_side": Mis("used the radius as the side length", r),
        "sqrt_pi_r": Mis("found the area as πr, forgetting to square the radius, and "
                         "then took the square root", (PI * r).sqrt()),
        "pi_r": Mis("used πr, forgetting to square the radius or take the root", PI * r),
        "other_measure": Mis("gave the perimeter instead of one side" if ask == "side"
                             else "gave one side instead of the perimeter",
                             E(4) * side if ask == "side" else side),
        "circumference": Mis("used the circumference", E(2) * PI * r),
    }
    if given == "diameter":
        # using the diameter as the radius doubles the side, and so doubles
        # whichever of the side and the perimeter the item asks for
        pool = {"diameter_as_radius": Mis("used the diameter as the radius",
                                          E(2) * key), **pool}
    rationale = (f"The circle has area pi({r.plain()})^2 = {(PI*r**2).plain()}; a square of that "
                 f"area has side {side.plain()}"
                 + (f", so its perimeter is {key.plain()}." if ask == "perimeter" else "."))
    P = {"kind": "equal_area_square", "r": float(r), "ask": ask}
    choices, latex, reasons, letter = _assemble_radicals(key, pick(pool, wrongs), rng)
    return Item("GEO.circle.equal_area_square", "circle and square area", "hard", seed, stem,
                "mcq", key, letter, rationale, choices, reasons, latex, params=P)


def circle_convert(rng: random.Random, seed: int, *, given=None, ask=None, r=None,
                   unit=None, fmt=None, wrongs=None) -> Item:
    """Move between a circle's radius, diameter, circumference and area."""
    given = given or rng.choice(["circumference", "diameter", "area"])
    ask = ask or rng.choice([a for a in ("diameter", "radius", "circumference") if a != given])
    unit = unit or rng.choice(UNITS[:4])
    fmt = fmt or rng.choice(["spr", "mcq"])
    rr = E(r or rng.randint(3, 40)) / E(2 if given == "circumference" and ask == "diameter" else 1)
    vals = {"radius": rr, "diameter": E(2) * rr,
            "circumference": E(2) * PI * rr, "area": PI * rr ** 2}
    key = vals[ask]
    gv = vals[given]
    P = {"kind": "circle_convert", "r": float(rr), "ask": ask, "given": given}
    stem = (f"A circle has {'an' if given == 'area' else 'a'} {given} of {gv.plain()} "
            f"{unit.many() if given in ('radius', 'diameter', 'circumference') else 'square ' + unit.many()}. "
            f"What is the {ask}, in {unit.many()}, of the circle?")
    pool = {k: Mis(f"gave the {k} instead", v) for k, v in vals.items() if k != ask}
    pool["quarter"] = Mis("halved when the value should have been doubled", key / E(4))
    pool["quadruple"] = Mis("doubled when the value should have been halved", key * E(4))
    rationale = f"From {given} = {gv.plain()}, the radius is {rr.plain()}, so the {ask} is {key.plain()}."
    if fmt == "spr":
        if not key.is_rational:
            raise ItemError("grid-in must be numeric")
        return Item("GEO.circle.convert", "circle measures", "medium", seed, stem, "spr", key,
                    key.gridin(), rationale, params=P,
                    spr_mistakes=gridin_wrongs(key, pool))
    choices, latex, reasons, letter = assemble(key, pick(pool, wrongs), rng)
    return Item("GEO.circle.convert", "circle measures", "medium", seed, stem, "mcq", key,
                letter, rationale, choices, reasons, latex, params=P)


def formula_solve(rng: random.Random, seed: int, *, a=None, b=None, volume=None,
                  ounces=None, wrongs=None) -> Item:
    """A nonstandard volume formula is supplied; solve it for its variable.

    The tested skill is substituting into a given formula and taking a cube
    root -- not recalling a formula -- so the coefficient is deliberately odd.
    """
    a = a or rng.choice([3, 5, 7, 9, 11, 13])
    b = b or rng.choice([12, 16, 24, 32, 36, 48, 64])
    volume = volume or rng.randrange(150, 900)
    exact = (b * volume / (a * math.pi)) ** (1 / 3)
    key = E(Fraction(round(exact * 100), 100))
    P = {"kind": "formula_solve", "a": a, "b": b, "volume": volume}
    vessel = rng.choice(["glass", "vase", "tumbler", "beaker"])
    stem = (f"The {vessel} pictured above can hold a maximum volume of {volume} cubic "
            f"centimeters"
            + (f", which is approximately {ounces} fluid ounces" if ounces else "")
            + f". Its volume is given by Volume = {a}πk³⁄{b}, where k is the "
            f"height in centimeters. What is the value of k, in centimeters?")
    def approx(x): return E(Fraction(round(x * 100), 100))
    pool = {
        "cube_root_only": Mis("ignored the coefficient and took the cube root of the "
                              "volume alone", approx(volume ** (1 / 3))),
        "no_pi": Mis("left pi out of the calculation", approx((b * volume / a) ** (1 / 3))),
        "inverted": Mis("inverted the coefficient",
                        approx((a * volume / (b * math.pi)) ** (1 / 3))),
        "square_root": Mis("took a square root instead of a cube root",
                           approx((b * volume / (a * math.pi)) ** (1 / 2))),
        "cone": Mis("used the cone formula ⅓πk³ instead of the one printed",
                    approx((3 * volume / math.pi) ** (1 / 3))),
        "ounces_root": Mis("took the cube root of the volume in fluid ounces rather "
                           "than in cubic centimeters",
                           approx(ounces ** (1 / 3)) if ounces else None),
    }
    rationale = (f"{a}πk³/{b} = {volume} gives k³ = {b}({volume})/({a}π), so "
                 f"k ~= {float(key):.2f}.")
    choices, latex, reasons, letter = assemble(
        key, pick(pool, wrongs), rng, fmt_value=lambda v: f"{float(v):.2f}")
    return Item("GEO.context.formula_solve", "solving a supplied formula", "hard", seed, stem,
                "mcq", key, letter, rationale, choices, reasons, latex, params=P)
