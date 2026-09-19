# Reading the wrong answers back, and the picture they are printed beside

`satbank check` asks whether the key is right. It never asks whether a
distractor is *also* right, and it never looks at the figure at all.

The clearest way to see what that costs is `tvdata.best_model`, before it was
guarded. The item prints a scatter of dots and four quadratics, and asks which
one models the data. Its key fitted the dots. So did one of its distractors —
`y = 2x² − 11x + 20` against `y = 2x² − 11x + 18`, on a chart whose gridlines are
two apart, is two curves nobody could tell apart. Every check was green:
`coverage`, `transcript`, `acceptance` and `audit` all only ever asked about the
key, which was right; `structure` counted surface forms, which matched; `prose`
found no placeholder; `capacity` counted distinct stems. An item with two correct
answers is not a bug any of them is shaped to find, because **an option that no
code ever solves cannot be found wrong by any amount of solving the key.**

`option_check.py` closes that, and the second hole beside it: the audit
re-derives an answer from `item.params`, which is the same set of numbers the
template drew the chart from, so a renderer that drifted away from the answer
would be invisible to it. This topic is almost entirely questions about pictures,
so the checker reads the picture.

```bash
PYTHONPATH=. python3 satbank/topics/two_variable_data/option_check.py
PYTHONPATH=. python3 .../option_check.py --draws 800 --template tvdata.fit_slope
PYTHONPATH=. python3 .../option_check.py --prove       # show the checks can fail
```

```
  ok   tvdata.point_read              400 items, 0 defects   (the plotted reading)
  ok   tvdata.predict_from_line       400 items, 0 defects   (the line's value)
  ok   tvdata.fit_slope               400 items, 0 defects   (the drawn slope)
  ok   tvdata.fit_equation            400 items, 0 defects   (one equation fits the dots)
  ok   tvdata.residual                400 items, 0 defects   (the gap to the line)
  ok   tvdata.curve_read              400 items, 0 defects   (the curve's value)
  ok   tvdata.interval_change         400 items, 0 defects   (one interval moves furthest)
  ok   tvdata.series_extreme          400 items, 0 defects   (one reading is the extreme)
  ok   tvdata.rate_of_change          400 items, 0 defects   (the rate matches the dots)
  ok   tvdata.slope_scaled            400 items, 0 defects   (the stated slope is the drawn one)
  ok   tvdata.association             400 items, 0 defects   (one sentence describes the direction)
  ok   tvdata.interpret_slope         400 items, 0 defects   (one sentence reads the slope right)
  ok   tvdata.model_type              400 items, 0 defects   (one shape matches the scenario)
  ok   tvdata.graph_statement         389 items, 0 defects   (one statement is untrue)
  ok   tvdata.best_model              400 items, 0 defects   (one model fits the dots)
  ok   tvdata.growth_compare          400 items, 0 defects   (one claim about the crossing)
  ok   tvdata.invest_compare          400 items, 0 defects   (one sentence about the two accounts)
  ok   tvdata.nonlinear_table         400 items, 0 defects   (one table is not linear)
```

All eighteen templates are covered. None is exempt.

## Reading the chart

The reader imports `generate` and `ItemError` from the engine and nothing else —
no template, no renderer, no solver, no chart code. It gets the finished item in
the state a student receives it, and everything after that comes from the printed
stem, the printed options and the SVG's own pixels.

**The scale comes from the printed gridline labels, not from the parameters.**
`chart()` collects every `class="gr"` gridline and every `class="lb xl"` /
`class="lb yl"` label, pairs each label with its own pixel position, and fits the
pixels-to-data map through the outermost pair. It then checks that map against
every label it was *not* fitted through, to a thousandth of the axis — which is
the width of the SVG's own two-decimal-place rounding. An axis that was
mislabelled, or labelled unevenly, fails there and nowhere else in the engine.

From that map it recovers, all in data coordinates:

| drawn as | read as |
|---|---|
| `<circle class="pt">` | a plotted point |
| `<line class="bf">` | the line of best fit, as `(slope, intercept)`, plus the length over which it is actually drawn |
| `<polyline class="cv">` | the curve, interpolated between its own samples |
| `<polyline class="sr">` | the line graph, as its vertices |
| the spacing of the `class="gr"` lines | the gridline step in data units, on each axis |

