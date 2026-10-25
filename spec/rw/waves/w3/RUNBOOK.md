# Wave 3 overnight runbook (lead)

Started 2026-10-20 01:30 at the user's request: "throughout the night, run multiple agents non stop to resume the
ebrw questions, dont wait for my input ... the limit will reset in every 5 hour starting from 2am".

**Not done overnight, the user's call in the morning:** deploying to prod (prac.fsat.io) and any git commit.
Report "deploy pending" with the morning summary.

## Every wake (cron tick, a handback, or after a usage-limit reset)

1. `python3 spec/rw/waves/scripts/w3_status.py` (stage per batch, from disk).
2. For each batch, the next step by stage (hard cap: 20 subagents at once, counting any finished writer still waiting on its own helper; keep 18 to 19 so solves and reviews can start; one agent per staged file at a time; reviewers and solvers before new writers):

| Stage | Next | Who |
|---|---|---|
| plan | writer | Agent, default model (Opus) |
| writing / writing (unreadable) | writer in continue mode (same prompt) | Agent, Opus |
| written | reviewer | Agent, Opus |
| reviewed | `w3_lead.py prep <batch>`, then the safety solve (Opus) and, if prep made a gate set, 2 gate runs (`model: "haiku"`), in parallel | lead + Agents |
| solve answers in | `w3_lead.py finish <batch>` (gate score -> band rule -> apply_safety -> promote) | lead only, one at a time |
| solved / promoted | done (note `not_agreed` hard items for the morning; they stay unpromoted) | |

3. Never relaunch a stage whose agent is still running: `<SP>/running.json` maps batch -> {stage, agent id, launch time};
   update it on every launch and every handback (remove the batch when its agent hands back). A writer or
reviewer cut off by the limit leaves a partial file; the same prompt continues it.

Waiting stages (cap reached): `<SP>/queue.json`, a list of {batch, stage}; on every handback launch from its front first
(solvers and reviewers before writers). The registry undercounts: a finished writer still waiting on its own helper
holds a slot, so the cap can bite at 18 to 19 in the registry.

Env for the lead script: `W3_SCRATCH=/private/tmp/claude-501/-Users-workingmyassof-freshbot-satbank/11932fea-c5c4-475d-bd5f-041033f1446a/scratchpad/w3`.

## Band rule (scripted in w3_lead.py)

