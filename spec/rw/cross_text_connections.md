# Cross-Text Connections (Craft and Structure): bank analysis

Source: 41 official items in `material/rw/transcripts/cross_text_connections.json` (24 of them corrected and verified against the page image), keys in `material/rw/keys/cross_text_connections.json`. Item ids are `tier.n` (1 = easy, 2 = medium, 3 = hard). All numbers below were computed with Python over the corrected transcript; the subtype, relationship and distractor labels are a hand coding of every item and option.

## 1. Snapshot

| Tier | Items | A | B | C | D | Passage words, both texts (min / median / max) | Text 1 median | Text 2 median | Mean option words | Mean stem words |
|---|---|---|---|---|---|---|---|---|---|---|
| easy | 16 | 4 | 2 | 3 | 7 | 112 / 135.5 / 150 | 64.5 | 66 | 16.3 | 21.1 |
| medium | 11 | 2 | 4 | 1 | 4 | 125 / 138 / 152 | 69 | 65 | 17.5 | 21.4 |
| hard | 14 | 3 | 3 | 3 | 5 | 122 / 137.5 / 156 | 70 | 67.5 | 23.1 | 22.4 |
| all | 41 | 9 | 9 | 7 | 16 | 112 / 136 / 156 | 69 | 67 | 18.9 | 21.6 |

- D is the key in 16 of 41 items (39%), 7 of 16 in easy. This is a quirk of the sample, not a rule; generated sets should balance letters.
- Passage length is flat across tiers. Each text is 50 to 87 words, a median of 3 sentences, and the two texts are close to equal length. Difficulty does not come from length.
- Options get longer with tier (16.3, 17.5, 23.1 words) because hard options are two-clause (concession plus rebuttal, or "Text 1 does X, whereas Text 2 does Y").

### Stem wording variants

| # | Wording (slots in brackets) | Count | Items |
|---|---|---|---|
| 1 | Based on the texts, how would [speaker] most likely respond to [target]? | 18 | 1.1, 1.4, 1.10, 1.15, 2.4, 2.5*, 2.6, 2.8, 2.9, 2.11, 3.2, 3.3, 3.6, 3.7, 3.9, 3.12, 3.13, 3.14 |
| 2 | Based on the texts, what would [speaker] most likely say about [target]? | 3 | 1.3, 2.2, 2.10 |
| 3 | Based on the texts, how would [speaker] most likely characterize [target]? | 2 | 2.7, 3.8 |
| 4 | Based on the (two) texts, how would [speaker] most likely regard [target]? | 2 | 1.7, 1.11 |
| 5 | Based on the texts, how would [speaker] most likely describe [target]? | 1 | 3.5 |
| 6 | Based on the texts, what response would the author of Text 2 most likely suggest for someone in the situation described in the underlined sentence in Text 1? | 1 | 1.16 |
| 7 | Based on the texts, both authors would most likely agree with which statement? | 5 | 1.2, 1.6, 1.12, 1.13, 2.3 |
| 8 | Based on the texts, the author of Text 1 and the author of Text 2 would most likely agree with which statement? | 1 | 1.5 |
| 9 | Based on the texts, [party in Text 1] and [party in Text 2] would most likely agree with which statement (about [topic])? | 2 | 2.1, 3.1 |
| 10 | Based on the texts, if [party in Text 1] and [party in Text 2] were aware of the findings of both experiments, they would most likely agree with which statement? | 1 | 3.4 |
| 11 | Which choice best describes a difference in how the author(s) of Text 1 and (the author of) Text 2 view [object]? | 4 | 1.8, 1.9, 1.14, 3.10 |
| 12 | Which choice best describes how Text 1 and Text 2 relate to each other? | 1 | 3.11 |

\* 2.5 drops "most" ("how would Artemieva likely respond"). 36 of 41 stems open "Based on the texts" (1.11: "Based on the two texts"); only the 5 difference and relate stems do not. 7 stems tag the speaker with "(Text 1)" or "(Text 2)" after a name.

## 2. Subtypes

Four tasks, one of which dominates.

| Subtype | easy | medium | hard | total |
|---|---|---|---|---|
| S1 Response prediction ("how would X respond / say / characterize / regard / describe / suggest") | 8 | 9 | 10 | 27 |
| S2 Agreement ("would most likely agree with which statement") | 5 | 2 | 2 | 9 |
| S3 Difference ("best describes a difference in how ... view") | 3 | 0 | 1 | 4 |
| S4 Relationship ("how Text 1 and Text 2 relate to each other") | 0 | 0 | 1 | 1 |

