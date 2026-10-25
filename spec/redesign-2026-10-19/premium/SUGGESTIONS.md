# Premium renovation: pick from this list

Merged from AUDIT, REFERENCES, MOTION, ICONS, DISCOVER and pages/ (sources per item: SUGGESTIONS-INDEX.md).
Size: S = hours, M = a day or two, L = several days. Fixed and untouched: logo, #F18508 (also the selection colour),
`.pill` 42px / 10px corners, `.pill.sm`, `.btn`, `.quiet`, Source Serif 4 and Bluebook in the test window, zero loss.
Demo IDs: added when the demo page lands.

## In one line

Fewer things on each screen, one raised hero per page, an orange button that feels pressable, and motion that shows
what changed: calm and solid instead of flat and crowded.

## Recommended set (most premium per unit of work first)

1. **Calm Practice**: the three control rows become one (presets in one menu on the Your set card, view and sort in one View menu, one tick box for Select all and Clear); no grey bars until a skill has answers; domains as plain titled lists, no boxes. About 65 things on screen become 30; phones see skills on the first screen. *Practice* (M)
2. **An orange button you want to press**: faint top sheen, darker edge, small warm shadow; hover brightens and never jumps; press sinks it; busy shows a spinner after 0.3s at the same width; done draws a check. `.btn` gets a white face and a fine edge. *Every page* (S)
3. **Air between groups**: page top 32px, 32-40px between groups, card padding 20px; rows inside lists stay tight. *Every page* (S)
4. **Shadow steps in warm light**: five shadow levels tinted warm brown, not grey; cards get a soft edge instead of a solid line; a warm off-white page so white cards read as raised. *Shared* (M)
5. **One hero per page**: the one thing a page is about is its only raised card, everything else flat: Today Up next, Practice Your set, Tests Next test, Plan today's card, Words Today's words, Review the question, Results and Report the score, Compete the Daily, Profile a name plate. (M)
6. **Calm first screens everywhere**: at a laptop's first screen, 1 orange button, at most 6 other controls, 1-3 surfaces, no empty bars; filters behind one "Filters · 2" button with removable chips; section chips only once you scroll. Review 8 control rows to 4, Tests 9 Starts to 4 rows plus "5 more", then Words, Plan, Results, Today, Me. (L)
7. **Answers that land** (practice, never the test): right: the answer fills, its letter pops once, a check draws, the progress segment fills; wrong: your pick dims and is struck, the right one fills, no shake; the verdict scrolls into view. *Session, Review, Today question* (M)
8. **Big hero numbers**: one number per page at 56-64px (score, set result, due words, days to exam); a darker ink for headings and that number. *Results, Report, Summary, Today, Words, Tests* (S)
9. **Highlights and states**: stronger orange text selection, highlighter-style marks, orange text cursor, a hover band on every clickable row and card, a press on everything pressable, one shared "selected" look, disabled as solid grey rather than see-through. *Every page* (S)
10. **Things leave, not vanish**: sheets, menus, popovers and toasts animate out (today they blink away); menus grow from their button; toasts stack like cards and fan out on hover; one set of speeds; keyboard actions stay instant; "reduce motion" keeps short fades. *Shared* (L)
11. **Moments that reward**: set finished (score counts up, accuracy ring, skill bars move old to new), test scored (gauge sweeps with the number, change chip lands last, once), daily goal met (ring closes, check, once a day), streak +1 (flame fills, number rolls), mistake fixed (row glows and leaves, counts roll). *Summary, Report, Today, sidebar, Review* (M)
12. **One icon set, filled when active**: Phosphor (a free icon family with outline and filled twins), one line weight, nine scattered icon copies merged into one; the current nav item and "on" toggles (Mark, Save, Star) show the filled twin. *Shell, every page* (L)
13. **Drawn marks, not symbols**: 128 uses of ✓ ✕ ⋯ ▾ ‹ › are missing from our font and borrow each device's symbol font; replace them with drawn icons (or a tiny marks font, Rules 12). *37 files* (M)
14. **Page entry**: the page's blocks rise 8px into place, at most 6, 30ms apart, once per visit, never on back or refresh, the main button never delayed; between pages the sidebar's current marker slides to the new item. *All but the test window* (M)
15. **Data with weight**: the gauge as an instrument (thick groove, warm band, knob needle), an amber fade under trend lines, 6px meters and rings that sweep on change, hovering a chart shows that sitting's score in the big number. *Results, Report, Today, Tests* (M)
16. **Fix the open bugs**: the list at the end, mostly small. (S)

