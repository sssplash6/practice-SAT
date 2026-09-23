"""How a nonlinear equation is printed, and how its four options are built.

Everything on this topic's page is an equation: a quadratic set to zero, a
radical, a rational equation, a system of a line and a curve, a formula
rearranged for one of its letters. The printing lives here once -- a
coefficient, a power, a signed sum, a bracket, an ordered pair, a solution set
-- and nothing in this file solves anything. The algebra lives in the families
and is re-derived, from the mathematics rather than from these helpers, in
`audit.py`.

The SAT is typeset, so this is too: x², √, ±, and U+2212 for a minus sign.
"""

from __future__ import annotations

import random
import re
from fractions import Fraction as Q

from ...exact import E, Exact
from ...item import (ItemError, Mis, assemble, assemble_text, gridin_mistakes,
                     numeral)

__all__ = ["Q", "E", "MINUS", "PM", "ROOT", "q", "ex", "num", "dec", "sup",
           "mono", "join", "poly", "paren", "frac", "prod", "point", "setof",
           "sent", "displayed", "terminating", "griddable", "gridin", "choices",
           "pick", "eq", "signed_terms", "coef_times", "opt", "text_choices",
           "cap", "gridin_pool"]

MINUS = "−"        # the typeset minus the source prints
PM = "±"
ROOT = "√"
_SUP = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶"
                                   "⁷⁸⁹")
GROUP_FROM = 1_000


# ------------------------------------------------------------------ numbers

def q(v) -> Q:
    if isinstance(v, Q):
        return v
    if isinstance(v, float):
        return Q(str(v))
    if isinstance(v, Exact):
        if v.pi_exp != 0 or v.rad != 1:
            raise ValueError(f"{v.plain()} is not a rational value")
        return v.coef
    return Q(v)


def ex(v) -> Exact:
    return v if isinstance(v, Exact) else E(q(v))


def terminating(v) -> bool:
    d = q(v).denominator
    for p in (2, 5):
        while d % p == 0:
            d //= p
    return d == 1


def sup(n: int) -> str:
    return str(int(n)).translate(_SUP)


def num(v, group: bool = True) -> str:
    """A bare number as the source prints it: 8, −11, 40,000, 9/4."""
    v = q(v)
    if v.denominator == 1:
        n = abs(v.numerator)
        body = f"{n:,}" if group and n >= GROUP_FROM else str(n)
    else:
        body = f"{abs(v.numerator)}/{v.denominator}"
    return (MINUS if v < 0 else "") + body


def dec(v, places: int | None = None) -> str:
    """A decimal: 0.606, 331.3, 4.5. Falls back to a fraction when it repeats."""
    v = q(v)
    if places is None:
        if not terminating(v):
            return num(v)
        d, twos, fives = v.denominator, 0, 0
        while d % 2 == 0:
            d //= 2
            twos += 1
        while d % 5 == 0:
            d //= 5
            fives += 1
        places = max(twos, fives)
    head = MINUS if v < 0 else ""
    a = abs(v)
    if places == 0:
        return head + f"{int(a):,}"
    return head + f"{float(a):,.{places}f}"


GRID_WIDTH = 5          # characters a positive grid-in answer may use


def griddable(v) -> bool:
    """What a student can actually enter.

    The digital SAT takes five characters for a positive answer and six for a
    negative one, the extra being the minus sign -- so the test is on the length
    of what is printed, once the sign is set aside. `−0.5625` is six characters
    of answer and does not fit, however exact it is.
    """
    v = q(v)
    if v.denominator == 1:
        return abs(v.numerator) < 100_000
    if not terminating(v) and (abs(v.numerator) >= 1000 or v.denominator >= 1000):
        return False
    return len(gridin(v).lstrip("-" + MINUS)) <= GRID_WIDTH


def gridin(v) -> str:
    """The grid-in form: digits only, a short decimal, or a fraction.

    Nothing here is ever rounded. A decimal is used only when it is exactly the
    value -- the round trip through `Q` is what proves that -- and anything else
    is printed as a fraction, so the page can never carry an answer the key does
    not have. Three topics in earlier waves shipped an item whose printed page
    could not produce its own key, every one of them by rounding; this topic has
    no stem that says `closest`, `nearest` or `approximately` and none that
    prints money, so the exactness below is the whole of the guard it needs.
    """
    v = q(v)
    if v.denominator == 1:
        return str(v.numerator)
    if terminating(v):
        s = f"{float(v):.6f}".rstrip("0").rstrip(".")
        if Q(s) == v:                       # exact, not merely close
            return s
    return f"{v.numerator}/{v.denominator}"


