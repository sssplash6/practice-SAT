# Generating original Reading and Writing items: brief

Goal: for one skill (or part of one), write ONE original item for every (template, tier) cell where the official bank has at least one item of that template at that tier. Cells with no official item at that tier are skipped. Quality bar: an SAT reviewer should not be able to tell the item from an official one, except that it is new.

Read first: `spec/rw/README.md`, your skill's report `spec/rw/<slug>.md` (all of it, sections 2, 3, 5, 6, 7 and 8 in detail) and the official items in `material/rw/transcripts/<slug>.json`. Do not commit anything to git. Work files go in your own folder `$SCRATCH/gen_<slug>_<part>/` (the scratchpad is shared with other agents). Never use the em dash in your notes, explanations or replies; it is allowed only where an item's own text needs it (CB style uses closed em dashes inside passages and options).

## Step 1: the cell plan

1. Take the template list from section 8 of the report ("Recommended build" or equivalent). Use those templates and codes; if the report gives template families without codes, make short stable codes (e.g. `S1_comma_conj`).
2. Assign every official item of your scope to exactly one template (write the mapping to your work folder as JSON). A template's tiers = the tiers of its official items.
3. Cells = (template, tier) pairs with at least one official item. Skip the rest. Record skipped pairs too.

## Step 2: write one item per cell

Look at the official items of that cell (the "models") before writing. Match them; do not copy them.

**Fidelity**
- Stem: use the exact official stem wording for that subtype (stems are generic; reuse them verbatim, including variants such as "Based on the texts, ..." or "The student wants to ...").
- Length: SAT passages are long for their type. Target the upper half of the official range for the cell: at least the official median word count for that template and tier, ideally between the median and the 75th percentile, never above the skill's official maximum. Compute these numbers with Python from the transcripts; report actual word counts.
- Build the passage with the same sequence of moves, sentence length and vocabulary level as the models in that cell (section 3 and 6 of the report give the measures per tier).
- Options: same shape as the models (length, parallel syntax, shared opening words, phrase vs sentence). Each distractor follows one named recipe from section 5/7 of the report, in roughly the official proportions for that tier. The tier must come from the same difficulty drivers the report measured (reasoning steps, clue distance, distractor closeness, word rarity), not from passage length alone.
- College Board house style: curly quotes and apostrophes, closed em dashes, en dashes in number ranges, `______` for the blank, `<u>...</u>` for underlined text, `\n\n` between paragraphs, `\n` between poem lines, `Text 1\n\n...\n\nText 2\n\n...` for paired texts, notes as an intro line then `• ` lines. Literary source line exactly in the CB format: "The following text is (adapted) from <Author>’s <year> <genre> <Title>." plus an optional context sentence.

