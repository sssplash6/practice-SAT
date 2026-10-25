# Transitions: what makes a band-7 item

Source: every Transitions item in `material/rw/cb_api/transitions.json` with band 5, 6 or 7 (27, 25 and 16 items). All 16 band-7 and all 25 band-6 items were read with CB's rationale. Measures come from Python over the CB text; template, hard patterns, traps and distractor recipes are hand annotations made while reading (listed per item in section 1). Gaps are band 6 against band 7 with AUC (chance that a random band-7 item scores higher than a random band-6 item; 0.50 is no separation) and a permutation p value. With 16 band-7 items, only large gaps can reach p below 0.05; treat p above 0.10 as "no reliable difference".

## 1. Counts

| | Band 5 | Band 6 | Band 7 |
|---|---|---|---|
| Items | 27 (all CB medium) | 25 (all CB hard) | 16 (all CB hard) |
| Blank opens a sentence | 23 | 18 | 12 |
| Blank after a semicolon | 1 | 2 | 3 |
| Blank inside a sentence (interrupter, after an opening phrase) | 3 | 5 | 1 |
| Phrase options naming the relation ("Undermining this explanation,") | 1 | 0 | 1 |
| Already in our transcript set | 9 | 13 | 4 |

Template mix (our codes from `satbank/rw/transitions.json`; two new names where none fit):

| Template | Band 6 | Band 7 |
|---|---|---|
| C1_two_subject (contrast, two subjects) | 3 | 0 |
| C2_belief_finding (view or appearance, then finding) | 2 | 0 |
| C3_limiting_fact (claim, then a limiting fact or exception) | 2 | 1 |
| new C4_replacement (A says X does not happen; B says what happens instead) | 1 | 0 |
| K1_grant_turn (grant, then "but" or "Still") | 2 | 0 |
| K2_qualification | 2 | 1 |
| E1_consequence (consequence or conclusion licensed by A) | 2 | 3 |
| E2_motive_action | 0 | 1 |
| P1_purpose_aptness | 3 | 0 |
| A1_addition | 2 | 2 |
| X1_example | 1 | 0 |
| S1_spec_restate | 3 | 1 |
| M1_emphasis (stronger same-direction fact) | 0 | 3 |
| T1_sequence_time | 0 | 1 |
| U1_culmination_alt (ultimately, alternatively) | 2 | 2 |
| new R1_named_relation (options are participial phrases naming what B does to an earlier element) | 0 | 1 |

Per-item assignment (cb_id key, template):
- Band 7: 00e0170f In fact M1; 47e238be indeed M1; a266d876 indeed M1; a2bff07e As such E1; a965c6ed Hence E1; f5a00eff Hence E1; 3a715eca Accordingly E2; 7ce14583 What's more A1; 8fbf206d Additionally A1; 332e75bf Ultimately U1; e225cf02 alternatively U1; d3b7d7a3 more often S1; 2b08f514 Again and again T1; ecb31049 That said K2; fc95a352 Nevertheless C3; e6b1e12c Undermining this explanation R1.
- Band 6: 11df9b99, 480ade7e, edf30612 by contrast / In contrast C1; 2ba97187 On the contrary, a7a944ed though C2; b5ed1a8b by contrast, c071eca2 though C3; 70c19cf6 Instead C4; 974b5a8c, f5959727 Of course K1; 176edca6 Granted, 9dc4e640 that said K2; 42e6cc83 then, 578ca79a Accordingly E1; 1e31470f Fittingly, 8112b7e3 and f5149550 To that end P1; 1872cd6d Moreover, 4d2736f0 Similarly A1; 1c6e1d55 for instance X1; 4b7a84b0 More often, 8e9677e6 Specifically, e3edc138 That is S1; 6e0c60da Ultimately, 9502ec65 Alternatively U1.

Templates with no band-7 items: C1, C2, K1, P1, X1 (and C4). The plain contrast family that dominates band 6 (8 of 25 items are C1 to C4) has one band-7 item, and that one keys "Nevertheless" rather than a contrast word. Band 7 needs M1_emphasis, which has no band-6 item. Our transcripts drifted: 3.6, 3.10, 3.12 and 3.20 are now band 7; 2.6 and 3.1, 3.3, 3.4, 3.7, 3.8, 3.13 to 3.19 are band 6. Only 3 of our 10 authored hard items list a band-7 model.

