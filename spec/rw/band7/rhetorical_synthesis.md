# Rhetorical Synthesis: what makes a band-7 item

Source: every Rhetorical Synthesis item in `material/rw/cb_api/rhetorical_synthesis.json` with band 5, 6 or 7 (40, 23 and 20 items). All 20 band-7 and all 23 band-6 items were read with CB's rationale. Measures come from Python over the CB text; the passage measures use the bullet notes only (the intro line and goal sentence removed), because sentence splitting means nothing for bullets. Template, reasoning steps, derived keys and distractor recipes are hand annotations made while reading (listed per item in section 1). Gaps are band 6 against band 7 with AUC (chance that a random band-7 item scores higher; 0.50 is no separation) and a permutation p value. With about 20 items per band, treat p above 0.10 as "no reliable difference".

## 1. Counts

| | Band 5 | Band 6 | Band 7 |
|---|---|---|---|
| Items | 40 (all CB medium) | 23 (all CB hard) | 20 (all CB hard) |
| Notes with numbers | 30 | 14 | 17 |
| Two-part goals (make and support, describe and explain, X and Y) | | 6 | 3 |
| Already in our transcript set | 20 | 8 | 9 |

Template mix (goal types from `satbank/rw/rhetorical_synthesis.json`; two new names where none fit):

