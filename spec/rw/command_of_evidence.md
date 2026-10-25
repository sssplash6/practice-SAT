# Command of Evidence (Information and Ideas): bank analysis

Source: 136 official items in `material/rw/transcripts/command_of_evidence.json` (ids `1.n` easy, `2.n` medium, `3.n` hard). 115 items were checked against their images: every flagged item plus the two unflagged literary items whose blank was missing. The 66 tables and graphs are now in the `table`/`figure` fields. All counts below come from Python run over the corrected transcript, plus per-item coding notes (subtype, data shape, claim mapping, one label per wrong option) made while viewing each image. Item ids are cited as examples. Wording in quotes is kept under 15 words.

## 1. Snapshot

| | easy | medium | hard | all |
|---|---|---|---|---|
| items | 45 | 43 | 48 | 136 |
| answer A / B / C / D | 14 / 7 / 14 / 10 | 9 / 14 / 10 / 10 | 13 / 12 / 10 / 13 | 36 / 33 / 34 / 33 |
| passage words (prose only) min / median / max | 20 / 66 / 113 | 25 / 68 / 109 | 26 / 97.5 / 119 | 20 / 76 / 119 |
| passage + options words, median | 112 | 157 | 187 | |
| items with a table or graph | 25 | 20 | 21 | 66 |

The letters are balanced overall (33 to 36 each). Within subtypes there is some skew, which a generator should not copy: quantitative completion answers are C 18 times out of 43, and quantitative description answers are C only once out of 23.

Passage length by subtype (prose words, median, easy / medium / hard):
- quantitative completion: 60.5 / 69 / 101
- quantitative description: 78 / 65 / 97
- textual finding: 72 / 90 / 107.5
- literary quotation: 27 / 40.5 / 39 (only the setup; the quotations are the options)
- quotation from a source person: 70 / 59.5 / 90

Other features:
- **Data displays:** 36 tables and 30 graphs (19 bar, 11 line). There are no scatterplots, pie charts or dot plots. Every table and graph has a title. One table has a footnote (2.24, rounding).
- **Blanks:** 63 items have a `______`. 43 are data completions, where the blank is always the last thing in the passage. 20 are literary quotation setups, where it follows a colon or "says,".
- **Underlined claim:** 10 items (1.14, 1.17, 1.32, 1.41, 2.4, 3.6, 3.19, 3.21, 3.23, 3.40). 2.30's stem also names an underlined claim, but no underlining shows in the image.
- **Polarity:** 120 items ask for support, illustration or completion. 7 ask the student to weaken (2.16, 2.30, 3.1, 3.9, 3.10, 3.48, plus 3.21 "challenges"): none easy, 2 medium, 5 hard.

Stem families (136):

| family | count | wording variants |
|---|---|---|
| data completion | 41 (+2) | "Which choice most effectively uses data from the table/graph to complete the X?" X = statement 19, example 9, text 6, assertion 3, claim 1, comparison 1, researcher's example 1, student's conclusion 1. Two more completions say "to support the statement" (1.38) or "to illustrate the claim" (3.30). |
| data description | 23 | "Which choice best describes data from/in the table/graph that support [Name]'s conclusion/claim/assertion?" (18). "Which choice most effectively uses data from the table to support/justify..." (5). One says "weaken" (3.1). |
| hypothetical finding | 38 | "Which finding, if true, would most directly support/weaken [Name]'s hypothesis/conclusion/claim?" Variants: "most directly" 34 vs "most strongly" 4; "finding" 33, "statement" 4, "detail" 1; 9 narrow it ("Which finding about the basin", "from the model tests"); "support" 32, "weaken" 5, "illustrate" 1. |
| literary quotation | 20 | "Which quotation from [Title] most effectively illustrates the claim?" (19: 17 name the title, 1 says "from the poem", 1 "from a translation of Hedda Gabler"). Also "Which choice most effectively uses a quotation from King Lear to illustrate the claim?" (3.37). |
| quotation from a source person | 12 | "Which quotation from a participant / survey respondent / work by a historian / literary critic / art critic / scholarly article / the interviews would best illustrate / best support / be the most effective evidence for the student to include in support of this claim / most directly challenge...?" Also 1.32's "Which survey response from a bike rider...". |

## 2. Subtypes

