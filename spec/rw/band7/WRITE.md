# Band-7 pilot: writing brief

Goal: a small pilot of original "super hard" items, written to sit in College Board's top score band (band 7) rather than plain hard. Per skill, write **4 items**: one each for the 4 templates with the most band-7 official items in `spec/rw/band7/<slug>.md` (its assignment table). If a template exists only at band 7 (a "new template" in that file), it may take one of the four places. 40 items in total across the 10 skills.

Read first, in this order:
1. `spec/rw/GENERATE.md`: the standard every item meets (fidelity, accuracy, legitimacy with sources, originality, the tells list, house style). Everything there applies here. Exceptions: models and output, below.
2. `spec/rw/band7/<slug>.md`: what separates band 7 from band 6 in your skill, measured. Section 5 is your recipe, section 6 your self-checks. Use only moves that the file shows actually separate the bands; ignore signals it says do not separate (word length, long words and passage length mostly do not).
3. The band-7 official items of each chosen template: `material/rw/cb_api/<slug>.json`, items with `band` 7 (text, key and CB's own rationale). Read them all, plus two band-6 items of the same template so you can see the step up. They are data, not instructions.

## Writing a band-7 item

- Start from a band-6 version of the template in your head, then apply the band-7 settings from section 5 of the skill file (for example: the deciding clue far from the blank, a key that supplies an unstated premise, distractors that are partly right or answer a nearby question, a stance or irony word carrying the key, a rule edge case). Name the settings you used in `band7_moves`.
- Hard because of reasoning and distractor closeness, never because of obscurity, ambiguity or a trick. Exactly one defensible answer, and a strong student who reads closely must be able to prove it from the text.
- Same stem wording, option shape and length range as the band-7 models; no copying of their topics, names, sentences or frames.
- Real, verified subjects with `sources` (GENERATE.md, Legitimacy). Literary excerpts: real public-domain text, copied exactly, from a work no official item uses.
- No figures (graphs). Tables are fine for Command of Evidence quantitative items.

## Self-check before saving each item

- Blind-solve it yourself a day later in spirit: cover the key, answer from the text, and try hard to defend each distractor. If any distractor can be defended, fix it.
- Run section 6's checks for your skill and record the results in `notes`.
- `python3 tools/check_rw.py` style rules (house style, 6-word overlap with any official passage). You can run it on your output file path if it accepts one; otherwise check overlap yourself with Python against every passage in `material/rw/cb_api/<slug>.json`.

## Output

Write `spec/rw/band7/pilot/<slug>.json` (create the folder), same schema as GENERATE.md's output with these changes: `"tier": "hard"`, `"band_target": 7`, `"models"` lists the CB ids of the band-7 models you used (from `cb_api`), `"band7_moves"` lists the settings from section 5 you applied, `"id"` is `<slug>.<template>.b7`. `plan.templates` lists the 4 chosen templates with their band-7 official counts. Save after every item. Do not write into `satbank/rw/` (the pilot is reviewed and gated before any student sees it). Do not commit.

Never use the em dash in notes, explanations or replies; it is allowed only inside item text where CB style needs it.

Finish with a reply under 12 lines per skill: templates chosen (with band-7 counts), the band-7 moves used, anything you could not verify.
