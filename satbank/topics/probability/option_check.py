#!/usr/bin/env python3
"""Decide every printed option from the printed page.

The gate only ever asks whether the key is right. It never reads a *wrong*
option as mathematics, so an item with two correct options passes all seven
checks and reaches a student as a question with no defensible answer. This
file closes that hole for Probability, and it closes a second one the gate
cannot see at all: **a printed table that does not add up**. A table whose
rows and columns disagree with their own margins is a question nobody can
answer, and no check in `satbank/` reads a table as arithmetic.

What it does, and what it is allowed to look at
-----------------------------------------------

`item.params` is never read. Not once -- `grep params option_check.py` returns
nothing but this sentence. Everything below comes from what the page shows:
`item.table` (the printed rows, including the printed margins), `item.stem`,
`item.choices` and `item.answer`.

1. **Closure.** The printed table is added up again from its own interior
   cells: every row must reach its printed row total, every column its printed
   column total, and the two margins must meet at the printed grand total. A
   column of percentages must reach the 100% it prints.

2. **The question.** The last sentence of the stem is parsed into an *event*
   clause and, where there is one, a *condition* clause. Each clause is then
   matched against the table's **printed labels** -- not against any phrase
   this topic's `world.py` holds -- by stemmed token containment, with a
   numeric reading for interval labels so that "at least 10 years of age"
   resolves to the columns 10-19 years and 20+ years. A label whose tokens are
   a proper subset of another matched label's is dropped, which is what keeps
   "Has bicycle paths" from being read out of "does not have bicycle paths".

3. **Every option.** Each printed option is parsed to an exact `Fraction`
   (12/16, 1/4, 0.40, 13.3%, or a count) and compared with the value the cells
   give. Exactly one option must be correct and it must be the keyed one. For
   a stem that says *closest*, the keyed option must be strictly nearer the
   exact value than every other -- rounding the key correctly is not the same
   thing, because the student compares against the four numbers on the page.

4. **Grid-ins.** The printed answer is recomputed from the page and must also
   fit the digital SAT's five characters.

Independence, and how far it goes
---------------------------------

The reader shares no function with any template. It re-implements the table
arithmetic, the rounding, the option parsing and the reading of the question.
The one thing it takes from `world.py` is the list of scenarios, and only in
`--selftest`, to prove that every scenario's English resolves to the
categories it names -- which is a test *of* `world.py`, not a use of it.

Run it:

    python3 satbank/topics/probability/option_check.py            # a volume sweep
    python3 satbank/topics/probability/option_check.py --selftest # the fault proofs
"""

from __future__ import annotations

import argparse
import math
import os
import re
import sys
from fractions import Fraction as Q

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))

from satbank.exact import MINUS
from satbank.item import ItemError                                  # noqa: E402
from satbank.registry import generate                               # noqa: E402
from satbank.topic import load_topics                               # noqa: E402

LETTERS = "ABCD"
GRID_CHARS = 5


# ------------------------------------------------------------------- words

_IRREGULAR = {"has": "have", "have": "have", "having": "have", "had": "have",
              "do": "do", "does": "do", "did": "do", "doing": "do",
              "is": "be", "are": "be", "was": "be", "were": "be", "be": "be",
              "been": "be", "am": "be", "men": "man", "women": "woman",
              "people": "person", "an": "a", "the": "the",
              # a printed label negates with "No", a sentence with "not"; they
              # are one token here, or "No state income tax" gets read out of
              # "does not have a state-level income tax", the opposite row
              "no": "not", "not": "not", "none": "not"}


def stem_word(w: str) -> str:
    """One spelling for the morphological variants this topic actually uses.

    Crude on purpose, and exact where it matters: both the printed label and
    the sentence go through it, so what counts is that "purchased"/"purchase",
    "males"/"male" and "maples"/"maple" land on the same token, not that the
    token is a real word. The trailing "e" comes off last, because "purchased"
    loses a "d" and "maples" an "s" and the two rules must not disagree.
    """
    if w in _IRREGULAR:
        return _IRREGULAR[w]
    if w.endswith("ies") and len(w) > 4:
        w = w[:-3] + "y"
    elif w.endswith("ing") and len(w) > 5:
        w = w[:-3]
    elif w.endswith("ed") and len(w) > 4:
        w = w[:-2]
    elif w.endswith("es") and len(w) > 4:
        w = w[:-2]
    elif w.endswith("s") and not w.endswith("ss") and len(w) > 3:
        w = w[:-1]
    return w.rstrip("e") if len(w) > 3 else w


def tokens(text: str) -> list[str]:
    """A phrase as a list of stemmed tokens, in order.

    Nothing is discarded as a stop word: "not", "no" and a bare "a" are
    exactly the tokens that tell two printed labels apart, and a filter that
    drops them makes the reader agree with the wrong column without
    complaining.
    """
    t = str(text).replace(",", "").replace(MINUS, "-")
    t = re.sub(r"[\u2013\u2014/\-]", " ", t)
    # A one-character token keeps its case. "Group A" and "Site B" are labels
    # whose whole identity is that letter, and lower-casing them makes the
    # article in "a flower from site B" match the column Site A. Everything
    # longer is folded, because nothing else depends on case.
    return [w if len(w) == 1 and w.isalpha() else stem_word(w.lower())
            for w in re.findall(r"[A-Za-z0-9$+]+", t)]


def words(text: str) -> set[str]:
    return set(tokens(text))


# "Number of weekdays" is a column heading, not a sentence, and the prose that
# names it never says "number of". These are dropped from the LABEL only; a
# clause keeps every word it has, so nothing the stem says is thrown away.
LABEL_NOISE = {"number", "of", "the", "total"}


def label_words(label: str) -> set[str]:
    return {w for w in tokens(label) if w not in LABEL_NOISE}


def label_tokens(label: str) -> list[str]:
    return [w for w in tokens(label) if w not in LABEL_NOISE]


# ---------------------------------------------------------------- intervals

INF = math.inf


def label_span(label: str):
    """A printed label read as a range of numbers, or None."""
    t = label.replace(",", "")
    m = re.search(r"(\d+)\s*[–—-]\s*(\d+)", t)
    if m:
        return float(m.group(1)), float(m.group(2))
    m = re.search(r"(\d+)\s*\+", t)
    if m:
        return float(m.group(1)), INF
    m = re.fullmatch(r"\s*(\d+)\s*[A-Za-z]*\s*", t)
    if m:
        return float(m.group(1)), float(m.group(1))
    return None


