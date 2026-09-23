"""Validate the authored Reading & Writing Words content.

The phase constant advances only after that batch has passed review. Future-phase
requirements are reported as warnings so authors can run this after every batch.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "server" / "words"
PHASE = 1
FILES = (
    "classes", "traps", "sat", "transitions", "pairs", "confusions",
    "roots", "foils", "collections", "fills", "frames", "adjudications",
)
SUBJECTS = {"science", "history", "literature"}
LOGICS = {
    "contrast", "concession", "cause-effect", "addition", "example",
    "sequence", "clarification", "similarity", "conclusion",
}
TRAPS = {
    "reversed", "too_strong", "too_weak", "connotation", "lookalike",
    "everyday", "topical", "wrong_logic", "reversed_direction",
}
MINIMUMS = {
    2: {"classes": 150, "traps": 9, "sat_core": 400},
    3: {"sat_advanced": 600, "second_sense": 100, "answer_choice": 90},
    4: {"transitions": 80, "pairs": 150},
    5: {"confusions": 700, "roots": 80, "foils": 60},
    6: {"frames": 1500},
}


def load(name: str, problems: list[str]) -> list | dict:
    path = CONTENT / f"{name}.json"
    if not path.exists():
        return []
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        problems.append(f"{path.relative_to(ROOT)}: {exc}")
        return []
    if not isinstance(value, (list, dict)):
        problems.append(f"{name}: expected a JSON array or object")
        return []
    return value


def rows(value: list | dict, key: str = "entries") -> list:
    return value if isinstance(value, list) else value.get(key, [])


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def check_words(data: dict[str, list | dict], errors: list[str]) -> None:
    entries = rows(data["sat"])
    classes = {c.get("id") for c in rows(data["classes"]) if isinstance(c, dict)}
    slugs: set[str] = set()
    senses: set[tuple[str, str]] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append("sat: each entry must be an object")
            continue
        slug = entry.get("slug", "")
        word = entry.get("word", "")
        sense = entry.get("sense", "")
        label = slug or repr(word)
        require(bool(slug and isinstance(slug, str)), f"{label}: missing slug", errors)
        require(slug not in slugs, f"{label}: duplicate slug", errors)
        slugs.add(slug)
        pair = (str(word).casefold(), str(sense).casefold())
        require(pair not in senses, f"{label}: duplicate (word, sense)", errors)
        senses.add(pair)
        for field in ("word", "meaning", "short", "pos", "collection", "level", "tier"):
            require(bool(entry.get(field)), f"{label}: missing {field}", errors)
        require(len(entry.get("short", "")) <= 60, f"{label}: short exceeds 60 characters", errors)
        require(bool(entry.get("examples") or entry.get("cloze")), f"{label}: no example or cloze", errors)
        for example in entry.get("examples", []):
            require(isinstance(example, str) and bool(re.search(r"\[\[[^\[\]]+\]\]", example)),
                    f"{label}: example has no highlighted word", errors)
        require(entry.get("pos") in {"n.", "v.", "adj.", "adv.", "phrase."}, f"{label}: invalid pos", errors)
        require(entry.get("tier") in {"core", "advanced"}, f"{label}: invalid tier", errors)
        require(entry.get("level") in {"easy", "medium", "hard"}, f"{label}: invalid level", errors)
        require(entry.get("class") in classes, f"{label}: unknown class", errors)
        require(entry.get("polarity") in (-1, 0, 1), f"{label}: invalid polarity", errors)
        require(type(entry.get("intensity")) is int and 1 <= entry["intensity"] <= 5,
                f"{label}: invalid intensity", errors)
        require(isinstance(entry.get("pattern"), list) and bool(entry["pattern"]),
                f"{label}: missing pattern", errors)
        require(isinstance(entry.get("subjects"), list) and bool(set(entry["subjects"]) & SUBJECTS),
                f"{label}: missing subjects", errors)
        require(isinstance(entry.get("lists"), list) and isinstance(entry.get("uses"), list),
                f"{label}: lists and uses must be arrays", errors)
        require(entry.get("value") in (1, 2, 3), f"{label}: invalid value", errors)
        same = entry.get("same", [])
        require(isinstance(same, list) and len(same) >= 2 and
                all(isinstance(s, str) and s.strip() for s in same),
                f"{label}: fewer than 2 valid same", errors)
        require(bool(entry.get("opposite")) or entry.get("no_opposite") is True,
                f"{label}: no opposite or no_opposite", errors)
        require(bool(entry.get("lookalikes")), f"{label}: no confusion with tell", errors)
        for look in entry.get("lookalikes", []):
            require(isinstance(look, dict) and bool(look.get("word")) and bool(look.get("tell")),
                    f"{label}: lookalike missing word or tell", errors)
        if "answer-choice" in entry.get("lists", []):
            require(bool(entry.get("uses")), f"{label}: answer-choice entry missing uses", errors)
        if entry.get("second_sense"):
            require(bool(sense), f"{label}: second sense missing disambiguator", errors)
            require(len(entry.get("nearly", [])) >= 3, f"{label}: second sense needs 3 nearly texts", errors)
        require("freq_band" in entry or (ROOT / "tools/data/freq.txt").exists(),
                f"{label}: no frequency source or override", errors)
        if "freq_band" in entry:
            require(type(entry["freq_band"]) is int and 1 <= entry["freq_band"] <= 5,
                    f"{label}: invalid freq_band", errors)


def check_reference_data(data: dict[str, list | dict], errors: list[str]) -> None:
    classes = rows(data["classes"])
    ids = {c.get("id") for c in classes if isinstance(c, dict)}
    for c in classes:
        label = c.get("id", "class")
        require(bool(c.get("id") and c.get("dimension")), f"{label}: missing id or dimension", errors)
        require(c.get("opposite") in ids, f"{label}: unknown opposite", errors)
    opposite_by_id = {c.get("id"): c.get("opposite") for c in classes if isinstance(c, dict)}
    require(len(opposite_by_id) == len(classes), "classes: duplicate id", errors)
    for class_id, opposite in opposite_by_id.items():
        require(opposite_by_id.get(opposite) == class_id,
                f"{class_id}: opposite is not reciprocal", errors)
    traps = rows(data["traps"])
    require({t.get("id") for t in traps if isinstance(t, dict)} <= TRAPS,
            "traps: unknown trap id", errors)
    for t in traps:
        require(all(t.get(k) for k in ("id", "name", "tell", "check")),
                f"{t.get('id', 'trap')}: incomplete trap", errors)


def legal_key(word: dict, need: dict) -> bool:
    return (
        word.get("class") == need.get("class")
        and word.get("polarity") == need.get("polarity")
        and need.get("lo", 0) <= word.get("intensity", -1) <= need.get("hi", 0)
        and word.get("pos") == need.get("pos")
        and need.get("pattern") in word.get("pattern", [])
    )


def check_review_gate(item: dict, adjudications: list, errors: list[str]) -> None:
    """A reviewed template needs two independent matching approvals per item."""
    if item.get("reviewed") is None:
        return
    ident = item.get("id", "template")
    require(isinstance(item.get("reviewed"), dict) and
            all(item["reviewed"].get(k) for k in ("by", "date")),
            f"{ident}: reviewed metadata incomplete", errors)
    keys = item.get("keys") or item.get("fits") or []
    for key in keys:
        for seed in range(5):
            votes = [a for a in adjudications if a.get("frame") == ident and
                     a.get("key") == key and a.get("seed") == seed]
            approved = {a.get("by") for a in votes if a.get("verdict") == "one" and
                        a.get("option") == key}
            require(len(approved) >= 2 and not any(a.get("verdict") != "one" for a in votes),
                    f"{ident}/{key}/{seed}: reviewed without two agreeing adjudications", errors)


def check_later(data: dict[str, list | dict], phase: int, errors: list[str], warnings: list[str]) -> dict[str, int]:
    sat = rows(data["sat"])
    transitions = rows(data["transitions"])
    pairs = rows(data["pairs"])
    frames = rows(data["frames"])
    counts = {
        "classes": len(rows(data["classes"])), "traps": len(rows(data["traps"])),
        "sat_core": sum(w.get("tier") == "core" and not w.get("second_sense") for w in sat),
        "sat_advanced": sum(w.get("tier") == "advanced" and not w.get("second_sense") for w in sat),
        "second_sense": sum(bool(w.get("second_sense")) for w in sat),
        "answer_choice": sum("answer-choice" in w.get("lists", []) for w in sat),
        "transitions": len(transitions), "pairs": len(pairs),
        "confusions": len(rows(data["confusions"])), "roots": len(rows(data["roots"])),
        "foils": len(rows(data["foils"])), "frames": len(frames),
    }
    if phase >= 2:
        require({t.get("id") for t in rows(data["traps"])} == TRAPS,
                "traps: expected exactly the nine W1 trap kinds", errors)
    for gate_phase, minimums in MINIMUMS.items():
        for name, minimum in minimums.items():
            if counts[name] < minimum:
                target = errors if gate_phase <= phase else warnings
                target.append(f"{name}: {counts[name]} of {minimum} minimum (phase {gate_phase})")
    if phase >= 4:
        for transition in transitions:
            label = transition.get("slug", "transition")
            require(bool(transition.get("word") and transition.get("meaning") and
                         transition.get("short") and transition.get("pos") and
                         transition.get("examples")) and transition.get("logic") in LOGICS,
                    f"{label}: incomplete transition", errors)
            require(len(transition.get("short", "")) <= 60,
                    f"{label}: short exceeds 60 characters", errors)
        logic_counts = Counter(p.get("logic") for p in pairs)
        for logic in LOGICS:
            require(logic_counts[logic] >= 15, f"pairs: {logic} has {logic_counts[logic]} of 15", errors)
        for pair in pairs:
            require(pair.get("logic") in LOGICS and len(pair.get("s2", [])) >= 5 and
                    bool(pair.get("fits")) and pair.get("subject") in SUBJECTS,
                    f"{pair.get('id', 'pair')}: invalid transition family", errors)
            check_review_gate(pair, rows(data["adjudications"]), errors)
    if phase >= 5:
        for confusion in rows(data["confusions"]):
            require(confusion.get("kind") in {"lookalike", "nearmiss", "sense"} and
                    len(confusion.get("words", [])) == 2 and bool(confusion.get("tell")),
                    f"{confusion.get('id', 'confusion')}: incomplete confusion", errors)
        sat_slugs = {w.get("slug") for w in sat}
        sat_heads = {w.get("word", "").casefold() for w in sat}
        for root in rows(data["roots"]):
            require(bool(root.get("id") and root.get("forms") and root.get("meaning") and
                         root.get("origin")), f"{root.get('id', 'root')}: incomplete root", errors)
            for related in root.get("words", []):
                slug = related.get("slug")
                word = next((w.get("word", "") for w in sat if w.get("slug") == slug), "")
                require(slug in sat_slugs and related.get("split", "").replace("|", "").casefold()
                        == word.casefold() and bool(related.get("gloss")),
                        f"{root.get('id', 'root')}: invalid split for {slug}", errors)
        for foil in rows(data["foils"]):
            name = foil if isinstance(foil, str) else foil.get("word", "")
            require(bool(name) and name.casefold() not in sat_heads,
                    f"foil {name!r}: duplicates a library word", errors)
    if phase >= 6:
        by_word: dict[str, list[dict]] = defaultdict(list)
        by_class: Counter = Counter()
        seen_texts: set[str] = set()
        for frame in frames:
            label = frame.get("id", "frame")
            need = frame.get("need", {})
            require(frame.get("subject") in SUBJECTS and frame.get("stem") in {"complete", "nearly"}
                    and all(k in need for k in ("class", "polarity", "lo", "hi", "pos", "pattern"))
                    and "reviewed" in frame and "____" in frame.get("text", "")
                    and "[[" in frame.get("text", ""), f"{label}: malformed or prematurely reviewed", errors)
            unfilled = re.sub(r"\{[^{}]+\}", "{slot}", frame.get("text", ""))
            require(unfilled not in seen_texts, f"{label}: duplicate unfilled text", errors)
            seen_texts.add(unfilled)
            by_class[need.get("class")] += 1
            candidates = [w for w in sat if legal_key(w, need)]
            require(bool(candidates), f"{label}: no legal SAT key", errors)
            for word in candidates:
                by_word[word["slug"]].append(frame)
            check_review_gate({**frame, "keys": [w["slug"] for w in candidates]},
                              rows(data["adjudications"]), errors)
        for entry in sat:
            candidates = by_word[entry["slug"]]
            require(len(candidates) >= 6, f"{entry['slug']}: fewer than 6 legal frames", errors)
            require(len({f["subject"] for f in candidates}) >= 2,
                    f"{entry['slug']}: legal frames cover fewer than 2 subjects", errors)
        for class_id in {c.get("id") for c in rows(data["classes"])}:
            require(by_class[class_id] >= 6,
                    f"{class_id}: fewer than 6 frames", errors)
        literature = [f for f in frames if f.get("subject") == "literature"]
        excerpt = [f for f in literature if f.get("source")]
        share = len(excerpt) / len(literature) if literature else 0
        require(share >= .2, f"literature excerpt share {share:.1%} is below 20%", errors)
        warnings.append("servable frame minimum waits for independent adjudications and S9 review gate")
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review", action="store_true", help="list frames awaiting adjudication")
    args = parser.parse_args()
    errors: list[str] = []
    warnings: list[str] = []
    data = {name: load(name, errors) for name in FILES}
    check_reference_data(data, errors)
    check_words(data, errors)
    counts = check_later(data, PHASE, errors, warnings)
    if args.review:
        for frame in rows(data["frames"]):
            if frame.get("reviewed") is None:
                print(f"REVIEW {frame.get('id')}: {frame.get('text')}")
    print("Words content:", ", ".join(f"{name}={count}" for name, count in counts.items()))
    for message in warnings:
        print("WARNING:", message)
    for message in errors:
        print("ERROR:", message, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
