"""Every sentence this topic can print about a margin of error, and what it says.

A builder here turns a scene and a study into three things: the sentence a
student reads, the `Claim` that sentence asserts, and the mistake a student
makes by choosing it. It never decides whether the sentence is right --
`study.supported` does that, from the study, and a builder cannot see the
answer even in principle because it is not told which study it will be run
against.

The four confusions this catalogue exists to hold apart, in a teacher's words:

* **the margin is an interval, not a bound.** "It is not possible that the
  value is below L" is a claim of certainty, and a sample never gives one.
* **the margin describes the population parameter**, not the sample and not
  any one member of the population. An interval around a mean says nothing
  about how far a single visitor hiked.
* **a larger sample narrows the interval** and a higher confidence level
  widens it -- so a margin is a fact about the design, not about the answer.
* **the statistic is a point estimate**, so "the value *is* E" is false even
  though E is the number the study reported.

A spec is a name, optionally with a value: ``"doubtful:35"`` prints "It is
doubtful that ... is 35%". The value is read as an exact decimal in the units
the stem prints.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q

from ...item import ItemError
from .study import Band, Claim, Not, Only, Outside, Study
from .values import dec, q

__all__ = ["Printed", "build", "catalogue", "NAMES"]


@dataclass(frozen=True)
class Printed:
    name: str
    text: str
    claim: Claim
    why: str            # the mistake this option is made of; blank is never used


def _arg(sc, spec: str):
    base, _, tail = spec.partition(":")
    if not tail:
        return base, None
    return base, q(Q(tail))


def _floor(v: Q) -> Q:
    return Q(v.numerator // v.denominator)


# --------------------------------------------------------------- the builders
#
# Each takes (scene, study, value) and returns (text, Claim, why).

def _interval(sc, st, v):
    lo, hi = st.lo, st.hi
    pair = sc.pair(lo, hi)
    if sc.style == "plausible_values":
        text = f"Plausible values of {sc.subject_lc} are between {pair}."
    elif sc.style == "it_is_plausible":
        text = f"It is plausible that {sc.subject_lc} is between {pair}."
    elif sc.style == "between_pop":
        text = f"Between {pair} of {sc.pop_all} {sc.trait}."
    else:
        text = f"{sc.subject} is between {pair}."
    return text, Claim("parameter", "frame", "plausible", Band(lo, hi)), \
        ("read the margin of error as though the sample spoke for the whole "
         "population, when this sample was not selected at random")


def _point(sc, st, v):
    return (f"{sc.subject} is {sc.one(st.estimate)}.",
            Claim("parameter", "frame", "plausible", Only(q(st.estimate))),
            "gave the sample's estimate as the population's value, when one "
            "sample can only estimate it")


def _point_exact(sc, st, v):
    return (f"{sc.subject} is exactly {sc.one(st.estimate)}.",
            Claim("parameter", "frame", "certain", Only(q(st.estimate))),
            "read a point estimate as an exact population value, which no single "
            "sample can settle")


def _point_upper(sc, st, v):
    return (f"{sc.subject} is {sc.one(st.hi)}.",
            Claim("parameter", "frame", "plausible", Only(st.hi)),
            "took the top of the interval as the population's value, rather than "
            "as the largest value the margin makes plausible")


def _point_lower(sc, st, v):
    return (f"{sc.subject} is {sc.one(st.lo)}.",
            Claim("parameter", "frame", "plausible", Only(st.lo)),
            "took the bottom of the interval as the population's value, rather "
            "than as the smallest value the margin makes plausible")


def _greater_est(sc, st, v):
    return (f"{sc.subject} is greater than {sc.one(st.estimate)}.",
            Claim("parameter", "frame", "plausible", Band(q(st.estimate), None)),
            "read the margin of error as though it could only push the value up "
            "from the estimate")


def _less_est(sc, st, v):
    return (f"{sc.subject} is less than {sc.one(st.estimate)}.",
            Claim("parameter", "frame", "plausible", Band(None, q(st.estimate))),
            "read the margin of error as though it could only pull the value down "
            "from the estimate")


def _outside(sc, st, v):
    # a unit goes on both endpoints wherever the scene puts one on each --
    # "less than 27 or greater than 37%" was printing the per-cent sign on
    # the second number alone
    lo = sc.one(st.lo) if sc.unit_each else sc.num(st.lo)
    return (f"{sc.subject} is less than {lo} or greater than "
            f"{sc.one(st.hi)}.",
            Claim("parameter", "frame", "plausible", Outside(st.lo, st.hi)),
            "turned the interval inside out and ruled out exactly the values the "
            "margin of error makes plausible")


def _more_than_upper(sc, st, v):
    return (f"More than {sc.one(st.hi)} of {sc.pop_all} {sc.trait}.",
            Claim("parameter", "frame", "plausible", Band(st.hi, None)),
            "read the top of the interval as a floor the population is above, "
            "rather than as the highest plausible value")


def _less_than_lower(sc, st, v):
    return (f"Fewer than {sc.one(st.lo)} of {sc.pop_all} {sc.trait}.",
            Claim("parameter", "frame", "plausible", Band(None, st.lo)),
            "read the bottom of the interval as a ceiling the population is "
            "below, rather than as the lowest plausible value")


def _not_possible_below(sc, st, v):
    return (f"It is not possible that {sc.subject_lc} is less than "
            f"{sc.one(st.lo)}.",
            Claim("parameter", "frame", "certain", Band(st.lo, None)),
            "read the margin as a bound rather than as an interval of plausible "
            "values -- a sample rules nothing out")


def _not_possible_above(sc, st, v):
    return (f"It is not possible that {sc.subject_lc} is greater than "
            f"{sc.one(st.hi)}.",
            Claim("parameter", "frame", "certain", Band(None, st.hi)),
            "read the margin as a bound rather than as an interval of plausible "
            "values -- a sample rules nothing out")


def _doubtful(sc, st, v):
    if v is None:
        raise ItemError("a doubtful-value claim needs the value it doubts")
    inside = st.margin is not None and st.lo <= v <= st.hi
    why = ("called a value doubtful although it sits inside the interval the "
           "margin of error makes plausible" if inside else
           "doubted a value on the strength of a sample that was never drawn "
           "at random")
    return (f"It is doubtful that {sc.subject_lc} is {sc.one(v)}.",
            Claim("parameter", "frame", "plausible", Not(v)), why)


def _plausible_below(sc, st, v):
    return (f"It is plausible that {sc.subject_lc} is less than {sc.one(st.lo)}.",
            Claim("parameter", "frame", "plausible", Band(None, st.lo)),
            "offered a value below the interval as plausible, though the margin "
            "of error is where the plausible values stop")


def _plausible_above(sc, st, v):
    return (f"It is plausible that {sc.subject_lc} is greater than {sc.one(st.hi)}.",
            Claim("parameter", "frame", "plausible", Band(st.hi, None)),
            "offered a value above the interval as plausible, though the margin "
            "of error is where the plausible values stop")


def _count_from_sample(sc, st, v):
    # a headcount, so it prints as a whole number with its thousands
    # separator -- not through the scene's own `num`, which carries the
    # decimal places the *measure* is printed to. A proportion scene fixes
    # two places, and reading a count through it printed "between 280.00 and
    # 280.00": the wrong surface and, because a margin below 1 floors to
    # nothing, a range with no width.
    m = _floor(q(st.margin))
    if st.n <= 0 or m <= 0:
        raise ItemError("this study's margin does not reach a whole member of "
                        "the sample, so there is no such range to misread")
    lo, hi = Q(st.n) - m, Q(st.n) + m
    if lo <= 0:
        raise ItemError("the misread range would run below zero")
    return (f"Plausible values of {sc.count_np} are between {dec(lo, 0)} and "
            f"{dec(hi, 0)}.",
            Claim("count", "frame", "plausible", Band(lo, hi)),
            "applied the margin of error to the size of the sample instead of to "
            "the estimate it belongs to")


def _individuals(sc, st, v):
    return (f"{sc.indiv} are between {sc.pair(st.lo, st.hi)}.",
            Claim("individuals", "frame", "plausible", Band(st.lo, st.hi)),
            f"applied the margin to the individual {sc.members} rather than to "
            f"the population value the study estimated")


def _individuals_sample(sc, st, v):
    return (f"{sc.indiv_sample} are between {sc.pair(st.lo, st.hi)}.",
            Claim("individuals", "sample", "plausible", Band(st.lo, st.hi)),
            f"applied the margin to the {sc.members} that were measured rather "
            f"than to the population value the study estimated")


def _all_individuals(sc, st, v):
    return (f"It is likely that all {sc.members} {sc.did} between "
            f"{sc.pair(st.lo, st.hi)}.",
            Claim("individuals", "frame", "plausible", Band(st.lo, st.hi)),
            f"read the interval as holding for every {sc.member} rather than for "
            f"the mean of all of them")


def _most_exactly(sc, st, v):
    return (f"It is likely that most {sc.members} {sc.did} exactly "
            f"{sc.one(st.estimate)}.",
            Claim("individuals", "frame", "certain", Only(q(st.estimate))),
            f"read the estimated mean as the value most {sc.members} actually "
            f"have, which is what a mean is not")


def _none_below(sc, st, v):
    if v is None:
        raise ItemError("a none-below claim needs the value nothing falls under")
    return (f"It is not possible that any {sc.member} {sc.did} less than "
            f"{sc.one(v)}.",
            Claim("individuals", "frame", "certain", Band(v, None)),
            f"read the margin as ruling out {sc.members} below it, though it "
            f"describes the mean and not any one {sc.member}")


def _error_rate(sc, st, v):
    return (f"Approximately {sc.one(st.margin)} of the {sc.members} in the study "
            f"who are classified as {sc.label} are not really {sc.label}.",
            Claim("misclassification", "sample", "approximate", Only(q(st.margin))),
            "read the margin of error as the share of the sample that was put in "
            "the wrong group")


def _approx_frame(sc, st, v):
    return (f"Approximately {sc.one(st.estimate)} of {sc.pop_all} {sc.trait}.",
            Claim("parameter", "frame", "approximate", Only(q(st.estimate))),
            "generalized from a sample that chose itself, which speaks for "
            "nobody but the units in it")


def _approx_wider(sc, st, v):
    return (f"Approximately {sc.one(st.estimate)} of {sc.extra['wider_all']} "
            f"{sc.trait}.",
            Claim("parameter", "wider", "approximate", Only(q(st.estimate))),
            f"applied a statistic measured on {sc.pop_all} to "
            f"{sc.extra['wider_all']}, a group it was never measured on")


def _wider_majority(sc, st, v):
    return (sc.extra["wider_claims"]["majority"],
            Claim("parameter", "wider", "plausible", Band(Q(50), None)),
            f"answered about {sc.extra['wider_all']}, and about a different "
            f"measurement again, when the study measured {sc.pop_all}")


def _wider_mean(sc, st, v):
    return (sc.extra["wider_claims"]["mean"],
            Claim("parameter", "wider", "approximate", Only(q(st.estimate))),
            f"read a percent measured on {sc.pop_all} as an average for "
            f"{sc.extra['wider_all']}")


def _no_conclusion_a(sc, st, v):
    return (sc.extra["no_conc"][0],
            Claim("parameter", "frame", "plausible", None,
                  kind="no_conclusion", ground="mixed_sample"),
            "refused the conclusion because the sample held members without the "
            "trait as well as members with it, which is what a sample has to "
            "hold to measure anything")


def _no_conclusion_b(sc, st, v):
    return (sc.extra["no_conc"][1],
            Claim("parameter", "frame", "plausible", None,
                  kind="no_conclusion", ground="not_exhaustive"),
            "asked the sample to be the whole population before it may be used, "
            "which would refuse every inference ever drawn from a sample")


def _no_conclusion_self(sc, st, v):
    return (sc.extra["no_conc_self"],
            Claim("parameter", "frame", "plausible", None,
                  kind="no_conclusion", ground="not_random"),
            "refused a conclusion a randomly selected sample does support")


BUILDERS = {
    "interval": _interval,
    "no_conclusion_self": _no_conclusion_self,
    "point": _point,
    "point_exact": _point_exact,
    "point_upper": _point_upper,
    "point_lower": _point_lower,
    "greater_est": _greater_est,
    "less_est": _less_est,
    "outside": _outside,
    "more_than_upper": _more_than_upper,
    "less_than_lower": _less_than_lower,
    "not_possible_below": _not_possible_below,
    "not_possible_above": _not_possible_above,
    "doubtful": _doubtful,
    "plausible_below": _plausible_below,
    "plausible_above": _plausible_above,
    "count_from_sample": _count_from_sample,
    "individuals": _individuals,
    "individuals_sample": _individuals_sample,
    "all_individuals": _all_individuals,
    "most_exactly": _most_exactly,
    "none_below": _none_below,
    "error_rate": _error_rate,
    "approx_frame": _approx_frame,
    "approx_wider": _approx_wider,
    "wider_majority": _wider_majority,
    "wider_mean": _wider_mean,
    "no_conclusion_a": _no_conclusion_a,
    "no_conclusion_b": _no_conclusion_b,
}

NAMES = tuple(BUILDERS)

# which names a scene can print, by what the scene's vocabulary supplies
NEEDS = {
    "individuals": "indiv", "individuals_sample": "indiv_sample",
    "all_individuals": "did", "most_exactly": "did", "none_below": "did",
    "error_rate": "label", "more_than_upper": "trait",
    "less_than_lower": "trait", "count_from_sample": "count_np",
}
EXTRA_NEEDS = {"no_conclusion_a": "no_conc", "no_conclusion_b": "no_conc",
               "no_conclusion_self": "no_conc_self", "approx_wider": "wider_all",
               "wider_majority": "wider_claims", "wider_mean": "wider_claims"}


# a sentence that prints an endpoint cannot be written without a margin
# "More than 35% of all adults who own televisions use ..." counts members of
# a population, so it is a sentence about a percent. A mean has no such
# reading -- the anonymous scene printed "More than 62 of the population are
# in the population" before this was here -- and a proportion between 0 and 1
# does not either.
WANTS_PERCENT = frozenset({"more_than_upper", "less_than_lower"})

# two sentences that say the same wrong thing, differing only by the word
# "exactly". Printing both wastes an option and reads as a misprint.
CONFLICT = (frozenset({"point", "point_exact"}),)

WANTS_MARGIN = frozenset({
    "interval", "point_upper", "point_lower", "outside", "more_than_upper",
    "less_than_lower", "not_possible_below", "not_possible_above",
    "plausible_below", "plausible_above", "count_from_sample", "individuals",
    "individuals_sample", "all_individuals", "error_rate"})


def build(sc, st: Study, spec: str) -> Printed:
    """One printed option, from a scene, a study and a spec."""
    base, v = _arg(sc, spec)
    fn = BUILDERS.get(base)
    if fn is None:
        raise ItemError(f"no claim named {base!r}")
    if base in WANTS_MARGIN and st.margin is None:
        raise ItemError(f"{base!r} prints an endpoint and this study has no margin")
    if base in WANTS_PERCENT and sc.quantity != "percent":
        raise ItemError(f"{base!r} counts members of a population and only a "
                        f"percent reads that way")
    need = NEEDS.get(base)
    if need and not getattr(sc, need):
        raise ItemError(f"scene {sc.key!r} has no wording for {base!r}")
    need = EXTRA_NEEDS.get(base)
    if need and need not in sc.extra:
        raise ItemError(f"scene {sc.key!r} has no wording for {base!r}")
    text, claim, why = fn(sc, st, v)
    if "  " in text or not text.endswith("."):
        raise ItemError(f"the claim {spec!r} did not render as a sentence: {text!r}")
    return Printed(spec, text, claim, why)


def catalogue(sc, st: Study, specs) -> list[Printed]:
    out = [build(sc, st, s) for s in specs]
    if len({p.text for p in out}) != len(out):
        raise ItemError("two of the printed options are the same sentence")
    bases = {s.partition(":")[0] for s in specs}
    for pair in CONFLICT:
        if pair <= bases:
            raise ItemError(f"{sorted(pair)} say the same thing twice")
    return out
