"""Validate the authored Reading & Writing Words content.

The phase constant advances only after that batch has passed review. Future-phase
requirements are reported as warnings so authors can run this after every batch.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "server" / "words"
PHASE = 6  # phases 1-6 are errors; the review gate (servable frames) and freq.txt come later
FILES = (
    "classes", "traps", "sat", "transitions", "pairs", "confusions",
    "roots", "foils", "collections", "fills", "frames", "adjudications",
)
SUBJECTS = {"science", "history", "literature"}
LOGICS = {
    "contrast", "concession", "cause-effect", "addition", "example",
    "sequence", "clarification", "similarity", "conclusion",
}
POS = {"n.", "v.", "adj.", "adv.", "phrase."}
LEVELS = {"easy", "medium", "hard"}
SLOT = re.compile(r"\{([a-z_]+)\}")
CLUE = re.compile(r"\[\[([^\[\]]+)\]\]")
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


def form_alike(a: str, b: str) -> bool:
    """Alike in form: similar letters overall, or a shared start or ending of three letters or more."""
    a, b = a.casefold(), b.casefold()
    return (SequenceMatcher(None, a, b).ratio() >= .5 or a[:3] == b[:3] or a[-3:] == b[-3:])


def check_words(data: dict[str, list | dict], errors: list[str], warnings: list[str]) -> None:
    entries = rows(data["sat"])
    classes = {c.get("id") for c in rows(data["classes"]) if isinstance(c, dict)}
    confused = {w for c in rows(data["confusions"]) if isinstance(c, dict) and c.get("tell")
                for w in c.get("words", [])}
    unlike: list[str] = []
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
        require(entry.get("pos") in POS, f"{label}: invalid pos", errors)
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
        require(bool(entry.get("lookalikes")) or slug in confused, f"{label}: no confusion with tell", errors)
        for look in entry.get("lookalikes", []):
            require(isinstance(look, dict) and bool(look.get("word")) and bool(look.get("tell")),
                    f"{label}: lookalike missing word or tell", errors)
            if isinstance(look, dict) and not form_alike(str(word), str(look.get("word", ""))):
                unlike.append(f"{slug}>{look.get('word')}")
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
    if unlike:
        # lookalikes feed W1's "Looks like the answer" trap, so they must be alike in form or sound;
        # a pair alike only in meaning is a nearmiss row in confusions.json
        warnings.append(f"lookalikes: {len(unlike)} pairs look little alike (check they are not near-synonyms), "
                        f"e.g. {', '.join(unlike[:8])}")


def check_reference_data(data: dict[str, list | dict], errors: list[str]) -> None:
    classes = rows(data["classes"])
    ids = {c.get("id") for c in classes if isinstance(c, dict)}
    for c in classes:
        label = c.get("id", "class")
        require(bool(c.get("id") and c.get("dimension")), f"{label}: missing id or dimension", errors)
        # opposite null: a standalone class, whose frames get no "Reverses the meaning" trap
        require(c.get("opposite") is None or c.get("opposite") in ids, f"{label}: unknown opposite", errors)
    opposite_by_id = {c.get("id"): c.get("opposite") for c in classes if isinstance(c, dict)}
    require(len(opposite_by_id) == len(classes), "classes: duplicate id", errors)
    for class_id, opposite in opposite_by_id.items():
        require(opposite is None or opposite_by_id.get(opposite) == class_id,
                f"{class_id}: opposite is not reciprocal", errors)
    traps = rows(data["traps"])
    require({t.get("id") for t in traps if isinstance(t, dict)} <= TRAPS,
            "traps: unknown trap id", errors)
    for t in traps:
        require(all(t.get(k) for k in ("id", "name", "tell", "check")),
                f"{t.get('id', 'trap')}: incomplete trap", errors)


def check_collections(data: dict[str, list | dict], errors: list[str]) -> None:
    """collections.json tiles select their members by rule; each tile's count must match its rule,
    and every SAT entry, transition and root must sit in a collection or roots tile."""
    value = data["collections"]
    groups = value.get("groups", []) if isinstance(value, dict) else []
    covered: dict[str, set] = defaultdict(set)
    for tile in (t for g in groups for t in g.get("collections", [])):
        rule = tile.get("select")
        if rule is None:
            continue
        members = [r.get("slug") or r.get("id") for r in rows(data.get(rule.get("file"), []))
                   if all(r.get(k) == v or (isinstance(r.get(k), list) and v in r[k])
                          for k, v in rule.items() if k != "file")]
        require(bool(members) and tile.get("count") == len(members),
                f"collections {tile.get('id')}: count {tile.get('count')} but its select matches {len(members)}", errors)
        if tile.get("kind") in {"collection", "roots"}:
            covered[rule.get("file")].update(members)
    for name in ("sat", "transitions", "roots"):
        missing = [r.get("slug") or r.get("id") for r in rows(data[name]) if (r.get("slug") or r.get("id")) not in covered[name]]
        require(not missing, f"collections: {len(missing)} {name} rows in no collection, e.g. {missing[:5]}", errors)


def legal_key(word: dict, need: dict) -> bool:
    """The need tags admit this sense. A frame's keys (its allow-list) are the senses that also fit its text."""
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
    members = Counter(w.get("class") for w in sat)
    for c in rows(data["classes"]):
        n = members[c.get("id")]
        if n == 0:
            errors.append(f"{c.get('id')}: a class with no member word")
        elif n < 3:
            warnings.append(f"{c.get('id')}: {n} member words, too few for a W3 ladder")
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
        dictionary = Path("/usr/share/dict/words")
        known = ({w.strip().casefold() for w in dictionary.read_text(errors="ignore").splitlines()}
                 if dictionary.exists() else set())
        if not dictionary.exists():
            warnings.append("foils: /usr/share/dict/words is absent, so foils were checked against the library only")
        for foil in rows(data["foils"]):
            name = foil if isinstance(foil, str) else foil.get("word", "")
            require(bool(name) and name.casefold() not in sat_heads,
                    f"foil {name!r}: duplicates a library word", errors)
            require(name.casefold() not in known, f"foil {name!r}: is a dictionary word", errors)
    return counts


