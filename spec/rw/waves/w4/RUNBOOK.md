# Wave 4 runbook (lead)

Started 2026-10-20 10:20 after the user: "but we should have 5k in total". 5,000-item target; 2,850 live after
wave 3. Wave 4 is 1,075 items in 46 batches (`plan.json`, frozen by `make_plan.py 4`); wave 5 is the rest (about
1,075), planned with `make_plan.py 5` once wave 4 is promoted (rw_plan recomputes from live counts).

**Not done without the user:** deploy to prac.fsat.io, git commit.

Same procedure as `spec/rw/waves/w3/RUNBOOK.md` (stage table, band rule, prompts), with these changes:
- Scripts: `WAVE=w4 python3 spec/rw/waves/scripts/wave_status.py`; lead steps
  `WAVE=w4 W3_SCRATCH=<SP> python3 spec/rw/waves/scripts/wave_lead.py prep|finish <batch>`.
- `<SP>` = `/private/tmp/claude-501/-Users-workingmyassof-freshbot-satbank/11932fea-c5c4-475d-bd5f-041033f1446a/scratchpad/w4`
  (registry `<SP>/reg.py`, `running.json`, `queue.json`).
- Every prompt adds: "Do not launch sub-agents. Web search may be used up: fetch pages directly. Never put the
  user's email or any personal data into a web request." WAVE.md now holds the wave-3 lessons; writers read them.
- Cap: 20 agents at once; keep 18 to 19 in the registry.

## Log

