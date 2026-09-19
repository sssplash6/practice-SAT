"""The four sentences of a scaled-up count: certain or estimated, right or wrong.

Two axes, and the study settles both. A sample of {k} out of {n} scales up to
`size * k / n`, which is the only count the study points at -- and it points
at it *approximately*, because one sample estimates a population value and
does not fix it. So a sentence saying the count **must** be that number asks
for a certainty a sample never provides, and a sentence naming a different
number is about a value the study never reported.

Neither fact is written down here. Both come out of `study.supported`: the
"must" sentences carry the `certain` modality against an `approximate`
report, and the wrong-value sentences carry a value the report does not hold.
"""

from __future__ import annotations

from ...item import ItemError
from .claims import Printed
from .study import Claim, Only
from .values import Q, dec

__all__ = ["count_specs", "SPECS"]

SPECS = ("best_right", "best_wrong", "must_right", "must_wrong")

WHY = {
    "best_wrong": "divided the population by the number of {members} in the "
                  "sample with the trait instead of scaling by the share of the "
                  "sample that had it",
    "must_right": "read a scaled-up estimate as a count the sample makes "
                  "certain, when one sample only estimates it",
    "must_wrong": "divided instead of scaling, and then read the result as a "
                  "count the sample makes certain",
}


def _count(sc, st, v, certain: bool, why: str) -> Printed:
    text = (sc.extra["must"] if certain else sc.extra["best"]).format(
        v=dec(v, 0))
    return Printed("must" if certain else "best", text,
                   Claim("count", "frame", "certain" if certain else "approximate",
                         Only(Q(v))), why)


def count_specs(sc, st, right, other, options=None):
    """The four printed sentences, and the specs that name them."""
    specs = list(options) if options is not None else list(SPECS)
    if len(specs) != 4 or len(set(specs)) != 4:
        raise ItemError("this template prints its four sentences once each")
    vals = {"right": Q(right), "wrong": Q(other)}
    out = []
    for spec in specs:
        head, _, which = spec.partition("_")
        if head not in ("best", "must") or which not in vals:
            raise ItemError(f"no count sentence named {spec!r}")
        why = WHY.get(spec, "").format(members=sc.members)
        out.append(_count(sc, st, vals[which], head == "must", why))
    if len({p.text for p in out}) != 4:
        raise ItemError("two of the four count sentences print the same")
    return specs, out
