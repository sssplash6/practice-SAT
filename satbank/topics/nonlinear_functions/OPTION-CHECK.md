# Reading the wrong answers back

`satbank check` asks whether the key is right. It never asks whether a
distractor is *also* right.

Nothing in the engine reads a wrong option as mathematics. `assemble_text`
takes four strings, shuffles them and records which one is the key;
`common.text_item` deduplicates them by the signature it was handed, not by
anything it solves; `audit` re-derives the key and compares; `structure` counts
surface forms and `prose` looks for placeholders. All of that is satisfied by
an item with two correct answers. The hole is structural, not a gap someone
forgot to fill: an option that no code ever solves cannot be found wrong by any
amount of solving the key.

`option_check.py` closes it for this topic. It parses the printed stem, the
printed table, the printed options and the SVG's own pixel geometry back into
mathematics, decides every option from that alone, and asserts that exactly one
option has the property the stem asks for and that it is the keyed one.

```bash
PYTHONPATH=. python3 satbank/topics/nonlinear_functions/option_check.py
PYTHONPATH=. python3 .../option_check.py --draws 800 --template nlfunc.exp_model
PYTHONPATH=. python3 .../option_check.py --selftest
```

```
  ok   nlfunc.evaluate                400 items, 0 defects   (the printed rule at the printed input)
  ok   nlfunc.exp_model               400 items, 0 defects   (the model the printed words describe)
  ok   nlfunc.exp_period              400 items, 0 defects   (the model that folds the period into the exponent)
  ok   nlfunc.graph_equation          400 items, 0 defects   (the equation the drawn curve follows)
  ok   nlfunc.graph_intercept         203 items, 0 defects   (the drawn curve's value on the y-axis)
  ok   nlfunc.factor_from_table       400 items, 0 defects   (the factor whose every zero the table shows)
  ...                                                         all 33 templates with options
  --   nlfunc.abs_value                 0 items   (grid-in only: no options to read)
  --   nlfunc.exp_power_table           0 items   (grid-in only: no options to read)
  --   nlfunc.zeros_constant            0 items   (grid-in only: no options to read)

11,904 items read back
```

Three templates answer only with a grid-in. They are reported by name as having
nothing to read rather than passed over silently, so the count of covered
templates is visible instead of implied.

## Why this topic in particular

It is the largest in the set and the worst exposed, three ways.

**Most of the options are equations, and an equation can be the same model
written differently.** `600(0.85)^t` and `600(17/20)^t` are one model;
`1,800(1.02)^(q/4)` and `1,800(1.02^(1/4))^q` are one model; `48(3³)^((1/6)x)`
and `48(729)^((1/18)x)` are one function. Eleven templates print equations as
options, and the engine keeps them apart by comparing the signature the
template handed it — a signature that says nothing about what was actually
printed. So every equation option here is **solved**, never compared with the
key's text: `exp_model` asks which option starts where the words say and
multiplies by what the words say, at three successive periods; `exp_from_table`
which option reproduces every printed row; `graph_equation` which option passes
through twenty-five points sampled off the drawn curve.

**A distractor can be a true statement about the model.** `interpret_initial`'s
"The minimum estimated number of advertisements during the 5 years was 1,708"
is true; it is simply not what the y-intercept says. So a sentence is decided
in two steps: what claim it makes, read from its own English, and what number
it attaches to that claim, checked against a number the item itself prints.

**Eight templates hang the question on a drawn curve.** A picture is only
checked if something reads it — both what it says and how finely it can be
read, since two options nearer together than the gridlines can separate are two
answers whichever one is keyed.

## What it parses

The reader is deliberately thin. `generate` is used only to obtain the finished
item, in the state a student would receive it, and `expr.parse` / `expr.agree`
read printed mathematics back. It imports nothing from this topic — not
`common.py`, not `figures.py`, not `audit.py` — so a rendering bug is invisible
to the renderer and visible here.

