"""The three hard items whose answer is an expression with a letter in it.

None of these is arithmetic. Each is a rearrangement, and the options differ
by where a term was moved to -- inside the fraction, outside it, into the
denominator -- which is exactly what a student gets wrong.
"""

from __future__ import annotations

import random
from fractions import Fraction as Q

from ....item import Item, ItemError, Mis, assemble
from ...linear_functions.common import choose, dec, ex, numtext, q
from .define import _text_item

__all__ = ["parameter_intercept", "affine_conversion", "unit_relation"]


# ------------------------------------------------- an intercept with a letter

def parameter_intercept(rng: random.Random, seed: int, *, c=None, a=None, b=None, e=None,
                        k=None, letter=None) -> Item:
    """f(x) = cd(ax + b) + e, and the x-intercept of y = f(x) + k."""
    letter = letter or rng.choice(["d", "c", "k", "p"])
    var = "x"
    c = int(c if c is not None else rng.randint(2, 9))
    a = int(a if a is not None else rng.randrange(5, 45, 5))
    b = int(b if b is not None else rng.randint(3, 30))
    e = int(e if e is not None else rng.randint(2, 30))
    k = int(k if k is not None else rng.randint(2, 15))
    if letter == var:
        raise ItemError("the constant needs a letter other than the variable")
    cb, ca, top = c * b, c * a, e + k
    stem = (f"f({var}) = {numtext(c)}{letter}({numtext(a)}{var} + {numtext(b)}) + "
            f"{numtext(e)} Which of the following represents the x-intercept of the graph "
            f"of y = f({var}) + {numtext(k)} in the xy-plane, where {letter} is a "
            f"constant?")
    key = (f"((-{numtext(cb)}{letter} - {numtext(top)})/({numtext(ca)}{letter}), 0)")
    wrongs = [Mis("left the added constant outside the fraction",
                  (f"({numtext(k)} - ({numtext(cb)}{letter} + {numtext(e)})/"
                   f"({numtext(ca)}{letter}), 0)", ["outside", cb, e, ca, k])),
              Mis("added the constant to the denominator instead of the numerator",
                  (f"(-{numtext(b + e)}/({numtext(ca)}{letter} + {numtext(k)}), 0)",
                   ["denominator", b + e, ca, k])),
              Mis("did not divide by the coefficient of x",
                  (f"({numtext(cb)}{letter} + {numtext(top)}, 0)",
                   ["undivided", cb, top])),
              Mis("changed the sign of the whole numerator",
                  (f"(({numtext(cb)}{letter} + {numtext(top)})/({numtext(ca)}{letter}), 0)",
                   ["unsigned", cb, top, ca]))]
    P = {"kind": "lf_param_intercept", "c": c, "a": a, "b": b, "e": e, "k": k}
    rationale = (f"Expanding gives y = {numtext(ca)}{letter}{var} + {numtext(cb)}{letter} "
                 f"+ {numtext(top)}, which is zero at x = -({numtext(cb)}{letter} + "
                 f"{numtext(top)})/({numtext(ca)}{letter}).")
    return _text_item("lin.parameter_intercept", "an intercept with a parameter", "hard",
                      seed, stem, key, ["ratio", cb, top, ca], wrongs, rng, P, rationale)


# ------------------------------------------------------- a scaled conversion

CONV_CTX = [
    dict(text="F(x) = ({p}/{qd})(x - {s}) + {t} The function F gives the temperature, in "
              "degrees Fahrenheit, that corresponds to a temperature of x kelvins. If a "
              "temperature increased by {delta} kelvins, by how much did the temperature "
              "increase, in degrees Fahrenheit?",
         inverse="The equation h = {p}(v - {s})/{qd} + {t} gives the corresponding "
                 "temperature h, in degrees Fahrenheit, of any substance that has a "
                 "temperature of v kelvins, where v > 0. If a substance has a temperature "
                 "of {value} degrees Fahrenheit, what is the corresponding temperature, in "
                 "kelvins, of this substance?",
         p=9, qd=5, s=Q(27315, 100), t=32, places=2),
]


