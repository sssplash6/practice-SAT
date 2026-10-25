# SUGGESTIONS.md: where each item comes from

For the builders. Paths are under premium/; `p/x` = pages/x.md; `§` = section, items by number. REF = REFERENCES.md.
Recipes (CSS values, timings, hooks) live in the sources; SUGGESTIONS.md only names the change.

Token alias: `--shadow-1..5` = REF §3 R4 `--e0..--e4` (1 ring at rest, 2 clickable/hover, 3 hero, 4 menus, popovers,
toasts: replaces `--shadow-float`, 5 sheets, palette: replaces `--shadow-pop`). p/me-compete-misc §3 `--shadow-1` is the
hero level (= `--shadow-3` here). Page files' "lift 1px on hover" for `.pill` is overruled by REF §2.4 and MOTION C2: no
transform on button hover; clickable cards may move 1px max (REF R9). Pill hover lightens per REF R1 (dark text gains contrast); DISCOVER B4 overruled. Wrong answers: MOTION F2 (no shake) overrules AUDIT §10.2.
Icons: ICONS §2 (Phosphor pinned at 2b75f3ad12b4) overrules DISCOVER I2 (keep hand-drawn).

## Recommended set

1. Calm Practice: p/practice §2, §8.1-4, §8.7-8; AUDIT §C.3, C.8, C.9, C.12, §12 Practice; DISCOVER §2.0 C1-C3, C6, C7
2. An orange button you want to press: REF §2.3-5, §3 R1, R1b, R2, R3, R10, R11, R19, R23; AUDIT §2.1-4, 2.6-7; MOTION §3.4 C1-C4, C13; DISCOVER §2.2 B1, B2, B4; p/today §4, p/practice §4, p/runner §4, p/tests §4, p/results §4, p/plan §4, p/words §4, p/me-compete-misc §4
3. Air between groups: AUDIT §0 row 5, §C.1, §C rule of thumb; DISCOVER §2.0 C5; p/practice §2 "Space", p/today §2, p/tests §2, p/words §2, p/plan §2, p/runner §2
4. Shadow steps in warm light: REF §2.1-2, 2.7, §3 R4-R6, R22, §5.3-4; AUDIT §0 row 1, §1.1-5, §5.2-3; DISCOVER §2.1 D1, D2, §2.10 K1-K2
5. One hero per page: AUDIT §8, §C.10, §1.8-9; REF R7; p/today §3, p/practice §3, p/tests §3, p/plan §3, p/words §3, p/review §3, p/results §3, p/runner §3, p/me-compete-misc §3
6. Calm first screens everywhere: AUDIT §C (table and rule of thumb), §C.4-7, C.11-14, §12; DISCOVER §2.0 C1-C9, §1 #4-5; p/review §2, §8.1-3; p/tests §2, §8.2-5; p/words §2, §8.1; p/plan §2, §8.2, §8.6; p/results §2, §8.6-7; p/today §2; p/me-compete-misc §2
7. Answers that land: MOTION §3.7 F1-F3, F10-F11; AUDIT §10.1-3, 10.11-13; p/runner §5, §7, §8.1, §8.3, §8.9; DISCOVER §2.6 F2
8. Big hero numbers: AUDIT §0 row 6, §4.1-6, §8.2-4; p/results §3; p/words §3; p/today §3; p/runner §3; p/tests §3
9. Highlights and states: AUDIT §3.1-5, 3.10-11, §2.15; MOTION §3.4 C1; DISCOVER §2.5 H4
10. Things leave, not vanish: MOTION §1, §2, §3.5 S1-S7, §4.1-4.5; AUDIT §7.1-2, 7.7, §11.4-5; REF R16-R18; DISCOVER §2.3 M3, M5, M7, §2.11 Ph5
11. Moments that reward: MOTION §3.7 F4-F9, §3.6 D2, D4, D7; AUDIT §8.3, 8.5-6, §10.4-6; p/runner §3, §7, §8.4; p/results §5.1, §7, §8.2; p/today §7; p/review §5, §8.4; DISCOVER §2.6 F1, §2.7 P3
12. One icon set, filled when active: ICONS §2-5, §11, Shared asks; AUDIT §6.1, 6.4; DISCOVER §2.4 I1-I3, §1 #20-21
13. Drawn marks, not symbols: ICONS §1a, §6; AUDIT §6.2-3; p/runner §6, p/review §6, p/results §6, p/tests §6, p/plan §6, p/words §6, p/today §6, p/me-compete-misc §6
14. Page entry: MOTION §3.1 N1, N2, N4, N7, §3.2 M1-M4; REF R15, §5.5; AUDIT §0 row 4, §7.3, 7.5
15. Data with weight: AUDIT §9.1-6; MOTION §3.6 D3-D7; REF R21; p/results §3, §5.3, §8.3, §8.5
16. Fix the open bugs: see Bugs below

