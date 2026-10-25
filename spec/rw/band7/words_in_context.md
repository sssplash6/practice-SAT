# Words in Context: what makes a band-7 item

Source: every Words in Context item in `material/rw/cb_api/words_in_context.json` with band 5, 6 or 7 (29, 28 and 33 items). All 33 band-7 and all 28 band-6 items were read with CB's rationale. Measures come from Python over the CB text; template, reasoning steps, clue position and distractor recipes are hand annotations made while reading (listed per item at the end of section 1 so they can be audited). Gaps are reported as band 6 against band 7, with AUC (chance that a random band-7 item scores higher than a random band-6 item; 0.50 means no separation) and a permutation p value. With about 30 items per band, anything with p above 0.10 should be read as "no reliable difference".

## 1. Counts

| | Band 5 | Band 6 | Band 7 |
|---|---|---|---|
| Items | 29 (all CB medium) | 28 (all CB hard) | 33 (all CB hard) |
| "Most nearly mean" (literary) | 1 | 1 | 3 |
| Blank completion | 28 | 27 | 30 |
| Items with phrase options | 10 | 6 | 9 |
| Already in our transcript set | 14 | 13 | 7 |

Template mix (our codes from `satbank/rw/words_in_context.json`, same assignment rule: B6 if any option is multiword, else B5 if a negator frames the blank's sentence, else B1 to B4 by primary clue):

| Template | Band 6 | Band 7 | Change |
|---|---|---|---|
| B1 restatement | 10 | 5 | halves |
| B2 cause or consequence | 3 | 5 | up |
| B3 contrast, received view then finding | 1 | 5 | up sharply |
| B4 example-pinned | 0 | 3 | band 7 only |
| B5 negated frame | 7 | 4 | down |
| B6 phrase options | 6 | 8 | flat |
| M1 underlined word | 1 | 2 | flat |
| M2 underlined phrase or phrase options | 0 | 1 | band 7 only |

No new template is needed: every band-6 and band-7 item fits one of the eight codes. B4 and M2 have band-7 items but no band-6 items. Every template has at least one band-7 item.

Per-item assignment (cb_id: template, key):
- Band 7. B1: 1eeb9bb8 inertia, 4b54bbf0 engendering, 5444db38 exploited, 93665100 repudiates, bce4d106 ubiquity. B2: 0e033f9b prudent, 571cf537 tenuous, 7bc05fa2 buttress, a756aa95 peripheral, e26d23c4 stymie. B3: 177ed7dc surreptitiously, 22a41819 dogmatic, 6c9f1727 notional, a5e747f0 opaque, e8fb0744 negligible. B4: 9ff88d6b counterfactual, a06c434d disparate, dd19befa elasticity. B5: 6017ae31 ambiguity (preclude), d3ca5d59 accessible (little commentary), d5ad34f0 corroborate (fail to), d7807ec8 sanguine (less). B6: 1455b754 inconsequential to, 15daaded concentrated among, 3021d9ef proxies for, 5a97d9cd mediated by, 5ccbfe22 an inducement, 5e57efec independent of, 7afb470b demarcated from, b411eb09 paucity of. M1: 6557f7fc reserve/Constraint, 7f935017 manifest/Perceptible. M2: be94c9fc disputing/Providing resistance to.
- Band 6. B1: 0ed8f24f impending, 10c236ce supposition, 3d658a5a homogeneous, 76e4c51d variable, 79fe7550 foster, 98364791 innocuous, a60b0004 prescribed, adc8ea28 discern, e35d481c surmised, f99847ed inventive. B2: 4ce8e2fa opaque, 83fd3cf4 mitigate, a1ff8ce3 defunct. B3: b35e2fdc unassuming. B5: 4d13a0c0 conjectures, 6c086e70 optimize, aaa3ee7c intersect, bbb77c84 superseded, dba9eaf8 latent, e7d37666 unimportant, f83f0aab diverse. B6: 0462dac3 an exhaustive, 4fa7e50e overshadowed by, 5dce6cab a straightforward, 7b4dde72 manifest in, 994be036 a modest, af4300b0 an arduous. M1: 9b22bf7b determine/Dictate.

Note the drift from our older tiers: d3ca5d59 (our 2.6, filed medium) is now band 7, and adc8ea28 (our 2.27) is band 6. Six of our hard models (3.1, 3.2, 3.10, 3.19, 3.20, 3.23) are band 7; twelve (3.4, 3.8, 3.11 to 3.14, 3.16, 3.17, 3.21, 3.22, 3.24, 3.25) are band 6, and two (3.5, 3.6) are now band 5. Only 3 of our 7 authored hard items list a band-7 model.

## 2. What separates 7 from 6, measured

### The rarity measure

Word rarity is a familiarity rank built from two corpora, both already on this machine:
- `tools/data/freq.txt` (56.7 million words of 1850 to 1928 Gutenberg prose plus a few federal texts; rank = line number). Lookup takes the commonest of the printed form and simple stems (minus -s, -es, -ies, -ed, -ing, -ly).
- A modern correction corpus of 487,000 words: the federal texts in the frequency cache (`~/.cache/satbank/frequency`, NSF, NASA, NOAA and CRS files, 367,000 words) plus every CB passage of the other nine R&W skills. When a form occurs 3 or more times there, its modern rate is converted to the Gutenberg rank that has the same rate, and the commoner of the two ranks is kept. This credits words the old corpus misses (optimize, counterfactual, disparate).
- Unseen words get rank 1,000,000. A phrase option takes the rank of its rarest content word (articles, prepositions and pronouns ignored).

Reported both raw (`freq.txt` only, the measure `spec/rw/words_in_context.md` uses) and corrected.

### Results

| Signal | Band 5 | Band 6 | Band 7 | AUC | p | Separates? |
|---|---|---|---|---|---|---|
| Passage words (mean) | 51.5 | 54.1 | 54.1 | 0.50 | 0.95 | no |
| Words per sentence | 34.0 | 33.7 | 36.4 | 0.55 | 0.52 | no |
| Characters per word | 5.37 | 5.25 | 5.36 | 0.57 | 0.36 | no |
| Long-word rate (9+ letters) | 17.3% | 15.6% | 16.6% | 0.55 | 0.47 | no |
| Passage tokens past rank 10,000 | 15.5% | 14.3% | 16.9% | 0.62 | 0.11 | weak |
| Key rank, raw (median) | 24,847 | 14,646 | 25,158 | 0.67 | 0.02 | yes |
| Key rank, corrected (median) | 15,069 | 8,977 | 18,828 | 0.62 | 0.11 | weak |
| Key past rank 20,000, corrected | 11/29 | 7/28 | 16/33 | 0.62 | 0.07 | weak |
| Mean log rank of all four options, corrected | 4.09 | 3.98 | 4.28 | 0.68 | 0.01 | **yes** |
| Rarest distractor, corrected (geometric mean rank) | 52,000 | 33,000 | 79,000 | 0.69 | 0.01 | **yes** |
| Items with 3 or 4 options past rank 10,000 | 10/29 | 7/28 | 16/33 | | | **yes** |
| Items with all four options past rank 10,000 | 4/29 | 3/28 | 7/33 | | | yes |
| Key is the rarest option | 28% | 25% | 27% | 0.51 | 1.00 | no |
| Key length rank (1 = longest) | 2.48 | 2.61 | 2.52 | 0.48 | 0.78 | no |
| Key is the longest option | 28% | 21% | 30% | 0.54 | 0.56 | no |
| Key content words found in passage | 0% | 3.6% | 1.5% | 0.50 | 0.75 | no (keys never echo the passage) |
| Blank in the last sentence | 86% | 50% | 73% | 0.61 | 0.11 | weak |
| Negator in the blank's sentence | 38% | 46% | 36% | 0.45 | 0.46 | no |
| Needs an extra inference step (steps 2+) | | 17/28 | 24/33 | 0.58 | 0.21 | weak |
| Three-step items | | 1/28 | 4/33 | | | weak |
| Clue in another sentence than the blank | | 12/28 | 10/33 | 0.44 | 0.43 | no (if anything closer at band 7) |
| Distractors that are partly right (per item) | | 0.93 | 0.73 | 0.44 | 0.45 | no (fewer at band 7) |
| Items whose three distractors are all plainly unsupported | | 2/28 | 6/33 | | | weak |
| Concessive frame (While, Though, Although, Despite) around the blank | | 1/28 | 7/33 | 0.59 | 0.06 | yes, small |
| Key used in a transferred or secondary sense | | 2/28 | 8/33 | 0.59 | 0.09 | yes, small |
| Clue itself carries a rare or technical word | | 6/28 | 12/33 | 0.57 | 0.27 | weak |

Reasoning steps follow the source report's section 6 ("items needing an extra inference step"): 1 = the clue paraphrases the key; 2 = one extra move (negation, implication, ranking, an implicit contrast, generalizing from examples); 3 = two moves chained (for example a negated claim plus a reason the claim was plausible).

What the numbers say:
1. **Option-set rarity is the strongest separator, stronger than key rarity.** At band 7 the whole set of four words moves up the rarity scale: in half the items three or four options are past rank 10,000, against a quarter at band 6. The rarest distractor is about twice as rare. The source report predicted key rarity; the key matters (raw AUC 0.67), but once modern academic words are credited it is the set, not the key, that holds up.
2. **Rarity is not monotonic across bands.** Band 6 keys are commoner than band 5 keys on both measures (corrected 8,977 against 15,069). Band 6 is reasoning with plain keys (variable, foster, diverse, a modest, unimportant); band 7 puts the rare words back on top of the reasoning.
3. **At one step, band 7 is purely vocabulary.** Among one-step items the median corrected key rank is 8,204 at band 6 (11 items) and 21,324 at band 7 (9 items): repudiates, paucity of, tenuous, ubiquity, peripheral, opaque, disparate, prudent, an inducement. The three-step band-7 items have ordinary keys (independent of, accessible, corroborate, inconsequential to).
4. **Distractors do not get closer.** Partly right distractors fall from 0.93 to 0.73 per item, and six band-7 items have three plainly unsupported distractors. The band-7 trap is that the student cannot rule out a word they do not know, not that a distractor almost fits.
5. **No signal:** passage length, sentence length, word length, long-word rate, key length, key overlap with the passage, clue distance, negators. Do not use them to aim at band 7.

### Per-item annotations

Hand annotations behind the counts above, for audit. Distractor recipes are in option order, key left out.

| cb_id | band | template | steps | clue (1 same sentence, 2 other sentence, 3 combined) | partly right | distractor recipes | flags |
|---|---|---|---|---|---|---|---|
| 1eeb9bb8 | 7 | B1 | 2 | 2 | 1 | ANT, CONNOT, ANT | transferred sense |
| 4b54bbf0 | 7 | B1 | 2 | 1 | 0 | ASSOC, ASSOC, ASSOC | collocation trap |
| 5444db38 | 7 | B1 | 2 | 1 | 1 | CONNOT, ANT, UNSUP | transferred sense |
| 93665100 | 7 | B1 | 1 | 1 | 1 | ANT, UNSUP, CONNOT | - |
| bce4d106 | 7 | B1 | 1 | 2 | 1 | UNSUP, UNSUP, CONNOT | rare clue |
| 0e033f9b | 7 | B2 | 1 | 1 | 1 | ANT, ANT, CONNOT | - |
| 571cf537 | 7 | B2 | 1 | 1 | 2 | CONNOT, UNSUP, CONNOT | - |
| 7bc05fa2 | 7 | B2 | 2 | 1 | 0 | UNSUP, UNSUP, UNSUP | transferred sense, rare clue |
| a756aa95 | 7 | B2 | 1 | 1 | 0 | UNSUP, UNSUP, UNSUP | collocation trap |
| e26d23c4 | 7 | B2 | 2 | 1 | 0 | ANT, UNSUP, UNSUP | - |
| 177ed7dc | 7 | B3 | 2 | 1 | 1 | UNSUP, UNSUP, CONNOT | concessive |
| 22a41819 | 7 | B3 | 2 | 2 | 2 | UNSUP, ANT-party, ANT-party | rare clue |
| 6c9f1727 | 7 | B3 | 2 | 1 | 1 | UNSUP, CONNOT, ANT | - |
| a5e747f0 | 7 | B3 | 1 | 2 | 0 | ANT, UNSUP, ANT | concessive, transferred sense |
| e8fb0744 | 7 | B3 | 2 | 2 | 1 | UNSUP, UNSUP, ANT-party | - |
| 9ff88d6b | 7 | B4 | 2 | 1 | 2 | UNSUP, CONNOT, CONNOT | - |
| a06c434d | 7 | B4 | 1 | 1 | 0 | ANT, UNSUP, ANT | - |
| dd19befa | 7 | B4 | 2 | 1 | 2 | CONNOT, UNSUP, CONNOT | transferred sense |
| 6017ae31 | 7 | B5 | 2 | 1 | 1 | CONNOT, UNSUP, ANT | - |
| d3ca5d59 | 7 | B5 | 3 | 2 | 0 | ANT, ANT, ANT | - |
| d5ad34f0 | 7 | B5 | 3 | 2 | 0 | UNSUP, UNSUP, UNSUP | rare clue |
| d7807ec8 | 7 | B5 | 2 | 1 | 0 | UNSUP, UNSUP, UNSUP | concessive, rare clue |
| 1455b754 | 7 | B6 | 3 | 3 | 1 | UNSUP, UNSUP, CONNOT | concessive |
| 15daaded | 7 | B6 | 2 | 1 | 0 | UNSUP, UNSUP, UNSUP | concessive, rare clue |
| 3021d9ef | 7 | B6 | 2 | 1 | 0 | UNSUP, UNSUP, UNSUP | concessive, rare clue |
| 5a97d9cd | 7 | B6 | 2 | 1 | 0 | UNSUP, ANT, ANT | rare clue |
| 5ccbfe22 | 7 | B6 | 1 | 2 | 2 | CONNOT, UNSUP, CONNOT | - |
| 5e57efec | 7 | B6 | 3 | 1 | 0 | UNSUP, ANT, UNSUP | rare clue |
| 7afb470b | 7 | B6 | 2 | 1 | 0 | UNSUP, ANT, UNSUP | rare clue |
| b411eb09 | 7 | B6 | 1 | 1 | 0 | UNSUP, ANT, UNSUP | concessive |
| 6557f7fc | 7 | M1 | 2 | 2 | 2 | SENSE, CONNOT, SENSE | transferred sense, rare clue |
| 7f935017 | 7 | M1 | 2 | 1 | 1 | SENSE, UNSUP, CONNOT | transferred sense, rare clue |
| be94c9fc | 7 | M2 | 2 | 1 | 1 | SENSE, SENSE, CONNOT | transferred sense |
| 0ed8f24f | 6 | B1 | 1 | 2 | 0 | ANT, UNSUP, UNSUP | rare clue |
| 10c236ce | 6 | B1 | 2 | 1 | 2 | CONNOT, CONNOT, UNSUP | rare clue |
| 3d658a5a | 6 | B1 | 2 | 1 | 1 | CONNOT, UNSUP, ANT | rare clue |
| 76e4c51d | 6 | B1 | 1 | 1 | 1 | UNSUP, CONNOT, ANT | - |
| 79fe7550 | 6 | B1 | 1 | 2 | 0 | UNSUP, UNSUP, ANT | - |
| 98364791 | 6 | B1 | 1 | 1 | 0 | UNSUP, UNSUP, UNSUP | concessive |
| a60b0004 | 6 | B1 | 1 | 2 | 1 | UNSUP, UNSUP, CONNOT | - |
| adc8ea28 | 6 | B1 | 1 | 1 | 1 | UNSUP, UNSUP, CONNOT | - |
| e35d481c | 6 | B1 | 1 | 1 | 1 | CONNOT, ANT-party, UNSUP | - |
| f99847ed | 6 | B1 | 1 | 1 | 0 | ANT, UNSUP, UNSUP | - |
| 4ce8e2fa | 6 | B2 | 2 | 2 | 0 | UNSUP, UNSUP, ANT | transferred sense |
| 83fd3cf4 | 6 | B2 | 2 | 2 | 0 | UNSUP, UNSUP, ANT | - |
| a1ff8ce3 | 6 | B2 | 1 | 1 | 1 | CONNOT, ANT, UNSUP | - |
| b35e2fdc | 6 | B3 | 2 | 1 | 1 | ANT-party, UNSUP, ANT | - |
| 4d13a0c0 | 6 | B5 | 1 | 2 | 2 | CONNOT, CONNOT, UNSUP | - |
| 6c086e70 | 6 | B5 | 3 | 2 | 1 | UNSUP, CONNOT, UNSUP | - |
| aaa3ee7c | 6 | B5 | 2 | 2 | 0 | UNSUP, UNSUP, ANT | - |
| bbb77c84 | 6 | B5 | 2 | 1 | 2 | CONNOT, CONNOT, UNSUP | rare clue |
| dba9eaf8 | 6 | B5 | 2 | 1 | 0 | UNSUP, UNSUP, ANT | rare clue |
| e7d37666 | 6 | B5 | 2 | 1 | 2 | ANT-negflip, UNSUP, ANT-negflip | - |
| f83f0aab | 6 | B5 | 2 | 2 | 1 | ASSOC, UNSUP, CONNOT | - |
| 0462dac3 | 6 | B6 | 2 | 1 | 3 | ANT-negflip, ANT-negflip, ANT-negflip | - |
| 4fa7e50e | 6 | B6 | 2 | 2 | 1 | UNSUP, UNSUP, CONNOT | - |
| 5dce6cab | 6 | B6 | 2 | 1 | 1 | CONNOT, UNSUP, UNSUP | - |
| 7b4dde72 | 6 | B6 | 2 | 1 | 0 | UNSUP, UNSUP, UNSUP | rare clue |
| 994be036 | 6 | B6 | 2 | 2 | 0 | UNSUP, ASSOC, UNSUP | - |
| af4300b0 | 6 | B6 | 1 | 2 | 1 | ANT, CONNOT, UNSUP | - |
| 9b22bf7b | 6 | M1 | 2 | 1 | 3 | SENSE, SENSE, SENSE | transferred sense |

## 3. What separates 7 from 6, read

The concrete moves, with examples:

1. **Every option is a word a strong 11th grader may not own.** b411eb09 sets paucity of against profusion of and verisimilitude in; d7807ec8 offers sanguine, recalcitrant, misanthropic. The logic is one step ("though there have been many studies"), but a student who knows neither paucity nor profusion cannot use it. Band-6 one-step items use keys like foster, variable, inventive.
2. **A familiar word in a transferred sense.** elasticity of a swan's "familial structure", buttress "his right to hold the throne", inertia for subscribers who never cancel, exploited for "made productive use of", opaque prose. In 4b54bbf0 "exploiting demand" is a wrong answer; in 5444db38 "exploited" is the key. The student must hold the secondary sense against the everyday one.
3. **The clue itself is a rare word.** bce4d106 restates ubiquity with "a plethora of beads"; 6557f7fc pins Constraint with "unexpectedly reticent". The paraphrase only helps a student who knows the clue word.
4. **A concessive frame that hides the direction.** 1455b754: "recent scholarship has undermined claims that the works ... were ______ other Muslim philosophers", followed by a fact that would have supported those claims. The student must undo "undermined claims that" and see the second clause as the reason the claim was tempting. 3021d9ef works the same way ("make it tempting to treat ... as ______").
5. **The counterintuitive key.** d3ca5d59: paintings "have elicited little commentary" because they seem so ______; critics prefer art that is "cryptic or overtly challenging". All three distractors (innovative, subversive, profound) are what one expects to say of praised art, and the key is the plain accessible. The band-6 negation items (by no means unimportant, unlikely to be superseded) state the frame outright.
6. **Technical paraphrase dense enough to block the clue.** 7afb470b ("obligate nature", "euryhaline (able to tolerate high salinity)"), 15daaded ("deep-bodied physical forms ... highly dispersed across the morphological spectrum"). The key is the opposite of dispersed, but the student first has to parse the gloss.
7. **Received view, then the finding, with the blank in the received view.** e8fb0744 "challenging the accepted view that ... female participation in hunting was ______". The trap commonplace describes the finding, not the view. Band 6 has this once (aaa3ee7c, intersect), band 7 five times with B3.
8. **Long interruption between subject and blank.** 177ed7dc puts a 30-word appositive between the subject and "were originally distributed ______", and the clue words (underground, anonymously) sit inside the interruption.

What does not change: the blank still sits in a two-sentence informational paragraph, the clue is usually in the same sentence (after a colon, since, as, or a contrast), and the key never repeats a passage word.

## 4. Distractor recipes at band 7

Recipe tags from `spec/rw/words_in_context.md` section 5. Wrong party (the trait of the other side of a contrast) and negation flip (the natural positive word under a negated frame) are sub-recipes of reversal, counted separately here.

| Recipe | Band 6 (84 distractors) | Band 7 (99) |
|---|---|---|
| Plausible but unsupported (UNSUP) | 43 (51%) | 47 (47%) |
| Reversal (ANT), plain or direction | 12 | 21 |
| Reversal: trait of the wrong party | 2 | 3 |
| Reversal: negation flip | 5 | 0 |
| Wrong nuance, degree or agent (CONNOT) | 17 (20%) | 20 (20%) |
| Another sense of the target (SENSE) | 3 | 5 |
| Topic echo (ASSOC) | 2 | 3 |

- **The mix barely moves.** UNSUP stays the backbone, CONNOT stays at a fifth. What changes is the register of the UNSUP words: at band 6 they are often common (require, remember, deceptive, novel), at band 7 they are rare and academic (desultory, verisimilitude in, contrivances of, recalcitrant), so a student cannot reject them by meaning.
- **Negation flips are band 6 only.** Band 6 uses the natural positive word under "by no means" or "unlikely to ever have" (substantial, appropriate; imaginative, superficial, questionable). Band-7 negated frames use reversals of the implicit logic instead (d3ca5d59: innovative, subversive, profound).
- **Band 7 only: collocation traps.** In a756aa95 every distractor makes a stock phrase with the slot's noun (approximate location, concealed location, unobtrusive location); in 4b54bbf0 every distractor is a market verb that pairs with demand (exploiting, monetizing, appraising) but has the wrong agent.
- **How the hardest distractor is built at band 7**, by frequency:
  - a near synonym from the key's field that fails on one feature (disingenuously against surreptitiously: insincere, not secret; spurious against notional: false, not unproven; recants against repudiates: applies to one's own earlier belief; retrospective and analogical against counterfactual; cohesion and reciprocity against elasticity; fecundity against ubiquity);
  - in meaning items, a real sense of the target (Modesty and Composure for reserve; Realized for manifest; Arguing about for disputing) plus one topic word (Dwindling for a setting sun);
  - a word naming the earlier, misleading half of the passage (inconspicuousness, built from "too faint for detection", against ambiguity).

