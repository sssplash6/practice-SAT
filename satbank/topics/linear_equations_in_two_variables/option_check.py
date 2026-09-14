"""Read the four printed options back, and check only one of them is right.

`satbank check` asks whether the key is correct. It never asks whether a
*distractor* is also correct, because nothing in the engine reads the wrong
options as mathematics -- they are strings that `assemble` and `assemble_text`
ordered and shuffled. An item with two right answers therefore passes every
gate the engine has.

This topic is exposed to that in a particular way: two equations can be the
same line written differently (2x + 4y = 10 and x + 2y = 5), and two equations
can model the same situation. So this script parses the printed stem, the
printed table and the drawn SVG back into linear algebra, decides every option
from its own printed text, and asserts that exactly one option has the property
the stem asks for and that it is the keyed one. It imports no template, no
renderer and no solver: `generate` is used only to obtain the finished item,
exactly as a student would receive it.

    PYTHONPATH=. python3 satbank/topics/linear_equations_in_two_variables/option_check.py
    PYTHONPATH=. python3 .../option_check.py --draws 2000 --template le2.which_table

Exits non-zero on the first kind of defect it finds, and prints the item.
"""

from __future__ import annotations

import argparse
import re
import sys
from fractions import Fraction as Q

from satbank.item import ItemError
from satbank.registry import generate

MINUS = "−"


class Unreadable(Exception):
    """The printed text is not something this reader understands."""


# --------------------------------------------------- printed text -> numbers

def num(text: str) -> Q:
    """A printed number: 8, -11, 1,277.94, 9/7, 3.5, (3/4)."""
    t = text.replace(MINUS, "-").replace(",", "").replace(" ", "").strip()
    if t.startswith("(") and t.endswith(")"):
        t = t[1:-1]
    if t.startswith("-(") and t.endswith(")"):
        t = "-" + t[2:-1]
    if "/" in t:
        a, b = t.split("/", 1)
        return Q(a) / Q(b)
    return Q(t)


# one term of a printed side: a sign, then a coefficient written as a bracketed
# fraction, a loose fraction, a decimal or a whole number, then a variable
TERM = re.compile(r"([+-]?)(?:\((\d+)/(\d+)\)|(\d+)/(\d+)|(\d+\.\d+)|(\d+))?([a-zA-Z])?")
PRODUCT = re.compile(r"^([+-]?)\(?([\d.,]+)\)?\(([\d.,]+)\)$")
SCALED_SUM = re.compile(r"^([+-]?)([\d.,]*)\(([a-zA-Z])\s*\+\s*([a-zA-Z])\)$")


def side(text: str) -> tuple[dict, Q]:
    """One side of an equation as ({variable: coefficient}, constant).

    Handles the four layouts this topic prints: a sum of terms, a product of
    two bracketed numbers -- (0.04)(24) and 35(1.49) -- a number times a
    bracketed sum of variables, and a bare product of two variables.
    """
    t = text.replace(MINUS, "-").replace(",", "").replace(" ", "")
    m = PRODUCT.match(t)
    if m:
        v = num(m.group(2)) * num(m.group(3))
        return {}, -v if m.group(1) == "-" else v
    m = SCALED_SUM.match(t)
    if m:
        k = num(m.group(2)) if m.group(2) else Q(1)
        if m.group(1) == "-":
            k = -k
        return {m.group(3): k, m.group(4): k}, Q(0)
    if re.fullmatch(r"[+-]?[\d.]*[a-zA-Z]{2,}", t):
        raise Unreadable(f"{text!r} multiplies the variables together")
    coef, const, i = {}, Q(0), 0
    while i < len(t):
        m = TERM.match(t, i)
        if m is None or m.end() == i:
            raise Unreadable(f"{text!r} at {t[i:]!r}")
        sign, pn, pd, fn, fd, dec, whole, var = m.groups()
        if pn:
            v = Q(int(pn), int(pd))
        elif fn:
            v = Q(int(fn), int(fd))
        elif dec:
            v = Q(dec)
        elif whole:
            v = Q(int(whole))
        elif var:
            v = Q(1)
        else:
            raise Unreadable(f"{text!r} at {t[i:]!r}")
        if sign == "-":
            v = -v
        if var:
            coef[var] = coef.get(var, Q(0)) + v
        else:
            const += v
        i = m.end()
    return coef, const


def row(eq: str) -> tuple[dict, Q]:
    """A printed equation as the row (coefficients, constant), with everything
    moved to the left of the equals sign. `3y = 5x` and `-5x + 3y = 0` read
    alike, and `(1/5)x + (1/7)y - 70 = 0` reads as its two coefficients."""
    if eq.count("=") != 1:
        raise Unreadable(eq)
    lhs, rhs = eq.split("=")
    lc, lk = side(lhs)
    rc, rk = side(rhs)
    for v, c in rc.items():
        lc[v] = lc.get(v, Q(0)) - c
    return {v: c for v, c in lc.items() if c != 0}, rk - lk


