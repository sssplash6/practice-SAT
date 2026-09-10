# satbank

An SAT Math item generator. Each question **type** is a template — a parameter
space, a solver, a set of distractors derived from real student misconceptions,
and a verifier — so one template yields unlimited items whose answers are
computed, never guessed.

No model runs at generation time. An LLM's job here is offline: turning a source
question into a template. Generation itself is deterministic code, so an item is
reproducible from its seed and provably correct before it ships.

## Status

One domain is complete: **Geometry and Trigonometry → Area and Volume**, built
from 59 official items across three difficulty tiers.

| | |
|---|---|
| Templates | 19 |
| Official answers reproduced | 59 / 59 |
| Distinct items generated and independently audited | **116,763, 0 disagreements** |
| Option sets matching College Board exactly | 13 / 45 multiple-choice items |
| Individual official distractors recreated | 70% |
| Structural validation (options, ordering, prose) | 7,600 items, 0 failures |
| Distractors traced to a named misconception | 99% |
| Throughput, with the audit on | ~10,000 items/second |

## Run it

```bash
PYTHONPATH=. python3 -m satbank templates            # list the 19 templates
PYTHONPATH=. python3 -m satbank generate --n 5       # print items with answer rationales
PYTHONPATH=. python3 -m satbank generate --template measure.inverse --n 3
PYTHONPATH=. python3 -m satbank export --n 500 --out pool.json

PYTHONPATH=. python3 tests/test_sources.py           # the 59 official items
PYTHONPATH=. python3 tests/test_math.py 2000         # re-derive answers independently
PYTHONPATH=. python3 tests/test_fuzz.py              # structural validation at volume
```

## How it is put together

```
satbank/exact.py       coef * pi^e * sqrt(rad) arithmetic -- every answer form in the
                       source set: 192pi, 135/8, 36sqrt13, 2sqrt(pi), 19652pi/375
satbank/shapes.py      13 shapes, 21 symbolic formulas, SAT phrasing conventions
satbank/verify.py      the same 21 formulas written again, numerically and
                       independently; a key ships only when both routes agree
satbank/item.py        choice assembly: misconception-driven, ascending order, and
                       the key is never the only option of its surface form
satbank/figures.py     generated SVG -- coordinate grids, solids, similar rectangles
satbank/families/      the 19 templates, grouped into 6 families
satbank/sources.py     the 59 official items encoded as template parameters
satbank/audit.py       an independent solver for all 19 templates; every item is
                       re-derived here before release
satbank/registry.py    every template by name, with retry on rejected parameters
```

### The families

The 59 source items are not 59 templates. They collapse to six families crossed
with the axes the source actually varies — which quantity is given (radius /
diameter / base circumference / base area), how the sentence is framed, whether
units are spelled out or abbreviated, and multiple-choice versus grid-in.

1. **Measurement** — dimensions to a measure, or a measure back to a dimension
2. **Similarity and scaling** — lengths by *k*, areas by *k²*, volumes by *k³*
3. **Coordinate geometry** — the figure is generated from the same parameters
4. **Expression form** — the options are expressions, not values
5. **Context** — partial fills, combined figures, percent resizing
6. **Supplied formula** — substitute into a formula given in the item

### Why every answer is computed twice

No item leaves `generate()` until a second, independently written solver has
re-derived its answer and agreed. Two layers do this:

- `verify.py` re-implements all 21 geometry formulas numerically, written from
  the geometry rather than from `shapes.py`. The measurement family checks
  against it as it builds.
- `audit.py` re-derives the answer of **every** template from the item's own
  `params`, in plain floats, sharing no reasoning with the generators. Inverse
  items are checked by numerically root-finding the unknown rather than by any
  algebra the generator performs.

A wrong answer therefore has to be produced twice, identically, by two
separately written pieces of code, to escape. The check costs about 7% of
throughput and is on by default; `generate(..., verify=False)` exists only to
measure that cost.

That double-entry approach found an error in the source material: item 2.8
(`37dde49f`) is keyed **C (7.79)**, but its own formula `V = 7πk³/48` with
`V = 473` gives **10.11**, option D. 7.79 is the cube root of 473 — the answer
you get by dropping the coefficient, i.e. the intended distractor.

## Known limits

Nine of the nineteen templates have a bounded parameter space, four of them
badly: `coord.square_diagonals` tops out at **24** distinct items,
`circle.equal_area_square` at 57, `expression.symbolic_volume` at 120,
`context.container_percent` at 240. Those constructions are rigid and need
loosening before a student can drill them heavily.

The other ten had not saturated at 20,000 draws each. `measure.forward` alone
has ~1.78 million parameterisations by direct count.

Sampling also collides: 30,000 random draws yielded 17,229 distinct items (57%
unique). Serving students needs enumeration by seed plus per-student history,
not random draws.

## Adding a domain

Add shapes or formulas to `shapes.py` **and** `verify.py`; write the template in
`families/`, having it record the numbers that determine its answer in `P`; add
an independent solver for it to `audit.py`; register it; encode the source items
you learned it from in `sources.py`. The acceptance test then holds that template to the official
answers permanently — it has already caught one regression that a wider
parameter space introduced.
