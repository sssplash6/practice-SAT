"""An independently written solver for every template in this topic.

Nothing here imports `study.py`, `claims.py` or any family. The rule about
what a margin of error supports is written out a second time, in this file,
over value sets of its own; the sentences are taken apart here with this
file's own patterns; and the arithmetic is redone from `item.params`. A
template and a solver that shared a helper would share its mistakes, and the
one defect this topic was built to avoid -- an engine that has been told the
answer and agrees with itself -- would survive both.

What it does take from the topic is **vocabulary**: what this scenario calls
its population, its members and the thing it measured. Those cannot be
recovered from a page any more than a scatterplot's units can be recovered
from its pixels, and they are facts about the scenario rather than about the
answer.

The rule, restated:

    a random sample with a margin of error M around an estimate E supports
    exactly one thing -- that the population's value plausibly lies in
    [E-M, E+M]. It supports a statement about the count when, and only when,
    the page states the size of the population. It supports nothing about
    individuals, nothing about a group the units were not drawn from, and
    nothing with certainty. Without randomness it supports nothing about the
    population at all.
"""

from __future__ import annotations

import re
from fractions import Fraction as Q

from ...audit import AuditError
from .families.design import DESIGNS, PLAUSIBLE
from .families.estimate import FREQ, GROUP, RANGE, SCALE, TWO_WAY
from .world import (COUNT_SCENES, MEAN_SCENES, PCT_SCENES, SUBGROUP_SCENES,
                    TABLE_SCENES)

__all__ = ["AUDITS"]

ALL_SCENES = {**PCT_SCENES, **MEAN_SCENES, **TABLE_SCENES, **SUBGROUP_SCENES,
              **COUNT_SCENES}


# --------------------------------------------------------------- value sets
#
# ("band", lo, hi) with None for an open end, ("only", v), ("not", v),
# ("outside", lo, hi). Written here rather than imported, so a mistake in the
# generator's own set algebra cannot be confirmed by this file.

def _holds(outer, inner) -> bool:
    """Is every value `inner` allows also allowed by `outer`?"""
    ok, oa, ob = (outer + (None,))[:3] if outer[0] != "only" else \
        ("only", outer[1], None)
    ik = inner[0]
    if ok == "band":
        lo, hi = outer[1], outer[2]
        if ik == "band":
            a, b = inner[1], inner[2]
            below = lo is None or (a is not None and a >= lo)
            above = hi is None or (b is not None and b <= hi)
            return below and above
        if ik == "only":
            return ((lo is None or inner[1] >= lo)
                    and (hi is None or inner[1] <= hi))
        return lo is None and hi is None
    if ok == "only":
        v = outer[1]
        if ik == "only":
            return inner[1] == v
        if ik == "band":
            return inner[1] is not None and inner[1] == inner[2] == v
        return False
    if ok == "not":
        v = outer[1]
        if ik == "only":
            return inner[1] != v
        if ik == "band":
            if inner[1] is None or inner[2] is None:
                return False
            return v < inner[1] or v > inner[2]
        return ik == "not" and inner[1] == v
    if ok == "outside":
        lo, hi = outer[1], outer[2]
        if ik == "only":
            return inner[1] < lo or inner[1] > hi
        if ik == "band":
            if inner[2] is not None and inner[2] < lo:
                return True
            return inner[1] is not None and inner[1] > hi
        return False
    raise AuditError(f"unreadable value set {outer!r}")


def _negate(vs):
    k = vs[0]
    if k == "band":
        lo, hi = vs[1], vs[2]
        if lo is None and hi is not None:
            return ("band", hi, None)
        if hi is None and lo is not None:
            return ("band", None, lo)
        if lo is None and hi is None:
            raise AuditError("the negation of everything is nothing")
        return ("outside", lo, hi)
    if k == "only":
        return ("not", vs[1])
    raise AuditError(f"cannot negate {vs!r}")


RANK = {"approximate": 0, "plausible": 1, "certain": 2}


# ------------------------------------------------------- reading a sentence

# a printed number, thousands separators and decimals included, and never
# the full stop that ends the sentence -- a character class holding both the
# comma and the point swallows it and turns "0.91." into a parse error
_N = r"(\d[\d,]*(?:\.\d+)?)"
_NUM = re.compile(r"(?<![\w.])" + _N)


def _q(text: str) -> Q:
    return Q(text.replace(",", ""))


def _nums(text: str) -> list[Q]:
    return [_q(m) for m in _NUM.findall(text)]


