# Boundaries (Standard English Conventions): bank analysis

Source: 95 official items (`material/rw/transcripts/boundaries.json`, all 95 checked against the item images; punctuation, dash type and quote shape verified character by character). All numbers below were computed with Python over the corrected transcript plus a hand annotation of every item (rule tested, and an error tag for each of the 285 wrong options). Item ids are `tier.n` (1 = easy, 2 = medium, 3 = hard).

In this report option text is quoted in backticks exactly as printed; `L` and `R` stand for the words left and right of the boundary.

---

## 1. Snapshot

| | Easy | Medium | Hard | All |
|---|---|---|---|---|
| Items | 32 | 28 | 35 | 95 |
| Key A / B / C / D | 4 / 8 / 9 / 11 | 5 / 4 / 8 / 11 | 8 / 7 / 6 / 14 | 17 / 19 / 23 / 36 |
| Passage words (min / median / max, blank excluded) | 19 / 40 / 57 | 32 / 47.5 / 61 | 27 / 47 / 58 | 19 / 45 / 61 |
| Words in the sentence that holds the blank (median) | 26.5 | 34 | 39 | |
| Words before the blank inside that sentence (median) | 10 | 15.5 | 16 | |
| Sentences per passage with the key filled in (1 / 2 / 3 / 4) | 7 / 20 / 4 / 1 | 9 / 16 / 2 / 1 | 12 / 19 / 4 / 0 | 28 / 55 / 10 / 2 |

- Answer letters are skewed toward D (36 of 95, 38%); A is least common (18%).
- Stem: one wording only, 95 of 95: "Which choice completes the text so that it conforms to the conventions of Standard English?"
- The blank sits in the last sentence of the passage in 90 of 95 items. It is never the first token; it ends the passage in 2 items (1.18, 1.24, both question items).
- Options are short: mean 2.1 words (easy 2.1, medium 1.9, hard 2.4), maximum 8. In 91 of 95 items all four options begin with the same word (the last word before the boundary); the 4 exceptions are question items that vary word order.
- In 51 of 95 items (16 / 16 / 19) the four options contain exactly the same words and differ only in punctuation and capitalisation. In the other 44 a function word is added, dropped or moved (`and`, `but`, `which`, `that`, `it was`, `later`, `do`/`did`, word order in questions).

## 2. Subtypes

Every item uses the same stem, so subtypes are defined by the grammatical position of the blank. Six families cover the bank.

| Family | Easy | Medium | Hard | Total |
|---|---|---|---|---|
| S1 Joining two independent clauses | 6 | 11 | 17 | 34 |
| S2 Main clause plus a modifier or explanation (intro comma, trailing modifier, colon) | 6 | 7 | 6 | 19 |
| S3 Closing or opening a pair around a supplementary element | 1 | 6 | 3 | 10 |
| S4 Integrated elements: no punctuation allowed | 11 | 3 | 7 | 21 |
| S5 Items in a series | 3 | 1 | 2 | 6 |
| S6 Question versus statement | 5 | 0 | 0 | 5 |

**S1 Joining two independent clauses (34).** Both sides of the blank are complete clauses. The student must find a subject and finite verb on each side and pick the one legal joint offered: comma plus coordinating conjunction (11), period (13), semicolon (2), colon (1), or a semicolon/period placed on the correct side of a conjunctive adverb (7). The hard version hides the second clause's start behind a long introductory phrase (`By dissolving and reweaving the silk in a solution of ...,`), so the student has to see that this phrase belongs to the second sentence and that the boundary goes before it.

**S2 Main clause plus modifier or explanation (19).** One side is a complete clause, the other is not. Three tasks:
- comma after an introductory element before the subject (6: dependent clause with While / Because / Although, participial phrase, or an introductory appositive);
- comma before a trailing nonrestrictive modifier (7: `such as` phrase, sentence-final `which` clause, `-ing` participial phrase, absolute phrase, sentence appositive);
- colon after a complete clause before an explanation, list or single specified item (6).
The wrong options put a period or semicolon there, which leaves a fragment.

**S3 Pairs (10).** A supplementary element (appositive, `according to X`, interrupter, parenthetical) is already opened or closed somewhere in the passage; the blank supplies the partner. Comma pairs 5, dash pairs 4, parentheses 1. The student must look away from the blank (2 to 16 words) to find the partner mark and copy its type.

