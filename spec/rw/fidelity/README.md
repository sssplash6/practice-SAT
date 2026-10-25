# Fidelity pass (paused 2026-10-12, evening)

Goal: authored items in `satbank/rw/` at least as faithful as official ones.

Done:
- `tools/check_rw.py` now fails a skill whose passages are plainer than official per tier (word length, 9+ letter words), whose sentence length is off by more than 15%, or whose key-longest rate is more than 10 points off. All 10 skills fail it at the moment.
- Blind round 1 (`round1/`): judges told our items from official ones with AUC 0.9 to 1.0; only 21 of 306 passed. The tells are now in `spec/rw/GENERATE.md` ("What gives an imitation away"); each item's tell is in `round1/tells.json`.

Not done (no item has been changed yet; all 306 are intact):
1. Rewrite every file to `REWRITE.md` (22 agents, about 14 items each; set `$SCRATCH` to a work folder).
2. Re-review the changed items (`"review": null`) to `spec/rw/VERIFY.md`.
3. Blind round 2: `python3 spec/rw/fidelity/build.py round2 round1` (run from the repo root), one judge per set to `JUDGE.md`, then `python3 spec/rw/fidelity/score.py round2`.

Progress (2026-10-12, max 3 agents at once): Inferences rewritten and reviewed (9 pass, 17 fixed). Rhetorical Synthesis 2/2 rewritten. Open item for the end: questions a reviewer wrote itself need one more independent blind solve: `inferences.S11.medium`.

## State after blind round 2 (2026-10-13)

All 306 items are rewritten and reviewed (every item has a `review`; reviewer-written items `inferences.S11.medium` and `text_structure_and_purpose.P_profile.hard` have a `second_blind`). `tools/check_rw.py` and `tools/rw_options.py` pass.

Blind round 2 (`round2/`, scores from `python3 spec/rw/fidelity/score.py round2`, judge summaries in `round2/summary.md`): no real gain. Mean p for our items 0.74 to 0.72; items passing as official (p 0.5 or below) 21 to 15, mostly literary. Where judges recognised no official item (Form, Structure, and Sense; Rhetorical Synthesis) AUC is 0.98 and 1.00. Elsewhere judges recognised about half the official items from memory, so AUC there is not meaningful.

The round-1 fixes created new tells, the same in every skill: over-specific passages (exact numbers per 100 words are 1.5 to 2 times official), researcher plus year plus institution packing, flawless polish (official items have contractions, casual asides, generic "researchers", em dash and parenthesis asides at about twice our rate), passages built backwards from the key (alternatives closed off in advance, details planted for distractors), near-miss trap distractors where official ones are accurate but off the goal, and frames copied from official items.

Feature check on the round-2 judgments (no agent cost): surface measures barely predict the judges. Single-feature AUC ours vs official is 0.41 to 0.61 (numbers per 100 words 0.61, chars per word 0.61, asides 0.43, key-longest 0.50) and Spearman rho with p is 0.1 to 0.3, while the judges separate at AUC about 1.0. Passage length is the strongest (our medians are 5 to 20 words over official in every skill because the gate demands at least the models' median; within-skill rho with p is 0.36 to 0.61 in six skills). Our literary items average p 0.51, informational 0.73: human-written text passes, composed text almost never does. The remaining tell is texture, which a brief revision will not fix.

Next (decided with the advisor, 2026-10-13; waiting on the user's choice of bar):
- Stop the gates that push toward tells: density as a two-sided band around official, not a floor; length near the official median, not above it.
- No more brief-revision rounds and no 5,000-item writer waves until a bar is chosen and something meets it.
- If the bar stays "judges cannot tell": change the pipeline, not the brief. Passage first, adapted from a real human-written source paragraph (press release, museum label, journal summary) with a 6-gram overlap check against the source; a different agent then writes the question. Fact cards for the 5,000 plan become source excerpts, not fact lists.
- Measure properly: pilot only in Form, Structure, and Sense and Rhetorical Synthesis (judges recognised no official item there), at least 15 items per arm, with officials recognised in round 1 or 2 excluded (`build.py` needs an id filter).
- Alternative bar: a panel of 2 or 3 of the user's own tutors rating a mixed set.
- Independent of all this: wire the 306 reviewed items into practice (`server/api_practice.py` reports no R&W bank).

## Tutor panel (bar option a, 2026-10-13)

`tutors/panel1/`: `SAT_RW_Tutor_Panel.pdf` (also in `~/Downloads`), `panel.html` and `key.json` (which items are ours). 85 items: 40 ours (4 per skill, one template each) and 45 official (4 per skill, 5 in the largest skills), graphs left out of both sides, officials with non-CB keys or known transcription gaps left out (so the official Inferences items are easy and medium). Built by `tutor_pdf.py panel1`, which refuses to overwrite a sent panel, then made fillable (595 checkbox and text fields) by `tutor_fields.py add panel1`; `tutor_fields.py read panel1 <returned pdfs>` pulls the answers out in `score.py`'s judged format. Score returned answer grids against `key.json`, leaving out items a tutor marked as seen; bar met if the tutors' pooled AUC is below 0.65.

Result (reported 2026-10-15): several mentors rated all 85 items 1 ("sure it is official"), ours included: AUC 0.5, a soft pass (identical ratings from every rater; returned PDFs not on file). They also asked for harder items than plain hard, which is CB's score band 7: that work continues in `spec/rw/band7/` (analysis, pilot, gate in `PROXY.md`). Its finding for the 5,000 plan: in Central Ideas and Inferences, distractor design alone did not reach band 7 (a blind solver named each designed trap and rejected it), which points back to the source-anchored passage pipeline above.
