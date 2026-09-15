# Reading the wrong answers back

`satbank check` asks whether the key is right. It never asks whether a
distractor is *also* right.

Nothing in the engine reads a wrong option as mathematics. `assemble_text`
takes four strings, shuffles them and records which one is the key; `_text_item`
deduplicates them by the slope-and-intercept signature it was handed, not by
anything it solves; `audit` re-derives the key and compares; `structure` counts
surface forms and `prose` looks for placeholders. All of that is satisfied by an
item with two correct answers. The hole is structural, not a gap someone forgot
to fill: an option that no code ever solves cannot be found wrong by any amount
of solving the key.

`option_check.py` closes it for this topic. It parses the printed stem, the
printed table, the printed options and the SVG's own pixel geometry back into
linear algebra, decides every option from that alone, and asserts that exactly
one option has the property the stem asks for and that it is the keyed one.

```bash
PYTHONPATH=. python3 satbank/topics/linear_functions/option_check.py
PYTHONPATH=. python3 .../option_check.py --draws 2500 --template lin.from_points
PYTHONPATH=. python3 .../option_check.py --selftest
```

```
  ok   lin.from_points            2,500 items, 0 defects   (through both printed points)
  ok   lin.from_table             2,500 items, 0 defects   (fits every row of the table)
  ok   lin.define_line            2,500 items, 0 defects   (the stated slope and value)
  ok   lin.model_equation         2,500 items, 0 defects   (the situation's own rate and starting amount)
  ok   lin.tiered_cost            2,500 items, 0 defects   (the two printed prices at several sizes)
  ok   lin.interpret_slope        2,500 items, 0 defects   (the rate the coefficient stands for)
  ok   lin.graph_read             2,500 items, 0 defects   (the drawn value at the stated input)
  ok   lin.graph_shifted          2,500 items, 0 defects   (the drawn line lifted by the printed shift)
  ok   lin.unit_relation          2,500 items, 0 defects   (the same plane as the table's energy sum)
  ...                                                       all 23 templates

47,830 items read back
```

## Why this topic in particular

Three exposures, and one check shape for each.

**Two equations can be the same line written differently.** `y = 2x + 3` and
`2x - y = -3` and `4x - 2y = -6` are one line; so are `P(t) = 900 + 20t` and
`P(t) = 900 + 20(t - 0)`. Four templates print equations as options, and the
engine keeps them apart by comparing the `[num, den, num, den]` signature the
template handed it — a signature that says nothing about what was actually
printed. So every equation option here is **solved**, never compared with the
key's text: `lin.from_points` asks which option passes through both printed
points, `lin.from_table` which fits every printed row, `lin.tiered_cost` which
charges what the two printed prices come to at four different group sizes.

**A distractor can be a true statement about the model.** `interpret_slope`'s
"The video game system costs $100" is true; it is simply not what the slope
means. So a sentence is decided in two steps: what claim it makes, read from
its own English, and what number it attaches to that claim, checked against a
number the item itself prints. A sentence whose number the item never prints
anywhere cannot be checked at all — and that turns out to be the defect below.

**A drawn line is only checked if something reads the picture.** Four templates
hang the question on a figure. Both figure readers recover the line from pixels
and consult none of the item's parameters — and the chart reader also recovers
how finely the picture can be read, because two options a reader cannot
separate are two answers, whichever one is keyed.

## What it parses

The reader is deliberately naive. It knows how an SAT page prints a linear
expression and nothing else — no `Poly`, no `Exact`, no `common.py`. `generate`
is the only thing it imports from the engine, and only to obtain the finished
item, in the state a student would receive it.

| printed form | read as |
|---|---|
| `-2x + 7`, `9.25 + 0.50x`, `(5/6)x - 2`, `82 + x/20`, `w/191`, `x/5.7`, `(1/84)x` | a side, as `({variable: coefficient}, constant)` |
| `35 - (1/2)(p + c)` | the same, with the bracketed sum distributed |
| `j(x) = -2x + 7`, `y = 9.25 + 0.50x`, `P = w/191`, `d = 7m` | a function, as `(variable, slope, intercept)` |
| `x = 4.2k`, `xk = 4.2` | a row in two unknowns — *not* a function, and never a hit |
| `(-4, 0)`, `(0, -8)` | an ordered pair of exact Fractions |
| `((-45d - 12)/(20d), 0)` | an expression in one letter, evaluated at six values of it |
| `-11`, `2,300`, `9/7`, `3.5`, `$46.60`, `(3/4)` | a Fraction |
| a table, printed as a row per point *or* a row per series | two numeric columns |
| the SVG of a coordinate grid | the drawn line as `(slope, intercept)` |
| the SVG of a labelled chart | the same, from the tick labels and the polyline |

Two details in the parsing are load-bearing, and both cost a bug to learn.
`-7/6` must not read as `-7`, so the fraction alternative comes first in the
number pattern. And the expression evaluator is a fifteen-line
recursive-descent parser rather than `eval`, so `45d` and `2(p + c)` are
multiplications where they are written and nothing but digits, one letter,
brackets and the four operators is ever evaluated.