## More, by theme

**Depth and surfaces**
- **Sidebar Now card**: Up next and Today as one white raised card with a goal ring, the streak and the button. *Shell* (S)
- **Question sheet**: in practice the question sits on a white sheet over a tinted ground; options are raised keys that sink when picked. *Session* (S)
- **Shadow on scroll**: top bars, footers and sticky heads get a soft shadow only while content slides under them. *Session, Review, Plan* (S)
- **Up and down**: inputs, switch tracks and meter tracks get a faint inner shadow, so raised buttons sit beside recessed wells. (S)
- **Dark mode depth**: higher surfaces lighter, a 1px top highlight, soft white edges instead of black shadows. (S)
- **Figure edge**: a faint outline on question graphs, test previews and share cards. (S)

**Buttons and controls**
- **Arrow nudge**: the arrow on Start, Continue and Next slides 3px on hover; never an arrow in a circle. (S)
- **Sliding thumbs**: segmented controls and tabs slide their highlight and settle softly; the thumb sits slightly raised. (S)
- **Drawn checkbox**: 18px, 5px corners, the check draws in, a bar for "some". *Practice, Review, Tests, Plan, Today* (S)
- **Fields**: white, faint inner shadow, ink edge plus a soft orange halo on focus, one small shake when invalid. (S)
- **Split buttons**: Start and its menu as one shape with a divider and a chevron that turns. *Review, Report* (S)
- **Quiet menus**: ⋯ buttons are ghost icons until hover, not grey squares. *Plan, Tests, Words* (S)
- **Switch and slider**: the knob stretches while pressed; a dragged slider shows its value above the thumb. (S)
- **Code boxes**: the active box raised with an orange cursor; all six turn orange on success, nudge on error. *Sign in, Pair* (S)
- **Confidence trio**: Sure, Not sure, Guessing as one group with dividers, the pick pressed in. *Session* (S)
- **Phone taps**: no grey tap flash or text selection on buttons. (S)

**Motion**
- **Folds open smoothly**: height and fade instead of a snap. *Today, Results, Review, Me* (S)
- **Lists that glide**: new rows slide in, removed rows shrink out and the gap closes, sorted rows move to their place. (M)
- **Rolling numbers**: a changed figure rolls digit by digit in the direction it moved; never on first load. (S)
- **Charts draw in once**: lines draw, bars rise, the heatmap wipes; first view only, never on resize. *Results, Report, Me* (M)
- **Card into page**: a Results row grows into its Report header, the Tests card into the test start. (M)
- **Sidebar morphs**: collapsing the sidebar and folding the Now card glide instead of jumping. *Shell* (M)
- **Phone sheets**: follow the finger, flick to close, spring back when let go short. (M)
- **Loading**: content fades in over its placeholder; no shimmer. (S)

**Icons and imagery**
- **Topic glyphs redrawn**: lines thick enough at 20px, 7 redrawn, no pale box; shown on Practice's set card and skill window. (M)
- **Logo spot drawings**: the mark's four corners as the only illustration, at 5 moments (first use, all clear, 404, set done, test done); an empty filtered list gets one line and Clear. (M)
- **Sample rows**: first-use empties show a dimmed example (ghost chart, sitting, podium) instead of a bare sentence. (S)
- **Kind marks on rows**: a 16px glyph for warm-up, words, test or review instead of a tag badge. *Today, Plan* (S)
- **One badge style**: achievements drawn the same on Profile and Compete; the sparkle and gem clichés go. (M)
- **Quick in ink**: the Quick bolt drops its orange (one orange per screen). *Shell* (S)
- **Share image and app icon**: a plain share card so links stop unfurling blank in Telegram; favicon.ico; a phone icon. (S)
- **Route drawing**: "How scoring works" as a small drawing of module 1 forking to harder or easier. *Tests* (S)

