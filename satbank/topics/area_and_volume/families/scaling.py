"""Similarity and scaling.

One fact generates this whole family: if two similar figures have linear ratio
k, then lengths and perimeters scale by k, areas by k**2, and volumes by k**3.

Nearly every distractor in the source items for this skill is a student
applying the wrong power of k -- so the misconception list writes itself, and
it is the same list whether the figures are triangles, rectangles, squares,
parallelograms or cylinders.
"""

from __future__ import annotations

import random
from fractions import Fraction

from ....exact import E, PI, Exact
from ....figures import cylinder_rh, two_rectangles
from ....item import Item, ItemError, Mis, assemble, assemble_text, gridin_mistakes
from ....shapes import UNITS, Unit, unit_noun
from ..kit import decimal_text, pick

__all__ = ["similar_linear", "similar_area", "solid_scaling", "percent_change"]

TRIPLES = [("ABC", "DEF"), ("TUV", "XYZ"), ("JKL", "RST"), ("PQR", "LMN")]
QUADS = [("ABCD", "PQRS"), ("ABCD", "EFGH"), ("JKLM", "WXYZ")]


def _wrong_powers(base: Exact, k: Fraction, correct_power: int) -> dict[str, Mis]:
    """The core misconception pool: right idea, wrong power of k."""
    names = {1: "the length ratio", 2: "the square of the ratio", 3: "the cube of the ratio"}
    keys = {1: "linear", 2: "square", 3: "cube"}
    out: dict[str, Mis] = {}
    for p in (1, 2, 3):
        if p == correct_power:
            continue
        out[keys[p]] = Mis(f"scaled by {names[p]} instead of {names[correct_power]}",
                           base * E(k ** p))
    out["down"] = Mis("scaled in the wrong direction (divided instead of multiplied)",
                      base / E(k ** correct_power))
    out["unchanged"] = Mis("left the value unchanged", base)
    return out


# ------------------------------------------------------- perimeter / length

