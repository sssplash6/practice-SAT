"""Sides: the Pythagorean theorem and the two special triangles.

Nothing here rounds until it prints. A hypotenuse is √(a² + b²) as an `Exact`
all the way to the page, a 30-60-90 leg keeps its √3, and an isosceles right
triangle's perimeter keeps both halves of `a + b√2` in a `Surd`. Where a source
item prints a decimal that is a rendering decision, taken at the last moment,
and any stem that says *closest* refuses a draw whose printed options cannot
single one answer out.
"""

from __future__ import annotations

import math
import random
from fractions import Fraction as Q

from ....exact import E, Exact
from ....item import Item, ItemError, Mis, assemble, assemble_text, gridin_mistakes
from ....shapes import UNITS, Unit
from ..figures import right_triangle, trapezoid_logo
from ..kit import (S0, Surd, assemble_surd, closest_only, exact_leg, pick,
                   places_text)

__all__ = ["pythagoras", "leg_expression", "rectangle_diagonal",
           "special_triangle", "special_perimeter", "equilateral_logo"]

MINUS = "\N{MINUS SIGN}"
LETTERS = ("a", "b", "c", "h", "k", "m", "n", "x", "y", "z")
TRIOS = (("A", "B", "C"), ("P", "Q", "R"), ("R", "S", "T"), ("X", "Y", "Z"),
         ("D", "E", "F"), ("J", "K", "L"), ("L", "M", "N"), ("U", "V", "W"))


def _round_to(v: Exact, places: int) -> Exact:
    """The value as it will be printed, still exact -- a rational, not a float."""
    scale = 10 ** places
    n = math.floor(float(v) * scale + 0.5)
    return E(Q(n, scale))


def _aspect_ok(a: float, b: float) -> None:
    if not 0.125 <= a / b <= 8.0:
        raise ItemError("a triangle this thin cannot be drawn legibly")


def _unit_phrase(unit: Unit | None, plural: bool = True) -> str:
    if unit is None:
        return ""
    return unit.many() if plural else unit.noun


# ============================================================ Pythagoras

def _hyp_pool(a: Exact, b: Exact, key: Exact) -> dict:
    """The wrong answers a student actually produces for a hypotenuse."""
    return {
        "sqrt_sum": Mis("took the square root of the sum of the legs instead of the "
                        "sum of their squares", E(1, 0, a.coef + b.coef)),
        "average": Mis("averaged the two legs", (a + b) / E(2)),
        "add": Mis("added the legs instead of using the Pythagorean theorem", a + b),
        "double_sum": Mis("doubled the sum of the legs, as though finding a perimeter",
                          E(2) * (a + b)),
        "sum_squares": Mis("gave the sum of the squares without taking the square root",
                           a ** 2 + b ** 2),
        "half_squares": Mis("halved the sum of the squares instead of taking its "
                            "square root", (a ** 2 + b ** 2) / E(2)),
        "difference": Mis("subtracted the squares instead of adding them",
                          exact_leg(a, b) if float(a) > float(b) else
                          (exact_leg(b, a) if float(b) > float(a) else None)),
        "product": Mis("multiplied the legs instead of squaring and adding them", a * b),
        "half": Mis("halved the longer leg", (a if float(a) > float(b) else b) / E(2)),
    }


def _leg_pool(c: Exact, a: Exact, key: Exact) -> dict:
    return {
        "add_squares": Mis("added the squares instead of subtracting them",
                           E(1, 0, c.coef ** 2 + a.coef ** 2)),
        "subtract": Mis("subtracted the leg from the hypotenuse", c - a),
        "no_root": Mis("stopped at the square of the missing leg", c ** 2 - a ** 2),
        "sqrt_difference": Mis("took the square root of the difference of the lengths "
                               "instead of the difference of their squares",
                               E(1, 0, c.coef - a.coef) if c.coef > a.coef else None),
        "half": Mis("halved the hypotenuse", c / E(2)),
        "hypotenuse": Mis("gave the hypotenuse, which the stem states", c),
    }


