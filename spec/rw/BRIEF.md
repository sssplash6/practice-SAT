# Reading and Writing bank: transcription and analysis brief

Source: 846 official SAT Reading and Writing questions (College Board question bank IDs), 10 skills x 3 difficulty tiers (easy/medium/hard), in `material/rw/`. Each question is one image `material/rw/items/<slug>/<tier>/<n>.jpg`. The answer key is `material/rw/keys/<slug>.json`. The OCR draft transcript is `material/rw/transcripts/<slug>.json`.

The goal is to learn the question types well enough to write ORIGINAL questions of the same kinds at the same quality, the way `satbank/` does for math. Nothing official is copied into the product.

## Part 1: finish the transcript (`material/rw/transcripts/<slug>.json`)

The draft is tesseract OCR, cross-checked against macOS Vision. Word-level disagreements were already fixed. View the image (Read tool on the jpg, several images per turn) and correct the item when ANY of these hold:
- `check` is non-empty (an unresolved disagreement between the two OCR engines; the image is the judge)
- `ocr_flags` mentions "options read as" or "wide gaps"
- `options` is not exactly 4 strings
- the `stem` is not the question sentence (the parser sometimes pulls the end of the passage into the stem or vice versa)
- the question needs a blank and `passage` has no `______` (or has more than one)
- the stem mentions an underlined portion, a table, a graph, a poem or notes
- (boundaries and form_structure_and_sense only) any option or the passage contains a dash or hyphen: hyphen `-`, en dash `–` and em dash `—` must be told apart.

Conventions:
- `passage`: paragraphs separated by `\n\n`. Poem lines separated by `\n`. Cross-text items: `Text 1\n\n...\n\nText 2\n\n...`. Notes items (rhetorical synthesis): the intro line, then each bullet on its own line starting `• `, joined with `\n`.
- The answer blank is exactly `______`. Underlined text: `<u>...</u>`. Keep curly quotes and apostrophes as printed (`’ “ ”`), keep em dashes `—`. Ignore italics.
- `table`: `{"title": str|null, "columns": [str], "rows": [[str]], "note": str|null}` with every cell as printed.
- `figure`: `{"kind": "bar graph|line graph|scatterplot|...", "title": str|null, "x_axis": str|null, "y_axis": str|null, "description": str}`. The description must carry every value a student needs (read values off the axes as precisely as the gridlines allow; say "about" when estimated).
- After fixing, set `"check": []` and `"verified": "image"` on that item. Leave other items untouched. Remove the top-level "OCR draft" note and replace it with "tesseract OCR cross-checked with Vision; flagged items verified against the image".
- Edit the JSON with a small Python script (json.load / json.dump with `indent=2, ensure_ascii=False`). Keep every other field.
- Do not fix the official wording, even where it looks odd: transcribe exactly.

## Part 2: analysis (`spec/rw/<slug>.md`)

Read EVERY item of the skill (from the corrected transcript, plus images where a table or figure matters). Compute numbers with Python rather than guessing. Write a thorough markdown report with these sections:

1. **Snapshot**: item counts per tier; answer-letter distribution; passage length in words (min/median/max per tier); stem wording variants with counts.
2. **Subtypes**: every distinct task the skill contains (e.g. textual vs quantitative evidence, main idea vs detail, purpose vs structure vs function-of-underlined). For each: definition, count per tier, what exactly the student must do, the precise question wording(s).
3. **Passages**: subject areas (natural science, social science, humanities/arts, history, literature) with counts; genres (informational paragraph, literary excerpt with an attribution line like "The following text is adapted from ...", poem, two short texts, research notes, table/graph); how the passage is built sentence by sentence (the typical "move" order, e.g. context -> researcher claim -> evidence -> twist); names, dates, places conventions; vocabulary level.
4. **The correct answer**: how it is justified by the text; how it is worded (paraphrase vs echo, length relative to distractors).
5. **Distractor recipes**: name each wrong-answer archetype (e.g. "true but irrelevant", "too broad", "reverses the relationship", "comma splice", "contrast word where continuation is needed"), with frequency and 1 to 2 short illustrative examples written in YOUR OWN words or quoted under 15 words.
6. **Difficulty**: what concretely separates easy, medium and hard (passage density, vocabulary, closeness of distractors, inference steps, rule subtlety). Give measurable signals where you can.
7. **Skill-specific inventory** (as relevant): the full list of grammar rules tested with counts (conventions skills); every transition word or phrase used in options, grouped by logical relation, with how often each is correct (transitions); the target words and their option sets characterised by register/frequency (words in context); data-claim structures (evidence); goal phrasing types (synthesis), etc.
8. **Generation blueprint**: how to produce NEW original items of this skill at the same quality. Per subtype: the slots a template needs, the answer logic, how each distractor type is constructed, which parts can be fully programmatic (e.g. punctuation variants of a fixed sentence) and which need an author or language model to write passage text, automatic checks that would catch a broken item, and realistic quality risks. End with a recommended number of distinct templates and items per tier, and which subtypes to build first.

Keep the report factual and specific to this bank; avoid generic SAT advice. Write in plain English. Never use the em dash character in the report (use a colon, comma or parentheses); the em dash is allowed only inside quoted passage text and in the transcript JSON. Do not commit anything to git.

Finish with a short reply (under 15 lines): how many items you verified against images and fixed, anything you could not resolve, and the 3 most important findings.
