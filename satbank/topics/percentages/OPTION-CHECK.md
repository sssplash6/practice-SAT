# Reading the wrong answers back

`satbank check` asks whether the key is right. It never asks whether a
distractor is *also* right.

Nothing in the engine reads a wrong option as mathematics. `assemble_text` takes
four strings, shuffles them and records which one is the key; `assemble` sorts
four numbers; `audit` re-derives the key and compares; `structure` counts surface
forms and `prose` looks for placeholders. All of that is satisfied by an item
with two defensible answers. The hole is structural: an option no code ever
solves cannot be found wrong by any amount of solving the key.

`option_check.py` closes it for this topic.

```bash
PYTHONPATH=. python3 satbank/topics/percentages/option_check.py
PYTHONPATH=. python3 .../option_check.py --draws 3000 --template pct.conclusion
PYTHONPATH=. python3 .../option_check.py --selftest
PYTHONPATH=. python3 .../option_check.py --sources
```

```
  ok   pct.conclusion           3,000 items, 0 defects   (the one conclusion the percentages support)
  ok   pct.table_share          2,934 items, 0 defects, 20 not asked this way   (the nearest of the four)
  ok   pct.find_percent           993 items, 0 defects, 1,058 not asked this way   (the nearest of the four)
  ok   pct.expression           3,000 items, 0 defects   (the quantity after the change)
  ok   pct.per_serving_model    3,000 items, 0 defects   (a model in servings)
  ok   pct.of                     233 items, 0 defects, 2,071 not asked this way   (the nearest of the four)
  ok   pct.increase_decrease      458 items, 0 defects, 1,753 not asked this way   (the nearest of the four)
  ok   pct.compound_share       1,211 items, 0 defects, 1,525 not asked this way   (the nearest of the four)
```

## Which items can be checked this way, and which cannot

Most of this topic answers with a number, and two numbers cannot both be the
answer to "what is 4% of 350?" -- `assemble` drops a distractor that equals the
key, so a numeric option set is safe by construction. Two families are not.

**The options are text.** `pct.expression` prints expressions, `pct.per_serving_model`
prints equations and `pct.conclusion` prints sentences. Nothing sorts them,
nothing evaluates them, and two of them can say the same thing.

**The item rounds.** "To the nearest whole percent" and "of the following, which
is closest to" have a right answer only while one printed option is nearer the
exact value than every other. Two options equally near is two right answers, and
a value sitting exactly halfway between two whole percents is answered by a
convention the stem never states. Neither is visible to the gate, which compares
the key against the key.

The remaining templates -- `pct.reverse`, `pct.change`, `pct.multiplier`,
`pct.two_step`, `pct.successive`, `pct.markup_discount`, `pct.repeated_rate`,
`pct.remainder_total`, `pct.percent_table`, `pct.series` -- ask for one exact
value, and are not checked here. That is a statement about them, not an
omission: there is no second option that could be right.

## What it parses

The reader is deliberately naive. It knows how an SAT page prints a percent and
nothing else -- no `Num`, no `values.py`, no template. `generate` is the only
thing imported from the engine, and only to obtain the finished item in the
state a student would receive it.

| printed form | read as |
|---|---|
| `0.89h`, `89h`, `1.09x` | a coefficient times the variable |
| `h + 0.89`, `x − 50` | the variable shifted |
| `5^x`, `(0.05)^x`, `(1.05)^x` | a base raised to the variable |
| `x/5` | the variable divided |
| `p = <expression>` | a model, by its left-hand name and its function |
| `$4.50`, `145,800`, `12.5%`, `−3`, `9/7` | an exact Fraction |
| a printed two-way table | row labels, column headings and counts |
| `Viewers voting by social media were more likely to prefer ...` | a comparison between the two channels the stem names |

Functions are compared at **several** values, never one. `p = 5x` and `p = 5^x`
agree at one serving, so a check that tried a single x would certify an item with
two right answers.

## What it asserts

Every check is the same shape -- classify all four, demand exactly one hit,
demand it is the keyed one -- so a second right answer fails as loudly as a wrong
key.