def similar_linear(rng: random.Random, seed: int, *, presentation=None, ask=None,
                   unit: Unit | None = None, fmt="mcq", k=None, base=None,
                   side=None, p1=None, sl=None, wrongs=None) -> Item:
    """Similar figures, linear ratio k, ask for a length or a perimeter."""
    presentation = presentation or rng.choice(["relation", "table", "two_sides", "rect_figure"])
    ask = ask or rng.choice(["perimeter", "side"])
    unit = unit or rng.choice(UNITS)
    a, b = rng.choice(TRIPLES)
    k = Fraction(k) if k else Fraction(rng.choice([2, 3, 4, 5, 6, 9, 10]))

    if presentation == "relation":
        base_perim = E(base) if base else E(rng.randint(4, 40) * k.denominator)
        key = base_perim * E(k)
        stem = (f"Triangle {a} and triangle {b} are similar triangles, where side {a[0]}{a[1]} "
                f"and side {b[0]}{b[1]} are corresponding sides. If {b[0]}{b[1]} = "
                f"{'' if k == 1 else k}{a[0]}{a[1]} and the perimeter of triangle {a} is "
                f"{base_perim.plain()}, what is the perimeter of triangle {b}?")
        P = {"kind": "similar_linear", "scaled": float(base_perim), "k": float(k)}
        pool = _wrong_powers(base_perim, k, 1)
        pool["three_sides"] = Mis("scaled the perimeter, then multiplied by 3 for the "
                                  "three sides as well", base_perim * E(k) * E(3))
        rationale = (f"Corresponding sides are in ratio {k}, so perimeters are too: "
                     f"{base_perim.plain()} × {k} = {key.plain()}.")
        table = None
    elif presentation == "table":
        side_n = side or rng.randint(2, 20)
        p1 = E(p1) if p1 else E(rng.randint(2 * side_n + 1, 4 * side_n))   # triangle inequality
        p2 = p1 * E(k)
        side = E(side_n)
        key = side * E(k)
        stem = (f"The table gives the perimeters of similar triangles {a} and {b}, where side "
                f"{a[0]}{a[1]} corresponds to side {b[0]}{b[1]}. The length of {a[0]}{a[1]} is "
                f"{side.plain()}. What is the length of {b[0]}{b[1]}?")
        table = [["", "Perimeter"], [f"Triangle {a}", p1.plain()], [f"Triangle {b}", p2.plain()]]
        P = {"kind": "similar_linear", "scaled": float(side), "k": float(k)}
        pool = _wrong_powers(side, k, 1)
        pool["plus_perimeter"] = Mis("added the smaller triangle's perimeter to the "
                                     "given side", side + p1)
        rationale = (f"The perimeters give ratio {p2.plain()}/{p1.plain()} = {k}, so "
                     f"{b[0]}{b[1]} = {side.plain()} × {k} = {key.plain()}.")
    elif presentation == "rect_figure":
        # Two similar rectangles drawn to scale; k comes from the marked sides.
        sw = side or rng.randint(3, 9)                     # small rectangle's height
        # the base is a multiple of the marked side, so the scaled length stays whole
        sl = sl or sw * rng.randint(2, 3)                  # small rectangle's base
        bw = E(base) if base else E(sw) * E(k)             # big rectangle's height
        kk = bw / E(sw)
        key = E(sl) * kk
        unit_word = "inches"
        stem = (f"Rectangles ABCD and QRST shown are similar, where A, B, C, and D correspond "
                f"to Q, R, S, and T, respectively. What is the length, in inches (in), of "
                f"side AD?")
        table = None
        P = {"kind": "similar_linear", "scaled": float(sl), "k": float(kk)}
        pool = {
            "down": Mis("used the ratio upside down", E(sl) / kk),
            "diff": Mis("added the difference of the marked sides instead of scaling",
                        E(sl) + bw - E(sw)),
            "unchanged": Mis("gave the corresponding side unchanged", E(sl)),
            "square": Mis("scaled by the square of the ratio", E(sl) * kk * kk),
            "marked": Mis("gave the marked side of the larger rectangle", bw),
            "product": Mis("multiplied the two marked sides instead of using their "
                           "ratio", E(sw) * bw),
        }
        rationale = (f"The marked sides give ratio {bw.plain()}/{sw} = {kk.plain()}, so "
                     f"AD = {sl} × {kk.plain()} = {key.plain()}.")
        fig = two_rectangles(f"{bw.plain()} in", f"{sw} in", f"{sl} in")
        if fmt == "spr":
            return Item("GEO.similar.linear", "similar figures", "medium", seed, stem, "spr",
                        key, key.gridin(), rationale, figure=fig, params=P,
                        spr_mistakes=gridin_mistakes(key, pick(pool, None)))
        choices, latex, reasons, letter = assemble(key, pick(pool, wrongs), rng)
        return Item("GEO.similar.linear", "similar figures", "medium", seed, stem, "mcq", key,
                    letter, rationale, choices, reasons, latex, figure=fig, params=P)
    else:  # two_sides -- a corresponding pair fixes k, then scale the perimeter
        s1_n = side or rng.randint(3, 20)
        s1 = E(s1_n)
        s2 = s1 * E(k)
        perim = E(base) if base else E(rng.randint(2 * s1_n + 1, 4 * s1_n))  # triangle inequality
        key = perim * E(k)
        stem = (f"Triangle {a} is similar to triangle {b}, where {a[0]} corresponds to {b[0]} "
                f"and {a[1]} corresponds to {b[1]}. The length of side {a[0]}{a[1]} is "
                f"{s1.plain()}, and the perimeter of triangle {a} is {perim.plain()}. The length "
                f"of side {b[0]}{b[1]} is {s2.plain()}. What is the perimeter of triangle {b}?")
        table = None
        P = {"kind": "similar_linear", "scaled": float(perim), "k": float(k)}
        pool = _wrong_powers(perim, k, 1)
        pool["side_as_k"] = Mis("used the given side length as the scale factor",
                                perim * s1)
        pool["side_as_k_sq"] = Mis("used the given side length as the scale factor and "
                                   "squared it", perim * s1 * s1)
        rationale = (f"The ratio is {s2.plain()}/{s1.plain()} = {k}, so the perimeter of {b} "
                     f"is {perim.plain()} × {k} = {key.plain()}.")

    if fmt == "spr":
        return Item("GEO.similar.linear", "similar figures", "easy", seed, stem, "spr",
                    key, key.gridin(), rationale, table=table, params=P,
                    spr_mistakes=gridin_mistakes(key, pick(pool, None)))
    choices, latex, reasons, letter = assemble(key, pick(pool, wrongs), rng)
    return Item("GEO.similar.linear", "similar figures", "easy", seed, stem, "mcq", key,
                letter, rationale, choices, reasons, latex, table=table, params=P)