## 2. What separates 7 from 6, measured

### The connective rarity measure

Three measures, because no single corpus fits connectives:
- **Bank exposure**: how many of the 194 CB Transitions items offer the connective as any option (case-folded). This is the student-facing measure: how often a student meets the word in this exact task. Plus membership in the source report's 13 core connectives (however, for example, for instance, as a result, by contrast, for this reason, in addition, next, therefore, thus, consequently, similarly, likewise).
- **Old-prose rate**: occurrences per million words in connective position (start of a sentence or clause, after `. ; : ! ?` or a line break, followed by a comma) in the 56.7-million-word Gutenberg corpus cached at `~/.cache/satbank/frequency` (the sources of `tools/data/freq.txt`). It misses modern connectives almost entirely (Additionally, Regardless and In contrast never occur there in that position).
- **Modern rate**: the same count in the cached federal texts (NSF, NASA, NOAA, CRS; 367,000 words). Small sample: one hit is 2.7 per million, so single-digit counts are noise.

Across all seven bands the measures do track difficulty: the core-13 share of keys falls from 57% (band 1) to 0% (band 7), and key band correlates with bank exposure at Spearman -0.21 and with the modern rate at -0.31.

| Band | Keys | Core-13 key | Median bank exposure of key | Median old-prose rate | Median modern rate | Adversative key |
|---|---|---|---|---|---|---|
| 1 | 7 | 57% | 12 | 22.3 | 5.4 | 29% |
| 2 | 26 | 58% | 15.5 | 4.0 | 17.7 | 23% |
| 3 | 47 | 47% | 11 | 0.9 | 5.4 | 19% |
| 4 | 46 | 37% | 17 | 1.3 | 9.5 | 28% |
| 5 | 27 | 26% | 10 | 0.1 | 5.4 | 30% |
| 6 | 25 | 20% | 6 | 0.3 | 2.7 | 48% |
| 7 | 16 | 0% | 6.5 | 0.6 | 2.7 | 19% |

**Rarity saturates at band 6.** Band-6 and band-7 keys are equally rare by every measure except one: band 7 never keys a core-13 connective (0 of 16, against 5 of 25 at band 6: similarly, for instance, by contrast three times). The source report's finding (hard keys are rarer) holds for easy against hard, not for 6 against 7.

### Results

| Signal | Band 5 | Band 6 | Band 7 | AUC | p | Separates? |
|---|---|---|---|---|---|---|
| Passage words | 52.6 | 57.3 | 58.7 | 0.52 | 0.83 | no |
| Words per sentence | 24.4 | 24.1 | 26.8 | 0.63 | 0.17 | weak |
| Characters per word | 5.35 | 5.11 | 5.37 | 0.69 | 0.04 | **yes** |
| Long-word rate | 14.5% | 13.5% | 14.7% | 0.59 | 0.31 | no |
| Passage tokens past rank 10,000 | 17.5% | 17.1% | 18.3% | 0.65 | 0.12 | weak |
| Words in the blank's sentence | 23.6 | 23.7 | 26.8 | 0.59 | 0.35 | no |
| Key from the core 13 | 7/27 | 5/25 | 0/16 | 0.40 | 0.15 | weak (but absolute at band 7) |
| Key bank exposure (mean) | 12.7 | 11.5 | 8.1 | 0.40 | 0.28 | no |
| Key is the rarest option by bank exposure | 59% | 64% | 69% | 0.52 | 1.00 | no |
| Key old-prose rate, modern rate | | | | 0.52, 0.43 | 0.87, 0.45 | no |
| Key length rank (1 = longest) | 2.48 | 2.32 | 2.69 | 0.58 | 0.41 | no |
| Key is adversative (contrast or concession) | 30% | 48% | 19% | 0.35 | 0.10 | yes, reversed |
| Distractor from the key's narrow family | | 0/25 | 0/16 | | | no |
| Distractor from the key's broad family | 2/27 | 2/25 | 1/16 | | | no |
| Broad families among the four options | 3.33 | 3.56 | 3.38 | 0.42 | 0.40 | no |
| A sentence follows the blank's sentence | | 3/25 | 0/16 | | | no |
| Clue reaches beyond the adjacent sentence | | 4/25 | 2/16 | 0.48 | 1.00 | no |
| Relation is rhetorical (concession, emphasis, restatement, purpose, culmination, conclusion) | | 11/25 | 9/16 | 0.56 | 0.53 | no |
| Hard patterns of report section 6 present (mean) | | 0.60 | 0.94 | 0.63 | 0.14 | weak |
| **Surface contrast, non-adversative key** (hand) | | 1/25 | 8/16 | 0.73 | 0.001 | **strongest** |
| Same referent, new member (hand) | | 1/25 | 3/16 | 0.57 | 0.29 | weak |
| Items with a phantom-sequence or premature-summary decoy | | 5/25 | 0/16 | 0.40 | 0.14 | weak (but absolute) |