### S1 Response prediction (27)

**Definition.** One text supplies a speaker (its author, or a researcher it reports), the other supplies a target (a claim, view, hypothesis, problem or underlined portion). The student picks what the speaker would say about the target.

**Direction.** Text 2 speaks about Text 1 in 23 items. Text 1 speaks about Text 2 in 4 (1.11, 2.2, 2.6, 3.7); in all four, Text 1 holds a general frame (a claim about a whole field, a physics puzzle, a philosophical position, a crediting practice) and Text 2 is a specific case the frame explains.

**Speaker.** "the author of Text 2" 12; a named researcher, team or role in Text 2 ("Singh and Roy (Text 2)", "the ecologist in Text 2", "the researchers in Text 2", "Graeber and Wengrow (Text 2)") 11; "the author of Text 1" 4.

**Target.** Underlined portion or claim 11 (10 in Text 1, 1 in Text 2); a named object 14 ("the research discussed in Text 1", "the claim about Appia's level of technical expertise made by Bremner in Text 1", "Siraj's hypothesis", "the consensus view", "the problem presented in Text 1", "the view of the theorists", "the assessment of Orlando", "the 'conventional wisdom'"); the whole other text 2 ("the discussion in Text 1/2").

**Option shells.**

| Shell | Items | Example shape (own words) |
|---|---|---|
| By + gerund phrase, no final period | 14 | By noting that the claim ignores X |
| As + evaluative adjective, because/since + reason | 3 (1.7, 1.11, 3.8) | As unsurprising, because X |
| Pronoun statement ("It ...", "They would ...", "That behavior ...") | 5 (2.2, 2.10, 3.5, 3.6, 3.12) | It may seem plausible, but X |
| Plain declarative statement | 4 (1.1, 1.3, 1.4, 2.4) | Requiring X does not necessarily lead to Y. |
| Imperative advice | 1 (1.16) | State a preference. |

**What the student must do.** (1) Locate the exact target claim in the object text. (2) Pin down the speaker text's position and its grounds (usually a finding). (3) Classify the relation: does the finding refute, limit, explain, solve or support the target? (4) Choose the option that states that relation, aimed at that target, and adds nothing the speaker text does not license.

### S2 Agreement (9)

**Definition.** Two texts that disagree on something (cause, interpretation, authorship, emphasis) still share one proposition; find it. In 8 of 9 the texts conflict on a visible point and the key is the premise underneath the conflict (both think the bird species are restricted, they only disagree on why). 3.4 is different: the texts report two compatible experiments and the key is a new inference from combining them (the 2007 broths probably lacked the dipeptides found in 2022).

**Stems:** "both authors" 5, "the author of Text 1 and the author of Text 2" 1, named parties 2 (2.1 adds "about microbes"), hypothetical "if ... were aware of the findings of both experiments" 1.

**Options:** always plain declarative sentences, 7 to 27 words.

### S3 Difference (4)

**Definition.** Name the dimension on which the authors differ. Options are two-sided: either a comparative (1.8: Text 1's author believes the moon "formed more slowly than" Text 2's author does) or a split clause ("While the author of Text 1 ..., the author of Text 2 ...", "X ..., whereas Y ..."). The student must get both halves right; most distractors get one half right or both halves on the wrong dimension.

**Objects viewed:** "the evidence for the formation of the moon", "the study of Soyinka's works of drama", "Strassburg's team's study", "Barbara Tuchman's The Guns of August".

### S4 Relationship (1, hard)

3.11 asks how the texts relate. Options describe each text's function; the key says, in effect, that Text 1 reports findings plus another team's explanation of them and Text 2 adds detail that casts doubt on that explanation. This is Text Structure and Purpose vocabulary applied to a pair: presents, discusses, argues, advocates, describes a critique, offers details, calls into question, reconciles.

## 3. Passages

### Subject areas

