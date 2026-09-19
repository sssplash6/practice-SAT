"""Decide every printed option from the printed page, and check exactly one holds.

`satbank check` only ever asks whether the key is right. It never reads a
*wrong* option as mathematics, and in a topic whose options are sentences
about a margin of error that is the whole risk: "the mean is between 4 and 5"
and "it is plausible that the mean is between 4 and 5" are both true, and an
item offering both reaches a student with no defensible answer while passing
all seven checks.

It is also the only check that can catch the failure this topic's sibling was
rejected for twice -- a template that has been told the answer and an audit
that has been told the same answer agree with each other forever. This script
is told nothing. It reads the **printed stem** for the study (how the units
were chosen, what was estimated, with what margin, and whether the page
states the size of the population), reads the **printed table** and re-adds
it, reads the **four printed sentences**, and applies the rule itself.

    PYTHONPATH=. python3 satbank/topics/sample_statistics_and_margin_of_error/option_check.py
    PYTHONPATH=. python3 .../option_check.py --draws 800 --template sstat.interpret_mean
    PYTHONPATH=. python3 .../option_check.py --selftest   # show the checks can fail

What it takes from the engine: `generate` and `ItemError`. What it takes from
the topic: the scene catalogues, as **vocabulary** -- what this scenario
calls its population, its members and the thing it measured. A page cannot
say that "all largemouth bass in the pond" is a smaller group than "all fish
in the pond"; that is a fact about the world the scenario assumes, of the
same kind as a scatterplot's units. Which sentence a study licenses is
decided here, from the page, every time.

Nothing here imports `study.py`, `claims.py`, `audit.py` or any family
module's logic -- only the scene records that hold the wording.
"""

from __future__ import annotations

import argparse
import re
import sys
from fractions import Fraction as Q

from satbank.item import ItemError
from satbank.registry import generate
from satbank.topics.sample_statistics_and_margin_of_error.families.design import (
    DESIGNS, PLAUSIBLE)
from satbank.topics.sample_statistics_and_margin_of_error.families.estimate import (
    FREQ, GROUP, RANGE, SCALE, TWO_WAY)
from satbank.topics.sample_statistics_and_margin_of_error.world import (
    COUNT_SCENES, MEAN_SCENES, PCT_SCENES, SUBGROUP_SCENES, TABLE_SCENES)

SCENES = {**PCT_SCENES, **MEAN_SCENES, **TABLE_SCENES, **SUBGROUP_SCENES,
          **COUNT_SCENES}


class Unreadable(Exception):
    """The printed item is not something this reader understands.

    Raised, never swallowed. A reader that quietly stops reading reports no
    defects, which prints in exactly the same words as an item that has none.
    """


class Defect(Exception):
    """The printed page has no single defensible answer, or the wrong one."""


def keyed(item) -> str:
    return item.choices["ABCD".index(item.answer)]


# ------------------------------------------------------------ reading numbers

NUM = r"(\d[\d,]*(?:\.\d+)?)"
_NUM = re.compile(r"(?<![\w.])" + NUM)


def Qs(text: str) -> Q:
    return Q(str(text).replace(",", "").replace("%", "").strip())


def nums(text: str) -> list[Q]:
    return [Qs(m) for m in _NUM.findall(text)]


def is_random(stem: str) -> bool:
    """Were the units chosen by the study, or did they choose themselves?"""
    return bool(re.search(r"\b(at random|random sample|randomly|chosen at random)\b",
                          stem, re.I))


def estimate_and_margin(stem: str) -> tuple[Q, Q]:
    """The two numbers the whole subject turns on, off the page.

    The margin is the number the phrase "margin of error" introduces; the
    estimate is the last number printed before that phrase. Every scenario in
    the topic states them in that order, and a stem that does not is refused
    rather than guessed at.
    """
    m = re.search(r"margin of error (?:of|is)\s+" + NUM, stem)
    if not m:
        raise Unreadable("the stem states no margin of error")
    head = stem[:m.start()]
    before = nums(head)
    if not before:
        raise Unreadable("the stem states no estimate before its margin of error")
    return before[-1], Qs(m.group(1))


def stated_population(stem: str) -> Q | None:
    """The size of the population, when the page states one.

    A margin of error is a statement about a percent. It becomes a statement
    about a *number* of members only when the page says how many members
    there are -- which is the only difference between official item 2.7,
    where a count is the answer, and official item 1.4, where a count is a
    distractor. So this is read off the page and never assumed.
    """
    for pat in (r"population of ([\d,]+)", r"total of ([\d,]+)",
                r"bag containing ([\d,]+)", r"crate holding ([\d,]+)",
                r"district has ([\d,]+)", r"A city has ([\d,]+)",
                r"has ([\d,]+) households", r"nursery has ([\d,]+)"):
        m = re.search(pat, stem)
        if m:
            return Qs(m.group(1))
    return None