Reasoning steps: the source report does not count steps; it lists five hard patterns (concession frame; content contrast with logical support; argument-level link; restating an abstract claim; stacked or pre-empted connectives). I counted those per item. Band 7 averages 0.94 patterns against 0.60, a weak gap; the one pattern that separates sharply is the second.

What the numbers say:
1. **The defining band-7 move is a surface contrast with a supporting or consequential relation.** Half the band-7 items (8 of 16) put opposite-looking content next to the blank while the right relation is emphasis, consequence or conclusion, and offer one or two adversative decoys. Band 6 does this once in 25.
2. **Band 6 is where plain contrast and concession live.** 12 of 25 band-6 keys are adversative; only 3 of 16 band-7 keys are, and none is a plain contrast word.
3. **Key rarity is a floor, not a lever.** Every band-7 key is outside the core 13, but band-7 keys are no rarer than band-6 keys. Familiar words (Additionally, Nevertheless, indeed, In fact) are band-7 keys when the passage makes their relation hard to see.
4. **Denser words, slightly.** Characters per word rise from 5.11 to 5.37 (p 0.04): band-7 passages read like abstracts (siderophile, proteome, conspecific brood parasitism, geodetic data).
5. **No signal:** passage length, key length, distractor family closeness (still never two options of one relation), clue reach.

### Per-item annotations

Hand annotations behind the counts above, for audit. Distractor recipes are in option order, key left out.

