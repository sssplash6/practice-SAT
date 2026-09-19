# What `option_check.py` reads, and what it found

`satbank check` asks one question: is the key right? It never reads a **wrong**
option as mathematics. Ten of the twelve templates here answer with a
*sentence about a margin of error*, and that is precisely where the gate is
blind — "the mean is between 4 and 5 miles" and "it is plausible that the mean
is between 4 and 5 miles" are both true, and an item offering both reaches a
student with no defensible answer having passed all seven checks.

There is a second reason this file exists on this topic in particular. Its
sibling, Evaluating Statistical Claims, was built twice on an engine that had
been *told* the answer — once as a string predicate, once as a `correct_id`
parameter — and both times the template, the audit and the checker shared one
opinion and none of them could disagree. So the rule that decides what a
margin of error supports is written three times in this package, by three
different routes:

| | works from |
|---|---|
| `study.py` (the templates) | the study a template was handed |
| `audit.py` | `item.params`, parsing the printed sentences with its own patterns |
| `option_check.py` | the **printed stem**, the **printed table** and the **printed sentences**, and nothing else |

`option_check.py` imports `generate`, `ItemError` and the scene records. It
does not import `study.py`, `claims.py`, `audit.py`, or any family's logic.

## What it reads off the page

* **the estimate and the margin** — the margin is the number the phrase
  "margin of error" introduces; the estimate is the last number printed
  before that phrase. A stem that does not state them that way is refused
  rather than guessed at.
* **whether the units were chosen at random**, from the words "at random",
  "random sample", "randomly" — and their absence.
* **whether the page states the size of the population.** This is the whole
  difference between official item 2.7, where a statement about a *count* is
  the answer, and official item 1.4, where the same shape of sentence is a
  distractor. It is read off the stem and never assumed.
* **the table, re-added**: every row against its own total, every column
  against its own, both margins against the grand total, and the body against
  the sample size the stem names. No gate check reads a table as arithmetic.
* **the estimate the stem quotes against the table it came from** — official
  item 3.1 says 30% and its table says 240 of 799, and nothing else in the
  engine would notice if those two parted company.
* **each of the four sentences**: what it is about (the population's value,
  the number of members with the trait, the individual members, the sample,
  a misclassification, a wider group), how strongly it asserts it
  (approximately / plainly / with certainty), and over what set of values.

## The rule, as this file states it

    a random sample with a margin of error M around an estimate E supports
    exactly one thing: that the population's value plausibly lies in
    [E-M, E+M].

    It supports a statement about a count when, and only when, the page
    states the size of the population.

    It supports nothing about individual members, nothing about a group the
    units were not drawn from, and nothing with certainty.

    Without randomness it supports nothing about the population at all -- and
    then a sentence saying so is the answer, but only if it says *why*. "The
    sample did not include all the people who watch nature shows" is true of
    every sample ever drawn; refusing an inference on that ground would
    refuse every inference.

A sentence is supported when the pair (what it is about, whose value it is)
is something the study reports, its modality is no stronger than the study's,
and the study's own value set is **contained** in the sentence's.

Containment rather than equality is what catches two defensible answers on
one page: a sentence naming a *wider* interval is genuinely true, so a page
printing both it and the tight one has two answers and is refused. But
containment alone is too kind to the key, so there is one more test —
`key_is_tight`: a keyed two-sided interval must be the study's own interval,
not merely a true one. Without it, a rendering bug that widened the printed
endpoints would pass unnoticed, and fault 3 below proves it would not now.

## Three things the house note gets right, and how they are honoured here

* **Read the printed string, not your own parameters.** Every number this
  file uses comes out of `item.stem`, `item.table`, `item.choices` or
  `item.answer`. `item.params` is read once, for `params["scene"]`, to know
  which scenario's vocabulary to use — the same concession
  `evaluating_statistical_claims` makes, and for the same reason: a page
  cannot say that "all largemouth bass in the pond" is a smaller group than
  "all fish in the pond".
* **Check generated draws, not the source items.** The defect below lives in
  a scene configuration no official item uses. The eighteen official items
  are read too, at the end, by the same readers.
