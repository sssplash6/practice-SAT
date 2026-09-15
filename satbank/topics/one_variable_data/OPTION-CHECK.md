# Reading the wrong answers back

`satbank check` asks whether the key is right. It never asks whether a
distractor is *also* right.

Nothing in the engine reads a wrong option as mathematics. `assemble_text` takes
four strings, shuffles them and records which one is the key; `audit` re-derives
the key and compares; `structure` counts surface forms and `prose` looks for
placeholders. All seven gate checks stop at the key, so an item with two correct
answers passes every one of them and reaches a student as a question with no
defensible answer.

This topic has the sharpest exposure of any, because most of its options are
**sentences about a distribution**. "The mean of data set A is greater than the
mean of data set B" is not a value the engine can compare; it is a claim, and
whether a claim is true depends on numbers printed in a table or drawn in a
picture. A distractor that happens to be true is invisible to everything the
engine does.

`option_check.py` closes the hole for all nineteen templates. It decides every
option from its printed text and from the item's own table or chart, then
asserts both halves: exactly one option is right, **and** it is the keyed one.

```bash
PYTHONPATH=. python3 satbank/topics/one_variable_data/option_check.py
PYTHONPATH=. python3 .../option_check.py --draws 2000 --template ovd.box_compare
PYTHONPATH=. python3 .../option_check.py --selftest
PYTHONPATH=. python3 .../option_check.py --sources
```

```
  ok   ovd.list_stat              460 items, 0 defects, 140 grid-ins
  ok   ovd.table_stat             600 items, 0 defects
  ok   ovd.bar_read               600 items, 0 defects
  ...
  ok   ovd.must_be_true           600 items, 0 defects

10,418 option sets read back
```

## What it parses

The reader is deliberately naive. It knows how an SAT page prints a list, a
table and a chart, and nothing else — no `common.py`, no `plot.py`, no family
module. `generate` is the only thing imported from the engine, and only to
obtain the finished item in the state a student would receive it. `mean`,
`median`, `mode`, `range` and variance are written out again here; the
duplication is the point.

| printed form | read as |
|---|---|
| `2, 2, 3, 4.5, 11` | a data set. Values split on the comma *and space*, never on the comma inside `1,126` |
| `81°F`, `0.95%`, `3,025`, `9/7`, `−11`, `$1.29` | a `Fraction` |
| a printed table | series by name, the way round the table runs settled by its corner cell and its shape, never by guessing which of two numeric rows is the data |
| `18` / `Frequency 6`, or `3a` | a value and its count; a symbolic count reads as its coefficient |
| `4 (frequency 4), 8 (frequency 3)` | a whole frequency table, as one option |
| `The mean of data set A is greater than the mean of data set B.` | (measure, subject, relation, measure, subject) |
| `I and II`, `III only`, `Neither I nor II` | the set of numbered statements an option claims |
| `Mean` / `Standard deviation` / `Median of the high temperatures` | which measure of the printed data set the option names |
| the SVG of a dot plot | the data set, one value per dot |
| the SVG of a bar graph | `[(label, height)]` |
| the SVG of a box plot | the five numbers it draws |
| the SVG of two histograms | `[(label, bin edges, counts)]` per panel |

The chart readers are the part worth stealing. Each one takes the axis labels
the chart draws *for a student*, fits pixels-per-unit from them, checks every
other label falls on that line, and then maps each dot, bar, box edge and bin
back to a value. They consult none of the item's parameters: this is what a
reader with a ruler would get, so the picture is checked against the options
rather than the options against each other. Panels are separated by the line
their bars stand on and labels attach to the first floor at or below them, so
nothing is assumed about how tall a panel is.

## What it asserts

Every check is the same shape — decide all four, demand exactly one hit, demand
it is the keyed one — so a second correct answer fails as loudly as a wrong key.

