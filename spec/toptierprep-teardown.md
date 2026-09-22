# TopTierPrep teardown

Walked through on 2026-09-23 from a logged-in free-tier account
(toptierprep.com). I went through every sidebar section, one QBank session, a
vocab quiz, a flashcard, the Question of the Day, and a two-module practice
exam through to its score report. The contests and leaderboards were empty
that day, so only their empty states were seen.

This is a reference for building something in the same category. It records
what they built and how it behaves. It is not a blueprint to copy: see
[What not to copy](#what-not-to-copy).

## Stack and visual system

| thing | what they use |
|---|---|
| UI kit | Tailwind v4 + shadcn/ui (oklch CSS variables on `:root`, Radix menus/selects/dialogs) |
| body font | Figtree Variable, everywhere |
| display font | Bricolage Grotesque Variable, only on the study-plan wizard step titles (30/700) |
| math | KaTeX (`KaTeX_Main`, `KaTeX_Math`) |
| calculator | embedded Desmos graphing calculator |
| primary | `rgb(15,101,223)` ≈ `#0F65DF` |
| text | `oklch(.145 0 0)`; muted `oklch(.551 .027 264)` |
| canvas | light gray (`oklch ~.967`) behind white cards |
| cards | white, radius 18px, no shadow, 20px padding |
| buttons | radius ~26px (pill), 14px/600, 16px horizontal padding |
| page H1 | 36px/700 |

Difficulty is coded by colour throughout: green easy, blue (QBank) or amber
(vocab) medium, red hard.

## App shell

- **Left sidebar, ~220px**, collapses to a ~60px icon rail with a toggle next
  to the logo. Stacked black "TOP TIER PREP" wordmark.
- Nav, in order: Dashboard, Practice, Study Plan, Results, Question Bank,
  Contests & Challenges, Contests Rankings, Leaderboards, Vocabulary,
  Subscription. The active item is a gray-blue pill in bold.
- Bottom: a blue "Upgrade to Pro · Unlimited tests & QBank" card with a TRIAL
  badge, then the user card (avatar, name, role, chevron). The user card opens
  a popover with name + email, My Profile, Send feedback, and Sign out (red).
- **Floating button, bottom-right, on every page**: "Add your own word (drag to
  move)". It is a draggable quick-add into the vocab "Custom Added Words"
  collection. It overlaps the Next button in QBank sessions.
- Auth is `/auth`; unauthenticated routes redirect there. Sign-in is Google;
  email/password can be added later from the profile.

## Routes

| route | page |
|---|---|
| `/dashboard` | home |
| `/practice` → `/practice/full-length` | practice-test catalog |
| `/practice/session?id=` | exam runner (Bluebook clone) |
| `/study-plan`, `/study-plan/create` | plan landing, 4-step wizard |
| `/results`, `/results/{sessionId}` | results list, score report |
| `/question-bank`, `/question-bank/session/{uuid}` | session builder, practice session |
| `/contest-challenge`, `/contest-rankings`, `/leaderboard` | competition |
| `/vocabulary/library`, `/flashcards?cardId=`, `/quizzes`, `/my-words/saved` | vocab |
| `/subscription`, `/profile` | billing, profile |

## Dashboard

1. **Hero**: full-width blue rounded banner. Date eyebrow ("WEDNESDAY,
   SEPTEMBER 23"), "Good Morning, {name}", a monochrome-blue illustration on
   the right (books, globe, column, apple, hand writing).
2. **Question of the Day** (two columns: one R&W, one Math, each with an
   "Answer" outline button) beside a **study-time card**: "0m study time
   today / 0m this month" above a month calendar with round day cells, today
   filled black and other months' days faded. (It highlighted the 22nd on the
   23rd, which looks like a timezone bug.)
3. **Study plan CTA**: "Build Your Adaptive DSAT Study Plan", three
   coloured-dot bullets (custom daily pacing / score-drift adjustments /
   scheduled rest days), "Build My Plan →".