COMPARE = [
    (r"\bat least (\d[\d,]*)", lambda n: (n, INF)),
    (r"\b(\d[\d,]*) or more\b", lambda n: (n, INF)),
    (r"\bat or above (\d[\d,]*)", lambda n: (n, INF)),
    (r"\bmore than (\d[\d,]*)", lambda n: (n + 1e-9, INF)),
    (r"\bgreater than (\d[\d,]*)", lambda n: (n + 1e-9, INF)),
    (r"\bafter (\d[\d,]*)", lambda n: (n + 1e-9, INF)),
    (r"\bless than (\d[\d,]*)", lambda n: (-INF, n - 1e-9)),
    (r"\bunder (\d[\d,]*)", lambda n: (-INF, n - 1e-9)),
    (r"\bbelow (\d[\d,]*)", lambda n: (-INF, n - 1e-9)),
    (r"\bbefore (\d[\d,]*)", lambda n: (-INF, n - 1e-9)),
    (r"\bno more than (\d[\d,]*)", lambda n: (-INF, n)),
    (r"\bat most (\d[\d,]*)", lambda n: (-INF, n)),
]
RANGE = re.compile(r"\bfrom (\d[\d,]*) to (\d[\d,]*)|\bbetween (\d[\d,]*) and "
                   r"(\d[\d,]*)")


def clause_span(clause: str):
    """A clause read as a comparison, or None. "at least 10 years" -> [10, inf)."""
    m = RANGE.search(clause)
    if m:
        a, b = (m.group(1), m.group(2)) if m.group(1) else (m.group(3), m.group(4))
        return float(a.replace(",", "")), float(b.replace(",", ""))
    for pat, make in COMPARE:
        m = re.search(pat, clause, re.I)
        if m:
            return make(float(m.group(1).replace(",", "")))
    return None


# ------------------------------------------------------------ label matching

def match_labels(clause: str, labels: list[str]) -> tuple[int, ...]:
    """Which printed labels the clause names, read off the clause alone.

    Three readings, in order, and the first that finds anything wins.

    1. **A comparison over interval labels.** "at least 10 years of age" is
       not a label and never will be; it is a cut through the columns
       0-9 years, 10-19 years and 20+ years, and it names the two whose
       ranges lie inside it. Tried first, because "before 2010" contains the
       token 2010 and would otherwise be read as the 2010 column itself.
    2. **Containment.** Every token of the label appears somewhere in the
       clause, in any order, which is what matches the row "Gasoline not
       purchased" to "did not purchase gasoline", and a one-character token
       keeps its case so that the article in "a flower from site B" is not
       read as the column Site A.

    A label whose tokens are a proper subset of another matched label's is
    then dropped: "Has bicycle paths" sits inside "does not have bicycle
    paths" and is not what that clause means.
    """
    span = clause_span(clause)
    spans = [label_span(lab) for lab in labels]
    # the numeric reading applies only to an axis that is *entirely* intervals.
    # "1 visit" reads as the number 1, so "less than 40 years old" was matching
    # the visits column of a table whose ages are rows -- a cut through an axis
    # that is not ordered at all.
    if span is not None and len(labels) > 1 and all(t is not None for t in spans):
        lo, hi = span
        out = [i for i, t in enumerate(spans) if lo <= t[0] and t[1] <= hi]
        if out:
            return tuple(out)
    cw = words(clause)
    hit = [(i, label_words(lab)) for i, lab in enumerate(labels)
           if lab.strip() and label_words(lab) and label_words(lab) <= cw]
    return tuple(sorted(i for i, w in hit
                        if not any(w < w2 for j, w2 in hit if j != i)))


# --------------------------------------------------------------- the table

def cell_value(text: str):
    t = str(text).replace(",", "").replace("%", "").strip()
    try:
        return int(t)
    except ValueError:
        return None


class Printed:
    """A two-way table as the page prints it, re-added from its own cells."""

    def __init__(self, rows):
        head = rows[0]
        self.margins = head[-1].strip() == "Total" and rows[-1][0].strip() == "Total"
        body = rows[1:-1] if self.margins else rows[1:]
        self.col_labels = [c for c in (head[1:-1] if self.margins else head[1:])]
        self.row_labels = [r[0] for r in body]
        self.cells = [[cell_value(v) for v in r[1:1 + len(self.col_labels)]]
                      for r in body]
        self.row_total = ([cell_value(r[-1]) for r in body] if self.margins
                          else None)
        self.col_total = ([cell_value(v) for v in rows[-1][1:-1]] if self.margins
                          else None)
        self.grand = cell_value(rows[-1][-1]) if self.margins else None
        self.hidden = [(i, j) for i, r in enumerate(self.cells)
                       for j, v in enumerate(r) if v is None]

    @property
    def nr(self):
        return len(self.cells)

    @property
    def nc(self):
        return len(self.col_labels)

    def total(self) -> int:
        return sum(v for r in self.cells for v in r if v is not None)

    def count(self, rows, cols) -> int:
        rows = range(self.nr) if rows is None else rows
        cols = range(self.nc) if cols is None else cols
        return sum(self.cells[i][j] for i in rows for j in cols)

    def closure(self) -> list[str]:
        """Add the printed table up again. A margin that is not the sum of the
        cells it stands at the end of is a defect the gate cannot see."""
        bad = []
        if self.hidden:
            return bad                      # a cell printed as x or ? is the question
        if not self.margins:
            return bad
        for i, r in enumerate(self.cells):
            if sum(r) != self.row_total[i]:
                bad.append(f"row {self.row_labels[i]!r} holds {r} summing to "
                           f"{sum(r)}, but its printed total is {self.row_total[i]}")
        for j in range(self.nc):
            col = [self.cells[i][j] for i in range(self.nr)]
            if sum(col) != self.col_total[j]:
                bad.append(f"column {self.col_labels[j]!r} holds {col} summing to "
                           f"{sum(col)}, but its printed total is "
                           f"{self.col_total[j]}")
        if sum(self.row_total) != self.grand:
            bad.append(f"the row totals {self.row_total} sum to "
                       f"{sum(self.row_total)}, not to the printed grand total "
                       f"{self.grand}")
        if sum(self.col_total) != self.grand:
            bad.append(f"the column totals {self.col_total} sum to "
                       f"{sum(self.col_total)}, not to the printed grand total "
                       f"{self.grand}")
        return bad


