"""A line meeting a curve.

Fourteen of the official items are a quadratic and a linear equation printed
together, and what varies is the surface each one is written on -- y on its own,
a product of two brackets, a square, x² gathered with the y term, a line in
standard form, a line already solved, a bracket that is really a line -- and
what is asked for: one x, the y-coordinate, the product xy, the pair itself,
both pairs, or the sum of the two y-values.

Everything here substitutes the line into the curve and solves the quadratic
that leaves. `audit.py` does it the other way round, by sweeping the printed
coefficients for a common root, so neither route can cover for the other. The
coordinates are kept as exact surds, because the source does print
(1 + √3, √3).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from fractions import Fraction as Q

from ....exact import E
from ....item import Item, ItemError, Mis
from ..kit import (MINUS, ROOT, choices, displayed, eq, gridin, griddable,
                   gridin_pool, join, mono, num, paren, pick, poly, q, sent, sup,
                   text_choices)

__all__ = ["curve_line_system", "sum_product", "secant_slope"]


# ------------------------------------------------------------------ surds

@dataclass(frozen=True)
class Surd:
    """p + g·√m, exactly. m = 1 covers every rational value."""
    p: Q
    g: Q = Q(0)
    m: Q = Q(1)

    @staticmethod
    def of(p, g=0, m=1) -> "Surd":
        p, g, m = q(p), q(g), q(m)
        if g == 0 or m == 0:
            return Surd(p, Q(0), Q(1))
        if m == 1:
            return Surd(p + g, Q(0), Q(1))
        return Surd(p, g, m)

    @property
    def rational(self) -> bool:
        return self.g == 0

    def __add__(self, o) -> "Surd":
        o = o if isinstance(o, Surd) else Surd.of(o)
        if self.g and o.g and self.m != o.m:
            raise ItemError("two unlike radicals cannot be added")
        m = self.m if self.g else o.m
        return Surd.of(self.p + o.p, self.g + o.g, m)

    def __neg__(self) -> "Surd":
        return Surd(-self.p, -self.g, self.m)

    def __sub__(self, o) -> "Surd":
        return self + (-(o if isinstance(o, Surd) else Surd.of(o)))

    def scale(self, k) -> "Surd":
        k = q(k)
        return Surd.of(self.p * k, self.g * k, self.m)

    def __mul__(self, o) -> "Surd":
        o = o if isinstance(o, Surd) else Surd.of(o)
        if o.rational:
            return self.scale(o.p)
        if self.rational:
            return o.scale(self.p)
        if self.m != o.m:
            raise ItemError("two unlike radicals cannot be multiplied here")
        return Surd.of(self.p * o.p + self.g * o.g * self.m,
                       self.p * o.g + self.g * o.p, self.m)

    def __float__(self) -> float:
        return float(self.p) + float(self.g) * math.sqrt(float(self.m))

    def text(self) -> str:
        """`1 + √3`, `−√35`, `(1/3)√46`.

        A fractional coefficient is bracketed: `1/3√46` could be read as
        1/(3√46), and a page that can be read two ways has two answers.
        """
        if self.rational:
            return num(self.p)
        g = abs(self.g)
        head = "" if g == 1 else (num(g) if g.denominator == 1 else f"({num(g)})")
        body = (MINUS if self.g < 0 else "") + head + ROOT + num(self.m)
        return join([num(self.p), body]) if self.p else body


def _sqrt_surd(v) -> Surd | None:
    """√v as p + g√m with p = 0, or None when v is negative."""
    v = q(v)
    if v < 0:
        return None
    n, d = v.numerator, v.denominator
    g, m = 1, n * d
    i = 2
    while i * i <= m:
        while m % (i * i) == 0:
            m //= i * i
            g *= i
        i += 1
    return Surd.of(0, Q(g, d), Q(m))


# --------------------------------------------- a printed equation, reduced

def spec_terms(lhs, rhs=()):
    return ("terms", list(lhs), list(rhs))


def _reduce(spec) -> tuple:
    """A printed equation as (A, B, C, D) with A·x² + B·x + C·y + D = 0."""
    kind = spec[0]
    if kind == "terms":
        out = {"x2": Q(0), "x": Q(0), "y": Q(0), "": Q(0)}
        for c, mon in spec[1]:
            out[mon] += q(c)
        for c, mon in spec[2]:
            out[mon] -= q(c)
        return out["x2"], out["x"], out["y"], out[""]
    if kind == "factored":                       # y = (x − r)(x − s)
        r, s = q(spec[1]), q(spec[2])
        return Q(1), -(r + s), Q(-1), r * s
    if kind == "square":                         # y = (x − h)²
        h = q(spec[1])
        return Q(1), -2 * h, Q(-1), h * h
    if kind == "bracket":                        # p·y + k = c(x + d)
        p, k, c, d = q(spec[1]), q(spec[2]), q(spec[3]), q(spec[4])
        return Q(0), -c, p, k - c * d
    raise ItemError(f"unknown equation shape {kind!r}")


def _print(spec) -> str:
    kind = spec[0]
    if kind == "terms":
        return eq(_side(spec[1]), _side(spec[2]))
    if kind == "factored":
        r, s = q(spec[1]), q(spec[2])
        return eq("y", paren(join(["x", mono(-r, "")]))
                  + paren(join(["x", mono(-s, "")])))
    if kind == "square":
        h = q(spec[1])
        return eq("y", paren(join(["x", mono(-h, "")])) + sup(2))
    p, k, c, d = q(spec[1]), q(spec[2]), q(spec[3]), q(spec[4])
    return eq(join([mono(p, "y"), mono(k, "")]),
              (num(c) if c != 1 else "") + paren(join(["x", mono(d, "")])))


_MON = {"x2": ("x", 2), "x": ("x", 1), "y": ("y", 1), "": ("", 1)}


def _side(terms) -> str:
    if not terms:
        return "0"
    parts = []
    for c, m in terms:
        sym, power = _MON[m]
        parts.append(mono(c, sym, power))
    return join(parts)


# ------------------------------------------------------------- the frames

FRAMES = {
    "possible_x": "If (x, y) is a solution to the system of equations above, which "
                  "of the following is a possible value of x?",
    "could_be_x": "If (x, y) is a solution to the system of equations above, which "
                  "of the following could be the value of x ?",
    "one_possible_x": "If the ordered pair (x, y) satisfies the system of equations "
                      "above, what is one possible value of x ?",
    "one_solution_x": "If one solution to the system of equations above is (x, y), "
                      "what is one possible value of x ?",
    "solution_x": "The solution to the given system of equations is (x, y). What is "
                  "the value of x?",
    "intersect_x": "The graphs of the equations in the given system of equations "
                   "intersect at the point (x, y) in the xy-plane. What is a "
                   "possible value of x?",
    "possible_xy": "A solution to the given system of equations is (x, y). Which of "
                   "the following is a possible value of xy ?",
    "positive_xy": "If (x, y) is a solution of the system of equations above and "
                   "x > 0, what is the value of xy ?",
    "which_pair": "Which ordered pair (x, y) is a solution to the given system of "
                  "equations?",
    "the_pair": "Which ordered pair (x, y) is the solution to the given system of "
                "equations?",
    "which_pair_plain": "Which ordered pair is a solution to the system of equations "
                        "above?",
    "both_pairs": "When the equations above are graphed in the xy-plane, what are the "
                  "coordinates (x, y) of the points of intersection of the two "
                  "graphs?",
    "sum_y": "If (x₁, y₁) and (x₂, y₂) are the two solutions to "
             "the system of equations above, what is the value of "
             "y₁ + y₂ ?",
    "y_coordinate": "In the xy-plane, what is the y-coordinate of the point of "
                    "intersection of the graphs of {e1} and {e2} ?",
    "meets_at": "In the xy-plane, the graph of {e1} intersects the graph of {e2} at "
                "the points (0, 0) and (a, a). What is the value of a ?",
}


# --------------------------------------------------------- the main template

def curve_line_system(rng: random.Random, seed: int, *, curve=None, line=None,
                      ask=None, frame=None, fmt=None, branch=None, offsets=None,
                      wrongs=None, sign_rule=True, difficulty="medium") -> Item:
    """One quadratic and one linear equation, printed as the source prints them."""
    if curve is None:
        curve, line = _draw(rng)
    A1, B1, C1, D1 = _reduce(curve)
    A2, B2, C2, D2 = _reduce(line)
    if A1 == 0 or A2 != 0:
        raise ItemError("this template needs one quadratic and one line")
    if C1 == 0 or C2 == 0:
        raise ItemError("both equations have to carry the y term")

    # y = −(B2·x + D2)/C2, put into the curve
    qa = A1
    qb = B1 - C1 * B2 / C2
    qc = D1 - C1 * D2 / C2
    disc = qb * qb - 4 * qa * qc
    root = _sqrt_surd(disc)
    if root is None:
        raise ItemError("the line misses the curve")
    xs = sorted({Surd.of(-qb / (2 * qa)) + root.scale(1 / (2 * qa)),
                 Surd.of(-qb / (2 * qa)) - root.scale(1 / (2 * qa))},
                key=float)
    ys = [(Surd.of(-D2 / C2) - x.scale(B2 / C2)) for x in xs]
    pts = list(zip(xs, ys))

    ask = ask or rng.choice(["possible_x", "which_pair", "possible_xy", "solution_x"])
    branch = branch or rng.choice(["lo", "hi"])
    frame = frame or ask
    text = FRAMES[frame]
    if "{e1}" in text:
        stem = sent(text.format(e1=_print(curve), e2=_print(line)))
    else:
        stem = displayed(_print(curve), _print(line), sent(text))

    P = {"kind": "nleq_curve_line", "curve": _pack(curve), "line": _pack(line),
         "ask": ask, "branch": branch}
    rationale = _story(curve, line, pts)

    if ask in ("which_pair", "the_pair", "which_pair_plain", "both_pairs"):
        return _pair_item(seed, stem, pts, curve, line, A1, B1, C1, D1, B2, C2, D2,
                          ask, branch, offsets, wrongs, rng, rationale, P, difficulty)
    key, pool, admits = _value_key(ask, pts, xs, ys, A1, B2, C2, D2, branch, line)
    if key is None:
        raise ItemError("this draw does not answer the question asked")
    if not key.rational:
        raise ItemError("the value asked for is not a number the grid can take")
    fmt = fmt or ("mcq" if ask.startswith(("possible", "could", "which")) else "spr")
    keyx = E(key.p)
    if fmt == "spr":
        if not griddable(key.p):
            raise ItemError("that answer could not be entered in the grid")
        # the near_* entries are neighbours offered as options, not mistakes
        named = {n: m for n, m in pool.items() if not n.startswith("near_")}
        # a coefficient read off the page is the one printed, sign and all
        for n, spec, mon in (("line_coef", line, "x"), ("curve_coef", curve, "x2")):
            if n in named:
                named[n] = Mis(named[n].reason, _printed_coef(spec, mon))
        return Item("nleq.curve_line_system", "a line meeting a curve", difficulty,
                    seed, sent(stem), "spr", keyx, gridin(key.p), rationale,
                    params=P, spr_mistakes=gridin_pool(keyx, named.values(), admits))
    ch, tex, why, letter = choices(keyx, pick(pool, wrongs), rng,
                                   sign_rule=sign_rule, guard=wrongs is None,
                                   forbid=admits)
    return Item("nleq.curve_line_system", "a line meeting a curve", difficulty, seed,
                sent(stem), "mcq", keyx, letter, rationale, ch, why, tex,
                params=dict(P, options=list(ch)))


def _printed_coef(spec, mon):
    """The number printed in front of `mon`, or None when no number is: the
    term is missing, printed twice, carries a bare 1 or minus sign, or sits
    inside a bracket."""
    if spec[0] != "terms":
        return None
    cs = [q(c) for c, m in spec[1] + spec[2] if m == mon]
    return cs[0] if len(cs) == 1 and abs(cs[0]) != 1 else None


def _value_key(ask, pts, xs, ys, A1, B2, C2, D2, branch, line):
    """The keyed value and the pool of wrong ones, with every *right* value
    struck out of the pool first.

    "Which of the following is a possible value of x?" is answered by either
    root, so the other root is a second key, not a distractor -- and so is any
    near-miss that lands on it. The same goes for xy when the stem does not
    single out one of the two points. The set of values that genuinely answer
    the question is worked out here and removed from the pool wholesale, rather
    than one pool entry at a time.
    """
    key, pool, correct = _value_pool(ask, pts, xs, ys, A1, B2, C2, D2, branch,
                                     line)
    if key is None:
        return None, {}, ()
    return key, _drop_correct(pool, correct, key), correct


def _drop_correct(pool: dict, correct, key) -> dict:
    live = {float(v) for v in correct if float(v) != float(key.p)}
    out = {}
    for name, m in pool.items():
        if m.value is not None and any(abs(float(m.value) - c) < 1e-12
                                       for c in live):
            out[name] = Mis(m.reason, None)
        else:
            out[name] = m
    return out


def _value_pool(ask, pts, xs, ys, A1, B2, C2, D2, branch, line):
    lo, hi = xs[0], xs[-1]
    ylo, yhi = ys[0], ys[-1]
    one = len(set(xs)) == 1
    # a repeated root leaves one point, so "the other branch" is that same point
    first = min(1, len(xs) - 1) if branch == "hi" else 0

    def rat(s):
        return s if s.rational else None

    if ask in ("possible_x", "could_be_x", "one_possible_x", "one_solution_x",
               "intersect_x"):
        key = rat(xs[first]) or rat(xs[-1 - first])
        other = hi if key == lo else lo
        yk = ys[first] if key == xs[first] else ys[-1 - first]
        pool = {
            "other": Mis("reported the other point's x-coordinate", _v(other)),
            "y_instead": Mis("reported the y-coordinate of that point instead",
                             _v(yk)),
            "y_other": Mis("reported the other point's y-coordinate instead",
                           _v(yhi if key == lo else ylo)),
            "sum": Mis("added the two solutions instead of choosing one",
                       _v(lo + hi)),
            "product": Mis("multiplied the two solutions instead of choosing one",
                           _v(lo * hi)),
            "sign": Mis("lost the sign when dividing", _neg(key)),
            "const": Mis("read the constant from the line as the answer",
                         -D2 / C2),
            "line_coef": Mis("read the coefficient of x in the line as the answer",
                             B2 if B2 else None),
            "curve_coef": Mis("read the coefficient of x² in the curve as the "
                              "answer", A1),
        }
        if key is None:
            return None, {}, ()
        pool.update(_near(key))
        return key, pool, [x.p for x in xs if x.rational]
    if ask == "solution_x":
        if not one or not lo.rational:
            return None, {}, ()
        return lo, {"negate": Mis("solved for the wrong sign of x", _neg(lo)),
                    "half": Mis("halved the solution as well as dividing by the "
                                "leading coefficient", _v(lo.scale(Q(1, 2)))),
                    "y_instead": Mis("reported the y-coordinate instead",
                                     _v(ylo))}, [lo.p]
    if ask == "y_coordinate":
        key = rat(ylo) if one or ylo == yhi else None
        return key, {}, ([key.p] if key is not None else ())
    if ask in ("possible_xy", "positive_xy"):
        prods = [x * y for x, y in pts]
        if ask == "positive_xy":
            live = [i for i, (x, _) in enumerate(pts) if float(x) > 0]
            if len(live) != 1:
                return None, {}, ()
            i = live[0]
            # the stem singles out the point with positive x, so the other
            # point's product is a legitimate wrong answer
            correct = [prods[i].p] if prods[i].rational else []
        else:
            i = min(first, len(prods) - 1)
            correct = [v.p for v in prods if v.rational]
        key = rat(prods[i])
        if key is None:
            return None, {}, ()
        x, y = pts[i]
        other = (i + 1) % len(pts)
        pool = {
            "other": Mis("multiplied the other point's coordinates instead",
                         _v(prods[other])),
            "x_only": Mis("reported x rather than the product asked for", _v(x)),
            "y_only": Mis("reported y rather than the product asked for", _v(y)),
            "x_other": Mis("reported the other point's x rather than the product",
                           _v(pts[other][0])),
            "double_x": Mis("doubled x instead of multiplying it by y",
                            _v(x.scale(2))),
            "sum": Mis("added the two coordinates instead of multiplying them",
                       _v(x + y)),
            "square": Mis("squared one coordinate instead of multiplying the two",
                          _v(x * x)),
        }
        pool.update(_line_numbers(line))
        return key, pool, correct
    if ask == "sum_y":
        if len(set(xs)) != 2:
            # the stem names (x\u2081, y\u2081) and (x\u2082, y\u2082) as two
            # solutions; a repeated root leaves one, and their sum is then two
            # answers depending on whether it is counted once or twice
            return None, {}, ()
        key = ylo + yhi
        pool = {
            "sum_x": Mis("added the two x-coordinates instead of the two "
                         "y-coordinates", _v(lo + hi)),
            "one_only": Mis("reported one of the two y-values rather than their "
                            "sum", _v(ylo)),
            "x_one": Mis("reported one of the two x-values instead", _v(lo)),
            "x_other": Mis("reported the other x-value instead", _v(hi)),
            "other_only": Mis("reported the other y-value rather than the sum",
                              _v(yhi)),
            "negate": Mis("lost the sign of the sum", _neg(key)),
            "product": Mis("multiplied the two y-values instead of adding them",
                           _v(ylo * yhi)),
        }
        return key, pool, ([key.p] if key.rational else ())
    if ask == "meets_at":
        live = [x for x in xs if float(x) != 0]
        if len(live) != 1 or not live[0].rational:
            return None, {}, ()
        return live[0], {}, [live[0].p]
    return None, {}, ()


def _near(key) -> dict:
    if key is None:
        return {}
    """The nearby whole numbers a "which of these works" item offers.

    The source's option set for those items is usually a short run of
    consecutive integers around the solution: the question is whether a student
    can test a candidate, and the wrong candidates are simply the neighbours.
    """
    out = {}
    if not key.rational or key.p.denominator != 1:
        return out
    for n in range(1, 6):
        out[f"near_up_{n}"] = Mis("a nearby whole number that satisfies neither "
                                  "equation", key.p + n)
        out[f"near_down_{n}"] = Mis("a nearby whole number that satisfies neither "
                                    "equation", key.p - n)
    return out


def _line_numbers(line) -> dict:
    """The numbers a bracketed line prints, offered as answers in their own right."""
    if line[0] != "bracket":
        return {}
    c, d = q(line[3]), q(line[4])
    return {
        "line_coef": Mis("read the number in front of the bracket as the answer", c),
        "line_const": Mis("read the number inside the bracket as the answer", d),
        "line_const_square": Mis("squared the number inside the bracket", d * d),
    }


def _v(s):
    return s.p if isinstance(s, Surd) and s.rational else None


def _neg(s):
    return -s.p if isinstance(s, Surd) and s.rational else None


def _pair_item(seed, stem, pts, curve, line, A1, B1, C1, D1, B2, C2, D2, ask,
               branch, offsets, wrongs, rng, rationale, P, difficulty) -> Item:
    """An item whose options are points, with every option that is *also* a
    solution refused before it is printed.

    "Which ordered pair is a solution to the given system?" has as many correct
    answers as the system has solutions, and a line meets a curve twice. So the
    other intersection is not a distractor -- it is a second key -- and neither
    is any near-miss that happens to land on it: the origin when the origin is
    the other crossing, a point one gridline along when that is where the second
    crossing sits. Rather than special-case those one at a time, every candidate
    point is substituted into both printed equations here and dropped if it
    satisfies both. `pt` is the single place a point becomes text, so nothing
    can get onto the page without passing through the test.
    """
    def solves(x, y) -> bool:
        try:
            curve_val = ((x * x).scale(A1) + x.scale(B1) + y.scale(C1)
                         + Surd.of(D1))
            line_val = x.scale(B2) + y.scale(C2) + Surd.of(D2)
        except ItemError:
            return False
        return _is_zero(curve_val) and _is_zero(line_val)

    def pt(x, y, key=False):
        if x is None or y is None:
            return None
        if not key and solves(x, y):
            return None
        return f"({x.text()}, {y.text()})"

    def on_line(x):
        return Surd.of(-D2 / C2) - x.scale(B2 / C2)

    def on_curve(x):
        if C1 == 0:
            return None
        return (x * x).scale(-A1 / C1) - x.scale(B1 / C1) - Surd.of(D1 / C1)

    lo, hi = pts[0], pts[-1]
    offsets = offsets or [2, 3, 4]
    if ask == "both_pairs":
        if lo == hi:
            raise ItemError("the two points coincide, so there is only one")
        order = [hi, lo]                     # the source prints the larger x first
        key = " and ".join(pt(*p, key=True) for p in order)
        true_set = {(float(x), float(y)) for x, y in order}
        k = -D2 / C2                         # a horizontal line's own height
        pool = {
            "no_constant": Mis("read the y-values off x² alone, leaving the curve's "
                               "constant term out",
                               _two(pt, [(x, x * x) for x, _ in order], true_set)),
            "y_as_x": Mis("used the line's own value as x and then read the curve",
                          _two(pt, [(Surd.of(k), on_curve(Surd.of(k))),
                                    (Surd.of(-k), on_curve(Surd.of(-k)))],
                               true_set) if C1 and k else None),
            "sign_const": Mis("moved the curve's constant across without changing "
                              "its sign",
                              _mirror(pt, A1, C1, D1, k, true_set, flip=True)),
            "swapped": Mis("wrote each pair's coordinates the wrong way round",
                           _two(pt, [(y, x) for x, y in order], true_set)),
        }
    else:
        if lo != hi and ask == "the_pair":
            raise ItemError("the stem promises a single solution")
        target = hi if branch == "hi" else lo
        other = lo if target is hi else hi
        key = pt(*target, key=True)
        roots = _curve_roots(curve)
        pool = {
            "other": Mis("named the other point the two graphs share", pt(*other)
                         if other != target else None),
            "swapped": Mis("wrote the two coordinates the wrong way round",
                           pt(target[1], target[0])),
            "y_sign": Mis("lost the sign of the y-coordinate",
                          pt(target[0], -target[1])),
            "x_sign": Mis("lost the sign of the x-coordinate",
                          pt(-target[0], target[1])),
            "origin": Mis("named the origin rather than the point the two graphs "
                          "share", pt(Surd.of(0), Surd.of(0))
                          if float(target[0]) or float(target[1]) else None),
            "intercept": Mis("named where the line crosses the y-axis rather than "
                             "where it meets the curve",
                             pt(Surd.of(0), Surd.of(-D2 / C2))
                             if float(target[0]) else None),
            "curve_only_radical": Mis("dropped the whole-number part of the "
                                      "x-coordinate and read the y-value off the "
                                      "curve",
                                      _radical_only(pt, target[0], on_curve)),
            "roots_as_pair": Mis("read the two numbers the brackets give as the "
                                 "coordinates",
                                 pt(Surd.of(roots[0]), Surd.of(roots[1]))
                                 if roots else None),
            "roots_swapped": Mis("read the two numbers the brackets give and wrote "
                                 "them the wrong way round",
                                 pt(Surd.of(roots[1]), Surd.of(roots[0]))
                                 if roots else None),
            "zero_and_root": Mis("paired zero with one of the numbers the brackets "
                                 "give", pt(Surd.of(0), Surd.of(roots[0]))
                                 if roots else None),
        }
        flip = _flipped_branch(curve, B2, C2, -D2, branch)
        if flip is not None:
            fy = on_line(flip)
            pool["line_sign"] = Mis("used the wrong sign for the line's constant "
                                    "when substituting, then read y off the line",
                                    pt(flip, fy))
            if not flip.rational and flip.p:
                rad = Surd.of(0, flip.g, flip.m)
                pool["line_sign_radical"] = Mis(
                    "used the wrong sign for the line's constant and then dropped "
                    "the whole-number part of x", pt(rad, on_line(rad)))
        for i, t in enumerate(offsets, start=1):
            xx = target[0] + Surd.of(t)
            pool[f"line_only_{i}"] = Mis("named a point on the line that is not on "
                                         "the curve", pt(xx, on_line(xx)))
            cc = on_curve(xx)
            pool[f"curve_only_{i}"] = Mis("named a point on the curve that is not "
                                          "on the line",
                                          pt(xx, cc) if cc is not None else None)
    ch, why, letter = text_choices(key, pick(pool, wrongs), rng, check=False)
    return Item("nleq.curve_line_system", "a line meeting a curve", difficulty, seed,
                sent(stem), "mcq", E(1), letter, rationale, ch, why, list(ch),
                params=dict(P, options=list(ch)))


def _is_zero(s: Surd) -> bool:
    return s.p == 0 and s.g == 0


def _two(pt, pairs, true_set) -> str | None:
    """Two printed points, refused when they are the pair the stem asks for."""
    if any(p is None or p[0] is None or p[1] is None for p in pairs):
        return None
    if {(float(x), float(y)) for x, y in pairs} == true_set:
        return None
    out = [pt(*p, key=True) for p in pairs]
    return " and ".join(out) if out[0] != out[1] else None


def _mirror(pt, A1, C1, D1, k, true_set, flip=False) -> str | None:
    """The two points a horizontal line gives when the constant keeps its sign."""
    if A1 == 0 or C1 == 0:
        return None
    v = (-C1 * k + (D1 if flip else -D1)) / A1
    r = _sqrt_surd(v)
    if r is None or float(r) == 0:
        return None
    return _two(pt, [(x, Surd.of(k)) for x in (r, -r)], true_set)


def _radical_only(pt, x, on_curve) -> str | None:
    if x.rational or x.p == 0:
        return None
    r = Surd.of(0, x.g, x.m)
    y = on_curve(r)
    return pt(r, y) if y is not None else None


def _flipped_branch(curve, B2, C2, D2, branch):
    """The x this system gives when the line's constant is substituted with the
    wrong sign -- the root of the option set 3.2 is built around."""
    A1, B1, C1, D1 = _reduce(curve)
    if A1 == 0 or C2 == 0:
        return None
    qb = B1 - C1 * B2 / C2
    qc = D1 - C1 * D2 / C2
    r = _sqrt_surd(qb * qb - 4 * A1 * qc)
    if r is None:
        return None
    xs = sorted({Surd.of(-qb / (2 * A1)) + r.scale(1 / (2 * A1)),
                 Surd.of(-qb / (2 * A1)) - r.scale(1 / (2 * A1))}, key=float)
    return xs[-1] if branch == "hi" else xs[0]


def _curve_roots(curve):
    if curve[0] == "factored":
        return [q(curve[1]), q(curve[2])]
    return None


def _root_pair(pts) -> str | None:
    out = []
    for x, y in pts:
        if not y.rational or y.p < 0:
            return None
        r = _sqrt_surd(y.p)
        if r is None or not r.rational:
            return None
        out.append(f"({r.text()}, {y.text()})")
    return " and ".join(out) if len(out) == 2 and out[0] != out[1] else None


def _listed(parts) -> str:
    parts = list(parts)
    if len(parts) < 2:
        return "".join(parts)
    return ", ".join(parts[:-1]) + f" and {parts[-1]}"


def _story(curve, line, pts) -> str:
    xs = _listed([x.text() for x, _ in pts])
    ys = _listed([y.text() for _, y in pts])
    if len(pts) == 2 and pts[0] != pts[1]:
        return sent(f"Putting the line into {_print(curve)} leaves a quadratic in x "
                    f"whose solutions are {xs}, and the line then gives y = {ys}.")
    return sent(f"Putting the line into {_print(curve)} leaves a quadratic in x with "
                f"the single solution x = {pts[0][0].text()}, and the line then "
                f"gives y = {pts[0][1].text()}.")


def _draw(rng: random.Random):
    """A random curve and line that cross at points the page can print."""
    shape = rng.choice(["plain", "factored", "square", "gathered"])
    m = Q(rng.choice([i for i in range(-8, 9) if i]))
    r1 = Q(rng.randint(-8, 8))
    r2 = Q(rng.randint(-8, 8))
    b = Q(rng.randint(-12, 12))
    if shape == "factored":
        curve = ("factored", r1, r2)
    elif shape == "square":
        curve = ("square", r1)
    elif shape == "gathered":
        a = Q(rng.choice([1, 2, 3]))
        curve = spec_terms([(a, "x2")], [(rng.randint(-6, 6), "x"), (1, "y"),
                                         (rng.randint(-20, 20), "")])
    else:
        curve = spec_terms([(1, "y")], [(Q(rng.choice([1, 1, 2, 3, 5])), "x2"),
                                        (r1, "x"), (r2, "")])
    if rng.random() < 0.5:
        line = spec_terms([(1, "y")], [(m, "x"), (b, "")])
    else:
        line = spec_terms([(m, "x"), (1, "y")], [(b, "")])
    return curve, line


# --------------------------------------------- the sum and the product given

def sum_product(rng: random.Random, seed: int, *, total=None, product=None,
                ask="one_solution_x", fmt="spr", wrongs=None,
                difficulty="medium") -> Item:
    """x + y = S and xy = P -- the two unknowns are the roots of one quadratic."""
    total = Q(rng.randint(5, 30)) if total is None else q(total)
    product = Q(rng.randint(4, 200)) if product is None else q(product)
    disc = total * total - 4 * product
    if disc <= 0:
        raise ItemError("no real pair has that sum and that product")
    r = _sqrt_surd(disc)
    if r is None or not r.rational:
        raise ItemError("the pair would not print cleanly")
    lo = (total - r.p) / 2
    hi = (total + r.p) / 2
    stem = displayed(eq(join(["x", "y"]), num(total)), eq("xy", num(product)),
                     sent(FRAMES[ask]))
    key = hi
    pool = {
        "other": Mis("reported the other unknown", lo),
        "half_total": Mis("split the total evenly between the two unknowns",
                          total / 2),
        "difference": Mis("subtracted the two unknowns instead of choosing one",
                          hi - lo),
        "product_half": Mis("halved the product instead of solving the quadratic",
                            product / 2),
        "total_itself": Mis("reported the total rather than one of the two numbers",
                            total),
    }
    P = {"kind": "nleq_sum_product", "total": _p(total), "product": _p(product),
         "ask": ask}
    rationale = sent(f"The two numbers are the solutions of "
                     f"{poly((product, -total, 1))} = 0, which are {num(lo)} and "
                     f"{num(hi)}.")
    keyx = E(key)
    if fmt == "spr":
        if not griddable(key):
            raise ItemError("that answer could not be entered in the grid")
        # x may be either number, so the other one is a right answer here
        return Item("nleq.sum_product", "a sum and a product", difficulty, seed,
                    sent(stem), "spr", keyx, gridin(key), rationale, params=P,
                    spr_mistakes=gridin_pool(keyx, pool.values(), [lo, hi]))
    ch, tex, why, letter = choices(keyx, pick(pool, wrongs), rng, guard=wrongs is None)
    return Item("nleq.sum_product", "a sum and a product", difficulty, seed,
                sent(stem), "mcq", keyx, letter, rationale, ch, why, tex, params=P)


# ------------------------------------------- the slope of a line through a curve

def secant_slope(rng: random.Random, seed: int, *, a=1, b=0, c=None, x1=None,
                 x2=None, fmt="mcq", wrongs=None, difficulty="hard") -> Item:
    """A line crosses y = ax² + bx + c twice; its slope is a(x₁ + x₂) + b."""
    a, b = q(a), q(b)
    c = Q(rng.randint(-20, 20)) if c is None else q(c)
    x1 = Q(rng.randint(-8, 8)) if x1 is None else q(x1)
    x2 = Q(rng.randint(-8, 8)) if x2 is None else q(x2)
    if x1 == x2 or a == 0:
        raise ItemError("two points on the same vertical line have no slope")
    y1, y2 = a * x1 * x1 + b * x1 + c, a * x2 * x2 + b * x2 + c
    key = (y2 - y1) / (x2 - x1)
    if fmt == "mcq" and key == 0:
        raise ItemError("a zero slope collapses the sign mistakes")
    curve = eq("y", poly((c, b, a)))
    stem = sent(f"In the xy-plane, the graph of {curve} intersects line p at "
                f"({num(x1)}, a) and ({num(x2)}, b), where a and b are constants. "
                f"What is the slope of line p ?")
    pool = {
        "negate": Mis("subtracted the two points in opposite orders on the top and "
                      "the bottom", -key),
        "run_only": Mis("divided by the rise instead of the run",
                        (x2 - x1) / (y2 - y1) if y1 != y2 else None),
        "rise_only": Mis("reported the rise without dividing by the run", y2 - y1),
        "half": Mis("halved the slope, as though the run were twice what it is",
                    key / 2),
        "sum_x": Mis("added the two x-values instead of finding the slope", x1 + x2),
        "sign_first": Mis("dropped the sign of the first point's y-value before "
                          "subtracting", (y2 - abs(y1)) / (x2 - x1)),
        "sign_first_neg": Mis("dropped the sign of the first point's y-value and "
                              "then subtracted the wrong way round",
                              -(y2 - abs(y1)) / (x2 - x1)),
        "no_shift": Mis("left the curve's constant term in the difference",
                        key + c if c else None),
    }
    P = {"kind": "nleq_secant", "a": _p(a), "b": _p(b), "c": _p(c), "x1": _p(x1),
         "x2": _p(x2)}
    rationale = sent(f"The two points are ({num(x1)}, {num(y1)}) and "
                     f"({num(x2)}, {num(y2)}), so the slope is "
                     f"({num(y2)} {MINUS} {num(y1)})/({num(x2)} {MINUS} {num(x1)}) "
                     f"= {num(key)}.")
    keyx = E(key)
    if fmt == "spr":
        if not griddable(key):
            raise ItemError("that answer could not be entered in the grid")
        # key + c is not what keeping c in the rise gives, key ± c/(x₂ − x₁)
        named = [m for n, m in pool.items() if n != "no_shift"]
        return Item("nleq.secant_slope", "the slope of a secant", difficulty, seed,
                    sent(stem), "spr", keyx, gridin(key), rationale, params=P,
                    spr_mistakes=gridin_pool(keyx, named))
    ch, tex, why, letter = choices(keyx, pick(pool, wrongs), rng, guard=wrongs is None)
    return Item("nleq.secant_slope", "the slope of a secant", difficulty, seed,
                sent(stem), "mcq", keyx, letter, rationale, ch, why, tex, params=P)


# ------------------------------------------------------------ params packing

def _p(v) -> list:
    v = q(v)
    return [v.numerator, v.denominator]


def _pack(spec) -> list:
    kind = spec[0]
    if kind == "terms":
        return ["terms", [[_p(c), m] for c, m in spec[1]],
                [[_p(c), m] for c, m in spec[2]]]
    return [kind] + [_p(v) for v in spec[1:]]