**Highlights and states**
- **Unread dots**: new things get a dot with one soft pulse when they first appear. *Review, nav* (S)
- **Your row**: amber edge, sticks to the edge when scrolled off, slides from its old rank with "Up 3". *Leaderboard, Challenge* (M)
- **Pick flash**: a menu flashes the chosen row once before it closes. (S)
- **Open item forward**: the selected mistake row comes forward while the rest recede. *Review* (S)
- **Search matches**: matched letters underlined orange. *Palette, Practice, Words* (S)
- **Tooltips**: dark chips with white text; the first waits 0.4s, the next open at once. (S)
- **Keycaps that flash** when their shortcut fires; **thin warm scrollbars**. (S)

**Feedback and delight**
- **Saved in place**: Save turns to Saving then Saved with a drawn check, no toast. *Notes, Settings, Plan, Tests* (S)
- **In a row**: at 3, 5 and 10 right a small flame chip pops once in the session bar. (S)
- **Mastery moves**: after a verdict the skill bar slides old to new and the word rolls (Developing to Proficient). (S)
- **Task ticks**: the check draws, the row tucks into "2 done", the count rolls; the last one closes a ring on the day. *Today, Plan* (S)
- **Milestones**: streak days 7, 30, 100, 365 get one toast with the flame; a "New best" badge beside a score that beats your best, once. (S)
- **Counts over percentages**: "3 of 8 skills proficient", "12 due today". *Plan, Practice, Results* (S)
- **Milestone share card**: streak, new best and contest rank as a card saved from /share. (M)
- **Phone haptics**: a tiny tick on right, two on wrong; **sound** optional and off by default. (S)

**Per page**
- **Today**: Up next lifted with a featured first task and the full Start; side rows rest as label, value, chevron; phones get one day strip. (M)
- **Session**: tools down to 5 (Report, History into More); Details shows 2 rows before you answer; key hints on hover; Summary phone buttons 5 to 3. (M)
- **Review**: Search, Sort and Filters only; rows trimmed to one badge and three facts (6-7 mistakes visible, was 4); the action bar docks under the list. (M)
- **Words**: one filter row; tiles without empty dots; Start plus one "Other ways" menu; flashcards follow the finger with Know / Again stamps, fly out, and the deck thins. (M)
- **Plan**: Start alone on today's card; calendar with one nav and unboxed days; status tiles as a number plus one line; wizard side panel calmed; Shape sheet with a live week chart. (L)
- **Tests**: the Next test card shows the test's module shape as a tick strip; kind rows one line each. (M)
- **Results and Report**: the score leads the Report's main column; header one row (Retake into ⋯); question tools from 3 rows to 1. (M)
- **Profile**: a full-width plate with a 72px living mark and ring, name, level, last 3 badges. (M)
- **Compete**: the Daily as the focal card with one menu; a stepped, raised podium; the contest rank rolls in once. (M)
- **Sign in, Welcome, Pair**: a brand bar instead of the app sidebar, a centred raised card, one sign-in method plus "Other ways". (L)
- **Test window**: Bluebook's header only (Save and Report into More); the break countdown at 44px; nothing else moves. (S)
- **Small pages**: Help as one surface, 404 centred with the drifted mark, Settings with one index, Parent with a hero figure. (S)

## Rules this relaxes (yes or no each)