def same_line(a, b) -> bool:
    """Two rows describe the same line when one is a nonzero multiple of the
    other. This is the check that `2x + 4y = 10` and `x + 2y = 5` must fail."""
    (ca, ka), (cb, kb) = a, b
    names = sorted(set(ca) | set(cb))
    if not names:
        return False
    va = [ca.get(n, Q(0)) for n in names] + [ka]
    vb = [cb.get(n, Q(0)) for n in names] + [kb]
    lead = next((i for i, v in enumerate(va) if v != 0), None)
    if lead is None or vb[lead] == 0:
        return False
    r = vb[lead] / va[lead]
    return all(x * r == y for x, y in zip(va, vb))


def as_line(r) -> tuple[Q, Q]:
    """A row in x and y as (slope, y-intercept)."""
    coef, const = r
    a, b = coef.get("x", Q(0)), coef.get("y", Q(0))
    if b == 0:
        raise Unreadable("a vertical line has no slope")
    return -a / b, const / b


def satisfies(r, values: dict) -> bool:
    coef, const = r
    if set(coef) - set(values):
        return False
    return sum(c * values[v] for v, c in coef.items()) == const


def point(text: str) -> tuple[Q, Q]:
    m = re.fullmatch(r"\(([^,]+),([^,]+)\)", text.strip())
    if m is None:
        raise Unreadable(text)
    return num(m.group(1)), num(m.group(2))


def pairs(text: str) -> list:
    """`(0, 8), (2, 148), (4, 288)` as three points. The separator between the
    pairs is `), (`, which a thousands separator inside a pair cannot be."""
    out = [p.strip(" ()") for p in text.split("), (")]
    if len(out) != 3:
        raise Unreadable(text)
    got = []
    for p in out:
        parts = [x for x in p.split(", ") if x.strip()]
        if len(parts) != 2:
            raise Unreadable(text)
        got.append((num(parts[0]), num(parts[1])))
    return got


LETTERED = re.compile(r"^([+-]?)(\d*|[A-Z])([a-z])\s*([+-])\s*(\d*|[A-Z])([a-z])"
                      r"\s*=\s*(-?[\d,]+)$")


def lettered(option: str) -> tuple:
    """`18x + Ry = 36` as (x-coefficient, y-coefficient, constant), where one of
    the two coefficients is the letter rather than a number.

    A plain reader that treats `Ry` as two variables gets the wrong line, which
    is exactly the sort of thing this file exists to avoid: the letter is a
    coefficient, not a second unknown.
    """
    t = option.replace(MINUS, "-").replace(" ", "")
    m = re.fullmatch(r"([+-]?)(\d*|[A-Z])([a-z])([+-])(\d*|[A-Z])([a-z])=(-?[\d,]+)",
                     t)
    if m is None:
        raise Unreadable(option)
    s1, c1, v1, op, c2, v2, k = m.groups()

    def coef(txt, sign):
        if txt.isalpha():
            return txt
        value = Q(int(txt)) if txt else Q(1)
        return -value if sign == "-" else value

    return ((v1, coef(c1, s1)), (v2, coef(c2, "-" if op == "-" else "")), num(k))


AFFINE = re.compile(r"([+-]?)\(?(\d*)([a-zA-Z]?)\)?(?:/(\d+))?")


def affine(text: str, var: str) -> tuple[Q, Q]:
    """`-(3r)/2 + 7/2` as (coefficient of r, constant)."""
    t = text.replace(MINUS, "-").replace(" ", "")
    slope, const, i = Q(0), Q(0), 0
    while i < len(t):
        m = AFFINE.match(t, i)
        if m is None or m.end() == i:
            raise Unreadable(f"{text!r} at {t[i:]!r}")
        sign, whole, name, den = m.groups()
        if name and name != var:
            raise Unreadable(f"{text!r} mentions {name!r}, not {var!r}")
        v = Q(int(whole) if whole else 1, int(den) if den else 1)
        if sign == "-":
            v = -v
        if name:
            slope += v
        else:
            const += v
        i = m.end()
    return slope, const


def parametric(text: str, var: str) -> tuple:
    m = re.fullmatch(r"\((.+),(.+)\)", text.strip())
    if m is None:
        raise Unreadable(text)
    return affine(m.group(1), var), affine(m.group(2), var)


# ------------------------------------------------ a drawn figure -> a line

def line_from_grid(svg: str) -> tuple[Q, Q]:
    """The drawn line as (slope, intercept), read back out of a coordinate grid.

    The axes locate the origin in pixels and the spacing of the gridlines gives
    the pixels per unit. Nothing about the item's parameters is consulted: this
    is what a reader with a ruler would get, so it checks the picture against
    the options rather than the options against each other.
    """
    ax = re.findall(r'<line class="ax" x1="([^"]+)" y1="([^"]+)" '
                    r'x2="([^"]+)" y2="([^"]+)"', svg)
    horizontal = [a for a in ax if a[1] == a[3]]
    vertical = [a for a in ax if a[0] == a[2]]
    if len(horizontal) != 1 or len(vertical) != 1:
        raise Unreadable("the axes are not one horizontal and one vertical")
    y0, x0 = Q(horizontal[0][1]), Q(vertical[0][0])
    gr = re.findall(r'<line class="gr" x1="([^"]+)" y1="[^"]+" '
                    r'x2="([^"]+)" y2="[^"]+"', svg)
    xs = sorted({Q(a) for a, b in gr if a == b})
    gaps = {b - a for a, b in zip(xs, xs[1:])}
    if len(gaps) != 1:
        raise Unreadable("the gridlines are not evenly spaced")
    px = gaps.pop()
    seg = re.findall(r'<line class="sg" x1="([^"]+)" y1="([^"]+)" '
                     r'x2="([^"]+)" y2="([^"]+)"', svg)
    if len(seg) != 1:
        raise Unreadable(f"{len(seg)} lines drawn, not one")
    x1, ya, x2, yb = seg[0]
    ax1, ay1 = (Q(x1) - x0) / px, (y0 - Q(ya)) / px
    ax2, ay2 = (Q(x2) - x0) / px, (y0 - Q(yb)) / px
    if ax1 == ax2:
        raise Unreadable("a vertical drawn line has no slope")
    m = (ay2 - ay1) / (ax2 - ax1)
    return m, ay1 - m * ax1


