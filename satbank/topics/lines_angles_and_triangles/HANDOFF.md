# Lines, Angles, and Triangles — handoff

Paused mid-wave. The seven-check gate is **green on the full run**:

```
Lines, Angles, and Triangles  [lines_angles_and_triangles]  PASS
    ok   coverage    48/48 encoded, 0 excluded
    ok   transcript  48/48 items
    ok   acceptance  48/48 answers, 88% of official distractors recreated, 27/33 option sets complete
    ok   audit       9,237 items re-derived
    ok   structure   98% of distractors named
    ok   prose       9,237 items read
    ok   capacity    30,242+ distinct items
```

Distractor fidelity **88%**, 48/48 encoded, **0 excluded**.

## What is done

31 templates, all prefixed `lat.`, in three family files.

`families/triangles.py` — `triangle_sum` (5 stem frames, 6 source items),
`isosceles` (base / exterior), `isosceles_possible`, `angle_algebra`,
`exterior_angle` (extended / extend_base), `isosceles_cross` (covers 3.1, 3.6,
3.12 — the same configuration run forwards and backwards), `vertical_isosceles`,
`crossing_triangles`.

`families/parallels.py` — `transversal` (spot-based: a marked angle is
`(line, above/below, left/right)`), `transversal_proof`, `transversal_inequality`,
`eight_angles`, `parallel_triangle`, `midsegment_angle`, `perp_transversal`,
`two_transversals`, `three_lines_point`, `three_lines_triangle`, `big_chain`.

`families/similar.py` — `similar_angle` (dilate / ratio / expr / quad),
`similar_side`, `shadow`, `parallel_segments`, `ratio_match`, `similar_needed`,
`similar_sufficient`, `vertical_similar`, `altitude_legs`, `geometric_mean`,
`parallel_cut_area`, `area_range`.

Plus `figures.py` (the `Fig` builder), `kit.py` (named pool `pick`, `unambiguous`
halfway guard, `deg`/`plain`/`dec`), `audit.py`, `sources.py`, and the transcript
at `material/transcripts/lines_angles_and_triangles.json`.

### Figures: none hard-coded

Every figure is built by solving the item's own geometry in Cartesian
coordinates and handing the points to `Fig`, which scales them into the SVG.
There is no fixed picture anywhere in the topic and no figure that survives a
parameter change. **All figures are drawn to scale** — a 46° apex is 46° of arc
on the page — with exactly one exception: `transversal` clamps its slope into
[24°, 156°] when the printed angle is outside that band (only source item 1.17,
170°, hits this) and then emits the source set's own "Note: Figure not drawn to
scale." caption. `Fig` raises `ItemError` on a degenerate draw (angles that do
not close, a point that would miss the segment it must lie on, a figure flatter
than 1:22, an arc span under 6°), so the registry redraws rather than shipping a
bad picture.

I rendered 34 source-item figures to PNG and looked at every one. Defects found
and fixed by eye: overlapping `x°`/`z°` labels in 1.2, an `x°` label landing on
segment `AD` in 1.6, `r` and `t` line labels printed on top of each other in 3.3,
and narrow-wedge labels (13°, 20°, 23°, 31°) written across the lines that make
the angle.

## option_check.py — written, NOT YET RUN

`option_check.py` exists and is syntactically complete, but **it has never been
executed**. Treat it as a draft. Run it first:

```
PYTHONPATH=. python3 satbank/topics/lines_angles_and_triangles/option_check.py --selftest
PYTHONPATH=. python3 satbank/topics/lines_angles_and_triangles/option_check.py
```

Expect to fix parsing bugs in the SVG reader before it is trustworthy. What it
is meant to do, and what still needs verifying:

### Recovering geometry from the SVG's pixels

`Drawn` parses only the emitted markup — it imports no template and no figure
code. `figures.py` emits exactly four shapes, and the reader keys off them:

* `<line class="fg" x1 y1 x2 y2/>` → the drawn segments.
* `<path class="ar" d="Mx1,y1 Ar,r 0 0 0 x2,y2"/>` → an angle arc. The arc's
  **vertex is not in the markup** and must be recovered: the two candidate
  centres are `midpoint ± sqrt(r² − d²/4)·n`, and the right one is whichever
  lands within 3px of a drawn vertex. The angle is then the turn between the two
  endpoint directions from that centre.
