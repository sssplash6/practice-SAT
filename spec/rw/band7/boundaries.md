# Boundaries: what makes a band-7 item

Source: every band 5, 6 and 7 item in `material/rw/cb_api/boundaries.json` (26 / 43 / 54 items). All 54 band-7 and all 43 band-6 items were read with CB's rationale. Only 19 of the 54 band-7 items are in our transcript set, so most of what follows was invisible to `spec/rw/boundaries.md`. Each item was hand-assigned a template and each wrong option a distractor tag (codes from section 5 of the skill report); numbers were then computed with Python (`register()` from `tools/check_rw.py` for the register measures). The rationale's "convention being tested" line was not used for templates: it is missing in older rationales and one phrase ("punctuation within a sentence") covers five different rules.

Band drift: 12 of the 95 transcript items sit outside their PDF tier (for example 1.4 and 1.17, filed easy, are band 6; 2.16, filed medium, is band 7). Everything below uses `band`. Several authored items were modelled on band 6 or 7 officials already (`S1_semicolon.easy` on a band-6 item, `S5_series.medium` on a band-7 item), so the bank is not entirely free of band-7 models, but no item was written to band-7 settings.

Terms: `L` and `R` are the words left and right of the boundary; the **run** is the sentence holding the blank as the student sees it, before the boundary is resolved (for period keys it spans both future sentences); the **opener** is whatever sits between the blank and the subject of the second clause.

## 1. Counts

### Template mix per band

| Family | Template | Band 5 | Band 6 | Band 7 |
|---|---|---|---|---|
| S1 joining clauses | S1_comma_conj (`L, but R`) | 3 | 2 | **0** |
| | S1_period | 3 | 7 | 10 |
| | S1_semicolon | 3 | 3 | 3 |
| | S1_colon_clauses | 0 | 3 | 5 |
| | S1_adverb (`L, though; R` and kin) | 1 | 4 | **11** |
| S2 clause plus modifier | S2_intro_comma | 2 | 1 | **0** |
| | S2_trailing | 1 | 0 | 4 |
| | S2_colon (incl. one lone-dash key at band 6) | 2 | 5 | 3 |
| S3 pairs | S3_comma_pair | 4 | 1 | **0** |
| | S3_dash_pair | 4 | 2 | 3 |
| | **S3_adverb_pair (new)** | 0 | 1 | 2 |
| S4 no punctuation | S4_subj_verb | 1 | 3 | **0** |
| | S4_compound | 1 | 1 | **0** |
| | S4_restrictive | 0 | 7 | 8 |
| S5 series | S5_series (all complex, semicolons) | 1 | 3 | 5 |
| | Total | 26 | 43 | 54 |

New template **S3_adverb_pair**: a conjunctive adverb set off by a comma pair where no second main clause follows (a participial phrase, or the main clause after an intro phrase), so the textbook `; however,` and `, however;` options are both wrong. Items: 5cc69ee1 and e3c1b4f7 (band 7), 1ee4485c (band 6). It uses the S1_adverb option menu but the S3 key.

### Rule inventory per band (what the item actually tests)

| Rule | 5 | 6 | 7 | Band-7 key shapes |
|---|---|---|---|---|
| Comma + coordinating conjunction | 3 | 2 | 0 | |
| Period, second sentence opens with a modifier | 3 | 7 | 10 | `L. Known`, `L. As`, `L. Because`, `L. Creations` |
| Semicolon between clauses | 3 | 3 | 3 | subject of clause 1 is a That-clause (2), clause 2 subject is a gerund (2) |
| Colon between clauses (second explains the first) | 0 | 3 | 5 | `functions:`, `emerged:`, `food:`, `spectrum:`, `indiscriminate:` |
| Adverb closes clause 1, contrast with the previous sentence | 0 | 1 | 10 | `, though;` 5, `, however;` 3, `, though:` 1, `, however:` before a list 1 |
| Adverb opens clause 2 | 1 | 1 | 0 | (band 5 and band 6: `; rather,`) |
| Adverb closes a dash supplement, then a clause join | 0 | 0 | 1 | `, respectively;` |
| Other adverb item (`however. It`, `, for one. The`) | 0 | 2 | 0 | |
| Comma pair around an adverb, no clause join | 0 | 1 | 2 | `observation, however,`, `work, though,` |
| Intro element comma | 2 | 1 | 0 | |
| Trailing nonrestrictive element (participle, absolute, sentence appositive) | 1 | 0 | 4 | `supposed, a finding`, `quilts, the stitching`, `writers, among them` |
| Colon (or dash) before an explanation or list | 2 | 5 | 3 | `extensive: a`, `continents: geological`, `music: the flute. A` |
| Dash pair / comma pair partner | 8 | 3 | 3 | nested: `Ecuador)` + dash, comma inside a dash pair |
| Restrictive title + name | 0 | 4 | 5 | `critic Stina Chyn claims`, `French portrait artist Marie-Denise Villers` |
| Restrictive appositive, not a person | 0 | 0 | 2 | `chemical compound aluminum oxide`, `fellow OECD nations Chile` |
| Restrictive that-clause | 0 | 3 | 1 | `so dependable that` |
| Subject-verb, modifier-noun, compound (no mark) | 2 | 4 | 0 | |
| Complex series (semicolons) | 1 | 3 | 5 | three of five add a second rule inside the option |