def intercepts_from_chart(svg: str) -> tuple[Q, Q]:
    """The two intercepts the chart draws, as whole numbers.

    A chart carries no gridlines through the origin, so the scale comes from
    the printed tick labels: two of them on each axis fix the affine map from
    pixels back to the quantities the axes are named for.
    """
    xt = [(Q(x), Q(lab)) for x, lab in re.findall(
        r'<text class="lb" x="([^"]+)" y="[^"]+" text-anchor="middle">([^<]+)</text>',
        svg)]
    yt = [(Q(y), Q(lab)) for y, lab in re.findall(
        r'<text class="lb" x="[^"]+" y="([^"]+)" text-anchor="end">([^<]+)</text>', svg)]
    if len(xt) < 2 or len(yt) < 2:
        raise Unreadable("too few tick labels to fix the scale")

    def mapper(ticks, shift=Q(0)):
        (p1, v1), (p2, v2) = ticks[0], ticks[-1]
        if p1 == p2:
            raise Unreadable("two tick labels at one pixel")
        k = (v2 - v1) / (p2 - p1)
        return lambda p: v1 + (p - p1 - shift) * k

    fx = mapper(xt)
    fy = mapper([(p - 4, v) for p, v in yt])          # the label sits 4px low
    pts = re.findall(r'<polyline class="ln" points="([^"]+)"', svg)
    if len(pts) != 1:
        raise Unreadable(f"{len(pts)} polylines, not one")
    coords = [tuple(Q(c) for c in p.split(",")) for p in pts[0].split()]
    (px1, py1), (px2, py2) = coords[0], coords[-1]
    x1, y1, x2, y2 = fx(px1), fy(py1), fx(px2), fy(py2)
    if x1 == x2:
        raise Unreadable("a vertical plotted line has no slope")
    m = (y2 - y1) / (x2 - x1)
    b = y1 - m * x1
    if m == 0:
        raise Unreadable("the plotted line is flat")
    # the pixels are rounded to two places, so the recovered ends are within a
    # hair of the whole numbers the axes count in; anything further off is a
    # picture that does not match its own scale
    xi, yi = -b / m, b
    wx, wy = round(float(xi)), round(float(yi))
    if abs(float(xi) - wx) > 0.02 * max(1, abs(wx)) or \
       abs(float(yi) - wy) > 0.02 * max(1, abs(wy)):
        raise Unreadable(f"the drawn ends ({float(xi):.3f}, {float(yi):.3f}) are not "
                         f"whole numbers")
    return Q(wx), Q(wy)


# ------------------------------------------------------- reading the stem

def stem_number(stem: str, pattern: str) -> Q:
    m = re.search(pattern, stem)
    if m is None:
        raise Unreadable(f"{pattern!r} not in the stem")
    return num(m.group(1))


N = r"(-?\d[\d,]*(?:\.\d+)?)"
POLYGON_SIDES = {"triangles": 3, "squares": 4, "pentagons": 5, "hexagons": 6,
                 "octagons": 8}


def situation_model_standard(stem: str):
    """The row the situation itself demands, read out of the printed stem."""
    if "prepare a sandwich" in stem:
        a = stem_number(stem, rf"employee {N} minutes to prepare a sandwich")
        b = stem_number(stem, rf"and {N} minutes to prepare a salad")
        c = stem_number(stem, rf"total of {N} minutes")
        return {"x": a, "y": b}, c
    if "10-ride pass" in stem:
        a = stem_number(stem, rf"A 10-ride pass costs \${N}")
        b = stem_number(stem, rf"a single-ride pass costs \${N}")
        c = stem_number(stem, rf"Tony spends \${N} per month")
        return {"g": a, "t": b}, c
    if "buys forks" in stem:
        a = stem_number(stem, rf"forks for \${N} each")
        b = stem_number(stem, rf"plates for \${N} each")
        c = stem_number(stem, rf"is \${N}\.")
        return {"x": a, "y": b}, c
    if "assignment worth" in stem:
        c = stem_number(stem, rf"assignment worth {N} points")
        a = stem_number(stem, rf"questions worth {N} points?  ?and")
        b = stem_number(stem, rf"and questions worth {N} points")
        return {"x": a, "y": b}, c
    if "side length r" in stem:
        n1, p1 = re.search(rf"A total of {N} (\w+) each have side length r", stem).groups()
        n2, p2 = re.search(rf"A total of {N} (\w+) each have side length t", stem).groups()
        c = stem_number(stem, rf"perimeters of all these .+? is {N}\.")
        return ({"r": num(n1) * POLYGON_SIDES[p1], "t": num(n2) * POLYGON_SIDES[p2]}, c)
    if "total expense budget" in stem:
        c = stem_number(stem, rf"and {N} million dollars for all other expenses")
        return {"x": Q(1), "y": Q(-1)}, c
    raise Unreadable("an unfamiliar situation")


