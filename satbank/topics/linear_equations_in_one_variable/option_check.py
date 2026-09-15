"""Read the four printed options back, and check only one of them is right.

`satbank check` asks whether the key is correct. It never asks whether a
*distractor* is also correct, because nothing in the engine reads a wrong
option as mathematics: `assemble_text` takes four strings, shuffles them and
records which one is the key; `audit` re-derives the key from the parameters;
`structure` counts surface forms and `prose` looks for placeholders. All seven
gate checks stop at the key, so an item with two right answers passes every one
of them and reaches a student as a question with no defensible answer.

This script closes that hole for this topic. It parses the four printed option
strings -- equations, constant pairs, Roman-numeral statement sets, ranges,
sentences and numbers -- back into algebra, decides each option's status from
that algebra alone, and asserts that exactly one option has the property the
stem asks for and that it is the keyed one. Both halves: asserting only that
the key is right is what the engine already does.

The reader shares nothing with the renderer. It is a small tokenizer and a
recursive-descent parser for the printed language of an SAT algebra page --
`9m/7`, `-(1/6)x`, `(17)(11)x`, `782 + 52(t - 2)`, `w^2 + 18w` -- and it
consults no template, no `forms.py` and no item parameter. `generate` is the
only thing imported from the engine, and only to obtain the finished item in
the state a student would receive it.

    PYTHONPATH=. python3 satbank/topics/linear_equations_in_one_variable/option_check.py
    PYTHONPATH=. python3 .../option_check.py --draws 2000 --template lin1.model_context
    PYTHONPATH=. python3 .../option_check.py --selftest
    PYTHONPATH=. python3 .../option_check.py --sources

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
NEQ = "≠"


class Unreadable(Exception):
    """The printed text is not something this reader understands.

    Raised rather than swallowed: an option shape nobody taught this reader
    about is an unchecked option, which is the thing the script exists to stop.
    """


class NotPolynomial(Unreadable):
    """The printed text divides by the unknown -- readable, but no polynomial.

    `2/c` is a perfectly clear option; it simply cannot be the linear model the
    words describe, so the expression check counts it wrong rather than giving
    up on the item.
    """


# --------------------------------------------------- printed text -> numbers

def plain(text: str) -> str:
    """The typeset minus as a hyphen, and 2,300 as 2300."""
    t = str(text).replace(MINUS, "-").replace("–", "-")
    return re.sub(r"(?<=\d),(?=\d\d\d(?:\D|$))", "", t)


def num(text: str) -> Q:
    """A printed number: 8, -11, 2,300, 9/7, 3.5, $9.50, 40%."""
    t = plain(text).replace("$", "").replace("%", "").replace(" ", "").strip()
    if not t:
        raise Unreadable(f"{text!r} carries no number")
    try:
        if "/" in t:
            a, b = t.split("/", 1)
            return Q(a) / Q(b)
        return Q(t)
    except (ValueError, ZeroDivisionError):
        raise Unreadable(f"{text!r} is not a number") from None


# ------------------------------------------- printed text -> a polynomial

# A polynomial in the one unknown, lowest degree first, as exact Fractions.
# Quadratics appear only among the wrong options of `expression_in_terms`
# ("found the area instead of the perimeter"), and have to be read to be
# refused.

def p_num(v) -> tuple:
    return (Q(v),)


P_VAR = (Q(0), Q(1))


def p_trim(c: list) -> tuple:
    while len(c) > 1 and c[-1] == 0:
        c.pop()
    return tuple(c)


def p_add(a: tuple, b: tuple) -> tuple:
    n = max(len(a), len(b))
    return p_trim([(a[i] if i < len(a) else Q(0)) + (b[i] if i < len(b) else Q(0))
                   for i in range(n)])


def p_neg(a: tuple) -> tuple:
    return tuple(-c for c in a)


def p_sub(a: tuple, b: tuple) -> tuple:
    return p_add(a, p_neg(b))


def p_mul(a: tuple, b: tuple) -> tuple:
    out = [Q(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return p_trim(out)


def p_div(a: tuple, b: tuple) -> tuple:
    if len(b) != 1:
        raise NotPolynomial("a division by the unknown")
    if b[0] == 0:
        raise Unreadable("a division by zero")
    return p_trim([c / b[0] for c in a])


def p_pow(a: tuple, n: int) -> tuple:
    out = p_num(1)
    for _ in range(n):
        out = p_mul(out, a)
    return out


TOKEN = re.compile(r"\s*(?:(?P<num>\d+(?:\.\d+)?)|(?P<name>[a-zA-Z])|(?P<op>[-+*/()^]))")


def tokens(text: str) -> list:
    s = plain(text).strip()
    out, i = [], 0
    while i < len(s):
        m = TOKEN.match(s, i)
        if m is None:
            raise Unreadable(f"{text!r} at {s[i:]!r}")
        i = m.end()
        kind = m.lastgroup
        out.append((kind, m.group(kind)))
    return out


class Reader:
    """expr := term (('+'|'-') term)* ; term := factor (('*'|'/'|juxtaposed) factor)*
    factor := ('-'|'+')* atom ['^' int] ; atom := number | letter | '(' expr ')'

    A letter the environment names is its value; any other letter is the one
    unknown, and a second one makes the text unreadable rather than guessed at.
    """

    def __init__(self, text: str, env: dict):
        self.text, self.t, self.i, self.env = text, tokens(text), 0, env
        self.free: set = set()

    def peek(self) -> tuple:
        return self.t[self.i] if self.i < len(self.t) else (None, None)

    def take(self) -> tuple:
        tok = self.peek()
        self.i += 1
        return tok

    def parse(self) -> tuple:
        if not self.t:
            raise Unreadable(f"{self.text!r} is empty")
        v = self.expr()
        if self.i != len(self.t):
            raise Unreadable(f"{self.text!r} trails {self.t[self.i:]!r}")
        if len(self.free) > 1:
            raise Unreadable(f"{self.text!r} has {len(self.free)} unknowns: "
                             f"{sorted(self.free)}")
        return v

    def expr(self) -> tuple:
        v = self.term()
        while self.peek() in (("op", "+"), ("op", "-")):
            op = self.take()[1]
            r = self.term()
            v = p_add(v, r) if op == "+" else p_sub(v, r)
        return v

    def term(self) -> tuple:
        v = self.factor()
        while True:
            kind, s = self.peek()
            if (kind, s) == ("op", "*"):
                self.i += 1
                v = p_mul(v, self.factor())
            elif (kind, s) == ("op", "/"):
                self.i += 1
                v = p_div(v, self.factor())
            elif kind in ("num", "name") or (kind, s) == ("op", "("):
                v = p_mul(v, self.factor())          # 5x, 2(w + 5), (17)(11)x
            else:
                return v

    def factor(self) -> tuple:
        kind, s = self.peek()
        if (kind, s) == ("op", "-"):
            self.i += 1
            return p_neg(self.factor())
        if (kind, s) == ("op", "+"):
            self.i += 1
            return self.factor()
        v = self.atom()
        if self.peek() == ("op", "^"):
            self.i += 1
            kind, s = self.take()
            if kind != "num" or "." in s:
                raise Unreadable(f"{self.text!r} has a power this reader cannot read")
            v = p_pow(v, int(s))
        return v

    def atom(self) -> tuple:
        kind, s = self.take()
        if kind == "num":
            return p_num(Q(s))
        if kind == "name":
            if s in self.env:
                return p_num(self.env[s])
            self.free.add(s)
            return P_VAR
        if (kind, s) == ("op", "("):
            v = self.expr()
            if self.take() != ("op", ")"):
                raise Unreadable(f"{self.text!r} has an unclosed bracket")
            return v
        raise Unreadable(f"{self.text!r} begins {s!r}")


def poly(text: str, env: dict | None = None) -> tuple:
    """A printed expression as a polynomial in its one unknown."""
    return Reader(text, env or {}).parse()


def unknowns(text: str, env: dict | None = None) -> set:
    r = Reader(text, env or {})
    r.parse()
    return r.free


def eq_unknowns(text: str, env: dict | None = None) -> set:
    """The unknowns of a printed equation -- both sides of it."""
    if text.count("=") != 1:
        raise Unreadable(f"{text!r} is not one equation")
    lhs, rhs = text.split("=")
    return unknowns(lhs, env) | unknowns(rhs, env)


def value(text: str, env: dict | None = None) -> Q:
    """A printed expression that comes out a number, given the values it needs."""
    p = poly(text, env)
    if len(p) != 1:
        raise Unreadable(f"{text!r} still contains an unknown")
    return p[0]


def gathered(eq: str, env: dict | None = None) -> tuple:
    """One printed equation as lhs - rhs, everything moved to the left."""
    if eq.count("=") != 1:
        raise Unreadable(f"{eq!r} is not one equation")
    lhs, rhs = eq.split("=")
    env = env or {}
    a, b = Reader(lhs, env), Reader(rhs, env)
    pa, pb = a.parse(), b.parse()
    if len(a.free | b.free) > 1:
        raise Unreadable(f"{eq!r} has {len(a.free | b.free)} unknowns")
    return p_sub(pa, pb)


def solution(eq: str, env: dict | None = None) -> tuple:
    """('one', value), ('none', None) or ('many', None) -- the solution set of a
    printed equation in one unknown, read off the gathered coefficients."""
    d = gathered(eq, env)
    if len(d) > 2:
        raise Unreadable(f"{eq!r} is not linear")
    a = d[1] if len(d) > 1 else Q(0)
    if a != 0:
        return "one", -d[0] / a
    return ("many", None) if d[0] == 0 else ("none", None)


def solved(eq: str, env: dict | None = None) -> Q:
    kind, v = solution(eq, env)
    if kind != "one":
        raise Unreadable(f"{eq!r} has {kind} solutions")
    return v


def could_be(eq: str, env: dict, spare: str | None, want: str) -> bool:
    """Can the equation have the solution set `want` for some value of the one
    constant still left open?

    `identity_constant`'s third shape prints two constants and asks for one of
    them, so the option is right when *some* value of the other constant makes
    the two sides agree. Both sides are affine in that constant, so reading the
    gathered coefficients at two values of it determines them at every value --
    and a third reading checks that affinity rather than assuming it.
    """
    if spare is None:
        return solution(eq, env)[0] == want
    coef = {}
    for g in (Q(0), Q(1), Q(2)):
        d = gathered(eq, {**env, spare: g})
        if len(d) > 2:
            raise Unreadable(f"{eq!r} is not linear")
        coef[g] = (d[1] if len(d) > 1 else Q(0), d[0])
    (a0, b0), (a1, b1), (a2, b2) = coef[Q(0)], coef[Q(1)], coef[Q(2)]
    da, db = a1 - a0, b1 - b0
    if (a0 + 2 * da, b0 + 2 * db) != (a2, b2):
        raise Unreadable(f"{eq!r} is not affine in {spare!r}")
    if want == "many":                      # a(g) = 0 and b(g) = 0 together
        if da:
            g = -a0 / da
            return b0 + db * g == 0
        return a0 == 0 and (db != 0 or b0 == 0)
    if want == "none":                      # a(g) = 0 while b(g) is not
        if da:
            g = -a0 / da
            return b0 + db * g != 0
        return a0 == 0 and (db != 0 or b0 != 0)
    if da or a0 != 0:                       # some g leaves a coefficient standing
        return True
    return False


# ------------------------------------------------------------ the assertion

def keyed(item) -> int:
    return "ABCD".index(item.answer)


def verdict(item, hits: list, what: str) -> str:
    """Both halves. `hits.count(True) == 1` catches the second right answer;
    `hits[keyed]` catches the right answer attached to the wrong letter."""
    if hits.count(True) != 1:
        right = ", ".join(repr(c) for c, h in zip(item.choices, hits) if h)
        raise AssertionError(f"{hits.count(True)} of the four options are right"
                             + (f": {right}" if right else ""))
    if not hits[keyed(item)]:
        raise AssertionError(f"the right option is {item.choices[hits.index(True)]!r}, "
                             f"but the key is {item.choices[keyed(item)]!r}")
    return what


def one_of(patterns: list, text: str):
    for p in patterns:
        m = p.match(text)
        if m:
            return m
    raise Unreadable(f"no reader for {text!r}")


def R(p: str):
    return re.compile(p)


# ------------------------------- solve the printed equation, then evaluate the ask

ASK_FRAMES = [
    R(r"^(?P<eq>.+?) What value of (?P<ask>\w) is the solution to the given equation\?$"),
    R(r"^(?P<eq>.+?) In the equation above, what is the value of (?P<ask>\w) \?$"),
    R(r"^(?P<eq>.+?) What value of (?P<ask>\w) is the solution of the equation above\?$"),
    R(r"^What value of (?P<ask>\w) satisfies the equation (?P<eq>.+)\?$"),
    R(r"^What is the solution to the equation (?P<eq>.+)\?$"),
    R(r"^What value of (?P<ask>\w) is the solution to the equation (?P<eq>.+)\?$"),
    R(r"^For what value of (?P<ask>\w) does (?P<eq>.+) \?$"),
    R(r"^(?P<eq>.+) If (?P<v>\w) is the solution to the equation above, what is the "
      r"value of (?P<ask>.+)\?$"),
    R(r"^If (?P<eq>.+), what is the value of (?P<ask>.+)\?$"),
    R(r"^(?P<eq>.+?) What is the value of (?P<ask>.+)\?$"),
]


def check_asked_value(item) -> str:
    """The equation is printed in the stem, so the answer is not the engine's to
    assert: solve what is on the page and evaluate what the page asks for."""
    m = one_of(ASK_FRAMES, item.stem)
    eq = m.group("eq")
    names = eq_unknowns(eq)
    if len(names) != 1:
        raise Unreadable(f"{eq!r} does not have one unknown")
    var = names.pop()
    x0 = solved(eq)
    ask = m.groupdict().get("ask") or var
    target = value(ask, {var: x0})
    hits = [num(c) == target for c in item.choices]
    return verdict(item, hits, f"{ask} = {target}")


# ------------------------------------------------------- how many solutions

COUNT_STEMS = [R(r"^How many solutions does the equation (?P<eq>.+) have\?$"),
               R(r"^(?P<eq>.+) How many solutions exist to the equation shown above\?$")]
COUNT_WORDS = {"zero": 0, "none": 0, "exactly one": 1, "exactly 1": 1,
               "exactly two": 2, "exactly 2": 2, "exactly three": 3, "exactly 3": 3,
               "infinitely many": "many", "infinitely many solutions": "many"}
TRUTH_COUNT = {"one": 1, "none": 0, "many": "many"}


def claim_count(text: str):
    key = plain(text).strip().rstrip(".").lower()
    if key not in COUNT_WORDS:
        raise Unreadable(f"{text!r} is not a count this reader knows")
    return COUNT_WORDS[key]


def check_count_solutions(item) -> str:
    """Exactly one option names the number of solutions the printed equation has,
    and no two options name the same number."""
    eq = one_of(COUNT_STEMS, item.stem).group("eq")
    said = [claim_count(c) for c in item.choices]
    if len(set(map(str, said))) != 4:
        raise AssertionError(f"two options give the same solution count: {said}")
    want = TRUTH_COUNT[solution(eq)[0]]
    return verdict(item, [s == want for s in said], f"{want} solution(s)")


# ---------------------------------- the constant that fixes the solution set

CONST_STEM = R(r"^(?P<eq>.+) In the given equation, (?P<detail>.+?)\. If the equation "
               r"has (?P<want>infinitely many solutions|no solution), what is the "
               r"value of (?P<letter>\w)\?$")
NAMED = R(r"^(?P<names>.+?) (?:is a constant|are constants)")


def check_constant(item) -> str:
    """Substitute each printed value back into the printed equation and classify
    what comes out. A distractor that also empties the equation -- or also makes
    it an identity -- is a second right answer."""
    m = CONST_STEM.match(item.stem)
    if m is None:
        raise Unreadable(item.stem)
    eq, letter = m.group("eq"), m.group("letter")
    want = "many" if m.group("want").startswith("infinitely") else "none"
    named = NAMED.match(m.group("detail"))
    if named is None:
        raise Unreadable(m.group("detail"))
    others = [n for n in re.findall(r"\b([a-z])\b", named.group("names")) if n != letter]
    if len(others) > 1:
        raise Unreadable(f"{len(others)} constants left open")
    spare = others[0] if others else None
    hits = [could_be(eq, {letter: num(c)}, spare, want) for c in item.choices]
    return verdict(item, hits, f"{want} for one printed value of {letter}")


# ------------------------------------------------ both constants, as a pair

PAIR_STEM = R(r"In the equation above, (?P<a>\w) and (?P<b>\w) are constants\. If the "
              r"equation has (?P<want>infinitely many solutions|no solution), what are "
              r"the values of (?P=a) and (?P=b)\?$")
PAIR = R(r"^(?P<a>\w) = (?P<av>\S+) and (?P<b>\w) = (?P<bv>\S+)$")


def check_pair(item) -> str:
    """Each printed pair goes back into the printed equation; exactly one may
    leave an identity behind."""
    lines = item.stem.split("\n")
    m = PAIR_STEM.search(item.stem)
    if m is None or len(lines) < 2:
        raise Unreadable(item.stem)
    eq = lines[0]
    want = "many" if m.group("want").startswith("infinitely") else "none"
    hits = []
    for c in item.choices:
        p = PAIR.match(plain(c).strip())
        if p is None:
            raise Unreadable(c)
        if {p.group("a"), p.group("b")} != {m.group("a"), m.group("b")}:
            raise Unreadable(f"{c!r} names constants the stem does not")
        env = {p.group("a"): num(p.group("av")), p.group("b"): num(p.group("bv"))}
        hits.append(solution(eq, env)[0] == want)
    return verdict(item, hits, f"{want} for one printed pair")


# ------------------------------------------------ which statements must be true

COND_STEM = R(r"^The equation (?P<lhs>.+?) = (?P<a>\w)\((?P<v>\w) \+ (?P<b>\w)\), where "
              r"(?P=a) and (?P=b) are constants, has no solutions\. Which of the "
              r"following must be true\? (?P<says>.+)$")
COND_LIST = R(r"^I\. (?P<i>.+?) II\. (?P<ii>.+?) III\. (?P<iii>.+)\.$")
COND_SAYS = R(r"^(?P<of>ab|a|b) (?P<rel>=|" + NEQ + r"|!=) (?P<n>\S+)$")
LABEL_SETS = {"I only": {0}, "II only": {1}, "III only": {2},
              "I and II only": {0, 1}, "I and III only": {0, 2},
              "II and III only": {1, 2}, "I, II, and III": {0, 1, 2},
              "None": set(), "None of the above": set()}


def check_conditions(item) -> str:
    """m*v + c = a(v + b) is empty exactly when a = m and ab != c, so a is pinned,
    ab is anything but c, and b is anything but c/m. Each printed statement is
    read against that, and the option that names the true ones must be the key."""
    m = COND_STEM.match(item.stem)
    if m is None:
        raise Unreadable(item.stem)
    var, a_name, b_name = m.group("v"), m.group("a"), m.group("b")
    left = poly(m.group("lhs"))
    if unknowns(m.group("lhs")) != {var}:
        raise AssertionError(f"the two sides are about different unknowns: "
                             f"{m.group('lhs')!r} against {var!r}")
    if len(left) != 2 or left[1] == 0:
        raise Unreadable(f"{m.group('lhs')!r} is not a linear side")
    slope, const = left[1], left[0]
    says = COND_LIST.match(m.group("says"))
    if says is None:
        raise Unreadable(m.group("says"))
    true = []
    for text in (says.group("i"), says.group("ii"), says.group("iii")):
        s = COND_SAYS.match(plain(text).strip())
        if s is None:
            raise Unreadable(text)
        of, rel, n = s.group("of"), s.group("rel"), num(s.group("n"))
        pinned = {a_name: ("is", slope), "ab": ("not", const),
                  b_name: ("not", const / slope)}
        if of not in pinned:
            raise Unreadable(f"{text!r} is about neither constant")
        how, at = pinned[of]
        if how == "is":                       # the quantity can only be `at`
            true.append((n == at) if rel == "=" else (n != at))
        else:                                 # anything but `at`
            true.append(False if rel == "=" else n == at)
    want = {i for i, t in enumerate(true) if t}
    got = []
    for c in item.choices:
        label = plain(c).strip()
        if label not in LABEL_SETS:
            raise Unreadable(f"{c!r} is not a statement set this reader knows")
        got.append(LABEL_SETS[label])
    if len(got) != len({frozenset(g) for g in got}):
        raise AssertionError(f"two options name the same statements: {got}")
    return verdict(item, [g == want for g in got],
                   f"statements {sorted(i + 1 for i in want)} must be true")


# ----------------------------------- the same expression over two denominators

ZERO_STEM = R(r"^If (?P<eq>.+), the value of (?P<inner>.+?) is between which of the "
              r"following pairs of values\?$")
SPAN = R(r"^(?P<lo>\S+) and (?P<hi>\S+)$")


def check_zero_chunk(item) -> str:
    """The equation forces one value for the bracket; exactly one printed range
    may contain it, endpoints included -- a range that ends on the value is a
    second answer a student can argue for."""
    m = ZERO_STEM.match(item.stem)
    if m is None:
        raise Unreadable(item.stem)
    eq = m.group("eq")
    names = eq_unknowns(eq)
    if len(names) != 1:
        raise Unreadable(f"{eq!r} does not have one unknown")
    t = value(m.group("inner"), {names.pop(): solved(eq)})
    spans = []
    for c in item.choices:
        s = SPAN.match(plain(c).strip())
        if s is None:
            raise Unreadable(c)
        spans.append((num(s.group("lo")), num(s.group("hi"))))
    verdict(item, [lo <= t <= hi for lo, hi in spans], "")
    lo, hi = spans[keyed(item)]
    if not lo < t < hi:
        raise AssertionError(f"the keyed range ends on {t}, the value it should contain")
    return f"the bracket is {t}"


# ---------------------------------------------------- an equivalent equation

EQUIV_STEM = R(r"^Which of the following is equivalent to (?P<eq>.+)\?$")


def check_equivalent(item) -> str:
    """Equivalent equations are the ones with the same solution set, so this is
    the template where two options can both be right by definition."""
    m = EQUIV_STEM.match(item.stem)
    if m is None:
        raise Unreadable(item.stem)
    want = solution(m.group("eq"))
    hits = [solution(c) == want for c in item.choices]
    return verdict(item, hits, f"solution set {want[0]}")


# --------------------------------------------- which equation models the words

N = r"[\d,]+(?:\.\d+)?"

MODEL_STEMS = [
    ("phrase", R(rf"^(?P<add>{N}) more than (?P<mult>{N}) times a number (?P<v>\w) is "
                 rf"equal to (?P<total>{N})\. Which equation represents this "
                 rf"situation\?$")),
    ("base_after", R(rf"^The cost to rent .+? from a certain company is \$(?P<base>{N}) "
                     rf"for the first (?P<hrs>{N}) hours and an additional "
                     rf"\$(?P<rate>{N}) per hour for each hour after the first "
                     rf"(?P<hrs2>{N}) hours\. If the total cost to rent .+? from the "
                     rf"company for (?P<v>\w) hours, where (?P=v) > (?P<hrs3>{N}), is "
                     rf"\$(?P<total>{N}), which equation represents this situation\?$")),
    ("fuel", R(rf"^(?P<who>\w+) drives an average of (?P<miles>{N}) miles each week\. "
               rf"(?P=who)'s car can travel an average of (?P<mpg>{N}) miles per gallon "
               rf"of gasoline\. (?P=who) would like to reduce the weekly expenditure on "
               rf"gasoline by \$(?P<cut>{N})\. Assuming gasoline costs \$(?P<cost>{N}) "
               rf"per gallon, which equation can (?P=who) use to determine how many "
               rf"fewer average miles, (?P<v>\w), should be driven each week\?$")),
    ("unit_profit", R(rf"^A certain (?P<thing>.+?) costs a company \$(?P<make>{N}) to "
                      rf"make\. The (?P=thing) is sold by a salesperson who earns a "
                      rf"commission that is equal to (?P<comm>{N})% of the sales price "
                      rf"of the (?P=thing)\. .+? If the sales price of the (?P=thing) is "
                      rf"\$(?P<price>{N}), which of the following equations gives the "
                      rf"number of units, (?P<v>\w), of the (?P=thing) the company sold "
                      rf"to make a profit of \$(?P<total>{N})\?$")),
]

MIX_STEMS = [
    R(rf"^Each side of an? (?P<total>{N})-sided \w+ has one of three lengths\. The "
      rf"number of sides with length {N} centimeters \(cm\) is (?P<mult>{N}) times the "
      rf"number of sides (?P<v>\w) with length {N} cm\. There are (?P<fixed>{N}) sides "
      rf"with length {N} cm\. Which equation must be true for the value of (?P=v)\?$"),
    R(rf"^A (?P<maker>[\w ]+?) makes {N}-inch, {N}-inch, and {N}-inch (?P<thing>.+?)\. "
      rf"During a certain day, the number of {N}-inch (?P=thing) that the (?P=maker) "
      rf"makes is (?P<mult>{N}) times the number (?P<v>\w) of {N}-inch (?P=thing) it "
      rf"makes, and the number of {N}-inch (?P=thing) it makes is (?P<fixed>{N})\. "
      rf"During this day, the (?P=maker) makes (?P<total>{N}) (?P=thing) total\. Which "
      rf"equation represents this situation\?$"),
]


def model_target(stem: str) -> tuple:
    """(variable, the value the words force) for a 'which equation' stem."""
    for shape, pat in MODEL_STEMS:
        m = pat.match(stem)
        if m is None:
            continue
        g = {k: num(v) for k, v in m.groupdict().items()
             if v is not None and k not in ("v", "who", "thing")}
        v = m.group("v")
        if shape == "phrase":
            return v, (g["total"] - g["add"]) / g["mult"]
        if shape == "base_after":
            if not g["hrs"] == g["hrs2"] == g["hrs3"]:
                raise AssertionError("the stem names two different opening periods")
            return v, g["hrs"] + (g["total"] - g["base"]) / g["rate"]
        if shape == "fuel":
            return v, g["cut"] * g["mpg"] / g["cost"]
        each = g["price"] * (1 - g["comm"] / 100) - g["make"]
        if each <= 0:
            raise AssertionError("the stem's product loses money on every unit")
        return v, g["total"] / each
    for pat in MIX_STEMS:
        m = pat.match(stem)
        if m is None:
            continue
        g = {k: num(m.group(k)) for k in ("total", "mult", "fixed")}
        return m.group("v"), (g["total"] - g["fixed"]) / (g["mult"] + 1)
    raise Unreadable(f"no reader for {stem!r}")


def check_model(item) -> str:
    """Two equations that model the same situation are the same equation, however
    differently they print, so each option is decided by solving it -- never by
    comparing its text with the key's."""
    var, target = model_target(item.stem)
    hits = []
    for c in item.choices:
        if eq_unknowns(c) != {var}:
            hits.append(False)
            continue
        hits.append(solution(c) == ("one", target))
    return verdict(item, hits, f"{var} = {target}")