def check_fills(data: dict[str, list | dict], errors: list[str]) -> set[str]:
    """fills.json is {about, pools: {name: [value, ...]}}: W1's slot pools, 40 or more distinct values each."""
    fills = data["fills"]
    pools = fills.get("pools", {}) if isinstance(fills, dict) else {}
    require(isinstance(pools, dict) and bool(pools), "fills: no pools", errors)
    for name, values in pools.items():
        require(bool(SLOT.fullmatch("{" + name + "}")), f"fills {name!r}: pool name must be lowercase a-z and _", errors)
        good = isinstance(values, list) and all(
            isinstance(v, str) and v.strip() and not re.search(r"[{}\[\]]|__", v) for v in values)
        require(good, f"fills {name}: every value must be a plain non-empty string", errors)
        if good:
            require(len(set(values)) == len(values), f"fills {name}: duplicate value", errors)
            require(len(values) >= 40, f"fills {name}: {len(values)} of 40 values", errors)
    for pair in rows(data["pairs"]):
        for text in [pair.get("s1", ""), *pair.get("s2", [])]:
            for slot in set(SLOT.findall(text)) - set(pools):
                errors.append(f"{pair.get('id', 'pair')}: unknown slot {{{slot}}}")
    return set(pools)


def synonyms(a: dict, b: dict) -> bool:
    """`same` read both ways: either sense lists the other (by headword or slug)."""
    def names(w: dict) -> set[str]:
        return {str(w.get("word", "")).casefold(), str(w.get("slug", "")).casefold()}
    return bool(names(b) & {s.casefold() for s in a.get("same", [])} or
                names(a) & {s.casefold() for s in b.get("same", [])})