# ------------------------------------------------------------------- areas

def similar_area(rng: random.Random, seed: int, *, direction=None, shape=None,
                 fmt="mcq", k=None, area=None, side=None, wrongs=None) -> Item:
    """Areas scale by k**2 -- forwards, or backwards from an area ratio."""
    direction = direction or rng.choice(["area_from_ratio", "ratio_from_sides", "side_from_areas"])
    if direction == "side_from_areas":
        shape = shape or rng.choice(["rectangle", "parallelogram"])   # a square has no "longest side"
    else:
        shape = shape or rng.choice(["triangle", "rectangle", "parallelogram", "square"])
    a, b = rng.choice(QUADS if shape in ("rectangle", "parallelogram", "square") else TRIPLES)
    k = Fraction(k) if k else Fraction(rng.choice([2, 3, 4, 5, 6, 9]))
    noun = shape.capitalize()

    if direction == "area_from_ratio":
        area1 = E(area) if area else E(rng.randint(3, 60))
        key = area1 * E(k ** 2)
        stem = (f"{noun} {a} is similar to {shape} {b}. The length of each side of {shape} {b} "
                f"is {k} times the length of its corresponding side of {shape} {a}. The area of "
                f"{shape} {a} is {area1.plain()} square centimeters. What is the area, in square "
                f"centimeters, of {shape} {b}?")
        P = {"kind": "similar_area", "mode": "area_from_ratio", "base": float(area1),
             "k": float(k)}
        pool = _wrong_powers(area1, k, 2)
        pool["plus_ratio"] = Mis("added the scale factor to the area instead of "
                                 "multiplying by its square", area1 + E(k))
        pool["plus_area"] = Mis("added the original area to the scaled area",
                                area1 + area1 * E(k ** 2))
        rationale = f"Areas scale by the square of the ratio: {area1.plain()} x {k}² = {key.plain()}."
    elif direction == "ratio_from_sides":
        key = E(k ** 2)
        stem = (f"Square A has side lengths that are {k} times the side lengths of square B. "
                f"The area of square A is m times the area of square B. What is the value of m?")
        P = {"kind": "similar_area", "mode": "ratio_from_sides", "k": float(k)}
        pool = {
            "linear": Mis("gave the length ratio instead of the area ratio", E(k)),
            "double": Mis("doubled the length ratio", E(2 * k)),
            "half": Mis("halved the length ratio", E(Fraction(k, 2))),
            "cube": Mis("cubed the ratio as if it were a volume", E(k ** 3)),
        }
        rationale = f"Area ratio is the square of the length ratio: {k}² = {key.plain()}."
    else:  # side_from_areas -- k comes out of a square root
        k2 = k ** 2
        small = E(side) if side else E(rng.randint(2, 20))
        area_small = E(area) if area else small ** 2 * E(rng.randint(1, 4))
        area_big = area_small * E(k2)
        big_side = small * E(k)
        key = small
        stem = (f"{noun} {a} is similar to {shape} {b}. The area of {shape} {a} is "
                f"{area_big.plain()} square inches, and the area of {shape} {b} is "
                f"{area_small.plain()} square inches. The length of the longest side of {shape} "
                f"{a} is {big_side.plain()} inches. What is the length, in inches, of the longest "
                f"side of {shape} {b}?")
        P = {"kind": "similar_area", "mode": "side_from_areas", "big_side": float(big_side),
             "k": float(k)}
        pool = {
            "area_ratio_as_length": Mis("used the area ratio as the length ratio",
                                        big_side / E(k2)),
            "ratio_itself": Mis("gave the area ratio itself", E(k2)),
            "unchanged": Mis("left the length unchanged", big_side),
            "multiplied": Mis("multiplied instead of divided", big_side * E(k)),
        }
        rationale = (f"Area ratio {area_big.plain()}/{area_small.plain()} = {k2}, so the length "
                     f"ratio is {k}, and {big_side.plain()}/{k} = {key.plain()}.")

    if fmt == "spr":
        return Item("GEO.similar.area", "similar figures", "medium", seed, stem, "spr",
                    key, key.gridin(), rationale, params=P,
                    spr_mistakes=gridin_mistakes(key, pick(pool, None)))
    choices, latex, reasons, letter = assemble(key, pick(pool, wrongs), rng)
    return Item("GEO.similar.area", "similar figures", "medium", seed, stem, "mcq", key,
                letter, rationale, choices, reasons, latex, params=P)


