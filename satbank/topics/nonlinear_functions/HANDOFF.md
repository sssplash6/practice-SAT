# Nonlinear Functions — state

Complete. The gate is green, `option_check.py` is clean, `OPTION-CHECK.md` is
written, and a page of items has been read by eye and by rendered figure.

```
Nonlinear Functions  [nonlinear_functions]  PASS
    ok   coverage    105/110 encoded, 5 excluded
    ok   transcript  110/110 items
    ok   acceptance  105/105 answers, 96% of official distractors recreated, 76/84 option sets complete
    ok   audit       10,800 items re-derived
    ok   structure   99% of distractors named
    ok   prose       10,800 items read
    ok   capacity    33,577+ distinct items
```

`option_check.py`: 33 templates with options, 400 draws each, **11,877 items
read back, 0 defects, 0 unreadable**. Three templates answer only with a
grid-in and are reported by name as having nothing to read.
`--selftest` catches all six injected faults.

## What is here

* `material/transcripts/nonlinear_functions.json` — all 110 items, transcribed
  from the images.
* 36 templates in seven family modules, plus `common.py` (rendering),
  `figures.py` (this topic's own SVG, because `plot.curve` fits gridlines to
  its data and a y-intercept item needs gridlines a reader can count),
  `audit.py`, `sources.py`, `option_check.py`, `OPTION-CHECK.md`.

| family file | templates |
|---|---|
| `families/evaluate.py` | `nlfunc.evaluate`, `exp_evaluate`, `solve_value`, `param_value`, `abs_value` |
| `families/intercepts.py` | `nlfunc.y_intercept`, `x_intercept` |
| `families/graphs.py` | `nlfunc.graph_intercept`, `graph_context`, `graph_zeros`, `graph_equation` |
| `families/exponential.py` | `nlfunc.exp_model`, `exp_period`, `exp_from_table`, `exp_offset`, `exp_anchor`, `exp_reach` |
| `families/exp_forms.py` | `nlfunc.exp_rate`, `exp_two_points`, `exp_display`, `exp_rewrite`, `exp_steps`, `exp_power_table` |
| `families/quadratic.py` | `nlfunc.vertex_value`, `vertex_symmetry`, `shift_max`, `quad_must_be_true`, `quad_fit` |
| `families/interpret.py` | `nlfunc.interpret_value`, `interpret_initial`, `interpret_rate`, `quad_feature` |
| `families/word.py` | `nlfunc.quad_word`, `build_expression` |
| `families/polynomial.py` | `nlfunc.factor_from_table`, `zeros_constant` |

## The five exclusions (4.5%; the wave's highest count)

All five have **picture- or table-valued options**, so there is no printed
option text to carry the answer and a template would have to generate three
wrong pictures as carefully as the right one. Reasoning and the rejected
alternative are set out in full in `OPTION-CHECK.md`, under "Why five items are
excluded, and why not fewer".

| id | what its four options are |
|---|---|
| 1.2 | four two-column tables of readings taken off a drawn parabola |
| 1.4 | four coordinate grids showing four cubic curves |
| 1.11 | four coordinate grids of parabolas differing only in vertex position |
| 1.21 | four two-row tables of `x` and `h(x)` |
| 2.9 | four graphs of exponential curves differing in direction and steepness |

Every other picture-bearing item — 1.1, 1.7, 1.10, 1.13, 1.16, 1.18, 1.20,
1.23, 1.25, 2.31, 3.41 — is encoded, because there the picture carries the
question and the options are text.

## The three acceptance failures (history; all fixed)

* **2.19** — the engine printed "brachiopods species" where College Board
  prints "brachiopod species". One `thing` string was serving both the plural
  stem and the singular option sentences. Fixed at the one place the stem needs
  the plural.
* **3.9, 3.14** — `ItemError: the key would be the only option of its surface
  form`. The local guard was stricter than the gate's own `check._shape` (it
  tested U+2212 as well as the ASCII hyphen) and was being applied to source
  items, where College Board's option set is the authority — 3.14's key
  genuinely is the only option containing a slash, and the gate never runs
  `structure` on source items anyway. Fixed by aligning the guard with the gate
  and skipping it when a source item names its own `wrongs`.

## What the preview pass found

`tools/preview.py nonlinear_functions --per 3`, read as text, and the figures
rendered to PNG and looked at. It has never come back empty on this project and
did not here: **eighteen defects**, none of which any of the seven gate checks
can see.