def pythagoras(rng: random.Random, seed: int, *, mode=None, a=None, b=None,
               approximate=False, places=1, unit=None, frame=None, fmt=None,
               layout=None, label=None, note=True, wrongs=None) -> Item:
    """Two sides of a right triangle are given; find the third.

    `mode="hypotenuse"` gives the two legs, `mode="leg"` the hypotenuse and one
    leg. `approximate` prints the options as decimals and asks which is closest,
    which is a rendering decision: the answer is still √(a² + b²) exactly.
    """
    mode = mode or rng.choice(["hypotenuse", "hypotenuse", "leg"])
    frame = frame or rng.choice(["figure", "figure", "text"])
    fmt = fmt or ("spr" if rng.random() < 0.2 else "mcq")
    layout = layout or rng.choice(["left", "right"])

    if mode == "hypotenuse":
        a = E(a if a is not None else rng.randint(2, 60))
        b = E(b if b is not None else rng.randint(2, 60))
        key = (a ** 2 + b ** 2).sqrt()
        if key is None:
            raise ItemError("the hypotenuse is not expressible")
        legs = (a, b)
        given_pair = [float(a), float(b)]
        pool = _hyp_pool(a, b, key)
        noun = "hypotenuse"
    else:
        c = E(a if a is not None else rng.randint(5, 60))
        leg = E(b if b is not None else rng.randint(2, 59))
        if float(leg) >= float(c):
            raise ItemError("a leg is shorter than the hypotenuse")
        key = exact_leg(c, leg)
        legs = (key, leg)
        given_pair = [float(leg), float(c)]
        pool = _leg_pool(c, leg, key)
        noun = "other leg"
    _aspect_ok(float(legs[0]), float(legs[1]))

    post = (lambda v: _round_to(v, places)) if approximate else (lambda v: v)
    exact_key = key
    key = post(key)

    # ------------------------------------------------------------- the stem
    unit_words = _unit_phrase(unit)
    tail = f", in {unit_words}," if unit_words else ""
    if frame == "figure":
        letter = label or rng.choice(LETTERS)
        if mode == "hypotenuse":
            sides = {"p": a.plain(), "q": b.plain()}
            if label is not None:
                sides["hyp"] = letter
        else:
            sides = {"q": leg.plain(), "hyp": c.plain()}
            if label is not None:
                sides["p"] = letter
        fig = right_triangle(float(legs[0]), float(legs[1]), layout=layout,
                             sides=sides, note=note)
        if label is not None:
            asked = f"the value of {letter}"
            shown = (f"In the right triangle shown, which of the following is closest to "
                     f"{asked} ?" if approximate else
                     f"In the right triangle shown, what is {asked} ?")
        else:
            which = ("the legs of a right triangle are shown" if mode == "hypotenuse"
                     else "the hypotenuse and one leg of a right triangle are shown")
            shown = (f"The lengths of {which}. Which of the following is closest to the "
                     f"length of the triangle's {noun}?" if approximate else
                     f"The lengths of {which}. What is the length of the triangle's "
                     f"{noun}?")
        stem = shown
    else:
        fig = None
        if mode == "hypotenuse":
            first = f"{a.plain()} {unit_words}" if unit_words else a.plain()
            second = f"{b.plain()} {unit_words}" if unit_words else b.plain()
            lead = f"A right triangle has legs with lengths of {first} and {second}."
        else:
            first = f"{c.plain()} {unit_words}" if unit_words else c.plain()
            second = f"{leg.plain()} {unit_words}" if unit_words else leg.plain()
            lead = (f"A right triangle has a hypotenuse of length {first} and a leg of "
                    f"length {second}.")
        ask = ("Which of the following is closest to the length of this triangle's "
               f"{noun}{tail}?" if approximate else
               f"What is the length of this triangle's {noun}{tail}?")
        stem = f"{lead} {ask}"

    formula = ("a² + b² = c²" if mode == "hypotenuse" else "c² − a² = b²")
    rationale = (f"By the Pythagorean theorem the {noun} is "
                 f"{exact_key.plain()}" +
                 (f", which is about {places_text(float(exact_key), places)}."
                  if approximate else f" ({formula})."))
    P = {"kind": "rtt_pythagoras", "mode": mode, "given": given_pair,
         "places": places if approximate else None}

    if fmt == "spr" and mode == "hypotenuse":
        # neither halving a leg nor a perimeter is a route a student takes to a
        # hypotenuse, and a grid-in only names a mistake the student made
        pool["half"] = pool["double_sum"] = None
    mistakes = [Mis(m.reason, post(m.value)) for m in pick(pool, wrongs)
                if m.value is not None]
    if fmt == "spr":
        if not key.is_rational:
            raise ItemError("this length cannot be entered in a grid-in")
        return Item("rtt.pythagoras", "the Pythagorean theorem", "easy", seed, stem,
                    "spr", key, key.gridin(), rationale, figure=fig, params=P,
                    spr_mistakes=gridin_mistakes(key, mistakes))

    fmt_value = (lambda v: places_text(float(v), places)) if approximate else None
    choices, latex, reasons, letter_ = assemble(key, mistakes, rng, fmt_value=fmt_value)
    if len(set(choices)) != 4:
        raise ItemError("two options round to the same printed number")
    if approximate:
        closest_only(float(exact_key), [float(c_.replace(",", "")) for c_ in choices],
                     float(key))
    return Item("rtt.pythagoras", "the Pythagorean theorem", "easy", seed, stem, "mcq",
                key, letter_, rationale, choices, reasons, latex, figure=fig, params=P)