# ------------------------------------------------------------------ the rule
#
# Written out here for the third time, over sets of this file's own making.
# A set is ("band", lo, hi) with None for an open end, ("only", v),
# ("not", v) or ("outside", lo, hi).

RANK = {"approximate": 0, "plausible": 1, "certain": 2}


def covers(claim, report) -> bool:
    """Does the sentence's assertion cover everything the study leaves open?"""
    k = claim[0]
    if k == "band":
        lo, hi = claim[1], claim[2]
        if report[0] == "band":
            a, b = report[1], report[2]
            return ((lo is None or (a is not None and a >= lo))
                    and (hi is None or (b is not None and b <= hi)))
        if report[0] == "only":
            return ((lo is None or report[1] >= lo)
                    and (hi is None or report[1] <= hi))
    elif k == "only":
        if report[0] == "only":
            return report[1] == claim[1]
        if report[0] == "band":
            return report[1] is not None and report[1] == report[2] == claim[1]
    elif k == "not":
        if report[0] == "only":
            return report[1] != claim[1]
        if report[0] == "band":
            if report[1] is None or report[2] is None:
                return False
            return claim[1] < report[1] or claim[1] > report[2]
    elif k == "outside":
        if report[0] == "only":
            return report[1] < claim[1] or report[1] > claim[2]
        if report[0] == "band":
            if report[2] is not None and report[2] < claim[1]:
                return True
            return report[1] is not None and report[1] > claim[2]
    raise Unreadable(f"cannot compare {claim!r} with {report!r}")


def holds(v, report_set) -> bool:
    """Is the single value `v` one the study leaves plausible?"""
    if report_set[0] == "band":
        lo, hi = report_set[1], report_set[2]
        return (lo is None or v >= lo) and (hi is None or v <= hi)
    if report_set[0] == "only":
        return v == report_set[1]
    raise Unreadable(f"cannot test membership of {report_set!r}")


def study_reports(est: Q, moe: Q | None, random: bool, size: Q | None,
                  percent: bool) -> dict:
    """What the page's study supports. The rule, third writing."""
    out = {("statistic", "sample"): ("certain", ("only", est))}
    if not random:
        return out
    per = Q(1, 100) if percent else Q(1)
    if moe is None:
        out[("parameter", "frame")] = ("approximate", ("only", est))
        if size is not None:
            out[("count", "frame")] = ("approximate", ("only", size * est * per))
        return out
    out[("parameter", "frame")] = ("plausible", ("band", est - moe, est + moe))
    if size is not None:
        out[("count", "frame")] = ("plausible", ("band", (est - moe) * size * per,
                                                 (est + moe) * size * per))
    return out


# -------------------------------------------------------- reading a sentence

def negate(vs):
    k = vs[0]
    if k == "band" and vs[1] is None and vs[2] is not None:
        return ("band", vs[2], None)
    if k == "band" and vs[2] is None and vs[1] is not None:
        return ("band", None, vs[1])
    if k == "band" and vs[1] is not None and vs[2] is not None:
        return ("outside", vs[1], vs[2])
    if k == "only":
        return ("not", vs[1])
    raise Unreadable(f"cannot negate {vs!r}")


def value_set(text: str):
    m = re.search(rf"less than {NUM}[^.]*?or (?:greater|more) than {NUM}", text, re.I)
    if m:
        return ("outside", Qs(m.group(1)), Qs(m.group(2)))
    m = re.search(rf"between {NUM}[^.]*? and {NUM}", text, re.I)
    if m:
        return ("band", Qs(m.group(1)), Qs(m.group(2)))
    m = re.search(rf"(?:greater|more) than {NUM}", text, re.I)
    if m:
        return ("band", Qs(m.group(1)), None)
    m = re.search(rf"(?:less|fewer) than {NUM}", text, re.I)
    if m:
        return ("band", None, Qs(m.group(1)))
    ns = nums(text)
    return ("only", ns[-1]) if ns else None


