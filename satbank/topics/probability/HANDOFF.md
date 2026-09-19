# Probability — handoff

Wave 4, second topic. Sibling to read first: `../evaluating_statistical_claims/`.

**Status: transcript done, templates in progress.** Update this file as you go.

## Done

* `material/transcripts/probability.json` — all 36 items read off the images and
  transcribed. Verified against `material/keys/probability.json`: every MCQ key
  letter points at the transcribed `answer_value`, every grid-in value matches.
  10 of 36 are grid-ins (2.5, 2.7, 2.11, 2.13, 3.1, 3.2, 3.3, 3.4, 3.5, 3.9),
  which is the brief's count.

## The shape of the official set

| shape | items |
|---|---|
| counts listed in the stem | 1.7, 1.9, 1.12, 1.13, 2.4, 2.11 |
| one-way frequency table | 1.1, 1.4, 1.6 |
| grouped frequency table, conditional | 2.9 |
| count from a stated probability | 1.11, 2.7, 3.4 |
| answer in terms of n | 1.10 |
| rate / share of a total | 2.8 |
| two-way marginal | 1.2, 1.8, 1.14, 2.13 |
| two-way joint | 2.1, 2.3 |
| two-way conditional | 1.3, 2.2, 2.6, 2.12, 3.9 |
| two-way conditional, merged columns/rows | 3.1, 3.5, 3.8 |
| two-way conditional as a percent | 3.6 |
| two-way conditional, "closest to" | 3.7 |
| unknown cell from a conditional | 3.2 |
| unknown cell from the grand total | 1.5 |
| column percentages with a stated ratio | 3.3 |
| which row is closest to a fraction | 2.10 |

## Planned templates (prefix `prob.`)

`simple.py`  bag, subset, data_set, symbolic, rate_share, count_from_prob
`freq.py`    freq_table, freq_grouped
`twoway.py`  marginal, joint, conditional, grouped
`derived.py` percent, closest, missing_cell, cell_from_total, ratio_columns, nearest_row

## The three traps this topic was warned about, and the answer to each

1. **P(A|B) vs P(B|A).** No template ever writes "the answer is this cell over
   that one". Every question is an `Event` (a set of (row, col) index pairs
   built from a row set and a column set) and an optional condition `Event`;
   the value is `|A ∩ B| / |B|`, with `B` the whole table for an unconditional
   ask. The reversed conditional is a *named* member of the distractor pool
   (`reverse`), so it prints as a wrong answer rather than hiding as a bug.
2. **A printed table must close.** `tables.py` builds cells first and derives
   every margin by summation; `option_check.py` re-reads the printed rows and
   asserts row sums, column sums and the grand total all agree — it does not
   trust the builder.
3. **Exact fractions and the halfway guard.** Everything is `fractions.Fraction`
   end to end; `values.py` carries `unambiguous(v, step)` copied from
   `percentages/values.py` (the house pattern — `ratios` copied it too), used by
   every "closest"/"nearest"/percent template. `griddable()` refuses at draw
   time any grid-in answer that will not fit the digital SAT's five characters.

## Next

Write `values.py`, then `tables.py`, then the families, then `audit.py`,
`sources.py`, `option_check.py`, `OPTION-CHECK.md`.

## Defects found and not yet fixed

(none yet)
