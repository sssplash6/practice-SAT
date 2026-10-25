# Form, Structure, and Sense: what makes a band-7 item

Source: every band 5, 6 and 7 item in `material/rw/cb_api/form_structure_and_sense.json` (25 / 29 / 32 items). All 32 band-7 and all 29 band-6 items were read with CB's rationale. Only 12 of the 32 band-7 items are in our transcript set, and the largest band-7 cluster (section 3, move 1) has just one transcript member, filed at band 6, so `spec/rw/form_structure_and_sense.md` could not see it. Each item was hand-assigned a template and each wrong option a distractor tag (codes from section 5 of the skill report, R3 recipes W/N/P/E/V/S); numbers were computed with Python (`register()` from `tools/check_rw.py` for register measures).

Band drift: 13 of the 92 transcript items sit outside their PDF tier (2.6, filed medium, is band 7; 2.1 and 2.9 are band 6; 3.10 and 3.11, filed hard, are band 3). Everything below uses `band`. Some authored items were already modelled on band 6 or 7 officials (`R5_possessive_det.medium` on a band-7 item, `R2_ing.medium` and `R2_finite_second.medium` on band-6 items), but none was written to band-7 settings.

Terms: the **run** is the sentence holding the blank; the **anchor** is the word the blank must agree with or wait for (subject head for agreement, the downstream main verb for verb-form items, the antecedent for pronouns); **attractors** are nouns of the opposite number between anchor and blank.

## 1. Counts

### Template and rule mix per band

| Rule | Template | Band 5 | Band 6 | Band 7 |
|---|---|---|---|---|
| R1 subject-verb agreement | R1_be | 4 | 3 | 2 |
| | R1_lex | 3 | 3 | 5 |
| | R1_quant_compound | 2 | 0 | 3 |
| | R1_rel_poss | 1 | 1 | 2 |
| | **R1 total** | 10 | 7 | **12** |
| R2 finite vs nonfinite | R2_finite_main | 1 | 1 | 0 |
| | R2_finite_second | 0 | 2 | 0 |
| | R2_to_inf | 0 | 1 | 0 |
| | R2_ing (trailing phrase; at band 7 absolute phrases) | 0 | 1 | 2 |
| | **R2_interrupter (new)** | 0 | 1 | **9** |
| | **R2 total** | 1 | 6 | **11** |
| R3 modifier placement | R3_prep_gerund | 3 | 3 | 1 |
| | R3_past_participle (incl. "Compared with that of") | 3 | 3 | 3 |
| | R3_ing_participle | 1 | 2 | 1 |
| | R3_appositive | 1 | 3 | 0 |
| | **R3 total** | 8 | **11** | 5 |
| R4 tense | R4_past_dated (past progressive) | 1 | 0 | 0 |
| R5 pronoun | R5_personal | 3 | 2 | 0 |
| | R5_possessive_det | 0 | 3 | 2 |
| R6 plural vs possessive | R6_grid / R6_individual | 2 / 0 | 0 / 0 | 1 / 1 |
| | Total | 25 | 29 | 32 |