# ------------------------------------------------------- solids: k**3 and mixed

def solid_scaling(rng: random.Random, seed: int, *, mode=None, fmt="mcq",
                  rf=None, hf=None, v=None, pair=None, wrongs=None) -> Item:
    """A cylinder whose radius and height scale by different factors."""
    mode = mode or rng.choice(["volume_multiple", "which_pair"])
    if mode == "volume_multiple":
        rf = Fraction(rf) if rf else Fraction(rng.choice([2, 3, Fraction(1, 2), 4]))
        hf = Fraction(hf) if hf else Fraction(rng.choice([2, 3, Fraction(1, 2), Fraction(1, 3)]))
        v = E(v) if v else E(rng.randint(10, 90))
        factor = rf ** 2 * hf
        key = v * E(factor)
        stem = (f"The volume of right circular cylinder A is {v.plain()} cubic centimeters. What "
                f"is the volume, in cubic centimeters, of a right circular cylinder with "
                f"{_times(rf)} the radius and {_times(hf)} the height of cylinder A?")
        P = {"kind": "solid_scaling", "mode": "volume_multiple", "v": float(v),
             "rf": float(rf), "hf": float(hf)}
        pool = {
            "linear_radius": Mis("scaled the radius linearly instead of squaring it",
                                 v * E(rf * hf)),
            "radius_only": Mis("applied the radius factor only", v * E(rf ** 2)),
            "height_only": Mis("applied the height factor only", v * E(hf)),
            "cube_radius": Mis("cubed the radius factor", v * E(rf ** 3 * hf)),
            "unchanged": Mis("left the volume unchanged", v),
        }
        rationale = (f"Volume scales by (radius factor)² × (height factor) = {rf}² × {hf} = "
                     f"{factor}, so {v.plain()} x {factor} = {key.plain()}.")
        choices, latex, reasons, letter = assemble(key, pick(pool, wrongs), rng)
        return Item("GEO.scaling.cylinder", "solid scaling", "hard", seed, stem, "mcq", key,
                    letter, rationale, choices, reasons, latex, params=P)

    # which_pair: give the volume multiple, ask which (R, H) produces it
    a, b = pair or rng.choice([(2, 3), (3, 2), (5, 2), (7, 8), (4, 5), (6, 3), (3, 7)])
    mult = a ** 2 * b
    P = {"kind": "solid_scaling", "mode": "which_pair", "a": a, "b": b, "mult": mult}
    key_text = f"R = {a}r and H = {b}h"
    stem = (f"The figure shown is a right circular cylinder with a radius of r and a height of h. "
            f"A second right circular cylinder (not shown) has a volume that is {mult} times as "
            f"large as the volume of the cylinder shown. Which of the following could represent "
            f"the radius R, in terms of r, and the height H, in terms of h, of the second "
            f"cylinder?")
    pool = {
        "swapped": Mis(f"swapped the factors ({b}^2 x {a} = {b*b*a}, not {mult})",
                       f"R = {b}r and H = {a}h"),
        "square_height": Mis("squared the height factor instead of the radius factor",
                             f"R = {b}r and H = {a*a}h"),
        "square_both": Mis("put the squared factor on the radius as well",
                           f"R = {a*a}r and H = {b}h"),
    }
    choices, reasons, letter = assemble_text(key_text, pick(pool, wrongs), rng)
    return Item("GEO.scaling.which_pair", "solid scaling", "hard", seed, stem, "mcq",
                E(mult), letter,
                f"V = πR²H = π({a}r)²({b}h) = {mult}πr²h.",
                choices, reasons, choices, figure=cylinder_rh(), params=P)


