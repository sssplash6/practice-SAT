# Reading the wrong answers back

`satbank check` asks whether the key is right. It never asks whether a
*distractor* is also right.

Nothing in the engine reads a wrong option as mathematics. `assemble_text` takes
four strings, shuffles them and records which one is the key; `audit` re-derives
the key and compares; `structure` counts surface forms and `prose` looks for
placeholders. All of that is satisfied by an item with two correct answers. For a
topic whose entire question is *which of these is equivalent*, that is the
sharpest hole in the project: equivalence is not a string comparison, so two
options that look nothing alike can be the same expression.

`option_check.py` closes it. It re-reads the item as a student receives it — the
expression printed in the **stem**, and the four printed **options** — evaluates
every option at a spread of rational points away from any pole, and asserts both
halves: exactly one option is equivalent, and the equivalent one is the keyed
letter.

```bash
PYTHONPATH=. python3 satbank/topics/equivalent_expressions/option_check.py
PYTHONPATH=. python3 .../option_check.py --draws 1000 --template eqx.product
```

```
  ok   eqx.combine_like             400 items, 0 defects   (equivalent to the printed expression)
  ok   eqx.which_factor             400 items, 0 defects   (the true verdict on the two candidates)
  ok   eqx.match_constant           400 items, 0 defects   (the only constant that makes the identity true)
  ...
8,400 items read, 0 defects
```

## What it reads, and what it shares

`generate` is the only thing imported from the engine, and only to obtain the
finished item. Nothing is taken from `item.params`: the question itself is parsed
out of the printed stem, so a stem and an option set that have drifted apart are
visible here and nowhere else.

The reader is a **second, independent implementation**. `audit.py` reads an
expression by recursive descent; this file tokenises, inserts the multiplication
signs the page leaves out, converts to postfix and evaluates a stack. The two
share no code and no algorithm, so a bug in one cannot hide in the other — and
neither goes back through the renderer, which is the point: a renderer that drops
a minus sign is invisible to any check that re-renders and compares.

| printed form | read as |
|---|---|
| `3x² − 2x + 3`, `−(1/6)x + 8`, `−2.95x² − 7.2x + 12.16` | a value at each sample point |
| `2a²(a + 3)`, `(x − 5)(x + 8)`, `8x(x⁹ − x⁸ + 11)` | implicit multiplication made explicit |
| `x⁻²y³z¹⁰`, `(x + 4)^(1/2)`, `2x³` | superscript runs and `^(…)` as exponents |
| `¹⁴√x`, `³√(x³y⁶)`, `y√y/(x²·³√x)` | a root of the given index |
| `9/((x + 1)(4x − 5))`, `x + 1 − 2/(x − 3)` | division, left-associative |

## What it asserts

Every check has the same shape — classify all four, demand exactly one hit,
demand it is the keyed one — so a second correct answer fails as loudly as a
wrong key.

| templates | property, decided from the printed page |
|---|---|
| the sixteen whose options are expressions | the option and the stem's expression agree at every sample point in one of three windows |
| `eqx.which_factor` (pick) | the polynomial vanishes where the option vanishes — the option is solved numerically, no division is done |
| `eqx.which_factor` (roman) | which of the two printed candidates divide, and therefore which verdict is true |
| `eqx.match_constant`, `eqx.factor_constant` (one letter) | the option's own printed value, put back into the printed identity, closes it |
| `eqx.match_constant` (cubic), `eqx.rational_combine`, `eqx.divide_remainder` (two letters) | both constants recovered from the printed equation by eliminating between two sample points; the four printed numbers compared to the combination the stem asks for |
| `eqx.factor_constant` (`sq_over`) | the option is a perfect square, which is the whole content of "which could be the value of c" |
| `eqx.coef_combination`, `eqx.exponent_value` | grid-ins: there are no options to read, and this says so rather than passing quietly |

## What it caught

**One live defect, in two templates.** `eqx.rational_combine` and
`eqx.divide_remainder` name their two constants with letters drawn at random,
and the draw did not exclude the letter already in use as the variable:

```
5/(t − 3) + 2/(t + 5) = (tt + p)/((t − 3)(t + 5))
The equation above is true for all t > 3, where t and p are positive constants.
What is the value of tp ?
```

`t` is the variable and `t` is a constant; `tt` is not an expression; and the
options are then numbers nobody can arrive at. Three per cent of
`rational_combine` draws and two per cent of `divide_remainder` draws were like
this. Every check the engine has passes them — coverage, transcript, acceptance,
audit, structure, prose and capacity all stop at the key, and the key's *value*
is still the one the algebra gives. The fix was to draw both constant letters
from the pool with the variable removed.

The official items never showed it, because `sources.py` pins the letters the
College Board item prints. It only appeared in generated draws, which is the
argument for running this over draws rather than over the source set.

**Three injected faults**, because a check nobody has seen fail is worth nothing.
Over the sixteen expression templates:

| injected fault | caught |
|---|---|
| the answer letter moved to a distractor | 638 / 638 |
| a second option that is also correct (the key printed twice, once with `+ 0`) | 638 / 638 |
| one minus sign dropped from the printed key | 330 / 330 |

The third is the one that matters most: it is a *rendering* fault, not a
mathematical one, and it is invisible to any check that compares the option
against something the renderer produced.

## Running the same check on another topic

Three things are needed, and only the first is topic-specific.

1. **A property each option has or does not have, decided from its printed
   text.** Here it is "takes the same value as the stem's expression at a dozen
   points"; elsewhere it will be something else. If the property cannot be
   decided from the printed option, say so — the grid-in rows above are labelled
   rather than skipped.
2. **A reader that shares nothing with the renderer, and preferably nothing with
   the audit either.** Parse the string; do not re-render it and compare.
3. **Both halves of the assertion.** `sum(hits) == 1` catches the second correct
   answer; `hits[keyed]` catches the right answer attached to the wrong letter.
   Checking only the second is what the engine already does.
