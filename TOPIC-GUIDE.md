# Building a topic

One topic = one self-contained package under `satbank/topics/<slug>/`. Nothing
outside that directory changes, which is what lets several topics be built at
once. Read this whole file before writing code.

## What you are given

```
material/keys/<slug>.json           the official answer key, from the PDF's text layer
material/items/<slug>/<tier>/N.jpg  one image per question, named by item id
```

`1-7.jpg` is item `1.7`. The key file gives, for every item, its id, the
College Board id, its tier (easy / medium / hard) and its official answer: a
letter for multiple choice, the written value for a grid-in. **Read every
question image.** The text layer holds the key table only; the questions are
pictures.

## What you produce

```
material/transcripts/<slug>.json    every question, transcribed
satbank/topics/<slug>/__init__.py   TOPIC = Topic(...)
satbank/topics/<slug>/templates.py  the generators (split into several files if it helps)
satbank/topics/<slug>/audit.py      an independent solver for every template
satbank/topics/<slug>/sources.py    ALL = [...] and EXCLUDED = {...}
```

### The transcript

```json
{"topic": "Circles", "slug": "circles", "items": [
  {"id": "1.1", "cb_id": "23c5fcce", "tier": "easy", "format": "mcq",
   "stem": "A circle has a radius of 7 inches. What is the circumference...",
   "options": ["14π", "49π", "7π", "28π"], "answer_letter": "A",
   "answer_value": "14π", "figure": "circle with a radius drawn and labelled 7",
   "table": null, "notes": ""}]}
```

Transcribe what is printed, in printed order — do not sort the options, do not
fix the source's typos. `format` is `mcq` or `spr` (grid-in). For a grid-in,
`options` is `[]` and `answer_value` is the key file's answer. `figure`
describes the picture in a sentence; `table` holds a table as rows, header
first. The check refuses a transcript whose answer does not match the key
table, so transcribe carefully and let the disagreement tell you which of the
two you misread.

### The templates

A template is a function `(rng, seed, **params) -> Item`. Study
`satbank/topics/area_and_volume/families/measure.py` first: it is the pattern.

* Every number in the stem comes from `rng` or from a caller's keyword, so a
  source item can be rebuilt exactly by passing its own numbers.
* Compute the answer exactly — `Exact` for measures, `Poly` and `Fraction`
  from `satbank/expr.py` for algebra. Never float.
* Record in `params` everything needed to re-derive the answer, under a
  `"kind"` unique to this template across the whole engine.
* Raise `ItemError` to reject a draw whose numbers would make a bad item
  (an answer that cannot be gridded, a degenerate figure, a repeated option).
  Rejecting is free; the registry redraws.
* `assemble(...)` builds and orders the options. Pass `signed=True` when a
  negative answer is legitimate, and `fillers="shift"` when the answer solves
  an equation rather than measures something.
* Every distractor carries the misconception that produces it, in words a
  teacher would use: "used the diameter as the radius", "found x, not 2x".
  Distractors invented to fill space are the difference between a bank and a
  worksheet generator.

### The audit

`audit.py` maps each `kind` to a solver that recomputes the answer **from the
params alone**. Write it from the mathematics, not by calling the generator's
helpers — if it shares a helper with the template, a wrong helper passes
twice. Inverse items: root-find with `solve_for` rather than rearranging.

### The sources

```python
ALL = [
    S("1.1", lambda r: circumference(r, 0, radius=7, unit=IN, fmt="mcq")),
    ...
]
EXCLUDED = {"2.14": "reads a value off a scatterplot printed in the source; the "
                    "item is about the picture, not a rule a template can vary"}
```

No answer is written here. The check drives your template with the source
item's own numbers and compares against the material. Every id in the key file
must appear in `ALL` or in `EXCLUDED` with a reason somebody can review; at
most 15% may be excluded.

## The gate

```bash
PYTHONPATH=. python3 -m satbank check --topic <slug> --quick    # while iterating
PYTHONPATH=. python3 -m satbank check --topic <slug>            # before you report done
```

Seven checks, all of which must pass:

| check | what fails it |
|---|---|
| coverage | an official item neither encoded nor excluded; a thin exclusion reason |
| transcript | a missing stem, or an answer that disagrees with the key table |
| acceptance | the engine does not reproduce an official answer; under 40% of official options recreated |
| audit | a generated item the independent solver disagrees with |
| structure | options not ascending, the key alone in its surface form, under 80% of distractors named |
| prose | a placeholder, a doubled space, a stem that is not a sentence |
| capacity | a template that cannot make 200 distinct items |

## How an item should read on the page

The SAT is typeset, so the engine is too. Write **π, ², ³, √, ≤, ≥, ×, ·, −**
as they are printed — not `pi`, `^2`, `<=`, `sqrt`. Your audit may keep a
plain-ASCII spelling of an expression, which is healthy: it has to be written
from the mathematics rather than from the generator, and the shared
normaliser (`item.norm_text`) knows that `V = πr³` and `V = pi*r^3` are one
answer.

Options carry a unit (`8 cm²`) only when the source item prints one — some do,
most leave the unit in the stem. Pass `fmt_value=` to `assemble` for the ones
that do, and set it per source item rather than guessing for the template.

Look at your items before you report done:

```bash
PYTHONPATH=. python3 tools/preview.py <slug> --per 3 --out /tmp/<slug>.html
```

That renders every template's items with the figure, the table, the key
marked and each distractor's misconception beside it. A page of items is the
only way to see that a stem reads like an SAT stem.

## Rules

1. **Do not edit anything outside `satbank/topics/<slug>/` and your transcript.**
   `exact.py`, `expr.py`, `item.py`, `plot.py`, `figures.py`, `shapes.py`,
   `check.py` are shared. If you need something added to them, say so in your
   report and work around it meanwhile.
2. **Do not commit.** Report when the gate is green; the work is reviewed and
   committed centrally.
3. Template names must be unique engine-wide — prefix them with a family word
   of your own (`circles.arc`, `prob.two_way`), not a bare `forward`.
4. Match the source's voice. SAT stems are plain and short, units are spelled
   out on first use and abbreviated after, and a question ends in a question
   mark. Copy the phrasing patterns you transcribed; do not invent a house
   style.
5. An item must be answerable from the text and figure alone. If a source item
   depends on a picture you cannot regenerate from parameters, exclude it
   rather than ship a template with a fixed picture.
