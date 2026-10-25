# Words in Context (Craft and Structure): bank analysis

Source: 111 official items (58 easy, 28 medium, 25 hard) in `material/rw/transcripts/words_in_context.json`, read in full after 61 items were checked against their images. Counts come from Python over the transcript. Subject, clue type and distractor archetype are hand annotations made while reading every item; they are judgement calls, but each one is listed per item in section 7 so it can be audited.

Frequency data: `tools/data/freq.txt` (74,989 word forms, rank = line number). It is built from about 450 Project Gutenberg books by authors active 1850 to 1928 plus NSF, NASA, NOAA and CRS texts, so it is a literary, old-fashioned corpus. Modern academic words are undercounted or missing: creativity, motivation, predictable, repetitive, newfound, melodic, optimize, marginalize and categorize are absent, and "computer" ranks about 29,800. Ranks are reliable for comparing the four options of one item and for comparing tiers, not as an absolute measure of how hard a word is for a 2026 student. For a multiword option the rank is that of its rarest content word (articles, prepositions and the repeated "his mother" ignored); inflected forms are looked up as printed, then with -s, -ed or -ing stripped.

Item 3.18 is a screenshot in a different layout (serif font, boxed options) and its cb_id `abcd0009` is a placeholder, not a real question ID.

## 1. Snapshot

| Tier | Items | Blank completion | "Most nearly mean" | A | B | C | D |
|---|---|---|---|---|---|---|---|
| Easy | 58 | 43 | 15 | 16 | 18 | 11 | 13 |
| Medium | 28 | 23 | 5 | 9 | 6 | 4 | 9 |
| Hard | 25 | 22 | 3 | 1 | 9 | 12 | 3 |
| All | 111 | 88 | 23 | 26 | 33 | 27 | 25 |

The letter spread is even overall; hard is lopsided (one A in 25, twelve Cs). That is an accident of this sample, not something to copy.

Passage length in words (blank not counted; for "most nearly mean" items the intro line and any copyright line are included, the excerpt alone is in brackets):

| Tier | All items min / median / max | Blank items | Meaning items (excerpt only) |
|---|---|---|---|
| Easy | 31 / 51.5 / 95 | 31 / 50 / 60 | 40 / 67 / 95 (25 / 49 / 68) |
| Medium | 35 / 49 / 78 | 35 / 48 / 66 | 60 / 72 / 78 (30 / 51 / 59) |
| Hard | 43 / 54 / 96 | 43 / 53.5 / 76 | 49 / 78 / 96 (37 / 63 / 63) |

Length barely moves with tier. Blank passages are one to four sentences, and two is the norm (56 of 88): easy 7 one-sentence, 27 two, 8 three, 1 four; medium 6 / 14 / 3; hard 5 / 15 / 1 / 1.

Stem wording, four variants:

| Stem | Count | Tiers |
|---|---|---|
| Which choice completes the text with the most logical and precise word or phrase? | 87 | 42 E, 23 M, 22 H |
| Which choice completes the text with the most logical and precise word? | 1 | 1.34 (E) |
| As used in the text, what does the word “X” most nearly mean? | 21 | 15 E, 3 M, 3 H |
| As used in the text, what does the phrase “X” most nearly mean? | 2 | 2.1 “a singular”, 2.8 “reconcile his mother to” (both M) |

The "word or phrase" stem is used even when every option is a single word.

## 2. Subtypes

### 2a. Blank completion (88 items: 43 E, 23 M, 22 H)

Definition: an informational paragraph has one `______`; the student picks the word or phrase that makes the paragraph say what its other sentences establish.

What the student must do: find the clue unit (a later clause, the next sentence, or a contrast with an earlier sentence), state in their own words what the blank must mean, and pick the option whose dictionary meaning matches, rejecting options that fit the grammar but assert something unsupported or the reverse.

Wording: "Which choice completes the text with the most logical and precise word or phrase?" (87) or "...precise word?" (1).

Option form (all four options always share part of speech and frame):

| Key form | Easy | Medium | Hard | Examples |
|---|---|---|---|---|
| verb | 20 | 10 | 6 | spans, preserving, embraced, transcending, negating |
| adjective | 11 | 6 | 8 | vivid, abrupt, accessible, dogmatic, homogeneous |
| noun | 4 | 1 | 2 | patterns, complexity, consensus, anomaly, supposition |
| adjective + preposition | 4 | 1 | 2 | inexperienced with, distant from, receptive to, independent of |
| noun + preposition | 2 | 2 | 2 | indicator of, reputation for, ambivalence toward, exposure to |
| verb + preposition | 1 | 2 | 1 | depended on, speculate about, conform to, mediated by |
| article + adjective or noun | 1 | 1 | 1 | a suitable / an arbitrary; a collaboration / an analogy; a discernible / a straightforward |

20 of 88 blank items use phrase options (17 with all four options multiword, 3 mixed such as "question / react to / perceive / conform to"). When an article is part of the option, each option carries its own a/an.

The blank items split by the kind of clue that pins the key (primary clue, section 7 gives full counts): restatement 40, cause or consequence 19, contrast 14, example 12, collocation only 2, tone 1. These are not separate stems but they are separate writing recipes, so section 8 treats them as templates.

### 2b. "As used in the text, what does the word/phrase X most nearly mean?" (23 items: 15 E, 5 M, 3 H)

Definition: a literary excerpt has one word or phrase underlined (`<u>...</u>` in the transcript); the stem quotes it; the student picks the option that means what the word means in this sentence.

What the student must do: ignore the word's everyday sense, read its immediate frame (its object, complement or the noun it modifies), and choose the synonym that fits that frame. Example: "drew" with "the shades far down" means pulled, not sketched.

Every one of these 23 items is a literary excerpt and none of the 88 blank items is, so subtype and genre coincide exactly in this bank.

Option form: options are capitalized (all 23; blank options are always lowercase), and they copy the target's inflection (drew: Pulled, Drained, Inspired, Sketched; reaching: Arriving at, Consulting with, Running to, Clinging to). Target POS: verb 12, adjective 6, verb phrase 2, verb + preposition 1, article + adjective 1, noun 1. Four items have phrase options: 1.30 (verb + preposition), 2.1 ("A lonely / An extraordinary"), 2.8 (all four start "Get his mother to ..."), 2.26 (four definitions such as "Take into account and follow"); 1.56 mixes "Held up" with single words.

## 3. Passages

Subjects (hand classified; archaeology, anthropology, economics, psychology and linguistics count as social science; arts, art and literary criticism and philosophy as humanities; dated events and figures as history; excerpts from fiction, poetry, drama and memoir as literature):

| Subject | Easy | Medium | Hard | All |
|---|---|---|---|---|
| Humanities and arts | 18 | 5 | 6 | 29 |
| Natural science | 13 | 9 | 6 | 28 |
| Literature (excerpt) | 15 | 5 | 3 | 23 |
| Social science | 6 | 6 | 10 | 22 |
| History | 6 | 3 | 0 | 9 |

