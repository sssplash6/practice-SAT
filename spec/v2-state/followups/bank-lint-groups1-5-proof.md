# Bank lint groups 1–5 seed comparison

The [seed dump](../../../tools/bank_lint_seed_dump.jsonl.gz) contains the master and branch outputs for seeds 0–199 of all 39 templates changed by groups 1–4. Each of its 7,800 JSON Lines records has the template, seed, both generated items, and the comparison results. The master baseline is commit `7aa0272`; the branch output is after group 4.

| Result | Count |
| --- | ---: |
| Seeds that generated on master | 7,549 |
| Master-working seeds with a changed answer, key, ordered option values, stem numbers, option numbers, parameter numbers, table numbers, format, or figure | 0 |
| Master-working seeds changed by the generation fallback, by whole-item hash | 0 |
| Seeds that failed all 60 draws on master and now generate | 251 |
| Seeds still failing | 0 |

For ordered option values, the comparison normalizes only singular/plural forms of the same unit (for example, `feet` to `foot`) at each option index. It also compares every printed number in each option at that index. The 29 changed option lists differ only in those unit forms. Eight parameter dictionaries changed only in their embedded display text; their numeric parameters and option signatures are unchanged.

The 251 revived addresses belong to `lat.shadow` (15), `lat.vertical_similar` (31), `nleq.product_roots_constant` (35), `nleq.rational_combine` (12), `nleq.rational_quadratic` (8), `nleq.sum_product` (15), `prob.two_way.nearest_row` (69), `rr.table_unit_price` (10), `rtt.parallel_similar` (50), `sstat.count_claim` (1), and `sys.unknown_coefficient` (5). The fallback begins only after the original 60 draws fail.

The comparison checks numeric data in stems, options, tables, and parameters. Rationales and reasons may gain a concluding number because the wording now states the answer. The dump retains the complete before and after wording for review.

To inspect the dump: `gzip -dc tools/bank_lint_seed_dump.jsonl.gz | less`.
