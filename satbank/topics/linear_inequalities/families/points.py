"""Testing a candidate against an inequality -- the family whose options are
points rather than relations.

Seven of the official items ask the same question in four costumes: which
ordered pair, which of three labelled pairs, which table of pairs, and which
system the given point satisfies. The mathematics is one substitution either
way, so one template builds all four and one solver checks all four by putting
the numbers back in.

The distractors are the points a particular slip accepts. A point on the far
side of the boundary is the student who read the relation the wrong way round;
a point that works only with its coordinates exchanged is the student who
substituted y for x; a point on the line itself is the student who forgot that
a strict inequality excludes its own boundary. Each option is labelled with the
first of those that would have let it through.
"""

from __future__ import annotations

import random

from ....exact import E
from ....item import Item, ItemError, Mis
from .kit import Q, num, rel, sent, side, text_choices

__all__ = ["point_solution"]

# A constraint is printed the way the source prints one:
#   ("y", m, b, op)       y ⋈ mx + b
#   ("lin", a, b, c, op)  ax + by ⋈ c
#   ("var", name, c, op)  x ⋈ c
LOOSE = {"<": "<=", ">": ">=", "<=": "<=", ">=": ">="}
FLIP = {"<": ">", ">": "<", "<=": ">=", ">=": "<="}


def _cmp(a, op: str, b) -> bool:
    return {"<": a < b, "<=": a <= b, ">": a > b, ">=": a >= b}[op]


def show(row) -> str:
    """The relation as it is printed above the question."""
    if row[0] == "y":
        _, m, b, op = row
        return rel("y", op, side([(m, "x")], b))
    if row[0] == "lin":
        _, a, b, c, op = row
        return rel(side([(a, "x"), (b, "y")]), op, num(c))
    _, name, c, op = row
    return rel(name, op, num(c))


def boundary(row) -> str:
    """The line an inequality's region is bounded by."""
    if row[0] == "y":
        return f"y = {side([(row[1], 'x')], row[2])}"
    if row[0] == "lin":
        return f"{side([(row[1], 'x'), (row[2], 'y')])} = {num(row[3])}"
    return f"{row[1]} = {num(row[2])}"


def holds(row, x, y) -> bool:
    x, y = Q(x), Q(y)
    if row[0] == "y":
        return _cmp(y, row[3], Q(row[1]) * x + Q(row[2]))
    if row[0] == "lin":
        return _cmp(Q(row[1]) * x + Q(row[2]) * y, row[4], Q(row[3]))
    return _cmp(x if row[1] == "x" else y, row[3], Q(row[2]))


def satisfies(rows, x, y) -> bool:
    return all(holds(r, x, y) for r in rows)


def substituted(row, x, y) -> str:
    """The relation with the point put in, and then worked out."""
    if row[0] == "y":
        _, m, b, op = row
        inner = side([(m, f"({num(x)})")], b)
        return f"{rel(num(y), op, inner)}, or {rel(num(y), op, num(m * Q(x) + b))}"
    if row[0] == "lin":
        _, a, b, c, op = row
        inner = side([(a, f"({num(x)})"), (b, f"({num(y)})")])
        return f"{rel(inner, op, num(c))}, or {rel(num(a * Q(x) + b * Q(y)), op, num(c))}"
    _, name, c, op = row
    return rel(num(x if name == "x" else y), op, num(c))


def _positive(row):
    """The same relation with every minus sign on a coefficient dropped."""
    if row[0] == "y":
        return ("y", abs(Q(row[1])), row[2], row[3])
    if row[0] == "lin":
        return ("lin", abs(Q(row[1])), abs(Q(row[2])), row[3], row[4])
    return row


def _flipped(row):
    return row[:-1] + (FLIP[row[-1]],)


def _loosened(row):
    return row[:-1] + (LOOSE[row[-1]],)


def _on_line(rows, x, y) -> bool:
    return any(not holds(r, x, y) and holds(_loosened(r), x, y) for r in rows)


