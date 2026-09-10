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

from ..exact import E, PI, Exact
from ..figures import triangle_xyz
from ..item import Item, ItemError, Mis, assemble, assemble_text
from ..shapes import SHAPES, UNITS, Unit, measure_phrase, unit_noun

__all__ = ["expression_measure", "symbolic_volume", "remaining_volume",
           "combined_area", "missing_side", "container_percent"]


# ------------------------------------------------------------- EXPRESSION

def expression_measure(rng: random.Random, seed: int, *, shape=None, measure=None,
                       dims=None, unit=None) -> Item:
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
            key, wrong = f"{s} * {s}", [
                Mis("doubled the side instead of squaring it", f"2 * {s}"),
                Mis("found the perimeter", f"4 * {s}"),
                Mis("doubled the squared side", f"2 * {s} * {s}")]
        else:
            key, wrong = f"4 * {s}", [
                Mis("squared the side, giving the area", f"{s} * {s}"),
                Mis("used two sides only", f"2 * {s}"),
                Mis("doubled the area", f"2 * {s} * {s}")]
    else:
        l = (dims or {}).get("l") or rng.randint(2, 60)
        w = (dims or {}).get("w") or rng.randint(2, 60)
        stem = (f"A rectangle has a length of {l} {unit.many() if unit.abbr else 'units'} and a "
                f"width of {w} {unit.many() if unit.abbr else 'units'}. Which expression gives "
                f"{measure_phrase(measure, unit, 'words')} of this rectangle?")
        if measure == "area":
            key, wrong = f"{l} * {w}", [
                Mis("found the perimeter", f"2({l} + {w})"),
                Mis("doubled the area", f"2({l} * {w})"),
                Mis("added the dimensions", f"{l} + {w}")]
        else:
            key, wrong = f"2({l} + {w})", [
                Mis("found the area", f"{l} * {w}"),
                Mis("added the two given sides only", f"{l} + {w}"),
                Mis("doubled the area", f"2({l} * {w})")]
    choices, reasons, letter = assemble_text(key, wrong, rng)
    return Item("GEO.expression.measure", f"{shape} {measure}", "easy", seed, stem, "mcq",
                E(0), letter, f"The correct expression is {key}.", choices, reasons, choices)


def symbolic_volume(rng: random.Random, seed: int, *, c=None, relation=None) -> Item:
    """A cylinder whose height is stated in terms of its radius; expand V."""
    c = c or rng.randint(2, 16)
    relation = relation or rng.choice(["longer", "times"])
    if relation == "longer":
        stem = (f"A manufacturer determined that right cylindrical containers with a height that "
                f"is {c} inches longer than the radius offer the optimal number of containers to "
                f"be displayed on a shelf. Which of the following expresses the volume V, in "
                f"cubic inches, of such containers, where r is the radius, in inches?")
        key = f"V = pi*r^3 + {c}pi*r^2"
        wrong = [Mis("multiplied instead of expanding the sum", f"V = {c}pi*r^3"),
                 Mis("did not square the radius in the second term", f"V = pi*r^2 + {c}pi*r"),
                 Mis("doubled the radius instead of adding the height", f"V = pi(2r)^3")]
        rationale = f"V = pi*r^2*h with h = r + {c} gives pi*r^2(r + {c}) = pi*r^3 + {c}pi*r^2."
    else:
        stem = (f"A right circular cylinder has a height that is {c} times its radius. Which of "
                f"the following expresses the volume V, in cubic units, of the cylinder, where r "
                f"is the radius?")
        key = f"V = {c}pi*r^3"
        wrong = [Mis("did not square the radius", f"V = {c}pi*r^2"),
                 Mis("added the height instead of multiplying", f"V = pi*r^3 + {c}pi*r^2"),
                 Mis("applied the factor to the radius", f"V = pi({c}r)^3")]
        rationale = f"V = pi*r^2*h with h = {c}r gives {c}pi*r^3."
    choices, reasons, letter = assemble_text(key, wrong, rng)
    return Item("GEO.expression.symbolic_volume", "cylinder volume", "hard", seed, stem, "mcq",
                E(0), letter, rationale, choices, reasons, choices)


# ---------------------------------------------------------------- CONTEXT

