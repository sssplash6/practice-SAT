"""Situations that come out as a quadratic, and situations that come out as an
expression.

The first half answers with a number, so `assemble` orders the options; the
second half answers with an expression and is assembled as text. Both share
the same source of wrong answers: the other quantity in the situation. The
length rather than the width, the larger integer rather than the smaller, the
perimeter rather than the side -- every one of them is a true fact about the
figure and none of them is what was asked.
"""

from __future__ import annotations

import random
from fractions import Fraction as Q

from ....item import ItemError, Mis
from ..common import (MINUS, dec, factored, fn, num, pair, pick, poly_text, q, sig,
                      sup, text_item, value_item)

__all__ = ["quad_word", "build_expression"]

RECT_DOUBLE = ("A rectangular {thing} has an area of {area} square {unit}. If the "
               "length of the {thing} is twice the width, what is the width of the "
               "{thing}, in {unit}?")
RECT_OFFSET = ("A rectangle has a length of x units and a width of (x {MINUS} {d}) "
               "units. If the rectangle has an area of {area} square units, what is "
               "the value of x?")
PRODUCT = ("The product of two positive integers is {p}. If the first integer is {c} "
           "greater than {mult} the second integer, what is the smaller of the two "
           "integers?")
TRIANGLE = ("The area of a triangle is {area} square centimeters. The length of the "
            "base of the triangle is {d} centimeters greater than the height of the "
            "triangle. What is the height, in centimeters, of the triangle?")
GARDEN = ("A landscaper is designing a rectangular garden. The length of the garden "
          "is to be {d} feet longer than the width. If the area of the garden will be "
          "{area} square feet, what will be the length, in feet, of the garden?")
TRIANGLE_X = ("The area of a triangle is equal to x² square centimeters. The length "
              "of the base of the triangle is {b} centimeters, and the height of the "
              "triangle is x {MINUS} {h} centimeters. What is the value of x?")
THINGS = [("volleyball court", "meters"), ("badminton court", "meters"),
          ("garden plot", "feet"), ("patio", "feet")]