- 10:20 plan frozen (1,075 items, 46 batches); WAVE.md wave-3 lessons added; wave_status.py / wave_lead.py.
- 10:17 18 writers launched (all b1 + b2 of CID, Inf, CoE, WiC, TSP, RS, Bnd, FSS); 28 batches queued in <SP>/queue.json.
- 10:48 boundaries_b1 written (25, done; item 12 band 6, no band-7 S4 officials) -> reviewer; writer cross_text_connections_b2 launched.
- 10:50 boundaries_b2 written (25, done; S1_comma_conj, S4_compound band-7 cells written band 6) -> reviewer. FOR WAVE 5: make_plan.py deals band 7 to templates with no band-7 officials (S4_subj_verb, S1_comma_conj, S4_compound); skip those when planning.
- 10:52 tick: 2 in review (Bnd b1, b2); RS b1, Trn b1, FSS b1 written, writers still handing back; reading writers still researching (0 saved). 19 running, 27 queued.
- 10:54 form_structure_and_sense_b1 written (24, done; 07 band 6) -> reviewer. Writer had edited claims.txt in place with sed: every saved w4 item id still has its claim; WAVE.md now says claims.txt is append-only.
- 10:55 rhetorical_synthesis_b1 written (24, done; AUD_FAM band 6) -> reviewer.
- 10:58 boundaries_b1 reviewed (22 pass, 3 fixed) -> safety + 2 gates. transitions_b1 written (23, done; K1_grant_turn, C1_two_subject band 6; medium register at floor) -> reviewer on next free slot (cap).
- 10:58 reg.py now counts agents (comma ids), not batches; 20 agents at cap. Pending on next free slot: transitions_b1 reviewer.
- 10:58 form_structure_and_sense_b2 written (24, done; R3_appositive, R2_finite_main, R2_to_inf band 6) -> reviewer.
- 10:59 PROMOTED boundaries_b1 (first w4 batch). Gate doubts on w4b1_02 (Chan Chan, D: the appositive opens a new sentence) and w4b1_06 (Hunga Tonga, A: colon; D and C leave a fragment) checked by lead: keys sound.
- 11:00 boundaries_b1 w4b1_04 (rock glaciers): safety and both gates chose the '; however,' trap; lead upheld key ', however;' (CB band-7 adverb shape, band7/boundaries.md 3.1), lead_override recorded, promoted 25/25. rhetorical_synthesis_b2 written (24, done) -> reviewer.
- 11:02 boundaries_b2 reviewed (22 pass, 3 fixed; 09 rebuilt to the band-6 ', and' shape) -> safety + gate1; gate2 on next free slot.
- 11:04 PROMOTED boundaries_b2 25/25 (gate 0.71/0.40/ours 0.63 -> six). w4 live 50. Writer words_in_context_b3 launched.
- 11:05 form_structure_and_sense_b2 reviewed (21 pass, 3 fixed; 04 had a pronoun error in its passage) -> safety; gates 1 and 2 pending a slot (<SP>/pending_solves.json).
- 11:05 rhetorical_synthesis_b1 reviewed (21 pass, 3 fixed) -> prepped; safety + gates pending a slot. FSS b2 gate1 launched.
- 11:06 FSS b2 safety in (0 flagged), gate2 launched. inferences_b1 written (24, done; all premises fetched) -> reviewer. Pending: RS b1 safety + 2 gates.
- 11:06 transitions_b1 reviewed (21 pass, 2 fixed; 05 hardened to band 7) -> prepped, solves pending. RS b1 safety launched.
- 11:06 form_structure_and_sense_b1 reviewed (18 pass, 6 fixed; 23 had a second defensible tense) -> prepped, solves pending. RS b1 gate1 launched.
- 11:07 PROMOTED form_structure_and_sense_b2 24/24 (gate 0.84/0.72/ours 0.76 -> review). w4 live 74. Transitions b1 safety + 2 gates launched; pending FSS b1 solves.
- 11:07 PROMOTED rhetorical_synthesis_b1 24/24 (gate 0.79/0.83/ours 0.84 -> six). w4 live 98. Trn b1 safety in (0 flagged). FSS b1 safety + 2 gates launched.
- 11:08 PROMOTED transitions_b1 23/23 (gate 0.60/0.38/ours 0.63 -> six). w4 live 121. FSS b1 safety in (0 flagged), gate2 launched. Writer central_ideas_and_details_b3 launched.
- 11:08 central_ideas_and_details_b1 written (25, done; all premises fetched) -> reviewer. Told CID b2 writer to replace w4b2_01 (torrent frog) since b1 item 11 (Bornean rock frog, stream noise) claimed first.
- 11:09 PROMOTED form_structure_and_sense_b1 24/24 (gate 0.83/0.75/ours 0.65 -> review; both gates took the dangling-modifier trap on w4b1_01, lead checked key B sound). w4 live 145. inferences_b2 written (24) -> reviewer; writers TSP b3, RS b3 launched.
- 11:10 rhetorical_synthesis_b2 reviewed (19 pass, 5 fixed; 19 Moksha Patam duplicated official FSS 2ee50d41, replaced) -> safety; gates pending.
- 11:12 PROMOTED rhetorical_synthesis_b2 24/24 (gate 0.84/0.85/ours 0.84 -> review). w4 live 169. Writer boundaries_b3 launched.
- 11:13 command_of_evidence_b1 written (22, done; 09 band 6) -> reviewer.
- 11:14 words_in_context_b1 written (24, done) -> reviewer, told to break the 'first African American' twin frame (13/15) and move two of a 7-item topic cluster to other fields.
- 11:15 central_ideas_and_details_b2 written (24, done; frog item replaced by orpiment) -> reviewer (4 unconfirmed minor details to confirm or soften). Another early sed edit to claims.txt: every saved w4 id still claimed.
- 11:15 command_of_evidence_b2 written (22, done) -> reviewer.
- 11:17 tick: 7 promoted (169 live), 7 in review, TSP b2 and WiC b2 written (writers handing back), 11 writers running; 20 agents at cap, 19 queued.
- 11:18 words_in_context_b2 written (24, done; M1 band-7 key rank 3,913) -> reviewer.
- 11:20 cross_text_connections_b1 written (18, done) -> reviewer. TSP b2 writer told to replace w4b2_07 (Bratsberg-Rogeberg claimed first by CTC w4b1_07).
- 11:22 central_ideas_and_details_b1 reviewed (21 pass, 4 fixed; translator credited, 05 kept as third social-misprediction item) -> safety (no gate, CID rule six).
- 11:22 PROMOTED central_ideas_and_details_b1 25/25 (six). w4 live 194. Writer form_structure_and_sense_b3 launched.
- 11:24 inferences_b2 reviewed (15 pass, 7 fixed, 2 removed: sea otters duplicated official 8584f3ce; cabdriver study too famous) -> safety (no gate).
- 11:24 PROMOTED inferences_b2 22/22 (six). w4 live 216. Writer transitions_b3 launched.
- 11:25 central_ideas_and_details_b2 reviewed (14 pass, 10 fixed; 4 hard items read too easy; Homar detail cut) -> safety.
- 11:26 PROMOTED central_ideas_and_details_b2 24/24 (six). w4 live 240. Writer command_of_evidence_b4 launched.
- 11:26 text_structure_and_purpose_b2 written (25, done; w4b2_07 replaced by riderless bicycles) -> reviewer.
- 11:28 command_of_evidence_b1 reviewed (16 pass, 6 fixed; 01 option was the key's exact opposite) -> safety; gates pending.
- 11:29 inferences_b1 reviewed (16 pass, 8 fixed; 11 replaced in place: Madeira mice duplicated official RS 296801d2, now Chatterton) -> safety. WAVE.md: saturated-themes list added (forgery by anachronism 5, social mispredictions 3, termite mounds 3, Navajo weaving 3).
- 11:29 PROMOTED inferences_b1 24/24 (six). w4 live 264. CoE b1 gate2 launched.
- 11:30 words_in_context_b1 reviewed (20 pass, 4 fixed; 13 and 15 replaced, cluster 7 -> 5; species name corrected) -> safety. Kept 06 at band 7 (all four options past 10,000, mean log above band-7 mean). Writer words_in_context_b4 launched.
- 11:31 PROMOTED command_of_evidence_b1 22/22 (gate 0.81/0.77/ours 0.77 -> review). w4 live 286. Writer text_structure_and_purpose_b4 launched.
- 11:31 PROMOTED words_in_context_b1 24/24 (review). w4 live 310. Writer rhetorical_synthesis_b4 launched.
- 11:31 command_of_evidence_b2 reviewed (15 pass, 7 fixed; 19 cuttlefish duplicated official WiC 710799ae, now goats) -> safety; gates pending.
- 11:32 CoE b2 w4b2_09 (Tunisia/Morocco enrollment): passage presupposed a Moroccan crossover the table does not show; lead reworded ('long before it even matched'). Safety in (0 flagged).
- 11:32 text_structure_and_purpose_b1 written (25, done; P_profile, S13 band 6) -> reviewer pending a slot. CoE b2 gates launched.
- 11:34 PROMOTED command_of_evidence_b2 22/22 (review). w4 live 332. cross_text_connections_b2 written (17, done) -> reviewer; TSP b1 reviewer launched; writer boundaries_b4 launched.
- 11:35 words_in_context_b2 reviewed (22 pass, 2 fixed; 05 to band 6, only 04 band 7) -> safety.
- 11:35 PROMOTED words_in_context_b2 24/24 (review). w4 live 356. Writer form_structure_and_sense_b4 launched.
- 11:38 cross_text_connections_b1 reviewed (11 pass, 6 fixed, 1 removed: 15 autumn-leaves sunscreen was the round-1 tell subject; 02 Cameron misquote restored) -> safety.
- 11:38 PROMOTED cross_text_connections_b1 17/17 (six). w4 live 373. Writer transitions_b4 launched.
- 11:40 transitions_b2 written (23, done) -> reviewer.
- 11:44 text_structure_and_purpose_b2 reviewed (18 pass, 7 fixed; Clare source line corrected to 1832; bicycle claim confirmed on PubMed) -> safety; gates pending.
- 11:46 PROMOTED text_structure_and_purpose_b2 25/25 (gate 0.84/0.73/ours 0.88 -> six). w4 live 398. Writer command_of_evidence_b5 launched.
- 11:46 transitions_b2 reviewed (19 pass, 4 fixed; 15 had a defensible 'Similarly') -> safety; gates pending.
- 11:47 cross_text_connections_b2 reviewed (9 pass, 8 fixed; Ossian reframed away from forgery-exposure) -> safety.
- 11:47 rhetorical_synthesis_b3 written (24, done) -> reviewer.
- 11:47 PROMOTED cross_text_connections_b2 17/17 (six); Cross-Text done for w4. w4 live 415. Trn b2 safety in (0 flagged; 'Alternatively' key is the U1_culmination_alt template, fine), gates launched.
- 11:48 PROMOTED transitions_b2 23/23 (gate 0.66/0.48/ours 0.68 -> six). w4 live 438. Writers words_in_context_b5, rhetorical_synthesis_b5 launched.
- 11:50 text_structure_and_purpose_b1 reviewed (16 pass, 8 fixed, 1 removed: 11 gliding ants duplicated live FSS w1b3_03) -> safety; gates pending.
- 11:50 central_ideas_and_details_b3 written (24, done) -> reviewer. TSP b1 safety in (0 flagged), gate1 running, gate2 pending.
- 11:52 tick + PROMOTED text_structure_and_purpose_b1 24/24 (gate 0.85/0.76/ours 0.86 -> six). w4 live 462 from 20 batches. In flight: CID b3, RS b3 reviews; Bnd b3 written (writer handing back); 7 writers. Writer boundaries_b5 launched; 6 queued.
- 11:56 boundaries_b3 written (25, done) -> reviewer (check the named Ivanova cicada-wing claim).
- 12:00 rhetorical_synthesis_b3 reviewed (20 pass, 4 fixed; 01 fog collectors repeated live fog items, now Nijo nightingale floors) -> safety; gates pending.
- 12:02 central_ideas_and_details_b3 reviewed (20 pass, 4 fixed) -> safety. RS b3 safety in (0 flagged), gate1 running, gate2 pending.
- 12:04 PROMOTED central_ideas_and_details_b3 24/24 (six); CID done for w4. w4 live 486. FSS b3 (24) and WiC b3 (24) written -> reviewers; RS b3 gate2 launched; writer form_structure_and_sense_b5 launched.
- 12:13 PROMOTED rhetorical_synthesis_b3 24/24 (gate 0.81/0.83/ours 0.87 -> six). w4 live 510. Wave of handbacks: boundaries_b3 reviewed (23 pass, 2 fixed; Atacama item moved to Sardine Run) -> safety + 2 gates; written -> reviewers: FSS b4, CoE b3, RS b4, Inf b3, Trn b3 (Braess fame call), Bnd b4 (told to replace Man'yoshu w4b4_04, b3 claimed first), TSP b3. transitions_b4 written (22) -> reviewer pending a slot.
- 12:13 form_structure_and_sense_b3 reviewed (22 pass, 2 fixed) -> safety; gates + Trn b4 reviewer pending.
- 12:15 Bnd b3 gate1 doubts on w4b3_02 (Figari) and w4b3_01 (Foguang) checked by lead: other options splice; keys sound. FSS b3 gates running.
- 12:15 PROMOTED boundaries_b3 25/25 (gate 0.74/0.44/ours 0.62 -> six). w4 live 535. words_in_context_b3 reviewed (24 pass, 5 band 7) -> safety. Writer command_of_evidence_b6 launched.
- 12:16 PROMOTED words_in_context_b3 24/24 (review) and form_structure_and_sense_b3 24/24 (gate 0.86/0.78/ours 0.78 -> review; both gates took the comma-splice trap on w4b3_07, absolute-phrase key D sound). w4 live 583. Writers command_of_evidence_b7, words_in_context_b6, words_in_context_b7 launched; 1 queued.
- 12:17 tick: 25 promoted (583 live), 8 in review, RS b5 written (writer handing back), 10 writers; 20 agents at cap; 1 queued (WiC b8).

## PAUSED 2026-10-20 ~12:20 (user out of tokens) - how to resume

All agents stopped, overnight-style timer cancelled, registry (`<SP>/running.json`) cleared. Every staged and bank
JSON file parses; `server/checks/rw_bank.py` passes. Not deployed, not committed.

State: 25 of 46 batches promoted (583 w4 items live; R&W bank 3,433 locally). Remaining 21 batches:
- **Written, need review** (reviewers were stopped mid-run; the reviewer prompt keeps items that already carry
  `review` and reviews the rest): inferences_b3, command_of_evidence_b3, text_structure_and_purpose_b3,
  rhetorical_synthesis_b4, rhetorical_synthesis_b5, transitions_b3, transitions_b4, boundaries_b4,
  form_structure_and_sense_b4. Carry the per-batch notes in the Log above into each reviewer prompt; in particular
  boundaries_b4 must replace w4b4_04 (Man'yoshu, claimed first by w4b3_04) and transitions_b3 judges Braess (04).
- **Partly written** (writer prompt continues an existing file): command_of_evidence_b4 (17/22),
  words_in_context_b4 (18/24), text_structure_and_purpose_b4 (7/25), boundaries_b5 (5/25),
  command_of_evidence_b5 (0/22 saved, some claims may exist).
- **Not started**: command_of_evidence_b6, b7; words_in_context_b5 (claims exist, no file), b6, b7, b8;
  form_structure_and_sense_b5. A stopped writer may have left claim lines with no items: the next writer for that
  batch should reuse its own earlier claims (grep claims.txt for the batch id, e.g. `w4b5_`).
- Then wave 5: `python3 spec/rw/waves/scripts/make_plan.py 5` (skip band 7 for templates with no band-7 officials,
  see the 10:50 note), and run it the same way until the bank reaches 5,000.

To restart: ask Claude to "resume wave 4 from spec/rw/waves/w4/RUNBOOK.md". Writer prompt template:
`<SP>/writer_prompt.txt`; reviewer/solver prompts as used above (w3 RUNBOOK has the originals).
- 13:14 DEPLOYED (deploy/push.sh, user's request): prod R&W bank 3,433 = waves 1-3 + 25 promoted w4 batches. Wave 4 still paused at 25/46.