| subtype | easy | medium | hard | total |
|---|---|---|---|---|
| Q1 quantitative completion (blank filled with data) | 22 | 13 | 8 | 43 |
| Q2 quantitative description (pick the data statement that supports a stated claim) | 3 | 7 | 13 | 23 |
| T1 hypothetical finding supports/weakens a claim | 9 | 11 | 18 | 38 |
| T2 quotation from a literary work illustrates a claim | 5 | 10 | 5 | 20 |
| T3 quotation from a person (participant, critic, historian) supports a claim | 6 | 2 | 4 | 12 |

**Q1 Quantitative completion (43).** The passage gives a context and a general claim, then ends in a blank, usually after "for example," / "According to the table," / a colon / a dangling clause ("the winds were ______"). Every option is a continuation of that sentence (91 of 172 options start lowercase). The student must (a) find the cells or points the sentence is about and (b) pick the option that is both true of the data and makes the sentence true. In easy items the options are often bare values: 11 easy items have options of one to four words, such as a name, a year, "0.75." or "170 electoral college votes.". In 13 of 22 easy items the four options differ only in numbers or names. Harder items have full-clause options that differ in structure. Stems always say "most effectively uses data from the table/graph to complete the ...".

**Q2 Quantitative description (23).** The passage describes a study and states a conclusion in the last sentence (19 of 23). It almost never mentions the display: only 1 of 23 says "the table" or "the graph". The options are full declarative sentences about the data (mean 26 words; none start lowercase). The student must find the one statement that is accurate and that bears on the specific conclusion. Typical wrong options are true but address something else, or are false readings. One item (3.1) asks which data weaken a hypothesis: the answer shows no difference between conditions.

**T1 Hypothetical finding (38).** The passage reports a researcher's hypothesis, conclusion, claim or prediction, usually in the last sentence (34 of 38). The options are "if true" findings, all plausible and on topic. The student must pick the finding whose truth makes the claim more likely (or less, for weaken). Most of the work is spotting which observable outcome the claim predicts and which comparison group is needed. Claim forms (author's coding):
- **Competing explanations, choose the evidence that discriminates (10):** 2.9 wet-and-warm vs brief melt; 3.8 urban vs sparse; 2.30, 3.6, 3.9, 3.10, 3.14, 3.15, 3.48, 1.25.
- **Causal or effect claim (7):** 1.1, 1.17, 1.41, 2.16, 2.21, 2.38, 3.25.
- **Group comparison, moderation or interaction (7):** 1.35, 2.6, 2.7, 2.43, 3.39, 3.41, 3.42.
- **Existence of a behavior or property (6):** 1.5, 1.8, 1.29, 1.45, 2.33, 3.7.
- **Generalization or association across cases (4):** 2.1, 2.4, 3.12, 3.47.
- **Prediction about the future (2):** 3.28, 3.36.
- **Explicit two-part claim (2):** 3.31, 3.45.

**T2 Literary quotation (20).** No excerpt is printed. The passage is an attribution line ("Title is a YEAR genre by Author."), 0 to 2 sentences of plot context, and a claim about a character, speaker or setting. It ends with `: ______` (15), or with the blank completing a lead-in: "as is evident when [she] says, ______" (2.26, 2.36), "writing, ______" (1.36), "as when Mansfield writes of the teenager, ______" (3.34), or "as is evident when he ______" (3.37, whose options start with a verb). Each option is a quotation of 1 to 3 sentences or 1 to 4 poem lines (median 24 words easy, 25 medium, 31 hard). The student matches the quotation to every element of the claim.
- Genres: poem 7, short story 4, novel 4, play 4, travel book 1.
- Dates: 1606 to 1922, all public domain (Shakespeare, Wheatley, Austen, Brontë, Whitman, Trollope, Ibsen, Wilde, Dunbar-Nelson, Dunbar, Mansfield, McKay, Cather, Sophocles in an 1870 translation).

**T3 Quotation from a source person (12).** An informational passage about a person, artwork or study ends with someone's claim (11 of 12 in the last sentence). Each option is a quotation attributed to a participant, respondent, historian or critic. The student picks the one that states the claim's content. In 3.21 the task is reversed: pick the quotation that challenges the underlined claim.

## 3. Passages

