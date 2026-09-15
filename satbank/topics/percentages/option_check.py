"""Read the four printed options back, and check only one of them is right.

`satbank check` asks whether the key is correct. It never asks whether a
*distractor* is also correct: nothing in the engine reads a wrong option as
mathematics. `assemble_text` takes four strings, shuffles them and records which
one is the key; `audit` re-derives the key; `structure` counts surface forms and
`prose` looks for placeholders. An item with two right answers passes every one
of them.

This script closes that hole for the templates whose options are not numbers --
the two that print expressions and the one that prints sentences -- and for the
numeric templates that ask which option is *closest to* a value, where two
options can be equally close and the gate cannot see it.

Every check has the same shape: decide the property for all four options from
their printed text and the printed stem, demand exactly one hit, and demand it
is the keyed one. The readers share nothing with the renderer -- they parse the
strings a student would read -- and `generate` is the only thing imported from
the engine.

    PYTHONPATH=. python3 satbank/topics/percentages/option_check.py
    PYTHONPATH=. python3 .../option_check.py --draws 2000 --template pct.conclusion
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


class Unreadable(Exception):
    """The printed text is not something this reader understands.

    Raised rather than swallowed: an option shape nobody taught this reader
    about is an unchecked option, which is the thing the script exists to stop.
    """


# --------------------------------------------------- printed text -> numbers

def num(text: str) -> Q:
    """A printed number: 5, 0.89, 1.05, 145,800, −3, 12.5%, $4.50."""
    t = (text.replace(MINUS, "-").replace(",", "").replace("$", "")
         .replace("%", "").strip())
    if not t:
        raise Unreadable(f"{text!r} carries no number")
    try:
        if "/" in t:
            a, b = t.split("/", 1)
            return Q(int(a), int(b))
        return Q(t)
    except (ValueError, ZeroDivisionError):
        raise Unreadable(f"{text!r} is not a number") from None


# the five expression shapes these templates print, and nothing else
COEF_VAR = re.compile(r"^(-?[\d.]*)([a-z])$")               # 0.89h, 89h, x
VAR_SHIFT = re.compile(r"^([a-z])\s*([+-])\s*(-?[\d.]+)$")  # h + 0.89, x - 50
POWER = re.compile(r"^\(?(-?[\d.]+)\)?\^([a-z])$")          # 5^x, (0.05)^x
VAR_OVER = re.compile(r"^([a-z])/(-?[\d.]+)$")              # x/5


def expression(text: str):
    """A printed expression in one variable as (variable, f) with f exact.

    The reader knows the shapes an SAT page prints for a percent written
    algebraically and refuses everything else, so a new shape cannot pass
    unexamined.
    """
    t = text.replace(MINUS, "-").strip()
    m = COEF_VAR.match(t)
    if m:
        c = Q(1) if m.group(1) in ("", "-") else num(m.group(1))
        if m.group(1) == "-":
            c = Q(-1)
        var = m.group(2)
        return var, lambda v, c=c: c * v
    m = VAR_SHIFT.match(t)
    if m:
        var, sign, k = m.group(1), m.group(2), num(m.group(3))
        k = k if sign == "+" else -k
        return var, lambda v, k=k: v + k
    m = POWER.match(t)
    if m:
        base, var = num(m.group(1)), m.group(2)
        return var, lambda v, base=base: base ** int(v)
    m = VAR_OVER.match(t)
    if m:
        var, d = m.group(1), num(m.group(2))
        if d == 0:
            raise Unreadable(t)
        return var, lambda v, d=d: v / d
    raise Unreadable(f"{text!r} is not an expression this reader knows")


def equation(text: str):
    """`p = <expression in x>` as (left-hand name, variable, f)."""
    if text.count("=") != 1:
        raise Unreadable(text)
    lhs, rhs = (p.strip() for p in text.split("="))
    var, f = expression(rhs)
    return lhs, var, f


def agrees(f, g, at) -> bool:
    """Two functions that agree at every test value are one function here.

    `at` carries several values on purpose: p = 5x and p = 5^x agree at one
    serving, which is exactly how a one-point check lets a second right answer
    through.
    """
    for v in at:
        try:
            if f(v) != g(v):
                return False
        except (ValueError, OverflowError, ZeroDivisionError):
            return False
    return True


# ------------------------------------------------ the expression templates

PCT_OF = re.compile(r"is ([\d.]+)% of the")
PCT_CHANGE = re.compile(r"(increasing|decreasing) the quantity ([a-z]) by ([\d.]+)%")
WHERE_VAR = re.compile(r"where ([a-z]) (?:is|>)")


def check_expression(item) -> str:
    """One percent of a quantity, written as an expression rather than worked
    out. Exactly one option must be that expression at every value."""
    m = PCT_CHANGE.search(item.stem)
    if m:
        pct = num(m.group(3))
        var = m.group(2)
        r = pct / 100
        truth = (lambda v: (1 + r) * v) if m.group(1) == "increasing" \
            else (lambda v: (1 - r) * v)
        what = "the quantity after the change"
    else:
        m = PCT_OF.search(item.stem)
        w = WHERE_VAR.search(item.stem)
        if m is None or w is None:
            raise Unreadable(item.stem)
        pct, var = num(m.group(1)), w.group(1)
        truth = lambda v, r=pct / 100: r * v                          # noqa: E731
        what = "a percent of the quantity"
    at = [Q(1), Q(2), Q(10), Q(7, 2)]
    hits = []
    for c in item.choices:
        v, f = expression(c)
        hits.append(v == var and agrees(f, truth, at))
    return _verdict(item, hits, what)


DAILY = re.compile(r"which is ([\d.]+)% of the daily allowance")
SERVINGS = re.compile(r"provided by ([a-z]) servings")


def check_per_serving(item) -> str:
    """x servings of a food each worth p% of a daily allowance. Exactly one
    model must give the right percentage for every number of servings."""
    m, s = DAILY.search(item.stem), SERVINGS.search(item.stem)
    if m is None or s is None:
        raise Unreadable(item.stem)
    per, var = num(m.group(1)), s.group(1)
    truth = lambda v, p=per: p * v                                    # noqa: E731
    at = [Q(1), Q(2), Q(3), Q(10)]
    hits = []
    for c in item.choices:
        lhs, v, f = equation(c)
        hits.append(lhs == "p" and v == var and agrees(f, truth, at))
    return _verdict(item, hits, "a model in servings")


# -------------------------------------------------- the sentence template

TURNOUT = re.compile(r"An estimated (\d+)% of the (\w+) voted, and (\d+)% of the votes "
                     r"were cast (.+?)\. (.+?) earned (\d+)% of the votes cast (.+?) and "
                     r"(\d+)% of the votes cast (.+?)\.")


def vote_facts(stem: str) -> dict:
    """The numbers a reader takes off the stem, and the two channels by name."""
    m = TURNOUT.search(stem)
    if m is None:
        raise Unreadable(stem)
    who, use_a, name, use_b = m.group(2), m.group(4), m.group(5), m.group(9)
    turnout, split = Q(int(m.group(1))), Q(int(m.group(3)))
    rate_a, rate_b = Q(int(m.group(6))), Q(int(m.group(8)))
    if m.group(7) != use_a:
        raise AssertionError(f"the stem splits the vote {use_a!r} and then reports a rate "
                             f"for {m.group(7)!r}")
    if use_a == use_b:
        raise AssertionError(f"both rates are reported for {use_a!r}")
    return {"who": who, "name": name, "turnout": turnout, "split": split,
            "use_a": use_a, "rate_a": rate_a, "use_b": use_b, "rate_b": rate_b,
            # what share of the votes actually cast this candidate took
            "overall": split * rate_a / 100 + (100 - split) * rate_b / 100}


def supported(option: str, f: dict) -> bool:
    """Is this printed sentence a conclusion the printed percentages support?

    Five sentence shapes, each decided on its own terms. A sentence that fits
    none of them is `Unreadable` rather than "not supported": an unrecognised
    conclusion is an unchecked conclusion.
    """
    s = option.rstrip(".")
    if "more likely to prefer" in s:
        # a comparison between the two channels: whichever is named first has
        # to be the one with the higher rate among its own voters
        first, second = s.split("more likely to prefer", 1)
        rest = second.split("than were", 1)
        if len(rest) != 2:
            raise Unreadable(option)
        a_first = f["use_a"] in first and f["use_b"] in rest[1]
        b_first = f["use_b"] in first and f["use_a"] in rest[1]
        if not (a_first or b_first):
            raise Unreadable(option)
        return f["rate_a"] > f["rate_b"] if a_first else f["rate_b"] > f["rate_a"]
    if "would have won" in s:
        # both "would have won" sentences are counterfactual: one extends the
        # result to the people who did not vote, the other moves one channel's
        # voters to the other channel. The stem reports rates among the votes
        # actually cast through each channel and says nothing about how anybody
        # else would have voted, so neither follows from it.
        if "had voted" not in s:
            raise Unreadable(option)
        return False
    if "preferred" in s and "More than half of all" in s:
        # the most this data can say about *all* of them: the candidate's share
        # of the votes cast, of the share of people who cast one
        return f["turnout"] * f["overall"] / 100 > 50
    if "likely to be" in s:
        # an attribute of the two groups that nobody collected: age, income,
        # anything. Supported only if the stem carries a figure for it, and it
        # never does.
        claim = s.split("likely to be", 1)[1].split(" than")[0].strip()
        return claim in f["who"] and False
    raise Unreadable(f"{option!r} is a conclusion this reader cannot decide")


def check_conclusion(item) -> str:
    """Percentages of a vote, and which of four sentences they support."""
    f = vote_facts(item.stem)
    if f["overall"] >= 50:
        raise AssertionError(
            f"the stem's own numbers give {f['name']} {float(f['overall'])}% of the votes "
            f"cast, so the premise that {f['name']} did not win does not hold")
    if f["turnout"] > 100 or f["split"] > 100:
        raise AssertionError("a share of more than everybody")
    hits = [supported(c, f) for c in item.choices]
    return _verdict(item, hits, "the one conclusion the percentages support")


# --------------------------------------------- the "closest to" templates
#
# These options are numbers, so no two of them can be equal -- `assemble` drops
# a duplicate value. What it cannot drop is a *tie*: when the value the stem
# describes sits exactly between two of the four printed options, both are
# "closest to" it and the item has two right answers. The exact value is
# recomputed here from the stem's own printed numbers.

TIP = re.compile(r"the tip is ([\d.]+)% of the customer's bill.*bill that is \$([\d,.]+)",
                 re.S)
PROJECT = re.compile(r"approximately ([\d,]+) .*will (increase|decrease) by ([\d.]+)%",
                     re.S)
SHARE_OF = re.compile(r"([\d.]+)% of the items in .* are \w+\. Of all the \w+ items in "
                      r".*?, ([\d.]+)% are also \w+\.(?: Of the \w+ \w+ items, "
                      r"([\d.]+)% are also \w+\.)?", re.S)
NOT_SHARE = re.compile(r"^([\d.]+)% of the items in .* are \w+\. Of those, ([\d.]+)% are "
                       r"also \w+\.(?: Of the \w+ \w+ items, ([\d.]+)% are also \w+\.)?",
                       re.S)


def closest(item, exact: Q) -> str:
    """Exactly one printed option is nearest the value the stem describes."""
    vals = [num(c) for c in item.choices]
    gaps = [abs(v - exact) for v in vals]
    best = min(gaps)
    hits = [g == best for g in gaps]
    if hits.count(True) != 1:
        tied = [item.choices[i] for i, h in enumerate(hits) if h]
        raise AssertionError(f"{len(tied)} options are equally close to {float(exact)}: "
                             f"{tied}")
    return _verdict(item, hits, "the nearest of the four")


def check_rate_closest(item) -> str | None:
    """A tip at a stated rate, asked as "closest to"."""
    m = TIP.search(item.stem)
    if m is None:
        return None                       # another frame of the same template
    return closest(item, num(m.group(1)) * num(m.group(2)) / 100)


def check_projection(item) -> str | None:
    """A population moved by a percent, asked as "closest to"."""
    m = PROJECT.search(item.stem)
    if m is None:
        return None
    n, pct = num(m.group(1)), num(m.group(3))
    sign = 1 if m.group(2) == "increase" else -1
    return closest(item, n * (1 + sign * pct / 100))


def check_compound_share(item) -> str | None:
    """A percent of a percent, asked as "closest to"."""
    if "closest to" not in item.stem:
        return None
    m = SHARE_OF.search(item.stem) or NOT_SHARE.search(item.stem)
    if m is None:
        raise Unreadable(item.stem)
    share = Q(100)
    for g in m.groups():
        if g is not None:
            share = share * num(g) / 100
    if "that are not" in item.stem:
        share = 100 - share
    return closest(item, share)


# ------------------------------------------------- the templates that round
#
# "To the nearest whole percent" and "closest to" both have a right answer only
# while the exact value is nearer one printed option than any other. A value
# that lands exactly halfway between two whole percents is answered by a
# rounding convention the stem never states, and if both neighbours are printed
# the item has two defensible answers. The exact value is recomputed here from
# the table the item prints, not from its parameters.


def cell(text: str) -> Q:
    return num(text)


def table_columns(table) -> tuple[list, list, list]:
    """A printed two-way table as (row labels, column headers, counts)."""
    head = table[0]
    body = [r for r in table[1:] if r[0] != "Total"]
    cols = [c for c in head[1:] if c != "Total"]
    counts = [[cell(r[k + 1]) for k in range(len(cols))] for r in body]
    return [r[0] for r in body], cols, counts


def column_named(cols: list, phrase: str) -> int:
    """The one column whose heading the stem's phrase names."""
    hits = [k for k, c in enumerate(cols) if c.lower() in phrase.lower()]
    if len(hits) != 1:
        raise Unreadable(f"{phrase!r} names {len(hits)} of {cols}")
    return hits[0]


