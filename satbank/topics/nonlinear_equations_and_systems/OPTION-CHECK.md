# Reading the wrong answers back

`satbank check` asks whether the key is right. It never asks whether a
distractor is *also* right.

Nothing in the engine reads a wrong option as mathematics. `assemble` sorts four
values and records which one is the key; `assemble_text` shuffles four strings;
`audit` re-derives the key and compares; `structure` counts surface forms and
`prose` looks for placeholders. All of that is satisfied by an item with two
correct answers.

For this topic the hole is not theoretical, and it is not one hole but three.

* **A line meets a curve twice.** "Which ordered pair is a solution to the given
  system?" is answered by *either* crossing, so the other crossing is a second
  key, not a distractor. So is any near-miss that happens to land on it.
* **"Which of the following is a possible value of x"** has the same shape one
  level down: both roots answer it.
* **Squaring a radical and clearing a denominator invent roots.** A candidate the
  squared equation has and the printed equation does not is exactly what the
  hard tier is testing, and a distractor that is secretly a genuine solution is
  the same defect wearing the other hat.

`option_check.py` closes all three. It substitutes every printed option back into
the **printed** equation — the radical still a radical, the denominators still
denominators — and asserts that exactly one option satisfies it and that it is
the keyed one.

```bash
PYTHONPATH=. python3 satbank/topics/nonlinear_equations_and_systems/option_check.py
PYTHONPATH=. python3 .../option_check.py --draws 2000 --template nleq.radical_equation
PYTHONPATH=. python3 .../option_check.py --selftest
```

```
  ok   nleq.isolate_sum                 400 items, 0 defects   (exactly one printed option rearranges the printed formula)
  ok   nleq.isolate_bracket             400 items, 0 defects   (exactly one printed option rearranges the printed formula)
  ok   nleq.isolate_factor              400 items, 0 defects   (exactly one printed option rearranges the printed formula)
  ok   nleq.isolate_denominator         400 items, 0 defects   (exactly one printed option rearranges the printed formula)
  ok   nleq.scale_relation              400 items, 0 defects   (exactly one printed inequality is equivalent)
  ok   nleq.square_equation             400 items, 0 defects   (exactly one printed option satisfies the printed equation)
  ok   nleq.absolute_equation           400 items, 0 defects   (the gridded value matches the printed equation's solutions)
  ok   nleq.quadratic_solve             400 items, 0 defects   (the gridded answer satisfies the printed equation)
  ok   nleq.quadratic_formula           400 items, 0 defects   (exactly one printed option names the solutions)
  ok   nleq.factored_equation           400 items, 0 defects   (exactly one printed option is the quantity asked for)
  ok   nleq.shared_factor               400 items, 0 defects   (the gridded value matches the printed equation's solutions)
  ok   nleq.cancel_squares              400 items, 0 defects   (exactly one printed option satisfies the printed equation)
  ok   nleq.scaled_quadratic            400 items, 0 defects   (the gridded value matches the printed equation's solutions)
  ok   nleq.radical_equation            400 items, 0 defects   (the gridded answer satisfies the printed equation)
  ok   nleq.rational_linear             400 items, 0 defects   (exactly one printed option satisfies the printed equation)
  ok   nleq.rational_quadratic          377 items, 0 defects   (the gridded answer satisfies the printed equation)
  ok   nleq.rational_combine            387 items, 0 defects   (exactly one printed option satisfies the printed equation)
  ok   nleq.curve_line_system           400 items, 0 defects   (exactly one printed option answers the printed system)
  ok   nleq.count_real_solutions        400 items, 0 defects   (exactly one option gives the printed count (2))
  ok   nleq.count_system_solutions      400 items, 0 defects   (exactly one option gives the printed count (0))
  ok   nleq.graph_solution              400 items, 0 defects   (exactly one option names the point the picture marks)
  ok   nleq.graph_count                 400 items, 0 defects   (exactly one option gives the drawn count (0))
  ok   nleq.function_meets              398 items, 0 defects   (the gridded value satisfies f(a) = g(a) and sits on the drawn curve)
  ok   nleq.discriminant_constant       400 items, 0 defects   (the gridded constant leaves the printed equation one solution)
  ok   nleq.symbolic_intersections      400 items, 0 defects   (exactly one option gives the count the signs force (0))
  ok   nleq.sum_product                 362 items, 0 defects   (the gridded value belongs to a pair satisfying both equations)
```

## What it reads