**Every line of best fit is refitted from the dots.** A line-of-best-fit item is
answerable only if the drawn scatter really has the drawn line as its
least-squares line. So `regression()` refits the recovered dots by the normal
equations — `m = (nΣxy − ΣxΣy) / (nΣx² − (Σx)²)` — and `agrees()` demands that the
refit and the drawn line be within a two-hundredth of the chart's height of each
other at both ends of the data. That is a pixel. It is checked for
`predict_from_line`, `fit_slope`, `fit_equation`, `residual`, `slope_scaled` and
`association`; `interpret_slope` additionally checks the drawn line against the
slope the stem writes down in its own equation.

**The gridline rule is enforced against the drawn gridlines.** Two options closer
together than the chart's own gridline spacing cannot be separated by any reader,
whatever the parameters said. `unique_nearest(..., step)` asserts it from the step
it recovered. For a slope the resolution is one gridline over the length the line
is actually drawn, which is what a reader measuring rise over run has; for a
plotted point the rule is half a gridline in x, which is the gap at which one dot
is visibly on a gridline and the next visibly is not. The templates enforce the
same rule themselves through `common.separated`, so this is the second of two
independent statements of it — a template that quietly stopped calling it would
still be caught here.

## What it asserts

Every check has the same shape: classify all four options, demand exactly one
hit, demand it is the keyed one. A second correct answer fails as loudly as a
wrong key. Grid-ins have no options, so there the printed answer must *be* the
value the picture shows, to within half a gridline.

| template | decided from the printed item |
|---|---|
| `point_read` | the plotted y at the x the stem names, with no other dot within half a gridline of it |
| `predict_from_line` | the refitted line's value at the x the stem names |
| `fit_slope` | the drawn line's slope |
| `fit_equation` | each printed equation re-parsed and scored against the refitted line over the data's x-range |
| `residual` | the gap between the named dot and the drawn line |
| `curve_read` | the drawn curve interpolated at the speed (or the two speeds) in the stem |
| `interval_change` | the move between the two readings each printed interval names |
| `series_extreme` | the reading each printed label names, years and month names alike |
| `rate_of_change` | the two dots the stem names, over the days between them |
| `slope_scaled` | the slope and the step the stem states, and that the drawn line has that slope |
| `association` | the sign of the refitted slope, against all four sentences |
| `interpret_slope` | the slope in the stem's own equation, against "each year" and "every 10 years" in all four |
| `model_type` | constant amount against constant percentage, rising against falling, read out of the scenario |
| `graph_statement` | the four statements re-decided against the recovered vertices |
| `best_model` | each printed quadratic re-parsed and evaluated at every recovered dot |
| `growth_compare` | `aˣ` against the printed line, sampled, with a touch point not counted as a crossing |
| `invest_compare` | the principal, rate and fee read out of the printed table |
| `nonlinear_table` | the differences of each printed table's own y-values |

## Proving it can fail

A check nobody has seen fail is worth nothing. `--prove` injects four known-bad
items and all four are caught:

```
  ok   a prediction keyed to the wrong option
         caught: the line's value is 7.80001, nearest '7.8', but the key is '8.7'
  ok   a line of best fit drawn at the wrong slope
         caught: the drawn line y = 1.909x + -1.592 is not the line of best fit of the
                 drawn points, which is y = 1.8x + -1.499
  ok   an association item with two true sentences
         caught: 2 of the four sentences are true of a line of slope -4.8
  ok   a table item with two nonlinear tables
         caught: 2 of the four tables are nonlinear
```

The second is the one to keep. Nothing is wrong with that item's parameters, its
key or its audit — only twelve pixels of the picture were moved, and the drift
between the figure and the answer is caught because the dots were refitted rather
than trusted.

## What it found

Six live defects, none of which any of the seven checks could see.

1. **Two options that both fit.** `best_model` and `fit_equation` had no guard
   that a distractor misses the data *visibly*, so a draw could print two curves
   or two lines that equally well modelled the dots. Both now require every
   distractor to miss by at least a quarter of the data's y-range somewhere in the
   plotted x-range, against the key's zero; the checker demands the same gap from
   the other side.
2. **`ordinal(1)` printed "11st".** The suffix table was keyed by the whole
   number rather than by its last digit, so every stem saying "during the 1st
   growing season" was malformed. Found by the checker failing to parse its own
   stem — and then visible on the page, which is where a reader would have met it.
3. **A point_read naming an x with three dots inside half a gridline of it.** The
   question "how many books were borrowed on the day with 82 visitors" is
   unanswerable when the chart is gridlined every ten and the dots are two apart.
   The template now refuses such a draw.
