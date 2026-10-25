# Text Structure and Purpose: what makes a band-7 item

Source: every Text Structure and Purpose item in `material/rw/cb_api/text_structure_and_purpose.json` with band 5, 6 or 7 (21, 23 and 19 items). All 19 band-7 and all 23 band-6 items were read with CB's rationale. Measures come from Python over the CB text; template, subtype, key parts, near misses and distractor recipes are hand annotations made while reading (listed per item in section 1). Gaps are band 6 against band 7 with AUC (chance that a random band-7 item scores higher; 0.50 is no separation) and a permutation p value. With about 20 items per band, treat p above 0.10 as "no reliable difference". Note: the CB API text drops most underline tags, so the underlined span was read from the rationale.

## 1. Counts

| | Band 5 | Band 6 | Band 7 |
|---|---|---|---|
| Items | 21 (all CB medium) | 23 (all CB hard) | 19 (all CB hard) |
| Main purpose | 3 | 10 | 3 |
| Overall structure | 10 | 2 | 4 |
| Function of a part (incl. "function of the third sentence") | 8 | 11 | 12 |
| Literary excerpts | | 8 (35%) | 4 (21%) |
| Already in our transcript set | 10 | 7 | 9 |

Template mix (our codes from `satbank/rw/text_structure_and_purpose__a.json` (S) and `__b.json` (P, F); new names where none fit):

