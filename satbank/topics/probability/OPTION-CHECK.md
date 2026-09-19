# Reading the Probability page back

`option_check.py` decides **every printed option from the printed page**. It
reads `item.table`, `item.stem`, `item.choices` and `item.answer`, and nothing
else — `grep -n 'params' option_check.py` returns only the sentence that says
so. It shares no function with any template: the table arithmetic, the
rounding, the option parsing and the reading of the question are all written
again here.

Two holes it closes that the gate cannot see:

1. **An item with two correct options** passes all seven gate checks, because
   the gate only ever asks whether the *key* is right.
2. **A printed table that does not add up.** Nothing in `satbank/` reads a
   table as arithmetic. A table whose rows disagree with their margins is a
   question nobody can answer, and the College Board has shipped one — see
   below.

```
PYTHONPATH=. python3 satbank/topics/probability/option_check.py            # sweep
PYTHONPATH=. python3 satbank/topics/probability/option_check.py --selftest # proofs
```

## What it does, in order

**1. Closure.** `Printed` takes the rows the page shows and re-adds them from
the interior cells alone: every row must reach its printed row total, every
column its printed column total, and the two margins must meet at the printed
grand total. A one-way frequency table's printed Total must equal its counts;
each column of a percentage table must reach the 100% it prints. A cell
printed as `x` or `?` is the question, and its row and column are skipped.

**2. The question.** The last sentence of the stem is matched against seven
frames (`given`, `if_cond`, `select_cond`, `of_the`, two that run two clauses
together, and the plain unconditional one) and split into an *event* clause
and, where there is one, a *condition* clause. **A frame that parses but names
no printed label is the wrong frame, not a dead end** — the reader keeps
looking, because "If one of the 799 teens surveyed is selected at random" has
the shape of a condition and names no column.

**3. The clauses become cells.** Each clause is matched against the table's
**printed labels**, never against a phrase from `world.py`. Three readings, in
order:

* *A comparison over interval labels.* "at least 10 years of age" is not a
  label; it is a cut, and it names the columns `10–19 years` and `20+ years`
  because their ranges lie inside it. Tried first, because "before 2010"
  contains the token `2010`. Only an axis whose labels are **all** intervals
  is read this way — "1 visit" parses as the number 1, and the age cut was
  matching the visits column of a table whose ages are rows.
* *Containment inside a short run.* Every token of the label appears in the
  clause, stemmed, in any order but close together.
* A label whose tokens are a proper subset of another matched label's is
  dropped, which is what stops `Has bicycle paths` being read out of "does
  not have bicycle paths".

Three details of the matcher are load-bearing, and each was put there by a
draw it got wrong:

| detail | what it stops |
|---|---|
| `no` and `not` are one token | `No state income tax` being read out of "does **not** have a state-level income tax" — the *opposite row* |
| a one-character token keeps its case | the article in "a flower from site B" matching the column `Site A` |
| a label's words must stand within `len + 4` tokens | `2 out of 5` being read out of "a score of **0 out of 5** received that score on Day **2**" |

A conjunction is split before matching, and the split is accepted only when
one half is purely a row and the other purely a column — which is what a joint
question is. A union written with "and" ("medium and heavy texters") fails
that test and falls through to the whole clause, where it belongs.

**4. Every option.** Each is parsed to an exact `Fraction` — `12/16`, `1/4`,
`0.40`, `13.3%`, `252` — and compared with the value the cells give. Exactly
one must be correct and it must be the keyed one. For a stem that says
*closest*, the keyed option must be **strictly nearer the exact value than
every other**: rounding the key correctly is not the same thing, because the
student compares against the four numbers on the page. For a percent, the
reader rounds the exact value itself, half up, and refuses a value sitting
exactly halfway.

**5. Grid-ins.** The printed answer is recomputed from the page and must also
fit the digital SAT's five characters.

Nothing is skipped silently. A page the reader cannot parse is counted and
printed as `UNREAD`, and the run fails on it, because a reader that has
stopped matching prints `0 defects` in the same words as one that checked
everything.

## The scenario-English proof

`--selftest` first checks something no other topic needed: **every phrase a
scenario can print must name the categories it stands for.** For all 22
two-way scenarios, for every row, column and union, all four sentence forms
(`n`, `p`, `g`, `pl`) are put through the reader and must resolve to exactly
that selection's indices — 300-odd assertions.

This is the load-bearing assumption of the whole checker, and it was wrong 76
times when it was first run. The worst were not near-misses:

```
taxes.row 'No state income tax': the p phrase 'does not have a state-level
  income tax' reads as ['State income tax'], not as ['No state income tax']
flowers.col 'Site B': the n phrase 'a flower from site B' reads as
  ['Site A', 'Site B'], not as ['Site B']
```

