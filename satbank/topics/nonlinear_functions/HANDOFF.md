# Nonlinear Functions — handoff

Paused on budget, not cancelled. **The gate is green and `option_check.py` is
written and clean.** The three acceptance failures named in the pause message
were diagnosed and fixed before the pause; they are recorded below as history,
not as open work.

```
Nonlinear Functions  [nonlinear_functions]  PASS
    ok   coverage    105/110 encoded, 5 excluded
    ok   transcript  110/110 items
    ok   acceptance  105/105 answers, 96% of official distractors recreated, 76/84 option sets complete
    ok   audit       10,800 items re-derived
    ok   structure   99% of distractors named
    ok   prose       10,800 items read
    ok   capacity    33,559+ distinct items
```

## What is done

* `material/transcripts/nonlinear_functions.json` — all 110 items transcribed
  from the images (every image read; the key table was used only to check).
* `satbank/topics/nonlinear_functions/` — `__init__.py`, `common.py`,
  `figures.py`, `audit.py`, `sources.py`, `option_check.py`, and seven family
  modules under `families/`.
* 36 templates, all live, none stubbed. Every one passes audit, structure,
  prose and capacity at full volume (1,200 draws each).

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

## What is NOT done

1. **`OPTION-CHECK.md` is not written.** `option_check.py` is finished, green
   at 400 draws per template (11,904 items read back) and its `--selftest`
   catches all six injected faults, but the prose note that explains it has
   not been written yet. That is the one deliverable missing.
2. **Nobody has looked at a page of items.** `tools/preview.py
   nonlinear_functions --per 3` has not been run. Every prose defect in waves
   1 and 2 was found by eye; this topic has not had that pass.

## The three acceptance failures — diagnosed and fixed

All three were real and all three are closed.

* **2.19** — the engine printed *"the number of brachiopods species"* where
  College Board prints *"brachiopod species"*. Cause: one `thing` string was
  used both in the stem (plural, "species of brachiopods") and inside the
  option sentences (singular, "brachiopod species"). Fixed by storing the
  singular and appending `"s"` at the one place the stem needs the plural
  (`families/interpret.py`, `interpret_rate`), and by changing the source row
  to `thing="brachiopod"`.
* **3.9 and 3.14** — both raised `ItemError("the key would be the only option
  of its surface form")`. Cause: `common.choose`/`common.text_item` applied a
  *stricter* guard than the gate's own `check._shape`, and applied it to
  source items as well as to free draws. Two separate bugs:
  - the local guard tested `startswith(("-", MINUS))` while the gate tests
    only the ASCII hyphen, so `−1 < r < 0` looked unique when the gate would
    have seen it as identical to `r < −1` (3.9);
  - College Board's own option set for 3.14 genuinely leaves the key as the
    only option containing a slash (`1,800(1.02)^(q/4)` against three options
    with no slash). The gate never runs `structure` on source items, so this
    is legal; the engine was refusing to build an item the gate would accept.

  Fixed by aligning `_surface` with `check._shape` exactly, and by making
  `common.pick` return a `Named` list that records whether a source item chose
  the wrong answers. When it did, College Board's set is the authority and the
  surface guard is skipped; free draws are still guarded.

## The five excluded items (4.5% of 110; ceiling is 15%)

All five have **options that are pictures or tables**, so no printed option
text can carry the answer. They are the only five such items in the topic.

| id | why |
|---|---|
| 1.2 | the four options are two-column tables of readings taken off a drawn parabola; the item matches a picture to a table |
| 1.4 | the four options are coordinate grids showing four cubic curves |
| 1.11 | the four options are coordinate grids showing four parabolas that differ only in where the vertex sits |
| 1.21 | the four options are two-row tables of `x` and `h(x)` |
| 2.9 | the four options are graphs of exponential curves differing in direction and steepness |

Rendering a table option as a line of text (`"x: 1, 2, 3; h(x): −2, 1, 6"`)
was considered and rejected: it is not what the source prints, and the
acceptance check would then be comparing the engine against a format the
engine invented. If a reviewer wants these four back, the honest route is a
table-valued option type in the core, not a text rendering.

## What `option_check.py` covers, per template