def age_range(label: str) -> tuple[float, float]:
    """`18-35 years old`, `Greater than 65 years old`, `51 years or greater`."""
    ns = [int(n) for n in re.findall(r"\d+", label)]
    if not ns:
        raise Unreadable(label)
    if "greater" in label.lower() or "or more" in label.lower():
        return float(ns[0]), float("inf")
    return float(ns[0]), float(ns[-1])


ROW_SHARE = re.compile(r"to the nearest whole percent, what percent of (.+?) "
                       r"(?:received|responded with|reported) (.+?)\?")
GROUP_DIFF = re.compile(r"difference between the percentage of (.+?) who responded with "
                        r"(.+?) and the percentage of (.+?) who responded", re.S)


def check_table_share(item) -> str | None:
    """A percent read off a printed table, rounded to a whole percent."""
    if item.table is None:
        return None
    m = GROUP_DIFF.search(item.stem)
    if m:
        rows, cols, counts = table_columns(item.table)
        k = column_named(cols, m.group(2))
        wanted = []
        for phrase in (m.group(1), m.group(3)):
            lo, hi = age_range(phrase)
            members = [i for i, r in enumerate(rows)
                       if lo <= age_range(r)[0] and age_range(r)[1] <= hi]
            if not members:
                raise Unreadable(f"no row of {rows} lies inside {phrase!r}")
            wanted.append(members)
        pcts = [100 * sum(counts[i][k] for i in g) / sum(sum(counts[i]) for i in g)
                for g in wanted]
        return _round_and_closest(item, abs(pcts[0] - pcts[1]))
    m = ROW_SHARE.search(item.stem)
    if m:
        rows, cols, counts = table_columns(item.table)
        i = [n for n, r in enumerate(rows) if r in m.group(1)]
        if len(i) != 1:
            raise Unreadable(f"{m.group(1)!r} names {len(i)} of {rows}")
        k = column_named(cols, m.group(2))
        return _round_and_closest(item, 100 * counts[i[0]][k] / sum(counts[i[0]]))
    return None