Rules that disappear at band 7: comma + conjunction, intro comma, plain comma pairs, subject-verb and compound no-mark items. Rules that concentrate at band 7: the adverb family (13 of 54, 24%, against 5 of 43 and 1 of 26), colon between clauses, trailing noun-phrase elements, title + name.

## 2. What separates 7 from 6, measured

Reasoning steps (rubric, since the skill report does not count them): 2 base steps (status of the left side, status of the right side), plus 1 each for an opener of 3+ words before clause 2's subject, a deciding mark elsewhere in the passage (pair partner or series semicolon), two or more boundary slots varying across the options, and a distractor that is only wrong by meaning. "Cue outside the window" means the evidence that kills the best distractor is more than 6 words from the blank (opener of 6+ words, partner 7+ words away) or in another sentence (meaning-decided items).

| Signal | Band 5 | Band 6 | Band 7 | Gap 6 to 7 | Separates? |
|---|---|---|---|---|---|
| Items with a meaning-decided distractor (tag LOG) | 4% | 14% | **28%** | doubled | **yes, strongest** |
| Adverb items (S1_adverb + S3_adverb_pair) | 4% | 12% | 24% | doubled | yes (rule mix) |
| Cue outside a 6-word window | 31% | 37% | **57%** | +20 points | yes |
| Reasoning steps, mean / share with 4+ | 2.7 / 8% | 3.0 / 19% | 3.2 / 35% | +0.25 / +16 points | yes, moderate |
| Run length, mean (median) | 35 (34) | 32 (33) | 37 (38) | +5 words | moderate |
| Runs of 38+ words | 31% | 35% | 52% | +17 points | moderate |
| Words per sentence (passage) | 31.3 | 30.2 | 35.3 | +17% | moderate |
| Opener before clause 2's subject, clause-join items: mean / share 8+ words | 3.0 / 10% | 5.1 / 26% | 6.4 / 36% | +1.3 words | weak |
| S1_period opener only: median (range) | 3 (0 to 5) | 8 (0 to 26) | 10 (5 to 31) | +2 | weak |
| Words after the blank in the run | 18.5 | 16.2 | 19.1 | +3 | weak |
| Passage words, median | 51 | 46 | 47 | none | no |
| Chars per word | 5.10 | 5.17 | 5.18 | none | no |
| Words of 9+ letters | 13.6% | 14.8% | 14.9% | none | no |
| Rarity (words found in 3 or fewer of the 1,845 official R&W passages) | 18.4% | 17.9% | 17.5% | none | no |
| Option length, words | 2.1 | 2.7 | 2.3 | reversed | no |
| Key is the longest / shortest option | 50% / 31% | 42% / 35% | 52% / 33% | noise | no |
| Key-passage word overlap minus distractor overlap | 0.01 | -0.01 | -0.01 | none | no (options share their words) |
| Same-word option sets varying at 2+ slots | 20% | 69% | 65% | none | separates 5 from 6 only |
| Partly right distractors (match the key at one slot) per item | 0.5 | 1.4 | 1.1 | reversed | no |
| Items with 2+ comma-splice distractors | 4% | 12% | 6% | reversed | no |

