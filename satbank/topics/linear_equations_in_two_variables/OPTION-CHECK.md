# Reading the wrong answers back

`satbank check` asks whether the key is right. It never asks whether a
*distractor* is also right.

Nothing in the engine reads a wrong option as mathematics. `assemble` orders
four values, `assemble_text` shuffles four strings and records which one is the
key; `audit` re-derives the key and compares; `structure` counts surface forms
and `prose` looks for placeholders. Every one of those is satisfied by an item
with two correct answers, because every one of them stops at the key.

This topic is exposed to that in two particular ways. Two equations can be the
same line written differently — `2x + 4y = 10` and `x + 2y = 5` — and two
equations can model the same situation, which is what an item asking "which
equation represents this situation?" is made of.

`option_check.py` closes the hole. It parses the printed stem, the printed
table and the drawn SVG back into linear algebra, decides every option's status
from that algebra alone, and asserts that exactly one option has the property
the stem asks for and that it is the keyed one.

```bash
PYTHONPATH=. python3 satbank/topics/linear_equations_in_two_variables/option_check.py
PYTHONPATH=. python3 .../option_check.py --draws 2000 --template le2.which_table
PYTHONPATH=. python3 .../option_check.py --selftest
```

```
  ok   le2.model_standard             500 items, 0 defects   (models the printed situation)
  ok   le2.model_percent              500 items, 0 defects   (models the printed situation)
  ok   le2.material_table             500 items, 0 defects   (weighs the two remaining rock types)
  ok   le2.interpret_coefficient      311 items, 0 defects   (the rate for the right quantity)
  ok   le2.interpret_constant         500 items, 0 defects   (the total of both quantities)
  ok   le2.interpret_point            500 items, 0 defects   (names the printed pair in order)
  ok   le2.parallel_perpendicular     500 items, 0 defects   (the slope the relation demands)
  ok   le2.slope_two_points           199 items, 0 defects   (the slope through the two intercepts)
  ok   le2.intercepts                 243 items, 0 defects   (the y-intercept of the drawn line)
  ok   le2.line_equation              500 items, 0 defects   (the line the stem fixes)
  ok   le2.line_from_graph            500 items, 0 defects   (the drawn line for some positive R)
  ok   le2.graph_combinations         464 items, 0 defects   (the line the chart draws)
  ok   le2.table_equation             500 items, 0 defects   (holds at every printed row)
  ok   le2.which_table                500 items, 0 defects   (three pairs on the printed line)
  ok   le2.table_symbolic             195 items, 0 defects   (the slope of the printed table)
  ok   le2.table_line                 500 items, 0 defects   (the translated line's x-intercept)
  ok   le2.equivalent_system          500 items, 0 defects   (lies on both lines for every r)

7,412 items read back
```

## What it parses

The reader is deliberately naive. It knows how an SAT page prints a linear
equation and nothing else — no `Poly`, no `Exact`, no `common.py`. `generate` is
the only thing it imports from the engine, and only to obtain the finished item
in the state a student would receive it.

| printed form | read as |
|---|---|
| `3a + 4b = 25`, `(1/5)x + (1/7)y - 70 = 0`, `y = 0.1x` | a row `(coefficients, constant)`, everything moved left of the equals sign |
| `0.02x + 0.96y = (0.04)(24)`, `1.53a + 1.44b = 35(1.49)` | the same, with the right-hand side's product multiplied out |
| `4(x + y) = 70`, `4xy = 70` | a scaled sum of the variables, and a product of them — neither is a line |
| `18x + Ry = 36` | an x-coefficient, a y-coefficient and a constant, where one coefficient is the *letter* rather than a number |
| `(0, 8), (2, 148), (4, 288)` | three points, split on `), (` so a thousands separator inside a pair cannot be mistaken for the separator between them |
| `(-(3r)/2 + 7/2, r)` | two affine functions of the named parameter |
| `-11`, `1,277.94`, `9/7`, `3.5`, `(3/4)`, `-(1/4)` | a Fraction |
| the SVG of a coordinate grid | the drawn line as `(slope, intercept)` |
| the SVG of a plotted chart | the two intercepts the chart draws, as whole numbers |