def read_sentence(sc, text: str):
    """(aspect, population, modality, value set) for one printed option."""
    if "no conclusion can be made" in text:
        return ("no_conclusion", "frame", "plausible", None)
    body = text
    if sc.trait and sc.trait in body:
        body = body.replace(sc.trait, " ")

    if "are not really" in text:
        where = ("misclassification", "sample")
    elif sc.indiv_sample and text.startswith(sc.indiv_sample):
        where = ("individuals", "sample")
    elif sc.indiv and text.startswith(sc.indiv):
        where = ("individuals", "frame")
    elif sc.did and re.search(rf"\b(all|most|any) ({re.escape(sc.members)}|"
                              rf"{re.escape(sc.member)}) {re.escape(sc.did)}\b", text):
        where = ("individuals", "frame")
    elif sc.count_np and sc.count_np in text:
        where = ("count", "frame")
    elif "wider_all" in sc.extra and sc.extra["wider_all"] in text:
        where = ("parameter", "wider")
    else:
        where = ("parameter", "frame")

    neg = False
    if text.startswith("It is not possible that"):
        modality, neg = "certain", True
    elif "doubtful that" in text:
        modality, neg = "plausible", True
    elif re.search(r"\bexactly\b|\bmust\b", text):
        modality = "certain"
    elif re.search(r"\bapproximately\b", text, re.I):
        modality = "approximate"
    else:
        modality = "plausible"

    vs = value_set(body)
    if neg:
        vs = negate(vs)
    return where + (modality, vs)


def sentence_holds(sc, text: str, rep: dict) -> bool:
    aspect, pop, modality, vs = read_sentence(sc, text)
    if aspect == "no_conclusion":
        return ("parameter", "frame") not in rep
    r = rep.get((aspect, pop))
    if r is None:
        return False
    if vs is None:
        raise Unreadable(f"no value in a sentence the study speaks to: {text!r}")
    if RANK[modality] > RANK[r[0]]:
        return False
    return covers(vs, r[1])


# ----------------------------------------------------------------- utilities

def key_is_tight(item, claim, report) -> None:
    """A two-sided interval must be *the* interval, not merely a true one.

    Containment is the right test for "is this sentence supported", and it is
    what catches two defensible answers on one page. It is too kind to the
    key, though: "plausible values are between 32.5% and 43.5%" stays true
    when the stem's margin shrinks, so a rendering bug that widened the
    printed endpoints would pass unnoticed. The stems ask for the *best*
    interpretation, and College Board words it "plausible values ... are
    between L and U" -- naming the plausible values rather than bounding
    them -- so the key's two endpoints have to be the study's own.
    """
    if claim is None or claim[0] != "band" or None in (claim[1], claim[2]):
        return
    if report[0] != "band" or None in (report[1], report[2]):
        return
    if (claim[1], claim[2]) != (report[1], report[2]):
        raise Defect(f"the keyed interval runs from {claim[1]} to {claim[2]}, but "
                     f"the study's own interval runs from {report[1]} to "
                     f"{report[2]}; the key is true but it is not the answer")


def exactly_one(item, hits: list[str], what: str) -> None:
    if len(hits) != 1:
        raise Defect(f"{len(hits)} of the four options {what}: {hits}")
    if hits[0] != keyed(item):
        raise Defect(f"the option that {what} is {hits[0]!r}, but the key is "
                     f"{keyed(item)!r}")


def four_distinct(item) -> None:
    if len(item.choices) != 4 or len(set(item.choices)) != 4:
        raise Defect(f"the page does not print four different options: {item.choices}")
    for c in item.choices:
        if "pi" in c.lower() or "π" in c:
            raise Defect(f"the option {c!r} carries the letters 'pi', which the "
                         f"gate's surface check reads as a pi-bearing option")


def closed_table(item, n: int | None = None, totals: bool = False) -> list[list[int]]:
    """Re-add the printed table, and say what the body of it holds.

    No gate check reads a table as arithmetic. A row that does not add to its
    own total, or a table that does not add to the sample the stem names, is
    a page a student cannot answer, and it is invisible everywhere else.
    """
    if not item.table:
        raise Unreadable("the item prints no table")
    head, *rows = item.table
    body, rtot = [], []
    for row in rows:
        if totals and row[0] == "Total":
            continue
        cells = [int(str(c).replace(",", "")) for c in row[1:]]
        if totals:
            *cells, tot = cells
            if sum(cells) != tot:
                raise Defect(f"the row {row[0]!r} holds {cells} but prints a "
                             f"total of {tot}")
            rtot.append(tot)
        body.append(cells)
    if totals:
        last = [r for r in rows if r[0] == "Total"]
        if len(last) != 1:
            raise Defect("the table prints no Total row")
        printed = [int(str(c).replace(",", "")) for c in last[0][1:]]
        *cols, grand = printed
        for j, c in enumerate(cols):
            if sum(r[j] for r in body) != c:
                raise Defect(f"column {head[j + 1]!r} holds "
                             f"{[r[j] for r in body]} but prints a total of {c}")
        if sum(rtot) != grand or sum(cols) != grand:
            raise Defect(f"the table's margins do not meet at its grand total "
                         f"{grand}")
    if n is not None and sum(sum(r) for r in body) != n:
        raise Defect(f"the table holds {sum(sum(r) for r in body)} units but the "
                     f"stem names a sample of {n}")
    return body