Plainly: band 7 is not denser prose, not longer passages and not more slots per option. It is a different rule mix (adverbs, colons between clauses, trailing noun phrases), a longer unresolved sentence, and distractors whose fault is in meaning or far from the blank. The skill report's "hard items stack comma splices" describes band 6 better than band 7.

## 3. What separates 7 from 6, read

1. **The adverb belongs to clause 1 and answers the previous sentence.** 10 of 11 band-7 S1_adverb keys close clause 1 (`, though;`, `, however;`, `, though:`); the contrast is with the sentence before, so `L; though R` and `L; however, R` read like the textbook pattern and fail only on meaning. Example: "Compiling isn’t exclusive to certain programming languages, however;" (b771d175). At band 6 the adverb items still include plain splice sets (`however. It`, `; rather,`).
2. **The same adverb, but no clause join.** 5cc69ee1 ("recognize the need for direct observation, however, recommending...") and e3c1b4f7 put `; however,` and `, though;` among the options when the right side is a participial phrase or a main clause after an intro phrase. A student who memorised the band-7 adverb pattern picks a semicolon.
3. **The opener after a period key could modify clause 1's last noun.** "Pather Panchali, a quiet black-and-white drama" reads as an appositive until "Ray’s film was" arrives 9 words later (0fa289a7). Six of ten band-7 openers are noun-phrase appositives or past participles of this kind ("Creations so small that", "Developed by Japanese violinist", "Known as members of the office"); CB's own rationale for 4b424102 says the phrase "could logically be attached to either" clause. Band-6 openers are more often prepositional or gerund subjects ("In 1420 CE,", "Adding a light-colored covering").
4. **Openers that carry their own punctuation and length.** 952fd392's opener runs 31 words and contains a semicolon series; 5bed774c's "As evidenced by his belief that instead of evoking particular emotions" runs 30.
5. **Clause 2 starts with a subordinator.** "whereas the genome in each cell contains a complete DNA sequence," (bb4557cf), "whereas rennet-coagulated cheesemaking became key" (9579581e), "Because the hole’s small size restricts light" (615f001e): the second clause looks dependent, so a comma looks legal.
6. **Clause 1 hides its subject.** "That the geographic center of North America lay in the state of North Dakota" (7e37affc, 235c8338 is the same frame); clause 2's subject is a gerund ("establishing its precise coordinates proved more divisive").
7. **A legal mark is rejected by meaning or context.** 7e37affc rejects a colon because clause 2 contrasts rather than explains; 952fd392 rejects a semicolon because the sentence already uses semicolons inside a series. Outside the adverb items, these are the only two items in bands 5 to 7 that offer two different strong marks at the same position and reject one on meaning or context (a break of the "no twin" rule); both are band 7. Colon-clause keys add `while` / `, while` / `and` distractors that are wrong by relation (6fac7f45, 2c4cd76d, 8772475b).
8. **Trailing noun phrases that contain a finite verb.** "a finding that, if true, would overturn current theories" (0b005ae2), "a decision that, by allowing the narrative to be shaped" (e67f9967), "among them Nigerian American essayist ... Teju Cole, who has written" (adf210e7): the phrase looks like a clause, so period and semicolon options look right.
9. **Restrictive appositives beyond the name pattern.** "the chemical compound aluminum oxide" and "fellow OECD nations Chile and Luxembourg"; title + name sets add a second slot after the name ("critic Stina Chyn claims" then a quotation).
10. **Two levels of supplement in one option.** "Quito (present-day Ecuador)" then a closing dash (83898524); a comma inside a dash pair ("described, from hair to grass to sculptures" then the dash, 6e071432); `, respectively;` where the comma belongs to a dash element and the semicolon joins clauses (e41018de).
11. **Series with a second rule inside the option.** "an uncommon practice at the time;" (no comma: the phrase is restrictive, aaa1907f); "species, both native and nonnative;" (db24ecc9); "leaves; man-made trash," (9c3630b9).

## 4. Distractor recipes at band 7

Share of items carrying at least one distractor with the tag (instances in brackets).