def pt(x, y) -> str:
    return f"({num(x)}, {num(y)})"


# --------------------------------------------------------- naming the slip

def _reason(rows, x, y, used: set) -> tuple[str, str]:
    """The first slip that would have let this point through, and its name.

    Order matters: the most specific explanation wins, and a name already spent
    on another option falls through to the next, so no two options carry the
    same sentence.
    """
    one = len(rows) == 1
    what = "the inequality" if one else "both inequalities"
    # the relation the point actually sits on, and the one a dropped minus
    # sign would actually change -- naming the wrong row makes the sentence
    # say nothing
    on = next((r for r in rows
               if not holds(r, x, y) and holds(_loosened(r), x, y)), None)
    signed = next((r for r in rows if show(_positive(r)) != show(r)), None)
    tests = [
        ("boundary", on is not None and all(holds(_loosened(r), x, y)
                                            for r in rows),
         f"the point lies on the boundary line {boundary(on)}, which a strict "
         f"inequality leaves out" if on else ""),
        ("swap", satisfies(rows, y, x),
         "substituted the coordinates in the other order, putting the "
         "y-value in for x"),
        ("sign", signed is not None and satisfies([_positive(r) for r in rows],
                                                  x, y),
         f"dropped a minus sign on a coefficient, which turns {show(signed)} "
         f"into {show(_positive(signed))}" if signed else ""),
        ("flip", satisfies([_flipped(r) for r in rows], x, y),
         f"read {what} the wrong way round, so the region on the other side "
         f"of the boundary looked like the solution"),
    ]
    if not one:
        for i in range(len(rows)):
            ok = holds(rows[i], x, y) and not satisfies(rows, x, y)
            tests.insert(2, (f"only{i}", ok,
                             f"checked {show(rows[i])} and stopped, without "
                             f"testing the other inequality"))
    for name, ok, why in tests:
        if ok and name not in used:
            used.add(name)
            return name, why
    bad = next(r for r in rows if not holds(r, x, y))
    return "misread", (f"did not substitute the point into {show(bad)}, which "
                       f"{pt(x, y)} does not satisfy")


# -------------------------------------------------- which point is a solution

POINT_FRAMES = [
    "{q}\nWhich point (x, y) is a solution to the given inequality in the "
    "xy-plane?",
    "{q}\nWhich of the following ordered pairs (x, y) satisfies the given "
    "inequality?",
]
SYSTEM_FRAMES = [
    "{q}\nWhich of the following ordered pairs (x, y) satisfies the system of "
    "inequalities above?",
    "{q}\nWhich point (x, y) is a solution to the given system of inequalities "
    "in the xy-plane?",
]


def _draw_rows(rng, n: int):
    rows = []
    for i in range(n):
        if rng.random() < 0.7:
            m = rng.choice([i for i in range(-5, 6) if i])
            b = rng.randint(-6, 6)
            rows.append(("y", Q(m), Q(b), rng.choice(["<", "<=", ">", ">="])))
        else:
            a = rng.choice([i for i in range(-4, 5) if i])
            b = rng.choice([i for i in range(-4, 5) if i])
            rows.append(("lin", Q(a), Q(b), Q(rng.randint(-8, 8)),
                         rng.choice(["<", "<=", ">", ">="])))
    return rows


def _as_rows(raw):
    """Source rows arrive as plain tuples; the numbers become exact here."""
    out = []
    for r in raw:
        if r[0] == "y":
            out.append(("y", Q(r[1]), Q(r[2]), r[3]))
        elif r[0] == "lin":
            out.append(("lin", Q(r[1]), Q(r[2]), Q(r[3]), r[4]))
        else:
            out.append(("var", r[1], Q(r[2]), r[3]))
    return out


