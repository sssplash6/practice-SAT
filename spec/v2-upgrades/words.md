# v2 upgrades: Words (vocabulary)

Written 2026-09-23 for `spec/rebuild-v2.md` §3.8 (lines 9134–10029). It merges the three designers'
proposals in `spec/v2-upgrades/_proposals/words.json` (outcomes, experience, unfair advantage;
cited below as "outcomes #1" and so on, and "outcomes G3" for a parity gap) into one
build-ready list, W1–W22. The TopTierPrep inventory is §3.8.1, checked against
`spec/toptierprep-teardown.md`, `ttp-notes.md` and the live walk in `ttp-live.md`.

* **Precedence.** `spec/v2-decisions.md` wins over this file. This file wins over §3.8 where
  they differ, and §3 lists every change. Part 2 resolutions (R1–R38) still hold, except the
  lines named in §3.2 "Outside the section".
* **Decision 2 changes the section's centre.** Words is SAT Reading & Writing vocabulary only:
  SAT words and transitions, no Math-language deck. That removes every bank-linked extra in
  §3.8.4 (In a real question, Practice 10 questions with it, mix-up drills, Mistake → words,
  tap-to-define in math stems, Translate the phrase, the Math word of the day) and leaves the
  library at about 820 entries, below their 1,002. This file puts the bank's power back on the
  R&W side instead: SAT-form items that never run out, each wrong option naming its trap
  (W1–W3), and it rebuilds the library above theirs (W17).
* **Math-first, additive** (decision 3). The R&W items live inside Words (`server/rw_items.py`),
  addressed by `(template, seed, word)` in the bank's Item shape, and are answered into
  `word_reviews`. They are not in `attempts`, Practice, Tests, the estimate or Compete. When the
  R&W bank arrives, the same addresses move into the bank without a rewrite.
* **Siblings.** `shell-me.md` (U1–U28), `today.md` (T1–T20), `plan.md` (L1–L20) and
  `practice.md` (P1–P25) are already written. Today's third day's-question slot (T14) is W21's
  item. The Due row (T2) and the Plan's Words task (L4) launch W11's run. Up next (U1) gains
  one `words` kind. Where this file needs a sibling to change, §3.2 lists it; nothing is
  specified twice.
* **The bar.** A student who uses TopTierPrep's Vocabulary today opens ours and wants to switch,
  because every review here moves them toward the SAT's own Words in Context and Transitions
  items, "known" is proven, and the day's words take one tap. Parity is failure.
* **Names.** Upgrades are W1–W22. Builders are Part 4's tasks. S9 owns everything under
  `web/words/**`, `server/words*`, `server/rw_items.py` and `tools/build_words.py`; other
  owners are named per upgrade.
* **Facts this file relies on.**
  * Their QBank: Words in Context 261 College Board + 102 of their own; Transitions 194 + 10
    (`ttp-notes.md`). Both finite.
  * R&W pace: 32:00 for 27 questions = 71 s a question.
  * `satbank/check.py` gates a topic on `material/keys/<slug>.json` (official answers read from
    the College Board PDF). There are no R&W key files, so an R&W generator cannot pass that
    gate. It gets its own verifier (W1).
  * The bank already has 26 "Which expression/equation represents…" stems with named mistakes
    (linear and inequality topics), so a separate phrase-translation generator adds nothing.
  * The crowd rule is 20 answers (open question 12, R27).
  * `kv` (S8) holds an HMAC secret; W1's sheet samples sign with it.

---

## 1. Scorecard

"v2 spec" is §3.8 as written, after decision 2. The verdict says why ours is way better, or
PARITY with the upgrade that fixes it.

| # | Their feature | Their version | v2 spec | After these upgrades | Verdict |
|---|---|---|---|---|---|
| 1 | Nav item and route | Sidebar "Vocabulary" → /vocabulary → /vocabulary/library | Sidebar Words with a "12 due" meta, `G W`, the phone menu sheet (R1); /vocabulary/ redirects | The meta reads "12 due · 9 min"; the phone menu row has its own Start; Up next and `G N` start it when it is the next thing; a home-screen shortcut (W11) | v2 PARITY: a nav item. **W11 → WAY BETTER.** The nav says what is owed and starts it. |
| 2 | Four pill tabs | Library / Flashcards / Quizzes / My Words, each a route | The same four as a segment control | **Today's words** sits above the tabs on every Words page: due, proofs, new words and checks in one run sized in minutes, one Start (W11) | v2 PARITY: the student still picks a tool before being told what to do. **W11 → WAY BETTER.** |
| 3 | Library size and default | 1,002 claimed; opens filtered to "Must know 650"; the default collection lists words twice | About 1,090 with 220 math terms. After decision 2 about 820 | ≥1,100 R&W entries (400 core, 600 advanced, 80 transitions, about 100 second senses as their own entries), plus 80 roots; the build fails on a duplicate (W17). Placement means fewer of them to study (W10) | v2 BELOW theirs after decision 2. **W17 + W10 → WAY BETTER.** More words, no duplicates, sense-level, and the ones you know are skipped. |
| 4 | Difficulty filter and colours | Authored Easy / Medium / Hard, colour-coded | The authored level as bars (the bank-derived level went with decision 2) | Measured from everyone's first-try in-context answers after 20 ("58% right in context"), the authored level marked "est." until then; a **Hard for you** sort (W18) | v2 PARITY: an authored guess, like theirs. **W18 → WAY BETTER.** |
| 5 | Topic filter | General / Academic / Science / Economics / Transitions | SAT subjects and transition logics (their five plus two, once math topics go) | Plus **Family** (strength ladders, W3), **Roots** (W4), second meanings and answer-choice language (W17), and status filters for traps and stubborn words (W5, W9) | v2 PARITY. **W3 + W4 + W5 → WAY BETTER.** Filters by how the SAT tests a word. |
| 6 | Collection filter | Must know 650 / The College Panda's 400 / Custom | Our own collections as tiles with known-bars and due dots | Adds Second meanings, Answer-choice language and Roots; **paste any book's or teacher's word list** and get it matched to our entries with our meanings (W17, W19) | v2 PARITY, and below for a student working from a book list. **W19 → WAY BETTER.** |
| 7 | Start Practice Session | Flashcards over the whole collection; ignores the filters | A sticky study bar that acts on the filter or selection | The same, plus Today's words as the default action (W11) | **WAY BETTER already** (it acts on what the student sees). |
| 8 | Word tile grid | 6 columns, border by difficulty; no search, status, progress or meaning; not focusable | Buttons with pips, status, due, star; search; Meanings toggle; legend | Adds a proven mark, a stubborn knot and a trap dot; in self-test mode a tile opens covered (W7, W9, W14) | **WAY BETTER already.** |
| 9 | Library data quality | eloquent, elusive, inherent… listed twice | The build fails on a duplicate (word, sense) | Per-sense slugs, so each sense has its own state (W17) | **WAY BETTER already.** |
| 10 | Tile → flashcard | One click to a front-first card | The sheet opens with the meaning showing; recall needs Flashcards from here (two clicks) | With Meanings off the sheet opens covered: Space shows, 1 / 2 grade, ← → page on front-first. Browsing is reviewing (W14) | v2 BELOW (one more click to recall). **W14 → WAY BETTER.** |
| 11 | Flashcard frame | Difficulty pill, stacked deck, big word, click to flip | The same, plus keys, swipe, aria-live, reduced motion | Adds **In a sentence** and **Commit first** fronts (W7, W8) | v2 PARITY in kind. **W7 + W8 → WAY BETTER.** |
| 12 | Card back: definition and example | Bold definition, one fixed example | Meaning and 2–3 authored examples | **In a new sentence**: a fresh generated sentence on every review across science, history and literature; collocations; BUILT FROM roots; the SHADES ladder; "Last time you picked X"; your own hook (W8, W3, W4, W9) | v2 PARITY: fixed sentences get memorised with the card. **W8 → WAY BETTER.** |
| 13 | Synonyms / Antonyms | Two flat lists with icons | SAME AS / OPPOSITE chips | **Shades**: the family as a ladder by strength and tone, tested by Most precise and Order the ladder (W3) | v2 PARITY. **W3 → WAY BETTER.** The near-synonym difference is the SAT skill. |
| 14 | Common Confusions | A blue list of lookalikes | NOT THE SAME AS rows with a tell; Quiz the pair | Adds the student's own picks ("you picked illusory 3×"), the Fix card for stubborn words, and Drill it on the pair (W9, W5) | **WAY BETTER already** (tells). W9 makes it personal. |
| 15 | Save star | Appears after the flip; files the word | ★ on sheet and card; a Saved deck | ★ means study soon: front of New, back in Today's words after 14 days untouched, exam cap at any box (W14) | v2 PARITY: a bookmark. **W14 → WAY BETTER.** |
| 16 | I Know / Don't Know | Self-grade; Don't Know does nothing; Due stayed 0 | Real boxes, requeue, regrade, outcome line; Known after 10+ days of self-grades | A self-grade stops at box 3. **Known** needs a right, unguessed in-context answer on a due review; Known and Claimed are shown apart everywhere; "your Know holds up 78%"; Commit first when it doesn't; a Thought I knew deck (W7) | v2 PARITY: still self-report. **W7 → WAY BETTER.** Known predicts test-day points. |
| 17 | Previous / Next | Free movement | ← → through the run, skip to the end, regrade the latest grade | The same | **WAY BETTER already.** |
| 18 | New-word allowance | 5 / 20 / 30 a day by tier; opening a card spends one | Free; a daily goal, never a cap | The goal is set from the exam date, each chip showing its finish date and review load (W12) | **WAY BETTER already.** W12 makes the number mean something. |
| 19 | Quiz: collection select | All Collections or one | Deck tiles with counts: Due, New, Missed lately, Saved, a collection, a topic, My own | Adds Today's words, Claimed, Thought I knew, Fell for a trap ▸, Stubborn, At risk, a family, a root (W5, W7, W9, W12) | **WAY BETTER already.** |
| 20 | Quiz timer | None / 30 s / 60 s | Off / 15 / 30 / 60 s, draining bar, "Out of time" | Adds **SAT pace** (71 s), time per type against it, rushed misses, and the **Words check**: 12 SAT-form items in 14:12 (W15) | v2 PARITY: a stopwatch. **W15 → WAY BETTER.** |
| 21 | Quiz item | Definition → 4 word tiles; the only type; not keyboard reachable | 7 types; In context and Pick the transition from a finite authored pool | Generated Words in Context (both SAT stems), Most precise, Order the ladder, Transitions, Decode it, Type it. Unlimited, each regenerated exactly from its address (W1–W4, W8) | v2 PARITY on supply: a daily quizzer meets repeats within a week. **W1 + W2 → WAY BETTER.** |
| 22 | Distractors | Near-synonyms, more than one fits (ingenious / imaginative / innovative / original) | Never a synonym or one hop; same part of speech; build proves 3 | A feature-verified single key; near-synonyms appear only as named traps that break the degree, tone or sense the clue fixes; the crowd pulls a distractor strong students pick (W1, W18) | v2 fixes their bug but trains an easier task than the SAT. **W1 → WAY BETTER.** |
| 23 | Wrong-answer feedback | Red tint and "Correct answer: X" | Key amber, pick struck; the mix-up and its tell | Every option's reason at once with a named trap and its check question; the clue lit; **Same word, new text** (T), **Same trap, new word** (Shift+T) (W1) | **WAY BETTER already.** W1 adds the SAT's traps and the next item. |
| 24 | Right-answer feedback | Green tint, no text | A Why toggle, then Next | The clue flashes with the reasons and it moves on after 700 ms: one key per right item (W1) | **WAY BETTER.** |
| 25 | Quiz session | No score, no count, no end | Count line and summary: by type, mix-ups, next reviews, Up next | Adds How you missed (by trap and logic), word gaps vs reading gaps, calibration, graduations, and Next: {Up next} (W5, W6, W7, W13) | **WAY BETTER already.** |
| 26 | Report | Chip → shared modal | R17's modal with Wrong or unclear definition | One-tap **Another choice also fits** on every verdict; Suggest a better meaning, prefilled; the crowd guard; fix-once replies (W18) | v2 PARITY: a form. **W18 → WAY BETTER.** |
| 27 | My Words | Saved Words N / Due Today N cards | 8 stat tiles, 14-day forecast, table, bulk bar | 12 tiles (Claimed, Thought I knew, Fell for a trap, Stubborn, At risk…), How you miss words, logic mix-ups, By exam day, recall %, the word wall (W5, W7, W9, W12, W13) | v2 PARITY in kind: lists. **→ WAY BETTER.** It says why you miss and what will slip. |
| 28 | My Words filters | Difficulty / Topic / Collection | The shared filter bar, Collection included | Plus trap, family and root filters | **WAY BETTER already.** |
| 29 | My Words empty state | "No saved words match these filters" | Per-state messages with actions | The same | **WAY BETTER already.** |
| 30 | Add-your-own-word FAB | Draggable; covers Next; one typed word | Quick sheet tab (R29), Add to my words on a selection, `N`, Quizlet import | Paste a passage (finds and stars its SAT words), paste a word list, **log a missed Bluebook Words-in-Context or Transitions question** → trap named, twins started (W19) | v2 PARITY: one word at a time, minus the overlap. **W19 → WAY BETTER.** |
| 31 | Plan: Include vocabulary practice | A toggle on step 4 | Step 4 Words row: 5 / 10 / 20, words from | Chips 0 · 5 · 10 · 15 · 20 · 30 · Auto, each with its finish date and review load 2 weeks out (W12) | v2 PARITY: a number picked blind. **W12 → WAY BETTER.** |
| 32 | Plan: Vocabulary / Flashcards tasks | Duration, aiReason, Study words / Review cards, done / skip | A Words task: minutes, reason, three launch buttons, auto-done, budget | One launch into Today's words; minutes at the student's own pace; a reason with real counts (W11) | v2 PARITY: three buttons, pick a mode. **W11 → WAY BETTER.** |
| 33 | Plan landing "1,002 words" | A claimed count | "1,090" | A live count with no duplicates, and "you know about 540 of them" (W17, W10) | v2 PARITY. **W10 → WAY BETTER.** |
| 34 | Profile vocab surfaces | "Vocab N Word" (cards opened), Saved Words, Include Vocab Review | Words known / studied / saved / reviews this week; Include words switch | Known vs claimed, vocabulary-size estimate and its growth, "your Know holds up 82%", core done by a date, top trap with Drill it (W7, W10, W12, W5) | v2 PARITY: counts. **→ WAY BETTER.** Outcomes, not activity. |
| 35 | Subscription meter | "New Words Today 0/5" | None; free | The same | **WAY BETTER already.** |
| 36 | Their QBank Words in Context | 261 + 102 fixed items, prose explanations | 1–3 authored In context texts per word | Unlimited generated items with named traps, the clue shown, another like this, trap drills (W1, W5) | v2 PARITY: finite. **W1 → WAY BETTER.** |
| 37 | Their QBank Transitions | 194 + 10 fixed items | 2–4 authored pairs per transition | Unlimited generated items, the logic named on every option, relationship-first mode, a 9×9 logic mix-up grid with drills (W2) | v2 PARITY: finite. **W2 → WAY BETTER.** |
| 38 | Teacher dashboard (hidden) | Assigns tests and QBank only | Nothing for words | Share a list; a class words assignment with a known-by-date goal and per-word class miss rates; printed worksheets with keys, a different version per student (W20) | They lack it for words. **W20 → WAY BETTER.** |
| 39 | "Spaced review" | Claimed on the plan landing; Due stayed 0 | Honest boxes, exam cap, 14-day forecast | Recall measured on due reviews and intervals scaled to it, fuzz so days don't clump, a debt breaker, retention to exam day (W12, W13) | **WAY BETTER already.** W12 + W13 make the schedule measure itself. |