**S4 No punctuation (21).** The blank falls between two tightly bound parts: subject and verb (3), verb and complement (3), preposition and object (5), noun and its prepositional modifier (1), two halves of a compound joined by `and` (2), noun and restrictive `that` clause (2), title and name forming a restrictive appositive (5). The key adds no mark; the three wrong options each add a different one.

**S5 Series (6).** Simple list with commas (3, easy) or a complex list whose items contain commas, so semicolons separate items (3, medium/hard).

**S6 Question versus statement (5, easy only).** The option set crosses word order (inverted / statement) with end mark (`?` / `.`). Direct questions (`How ______`, `Where ______`) need inversion and `?`; embedded questions and relative clauses need statement order and a period.

## 3. Passages

**Genre.** 95 of 95 are a single informational paragraph. There are no literary excerpts, attribution lines, poems, paired texts, notes, tables or figures. Literature appears only as a topic (a critic's claim about a novel, a play's subject).

**Subject areas** (hand-tagged):

| Subject | Easy | Medium | Hard | Total |
|---|---|---|---|---|
| Natural science and technology | 11 | 10 | 12 | 33 |
| History and archaeology | 7 | 6 | 5 | 18 |
| Arts (visual art, music, film, design) | 6 | 4 | 6 | 16 |
| Literature, language, philosophy | 4 | 6 | 6 | 16 |
| Social science (economics, psychology, business, culture) | 4 | 2 | 6 | 12 |

**How a passage is built.** With the key filled in, 55 passages have two sentences, 28 have one, 12 have three or four. The dominant pattern is:
1. a context sentence that names a person, work or phenomenon with a descriptor ("Seneca sculptor Marie Watt's blanket art comes in a range of shapes and sizes."), then
2. a long target sentence that carries the blank, usually 25 to 45 words, built from stacked modifiers: introductory phrase, subject with appositive, main verb, then a tail (list, participial phrase, second clause).
One-sentence items are a single long target sentence, typically with an introductory element and an appositive. For S1 items the "second sentence" of the key only exists once the period or semicolon is chosen, so the passage reads as one run before answering.

The content move order inside the target sentence repeats: who/what (with title or appositive) -> what they did or found -> a detail, consequence or contrast. Contrast (`but`, `however`, `though`, `rather`) and result (`thus`, `making it ...`) are common, but logic is tested only in the 7 conjunctive-adverb items.

**Names, dates, places.** 60 of 95 passages name a real person, nearly always as "[descriptor] [occupation] [Full Name]" with no commas ("marine biologist Dr. Albert Jones", "Rice University geoscientist Ming Tang"); this house style is itself the rule tested in the 5 restrictive-appositive items. 37 passages contain a year. About 40 of 95 centre an Indigenous, African or African diaspora, Latin American, or Asian / Asian American subject (Tewa, Navajo, Chickasaw, Mohegan, Hawaiian, Inuit, Nigerian, Kenyan, Haitian, Bengali, Japanese American, Puerto Rican, Mexican). Diacritics and special letters are kept (Monáe, Mānoa, ‘āina, Sáanii, hwæt, Mithöfer, Álvarez, Neuländer, Macías). Titles of works are italic in print.

**Vocabulary.** Mean word length 5.04 / 5.06 / 5.22 letters; words of 10+ letters are 7.2% / 7.9% / 9.0% of tokens (easy / medium / hard). Technical words appear (phytotoxicity, endophytic, subducts, epistolary, oeuvre, frisson, gigapascals) but never decide the answer; a student can solve every item from clause structure alone.

**Punctuation already in the passage.** Em dashes appear in 11 passages (3 / 2 / 6), parentheses in 14, quotation marks in 13. Hard passages use dashes and parentheses near the blank as structure the student must parse, not as the thing being chosen. Two en dashes appear in compound modifiers (3.20 "Nobel Prize–winning", 3.35 "fungi–produced"); neither is tested.

## 4. The correct answer