# ------------------------------------------ an expression in terms of a variable

EXPR_STEMS = [
    ("unit_rate", R(rf"^One pound of (?P<thing>.+?) costs \$(?P<price>{N})\. At this "
                    rf"rate, how many dollars will (?P<v>\w) pounds of (?P=thing) "
                    rf"cost\?$")),
    ("more_than_times", R(rf"^(?P<a>\w+) has (?P<v>\w) (?P<thing>.+?)\. (?P<b>\w+) has "
                          rf"(?P<add>{N}) more than (?P<times>twice|{N} times) the "
                          rf"number of (?P=thing) that (?P=a) has\. In terms of (?P=v), "
                          rf"how many (?P=thing) does (?P=b) have\?$")),
    ("perimeter", R(rf"^The width of a rectangular (?P<thing>.+?) is (?P<v>\w) feet\. "
                    rf"The length of the (?P<short>.+?) is (?P<d>{N}) feet longer than "
                    rf"its width\. Which of the following expresses the perimeter, in "
                    rf"feet, of the (?P=thing) in terms of (?P=v)\?$")),
    ("two_kinds", R(rf"^A science teacher is preparing the (?P<n>{N}) stations of a "
                    rf"science laboratory\. .+? Experiment A requires (?P<p>{N}) "
                    rf"(?P<unit>.+?), and Experiment B requires (?P<q>{N}) (?P=unit)\. "
                    rf"If (?P<v>\w) is the number of stations that will be set up for "
                    rf"Experiment A and the remaining stations will be set up for "
                    rf"Experiment B, which of the following expressions represents the "
                    rf"total number of (?P=unit) required\?$")),
]


