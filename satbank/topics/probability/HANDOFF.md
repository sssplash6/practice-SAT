# Probability — handoff

Wave 4, second topic. **Complete and green**; nothing is stubbed. 36 official
items (14 easy / 13 medium / 9 hard), 10 of them grid-ins, 0 exclusions,
16 templates, 18,006 distinct items in 1,200 draws each.

Sibling to read first: `../evaluating_statistical_claims/`. Then
`../one_variable_data/` for table rendering and `../percentages/values.py` for
`unambiguous`, the halfway guard, which is copied into `values.py` here.

## Gate

```
PYTHONPATH=. python3 -m satbank check --topic probability
  ok   coverage    36/36 encoded, 0 excluded
  ok   transcript  36/36 items
  ok   acceptance  36/36 answers, 97% of official distractors recreated, 24/26 option sets complete
  ok   audit       4,763 items re-derived
  ok   structure   100% of distractors named
  ok   prose       4,763 items read
  ok   capacity    18,294+ distinct items

PYTHONPATH=. python3 satbank/topics/probability/option_check.py --selftest
  0 scenario-English mismatches, 16/16 injected faults caught

PYTHONPATH=. python3 satbank/topics/probability/option_check.py --per 900
  14,321 items built, 14,321 read back, 0 unreadable, 0 defects
```

## The three traps this topic was warned about, and the answer to each

**1. "Given that" is the whole item.** No template ever names a denominator.
A question is an `Event` (a set of `(row, col)` cells built from a row set and
a column set) and a condition `Event`, and the value is always

```python
table.count(meet(event, given)) / table.count(given)
```

with `given` the whole table when the question is unconditional. There is no
line of code in which the wrong denominator could be written, because no line
picks one. P(B|A) is `reverse`, a *named* member of every conditional pool,
and it prints as a wrong answer with the teacher's sentence beside it. The
`option_check` proves the distinction three ways: it replaces a keyed option
with P(B|A) and catches it, it swaps the event and the condition **in the
stem** and catches that, and it does the same to a grid-in.

**2. A printed table must be arithmetically closed.** `world.Table` takes the
interior cells and *derives* every margin by summation — a margin is never
data a template supplies. `option_check.Printed` then adds the printed rows up
again, from the page, and asserts rows, columns and the grand total all meet.
That check found, on its first run, that **College Board's own table for item
1.2 does not add up**: 60 + 35 = 95 under a printed column total of 90, and
90 + 40 = 130 under a printed grand total of 135. Recorded in the transcript's
`notes` and in the `sources.py` row; the engine prints 95.

**3. Exact fractions and the halfway guard.** Every count and probability is a
`fractions.Fraction` from the cell to the page; no float is ever used to
compute or compare a value. `values.PVal` carries the exact value **and the
string printed for it**, because the source set prints the same number as
`10/40`, `1/4`, `0.40` and `13.3%`, and `Exact` can hold only the second.
`values.unambiguous` (copied from `percentages`) refuses any draw whose value
sits exactly halfway between two printable answers, and a "closest to" page
additionally refuses a draw where two printed options are equally near.
`values.grid` refuses at draw time any grid-in that will not fit the digital
SAT's five characters — `23/60` and `0.26` are answers a student can enter,
`415/799` is not.

## The sixteen templates

| template | official items | distinct / 1,200 |
|---|---|---:|
| `prob.bag` | 1.12, 2.4, 2.11 | 1,200 |
| `prob.subset` | 1.7, 1.9, 2.5 | 1,051 |
| `prob.data_set` | 1.13 | 1,200 |
| `prob.count_from_prob` | 1.11, 2.7, 3.4 | 1,183 |
| `prob.symbolic` | 1.10 | 846 |
| `prob.rate_share` | 2.8 | 967 |
| `prob.freq_table` | 1.1, 1.4, 1.6 | 1,200 |
| `prob.freq_grouped` | 2.9 | 1,200 |
| `prob.two_way.marginal` | 1.2, 1.8, 1.14, 2.13 | 1,200 |
| `prob.two_way.joint` | 2.1, 2.3 | 1,200 |
| `prob.two_way.conditional` | 1.3, 2.2, 2.6, 2.12, 3.6, 3.7, 3.9 | 1,200 |
| `prob.two_way.grouped` | 3.1, 3.5, 3.8 | 1,200 |
| `prob.two_way.missing_cell` | 3.2 | 1,200 |
| `prob.two_way.cell_from_total` | 1.5 | 1,200 |
| `prob.two_way.percent_columns` | 3.3 | 1,199 |
| `prob.two_way.nearest_row` | 2.10 | 760 |

