# Rhetorical Synthesis (Expression of Ideas): bank analysis

Source: 92 official items (22 easy, 46 medium, 24 hard), transcript `material/rw/transcripts/rhetorical_synthesis.json` (all 92 items verified against the images). Every number below was computed with Python from the corrected transcript; goal types and distractor archetypes were labelled by hand for all 92 items and 276 distractors, then tallied.

Every item has the same shape: an intro line ("While researching a topic, a student has taken the following notes:"), four to six research notes, a goal sentence ("The student wants to ...") and the fixed question "Which choice most effectively uses relevant information from the notes to accomplish this goal?". The four options are single sentences built from the notes. The skill is not reading comprehension: nearly every option is true to the notes, and the item is decided by which sentence does the specific rhetorical job named in the goal.

## 1. Snapshot

**Items per tier:** easy 22, medium 46, hard 24.

**Answer letters**

| Tier | A | B | C | D |
|---|---|---|---|---|
| easy | 8 | 2 | 5 | 7 |
| medium | 14 | 13 | 6 | 13 |
| hard | 6 | 3 | 10 | 5 |
| all | 28 | 18 | 21 | 25 |

Roughly flat overall. B is thin in easy (2 of 22) and C is heavy in hard (10 of 24), but the samples are small.

**Notes length** (words in the bullets, intro line excluded)

| Tier | min | median | max | mean | words per bullet |
|---|---|---|---|---|---|
| easy | 27 | 59.5 | 92 | 58.7 | 12.0 |
| medium | 44 | 65 | 99 | 66.9 | 13.7 |
| hard | 36 | 75.5 | 111 | 75.9 | 14.9 |

Bullet count: 5 bullets in 70 items, 4 in 10, 6 in 10, 3 in 1, 2 in 1 (mean 4.95). The 3- and 2-line cases are items printed without bullet glyphs (see below).

**Layout variants (from the images)**
- 82 items: intro line plus bullet glyphs.
- 10 items (1.15, 1.16, 2.25 to 2.32): the same notes printed as indented lines with no bullet glyphs; some lines carry two sentences. Stored as one "• " line per printed line.
- 1 item (2.38): no intro line and no goal sentence; the older stem "Which choice most effectively uses information from the given sentences to emphasize a difference between the eggs of the two species?"
- 1 item (3.15): hybrid; a normal goal sentence followed by the older stem "Which choice most effectively uses information from the given sentences to emphasize the relative sizes of the two capitals’ populations?"

**Stem variants**

| Count | Question sentence |
|---|---|
| 88 | The student wants to [goal]. Which choice most effectively uses relevant information from the notes to accomplish this goal? |
| 2 | ... to accomplish these goals? (1.19 "define ... and provide an example", 3.11 "make and support a generalization") |
| 1 | legacy, no goal sentence (2.38) |
| 1 | hybrid (3.15) |

Note that the plural "these goals" is not used consistently: the other three "make and support" items and both "explanation and an example" items use "this goal".

**Goal verbs** (first word after "The student wants to", 91 items): emphasize 27, describe 9, present 9, explain 8, provide 8, specify 7, make 5, introduce 4, identify 3, compare 3, contrast 3, summarize 2, define 1, begin 1, use 1. The goal sentence averages 13.5 words (easy 13.2, medium 13.9, hard 12.8).

**Option length** (words): keys average 20.9 (median 21), distractors 19.3 (median 19). By tier the key averages 18.0 / 21.1 / 23.3 against distractors 17.0 / 19.8 / 20.7. The key is the longest option in 28 items, second longest in 28, third in 21 and shortest in 15. In hard it is never the shortest. Length is a weak cue, not a reliable one.

## 2. Subtypes

Every item is "pick the sentence that accomplishes the goal". The subtypes differ in what the goal demands of the sentence. Fifteen goal types, grouped into six families. Counts are easy / medium / hard.

| Family | Goal type | e / m / h | Total | What the student must do |
|---|---|---|---|---|
| Comparison | Similarity (SIM) | 3 / 3 / 1 | 7 | Find the option that names both items and states a trait they share |
| Comparison | Difference (DIFF) | 2 / 8 / 2 | 12 | Find the option that names both items and contrasts them on the same attribute |
| Comparison | Order or relative degree (RANK) | 2 / 3 / 1 | 6 | Find the option that states which is earlier, higher, larger, or hotter, with the right direction |
| Single fact | Specify / identify (SPEC) | 4 / 2 / 1 | 7 | Find the option that answers a wh-question (who, where, how many, what name) |
| Single fact | Emphasize one attribute (EMPH) | 4 / 5 / 0 | 9 | Find the option that foregrounds one quality (distance, harshness, size, uniqueness, duration) |
| Single fact | Describe (DESC) | 3 / 1 / 1 | 5 | Find the option that gives the physical form, configuration, style or process |
| Explanation | Explain cause, origin, advantage, mechanism, definition, significance (EXPL) | 1 / 5 / 4 | 10 | Find the option that states the effect and links it to its cause |
| Explanation | Example, or explanation plus example (EXAMPLE) | 1 / 3 / 1 | 5 | Find the option with a named instance (and, when asked, the general definition) |
| Research | Study aim, method, results (STUDY) | 0 / 3 / 3 | 6 | Find the option that reports the requested slot of the study arc and only that |
| Abstraction | Generalization, with or without support (GEN) | 0 / 2 / 3 | 5 | Find the option with a broad claim, plus the specific case when "support" is asked |
| Abstraction | Overview or summary (OVERVIEW) | 1 / 0 / 3 | 4 | Find the option that spans the whole notes arc at a high level |
| Audience | Introduce or describe to an unfamiliar or new audience (AUD_NEW) | 1 / 6 / 0 | 7 | Find the option that identifies the person or concept before giving the detail |
| Audience | Present or describe to an already familiar audience (AUD_FAM) | 0 / 3 / 2 | 5 | Find the option that gives the new detail without re-explaining the known term |
| Other | Quotation (QUOTE) | 0 / 2 / 1 | 3 | Find the option that quotes the words that carry the goal |
| Other | Begin a narrative (NARR) | 0 / 0 / 1 | 1 | Find the option that starts the story at its chronological beginning |