- **Justification is purely syntactic.** Meaning matters only to decide clause boundaries and, in 4 items, which clause a conjunctive adverb belongs to (2.8, 3.25, 3.29, 3.33). No item needs outside knowledge or vocabulary.
- **What the key carries** (by family): S1 keys are `L, but R` / `L, and R` (11), `L. R` (13), `L; R` (2), `L: R` (1), `L, though; R` / `L; rather, R` style (7). S4 keys carry no punctuation mark (21 of 21; two of them include a function word: `company that`, `waterways and the fact that`). S2 keys are a comma (13) or a colon (6). S3 keys are the partner mark (`L,` 5, `L—` 4, `L)` 1).
- **Distribution of marks in keys:** no punctuation 21, comma alone 20, period 16 (plus 3 combined with a colon, comma or parenthesis), comma + coordinating conjunction 12 (the 11 clause joints plus 3.12 `and, in the process,`), semicolon 10 (7 of them with a comma around an adverb or inside a list), colon 6, dash 4, question mark 2, closing parenthesis alone 1.
- **Marks offered versus keyed:** a dash appears in 19 option sets and is the key in only 4 (all pair items); a colon in 33 sets, key in 7; a semicolon in 39 sets, key in 10; a no-punctuation option in 73 sets, key in 21.
- **Length is no clue:** the key is the shortest option in 34 items, the longest in 39, in the middle in 22.
- **Exactly one acceptable boundary is ever offered.** No item offers both a period and a semicolon version of the same option (0 of 95). No colon key is accompanied by a lone-dash option (0 of 7). No `, and` / `, but` key is accompanied by a semicolon or period option (0 of 11). Mismatched-pair options (comma where the partner is a dash, and so on) appear only when the partner mark is visible in the passage. This "no twin" discipline is what keeps the items unambiguous.

## 5. Distractor recipes

Each of the 285 wrong options was tagged with the error it commits (some carry two tags). Counts are tag instances, easy / medium / hard.

| Archetype | E | M | H | Total | What it does | Illustration |
|---|---|---|---|---|---|---|
| Comma splice | 5 | 13 | 33 | 51 | Comma alone between two independent clauses, including a comma before an introductory phrase that starts the second clause | 2.27 `adjustments, prior`; 3.20 `essays, praising` |
| Missing required mark | 10 | 13 | 8 | 31 | Omits the comma after an intro element, the closing comma/dash of a pair, the colon before an explanation, or the series comma | 2.1 `nutrients` leaves the appositive opened by a comma unclosed |
| Semicolon with a non-clause | 8 | 8 | 11 | 27 | Semicolon where one side is a phrase or dependent clause | 1.8 `asteroids; several`; 2.26 `fungi; producing` |
| Colon in the wrong place | 12 | 7 | 8 | 27 | Colon after an incomplete clause, typically between verb or preposition and its object | 1.5 `of:`; 2.15 `new, sequencing:` |
| Fused sentence | 5 | 11 | 10 | 26 | Two clauses with no mark and no conjunction | 2.2 `1680`; 3.7 `however it` |
| Comma intrudes into a unit | 11 | 6 | 8 | 25 | Comma between subject and verb, verb and object, preposition and object, title and name, or before a restrictive `that` | 2.3 `California,`; 1.29 `company, that` |
| Added word creates the error | 3 | 6 | 10 | 19 | Inserts `and`, `which`, `that`, `it was`, `later` so the sentence still breaks (usually into a comma splice) | 3.8 `Panchali, which was a`; 3.18 `extensive, it was a` |
| Period leaves a fragment | 9 | 4 | 5 | 18 | Full stop before or after a phrase that cannot stand alone | 1.19 `classroom.`; 2.4 `CE. Making` |
| Conjunction without comma | 6 | 6 | 3 | 15 | `L but R` / `L and R` joining two independent clauses | 1.2 `fibers but` |
| Misplaced boundary or adverb | 0 | 3 | 11 | 14 | Boundary on the wrong side of an introductory phrase or conjunctive adverb; the intro phrase is glued to the first clause and a splice appears later | 3.4 `silk by`; 3.29 `1929. For one, the` |
| Stray dash | 8 | 1 | 1 | 10 | Single dash with no partner and no role | 1.9 `from—`; 1.22 `of—` |
| Mismatched pair | 0 | 8 | 2 | 10 | Closes or opens a pair with a different mark than its partner | 2.13 `prose,` against an opening dash |
| Question errors | 6+6+6 | 0 | 0 | 18 tags on 15 options | Inverted order in an embedded clause, `?` on a statement, direct question left uninverted or ending in a period | 1.7 `do most people prefer in a diet drink?` |
| Comma after the conjunction | 3 | 1 | 1 | 5 | `L but, R`, `L, but, R`, `L and, R` | 1.31 `world, but,` |
| Commas around a restrictive element | 0 | 2 | 3 | 5 | Treats title + name, or an essential modifier, as nonessential | 3.30 `linguist, Diane Massam,` |
| Logic-wrong adverb placement | 0 | 1 | 3 | 4 | Grammatical but the adverb's meaning fits the other clause | 3.33 `speculative, though` turns "though" into a concession |
| Series errors | 2 | 1 | 4 | 7 | Semicolon or colon inside a simple list; commas only, or misplaced semicolons, in a complex list | 3.21 `Basic; in 2009, an online television network;` |

