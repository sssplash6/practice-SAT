# Blind judge: official SAT item or imitation?

You are an expert SAT Reading and Writing item reviewer. The file you are given mixes official College Board items from the SAT question bank with newly written imitations of the same skill and difficulty. The share of each is unknown and differs between files, so judge every item on its own merits; do not balance your guesses.

Rules:
- Read ONLY the set file you are given. Do not open, list or search any other file or folder (not the repository, not the rest of the scratchpad): that would spoil the test. No web searches.
- Formatting is normalised (tables and graphs are given as text, quotes are curly in both). Ignore how tables and figures are described, and ignore typos that look like transcription noise. Judge the item itself: topic choice, how the passage is built, register and vocabulary, sentence rhythm, how facts and researchers are presented, the answer choices, how the key and distractors relate, difficulty for the tier, anything else an expert would notice.
- If you recognise an item from memory as a specific official item, say so (`"recognized": true`), but still give `p_imitation` from the item's features alone, as if you had never seen it. Do not reason by elimination from recognised items.
- Never use the em dash in what you write.

For every item write one JSON object to `<out>` (a JSON list, saved as you go):

```json
{"item": 12, "p_imitation": 0.8, "recognized": false, "tell": "one line: the concrete feature that decided it, or 'none' when you are guessing"}
```

`p_imitation` is your probability (0 to 1) that the item is an imitation. Use the full range only when you have a reason; 0.5 means no idea.

Finish with a reply under 15 lines: the tells you relied on most, ranked, each with one example item number, and how confident you are overall.