def _which_point(rng, kw):
    rows = _as_rows(kw["rows"]) if kw.get("rows") else _draw_rows(
        rng, kw.get("n_rows") or rng.choice([1, 1, 2]))
    span = kw.get("span", 6)
    grid = [(x, y) for x in range(-span, span + 1) for y in range(-span, span + 1)]
    good = [p for p in grid if satisfies(rows, *p)]
    bad = [p for p in grid if not satisfies(rows, *p)]
    if not good or len(bad) < 3:
        raise ItemError("the region leaves nothing to choose between")
    cands = kw.get("cands")
    if cands is None:
        key_pt = rng.choice(good)
        rng.shuffle(bad)
        picked, used = [], set()
        for p in bad:
            name, why = _reason(rows, *p, used)
            if name == "misread":
                continue
            picked.append((p, why))
            if len(picked) == 3:
                break
        if len(picked) < 3:
            raise ItemError("no three wrong points with three different slips")
        cands = [key_pt] + [p for p, _ in picked]
        wrong = [Mis(why, pt(*p)) for p, why in picked]
    else:
        hits = [p for p in cands if satisfies(rows, *p)]
        if len(hits) != 1:
            raise ItemError(f"{len(hits)} of the given points are solutions")
        key_pt, used = hits[0], set()
        wrong = [Mis(_reason(rows, *p, used)[1], pt(*p))
                 for p in cands if p != key_pt]

    frames = POINT_FRAMES if len(rows) == 1 else SYSTEM_FRAMES
    frame = frames[kw.get("frame", 0) % len(frames)]
    stem = frame.format(q="\n".join(show(r) for r in rows))
    P = {"rows": [list(map(_plain, r)) for r in rows],
         "cands": [[pt(*p), float(p[0]), float(p[1])] for p in cands]}
    checks = ", and ".join(substituted(r, *key_pt) for r in rows)
    fails = ("the inequality" if len(rows) == 1 else
             "at least one of the two inequalities")
    rationale = (f"Substituting x = {num(key_pt[0])} and y = {num(key_pt[1])} "
                 f"gives {checks}, both of which are true. Each of the other "
                 f"three points fails {fails}."
                 if len(rows) > 1 else
                 f"Substituting x = {num(key_pt[0])} and y = {num(key_pt[1])} "
                 f"gives {checks}, which is true. Each of the other three "
                 f"points fails {fails}.")
    return pt(*key_pt), wrong, stem, P, rationale, "medium"


def _plain(v):
    return v if isinstance(v, str) else float(v)


# ------------------------------------------- which of three labelled pairs

ROMAN = ("I", "II", "III")
TRANSFORMS = {
    "swap": ("substituted each pair with the coordinates in the other order",
             lambda rows, x, y: satisfies(rows, y, x)),
    "abs": ("ignored the sign of the left side, so a negative value was "
            "compared as though it were positive",
            lambda rows, x, y: _abs_holds(rows, x, y)),
    "negative": ("looked for pairs that make the left side negative rather "
                 "than less than the number on the right",
                 lambda rows, x, y: _left(rows[0], x, y) < 0),
    "flip": ("read the inequality the wrong way round",
             lambda rows, x, y: satisfies([_flipped(r) for r in rows], x, y)),
    "loose": ("counted a pair that makes the two sides equal, although the "
              "inequality is strict",
              lambda rows, x, y: satisfies([_loosened(r) for r in rows], x, y)),
}


def _left(row, x, y) -> Q:
    """The value of the left side of the relation, as it is printed."""
    if row[0] == "y":
        return Q(y)
    if row[0] == "lin":
        return Q(row[1]) * Q(x) + Q(row[2]) * Q(y)
    return Q(x) if row[1] == "x" else Q(y)


def _abs_holds(rows, x, y) -> bool:
    row = rows[0]
    if row[0] != "lin":
        return False
    return _cmp(abs(Q(row[1]) * Q(x) + Q(row[2]) * Q(y)), row[4], Q(row[3]))


def _name_subset(flags) -> str:
    names = [r for r, f in zip(ROMAN, flags) if f]
    if len(names) == 3:
        return "I, II, and III"
    return f"{' and '.join(names)} only"


