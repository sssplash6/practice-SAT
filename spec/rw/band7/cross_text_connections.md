# Cross-Text Connections: what makes a band-7 item

Source: every Cross-Text Connections item in `material/rw/cb_api/cross_text_connections.json` with band 5, 6 or 7 (10, 14 and 13 items). All 13 band-7 and all 14 band-6 items were read with CB's rationale. Measures come from Python over the CB text (both texts counted together, the "Text 1" and "Text 2" labels removed); template, reasoning steps, partly right distractors and recipes are hand annotations made while reading (listed per item in section 1). Gaps are band 6 against band 7 with AUC (chance that a random band-7 item scores higher; 0.50 is no separation) and a permutation p value. **With 13 and 14 items, only very large gaps reach p below 0.05, and every number below has wide error; the reading in section 3 carries more weight than usual.**

## 1. Counts

| | Band 5 | Band 6 | Band 7 |
|---|---|---|---|
| Items | 10 (all CB medium) | 14 (all CB hard) | 13 (all CB hard) |
| Respond / characterize / regard / say about / describe | 6 | 12 | 8 |
| Agree with which statement | 2 | 1 | 3 |
| Difference, relate, and new stems | 2 | 1 | 2 |
| Text 1 is the speaker | | 1 | 3 |
| Pair includes a literary excerpt | 0 | 0 | 1 |
| Already in our transcript set | 6 | 10 | 6 |

Template mix (our codes from `satbank/rw/cross_text_connections.json`; three new names where none fit):