def snap(v: Q, step: Q = Q(1)) -> Q:
    k = v / step
    w = k.numerator // k.denominator
    return (w + (1 if 2 * (k - w) >= 1 else 0)) * step


# ================================================================== the readers

def read_interpret(item) -> None:
    """The three sentence templates about an estimate and its margin."""
    four_distinct(item)
    sc = SCENES[item.params["scene"]]
    est, moe = estimate_and_margin(item.stem)
    size = stated_population(item.stem)
    rep = study_reports(est, moe, is_random(item.stem), size,
                        sc.quantity == "percent")
    hits = [c for c in item.choices if sentence_holds(sc, c, rep)]
    exactly_one(item, hits, "is supported by the study the stem describes")
    aspect, pop, _, vs = read_sentence(sc, hits[0])
    if (aspect, pop) in rep:
        key_is_tight(item, vs, rep[(aspect, pop)][1])


def read_interpret_table(item) -> None:
    """The same, plus the table the stem's estimate was read off."""
    sc = SCENES[item.params["scene"]]
    n = nums(item.stem)[0]
    body = closed_table(item, n=int(n), totals=True)
    rows = [r[0] for r in item.table[1:] if r[0] != "Total"]
    named = [i for i, r in enumerate(rows) if r.lower() in item.stem.lower()]
    if len(named) != 1:
        raise Unreadable(f"the stem names {len(named)} of the table's rows")
    est, _ = estimate_and_margin(item.stem)
    from_table = snap(Q(100 * sum(body[named[0]]), int(n)), Q(1))
    if from_table != est:
        raise Defect(f"the stem says the estimate is {est}% but the table's "
                     f"{rows[named[0]]!r} row is {sum(body[named[0]])} of {int(n)}, "
                     f"which is {from_table}%")
    read_interpret(item)


def read_subgroup(item) -> None:
    """A percent measured on one kind of unit, with no margin of error."""
    four_distinct(item)
    sc = SCENES[item.params["scene"]]
    m = re.search(r"of which " + NUM + "%", item.stem)
    if not m:
        raise Unreadable("the stem does not report a percent of the subgroup")
    est = Qs(m.group(1))
    if re.search(r"margin of error", item.stem):
        raise Unreadable("this reader expects a study with no margin of error")
    rep = study_reports(est, None, is_random(item.stem),
                        stated_population(item.stem), True)
    hits = [c for c in item.choices if sentence_holds(sc, c, rep)]
    exactly_one(item, hits, "is supported by the sample the stem describes")


def read_count_claim(item) -> None:
    """Exactly-so against best-estimate, and the two counts."""
    four_distinct(item)
    ns = nums(item.stem)
    m = re.search(r"If ([\d,]+) ", item.stem)
    if not m or len(ns) < 3:
        raise Unreadable("the stem does not state a sample and a population")
    n, k, size = ns[0], ns[1], Qs(m.group(1))
    if not 0 < k < n or size <= n:
        raise Unreadable("the sample is not a proper part of the population")
    right = size * k / n
    hits = []
    for c in item.choices:
        v = nums(c)[-1]
        certain = bool(re.search(r"\bmust\b|\bexactly\b", c, re.I))
        # one sample estimates the count and cannot settle it
        if v == right and not certain:
            hits.append(c)
    exactly_one(item, hits, "states the count the sample estimates, as an estimate")


def read_scale_count(item) -> None:
    """k of n, scaled up: the key must be the option nearest the estimate."""
    four_distinct(item)
    ns = nums(item.stem)
    if len(ns) != 3:
        raise Unreadable(f"the stem prints {len(ns)} numbers, not three")
    N, n, k = max(ns), sorted(ns)[1], min(ns)
    if not (k < n < N):
        raise Unreadable("the three numbers are not a count, a sample and a population")
    exact = N * k / n
    vals = [Qs(c) for c in item.choices]
    if len(set(vals)) != 4:
        raise Defect(f"two options print the same number: {item.choices}")
    best = min(abs(v - exact) for v in vals)
    near = [c for c, v in zip(item.choices, vals) if abs(v - exact) == best]
    exactly_one(item, near, f"is nearest the estimate {float(exact):.2f}")


def read_scale_group(item) -> None:
    """A percent of one class, scaled to every class."""
    four_distinct(item)
    m = re.search(NUM + r" percent", item.stem)
    g = re.search(r"there are ([\d,]+)|carries ([\d,]+)", item.stem)
    if not m or not g:
        raise Unreadable("the stem does not state a percent and a number of groups")
    pct = Qs(m.group(1))
    groups = Qs(g.group(1) or g.group(2))
    size = nums(item.stem)[0]
    exact = (100 - pct) / 100 * size * groups
    vals = [Qs(c) for c in item.choices]
    best = min(abs(v - exact) for v in vals)
    near = [c for c, v in zip(item.choices, vals) if abs(v - exact) == best]
    exactly_one(item, near, f"is nearest the estimate {float(exact):.1f}")