Patterns in how the three wrong options are chosen:
- **One option per neighbouring rule.** A typical set offers the key plus three marks that each break a different rule: for clause joints the splice / fused / conjunction-without-comma trio (8 of 11 comma-plus-conjunction items use exactly `L, but` key with `L but`, `L,`, `L`); for no-punctuation items three single marks drawn from comma, colon, semicolon and dash (13 of 21).
- **Hard items stack comma splices.** 11 hard items have two or more wrong options that are comma splices in different disguises (plain comma, comma plus added `which`/`and`, intro phrase glued to the first clause); only 2 medium and 0 easy items do.
- **Strong marks are always decoys where a phrase follows.** In S2, a period option and a semicolon option appear together in 15 of 19 items, both producing fragments.
- **Mismatched pairs only in S3.** All 10 mismatch tags are in pair items.

## 6. Difficulty

| Signal | Easy | Medium | Hard |
|---|---|---|---|
| Median words in the blank's sentence | 26.5 | 34 | 39 |
| Clause-joining items (S1) | 6 (19%) | 11 (39%) | 17 (49%) |
| Key is "no punctuation" | 11 (34%) | 3 (11%) | 7 (20%) |
| Items with at least one comma-splice option / with two or more | 5 / 0 | 11 / 2 | 19 / 11 |
| Misplaced-boundary or logic-wrong options | 0 | 3 | 12 |
| Length of the introductory phrase that follows a period key (words to its comma) | none (1.14 opens with the subject) | 2 to 3 | 5 to 12 |
| Option sets using four different boundary marks / three / two | 24 / 1 / 7 | 21 / 3 / 4 | 22 / 9 / 4 |
| Conjunctive-adverb placement items | 0 | 1 | 6 |
| Colon-before-explanation items | 0 | 1 | 5 |
| Restrictive appositive (title + name) items | 0 | 0 | 5 |
| Question items | 5 | 0 | 0 |
| Mean word length / share of 10+ letter words | 5.04 / 7.2% | 5.06 / 7.9% | 5.22 / 9.0% |

What concretely separates the tiers:
- **Easy**: the deciding structure is local. The blank sits between a preposition and its object (`of`, `from`, `by`, `to`), a verb and its object, list items, or two short clauses where the second starts with a pronoun subject. Usually four distinct marks per option set (24 of 32), several of them plainly odd (a dash or colon after `of`). All question-form items are easy.
- **Medium**: the deciding clue is a few words away. Pair items need the partner mark found earlier or later (2 to 16 words away); clause items have a short introductory phrase after the boundary (`According to some historians,`, `Prior to VisiCalc's release,`); subject-verb items put a long introductory phrase or a long subject (up to 15 words) before the blank so a comma feels natural. The modifier family (participial `-ing` tails) peaks here.
- **Hard**: (a) the introductory phrase that opens the second clause is long (5 to 12 words: participial, appositive, `As evidenced by ...`) so a comma version looks natural; (b) the same mark appears in two or three options and only its position differs (adverb placement: `information, though;` vs `information; though`); (c) meaning decides the side of the adverb in 4 items; (d) a colon must follow a complete clause and introduce a noun phrase (`extensive: a network ...`); (e) most hard no-punctuation keys (5 of 7) are restrictive appositives where commas look "polite" (`playwright Wakako Yamauchi`). Passage length does not grow from medium to hard (median 47.5 vs 47 words); the difficulty is in structure, not in reading load.