| Area | easy | medium | hard | total | Items |
|---|---|---|---|---|---|
| Natural science (biology, ecology, astronomy, physics, chemistry, earth science, paleontology) | 5 | 4 | 8 | 17 | 1.8, 1.10, 1.12, 1.14, 1.15, 2.1, 2.2, 2.5, 2.9, 3.2, 3.3, 3.4, 3.5, 3.6, 3.11, 3.12, 3.13 |
| Social science (political science, psychology, economics, geography, linguistics, anthropology) | 2 | 5 | 1 | 8 | 1.1, 1.16, 2.3, 2.7, 2.8, 2.10, 2.11, 3.14 |
| Arts (dance, art history, painting, music, sculpture, theater, film and games) | 5 | 1 | 1 | 7 | 1.2, 1.3, 1.4, 1.7, 1.13, 2.4, 3.7 |
| Literature (criticism, authorship, literary history) | 2 | 0 | 3 | 5 | 1.9, 1.11, 3.1, 3.8, 3.9 |
| History | 2 | 0 | 1 | 3 | 1.5, 1.6, 3.10 |
| Philosophy | 0 | 1 | 0 | 1 | 2.6 |

Hard leans to natural science (8 of 14) and literature criticism (3); easy leans to arts and accessible science.

### Genre

All 41 are "two short texts": two informational or argumentative paragraphs headed Text 1 and Text 2. There are no literary excerpts, attribution lines, poems, tables, graphs or notes. Italics mark only titles and species names. 11 items underline part of a text (10 in Text 1, 1 in Text 2): 4 whole sentences and 7 clauses (often after "Thus," or "but"), 8 to 27 words (median 18), and the underlined part is always the single sentence or clause the stem targets (a claim in 10, a situation in 1.16).