**Prose and rationale**

1. `evaluate` (rational): "p(35) = 22/35 = 22/35" — the same quotient printed
   twice when it is already in lowest terms.
2. `shift_max`: "f is greatest at t = 83/8 = 83/8", same cause.
3. `quad_fit` (table): "p(x) = 2(x − 10)² + 0" and "4(x − 36)² + −1".
4. `zeros_constant`: "(x − −3)(x − 1)(x − 5)".
5. `exp_power_table`: "g(x) = a^(4x − −1)".
6. `exp_display`: "the answer is neither i nor ii" — Roman numerals lowercased.
7. `quad_must_be_true`: the same lowercasing in three distractor reasons.
8. `graph_zeros`: "f(x) = 0 for one values of x".
9. `exp_steps` (bounce): the rationale ended "= 27/2 feet" where the grid-in
   answer is 13.5; `quad_fit` (three points) likewise printed "13,143/5".
10. `interpret_initial`: "At t = 0 the power is 1" on models written in x.
11. `interpret_value`: a thrown object's distractor was explained as "a
    multiplier of the previous year's value".
12. `vertex_value` (factored): a distractor's reason described an arithmetic it
    did not perform.

**Typography**

13. Every negative numeric option printed an ASCII hyphen — `Exact.plain()`
    writes `-11` where the source typesets `−11`. Every numeric-option
    template now renders through this topic's own `num()`.
14. Every figure's tick labels did the same (`-10`, `-2`) and printed `2000`
    without a thousands separator.

**Items that were internally wrong or degenerate**

15. `exp_rate`: with the period drawn as 4, the stem counted months, asked for
    a yearly percent, and printed an exponent of `x/4` — the item contradicted
    itself, and the checker had encoded the same wrong assumption. The divisor
    is now twelve.
16. `exp_steps` (culture): the doubling count was being reused from the
    year-counting branch, so the answer could be a day the table already
    prints, and "Day 0" could appear as an option.
17. `exp_model` (jackrabbits): "had reached 10 billion" was a fixed constant
    that did not follow from the generated start, rate and span. It is now
    computed and printed as a magnitude.
18. Degenerate option bases: a 100% rise and a 1% rise each produced a
    distractor of `(1)^t`; an exponent of 1 collapsed three of four
    misconceptions onto the key. All now refused at draw time.

**Figures** (rendered with `qlmanage` and looked at; the browser extension was
not connected)

19. `graph_intercept`'s decaying exponential came out a 180×396 sliver with the
    tick labels sitting on top of the curve — the plane forced one pixel scale
    on both axes, and this shape's y range is fourteen units against five of x.
    The two axes are now scaled independently, as a printed SAT plane is, and
    the decay and growth windows follow the source's own (x from −1 to 1).
20. `graph_equation`'s quartic was drawn to the height of its own tails, which
    made all three zeros and the repeated root sit flat on the axis — the
    question was unanswerable from the picture. The window is now set by the
    turning points between the outermost zeros, which reproduces College
    Board's own y range for item 2.31 exactly.
21. `quad_feature`'s marble chart had up to sixteen y labels touching each
    other on a 190-pixel axis.
22. `graph_context`'s "3,000" tick collided with the axis's `x` glyph.
23. An axis could be drawn with twenty-eight labels on it; label density is now
    thinned automatically, and the origin's `O` is dropped when the units are
    too narrow for it to clear the `−1` label.

## Live defects `option_check.py` found (all fixed)

Detailed in `OPTION-CHECK.md`. In short: a growth factor printed to one decimal
place so `24(3.8)^t` could not come from a 275% rise; a rising-rate variant
keyed `0 < r < 1` when the stem only forces `r > 0`; a `factor_from_table`
distractor that was genuinely a forced factor; and a mirror pair of zeros that
made the sign-flipped distractor the same polynomial as the key.

## Nothing outside the topic was changed

Only `satbank/topics/nonlinear_functions/` and
`material/transcripts/nonlinear_functions.json`. No change to the shared core
was needed. `expr.parse` / `expr.agree` read every printed form this topic
produces, and `assemble` / `assemble_text` needed no extension — the one thing
worth noting for the core is that `Exact.plain()` writes an ASCII hyphen, which
every topic with signed numeric options has to paper over with its own
`fmt_value`; a typeset minus there would save each of them a step.