* `<path class="ar" d="Mx1,y1 Lx2,y2 Lx3,y3"/>` → a right-angle square; its
  vertex is `p1 + p3 − p2` and the reader asserts the marked angle really is 90°.
* `<text class="it|lb" x y ...>BODY</text>` → labels. A body ending in `°` is an
  angle name; a one- or two-character body is a **point name**, bound to the
  nearest drawn vertex within 46px.

Vertices are every segment endpoint **plus every proper crossing of two drawn
segments** (`_cross`, with the parameters strictly inside both segments), merged
within 1.5px. That is what lets `C` in item 1.6 or `W` in 3.2 be found at all —
they are crossings, not endpoints.

Angle labels are bound to arcs by bisector direction (within 34°) and radius
band, one-to-one; `Fig` now varies the label distance for narrow wedges, so the
binding must be by **direction**, not by an exact distance.

### What must be asserted, per template

`audit_figure` is the universal part and is where "the 40° angle at the wrong
vertex" dies. For every item with a figure it asserts:

1. a number printed beside an arc equals that arc's own drawn span (±1.4°);
2. two arcs marked with the same letter are drawn the same size;
3. a letter the **stem** assigns a value to (`y = 20`) is drawn at that value —
   this is the cross-check between prose and picture;
4. the letter the question asks for is drawn at the item's own answer, with
   `2b°` handled as twice it.

On top of that each template decides its four options from the printed page:

* `isosceles`, `isosceles_cross`, `crossing_triangles`, `parallel_triangle`,
  `perp_transversal`, `three_lines_point`, `three_lines_triangle`,
  `exterior_angle`(extended), `triangle_sum`(right_figure) — measure the arc
  marked with the stem's own letter and require exactly one option to equal it.
* `vertical_isosceles`, `midsegment_angle`, `big_chain`, `exterior_angle`
  (extend_base) — the asked angle is **not** marked, so it is measured at the
  three named points the drawing actually places (`Drawn.angle_named("QPR")`).
* `transversal` — measures both marked angles and reads the relation off the
  drawing (equal or supplementary), so it still works on the one not-to-scale
  figure.
* `ratio_match`, `vertical_similar`, `altitude_legs`, `geometric_mean`,
  `parallel_segments` — **segment lengths**: every printed length is divided by
  its drawn pixel length and the resulting scale factors must agree to 2%, then
  the asked length is read off the drawing and divided by that scale.
* `transversal_proof`, `transversal_inequality`, `eight_angles`,
  `similar_needed`, `similar_sufficient`, `isosceles_possible`, `shadow`,
  `similar_angle`, `similar_side`, `parallel_cut_area`, `area_range` — decided
  from the printed text alone (each option evaluated, exactly one true).

`_leg_scale` in `check_altitude_legs` is half-written (it has a dead loop and a
`del best`); rewrite it before trusting that template. `check_vertical_similar`
has an unused `lengths` dict for the same reason.

### Proving the check can fail

`CASES` injects eight known-bad items — a duplicated key, the key letter moved,
an arc bent 28° away from its label, two angle labels swapped in the figure, a
figure lifted from a different draw, a printed length the drawing does not use,
a fourth possible measure where one must be impossible, and a key that is in
fact one of the five reachable sums. `--selftest` must catch all eight. If any
slips through, that check is not doing its job.

## Where figure/answer agreement is least certain

* **`lat.transversal`** — the only place a figure is not to scale. The spot
  relation survives the clamp, but nothing has verified that across the whole
  `given ∈ [15,165]` range; `check_transversal` is written to tolerate it.
* **`lat.big_chain` (3.2)** and **`lat.isosceles_cross` at small base angles
  (3.12 draws a 12° base)** — both produce figures with aspect ratios near 5:1
  and points that must land in order along a line. The builders raise
  `ItemError` when the order breaks, but the rejection rate across the draw
  range has not been measured.
* **`lat.two_transversals` (3.9)** — the bisecting ray at the lower crossing is
  drawn but never named in the stem; the item is only answerable because the two
  angles are both marked `w°`. `check_two_transversals` asserts they are drawn
  equal, which is the thing to keep.
* **`lat.altitude_legs` / `lat.geometric_mean`** — very flat triangles (3.14 is
  43 wide by 11 tall). Drawn exactly, but the pixel-length checks will be the
  most sensitive to rounding here.

## Next line of work

Run `option_check.py --selftest`, fix the SVG-reader parsing bugs it turns up,
then rewrite `_leg_scale` properly and run the full pass.
