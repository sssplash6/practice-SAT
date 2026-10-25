"""The Reading and Writing bank as topics: one per skill, one template per authored
template code, its items the reviewed ones in `satbank/rw/<slug>*.json`.

These items are written, not generated, so a template's seeds cycle over its few
fixed items (`seed % n`); practice's dedupe stops a learner seeing one twice. The
audit's solver is the authored key itself: the independent check for these items
was the blind solve and review (spec/rw/VERIFY.md), not a re-derivation. An item
with a figure gets its SVG from `rw_figures.render` at load time.

Self-check: python3 -m satbank.topics.rw
"""

from __future__ import annotations

import glob
import json
import os
import re
from collections import defaultdict
from itertools import zip_longest

from satbank import rw_figures
from satbank.exact import E
from satbank.item import Item
from satbank.topic import Topic

BANK = os.path.join(os.path.dirname(os.path.dirname(__file__)), "rw")
KIND = "rw_fixed"


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", re.sub(r"\(.*?\)", "", name.lower())).strip("_")


def _item(name: str, it: dict, seed: int) -> Item:
    letters = "ABCD"
    key = it["answer_letter"]
    table = it.get("table")
    item = Item(name, it.get("subtype") or it["template"], it["tier"], seed, it["stem"], "mcq", E(0), key,
                it["explanation"], list(it["options"]),
                ["" if L == key else it["distractors"][L]["why_wrong"] for L in letters],
                table=[table["columns"], *table["rows"]] if table else None,
                params={"kind": KIND, "key": it["options"][letters.index(key)]},
                source_id=it["id"], text=it["passage"])
    item.table_title = table.get("title") if table else None     # practice.to_question passes it on
    item.band = it.get("band")              # CB score band the item was written to (7 = "super hard"), when known
    fig = it.get("figure")
    if fig:
        item.figure = rw_figures.render(fig)
        item.figure_alt = fig["description"]
    return item


def _template(name: str, about: str, items: list[dict]):
    def make(rng, seed):
        return _item(name, items[seed % len(items)], seed)
    make.__doc__ = about
    return make


def _topics() -> list[Topic]:
    files = defaultdict(list)
    for path in sorted(glob.glob(os.path.join(BANK, "*.json"))):
        files[os.path.basename(path)[:-5].split("__")[0]].append(json.load(open(path)))
    out = []
    for slug, parts in sorted(files.items()):
        names = {}
        for t in (t for p in parts for t in p["plan"]["templates"]):
            names.setdefault(t["code"], t["name"])        # the first part names a code (band-7 parts come later)
        by_code = defaultdict(list)
        for p in parts:
            for it in p["items"]:
                by_code[it["template"]].append(it)
        topic = Topic(f"rw_{slug}", parts[0]["skill"], parts[0]["domain"],
                      audits={KIND: lambda params: params["key"]} if not out else {})
        used = set()
        for code, items in sorted(by_code.items()):
            short = _slug(names.get(code, code)) or code.lower()
            short = short if short not in used else f"{short}_{code.lower()}"
            used.add(short)
            # tiers interleaved, so the first seeds a survey samples (blueprint.kinds: 18) meet every tier
            tiers = [sorted((i for i in items if i["tier"] == t), key=lambda i: i["id"]) for t in ("easy", "medium", "hard")]
            items = [i for row in zip_longest(*tiers) for i in row if i]
            topic.templates[f"rw_{slug}.{short}"] = _template(f"rw_{slug}.{short}", names.get(code, code), items)
        out.append(topic)
    return out


TOPICS = _topics()


if __name__ == "__main__":
    from satbank.registry import generate, templates, topic_of
    from server import deps
    n = 0
    for t in templates():
        if not topic_of(t).startswith("rw_"):
            continue
        assert deps.subject_of(t) == "rw" and deps.subject_of(topic_of(t)) == "rw", t
        size = len({generate(t, s).source_id for s in range(300)})
        for s in range(size):
            it = generate(t, s)
            assert it.text and len(it.choices) == 4 and it.reasons.count("") == 1, (t, s)
            n += 1
        # the practice survey samples 18 seeds: every tier the type has must show among them
        assert {generate(t, s).difficulty for s in range(min(size, 18))} == {generate(t, s).difficulty for s in range(size)}, t
    print(f"{len(TOPICS)} skills, {n} items, all through registry.generate and the audit")