# -------------------------------------------------------------- expressions

def mono(c, sym: str = "", power: int = 1, style: str = "frac") -> str:
    """One term: '3x²', '−x', '(1/2)y', '0.606T', '42cf', '8'."""
    c = q(c)
    body = "" if not sym else (sym if power == 1 else sym + sup(power))
    if c == 0:
        return "0"
    if not body:
        return dec(c) if style == "dec" else num(c)
    if c == 1:
        return body
    if c == -1:
        return MINUS + body
    if c.denominator != 1 and style == "frac":
        return (MINUS if c < 0 else "") + f"({num(abs(c))}){body}"
    head = dec(c) if style == "dec" else num(c)
    return f"{head}{body}"


def join(parts: list[str]) -> str:
    """Sum already-signed pieces readably: '3x − 7', never '3x + −7'."""
    parts = [p for p in parts if p not in ("", "0")]
    if not parts:
        return "0"
    out = parts[0]
    for p in parts[1:]:
        if p.startswith(MINUS):
            out += f" {MINUS} {p[1:]}"
        elif p.startswith("-"):
            out += f" {MINUS} {p[1:]}"
        else:
            out += f" + {p}"
    return out


def signed_terms(terms, style: str = "frac") -> str:
    """A signed sum from [(coefficient, symbol), ...]; '' is the constant term."""
    return join([mono(c, s, style=style) for c, s in terms if q(c) != 0]) or "0"


def poly(coeffs, var: str = "x", style: str = "frac") -> str:
    """Coefficients lowest degree first: (18, -15, 3) -> '3x² − 15x + 18'."""
    parts = []
    for i in range(len(coeffs) - 1, -1, -1):
        if q(coeffs[i]) != 0:
            parts.append(mono(coeffs[i], var if i else "", i or 1, style))
    return join(parts) if parts else "0"


def paren(body: str) -> str:
    return f"({body})"


def _atomic(body: str) -> bool:
    """Does this printed piece need no brackets inside a product or quotient?"""
    return not re.search(r"[+\s]|" + MINUS, body.strip().lstrip(MINUS))


def frac(numerator: str, denominator: str) -> str:
    """A quotient as the page prints one: 'mv²/L', '(k + 15m)/8', '14/(p − 9)'."""
    n = numerator if _atomic(numerator) else paren(numerator)
    d = denominator if _atomic(denominator) else paren(denominator)
    return f"{n}/{d}" if d != "1" else n


def prod(*pieces: str) -> str:
    """A product written by juxtaposition: '150vx', '2(n + p)'."""
    return "".join(p for p in pieces if p not in ("", "1"))


def coef_times(c, body: str, style: str = "frac") -> str:
    """'2(n + p)', '−(x − 3)', '(25/9)(D − T)', '100T'."""
    c = q(c)
    inner = body if _atomic(body) else paren(body)
    if c == 1:
        return inner
    if c == -1:
        return MINUS + inner
    if c.denominator != 1 and style == "frac":
        return (MINUS if c < 0 else "") + f"({num(abs(c))}){inner}"
    return f"{dec(c) if style == 'dec' else num(c)}{inner}"


def eq(lhs: str, rhs: str) -> str:
    return f"{lhs} = {rhs}"


def point(x, y, style: str = "frac") -> str:
    fx = x if isinstance(x, str) else (dec(x) if style == "dec" else num(x))
    fy = y if isinstance(y, str) else (dec(y) if style == "dec" else num(y))
    return f"({fx}, {fy})"


def setof(values) -> str:
    """A solution set as the source prints one: '{−1, 5}'."""
    return "{" + ", ".join(v if isinstance(v, str) else num(v) for v in values) + "}"


def sent(text: str) -> str:
    """One space between words; a displayed line keeps its own line."""
    text = re.sub(r"[ \t]+", " ", text)
    return re.sub(r" *\n *", "\n", text).strip()