def check_expression(item) -> str:
    """The option is right when it is the same function of the variable as the
    words describe -- read as a polynomial, so 3n + 6 and 6 + 3n are one answer
    and n^2 + 18 is not."""
    for shape, pat in EXPR_STEMS:
        m = pat.match(item.stem)
        if m is None:
            continue
        v = m.group("v")
        if shape == "unit_rate":
            want = (Q(0), num(m.group("price")))
        elif shape == "more_than_times":
            t = m.group("times")
            mult = Q(2) if t == "twice" else num(t.split()[0])
            want = (num(m.group("add")), mult)
        elif shape == "perimeter":
            want = (2 * num(m.group("d")), Q(4))
        else:
            p, q, n = (num(m.group(k)) for k in ("p", "q", "n"))
            want = (q * n, p - q)
        if want[1] == 0:
            raise Unreadable(f"{item.stem!r} describes no rate to check")
        hits = []
        for c in item.choices:
            try:
                got = poly(c)
            except NotPolynomial:
                hits.append(False)           # 2/c is readable, and is not 2c
                continue
            hits.append(unknowns(c) == {v} and p_trim(list(got)) == p_trim(list(want)))
        return verdict(item, hits, f"the expression {want[1]}{v} + {want[0]}")
    raise Unreadable(f"no reader for {item.stem!r}")


