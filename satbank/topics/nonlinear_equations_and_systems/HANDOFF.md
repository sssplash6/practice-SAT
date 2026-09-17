# Nonlinear Equations and Systems — handoff

Paused mid-build, on budget. Nothing is stubbed: every template listed in
`__init__.py` is written and generates items. Three defects are open and named
below. **The gate is not green** — do not report this topic as done.

Last quick gate (`--quick`), for reference:

```
  ok   coverage    84/85 encoded, 1 excluded
  ok   transcript  85/85 items
 FAIL  acceptance  79/84 answers, 99% of official distractors recreated
 FAIL  audit       1,118 items re-derived
  ok   structure   100% of distractors named
  ok   prose       1,118 items read
  ok   capacity    5,689+ distinct items
```

## State of the templates

32 templates in five families; all written, none a stub.

| file | templates |
|---|---|
| `families/literal.py` | `isolate_sum`, `isolate_bracket`, `isolate_factor`, `isolate_denominator`, `scale_relation` |
| `families/solve.py` | `square_equation`, `absolute_equation`, `quadratic_solve`, `quadratic_formula`, `factored_equation`, `shared_factor`, `cancel_squares`, `scaled_quadratic`, `radical_equation`, `rational_linear`, `rational_quadratic`, `rational_combine`, `product_roots_constant`, `paired_quadratics` |
| `families/system.py` | `curve_line_system`, `sum_product`, `secant_slope` |
| `families/condition.py` | `count_real_solutions`, `count_system_solutions`, `symbolic_intersections`, `discriminant_constant`, `tangent_constant`, `tangent_point`, `integer_roots_constant` |
| `families/graph.py` | `graph_solution`, `graph_count`, `function_meets` |

`figure.py` is a local SVG drawer (grid + polyline curve + segment + marked
point), because `satbank/figures.py` draws only straight segments and is shared.
Class names match it (`ax`, `gr`, `sg`, `pt`) plus `cv` for a curve, so the same
pixel-geometry reader works on both.

`audit.py` has a solver for all 32 `kind`s. It shares no code with the families:
it finds roots by sign-change sweep and bisection (never a discriminant, never
the quadratic formula), counts solutions by counting those roots, finds a
"leaves exactly one solution" constant by bisecting on the root count, and for
option-valued items reads the four printed strings back and decides which one is
right.

## `nleq.isolate_factor` — resolved, and it was not float arithmetic

**It was a reader limitation in my `audit.py`, not an arithmetic error, and not a
tolerance. Nothing was papered over.**

The coordinator read `g = 7.040000000000001` in the error text as float residue.
It is not: that number is the audit's own sample value for the product `j·b`
(2.2 × 3.2), printed by `repr`. The message said *"**0** of the four printed
options give g = …"* — zero, not "none matched closely enough". No comparison was
ever reached. Demonstrated directly:

```python
>>> parse("jb")(j=2.2, b=3.2)
ParseError: no value given for 'jb'
>>> parse("j*b")(j=2.2, b=3.2)
7.040000000000001
>>> Fraction(11,5) * Fraction(16,5)          # the same product, exactly
Fraction(176, 25)
```

`expr.parse`'s name token is `[A-Za-z][A-Za-z_]*`, so a printed `jb` lexes as one
variable called `jb` and the parse raises before any arithmetic happens. Every
option of every `isolate_factor` draw whose answer is a juxtaposed product
(`g = jb`, `c = cy/55`, `c = sv`) was unreadable, so the audit found zero valid
options and said so. The template's mathematics was right the whole time; the
audit could not read the page.

Two changes, neither of them a tolerance:

1. `audit._split_names` splits a letter run greedily into the longest names the
   caller actually gave values to — `cy` → `c*y`, `V_B` left alone. A run that
   cannot be split is left alone and the parse fails, which correctly counts as
   an option nobody can read.
2. `audit._env` now hands out **dyadic** sample values (2.25, 3.5, 5.125, …), so
   products and differences of them are exact in binary floating point and the
   comparison is not measuring the arithmetic's own residue. The residual
   relative tolerance compares two float evaluations of the same rational, which
   is what any numeric reader must do; it is not hiding a disagreement.

`kit.text_choices` had the **same** blind spot and it was worse there: it calls
`expr.agree` to drop a distractor that is the key in a different jacket, `agree`
swallows `ParseError` internally and returns "not equal", so for every
juxtaposed-product option the duplicate-key check was silently a no-op.
`kit._juxtaposed` now does the same splitting before `agree` is called. This was
found while fixing the audit, not by the gate.

After both changes: `nleq.isolate_factor` and `nleq.scale_relation` generate 60
seeds each with 0 audit failures.

