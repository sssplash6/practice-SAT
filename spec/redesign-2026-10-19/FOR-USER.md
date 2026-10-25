### Needs your call (each already has a default)

1. **Plan: "shape next week" sheet.** *Built (your call).* Plan › week head › "Shape this week" (or "Shape week" on a later week): mark days busy or short, change a day's minutes, swap a focus skill for the week. The Monday "Your week" sheet links to it.
2. **"Twin".** Two agents renamed it; I put "Twin" back so the app uses one word. *Twin.*
3. **Practice: animated orange search box.** Keep it, or use a plain field (saves about 60px)? *Kept.*
4. **Today's header.** "Good morning, Name", or just "Today"? *Greeting.*
5. **Post-contest rank.** 44px now (it was 84px). *44px.*

### Settled

- **Orange stays the selection colour.** A picked answer is an orange outline; the correct answer turns orange on Check.

### New

One "?" that explains (works on touch). Buttons that confirm in place (Saving, Saved, Copied). Tick meters for minutes and goals. Numbers that roll when they change, never on load. A day readout under the activity heatmap. Tab and switch marks that slide. Soft fades at scroll edges. The sidebar's Up next card folds to one line.

### Changed, by page (tell me if you want any back)

- **Today:** two columns, the work left and "Today at a glance" right. Up next and Due today are one card. The SAT countdown is a plain row.
- **Practice:** the Start bar is a right column from 1280px wide. Presets are always shown. Only Start practice is orange.
- **Answering screens:** the question starts about 100px higher. A Details column in practice from 1280px. The Summary is two columns.
- **Review:** the list sits beside the question from 1280px. Stat tiles are a tab row. Minutes are behind Start ▾. Saved questions are pinned first (the page fetches your newest 100 saved).
- **Results:** a right column. The estimate is the big number (out of 800). Sitting rows lost their Review button (the name links there). Chart gridlines are dashed, everywhere.
- **Tests:** two columns, one Start in the header. Papers are preview tiles on wide screens.
- **Plan:** the Day card and Start come first. "A study day" is a slider. The tab bar no longer sticks on a laptop.
- **Words:** the word grid is near the top. All four hidden tools are back (Export, Import, forecast, offline). Decks are rows.
- **Profile:** charts take the wide column; analytics start folded; Learning preferences live in Settings.
- **Compete:** the overview is three surfaces; Champions moved to Rankings.

Checked: no button, link or field is gone. Everything missing from a page's old layout was renamed, merged or moved, as each card below says.

## From the visual review (2026-10-19)

- Practice tree: skill rows now use the app's short names on one line (e.g. "Two-variable equations"; full College Board name on hover). Keep, or go back to the full names (they wrap onto two lines again)?
- Tests papers: each paper tile shows Start and ⋯ only on hover or keyboard focus (always on phones and on the next test's tile), and the "About your level" badge is dropped (Harder and Easier stay). Keep, or show them always? The revert is in passes/tests.md "## Visual review".

## Server notes (out of scope for the UI work, not changed)

- Words: "Next reviews" counts a requeued card twice (the Words reviewer's report, passes/words.md "## Visual review").
- The local database copy holds test learners written by server/checks/s7.py (ids starting `a:s7`, templates `synthetic.0`, `geo.circle_area`); their pages return 500 (KeyError in registry.topic_of). Fixture data only; real learners are not affected, but topic_of has no fallback for a removed template.
- Review's standalone walk page (/review/walk/) can't open a walk: it reads GET /api/review/walk/{id}, which the server never had, and the fallback (GET /api/drill/{id}) doesn't return the walk. Same in the last commit, so not caused by the redesign. The walk itself works in Review's pane.
- /challenge/ always redirects to today's Daily (server/api_compete.py:849), so web/challenge/index.html is only reachable at /challenge/index.html. Same in the last commit. Today's "Yesterday: #rank" link now goes straight to that day's contest page (the server doesn't send that field yet, so it doesn't show today). Keep the old challenge page or remove it: your call.

## A tap further than before (nothing lost; INVENTORY-FINAL.md has every item)

- Today's five side cards and Profile's five cards start folded (open state is remembered).
- Learning preferences live only in Settings.
- Practice presets, and Results' range and sort, take 2 taps instead of 1.
- The Words legend is behind the ⋯ menu; Champions moved from Compete to Your rankings.

## Calls the shared builder made (overrule any)

- Correct / repaired cells in maps and legends are an amber wash, not solid amber (charts and the runner stay solid).
- Stat rows inside cards are tighter (Plan, Words study, Compete, Practice, Parent).
- The save banner reads "Your progress is only in this browser." with "Save to email".
