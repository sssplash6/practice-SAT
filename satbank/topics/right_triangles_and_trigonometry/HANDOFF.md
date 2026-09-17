# Right Triangles and Trigonometry — handoff

Paused on budget, not cancelled. The tree is in a consistent state: nothing is
half-written and the quick gate passes.

```
PYTHONPATH=. python3 -m satbank check --topic right_triangles_and_trigonometry --quick
  ok coverage    33/33 encoded, 0 excluded
  ok transcript  33/33 items
  ok acceptance  33/33 answers, 100% of official distractors recreated, 20/20 option sets complete
  ok audit       749 items re-derived
  ok structure   99% of distractors named
  ok prose       749 items read
  ok capacity    3,639+ distinct items
```

The **full** gate (`--per 300 --draws 1200`) last ran green at 20,506 distinct
items, before the final four cosmetic changes listed under "next" below. Those
changes are all figure-legibility or wording guards; the quick gate has been
green after every one of them, but the full gate has not been re-run since.

## Templates — all 19 written, all 33 official items encoded, 0 excluded

| file | templates |
|---|---|
| `families/sides.py` | `rtt.pythagoras`, `rtt.leg_expression`, `rtt.rectangle_diagonal`, `rtt.special_triangle`, `rtt.special_perimeter`, `rtt.equilateral_logo` |
| `families/ratios.py` | `rtt.trig_ratio`, `rtt.ratio_to_side`, `rtt.cofunction_match`, `rtt.cofunction_angles`, `rtt.complement_tangent`, `rtt.complement_ratio`, `rtt.split_right_angle` |
| `families/similar.py` | `rtt.similar_ratio`, `rtt.similar_side`, `rtt.similar_sides_ratio` |
| `families/composite.py` | `rtt.altitude_special`, `rtt.nested_similar`, `rtt.parallel_similar` |

`sources.py` pins every one of the 33 items to its own numbers and names the
three distractors College Board printed, in printed order, through `kit.pick`
and `wrongs=[...]`. `EXCLUDED` is empty. `audit.py` has an independently
written solver for all 19 `kind`s: float trigonometry and coordinate geometry
against the templates' exact radicals, so the two routes share no arithmetic.

## `option_check.py` — complete, and it has been proved to fail

**It decides every printed option for all nineteen templates.** There is no
template it does not cover. Last full sweep:

```
PYTHONPATH=. python3 satbank/topics/right_triangles_and_trigonometry/option_check.py --draws 2000
  ok  every one of the 19 templates      0 defects
  ok  the 33 official items              0 defects
```

`--sources` runs the same checks over the encoded College Board items, which is
the only thing in the repo that reads two option shapes reachable from no
`generate` call: the unsimplified `3/√3` spelling of item 3.9 and the `√3`
tangent of item 3.6.

**Yes, it has been proved it can fail.** `--selftest` injects ten known-bad
items by hand and confirms each is caught — 10/10:

| injected | what it proves |
|---|---|
| the key a second time as `√1,184` beside `4√74` | the reader compares numbers, not strings |
| the key moved to another letter | `hits[keyed]`, the half the engine already does |
| the key printed without its denominator | zero correct options fails as loudly as two |
| a figure spliced from a draw at other lengths | the picture is read, not trusted |
| the right-angle square drawn on the wrong corner | the mark's vertex is recovered from pixels |
| a marked angle that is not the angle drawn | a label that lies about its own corner |
| a triangle drawn out of proportion to its labels | drawn side lengths against printed ones |
| two options equally close on a "closest" stem | the halfway guard, on the printed page |
| a correspondence the letter order contradicts | similar-triangle correspondence is checked |
| a parallel segment drawn out of parallel | the cut's own geometry |

## SVG read-back — in place

`Figure` in `option_check.py` parses the SVG and recovers, from pixel geometry
alone and with no parameter of the item consulted:

* the three drawn vertices, from the triangle's `path` data;
* **the right-angle mark's vertex**, as `p1 + p3 − p2` of the square's three
  points, matched to a drawn corner and asserted to be a 90° corner (and the
  only one);
* **the drawn side lengths**, with each printed number assigned to the segment
  it sits nearest, and every pair of numerically labelled sides asserted to be
  drawn in the labelled ratio to 1%;
* **the labelled angle**, assigned to its nearest corner and asserted to equal
  the angle actually drawn there to 0.6°;
* the extra segments of the composite figures — an altitude, and a cut
  parallel to a leg — with perpendicularity, parallelism and endpoint
  incidence all checked.

Figures are drawn **exactly to scale** from the item's parameters, which is
what makes the read-back meaningful. Where a source item prints "Note: Figure
not drawn to scale." the note is reproduced, but the drawing is still true.

The figure-carrying checks (`special_triangle`, `nested_similar`,
`parallel_similar`, `altitude_special`, `trig_ratio`) decide their options
**exactly**, from the printed numbers, and use the pixels as a second,
independent assertion that the picture agrees. Deciding options from pixel
measurements was tried first and was too blunt — it reported two draws where
options differed by 0.07% as "two correct answers"; both were false alarms.

## Exact values — no float in any answer path

Confirmed. `Exact`/`E` carries every length, ratio and radical from the draw to
the printed string: a 30-60-90 leg keeps its `√3`, `sin 60°` is
`E(1/2, 0, 3)`, and `4√74` is `Exact.plain()`. `float()` appears only to
*order* options (inside the shared `assemble`), to check a shape is drawable,
and in `audit.py`, which is meant to be a separate numeric route.

One answer shape `Exact` cannot hold is a rational added to a radical —
`58 + 58√2`, item 3.16. `kit.Surd` (`a + b√d` over exact `Fraction`s, with
rationalising division) covers it, stays exact to the page, and is local to
this topic; `exact.py` was not touched. `Item.key` holds the `Surd` and the
shared `audit` compares it through `float()` and `.plain()`, both of which
`Surd` implements.

Rounding happens once, at the last moment, only where a source item prints a
decimal: `kit.places_text`, guarded by `kit.closest_only`, which refuses a draw
whose printed options cannot single the key out. `kit.grid_ok` refuses a
grid-in that is not enterable as digits.

## What I was about to do next

Re-run the full gate and the 2,000-draw `option_check` sweep after the last
four legibility/wording guards, and write `OPTION-CHECK.md` — the only
deliverable not yet on disk.