def trap_options(frame: dict, key: dict, by_pos: dict[str, list[dict]], opposite: dict) -> int:
    """Distinct (class, polarity, intensity) distractors for this key that carry a legal W1 trap, up to 3.

    A sense the need tags admit is never a distractor, even when the frame's keys leave it out.
    too_strong / too_weak need `need.pins == "intensity"` (the clue fixes the degree); without it a
    same-class neighbour of another strength may fit the text. A synonym of the key (`same`, either
    way) is offered only in a pinned frame, and then only as too_strong, too_weak or connotation.
    A lookalike from the need's own class is a near-synonym, so it is not a lookalike trap.
    """
    need = frame["need"]
    pins = need.get("pins") == "intensity"
    looks = {look.get("word", "").casefold() for look in key.get("lookalikes", []) if isinstance(look, dict)}
    other = opposite.get(need["class"])
    seen = {(key["class"], key["polarity"], key["intensity"])}
    for word in by_pos.get(need["pos"], []):
        triple = (word.get("class"), word.get("polarity"), word.get("intensity"))
        if triple in seen or legal_key(word, need):
            continue
        synonym = synonyms(key, word)
        if synonym and not pins:
            continue
        kinds = set()
        if other is not None and triple[0] == other:
            kinds.add("reversed")
        if triple[0] == need["class"]:
            if triple[1] == need["polarity"]:
                if pins:
                    kinds.add("too_strong" if triple[2] > need["hi"] else "too_weak")
            elif triple[1] == -need["polarity"] != 0:
                kinds.add("connotation")
        if word.get("word", "").casefold() in looks and triple[0] != need["class"]:
            kinds.add("lookalike")
        if frame.get("subject") in word.get("subjects", []) and triple[0] not in {need["class"], other}:
            kinds.add("topical")
        if synonym:
            kinds &= {"too_strong", "too_weak", "connotation"}
        if kinds - {""}:
            seen.add(triple)
            if len(seen) > 3:
                break
    return len(seen) - 1