The first is the reader agreeing with the opposite row. Every one is fixed —
some in the matcher, some by rewording a scenario — and the test is in
`--selftest`, so a new scenario cannot be added without re-running the proof.

## Sixteen injected faults, sixteen caught

**A fault counts as caught only when the reader reports a defect.** An
`Unreadable` page is a reader that stopped working, not a catch, and is
printed as a failure. (Wave 3 had four fault-injection proofs that were
themselves broken; one caught its fault only because the splice failed to
parse.)

| fault | what it proves |
|---|---|
| a printed column total raised by one | closure reads columns |
| a printed grand total raised by seven | closure reads the corner |
| the key letter moved to a wrong option | the letter is checked, not the set |
| a distractor rewritten to the key's own value | two correct options are caught |
| the keyed option replaced by **P(B\|A)** | the reversed conditional is caught |
| **the event and the condition exchanged in the stem** | the reader reads the *sentence*; a checker that guessed the question would report nothing |
| a grid-in answering the reversed conditional | grid-ins get the same treatment |
| a grid-in answer of 11 characters | the five-character field is enforced |
| a percent key rounded to the wrong neighbour | the rounding is re-done, not trusted |
| a second option exactly as close as the key | a "closest to" page with no single answer |
| the second-closest option keyed | "closest to" picks the right one |
| an interior cell changed after the options were chosen | the options are decided from the cells |
| a frequency table whose printed total is wrong | one-way closure |
| the second-nearest row keyed | word-valued options are decided |
| a column of percentages totalling 105% | percentage-table closure |
| two algebraically equal options in terms of n | the `in terms of n` page is decided |

## What the sweep found

**14,321 generated draws and all 36 source items read back: 0 unreadable, 0
defects** — but that number is only the *last* run. Getting there took eleven
rounds, and every round found something. What the checker actually found, in
the order it found it:

1. **The College Board's own table for item 1.2 does not add up.** The cells
   are 60 and 35 in the *Beverage purchased* column and the printed column
   total is 90; 60 + 35 = 95, and 90 + 40 = 130 against a printed grand total
   of 135. The row totals and the grand total are consistent and no option
   depends on the wrong margin, so the item is still answerable — but the
   engine prints 95, and the transcript records the discrepancy. Found by the
   closure check on the first run, before a single generated item.
2. **Three templates printed a rounded decimal under a stem that never said
   so.** `What fraction of the X are Y?` and `Of the X, what fraction ...?`
   have nowhere to put "which of the following is closest to", and a draw that
   rounded under those frames printed an answer no option held: 19/29 keyed as
   `0.66` with 0.66 nowhere among the four. The fix is `HEDGED` in
   `families/twoway.py` — a rounded answer may print only under a frame that
   can say it is rounded.
3. **Grid-ins recorded the surface a free draw happened to roll**, so the
   audit rounded an answer the page never rounded (`5/9` re-derived as
   `0.556`). `grid_exact` now forces the exact surface for any `spr` draw.
4. **The contestants table is not a cross-classification of its units.** It
   counts one row per contestant *per day*, so "the probability that a
   contestant is in the Day 3 row" is meaningless, and the row phrases say
   "that score", which needs a score to have been named. `Ctx.condition_axis`
   now restricts that scenario to questions conditioned on a score. Found by
   reading the preview page.
5. **A joint question printed "but" between two negatives** — "does not have
   camping facilities **but** does not have bicycle paths". The contrast is
   now used only when the two predicates differ in polarity.
6. **Four scenarios could not state their own grand total**, so
   `cell_from_total` was producing a page from which the hidden cell could not
   be recovered at all. The template now refuses a scenario whose prose never
   prints the total.
7. Smaller things the eye caught on the rendered page: "a egg sandwich", "a
   orange button", "n green tiles **on** a bag", "If one of these kittens
   **who is** chocolate-colored", a rationale that answered `4/5` under a
   grid-in keyed `0.8`, and a "closest to being one fourth" item whose two
   nearest rows were 6 and 10 away — a judgement call printed as a fact, now
   refused unless the runner-up is at least twice as far.

Items 2, 3 and 6 were live defects in shipped-looking items that every one of
the seven gate checks passed.

## What it does not check

* It does not read the *rationale*. A wrong explanation beside a right answer
  is still possible and is only caught by reading the page.
* It routes to a family reader by `item.template`. The **decision** is made
  from the page in every case, but the choice of *which* reader is told by the
  item's own name.
* `check_missing_cell` re-derives the hidden cell from the stated probability
  and checks the two agree, but the stated probability is itself printed by
  the template, so what is proved is consistency, not that the stem's fraction
  is the one a reader would want.
* Nothing here checks that a distractor is *plausible*, only that it is wrong.