| cb_id | band | template | hard patterns | surface contrast | same referent | distractor recipes |
|---|---|---|---|---|---|---|
| 7ce14583 | 7 | A1_addition | 0 | - | yes | wrong grain, wrong grain, false opp |
| 8fbf206d | 7 | A1_addition | 0 | - | yes | unearned cause, false opp, wrong grain |
| fc95a352 | 7 | C3_limiting_fact | 0 | - | - | unearned cause, false parallel, additive |
| a2bff07e | 7 | E1_consequence | 2 | yes | - | false opp, wrong grain, false opp |
| a965c6ed | 7 | E1_consequence | 1 | yes | - | false opp, false opp, wrong grain |
| f5a00eff | 7 | E1_consequence | 2 | yes | - | false opp, wrong grain, false parallel |
| 3a715eca | 7 | E2_motive_action | 1 | yes | - | wrong grain, false opp, wrong grain |
| ecb31049 | 7 | K2_qualification | 1 | - | - | unearned cause, additive, wrong grain |
| 00e0170f | 7 | M1_emphasis | 1 | yes | - | unearned cause, false opp, false opp |
| 47e238be | 7 | M1_emphasis | 1 | yes | - | false opp, additive, unearned cause |
| a266d876 | 7 | M1_emphasis | 1 | yes | - | false opp, unearned cause, additive |
| e6b1e12c | 7 | R1_named_relation | 1 | - | - | false opp, false parallel, false parallel |
| d3b7d7a3 | 7 | S1_spec_restate | 2 | yes | - | unearned cause, additive, false opp |
| 2b08f514 | 7 | T1_sequence_time | 1 | - | - | wrong grain, unearned cause, false opp |
| 332e75bf | 7 | U1_culmination_alt | 1 | - | - | unearned cause, additive, unearned cause |
| e225cf02 | 7 | U1_culmination_alt | 0 | - | yes | wrong grain, wrong grain, false parallel |
| 1872cd6d | 6 | A1_addition | 0 | - | yes | wrong grain, false opp, wrong grain |
| 4d2736f0 | 6 | A1_addition | 0 | - | - | wrong grain, unearned cause, false opp |
| 11df9b99 | 6 | C1_two_subject | 0 | - | - | wrong grain, wrong grain, false parallel |
| 480ade7e | 6 | C1_two_subject | 0 | - | - | additive, wrong grain, unearned cause |
| edf30612 | 6 | C1_two_subject | 0 | - | - | wrong grain, unearned cause, false parallel |
| 2ba97187 | 6 | C2_belief_finding | 0 | - | - | additive, unearned cause, phantom seq |
| a7a944ed | 6 | C2_belief_finding | 1 | - | - | wrong grain, unearned cause, false parallel |
| b5ed1a8b | 6 | C3_limiting_fact | 0 | - | - | unearned cause, false parallel, wrong grain |
| c071eca2 | 6 | C3_limiting_fact | 1 | - | - | unearned cause, wrong grain, additive |
| 70c19cf6 | 6 | C4_replacement | 0 | - | - | wrong grain, false opp, false opp |
| 42e6cc83 | 6 | E1_consequence | 1 | - | - | false opp, additive, wrong grain |
| 578ca79a | 6 | E1_consequence | 0 | - | - | summary, false opp, false opp |
| 974b5a8c | 6 | K1_grant_turn | 2 | - | - | false opp, wrong grain, additive |
| f5959727 | 6 | K1_grant_turn | 2 | - | - | additive, false parallel, unearned cause |
| 176edca6 | 6 | K2_qualification | 1 | - | - | wrong grain, wrong grain, unearned cause |
| 9dc4e640 | 6 | K2_qualification | 1 | - | - | unearned cause, wrong grain, false parallel |
| 1e31470f | 6 | P1_purpose_aptness | 1 | - | - | additive, phantom seq, false opp |
| 8112b7e3 | 6 | P1_purpose_aptness | 1 | - | - | summary, wrong grain, additive |
| f5149550 | 6 | P1_purpose_aptness | 1 | - | - | wrong grain, false opp, additive |
| 4b7a84b0 | 6 | S1_spec_restate | 1 | yes | - | additive, false opp, false opp |
| 8e9677e6 | 6 | S1_spec_restate | 0 | - | - | additive, false opp, unearned cause |
| e3edc138 | 6 | S1_spec_restate | 1 | - | - | additive, false opp, false parallel |
| 6e0c60da | 6 | U1_culmination_alt | 1 | - | - | unearned cause, additive, additive |
| 9502ec65 | 6 | U1_culmination_alt | 0 | - | - | wrong grain, wrong grain, unearned cause |
| 1c6e1d55 | 6 | X1_example | 0 | - | - | additive, phantom seq, false opp |

## 3. What separates 7 from 6, read

1. **Outlier, then the majority (emphasis).** 47e238be and a266d876 share one frame: "mark Iceland's volcanoes as extreme outliers; ______ many ... are fed by shallow pockets". B describes other volcanoes with the opposite value, so "nevertheless" looks right; the key "indeed" says the contrast proves the outlier claim. 00e0170f does the same with "their dream remains unrealized. In fact, ... all are in Asia."
2. **Consequence whose content is a correction.** a965c6ed: "appears external ... Hence, the shell is often incorrectly assumed to be an exoskeleton". B is full of contrast ("incorrectly", "when in fact"), and "However" and "That being said" are offered; the relation to A is cause. a2bff07e: B says Ostrom's work "is a repudiation of" a view, which invites "By contrast"; the key "As such" draws the conclusion.
3. **Conclusion across three sentences.** f5a00eff: a counterfactual model, then "Siderophiles are much more abundant ... however", then "Hence, extraterrestrial material ... accreted". The "however" sits in A, so "That said" is tempting.
4. **Same referent, new member.** 8fbf206d: vivid prose about color tools, then "______ Varichon's book features many high-quality images of these ... tools". B points back to the same tools, so "Specifically" tempts; the images are a second feature (Additionally). 7ce14583 ("What's more") and e225cf02 ("alternatively", a single named duck whose behavior differs) work the same way: B looks like an instance or a rewording.
5. **A familiar adversative in a less common role.** fc95a352 keys "Nevertheless" for an exception to a habit ("typically custom fits ... for the film Sunshine ... standard sizes"); the other three options are not adversative, so the item is hard only because students hold "nevertheless" as "despite that". e6b1e12c makes the student tell an explanation from a phenomenon: "Undermining this explanation" against "Contrary to this phenomenon".
6. **Rare time and frequency keys.** "Again and again," (2b08f514, bank exposure 1) with a "yet" inside B that pre-empts the concession decoy; "more often," (d3b7d7a3) after "However, a 2016 study ... complicates this popular narrative;".

