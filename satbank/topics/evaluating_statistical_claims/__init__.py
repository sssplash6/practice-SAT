"""Problem-Solving and Data Analysis -> Evaluating Statistical Claims.

Six templates over the 11 official items. Every item here is a sentence-valued
question, so the whole difficulty is that the answer must be *derived* rather
than written down: this topic was built twice before on a predicate that
matched the answer's text, and on a `correct_id` parameter that named it, and
both passed the full gate while reasoning about nothing.

So no file in this package -- not a template, not `sources.py`, not `audit.py`,
not `option_check.py` -- states which option is correct. Each template is given
a study: the population, the sampling frame, the method, whether there was
random assignment, and what was reported. It renders that study into the stem
and then works out which of the printed options the study supports, under four
rules:

* generalization reaches the frame the units were randomly selected from, and
  no further (`families/scope.py`);
* a causal claim needs random assignment, not merely random selection
  (`families/conclude.py`);
* a self-selected or convenience sample earns neither, and supports only a
  statement about the method (`families/method.py`);
* one sample estimates a population value and does not fix it, so a "must be
  true" claim that the percentage holds exactly, or repeats, is false
  (`families/claims.py`).

Because the stem is rendered from the same study the answer is derived from,
the two cannot disagree: changing the frame changes the printed stem and moves
the key with it, and a `wrongs=` list that names the licensed option is
refused rather than keyed.
"""

from __future__ import annotations

from ...topic import Topic
from .audit import AUDITS
from .families import claims as C
from .families import conclude as K
from .families import method as M
from .families import scope as G
from .families import supply as U
from .sources import ALL, EXCLUDED

TEMPLATES = {
    "esc.study_conclusion_supply": U.study_conclusion,
    "esc.sampling_method_supply": U.sampling_method,
    "esc.generalize": G.generalize,
    "esc.generalize_table": G.generalize_table,
    "esc.must_be_true": C.must_be_true,
    "esc.inference": C.inference,
    "esc.sample_quality": M.sample_quality,
    "esc.conclusion": K.conclusion,
}

TOPIC = Topic(
    slug="evaluating_statistical_claims",
    name="Evaluating Statistical Claims",
    domain="Problem-Solving and Data Analysis",
    templates=TEMPLATES,
    audits=AUDITS,
    sources=ALL,
    excluded=EXCLUDED,
)