def situation_model_percent(stem: str):
    if "Fertilizer A contains" in stem:
        pa = stem_number(stem, rf"Fertilizer A contains {N}% filler")
        pb = stem_number(stem, rf"Fertilizer B contains {N}% filler")
        c = stem_number(stem, rf"total of\s+{N} pounds of filler")
        return {"x": pa / 100, "y": pb / 100}, c
    if "low-salt mixture" in stem:
        pa = stem_number(stem, rf"low-salt mixture, which is {N}%")
        pb = stem_number(stem, rf"high-salt mixture, which is {N}%")
        v = stem_number(stem, rf"to create {N} kilograms")
        pm = stem_number(stem, rf"mixture that is {N}% salt by\s+weight")
        return {"x": pa / 100, "y": pb / 100}, pm / 100 * v
    if "swim club" in stem:
        pa = stem_number(stem, rf"advanced swimmers in the club increased by "
                               rf"approximately {N}%")
        pb = stem_number(stem, rf"intermediate\s+swimmers in the club increased by "
                               rf"approximately {N}%")
        pm = stem_number(stem, rf"total number of swimmers in the club increased by "
                               rf"approximately {N}%")
        v = stem_number(stem, rf"a total of {N} swimmers")
        return {"a": 1 + pa / 100, "b": 1 + pb / 100}, v * (1 + pm / 100)
    raise Unreadable("an unfamiliar percentage situation")


# ------------------------------------------------------------- the checks

def keyed(item) -> int:
    return "ABCD".index(item.answer)


def one_hit(item, hits, what: str, detail=""):
    """Both halves: exactly one option is right, and it is the keyed one."""
    if hits.count(True) != 1:
        raise AssertionError(f"{hits.count(True)} of the four options are correct"
                             f"{detail}")
    if not hits[keyed(item)]:
        raise AssertionError(f"the keyed option is not the correct one{detail}")
    return what


def _rows(item):
    out = []
    for c in item.choices:
        try:
            out.append(row(c))
        except Unreadable:
            out.append(None)                       # an option no line can match
    return out


def check_model(item) -> str:
    """The printed equation has to be the situation's own, up to a multiple."""
    want = (situation_model_percent(item.stem) if "%" in item.stem
            else situation_model_standard(item.stem))
    hits = [r is not None and same_line(want, r) for r in _rows(item)]
    return one_hit(item, hits, "models the printed situation")


def check_material(item) -> str:
    """Either of the two remaining rock types may be x, so both readings count."""
    if "Only " not in item.stem:
        return check_material_interpret(item)
    body = re.search(r"Only (.+?) will be used in the garden", item.stem).group(1)
    names = [n.strip() for n in re.split(r",\s*and\s+|,\s*|\s+and\s+", body)
             if n.strip()]
    total = stem_number(item.stem, rf"total weight of {N} pounds")
    known = re.search(rf"If {N} pounds of (\w+) is used", item.stem)
    weighed, w = known.group(2), num(known.group(1))
    density = {}
    for name, d, _cost in [r for r in item.table[1:]]:
        density[name.lower()] = num(d)
    rest = [density[n] for n in names if n != weighed]
    if len(rest) != 2:
        raise Unreadable("the garden does not hold exactly two unweighed rock types")
    left = total - w
    wants = [({"x": rest[0], "y": rest[1]}, left), ({"x": rest[1], "y": rest[0]}, left)]
    hits = [r is not None and any(same_line(w_, r) for w_ in wants) for r in _rows(item)]
    return one_hit(item, hits, "weighs the two remaining rock types")


def check_material_interpret(item) -> str:
    """The fixed amount covers the rock types the printed equation does not price.

    Which two those are is read off the equation: each of its two terms prints a
    cost per pound and a weight per volume, and the table says whose they are.
    """
    eq = re.search(r"The equation (.+?) gives the total cost", item.stem).group(1)
    priced = set()
    for cost, dens in re.findall(rf"{N}\({N}[a-z]\)", eq):
        for name, d, c in item.table[1:]:
            if num(d) == num(dens) and num(c.lstrip("$")) == num(cost):
                priced.add(name.lower())
    if len(priced) != 2:
        raise Unreadable(f"the equation prices {len(priced)} rock types, not two")
    rest = [n.lower() for n, _, _ in item.table[1:] if n.lower() not in priced]
    want = set(rest)
    hits = []
    for c in item.choices:
        named = {n.lower() for n, _, _ in item.table[1:] if n.lower() in c.lower()}
        hits.append(named == want)
    return one_hit(item, hits, "the rock types the equation does not price")


# What a sentence option is *about*, tested in this order: an option that says
# "average number of trees per hectare" is a rate even though it also says
# "number of". The vocabulary is small because the options are.
KINDS = [
    ("diff", re.compile(r"\bdifference\b")),
    ("rate", re.compile(r"\bprice, in dollars, of one\b|\bper hectare\b|"
                        r"\beach side of\b|\bfor each minute\b|"
                        r"\bprice, in dollars, of each\b")),
    ("total", re.compile(r"\btotal\b|\bsum of\b")),
    ("count", re.compile(r"\bnumber of\b")),
    ("one", re.compile(r"\blength, in centimeters, of one\b")),
]