# ================================================== the theorem as an expression

def leg_expression(rng: random.Random, seed: int, *, mode=None, c=None, a=None,
                   label=None, layout=None, note=True, wrongs=None) -> Item:
    """The options are the expression itself, not its value.

    So the mistake on offer is a mistake in setting the theorem up -- forgetting
    the root, squaring the difference instead of differencing the squares -- and
    the item never asks the student to evaluate anything.
    """
    mode = mode or rng.choice(["leg", "hypotenuse"])
    layout = layout or rng.choice(["left", "right"])
    letter = label or rng.choice(LETTERS)
    big = E(c if c is not None else rng.randint(6, 90))
    small = E(a if a is not None else rng.randint(2, 89))
    if float(small) >= float(big):
        raise ItemError("the two given lengths are in the wrong order")
    B, A = big.plain(), small.plain()

    if mode == "leg":
        key_text = f"√({B}² {MINUS} {A}²)"
        third = exact_leg(big, small)
        sides = {"p": A, "hyp": B, "q": letter}
        shape = (float(small), float(third))
        pool = {
            "no_root": Mis("subtracted the squares but did not take the square root",
                           f"{B}² {MINUS} {A}²"),
            "no_squares": Mis("subtracted the lengths under the root instead of their "
                              "squares", f"√({B} {MINUS} {A})"),
            "plain_difference": Mis("subtracted the two given lengths",
                                    f"{B} {MINUS} {A}"),
            "added": Mis("added the squares instead of subtracting them",
                         f"√({B}² + {A}²)"),
            "swapped": Mis("subtracted the hypotenuse's square from the leg's",
                           f"√({A}² {MINUS} {B}²)"),
        }
    else:
        key_text = f"√({B}² + {A}²)"
        sides = {"p": A, "q": B, "hyp": letter}
        shape = (float(small), float(big))
        pool = {
            "no_root": Mis("added the squares but did not take the square root",
                           f"{B}² + {A}²"),
            "no_squares": Mis("added the lengths under the root instead of their "
                              "squares", f"√({B} + {A})"),
            "plain_sum": Mis("added the two given lengths", f"{B} + {A}"),
            "subtracted": Mis("subtracted the squares instead of adding them",
                              f"√({B}² {MINUS} {A}²)"),
            "halved": Mis("halved the sum of the squares instead of taking its square "
                          "root", f"({B}² + {A}²)/2"),
        }
    _aspect_ok(*shape)
    fig = right_triangle(shape[0], shape[1], layout=layout, sides=sides, note=note)
    stem = rng.choice([
        f"For the triangle shown, which expression represents the value of {letter} ?",
        f"For the right triangle shown, which expression gives the value of {letter} ?",
    ])
    rationale = (f"The theorem gives {letter}² = {B}² {MINUS} {A}²" if mode == "leg"
                 else f"The theorem gives {letter}² = {B}² + {A}²")
    rationale += f", so {letter} = {key_text}."
    P = {"kind": "rtt_leg_expression", "mode": mode, "big": float(big),
         "small": float(small)}
    choices, reasons, letter_ = assemble_text(key_text, pick(pool, wrongs), rng)
    return Item("rtt.leg_expression", "the Pythagorean theorem", "medium", seed, stem,
                "mcq", E(0), letter_, rationale, choices, reasons, choices,
                figure=fig, params=P)