New template **R2_interrupter**: the blank sits right after the subject (sometimes it holds the subject's last word) and opens a phrase that runs 9 to 21 words before the sentence's real finite verb. The key is nonfinite (`searching`, `dating`, `examining`, `suggesting`, `including`, `Serra, intending`, `Udé, having`) or just the comma that opens a supplement whose participle is already in the passage (`works,` before "much admired", `swimming,` before "widely understood"). Every distractor is a finite verb. Band-7 items: 1a61e2ae, 3a1239d2, 505054e3, 9127635a, a2816c7f, aa443c4b, c9a677e9, d222f7d9, f768090a; band-6 member: transcript 3.9 (61160f0a, "Madeline L’Engle, ______ to create"), which our plan files under R2_ing.

### Rule inventory with sub-rules (band 5 / 6 / 7)

- **R1 agreement (10 / 7 / 12).** Each item counted once, first matching row: intervener containing its own finite verb of the opposite number 0 / 1 / 5 ("which include", "which seem", "the organism uses", "a person has internalized", "what traits distinguish"); quantifier head "each one of" / "many of whom" 1 / 0 / 1 (a second band-7 "each one of" item is in the row before); compound subject (incl. "X and Y, not Z") 1 / 0 / 1; possessor of the other number before the head 0 / 0 / 2 (compound possessor + singular "analysis"; singular "her book’s" + plural "musings"); gerund subject 0 / 1 / 0; inverted subject 1 / 0 / 0; relative-clause verb 1 / 1 / 0; any other head with prepositional, participial or appositive interveners 6 / 4 / 3. Plural keys 4 / 2 / 6.
- **R2 verb form (1 / 6 / 11).** Missing main verb 1 / 1 / 0; second verb of a compound predicate or verb of a that-clause 0 / 2 / 0; purpose infinitive 0 / 1 / 0; trailing participial phrase 0 / 1 / 0; absolute phrase (noun + participle after a complete clause) 0 / 0 / 2; interrupter between subject and delayed main verb 0 / 1 / 9.
- **R3 dangling modifier (8 / 11 / 5).** Plain agent or thing as the right subject 5 / 9 / 2; "the Y of X", possessive or "findings from" as the right subject 1 / 2 / 3; passive key 2 / 0 / 0; "Compared with (to) that of" openers 0 / 0 / 2.
- **R5 pronoun (3 / 5 / 2).** Personal pronoun number 3 / 2 / 0; possessive determiner its/their vs contractions 0 / 3 / 2; pronoun before its antecedent 0 / 1 / 1; antecedent 15+ words away 1 / 1 / 2.
- **R6 apostrophes (2 / 0 / 2).** Two- or three-slot grid 2 / 0 / 1 (band 7: generic plural possessor "objects’"); individual possession 0 / 0 / 1.
- **R4 tense (1 / 0 / 0).** Tense items stop at band 5.

The hard-tier story in the skill report ("dangling modifiers carry 43% of hard") is a band-6 story: R3 is 38% of band 6 and 16% of band 7. Band 7 is 72% agreement and verb-form items (R1 + R2) built around long interrupters.

## 2. What separates 7 from 6, measured

Reasoning steps (rubric): 1 base step (what the blank must supply), plus 1 per extra rule dimension the options vary on (number, finiteness, punctuation, tense, spelling, pronoun kind, apostrophe, modifier subject), plus 1 if the anchor is 10+ words away, 1 if at least one attractor sits between, 1 if 15+ words of the run follow the blank. "Cue outside the window" means the anchor is more than 6 words from the blank.

| Signal | Band 5 | Band 6 | Band 7 | Gap 6 to 7 | Separates? |
|---|---|---|---|---|---|
| R1 + R2 share / R2_interrupter share | 44% / 0 | 45% / 3% | 72% / 28% | +27 / +25 points | **yes, strongest (rule mix)** |
| Words after the blank in the run: mean (median) | 8.5 (7) | 10.6 (9) | 17.9 (16) | +7 words | **yes** |
| Runs with 15+ words after the blank | 12% | 28% | 53% | +25 points | **yes** |
| Run length: mean (median) | 23 (25) | 26 (27) | 33 (34) | +6 words | yes |
| Runs of 30+ words | 24% | 45% | 63% | +18 points | yes, moderate |
| Words per sentence (passage) | 23.9 | 25.1 | 29.6 | +18% | moderate |
| Cue outside a 6-word window | 40% | 48% | 69% | +21 points | yes |
| Reasoning steps: mean / share with 4+ | 1.9 / 8% | 2.2 / 21% | 2.8 / 38% | +0.5 / +17 points | yes, moderate |
| Anchor distance (R1, R2, R5): mean (median) | 9.4 (9) | 13.1 (12) | 14.7 (16) | +1.6 | weak |
| R1 head-to-blank distance, mean | 7.6 | 12.7 | 13.2 | +0.5 | **no** (separates 5 from 6 only) |
| R1 attractors: mean / items with 2+ | 1.4 / 5 of 10 | 1.7 / 4 of 7 | 2.5 / 8 of 12 | +0.8 | yes, small n |
| R1 opposite-number finite verb inside the intervener | 0 of 10 | 1 of 7 | 5 of 12 | +35 points | yes, small n |
| Option sets varying on 2+ rule dimensions | 12% | 24% | 31% | +7 points | weak |
| Passage words, median | 41 | 44 | 51.5 | +7 | weak (mean 41.7 vs 45.0) |
| Chars per word | 5.26 | 5.25 | 5.35 | +0.1 | no |
| Words of 9+ letters | 14.6% | 16.5% | 16.9% | none | no |
| Rarity (words in 3 or fewer of the 1,845 official passages) | 18.1% | 20.3% | 19.1% | reversed | no |
| Option length, words | 5.0 | 6.5 | 3.6 | follows the R3 share | no |
| Key is the shortest / longest option | 48% / 12% | 59% / 3% | 41% / 9% | noise | no |
| Key-passage overlap minus distractor overlap | -0.01 | -0.03 | -0.08 | R3 artefact | no |
| R3 opener length / option length | 11.8 / 11.6 | 10.3 / 14.5 | 11.2 / 13.9 | none | no |

Plainly: band 7 does not come from rarer words or longer options. It comes from where the deciding word sits (after the blank, 9 to 21 words downstream), from interveners that contain their own verbs, and from a rule mix tilted to verb form. Raw subject-to-verb distance stops helping after band 6.

## 3. What separates 7 from 6, read

1. **A finite verb that reads correctly until the real verb arrives (R2_interrupter, 9 of 32).** "scientists ______ for evidence of self-awareness in snakes" accepts `searched` until "adapted" arrives 16 words later (3a1239d2). Same in "Aslanian’s macroanalysis ______ nearly 1,000 book titles published between 1512 and 1800 shows" (c9a677e9) and "a unique tradition of embroidery ______ back over two thousand years" (505054e3). In 4 of 9 the phrase has no commas at all (a restrictive participle), so no punctuation warns that the subject is interrupted. The band-6 member has commas around it.
2. **Punctuation inside the verb-form options (5 of 9 interrupter items, 0 at band 6).** `Udé, having` / `Udé, has` / `Udé has` / `Udé`; `Serra, intending` / `Serra, intends`; `works,` / `works were` / `works, were` / `works had been`. The student must decide finiteness and the opening comma together, and the comma + finite version looks like a correct supplement.
3. **Absolute phrases after a complete clause (R2_ing at band 7).** "their design ______ airflow, protection from insects" (81f09e07) and "its vehicles ______ by collectors" (c88ba1b7): the noun before the blank lets every finite option form a full clause, so the error is a comma splice, not a missing subject (band 6: "appeal, ______ her the moniker").
4. **Interveners with their own verb (R1).** "each one of these plays, which include Henry V and Richard III, ______" (0fe5ce68); "the toxins the organism uses to protect itself from predation actually ______" (1c65db8f). The intervener's verb agrees with the attractor, so the wrong number sounds right twice.
5. **Plural heads behind singular nouns.** Half the band-7 R1 keys are plural (6 of 12 vs 2 of 7): "The trailblazing accomplishments of Goldin, winner of the 2023 Nobel Prize" (b32eab9f, five singular nouns before the blank).
6. **Heads that are not the nearest plausible subject.** "the shape of each statue’s ears, like the shape of each person’s ears, ______" (8a9d2f4e) puts a plural noun right before the blank twice; "each one of a ghazal’s couplets, while adhering to" runs 22 words; "So shrewd an observer is Shōnagon" opens an inverted frame before "her book’s musings ... ______".
7. **R3 keys whose subject is a property, not the thing.** "Compared to that of alumina glass," needs "silica glass’s atomic arrangement", and the distractors start with "silica glass", the noun the opener seems to describe (2dd1b8bf); likewise "the HHI score of a less concentrated market" (fced396a) and "findings from a 2022 study suggested" after "Supported by biochemical analyses" (8b017d4e). 3 of 5 band-7 R3 keys work this way against 2 of 11 at band 6.
8. **Pronouns before or far from their antecedent.** "With ______ eight panels of text stitched together" resolves to "the poems" 16 words later (0bcb4417); "In ______ place is a far more personal subject" points back 22 words to "the types", past a singular sculpture and artist (18382e67).
9. **Apostrophes in two slots with a generic plural.** "variables that characterize objects’ movement" (2784cbaf); "rock’s and rap’s chorus-to-verse ratios" (4c335aea, individual possession).

## 4. Distractor recipes at band 7

Share of items carrying at least one distractor with the recipe (instances in brackets).

| Recipe | Band 5 | Band 6 | Band 7 |
|---|---|---|---|
| Wrong number verb (R1) | 40% (30) | 24% (19) | 41% (35) |
| **Finite where a nonfinite is needed (second main verb, or comma splice)** | 0 | 10% (8) | **34% (33)** |
| **Punctuation also wrong in the option** | 0 | 0 | **16% (8)** |
| Nonfinite where a finite verb is needed | 4% (3) | 17% (11) | 6% (2) |
| Dangling modifier, any recipe (R3) | 32% (24) | 38% (33) | 16% (15) |
| of which wrong noun as subject (W) | 71% of R3 tags | 55% | 60% |
| of which expletive opener (E) | 0 | 9% | 13% |
| Pronoun: wrong number, contraction, demonstrative | 12% (9) | 17% (17) | 6% (6) |
| Apostrophe grid | 8% (6) | 0 | 6% (6) |
| Tense | 4% (3) | 0 | 0 |

- **Dominant at band 7**: wrong number (all 12 R1 items, three wrong-number forms each) and finite-for-nonfinite (11 items). Together they cover 23 of 32 items.
- **Only at band 7**: finite verb + comma variants of the same option (`N, V-s` beside `N V-s`); finite forms after an absolute-phrase noun (comma splice); the "that of" comparison where the wrong subject is the thing instead of its property.
- **How the hardest distractor is built:**
  - R2_interrupter: the simple past or present of the same verb (`searched`, `examined`, `dates`), which makes subject + verb a complete, sensible clause up to the downstream verb; with punctuation, the comma + finite form (`Serra, intends`).
  - R1: the form agreeing with the nearest noun, which is also the number of the intervener's own verb (`include`, `seem`, `uses`).
  - R3: the clause that keeps every fact and starts with the concrete noun one level off (`silica glass is at a significant disadvantage`).
  - R5: the wrong-number determiner matching the nearest noun (`its` beside "sculpture"); the contractions are easy rejects.

## 5. Band-7 writing recipe

Options for R1, R2, R5 and R6 are built by code (`spec/rw/README.md`, build order 1); R3 options are transforms of one canonical clause. "Where": **Plan** (batch planner), **Passage** (writer prompt), **Options** (option builder), **Judge** (acceptance check).

### Settings the code can control

| Knob | Band 6 | Band 7 | Where |
|---|---|---|---|
| Rule mix per 50 items | R3 19, R1 12, R2 10, R5 9 | R1 19, R2 17 (interrupter 14, absolute 3), R3 8, R5 3, R6 3, R4 0 | Plan |
| Deciding word after the blank | 28% of items have 15+ run words after the blank | 50%+ | Passage |
| Run length | median 27 | 30 to 54, median 34 | Passage |
| R1 attractors between head and blank | mean 1.7 | 2 to 5 | Passage, counted by Judge (parser) |
| R1 intervener with its own finite verb of the other number | 1 in 7 | about 40% (relative or reduced relative clause) | Passage |
| R1 head number | mostly singular | half plural, behind singular nouns | Plan |
| R1 head-to-blank distance | 1 to 27 | 5 to 22 (keep; it does not separate) | Passage |
| R1 nonfinite distractor | 2 of 7 | 2 of 12 (`animating`, `determining`) | Options |
| R2_interrupter verb distance | 10 | 9 to 21 words from blank to main verb | Passage |
| R2_interrupter commas around the phrase | yes | none in about 45% (restrictive participle) | Passage |
| R2_interrupter key form | -ing | -ing 6, having + participle 1, comma only 2 (of 9) | Options |
| Punctuation slot in verb-form options | never | about 55% of interrupter items | Options |
| Garden path | not required | each finite distractor forms a grammatical, sensible clause with the subject up to the downstream verb | Judge |
| R3 right subject | the agent or thing | "the Y of X", "X’s Y", "findings from X"; opener "Compared with that of" or a property claim | Passage + Options |
| R5 antecedent | 5 to 17 words, mostly before the pronoun | 15+ words, after the pronoun or a sentence back, with other-number nouns between | Passage |

### Per template

- **R2_interrupter** (new, 9). Subject (often "title Name" or "X’s noun") + blank + 8 to 20 words of phrase (object, prepositional phrases, an embedded dash or relative element) + the finite main verb + 5 to 15 more words. Options: key nonfinite; three finite forms of the same verb (past, present, present perfect or progressive), chosen so each one makes subject + verb a complete clause; in about half the items fold the comma into the options (`N, V-ing` key; `N, V-s`, `N V-s`, `N V-ed` distractors). Judge: with the key the sentence has exactly one finite main verb; with each distractor it has two.
- **R2_ing, absolute variant** (2). Complete clause + comma + possessive or article noun ("their design", "its vehicles") + blank + object. Options: `V-ing` or past participle key; `had V-ed`, `was V-ing`, `V-ed` (each a comma splice).
- **R1_lex** (5) and **R1_be** (2). Change from band 6: keep the distance, but fill the intervener with 2 to 5 nouns of the other number and, in about 40%, a relative clause whose own verb agrees with them; use plural heads half the time. A comparison intervener ("like the shape of each person’s ears") or an adjectival phrase with a title ("most known for her 1979 historical novel ...") also works. Options unchanged: wrong number in three tenses.
- **R1_quant_compound** (3). "each one of [plural], which [plural verb] ..., ______" or "each one of a [noun]’s [plurals], while adhering to ..."; compound with a contrast tag ("X and Y, not Z, ______"). Optionally one -ing distractor.
- **R1_rel_poss** (2). A possessor of the other number before the head ("A and B’s analysis", "her book’s musings"); an inverted "So [adjective] an observer is X that ..." frame is one band-7 setting.
- **R3_past_participle** (3), **R3_prep_gerund** (1), **R3_ing_participle** (1). Write the opener about a property, comparison or support ("Compared with that of ...", "Supported by analyses of ...", "Despite being cheap, versatile, and easy to produce") so the right subject is a noun phrase built on the obvious noun; distractors: the obvious noun as subject (W), an expletive (E), a possessive or nominalised version (P, N). Keep options 12 to 16 words and equally grammatical. Reserve these for about 15% of a band-7 batch.
- **R5_possessive_det** (2). Put the determiner before its antecedent ("With ______ eight panels ..., the poems") or 15+ words after it with a singular attractor between; options the 2 x 2 grid (`its`, `it’s`, `their`, `they’re`).
- **R6_grid / R6_individual** (1 / 1). Two slots, one a generic plural possessor ("objects’ movement"), or individual possession ("rock’s and rap’s").
- **No band-7 items**: R2_finite_main, R2_finite_second, R2_to_inf, R3_appositive, R4_present, R4_past_dated, R4_pastperf_future, R5_personal. Our hard set has items in five of these (R2_finite_main, R2_finite_second, R2_to_inf, R3_appositive, R4_pastperf_future); move those slots to R2_interrupter and R1.

## 6. Checks

| Check | How | Band 6 vs 7 | Reliability |
|---|---|---|---|
| Rule mix | Plan counts per batch | 45% vs 72% R1 + R2; 3% vs 28% interrupter | High for a batch |
| 15+ run words after the blank | Computed | 28% vs 53% | Moderate to high; the best single per-item signal |
| Interrupter distance and garden path | Computed distance 9+ words to the main verb; judge truncates the sentence just before that verb and confirms at least one finite distractor reads as a complete, sensible clause there | 9 of 9 band-7 interrupter items pass both | High within the template |
| Run of 30+ words | Computed | 45% vs 63% | Moderate |
| Cue outside a 6-word window | Computed from the anchor | 48% vs 69% | Moderate |
| R1 attractors 2+ and an intervener verb of the other number | Parser (head, number, embedded verbs) | 4 of 7 vs 8 of 12; 1 of 7 vs 5 of 12 | Moderate, small samples |
| Reasoning steps 4+ | Rubric in section 2 | 21% vs 38% | Moderate, batch level |
| R3 key subject is a property or "of" phrase | Judge labels the key's head noun vs the opener's obvious noun | 2 of 11 vs 3 of 5 | Weak (n = 5) |
| Local-window solve (agent) | A fast solver sees 6 words each side of the blank plus the options; a confident correct pick means band 6 or lower | follows from the cue row | Untested; calibrate on the 61 band 6 and 7 officials first |
| Do not use | Chars per word, long-word share, rarity, option length, key length rank, key overlap, R1 head-to-blank distance alone, R3 opener length | no gap or reversed | These do not separate 6 from 7 |

Applied to our 16 authored hard items: mean run 27 words with 12 after the blank (band 7: 33 and 18), no R2_interrupter item, and 5 of 16 items in templates with no band-7 officials (one of them R4, a rule with no item above band 5).

## Appendix: template assignment, bands 6 and 7

CB ids (`cb_id` in `material/rw/cb_api/form_structure_and_sense.json`), transcript id in brackets where one exists.

| Template | Band 6 | Band 7 |
|---|---|---|
| R1_be | c91ef0f0, ea0aa676 (3.2), ecba68b5 | 8a9d2f4e, dc645172 (3.3) |
| R1_lex | 329255db, 9994ae0d, f4fd123c (1.9) | 16740ab4, 1c65db8f, ae439895, b0fb36ad (3.20), b32eab9f |
| R1_quant_compound | none | 0fe5ce68 (3.6), 5fd86f4b, c7cb5186 |
| R1_rel_poss | ee4aa2aa | 863065c7 (3.23), f10b7ce4 (3.25) |
| R2_finite_main | a75d5984 (3.13) | none |
| R2_finite_second | 3daf126e, b74f676f (2.1) | none |
| R2_ing | a30567fd (2.9) | 81f09e07, c88ba1b7 |
| R2_interrupter | 61160f0a (3.9) | 1a61e2ae, 3a1239d2, 505054e3, 9127635a, a2816c7f, aa443c4b, c9a677e9, d222f7d9, f768090a |
| R2_to_inf | 512f0ac9 (3.19) | none |
| R3_appositive | 2b6e1c06, 5b8f9cf2 (3.7), e060dd6b | none |
| R3_ing_participle | 9df6da04 (3.14), dab8b8ee (3.5) | 2bca654a (3.21) |
| R3_past_participle | 772835db, b369d54c, f0864217 (3.1) | 2dd1b8bf, 8b017d4e (3.27), fced396a (3.26) |
| R3_prep_gerund | 188f7e3c (3.18), d2b81427 (3.17), dfbf5d33 (3.15) | 37e5c794 (3.16) |
| R5_personal | 908a76b8, 99dedf36 | none |
| R5_possessive_det | 2cb1ee22, 3bceeb93 (3.4), 872a002e (3.22) | 0bcb4417 (2.6), 18382e67 |
| R6_grid | none | 2784cbaf (3.24) |
| R6_individual | none | 4c335aea (3.28) |