SHIPMENT = re.compile(r"contains ([\d,]+) \w+, of which ([\d,]+) are")


def check_find_percent(item) -> str | None:
    """A part of a shipment as a percent, rounded to a whole percent."""
    m = SHIPMENT.search(item.stem)
    if m is None or "nearest whole percent" not in item.stem:
        return None
    return _round_and_closest(item, 100 * num(m.group(2)) / num(m.group(1)))


def _round_and_closest(item, exact: Q) -> str:
    """The exact value must not sit halfway between two whole percents, and
    exactly one printed option must be the nearest."""
    if (exact * 2).denominator == 1 and exact.denominator == 2:
        raise AssertionError(f"the exact value is {float(exact)}, halfway between two "
                             f"whole percents: which one is 'nearest' is a convention "
                             f"the stem does not state")
    return closest(item, exact)


CHECKS = {
    "pct.conclusion": check_conclusion,
    "pct.table_share": check_table_share,
    "pct.find_percent": check_find_percent,
    "pct.expression": check_expression,
    "pct.per_serving_model": check_per_serving,
    "pct.of": check_rate_closest,
    "pct.increase_decrease": check_projection,
    "pct.compound_share": check_compound_share,
}


def keyed(item) -> int:
    return "ABCD".index(item.answer)


def _verdict(item, hits, what: str) -> str:
    """Both halves of the assertion: one hit, and the keyed one."""
    if hits.count(True) != 1:
        raise AssertionError(f"{hits.count(True)} of the four options are right: "
                             + ", ".join(f"{c!r}" for c, h in zip(item.choices, hits) if h))
    if not hits[keyed(item)]:
        raise AssertionError(f"the right option is "
                             f"{item.choices[hits.index(True)]!r}, but the key is "
                             f"{item.choices[keyed(item)]!r}")
    return what