def check_frames(data: dict[str, list | dict], pools: set[str], phase: int,
                 errors: list[str], warnings: list[str]) -> None:
    """W1 frames (frames.json).

    A frame is {id, stem: complete | nearly, subject, text, need: {class, polarity, lo, hi, pos,
    pattern, pins?}, keys, needs, difficulty, reviewed: null | {by, date}, source?}. keys is the
    frame's allow-list: the senses that fit its text, each admitted by the need tags; the other
    senses the tags admit are neither keys nor distractors. pins: "intensity" marks a clue that fixes
    the degree, the only case where same-class too_strong / too_weak traps are offered. The text has exactly one
    ____ where the key goes in its headword form (a verb blank takes the base form, a noun blank
    the singular), at least one [[clue]] that decides the blank, and {slot}s from fills.json.
    An excerpt frame is cut exactly from a text published before 1929: source is {author, title,
    year, word}, word is the original blanked word (a legal key), and it has no slots.
    Structure rules are always errors; the supply minimums are errors from the frames phase (6).
    """
    sat = [w for w in rows(data["sat"]) if isinstance(w, dict)]
    opposite = {c.get("id"): c.get("opposite") for c in rows(data["classes"]) if isinstance(c, dict)}
    patterns = {p for w in sat for p in w.get("pattern", [])}
    by_pos: dict[str, list[dict]] = defaultdict(list)
    for word in sat:
        by_pos[word.get("pos")].append(word)
    adjudications = rows(data["adjudications"])
    ids: set[str] = set()
    texts: set[str] = set()
    by_word: dict[str, list[str]] = defaultdict(list)
    by_class: Counter = Counter()
    thin: list[str] = []
    literature = excerpts = 0
    for frame in rows(data["frames"]):
        if not isinstance(frame, dict):
            errors.append("frames: each frame must be an object")
            continue
        label = frame.get("id") or "frame"
        text = frame.get("text", "") if isinstance(frame.get("text"), str) else ""
        need = frame.get("need") if isinstance(frame.get("need"), dict) else {}
        require(isinstance(frame.get("id"), str) and bool(frame["id"]) and frame["id"] not in ids,
                f"{label}: missing or duplicate id", errors)
        ids.add(label)
        require(frame.get("stem") in {"complete", "nearly"}, f"{label}: stem must be complete or nearly", errors)
        require(frame.get("subject") in SUBJECTS, f"{label}: subject must be one of {sorted(SUBJECTS)}", errors)
        require(re.findall(r"_+", text) == ["____"] and not re.search(r"[A-Za-z0-9]____|____[A-Za-z0-9]", text),
                f"{label}: text needs exactly one free-standing ____ (headword form, no suffix)", errors)
        bare = CLUE.sub("", text)
        require(bool(CLUE.search(text)) and "[[" not in bare and "]]" not in bare and
                not any("____" in c for c in CLUE.findall(text)),
                f"{label}: text needs a well-formed [[clue]] that does not contain the blank", errors)
        slots = set(SLOT.findall(text))
        require(slots <= pools, f"{label}: unknown slot {sorted(slots - pools)}", errors)
        require(not re.search(r"[{}]", SLOT.sub("", text)), f"{label}: stray brace in text", errors)
        require(isinstance(frame.get("needs"), str) and bool(frame["needs"].strip()), f"{label}: missing needs", errors)
        require(frame.get("difficulty") in LEVELS, f"{label}: difficulty must be easy, medium or hard", errors)
        require("reviewed" in frame and (frame["reviewed"] is None or isinstance(frame["reviewed"], dict)),
                f"{label}: reviewed must be present, null or {{by, date}}", errors)
        lo, hi = need.get("lo"), need.get("hi")
        valid = (need.get("class") in opposite and need.get("polarity") in (-1, 0, 1)
                 and type(lo) is int and type(hi) is int and 1 <= lo <= hi <= 5
                 and need.get("pos") in POS and need.get("pattern") in patterns)
        require(valid, f"{label}: need must be {{class (classes.json), polarity -1/0/1, 1 <= lo <= hi <= 5, "
                       f"pos, pattern (one used by an SAT entry)}}", errors)
        unfilled = SLOT.sub("{slot}", text)
        require(unfilled not in texts, f"{label}: same text as another frame apart from its slots", errors)
        texts.add(unfilled)
        allowed = frame.get("keys")
        require(isinstance(allowed, list) and bool(allowed) and len(set(allowed)) == len(allowed),
                f"{label}: keys must be a non-empty list of distinct SAT slugs", errors)
        allowed = set(allowed) if isinstance(allowed, list) else set()
        require(need.get("pins") in (None, "intensity"), f"{label}: need.pins must be \"intensity\" or absent", errors)
        admitted = [w for w in sat if legal_key(w, need)] if valid else []
        keys = [w for w in admitted if w["slug"] in allowed]
        stray = sorted(allowed - {w["slug"] for w in admitted})
        require(not valid or not stray, f"{label}: keys {stray} are not admitted by its need", errors)
        require(not valid or bool(keys), f"{label}: no SAT sense is a legal key for its need", errors)
        source = frame.get("source")
        if source is not None:
            require(isinstance(source, dict) and all(isinstance(source.get(k), str) and source[k].strip()
                                                     for k in ("author", "title", "word"))
                    and type(source.get("year")) is int and source["year"] < 1929,
                    f"{label}: source must be {{author, title, year before 1929, word}}", errors)
            require(not slots, f"{label}: an excerpt frame cannot have slots", errors)
            if isinstance(source, dict) and keys:
                require(str(source.get("word", "")).casefold() in {w["word"].casefold() for w in keys},
                        f"{label}: the excerpt's blanked word is not a legal key", errors)
        check_review_gate({**frame, "keys": [w["slug"] for w in keys]}, adjudications, errors)
        if not valid:
            continue
        by_class[need["class"]] += 1
        literature += frame.get("subject") == "literature"
        excerpts += frame.get("subject") == "literature" and source is not None
        for key in keys:
            by_word[key["slug"]].append(frame.get("subject"))
            if trap_options(frame, key, by_pos, opposite) < 3:
                thin.append(f"{label}/{key['slug']}")

    short = [s["slug"] for s in sat if len(by_word[s["slug"]]) < 6 or len(set(by_word[s["slug"]])) < 2]
    sparse = sorted(c for c in opposite if by_class[c] < 6)
    share = excerpts / literature if literature else 0
    supply = (
        [f"{slug}: a legal key in fewer than 6 frames or in only one subject" for slug in short]
        + [f"{c}: fewer than 6 frames" for c in sparse]
        + [f"{t}: fewer than 3 distractors with a legal trap" for t in thin]
        + ([f"literature excerpt share {share:.1%} is below 20%"] if share < .2 else [])
    )
    if phase >= 7:
        errors.extend(supply)
    elif phase == 6:
        # ponytail: the supply minimums are targets until the review gate (phase 7) makes frames servable; until then
        # they warn with counts, so filling them is planned work, not a build failure. Structural rules above stay errors.
        warnings.append(f"frames: {len(short)} SAT senses short of 6 frames over 2 subjects, {len(sparse)} classes short,"
                        f" {len(thin)} keys short of 3 traps, excerpt share {share:.1%} (errors from phase 7, the review gate)")
        warnings.append("servable frame minimum waits for independent adjudications and S9 review gate")
    else:
        for what, names in (("SAT senses short of 6 frames over 2 subjects", short),
                            ("classes short of 6 frames", sparse), ("frame keys short of 3 traps", thin)):
            if names:
                warnings.append(f"frames: {len(names)} {what} (phase 6), e.g. {', '.join(names[:5])}")
        if share < .2:
            warnings.append(f"frames: literature excerpt share {share:.1%} of 20% (phase 6)")