def _roman(rng, kw):
    rows = _as_rows(kw["rows"]) if kw.get("rows") else _draw_rows(rng, 1)
    pairs = kw.get("pairs")
    if pairs is None:
        pool = [(x, y) for x in range(-4, 7) for y in range(-4, 7)]
        rng.shuffle(pool)
        pairs = pool[:3]
    flags = [satisfies(rows, *p) for p in pairs]
    if not any(flags) or all(flags):
        raise ItemError("the three pairs do not split, so the options collapse")
    key = _name_subset(flags)
    picks = kw.get("picks") or ["swap", "abs", "negative", "flip", "loose"]
    wrong, seen = [], {tuple(flags)}
    for name in picks:
        why, test = TRANSFORMS[name]
        got = tuple(bool(test(rows, *p)) for p in pairs)
        if got in seen or not any(got):
            continue
        seen.add(got)
        wrong.append(Mis(why, _name_subset(got)))
    listed = "\n".join(f"{r}. {pt(*p)}" for r, p in zip(ROMAN, pairs))
    stem = (f"{show(rows[0])}\n{listed}\nWhich of the ordered pairs (x, y) "
            f"listed above satisfies the given inequality?")
    P = {"rows": [list(map(_plain, r)) for r in rows],
         "pairs": [[float(a), float(b)] for a, b in pairs]}
    yes = [r for r, f in zip(ROMAN, flags) if f]
    rationale = (f"Substituting each pair into {show(rows[0])} leaves it true "
                 f"for {' and '.join(yes)} and false for the rest, so the "
                 f"answer is {key}.")
    return key, wrong, stem, P, rationale, "easy"


# ------------------------------------------------- which table of pairs

TABLE_FRAMES = [
    "{q}\nFor which of the following lists of ordered pairs (x, y) are all "
    "three pairs solutions to the given inequality?",
    "{q}\nEach of the following lists gives three ordered pairs (x, y). "
    "For which list is every pair a solution to "
    "the given inequality?",
]


def _rows_text(pairs) -> str:
    return ", ".join(pt(*p) for p in pairs)


def _table(rng, kw):
    row = _as_rows(kw["rows"])[0] if kw.get("rows") else _draw_rows(rng, 1)[0]
    if row[0] != "y":
        raise ItemError("a table item is printed with y on its own")
    xs = kw.get("xs") or sorted(rng.sample(range(1, 12), 3))
    step = kw.get("step") or rng.choice([2, 3, 4, 5, 6])
    up = row[3] in (">", ">=")
    good, bad = (step, -step) if up else (-step, step)
    key_off = kw.get("key_off") or [good] * 3
    offs = kw.get("wrong_offs") or [
        [0, 0, 0], [bad] * 3, [good, bad, 0], [bad, good, good],
        [good, good, bad]]

    def build(offsets):
        return [(x, Q(row[1]) * Q(x) + Q(row[2]) + Q(o))
                for x, o in zip(xs, offsets)]

    key_rows = build(key_off)
    if not all(satisfies([row], *p) for p in key_rows):
        raise ItemError("the keyed table does not satisfy the inequality")
    wrong, seen = [], {_rows_text(key_rows)}
    for offsets in offs:
        pairs = build(offsets)
        misses = [p for p in pairs if not satisfies([row], *p)]
        text = _rows_text(pairs)
        if not misses or text in seen:
            continue
        seen.add(text)
        if all(o == 0 for o in offsets):
            why = (f"used {boundary(row)} itself, so every pair sits on the "
                   f"boundary line, which a strict inequality leaves out")
        elif len(misses) == len(pairs):
            why = ("put every value of y on the wrong side of the boundary "
                   "line")
        elif len(misses) == 1:
            why = (f"the pair at x = {num(misses[0][0])} lies on the wrong "
                   f"side of the boundary line, although the other two are "
                   f"solutions")
        else:
            hit = next(p for p in pairs if satisfies([row], *p))
            why = (f"checked the pair at x = {num(hit[0])} and stopped; the "
                   f"other two lie on the wrong side of the boundary line")
        wrong.append(Mis(why, text))
    if len(wrong) < 3:
        raise ItemError("could not build three tables that all fail")
    wrong = wrong[:3]
    frame = TABLE_FRAMES[kw.get("frame", 0) % len(TABLE_FRAMES)]
    stem = frame.format(q=show(row))
    tables = [key_rows] + [build(o) for o in offs
                           if _rows_text(build(o)) in {m.value for m in wrong}]
    P = {"rows": [list(map(_plain, row))],
         "tables": [[_rows_text(t), [[float(a), float(b)] for a, b in t]]
                    for t in tables]}
    rationale = (f"At x = {num(xs[0])} the boundary is "
                 f"{num(Q(row[1]) * Q(xs[0]) + Q(row[2]))}, and only one table "
                 f"keeps every value of y on the required side of the boundary "
                 f"at all three values of x.")
    return _rows_text(key_rows), wrong, stem, P, rationale, "medium"