Family totals: comparison 25 (27%), single fact 21 (23%), explanation 15 (16%), audience 12 (13%), research 6 (7%), abstraction 9 (10%), other 4 (4%).

Two modifiers cut across types and raise difficulty when present: an audience clause (12 items: 1 easy, 9 medium, 2 hard) and a two-part goal (10 items: "make and support", "an explanation and an example", "define ... and provide an example", "aim and methodology", "the study and its findings", "the scientist and her field of study": 1 / 5 / 4). Three goals require a quotation (0 / 2 / 1).

The precise wording of every goal is catalogued in section 7.

## 3. Passages

**Genre.** All 92 are research notes. There is no literary excerpt, table or graph. Two hard items label bullets inside the notes: 3.21 ("Finding: ..." twice) and 3.24 ("Step 1:" to "Step 4:").

**Subject areas** (hand-assigned)

| Subject | easy | medium | hard | total |
|---|---|---|---|---|
| Natural science and technology | 10 | 18 | 11 | 39 |
| Arts and literature | 5 | 13 | 4 | 22 |
| History | 5 | 7 | 5 | 17 |
| Social science and culture | 2 | 8 | 4 | 14 |

Science covers ecology, astronomy, chemistry, geology, materials and neuroscience. Arts items are almost all about one named artist and one titled work (painting, sculpture, installation, leporello, photograph, web series). History leans to US civil rights, Indigenous history and inventors, plus pre-modern empires and libraries.

**How the notes are built.** Five recurring arcs account for nearly every item:

1. *Parallel pair* (most SIM, DIFF and RANK items): a framing bullet that names the shared category, then two bullets for entity X, then two matching bullets for entity Y, written in the same syntax so the attributes line up. Example shape: "Dhaka muslin is ... / It has ... ; Sheeting muslin is ... / It has ...". Comparison attributes are always stated once per entity, in parallel positions.
2. *Study arc* (STUDY, AUD_FAM, several EXPL): background or definition, then researcher and aim ("wanted to better understand", "sought to", "designed a study to find out"), then method, then finding(s), then sometimes an interpretation ("One explanation for this relationship is ...").
3. *Profile* (most arts items, AUD_NEW, DESC): identity line (nationality plus profession: "a Korean American artist", "a Native Hawaiian sculptor"), what the person is known for, a titled work with a year, then one or two physical features of the work.
4. *Definition plus instance* (EXAMPLE, some EXPL and AUD): a term is defined, an instance is named, a detail of the instance follows. Every technical term the options rely on is defined inside the notes (carrying capacity, radiant, leporello, torsion, commodity chain, quenching, Lazarus species).
5. *Event and legacy* (history items): event, motive or context, outcome, lasting effect ("had a lasting impact", "led to a set of 2005 legal protections").