## 7. Skill-specific inventory: every rule tested

Counts are easy / medium / hard. "Wrong-option patterns" lists the tags of the 3 distractors per item, totalled over the rule's items.

### S1 Joining independent clauses (34)

| Rule | E | M | H | Items | Key shape | Wrong-option patterns |
|---|---|---|---|---|---|---|
| Comma + coordinating conjunction between independent clauses | 4 | 5 | 2 | 1.2, 1.26, 1.27, 1.31, 2.2, 2.5, 2.12, 2.17, 2.21, 3.9, 3.31 | `L, but R` (6 with but, 5 with and) | comma splice 10, conjunction without comma 10, fused 9, comma after conjunction 4 (`but,` `, but,` `and,`), colon after conjunction 1 |
| Period between independent clauses | 1 | 4 | 8 | 1.14, 2.7, 2.9, 2.10, 2.27, 3.4, 3.8, 3.10, 3.17, 3.20, 3.28, 3.32, 3.35 | `L. R`; in 12 of 13 the second sentence opens with an introductory element (According to, In 1420 CE, Prior to, By dissolving, A quiet ... drama, Translated as, Analyzing, Praising, Developed by, As evidenced by, By researching) | comma splice 25, fused 9, added word 8 (`and`, `which`, `which was a`, `that,`), misplaced (intro phrase glued to first clause, splice later) 6, conjunction without comma 3. Never a semicolon option. |
| Semicolon between independent clauses | 1 | 1 | 0 | 1.4, 2.22 | `L; R` | comma splice 3, fused 2, added `later` 2, conjunction without comma 1. Never a period option. |
| Colon between independent clauses (second explains first) | 0 | 0 | 1 | 3.16 | `functions:` then a whereas-clause sentence | fused, comma splice, `and,` |
| Conjunctive adverb / transitional phrase: semicolon or period on the correct side, comma on the other | 0 | 1 | 6 | 2.8 (even so), 3.5 (rather), 3.6 and 3.33 (though), 3.7 and 3.25 (however), 3.29 (for one) | `L; even so, R`, `L; rather, R` (adverb opens clause 2); `L, though; R`, `L, however; R`, `L, however. R`, `L, for one. R` (adverb closes clause 1: 5 of 7) | comma splice with the adverb (`, though,`) 10, misplaced side 5, logic-wrong 4, fused 4, semicolon + subordinate `though` clause 2 |

### S2 Main clause plus modifier or explanation (19)

| Rule | E | M | H | Items | Key shape | Wrong-option patterns |
|---|---|---|---|---|---|---|
| Comma after an introductory element | 4 | 2 | 0 | 1.1 (While ...), 1.6 (Because ...), 1.8 (Although ...), 1.19 (Hoping ...), 2.20 (Powered with ...), 2.25 (A conceptual artist ...) | `L,` before the subject | missing comma 6, semicolon 4, period fragment 3, added `and` 2, colon 2, commas around the essential `collected by ...` 2 |
| Comma before a trailing nonrestrictive modifier | 2 | 4 | 1 | 1.11 (such as), 1.32 (which), 2.4 (making), 2.19 (positing), 2.24 (sentence appositive "an apt assessment"), 2.26 (producing), 3.24 (absolute phrase) | `L, R` | semicolon fragment 7, period fragment 6, missing comma 4, added `and` 3, fused 1, colon 1 |
| Colon after a complete clause before explanation, list or specified item | 0 | 1 | 5 | 2.15, 3.2, 3.18, 3.19, 3.22, 3.26 | `new: sequencing`, `high on:`, `extensive: a`, `music: the flute. A`, `plant:`, `continents: geological` | semicolon fragment 5, period fragment 5, missing colon 3, comma splice 2, misplaced period 2. Never a lone dash option. |

### S3 Pairs around a supplementary element (10)