def _vset(text: str):
    """What range of values the sentence asserts, before any negation.

    Case-insensitive throughout: the same assertion is printed "Between 4 and
    5" at the head of a sentence and "is between 4 and 5" inside one, and a
    reader that saw only the second would quietly stop reading half the page.
    """
    t = text
    m = re.search(rf"less than {_N}[^.]*?or (?:greater|more) than {_N}", t, re.I)
    if m:
        return ("outside", _q(m.group(1)), _q(m.group(2)))
    m = re.search(rf"between {_N}[^.]*? and {_N}", t, re.I)
    if m:
        return ("band", _q(m.group(1)), _q(m.group(2)))
    m = re.search(rf"(?:greater|more) than {_N}", t, re.I)
    if m:
        return ("band", _q(m.group(1)), None)
    m = re.search(rf"(?:less|fewer) than {_N}", t, re.I)
    if m:
        return ("band", None, _q(m.group(1)))
    ns = _nums(t)
    if not ns:
        return None                 # the sentence names no value at all
    return ("only", ns[-1])


# what a "no conclusion can be made" sentence blames, read off the sentence.
# Only the first is ever a reason: every sample leaves somebody out and every
# sample holds members without the trait, so refusing an inference on either
# of those grounds would refuse every inference ever drawn from a sample.
_GROUNDS = ((r"chose to take part", "not_random"),
            (r"did not include all", "not_exhaustive"),
            (r"and not just", "mixed_sample"))


def _ground(text: str) -> str:
    for pat, name in _GROUNDS:
        if re.search(pat, text):
            return name
    raise AuditError(f"a no-conclusion sentence that blames nothing: {text!r}")


def _read(sc, text: str):
    """(aspect, population, modality, value set) for one printed sentence."""
    if "no conclusion can be made" in text:
        return ("no_conclusion", _ground(text), "plausible", None)

    body = text
    for frag in (sc.trait, sc.extra.get("wider_trait", "")):
        if frag and frag in body:
            body = body.replace(frag, " ")

    # who or what the sentence is about
    if "are not really" in text:
        aspect, pop = "misclassification", "sample"
    elif sc.indiv_sample and text.startswith(sc.indiv_sample):
        aspect, pop = "individuals", "sample"
    elif sc.indiv and text.startswith(sc.indiv):
        aspect, pop = "individuals", "frame"
    elif sc.did and re.search(rf"\b(all|most|any) ({re.escape(sc.members)}|"
                              rf"{re.escape(sc.member)}) {re.escape(sc.did)}\b", text):
        aspect, pop = "individuals", "frame"
    elif sc.count_np and sc.count_np in text:
        aspect, pop = "count", "frame"
    elif "wider_all" in sc.extra and sc.extra["wider_all"] in text:
        aspect, pop = "parameter", "wider"
    else:
        aspect, pop = "parameter", "frame"

    negated = False
    if text.startswith("It is not possible that"):
        modality, negated = "certain", True
    elif " is doubtful that " in text or text.startswith("It is doubtful that"):
        modality, negated = "plausible", True
    elif re.search(r"\bexactly\b|\bmust\b", text):
        modality = "certain"
    elif re.search(r"\b[Aa]pproximately\b", text):
        modality = "approximate"
    else:
        modality = "plausible"

    vs = _vset(body)
    if negated:
        vs = _negate(vs)
    return (aspect, pop, modality, vs)


# ---------------------------------------------------------- what a study says

def _reports(p: dict) -> dict:
    """The rule, written out here for the second time."""
    est = Q(p["estimate"])
    out = {("statistic", "sample"): ("certain", ("only", est))}
    if not p.get("random", True):
        return out
    m = p.get("margin")
    per = Q(1, 100) if p["quantity"] == "percent" else Q(1)
    if m is None:
        out[("parameter", "frame")] = ("approximate", ("only", est))
        if p.get("size") is not None and p["quantity"] in ("percent", "proportion"):
            out[("count", "frame")] = ("approximate",
                                       ("only", Q(p["size"]) * est * per))
        return out
    m = Q(m)
    out[("parameter", "frame")] = ("plausible", ("band", est - m, est + m))
    if p.get("size") is not None and p["quantity"] in ("percent", "proportion"):
        s = Q(p["size"]) * per
        out[("count", "frame")] = ("plausible",
                                   ("band", (est - m) * s, (est + m) * s))
    return out


def _supported(p: dict, claim) -> bool:
    aspect, pop, modality, vs = claim
    rep = _reports(p)
    if aspect == "no_conclusion":
        return (("parameter", "frame") not in rep
                and pop == "not_random" and not p.get("random", True))
    r = rep.get((aspect, pop))
    if r is None:
        return False                # nothing is reported about this subject
    if vs is None:
        raise AuditError("a sentence about something the study reports, with no "
                         "value in it, cannot be judged")
    if RANK[modality] > RANK[r[0]]:
        return False
    return _holds(vs, r[1])


def _one(p: dict, texts: list[str], sc) -> str:
    good = [t for t in texts if _supported(p, _read(sc, t))]
    if len(good) != 1:
        raise AuditError(f"{len(good)} of the four printed statements hold: {good}")
    return good[0]


# ------------------------------------------------------------- the solvers