# each interpretation context, and the two things its two variables count, as
# they are named in the options
NOUNS = [
    ("charges for x drinks and y salads", "drink", "salad"),
    ("number of sides of figure A", "figure a", "figure b"),
    ("hectare industrial park", "industrial park", "neighborhood"),
    ("small containers and y large containers", "small container",
     "large container"),
    ("Maria spends running", "running", "biking"),
    ("binders that cost x dollars", "binders", "notebooks"),
    ("In triangle QRS", "qr", "sq"),
]


def kind(text: str) -> str:
    low = text.lower()
    for name, pat in KINDS:
        if pat.search(low):
            return name
    raise Unreadable(text)


def nouns(stem: str) -> tuple[str, str]:
    for marker, xn, yn in NOUNS:
        if marker in stem:
            return xn, yn
    raise Unreadable("an unfamiliar interpretation context")


def queried(stem: str) -> str:
    """The number, term or letter the question asks about."""
    for pat in (r"best interpretation (?:of|for) (?:the number )?(\S+?) in this context",
                r"what does the number (\S+?) represent"):
        m = re.search(pat, stem)
        if m:
            return m.group(1)
    raise Unreadable("the question does not say what it is asking about")


def mentions(text: str, noun: str) -> bool:
    low = text.lower()
    return noun in low or (noun.endswith("s") and noun[:-1] in low) or \
        (not noun.endswith("s") and noun + "s" in low)


def printed_equation(stem: str) -> str:
    """The equation the stem shows, whether displayed on its own line or run
    into a sentence as `The equation ... represents this situation`."""
    for pat in (r"The equation (.+?) represents this situation",
                r"The equation (.+?) models",
                r"equation (.+?) gives the total cost"):
        m = re.search(pat, stem)
        if m:
            return m.group(1).strip()
    head = stem.split("\n")[0]
    if "=" in head and len(head.split()) <= 8:
        return head.strip()
    raise Unreadable("no equation printed in the stem")


def two_variable_sides(eq: str) -> tuple[dict, Q]:
    """The equation's two-variable side, with a lone named total dropped.

    `F = 2.50x + 7.00y` prices drinks and salads exactly as `2.50x + 7.00y = F`
    would; what matters is which coefficient sits against which variable.
    """
    lhs, rhs = eq.split("=")
    if re.fullmatch(r"\s*[A-Za-z]\s*", lhs):
        return side(rhs)
    if re.fullmatch(r"\s*[A-Za-z]\s*", rhs):
        return side(lhs)
    return row(eq)


def check_meaning(item) -> str:
    """Exactly one sentence names the quantity the printed equation attaches to
    the number asked about -- and the other three name something else."""
    coef, const = two_variable_sides(printed_equation(item.stem))
    token = queried(item.stem)
    xn, yn = nouns(item.stem)
    kinds = [kind(c) for c in item.choices]

    if token in ("x", "y"):                       # the variable itself is a rate
        want_kind, want_noun = "rate", (xn if token == "x" else yn)
    elif re.fullmatch(rf"{N}[a-z]", token):       # a whole term: an amount
        var = token[-1]
        want_kind, want_noun = "total", (xn if var == "x" else yn)
    else:
        value = num(token)
        owners = [v for v, c in coef.items() if c == value]
        if len(owners) == 1:                      # a coefficient: a rate
            want_kind = "rate"
            want_noun = xn if owners[0] in ("x", "a", "g") else yn
        elif value == const:                      # the constant: a total of both
            hits = [k == "total" and (mentions(c, xn) and mentions(c, yn)
                                      or "three sides" in c.lower())
                    for k, c in zip(kinds, item.choices)]
            return one_hit(item, hits, "the total of both quantities")
        else:
            raise Unreadable(f"{token!r} is neither a coefficient nor the constant")
    hits = [k == want_kind and mentions(c, want_noun)
            for k, c in zip(kinds, item.choices)]
    return one_hit(item, hits, f"the {want_kind} for the right quantity")


def check_coefficient(item) -> str:
    """`which represents the price of each smaller container` is the coefficient."""
    if "which of the following represents the price" not in item.stem.lower():
        return check_meaning(item)
    eq = re.search(r"The equation (.+?) represents this situation", item.stem).group(1)
    coef, _ = row(eq)
    want = coef["x"]
    hits = []
    for c in item.choices:
        try:
            hits.append(num(c) == want)
        except Exception:
            hits.append(False)
    return one_hit(item, hits, "the coefficient of x, alone")


def check_point_meaning(item) -> str:
    """The sentence has to name the printed pair, in the printed order."""
    m = re.search(rf"\({N}, {N}\) in this context", item.stem)
    x, y = num(m.group(1)), num(m.group(2))
    hits = []
    for c in item.choices:
        if "less than the perimeter" in c:
            hits.append(False)
            continue
        got = re.findall(rf"{N}", c)
        if "length is" in c:                       # `The length is 8 m, and ...`
            hits.append(len(got) >= 2 and (num(got[0]), num(got[1])) == (x, y))
        else:                                      # `If 24 triangles ..., then ...`
            first, second = c.split(", then ")
            same = (num(re.search(rf"{N}", first).group(1)) == x and
                    num(re.search(rf"{N}", second).group(1)) == y)
            hits.append(same and "straws" not in second)
    return one_hit(item, hits, "names the printed pair in order")


