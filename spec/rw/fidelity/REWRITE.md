# Fidelity rewrite: make the authored items indistinguishable from official ones

The authored items in `satbank/rw/` are correct and reviewed, but measurably plainer than the official items, and blind judges could tell many of them apart. Your job: rewrite the items of ONE file so that an expert cannot tell them from official items, without breaking what already works (one defensible answer, true and sourced facts, exact literary text). Do not commit. Work files go in `$SCRATCH/rewrite2_<file stem>_<part>/` (part as given in your prompt; ignore older `rewrite_*` folders, they are from a stopped attempt). Never use the em dash outside item text.

Read first: `spec/rw/GENERATE.md` (the standard still applies in full), your skill report `spec/rw/<slug>.md`, and for every item the official models it lists (`material/rw/transcripts/<slug>.json`). Before rewriting an item, read 4 or 5 official passages of the same template and tier side by side with it.

## Picking up a stopped attempt

Some slices were started and stopped. Items in your list that already have a `rewrite` field are done: skip them. If your work folder already exists, it holds research and drafts from the stopped attempt on the same items: reuse what is sound. Lines in `claims.txt` that name your own item ids are yours to keep or replace.

## What to fix

1. **Judge tells.** `spec/rw/fidelity/round1/tells.json` maps each authored id to the blind judge's probability that it is an imitation (`p`) and the feature that gave it away (`tell`). Fix every tell for your items, starting with the highest `p`. The bank-wide tells the judges reported are listed at the end of this brief; check every item against all of them, not only its own tell.
2. **Register.** Official passages are denser: longer words, more precise domain terms, academic verbs and nominalisations ("the researchers attributed the decline to...", "a phenomenon known as..."), compact noun phrases. `python3 tools/check_rw.py <slug>` prints, per tier, chars per word and the share of 9+ letter words (names and sentence starts left out) for ours vs official, plus words per sentence. Your items, taken on their own, must reach at least the official value for their tier on both density measures, with words per sentence within 15%. Aim close to the official value (up to about 10% above it): prose far denser than official is as much a tell as plain prose. Raise density the way the official writers do, through the subject's own vocabulary and tighter syntax, never by swapping in thesaurus words or padding. If a sentence reads as if it were made difficult on purpose, it is a tell too.
   Measure your own items with:
   `python3 -c "import json,statistics as s,sys;sys.path.insert(0,'tools');from check_rw import register;d=json.load(open('satbank/rw/<file>.json'));[print(t,[round(s.mean(register(i['passage'])[k] for i in d['items'] if i['tier']==t),3) for k in range(3)]) for t in ('easy','medium','hard') if any(i['tier']==t for i in d['items'])]"`
3. **Key length.** The checker also compares how often the key is the longest option with the official rate for the skill (within 10 points). Where your file is below it, let the key be the longest option in more items, as the official items do, without making it obviously the fullest or most careful choice.
4. **Topic and framing.** Where a tell is about the subject (a textbook-famous study, a too-familiar fact, a history-lesson framing where official items describe a specific, recent piece of research), replace the subject with one of the kind the official bank uses. A new subject means the full GENERATE.md process: web-verified facts with URLs in `sources`, not in any official item and not used by any other item in `satbank/rw/*.json` (grep before choosing).

## What must not break

- **Literary excerpts stay exact** public-domain text. You may change their options and key, not the excerpt.
- **Exactly one defensible answer.** After every change, solve the item again as a student; redo the distractor recipes, `explanation`, every `why_wrong` and `word_count`.
- **Conventions items** (Boundaries; Form, Structure, and Sense): the tested rule and all four options must still be judged correctly; only one option acceptable.
- **Facts**: every new or changed factual claim is web-verified and in `sources`. If web search stops working, verify through journal pages, DOIs (Europe PMC, Crossref) and official data sites with WebFetch or curl; if a fact still cannot be verified, generalise it and say so in `notes`. Never add an unsourced specific to sound denser.
- Keep `id`, `template`, `subtype`, `tier`, `models` and the official stem wording. Keep letters balanced within the file (you may re-letter).
- Length stays at or above the models' median (the checker enforces it).

## Recording

Edit in place with a small Python script (json load and dump, `indent=2, ensure_ascii=False`, under the lock below); re-read the file first. On every item you change, add `"rewrite": "<one line: what changed>"` and set `"review": null` so the reviewer re-checks it. Leave untouched items as they are. Run `python3 tools/check_rw.py <slug>` and fix what it reports for your items (the per-tier lines merge all parts of a split skill; make your own items pass on their own).

Reply in under 10 lines: items changed, subjects replaced, your items' density per tier vs official, key-longest count, anything you could not verify.

## Bank-wide tells from the blind judges

They are now part of the standard: read "What gives an imitation away" in `spec/rw/GENERATE.md` and check every item against each point. Baseline: judges flagged 251 of 306 items at p 0.7 or above; only 21 passed as official. Expect most informational items to need a new subject (topic fame was the top tell in every skill).

## Parallel work on one file

Other agents may edit other items of the same file, and other agents are choosing new subjects at the same time. Before choosing a subject, append `<subject in a few words> | <item id>` to `spec/rw/fidelity/claims.txt` (with `>>`), re-read it, and pick another if someone claimed it. Write the file only under a lock and only your ids:

```python
import fcntl, json
with open(path + ".lock", "w") as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    d = json.load(open(path))
    # change only your items in d["items"]
    json.dump(d, open(path, "w"), indent=2, ensure_ascii=False)
```
