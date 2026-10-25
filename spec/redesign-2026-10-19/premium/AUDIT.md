# Premium renovation: audit, 2026-10-19

Code-level only (no browser, no screenshots). Lenses: redesign-existing-projects, high-end-visual-design (mined, not
followed: its rounded-full pills, double bezels, mesh gradients and glass clash with the fixed rules), emil-design-eng.
Inputs: BRIEF, DIRECTION (incl. section 9), INSPO-VISUAL section 2, ui.css, ui.js, kit.js, charts.js, runner.css,
question.js, every page. Companion files: REFERENCES.md (browser references), MOTION.md (motion system), ICONS.md
(icons and illustration); this file lists those areas' gaps only.

The user, in order: "visuals improved a bit, but i was expecting more ... cool buttons, motions, animations ... adding
depth ... it should feel premium"; "icons, highlights and bunch of stuff can be improved a lot"; on Practice at 1440:
"premium means it is not clustered like this". So two goals pull together: MORE depth and life, FEWER things on screen.

Fixed, untouched by every item below: the logo and #F18508 (dark text on orange; orange is the selection colour);
`.pill` 42px / 10px corners, `.pill.sm`, `.btn`, `.quiet`, no radius 24px+ on buttons, nothing taller than 48px;
Source Serif 4 for questions and Bluebook fidelity in the test window; no em dashes; zero functionality loss (hiding
behind one control or folding is fine, removing is not); status never colour alone (ui.css:192-230 glyphs stay).

Item format: `file:line  now -> premium  [slop]`. Slop risk: **L** reads as craft, safe at any dose; **M** fine once,
gimmicky if repeated or loud; **H** likely reads AI-generated or template-y, only with a strong reason.

## 0. DIRECTION v2 rules this audit proposes to relax (a decision for the lead, not a contradiction)

| DIRECTION rule | Proposed now |
|---|---|
| 3: shadows only on floats; cards are flat `--tile` + hairline | an elevation scale e0-e4; cards resting at e1, link cards lift to e2 on hover |
| 6: no gradients except chart fills and scroll fades | subtle vertical gradients on `.pill` and hero surfaces, amber area fills under trends, one warm radial on Today's hero |
| 6: no glow, glass, blur, grain | tinted amber shadow under the primary; backdrop blur on sheets and the phone tab bar only; grain stays out |
| 7: nothing animates on load | one entrance per page per session (40ms stagger), hero figures count up, the gauge sweeps |
| 2: page 16/48, card gap 12, card pad 16 | page top 32, 32-40 between groups, 16 inside a group, card pad 20 (16 phone); density only inside lists |
| 1: hero step caps at 44 | a display step (56-64) for the one number a page is about |

Everything else in DIRECTION stays: Geist (Cyrillic needed, no font swap), the type scale below hero, tokens, the
class contract, sentence case, no uppercase kickers, one orange accent.

## Top 10 overall (do these first)

1. Un-clutter the first screen of every page (section C): Practice first, then Today, Results, Words, Me.
2. Elevation scale + invert surfaces: canvas `--tile`, cards white at e1 with a top highlight (ui.css:89, 107-108, 1203).
3. `.pill` with real depth: layered fill, inner highlight, tinted amber shadow, press sink, loading and success states (ui.css:855-876).
4. Hero numbers at a display size: score estimate, test score, streak, due words (ui.css:1678, 1255).
5. Answer feedback that lands: right fills and pops, wrong nudges, Fixed earns a moment (ui.css:2040-2044, runner.css:229-257).
6. The session Summary and the test score reveal as real hero screens (section 8).
7. Exit motion for every float, origin-aware popovers, Sonner-like toasts (kit.js:409, 471, 868; ui.css:2551).
8. Restore space between groups: page top 32, group gap 32-40, card pad 20 (ui.css:131-132, 439).
9. Highlights: stronger `::selection`, a highlighter `mark`, amber caret, filled icon on the current nav item (ui.css:277, 285, 580).
10. Data viz with weight: thicker gauge and rings, area fills, a crosshair readout (ui.css:1380-1390, 1628, 1683).

## C. Clutter (new top-level lens)