def _given_line(stem: str) -> tuple[Q, Q]:
    m = re.search(r"defined by (?:the equation )?(.+?)\. Line", stem)
    if m is None:
        raise Unreadable(stem)
    return as_line(row(m.group(1)))


def check_par_perp(item) -> str:
    """The option must be the slope, or the equation, the relation demands."""
    if "with equation x =" in item.stem or "with equation y =" in item.stem:
        vertical = "equation x =" in item.stem
        perpendicular = "perpendicular" in item.stem
        flat = vertical == perpendicular
        hits = []
        for c in item.choices:
            if "undefined" in c:
                hits.append(not flat)
                continue
            try:
                hits.append(flat and num(c) == 0)
            except Exception:
                hits.append(False)
        return one_hit(item, hits, "the slope of a line across an axis")
    m, _ = _given_line(item.stem)
    want = m if "parallel" in item.stem else -1 / m
    if "Which of the following is an equation" in item.stem:
        b = stem_number(item.stem, rf"y-intercept of line \w+ is \(0, {N}\)")
        hits = []
        for r in _rows(item):
            if r is None:
                hits.append(False)
                continue
            try:
                s_, i_ = as_line(r)
            except Unreadable:
                hits.append(False)
                continue
            hits.append(s_ == want and i_ == b)
        return one_hit(item, hits, "the line with that slope through that point")
    hits = []
    for c in item.choices:
        try:
            hits.append(num(c) == want)
        except Exception:
            hits.append(False)
    return one_hit(item, hits, "the slope the relation demands")


def check_slope_two_points(item) -> str:
    """The slope through the two printed intercepts."""
    m = re.search(rf"x-intercept of \({N}, 0\) and a y-intercept of \(0, ([^)]+)\)",
                  item.stem)
    if m is None:
        raise Unreadable(item.stem)
    x1, y2 = num(m.group(1)), num(m.group(2))
    want = (y2 - 0) / (0 - x1)
    hits = []
    for c in item.choices:
        try:
            hits.append(num(c) == want)
        except Exception:
            hits.append(False)
    return one_hit(item, hits, "the slope through the two intercepts")


def check_intercepts(item) -> str:
    """b/a off the printed equation, or the y-intercept off the drawn line."""
    if item.figure:
        m, b = line_from_grid(item.figure)
        hits = []
        for c in item.choices:
            try:
                px, py = point(c)
            except Unreadable:
                hits.append(False)
                continue
            hits.append(px == 0 and py == b)
        return one_hit(item, hits, "the y-intercept of the drawn line")
    eq = re.search(r"The graph of (.+?) in the xy-plane has an x-intercept",
                   item.stem).group(1)
    coef, const = row(eq)
    a, b = const / coef["x"], const / coef["y"]
    hits = []
    for c in item.choices:
        try:
            hits.append(num(c) == b / a)
        except Exception:
            hits.append(False)
    return one_hit(item, hits, "the ratio of the two intercepts")


def check_line_equation(item) -> str:
    """The line the printed slope and point, or the two printed points, fix."""
    V = r"([^,()]+)"
    m = re.search(rf"slope of (\S+) and passes through the point \({V},{V}\)",
                  item.stem)
    if m:
        want = (num(m.group(1)), num(m.group(3)))
        if num(m.group(2)) != 0:
            raise Unreadable("the printed point is not on the y-axis")
    else:
        m = re.search(rf"passes through the points \({V},{V}\) and \({V},{V}\)",
                      item.stem)
        if m is None:
            raise Unreadable(item.stem)
        x1, y1, x2, y2 = (num(g) for g in m.groups())
        if x1 == x2:
            raise Unreadable("two points on a vertical line")
        slope = (y2 - y1) / (x2 - x1)
        want = (slope, y1 - slope * x1)
    hits = []
    for r in _rows(item):
        try:
            hits.append(r is not None and as_line(r) == want)
        except Unreadable:
            hits.append(False)
    return one_hit(item, hits, "the line the stem fixes")


def check_graph_line(item) -> str:
    """Every option is measured against the drawn line, not against the others."""
    m, b = line_from_grid(item.figure)
    shift = re.search(rf"graph of y = \w\(x\) \+ {N} is shown", item.stem)
    if shift:
        k = num(shift.group(1))
        hits = []
        for c in item.choices:
            try:
                f = as_line(row(c.split("=", 1)[1] + "= y"))
            except Unreadable:
                hits.append(False)
                continue
            hits.append(f[0] == m and f[1] + k == b)
        return one_hit(item, hits, "the function the drawn line was shifted from")
    if "R is a positive constant" in item.stem:
        if m == 0 or b == 0:
            raise Unreadable("the drawn line misses one of the axes")
        xi, yi = -b / m, b
        hits = []
        for c in item.choices:
            try:
                (v1, c1), (v2, c2), const = lettered(c)
            except Unreadable:
                hits.append(False)
                continue
            by = dict([(v1, c1), (v2, c2)])
            if set(by) != {"x", "y"} or sorted(map(str, by.values())).count("R") != 1:
                hits.append(False)
                continue
            # whichever coefficient is a number fixes one intercept outright;
            # the letter has to come out positive to give the other
            if by["x"] == "R":
                fixed_ok = by["y"] != 0 and const / by["y"] == yi
                letter = const / xi
            else:
                fixed_ok = by["x"] != 0 and const / by["x"] == xi
                letter = const / yi
            hits.append(fixed_ok and letter > 0)
        return one_hit(item, hits, "the drawn line for some positive R")
    hits = []
    for r in _rows(item):
        try:
            hits.append(r is not None and as_line(r) == (m, b))
        except Unreadable:
            hits.append(False)
    return one_hit(item, hits, "the drawn line")


