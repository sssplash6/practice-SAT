# Inferences: what makes a band-7 item

Source: `material/rw/cb_api/inferences.json` (140 official items with CB's rationale and official key). Bands 5, 6 and 7 hold 22, 38 and 34 items. Our transcript set covers 23 of the band-6 items and 10 of the band-7 items, so 39 of the 72 were new to us. The old transcript had no usable key for its hard tier (the letters were solved by reading); checked against the official keys, all 71 transcript letters are correct, so nothing in `spec/rw/inferences.md` needs a key fix. All 72 band-6 and band-7 items were read with CB's rationale and hand-coded. The numbers below come from a scratch script over the CB file (register measures reuse `tools/check_rw.py`, rarity uses `tools/data/freq.txt`).

**AUC** in the tables is the chance that a random band-7 item scores higher than a random band-6 item (ties count half). 50% means no separation; 70% or more (or 30% or less) is a real gap here (one standard error is about 7 points). Hand codes were made by one reader who knew the band, so they are a careful reading, not a blind measure. The two CB-rationale lengths in section 2 are independent of my reading and agree with it.

## 1. Counts

| | band 5 | band 6 | band 7 |
|---|---|---|---|
| items | 22 | 38 | 34 |
| stem | "Which choice most logically completes the text?" in all | same | same |

Template mix (codes from `satbank/rw/inferences.json` and `spec/rw/inferences.md` section 7; band 5 only where the transcript plan already assigns one):

| template | band 5 (12 of 22 coded) | band 6 | band 7 |
|---|---|---|---|
| S1 controlled comparison | 1 | 3 | 3 |
| S2 principle plus case (S10 trade-off folded in) | 4 | 11 | 10 |
| S3 rule or timeline rejects a premise | 1 | 4 | 4 |
| S4 elimination | 0 | 1 | 3 |
| S5 undercut, hedged conclusion | 2 | 0 | 2 |
| S6 X but not Y | 0 | 6 | 3 |
| S7 two cases or two accounts | 0 | 5 | 1 |
| S8 co-occurrence | 1 | 2 | 0 |
| S9 action reveals belief or motive | 2 | 2 | 2 |
| S11 received view plus counterevidence | 1 | 3 | 4 |
| **M1 method flaw** (new): a study design or sampling problem limits what the results show | | 1 | 2 |

Target of the missing ending (spec section 2 codes):

| target | band 6 | band 7 |
|---|---|---|
| T1 conclusion from evidence | 15 | 11 |
| T2 someone else's belief, assumption or implication | 2 | 8 |
| T3 consequence or prediction | 10 | 6 |
| T4 explanation or mechanism | 8 | 7 |
| T5 status of the evidence | 3 | 2 |

Notes: S2 is the workhorse at both bands. S4 (elimination), S5 (undercut) and M1 lean to band 7; S6, S7 and S8 lean to band 6. Our plan skipped S5 at hard, but the CB bank has two band-7 S5 items (8e6a96f5 duckweed, db57afa3 Venus whistler waves). The clearest mix change is the target: reconstructing what a named party "implies", "contends" or "reasons" is 8 of 34 at band 7 and 2 of 38 at band 6.

## 2. What separates 7 from 6, measured

Hand-coded measures:
- **Reasoning steps**: the scale of `spec/rw/inferences.md` 7.2 (1 = combine the blank sentence with one fact; 2 = one unstated bridge; 3 = two chained bridges, or a counterfactual, a direction, or someone else's belief to hold).
- **Clue distance**: sentences between the farthest premise the key needs and the sentence with the blank (0 = the premise is in the blank sentence).
- **Partly-right distractors**: wrong endings that keep a true premise or the right pieces and break one link.
- **Near-miss labels**: MIX, CAUSE, ECHO, PART, POL, REP, as in spec section 5.

| measure | band 5 median | band 6 median (mean) | band 7 median (mean) | AUC 7>6 | verdict |
|---|---|---|---|---|---|
| passage words (prose) | 83.5 | 101 (94) | 108 (106) | 71% | separates, modestly (band 5 to 7 rises steadily) |
| option length, words (mean of 4) | 14.9 | 17.4 (18.0) | 21.0 (22.3) | 70% | separates |
| same, T1 conclusion items only | | 17.3 | 27.0 | | strongest where the target is a conclusion |
| key length, words | 13 | 17 | 21 | 66% | weak (all options grow together) |
| key / distractor length ratio | 1.00 | 0.98 | 0.94 | 41% | no; the band-7 key is, if anything, a bit shorter than its distractors |
| words per sentence | 24.8 | 25.1 | 26.9 | 56% | no |
| chars per word | 5.42 | 5.37 | 5.41 | 45% | no |
| long-word rate (9+ letters) | 16% | 16% | 17% | 51% | no |
| rare-word rate (rank beyond 10,000) | 22% | 21% | 25% | 57% | no |
| key rare-word rate | 26% | 24% | 20% | 38% | weak, reversed: band-7 keys use plainer words than band-6 keys |
| key overlap with passage | 0.50 | 0.52 | 0.49 | 41% | no |
| key minus best distractor overlap | -0.10 | -0.10 | -0.19 | 37% | weak: at band 7 the best distractor out-borrows the key by more |
| key carries a hedge | 36% | 42% | 47% | 53% | no |
| distractors carrying a hedge (mean) | 0.64 | 0.92 | 1.29 | 58% | no |
| key contains a negation or contrast word | 32% | 21% | 50% | 65% | weak |
| options with a negation or contrast word (mean) | 0.77 | 0.89 | 1.56 | 66% | weak |
| asides per passage (parentheses, dash pairs; mean) | 0.50 | 0.74 | 1.26 | 63% | weak |
| passages with a number / with a percentage | 50% / 5% | 42% / 11% | 62% / 21% | | weak |
| reasoning steps (hand) | | 2 (1.97) | 2 (2.44) | 71% | separates: 3 steps in 15 of 34 band-7 items, 4 of 38 band-6 |
| clue distance (hand) | | 1 (1.53) | 2 (2.06) | 66% | weak: 2 or more in 23 of 34 vs 15 of 38 |
| partly-right distractors (hand) | | 1 (0.76) | 1.5 (1.56) | 72% | separates: 2 or more in 17 of 34 vs 6 of 38; all 3 in 7 vs 1 |
| near-miss labels (hand) | | 1 (0.84) | 1 (0.94) | 52% | no (band-7 reversals are near misses too, see section 4) |
| CB rationale words per distractor | 42 | 50 | 68.5 | 72% | separates (independent of my coding) |
| CB rationale words for the key | 114 | 132 | 157 | 70% | separates (independent of my coding) |

Plainly: vocabulary, sentence length, word overlap and the key's hedge do **not** separate band 7 from band 6. Length separates a little (passages about 7 words longer, options about 4 words longer). The real gap is in the logic: more steps, more distractors that are right in part, and keys that CB itself needs about 25 more words to justify and about 19 more words per distractor to refute.

## 3. What separates 7 from 6, read

1. **The ending reconstructs someone else's reasoning.** Lead-ins such as "These scientists therefore imply that", "Ghisbain therefore contends that", "some linguists reason that" and "leading other scientists to suggest that" ask for a claim the passage's author never makes. In db57afa3 the other scientists must keep the whistler waves (their energy signatures match Earth's) and drop only lightning as the cause: "geophysical characteristics of Venus not shared with Earth". In 5f16d809 the defenders' general point ("reimaginings ... are almost as old as the myths themselves") must be turned against the purists' specific charge, giving "not indicative of a novel attitude regarding fidelity".

2. **The key is negative, conditional or "other than".** Half the band-7 keys carry a negation or contrast (band 6: a fifth): "driven by one or more factors not associated with mate attraction" (27ea642e); "human activity likely played no role" (ac285054); "if each ecotype is indeed locally adapted ..., those adaptations are to other environmental conditions" (8e6a96f5). The student has to accept a conclusion about what the evidence rules out, not what it shows.

3. **The decisive premise hides in an aside or a subordinate clause.**
   - 8e6a96f5 parks it in a parenthesis: "(The researchers did not replicate local differences in light or temperature.)"
   - 1ffd60ce: "despite Sidon's persistent oppressive financial obligations" rules out simply adding silver.
   - 26f5c4ba: the burden that explains the choice is in sentence 1's "green plans that cap electricity usage".
   - 4802f6a5 defines specificity in a parenthesis, and the key depends on that definition.
   Band-7 passages carry 1.3 asides on average (band 6: 0.7).

4. **Several facts with graded strength must all be honoured.**
   - 8209f485 weighs three candidate causes against three findings. The key allots each its exact weight: "a social learning effect that eventually diminishes, though environmental constraints cannot be ruled out".
   - 9869c261 maps coarse grains, fine grains and cracking onto streams, a lake and drying.
   - b9a3941b compares three date ranges ("as early as 2300–1900 BCE" against Anatolia's "circa 2200–2000 BCE").
   - 4b8eda0a states the bar outright: an interpretation "that accounts for all the evidence".

5. **Direction, quantity and sequence.** In 1ffd60ce the student has to see that keeping the silver and cutting the weight raises the silver share. 96d1c1fe offers four directions of transport and exchange. f1bfbed3 needs the direction of a counting bias (who split species more). e9521fd1 needs the order of two events (the language split preceded maize).

6. **A long-range premise in a plain passage.** f27559d4 (volunteering, 6%) is short and easy to read, but the key needs the author's claim in sentence 1 ("good for society as a whole"). 5cd55c77 needs sentence 1's "drawn toward areas where light is present". Band 7 can come from distance alone.

What band 6 looks like by contrast: the lead-in nearly states the relation ("Suspecting that disruptions to an unpleasant experience would have the opposite effect", ce4448b7; the one-sentence 0dba14e6), one principle maps onto one case, and distractors are mostly off-topic claims or comparisons with unmentioned groups.

## 4. Distractor recipes at band 7

Labels from `spec/rw/inferences.md` section 5. 114 band-6 and 102 band-7 wrong options:

| recipe | band 6 | band 7 | change |
|---|---|---|---|
| REV reversal (contradicts or runs the logic backwards) | 22 | 30 | up |
| MIX swap (right pieces, wrong entity, variable, time or link) | 14 | 19 | up |
| OUT off-topic claim | 31 | 21 | down |
| CMP unsupported comparison | 14 | 6 | down |
| EXT overreach | 12 | 11 | flat |
| CAUSE rival mechanism | 10 | 10 | flat |
| ECHO, VAR, REP, POL, PART, REC, FUT | 11 | 5 | down |

REV + MIX make up 48% of band-7 distractors (32% at band 6). Items with at least two REV or MIX distractors: 18 of 34 at band 7, 9 of 38 at band 6. No label appears only at band 7. What changes is how REV and MIX are built:

- **Rescue of the received view.** b9a3941b C keeps diffusion from Anatolia but by "an alternate route". D pushes Anatolia's date earlier. 8e6a96f5 D blames a mismatch in zinc levels. Each saves the old view instead of accepting the new evidence.
- **The wrong premise attacked.** In db57afa3 the distractors doubt the data, whether the waves are whistlers, and Venusian lightning's properties; only the key doubts the one link the evidence undercuts.
- **Permutation sets.** All four options recombine the same pieces: lake / stream / drying (9869c261), direction of transport (96d1c1fe), social learning / environment / genetics (8209f485). Only one combination fits every fact.
- **Direction flips that sound like the key.** f1bfbed3 C ("less sensitive to the degree of morphological variation") is the key's mechanism pointed the wrong way. 6b8a7c74 A swaps the effort of *using* a card for the effort of *obtaining* it.

How the hardest distractor is built: from the key's own components with one link moved, or as the natural rebuttal a reader expects. 5f16d809 C, "purists are overlooking a long tradition of adapting ... to focus on female characters", sounds like the defenders' answer but narrows their general claim to one they never made. CB spends 90 or more words refuting such options.

## 5. Band-7 writing recipe

General settings for every band-7 draft:
- Passage 100 to 120 words in 3 to 5 sentences. At least one needed premise sits two or more sentences before the blank, or inside an aside (parenthesis, dash pair, "despite" clause).
- Options 20 to 30 words; the key no longer than the distractors.
- Key: a negative, conditional or "other than" conclusion where the logic allows it; hedge it as the evidence requires, not by habit.
- At least two distractors partly right: they keep a true premise or the right pieces and break one link. At least two REV or MIX. At most one plain OUT.
- Do not raise vocabulary or sentence length; neither moves the band.

Per template (band-7 counts in brackets):

**S2 principle plus case [10].** Change from a band-6 S2:
- Give the principle two parts or a constraint (minimize cost *and* inconvenience; "despite ... financial obligations"); chain two principles (gift-card effort norm plus card usability); or make the case reverse a stated trend (Bertrand: competition now favours brains, not bodies).
- The blank asks for the explanation or consequence the constraint forces.
- Distractors: REV (the trend continued), MIX (the right mechanism on the wrong variable: weight instead of proportion, using instead of obtaining), CAUSE (a rival motive the definitions exclude).

**S11 received view plus counterevidence [4].**
- The new interpretation must account for every piece of evidence: a woman *and* a man taped to the wall (4b8eda0a); anterior genes everywhere *and* posterior genes at the edges (086dd8cc).
- Or the blank asks what the doubters "imply" (sleep: "advantageous in ways that have yet to be discovered").
- Distractors: partial revisions that explain only one piece (MIX, PART); the old view (REV); an overgeneralization to "most traits" (EXT).

**S3 timeline or rule [4].**
- Use three or more dates or ranges, one of them overlapping another (iron metallurgy); or a rule about shared vocabulary run backwards (Uto-Aztecan maize).
- Key: a negative or independent-origin conclusion ("played no role", "would not have featured", "preceded the acquisition").
- Distractors: rescues (another route, an earlier origin) and a sequence swap.

**S4 elimination [3].**
- Name three candidates and give each a finding of different strength (a temporary correlation, a modest one, none).
- Key: the survivor with the exact hedge on the rest.
- Distractors: every other weighting of the same candidates (permutation set). Or set a direction trap (which census split species more) or a direction-of-movement set (96d1c1fe).

**S1 controlled comparison [3].**
- Hide the comparison in numbers or a parenthetical definition (42.7% vs 37.5%; 64% vs 95.5%; specificity defined in parentheses).
- Key: interprets the numbers ("do not always avoid", "greater genetic difference").
- Distractors: a comparison with an unmeasured group (CMP), a misread of the definition (REV), the right numbers attached to the wrong period (MIX).

**S6 X but not Y [3].**
- The blank names the two poles of a disparity (Brâncuşi: importance vs output); or a consequence of the one affected stage (light blocks hatching only); or the side of a contrast a party would dispute (Aztec ethics).
- Distractors: pairs that are both real but not in tension (REV), and one-factor versions (PART).

**S5 undercut [2]** (none in our hard plan; add it).
- A hypothesis, a null result, and a parenthetical limit on what was tested. Key: "if X is true, it must be due to something other than what was tested".
- Or: a lack of corroboration redirects the cause, not the observation.
- Distractors: overreach ("do not represent adaptations" at all), a rival excuse, attacks on the wrong premise.

**S9 action reveals belief [2].**
- Phrase the lead-in as a counterfactual belief ("thought that if he hadn't already seen it") or as what a recommendation implies about an existing tool (HST "will likely continue to be used primarily" outside the solar system).
- Distractors: an overstatement of the recommendation (EXT); details echoed from the passage (ECHO, MIX).

**M1 method flaw [2]** (new).
- A study design flaw (no control for task difficulty), or a practice resting on an unrepresentative case (bumblebees as the model for all wild bees).
- Key: what the results could wrongly suggest, or the caution the critic urges.
- Distractors: other sensible limitations the flaw does not produce, and an overreach ("should not use bumblebees ... even ones with feeding patterns ... similar").

**S7 two accounts [1].**
- Band 7 only when one account is a counter-argument whose general claim must be applied to the other side's specific charge (5f16d809).
- The common-ground and "depends on location" versions stay at band 6.

**No band-7 items:** S8 co-occurrence. Do not aim it at band 7.

## 6. Checks

Only signals that separated in section 2. Reliability is the AUC on the official items, or the two rates.

Automatic (script):
1. **Option length.** Mean option length 20 words or more (band 7 median 21, band 6 17). Reliability 70%.
2. **Passage length.** 100 or more prose words (band 7 median 108, band 6 101). Reliability 71%, but the gap is small, so use it only to reject short drafts.
3. **Key not longer than the distractors.** Key-to-distractor length ratio of 1.0 or less. It does not separate the bands (41%), but it keeps a band-7 draft from giving itself away.
4. **Soft flags, not gates:** key contains a negation, contrast or conditional (65%); two or more options with one (66%); one or more asides in the passage (63%). Each is weak alone. A draft with none of the three is unlikely to read as band 7.
5. **Not used:** chars per word, long-word rate, rarity, words per sentence, overlap, key hedge.

Agent-run (a reviewer model reads the draft):
6. **Steps.** Count bridges on the spec 7.2 scale and list the sentences each bridge uses. Band 7: 3 steps, or 2 steps with a premise two or more sentences from the blank. Reliability 71% for steps; 3-step items are 44% of band 7 and 11% of band 6.
7. **Partly-right distractors.** For each wrong option, name the true premise or correct piece it keeps and the one link it breaks. Band 7: at least two. 17 of 34 band-7 items qualify against 6 of 38 band-6 (reliability 72%). A text proxy (concession words in CB-style refutations) did not work (52%), so use the agent.
8. **Recipe mix.** Label distractors with section 4 codes. Require two or more REV or MIX (18 of 34 band-7, 9 of 38 band-6). Reject drafts whose distractors are mostly OUT and CMP.
9. **Target.** Prefer T2 lead-ins (someone else's implication). They are a strong sign when present (8 of 34 vs 2 of 38) but not required.
10. **Refutation length (experimental).** Ask the reviewer to justify the key and refute each distractor in CB's style. On the official items CB needs 157 words for a band-7 key and 69 per distractor, against 132 and 50 at band 6 (AUC 70% and 72%). If every distractor of a draft can be refuted in one short sentence, it is a band-6 draft. The cut-off depends on the reviewer's verbosity, so calibrate it on 10 official items of each band first.

A draft that passes 1, 6, 7 and 8 matches band 7 on every signal that separated the official items.