# ------------------------------------------- what one coefficient means in words

GROWTH_STEM = R(rf"^(?P<eq>.+?) A (?P<thing>.+?) had a height of (?P<start>{N}) feet "
                rf"when it was planted\. The equation above can be used to find how "
                rf"many years (?P<v>\w) it took the (?P=thing) to reach a height of "
                rf"(?P<final>{N}) feet\. Which of the following is the best "
                rf"interpretation of the number (?P<n>{N}) in this context\?$")
GROWTH_SAYS = [
    (R(r"^The average number of feet that the (?P<thing>.+?) grew per year$"), "rate"),
    (R(r"^The number of years it took the (?P<thing>.+?) to double its height$"),
     "double"),
    (R(r"^The height, in feet, of the (?P<thing>.+?) when the (?P=thing) was 1 year "
       r"old$"), "at_one"),
    (R(rf"^The average number of years it takes similar (?P<thing>.+?)s to grow "
       rf"(?P<f>{N}) feet$"), "to_grow"),
]

REVENUE_STEM = R(r"^A company that creates and sells (?P<thing>.+?) calculates its "
                 r"monthly profit, in dollars, by subtracting its fixed monthly costs, "
                 r"in dollars, from its monthly sales revenue, in dollars\. The equation "
                 r"(?P<eq>.+?) represents this situation for a month where (?P<v>\w) "
                 r"(?P=thing) are created and sold\. Which statement is the best "
                 r"interpretation of (?P<term>.+?) in this context\?$")