| Rule | E | M | H | Items | Key | Wrong-option patterns |
|---|---|---|---|---|---|---|
| Comma pair (appositive, `according to X`, which clause, interrupter) | 1 | 3 | 1 | 1.10, 2.1, 2.6, 2.14, 3.12 | the missing comma (`movement, which`, `nutrients,`, `Swentzell,`, `method, called`, `and, in the process,`) | missing partner 6, dash or parenthesis instead 5, colon 2, period 1, added `and` 1 |
| Dash pair | 0 | 2 | 2 | 2.13, 2.18, 3.15, 3.34 | `prose—`, `chloroplasts—`, `Culture—`, `models—which` | comma instead 4, missing 4, semicolon 2, colon 1, dash on the wrong side of `which` 1 |
| Parentheses | 0 | 1 | 0 | 2.28 | `estimates)` with no comma after | `estimates),` (comma between verb and its `in` phrase), dash instead, missing |

### S4 Integrated elements, no punctuation (21)

| Rule | E | M | H | Items | Key | Wrong-option patterns |
|---|---|---|---|---|---|---|
| Preposition and its object (incl. passive `by`) | 5 | 0 | 0 | 1.5, 1.9, 1.21, 1.22, 1.23 | `of`, `from`, `by`, `of`, `to` | comma 5, colon 4, dash 4, semicolon 2 |
| Verb and its complement or object | 3 | 0 | 0 | 1.13, 1.15, 1.16 | `blend with`, `appreciate the`, `unearthed` | comma 3, colon 2, period 2, semicolon 1, dash 1 |
| Noun and its prepositional modifier | 1 | 0 | 0 | 1.20 | `pieces` (of pottery) | colon, comma, dash |
| Subject and verb | 0 | 2 | 1 | 2.3, 2.11, 3.13 | `California`, `falling`, `Kingelez` | comma 3, colon 3, semicolon 2, dash 1 |
| Compound joined by `and`; no comma after `that` | 0 | 1 | 1 | 2.23, 3.3 | `waterways and the fact that`, `regions` (+ and what impact) | comma variants around `and`/`that` 4, colon 1, semicolon 1 |
| Restrictive `that` clause | 2 | 0 | 0 | 1.17, 1.29 | `club` (that is ...), `company that` | comma before `that` 2, missing `that` 2, dash 1, `, and` 1 |
| Restrictive appositive (title or descriptor + name) | 0 | 0 | 5 | 3.1, 3.11, 3.14, 3.27, 3.30 | `Entomologist Heather Grab`, `geologist`, `playwright Wakako Yamauchi`, `nations Chile`, `linguist Diane Massam` | comma intrudes 6, colon 4, commas around the name 3, semicolon 2 |

### S5 Series (6)

| Rule | E | M | H | Items | Key | Wrong-option patterns |
|---|---|---|---|---|---|---|
| Commas between items of a simple series | 3 | 0 | 0 | 1.3, 1.12, 1.25 | `life,`, `themselves,`, `libraries, train` | missing comma 3, semicolon 2, colon 2, `. And` 1, dash 1 |
| Semicolons between items that contain commas | 0 | 1 | 2 | 2.16, 3.21, 3.23 | `Stanford;`, `Basic, in 2009; an online television network,`, `Lagos; A Kind of Marriage,` | commas only 3, semicolon in the wrong slot 2, colon 2, no mark 1, missing comma before the item's appositive 1 |

### S6 Question versus statement (5)

| Rule | E | Items | Key | Wrong-option patterns |
|---|---|---|---|---|
| Direct question: inverted order + `?` | 2 | 1.18 (`How ______`), 1.30 (`Where ______`) | `will Umuofia’s traditions be affected?`, `did the word “chortle” come from?` | statement order with `.` or `?`, inverted with `.` (all 3 combinations) |
| Embedded question or relative clause: statement order + `.` | 3 | 1.7 (how much ...), 1.24 (gates Soto would see), 1.28 (mouthpiece where ...) | `most people prefer in a diet drink.` | inverted with `?`, inverted with `.`, statement order with `?` |

### Cross-cutting features