def remaining_volume(rng: random.Random, seed: int, *, base=None, h=None, filled=None) -> Item:
    """A sealed can: total volume minus the poured liquid is the solid contents."""
    base = E(base or rng.choice([40, 50, 60, 75, 80, 90, 100]))
    h = E(h or rng.randint(6, 15))
    total = base * h
    lo = max(5, int(float(total) * 0.1) // 5 * 5)
    hi = max(lo + 5, int(float(total) * 0.5))
    filled = E(filled or rng.randrange(lo, hi, 5))
    key = total - filled
    contents = rng.choice([("fruit", "syrup"), ("olives", "brine"), ("beans", "sauce")])
    stem = (f"A cylindrical can containing pieces of {contents[0]} is filled to the top with "
            f"{contents[1]} before being sealed. The base of the can has an area of "
            f"{base.plain()} cm^2, and the height of the can is {h.plain()} cm. If "
            f"{filled.plain()} cm^3 of {contents[1]} is needed to fill the can to the top, which "
            f"of the following is closest to the total volume of the pieces of {contents[0]} in "
            f"the can?")
    mistakes = [Mis("gave the volume of the whole can", total),
                Mis("added the base area to the poured volume", base + filled),
                Mis("divided the base area by the height", base / h),
                Mis("subtracted the base area instead of the poured volume", total - base)]
    rationale = (f"The can holds {base.plain()} × {h.plain()} = {total.plain()} cm^3; the "
                 f"pieces take up {total.plain()} - {filled.plain()} = {key.plain()} cm^3.")
    choices, latex, reasons, letter = assemble(key, mistakes, rng)
    return Item("GEO.context.remaining_volume", "volume in context", "medium", seed, stem,
                "mcq", key, letter, rationale, choices, reasons, latex)


def combined_area(rng: random.Random, seed: int, *, tri_area=None, side=None) -> Item:
    """Two figures, one area given directly and one to be computed, then summed."""
    tri = E(tri_area or rng.randrange(20, 140, 2))
    s = E(side or rng.randint(3, 14))
    key = tri + s ** 2
    stem = (f"Triangle R has an area of {tri.plain()} square centimeters (cm^2). Square S has "
            f"side lengths of {s.plain()} cm. What is the total area of triangle R and square S, "
            f"in cm^2?")
    mistakes = [Mis("added the side length instead of the area of the square", tri + s),
                Mis("halved the given area before adding", tri / E(2) + s ** 2),
                Mis("added the perimeter of the square", tri + E(4) * s),
                Mis("gave the area of the triangle only", tri)]
    rationale = (f"The square has area {s.plain()}² = {(s**2).plain()}, so the total is "
                 f"{tri.plain()} + {(s**2).plain()} = {key.plain()}.")
    choices, latex, reasons, letter = assemble(key, mistakes, rng)
    return Item("GEO.context.combined_area", "combined area", "easy", seed, stem, "mcq", key,
                letter, rationale, choices, reasons, latex)


def missing_side(rng: random.Random, seed: int, *, sides=None) -> Item:
    """Perimeter and two sides given; find the third. Must close as a triangle."""
    if sides:
        x, y, z = sides
    else:
        for _ in range(200):
            x, y, z = (rng.randint(3, 14) for _ in range(3))
            if x + y > z and x + z > y and y + z > x and len({x, y, z}) == 3:
                break
        else:
            raise ItemError("no valid triangle")
    p = x + y + z
    key = E(z)
    stem = (f"The triangle shown has a perimeter of {p} units. If x = {x} units and y = {y} "
            f"units, what is the value of z, in units?")
    mistakes = [Mis("reported one of the given sides", E(y)),
                Mis("reported the other given side", E(x)),
                Mis("added the two given sides instead of subtracting", E(x + y)),
                Mis("subtracted only one of the given sides", E(p - x))]
    rationale = f"z = {p} - {x} - {y} = {z}."
    choices, latex, reasons, letter = assemble(key, mistakes, rng)
    return Item("GEO.context.missing_side", "triangle perimeter", "easy", seed, stem, "mcq",
                key, letter, rationale, choices, reasons, latex, figure=triangle_xyz())


def container_percent(rng: random.Random, seed: int, *, rA=None, pct=None, h=None) -> Item:
    """Container B's radius is p% longer than A's; find B's volume."""
    pct = pct or rng.choice([25, 50, 75, 100])
    step = 100 // math.gcd(pct, 100)
    rA = E(rA or rng.randrange(step * 2, step * 12, step))
    h = E(h or rng.choice([20, 25, 30, 40, 50, 60]))
    ratio = Fraction(100 + pct, 100)
    rB = rA * E(ratio)
    key = PI * rB ** 2 * h
    stem = (f"A manufacturing company produces two sizes of cylindrical containers that each have "
            f"a height of {h.plain()} centimeters. The radius of container A is {rA.plain()} "
            f"centimeters, and the radius of container B is {pct}% longer than the radius of "
            f"container A. What is the volume, in cubic centimeters, of container B?")
    mistakes = [Mis("scaled container A's volume by the radius percent, not its square",
                    PI * rA ** 2 * h * E(ratio)),
                Mis("applied the percent increase twice", PI * (rB * E(ratio)) ** 2 * h),
                Mis("used container A's radius", PI * rA ** 2 * h),
                Mis("multiplied the two radii instead of squaring B's", PI * rA * rB * h)]
    rationale = (f"r_B = {rA.plain()} × {ratio} = {rB.plain()}, so "
                 f"V = π({rB.plain()})²({h.plain()}) = {key.plain()}.")
    choices, latex, reasons, letter = assemble(key, mistakes, rng)
    return Item("GEO.context.container_percent", "cylinder volume", "hard", seed, stem, "mcq",
                key, letter, rationale, choices, reasons, latex)


def equal_area_square(rng: random.Random, seed: int, *, r=None) -> Item:
    """A square with the same area as a circle -- the side is r*sqrt(pi)."""
    r = E(r or rng.randint(2, 20))
    key = (PI * r ** 2).sqrt()
    if key is None:
        raise ItemError("side is not expressible exactly")
    stem = rng.choice([
        f"What is the length of one side of a square that has the same area as a circle with "
        f"radius {r.plain()}?",
        f"A square and a circle have the same area. If the radius of the circle is "
        f"{r.plain()}, what is the side length of the square?",
        f"A circle has radius {r.plain()}. What is the side length of a square whose area is "
        f"equal to the area of this circle?",
    ])
    mistakes = [Mis("used the radius as the side length", r),
                Mis("took the square root of pi*r rather than pi*r^2", (PI * r).sqrt()),
                Mis("used pi*r, forgetting to square the radius or take the root", PI * r),
                Mis("used the circumference", E(2) * PI * r)]
    rationale = (f"The circle has area π({r.plain()})² = {(PI*r**2).plain()}; a square of that "
                 f"area has side sqrt({(PI*r**2).plain()}) = {key.plain()}.")
    choices, latex, reasons, letter = assemble(key, mistakes, rng)
    return Item("GEO.circle.equal_area_square", "circle and square area", "hard", seed, stem,
                "mcq", key, letter, rationale, choices, reasons, latex)


def circle_convert(rng: random.Random, seed: int, *, given=None, ask=None, r=None,
                   unit=None, fmt=None) -> Item:
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
    stem = (f"A circle has {'an' if given == 'area' else 'a'} {given} of {gv.plain()} "
            f"{unit.many() if given in ('radius', 'diameter', 'circumference') else 'square ' + unit.many()}. "
            f"What is the {ask}, in {unit.many()}, of the circle?")
    mistakes = [Mis(f"gave the {k} instead", v) for k, v in vals.items() if k != ask]
    mistakes += [Mis("halved when the value should have been doubled", key / E(4)),
                 Mis("doubled when the value should have been halved", key * E(4))]
    rationale = f"From {given} = {gv.plain()}, the radius is {rr.plain()}, so the {ask} is {key.plain()}."
    if fmt == "spr":
        if not key.is_rational:
            raise ItemError("grid-in must be numeric")
        return Item("GEO.circle.convert", "circle measures", "medium", seed, stem, "spr", key,
                    key.gridin(), rationale)
    choices, latex, reasons, letter = assemble(key, mistakes, rng)
    return Item("GEO.circle.convert", "circle measures", "medium", seed, stem, "mcq", key,
                letter, rationale, choices, reasons, latex)


def formula_solve(rng: random.Random, seed: int, *, a=None, b=None, volume=None) -> Item:
    """A nonstandard volume formula is supplied; solve it for its variable.

    The tested skill is substituting into a given formula and taking a cube
    root -- not recalling a formula -- so the coefficient is deliberately odd.
    """
    a = a or rng.choice([3, 5, 7, 11])
    b = b or rng.choice([16, 24, 32, 48])
    volume = volume or rng.choice([236, 355, 473, 591, 710])
    exact = (b * volume / (a * math.pi)) ** (1 / 3)
    key = E(Fraction(round(exact * 100), 100))
    vessel = rng.choice(["glass", "vase", "tumbler", "beaker"])
    stem = (f"The {vessel} pictured above can hold a maximum volume of {volume} cubic "
            f"centimeters. Its volume is given by Volume = {a}πk³⁄{b}, where k is the "
            f"height in centimeters. What is the value of k, in centimeters?")
    def approx(x): return E(Fraction(round(x * 100), 100))
    mistakes = [Mis("ignored the coefficient and took the cube root of the volume alone",
                    approx(volume ** (1 / 3))),
                Mis("left pi out of the calculation", approx((b * volume / a) ** (1 / 3))),
                Mis("inverted the coefficient", approx((a * volume / (b * math.pi)) ** (1 / 3))),
                Mis("took a square root instead of a cube root",
                    approx((b * volume / (a * math.pi)) ** (1 / 2)))]
    rationale = (f"{a}πk³/{b} = {volume} gives k³ = {b}({volume})/({a}π), so "
                 f"k ~= {key.plain()}.")
    choices, latex, reasons, letter = assemble(
        key, mistakes, rng, fmt_value=lambda v: f"{float(v):.2f}")
    return Item("GEO.context.formula_solve", "solving a supplied formula", "hard", seed, stem,
                "mcq", key, letter, rationale, choices, reasons, latex)