| template | property, decided from the printed text |
|---|---|
| `pct.expression` | the percent and the variable come off the stem; exactly one printed expression equals p% of it (or the quantity after the change) at x = 1, 2, 10 and 7/2 |
| `pct.per_serving_model` | the percent per serving comes off the stem; exactly one printed model gives p = per·x at x = 1, 2, 3 and 10 |
| `pct.conclusion` | the turnout, the split and the two rates come off the stem; each printed sentence is decided on its own terms, and exactly one is supported |
| `pct.table_share` | the table is read back, the stem's group and column phrases are matched to its rows and headings, and the exact percent is recomputed and compared with the four |
| `pct.find_percent`, `pct.of`, `pct.increase_decrease`, `pct.compound_share` | the exact value is recomputed from the stem's own printed numbers; exactly one option is nearest it, and no value sits halfway |

The conclusion item is worth spelling out, because "is this statement supported"
is not arithmetic. Five sentence shapes, each decided on its own terms:

* **a comparison between the two channels** -- supported exactly when the
  channel named first has the higher rate among its own voters. Numeric.
* **"If all *who* had voted, *name* would have won"** -- the stem reports rates
  among the votes actually cast. It says nothing about anybody who did not vote,
  so nothing about them follows. Structural.
* **"If all who voted had voted *this way* instead of *that way* ..."** -- the
  same: one channel's rate is a fact about that channel's voters, not a rate that
  would survive moving the other channel's voters across. Structural.
* **"*Who* voting *this way* were likely to be younger ..."** -- an attribute
  nobody collected. Structural.
* **"More than half of all *who* preferred *name*"** -- numeric, and computed:
  the most this data can say about *all* of them is the candidate's share of the
  votes cast, of the share of people who cast one.

A sentence matching none of the five raises `Unreadable` rather than counting as
unsupported. An unrecognised conclusion is an unchecked conclusion, which is the
thing this script exists to stop.

## What it caught

**One live defect, in the rounding family.** `pct.find_percent`'s
`nearest_whole` frame asks for a share "to the nearest whole percent" and the
draw is free to land exactly halfway:

```
A shipment contains 40 bolts, of which 37 are stainless steel. To the nearest
whole percent, what percent of the bolts in the shipment are stainless steel?
    A) 3%    B) 7%    C) 37%   * D) 93%
        37/40 = 92.5%
```

92.5% is 93% under round-half-up and 92% under round-half-to-even. The stem
states no convention, so a student taught the other one does the work correctly
and is marked wrong. Twelve draws in twelve thousand land on a halfway value
across `pct.find_percent` and `pct.table_share`; in none of those twelve were
*both* neighbours printed, so this is an item resting on an unstated convention
rather than an item with two printed right answers -- but it is the same hole,
found the same way, and the gate is green on every one of them.

The fix is `values.unambiguous(value, step)`, used everywhere a stem says
"nearest" or "closest to": it rounds exactly as `snap` does and throws the draw
away when the value sits halfway. Rejecting is free; the registry redraws.

**Four dead misconceptions**, found while reading the text templates back.
`assemble_text` prints the first three distractors it is handed, and every one
of these pools listed more: `pct.conclusion` four, `pct.expression` four per
form, `pct.per_serving_model` five. The tail of each list had never reached a
page. In `pct.conclusion` the unprinted one was "More than half of all viewers
preferred Contestant 2" -- the strongest of the four, the one a student who
reads the two rates as shares of everybody actually picks.

The three source items name the sentences the College Board printed through
`wrongs=`, and a free draw now shuffles its pool, so every misconception in the
file reaches a page. `pct.per_serving_model` keeps one pin: `p = 5^x` is the
only distractor printed in the key's own surface form, and without it the
`structure` check rightly calls `p = 5x` guessable at a glance.

**Four injected faults** (`--selftest`), because a check nobody has seen fail is
worth nothing: the key printed again with a trailing zero, the key moved a
letter, the key said a second time in other words, and an option moved to sit
exactly as far from the exact value as the key. All four are reported, and
between them they exercise both halves of the assertion.

```
  ok   the key again, with a trailing zero: 2 of the four options are right: '1.55h', '1.550h'
  ok   the key moved a letter: the right option is 'p = 20x', but the key is 'p = (0.2)^x'
  ok   the key said twice: 2 of the four options are right: ...
  ok   an option tied with the key: 2 options are equally close to 707520.0: ['707,540', '707,500']
```

**Nothing in the official sets.** `--sources` runs the same assertions over the
official option sets; the nine that are asked this way all read back with exactly
one right answer.
