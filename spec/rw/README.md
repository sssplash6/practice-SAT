# Reading and Writing bank: overview

846 official SAT Reading and Writing questions (10 skills x 3 tiers), transcribed and analysed so we can write original questions of the same kinds at the same quality, the way `satbank/` does for math. Nothing official ships in the product.

## Files

| What | Where |
|---|---|
| Source PDFs and question images (git-ignored) | `material/rw/*.pdf`, `material/rw/items/<skill>/<tier>/<n>.jpg` |
| Answer keys from the PDF text layer | `material/rw/keys/<skill>.json` (rebuild: `python3 tools/extract_material.py material/rw`) |
| Transcripts: passage, stem, 4 options, key, table/figure | `material/rw/transcripts/<skill>.json` |
| Per-skill analysis (8 sections each) | `spec/rw/<skill>.md` |
| Brief the analyses followed | `spec/rw/BRIEF.md` |
| Every R&W item in CB's bank (1,845) as text, with key, CB rationale, tier and score band | `material/rw/cb_api/<skill>.json` (rebuild: `/usr/bin/python3 tools/cb_rw_fetch.py`) |
| Band 7 vs band 6, per skill; the band-7 pilot brief and items | `spec/rw/band7/<skill>.md`, `spec/rw/band7/WRITE.md`, `spec/rw/band7/pilot/` |

Transcripts: all 846 items have 4 options and a key; 658 were checked against the image. Pipeline: tesseract OCR, cross-checked word by word against macOS Vision, then every disagreement, table, graph, underline, dash-sensitive item and broken layout checked against the image (`"verified": "image"`). Conventions: blank `______`, underline `<u>...</u>`, paragraphs `\n\n`, poem lines `\n`, cross-text `Text 1\n\n...\n\nText 2\n\n...`, notes as `• ` lines, curly quotes as printed.

## Score bands

CB's public label has three tiers, but every item also carries a 1 to 7 score band (`score_band_range_cd`): R&W easy is bands 1 to 3, medium 4 and 5, hard 6 and 7. "Super hard" means band 7 (305 of the 610 hard items). Transcripts and authored items now carry `band` / `cb_tier` and `model_bands`. The PDF tiers differ from CB's current tiers for about 16% of transcribed items; trust `band`.

## The bank at a glance

| Domain (share of the test) | Skill | E / M / H | Median passage words | Subtypes | Templates proposed | First batch |
|---|---|---|---|---|---|---|
| Information and Ideas (26%) | Central Ideas and Details | 19 / 27 / 21 | 87 | main idea, explicit detail, supported detail | 8 | 140 |
| | Inferences | 15 / 22 / 34 | 95 | one ("most logically completes"), 12 logical structures | 10 | 120 |
| | Command of Evidence | 45 / 43 / 48 | 76 | data completion, data description, "finding, if true", literary quotation, person quotation | 14 | 120 to 180 |
| Craft and Structure (28%) | Words in Context | 58 / 28 / 25 | 52 | blank completion, "most nearly mean" | 8 | 150 |
| | Text Structure and Purpose | 23 / 24 / 19 | 89 | main purpose, overall structure, function of underlined part | about 30 (small) | 120 |
| | Cross-Text Connections | 16 / 11 / 14 | 139 | respond, agree, difference, relationship | 14 | 120 |
| Expression of Ideas (20%) | Rhetorical Synthesis | 22 / 46 / 24 | 83 (notes) | 15 goal types in 6 families (comparison, profile, study, abstraction, quotation, narrative) | 6 generators, about 30 goal frames | 120 |
| | Transitions | 37 / 18 / 20 | 53 | 16 relation groups | 14 | 100 |
| Standard English Conventions (26%) | Boundaries | 32 / 28 / 35 | 45 | 19 rules in 6 families | 16 | 150 |
| | Form, Structure, and Sense | 40 / 24 / 28 | 43 | 6 rules | 19 | 184 |

## What holds across every skill

1. **Passage length does not make a question hard.** Median length is flat across tiers in every skill (for example Inferences about 95 words in all three tiers, Cross-Text about 137). Difficulty comes from: denser sentences and rarer words, more reasoning steps (Inferences 1.5 easy to 2.0 hard), distractors that reuse the right pieces with one wrong link, and rarer keys (Transitions: 70% of easy keys come from 13 common connectives, 10% of hard ones).
2. **Exactly one defensible answer, by construction.** Boundaries never offers two marks that would both work (period vs semicolon); Transitions never repeats the key's relation among the distractors (75 of 75) and avoids defensible pairs (contrast with concession). Every generator needs a judge for this, not just a key.
3. **The key has no surface tell.** It is not reliably the longest option, and it reuses passage words at about the same rate as the distractors (Inferences 0.42 vs 0.44, CID 32% vs 38%, WiC keys never repeat a passage word). Keys hedge more and never use absolutes. Generated items must keep this: check length rank, word overlap and hedging per item and per batch.
4. **Wrong answers come from a short, named list per skill** (unsupported claim, reversal, true but off-goal, wrong entity or variable, wrong relation, comma splice in disguise, ...). Each report names them with frequencies; generators should label every distractor with its recipe, which is also the explanation students see.
5. **The official set has tells we should not copy:** answer letters are skewed (Cross-Text D 39%, Boundaries D 38%, Text Structure medium has no C), "By noting ..." is always the Cross-Text key, "compare/contrast" options are never correct in Text Structure. Balance letters per tier and vary option openings.
6. **Literary passages are real excerpts with a source line** ("The following text is adapted from <author>'s <year> novel <title>."). Do not invent these: use real public-domain text (pre-1929) with an accurate attribution. Informational passages are original prose about real-sounding research, built from a fixed sequence of moves (context, claim, evidence, twist).