---

## 2. Accepted upgrades

### Layout after these upgrades

`/words/` at 1280, top to bottom (the phone stacks the same order):

```
title    H1 Words · "1,180 words · 212 known · 64 claimed · 12 due" · search · Bring words ▾ · Add a word
today    Today's words panel (W11)                                           [on every Words page but the runner]
tabs     Library · Flashcards · Quiz · My words
strip    Due today (debt line, W12) · New today (goal, W12) · Word of the day (answer it, W21) · Transition of the day (W21)
exam     By exam day (W12)  — or "Set your SAT date to see your finish line" with UI.examDate
groups   READING & WRITING (All · SAT core · SAT advanced · Transitions · Second meanings · Answer-choice language) · ROOTS · MINE
filters  Collection · Topic · Family · Difficulty · Status · Part of speech · Sort · Meanings · Select
legend   ●●●○○ strength · ✓ proven · DUE · ★ saved · ● fell for a trap · ⌇ stubborn · ▮▮▯ difficulty (est.)
grid     tiles (or the logic map when c=transitions, W2; root tiles when c=roots, W4)
bar      sticky study bar
```

Build order inside S9: W17 content and W1–W2 generators first (everything else reads them),
then W7's rules, W11's run, and the rest in any order; W22 last.

### A. Questions that never run out, for Reading & Writing

#### W1. Words in Context, generated: every wrong option names its trap, the clue lights up, another like this is one key

*From: outcomes #1, experience #1, unfair-advantage #1, and the distractor, supply, feedback
and card-back gaps of all three. Effort L (content). Builders: S9 (`server/rw_items.py`,
content, runner, sheet), F3 (spans and per-option reasons in `UI.workspace` quiz mode), F4
(columns).*

**Why.** Words in Context is where vocabulary becomes points: a 2–4 sentence text, one blank,
"the most logical and precise word or phrase". Theirs quizzes bare definitions with
near-synonyms that all fit, and their bank's pool is finite with prose explanations. Ours makes
the real form without limit, with one defensible key, a named trap on every wrong option and
the clue shown: the bank's misconception engine, carried to R&W.

**Content** (`server/words/`, S9).
* **Sense features** on every SAT entry: `class` (semantic family id, about 150: weaken,
  confirm, cautious, novel, obscure, praise, criticize…), `polarity` (−1 / 0 / +1), `intensity`
  (1–5 within the class), `pattern` (argument patterns it fits: verb-claim, verb-person,
  adj-person, adj-approach, noun-result…), `subjects` (passage subjects where it is a topical
  lure).
* **`classes.json`**: `{id, dimension ("how critical"), opposite}` per class.
* **`traps.json`**: the trap kinds, each `{id, name, tell, check}`. D is a distractor, N the
  frame's need, K the key:

  | id | name | legal when | check line (shown under the reason) |
  |---|---|---|---|
  | `reversed` | Reverses the meaning | D.class = opposite(N.class) | "Ask: does the text push for or against?" |
  | `too_strong` | Too strong | D.class = N.class, same polarity, D.intensity > N.hi | "Ask: does the text go that far?" |
  | `too_weak` | Too weak | same, D.intensity < N.lo | "Ask: is the text more certain than this?" |
  | `connotation` | Wrong tone | D.class = N.class, opposite polarity | "Ask: is the text approving or critical?" |
  | `lookalike` | Looks like the answer | D is one of K's lookalike confusions | "Ask: which word is it really?" |
  | `everyday` | Everyday meaning | `nearly` items only: D is K's common sense | "Ask: what does the word mean here, not usually?" |
  | `topical` | Fits the subject, not the blank | frame.subject ∈ D.subjects, D.class ∉ {N.class, opposite} | "Ask: what job does the blank do?" |
  | `wrong_logic` | Wrong relationship | transitions (W2) | "Ask: how do the two sentences relate?" |
  | `reversed_direction` | Cause and effect swapped | transitions (W2) | "Ask: which came first?" |

  "Unsupported" is folded into `topical` (§4).
* **`frames.json`**: about 300 frames, at least 2 per class, spread over science · history &
  social studies · literature & arts. A frame is `{id, stem: complete | nearly, subject, text,
  need: {class, polarity, lo, hi, pos, pattern}, needs, difficulty}`. `text` has `{slot}` fills,
  one `____`, and the clue marked `[[…]]`. `needs` is one line ("to weaken or contradict").
* **`fills.json`**: slot pools (researcher names from many origins, fields, sites, organisms,
  artworks, periods, quantities).
* The spec's authored `cloze` per word become fixed frames (no slots) with the same need tags.
  Each second-sense entry carries at least one `nearly` text.

**Generator** (`server/rw_items.py`, S9, stdlib only).
* `item(template, seed, word=None, want_trap=None)` returns the bank's Item shape as a dict:
  `{template, skill: 'Words in Context', difficulty, seed, word, stem, text, choices[4],
  answer_index, reasons[4], traps[4] (null on the key), spans: [{start, end, kind:'clue'}],
  rationale, needs}`. Templates: `rw.wic.<frame>` and `rw.nearly.<entry>.<n>`.
