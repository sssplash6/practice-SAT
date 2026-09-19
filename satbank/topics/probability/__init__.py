"""Problem-Solving and Data Analysis -> Probability.

Sixteen templates over the 36 official items. Two thirds of the set reads a
printed table, and the sharp edge throughout is the denominator: "given that"
turns P(A and B) into P(A|B), and choosing P(B|A) instead is both the mistake
the items exist to test and the mistake an engine can make without anybody
noticing, because the audit would re-derive the same wrong thing.

So the arithmetic is arranged to make that impossible rather than unlikely.
`world.py` builds a table from its cells alone and derives every margin; a
question is an event and a condition, each a set of cells; and the value is
always

    count(event and condition) / count(condition)

with the condition the whole table when the question is unconditional. No
template picks a numerator and a denominator, so there is no line of code in
which the wrong denominator could be written. The reversed conditional is a
named member of every conditional pool -- `reverse` -- and prints as a wrong
answer with the teacher's sentence beside it.

Three further rules the topic keeps:

* **Exactness.** Every count and every probability is a `fractions.Fraction`
  from the cell to the page. `values.PVal` carries the exact value *and* the
  string printed for it, because the College Board prints the same number as
  10/40, as 1/4, as 0.40 and as 13.3%, and `Exact` can hold only the second.
* **The halfway guard.** Any stem that says *closest*, *nearest* or
  *approximately*, or that asks for a percent, refuses a draw whose value sits
  exactly between two printable answers (`values.unambiguous`, copied from
  `percentages`), and a "closest to" page additionally refuses a draw where
  two printed options are equally near the exact value.
* **Griddable answers.** A grid-in whose value will not fit the digital SAT's
  five characters is refused at draw time by `values.grid`, not discovered
  later: 23/60 and 0.26 are answers a student can enter, 415/799 is not.

`option_check.py` reads the printed page back -- adding the table up from its
own cells, finding the event and the condition in the printed stem, and
recomputing every printed option -- and shares nothing with the code above.
"""

from __future__ import annotations

from ...topic import Topic
from .audit import AUDITS
from .families import derived as D
from .families import freq as F
from .families import simple as S
from .families import twoway as T
from .sources import ALL, EXCLUDED

TEMPLATES = {
    "prob.bag": S.bag,
    "prob.subset": S.subset,
    "prob.data_set": S.data_set,
    "prob.count_from_prob": S.count_from_prob,
    "prob.symbolic": S.symbolic,
    "prob.rate_share": S.rate_share,
    "prob.freq_table": F.freq_table,
    "prob.freq_grouped": F.freq_grouped,
    "prob.two_way.marginal": T.marginal,
    "prob.two_way.joint": T.joint,
    "prob.two_way.conditional": T.conditional,
    "prob.two_way.grouped": T.grouped,
    "prob.two_way.missing_cell": D.missing_cell,
    "prob.two_way.cell_from_total": D.cell_from_total,
    "prob.two_way.percent_columns": D.percent_columns,
    "prob.two_way.nearest_row": D.nearest_row,
}

TOPIC = Topic(
    slug="probability",
    name="Probability",
    domain="Problem-Solving and Data Analysis",
    templates=TEMPLATES,
    audits=AUDITS,
    sources=ALL,
    excluded=EXCLUDED,
)
