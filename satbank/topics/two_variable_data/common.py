"""Shared machinery for Two-Variable Data.

Three things live here that the templates all need.

**Exact arithmetic that matches the page.** Every slope, intercept, reading and
residual is a `Fraction` until it is printed, so an option is never off by a
rounding error the student cannot see. A negative option prints with the
typeset minus the source uses, not a hyphen.

**The two guards.** A chart can only be read to the resolution of its own
gridlines, and a stem that says *closest* has an answer only while one option is
genuinely nearer than the rest. `separated` refuses a draw whose options are
closer together than the chart can distinguish, and `closest_guard` refuses one
whose true value sits between two of them. Both raise `ItemError`, so the
registry simply draws again.

**A scatter that really does have the drawn line as its line of best fit.**
`fit_scatter` builds the points as the line plus a residual vector chosen to be
orthogonal to both `1` and `x`, which is exactly the condition for the ordinary
least-squares line of those points to be the line it started from. `regression`
recomputes it, and `option_check.py` recomputes it a third time from the pixels.
"""

from __future__ import annotations

import random
from fractions import Fraction as Q

from ...exact import E, Exact
from ...item import ItemError, Mis, assemble

__all__ = ["q", "num_str", "MINUS", "year_text", "bow", "ascending", "snap", "assemble_num", "pick", "separated",
           "closest_guard", "regression", "fit_scatter", "balance", "clean",
           "listing", "count_word", "ordinal", "cap_first", "plural"]

MINUS = "−"          # U+2212, the minus sign the source items print


# ------------------------------------------------------------------ numbers

def q(v) -> Q:
    """Anything numeric to an exact Fraction. A float arrives as its digits."""
    if isinstance(v, Q):
        return v
    if isinstance(v, Exact):
        if not v.is_rational:
            raise ItemError("value is not a rational number")
        return v.coef
    if isinstance(v, int):
        return Q(v)
    return Q(str(v))


def _terminates(d: int) -> bool:
    while d % 2 == 0:
        d //= 2
    while d % 5 == 0:
        d //= 5
    return d == 1


def _round(v, places: int = 0) -> Q:
    """Round half away from zero, the way a test paper rounds."""
    v = q(v)
    scale = Q(10) ** places
    x = v * scale
    n, d = x.numerator, x.denominator
    whole = (2 * n + d) // (2 * d) if n >= 0 else -((-2 * n + d) // (2 * d))
    return Q(whole) / scale