4. **A residual item with two tied "highest" points.** "For the charity with the
   greatest percent" needs one dot to be unambiguously the greatest; the template
   only refused an exact tie, so two dots a quarter of a gridline apart shipped.
   It now requires a full gridline between the highest and the next.
5. **`x = 5/7` in a stem.** `residual` spread its points evenly across the data
   range and then printed the x it was asking about, which was not a number a page
   would print. Its x-values now sit on the gridlines.
6. **A banker's-rounding disagreement.** `curve_read` rounded its key with
   Python's `round`, which rounds halves to even, while the audit rounded halves
   away from zero. On an exact half the two disagreed — and the item that printed
   was the one whose page cannot produce its own key. Both now use
   `common.snap`, and a stem saying *closest*, *nearest*, *approximately* or
   *best estimate* refuses an exact half outright rather than picking a
   convention the stem never states.

Reading the items on a page found six more that no check reads for: a stem
printing "rounded to the nearest ," with an empty placeholder, an axis labelled
0.5, 2.5, 4.5, eleven four-digit year labels overlapping each other, two y-axis
titles clipped by the frame, a stem saying "every 5 years" over a chart drawn
every 10, and a June temperature of 250 °F.

## `charts.py`, promoted: `plot.chart_scatter` and its two siblings

This topic drew its own charts rather than calling `plot.scatter`. The reason
is worth keeping, because it is the requirement the promoted version had to
meet — and it now lives in `satbank/plot.py` as `chart_scatter`,
`chart_series` and `chart_curve`, with `fmt_tick` and `ticks_between` beside
them. `charts.py` is gone; the families import from `plot` directly.

`plot.scatter` fits its axes to the data it is handed. That is right for a chart
that illustrates and wrong for a chart that is *the question*: two draws of the
same item can end up gridlined differently, so what a reader can resolve stops
being something the template knows. And because the gridlines carry no printed
labels of their own, there is nothing in the SVG to recover a scale from — the
picture cannot be read back, so nothing can check that it still agrees with the
answer. That older `scatter` is untouched and still there for a chart that only
illustrates.

The promoted version needed three things, and it has all three:

* **A stated window.** `x0, x1, y0, y1` are arguments, never inferred from the
  data. A caller that wants the old behaviour can compute them and pass them.
* **Stated gridline steps.** `xstep` and `ystep` are arguments too, with a
  separate `xlabel_every` / `ylabel_every` for how often a gridline is labelled.
  The step is the resolution of the chart, which is the number the item's
  separation guard has to compare its options against; it must not be a function
  of the data.
* **Label-bearing gridlines that can be read back.** Each labelled gridline emits
  its own `<text>` at the gridline's pixel position, in a distinguishable class.
  That is the whole readback contract: a checker can pair labels with positions,
  fit the pixels-to-data map, and verify it against the labels it did not use.
  Give the drawn line of best fit, the drawn curve and the drawn series each
  their own class as well, and the picture states everything a reader takes off
  it.

Nothing else in it was topic-specific, and all of it came across. The
axis-label thinning, the left gutter sized to the widest printed label and the
window aligned to the *labelled* gridlines rather than to every gridline are
all general chart housekeeping, and all three were added because the page
showed them missing.

### The one thing the promotion changed on the page

`plot._nice`, the label formatter for the older charts, typesets its minus;
`charts.fmt_tick` spelled the same sign with the keyboard hyphen. Two
formatters in one module disagreeing about a sign is exactly what the bank
spent a wave removing, so the promoted `fmt_tick` typesets it — which moved
**1,028 axis labels across 600 draws of the eighteen templates**, in
`fit_slope`, `best_model`, `predict_from_line` and `fit_equation`.

That is the whole of the change. Fingerprinting every field of every item —
stem, options, latex, answer, rationale, reasons, table, params and the figure
itself — over 600 draws of all eighteen templates gives the identical digest
before and after once the minus is folded back, so nothing else moved by a
byte.

And the reader was checked to be reading it rather than skipping it. `num()`
already folded U+2212 on the way in, which is why nothing broke; disabling
just that fold turns `fit_slope` from 0 defects in 600 draws to **600**,
`best_model` to 241 and `predict_from_line` to 53. A checker that had quietly
stopped parsing these labels would look exactly like one that passed, so the
difference had to be shown rather than assumed.
