# Verifying authored Reading and Writing items: brief

You are the independent reviewer for one generated file in `satbank/rw/`. You did not write these items. Your job is to make sure each one is correct, legitimate and faithful to the official bank before any student sees it. Do not commit anything. Work files go in your own folder `$SCRATCH/verify_<file stem>/`. Never use the em dash in notes or replies (it is allowed only inside item text, where CB style needs it).

Read first: `spec/rw/GENERATE.md` (the standard the author worked to), the skill report `spec/rw/<slug>.md` and, for comparison, the official models each item lists (`models`, ids in `material/rw/transcripts/<slug>.json`).

## For every item

1. **Blind solve.** Before reading `answer_letter`, `explanation` or `distractors`, write down your answer from the passage, stem, options, table and figure only, with a one-line reason. Do this for ALL items first (write the answers to your work folder), then compare with the keys.
   - If you disagree with the key, or you find a second defensible option, the item fails. Fix it (rewrite the option or the passage so exactly one answer is defensible) or, if it cannot be fixed cleanly, delete it.
2. **Facts.** Check every factual claim in the passage, notes, table and options that names a real person, place, institution, work, date, number or finding: open the item's `sources` (WebFetch) and confirm the claim is there; search (WebSearch) when a source is missing or does not support it. Load the tools with ToolSearch query `select:WebSearch,WebFetch`. Fix wrong facts or generalise them; add the source you used.
3. **Literary text.** For excerpts and quotations from works, fetch the public-domain source and confirm the text is copied exactly (CB-style bracketed glosses and trims allowed), and that author, year, genre and title in the source line are correct.
4. **Fidelity.** Compare with the listed models: same stem wording, comparable length (at least the models' median word count), same move sequence, options of the same shape, distractor recipes that exist in the report, and a difficulty that matches the tier for the reasons the report gives (not length alone). Fix drift.
5. **Conventions and style.** Grammar and punctuation in the passage must be impeccable except where the item tests it; CB house style (curly quotes, closed em dashes, en dash ranges, `______`, `<u>`).
6. **Explanations.** `explanation` and every `why_wrong` must be correct, specific and student-readable; fix them if your blind solve exposed a weaker justification.

## Recording

Edit the items in place with a small Python script (json load and dump, `indent=2, ensure_ascii=False`). On every item add:

```json
"review": {"blind_answer": "C", "agreed": true, "facts_checked": 5, "fixes": ["changed the year of X from 1911 to 1912 (source ...)"], "status": "pass"}
```

`status` is `pass` (no change needed), `fixed` (you changed it and it now passes) or `removed` (you deleted the item; keep a record in a top-level `removed` list with id and reason). Then run `python3 tools/check_rw.py <slug>` and fix anything it reports for your file.

Finish with a reply under 12 lines: items passed, fixed and removed; blind-solve agreement rate before fixes; the most serious problems found.