**The halfway guard is not what this needed**, and I want to be plain about it so
nobody adds a fake one: no stem in this topic says *closest*, *nearest* or
*approximately*, and none prints money. Nothing is ever rounded — `kit.dec`
prints a terminating decimal exactly and falls back to a fraction otherwise, and
`kit.gridin` round-trips through `Fraction` and falls back to a fraction rather
than round. `kit.approx_free` exists and is the `percentages.values.unambiguous`
guard, but **it is currently unwired**, which is the one loose end here: either
wire it into `tangent_constant` (the only template that prints a decimal constant
into a stem) or delete it. Do not leave a guard in the file that nothing calls.

## Three open defects

1. **`square_equation` — 5 source items regressed (acceptance).** I widened its
   parameter draw for capacity and changed `spare=0` to `spare=None`. A caller
   that passes `k` but not `spare` (1.8, 1.11, 1.13, 2.21, 3.30) now gets a
   *randomly drawn* `spare`, so `inner = (k − spare)/a` is no longer a perfect
   square and the template rejects. Fix: draw `spare` only when `k` is also None,
   or pass `spare=0` explicitly on those five rows. Capacity is fine either way
   (298 distinct in 300 draws). This is my regression, introduced after the
   run in which acceptance was 84/84.
2. **`scaled_quadratic` audit — "no real solutions".** `shape="divide"` draws
   `k`, `b`, `c` independently, so `k·x² + k·b·x + c = 0` often has none; the
   template computes `−c/k` without ever needing a root, the audit finds a root
   first. Fix the *template* (reject a draw with no real solution — the stem
   implies one exists), not the audit.
3. **`curve_line_system` audit seed 1 — "2 options name a point the graphs
   share".** A genuine two-correct-answers defect of exactly the kind
   `option_check.py` is for: on that draw two of the four printed points both
   satisfy both equations. Look at it before anything else; `_pair_item`'s
   `other`/`curve_only_*` pool entries are the likely source.

## Excluded item

`2.33` (cb `75a32330`) — **the four options are themselves graphs**: four drawn
xy-planes each carrying a parabola and a line, and the question is which picture
the printed system makes. An option that is a picture cannot be generated as an
option string or read back as mathematics. 1 of 85 = 1.2%, well inside the 15%
ceiling.

Two source rows carry `note`s rather than exclusions, and a reviewer should weigh
them: `1.2` (source draws an increasing curve tangent to the line; the template
draws a parabola tangent at the same marked point — the drawn curve family
differs, the mathematics and the option set do not) and `1.21` (the source's
fourth option, `(8, 84)`, lies on neither graph, so it is not reproduced).

## What `option_check.py` must cover

Not started. It is the one deliverable entirely missing. Per template:

| template | property, decided from the printed text |
|---|---|
| `radical_equation`, `rational_linear`, `rational_quadratic`, `rational_combine` | **the extraneous-root check, and the reason this file exists.** Substitute each printed option into the **printed** equation — the radical as a radical, the denominators as denominators — and demand exactly one option satisfies it. A candidate that satisfies the *squared* or *cleared* equation but not the printed one must come out false. The templates already filter their own candidates this way, so this is the independent second opinion, and it must not reuse `_radical_holds` or `f(x)` from `families/solve.py` |
| `curve_line_system` (`which_pair`, `the_pair`, `both_pairs`) | parse each printed point (surds included — the source prints `(1 + √3, √3)`) and substitute into both printed equations; exactly one option satisfies both. **Defect 3 above will fail here** |
| `quadratic_formula` (all three styles) | evaluate each printed option, ± expanded, and check it is a root of the printed quadratic; exactly one option names the root(s) |
| `isolate_sum`/`bracket`/`factor`/`denominator` | give the non-target letters values, read `t` off each printed option, substitute every letter back into the **printed** original equation, demand both sides agree for exactly one option. Needs its own copy of the juxtaposition splitter — a third one, deliberately, per `OPTION-CHECK.md` |
| `scale_relation` | recover each option's coefficients by evaluating at (0,0), (1,0), (0,1); exactly one describes the same half-plane |
| `graph_solution`, `graph_count`, `function_meets` | read the **SVG** back: origin and pixels-per-unit from the `ax`/`gr` lines, the marked point from its `pt` circle, the line from its `sg` segment, the curve from its `cv` polyline. Check the options against the *picture*, not against the parameters that drew it. This is the only check that can catch a figure drifting from its answer |
| `count_real_solutions`, `count_system_solutions`, `symbolic_intersections`, `count`-style items | each label is a claim about a number; decide the number from the printed equation and demand exactly one label is true |
| `factored_equation`, `shared_factor`, `square_equation`, `absolute_equation` | substitute each printed numeric option into the printed equation |

And: assert over **generated draws**, not the source rows; both halves of every
assertion (`hits == 1` *and* `hits[keyed]`); and inject a known-bad option set to
prove the check can fail, recording it in `OPTION-CHECK.md`.

## Next thing I was about to do

Fix defect 1 by drawing `spare` only when `k` is also None, then defects 2 and 3.