## 5. Band-7 writing recipe

Settings common to every template:
- Choose the key and all three distractors past corrected rank 10,000, at least two past 20,000 (section 6 gives the check). Do not use a rare key with common distractors: that is the band-5 pattern.
- Keep the passage at 40 to 70 words and one to two sentences; length is not the lever.
- Make the clue paraphrase a level more abstract than the key, or put a rare word in the clue itself (plethora for ubiquity, reticent for constraint).
- At least one distractor must be a near synonym that fails on a single feature (agent, degree, secrecy against insincerity, unproven against false). The other two can be plainly unsupported if they are rare.
- One-step logic is fine only when the vocabulary carries the item; a common key needs a three-step chain (see B5 and B6).

Per template, what to change from a band-6 version:
- **B1 restatement.** Band 6: "this rejection is evident" style clue with a common key (variable, foster, inventive). Band 7: same clue structure but a rare key (repudiates, ubiquity) or a familiar word in a secondary sense (inertia, exploited), and the clue phrased in a different register from the key ("passivity in the interim" for inertia). Add one near-synonym distractor (recants for repudiates).
- **B2 cause or consequence.** Put the cause in a since, as or by clause in the same sentence ("as it fails to account for several recent archaeological discoveries"). Key an evaluative or figurative word (tenuous, prudent, buttress, stymie, peripheral). Distractors from the same evaluative family with the wrong ground (unoriginal, disorienting for tenuous) or stock collocates of the slot noun.
- **B3 contrast, received view then finding.** Band 7 wants this template more than any other. Use While, Though, Despite or "Until recently ... but" and leave the direction implicit (dogmatic is never contrasted with an antonym in the text; Johnson's "self-effacement" is). Put the blank on the view being challenged or on the side that is not described, and offer the described side's trait as a reversal (commonplace, unpretentious).
- **B4 example-pinned.** Give a colon and a list or a described experiment, and key the abstract category the examples instantiate (counterfactual from a "would have gone if" description; disparate from three contrasting styles; elasticity from fostering and male-male pairs). Distractors: other abstract categories the examples half fit (retrospective, analogical; cohesion, reciprocity).
- **B5 negated frame.** Band-6 B5 states the negation plainly ("by no means", "unlikely to be"). Band 7 hides it in a verb or comparative (preclude, fail to, less ______ observers countered) or makes the key the counterintuitive one that a negated fact implies (little commentary because the paintings seem accessible). Drop the negation-flip distractors; use reversals of the implied logic.
- **B6 phrase options.** Use word + preposition keys with academic heads (proxies for, mediated by, demarcated from, inconsequential to, paucity of), or a/an + noun (an inducement). For a three-step version with a common key, make the consequence the only clue (independent of: costs that do not scale with gift size make large donors cheaper). A concessive "although X makes it tempting to treat A as ______ B" frame suits this template.
- **M1 underlined word.** Use dense literary prose (Wharton, Beckett, Baldwin) with a common target in a sense that is not its first one (reserve as restraint, manifest as perceptible). Two distractors are real senses of the target that fit the sentence loosely, one is a topic word from the scene. Key a word that is itself mid-frequency (Constraint, Perceptible), not a plain everyday synonym.
- **M2 underlined phrase or phrase options.** Paraphrase options sharing a frame ("Providing resistance to", "Asserting possession of"), with the target used figuratively (crowds disputing a taxi's passage). Every distractor is a real sense of the target.

## 6. Checks

Automatic, using only signals that separated in section 2:

1. **Option-set rarity (best single check).** Compute the corrected rank of each option's rarest content word. Pass for band 7 when at least 3 of 4 options are past rank 10,000. Hits 16 of 33 band-7 items and 7 of 28 band-6 items (and 10 of 29 band 5). Equivalent continuous form: mean log10 rank of the four options at least 4.2 (band 6 mean 3.98, band 7 4.28; AUC 0.68). Reliability: moderate; it flags rarity, not difficulty of reasoning.
2. **Rarest distractor.** At least one distractor past rank 50,000 (or unseen in both corpora). AUC 0.69. Use with check 1, not alone.
3. **Combined gate.** Corrected key rank above 20,000, or three-step reasoning, or 3 of 4 options past rank 10,000. Passes 22 of 33 band-7 items and 10 of 28 band-6 items (67% against 36%). This is the recommended gate; expect about one band-6-like draft in three to slip through, so pair it with check 5.
4. **Band-5 guard.** A rare key with commoner distractors (key the rarest option and two or more distractors under rank 10,000) is the band-5 pattern; reject it as a band-7 draft.

Agent-run:

5. **Reasoning and frame annotation.** An agent labels steps (1, 2 or 3), concessive frame (yes or no) and transferred-sense key (yes or no). Band 7 had a concessive frame in 7 of 33 items (band 6: 1 of 28) and a transferred sense in 8 of 33 (band 6: 2 of 28); steps 2+ in 24 of 33 (band 6: 17 of 28). Use these as "at least one present" when check 1 fails. Weak to moderate.
6. **Unknown-word solve.** Have a solver model list which of the four options a typical 1400-scorer would not know. A band-7 draft should have at least two. This is an untested proxy for check 1; use it only to catch modern words the corpora miss.

Do not gate on: passage length, words per sentence, characters per word, long-word rate, key length rank, key-passage overlap, clue distance, negators. None separated band 7 from band 6. A blind solve by a strong model also does not tell 6 from 7 (it knows every word); it remains the correctness check only.