# ============================================== a rectangle and its diagonal

def rectangle_diagonal(rng: random.Random, seed: int, *, short=None, long=None,
                       ask=None, fmt=None, wrongs=None) -> Item:
    """The diagonal of a rectangle is the hypotenuse of two congruent triangles."""
    s = E(short if short is not None else rng.randint(2, 30))
    L = E(long if long is not None else rng.randint(3, 60))
    if float(L) <= float(s):
        raise ItemError("the longer side has to be longer")
    diag = (s ** 2 + L ** 2).sqrt()
    if diag is None:
        raise ItemError("the diagonal is not expressible")
    ask = ask or "long"
    fmt = fmt or ("spr" if rng.random() < 0.4 else "mcq")
    key = L if ask == "long" else s
    other, other_name = (s, "shorter") if ask == "long" else (L, "longer")
    want = "longer" if ask == "long" else "shorter"

    pool = {
        "divide": Mis("divided the diagonal by the given side instead of using the "
                      "Pythagorean theorem", diag / other),
        "added": Mis("added the squares instead of subtracting them",
                     (diag ** 2 + other ** 2).sqrt()),
        "no_root": Mis("stopped at the square of the side", diag ** 2 - other ** 2),
        "half": Mis("halved the diagonal", diag / E(2)),
        "given": Mis(f"gave the {other_name} side, which the stem states", other),
        "double": Mis("doubled the side, as though the diagonal crossed two of them",
                      E(2) * key),
    }
    stem = rng.choice([
        f"The length of a rectangle's diagonal is {diag.plain()}, and the length of the "
        f"rectangle's {other_name} side is {other.plain()}. What is the length of the "
        f"rectangle's {want} side?",
        f"A rectangle has a diagonal of length {diag.plain()} and a {other_name} side of "
        f"length {other.plain()}. What is the length of the rectangle's {want} side?",
    ])
    rationale = (f"The diagonal and the two sides make a right triangle, so the {want} "
                 f"side is √({diag.plain()}² − {other.plain()}²) = {key.plain()}.")
    P = {"kind": "rtt_rectangle_diagonal", "short": float(s), "long": float(L),
         "ask": ask}
    if fmt == "spr":
        if not key.is_rational:
            raise ItemError("this length cannot be entered in a grid-in")
        pool["double"] = None           # doubling the side needs the side first
        return Item("rtt.rectangle_diagonal", "rectangles and the theorem", "medium",
                    seed, stem, "spr", key, key.gridin(), rationale, params=P,
                    spr_mistakes=gridin_mistakes(key, pick(pool, wrongs)))
    choices, latex, reasons, letter = assemble(key, pick(pool, wrongs), rng)
    return Item("rtt.rectangle_diagonal", "rectangles and the theorem", "medium", seed,
                stem, "mcq", key, letter, rationale, choices, reasons, latex, params=P)


# ============================================== 30-60-90 and 45-45-90

TAN = {30: E(Q(1, 3), 0, 3), 45: E(1), 60: E(1, 0, 3)}
SIN = {30: E(Q(1, 2)), 45: E(Q(1, 2), 0, 2), 60: E(Q(1, 2), 0, 3)}
COS = {30: E(Q(1, 2), 0, 3), 45: E(Q(1, 2), 0, 2), 60: E(Q(1, 2))}


def _special_sides(alpha: int, given: str, value: Exact) -> dict:
    """The three sides, from whichever one the stem hands over.

    `alpha` is the angle at the far end of the leg `p`, so the leg `q` is
    opposite it and the hypotenuse is opposite the right angle.
    """
    if given == "p":
        v = value
        return {"p": v, "q": v * TAN[alpha], "hyp": v / COS[alpha]}
    if given == "q":
        h = value
        return {"p": h / TAN[alpha], "q": h, "hyp": h / SIN[alpha]}
    c = value
    return {"p": c * COS[alpha], "q": c * SIN[alpha], "hyp": c}


