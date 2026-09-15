# Reading the wrong answers back

`satbank check` asks whether the key is right. It never asks whether a
distractor is *also* right.

Nothing in the engine reads a wrong option as mathematics. `assemble_text` takes
four strings, shuffles them and records which one is the key; `audit` re-derives
the key from the parameters and compares; `structure` counts surface forms and
`prose` looks for placeholders. All seven gate checks stop at the key, so an item
with two correct options passes every one of them and reaches a student as a
question with no defensible answer. The hole is structural, not something
somebody forgot to fill in: an option no code ever solves cannot be found wrong
by any amount of solving the key.

`option_check.py` closes it for this topic. It parses the four printed option
strings — equations, constant pairs, Roman-numeral statement sets, ranges,
sentences and numbers — back into algebra, decides each option's status from
that algebra alone, and asserts that exactly one option has the property the stem
asks for **and** that it is the keyed one.

```bash
PYTHONPATH=. python3 satbank/topics/linear_equations_in_one_variable/option_check.py
PYTHONPATH=. python3 .../option_check.py --draws 6000 --template lin1.model_context
PYTHONPATH=. python3 .../option_check.py --selftest
PYTHONPATH=. python3 .../option_check.py --sources
```

```
  ok   lin1.solve                     4,860 items, 0 defects, 1,140 grid-ins
  ok   lin1.distribute                4,933 items, 0 defects, 1,067 grid-ins
  ok   lin1.then_value                4,823 items, 0 defects, 1,177 grid-ins
  ok   lin1.chunk                     4,800 items, 0 defects, 1,200 grid-ins
  ok   lin1.reciprocal                5,370 items, 0 defects,   630 grid-ins
  ok   lin1.count_solutions           6,000 items, 0 defects
  ok   lin1.identity_constant         2,961 items, 0 defects, 3,039 grid-ins
  ok   lin1.no_solution_constant      3,629 items, 0 defects, 2,371 grid-ins
  ok   lin1.identity_pair             6,000 items, 0 defects
  ok   lin1.no_solution_conditions    6,000 items, 0 defects
  ok   lin1.zero_chunk                6,000 items, 0 defects
  ok   lin1.equivalent_equation       6,000 items, 0 defects
  ok   lin1.context_solve             3,894 items, 0 defects, 2,106 grid-ins
  ok   lin1.model_count_mix           6,000 items, 0 defects
  ok   lin1.model_context             6,000 items, 0 defects
  ok   lin1.expression_in_terms       6,000 items, 0 defects
  ok   lin1.interpret_coefficient     6,000 items, 0 defects
  ok   lin1.percent_original          6,000 items, 0 defects
```

That is `--draws 6000`: 95,270 option sets read back. Every one of the eighteen
templates, plus all 47 official multiple-choice option sets (`--sources`; the
other 18 source items are grid-ins, which have no options at all).

## What it parses

The reader is deliberately naive and shares nothing with the renderer. It is a
tokenizer and a recursive-descent parser for the printed language of an SAT
algebra page, and it knows `kit.py`, `forms.py` and the templates not at all.
`generate` is the only thing imported from the engine, and only to obtain the
finished item in the state a student receives it.

| printed form | read as |
|---|---|
| `9m/7`, `-(1/6)x`, `(5/17)m`, `(17)(11)x`, `14(2n)`, `782 + 52(t - 2)` | a polynomial in the one unknown, exact in `Fraction`s |
| `w^2 + 18w`, `2/c` | a quadratic, and a division by the unknown — read so they can be *refused*, not skipped |
| `a(8 - m) - b = -18 - 6m` with `a = 6 and b = 66` | the same, with the printed pair substituted first |
| `(24j + 28)/4 - b/3 = a(j - 3)` | the same, with one constant left open and solved for |
| `21 = 18`, `10x + 25 = 25` | `lhs - rhs`, then `one` / `none` / `many` off the two coefficients |
| `I. a = 4 II. b ≠ 5/2 III. a = 10` | three claims about the pinned constants |
| `-1 and 4` | a closed range |
| `The number of years it took the tree to double its height` | a number: `start / rate` |
| `-11`, `2,300`, `9/7`, `3.5`, `$623,500`, `40%` | a `Fraction` — the typeset minus, thousands separators, money and percents all handled |