Text 2 never names Text 1 or its author. The link is topical: 27 of 41 pairs share a proper noun (the same researcher, place or work), and the rest share a subject (bluegrass, curiosity, emotional contagion). 20 of 41 Text 2s contain an explicit contrast or negation word (However, Although, While, Yet, Instead, not, n't, "challenges", "weakened"), but only 7 signal it in the first sentence. So in about half the items the relation must be inferred from content alone.

### How the texts are built

**Text 1** (four recurring frames):
- Reported claim (most common): context, then a named party's claim, then its basis, often closing on "Thus," (1.1 Fowler on compulsory voting; 2.5 Siraj's comet hypothesis; 3.13 Storey's chicken bone; 3.12 Potvin's magpies; 3.11 Wang plus Miller and Simpson).
- Standard view: "Most scientists agree", "Conventional wisdom long held", "the consensus view among researchers", "Some theorists have argued", "many scholars had assumed" (1.8, 3.14, 2.8, 3.5, 2.7). Built to be overturned or limited by a newer study in Text 2.
- Problem statement: a field's difficulty (2.11 inconsistent urban definitions, 3.6 unreliable fossil dating) or a practice that avoids one (3.7 film credits).
- Author's thesis (arts, literature, history): an evaluative claim in the author's own voice (1.9 Soyinka in three periods, 3.9 Orlando as an oddity, 3.10 Tuchman's weaknesses, 1.11 neglect of cookbooks).

**Text 2** (typical move order): named researcher or team plus method, then finding, then an implication that bears on Text 1's claim ("It is thus likely that competition ..., not temperature, limits ...", "The timing suggests that ..."). Alternatives: a concession then a counterpoint ("While Strassburg's team's findings certainly offer encouraging insight, it's important to consider ..."; "In their destabilizing effect ..., the sermons ... recall those in Ellison's. Yet ..."), or a flat counter-thesis in the first sentence ("Bluegrass isn't simply ...", "Adolphe Appia was not an amateur ..."). 19 of 41 Text 2s are built around a reported study; 22 are the author's own argument.

### Names, dates, places

Real scholars, introduced with a role label and full name ("Public policy researcher Anthony Fowler", "Art historian and archaeologist Lisa Trever", "Ecologist Juan Amat"), then surname only. Teams appear as "X and colleagues", "X et al.", "a team led by X", "researchers from [institution]". 17 of 41 passages carry a year (1577 to 2022); recent study years (2007, 2010, 2015, 2020, 2021, 2022) mark the newer side of a debate. Places are specific (Sterkfontein Caves, El Arenal, Svalbard, Freetown, Bologna). Numbers are sparse and never needed for calculation.

### Vocabulary

Easy passages are plain (mean word length 5.0 letters; 11.3% of words have 9 or more letters). Medium and hard are academic (5.2 letters; 15.7% and 15.3% long words): "conjugation", "physiochemical", "pastoralism", "stratigraphic", "interpolated", "preponderance", "implausibly reductive". Hard passages define technical terms inline with dashes or parentheses (eDNA, nanohybrids, breccia, emotional contagion). Em dashes appear in 14 passages.

## 4. The correct answer

**Justification.** The key always needs both texts. In S1 it is the speaker's position applied to the target. In S2 it is the proposition each text entails separately. In S3 it is a pair of paraphrases, one per text, on the same dimension.

**What the key names.** In respond items, the key usually names the thing the speaker's text has and the target lacks: iridium (2.5), populations that adapt (2.9), contagion without in-person contact (2.10), Appia's apprenticeship (2.4), an earlier Bolognese painting (1.4), a second cause of pinkness (1.15), a wider cultural tradition (3.8). That missing piece is the core of the answer.

**Paraphrase vs echo.** Keys paraphrase at a slightly higher level of abstraction than the passage ("mode of subsistence" for pastoralism; "a widespread practice in film and television" for crediting). Measured as the share of an option's content words found in the passage:

| Tier | Key | Distractors |
|---|---|---|
| easy | 0.53 | 0.43 |
| medium | 0.37 | 0.36 |
| hard | 0.34 | 0.42 |

Easy keys echo the passage more than their distractors; hard keys echo it less (hard distractors recycle passage words to sound right).

**Hedging.** 16 of 41 keys (39%) carry a hedge (may, might, likely, probably, not necessarily, some, certain), against 30 of 123 distractors (24%). Typical key hedges: "does not necessarily lead to", "may not be exclusively motivated", "might be adequately explained without", "not inevitably". Strong words (only, exclusively, must, greatly, inevitable, regardless, primarily, mostly) appear in 22% of distractors and 17% of keys, so that signal is weak.

**Length.** The key is the longest option in 9 of 16 easy items, 4 of 11 medium and 3 of 14 hard (16 of 41). In easy items the key averages 16.8 words against 16.1 for distractors; in medium and hard it is slightly shorter (16.2 vs 17.9, 22.6 vs 23.3).

**Verb tells in "By ..." options.** Across the 14 By-items: "noting" is correct 4 of 4 times, "observing" 1 of 1, "cautioning" 1 of 1, "pointing out" 3 of 6; while "arguing" is correct 1 of 7, "suggesting" 1 of 5, and "conceding", "concurring", "insisting", "praising", "claiming", "asserting", "recommending" are never correct (0 of 17 together). Mild observation verbs mark keys; advocacy and concession verbs mark distractors. This is a test-taking tell in the official set that generated items should not reproduce systematically.

## 5. Distractor recipes

123 wrong options, each coded with its main flaw:

| Code | Archetype | easy | medium | hard | total |
|---|---|---|---|---|---|
| D1 | Unaddressed add-on: a plausible claim on the topic that neither text supports (a new factor, comparison or recommendation) | 20 | 11 | 4 | 35 |
| D3 | Twisted detail: recycles a word or detail from a passage into a claim the passage does not make | 12 | 7 | 14 | 33 |
| D2 | Wrong side: gives the speaker the other text's stance, or the reverse of its own | 6 | 9 | 7 | 22 |
| D7 | Half right: two-part option with one correct clause and one unsupported or wrong clause | 0 | 0 | 9 | 9 |
| D6 | Right verdict, wrong reason: the stance or label could fit, but the "because" is not the speaker's reason | 6 | 0 | 2 | 8 |
| D5 | Overstatement: right direction, too absolute (only, exclusively, denying, crucial) | 2 | 3 | 1 | 6 |
| D8 | Wrong target or dimension: answers about a different claim, or a different axis of the disagreement | 2 | 1 | 2 | 5 |
| D9 | Generic academic move: more research is needed, look at other topics | 0 | 2 | 1 | 3 |
| D4 | One text only (agreement items): one author would accept it, the other would reject it | 0 | 0 | 1 | 1 |
| D10 | Understatement: too mild a verdict for a clear refutation | 0 | 0 | 1 | 1 |

Examples (paraphrased unless quoted):
- **D1** 1.1: only countries of a certain population size should require voting (no text mentions population). 2.11: recommending an institution investigate the problem.
- **D3** 1.15: "tail feathers are pinker than their other feathers" bends Text 2's gland "near their tail". 3.4: a claim about molecular weight built from Text 2's "low molecular weights" detail.
- **D2** 2.2: the experiment "is consistent with ... a microscopic level but not at a macroscopic level", the reverse of what the experiment shows. 3.14: hierarchical roles absent before agriculture, which Text 2's "esteemed individuals" contradicts.
- **D7** 3.9: agreeing that Orlando is less impressive, but calling it a classic (the concession is one the author never makes). 3.10: the Text 1 half is right ("relied more on the work of other historians"), the Text 2 half is invented.
- **D6** 1.7: the purists' view "as shortsighted, because bluegrass could enlarge its audience" (Text 2 would reject purism, but not for that reason). All three wrong options in 1.7 and 1.11 are this type: As-adjective items are built by keeping the attitude plausible and swapping the reason.
- **D5** 2.8: people seek apparently useless information "only because they think they can use it later". 3.2: denying the risk is likely at all.
- **D8** 1.8: the moon formed "much earlier" (timing) where the texts differ on speed. 2.10: about smiling as evidence, not about the in-person requirement.
- **D9** 3.3: more research needs to be conducted into the causes.

In agreement items, the wrong options split into: true for one text only or contradicted by the other (1.6 "likely not a real person" overstates Text 2; 3.1 Shakespeare's complete works, which Sykes would reject), and topic add-ons that neither text addresses (1.12 nests, genetics, better tools). In difference items, the wrong options mismatch the dimension (1.14 percentage of farmland, carbon vs biodiversity) or invent a view for one author.

## 6. Difficulty

What separates the tiers, concretely:

| Signal | easy | medium | hard |
|---|---|---|---|
| Subtype mix (respond / agree / difference / relate) | 8 / 5 / 3 / 0 | 9 / 2 / 0 / 0 | 10 / 2 / 1 / 1 |
| Mean option length (words) | 16.3 | 17.5 | 23.1 |
| Two-clause options (but / whereas / while) | 6 (all in difference items) | 0 | 19 |
| Long-word share in passages | 11.3% | 15.7% | 15.3% |
| Share of distractors that are unaddressed add-ons (D1) | 42% | 33% | 10% |
| Share of distractors that are twisted details or half right (D3 + D7) | 25% | 21% | 55% |
| Key vs distractor echo of passage words | 0.53 vs 0.43 | 0.37 vs 0.36 | 0.34 vs 0.42 |
| Key is the longest option | 9 of 16 | 4 of 11 | 3 of 14 |

Qualitative differences:
- **Relation complexity.** Easy items rest on a flat contradiction (Text 2 says the opposite of Text 1: 7 of the 14 "challenge" items are easy) or on agreement over a surface fact (5 of the 8 "agree despite difference" items). Hard items rest on partial relations: concede and rebut (3.2, 3.9), same conclusion with better evidence (3.13), a shared methodological assumption (3.1, both rely on Fletcher's distinct style), a joint inference from two experiments (3.4), solution mapping (3.6, 3.7), or a function description of each text (3.11).
- **Inference steps.** Easy: one step (negate or confirm the target). Hard: two or three (find what Text 2 grants, what it rejects, and on what grounds; or derive a fact neither text states).
- **Distractor closeness.** Easy distractors mostly bring in new topics, so a student can reject them by asking "is this mentioned?". Hard distractors use the passage's own vocabulary and are wrong in one clause or in the strength of the verdict.
- **Passage length is not a lever**: medians 135.5, 138, 137.5 words.
- **Vocabulary and abstraction.** Medium and hard passages use discipline terms and abstract nouns, and the key is phrased one level more abstract than the text.

## 7. Skill-specific inventory

### 7.1 Relationship types between the two texts

Every item was coded for how Text 2 stands to Text 1 (or the reverse when Text 1 is the speaker).

| Relation | Definition | easy | medium | hard | Items |
|---|---|---|---|---|---|
| **Challenge / refute** | Text 2 says Text 1's claim is wrong, using new data, a counterexample, a rival hypothesis or a reinterpretation | 7 | 3 | 4 | 1.1, 1.3, 1.4, 1.7, 1.8, 1.9, 1.16, 2.4, 2.5, 2.10, 3.3, 3.5, 3.11, 3.14 |
| **Qualify / complicate** | Text 2 accepts part of Text 1 but limits its scope or strength, adds a second cause, or offers a competing explanation that is possible rather than proven | 3 | 3 | 4 | 1.10, 1.14, 1.15, 2.7, 2.8, 2.9, 3.2, 3.8, 3.9, 3.12 |
| **Agree despite difference** | the texts differ on cause, interpretation or emphasis but share a premise | 5 | 2 | 1 | 1.2, 1.5, 1.6, 1.12, 1.13, 2.1, 2.3, 3.1 |
| **Solution to a problem** | one text names a problem, the other supplies a method or practice that solves it | 0 | 1 | 2 | 2.11, 3.6, 3.7 |
| **Case fits the other text's frame** | Text 2 is an instance or piece of evidence that Text 1's general claim explains | 1 | 2 | 0 | 1.11, 2.2, 2.6 |
| **Same conclusion, new evidence** | Text 2 accepts Text 1's conclusion but replaces its weakened evidence with stronger evidence | 0 | 0 | 1 | 3.13 |
| **Complementary findings, joint inference** | two compatible studies that together imply something neither states | 0 | 0 | 1 | 3.4 |
| **Parallel critiques** | both texts criticise the same work, on different grounds | 0 | 0 | 1 | 3.10 |

How the challenge is made (14 items): new study data contradicts the claim (1.1, 1.8, 1.16, 2.10, 3.3, 3.5); counterexample to a "first" or "requires" claim (1.4 an earlier painting, 2.4 an apprenticeship); rival hypothesis with evidence (2.5 asteroid and iridium); reinterpretation or framework critique (1.3 realism vs creativity, 1.7 bluegrass was always mixed, 1.9 phases as limiting, 3.14 no linear stages); undermining the mechanism of an explanation (3.11 surface remains do not last).

How the qualification is made (10 items): limit the degree (1.10 emotions "likely very rudimentary"); add a caveat or cost (1.14 food supply); add a second cause (1.15 gland pigments; 3.8 a community tradition as well as Ellison; 2.8 usefulness as well as information for its own sake); widen a too-narrow claim (2.7 symbols could be words or syllables); local counterexample to a generalization (2.9 Svalbard bears adapting); concede and narrow (3.2 conjugation can also reduce toxicity; 3.9 lighter in tone but thematically central); possible alternative explanation (3.12 novelty, not altruism).

The agreement items, by what is shared: same phenomenon, rival causes (1.5 cassava spread slowly; 1.12 birds restricted to elevations); dispute over facts, same reception (1.6 Ludington widely admired); same premise, different emphasis (1.2 jazz shaped Ailey's work; 1.13 Lewis's subjects varied); same conclusion from different readings of a null result (2.1 conditions are hostile to microbes); convergent trends (2.3 consumer behavior is reshaping music businesses); shared methodological assumption under an authorship dispute (3.1).

### 7.2 Stem variants (speaker x verb x target)

- Verbs: respond 18, say about 3, characterize 2, regard 2, describe 1, suggest (for someone in a situation) 1; agree 9; "a difference in how ... view" 4; "relate to each other" 1. Section 1 has the exact wordings and counts.
- Speaker labels: "the author of Text 2" 12, named or role-labelled party of Text 2 11 ("Singh and Roy (Text 2)", "Lisa Trever (Text 2)", "the ecologist in Text 2", "Artemieva", "Dubey and colleagues (Text 2)", "the researchers in Text 2" x3, "Chris Brierley (Text 2)", "Cáceres and colleagues (Text 2)", "Graeber and Wengrow (Text 2)"), "the author of Text 1" 4.
- Target labels name the kind of speech act: research, interpretation, claim, conclusion, assertion, hypothesis, theory, view, consensus view, perspective, assessment, problem, discussion, situation, "conventional wisdom", experiment, proponents of a stance. The label is a hint: "problem" signals a solution key (2.11), "assessment" an evaluative reply (3.9), "hypothesis" a rival hypothesis (2.5), "consensus view" or "conventional wisdom" a challenge (2.8, 3.14).
- The option shell follows the verb: "respond" mostly takes By-gerund (13 of 18) or a statement; "regard" and "characterize" take As-adjective (3 of 4); "say about" takes It-statements (2 of 3) and "describe" one (3.5); "suggest for someone" takes imperatives.

### 7.3 How the key is derived in "how would [Text 2 speaker] respond" items

A procedure that reproduces all 27 S1 keys:

1. Reduce the target to one proposition P (the underlined sentence, the named claim, or the main claim of the other text).
2. Reduce the speaker's text to its finding F and what F implies for P.
3. Classify the relation (7.1) and phrase the key from the matching template:

| Relation | Key template (own words) | Items |
|---|---|---|
| Refuted by new data | P is not necessarily so / P is likely wrong, given F | 1.1, 1.3, 3.3, 3.5 |
| Counterexample | F is an earlier or opposite case, so P's "first / requires / lacked" is false | 1.4, 2.4, 2.10 |
| Rival hypothesis | P fails to account for E (the evidence behind the rival) | 2.5 |
| Framework critique | label P's approach (illogical, limiting) and give the overlooked fact | 1.7, 3.14 |
| Limit degree or scope | if P holds at all, it holds only weakly / only sometimes | 1.10, 2.8 |
| Second cause or factor | P is incomplete: X is not the only cause | 1.15, 3.8 |
| Widen or correct | P overlooks aspects that F shows | 2.7, 2.9 |
| Concede then rebut | agree with part A of P, but F shows not-B | 3.2, 3.9 |
| Alternative explanation | the behavior might be explained without P | 3.12 |
| Same conclusion, better evidence | P is persuasive, but F supports it better than P's own evidence | 3.13 |
| Solution | F (method or practice) answers the problem in P | 2.11, 3.6, 3.7 |
| Case fits frame (Text 1 speaking) | F is unsurprising / is evidence for the frame / runs into the frame's objection | 1.11, 2.2, 2.6 |
| Practical advice | do the thing F recommends | 1.16 |

4. Keep the key at the speaker's level of commitment. If the speaker's text hedges ("may", "possibly", "it can be difficult to exclude"), the key hedges too (1.3, 2.8, 3.12). If the speaker grants part of P, the key grants it ("By agreeing that ... but pointing out that ..."). Most distractor traps are a commitment level the speaker does not have: denial where the speaker concedes (3.2 C), concession where the speaker rejects (3.14 A), praise where the speaker is neutral (2.5 C).
5. Aim the key at P, not at a side detail of the target text (D8 traps answer about smiling in 2.10, or the timing of formation in 1.8).
6. Express it in the stem's shell. In By-gerund items the gerund encodes the stance (noting, pointing out, cautioning, disputing, acknowledging ... but insisting), and the that-clause carries the content.

For "both would agree" items the key is found by listing what each text takes for granted before it argues, and keeping the item that survives in both (1.5: whatever the cause, cassava caught on long after it arrived; 1.6: whether or not the ride happened, Ludington is admired). For difference items the key names the axis first (speed of formation, attitude to the findings, the source of the flaw) and states each author's value on it.

### 7.4 Relationship cues in the passages

- Openers of a challenge: "challenges the idea that" (3.3), "weakened the case for" (3.13), "was not an amateur" (2.4), "isn't simply" (1.7), "In reality" (1.7), "It is tempting to ... However" (1.9), "However, forcing people ... may have negative consequences" (1.1).
- Qualifiers: "Still," (1.10), "While ... certainly offer encouraging insight, it's important to consider" (1.14), "has drawn deserved attention, but ... vary by case" (3.2), "Though it is lighter in tone ... nonetheless" (3.9), "While acknowledging that ..." (2.8), "At the same time, it can be difficult to exclude" (3.12).
- Conclusion markers: "Thus" in 4 Text 1s and 4 Text 2s; "suggests", "It is thus likely that", "the preponderance of evidence now favors".
- About half the items carry none of these; the reader must infer the relation from the findings alone.

## 8. Generation blueprint

### Slots (shared by all subtypes)

- `field`, `topic` (one natural phenomenon, social pattern, artwork, author or historical event).
- Text 1: `frame` (reported claim, standard view, problem, author's thesis), `claim_P` (one sentence, underlinable), `basis_1` (one or two sentences), optional "Thus" conclusion. 55 to 85 words, 3 to 4 sentences.
- Text 2: `speaker` (role label plus full name, or "researchers from [institution]", or the author's voice), `method_or_evidence`, `finding_F`, `implication` linking F to the topic without mentioning Text 1. 50 to 85 words, 3 to 4 sentences.
- `relation` from 7.1, which fixes the key template.
- Stem: `speaker_phrase` x `verb` x `target_label` (+ underline), assembled by grammar.
- Options: shell type, key, three distractors with assigned archetypes.

### S1 Response prediction (build first: 27 of 41, two thirds of the skill)

- Answer logic: section 7.3, steps 1 to 6.
- Distractors: easy, two D1 add-ons plus one D2 or D3; medium, one each of D1, D2, D3 (or D5); hard, D3 and D7 heavy (two half-right two-part options and one twisted detail or wrong side). For As-adjective shells, keep three plausible attitudes and give each a reason the speaker never gives (D6). For two-part By shells, build distractors by recombining clause halves: right concession plus wrong rebuttal, wrong concession plus right rebuttal, denial instead of concession.
- Programmatic: stem assembly; underline markup and its position; option shells (By / As / It); clause recombination for D7; verb assignment (balance mild and strong verbs between key and distractors so the 7.3 verb tell disappears); letter balancing.
- Needs an author or LLM: both texts, the key paraphrase (one abstraction step above the passage), the D1 and D3 content.

### S2 Agreement

- Slots add `shared_premise` (what both texts assume) and `conflict_point` (what they argue about).
- Answer logic: the key is the shared premise, stated neutrally and at the topic level ("X did not become significant until long after it was introduced"). Each text must entail it on its own.
- Distractors: one D4 (Text 1 only or Text 2 only, ideally the conflict point stated as fact), one D1 add-on, one D3 twisted detail or D5 overstatement. Hard variant: a shared hidden assumption (3.1 pattern) or a joint inference from two experiments (3.4 pattern).

### S3 Difference

- Slots add `axis` (speed, attitude, method, source of flaw) and the two values.
- Answer logic: "The author of Text 1 [value 1], whereas the author of Text 2 [value 2]" or a comparative "more ... than".
- Distractors: right axis with values swapped (D2); a second axis neither text discusses (D1, D8); one half right, one half invented (D7). Programmatic: comparative and whereas shells, value swaps. Authored: the axis and paraphrases.

### S4 Relationship

- Options are function descriptions for each text ("presents findings and an attempt to explain them" / "calls that explanation into question"). Distractors misassign functions (D3), reverse the stance (D2) or move a function to the wrong text. Low volume: 1 in 41.

### Automatic checks

1. Format: passage matches `Text 1\n\n...\n\nText 2\n\n...`; each text 50 to 90 words, total 110 to 160; at most one `<u>` span, present if and only if the stem says "underlined", and located in the text the stem names.
2. Speaker check: a named speaker in the stem appears only in the text the stem assigns ("(Text 2)").
3. No cross-reference: neither text mentions "Text 1", "Text 2" or "the author".
4. Option shells: all four options share the same opener type and end the same way (By options without a period, statements with one); lengths within 30% of each other; across a set, key is longest in at most about 30% of items.
5. Tell control: across a set, each By-verb appears in keys and distractors in rough proportion; at least one distractor is hedged when the key is hedged; key content-word overlap with the passage no more than 0.1 above the highest distractor in medium and hard items.
6. Model adjudication: an independent model solves the item from both texts and must choose the key and cite one sentence from each text; given each distractor, it must fail to find support (or find a contradiction). Ablation: given only the speaker's text, a respond or agree item should not be solvable above chance when its key depends on the target; for agreement items, an entailment check per text must pass for the key and fail for each distractor in at least one text.
7. Relation check: the model labels the relation from the passage alone; it must match the template the item was built from.

### Quality risks

- Real people and findings. The official set uses real scholars and real studies. Generated items should use invented researchers and institutions, or describe real phenomena only in ways that are accurate; invented findings attached to real names would be misinformation.
- Defensible D1 add-ons. A plausible recommendation (1.1 option D: make voting easier) may be something the speaker would in fact endorse; the adjudication step must ask "does the text support it", not "is it reasonable".
- Qualify vs challenge ambiguity. If Text 2's finding is ambiguous, "it is wrong" and "it is incomplete" both look right. Fix the commitment level in the Text 2 wording ("may", "not only", "rather than") before writing options.
- Over-signposting. Generated Text 2s tend to open with "However, this view ignores ...". Only 7 of 41 official Text 2s signal contrast in their first sentence; vary it, and leave about half without explicit contrast words.
- Single-text solvability. Keys that merely restate Text 2's finding make Text 1 irrelevant; the key must be phrased in terms of Text 1's claim.
- Tells. Avoid "noting" and "pointing out" only in keys, and avoid hedged keys against absolute distractors every time.

### Recommended scale and order

Templates: about 14 distinct templates. S1: refuted by new data, counterexample, rival hypothesis, framework critique, limit degree, second cause, concede then rebut, alternative explanation, solution, case fits frame (Text 1 speaking) = 10. S2: rival causes shared fact, shared hidden assumption, joint inference = 3. S3: one comparative/whereas template with axis slot = 1 (S4 as a variant of S3 for hard).

Items per tier (first release, 40 per tier, mix tilted from the bank's proportions):

| Tier | Respond | Agree | Difference | Relate |
|---|---|---|---|---|
| easy | 20 | 13 | 7 | 0 |
| medium | 28 | 8 | 4 | 0 |
| hard | 28 | 6 | 3 | 3 |

Build order: (1) S1 with Text 2 speaking about Text 1, By-gerund options, challenge and qualify relations (20 of the 27 S1 items fall in these two families); (2) S2 rival-cause agreement items for easy; (3) S3 difference; (4) hard variants: concede-then-rebut two-part options, same conclusion with better evidence, joint inference, Text 1 speaking about Text 2, and the relate stem.