def special_triangle(rng: random.Random, seed: int, *, alpha=None, given=None,
                     value=None, ask=None, layout=None, names=None, label=None,
                     mark=None, fmt=None, note=True, wrongs=None) -> Item:
    """One side and one special angle fix the whole triangle.

    Every draw picks the angle as well as the size, so the template is not
    built round a single triangle: 30-60-90 and 45-45-90 both come out of it,
    from any one of the three sides, and it will ask for a side or an angle.
    """
    alpha = alpha or rng.choice([30, 45, 60])
    given = given or rng.choice(["p", "q", "hyp"])
    ask = ask or rng.choice(["p", "q", "hyp", "angle_p", "angle_q"])
    if ask == given:
        raise ItemError("the stem would be asking for the number it states")
    layout = layout or rng.choice(["left", "right"])
    val = E(value if value is not None else rng.randint(2, 60))
    sides = _special_sides(alpha, given, val)
    _aspect_ok(float(sides["p"]), float(sides["q"]))
    fmt = fmt or ("spr" if rng.random() < 0.35 else "mcq")
    letter = label or rng.choice(LETTERS)
    trio = names or (rng.choice(TRIOS) if rng.random() < 0.4 else None)
    beta = 90 - alpha

    # ------------------------------------------------------------ the figure
    shown = {k: (v.plain() if k == given else "") for k, v in sides.items()}
    shown = {k: v for k, v in shown.items() if v}
    angle_marks = {}
    if mark is None:
        mark = "p" if alpha != 45 else rng.choice(["p", "q", "both"])
    if ask.startswith("angle"):
        angle_marks[ask.split("_")[1]] = f"{letter}°"
        other = "q" if ask.endswith("p") else "p"
        if mark in (other, "both"):
            angle_marks[other] = f"{alpha if other == 'p' else beta}°"
        # the stem gives a second side when no angle is marked, or the angle is
        # not determined at all
        second = next(k for k in ("p", "q", "hyp") if k != given)
        shown[second] = sides[second].plain()
    else:
        for key_ in (("p", "q") if mark == "both" else (mark,)):
            if key_ in ("p", "q"):
                angle_marks[key_] = f"{alpha if key_ == 'p' else beta}°"
        # the side asked for is lettered only when the vertices are unnamed;
        # a named triangle says which segment it wants in the stem instead
        if trio is None:
            shown[ask] = letter
    named = ({"rt": trio[0], "p": trio[1], "q": trio[2]} if trio else None)
    fig = right_triangle(float(sides["p"]), float(sides["q"]), layout=layout,
                         sides=shown, angles=angle_marks, names=named, note=note)

    # --------------------------------------------------------- the question
    if ask.startswith("angle"):
        key = E(alpha if ask.endswith("p") else beta)
        stem = rng.choice([
            f"In the triangle shown, what is the value of {letter} ?",
            f"In the right triangle shown, what is the value of {letter} ?",
        ])
        rationale = (f"The two legs are {sides['p'].plain()} and {sides['q'].plain()}, "
                     f"so the marked angle measures {key.plain()} degrees.")
        pool = {
            "complement": Mis("gave the other acute angle", E(beta if ask.endswith("p")
                                                              else alpha)),
            "right_angle": Mis("gave the right angle rather than the marked one", E(90)),
            "side": Mis("gave the length of a side instead of the angle measure",
                        sides[given]),
            "straight": Mis("subtracted from 180 instead of from 90",
                            E(180) - E(alpha if ask.endswith("p") else beta)),
        }
    else:
        key = sides[ask]
        if trio:
            seg = {"p": trio[0] + trio[1], "q": trio[0] + trio[2],
                   "hyp": trio[1] + trio[2]}[ask]
            stem = rng.choice([
                f"In the right triangle shown above, what is the length of {seg} ?",
                f"In the right triangle shown, what is the length of {seg} ?",
            ])
        else:
            stem = rng.choice([
                f"In the triangle shown, what is the value of {letter} ?",
                f"In the right triangle shown, what is the value of {letter} ?",
            ])
        shape_ratio = "1 : 1 : √2" if alpha == 45 else "1 : √3 : 2"
        noun = {"p": f"the leg beside the {alpha}° angle",
                "q": f"the leg opposite the {alpha}° angle",
                "hyp": "the hypotenuse"}
        rationale = (f"The angles are {alpha}°, {beta}° and 90°, so the sides are in "
                     f"the ratio {shape_ratio}. {noun[given][0].upper()}"
                     f"{noun[given][1:]} is {sides[given].plain()}, which makes "
                     f"{noun[ask]} {key.plain()}.")
        pool = {
            "angle_measure": Mis("gave the measure of the marked angle instead of the "
                                 "length of the side", E(alpha)),
            "double": Mis("doubled the given side", E(2) * sides[given]),
            "sum_with_angle": Mis("added the given length and the marked angle measure",
                                  sides[given] + E(alpha)),
            "half": Mis("halved the given side", sides[given] / E(2)),
            "third_side": Mis("gave the third side of the triangle",
                              sides[next(k for k in ("p", "q", "hyp")
                                         if k not in (given, ask))]),
            "reciprocal": Mis("multiplied by the ratio where it should have divided",
                              sides[given] ** 2 / key),
        }
    P = {"kind": "rtt_special_triangle", "alpha": alpha, "given": given,
         "value": float(val), "ask": ask}
    if fmt == "spr":
        if not key.is_rational:
            raise ItemError("this answer cannot be entered in a grid-in")
        # that route is 180 minus the marked other angle, which is this value
        # only when both acute angles are 45
        if ask.startswith("angle") and not (alpha == 45 and len(angle_marks) == 2):
            pool["straight"] = None
        return Item("rtt.special_triangle", "special right triangles", "medium", seed,
                    stem, "spr", key, key.gridin(), rationale, figure=fig, params=P,
                    spr_mistakes=gridin_mistakes(key, pick(pool, wrongs)))
    choices, latex, reasons, letter_ = assemble(key, pick(pool, wrongs), rng)
    return Item("rtt.special_triangle", "special right triangles", "medium", seed, stem,
                "mcq", key, letter_, rationale, choices, reasons, latex, figure=fig,
                params=P)