# ------------------------------------------------- proving the check bites

def selftest() -> int:
    """Four faults, injected on purpose. A check nobody has seen fail is worth
    nothing, so each has to be reported, by the right half of the assertion."""
    cases = []

    # 1. a second correct expression: the key again, printed with a trailing
    #    zero, so the strings differ and the functions do not
    item = _draw("pct.expression", lambda it: "." in it.choices[keyed(it)])
    item.choices = list(item.choices)
    item.choices[(keyed(item) + 1) % 4] = item.choices[keyed(item)].replace(
        "x", "0x").replace("h", "0h").replace("n", "0n").replace("w", "0w")
    cases.append(("the key again, with a trailing zero", item, CHECKS["pct.expression"]))

    # 2. the right answer attached to the wrong letter
    item = _draw("pct.per_serving_model", lambda it: True)
    item.answer = "ABCD"[(keyed(item) + 1) % 4]
    cases.append(("the key moved a letter", item, CHECKS["pct.per_serving_model"]))

    # 3. a second supported conclusion: the key's comparison said again in
    #    other words, which is the shape a real duplicate would take
    item = _draw("pct.conclusion", lambda it: True)
    key = item.choices[keyed(item)]
    item.choices = list(item.choices)
    item.choices[(keyed(item) + 2) % 4] = ("It is fair to say that " + key[0].lower()
                                           + key[1:])
    cases.append(("the key said twice", item, CHECKS["pct.conclusion"]))

    # 4. a tie: an option moved to sit exactly as far from the exact value as
    #    the key does, on the other side
    def rounded(it):                       # one whose key is not the exact value
        m = PROJECT.search(it.stem)
        return m is not None and num(it.choices[keyed(it)]) != (
            num(m.group(1)) * (1 + num(m.group(3)) / 100))

    item = _draw("pct.increase_decrease", rounded)
    m = PROJECT.search(item.stem)
    exact = num(m.group(1)) * (1 + num(m.group(3)) / 100)
    key = num(item.choices[keyed(item)])
    item.choices = list(item.choices)
    item.choices[(keyed(item) + 1) % 4] = f"{float(2 * exact - key):,.0f}"
    cases.append(("an option tied with the key", item, CHECKS["pct.increase_decrease"]))

    bad = 0
    for what, item, checker in cases:
        try:
            checker(item)
            print(f" FAIL  {what}: not caught")
            bad = 1
        except (AssertionError, Unreadable) as exc:
            print(f"  ok   {what}: {exc}")
    return bad


