# Wave 5 runbook (lead)

Started 2026-10-27 while wave 4 finishes, at the user's request ("spin up more agents"). Wave 5 is the last wave: 1,085
items in 48 batches (`plan.json`, frozen by `make_plan.py 5 --pending w4`, which counts wave 4's unpromoted planned
cells as written). Wave 4 plus wave 5 bring the R&W bank to 5,000, short only by the items reviewers remove in either
wave (top up with a small wave 6 if needed: `make_plan.py 6` with WAVES raised in tools/rw_plan.py).

**Not done without the user:** deploy to prac.fsat.io, git commit.

Same procedure as `spec/rw/waves/w4/RUNBOOK.md` and `w3/RUNBOOK.md` (stage table, band rule, prompts), with:
- Scripts: `WAVE=w5 python3 spec/rw/waves/scripts/wave_status.py`; lead steps
  `WAVE=w5 W3_SCRATCH=<S5> python3 spec/rw/waves/scripts/wave_lead.py prep|finish <batch>`.
- `<S5>` = `/private/tmp/claude-501/-Users-workingmyassof-freshbot-satbank/76b9850c-8a09-4251-b31f-505f38295172/scratchpad/w5`. One registry for both waves: `<w4 SP>/reg.py`, wave-5 batches registered as `w5.<batch>`.
- Writer and reviewer prompts: the w4 ones with w4 -> w5 and the w5 scratch (`<S5>/writer_prompt.txt`).
- Band rule changes in make_plan.py: hard cells on templates with no band-7 official item are band 6 by plan; hard
  FSS tense cells moved to medium. WAVE.md has the wave-4 lessons.
- Cap: 20 agents at once across both waves; wave-4 reviewers and solvers go first.

## Log

- 09:33 plan frozen (1,085 items, 48 batches); WAVE.md wave-4 lessons added.
- 09:35 9 writers launched (b1 of every skill but FSS); 39 batches queued in <w4 SP>/queue.json (round-robin by skill).
- 09:43 USER: no new batches until the running set is finished. Queue held in <w4 SP>/queue_held.txt (39 w5 writer batches, untouched); queue.json emptied. In-flight batches still get their review and blind solves so they can be promoted.
- 09:45 USER said 'stop all', all 19 agents stopped; a minute later the user asked to resume all: 18 resumed with their context, WiC b6 writer (it had stalled) relaunched in continue mode. The 39 held w5 batches stay held.
- 09:50 PROMOTED command_of_evidence_b4 (gate {"band6": 0.79, "band7": 0.72, "ours": 0.73, "rule": "review"}; safety 0 flagged). USER: no new agents at all (I had kept launching review/solve agents for finished batches; wrong reading). From now on only the agents already running finish; finished writer batches wait for review; nothing else launched. FSS b5 gate2 not launched.
- 10:34 network outage (ENOTFOUND) killed the 10 running writers; user said resume: all 10 resumed with their context (same agents, no new ones).
- 10:36 boundaries_b1 written (25, done; ambahan and Epischura withdrawn) -> WAITS for a reviewer. Reviewer notes: 19 same genus as a live CID item (N. pulcher); 07 may be band 6; 10 runs 57 words.
- 10:37 rhetorical_synthesis_b1 written (24, done; EXAMPLE hard written band 6, no band-7 officials; Aryabhata clashed with official RS 3.17) -> WAITS for a reviewer. Reviewer notes: easy and hard at the density warning line; 14 tiger bush option A softest. Planner note: make_plan only reads band-7 tables for Bnd and FSS, so other skills' no-band-7 templates (RS EXAMPLE) still get band 7 in the plan; writers downgrade them.
- 10:43 inferences_b1 written (19, done; Chace Act withdrawn as twin of official 1.3; Kopiez sample library already CoE w4b3_12, now Beck lead white) -> WAITS for a reviewer.
- 10:44 transitions_b1 written (23, done; K1_grant_turn, P1_purpose_aptness hard written band 6, no band-7 officials; camera traps, Linnaeus, scurvy, Empire State lightning withdrawn) -> WAITS for a reviewer.
- 10:45 words_in_context_b1 written (24, done; Elizabeth and Her German Garden claimed first by TSP w5b1_12, now Canfield) -> WAITS for a reviewer.
- 10:50 text_structure_and_purpose_b1 written (21, done; 04 P_profile and 06 S14 hard band 6, no band-7 officials) -> WAITS for a reviewer. Reviewer notes: 14 Japanese macaques in hot springs may be famous and shares a species with an official WiC item; 08, 11 keep the period outside the underline; easy register exactly at the floor.
- 10:52 central_ideas_and_details_b1 written (25, done) -> WAITS for a reviewer. Reviewer notes: 08 Arctic hare near live CTC Arctic-fox item; 03 Haitian Revolution frame may be classroom-known; four literary passages above model median length.
- 11:01 cross_text_connections_b1 written (19, done; orchids, Dene-Yeniseian, potted plants, Ghent Altarpiece, Iran fertility withdrawn) -> WAITS for a reviewer. Reviewer notes: 02 Paris women's guild rests on a dissertation abstract on medievalists.net; cycad and pika prior views unsourced, framed as the author's.

