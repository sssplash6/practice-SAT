# Reading the page back

`satbank check` asks whether the key is right. It never asks whether a
*distractor* is also right, because nothing in the engine reads the wrong
options as mathematics. In this topic there is a second hole of the same shape
and it is wider: nothing in the engine reads the **figure** either. A triangle
drawn with the 40° angle at the wrong vertex is a wrong question that coverage,
transcript, acceptance, audit, structure, prose and capacity all call right,
because every one of them re-derives from the parameters and never once looks
at the picture the student is actually given.

`option_check.py` closes both. It parses the printed stem, the printed options
and the SVG's own pixel geometry, and it imports no template, no figure builder
and no solver — `generate` is used only to obtain the finished item, exactly as
a student would receive it.

```
PYTHONPATH=. python3 satbank/topics/lines_angles_and_triangles/option_check.py --selftest
PYTHONPATH=. python3 satbank/topics/lines_angles_and_triangles/option_check.py --draws 1000
PYTHONPATH=. python3 .../option_check.py --draws 1500 --template lat.transversal
```

## What the reader gets out of a figure

`figures.py` emits four shapes and nothing else, so the reader keys off those
and reconstructs the rest.

**Vertices.** Every segment endpoint, plus every proper crossing of two drawn
segments (both parameters strictly inside), merged within 1.5px. Crossings
matter: `C` in item 1.6 and `W` in 3.2 are named points that exist only as
intersections, and without them those items cannot be read at all.

**Angles.** An arc is `M x₁,y₁ A r,r 0 0 0 x₂,y₂` and its vertex is not in the
markup. It is recovered as `midpoint ± √(r² − d²/4)·n̂`, one of two candidates,
resolved by which lands within 3px of a drawn vertex.

The angle is then **not** measured from the arc. An arc is twenty pixels across
with ends rounded to a tenth of a pixel, which leaves half a degree of slop —
enough to lose an item whose options are a degree apart, and that is exactly
what happened on the first run. So the arc says only *which two rays* are
marked, each end is snapped to the drawn line it points along, and the angle is
measured between those lines, which run for hundreds of pixels and read to a
twentieth of a degree. An arc end that snaps to no drawn line is itself a
defect and is reported.

**Right angles.** A square `M p₁ L p₂ L p₃` has vertex `p₁ + p₃ − p₂`; the
reader asserts the angle really is 90°.

**Points.** A one- or two-character text is bound to the nearest vertex within
46px. That is what lets the reader answer "the measure of angle QPR" by
measuring where the drawing actually puts Q, P and R.

**Which number names which angle.** A label belongs to the arc whose wedge it
falls inside and whose vertex it is nearest — the way a person reads it — with
a global nearest-first assignment. If the runner-up is within 1.3× of the
winner, nobody can tell which angle the number names, and the figure is
reported rather than guessed at. `figures.py` now refuses to draw such a figure
in the first place, using the same test.

## What it asserts

`audit_figure` runs on every item that has a figure and is where a figure that
drifted from its answer dies. Four assertions:

1. a number printed beside an arc is that arc's own drawn span;
2. two arcs marked with the same letter are drawn the same size;
3. a letter the **stem** assigns a value to (`y = 20`) is drawn at that value —
   the cross-check between prose and picture;
4. the letter the question asks for is drawn at the item's own answer, with
   `2b°` handled as twice it.

On top of that, each template decides its four options from the printed page:

| how the answer is recovered | templates |
|---|---|
| measure the arc marked with the stem's own letter | `isosceles`, `isosceles_cross`, `crossing_triangles`, `parallel_triangle`, `perp_transversal`, `three_lines_point`, `three_lines_triangle`, `angle_algebra`, `exterior_angle` (extended), `triangle_sum` (right_figure) |
| measure between three **named** points, because the asked angle is not marked | `vertical_isosceles`, `midsegment_angle`, `big_chain`, `exterior_angle` (extend_base) |
| read the relation (equal / supplementary) off the two drawn marks | `transversal`, `transversal_proof`, `transversal_inequality` |
| divide every printed length by its drawn pixel length and require one scale | `ratio_match`, `vertical_similar`, `altitude_legs`, `geometric_mean`, `parallel_segments` |
| evaluate each option from the printed text alone | `eight_angles`, `similar_needed`, `similar_sufficient`, `isosceles_possible`, `shadow`, `similar_angle`, `similar_side`, `parallel_cut_area`, `area_range`, `triangle_sum` (the other frames) |

Every route ends at `settle`: exactly one option is correct, and it is the one
the key points at.

Three things this file tries to get right, copied from
`systems_of_linear_equations/option_check.py`:

* **read the printed string, not the parameters** — a rendering bug that drops
  a minus sign is invisible to any check that goes back through the renderer;