## More

Depth and surfaces
- Sidebar Now card: AUDIT §1.8, §8.9; DISCOVER §2.7 P5
- Question sheet: p/runner §3, §8.2-3; AUDIT §12 Practice session 2
- Shadow on scroll: p/runner §3; p/review §3; p/plan §3 (sticky bars)
- Up and down: REF R22; AUDIT §1.5
- Dark mode depth: AUDIT §5.3-4; REF R4 dark, R5; DISCOVER §2.10 K1-K4
- Figure edge: DISCOVER §2.1 D4

Buttons and controls
- Arrow nudge: REF R23; AUDIT §2.5; p/today §4
- Sliding thumbs: REF R12-13; AUDIT §2.8; MOTION C5-C6; p/results §4; p/me-compete-misc §4 (`C.under`, subnav)
- Drawn checkbox: AUDIT §2.12; p/practice §4; p/today §4; p/tests §4; p/plan §4; MOTION C9
- Fields: AUDIT §2.10-11; p/me-compete-misc §4
- Split buttons: p/results §4; p/review §4
- Quiet menus: p/plan §4; p/tests §4; p/words §4
- Switch and slider: AUDIT §2.13-14; DISCOVER §2.11 Ph3; MOTION C7
- Code boxes: AUDIT §2.16, §12 Sign in; p/me-compete-misc §4
- Confidence trio: AUDIT §2.18
- Phone taps: DISCOVER §2.2 B6

Motion
- Folds open smoothly: MOTION C10; p/today §5, §8.7; p/review §5; p/me-compete-misc §4
- Lists that glide: MOTION §3.3 L1-L4; REF R16; p/words §5 (order ladder)
- Rolling numbers: MOTION D1; REF R14; DISCOVER §2.3 M9, §2.9 N1
- Charts draw in once: MOTION D5-D8; p/results §5.2, 5.4-5; p/me-compete-misc §5 (parent bars)
- Card into page: MOTION N3; AUDIT §7.5, §8.7
- Sidebar morphs: MOTION §3.8 B1-B2
- Phone sheets: MOTION S2; DISCOVER §2.11 Ph2; AUDIT §11.5
- Loading: MOTION M2; AUDIT §9.9; DISCOVER §2.8 E2; REF R20 (shimmer rejected)

Icons and imagery
- Topic glyphs redrawn: ICONS §1f, §7; p/practice §6
- Logo spot drawings: ICONS §9; AUDIT §6.5; p/me-compete-misc §6 (404)
- Sample rows: ICONS §9 (`UI.empty`); p/tests §6; p/me-compete-misc §6; p/review §6
- Kind marks on rows: p/today §6; p/plan §6
- One badge style: ICONS §7 (badges); p/me-compete-misc §6
- Quick in ink: ICONS §1g, §4 (bolt)
- Share image and app icon: ICONS §10; AUDIT §11.8-9, §12 Share
- Route drawing: p/tests §6

Highlights and states
- Unread dots: AUDIT §3.7; p/review §2; MOTION B4
- Your row: AUDIT §3.6, §12 Leaderboard; p/me-compete-misc §4; p/runner §7 (challenge)
- Pick flash: DISCOVER §2.5 H2
- Open item forward: DISCOVER §2.5 H3
- Search matches: AUDIT §3.9; DISCOVER §2.5 H4
- Tooltips: AUDIT §7.8, §11.3; MOTION C11; DISCOVER §2.3 M4
- Keycaps that flash, scrollbars: AUDIT §11.7, §11.1

