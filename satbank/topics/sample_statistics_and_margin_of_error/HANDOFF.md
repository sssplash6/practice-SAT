# Sample Statistics and Margin of Error — handoff

Started 2026-09-19. Wave 4, the third and last topic of the wave.
18 official items: 6 easy / 8 medium / 4 hard, two of them grid-ins (2.6, 3.2).

## Status

**Gate green on all seven checks** (18/18 encoded, 0 excluded, 100% of
official distractors, 16/16 complete option sets, 13,586+ distinct items).
`option_check.py` and `OPTION-CHECK.md` are the remaining pieces.

* **Transcribed: 18/18.** `material/transcripts/sample_statistics_and_margin_of_error.json`
  is complete; every question image was read. The two grid-ins are 2.6 (3540)
  and 3.2 (94). Three items carry a table (2.6, 3.1, 3.2) and 3.3 carries a
  summary table of two samples.
* **Template plan: 12 templates, 18/18 encoded, 0 excluded.** See the table
  below.
* Everything else: in progress. This file is rewritten as each piece lands.

## The one design decision, and why

A margin of error is a statement about a **population parameter**, and the
four claims students confuse are the distractor pool:

1. the interval is *plausible*, not certain — "it is not possible that the
   value is below L" is false;
2. the margin describes the parameter, not the sample and not individuals;
3. a larger sample narrows the interval, a higher confidence level widens it;
4. the statistic is a point estimate, so "the value **is** E" is false even
   when E is the estimate.

None of that may be written down as "option B is right". Following
`evaluating_statistical_claims`, the topic carries a tiny inference engine in
`study.py`:

* a **Study** is what the page says: how the units were chosen, from what
  population, the sample size, the estimate, the margin, and the population
  size when the stem gives one;
* `reports(study)` derives **what the study actually supports** — a dict from
  `(aspect, population)` to a `Report(modality, value-set)`. A random sample
  with a margin reports `("parameter", "frame") -> plausible [E-M, E+M]`; the
  sample statistic is reported `certain {E}`; a count parameter is reported
  only when the stem gives the population size; individuals, misclassification
  and any wider population are **not keys of that dict at all**;
* a printed option is a **Claim** `(aspect, population, modality, value-set)`,
  and `supported(study, claim)` is one rule:

      the pair must be reported,
      the claim's modality must not be stronger than the report's,
      and the report's value-set must be contained in the claim's.

Everything falls out of that one rule. `"the parameter is exactly E"` is a
`certain` claim against a `plausible` report, so false. `"it is not possible
that the parameter is below L"` is `certain`, so false. `"the actual values of
all members are between L and U"` has aspect `individuals`, which is not a key
of `reports`, so false. `"plausible values of the number are between ..."` is
aspect `count`, reported only when the population size is printed — which is
why it is right in 2.7 and wrong in 1.4, from the same rule. `"no conclusion
can be made"` is supported exactly when `("parameter","frame")` is absent,
which happens for a self-selected sample — so that branch is reachable and is
exercised by free draws.

`sources.py` names no answer and no `correct_id`. The wrong-answer test: hand
a source item a `wrongs=` list naming the claim its own study supports and the
template raises rather than keying it.

## Templates

| template | source items | what it is |
|---|---|---|
| `sstat.scale_count` | 1.1, 1.2 | k of n in the sample, scale to the population |
| `sstat.scale_group` | 3.4 | a percent in one group, population a product, complement asked |
| `sstat.scale_range` | 1.3 | mean of a small sample x total units, range-valued options |
| `sstat.scale_two_way` | 2.6 | two-way table, grid-in |
| `sstat.scale_frequency` | 3.2 | frequency table, difference of two groups, grid-in |
| `sstat.interpret_mean` | 1.5, 1.6, 2.2 | sentence options about a mean +- margin |
| `sstat.interpret_percent` | 1.4, 2.3, 2.8 | sentence options about a percent or proportion |
| `sstat.interpret_table` | 3.1 | the same, with the estimate read off a two-way table |
| `sstat.subgroup_claim` | 2.1 | a statistic measured on a subgroup, no margin |
| `sstat.count_claim` | 2.5 | "exactly/must" against "the best estimate is" |
| `sstat.plausible_count` | 2.4, 2.7 | which count, or which range of counts, is plausible |
| `sstat.margin_size` | 3.3 | why one sample's margin is larger |

## What is done / next

1. Done — `values.py` (exact printing), `study.py` (the rule), `world.py`
   and `claims.py` (the vocabulary and the sentence catalogue),
   `count_claims.py`.
2. Done — `families/estimate.py` (five numeric templates),
   `families/interpret.py` (five sentence templates),
   `families/design.py` (two).
3. Done — `audit.py`: the rule written out a second time over its own value
   sets, parsing the printed sentences with its own patterns. It imports
   neither `study.py` nor `claims.py`.
4. Done — `sources.py` (18/18, `EXCLUDED` empty), `__init__.py`.
5. **Next** — `option_check.py` + `OPTION-CHECK.md`: a third writing of the
   rule that reads the numbers off the printed **stem** rather than out of
   `item.params`, plus the table arithmetic, plus injected faults.

## Defects found and not yet fixed

None outstanding. Two found and fixed while building:

* the audit's interval reader was case-sensitive, so it could not read
  "Between 28.59% and 35.41% ..." at the head of a sentence and silently
  fell through to "the last number in the sentence". It reported 0 of 4
  statements holding rather than a wrong answer, which is the only reason it
  was noticed; a reader that had defaulted to True would have passed.
* the same reader's number pattern was `[\d,.]+`, which swallows the full
  stop that ends the sentence and turns `0.91.` into a parse error.

## Known weak point, named rather than hidden

`scale_group`'s `half` distractor (23,400 in official item 3.4) is the
thinnest named misconception in the topic: it is half the state's students,
reached by assuming the class splits evenly instead of using the reported
percent. It is a real default students fall back on, but it is the one wrong
answer here that is not arithmetic done wrongly.

## Traps already known

* `check._shape` reads the letters **pi** inside ordinary English, so an
  option naming *participants*, *opinion* or *pizza* looks like a pi-option
  and the key becomes "the only option of its shape". Vocabulary is checked
  for the substring before it is used.
* A printed table must be arithmetically closed and no gate check reads one.
  `option_check` re-adds every row, column and margin, and checks the estimate
  the stem quotes against the table it was read from (3.1: 240/799 = 30.0%).
* Anything saying *best estimate*, *about*, *closest* or *nearest* rounds, so
  the draw is refused when the exact value sits halfway between two printable
  answers (`values.unambiguous`).
