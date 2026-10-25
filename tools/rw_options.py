"""Rule checks on the answer options of Transitions and Boundaries items.

The official bank never offers two acceptable options. Where the rule is
mechanical, code can see a second acceptable option before a reviewer does:
Transitions options are looked up in the bank's own connective inventory
(spec/rw/transitions.md, section 7a), Boundaries options are compared mark by mark.

    python3 tools/rw_options.py              # self-check, then every authored item
    python3 tools/rw_options.py <file.json>  # a staged batch
"""

from __future__ import annotations

import functools
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# pairs the bank never offers as key plus decoy, because both would read as acceptable
EXCLUDED = [{"contrast", "concession"}, {"addition", "similarity"}, {"example", "specification"},
            {"purpose", "cause"}, {"appropriateness", "cause"}]


@functools.cache
def relations() -> dict[str, str]:
    """Connective -> fine relation, from the inventory tables in transitions.md 7a."""
    out, rel = {}, None
    text = open(os.path.join(ROOT, "spec/rw/transitions.md"), encoding="utf-8").read()
    for line in text.split("### 7a.")[1].split("### 7b.")[0].splitlines():
        m = re.match(r"\*\*([A-Za-z]+)", line)
        if m:
            rel = m.group(1).lower()
        elif line and not line.startswith("|"):
            rel = None                           # prose after the last table, then a totals table
        m = re.match(r"\| ([a-z’' ]+?) \| \d", line)
        if m and rel:
            out[m.group(1).replace("'", "’")] = rel
    return out


def connective(option: str) -> str:
    return option.strip().rstrip(",").strip().lower().replace("'", "’")


def transitions(it: dict) -> list[str]:
    rel, bad = relations(), []
    opts = [connective(o) for o in it["options"]]
    unknown = [o for o in opts if o not in rel]
    if unknown:
        return [f"not in the official connective inventory: {', '.join(unknown)}"]
    key = rel[opts["ABCD".index(it["answer_letter"])]]
    decoys = [rel[o] for i, o in enumerate(opts) if "ABCD"[i] != it["answer_letter"]]
    if key in decoys:
        bad.append(f"a decoy shares the key's relation ({key})")
    for d in set(decoys):
        if {key, d} in EXCLUDED:
            bad.append(f"{d} decoy next to a {key} key reads as acceptable")
    if len(decoys) - len(set(decoys)) > 1:
        bad.append("decoys repeat a relation more than once")
    return bad


def mark(option: str, first: str) -> str:
    """What an option puts at the boundary: the option minus its first word, lowercased."""
    return option[len(first):].strip().lower()


def boundaries(it: dict) -> list[str]:
    if it["template"].startswith("S6"):          # question items vary word order on purpose
        return []
    opts = it["options"]
    firsts = {re.match(r"[^\s,;:.—?)”]+", o).group(0) for o in opts}      # a closing quote belongs to the mark
    if len(firsts) != 1:
        return ["options do not share their first word"]
    first = firsts.pop()
    marks = [mark(o, first) for o in opts]
    key = marks["ABCD".index(it["answer_letter"])]
    bad = []
    # S2 offers both as fragment decoys; a twin only matters when one of them is the key
    if sum(m.replace(";", ".") == key.replace(";", ".") for m in marks) > 1:
        bad.append("a period and a semicolon version of the key are both offered")
    if re.match(r", (and|but)\b", key) and any(m in (";", ".") for m in marks):
        bad.append("comma plus conjunction key next to a semicolon or period option")
    if key.startswith(":") and "—" + key[1:] in marks:
        bad.append("colon key next to a lone dash option")
    return bad


CHECKS = {"transitions": transitions, "boundaries": boundaries}


def demo() -> None:
    assert relations()["however"] == "contrast" and relations()["that said"] == "concession"
    t = lambda opts, k: transitions({"options": opts, "answer_letter": k})
    assert t(["However,", "As a result,", "Similarly,", "In conclusion,"], "A") == []
    assert t(["However,", "Nevertheless,", "Similarly,", "For example,"], "A")    # contrast key, concession decoy
    assert t(["By contrast,", "However,", "Thus,", "For example,"], "A")         # shared relation
    assert t(["Anyway,", "However,", "Thus,", "For example,"], "B")              # not in the inventory
    b = lambda opts, k, tm="S1_comma_conj": boundaries({"options": opts, "answer_letter": k, "template": tm})
    assert b(["baffling but", "baffling, but", "baffling,", "baffling, but,"], "B") == []
    assert b(["figures;", "figures,", "figures.", "figures"], "A")               # twin period / semicolon
    assert b(["Chad.", "Chad;", "Chad,", "Chad"], "C") == []                    # both strong marks wrong
    assert b(["work, but", "work;", "work", "work,"], "A")                       # comma+but next to semicolon
    assert b(["extensive:", "extensive—", "extensive", "extensive;"], "A")       # colon next to lone dash
    assert b(["Chad,", "Chad", "Chad;", "Chad, and"], "A") == []
    assert b(["fortune,”", "fortune”,", "fortune”", "fortune.”"], "A") == []       # quote marks: first word is still "fortune"


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from check_rw import load
    demo()
    n = 0
    # with file paths (a staged wave batch), check those files; else every served item
    sets = [load(p) for p in sys.argv[1:]] or [load(slug) for slug in CHECKS]
    for skills in sets:
        for slug, items in skills.items():
            for it in items if slug in CHECKS else ():
                for b in CHECKS[slug](it):
                    n += 1
                    print(f"{it['id']}: {b}")
    print(f"self-check ok, {n} problems")