# ====================================== a special triangle from its perimeter

ROOT2, ROOT3 = Surd.of(0, 1, 2), Surd.of(0, 1, 3)


def _family(shape: str, unit_side: Surd) -> dict:
    """The three sides and the perimeter, as multiples of the defining side."""
    if shape == "isosceles":
        leg = unit_side
        return {"leg": leg, "other_leg": leg, "hyp": leg * ROOT2,
                "perimeter": leg * Surd.of(2) + leg * ROOT2}
    short = unit_side
    return {"short": short, "long": short * ROOT3, "hyp": short * Surd.of(2),
            "perimeter": short * Surd.of(3) + short * ROOT3}


def _defining(shape: str, given: str, value: Surd) -> Surd:
    """Undo whichever side or perimeter the stem states, back to the base side."""
    base = _family(shape, Surd.of(1))
    if given not in base:
        raise ItemError(f"{shape} has no measure called {given!r}")
    return value / base[given]


ASK_NOUN = {"leg": "one leg", "other_leg": "the other leg", "hyp": "the hypotenuse",
            "perimeter": "the perimeter", "short": "the shorter leg",
            "long": "the longer leg"}
GIVEN_NOUN = {"leg": "a leg of length", "hyp": "a hypotenuse of length",
              "perimeter": "a perimeter of", "short": "a shorter leg of length",
              "long": "a longer leg of length"}


