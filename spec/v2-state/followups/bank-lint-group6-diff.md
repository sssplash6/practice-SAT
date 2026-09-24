# Bank lint group 6: seed comparison

Compared `registry.generate(template, seed)` against `efadabd` for every seed
from 0 through 49 in the ten `reasons` templates. Each item's full `repr` and
each field's `repr` were SHA-256 hashed before and after the fix. The lists
below contain every changed seed in that range; 394 generated items were byte
identical. The four pre-existing `lat.shadow` generation failures (10, 32, 35,
39) were also unchanged. That leaves 102 changed seed outcomes.

| Template | Changed seeds | Changed fields | Why |
| --- | --- | --- | --- |
| `tvdata.interval_change` | 2, 3, 15, 17, 25 | reasons, rationale | Only the interval with the largest reverse move keeps the superlative reason; the other reverse moves get a true reason. The rationale compares rises or falls, rather than absolute movement. |
| `tvdata.interval_change` | 4, 18, 23, 37, 39 | stem, answer letter, choices, reasons, rationale, figure, params | The coffee warmed after being left in a constant-temperature room; rejecting that draw selects a cooling chart. |
| `tvdata.interval_change` | 28, 40 | stem, choices, reasons, rationale, figure, params | Same coffee-warming defect; these retries retained the answer letter. |
| `tvdata.interval_change` | 26, 47 | stem, answer letter, choices, reasons, rationale, figure, params | No interval rose; rejecting that draw selects a chart with an actual rise. |
| `tvdata.interval_change` | 32 | stem, answer letter, choices, reasons, rationale, figure, params | The first draw had no rise; its first replacement warmed coffee, so it was also rejected. |
| `lin.model_value` | 1, 2, 6, 9, 13, 17, 38, 42, 44, 45 | reasons | The option computed as rate times input minus the starting amount now says it subtracted that amount. |
| `lin.model_value` | 7, 11, 16, 33, 39 | choices, reasons | In a negative-rate draw the previously duplicated option is now distinct and carries its own true reason. |
| `prob.two_way.grouped` | 4, 5, 7, 20, 31, 34, 41, 48, 49 | grid-in mistakes | A count from one member of a union is described as that member's row or column, rather than as subtracting unrelated counts. |
| `lin.from_table` | 0, 1, 3, 5, 7, 8, 9, 11, 12, 14, 18, 20, 21, 24, 25, 26, 27, 29, 30, 31, 33, 34, 38, 40, 41, 42, 43, 44, 45, 47, 48, 49 | choices, reasons, option signatures in params | Tables starting away from zero now offer equations fitted to a row. The `step + 1` slope gets a reason that describes its actual computation. The stem, table, and key are unchanged. |
| `lat.shadow` | 2, 7, 23, 48 | stem, key, answer letter, choices, reasons, rationale, params | Equal known height and shadow made the answer the second shadow. Redrew the free height. |
| `lat.shadow` | 16, 17, 18, 20, 36 | stem, key, choices, reasons, rationale, params | Same equal-height degeneracy; seed 36 was missed by the repeated-reason lint. |
| `rr.cube_density` | 30 | stem, key, answer, grid-in mistakes, rationale, params | A one-unit edge made density and mass equal; seed 30 was a grid-in missed by the repeated-reason lint. |
| `rr.cube_density` | 34, 41 | stem, key, answer letter, choices, reasons, rationale, params | Same one-unit-edge degeneracy. |
| `rr.cube_density` | 37, 38 | stem, format, key, answer, choices, reasons, grid-in mistakes, rationale, params | Same one-unit-edge degeneracy; retry also selected a different format. |
| `nlfunc.evaluate` | 35 | stem, key, answer letter, choices, reasons, rationale, params | Rejected `x²` at `x = 2`, where squaring and doubling coincide. |
| `nlfunc.evaluate` | 46 | stem, key, choices, reasons, rationale, params | Same degeneracy. |
| `nleq.secant_slope` | 48 | stem, key, choices, reasons, rationale, params | Symmetric `x = 1` and `x = −1` gave slope zero and collapsed the sign mistakes. |
| `lin1.context_solve` | 6, 9, 10, 32 | answer letter, choices, reasons | Replaced the duplicated “extra hours” value with the distinct error of adding the first reading's hours twice. Stem and key are unchanged. |
| `esc.conclusion` | 1, 8, 16, 18, 20, 22, 31, 35, 39, 44 | reasons | Replaced “plots who were not selected” with grammatical unit-neutral wording. |

Twenty-seven seeds changed their generated quantities: `tvdata.interval_change`
4, 18, 23, 26, 28, 32, 37, 39, 40, 47; `lat.shadow` 2, 7, 16, 17, 18, 20, 23, 36, 48;
`rr.cube_density` 30, 34, 37, 38, 41; `nlfunc.evaluate` 35, 46; and
`nleq.secant_slope` 48. All twenty-seven had one of the rejected degenerate draws.
The other 75 changed items retain their stem, key, and underlying quantities;
only reasons, options, their order, or the explanation changed. Twenty-five
changed seeds were absent from the triage's 77-case list but exhibited the
same reason, grammar, or degeneracy defects.