- **Integrated quotations** (2 items, both medium): the blank is at a closing quotation mark; the comma goes inside the closing quote before a trailing modifier (2.19 `soul,” positing`, 2.24 `materialism,”`). Wrong options put a colon, semicolon or period after the quote, or add `and`. Quotations elsewhere (11 passages) flow into the sentence with no introducing comma or colon ("represents her idea that “we all come ...”") but are never at the blank.
- **Parentheses next to the blank** (4): 2.14 (open comma pair before a parenthetical), 2.21 (`(Ru), but`), 2.28 (close paren), 3.35 (`plant). By`).
- **Coordinating conjunctions in keys**: `but` 6, `and` 5. Never `so`, `yet`, `or`.
- **Conjunctive adverbs and transitional phrases in options**: `however` 2, `though` 2, `even so` 1, `rather` 1, `for one` 1, all correct in exactly one position.
- **Dash types**: every tested dash is an em dash; hyphens occur only inside compounds in the passage; en dashes only in 2 untested compound modifiers.

## 8. Generation blueprint

### General template

Every item can be reduced to: a passage string with one boundary slot, the left word `L`, the right word `R` (needed whenever capitalisation or a function word changes), a rule key, and a set of four mark-variants. Everything except the passage text is programmatic.

Slots common to all templates:
- `topic`, `named_entity` (person with "[descriptor] [occupation] [Full Name]" style, or a work/phenomenon), `year` optional;
- `context_sentence` (optional, 12 to 25 words);
- `target_sentence` with the boundary marked, built to the rule's structural recipe below; 25 to 45 words for medium/hard, 12 to 30 for easy;
- `L`, `R`, `rule`, `tier`.

Option rendering (programmatic): apply the rule's variant set to `L`/`R`, capitalise `R` after `.` or `?`, keep proper nouns, shuffle with letter balancing (target 25% each; the official bank leans D at 38%, which we should not copy).

### Per subtype

**S1 Clause joints** (templates: comma+conjunction, period with introductory phrase, semicolon, conjunctive adverb, colon between clauses)
- Author/LLM writes: two independent clauses with a real logical relation. For period keys at hard tier, clause 2 must open with a 5 to 12 word introductory phrase (participial, `By + -ing`, `As + participle`, appositive noun phrase) followed by a comma and its subject; medium uses 2 to 3 word openers (`According to X,`, `In 1420 CE,`).
- Answer logic: key = the one legal joint offered. Never offer an equivalent twin: if key is `.` there is no `;` option and no `, and` option; if key is `, but` there is no `.` or `;`.
- Distractors (programmatic menus taken from the bank):
  - comma+conjunction key: `L R` (fused), `L, R` (splice), `L conj R`; hard variant swaps one for `L conj, R` or `L, conj, R`.
  - period key: `L R`, `L, R`, plus one of `L and R` / `L, which R` / `L that, R`; hard variant replaces one with the "glued intro" form `L intro-word ...` (period removed so the intro phrase attaches to clause 1, leaving a splice at its comma).
  - semicolon key: `L, R`, `L R`, `L and R`.
  - adverb key: generate all placements of `;`/`.` and `,` around the adverb (`L; adv, R`, `L, adv; R`, `L, adv, R`, `L adv, R`, `L; adv R`) and keep the key plus three that are wrong; for adverbs that close clause 1 (`though`, `however`, `for one`), the "opens clause 2" placement is the logic distractor.
- Checks: dependency parse (or LLM judge) confirms both sides contain a finite main clause; the period variant's second sentence is complete; the adverb's meaning fits only the keyed side (LLM judge with a forced explanation).
- Risks: the logic distractor can be defensible (`; however,` often reads fine); short clauses where a comma-less `and` is arguably acceptable; `though` read as a subordinator making the comma version grammatical (3.33 uses exactly this, so the logic must be clear).

**S2 Modifier and colon** (templates: intro comma, trailing modifier, colon before explanation)
- Author writes: a main clause plus an introductory dependent clause / participial phrase (easy, medium), or a trailing `-ing` phrase, `such as` phrase, absolute phrase, `which` clause; for colon keys, a complete clause ending in a word that announces something (`something new`, `far more extensive`, `two varieties of the plant`) followed by a noun phrase or list.
- Distractor menu: `L` (missing), `L.` / `L. R` (fragment), `L;` (fragment), and `L:` for comma keys or `L,`/`L` for colon keys. Never offer a lone dash when the key is a colon.
- Checks: the non-clause side really lacks a finite main verb (parser); for colon keys the left side is a complete clause and the right side is not a second clause unless intended.
- Risks: dash and colon equivalence; trailing modifiers that could also be read as a new clause.

