# Can a model's blind solve tell band 7 from band 6?

Run 2026-10-16. Haiku blind-solved 885 official CB items (all 585 hard items without a graph, plus 150 each from bands 4 and 5), with keys and bands hidden, giving an answer and a probability for each option. "Doubt" is 1 minus the probability it put on the key. AUC is the chance a band-7 item draws more doubt than a band-6 one (0.5 = no signal).

| Band | Items | Haiku right | Mean p(key) |
|---|---|---|---|
| 4 | 150 | 97% | 0.84 |
| 5 | 150 | 99% | 0.83 |
| 6 | 294 | 96% | 0.80 |
| 7 | 291 | 87% | 0.71 |

Doubt AUC, band 7 vs 6: **0.62** overall (hard vs medium: 0.64).

| Skill | Right, band 6 | Right, band 7 | AUC 7 vs 6 |
|---|---|---|---|
| Boundaries | 81% | 52% | 0.68 |
| Central Ideas and Details | 100% | 91% | 0.67 |
| Inferences | 100% | 94% | 0.67 |
| Command of Evidence | 98% | 100% | 0.65 |
| Cross-Text Connections (small) | 100% | 100% | 0.82 |
| Rhetorical Synthesis | 100% | 90% | 0.61 |
| Form, Structure, and Sense | 93% | 91% | 0.58 |
| Transitions | 92% | 81% | 0.58 |
| Text Structure and Purpose | 100% | 100% | 0.58 |
| Words in Context | 100% | 100% | 0.50 |

## What this means for the gate

- **Not an item-level gate.** 0.62 is a real but weak signal: a single item's doubt cannot say band 6 or 7. Haiku also may have seen these public items, which would hide some difficulty.
- **A batch-level check.** A set of band-7 drafts in a skill should draw about the band-7 doubt of that skill's officials (overall mean p(key) near 0.71, not 0.80). A batch that looks like band 5 has missed.
- **Useful per skill where AUC is 0.65 or more** (Boundaries, Central Ideas, Inferences, Command of Evidence); no use for Words in Context, where the option-rarity measure in `words_in_context.md` is the check instead.
- **Low accuracy is also what a broken item looks like.** Run the solve only after review (`spec/rw/VERIFY.md`); a confident miss on a reviewed item still goes back to the reviewer before it counts as "hard".

Scripts used (scratchpad, rebuildable): batches from `material/rw/cb_api` with an opaque qid and the key kept apart; scoring by band and skill.

## Gate rule used for the band-7 pilot (2026-10-16)

Per skill: the reviewed pilot items are blind-solved by Haiku mixed with 6 band-6 and 6 band-7 official anchors of the same skill (same instructions as above, keys apart). Compare the pilot's mean p(key) with the anchors':
- anchors separate (band 7 at least 0.05 below band 6): pass when the pilot sits closer to band 7 than to band 6;
- anchors do not separate (the proxy is blind for that skill in this sample): pass when the pilot is at least as hard as the harder anchor group plus 0.02, else harden; the reviewer's band-7 verdict decides the rest.
A skill that fails goes to a hardening agent with the solver's per-option weights, then back through the gate. Items the solver gets wrong still need the final independent blind solve (no second defensible option) before they serve.

First pass (mean p(key): band-6 anchors / band-7 anchors / pilot): Boundaries 0.62 / 0.18 / 0.30 pass; Transitions 0.71 / 0.62 / 0.58 pass; Command of Evidence 0.82 / 0.84 / 0.81 pass (blind); Words in Context 0.88 / 0.88 / 0.87 pass (blind); Central Ideas 0.87 / 0.67 / 0.88, Inferences 0.80 / 0.73 / 0.84, Form, Structure, and Sense 0.91 / 0.76 / 0.91, Rhetorical Synthesis 0.85 / 0.75 / 0.84, Cross-Text 0.81 / 0.80 / 0.89, Text Structure 0.77 / 0.84 / 0.87 harden.

After hardening (same gate): Rhetorical Synthesis about 0.71 to 0.79 on the hardened items, pass; Text Structure 0.75 / 0.83 / 0.84, pass (anchors blind); Cross-Text 0.80 / 0.73 / 0.80, band 6; Central Ideas and Inferences still band 6 after two hardening rounds (the solver named each designed trap and rejected it for the intended reason; the levers left would make a second option defensible); Form, Structure, and Sense indistinguishable from its band-7 officials (0.82 to 0.93 on those), so the reviewer's band-7 verdict stands. A blind safety solve by a strong model over all 40 found no second defensible option and nothing unfair (40 of 40 agree). Promoted to `satbank/rw/<skill>__b7.json`: 28 items `band` 7, 12 items `band` 6 (Central Ideas, Inferences, Cross-Text), all `tier` hard.
