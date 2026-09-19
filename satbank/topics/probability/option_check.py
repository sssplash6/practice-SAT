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
              "people": "person", "an": "a", "the": "the"}


def stem_word(w: str) -> str:
    if w in _IRREGULAR:
        return _IRREGULAR[w]
    if w.endswith("ies") and len(w) > 4:
        return w[:-3] + "y"
    for suf in ("ing", "ed", "es", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            return w[:-len(suf)]
    return w


def words(text: str) -> set[str]:
    """Every token of a phrase, stemmed. Nothing is discarded as a stop word:
    "not", "no" and a bare "a" are exactly the tokens that tell two printed
    labels apart, and a filter that drops them makes the reader agree with
    the wrong column without complaining."""
    t = str(text).lower().replace(",", "").replace("−", "-")
    t = re.sub(r"[–—/\-]", " ", t)
    return {stem_word(w) for w in re.findall(r"[a-z0-9$+]+", t)}


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

    A label is named when every one of its tokens appears in the clause. A
    label whose tokens are a proper subset of another named label's is then
    dropped: "Has bicycle paths" is inside "does not have bicycle paths" and
    is not what that clause means.
    """
    cw = words(clause)
    hit = [(i, words(lab)) for i, lab in enumerate(labels)
           if lab.strip() and words(lab) and words(lab) <= cw]
    keep = [i for i, w in hit
            if not any(w < w2 for j, w2 in hit if j != i)]
    if keep:
        return tuple(sorted(keep))
    span = clause_span(clause)
    if span is None:
        return ()
    lo, hi = span
    out = [i for i, lab in enumerate(labels)
           if (s := label_span(lab)) and lo <= s[0] and s[1] <= hi]
    return tuple(out)


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
    for name, pat in FRAMES:
        m = pat.match(qs)
        if not m:
            continue
        if name in ("split_fraction", "split_percent"):
            return split_two(m.group("rest"), rows, cols)
        ev, cond = m.group("ev"), m.groupdict().get("cond")
        e = sets_in(ev, rows, cols)
        c = sets_in(cond, rows, cols) if cond else ((), ())
        if e == ((), ()):
            raise Unreadable(f"no printed label is named in {ev!r}")
        if cond and c == ((), ()):
            raise Unreadable(f"no printed label is named in {cond!r}")
        if cond and _axis(e) is not None and _axis(e) == _axis(c):
            raise Unreadable("the event and the condition read as the same axis")
        return e[0] or None, e[1] or None, c[0] or None, c[1] or None
    raise Unreadable(f"no question frame matches {qs!r}")


def _axis(pair):
    if pair[0] and not pair[1]:
        return "row"
    if pair[1] and not pair[0]:
        return "col"
    return None


def sets_in(clause: str, rows: list[str], cols: list[str]):
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