def quad_word(rng: random.Random, seed: int, *, mode=None, w=None, d=None, p=None,
              c=None, thing=None, fmt="mcq", wrongs=None) -> object:
    """A situation whose equation is quadratic, answered with a number."""
    mode = mode or rng.choice(["rect_double", "rect_offset", "product", "triangle",
                               "garden", "triangle_x"])

    if mode == "rect_double":
        thing, unit = THINGS[rng.randrange(len(THINGS))] if thing is None \
            else THINGS[thing]
        w = q(w if w is not None else rng.randint(3, 30))
        area = 2 * w ** 2
        key = w
        pool = {
            "length": ("gave the length rather than the width", 2 * w),
            "perimeter": ("gave the distance around the rectangle", 6 * w),
            "sum": ("added the two side lengths", 3 * w),
            "area_half": ("halved the area instead of solving for the width", area / 2),
        }
        order = ["length", "perimeter", "sum", "area_half"]
        stem = RECT_DOUBLE.format(thing=thing, area=num(area), unit=unit)
        why = (f"With length 2w the area is 2w² = {num(area)}, so w² = {num(w ** 2)} "
               f"and w = {num(w)}.")
        P = {"kind": "nlf_quad_word", "mode": mode, "w": [w.numerator, w.denominator]}

    elif mode == "rect_offset":
        w = q(w if w is not None else rng.randint(6, 40))
        d = q(d if d is not None else rng.randint(2, 20))
        if w <= d:
            raise ItemError("the width must stay positive")
        area = w * (w - d)
        key = w
        pool = {
            "width": ("gave the width rather than the value of x", w - d),
            "sum": ("added the two dimensions", 2 * w - d),
            "area": ("gave the area rather than the value of x", area),
            "offset": ("added the offset to the width instead of solving", w + d),
        }
        order = ["width", "sum", "area", "offset"]
        stem = RECT_OFFSET.format(MINUS=MINUS, d=num(d), area=num(area))
        why = (f"x(x {MINUS} {num(d)}) = {num(area)} factors as "
               f"(x {MINUS} {num(w)})(x + {num(w - d)}), so x = {num(w)}.")
        P = {"kind": "nlf_quad_word", "mode": mode, "w": [w.numerator, w.denominator],
             "d": [d.numerator, d.denominator]}

    elif mode == "product":
        w = q(w if w is not None else rng.randint(3, 25))
        c = q(c if c is not None else rng.randint(3, 20))
        mult = int(p if p is not None else rng.choice([2, 3]))
        first = mult * w + c
        product = first * w
        if first <= w:
            raise ItemError("the first integer must be the larger of the two")
        key = w
        pool = {
            "larger": ("gave the larger of the two integers", first),
            "double_larger": ("doubled the larger integer", 2 * first),
            "half": ("halved the smaller integer", w / 2),
            "difference": ("gave the difference between the two integers", first - w),
        }
        order = ["larger", "double_larger", "half", "difference"]
        word = {2: "twice", 3: "three times"}[mult]
        stem = PRODUCT.format(p=num(product), c=num(c), mult=word)
        why = (f"({num(mult)}n + {num(c)})n = {num(product)} has the positive solution "
               f"n = {num(w)}, and the other integer is {num(first)}.")
        P = {"kind": "nlf_quad_word", "mode": mode, "w": [w.numerator, w.denominator],
             "c": [c.numerator, c.denominator], "mult": mult}

    elif mode == "triangle":
        w = q(w if w is not None else rng.randint(4, 40))
        d = q(d if d is not None else 2 * rng.randint(1, 12))
        area = w * (w + d) / 2
        if area.denominator != 1:
            raise ItemError("the printed area must be a whole number")
        key = w
        pool = {
            "base": ("gave the base rather than the height", w + d),
            "double": ("doubled the height", 2 * w),
            "half_base": ("halved the base", (w + d) / 2),
            "sum": ("added the base and the height", 2 * w + d),
        }
        order = ["base", "double", "half_base", "sum"]
        stem = TRIANGLE.format(area=num(area), d=num(d))
        why = (f"(1/2)h(h + {num(d)}) = {num(area)} gives h² + {num(d)}h "
               f"{MINUS} {num(2 * area)} = 0, so h = {num(w)}.")
        P = {"kind": "nlf_quad_word", "mode": mode, "w": [w.numerator, w.denominator],
             "d": [d.numerator, d.denominator]}

    elif mode == "garden":
        w = q(w if w is not None else rng.randint(4, 40))
        d = q(d if d is not None else rng.randint(2, 15))
        area = w * (w + d)
        key = w + d
        pool = {}
        order = []
        stem = GARDEN.format(d=num(d), area=num(area))
        why = (f"w(w + {num(d)}) = {num(area)} gives w = {num(w)}, so the length is "
               f"{num(w)} + {num(d)} = {num(key)}.")
        P = {"kind": "nlf_quad_word", "mode": mode, "w": [w.numerator, w.denominator],
             "d": [d.numerator, d.denominator]}
        fmt = "spr"

    else:                                                       # triangle_x
        d = q(d if d is not None else rng.randint(2, 20))
        c = q(c if c is not None else 2 * rng.randint(2, 20))
        # area x² = (1/2)(2x + 2c)(x − d)  ->  x² = (x + c)(x − d)  ->  x = cd/(c − d)
        if c == d:
            raise ItemError("the two offsets must differ")
        key = c * d / (c - d)
        if key.denominator != 1 or key <= d:
            raise ItemError("the printed answer must be a whole number above the offset")
        pool = {
            "sum": ("added the two printed numbers", c + d),
            "product": ("multiplied the two printed numbers", c * d),
            "difference": ("subtracted the two printed numbers", abs(c - d)),
        }
        order = ["sum", "product", "difference"]
        stem = TRIANGLE_X.format(b=poly_text([2 * c, 2]), MINUS=MINUS, h=num(d))
        why = (f"x² = (1/2)({num(2 * c)} + 2x)(x {MINUS} {num(d)}) simplifies to "
               f"x² = x² + {num(c - d)}x {MINUS} {num(c * d)}, so x = {num(key)}.")
        P = {"kind": "nlf_quad_word", "mode": mode, "c": [c.numerator, c.denominator],
             "d": [d.numerator, d.denominator]}
        fmt = "spr"

    return value_item("nlfunc.quad_word", "a situation that becomes a quadratic",
                      "medium", seed, stem, key, pick(pool, order, wrongs), rng, P,
                      why, fmt=fmt, signed=False)