REVENUE_SAYS = [
    (R(r"^The monthly sales revenue, in dollars, from each (?P<one>.+?) sold$"),
     ("revenue", "each")),
    (R(r"^The monthly cost, in dollars, of creating each (?P<one>.+)$"),
     ("cost", "each")),
    (R(r"^The monthly sales revenue, in dollars, from selling (?P<v>\w) (?P<thing>.+)$"),
     ("revenue", "all")),
    (R(r"^The monthly cost, in dollars, of creating (?P<v>\w) (?P<thing>.+)$"),
     ("cost", "all")),
]


def check_interpret(item) -> str:
    """A sentence is a claim about a number, so it can be evaluated. A distractor
    that happens to be a true claim about this model is a second right answer --
    the same shape of defect as a second supported conclusion."""
    m = GROWTH_STEM.match(item.stem)
    if m is not None:
        thing, want = m.group("thing"), num(m.group("n"))
        d = gathered(m.group("eq"))
        if len(d) != 2:
            raise Unreadable(f"{m.group('eq')!r} is not a linear equation")
        rate, start, final = d[1], num(m.group("start")), num(m.group("final"))
        if rate != want:
            raise AssertionError(f"the stem asks about {want}, but the equation's rate "
                                 f"is {rate}")
        if start - final != d[0]:
            raise AssertionError(f"the printed equation does not say {start} feet grows "
                                 f"to {final} feet")
        hits = []
        for c in item.choices:
            said = None
            for pat, kind in GROWTH_SAYS:
                s = pat.match(plain(c).strip())
                if s is None:
                    continue
                if s.group("thing") != thing:
                    raise Unreadable(f"{c!r} is about a {s.group('thing')}")
                said = {"rate": rate, "double": start / rate,
                        "at_one": start + rate}.get(kind)
                if kind == "to_grow":
                    said = num(s.group("f")) / rate
                break
            if said is None:
                raise Unreadable(f"{c!r} is not a claim this reader knows")
            hits.append(said == want)
        return verdict(item, hits, f"the number {want} is the rate")

    m = REVENUE_STEM.match(item.stem)
    if m is None:
        raise Unreadable(f"no reader for {item.stem!r}")
    var, term = m.group("v"), m.group("term")
    lhs, rhs = m.group("eq").split("=")
    rate = poly(term)
    if len(poly(lhs)) != 1:
        raise AssertionError("the profit side of the equation is not a number")
    if len(rate) != 2 or rate[0] != 0 or unknowns(term) != {var}:
        raise AssertionError(f"{term!r} is not a rate times {var}")
    fixed = p_sub(poly(rhs), rate)
    if len(fixed) != 1 or fixed[0] >= 0:
        raise AssertionError(f"the equation does not subtract a fixed cost from {term!r}")
    hits = []
    for c in item.choices:
        said = None
        for pat, kind in REVENUE_SAYS:
            s = pat.match(plain(c).strip())
            if s is None:
                continue
            if "v" in s.groupdict() and s.group("v") != var:
                raise Unreadable(f"{c!r} is about {s.group('v')!r}, not {var!r}")
            said = kind
            break
        if said is None:
            raise Unreadable(f"{c!r} is not a claim this reader knows")
        hits.append(said == ("revenue", "all"))
    return verdict(item, hits, f"{term} is revenue across all {var}")