Written and passing. Every option is decided from its **printed text** (or
from the SVG's own pixel geometry); nothing consults `item.params`. The only
engine imports are `registry.generate`, `expr.parse` and `expr.agree`.

| template | what makes an option decidable |
|---|---|
| `evaluate`, `exp_evaluate` | the rule is parsed out of the stem and evaluated at the printed input; all four printed numbers must also be distinct |
| `solve_value` | the option is substituted back into the printed equation (`7n³ = 56`, `½mv² = E`) |
| `param_value` | the hidden `c` is recovered from the printed `p(c) = v`, then the value at the printed input |
| `y_intercept` | the printed rule at x = 0, matched against each printed point; the identity mode demands exactly one option of the form `f(0)` |
| `x_intercept` | each printed point is substituted into the printed rule; the NOT variant demands exactly one option that is *not* a zero |
| `graph_intercept` | the y-intercept is read off the **drawn** polyline at the drawn vertical axis, and no option may sit within a gridline of the key |
| `graph_context` | the drawn start value or the drawn peak, with the same gridline separation rule |
| `graph_zeros` | sign changes counted along the drawn polyline |
| `graph_equation` | each printed equation is evaluated at 25 points sampled off the drawn curve, to a fiftieth of a gridline |
| `exp_model`, `exp_period`, `exp_anchor`, `exp_reach`, `exp_offset` | the intended model is rebuilt from the words (start, percent, period, ambient) and each printed equation is evaluated at 0, 1 and 2 periods — so the same model written a different way is caught |
| `exp_from_table` | each printed equation must reproduce every printed row |
| `exp_rate` | the growth factor from the printed percent; the yearly percent from the printed period form; the r-range mode tests six sample values of r against each printed interval |
| `exp_two_points` | `a` and `b` are recovered from the two printed points |
| `exp_display` | each Roman-numeral equation is evaluated at x = 0 and compared with the number literals it prints — "displays as a constant" made concrete |
| `exp_rewrite` | the y-intercept must appear among the option's own literals; the coefficient mode asserts all four forms are equivalent and then finds the one whose printed coefficient of x is 1/c |
| `exp_steps` | doublings counted from the printed ratio, including scientific notation in the table |
| `vertex_value` | the vertex is found by numerical search on the parsed rule, never by algebra the generator shares |
| `vertex_symmetry`, `shift_max`, `quad_fit`, `quad_must_be_true` | rebuilt from the printed vertex, zeros, or the pair of equal values |
| `interpret_value`, `interpret_initial`, `interpret_rate`, `quad_feature` | each sentence is matched against the shape its family prints, and the numbers it names are checked against numbers the item itself prints |
| `quad_word`, `build_expression`, `factor_from_table` | the situation's equation is rebuilt from the stem; expressions are compared with `expr.agree`; a factor is a hit only if every one of its zeros is a zero the table shows |
| `abs_value`, `exp_power_table`, `zeros_constant` | grid-in only — reported as having no options to read rather than passed silently |

`--selftest` injects six faults and catches all six: a model rewritten with a
fractional base, an exponential with the root taken into the base, the key
under the wrong letter, a figure spliced in from another item, a distractor
moved to six tenths of a gridline from the key, and a sentence repeated under
another noun.

### Four live defects it found, all now fixed

1. `exp_anchor` printed its growth factor to one decimal place, so a 275%
   rise printed as `24(3.8)^t` when the words demand 3.75 — the printed option
   could not be produced from the printed stem. Now printed exactly.
2. `exp_rate`'s rising variant keyed `0 < r < 1` for a model that rises by a
   fixed percent, which only forces `r > 0`; `r = 2` satisfies the stem and
   not the key. The rising variant is no longer drawn.
3. `factor_from_table` offered a single factor of one of the table's own zeros
   as a distractor — it is genuinely forced, so the item had two correct
   answers. Replaced with a repeated factor, which is not forced.
4. `factor_from_table` also allowed a mirror pair of zeros (−2 and 2), which
   made the sign-flipped distractor the same polynomial as the key. Now
   rejected at draw time.

## What I was about to do next

Write `OPTION-CHECK.md` from the material above, then run
`tools/preview.py nonlinear_functions --per 3` and read a page of items by eye.