Every arc contains one or two bullets that no goal of the item uses (a museum's city, a founding date, an award) so that distractors can be built from them.

**Sentence style.** Each bullet is one plain declarative sentence (a few printed lines hold two). 20% of bullets (89 of 455) open with a pronoun or demonstrative ("It", "This", "She", "Her", "His", "They", "He"), so bullets lean on the previous one. The most common openers are "The" (83) and "In" (35, mostly dates and places).

**Names, dates, places.** Real people and institutions, with deliberate global and cultural spread: Simphiwe Ndzube, Hesham Sallam, Sada Mire, Maika’i Tubbs, Arelee Estefanía Muñoz-Hernández, Jianbo Tang, Sámi activists, the A:shiwi A:wan Museum. Diacritics, curly apostrophes, subscripts (NH₃, N₂) and units (km², °F, mg/oz) are printed. 52 items have at least one year in the notes and 37 have other numbers; work titles carry a year in parentheses. Hedged claims are kept hedged ("may have populated", "historians believe", "is thought to be").

**Vocabulary.** General academic register with a domain term or two per item, always glossed in the notes. Hard notes are longer per bullet (14.9 words against 12.0 in easy) and denser in nominal phrases ("thermoplastic polyurethane (TPU) fiber", "styrene-ethylene-butylene-styrene (SEBS) rubber fiber"), but the vocabulary itself does not climb much.

## 4. The correct answer

**Justification is goal fit, not truth.** In 258 of 276 distractors the sentence is accurate to the notes (section 5). The key wins because its content and its framing match the goal: the right bullets, joined by the right relation, at the right level of generality for the named audience.

**How much of the notes the key uses.** Estimating coverage by content-word overlap, the key draws on 2.2 bullets on average and the distractors on 2.0 (easy 2.4 vs 2.3, medium 2.2 vs 2.0, hard 2.0 vs 1.8). "Uses the most information" is therefore not the rule; several distractors pack in more facts than the key (2.14 A lists all four of McKay's works; 1.9 B and C each fuse two bullets). The key uses exactly the bullets the goal needs.

**Wording.** Keys are close paraphrases. The share of a key's content words that do not appear in the notes or goal is 11% in easy, 16% in medium and 21% in hard, about the same as for distractors (11%, 18%, 20%), so closeness to the notes does not separate them either. The rewording moves are:
- recombination of two or three bullets into one sentence with an appositive or participial opener ("One of the most influential artists of the twentieth century, Mexican painter Frida Kahlo is best known for ...");
- a relation word added that the notes never state: "both", "whereas", "while", "unlike", "than", "after", "because", "to recognize", "given that", "making ... less reliable";
- small derived claims computed from the notes: "hotter than most but not all" (2.37), "years after" (2.44), "thicker than" (2.41), "accounts for more of its country’s population" (3.15), "range widely in length, from a few dozen miles to a few hundred" (2.12), "Neither of ... two ways ... requires the bird to dive" (3.18), "far less of the rare and expensive metal" (2.3);
- attribution kept when the goal is about a study or a source ("According to a 2015 study", "According to Padmanabhan and Chen").

The key never adds outside facts. The one wording liberty spotted: 3.5 A says "visual effects artist" where the notes say "special effects artist".

**Opening words of the key:** "The" 22, "In" 7, "A" 4, "According" 3, "Although" 3, "While" 2, "After" 2, "One" 2; the rest open with a name or a participle.

**Relation markers in comparison keys:** SIM keys use "both" 5 of 7 times, plus "Like", "as is" and "Neither". DIFF keys use "while" or "whereas" in 8 of 12, plus "Although" (2), "Unlike" and "than". RANK keys use "than" 4 times, "After"/"after" 2, "Even though" 1.

## 5. Distractor recipes

Nine archetypes cover all 276 distractors.

| Code | Archetype | Count | Share | easy | medium | hard |
|---|---|---|---|---|---|---|
| OG | Accurate and on topic, but serves another goal | 132 | 48% | 58% | 49% | 38% |
| PART | Delivers only part of what the goal needs | 65 | 24% | 27% | 21% | 25% |
| VAGUE | Names the goal's relation or quality without the specific content | 19 | 7% | 6% | 9% | 3% |
| FALSE | Misstates, reverses or overstates the notes | 18 | 7% | 2% | 4% | 17% |
| REL | Wrong relation (difference for similarity, or the reverse; wrong dimension) | 15 | 5% | 6% | 5% | 6% |
| AUD | Audience mismatch | 15 | 5% | 0% | 9% | 4% |
| NOQ | Quotation goal: no quotation, or a quotation that does a different job | 7 | 3% | 0% | 3% | 4% |
| LIST | Puts both data points side by side but never states the relation | 4 | 1% | 0% | 1% | 4% |
| OPP | Emphasizes the opposite of the requested quality | 1 | <1% | 2% | 0% | 0% |

**OG, accurate but off-goal (132).** Each unused bullet becomes a sentence that would be right for a neighboring goal. In a "specify the location" item, the distractors give the dates, the territory and the capital's name (1.9). In study items they swap slots: aim offered for results, method offered for aim. The archetype works because the distractor is true, fluent and topical. Example: for "emphasize how far the infantrymen traveled" (1.15), one distractor gives the purpose of the 1897 ride, another the anniversary year.

**PART, partial (65).** The most common shapes: one side of a two-entity comparison ("Sheeting muslin is machine made, has a coarse weave ..."), one half of a two-part goal (definition without example, generalization without support, study without findings, method without aim), and one of several required components in an overview. Example: for an explanation-plus-example goal, an option that only offers a quoted instruction from one meditation (3.4 C).

**VAGUE, empty version of the goal (19).** Asserts that the relation holds but gives nothing to back it: "they are quite different" (2.11 A), "Romney wool will be different than other kinds of wool" (2.10 B), "each serve a purpose for readers" (2.17 C), "developed a distinctive style" without saying what it is (2.4 A). Half of them (10 of 19) sit in DIFF items.

**FALSE, misreading (18).** Rare before hard (1, 5, 12 by tier). Forms: reversed direction (1.17 B swaps which bird is at risk; 2.27 C puts the US march first), conflation (2.44 A puts both keepers in Mississippi; 3.21 B attaches the 52% phosphorus figure to flower blooms), overclaim (3.23 D says the find "disproved" Plot's claims; 3.20 A turns two names into a rule), wrong agent (3.19 D says the NCAI passed the act; 3.24 A says the UV light solidifies), unsupported addition (2.35 A "at the time the Hart-Celler Act was proposed").

**REL, wrong relation (15).** The mirror option in comparison items: a "both" sentence when a difference is asked (1.13 A, 2.41 A, 3.3 B and D), a "whereas" sentence when a similarity is asked (1.10 B, 1.11 C, 1.22 D, 2.24 A, 2.30 A, 2.46 A and B, 3.18 C), or a comparison on the wrong dimension (2.44 D compares when the keepers' careers ended, not when they began).

**AUD, audience mismatch (15).** For a familiar audience, the option re-defines what the audience knows (eDNA defined in 2.1 C and D; leporellos explained in all three wrong options of 2.18). For an unfamiliar audience, the option drops the identifying context ("The rocking chair is made from walnut ..." with no maker, 2.34 D; "Park’s 2013 installation ..." with no word on who Park is, 2.36 A).

**NOQ (7).** Paraphrase where a quotation was required (2.9 B and C, 2.29 B, 3.6 D) or a real quotation that serves another purpose (3.6 A quotes "super-cooperators", which supports the theory instead of questioning it).

**LIST (4).** Both numbers present, relation missing: "The populations of the capitals ... are 907,802 ... and 7,781,631 ..., respectively" (3.15 D).

**Typical mix per item.** A typical item has two OG and one PART or relation-type distractor. Comparison items replace OG with REL plus PART plus VAGUE. Audience items carry one or two AUD. Hard items swap one OG for a FALSE.

## 6. Difficulty

| Signal | easy | medium | hard |
|---|---|---|---|
| Notes words, mean (median) | 58.7 (59.5) | 66.9 (65) | 75.9 (75.5) |
| Words per bullet | 12.0 | 13.7 | 14.9 |
| Key words, mean | 18.0 | 21.1 | 23.3 |
| Key content words not in notes | 11% | 16% | 21% |
| Bullets used by key (estimate) | 2.4 | 2.2 | 2.0 |
| OG share of distractors | 58% | 49% | 38% |
| FALSE share of distractors | 2% | 4% | 17% |
| Items with audience clause | 1 | 9 | 2 |
| Items with two-part goal | 1 | 5 | 4 |

What concretely separates the tiers:

- **Easy (22).** 11 of 22 are single-fact goals (SPEC 4, EMPH 4, DESC 3) where one or two bullets answer the goal almost verbatim (1.4 D "has roughly 100 gray wolves", 1.9 D "located near present-day Baghdad"). Comparison items (7) use clean parallel pairs and an obvious marker. Distractors are OG or PART; only one easy distractor misstates anything. The goal noun points straight at a bullet ("number", "location", "shape").
- **Medium (46).** Introduces the audience clause (9 of the 12 audience items), quotation goals, two-part goals, and DIFF items where the two sides must be matched on the same attribute (2.10: fine wool for apparel vs thick wool for rugs). VAGUE distractors peak here (9%), offering the goal's relation word with no content. Keys start to need a small derivation (2.3 "far less ... than do other platinum catalysts"; 2.44 "years after").
- **Hard (24).** Goals become abstract: GEN 3, STUDY 3, EXPL 4, OVERVIEW 3. The key must compress three bullets or produce a generalization ("can result in huge disparities", "Exoplanet names have diverse origins"). Distractors are closer: accurate sentences from adjacent study slots (aim vs method vs finding: 3.1, 3.10) and subtle misreadings (17% FALSE). Notes are longer and denser. Keys paraphrase more (21% new content words) and are never the shortest option.

Two hard items are hard only because of their distractors, not their goal: 3.19 ("identify an accomplishment") and 3.13 ("explain what a quenched galaxy is") have easy-looking goals but a misattribution or a near-paraphrase of a neighboring bullet among the options.

## 7. Skill-specific inventory: goal types, exact phrasing, key logic, distractor logic

Phrasings are quoted from the goal sentence ("The student wants to ..."). For each goal type, "serves instead" names the goal a distractor would accomplish.

### 7.1 Similarity (7: 3 / 3 / 1)

Phrasings:
- "emphasize a similarity between the Laas Geel paintings and the Dhagah Nabi Galay paintings" (1.10)
- "emphasize a similarity between Beard’s invention and Jones’s invention" (1.11)
- "emphasize a similarity between the two specimens" (1.22)
- "emphasize a similarity between the two works" (2.24)
- "emphasize a similarity in how people in Bangkok and Chiang Mai celebrate Songkran" (2.30)
- "emphasize a similarity between Uros Island and Fortuna" (2.46)
- "emphasize a similarity between the two ways a magnificent frigatebird acquires food" (3.18)

Key: names both items and the shared trait, usually with "both" (5 of 7); the trait is stated once per entity in the notes (genus *Tyrannosaurus* twice; "improved on the existing design" twice) or is a category both belong to (rock art in the same scans; LED sculptures by the same artist). Hard version (3.18): the shared trait is derived; bullet 2 says the bird does not dive, bullets 3 and 4 give two ways of feeding, and the key says neither way requires diving.

Distractors (21): PART 8 (one entity's feature; serves "describe X"), REL 8 (a contrast; serves "emphasize a difference"), OG 3 (dates, exhibition record; serves "give background on the artist"), VAGUE 1 (2.30 C "don’t do so in exactly the same way"), LIST 1 (3.18 D lists both feeding methods with "In addition to"; serves "describe the two ways"). Nearly every SIM item has exactly one REL option and one or two PART options.

### 7.2 Difference (12: 2 / 8 / 2)

Phrasings:
- "emphasize a difference between the two muslins" (1.2)
- "emphasize a difference between the behavior of jellyfish and that of black dragonfish" (1.13)
- "emphasize how Romney wool differs from Merino and Rambouillet wool" (2.10)
- "emphasize a difference between surface-dwelling and cave-dwelling tetras" (2.11)
- "emphasize a difference between the MexiCali Biennial and traditional biennials" (2.19)
- "emphasize a difference between the two books" (3.3)
- legacy: "emphasize a difference between the eggs of the two species" (2.38)
- "contrast the purposes of the two maps in The Hobbit" (2.17)
- "contrast Minnesota’s definition of a lake with Wisconsin’s" (2.23)
- "contrast the two samples" (2.41)
- "compare the causes of crown shyness proposed in the two theories" (2.32)
- "compare the two women’s contributions to the March on Washington" (3.14)

"Compare" behaves like "contrast" here: both "compare" keys are built on a contrast ("While Jacobs proposes ..., Ng posits ..."; "Although Hedgeman worked behind the scenes ..., Bates was the sole woman to speak").

Key: both sides of the same attribute in one sentence, joined by while or whereas (8 of 12), Although, Unlike, or a comparative ("more restrictive than", "thicker than", "were longer"). 3.3 concedes the similarity first and then gives the difference. The attribute chosen is the one the goal names (purposes, causes, behavior), not just any difference.

Distractors (36): OG 12 (define the category or give general background; serves "introduce the topic", e.g. 2.11 C introduces the species and its two populations), VAGUE 10 (says they differ without how; serves nothing; 2.32 C names both theories but not their causes), PART 8 (one side only; serves "describe X", e.g. 1.13 B is only about dragonfish), REL 5 (a "both" sentence; serves "emphasize a similarity", e.g. 2.41 A "the surface temperature of both samples increased"), LIST 1 (2.38 D gives both egg lengths as what the study determined, with no contrast). In 3.3 C the option contrasts the laws the books influenced, which the notes present as what the two books have in common; it is labelled REL.

### 7.3 Order or relative degree (6: 2 / 3 / 1)

Phrasings:
- "compare the extinction risk faced by C. olivacea with that faced by C. furcatus" (1.17)
- "identify which of the three foods has the highest magnesium content" (1.20)
- "emphasize the order in which the two marches occurred" (2.27)
- "emphasize how hot the Sun is relative to nearby stars" (2.37)
- "emphasize the order in which the two lighthouse keepers began their careers" (2.44)
- "emphasize the relative sizes of the two capitals’ populations" (3.15)

Key: an explicit comparative or sequence word with the right direction: "a higher risk ... than", "150 mg/oz ..., which is more than peanuts and almonds", "After ... , suffragists in the US marched ...", "began her career ... years after Maria Younghans did", "hotter than most but not all", "Even though Hanoi ... is larger ..., Ulaanbaatar accounts for more of its country’s population". The key often drops the raw numbers (2.27 and 2.44 give no dates).

Distractors (18): OG 7 (background, e.g. 2.44 B on why keepers mattered), PART 4 (one entity's value or two of three foods: 1.20 A; serves "describe X"), FALSE 3 (reversed order or risk: 1.17 B, 2.27 C; conflation: 2.44 A), LIST 2 (3.15 A and D: both populations with no relation), REL 1 (2.44 D compares end dates, the wrong dimension), VAGUE 1 (1.17 C "have evaluated both").

### 7.4 Specify or identify a single fact (7: 4 / 2 / 1)

Phrasings:
- "specify who may have first populated the Azores, according to the 2015 study" (1.3)
- "specify the number of gray wolves in Yellowstone" (1.4)
- "specify the location of Ctesiphon" (1.9)
- "specify how many chromosomes the pineapple has" (2.39)
- "specify the fanner basket’s name in Choctaw" (2.45)
- "identify the setting of Cather’s novel My Ántonia" (1.5)
- "identify an accomplishment of the NCAI" (3.19)

Key: the one bullet that answers the wh-question, near-verbatim, with the entity named and at most one appositive for context (1.9 D "Ctesiphon, the capital of the Sasanian Empire, was located near present-day Baghdad, Iraq.").

Distractors (21): OG 17 (each other bullet; serves "specify a different fact": dates, area, founders, the archive's name meaning), PART 2 (1.3 B says who was not first; 1.5 D sets "some of her novels" in Nebraska without naming this one), VAGUE 1 (2.39 C "more than the melon does"), FALSE 1 (3.19 D credits the NCAI with passing the law).

### 7.5 Emphasize one attribute (9: 4 / 5 / 0)

Phrasings:
- "emphasize how harsh the conditions can be in the tundra" (1.7)
- "emphasize Wu’s most well-known achievement" (1.14)
- "emphasize how far the infantrymen traveled" (1.15)
- "emphasize how many islands in Komodo National Park have Komodo dragons living on them" (1.16)
- "emphasize the thoroughness of Ida Tarbell’s investigation of the Standard Oil Company" (2.6)
- "emphasize Claude McKay’s accomplishments before moving to Harlem" (2.14)
- "emphasize how long the museum has existed" (2.20)
- "emphasize the uniqueness of Taylor’s accomplishment" (2.33)
- "emphasize the size of Tecozautla" (2.40)

Key: the quantity, superlative or exclusive fact with an emphatic frame: "a frigid –30 degrees", "a total of 1,900 miles", "Only four of the twenty-nine islands", "not only ... but also", "the only Black woman to publish a Civil War memoir", "since 1992", "best known for". 2.14 needs a time filter: the 1912 collections were published before the 1914 move; the famous works came later.

Distractors (27): OG 23 (other true facts; serves "describe the purpose", "give the anniversary", "list the services municipalities provide"), PART 2 (1.16 D total islands only; 2.6 C interviews only), VAGUE 1 (1.16 A "live on islands"), OPP 1 (1.7 C stresses the relatively mild growing season). Traps: 2.14 D opens "Before moving to Harlem" but names the Harlem-era works; 2.20 C gives "the 1990s" plus the mission statement.

### 7.6 Describe (5: 3 / 1 / 1)

Phrasings:
- "describe how fabric is used in Assertion of Will" (1.1)
- "describe the wok’s shape" (1.8)
- "describe how the bicycles in Double Phantom/EntroP.R. are fused together" (1.18)
- "describe the distinctive style of Houser’s sculptures" (2.4)
- "describe how DLS cures 3D objects" (3.24)

Key: the formal-feature bullets merged ("a round, wide base and high, angled sides"; "share the same rear wheel while facing opposite directions"; "employ abstract, modernist forms to depict Native American figures"). 3.24 compresses four labelled steps into the correct order.

Distractors (15): OG 10 (function, history, book about the object, artist identity; serves "describe the wok's function", "identify the artist"), VAGUE 2 (1.18 A "fused together" with no how; 2.4 A "developed a distinctive style" with no description), FALSE 3 (3.24 A, B and D each garble the process: the light solidifies, the object "passes through" the dead zone, curing finishes in the dead zone rather than the oven).

### 7.7 Explain (10: 1 / 5 / 4)

Phrasings:
- "explain the origin of the species’ name" (1.6)
- "explain the origin of the Perseid meteor shower’s name" (2.13)
- "specify the reason the Mayflower Compact was created" (2.7)
- "specify why historians believe Abele designed most of Duke’s campus buildings" (2.15)
- "explain why brine pools are toxic to most sea life" (2.31)
- "explain an advantage of the new platinum catalyst developed by Jianbo Tang and his colleagues" (2.3)
- "explain a disadvantage of relying on audio features to predict a song’s popularity" (3.2)
- "explain how the House of Wisdom preserved the world’s knowledge" (3.17)
- "explain what a quenched galaxy is" (3.13)
- "emphasize the significance of the 1990 discovery to Plot’s reputation" (3.23)

Key: effect plus an explicit link to its cause: "named Mansourasaurus to recognize the team", "named for the constellation Perseus, the location of the meteor shower’s radiant", "created to establish a common government", "Given that ... , historians believe", "toxic ... because it is three to eight times saltier", "While still highly effective, ... requires far less", "may misidentify ..., making such algorithms less reliable", "collected writings ... and created paper versions", "a quenched galaxy is one that no longer forms stars", "Evidence that ... suggests that Plot may not have been the first".

Distractors (30): OG 21 (other true facts; often one option holds both halves with no link, e.g. 1.6 C names the discoverers but never says the name honors them; 2.15 C gives the styles and the firm; serves "describe the discovery" or "describe the buildings"), PART 4 (the claim without its reason: 2.15 B and D; the problem without the solution: 2.3 C; what was preserved rather than how: 3.17 C), FALSE 4 (2.3 B says the new catalyst needs the usual amount; 3.17 A adds China as a knowledge source; 3.23 A and D misstate who challenged what and overclaim "disproved"), VAGUE 1 (2.13 B "may be linked to a single spot").

### 7.8 Example, or explanation plus example (5: 1 / 3 / 1)

Phrasings:
- "define the term “Lazarus species” and provide an example of one" (1.19, "these goals")
- "provide an explanation and an example of Aeolian landforms" (2.16)
- "provide an explanation and an example of Oliveros’s Sonic Meditations" (3.4)
- "provide an example of an air mass" (2.25)
- "provide an example of a fruit that contains vitamin C" (2.42)

Key: general statement plus a named instance joined by "such as", "for instance", "include", "One type of ... is". Bare-example keys name the instance with its category (cA, continental arctic; pineapple).

Distractors (15): PART 6 (definition only, e.g. 3.4 B; example only, e.g. 1.19 B and 3.4 C; or an example of the wrong level, 2.16 A gives a process instead of a landform), OG 6 (general facts about the category; serves "define air masses" or "explain why humans need vitamin C from food"), VAGUE 1 (2.42 A "such as fruits"), REL 1 (3.4 D contrasts the two meditations), FALSE 1 (2.16 C calls the three wind processes "examples" of landforms).

### 7.9 Research study (6: 0 / 3 / 3)

Phrasings:
- "present the study and its findings" (2.2)
- "present the study’s results" (2.5)
- "present LIGO’s aim and methodology" (2.21)
- "present the primary aim of the research study" (3.1)
- "summarize the study’s findings" (3.10)
- "present the findings of the study" (3.21)

Key: restates exactly the requested slot of the study arc, with attribution when "study" is in the goal ("A study led by ... identified a total of 74 ... species"; "A physics study designed to detect and analyze gravitational waves, LIGO uses ..."). When findings are plural the key merges them ("not only helped remove phosphorus ... but also yielded market-quality blooms").

Distractors (18): OG 9 (adjacent slots; aim offered for results, 2.5 C; method offered for aim, 3.1 B; results offered for aim, 3.1 C; method offered for findings, 3.10 A), PART 6 (finding without the study, 2.2 B and C; study without the finding, 2.2 D; method without aim, 2.21 C; one finding of two, 3.21 A and 3.10 B), FALSE 3 (3.1 D presents the background premise as the team's analysis; 3.21 B and D mis-attach the numbers).

### 7.10 Generalization (5: 0 / 2 / 3)

Phrasings:
- "make a generalization about ultramarathons" (2.12)
- "make and support a generalization about the effect of redesigning a city flag" (2.22)
- "make and support a generalization about nissologists’ definition of an island" (3.11, "these goals")
- "make and support a generalization about the Alta conflict" (3.12)
- "make and support a generalization about exoplanets" (3.20)

Key: a class-level claim, usually hedged with "can", followed by the case as support: "..., as the example of Sweden shows", "..., as was the case when Pocatello ...", "..., a fact that can be seen in the cases of ...", "had a lasting impact, resulting in ...". Without "support" the key is the claim alone, abstracted from two data points ("range widely in length, from a few dozen miles to a few hundred").

Distractors (15): PART 9 (the support without the claim: all three wrong options of 2.22; 3.11 C, 3.12 C; the claim without the support: 3.12 B, 3.11 B; examples without generalizing: 2.12 A), OG 5 (a contrast of two cases: 2.12 B and D, 3.20 B; a generalization about the wrong class, stars instead of exoplanets: 3.20 C; an event description: 3.12 A), FALSE 1 (3.20 A over-generalizes from two names).

### 7.11 Overview or summary (4: 1 / 0 / 3)

Phrasings:
- "provide an overview of the Haber-Bosch process" (1.21)
- "provide an overview of the matsutake commodity chain" (3.8)
- "summarize the kelp highway hypothesis" (3.9)
- "provide a historical overview of the two theories" (3.22)

Key: one sentence that spans the arc: inputs, conditions and output (1.21 B); both ends of the chain plus its time frame (3.8 C); claim, route and resources (3.9 C); both theories plus how the debate ended (3.22 A).

Distractors (12): PART 7 (one component: inputs only, one end of the chain, one theory; serves "describe X's inputs"), OG 3 (definition of a commodity chain, origins quote, glacier submersion), VAGUE 1 (3.9 B names the hypothesis without its content), FALSE 1 (3.22 B says all three scholars held both views).

### 7.12 Unfamiliar or new audience (7: 1 / 6 / 0)

Phrasings:
- "introduce Kahlo to an audience unfamiliar with the artist" (1.12)
- "introduce the scientist and her field of study to a new audience" (2.8)
- "introduce the Slow Food movement to a new audience" (2.26)
- "describe the rocking chair to an audience unfamiliar with Sam Maloof" (2.34)
- "present the significance of the Hart-Celler Act to an audience unfamiliar with the history of US immigration" (2.35)
- "describe Unwoven Light to an audience unfamiliar with Soo Sunny Park" (2.36)
- "present historical analysis to an audience unfamiliar with the concept" (2.43)

Key: an identifying appositive or definition (nationality, profession, category) plus the target content: "Mexican painter Frida Kahlo"; "Marine biologist Camille Jazmin Gaynus studies coral reefs, vital underwater ecosystems ..."; "American woodworker Sam Maloof"; "Korean American artist Soo Sunny Park"; "An approach to art criticism, historical analysis considers ..."; "the national-origins quota system, which favored immigrants from northern Europe".

Distractors (21): OG 10 (a single painting or work detail when the person must be introduced, 1.12 A to C; founding dates, 2.26 B; a grant, 2.34 C; the other concept, texture analysis, 2.43 A and B), AUD 6 (the right detail with no orienting context: 2.8 D treats Gaynus as known; 2.34 D and 2.36 A and C use the artist's name without saying who they are; 2.35 C mentions "the quota system in place" without saying what it did; 2.43 D gives a historical analysis of one painting without saying what historical analysis is), PART 4 (field without scientist, 2.8 C; one goal of the movement, 2.26 C and D; the old quota rule without its significance, 2.35 B), FALSE 1 (2.35 A adds a timing claim the notes do not make).

### 7.13 Already familiar audience (5: 0 / 3 / 2)

Phrasings:
- "present the study to an audience already familiar with environmental DNA" (2.1)
- "describe Adnan’s December from My Window to an audience already familiar with leporellos" (2.18)
- "describe where Fung is in the photograph to an audience already familiar with Kang and Fung" (2.28)
- "present the study’s findings to an audience already familiar with thermal inversions" (3.7)
- "introduce Cathryn Halverson’s book to an audience already familiar with the Atlantic Monthly" (3.16)

Key: uses the known term bare and spends its words on the new content ("analyzed eDNA in water samples ... for evidence of invasive constrictor snakes"; "When expanded, Adnan’s 1993 leporello ... reveals a panoramic landscape painted in ink and watercolor").

Distractors (15): AUD 9 (re-explain what the audience knows: eDNA defined twice in 2.1; leporellos explained in all three wrong options of 2.18; Kang re-introduced, 2.28 A; thermal inversion defined, 3.7 D; the magazine described, 3.16 B and C), PART 3 (mechanism without finding, 3.7 A; the paintings' place instead of Fung's, 2.28 C; one author, 3.16 D), OG 3. Note that 2.1 D is otherwise complete and fails only by redefining eDNA: the cleanest test of the audience rule.

### 7.14 Quotation (3: 0 / 2 / 1)

Phrasings:
- "explain the goal of Brook Farm using a quotation from George Ripley" (2.9)
- "provide a quotation from Acquah that explains why she used pointillism in “Exquisite.”" (2.29)
- "use a quotation to emphasize a potential problem with the wood-wide web theory" (3.6)

Key: quotes the words that carry the goal (the goal clause, "illusion of movement", "disconnected from evidence") and ties them to the named entity and source.

Distractors (9): NOQ 7 (paraphrase with no quotation: 2.9 B and C, 2.29 B, 3.6 D; or a quotation doing another job: 3.6 A supports the theory, 3.6 B shows popularity, 2.29 D quotes her view of Ghanaian women), PART 2 (2.9 A quotes only part of the goal and drops Brook Farm; 2.29 C quotes the technique but not its effect, so not "why"). 2.29 D also misquotes "heroines" as "heroes" (confirmed in the image).

### 7.15 Narrative opening (1: hard)

Phrasing: "begin a narrative about Wong’s award-nominated web series" (3.5).

Key: the chronological start in narrative register: "In 2012, director and visual effects artist Freddie Wong launched a new action-comedy web series: Video Game High School." Distractors (3, all OG): reception plus nomination (B; serves "summarize the reception"), a jump to the outcome with "would go on to" (C; serves "end the narrative"), premiere and later nomination in one breath (D; serves "summarize the series' history").

## 8. Generation blueprint

### 8.1 Shared model (all subtypes)

Represent the notes as structured facts, not prose:

- `Fact(id, entity, role, attribute, value, text)` where role is one of identity, background, definition, aim, method, finding, interpretation, date, location, quantity, quote, example, outcome.
- `Goal(type, targets, relation, audience, needs_quote)`: `targets` is the set of fact ids the key must use; `relation` is one of none, both, contrast, order, comparative, cause, example_of, generalize; `audience` is none, new or familiar.
- The key is a realization of exactly `targets` under `relation`. Each distractor is a realization of a different fact set or relation, tagged with its archetype.

This makes correctness checkable by tags, so the language model (or author) only writes surface sentences. It mirrors `satbank/item.py`'s idea of a key plus named misconceptions; here the "misconceptions" are the archetypes in section 5.

**Notes rules (from the bank):** intro line verbatim; 4 to 6 bullets (5 is the default; 76% of the bank); 10 to 18 words each (easy target about 12, hard about 15); one plain declarative sentence each; allow pronoun-led follow-ups ("It ...", "She ...") for about one bullet in five; every technical term defined inside the notes; at least one bullet that no option needs is optional but common, and one or two bullets must exist only to feed OG distractors.

**Goal sentence:** "The student wants to [verb] [object][ to an audience ...]." followed by the fixed question. Use the verbs in the bank's proportions (emphasize about 30%, then describe, present, explain, provide, specify).

### 8.2 Comparison generator: SIM, DIFF, RANK (build first; 27% of the bank)

Slots: category C; entities X, Y (optionally Z for "which of three"); shared attribute s (for SIM); contrast attribute a with values aX, aY (for DIFF); quantity or date q with values (for RANK); one background fact per entity.

Notes: framing bullet ("X and Y are two kinds of C" or a definition), then parallel bullets per entity in identical syntax.

Key: SIM "Both X and Y [s]." or "Like X, Y [s]."; DIFF "X [aX], whereas Y [aY]." (rotate while, whereas, unlike, although-concession, comparative adjective); RANK "X [verb] [more/earlier/higher] than Y" or "After X ..., Y ...", optionally without the raw numbers.

Distractors, programmatic:
- REL: the same entities with the opposite frame (for SIM, a whereas-sentence on the contrast attribute; for DIFF, a both-sentence on the shared attribute). Requires the notes to carry one shared and one differing attribute; build both in every pair.
- PART: one entity's attribute only.
- VAGUE: "X and Y [differ / are similar] in some ways" style, from a small phrase bank ("are quite different", "don’t do so in exactly the same way").
- RANK only: FALSE by reversing order or comparative; LIST by giving both values with "respectively" or "and" and no comparative; wrong-dimension by comparing the other quantity (end dates instead of start dates).
- OG: the framing bullet or a background fact.

Programmatic share: notes skeleton, goal, key frame and all distractor frames can be generated from a fact table; a language model only smooths wording. Checks: the key mentions every entity; the key contains a marker from the allowed set for its relation and no marker from the opposite set; each REL option contains an opposite marker; each PART option mentions exactly one entity; RANK direction recomputed from the numbers; no option except the key satisfies (entities complete AND relation correct).

Risks: a "both" option that also happens to be true for the similarity goal (two shared traits in the notes): allow exactly one shared trait. The 3.3 C pattern (a contrast of outcomes when the notes frame those outcomes as the shared trait) is ambiguous for students; avoid it.

### 8.3 Profile generator: SPEC, EMPH, DESC, AUD_NEW, AUD_FAM, EXAMPLE (38 items, 41% of the bank)

Slots: person or object name; identity appositive (nationality plus profession or category); known-for fact; titled work with year; two physical features; one quantity or superlative; one definition of a term the work belongs to (leporello, Lazarus species).

Goal derivation from one note set (several items per note set are possible):
- SPEC: target = the bullet answering a wh-question; key near-verbatim with one appositive.
- EMPH: target = the quantity or superlative bullet; key adds an emphatic frame ("a total of", "only", "not only ... but also").
- DESC: target = the two feature bullets; key merges them.
- AUD_NEW: target = identity + feature; key leads with the identity appositive. AUD distractor = the feature without identity.
- AUD_FAM: target = feature; key uses the defined term bare. AUD distractors = the feature plus the definition of the familiar term (up to all three distractors, as in 2.18).
- EXAMPLE: target = definition + instance; PART distractors = each half alone.

Distractors: OG from every unused bullet (this is the main source; 48% of the bank), VAGUE by naming the attribute without content ("has a distinctive style"), OPP by foregrounding a fact that softens the requested quality (the mild summer for "how harsh").

Programmatic share: high once the fact table exists; the language model writes the profile facts (or an author supplies real, checked facts). Checks: OG options must be true and must not contain the target value; SPEC key must contain the target value; AUD_FAM key must not contain the definition text; AUD_NEW key must contain the identity appositive; at most one option contains all target facts.

Risks: real people and works. Every fact must be verified or the person must be fictional; misattributed facts about real artists are the biggest reputational risk in this family. Prefer invented researchers and artists with plausible names from many cultures, or a curated set of checked facts.

### 8.4 Study generator: STUDY, study-based EXPL and AUD_FAM (about 10%)

Slots: background or definition; researcher(s) with field and institution; aim ("wanted to better understand", "sought to", "designed a study to find out"); method (materials, models, place); finding 1 with a number; finding 2 or interpretation.

Key: the requested slot(s) with attribution. Distractors by slot swap (aim for findings, method for aim), PART (study without finding, finding without study, one of two findings), and in hard items FALSE by number misattachment (move a percentage from one finding to the other's measure, drop "more than the control", drop "per square meter").

Checks: every option tagged with roles; key roles equal goal roles exactly; FALSE options differ from a true option by one swapped value and are verified false against the fact table; findings options never introduce a number not in the notes.

Risks: invented science that reads as real. Keep claims plausible and modest, attribute everything to "researchers" or named fictional teams, and avoid medical advice.

### 8.5 Abstraction generator: GEN, OVERVIEW, EXPL (cause, significance), NARR (about 20%)

Slots: two or three cases with a common pattern (for GEN); an ordered process or chain (for OVERVIEW); cause and effect bullets (for EXPL); a dated sequence (for NARR).

Key: needs a language model or author: GEN "[Class] can [pattern], as [case] shows"; OVERVIEW one sentence that touches every stage; EXPL "[effect] because / to / making [cause]"; NARR the first event in narrative register.

Distractors: support-only and claim-only PART (GEN), single-stage PART (OVERVIEW), both-halves-no-link OG (EXPL), wrong-class generalization, over-generalization FALSE ("all", or a rule drawn from names), jump-to-outcome OG (NARR).

Checks: GEN key contains a hedge (can, may, often) and a support connector (as ... shows, as was the case, a fact that can be seen); OVERVIEW key covers at least one fact from each stage; EXPL key contains a causal connector; no distractor contains both the claim and its support. A separate language-model judge should answer the item cold and must pick the key, and must give a one-line failure reason for each distractor.

Risks: the generalization drifting beyond what the cases support; a "claim plus support" distractor accidentally becoming a second key.

### 8.6 Quotation generator (3%)

Slots: one or two quotations in the notes, attributed; the goal names the job the quote must do (explain a goal, explain why, show a problem).

Key: quote the span that carries the job verbatim and tie it to the entity. Distractors: paraphrase without quotes, a second quote that does another job (praise instead of criticism), a truncated quote that loses the link.

Checks: every quoted span in an option appears verbatim in the notes (except a deliberate misquote, which should not be used: the bank's one misquote, 2.29 D, is incidental); the key's quote contains the goal keyword or its synonym list.

### 8.7 Automatic checks for every item

1. Notes: intro line exact; 4 to 6 bullets; each bullet one sentence, 6 to 25 words.
2. Goal sentence matches a template in section 7; question sentence fixed.
3. All content words in every option appear in the notes or goal, apart from a whitelist of relation words and light paraphrase (flag anything else for review; FALSE distractors excepted).
4. Exactly one option satisfies the goal predicate computed from tags.
5. Every non-FALSE distractor is true against the fact table.
6. Length: key within 0.75 to 1.4 times the distractor mean; across a batch the key is longest in no more than about a third of items and shortest in at least one in seven, matching the bank (28 and 15 of 92).
7. Letter balance across a batch (bank: A 30%, B 20%, C 23%, D 27%).
8. No two options share the same fact set and relation.
9. Typography: curly quotes and apostrophes; the house rule bans em dashes in UI text, so write appositives with commas or parentheses even though the official items use em dashes (2.1 D, 2.10, 2.23, 2.40 D).

### 8.8 Recommended build

- **Templates:** 6 generators (comparison, profile, study, abstraction, quotation, narrative) covering the 15 goal types, with about 30 distinct goal phrasings (the bank's 92 goal sentences are all distinct but collapse to roughly that many frames).
- **Items per tier for a first release:** 30 easy, 60 medium, 30 hard (the bank's 24 / 50 / 26% split).
- **Mix per tier** (follow the bank): easy mostly SPEC, EMPH, DESC and SIM/DIFF with parallel pairs; medium adds audience items (most of them), quotation and two-part goals; hard concentrates GEN, STUDY, OVERVIEW and EXPL and is the only tier where FALSE distractors are common (about one per item).
- **Build order:** (1) comparison generator, most programmatic and 27% of the bank; (2) profile generator for SPEC, EMPH, DESC and both audience types, which reuses one note set for several goals; (3) study generator; (4) abstraction generator with a model judge; (5) quotation and narrative last (4 items in the bank).