| Template | Band 6 | Band 7 |
|---|---|---|
| S1_refute_data | 2 | 1 |
| S1_framework_critique | 3 | 1 |
| S1_limit_degree | 2 | 0 |
| S1_second_factor | 1 | 2 |
| S1_concede_rebut | 2 | 1 |
| S1_alt_explanation | 1 | 0 |
| S1_solution | 0 | 3 |
| S1_case_fits_frame (Text 1 speaking) | 1 | 1 |
| S2_shared_premise | 1 | 0 |
| S2_joint_inference | 0 | 1 |
| S3_difference | 1 | 0 |
| new apply_model (stem: explain Text 2's results "using the model presented in Text 1") | 0 | 1 |
| new disagree_question (stem: the two parties "would most likely disagree about the answer to which question"; options are questions) | 0 | 1 |
| new lit_reading (Text 1 a literary excerpt, Text 2 a critical reading; which statement about the excerpt would Text 2's author accept) | 0 | 1 |

Per-item assignment:
- Band 7: S1_solution 4b4ab04e (mycoprotein; Text 1 speaks), f3c45b4f (Sterkfontein dating), f7c02e89 (film credits; Text 1 speaks); S1_second_factor 592f94c2 (public art), e4e2aeb3 (Morrison and Ellison); S1_refute_data 3cfbf077 (K2-18 b); S1_framework_critique 96f3accc (Arrival of the Train); S1_concede_rebut d0198544 (El Arenal chicken); S1_case_fits_frame 03080769 (Moore; Text 1 speaks); S2_joint_inference a87c3925 (umami); apply_model 1917ba9a (protogynous fish); disagree_question 5e4e082c (molybdenum); lit_reading 9828ab3d (Howards End).
- Band 6: S1_refute_data 84dbd633, d72b325e; S1_framework_critique 6977d22b, c885c38b, d6c77ae5; S1_limit_degree 27d9bb69, 5e101c70; S1_second_factor 12d81fc1; S1_concede_rebut 105ea6de, 6a1dc7c5; S1_alt_explanation 35e21b06; S1_case_fits_frame 8de51658; S2_shared_premise c106b9f7; S3_difference 17bf10de.

Templates with no band-7 items: S1_counterexample, S1_rival_hypothesis, S1_limit_degree, S1_alt_explanation, S2_shared_premise, S2_hidden_assumption, S3_difference, S4_relate. Band 7 adds solution mapping (3 of 13) and three new formats that ask the student to combine the texts into a claim neither states. Our transcripts drifted: 2.6, 3.4, 3.6, 3.7, 3.8, 3.13 are band 7; 1.13 (filed easy), 2.2, 2.7, 2.8, 3.2, 3.5, 3.9, 3.10, 3.12, 3.14 are band 6. Four of our 10 authored hard items list a band-7 model.

## 2. What separates 7 from 6, measured

| Signal | Band 5 | Band 6 | Band 7 | AUC | p | Separates? |
|---|---|---|---|---|---|---|
| Passage words, both texts | 136.3 | 131.4 | 140.7 | 0.74 | 0.03 | yes |
| Passages of 140+ words | 6/10 | 6/14 | 8/13 | | | weak |
| Words per sentence | 22.5 | 25.7 | 24.3 | 0.38 | 0.33 | no |
| Characters per word | 5.07 | 5.45 | 5.28 | 0.36 | 0.23 | no (if anything lower) |
| Long-word rate | 13.0% | 17.5% | 16.4% | 0.47 | 0.78 | no |
| Passage words past rank 10,000 (`freq.txt`) | 13.3% | 16.0% | 17.1% | 0.54 | 0.77 | no |
| **Key length in words** | 19.8 | 18.4 | 27.0 | 0.83 | 0.003 | **yes** |
| Keys of 25+ words | 2/10 | 2/14 | 5/13 | | | yes |
| Mean option length in words | 20.6 | 19.7 | 26.8 | | | yes |
| Key length rank (1 = longest) | 2.40 | 3.00 | 2.69 | 0.42 | 0.47 | no |
| Key content words found in passage | 45% | 43% | 43% | 0.48 | 0.90 | no |
| Distractor content words found in passage | 50% | 44% | 51% | 0.68 | 0.14 | weak |
| Key carries a hedge | 2/10 | 5/14 | 4/13 | | | no |
| Options with a "but / whereas / while" two-part shell | 8 | 17 | 6 | | | no (falls) |
| **Reasoning steps** (report section 6 count) | | 1.93 | 2.62 | 0.80 | 0.002 | **yes** |
| Three-step items | | 1/14 | 8/13 | | | yes |
| **Partly right distractors per item** | | 0.93 | 1.92 | 0.82 | 0.002 | **yes** |
| Distractors that twist a passage detail (D3) per item | | 0.29 | 1.08 | 0.79 | 0.006 | yes |
| Key states a conclusion neither text states (synthesis) | | 2/14 | 7/13 | 0.70 | 0.05 | yes |
| Text 1 is the speaker | | 1/14 | 3/13 | 0.58 | 0.34 | no |
| New stem format | | 0/14 | 3/13 | 0.62 | 0.10 | weak |

Clue distance in the usual sense does not apply (the answer always needs both texts); its analogue here is whether the key needs a fact neither text states, the synthesis row above.

Reasoning steps follow `spec/rw/cross_text_connections.md` section 6: one step negates or confirms the target; two steps find what the speaker grants or rejects and on what grounds; three steps derive a fact neither text states (combine a value or mechanism from one text with the situation in the other).

What the numbers say:
1. **Band 7 adds a step.** 8 of 13 band-7 items need three steps against 1 of 14 at band 6, and 7 of 13 keys state a conclusion neither text states (K2-18 b is unlikely to hold liquid water; the 2007 broths probably lacked the dipeptides; a cheaper substrate would help cut deforestation). Band-6 keys are mostly a stance toward the target (questionable, overly optimistic, not supported).
2. **Distractors get closer by reusing details.** Partly right distractors double (0.93 to 1.92 per item), almost all of the rise is twisted details (D3: 4 at band 6, 14 at band 7), and distractors reuse more passage words (51% against 44%).
3. **Keys and options are longer**, about 9 words, because the key carries the derived claim and its basis. Length rank does not move.
4. **The two-part "concede but rebut" shell is a band-6 device.** Two-clause options fall from 17 to 6; concede-rebut and half-right (D7) items are as common or more common at band 6.
5. **Register does not separate.** Characters per word, long words and rare words are flat or slightly lower at band 7; passage length rises a little (141 against 131 words) because the texts carry a mechanism and a number.

### Per-item annotations

Hand annotations behind the counts above, for audit. Distractor recipes are in option order, key left out.

| cb_id | band | template | steps | partly right | synthesis key | Text 1 speaks | distractor recipes |
|---|---|---|---|---|---|---|---|
| 03080769 | 7 | S1_case_fits_frame | 3 | 2 | yes | yes | D2, D3, D3 |
| d0198544 | 7 | S1_concede_rebut | 3 | 2 | - | - | D7, D1, D3 |
| 96f3accc | 7 | S1_framework_critique | 2 | 3 | - | - | D3, D7, D7 |
| 3cfbf077 | 7 | S1_refute_data | 3 | 2 | yes | - | D2, D1, D7 |
| 592f94c2 | 7 | S1_second_factor | 2 | 1 | - | - | D5, D2, D8 |
| e4e2aeb3 | 7 | S1_second_factor | 2 | 2 | - | - | D8, D2, D3 |
| 4b4ab04e | 7 | S1_solution | 3 | 2 | yes | yes | D3, D3, D1 |
| f3c45b4f | 7 | S1_solution | 2 | 2 | - | - | D3, D2, D3 |
| f7c02e89 | 7 | S1_solution | 2 | 1 | - | yes | D1, D3, D2 |
| a87c3925 | 7 | S2_joint_inference | 3 | 2 | yes | - | D1, D3, D3 |
| 1917ba9a | 7 | new_apply_model | 3 | 2 | yes | - | D7, D2, D6 |
| 5e4e082c | 7 | new_disagree_question | 3 | 2 | yes | - | D1, D8, D3 |
| 9828ab3d | 7 | new_lit_reading | 3 | 2 | yes | - | D2, D2, D3 |
| 35e21b06 | 6 | S1_alt_explanation | 2 | 1 | - | - | D3, D2, D6 |
| 8de51658 | 6 | S1_case_fits_frame | 3 | 0 | yes | yes | D1, D2, D9 |
| 105ea6de | 6 | S1_concede_rebut | 2 | 2 | - | - | D7, D7, D2 |
| 6a1dc7c5 | 6 | S1_concede_rebut | 2 | 3 | - | - | D7, D7, D7 |
| 6977d22b | 6 | S1_framework_critique | 2 | 0 | - | - | D1, D3, D2 |
| c885c38b | 6 | S1_framework_critique | 2 | 1 | - | - | D2, D2, D8 |
| d6c77ae5 | 6 | S1_framework_critique | 2 | 0 | - | - | D6, D6, D6 |
| 27d9bb69 | 6 | S1_limit_degree | 2 | 1 | - | - | D5, D1, D2 |
| 5e101c70 | 6 | S1_limit_degree | 1 | 0 | - | - | D2, D8, D2 |
| 84dbd633 | 6 | S1_refute_data | 2 | 1 | - | - | D7, D1, D2 |
| d72b325e | 6 | S1_refute_data | 1 | 1 | - | - | D10, D2, D5 |
| 12d81fc1 | 6 | S1_second_factor | 2 | 0 | - | - | D2, D1, D1 |
| c106b9f7 | 6 | S2_shared_premise | 2 | 1 | yes | - | D2, D3, D1 |
| 17bf10de | 6 | S3_difference | 2 | 2 | - | - | D7, D7, D3 |

## 3. What separates 7 from 6, read

1. **A number or mechanism in one text decides the other.** 3cfbf077: Text 1 puts K2-18 b "right on the inner edge" of a zone starting at "about 1 astronomical unit"; Text 2 moves the inner edge "as far out as 3.85 AU". Neither text says K2-18 b is now too close; the key does. Two distractors reverse the direction (temperatures "likely too high"; planets "too far from the stars").
2. **Apply a model to an experiment.** 1917ba9a asks which choice "best explains the difference in the outcomes of the two tanks", "using the model presented in Text 1". Each option is about 55 words and pairs the two tanks with "whereas"; one distractor gets the outcome right without using the model ("could not reproduce regardless of their size").
3. **Name the crux.** 5e4e082c asks which question the two teams "would most likely disagree about". The trap C is a question both would answer the same way (both accept oxidative weathering); the key B isolates timing. The student must sort shared premises from the disputed one.
4. **Text 1 speaks, and must be extended.** 4b4ab04e: Text 1's author never mentions deforestation, but Text 1's "cheaper substrate" plus Text 2's beef-replacement study yields the key. 03080769: the author of Text 1 answers external world skeptics by reporting what Moore "would assert".
5. **Solution mapping.** f3c45b4f and f7c02e89 pair a problem with a method; the hardest distractor gets the method's detail wrong by one word ("applied to the fossils directly" where Text 2 says the breccia around them).
6. **A critical frame applied to a literary excerpt.** 9828ab3d pairs Forster's King's Cross passage with an essay on city against countryside; every option uses the essay's vocabulary (materialism, idealism, authentic connection), and two reverse which side King's Cross stands for.
7. **Abstract restatement of a second factor.** 592f94c2: the key says reactions "aren't exclusively the result of attributes inherent in the works themselves", a level above Text 2's "aren't effectively integrated within their surroundings".

How band 6 is hard instead: a concede-then-rebut response with two-part options (105ea6de, 6a1dc7c5), a stance label with a reason (As questionable, because ...; overly optimistic given ...), or a framework critique (no linear stages). The relation is partial, but the key does not leave the two texts' own claims.

## 4. Distractor recipes at band 7

Recipe codes from `spec/rw/cross_text_connections.md` section 5.

| Recipe | Band 6 (42 distractors) | Band 7 (39) |
|---|---|---|
| D3 twisted detail | 4 (10%) | 14 (36%) |
| D2 wrong side or reversal | 13 (31%) | 9 (23%) |
| D1 unaddressed add-on | 7 (17%) | 6 (15%) |
| D7 half right | 8 (19%) | 5 (13%) |
| D8 wrong target or dimension | 2 | 3 |
| D6 right verdict, wrong reason | 4 | 1 |
| D5 overstatement | 2 | 1 |
| D9, D10 (generic move, understatement) | 2 | 0 |

- **Twisted detail is the band-7 recipe.** It builds a claim from the passage's own nouns that neither text makes: "water consumption would remain static ... substitute mycoprotein for chicken and pork" (4b4ab04e A), "film historians tend to regard as naïve" (96f3accc B, from Text 2's "(naïve) before"), "applied to the fossils directly" (f3c45b4f D).
- **Direction reversals on a derived claim.** In 3cfbf077 and 9828ab3d the wrong-side distractors reverse the derived conclusion (too high instead of too low; materialism instead of idealism), so a student who skips the derivation cannot tell them from the key.
- **Band 7 only:** a distractor that is the right answer to a neighboring question (the shared-premise question in 5e4e082c C; the non-model explanation in 1917ba9a D).
- **Falling at band 7:** "As X, because Y" items where every distractor is a wrong reason (d6c77ae5), and the concede-rebut half-right shell.
- How the hardest distractor is built: take the key's derived claim, keep its vocabulary, and either reverse its direction or swap one detail for a neighboring one from the passage.

## 5. Band-7 writing recipe

Settings common to every band-7 template:
- Two texts of 65 to 75 words each (about 140 in all), academic but not denser than band 6; one text must carry a number, threshold or mechanism the other text's case can be checked against.
- The key states a consequence that follows from combining the texts and that neither text states, in 25 to 30 words, hedged to the speaker's commitment.
- Distractors: two twisted details (passage nouns in a claim neither text makes), one reversal of the derived claim. No add-on topics, no "conduct more research".
- Prefer Text 1 as the speaker in about a quarter of items: it forces the student to extend Text 1's position to a case it never mentions.

Per template (what to change from band 6):
- **S1_refute_data.** Band 6: Text 2's study finds no effect, key "not supported by the team's findings". Band 7: Text 2 changes a threshold or parameter, and the key applies the new value to the case named in Text 1 (3cfbf077).
- **S1_solution.** Problem in one text, method or practice in the other, often with Text 1 as speaker (f7c02e89, 4b4ab04e). For band 7 the solution must reach the other text's goal through an unstated link (cost to access to deforestation). Hardest distractor: the method with one detail moved.
- **S1_second_factor.** Key phrased one level more abstract than Text 2 ("aren't exclusively the result of attributes inherent in the works"). Distractors: overstatement ("unrelated to the unconventionality"), wrong target.
- **S1_framework_critique.** Use an agreement stem about the other text's description ("would most likely agree with which statement about the description ... in Text 1"); the key names the motive behind the description, the distractors are half-right pairs that start with "not based on evidence" or "a misconception" and add a wrong cause.
- **S1_concede_rebut.** Band 7 version: "same conclusion, better evidence" (d0198544). Keep the conclusion and swap the evidence; distractors object to a timeline or an assumption neither text raises.
- **S1_case_fits_frame (Text 1 speaking).** Text 1 states a general principle; Text 2 describes people who hold the opposite. Key reports how the principle answers them (03080769).
- **S2_joint_inference.** Two compatible experiments; key derives a fact about one experiment's materials from the other's finding (a87c3925). Distractors use one text's technical detail (molecular weight, fermentation).
- **apply_model (new).** Text 1 states a causal model with a threshold; Text 2 reports a two-condition experiment with numbers. Options pair the two conditions with "whereas"; distractors: the right outcome without the model, the model misapplied (small fish succeed), the model reversed.
- **disagree_question (new).** Two teams agree on mechanism but disagree on timing or attribution. Options are four questions: the disputed one (key), one both answer alike, one neither addresses, one that twists the method critique.
- **lit_reading (new).** Text 1 a public-domain literary excerpt (pre-1929), Text 2 a critical reading of the work. Key applies the critic's frame to the excerpt's image; distractors reverse which side of the frame the image stands for.
- **No band-7 items:** S1_counterexample, S1_rival_hypothesis, S1_limit_degree, S1_alt_explanation, S2_shared_premise, S2_hidden_assumption, S3_difference, S4_relate. Keep them for bands 5 and 6.

## 6. Checks

Small samples: every rate below comes from 13 and 14 items and could be off by 15 points either way.

Automatic:

1. **Key length.** Key of 25 words or more: 5 of 13 band-7 items, 2 of 14 band-6, 2 of 10 band-5. Mean option length of at least 24 words is a looser version. Moderate; easy to game by padding, so pair with check 4.
2. **Distractor overlap.** Mean share of distractor content words that occur in the passage at least 0.48 (band 7 mean 0.51, band 6 0.44). Weak; it flags twisted-detail distractors, not their quality.
3. **Passage length** of 135 to 150 words. Weak (AUC 0.74 but small n); do not use alone.

Agent-run:

4. **Synthesis key.** An agent states, for the key, which sentence of each text it needs and whether the key's claim appears in either text. A band-7 draft's key must need both texts and appear in neither. Band 7: 7 of 13; band 6: 2 of 14. Reliable; this is the main gate.
5. **Step count.** The agent counts steps as in the source report section 6; require 3. Band 7: 8 of 13; band 6: 1 of 14.
6. **Distractor audit.** For each distractor the agent names the passage words it reuses and why the claim fails. Require at least two distractors that reuse passage nouns (D3) or reverse the derived claim. Band 7 averages 1.9 partly right distractors; band 6, 0.9.

Do not gate on: characters per word, long-word or rare-word share, key length rank, key overlap, hedges, two-part "but" options. None separated band 7 from band 6, and the two-part shell is more common at band 6.
