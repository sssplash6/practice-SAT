"""Problem-Solving and Data Analysis -> Sample Statistics and Margin of Error.

Twelve templates over the 18 official items. Half of them answer with a
number -- a sample statistic scaled up to the population it came from -- and
half answer with a sentence about what an estimate and its margin of error
do and do not license. The second half is where the topic is hard, and it is
built the way `evaluating_statistical_claims` is built: **nothing states
which option is correct.**

`study.py` holds the whole of the reasoning. A template is handed a study --
how the units were chosen, how many, what was estimated, with what margin,
and whether the page states the size of the population -- renders that study
into the stem, renders four claims into four sentences, and then asks
`study.supported` which of the four the study licenses. Exactly one must, or
the draw is refused. Move any part of the study and the page moves with it:
take the margin away and the interval claims stop holding; take the
randomness away and nothing about the population is licensed at all, so "no
conclusion can be made" becomes the answer; state the population's size and
a claim about a *count* becomes readable, which is the only difference
between official item 2.7, where such a claim is the key, and official item
1.4, where the same shape of sentence is a distractor.

The four confusions the topic exists to separate are the distractor pool,
and each one falls out of the rule rather than being asserted:

* the interval is **plausible, not certain** -- a claim carrying "it is not
  possible", "must" or "exactly" asks for a confidence a sample never gives;
* the margin describes the **population parameter**, not the sample and not
  individuals -- those are not things the study reports at all;
* a **larger sample narrows** the interval, and the stem's "the same method"
  closes off every other explanation (`sstat.margin_size`);
* the statistic is a **point estimate**, so "the value is E" is false even
  though E is the number the study reported.

`audit.py` writes the rule out a second time, over its own value sets, and
takes the printed sentences apart with its own patterns. `option_check.py`
writes it a third time and reads the numbers off the printed **stem** rather
than out of `item.params`.
"""

from __future__ import annotations

from ...topic import Topic
from .audit import AUDITS
from .families import design as D
from .families import estimate as E
from .families import interpret as I
from .sources import ALL, EXCLUDED

TEMPLATES = {
    "sstat.scale_count": E.scale_count,
    "sstat.scale_group": E.scale_group,
    "sstat.scale_range": E.scale_range,
    "sstat.scale_two_way": E.scale_two_way,
    "sstat.scale_frequency": E.scale_frequency,
    "sstat.interpret_mean": I.interpret_mean,
    "sstat.interpret_percent": I.interpret_percent,
    "sstat.interpret_table": I.interpret_table,
    "sstat.subgroup_claim": I.subgroup_claim,
    "sstat.count_claim": I.count_claim,
    "sstat.plausible_count": D.plausible_count,
    "sstat.margin_size": D.margin_size,
}

TOPIC = Topic(
    slug="sample_statistics_and_margin_of_error",
    name="Sample Statistics and Margin of Error",
    domain="Problem-Solving and Data Analysis",
    templates=TEMPLATES,
    audits=AUDITS,
    sources=ALL,
    excluded=EXCLUDED,
)
