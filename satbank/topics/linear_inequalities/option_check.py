"""Read the four printed options back, and check only one of them is right.

`satbank check` asks whether the key is correct. It never asks whether a
*distractor* is also correct: nothing in the engine reads a wrong option as
mathematics -- they are strings `assemble_text` shuffled. An item with two right
answers therefore passes every gate the engine has, and in this topic two
printed inequalities can describe one solution set while looking nothing alike
(−2x > 6 and x < −3), which is exactly how a second correct answer gets in.

This script closes that hole. It parses the printed option strings back into
relations, decides each option's truth set **by putting numbers in on both sides
of every boundary**, and asserts that exactly one option has the property the
stem asks for and that it is the keyed one. It imports no template, no renderer
and no solver: `generate` is used only to obtain the finished item, in the state
a student would receive it, and the reader below re-implements the printing
rules it needs rather than calling the ones that produced them -- so a renderer
that drops a minus sign or a ≤ is visible here.

    PYTHONPATH=. python3 satbank/topics/linear_inequalities/option_check.py
    PYTHONPATH=. python3 .../option_check.py --draws 2000 --template ineq.solve_linear

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
SYM = {"<=": "≤", ">=": "≥", "<": "<", ">": ">"}


class Unreadable(Exception):
    """The printed text is not something this reader understands."""


# ------------------------------------------------ printed text -> arithmetic

TOKEN = re.compile(r"\s*(?:(\d+\.\d+|\d+)|([A-Za-zℓ])|([+\-*/()]))")
MIXED = re.compile(r"(?<![\d.])(\d+) (\d+)/(\d+)")


def tokenize(text: str) -> list:
    """The printed expression as tokens. A mixed number, 11 2/3, is one value:
    it is the only place this page puts a space inside a number."""
    t = MIXED.sub(r"(\1+\2/\3)", text.replace(MINUS, "-").replace(",", ""))
    out, i = [], 0
    while i < len(t):
        if t[i].isspace():
            i += 1
            continue
        m = TOKEN.match(t, i)
        if m is None:
            raise Unreadable(f"{text!r} at {t[i:]!r}")
        num, var, op = m.groups()
        out.append(("n", Q(num)) if num else ("v", var) if var else ("o", op))
        i = m.end()
    return out


def compile_expr(text: str):
    """A printed expression as a function of the variables in it.

    Implicit multiplication is what the page prints: 2x, 165(12.7), (72)(16),
    0.20(300). Nothing here knows how the expression was built.
    """
    toks = tokenize(text)
    pos = 0

    def peek():
        return toks[pos] if pos < len(toks) else None

    def eat(op=None):
        nonlocal pos
        tok = peek()
        if tok is None or (op and tok != ("o", op)):
            raise Unreadable(f"{text!r}: expected {op!r}")
        pos += 1
        return tok

    def atom():
        tok = peek()
        if tok is None:
            raise Unreadable(f"{text!r}: ended early")
        if tok == ("o", "("):
            eat("(")
            f = expression()
            eat(")")
            return f
        if tok[0] == "n":
            eat()
            return lambda env, k=tok[1]: k
        if tok[0] == "v":
            eat()
            return lambda env, name=tok[1]: env[name]
        raise Unreadable(f"{text!r}: stray {tok[1]!r}")

    def unary():
        if peek() == ("o", "-"):
            eat("-")
            inner = unary()
            return lambda env: -inner(env)
        return atom()

    def product():
        f = unary()
        while True:
            tok = peek()
            if tok in (("o", "*"), ("o", "/")):
                eat()
                g = unary()
                f = ((lambda env, a=f, b=g: a(env) * b(env)) if tok == ("o", "*")
                     else (lambda env, a=f, b=g: a(env) / b(env)))
            elif tok is not None and (tok[0] in "nv" or tok == ("o", "(")):
                g = unary()                       # 2x, 165(12.7), (72)(16)
                f = lambda env, a=f, b=g: a(env) * b(env)  # noqa: E731
            else:
                return f

    def expression():
        f = product()
        while peek() in (("o", "+"), ("o", "-")):
            tok = eat()
            g = product()
            f = ((lambda env, a=f, b=g: a(env) + b(env)) if tok == ("o", "+")
                 else (lambda env, a=f, b=g: a(env) - b(env)))
        return f

    fn = expression()
    if pos != len(toks):
        raise Unreadable(f"{text!r}: {toks[pos:]} left over")
    return fn


# -------------------------------------------------- printed text -> relations

RELATION = re.compile(r"\s*(≤|≥|<|>)\s*")
VAR = re.compile(r"[A-Za-zℓ]")


def compare(a: Q, op: str, b: Q) -> bool:
    return {"<": a < b, "≤": a <= b, ">": a > b, "≥": a >= b}[op]


class Cmp:
    """One printed comparison, as two sides that can be evaluated."""

    def __init__(self, lhs: str, op: str, rhs: str):
        self.op, self.text = op, f"{lhs} {op} {rhs}"
        self.lhs, self.rhs = compile_expr(lhs), compile_expr(rhs)

    def holds(self, env: dict) -> bool:
        return compare(self.lhs(env), self.op, self.rhs(env))

    def boundary(self, var: str, env: dict):
        """Where this comparison turns over, as the named variable moves.

        Both sides are linear, so two samples fix the crossing exactly; None
        when the comparison does not depend on this variable.
        """
        def gap(t):
            return self.lhs({**env, var: t}) - self.rhs({**env, var: t})

        at0, at1 = gap(Q(0)), gap(Q(1))
        return None if at1 == at0 else -at0 / (at1 - at0)


def chain(text: str) -> list:
    """`1,510 ≤ d ≤ 4,130` as the two comparisons it stands for."""
    parts = RELATION.split(text.strip())
    if len(parts) < 3 or len(parts) % 2 == 0:
        raise Unreadable(text)
    return [Cmp(parts[i], parts[i + 1], parts[i + 2])
            for i in range(0, len(parts) - 2, 2)]


def formula(text: str) -> list:
    """A printed option as OR of AND of comparisons.

    `x < 6 or x > 18` is a union; `x + y ≥ 20, 3x + 4y ≤ 80` and
    `p + 36 > 60, where p ≤ 150` are both conjunctions -- a system and a rider
    are read the same way, because they mean the same thing.
    """
    ors = []
    for part in re.split(r"\s+or\s+", text.strip()):
        rows = []
        for piece in re.split(r",\s*where\s+|,\s+", part):
            rows += chain(piece)
        ors.append(rows)
    return ors


def holds(f: list, env: dict) -> bool:
    return any(all(c.holds(env) for c in rows) for rows in f)


def variables(text: str) -> set:
    return set(VAR.findall(text.replace("or", " ").replace("where", " ")))


def test_points(fs: list, var: str, env: dict) -> list:
    """Every value worth trying: each boundary, a point either side of it, the
    midpoints between them, and a value far outside them all."""
    edges = sorted({c.boundary(var, env) for f in fs for rows in f for c in rows
                    if c.boundary(var, env) is not None})
    if not edges:
        return [Q(-1000), Q(-1), Q(0), Q(1), Q(1000)]
    gaps = [b - a for a, b in zip(edges, edges[1:])]
    step = min(gaps) / 3 if gaps else Q(1)
    step = min(step, Q(1, 4))
    out = set(edges)
    for e in edges:
        out |= {e - step, e + step}
    out |= {a + (b - a) / 2 for a, b in zip(edges, edges[1:])}
    out |= {edges[0] - 1000, edges[-1] + 1000}
    return sorted(out)


def same_set(f1: list, f2: list, slices: list) -> bool:
    """Do these two printed relations describe the same set?

    Decided by evaluation only: every boundary of either one is visited, and a
    value on each side of it is put into both. Two relations that differ by a
    sign that failed to turn over disagree at the first such value.
    """
    for var, env in slices:
        for t in test_points([f1, f2], var, env):
            here = {**env, var: t}
            try:
                if holds(f1, here) != holds(f2, here):
                    return False
            except (KeyError, ZeroDivisionError):
                return False
    return True


def implies(f1: list, f2: list, slices: list) -> bool:
    """Is everything f1 allows also allowed by f2?"""
    for var, env in slices:
        for t in test_points([f1, f2], var, env):
            here = {**env, var: t}
            if holds(f1, here) and not holds(f2, here):
                return False
    return True


def anchors(fs: list, var: str, names: set) -> list:
    """Values of one variable worth pinning another slice to: wherever some
    comparison turns over, and a step either side of it.

    Pinning at arbitrary numbers is not enough. Two four-row systems can both
    be empty on every slice through the origin and still describe different
    sets -- the region that separates them sits at the rows' own boundaries,
    which is where these values come from.
    """
    zero = {n: Q(0) for n in names if n != var}
    vals = set()
    for f in fs:
        for rows in f:
            for c in rows:
                try:
                    edge = c.boundary(var, zero)
                except KeyError:
                    continue
                if edge is not None:
                    vals.add(edge)
    out = set(vals) | {Q(0), Q(1)}
    for v in sorted(vals)[:8]:
        out |= {v - 1, v + 1}
    return sorted(out)[:16]


def slices_for(names: set, fs: list) -> list:
    """One variable moves; the others are pinned where something changes."""
    names = sorted(names)
    if len(names) == 1:
        return [(names[0], {})]
    out = []
    for v in names:
        others = [n for n in names if n != v]
        for other in others:
            for val in anchors(fs, other, set(names)):
                out.append((v, {n: (val if n == other else Q(0))
                                for n in others}))
    return out


# ------------------------------------------------------ small printed things

def number(text: str) -> Q:
    """`205`, `−14`, `97.9°F`, `2,300`: the number an option carries."""
    t = re.sub(r"[^0-9./\-]", "", text.replace(MINUS, "-").replace(",", ""))
    if not t:
        raise Unreadable(text)
    return Q(t)


def point(text: str) -> tuple:
    m = re.fullmatch(r"\(([^,]+),([^,]+)\)", text.strip())
    if m is None:
        raise Unreadable(text)
    return number(m.group(1)), number(m.group(2))


def pairs(text: str) -> list:
    return [point(p) for p in re.findall(r"\([^)]*\)", text)]


def romans(text: str) -> set:
    return set(re.findall(r"\b(I{1,3})\b", text))


def keyed(item) -> int:
    return "ABCD".index(item.answer)


def one_hit(item, hits: list, what: str) -> str:
    """Both halves of the assertion: exactly one right option, and it is keyed."""
    if hits.count(True) != 1:
        raise AssertionError(f"{hits.count(True)} of the four options are "
                             f"correct ({what})")
    if not hits[keyed(item)]:
        raise AssertionError(f"the keyed option is not the correct one ({what})")
    return what


def against(item, truth: str, names=None) -> str:
    """Every option, compared with a relation built from the item's own numbers
    -- never from the renderer that printed the options."""
    want = formula(truth)
    names = names or (variables(truth) | variables(" ".join(item.choices)))
    hits = []
    for c in item.choices:
        got = formula(c)
        hits.append(same_set(want, got, slices_for(names, [want, got])))
    return one_hit(item, hits, "same solution set")


# ------------------------------------------------------------- the checks

def check_solve(item) -> str:
    """Exactly one option describes the same values as the printed inequality."""
    printed = item.stem.split("\n")[0]
    want = formula(printed)
    var = item.params["var"]
    hits = [same_set(want, formula(c), [(var, {})]) for c in item.choices]
    return one_hit(item, hits, "the values the printed inequality allows")


def check_y_range(item) -> str:
    """The y-values the system leaves, worked out from the printed rows."""
    rows = [chain(line)[0] for line in item.stem.split("\n")[:2]]
    u, v = item.params["u"], item.params["v"]
    x_edge = rows[1].boundary(u, {})
    if x_edge is None or not rows[1].holds({u: x_edge + 1}):
        raise Unreadable("the second row does not bound x from below")
    lowest = rows[0].boundary(v, {u: x_edge})
    if lowest is None:
        raise Unreadable("the first row does not bound y")
    strict = ">" if not rows[0].holds({u: x_edge, v: lowest}) else "≥"
    return against(item, f"{v} {strict} {lowest}", {v})


def check_range_solve(item) -> str:
    rate = Q(*item.params["rate"])
    k1, k2, base, var = (Q(item.params["k1"]), Q(item.params["k2"]),
                         item.params["base"], item.params["var"])
    return against(item, f"{k1}*{base} ≤ {base} + {rate}*{var} ≤ {k2}*{base}",
                   {base, var})


def check_triangle(item) -> str:
    a, b = (Q(int(n)) for n in
            re.search(r"side lengths of (\d+) and (\d+)", item.stem).groups())
    var = item.params["var"]
    return against(item, f"{abs(a - b)} < {var} < {a + b}", {var})


def check_dimension(item) -> str:
    p = item.params
    cap, height, factor = Q(p["cap"]), Q(p["height"]), Q(*p["factor"])
    var = p["var"]
    return against(item, f"0 < {var} ≤ {(cap - height) / (2 * (1 + factor))}",
                   {var})


def check_model_two(item) -> str:
    p = item.params
    a, b = Q(*p["a"]), Q(*p["b"])
    return against(item, f"{a}*{p['u']} + {b}*{p['v']} {SYM[p['op']]} "
                         f"{Q(p['total'])}", {p["u"], p["v"]})


def check_model_one(item) -> str:
    """The relation the situation means, written here from its numbers alone."""
    p, v = item.params, item.params["var"]
    shape = p["shape"]
    if shape == "perimeter":
        truth = f"2*{v} + {2 * Q(p['length'])} {SYM[p['op']]} {Q(p['total'])}"
    elif shape == "payback":
        truth = f"{Q(p['install'])} < ({Q(p['before'])} - {Q(p['after'])})*{v}"
    elif shape == "two_group":
        truth = (f"{Q(p['n1'])}*({v} + {Q(p['gap'])}) + {Q(p['n2'])}*{v} "
                 f"{SYM[p['op']]} {Q(p['total'])}")
    elif shape == "race":
        truth = f"{v} + {Q(p['ride'])} > {Q(p['walk'])}"
    elif shape == "mean":
        total = sum(Q(s) for s in p["scores"])
        n = len(p["scores"]) + 1
        truth = f"({v} + {total})/{n} {SYM[p['op']]} {Q(p['target'])}"
    elif shape == "share":
        half, first, pct = Q(p["half"]), Q(p["first"]), Q(p["pct"])
        truth = (f"{v} + {first} > {pct / 100}*({2 * half}), "
                 f"where {v} ≤ {half}")
    else:
        raise Unreadable(f"no truth for shape {shape!r}")
    return against(item, truth, {v})


def check_model_system(item) -> str:
    p, u, v = item.params, item.params["u"], item.params["v"]
    shape = p["shape"]
    if shape == "count_cost":
        truth = (f"{u} + {v} ≥ {Q(p['least'])}, "
                 f"{Q(p['a'])}*{u} + {Q(p['b'])}*{v} ≤ {Q(p['budget'])}")
    elif shape == "ratio":
        left = (f"{Q(*p['w1'])}*{u} + {Q(*p['w2'])}*{v}" if p["weights"]
                else f"{u} + {v}")
        truth = (f"{left} ≤ {Q(p['cap'])}, "
                 f"{u} {SYM[p['ratio_op']]} {Q(p['k'])}*{v}")
    elif shape == "staffing":
        truth = (f"{Q(p['pay1'])}*{u} + {Q(p['pay2'])}*{v} ≤ {Q(p['budget'])}, "
                 f"{u} + {v} ≥ {Q(p['staff'])}, {u} ≥ {Q(p['min1'])}, "
                 f"{v} ≥ {Q(p['min2'])}")
    else:
        raise Unreadable(f"no truth for shape {shape!r}")
    return against(item, truth, {u, v})


def check_band_extremes(item) -> str:
    p = item.params
    return against(item, f"{Q(*p['lo'])} ≤ {p['var']} ≤ {Q(*p['hi'])}",
                   {p["var"]})


def check_band_scale(item) -> str:
    p = item.params
    lo, hi, rate, var = Q(*p["lo"]), Q(*p["hi"]), Q(*p["rate"]), p["var"]
    if p["shape"] == "divide":
        truth = f"{rate / hi} ≤ {var} ≤ {rate / lo}"
    else:
        truth = f"{rate * lo} {SYM[p['op']]} {var} {SYM[p['op']]} {rate * hi}"
    return against(item, truth, {var})


def check_band_formula(item) -> str:
    p = item.params
    lo, hi = Q(*p["lo"]), Q(*p["hi"])
    mult, off, var = Q(*p["mult"]), Q(*p["off"]), p["var"]
    return against(item, f"{off + mult * lo} {SYM[p['op']]} {var} "
                         f"{SYM[p['op']]} {off + mult * hi}", {var})


def check_which_interval(item) -> str:
    """Exactly one interval keeps every value it allows past the threshold."""
    thr = Q(re.search(r"more than ([\d,.]+) ", item.stem).group(1)
            .replace(",", ""))
    var = re.search(r"values of (\w+), in", item.stem).group(1)
    above = formula(f"{var} > {thr}")
    hits = [implies(formula(c), above, [(var, {})]) for c in item.choices]
    return one_hit(item, hits, "every value past the threshold")


def check_value_in_range(item) -> str:
    p = item.params
    lo, hi, n = Q(*p["lo"]), Q(*p["hi"]), Q(p["n"])
    hits = [lo * n <= number(c) <= hi * n for c in item.choices]
    return one_hit(item, hits, "the only value inside the band")


def _extreme(p, satisfied, want: str) -> int:
    """The greatest or least whole number the condition allows, by trying them."""
    works = [k for k in range(1, 5000) if satisfied(k)]
    if not works:
        raise Unreadable("no whole number satisfies the condition")
    return max(works) if want == "greatest" else min(works)


def check_whole_bound(item) -> str:
    p = item.params
    fee, rate = Q(*p["fee"]), Q(*p["rate"])
    limit, scale = Q(*p["limit"]), Q(*p["scale"])
    want = _extreme(p, lambda k: compare(scale * (fee + rate * k),
                                         SYM[p["op"]], limit), p["want"])
    hits = [number(c) == want for c in item.choices]
    return one_hit(item, hits, f"the {p['want']} whole number that works")


def check_pair_max(item) -> str:
    p = item.params
    w1, w2, cap = Q(*p["w1"]), Q(*p["w2"]), Q(*p["cap"])
    least = int(p["least"])
    best = max(h for h in range(0, least + 6)
               if w1 * max(0, least - h) + w2 * h <= cap)
    hits = [number(c) == best for c in item.choices]
    return one_hit(item, hits, "the largest load that fits")


def check_greatest_value(item) -> str:
    p = item.params
    bound = Q(p["m"]) * Q(p["y"]) + Q(p["sign"]) * Q(p["k"])
    op = SYM[p["op"]]
    # the extreme allowed value: it satisfies the bound and nothing past it does
    hits = []
    for c in item.choices:
        v = number(c)
        hits.append(compare(v, op, bound) and
                    not compare(v + (1 if op == "≤" else -1), op, bound))
    return one_hit(item, hits, "the extreme value the bound allows")


def check_point(item) -> str:
    ask = item.params["ask"]
    if ask == "system":
        x, y = point(re.search(r"The point (\([^)]*\))", item.stem).group(1))
        hits = [holds(formula(c), {"x": x, "y": y}) for c in item.choices]
        return one_hit(item, hits, "the system the point satisfies")
    rows = formula("\n".join(item.stem.split("\n")[:len(item.params["rows"])])
                   .replace("\n", ", "))
    if ask == "point":
        hits = [holds(rows, dict(zip("xy", point(c)))) for c in item.choices]
        return one_hit(item, hits, "the point that satisfies every row")
    if ask == "table":
        hits = [all(holds(rows, dict(zip("xy", p))) for p in pairs(c))
                for c in item.choices]
        return one_hit(item, hits, "the table whose every pair satisfies it")
    listed = re.findall(r"^(I{1,3})\. (\(.*\))$", item.stem, re.M)
    good = {name for name, text in listed
            if holds(rows, dict(zip("xy", point(text))))}
    hits = [romans(c) == good for c in item.choices]
    return one_hit(item, hits, "the pairs that satisfy the inequality")


def check_interpret(item) -> str:
    """The options are sentences, so the property is read out of the sentence:
    which numbers it puts where, and whether what it then claims is true."""
    p = item.params
    if p["shape"] == "pair":
        first, second, cap = Q(p["first"]), Q(p["second"]), Q(p["cap"])
        hits = []
        for c in item.choices:
            m = re.search(rf"{p['n1']} ([\d,]+) and {p['n2']} ([\d,]+), its "
                          rf"{p['measure']} is (.+?) ([\d,]+)\.", c)
            if m is None:
                hits.append(False)
                continue
            a, b, word, limit = (number(m.group(1)), number(m.group(2)),
                                 m.group(3), number(m.group(4)))
            said = {"less than or equal to": "≤", "greater than or equal to": "≥",
                    "less than": "<", "greater than": ">"}.get(word)
            hits.append(said is not None and (a, b) == (first, second) and
                        compare(2 * (a + b), said, limit) and
                        compare(2 * (a + b), SYM[p["op"]], cap))
        return one_hit(item, hits, "the pair read in the order the stem names")
    shown = re.search(r"interpretation of (\d+)(\w) in", item.stem)
    var = shown.group(2)
    goods = re.search(r"purchase (\w) ([\w -]+?) and (\w) ([\w -]+?) for",
                      item.stem)
    thing = goods.group(2) if goods.group(1) == var else goods.group(4)
    hits = [c.startswith("The total amount") and c.endswith(thing)
            for c in item.choices]
    return one_hit(item, hits, "the total spent on the term's own goods")


# a template that normally grids in still has an option set to check; ask for it
KWARGS = {"ineq.greatest_value": {"fmt": "mcq"},
          "ineq.whole_number_bound": {"fmt": "mcq"}}

CHECKS = {
    "ineq.solve_linear": check_solve,
    "ineq.y_range_from_system": check_y_range,
    "ineq.range_solve": check_range_solve,
    "ineq.triangle_third_side": check_triangle,
    "ineq.allowable_dimension": check_dimension,
    "ineq.model_two_var": check_model_two,
    "ineq.model_one_var": check_model_one,
    "ineq.model_system": check_model_system,
    "ineq.band_from_extremes": check_band_extremes,
    "ineq.band_scale": check_band_scale,
    "ineq.band_formula": check_band_formula,
    "ineq.which_interval": check_which_interval,
    "ineq.value_in_range": check_value_in_range,
    "ineq.whole_number_bound": check_whole_bound,
    "ineq.pair_max": check_pair_max,
    "ineq.greatest_value": check_greatest_value,
    "ineq.point_solution": check_point,
    "ineq.interpret": check_interpret,
}


# ------------------------------------------------- proving the check bites

def selftest() -> int:
    """Three faults, injected on purpose. A check nobody has seen fail is worth
    nothing, so each of these must be reported, and by the right half of the
    assertion."""
    cases = []

    # 1. a distractor that is the key again with its rows in another order: the
    #    same conditions, and a different string, so nothing that compares
    #    strings would see it
    item = generate("ineq.model_system", 3)
    rows = item.choices[keyed(item)].split(", ")
    item.choices = list(item.choices)
    item.choices[(keyed(item) + 1) % 4] = ", ".join(rows[1:] + rows[:1])
    cases.append(("a second correct system", item, CHECKS["ineq.model_system"]))

    # 2. the right answer attached to the wrong letter
    item = generate("ineq.solve_linear", 4)
    item.answer = "ABCD"[(keyed(item) + 1) % 4]
    cases.append(("the key moved a letter", item, CHECKS["ineq.solve_linear"]))

    # 3. a distractor rewritten as the key's own inequality, multiplied through
    #    by a negative number -- the sign rule, correctly applied, twice
    item = generate("ineq.solve_linear", 9)
    key = item.choices[keyed(item)]
    var, op, bound = RELATION.split(key)
    flip = {"<": ">", ">": "<", "≤": "≥", "≥": "≤"}[op]
    twin = f"-2{var} {flip} {-2 * Q(bound.replace(MINUS, '-'))}"
    item.choices = list(item.choices)
    item.choices[(keyed(item) + 2) % 4] = twin
    cases.append(("the key again, times −2", item, CHECKS["ineq.solve_linear"]))

    bad = 0
    for what, item, checker in cases:
        try:
            checker(item)
            print(f" FAIL  {what}: not caught")
            bad = 1
        except (AssertionError, Unreadable) as exc:
            print(f"  ok   {what}: {exc}")
    return bad


def check_sources() -> int:
    """The same assertions, over the 46 official option sets as transcribed."""
    import random
    from satbank.topic import load_topics

    bad = 0
    for src in load_topics()["linear_inequalities"].sources:
        item = src.build(random.Random(0))
        if item.fmt != "mcq":
            continue
        checker = CHECKS.get(item.template)
        if checker is None:
            print(f" ????  {src.id}: no check for {item.template}")
            continue
        try:
            checker(item)
        except (AssertionError, Unreadable) as exc:
            bad += 1
            print(f" FAIL  {src.id} ({item.template}): {exc}")
            print(item.pretty())
    print(f"\n{'all official option sets read back' if not bad else bad}"
          f"{'' if not bad else ' official option sets have two right answers'}")
    return 1 if bad else 0


# ------------------------------------------------------------------ driver

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--draws", type=int, default=600,
                    help="seeds to try per template (default 600)")
    ap.add_argument("--template", action="append",
                    help="check only this template; repeatable")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--selftest", action="store_true",
                    help="inject three faults and show each one caught")
    ap.add_argument("--sources", action="store_true",
                    help="check the 46 official option sets instead of draws")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if args.sources:
        return check_sources()

    worst, checked = 0, 0
    for name in args.template or list(CHECKS):
        checker = CHECKS[name]
        made, skipped, bad, what = 0, 0, 0, ""
        for seed in range(args.draws):
            try:
                item = generate(name, seed, **KWARGS.get(name, {}))
            except ItemError:
                continue
            if item.fmt != "mcq":
                skipped += 1
                continue
            made += 1
            try:
                what = checker(item)
            except (AssertionError, Unreadable) as exc:
                bad += 1
                if bad == 1 and not args.quiet:
                    print(f"\n{name} seed {seed}: {exc}")
                    print(item.pretty())
        checked += made
        mark = "  ok  " if not bad else " FAIL "
        tail = f", {skipped} grid-ins" if skipped else ""
        print(f"{mark} {name:<26} {made:>5,} items{tail}, {bad} defects  ({what})")
        worst |= 1 if bad else 0
    print(f"\n{checked:,} option sets read back")
    return worst


if __name__ == "__main__":
    sys.exit(main())