# ------------------------------------------------ answering with an expression

AREA_LENGTH = ("The area A, in square centimeters, of a rectangular {thing} can be "
               "represented by the expression w(w + {d}), where w is the width, in "
               "centimeters, of the {thing}. Which expression represents the length, "
               "in centimeters, of the {thing}?")
PRODUCT_MORE = ("The function f gives the product of a number, x, and a number that "
                "is {d} more than x. Which equation defines f?")
VOLUME = ("A park ranger hung {thing} houses each in the shape of a right rectangular "
          "prism for {animal}. Each house has a height of {h} inches. The length of "
          "each house's base is x inches, which is {d} inch{es} more than the width of "
          "the house's base. Which function V gives the volume of each house, in "
          "cubic inches, in terms of the length of the house's base?")
CUBE = ("The surface area of a cube is 6({a}/{d})², where a is a positive constant. "
        "Which of the following gives the perimeter of one face of the cube?")
PAINTINGS = ["painting", "poster", "photograph", "mirror"]
CRITTERS = [("squirrel", "fox squirrels"), ("bird", "finches"), ("bat", "brown bats")]


def build_expression(rng: random.Random, seed: int, *, mode=None, d=None, h=None,
                     den=None, thing=None, wrongs=None) -> object:
    """The answer is an expression, and three of the four are the item's own parts."""
    mode = mode or rng.choice(["length", "product", "volume", "cube"])

    if mode == "length":
        thing = thing or rng.choice(PAINTINGS)
        d = int(d if d is not None else rng.randint(3, 60))
        key = f"(w + {num(d)})"
        pool = {
            "width": ("gave the width, which the expression already names",
                      pair("w", "w")),
            "offset": ("gave the number added to the width rather than the length",
                       pair(num(d), "d")),
            "area": ("gave the area rather than one of its factors",
                     pair(f"w(w + {num(d)})", "area")),
            "doubled": ("doubled the width instead of adding the offset",
                        pair(f"(2w + {num(d)})", "2w+d")),
        }
        order = ["width", "offset", "area", "doubled"]
        stem = AREA_LENGTH.format(thing=thing, d=num(d))
        why = (f"The area is width × length, and the expression is w times "
               f"(w + {num(d)}), so the length is (w + {num(d)}).")
        P = {"kind": "nlf_build_expression", "mode": mode, "d": d}
        return text_item("nlfunc.build_expression", "naming a factor of an area",
                         "medium", seed, stem, key, sig("w+d"),
                         pick(pool, order, wrongs), rng, P, why)

    if mode == "product":
        d = int(d if d is not None else rng.randint(3, 99))
        key = f"f(x) = x² + {num(d)}x"
        pool = {
            "plus_x": ("added x and the offset instead of multiplying",
                       pair(f"f(x) = x² + x + {num(d)}", "x+d")),
            "plus_d": ("added the offset without multiplying it by x",
                       pair(f"f(x) = x² + {num(d)}", "d")),
            "both": ("multiplied and then added the offset a second time",
                     pair(f"f(x) = x² + {num(d)}x + {num(d)}", "dx+d")),
            "square_d": ("squared the offset as well", pair(f"f(x) = x² + {num(d)}x + "
                                                            f"{num(d * d)}", "dx+dd")),
        }
        order = ["plus_x", "plus_d", "both", "square_d"]
        why = (f"The second number is x + {num(d)}, so the product is "
               f"x(x + {num(d)}) = x² + {num(d)}x.")
        P = {"kind": "nlf_build_expression", "mode": mode, "d": d}
        return text_item("nlfunc.build_expression", "a product written as a function",
                         "hard", seed, PRODUCT_MORE.format(d=num(d)), key, sig("dx"),
                         pick(pool, order, wrongs), rng, P, why)

    if mode == "volume":
        thing, animal = CRITTERS[rng.randrange(len(CRITTERS))] if thing is None \
            else CRITTERS[thing]
        h = int(h if h is not None else rng.randint(6, 24))
        d = int(d if d is not None else rng.randint(1, 5))
        key = f"V(x) = {num(h)}x(x {MINUS} {num(d)})"
        pool = {
            "plus": ("added the offset to the length instead of subtracting it",
                     pair(f"V(x) = {num(h)}x(x + {num(d)})", h, d, "plus")),
            "height_factor": ("made the height a factor of the base instead of a "
                              "separate dimension",
                              pair(f"V(x) = x(x + {num(h)})(x {MINUS} {num(d)})",
                                   h, d, "factor_minus")),
            "both": ("made the height a factor and added the offset",
                     pair(f"V(x) = x(x + {num(h)})(x + {num(d)})", h, d, "factor_plus")),
            "no_height": ("left the height out altogether",
                          pair(f"V(x) = x(x {MINUS} {num(d)})", 1, d, "none")),
        }
        order = ["plus", "height_factor", "both", "no_height"]
        es = "" if d == 1 else "es"
        stem = VOLUME.format(thing=thing, animal=animal, h=num(h), d=num(d), es=es)
        why = (f"The width is x {MINUS} {num(d)}, so the volume is "
               f"{num(h)} · x · (x {MINUS} {num(d)}).")
        P = {"kind": "nlf_build_expression", "mode": mode, "h": h, "d": d}
        return text_item("nlfunc.build_expression", "a volume written as a function",
                         "hard", seed, stem, key, sig(h, d, "minus"),
                         pick(pool, order, wrongs), rng, P, why)

    den = int(den if den is not None else rng.choice([2, 4, 4, 8]))
    if den not in (1, 2, 4, 8):
        raise ItemError("the perimeter must print without an awkward fraction")

    def scaled(m) -> str:
        m = Q(m)
        if m == 1:
            return "a"
        if m.denominator == 1:
            return f"{num(m)}a"
        if m.numerator == 1:
            return f"a/{num(m.denominator)}"
        return f"({num(m)})a"

    mult = Q(4, den)
    key = scaled(mult)
    pool = {
        "side": ("gave the length of one edge rather than the perimeter of a face",
                 pair(scaled(Q(1, den)), Q(1, den))),
        "raw_four": ("multiplied a by 4 rather than the edge by 4",
                     pair(scaled(4), 4)),
        "six": ("used the 6 from the surface-area formula as the multiplier",
                pair(scaled(6), 6)),
        "quarter": ("divided by 4 as well as by the printed denominator",
                    pair(scaled(Q(1, 4 * den)), Q(1, 4 * den))),
    }
    order = ["side", "raw_four", "six", "quarter"]
    why = (f"A cube's surface area is 6 times the square of an edge, so the edge is "
           f"{scaled(Q(1, den))} and one face has perimeter 4 · {scaled(Q(1, den))} = "
           f"{key}.")
    P = {"kind": "nlf_build_expression", "mode": "cube", "den": den}
    return text_item("nlfunc.build_expression", "a perimeter from a surface area",
                     "hard", seed, CUBE.format(a="a", d=num(den)), key, sig(mult),
                     pick(pool, order, wrongs), rng, P, why)