Two readers are worth stealing. The **grid reader** locates the origin from the
two `class="ax"` lines, gets pixels-per-unit from the spacing of the
`class="gr"` lines, and maps each `class="sg"` endpoint back to data
coordinates; it consults none of the item's parameters, so it checks the
picture against the options rather than the options against each other. The
**chart reader** has no origin to work from — a bar-and-line chart's axes start
where the data does — so it builds its scale out of the printed tick labels
instead, and rounds the recovered intercepts to whole numbers only after
checking they are within a hair of one, because the SVG's pixels are rounded to
two places.

## What it asserts

Every check is the same shape — classify all four, demand exactly one hit,
demand it is the keyed one — so a second correct answer fails as loudly as a
wrong key.

| template | property, decided from the printed text |
|---|---|
| `le2.model_standard` | the option is the situation's own equation, whose numbers are read out of the printed stem, up to a nonzero multiple |
| `le2.model_percent` | the same, with the percentages and the blended total read out of the stem |
| `le2.material_table` | for the equation ask, the option weighs the two rock types the garden has left, in either order, against what is left of the total; for the interpretation ask, the option names the two rock types the printed equation does *not* price |
| `le2.interpret_coefficient` | the option is the bare coefficient of x, or — for the sentence asks — is the one sentence of the right kind naming the quantity the printed equation attaches that number to |
| `le2.interpret_constant` | exactly one sentence is a total of *both* quantities the stem names |
| `le2.interpret_point` | the sentence names the printed pair, in the printed order, as the quantities rather than as amounts short of a total |
| `le2.parallel_perpendicular` | the option is the slope, or the equation, the printed line and the printed relation demand |
| `le2.slope_two_points` | the option is the slope through the two printed intercepts |
| `le2.intercepts` | the option is b/a for the printed equation, or the y-intercept of the line read off the SVG |
| `le2.line_equation` | the option is the line the printed slope-and-point, or the two printed points, fix |
| `le2.line_from_graph` | the option is the line read off the SVG; the function it was shifted from; or the equation that becomes that line for some *positive* R |
| `le2.graph_combinations` | the option is the line the chart draws, or the value its two intercepts and the printed rate give |
| `le2.table_equation` | the option's equation holds at every row the table prints |
| `le2.which_table` | every pair the option prints lies on the equation in the stem |
| `le2.table_symbolic` | the option equals the printed table's slope at n = 0, 5, −7 and 3/2 |
| `le2.table_line` | the option is the value the table's line takes at the printed input, or the x-intercept it reaches after the printed translation |
| `le2.equivalent_system` | the parameterized point lies on both printed equations at r = 0, 1, −3 and 7/2 |

The templates left out answer with a bare number drawn from a set of four
distinct numbers — `le2.substitute`, `le2.context_substitute`, `le2.point_on_line`
and the grid-ins. Four distinct numbers cannot hold two correct answers, and
`audit` already re-derives which of them is right.

## What it caught

**One live defect, in `le2.which_table`.** The standard-form draw chose the two
coefficients independently, so it could produce `2x + 2y = -68` — an equation
symmetric in x and y. The pool's "read the table the wrong way round, taking the
y-values as the inputs" distractor then satisfies the equation exactly as well
as the key does:

```
2x + 2y = -68
Which table gives three values of x and their corresponding values of y for the given equation?
    (2, -40), (4, -38), (6, -36)      <- wrong
    (-36, 2), (-38, 4), (-40, 6)      <- correct, and offered as a distractor
    (-40, 2), (-38, 4), (-36, 6)      <- wrong
  * (2, -36), (4, -38), (6, -40)      <- correct, and the key
```

The full gate passes this item: coverage, transcript, acceptance, audit,
structure, prose and capacity are all green on it, because every one of them
stops at the key. The fix is one rejection — `Ac == Bc` is refused, with the
reason written where the next reader will find it.

**Two readability faults the same run surfaced**, both fixed in the templates
rather than in the reader: a `which_table` option printed as
`(2, -182), (6, -614), (10, -1,046)`, which is four commas in one pair and which
the reader could not split either, and a coefficient the reader took for two
unknowns because `Ry` had been parsed a letter at a time.

**Three injected faults**, because a check nobody has seen fail is worth
nothing. `--selftest` rebuilds the symmetric option set above by hand, doubles a
model equation into one of its own distractors (the `2x + 4y = 10` against
`x + 2y = 5` case), and moves a key to another letter. All three are caught, and
the message names what went wrong.