The reader is deliberately naive. It imports `generate`, to obtain the finished
item exactly as a student receives it, and `expr.parse`, to evaluate printed
text. It imports **nothing** from this topic: no template, no `kit`, no `audit`,
no renderer.

| printed form | read as |
|---|---|
| `√(2x + 6) + 4 = x + 3` | two sides, each evaluated at a candidate — a negative radicand simply raises, which is the extraneous-root test |
| `4x²/(x² − 9) − 2x/(x + 3) = 1/(x − 3)` | the same; a zero denominator raises, so an excluded value cannot pass |
| `(x − 4)(x + 2)(x − 1) = 0` | a polynomial recovered by evaluating it at whole numbers and interpolating, then solved by monotone intervals and bisection |
| `\|x − 4\| = 12` | not a polynomial: interpolation is rejected by its own probes, and the solutions come from a sign-change scan instead |
| `p = 8yv`, `c = 55g/y` | a formula in several letters; `8yv` is split into `8*y*v` before parsing |
| `(−5 ± √(25 + 168))/12` | both branches of the `±`, evaluated |
| `(1 + √3, √3)` | an ordered pair, each coordinate evaluated |
| `{−1, 5}` | a solution set |
| `4x − 16y > −32` | a half-plane, as (A, B, C) plus a direction, recovered by evaluating at (0,0), (1,0), (0,1) |
| the SVG of a drawn plane | origin and scale from the axes and gridlines; the marked point from its circle; the line from its segment; the curve from its polyline |

Two things in that table were the difference between a checker that works and one
that quietly passes everything.

**`expr.parse` lexes a run of letters as one variable name.** That is right for
`V_B` and wrong for `cy`, which is a product. Without splitting, every option of
every `isolate_factor` item raised `ParseError`, the checker counted them all as
wrong, and the failure it reported was "0 of the four options" — not a
disagreement about arithmetic but a page nobody could read. The same blind spot
was live in `kit.text_choices`, where `expr.agree` swallows `ParseError`
internally and returns "not equal", so the duplicate-key guard was a no-op for
exactly the items that most needed it. Both now split; the parser is shared and
was not changed.

**An interpolation has to be probed past any kink.** `|x − 4| − 12` fits a
straight line perfectly at 0, 1 and any probe below the kink at x = 4, so the
first version of this file "solved" absolute-value equations as though they were
linear and got the wrong roots. The probes now run out to ±57, and a fit that
survives them is a polynomial.

## What it asserts

Every check is the same shape — classify all four options, demand exactly one
hit, demand it is the keyed one — so a second correct answer fails as loudly as a
wrong key. Grid-ins have no options to compare, so there the assertion is that
the **gridded answer itself** satisfies the printed equation, which is where the
extraneous-root check earns most of its keep.

| template | property, decided from the printed page |
|---|---|
| `square_equation`, `quadratic_solve`, `cancel_squares`, `rational_*`, `radical_equation`, `curve_line_system` (numeric asks) | the option, substituted into the printed equation, satisfies it — and has the sign the stem asks for |
| `factored_equation`, `shared_factor`, `scaled_quadratic`, `absolute_equation` (sum asks) | the solutions are found from the printed equation and combined as the stem says |
| `isolate_*` | the other letters get values, the option says what the target is, and the whole lot goes back into the printed formula |
| `scale_relation` | one coefficient triple is a positive multiple of the other, with the sense preserved |
| `quadratic_formula` | each option, `±` expanded, is a root of the printed quadratic |
| `curve_line_system` (pairs) | each printed point satisfies **both** printed equations |
| `radical_equation` (solution set) | the set is the solution set exactly: no extraneous root kept, no genuine root dropped |
| `count_*`, `symbolic_intersections` | the count is decided from the printed equations; the symbolic one by trying many positive values and requiring the count not to depend on which |
| `discriminant_constant` | each printed constant is substituted back and the solutions of the result counted, because "no real solutions" is true of a whole range and an option set can easily print two that qualify |
| `graph_solution`, `graph_count`, `function_meets` | read out of the SVG: the marked point must lie on both drawn graphs, and the options are checked against the **picture** |

## What it found

**Four live defects, three of them items with two correct answers.**

**1. The other intersection, printed as a distractor.** `curve_line_system` seed
1 offered both points the two graphs share:

```
y = (x + 2)²
8x + y = 3
Which ordered pair (x, y) is a solution to the given system of equations?
  (−6 − √35, 51 + 8√35)   <- the key
  (−6 + √35, 51 − 8√35)   <- "the other point the two graphs share"  ← also correct
```