# ------------------------------------------- two discounts, back to the original

PERCENT_STEM = R(rf"purchased the (?P<street>[\w ]+?) property and received a "
                 rf"(?P<d1>{N})% discount off the original price along with an "
                 rf"additional (?P<d2>{N})% off the discounted price for purchasing the "
                 rf"property in cash\. Which of the following best approximates the "
                 rf"original price, in dollars, of the (?P=street) property\?$")


def check_percent(item) -> str:
    """'Best approximates' is decided by distance, and two options can be equally
    close -- which the gate, comparing only with the key, cannot see."""
    m = PERCENT_STEM.search(item.stem)
    if m is None:
        raise Unreadable(f"no reader for {item.stem!r}")
    rows = [r for r in (item.table or []) if r[0] == m.group("street")]
    if len(rows) != 1:
        raise AssertionError(f"{m.group('street')!r} is not one row of the table")
    paid = num(rows[0][1])
    left = (1 - num(m.group("d1")) / 100) * (1 - num(m.group("d2")) / 100)
    if left <= 0:
        raise AssertionError("the two discounts leave nothing to pay")
    want = paid / left
    gaps = [abs(num(c) - want) for c in item.choices]
    return verdict(item, [g == min(gaps) for g in gaps], f"about {float(want):,.0f}")


# ------------------------------------------------- a sentence to solve outright