**Subject areas (author's coding, 136):**

| area | easy | medium | hard | total |
|---|---|---|---|---|
| life science (ecology, animal behavior, plants, genetics, physiology) | 8 | 10 | 12 | 30 |
| earth and space science (rivers, volcanoes, glaciers, astronomy, paleontology) | 5 | 6 | 9 | 20 |
| technology and engineering | 3 | 1 | 2 | 6 |
| psychology and behavior | 4 | 3 | 2 | 9 |
| economics and business | 2 | 3 | 5 | 10 |
| sociology, education, geography | 7 | 4 | 2 | 13 |
| linguistics | 0 | 0 | 2 | 2 |
| archaeology and anthropology | 0 | 2 | 3 | 5 |
| history | 7 | 1 | 1 | 9 |
| arts and humanities (dance, fashion, music, sculpture, literary studies, philosophy) | 4 | 3 | 5 | 12 |
| literature (literary quotation items) | 5 | 10 | 5 | 20 |

Natural science dominates (56), mostly in data and finding items. All 20 literature items are T2. Arts and humanities passages are mostly T1 and T3. Easy history and geography items are often simple table lookups: tribal land areas (1.38, 1.44), an 1844 election (1.33), pyramids (1.43), French guilds (1.27).

**Genres:**
- informational science or social-science paragraph with a named study (T1, Q2): 61
- informational paragraph with a data display and a final blank (Q1): 43
- literary attribution plus claim, no excerpt (T2): 20
- informational paragraph about a person or work, ending in someone's claim (T3): 12

There are no cross-text pairs and no notes lists.

**Sentence-by-sentence moves:**
- **T1:**
  1. Background or definition, often with an inline gloss ("transposons, DNA sequences that move within an organism's genome").
  2. Named researchers and what they did ("analyzed hundreds of hours of recordings").
  3. Optionally, a prior belief or a result that sets up a contrast ("have long believed", "But"). 19 of 38 contain a contrast word; 6 open with an explicit prior-belief setup.
  4. The claim, hypothesis or conclusion, last (34 of 38).

  Medians are 3 sentences (range 1 to 5).
- **Q2:**
  1. Context.
  2. Method, naming exactly the variables that become the table columns or graph series.
  3. Conclusion, last.

  Medians are 3 sentences (range 2 to 7). The conclusion is a paraphrase of a data pattern, never a number.
- **Q1:**
  1. Context.
  2. Optionally the study or "A student is researching ...". 19 of 136 passages involve "a student": 9 are Q1, 4 Q2, 3 T1, 3 T3.
  3. A general statement.
  4. The blank.

  The general statement often contains the quantifier the data must satisfy: "Several states saw rapid growth", "varied widely depending on which occupation", "sex-specific differences".
- **T2:** attribution line, then optional context, then claim plus blank.
- **T3:** context about the person or work, then "a student / curator / researcher claims that ...".

**Names, dates, places:**
- Researchers are real and named in full, often with diverse names and diacritics (Angélica Torices, De'Aira Bryant, Veronika Bókony, Raúl Hernández-Pérez).
- 35 passages use "Name and colleagues", "and her team" or "et al."; 11 name two researchers.
- 30 passages include a year ("In a 2022 study", "built ... in 1992").
- Places are specific (Brazilian Pantanal, Evron Quarry in Israel, Lake Mjøsa, a site in Oman).
- Unattributed actors are generic: "a student", "a researcher", "museum administrators".

**Vocabulary (non-literary passages):**

| | easy | medium | hard |
|---|---|---|---|
| words of 9 or more letters | 12.8% | 15.4% | 16.9% |
| mean sentence length (words) | 19.4 | 24.1 | 28.8 |
| longest sentence (words) | 59 | 58 | 69 |

Technical terms are usually glossed in apposition or parentheses, so domain knowledge is never required. Hard passages stack these glosses (3.2 defines liquid chromatography mid-sentence; 3.20 explains how correlation strength is read).

## 4. The correct answer

- **T1:** The key operationalizes the claim. It names the observable outcome the claim predicts, for the right entity, and with the needed comparison.
  - Easy: one step, the claim's variable measured directly (1.1: more heliostats, under six minutes).
  - Hard: one inference. In 3.9, recipients withdrawing all transfers as cash removes the money-form difference, so the explanation is weakened. In 3.14, bank collapses at many upstream points mean diffuse sediment input. In 3.45, E. coli surviving digestion shows the feeding risk the venom is said to reduce.
  - The key rarely repeats the claim's wording; it substitutes concrete terms (claim "help care for newborns", key "feeding young that are not their own").
- **Q1:** The key must be true of the data and must make the sentence's claim true. When the sentence states a contrast ("all wanted cooler, ______"), the key supplies the contrasting data point (1.7). When the claim is quantified ("several states"), the key covers multiple entities (1.6).
- **Q2:** The key reports the exact pattern the conclusion names, at the needed scope: all three columns (3.20), every region plus the overall share (3.24), both periods (3.30), both treatment groups against control (3.43). Its wording echoes the variable names in the display ("further from 0", "provisioning services").
- **T2, T3:** The key matches every element of the claim. In two-part claims (2.26 virtuous and unforgiving; 3.17 aware of grief and believes it justified; 3.34 pleasant looks, unpleasant attitude) it is the only option with both parts.
- **Length is not a cue.** The mean ratio of key length to mean distractor length is 1.02 (Q1), 0.97 (Q2), 1.06 (T1), 1.13 (T2) and 1.01 (T3). The key is strictly the longest option in only 25 of 136 items. Options within an item are built to the same frame: same subject, same length band, same data vocabulary.

## 5. Distractor recipes

408 wrong options were labelled (3 per item). Textual items (T1, T2, T3: 210 options):

| archetype | T1 | T2 | T3 | how it is built |
|---|---|---|---|---|
| off-target (on topic, misses the claim's key element) | 56 | 21 | 21 | same entity, different variable. 1.1: an option about flavor when the claim is about roasting time. 1.15: describes the dance's sound, not its source. |
| wrong subject (right relation, wrong entity, group or time) | 21 | 5 | 5 | 3.15: frog-to-frog transfer when the claim is snake-to-frog. 2.16: emotionality vs star ratings instead of box office. 3.36: new students now instead of former students as adults. |
| opposite (would weaken when support is asked, or vice versa) | 18 | 2 | 3 | 2.9: a short-lived water influx (fits the rival "brief melting" view). 3.28: the model works faster (favors replacement). |
| half-match (one part of a two-part claim) | 2 | 19 | 4 | literary items: the quotation shows only the unpleasant attitude, or only New York and not the island. 1.13: relief without confidence. |
| keyword lure (shares a word or image, not the meaning) | 2 | 12 | 2 | 1.36: "none has understood you" for a claim about not understanding oneself. 2.13: an important tone in speech when the claim is about appearance. |
| other logical traps | 8 | 0 | 0 | 3.14: sediment entering downstream of the sampling sites (cannot affect them). 3.9: a spending-rate difference consistent with the explanation. 3.42: a mismatched comparison that confounds two factors. 3.39: compares stores within one spacing level instead of the effect size. |
| restates context, too general, partial, reversed | 7 | 1 | 1 | 2.1: restates the human hippocampus fact already in the passage. 2.10: vague "advantages". |

Quantitative items (Q1, Q2: 198 options):

| archetype | Q1 | Q2 | how it is built |
|---|---|---|---|
| inaccurate (false reading of a value or relation) | 30 | 28 | misplaced value (2.27: 6.3 belongs to thermostats, not cars). Wrong extreme (1.14: calls the 2013 peak the low). Wrong threshold (2.25: "above 30" when the bar is about 27). |
| wrong group (right operation, wrong row, series, year or condition) | 37 | 3 | the value of a neighboring row or series (1.43, 1.44: heights or areas of the other entities). The other region's bar (1.2). The other temperature source (3.29). |
| accurate but irrelevant (true data that does not address the claim) | 17 | 21 | a different measure (2.14: phosphate when the claim is about nitrate). A comparison inside one condition (2.3, 3.1). Sameness where difference is claimed (1.4). |
| partial or cherry-picked (single point, one group, one year) | 10 | 11 | a single-year value where a trend is claimed (2.40, 2.22). One group without the control (2.25, 3.1). The extremes only, not "every region" (3.24). |
| wrong direction (comparison reversed) | 16 | 0 | full 2x2 option sets of larger/smaller (1.3, 1.9). A lower bar named as higher (1.21). |
| outside the data | 11 | 0 | a number or category not in the display (1.31: 10%, 20%, 45%, none near a bar). 2.39: categories the graph lacks. 3.4: baselines not graphed. |
| contradicts the claim (true data pointing the other way) | 4 | 4 | 1.10: a true decline offered as an example of growth. 3.2: a compound present in the soil sample, which suggests contamination. |
| half-match | 0 | 2 | 3.18: the mass decrease paired with an irrelevant toxin count. |
| other | 4 | 0 | 1.33: numbers lifted from elsewhere (digits of another cell, or the passage's year 1844 recast as "44 votes"). |

Q1 leans on mechanical misreads (wrong group plus wrong direction is 53 of 129). Q2 leans on the true-or-false versus relevant-or-irrelevant split: 28 of 69 Q2 distractors (41%) are false readings (3 of them also outside or partial, counted once), and 41 (59%) are true but insufficient. Section 7 has the full misuse catalogue.

## 6. Difficulty

| signal | easy | medium | hard |
|---|---|---|---|
| share Q1 completion | 22/45 | 13/43 | 8/48 |
| share Q2 description | 3/45 | 7/43 | 13/48 |
| share T1 finding | 9/45 | 11/43 | 18/48 |
| pure lookups (P1, section 7) | 10 | 1 | 0 |
| quantified, multi-part, condition-vs-control data claims (P5 + P8) | 0 | 7 | 13 |
| Q1 options differing only in numbers or names | 13/22 | 1/13 | 2/8 |
| data points in the display (median) | 8 | 9 | 12 |
| displays with 3 or more series | 7/25 | 13/20 | 13/21 |
| weaken items | 0 | 2 | 5 |
| passage words (median) | 66 | 68 | 97.5 |
| passage + options words (median) | 112 | 157 | 187 |
| mean sentence length | 19.4 | 24.1 | 28.8 |

What separates the tiers concretely:
- **Easy:**
  - Data: a single named cell or bar, a min or max, or one pairwise comparison, with value-only options.
  - Findings: one-step operationalizations, with off-target distractors on obviously different variables (flavor, peeling, funding).
  - Literary: plain-language texts (1856 to 1921) with a single-trait claim.
- **Medium:**
  - Data: trends over time and treatment vs control in grouped bars or multi-line graphs, often read as "about" values. Distractors are full statements that are subtly false (2.12: "above 200 April to July"; 2.34: rank and direction in one year).
  - Literary: two-part or contrast claims, so half-match distractors dominate (13 of 30 literary wrong options at this tier).
- **Hard:**
  - Data: claims with quantifiers ("for each of the three", "all except one", "every region ... majority overall"), interactions (3.26 morph x genus) or combining a passage number with the display (3.16, 3.19).
  - Findings: the claim discriminates between explanations, and the key requires an inference about mechanism or study design. "Opposite" distractors rise (12 of 54 T1 wrong options, vs 2 of 27 in easy).
  - Literary: older or translated language (Sophocles, Shakespeare, Trollope, Cather) and longer quotations (median 31 words).
  - Weaken polarity appears.

## 7. Skill-specific inventory: data-claim structures

### 7.1 Data structures (66 items)

- **Tables (36):**
  - Rows: 2 to 5. Columns: 2 to 5, including the label column.
  - Commonest shapes (rows x columns): 3x3 (6), 5x4 (6), 4x4 (4), 2x4, 5x3 and 4x5 (3 each). Largest: 5x5.
  - 16 tables have a categorical column besides the row label: type, yes/no, size class, years built, observatory instrument.
  - Cells hold:
    - plain numbers with units in the header;
    - percents;
    - signed values (effect values −0.6254 in 1.40; correlations in 3.20; percentage-point changes in 3.23);
    - year ranges;
    - "not detected" (3.2);
    - "≤0.03" (2.14);
    - missing cells (3.40).
  - Headers carry units in parentheses. 2.14 has a two-level header (2 areas x 2 depths). 3.24 puts overall percentages inside the column headers.
- **Bar graphs (19):**
  - Single series: 5 (3 to 5 bars, such as glacier areas or volcano deformation).
  - Grouped, 2 series: 6 (1 to 4 categories; 1.2 is just two bars).
  - Grouped, 3 series: 8 (2 to 6 categories; 3.30 has 3 series x 6 years).
  - The y axis has labelled gridlines (steps of 25, 50 or 100), and values often fall between gridlines, so the text uses "about".
- **Line graphs (11):**
  - Mostly 3 or 4 lines (9 of 11).
  - x points: 3 to 12 (seasons, years, decades, minutes from treatment, marketing years).
  - One single-line graph (1.14, 10 years).
- **Value types:** plain quantities with units (20), percents (13), counts (9), and assorted ratings, indices, correlations, signed changes, ages and concentrations.

### 7.2 Claim-to-data mapping patterns

Each quantitative item has one primary pattern:

| pattern | what the claim or blank requires | easy | med | hard | Q1 | Q2 | examples |
|---|---|---|---|---|---|---|---|
| P1 lookup | read one named cell or bar, or reverse-lookup (find the row with value v, report another column), or filter rows by a value | 10 | 1 | 0 | 11 | 0 | 1.30 one cell; 1.37 reverse lookup; 1.12 rows where moons = 1; 1.40 the row with a negative effect |
| P2 extreme or rank | max or min in a column or series, or the entity that is max on two measures | 6 | 0 | 1 | 6 | 1 | 1.9 largest; 1.23 min in both columns; 1.34 the year that is the peak for both rows; 3.44 filter then earliest |
| P3 pairwise comparison | two entities on one measure (A > B), or two comparisons together | 6 | 5 | 1 | 11 | 1 | 1.3 shorter footprint but longer stride; 2.28 subtractive vs additive; 2.32 one comparison per year; 3.29 the same element from two sources |
| P4 change over time | rise, fall, endpoints despite variation, shape similarity, distribution shift | 3 | 5 | 0 | 5 | 3 | 1.10 big rise in one country; 1.14 endpoints show a fall; 2.12 same rise-then-fall shape; 2.22 the majority moves from small to large diameters |
| P5 condition vs control | treated vs untreated at the same point, a gap between paired bars, no difference between conditions | 0 | 6 | 6 | 6 | 6 | 2.5 treated above untreated at 48 h; 2.25 nitrogen above control every year; 3.1 conditions equal (weaken); 3.46 the ethylene gap by temperature |
| P6 passage criterion plus data | combine a number or relation stated in the prose with the display | 0 | 2 | 3 | 2 | 3 | 2.8 artifacts above the 400 °C threshold in the passage; 3.16 four times the force with nearly equal weight; 3.19 61 million vs 15 million first-language speakers; 3.27 a bound between the two estimates |
| P7 presence or absence | detected vs not detected, yes/no column, fluctuation with gaps | 0 | 0 | 3 | 1 | 2 | 3.2 in the meteorite, not in the soil; 3.22 rows with "no" |
| P8 quantified or multi-part claim | "for each", "all except one", "every ... and majority", opposite movement of two measures, order reversal, counterexample to a monotonic trend, interaction | 0 | 1 | 7 | 1 | 7 | 3.20 all three columns; 3.23 necessary but not sufficient; 3.24 every region plus the overall majority; 3.30 order flips between 2005 and 2010; 2.42 largest bill with the coolest habitat; 3.26 the effect varies by morph and genus |

The pattern predicts the tier almost on its own: P1 and P2 are 16 of 18 easy, while P5, P6, P7 and P8 are 0 easy and 28 medium or hard.

### 7.3 How distractors misuse data (exact mechanics)

1. **True data, wrong measure.** The statement is accurate but about a column or series the claim does not name: phosphate for a nitrate claim (2.14); lunges per dive for a filter-time claim (2.18); defense or nondefense outlays for a total-outlays claim (3.23 A, C).
2. **True data, no comparison.** The claim is comparative or causal, and the option reports one group or condition alone, accurately (2.25 D, 3.1 A and D, 2.3 C). The commonest Q2 trap.
3. **Wrong comparison axis.** It compares across the wrong dimension: across years when the claim is about treatment (2.25 C); between two large papers when the claim is about size (1.22 A, B).
4. **Cherry-picked single point.** A trend or "every X" claim answered with one year, one site or the two extremes (2.40 A, 2.22 B, 3.24 D, 3.40 B).
5. **Half the multi-part claim.** Toxin without growth, or growth without toxin (3.18 A, C); only the share in each region, not the majority overall (3.24 C).
6. **Reversed direction.** Larger vs smaller swapped. In easy items this is built as a full factorial: all four combinations of two comparisons (1.3: longer/shorter footprint x longer/shorter stride; 1.9, 1.23 similar), so exactly one combination matches the table.
7. **Wrong row or series, right frame.** The same sentence with a neighbor's value (1.37, 1.38, 1.43, 1.44, 2.41), the other region's bar (1.2), Japan's line for Algeria (2.15), the slow source instead of the fast one (3.29).
8. **Misplaced value.** A real number from the display attached to the wrong label (2.27 A, B swap thermostat and car values; 2.28 D gives the "neither" bar as subtractive).
9. **Near-miss threshold.** A value just across a stated bound: "above 30" for a bar at about 27 (2.25 A); "more than 80%" for about 78 (3.5 C); "more than 105 days" for about 104 (2.40 D).
10. **Wrong extreme or turning point.** Calls the peak year the low (1.14 B), calls the US low point its highest (2.34 D), or names the wrong year for a shared peak (1.34).
11. **Sameness offered as difference, or the reverse.** Equal values offered as an example of variation (1.4 A, D; 2.24 B); a near-equal pair offered as a strength difference (3.20 A).
12. **Contradicting evidence.** True data that points away from the claim: a decline as an example of growth (1.10 D, 1.6 A); the hypothesis-confirming pattern offered for a "not fully supported" conclusion (2.42 C); a compound found in soil (3.2 B).
13. **Outside the display.** Categories, baselines or values that are not shown (2.39 B, D; 3.4 B, D; 1.31 B, C, D; 3.22 D). It includes numbers assembled from elsewhere (1.33: the passage year or a cell's digits).
14. **Sign confused with strength.** With signed data, an option that is true about signs but not about magnitude (3.20 C, where negative vs positive is not "stronger").

### 7.4 Textual claim-to-evidence mapping

- **T1:** The finding must instantiate the claim's variables in an observable outcome, keep the claim's entity, and include the comparison group when the claim is comparative. Wrong options break exactly one of these: a different variable (off-target), a different entity (wrong subject), the comparison or its direction (partial, reversed), or the polarity (opposite).
- **T2 and T3:** Decompose the claim into components (agent, attitude or action, object, and sometimes a contrast or time). The key matches all components. Distractors match zero (off-target), one of two (half-match) or only a surface word (keyword lure).

## 8. Generation blueprint

### 8.1 Q1 and Q2 quantitative (build first; most programmatic)

**Item object.** `{domain, entities[], measures[], units, display: table|bar|line, data[][], claim_pattern P1..P8, claim_predicate, prose_slots, options[4], answer, distractor_types[3]}`.

**Step 1: dataset.**
- Pick a display shape from the bank's range:
  - tables of 2 to 5 rows and 2 to 5 columns;
  - bar graphs of 1 to 3 series by 2 to 6 categories;
  - line graphs of 2 to 4 series by 3 to 12 x points.
- Sample values from a domain profile (unit, realistic range, rounding).
- Then enforce constraints, in this order:
  1. The target predicate is true. Example for P5: treated > control at every x.
  2. Every distractor predicate has its intended truth value.
  3. Readability:
     - graph values that the options cite sit on or within a quarter gridline of a tick;
     - differences the student must see are at least one gridline (or at least 10% relative) apart;
     - there are no accidental ties unless the item is about sameness;
     - near-miss values used for threshold traps (category 9) sit 3 to 8% from the bound.
- A small solver (rejection sampling is enough at these sizes) regenerates until all constraints hold.

**Step 2: claim.** Choose a pattern and instantiate its predicate over the data. Examples:
- P3: `cmp(row=A, row=B, col=m, op=">")`
- P4: `trend(series=s, t0, t1, dir=up, min_change=k)`
- P5: `all(x: treat[x] - control[x] > d)`
- P8: `forall(col in C: |v[r1][col]| > |v[r2][col]|)`, or `necessary_not_sufficient(cond, outcome)`

Render the claim in prose:
- Q1: a general statement followed by "for example, ______" or a dangling clause.
- Q2: a researcher's conclusion as the last sentence. It is a paraphrase of the predicate, never a number.

**Step 3: four statements.** Represent each option as a structured statement `{entities, measure, operation, values, quantifier}` and render it through a template. Q1 options are lowercase continuations; Q2 options are full sentences of 15 to 40 words with parallel frames.
- **Key:** `true_in_data(stmt) and entails(stmt, claim)`.
- **Distractors** come from mutation operators applied to the key, each producing a known verdict:

| operator | verdict |
|---|---|
| swap row, series or year (wrong group) | false, or true but not entailing |
| flip comparator (reversed) | false |
| substitute another measure column (true, wrong measure) | true, not entailing |
| drop the comparison to one cell or one group (partial) | true, not entailing |
| keep one half of a conjunction (half) | true, not entailing |
| move a value across a threshold or misattach a value to a neighbor label (inaccurate) | false |
| choose a true statement whose predicate implies the negation of the claim (contradicts) | true, refutes |
| cite a category or number absent from the data (outside) | not evaluable |

- **Mix to imitate the bank:**
  - Easy Q1: 2 or 3 of {wrong group, reversed}, often as a full 2x2 factorial or as value-only options.
  - Q2: about 1 or 2 true-but-not-entailing plus 1 or 2 false.

**Step 4: automatic verification.** All four checks must pass; reject the item otherwise.
1. Evaluate every option on the data with the same predicate engine. Exactly one option must be `true and entails`. No distractor may be `true and entails`, including under the "about" tolerance used for graph readings (evaluate with the reading tolerance both ways).
2. Recompute any derived numbers (ratios, differences) quoted in options.
3. For graphs, render the chart and run the predicate on values rounded to the nearest readable gridline fraction, as a student would read them.
4. Structural checks:
   - Q1 has exactly one blank, at the end;
   - Q2 has no blank and the conclusion in the last sentence;
   - option lengths are within ±35% of their mean;
   - answer letters are balanced over a batch;
   - the passage does not state the key's numbers.

**What needs a language model:** the 2 to 5 sentence context and method prose (with inline glosses), the domain choice, and natural paraphrases of the predicate. Keep the prose slots constrained: context, researchers (invented names), method naming each measured variable, claim.

**Risks:**
- Unrealistic data (impossible magnitudes).
- Graph values the student cannot read to the option's precision.
- Two options defensible because "supports" is read loosely (for example, a single-group true statement that some reviewers accept as support). Mitigate by always making the claim comparative or quantified when the pattern is P3 to P8.
- Paraphrase drift, where the prose conclusion no longer matches the predicate.

### 8.2 T1 hypothetical finding

- **Slots:**
  - background with gloss;
  - researchers and method;
  - the claim (one of the 7 forms in section 2), last;
  - a competitor explanation, when the form is "competing explanations";
  - the polarity (support or weaken).
- **Answer logic:** write the claim as `IV -> outcome` for `entity`, with `comparison group`. The key states an observation that would follow if the claim is true and not under the rival.
- **Distractors:** one each from {off-target: same entity, different outcome variable; wrong subject: right outcome, different entity or time; opposite: the rival's prediction}. A fourth kind for hard items: a logically void finding (wrong location or timing, a confounded comparison, a pattern consistent with both explanations).
- **Programmatic part:** the claim schema, and slot substitution to build the three distractor types from the key. **Needs an author or model:** the passage, the plausibility of every finding, and the hard-tier logic traps.
- **Checks:**
  - a model judge, sampled several times, must pick the key and must label each distractor with its intended type;
  - no option may be already stated in the passage;
  - the key may not share more content words with the claim than the best distractor does by a wide margin (the bank avoids echo cues).
- **Risk:** distractors that a careful reader could argue also support the claim, especially for "opposite" at the weaken polarity.

### 8.3 T2 literary quotation

- **Slots:** a public-domain work (pre-1929, author, year, genre), 0 to 2 context sentences, and a claim about a trait, attitude or contrast, in one of three forms: single trait (easy), two-part or contrast (medium and hard), or a stance over time (2.31 cycle).
- **Answer logic:** the key quotation satisfies every component of the claim.
- **Distractors:** quotations from the same work, chosen to satisfy:
  - one component only (half-match);
  - a shared word only (keyword lure);
  - a nearby but different trait or speaker (off-target or wrong subject).
- **Needs:** retrieval from a verified source text, never generated quotations. A model can propose candidate passages and label their components; a string match against the source confirms each quotation exists verbatim.
- **Checks:**
  - every quotation is found in the source;
  - the claim's components are listed explicitly, and only the key covers all of them;
  - option lengths match within one sentence;
  - the passage ends `: ______` or with a lead-in such as "as is evident when ... says, ______".
- **Risks:** archaic language making the key ambiguous, and claims so abstract that two quotations fit.

### 8.4 T3 quotation from a source person

The same logic as T2, but every quotation is invented (participant, critic, historian), so it is fully writable by a model. Slots: the subject (an artist, a program, a study), the claimant (student, curator, journalist), the claim (often two-part), and the polarity (support or challenge). Distractors: off-target (describes the work but not the claimed relation), wrong direction of influence (2.23 C), half-match.

### 8.5 Recommended build

- **Templates:** about 14 distinct templates.
  - Q1: 6 (P1 lookup, P2 extreme, P3 pairwise, P4 trend, P5 control, P6 or P7 combined).
  - Q2: 4 (P4, P5, P8 quantifier, P8 multi-part or interaction).
  - T1: 2 (single-claim support or weaken; competing explanations).
  - T2: 1, with three claim shapes.
  - T3: 1.
- **Mix per tier** (mirrors the bank): easy about 50% Q1 (mostly P1 to P3), 10% Q2, 20% T1, 10% T2, 10% T3. Medium about 30% Q1, 15% Q2, 25% T1, 25% T2, 5% T3. Hard about 15% Q1, 25% Q2, 40% T1, 10% T2, 10% T3.
- **Volume:** 40 to 60 items per tier is a realistic first target (120 to 180 total). Q1 and Q2 can be produced in quantity once the predicate engine exists.
- **Build order:**
  1. Q1 P1 to P4 with tables. Fully programmatic apart from the prose, they cover most easy items, and the predicate engine they need is reused by everything else.
  2. Q1 and Q2 on bar and line graphs (add chart rendering and reading tolerance).
  3. Q2 P5 and P8 for the hard tier.
  4. T1 with a model and a judge.
  5. T3.
  6. T2 last, because it needs a verified public-domain text pipeline.