def affine_conversion(rng: random.Random, seed: int, *, ctx=0, delta=None, ask=None,
                      target=None, fmt=None) -> Item:
    """A conversion of the form (p/q)(x - s) + t: a change, or a value back."""
    d = CONV_CTX[ctx]
    ask = ask or rng.choice(["change", "inverse"])
    p, qd, s, t = q(d["p"]), q(d["qd"]), q(d["s"]), q(d["t"])
    scale = p / qd
    if ask == "change":
        delta = q(delta) if delta is not None else Q(rng.randrange(50, 1500, 10), 100)
        key = scale * delta
        stem = d["text"].format(p=numtext(p), qd=numtext(qd), s=numtext(s, "dec"),
                                t=numtext(t), delta=dec(delta, 2))
        mistakes = [Mis("added the constant term to a difference that does not need it",
                        key + t),
                    Mis("substituted the change into the whole formula",
                        scale * (s - delta)),
                    Mis("substituted the change into the whole formula and kept the "
                        "constant term", scale * (s - delta) + t),
                    Mis("inverted the scale factor", delta * qd / p)]
        rationale = (f"A change of {dec(delta, 2)} scales by {numtext(p)}/{numtext(qd)}, "
                     f"giving {dec(key, 2)}.")
        P = {"kind": "lf_affine", "ask": ask, "p": [p.numerator, p.denominator],
             "qd": [qd.numerator, qd.denominator], "s": [s.numerator, s.denominator],
             "t": [t.numerator, t.denominator],
             "delta": [delta.numerator, delta.denominator], "places": 2}
        fmt = fmt or "mcq"
    else:
        target = q(target) if target is not None else Q(rng.randrange(20000, 60000, 1), 100)
        key = (target - t) / scale + s
        if key <= 0:
            raise ItemError("a kelvin temperature must be positive")
        stem = d["inverse"].format(p=numtext(p), qd=numtext(qd), s=numtext(s, "dec"),
                                   t=numtext(t), value=dec(target, 2))
        mistakes = [Mis("added the shift instead of subtracting the constant term",
                        (target + t) / scale + s),
                    Mis("left the shift out", (target - t) / scale),
                    Mis("inverted the scale factor", (target - t) * scale + s)]
        rationale = (f"({dec(target, 2)} - {numtext(t)}) x {numtext(qd)}/{numtext(p)} + "
                     f"{numtext(s, 'dec')} = {numtext(key, 'dec')}.")
        P = {"kind": "lf_affine", "ask": ask, "p": [p.numerator, p.denominator],
             "qd": [qd.numerator, qd.denominator], "s": [s.numerator, s.denominator],
             "t": [t.numerator, t.denominator],
             "target": [target.numerator, target.denominator], "places": None}
        fmt = fmt or "spr"
    keyx = ex(key)
    if fmt == "spr":
        if not keyx.is_rational or len(keyx.gridin()) > 8:
            raise ItemError("the answer does not fit a grid-in")
        return Item("lin.affine_conversion", "a scaled linear conversion", "hard", seed,
                    stem, "spr", keyx, keyx.gridin(), rationale, params=P)
    mistakes = [Mis(r.reason, ex(r.value)) for r in mistakes if r.value is not None]
    choices, latex, reasons, letter = choose(
        keyx, mistakes, rng, fmt_value=lambda v: dec(v, 2), signed=True, fillers="shift")
    return Item("lin.affine_conversion", "a scaled linear conversion", "hard", seed, stem,
                "mcq", keyx, letter, rationale, choices, reasons, latex, params=P)


# ------------------------------------------------ a table of equivalent units

NUTRIENTS = [("Protein", "p"), ("Fat", "f"), ("Carbohydrate", "c")]
TABLE_HEAD = ["Macronutrient", "Food calories", "Kilojoules"]
RATIO = Q(4184, 1000)