CONTEXT_SCENES = [
    ("membership", R(rf"^A (?P<place>[\w ]+) charges its members a onetime "
                     rf"\$(?P<fee>{N}) enrollment fee and a membership fee of "
                     rf"\$(?P<rate>{N}) per "
                     rf"month\. .+? after how many months will a member have been "
                     rf"charged a total of \$(?P<total>{N}) at the (?P=place)\?$"),
     lambda g: (g["total"] - g["fee"]) / g["rate"]),
    ("books", R(rf"^A \w+ has (?P<total>{N}) (?P<thing>\w+) to distribute to a group of "
                rf"children\. If he gives each child (?P<each>{N}) (?P=thing), he will "
                rf"have (?P<left>{N}) (?P=thing) left over\. How many children are in "
                rf"the group\?$"),
     lambda g: (g["total"] - g["left"]) / g["each"]),
    ("coupon", R(rf"^(?P<who>\w+) bought (?P<n>{N}) (?P<thing>[\w ]+) that were each the "
                 rf"same price\. (?P=who) used a coupon for \$(?P<off>{N}) off the "
                 rf"entire purchase\. The cost for the entire purchase after using the "
                 rf"coupon was \$(?P<total>{N})\. What was the original price, in "
                 rf"dollars, for 1 [\w ]+\?$"),
     lambda g: (g["total"] + g["off"]) / g["n"]),
    ("candle", R(rf"^A candle is made of (?P<start>{N}) ounces of wax\. When the candle "
                 rf"is burning, the amount of wax in the candle decreases by 1 ounce "
                 rf"every (?P<hours>{N}) hours\. If (?P<left>{N}) ounces of wax remain "
                 rf"in this candle, for how many hours has it been burning\?$"),
     lambda g: (g["start"] - g["left"]) * g["hours"]),
    ("plant", R(rf"^An agricultural scientist .+? for the next (?P<days>{N}) days\. The "
                rf"scientist found that the height of the plant increased by an average "
                rf"of (?P<rate>{N}) centimeters per day for the (?P<days2>{N}) days\. If "
                rf"the height of the plant on the last day of the study was "
                rf"(?P<total>{N}) centimeters, what was the height, in centimeters, of "
                rf"the \w+ plant at the beginning of the study\?$"),
     lambda g: g["total"] - g["rate"] * g["days"]),
    ("museum", R(rf"^A [\w ]+ rents (?P<thing>[\w ]+) to visitors\. The [\w ]+ earns "
                 rf"revenue of \$(?P<per>{N}) for each [\w ]+ rented for the day\. On "
                 rf"\w+, the [\w ]+ earned \$(?P<profit>{N}) in profit from renting "
                 rf"(?P=thing) after paying daily expenses of \$(?P<costs>{N})\. How "
                 rf"many (?P=thing) did the [\w ]+ rent on \w+\? \(profit = total "
                 rf"revenue - total expenses\)\.$"),
     lambda g: (g["profit"] + g["costs"]) / g["per"]),
    ("overtime", R(rf"^(?P<who>\w+)'s regular wage at her job is p dollars per hour for "
                   rf"the first (?P<base>{N}) hours of work in a day plus (?P<rate>{N}) "
                   rf"times her regular hourly wage for work in excess of (?P<base2>{N}) "
                   rf"hours that day\. On a given day, (?P=who) worked for "
                   rf"(?P<worked>{N}) hours, and her total earnings for that day were "
                   rf"\$(?P<total>{N})\. What is (?P=who)'s regular hourly wage\?$"),
     lambda g: g["total"] / (g["base"] + g["rate"] * (g["worked"] - g["base"]))),
    ("auger", R(rf"^\w+ used a tool called an auger to remove (?P<crop>\w+) from a "
                rf"storage bin at a constant rate\. The bin contained (?P<start>{N}) "
                rf"bushels of (?P=crop) when \w+ began to use the auger\. After "
                rf"(?P<t1>{N}) hours of using the auger, (?P<mid>{N}) bushels of "
                rf"(?P=crop) remained in the bin\. If the auger continues to remove "
                rf"(?P=crop) at this rate, what is the total number of hours \w+ will "
                rf"have been using the auger when (?P<left>{N}) bushels of (?P=crop) "
                rf"remain in the bin\?$"),
     lambda g: (g["start"] - g["left"]) * g["t1"] / (g["start"] - g["mid"])),
    ("flags", R(rf"^A [\w ]+ used a total of (?P<total>{N}) flags that were either "
                rf"(?P<c1>\w+) or (?P<c2>\w+) for [\w ]+\. The \w+ used (?P<one>{N}) "
                rf"(?P=c1) flags\. How many (?P=c2) flags were used\?$"),
     lambda g: g["total"] - g["one"]),
    ("isosceles", R(rf"^The perimeter of an isosceles triangle is (?P<perim>{N}) "
                    rf"inches\. Each of the two congruent sides of the triangle has a "
                    rf"length of "
                    rf"(?P<leg>{N}) inches\. What is the length, in inches, of the third "
                    rf"side\?$"),
     lambda g: g["perim"] - 2 * g["leg"]),
]


def check_context_solve(item) -> str:
    """The sentence, not the engine, says what the answer is."""
    for name, pat, fn in CONTEXT_SCENES:
        m = pat.match(item.stem)
        if m is None:
            continue
        g = {}
        for k, v in m.groupdict().items():
            if v is None or k in ("place", "thing", "who", "crop", "c1", "c2"):
                continue
            g[k] = num(v)
        if name == "plant" and g["days"] != g["days2"]:
            raise AssertionError("the stem names two different study lengths")
        if name == "overtime" and g["base"] != g["base2"]:
            raise AssertionError("the stem names two different regular days")
        want = fn(g)
        return verdict(item, [num(c) == want for c in item.choices], f"{name}: {want}")
    raise Unreadable(f"no reader for {item.stem!r}")


CHECKS = {
    "lin1.solve": check_asked_value,
    "lin1.distribute": check_asked_value,
    "lin1.then_value": check_asked_value,
    "lin1.chunk": check_asked_value,
    "lin1.reciprocal": check_asked_value,
    "lin1.count_solutions": check_count_solutions,
    "lin1.identity_constant": check_constant,
    "lin1.no_solution_constant": check_constant,
    "lin1.identity_pair": check_pair,
    "lin1.no_solution_conditions": check_conditions,
    "lin1.zero_chunk": check_zero_chunk,
    "lin1.equivalent_equation": check_equivalent,
    "lin1.context_solve": check_context_solve,
    "lin1.model_count_mix": check_model,
    "lin1.model_context": check_model,
    "lin1.expression_in_terms": check_expression,
    "lin1.interpret_coefficient": check_interpret,
    "lin1.percent_original": check_percent,
}


# ------------------------------------------------- proving the check bites

def _frac(v: Q) -> str:
    return str(v.numerator) if v.denominator == 1 else f"({v.numerator}/{v.denominator})"


def _same_equation(eq: str, k: int) -> str:
    """The printed equation again, scaled by k: the same mathematics, a string
    that shares almost nothing with the original."""
    d = gathered(eq)
    var = eq_unknowns(eq).pop()
    return f"{_frac(d[1] * k)}{var} = {_frac(-d[0] * k)}"