def _sentences(p: dict) -> str:
    sc = ALL_SCENES[p["scene"]]
    return _one(p, p["texts"], sc)


def _subgroup(p: dict) -> str:
    return _sentences(p)


def _count_claim(p: dict) -> str:
    sc = ALL_SCENES[p["scene"]]
    right = Q(p["size"]) * Q(p["k"], p["n"])
    good = []
    for t in p["texts"]:
        v = _nums(t)[-1]
        certain = bool(re.search(r"\bmust\b|\bExactly\b|\bexactly\b", t))
        # one sample estimates the count; it does not settle it
        if not certain and v == right:
            good.append(t)
    if len(good) != 1:
        raise AuditError(f"{len(good)} of the four count sentences hold")
    return good[0]


def _scale_count(p: dict) -> float:
    return float(Q(p["base"]) * Q(p["k"], p["n"]))


def _scale_group(p: dict) -> float:
    return float((p["n"] - p["k"]) * p["g"])


def _scale_range(p: dict) -> str:
    kit = RANGE[p["ctx"]]
    vals = p["vals"]
    est = Q(sum(vals), len(vals)) * p["T"]
    hits = []
    for text in p["choices"]:
        a, b = (Q(x.replace(",", "")) for x in text.split(" to "))
        if b - a != kit.extra["width"]:
            raise AuditError(f"the range {text!r} is not {kit.extra['width']} wide")
        if a <= est <= b:
            hits.append(text)
    if len(hits) != 1:
        raise AuditError(f"the estimate {float(est)} lies in {len(hits)} of the "
                         f"printed ranges")
    return hits[0]


def _scale_two_way(p: dict) -> float:
    n = sum(sum(row) for row in p["counts"])
    col = sum(row[p["focus"]] for row in p["counts"])
    v = Q(p["N"] * col, n)
    return float(v.numerator // v.denominator + (1 if 2 * (v - v.numerator //
                                                           v.denominator) >= 1 else 0))


def _scale_frequency(p: dict) -> float:
    e = FREQ[p["ctx"]].extra
    f = p["freq"]
    n = sum(f)
    d = sum(f[i] for i in e["plus"]) - sum(f[i] for i in e["minus"])
    v = Q(d * p["P"], n)
    w = v.numerator // v.denominator
    return float(w + (1 if 2 * (v - w) >= 1 else 0))


def _plausible_count(p: dict) -> str:
    est, m, N = Q(p["estimate"]), Q(p["margin"]), Q(p["N"])
    lo, hi = N * (est - m) / 100, N * (est + m) / 100
    hits = []
    for text in p["texts"]:
        if p["form"] == "value":
            v = Q(text.replace(",", ""))
            if lo <= v <= hi:
                hits.append(text)
            continue
        sym = re.escape(p["sym"])
        m1 = re.match(rf"^([\d,]+) < {sym} < ([\d,]+)$", text)
        if m1:
            a, b = (Q(x.replace(",", "")) for x in m1.groups())
            if a <= lo and b >= hi:
                hits.append(text)
            continue
        m2 = re.match(rf"^{sym} ([<>]) ([\d,]+)$", text)
        if not m2:
            raise AuditError(f"unreadable option {text!r}")
        v = Q(m2.group(2).replace(",", ""))
        if (m2.group(1) == ">" and v <= lo) or (m2.group(1) == "<" and v >= hi):
            hits.append(text)
    if len(hits) != 1:
        raise AuditError(f"{len(hits)} of the four options hold: {hits}")
    return hits[0]


def _margin_size(p: dict) -> str:
    """With the method and the population fixed, only the sample size is free,
    and the margin falls as the sample grows."""
    ma, mb = Q(p["ma"]), Q(p["mb"])
    a, b = p["names"]
    hits = []
    for text in p["texts"]:
        m = re.match(rf"^Sample ([{a}{b}]) had a (smaller|larger) sample size\.$",
                     text)
        if not m:
            continue
        who, how = m.group(1), m.group(2)
        mine, other = (ma, mb) if who == a else (mb, ma)
        if (how == "smaller") == (mine > other):
            hits.append(text)
    if len(hits) != 1:
        raise AuditError(f"{len(hits)} of the printed reasons hold")
    return hits[0]


AUDITS = {
    "sstat.scale_count": _scale_count,
    "sstat.scale_group": _scale_group,
    "sstat.scale_range": _scale_range,
    "sstat.scale_two_way": _scale_two_way,
    "sstat.scale_frequency": _scale_frequency,
    "sstat.interpret_mean": _sentences,
    "sstat.interpret_percent": _sentences,
    "sstat.interpret_table": _sentences,
    "sstat.subgroup_claim": _subgroup,
    "sstat.count_claim": _count_claim,
    "sstat.plausible_count": _plausible_count,
    "sstat.margin_size": _margin_size,
}
