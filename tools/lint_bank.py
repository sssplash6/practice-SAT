"""Read-only review scan of every bank template at seeds 0 through 49.

Run from anywhere with ``python3 tools/lint_bank.py``. Findings are leads for
human review, especially the last-number rationale check; this tool never
changes a question, the bank, or a database. It exits 0 even with findings.
"""

from __future__ import annotations

import math
import random
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from satbank.item import ItemError, numeral  # noqa: E402
from satbank.registry import generate, templates  # noqa: E402


CHECKS = (
    "generation_error",
    "low_yield",
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
    "filler_majority",
    "placeholder",
)

PLURAL = re.compile(r"(?<![\d.−-])(?<![+−-]\s)\b1\s+"
                    r"([a-z][a-z-]*s|feet|people|children|men|women)\b", re.I)
PLURAL_EXCEPTIONS = {
    "as", "costs", "equals", "gathers", "gives", "goes", "has", "his",
    "intersects", "is", "its", "leaves", "less", "lies", "makes",
    "means", "minus", "plus", "reaches", "removes", "shows", "this", "was",
    "appears", "defines", "satisfies", "times",
}
TABLE_WORD = re.compile(r"\btables?\b", re.I)
FIGURE_WORD = re.compile(r"\b(?i:figures?)\b(?!\s+[A-Z]\b)|\b(?i:pictured|diagram)\b")
GRAPH_WORD = re.compile(r"\bgraphs?\b", re.I)
GRAPH_DEFINED = re.compile(r"\bgraphs?\s+of\b|\bgraphed\b", re.I)
GRAPH_POINTED = re.compile(
    r"\bgraphs?\s+(?:shown|above|below|shows?)\b|\bshown\s+in\s+the\s+graph\b"
    r"|\bgraphs?\s+of\b[^.?]*\b(?:is|are)\s+shown\b|\bfollowing\s+graphs\b", re.I)
FILLER = "near-miss arithmetic slip"
SINGLES_OUT = re.compile(
    r"\b(?:furthest|farthest|greatest|largest|smallest|highest|lowest|fewest|"
    r"the most|the least)\b", re.I)
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
CLAUSE_START = re.compile(r"\b(?:so|thus|therefore|hence|giving)\b|^", re.I)
COMBINE_ASK = re.compile(
    r"\b(?:sum|product|difference)\b|\bhow much (?:greater|less|more)\b"
    r"|\bvalue of \w+ ?[+−-] ?\w+", re.I)
CONCLUSION = re.compile(
    r"\b(?:so|thus|therefore|hence)\b[^.;!?]{0,70}$"
    r"|\b(?:answer|result|value)\s+(?:is|equals)\s*$", re.I
)


def snippet(value: object, limit: int = 118) -> str:
    """Keep each finding on one printable table row."""
    text = " ".join(str(value).split())
    return (text[:limit - 1] + "…" if len(text) > limit else text).replace("|", "\\|")


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


def valued(item) -> bool:
    """Numeric choices that express answer values, rather than labels like years."""
    if not item.choices or not all(numeral(o) is not None for o in item.choices):
        return False
    shown = numeral(displayed_answer(item))
    if shown is None:
        return False
    key = float(item.key)
    return any(math.isclose(shown, v, rel_tol=1e-6, abs_tol=1e-9)
               for v in (key, key * 100))


def repeated_reasons(item, report) -> None:
    """Flag a repeated MCQ reason only if one claim cannot explain both values."""
    by: dict[str, list[str]] = {}
    for i, (option, reason) in enumerate(zip(item.choices, item.reasons)):
        if reason and "ABCD"[i] != item.answer:
            by.setdefault(" ".join(reason.lower().split()), []).append(option)
    fillers = len(by.pop(FILLER, []))
    if fillers >= 2:
        report("filler_majority", f"{fillers} of 3 wrong options are unnamed "
               f"near-misses: {item.choices}")
    for reason, options in by.items():
        if len(options) > 1 and (valued(item) or SINGLES_OUT.search(reason)):
            report("repeated_reason", f"{reason} <- {', '.join(options)}")
            return


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
    if not COMBINE_ASK.search(item.stem):
        starts = list(CLAUSE_START.finditer(item.rationale))
        clause = item.rationale[starts[-1].end():] if starts else item.rationale
        values = (numeral(m.group().strip()) for m in NUMBER.finditer(clause))
        if any(v is not None and math.isclose(v, expected,
                                             rel_tol=1e-5, abs_tol=1e-5)
               for v in values):
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
    grammar_parts.extend((f"option {i + 1}", option)
                         for i, option in enumerate(item.choices))
    for label, text in grammar_parts:
        for match in PLURAL.finditer(text):
            if match.group(1).lower() not in PLURAL_EXCEPTIONS:
                report("1_plural", f"{label}: {match.group(0)!r} in {text}")
                break

    if TABLE_WORD.search(item.stem) and not item.table:
        report("missing_table", item.stem)
    if FIGURE_WORD.search(item.stem) and not item.figure:
        report("missing_figure", item.stem)
    if (not item.figure and GRAPH_WORD.search(item.stem)
            and (GRAPH_POINTED.search(item.stem)
                 or not GRAPH_DEFINED.search(item.stem))):
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
    if item.fmt == "mcq":
        repeated_reasons(item, report)

    mismatch = last_number_disagrees(item)
    if mismatch:
        report("rationale_final_number_mismatch", mismatch)
    for label, text in displayed_text(item):
        if PLACEHOLDER.search(text):
            report("placeholder", f"{label}: {text}")
            break


def ordinary_rejections(name: str, seed: int) -> Counter[str] | None:
    """Replay the registry's first 60 draws; return reasons only if all failed.

    ``generate`` now retries beyond 60 for ordinary bank seeds, so its success
    alone no longer reveals a low-yield template. Replaying the same draws
    keeps the scanner read-only and leaves the served item untouched.
    """
    fn = templates()[name]
    why: Counter[str] = Counter()
    for i in range(60):
        try:
            fn(random.Random(seed * 1_000_003 + i), seed)
        except (ItemError, ValueError, ZeroDivisionError, KeyError, StopIteration) as exc:
            why[f"{type(exc).__name__}: {exc}"] += 1
        else:
            return None
    return why


def main() -> int:
    findings: list[tuple[str, int, str, str]] = []
    names = sorted(templates())
    for name in names:
        exhausted: dict[int, Counter[str]] = {}
        for seed in range(50):
            def report(check: str, detail: str) -> None:
                findings.append((name, seed, check, snippet(detail)))

            try:
                item = generate(name, seed)
            except Exception as exc:
                report("generation_error", f"{type(exc).__name__}: {exc}")
                continue
            scan(item, report)
            why = ordinary_rejections(name, seed)
            if why is not None:
                exhausted[seed] = why
        if exhausted:
            seeds = list(exhausted)
            reason, count = exhausted[seeds[0]].most_common(1)[0]
            findings.append((name, seeds[0], "low_yield",
                             snippet(f"{len(seeds)}/50 seeds needed the fallback "
                                     f"after 60 draws (seeds {seeds}); "
                                     f"{count}× {reason}", limit=240)))

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