def displayed(*lines: str) -> str:
    return "\n".join(lines)


def cap(text: str) -> str:
    """A sentence built from clauses still opens with a capital letter."""
    text = text.lstrip()
    return text[:1].upper() + text[1:] if text else text


# --------------------------------------------------------------- option sets

_LETTERS = re.compile(r"[a-zA-Z]")


def _surface(opt: str) -> tuple:
    """What an option looks like at a glance -- the signature the gate uses.

    Both minus signs count. The page prints U+2212 and a literal in this file
    may carry the ASCII hyphen, and reading only one of them stops this seeing
    negatives at all -- which is most of what the guard is for, since a lone
    negative among three positives is the answer. This copy was blind to the
    typeset minus, so it passed option sets the gate then caught.
    """
    return (bool(_LETTERS.search(opt)), "/" in opt, "." in opt,
            opt.strip().startswith(("-", MINUS)))


def _stands_alone(texts, key_index: int) -> bool:
    """Is the key the only option of its shape, with the rest forming a crowd?

    Four options that all look different give nothing away -- every one is then
    the only one of its own shape and the key does not stand out. The key
    standing alone only tells a student something when there is a crowd for it
    to stand out from, which is the rule `check._structure` applies.
    """
    shapes = [_surface(t) for t in texts]
    others = [s for i, s in enumerate(shapes) if i != key_index]
    return (shapes.count(shapes[key_index]) == 1
            and max(others.count(s) for s in others) > 1)


def opt(v) -> str:
    """A numeric option as the page prints it: 9/4, 40,000, −8.

    The minus is the typeset one, because that is what the source prints and
    because a plain hyphen makes a lone negative key the odd one out at a
    glance -- which is a real defect when the source's own option set puts one
    negative against three positives, as `x² = 64` does.
    """
    return ex(v).plain().replace("-", MINUS)


def _free_assembly(key: Exact, pool: list[Mis], fmt_value):
    """Four numeric options in ascending order, with no rule about signs.

    `assemble` refuses an option set in which the key is the only option of its
    sign, on the evidence that College Board never prints one. Two official
    items in this topic do -- x² = 64 keyed −8 against 4, 32 and 128, and
    y = x + 1 with y = x² + x keyed −1 against 0, 2 and 3 -- so those two
    are assembled here instead. The guard that replaces it is the typeset minus:
    printed as U+2212 rather than a hyphen, a lone negative key no longer looks
    different from its neighbours at a glance, which is what the rule was for.
    """
    picked, seen = [], {key}
    for m in pool:
        if m.value is None or m.value in seen:
            continue
        seen.add(m.value)
        picked.append(m)
        if len(picked) == 3:
            break
    if len(picked) < 3:
        raise ItemError("could not build three distinct distractors")
    options = sorted([(key, "")] + [(m.value, m.reason) for m in picked],
                     key=lambda t: float(t[0]))
    show = fmt_value or opt
    texts = [show(v) for v, _ in options]
    letter = "ABCD"[next(i for i, (_, r) in enumerate(options) if r == "")]
    return texts, list(texts), [r for _, r in options], letter


def choices(key, mistakes: list[Mis], rng: random.Random, fmt_value=None,
            signed: bool = True, sign_rule: bool = True, guard: bool = True,
            forbid=()):
    """assemble(), then refuse a draw where the key stands alone on the page.

    An algebra answer is signed, and it solves rather than measures, so the
    fallback near-misses shift rather than scale. The sign rule itself is
    `assemble`'s; nothing here reorders the pool to game it. `signed=False` is
    for the handful of source items whose own four options are a negative key
    against three positives -- a shape `assemble` refuses by default, and
    rightly, but which College Board does print.
    """
    key = ex(key)
    pool = [Mis(m.reason, ex(m.value)) for m in mistakes if m.value is not None]
    built = (_free_assembly(key, pool, fmt_value) if not sign_rule else
             assemble(key, pool, rng, fmt_value=fmt_value or opt, signed=signed,
                      fillers="shift"))
    if len(set(built[0])) != 4:
        raise ItemError("two options render the same way")
    # Striking a value out of the pool is not enough. When the pool runs short
    # `assemble` fills the gap with near-misses of its own -- key ± 1, ± 2 -- and
    # those never passed through the pool, so a second correct answer can arrive
    # by that route: two roots one apart, and the filler for the first is the
    # second. The four options as built are therefore checked against the values
    # the question genuinely admits.
    banned = {float(ex(v)) for v in forbid if v is not None}
    banned.discard(float(key))
    for i, text in enumerate(built[0]):
        if i == "ABCD".index(built[3]):
            continue
        shown = numeral(text)
        if shown is not None and any(abs(shown - b) <= 1e-9 * max(1.0, abs(b))
                                     for b in banned):
            raise ItemError(f"the option {text!r} is a second correct answer")
    if guard and _stands_alone(built[0], "ABCD".index(built[3])):
        raise ItemError("the key would be the only option of its printed form")
    return built