def _draw(name: str, want):
    for seed in range(400):
        try:
            item = generate(name, seed)
        except ItemError:
            continue
        if item.fmt == "mcq" and want(item):
            return item
    raise RuntimeError(f"no {name} draw to injure")


def check_sources() -> int:
    """The same assertions over the official option sets, as transcribed."""
    import random

    from satbank.topic import load_topics

    bad = checked = 0
    for src in load_topics()["percentages"].sources:
        item = src.build(random.Random(0))
        if item.fmt != "mcq" or item.template not in CHECKS:
            continue
        try:
            if CHECKS[item.template](item) is not None:
                checked += 1
        except (AssertionError, Unreadable) as exc:
            bad += 1
            print(f" FAIL  {src.id} ({item.template}): {exc}")
            print(item.pretty())
    print(f"\n{checked} official option sets read back"
          + ("" if not bad else f", {bad} with two right answers"))
    return 1 if bad else 0


# ------------------------------------------------------------------ driver

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--draws", type=int, default=600,
                    help="seeds to try per template (default 600)")
    ap.add_argument("--template", action="append",
                    help="check only this template; repeatable")
    ap.add_argument("--selftest", action="store_true",
                    help="inject four faults and show each one caught")
    ap.add_argument("--sources", action="store_true",
                    help="check the official option sets instead of draws")
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
                continue
            try:
                got = checker(item)
            except (AssertionError, Unreadable) as exc:
                bad += 1
                if bad == 1:
                    print(f"\n{name} seed {seed}: {exc}")
                    print(item.pretty())
                continue
            if got is None:
                skipped += 1
            else:
                made += 1
                what = got
        mark = "  ok  " if not bad else " FAIL "
        tail = f", {skipped:,} not asked this way" if skipped else ""
        print(f"{mark} {name:<24} {made:>5,} items, {bad} defects{tail}   ({what})")
        worst |= 1 if bad else 0
    return worst


if __name__ == "__main__":
    sys.exit(main())