| Template | Band 6 | Band 7 |
|---|---|---|
| P_lit (literary feeling, trait or situation) | 4 | 1 |
| P_view (view, then challenge or caution) | 2 | 1 |
| P_profile | 2 | 0 |
| P_study | 1 | 1 |
| new P_two_approaches (two ways of doing one thing) | 1 | 0 |
| F_lit (literary detail or image) | 4 | 1 |
| F_setup (the span sets up what the rest of the text does with it) | 2 | 4 |
| new F_reason (the span is the consideration behind a conclusion or decision stated elsewhere) | 2 | 2 |
| F_example | 2 | 2 |
| F_qualify | 0 | 2 |
| F_method | 1 | 0 |
| new F_implication (the span draws a practical implication from a finding) | 0 | 1 |
| S6_field_distinction | 0 | 1 |
| S15_phenomenon_refute_two_third | 0 | 1 |
| S16_finding_pattern_exception | 1 | 0 |
| new S17_method_two_approaches (method, two approaches, relative advantage of each) | 0 | 1 |
| new S18_question_hypothesis_conflict (open question, a team's hypothesis, an observation that conflicts with it) | 0 | 1 |
| new S19_observation_test_implication (unexpected observation, an effort to explain it, an implication) | 1 | 0 |

Per-item assignment:
- Band 7: F_setup 1f2d6173, 6bc0ba75, a2f64e58, df45f0eb; F_reason 153aaae2, de059199; F_example 2e744883, 9b01bcf4; F_qualify 0f2933b9 (Shakespeare), df46a2ee (Conrad); F_lit cf46f239 (Melville); F_implication c762ca58; S6 6d44060a; S15 6ae393f7; S17 70e6af39; S18 f61c22f3; P_study 82cb7dda; P_lit b0f7541b (Melville); P_view c61a7c4a.
- Band 6: P_lit 03c9f327 (Brontë), 0a04cac5 (Austen), 5f56fdec (McClellan), ad4f7362 (Dryden); P_view 0b5ecf0e, a1d2c4d0; P_profile 65406d2c, d9915c15; P_study d4732483; P_two_approaches 975b0602; F_lit 37c481f8 (Heng), 39857700 (Wharton), 5336f2e4 (Hurston), 570970cd (Ohiyesa); F_setup ca50de52, e818241b; F_reason 662ebff2, 93ce86d0; F_example ac9a3a26, cce2f8dc; F_method 3e6ad72d; S16 4ed09415; S19 8af926b1.

Band 7 is a function-of-a-part skill: 12 of 19 items, against 11 of 23 at band 6, while main purpose falls from 10 to 3. Templates with band-7 items: F_setup, F_reason, F_example, F_qualify, F_lit, F_implication, S6, S15, S17, S18, P_study, P_lit, P_view. Templates with none: P_profile, P_effort, P_argue, F_term, F_limit, F_method, F_answer, and structure S1 to S5, S7 to S14, S16. Our transcripts drifted: 2.4 and 2.11 (filed medium) are now band 7, with 3.1, 3.3, 3.4, 3.10, 3.11, 3.12, 3.14; and 3.2, 3.13, 3.15 to 3.19 are band 6. Six of our 11 authored hard items list a band-7 model.

## 2. What separates 7 from 6, measured

Word rarity here is the share of lowercase passage words past rank 10,000 in `tools/data/freq.txt` (the same lookup as the Words in Context report).

| Signal | Band 5 | Band 6 | Band 7 | AUC | p | Separates? |
|---|---|---|---|---|---|---|
| Passage words | 83.8 | 83.6 | 91.3 | 0.63 | 0.14 | weak |
| Words per sentence | 32.8 | 27.1 | 33.8 | 0.63 | 0.15 | weak |
| Characters per word | 5.09 | 5.23 | 5.21 | 0.48 | 0.84 | no |
| Long-word rate | 12.8% | 14.1% | 15.0% | 0.54 | 0.65 | no |
| Passage words past rank 10,000 | 12.3% | 12.4% | 15.7% | 0.63 | 0.17 | weak |
| **Key length in words (mean)** | 19.9 | 16.1 | 22.3 | 0.75 | 0.003 | **yes** |
| Key length, median within subtype (purpose / structure / function) | 19 / 19.5 / 18 | 14.5 / 30 / 14 | 19 / 28 / 23 | | | yes for function and purpose; structure flat (2 band-6 items) |
| Mean option length in words | 19.9 | 17.1 | 22.2 | | | yes |
| Key length rank (1 = longest) | 2.43 | 2.83 | 2.68 | 0.47 | 0.78 | no |
| Key is the longest option | 33% | 9% | 21% | 0.56 | 0.37 | no |
| Key content words found in passage | 24% | 27% | 27% | 0.50 | 0.99 | no |
| Distractor content words found in passage | 22% | 28% | 27% | 0.52 | 0.82 | no |
| Key carries a hedge (some, may, helps, certain, likely, suggests) | 3/21 | 7/23 | 8/19 | | | no |
| Distractors with an absolute (all, only, primary, main, never) | 3/63 | 4/69 | 5/57 | | | no |
| Parts the key asserts (mean; the step count) | | 1.74 | 2.11 | 0.64 | 0.12 | weak |
| Keys with three parts | | 3/23 | 6/19 | | | weak |
| Partly right distractors per item | | 1.17 | 1.53 | 0.61 | 0.21 | weak |
| **Items with a distractor right in its first part and wrong only later** | | 3/23 | 7/19 | 0.63 | 0.05 | **yes** |
| Distractors of that kind (total) | | 4 | 14 | | | yes |
| Literary items | | 8/23 | 4/19 | 0.43 | 0.49 | no (falls) |
| Clue direction, function items: the key depends on a sentence after the span | | 2/11 | 6/12 | | | yes |

Reasoning steps: the source report does not count steps; its section 6 says hard keys state "a dual purpose" or "a precise relation" and hard structure options have three moves. So the step count here is the number of separate claims the key makes that must each be checked (role of the span, what the text does with it, how that turns out). Band 7 averages 2.11 against 1.74.

What the numbers say:
1. **Longer, compound keys are the clearest signal.** Function keys run 23 words against 14 at band 6 and purpose keys 19 against 14.5; structure keys are long at both bands (28 and 30, from only 2 band-6 structure items). The options do not just get wordier: they carry a second clause about what the rest of the text does ("that the text goes on to suggest is a consequence of ..."). Length rank stays near chance, because every option grows.
2. **The distractors are right in their first half.** Seven band-7 items (14 distractors) have options that describe the span correctly and fail in a later clause; three band-6 items (4 distractors) do. This is the source report's "first move right, later move wrong" pattern, moved from structure items into function items.
3. **Band 5 also has long keys** (median 19), because it is structure-heavy (10 of 21). Key length separates band 7 from band 6 only within a subtype.
4. **The deciding sentence moves after the span.** In 6 of 12 band-7 function items the key depends on a sentence after the underline (the turn, the interpretation, the researchers' response); in band 6, 2 of 11.
5. **Not signals:** characters per word, long-word rate, passage overlap of key or distractors, hedges, absolutes, key length rank. Passage length, sentence length and rarity lean upward at band 7 (91 against 84 words; 15.7% against 12.4% rare words) but not reliably.
6. **Literary passages do not make band 7.** The literary share falls (35% to 21%), but the four band-7 literary items all use pre-1910 or archaic prose (Shakespeare 1611, Melville 1855 and 1857, Conrad 1907); band-6 literary items include a 2023 novel and Hurston.

### Per-item annotations

Hand annotations behind the counts above, for audit. Distractor recipes are in option order, key left out.

| cb_id | band | template | key parts | partly right | first part right, later wrong | distractor recipes |
|---|---|---|---|---|---|---|
| 2e744883 | 7 | F_example | 1 | 1 | 0 | PART, INV, INV |
| 9b01bcf4 | 7 | F_example | 1 | 1 | 0 | INV, REV, BROAD |
| c762ca58 | 7 | F_implication | 2 | 2 | 1 | SWAP, BROAD, INV |
| cf46f239 | 7 | F_lit | 2 | 1 | 0 | INV, INV, LIT |
| 0f2933b9 | 7 | F_qualify | 2 | 2 | 0 | PART, STANCE, BROAD |
| df46a2ee | 7 | F_qualify | 1 | 0 | 0 | INV, REL, LIT |
| 153aaae2 | 7 | F_reason | 2 | 0 | 0 | INV, INV, INV |
| de059199 | 7 | F_reason | 3 | 2 | 0 | STANCE, SWAP, PART |
| 1f2d6173 | 7 | F_setup | 2 | 3 | 3 | INV, INV, INV |
| 6bc0ba75 | 7 | F_setup | 2 | 0 | 0 | INV, INV, REL |
| a2f64e58 | 7 | F_setup | 3 | 3 | 3 | INV, INV, INV |
| df45f0eb | 7 | F_setup | 3 | 3 | 2 | INV, INV, REL |
| b0f7541b | 7 | P_lit | 1 | 2 | 0 | BROAD, INV, PART |
| 82cb7dda | 7 | P_study | 2 | 2 | 0 | INV, LIT, SWAP |
| c61a7c4a | 7 | P_view | 2 | 2 | 0 | STANCE, STANCE, SWAP |
| 6ae393f7 | 7 | S15_phenomenon_refute_two_third | 3 | 2 | 2 | INV, INV, REV |
| 70e6af39 | 7 | S17_method_two_approaches | 3 | 1 | 1 | INV, INV, STANCE |
| f61c22f3 | 7 | S18_question_hypothesis_conflict | 3 | 2 | 2 | INV, INV, REV |
| 6d44060a | 7 | S6_field_distinction | 2 | 0 | 0 | BROAD, INV, INV |
| ac9a3a26 | 6 | F_example | 2 | 1 | 0 | BROAD, REV, PART |
| cce2f8dc | 6 | F_example | 2 | 0 | 0 | REV, INV, INV |
| 37c481f8 | 6 | F_lit | 1 | 2 | 0 | INV, SWAP, PART |
| 39857700 | 6 | F_lit | 2 | 2 | 0 | PART, REV, REL |
| 5336f2e4 | 6 | F_lit | 1 | 2 | 0 | PART, PART, INV |
| 570970cd | 6 | F_lit | 2 | 1 | 0 | SWAP, INV, INV |
| 3e6ad72d | 6 | F_method | 1 | 1 | 0 | REL, REL, INV |
| 662ebff2 | 6 | F_reason | 3 | 1 | 1 | INV, BROAD, INV |
| 93ce86d0 | 6 | F_reason | 2 | 0 | 0 | STANCE, INV, REL |
| ca50de52 | 6 | F_setup | 1 | 1 | 0 | SWAP, INV, SWAP |
| e818241b | 6 | F_setup | 2 | 1 | 0 | SWAP, REL, INV |
| 03c9f327 | 6 | P_lit | 2 | 2 | 1 | INV, PART, BROAD |
| 0a04cac5 | 6 | P_lit | 2 | 0 | 0 | INV, INV, REV |
| 5f56fdec | 6 | P_lit | 1 | 2 | 0 | BROAD, PART, REV |
| ad4f7362 | 6 | P_lit | 1 | 2 | 0 | INV, PART, LIT |
| 65406d2c | 6 | P_profile | 2 | 2 | 0 | BROAD, INV, BROAD |
| d9915c15 | 6 | P_profile | 1 | 0 | 0 | INV, INV, PART |
| d4732483 | 6 | P_study | 2 | 1 | 0 | INV, REV, STANCE |
| 975b0602 | 6 | P_two_approaches | 1 | 0 | 0 | INV, STANCE, INV |
| 0b5ecf0e | 6 | P_view | 1 | 1 | 0 | PART, STANCE, INV |
| a1d2c4d0 | 6 | P_view | 2 | 1 | 0 | STANCE, SWAP, INV |
| 4ed09415 | 6 | S16_finding_pattern_exception | 3 | 3 | 2 | INV, INV, STANCE |
| 8af926b1 | 6 | S19_observation_test_implication | 3 | 1 | 0 | INV, INV, INV |

## 3. What separates 7 from 6, read

1. **The span is a means, not a claim.** Band-7 underlines pick out a consideration, a set-up or a qualification, and the key names its relation to a claim elsewhere: "identifies a consideration that factored into an interpretation" (153aaae2), "describe a consideration that led the researchers to employ an alternative approach" (de059199). Band-6 function keys name the span's own content ("explain part of the methodology", "illustrate the changeable nature of the fishing grounds").
2. **Three-layer function options.** a2f64e58: the key "discusses a characteristic shared by certain animals" in order to "explain why researchers raised a possibility", one "not to be supported by data described later". Every distractor opens with a true first layer (a pattern, a similarity, a trait shared by certain animals) and invents the later layers.
3. **The rest of the text reverses the span.** In a2f64e58 the underlined trait sets up a hypothesis the data then refute; in df45f0eb the opening conflict is later explained by "a complicating factor in the data"; in 1f2d6173 the scholarly focus "obscures the ideological diversity". The student must read past the span to the turn and fold the turn into the answer.
4. **Abstract key, concrete passage.** 6d44060a summarizes a passage on Plato, Barnes and moral motive as "some works in that field are more comprehensive than others"; 70e6af39 summarizes canting and cap as "two approaches ... and then addresses the relative advantage of each". The key shares almost no words with the passage, the same as at band 6, but the abstraction gap is larger.
5. **Archaic literary text with a self-qualifying span.** 0f2933b9 underlines "I might be some allay—or I o'erween [presume] to think so"; the key is "one benefit his presence may afford ... is merely speculative". df46a2ee underlines "a soft kind of rock" after "steady like a rock" (key: "It qualifies an earlier description"). cf46f239 makes the student infer, from a long Melville sentence, that Israel's mildness explains why he was cheated.
6. **Hedged dual purpose.** c61a7c4a: "discusses the study ... to illustrate why caution is needed". The distractors keep the study and change the purpose (critique methods, solve a problem, findings often misunderstood).

How band 6 is hard instead: a literary purpose with a two-part feeling ("a contrast between Jane's outward calmness and internal restlessness"), a local-link function ("illustrates an idea that is introduced in the previous sentence") where the trap describes the neighbor sentence, and purpose items with dense content (silversword alliance, sartorial practice).

## 4. Distractor recipes at band 7

Recipe tags from `spec/rw/text_structure_and_purpose.md` section 5. Each distractor has one primary tag; a compound option whose first part is right and whose later part is invented is tagged INV.

| Recipe | Band 6 (69 distractors) | Band 7 (57) |
|---|---|---|
| Off-text invention (INV) | 29 (42%) | 30 (53%) |
| Partial (PART) | 10 (14%) | 4 (7%) |
| Overreach (BROAD) | 6 | 5 |
| Wrong stance (STANCE) | 6 | 5 |
| Misattribution (SWAP) | 6 | 4 |
| Reversal (REV) | 6 | 3 |
| Wrong relation (REL) | 5 | 3 |
| Word hook (LIT) | 1 | 3 |

- **INV dominates, but it moves inside the option.** At band 6 an invented distractor is usually wholly off ("To call for additional research"). At band 7, 14 of the 30 INV distractors start with the correct role of the span and invent only the second or third clause ("a trend in scholarship ... that the text claims has been reevaluated by researchers"). That is the hardest distractor at band 7.
- **PART falls.** Band 6 traps students with the neighbor sentence's job (39857700 A, 5336f2e4 A and B, e818241b A). Band 7 rarely does; its spans are relational, so "the neighbor's job" is already in every option.
- **Band 7 only: the three-option first-half match.** In 1f2d6173 and a2f64e58 all three distractors share the key's first half.
- **Structure distractors at band 7** keep moves 1 and 2 and break move 3 by stance or reversal (6ae393f7 D "a persuasive account ... has yet to be put forward"; f61c22f3 A "a finding that led the team to refine the hypothesis"; f61c22f3 D "data ... that validate the hypothesis").
- Verbs that are never keyed stay never keyed (compare, contrast, critique, concede, urge, call for).

## 5. Band-7 writing recipe

Settings common to every band-7 template:
- Subtype: function of a part (about two thirds of band 7), then structure; main purpose only with a dual or hedged purpose.
- Passage: 85 to 110 words, two to four long sentences (about 30 words each), academic register, with a turn (however, but, yet, instead) after the span.
- The span is not the main claim. Underline a consideration, a set-up, a qualification, a number or an implication whose job depends on a later sentence.
- Key: 20 to 30 words for function and purpose items (structure keys are already this long at band 6), two or three clauses: the span's role, then what the text does with it ("that the text goes on to ...", "in order to explain why ...", "that, according to the text, ..."). Hedge it where the passage hedges.
- Distractors: build at least two by keeping the key's first clause (or a true paraphrase of it) and inventing the later clause; the third can be wholly invented or a stance flip.

Per template (what to change from band 6):
- **F_setup.** Band 6: the span is a question or a problem, and the key says it sets up what follows. Band 7: the span is a view, trait or finding that a later sentence overturns, and the key carries both halves (1f2d6173, a2f64e58, df45f0eb). Distractors keep half one and change the overturn (reevaluated by researchers; a theory about exceptions; a hypothesis about origins).
- **F_reason (new).** The span is the reason behind a decision or interpretation stated in another sentence ("a period coinciding with extremely arid conditions"; "would run counter to the ecological promise"). Key: "identifies a consideration that ... led to / factored into ...". Distractors: a causal story the text never tells ("explain why production ... abruptly ceased"), or the neighbor sentence's job ("illustrate how the researchers adapted ...").
- **F_example.** Underline a number or a single case whose job is to show extent or position, not content ("more than 7,000 in all" underscores extent; Cruse's criticism of Black nationalists "helps explain Cruse's position"). Distractors: the topic of the rest of the sentence (PART), a controversy or reputation the text does not claim.
- **F_qualify.** Archaic or literary prose where the span limits an earlier description ("a soft kind of rock"; "or I o'erween to think so"). Key short and abstract ("qualifies an earlier description") or names the qualification ("merely speculative"). Distractors: invented inner states, a literalized word hook ("a private opinion").
- **F_lit.** Use pre-1910 prose with a long periodic sentence and require an inference from the span to an outcome elsewhere (Israel's mildness explains why he was cheated). Band-6 F_lit asks what the image shows directly.
- **F_implication (new).** The span is the closing "therefore, X should ..." sentence; key: it shows a finding "has practical implications ... particularly relevant for" one class. Distractors: the right recommendation for the wrong class ("companies that value product quality"), a call for more research.
- **Structure (S6, S15, S17, S18).** Three moves stated abstractly, where move 3 carries a stance (refuted, regarded as plausible, conflicts with the hypothesis, relative advantage). Distractors keep moves 1 and 2 and change move 3's stance or outcome.
- **P_study, P_view, P_lit.** Dual purpose with a hedge ("summarizes a finding suggesting that some mechanisms ... resemble"; "to illustrate why caution is needed"), or a very short abstract key for an archaic narrative ("It presents an account of a misunderstanding"). Distractors: the right study with the wrong purpose; a literalized feeling.
- **No band-7 items:** P_profile, P_effort, P_argue, F_term, F_limit, F_method, F_answer, and structure templates S1 to S5, S7 to S14, S16, S19. Use them for bands 5 and 6.

## 6. Checks

Automatic:

1. **Key length within subtype.** Function key at least 18 words: 8 of 12 band-7 function items, 2 of 11 band-6. Purpose key at least 16 words: 2 of 3 band 7, 3 of 10 band 6. Structure keys are 22 words or more at both bands, so length does not help there. Over all subtypes, a key of 20 words or more holds for 12 of 19 band-7 items, 5 of 23 band-6 items and 9 of 21 band-5 items (band 5 is structure-heavy). Moderate.
2. **Mean option length at least 20 words.** 12 of 19 band 7, 5 of 23 band 6. Same caveat about band 5.
3. **Compound clause marker in the key** (the text goes on, later in the text, in order to, according to the text, presented in the text, that follows, previous sentence). 6 of 19 band-7 keys, 3 of 23 band-6 keys. Weak alone; use as a tie-breaker.

Agent-run:

4. **First-half match.** An agent splits each option into clauses and marks each clause true or false against the passage. A band-7 draft needs at least two distractors whose first clause is true and a later clause false. Band 7: 7 of 19 items had at least one such distractor and 14 distractors in all; band 6: 3 of 23 and 4. Reliable as a positive signal; this is the main gate.
5. **Key parts.** The agent counts the separate claims in the key; require at least 2, prefer 3 (band 7: 6 of 19 keys have 3 parts, band 6: 3 of 23).
6. **Span role.** The agent states whether the span is the main claim or a means (consideration, set-up, qualification, implication). Band 7 drafts should be "means".

Do not gate on: characters per word, long-word rate, key length rank, key or distractor overlap with the passage, hedges or absolutes counts, literary versus informational. None separated band 7 from band 6.