The pool entry was called `other` and its stated misconception was "named the
other point the two graphs share" — which is not a mistake, it is an answer. The
fix is not to delete that one entry: the origin is also a second key when the
origin is the other crossing, and so is a point one gridline along when that is
where the second crossing sits. Every candidate point is now substituted into
both printed equations before it is printed, and dropped if it satisfies both.
`pt()` is the single place a point becomes text, so nothing reaches the page
without passing that test.

**2. The same defect one level down.** `quadratic_solve` seed 15:

```
−2x² + (16/3)x + 70/3 = 0
Which of the following is a solution to the given equation?
  −5   −7/3 ← also correct   7/3   5 ← the key
```

Both roots answer "which of the following is a solution". Fixed by a shared
`_strike`, which removes every root from the pool for the asks that any solution
answers — and deliberately leaves it in for "the *positive* solution", where the
other root is a fair wrong answer because it is what a student who ignored the
word `positive` would pick.

**3. A line lying along a whole arm of a V.** `graph_solution` drew
`y = |x − 4| + 3` against `y = −x + 5`. The left arm of the V *is* that line:
every point of it is a solution, and the picture shows two graphs on top of each
other with one of them marked. The arm-by-arm crossing count returned 1, because
the degenerate arm divides by a zero slope and was being skipped. It now detects
the coincidence and refuses the draw.

**4. A figure that did not contain its own answer.** `function_meets` drew f over
a window chosen from the vertex, then keyed `a = 17`, where f(17) = −26 — far
below the drawn window. The picture could not show the agreement it was keyed on.
The window is now computed from the agreement points and the draw is refused if
either falls outside it. Only the SVG read-back can catch this: nothing that
works from the parameters ever looks at what was actually drawn.

Alongside these the run surfaced two defects in the checker itself (the letter
splitting and the interpolation probes, both above) and one in `graph_count`'s
picture reader, which skipped any sample pair with a zero gap and so missed
crossings that the sampler landed on exactly.

## Proving it can fail

`--selftest` injects seven known-bad items and requires every one to be caught:

```
  ok   caught: a distractor that is the other intersection
         -> 2 of the four options lie on both printed graphs
  ok   caught: the key replaced by the set that keeps the extraneous root
         -> 0 of the four options is the solution set of '√(x + 6) + 6 = x + 6'
  ok   caught: the answer letter moved one place
         -> the keyed option does not satisfy '5(x − 8)² = 125'
  ok   caught: a distractor that is the key written differently
         -> 2 of the four options rearrange '4p = y + 6v' correctly
  ok   caught: the marked point moved one gridline
         -> the marked point (3.000, 0.000) is not on the drawn line
  ok   caught: a count keyed to the wrong statement
         -> the keyed option does not say the printed system has 0 solutions
  ok   caught: a grid-in answer that makes a denominator zero
         -> the gridded answer '-2' does not satisfy '288/(x + 2) = x'

7 injected faults, all caught
```

The first attempt at this proved nothing, and that is worth recording. The
"other intersection" injection printed the second point as a rounded decimal,
`(−0.0839202, 3.67136)`, which is not a solution of anything — so the checker
correctly reported no defect, and the self-test correctly reported a miss. An
injection that is not actually a fault is a test that passes for the wrong
reason. Each case now **verifies its own premise** before it is used: the
injected point is checked against both printed equations, and `_show` refuses to
print a value it would have to approximate.

## Running the same check on another topic

1. **A property each option has or does not have, decided from its printed
   text.** For this topic that is nearly always "substitute it back into the
   printed equation", and the reason that is the right shape is that extraneous
   roots then need no special handling at all: a negative radicand and a zero
   denominator both simply raise, exactly as they fail for the student.

2. **A reader that shares nothing with the renderer.** Parse the string; do not
   re-render and compare. This file re-implements the printing rules it needs in
   about a hundred lines, and that duplication is the point — it is the third
   independent copy of the letter-run splitter in this topic, after `audit.py`
   and `kit.py`, and they are deliberately not shared.

3. **Both halves of the assertion.** `hits.count(True) == 1` catches the second
   correct answer; `hits[keyed]` catches the right answer on the wrong letter.

Three further notes. Assert over generated **draws**: every defect above lived in
a free draw, and the official option sets — the ones a source item pins — were
right throughout. Where a figure carries part of the question, read the figure;
defect 4 is invisible to everything else. And when a surface only a source item
uses needs checking — here the braced solution set, which free draws no longer
print because `check._prose` reads a brace as an unrendered placeholder — let the
self-test build it by passing the template its parameters, rather than dropping
the check.