| Recipe (skill report section 5) | Band 5 | Band 6 | Band 7 |
|---|---|---|---|
| Comma splice | 38% (12) | 44% (24) | 52% (32) |
| **Logic-wrong (legal shape, wrong meaning)** | 4% (1) | 14% (8) | **28% (21)** |
| Semicolon with a non-clause | 23% (6) | 26% (12) | 30% (18) |
| Missing required mark | 50% (13) | 30% (15) | 22% (14) |
| Misplaced boundary (opener glued to clause 1, adverb on wrong side) | 15% (4) | 23% (10) | 22% (14) |
| Fused sentence | 23% (6) | 19% (8) | 20% (12) |
| Colon in the wrong place | 27% (7) | 19% (8) | 17% (9) |
| Comma intrudes into a unit | 8% (5) | 26% (21) | 15% (12) |
| Added word creates the error (`which was a`, `who are known`, `it’s because`, `that,`) | 12% (5) | 9% (5) | 15% (10) |
| Fragment | 19% (5) | 19% (8) | 15% (8) |
| Conjunction without comma | 31% (8) | 21% (9) | 13% (7) |
| Commas around a restrictive element | 0 | 5% (2) | 11% (7) |
| Series errors | 4% (1) | 7% (6) | 9% (10) |
| Mismatched pair | 23% (7) | 7% (4) | 6% (3) |
| Stray dash | 4% (1) | 7% (3) | 4% (2) |

- **Dominant at band 7**: comma splice (as at every band), then logic-wrong and semicolon-with-a-non-clause. Logic-wrong is the recipe that grows most; mismatched pairs, missing marks and conjunction-without-comma fade.
- **Only at band 7**: a colon rejected because the relation is contrast (7e37affc); a semicolon rejected because of series semicolons in the same sentence (952fd392); one dash asked to close a pair and join clauses at once (e41018de); a boundary that leaves two uncoordinated subjects ("music. The flute, a relatively quiet instrument, its full range", 3a2d77d7); commas around a restrictive non-person appositive (59a246dc).
- **How the hardest distractor is built**, per template:
  - S1_adverb: the "opens clause 2" placement (`L; however, R`), which is the pattern students are taught; it fails only against the previous sentence.
  - S1_period: the comma version (`L, Known as ...`), which reads as a normal trailing modifier of clause 1's last noun; the splice shows up 7 to 31 words later at clause 2's subject.
  - S1_colon_clauses / S1_semicolon: a relation word (`while`, `and`) or the other strong mark (colon for semicolon), wrong by meaning.
  - S2_trailing / S2_colon: semicolon or period before a noun phrase that contains a relative clause with a finite verb.
  - S4_restrictive: commas around the name (`critic, Stina Chyn, claims`), which look polite.
  - S5_series: the comma version of the series mark when the matching semicolon comes later in the sentence.
  - S3 pairs: the mark at the wrong nesting level (dash where the inner comma belongs).

## 5. Band-7 writing recipe

Our options are built by code once the sentence exists (`spec/rw/README.md`, build order 1). "Where" says who controls the knob: **Plan** (batch planner), **Passage** (the writer prompt), **Options** (the option builder), **Judge** (the acceptance check).

### Settings the code can control

| Knob | Band 6 | Band 7 | Where |
|---|---|---|---|
| Rule mix per 50 items | S1 22, S4 13, S2 7, S5 3, S3 5 | S1 27 (adverb 10), S4_restrictive 7, S2 6 (trailing 4), S5 5, S3 5 (adverb pair 2); no comma_conj, intro comma, comma pair, subj-verb, compound | Plan |
| Logic-wrong distractor | 1 in 7 items | at least 1 in every adverb and colon-clause item (about 30% of the batch) | Options |
| Adverb side in the key | mixed | closes clause 1 (`L, adv; R` or `L, adv: R`); the clause-1 claim must contrast with the previous sentence | Passage + Options |
| Run length (sentence holding the blank, unresolved) | median 33 | 38 to 50 words | Passage |
| Opener before clause 2's subject (period keys) | 0 to 26, median 8 | 8 to 30, median 10; an appositive noun phrase or past participle that could modify clause 1's last noun | Passage |
| Clause 2 opener type (colon and semicolon keys) | subject first | a subordinate clause (`whereas`, `because`) or a gerund subject | Passage |
| Clause 1 subject | noun phrase | a That-clause or long noun clause, in 1 of 3 semicolon items | Passage |
| Trailing element (S2) | participial phrase | sentence appositive or absolute phrase whose noun has a relative clause with a finite verb | Passage |
| Slots per option | 1 to 3 | same; add the second slot as a different rule (restrictive phrase in a series item, verb-quotation after a name) rather than a second mark of the same kind | Options |
| Cue distance | 37% outside 6 words | 55%+ outside 6 words | Plan + Judge |
| Twin marks (two legal marks offered) | never | allowed only with a stated meaning or context reason (contrast vs explanation, series semicolons) | Options + Judge |

