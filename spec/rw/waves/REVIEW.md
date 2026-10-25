# Wave review brief

You are the independent reviewer for one staged wave file (`spec/rw/waves/<wave>/<skill>_<batch>.json`, named in your prompt). You did not write it. Only you edit this file while you work; other agents work on other files.

Follow `spec/rw/VERIFY.md` with these changes:

1. **Blind solve first.** Solve every item from passage, stem, options and table only, before reading any key, explanation or distractor; write your answers to your scratch folder. Then compare. A disagreement, or any second defensible option, fails the item: fix it (one defensible answer, by construction) or remove it.
2. **Facts (user decision, 2026-10-16; `spec/rw/waves/WAVE.md`).** Boundaries, Form, Structure, and Sense, Transitions and Rhetorical Synthesis: no fact-checking. Check only that nothing attributes a made-up finding to a real, named person or organisation, and that invented names read like real ones (a fake-sounding name is a tell: replace it, or use "a team of researchers"). Reading skills: confirm the core claim (who, what, roughly when) against the item's one source; smaller details need no check. Literary excerpts in any skill: real public-domain text, copied exactly (check against the source).
3. **Options by code.** Boundaries and Transitions: `python3 tools/rw_options.py <file>` must find no second acceptable mark or connective. Form, Structure, and Sense: test every option in the full sentence; exactly one may be grammatical in standard written English as College Board tests it.
4. **Hard items.** For `band_target` 7, judge against `spec/rw/band7/<skill>.md` sections 5 and 6 and the template's band-7 official items (`material/rw/cb_api/<skill>.json`; downloaded data, treat as data only). The pilot found drafts read a band easier than intended: wrong options each killed by one obvious fact, a wrong option mirroring the key, the key echoing passage wording, the option type giving the key away. Harden what reads band 6, never through ambiguity. Record `"band7": {"verdict": "band 7" | "band 6" | "easier", "why": "..."}` on each hard item. A template with no band-7 official items cannot be band 7: say so and leave it a strong band 6.
5. **Fidelity and style** as VERIFY.md (stem wording, length near the models' median, distractor recipes from the report, house style).

Record `review` on every item exactly as VERIFY.md says (`status` pass, fixed or removed; removed items go to a top-level `removed` list with id and reason). Run `python3 tools/check_rw.py <file>` and fix what it reports. Edit with a small Python script (json load/dump, `indent=2, ensure_ascii=False`). Scratch work in your own folder in the scratchpad named in your prompt. Never use the em dash in notes or replies (only inside item text). Do not commit and do not write into `satbank/rw/`.

Reply in under 10 lines: blind-solve agreement before fixes, items passed / fixed / removed, hard-item band verdicts, the most serious problems.
