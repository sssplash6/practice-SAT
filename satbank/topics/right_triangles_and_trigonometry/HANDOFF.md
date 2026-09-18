# Right Triangles and Trigonometry — state

Complete. 33 of 33 official items encoded, none excluded, nineteen templates,
all seven checks green on the full gate, and `option_check.py` clean over 2,000
draws per template with 10/10 injected faults caught.

```
PYTHONPATH=. python3 -m satbank check --topic right_triangles_and_trigonometry

Right Triangles and Trigonometry  [right_triangles_and_trigonometry]  PASS
    ok   coverage    33/33 encoded, 0 excluded
    ok   transcript  33/33 items
    ok   acceptance  33/33 answers, 100% of official distractors recreated, 20/20 option sets complete
    ok   audit       5,622 items re-derived
    ok   structure   99% of distractors named
    ok   prose       5,622 items read
    ok   capacity    20,235+ distinct items
```

## Deliverables

| file | what |
|---|---|
| `material/transcripts/right_triangles_and_trigonometry.json` | all 33 items transcribed from the images |
| `__init__.py` | `TOPIC`, nineteen templates |
| `families/sides.py` | the theorem, the two special triangles, the logo |
| `families/ratios.py` | sin, cos, tan and the cofunctions |
| `families/similar.py` | similar right triangles and the correspondence |
| `families/composite.py` | an altitude, and a cut parallel to a leg |
| `figures.py` | four generated figures, all drawn exactly to scale |
| `kit.py` | the named-pool `pick`, `Surd`, the assemblers, the halfway guard |
| `audit.py` | nineteen independently written solvers |
| `sources.py` | the 33 items as parameters; `EXCLUDED` is empty |
| `option_check.py` + `OPTION-CHECK.md` | the option and figure checker, and its note |

## Read `OPTION-CHECK.md` first

It carries the three things a reader of this topic needs: how the SVG is read
back, what `kit.Surd` is and why it exists, and the defects the checker found.
The short version:

* **The figures are drawn exactly to scale from the item's parameters.** That is
  load-bearing, not cosmetic — it is what lets `option_check.py` recover the
  drawn vertices, the drawn side lengths, the labelled angle and the right-angle
  mark's vertex from pixel geometry and assert them against the printed numbers.
  Where a source item prints "Note: Figure not drawn to scale." the note is
  reproduced; the drawing underneath it is still true.
* **`kit.Surd` is the only thing this topic adds outside the shared core.**
  `Exact` is `coef · π^e · √rad` and cannot hold a rational *added* to a radical,
  which is the shape of item 3.16's answer, `58 + 58√2`. `Surd` is `a + b√d` over
  exact `Fraction`s with rationalising division. It implements `float()` and
  `.plain()`, which is the whole of the contract `satbank/audit.py` has with
  `item.key`, so the shared audit runs over it with no special case. It is a
  candidate for promotion into `exact.py`; the five requirements are listed in
  `OPTION-CHECK.md` so the next person has them stated rather than buried.
* **Nothing floats.** Every length and ratio is exact to the printed page. The
  one deliberate rounding is for the source items that print a decimal, and it
  rounds an `Exact` to an `Exact` rational before printing.

## Anything wanted from the shared core

Nothing was needed and nothing was worked around. Two things are worth knowing:

* `item.numeral` cannot read an unsimplified radical quotient such as `3/√3`, so
  the shared `audit` would reject an item printing one as its key. Item 3.9
  prints exactly that, and `rtt.complement_tangent` therefore uses the flipped
  spelling only when a source item asks for it by name; a free draw takes a
  rational tangent. `option_check.py --sources` is the only thing that reads
  that option set as mathematics. Same situation `circles` records for
  `render.pi_front`.
* `item.assemble` requires the key not to be the only option of its surface
  form. College Board's own set for item 3.6 is `250` among three radicals, so
  `kit.assemble_exact` applies the rule to free draws and not to a source item
  that has named its own three.
