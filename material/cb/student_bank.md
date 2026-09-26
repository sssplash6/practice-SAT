# Signed-in Student Question Bank observation

## Source

- Permission: College Board, by phone to the user, 2026-09-27; written confirmation pending
- Observed 2026-09-26 21:38 UTC, after the user signed in directly: https://mypractice.collegeboard.org/questionbank/search and https://mypractice.collegeboard.org/questionbank/results
- Comparison source, fetched 2026-09-26 UTC: https://qbank-api.collegeboard.org/msreportingquestionbank-prod/questionbank/digital/get-questions (public Educator Question Bank metadata only; see `cb_index.json`)

## Findings

| SAT inventory | Math | Reading and Writing | Total |
| --- | ---: | ---: | ---: |
| Student Question Bank, all domains, no filters | 1,466 | 1,845 | 3,311 |
| Public Educator Question Bank | 1,925 | 1,845 | 3,770 |

- The signed-in Student bank shows 484 Math Algebra items; the public Educator bank shows 616. The first ten visible Student IDs in each section were absent from the public Educator index. Equal Reading and Writing totals therefore do not establish identical inventories.
- The Student results table exposes ID, difficulty, domain, and skill. It does not display the item's 1–7 `score_band_range_cd` field. A complete Student index with bands needs a College Board metadata export or an authorized data interface that supplies this field.
- Selecting an ID opens a preview modal while the address remains `https://mypractice.collegeboard.org/questionbank/results`. No stable per-item URL was verified. A partner-provided link template would resolve this gap.
- This observation contains no account details, question stems, answer choices, answers, explanations, or screenshots. No authenticated response or credential was copied into the repository.

## Partner export fields needed

A metadata-only SAT export with `{cb_id, subject, domain, skill, tier, band, public_item_url}` (or a documented link template). Include the inventory name and an export date so the Educator and Student sets can be compared without assuming their IDs overlap.