Shared causes (each page's count and fixes are in section 12):
1. ui.css:131-132, 439  card pad 16, card gap 12, page 16/48: groups touch, so 30 small things read as one mass -> pad 20, gap 16 within a group, 32-40 between groups, page top 32  [L]
2. ui.css:1203  every group is a bordered box, boxes sit in a 2-col grid of boxes -> one surface per region; inside it, rows split by hairlines or space only (no box per group)  [L]
3. ui.css:1976-1981, practice/builder.js:732  `.mbar` renders with `--m:0` for unanswered skills: an empty grey bar on every untouched row (the screenshot) -> no track until there is data; the row shows nothing or "New"  [L]
4. ui.css:1180-1185, 1147  `.filters` / `.chips` rows sit above content as loose controls -> one "View" or "Filters" control that opens a popover; only the 1-2 controls used every visit stay visible  [L]
5. ui.css:938-943, 922  secondary routes as bare `.quiet` / `.link` lists in asides -> one "More" menu, or icon rows with counts in a single list surface  [L]
6. ui.css:1205-1211  `.card-head` carries title + kicker + meta + actions + fold on one row -> title and at most one action; meta moves under the title or into the fold  [L]
7. ui.css:2669-2677  folds help, but each fold is another visible toggle line -> a page has at most one "More detail" fold per region  [L]
8. practice/builder.js:451-509, 688-698  the screenshot's three toolbars: preset chips + All presets + Options + Diagnostic, then a Skills/Map/Habits seg + Select all + Clear + an 8-way sort -> presets as one row of 3 with the rest in "More", view + sort + bulk select in one "View" popover, Diagnostic into the empty state where it applies  [L]
9. practice/builder.js:254-255, 423  aside: Start card, a "Ready to start" fold, then Mistakes / Saved / Your sets as bare links -> Start card alone at e1; the three pools as one list surface with counts and chevrons  [L]
10. Pattern across pages: equal-weight neighbours (four domain boxes, four stat tiles, three link cards) -> one leads (larger, raised), the rest recede into a quiet list  [L]
11. ui.js:2449, me/me.js:1210, me/settings/settings.js:37  the sticky section-chip bar shows at rest above the title on Tests, Me (12 chips) and Settings (which also lists the same sections in its aside) -> at 1280+ show it only once stuck, or as one "Jump to" menu; phones keep chips  [L]
12. Pattern: the same route twice on one screen (Diagnostic in the preset row and in Ready, builder.js:509 + 412; Mistakes and Saved as chips and as aside links, 456-459 + 253-254; Report in the exam header and in More, runner.js:1420 + 2463) -> one place each  [L]
13. Pattern: per-row hidden-but-reserved lines (`.reveal` keeps height, tests/index.html:133) and per-row menus visible at rest (plan-ui.js:311) -> move row extras into a `UI.why` or a hover-revealed menu so a row is one line  [L]
14. Pattern: two clocks or two counters for one fact (session stopwatch beside the top clock, runner.js:1401; words run "n left" under the segments, words/run/index.html:454) -> one  [L]

First-screen counts at 1440x900 (from the page passes; approximate, a student with data):

| Page | Controls | Boxes | Bars | Worst offender |
|---|---|---|---|---|
| Today | ~26 (+14 on hover) | 3 holding 9 blocks | 5 | 8-control size row before Study, index.html:1023-1036 |
| Plan | ~40 | 7-9 | 5 + one per calendar cell | 3 rows before the day, 9-item week toolbar, plan.js:362, 1333 |
| Tests | ~32 | 3 + preview frames | 4 | 9 equal Starts under the pill, tests.js:434 |
| Practice | ~17 before the first skill, ~65 total | 6 | 23, all empty | 3 toolbars, builder.js:451-509, 694-700 |
| Review | ~19 before the first row | 3-4 | pips per row | 7 strips before the list, review/index.html:23 |
| Results | ~24 | 3-5 | 2 | 12 equal key-value rows in the aside, results/page.js:233, 323 |
| Report | ~25 | 3-5 | gauge + stackbar | 5 header actions, 9-fact meta, report/page.js:260, 364-389 |
| Words | ~40 + 36 tile buttons | 4 + 36 tiles | ~85 marks | 9-control toolbar, words/index.html:374-403 |
| Session | ~37 around one question | 2 | rail + stopwatch | tool row before the stem, two clocks, runner.js:1401, 1421 |
| Test window | ~23 | 1 | 22 segments | Save and Report in the header beyond Bluebook, runner.js:1420 |
| Me | ~45 | 4 + 4 tiles | ~22 | 12 chips + 26 head icons, me/me.js:91-92, 1210 |
| Settings | ~40 | 1-2 | 13 skeleton bars | sections listed twice, settings.js:37-43 |
| Compete | ~35 | 3 + 10 cells + 6 parts | ~22 | 10-cell ladder before the fold, overview.js:87-119 |
| Leaderboard | ~24 | podium + strip + table | 0 | 15 loose controls in the aside, leaderboard.js:85-131 |
| Contest lobby | ~30 + 30 day squares | 4 + 10 | 20 | ladder above Start, contest.js:216 |
| Help | ~30 | 4-5 | 0 | aside repeats the ? sheet, help/index.html:58-62 |
| Sign in, Welcome | ~24 incl. the shell | 1 | 0 | full app shell around a signed-out card, signin/index.html:18 |

Rule of thumb for the passes: first screen at 1440x900 holds 1 primary, at most 6 other controls, 1-3 surfaces, no
placeholder bars. Generous gaps between groups; tight rows inside lists.

## 1. Why it reads plain (surfaces, elevation, shell, headers, space, brand)

1. ui.css:107-108  two shadow tokens (`--shadow-pop`, `--shadow-float`), nothing for resting or raised -> `--e1` (0 1px 2px warm .06 + hairline), `--e2` hover (0 6px 16px -6px warm .14), `--e3` float, `--e4` modal; one light source from above  [L]
2. ui.css:1203  `.card` = `--tile` + inset hairline on white paper (1.10:1, the audits measured): flat tiles -> canvas `--tile`, cards `--paper` at e1 with `inset 0 1px 0 #fff` top highlight; `--surface`/`--well` (317-318) carry most of it, but rules that hard-code paper inside a tile flip the wrong way and need a pass: `.card.line` 1204, `.field` in cards 985, `.card-err` 1224, `.nextup` / `.side-day` 742, 766, `figure.chart` 1573, `.cal-d` 1740, 1768, `.cal-sw` 1808, `.heat` 1839  [L]
3. ui.css:89  `--paper` pure #FFFFFF next to warm tiles (96-101): two temperatures -> warm canvas #F7F5F1, cards #FFFFFF, so white becomes "raised"  [L]
4. ui.css:518-526  sidebar flat `--tile` with a 1px right border, same tone as cards -> sidebar sits on the canvas tone; main is the raised plane (Linear's inset main: 8px margin, 12px radius, e1)  [M]
5. ui.css:1027, 1120  the only light source in the app is the range thumb and the switch knob -> top highlight on raised surfaces, inner shadow on wells (`.field`, `.seg`, tracks), shadow below floats  [L]
6. ui.css:846 + every page  no shared page header: each page writes a 22px `.h1`, no fact line, no rhythm -> `.page-head` (h1 26-28, one 13px soft fact line, the page primary right), 24px under it  [L]
7. ui.css:536, 559-563  brand shows as a 26px mark and orange selections only -> brand moments with restraint: a faint warm radial behind Today's hero, the mark as an 8% emboss in hero cards, amber edge on the one primary card  [M]
8. ui.css:741-743, 764-768  sidebar Now block and Today card are paper boxes with inset lines on a tile sidebar -> one raised card (e1, white) with the Up next pill, a ring for the day goal; no box in box  [L]
9. ui.css:1243-1259  `.stat` tiles: flat, 28px figure, no hierarchy between stats -> one lead stat at display size, the rest as a quiet row with dividers  [L]
10. ui.css:1355-1359  empty state is a dimmed sample row at .55 opacity -> keep the sample, add a 48px topic glyph (ui.js:671ff) and a warmer surface; one action  [L]
11. Texture: none anywhere -> leave it out (grain on an app UI reads AI-made); depth comes from elevation and light, not noise  [H if added]

## 2. Buttons and controls

1. ui.css:855-863  `.pill` is one flat amber fill -> `linear-gradient(#F4952A, #F18508)` (a 4-6% top lift), `inset 0 1px 0 rgba(255,255,255,.35)`, `inset 0 -1px 0 rgba(120,60,0,.12)`, outer `0 1px 2px rgba(150,70,0,.25), 0 6px 14px -6px rgba(241,133,8,.5)`; 42px/10px kept  [L subtle, M glossy]
2. ui.css:871-873  hover is an 8% darken, press only `scale(.97)` -> hover: shadow grows, fill brightens 3%; press: `translateY(1px)`, outer shadow collapses, inner shadow deepens (a key going down), 120ms  [L]
3. ui.css:874-876  disabled = opacity .32, busy = opacity .6, no spinner -> disabled: `--mat` fill + `--soft` text, no shadow; busy: 16px spinner replaces the icon, label stays, width held  [L]
4. ui.css:2473-2476  `UI.saving` swaps labels on `.btn`, nothing on `.pill` -> success morph on the pill: check draws in (stroke-dashoffset 220ms), "Saved" 900ms, back  [L]
5. ui.css:868  a trailing arrow sits static -> on hover it nudges 2px right (Start, Continue, Next); never a button-in-button circle  [L; H as a nested circle]
6. ui.css:880-908  `.btn` is a `--well` fill that vanishes into tiles -> on paper: white, 1px line, e1, `inset 0 -1px 0 --line` (Geist secondary); pressed: inset shadow; the amber pressed state (904) stays  [L]
7. ui.css:922-936  `.quiet` only underlines on hover -> soft-to-ink colour step plus a chevron nudge on route-like quiets  [L]
8. ui.css:1049-1073, 2523-2530  `.seg` thumb is paper + amber ring, flat -> thumb gets e1 (0 1px 2px, 0 1px 1px), the well gets an inner shadow; ring stays (selection colour)  [L]
9. ui.css:1147-1165  `.chips`: flat well; selected is fill + ring + bold -> unselected: paper + hairline; selected keeps wash-2 + amber ring, a 12px check slides in; press scale .97  [L]
10. ui.css:965-973  `.field`: tile fill, focus = ink inset -> paper, 1px line, `inset 0 1px 2px rgba(0,0,0,.04)`; focus: ink edge + 3px `--wash-2` halo; invalid (987): ink edge + a 160ms 3px shake once  [L, shake M]
11. ui.css:976-981  `select.field` chevron is two CSS gradients -> the icon set's chev svg, 16px, rotates when open  [L]
12. ui.css:997-998, 245  `.check` is the native box with `accent-color` (Practice's domain lists are made of these) -> custom 18px box, 5px corners, hairline; checked amber with a drawn check; indeterminate bar  [L]
13. ui.css:1112-1126  `.switch`: flat track -> inset track shadow, knob stretches 20 to 24px while pressed, check fades  [L]
14. ui.css:1016-1044  range and score slider: decent thumb -> thumb grows 22 to 26 on drag, bubble rises 4px and gains a nub  [L]
15. ui.css:725-735, 2100-2105, 570-585, 357-374  no `:active` on `.ibtn`, `.x`, `.side-item`, `.choice-row`, chips, seg (only `.pill` 873, `.btn` 902, `.cell` 1428, `.opt` 2036) -> `scale(.96)` 100ms on every pressable  [L]
16. ui.css:1003-1013  `.otp`: flat tiles -> focused box raised e2 with amber caret, filled boxes ink hairline; all six go wash + check on success, shake on error  [L]
17. ui.css:308-310  focus ring is a 2px ink outline that snaps on -> keep ink (contrast), animate offset 4 to 2px in 120ms, follow the control's radius  [L]
18. runner.css:312-325  the split Check (Sure / Not sure / Guessing): equal flat parts -> one raised group with dividers, the chosen part pressed in  [L]

## 3. Highlights and states

1. ui.css:285, 277  `::selection` and `mark` are the same `--wash-2`: selection is weak and confusable with marks -> selection `color-mix(amber 32%)`; `mark` as a highlighter: `linear-gradient(transparent 52%, var(--wash-2) 52%)` with 2px radius  [L]
2. ui.css:1007  `caret-color` set only on `.otp` -> `caret-color: var(--amber)` on every input and textarea  [L]
3. ui.css:579-584  current nav: wash + 3px bar, icon goes ink -> filled icon variant, the bar slides between items across page changes (a view-transition name)  [L]
4. ui.css:1203, 1248-1253  link cards and link stats have no hover at all -> lift 1px to e2, hairline warms to `--mat`, 160ms  [L]
5. ui.css:1326  row hover only on `.table.hover` -> every clickable row: tile wash + chevron reveal at the right  [L]
6. ui.css:1321-1322  `tr.you`: wash + 3px amber inset -> plus the avatar ring and a sticky "you" row pinned top or bottom when it scrolls out (compete)  [L]
7. ui.css:1969, 1285, 663  new and unread: 7px dot, count badge -> dot with one soft ring pulse on first appearance (once, not a loop)  [M]
8. ui.css:1455, 109  current cell ring (2px ink, paper gap): right; current question in the session rail is also ink (runner.css:531, 535) -> keep; add a 1.5px amber under-tick on the session rail's current item  [L]
9. ui.css:2315-2317  palette match = bold only -> matched letters underlined amber  [L]
10. ui.css:1251, 1534, 1606  pressed filters, legend toggles and chart hits each draw their own wash + ring -> one shared "selected" recipe (wash-2, 1.5px amber inset, e1)  [L]
11. ui.css:874, 903, 1125, 1535  disabled = opacity .32-.45 on see-through surfaces -> solid `--faint` text on a `--tile` fill (opacity over depth looks cheap)  [L]

## 4. Typography moments

1. ui.css:841-848, 1678  scale caps at 44 (`.gauge-v`), weights 400-600 -> a display step 56-64 / 600 / -0.035em for one number per page; units small on the same baseline (1256 pattern)  [L]
2. ui.css:90, 846  headings are `--ink` #3F3F3F graphite, same as body -> a new `--ink-strong` (#1E1E1E light, about #F5F2EC dark) for headings and hero figures; body stays graphite. Not `--ink-deep`: that is the label on orange and stays #1E1E1E in dark (ui.css:91, 165)  [L]
3. ui.css:846  page title 22px on hub pages -> 26-28 on Today, Results, Plan, Tests, Practice; 22 stays for sub-pages  [L]
4. ui.css:844  `.num` forces tabular figures on lone figures too -> lone hero figures proportional (DIRECTION 1 already says so; `.num` contradicts it)  [L]
5. ui.css:1206, 2079  card and sheet titles 16/600 equal to every other title -> 15/600 in `--ink-strong` with the meta 12.5 soft on the same baseline  [L]
6. ui.css:96-101  three text steps (ink, soft, faint) -> add `--ink-2` (#55514B) between ink and soft for secondary values  [L]
7. ui.css:2018  serif only in questions -> optional Source Serif 4 italic for one editorial line (Summary headline, Today greeting)  [M]

## 5. Colour depth and dark mode

1. ui.css:92-95  orange has four tones (wash, wash-2, amber, amber-deep) -> an amber ramp (100-700) for gradients, tinted shadows, area fills and dark-mode glows  [L]
2. ui.css:107-108, 181  shadows are neutral `rgba(30,30,30)` -> warm tint `rgba(60,40,15,x)`; under orange, amber-tinted  [L]
3. ui.css:160-187  dark: tile #242220 on paper #1A1917, elevation by lightness only -> plus a 1px `rgba(255,255,255,.05)` top highlight on raised surfaces; e-scale values for dark  [L]
4. ui.css:168-169  dark `--wash` is amber at .13 alpha: flat on every surface -> dark hero gets a faint amber radial (6%) so the brand glows in the dark  [M]
5. head.js:12-13, manifest.webmanifest  theme-color flips to #1A1917 only at load; manifest `theme_color` and `background_color` #FFFFFF -> warm canvas value, live update on a theme switch  [L]
6. ui.css:1617-1669  charts are ink plus amber, all flat -> amber area gradients under "you" lines, ink at 2 alphas for context  [L]

## 6. Iconography (gaps only; ICONS.md owns the fix)

1. ui.js:428-475  base stroke 1.6, overrides 1.5 (444, 449), 1.7 (445), 1.8 (456, 469, 472, 475), 1.9 (443) -> one stroke per size  [L]
2. Unicode stand-ins: verdict `✓ ✕` (question.js:1438, 1453), sort `↕ ▲ ▼` (ui.css:1317-1319), `ⓘ` (1368), delta `▲ ▼` (kit.js:1700), `▸ ▾` (runner.css:52-53), checks (ui.css:429, 1124, 1276, 2177, 2211), `✕` (994) -> drawn svg from the set  [L]
3. ui.css:1169-1173, 978, 2673  three CSS-drawn chevrons -> `icon('chev')`  [L]
4. ui.css:580, 458  no filled or duotone active variant (sidebar, phone tabs) -> filled on current  [L]
5. No illustration anywhere (empty states, 404, onboarding, Summary) -> topic glyphs (ui.js:671ff) scaled to 48-64 as the illustration language  [L]
6. ui.js:449  the clock icon has a `.hand` class nothing animates; flame (444) never flickers -> one-shot icon motion on state change only  [M]

## 7. Motion (gaps only; MOTION.md owns the system)

1. kit.js:409, 471, 868  no exit animation: popovers, menus, tips `el.remove()`, sheets `d.close()`, toasts `el.remove()` -> 120-180ms exits (opacity + 4px or scale .98)  [L]
2. ui.css:2551, 2156, 2196  `pop` grows from centre -> `transform-origin` on the trigger side (kit `place()` knows it)  [L]
3. ui.css:2555, kit.js:1692  `.rise` is a no-op, `countUp` is opt-in and used nowhere -> one entrance per page per session; hero figures count up  [M]
4. ui.css:1272 vs 1979, 1385-1390  `.meter` animates width, `.mbar` scaleX, `.ring` not at all -> a registered `<number>` property so rings and meters fill on change; note runner.css:134 already registers `--p` as `<percentage>` (the strike hold), which breaks `.ring`'s numeric `--p` on runner pages: rename one first  [L]
5. ui.css:2571  page change = 120ms fade of main only -> shared-element morph for the sidebar current bar and card-to-page (Tests next test to the test)  [M]
6. ui.css:1430, 1498  only cells and strip squares respond to hover -> link cards lift; cursor spotlight borders only on hero cards if at all  [L; spotlight H]
7. ui.css:2573-2579  reduced motion kills every transition -> keep opacity and colour fades, drop movement (Emil)  [L]
8. kit.js:773-787  tooltips: 350ms delay every time -> instant after the first one is open  [L]
9. practice/index.html:96-108  the search's orange edge runs round forever (4.5s loop): the user asked for the glowing box, but it is the app's only loop and pulls the eye from the task -> keep the glow, sweep once on load and on blur, then rest lit  [M]

## 8. Depth and hero moments

1. index.html:759-760, 94-105  Today's top: a 22px greeting, a date meta, a row of 14px glance links hidden from 1280 -> a hero band: greeting 28, the day's goal as a ring at display size beside the streak, Up next as the one raised card with the pill, a faint warm radial behind  [L; radial M]
2. index.html:1925  Today's score scale: a thin track in a card -> the estimate as a display figure with the band and target under it  [L]
3. practice/session/session.js:401-402, practice/session/index.html:61-64  Summary: `right / n` at 44px, accuracy 16px, a list of mastery words -> display 64 figure that counts up on arrival, an accuracy ring, each topic's bar animating old to new, "Set complete" as a calm headline, the next step as the one raised card  [L]
4. results/index.html:61-62  `.rs-big` estimate at 44 -> display step, the range as the hero with a "+30 since" chip and the scale under it  [L]
5. results/report/page.js:554-555, charts.js:847-860  the one real reveal (gauge sweep when FRESH) -> a sequence: band sweeps, figure counts in sync, the previous band ghosts in, the delta chip lands last (about 1.6s total, once)  [L]
6. test/test.js:713  end-of-test scale animates on its own -> the same reveal sequence as the report, outside the Bluebook window  [L]
7. tests/index.html:37, tests/tests.js:249  next test: an h2 and a meta line in a grid row -> a raised e2 card: test name large, sections as small facts, the pill; it morphs into the test window on Start  [L; morph M]
8. plan/index.html:105-107, plan/plan.js:764  the day card: a head row and task rows -> today's card raised, a ring for the day's minutes, each task row draws its check when done  [L]
9. ui.css:741-771  the sidebar Now block (Up next + Today) is the hero on every page -> one white e1 card, ring + streak + the pill, the only raised object in the sidebar  [L]

## 9. Data visualization

1. ui.css:1683, 1691-1692  gauge: 2px `--mat` track under a 16px amber band, ink needle -> track as wide as the band with an inner shade, band with a gentle amber ramp along the arc and round caps, needle as a knob dot  [L]
2. charts.js:847-860  gauge sweep (1.2s) only when `animate` (report FRESH, test end) -> also on a band change anywhere; the big figure counts in sync  [L]
3. ui.css:1628, 1657-1663  trend and line charts: 2px ink line, no area -> amber-to-transparent area under "you", the last point haloed  [L]
4. ui.css:1271, 1976  meters 4px, mastery bars 3px: lifeless -> 6px, rounded, a 1px inner top highlight on the fill  [L]
5. ui.css:1380-1390  ring: 3px conic, square ends, no motion -> svg ring 5px, round caps, animated `--p`  [L]
6. ui.css:1600-1607  chart hover = 6% ink box -> crosshair line + a floating value chip (ink chip, white text)  [L]
7. ui.css:1765-1788  plan calendar: flat bordered cells -> today raised e1, exam day amber with a soft amber shadow, done days a filled dot that pops once  [L]
8. ui.css:1834-1868  heatmap: good bones -> hovered column tints, today cell ring, cells 2px larger on hover  [L]
9. ui.css:1232-1237  skeletons static by rule 8 -> after 400ms of waiting, one slow 1.2s opacity breath (no shimmer sweep)  [M]

## 10. Feedback and delight

1. ui.css:2040-2042, runner.css:93-96  right answer: wash + ring, the letter fills amber, no motion -> letter circle pops 1 to 1.12 to 1 (160ms), check draws in, the option settles to e1  [L]
2. ui.css:2043-2044, runner.css:97  wrong: line-through, soft letter -> picked option nudges 3px twice (160ms), the right one fills 120ms later  [M]
3. runner.css:232-236  verdict head: 18px unicode glyph -> svg glyph in a 28px filled circle (amber right, ink wrong), slides in with the text  [L]
4. runner.css:253-257  "Fixed": a 200ms scale-in line -> a chip with a drawn check; the sidebar mistakes count rolls down (kit roll)  [L]
5. runner.js:1946-1953  "3 in a row" is text only -> at 3, 5, 10 a flame chip pops in the top bar once  [M]
6. ui.css:1276  goal met: a ✓ appended to the meter text -> the ring closes, a check scales in, one toast "Daily goal met" with the flame  [M; confetti H]
7. runner.css:238-242  mastery change after a verdict: static bar and word -> the bar animates old to new, the word cross-fades  [L]
8. question.js:738  haptics only on the strike hold -> 10ms tick on Check right, 2x8ms on wrong, phones only  [L]
9. ui.css:1222-1228  error = an ink dot and text -> icon, the reason, Retry with a spinner while retrying  [L]
10. No sound -> optional, off by default, Settings toggle  [M]
11. runner.js:2064  after Check, focus jumps to Next with `preventScroll`, so on a long stem the verdict lands below the fold unseen -> scroll the verdict head into view (`block: nearest`); feedback nobody sees is no feedback  [L]
12. ui.css:874, question.js:1093  a disabled Check snaps from .32 opacity to amber; "Checking" exists only for screen readers -> Check arms with a 160ms fill once a choice is picked; "Checking" shows in the label after 300ms  [L]
13. runner.js:1918, runner.css:540  the rail repaints every segment, so an answered segment just appears (only added slots animate) -> the segment just answered fills left to right in 220ms  [L]

## 11. Details

1. No `scrollbar-color` anywhere (ui.css:333, 566, 1327 only set width) -> `scrollbar-color: var(--mat) transparent`, thin  [L]
2. ui.css:2344  calc bar `cursor: grab` without `grabbing` on press -> add it  [L]
3. ui.css:2232-2238  tooltips: paper chip like a popover -> ink chip, white text, 6px radius, small nub  [L]
4. ui.css:2248-2278  toasts: paper rows, rise in, vanish -> Sonner stack (2nd at .96, 3rd at .92, fan out on hover), success icon in an amber disc, a hairline timer  [L]
5. ui.css:2066-2099  sheets: shadow-pop, no backdrop blur, phone handle with no drag -> backdrop blur 4px, drag-to-dismiss with velocity on phones  [M]
6. ui.css:445-466  phone tabs: flat paper bar, 2px amber bar on top of the current tab -> 85% paper with backdrop blur, filled current icon, the indicator slides  [M]
7. ui.css:1292-1296  `.kbd` keycaps: good -> flash the keycap when its shortcut fires  [M]
8. favicon: `mark.svg` on 41 of 42 pages (missing in mistakes/index.html); no dark variant; no `og:image` on any page (share/index.html:7 has a description only) -> add the link, a dark-aware svg, an OG card per share link  [L]
9. manifest.webmanifest  white splash -> warm canvas and the mark  [L]
10. tour.js:104-105  the "Tour paused" chip and its button use `border-radius: 999px` (a banned fully rounded button) and an off-brand fallback #F28C18; `tools/check-ui.py` does not scan JS strings -> chip 12px, button `.pill.sm`, #F18508; extend the check to JS  [L]
11. tour.js:95  the tour ring animates top/left/width/height over a .5 black dim -> transform glide, .38 dim, 2px amber ring with a `--wash` halo  [L]
12. ui.css:2612-2655  print: already right (chrome hidden, state fills forced exact); no change. App icons (icon-192, icon-512, apple-touch-icon.png) were not viewed (no browser): confirm they carry the mark on the warm canvas  [L]
13. ui.css:22, 24-25, 29  the header rules still say "Nothing floats over content", "no shimmer", "Motion is entry only; nothing loops" -> rewrite them with section 0 so later passes do not undo the renovation  [L]

## 12. Per page

A short index, two items per page (the biggest clutter fix, then the biggest premium move). The page auditors'
files in premium/pages/ carry the full lists; counts per page are in section C.

Today
1. index.html:1023-1036  Minutes/Questions seg, 5 size chips, a clock toggle and an estimate on one loose row before Study -> one "15 min" menu beside Study (Plan's menu, plan.js:818); the estimate becomes Study's second line  [L]
2. index.html:759, 2233  22px greeting on bare paper; the SAT countdown a 14.5px value in a row -> hero band (section 8.1) and the countdown as a 40px figure, "days to Nov 7" under it  [L; radial M]

Plan
1. plan/plan.js:362-363, 613, 1333-1352  three rows before the day, then a 9-item week toolbar -> settings line into the plan menu, the banner into the day card, Shape and This week in one menu  [L]
2. plan/plan.js:425, 888  days left is 28px inside the aside; "Day done" is plain text -> a 44px "23 days to Nov 7" by the h1; Day done as an amber check disc that pins in, the streak rolling  [M]

Tests
1. tests/tests.js:434-460  nine New test rows, each with its own Start, each reserving a blank `.reveal` line -> 3 visible, the other 6 behind "More test kinds, 6"; tags into `UI.why`  [L]
2. tests/tests.js:249, 107  next test is a 16px h2 on a flat tile; the estimate 28px in the aside -> the page's one raised card (section 8.7); the estimate at 44 with an "Up 40 since Oct 3" chip  [L]

Practice
1. practice/builder.js:451-509, 694-700, 732  three toolbars before content and 23 empty mastery bars -> one Presets menu, one View menu (view, sort, select all, clear), no bars until there is data  [L]
2. practice/index.html:76, 156  the Start card is a flat tile; four domain boxes read as forms -> Start as the raised hero with "10 questions · 15 min" at 28; domains as titled hairline lists on paper, 32px gutter, no boxes  [L]

Review
1. review/index.html:23, 89; review/review.js:287, 372, 1214  7 strips and ~19 controls before the first row -> new-miss notice as a dot on the Redo tab, Walk into the Start menu, filters down to Search + Filters·n, Insights into the list head  [L]
2. review/review.js:728  "Done for today" exists only as a tab check -> a hero empty state: a drawn check, 28px "Done for today", this week's fixed count  [L]

Results
1. results/page.js:437-457, 224-233, 323  the sittings head holds 4 controls; the aside 12 equal key-value rows under a repeated "Estimate" title -> seg + one dropdown; 3 totals and an "All totals" fold  [L]
2. results/page.js:253, results/index.html:61-65  the 44px band shares a head with chart controls; the target track is hand drawn -> display-size band on its own row with a trend chip; `UI.scale` with a labelled target  [L]

Report
1. results/report/page.js:260, 364-389  a meta line of up to 9 facts and 5 header actions -> date · minutes · Timed; Retake into the ⋯ menu  [L]
2. results/report/index.html:271  the gauge, the report's biggest moment, renders ~268px wide in the aside -> a full-width hero above the columns from 1280, the FRESH sweep kept (section 8.5)  [M]

Words
1. words/index.html:374-403; assets/words-ui.js:431-441  search + 6 filters + count + ? + gear, then Today's words with 8 controls -> search, Sort and one "Filter (n)"; the Start pill and one "More ways" menu  [L]
2. assets/words-ui.js:375  the day's due count is 12.5px soft text beside the h2 -> 40px due figure, the new-words meter as a ring around it, the page's one raised card  [L]

Words run (flashcards)
1. words/run/index.html:867-896  the summary stacks 9 groups at 20px gaps -> score hero, Moved and Still learning, the rest in one Details fold  [L]
2. words/run/index.html:50-52, 485-509  a flat card with a bare rotateY; swipes give no grade cue; the next card just swaps in -> paper face with a layered shadow and two under-cards for deck thickness; "Know" / "Don't know" fades in on drag; the card exits in the grade's direction  [L; drag label M]

Practice session
1. assets/runner.js:1421, 1612, 1401  7 tools in a row before the stem, Details open as a boxed panel before any answer, a second clock -> Mark and Eliminate visible, the rest in one "More" (keys unchanged); Details after the reveal; stopwatch digits after 50% of budget  [L]
2. assets/question.js:1452, ui.css:2021  a 16px verdict with a bare glyph; options are flat tile slabs -> section 10.1-10.3 with options as paper cards at e1 (practice and inline only, never `.ws-exam`); the verdict scrolls into view  [L]

Session Summary
1. practice/session/session.js:516-518, 556-572  8 filter chips over the Review list; a pill plus 3 buttons plus More -> one "Show" menu; pill, one btn, More  [L]
2. practice/session/index.html:61-62  "7 / 10" at 44, nothing moves -> section 8.3 (a 120px accuracy ring, count-up, a delta chip, bars old to new)  [M]

Test window (Bluebook, off limits: runner.css:93-131, 426-430, 449-457, 471-489, 585-593, 624-656, 670, 681-716, 807-810)
1. assets/runner.js:1420, 1426, 1352  Save and Report in the question header, "Add a note" under every question, a Ranked badge -> Bluebook's three header items; the rest into More and the title tooltip  [L]
2. assets/runner.css:587, 636, 462  number chip and navigator button are `--tile`; the clock pulses at 1:00 in the test too -> ink number box and ink navigator button as Bluebook draws them; the pulse limited to practice  [L]

Me
1. me/me.js:91-92, 1210  a 12-chip section bar and a ? plus a fold on every card head (26 icon buttons) -> "Jump to" menu at 1280+; one menu per card head  [L]
2. me/me.js:190, me/me.css:72-77  the page title lives in the 300px aside; a 56px flat avatar -> a full-width header: 72px avatar with an amber progress ring, name at 28, three hero figures  [L]

Settings
1. me/settings/settings.js:37-43, 75-76  sections listed twice; 13 prefs open with help lines -> no chip bar at 1280+; 4 open per section, the rest under the existing "More options"  [L]
2. assets/ui.js:770, ui.css:1138  13 empty skeleton bars while prefs load; "Saved" fades as plain text -> render from the prefs cache; a check that draws in with a 600ms row wash  [L]

Compete
1. compete/overview.js:87-119  Start, Warm up and More, then a 10-cell ladder before the fold -> Start alone (Warm up in More), the ladder behind "See the 10 questions"  [L]
2. compete/overview.js:42, compete/compete.css:57  Daily Challenge is the same flat tile as everything; rank 28px -> the page's raised hero, a 3px amber top edge, rank at 44  [L]

Leaderboard and Rankings
1. compete/leaderboard/leaderboard.js:85-131  ~15 loose controls in the aside (7 metrics, 6 periods, stepper, 2 selects) -> metric dropdown, a 3-way period seg, scope and domain behind Filters  [L]
2. assets/compete-ui.js:106-117, ui.css:1321  a flat podium; your row is a wash only -> a stepped podium at e2 that rises 2-1-3 once; your row with a 3px amber edge, sticky when scrolled off, sliding from its old rank with "Up 3"  [M]

Contest
1. compete/contest/contest.js:216, 286-406  the ladder sits above Start; the result stacks up to 15 groups -> Start first; result as hero (rank, score, rating change) + actions + strip, the rest in Details  [L]
2. compete/contest/contest.js:408, 320-321  a 320ms fade reveal; a level-up is sub text -> the rank rolls in once, the level ring animates old to new with a one-line "Level 5" banner  [M]

Help: help/index.html:58-62 shortcuts card duplicates the ? sheet -> one line "Press ? for every shortcut" [L]; help/index.html:97 a boxed card per group -> plain sections on paper, rows keep hairlines [L]
Sign in: signin/index.html:18 the full app shell frames a signed-out card -> brand bar only [M]; kit.js:1408-1414 OTP has no busy or success state -> boxes dim and disable while checking, nudge on error, turn amber on success [M]
Welcome: welcome/index.html:26 full app shell -> brand bar only [L]; welcome/index.html:28-33 a 440px card on an empty page -> from 1100 a two-column hero: the mark at 56, one line, a real product moment built from `.opt` + verdict classes [M]
Parent: parent/index.html:50 blank until two requests return -> a week-card skeleton [L]; parent/parent.js:107 answers this week is one tile of six -> the hero figure with a delta chip and "5 of 7" days [L]
404: 404.html:17 content top-left inside the shell -> centred at 20vh [L]; 404.html:27 a plain h1 -> a large "404" in `--mat` and a search that opens the palette with the path [M]
Share: share/index.html:6-8 no og tags on any page, links unfurl bare in Telegram -> og/twitter tags and a 1200x630 brand card [L]; share/index.html:29-31 a plain "live" line -> a static amber dot and the student's avatar [L]
Challenge: challenge/index.html:24 rank 28px -> 56px with "of 37" [L]; challenge/index.html:77 "No one yet." -> a dimmed sample row, "Be first today", Start [L]
Diagnostic: diagnostic/index.html:38-42 three fact rows describe the result -> a ghost score scale with "Your first band" [L]; diagnostic/verified.html:25 a plain h1 -> an amber check disc that pins in [L]
Tour: tour.js:153-160 Skip, Back, Try it, Next and dots in one row -> Back and Next, Skip as an x, "2 of 5" [L]; tour.js:104-105 see section 11.10 [L]
Quick sheet: quick.js:142-144 "Got time?" chips before the question -> after the verdict, or one footer menu [L]; quick.js:202-203 the skill shows twice -> pass `head: false` [L]
Mistakes: mistakes/index.html:8 redirect stub without favicon or ui.css -> add both so the one-frame flash is the app's paper [L]