### Per template

- **S1_period** (10 band-7 items, e.g. 3.8, 3.32, 3.35). Change from band 6: lengthen the opener to 8 to 30 words and make it a noun-phrase appositive or past participle that describes clause 2's subject but could hang on clause 1's last noun; let the opener carry internal commas or a short series. Options: `L. R` key, `L, R` (splice), `L R` (glued), and one of `L and R`, `L, which was a R`, `L who are R`, `L that, R`.
- **S1_adverb** (11). Write clause 1 so that it corrects or qualifies the previous sentence ("hardly pristine", "ultimately speculative", "doesn’t make such decisions single-handedly") and clause 2 elaborates it. Key `L, though; R` or `L, however; R`; colon variant `L, though: R` when clause 2 explains. Distractors: `L; though R` or `L; however, R` (logic), `L, though R` (logic or fused), `L, though, R` (splice). Keep `though` and `however`; band 7 never uses `rather` or `for one`.
- **S3_adverb_pair** (new, 2). Main clause + adverb + participial phrase, or intro phrase + adverb + main clause. Key `L, adv, R`; distractors `L; adv, R`, `L, adv; R`, `L. Adv, R` or `L, adv R`. Build it from the S1_adverb menu so the two templates share traps.
- **S1_colon_clauses** (5). Clause 1 announces ("develop different functions", "divergent strategies ... emerged", "notoriously indiscriminate"); clause 2 explains, often opening with `whereas` or a participial phrase. Distractors: `L,`, `L`, and a relation word (`L while`, `L, while`, `L and`).
- **S1_semicolon** (3). Clause 1 subject is a That-clause or the sentence is long and parallel; clause 2 subject is a gerund. Offer a colon distractor only when clause 2 contrasts (logic), plus `L,` and `L`, or `L that` / `L which` (added word).
- **S2_trailing** (4). Main clause + `, a finding that ...` / `, a decision that, by ..., amplified` / absolute `, the stitching barely visible` / `, among them X, who has written`. Distractors `L;`, `L.`, `L` or `L, and`.
- **S2_colon** (3). Clause ending in an announcing word ("something far more extensive", "the origin of Earth’s continents") + a noun phrase with a relative clause; or a colon + period in one option ("music: the flute. A"). Distractors: semicolon, period, comma + `it was a`.
- **S3_dash_pair** (3). Put a second level inside the dash element (parentheses, a comma-set supplement, an `or X, as ...` alternative name); partner 7 to 10 words away; options mix the levels.
- **S4_restrictive** (8). Title + name followed by more material that tempts a comma (verb, quotation, dates, `and his colleagues`), or a non-person restrictive appositive (`the chemical compound X`, `fellow OECD nations X and Y`). Options: `title Name`, `title, Name`, `title Name,`, `title, Name,`, or colon/semicolon/dash.
- **S5_series** (5). Three long items (verb phrases or nouns with `such as` supplements), blank in item 1, the revealing semicolon after the blank; add a second rule inside the option (restrictive phrase with no comma, or the comma before a supplement).
- **No band-7 items**: S1_comma_conj, S2_intro_comma, S3_comma_pair, S4_object, S4_subj_verb, S4_compound, S6_question. Do not write band-7 versions of these; move their hard-tier slots to the templates above. Our current hard set includes S1_comma_conj, S3_comma_pair, S4_subj_verb and S4_compound items.

## 6. Checks