| printed form | read as |
|---|---|
| `x³ + 15`, `(x² − 6x + 3)/(x − 1)`, `4 + √x`, `16/x`, `(x + 0.25x)(50 − x)` | a function of x, through `expr.parse` |
| `2(3^x)`, `600(0.85)^t`, `233(1.70)^(x/2)`, `5(2^(−x))`, `48(3³)^((1/6)x)` | the same, with the caret and the typeset superscripts |
| `f(x) = …`, `d = …`, `60,000 = 50,000(1.03)^t` | split at the single equals sign; both sides read |
| `(0, −5)`, `(−2/3, 0)` | an ordered pair of exact Fractions |
| `−1 < r < 0`, `−3 < x < 1` | a range, tested against six sample values |
| `Day 12`, `I and II`, `Zero` | a labelled count, mapped to its number |
| `−11`, `2,300`, `9/7`, `3.5`, `$46.60`, `10%`, `2.5 × 10⁵` | a Fraction |
| a table, printed as a row per point or a row per series | two numeric columns |
| the SVG of a plane or of a labelled chart | the drawn curve, in data coordinates |

Two details in the parsing are load-bearing. The number pattern puts the
fraction alternative first, so `−7/6` is not read as `−7`. And a tick label is
drawn at a text *baseline*, several pixels off the tick it names, so each label
is snapped to the gridline it is nearest before the scale is fitted — reading
the label's own y attribute as the tick position put every chart four pixels
out, which was enough to make a marble's starting height read 13.337 instead of
13.

The figure reader consults no parameter of the item. The two `class="ax"` lines
fix where each scale's zero sits; the printed `class="lb"` tick labels fix how
many units a pixel is worth; the `class="gr"` gridlines fix how finely the
picture can be read; and the `class="ln"` polyline is the curve. It returns the
gridline spacing along with the curve, because that is what says whether two
options are separable at all.

## What it asserts

Every check is the same shape — classify all four, demand exactly one hit,
demand it is the keyed one — so a second correct answer fails as loudly as a
wrong key.

| template | property, decided from the printed item |
|---|---|
| `nlfunc.evaluate`, `nlfunc.exp_evaluate` | is the rule printed in the stem, evaluated at the input printed in the stem — and the four printed numbers are four different numbers |
| `nlfunc.solve_value` | substituted back into the printed equation, gives the printed target |
| `nlfunc.param_value` | the hidden constant is recovered from the printed `p(c) = v`, then the rule is evaluated |
| `nlfunc.y_intercept` | is the point `(0, f(0))` of the printed rule — or, in the identity mode, is `f(0)` itself |
| `nlfunc.x_intercept` | substituted into the printed rule, gives zero — or, for the NOT variant, is the only printed point that does not |
| `nlfunc.graph_intercept` | is where the **drawn** curve meets the drawn vertical axis, and no option lies within a gridline of the key |
| `nlfunc.graph_context` | is the **drawn** starting value, or where the **drawn** curve is highest, with the same separation rule |
| `nlfunc.graph_zeros` | is the number of times the **drawn** polyline changes sign |
| `nlfunc.graph_equation` | agrees with twenty-five points sampled off the **drawn** curve, to a fiftieth of a gridline |
| `nlfunc.exp_model`, `nlfunc.exp_anchor` | starts where the words say and multiplies by what the words say, checked at three successive periods |
| `nlfunc.exp_period` | gives the printed start at 0 and the printed factor after one whole period, with the period read out of the stem |
| `nlfunc.exp_from_table` | reproduces every row of the printed table |
| `nlfunc.exp_offset` | starts at the printed temperature, passes within half a degree of both printed readings, and settles on the printed room temperature |
| `nlfunc.exp_reach` | is the equation whose two sides are the printed target and the printed current value growing by the printed percent |
| `nlfunc.exp_rate` | is the factor a printed percent multiplies by, the percent a whole year takes off, or the range of r that makes the printed model behave as stated |
| `nlfunc.exp_two_points` | is the product of the two constants the two printed points force |
| `nlfunc.exp_display` | each Roman-numeral equation is evaluated at x = 0 and compared with the number literals it prints — "displays as a constant or coefficient", made concrete |
| `nlfunc.exp_rewrite` | the y-intercept appears among the option's own printed literals; or, for the coefficient mode, all four forms are asserted equivalent and the one whose printed coefficient of x is 1/c is found |
| `nlfunc.exp_steps` | the doublings are counted from the printed ratio, including the table's scientific notation |
| `nlfunc.vertex_value` | is where the printed parabola turns, or what it is worth there, found by numerical search on the parsed rule rather than by any algebra the generator shares |
| `nlfunc.vertex_symmetry` | is the printed intercept reflected in the printed vertex |
| `nlfunc.shift_max` | the four printed expressions come to four different numbers, one of which is the true maximum |
| `nlfunc.quad_must_be_true` | both claims are decided from the coefficient and axis the printed facts force |
| `nlfunc.quad_fit` | is the parabola with the printed initial height and printed vertex, at the printed time |
| `nlfunc.interpret_value`, `nlfunc.interpret_initial`, `nlfunc.interpret_rate`, `nlfunc.quad_feature` | the sentence matches the shape its family prints *and* names the numbers the item itself prints |
| `nlfunc.quad_word` | solves the equation the situation's own printed numbers set up |
| `nlfunc.build_expression` | is equivalent, by `expr.agree`, to the expression the words describe |
| `nlfunc.factor_from_table` | every zero of the printed factor is a zero the table shows, and the factor has no other zero |

