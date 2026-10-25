# Inferences (Information and Ideas): analysis of the 71 official items

Source: `material/rw/transcripts/inferences.json` (corrected against the images), key `material/rw/keys/inferences.json`, images `material/rw/items/inferences/<tier>/<n>.jpg`. All counts below were computed with Python from the corrected transcript; the structural labels (sections 2, 5 and 7) are my hand annotation of every item, tallied with Python.

**Data notes.**
- The tier 3 key is unusable: `Inferences 3~Key.pdf` has no visible Answer column, and its text layer holds numbers such as 519, 372 and 421 that track the item image heights, not letters. All 34 hard answer letters in the transcript were therefore solved by reading the items (each item's `notes` says so). Every one of them has a single defensible answer, but they are not official.
- 61 items were checked against the image: the 52 flagged by the brief's rules, item 2.20 (blank glued to "that"), and the 8 unflagged hard items (answer letters). 45 drafts had lost the blank because it wrapped onto its own line. In 3 items (3.19, 3.21, 3.22) the passage tail and the stem had swapped places, and in 4 items (3.19 to 3.22) the options had been cut at the wrong line because these four print the letter beside the second line of a two-line option. Other fixes: names with diacritics (María, João, Dančák, Anikó), en dashes in 5 date ranges, "i.e.", "bellulus", "code—by", two stray paragraph breaks, and straight quotes changed to curly ones.

## 1. Snapshot

| | easy | medium | hard | all |
|---|---|---|---|---|
| items | 15 | 22 | 34 | 71 |
| key A / B / C / D | 5 / 5 / 3 / 2 | 6 / 8 / 3 / 5 | 8 / 12 / 7 / 7 (solved) | 19 / 25 / 13 / 14 |
| passage words min / median / max | 60 / 93 / 129 | 48 / 95.5 / 122 | 64 / 96 / 123 | 48 / 95 / 129 |
| sentences min / median / max | 3 / 6 / 9 | 3 / 4 / 8 | 2 / 4 / 6 | |
| mean words per sentence | 17.5 | 23.6 | 27.3 | |

Passage length does not separate the tiers. Sentence length does: hard passages say the same amount in fewer, longer sentences.

**Stem.** One wording only: "Which choice most logically completes the text?" (71 of 71). The real task wording is the lead-in that comes right before the blank.

**Blank.** Every passage has exactly one blank, always at the very end (71 of 71). All four options continue the same unfinished sentence, so grammar never gives the answer away. Options begin in lower case unless they start with a proper noun or a species name, and they end with a period.

**What grammatical slot the blank fills** (from the lead-in):

| slot | example lead-in | easy | med | hard | all |
|---|---|---|---|---|---|
| `that`-clause after a reporting verb or noun | "This finding suggests that", "the team concluded that", "casting doubt on the idea that" | 7 | 16 | 17 | 40 |
| predicate for a subject already given | "the 'pay as you wish' model may", "In this way, Fornés", "the burrowing action of crabs" | 5 | 3 | 9 | 17 |
| phrase complement | "serve as", "affected by", "serves to", "encouraging them to", "affect viewers by", "the unintended effect of" | 2 | 1 | 3 | 6 |
| `because`-clause (explanation) | "to feel realistic because", "most likely because the" | 1 | 1 | 3 | 5 |
| main clause after a transition | "Therefore, ______", "Consequently, ______" | 0 | 1 | 2 | 3 |

**Signal words in the sentence with the blank** (an item can have several):

| signal | easy | med | hard |
|---|---|---|---|
| suggest(s/ing) | 7 | 6 | 13 |
| therefore | 3 | 10 | 7 |
| conclude(d) / conclusion | 1 | 5 | 3 |
| thus | 0 | 2 | 4 |
| imply / infer | 0 | 2 | 3 |
| because | 2 | 1 | 3 |
| since | 1 | 2 | 1 |
| hypothesize | 1 | 1 | 0 |
| hence | 1 | 1 | 0 |
| consequently | 0 | 0 | 1 |

Only 4 items (1.6, 3.3, 3.8, 3.9) have no explicit inference word; there the logic is carried by "In this way", "thereby encouraging", "are also" or "According to Mulvey's logic". The lead-in usually names who draws the conclusion: the finding ("This finding suggests"), the researchers ("Payré concluded"), a third party ("both Whitten and these art historians likely agree", "some Indigenous advocates express concern"), or the student ("it can reasonably be inferred").

## 2. Subtypes

There is one question format: a short informational paragraph that stops mid-sentence, and four endings to choose from. What changes is what the missing ending has to supply. Six targets appear:

| code | target of the inference | easy | med | hard | all |
|---|---|---|---|---|---|
| T1 | a conclusion about the world drawn from the stated evidence | 9 | 14 | 7 | 30 |
| T3 | a prediction, consequence or requirement ("would", "risk", "need to", "unintended effect of") | 2 | 1 | 11 | 14 |
| T4 | an explanation: why something happened or what mechanism lies behind a finding | 2 | 1 | 9 | 12 |
| T2 | what a person or group believes, assumes, intends or would agree on | 0 | 1 | 6 | 7 |
| T5 | the status of the evidence ("not conclusive", "we cannot say", "casting doubt on") | 0 | 4 | 0 | 4 |
| T6 | the role or function of an example or practice ("serves to", "serve as", "In this way") | 2 | 1 | 1 | 4 |

**T1, finding to conclusion.** The passage reports one or more results; the key states what they show, usually one level more general than the data (tanks to "shallow lakes and ponds"; two musicians to "some musicians ... others"). Lead-ins: "This finding suggests that", "the team concluded that", "These replies suggest that", "Either explanation suggests that". The student must combine every stated result and stop at the conclusion the results license, not one step past it.

**T3, consequence or prediction.** A principle or result is applied forward: what participants would report (3.2), what audiences are encouraged to do (3.3), what scholars risk (3.12), what rail needs (3.11), what an approach could fail to do (3.33). Lead-ins: "would thus", "thereby encouraging them to", "therefore", "for rail to remain a viable alternative ..., ______", "may have the unintended effect of", "could thus". Hard-heavy (11 of 14), because the student has to run the logic rather than recognise it.

**T4, explanation.** The blank supplies a cause, mechanism or route: "because", "most likely because the", "replaced by technology that", "suggesting that [mechanism]". Examples: 3.18 (resin casting destroys the burrow, so it cannot be repeated over time), 3.22 (uninfected workers carry the load), 3.23 (farmers learned the techniques second-hand), 3.27 (migrants carried turkey-farming with them).

**T2, someone's reasoning.** The student reconstructs a belief or assumption that is not the author's: what scholars "assumed" (3.4), what Isla "thought" (3.7), what scientists "imply" (3.10), what a recommendation "implies" (3.6), what two disagreeing parties "likely agree" on (3.15), what gift givers wrongly assume (3.34), whom a declaration was addressed to (2.9). This is the hardest target: 6 of its 7 items are hard, and 4 of the 7 need three steps.

**T5, evidential status.** The key is a hedge: the evidence is "not conclusive" (2.18), "we cannot say at present" (2.20), the present surface "might not accurately reflect" the past (2.11), or the frame asks what the evidence casts doubt on (2.4). This target appears only in the medium tier here.

**T6, function of an example.** "In this way, Fornés ______" leads to "illustrates the artistic opportunity offered by ..."; "the example of Johnson serves to ______" leads to "illustrate both ... and ...". It sits close to Text Structure and Purpose but is answered by logic, not by structure.

## 3. Passages

**Subject areas.**

| | easy | med | hard | all |
|---|---|---|---|---|
| natural science (ecology, animal behaviour, geology, planetary science, astronomy, botany, evolution) | 6 | 6 | 12 | 24 |
| humanities and arts (theater, film, literature, painting, music, dance) | 5 | 6 | 6 | 17 |
| social science (psychology, marketing, management, economics, linguistics, policy, research methods) | 3 | 3 | 9 | 15 |
| history and archaeology (incl. history of technology, ethnobiology) | 1 | 7 | 7 | 15 |

**Genre.** All 71 are single informational paragraphs written in the test's own expository voice. There are no literary excerpts with an attribution line, no poems, no paired texts, no research notes and no tables or graphs. Humanities passages are written about a work ("Ana Castillo's 1986 novel ...", "Laura Mulvey has theorized ..."), never quoted from it at length. Quoted material is limited to short phrases: a studio sign (1.12), an article title (2.1), Whitten's and the historians' wording (3.15) and a historian's characterization (3.30).

**How a passage is built.** Four templates cover nearly every item.

1. *Study report* (roughly half the bank: about 35 passages report a study, survey, experiment, simulation or analysis). Background or definition (1 or 2 sentences), then a named researcher and team with role ("Ecologist Ralf Aben and his team", "Sarah M. Aarons and colleagues"), then the method in one sentence, then the result (often a comparison, ratio or percentage), then a signal plus the blank. Examples: 1.1, 1.7, 2.6, 2.8, 3.17, 3.20, 3.21.
2. *Received view, then new evidence* (17 of 71 contain an explicit received-view marker such as "long thought", "used to believe", "Some scholars have asserted", "Conventional theories ... hold", "One theory"). A belief is stated, "However"/"But recently" introduces counterevidence, and the blank names the revised view or what the evidence undercuts. Examples: 2.4, 2.18, 3.5, 3.19, 3.24.
3. *Principle, then case* (most of structure S2, 18 items). A rule, theory or mechanism is stated in general terms (Brecht's aim, Mulvey's theory, why marketplaces arise, how wood decays, how voters qualified), then a specific case is introduced, and the blank applies the rule to the case.
4. *General claim, then example* (1.6, 2.1, 1.11). An institution or practice is described, then "One such artist was ..." or "the example of Johnson".

Common sentence moves, in order: context, then actor, then method or claim, then result, then complication ("however", "but", "by contrast", "while"), then signal plus blank. Contrast markers per passage: 0.80 easy, 0.86 medium, 0.91 hard. The hard tier packs these moves into 2 to 6 sentences, using em dashes (0.35 per passage), parentheticals (0.68 per passage, e.g. glosses like "(i.e., credentialed experts)" or "(flights of 50 to 210 minutes, from takeoff to landing)") and participial tails (", suggesting that").

**Names, dates, places.**
- 42 of 71 passages name a person (12/15 easy, 11/22 medium, 19/34 hard). Researchers come as full name plus field ("entomologist Susanne Foitzik", "materials scientist Anikó Bezur") or as "X, Y, and colleagues". Names are deliberately international (Dančák, Tjiasmanto, Izidoro, Rajendran, Reshadi, Umehara).
- Historical and cultural figures are well documented but not famous (Georgia Douglas Johnson, Alice Guy-Blaché, María Irene Fornés, Jack Whitten, Henry Ossawa Tanner).
- Indigenous topics recur (2.21, 3.8, 3.23, 3.27, 3.28) and are written respectfully, with self-names first ("Haudenosaunee (Iroquois)").
- 24 passages give a year or decade; 13 give a percentage, ratio or large count (9 of them hard: "42.7% of trials", "94.8 percent", "only about 6%", "more than seven times likelier").
- 8 items (mostly hard) give a Latin binomial in full and then abbreviate it (N. pudica, F. hypoleuca, A. ocellaris, S. caninervis, M. boolii).

**Vocabulary.** Flesch-Kincaid grade (rough, computed): 9.7 easy, 14.4 medium, 16.5 hard. Share of words with 3 or more syllables: 15.3%, 22.5%, 24.0%. Mean word length: 4.94, 5.43, 5.55 letters. Easy passages use everyday words with short sentences ("The crows find a stick without a hook on the ground."). Hard passages use academic vocabulary that the student must parse but is never tested directly: notwithstanding, engender, interrogation, morphological, concurrent, corroboration, efficacy, consequential, ostentatious, prosaic, conspicuous, experiential.

## 4. The correct answer

**How it is justified.** In every item the key is the only option that (a) uses all of the evidence given and (b) claims no more than that evidence supports. Typical justifications:
- combine two facts that sit in different sentences: 1.7 (black wolves common where distemper recurs, plus black wolves more often immune, so the gene variant may be linked to immunity);
- apply a stated principle to a stated case: 3.16 (the real-estate tax was the main route to the vote, so voters probably held real estate);
- remove the alternatives: 2.17 (no father among the males, eggs laid by enclosure females, so parthenogenesis);
- track a direction: 3.1 (Coll's team counted more, and the uncertain group is microorganisms, so Coll's team split variants into separate species).

**Wording.**
- Paraphrase, not echo. Content-word overlap with the passage is the same for keys and distractors (0.42 vs 0.44 easy, 0.40 vs 0.45 medium, 0.43 vs 0.44 hard). Word matching does not find the key, and distractors are built from passage vocabulary just as often.
- One step more abstract than the passage. "the timing of downbeats and offbeats may play a crucial role" (2.6); "correlations in a country between languages and regions ... can replicate themselves" (2.19); "the practice ... not only effectively maintained a food source but also promoted its robustness" (2.21).
- Hedged. About half the keys contain a hedge (may, might, likely, probably, some, can, could, potentially): 7/15 easy, 11/22 medium, 16/34 hard. Among distractors the rate is 20%, 32% and 25%. No key makes an unhedged absolute claim. The only "absolute" words in keys are false alarms such as "if only viewed online", "only until the end", "not always avoid" and "most likely".
- Not the longest option. The key's length rank (1 = longest) is spread out: easy 3/3/5/4, medium 5/7/7/3, hard 7/13/4/10. Mean key length is 12.7, 15.0 and 17.9 words, against 14.2, 15.0 and 18.4 words for distractors. Length is not a cue.
- Mirrors the frame. When the lead-in is negative ("casting doubt on the idea that", "unintended effect of"), the key states the thing undermined or the bad effect, not the conclusion the evidence supports.

## 5. Distractor recipes

213 wrong options, each labelled with its single main flaw:

| archetype | what it does | easy | med | hard | all |
|---|---|---|---|---|---|
| Off-topic claim (OUT) | asserts something the passage never addresses: a new place, motive, outcome or use | 13 | 22 | 31 | 66 (31%) |
| Reversal (REV) | contradicts a stated fact or runs the inference the wrong way | 12 | 14 | 26 | 52 (24%) |
| Unsupported comparison (CMP) | compares with a group, period or species the passage never measured | 6 | 6 | 10 | 22 (10%) |
| Overreach (EXT) | a stronger or wider version of a defensible idea: must, necessarily, eliminates, regardless, all | 2 | 10 | 9 | 21 (10%) |
| Swap (MIX) | uses the right pieces but attaches them to the wrong entity, generation, variable or date | 0 | 4 | 11 | 15 (7%) |
| Rival mechanism (CAUSE) | a plausible explanation that the text does not support | 3 | 2 | 7 | 12 (6%) |
| Wrong variable (VAR) | names a factor the study never varied | 3 | 1 | 1 | 5 |
| Speculative future (FUT) | predicts a later development | 4 | 0 | 1 | 5 |
| Detail echo (ECHO) | recycles a minor passage detail into a claim the text never makes | 0 | 1 | 4 | 5 |
| Recommendation (REC) | "should", "best", "better than": a value judgment | 2 | 1 | 2 | 5 |
| Polarity trap (POL) | in a "casting doubt" frame, states what the evidence supports | 0 | 2 | 0 | 2 |
| True but not the step (REP) | a true restatement of a premise that does not complete the logic | 0 | 2 | 0 | 2 |
| Half the evidence (PART) | fits only one of the facts that the key must satisfy together | 0 | 1 | 0 | 1 |

Illustrations (my wording unless quoted):
- **OUT**: 1.1 B brings in deep lakes, which the study never examined. 2.9 B speculates about how the French government reacted.
- **REV**: 2.5 C claims 1400s mapmakers used a compound invented in the 1900s. 3.11 C would add airport-style procedures to rail, which lengthens the lead times the passage says must be avoided. Subtle hard-tier reversal, 3.1 C: says the earlier team was less sensitive to variation within species, which would push the count the wrong way.
- **CMP**: 3.20 C compares clownfish with "other species of coral reef fish". 2.21 C compares with the Sakha and Kaluli songs that were mentioned only in passing.
- **EXT**: 2.18 C "eliminates the possibility that the figure is Venus." 2.6 A credits synchronized offbeats alone "regardless of whether downbeats are delayed", although both factors were changed together.
- **MIX**: 2.10 C moves the delay from the middle ring to the outermost ring. 2.17 A moves parthenogenesis back one generation. 3.34 A confuses the effort of using a card with the effort of obtaining it. 3.14 A turns "location" (interior vs edge) into "panne size".
- **CAUSE**: 1.9 B (underground pitchers serve to absorb moisture). 3.19 A (volunteers' messages were simply more upbeat).
- **VAR**: 1.14 A, B and D each name a different variable (audience size, viewing time, time of day) when only ad detail was varied.
- **ECHO**: 3.13 D picks up "Morse code"; 3.16 C picks up "doors and windows".
- **POL**: 2.4 D (paintings carried symbolic meaning) is what the lemon finding supports, but the frame asks what it casts doubt on.
- **REP**: 2.12 A, "dramaturges can have a profound impact on ... plays and musicals", is true of theater but never reaches choreographers.

**Typical mix per item.** The most common sets are {REV, OUT, EXT} (8 items), {REV, OUT, OUT} (5), {OUT, OUT, OUT} (4) and {REV, REV, OUT} (4). 42 of 71 items include at least one reversal. Near-miss distractors (MIX, CAUSE, ECHO, PART, POL, REP) average 0.20 per item in easy, 0.55 in medium and 0.65 in hard.

## 6. Difficulty

| signal | easy | medium | hard |
|---|---|---|---|
| mean reasoning steps (section 7) | 1.47 | 1.55 | 2.03 |
| items needing 3 steps | 0 | 1 | 6 |
| mean words per sentence | 17.5 | 23.6 | 27.3 |
| Flesch-Kincaid grade (approx.) | 9.7 | 14.4 | 16.5 |
| share of 3+ syllable words | 15.3% | 22.5% | 24.0% |
| mean key length (words) | 12.7 | 15.0 | 17.9 |
| near-miss distractors per item | 0.20 | 0.55 | 0.65 |
| items with a MIX distractor | 0 | 3 | 9 |
| targets T2 + T3 + T4 (reasoning about beliefs, consequences, causes) | 4 of 15 | 3 of 22 | 26 of 34 |
| passages with a statistic | 1 | 3 | 9 |

What concretely separates the tiers:
- **Easy.** Short, plain sentences. The conclusion is one step from the last two sentences. Distractors are mostly off-topic or flatly contradicted, so they can be eliminated without fully understanding the passage (1.14: three of the options name variables the study never varied). Inferences are near-paraphrases: "tanks with watermilfoil released less methane" leads to "watermilfoil helps prevent methane from escaping".
- **Medium.** Academic vocabulary and longer sentences, but still mostly T1 conclusions. New here: overreach distractors (10 of 21 EXT labels are medium), negative or hedged frames ("casting doubt on", "not conclusive", "cannot say", "might not accurately reflect"), and the first swaps of entities.
- **Hard.** Two things change. First, the target moves from "what does the evidence show" to "what follows, what explains it, or what does someone else believe" (26 of 34 items). Second, the wrong answers become near misses that reuse the right pieces with one wrong link (MIX, CAUSE, subtle REV). Several hard keys require holding a counterfactual or a direction: 3.7 ("if he hadn't already seen it"), 3.33 ("If this view is correct"), 3.1 (which team split species more), 3.34 (givers' belief versus recipients' preference).
- **Not a signal.** Passage length (median 93, 95.5 and 96 words) and answer length relative to distractors. Hard keys are longer only because every option in a hard item is longer.

## 7. Skill-specific inventory: logical structures and reasoning steps

### 7.1 Logical structures of the passages

Each item is assigned the one structure that produces its key.

| code | structure (schema) | easy | med | hard | all | mean steps | items |
|---|---|---|---|---|---|---|---|
| S2 | **Principle plus case leads to consequence**: "if A then B; A holds, so B". The principle may be a theory, a mechanism, a rule or a social norm | 1 | 3 | 14 | 18 | 1.83 | 1.3, 2.3, 2.12, 2.22, 3.2, 3.3, 3.4, 3.8, 3.9, 3.11, 3.12, 3.13, 3.16, 3.18, 3.28, 3.30, 3.33, 3.34 |
| S9 | **Behaviour, design or content reveals a motive, purpose or reason**: "X did D; D only makes sense if X wanted or believed M" | 3 | 1 | 4 | 8 | 2.00 | 1.8, 1.9, 1.11, 2.9, 3.6, 3.7, 3.19, 3.22 |
| S11 | **Received view plus counterevidence leads to revision**: "Some hold P. However, Q. So P is doubtful, or R is the better account" | 1 | 4 | 3 | 8 | 1.75 | 1.13, 2.2, 2.4, 2.13, 2.15, 3.10, 3.24, 3.26 |
| S1 | **Controlled comparison of two groups**: "Groups differ only in F; outcome O differs, so F affects O" | 3 | 2 | 2 | 7 | 1.71 | 1.1, 1.4, 1.14, 2.6, 2.10, 3.17, 3.21 |
| S3 | **Rule or timeline plus observation rejects a premise (modus tollens, dating)**: "If X, then not Y; Y observed, so not X" | 1 | 2 | 3 | 6 | 1.67 | 1.5, 2.5, 2.16, 3.5, 3.27, 3.32 |
| S6 | **X but not Y, so Z**: two members of one set differ on one property, and the difference implies Z | 2 | 1 | 3 | 6 | 1.33 | 1.10, 1.12, 2.7, 3.20, 3.25, 3.29 |
| S7 | **Two cases or two accounts lead to a conditional or a common ground**: opposite outcomes, so "depends on"; a time sequence, so an onset bound; rival accounts share an implication | 1 | 2 | 2 | 5 | 2.00 | 1.2, 2.8, 2.14, 3.14, 3.15 |
| S4 | **Elimination of alternatives**: "Only explanations E1 or E2 are possible; E1 is ruled out, so E2" | 0 | 1 | 2 | 3 | 2.33 | 2.17, 3.1, 3.23 |
| S5 | **Undercut leads to a hedged conclusion**: evidence for P plus an equally good rival (or a tie), so P is not established | 0 | 3 | 0 | 3 | 1.00 | 2.11, 2.18, 2.20 |
| S8 | **Co-occurrence or repeated pattern leads to a link**: "A and B go together (or a pattern recurs), so A is linked to B" | 1 | 2 | 0 | 3 | 1.67 | 1.7, 2.19, 2.21 |
| S10 | **Trade-off leads to a net outcome**: a benefit and a cost, and the stated conditions decide which wins | 1 | 0 | 1 | 2 | 2.00 | 1.15, 3.31 |
| S12 | **General claim plus example**: the example illustrates the claim | 1 | 1 | 0 | 2 | 1.50 | 1.6, 2.1 |

How each structure appears in practice:
- **S2** carries the hard tier (14 of 34). The principle is often a named theory (Brecht in 3.3, Mulvey in 3.9), a causal mechanism (resin casting destroys the burrow in 3.18; marketplaces arise from unequal resources in 3.4), or an institutional rule (tax-based voting in 3.16; confidentiality clauses in 3.28). Hard versions apply the principle to someone's mistaken premise (3.4: scholars underrated ecological diversity, so they assumed markets offered nothing new), or chain two principles (3.34: time spent signals thoughtfulness, and digital cards take little time to buy, so givers wrongly assume recipients will value them less).
- **S1** is the easy-tier workhorse (1.1, 1.4, 1.14). The hard versions hide the comparison inside numbers that need interpreting: in 3.21, 42.7% against 37.5% means the sea stars barely discriminate, so they will eat starving urchins, so their recovery could help clear urchin barrens.
- **S3** contains the classic "anachronism" items (2.5: a 1900s ink compound found in a supposedly 1400s map; 3.32: the Round Table was first introduced in 1155, so an 11th-century source could not have featured it) and the "survival needs a condition" item (2.16: wood survives only under sediment).
- **S6** "X but not Y, so Z": 1.10 (hooked tools are guarded and plain ones are not, so the hooked ones are more valuable), 3.20 (light had no effect on spawning or fertilization but blocked hatching, so settling in lit areas endangers reproduction), 3.25 (savings fell on manufacturing, not on authoring, so authoring costs were less affected).
- **S4** elimination is always flagged in the text: "weren't genetically similar enough to any of the males" (2.17), "Barring the possibility of ..." (3.23), "only partly attributable" plus "similar counts" in the well-understood groups (3.1).
- **S5** appears only in the medium tier: an alternative explanation (cupids were linked with fishing in general), a tie between claims (no evidence favours any claimed inventor), or later processes that could have altered the evidence (erosion).

### 7.2 Reasoning steps the key requires

A step is one inferential move the student must add that the text does not state. 1 step: combine the blank sentence with one stated fact and generalize slightly. 2 steps: add one unstated bridge (apply a principle to a case, link two separated facts, or translate the passage's terms into the option's terms). 3 steps: chain two bridges, or hold a counterfactual or direction (which group did more; what someone else believed).

| steps | easy | medium | hard | all |
|---|---|---|---|---|
| 1 | 8 | 11 | 5 | 24 |
| 2 | 7 | 10 | 23 | 40 |
| 3 | 0 | 1 | 6 | 7 |
| mean | 1.47 | 1.55 | 2.03 | 1.70 |

The 3-step items are 2.4, 3.1, 3.4, 3.7, 3.15, 3.21 and 3.34. Three of them (3.4, 3.7, 3.15) ask about someone else's reasoning, and 3.34 ends with a belief contrasted with a preference. The one-step hard items (3.12, 3.13, 3.18, 3.25, 3.29) earn their tier through vocabulary and sentence density rather than logic.

### 7.3 Hedge and frame vocabulary

- Hedges in keys: may (14 keys), some (8), likely (8), can or could (3), probably (2), might (1), potentially (1). "most strongly suggest", "may suggest" and "most likely because" in lead-ins set the expected strength.
- Absolute markers in distractors: must, necessarily, eliminates, regardless, only if, all the planets, the best way, will soon replace, the most thematically accessible.
- Negative frames that invert what the key states: "casting doubt on the idea that" (2.4), "the unintended effect of" (3.28), "risk" (3.12), "fail to consider" as the key of a conditional frame (3.33), "wrongly assume" (3.34).

## 8. Generation blueprint

### 8.1 Shared skeleton (all templates)

Item = paragraph (60 to 125 words) ending in an unfinished sentence + the fixed stem + four endings.

Slots common to every template: `domain` (natural science 34%, humanities and arts 24%, social science 21%, history and archaeology 21%), `actor` (fictional researcher with full name and field, or "researchers"), `setting` (organism, site, work or institution), `evidence` (1 to 3 facts), `signal` (lead-in from section 1), `slot_form` (`that`-clause 56%, predicate 24%, phrase 8%, `because` 7%, transition 4%), `hedge` for the key.

Fully programmatic parts:
- the stem;
- the final lead-in sentence (signal phrase plus actor, chosen from the inventory in section 1);
- answer-letter balancing;
- surface typography (curly quotes, en dashes in ranges, species abbreviation after first mention);
- the slot-form agreement check (every option must read as a grammatical continuation of the same lead-in);
- distractor frames that only need slot values: VAR (swap in an unmanipulated variable), CMP (add "than [unmeasured group]"), EXT (strengthen the key's hedge to must, all or necessarily), REV (negate or invert the key's direction), FUT ("will soon ...").

Parts that need an author or a language model: the passage prose, the key's paraphrase one level up from the data, and every near-miss distractor (MIX, CAUSE, ECHO, POL), since those must be plausible in context.

### 8.2 Templates by structure

**S1 Controlled comparison (easy to medium).** Slots: `factor` with two levels, `outcome`, `direction`, optional statistic. Key: "[level 1 of factor] [may] [increase/reduce] [outcome]", generalized to the real setting. Distractors: VAR (an unvaried factor), CMP (an unmeasured setting), EXT or REC ("the best way to ..."), REV (opposite direction). Hard variant: give two close percentages, so the key must read near-equality as "do not avoid" (the 3.21 pattern), and add one more applied step.

**S2 Principle plus case (medium to hard; build first).** Slots: `principle` (theory, mechanism, rule or norm in one sentence, attributed or general), `case` (meets the antecedent), optional `mistaken premise` (for hard). Key: the consequent applied to the case, hedged. Distractors: REV (the consequent negated or reversed), MIX (the principle applied to the wrong party, e.g. the method instead of the object), CAUSE (a different mechanism), OUT. Hard variant: the blank asks what someone *assumed* given a wrong premise (3.4), or chains two principles (3.34).

**S3 Modus tollens and dating (medium to hard).** Slots: `rule` (X appears only after date D, or Y survives only if C), `observation`, `claim under test`. Key: the claim is false, the object is later than claimed, or condition C held. Distractors: REV (accepts the claim), EXT (generalizes the rejection to all related knowledge, as in 2.5 A), HEDGE-REV ("not enough information"), MIX (applies the date to the wrong source).

**S4 Elimination (medium to hard).** Slots: `candidates` (2 or 3), the `exclusion facts`, the `survivor`. Key: the survivor, hedged ("probably"). Distractors: MIX (the survivor attached to the wrong generation or entity), EXT (in captivity but not in the wild), CAUSE (an added condition).

**S5 Undercut (medium).** Slots: `claim`, `supporting evidence`, `rival explanation or tie`. Key: "is not conclusive evidence that ...", "we cannot say ...", "might not accurately reflect ...". Distractors: EXT ("eliminates the possibility"), REV ("would be difficult to account for otherwise"), OUT.

**S6 X but not Y (easy to hard).** Slots: two members of a set, the property on which they differ, what that implies. Key: Z. Distractors: REV (claims the two members are alike, or that the unaffected one was affected), CMP (an outside group), CAUSE.

**S7 Two cases or accounts (easy to hard).** Slots: `case A` with outcome, `case B` with the opposite outcome, the distinguishing feature; or `account A` and `account B` with a shared consequence. Key: "depends on [feature]", "no later than [date]", or the common ground. Distractors: MIX (the wrong distinguishing feature, e.g. size instead of location), PART (fits only one account), spurious feature (band against solo artist, as in 1.2 B).

**S8 Co-occurrence (easy to medium).** Slots: two observations that line up. Key: "[A] may be linked to [B]" or the abstract rule. Distractors: FUT, CMP (other species or regions), REV.

**S9 Action reveals motive or belief (easy to hard).** Slots: `agent`, `action`, the `context` that makes the action rational. Key: the motive or belief. Distractors: CAUSE (a rival motive), MIX (the right place or time attached to the wrong entity, as in 3.7 B with Germany), OUT. Hard variant: phrase the lead-in as a counterfactual ("thought that if he hadn't already seen it, ...").

**S11 Received view plus counterevidence (medium to hard).** Slots: `holder` of the view ("Some art historians"), `view`, `counterevidence`, `frame` (positive: "suggests that"; negative: "casting doubt on the idea that"). Key: the revised view, or the view undercut. Distractors: POL (the supported view offered in a doubt frame), REV (endorses the old view), CMP.

**S10 and S12** are rare (2 items each). Fold S10 into S2 as a variant ("benefit vs cost under stated condition") and S12 into S9 as a "function of an example" variant.

### 8.3 Automatic checks that would catch broken items

- Exactly one `______`, at the end of the passage. Stem identical to the official one. Four options, each starting in lower case (unless it starts with a proper noun or species name) and ending with a period.
- Grammar: each option, appended to the lead-in, parses as one sentence (spot check with a language model, or a rule for `that` plus finite clause, `to` plus verb, `by` plus gerund).
- Key hedge present; no unhedged absolute in the key (must, all, never, always, necessarily, eliminates).
- Length: the key is not the longest option by more than 20%, and across a batch the key's length rank is roughly uniform.
- Overlap parity: the content-word overlap of key and distractors with the passage is within 0.1 of each other (the bank's gap is 0.01 to 0.05), so neither copying nor avoiding passage words gives the key away.
- Solver test: a model must pick the key with the passage present. With the passage removed it should do no better than chance, otherwise the item is answerable from world knowledge.
- Per-distractor label: a model must label each wrong option with one archetype and quote the passage fact that it contradicts or goes beyond. Reject the item if any distractor gets "supported".
- Answer-letter balance per batch. Note that the official set leans to B (25 of 71) and is light on C (13).

### 8.4 Quality risks

- Defensible distractors. EXT and CAUSE options written with "may" can become true; keep distractor hedges rare (the bank's rate is 20 to 32%) or make sure that the content itself is unsupported.
- Over-hedged, vague keys. The bank's keys are hedged but specific (they name the factor, group or mechanism). A key like "the results may be important" is not acceptable.
- Facts attributed to real people. The official items cite real researchers and real findings. For original items, invent researchers and keep the science plausible but general, or check every claim. Never attach invented findings to a real scientist.
- Passages that announce the answer. Easy items state the result plainly, but the key still generalizes one step. If the key's clause appears verbatim in the passage, the item turns into detail recall (that skill is Central Ideas and Details).
- Negative frames. POL items invert the usual logic and are easy to write wrongly. Have a model restate the frame ("which idea does this evidence weaken?") before accepting the item.

### 8.5 Recommended scope and build order

- **Templates:** 10 (S1, S2, S3, S4, S5, S6, S7, S8, S9 with S12 folded in, S11; S10 as an S2 variant). Each template gets an easy, a medium and a hard recipe, varying sentence length (about 17, 24 and 27 words per sentence), target (T1 for easy; T2, T3 or T4 for hard) and distractor mix (mostly OUT and REV for easy; at least one MIX or CAUSE for hard).
- **First batch:** about 120 items: 30 easy, 40 medium, 50 hard. This follows the bank's lean toward hard items (48% hard) while giving practice enough easy material.
- **Build first:**
  1. S2 Principle plus case: 25% of the bank and 41% of the hard tier.
  2. S1 Controlled comparison: the easy-tier backbone, and the slots are the most mechanical.
  3. S11 Received view plus counterevidence: covers the negative frames.
  4. S9 Motive or belief: the hard T2 items.
  5. S6 "X but not Y".
  6. The rest (S3, S7, S4, S5, S8).