# ------------------------------------------ which system the point satisfies

def _quadrant(rng, kw):
    x = kw.get("x") if kw.get("x") is not None else rng.choice(
        [i for i in range(-9, 10) if i])
    y = kw.get("y") if kw.get("y") is not None else rng.choice(
        [i for i in range(-9, 10) if i])
    if x == 0 or y == 0:
        raise ItemError("a coordinate of zero satisfies neither sign condition")
    strict = kw.get("op", ">")
    weak = {">": "<", "<": ">"}[strict]
    sx = strict if x > 0 else weak
    sy = strict if y > 0 else weak

    def system(ox, oy) -> str:
        return f"{rel('x', ox, '0')}, {rel('y', oy, '0')}"

    key = system(sx, sy)
    other = {sx: {">": "<", "<": ">"}[sx], sy: {">": "<", "<": ">"}[sy]}
    wrong = [
        Mis(f"read the second coordinate as {_sign_word(-y)}, although "
            f"{num(y)} is {_sign_word(y)}", system(sx, other[sy])),
        Mis(f"read the first coordinate as {_sign_word(-x)}, although "
            f"{num(x)} is {_sign_word(x)}", system(other[sx], sy)),
        Mis("read both coordinates as having the opposite sign",
            system(other[sx], other[sy]))]
    stem = (f"The point {pt(x, y)} in the xy-plane is a solution to which of "
            f"the following systems of inequalities?")
    P = {"point": [float(x), float(y)],
         "systems": [[key, [["var", "x", 0.0, sx], ["var", "y", 0.0, sy]]]] +
                    [[m.value, _sys_rows(m.value)] for m in wrong]}
    rationale = (f"The first coordinate, {num(x)}, is {_sign_word(x)} and the "
                 f"second, {num(y)}, is {_sign_word(y)}, so the point lies "
                 f"where {key}.")
    return key, wrong, stem, P, rationale, "easy"


def _sign_word(v) -> str:
    return "positive" if v > 0 else "negative"


def _sys_rows(text: str):
    out = []
    for part in text.split(", "):
        name, op, rhs = part.split(" ")
        out.append(["var", name, float(rhs), "<" if op == "<" else ">"])
    return out


# -------------------------------------------------------------- the template

ASKS = {"point": _which_point, "roman": _roman, "table": _table,
        "system": _quadrant}


def point_solution(rng: random.Random, seed: int, *, ask=None, **kw) -> Item:
    """Which candidate satisfies the relation -- a point, a list, or a table."""
    ask = ask or rng.choice(list(ASKS))
    key, wrong, stem, P, rationale, tier = ASKS[ask](rng, kw)
    P["kind"] = "ineq_point_solution"
    P["ask"] = ask
    ch, why, letter = text_choices(key, wrong, rng)
    return Item("ineq.point_solution", "testing a candidate against an "
                "inequality", kw.get("tier", tier), seed, sent(stem), "mcq",
                E(0), letter, rationale, ch, why, list(ch), params=P)