class OneWay:
    """A frequency table: one label column, one count column, maybe a total."""

    def __init__(self, rows):
        body = rows[1:]
        self.total_row = body and body[-1][0].strip() == "Total"
        self.printed_total = cell_value(body[-1][1]) if self.total_row else None
        if self.total_row:
            body = body[:-1]
        self.labels = [r[0] for r in body]
        self.counts = [cell_value(r[1]) for r in body]

    def closure(self) -> list[str]:
        if self.total_row and sum(self.counts) != self.printed_total:
            return [f"the counts {self.counts} sum to {sum(self.counts)}, not to the "
                    f"printed total {self.printed_total}"]
        return []


# ---------------------------------------------------------------- options

NUM = re.compile(r"^\s*[−-]?\s*[\d,]+(?:\.\d+)?\s*%?\s*$")


def option_value(text: str):
    """A printed option as an exact rational, or None when it is words."""
    t = str(text).strip().replace(",", "").replace("−", "-")
    pct = t.endswith("%")
    t = t[:-1] if pct else t
    if "/" in t:
        a, b = t.split("/", 1)
        try:
            v = Q(a) / Q(b)
        except (ValueError, ZeroDivisionError):
            return None
    else:
        try:
            v = Q(t)
        except ValueError:
            return None
    return v / 100 if pct else v


def decimals(text: str) -> int:
    t = str(text).rstrip("%")
    return len(t.split(".")[1]) if "." in t else 0


def half_up(v: Q, step: Q) -> Q:
    k = v / step
    n = k.numerator // k.denominator
    return (n + 1 if (k - n) * 2 >= 1 else n) * step


# ------------------------------------------------------- reading the question

QMARK = re.compile(r"\s*\(Express your answer.*?\)\s*$", re.I)


def question(stem: str) -> str:
    """The sentence that asks, which is the last one on the page."""
    text = QMARK.sub("", stem.replace("\n", " ")).strip()
    parts = re.split(r"(?<=[.?])\s+(?=[A-Z])", text)
    return parts[-1].strip()


ASK = r"(?:what is the probability|which of the following is closest to the probability)"
FRAMES = [
    ("select_cond", re.compile(r"^If one of the (?P<cond>.+?) is selected at random, "
                               + ASK + r" that (?:the )?\S+ (?P<ev>.+)\?$", re.I)),
    ("given", re.compile(r"^.*?" + ASK + r" of selecting (?P<ev>.+?), given that "
                         r"(?:the )?\S+ (?P<cond>.+)\?$", re.I)),
    ("if_cond", re.compile(r"^If (?:the |a |an )?\S+(?: \S+)? (?P<cond>.+?), " + ASK
                           + r" that (?:the )?\S+ (?P<ev>.+)\?$", re.I)),
    ("of_the", re.compile(r"^Of the (?P<cond>.+?), what fraction (?P<ev>.+)\?$", re.I)),
    ("split_fraction", re.compile(r"^What fraction of the (?P<rest>.+)\?$", re.I)),
    ("split_percent", re.compile(r"^.*?what percent of (?P<rest>.+)\?$", re.I)),
    ("plain", re.compile(r"^.*?" + ASK + r" (?:that|of selecting) (?P<ev>.+)\?$",
                         re.I)),
]


class Unreadable(Exception):
    """The reader could not find the question on the page.

    Raised, never swallowed. A reader that quietly skips what it cannot parse
    reports "0 defects" in the same words as one that checked everything.
    """


def read_question(stem: str, rows: list[str], cols: list[str]):
    """(event rows, event cols, condition rows, condition cols), from the page."""
    qs = question(stem)
    why = []
    for name, pat in FRAMES:
        m = pat.match(qs)
        if not m:
            continue
        try:
            if name in ("split_fraction", "split_percent"):
                return split_two(m.group("rest"), rows, cols)
            ev, cond = m.group("ev"), m.groupdict().get("cond")
            e = sets_in(ev, rows, cols)
            c = sets_in(cond, rows, cols) if cond else ((), ())
            if e == ((), ()):
                raise Unreadable(f"{name}: no printed label is named in {ev!r}")
            if cond and c == ((), ()):
                raise Unreadable(f"{name}: no printed label is named in {cond!r}")
            if cond and _axis(e) is not None and _axis(e) == _axis(c):
                raise Unreadable(f"{name}: the event and the condition read as the "
                                 f"same axis")
            return e[0] or None, e[1] or None, c[0] or None, c[1] or None
        except Unreadable as exc:
            # the sentence fits this frame's punctuation but not its meaning --
            # "If one of these teens surveyed is selected at random" has the
            # shape of a condition and names no column. Keep looking; only a
            # page that fits no frame at all is unreadable.
            why.append(str(exc))
    raise Unreadable(f"no question frame reads {qs!r} ({'; '.join(why) or 'no match'})")


def _axis(pair):
    if pair[0] and not pair[1]:
        return "row"
    if pair[1] and not pair[0]:
        return "col"
    return None


JOIN = re.compile(r"\s+(?:and|but)\s+")


def sets_in(clause: str, rows: list[str], cols: list[str]):
    """The rows and the columns a clause names.

    A joint question names one of each, joined by "and" or "but", and the two
    halves leak into one another: "did not purchase gasoline and purchased a
    beverage" contains every token of the column "Beverage not purchased"
    although it says the opposite. So a conjunction is split first, and the
    split is accepted only when one half is purely a row and the other purely
    a column -- which is what a joint question is. A union written with "and"
    ("medium and heavy texters") fails that test and falls through to the
    whole clause, where it belongs.
    """
    for m in JOIN.finditer(clause):
        left, right = clause[:m.start()], clause[m.end():]
        lr, lc = match_labels(left, rows), match_labels(left, cols)
        rr, rc = match_labels(right, rows), match_labels(right, cols)
        if lr and not lc and rc and not rr:
            return lr, rc
        if lc and not lr and rr and not rc:
            return rr, lc
    return match_labels(clause, rows), match_labels(clause, cols)


def split_two(rest: str, rows: list[str], cols: list[str]):
    """"...states that have a state-level sales tax do not have a ... income tax"

    Two clauses run together with no punctuation between them, so every split
    point is tried and the one that names exactly one set on each axis wins.
    The first half is the condition: that is what "what fraction of X Y" means.
    """
    toks = rest.split()
    best = None
    for k in range(1, len(toks)):
        left, right = " ".join(toks[:k]), " ".join(toks[k:])
        lr, lc = sets_in(left, rows, cols)
        rr, rc = sets_in(right, rows, cols)
        for cond, ev in (((lr, ()), ((), rc)), (((), lc), (rr, ()))):
            if not (cond[0] or cond[1]) or not (ev[0] or ev[1]):
                continue
            score = len(words(left)) + len(words(right))
            if best is None or score > best[0]:
                best = (score, ev, cond)
    if best is None:
        raise Unreadable(f"cannot split {rest!r} into a condition and an event")
    _, ev, cond = best
    return ev[0] or None, ev[1] or None, cond[0] or None, cond[1] or None