def special_perimeter(rng: random.Random, seed: int, *, shape=None, given=None,
                      value=None, ask=None, unit=None, fmt=None, frame=None,
                      superlative=False, wrongs=None) -> Item:
    """A 45-45-90 or a 30-60-90 given one measure; find another.

    The answers here are the one shape `Exact` cannot hold -- a perimeter like
    58 + 58√2 -- so this family works in `Surd` and prints the rational part and
    the radical part side by side, exactly as the source does.
    """
    shape = shape or rng.choice(["isosceles", "thirty_sixty"])
    keys = list(_family(shape, Surd.of(1)))
    given = given or rng.choice([k for k in keys if k != "other_leg"])
    ask = ask or rng.choice([k for k in keys if k not in (given, "other_leg")])
    if ask == given:
        raise ItemError("the stem would be asking for the number it states")
    frame = frame or ("is" if (given == "perimeter" and rng.random() < 0.4)
                      else "has")

    if value is None:
        base = Surd.of(rng.randint(2, 99))
        value = _family(shape, base)[given]
    value = value if isinstance(value, Surd) else Surd.of(value)
    base = _defining(shape, given, value)
    if float(base) <= 0:
        raise ItemError("that measure does not describe a triangle")
    sides = _family(shape, base)
    key = sides[ask]

    unit_words = _unit_phrase(unit)
    tail = f", in {unit_words}," if unit_words else ""
    noun = "An isosceles right triangle" if shape == "isosceles" else \
        "A triangle with angle measures 30°, 60°, and 90°"
    stated = f"{value.plain()} {unit_words}".strip()
    if superlative and ask in ("hyp", "long", "short"):
        asked = {"hyp": "the longest side", "long": "the longer leg",
                 "short": "the shortest side"}[ask]
    else:
        asked = ASK_NOUN[ask]
    if frame == "is" and given != "perimeter":
        # "The leg of an isosceles right triangle" does not say which leg; only
        # the perimeter reads naturally in the source's second frame
        raise ItemError("that measure does not fit the second sentence frame")
    if frame == "has":
        lead = f"{noun} has {GIVEN_NOUN[given]} {stated}."
    else:
        lead = f"The perimeter of {noun[0].lower() + noun[1:]} is {stated}."
    stem = f"{lead} What is the length{tail} of {asked} of this triangle?" \
        if ask != "perimeter" else f"{lead} What is the perimeter{tail} of this triangle?"

    pool = {
        "leg": Mis("gave the length of a leg", sides.get("leg") or sides.get("short")),
        "short": Mis("gave the shorter leg", sides.get("short")),
        "long": Mis("gave the longer leg", sides.get("long")),
        "hyp": Mis("gave the hypotenuse", sides["hyp"]),
        "perimeter": Mis("gave the perimeter", sides["perimeter"]),
        "half_hyp": Mis("took half the hypotenuse for a leg instead of dividing by √2",
                        sides["hyp"] / Surd.of(2)),
        "double_leg": Mis("doubled a leg, leaving the hypotenuse out",
                          Surd.of(2) * (sides.get("leg") or sides.get("short"))),
        "legs_as_hyp": Mis("multiplied the hypotenuse by √2 to get each leg instead of "
                           "dividing", sides["hyp"] + Surd.of(2) * sides["hyp"] * ROOT2),
        "hyp_root2": Mis("multiplied the hypotenuse by √2 as well", sides["hyp"] * ROOT2),
    }
    rationale = (f"The sides are in the ratio 1 : 1 : √2" if shape == "isosceles"
                 else "The sides are in the ratio 1 : √3 : 2")
    rationale += (f", so {ASK_NOUN[given]} of {value.plain()} makes "
                  f"{asked} {key.plain()}.")
    P = {"kind": "rtt_special_perimeter", "shape": shape, "given": given,
         "value": [str(value.a), str(value.b), value.d], "ask": ask}
    mistakes = [m for m in pick(pool, wrongs) if m.value is not None]
    if fmt == "spr":
        if not key.rational or float(key) <= 0:
            raise ItemError("this answer cannot be entered in a grid-in")
        answer = (f"{key.a.numerator}" if key.a.denominator == 1
                  else f"{key.a.numerator}/{key.a.denominator}")
        if ask != "perimeter":
            # a whole perimeter, and two ways of working one out: none of them
            # is a route to a single side
            pool["legs_as_hyp"] = pool["double_leg"] = pool["hyp_root2"] = None
        # a Surd has `.rational`, not the `.is_rational` the shared filter reads,
        # so a radical that cannot be typed is dropped here
        mistakes = [m for m in pick(pool, wrongs) if m.value.rational]
        return Item("rtt.special_perimeter", "special right triangles", "hard", seed,
                    stem, "spr", key, answer, rationale, params=P,
                    spr_mistakes=gridin_mistakes(key, mistakes))
    choices, latex, reasons, letter = assemble_surd(
        key, mistakes, rng, enforce_form=wrongs is None)
    return Item("rtt.special_perimeter", "special right triangles", "hard", seed, stem,
                "mcq", key, letter, rationale, choices, reasons, latex, params=P)