Hard leans to social science (economics of donations, residential mobility, cassette prices, corpus linguistics, income inequality research).

Genres: 88 informational paragraphs (all blank items) and 23 literary excerpts (all meaning items): 13 novels, 6 short stories, 2 poems, 1 play, 1 autobiography. No tables, graphs, research notes or paired texts appear in this skill.

Literary excerpt conventions:
- Intro line: "The following text is from [Author]’s [year] [genre] [Title]." 13 of 23 say "adapted from". 16 add a context sentence naming the speaker or situation ("Alice, a child, is talking to her cat."). One reverses the order ("from the 1989 novel The Ancient Child by Kiowa writer N. Scott Momaday").
- 17 of 23 sources are from 1837 to 1928 (Hawthorne twice, Stoker, Carroll, Chesnutt, Eliot, Wilde, Larsen, McKay, Fitzgerald, Hurston, Sinclair, Tarkington, Sui Sin Far, Matheus, Martí in translation, Seacole); 6 are from 1989 to 2021 and carry a "©year by Author" line.
- 7 use bracketed editorial insertions to resolve pronouns or fix grammar ("[Jay Gatsby]", "[the rose]", "[A]").
- The excerpt is one short paragraph (25 to 68 words). The target sits in the middle of a sentence whose other words decide its sense. Poems keep line breaks (1.19) or are run in with wide gaps (1.45); the play excerpt gives each speaker line with the name in capitals (3.15).

Blank passage build, sentence by sentence:
- Claim with blank first, support after: the blank is in sentence 1 in 41 of 88 items (E 19, M 8, H 14). Typical: "[Role] [Name] [did/argues] ... ______ ...", then a sentence or post-colon clause that restates, explains or exemplifies. In 20 of 88 the clue follows a colon, semicolon or dash in the same sentence (E 11, M 3, H 6).
- Context first, summarising blank last: the blank is in the final sentence in 62 of 88 (includes the 18 one-sentence passages). Typical: a fact, then "These unique ______ allow...", "It was ______ for a business to be featured, since...".
- Received view, then finding: "Some scientists have suggested that ... ______ ..., but [researcher]'s research suggests ..." or "challenging the accepted view that ... ______. ... in fact ...". About 8 items, mostly hard (1.27, 1.31, 2.17, 3.8, 3.10, 3.12, 3.14, 3.25).
- Negation sits in the blank's sentence in 7 of 43 easy, 11 of 23 medium and 8 of 22 hard blank items (not, no, little, less, unlikely, without, cannot, declines to, avoiding, by no means). Medium uses it most.

Names, dates, places: 59 of 88 blank passages put a role noun before a full name ("Economist Jingting Fan", "Archaeologist Erika Karuzas", "Dance choreographer Jawole Willa Jo Zollar"); 14 add "and colleagues", "et al." or "team"; 29 give a year. About 15 center an Indigenous, Black, Latinx, Korean American or other community or artist (Osage, Quechua, Lenape, Kumeyaay, Taíno, Crow Tribe, Salish and Kootenai). Technical terms get a parenthetical gloss: "pessoi (glass game pieces)", "aerialist (mid-air acrobat)", "polyploidy (whole genome duplication)". Species names are given in full (Posidonia australis, Acropora palmata, Tmesipteris oblanceolata). Titles of works are italic in print (italics are dropped in the transcript).

Vocabulary level: share of lowercase passage tokens rarer than rank 10,000 (median per item) is 12.8% easy, 14.3% medium, 18.0% hard. Easy passages read like a museum label or science news brief; hard ones read like an abstract ("nuisance costs", "residential location choices are not fully reducible to economic factors", "compositional specification").

## 4. The correct answer

How it is justified:
- Blank items: the key is the word whose plain meaning equals a paraphrase elsewhere in the passage (restatement), or the only word that makes a stated logical link true (cause, contrast), or the word that the examples instantiate. The key never repeats a passage word: in 88 blank items only one key shares a stem with the passage (1.7 "complexity" with "complicated"), and no distractor does. The test is always paraphrase to meaning, never word matching.
- Meaning items: the key is a plain, usually more common synonym of the target's contextual sense (easy keys median rank 3,304 against 6,316 for their distractors): Pulled, Priced, Gathers, Held up, Choose, Gentle. In hard meaning items the key itself is less common (Tolerate, Dictate, Developed).

How it is worded:
- Same part of speech, inflection and frame as the distractors; lowercase in blank items, capitalized in meaning items.
- Length is not a cue: mean option length is 8.9 characters for keys against 9.4 for distractors (easy), 11.6 against 10.8 (medium), 10.4 against 10.4 (hard); the key is the longest option in 33 of 111 items (30%, close to chance).
- Frequency is not a cue: the key is the rarest of the four in 25 of 111 items (23%) and the most common in 21 (19%), both near the 25% chance rate (details in section 7).
- Polarity of the key is often negative where the frame is negated: "by no means unimportant" (3.13), "how little consensus" (2.11), "lacked a straightforward explanation" (3.12), "not a very diverse group" (3.14).

## 5. Distractor recipes

Every distractor (333) was tagged with one archetype. Counts:

| Archetype | Blank E | Blank M | Blank H | Blank all (264) | Meaning all (69) |
|---|---|---|---|---|---|
| Plausible but unsupported (UNSUP) | 79 | 40 | 32 | 151 (57%) | 18 (26%) |
| Reversal / antonym of the key (ANT) | 34 | 16 | 16 | 66 (25%) | 4 (6%) |
| Right field, wrong nuance, degree or agent (CONNOT) | 7 | 9 | 14 | 30 (11%) | 7 (10%) |
| Topic echo (ASSOC) | 9 | 2 | 4 | 15 (6%) | 1 (1%) |
| Half the clue (HALF) | 0 | 2 | 0 | 2 (1%) | 0 |
| Another sense of the target word (SENSE) | n/a | n/a | n/a | n/a | 39 (57%) |

1. Plausible but unsupported. Same part of speech and register as the key, grammatical in the slot, but the passage never says or implies it. It is the backbone of the bank. Examples: 1.2 "nervous about her creative process" (nothing suggests nervousness); 2.10 "unlikely to be redundant" (unrelated to sampling scale); 3.9 "compliance with incorrect renditions". In hard items these are sophisticated words (subsumed in, inviolable, presuppose, transposed with) so that sounding academic is no help.

2. Reversal (antonym of the key or opposite polarity). Inserted, it makes the passage say the opposite of its clue. 56 of 111 items have at least one, 14 have two, none has three. Sub-recipes:
   - plain antonym: 1.44 "reduce their preservation efforts" when the trail adds protections; 2.24 "feasible";
   - the trait of the wrong party: 3.1 "unpretentious" describes Johnson, but the blank describes the editors he diverged from; 3.10 "commonplace" is the finding, but the blank is the view being challenged;
   - direction reversal: 1.22 "inherited" (Sumer passed concepts on); 2.18 "beneficiary of" (Sumner advocated); 3.5 "precursors of"; 3.23 "antecedent to";
   - negation flip: in "by no means ______" (3.13) the natural positive words "substantial" and "appropriate" become reversals.