def _draw(name: str, want=lambda it: True):
    for seed in range(600):
        try:
            item = generate(name, seed)
        except ItemError:
            continue
        if item.fmt == "mcq" and want(item):
            item.choices = list(item.choices)
            return item
    raise RuntimeError(f"no {name} draw to injure")


def selftest() -> int:
    """Seven faults, injected on purpose. A check nobody has seen fail is worth
    nothing, so each has to be reported, and by the right half of the assertion.
    Two of the seven are the defects this check actually found, rebuilt by hand
    now that the generators refuse to draw them."""
    cases = []

    # 1. a second equation that models the situation, printed rearranged --
    #    the defect this topic is most exposed to
    item = _draw("lin1.model_context")
    item.choices[(keyed(item) + 1) % 4] = _same_equation(item.choices[keyed(item)], 1)
    cases.append(("the key rearranged", item, CHECKS["lin1.model_context"]))

    # 2. a second equation equivalent to the given one, this time scaled
    item = _draw("lin1.equivalent_equation")
    item.choices[(keyed(item) + 2) % 4] = _same_equation(item.choices[keyed(item)], 2)
    cases.append(("a second equivalent equation", item,
                  CHECKS["lin1.equivalent_equation"]))

    # 3. a second pair that also makes the equation an identity: the keyed pair
    #    with one value written another way
    item = _draw("lin1.identity_pair")
    key = item.choices[keyed(item)]
    item.choices[(keyed(item) + 1) % 4] = re.sub(r"= (-?\d+) and", r"= \1.0 and", key)
    cases.append(("the key's pair written twice", item, CHECKS["lin1.identity_pair"]))

    # 4. two options that give the same solution count, spelled differently
    item = _draw("lin1.count_solutions",
                 lambda it: "Exactly one" in it.choices)
    spot = (item.choices.index("Exactly one") + 1) % 4
    item.choices[spot] = "Exactly 1"
    cases.append(("one count spelled two ways", item, CHECKS["lin1.count_solutions"]))

    # 5. the right answer attached to the wrong letter
    item = _draw("lin1.interpret_coefficient")
    item.answer = "ABCD"[(keyed(item) + 1) % 4]
    cases.append(("the key moved a letter", item, CHECKS["lin1.interpret_coefficient"]))

    # 6. the found defect, rebuilt: at 4n + 16 = 28 the tree doubles its height
    #    in 16/4 = 4 years, so the distractor describes the number 4 as truly as
    #    the key does
    item = _draw("lin1.interpret_coefficient")
    item.stem = ("4n + 16 = 28 A tree had a height of 16 feet when it was planted. The "
                 "equation above can be used to find how many years n it took the tree "
                 "to reach a height of 28 feet. Which of the following is the best "
                 "interpretation of the number 4 in this context?")
    item.choices = ["The height, in feet, of the tree when the tree was 1 year old",
                    "The average number of years it takes similar trees to grow 28 feet",
                    "The number of years it took the tree to double its height",
                    "The average number of feet that the tree grew per year"]
    item.answer = "D"
    cases.append(("a distractor that is also true of the number", item,
                  CHECKS["lin1.interpret_coefficient"]))

    # 7. the other found defect, rebuilt: 9n + 7n + 4n = 60 and 8n + 36 = 60 are
    #    both true for n = 3
    item = _draw("lin1.model_count_mix")
    item.stem = ("A manufacturing plant makes 9-inch, 7-inch, and 4-inch ceramic tiles. "
                 "During a certain day, the number of 9-inch ceramic tiles that the "
                 "manufacturing plant makes is 7 times the number n of 7-inch ceramic "
                 "tiles it makes, and the number of 4-inch ceramic tiles it makes is 36. "
                 "During this day, the manufacturing plant makes 60 ceramic tiles total. "
                 "Which equation represents this situation?")
    item.choices = ["7n + 36 = 60", "9n + 7n + 4n = 60", "9(7n) + 7n + 4(36) = 60",
                    "8n + 36 = 60"]
    item.answer = "D"
    cases.append(("two equations true for the same n", item,
                  CHECKS["lin1.model_count_mix"]))

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
    """The same assertions over the official option sets, as transcribed."""
    import random

    from satbank.topic import load_topics

    bad = checked = gridins = 0
    for src in load_topics()["linear_equations_in_one_variable"].sources:
        item = src.build(random.Random(0))
        if item.fmt != "mcq":
            gridins += 1
            continue
        # a template prints its shape after the name: lin1.solve.over
        name = ".".join(item.template.split(".")[:2])
        if name not in CHECKS:
            print(f" FAIL  {src.id}: nothing reads {item.template} back")
            bad += 1
            continue
        try:
            CHECKS[name](item)
            checked += 1
        except (AssertionError, Unreadable) as exc:
            bad += 1
            print(f" FAIL  {src.id} ({item.template}): {exc}")
            print(item.pretty())
    print(f"\n{checked} official option sets read back, {gridins} grid-ins skipped"
          + ("" if not bad else f", {bad} with a defect"))
    return 1 if bad else 0


# ------------------------------------------------------------------ driver

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--draws", type=int, default=600,
                    help="seeds to try per template (default 600)")
    ap.add_argument("--template", action="append",
                    help="check only this template; repeatable")
    ap.add_argument("--selftest", action="store_true",
                    help="inject seven faults and show each one caught")
    ap.add_argument("--sources", action="store_true",
                    help="check the official option sets instead of draws")
    ap.add_argument("--all", action="store_true",
                    help="report every defect, not just the first of a kind")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if args.sources:
        return check_sources()

    worst = 0
    for name in args.template or list(CHECKS):
        checker = CHECKS[name]
        made = skipped = bad = 0
        what = ""
        for seed in range(args.draws):
            try:
                item = generate(name, seed)
            except ItemError:
                continue
            if item.fmt != "mcq":
                skipped += 1
                continue
            try:
                what = checker(item)
                made += 1
            except (AssertionError, Unreadable) as exc:
                bad += 1
                if bad == 1 or args.all:
                    print(f"\n{name} seed {seed}: {exc}")
                    print(item.pretty())
        mark = "  ok  " if not bad else " FAIL "
        tail = f", {skipped:,} grid-ins" if skipped else ""
        print(f"{mark} {name:<30} {made:>5,} items, {bad} defects{tail}   ({what})")
        worst |= 1 if bad else 0
    return worst


if __name__ == "__main__":
    sys.exit(main())