def _times(f: Fraction) -> str:
    return {Fraction(1, 2): "half", Fraction(1, 3): "one third", Fraction(2): "twice",
            Fraction(3): "three times", Fraction(4): "four times"}.get(f, f"{f} times")


# ------------------------------------------------------------ percent change

def percent_change(rng: random.Random, seed: int, *, fmt=None, pct=None,
                   area=None, up=None, wrongs=None) -> Item:
    """Both dimensions change by p%; the area changes by (1 + p/100)**2."""
    fmt = fmt or rng.choice(["spr", "mcq"])
    pct = pct or rng.choice([10, 20, 25, 30, 40, 50])
    up = rng.random() < 0.75 if up is None else up
    ratio = Fraction(100 + pct, 100) if up else Fraction(100 - pct, 100)
    area = E(area) if area else E(rng.choice([120, 150, 180, 200, 240, 300, 360, 400, 480, 600]))
    key = area * E(ratio ** 2)
    P = {"kind": "percent_change", "area": float(area), "ratio": float(ratio)}
    word = "increased" if up else "decreased"
    thing = rng.choice(["poster", "photograph", "rug", "banner", "tile", "canvas"])
    stem = (f"A rectangular {thing} has an area of {area.plain()} square inches. A copy of the "
            f"{thing} is made in which the length and width of the original {thing} are each "
            f"{word} by {pct}%. What is the area, in square inches, of the copy?")
    pool = {
        "once": Mis("applied the percent change once instead of to both dimensions",
                    area * E(ratio)),
        "additive": Mis(f"{word} the area by {pct}% twice, additively",
                        area * E(1 + 2 * (ratio - 1))),
        "cube": Mis("cubed the ratio as if it were a volume", area * E(ratio ** 3)),
        "unchanged": Mis("left the area unchanged", area),
    }
    rationale = (f"Each dimension is multiplied by {ratio}, so the area is multiplied by "
                 f"({ratio})² = {ratio**2}: {area.plain()} × {ratio**2} = "
                 f"{decimal_text(key)}.")
    if fmt == "spr":
        return Item("GEO.scaling.percent", "area scaling", "hard", seed, stem, "spr", key,
                    key.gridin(), rationale, params=P,
                    spr_mistakes=gridin_mistakes(key, pick(pool, None)))
    choices, latex, reasons, letter = assemble(key, pick(pool, wrongs), rng,
                                               fmt_value=decimal_text)
    return Item("GEO.scaling.percent", "area scaling", "hard", seed, stem, "mcq", key, letter,
                rationale, choices, reasons, latex, params=P)