* **Prove the check can fail.** `--selftest` runs twenty-one injected faults
  and every one is caught. Each injection asserts that it actually changed
  something before it runs, so a splice that silently matched nothing fails
  as loudly as a reader that missed it.

## What it found

**Three live defects, all in generated draws, all fixed.**

1. **A range with no width, printed in the wrong surface.** The "applied the
   margin of error to the size of the sample" distractor printed its two
   counts through the *scene's* number format. A proportion scene fixes two
   decimal places for values like 0.49, so a headcount came out as `280.00`;
   and because a margin below 1 floors to nothing, the two endpoints were the
   same number. 98 draws in 1,500 of `sstat.interpret_percent` printed
   **"Plausible values of the number of seeds in the shipment that will
   sprout are between 280.00 and 280.00."** Every one passed the full gate:
   the option is a distractor, so nothing read it, and the key was right.
   Fixed by printing a count as a count and refusing the draw when the margin
   does not reach one member of the sample. The reader now checks that every
   printed range, right or wrong, is a range.

2. **The right verdict keyed for a reason that would refuse every sample.**
   On a self-selected draw, all three "no conclusion can be made" sentences
   came out supported, because the rule only asked whether the study reported
   anything about the population. So a page could be keyed to *"Since the
   sample did not include all the people who watch nature shows, no
   conclusion can be made"* — the right verdict, on a ground that is true of
   every sample there has ever been, printed beside the sentence that gives
   the actual reason. Fixed by giving a no-conclusion sentence a **ground**
   and checking the ground against the study: `not_random` holds when the
   units were not randomly selected, and `not_exhaustive` and `mixed_sample`
   never hold, because a sample is never the whole population and never holds
   only the members with the trait. Faults 14 and 15 keep it honest.

3. **The audit's sentence reader had stopped reading half the page.** Its
   interval pattern was case-sensitive, so `"Between 28.59% and 35.41% of all
   adults ..."` — the whole of official item 2.3's key, and every free draw
   in that wording — fell through to "the last number in the sentence" and
   was read as a point claim. It reported *0 of 4 statements hold*, which is
   the only reason it was noticed; a reader that had defaulted the other way
   would have passed everything. Its number class was `[\d,.]+`, which also
   swallows the full stop that ends a sentence and turned `0.91.` into a
   parse error. Both patterns are now folded once, on the way in, and the
   same fold is in this file.

## What the preview found that this file could not

Reading the rendered page is a separate pass and it found five more, none of
which any checker would have flagged, because each produced an item with
exactly one correct answer:

* **"More than 62 of the population are in the population."** A sentence that
  counts members of a population was offered on a scene measuring a *mean*.
  Those two sentences are now restricted to percent scenes.
* **"It is likely that all members measured between 69 and 73."** The
  anonymous study scene had been given a verb it has no use for.
* **"The percent ... is less than 27 or greater than 37%"** — the per-cent
  sign on the second endpoint only.
* **774 against 779** as two options on a stem that says "about how many".
  There is now a floor on how close two options may be: a tenth of the larger.
  The closest pair in any official item here is a third apart.
* **A class that splits down the middle**, where the group asked about, the
  group left out and half the total are all the same number, so three of the
  four options collapsed onto the key and the page filled up with
  `one_class` and `rate_of_groups` — two mistakes three orders of magnitude
  away from the answer. Those two pool entries are gone and the draw is
  refused instead.

## Running it

```
PYTHONPATH=. python3 satbank/topics/sample_statistics_and_margin_of_error/option_check.py
PYTHONPATH=. python3 .../option_check.py --draws 900 --template sstat.interpret_mean
PYTHONPATH=. python3 .../option_check.py --selftest
```

At 900 draws a template the sweep reads 10,811 generated items and the
eighteen official ones. **Re-run `--selftest` after any change to a
sentence's wording**: the readers are literal about what they parse, and a
reader that has stopped matching prints `0 defects` in exactly the same words
as one that checked everything. Watch the item counts too — a template that
started refusing every draw also prints zero.