3. Wrong nuance, degree or agent (near miss). Right semantic field and direction, wrong precision. It grows with tier (5%, 13%, 21% of blank distractors). Examples: 1.44 "inspire" against "promote" (a trail does not inspire efforts); 1.31 "reveal" against "justify" (the dates support skepticism rather than uncover it); 2.21 "dispute" and "withdraw" (only a person can dispute or withdraw a projection, not supply delays); 2.27 "yield" (fossils yield data, researchers do not); 3.17 "irrelevant to" (too strong for "almost no effect" and the wrong relation); 3.21 "protracted" and "curtailed" (sound biological, describe length not ranking).

4. Topic echo. A word that belongs to the passage's scene but cannot do the blank's job: 1.5 "counting" thousands of photographs; 1.9 "produces" for a plant; 2.7 "catalog" for archaeologists; 3.19 three market words (exploiting, monetizing, appraising) for a demand effect.

5. Half the clue. 2.15 has a two-sided clue (honors nature, dislikes wilderness); "responsiveness to" matches only the first half and "renunciation of" only the second, while the key "ambivalence toward" covers both.

6. Another sense of the target (meaning items only). The distractor is a correct synonym of the underlined word in some other context. 57% of meaning distractors; 6 of 23 meaning items use it for all three distractors (1.19 drew: Drained, Inspired, Sketched; 3.11 determine: Conclude, Evaluate, Select; 2.8 reconcile: apologize for, match, reunite with). Note the pair 1.41 and 3.11: both underline "determine"; the easy one keys "Choose", the hard one keys "Dictate" and offers "Select" (the easy key's sense) as a trap.

Relations among the options (asked for explicitly):
- Antonyms of the key: 66 of 264 blank distractors and 4 of 69 meaning distractors (section 7 marks each one ANT).
- Distractors that are synonyms of each other: rare, 8 of 111 items (1.3 prepared for / skilled in; 1.24 creative / bold; 1.26 avoided / disregarded; 1.18 opposed / disregarded; 3.6 entrenching / substantiating; 3.19 exploiting / monetizing; 2.12 underestimate / misconstrue; 2.5 exposed / discovered). In 5 of the 8 both members are reversals, so the pair is wrong for the same reason. Two distractors that are antonyms of each other occur once (3.21 protracted / curtailed).
- Plausible-sounding, wrong connotation: the CONNOT group (37 in all), concentrated in medium and hard.
- No form lookalikes: no distractor is chosen for looking or sounding like the key (no affect/effect style pairs anywhere in the 333).

## 6. Difficulty

| Signal | Easy | Medium | Hard |
|---|---|---|---|
| Share of "most nearly mean" items | 15/58 (26%) | 5/28 (18%) | 3/25 (12%) |
| Median passage length, words | 51.5 | 49 | 54 |
| Rare-token share in passage (median) | 12.8% | 14.3% | 18.0% |
| Key median frequency rank | 9,191 | 19,012 | 20,773 |
| Keys rarer than rank 10,000 (incl. absent) | 27/58 (47%) | 20/28 (71%) | 21/25 (84%) |
| Distractors rarer than rank 10,000 | 76/174 (44%) | 52/84 (62%) | 52/75 (69%) |
| Items with phrase options | 10/58 | 9/28 | 6/25 |
| Contrast clue present (blank items) | 6/43 (14%) | 9/23 (39%) | 7/22 (32%) |
| Negator in the blank's sentence (blank items) | 7/43 | 11/23 | 8/22 |
| Items needing an extra inference step | 1 | 2 | 7 |
| Blank distractors: UNSUP / ANT / CONNOT+HALF / ASSOC | 61 / 26 / 5 / 7 % | 58 / 23 / 16 / 3 % | 48 / 24 / 21 / 6 % |
| Meaning distractors that are other senses | 21/45 (47%) | 12/15 (80%) | 6/9 (67%) |

What concretely separates the tiers:
- Easy: everyday or mid-frequency keys (vivid, protect, patterns, available), a near-verbatim clue in the next clause ("the same pleasant musical quality" for melodic, "capabilities that were previously unavailable" for newfound), distractors that are obviously unrelated or plainly opposite. Meaning items use a common word in a concrete physical sense (drew the shades, supported by pillars, marked at twelve dollars).
- Medium: keys move to rank 10,000 to 40,000 (nullify, impede, concede, intangible, consensus); the clue is more often a contrast or a negated frame ("unlikely to be ______", "how little ______ there is", "declines to ______"); one distractor is usually a near miss in the right field. Meaning items use abstract senses (assumed greater precision, a singular change, consider = take into account and follow).
- Hard: Latinate academic keys (dogmatic, homogeneous, superseded, engendering, mediated by, undifferentiated); the reader must translate a technical paraphrase ("low species richness" means homogeneous, "costs, though variable, ... so charities will favor a few large donors" means independent of size) or do one logical step: negation (3.13 by no means unimportant), implication (3.6 a student under Vermeer's tutelage undercuts "solitary artist"), ranking (3.21 largest known genome, unlikely to be superseded), or reading a contrast that is only implicit (3.1). Distractors are all equally academic, so register gives nothing away, and one in five is a near miss.
- Not a difficulty signal: passage length, option length, and whether the key is rarer than its distractors within an item (key order among the four by frequency averages 2.52, 2.64 and 2.84 where 2.5 is chance, a slight drift only).

## 7. Skill-specific inventory

### 7a. Clue types that pin the key

Definitions used: restatement (another clause says what the blank means, often after a colon, a semicolon, "In this view", "Instead of", a definition or a parallel list); cause (because, since, so, thus, given that, due to, "which makes", "so ... that", "to ... so that"); contrast (but, however, unlike, while, despite, "challenging the accepted view ... in fact", "not ... but also"); example (for example, for instance, such as, including, "These characteristic works include", a list that instantiates the blank); tone (the passage's evaluation fixes the polarity, as in "It would be a mistake to ______ ... is essential viewing"); collocation (the blank's own object or complement decides it, as in "it ______ approximately 200 square kilometers").

| Clue (primary) | Blank E | Blank M | Blank H | Blank all | Meaning |
|---|---|---|---|---|---|
| Restatement / definition | 22 | 9 | 9 | 40 | 1 |
| Cause / consequence | 8 | 6 | 5 | 19 | 0 |
| Contrast | 3 | 5 | 6 | 14 | 2 |
| Example | 8 | 2 | 2 | 12 | 0 |
| Collocation (local frame) | 1 | 1 | 0 | 2 | 20 |
| Tone | 1 | 0 | 0 | 1 | 0 |

Counting every clue present (many items combine two): blank items restatement 43, contrast 22, cause 20, example 16, collocation 2, tone 1; meaning items collocation 22, contrast 3, restatement 2, tone 1, cause 1. Tone is almost never the deciding clue; when an item is evaluative it still states the reason (1.37 "is essential viewing"). Meaning items are decided by the target's immediate frame, with a contrast in two (1.1 the driver "however, was not in the least disturbed" against the narrator's fear; 3.15 "endure with equanimity" against "almost unbearable").

### 7b. Frequency of keys against distractors

Bands of frequency rank (head word of each option):

| | ≤2k | 2k to 5k | 5k to 10k | 10k to 20k | >20k | absent |
|---|---|---|---|---|---|---|
| Easy keys (58) | 7 | 13 | 11 | 15 | 10 | 2 |
| Easy distractors (174) | 21 | 39 | 38 | 36 | 34 | 6 |
| Medium keys (28) | 3 | 3 | 2 | 8 | 9 | 3 |
| Medium distractors (84) | 5 | 16 | 11 | 19 | 28 | 5 |
| Hard keys (25) | 0 | 2 | 2 | 7 | 10 | 4 |
| Hard distractors (75) | 3 | 8 | 12 | 13 | 34 | 5 |

Median rank, key against distractors: easy 9,191 against 8,235 (blank 10,484 / 9,498; meaning 3,304 / 6,316); medium 19,012 against 15,455 (blank 20,598 / 17,387; meaning 1,741 / 4,562); hard 20,773 against 22,201 (blank 22,039 / 25,087; meaning 11,533 / 5,839). Within each tier the distractors are drawn from the same frequency band as the key, so a student cannot win by picking the hardest or the easiest word. The whole option set moves up the frequency scale with tier. Meaning items invert this: the key is a plain word and the distractors are sometimes rarer.

Targets of the 23 meaning items (rank of the printed form): disturbed 2,351; spread 1,357; beckoning 10,463; receiving 3,928; drew 444; reaching 2,783; marked 1,561; specific 6,407; featured 13,131; soft 693; determine 7,356 (twice); sheltering 12,777; conceivable 10,187; collects 32,273 (collect is common, the -s form is rare in old fiction); supported 3,789; singular 2,889; quality 2,223; reconcile 10,399; assumed 3,022; consider 1,312; contracted 7,310; endure 2,537. Median 3,789; 13 of 23 are in the top 5,000. The difficulty is polysemy, not rarity.

### 7c. Distractor relations

- Antonym or reversal of the key: 70 of 333 distractors; at least one in 52 of 88 blank items and 4 of 23 meaning items; never three in one item.
- Other senses of the target word (meaning items): 39 of 69.
- Synonym pairs among distractors: 8 items (listed in section 5), 5 of them pairs of reversals.
- Antonym pair among distractors: 1 item (3.21).
- Wrong connotation or near miss: 37; topic echo: 16; half clue: 2.
- Form lookalikes of the key: 0.

### 7d. Full option inventory

Columns: item, tier, frame (blank, or the quoted target), part of speech of the slot, the four options in printed order with the key in bold, each followed by its frequency rank (n/a = not in the list) and, for distractors, its archetype tag, then the clue type(s). Tags: UNSUP plausible but unsupported, ANT reversal or antonym, CONNOT wrong nuance, degree or agent, ASSOC topic echo, HALF half the clue, SENSE another sense of the target. POS labels: art = article, prep = preposition.

| Item | Tier | Frame | POS | Options | Clue |
|---|---|---|---|---|---|
| 1.1 | E | “disturbed” | adj | Disorganized (36,546, SENSE) ; **Alarmed** (3,304) ; Offended (3,475, CONNOT) ; Interrupted (1,362, SENSE) | contrast |
| 1.2 | E | blank | adj+prep | nervous about (1,698, UNSUP) ; completed by (3,596, CONNOT) ; delayed by (5,951, UNSUP) ; **involved in** (3,490) | example |
| 1.3 | E | blank | adj+prep | prepared for (1,182, ANT) ; **inexperienced with** (10,264) ; skilled in (8,702, ANT) ; excited about (1,684, ASSOC) | contrast/restate |
| 1.4 | E | “spread” | verb | Hidden (1,267, UNSUP) ; Discussed (3,684, SENSE) ; **Extended** (2,883) ; Coated (13,323, SENSE) | local |
| 1.5 | E | blank | verb | replacing (15,313, UNSUP) ; inventing (22,350, UNSUP) ; **preserving** (12,387) ; counting (4,865, ASSOC) | cause |
| 1.6 | E | blank | adj | **newfound** (n/a) ; delicate (1,159, UNSUP) ; inevitable (3,248, UNSUP) ; habitual (6,745, ANT) | restate |
| 1.7 | E | blank | noun | accuracy (9,207, UNSUP) ; inactivity (25,361, UNSUP) ; **complexity** (22,595) ; restraint (5,100, ANT) | example |
| 1.8 | E | “beckoning” | adj | Demanding (9,930, CONNOT) ; Signaling (38,650, SENSE) ; **Inviting** (7,045) ; Shifting (6,655, UNSUP) | restate/local |
| 1.9 | E | blank | verb | acknowledges (25,275, UNSUP) ; produces (14,826, ASSOC) ; **spans** (39,986) ; advances (7,941, UNSUP) | local |
| 1.10 | E | blank | noun | quantities (11,331, UNSUP) ; decorations (11,020, ASSOC) ; **patterns** (12,384) ; agreements (22,288, UNSUP) | restate |
| 1.11 | E | blank | adj | **vivid** (3,088) ; unknown (1,536, UNSUP) ; definite (3,392, UNSUP) ; reserved (4,101, ANT) | restate |
| 1.12 | E | blank | adj | scholarly (16,741, UNSUP) ; **melodic** (n/a) ; jarring (15,524, ANT) ; personal (1,149, UNSUP) | restate |
| 1.13 | E | blank | verb | borrow (2,132, UNSUP) ; postpone (12,469, UNSUP) ; **protect** (2,995) ; decorate (24,688, UNSUP) | restate |
| 1.14 | E | “receiving” | verb | Denying (8,833, ANT) ; Entering (2,624, UNSUP) ; Carrying (1,676, ASSOC) ; **Hearing** (1,449) | local/contrast |
| 1.15 | E | blank | noun | **dominance** (26,408) ; creativity (n/a, UNSUP) ; insignificance (13,465, ANT) ; neutrality (20,110, UNSUP) | restate |
| 1.16 | E | blank | verb | verifying (33,018, UNSUP) ; multiplying (23,987, ASSOC) ; comforting (7,538, UNSUP) ; **ensuring** (37,753) | cause/contrast |
| 1.17 | E | blank | noun+prep | uncertainty about (5,836, ANT) ; **indicator of** (36,670) ; motivation for (n/a, UNSUP) ; criticism of (4,287, UNSUP) | restate |
| 1.18 | E | blank | verb | **stimulated** (10,980) ; assigned (9,498, UNSUP) ; opposed (6,009, ANT) ; disregarded (14,408, ANT) | example |
| 1.19 | E | “drew” | verb | **Pulled** (1,416) ; Drained (10,962, SENSE) ; Inspired (3,563, SENSE) ; Sketched (12,127, SENSE) | local |
| 1.20 | E | blank | art+adj | **a suitable** (4,378) ; a determined (1,132, UNSUP) ; an arbitrary (19,184, ANT) ; an unpredictable (69,096, UNSUP) | cause |
| 1.21 | E | blank | noun | rebellion (5,449, UNSUP) ; **partnership** (9,652) ; discovery (2,121, UNSUP) ; disagreement (21,266, ANT) | restate |
| 1.22 | E | blank | verb | transformed (7,004, CONNOT) ; **introduced** (2,442) ; inherited (5,311, ANT) ; overlooked (7,646, UNSUP) | example |
| 1.23 | E | blank | adj | **foundational** (51,323) ; supplementary (27,567, ANT) ; repetitive (n/a, UNSUP) ; ineffective (25,364, ANT) | restate |
| 1.24 | E | blank | adj | creative (12,684, ANT) ; bold (2,149, ANT) ; **traditional** (12,818) ; understandable (38,088, UNSUP) | restate/contrast |
| 1.25 | E | blank | verb | borrows (36,446, ASSOC) ; **spans** (39,986) ; judges (7,147, UNSUP) ; neglects (30,618, ANT) | example |
| 1.26 | E | blank | verb | avoided (3,900, ANT) ; **featured** (13,131) ; appreciated (6,563, UNSUP) ; disregarded (14,408, ANT) | restate |
| 1.27 | E | blank | verb | pretending (6,196, UNSUP) ; complaining (10,989, UNSUP) ; requiring (12,911, UNSUP) ; **demonstrating** (31,567) | restate |
| 1.28 | E | blank | adj | secretive (24,019, UNSUP) ; **efficient** (13,162) ; outgoing (29,081, UNSUP) ; unsympathetic (15,046, UNSUP) | restate |
| 1.29 | E | blank | verb+prep | admired (2,811, UNSUP) ; disagreed with (21,898, ANT) ; warned (3,049, UNSUP) ; **depended on** (5,245) | restate |
| 1.30 | E | “reaching” | verb+prep | **Arriving at** (6,189) ; Consulting with (9,244, SENSE) ; Running to (966, CONNOT) ; Clinging to (3,603, SENSE) | local |
| 1.31 | E | blank | verb | anticipate (10,355, UNSUP) ; inspect (11,868, UNSUP) ; reveal (5,151, CONNOT) ; **justify** (6,555) | cause |
| 1.32 | E | “marked” | verb | Staged (74,019, UNSUP) ; **Priced** (30,311) ; Stained (3,526, SENSE) ; Watched (691, SENSE) | local |
| 1.33 | E | blank | verb | reviewed (14,004, UNSUP) ; **defied** (9,978) ; respected (5,295, ANT) ; prevented (3,932, UNSUP) | restate |
| 1.34 | E | blank | adj | **distinct** (3,390) ; required (2,039, UNSUP) ; unintended (38,726, UNSUP) ; unknown (1,536, UNSUP) | example |
| 1.35 | E | blank | verb | suspect (2,796, UNSUP) ; **preserve** (5,472) ; suggest (2,741, UNSUP) ; imagine (1,283, UNSUP) | cause |
| 1.36 | E | “specific” | adj | Imaginary (6,384, UNSUP) ; Energetic (8,097, UNSUP) ; Correct (3,394, SENSE) ; **Particular** (1,057) | local |
| 1.37 | E | blank | verb | complicate (30,464, UNSUP) ; amplify (46,600, ANT) ; **overlook** (12,015) ; assemble (16,179, ASSOC) | tone |
| 1.38 | E | “featured” | verb | **Displayed** (4,724) ; Questioned (3,028, UNSUP) ; Approved (6,316, UNSUP) ; Ignored (6,635, ANT) | local |
| 1.39 | E | blank | adj | genuine (2,754, CONNOT) ; intentional (21,299, UNSUP) ; independent (3,829, UNSUP) ; **original** (2,034) | restate |
| 1.40 | E | “soft” | adj | **Gentle** (1,009) ; Sensitive (3,071, SENSE) ; Shapeless (11,192, SENSE) ; Bland (11,253, SENSE) | local/tone |
| 1.41 | E | “determine” | verb | **Choose** (1,629) ; Influence (1,059, SENSE) ; Demonstrate (17,084, UNSUP) ; Measure (2,003, SENSE) | local/restate |
| 1.42 | E | blank | adj | **responsive** (10,484) ; inactive (21,413, ANT) ; liked (896, UNSUP) ; distressed (4,714, ANT) | restate |
| 1.43 | E | blank | adj+prep | full of (272, ANT) ; drawn to (919, UNSUP) ; responsible for (3,178, UNSUP) ; **distant from** (1,304) | restate |
| 1.44 | E | blank | verb | inspire (9,540, CONNOT) ; ignore (8,698, ANT) ; **promote** (11,911) ; reduce (6,846, ANT) | cause |
| 1.45 | E | “sheltering” | adj | **Protective** (19,772) ; Restrictive (55,845, CONNOT) ; Affectionate (3,649, CONNOT) ; Suspicious (3,985, UNSUP) | local |
| 1.46 | E | blank | verb | circumvents (31,153, ANT) ; eclipses (41,971, UNSUP) ; fabricates (n/a, UNSUP) ; **exemplifies** (46,966) | example |
| 1.47 | E | blank | verb | conceptualize (n/a, UNSUP) ; neglect (4,494, ANT) ; illustrate (15,077, UNSUP) ; **overcome** (3,241) | cause/contrast |
| 1.48 | E | blank | verb | **reflect** (5,527) ; receive (1,457, ASSOC) ; evaluate (29,553, UNSUP) ; mimic (19,528, CONNOT) | restate |
| 1.49 | E | blank | adj+prep | surpassed by (12,244, UNSUP) ; **comparable to** (16,254) ; independent of (3,829, ANT) ; obtained from (2,844, UNSUP) | cause |
| 1.50 | E | blank | adj | catastrophic (45,594, ASSOC) ; elusive (15,718, UNSUP) ; **abrupt** (5,886) ; imminent (8,052, CONNOT) | restate |
| 1.51 | E | blank | verb | selecting (12,083, UNSUP) ; **inspecting** (14,965) ; creating (11,172, UNSUP) ; deciding (11,382, UNSUP) | restate |
| 1.52 | E | blank | noun+prep | complaint about (5,990, ANT) ; **reputation for** (2,526) ; question about (382, UNSUP) ; requirement for (23,336, UNSUP) | example |
| 1.53 | E | blank | verb | startle (12,840, UNSUP) ; **recognize** (3,528) ; familiarize (53,065, UNSUP) ; convey (5,318, UNSUP) | restate/example |
| 1.54 | E | “conceivable” | adj | Obvious (3,272, UNSUP) ; **Imaginable** (11,232) ; Straightforward (8,541, ANT) ; Uninterrupted (18,683, UNSUP) | local |
| 1.55 | E | “collects” | verb | Increases (12,334, SENSE) ; Makes (767, UNSUP) ; Ignores (34,627, ANT) ; **Gathers** (17,406) | local |
| 1.56 | E | “supported” | verb | **Held up** (318) ; Encouraged (4,564, SENSE) ; Improved on (4,844, UNSUP) ; Defended (9,450, SENSE) | local |
| 1.57 | E | blank | adj | predictable (n/a, UNSUP) ; complicated (8,372, UNSUP) ; representative (6,558, UNSUP) ; **available** (5,511) | contrast |
| 1.58 | E | blank | verb | distrusted (17,148, ANT) ; **embraced** (8,730) ; released (3,941, UNSUP) ; overlooked (7,646, ANT) | contrast/example |
| 2.1 | M | “a singular” | art+adj | A lonely (1,419, SENSE) ; A disagreeable (2,964, CONNOT) ; An acceptable (11,952, UNSUP) ; **An extraordinary** (1,741) | local |
| 2.2 | M | blank | verb | epitomizing (n/a, UNSUP) ; **transcending** (39,341) ; anticipating (16,330, UNSUP) ; reinforcing (64,197, ANT) | example |
| 2.3 | M | “quality” | noun | Standard (4,104, SENSE) ; Prestige (14,512, SENSE) ; **Characteristic** (3,635) ; Accomplishment (9,880, CONNOT) | local |
| 2.4 | M | blank | art+noun | a collaboration (19,073, UNSUP) ; an accessory (26,584, UNSUP) ; a contradiction (10,675, ANT) ; **an analogy** (19,920) | restate |
| 2.5 | M | blank | verb | exposed (4,760, CONNOT) ; **asserted** (5,760) ; discovered (1,127, CONNOT) ; doubted (4,158, ANT) | restate |
| 2.6 | M | blank | adj | innovative (57,486, UNSUP) ; subversive (43,284, ANT) ; profound (2,644, ANT) ; **accessible** (15,210) | contrast |
| 2.7 | M | blank | verb+prep | **speculate about** (13,534) ; dismiss (8,996, UNSUP) ; expand on (12,854, UNSUP) ; catalog (n/a, ASSOC) | cause/contrast |
| 2.8 | M | “reconcile his mother to” | verb phrase | **Get his mother to accept** (1,369) ; Get his mother to apologize for (9,644, SENSE) ; Get his mother to match (2,091, SENSE) ; Get his mother to reunite with (52,029, SENSE) | local |
| 2.9 | M | blank | verb | recommend (7,985, UNSUP) ; criticize (25,739, CONNOT) ; **impede** (32,788) ; construct (17,387, ANT) | restate |
| 2.10 | M | blank | adj | neglected (3,792, UNSUP) ; redundant (44,163, UNSUP) ; ongoing (37,346, UNSUP) ; **uniform** (4,122) | cause/contrast |
| 2.11 | M | blank | noun | deliberation (7,902, ANT) ; vigilance (12,090, UNSUP) ; interest (494, UNSUP) ; **consensus** (32,279) | restate |
| 2.12 | M | blank | verb | **nullify** (46,118) ; denigrate (n/a, CONNOT) ; underestimate (44,363, UNSUP) ; misconstrue (42,211, UNSUP) | contrast |
| 2.13 | M | blank | adj | repeatable (n/a, UNSUP) ; explicable (41,153, UNSUP) ; regrettable (32,532, UNSUP) ; **intangible** (15,016) | restate/contrast |
| 2.14 | M | blank | adj | **recognizable** (27,767) ; intriguing (30,233, UNSUP) ; significant (4,656, CONNOT) ; useful (2,458, UNSUP) | contrast/cause |
| 2.15 | M | blank | noun+prep | responsiveness to (36,841, HALF) ; **ambivalence toward** (n/a) ; renunciation of (13,070, HALF) ; mastery over (8,507, UNSUP) | contrast |
| 2.16 | M | blank | verb | engulfs (66,364, UNSUP) ; encourages (24,122, UNSUP) ; **comprises** (51,056) ; provokes (39,225, UNSUP) | local/restate |
| 2.17 | M | blank | verb | waive (22,705, CONNOT) ; **concede** (19,494) ; refute (26,766, ANT) ; require (3,631, UNSUP) | cause |
| 2.18 | M | blank | noun+prep | **proponent of** (n/a) ; supplement to (18,500, UNSUP) ; beneficiary of (38,180, ANT) ; distraction for (10,904, UNSUP) | example |
| 2.19 | M | “assumed” | verb | **Acquired** (4,678) ; Acknowledged (4,562, SENSE) ; Imitated (15,293, SENSE) ; Speculated (17,735, SENSE) | local |
| 2.20 | M | blank | verb+prep | question (382, ANT) ; react to (36,826, UNSUP) ; perceive (3,266, UNSUP) ; **conform to** (18,529) | restate |
| 2.21 | M | blank | verb | dispute (5,979, CONNOT) ; withdraw (5,102, CONNOT) ; underscore (74,500, ANT) ; **invalidate** (40,492) | contrast |
| 2.22 | M | blank | verb | acquire (10,820, UNSUP) ; develop (5,791, ASSOC) ; attract (5,414, UNSUP) ; **confirm** (10,674) | cause |
| 2.23 | M | blank | verb | epitomize (n/a, UNSUP) ; **marginalize** (n/a) ; extol (41,154, ANT) ; substantiate (38,050, UNSUP) | restate |
| 2.24 | M | blank | adj | **insurmountable** (24,953) ; feasible (16,268, ANT) ; substantial (5,835, UNSUP) ; unnecessary (4,556, UNSUP) | cause |
| 2.25 | M | blank | adj | risky (15,616, ANT) ; misleading (17,174, UNSUP) ; **advantageous** (17,474) ; unremarkable (64,876, ANT) | cause |
| 2.26 | M | “consider” | verb phrase | **Take into account and follow** (853) ; Admire steadily and praise (3,231, SENSE) ; Come to a decision about (2,151, SENSE) ; Have an opinion on (944, SENSE) | local |
| 2.27 | M | blank | verb | exploit (17,324, UNSUP) ; **discern** (7,553) ; prioritize (47,469, UNSUP) ; yield (3,158, CONNOT) | restate |
| 2.28 | M | blank | adj+prep | **receptive to** (20,598) ; apprised of (24,260, UNSUP) ; incensed by (14,364, ANT) ; cited in (21,381, UNSUP) | restate/contrast |
| 3.1 | H | blank | adj | proficient (26,755, UNSUP) ; **dogmatic** (22,753) ; ambiguous (21,875, UNSUP) ; unpretentious (30,052, ANT) | contrast |
| 3.2 | H | blank | adj+prep | supplemental to (40,012, UNSUP) ; predictive of (35,209, ANT) ; **independent of** (3,829) ; subsumed in (n/a, UNSUP) | cause |
| 3.3 | H | “contracted” | verb | Restricted (15,615, SENSE) ; Described (2,318, UNSUP) ; **Developed** (3,358) ; Settled (1,151, SENSE) | local |
| 3.4 | H | blank | adj | overlooked (7,646, UNSUP) ; powerful (1,932, CONNOT) ; routine (6,712, ANT) ; **variable** (20,504) | restate |
| 3.5 | H | blank | noun+prep | refinements of (24,777, CONNOT) ; precursors of (55,742, ANT) ; **commonalities with** (n/a) ; animosities toward (40,143, UNSUP) | example |
| 3.6 | H | blank | verb | **negating** (n/a) ; prefiguring (n/a, UNSUP) ; entrenching (66,373, ANT) ; substantiating (38,050, ANT) | cause |
| 3.7 | H | blank | noun | hypothesis (15,178, CONNOT) ; affinity (17,131, UNSUP) ; **anomaly** (25,072) ; corroboration (27,640, ANT) | contrast |
| 3.8 | H | blank | adj | depleted (26,644, CONNOT) ; **homogeneous** (35,098) ; immature (22,201, UNSUP) ; dispersed (9,302, ANT) | restate |
| 3.9 | H | blank | noun+prep | compliance with (11,411, UNSUP) ; **exposure to** (8,007) ; criteria for (13,158, UNSUP) ; forfeiture of (41,183, UNSUP) | restate |
| 3.10 | H | blank | adj | inevitable (3,248, UNSUP) ; satisfactory (4,385, UNSUP) ; **negligible** (31,319) ; commonplace (3,925, ANT) | contrast |
| 3.11 | H | “determine” | verb | Conclude (9,881, SENSE) ; **Dictate** (13,205) ; Evaluate (29,553, SENSE) ; Select (5,839, SENSE) | local/cause |
| 3.12 | H | blank | art+adj | a discernible (16,348, CONNOT) ; **a straightforward** (8,541) ; an inconclusive (55,216, UNSUP) ; an unbiased (38,085, UNSUP) | cause/restate |
| 3.13 | H | blank | adj | substantial (5,835, ANT) ; satisfying (11,216, UNSUP) ; **unimportant** (10,438) ; appropriate (6,805, ANT) | restate |
| 3.14 | H | blank | adj | predatory (35,208, ASSOC) ; obscure (5,213, UNSUP) ; **diverse** (20,773) ; localized (51,643, CONNOT) | contrast/example |
| 3.15 | H | “endure” | verb | Regret (1,658, UNSUP) ; Persist (9,608, SENSE) ; **Tolerate** (11,533) ; Encourage (5,796, UNSUP) | contrast/local |
| 3.16 | H | blank | verb | interjected (16,277, UNSUP) ; committed (3,111, UNSUP) ; illustrated (3,916, CONNOT) ; **prescribed** (12,702) | restate |
| 3.17 | H | blank | adj+prep | consistent with (9,500, UNSUP) ; representative of (6,558, UNSUP) ; **overshadowed by** (15,138) ; irrelevant to (14,569, CONNOT) | restate |
| 3.18 | H | blank | adj | inviolable (30,929, UNSUP) ; innocuous (32,796, UNSUP) ; **undifferentiated** (n/a) ; ubiquitous (25,257, CONNOT) | example |
| 3.19 | H | blank | verb | exploiting (44,738, ASSOC) ; monetizing (n/a, ASSOC) ; appraising (33,518, ASSOC) ; **engendering** (33,645) | restate |
| 3.20 | H | blank | adj | authoritative (14,539, ANT) ; **opaque** (21,324) ; empirical (44,709, UNSUP) ; facile (16,788, ANT) | restate/contrast |
| 3.21 | H | blank | verb | protracted (18,293, CONNOT) ; **superseded** (23,185) ; curtailed (26,394, CONNOT) ; obviated (44,051, UNSUP) | cause |
| 3.22 | H | blank | noun | recognition (3,597, CONNOT) ; scheme (2,107, CONNOT) ; **supposition** (10,845) ; synopsis (35,808, UNSUP) | restate |
| 3.23 | H | blank | verb+prep | transposed with (44,345, UNSUP) ; **mediated by** (47,277) ; decoupled from (n/a, ANT) ; antecedent to (35,359, ANT) | contrast |
| 3.24 | H | blank | verb | adorn (15,836, UNSUP) ; **optimize** (n/a) ; endorse (24,916, CONNOT) ; counteract (22,744, UNSUP) | contrast/example |
| 3.25 | H | blank | verb | presuppose (64,079, UNSUP) ; categorize (n/a, UNSUP) ; **mitigate** (19,328) ; validate (46,503, ANT) | cause |

## 8. Generation blueprint

### 8a. What already exists in this repo

`server/words.py` already serves Words in Context items (`rw.wic.<frame>` templates) from `server/words/frames.json` (5,070 "complete" frames and 306 "nearly" frames, each with a `need` of class, polarity, intensity, POS and pattern, `keys`, and a `[[clue]]` span) and a 1,244-entry library `server/words/sat.json` (meaning, `same`, `opposite`, `lookalikes`, `everyday` and second senses, `freq_band`). Distractors are picked from the library by trap kind (`lookalike`, `too_strong`, `too_weak`, `connotation`, `reversed`, `topical`), in that priority order. Measured against this bank:

1. Passage length: frame texts have a median of 19 words ("complete") and 24 ("nearly"); official blank passages have a median of 50 and meaning excerpts 49 plus an intro line. The official clue usually sits in a second sentence or a post-colon clause, which a 19-word frame rarely has room for.
2. Distractor mix: the generator's first choices (lookalike, then intensity) are almost absent from the official bank (0 lookalikes, about 3 intensity traps in 333). The official majority is the plausible-but-unsupported word of the same register (57% of blank distractors), which in the generator only enters through the `topical` kind, ranked last. Reversals should be at most two per item; official items never use three.
3. Phrase options: 25 of 111 official items use phrase options (adjective, noun or verb plus preposition; a/an plus word; paraphrase definitions). Library entries are single words, so this whole format is missing.
4. The "nearly" format: rendering `rw.wic.f1-accept-01` with seed 0 gives a text that still contains `____`, a stem asking what “acknowledge” means, and choices dismiss / repudiate / reject / acknowledge with three `reversed` traps, so the stem word is itself an option. The official subtype underlines a common word inside a literary excerpt and never offers the word itself; it is worth checking whether the current "nearly" output is intended. Only 6 of the 22 distinct official targets have an entry in the library (marked, specific, reconcile, assume, contract, endure), and for some only the main sense, because official targets are everyday words (drew, soft, spread, determine).

The blueprint below is written so it can reuse the library (POS, polarity, `same`, `opposite`, second senses) and `freq.txt` rather than a new resource.

### 8b. Subtype B: blank completion

Slots:
1. Subject: humanities and arts, natural science, social science, history (bank ratio 29 : 28 : 22 : 9).
2. Actor: role noun + full name ("Marine biologist ..."), optional "and colleagues", optional year. Use invented researchers, or real facts that have been checked; an invented finding attached to a real person is misinformation.
3. Claim sentence with `______` in a slot of fixed POS and option frame (bare word, word + preposition, a/an + word).
4. Clue unit of one type: restatement, cause, contrast or example, placed after the blank (colon, semicolon, next sentence; 41 of 88 official blanks are in sentence 1) or before it (context sentence, blank last).
5. Optional negation overlay on the blank's sentence ("unlikely to", "by no means", "how little", "declines to", "avoiding"), used in about half of medium items.
6. Key: one word or phrase whose dictionary meaning is entailed by the clue; frequency band by tier (easy mostly ranks 2,000 to 20,000; medium and hard mostly above 10,000; use the library's `freq_band` or `freq.txt`, remembering that the old corpus overstates the rarity of modern academic words).
7. Three distractors, same POS, frame and frequency band as the key, mixed by tier: easy 2 unsupported + 1 reversal (or 3 unsupported), medium 1 to 2 unsupported + 1 reversal + 1 near miss, hard 1 unsupported + 1 reversal + 1 near miss (or 2 near misses). Topic echo as an occasional substitute for an unsupported word.

Answer logic: inserting the key makes every sentence consistent; inserting a reversal contradicts the clue; inserting an unsupported word makes a claim the passage gives no grounds for; a near miss is close but fails on agent, degree or the exact relation (justify vs reveal, invalidate vs dispute).

How each distractor is built:
- Reversal: the library's `opposite` of the key, or a word from the opposite class; for negated frames, the key's natural positive counterpart; for direction items, the converse relation (inherited for introduced, beneficiary for proponent).
- Unsupported: a same-POS, same-band word from an unrelated class that still collocates with the slot (it must read as grammatical English: "comforting the plants’ survival" is borderline).
- Near miss: same class, wrong intensity or a word whose usual subject differs from the passage's subject (a person disputes, a delay invalidates).
- Topic echo: a word from the passage's subject field (photographs, counting; archaeology, catalog).
- Half clue (for two-sided clues): one word for each side.

Programmatic: option frame and a/an agreement, lowercase options, POS and frequency-band matching, answer-letter balancing, blank formatting (`______` then punctuation with no space), candidate pools from the library by class/polarity/intensity, the checks below. Needs an author or language model: the passage and its clue unit, choosing unsupported distractors that are genuinely plausible-sounding, checking that no distractor is defensible in a looser reading, and fact safety.

Automatic checks:
- exactly one `______`; 30 to 80 words; 1 to 4 sentences; clue span present and marked;
- four distinct options, same POS and frame, a/an correct;
- neither the key nor any distractor (nor a word sharing its first five letters) appears in the passage; the official bank has one such overlap in 88;
- no distractor in the key's `same` list; at most two reversals; no two distractors in each other's `same` list unless both are reversals;
- frequency: key and distractors within one band of each other, key band within the tier target;
- blind solve by a model with no rationale: the key must win reliably; with the clue unit deleted, accuracy on the key should drop sharply (proves the clue does the work); each distractor substituted into the passage is judged false or unsupported;
- typography: curly quotes and apostrophes, en dash in number ranges.

Quality risks: two defensible answers (inspire vs promote type pairs need an explicit tie-breaker in the clue); a distractor that is right in a rarer sense; models drifting to rare showy keys at easy level; the clue word leaking into an option; reversals that are too obvious; passages that state the key outright; using absence from `freq.txt` as proof of difficulty (creativity and predictable are absent but easy).

### 8c. Subtype M: "most nearly mean"

Slots:
1. Excerpt: 25 to 70 words of public-domain literature (novel, story, poem, play, memoir). The bank's own sources are mostly 1837 to 1928; the repo already lists about 450 public-domain Gutenberg books from 1850 to 1928 in `tools/data/freq_sources.txt`, which can be mined for sentences without copying any official item. Avoid in-copyright modern excerpts.
2. Intro line: "The following text is (adapted) from [Author]’s [year] [genre] [Title]." plus an optional context sentence; bracketed insertions where a pronoun needs a referent.
3. Target: a common polysemous word (bank median rank 3,789) used in a sense other than its everyday one, marked `<u>...</u>`, quoted in the stem; "word" stem for one word, "phrase" stem for two or more.
4. Key: a plain synonym of the contextual sense, same inflection, capitalized.
5. Distractors: two or three synonyms of other senses of the target (drew: Sketched, Drained, Inspired), optionally one unsupported word or a reversal (Ignored for featured). For phrase targets, four paraphrases sharing a frame ("Get his mother to ...").

Programmatic: inflecting all options to the target's form, capitalization, underline and stem, intro line from metadata, scanning the corpus for sentences containing candidate targets. Needs an author or model: a sense inventory for everyday words (the library covers only 6 of the 22 distinct official targets), confirming that the excerpt fixes one sense, and choosing excerpts that read well alone.

Checks: target appears once and is underlined; the key is not a sense that also fits the sentence loosely (blind model must pick it reliably); every distractor is a true synonym of the target in some context (otherwise it is an unsupported word, which is fine but should be at most one); options share inflection; excerpt length and intro format.

Quality risks: an excerpt where two senses both work; old texts with archaic senses that are themselves obscure; offensive or dated content in 19th-century fiction; overly long excerpts.

### 8d. Templates, quantities, order

Recommended distinct templates: 8.
- B1 restatement (clue after a colon or in the next sentence), B2 cause or consequence, B3 contrast (including received view then finding), B4 example-pinned, B5 negated frame (an overlay on B1 to B4 for medium and hard), B6 phrase options (word + preposition, a/an + word), M1 underlined word, M2 underlined phrase with paraphrase options.

Recommended first bank: about 150 items, 60 easy, 45 medium, 45 hard (the official bank is easy heavy at 58/28/25, but practice needs more hard items), keeping the official subtype shares per tier: easy 45 blank + 15 meaning, medium 37 + 8, hard 40 + 5. Within blank items aim at the official clue mix: restatement about 45%, cause 20%, contrast 15% (rising to about 30% in medium and hard), example 15%; phrase options in about a fifth; negated frames in about half of medium items. Then scale toward three times the official counts per tier.

Build order: B1 and B2 first (two thirds of official blank items, and the clue can be checked mechanically against the key's library meaning), then B3 with the B5 negation overlay (this is what makes items hard), then M1 (needs a sense inventory and excerpt mining), then the B6 phrase-option format and M2.