def meet(a, b):
    if a is None:
        return b
    if b is None:
        return a
    return tuple(i for i in a if i in b)


# ------------------------------------------------------------- the verdict

def judge(item, exact: Q, note="") -> list[str]:
    """Decide every printed option against the value the page gives."""
    bad = []
    if item.fmt == "spr":
        got = option_value(item.answer)
        if got is None:
            return [f"the grid-in answer {item.answer!r} is not a number"]
        if got != exact:
            bad.append(f"the page gives {exact} but the grid-in answer reads "
                       f"{item.answer!r} ({got})")
        if len(item.answer) > GRID_CHARS:
            bad.append(f"the grid-in answer {item.answer!r} needs "
                       f"{len(item.answer)} characters, more than the {GRID_CHARS} "
                       f"the field holds")
        return bad

    vals = [option_value(c) for c in item.choices]
    if any(v is None for v in vals):
        return [f"an option is not a number: {item.choices}"]
    if len(set(vals)) != 4:
        bad.append(f"two options have the same value: {item.choices}")
    ki = LETTERS.index(item.answer)

    if re.search(r"\bclosest\b|\bapproximately\b|\bnearest\b", item.stem, re.I) \
            and "%" not in item.choices[ki]:
        gaps = [abs(v - exact) for v in vals]
        best = min(gaps)
        near = [i for i, g in enumerate(gaps) if g == best]
        if len(near) != 1:
            bad.append(f"options {[item.choices[i] for i in near]} are equally close "
                       f"to the exact value {exact}, so the page has no single "
                       f"closest answer")
        elif near[0] != ki:
            bad.append(f"the exact value {exact} is closest to "
                       f"{item.choices[near[0]]!r}, but {item.choices[ki]!r} is keyed")
        return bad

    kt = item.choices[ki]
    if "%" in kt:
        step = Q(1, 10 ** decimals(kt))
        scaled = exact * 100
        if (scaled / step - (scaled / step).numerator // (scaled / step).denominator) \
                * 2 == 1:
            bad.append(f"{scaled}% sits exactly halfway between two printable "
                       f"percents, so which is nearest is a convention")
        target = half_up(scaled, step) / 100
    elif "." in kt:
        target = exact                      # an exact decimal; the stem promised one
    else:
        target = exact

    right = [i for i, v in enumerate(vals) if v == target]
    if len(right) != 1:
        bad.append(f"{len(right)} of the four options equal {target} "
                   f"({[item.choices[i] for i in right]}) in {item.choices}{note}")
    elif right[0] != ki:
        bad.append(f"the page gives {target}, printed as "
                   f"{item.choices[right[0]]!r}, but {item.choices[ki]!r} is keyed")
    return bad


# ------------------------------------------------------------- the families

def check_two_way(item) -> list[str]:
    T = Printed(item.table)
    bad = T.closure()
    er, ec, cr, cc = read_question(item.stem, T.row_labels, T.col_labels)
    den = T.count(cr, cc)
    if den == 0:
        return bad + ["the condition the stem names covers no cells"]
    exact = Q(T.count(meet(er, cr), meet(ec, cc)), den)
    return bad + judge(item, exact)


def check_freq_table(item) -> list[str]:
    F = OneWay(item.table)
    bad = F.closure()
    hit = match_labels(question(item.stem), F.labels)
    if len(hit) != 1:
        raise Unreadable(f"the question names {len(hit)} of the printed categories")
    return bad + judge(item, Q(F.counts[hit[0]], sum(F.counts)))


def check_freq_grouped(item) -> list[str]:
    F = OneWay(item.table)
    bad = F.closure()
    qs = question(item.stem)
    spans = []
    for m in re.finditer(r"at least (\d[\d,]*)|scored at least (\d[\d,]*)", qs, re.I):
        spans.append(float((m.group(1) or m.group(2)).replace(",", "")))
    if len(spans) != 2:
        raise Unreadable(f"expected two cuts in {qs!r}, found {spans}")
    lo, hi = spans
    inside = [F.counts[i] for i, lab in enumerate(F.labels)
              if (s := label_span(lab)) and s[0] >= lo]
    above = [F.counts[i] for i, lab in enumerate(F.labels)
             if (s := label_span(lab)) and s[0] >= hi]
    if not inside:
        raise Unreadable("no printed interval falls inside the condition")
    return bad + judge(item, Q(sum(above), sum(inside)))


LIST_SPLIT = re.compile(r",\s*and\s+|\s+and\s+|,\s*")


def check_bag(item) -> list[str]:
    head = item.stem.split(". ")[0]
    body = head.split(":", 1)[1] if ":" in head else \
        re.sub(r"^.*?(?:contains|there are)\s+", "", head, flags=re.I)
    pairs = []
    for part in LIST_SPLIT.split(body.rstrip(".")):
        m = re.match(r"^\s*(\d[\d,]*)\s+([A-Za-z]+)", part)
        if m:
            pairs.append((int(m.group(1).replace(",", "")), m.group(2).lower()))
    if len(pairs) < 2:
        raise Unreadable(f"cannot read the counts out of {head!r}")
    total = sum(k for k, _ in pairs)
    qs = question(item.stem)
    m = re.search(r"neither (\w+) nor (\w+)", qs, re.I)
    if m:
        out = {m.group(1).lower(), m.group(2).lower()}
        if not out <= {c for _, c in pairs}:
            raise Unreadable(f"the excluded colours {out} are not in the list")
        num = sum(k for k, c in pairs if c not in out)
    else:
        named = [k for k, c in pairs if re.search(rf"\b{c}\b", qs, re.I)]
        if len(named) != 1:
            raise Unreadable(f"the question names {len(named)} of the listed kinds")
        num = named[0]
    return judge(item, Q(num, total))


def check_subset(item) -> list[str]:
    head = item.stem.split(". ")[0]
    nums = [int(t.replace(",", "")) for t in re.findall(r"\b(\d[\d,]*)\b", head)]
    if re.search(r"\bpolygon\b", head, re.I):
        if not nums:
            raise Unreadable("no side count in the polygon stem")
        return judge(item, Q(1, nums[0]))
    big = [v for v in nums if v == max(nums)]
    small = [v for v in nums if v != max(nums)]
    if not big or not small:
        raise Unreadable(f"cannot read a part and a whole out of {head!r}")
    return judge(item, Q(small[0], max(nums)))


def check_data_set(item) -> list[str]:
    first = item.stem.split("\n")[0]
    vals = [int(t.replace(",", "").replace("−", "-"))
            for t in re.findall(r"−?-?\d[\d,]*", first)]
    if len(vals) < 3:
        raise Unreadable(f"cannot read a data set out of {first!r}")
    qs = question(item.stem)
    tests = {"negative": lambda v: v < 0, "positive": lambda v: v > 0,
             "even": lambda v: v % 2 == 0, "odd": lambda v: v % 2 != 0}
    named = [t for t in tests if re.search(rf"\b{t}\b", qs, re.I)]
    if len(named) != 1:
        raise Unreadable(f"the question names {named} traits")
    return judge(item, Q(sum(1 for v in vals if tests[named[0]](v)), len(vals)))


def check_count(item) -> list[str]:
    stem = item.stem
    probs = [Q(t) for t in re.findall(r"\b(0\.\d+)\b", stem)]
    if not probs:
        raise Unreadable("no probability printed in the stem")
    if re.search(r"nearest integer", stem, re.I):
        m = re.search(r"increased to ([\d,]+)", stem)
        if not m:
            raise Unreadable("no total printed for the rounding question")
        n = int(m.group(1).replace(",", ""))
        exact = probs[0] * n
        if (exact - exact.numerator // exact.denominator) * 2 == 1:
            return [f"{exact} sits exactly halfway between two integers"]
        return judge(item, half_up(exact, Q(1)))
    m = re.search(r"total of ([\d,]+)|contains a total of ([\d,]+)|has ([\d,]+)|"
                  r"holds ([\d,]+)", stem)
    if not m:
        raise Unreadable("no total printed in the stem")
    n = int(next(g for g in m.groups() if g).replace(",", ""))
    if len(probs) == 2:
        return judge(item, (1 - probs[0] - probs[1]) * n)
    return judge(item, probs[0] * n)


def check_symbolic(item) -> list[str]:
    m = re.match(r"There are n ([\w\- ]+?) and ([\d,]+) ([\w\- ]+?) on a ", item.stem)
    if not m:
        raise Unreadable(f"cannot read the two groups out of {item.stem[:60]!r}")
    first, k, second = m.group(1), int(m.group(2).replace(",", "")), m.group(3)
    qs = question(item.stem)
    mm = re.search(r"of selecting a ([\w\- ]+?) ", qs)
    if not mm:
        raise Unreadable(f"cannot read which group is asked for in {qs!r}")
    asked = mm.group(1).strip()
    if words(asked) <= words(first):
        top = lambda n: n
    elif words(asked) <= words(second):
        top = lambda n: k
    else:
        raise Unreadable(f"{asked!r} names neither group")

    def value(text, n):
        """An option in n as an exact rational at a given n.

        The two sides of the bar are evaluated separately in integers and the
        fraction built from them: `eval` on the whole string would divide in
        floating point, and 7/36 would never equal Fraction(7, 36).
        """
        t = text.replace("\u2212", "-").replace(",", "")
        if t.count("/") != 1 or not re.fullmatch(r"[0-9n+() /]+", t):
            return None
        top, bot = t.split("/")
        try:
            a, b = (int(eval(x.replace("n", f"({n})"), {"__builtins__": {}}, {}))
                    for x in (top, bot))
        except Exception:                                           # noqa: BLE001
            return None
        return None if b == 0 else Q(a, b)

    right = []
    for i, ch in enumerate(item.choices):
        if all((v := value(ch, n)) is not None and v == Q(top(n), n + k)
               for n in (7, 13, 29)):
            right.append(i)
    if len(right) != 1:
        return [f"{len(right)} of the four options equal the probability in n: "
                f"{item.choices}"]
    if right[0] != LETTERS.index(item.answer):
        return [f"the correct option is {item.choices[right[0]]!r} but "
                f"{item.choices[LETTERS.index(item.answer)]!r} is keyed"]
    return []


def check_rate(item) -> list[str]:
    m = re.match(r"If ([\d,]+) .*?\bfirst ([\d,]+) .*?\bfirst (\d+) days\?",
                 item.stem)
    if not m:
        raise Unreadable(f"cannot read the rate, target and span out of "
                         f"{item.stem[:80]!r}")
    rate, total, days = (int(g.replace(",", "")) for g in m.groups())
    return judge(item, Q(rate * days, total))


def check_missing_cell(item) -> list[str]:
    T = Printed(item.table)
    bad = T.closure()
    if len(T.hidden) != 1:
        raise Unreadable(f"{len(T.hidden)} cells are printed as unknown")
    hr, hc = T.hidden[0]
    qs = question(item.stem)
    said = [s for s in re.split(r"(?<=[.?])\s+(?=[A-Z])",
                                QMARK.sub("", item.stem)) if "probability" in s]
    if not said:
        raise Unreadable("no stated probability on the page")
    sent = said[-1]
    m = re.search(r"who (.+?) is chosen at random", sent)
    if not m:
        raise Unreadable(f"cannot find the condition in {sent!r}")
    rows = match_labels(m.group(1), T.row_labels)
    m2 = re.search(r"the probability that (.+?) is ([\d,]+)/([\d,]+)", sent)
    if not m2:
        raise Unreadable(f"cannot find the stated probability in {sent!r}")
    cols = match_labels(m2.group(1), T.col_labels)
    p = Q(int(m2.group(2)), int(m2.group(3)))
    if len(rows) != 1 or len(cols) != 1:
        raise Unreadable(f"the stem names {len(rows)} rows and {len(cols)} columns")
    if rows[0] != hr:
        raise Unreadable("the stated probability is about a row with no unknown")
    known = [v for j, v in enumerate(T.cells[hr]) if j != hc]
    top = T.cells[hr][cols[0]]
    if top is None:
        return bad + ["the stated probability is about the hidden cell itself"]
    if p == 0:
        return bad + ["a stated probability of zero determines nothing"]
    total = Q(top) / p
    x = total - sum(known)
    if x.denominator != 1:
        return bad + [f"the stated probability {p} gives a non-integer cell {x}"]
    if not qs.startswith("What is the value of x"):
        raise Unreadable(f"unexpected question {qs!r}")
    return bad + judge(item, Q(x))


def check_cell_from_total(item) -> list[str]:
    T = Printed(item.table)
    bad = T.closure()
    if len(T.hidden) != 1:
        raise Unreadable(f"{len(T.hidden)} cells are printed as unknown")
    printed = sum(v for r in T.cells for v in r if v is not None)
    prose = QMARK.sub("", item.stem)[:-len(question(item.stem))]
    bigger = {int(t.replace(",", "")) for t in re.findall(r"\b(\d[\d,]*)\b", prose)
              if int(t.replace(",", "")) > printed}
    if len(bigger) != 1:
        raise Unreadable(f"the scenario prose names {sorted(bigger)} as possible "
                         f"grand totals; exactly one is needed")
    n = bigger.pop()
    qs = question(item.stem)
    m = re.match(r"^How many of the (?P<rest>.+)\?$", qs, re.I)
    if not m:
        raise Unreadable(f"unexpected question {qs!r}")
    # "the seedlings that did not flower were grown under a lamp" is a column
    # clause and a row clause run together, and the "not" in the first half
    # reaches the row label in the second. Split it the way the percent frame
    # is split, and take whichever half names each axis on its own.
    er, ec, cr, cc = split_two(m.group("rest"), T.row_labels, T.col_labels)
    rows = tuple(sorted(set((er or ()) + (cr or ()))))
    cols = tuple(sorted(set((ec or ()) + (cc or ()))))
    hr, hc = T.hidden[0]
    if rows != (hr,) or cols != (hc,):
        raise Unreadable(f"the question names rows {rows} and columns {cols}, but "
                         f"the unknown cell is at {(hr, hc)}")
    return bad + judge(item, Q(n - printed))


MULTS = {"twice": 2, "three times": 3, "four times": 4}


def check_percent_columns(item) -> list[str]:
    rows = item.table
    labels = [r[0] for r in rows[1:-1]]
    cols = rows[0][1:]
    pct = [[Q(str(v).rstrip("%")) for v in r[1:]] for r in rows[1:-1]]
    bad = []
    for j, lab in enumerate(cols):
        s = sum(r[j] for r in pct)
        if s != 100:
            bad.append(f"the {lab} column of percentages totals {s}%, not 100%")
    m = re.search(r"the number of ([\w\- ]+?) (?:responses|answers) was "
                  r"(twice|three times|four times) the number of "
                  r"([\w\- ]+?) (?:responses|answers)", item.stem)
    if not m:
        raise Unreadable("the ratio between the two columns is not printed")
    bigger, mult = m.group(1), MULTS[m.group(2)]
    big = [j for j, lab in enumerate(cols) if words(lab) <= words(bigger)]
    if len(big) != 1:
        raise Unreadable(f"{bigger!r} names {len(big)} of the printed columns")
    qs = question(item.stem)
    mm = re.search(r"preferred (?:a )?(.+?) is selected at random", qs)
    if not mm:
        raise Unreadable(f"cannot find the conditioning row in {qs!r}")
    hit = [i for i, lab in enumerate(labels) if words(lab) <= words(mm.group(1))]
    if len(hit) != 1:
        raise Unreadable(f"the question names {len(hit)} rows")
    tail = qs.split("probability that", 1)[-1]
    asked = [j for j, lab in enumerate(cols) if words(lab) <= words(tail)]
    if len(asked) != 1:
        raise Unreadable(f"the question names {len(asked)} columns")
    w = [mult if j == big[0] else 1 for j in range(len(cols))]
    parts = [pct[hit[0]][j] * w[j] for j in range(len(cols))]
    if sum(parts) == 0:
        return bad + ["nobody chose this row, so the condition is empty"]
    return bad + judge(item, parts[asked[0]] / sum(parts))


FRAC_WORDS = {"one half": Q(1, 2), "one third": Q(1, 3), "one fourth": Q(1, 4),
              "two thirds": Q(2, 3), "one fifth": Q(1, 5),
              "three fourths": Q(3, 4)}


def check_nearest_row(item) -> list[str]:
    T = Printed(item.table)
    bad = T.closure()
    qs = question(item.stem)
    frac = [v for k, v in FRAC_WORDS.items() if k in qs.lower()]
    if len(frac) != 1:
        raise Unreadable(f"the question names {len(frac)} fractions")
    cols = match_labels(qs, T.col_labels)
    if len(cols) != 1:
        raise Unreadable(f"the question names {len(cols)} columns")
    j = cols[0]
    colv = [T.cells[i][j] for i in range(T.nr)]
    target = frac[0] * sum(colv)
    gaps = [abs(Q(v) - target) for v in colv]
    best = min(gaps)
    near = [i for i, g in enumerate(gaps) if g == best]
    if len(near) != 1:
        bad.append(f"rows {[T.row_labels[i] for i in near]} are equally close to "
                   f"{target}, so there is no single nearest row")
        return bad
    want = T.row_labels[near[0]]
    if sorted(item.choices) != sorted(T.row_labels):
        bad.append(f"the options {item.choices} are not the table's rows "
                   f"{T.row_labels}")
    keyed = item.choices[LETTERS.index(item.answer)]
    if keyed != want:
        bad.append(f"{want!r} is nearest to {target} but {keyed!r} is keyed")
    return bad


READERS = {
    "prob.two_way.marginal": check_two_way,
    "prob.two_way.joint": check_two_way,
    "prob.two_way.conditional": check_two_way,
    "prob.two_way.grouped": check_two_way,
    "prob.two_way.missing_cell": check_missing_cell,
    "prob.two_way.cell_from_total": check_cell_from_total,
    "prob.two_way.percent_columns": check_percent_columns,
    "prob.two_way.nearest_row": check_nearest_row,
    "prob.freq_table": check_freq_table,
    "prob.freq_grouped": check_freq_grouped,
    "prob.bag": check_bag,
    "prob.subset": check_subset,
    "prob.data_set": check_data_set,
    "prob.count_from_prob": check_count,
    "prob.symbolic": check_symbolic,
    "prob.rate_share": check_rate,
}


# ----------------------------------------------------------------- the sweep

def inspect(item) -> list[str]:
    reader = READERS.get(item.template)
    if reader is None:
        raise Unreadable(f"no reader for {item.template!r}")
    return reader(item)


def sweep(per: int, verbose: bool = False):
    topic = load_topics()["probability"]
    read = made = 0
    defects, unread = [], []
    for name in topic.templates:
        for seed in range(per):
            try:
                item = generate(name, seed)
            except ItemError:
                continue
            made += 1
            try:
                bad = inspect(item)
            except Unreadable as exc:
                unread.append(f"{name} seed {seed}: {exc}")
                continue
            read += 1
            for b in bad:
                defects.append(f"{name} seed {seed}: {b}")
    import random as _r
    for s in topic.sources:
        item = s.build(_r.Random(0))
        made += 1
        try:
            bad = inspect(item)
        except Unreadable as exc:
            unread.append(f"source {s.id}: {exc}")
            continue
        read += 1
        for b in bad:
            defects.append(f"source {s.id}: {b}")
    return made, read, defects, unread


def scenario_english() -> list[str]:
    """Every phrase a scenario can print must name the categories it stands for.

    This is the load-bearing assumption of the whole checker: the reader finds
    the event and the condition by matching the stem against the table's
    printed labels, so a scenario whose sentence says "does not have a
    state-level income tax" while its table column says "No state income tax"
    would be read as naming nothing -- or, worse, as naming the opposite
    column. Checking it here means a new scenario cannot be added without the
    proof being re-run.
    """
    from satbank.topics.probability.world import TWO_WAY
    bad = []
    for key, c in sorted(TWO_WAY.items()):
        for axis, sels, labels in (("row", c.row_sels(), [r.label for r in c.rows]),
                                   ("col", c.col_sels(), [x.label for x in c.cols])):
            for sel in sels:
                for form in ("n", "p", "g", "pl"):
                    phrase = getattr(sel, form) or sel.p
                    got = match_labels(phrase, labels)
                    if got != tuple(sorted(sel.idx)):
                        bad.append(
                            f"{key}.{axis} {sel.label or sel.n!r}: the {form} phrase "
                            f"{phrase!r} reads as {[labels[i] for i in got]}, not as "
                            f"{[labels[i] for i in sel.idx]}")
    return bad


# ------------------------------------------------------------ fault injection

import copy                                                         # noqa: E402


def _first(pred, names, per=200):
    for name in names:
        for seed in range(per):
            try:
                item = generate(name, seed)
            except ItemError:
                continue
            if pred(item):
                return copy.deepcopy(item)
    return None


TWO = ["prob.two_way.marginal", "prob.two_way.joint", "prob.two_way.conditional",
       "prob.two_way.grouped"]


def f_margin():
    """A printed column total that is one more than the column."""
    it = _first(lambda i: i.table and Printed(i.table).margins and i.fmt == "mcq", TWO)
    it.table[-1][1] = str(int(it.table[-1][1].replace(",", "")) + 1)
    return "a printed column total raised by one", it


def f_grand():
    """A grand total that no longer matches its margins."""
    it = _first(lambda i: i.table and Printed(i.table).margins, TWO)
    it.table[-1][-1] = str(int(it.table[-1][-1].replace(",", "")) + 7)
    return "a printed grand total raised by seven", it


def f_key_letter():
    """The right options, the wrong letter."""
    it = _first(lambda i: i.fmt == "mcq", TWO)
    it.answer = "A" if it.answer != "A" else "B"
    return "the key letter moved to a wrong option", it


def f_duplicate():
    """A distractor rewritten to the key's value in another spelling."""
    it = _first(lambda i: i.fmt == "mcq" and "/" in i.choices[0], TWO)
    ki = LETTERS.index(it.answer)
    v = option_value(it.choices[ki])
    wi = next(i for i in range(4) if i != ki)
    it.choices[wi] = f"{v.numerator}/{v.denominator}"
    it.latex_choices = list(it.choices)
    return "a distractor rewritten to the key's own value", it


def f_reverse():
    """The keyed option replaced by P(B|A) -- the conditional the other way."""
    def ok(i):
        if i.fmt != "mcq" or not i.table:
            return False
        T = Printed(i.table)
        try:
            er, ec, cr, cc = read_question(i.stem, T.row_labels, T.col_labels)
        except Unreadable:
            return False
        if not (cr or cc):
            return False
        a, b = T.count(cr, cc), T.count(er, ec)
        return a != b and b and T.count(meet(er, cr), meet(ec, cc))
    it = _first(ok, ["prob.two_way.conditional", "prob.two_way.grouped"])
    T = Printed(it.table)
    er, ec, cr, cc = read_question(it.stem, T.row_labels, T.col_labels)
    num = T.count(meet(er, cr), meet(ec, cc))
    it.choices[LETTERS.index(it.answer)] = f"{num}/{T.count(er, ec)}"
    it.latex_choices = list(it.choices)
    return "the keyed option replaced by the reversed conditional", it


def f_swap_clauses():
    """The stem's event and condition exchanged, the options left alone.

    The only thing that changes is the sentence, so a reader that guessed the
    question instead of reading it would report nothing.
    """
    pat = re.compile(r"(of selecting )(.+?)(, given that (?:the )?\S+ )(.+?)(\?)")
    it = _first(lambda i: i.fmt == "mcq" and pat.search(i.stem),
                ["prob.two_way.conditional", "prob.two_way.grouped"])
    it.stem = pat.sub(lambda m: m.group(1) + m.group(4) + m.group(3) + m.group(2)
                      + m.group(5), it.stem, count=1)
    return "the event and the condition exchanged in the stem", it


def f_grid_reverse():
    """A grid-in answering P(B|A) where the stem asks P(A|B)."""
    def ok(i):
        if i.fmt != "spr" or not i.table:
            return False
        T = Printed(i.table)
        try:
            er, ec, cr, cc = read_question(i.stem, T.row_labels, T.col_labels)
        except Unreadable:
            return False
        return (cr or cc) and T.count(er, ec) and T.count(cr, cc) != T.count(er, ec)
    it = _first(ok, ["prob.two_way.conditional", "prob.two_way.grouped"])
    T = Printed(it.table)
    er, ec, cr, cc = read_question(it.stem, T.row_labels, T.col_labels)
    v = Q(T.count(meet(er, cr), meet(ec, cc)), T.count(er, ec))
    it.answer = f"{v.numerator}/{v.denominator}"
    return "a grid-in answering the reversed conditional", it


def f_grid_long():
    """A grid-in answer too long for the five-character field."""
    it = _first(lambda i: i.fmt == "spr" and i.table, TWO)
    T = Printed(it.table)
    er, ec, cr, cc = read_question(it.stem, T.row_labels, T.col_labels)
    num, den = T.count(meet(er, cr), meet(ec, cc)), T.count(cr, cc)
    it.answer = f"{num * 1000}/{den * 1000}"
    return "a grid-in answer that will not fit the five-character field", it


def f_percent_round():
    """A percent key rounded to the wrong neighbour."""
    it = _first(lambda i: i.fmt == "mcq" and "%" in i.choices[0] and i.table, TWO)
    ki = LETTERS.index(it.answer)
    d = decimals(it.choices[ki])
    v = option_value(it.choices[ki]) * 100 + Q(1, 10 ** d)
    it.choices[ki] = f"{float(v):.{d}f}%"
    it.latex_choices = list(it.choices)
    return "a percent key rounded to the wrong neighbour", it


def f_closest_tie():
    """A second option exactly as far from the exact value as the key.

    The twin is the key's mirror image in the exact value, and it is printed
    as a fraction rather than a decimal because the mirror of a two-place
    decimal usually is not one -- rounding it to two places would destroy the
    tie and the fault would pass for the wrong reason.
    """
    def ok(i):
        return (i.fmt == "mcq" and i.table
                and re.search(r"\bclosest\b", i.stem, re.I)
                and "%" not in i.choices[0])
    it = _first(ok, ["prob.two_way.conditional", "prob.two_way.grouped"], per=400)
    T = Printed(it.table)
    er, ec, cr, cc = read_question(it.stem, T.row_labels, T.col_labels)
    exact = Q(T.count(meet(er, cr), meet(ec, cc)), T.count(cr, cc))
    ki = LETTERS.index(it.answer)
    twin = 2 * exact - option_value(it.choices[ki])
    wi = next(i for i in range(4) if i != ki)
    it.choices[wi] = f"{twin.numerator}/{twin.denominator}"
    it.latex_choices = list(it.choices)
    return "a second option exactly as close as the key on a 'closest to' page", it


def f_second_closest():
    """The second-closest option keyed on a "closest to" page."""
    def ok(i):
        return (i.fmt == "mcq" and i.table
                and re.search(r"\bclosest\b", i.stem, re.I)
                and "%" not in i.choices[0])
    it = _first(ok, ["prob.two_way.conditional", "prob.two_way.grouped"], per=400)
    ki = LETTERS.index(it.answer)
    it.answer = LETTERS[(ki + 1) % 4]
    return "the second-closest option keyed on a 'closest to' page", it


def f_cell():
    """One interior cell of the table changed after the options were built."""
    it = _first(lambda i: i.fmt == "mcq" and i.table and not Printed(i.table).margins,
                ["prob.two_way.conditional", "prob.two_way.joint"], per=400)
    it.table[1][1] = str(int(it.table[1][1].replace(",", "")) + 5)
    return "an interior cell changed after the options were chosen", it


def f_freq_total():
    """A one-way table whose printed total is not the sum of its counts."""
    it = _first(lambda i: i.table and OneWay(i.table).total_row,
                ["prob.freq_table", "prob.freq_grouped"], per=400)
    it.table[-1][1] = str(int(it.table[-1][1].replace(",", "")) + 3)
    return "a frequency table whose printed total is wrong", it


def f_nearest_row():
    """The second-nearest row keyed."""
    it = _first(lambda i: i.fmt == "mcq", ["prob.two_way.nearest_row"], per=400)
    ki = LETTERS.index(it.answer)
    it.answer = LETTERS[(ki + 1) % 4]
    return "the second-nearest row keyed", it


def f_pct_column():
    """A column of percentages that no longer totals 100."""
    it = _first(lambda i: bool(i.table), ["prob.two_way.percent_columns"], per=400)
    it.table[1][1] = f"{int(it.table[1][1].rstrip('%')) + 5}%"
    return "a column of percentages totalling 105%", it


def f_symbolic():
    """Two algebraically equal options on a 'in terms of n' page."""
    it = _first(lambda i: i.fmt == "mcq", ["prob.symbolic"], per=400)
    ki = LETTERS.index(it.answer)
    wi = next(i for i in range(4) if i != ki)
    it.choices[wi] = it.choices[ki].replace("n/(", "(n)/(")
    it.latex_choices = list(it.choices)
    return "two algebraically equal options in terms of n", it


FAULTS = [f_margin, f_grand, f_key_letter, f_duplicate, f_reverse, f_swap_clauses,
          f_grid_reverse, f_grid_long, f_percent_round, f_closest_tie,
          f_second_closest, f_cell, f_freq_total, f_nearest_row, f_pct_column,
          f_symbolic]


def selftest() -> int:
    print("scenario English -> printed labels")
    bad = scenario_english()
    for b in bad:
        print(f"  FAIL {b}")
    print(f"  {'FAIL' if bad else 'ok'}: every scenario phrase resolves to the "
          f"categories it names ({len(bad)} mismatches)\n")

    print("injected faults (a fault counts as caught only when the reader reports a")
    print("defect; an Unreadable page is a reader that stopped working, not a catch)")
    caught = 0
    for make in FAULTS:
        try:
            what, item = make()
        except Exception as exc:                                    # noqa: BLE001
            print(f"  FAIL could not build the fault {make.__name__}: "
                  f"{type(exc).__name__}: {exc}")
            continue
        try:
            found = inspect(item)
        except Unreadable as exc:
            print(f"  FAIL {what}: the reader could not read the page ({exc})")
            continue
        if found:
            caught += 1
            print(f"  ok   {what}\n         -> {found[0]}")
        else:
            print(f"  FAIL {what}: not caught")
    print(f"\n  {caught}/{len(FAULTS)} faults caught")
    return 0 if (caught == len(FAULTS) and not bad) else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--per", type=int, default=300)
    ap.add_argument("--show", type=int, default=12)
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    made, read, defects, unread = sweep(a.per)
    print(f"{made:,} items built, {read:,} read back from the page")
    for u in unread[:a.show]:
        print(f"  UNREAD {u}")
    if len(unread) > a.show:
        print(f"  ... and {len(unread) - a.show:,} more unreadable")
    for d in defects[:a.show]:
        print(f"  DEFECT {d}")
    if len(defects) > a.show:
        print(f"  ... and {len(defects) - a.show:,} more defects")
    print(f"{len(unread):,} unreadable, {len(defects):,} defects")
    return 1 if (unread or defects) else 0


if __name__ == "__main__":
    sys.exit(main())
