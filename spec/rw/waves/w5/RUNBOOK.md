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