def read_scale_range(item) -> None:
    """The sample mean scaled up, answered by one of four ranges."""
    four_distinct(item)
    t = re.search(r"is ([\d,]+) acres|has ([\d,]+) shelves", item.stem)
    v = re.search(r"are ((?:[\d,]+, )+and [\d,]+)\.", item.stem)
    if not t or not v:
        raise Unreadable("the stem does not state a total and a list of counts")
    total = Qs(t.group(1) or t.group(2))
    vals = nums(v.group(1))
    est = sum(vals) / len(vals) * total
    inside = []
    for c in item.choices:
        parts = c.split(" to ")
        if len(parts) != 2:
            raise Unreadable(f"the option {c!r} is not a range")
        lo, hi = Qs(parts[0]), Qs(parts[1])
        if lo >= hi:
            raise Defect(f"the range {c!r} runs backwards")
        if lo <= est <= hi:
            inside.append(c)
    exactly_one(item, inside, f"contains the estimate {float(est):.1f}")


def read_scale_two_way(item) -> None:
    """A two-way table of a sample, scaled to the population. Grid-in."""
    n = nums(item.stem)[0]
    body = closed_table(item, n=int(n))
    head = item.table[0][1:]
    named = [j for j, h in enumerate(head) if h.lower() in item.stem.lower()]
    if len(named) != 1:
        raise Unreadable(f"the stem names {len(named)} of the table's columns")
    N = re.search(r"total of ([\d,]+)|has ([\d,]+) employees", item.stem)
    if not N:
        raise Unreadable("the stem does not state the size of the population")
    size = Qs(N.group(1) or N.group(2))
    col = sum(r[named[0]] for r in body)
    want = snap(size * col / n)
    if Qs(item.answer) != want:
        raise Defect(f"the table gives {col} of {int(n)} and the stem a population "
                     f"of {int(size)}, so the estimate is {want}; the item answers "
                     f"{item.answer!r}")


def read_scale_frequency(item) -> None:
    """A frequency table, two groups differenced and scaled. Grid-in."""
    n = nums(item.stem)[0]
    body = closed_table(item, n=int(n))
    rows = [r[0] for r in item.table[1:]]
    cut = "and the number of those who"
    if cut not in item.stem:
        raise Unreadable("the stem does not name two groups to difference")
    first, second = item.stem.split(cut, 1)
    plus = [i for i, r in enumerate(rows) if r.lower() in first.lower()]
    minus = [i for i, r in enumerate(rows) if r.lower() in second.lower()]
    if not plus or not minus or set(plus) & set(minus) or \
            len(plus) + len(minus) != len(rows):
        raise Unreadable(f"the stem sorts the table's rows into {plus} and {minus}")
    P = re.search(r"was ([\d,]+) million|has ([\d,]+) thousand", item.stem)
    if not P:
        raise Unreadable("the stem does not state the size of the population")
    scale = Qs(P.group(1) or P.group(2))
    d = sum(body[i][0] for i in plus) - sum(body[i][0] for i in minus)
    want = snap(Q(d) * scale / n)
    if Qs(item.answer) != want:
        raise Defect(f"the table differences to {d} of {int(n)}, so the estimate is "
                     f"{want}; the item answers {item.answer!r}")


def read_plausible_count(item) -> None:
    """Which count, or which range of counts, the margin leaves open."""
    four_distinct(item)
    est, moe = estimate_and_margin(item.stem)
    size = stated_population(item.stem)
    if size is None:
        raise Unreadable("the stem does not state the size of the population")
    rep = study_reports(est, moe, is_random(item.stem), size, True)
    band = rep[("count", "frame")][1]
    hits, tight = [], {}
    for c in item.choices:
        if re.fullmatch(r"[\d,]+", c):                     # a single count
            if holds(Qs(c), band):
                hits.append(c)
            continue
        m = re.fullmatch(r"([\d,]+) < [a-z] < ([\d,]+)", c)
        if m:
            claim = ("band", Qs(m.group(1)), Qs(m.group(2)))
        else:
            m = re.fullmatch(r"[a-z] ([<>]) ([\d,]+)", c)
            if not m:
                raise Unreadable(f"the option {c!r} is neither a count nor a range")
            claim = (("band", Qs(m.group(2)), None) if m.group(1) == ">"
                     else ("band", None, Qs(m.group(2))))
        if covers(claim, band):
            hits.append(c)
            tight[c] = claim
    exactly_one(item, hits, "the margin of error leaves plausible")
    if hits[0] in tight:
        key_is_tight(item, tight[hits[0]], band)