The grid reader locates the origin from the two `class="ax"` lines, takes
pixels-per-unit from the spacing of the `class="gr"` lines, and maps each
`class="sg"` endpoint back to data coordinates — exactly, in Fractions. The
chart reader cannot do that, because a chart's axes sit at the frame's edge
rather than at the origin, so it fixes the affine map from the printed tick
labels instead and works in floats. It returns two more numbers with the line:
the gap between the horizontal gridlines, and the run between the plotted ends.
Those say what the picture can be read to — four tenths of a gridline for a
value, and that over the run for a rate, since a rate read off a picture is two
such readings divided by the distance between them. A third figure predicate,
`figure_carries_numbers`, asks only whether a picture has any numeric label at
all. Both of those turned out to matter.

## What it asserts

Every check is the same shape — classify all four, demand exactly one hit,
demand it is the keyed one — so a second correct answer fails as loudly as a
wrong key.

| template | property, decided from the printed item |
|---|---|
| `lin.from_points` | passes through both points printed in the stem |
| `lin.from_table` | fits every row of the printed table |
| `lin.define_line` | meets every condition the stem states — `f(0)`, `f(1)`, a stated slope |
| `lin.model_equation` | is the rate and starting amount the printed words demand |
| `lin.per_unit_model` | is the `1 per N` rate the printed words demand, with its sign |
| `lin.tiered_cost` | charges what the two printed prices come to, at four group sizes |
| `lin.context_two_points` | passes through both printed readings — or is the third one they predict |
| `lin.unit_relation` | is the same relation as the table's own energy sum, tested at several values |
| `lin.parameter_intercept` | is the x-intercept at six values of the letter |
| `lin.x_intercept`, `lin.y_intercept` | is the point where the printed (or drawn) line meets that axis |
| `lin.graph_read` | is the rate, the value or the equation the **drawn** line gives, by a margin the drawn scale can resolve |
| `lin.graph_shifted` | is the **drawn** line lifted by the shift the stem prints |
| `lin.interpret_slope` | claims the modelled quantity per unit of the input, with the number the item prints |
| `lin.interpret_constant` | names the value at the start, at the shift, or in the year `t` really means |
| `lin.interpret_x_intercept` | names the moment the modelled quantity reaches zero |
| `lin.evaluate`, `lin.coefficient`, `lin.combine`, `lin.inner_scale`, `lin.table_facts`, `lin.model_value`, `lin.affine_conversion` | is the printed rule, evaluated — and no two options print the same number |

That last row is the one to be honest about. Those templates answer with a bare
number, and `assemble` keeps four distinct `Exact`s apart, so the classic second
right answer is hard to build there. What is *not* hard to build is two options
that print the same number after a formatter rounds them, so the check reads the
rule out of the stem (or the table), evaluates it, and demands both that exactly
one printed option equals it and that the four printed numbers are four distinct
numbers.

## What it caught

**Three live defects**, all invisible to every one of the seven gate checks,
because every one of those stops at the key.

### 1. A question with no defensible answer

`lin.interpret_slope`'s video-game context drew a picture with no scale on it:

```
The graph of the function f, where y = f(x), gives the total cost y, in dollars,
for a certain video game system and x games. What is the best interpretation of
the slope of the graph in this context?

    Each game costs $41.               <- the key
    The video game system costs $60.
    Each game costs $60.               <- equally defensible
    The video game system costs $41.
```

The stem states no number. The figure — `_scaleless_line` — is two axes and a
line, with no tick labels anywhere. So nothing in the item tells a student
whether the slope is 41 or 60, and "Each game costs $41" and "Each game costs
$60" are exactly as good as each other. Every draw of that context shipped this
way: 68 of 400 seeds, and the official item it is learned from among them.

The context already carried a `scaled=True` flag that nothing read. It now draws
a real chart with labelled axes — which is what College Board's own figure for
this item is: *"a line in the xy-plane with x from 0 to 10 and y from 0 to 500,
passing through (0, 100) and (10, 350)"*. The check reads the slope back off
that chart and matches it against the number each sentence names, so the two
`Each game costs $N` options are now told apart by the picture.

The other scaleless contexts are untouched and correct: "The electrician's
hourly rate" against "The electrician's onetime fee" needs no scale, because
neither option names a number.

### 2. A key that contradicted the table printed above it

`lin.context_two_points` prints the Greenleaf population item with its rate as a
decimal, because the source item's rate is `-1.6`. The generated draws chose a
gap of 8 to 20 years and arbitrary populations, and `dec(v, None)` renders a
rate with no finite decimal expansion by silently rounding it:

```
      | Year  | Population |
      | 2,000 | 1,172      |
      | 2,017 | 557        |

  * P(t) = 1,172 - 36t       <- the key.  1,172 - 36(17) = 560, not 557
    P(t) = 1,172 - 615t
    P(t) = 1,172 + 615(t - 2,000)
    P(t) = 1,172 - 36(t - 2,000)
```

