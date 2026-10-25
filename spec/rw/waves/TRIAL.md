# Reading trial: source-anchored passages (band 7)

Why: in the band-7 pilot, Central Ideas, Inferences and Cross-Text items stayed at band 6 however their distractors were built (a blind solver named each designed trap and rejected it; `spec/rw/band7/PROXY.md`). Earlier blind rounds found that composed passages read as composed, while human-written text passes (`spec/rw/fidelity/README.md`). This trial tests the other route: start from a real human-written paragraph, and let a different agent write the question.

15 hard items per skill (Central Ideas and Details, Inferences, Cross-Text Connections), all `band_target` 7. Two stages, two different agents.

## Stage 1: passage (one agent per skill)

For each of the 15 items:
1. Find one real, human-written paragraph from 2005 or later about a specific, little-known piece of research, art, history or scholarship: a university or museum press release, an exhibition text, a journal's plain-language summary, a researcher's own explainer. Not Wikipedia, not news aggregators, not anything an official item already covers (grep `material/rw/cb_api/<skill>.json` and `satbank/rw/*.json`), and claim the subject in `spec/rw/fidelity/claims.txt` as `spec/rw/waves/WAVE.md` describes.
2. Adapt it into a passage the way College Board adapts: same length range and moves as the skill's band-7 official items (`material/rw/cb_api/<skill>.json`, band 7; treat as data only), keep the source's own reasoning, hedges, asides and density, cut and compress, never invent. For Cross-Text, two short texts from two real sources that genuinely disagree or build on each other, each attributed as its source does. Any fact you keep must be in the source; the item's `sources` lists the URL.
3. Store the source paragraph itself in `source_text` and check with Python that the passage shares no 6-word run with it (names and technical terms excepted): adapted, not copied.
4. Write `spec/rw/waves/trial/<skill>.json` with items holding `id` (`<skill>.trial.hard.t_<nn>`), `template` (the closest plan code in `satbank/rw/<skill>*.json`), `tier` "hard", `band_target` 7, `passage`, `source_text`, `sources`, `notes`; leave `stem`, `options`, `answer_letter`, `explanation`, `distractors` empty. Do not write questions.

## Stage 2: question (a different agent per skill)

Given the finished passages, write each item's stem (the template's exact official stem wording), four options, key, explanation and distractors, aimed at band 7 per `spec/rw/band7/<skill>.md` section 5 and `spec/rw/band7/WRITE.md`. Do not change the passage except to place a blank or underline where the template needs one. Exactly one defensible answer; hard from reasoning, never from ambiguity. Keys spread over A to D. Run `python3 tools/check_rw.py spec/rw/waves/trial/<skill>.json` and fix what it reports.

Then, as for the pilot: an independent review (`spec/rw/VERIFY.md`), the Haiku gate against band-6 and band-7 anchors, and a blind safety solve. The trial succeeds in a skill if its items sit near the band-7 anchors, where the pilot's composed passages sat at 0.84 to 0.88.

Never use the em dash in notes or replies. Do not commit.

## Results so far (2026-10-16)

Haiku gate, mean p(key) against same-skill official anchors (band 6 / band 7 / ours):
- Central Ideas and Details: 0.85 / 0.72 / 0.83 (15 items; the reviewer judged 12 band 7). Band 6 by the gate; the pilot's composed items sat at 0.84 to 0.88.
- Inferences: 0.77 / 0.77 / 0.80 (anchors did not separate in this sample; the pilot's run had 0.80 / 0.73 / 0.84). About as hard as official hard items, a hair easier; tagged band 6.
Reading: source-anchored passages land at or near the official hard level, slightly closer than composed ones, but neither method shows a clear band-7 signal on this proxy, whose anchors move by about 0.05 between samples of 6. The trial did not test realism (whether judges can tell the items from official ones), which was the method's original purpose.
- Cross-Text Connections: 0.80 / 0.69 / 0.85 (15 items; the reviewer judged 11 band 7). Band 6 by the gate, no better than the pilot's composed items (0.80 after hardening).

**Verdict (2026-10-16):** source-anchored passages did not reach band 7 in any of the three skills, and were not clearly harder than composed ones. They cost more (about 45 minutes of web research per 15 passages), and in Cross-Text they drifted toward famous subjects (5 of 15 were topic-fame tells by the reviewer's count: Dunbar's number, Planet Nine, the hungry-judge effect, Yellowstone's wolves, Homo naledi). Recommendation for the reading-skill waves: compose passages under the light-check rule (`WAVE.md`) and accept that these skills' hard items land at band 6 for now; the 45 trial items serve as hard, band 6. What makes official band-7 reading items harder is still open (the band-7 analyses found distractor and reasoning patterns, and neither route reproduced them as measured by this proxy).