def text_choices(key: str, mistakes: list[Mis], rng: random.Random, variables=(),
                 check: bool = True, guard: bool = False):
    """Four printed expressions, one of them right, shuffled.

    Where the options are equations rather than values there is no ascending
    order to hide the key in, so the only defence against two correct answers is
    to decide each candidate as mathematics before it is printed. Every
    distractor is evaluated against the key at several points and dropped if the
    two agree -- a distractor that is the key in a different jacket is a question
    with no defensible answer, and `assemble_text` would shuffle it in without a
    murmur.

    `guard` additionally refuses a free draw in which the key is the only option
    of its printed shape. Source items are exempt: College Board does print an
    option set whose key is the only fraction, and reproducing what it printed is
    the whole point of encoding one.
    """
    from ...expr import ParseError, agree, parse
    keep, seen = [], {key}
    names = tuple(variables)
    for m in mistakes:
        if m.value is None or m.value in seen:
            continue
        if check and names:
            try:
                same = agree(parse(_rhs(m.value), names=names),
                             parse(_rhs(key), names=names), variables=names)
            except ParseError as exc:
                # `agree` used to answer "not equal" when it could read neither
                # side, which made this guard a no-op for every juxtaposed
                # product. It now says so, and an option this topic prints but
                # cannot read back is a bug here, not an unlucky draw -- so it
                # is raised past `generate`, which would otherwise retry it away.
                raise RuntimeError(f"{__name__}: cannot decide whether "
                                   f"{m.value!r} duplicates the key {key!r}: "
                                   f"{exc}") from exc
            except (ZeroDivisionError, ValueError):
                raise ItemError(f"cannot decide whether {m.value!r} is the key")
            if same:
                continue
        seen.add(m.value)
        keep.append(m)
    if len(keep) < 3:
        raise ItemError("could not build three distinct wrong options")
    built = assemble_text(key, keep, rng)
    if guard:
        shapes = [_surface(c) for c in built[0]]
        if shapes.count(shapes["ABCD".index(built[2])]) == 1:
            raise ItemError("the key would be the only option of its printed form")
    return built


def _rhs(option: str) -> str:
    """The side of a printed option that carries the mathematics."""
    return option.split(" = ", 1)[1] if " = " in option else option


def gridin_pool(key, mistakes, forbid=()) -> list[Mis]:
    """A grid-in's named wrong answers, from the pool its options are drawn from.

    `forbid` is every value the question genuinely admits -- "one possible
    solution" is answered by either root -- and none of those may be filed as a
    mistake; `gridin_mistakes` then drops the key, repeats and missing values.
    """
    banned = [float(ex(v)) for v in forbid if v is not None]
    kept = [Mis(m.reason, ex(m.value)) for m in mistakes if m.value is not None]
    kept = [m for m in kept
            if not any(abs(float(m.value) - b) <= 1e-9 * max(1.0, abs(b))
                       for b in banned)]
    return gridin_mistakes(ex(key), kept)


def pick(pool: dict, wrongs: list | None) -> list[Mis]:
    """The misconceptions this draw offers, in the order they are offered.

    A source item names the three College Board actually printed; a free draw
    gets the whole pool and lets `assemble` choose.
    """
    keys = list(pool) if wrongs is None else list(wrongs)
    out = []
    for k in keys:
        if k not in pool:
            raise ItemError(f"no misconception named {k!r}")
        m = pool[k]
        if m.value is not None:
            out.append(m)
    return out