**S3 Pairs**
- Author writes: a sentence with a nonessential element between subject and verb (appositive, `according to X`, interrupter) or a dash-set definition. The program removes one partner mark and makes it the blank.
- Distractor menu: the other two pair marks (comma / dash / parenthesis) and either no mark or a colon/semicolon.
- Checks: the partner mark is present in the passage and of the key's type; removing the whole element leaves a grammatical sentence (proves it is nonessential); no other mark between partners.
- Risks: if the partner is far away the item is fair only at medium/hard; avoid elements that could be restrictive.

**S4 No punctuation**
- Fully programmatic once a sentence exists: choose a boundary between a head and its dependent (subject/verb, verb/object, preposition/object, title/name). Key = bare `L`; distractors = three of `L,` `L:` `L;` `L—` (easy uses comma/colon/dash, medium/hard prefer comma/colon/semicolon). Restrictive appositive items add `L, Name,` (commas around the name).
- Checks: dependency arc crosses the blank (nsubj, dobj, pobj, compound/appos with no determiner before the title); the subject before a subject-verb blank should be long (10+ words) at medium/hard so the comma feels tempting.
- Risks: restrictive vs nonrestrictive appositive ambiguity (`the linguist, Diane Massam,` is acceptable if the title has an article; keep the bank's article-less "occupation Name" form).

**S5 Series**
- Easy: a three-item list of nouns or verb phrases, blank after item 1 or 2; distractors missing comma, semicolon, colon, dash.
- Medium/hard: a three-item list whose items carry appositives or dates (`X, a television play about ...`); the program generates semicolon/comma permutations at the blank.
- Checks: exactly the items intended; Oxford comma consistent with the rest of the passage.

**S6 Questions**
- Programmatic 2 x 2 grid: {inverted, statement order} x {`?`, `.`}. Author writes either a direct-question opener (`How`, `Where`, `Why` at sentence start or after a colon) or an embedded/relative clause frame (`to determine how much ...`, `the place where ...`).
- Checks: auxiliary insertion (`do`/`did`/`will`) correct in the inverted variants; capitalisation of the following sentence.

### Automatic checks for every item

1. Exactly one `______`, four distinct options, same first word in all non-question items.
2. Options differ only in punctuation, capitalisation and an allowed function-word list for that rule.
3. No equivalent-twin options (period/semicolon, colon/lone dash, `, conj` vs `;`).
4. Each option rendered into the passage and judged by an LLM grader for standard/non-standard with the error named; exactly one standard, and each wrong option's error matches its intended tag.
5. Pair items: partner mark present and of the key's type.
6. Typography: em dash U+2014 with no spaces; hyphens in compounds; curly quotes and apostrophes; commas and periods inside closing quotes.
7. Fact and number sanity on the passage. The official bank itself has a slip (1.31 calls a 1,280 m bridge "even longer" than a 1,377 m one), so numeric comparisons need a check.
8. Balance: answer letters about 25% each; key mark types and rule mix per tier as below.

### Recommended build

- **Distinct templates: 16** (S1: 5, S2: 3, S3: 2 (comma/paren pair, dash pair), S4: 4 (prep/verb object, subject-verb, compound, restrictive appositive/that clause), S5: 1, S6: 1).
- **Items per tier for a first set of 150** (mix follows the bank): easy 50 (no-punctuation 17, clause joints 9, modifier/colon 9, questions 8, series 5, pairs 2); medium 50 (clause joints 20, modifier/colon 12, pairs 11, no-punctuation 5, series 2); hard 50 (clause joints 24, no-punctuation incl. restrictive appositives 10, modifier/colon 9, pairs 4, series 3).
- **Build order**: (1) S1 comma+conjunction and period-with-introductory-phrase (24 bank items; S1 as a whole is half of the hard tier; distractors fully programmatic); (2) S4 no-punctuation (cheap: any good sentence yields an item); (3) S2 trailing modifier and colon; (4) S1 conjunctive adverb (needs the logic judge); (5) S3 pairs; (6) S5 and S6.
