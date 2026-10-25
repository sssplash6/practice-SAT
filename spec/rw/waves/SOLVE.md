# Blind solves for staged wave items (gate and safety)

You are a blind solver. The set file named in your prompt holds items with an opaque `qid`, a `passage` (a table
or figure, if any, is written into the passage as text), a `question` and four `options` (A to D). The keys are in a
separate file you must never open (`key.json` beside the set). Do not open any other file under `spec/rw/`,
`satbank/rw/` or `material/rw/` either: the items' sources, keys and explanations are there.

Solve every item on its own, from the passage, question and options only, as a careful student taking the SAT would.

## Gate solve (fast model)

Set: `<dir>/gate.json`. Write `<dir>/answers/<your run number>.json`:

    {"g000": {"answer": "B", "p": {"A": 0.05, "B": 0.80, "C": 0.10, "D": 0.05}}, ...}

`p` is your honest probability for each option (sums to about 1). Answer every qid. No explanations.

## Safety solve (independent judge)

Set: `<dir>/safety.json`. Write `<dir>/answers.json`:

    {"s00": {"answer": "D", "also_defensible": [], "unfair": ""}, ...}

- `answer`: the one option you would mark.
- `also_defensible`: any other option a strong student could defend as correct under College Board's standard (the
  text supports it, or the grammar allows it). Be strict: an option that is merely tempting is not defensible.
- `unfair`: a short note if the item is broken in a way that is not a second answer (the passage contradicts
  itself, the question cannot be answered from the text, a needed fact is missing), else "".

Answer every qid. Save the file as you go. No git commands. Never use the em dash in replies. Reply in 3 lines:
items solved, how many you flagged and why in a few words.