def num_str(v, places: int | None = None, group: bool = True) -> str:
    """A number as an option prints it: 480, 1,200, 4.5, −0.7.

    `group=False` prints a year: 1960, never 1,960.
    """
    f = q(v)
    if places is not None:
        f = _round(f, places)
    sign = MINUS if f < 0 else ""
    a = -f if f < 0 else f
    whole = a.numerator // a.denominator
    rest = a - whole
    if places is not None:
        if places == 0:
            return sign + (f"{whole:,}" if group else str(whole))
        digits = str((rest * Q(10) ** places).numerator).rjust(places, "0")
        return f"{sign}{whole:,}.{digits}" if group else f"{sign}{whole}.{digits}"
    if rest == 0:
        return sign + (f"{whole:,}" if group else str(whole))
    if not _terminates(a.denominator):
        return f"{sign}{a.numerator}/{a.denominator}"
    digits = ""
    while rest != 0:
        rest *= 10
        digits += str(rest.numerator // rest.denominator)
        rest -= rest.numerator // rest.denominator
    head = f"{whole:,}" if group else str(whole)
    return f"{sign}{head}.{digits}"


def decimals(v) -> int:
    s = num_str(v)
    return len(s.split(".")[1]) if "." in s else 0


def clean(v, places: int = 2):
    """An SAT answer is a whole number or a short decimal, never 211/11."""
    f = q(v)
    if f.denominator == 1:
        return f
    if _terminates(f.denominator) and decimals(f) <= places:
        return f
    raise ItemError(f"{f} is not an answer this test would print")


# -------------------------------------------------------------- the guards

def snap(v, step, strict: bool = False):
    """`v` rounded to the nearest multiple of `step`, halves away from zero.

    `strict=True` refuses a value sitting exactly halfway, which is the guard a
    stem saying *closest*, *nearest*, *approximately* or *best estimate* needs:
    which of the two neighbours is nearest is then a rounding convention the
    stem never states, and three topics have already shipped an item whose
    printed page cannot produce its own key.
    """
    v, step = q(v), q(step)
    k = v / step
    n, d = k.numerator, k.denominator
    if strict and d == 2:
        raise ItemError(f"{v} sits exactly halfway between two printable answers")
    whole = (2 * n + d) // (2 * d) if n >= 0 else -((-2 * n + d) // (2 * d))
    return Q(whole) * step


def separated(key, others, step) -> None:
    """Refuse options a reader cannot tell apart on this chart.

    A chart can be read only to the spacing of its own gridlines, so an option
    within one gridline of the key is an option the reader has no way to rule
    out. Linear Functions once offered 24 against 25 on an axis gridlined every
    ten and was green on all seven checks; this is that defect's guard.
    """
    step = q(step)
    if step <= 0:
        raise ItemError("a chart with no gridlines cannot be read")
    for o in others:
        gap = abs(q(key) - q(o))
        if gap < step:
            raise ItemError(
                f"the options {num_str(key)} and {num_str(o)} are {num_str(gap)} apart "
                f"on a chart gridlined every {num_str(step)}: no reader can separate them")


def closest_guard(value, key, others) -> None:
    """Refuse a draw whose true value does not clearly pick the keyed option.

    A stem that says *closest*, *nearest*, *approximately* or *best estimate*
    has an answer only while one option is nearer than every other. Three
    topics shipped items whose printed page cannot produce the key -- a value
    landing exactly between two printable answers -- and every check was green,
    because the audit re-derives from the parameters and never from the page.
    """
    v, k = q(value), q(key)
    dk = abs(v - k)
    for o in others:
        o = q(o)
        do = abs(v - o)
        if do <= dk:
            raise ItemError(f"{num_str(v)} is at least as close to {num_str(o)} as it is "
                            f"to the keyed {num_str(k)}")
        if do - dk < abs(k - o) / 4:
            raise ItemError(f"{num_str(v)} sits too near the middle of {num_str(k)} and "
                            f"{num_str(o)} for either to be the closest")


# ------------------------------------------------------- lines of best fit

def regression(points) -> tuple:
    """The ordinary least-squares line of those points, exactly, as (m, b)."""
    xs = [q(p[0]) for p in points]
    ys = [q(p[1]) for p in points]
    n = len(xs)
    if n < 3:
        raise ItemError("a line of best fit needs at least three points")
    mx = sum(xs, Q(0)) / n
    my = sum(ys, Q(0)) / n
    sxx = sum(((x - mx) ** 2 for x in xs), Q(0))
    if sxx == 0:
        raise ItemError("every point has the same x-value")
    sxy = sum(((x - mx) * (y - my) for x, y in zip(xs, ys)), Q(0))
    m = sxy / sxx
    return m, my - m * mx


def balance(xs, resid, p: int, q_i: int) -> list:
    """Set two of the residuals so the whole vector is a true residual vector.

    Least squares leaves residuals with `sum(r) = 0` and `sum(x*r) = 0`; those
    two equations are exactly what makes `y = mx + b` the fitted line of the
    points `(x, mx + b + r)`. Everything outside positions p and q is the
    caller's, and these two are solved for.
    """
    xs = [q(v) for v in xs]
    r = [q(v) for v in resid]
    if p == q_i or xs[p] == xs[q_i]:
        raise ItemError("the two balanced points must sit at different x-values")
    s = sum((v for i, v in enumerate(r) if i not in (p, q_i)), Q(0))
    t = sum((xs[i] * v for i, v in enumerate(r) if i not in (p, q_i)), Q(0))
    rp = (xs[q_i] * s - t) / (xs[p] - xs[q_i])
    r[p] = rp
    r[q_i] = -s - rp
    return r


def fit_scatter(m, b, xs, resid) -> list:
    """The points `(x, mx + b + r)`, refusing any r that is not a residual."""
    m, b = q(m), q(b)
    xs = [q(x) for x in xs]
    r = [q(v) for v in resid]
    if len(xs) != len(r):
        raise ItemError("one residual per point")
    if sum(r, Q(0)) != 0 or sum((x * v for x, v in zip(xs, r)), Q(0)) != 0:
        raise ItemError("those residuals do not leave y = mx + b as the line of best fit")
    return [(x, m * x + b + v) for x, v in zip(xs, r)]


def wiggle(rng: random.Random, n: int, scale) -> list:
    """A random residual vector for `n` equally spaced x-values.

    Built from shifted copies of (1, −2, 1), each of which already sums to zero
    and, on an arithmetic progression of x, is already orthogonal to x. Any
    combination of them is therefore a residual vector, whatever the coefficients.
    """
    if n < 4:
        raise ItemError("too few points to scatter")
    scale = q(scale)
    r = [Q(0)] * n
    for k in range(n - 2):
        c = rng.choice((-1, -1, 0, 1, 1))
        r[k] += c
        r[k + 1] -= 2 * c
        r[k + 2] += c
    if all(v == 0 for v in r):
        raise ItemError("the points landed exactly on the line")
    return [v * scale for v in r]


def bow(xs, top) -> list:
    """A residual vector shaped like a bowl: high at both ends, low in the middle.

    Real series often curve away from their own line of best fit at both ends,
    and a template whose line dips below zero needs its first point lifted
    above the axis. `u² − mean(u²)` is orthogonal to 1 by construction and to x
    because x is symmetric about its own mean, so these are residuals like any
    other and the line of best fit is untouched.
    """
    xs = [q(v) for v in xs]
    n = len(xs)
    if n < 4:
        raise ItemError("too few points to bow")
    mx = sum(xs, Q(0)) / n
    u = [x - mx for x in xs]
    if sum(u, Q(0)) != 0 or sum((v ** 3 for v in u), Q(0)) != 0:
        raise ItemError("a bow needs x-values symmetric about their own mean")
    sq = [v * v for v in u]
    c = sum(sq, Q(0)) / n
    shape = [v - c for v in sq]
    peak = max(shape)
    if peak <= 0:
        raise ItemError("that spacing gives no bow")
    return [q(top) * v / peak for v in shape]


# ------------------------------------------------------------------ options

def pick(pool: dict, order, wrongs=None) -> list:
    """The misconceptions this draw offers, in the order it offers them.

    A free draw takes the template's default order; a source item names the
    three College Board itself printed, so its own option set is reproduced
    rather than crowded out by whichever wrong answers happen to sort first.
    """
    names = list(order if wrongs is None else wrongs)
    out = []
    for name in names:
        if name not in pool:
            raise ItemError(f"no misconception named {name!r} in this pool")
        why, value = pool[name]
        if value is not None:
            out.append(Mis(why, value))
    return out


def ascending(choices, reasons, letter):
    """Put numeric options in the order the SAT prints them.

    `assemble_text` shuffles, which is right for sentences and wrong for four
    years: the engine's own structure check reads those as numbers and expects
    them to ascend.
    """
    try:
        order = sorted(range(4), key=lambda i: Q(str(choices[i]).replace(",", "")))
    except (ValueError, ArithmeticError):
        return choices, reasons, letter
    keyed = order.index("ABCD".index(letter))
    return ([choices[i] for i in order], [reasons[i] for i in order], "ABCD"[keyed])


def _surface(opt: str) -> tuple:
    return ("/" in opt, "." in opt)


def assemble_num(key, mistakes: list[Mis], rng: random.Random, *,
                 prefix: str = "", suffix: str = "", places: int | None = None,
                 signed: bool = False, fillers: str = "shift"):
    """Four numeric options, printed so the key does not give itself away.

    `assemble` never consults the Random it is handed, so it can be run twice
    with the same arguments: the first pass only learns which three distractors
    won, so that how they print can be decided once all four are known.
    """
    if places is not None:
        mistakes = [m for m in mistakes if m.value is None
                    or _round(m.value.coef, places) == m.value.coef]
    key = key if isinstance(key, Exact) else E(q(key))
    picked: list[Exact] = []

    def probe(v):
        picked.append(v)
        return v.plain()

    assemble(key, mistakes, rng, fmt_value=probe, signed=signed, fillers=fillers)
    if places is None:
        dec = [decimals(v.coef) for v in picked]
        key_dec = decimals(q(key))
        if key_dec > 0 and sum(1 for d in dec if d > 0) == 1:
            places = max(dec)

    def show(v):
        return prefix + num_str(v.coef, places) + suffix

    choices, latex, reasons, letter = assemble(key, mistakes, rng, fmt_value=show,
                                               signed=signed, fillers=fillers)
    if len(set(choices)) != 4:
        raise ItemError(f"two options print the same: {choices}")
    shapes = [_surface(c) for c in choices]
    if shapes.count(shapes["ABCD".index(letter)]) == 1:
        raise ItemError(f"the key is the only option that reads like "
                        f"{choices['ABCD'.index(letter)]!r}")
    return choices, latex, reasons, letter


def option_values(choices: list[str]) -> list:
    """The numbers four printed options carry, for the separation guard."""
    out = []
    for c in choices:
        t = c.replace(MINUS, "-").replace(",", "").strip().lstrip("$").rstrip("%")
        out.append(Q(t))
    return out


# -------------------------------------------------------------------- prose

WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven",
         8: "eight", 9: "nine", 10: "ten", 11: "eleven", 12: "twelve",
         13: "thirteen", 14: "fourteen", 15: "fifteen", 16: "sixteen",
         17: "seventeen", 18: "eighteen", 19: "nineteen", 20: "twenty",
         21: "twenty-one", 22: "twenty-two", 23: "twenty-three",
         24: "twenty-four", 25: "twenty-five"}

ORDINALS = {1: "st", 2: "nd", 3: "rd"}


def count_word(n: int) -> str:
    return WORDS.get(n, f"{n:,}")


def ordinal(n: int) -> str:
    if 11 <= n % 100 <= 13:
        return f"{n}th"
    return f"{n}{ORDINALS.get(n % 10, 'th')}"


def plural(n: int, noun: str, many: str | None = None) -> str:
    return f"{n} {noun}" if n == 1 else f"{n} {many or noun + 's'}"


def listing(parts: list[str], joiner: str = "and") -> str:
    if len(parts) == 1:
        return parts[0]
    if len(parts) == 2:
        return f"{parts[0]} {joiner} {parts[1]}"
    return ", ".join(parts[:-1]) + f", {joiner} {parts[-1]}"


def year_text(v) -> str:
    """A year, never grouped: 1960 and not 1,960."""
    return num_str(v, group=False)


def cap_first(s: str) -> str:
    return s[0].upper() + s[1:] if s else s