How band 6 is hard instead: a grant before a turn ("Of course ... but", "Of course ... Still"), purpose and aptness (To that end, Fittingly), restating a debate (That is), a contrast connective placed as an interrupter ("A flipped chiral molecule, ______ can be compared"). In band 6 the relation, once seen, matches the surface; in band 7 the surface points the wrong way.

## 4. Distractor recipes at band 7

Recipe names from `spec/rw/transitions.md` section 5.

| Recipe | Band 6 (75 distractors) | Band 7 (48) |
|---|---|---|
| False opposition (contrast or concession decoy) | 15 (20%) | 15 (31%) |
| Unearned cause (incl. to that end, fittingly) | 13 (17%) | 10 (21%) |
| Wrong grain (example, restatement, specification, emphasis) | 20 (27%) | 12 (25%) |
| Additive decoy | 15 (20%) | 6 (13%) |
| False parallel (similarly, likewise, "drawing a similar conclusion") | 7 (9%) | 5 (10%) |
| Phantom sequence or time | 3 (4%) | 0 |
| Premature summary | 2 (3%) | 0 |

- **False opposition dominates at band 7**, and it is the hardest distractor in the 8 surface-contrast items: the decoy names the relation the content seems to have (nevertheless, that said, however, by contrast). Three band-7 items offer two adversative decoys (00e0170f, a2bff07e, a965c6ed), often a synonym pair (Nevertheless and That said; That being said and However), which a careful student can drop together; the trap works on the first read.
- **Obvious decoys disappear.** No band-7 item offers an ordinal, "In sum" or a time word that cannot apply; band 6 has five.
- **Band 7 only: a same-family decoy.** e6b1e12c is the one item in either band whose decoy shares the key's relation ("Contrary to this phenomenon" against "Undermining this explanation"); it fails on its referent, not its relation.
- **Wrong grain against a same-referent B.** In the addition and alternative items the hardest decoy is Specifically, In other words, For instance, In particular or For example, because B names the same object or a single case.
- Still true at band 7: the key's relation is never repeated among the distractors.

## 5. Band-7 writing recipe

Settings common to every band-7 template:
- Key outside the core 13. Prefer: indeed, in fact, hence, accordingly, as such, what's more, additionally, alternatively, ultimately, more often, that said, nevertheless (used for an exception).
- No phantom-sequence or premature-summary decoys; every decoy must be a relation a hurried reader could attach.
- At least one false-opposition decoy whenever the key is not adversative; two (a synonym pair) is allowed.
- Characters per word at least 5.3 (band-7 mean 5.37): a technical or academic subject with glossed terms.
- Two or three sentences, 50 to 65 words; the blank opens the last sentence or follows a semicolon.