- Central Ideas, Inferences, Cross-Text: `six` (band 6 by plan), no gate.
- Words in Context: `review` (the reviewer's rarity call), no gate.
- Other six skills: gate per batch when it has reviewed band-7 targets (2 Haiku runs over the batch's hard items
  plus 6 official anchors each of band 5, 6, 7). Anchors separate (b6 - b7 >= 0.05): `review` when ours is closer to
  b7 than to b6; else `review` when ours <= min(b6, b7) + 0.02; otherwise `six`.

## Prompts (fill <skill>, <b>, <batch> = <skill>_<b>, <SP> = the scratch root above)

Writer: "Wave 3 writer. Read spec/rw/waves/WAVE.md and follow it exactly. Your batch: wave w3, skill <skill>, batch
<b> (cells in spec/rw/waves/w3/plan.json under [<skill>][<b>]); output spec/rw/waves/w3/<batch>.json. If that file
already exists (an earlier run was cut off by a usage limit), keep its items and write only the missing cells.
Claims in spec/rw/fidelity/claims.txt whose id ends in `.w3<b>_NN` for your skill were made by an earlier run of this
same batch whose file was lost: those subjects are yours to reuse or drop. Many writers run at once: re-read
claims.txt right after each append. Save after every few items. When every planned item is written and check_rw
passes, set top-level "done": true. Do not launch sub-agents (agent slots are capped at 20 for the whole run); if web
search is rate-limited, fetch pages directly. Scratch: <SP>/<batch>/write. No git commands of any kind (the tree holds the
user's uncommitted work); never write into satbank/rw/; no deploy. Reply in under 10 lines as WAVE.md says."

Reviewer: "Wave 3 reviewer. Read spec/rw/waves/REVIEW.md and follow it exactly. Your file:
spec/rw/waves/w3/<batch>.json. Scratch: <SP>/<batch>/review. If some items already carry `review` (an earlier run
was cut off), keep those and review the rest. No git commands of any kind; never write into satbank/rw/. Reply in
under 10 lines."

Safety: "Blind solver. Read spec/rw/waves/SOLVE.md and do the Safety solve. Set dir: <SP>/<batch>/safety. No git
commands. Reply in 3 lines."

Gate (model haiku, runs 1 and 2): "Blind solver. Read spec/rw/waves/SOLVE.md and do the Gate solve. Set dir:
<SP>/<batch>/gate; your run number: <n>. No git commands. Reply in 3 lines."

## Log

- 01:30 runbook, SOLVE.md, w3_status.py, w3_lead.py (dry-run tested on a throwaway copy, cleaned up).
- 01:35 14 writers launched: b1 of all 10 skills, b2 of words_in_context, command_of_evidence, boundaries, form_structure_and_sense.
- 01:45 tick: 14 writers running (3 files started), nothing to advance.
- 01:59 boundaries_b1 written (25, done) -> reviewer; writer words_in_context_b3 launched.
- 02:00 form_structure_and_sense_b1 (24) and boundaries_b2 (25) written -> reviewers; writer command_of_evidence_b3 launched.
- 02:01 cross_text_connections_b1 written (18) -> reviewer; writer cross_text_connections_b2 launched.
- 02:01 inferences_b1 written (24) -> reviewer; writer inferences_b2 launched.
- 02:02 transitions_b1 written (23) -> reviewer; writer transitions_b2 launched.
- 02:03 form_structure_and_sense_b2 written (24) -> reviewer.
- 02:23 central_ideas_and_details_b1 written (24) -> reviewer. Hit the 20-subagent cap; writer central_ideas_and_details_b2 waits for a slot.
- 02:05 reset tick: no agent died; 19 running (11 writers, 8 reviewers); 12 batches written, none reviewed yet; slots full.
- 02:05 command_of_evidence_b1 written (22) -> reviewer.
- 02:05 tick: 19 running, slots full, nothing to advance.
- 02:06 rhetorical_synthesis_b1 (24) and words_in_context_b1 (24) written -> reviewers.
- 02:3x form_structure_and_sense_b1 reviewed (22 pass, 2 fixed); prepped (7 hard, gate set). Cap hit at registry 18: safety, gate x2 and writer CID b2 queued.
- 02:08 boundaries_b1 reviewed (21 pass, 4 fixed; 6 band-7 verdicts); prepped. Launched FSS b1 safety + gate run 1. Queue: FSS b1 gate2, bnd b1 safety+gate1, CID b2 writer.
- 02:09 boundaries_b2 reviewed (19 pass, 6 fixed; 4 band-7 verdicts), prepped. FSS b1 safety in (0 flagged); gates running. Launched bnd b1 safety+gate1, WiC b2 reviewer (writer done, 24).
- 02:09 cross_text_connections_b1 reviewed (7 pass, 11 fixed; all hard band 6), prepped, safety launched. FSS b1 gate run 1 in. bnd b1 gate2 launched.
- 02:11 PROMOTED: form_structure_and_sense_b1 24/24 (gate 0.86/0.72/ours 0.71 -> review), cross_text_connections_b1 18/18 (six), boundaries_b1 25/25 (gate 0.74/0.45/ours 0.59 -> review); rw_bank check ok. FSS b2 reviewed (19 pass, 5 fixed), safety in; gates running. Writers boundaries_b3, form_structure_and_sense_b3, central_ideas_and_details_b2 launched.
- 02:11 PROMOTED form_structure_and_sense_b2 24/24 (gate 0.83/0.69/ours 0.75 -> review). transitions_b1 reviewed (15 pass, 8 fixed), solves launched. text_structure_and_purpose_b1 written (25) -> reviewer.
- 02:12 PROMOTED boundaries_b2 25/25 (gate 0.68/0.36/ours 0.54 -> six). transitions_b1 safety in (0 flagged). Writers transitions_b3, rhetorical_synthesis_b2 launched.
- 02:12 PROMOTED transitions_b1 23/23 (gate 0.57/0.40/ours 0.65 -> six). Writer words_in_context_b4 launched.
- 02:15 central_ideas_and_details_b1 reviewed (18 pass, 6 fixed; 5 hard hardened) -> safety. rhetorical_synthesis_b1 reviewed (11 pass, 13 fixed; 3 band-7) -> safety; gates queued (cap).
- 02:16 PROMOTED central_ideas_and_details_b1 24/24 (six). RS b1 safety in (0 flagged); gates running.
- 02:16 PROMOTED rhetorical_synthesis_b1 24/24 (gate 0.73/0.77/ours 0.81 -> six). Writers text_structure_and_purpose_b2, inferences_b3 launched.
- 02:17 inferences_b1 reviewed (14 pass, 10 fixed; 7 hard hardened; 3 sources replaced) -> safety. Note for morning: 04, 10, 12 are well-known topics.
- 02:18 PROMOTED inferences_b1 24/24 (six). Writer central_ideas_and_details_b3 launched.
- 02:19 command_of_evidence_b1 reviewed (15 pass, 6 fixed, 1 removed: 08 too famous; 3 band-7) -> safety; gates queued (cap bites at registry 19, keep 18).
- 02:20 CoE b1 safety in (0 flagged); gate run 1 launched, run 2 queued.
- 02:20 words_in_context_b1 reviewed (16 pass, 8 fixed; 5 band-7) -> safety. Lead call: item 04 kept band 6 (target 6, plays easy).
- 02:21 PROMOTED words_in_context_b1 24/24 (review rule). CoE b1 gate run 2 launched. Writer words_in_context_b5 launched.
- 02:21 PROMOTED command_of_evidence_b1 21/21 (gate 0.80/0.75/ours 0.79 -> six). Writer form_structure_and_sense_b4 launched.
- 02:23 text_structure_and_purpose_b1 reviewed (18 pass, 7 fixed: all hard items hardened; 3 band-7) -> safety; gates queued.
- 02:26 PROMOTED text_structure_and_purpose_b1 25/25 (gate 0.86/0.77/ours 0.85 -> six). words_in_context_b2 reviewed (15 pass, 9 fixed; 3 band-7) -> safety. Writer command_of_evidence_b4 launched. Live: 281.
- 02:26 PROMOTED words_in_context_b2 24/24 (review). Writer rhetorical_synthesis_b3 launched. Live: 305.
- 02:38 transitions_b2 written (23) -> reviewer.
- 02:44 cross_text_connections_b2 written (17) -> reviewer. NOTE: the shared web-search budget ran out for writers around now; they fall back to fetching pages directly (WebFetch). Tell reading-skill agents to fetch when search fails.
- 02:45 tick: 19 running (17 writers incl. 6 finishing, 2 reviewers), 13 batches promoted, 305 live; no deaths, slots full.
- 02:45 words_in_context_b3 written (23) -> reviewer.
- 02:45 form_structure_and_sense_b3 written (24) -> reviewer.
- 02:46 transitions_b2 reviewed (22 pass, 1 fixed; 3 band-7) -> safety; gates queued.
- 02:47 boundaries_b3 written (25) -> reviewer. Transitions b2 gate run 1 in, run 2 running.
- 02:48 command_of_evidence_b2 written (22) -> reviewer. Writers were spawning helper agents (that is what fills the cap): from now on every prompt says no sub-agents.
- 02:48 PROMOTED transitions_b2 23/23 (gate 0.64/0.32/ours 0.72 -> six). Writer boundaries_b4 launched.
- 02:49 rhetorical_synthesis_b2 written (24) -> reviewer (told to drop made-up figures on the real ogre-faced spider study).
- 02:50 transitions_b3 written (23) -> reviewer.
- 02:51 inferences_b2 written (23) -> reviewer.
- 02:52 form_structure_and_sense_b3 reviewed (20 pass, 4 fixed; 5 band-7) -> safety; gates queued.
- 02:53 cross_text_connections_b2 reviewed (11 pass, 6 fixed; all band 6) -> safety. FSS b3 gate run 1 in, run 2 running.
- 02:54 PROMOTED cross_text_connections_b2 17/17 (six); cross-text skill complete. Writer form_structure_and_sense_b5 launched.
- 02:55 PROMOTED form_structure_and_sense_b3 24/24 (gate 0.86/0.71/ours 0.66 -> review). Lead checked gate doubt g006 (w3b3_02, dangling 'Drawn from recordings'): key D sound, Haiku fell for the trap. Writer rhetorical_synthesis_b4 launched.
- 02:55 boundaries_b3 reviewed (20 pass, 5 fixed; 6 band-7) -> safety; gates queued.
- 02:57 rhetorical_synthesis_b2 reviewed (22 pass, 2 fixed; spider figures made qualitative) -> safety+gate1, gate2 queued. central_ideas_and_details_b2 written (24) -> reviewer. words_in_context_b4 written (23) -> reviewer. bnd b3 gate1 in.
- 02:58 RS b2 safety in (0 flagged), gate run 1 in. Writer text_structure_and_purpose_b3 launched.
- 02:59 PROMOTED boundaries_b3 25/25 (gate 0.76/0.44/ours 0.65 -> six) and rhetorical_synthesis_b2 24/24 (gate 0.81/0.78/ours 0.86 -> six). words_in_context_b3 reviewed (18 pass, 5 fixed; 4 band-7) -> safety. Writer command_of_evidence_b5 launched.
- 02:59 PROMOTED words_in_context_b3 23/23 (review). Writer words_in_context_b6 launched. Live: 441.
- 03:00 transitions_b3 reviewed (21 pass, 2 fixed; 1 band-7) -> safety; gates queued.
- 03:01 command_of_evidence_b2 reviewed (16 pass, 6 fixed; 4 band-7) -> safety; gates queued. Transitions b3 gate2 running.
- 03:02 PROMOTED transitions_b3 23/23 (gate 0.64/0.32/ours 0.49 -> six). CoE b2 safety in (0 flagged); gates running. rhetorical_synthesis_b3 written (24) -> reviewer; form_structure_and_sense_b4 written (24) -> reviewer.
- 03:02 CoE b2 gate run 1 in. Writer transitions_b4 launched.
- 03:02 PROMOTED command_of_evidence_b2 22/22 (gate 0.76/0.79/ours 0.74, anchors blind -> review). Writer boundaries_b5 launched. Live: 486.
- 03:03 words_in_context_b5 written (23) -> reviewer.
- 03:05 central_ideas_and_details_b3 written (23; literary share 17% vs ~25%) -> reviewer.
- 03:05 inferences_b3 written (23) -> reviewer, told to confirm 9 premises that only had title/authors/year (search ran out) or narrow/remove. For later READING-skill writers add: 'web search is used up: confirm each premise by fetching the abstract or page directly (DOI, PubMed, PMC, publisher); a subject whose premise you cannot confirm from a reachable page is dropped, not written from memory.'
- 03:06 tick: 19 running (10 writers, 9 reviewers), 21 promoted, 486 live; no deaths.
- 03:06 words_in_context_b4 reviewed (19 pass, 4 fixed; 2 band-7) -> safety.
- 03:07 PROMOTED words_in_context_b4 23/23 (review). inferences_b2 reviewed (11 pass, 11 fixed, 1 removed: Durrington Walls was a round1 subject) -> safety. command_of_evidence_b3 written (22) -> reviewer. Writer command_of_evidence_b6 launched. Live: 509.
- 03:07 PROMOTED inferences_b2 22/22 (six). Writer words_in_context_b7 launched. Live: 531.
- 03:08 text_structure_and_purpose_b2 written (25) -> reviewer.
- 03:09 central_ideas_and_details_b2 reviewed (16 pass, 8 fixed; 6 hard hardened; items 12 and 20 resourced) -> safety.
- 03:10 PROMOTED central_ideas_and_details_b2 24/24 (six). rhetorical_synthesis_b3 reviewed (20 pass, 4 fixed; 4 band-7) -> safety; gates queued. Writer text_structure_and_purpose_b4 launched. Live: 555.
- 03:12 form_structure_and_sense_b4 reviewed (18 pass, 6 fixed; 2 band-7). MORNING NOTE: its hard item 07 (R4_pastperf_future tense) is rated 'easier' than band 6 but stays in the hard tier; retier to medium? (WAVE.md: hard tense cells cannot reach band 6). RS b3 safety in; gates running; FSS b4 safety launched, gates queued.
- 03:13 PROMOTED rhetorical_synthesis_b3 24/24 (gate 0.77/0.81/ours 0.75, anchors blind -> review). FSS b4 safety in (0 flagged); gates running. Writer rhetorical_synthesis_b5 launched. Live: 579.
- 03:14 Lead checked FSS b4 gate doubts on our items: g005 (w3b4_03 appositive 'A crust of salts...') key D sound, Haiku misparsed the opener; g004 (w3b4_06) key C sound.
- 03:14 PROMOTED form_structure_and_sense_b4 24/24 (gate 0.85/0.75/ours 0.76 -> review). Writer command_of_evidence_b7 launched. Live: 603.
- 03:14 words_in_context_b5 reviewed (19 pass, 4 fixed; 3 band-7; flags resolved) -> safety.
- 03:15 PROMOTED words_in_context_b5 23/23 (review). Writer words_in_context_b8 launched: every one of the 46 batches now has a writer (or is past writing). Live: 626.
- 03:21 central_ideas_and_details_b3 reviewed (18 pass, 5 fixed; Ghost Army and Project Pigeon replaced as fame tells) -> safety. command_of_evidence_b3 reviewed (17 pass, 5 fixed; 4 band-7) -> safety; gates queued. MORNING NOTE: CID b3 keeps 5 borderline-fame subjects (Kalambo Falls, Seneca Village, crucian carp, killer whales of Eden, Morning Glory cloud).
- 03:21 PROMOTED central_ideas_and_details_b3 23/23 (six); Central Ideas complete. Live: 649.
- 03:21 CoE b3 safety in (0 flagged). Note: w3b3_08 key B says 6.5 m/s had 'only slightly fewer' bat deaths than 5.0 m/s in 2009 (0.55 vs 0.73, about 25% fewer but 0.18 per turbine against 2.29 at standard): defensible in context, worth a glance in the morning.
- 03:22 PROMOTED command_of_evidence_b3 (see line above).
- 03:23 text_structure_and_purpose_b2 reviewed (17 pass, 8 fixed; 2 band-7) -> safety + gates.
- 03:23 PROMOTED text_structure_and_purpose_b2 (see above).
- 03:25 rhetorical_synthesis_b4 written (24) -> reviewer.
- 03:27 form_structure_and_sense_b5 written (24) -> reviewer.
- 03:29 command_of_evidence_b4 written (22) -> reviewer.
- 03:29 inferences_b3 reviewed (8 pass, 15 fixed; all 9 memory-sourced premises confirmed from fetched abstracts, passages narrowed where needed; a misnamed researcher corrected) -> safety.
- 03:30 PROMOTED inferences_b3 (six); Inferences complete.
- 03:33 transitions_b4 written (22) -> reviewer.
- 03:34 form_structure_and_sense_b5 reviewed (22 pass, 2 fixed: two it-cleft/display options that were defensible) -> safety + gates.
- 03:35 PROMOTED form_structure_and_sense_b5; Form, Structure, and Sense complete.
- 03:36 boundaries_b4 written (25) -> reviewer.
- 03:36 boundaries_b5 written (25) -> reviewer.
- 03:38 rhetorical_synthesis_b4 reviewed (9 pass, 15 fixed; 2 band-7) -> safety + gates.
- 03:39 PROMOTED rhetorical_synthesis_b4 (see above).
- 03:40 transitions_b4 reviewed (19 pass, 3 fixed; Deinocheirus rebuilt to band 7) -> safety + gates.
- 03:41 boundaries_b5 reviewed (23 pass, 2 fixed: item 11 missing word restored; 07 claim moved off Gelleri) -> safety + gates. Transitions b4 safety in (0 flagged), gate 1 in.
- 03:41 PROMOTED transitions_b4; Transitions complete.
- 03:42 PROMOTED boundaries_b5 (see above).
- 03:44 command_of_evidence_b4 reviewed (12 pass, 10 fixed; 5 band-7; Enguri item rebuilt on height) -> safety + gates. rhetorical_synthesis_b5 written (23) -> reviewer.
- 03:45 PROMOTED command_of_evidence_b4 (see above). Lead checked gate doubt g026 (w3b4_05 remittances): GDP ratio is in the passage, key B sound.
- 03:45 tick: 36 promoted (836 live); 10 running (7 writers, 2 reviewers... ), every remaining batch has an agent; no deaths. TSP b3 and b4 writers have saved nothing yet (started 02:58 / 03:10): check again next tick.
- 03:48 boundaries_b4 reviewed (20 pass, 5 fixed; repeated live subject 23 replaced; 4 band-7) -> safety + gates.
- 03:48 words_in_context_b6 written (23) -> reviewer.
- 03:49 PROMOTED boundaries_b4; Boundaries complete.
- 03:50 rhetorical_synthesis_b5 reviewed (21 pass, 2 fixed; 2 band-7) -> safety + gates.
- 03:50 PROMOTED rhetorical_synthesis_b5; Rhetorical Synthesis complete.
- 03:53 command_of_evidence_b6 written (22) -> reviewer.
- 03:54 command_of_evidence_b5 written (22) -> reviewer.
- 03:55 words_in_context_b7 written (23) -> reviewer.
- 03:58 words_in_context_b6 reviewed (20 pass, 3 fixed; 3 band-7) -> safety. MORNING NOTE: WiC w3b6_22 premise (Juana Briones could not read or write) rests on a Wikipedia line tagged 'citation needed'.
- 03:58 PROMOTED words_in_context_b6 (review).
- 03:59 text_structure_and_purpose_b4 written (25) -> reviewer.
- 04:02 text_structure_and_purpose_b3 written (25) -> reviewer.
- 04:04 command_of_evidence_b6 reviewed (15 pass, 7 fixed; 2 band-7) -> safety + gates.
- 04:05 PROMOTED command_of_evidence_b6 (see above).
- 04:05 words_in_context_b7 reviewed (22 pass, 1 fixed; 4 band-7) -> safety.
- 04:06 tick + PROMOTED words_in_context_b7 (review). Remaining: CoE b5 (review), TSP b3 and b4 (review), CoE b7 and WiC b8 (writers finishing, files complete).
- 04:08 command_of_evidence_b5 reviewed (16 pass, 6 fixed; Lake Kossou year corrected; 6 band-7) -> safety + gates. command_of_evidence_b7 written (21) -> reviewer (told to move item 15 off Kenya electricity if it duplicates the b7 bank item).
- 04:09 PROMOTED command_of_evidence_b5 (see above).
- 04:11 MORNING NOTE (privacy): two agents sent the user's email address as a contact in the User-Agent header of Wikipedia API requests (TSP b3 writer's wk.sh, TSP b4 reviewer once). Removed from wk.sh; running agents told not to. Report to the user.
- 04:11 text_structure_and_purpose_b4 reviewed (18 pass, 7 fixed; 02 rated band 6 against target 7) -> safety in (0 flagged), gates running. words_in_context_b8 written (23) -> reviewer.
- 04:12 PROMOTED text_structure_and_purpose_b4 (see above). Gate note: official TSP anchors lose their underline markup in cb_api passages (g022 to g024), adding noise to TSP anchor scores.
- 04:15 text_structure_and_purpose_b3 reviewed (20 pass, 5 fixed; wrong coauthor first name corrected; 4 band-7) -> safety + gates.
- 04:16 PROMOTED text_structure_and_purpose_b3; Text Structure complete.
- 07:00 tick: words_in_context_b8 reviewed (21 pass, 2 fixed; band-7 cell rebuilt) and command_of_evidence_b7 reviewed (13 pass, 8 fixed; Kenya duplicate moved to Malaysia) -> final solves. 44 promoted, 1,024 live.
- 07:00 PROMOTED words_in_context_b8 (review); Words in Context complete. Only command_of_evidence_b7 left (safety + 2 gates running).
- 07:01 PROMOTED command_of_evidence_b7 after a lead fix: w3b7_08's table column 'Both habitats' renamed 'Combined' (the gate solver read option A as defensible through that label). ALL 46 BATCHES PROMOTED.

## Morning summary (2026-10-20 ~07:10)

- All 46 batches written, reviewed, blind-solved and promoted: 1,068 new items in `satbank/rw/<skill>__w3.json`
  (hard 336, medium 363, easy 369; hard bands: 78 band 7, 258 band 6). 2 items removed in review (one too famous,
  one a round-1 subject). No hard item failed the independent safety solve. `server/checks/rw_bank.py` passes and
  every w3 bank file passes `check_rw`. R&W bank now 2,850 items locally (was 1,782).
- NOT done (the user's call): deploy to prac.fsat.io, git commit.
- Privacy: two agents put the user's email in the User-Agent of Wikipedia requests (TSP b3 writer script, TSP b4
  reviewer once). Removed from the script; later prompts forbid it.
- For a look: FSS w3b4_07 hard tense item rated easier than band 6 (retier to medium?); CoE w3b3_08 key's
  "only slightly fewer" (0.55 vs 0.73); WiC w3b6_22 rests on a "citation needed" Wikipedia line; CID b3 keeps five
  borderline-famous subjects; inferences_b1 items 04, 10, 12 are well-known topics.
- Web search ran out mid-run; later writers/reviewers confirmed premises by fetching pages directly, and subjects
  that could not be confirmed were dropped, not written from memory.