A shape the reader has not been taught raises `Unreadable` and is counted as a
defect. An option nobody parses is an unchecked option, which is the thing the
script exists to stop.

## What it asserts

Every check has the same shape — decide the property for all four options from
their printed text and the printed stem, demand exactly one hit, demand it is the
keyed one — so a second correct answer fails as loudly as a wrong key.

| template | property, decided from the printed text |
|---|---|
| `lin1.solve`, `lin1.distribute`, `lin1.then_value`, `lin1.chunk`, `lin1.reciprocal` | the equation is on the page: solve *it*, evaluate what the page asks for, and exactly one printed number is that value |
| `lin1.count_solutions` | the printed equation's solution count, with all four claims required to be different counts |
| `lin1.identity_constant` | substituting the printed value leaves an identity — for some value of the second constant, where the stem prints two |
| `lin1.no_solution_constant` | substituting the printed value leaves a contradiction |
| `lin1.identity_pair` | substituting the printed pair `(a, b)` leaves an identity |
| `lin1.no_solution_conditions` | `m*v + c = a(v + b)` is empty exactly when `a = m` and `ab ≠ c`, so `a` is pinned, `ab` is anything but `c` and `b` is anything but `c/m`; each printed statement is tested against that and exactly one option names the true ones |
| `lin1.zero_chunk` | the bracket's forced value lies in exactly one printed range, endpoints included, and strictly inside the keyed one |
| `lin1.equivalent_equation` | the option has the same solution set as the printed equation — equivalence by definition, so the template where two options can both be right |
| `lin1.context_solve` | the sentence, read scene by scene, forces one value, and exactly one printed number is it |
| `lin1.model_context`, `lin1.model_count_mix` | the option, **solved**, has the solution the words force. Two equations that model the same situation are one equation however differently they print |
| `lin1.expression_in_terms` | the option is the same polynomial in the variable as the words describe |
| `lin1.interpret_coefficient` | the sentence, evaluated against the printed equation, comes out at the number the stem asks about |
| `lin1.percent_original` | the option is the unique closest to the price the table and the two discounts imply |

## What it caught

**Five live defects**, in five different templates. Every one of them passes
coverage, transcript, acceptance, audit, structure, prose and capacity.

**1. `lin1.equivalent_equation` — 74 items in 2,426 (3%).** Equivalent equations
are the ones with the same solution set, and in one unknown that is all
equivalence means. When the constant term equals the right-hand side, the option
that divides only the constants keeps the solution where it was:

```
Which of the following is equivalent to 10x + 25 = 25?
    2x + 5 = 5      <- the key                          x = 0
    10x + 5 = 5     <- "divided the constants only"     x = 0  as well
    2x + 25 = 5
    2x + 5 = 25
```

The option that subtracts the factor from every term collides the same way. The
fix computes the solution of all four wrong equations and refuses the draw if any
of them is the key's.

**2. `lin1.model_count_mix` — 9 items in 2,491.** The distractor that weights
each count by its length happens to land on the same `n`:

```
A manufacturing plant makes 9-inch, 7-inch, and 4-inch ceramic tiles... is 7 times
the number n of 7-inch... makes 60 ceramic tiles total. Which equation represents
this situation?
    9n + 7n + 4n = 60     <- 20n = 60, n = 3
    8n + 36 = 60          <- the key,  n = 3
```

Both equations hold at `n = 3`, so both model the day — and the polygon wording
of this same template asks outright for the equation that "must be true for the
value of `n`", which both are. The fix rejects a draw where any wrong equation
holds at the key's `n`.

**3. `lin1.model_context`, the unit-profit shape — 7 items in 5,993.** The same
failure, and the one that needed the most draws to surface:

```
A certain product costs a company $56 to make... a commission equal to 15% of the
sales price... the sales price is $160... a profit of $18,720?
    (0.15(160) + 56)u = 18,720      <- 24 + 56 = 80,  u = 234
    (160(1 - 0.15) - 56)u = 18,720  <- the key: 136 - 56 = 80,  u = 234
```

Adding the commission to the cost and taking it off the price give the same
number per unit whenever `make = price(1 - 2c)/2`, and the two options are then
one equation printed two ways. The fix gives each of the four shapes the
solutions its three wrong equations have and refuses the draw when one of them is
the key's.