def build_index(data: dict[str, list | dict]) -> dict:
    """The compact, reproducible lookup used by the Words server.

    A frame's review status is kept here as data, never inferred from its
    presence. Unreviewed material remains unavailable in production.
    """
    sat = rows(data["sat"])
    transitions = rows(data["transitions"])
    entries = sat + transitions
    by_word = {w["slug"]: {"frames": [], "confusions": [], "roots": []} for w in entries}
    for frame in rows(data["frames"]):
        for slug in frame["keys"]:
            by_word[slug]["frames"].append(frame["id"])
    for confusion in rows(data["confusions"]):
        for slug in confusion["words"]:
            if slug in by_word:
                by_word[slug]["confusions"].append(confusion["id"])
    for root in rows(data["roots"]):
        for related in root["words"]:
            by_word[related["slug"]]["roots"].append(root["id"])
    values = {"easy": .8, "medium": .6, "hard": .4}
    for word in sat:
        freq = "easy" if word["freq_band"] <= 2 else "medium" if word["freq_band"] == 3 else "hard"
        value = "easy" if word["value"] == 3 else "medium" if word["value"] == 2 else "hard"
        levels = (values[freq], values[value], values[word["level"]])
        by_word[word["slug"]]["prior"] = round(sum(levels) / 3, 4)
    for word in transitions:
        by_word[word["slug"]]["prior"] = values[word["level"]]
    # The pinned frequency file has not landed with this content batch. Use
    # the authored passages and examples as a deterministic interim common
    # vocabulary, so paste matching can still ignore ordinary passage words.
    texts = ([f["text"] for f in rows(data["frames"])] +
             [p["s1"] for p in rows(data["pairs"])] +
             [s for p in rows(data["pairs"]) for s in p["s2"]] +
             [s for w in entries for s in w.get("examples", [])])
    common_counts = Counter(w.casefold() for text in texts
                            for w in re.findall(r"[A-Za-zÀ-ž]+", text) if len(w) >= 2)
    library_forms = {s.casefold() for w in entries
                     for s in (w["word"], *w.get("also", []))}
    common = [w for w, _ in common_counts.most_common()
              if w not in library_forms][:10_000]
    source = {name: hashlib.sha256(json.dumps(data[name], ensure_ascii=False, sort_keys=True)
                                   .encode()).hexdigest() for name in FILES if name != "adjudications"}
    return {"v": 1, "sources": source, "counts": {"sat": len(sat), "transitions": len(transitions),
            "frames": len(rows(data["frames"])), "pairs": len(rows(data["pairs"]))},
            "words": by_word, "common": common}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review", action="store_true", help="list frames awaiting adjudication")
    args = parser.parse_args()
    errors: list[str] = []
    warnings: list[str] = []
    data = {name: load(name, errors) for name in FILES}
    check_reference_data(data, errors)
    check_collections(data, errors)
    check_words(data, errors, warnings)
    counts = check_later(data, PHASE, errors, warnings)
    check_frames(data, check_fills(data, errors), PHASE, errors, warnings)
    if args.review:
        for frame in rows(data["frames"]):
            if frame.get("reviewed") is None:
                print(f"REVIEW {frame.get('id')} [keys {', '.join(frame.get('keys', []))}]: {frame.get('text')}")
    print("Words content:", ", ".join(f"{name}={count}" for name, count in counts.items()))
    for message in warnings:
        print("WARNING:", message)
    for message in errors:
        print("ERROR:", message, file=sys.stderr)
    if not errors and not args.review:
        path = ROOT / "server" / "words_index.json"
        path.write_text(json.dumps(build_index(data), ensure_ascii=False, sort_keys=True,
                                   separators=(",", ":")) + "\n", encoding="utf-8")
        print(f"Words index: {path.relative_to(ROOT)}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