| template | property, decided from what is printed |
|---|---|
| `ovd.list_stat` | the named statistic of the printed list, or of the drawn dot plot; and the stem's own count of the values agrees with how many there are |
| `ovd.table_stat` | the named statistic of the one series the question names, rounded as the question says; two rows added, when it asks that; and the printed total is the sum of the rows |
| `ovd.bar_read` | the height, the difference or the mean of the bars **as drawn**, for the bars the question names |
| `ovd.freq_stat` | the statistic of the data set the table stands for — and, where the counts are `a`, `2a`, `3a`, the same answer for a = 2, 3 and 5, so an answer that moves with `a` is no answer |
| `ovd.freq_order` | exactly one printed ordering of mean, median and mode is the true one |
| `ovd.freq_two_groups` | the two medians differenced, or the one true comparison of the two means |
| `ovd.freq_choose` | the table that *is* the printed data; the one greatest mean; the one right-skewed set |
| `ovd.compare_sets` | each sentence tested against the two printed data sets: the means compared, what actually differs, and the numbered statements |
| `ovd.sd_compare` | from the summary table, the one claim its three columns force; from the drawn histograms, the wider distribution, recovered bin by bin |
| `ovd.measure_effect` | data sets the stem describes are built, the printed edit applied, and every measure that always survives it (or never does) counted |
| `ovd.odd_measure` | the one named measure of the printed values that is not the stated number |
| `ovd.new_data_set` | the drawn dot plot, shifted or extended as the stem says, then each comparison decided |
| `ovd.box_read` | the drawn part of the box plot, nearest exactly one option and within a hundredth of the drawn span of it |
| `ovd.box_compare` | the drawn medians decide the median claims; a mean claim is true only if it holds for every data set the picture allows |
| `ovd.unknown_value` | the value the two printed means force; or, for "NOT a possible value", each printed option tried in the list to see whether mean and median can agree |
| `ovd.mean_totals` | the removed value, or the combined mean, from the stem's own printed numbers |
| `ovd.mean_identity` | never asked as multiple choice — every draw is a grid-in, and the run says so rather than passing quietly |
| `ovd.reason_center` | what a total pins down, decided by splitting it several ways and keeping what every split agrees on; and which values the band holding the median allows |
| `ovd.must_be_true` | each numbered statement decided by search over the data sets the stem allows |

Two of these deserve a word, because "must be true" cannot be decided by
arithmetic on one data set.

**Search, not assertion.** For `ovd.must_be_true`, `ovd.measure_effect` and
`ovd.reason_center`'s first frame, the script builds many data sets consistent
with the printed stem — including the corner cases, which are the extremes for
these measures: every value equal, one value carrying half the total, one value
far below the rest. A statement called *false* has to produce a witness where it
fails. A statement called *true* has to survive every witness. Neither half is
taken on trust, and a statement that the search cannot decide is an error rather
than a guess.

**What a box plot leaves open.** A box plot draws five numbers, so the mean is
not among them — but that does not make a *comparison* of two means undecidable.
A quarter of the values sit in each of the four spans the plot draws, so the mean
of a data set drawn like this lies between `(least + Q1 + median + Q3)/4` and
`(Q1 + median + Q3 + greatest)/4`. While those two bands overlap, the mean
comparison is genuinely open and the two mean options are wrong. When they
separate, it is forced — and then there are two right answers.

## What it caught

**Two live defects**, in templates the full gate calls green.

### 1. `ovd.box_compare`: box plots far enough apart force the means too

The whole point of this item is that a mean cannot be read off a box plot, so
two of the four options are mean comparisons. That holds only while the two
pictures overlap. Seed 6 drew them apart:

```
Based on the box plots, which of the following statements must be true?
    group A: 31, 33, 35, 37, 47        group B: 33, 39, 43, 45, 49
  A) The mean   distance of group A is greater than ... group B.
  B) The median distance of group A is less    than ... group B.   <- the key
  C) The median distance of group A is greater than ... group B.
  D) The mean   distance of group A is less    than ... group B.   <- also true
```

Every data set drawn as group A has a mean below `(33+35+37+47)/4 = 38`; every
one drawn as group B has a mean above `(33+39+43+45)/4 = 40`. Written out as
eleven values, where the five-number summary sits at known positions, the mean of
A can reach at most 37 and the mean of B can fall no lower than 41. D is as true
as B — and it is offered as a distractor, with a reason attached explaining why a
student who picks it was wrong.