4. **Score progress** (current score, plus a target with a pencil to edit)
   beside an **exam countdown**: a pill date picker ("EXAM DATE: 3 OCTOBER
   2026") above a large live DD : HH : MM : SS.
5. **Recent tests taken.**

**QOTD modal**: the stem (with KaTeX), then choices as full-width rows. After
"Check answer", the chosen row turns red or green, an "Incorrect"/"Correct"
banner appears, and a "Show explanation" link opens the rationale. **It does
not highlight the correct choice**; you have to read the explanation. It
allows one attempt, and a "More practice" link sits in the footer.

## Practice tests (`/practice/full-length`)

- An **Estimated Score** card at the top (empty until a test is done).
- A single tab, "Full-Length Tests".
- Filter pills (Radix dropdowns with radio items): Difficulty
  (All/Easy/Medium/Hard), Type (All/Adaptive/Non-adaptive), Status (All/Not
  Attempted/In Progress/Completed), Access (All/Free/Paid), Sort By
  (Newest/Oldest/Hardest/Easiest; the current value is shown under the label).
- A **three-column card grid**, one card per paper (~29 papers: "Paper #N",
  plus "September Predictions" and "AUGUST PREDICTIONS (2026)"). Each card has
  the title, a Report button, tags (Free / Adaptive or Non-Adaptive /
  Standard), two stat tiles (People took N · Your last score), a gray
  "Comments N" button and a blue "Start Exam >".
- **Paid papers** are the same card, blurred, with a lock overlay reading
  "Paid exam · Unlock it with Pro or Elite · See plans".
- **Comments modal**: a threaded list (avatar, name, timestamp, Reply, "Show 1
  reply") with a composer pinned at the bottom. What people actually post is
  low-quality chatter, so a comment feature needs moderation from day one.
- **Report modal** (shared by exams, questions and vocab): a read-only
  "Sent with your report" box (exam, title, ID), Title (0/200), Category
  (General feedback / Bug / Wrong answer key / Typo / Feature request /
  Other), Details (0/5000), image attachments (up to 10 × 50 MB), and "Send
  feedback".

### Start-exam wizard

A modal with a segmented progress bar:

1. **How do you want to practice?** Full Test (all 4 modules) or Select
   Modules.
2. **Select modules** (only if chosen): a 2×2 grid of checkable cards, each
   with a coloured chip (R&W purple, MATH green) and "Module 1 · 27 questions
   · 32 min". A non-adaptive paper offers a fixed "Module 2 · Hard". It has
   Select all / Clear and an "N of 4 selected" count.
3. **Timer mode**: Timed (official limits) or Untimed.

Then comes a dark full-page gate: "Enter Fullscreen Mode · This exam runs in
fullscreen, just like the Digital SAT", with a "Proceed without entering full
screen mode" escape link.

### Exam runner: a near-exact Bluebook replica

- The app sidebar is gone. A thin multicolour dashed rule (red, cream, navy
  and green segments) sits under the header, above the footer and under the
  question strip, copying Bluebook's rule.
- **Header**: "Section 1, Module 1: Reading and Writing" with a Directions
  link (official directions in a modal); a large mm:ss timer in the centre
  with an eye toggle to hide it; on the right, Highlights & Notes and More
  (⋮ → Save and Exit). Math adds Calculator (Desmos in a floating, resizable
  panel) and Reference (the official formula sheet).
- **R&W**: two panes with a draggable divider (blue while dragging), passage
  on the left and question on the right. **Math**: one centred column. An SPR
  math item puts the official "Student-Produced Response Directions" and an
  examples table in the left pane.
- **Question strip**: number square, Mark for Review (→ "Unmark", yellow
  bookmark), Report, and an ABC toggle that adds a strike-out circle beside
  each choice (with Undo on a struck choice).
- **Choices**: full-width rows with a 2px black border and a circled letter.
  The selected choice gets a 3px blue border and a filled letter.
- **Highlights**: with H&N on, selecting text shows a toolbar with 4 colours
  (yellow, green, blue, pink), 3 underline styles and "Note". Clicking a
  highlight gives a "No note / Remove / Close" popover.
- **SPR input**: "Enter your answer (e.g., 5.566, -5.566, 2/3, -2/3)" with a
  monospace "Answer Preview:" line underneath.
- **Footer**: student name on the left; a centre pill "Question 1 of 27 ⌄"
  opens the module navigator (Current pin / Unanswered dashed / For Review
  flag, plus "Go to Review Page"); Back and Next on the right.
- **Check Your Work** page: three stat cards (Answered / Unanswered / For
  Review), a question grid, an amber warning ("26 questions unanswered.
  Unanswered questions are marked incorrect."), and "Next Module" or, on the
  last module, "Finish Module". The copy says you can't come back to a module
  after submitting it.
- Running selected modules shows no break screen between them.

### Score report (`/results/{sessionId}`)

- "PRACTICE TEST REVIEW · Paper #47 · 2025-08-31". The paper is dated like
  an official form.
- Three cards: a **R&W ring gauge** (200/800, "2 Correct, 25 Wrong"), a
  **blue centre card** (Total Score 420/1600, a progress bar, "4 of 49
  correct", a "Practice test — not ranked" pill) and a **Math ring gauge**.
- **Performance summary** tiles: Correct / Incorrect / Unanswered / Accuracy.
- **Domain performance**: a R&W | Math toggle, then a 2×2 grid of domain
  cards with %, a segmented bar and confusing copy ("20% of test section, 1-5
  questions").
- **Question review**: filters All / R&W / Math / Flagged (n); per-module
  grids ("R&W - M1 2/27") of large squares coloured green, red or gray, with
  an orange dot for flagged.
- **Review modal**: "R&W - M1 · Q2" with a status chip, a "Hide answers"
  toggle, Report and "2 of 49". It shows the passage in a gray box, the
  choices with the key in green, Your answer / Correct answer boxes, and a
  long-form Explanation that opens with "Justification:". Previous/Next moves
  across all 49 questions.
- The `/results` list card shows red chips listing the wrong question numbers
  per module ("2 3 4 5 6 7 +19") and a Review button. The top "Score Overview"
  card only fills in after a full four-module test.

## Question Bank

### Builder (`/question-bank`)

It is one screen with no page scroll and a fixed bottom action bar.

- A top toggle switches between **Question Bank** (College Board items: 1,848
  R&W, 1,921 Math) and **TTP Bank** (their own items: 1,315 R&W, 3,867 Math).
  TTP's R&W is lopsided: Rhetorical Synthesis 493, Transitions 10, SEC 22.
- **Select domains**: a live "N questions" count and an English | Math toggle.
  Each domain is an accordion card with a check circle and a count; it
  expands to skills, each with its own checkbox and count. The parent
  unchecks when any child is unchecked; there is no indeterminate glyph.
- **Advanced filter**: Bluebook Include | Exclude (QB tab only); Difficulty
  as multi-select pills; **Question Score 1–7** as a dual-thumb range (a
  finer difficulty scale); and selects for Solved (All / Solved only /
  Unsolved only), Marked for Review, and Redo List (All / Redo only).
- **Bottom bar**: Volume 10/20/30/40/50/All, Mode Timed | Untimed, "Start
  Practice Session".

Counts per skill (QB / TTP), useful as a sense of scale:

| domain | skill | QB | TTP |
|---|---|---:|---:|
| Algebra | Linear equations in one variable | 112 | 280 |
| | Linear functions | 170 | 408 |
| | Linear equations in two variables | 130 | 237 |
| | Systems of two linear equations | 126 | 216 |
| | Linear inequalities | 77 | 134 |
| Advanced Math | Equivalent expressions | 116 | 259 |
| | Nonlinear equations & systems | 164 | 401 |
| | Nonlinear functions | 258 | 530 |
| PSDA | Evaluating statistical claims | 12 | 5 |
| | Inference / margin of error | 28 | 35 |
| | One-variable data | 84 | 111 |
| | Percentages | 83 | 180 |
| | Probability | 49 | 59 |
| | Ratios, rates, proportions, units | 93 | 246 |
| | Two-variable data | 71 | 92 |
| Geometry & Trig | Area and volume | 110 | 184 |
| | Circles | 67 | 114 |
| | Lines, angles, triangles | 102 | 226 |
| | Right triangles & trig | 69 | 115 |
| Information & Ideas | Central Ideas / Command of Evidence / Inferences | 138 / 280 / 140 | 107 / 292 / 197 |
| Craft & Structure | Cross-Text / Text Structure / Words in Context | 61 / 149 / 261 | 29 / 58 / 102 |
| Expression of Ideas | Rhetorical Synthesis / Transitions | 204 / 194 | 493 / 10 |
| Std English Conventions | (Boundaries, Form Structure & Sense) | 421 | 22 |

### Session (`/question-bank/session/{uuid}`)

This is a practice mode, not a test mode: it gives immediate feedback and
allows unlimited retries.

- **Top bar**: Go Back; Details (a popover with question ID such as
  `025731-DC`, domain, skill and difficulty); Explanation, which appears only
  after a check; a centre countdown (10 questions = 60:00) with Hide; Clear
  Session (red); Share (`navigator.share`, which opens the OS share sheet and
  froze the page in the test browser); Calculator; Reference.
- **Question strip**: number, Mark for Review, Eliminate (a mode that adds ⊘
  to every choice; eliminated choices gray out), Report, Attempts (with a
  count badge), and a per-question stopwatch.
- **MCQ** is a 2×2 grid of choice cards. **SPR** is a full-width input with
  an Answer Preview line.
- **Check**: a correct pick turns green, a wrong one red. **The key is not
  revealed** and retries are unlimited. Each try is logged in an **Attempt
  History** modal (#, Correct/Incorrect · Option, time spent, timestamp). A
  wrong-then-right question counts as "Mixed".
- **Explanation** replaces the question card with a blue-tinted card; the
  button becomes "← Back to Question".
- **Bottom bar**: Previous; a centre "Question N of 10" pill that opens a
  **Question Overview** with a Status | Difficulty toggle (Status legend:
  Unanswered, Correct, Incorrect, Mixed, Marked, Current; Difficulty colours
  each cell easy/medium/hard); Check; Next.
- **There is no end-of-session summary.** Next is disabled on the last
  question and nothing lists sessions to resume. A session survives only by
  its URL.

## Study plan

- **Landing** (empty state): a blue hero ("Your path to the score you want",
  "Create my plan", "Takes about a minute · 1 plan left this cycle"); three
  stat cards (10 practice tests / 6,933 questions / 1,002 vocab words); "How
  it works" in three numbered cards; a "Your study plans" list.
- **Wizard** (the draft autosaves; "Exit setup" is always available):
  1. **Where you are**: R&W and Math sliders from 200 to 800 with a value
     bubble; the total is computed.
  2. **Where you're going**: target sliders (minimum = current), a NOW →
     TARGET card ("+400 points" pill, a 400–1600 range bar with both
     markers, per-section "500 → 700 (+200)"), the exam date, and "2 weeks
     to prepare · about 200 points per week".
  3. **Time you have**: daily-minutes chips (30m to 4h), a days-per-week
     slider ("5 days · 5h a week"), Mon–Sun tiles toggling STUDY (green) and
     REST (orange) that stay in sync with the slider, and "Solve a practice
     exam every day", locked below 150 minutes a day ("a full practice test
     runs 134 minutes").
  4. **What to focus on**: each of the 8 domains gets a Focus / Normal /
     Strong segmented control, with at most 4 on Focus and live
     "0/4 focus · 0 strong" badges. It adds an "Include vocabulary practice"
     toggle and a "Your plan at a glance" summary. "Create my study plan" is
     disabled until something is set to Focus.
- I did not generate a plan, so the plan view itself (daily tasks) was not
  seen. Plans are capped per billing cycle and called "AI Study Plan
  Generations".

## Vocabulary

Four large pill tabs, each its own route:

- **Library**: filters for Difficulty, Topic (General / Academic / Science /
  Economics / Transitions) and Collection (Must know 650 SAT words / The
  College Panda's 400 / Custom Added Words), plus "Start Practice Session".
  Words sit in a 6-column tile grid with a 1px border coloured by difficulty.
  Clicking a tile opens its flashcard.
- **Flashcards**: a difficulty pill; a stacked-deck card (two ghost cards
  behind it); the word, large. Clicking flips it to show the definition (bold),
  an italic example sentence, Synonyms, Antonyms and "Common Confusions"
  (lookalike words, e.g. illusory → illusion, illustrate, elusive). A save
  star, I Know / Don't Know, and Previous / Next. **Opening a card uses up
  one of the day's new-word allowance** (free: 5 a day).
- **Quizzes**: Collection select; timer (none / 30s / 60s). The definition is
  the prompt and four word tiles are the answers. A wrong pick tints red,
  fades the rest, and prints "Correct answer: {word}"; then Next.
- **My Words**: "Saved Words N" and "Due Today N" cards (spaced repetition),
  the same filters, and a dashed empty state.

## Competition

These were all empty on the day I looked (no active contests, no rankings).

- **Contests & Challenges**: a Global Leaderboard card (with a Rankings link),
  a Your Contest Stats card, and the list of active contests.
- **Contests Rankings**: a two-column grid of Performance Summary (with
  "Browse contests"), Contest Leaderboard (choose a finished contest), Your
  Rankings (global rank, contests played), Time Analysis ("average seconds
  per answered question, by difficulty"), Badge Progress, and Contest
  History.
- **Leaderboard**: a hero with room for a podium; Weekly / Monthly / Yearly;
  Global ↔ country select; Contest Points | Overall Score; columns Rank,
  Username, Accuracy, Time.
- Contests are gated by tier: free and standard paid contests on Pro;
  Elite-only prize contests on Elite.

## Profile (`/profile`)

- **Left third**: a tinted identity card (avatar with a camera badge, name,
  email, a "Not set yet" pill, and a 2×2 of Streak / Tests / Solved / Vocab);
  Performance Snapshot (global and country rank); Subscription & Credits
  meters; Saved Content (saved words, redo questions, saved questions);
  Account (name, email, set password, Google connected, sign out).
- **Right two-thirds**: Study Goals (target, exam-date countdown bar, daily
  and weekly goal, preferred time); subject performance; a Score Trend chart;
  Achievements (7-Day Streak, 1000 Solved, Consistency, Top Rank, View All);
  **Learning Preferences** (Practice Mode, Difficulty Level = Adaptive, and
  toggles for AI Explanations, Show Desmos Calculator and Include Vocab
  Review); Recent Activity.

## Monetisation (`/subscription`)

| | Free | Pro | Elite |
|---|---|---|---|
| monthly | $0 | $13.99 | $23.99 ("Most Popular") |
| 3-month | — | $35.99 ($12/mo, save 14%) | $59.99 ($20/mo, save 17%) |
| practice exams | 1 attempt | 20 + 10 retakes / mo | 30 + 20 retakes / mo |
| College Board QBank | unlimited | unlimited | unlimited |
| TTP Bank | 0 | "0 a day" (shown as is, looks unset) | "0 a day" |
| new vocab words | 5 / day | 20 / day | 30 / day |
| AI study plans | 1 | yes | yes |
| contests | — | free + standard paid | all + Elite prize contests |

- A usage meter per quota (label, n/max, bar) appears on both Subscription
  and Profile.
- Pro has a 7-day free trial; Elite does not. Trust strip: "7-Day Risk-Free
  Trial / Cancel Anytime in 1-Click / Instant Access". FAQ accordion.
- A payment history table (Date, ID, Method, Amount, Status, Receipt,
  Invoice), in USD.
- Their stated wedge: "The College Board question bank is unlimited on every
  plan; upgrading adds full-length practice tests, daily TopTierPrep questions
  and AI study plans."

## Where they are weak

These are the openings, roughly in order of how much a student would feel
them:

1. **QBank sessions never end.** There is no summary, no score, no list of
   sessions to resume and no review-mistakes flow.
2. **The key is hidden after a wrong answer** in both QOTD and QBank (you
   have to open the explanation). Unlimited retries also make "accuracy"
   meaningless.
3. **The home screen has no single next action.** The plan CTA, QOTD,
   countdown and score all compete for attention.
4. **The domain-performance copy doesn't make sense** ("20% of test section,
   1-5 questions"), and the Score Overview stays empty until a full
   four-module test.
5. **TTP Bank coverage is thin exactly where students need drilling**: SEC 22,
   Transitions 10, Evaluating statistical claims 5.
6. **Small bugs**: the calendar is off by one day; the vocab button covers
   Next; Share uses the OS share sheet; the overview popover ignores Esc; the
   paywall shows "0 TopTierPrep questions a day" on paid tiers; image-and-text
   stems float the image beside the text.
7. **The vocab allowance is spent just by opening a card**, which punishes
   browsing.
8. **Comments are unmoderated** chatter.

## How this maps onto satbank

- **The Math QBank is what satbank already builds.** TopTierPrep's TTP Bank
  is a fixed pool (3,867 Math items); satbank's templates produce unlimited
  verified items per skill, with distractors grounded in real misconceptions.
  That answers weakness 5 outright and is the strongest point of difference.
- **Skill taxonomy**: their 8 domains / 29 skills are the College Board's, the
  same taxonomy satbank's topics already follow.
- **Question Score 1–7** is a finer difficulty axis than easy/medium/hard;
  satbank's parameter space can place items on it deterministically.
- **The exam runner** has to be Bluebook-faithful (split pane, highlighter,
  ABC eliminate, navigator, Check Your Work, Desmos, reference sheet), because
  that is what students expect. The look should be our own; see below.

## What not to copy

- **Brand and chrome**: their name, wordmark, illustration and card layouts
  are theirs. Bluebook's multicolour dashed rule and exact exam chrome are
  College Board trade dress. Match Bluebook's *behaviour*, not its look.
- **Content**: explanations, TTP items and vocab entries (definitions,
  examples, "Common Confusions") are their copyrighted work. "The College
  Panda's 400" is a published book's word list. College Board QBank items are
  reusable only under College Board's terms, so check before shipping them.
- **Desmos** has its own API terms and needs an API key for embedding.