## How generation should work

One shared pipeline, with skill-specific slots:

1. **Plan**: pick subtype, tier, subject area and the logical "move plan" (the ordered sentence roles the report lists for that subtype).
2. **Passage**: a language model writes the passage to the plan, with tier targets (sentence length, word rarity). Literary items take a sourced public-domain excerpt instead.
3. **Options**: programmatic where the rule is mechanical (Boundaries and Form, Structure, and Sense punctuation and verb forms, Transitions option sets, Command of Evidence data statements); otherwise model-written, one per named distractor recipe.
4. **Judges**: automatic checks from section 8 of each report, then an independent solver that must pick the key and reject each distractor for its labelled reason. Reject the item on any disagreement.
5. **Batch checks**: letter balance, key length rank, overlap and hedging rates against the official figures.

## Build order (recommended)

1. **Standard English Conventions** (Boundaries, Form, Structure, and Sense). 26% of the test, and the options are fully programmatic once a sentence exists: each rule has a fixed set of three wrong forms. Correctness is rule-checkable. Start with clause joins and subject-verb agreement; dangling modifiers carry 43% of the hard Form, Structure, and Sense tier, so hard needs them.
2. **Transitions**: option sets are rule-built from the relation inventory; only the two-sentence passage needs writing. Start with contrast, cause and example (24 of 37 easy items).
   **Rhetorical Synthesis comparison goals** belong here too: 27% of that skill, almost every option is true to the notes and the item turns on fit to the goal, so a note set with two parallel items yields the key (both / whereas / than) and its distractors (one side only, opposite relation, vague "they differ") by program.
3. **Command of Evidence, quantitative**: dataset, claim and four data statements can all be generated and verified by code (a predicate engine over the table); only the framing prose needs a model.
4. **Words in Context**: upgrade the existing generator (below) rather than starting over.
5. **Inferences, Central Ideas and Details, Text Structure and Purpose, Cross-Text Connections, the rest of Rhetorical Synthesis**: model-written passages and options, held to quality by the judges. Inferences "principle plus case" and Text Structure "overall structure" are the most templatable starting points.

## Existing code this touches

`server/words.py` already serves Words in Context (`rw.wic.*`, 5,070 blank frames and 306 "nearly" frames) and Transitions (`rw.tr.*`). Against this bank, its WiC passages are too short (median 19 words vs 50), it ranks lookalike traps first (the official bank uses none), it has no phrase options (25 of 111 official items), and the "nearly" format renders broken: the passage keeps `____`, and the stem word is itself an option and the key. 48 "nearly" frames are servable. Details in `words_in_context.md` section 8a.

## Known gaps in the source

- **Inferences hard key is missing**: `Inferences 3~Key.pdf` has no Answer column; `keys/inferences.json` holds junk numbers for 3.1 to 3.34. The transcript carries answers solved by the analysis agent, marked unofficial in `notes`.
- CID 3.16 (`abcd0005`) and WiC 3.18 (`abcd0009`) have placeholder ids and a different layout; probably not official items. CoE 2.22, 3.4, 3.13 are not in the question bank index fetched 2026-09-26.
- CID 3.15 is filed under Central Ideas and Details but asks for the main purpose.
- CoE 2.30 asks about an underlined claim but nothing is underlined in the image. Boundaries 1.31 contains a factual slip in the official text (kept as printed).

## Authored bank (first batch)

306 original items in `satbank/rw/<skill>.json` (four skills split into `__a` / `__b` parts): one item per (template, tier) cell that has at least one official item at that tier; empty cells are skipped and listed in each file's `plan.skipped`.

- Written to `spec/rw/GENERATE.md`, then reviewed by a separate agent to `spec/rw/VERIFY.md`: blind solve, every fact checked against its source, literary excerpts checked word for word against the public-domain text. Each item records the outcome in `review` (207 pass, 99 fixed, 0 removed; blind solve agreed 306/306 after fixes).
- A bank-wide duplicate pass replaced 45 items whose subject repeated another item's (`replaced` field on those items); the replacements were reviewed the same way.
- Gate: `python3 tools/check_rw.py [slug]` checks shape, house style, blank count, length against the item's official models, 6-word overlap with any official passage, and sources, and prints letter balance and key-longest rates.

## In practice

`satbank/topics/rw.py` registers the bank as ten topics (`rw_<skill>`, one template per authored template code), so R&W practice sets run through the same drill as Math: Practice, Reading & Writing tab, a skill's Practise button or the mixed set. Items with a figure are held back until the runner draws graphs: 340 serve, the 300 first-batch items plus the 40 band-7 pilot items in `satbank/rw/<skill>__b7.json` (28 tagged `band` 7, 12 `band` 6; see `spec/rw/band7/PROXY.md`). An R&W miss opens one unnamed mistake on its type that clean answers anywhere in the skill pay down (`progress.miss_norm`); redo sets fall back to another type of the skill when a type has no fresh item. The passage is the item's `text`; `server/checks/rw_bank.py` is the end-to-end check. Tests, the daily challenge and the map stay Math only.