| Template | Band 6 | Band 7 |
|---|---|---|
| GEN (generalization, with or without support) | 3 | 4 |
| EXPL (explain how, why, significance) | 1 | 3 |
| DIFF (compare or contrast two items) | 2 | 3 |
| STUDY (aim, method, findings) | 5 | 2 |
| OVERVIEW | 3 | 1 |
| SIM | 1 | 1 |
| RANK | 0 | 1 |
| DESC | 1 | 1 |
| AUD_NEW | 0 | 1 |
| NARR | 0 | 1 |
| EMPH | 2 | 0 |
| SPEC | 1 | 0 |
| AUD_FAM | 1 | 0 |
| QUOTE | 1 | 0 |
| EXAMPLE | 1 | 0 |
| new CONTEXT (place X in its historical context, or in the context of someone's beliefs) | 1 | 1 |
| new REFUTE (refute a stated claim using the notes) | 0 | 1 |

Per-item assignment:
- Band 7: GEN 2c61e0b9 (kind of study), 3b02e88a (dhow materials), 3dcc7140 (nissologists, make and support), 7f5715e4 (farm-size hypothesis, make and support); EXPL 3fa48bf3 (Plot's reputation), 8fe4f4ab (House of Wisdom), ee51ad04 (nautical miles); DIFF 459df2ba (Fodor and Carruthers), 8e9e473d (dog ears), c34d6bff (Hedgeman and Bates); STUDY 5645f119 (findings), 973632d2 (aim); OVERVIEW 964c6055; SIM 19b08ead (significance of a similarity); RANK 5fa51c86; DESC b07a7634; AUD_NEW 96a86bce; NARR af88c47a; CONTEXT 7d5c32e6 (Einstein); REFUTE 07456405 (Storting).
- Band 6: GEN 0acc26b2, 622a351d, b0620764; EXPL d4b07ce6 (describe and explain); DIFF de01ccef, e98b1690; STUDY 5222ffab, 56b000d0, 8d1ddd1b, be3363dd, c40a1964; OVERVIEW 1773fa73, 5b8b69a2, b44141cf; SIM 9551ef8b; DESC cfade68d; EMPH 0fab0c90, 9336f63b; SPEC 87d34a39; AUD_FAM 39ccb463; QUOTE e8494245; EXAMPLE ec03f090; CONTEXT 1d79a59d (Valle).

Templates with no band-7 items: SPEC, EMPH, EXAMPLE, AUD_FAM, QUOTE. The band-6 mix leans on study slots (5 of 23 are STUDY, 3 of them "emphasize the aim" or "present the methods"); band 7 leans on generalization, explanation and comparison (10 of 20). Our transcripts drifted: 3.5, 3.11, 3.14, 3.15, 3.17, 3.21 to 3.24 are band 7; 3.8, 3.9, 3.10, 3.12, 3.16, 3.18, 3.19, 3.20 are band 6. Eight of our 13 authored hard items list a band-7 model.

## 2. What separates 7 from 6, measured

Rarity here is the share of lowercase note words past rank 10,000 in `tools/data/freq.txt` (the same lookup as the Words in Context report).

| Signal | Band 5 | Band 6 | Band 7 | AUC | p | Separates? |
|---|---|---|---|---|---|---|
| Notes words | 71.6 | 74.8 | 80.0 | 0.58 | 0.38 | no |
| Bullets | 5.05 | 5.22 | 5.15 | 0.47 | 0.66 | no |
| Words per bullet | 14.2 | 14.4 | 15.7 | 0.62 | 0.19 | weak |
| **Note words past rank 10,000** | 12.2% | 11.3% | 15.1% | 0.69 | 0.04 | **yes** |
| Characters per word (notes) | 4.97 | 4.98 | 5.30 | 0.66 | 0.07 | yes, small |
| Long-word rate (notes) | 12.3% | 13.1% | 16.6% | 0.65 | 0.11 | weak |
| Goal sentence words | 12.8 | 12.7 | 13.7 | 0.61 | 0.21 | no |
| Key length in words | 20.7 | 23.4 | 22.9 | 0.46 | 0.68 | no |
| Key length rank (1 = longest) | 2.35 | 2.17 | 2.05 | 0.48 | 0.82 | no |
| Key is the longest option | 28% | 30% | 35% | 0.52 | 1.00 | no |
| Key content words found in the notes | 85% | 80% | 74% | 0.39 | 0.22 | weak |
| Key content words new to notes and goal | 15% | 19% | 25% | 0.60 | 0.27 | weak |
| Bullets the key draws on (estimate) | 3.0 | 3.3 | 2.9 | 0.42 | 0.36 | no |
| Reasoning steps (mean) | | 1.87 | 2.15 | 0.62 | 0.15 | weak |
| Three-step items | | 2/23 | 4/20 | | | weak |
| Key states a derived claim the notes do not state | | 9/23 | 11/20 | 0.58 | 0.38 | no |
| **Misreading (FALSE) distractors per item** | | 0.43 | 0.90 | 0.62 | 0.15 | yes, as a count |
| **Items with two or more FALSE distractors** | | 2/23 | 7/20 | | | **yes** |
| **Items with a distractor that does the goal's job but misstates the notes** | | 6/23 | 10/20 | 0.64 | 0.07 | **yes** |
| Off-goal (OG) distractors per item | | 1.22 | 0.90 | 0.42 | 0.35 | no (falls) |
| Two-part goals | | 6/23 | 3/20 | | | no (falls) |

Clue distance does not apply to bullet notes; its analogue is how many bullets the key draws on, which does not separate (3.3 against 2.9).

Bullets the key draws on: a bullet counts when at least 30% of its content words (first five letters) appear in the option. Reasoning steps follow `spec/rw/rhetorical_synthesis.md` section 6: 1 = the goal noun points at one bullet; 2 = the key combines bullets or matches an attribute pair; 3 = the key derives a claim (a relation, a significance, a refutation) that requires checking a number or a mechanism across bullets.

What the numbers say:
1. **Band-7 distractors are wrong on the facts, not just off-goal.** The source report's hard-tier shift (FALSE rises, OG falls) continues from band 6 to band 7: FALSE distractors double (10 of 69 to 18 of 60) and seven band-7 items have two or more. The dangerous ones do exactly what the goal asks (they refute, compare, present both findings) and misstate a detail.
2. **Denser notes.** The share of rare words in the notes rises from 11% to 15% (malapportionment, cyanobacterium, nissologists, modularity, additive manufacturing). Notes length and bullet count do not change.
3. **No length or overlap signal.** Key length, key length rank and how many bullets the key uses are the same at both bands. Keys paraphrase a little more at band 7 (25% new words against 19%), not reliably.
4. **Band 6 and 7 overlap heavily.** Two "emphasize the aim of the research study" items with three slot-swap distractors sit at band 6 (56b000d0, c40a1964) and one at band 7 (973632d2); nothing in the text separates them. Expect some band-7 items whose difficulty is not visible in the item.

### Per-item annotations

Hand annotations behind the counts above, for audit. Distractor recipes are in option order, key left out.

| cb_id | band | template | steps | derived key | goal-shaped false distractors | distractor recipes |
|---|---|---|---|---|---|---|
| 96a86bce | 7 | AUD_NEW | 2 | - | 0 | AUD, OG, PART |
| 7d5c32e6 | 7 | CONTEXT | 2 | yes | 1 | FALSE, OG, PART |
| b07a7634 | 7 | DESC | 2 | - | 3 | FALSE, FALSE, FALSE |
| 459df2ba | 7 | DIFF | 3 | yes | 2 | PART, FALSE, FALSE |
| 8e9e473d | 7 | DIFF | 2 | - | 1 | FALSE, FALSE, REL |
| c34d6bff | 7 | DIFF | 2 | - | 0 | PART, REL, VAGUE |
| 3fa48bf3 | 7 | EXPL | 2 | yes | 2 | FALSE, PART, FALSE |
| 8fe4f4ab | 7 | EXPL | 2 | - | 0 | VAGUE, OG, PART |
| ee51ad04 | 7 | EXPL | 3 | yes | 1 | PART, FALSE, OG |
| 2c61e0b9 | 7 | GEN | 2 | yes | 0 | OG, OG, OG |
| 3b02e88a | 7 | GEN | 2 | yes | 0 | PART, OG, OG |
| 3dcc7140 | 7 | GEN | 2 | yes | 0 | OG, PART, OG |
| 7f5715e4 | 7 | GEN | 3 | yes | 1 | FALSE, OG, PART |
| af88c47a | 7 | NARR | 2 | - | 0 | OG, PART, PART |
| 964c6055 | 7 | OVERVIEW | 2 | - | 0 | VAGUE, PART, PART |
| 5fa51c86 | 7 | RANK | 2 | yes | 0 | LIST, OG, LIST |
| 07456405 | 7 | REFUTE | 2 | yes | 1 | FALSE, FALSE, OG |
| 19b08ead | 7 | SIM | 3 | yes | 2 | FALSE, PART, FALSE |
| 5645f119 | 7 | STUDY | 2 | - | 2 | PART, FALSE, FALSE |
| 973632d2 | 7 | STUDY | 1 | - | 0 | OG, OG, OG |
| 39ccb463 | 6 | AUD_FAM | 2 | - | 0 | AUD, AUD, PART |
| 1d79a59d | 6 | CONTEXT | 2 | - | 1 | PART, FALSE, PART |
| cfade68d | 6 | DESC | 1 | - | 0 | OG, REL, REL |
| de01ccef | 6 | DIFF | 2 | yes | 0 | REL, REL, OG |
| e98b1690 | 6 | DIFF | 3 | yes | 0 | OG, FALSE, OG |
| 0fab0c90 | 6 | EMPH | 2 | yes | 0 | OG, PART, OG |
| 9336f63b | 6 | EMPH | 2 | yes | 0 | OG, OG, OG |
| ec03f090 | 6 | EXAMPLE | 2 | - | 2 | PART, FALSE, FALSE |
| d4b07ce6 | 6 | EXPL | 2 | yes | 1 | PART, FALSE, PART |
| 0acc26b2 | 6 | GEN | 2 | - | 0 | PART, OG, PART |
| 622a351d | 6 | GEN | 2 | - | 0 | OG, PART, PART |
| b0620764 | 6 | GEN | 2 | yes | 1 | FALSE, OG, OG |
| 1773fa73 | 6 | OVERVIEW | 2 | - | 0 | PART, OG, PART |
| 5b8b69a2 | 6 | OVERVIEW | 2 | yes | 0 | PART, VAGUE, PART |
| b44141cf | 6 | OVERVIEW | 3 | yes | 0 | PART, FALSE, FALSE |
| e8494245 | 6 | QUOTE | 2 | - | 1 | NOQ, NOQ, FALSE |
| 9551ef8b | 6 | SIM | 2 | yes | 0 | PART, REL, PART |
| 87d34a39 | 6 | SPEC | 1 | - | 1 | OG, OG, FALSE |
| 5222ffab | 6 | STUDY | 2 | - | 0 | OG, PART, OG |
| 56b000d0 | 6 | STUDY | 1 | - | 0 | OG, OG, OG |
| 8d1ddd1b | 6 | STUDY | 2 | - | 0 | OG, PART, OG |
| be3363dd | 6 | STUDY | 1 | - | 0 | OG, OG, OG |
| c40a1964 | 6 | STUDY | 1 | - | 0 | OG, OG, PART |

## 3. What separates 7 from 6, read

1. **The goal-shaped false option.** 07456405 asks to refute a claim that malapportionment "favors small urban districts". Option B opens "It's untrue that malapportionment ... favors small urban districts" and then says the formula "overrepresents more populated districts", which the notes contradict. The key never says "untrue"; it states what the formula does. A student who checks only goal fit picks B.
2. **Numbers attached to the wrong noun.** 5645f119: "52% more total phosphorus than the control" becomes "52% more market-quality flower blooms" (B) and "removed 52% of phosphorus" (D). The key drops the numbers: FTWs "not only helped remove phosphorus ... but also yielded market-quality blooms".
3. **Process steps with a swapped agent.** b07a7634 (Digital Light Synthesis): all three distractors misdescribe the cure (the UV light is baked; DLS passes through the dead zone; curing completes in the dead zone). The student must trace four "Step" bullets.
4. **The derived relation.** 19b08ead: the similarity between two DNA kits is that both were "deemed by the researchers to be less effective than Pbact" for "insufficient yield or purity", which follows only from "the only one with both". 459df2ba: Fodorian modularity "is not as expansive in its definition ... as MMH is"; two distractors name the wrong dimension of difference. ee51ad04: nautical miles are "an efficient way to calculate distances at sea", a reason the notes imply but never state.
5. **The generalization one level up.** 2c61e0b9: the key "Researchers have used statistical methods to address questions of authorship" (in music) against three true statements about one song. 3b02e88a: "Although most materials used in dhow replicas are traditional, some modern materials are used."
6. **The right compared entity.** 8e9e473d compares dog breeds, not ear types (C compares the ears); c34d6bff compares contributions to the march, not careers (B).
7. **Unusual goal wording.** "refute a claim", "emphasize the significance of a similarity", "make a generalization about the kind of study", "place Einstein's argument within its historical context". Band 6 has one such goal (place the Declaration in the context of Valle's beliefs).

How band 6 is hard instead: study-slot swaps (aim, method, findings), make-and-support goals where one distractor gives only the claim and one only the example, and audience clauses. The distractors are mostly true.

## 4. Distractor recipes at band 7

Recipe codes from `spec/rw/rhetorical_synthesis.md` section 5.

| Recipe | Band 6 (69 distractors) | Band 7 (60) |
|---|---|---|
| OG accurate, serves another goal | 28 (41%) | 18 (30%) |
| PART only part of the goal | 21 (30%) | 16 (27%) |
| FALSE misstates, reverses or overstates | 10 (14%) | 18 (30%) |
| REL wrong relation or dimension | 5 | 2 |
| VAGUE | 1 | 3 |
| LIST | 0 | 2 |
| AUD | 2 | 1 |
| NOQ | 2 | 0 |

- **FALSE ties OG as the main recipe at band 7.** Its forms: wrong attachment of a number (5645f119), swapped agent (7d5c32e6 gives Einstein's view to Bohr; b07a7634), reversal (07456405 A, 8e9e473d B), scope shift (3fa48bf3 A: first to find *M. carinatus* remains rather than dinosaur remains), overclaim (3fa48bf3 D "disproved his claims"), wrong dimension stated as fact (459df2ba C and D).
- **The hardest distractor at band 7 is goal-shaped and false**: 16 such distractors in 10 band-7 items, against 7 in 6 band-6 items. Build it by writing the key's sentence pattern (refutation, comparison, two-finding summary) and changing one fact.
- **OG falls.** At band 6, three items have three accurate off-goal options (two of them study-slot items); at band 7, two.
- **LIST appears only at band 7** (5fa51c86: two populations side by side, relation missing). **NOQ and AUD** stay rare.

## 5. Band-7 writing recipe

Settings common to every band-7 template:
- Notes: five bullets, about 80 words, one or two technical terms with a gloss; aim for at least 14% rare words (past rank 10,000) and 5.2 characters per word in the bullets.
- At least one bullet carries a number, a ranking word ("the only one with both") or an ordered process, so a distractor can misattach it.
- The key states the relation or significance the goal asks for, often without the raw numbers, and adds at most one derived phrase ("not as expansive as", "accounts for more of its country's population", "less effective than").
- Distractors: two FALSE (at least one goal-shaped: it does the goal's job and misstates one fact) and one OG or PART. Avoid three study-slot swaps; that is band 6.

Per template (what to change from band 6):
- **GEN.** Band 6: make and support, with one claim-only and one example-only distractor. Band 7: the generalization must climb a level ("the kind of study", "the materials used", "applicability of the hypothesis to Thailand"), and distractors are true specific statements or a claim-plus-false-support (7f5715e4 A says the farms expanded).
- **EXPL.** Ask "how" or "why" where the notes give a chain of three bullets (collect, translate, copy; nautical mile, latitude, curvature). Distractors: what the thing is (OG), a reason for a neighbor (charts against flat maps), and a reversed link (latitude coordinates do not account for curvature).
- **DIFF.** Make the compared dimension non-obvious (high-level systems, not low-level; contributions to the march, not careers; breeds, not ears). Distractors: a false difference on the wrong dimension, the right comparison of the wrong entities, one side only.
- **SIM.** Ask for "the significance of a similarity" so the key must name why two items are alike, derived from a ranking bullet. Distractors: a true similarity without significance, two false similarities with numbers.
- **STUDY.** For band 7, use "present the findings" with two numeric findings; the key drops the numbers, two distractors misattach them. The plain "emphasize the aim" version belongs at band 6.
- **RANK.** Two entities, two measures that point opposite ways (Hanoi larger, Ulaanbaatar a larger share). Key "Even though X ..., Y ..."; distractors LIST both numbers or switch to the countries.
- **DESC.** A four-step process in labelled bullets; three distractors each swap an agent or a step.
- **REFUTE (new).** A notes set that supports the opposite of a stated claim through a formula or rule. Key states what the rule does; the hardest distractor opens with "It's untrue that ..." and misstates the rule.
- **CONTEXT (new).** Place an argument or document in its historical setting: the key spans the setting and the later outcome ("During the dawn of quantum theory", then Bohr's view "would become the widely accepted view"); one distractor swaps whose argument is whose.
- **OVERVIEW, AUD_NEW, NARR.** Keep the band-6 shape and add a goal-shaped false distractor; NARR keys begin at the chronological start, AUD_NEW keys identify the unfamiliar place or term named in the goal (Angkor Wat, not Tan).
- **No band-7 items:** SPEC, EMPH, EXAMPLE, AUD_FAM, QUOTE. Use them for bands 5 and 6.

## 6. Checks

Automatic:

1. **Note register.** Share of lowercase note words past rank 10,000 in `tools/data/freq.txt` at least 14%, or characters per word at least 5.2. Band 7 mean 15.1% and 5.30, band 6 11.3% and 4.98 (AUC 0.69 and 0.66). Moderate.
2. **Anti-band-6 shape.** Reject a band-7 draft whose three distractors are all accurate off-goal study slots, or whose goal is "emphasize the aim" or "present the methods". Cheap and safe, but it only removes the commonest band-6 pattern.

Agent-run:

3. **Fact check of every option.** An agent marks each option true or false against the notes and says whether it does the goal's job. A band-7 draft needs at least two FALSE distractors (band 7: 7 of 20 items; band 6: 2 of 23) and at least one that does the goal's job while false (band 7: 10 of 20; band 6: 6 of 23). This is the main gate; it is reliable when the agent checks numbers and agents bullet by bullet.
4. **Derived relation.** The agent states whether the key's relation or significance phrase appears in the notes. Prefer keys whose relation is derived (band 7: 11 of 20; band 6: 9 of 23). Weak alone.
5. **Blind solve with goal fit only.** Give a solver the goal and the options without the notes; a band-7 draft should leave at least two options that fit the goal. This tests the goal-shaped distractor directly. Untested on the official set; use as a supplement to check 3.

Do not gate on: notes length, bullet count, key length or length rank, bullets used by the key, two-part goals. None separated band 7 from band 6, and expect some band-6 and band-7 items to look alike.