* The seed picks the fills, the key (among the frame's legal keys when `word` is None), three
  distractors, each with one legal trap kind (preference: `want_trap`, lookalike,
  too_strong / too_weak, connotation, reversed, topical), and the option order.
* **Rules** (checked by generation and by the verifier):
  * K is legal: K.class = N.class, same polarity, N.lo ≤ K.intensity ≤ N.hi, same pos, N.pattern
    ∈ K.pattern.
  * No distractor is legal as a key.
  * No two options share (class, polarity, intensity). All four share pos.
  * No option, or its `also` form, appears in the filled text.
  * A distractor in K's `same` list is allowed only as too_strong, too_weak or connotation,
    which break the key rule by construction.
* **Reasons** are concrete: "Too strong: the text says the results only [[raised doubts]];
  “refute” means to prove false." The key's reason: "“undermine” means to weaken; the text
  needs something that weakens the claim."
* **Stems**: complete → "Which choice completes the text with the most logical and precise
  word or phrase?"; nearly → "As used in the text, what does the word “qualify” most nearly
  mean?".
* **Addresses**: `(template, seed, word)` regenerates the item exactly.
  `another(prev, like)`: `like='word'` gives the same word in a different frame (a new seed if
  it has one frame); `like='trap'` gives the same trap kind (the student's pick, else the key's
  hardest trap) with a different key.
* `__main__`: 200 seeds × every frame × up to 5 legal keys, re-deriving every rule from the
  features. It prints counts per frame and exits 1 naming the frame and seed.
  `ponytail:` the verifier re-checks from the same features; the content review (open question)
  is still the only check on the features themselves.

**Screens.**
* **Quiz item** (`UI.workspace` quiz mode): head "Words in Context · Science"; the text in
  serif 19px, the blank a 4em rule; 4 options in a column (A–D).
* **Verdict**:
  * the key amber and the pick struck through, as practice;
  * the `.mistake` line: a mono trap chip `TOO STRONG`, then the reason, then the trap's check
    line in `--soft`;
  * the clue span in wash with an amber underline, and "Clue: “did not support” → the blank
    needs “to weaken or contradict”";
  * **all four options show their reason** under them at once, no toggle;
  * the crowd line after 20 first tries on this frame: "52% right · 31% chose a too-strong
    word";
  * actions: **Same word, new text** (`T`), **Same trap, new word** (`Shift+T`), Open word (`O`),
    **Another choice also fits** (quiet, W18), Next (Enter).
* **A right answer**: the clue flashes and the reasons show; it moves on after 700 ms when
  `prefs.words_autonext` is on (default). Any key, or the pointer over the verdict, holds it.
  A wrong answer waits for Enter.
* **Tap-to-define**: library words in the text that are not options are `button.term`
  (§11's gloss), except in the Words check (W15).
* **Word sheet**: **IN AN SAT-STYLE QUESTION** replaces IN A REAL QUESTION. It shows an instant
  item for this word (the sample below), answered inline, with **Another**. The footer pill
  becomes **Practise 10 in context** (a quiz run of `incontext` and `nearly` items keyed on
  this word, each in a different frame or fill).

**Data and endpoints.**
* `word_reviews` gains `template TEXT`, `seed INTEGER`, `trap TEXT` (the picked option's trap;
  NULL when right or not generated). Index `word_reviews(template)` for crowd counts.
* Run formats add `incontext` (generated; authored cloze are fixed frames inside it) and
  `nearly`. A public item is `{item_id, kind, head, text, stem, choices}` only.
* The answer reply adds `{trap, reasons[4], traps[4], spans, needs, crowd: {n, key_pct,
  by_trap} | null}`.
* `POST /api/words/run/{id}/another {item_id, like: 'word' | 'trap'}` inserts one item after the
  current one and returns it; 409 until that item is answered.
* **Sheet sample**: `GET /api/words/{slug}` adds `sample: {item, token}`, where `token` =
  HMAC(kv secret, learner | template | seed | word | local day). `POST /api/words/sample/answer
  {token, answer, ms, conf?}` returns the verdict and files one `word_reviews` row (mode
  `sheet`, kind `incontext`) under §12's quiz rules (an early review does not promote).
  `POST /api/words/sample {slug, like}` returns a new sample. No session is made; a bad token,
  or one from another day, is 400.

**Uses the rest of the site.** T14's Word in context slot is one of these items (W21).
Practice P15's Reading & Writing seg lists "In context" and "Transitions" with their counts.
W3, W5, W6, W7, W15 and W18 read `trap`, `spans` and `needs`.

**Acceptance.**
1. `PYTHONPATH=. python3 server/rw_items.py` exits 0 and prints a count per frame. In a temp
   copy where one frame's `hi` is raised so a too_strong distractor becomes legal as a key, it
   exits 1 naming that frame.
2. `PYTHONPATH=. python3 -c "import server.rw_items as r; a=r.item('rw.wic.weaken-01',77,'undermine');
   assert a==r.item('rw.wic.weaken-01',77,'undermine') and len(a['choices'])==4"` passes.
3. `POST /api/words/run {mode:'quiz', deck:{source:'collection', value:'sat-core'},
   formats:['incontext'], count:10}`: the first item's JSON contains none of `answer_index`,
   `reasons`, `traps`, `trap`, `template`, `seed`, `word`, `key`, and its `text` contains
   `____`.
4. A wrong answer's reply has `trap` in `traps.json`'s ids, 4 non-empty `reasons`, and a
   `spans` entry of kind `clue`.
5. `POST …/another {like:'word'}` after answering returns an item; test_flow finds the same
   `word` and a different `template` for a word with 2 or more frames. Before answering it
   returns 409.
6. Over 2,000 generated items in test_flow: no option appears in its text; the four options
   share pos; no distractor is in the key's `same` list unless its trap is too_strong, too_weak
   or connotation.
7. Browser: `/words/?w=mitigate` shows IN AN SAT-STYLE QUESTION with 4 options and makes no
   request to `/api/words/run`. Answering shows 4 reason lines and a `.clue` element. In a quiz
   verdict, `T` loads a new item.

#### W2. Transitions, generated: every wrong option names its logic, the relationship comes first, and a logic map

*From: experience #2, outcomes #6, unfair-advantage #1 (3). Effort M. Builders: S9, F3 (idea
spans).*

**Why.** The SAT's Transitions item tests recognising how two sentences relate. Theirs is a
Topic tag on flashcards of "however", plus 10 of their own bank items. Ours generates the item,
names the logic behind every wrong option, trains naming the relationship before picking the
word, and targets the pair of logics this student confuses.

**Content.**
* `transitions.json` entries gain `logic` (the 9 groups: contrast, concession, cause → effect,
  addition, example, sequence, clarification and emphasis, similarity, conclusion). The file
  holds `logic_reasons` (a 9×9 table: "“Therefore” presents sentence 2 as a result of
  sentence 1; here sentence 2 goes against what was expected.") and `confusable` (concession~
  contrast, cause~sequence, example~addition, clarification~example, similarity~addition,
  conclusion~cause).
* `pairs.json`: about 40 families, at least 4 per logic. A family is `{id, logic, s1, s2[] (5 or
  more variants), fits (acceptable keys), compatible (logics that also read correctly, never
  offered as wrong), spans}`, with slots from `fills.json`. The logic holds by construction
  ("expected X to rise → it fell" is contrast). The spec's authored `pairs` become fixed
  families.

**Generator** (`rw_items.transition(template 'rw.tr.<family>', seed, word=None)`).
* The key comes from `fits` (or is the given word). Three options come from three other logics,
  nearest confusable first, never from `compatible`.
* Reasons come from the 9×9 table with the words filled in. It returns two `idea` spans and a
  relation label ("expected ↑ → found ↓ · contrast").
* The self-check (the same `__main__`) runs 200 seeds a family: 4 distinct logics, none
  compatible, the key word never in the text.

**Relationship first** (`prefs.words_relation`: auto | on | off; auto is on for the student's
first 20 transition items, off after 8 right logic picks in the last 10, back on after 3
transition misses in a row; the setup shows which and why).
* Step 1: "How does the second sentence relate to the first?" with the 4 options' logic names
  (keys 1–4; Enter skips to the words).
* Step 2: the 4 transitions. `given` stores `logic|word`.

**Verdict.** The two idea spans are highlighted with the relation label between them. The
`.mistake` line names both logics: "WRONG LOGIC · contrast for concession: “However” signals a
contrast, but sentence 2 first admits a point against the claim: that is concession
(“Admittedly”, “Still”)." `T` gives the same logic in a new text; `Shift+T` the same pair of
logics (the student's confusion) in a new text.

**Library logic map.** The Transitions collection (`?c=transitions`) replaces the grid with 9
columns (5 + 4 below 1100px, a scroll-snap row on a phone). Each column has the logic name, a
one-line test ("Does sentence 2 push against sentence 1? → contrast"), its transitions as
tiles, "Most mixed up with: concession" (the student's grid, else `confusable`), a known-bar and
"8 of 10 right in 30 days". The column head's **Practise** starts 8 items of that logic.

**Cards.** A transition's card back shows its logic group and two generated example pairs.

**Data.** Format `transition` is generated. The reply adds `{logic_needed, logic_picked,
spans, relation}`.

**Acceptance.**
1. The `rw_items.py` self-check covers every family with no failure.
2. A run of 20 `transition` items: in test_flow every stored item has 4 options from 4 logic
   groups, none in its family's `compatible`.
3. With `prefs.words_relation = 'on'`, the first public item has `step: 'logic'`, 4 logic names
   and no transitions; answering the step returns the 4 transitions.
4. `/words/?c=transitions` renders 9 `.logic-col` elements, each with a test line and tiles.
5. A wrong pick's reply has `logic_needed != logic_picked` and 2 spans of kind `idea`.

#### W3. Shades of meaning: strength and tone ladders, tested as Most precise and Order the ladder

*From: experience #6, unfair-advantage #9, the synonym and Topic gaps. Effort S on top of W1's
features. Builder: S9.*

**Why.** "Most precise" on the SAT means matching the text's strength and tone. Their synonyms
are a flat list, which is how their own quiz came to offer four words that all fit. A ladder
shows how near-synonyms differ, and two item types test exactly that.

**Screens.**
* **SHADES strip** on the sheet (under MEANING) and on card backs: the word's class (same pos)
  ordered by `intensity`, weakest → strongest ("question · doubt · challenge · dispute ·
  refute"), the current word in orange, each chip opening its sheet. A second row by polarity
  (+ / 0 / −) appears when the class mixes tones. One helper line: "The most precise word
  matches the text's strength and tone." An optional authored `shade` note on the current
  word: "Weaker than “prove”: the evidence points to it but doesn't settle it."
* **Most precise** (`precise`): W1 items from frames whose need pins one intensity, with two
  same-class neighbours (too_strong, too_weak) and one reversed. The verdict draws the ladder
  with the key and the pick marked.
* **Order the ladder** (`order`): 4 words of one class with distinct intensities, shuffled, to
  put weakest → strongest. Desktop: 1–4 pick a word, ↑ / ↓ move it, Enter checks; the pointer
  drags. Phone: 44px drag handles. The verdict shows the right order and names each misplaced
  word ("“condemn” is stronger than “criticize”"). It is rendered by `words-ui.js`, not
  `UI.workspace`. Order items are logged (kind `order`) and never move a box.
* **Library**: a **Family ▾** filter (classes with 3 or more words, named by their dimension:
  "How critical · 5") and Status **On a ladder**.

**Data.** `GET /api/words/{slug}` adds `shades: {dimension, words: [{slug, word, intensity,
polarity}], at}`. The build checks that every class used by `order` has 4 or more distinct
intensities and every class has a `dimension`.

**Acceptance.**
1. `GET /api/words/refute` has `shades.words` sorted by intensity with `shades.at` pointing at
   refute.
2. A run of `order` items: answering with the right order returns `correct: true` and files 4
   `word_reviews` rows of kind `order` with unchanged `box_before`/box.
3. The sheet for a word in a class of 5 shows a `.shades` strip with 5 chips and one
   `[aria-current]`.

#### W4. Roots and word families: decode words never studied

*From: outcomes #9, experience #9. Effort M (content). Builder: S9.*

**Why.** Their 1,002 words are memorised one at a time. Roots let a student infer or eliminate
an answer choice they have never seen, and one root carries several words.

**Content.** `roots.json`: about 80 roots, prefixes and suffixes (bene, mal, cred, chron, dict,
duc, fid, grat, loqu, luc, mit/miss, path, spec/spic, ten/tain, vert, voc; ab-, ante-, circum-,
contra-, dis-, ex-, in-, inter-, ob-, per-, pre-, pro-, re-, sub-, trans-; -ous, -ity, -ize,
-ence, -ive…). Each is `{id, forms, meaning, origin, false_friend?, words: [{slug, split
"circum|spect", gloss "look around → careful"}]}`. The build checks that every split re-joins to
its word and every slug exists. A word whose split would mislead is left out.

**Screens.**
* **BUILT FROM** row on the sheet and card backs: part chips ("circum- around · spect look").
  A chip opens the root sheet (`UI.word.open('root:spect')`): its meaning, the false friend if
  any, every family word with pips, and "Knowing “spect” helps with 11 words (4 known)".
* **Library**: a ROOTS group with one **Roots · 80 · 23 known** tile; selecting it turns the
  grid into root tiles, each with "family known 4/6". Topic ▾ gains a Roots group.
* **Decode it** (`decode`): a word never reviewed (box 0) with its parts; "What does it most
  likely mean?" with 4 meanings of similar length, never from the same family. `W` shows the
  parts when they are hidden (a hint). The verdict shows how the parts build the meaning. A
  right answer puts the word in box 1, due tomorrow; wrong, box 1 due today.
* **Which root do these share?** (`rootshare`): 3 family words, 4 roots.
* **Stats** (Words top meta on the Roots view, My words): "Roots known 23 of 80 · they help
  with about 260 words you haven't studied". A root is known when half its family is at box 3
  or higher.
* **Today's words** adds one root card for every 10 new words when two of them share a root.

**Data.** `GET /api/words/{slug}` adds `roots: [{id, forms, meaning, split, gloss}]`;
`GET /api/words/root/{id}`; deck source `root`; formats `decode`, `rootshare`.

**Acceptance.**
1. `tools/build_words.py` exits 1 when a split in a temp copy does not re-join to its word.
2. `GET /api/words/circumspect` has `roots` naming circum and spect.
3. A `decode` item's 4 options never include two words from the served word's families.
4. `/words/?c=roots` shows root tiles each with a "family known" line.

#### W5. How you miss words: the trap profile, trap drills and distractors that chase your weak spot

*From: outcomes #1 (panel), experience #1 (trap profile), unfair-advantage #2, outcomes #6 and
experience #2 (logic grid). Effort M. Builders: S9; S1 (Me's top trap line).*

**Why.** Theirs records nothing about how a student went wrong. Ours counts every miss by the
SAT's lure types, drills each one, and slips the student's weak lure into later items so they
learn to reject it.

**Screens.**
* **HOW YOU MISS WORDS** panel on My words and in each run summary: one row per trap kind with
  its count over 60 days, share of misses, a trend arrow against the previous 30 days, a chip
  for the last word missed that way, and **Drill it · 10**.
* **LOGIC MIX-UPS** (My words, the Transitions logic map, the summary): a 9×9 grid of only the
  non-empty cells on desktop (rows: the logic the text needed; columns: the logic picked;
  off-diagonal cells in ink opacity by count). Top cells are named: "You read concession as
  contrast 4×". A cell starts **Drill this pair · 8**. The phone shows the list form.
* Status **Fell for a trap ▸** (each kind with its count) in the Library and My words; a legend
  dot on tiles whose last in-context miss named a trap.

**Adaptive distractors.**
* A trap kind is **open** for a learner when it caused 3 or more of their last 20 in-context
  misses and at least 25% of them. While open, half of their generated items fill one distractor
  slot with that kind when the frame allows it. The verdict's details say "Includes a trap
  you're working on: Too strong".
* A logic confusion A→B is open after 2 such picks in 30 days with no 2 clean A answers since.
  While open, every A item includes a B option.

**Data and endpoints.**
* `GET /api/words/insights` (new; also feeds W6, W7, W12, W13): `traps: [{id, name, n, share,
  trend, last_word}]`, `logic: [{needed, picked, n}]`, `open: {traps, logic}`.
* Deck sources `trap` (value: trap id; every item carries an option of that kind, keys weighted
  to the learner's learning words) and `logic` (value `A>B`; keys of logic A, a B option in
  each).

**Uses the rest of the site.** W11's run includes 2 items for an open trap. Up next's `words`
row reason names it (§3.2). Me's "What keeps catching you" adds the top word trap (S1, §3.2).

**Acceptance.**
1. A learner with 4 in-context misses of trap `too_strong` in their last 10: `GET
   /api/words/insights` has `too_strong` in `open.traps`, and over 20 generated items for them
   at least 6 carry a too_strong option (test_flow reads the stored items).
2. `POST /api/words/run {mode:'quiz', deck:{source:'trap', value:'too_strong'}, count:10}`:
   every stored item has a too_strong option.
3. A learner with 2 concession items answered with contrast words: `insights.logic` has
   `{needed:'concession', picked:'contrast', n:2}`, and their next concession item has a
   contrast option.
4. `/words/mine/` shows `.trap-row` elements with a Drill it button each.

#### W6. The method trainer: predict the blank, find the clue, and tell a word gap from a reading gap

*From: outcomes #5. Effort M. Builders: S9, F3 (a staged item: options hidden, then shown).*

**Why.** A miss in context comes from not knowing the word or from misreading the text, and
the fixes differ: cards can't fix a reading gap and more reading can't fix an unknown word.
Their quiz trains dictionary matching. Ours teaches the SAT method with scaffolding that fades.

**Method mode** (`prefs.words_method`: auto | on | off). Auto is on for the student's first 30
in-context items, off after 8 right predictions in the last 10, back after 3 in-context misses
in a row. The setup and the item head say which ("Method off: your predictions are right 9 of
10 · Turn it on").
* **Step 1** (options hidden): "What does the blank need?" with 3 predictions: the frame's
  `needs` line and two from frames of other classes with different polarity (generated; keys
  1–3; Enter skips to the choices).
* **Step 2**: the 4 options.
* **On a miss**: "Tap the words that tell you" (any overlap with the clue counts; Enter skips),
  then the clue is shown.

**Diagnosis** (`word_reviews.gap`): prediction right and word wrong = `word`; prediction wrong =
`reading` (only when step 1 was answered).
* A word gap puts the key at the front of New (if unstudied) and in Missed lately.
* A reading gap adds the frame to a **Read for the clue** set, weighted to frames whose clue is
  8 or more words from the blank.

**Summary and My words**: "This week's misses: 7 word gaps · 3 reading gaps", with **Learn these
7** (a cards run of the keys) and **Practise finding the clue · 10** (an in-context run, Method
on, deck `readgap`).

**Acceptance.**
1. With `prefs.words_method = 'on'`, the first in-context item's public JSON has `step:
   'predict'` and 3 predictions and no choices.
2. Answering the prediction right and the word wrong stores `gap = 'word'`; the prediction
   wrong stores `gap = 'reading'`.
3. `GET /api/words/insights` has `gaps: {word, reading}` over 7 days.

### B. Known means proven

#### W7. The proof ladder: formats climb with the box, and Known needs a right answer in context

*From: outcomes #4, experience #3, unfair-advantage #3 (2)(3), and the self-grade gaps of all
three. Effort M. Builders: S9; S1, S3, S6 (labels on their tiles, §3.2).*

**Why.** Their I Know / Don't Know is self-report that never schedules, and their Vocab count is
cards opened. The spec's boxes work, but Known still rests on the student's say-so. Here a word
is Known only after the student got it right in the SAT's own format, after a gap, without
guessing, and the student sees how far their own "I know it" can be trusted.

**Rules** (`words.py` §12, replacing the Know rules).
* **Box 0 (new)**: in Today's words and Learn runs, a **Learn card** (word, meaning, one
  sentence, speak) with **Got it**, which files no grade. 3–5 items later a Meaning → word check
  grades it: right → box 2 (due in 3 days), wrong → box 1 (due today, requeued). In a plain
  Flashcards run, Know on a new word is still box 2.
* **Boxes 1–2**: a flashcard self-grade, or Meaning → word / Word → meaning in a quiz. Right on
  a due word → box + 1.
* **Box 3**: the due review is served as an in-context item (`nearly` for a second-sense word,
  `transition` for a transition, Meaning → word for an own word), in the card's place in a
  cards run, with the same keys. Right and not a guess → **box 4, Known**, and `proven` is set.
  Wrong → box 1.
* **A self-graded Know never moves a word above box 3.** At box 3 or higher it reschedules at
  the current box (box 3: in 2 days, flagged "Prove it") and never promotes.
* **Boxes 4–5**: served as in-context items with the hard trap set (everyday, too strong /
  too weak, lookalike) or `nearly`. Right → + 1; wrong → box 1.
* The spec's rules stay: no promotion on an early review, one box a day, the exam cap, a quiz
  grades only its target.
* **Statuses**: **Claimed** = box 3 with `proven` unset; **Known** = box 4 or higher (so every
  Known word is proven).

**Status line** after every grade names the next format: "Back Thu as an in-context question",
"Prove it in context to make it Known", "Known · back in 16 days".

**Commit first** (a card front; `prefs.words_commit`: auto | on | off). Before the flip the card
shows 3 short meanings and **No idea** (keys 1–3, 0). The flip shows whether the pick was right
and grades it (right = Know, else Don't know); there is no self-grade. Auto turns it on when the
student's Know holds up less than 75% of the time over their last 50 checked Knows, and the card
says so.

**Guess mark.** `I` before choosing (or the **Guessing** chip in the item head) files the answer
with `conf = 'guess'`. A right guess never promotes and keeps the word due tomorrow; the summary
reads "3 guesses · 2 right".

**Calibration.** Each self-graded Know (cards, placement, triage) is paired with that word's
next objective review. My words and each summary show "When you say Know, you're right 78% of
the time (last 100 checks)". A pair whose check went wrong puts the word in **Thought I knew**
(a status and a deck, 30 days, cleared by a right answer): "You were sure and it slipped."

**Everywhere a count shows**: "212 known · 64 claimed" (the Words H1 meta, the Today tile, Me,
Results). Achievements count Known only. The sheet's YOUR RECORD shows a 5-step ladder, filled by
facts: Seen · Recalled (box 2+) · Picked (a right recognition quiz) · In context (a right
in-context answer) · Known.

**Data.** `word_state` gains `proven TEXT` (date). `word_reviews` gains `conf TEXT`.
`/api/words` rows add `proven`, `claimed`; counts add `claimed`, `thought`. `insights` adds
`calibration: {pct, n}`.

**Acceptance.**
1. A word at box 3, due, graded `know` in a cards run: the reply has `box.after == 3`, `due ==
   today+2` and the status line contains "Prove it". In the next cards run containing it, the
   item for that word has `kind == 'incontext'`.
2. The same word answered right in context with no `conf`: `box.after == 4` and the word's row
   has `proven` set. Answered right with `conf:'guess'`: `box.after == 3`, `due == today+1`.
3. No sequence of self-graded `know` answers over 60 simulated days lifts a word above box 3
   (test_flow drives the clock).
4. With 50 checked Knows at 60% held, the next cards run's cfg has `commit: true` and its first
   public card has 3 meanings.
5. `GET /api/words` has `counts.claimed`, and the Words H1 meta contains "claimed".

#### W8. A fresh sentence on every review, and Type it

*From: unfair-advantage #3 (1)(5), outcomes #8 (context fronts), the card-back gaps. Effort S
on W1. Builders: S9, F3 (a text input in quiz mode, or `words-ui.js`).*

**Why.** One fixed example gets memorised with the card. A new sentence for the tested sense
every time teaches the meaning, not the sentence, across the SAT's three passage domains.
Producing the word is a stronger retrieval than recognising it.

* **IN A NEW SENTENCE** on every card back: a W1 frame filled with the key (the word
  highlighted), a new seed each review (`seed = hash(learner, word, reps)`), a different subject
  from the last one shown. The authored examples move under **More examples**.
* **SHOW FIRST** gains **In a sentence** (the word highlighted inside an unseen generated
  sentence) and Commit first (W7). Mixed includes In a sentence. Word stays the default.
* **Common partners** (`partners`, optional: "bolster a claim / an argument") on the back and
  the sheet.
* **Type it** (`typed`): a meaning and a generated sentence with the blank, and a text field.
  It accepts the word or its `also` forms, any case, accents folded. On words of 5 or more
  letters one edit (Damerau) counts as right and is flagged ("Spelling: ocurred → occurred").
  `W` shows the first letter and marks the answer as hinted (right but no promotion). Own words
  can use it.

**Acceptance.**
1. Two cards runs on the same word on different days show different IN A NEW SENTENCE texts;
   both contain the word.
2. A `typed` item answered "Mitigate " for mitigate returns `correct: true`; "mitigat" returns
   `correct: true, spelling: 'mitigate'`; "mitigation" returns `correct: false`.
3. The `typed` public item carries no `word`, `also` or answer field.

#### W9. Stubborn words get a Fix card and the student's own hook

*From: outcomes #11, experience #7, unfair-advantage #12. Effort S. Builder: S9.*

**Why.** A few words eat most of the review time. Serving the same failed card again wastes
it. Ours finds the word the student confuses it with from their own picks and changes the
approach until it sticks.

* **Stubborn**: 4 or more lapses, or 3 misses in 14 days. A knot glyph on the tile (its
  aria-label includes "stubborn"), Status **Stubborn**, a deck, a My words tile ("Stubborn 6 ·
  words that keep slipping get a different drill").
* **The Fix card**, served when a stubborn word comes due, in any run:
  1. "Missed 4 times · picked “illusory” 2× · “evasive” 1×" (from `word_reviews.given`).
  2. The word beside its most-picked wrong word (else its top lookalike): both meanings and the
     tell.
  3. BUILT FROM and SHADES rows when it has them.
  4. **My hook**: the student's own memory aid, up to 140 characters (`word_state.hook`). From
     then on it shows on every card back, and under the front after a miss.
  5. A 3-item pair quiz, the key alternating between the two words (W1 items when both have
     frames, else Meaning → word). All 3 right → box 2.
* **Schedule**: stubborn words run at 1, 2, 5 days; the flag clears after right objective
  answers on 2 different days, and the word rejoins at box 2.
* **Every card back**: when the last review was wrong, "Last time you picked “illusory”".

**Data.** `word_state.hook TEXT`; `PUT /api/words/{slug}/hook {text ≤ 140}` (set with
`textContent` only). Deck source `stubborn`.

**Acceptance.**
1. A word with 4 lapses: `/api/words` marks it `stubborn: true`, and its next due item in a run
   has `kind == 'fix'` with `picks` listing the given words.
2. `PUT /api/words/elusive/hook {text: 'e-LUSive: it gets loose'}` then a cards run: the back
   carries that hook.
3. After right in-context answers on 2 different days the flag clears and `box == 2`.

### C. The right work, less of it

#### W10. Placement and triage: skip what you already know

*From: outcomes #3, experience #5. Effort M. Builders: S9; S1, S6 (the estimate line).*

**Why.** Theirs starts everyone at word 1 of 650, at 5 a day on free. Ours measures what the
student knows in 3–4 minutes, with a guard against overclaiming, skips it, and gives a growth
number they can watch rise.

**Placement** (`/words/start/`, data-page `words-start`). It is the first-run state of the
Library's Today's words panel, of the Today tile ("Skip the words you already know · 4 min")
and of the Plan's first Words task.
* 48 real words, 8 from each of 6 bands (core easy / medium / hard; advanced easy / medium /
  hard), and 12 made-up words from `foils.json` (about 60 pronounceable non-words, rotating),
  in random order. One word per screen: "Do you know this word?" **Yes** (1) · **No** (2) ·
  **Not sure** (3), or two thumb buttons and a small third.
* After every third Yes on a real word, a 4-option Word → meaning check.
* **Estimate** per band: hit = the Yes rate on real words; fa = the Yes rate on made-up words;
  rate = max(0, (hit − fa)/(1 − fa)) × the band's check accuracy (the overall check accuracy
  when the band had none). Band estimate = band size × rate; the ± range adds the bands'
  1.96 × √(rate(1−rate)/n) × size in quadrature.
* **Result**: 6 band bars ("SAT core · medium: about 110 of 140"); "You know about 540 of the
  1,000 SAT words (±40)"; when any made-up word got a Yes, "You said yes to 2 of 12 made-up
  words, so we counted cautiously"; and what happens next: "The 190 you said you know come back
  once each as an in-context question over the next 2 weeks. New words start at SAT core ·
  medium."
* **Effects**: every Yes on a real word → box 3, Claimed, due spread over days 3–14 (seeded), so
  each is proven in context before it counts (W7). No and Not sure → the front of New. The New
  deck starts at the lowest band under 70% and skips bands estimated at 90% or more.
* **Re-check** is offered after 30 days. The history is a line on Me's Words tile ("~610 words ·
  +70 since Sep 23") and a line in Results' Words block.

**Triage** (`/words/study/?mode=sort&c=<collection>`): one big word at a time, no flip. **Know
it** (1) → box 3, Claimed, due spread over days 3–14 · **Not sure** (2) → starred (front of New)
· **New to me** (3) → stays New. On a phone: swipe right, up, left. `Z` undoes the last. A bar
reads "212 / 300 · 3 min", and a triage resumes where it stopped.

**Data.** Both are word runs: `mode: 'placement' | 'sort'`, answers `'yes' | 'no' | 'unsure'` or
0–3 for checks. A public placement item never says which words are made up. `word_state.placed
INTEGER DEFAULT 0`. `finish` returns `estimate: {n, lo, hi, bands}`; `/api/words` and
`words.me_stats` carry `estimate: {n, lo, hi, at, delta_30}`. Rows of mode `sort` and
`placement` don't count toward the streak or study reviews (R13), like lookups. Build checks: no
foil is a library word, or in the system word list (`/usr/share/dict/words`) when present; the
tool says when it is absent.

**Acceptance.**
1. `POST /api/words/run {mode:'placement'}` returns 60 items; none carries `foil`, `band` or a
   key; 12 of the stored items are foils (test_flow).
2. Answering Yes to every item: `finish.estimate.n` is below the library size and the result
   carries the caution line.
3. After placement, a word answered Yes has `box == 3`, `placed == 1`, and `due` between today+3
   and today+14.
4. In a triage, `Z` after a Know it restores the word's previous box.

#### W11. Today's words: one mixed run, sized in minutes, one tap from everywhere

*From: outcomes #7, experience #4, unfair-advantage #6, and the tabs, plan-task and phone gaps.
Effort M. Builders: S9 (run, panel, `words.today_summary`), F2 (Up next kind, manifest
shortcut, phone menu Start), S3 (Today tile and Due row), S7 (the Plan task's launch).*

**Why.** Theirs splits the day across four tabs and two plan buttons, and review never mixes
with new words. Ours is one tap to the right study for today, mixed, sized to the minutes the
student has, instant between items.

**The run** (`POST /api/words/run {mode:'mix', deck:{source:'today'}, box?: 5 | 10 | 15}`),
in this order:
1. Fix cards due (W9).
2. Due reviews, most overdue relative to their interval first, each in its ladder format (W7),
   capped by the debt spread (W12).
3. Proofs for Claimed words that are due.
4. Missed lately words not yet due, up to 3.
5. 2 items for an open trap (W5) and 2–3 transition items.
6. New words up to the day's goal: Learn cards with their checks 3–5 items later (W7), and a
   root card per W4.
7. One in-context item for a word learned yesterday.
* No two consecutive items share a word or a transition logic; the two words of a lookalike pair
  sit at least 3 items apart.
* **Box clock** ("4:10 left of your 6"): at zero the current item finishes and the summary
  opens. Without a box it ends when the parts are done.
* **Preview**: the panel's `›` opens a sheet listing each part with its count and a switch
  ("Due 12 · Proofs 4 · New 10 · Transitions 3"); Enter starts.
* **Minutes** use the learner's median seconds per card and per quiz item over 60 days (10 s and
  20 s until there are 20 of each). `words.minutes_today()` is the same figure, so the Plan
  budget and Up next agree.
* **Summary**: the primary is **Next: {Up next title}** (U1 chaining); the words run end is on
  T2's list of finish screens.

**Entry, each one tap.**
* **The Today's words panel** on every Words page but the runner: "Today's words · 12 due · 4
  proofs · 10 new · about 9 min", **Start**, chips 5 · 10 · 15, `›` preview. Done for the day:
  "Done · 34 reviews · Learn 10 more". New student: "Find your level · 3 min" (W10) with "or
  Learn 10".
* **Today's Words tile** primary (S3). Review cards, Learn 10 and Quiz move into its ⋯ menu.
* **The Plan's Words task** primary (S7), the same ⋯ menu.
* **Up next** kind `words` (F2), after `checks`: title "Today's words · 12 due · 9 min", reason
  from real counts ("12 come back today · 4 are proofs · Too strong caught you 5 times"). So
  `G N` starts it when it is first.
* The phone menu sheet's Words row carries **Start**; the nav meta reads "12 due · 9 min".
* A web-app manifest `shortcuts` entry "Today's words" → `/words/run/?today=1` (a long-press on
  the home-screen icon).

**Speed.**
* Each `/answer` reply carries `next`, and the runner renders it before the student finishes
  reading the verdict.
* Card grades are optimistic: the next card shows at once and the POST queues with retry.
  A quiz verdict renders on the reply, since the key stays on the server.
* A right quiz answer moves on after 700 ms (`prefs.words_autonext`, default on).

**Data.** `words.today_summary(learner, tz) → {due, proofs, new_goal, new_today, minutes, done,
title, reason, start: {path: '/api/words/run', body}}`. `done` = nothing due and the new goal met,
or a Today's words run finished today. The run is a server session, so it resumes on any device.

**Acceptance.**
1. A learner with 12 due, 2 Claimed due and a goal of 10: `POST /api/words/run {mode:'mix',
   deck:{source:'today'}}` stores items in the order Fix, due, proofs, …, with no two
   consecutive items sharing `word` (test_flow).
2. With `box: 5`, after 5 simulated minutes of `ms` the next answer's reply has `next: null` and
   the run is finished.
3. `GET /api/next` for that learner has an item with `kind == 'words'` whose `start.path` is
   `/api/words/run`.
4. The answer reply carries `next` with the next public item.
5. Browser: `/words/`, `/words/study/?mode=quiz` and `/words/mine/` each show `.today-words`
   with a Start button; `/words/run/` does not.

#### W12. Finish by test day: a goal from the exam date, a review-debt breaker and a retention forecast

*From: outcomes #10, experience #10, unfair-advantage #7, the plan and schedule gaps. Effort M.
Builders: S9; S7 (Plan step 4 renders the chips), F4 (prefs).*

**Why.** Theirs caps new words by subscription tier with no link to the exam. Nothing tells a
student whether they will finish, what today's new words cost later, or which words will slip
before the test. A wall of reviews after a few days away is the most common reason students
quit spaced review; ours breaks it up.

* **By exam day card** (the Words top, My words, Plan step 4), when `exam_date` is set:
  * "Nov 7 · 45 days · core: 180 left · advanced: 310 left · transition logics: 3 of 9 not yet
    known";
  * "168 of 212 studied words likely to hold on test day · 44 at risk" with **Review at risk
    (44)**. The per-word estimate is p = 2^(−t/h), h = the word's current interval × the
    learner's scale (W13) × 0.8^lapses, t = days from its last right answer to the exam; likely
    is p ≥ 0.8. A "How this is worked out" disclosure explains it (U13).
  * **New words a day** chips 0 · 5 · 10 · 15 · 20 · 30 · **Auto**, each with its finish date
    and review load two weeks out ("12 a day: core done Nov 24 · about 45 reviews a day, 8
    min"). Auto = ceil(core and transitions left ÷ max(1, days to exam − 10)), between 5 and 40.
    Picking a chip writes `prefs.words_goal`.
  * Falling behind is priced: "3 days missed: 14 a day keeps Nov 24, or stay at 12 and finish
    Nov 28", one tap each.
  * The load comes from `words.simulate(learner, goal)`: an expected-value run of the §12
    schedule with the learner's own lapse rate (default 0.2), pure, with an assert self-check.
* **Review debt**: when today's due count is over max(60, twice the learner's 14-day median of
  daily reviews), the Due tile and the Today's words panel read "84 due after 5 days away" and
  offer **Spread over 4 days** (caps daily reviews at ceil(due / 4), most overdue ÷ interval
  first, and pauses new words until the backlog is 1 day or less; `prefs.words_spread` = the end
  date) or **Do all now**. The forecast draws the spread as stacked bars.
* **Forecast**: My words' 14 daily bars continue as weekly bars to the exam, with the exam day
  marked.
* **Fuzz**: intervals of 3 days or more get ±10%, seeded by (learner, word, reps), so 30 words
  learned on one day don't all return on one day.
* **New deck order by test value**: SAT entries carry an authored `value` (1–3: how often the
  sense turns up in SAT-style answer choices); see §3 override for the full order.
* **Final 10 days**: no new advanced words; Today's words puts at-risk words first; the card
  reads "Final 10 days · reviews and at-risk words only". This sits on top of the spec's exam
  cap.

**Data.** `prefs.words_goal` becomes an integer 0–40 or `'auto'` (R11); `prefs.words_spread`
(date | null). `GET /api/words/insights` adds `finish: {left: {core, advanced, logics}, chips:
[{goal, core_done, advanced_done, load_2w, minutes}], at_risk, likely}` and `forecast_to_exam:
[{week, n}]`. Deck source `atrisk`.

**Acceptance.**
1. `PYTHONPATH=. python3 -c "import server.words as w; w._simulate_selfcheck()"` passes.
2. With `exam_date` today+45 and 180 core words left, `insights.finish.chips` has 7 entries and
   the Auto chip's goal equals `ceil(left / 35)` clamped to 5–40.
3. A learner with 90 due and a 14-day median of 20: `/api/words` has `debt: {due: 90, spread:
   23}`. After `PUT /api/me {prefs:{words_spread: today+4}}`, a Today's words run holds 23 due
   items and no new words.
4. Over 30 words graded Know on one day at box 2, their due dates span at least 2 distinct days.
5. With `exam_date` today+8, the New deck contains no `tier: advanced` words.

#### W13. The schedule measures itself: recall on due reviews, a per-learner scale, the word wall and each word's journey

*From: experience #11, outcomes G16. Effort S. Builders: S9; S6 (the Results block).*

**Why.** Their only progress numbers are counts. Ours shows every word's state at a glance, why
each word is where it is, and whether the schedule is working.

* **Recall on due reviews** (My words, Results): "Recall on due reviews, 30 days: 88%",
  counting only on-time due reviews (not early, not new), per box, against an 85–95% band.
  "Ready for test day: 212" = Known words not due again before the exam.
* **Per-learner scale**, stateless: over the last 50 on-time due reviews, recall above 95% →
  intervals × 1.2; below 80% → × 0.8; otherwise × 1. My words says "Your intervals: ×1.2 (you
  recall 96% of due words)".
* **The word wall** (a My words view beside the table): every word of the selected collection as
  a 12px cell in rows by level. Outline = new; 30% ink = learning; ink = claimed; orange =
  Known; an amber dot = due today; a knot = stubborn. Hover or focus: "mitigate · Known since Sep
  14"; click opens the sheet; arrow keys move; the legend carries counts. On a phone, tapping a
  row enlarges its cells to 44px targets.
* **Journey** (the sheet's YOUR RECORD): a timeline of every review, orange ● right, graphite ○
  wrong, a glyph per format (card / pick / in context), with the next due date and the exam date
  marked; hovering a point shows the pick and its trap.
* **Graduation** in the run summary: a word reaching Known shows "seen Sep 3 → missed Sep 6 → in
  context ✓ Sep 23".

**Data.** `insights.recall: {pct, n, by_box, scale}`; `GET /api/words/{slug}` adds `journey:
[{at, kind, correct, given, trap}]`.

**Acceptance.**
1. A learner with 50 on-time due reviews, 49 right: `insights.recall.scale == 1.2`, and the next
   box-2 Know sets due to today + round(7 × 1.2 ± fuzz).
2. `/words/mine/?view=wall` renders one `.wcell` per word of the collection, each with an
   aria-label naming its status.
3. `GET /api/words/mitigate` has `journey` with one entry per review, newest last.

#### W14. Browsing is reviewing, and a star means study soon

*From: outcomes G5, G12, experience G10. Effort S. Builder: S9.*

* **Covered sheet**: with Meanings off (the self-test grid), a tile opens the sheet covered:
  MEANING and everything below sit behind **Show** (Space); the footer offers **Don't know** (1)
  and **Know** (2), filed as a card review under §12 (early reviews don't promote); ← → page to
  the next tile front-first. With Meanings on, the sheet opens uncovered, as the spec says.
* **Star = study soon**: starred words go to the front of New (after looked-up words); a starred
  word not reviewed for 14 days joins Today's words; the exam cap applies to starred words at
  any box (each gets one review in the last 7 days). The Saved tile reads "Saved 12 · 4 not
  started".

**Acceptance.**
1. On `/words/` with `m` unset, clicking a tile opens the sheet with `.meaning` hidden; Space
   shows it; 2 posts one card review.
2. A starred box-0 word is first in the next New deck.

### D. Pace and play

#### W15. SAT pace: a pace timer, time per type, and the Words check

*From: unfair-advantage #5, outcomes G8, experience G6. Effort M. Builders: S9, F3 (exam mode
for word items).*

**Why.** Their timer is a stopwatch with no round, score or end. Ours rehearses the vocabulary
questions at the R&W section's own pace and reports time and traps per type.

* **Timer** adds **SAT pace (71 s)**: 32:00 ÷ 27. Every item's time is recorded; the summary
  shows the median per type against 71 s, and "Rushed misses (wrong in under 8 s): 3 · slow down
  on these", with a Slow to answer deck of the slowest words.
* **The Words check** (Quiz setup ▸ Words check; the summary's Up next): 12 items in 14:12 (12 ×
  71 s): 6 in context (1–2 of them `nearly`), 4 transitions, 2 most precise. Two stages: after
  item 6, the second half moves up a difficulty step when 5 or more were right, as module 2
  routes. It runs in R21's exam mode (navigator, Mark for review, strike, Check your work),
  with no feedback until the end and tap-to-define off.
* **Report**: the score; pace per item against 71 s; right/asked by type and by trap; every miss
  with its trap reason; the words behind the misses added to Missed lately; **Twin every miss
  (N)**, a quiz run of "same trap, new word" per miss.

**Data.** Timer value 71; run `mode: 'check'` (sessions kind `words`, listed by
`/api/history?kind=words` as "Words check").

**Acceptance.**
1. `POST /api/words/run {mode:'check'}` returns 12 public items and `timer_total == 852`.
2. In test_flow, 5 right of the first 6 makes items 7–12 one difficulty step up from 1–6.
3. No `.term` element exists on `/words/run/?id=<check>` before it finishes.

#### W16. Sprint: 60 seconds, one key per word, a personal best

*From: experience #12. Effort S. Builder: S9.*

* Quiz ▸ **Sprint**, 60 s or 120 s, of Meaning → word or transition-logic items from Learning
  and Known words. One key (or tap) answers and moves on at once; a slim timer bar; misses
  collect in a tray.
* End: score = right − wrong ÷ 3; "best 23 · today 26" and **New best** only when beaten; the
  tray with meanings and **Study these** (a cards run of them).
* Sprint answers (mode `sprint`) never promote. A miss marks the word Missed lately without
  dropping its box: a miss under time pressure is not a failed recall.

**Acceptance.** A sprint run's wrong answer leaves `box` unchanged and sets the word's `missed`
flag; `finish` returns `best` and `new_best`.

### E. Content that stays right

#### W17. A bigger, cleaner, sense-level library

*From: the size gaps of all three (outcomes G1, experience G1), unfair-advantage #4, G7,
outcomes G6, G17. Effort L (content). Builder: S9.*

**Why.** Decision 2 leaves about 820 entries against their 1,002, and a word with two senses
shares one state, so knowing the common sense of "qualify" marks the tested one Known.

* **Size**: SAT core about 400, SAT advanced about 600, transitions about 80, and about 100
  second senses as their own entries: about 1,180. Roots (W4) are not counted as words.
* **Per-sense slugs** for split words (`qualify.limit`, `qualify.meet`), so each sense has its
  own `word_state`. The sheet shows the other sense's status: "Other meaning · meet a
  requirement · Known".
* **Lists** (curated collections over entries, via `lists` on each entry):
  * **Second meanings** (`second-sense`): the senses the SAT tests that are not the common one.
  * **Answer-choice language** (`answer-choice`, about 90): the verbs and stance words R&W
    answer choices are written in (qualify, concede, undermine, corroborate, substantiate,
    illustrate, dismiss, reconcile, speculate, underscore, refute, characterize, critique;
    ambivalent, skeptical, wry, earnest, dismissive, nostalgic, measured, reverent, indignant…).
    Each carries `uses`, shown on the sheet as **HOW THE SAT USES IT**: "In answer choices: “It
    qualifies the claim made in the previous sentence.”"
* **New fields**: the W1 features, `value` (W12), `partners` (W8), `shade` (W3), `uses`,
  `lists`. `pos` is required on every entry. `match` is derived from `word` + `also`.
* **Count shown**: the H1 meta and the plan landing read the live count; the build fails on a
  duplicate (word, sense).

**Acceptance.**
1. `GET /api/words | jq '[.words[]|select(.own|not)]|length'` is at least 1100.
2. `jq '[.words[]|select(.own|not)|(.word|ascii_downcase)+"|"+(.sense//"")]|(length==(unique|length))'`
   is true.
3. `jq '[.words[]|select(.own|not)|select(.pos==null)]|length'` is 0.
4. `GET /api/words/qualify.limit` has `other_senses[0].slug == 'qualify.meet'`; grading one
   leaves the other's `box` unchanged.
5. `jq '[.words[]|select(.lists|index("answer-choice"))]|length'` is at least 80.

#### W18. Crowd difficulty, pick splits, "Another choice also fits", and distractors that police themselves

*From: unfair-advantage #11, outcomes G4, G11, experience G8, G14. Effort M. Builders: S9, F6
(the report kind), S1 admin (the suppress queue in `/admin/reports`).*

**Why.** Their levels are authored guesses and their near-synonym distractors ship unchecked,
reportable only through a long form. Ours measures difficulty and catches a bad distractor
before most students see it.

* **Measured difficulty**: after 20 first-try in-context answers across learners on a word as
  key, its tile bars and the sheet read from the real accuracy ("58% right in context"; 75%+
  easy, 45–75% medium, under 45% hard). Until then the authored level shows with "est.".
  Sorts **Most missed by students** and **Hard for you** (your lapses and Thought I knew).
* **Pick split** on every generated verdict after 20 first tries on that frame (W1's crowd
  line).
* **Another choice also fits**: one tap on any verdict files an R17 report (kind `word`, category
  "More than one right answer", context = the item's address and the student's pick) with no
  form; a toast confirms, with Undo.
* **Auto-guard**: a (frame, distractor word) pair is suppressed from generation when it is picked
  by 35% or more of first tries from learners with 80%+ in-context accuracy (20 or more such
  answers), or after 3 "also fits" reports from different learners. It is queued in
  `/admin/reports` with **Unsuppress**.
* **Report on a word** gains **Suggest a better meaning or example**, prefilled with the current
  text to edit. U3's fix-once applies: an accepted fix is edited into the JSON, the entry carries
  `corrected: date`, the sheet shows "Corrected Sep 24 after a student report", and each reporter
  gets U3's reply.

**Data.** Table `word_suppress(frame TEXT, word TEXT, why TEXT, at TEXT, PRIMARY KEY(frame,
word))`, read by the generator. `/api/words` rows add `measured: {pct, n} | null`.
`ponytail:` crowd figures are recomputed with a 10-minute memo; move to a nightly table if it
shows in profiles.

**Acceptance.**
1. With 20 seeded first-try answers on a word, 11 right, `/api/words` gives it `measured.pct ==
   55` and its tile `.dbars` reads Medium.
2. Three "also fits" reports from different learners on one (frame, word) create one
   `word_suppress` row, and 200 later items from that frame never offer that word.
3. The verdict's "Another choice also fits" makes exactly one `POST /api/report` with `kind:
   'word'` and no dialog opens.

### F. Bring, share, daily, offline

#### W19. Bring your words: paste a text, paste a word list, log a missed official question

*From: experience #8, unfair-advantage #8, outcomes G15, unfair-advantage G14. Effort M.
Builders: S9; F2 (the quick sheet's Add a word tab and Log a mistake type).*

**Why.** Their button adds one typed word and covers Next. Ours turns a passage, a book's list
or a missed Bluebook question into scheduled, quizzable words in one step.

* **Bring words ▾** in the Words title row, and a **Paste text** mode in the quick sheet's Add a
  word tab:
  * **From a text** (up to 20,000 characters): the text renders with library words underlined
    and marked new ○ / learning ◐ / known ●, matched in the browser from `/api/words/index`
    (nothing is sent until the student saves). A side table groups "4 new · 3 learning · 5
    known" with checkboxes, **Star the 4 new** (front of New), and **Save as a list** (default
    name "From pasted text · Sep 23"). Words of 7 or more letters not in the library or the
    common-word list are offered under **Not in the library**, each with **Make it my word**
    (meaning required).
  * **A word list** (words only, one per line or comma-separated, up to 1,000): each is matched
    to a library entry (`also` forms, case, accents): "380 of 400 found · 20 added as own words
    for you to fill in", saved as a named list of our entries with our meanings. No one else's
    definitions are copied.
  * **A question I missed** (also a "Words in Context / Transitions" type in the quick sheet's
    Log a mistake, U2): the 4 choices (autocompleted from the library), which was right, which I
    picked, and the text (optional). On save: the trap is classified from the features (pick vs
    key: lookalike, reversed, too strong / weak, tone, topical, logic A→B, or "Not
    classified"); both words are starred and due today; words not in the library become own
    words with the meaning to fill; the four are saved as a list ("Bluebook · Test 4 · Q12");
    the trap is logged (mode `outside`) into W5's profile; **3 twins** (same trap, new word) and
    **Quiz the set** start from the result.
* **Own words get more**: an own word whose example contains it gets Fill the blank items; on
  save it is linked to library lookalikes ("Looks like “illusory” in the library").

**Data.** Table `word_lists(learner, name, words JSON, created, PRIMARY KEY(learner, name))` for
lists that hold library slugs (own words keep `my_words.list`; `progress.carry` moves it).
`POST /api/words/lists/match {text}` → `{found: [slug], missing: [word]}`. `POST /api/words/lists
{name, words, own}`. `POST /api/words/outside {text?, choices[4], key, picked, label}` → `{trap,
list, run}`. `/api/words/index` serves SAT words' matchers.

**Acceptance.**
1. `POST /api/words/lists/match {text:"mitigate\nubiquitous\nzzqx"}` returns 2 found and
   `missing: ['zzqx']`.
2. `POST /api/words/outside {choices:['refute','question','support','describe'], key:'question',
   picked:'refute'}` returns `trap: 'too_strong'`, a list, and a run whose first item's stored
   options include a too_strong distractor.
3. Browser: pasting a 3-sentence text with two library words into From a text underlines exactly
   those two and makes no network request until Save.

#### W20. Share a list, class word goals, and printed worksheets with keys

*From: experience #13, unfair-advantage #10. Effort M. Builders: S9; F6 (`sets` kind `words`), S2
(the class assignment kind).*

* **Share**: any list or Library filter view has **Share**. It makes `sets` kind `words` (R18c)
  and `/s/?c=CODE`. The landing reads "Transitions for Friday · 30 words" with the list, **Add to
  my words** (library words into a new list; own words copied) and **Quiz them now**.
* **Class word goals** (R4, S2): an assignment kind `words` = a list plus a goal (Known by a
  date, or reviewed on N days). The teacher sees student × Known / Claimed / Learning / New /
  last review, sortable, and each word's class miss rate in context ("temper · 62% missed").
  Students see it in Today's Due list and as Up next's `assignment` row. S9 provides
  `words.assignment_progress(learner, list)`.
* **Worksheets**: **Print** beside Start in study setup: deck or words; types (In context /
  Transitions / Most precise / Meaning → word / Type it); 10–40 items; the key on a separate page
  (on). The sheet is serif, numbered, 4 options with bubbles, a name and date line, and a header
  code ("W-7KQ2 · 20 questions · Sep 23"). The key page gives each letter, a one-line trap reason
  per wrong option, and the word's meaning. **Grade a worksheet** takes the code and the letters
  ("CABD…"), files them through the run, updates word states and traps, and shows the summary.
  **Same sheet again** reprints by code; **New version** keeps the words and types with new
  seeds. A class assignment can go out as worksheets, each student with their own version.

**Data.** A worksheet is a word run with `mode: 'print'`; `/words/print/?id=` renders it;
`POST /api/words/run/{id}/grade {letters}`.

**Acceptance.**
1. `POST /api/sets {kind:'words', items:['mitigate','bolster']}` returns a code whose landing
   lists both words.
2. `POST /api/words/run {mode:'print', formats:['incontext'], count:10}` then `…/grade
   {letters:'AAAAAAAAAA'}` returns a summary with `asked == 10` and files 10 `word_reviews`.
3. Two `New version` prints of one sheet have the same words and different stored seeds.

#### W21. Word and transition of the day, answerable

*From: experience G17, unfair-advantage G19. Effort S. Builders: S9; S3 (T14 renders it).*

* `words.daily_item(day, 'wic')`: one in-context item, the same for everyone that day. The word is
  `daily.word(day, 'sat')`; the frame and seed come from sha256('wic:' + day). It is T14's third
  day's-question slot, recorded once through `words.record_daily`.
* On `/words/`, the **Word of the day** tile is that same item: answered on Today it shows its
  result here, and the reverse. After answering: the key, the reasons, the crowd split (20+),
  and Add to my words.
* The Math word of the day tile becomes **Transition of the day** (`words.daily_item(day,
  'transition')`), on `/words/` only, the same for everyone.

**Acceptance.** `GET /api/words/today` for two learners on one day returns the same `wic` and
`transition` item ids and no key; answering the `wic` item on `/words/` makes Today's third slot
show as answered.

#### W22. Offline cards on the phone

*From: outcomes #12, experience #4 (offline). Effort M. Builders: S9 (`web/words/sw.js`, the
queue), F2 (the manifest, and the shell §2.14 exception).*

**Why.** Five minutes without signal on a bus is five lost reviews. Cards carry no hidden key,
so they can go offline safely.

* A service worker scoped to `/words/` caches the runner and the Words content. **Take today's
  cards offline** stores the due and new card faces in IndexedDB (try/catch around every read
  and write).
* Offline grades queue with `item_id` and `at`, and replay in order on reconnect; the server
  claims each answer once, so a replay is safe. It applies §12 at the given `at`, which must be
  within the last 72 hours and not in the future (else 422). `progress.days` counts reviews by
  `at`, so a subway review keeps the streak.
* A banner reads "Offline · 14 grades will sync". Quiz types say they need a connection.

**Acceptance.**
1. `POST /api/words/run/{id}/answer {…, at: now − 2h}` files the review with that `at`; `at: now
   − 80h` returns 422.
2. Browser, offline emulated after Take today's cards offline: the cards run advances through the
   stored cards, and reconnecting posts the queued grades.

---

## 3. Spec overrides

### 3.1 Inside §3.8 (spec/rebuild-v2.md lines 9134–10029)

Each entry quotes the current text, then gives the replacement or addition.

1. **Box at the top** (9138).
   * Quote: "> **Read with resolutions:** R1, R10, R11, R13, R17, R24, R25, R29, R36 (§2.2).
     Where this spec disagrees with them, they win."
   * Append: "Read with `spec/v2-decisions.md` item 2 (SAT R&W vocabulary only, no Math
     language) and `spec/v2-upgrades/words.md` (W1–W22), which win over this section."

2. **Review change 1** (9217).
   * Quote: "With the math groups that makes about 1,090 distinct entries, more than theirs,
     and the build fails on a duplicate."
   * Replace with: "With about 100 second senses as their own entries that makes about 1,180
     distinct entries (W17), more than theirs, and the build fails on a duplicate."
   * Quote: "- **SAT words: core**, about 300 words." / "- **SAT words: advanced**, about 450
     words." / "- **Transitions**, about 70 words and phrases, grouped by logic."
   * Replace the numbers with 400, 600 and 80.

3. **Review change 2.** Quote: "- **meaning mix-ups** (median / mean);" Delete it.

4. **Review change 3.** Quote: "- the 19 math topics by domain;" Delete it, and add after the
   list: "Family ▾ (W3) and a Roots group (W4) join the filter bar."

5. **Review change 4.** Quote: "4. **A word with no bank link had no difficulty.** Every entry
   now carries an authored `level`. The bank-derived difficulty wins where it exists."
   Replace with: "4. **Every entry carries an authored `level`.** Measured difficulty from
   first-try in-context answers wins after 20 of them (W18)."

6. **Review change 11.** Quote: "- it has a reason line and three launch buttons: **Review
   cards**, **Learn 10** and **Quiz**;" Replace with: "- it has a reason line and one launch,
   **Today's words** (W11), with Review cards, Learn 10 and Quiz in its ⋯ menu;"

7. **Review change 13.** Quote: "13. **"Known" could be earned in three days**, because an early
   review promoted the word. Now only a due card (or a new one) moves up, while an early wrong
   answer still drops it. Known means right three times over at least ten days." Replace the
   last sentence with: "Known is box 4, reached only by a right, unguessed in-context answer on
   a due review; a self-graded Know stops at box 3 (Claimed) (W7)."

8. **Review changes 16, 17 and 18** (the sheet's drill session, the `_pick` fallback, bankless
   confusions). Delete all three: Words makes no drill sessions (decision 2). The sheet's sample
   needs no session (W1).

9. **Review change 21.** Quote: "- **Looked up**: a word tapped inside a question goes to the
   front of the New deck;" Replace "inside a question" with "inside a Words text". Quote: "-
   **two** words of the day (math and SAT), like their two questions of the day;" Replace with:
   "- an answerable Word of the day (Today's third slot) and Transition of the day (W21);".
   Quote: "- tap-to-define in rationales too, never on options;" Replace with: "- tap-to-define
   on non-option library words in Words texts;".

10. **§0 What it is** (9279). Quote the block from "Words is the vocabulary section: one set of
    tools over three kinds of word." through "3. **My own**: the student's own words, in their
    own lists." Replace with:
    "Words is the SAT Reading & Writing vocabulary section (decision 2): one set of tools over
    1. **Reading & Writing words**: SAT words (core and advanced), transitions, second meanings
       and answer-choice language (W17), with SAT-form items generated without limit: Words in
       Context, Most precise, Order the ladder and Transitions, every wrong option naming its
       trap (W1–W3);
    2. **Roots**: about 80 parts that decode words never studied (W4);
    3. **My own**: the student's own words and lists, including pasted texts, word lists and
       missed official questions (W19)."

11. **§1 Words tabs** (9303). Quote: "- **Words tabs** (`UI.wordsTabs(host, active)`): a
    4-segment control under the H1". Add before it: "- **Today's words panel** (W11) under the
    H1 on every Words page but the runner, above the tabs."

12. **§2 content files** (9316). Quote: "The content is authored as JSON under `server/words/`:
    `math.json`, `sat.json`, `transitions.json`, `confusions.json` and `collections.json`."
    Replace the list with: "`sat.json`, `transitions.json`, `confusions.json`,
    `collections.json`, `classes.json`, `traps.json`, `frames.json`, `fills.json`, `pairs.json`,
    `roots.json` and `foils.json` (W1–W4, W10)."

13. **§2 Entry fields.**
    * Quote: "- `pos`: n. / v. / adj. / adv. / phrase. Required on SAT words and transitions,
      optional on math words." Replace with: "- `pos`: n. / v. / adj. / adv. / phrase. Required
      on every entry."
    * Quote: "- `topics`: bank topic slugs for math words; subject tags for SAT words; the logic
      group for transitions." Replace with: "- `topics`: subject tags for SAT words; the logic
      group for transitions."
    * Delete the `symbols`, `figure`, `cloze_templates` and `bankless` bullets.
    * Quote: "- `match`: regexes that find the word in stems." Replace the bullet with: "-
      `match`: derived by the build from `word` and `also`; not authored."
    * Quote: "- `gloss`: underline inside questions. False for tiny words like \"of\" and
      \"per\"." Replace with: "- `gloss`: underline in Words texts (default true)."
    * Add: "- W1's `class`, `polarity`, `intensity`, `pattern`, `subjects`; `value` (1–3, W12);
      `lists`, `uses` (W17); `partners` (W8); `shade` (W3); `corrected` (W18)."
    * Quote: "- `cloze`: 1–3 fill-in items using `____`. For SAT words each is a 2–3 sentence
      \"In context\" text." Add: "Each is a fixed frame with need tags (W1); second-sense entries
      add at least one `nearly` text."

14. **§2 Collections** (9342). Quote the heading "###### Collections, about 1,090 entries" →
    "###### Collections, about 1,180 entries". Delete the **MATH LANGUAGE** block (from "**MATH
    LANGUAGE**" through the Geometry & Trig bullet). In **READING & WRITING**, set core to about
    400 and advanced to about 600, transitions to about 80, and add "- **Second meanings** and
    **Answer-choice language** (lists over entries, W17)." Add a **ROOTS** group: "about 80
    roots, prefixes and suffixes (W4)."

15. **§2 Confusions** (9372). Quote: "About 40 meaning mix-ups, about 60 lookalikes and the split
    senses. Each has `id`, `kind` (meaning | lookalike | sense), `words` [2], `tell` (one
    sentence that separates them), `links` [{template, reason regex}] for math, and `bankless`
    when there are no links." Replace with: "About 80 lookalikes and the split senses. Each has
    `id`, `kind` (lookalike | sense), `words` [2] and `tell`." Delete the "Meaning mix-ups"
    bullet and the "**Linking is curated, not guessed.**" block through "`tools/build_words.py`
    proposes links, and an author confirms them in the JSON."

16. **§2 Derived per word** (9389). Replace the whole list with: "Per sense: the frames where it
    is a legal key and their count, its family ladder (W3), its root family (W4), its gloss
    matchers. Per frame: its legal keys and trap kinds."

17. **§2 Build checks** (9398). Delete: "- A math word with no link and no `bankless`.", "- A
    confusion link that matches on none of 20 seeds.", "- A `cloze_template` whose stem no
    longer contains the word." and "- A `match` regex outside the restricted syntax." Add:
    "- An SAT sense that is a legal key in fewer than 2 contexts, or a context with fewer than 3
    legal traps for it. - A failing `rw_items.py` self-check. - A root split that does not
    re-join its word. - A foil that is a library word or a dictionary word. - A class used by
    `order` with fewer than 4 distinct intensities, or with no `dimension`. - An SAT entry with
    no `value`." Quote: "The tool prints proposed new links for an author and never writes them."
    Delete it.

18. **§3 Title row** (9415). Quote: "- H1 \"Words\", with the meta line \"1,090 words · 31 known ·
    12 due\" beside it." Replace with: "- H1 \"Words\", with the meta line \"1,180 words · 212
    known · 64 claimed · 12 due\" beside it." Quote: "- On the right, a search field and **Add a
    word** (quiet, + icon)." Replace with: "- On the right, a search field, **Bring words ▾**
    (W19) and **Add a word** (quiet, + icon)."

19. **§3 Today strip.**
    * Quote: "- **Due today**: a big number and a **Review** pill that starts the due flashcard
      deck directly." Add: "Past the debt threshold it reads \"84 due after 5 days away\" with
      Spread over 4 days (W12)."
    * Quote: "- **Math word of the day**: the word (700 20px), its `short` and **Open**." Replace
      with: "- **Transition of the day**: an answerable generated transitions item (W21)."
    * Quote: "- **Word of the day** (SAT): the same layout." Replace with: "- **Word of the
      day**: the day's in-context item, the same one as Today's third slot, answerable here
      (W21)."
    * Add after the strip: "- **By exam day** (W12), full width, or \"Set your SAT date to see
      your finish line\"."

20. **§3 Collections.** Quote: "4. **Collections**: three labelled groups, MATH LANGUAGE ·
    READING & WRITING · MINE, led by an **All** tile." Replace with: "4. **Collections**: three
    labelled groups, READING & WRITING · ROOTS · MINE, led by an **All** tile. Transitions opens
    the logic map (W2); Roots turns the grid into root tiles (W4)."

21. **§3 Filter bar.**
    * Quote: "- the 19 math topics by domain, each with its glyph and a count;" Delete; add
      "- roots (W4);" and a separate chip "- **Family ▾** (W3)".
    * Quote: "- **Status ▾**: All / New / Learning / Known / Due today / Saved / From my mistakes
      / Missed lately / Looked up / Two meanings / My own, each with a count." Replace with: "-
      **Status ▾**: All / New / Learning / Claimed / Known / Due today / Saved / Missed lately /
      Thought I knew / Fell for a trap ▸ / Stubborn / At risk / Looked up / Two meanings / On a
      ladder / Has a root / My own, each with a count."
    * Quote: "- **Sort ▾**: A–Z / By topic / Most used in the bank / Due soonest / Weakest first
      / Level / Recently added." Replace with: "- **Sort ▾**: A–Z / By topic / Test value / Due
      soonest / Weakest first / Hard for you / Most missed by students / Level / Recently
      added."

22. **§3 Legend.** Quote: "`●●●○○ strength · DUE · ★ saved · ● from your mistakes · ▮▮▯
    difficulty`" Replace with: "`●●●○○ strength · ✓ proven · DUE · ★ saved · ● fell for a trap ·
    ⌇ stubborn · ▮▮▯ difficulty (est. until measured)`".

23. **§3 Grid tile.** Quote: "- Top-right corner: ★ (orange fill when saved), an orange dot for an
    open mistake, and \"DUE\" in amber-deep mono when due." Replace "an orange dot for an open
    mistake" with "an orange dot when the last in-context miss named a trap, a ✓ when proven, a
    knot when stubborn". Quote: "- Hover shows `tile-2`. A click opens the word sheet (`?w=slug`)."
    Add: "With Meanings off the sheet opens covered (W14)."

24. **§4 Word sheet, chip row.** Quote: "- **Chip row**: the collection chip, topic chips (`UI.chip`
    with a glyph for math topics), the level with its bars, and, for math words, \"Used in 14
    kinds of bank question\"." Replace with: "- **Chip row**: the collection and list chips,
    subject chips, and the level with its bars (measured, or est., W18)."

25. **§4 Word sheet, blocks.**
    * Quote: "- **IN SYMBOLS**, and **FIGURE** when there is one (math)." Replace with: "-
      **SHADES** (W3), **BUILT FROM** (W4), **HOW THE SAT USES IT** (answer-choice words, W17),
      and the other sense's status for split words."
    * Quote the block from "- **IN A REAL QUESTION** (math words with bank > 0):" through
      "Loading shows \"Finding one…\". A failure shows \"Could not make one.\" with Try again."
      Replace with W1's **IN AN SAT-STYLE QUESTION** (sample, Answer it inline, Another; no
      session).
    * Quote: "- For linked math mix-ups, a meta line reads \"An option in 7 kinds of question is
      built on this mix-up\"." Delete. Quote: "- When the student has picked such an option, an
      orange dot and \"You fell for it 3× · last Sep 21\"." Replace with: "- When the student
      has picked the other word for this one, an orange dot and \"You picked it for this 3× ·
      last Sep 21\" (from `word_reviews.given`)." Quote: "- **Drill it** (`POST /api/drill
      {confusion, count:10}`) opens the practice session. It is absent for bankless
      confusions." Replace with: "- **Drill it**: a 6-item quiz run of the pair (deck `pair`)."
    * Quote: "- for math words, \"Questions that use it: 9 answered · 6 right\" with a mini bar,
      read from `attempts` on the linked templates;" Replace with: "- the 5-step ladder (W7), the
      journey timeline (W13), \"Last time you picked …\" and the hook (W9);". Quote: "- \"First
      seen Sep 12\" and \"Looked up 2× in questions\"." Replace "in questions" with "in Words
      texts".

26. **§4 Footer** (9504). Quote: "- Math words: a **Practice 10 questions with it** pill (`POST
    /api/drill {word, count:10}`) and **Flashcards from here** (quiet)." Delete. Quote: "- R&W
    words: a **Flashcards from here** pill and **Quiz it with its lookalikes** (quiet)." Replace
    with: "- A **Practise 10 in context** pill (W1), **Flashcards from here** and **Quiz it with
    its lookalikes** (quiet)."

27. **§5 Study setup, DECK.**
    * Quote: "- New (\"Next 10 from the skills you're working on\")." Replace with: "- New
      (\"Next 10 by test value\")."
    * Quote: "- From my mistakes." Replace with: "- Claimed (prove them). - Thought I knew. -
      Fell for a trap ▸. - Stubborn. - At risk."
    * Add first: "- **Today's words** (W11)." Add after "- A topic ▸.": "- A family ▸. - A
      root ▸."

28. **§5 HOW MANY, SHOW FIRST.** Quote: "3. **Cards only**: SHOW FIRST Word · Meaning · Mixed;
    ORDER Due first · Shuffle · A–Z." Replace SHOW FIRST with "Word · Meaning · In a sentence ·
    Commit first · Mixed" (W7, W8).

29. **§5 Quiz types.**
    * Quote: "- **QUESTION TYPES**, a multi-toggle that needs at least one: Meaning → word · Word →
      meaning · Fill the blank · In context · Pick the transition · In a real question ·
      Translate the phrase." Replace the list with: "Meaning → word · Word → meaning · Fill the
      blank · In context · Most nearly means · Most precise · Order the ladder · Pick the
      transition · Decode it · Type it".
    * Quote: "- In a real question and Translate need math words." Delete.
    * Quote: "- Own words allow the first two types only, and need 4 or more words." Replace
      with: "- Own words allow Meaning → word, Word → meaning, Type it, and Fill the blank when
      their example contains the word; they need 4 or more words."
    * Quote: "- **TIMER per question**: Off · 15 s · 30 s · 60 s." Replace with: "- **TIMER per
      question**: Off · 15 s · 30 s · 60 s · SAT pace (71 s) (W15)."
    * Add: "- **METHOD** Auto · On · Off (W6) and **RELATIONSHIP FIRST** Auto · On · Off (W2),
      each with its current state and reason. - **MODE** Quiz · Sprint (W16) · Words check (W15)
      · Print (W20)."

30. **§5 At a glance.** Quote: "5. **At a glance**: \"20 cards · about 5 min\" (10 s a card, 20 s a
    quiz item, or the timer value)". Replace the parenthesis with "(the learner's median per card
    and per quiz item over 60 days, 10 s and 20 s until there are 20 of each, or the timer
    value)".

31. **§6 Card back.** Quote: "- Content, top to bottom: the word, small; MEANING; EXAMPLES or IN
    SYMBOLS; IN A REAL QUESTION (math, instant from the index); SAME AS / OPPOSITE; up to two NOT
    THE SAME AS rows, then \"+1 more\", which opens the sheet; and **Open word**." Replace with:
    "- Content, top to bottom: the word, small; MEANING; IN A NEW SENTENCE (W8); More examples;
    partners; SHADES (W3); BUILT FROM (W4); SAME AS / OPPOSITE; up to two NOT THE SAME AS rows,
    then \"+1 more\"; \"Last time you picked …\" and My hook (W9); and **Open word**."

32. **§6 Controls and status line.** Quote: "- After a grade, a status line shows for 900ms, then
    the next card: \"Back in 3 days\", \"Again in 3 cards\", \"Known · back in 16 days\" or
    \"Early review · stays Thu\"." Add: "It names the next format when it changes (\"Back Thu as an
    in-context question\", \"Prove it in context to make it Known\"). A due box-3 word is served as
    an in-context item in the card's place (W7). A stubborn word is served as a Fix card (W9). In
    Commit first, the grade buttons are replaced by the 3 meanings and No idea (W7)."

33. **§7 Types** (9565).
    * Quote: "- **In context** (SAT words): an authored 2–3 sentence text with a blank and \"Which
      choice completes the text with the most logical and precise word?\", with 4 words of the
      same part of speech." Replace with: "- **In context**: a generated Words in Context item
      (W1), with the SAT's stem \"…the most logical and precise word or phrase?\"; **Most nearly
      means** for second senses (W1); **Most precise** and **Order the ladder** (W3)."
    * Quote: "- **Pick the transition**: an authored sentence pair with a blank opening the second
      sentence, and 4 transitions from 4 different logics." Replace "an authored sentence pair"
      with "a generated sentence pair (W2)".
    * Quote the bullets "- **In a real question**: …" and "- **Translate the phrase**: …". Delete
      both. Add "- **Decode it** and **Which root do these share?** (W4). - **Type it** (W8)."

34. **§7 Distractors.** Quote: "- Never a word in the target's `same` list, or one sharing a `same`
    entry with it (one hop)." Add: "Generated items (W1–W3) follow W1's feature rules instead: a
    `same` word may appear only as a too_strong, too_weak or connotation trap, which differs from
    the key on the feature the clue fixes." Quote: "1. up to two of the word's confusions,
    including lookalikes, which are the real trap;" keep, for Meaning → word and Word → meaning.

35. **§7 Verdict.**
    * Quote: "- a phrase misreading: \"Wrote it in the order it is read. “Less than” flips the
      order.\"" Delete. Add: "- a generated item: the trap chip, its reason, its check line, the
      clue, and all four options' reasons (W1); a transition names both logics (W2)."
    * Quote: "- A right answer gets a **Why** toggle that shows the meaning and one example."
      Replace with: "- A right answer flashes the clue with the reasons and moves on after 700 ms
      when `prefs.words_autonext` is on (W1)."
    * Quote: "- Links: **Open word**, and on a math confusion **Drill this mix-up in math**."
      Replace with: "- Links: **Open word** · **Same word, new text** (T) · **Same trap, new word**
      (Shift+T) · **Another choice also fits** (W18)."
    * Quote: "- ★ Save and `S` unlock with the verdict." Replace `S` with `B` (§2.8).

36. **§7 Keys.** Quote: "A–D or 1–4 choose, Enter goes on, S saves (after the verdict), O opens the
    word, P speaks it." Replace with: "A–D or 1–4 choose, I marks a guess before choosing (W7),
    Enter goes on, B saves (after the verdict), O opens the word, P speaks it, T / Shift+T another
    like this, W shows a hint (Decode it, Type it)."

37. **§8 Summary** (9611).
    * Quote: "- Quiz only: **By type** (Meaning → word 8/10 · In context 3/5 · Translate 4/5)."
      Replace with: "- Quiz only: **By type** (Meaning → word 8/10 · In context 3/5 · Transitions
      4/5), with median time per type against 71 s (W15)."
    * Quote: "- **Mix-ups**: `.mistake` rows (\"Mixed up median with mean ×2\", \"elusive / illusory
      ×1\"). Each math row has **Drill it in math**, and each lookalike row has **Quiz the
      pair**." Replace with: "- **How you missed**: rows by trap kind and logic pair, each with
      Drill it (W5); lookalike rows with Quiz the pair; word gaps vs reading gaps (W6); the
      calibration line (W7); graduations (W13)."
    * Quote: "- **Up next**: chips for the next deck (\"8 more due\", \"10 new\", \"Quiz these 20\"),
      a **Keep going** pill and a **Library** quiet button." Replace with: "- **Up next**: the
      primary is **Next: {Up next title}** (U1); chips for the next deck (\"8 more due\", \"10
      new\", \"Quiz these 20\") and a **Library** quiet button."

38. **§9 My words** (9627).
    * Quote: "1. **Stat tiles**: 8 in a 4×2 grid (2×4 on a phone)." Replace with: "1. **Stat
      tiles**: 12 in a 4×3 grid (2×6 on a phone)."
    * Quote: "- Known, with the helper \"Right 3 times, over 10+ days\"." Replace the helper with
      "Right in an SAT-style question after 10+ days".
    * Quote: "- From my mistakes, with the helper \"Words behind the mistakes you still have
      open\"." Replace with: "- Claimed (\"Said you know it; prove it in context\"). - Thought I
      knew. - Fell for a trap. - Stubborn. - At risk (with the exam date)."
    * After the Forecast, add: "- **HOW YOU MISS WORDS**, **LOGIC MIX-UPS** (W5), word gaps vs
      reading gaps (W6), **By exam day** (W12), calibration (W7), recall and the interval scale
      (W13). - A **Table · Wall** view toggle (W13)."
    * Quote: "- 14 bars, today in amber and the others in ink at 30%;" Add: "then weekly bars to
      the exam, with the debt spread stacked (W12)."
    * Quote: "6. **Tools**: Add a word · New list · Import · Export CSV · Print this list." Replace
      with: "6. **Tools**: Add a word · Bring words (text · word list · a question I missed, W19) ·
      New list · Import · Share · Export CSV · Print this list · Print a worksheet (W20)."
    * Quote: "- **From my mistakes, empty**: \"None of your open mistakes points to a word.\""
      Replace with: "- **Fell for a trap, empty**: \"No trap has caught you in the last 60
      days.\""

39. **§10 Import sheet.** Quote: "- A textarea for \"One per line: word, then a tab, ' - ', ':' or '
    — ', then the meaning\"." Add: "A line with no separator is read as a word to match against
    the library (W19's word list); only lines with neither a match nor a meaning are \"not
    understood\"."

40. **§11 Tap-to-define** (9689).
    * Quote: "- **Where**: stems and rationales in the practice session, the question of the day,
      the challenge and the report review. Never on answer options, and never in the test window
      or the diagnostic during a sitting." Replace with: "- **Where**: Words' own texts: quiz and
      sheet items (not their options), card-back sentences, Today's Word in context slot after
      answering, and pasted text (W19). Never during a Words check (W15). Math stems and
      rationales are not glossed (decision 2)."
    * Quote: "- **Setting**: \"Underline math words in questions\" on Me, on by default." Replace
      with: "- **Setting**: \"Underline library words in Words texts\" on Me, on by default."

41. **§11 Practice verdict and Mistakes page.** Quote: "- **Practice verdict**: when the named
    mistake is a linked confusion, a line under it reads \"Words: median · mean\"." through the
    Mistakes page bullet ("…the header gains **Review these words (N)**."). Delete both (decision
    2).

42. **§11 Today.** Quote: "- It shows the cards icon, \"Words\", a big \"12\" with \"due\", the meta
    \"4/10 new today\", and **Review**, which starts the due deck." Replace **Review** with "the
    primary **Today's words** (W11), with Review cards, Learn 10 and Quiz in its ⋯ menu; \"212 known
    · 64 claimed\" under the number". Quote: "- Below that, two lines: \"Math word · discriminant:
    how many real solutions a quadratic has\" and \"Word · corroborate: to confirm with evidence\".
    Each opens the sheet." Replace with: "- Below that, one line: \"Transition of the day ·
    answer it\" (the Word in context item is the day's-questions card's third slot, T14)."

43. **§11 Plan.**
    * Quote: "- NEW WORDS A DAY 5 · 10 · 20 (default 10);" Replace with: "- NEW WORDS A DAY 0 · 5
      · 10 · 15 · 20 · 30 · Auto (default 10), each chip with its finish date and review load
      (W12);"
    * Quote: "- NEW WORDS FROM Math language · SAT words · Transitions (multi-select, default Math
      language);" Replace with: "- NEW WORDS FROM SAT words · Transitions (multi-select, default
      both);"
    * Quote: "- It reads \"Words · 12 due · 10 new · about 6 min\". Minutes = due × 10 s + new × 25
      s, capped at a third of the day." Replace the second sentence with: "Minutes =
      `words.minutes_today()`, the Today's words plan at the learner's own pace (W11), capped at a
      third of the day."
    * Quote: "- Launch buttons: **Review cards** (the due deck), **Learn 10** (the New deck) and
      **Quiz** (today's words)." Replace with: "- Launch: **Today's words** (W11); Review cards,
      Learn 10 and Quiz in the ⋯ menu."
    * Quote: "- A reason line, e.g. \"12 words come back today; the new ones are from Circles and
      Percentages, the skills you're working on.\"" Replace the example with "\"12 words come back
      today, 4 of them to prove in context; 10 new from SAT core · medium.\""

44. **§11 Results.** Quote: "- a Words block with a stacked New / Learning / Known bar per group
    (Math language / SAT words / Transitions / Mine), quiz accuracy over the last 30 days, and
    reviews a day over 14 bars;" Replace with: "- a Words block with a stacked New / Learning /
    Claimed / Known bar per group (SAT core / SAT advanced / Transitions / Mine), in-context and
    transitions accuracy over 30 days with the top trap (W5), recall on due reviews (W13), the
    vocabulary-size estimate over time (W10), and reviews a day over 14 bars;"

45. **§11 Achievements.** Quote: "- **Achievements**, handed to Me: 50 / 250 / 1,000 words known,
    every word in a collection known, and a 7-day review streak." Add: "Known means proven (W7)."

46. **§12 Spaced review rules** (9729).
    * Quote: "- **Know on a new word (box 0)**: box 2." through "- **Known** is box 4 or higher, so
      it is reachable no sooner than day 10: know on day 0, then on day 3 or later, then on day 10
      or later." Replace the Know and Known bullets with W7's rules (Learn card and check; boxes
      1–2; box 3 proof; the box-3 cap on self-grades; boxes 4–5 hard set; Claimed and Known).
      Keep "At most one box up per word per local day", the exam cap and "A quiz grades only its
      target word".
    * Add: "- Intervals × the learner's scale (W13), ±10% fuzz on intervals of 3 days or more
      (W12). - Stubborn words run at 1, 2, 5 days (W9). - Placement and triage Know it → box 3,
      due spread over days 3–14 (W10). - Sprint and order answers never move a box (W3, W16)."
    * Quote: "- Missed lately: a wrong or don't-know in the last 14 days with no right answer
      since." Add after it: "- Claimed: box 3, not proven. - Thought I knew: a self-graded Know
      whose next objective check was wrong, within 30 days, no right since. - Stubborn: W9. - At
      risk: W12."
    * Quote the **New deck order** block from "1. Looked-up words and words linked to open
      traps." through "Question-language and phrase words are interleaved one in three."
      Replace with: "1. Starred and looked-up words. 2. Placement's No and Not sure, weakest band
      first (W10). 3. SAT core before SAT advanced (no advanced in the final 10 days, W12). 4. By
      `value`, 3 first (W12). 5. By level. 6. A–Z. All of this is filtered to the plan's New words
      from; transitions are interleaved one in four when both are chosen."

47. **§13 Phone.** Quote: "- The Today strip and the collection groups as horizontal scroll-snap
    rows, with tiles at 78% width and 160px." Add before it: "- The Today's words panel at full
    width with a 48px Start. - By exam day at full width." Add under Runner: "- Order the ladder
    uses 44px drag handles; triage uses swipe right / up / left."

48. **§14 Keys.** Quote: "- Quiz: A–D or 1–4, then Enter; S (after the verdict), O, P." Replace
    with: "- Quiz: A–D or 1–4 (I first to mark a guess), then Enter; B (after the verdict), O, P,
    T / Shift+T, W hint. - Commit first: 1–3, 0 No idea. - Triage: 1 / 2 / 3, Z undo. - Order the
    ladder: 1–4 pick, ↑ ↓ move, Enter check."

49. **§3.8.4 Extras** (9789). Delete the bullets "**Math language wired into the bank**", "**Real
    questions as examples, never the same twice**", "**Practice 10 questions that use this
    word**", "**Mix-up drills (Drill it)**", "**Mistake → words link**", "**Tap-to-define inside
    questions and rationales, logged as Looked up**" and "**Translate-the-phrase quizzes with
    named misreadings**". Quote: "- **Two words of the day, the same for everyone**: A math term
    and an SAT word sit beside the question of the day on Today, using the daily date hash."
    Replace with W21's line. Add one bullet per upgrade W1–W22, each its title.

50. **§3.8.5 Server changes** (9814).
    * Quote the **server/words/*.json** bullet. Replace its file list and counts with override 12's
      files and W17's counts; "Required on every entry: meaning, short (≤60), pos, ≥1 example or
      cloze, the W1 features and `value` (SAT words)."
    * Quote the **tools/build_words.py** bullet ("It generates 20 seeds per template. …"). Replace
      with: "It reads the content, derives the index (override 16), runs `rw_items`' self-check,
      and exits 1 on override 17's checks. It no longer scans the bank."
    * **server/words.py**: delete `of_reason(template, reason)` and `mistake_words(learner)`;
      change `record(learner, slug)` to read `word_reviews` only; the `deck` sources become
      today | due | new | missed | saved | claimed | thought | trap | logic | pair | stubborn |
      atrisk | readgap | lookedup | collection | topic | family | root | mine | list | words;
      add `today_summary`, `me_stats`, `insights`, `simulate`, `daily_item`, `record_daily`,
      `assignment_progress`, `queue_item` (for U1) and `ACHIEVEMENTS`. The runs' `cfg` adds
      `box, method, relation, commit, want_trap`.
    * Quote: "- **server/phrases.py (new)**: …" Replace the bullet with **server/rw_items.py
      (new)**: W1's and W2's generators and verifier, stdlib only, `__main__` self-check.
    * **db.py schema**: `word_state` adds `hook TEXT, proven TEXT, placed INTEGER DEFAULT 0`;
      `word_reviews` adds `template TEXT, seed INTEGER, trap TEXT, conf TEXT, gap TEXT`, mode adds
      sheet | sort | placement | sprint | check | outside | daily, kind adds incontext | nearly |
      precise | order | transition | decode | rootshare | typed | fix; new tables `word_lists`
      (W19) and `word_suppress` (W18); index `word_reviews(template)`. Quote: "LATER_COLUMNS adds
      learners.words_goal INT (NULL = 10, 0 = off), learners.words_from TEXT (JSON list, NULL =
      ['math']) and learners.gloss INT (NULL = on)." Delete (R11 prefs, §3.2).
    * **GET /api/words**: rows drop `bank` and add `proven, claimed, stubborn, at_risk, trap,
      family, roots, value, measured, lists`; counts add `claimed, thought, trapped, stubborn,
      atrisk`; add `estimate` (W10) and `debt` (W12); delete `mistakes` and `from_mistakes`.
    * **GET /api/words/{slug}**: delete `bank_examples` and `record.questions`; confusions drop
      `templates`, and `fell` counts picks from `word_reviews.given`; add `sample`, `shades`,
      `roots`, `journey`, `other_senses`, `measured`.
    * Quote the **POST /api/words/{slug}/example** bullet. Replace it with W1's sample endpoints.
    * **GET /api/words/today**: Quote: "today: {day, math:{slug,word,short,collection,excerpt},
      sat:{slug,word,short,pos,example}}, from daily.word(day, 'math') and daily.word(day,
      'sat')". Replace with: "today: {day, wic: {item, word}, transition: {item}}, from
      `words.daily_item` (W21)."
    * **POST /api/words/run**: modes cards | quiz | mix | sprint | check | print | placement |
      sort; formats meaning2word, word2meaning, cloze, incontext, nearly, precise, order,
      transition, decode, rootshare, typed (delete bankcloze and phrase); timer adds 71; the
      answer body adds `conf`, `gist`, `clue`, `logic`, `order`, `text`, `at`; the reply adds W1's
      and W2's fields, `status_line`, `ladder` and `next`; new `…/another` and `…/grade`.
    * Quote the **drill.py and POST /api/drill: word and mix-up sets** bullet. Delete it.
    * **progress.carry** also moves `word_lists`; `days()` excludes modes lookup, sort and
      placement from review counts.
    * **GET /api/me** words adds `claimed, estimate, calibration, finish, top_trap`.
    * **PUT /api/me** (superseded by R11): `words_goal` ∈ 0–40 or 'auto', `words_from` ⊆ {sat,
      transitions}, plus `words_autonext, words_commit, words_method, words_relation,
      words_spread` (§3.2).
    * **daily.py**: Quote: "word(day, group): a sha256 of 'word:{group}:{day}' over that group's
      library words (math: bank-linked words; sat: core then advanced, weighted to core), the same
      for everyone." Replace "(math: bank-linked words; sat: core then advanced, weighted to
      core)" with "(sat: core then advanced, weighted to core; transition)".
    * **test_flow checks**: delete "a word drill serves only linked templates…", "a confusion
      drill's items carry a matching reason" and "drill feedback lists radius and diameter…". Add
      W1–W22's server acceptance checks (as `server/checks/s9.py`).

51. **§3.8.6 Files.** Delete rows `server/words/math.json`, `server/phrases.py`,
    `server/drill.py` and `web/mistakes/index.html`. Add rows (owner S9):
    `server/words/{classes,traps,frames,fills,pairs,roots,foils}.json`, `server/rw_items.py`,
    `web/words/start/index.html`, `web/words/print/index.html`, `web/words/sw.js`.

52. **§3.8.7 Shared needs.** Quote: "- UI.question(host, q, {head}): a head override (label and
    glyph) for items with no topic, such as word, transition and phrase items." Replace "word,
    transition and phrase items" with "word, in-context and transition items". Add: "- `UI.workspace`
    quiz mode renders `spans` (clue, idea) and per-option reasons, and a staged item (options
    hidden for W6's and W2's first step) (F3). Order the ladder and Type it render in
    `words-ui.js`."

53. **§3.8.8 Acceptance checks** (9975).
    * Check 2: Quote: "prints at least 1000." Replace with "prints at least 1100."
    * Check 4: Quote: "jq '[.words[]|select(.collection|test(\"^sat|^transitions\"))|select(.pos==null)]|length'
      prints 0." Replace the filter with `select(.own|not)`.
    * Check 5: Quote: "contains due, new, learning, known, saved, mine, mistakes, missed, lookedup,
      new_today and goal". Replace "mistakes" with "claimed, thought, trapped, stubborn, atrisk".
    * Check 6: Quote: "Breaking one confusion link regex in a copy of the content makes it exit 1
      and name the link." Replace with: "Removing a frame so an SAT sense has fewer than 2
      contexts makes it exit 1 and name the sense."
    * Check 7: Replace with W1 acceptance 1.
    * Check 8: Add "`template`, `trap`, `traps`" to the forbidden keys.
    * Check 10: Add: "In a Today's words run the same new word is a Learn card, then a Meaning →
      word check 3–5 items later (W7)."
    * Check 13: Quote: "a due word at box 4 graded 'know' gets due ≤ exam_date−1." Replace with "a
      due word at box 4 answered right in context gets due ≤ exam_date−1; a self-graded 'know'
      leaves it at box 4."
    * Checks 14, 15 and 16: delete (decision 2).
    * Check 18: Quote: "GET /api/words/today returns both math and sat words, the same for two
      different learners on the same day." Replace with W21's acceptance.
    * Check 26: Add "Family" to the chips; the Today strip's 4 tiles are Due today, New today, Word
      of the day and Transition of the day.
    * Check 31: Quote: "On /words/?w=vertex the sheet is open with MEANING, IN A REAL QUESTION (an
      excerpt with a highlighted span, and no /api/drill request made yet), NOT THE SAME AS and
      YOUR RECORD. Clicking Answer it makes exactly one POST /api/words/vertex/example." Replace
      with: "On /words/?w=mitigate&m=1 the sheet is open with MEANING, IN AN SAT-STYLE QUESTION (4
      options, no /api/words/run request), NOT THE SAME AS and YOUR RECORD. Answering makes
      exactly one POST /api/words/sample/answer."
    * Check 32: replace "vertex" with "mitigate".
    * Check 35: Quote: "In /practice/session/, a stem containing 'median' has at least one
      button.term." through "No .term is ever inside .opts." Replace with: "In a Words in-context
      quiz item whose text contains a non-option library word, that word is a button.term.
      Clicking it opens .pop with the meaning and fires one POST /api/words/lookup. Escape closes
      it and returns focus. No .term is ever inside .opts, and /practice/session/ has none."
    * Check 37: Quote: "and two word-of-the-day lines matching GET /api/words/today." Replace with
      "and a Today's words primary whose click creates a run with `cfg.deck.source == 'today'`."
    * Check 38: Quote: "the day card shows a Words task with Review cards, Learn and Quiz." Replace
      with "the day card shows a Words task whose primary is Today's words, with Review cards,
      Learn and Quiz in its menu."

54. **§3.8.9 Open questions** (10018). Quote the first bullet ("- R&W words in v1: …"). Replace
    with: "- Resolved 2026-09-23 (decision 2): SAT R&W words and transitions only." Quote the
    "Nav placement" bullet: resolved by R1. Quote the "Tap-to-define in the daily challenge"
    bullet: moot (no math gloss). Quote the content-review bullet and add: "It now also covers
    about 300 frames, 40 transition families, the sense features, 80 roots and 60 foils; the
    verifier checks structure, not wording or features."

### 3.2 Outside the section (Part 2 and sibling lines these upgrades need; I1 applies them with the owners)

| where | change | upgrade |
|---|---|---|
| R1 | Words' nav meta "12 due" becomes "12 due · 9 min"; the phone menu sheet's Words row carries a Start | W11 |
| R10, §2.6 | The drill body's `word` and `confusion` fields and `words.resolve_drill` are not built (decision 2): delete the `word`, `confusion` entries (§2.6 lines on `like`, `word`, `confusion`, `assignment`; the Words row "`word`, `confusion`"; "and `words` / `confusion` when `words.of_reason(template, reason)` exists (S9)"). Source `word-example` is no longer produced | W1 |
| R17 | Word context: one-tap "More than one right answer" with no form (W18's Another choice also fits); category "Suggest a better meaning or example" | W18 |
| R18(c) | `sets.kind` adds `words` (a list of word slugs) | W20 |
| R24 | `word-example` leaves the `cfg.inline` source list (unused) | W1 |
| R25 | Words' "known" achievements count proven Known (box 4) | W7 |
| R4 / S2 Classes | Assignment kind `words` (a list and a goal), read through `words.assignment_progress` | W20 |
| §2.5 | `word_state` + `hook, proven, placed`; `word_reviews` + `template, seed, trap, conf, gap`; new `word_lists(learner, name, words JSON, created)`, `word_suppress(frame, word, why, at)`; index `word_reviews(template)`; `LEARNER_TABLES` and `carry` add `word_lists` | W1, W7, W9, W10, W18, W19 |
| §2.7 prefs | `gloss`: "Underline library words in Words texts". `words_goal`: integer 0–40 or `auto` (default 10). `words_from`: ⊆ {sat, transitions}, default both (math leaves). New: `words_autonext` (bool, true), `words_commit` (auto \| on \| off, auto), `words_method` (auto \| on \| off, auto), `words_relation` (auto \| on \| off, auto), `words_spread` (date \| null) | W1, W2, W6, W7, W12 |
| §2.8 keys | Flashcards and word quizzes: `I` guess (before choosing), `T` / `Shift+T` another like this (after the verdict), `W` hint, `0` No idea (Commit first), `Z` undo (triage) | W1, W4, W7, W8, W10 |
| §2.9 | S9 stops providing `words.of_reason` (F5 feedback words) and `UI.gloss` to S4 / S6 / S8 math stems. S9 adds `words.daily_item`, `words.record_daily` → S3 (already in today.md); `words.queue_item` → F2; `words.assignment_progress` → S2; `words.me_stats` gains `claimed, estimate, calibration, finish, top_trap` → S1 | W1, W5, W7, W10, W11, W20, W21 |
| §2.9 S4 hooks | "word chips in the verdict (`feedback.words`)" and "`UI.gloss` on stem and rationale" are not built (practice.md already drops the first) | decision 2 |
| §2.12 F5 | The `cfg.only` fallback fix is no longer needed by Words | W1 |
| Shell §2.14 | "No service worker" gains one exception: `web/words/sw.js`, scoped to `/words/`, cards only | W22 |
| F2 manifest | `shortcuts: [{name: "Today's words", url: '/words/run/?today=1'}]` | W11 |
| shell-me U1 | New kind `words` after `checks` (row 4b): when `prefs.words_goal > 0` and anything is due or the new goal is unmet; from `words.queue_item(learner, tz)`: title "Today's words · 12 due · 9 min", reason from real counts, `start: {path: '/api/words/run', body: {mode: 'mix', deck: {source: 'today'}}}`, `pts: null` | W11 |
| shell-me U2 | Log a mistake gains a "Words in Context / Transitions" type calling `POST /api/words/outside` | W19 |
| R29 quick sheet | The Add a word tab gains a Paste text mode (W19's From a text) | W19 |
| S1 Me | The Words tile (R31) reads "212 known · 64 claimed · 12 due"; the Words card adds the estimate line (W10), "Your Know holds up 82%" (W7), "Core done by Nov 24" (W12); What keeps catching you adds the top word trap with Drill it (W5); Learning preferences' "Words a day" seg becomes 0 · 5 · 10 · 15 · 20 · 30 · Auto | W5, W7, W10, W12 |
| today.md T2 | Row 6 reads "Today's words · 12 due · 10 new · ~9 min" and starts W11's run | W11 |
| today.md T14 | `words.daily_item` is W21's; its reasons are W1's trap reasons | W21 |
| plan.md L4 | The Words task's primary is Today's words; Review cards, Learn N and Quiz go in its ⋯ menu; step 4's Words row takes W12's chips (0 · 5 · 10 · 15 · 20 · 30 · Auto) with finish dates, and the By exam day card | W11, W12 |
| practice.md P15 | The Reading & Writing seg lists "In context · Transitions · Words check" with counts, each Start → its Words run | W1, W2, W15 |
| S6 Results | The Words block per §3.1 override 44; `/api/history?kind=words` labels mode `check` as "Words check" | W5, W10, W13, W15 |
| S1 admin | `/admin/reports` lists `word_suppress` rows with Unsuppress | W18 |

---

## 4. Rejected

* **The Math-language deck and everything built on it**: In a real question, Practice 10
  questions with it, math mix-up Drill it, Mistake → words chips (`feedback.words`), From my
  mistakes from math traps, tap-to-define in math stems and rationales, the Math word of the
  day, `words_from: math`, the drill body's `word` / `confusion`: decision 2.
* **Translate the phrase, in Words or moved to Practice** (experience G2, unfair-advantage G1):
  decision 2 for Words; the bank already has 26 "which expression/equation represents" items
  with named mistakes, and a generator outside satbank's gate would be unverified.
* **R&W items filed in `attempts` with subject `rw`, R9 traps, Review Redo, 3/10/30 check-ins
  and an "English words" Practice domain** (outcomes #2, unfair-advantage #1 (5), #2 (3)(5), #4
  (4)): every `attempts` consumer (mastery, estimate, boards, habits, coach) would need a subject
  filter while the site is Math-first (decision 3); the word schedule already brings a missed
  word back as a fresh in-context item, and the `(template, seed, word)` addresses move into the
  bank later without a rewrite.
* **The generators as satbank topic packages** (experience #1, #2; unfair-advantage #1):
  `check.py`'s gate rests on College Board key files that R&W does not have; `rw_items.py`
  keeps the Item shape and its own verifier.
* **Function-of-the-second-sentence and Tone item types** (unfair-advantage #4 (3)): those are
  Text Structure and Purpose questions, the R&W bank's job, not vocabulary (decision 2); the
  answer-choice words are taught (W17) and tested in context (W1).
* **A Words module tile on Tests, a daily words challenge in Compete, a daily sprint board**
  (unfair-advantage #5 (1)(4), experience #12): Tests and Compete stay Math (decisions 1 and 3);
  Today already carries one shared R&W item (T14).
* **Word of the day as twins, each student in their own context** (unfair-advantage G19): T14's
  crowd spread needs one identical item.
* **Six authored contexts per word, about 4,500 sentences, and a `ctx_seen` mask** (outcomes
  #8): the frame generator gives unlimited contexts per sense across the three passage domains.
* **Hesitant (slow-right) scheduling and a fast-right box skip** (unfair-advantage #3 (6),
  experience G15): two more schedule rules with no evidence over the proof ladder; time is
  recorded and reported (W15) and the scale (W13) tunes intervals from recall.
* **A Sure / Guess toggle on by default before every answer** (outcomes #4): an extra tap most
  students skip (today.md rejected the same); the optional `I` mark and objective proofs cover
  it.
* **A Review style setting (Cards / Sentences / Mixed)** (unfair-advantage #3 (4)): the ladder
  decides the format by box; a second setting would fight it.
* **A separate `scales.json`** (experience #6): ladders are a sort over W1's class, intensity
  and polarity; one source.
* **"Which word is strongest?" items** (unfair-advantage #9 (2)): Order the ladder and Most
  precise test the same thing, the second in SAT form.
* **An "unsupported" trap kind** (outcomes #1): it can't be generated or verified from
  features; folded into `topical`.
* **A projection area chart to the exam** (experience #10): it repeats the chips' finish dates;
  the weekly forecast bars show the load.
* **A separate To confirm deck after placement** (outcomes #3): every Know it word is already
  box 3 with a proof due in 3–14 days.
* **A starred word unstarring itself at Known** (experience G10): a control that changes itself
  surprises; the Saved tile says how many are not started.
* **A speed round unlocked at 85% untimed accuracy** (outcomes G8): Sprint is open to everyone;
  a gate adds a rule for no study gain.
* **The hook field popping in after 4 s without a flip** (unfair-advantage #12 (2)): it
  interrupts recall; the hook is written on the Fix card or the sheet.
* **A 14-day sparkline on Me's Words tile** (experience G13): the tile gives the week's change
  as a number; the chart lives in Results.
* **Check-ins from R&W traps as the first part of the mix run** (outcomes #7): they depend on
  the rejected attempts path; the run serves proofs and trap items instead.

---

Summary: 22 accepted upgrades (W1–W22) move Words from a near-copy of TopTierPrep's four tabs
into a Reading & Writing vocabulary section built on the site's unique power, now aimed at R&W.
Generated Words in Context, Most precise, Order the ladder and Transitions items never run out,
name the trap behind every wrong option and show the clue. "Known" has to be proven in context.
One sized Today's words run is a tap away from everywhere. Placement skips what the student
already knows, the exam date sets the pace, and the schedule measures its own recall. The
library grows past 1,100 sense-level entries plus 80 roots. 54 overrides remove the Math
language that decision 2 dropped, and 21 ideas are rejected with reasons.