## What it caught

**Four live defects**, all invisible to every one of the seven gate checks,
because every one of those stops at the key.

### 1. A printed option the printed stem cannot produce

`nlfunc.exp_anchor` printed its growth factor to one decimal place:

```
A model estimates that ... the number of beetles was 275% more than the number
at the end of the previous year. ... at the end of 2004 there were 342 beetles.

  * n = 24(3.8)^t        <- the key.  275% more is a factor of 3.75, not 3.8
    n = 24(2.75)^t
    n = 342(3.8)^t
    n = 342(2.75)^t
```

`dec(factor, 1)` rounded 3.75 to 3.8, so the keyed equation was not the model
the words describe and no option was. The audit agreed with itself because it
re-derived the exact 3.75 from the parameters and never looked at the string.
The fix is to print the factor exactly. This is the same shape as the defect
Linear Functions found in its Greenleaf item, and the lesson is the same: a
formatter that rounds silently turns a correct model into a wrong option.

### 2. A key that is not forced

`nlfunc.exp_rate` drew both directions of the population item:

```
P = P₀(1 + r)^y   If during this time the population of the city increases by a
fixed percent each year, which of the following must be true?

    r < −1
    −1 < r < 0
  * 0 < r < 1        <- the key
    r > 1
```

A *fall* by a fixed percent forces `−1 < r < 0`, which is why College Board
only asks that direction. A *rise* by a fixed percent forces only `r > 0`:
`r = 2` is a population that triples every year, satisfies the stem, and
satisfies none of the four printed ranges. The keyed option is not implied by
the stem. The rising variant is no longer drawn. The checker finds this by
testing six sample values of r against each printed range and against the
condition the stem states, rather than by trusting that one of the four must be
the answer.

### 3. A distractor that is genuinely a factor

`nlfunc.factor_from_table` offered, as a wrong answer, a single factor built
from one of the table's own zeros:

```
      | x  | h(x) |
      | −1 | 0    |
      |  0 | 8    |
      |  1 | 7    |
      |  2 | 0    |

  * (x + 1)(x − 2)     <- the key
    (x + 1)            <- "used only one of the two zeros" — but h(−1) = 0, so
                          this must be a factor too
```

If `h(−1) = 0` then `(x + 1)` divides `h`. The item asks which of the following
*must* be a factor, and two of the four must. Replaced with a repeated factor,
which is not forced by any table of values.

### 4. Two options that are the same polynomial

The same template drew mirror pairs of zeros. With zeros at −2 and 2 the key
`(x + 2)(x − 2)` and the sign-flipped distractor `(x − 2)(x + 2)` are two
spellings of one polynomial. The engine's own deduplication compared the
`[z1, z2]` signature, which differs, so it never noticed. Mirror pairs are now
rejected at draw time.

### Six injected faults

A check nobody has seen fail is worth nothing. `--selftest` builds six broken
option sets and confirms each is caught, with a message naming what went wrong:

