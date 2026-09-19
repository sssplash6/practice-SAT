"""What a study supports, worked out from the study.

This is the whole of the topic's reasoning, and it is the reason nothing in
this package ever writes down which option is correct. A template is handed a
**study** -- how the units were chosen, from what population, how many, what
was estimated and with what margin, and whether the stem gives the size of
the population. It renders that study into the stem, renders a set of
**claims** into the four options, and then asks this module which of the
printed claims the study supports. Whatever comes back is the key.

Move any part of the study and the page moves with it. Take the margin away
and the interval claims stop being supported and the "approximately" claim
starts. Take the randomness away and the population is no longer reported at
all, so "no conclusion can be made" becomes the answer. Give the stem the
population's size and a claim about a *count* becomes readable; leave it out
and the same sentence is unsupported -- which is the whole difference between
official item 2.7 and official item 1.4, from one rule rather than two.

## The rule

`reports(study)` is a dict from `(aspect, population)` to a `Report`. Those
keys are the only things the study says anything about:

    ("parameter", "frame")   plausible over [E-M, E+M]   -- a random sample
                             approximate at {E}          -- no margin stated
    ("count", "frame")       the same, scaled by the population size, and
                             present only when the stem states that size
    ("statistic", "sample")  certain at {E} -- what was actually measured

Individuals, misclassification, a wider population than the one sampled, and
every population parameter under a self-selected sample are simply absent.

A printed option is a `Claim(aspect, population, modality, vset)`, and

    supported(study, claim) iff  (aspect, population) is reported
                            and  the claim's modality is no stronger than
                                 the report's
                            and  the report's value-set is contained in the
                                 claim's.

Containment is the part that does the statistics. "The parameter is E" asserts
the single value E, which does not contain the interval, so a point estimate
is never a conclusion. "It is not possible that the parameter is below L"
contains the interval but asks for certainty, which a sample never gives.
"It is doubtful that the parameter is V" asserts everything except V, which
contains the interval exactly when V is outside it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction as Q

from .values import q

__all__ = ["Band", "Only", "Not", "Outside", "Claim", "Report", "Study",
           "reports", "supported", "MODALITY", "contains"]

# weakest first. A claim may not ask for more confidence than the study gives.
MODALITY = {"approximate": 0, "plausible": 1, "certain": 2}


# ------------------------------------------------------------- value sets

@dataclass(frozen=True)
class Band:
    """A closed interval. `lo` None is unbounded below, `hi` None above.

    Closed on purpose: the page writes the same interval three ways --
    "between 1,300 and 1,700", "1,300 < r < 1,700", "from 1,300 to 1,700" --
    and whether the endpoint is in or out is typography rather than
    statistics. Reading them all as closed means the three spellings are one
    claim, which is what a student reads them as.
    """
    lo: Q | None
    hi: Q | None


@dataclass(frozen=True)
class Only:
    """A single value."""
    v: Q


@dataclass(frozen=True)
class Not:
    """Everything except one value -- what "it is doubtful that it is V" says."""
    v: Q


@dataclass(frozen=True)
class Outside:
    """Everything below `lo` or above `hi` -- the interval turned inside out."""
    lo: Q
    hi: Q


def _ge(a, b) -> bool:      # a >= b, with None as +infinity on the left
    return True if a is None else (False if b is None else a >= b)


def _le(a, b) -> bool:      # a <= b, with None as -infinity on the left
    return True if a is None else (False if b is None else a <= b)


def contains(outer, inner) -> bool:
    """Is every value of `inner` a value of `outer`?"""
    if isinstance(outer, Band):
        if isinstance(inner, Band):
            return _le(outer.lo, inner.lo) and _ge(outer.hi, inner.hi)
        if isinstance(inner, Only):
            return _le(outer.lo, inner.v) and _ge(outer.hi, inner.v)
        return outer.lo is None and outer.hi is None      # only all of R holds Not(v)
    if isinstance(outer, Only):
        if isinstance(inner, Only):
            return outer.v == inner.v
        if isinstance(inner, Band):
            return inner.lo is not None and inner.lo == inner.hi == outer.v
        return False
    if isinstance(outer, Outside):
        if isinstance(inner, Only):
            return inner.v < outer.lo or inner.v > outer.hi
        if isinstance(inner, Band):
            if inner.hi is not None and inner.hi < outer.lo:
                return True
            return inner.lo is not None and inner.lo > outer.hi
        return False
    if isinstance(outer, Not):
        if isinstance(inner, Only):
            return inner.v != outer.v
        if isinstance(inner, Band):
            if inner.lo is None or inner.hi is None:
                return False
            return outer.v < inner.lo or outer.v > inner.hi
        return outer.v == inner.v
    raise TypeError(f"not a value set: {outer!r}")


# ------------------------------------------------------------- the records

@dataclass(frozen=True)
class Report:
    modality: str
    vset: object


@dataclass(frozen=True)
class Claim:
    """What one printed sentence asserts.

    `aspect` is what the sentence is about -- the population parameter, the
    number of members with the trait, the value each individual takes, the
    statistic the sample itself produced, or something the study never
    measured. `pop` is which group: the one sampled from, a wider one, the
    sample, or another group entirely.
    """
    aspect: str                 # parameter | count | individuals | statistic | other
    pop: str                    # frame | wider | sample | other
    modality: str               # approximate | plausible | certain
    vset: object = None
    kind: str = "value"         # value | member | no_conclusion


@dataclass
class Study:
    """The page, as data.

    `estimate` and `margin` are exact and are in the units the stem prints:
    percentage points for a percent, the measure's own units for a mean, a
    bare fraction of one for a proportion.
    """
    quantity: str                       # percent | proportion | mean
    estimate: Q
    margin: Q | None = None
    n: int = 0
    random: bool = True
    size: int | None = None             # the population's size, when the stem says
    extra: dict = field(default_factory=dict)

    @property
    def lo(self) -> Q:
        return q(self.estimate) - q(self.margin)

    @property
    def hi(self) -> Q:
        return q(self.estimate) + q(self.margin)


def _per(quantity: str) -> Q:
    """What one unit of the estimate is worth as a share of the population."""
    return Q(1, 100) if quantity == "percent" else Q(1)


def reports(st: Study) -> dict[tuple[str, str], Report]:
    """Everything the study says, and nothing else. See the module note."""
    out: dict[tuple[str, str], Report] = {
        ("statistic", "sample"): Report("certain", Only(q(st.estimate))),
    }
    if not st.random:
        # a sample that selected itself speaks for nobody but itself
        return out
    if st.margin is None:
        out[("parameter", "frame")] = Report("approximate", Only(q(st.estimate)))
        if st.size is not None and st.quantity in ("percent", "proportion"):
            out[("count", "frame")] = Report(
                "approximate", Only(st.size * q(st.estimate) * _per(st.quantity)))
        return out
    out[("parameter", "frame")] = Report("plausible", Band(st.lo, st.hi))
    if st.size is not None and st.quantity in ("percent", "proportion"):
        scale = st.size * _per(st.quantity)
        out[("count", "frame")] = Report("plausible", Band(st.lo * scale, st.hi * scale))
    return out


def supported(st: Study, claim: Claim) -> bool:
    """Does the study support this sentence? The one rule, and nothing else."""
    rep = reports(st)
    if claim.kind == "no_conclusion":
        # "no conclusion can be made about the population" is right exactly
        # when the study reports nothing about the population
        return ("parameter", "frame") not in rep
    r = rep.get((claim.aspect, claim.pop))
    if r is None:
        return False
    if MODALITY[claim.modality] > MODALITY[r.modality]:
        return False
    if claim.kind == "member":
        # "which of the following is a plausible value" asks the other
        # question: not whether the sentence covers everything the study
        # licenses, but whether the one value it names is among them
        return contains(r.vset, claim.vset)
    return contains(claim.vset, r.vset)


# A `member` claim -- "which of the following is a plausible value for the
# count" -- reverses the containment: the sentence names one value and asks
# whether the study leaves it plausible, rather than asserting a set that has
# to cover everything the study leaves plausible. Both readings are in
# `supported`, chosen by `Claim.kind`, because the page asks both questions:
# official item 2.4 prints intervals ("1,300 < r < 1,700") and official item
# 2.7 prints single numbers, from the very same report.