Feedback and delight
- Saved in place: AUDIT §2.4; MOTION C3; p/tests §4; p/plan §4; p/review §4; p/me-compete-misc §7
- In a row: AUDIT §10.5; p/runner §7
- Mastery moves: AUDIT §10.7; p/runner §5, §7
- Task ticks: p/today §5, §7; p/plan §5, §7, §8.5
- Milestones: DISCOVER §2.7 P3, §1 #1; p/today §7; p/results §7 (new best)
- Counts over percentages: DISCOVER §2.7 P1, §2.0 C8
- Milestone share card: DISCOVER §2.6 F5
- Phone haptics, sound: AUDIT §10.8, §10.10; DISCOVER §4

Per page
- Today: p/today §8
- Session: p/runner §2, §8.5-7; AUDIT §12 Practice session, Session Summary 1
- Review: p/review §8
- Words: p/words §8
- Plan: p/plan §8
- Tests: p/tests §8
- Results and Report: p/results §8
- Profile: p/me-compete-misc §8.6; AUDIT §12 Me
- Compete: p/me-compete-misc §8.4-5, §8.7, §8.9; AUDIT §12 Compete, Leaderboard, Contest
- Sign in, Welcome, Pair: p/me-compete-misc §2, §8.1-2; AUDIT §12 Sign in, Welcome
- Test window: AUDIT §12 Test window; p/runner §3, §5, §8 (test note); MOTION §3.9
- Small pages: AUDIT §12 Help, 404, Settings, Parent; p/me-compete-misc §2

## Rules this relaxes

1-2. AUDIT §0 row 1; REF §5.2-4; DISCOVER §2.1 D2 [call: D3]
3. AUDIT §0 row 2, §5.6; p/results §3; p/me-compete-misc §3 (`--hero-wash`); DISCOVER [call: D6]
4. AUDIT §0 row 3; REF §4 (glow numbers)
5. AUDIT §0 row 3, §11.5-6; p/plan §3; MOTION intro (no blur); REF §4 (never on scrolling content)
6. AUDIT §0 row 4; MOTION header (supersedes DIRECTION 7); REF §5.5
7. MOTION §2 (springs)
8. AUDIT §0 row 5, §C.1
9. AUDIT §0 row 6, §4.1
10. REF §5.1-2
11. REF §3 R4; AUDIT §4.2, 4.6, §5.1; p/me-compete-misc §3; MOTION §2
12. ICONS §6 (marks font and its mask fallback)
13. AUDIT §7.9; p/practice "For the user"

## Not doing

REF §4; DISCOVER §4; AUDIT §1.11; ICONS §9 (banned imagery); MOTION §1.9, §3.9; p/practice §8 (rejected list); p/review §8 (not proposed)

## Bugs found

Fixed: MOTION §4.5 and AUDIT §7.4 (`--p`, now `--m-hold` at runner.css:135); AUDIT §11.10 (tour chip radius; tour.js:105 now 8px).
1. ICONS §1b
2. ICONS §1a
3. ICONS §1d
4. ICONS §1f
5. AUDIT §10.11 (runner.js:2064)
6. p/review §5 (stale counts), §2 (bar over pane), §7 (phone toasts)
7. p/words §5 (run:50, 492, 509)
8. p/words §4, §8.5 (words-ui.js:275-286)
9. p/plan §5 (plan.js:613; plan/index.html:431)
10. p/me-compete-misc §1-2 (signin.js:18, welcome.js:14, pair/index.html:48; compete.css:196-197); p/today §2 (QotD Check); p/practice Shared asks (Now strip)
11. p/tests §1-2 (tests.js:215, 295)
12. tour.js:95, 102, 105; AUDIT §11.11; p/runner §5 (runner.css `.rn-between-bar > i`, MOTION D3)
13. p/results §5 (report page.js:557); p/me-compete-misc §2 (s/index.html, ui.css:2555)
14. AUDIT §11.8, §12 Mistakes; MOTION §4.2.7