**147 of 600 draws** were like this, close to one in four, and coverage,
transcript, acceptance, audit, structure, prose and capacity were all green on
every one of them.

The fix is in `boxes.py`: the two mean bands must overlap, or the draw is
rejected. The official item this template was learned from (3.15) sits
comfortably inside the rule — its bands are 23.5–25.25 and 23.5–25.0, and eleven
values can realize a mean of 24.909 for A against 23.909 for B, or 23.909 for A
against 24.636 for B. Either ordering is reachable, so neither mean option is
true and the item stands.

### 2. `ovd.reason_center`: the filler landed inside the band

"Which of the following could be the median of the weights of these fish?" is
answered by the band the middle fish falls in. The three wrong options are
values outside that band — except that when the two stated bounds are one apart,
two of the three coincide. `assemble` then has only two usable distractors and
pads the set from `_fillers`, which multiplies the key: half of a value inside
the band is another value inside the band.

```
Fourteen fish weighing less than 9 ounces are placed in tank A. ...
Which of the following could be the median of the weights of these 27 fish?
  A) 2.25   <- "near-miss arithmetic slip"   (also below 9: also possible)
  B) 4.5    <- the key
  C) 9.5      D) 12
```

The fix is in `means.py`: the impossible values are now drawn from a pool large
enough to yield three distinct ones whatever the bounds are, the boundary
strictness is read the way the stem words it, and the item refuses to ship if
any option other than the key could be the median.

**Six injected faults**, because a check nobody has seen fail is worth nothing.
`--selftest` rebuilds each kind of defect by hand and shows it caught, by the
right half of the assertion:

| injected | caught as |
|---|---|
| the key's comparison said backwards — the same claim, a different string | 2 of the four options are right |
| a range comparison the drawn boxes do force, added to a box-plot item | 2 of the four options are right (only the pixels can tell) |
| a second frequency table with exactly the key's mean, every count doubled | 2 of the four options are right |
| the key moved to another letter | the right option is X, but the key is Y |
| a bar graph that draws somebody else's data | 0 of the four options are right |
| half the key, in a "could be the median" item — defect 2, put back | 2 of the four options are right |

`--sources` runs the same assertions over the official option sets as
transcribed: 40 of the 49 items are multiple choice, and all 40 read back clean.

## Running the same check on another topic

The readers are topic-agnostic; the assertions are not, and should not be.

1. **A property each option has or does not have, decided from its printed
   text.** "Which statement correctly compares the means" becomes two means
   computed off the printed table. "Which measure is unchanged" becomes the edit
   applied to data sets the stem describes. If the property cannot be decided
   from the printed option, say so rather than skipping quietly — every reader
   here raises `Unreadable` on a shape nobody taught it, because an option no
   code reads is exactly what this script exists to stop.

2. **A reader that shares nothing with the renderer.** Parse the string; do not
   re-render it and compare. A renderer bug that drops a minus sign is invisible
   to any check that goes back through the renderer.

3. **Both halves of the assertion.** `hits.count(True) == 1` catches the second
   correct answer; `hits[keyed]` catches the right answer attached to the wrong
   letter. Checking only the second is what the engine already does.

Three further notes from doing it here.

Assert over generated *draws*, not over the source items: all 40 official option
sets were already clean, and both defects lived in draws no source item makes.

Where a figure carries part of the question, read the figure. Six of the
nineteen templates here are checked against pixels: dot plots, a bar graph, two
kinds of box plot and a pair of histograms. The box-plot defect could not have
been found any other way, because the four options are perfectly consistent with
each other — it is the picture that makes a second one true.

And watch what happens when a distractor pool comes up short. `assemble` pads
from `_fillers`, which knows nothing about the question: a multiple of the key
is a fine near-miss for "what is the mean" and a disaster for "which of these
could be the median". The second defect here was a filler, and the shape of it —
an item whose distractor list silently ran out — is worth looking for anywhere
options are built from a pool that can shrink.