```
  ok   caught a second correct answer, the same model written as a fraction: 2 of the four options are correct
  ok   caught the key rewritten with the root taken into the base: 2 of the four options are correct
  ok   caught the key under the wrong letter: the keyed option is not the correct one
  ok   caught a figure spliced in from another item: 0 of the four options are correct
  ok   caught a distractor moved inside what the chart can resolve: '13,800' is less than a gridline from the key on a chart gridlined every 2999.63
  ok   caught the key repeated under another species name: 2 of the four options are correct
```

1. the key's own model with its decimal base rewritten as a fraction — the
   "same model written differently" case, and the reason options are solved
   rather than compared;
2. `1,800(1.02)^(q/4)` restated as `1,800((1.02)^(1/4))^q`, which is the same
   function with the root moved into the base;
3. the answer letter moved two places, which is the half of the assertion the
   engine already does;
4. one `graph_intercept` figure spliced in from another item, so the options
   describe a curve that is not the one drawn;
5. a `graph_context` distractor moved to six tenths of a gridline from the key
   — a different number that no reader of the chart could separate from it;
6. an `interpret_rate` sentence repeated under a different species name, which
   is the "two true sentences" case the sentence checks exist for.

## Why five items are excluded, and why not fewer

Five of the 110 official items are excluded, which is the highest count in the
wave, so the reasoning belongs here where a reviewer will look for it.

| id | what its four options are |
|---|---|
| 1.2 | four two-column tables of readings taken off a drawn parabola |
| 1.4 | four coordinate grids showing four cubic curves |
| 1.11 | four coordinate grids showing four parabolas that differ only in where the vertex sits |
| 1.21 | four two-row tables of `x` and `h(x)` |
| 2.9 | four graphs of exponential curves differing in direction and steepness |

All five have **picture- or table-valued options**. There is no printed option
*text* in any of them, so the item cannot be answered from the text at all, and
a template would have to generate three wrong pictures as carefully as the
right one. `TOPIC-GUIDE.md` names exactly this case: "If a source item depends
on a picture you cannot regenerate from parameters, exclude it rather than ship
a template with a fixed picture."

Rendering a table option as a line of text — `x: 1, 2, 3; h(x): −2, 1, 6` — was
considered and rejected. It is not what the source prints, and the acceptance
check would then be comparing the engine against a format the engine itself
invented, which would make the 96% distractor figure meaningless for those
items. The other four topics in this wave that met the same problem handled it
the same way. Five of 110 is 4.5%, comfortably inside the 15% ceiling, and
every other picture-bearing item in the topic — 1.1, 1.7, 1.10, 1.13, 1.16,
1.18, 1.20, 1.23, 1.25, 2.31, 3.41 — *is* encoded, because in those the picture
carries the question and the options are text.

## Running the same check on another topic

The reader is topic-agnostic; the assertions are not, and should not be.

1. **A property each option has or does not have, decided from its printed
   text.** "Which equation models the population" becomes "which one starts
   where the words say and multiplies by what the words say"; "which form
   displays 1/c" becomes "which one's printed coefficient of x is the
   reciprocal of the c its own function implies". If the property cannot be
   decided from the printed option, say so rather than skipping quietly:
   `Unreadable` is reported by the driver and fails the run.

2. **A reader that shares nothing with the renderer.** Parse the string; do not
   re-render it and compare. Defect 1 above is exactly why — a check that went
   back through this topic's own `dec()` would have rounded 3.75 to 3.8 a
   second time and agreed with itself.

3. **Both halves of the assertion.** `hits.count(True) == 1` catches the second
   correct answer; `hits[keyed]` catches the right answer attached to the wrong
   letter. Checking only the second is what the engine already does.

Two further notes from doing it here. Assert over generated *draws*, not over
the source items: all four defects above live in draws no official item makes,
and two of them were in templates whose official item is perfectly fine. And
where a figure carries part of the question, read the figure — but read it
through its gridlines, not just its curve. Half of what a picture has to
provide is resolution: "the key and this distractor are six tenths of a
gridline apart" is a student's complaint, and no amount of re-deriving the key
will ever produce it.
