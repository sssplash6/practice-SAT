# UI redesign, 2026-10-19: the brief every agent reads first

## The user's words

> run full audit and the redesign of the website. it should feel super straightforward, make better use of
> side bars, auto hide non essential stuff, cut whitespaces, avoid ai slop, apdash has list of inspo sources
> inspect those to improve the ui of the website. this is exclusively ui redesign. feel free to use different
> font if needed, the only thing you should stick to it is the logo and brand color of orange.

Read as five goals:

1. **Straightforward.** Each page answers one question and shows one obvious next action in the first screen.
2. **Sidebars do work.** The left nav and (on wide screens) a right context column carry the things that are
   useful at a glance, so the main column holds only the task.
3. **Auto-hide the non-essential.** Helper text, explanations, metas, secondary actions and legends fold
   behind a small toggle, appear on hover/focus, or move to the side column. Nothing is deleted outright
   if a student might need it (phone shows everything desktop shows, just folded).
4. **Less whitespace.** Tighter cards, gaps and page padding; fewer stacked headers before content.
5. **No AI slop.** No uppercase letter-spaced mono kickers on everything, no generic card grids, no chatty
   copy, no decorative icons, no gradients, no em dashes.

Later, from the user: "dont be afraid to make some bigger change, just let me know. not a even single
functionality loss tho." So structural changes are welcome (move, merge, regroup, re-layout whole pages),
but **zero functionality loss**: every action, link, figure, state, keyboard shortcut, tooltip, empty /
error / loading state and phone path that exists today must still exist and be reachable. Folding or moving
something is fine; dropping it is not. Every big change goes in the report so the user can be told.

Also from the user, on the inspiration sources: "you should be fully auditing those sources in order to improve
the platform visually" (a real browser audit: INSPO-VISUAL.md), and "it doesnt need to be exclusively improving
existing stuff, it can also be adding some new stuff, replacing some stuff as well". So the sources may bring in
new components and replace existing ones (UI only, still zero functionality loss), not just restyle.

## Fixed

- **Logo** (`web/assets/mark.svg`, `brand/`) and **brand orange `#F18508`**. Orange fills take dark text
  (`--ink-deep`); white on orange is 2.4:1 and fails.
- **UI only.** No server, API, data or question-logic changes. `question.js` rendering logic stays.
- **Test fidelity rules stay:** Source Serif 4 for question text, the `[data-status]` / `--st-*` state tokens,
  difficulty tints, "status is never colour alone", the session and test window have no chrome.
- **Class names are a contract.** 40 pages and the shell key off `.side-*`, `.card`, `.pill`, `.btn`,
  `.quiet`, `[data-status]`, `--st-*`. Change values and layout, never rename or remove a class that
  another file uses (grep first).
- **Buttons:** primary `.pill` (amber, 42px, 10px corners; `.pill.sm`), secondary `.btn`, quiet `.quiet`.
  No new button styles, no radius >= 24px on buttons, nothing taller than 48px. `python3 tools/check-ui.py`.
- **Folding:** `ui.js` folds long helper text automatically (`FOLD_SEL`, ui.js ~2792). Add a class to
  `FOLD_SEL` for a new kind of info box, or `data-nofold` where text must always show (errors, live status).
- **Writing:** no em dashes anywhere (code, comments, UI text). Sentence case. No exclamation marks.
- **Working tree is dirty** with the user's uncommitted work. Never run `git stash`, `checkout`, `restore`,
  `reset` or commit. Edit files in place only.
- **Do not open a browser or take screenshots.** The user reviews every change themselves.

## What the shell audit already found (do not re-audit the shell)

- One shell (`UI.shell`, ui.js ~1408-2400): left sidebar 248px from 1100px wide, a 68px rail below that,
  phone top bar + five bottom tabs under 760px.
- The sidebar's height tiers hide its useful blocks on every laptop: `@media (max-height: 1099px)` hides Up
  next and the Today card from the sidebar and pushes them into a "Now strip" at the top of main. A
  1440x900 laptop never reaches 1100px tall, so the sidebar is nav-only and the Now strip eats main height.
- A right column exists only on Today (`.td-side`, 1080px+).
- 35 distinct font sizes are in use (7px to 56px); 45 `text-transform: uppercase` rules; 16
  `border-radius: 999px`; em dashes in UI strings in about ten files.
- Fonts: Archivo (UI), DM Mono (figures, kickers), Source Serif 4 (questions). Archivo has no Cyrillic.