def unit_relation(rng: random.Random, seed: int, *, mode=None, cal=None, fat=None,
                  total=None) -> Item:
    """The energy table: a conversion factor, or one variable in terms of two."""
    mode = mode or rng.choices(["solve", "ratio"], weights=[7, 3])[0]
    cal = int(cal if cal is not None else rng.randint(3, 7))
    fat = int(fat if fat is not None else rng.randint(cal + 2, 14))
    kj = [q(round(float(RATIO * v), 1)) for v in (cal, fat, cal)]
    table = [list(TABLE_HEAD)] + [
        [NUTRIENTS[i][0], dec(q(v), 1), dec(kj[i], 1)]
        for i, v in enumerate((cal, fat, cal))]
    lead = ("The table above gives the typical amounts of energy per gram, expressed in "
            "both food calories and kilojoules, of the three macronutrients in food. ")
    if mode == "ratio":
        r = q(round(float(kj[0] / cal), 1))
        inv = q(round(float(cal / kj[0]), 2))
        if r == inv or r == 0:
            raise ItemError("the factor and its reciprocal must differ")
        stem = lead + ("If x food calories is equivalent to k kilojoules, of the "
                       "following, which best represents the relationship between x and "
                       "k ?")
        key = f"k = {dec(r)}x"
        wrongs = [Mis("inverted the conversion factor", (f"k = {dec(inv)}x",
                                                         ["k_eq", inv.numerator,
                                                          inv.denominator])),
                  Mis("wrote the conversion the wrong way round",
                      (f"x = {dec(r)}k", ["x_eq", r.numerator, r.denominator])),
                  Mis("multiplied the two quantities instead of relating them",
                      (f"xk = {dec(r)}", ["prod", r.numerator, r.denominator])),
                  Mis("used the fat row's factor instead of a shared one",
                      (f"k = {dec(q(round(float(kj[1] / fat), 1)))}x",
                       ["k_eq", q(round(float(kj[1] / fat), 1)).numerator,
                        q(round(float(kj[1] / fat), 1)).denominator]))]
        P = {"kind": "lf_unit_relation", "mode": mode, "cal": cal, "fat": fat,
             "kj0": [kj[0].numerator, kj[0].denominator]}
        rationale = (f"{dec(q(cal), 1)} food calories is {dec(kj[0], 1)} kilojoules, so "
                     f"k is about {dec(r)} times x.")
        return _text_item("lin.unit_relation", "a conversion from a table", "medium", seed,
                          stem, key, ["k_eq", r.numerator, r.denominator], wrongs, rng, P,
                          rationale, table=table)

    total = int(total if total is not None else rng.randrange(cal * fat, 40 * fat, fat))
    if total % fat:
        raise ItemError("the total must divide by the fat row for a tidy constant")
    const = Q(total, fat)
    frac = Q(cal, fat)
    stem = lead + (f"If the {numtext(total)} food calories in a granola bar come entirely "
                   f"from p grams of protein, f grams of fat, and c grams of "
                   f"carbohydrate, which of the following expresses f in terms of p and "
                   f"c ?")
    key = f"f = {numtext(const)} - ({numtext(frac)})(p + c)"
    wrongs = [Mis("added the other two terms instead of subtracting them",
                  (f"f = {numtext(const)} + ({numtext(frac)})(p + c)",
                   ["s", const.numerator, const.denominator, 1, frac.numerator,
                    frac.denominator, "sum"])),
              Mis("subtracted the carbohydrate term instead of adding it",
                  (f"f = {numtext(const)} - ({numtext(frac)})(p - c)",
                   ["s", const.numerator, const.denominator, -1, frac.numerator,
                    frac.denominator, "diff"])),
              Mis("inverted the ratio of the two energy values and added",
                  (f"f = {numtext(const)} + ({numtext(1 / frac)})(p + c)",
                   ["s", const.numerator, const.denominator, 1, (1 / frac).numerator,
                    (1 / frac).denominator, "sum"])),
              Mis("inverted the ratio of the two energy values",
                  (f"f = {numtext(const)} - ({numtext(1 / frac)})(p + c)",
                   ["s", const.numerator, const.denominator, -1, (1 / frac).numerator,
                    (1 / frac).denominator, "sum"]))]
    P = {"kind": "lf_unit_relation", "mode": "solve", "cal": cal, "fat": fat,
         "total": total}
    rationale = (f"{numtext(total)} = {numtext(cal)}p + {numtext(fat)}f + {numtext(cal)}c "
                 f"rearranges to f = {numtext(const)} - ({numtext(frac)})(p + c).")
    return _text_item("lin.unit_relation", "solving a linear relation for one variable",
                      "hard", seed, stem, key,
                      ["s", const.numerator, const.denominator, -1, frac.numerator,
                       frac.denominator, "sum"], wrongs, rng, P, rationale, table=table)
