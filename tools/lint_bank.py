"""Read-only review scan of every bank template at seeds 0 through 49.

Run from anywhere with ``python3 tools/lint_bank.py``. Findings are leads for
human review, especially the last-number rationale check; this tool never
changes a question, the bank, or a database. It exits 0 even with findings.
"""

from __future__ import annotations

import math
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from satbank.item import numeral  # noqa: E402
from satbank.registry import generate, templates  # noqa: E402


CHECKS = (
    "generation_error",
    "1_plural",
    "missing_table",
    "missing_figure",
    "missing_graph",
    "duplicate_option_value",
    "mcq_fewer_than_4_distinct_options",
    "named_mistake_equals_answer",
    "rationale_final_number_mismatch",
    "empty_reason",
    "repeated_reason",
    "placeholder",
)

PLURAL = re.compile(r"(?<![\d.])\b1\s+([a-z][a-z-]*s)\b", re.I)
PLURAL_EXCEPTIONS = {
    "as", "costs", "equals", "gathers", "gives", "goes", "has", "his",
    "intersects", "is", "its", "leaves", "less", "lies", "makes",
    "means", "minus", "plus", "reaches", "removes", "shows", "this", "was",
}
PLACEHOLDER = re.compile(
    r"\{\s*\}|\{[^}]*[!:][^}]*\}|\{\s*[A-Za-z_]\w*\s*\}"
    r"|\bTODO\b|\bFIXME\b|\bnan\b"
    r"|\bNone\b(?!\s+of\b)"
)
NUMBER = re.compile(
    r"(?<![\w.])[-−]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?"
    r"(?:\s*/\s*[-−]?\d+(?:\.\d+)?)?\s*%?"
)
FINAL_TAIL = re.compile(r"\s*(?:percent|degrees?|units?|cm|mm|m|ft|feet|inches?)?\s*[.)!]*\s*$", re.I)
CONCLUSION = re.compile(
    r"\b(?:so|thus|therefore|hence)\b[^.;!?]{0,70}$"
    r"|\b(?:answer|result|value)\s+(?:is|equals)\s*$", re.I
)


def snippet(value: object) -> str:
    """Keep each finding on one printable table row."""
    text = " ".join(str(value).split())
    return (text[:117] + "…" if len(text) > 118 else text).replace("|", "\\|")


def same_value(a: str, b: str) -> bool:
    """Compare printed options by value when numeric, by display form otherwise."""
    left, right = numeral(a), numeral(b)
    if left is not None and right is not None:
        if "%" in a:
            left /= 100
        if "%" in b:
            right /= 100
        return math.isclose(left, right, rel_tol=1e-9, abs_tol=1e-9)
    # norm_text deliberately drops carets for another audit use, but that
    # would make 20x and 20^x look identical here.
    def display(s: str) -> str:
        return (s.lower().replace(" ", "").replace(",", "")
                .replace("−", "-").replace("π", "pi").replace("·", "*"))

    return display(a) == display(b)


def option_groups(options: list[str]) -> list[list[int]]:
    groups: list[list[int]] = []
    for index, value in enumerate(options):
        group = next((g for g in groups if same_value(value, options[g[0]])), None)
        if group is None:
            groups.append([index])
        else:
            group.append(index)
    return groups


def displayed_answer(item) -> str:
    if item.fmt == "mcq" and item.answer in "ABCD" and len(item.choices) > "ABCD".index(item.answer):
        return item.choices["ABCD".index(item.answer)]
    return item.answer


def last_number_disagrees(item) -> str | None:
    """Only inspect a clear concluding numeric expression at the prose's end."""
    answer = displayed_answer(item)
    expected = numeral(answer)
    if expected is None:
        return None
    matches = list(NUMBER.finditer(item.rationale))
    if not matches:
        return None
    last = matches[-1]
    if not FINAL_TAIL.fullmatch(item.rationale[last.end():]):
        return None
    if not CONCLUSION.search(item.rationale[max(0, last.start() - 45):last.start()]):
        return None
    stated = numeral(last.group().strip())
    if stated is None:
        return None
    # A percentage and an unmarked decimal use different scales. Leave such
    # cases for a reader rather than claiming they disagree.
    if ("%" in last.group()) != ("%" in answer):
        return None
    if math.isclose(stated, expected, rel_tol=1e-5, abs_tol=1e-5):
        return None
    return f"last number {last.group().strip()!r}; answer {answer!r}; {item.rationale[-80:]}"


