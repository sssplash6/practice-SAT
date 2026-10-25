# Form, Structure, and Sense (Standard English Conventions): bank analysis

Source: 92 official items in `material/rw/transcripts/form_structure_and_sense.json`, keys in `material/rw/keys/form_structure_and_sense.json` (the transcript's `answer_letter` matches the key for all 92). Item ids are `tier.n` (1 = easy, 2 = medium, 3 = hard). Every item was checked against its page image; 57 items needed a change (22 content fixes such as restored blanks, accents, dashes and the rebuilt item 3.14, plus straight apostrophes turned into the printed curly `’` in 43 items). All numbers below were computed with Python over the corrected transcript; the rule, subtype and distractor labels are a hand coding of every item and every option.

## 1. Snapshot

| Tier | Items | A | B | C | D | Passage words (min / median / max) | Mean words per option | Sentences per passage (1 / 2 / 3+) |
|---|---|---|---|---|---|---|---|---|
| easy | 40 | 13 | 6 | 8 | 13 | 15 / 40.5 / 59 | 1.6 | 12 / 21 / 7 |
| medium | 24 | 9 | 5 | 5 | 5 | 10 / 45.5 / 61 | 3.1 | 10 / 13 / 1 |
| hard | 28 | 10 | 5 | 3 | 10 | 12 / 43.5 / 65 | 7.0 | 11 / 16 / 1 |
| all | 92 | 32 | 16 | 16 | 28 | 10 / 42 / 65 | 3.6 | 33 / 50 / 9 |

- Letters are skewed: A or D is the key in 60 of 92 items (65%). This is a property of the sample, not a rule; generated sets should balance letters.
- Passage length is flat across tiers (medians 40.5, 45.5, 43.5 words). Difficulty does not come from length. Option length does climb (1.6, 3.1, 7.0 words) because the hard tier is dominated by clause-length modifier options.
- Every passage is a single paragraph of informational prose with exactly one blank. No item has a table, graph, poem, notes list, underlined portion or second text.

### Stem wording variants

| Wording | Count |
|---|---|
| Which choice completes the text so that it conforms to the conventions of Standard English? | 92 |

There is one stem for the whole skill. The rule being tested is never named; the student has to infer it from what varies across the four options.

## 2. Subtypes

The skill is six grammar rule families. Each item tests exactly one, and the four options differ only along that rule's dimension.

| Rule family | easy | medium | hard | total | Option length |
|---|---|---|---|---|---|
| R1 Subject-verb agreement | 10 | 9 | 6 | 25 | 1 to 2 words (one 5-word set) |
| R2 Finite vs nonfinite verb forms | 11 | 2 | 5 | 18 | 1 to 4 words |
| R3 Modifier placement (dangling modifiers) | 0 | 4 | 12 | 16 | 3 to 23 words, clauses |
| R4 Verb tense and aspect | 10 | 2 | 1 | 13 | 1 to 4 words |
| R5 Pronoun-antecedent agreement (incl. its/their vs contractions) | 5 | 4 | 2 | 11 | 1 to 2 words |
| R6 Plural vs possessive nouns | 4 | 3 | 2 | 9 | 1 to 6 words |

Verb rules (R1, R2, R4) are 56 of 92 items (61%). Easy is almost all verbs plus a few pronoun and apostrophe items; hard is 43% modifier items.

### R1 Subject-verb agreement (25: 10 / 9 / 6)

**Definition.** The blank is the finite verb (or the verb plus a short complement) of a clause whose subject is fixed in the passage. All four options are finite.
**Task.** Find the head noun of the subject, ignore whatever sits between it and the blank, and match number. The key is singular in 18 items and plural in 7.
**What makes it work.** In all 25 items the key is the only option with the right number; the three distractors share the wrong number and vary tense or aspect. The student never has to choose a tense in an R1 item.

### R2 Finite vs nonfinite (18: 11 / 2 / 5)

**Definition.** The options are four forms of one verb that differ in finiteness: finite (agreeing present or past), -ing participle, `having` + past participle, `to` + base, and a few rarer forms.
**Task.** Decide whether the clause still needs its finite verb (11 items: 7 missing main verbs, 2 second verbs of a compound predicate, 1 subordinate-clause verb, 1 relative-clause verb) or whether the clause is already complete and the blank opens a nonfinite phrase (7 items: purpose infinitive 3, infinitive after "the first" 1, -ing participial phrase 3).
**What makes it work.** In 17 of 18 items the key is the only finite form (or the only nonfinite form) in the set. The exception, 3.19, offers three nonfinite forms and the student must choose the purpose infinitive.

### R3 Modifier placement (16: 0 / 4 / 12)

**Definition.** The sentence opens with a modifier that has no subject of its own (a participial phrase, preposition + gerund, past participle, or a noun-phrase appositive). The blank is the start of the main clause, and the options are four rewrites of the same clause.
**Task.** Identify who or what the opening modifier describes, then choose the option whose grammatical subject (the first noun phrase after the comma) is that thing. All four options are otherwise grammatical sentences carrying the same facts.
**Blank position.** 9 items put the blank mid-sentence (options are fragments that join the rest of the sentence, sometimes ending in `who`, `that`, `but`, a colon or a semicolon); 7 put it at the very end of the passage (options are full clauses ending in a period). These 7 are the only passage-final blanks in the bank.

### R4 Verb tense and aspect (13: 10 / 2 / 1)

**Definition.** The subject is fixed, all four options agree with it in number, and they differ in tense, aspect or mood.
**Task.** Find the time cue (a date or span, a relative-time phrase, a habitual marker, a parallel verb, a conditional frame, a future marker) and match it. Keys: simple present 5, simple past 4, past perfect 3, future 1.

### R5 Pronoun-antecedent agreement (11: 5 / 4 / 2)

**Definition.** The blank is a pronoun (subject 5, object 3, possessive determiner 3); in two items the pronoun comes with its verb (`it was`, `they accumulate`).
**Task.** Find the antecedent and match number (singular antecedent 8, plural 3). In the possessive items, also reject the contractions `it’s` and `they’re`.
**Not tested.** Pronoun case in the I/me, who/whom sense never appears. The only "case" contrast is possessive vs contraction.

### R6 Plural vs possessive nouns (9: 4 / 3 / 2)

**Definition.** The options spell one or two nouns with and without apostrophes: `X’s`, `Xs`, `Xs’`, `X`, plus `its`/`it’s` once.
**Task.** Decide for each noun whether it is plural, possessive, or both, using a number cue in the passage (`a screw`, `each genre’s`, the singular person named earlier).

## 3. Passages

### Subject areas

| Area | easy | medium | hard | total |
|---|---|---|---|---|
| Natural science (incl. space, math, engineering, technology) | 18 | 6 | 13 | 37 |
| Arts (visual art, music, film, drama, design, architecture) | 8 | 5 | 3 | 16 |
| Social science (economics, linguistics, psychology, anthropology, law, media) | 7 | 4 | 4 | 15 |
| History (incl. history of inventions) | 4 | 6 | 4 | 14 |
| Literature (authors, poems, novels, plays) | 3 | 3 | 4 | 10 |

Science is 40% of the bank. The topic never matters to the answer; it is set dressing for the grammar.

### Genre

All 92 are short informational paragraphs. There are no literary excerpts with attribution lines, no poems, no paired texts, no notes and no data displays. Literature appears only as a topic (a writer, a novel, a poem described from outside), and quotations from works are short and embedded (2.7, 3.9, 3.20).

### How the passage is built

- 33 passages are a single sentence (12 easy, 10 medium, 11 hard). In these the whole sentence is the test frame: a long subject with interveners for R1, or an opening modifier plus blank for R3.
- 50 are two sentences. The usual order is: sentence 1 introduces a person or thing with a credential or a broad fact ("X is a paleoceanographer", "Earth is not a perfect sphere"); sentence 2 holds the blank and gives the specific detail (a finding, a habit, an achievement, an explanation).
- 9 have three to five sentences; the extra sentences are context. Context sentences can also plant the attractor for a pronoun item (2.3 names a woman researcher in the sentence after the blank to tempt `she`).
- The blank is in the last sentence in 86 of 92 items. Median words before the blank within its sentence: 7.5 easy, 15.5 medium, 13.5 hard.
- Punctuation is rich even though punctuation is not tested here: em dashes appear in 16 passages (mostly a pair around an interrupter), parentheses in 16, quotation marks in 13, colons in 9. These interrupters are exactly what separates subject from verb in harder R1 and R2 items.

### Names, dates, places

- 59 of 92 passages name a person (23 easy, 18 medium, 18 hard; one of them, 3.1, is a character in a drama). 36 use the article-free title construction "[nationality or identity] [profession] [Full Name]" (for example "Syrian American astronomer" + name, "Seneca and Abenaki archaeologist" + name). Subjects are deliberately diverse (Lebanese, Lakota, Moroccan, Maya, Tajik, Japanese American, African American figures).
- 33 passages contain a year or decade (14 / 8 / 11). Dates matter to the answer only in R4 items.
- Non-English names keep their diacritics (`Rocío`, `González-Torres`, `Lívia`, `Chraïbi`, `Shōnagon`, `Nuhād al-Ḥaddād`) and titles of works are italic in print (ignored in the transcript).

### Vocabulary

Mean word length rises slightly (5.23, 5.33, 5.42 letters) and so does the share of words with 10 or more letters (8.4%, 9.0%, 11.0%). Hard passages use more technical nouns (superlubricity, mycorrhizal, Herfindahl-Hirschman Index, kinematic variables), but the grammar never depends on knowing them.

## 4. The correct answer

- **Justification is purely structural.** The key is the only option that satisfies the rule: the only form of the right number (R1, 25 of 25), the only finite or only nonfinite form (R2, 17 of 18), the only tense matching the cue (R4), the only pronoun of the right number and kind (R5), the only correct apostrophe pattern (R6), the only clause whose subject is what the modifier describes (R3). Meaning matters only in R3 (who is doing the action) and R4 (when).
- **Wording.** The key is the plainest form available. It is the strictly shortest option in 37 items and tied for shortest in 9 more; it is the longest in only 3. In R3 the lengths are balanced (key mean 12.1 words, distractor mean 12.9), so length is not a reliable cue there.
- **Voice and possessives are not shortcuts.** In 4 of 16 R3 items the key is the passive or nominalised option (2.2 and 3.12 are passive, 2.19 and 3.26 start with a possessive or "the X of Y" noun phrase), because the opening modifier describes a thing, not an agent.

## 5. Distractor recipes

Counts are per distractor (3 per item, 276 in all).

| Family | Archetype | Count | Example (own words or short quote) |
|---|---|---|---|
| R1 | Wrong number, tense varied | 75 of 75 | singular subject, options `promote`, `are promoting`, `have promoted` |
| R4 | Wrong time frame: future | 6 | a dated past event offered as `will be` |
| R4 | Present or past progressive | 9 | `is being`, `are reaching`, `were getting` |
| R4 | Past perfect where the cue is present or future | 5 | `had measured` for a current tool |
| R4 | Simple past where present or past perfect is needed | 5 | `flew` for a yearly migration |
| R4 | Present simple or present perfect where another tense is needed | 10 | `has leveraged` for an 1860 decision |
| R4 | Conditional or exotic compound (would, would have, will have been -ing, had been -ing) | 4 | `will have been measuring` |
| R2 | Nonfinite where a finite verb is needed | 33 | `-ing` 11, `to` + base 10, `having` + past participle 9, rarer forms 3 |
| R2 | Finite where a nonfinite phrase is needed | 16 | `places`, `placed`, `place` after "the first" |
| R2 | Comma splice via pronoun + finite verb | 2 | `this will ensure`, `it ensures` after a complete clause and comma |
| R2 | Wrong nonfinite (participle or `and` + -ing instead of purpose infinitive) | 3 | 3.19 only |
| R5 | Wrong number pronoun | 21 | `it` for a plural antecedent, `their` for "the animal" |
| R5 | Right number, wrong kind (demonstrative, indefinite `one`, wrong person `we`, wrong referent `she`) | 6 | `this`/`that` where `it` refers back to "an object" |
| R5 | Contraction for possessive determiner | 6 | `it’s`, `they’re` |
| R6 | Needless apostrophe on a plain plural | 14 | `photo’s`, `story’s`, `variable’s` |
| R6 | Missing apostrophe on the possessor | 12 | `photographers early photos` |
| R6 | Wrong possessor number (`s’` vs `’s`) | 6 | `Moons’`, `novels’`, `screws’` |
| R6 | `it’s` for `its` | 2 | 1.2 |
| R3 | Wrong noun as subject (dangling) | 23 | the study, the place, a second person or the result becomes the subject |
| R3 | Nominalised subject | 9 | "the use of", "the transport of", "an estimated reduction in" |
| R3 | Expletive opener | 6 | "it was ... that/who", "there are/was" |
| R3 | Agent buried in a possessive | 5 | "the researchers’ theory is that", "Henry’s reign resumed" |
| R3 | Passive that leaves the wrong noun as subject | 3 | "nutrients can be transported through ..." |
| R3 | Subordinate clause placed first | 2 | "when a market is less concentrated, its score ..." |

Notes:
- 8 of 27 R6 distractors are wrong in both noun slots, so the R6 error counts above overlap (34 errors over 27 distractors). R1, R2, R4 distractors carry exactly one error relative to the rule tested.
- R3 distractors are grammatical sentences on their own; the only fault is what the opening modifier attaches to. The bank never adds a second error (no comma splices, no agreement slips) to an R3 distractor.
- Attractor nouns are planted for R1 and R5: a noun of the distractors' number sits between subject and blank (R1) or near the pronoun (R5). See section 6.

## 6. Difficulty

| Signal | easy | medium | hard |
|---|---|---|---|
| Rule mix | R1 10, R2 11, R4 10, R5 5, R6 4, R3 0 | R1 9, R5 4, R6 3, R3 4, R2 2, R4 2 | R3 12, R1 6, R2 5, R5 2, R6 2, R4 1 |
| Mean words per option | 1.6 | 3.1 | 7.0 |
| R1: words between subject head and blank (median) | 4 | 7 | 13.5 |
| R1: items with an opposite-number noun between subject and blank | 3 of 10 | 6 of 9 | 6 of 6 |
| R5: items with a competing antecedent or a pronoun before its antecedent | 0 of 5 | 4 of 4 | 2 of 2 |
| Passage-final blanks (full-sentence options) | 0 | 0 | 7 |
| Share of words with 10+ letters | 8.4% | 9.0% | 11.0% |
| Passage median words | 40.5 | 45.5 | 43.5 |

What concretely separates the tiers:
- **Easy.** In 7 of 10 R1 items the subject sits right before the blank or behind one short phrase with no number clash (1.38, 1.40); the two long easy interveners (1.7, 1.9) use lists of concrete nouns or a plain appositive. Tense items carry an explicit cue in the same sentence ("each year", "in a later chapter", "from 1440 to 1473"). R2 items are bare main-verb slots after a short subject (1.23, 1.31). Pronoun antecedents are the subject of the previous clause with no rival noun. R6 uses everyday nouns (photographer, Moon, people).
- **Medium.** Interveners carry an attractor: a plural inside an appositive (2.21), a dash interrupter full of plurals (2.20), a compound subject followed by "each with" (2.13), a "which" whose antecedent sits in the main clause (2.18). Pronoun items plant a rival noun (2.4: "rivers such as the Mississippi" tempts `it`) or put the pronoun before its antecedent (2.6). R3 appears with short, clear openers (2.2, 2.17).
- **Hard.** R1 subjects run up to 27 words (median 13.5) with stacked phrases, clauses and parentheses (3.2), a possessive inside the subject whose number differs from the head (3.23, 3.25), or "each one of" followed by a plural relative clause (3.6). R2 items hide the subject behind dash lists (3.13), split it across the blank (3.11), put an interrupter between relative pronoun and verb (3.8), or ask for a choice among three nonfinite forms (3.19). R6 adds plural possessives and individual possession (3.24, 3.28). R3 dominates, with longer clauses, passage-final blanks, and keys that are passive or nominalised.
- Length and topic do not drive difficulty; distance, attractors and the R3 share do.

## 7. Skill-specific inventory: grammar rules tested

### 7.1 Overview with counts per tier

| Rule | Sub-rule | easy | medium | hard | total |
|---|---|---|---|---|---|
| Subject-verb agreement | no intervener | 3 | 0 | 0 | 3 |
| | prepositional phrase | 3 | 3 | 0 | 6 |
| | appositive | 2 | 1 | 0 | 3 |
| | participial phrase (incl. one with a dash interrupter) | 2 | 2 | 0 | 4 |
| | compound subject with "and" | 0 | 1 | 0 | 1 |
| | relative pronoun "which" (antecedent in main clause) | 0 | 1 | 0 | 1 |
| | quantifier subject ("every", "each one of") | 0 | 1 | 1 | 2 |
| | long stacked interveners (clauses, parentheses) | 0 | 0 | 2 | 2 |
| | possessive inside subject, number differs from head | 0 | 0 | 2 | 2 |
| | plural head behind singular nouns | 0 | 0 | 1 | 1 |
| | collective noun as subject | 0 | 0 | 0 | 0 |
| Finite vs nonfinite | finite: missing main verb | 5 | 0 | 2 | 7 |
| | finite: second verb of compound predicate | 1 | 1 | 0 | 2 |
| | finite: verb of subordinate or relative clause | 1 | 0 | 1 | 2 |
| | nonfinite: to-infinitive of purpose | 2 | 0 | 1 | 3 |
| | nonfinite: to-infinitive after "the first" | 1 | 0 | 0 | 1 |
| | nonfinite: -ing participial phrase | 1 | 1 | 1 | 3 |
| Modifier placement | preposition + gerund opener | 0 | 2 | 4 | 6 |
| | past participial opener (incl. "Compared with that of") | 0 | 1 | 3 | 4 |
| | -ing participial opener | 0 | 0 | 3 | 3 |
| | noun-phrase appositive opener | 0 | 1 | 2 | 3 |
| Tense and aspect | simple present (habitual, general, parallel) | 5 | 0 | 0 | 5 |
| | simple past (dated) | 2 | 2 | 0 | 4 |
| | past perfect (earlier past, counterfactual "if") | 2 | 0 | 1 | 3 |
| | future | 1 | 0 | 0 | 1 |
| Pronoun-antecedent | personal pronoun, number | 5 | 3 | 0 | 8 |
| | possessive determiner its/their vs contractions | 0 | 1 | 2 | 3 |
| | pronoun case (I/me, who/whom) | 0 | 0 | 0 | 0 |
| Plural vs possessive | singular possessor + plural noun (incl. its + plural) | 2 | 2 | 0 | 4 |
| | singular possessive alone | 1 | 0 | 0 | 1 |
| | irregular plural possessive (people’s) | 1 | 0 | 0 | 1 |
| | plural noun + singular possessor | 0 | 1 | 0 | 1 |
| | plural noun + plural possessor | 0 | 0 | 1 | 1 |
| | individual possession of two nouns | 0 | 0 | 1 | 1 |

Not tested at all in this bank: collective nouns, "the number of / a number of", either/or and neither/nor subjects, indefinite pronouns as subjects (everyone, none), inverted subjects ("there is/are" before the subject), subjunctive, who/whom and other case contrasts, comparatives and logical comparison outside 3.26, and verb forms like lie/lay. Parallelism is never tested on its own but is the cue in 1.3, 1.11, 2.1 and 3.19.

### 7.2 Subject-verb agreement: how the options are built

Two option families. In both, the key is the only option with the right number.

**Be-family (11 items).** Forms drawn from `is / are / was / were / has been / have been` (plus `are being` once and negative contractions once). Typical: singular past key `was` with `are`, `have been`, `were`; singular present key `is` with `are`, `have been`, `were`.

**Lexical-verb family (13 items).** One verb in four forms: `V-s`, `V`, `are/is V-ing`, `have/has V-ed`. Typical: key `promotes` with `promote`, `are promoting`, `have promoted`; plural key `use` with `uses`, `is using`, `has used`.

**Variants.** 2.18 adds the predicate noun to the option and makes it agree too (`is a smaller, foam version` vs plural verb plus plural noun); 3.6 uses plural passives (`are focused`, `were focused`); 3.20 slips a bare -ing form into the wrong-number set; 2.21 carries a trailing comma on all four options because an interrupter follows.

| id | Key | Distractors | Subject head and intervener |
|---|---|---|---|
| 1.4 | was | are, have been, were | sg name + appositive |
| 1.6 | sweeps | sweep, are sweeping, were sweeping | `she`, none |
| 1.7 | were | was, is, has been | pl "Objects" + long "ranging from ... to ... to ..." phrase of singular nouns |
| 1.9 | promotes | promote, are promoting, have promoted | sg + appositive with plural noun |
| 1.18 | enable | has enabled, is enabling, enables | pl, none |
| 1.20 | remains | have remained, remain, are remaining | sg + participial phrase |
| 1.28 | were | is, was, has been | unfamiliar plural `ayllus`, none |
| 1.34 | use | is using, uses, has used | pl + "of" phrase with singular noun |
| 1.38 | was | are, have been, were | sg + "of Ohio" |
| 1.40 | is | are being, have been, are | sg + "of ... in ..." |
| 2.7 | evokes | are evoking, have evoked, evoke | sg "use" + "of “we”" |
| 2.11 | takes | are taking, have taken, take | sg "cycle" + "of lunar phases" |
| 2.13 | are | was, has been, is | compound X and Y + "each with ..." |
| 2.16 | is | are, have been, were | sg + participial phrase |
| 2.18 | is a smaller, foam version | were a smaller, foam version; are smaller, foam versions; were smaller, foam versions | relative `which`, antecedent in main clause |
| 2.20 | has entered | have entered, were entering, enter | sg + participial + dash interrupter with plurals |
| 2.21 | is, | are, / have been, / were, | sg + appositive with plurals |
| 2.22 | studies | are studying, have studied, study | sg name + "of [university] in Brazil" |
| 2.23 | was | have been, are, were | "Every last second of ... , which ..." |
| 3.2 | was | are, were, have been | sg, about 27 intervening words |
| 3.3 | aren’t | hasn’t been, wasn’t, isn’t | pl "talents" + singular nouns |
| 3.6 | focuses | focus, are focused, were focused | "each one of these plays, which include ..." |
| 3.20 | animates | have animated, animate, animating | sg "question" + two embedded "what" clauses |
| 3.23 | identifies | are identifying, identify, have identified | compound possessor + sg head "analysis" |
| 3.25 | fascinate | has fascinated, fascinates, is fascinating | sg possessor + pl head "musings" |

Key tense in R1: present 18, past 6, present perfect 1. Because all distractors fail on number, a student who ignores tense still gets every R1 item right.

### 7.3 Finite vs nonfinite: how the options are built

**Finite needed (11).** Canonical set: the four forms of one verb `{finite, -ing, having + past participle, to + base}`, used in 8 of 11 (1.14, 1.21, 1.23, 1.31, 1.35, 2.1, 3.8, 3.11). Variants replace one nonfinite slot: `to have + past participle` (1.11), `to be + -ing` (1.30), `by + -ing` (3.13). The finite key takes the tense the context demands (past in a compound predicate whose first verb is past, present for a general statement) and agrees with its subject.

**Nonfinite needed (7).** The key is the lone nonfinite form against three finite forms of the same verb in 6 of 7: `to` + base against `V-s / V-ed / V` (1.8), against `is V-ing / V-ed / V-s` (1.22), against `has V-ed / V-ed / V-s` (1.27); -ing against `V-ed / had V-ed / V` (2.9), against `V-ed / V-s / is V-ing` (3.9), and against two comma-splice options `this will V`, `it V-s` plus `V-s` (1.29). The odd one out is 3.19: `to forge` against `forging`, `forged`, `and forging`.

| id | Key | Distractors | Frame |
|---|---|---|---|
| 1.8 | to place | places, placed, place | "was the first ___" |
| 1.11 | suspended | to have suspended, suspending, to suspend | "applied ... and ___" |
| 1.14 | served | serving, having served, to serve | verb of a "how" clause |
| 1.21 | includes | having included, including, to include | main verb after appositive |
| 1.22 | to join | is joining, joined, joins | purpose after complete clause |
| 1.23 | explain | having explained, explaining, to explain | main verb |
| 1.27 | to study | has studied, studied, studies | purpose |
| 1.29 | ensuring | this will ensure, ensures, it ensures | result phrase after comma |
| 1.30 | includes | to be including, including, to include | main verb |
| 1.31 | serve | having served, to serve, serving | main verb |
| 1.35 | is | having been, to be, being | main verb (passive) |
| 2.1 | developed | developing, to develop, having developed | second verb, compound predicate split by a dash pair |
| 2.9 | earning | earned, had earned, earn | result phrase after comma |
| 3.8 | rain | to rain, raining, having rained | verb of a "that" clause split by an interrupter |
| 3.9 | looking | looked, looks, is looking | interrupter between subject and its verb |
| 3.11 | Union would finally acknowledge | Union to finally acknowledge; Union, having finally acknowledged; Union, finally acknowledging | blank splits the subject's name; main verb |
| 3.13 | have positioned | positioning, by positioning, having positioned | main verb after dash-enclosed list |
| 3.19 | to forge | forging, forged, and forging | purpose after a compound predicate |

Distractor form totals: -ing 12, to + base 10, having + past participle 9, past -ed 6, present -s 5, base 2, is + -ing 2, pronoun + finite 2, and one each of to have + participle, to be + -ing, has + participle, had + participle, by + -ing, and + -ing.

### 7.4 Tense and aspect: how the options are built

All four options are compatible with the subject's number. The three distractors are other tenses or aspects of the same verb, usually one future, one perfect and one progressive or simple form.

| id | Key | Distractors | Time cue |
|---|---|---|---|
| 1.1 | measures | had measured, would have measured, will have been measuring | present-day description |
| 1.3 | get | had gotten, got, were getting | parallel with present "pack up ... and ___" |
| 1.5 | will learn | had learned, had been learning, have learned | "in a later chapter" |
| 1.13 | was | is, will be, has been | "from 1440 to 1473" |
| 1.15 | had reached | reach, will reach, are reaching | "If ... and survived ..., could have reacted" |
| 1.17 | fly | flew, were flying, had flown | "Each year" + present "journey" |
| 1.24 | had invented | is inventing, will invent, invents | "fifteen years earlier" than an 1881 event |
| 1.25 | produce | are producing, produced, have produced | general function of future systems |
| 1.32 | was | is being, is, will be | "back in the 1860s" |
| 1.37 | survives | had survived, survived, would survive | habitual present ("is unable", "during periods of") |
| 2.8 | ascended | will ascend, ascends, is ascending | "By the time ___, ... had increased" |
| 2.12 | leveraged | has leveraged, is leveraging, will leverage | 1860 events reported in past |
| 3.10 | had already served | already served, was already serving, already serves | earlier than "when he joined ... 1947-48" |

Distractor totals by form: future 6, present progressive 6, present simple 6, simple past 5, past perfect 5, present perfect 4, past progressive 3, and one each of `would` + base, conditional perfect, future perfect progressive, past perfect progressive.

### 7.5 Pronouns: how the options are built

| id | Key | Distractors | Antecedent and trap |
|---|---|---|---|
| 1.12 | them | this, that, it | plural "these works" |
| 1.19 | it | this, that, these | "an object" |
| 1.26 | it was | one was, they were, both were | the temple (singular) |
| 1.33 | He | They all, Those, Both | the artist named twice |
| 1.39 | It | Those, They, Some | "Multitask learning" |
| 2.3 | it | she, they, those | "The human brain"; a woman researcher named in the next sentence |
| 2.4 | they accumulate | one accumulates, it accumulates, we accumulate | "rivers such as the Mississippi"; the singular river tempts `it` |
| 2.6 | their | it’s, they’re, its | "the poems", which comes after the pronoun |
| 2.15 | it | those, one, them | "the instrument"; plural "curves" right before |
| 3.4 | its | they’re, their, it’s | "The animal"; previous sentence used plural "platypuses ... them" |
| 3.22 | its | their, they’re, it’s | "the Tajik Republic", after the pronoun; plural "republics" right after the blank |

Build rule: for personal pronouns, the key plus wrong-number personal pronouns plus demonstratives and indefinites (`this/that/these/those`, `one`, `some`, `both`, `they all`), with a wrong person (`we`) or wrong referent (`she`) once each. For possessive determiners, a 2 x 2 grid of number (`its`/`their`) by spelling (possessive vs contraction).

### 7.6 Plural vs possessive nouns: how the options are built

Options are a grid of spellings for one or two noun slots. Three distractors are drawn from the wrong cells.

| id | Key | Distractors | Structure |
|---|---|---|---|
| 1.2 | its wings | its wings’, it’s wing’s, it’s wings’ | determiner (`its`/`it’s`) x noun (`wings`/`wings’`/`wing’s`) |
| 1.10 | Moon’s | Moons, Moons’, Moon | four spellings of one noun |
| 1.16 | photographer’s early photos | photographer’s early photo’s; photographers early photo’s; photographers early photos | full 2 x 2 |
| 1.36 | people’s stories | peoples story’s; peoples stories; people’s story’s | full 2 x 2, irregular plural |
| 2.5 | poems ... by the novel’s | poem’s ... novel’s; poem’s ... novels’; poems ... novels’ | full 2 x 2 across a 6-word phrase |
| 2.14 | screw’s threads. | screw’s thread’s.; screws’ threads.; screws threads’. | partial grid; options carry the sentence period |
| 2.24 | author’s political writings | authors political writings; author’s political writing’s; authors’ political writings’ | partial grid |
| 3.24 | variables that characterize objects’ | variable’s ... objects’; variables ... object’s; variables ... objects | two slots, key needs a plural possessive |
| 3.28 | rock’s and rap’s | rocks and raps; rocks and rap’s; rock and rap’s | individual vs joint possession |

### 7.7 Modifier placement: how the options are built

All four options restate the same facts with the same content words and differ in which noun phrase lands first after the comma. Lengths stay within a few words of each other.

| id | Opener type | Required subject | Key shape | Distractor archetypes |
|---|---|---|---|---|
| 2.2 | preposition + gerund ("Far from being ...") | the objects | passive with by-agent | wrong subject (people), nominalised, wrong subject (place) |
| 2.10 | noun-phrase appositive ("A pioneer in ...") | the scientist | name + verb + that-clause | wrong subject with comment clause, expletive "it was", wrong subject (analysis) |
| 2.17 | preposition + gerund ("since uncovering ...") | the researcher | name + "has argued that" | agent in possessive, wrong subject with interrupter, nominalised |
| 2.19 | past participle ("Named in 1999 as ...") | the achievement | possessive + nominalisation ("[name]’s 1935 synthesis of ...") | person as subject + semicolon, person + "which", passive with wrong subject |
| 3.1 | past participle ("Based on events ...") | the drama | title + "tells the story of" | wrong subject x2 (the character), expletive "there was" |
| 3.5 | -ing participle | the crusts | active clause + "according to a recent study" | nominalised x2, wrong subject (the study) |
| 3.7 | noun-phrase appositive | the novel | possessive + noun + participial phrase | wrong subject x3 (country, author, author after misplaced participle) |
| 3.12 | noun-phrase appositive | the state | passive ("is reached when ...") | "when" clause first, wrong subject (surfaces), gerund subject |
| 3.14 | -ing participle ("Knowing that ...") | the researchers | "the researchers theorize that ..." | agent in possessive, wrong subject x2 (the moths) |
| 3.15 | preposition + gerund ("Upon recovering ...") | the king | name + "resumed his reign," | nominalised, agent in possessive, expletive "it was ... who" |
| 3.16 | preposition + gerund ("Despite being cheap ...") | the material | noun + "have two associated problems:" | expletive "there are", wrong subject (problems), agent in possessive |
| 3.17 | preposition + gerund ("In assessing ...") | the critics | "many critics have focused ... but" | wrong subject (the director's use), expletive "there are", nominalised |
| 3.18 | preposition + gerund ("By reducing ...") | the structures | active present perfect | nominalised + passive, agent in possessive, passive with wrong subject |
| 3.21 | -ing participle ("Forming extensive networks ...") | the trees and fungus | compound subject + "can transport" | expletive "it is ... that", nominalised, passive with wrong subject |
| 3.26 | past participle, comparison ("Compared with that of ...") | a score | "the HHI score of a less concentrated market" | wrong subject x2 (the market), "when" clause first |
| 3.27 | past participle ("Supported by analyses ...") | the findings | "findings from a 2022 study suggested that" | wrong subject x3 (foods with an interrupter, diets, components) |

Required subject is a thing in 11 items and a person or group in 5. Mid-sentence blanks: 2.2, 2.10, 2.17, 2.19, 3.1, 3.7, 3.15, 3.16, 3.17; passage-final: 3.5, 3.12, 3.14, 3.18, 3.21, 3.26, 3.27.

## 8. Generation blueprint

### 8.1 Shared shell

- Passage: one informational paragraph, 1 to 3 sentences, 25 to 65 words, one `______`, blank in the last sentence. Prefer a named person introduced with the article-free title construction, a year where the rule needs it, and an em dash pair or parenthesis as natural intervener material. Curly `’`, `“ ”`.
- Stem: the fixed sentence above, always.
- Options: exactly four, differing only along the tested rule; key position balanced across A to D (the official skew toward A and D should not be copied).
- Topic spread to aim for: about 40% science, then arts, social science, history, literature in roughly equal parts.

### 8.2 Per family

**R1 Subject-verb agreement (fully programmatic options; authored passage).**
- Slots: subject head noun and its number; intervener material (tier-controlled); verb lemma; time frame; continuation after the blank.
- Tier settings: easy, mostly 0 to 5 intervening words with no number clash (a longer list of concrete nouns is fine); medium, 2 to 13 words with one opposite-number noun (appositive, participial phrase, dash interrupter, "each with", relative "which"); hard, 10 to 27 words with stacked phrases or clauses, or a shorter subject containing a possessive whose number differs from the head, or "each one of / every" plus a plural relative clause.
- Answer logic: inflect the verb for the head's number in the frame's tense.
- Distractors: the other number in three tenses or aspects. Be-family: present, past, present perfect. Lexical family: present, present progressive, present perfect. Never offer a right-number distractor.
- Checks: dependency parse finds the head and its `Number`; the key is the only option of that number; at least one opposite-number noun lies between head and blank for medium and hard; reject collective nouns, "data/media", "number of", "none", percentages of collectives and anything where usage varies by dialect.
- Risks: wrong head detection in compound or possessive subjects; foreign plurals (an `ayllus`-type noun needs a context cue that it is plural).

**R2 Finite vs nonfinite (fully programmatic options; authored frame).**
- Slots: frame type (main verb missing, second verb of compound predicate, subordinate or relative clause verb, purpose phrase, "the first ___", result phrase after comma, interrupter between subject and verb), verb lemma, tense.
- Answer logic: finite frames take the agreeing finite form; nonfinite frames take `to` + base or -ing.
- Distractors: finite frames use `{-ing, having + participle, to + base}`, optionally swapping one for `to have + participle`, `to be + -ing` or `by + -ing`. Nonfinite frames use three finite forms (`V-s`, `V-ed`, `is V-ing` / `had V-ed`), or pronoun + finite comma splices after a comma.
- Checks: with the key, each independent clause has exactly one finite verb; with each distractor, the parse shows a missing finite verb, a fragment, or a splice; an `-ed` distractor must not form a grammatical reduced relative (the trap 3.19 exploits on purpose); hard tier needs 8 or more words between subject and blank or an interrupter.
- Risks: past participle and past tense being the same spelling; purpose vs result readings both sounding acceptable.

**R4 Tense and aspect (programmatic options; authored cue).**
- Slots: time cue type (dated past, earlier-than-past, "by the time", habitual, general present, future marker, counterfactual "if"), verb lemma, subject number (held constant).
- Answer logic: the tense the cue forces. Distractors: three of future, past perfect, simple past, present progressive, present perfect, conditional, chosen so none is defensible.
- Checks: the cue phrase is present in the same or previous sentence; an LLM or rule check rejects any distractor that reads as acceptable (present perfect next to a dated past, progressive next to a habitual cue).
- Risks: this is the family most prone to two defensible answers. Keep cues explicit; reserve past perfect for clearly ordered past events.

**R5 Pronouns (programmatic options; authored antecedent and attractor).**
- Slots: antecedent and its number, pronoun role (subject, object, possessive determiner), attractor noun of the other number (medium and hard), antecedent before or after the pronoun (after only in medium and hard).
- Answer logic: the pronoun matching the antecedent. Distractors: wrong-number personal pronoun, demonstratives or indefinites, contractions for possessive determiners.
- Checks: exactly one candidate antecedent of the key's number within the window; the attractor matches a distractor; avoid gendered pronouns unless the referent is a named person.

**R6 Plural vs possessive (fully programmatic).**
- Slots: possessor noun (regular, irregular plural, proper), possessed noun, number cue for each, optional second possessor for individual possession.
- Answer logic: apply apostrophe rules per slot. Distractors: three wrong cells of the grid, covering one needless apostrophe on a plain plural, one missing apostrophe, one wrong possessor number.
- Checks: every slot has a number cue in the passage ("a", "each", "the", a named single person); curly apostrophes only; no generic plural that could be read either way unless the cue is explicit.

**R3 Modifier placement (authored passage and canonical clause; transforms generated and verified).**
- Slots: opener type (preposition + gerund, -ing participle, past participle, noun-phrase appositive, "Compared with that of"), the logical subject, the main-clause fact, a secondary participant (a study, place, person or result) to supply wrong subjects, blank mid-sentence or passage-final.
- Answer logic: the clause whose first noun phrase is the logical subject; allow passive or nominal keys when the opener describes a thing acted upon.
- Distractor recipes: (W) promote the secondary participant to subject; (N) nominalise the verb; (P) put the logical subject in a possessive; (E) expletive "it is ... that" or "there are"; (V) passive that leaves the wrong noun as subject; (S) subordinate clause first. Use three different recipes per item.
- Checks: all four options share at least 70% of content words and are within 25% of each other in length; the first noun phrase head of the key equals the annotated subject and differs in every distractor; each option is otherwise grammatical; an LLM judge confirms exactly one option leaves no dangling modifier.
- Risks: a transform that accidentally keeps the right subject (for example a possessive that some judges accept), a distractor with a second unintended error, and options that drift in meaning. This family needs a human or model review pass.

### 8.3 Templates, volumes and build order

Recommended templates: R1 4 (be-family, lexical family, quantifier or compound subject, relative-pronoun or possessive-inside-subject), R2 4 (finite main verb, finite second or subordinate verb, purpose infinitive, -ing phrase), R4 3 (present habitual or general, simple past dated, past perfect or future), R5 2 (personal pronoun, possessive determiner), R6 2 (two-slot grid, individual possession), R3 4 (one per opener type, sharing the six-recipe distractor engine). Total 19.

Recommended first pool: twice the official bank, with the same rule mix per tier.

| Tier | R1 | R2 | R3 | R4 | R5 | R6 | Total |
|---|---|---|---|---|---|---|---|
| easy | 20 | 22 | 0 | 20 | 10 | 8 | 80 |
| medium | 18 | 4 | 8 | 4 | 8 | 6 | 48 |
| hard | 12 | 10 | 24 | 2 | 4 | 4 | 56 |

Build order: R1 and R2 first (43 of 92 official items, options fully programmatic, easy and medium coverage), then R4 (mostly easy, but needs the acceptability check), then R6 and R5 (small, programmatic), then R3. R3 is the hardest to author but it is 43% of the hard tier, so a credible hard tier cannot ship without it.