**4. `lin1.interpret_coefficient` — 37 items in 2,463.** The sentences are claims
about a number, and two of them are true claims whenever the numbers line up:

```
4n + 16 = 28   A tree had a height of 16 feet when it was planted...
Which of the following is the best interpretation of the number 4?
    The average number of feet that the tree grew per year        <- the key
    The number of years it took the tree to double its height     <- 16/4 = 4 too
```

That is `start = rate²`. The second shape is `final = rate²`, where "the average
number of years it takes similar hedges to grow 16 feet" is `16/4 = 4` as well.
The fix evaluates all three wrong readings — `start/rate`, `start + rate`,
`final/rate` — and refuses the draw if any of them comes out at the rate itself.

**5. `lin1.context_solve`, the overtime scene — 54 items in 1,578.** Here the
count was not two right answers but *none*:

```
...her total earnings for that day were $206.62. What is her regular hourly wage?
    $21.75   <- the key, and 206.62 / 9.5 = 21.7494...
```

The wage is drawn in quarter-dollars and the day comes to 9.5 or 12.5 paid hours,
so the total lands on a half-cent and the stem rounds it. Nothing downstream can
see this: `audit` re-derives the key from `wage`, never from the string the page
prints. The fix refuses a total that will not print exactly in cents.

**Seven injected faults**, because a check nobody has seen fail is worth nothing.
Two of the seven are defects 2 and 4 above, rebuilt by hand now that the
generators refuse to draw them; the other five are a model equation rearranged
(`782 + 52(t - 2) = 886` against `52t = 208`), an equivalent equation scaled, a
keyed constant pair printed twice in different digits, one solution count spelled
two ways, and the key moved to another letter. Each is reported, by the right
half of the assertion.

## What it does not assert

Two things, said out loud rather than skipped quietly.

* **Grid-ins.** 18 of the 65 official items and about a fifth of the draws have
  no options at all. The value is still re-derived from the printed stem for
  every multiple-choice draw of the same templates, which is where a stem that
  disagrees with its key would show.
* **A stem's own side conditions.** `identity_constant`'s third shape prints
  "`b` and `a` are constants, and `b > 0`" and may still offer a negative option.
  That is a freebie a student can cross out without algebra, but it is not a
  second right answer, and this script does not rule on it.
* **Two *wrong* options that are the same equation.** About one draw in a
  thousand of `model_context` offers `6n = 61 + 5` and `5n + 6 = 61`, which are
  both `n = 11` and both wrong. The item still has exactly one defensible
  answer, so the assertion stands; it is inelegance, not a defect.

## Running the same check on another topic

Three things are needed, and the first is the whole design.

1. **A property each option has or does not have, decided from its printed
   text.** "Which equation models this" becomes *solve it and compare the
   solution* — never compare the strings, because `782 + 52(t - 2) = 886` and
   `52t + 678 = 886` are the same equation. "Which values make it an identity"
   becomes *substitute the printed pair and classify*. "Which statement is the
   best interpretation" becomes *evaluate the sentence as a number*. If the
   property cannot be decided from the printed option, say so rather than
   skipping.

2. **A reader that shares nothing with the renderer.** Parse the string; do not
   re-render it and compare. A renderer bug that drops a minus sign is invisible
   to any check that goes back through the renderer, and it was reading the
   *printed* `$206.62` rather than the parameter behind it that turned up defect
   4. The parser here is about 200 lines and owes nothing to `kit.py`; that
   duplication is the point.

3. **Both halves of the assertion.** `hits.count(True) == 1` catches the second
   correct answer; `hits[keyed]` catches the right answer attached to the wrong
   letter. Checking only the second is what the engine already does.

And check generated *draws*, not only the source items. All five defects here
live in parameter combinations no official item uses: the official
`equivalent_equation` has `b = 6` against `d = 12`, the official growth scene has
`rate = 2` against `start = 6`, and both were fine. 47 official option sets read
back clean, while the defects were 174 items in a 2,500-draw sweep of every
template and 7 more that only a 6,000-draw sweep of `model_context` reached.
Raise `--draws` until the count stops moving.
