# Signed-in Student Question Bank metadata export

## Source

- Permission: College Board, by phone to the user, 2026-09-27; written confirmation pending
- Observed 2026-09-26 21:49 UTC, after the user signed in directly: https://mypractice.collegeboard.org/questionbank/search and https://mypractice.collegeboard.org/questionbank/results
- Comparison source, fetched 2026-09-26 UTC: https://qbank-api.collegeboard.org/msreportingquestionbank-prod/questionbank/digital/get-questions (public Educator Question Bank metadata only; see `cb_index.json`)

## Export

[`student_index.json`](student_index.json) contains all 3,311 SAT items visible in the Student Question Bank results table, captured across every page with all four domains selected in each section. It contains only the item ID, section, domain, skill, and difficulty tier. No difficulty or active-question filter was applied. The raw browser table snapshot is cached outside the repository and can be re-imported with `python3 tools/cb_data.py --import-student PATH`.

| SAT inventory | Math | Reading and Writing | Total |
| --- | ---: | ---: | ---: |
| Student Question Bank | 1,466 | 1,845 | 3,311 |
| Public Educator Question Bank | 1,925 | 1,845 | 3,770 |

The full ID sets have **zero overlap**. Keep these as separate inventories; equal Reading and Writing totals do not imply the same items.

## Fields still unavailable

- The Student results table does not display the item's 1–7 `score_band_range_cd` field. `band` is therefore `null` in the export.
- Selecting an ID opens a preview modal while the address remains `https://mypractice.collegeboard.org/questionbank/results`. No stable per-item URL was verified; `public_item_url` is `null`.
- A partner metadata export containing the missing band and a documented item link template would fill these two fields. It need not contain question text, answers, credentials, or the confidential partnership email.

No account details, question stems, answer choices, answers, explanations, screenshots, or authenticated API responses were copied into the repository.