def read_margin_size(item) -> None:
    """Why one of two samples has the wider margin."""
    four_distinct(item)
    if not item.table or len(item.table) != 3:
        raise Unreadable("the item does not print two samples")
    (a, pa, ma), (b, pb, mb) = ([r[0], Qs(r[1]), Qs(r[2])] for r in item.table[1:])
    for p, m in ((pa, ma), (pb, mb)):
        if not 0 < m < 100 or not 0 < p < 100:
            raise Defect(f"the table prints a percent or a margin outside 0 to 100")
    s = re.search(rf"margin of error for sample ([{a}{b}]) is (greater|less) than "
                  rf"the margin of error for sample ([{a}{b}])", item.stem)
    if not s:
        raise Unreadable("the stem does not compare the two margins")
    first, word, second = s.group(1), s.group(2), s.group(3)
    got = {a: ma, b: mb}
    if (got[first] > got[second]) != (word == "greater"):
        raise Defect(f"the stem says sample {first}'s margin is {word} than sample "
                     f"{second}'s, but the table prints {got[first]} and "
                     f"{got[second]}")
    # the method and the population are fixed by the stem, so the sample size
    # is the only thing left that can move the margin, and it moves it down
    hits = []
    for c in item.choices:
        m = re.fullmatch(rf"Sample ([{a}{b}]) had a (smaller|larger) sample size\.",
                         c)
        if not m:
            continue
        mine, other = (ma, mb) if m.group(1) == a else (mb, ma)
        if (m.group(2) == "smaller") == (mine > other):
            hits.append(c)
    exactly_one(item, hits, "states the sample sizes the two margins imply")


READERS = {
    "sstat.scale_count": (read_scale_count, "the option nearest the estimate"),
    "sstat.scale_group": (read_scale_group, "the option nearest the estimate"),
    "sstat.scale_range": (read_scale_range, "the range holding the estimate"),
    "sstat.scale_two_way": (read_scale_two_way, "the table re-added and scaled"),
    "sstat.scale_frequency": (read_scale_frequency, "the table re-added and scaled"),
    "sstat.interpret_mean": (read_interpret, "every sentence judged from the stem"),
    "sstat.interpret_percent": (read_interpret, "every sentence judged from the stem"),
    "sstat.interpret_table": (read_interpret_table, "the table and every sentence"),
    "sstat.subgroup_claim": (read_subgroup, "every sentence, no margin stated"),
    "sstat.count_claim": (read_count_claim, "estimate against certainty"),
    "sstat.plausible_count": (read_plausible_count, "every count and range"),
    "sstat.margin_size": (read_margin_size, "the stem and the table agreeing"),
}


def sweep(name: str, draws: int):
    made, bad = 0, []
    for seed in range(draws):
        try:
            item = generate(name, seed)
        except ItemError:
            continue
        made += 1
        try:
            READERS[name][0](item)
        except (Defect, Unreadable) as exc:
            bad.append(f"{name} seed {seed}: {type(exc).__name__}: {exc}\n"
                       f"    {item.stem}\n    "
                       + "\n    ".join(f"{'*' if c == keyed(item) else ' '} {c}"
                                       for c in item.choices))
    return made, bad


def sources():
    from satbank.topics.sample_statistics_and_margin_of_error.sources import ALL
    import random
    made, bad = 0, []
    for s in ALL:
        item = s.build(random.Random(0))
        made += 1
        try:
            READERS[item.template][0](item)
        except (Defect, Unreadable) as exc:
            bad.append(f"{s.id}: {type(exc).__name__}: {exc}")
    return made, bad


# ===================================================================== selftest

def _prove(label: str, run) -> bool:
    try:
        run()
    except (Defect, Unreadable, ItemError) as exc:
        print(f"  ok   {label}\n         caught: {str(exc).splitlines()[0][:150]}")
        return True
    except Exception as exc:                                        # noqa: BLE001
        print(f"  FAIL {label}\n         crashed rather than reported: "
              f"{type(exc).__name__}: {exc}")
        return False
    print(f"  FAIL {label}\n         the reader passed an item it should refuse")
    return False


def _rekey(item, pick):
    hits = [i for i, c in enumerate(item.choices) if pick(c)]
    assert len(hits) == 1, f"the fault did not find one option to key: {item.choices}"
    item.answer = "ABCD"[hits[0]]
    return item


def _swap(item, pick, text):
    hits = [i for i, c in enumerate(item.choices) if pick(c)]
    assert len(hits) == 1, f"the fault did not find one option to swap: {item.choices}"
    assert item.choices[hits[0]] != text, "the fault swapped an option for itself"
    item.choices = list(item.choices)
    item.choices[hits[0]] = text
    return item


def _edit(item, old, new):
    assert old in item.stem, f"the fault's splice {old!r} is not in the stem"
    item.stem = item.stem.replace(old, new)
    return item