# ============================================ equilateral triangles in a row

def equilateral_logo(rng: random.Random, seed: int, *, count=None, perimeter=None,
                     shade=None, ask=None, unit=None, fmt=None, wrongs=None) -> Item:
    """A trapezoid built from congruent equilateral triangles.

    The perimeter counts the outside edges only -- an odd row of n triangles
    has n + 2 of them -- and the area of each is (√3/4)s², so the answer keeps
    its radical.
    """
    count = count or rng.choice([3, 5, 7, 9])
    if count % 2 == 0 or count < 3:
        raise ItemError("an even row is not a trapezoid")
    shade = shade or rng.choice(["up", "down"])
    # the figure shades part of the logo, so the question is about that part;
    # asking for the whole area beside a shaded picture reads as a trick
    ask = ask or "shaded"
    if ask != "shaded":
        raise ItemError("the shading in the figure would go unexplained")
    fmt = fmt or ("spr" if rng.random() < 0.2 else "mcq")
    edges = count + 2
    if perimeter is None:
        perimeter = edges * rng.randint(2, 30)
    s = E(Q(int(perimeter), edges))
    if s.coef.denominator != 1:
        raise ItemError("the side length is not a whole number")
    one = E(Q(1, 4), 0, 3) * s ** 2
    up, down = (count + 1) // 2, (count - 1) // 2
    shaded = up if shade == "up" else down
    n = {"shaded": shaded, "one": 1, "whole": count}[ask]
    key = E(n) * one

    unit_words = _unit_phrase(unit) or "centimeters"
    square_words = f"square {unit_words}"
    region = "the combined area of the shaded regions"
    word = {3: "three", 5: "five", 7: "seven", 9: "nine"}[count]
    stem = rng.choice([
        f"A graphic designer is creating a logo for a company. The logo is shown in the "
        f"figure above. The logo is in the shape of a trapezoid and consists of {word} "
        f"congruent equilateral triangles. If the perimeter of the logo is "
        f"{int(perimeter)} {unit_words}, what is {region}, in {square_words}, of the "
        f"logo?",
        f"The logo shown above is in the shape of a trapezoid and is made of {word} "
        f"congruent equilateral triangles. The perimeter of the logo is "
        f"{int(perimeter)} {unit_words}. What is {region}, in {square_words}?",
    ])
    pool = {
        "one_triangle": Mis("found the area of one triangle only", one),
        "half_triangle": Mis("halved a triangle's area, taking the shaded part to be "
                             "half of each triangle", one / E(2)),
        "square": Mis("used s² for the area, as though each triangle were a square",
                      s ** 2),
        "all_triangles": Mis("shaded every triangle instead of the ones that point "
                             "one way", E(count) * one),
        "other_half": Mis("shaded the triangles that point the other way",
                          E(down if shade == "up" else up) * one),
        "perimeter_side": Mis("used the perimeter as the side length",
                              E(Q(1, 4), 0, 3) * E(int(perimeter)) ** 2),
        "no_root": Mis("used one half base times height without the √3 in the height",
                       E(n) * s ** 2 / E(2)),
    }
    fig = trapezoid_logo(count, shade=shade)
    rationale = (f"The {edges} outside edges give s = {s.plain()}, and an equilateral "
                 f"triangle of side s has area (√3/4)s² = {one.plain()}, so "
                 f"{region} is {key.plain()}.")
    P = {"kind": "rtt_equilateral_logo", "count": count, "perimeter": int(perimeter),
         "shade": shade, "ask": ask}
    if fmt == "spr":
        raise ItemError("an area with a radical in it cannot be entered in a grid-in")
    choices, latex, reasons, letter = assemble(key, pick(pool, wrongs), rng)
    return Item("rtt.equilateral_logo", "equilateral triangles", "hard", seed, stem,
                "mcq", key, letter, rationale, choices, reasons, latex, figure=fig,
                params=P)