Per template (what to change from the band-6 version):
- **M1_emphasis (main band-7 template).** A: X is an outlier, unusual, or unrealized. B (after a semicolon or a period): most other cases have the opposite value, or every existing case lies elsewhere. Key indeed or in fact. Decoys: nevertheless (false opposition), in addition (additive), consequently (unearned cause). No band-6 counterpart exists; build it fresh.
- **E1_consequence.** Band 6 states a plain result. Band 7 makes B's content a correction, a repudiation or an "incorrectly assumed ... when in fact" statement, so that B contains its own contrast while following from A. Or spread the reasoning over three sentences with a "however" in sentence 2 and the conclusion after the blank. Key hence, as such or accordingly; decoys however and that said plus one wrong grain.
- **E2_motive_action.** A lesson or finding, then a change of practice phrased with "rather than" inside B. Key accordingly; decoys that said, in other words, for example.
- **A1_addition.** Band 6 lists two separate acts (weaving threads, stamping leaves). Band 7 makes B point back to the same object as A ("these ... tools", "in responding to Adnan's artwork") while adding a new feature. Key additionally or what's more; decoys specifically or in other words, plus one adversative.
- **U1_culmination_alt.** Culmination: a long struggle in A (often with a dash interruption), the resolution in B; key ultimately, decoys hence, to that end, moreover. Alternative: B describes one named case acting differently, with only instance-type decoys (in particular, for example, similarly) and no plain contrast word on offer.
- **S1_spec_restate.** Use the frequency form: A or the clause before the blank challenges a popular account; B (after a semicolon and an interrupter like "researchers determined,") gives the more common case. Key more often; decoys nevertheless, for this reason, additionally.
- **K2_qualification.** A long-held belief, then a record that cuts against it ("no fusion reaction ... had ever generated a net energy gain"). Key that said; decoys for this reason, moreover, specifically. This is close to band 6; keep the register dense.
- **C3_limiting_fact.** Habit, then a one-off exception keyed with nevertheless, with no other adversative option. Works only if the passage gives the exception a purpose (the spacesuits "reflected the ungainliness of actual spacesuits").
- **T1_sequence_time.** Repetition over decades with "Again and again," and a "yet" inside B that pre-empts the concession decoy (Granted).
- **R1_named_relation (new).** Options are participial phrases that name the referent ("Undermining this explanation", "Contrary to this phenomenon", "Confirming this hypothesis", "Drawing a similar conclusion"). A states a phenomenon and an explanation for it; B undermines the explanation, not the phenomenon.
- **No band-7 items:** C1_two_subject, C2_belief_finding, K1_grant_turn, P1_purpose_aptness, X1_example (and the new C4_replacement). Do not try to push these to band 7; use them for band 5 and 6.

## 6. Checks

Automatic:

1. **Key outside the core 13.** Necessary, not sufficient: all 16 band-7 items pass, and 20 of 25 band-6 items also pass.
2. **No obvious decoys.** Reject any option from the sequence family (firstly, next, lastly, second of all) or premature summary (in conclusion, in sum, in the end) unless it is the key. All 16 band-7 items pass; 4 of 25 band-6 items fail by this regex.
3. **Surface-contrast proxy.** Key not adversative, at least one adversative distractor, and an opposition word (however, though, but, yet, rather than, instead, incorrectly, unlike, whereas, while, not, only, outlier, majority, contrary, despite, in fact) in the sentence before the blank or the blank's own sentence. Passes 9 of 16 band-7 items, 3 of 25 band-6 and 5 of 27 band-5. Reliable as a positive signal: few band-6 items trip it.
4. **Register.** Characters per word (lowercase words, `register()` in `tools/check_rw.py`) at least 5.3: 11 of 16 band-7 items, 7 of 25 band-6.
5. **Combined gate** (1 and 2, and either 3 or 4): passes 14 of 16 band-7 items and 5 of 25 band-6 items (8 of 27 band-5). This was fitted on the same items it is scored on, so expect it to be looser on new drafts.

Agent-run:

6. **Trap annotation.** An agent states the relation of B to A and then says whether B's content, read alone, looks like a contrast (surface contrast) or like an instance or rewording of A (same referent). Band 7: one of these in 11 of 16 items; band 6: 2 of 25. Reliable if the agent is asked about the content first and the options second.
7. **Decoy pull.** For each adversative or wrong-grain decoy, the agent writes the misreading that makes it attractive. A band-7 draft should have one decoy with a misreading that a 1400-scorer would plausibly make on first read.

Do not gate on: key bank exposure or corpus rates beyond the core-13 rule, passage length, key length, family closeness, clue reach. None separated band 7 from band 6.