* **check generated draws, not the source items** — seven of the nine defects
  below live in draws no official item uses;
* **prove the check can fail** — see below.

## Proving it can fail

`--selftest` injects eight known-bad items and requires all eight to be caught.
The cases, and the mechanism that catches each:

| injected defect | caught by |
|---|---|
| a second option equal to the key | `settle`: 2 of 4 correct |
| the key letter moved | the option the drawing picks is not the keyed one |
| a real arc, at the right vertex, drawn 17° wide of its label | the arc no longer opens along two drawn lines |
| two angle labels swapped in the figure | the stem says `x = 99` but the figure draws `x°` as 48° |
| a figure lifted from another draw of the same template | same, via the stem's assignment |
| a printed length the drawing does not use | the four lengths give four different scales |
| a fourth *possible* measure where one must be impossible | 2 of 4 correct |
| a key that is in fact one of the five reachable sums | 0 of 4 correct |

The third case is the one to watch. It was first written as a malformed arc and
was caught for the wrong reason — because it no longer parsed. It was rewritten
to produce a perfectly valid arc, centred on a real vertex, at a size its label
does not say. That is the defect this whole file exists for, so the injection
has to be exactly that and nothing weaker.

## What it found

Nine live defects, over 30,749 generated items and all 48 official ones. Seven
of the nine are in the figures, which is the half of this topic nothing else
looks at.

| # | template | defect |
|---|---|---|
| 1 | `perp_transversal` | both `a°` arcs opened along the **other** transversal, so each was drawn at 141° under a label reading 39°. The figure had been eyeballed and passed. |
| 2 | `perp_transversal` | both transversals were drawn too short to reach line *n*, so the given 130° **and the answer's own `b°`** were marked at points where their own line was not present |
| 3 | `big_chain` | X and U drawn 34px apart with W between them; the drawn ∠TUR was 94° where the answer said 110° |
| 4 | `geometric_mean` | AD:DC ran as far as 196:1, putting the foot of the altitude 3.5px from a vertex — unreadable at any scale, and the reading 0.8% out |
| 5 | `similar_sufficient` | **two correct options** whenever the second angle happened to equal the shared one: "angles M and S are m° and a°" then also forces the triangles equiangular |
| 6 | `vertical_isosceles` | with one pair of arms many times the other, the two angle labels print 13px apart and which names which is not decidable |
| 7 | `crossing_triangles` | a shallow triangle drops the apex's `x°` label onto segment AD, where it reads as naming an angle at A |
| 8 | `parallel_triangle` | the apex's `x°` and the `z°` at the ℓ crossing converge to ~14px apart |
| 9 | `perp_transversal`, `transversal` | a line could be named `b` while the stem asked "What is the value of b?" |

Fixes went into the templates and the figure builder, never into the check.
Four of them are now guards in `figures.py` and the families — a label must be
plainly nearer its own vertex than any other number is; a transversal must be
drawn past the line it is marked against; two named points may not be drawn on
top of each other; the two pieces of a hypotenuse may not differ by more than
twenty times.

Two further findings were bugs in the reader rather than the items, and both
were worth the trouble:

* it read the **first** angle named in the stem rather than the one the
  question asks for, so "The measure of ∠JKL is 97° … What is the measure of
  ∠KJL?" measured the given. Everything asked for is now read out of the final
  sentence alone.
* it measured off the 21px arc instead of the drawn lines, which cost half a
  degree and lost a 168° answer to rounding.

## Honesty note on the distractors

Distractor fidelity is **90%** (89 of College Board's 99 printed distractors,
28 of 33 option sets complete). The ten that are not reproduced are named, item
by item, in `sources.py`:

* **1.1** — 36, 58 and 70 scatter around a key of 46 and answer to no route
  through an isosceles triangle with a 67° base angle. 0 of 3.
* **2.1** — 16.8 and 18.4 sit a tenth either side of 17.472 and answer to no
  proportion the figure admits. 19.6 is matched.
* **2.2** — 27 is not 10(5)/2 = 25, where inverting the proportion lands, nor
  any other arrangement of 10, 5 and 2.
* **3.5** — 2.2 and 2.3 are single tenths either side of 2.4. 2.5, the median
  from the right angle, is matched.
* **3.6** — 72 and 58 straddle 64 by eight and six degrees. 66, the supplement
  of the apex angle, is matched.

Two distractors were recovered honestly during this pass, by adding
misconceptions the pools genuinely lacked rather than by fitting to the digits:
"gave a right angle, which the figure only looks like" (`crossing_triangles`,
which the topic already used in `parallel_triangle`) and "stopped at the
supplement of the apex angle" (`isosceles_cross`). That moved 88% to 90%. The
remaining ten look like near-misses the item writer placed around the key, and
inventing a route to them would only hollow the number out.