The true rate is `-615/17 = -36.17...`. The engine recorded the exact rate in the
signature and the audit re-derived the exact rate, so the audit agreed with
itself; the *printed* option was a different line, and no option fit the table.
11 of 93 mcq draws. The fix is the guard the context already deserved — a
context that prints its rate as a decimal may only print a rate that has one —
and it is the same shape as the guards already there for half-way roundings and
non-integer intercepts. The source item still reproduces: `862` to `846` over
ten years is `-1.6`, which terminates.

### 3. Two options a reader of the graph could not choose between

`lin.graph_read` asks a value or a rate to be taken off a drawn line. Its
options were checked for being *different numbers*, which they always were, and
never for being far enough apart to be told apart on the picture:

```
The graph shows the estimated volume y, in liters, of the hydrogen when its
temperature is x kelvins. What is the estimated volume, in liters, when its
temperature is 600 kelvins?

    0
    24        <- the key
    25        <- "divided the input by the value"; a tenth of a gridline away
    600
```

The volume axis on that picture is labelled 0, 10, 20, 30. A student reads the
line at x = 600 and gets "about 24", or "about 25" — there is no reading of that
graph that separates them. The same shape turns up on the cab-fare item, where
`$6.00` was offered against `$6.14` on an axis with gridlines every ten dollars,
and once at `500/19` against `133/5` — two improper fractions, 1% apart, for a
question whose own stem says *estimated*. 44 of 800 mcq draws.

The fix is a separation rule in the generator, using the same `_ticks` that
places the gridlines: a misconception that lands within half a gridline of the
key (or, for a rate, half a gridline over the run) is not a wrong answer and is
dropped from the pool before the options are assembled. The check fails anything
inside four tenths of a gridline, so the gap between the two thresholds absorbs
the pixel rounding and a legal item can never be reported. All five official
`graph_read` items keep every distractor they had.

### Six injected faults

A check nobody has seen fail is worth nothing. `--selftest` builds five broken
option sets and confirms each is caught, with a message naming what went wrong:

```
  ok   caught a second correct answer, written differently: 2 of the four options are correct
  ok   caught the key rewritten as a scaled form: 2 of the four options are correct
  ok   caught the key under the wrong letter: the keyed option is not the correct one
  ok   caught a figure spliced in from another item: 0 of the four options are correct
  ok   caught a picture with no scale under numbered sentences: 2 of the four options are correct
  ok   caught two options a reader of the picture cannot separate: 2 of the four options are correct
```

1. the key's own line restated as `f(x) = 7 - 2x/1` and dropped into another
   slot — the "same line written differently" case, and the reason options are
   solved rather than compared;
2. the key with every number doubled and a `/2` on the end, which is the scaled
   standard form;
3. the answer letter moved two places, which is the half of the assertion the
   engine already does;
4. one `graph_shifted` item's figure spliced in from another, so the options
   describe a line that is not the one drawn;
5. the tick labels rubbed off the video-game chart — defect 1, kept as a
   regression;
6. a cab-fare distractor moved to four cents from the key, which is a twentieth
   of what that picture can resolve — defect 3, kept as a regression.

## Running the same check on another topic

The reader is topic-agnostic; the assertions are not, and should not be. Three
things are needed.

1. **A property each option has or does not have, decided from its printed
   text.** "Which equation defines f" becomes "which line passes through both
   printed points"; "which function models the charge" becomes "which one
   charges the right amount at four different group sizes"; "what does the slope
   mean" becomes "which sentence claims a rate of the modelled quantity per unit
   of the input, naming the number the item prints". If the property cannot be
   decided from the printed option, the option set cannot be checked this way —
   say so rather than skipping quietly. `Unreadable` is reported by the driver
   and fails the run.

2. **A reader that shares nothing with the renderer.** Parse the string, do not
   re-render it and compare. Defect 2 above is exactly why: a check that went
   back through `lin_text` would have rendered `-615/17` to `-36` a second time
   and agreed with itself. `option_check.py` re-implements the printing rules it
   needs in about a hundred lines; that duplication is the point.

3. **Both halves of the assertion.** `hits.count(True) == 1` catches the second
   correct answer; `hits[keyed]` catches the right answer attached to the wrong
   letter. Checking only the second is what the engine already does.

Three further notes from doing it here. Assert over generated *draws*, not over
the source items — all three defects above live in stem variants no source item
uses, and the first one reached the source item only because it reached every
draw of that context. Where a figure carries part of the question, read the
figure: two of the six injected faults are figure faults and a third is only
catchable by asking what the figure can resolve, and none of the three is
visible to any amount of reading the text. And read what the figure can *say*,
not only what it says: two of the three defects are a picture failing to carry
the information its own options need, and "the item prints no slope for the
options' numbers to be checked against" and "a reader can tell 0.6667 apart on
it" are better failure messages than any amount of re-deriving the key, because
they are the student's complaint rather than the engine's.