def check_combinations(item) -> str:
    """Every option is measured against the two intercepts the chart draws."""
    xi, yi = intercepts_from_chart(item.figure)   # what the money buys of each alone
    if xi == 0 or yi == 0:
        raise Unreadable("the drawn line passes through the origin")
    if "Which equation could represent" in item.stem:
        hits = []
        for r in _rows(item):
            try:
                s_, i_ = as_line(r)
            except Unreadable:
                hits.append(False)
                continue
            hits.append(i_ == yi and s_ != 0 and -i_ / s_ == xi)
        return one_hit(item, hits, "the line the chart draws")
    if "What is the value of s ?" in item.stem:
        rate = stem_number(item.stem, rf"earns \${N} per hour working at job A")
        want = rate * xi
    else:
        total = stem_number(item.stem, rf"purchased for \${N} at a certain store")
        bought = stem_number(item.stem, rf"and {N} pounds of tangerines")
        pa, pb = total / xi, total / yi
        want = (total - pa * bought) / pb
    hits = []
    for c in item.choices:
        try:
            hits.append(num(c) == want)
        except Exception:
            hits.append(False)
    return one_hit(item, hits, "what the chart's two intercepts give")


def check_table_equation(item) -> str:
    """The option must hold at every row the table prints."""
    head, *rows_ = item.table
    xs = [num(a) for a, _ in rows_]
    ys = [num(b) for _, b in rows_]
    hits = []
    for r in _rows(item):
        if r is None:
            hits.append(False)
            continue
        coef, const = r
        names = sorted(coef)
        if len(names) != 2:
            hits.append(False)
            continue
        xv, yv = ("x", "y") if set(names) == {"x", "y"} else (names[1], names[0])
        hits.append(all(satisfies(r, {xv: x, yv: y}) for x, y in zip(xs, ys)))
    return one_hit(item, hits, "holds at every printed row")


def check_which_table(item) -> str:
    """Every pair the option prints must satisfy the equation in the stem."""
    eq = row(item.stem.split("\n")[0])
    names = sorted(eq[0])
    xv, yv = ("x", "y") if set(names) == {"x", "y"} else (names[0], names[1])
    hits = [all(satisfies(eq, {xv: x, yv: y}) for x, y in pairs(c))
            for c in item.choices]
    return one_hit(item, hits, "three pairs on the printed line")


def check_table_symbolic(item) -> str:
    """The slope of the printed table, whatever the constant in it happens to be."""
    head, *rows_ = item.table
    hits = [True] * 4
    for n in (Q(0), Q(5), Q(-7), Q(3, 2)):
        xs, ys = [], []
        for a, b in rows_:
            xs.append(num(a))
            ys.append(affine(b, "n")[0] * n + affine(b, "n")[1])
        want = (ys[1] - ys[0]) / (xs[1] - xs[0])
        for i, c in enumerate(item.choices):
            try:
                if "n" in c:
                    m = re.fullmatch(r"\((.+)\)/\((.+)\)|\((.+)\)/(.+)", c.strip())
                    if m is None:
                        hits[i] = False
                        continue
                    g = [x for x in m.groups() if x is not None]
                    top, bot = affine(g[0], "n"), affine(g[1], "n")
                    denom = bot[0] * n + bot[1]
                    value = None if denom == 0 else (top[0] * n + top[1]) / denom
                else:
                    value = num(c)
            except Exception:
                value = None
            if value != want:
                hits[i] = False
    return one_hit(item, hits, "the slope of the printed table")


def check_table_line(item) -> str:
    """The value the printed table's line takes somewhere else, or -- after the
    printed translation -- where it reaches zero."""
    head, *rows_ = item.table
    xs = [num(a) for a, _ in rows_]
    ys = [num(b) for _, b in rows_]
    m = (ys[1] - ys[0]) / (xs[1] - xs[0])
    b = ys[0] - m * xs[0]
    if "passes through the point" in item.stem:
        at = num(re.search(r"passes through the point \(([^,]+),", item.stem).group(1))
        want = m * at + b
        hits = []
        for c in item.choices:
            try:
                hits.append(num(c) == want)
            except Exception:
                hits.append(False)
        return one_hit(item, hits, "the value the table's line takes there")
    k = stem_number(item.stem, rf"translating\s+line h down {N} units")
    want = (-(b - k) / m, Q(0))
    hits = []
    for c in item.choices:
        try:
            hits.append(point(c) == want)
        except Unreadable:
            hits.append(False)
    return one_hit(item, hits, "the translated line's x-intercept")


