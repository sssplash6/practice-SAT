# Command of Evidence: what makes a band-7 item

Source: `material/rw/cb_api/command_of_evidence.json` (277 official items with CB's rationale). Bands 5, 6 and 7 hold 48, 59 and 62 items. Only 28 band-6 and 23 band-7 items are in our transcript set, so 70 of the 121 were new to us. All 121 were read with CB's rationale and hand-coded. Graphs come as CB's bullet-list descriptions (values included), so every figure item could be checked. The numbers come from a scratch script over the CB file (register measures reuse `tools/check_rw.py`, rarity uses `tools/data/freq.txt`).

The skill is two different tasks, so everything below is split:
- **Textual**: T1 hypothetical finding, T2 literary quotation, T3 quotation from a person. 29 / 33 / 38 items at bands 5 / 6 / 7.
- **Quantitative**: Q1 data completion, Q2 data description. 19 / 26 / 24 items at bands 5 / 6 / 7.

**AUC** is the chance that a random band-7 item scores higher than a random band-6 item (ties count half). 50% means no separation; 70% or more (or 30% or less) is a real gap at these sizes (one standard error is about 7 points). Hand codes were made by one reader who knew the band, so treat them as a careful reading. CB's rationale lengths are an independent cross-check.

## 1. Counts

Textual (template codes from `satbank/rw/command_of_evidence__b.json`, plus one new):

| template | band 6 | band 7 |
|---|---|---|
| T1_single hypothetical finding, one claim | 17 | 21 |
| T1_compete finding that discriminates rival explanations | 3 | 8 |
| **T1_account** (new): "which finding would best account for the discrepancy / observation" | 0 | 2 |
| T2_lit_quote literary quotation | 7 | 3 |
| T3_person_quote quotation from a participant, critic or scholar | 6 | 4 |
| polarity: support / weaken or challenge / illustrate / account | 19 / 4 / 10 / 0 | 26 / 6 / 4 / 2 |

Quotation items fall from 13 of 33 at band 6 (14 of 29 at band 5) to 7 of 38 at band 7. Band 7 textual is mostly "Which finding, if true, ...".

Quantitative (codes from `satbank/rw/command_of_evidence__a.json`, plus Q1_P8):

| template | band 6 | band 7 |
|---|---|---|
| Q1_P1 lookup / Q1_P3 pairwise / Q1_P4 trend | 2 / 2 / 1 | 0 / 0 / 0 |
| Q1_P2 extreme (after a filter) | 0 | 1 |
| Q1_P5 condition vs control | 4 | 1 |
| Q1_P67 passage criterion combined with the display | 3 | 6 |
| **Q1_P8** quantified or two-part completion (new for Q1) | 1 | 2 |
| Q2_P4 trend | 2 | 2 |
| Q2_P5 condition vs control | 1 | 5 |
| Q2_P8 multipart / quantifier | 6 / 4 | 6 / 1 |
| Q1 / Q2 totals | 13 / 13 | 10 / 14 |
| tables / graphs | 15 / 11 | 10 / 14 |

At band 7 the simple Q1 patterns (lookup, pairwise, trend) disappear. Completions that need a passage relation (P67) double.

## 2. What separates 7 from 6, measured

Hand-coded measures:
- **Steps (textual)**: 1 = the finding names the claim's own variables directly; 2 = it needs the right comparison group, or one bridge from the claim's wording to an observable; 3 = the key supplies a premise or mechanism the passage does not state, or must discriminate rival explanations through such a bridge.
- **Steps (quantitative)**: the number of data operations needed to verify the key (read, filter, compare, check every row, interpolate), plus one for translating the measure through a passage relation.
- **Proxy (quantitative)**: the display's measure must be translated through a relation stated in the passage before it bears on the claim (an inverse correlation, a ratio, a threshold, a definition of the condition labels).
- **Partly right**: textual distractors labelled OPP, HALF, SUBJ or TRAP (they engage the claim's own variable and fail one requirement); quantitative distractors that are accurate readings of the display but insufficient (IRREL, PART, HALF, CONTRA).
- **Clue distance**: for this skill it is the "passage words" and "steps" rows. The needed fact (a definition, a date, a measure) sits in an earlier sentence, so it travels with passage length and steps; no separate count was kept.

### Textual

| measure | band 5 median | band 6 median (mean) | band 7 median (mean) | AUC 7>6 | verdict |
|---|---|---|---|---|---|
| passage words | 68 | 86 (79) | 104.5 (97) | 74% | separates; T1 only 94.5 vs 105, 71%; 100+ words in 26 of 38 vs 9 of 33 |
| stem words | 11 | 11 | 14.5 | 70.5% | separates; T1 only 74%: band-7 stems name the study and whose claim is tested |
| reasoning steps (hand) | | 2 (1.88) | 3 (2.61) | 80% | strongest: 3 steps in 23 of 38 vs 3 of 33 |
| items with a TRAP distractor (hand) | | 6 of 33 | 18 of 38 | | separates as a rate |
| partly-right distractors (hand) | | 2 (1.55) | 2 (1.74) | 56% | no |
| claim components the key must match (hand) | | 2 (1.55) | 2 (1.63) | 52% | no |
| CB rationale words for key / per distractor | 95 / 43 | 103 / 42 | 146 / 67 | 66% / 65% | weak |
| words per sentence | 23 | 27.5 | 29.5 | 57% | no |
| chars per word | 4.90 | 5.09 | 5.25 | 60% | no |
| long-word rate (9+ letters) | 12% | 15% | 15% | 52% | no |
| rare-word rate (rank beyond 10,000) | 18% | 20% | 21% | 55% | no |
| option length, words | 23.8 | 25.8 | 25.3 | 50% | no |
| key length rank / key-to-distractor length | 2 / 1.03 | 2 / 1.03 | 2 / 0.99 | 49% / 49% | no |
| key overlap / best distractor overlap with passage | 0.29 / 0.44 | 0.28 / 0.50 | 0.36 / 0.56 | 55% / 55% | no |
| options with a negation or contrast word (mean) | 0.86 | 1.15 | 1.55 | 60% | no |
| key hedged | 14% | 21% | 16% | 47% | no |

### Quantitative

| measure | band 5 median | band 6 median (mean) | band 7 median (mean) | AUC 7>6 | verdict |
|---|---|---|---|---|---|
| passage words (prose, display removed) | 79 | 92 (86) | 105.5 (101) | 73% | separates; Q2 only 91 vs 106, 80%; 100+ words in 15 of 24 vs 7 of 26 |
| option length, words | 17.5 | 21.9 | 28.1 | 69% | separates for Q1 (16.8 vs 29.3, 77%), not for Q2 (27.5 vs 27.4) |
| CB rationale words for key | 125 | 139.5 | 187.5 | 72% | separates; Q1 only 132 vs 207.5, 89% |
| reasoning steps (hand) | | 2 (2.31) | 3 (2.92) | 70% | separates: 3+ in 17 of 24 vs 11 of 26; 4 in 5 vs 0 |
| proxy needed (hand) | | 6 of 26 | 13 of 24 | 66% | separates as a rate |
| options with a negation or contrast word (mean) | 1.32 | 1.15 | 1.96 | 66% | weak |
| data points in the display | 12 | 12 | 10 | 39% | no; band-7 displays are not bigger |
| series per display (3 or more) | 13 of 19 | 15 of 26 | 16 of 24 | 48% | no |
| graphs rather than tables | 8 of 19 | 11 of 26 | 14 of 24 | | weak |
| partly-right (accurate but insufficient) distractors | | 1.5 (1.50) | 1 (1.29) | 45% | no, slightly fewer at band 7 |
| words per sentence / chars per word / long words | 24.7 / 5.16 / 16% | 27.1 / 5.32 / 15% | 28.5 / 5.41 / 15% | 53% / 53% / 51% | no |
| rare-word rate / mean log rank | 20% / 2.74 | 22% / 2.78 | 25% / 2.94 | 56% / 62% | no / weak |
| key overlap, key length rank | 0.50, 2 | 0.52, 2 | 0.53, 2 | 49%, 49% | no |

Plainly:
- Vocabulary, sentence length, word overlap and key position do not separate band 7 from band 6 in either half. Neither does display size.
- **Textual**: longer passages, longer and more specific stems, and above all keys that bring in a missing premise. Distractors are not more often partly right; they are more often logical traps.
- **Quantitative**: longer passages, a passage relation needed to read the display, more operations, and (for Q1) long compound options.

## 3. What separates 7 from 6, read

### Textual

1. **The key supplies the missing premise.** At band 6 the key usually restates the claim's variable in observable form ("Participants who had been looking at the trees helped ... pick up significantly more pens"). At band 7 the key adds a fact the passage never mentions, which completes the argument:
   - ALSOL: travel cost "high but largely independent of the number of goods they bring";
   - archaeologists' other tasks "that only human experts can do";
   - PCFG whales forage in kelp beds "inaccessible to whales as large as those" in the main group;
   - Etta-Nkwelle: African countries' unions "set individual foreign-currency accumulation policies".
   The student must see why that fact closes the gap.

2. **The comparison must discriminate.** Sevilla and Townsend's moderation claim needs a difference of differences: the key compares spaced against unspaced within each store, then across stores. Two distractors compare stores at one spacing level. Cuaya's dogs: the key pairs head length with speech against nonspeech; the passage never mentions head shape. In Washington and Mullainathan, voters must be compared with the too-young control group: "significantly more polarized ... than did subjects who were not old enough".

3. **Rival explanations and alternative routes.** Band 7 has 8 T1_compete items (band 6: 3). The key is often an unexpected route:
   - recipients withdraw "the entire amount in physical money" (the money-form explanation collapses);
   - migration instead of trade (Óc Eo);
   - fossils that "cannot be conclusively identified as ctenophores either".

4. **Stems narrow and name the claimant.** 5b74feb9 asks for a finding from Washington and Mullainathan's study that "would most directly weaken the claim made by people who favor the traditional view". The student must keep apart whose study it is and whose claim is tested. 10 of 38 band-7 textual stems narrow the finding (from the study, about the basin), against 4 of 33.

5. **Literary and person quotations at band 7.**
   - Literary items rest on hard language and near emotions, not on more half-matches: Richard II's "insinuate, flatter, bow, and bend my knee"; Lear's "Beat at this gate that let thy folly in"; Moore reading poetry "with a perfect contempt for it".
   - Person quotations run 40 to 55 words and are arguments themselves. In ca9dc00f the claim sits inside the author's rebuttal of an "overly object-focused" view.

### Quantitative

1. **The display must be read through a passage relation (proxy).** 13 of 24 band-7 items, 6 of 26 band-6.
   - The Mn/Ca ratio "inversely correlates with ocean oxygenation levels".
   - Fiber diameter maps to softness.
   - Fly types A and B are the ones with that gene *silenced*.
   - GDP's share of urban expansion rises as governments become more efficient.
   - Processing with inputs requires capital.
   - Payload capacity is holding force (given in the text) divided by weight (given in the graph).
   Misapplying the relation produces the band-7 direction errors.

2. **The blank concludes about the world, not about the data.** Examples: governments in Region 1 "experienced declines in efficiency"; worker and drone cells "probably closer in size" in western honeybee hives; "DptB may have developed as a specific defense". The student reads the data, applies the passage mechanism backwards, and names the cause.

3. **The right comparison must be picked out of many accurate ones.**
   - Packer's leave study: only the post-leave tests and only 2–4 days against 1–5 weeks count. The first test was taken before leave, and the no-leave group is beside the point.
   - Ibáñez's sugar maples: the key crosses conditions ("with nitrogen under moderate change exceeded growth without nitrogen under the current climate"). All three distractors are accurate comparisons of the wrong cells.

4. **Interpolation and bounds.** In 43f4013a, the PFBV ratio 0.709028 falls between two table rows. Its age must be placed inside the Hh4 bounds that only the passage gives (6 Ma to 4.75 Ma).

5. **Q1 options become long compound clauses** (median 29 words against 17). Value-only options ("6.1 days, and its rotational period is also 6.1 days.") vanish at band 7, except one filter-then-extreme item whose trap is the earliest row of the wrong data type.

6. **Not harder to read.** Band-7 displays have no more data points or series than band-6 ones. The difficulty is in what the numbers mean, not in finding them.

## 4. Distractor recipes at band 7

Labels follow `spec/rw/command_of_evidence.md` section 5: OFF off-target, SUBJ wrong subject, OPP opposite, HALF half-match, LURE keyword lure, TRAP other logical trap, GEN restates context; INACC inaccurate, WGRP wrong group, IRREL accurate but irrelevant, PART partial, WDIR wrong direction, OUTS outside the data, CONTRA contradicts the claim.

Textual (99 band-6 and 114 band-7 wrong options):

| recipe | band 6 | band 7 |
|---|---|---|
| OFF | 44 | 42 |
| TRAP | 6 | 27 |
| OPP | 18 | 21 |
| HALF | 15 | 13 |
| SUBJ | 12 | 5 |
| LURE, GEN | 4 | 6 |

TRAP is the band-7 recipe: 18 of 38 band-7 items have one, against 6 of 33. Its forms:
- consistent with both explanations (0240d11c B, similar elements from region to region; 0c622cfb D, channels from water or lava);
- a mismatched comparison (09775cbf C and D, 4a07be59 C);
- the wrong time window (4d38c2ea A, B, D: dated before, range expanded after, present-day artists);
- a factor that affects both groups equally (8e22efd9 B and D, cost increases that hit both kinds of plant);
- a comparison with no difference (5b74feb9 D, df91532e A and C, "just as likely").

SUBJ (wrong entity) is a band-6 recipe and fades. HALF stays, but at band 7 it appears in claims with three components (3a489e1e: a musical tradition, from beyond Chile, in the movement's foundation).

Quantitative (78 band-6 and 72 band-7 wrong options):

| recipe | band 6 | band 7 |
|---|---|---|
| IRREL | 27 | 21 |
| INACC | 22 | 19 |
| OUTS | 6 | 11 |
| WGRP | 7 | 5 |
| PART | 7 | 5 |
| WDIR | 4 | 6 |
| CONTRA, HALF | 5 | 5 |

The mix barely moves. OUTS rises: claims the display cannot settle (actual ticket cost, individual countries within a region, flies with both genes active, holding force taken from the graph). At band 7, WDIR usually comes from applying the proxy the wrong way: 3233c162 A says oxygenation increased where the Mn/Ca ratio rose, and cbdd5287 A credits DptA with the defense because type A flies survived.

How the hardest distractor is built:
- **Textual**: a finding that looks like a test of the claim but cannot decide it. 09775cbf D compares the two stores at each spacing level and never takes the within-store difference. 4a07be59 D has the right anatomical comparison on the wrong contrast (familiar against unfamiliar language).
- **Quantitative**: an accurate reading of the wrong cells, in a long compound sentence of the same shape as the key (627d93e3 A to C), or the proxy turned the wrong way.

## 5. Band-7 writing recipe

General settings:
- Passage 100 to 120 prose words. The fact the key depends on (a definition, a measure, a date, a mechanism, a passage number) goes in an earlier sentence, not the claim sentence.
- Do not raise vocabulary, sentence length or display size; none of them moves the band.

### Textual

**T1_single [21 at band 7].** Change from band 6:
- Make the claim need a missing premise (a cost structure, a mediator, an access mechanism), an interaction (a difference of differences), or a hidden variable the passage only implies (head shape, late-night activity for "electric lighting").
- Write the key as the observation that supplies it, in one or two clauses.
- Stem: name the study and the claimant. "Which finding from X's study, if true, would most directly support/weaken the claim made by Y?" Aim for 13 or more words.
- Distractors: one OPP (the rival's prediction or the reversed direction); one or two TRAP (consistent with both, mismatched comparison, wrong time window, affects both groups equally, no-difference); at most one OFF.

**T1_compete [8].**
- Two named views; the key is evidence only one predicts, often through an unexpected route (parasites carrying genes between species, withdrawal as cash, migration instead of trade, preservation too poor to tell).
- Use the weaken polarity in about a third.
- Distractors: one fits the rival (OPP), one fits both (TRAP), one is an irrelevant property of the same objects.

**T1_account [2]** (new).
- Stem: "which finding, if true, would best account for the discrepancy" or "most coherently and directly accounts for the observation".
- Passage: a pattern that differs between two groups or grows under a condition.
- Key: a difference that acts on only one group through the stated mechanism.
- Distractors: differences that act on both groups equally (TRAP), a restatement of a known fact (GEN), group differences on an off-target variable.

**T2_lit_quote [3].**
- Pre-1929 verse or drama, or an early modernist poem. The claim uses an indirect verb ("intimates that he is not entirely ready", "highlights an ambivalence", "expresses regret").
- Distractors: the same speaker in a nearby emotion (grief, loss of identity, defiance) and one with the opposite stance.
- Quotations verified verbatim, as in the base blueprint.

**T3_person_quote [4].**
- Quotations of 40 to 55 words that argue. The claim sits inside the author's rebuttal, or the stem asks which quotation challenges an underlined claim.
- Distractors: a quotation that sides with the view the text rejects (OPP), a reconciliation that misses the claim (TRAP), a half-match.

### Quantitative

**Q1_P67 passage criterion [6].**
- The passage states the relation needed to read the display: an inverse proxy, period bounds, which gene a label silences, a mechanism linking a share to a cause.
- The blank asks for a conclusion about the world (efficiency declined; cells closer in size; a gene is a specific defense) or an interpolated placement.
- Options are compound clauses of 25 to 35 words.
- Distractors: the proxy applied the wrong way (WDIR), a claim the display cannot settle (OUTS), a compound with one false clause (INACC).

**Q2_P5 condition vs control [5].**
- Build in a design wrinkle: a test taken before treatment, a third condition (no leave; whitefly-free air), or two outcome measures where only one bears on the claim (helpfulness against product attitude).
- Key: the right pair at the right time, often with a quantifier ("in both the second and third test administrations").
- Distractors: accurate comparisons with the wrong group, time or measure (IRREL x2), plus one false reading.

**Q2_P8 multipart [6].**
- An interaction or a cross-cell comparison (moderate-with-nitrogen against current-without), or a passage number combined with the display (holding force from the text, weight from the graph).
- Distractors: accurate comparisons of the wrong cells, all in the key's sentence frame.

**Q2_P4 trend [2].**
- The trend matters only through the passage (inputs require capital; delta 15-N tracks wastewater). Key: the contrast in rates, or the fluctuation that shows "intermittently".
- Distractors: levels instead of changes, constancy, a single misread cell.

**Q1_P8 [2]**: a quantified completion ("multiple lizard species move at an average of less than 90% ... while escaping") or a two-part one (heterogeneity plus the effect of the value prompt in both studies).

**Q1_P2 [1], Q1_P5 [1], Q2_P8 quantifier [1]**: band 7 only with a trap built in: a filter (spectroscopy only), a surprise relative to the stated expectation (the non-host plant gained mass), or "every region plus the overall majority".

**No band-7 items**: Q1_P1 lookup, Q1_P3 pairwise, Q1_P4 trend. Do not aim them at band 7.

## 6. Checks

Only signals that separated in section 2. Reliability is the AUC on the official items, or the band rates.

### Textual

Automatic:
1. **Passage length** 100 prose words or more: 26 of 38 band-7 items against 9 of 33 band-6 (AUC 74%).
2. **Stem length and specificity**: 13 words or more, naming the study or the claimant (25 of 38 against 12 of 33; AUC 70.5%, 74% within T1).
3. **Template**: a T1 finding item rather than a quotation item (31 of 38 against 20 of 33). This is a mix target, not a gate.
4. **Not used**: option length, vocabulary, overlap, key length, hedges.

Agent-run:
5. **Steps.** Ask the reviewer which premise the key adds that the passage does not state, or which rival it rules out. Band 7 needs a real answer: 3 steps in 23 of 38 band-7 items, 3 of 33 band-6 (AUC 80%, the strongest signal in this skill, but coded unblinded).
6. **TRAP present.** Label each distractor; band 7 should have at least one finding that looks like a test but cannot decide the claim (18 of 38 against 6 of 33). Reject a band-7 draft whose wrong options are all OFF or SUBJ.
7. **Discrimination check.** For T1_compete and weaken items, the reviewer states what each rival predicts for the key's finding; the key must split them and the TRAP must not.

### Quantitative

Automatic:
8. **Passage length** 100 prose words or more, display excluded: 15 of 24 against 7 of 26 (AUC 73%; Q2 80%).
9. **Q1 option length**: mean of 25 words or more (6 of 10 band-7 Q1 items, 2 of 13 band-6; AUC 77%). Reject value-only Q1 options for band 7.
10. **Predicate engine** (from the base blueprint): exactly one option true and sufficient. For band 7, also require at least two distractors that are evaluable and accurate for some cells (IRREL, PART) or false only through the proxy (WDIR).
11. **Not used**: display size, number of series, vocabulary, sentence length.

Agent-run:
12. **Proxy.** Ask: "What relation in the passage must be applied to the display before the key follows?" 13 of 24 band-7 items have one, against 6 of 26.
13. **Operations count.** List the reads, filters and comparisons needed to verify the key. Band 7: three or more (17 of 24 against 11 of 26; four in 5 against 0).
14. **Justification length (experimental).** CB needs a median 188 words to justify a band-7 key, against 140 at band 6, and 208 against 132 for Q1 (AUC 89%). A reviewer's CB-style justification is a usable proxy once calibrated on official items of each band.

A textual draft that passes 1, 2, 5 and 6, or a quantitative draft that passes 8, 10, 12 and 13 (plus 9 for Q1), matches band 7 on every signal that separated the official items.