## PAUSED 2026-10-27 (user: no new agents) - how to resume

None live yet. 9 batches written, all need review: boundaries_b1, central_ideas_and_details_b1, command_of_evidence_b1,
cross_text_connections_b1, inferences_b1, rhetorical_synthesis_b1, text_structure_and_purpose_b1, transitions_b1,
words_in_context_b1 (reviewer notes per batch in the log above). The other 39 batches are unstarted, listed in
`queue_held.txt` here (round-robin by skill). Prompts: `writer_prompt.txt`, `reviewer_prompt.txt` here (replace the
scratch path with the new session's scratchpad). Finish wave 4 first.
- 11:17 USER: 'resume wave 5'. Hold lifted. Finishing w4's 8 leftover batches alongside (reviews/solves first), then the 39 held w5 writers from the queue.
- 14:01 RESUMED wave 5: 9 b1 reviewers + 10 writers (b2 of nine skills, FSS b1); 29 batches still queued.
- 14:15 rhetorical_synthesis_b1 reviewed (16 pass, 8 fixed; 01, 03, 04 band 7; 14 tiger bush A rebuilt) -> safety + gate1, gate2 queued. check_rw crashed on queue_held.json in this folder (it globs every wave JSON): renamed to queue_held.txt.
- 14:15 words_in_context_b1 reviewed (22 pass, 2 fixed; 01 wrong options copied its model's, replaced; 03 Daphnia claim narrowed; 01, 02, 05, 06 band 7) -> safety.
- 14:16 PROMOTED words_in_context_b1 (review rule; safety 0 flagged): first w5 batch live.
- 14:17 PROMOTED rhetorical_synthesis_b1 (gate {"band6": 0.73, "band7": 0.76, "ours": 0.74, "rule": "review"}; safety 0 flagged).
- 14:17 PROMOTED (log above). inferences_b1 reviewed (11 pass, 8 fixed; all hard band 6) -> safety. FOR THE USER: 06 (industrial lead white in a painting attributed to the 1300s) sits on the saturated 'material postdates attribution' theme; kept. Writers central_ideas_and_details_b3, inferences_b3 launched.
- 14:18 boundaries_b1 reviewed (20 pass, 5 fixed; 19 cichlid, 18 aflaj, 25 Chinguetti replaced as concept twins of live items; 07 hardened; 7 band 7) -> safety + gate1, gate2 queued.
- 14:20 PROMOTED inferences_b1 19/19 (six). Safety flagged 01 (spider silk gift): key assumed a dose effect the study never tested; lead reworded key B to 'adding compounds that can make a female more willing', lead_override recorded.
- 14:21 command_of_evidence_b1 reviewed (15 pass, 6 fixed, 1 removed: 05 Berkeley soda tax repeated live Mexico sugary-drink tax item; 6 band 7; Nigeria figure corrected) -> safety + gates. Bnd b1 safety in (0 flagged).
- 14:22 command_of_evidence_b1 safety in (0 flagged; 10 'nearly identical' for 784 vs 748 -> lead changed to 'comparable'). Waiting on gate2.
- 14:23 PROMOTED boundaries_b1 (gate {"band6": 0.79, "band7": 0.37, "ours": 0.52, "rule": "review"}; lead checked gate doubt g007 Chi Wara absolute phrase, key C sound) and command_of_evidence_b1 (gate {"band6": 0.81, "band7": 0.8, "ours": 0.76, "rule": "review"}).
- 14:24 writers command_of_evidence_b3, words_in_context_b3, text_structure_and_purpose_b3 launched. w5 live 113, bank 3,852.
- 14:26 cross_text_connections_b1 reviewed (12 pass, 7 fixed; 11 glacier algae twin of live RS item, 15 Hebrew revival famous, both replaced; 02 confirmed on UA repository; all hard band 6) -> safety.
- 14:27 PROMOTED cross_text_connections_b1 (six; safety 0 flagged).
- 14:27 PROMOTED (CTC b1 above). transitions_b1 reviewed (15 pass, 8 fixed; 09 kotekan, 13 Bras Cubas, 21 hiragana were round-1 subjects, 17 trautonium copied a live frame: all replaced; 03, 05 band 7) -> safety + gates. Lead calls: Chang'e (row in an official CoE table, different idea) and butter tea (one bullet in live w2b5_01) kept.
- 14:28 text_structure_and_purpose_b1 reviewed (15 pass, 6 fixed; 4 band-7 drafts rebuilt; 14 snow monkeys judged famous, now weathered Roman glass) -> safety; gates queued. Reviewer found check_rw register() splits sentences without stripping <u> tags, so a period inside the underline fails the sentence-length gate.
- 14:28 tools/check_rw.py register(): sentences now split on tag-stripped text, so a period inside <u> ends a sentence (as CB writes it). TSP writers can put the period inside the underline from now on.
- 14:29 PROMOTED transitions_b1 (gate {"band6": 0.7, "band7": 0.39, "ours": 0.68, "rule": "six"}; safety 0 flagged). TSP b1 safety in (0 flagged), gates running.
- 14:30 PROMOTED text_structure_and_purpose_b1 (gate {"band6": 0.79, "band7": 0.71, "ours": 0.78, "rule": "six"}; missing-underline gate items are official anchors).
- 14:30 writers rhetorical_synthesis_b3, transitions_b3, boundaries_b3 launched. central_ideas_and_details_b1 reviewed (16 pass, 9 fixed; 13 had a defensible B (Antwerp), rewritten; 04 Paul clone of live Callard item and 08 Arctic hare replaced; 03 Haitian Revolution kept) -> safety.
- 14:31 PROMOTED central_ideas_and_details_b1 (six; safety 0 flagged). All 9 w5 b1 batches live.
- 14:32 writer form_structure_and_sense_b2 launched.
- 14:44 boundaries_b2 written (25, done; 5 band 7) -> reviewer (check 05 '; however,' trap and 18 colon rebuild).
- 14:46 rhetorical_synthesis_b2 written (24, done; Lebombo bone twin of live Ishango withdrawn) -> reviewer (plain the register back). form_structure_and_sense_b1 written (24, done; 5 band 7) -> reviewer.
- 15:01 form_structure_and_sense_b1 reviewed (19 pass, 5 fixed; 14 Nenets migration repeated live w3b4_14, now Turku Christmas Peace; 01, 02, 05, 07 band 7; 03 nyckelharpa band 6 under target 7) -> safety + gate1, gate2 queued.
- 15:01 boundaries_b2 reviewed (23 pass, 2 fixed; 14 had a defensible no-comma option, rebuilt; 06 Yamamoto cloned official 6d4b2e1e, now John Savio; 5 band 7) -> solves queued.
- 15:03 PROMOTED form_structure_and_sense_b1 (gate {"band6": 0.81, "band7": 0.62, "ours": 0.6, "rule": "review"}; safety 0 flagged).
- 15:03 writer inferences_b4 launched (Inferences now fully started).
- 15:04 PROMOTED boundaries_b2 (gate {"band6": 0.81, "band7": 0.41, "ours": 0.63, "rule": "six"}; safety 0 flagged).
- 15:05 words_in_context_b2 written (24, done) -> reviewer (two glass-bead artworks). Writer command_of_evidence_b4 launched.
- 15:06 transitions_b2 written (23, done; 3 band 7; Chulucanas withdrawn as near official Martinez) -> reviewer.
- 15:06 form_structure_and_sense_b2 written (24, done; 3 band 7) -> reviewer.
- 15:07 text_structure_and_purpose_b2 written (20, done; S16 hard band 6) -> reviewer.
- 15:10 rhetorical_synthesis_b2 reviewed (7 pass, 17 fixed; 06 leafcutter bees and 18 fire-triggered flowering replaced as concept twins of live items; 02, 04 band 7; medium and hard still ~11% over CB words per sentence, inside check_rw's 15%) -> safety + gate1, gate2 queued.
- 15:10 inferences_b2 written (19, done) -> reviewer.
- 15:11 rhetorical_synthesis_b2 safety flagged 02 (floating solar): D also defensible (reported the higher output in its attribution); lead rebuilt D as method plus aim, no result. Override on finish.
- 15:12 PROMOTED rhetorical_synthesis_b2 24/24 (gate {"band6": 0.83, "band7": 0.83, "ours": 0.81, "rule": "review"}); 02 promoted after the D rebuild, lead_override recorded.
- 15:12 cross_text_connections_b2 (18) and central_ideas_and_details_b2 (24) written -> reviewers. Writer words_in_context_b4 launched.
- 15:13 central_ideas_and_details_b3 written (24, done; CID now fully written) -> reviewer.
- 15:13 inferences_b3 written (19, done; natural science only 5 of 19, the free subjects were taken) -> reviewer.
- 15:14 boundaries_b3 written (25, done; paiza, ferrofluid, mangrove killifish withdrawn) -> reviewer.
- 15:28 transitions_b2 reviewed (17 pass, 6 fixed; 02, 05 band 7) and form_structure_and_sense_b2 reviewed (21 pass, 3 fixed; 10 Kadambini Ganguly near-copy of live FSS w2b1_22, now Telefon Hirmondo; 04, 06, 07 band 7) -> solves. Written: rhetorical_synthesis_b3 (24), transitions_b3 (23), command_of_evidence_b2 (22), text_structure_and_purpose_b3 (20) -> reviewers (RS b3 now, three queued).
- 15:28 inferences_b3 reviewed (18 pass, 1 fixed; all hard band 6) and text_structure_and_purpose_b2 reviewed (12 pass, 8 fixed; 08 Shklovsky round-1 subject and 18 Promenade plantee twin of live item replaced; 06 band 7) -> solves. WAVE.md saturated themes: ancient pottery residues.
- 15:29 PROMOTED transitions_b2 (gate {"band6": 0.62, "band7": 0.48, "ours": 0.67, "rule": "six"}; safety 0 flagged). FSS b2 safety in (0 flagged).
- 15:30 PROMOTED form_structure_and_sense_b2 (gate {"band6": 0.83, "band7": 0.74, "ours": 0.72, "rule": "review"}) and inferences_b3 (six); both safeties 0 flagged. TSP b2 safety in (0 flagged), gate2 in (missing-underline items are official anchors), gate1 running.
- 15:35 PROMOTED text_structure_and_purpose_b2 (gate {"band6": 0.79, "band7": 0.73, "ours": 0.85, "rule": "six"}). inferences_b2 reviewed (14 pass, 5 fixed; 08 Ye Xian and 09 Bretz floods fairly well known, kept) and central_ideas_and_details_b3 reviewed (13 pass, 11 fixed; 02 O'Keeffe kept) -> safety.
- 15:35 boundaries_b3 reviewed (22 pass, 3 fixed; 04 Lindy effect was official WiC b92c13fa, now Proteus effect; 17 Earth's hum live, now airglow; 5 band 7) -> solves. Reviewer text_structure_and_purpose_b3 and writers text_structure_and_purpose_b4, rhetorical_synthesis_b4 launched.
- 15:36 PROMOTED central_ideas_and_details_b3 (six; safety 0 flagged); CID done for w5.
- 15:37 PROMOTED inferences_b2 (six; safety 0 flagged). Bnd b3 safety in (0 flagged), gates running.
- 15:38 PROMOTED boundaries_b3 (gate {"band6": 0.83, "band7": 0.42, "ours": 0.54, "rule": "review"}); lead checked gate doubts g008 (Chilam Balam: B splices, key A sound) and g014 (Proteus: D 'though' concession fails on meaning, key B sound).
- 15:38 central_ideas_and_details_b2 reviewed (18 pass, 6 fixed; 05 fifth moth-and-bat subject, now Benin solar drip irrigation; 07 Scallop Shell cut to 64 words) -> safety. command_of_evidence_b3 written (22, done; 8 band 7) -> reviewer. Writers transitions_b4, boundaries_b4, form_structure_and_sense_b3, command_of_evidence_b5, words_in_context_b5 launched.
- 15:39 cross_text_connections_b2 reviewed (9 pass, 9 fixed; 13 Red Queen snails replaced by Black 1999 school-zone house prices, reviewer-written so the safety solve is its only blind check; all hard band 6) -> safety.
- 15:39 words_in_context_b2 reviewed (15 pass, 9 fixed; 18 'Ripped' was a second answer, now 'Shredded'; 12 Liza Lou replaced by Stasi files; 03, 04, 06 band 7) -> safety.
- 15:39 PROMOTED central_ideas_and_details_b2 (six; safety 0 flagged).
- 15:40 PROMOTED cross_text_connections_b2 (six; CTC done for w5) and words_in_context_b2 (review); safeties 0 flagged.
- 15:40 writers text_structure_and_purpose_b5, rhetorical_synthesis_b5, boundaries_b5 launched (TSP, RS, Bnd now fully started); 7 batches queued.
- 15:46 words_in_context_b3 written (24, done) -> reviewer (band of 05, two Cather works).

## PAUSED 2026-10-27 (user: "pause and save every bit of progress") - how to resume

All agents stopped; none running. Every wave and bank JSON file parses; `SATF_EMAIL_ONLY=0 PYTHONPATH=. python3
server/checks/rw_bank.py` passes. R&W bank 4,233 locally (494 w5 live, 22 of 48 batches promoted). Not deployed
(prod still 3,433 from 10-20), not committed.

- **Written, need review** (reviewers were stopped mid-run; the reviewer prompt keeps items that already carry
  `review`): command_of_evidence_b2, command_of_evidence_b3, words_in_context_b3, text_structure_and_purpose_b3,
  rhetorical_synthesis_b3, transitions_b3. Carry each batch's reviewer notes from the log above.
- **Partly written:** command_of_evidence_b4 (12/22). Writer prompt continues the file.
- **Not started** (19 in all; writers for many were stopped before saving, so claims.txt may already hold their
  `.w5bN_` subjects, which the writer prompt tells them to reuse): inferences_b4, command_of_evidence_b5 to b7,
  words_in_context_b4 to b8, text_structure_and_purpose_b4, b5, rhetorical_synthesis_b4, b5, transitions_b4,
  boundaries_b4, b5, form_structure_and_sense_b3 to b5. `queue_held.txt` lists the 7 that never had a writer.
- Prompts: `writer_prompt.txt`, `reviewer_prompt.txt` in this folder (fill `<skill>`, `<b>`, `<batch>`; point the
  scratch path at the new session's scratchpad). Lead steps as above (`wave_lead.py prep|finish`, WAVE=w5).
- Registry: copy `spec/rw/waves/scripts/reg.py` into the new scratchpad (it keeps running.json beside itself), cap 20 agents.
- Wave 4 leftovers are unchanged (see the PAUSED section of spec/rw/waves/w4/RUNBOOK.md); run them only if the
  user asks.
- 16:19 COMMITTED and pushed (b9cd45d, 86b4083, d6d9284). RESUMED wave 5: 6 reviewers (CoE b2, b3, WiC b3, TSP b3, RS b3, Trn b3) and 13 writers (Inf b4, CoE b4 to b5, WiC b4, b5, TSP b4, b5, RS b4, b5, Trn b4, Bnd b4, b5, FSS b3); 7 queued in queue_held.
- 16:37 rhetorical_synthesis_b3 reviewed (19 pass, 5 fixed; 05 Lazo repeated live Noguchi voluntary-camp item, now Manjiro; 15 guardian dogs and 23 sea ice replaced as twins; all 5 hard band 7) -> safety + gate1, gate2 queued.
- 16:39 PROMOTED rhetorical_synthesis_b3 (gate {"band6": 0.75, "band7": 0.72, "ours": 0.77, "rule": "six"}; safety 0 flagged).
- 16:41 rw_bank check failed after the RS b3 promote: its fixture wanted a type with exactly 3 items and none is left; server/checks/rw_bank.py now takes the smallest type with 3+ (passes; not yet committed). transitions_b3 reviewed (19 pass, 4 fixed; 02 solitary-bee twin, 03 Invisible Cities, 07 Sacred Cenote, 08 pigeon treadmill replaced; 02, 04 band 7) -> solves.
- 16:43 PROMOTED transitions_b3 (gate {"band6": 0.57, "band7": 0.37, "ours": 0.56, "rule": "six"}; safety 0 flagged). Writer form_structure_and_sense_b4 launched.
- 16:43 PROMOTED transitions_b3 (above). command_of_evidence_b2 reviewed (18 pass, 4 fixed; 10 pollinator-exclusion twin replaced by rare earth abundance; 03, 04, 08 band 7) -> solves.
- 16:45 PROMOTED command_of_evidence_b2 (gate {"band6": 0.8, "band7": 0.79, "ours": 0.77, "rule": "review"}; safety 0 flagged). words_in_context_b3 reviewed (19 pass, 5 fixed; 04 Kaptchuk open-label placebo was official CoE a95075c5, now de Araujo sweet-blind mice; 05 Cather now Austen Persuasion; 01, 02, 04, 05 band 7) -> safety. Writers command_of_evidence_b6, words_in_context_b6 launched.
- 16:46 PROMOTED words_in_context_b3 (review; safety 0 flagged).
- 16:46 writer form_structure_and_sense_b5 launched (FSS fully started).
- 16:47 command_of_evidence_b3 reviewed (10 pass, 10 fixed, 2 removed: 03 pottery residues (saturated) and 22 early computers (round-1 subject); 08 student conclusion narrowed; 01, 05, 07, 08, 10 band 7; 06, 09 band 6 under target 7) -> safety + gate1, gate2 queued. Two cells (T1_compete hard, Q1_P3 easy) left for a top-up.
- 16:47 text_structure_and_purpose_b3 reviewed (12 pass, 8 fixed; 03 1918 flu replaced by Augustine/Ambrose silent reading (Knox 1968); 05 hibernation clone replaced by Nigeria oil vs Botswana diamonds; 01, 02, 03 band 7) -> solves queued. CoE b3 gate2 launched.
- 16:49 PROMOTED command_of_evidence_b3 20/20 (gate {"band6": 0.82, "band7": 0.8, "ours": 0.8, "rule": "review"}; safety 0 flagged). Writer command_of_evidence_b7 launched.
- 16:50 PROMOTED text_structure_and_purpose_b3 (gate {"band6": 0.83, "band7": 0.75, "ours": 0.84, "rule": "six"}; safety 0 flagged).
- 16:50 writers words_in_context_b7, b8 launched: every w5 batch now has an agent or is promoted. Queue empty. w5 live 627, bank 4,366.

## PAUSED again 2026-10-27 (user: "pause and save every bit of progress") - how to resume

All 20 agents stopped (every stop confirmed); none running. Every wave and bank JSON file parses; the bank check
(`SATF_EMAIL_ONLY=0 PYTHONPATH=. python3 server/checks/rw_bank.py`) passes. R&W bank 4,366 locally (627 w5 live,
28 of 48 batches promoted). Prod still 3,433. Commits up to d6d9284 are pushed; everything after (the 6 batches
promoted since, claims.txt, WAVE.md themes, this log, server/checks/rw_bank.py fixture fix) is not committed.

- **Nothing written waits for review.** All 20 remaining batches are writers, every one stopped mid-run:
  - partly written (the writer prompt continues the file): command_of_evidence_b4 (12/22), command_of_evidence_b5
    (5/22), transitions_b4 (6/22), boundaries_b4 (11/25); command_of_evidence_b6 has a file with 0 items.
  - no items saved yet (claims.txt may already hold their `.w5bN_` subjects, which the prompt tells them to reuse):
    inferences_b4, command_of_evidence_b7, words_in_context_b4 to b8, text_structure_and_purpose_b4, b5,
    rhetorical_synthesis_b4, b5, boundaries_b5, form_structure_and_sense_b3 to b5.
- Removed by reviewers so far (top up at the end if the 5,000 count needs it): CoE b1 05, CoE b3 03 and 22, Inf b4 07 (lead: bomb-pulse twin of a live S3 item), CoE b7 14 (Q2_P4 medium).
- Resume: copy `spec/rw/waves/scripts/reg.py` into the new scratchpad, launch writers with `writer_prompt.txt`
  (scratch path replaced), cap 20, then review and solve as above. `queue_held.txt` is empty (every batch above is
  simply relaunched as a writer).
- 19:56 RESUMED (user 'resume'): 19 writers launched, form_structure_and_sense_b5 queued.
- 20:22 boundaries_b4 written (25, done; the 11 earlier hard items were reworded to lift register) -> reviewer.
- 20:25 transitions_b4 written (22, done; 8 inherited claims withdrawn as twins/famous) -> reviewer.
- 20:26 rhetorical_synthesis_b4 written (24, done; AUD_FAM and SPEC hard band 6, no band-7 officials) -> reviewer.
- 20:28 form_structure_and_sense_b3 written (24, done; Bontecou and Lukyanov withdrawn as twins) -> reviewer.
- 20:31 boundaries_b4 reviewed (23 pass, 2 fixed; 5 band 7; 03 ', though' meaning trap kept as CB f78997cf) -> safety + gate1, gate2 queued.
- 20:31 rhetorical_synthesis_b5 written (23, done; 3 inherited claims replaced) -> reviewer (break the rating-scale cluster; check named Karmarkar and Bollinger finding).
- 20:32 boundaries_b4 safety flagged 03 (Xenoturbella): D 'all, though' called defensible as a conjunction; lead: D makes the DNA-source clause a concession, but that clause is the reason, so D fails on meaning (CB band-7 f78997cf shape; same call as w4b1_04, w4b5_04). Override on finish.
- 20:32 Bnd b4 gate2 and writer form_structure_and_sense_b5 launched; queue empty.
- 20:33 form_structure_and_sense_b4 (24) and words_in_context_b4 (24; Megaponera and Waldfogel replaced) written -> reviewers.
- 20:34 PROMOTED boundaries_b4 25/25 (gate {"band6": 0.79, "band7": 0.42, "ours": 0.58, "rule": "review"}); 03 lead_override recorded.
- 20:35 command_of_evidence_b4 written (22, done; five kept passages reworded for register; writer ran one read-only git status by mistake, nothing changed) -> reviewer.
- 20:36 boundaries_b5 written (25, done; bluefin auction withdrawn, Wason task kept for a fame call) -> reviewer.
- 20:42 transitions_b4 reviewed (18 pass, 4 fixed; 15 sand mandala twin of live thangka item, now weather balloon launch; 01, 03 band 7) -> safety + gate1, gate2 queued.
- 20:43 form_structure_and_sense_b3 reviewed (22 pass, 2 fixed; 02 B defensible, rebuilt; 12 Burushaski twin of live Zulu noun classes, now Trans-Australian Railway straight) and rhetorical_synthesis_b4 reviewed (19 pass, 5 fixed; 21 Hurrian Hymn twin of live Seikilos, now empress tree) -> solves (RS b4 queued).
- 20:44 words_in_context_b5 written (24, done) -> reviewer queued; RS b4 safety launched.
- 20:44 PROMOTED transitions_b4 (gate {"band6": 0.64, "band7": 0.33, "ours": 0.44, "rule": "review"}; safety 0 flagged); Transitions done for w5. WiC b5 reviewer launched.
- 20:45 PROMOTED form_structure_and_sense_b3 (gate {"band6": 0.84, "band7": 0.71, "ours": 0.77, "rule": "review"}) and rhetorical_synthesis_b4 (six, no gate); safeties 0 flagged.
- 20:48 form_structure_and_sense_b4 reviewed (12 pass, 12 fixed; 08 'they' ambiguity fixed; 02 rebuilt to band 7) -> solves. Kim Whanki also used by WiC w5b8_08 (claimed later): told the WiC b8 writer to replace it.
- 20:50 PROMOTED form_structure_and_sense_b4 (gate {"band6": 0.8, "band7": 0.7, "ours": 0.77, "rule": "six"}; safety 0 flagged; gate doubt g018 Kim Whanki dangling modifier checked, key B sound).
- 20:50 rhetorical_synthesis_b5 reviewed (18 pass, 5 fixed; Karmarkar and Bollinger finding confirmed, data claim narrowed to one store; 15 Colon Classification and 23 VEI replaced; 01, 02, 04 band 7) -> solves.
- 20:50 text_structure_and_purpose_b5 written (20, done; Paris schoolyards twin withdrawn) -> reviewer.
- 20:51 PROMOTED rhetorical_synthesis_b5 (gate {"band6": 0.77, "band7": 0.82, "ours": 0.86, "rule": "six"}; safety 0 flagged); Rhetorical Synthesis done for w5.
- 20:52 command_of_evidence_b4 reviewed (17 pass, 5 fixed; 08 had a second defensible option, rebuilt; 01 'rather than' overclaim narrowed; 02, 04 band 7) -> solves.
- 20:53 command_of_evidence_b6 written (22, done; Q1_P3 hard band 6, no band-7 officials) -> reviewer.
- 20:54 PROMOTED command_of_evidence_b4 (gate {"band6": 0.83, "band7": 0.79, "ours": 0.7, "rule": "review"}; safety 0 flagged; lead changed 10's key 'roughly doubled' to 'grew by at least 85 percent'). words_in_context_b6 written (23, done) -> reviewer.
- 20:55 inferences_b4 written (19, done; Inferences fully written) -> reviewer.
- 20:55 boundaries_b5 reviewed (18 pass, 7 fixed; 11 Wason task famous, now Baker-baker paradox; 15 Proto-Sinaitic (script cluster) now Coade stone; 5 band 7) -> solves.
- 20:56 words_in_context_b8 written (23, done; Kim Whanki and Lake Hillier swapped out) -> reviewer.
- 20:58 PROMOTED boundaries_b5 (gate {"band6": 0.82, "band7": 0.43, "ours": 0.49, "rule": "review"}; safety 0 flagged; lead checked gate doubts g025 Fermi bubbles fronted appositive (key B) and g009 Shosoin colon (key D)); Boundaries done for w5. command_of_evidence_b7 written (22, done) -> reviewer.
- 20:58 words_in_context_b4 reviewed (19 pass, 5 fixed; 06 spaghetti fracture famous, now Landers triggered quakes; 01 Munduruku twin of live w3b6_02, now Braille readers; 02 reads band 6 under target 7) -> safety. text_structure_and_purpose_b4 written (20, done) -> reviewer.
- 20:59 PROMOTED words_in_context_b4 (rule review, no gate; safety 0 flagged).
- 21:02 words_in_context_b7 written (23, done; WiC fully written) -> reviewer.
- 21:06 words_in_context_b5 reviewed (23 pass, 1 fixed: 11 Chokwe sand stories too close to live FSS w1b5_11, reviewer wrote konbini item; lead added it as a one-item blind check in extra/) -> safety. Anolis added to WAVE.md saturated themes.
- 21:07 PROMOTED words_in_context_b5 (rule review, no gate; safety 0 flagged; replacement 11 blind-solved to its key).
- 21:10 words_in_context_b6 reviewed (20 pass, 3 fixed; 12 pig joystick overclaim 'demonstrating ... understood' narrowed to the paper; 08 Adams source swapped to AIC page; 02, 03 band 7) -> safety.
- 21:10 command_of_evidence_b5 written (22, done; 17 new + 5 kept hard) -> reviewer (asked to check 20's invented quotations are not put on a named person).
- 21:11 PROMOTED words_in_context_b6 (rule review, no gate; safety 0 flagged).
- 21:13 inferences_b4 reviewed (12 pass, 7 fixed; all 9 hard band 6 as planned). Lead removed 07 (ivory bomb-pulse dating: same carbon-14 setup as live inferences.S3.medium Hendriks, same template); kept 19 Repenomamus (overlap only with an official WiC item, different skill) -> safety (18 items). Quilts added to saturated themes.
- 21:14 PROMOTED inferences_b4 (rule six, no gate; safety 0 flagged); Inferences done for w5.
- 21:18 text_structure_and_purpose_b5 reviewed (11 pass, 9 fixed; 01 stick insect through bird guts twin of live Bnd w1b1_06, now Iliamna Lake seals; 01-03 band 7) -> solves.
- 21:18 words_in_context_b7 reviewed (22 pass, 1 fixed: 07 distractor 'contingent on' had a second reading, now 'analogous to'; 01, 04, 05 band 7) -> safety, plus 07 as a one-item blind check.
- 21:18 form_structure_and_sense_b5 written (24, done; 5 subjects swapped pre-review) -> reviewer. All 48 w5 batches now written.
- 21:19 PROMOTED text_structure_and_purpose_b5 (gate {"band6": 0.83, "band7": 0.8, "ours": 0.87, "rule": "six"}; safety 0 flagged; gate doubts were official anchors without underlines). command_of_evidence_b6 reviewed (14 pass, 8 fixed; 14 Bosten Lake rebuilt from Table 1, conclusion overreached; 16 bird/bat netting twin of live TSP w3b1_25, now PNG chords; 02, 04, 06 band 7) -> solves.
- 21:20 PROMOTED words_in_context_b7 (rule review, no gate; safety 0 flagged; 07 blind-solved to its key).
- 21:20 PROMOTED command_of_evidence_b6 (gate {"band6": 0.84, "band7": 0.8, "ours": 0.83, "rule": "six"}; safety 0 flagged).
- 21:27 text_structure_and_purpose_b4 reviewed (16 pass, 4 fixed; 13 Corrothers 'The Negro Singer' judged unsuitable and a same-poet cluster, now Lazarus 'Echoes'; 04 band 7) -> solves, plus 13 as a one-item blind check.
- 21:28 command_of_evidence_b7 reviewed (11 pass, 10 fixed, 1 removed: 14 Indonesia clean cooking twin of live w4b2_16; 19 Obata repeated two official items, now Rosa Bonheur; 01 Fersen overstated, rebuilt to band 7; 08 soap 1% -> 0.1%; 01, 03, 07, 08 band 7) -> solves, plus 19 as a one-item blind check.
- 21:29 PROMOTED text_structure_and_purpose_b4 (gate {"band6": 0.84, "band7": 0.8, "ours": 0.86, "rule": "six"}; safety 0 flagged; 13 Lazarus blind-solved to its key; gate doubts all official anchors); Text Structure done for w5.
- 21:30 PROMOTED command_of_evidence_b7 (gate {"band6": 0.83, "band7": 0.76, "ours": 0.84, "rule": "six"}; safety 0 flagged; 19 Bonheur blind-solved to its key, lead dropped C's 1853 Salon date that read as a clash with 1855).
- 21:32 words_in_context_b8 reviewed (7 pass, 16 fixed; overclaims narrowed in 09 orchid bees, 05 zombie flies, 18 Lozen, 04 Bemis, 11 Hyecho; 06 Sosa and 12 palm-leaf swapped to social/natural science; 02, 03 band 7; reviewer ran one read-only git status, nothing changed) -> safety, plus 06/09/12/16 as a blind check.
- 21:33 command_of_evidence_b5 reviewed (13 pass, 9 fixed; 20 Jovita Idar repeated official Transitions 2b5f4bdc, now Josefa Llanes Escoda, quotations unnamed; 06, 10 hardened; 01, 03, 05-10 band 7; reviewer ran one read-only git show, tree checked unchanged) -> solves, plus 20 as a one-item blind check.
- 21:35 PROMOTED words_in_context_b8 (rule review, no gate; safety 0 flagged; 06, 09, 12, 16 blind-solved to their keys); WiC done for w5.
- 21:35 PROMOTED command_of_evidence_b5 (gate {"band6": 0.82, "band7": 0.81, "ours": 0.75, "rule": "review"}; safety 0 flagged; 20 Escoda blind-solved to its key); CoE done for w5.
- 21:40 form_structure_and_sense_b5 reviewed (4 pass, 20 fixed; concept twins replaced: 09 Apocalypse Tapestry (official Bayeux) -> porcupine quills, 10 Anangu sand stories (live Chokwe sona) -> Lanzarote pit vineyards, 12 Stolzl (third Bauhaus weaver) -> Ohno kanban; 18 tubeworm sentence rewritten; 01, 06 band 7) -> solves, plus 09/10/12/18 as a blind check.
- 21:42 PROMOTED form_structure_and_sense_b5 (gate {"band6": 0.84, "band7": 0.69, "ours": 0.73, "rule": "review"}; safety 0 flagged; 09, 10, 12, 18 blind-solved to their keys). WAVE 5 COMPLETE: 48 of 48 batches promoted.

## DONE 2026-10-27 late night

All 48 batches promoted: 1,080 w5 items live in satbank/rw/<skill>__w5.json; R&W bank 4,819 locally, `tools/check_rw.py` 0 problems, `server/checks/rw_bank.py` passes. Prod still 3,433 (not deployed). Removed cells, if a top-up is wanted: CoE b1 05, CoE b3 03 and 22, Inf b4 07, CoE b7 14. Wave 4 still has 8 paused batches (182 items; see w4/RUNBOOK.md PAUSED) that are needed to reach 5,000.