def check_equivalent(item) -> str:
    """The parameterized point has to lie on both printed equations, for every r."""
    lines = item.stem.split("\n")
    rows_ = [row(lines[0]), row(lines[1])]
    var = re.search(r"For each real number (\w)", item.stem).group(1)
    hits = []
    for c in item.choices:
        try:
            (mx, cx), (my, cy) = parametric(c, var)
        except Unreadable:
            hits.append(False)
            continue
        hits.append(all(satisfies(r, {"x": mx * t + cx, "y": my * t + cy})
                        for r in rows_ for t in (Q(0), Q(1), Q(-3), Q(7, 2))))
    return one_hit(item, hits, "lies on both lines for every r")


CHECKS = {
    "le2.model_standard": check_model,
    "le2.model_percent": check_model,
    "le2.material_table": check_material,
    "le2.interpret_coefficient": check_coefficient,
    "le2.interpret_constant": check_meaning,
    "le2.interpret_point": check_point_meaning,
    "le2.parallel_perpendicular": check_par_perp,
    "le2.slope_two_points": check_slope_two_points,
    "le2.intercepts": check_intercepts,
    "le2.line_equation": check_line_equation,
    "le2.line_from_graph": check_graph_line,
    "le2.graph_combinations": check_combinations,
    "le2.table_equation": check_table_equation,
    "le2.which_table": check_which_table,
    "le2.table_symbolic": check_table_symbolic,
    "le2.table_line": check_table_line,
    "le2.equivalent_system": check_equivalent,
}

# the asks inside those templates that answer with a bare number: `audit` already
# re-derives the key, and four distinct numbers cannot hold two right answers
SKIP = ("[grid-in]",)


# ------------------------------------------------- proving it can fail

def _broken(item, **changes):
    """A copy of a finished item with something wrong done to it."""
    import copy
    bad = copy.deepcopy(item)
    for k, v in changes.items():
        setattr(bad, k, v)
    return bad


def selftest() -> int:
    """A check nobody has seen fail is worth nothing.

    Three faults, one of each kind the assertions are for: a second correct
    answer, the same line printed twice, and the right answer under the wrong
    letter.
    """
    cases = []

    # 1. a second correct answer: the equation is symmetric in x and y, so the
    #    option that swaps the columns satisfies it too
    item = generate("le2.which_table", 0)
    cases.append(("a second correct answer", _broken(
        item, stem="2x + 2y = -68\n" + item.stem.split("\n", 1)[1],
        choices=["(2, -36), (4, -38), (6, -40)", "(-36, 2), (-38, 4), (-40, 6)",
                 "(2, -74), (6, -40), (10, -6)", "(2, -148), (6, -444), (10, -740)"],
        answer="A"), check_which_table))

    # 2. the same line written twice: a distractor that is the key doubled
    item = generate("le2.model_standard", 0)
    keyed = item.choices[keyed_index := "ABCD".index(item.answer)]
    coef, const = row(keyed)
    doubled = " + ".join(f"{2 * c}{v}" for v, c in sorted(coef.items())) + \
              f" = {2 * const}"
    swapped = list(item.choices)
    swapped[(keyed_index + 1) % 4] = doubled
    cases.append(("the same line written twice",
                  _broken(item, choices=swapped), check_model))

    # 3. the right answer under the wrong letter
    item = generate("le2.line_equation", 0)
    other = "ABCD"[("ABCD".index(item.answer) + 2) % 4]
    cases.append(("the key under the wrong letter",
                  _broken(item, answer=other), check_line_equation))

    worst = 0
    for what, bad, checker in cases:
        try:
            checker(bad)
        except AssertionError as exc:
            print(f"  ok   caught {what}: {exc}")
            continue
        except Unreadable as exc:
            print(f" FAIL  {what} was not read at all: {exc}")
            worst = 1
            continue
        print(f" FAIL  {what} was not caught")
        worst = 1
    return worst


# ------------------------------------------------------------------ driver

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--draws", type=int, default=400,
                    help="seeds to try per template (default 400)")
    ap.add_argument("--template", action="append",
                    help="check only this template; repeatable")
    ap.add_argument("--selftest", action="store_true",
                    help="inject three faulty option sets and check each is caught")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    names = args.template or list(CHECKS)

    worst, total = 0, 0
    for name in names:
        checker = CHECKS[name]
        made, bad, skipped, what = 0, 0, 0, ""
        for seed in range(args.draws):
            try:
                item = generate(name, seed)
            except ItemError:
                continue
            if item.fmt != "mcq":
                continue
            made += 1
            try:
                what = checker(item) or what
            except Unreadable as exc:
                skipped += 1
                if skipped == 1:
                    print(f"\n{name} seed {seed}: unreadable -- {exc}")
                    print(item.pretty())
            except AssertionError as exc:
                bad += 1
                if bad == 1:
                    print(f"\n{name} seed {seed}: {exc}")
                    print(item.pretty())
        total += made
        mark = "  ok  " if not (bad or skipped) else " FAIL "
        tail = f", {skipped} unreadable" if skipped else ""
        print(f"{mark} {name:<28} {made:>5,} items, {bad} defects{tail}   ({what})")
        worst |= 1 if (bad or skipped) else 0
    print(f"\n{total:,} items read back")
    return worst


if __name__ == "__main__":
    sys.exit(main())