**Accuracy**
- Exactly one defensible answer. The key is fully justified by the text (or table/graph); every distractor is wrong for a specific reason a teacher could point to in the text. Check the report's "no second correct answer" rules for your skill (e.g. no two punctuation marks that both work; no distractor sharing the key's relation).
- Conventions items: every option must be judged by standard written English as the CB tests it (see the report's rule inventory). Only one option may be acceptable.
- Data items: all numbers internally consistent; verify every data statement with Python against the table or figure data. Graphs: give the full data in `figure.description` (and `figure.data` as a list of series/points) so the image can be drawn later.

**Legitimacy**
- Informational passages describe real subjects truthfully. Every named person, institution, study, place, date, number and finding must be real and correctly described. Verify each with web search (load the tools with ToolSearch query `select:WebSearch,WebFetch`) and record the URLs in `sources`. If a detail cannot be verified, remove or generalise it ("a team of researchers") rather than invent it. Simplify, never fabricate.
- "Finding, if true" and similar hypothetical items may state hypothetical results, as the official ones do, but the research context (who, what, why) must still be real.
- Quantitative datasets: prefer real published data (cite it). If you must use illustrative numbers, keep them plausible for the real phenomenon, say so in `notes`, and never attach them to a real named study.
- Literary excerpts: only real public-domain text (published before 1929). Fetch the text from a public-domain source (Project Gutenberg, Wikisource, Poetry Foundation's PD pages, etc.) and copy it exactly; CB-style adaptation only (bracketed glosses like [visits], trimming at sentence or line boundaries). Record the URL. Author, year and genre in the source line must be correct.
- Paired texts: if either text attributes a view to a real scholar or group, that view must be theirs (verify) or the text must be unattributed ("Some researchers argue ...").

**Originality**
- No official item's topic, named people, works or sentences. Before finalising, check your passage against every official passage in the skill (search for your key nouns and names; no shared 6-word run of content words). Literary excerpts must come from works not used in any official item of ANY skill (grep all transcripts for the author and title).
- Within your own items: no topic repeats; spread subject areas the way section 3 of the report measured (science, social science, humanities, literature, history).

**What gives an imitation away** (blind test, 2026-10-12: judges told the first batch from official items almost perfectly, AUC 0.9 to 1.0 in every skill, even on official items they did not recognise)
- *Topic fame.* The strongest tell in every skill. Official informational items describe a specific, usually recent (about 2005 to 2021) piece of work by named, little-known researchers, artists, writers or institutions (a named researcher, team, artist or institution; framings vary, and "X and colleagues" opens only about 1 official passage in 10), often from underrepresented groups and fields. Textbook or viral subjects (Mendel, John Snow, the marshmallow test, the Rosetta Stone, the Great Wall seen from space, Pluto's demotion, Fermat) read as imitations. Choose the subject the way the official writers do: a real, findable paper, exhibition, book or project that a well-read adult would not already know. Keep data and dates within the official range (years in official passages run to 2022, with only a handful later).
- *Literary choices.* Official excerpts come from less-anthologised public-domain works (often with a translator or context line) and their distractors are plausible misreadings. Avoid the most famous classics, and never use a silly distractor.
- *Cloned frames.* Matching a model's moves is right; copying its sentence skeleton, signal phrase ("Barring the possibility...", "Fittingly", "; ______ though,"), goal wording or distractor wording is a tell. Vary the architecture across items, as different official items of one template do.
- *Encyclopedia texture.* A hook opener ("Despite their name...", "Strikingly"), a textbook summary tone, trivia packed in (exact figures, glosses, institutions the question never uses), a colon followed by a tidy list of evidence that spells out the key, a "Thus" conclusion set up to be knocked down, clauses inserted only to lengthen the gap the item tests. Official passages are compressed and evaluative, and every detail does work.
- *Too-tidy options.* Mirror-pair distractors (confirms / challenges), three options sharing a long identical prefix, distractors that flatly contradict the text or use absolutes ("in any way", "ever", "no effect of any kind"), a main-purpose key that lists the passage's parts in order, the same distractor recipe worded the same way across items, the same stock lead-in in several items (", suggesting that", "The researchers therefore concluded that"). Official distractors are often natural, even slightly informal, and wrong for subtler reasons; hard-tier options are long and nuanced.
- *Plainer register.* Official passages use longer words and more domain terms at every tier (`tools/check_rw.py` measures this per tier); reach it through the subject's own vocabulary, not thesaurus swaps.
- *Rule coverage.* Test only points the official bank tests (the report's rule inventory), and use note formats the bank uses (no "Step 1:" labels, no bullet that exists only to set up the key).

**Answer letters and tells**
- Spread keys evenly over A to D across your items (decide the letter before writing the options). The key must not be the longest option more often than the official rate the report measured; match the report's figures on hedging and word overlap. Avoid the official tells the report lists (e.g. "By noting ..." always being the key).

## Output

Write `satbank/rw/<slug>.json` (or `satbank/rw/<slug>__<part>.json` if your brief names a part). Save after every few items so nothing is lost. Format:

```json
{
  "skill": "Boundaries",
  "slug": "boundaries",
  "part": null,
  "domain": "Standard English Conventions",
  "plan": {"templates": [{"code": "...", "name": "...", "official_tiers": {"easy": ["1.4", "1.9"], "medium": [], "hard": ["3.2"]}}],
           "skipped": [["<code>", "medium"]]},
  "items": [
    {
      "id": "boundaries.S1_comma_conj.hard",
      "template": "S1_comma_conj",
      "subtype": "Joining two independent clauses",
      "tier": "hard",
      "passage": "...",
      "stem": "...",
      "options": ["...", "...", "...", "..."],
      "answer_letter": "C",
      "table": null,
      "figure": null,
      "explanation": "2 to 4 plain sentences a student would read: why the key is right, pointing to the text.",
      "distractors": {"A": {"recipe": "comma splice", "why_wrong": "..."}, "B": {...}, "D": {...}},
      "models": ["3.2", "3.17"],
      "word_count": 52,
      "sources": [{"what": "date of the bridge opening", "url": "https://..."}],
      "notes": ""
    }
  ]
}
```

## Step 3: self-review before you finish

For every item: read it as a student and answer it without looking at the key; confirm word count against the cell's official median; confirm every fact has a source; run the originality check; run the letter-balance and longest-option counts with Python. Fix anything that fails.

Finish with a reply under 15 lines: cells planned, written and skipped; word-count median of your items vs the official median; anything you could not verify and what you did about it.
