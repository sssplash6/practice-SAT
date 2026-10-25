# Central Ideas and Details: what makes a band-7 item

Source: `material/rw/cb_api/central_ideas_and_details.json` (138 official items with CB's own rationale). Bands 5, 6 and 7 hold 23, 23 and 22 items. Only 16 of the 45 band-6 and band-7 items are in our transcript set (10 band 6, 6 band 7), so 29 of them were never seen when `spec/rw/central_ideas_and_details.md` and our templates were written. All 45 were read with their rationales and hand-coded; the numbers below come from a scratch script run over the CB file (register measures reuse `tools/check_rw.py`, word rarity uses the rank in `tools/data/freq.txt`).

How to read the separation number: **AUC** is the chance that a random band-7 item scores higher than a random band-6 item on that measure (ties count half). 50% means no separation; 70% or more (or 30% or less) is a real gap at these sample sizes (one standard error is about 9 points). Hand codes were made by one reader who knew each item's band, so treat them as a careful reading, not a blind measurement.

## 1. Counts

| | band 5 | band 6 | band 7 |
|---|---|---|---|
| items | 23 | 23 | 22 |
| main idea (MI) | 15 | 10 (2 in verse) | 9 (2 in verse) |
| supported detail (SD: "most strongly suggest", "based on the text", "best supported", "would most likely agree") | 6 | 10 | 11 |
| explicit detail (ED: "According to the text", "makes which point") | 2 | 2 | 0 |
| other | 0 | 1 misfiled purpose item (3.15) | 1 role-of-a-finding, 1 validity question |
| literary (prose / verse) | 4 | 3 / 4 | 3 / 2 |

Band-5 subtypes are read from the stem; band 6 and 7 are hand-assigned.

Template mix (codes from `satbank/rw/central_ideas_and_details.json`, plus two new ones):

| template | band 6 | band 7 | band-7 items |
|---|---|---|---|
| T1 main idea, study report or scholar argument | 2 | 3 | 024eb2ec, 7aa510fb, e80ba20d (3.20) |
| T2 main idea, view then correction | 4 | 4 | 251e5281, 70aacc03, 881ba6f1, f7bd14de |
| T3 main idea, profile | 1 | 0 | |
| T4_prose main idea, literary prose | 1 | 0 | |
| T4_poem main idea, poem or verse drama | 2 | 2 | b69d821d (3.17), 8d88740e |
| T5 explicit detail | 2 | 0 | |
| T6 supported detail (incl. literary and "would most likely agree") | 10 | 11 | 2b252bbd, 303537cf, 36e2868f, 4d3e3c52 (3.7), 7812801f (3.18), 8f3a200e, aa0968dd, d1b8a9ad (3.8), db2da2bf, dcca0dfc, ed314256 (3.1) |
| T7 central question | 0 | 0 | |
| **N1 role of a finding** (new): "the finding about X was important for which reason?" | 0 | 1 | 458b4a11 |
| **N2 validity question** (new): "most useful to answer in determining the validity of the researchers' claim" | 0 | 1 | 5869a196 |
| purpose (misfiled, 3.15) | 1 | 0 | |

The template and subtype mix barely moves from 6 to 7 (MI 10 vs 9, SD 10 vs 11). Band 7 is not a different kind of question; it is a harder build of the same kinds. The two new stems are worth adding as T6 variants; they appear only at band 7.

## 2. What separates 7 from 6, measured

Hand-coded measures, defined for this skill:
- **Reasoning steps**, on the scale of `spec/rw/central_ideas_and_details.md` section 6 made explicit: 0 = the key paraphrases one sentence; 1 = it joins stated pieces or carries a stated concession; 2 = it needs one unstated link (an inference, a figure turned into plain terms, or a term mapped through a definition given elsewhere); 3 = two chained links, or a reading against the surface (irony, litotes, a stance word).
- **Clue spread**: how many separate passage statements the key depends on.
- **Partly-right distractors**: wrong options that contain a clause or component the passage supports and fail on another one.
- **Stance**: the key hinges on one evaluative or ironic word or aside.

| measure | band 5 median | band 6 median (mean) | band 7 median (mean) | AUC 7>6 | verdict |
|---|---|---|---|---|---|
| option length, words (mean of 4) | 18.5 | 18.5 (19.8) | 23.5 (25.8) | 72% | separates |
| key length, words | 19 | 17 (19.4) | 24 (25.2) | 71% | separates (all options grow, not the key alone) |
| same, main-idea items only | | 20.6 | 33.8 | 87% | strongest single signal |
| distractors carrying a hedge (may, likely, suggests, can ...) | 0 | 0 (0.57) | 1 (1.32) | 70% | separates; main idea only 84% |
| key carries a hedge | | 30% of items | 64% of items | 67% | weak; main idea only 74% |
| words per sentence | 24.3 | 26.8 | 30.0 | 68% | weak; main idea 24.0 vs 32.7, supported detail flat (27.0 vs 27.3) |
| reasoning steps (hand) | | 2 (1.83) | 2 (2.32) | 71% | separates: 8 of 22 band-7 items need 3 steps, 1 of 23 band-6 |
| clue spread (hand) | | 2 (1.83) | 2 (2.36) | 73% | separates: 3+ statements in 8 of 22 vs 1 of 23 |
| partly-right distractors (hand) | | 1 (1.13) | 2 (1.77) | 67% | weak overall; all three partly right in 5 of 22 vs 1 of 23 |
| stance word or irony carries the key (hand) | | 1 of 23 | 7 of 22 | | separates as a rate |
| passage words | 86 | 85 | 87.5 | 56% | no |
| sentences | 4 | 3 | 3 | 43% | no |
| chars per word | 5.22 | 5.34 | 5.48 | 54% | no |
| long-word rate (9+ letters) | 14% | 17% | 18% | 53% | no |
| rare-word rate (rank beyond 10,000) | 22% | 21% | 26% | 54% | no (main idea only 62%) |
| key length rank (1 = longest) | 2 | 3 | 3 | 49% | no: the key is not the longest at either band |
| key / distractor length ratio | 0.97 | 0.95 | 0.98 | 52% | no |
| key overlap with passage (content words) | 0.53 | 0.36 | 0.43 | 59% | no |
| best distractor overlap | 0.64 | 0.62 | 0.67 | 56% | no: at both bands a distractor out-borrows the key |
| options sharing a first word | 2 | 2 | 3 | 55% | no |
| asides per passage (parentheses, dash pairs) | 0.65 (mean) | 0.57 (mean) | 1.14 (mean) | 65% | weak |
| key abstracts passage terms into a category (hand) | | 70% | 73% | | no |
| figurative reading needed (hand) | | 4 of 23 | 2 of 22 | | no, slightly more common at band 6 |
| CB rationale words per distractor | 46 | 49 | 60 | 64% | weak (CB needs more words to refute band-7 distractors) |

Plainly: vocabulary (word length, long words, rarity), passage length, word overlap and key length rank do **not** separate band 7 from band 6. What separates is the size and shape of the options (longer, two-part, hedged on all sides, especially in main idea items), sentence length in main-idea passages, and the logic the key needs (more statements joined, more readings against the surface).

## 3. What separates 7 from 6, read

1. **The key depends on one stance word, litotes or irony.** Seven band-7 items (one band-6 item) turn on a single evaluative signal that a skimmer reads past.
   - 881ba6f1: "which he putatively used to illustrate a robust model". The key ("not due to the importance of the metaphor in Smith's work") is unreachable without "putatively".
   - f7bd14de: "It is not inconceivable that Beowulf emerged from such a context". The key turns litotes into "has some plausibility".
   - 303537cf (Carroll): the Lord Chancellor marvels "And with such unanimity!" at a crowd shouting different things. The key: he "describes the crowd as being united, even though the crowd clearly appears otherwise".
   - dcca0dfc (Herron): "it would have been impertinent to inquire too closely into the actual achievements". The key reads the irony as "uncertain whether he has accomplished anything".
   - 8d88740e (Richard III): "I do beweep to many simple [gullible people]". The key: grief is pretended.
   - d1b8a9ad: the key comes from the aside "(subjects hardly unique to disco, by the way)".
   Band 6 uses figurative language instead (Shakespeare's "journey in my head", Mena's hat), which the bank treats as easier than irony.

2. **The key states what a finding means for a question, not the finding itself.** 024eb2ec poses "whether the material properties ... have been similarly affected", reports "significant interspecies variation", and the key answers the question ("have diversified during adaptive radiation"). 458b4a11 asks why "crucially, microorganism community composition was unchanged" matters; the key names the method concept ("ruled out a potential alternative explanation"). 7aa510fb's key names a relation between two sources ("Lang's model provides a means of explaining the finding by van Berlo"), so every option has to be checked for who claims what.

3. **The key needs three statements, one of them a definition or an aside.** db2da2bf: "same direction as the planet's spin" has to be mapped back to the definition of prograde two sentences earlier, and "all but one" turned into "may not be a remnant". 251e5281's key never names spike waves ("when traveling waves intersect in specific ways, the resulting wave may be higher"), so the student must chain the definition, the breaking rule and the exception. 70aacc03 hides the expectation the key negates inside a dash aside ("resource extraction requires initial investments ... best met by multinational corporations").

4. **Main-idea options become long two-part sentences in one shared frame.** In 70aacc03 and f7bd14de all four options open with "Although". Band-7 main-idea options run a median 34 words (band 6: 21). The first half of each option is usually true; the item is decided in the second half.

5. **Hedges are everywhere, so the hedge stops being a cue.** Band-7 distractors carry hedges 1.3 times per item (band 6: 0.6): "has likely diversified", "can likely be explained", "may not occur". The key must match the passage's exact degree ("some plausibility", "not compellingly addressed", "one potential means ... except in certain circumstances").

6. **Single sentences of 40 to 100 words.** 36e2868f (Mann) is one 100-word sentence with three parenthetical asides; 881ba6f1, 2b252bbd and 7aa510fb pack the claim into 30 to 45 word sentences. Main-idea passages run a median 33 words per sentence at band 7 (24 at band 6). Supported-detail passages do not lengthen.

7. **New tasks that test method, not content.** 5869a196 asks which question would test the researchers' claim; the key names a confound the passage never mentions (participants who "already knew that information independently of their phone"). Nothing like it appears below band 7.

What does not make band 7: harder words (band-6 passages are just as Latinate: "putatively" sits next to band-6 "longitudinal economic data"), longer passages, poems as such (band 6 has more verse), or keys that avoid passage words.

## 4. Distractor recipes at band 7

Labels from section 5 of `spec/rw/central_ideas_and_details.md`, plus three new ones. 69 band-6 and 66 band-7 wrong options:

| recipe | band 6 | band 7 | change |
|---|---|---|---|
| plausible but unsupported (UNS) | 25 | 17 | down |
| twisted detail (TWI) | 13 | 13 | flat |
| contradicts the text (CON) | 7 | 15 | doubles; almost all are half-true compounds |
| invented comparison (CMP) | 7 | 6 | flat |
| literal or tonal misreading (LIT) | 4 | 4 | flat |
| true but narrow (NAR) | 5 | 1 | nearly gone |
| overstated (OVR) | 5 | 1 | nearly gone |
| too broad (BRD) | 3 | 1 | nearly gone |
| **wrong attribution (ATT)**, new: the right content credited to the wrong source, or a known fact presented as the study's finding | 0 | 4 | band 7 only |
| **converse of a conditional (CONV)**, new | 0 | 1 | band 7 only (8f3a200e B: "Its absence ... indicates that the planet probably doesn't have life") |
| **wrong variable / non-discriminating question (VAR, NDI)**, new | 0 | 3 | band 7 only (validity item) |

What dominates at band 7: CON + TWI + ATT (32 of 66), against UNS + NAR + OVR + BRD at band 6 (38 of 69). The easy-to-reject kinds (narrow, overstated, too broad) almost vanish.

How the hardest distractor is built (one per band-7 item, read off the CB rationale as the one it spends most words on):
- **Key content plus an unsupported tail.** 881ba6f1 B starts with what the key says (later economists gave the metaphor "a significance it does not have") and then adds "but it is nevertheless a useful model". The student has to reject an option whose first half is correct.
- **True first clause, swapped second clause** in a shared two-part frame. 251e5281 A, B and C each open with a true statement and then attach the factor to the wrong wave type, the wrong mechanism, or the wrong source. db2da2bf A pairs a true "It doesn't have a retrograde orbit" with a false "but it likely has the same origin".
- **Relation reversal between two named sources.** 7aa510fb B: "Research by van Berlo et al. corroborates Lang's conclusion" turns "Lang's model explains van Berlo's finding" around.
- **Invented comparison that sounds like the text's own contrast.** f7bd14de C ("fits equally well with ... the seventh and eighth centuries"); 4d3e3c52 B and C compare with "other perovskite solar cell architectures" and "other established approaches".
- **Literary: the surface reading.** 8d88740e A takes Richard's weeping as earnest; dcca0dfc C takes "state secrets" literally.

## 5. Band-7 writing recipe

General settings for every band-7 draft, from sections 2 and 3:
- Options: main idea 30 to 40 words each, supported detail 18 to 25; all four in one frame (same opening word, or "Although X, Y"); the key is not the longest.
- At least two distractors partly right: a true first clause, then one wrong link (CON-half, TWI, ATT). Drop narrow, overstated and too-broad distractors.
- At least one distractor hedged like the key; the key's hedge copies the passage's exact degree.
- The key needs 3 passage statements, or 2 statements plus a stance word, an aside or a definition.
- Do not raise word rarity or passage length to make it harder; they do not move the band.

**T1 study report or scholar argument (3 band-7 items).** Change from a band-6 T1:
- Passage: 2 or 3 sentences, 30+ words each. Sentence 1 or 2 states a research question ("To investigate whether ...") or a problem ("what grounds opposition to lying ...?"); the last sentence gives the finding, an explanation from a second source, or a qualified answer ("unless doing so prevents ...").
- Key: answers the question, or names the relation between two sources ("X's model provides a means of explaining Y's finding"); carries the exception ("except in certain circumstances").
- Distractors: one ATT (swap who concluded or explained what), one CMP (rate or size comparison the text never makes), one CON-half (first half true, second negates the finding).

**T2 view then correction (4 band-7 items).** Change from a band-6 T2:
- Passage: the correction is signalled by one stance word or litotes ("putatively", "not inconceivable", "may appear counterintuitive") instead of a plain "However".
- The expected or earlier view can sit in a dash aside.
- Key: "Although [what the passage concedes, at its exact degree], [the revision]". All four options use the same "Although" frame and differ only in what is conceded or what is revised.
- Distractors: one keeps the earlier view (CON), one adds a tail to the key's own claim ("but it is nevertheless useful"), one invents a comparison or a source of doubt (A in f7bd14de: evidence "called into question by advocates for an earlier date").

**T4_poem verse (2 band-7 items).**
- Poem: one extended figure that has to be carried into a general claim (Sackville-West: a calm port leads to "how sweet / Old age might sink").
- Verse drama: the speaker says one thing and admits another (Richard III).
- Stem for drama: "Which choice best describes what happens in the text?" Options 30 to 40 words each, all naming the speaker's action plus a reason.
- Distractors: the sincere surface reading (LIT); the right action with the wrong allies or target (TWI); an invented later state of affairs (UNS).
- Public-domain text only.

**T6 supported detail (11 band-7 items, three variants).**
- *Informational*: two or three statements, one of them a definition or an aside, lead to a conclusion the text never states. The key maps a term back through the definition (prograde) or projects a consequence ("difficult to reproduce exactly in a different theatrical space"). Distractors: two half-true compounds in the key's frame ("It has a prograde orbit that is likely the result of ..."), one invented comparison with an entity the text names.
- *Literary irony*: the narrator or a character says something the scene contradicts (Carroll, Herron), or a narrator hedges at length (Mann). Stem: "Based on the text, which choice best describes [character]?" or "how does [character] respond?". Key frame: "[does A], even though [B]". Distractors: the surface reading, a literal reading of a joke, a half-true "[A], but [invented B]".
- *Would most likely agree*: a proposal plus a finding that splits it by case (NH3 on rocky planets vs mini-Neptunes). Key: the proposal holds in one case and not the other. Distractors: the converse of the conditional (CONV), the finding overextended to both cases (CON), an invented likelihood comparison (CMP).

**N1 role of a finding (new).**
- Stem: "It can most reasonably be inferred from the text that" ... "the finding about X was important for which reason?"
- The passage marks the finding with "crucially" or "allowing them to attribute".
- Key: a method-level description ("ruled out a potential alternative explanation").
- Distractors: a true result that is not the reason (NAR), an extension to new conditions (UNS), a claim that the unchanged factor varied (CON).

**N2 validity question (new).**
- Stem: "Which question would be most useful to answer" ... "the validity of the researchers' claim"?
- Passage: a two-condition study and the researchers' claim.
- Key: a question about a confound the passage leaves open.
- Distractors: a timing question that affects both conditions equally (NDI), and questions about a different variable (confidence, accuracy) (VAR).

**No band-7 items**: T3 profile, T4_prose main idea, T5 explicit detail, T7 central question. Do not aim these at band 7. A prose literary item aimed at band 7 should be written as T6 literary irony.

## 6. Checks

Only signals that separated in section 2 are used. Reliability is the AUC from section 2: the chance the check ranks a random band-7 official item above a random band-6 one.

Automatic (script):
1. **Option length.** Main idea: mean option length 28 words or more (band 7 median 34, band 6 median 21). Supported detail: 18 or more. Reliability 87% for main idea, about 63% for supported detail, so for supported detail it only screens out band-6 shapes.
2. **Distractor hedges.** At least one distractor with may, might, could, can, likely, suggests or tends. Reliability 70% overall, 84% for main idea. Also guards against the key being the only hedged option.
3. **Two-part frame.** At least two options contain a contrast or negation word (although, but, whereas, even though, rather than, instead, not). Band 7 averages 1.8 such options per item, band 6 1.2 (AUC 62%), so this is a weak screen, not a gate.
4. **Words per sentence, main idea only.** 30 or more (band 7 median 33, band 6 24). Reliability 68%; do not apply it to supported detail.
5. **Not used:** passage length, chars per word, long-word rate, word rarity, key overlap, key length rank. None separates band 7 from band 6, and pushing them would only make a draft look harder.

Agent-run (a reviewer model reads the draft, with this rubric):
6. **Steps.** Count unstated links with the section 2 scale. Band 7 should score 3, or 2 with three statements joined. Reliability about 71%. Asking for the passage sentences the key uses also gives the clue spread (73%).
7. **Partly-right distractors.** For each wrong option, quote the passage text that supports part of it, or say "none". Band 7 should have at least 2, ideally 3. Weak alone (67%), but all three partly right occurs in 5 of 22 band-7 items against 1 of 23 band-6 items, so treat 3 of 3 as a strong band-7 sign. A cheap proxy (CB-style refutation containing "although ... does mention") correlated only 0.46 with the hand count, so use the agent.
8. **Stance.** Ask: "Which single word or aside must the student weigh to reject the strongest distractor?" A real answer ("putatively", "not inconceivable", an ironic exclamation) appears in about a third of band-7 items and almost never at band 6.
9. **Recipe mix.** Label each distractor with the section 4 codes. Two or more of UNS, NAR, OVR, BRD marks a band-6 shape (13 of 23 band-6 items, 5 of 22 band-7). Two or more of CON, TWI, ATT marks band 7 (10 of 22 band-7 items, 4 of 23 band-6). Require the second and reject the first.
10. **Solver gap.** Run a cheap solver several times. A band-7 draft should draw the solver to the half-true distractor more often than a band-6 draft does. This is not validated on the official set yet; treat it as a tiebreaker.

Expected yield: a draft that passes 1, 2, 6, 7 and 9 matches the band-7 profile on every signal that actually separated the official items.