## Distractor fidelity: 97%, and the 3% named

Two of College Board's own wrong answers are not reached, and neither is
curve-fitted to:

* **1.5, option A `109`.** The table is 312 / 220 / `?` / 216 with a stated
  total of 1,000; the key is 252. The engine offers `468` (the total less the
  sports-playing row), `688` (the total less one cell) and `564` (the total
  less the other column). `109` is not the total less any row, column, cell or
  pair of cells, and no misconception this template models lands on it.
* **2.9, option D `25/34`.** The complement inside the condition is
  13 + 11 = 24 of 34, and the engine offers `24/34`. `25` is not any subtotal
  of the printed intervals (2, 7, 13, 11, 7, 3). It looks like an off-by-one
  in the source.

Every other official distractor in the set is produced by a named
misconception. 24 of the 26 multiple-choice source items have their complete
printed option set recreated.

## Files

```
values.py             PVal (exact value + printed surface), grid/griddable,
                      unambiguous, pick, mcq/spr/text_mcq, roll_fmt
world.py              Table, Event, meet, and 22 two-way scenarios with their
                      labels and four sentence forms per category
families/simple.py    bag, subset, data_set, count_from_prob, symbolic, rate_share
families/freq.py      freq_table, freq_grouped
families/twoway.py    marginal, joint, conditional, grouped
families/derived.py   missing_cell, cell_from_total, percent_columns, nearest_row
audit.py              an independent solver for all twelve kinds
sources.py            36/36 encoded, EXCLUDED empty
option_check.py       the page reader, the scenario-English proof, 16 faults
OPTION-CHECK.md       what it reads, what it found, and what it does not check
```

## Things to know before changing anything

**The scenario-English proof is the load-bearing test.** `option_check
--selftest` puts every sentence form of every category of every scenario
through the reader and requires it to resolve to exactly that category. It
failed 76 times when first run, and two of those failures were the reader
agreeing with the *opposite* row. **Re-run it after touching any phrase in
`world.py`, and after touching the matcher.**

**A rounded answer may print only under a frame that can say so.** `HEDGED` in
`families/twoway.py`. "What fraction of the X are Y?" has nowhere to put
"which of the following is closest to", and a draw that rounded under it
printed an answer none of the four options held. All seven gate checks were
green on those items.

**`Ctx.condition_axis`.** The contestants table counts one row per contestant
*per day*, so it is not a cross-classification of its units: a marginal or
joint probability off it is meaningless, and its row phrases say "that score",
which needs a score to have been named. Any future scenario of that shape
needs the same flag.

**Free draws must reach every printed shape.** `free()` and `roll_fmt()` give
a free draw a 25% chance of a grid-in and a 25% chance of a marginless table,
because both appear in the official set and a branch only a `sources.py` row
can enter is a branch no volume sweep ever reads. Three live defects were
found the day those branches became reachable.

## Two notes for the shared core (worked around here, not edited)

1. **`check._shape` reads the letters "pi" inside ordinary English.** Any
   word-valued option containing the substring `pi` reads as a π option, so
   the key becomes "the only option that looks like this".
   `prob.two_way.nearest_row` prints row labels as its options and refuses a
   draw whose labels contain `pi` — a guard that exists only because of this.
   `parks`' row label "Has camping facilities" contains it, which is why that
   scenario can never be used for that template.
2. **`item.assemble`'s `_fillers` are unexplainable options.** This topic
   treats reaching them as a bug in the pool rather than a fallback
   (`values.mcq` raises on a filler reason), which is why distractor naming is
   100% rather than merely above the floor. Worth considering as the default.

## Defects found and not fixed

None outstanding. The eleven found during the build are listed, with what each
one cost, in `OPTION-CHECK.md` → "What the sweep found".