def displayed_text(item) -> list[tuple[str, str]]:
    parts = [("stem", item.stem), ("rationale", item.rationale)]
    parts.extend((f"reason {i + 1}", reason) for i, reason in enumerate(item.reasons))
    parts.extend((f"option {i + 1}", option) for i, option in enumerate(item.choices))
    parts.extend((f"grid-in reason {i + 1}", m.reason) for i, m in enumerate(item.spr_mistakes))
    parts.extend((f"table row {i + 1}", " ".join(row)) for i, row in enumerate(item.table or ()))
    return parts


def scan(item, report) -> None:
    grammar_parts = [("stem", item.stem), ("rationale", item.rationale)]
    grammar_parts.extend((f"reason {i + 1}", reason) for i, reason in enumerate(item.reasons))
    grammar_parts.extend((f"grid-in reason {i + 1}", m.reason) for i, m in enumerate(item.spr_mistakes))
    for label, text in grammar_parts:
        for match in PLURAL.finditer(text):
            if match.group(1).lower() not in PLURAL_EXCEPTIONS:
                report("1_plural", f"{label}: {match.group(0)!r} in {text}")
                break

    stem = item.stem.lower()
    if re.search(r"\btable\b", stem) and not item.table:
        report("missing_table", item.stem)
    if re.search(r"\bfigure\b", stem) and not item.figure:
        report("missing_figure", item.stem)
    if re.search(r"\bgraph\b", stem) and not item.figure:
        report("missing_graph", item.stem)

    if item.fmt == "mcq":
        groups = option_groups(item.choices)
        repeats = [g for g in groups if len(g) > 1]
        if repeats:
            report("duplicate_option_value", "; ".join(
                ", ".join(f"{'ABCD'[i] if i < 4 else i + 1}={item.choices[i]}" for i in group)
                for group in repeats))
        if len(groups) < 4:
            report("mcq_fewer_than_4_distinct_options", f"{len(groups)} distinct: {item.choices}")
        key = displayed_answer(item)
        for i, reason in enumerate(item.reasons):
            if reason and i < len(item.choices) and same_value(item.choices[i], key):
                report("named_mistake_equals_answer", f"option {'ABCD'[i] if i < 4 else i + 1}: {reason}")
                break
        wrong_reasons = [r for i, r in enumerate(item.reasons)
                         if i >= 4 or "ABCD"[i] != item.answer]
    else:
        wrong_reasons = [m.reason for m in item.spr_mistakes]
        for m in item.spr_mistakes:
            if m.value is not None and math.isclose(float(m.value), float(item.key),
                                                     rel_tol=1e-9, abs_tol=1e-9):
                report("named_mistake_equals_answer", f"grid-in value {m.value}: {m.reason}")
                break
    if any(not str(reason).strip() for reason in wrong_reasons):
        report("empty_reason", f"wrong-option reasons: {wrong_reasons}")
    stripped = [" ".join(str(r).lower().split()) for r in wrong_reasons if str(r).strip()]
    repeated = next((r for r, count in Counter(stripped).items() if count > 1), None)
    if repeated:
        report("repeated_reason", repeated)

    mismatch = last_number_disagrees(item)
    if mismatch:
        report("rationale_final_number_mismatch", mismatch)
    for label, text in displayed_text(item):
        if PLACEHOLDER.search(text):
            report("placeholder", f"{label}: {text}")
            break


def main() -> int:
    findings: list[tuple[str, int, str, str]] = []
    names = sorted(templates())
    for name in names:
        for seed in range(50):
            def report(check: str, detail: str) -> None:
                findings.append((name, seed, check, snippet(detail)))

            try:
                item = generate(name, seed)
                scan(item, report)
            except Exception as exc:
                report("generation_error", f"{type(exc).__name__}: {exc}")

    print(f"Bank lint: {len(names)} templates × 50 seeds = {len(names) * 50} addresses attempted")
    print("Findings are for review; graph mentions and concluding numbers use text heuristics.")
    print("| template | seed | check | snippet |")
    print("| --- | ---: | --- | --- |")
    for name, seed, check, detail in findings:
        print(f"| {name} | {seed} | {check} | {detail} |")
    counts = Counter(check for _, _, check, _ in findings)
    print("\nPer-check counts")
    print("| check | count |")
    print("| --- | ---: |")
    for check in CHECKS:
        print(f"| {check} | {counts[check]} |")
    print(f"| total findings | {len(findings)} |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
