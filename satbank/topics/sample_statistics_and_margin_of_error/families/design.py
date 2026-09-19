"""Two families about what a margin of error is made of.

`plausible_count` turns the interval into counts: a percent with a margin,
against a population whose size the stem states, licenses an interval of
plausible counts -- and the page asks either which interval that is (official
item 2.4, whose options are inequalities in `r`) or which single count sits
inside it (official item 2.7, whose options are four numbers). Both readings
come out of the same report in `study.py`, chosen by `Claim.kind`.

`margin_size` is the other half of the subject and the one students are never
taught: the margin is a fact about the **design**. With the same method and
the same population, the margin falls as the sample grows, so the printed
margins say which sample was larger. The stem is worded from the comparison
of the two printed margins, so swapping the two margins in the table moves
both the stem and the answer.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from fractions import Fraction as Q

from ....exact import E
from ....item import Item, ItemError, Mis, assemble, assemble_text
from ..study import Band, Claim, Only, Study, supported
from ..values import Num, dec, q, tidy

__all__ = ["plausible_count", "margin_size", "PLAUSIBLE", "DESIGNS"]


@dataclass(frozen=True)
class Kit:
    key: str
    form: str
    stem: str
    ranges: dict = field(default_factory=dict)
    extra: dict = field(default_factory=dict)


# ----------------------------------------------- a plausible count, two ways

PLAUSIBLE = {
    "beads": Kit(
        key="beads", form="range",
        stem="A bag containing {N} beads of assorted colors is purchased from a "
             "craft store. To estimate the percent of red beads in the bag, a "
             "sample of beads is selected at random. The percent of red beads in "
             "the bag was estimated to be {est}, with an associated margin of "
             "error of {moe}. If {sym} is the actual number of red beads in the "
             "bag, which of the following is most plausible?",
        ranges=dict(N=(4000, 20000), Nstep=1000, est=(8, 40), moe=(1, 5)),
        extra=dict(sym="r")),
    "tiles": Kit(
        key="tiles", form="range",
        stem="A crate holding {N} floor tiles is delivered to a warehouse. To "
             "estimate the percent of the tiles that are chipped, a sample of "
             "tiles is selected at random. The percent of chipped tiles in the "
             "crate was estimated to be {est}, with an associated margin of "
             "error of {moe}. If {sym} is the actual number of chipped tiles in "
             "the crate, which of the following is most plausible?",
        ranges=dict(N=(2000, 16000), Nstep=500, est=(6, 34), moe=(1, 4)),
        extra=dict(sym="c")),
    "legislation": Kit(
        key="legislation", form="value",
        stem="From a population of {N} people, {n} were chosen at random and "
             "surveyed about a proposed piece of legislation. Based on the "
             "survey, it is estimated that {est} of people in the population "
             "support the legislation, with an associated margin of error of "
             "{moe}. Based on these results, which of the following is a "
             "plausible value for the total number of people in the population "
             "who support the proposed legislation?",
        ranges=dict(N=(20000, 90000), Nstep=5000, n=(500, 2000), nstep=100,
                    est=(20, 70), moe=(2, 6)),
        extra=dict(trait="support the legislation",
                   other="do not support the legislation")),
    "charter": Kit(
        key="charter", form="value",
        stem="A district has {N} households. A random sample of {n} of the "
             "households was surveyed about a proposed charter. Based on the "
             "survey, it is estimated that {est} of the district's households "
             "favor the charter, with an associated margin of error of {moe}. "
             "Based on these results, which of the following is a plausible "
             "value for the total number of households in the district that "
             "favor the charter?",
        ranges=dict(N=(12000, 60000), Nstep=2000, n=(400, 1600), nstep=100,
                    est=(25, 65), moe=(2, 5)),
        extra=dict(trait="favor the charter", other="do not favor the charter")),
}


def _counts(N: int, pct: Q) -> Q:
    return Q(N) * pct / 100


def plausible_count(rng: random.Random, seed: int, *, ctx=None, N=None, n=None,
                    est=None, moe=None, off=None, wrongs=None,
                    tier="medium") -> Item:
    """Which count, or which range of counts, the margin of error leaves open.

    `off` is where inside the interval the keyed count sits, in percentage
    points from the estimate -- official item 2.7 keys 16,750, which is
    1.5 points below 35% of 50,000. It is a position, not an answer: the
    engine still asks `study.supported` whether the value it produces is one
    the study leaves plausible, and refuses the draw if it is not.
    """
    kit = PLAUSIBLE[ctx] if ctx is not None else \
        PLAUSIBLE[rng.choice(sorted(PLAUSIBLE))]
    r = kit.ranges
    N = int(N) if N is not None else rng.randrange(r["N"][0], r["N"][1] + 1, r["Nstep"])
    est = q(est) if est is not None else Q(rng.randint(*r["est"]))
    moe = q(moe) if moe is not None else Q(rng.randint(*r["moe"]))
    if moe <= 0 or est - moe <= 0 or est + moe >= 100:
        raise ItemError("the interval has to sit inside 0% and 100%")
    n = None if "n" not in r else (int(n) if n is not None else
                                   rng.randrange(r["n"][0], r["n"][1] + 1, r["nstep"]))
    st = Study("percent", est, moe, n=n or 0, random=True, size=N)
    lo, hi = _counts(N, st.lo), _counts(N, st.hi)
    if lo.denominator != 1 or hi.denominator != 1:
        raise ItemError("the interval's endpoints have to be whole counts")

    stem = tidy(kit.stem.format(N=f"{N:,}", n=f"{n:,}" if n else "",
                                est=f"{dec(est, 0) if est.denominator == 1 else dec(est, 2)}%",
                                moe=f"{dec(moe, 0) if moe.denominator == 1 else dec(moe, 2)}%",
                                sym=kit.extra.get("sym", "")))

    if kit.form == "range":
        sym = kit.extra["sym"]
        mc, ec = _counts(N, moe), _counts(N, est)
        pool = {
            "interval": (f"{dec(lo, 0)} < {sym} < {dec(hi, 0)}", Band(lo, hi),
                         "read the margin of error as though it were the whole "
                         "of the estimate"),
            "above_upper": (f"{sym} > {dec(hi, 0)}", Band(hi, None),
                            "read the top of the interval as a floor the count "
                            "is above"),
            "below_lower": (f"{sym} < {dec(lo, 0)}", Band(None, lo),
                            "read the bottom of the interval as a ceiling the "
                            "count is below"),
            "margin_to_estimate": (f"{dec(mc, 0)} < {sym} < {dec(ec, 0)}",
                                   Band(mc, ec),
                                   "ran the interval from the margin as a count "
                                   "up to the estimate as a count, instead of "
                                   "the margin either side of the estimate"),
            "estimate_to_upper": (f"{dec(ec, 0)} < {sym} < {dec(hi, 0)}",
                                  Band(ec, hi),
                                  "applied the margin of error on one side of "
                                  "the estimate only"),
            "above_estimate": (f"{sym} > {dec(ec, 0)}", Band(ec, None),
                               "read the estimate itself as a floor the count "
                               "is above"),
        }
        printed = []
        for name, (text, band, why) in pool.items():
            printed.append((name, text, Claim("count", "frame", "plausible", band), why))
        good = [p for p in printed if supported(st, p[2])]
        if len(good) != 1:
            raise ItemError(f"{len(good)} of the ranges this scene can print are "
                            f"plausible; the page needs exactly one")
        key = good[0]
        bad = [p for p in printed if p is not key]
        if wrongs is not None:
            byname = {p[0]: p for p in bad}
            for w in wrongs:
                if w == key[0]:
                    raise ItemError(f"{w!r} is the range this study leaves "
                                    f"plausible; it cannot be a wrong answer")
                if w not in byname:
                    raise ItemError(f"no range named {w!r}")
            bad = [byname[w] for w in wrongs]
        else:
            rng.shuffle(bad)
        choices, reasons, letter = assemble_text(
            key[1], [Mis(p[3], p[1]) for p in bad], rng)
        if len(set(choices)) != 4:
            raise ItemError("two options print the same range")
        why = (f"{dec(st.lo, 2)}% to {dec(st.hi, 2)}% of {N:,} is {dec(lo, 0)} to "
               f"{dec(hi, 0)}, so those are the plausible counts.")
        P = dict(kind="sstat.plausible_count", ctx=kit.key, form="range", N=N,
                 n=n, estimate=str(est), margin=str(moe), texts=list(choices),
                 sym=sym)
        return Item("sstat.plausible_count", "sample statistics and margin of error",
                    tier, seed, stem, "mcq", E(0), letter, why, choices, reasons,
                    list(choices), params=P)

    # ---- four counts, one of them inside the interval
    off = Q(0) if off is None else q(off)
    if abs(off) >= moe:
        raise ItemError("the keyed count has to sit inside the interval")
    key_v = _counts(N, est + off)
    pool = {
        "sample_yes": (f"gave the {kit.extra['trait'].split()[0]}ers inside the "
                       f"sample rather than inside the population",
                       _counts(n or 0, est)),
        "sample_no": (f"gave the members of the sample who "
                      f"{kit.extra['other']}", _counts(n or 0, 100 - est)),
        "pop_no": (f"gave a plausible count for the people who "
                   f"{kit.extra['other']}", _counts(N, 100 - est + off)),
        "margin_count": ("gave the margin of error as a count instead of a "
                         "plausible value", _counts(N, moe)),
        "outside_high": ("took a count above the interval, where the margin of "
                         "error stops", _counts(N, est + moe + 1)),
    }
    pool = {a: (w, v) for a, (w, v) in pool.items()
            if v is not None and q(v).denominator == 1 and q(v) > 0}
    order = ["sample_yes", "sample_no", "pop_no", "margin_count", "outside_high"]
    names = list(wrongs if wrongs is not None else order)
    mistakes = []
    for name in names:
        if name not in pool:
            raise ItemError(f"no count named {name!r} in this pool")
        mistakes.append(Mis(pool[name][0], Num(pool[name][1])))
    choices, latex, reasons, letter = assemble(Num(key_v), mistakes, rng)

    # every printed number is judged by the study, the key included
    inside = [c for c in choices
              if supported(st, Claim("count", "frame", "plausible",
                                     Only(q(c.replace(",", ""))), kind="member"))]
    if len(inside) != 1 or inside[0] != choices["ABCD".index(letter)]:
        raise ItemError(f"{len(inside)} of the four printed counts are plausible "
                        f"values; the page needs exactly one, and it must be the key")
    why = (f"{dec(st.lo, 2)}% to {dec(st.hi, 2)}% of {N:,} is {dec(lo, 0)} to "
           f"{dec(hi, 0)}, and {dec(key_v, 0)} is in that interval.")
    P = dict(kind="sstat.plausible_count", ctx=kit.key, form="value", N=N, n=n,
             estimate=str(est), margin=str(moe), texts=list(choices),
             key=str(key_v))
    return Item("sstat.plausible_count", "sample statistics and margin of error",
                tier, seed, stem, "mcq", Num(key_v), letter, why, choices,
                reasons, latex, params=P)


# --------------------------------------------- why one margin is bigger

DESIGNS = {
    "proposition": Kit(
        key="proposition", form="reason",
        stem="The results of two random samples of votes for a proposition are "
             "shown above. The samples were selected from the same population, "
             "and the margins of error were calculated using the same method. "
             "Which of the following is the most appropriate reason that the "
             "margin of error for sample {a} is {cmp} than the margin of error "
             "for sample {b}?",
        ranges=dict(pct=(38, 62), moe=(Q(6, 10), Q(6))),
        extra=dict(head=("Sample", "Percent in favor", "Margin of error"),
                   names=("A", "B"), thing="votes",
                   reasons=dict(
                       smaller_n="Sample {a} had a smaller sample size.",
                       larger_n="Sample {a} had a larger sample size.",
                       same_n="Sample {a} and sample {b} had the same sample size.",
                       higher_pct="Sample {a} had a higher percent of favorable "
                                  "responses.",
                       lower_pct="Sample {a} had a lower percent of favorable "
                                 "responses.",
                       fewer_lost="Sample {a} had a smaller number of votes that "
                                  "could not be recorded.",
                       confidence="Sample {a} was reported at a higher level of "
                                  "confidence."))),
    "flavor": Kit(
        key="flavor", form="reason",
        stem="The results of two random samples of shoppers asked about a new "
             "flavor are shown above. The samples were selected from the same "
             "population, and the margins of error were calculated using the "
             "same method. Which of the following is the most appropriate reason "
             "that the margin of error for sample {a} is {cmp} than the margin "
             "of error for sample {b}?",
        ranges=dict(pct=(30, 70), moe=(Q(5, 10), Q(7))),
        extra=dict(head=("Sample", "Percent in favor", "Margin of error"),
                   names=("P", "Q"), thing="responses",
                   reasons=dict(
                       smaller_n="Sample {a} had a smaller sample size.",
                       larger_n="Sample {a} had a larger sample size.",
                       same_n="Sample {a} and sample {b} had the same sample size.",
                       higher_pct="Sample {a} had a higher percent of favorable "
                                  "responses.",
                       lower_pct="Sample {a} had a lower percent of favorable "
                                 "responses.",
                       fewer_lost="Sample {a} had a smaller number of responses "
                                  "that could not be recorded.",
                       confidence="Sample {a} was reported at a higher level of "
                                  "confidence."))),
}

# What settles a margin of error, once the stem has fixed the method and the
# population: the size of the sample, and nothing else the page offers. So a
# reason is right exactly when it states the size comparison the two printed
# margins imply, and every reason naming the statistic, the lost responses or
# the confidence level is ruled out by the stem's own "the same method".
SIZE_RULE = {"smaller_n": 1, "larger_n": -1, "same_n": 0}


def _reason_holds(name: str, ma: Q, mb: Q) -> bool:
    """Is this sentence the reason the two printed margins give?"""
    if name not in SIZE_RULE:
        return False               # the stem fixes the method, so nothing else moves
    sign = 0 if ma == mb else (1 if ma > mb else -1)
    return SIZE_RULE[name] == sign


def margin_size(rng: random.Random, seed: int, *, ctx=None, pcts=None, moes=None,
                wrongs=None, tier="hard") -> Item:
    """Two samples of the same population; why is one margin bigger?

    Both the stem's comparison and the answer are read off the two printed
    margins, so they cannot disagree: swap the margins in the table and the
    stem says "less" where it said "greater" and the key moves with it.
    """
    kit = DESIGNS[ctx] if ctx is not None else DESIGNS[rng.choice(sorted(DESIGNS))]
    e, r = kit.extra, kit.ranges
    if pcts is None:
        pa = Q(rng.randint(*r["pct"]))
        pb = Q(rng.randint(*r["pct"]))
    else:
        pa, pb = (q(v) for v in pcts)
    if moes is None:
        lo, hi = r["moe"]
        step = Q(1, 10)
        ma = q(lo) + rng.randint(0, int((q(hi) - q(lo)) / step)) * step
        mb = q(lo) + rng.randint(0, int((q(hi) - q(lo)) / step)) * step
    else:
        ma, mb = (q(v) for v in moes)
    if ma == mb:
        raise ItemError("the item is about a difference between the two margins")
    if pa == pb:
        raise ItemError("two samples reporting the same percent read as a misprint")
    for m, p in ((ma, pa), (mb, pb)):
        if m <= 0 or p - m <= 0 or p + m >= 100:
            raise ItemError("each interval has to sit inside 0% and 100%")

    a, b = e["names"]
    cmp_word = "greater" if ma > mb else "less"
    table = [list(e["head"]),
             [a, f"{dec(pa, 0) if pa.denominator == 1 else dec(pa, 1)}%",
              f"{dec(ma, 1)}%"],
             [b, f"{dec(pb, 0) if pb.denominator == 1 else dec(pb, 1)}%",
              f"{dec(mb, 1)}%"]]
    stem = tidy(kit.stem.format(a=a, b=b, cmp=cmp_word))

    texts = {nm: t.format(a=a, b=b) for nm, t in e["reasons"].items()}
    whys = {
        "smaller_n": "inverted the relationship: a smaller sample gives a wider "
                     "margin of error, not a narrower one",
        "larger_n": "inverted the relationship: a larger sample gives a narrower "
                    "margin of error, not a wider one",
        "same_n": "read two different margins as coming from samples of the same "
                  "size, when the size is the only thing the stem leaves free",
        "higher_pct": "read the margin off the statistic, when the stem fixes the "
                      "method and leaves only the sample size free",
        "lower_pct": "read the margin off the statistic, when the stem fixes the "
                     "method and leaves only the sample size free",
        "fewer_lost": f"looked for the difference in the {e['thing']} that were "
                      f"lost rather than in the size of the sample",
        "confidence": "reached for the confidence level, which does widen an "
                      "interval but which the stem has already fixed",
    }
    good = [nm for nm in texts if _reason_holds(nm, ma, mb)]
    if len(good) != 1:
        raise ItemError(f"{len(good)} of the reasons hold for these two margins")
    key = good[0]
    bad = [nm for nm in texts if nm != key]
    if wrongs is not None:
        for w in wrongs:
            if w == key:
                raise ItemError(f"{w!r} is the reason these margins give; it "
                                f"cannot be printed as a wrong answer")
            if w not in texts:
                raise ItemError(f"no reason named {w!r}")
        bad = list(wrongs)
    else:
        rng.shuffle(bad)
        bad = bad[:3]
    choices, reasons, letter = assemble_text(
        texts[key], [Mis(whys[nm], texts[nm]) for nm in bad], rng)
    if len(set(choices)) != 4:
        raise ItemError("two options print the same reason")
    bigger, smaller = (a, b) if ma > mb else (b, a)
    why = (f"The two margins were found the same way from the same population, "
           f"so the only thing that can differ is the size of the sample. "
           f"Sample {bigger} has the wider margin, so sample {bigger} is the "
           f"smaller sample and sample {smaller} is the larger one.")
    P = dict(kind="sstat.margin_size", ctx=kit.key, pa=str(pa), pb=str(pb),
             ma=str(ma), mb=str(mb), names=[a, b], texts=list(choices))
    return Item("sstat.margin_size", "sample statistics and margin of error",
                tier, seed, stem, "mcq", E(0), letter, why, choices, reasons,
                list(choices), table=table, params=P)