MENU = dict(ctx="menu", n=300, est=38, moe="11/2",
            options=["point", "greater_est", "interval", "count_from_sample"])
TEXTING = dict(ctx="texting", counts=[[110, 146], [139, 164], [166, 74]], moe=3,
               options=["error_rate", "not_possible_below", "point_upper",
                        "doubtful:35"])


def selftest() -> int:
    """Eighteen injected faults, each one proven caught."""
    ok = True

    # 1 -- the point estimate keyed: the mistake the whole topic is about
    ok &= _prove("an interval item keyed to the point estimate",
                 lambda: read_interpret(_rekey(
                     generate("sstat.interpret_percent", 0, **MENU),
                     lambda c: c.endswith("is 38%."))))

    # 2 -- a second true sentence on the page: a wider interval is also
    #      supported, so the page has two defensible answers
    ok &= _prove("a second true sentence smuggled onto an interval page",
                 lambda: read_interpret(_swap(
                     generate("sstat.interpret_percent", 0, **MENU),
                     lambda c: c.startswith("The percent") and c.endswith("is 38%."),
                     "Plausible values of the percent of the students at the "
                     "school who support a menu change are between 30% and 46%.")))

    # 3 -- the stem's margin shrunk, so the printed interval is still true
    #      but is no longer the study's own interval
    ok &= _prove("an interval wider than the stem's own margin allows",
                 lambda: read_interpret(_edit(
                     generate("sstat.interpret_percent", 0, **MENU),
                     "margin of error of 5.5%", "margin of error of 4.5%")))

    # 3b -- and the other way: an interval narrower than the margin, which
    #       leaves out values the study says are plausible
    ok &= _prove("an interval narrower than the stem's own margin",
                 lambda: read_interpret(_edit(
                     generate("sstat.interpret_percent", 0, **MENU),
                     "margin of error of 5.5%", "margin of error of 6.5%")))

    # 4 -- the sample stops being random and the interval is left keyed
    ok &= _prove("an interval keyed on a sample that selected itself",
                 lambda: read_interpret(_edit(
                     generate("sstat.interpret_percent", 0, **MENU),
                     "300 students were selected at random and were asked in a "
                     "survey",
                     "300 students chose to complete a survey")))

    # 5 -- "it is not possible" keyed: the margin read as a bound
    ok &= _prove("a margin read as a bound and keyed",
                 lambda: read_interpret_table(_rekey(
                     generate("sstat.interpret_table", 0, **TEXTING),
                     lambda c: c.startswith("It is not possible"))))

    # 6 -- one cell of the two-way table bent, so the rows stop adding up
    def bent_row():
        item = generate("sstat.interpret_table", 0, **TEXTING)
        item.table = [list(r) for r in item.table]
        assert item.table[3][1] == "166", item.table[3]
        item.table[3][1] = "160"
        read_interpret_table(item)
    ok &= _prove("a two-way table whose rows stopped adding up", bent_row)

    # 7 -- the table re-added consistently, but no longer the percent the
    #      stem quotes: closure alone would not see this
    def moved_row():
        item = generate("sstat.interpret_table", 0, **TEXTING)
        item.table = [list(r) for r in item.table]
        item.table[3] = ["Heavy", "166", "134", "300"]      # 240 -> 300, closed row
        item.table[2] = ["Medium", "139", "104", "243"]     # give the 60 back
        item.table[4] = ["Total", "415", "384", "799"]
        read_interpret_table(item)
    ok &= _prove("a table that adds up but no longer gives the stem's estimate",
                 moved_row)

    # 8 -- a scaled-up count keyed to the count inside the sample
    ok &= _prove("a scale-up item keyed to the sample's own count",
                 lambda: read_scale_count(_rekey(
                     generate("sstat.scale_count", 0, ctx="council", N=50, n=20,
                              k=6, wrongs=["sample_count", "unpolled",
                                           "rate_as_count"]),
                     lambda c: c == "6")))

    # 9 -- a grid-in whose answer drifted from the table it was read off
    def bent_grid():
        item = generate("sstat.scale_two_way", 0, ctx="mayor", N=6000,
                        counts=[[202, 20], [34, 144]])
        assert item.answer == "3540", item.answer
        item.answer = "3550"
        read_scale_two_way(item)
    ok &= _prove("a grid-in that drifted from its own table", bent_grid)

    # 10 -- a second plausible range on the page
    ok &= _prove("two plausible ranges printed together",
                 lambda: read_plausible_count(_swap(
                     generate("sstat.plausible_count", 0, ctx="beads", N=10_000,
                              est=15, moe=2,
                              wrongs=["above_upper", "margin_to_estimate",
                                      "below_lower"]),
                     lambda c: c == "r < 1,300", "1,200 < r < 1,800")))

    # 11 -- the two margins swapped in the table, the key left alone
    def swapped_margins():
        item = generate("sstat.margin_size", 0, ctx="proposition", pcts=(52, 48),
                        moes=("21/5", "8/5"),
                        wrongs=["fewer_lost", "higher_pct", "larger_n"])
        item.table = [list(r) for r in item.table]
        item.table[1][2], item.table[2][2] = item.table[2][2], item.table[1][2]
        read_margin_size(item)
    ok &= _prove("a margin table swapped under its own stem", swapped_margins)

    # 12 -- the count item keyed to the sentence that insists on the count
    ok &= _prove("an estimated count keyed to the sentence that makes it certain",
                 lambda: read_count_claim(_rekey(
                     generate("sstat.count_claim", 0, ctx="fruit", n=80, k=20,
                              size=1500,
                              options=["must_wrong", "must_right", "best_wrong",
                                       "best_right"]),
                     lambda c: c.startswith("Exactly 375"))))

    print("\n  the engine refusing a wrong answer it was asked for:")
    # these call the generators directly rather than through `generate`, which
    # retries an ItemError sixty times and then reports only that it gave up --
    # what has to be seen here is the reason the engine gave
    import random as _r

    from satbank.topics.sample_statistics_and_margin_of_error.families.design import (
        margin_size, plausible_count)
    from satbank.topics.sample_statistics_and_margin_of_error.families.interpret import (
        interpret_percent, interpret_table)

    # 13 -- ask for a page whose supported sentence has been taken away
    ok &= _prove("a source item whose four options hold nothing",
                 lambda: interpret_percent(_r.Random(0), 0, ctx="characteristic",
                                           est="49/100", moe="1/25",
                                           options=["plausible_below",
                                                    "point_exact",
                                                    "plausible_above", "point"]))

    # 14 -- ask for a page with two supported sentences
    ok &= _prove("a source item asked to print two supported sentences",
                 lambda: interpret_table(_r.Random(0), 0, ctx="texting",
                                         counts=[[110, 146], [139, 164],
                                                 [166, 74]], moe=3,
                                         options=["interval",
                                                  "not_possible_below",
                                                  "point_upper", "doubtful:35"]))

    # 15 -- ask for the licensed range as a wrong answer
    ok &= _prove("a source item asked to print the licensed range as a distractor",
                 lambda: plausible_count(_r.Random(0), 0, ctx="beads", N=10_000,
                                         est=15, moe=2,
                                         wrongs=["interval", "above_upper",
                                                 "below_lower"]))

    # 16 -- ask for the licensed reason as a wrong answer
    ok &= _prove("a source item asked to print the licensed reason as a distractor",
                 lambda: margin_size(_r.Random(0), 0, ctx="proposition",
                                     pcts=(52, 48), moes=("21/5", "8/5"),
                                     wrongs=["smaller_n", "higher_pct",
                                             "larger_n"]))

    # 17 -- a range item keyed to a range the estimate does not fall in
    ok &= _prove("a range item keyed to a range the estimate misses",
                 lambda: read_scale_range(_rekey(
                     generate("sstat.scale_range", 0, ctx="forest", T=253,
                              vals=[51, 59, 45, 52, 73],
                              wrongs=["low", "median", "high"]),
                     lambda c: c == "12,500 to 13,500")))

    # 18 -- the error official item 2.1 exists to test: a statistic measured
    #       on one kind of unit, applied to the whole population
    ok &= _prove("a subgroup statistic keyed to the wider population",
                 lambda: read_subgroup(_rekey(
                     generate("sstat.subgroup_claim", 0, ctx="pond", n=150,
                              est=30,
                              options=["wider_majority", "wider_mean",
                                       "approx_wider", "approx_frame"]),
                     lambda c: c.startswith("Approximately 30% of all fish"))))

    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--draws", type=int, default=400)
    ap.add_argument("--template", default=None)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()

    names = [args.template] if args.template else list(READERS)
    worst = 0
    for name in names:
        made, bad = sweep(name, args.draws)
        note = READERS[name][1]
        print(f"  {'ok ' if not bad else 'FAIL'}  {name:26} {made:5,} items, "
              f"{len(bad)} defects   ({note})")
        for b in bad[:3]:
            print("\n" + b + "\n")
        worst |= 1 if bad else 0
    if not args.template:
        made, bad = sources()
        print(f"  {'ok ' if not bad else 'FAIL'}  {'the official items':26} "
              f"{made:5,} items, {len(bad)} defects   (read the same way)")
        for b in bad:
            print("         - " + b)
        worst |= 1 if bad else 0
    return worst


if __name__ == "__main__":
    sys.exit(main())