| Check | How | Band 6 vs 7 | Reliability |
|---|---|---|---|
| Rule mix | Plan counts per batch against the table above | template shares | High for a batch, says nothing per item |
| Logic-wrong distractor present | Option-builder label; the judge must name the relation (contrast, explanation) or the previous sentence when rejecting it | 14% vs 28% | High as a batch rate (target 25 to 35%); per item it marks band 7 but most band-7 items lack it |
| Cue outside a 6-word window | Computed from labels: opener length, partner distance, logic tag | 37% vs 57% | Moderate; target 55%+ per batch |
| Local-window solve (agent) | A fast solver sees only 6 words each side of the blank plus the options; if it picks the key with confidence the item is band 6 or lower. Exempt S4_restrictive, which is local at every band | follows from the row above | Not yet tested on official items; run it on the 97 band 6 and 7 officials before trusting it |
| Run length 38+ words | Computed | 35% vs 52% | Moderate; easy to pad, so only count it with the cue check |
| Reasoning steps 4+ | Rubric in section 2 from labels | 19% vs 35% | Moderate, batch level |
| S1_period opener 8+ words and attachable to clause 1 | Length computed; attachability by judge prompt ("could this phrase modify the last noun before the boundary?") | 4 of 7 vs 8 of 10 at 8+ words | Weak alone |
| Do not use | Passage length, chars per word, long-word share, rarity, option length, key length rank, key overlap, slot count, partly right count, splice count | no gap or reversed | These do not separate 6 from 7 |

Applied to our 12 authored hard items: mean run 36 words (fine), but no distractor is labelled logic-wrong (the S1_adverb hard item has the band-7 shape through its `; though` option, labelled as a subordinate-clause error), and 4 of 12 use templates with no band-7 items.

## Appendix: template assignment, bands 6 and 7

CB ids (`cb_id` in `material/rw/cb_api/boundaries.json`), transcript id in brackets where one exists.

| Template | Band 6 | Band 7 |
|---|---|---|
| S1_adverb | 2bb7416a (3.7), 5670a657 (3.29), 81f43b85, a9e5b788 (3.5) | 21e58a83, 5aa171de, 790fc366 (3.6), 84658166, a05cc490, b771d175, be37d4ae, c06af4d8 (3.25), c15069eb, e41018de, f78997cf (3.33) |
| S1_colon_clauses | 435809d8, 9d4a701b, e76e74e8 | 2c4cd76d, 6fac7f45, 8772475b, 9579581e, bb4557cf (3.16) |
| S1_comma_conj | 59094d87 (3.9), 7ce4ee13 | none |
| S1_period | 1b97cce9, 5ee7fb04, 67667d72 (2.10), 73a6603c, 886dc9f9, aab74a3b (3.4), b15724fc (3.20) | 0fa289a7 (3.8), 4b424102, 5bed774c (3.32), 615f001e, 707461d8 (3.35), 940ff6f7, 952fd392, a872c60a (3.28), ba8ebf49 (3.10), f45ae404 (3.17) |
| S1_semicolon | 1724dac2 (1.4), 2c9c6ca9, 3fee46f2 | 235c8338, 7e37affc, eb95235b |
| S2_colon | 92f309b2, c101fc44 (2.15), c468db1c (3.22), e7afd0a1, fba5d8d1 (3.2) | 3a2d77d7 (3.19), e9aee0d8 (3.18), f30a478e (3.26) |
| S2_intro_comma | 8a264a54 | none |
| S2_trailing | none | 0b005ae2, 62120607 (3.24), adf210e7, e67f9967 |
| S3_adverb_pair | 1ee4485c | 5cc69ee1, e3c1b4f7 |
| S3_comma_pair | fdb16e20 (3.12) | none |
| S3_dash_pair | 626a1642 (3.34), aacddbd8 | 109d5bbb (3.15), 6e071432, 83898524 |
| S4_compound | 6ea8c23f (3.3) | none |
| S4_restrictive | 4dcedc31, 594b4a94 (3.11), 5ef9fc48, 603755a5 (1.17), 6181924a, 80aa7690 (3.30), d4fe8f03 | 0a114526, 13fcf575, 59a246dc, 5aae2475, 6d4b2e1e (3.14), 78e978b5 (3.27), 960dec02 (3.1), fa36d803 |
| S4_subj_verb | 2fd05c15, 8d00cd7c, f868d438 (3.13) | none |
| S5_series | 78b88c04 (3.21), a8fa749a (3.23), c49e946e | 05a14e18, 9c3630b9, aaa1907f, c04e9136 (2.16), db24ecc9 |