1. **Shadows only on floating things**: cards carry the lowest shadow level, clickable cards step up on hover, the hero one step higher.
2. **Solid 1px card border**: a soft see-through edge inside the shadow, which works on every background and in dark mode.
3. **No gradients**: three only: a faint sheen on the orange button, an amber fade under trend lines, a faint warm corner tint behind one hero per page.
4. **No glow**: a small warm shadow under the orange button (under 4px blur); no halos.
5. **No blur**: only behind the dimmed backdrop of sheets and under the phone tab bar; never on cards, text or scrolling content.
6. **Nothing animates on load**: one short page entry per visit; hero numbers count up on a new score; the gauge sweeps on a fresh test.
7. **One motion curve, no bounce**: three springy settles; one small bounce for rewards only.
8. **Spacing** (page 16/48, gap 12, padding 16): page top 32, 32-40 between groups, padding 20 (16 phone); rows stay 40.
9. **44px cap on hero numbers**: a 56-64px step for the one number a page is about.
10. **No shadow on `.btn`** (INSPO-VISUAL 6.4): a light top edge and a contact shadow.
11. **New named values**: `--shadow-1` to `--shadow-5` (replacing `--shadow-float`, `--shadow-pop`), `--hero-wash` (the warm tint), `--ink-strong` (#1E1E1E for headings and hero numbers), `--ink-2` (secondary values), warm page #F7F5F1, an amber ramp, motion speeds.
12. **A 3KB marks font** for ✓ ✕ inside text and 9px cells (no other edits), or drawn masks instead (more edits).
13. **The one loop**: Practice's turning search edge: keep it, sweep it once then rest lit, or slow it to 8s.

## Not doing

- Shake, red flash or sound on a wrong answer.
- Confetti, mascots, cartoon art, sparkles, rockets; nothing celebrates sign-up, a new plan or saved settings.
- XP, gems, hearts, lives, streak-loss nags or guilt banners.
- Glass, grain, aurora or mesh gradients, glowing or moving borders, cursor spotlights, 3D tilt, magnetic buttons, neumorphism.
- Buttons that lift or grow on hover (none of 6 measured premium sites do), fully round pills, arrows in nested circles, the chunky Duolingo 3D button.
- Shimmer placeholders, marquees, anything looping; slow 0.7s blur reveals (marketing sites only).
- Anything premium in the test window; blue or grey shadows on warm paper; cards inside cards.

## Bugs found

Fixed by the lead: runner.css `--p` clash (Today's meter and ring drew wrong; now `--m-hold`); tour.js chip button at 999px (now 8px).

Still open:
1. Icon line weights never apply: duplicate `stroke-width` attributes keep only the first, so every custom weight draws 1.6 and the inequality ray's bold part never shows.
2. 128 ✓ ✕ ⋯ ▾ ‹ › characters are missing from Geist and change shape from device to device.
3. Unknown icon names silently draw an orange dot (test.js, me.js, builder.js, session.js); `UI.ICON.more` does not exist.
4. Topic glyphs inside a selected chip likely show a pale box (`.chip .glyph` keeps `--gb`); to verify.
5. After Check, focus jumps to Next without scrolling: on a long question the verdict sits below the fold (runner.js:2064).
6. Review: after a fix, group, list and action bar counts stay stale until reload; from 1280 the bar covers the pane's foot; phone toasts hide under it.
7. Flashcards: the card keeps its 0.45s transition while dragged, so it trails the finger; swipe is touch only; the old card waits 0.9s after a grade.
8. Words Start shows nothing for 0.2-0.6s while it saves, so a double tap can start two runs (`startWords`).
9. Plan: banners replay their entry on every redraw; picking a day blinks for 1.1s (`.pl-flash`).
10. Two or three orange Starts on one screen: Sign in, Welcome and Pair keep the sidebar Start; the phone contest lobby shows three; Today's question Check; the phone Now strip.
11. Tests: when Up next is a resume, the hero and the In progress row show the same sitting.
12. tour.js still falls back to an off-brand #F28C18; the tour ring and the between-modules bar animate size and position (slow on phones).
13. Dead hooks: `data-animate` on the Report gauge has no CSS; `.rise` on /s/ and share cards does nothing.
14. mistakes/index.html has no favicon or ui.css (a white flash on redirect); page fades lack `::view-transition { pointer-events: none }`.
