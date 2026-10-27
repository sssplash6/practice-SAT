"""Gate for the authored Reading and Writing items in satbank/rw/.

Checks every item for shape, house style, length against the official cell it
models, verbatim overlap with any official passage, and sourcing; then, per
skill and tier, that passages are at least as dense as the official ones, with
sentence length and the key-longest rate close to official, and prints letter balance.

    python3 tools/check_rw.py            # all skills
    python3 tools/check_rw.py boundaries # one skill (parts are merged)
"""

from __future__ import annotations

import glob
import json
import os
import re
import statistics
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from satbank.rw_figures import render  # noqa: E402
BLANK = "______"
BLANK_SKILLS = {"boundaries", "form_structure_and_sense", "transitions", "inferences"}
NGRAM = 6


def words(s: str) -> list[str]:
    return re.findall(r"[a-z0-9’']+", s.lower().replace("<u>", " ").replace("</u>", " "))


def grams(s: str) -> set[tuple[str, ...]]:
    # the CB source line is house wording, not content
    s = re.sub(r"The following text is (adapted )?from", " ", s)
    w = words(s)
    return {tuple(w[i:i + NGRAM]) for i in range(len(w) - NGRAM + 1)}


def register(p: str) -> tuple[float, float, float]:
    """Mean word length, share of words of 9+ letters (names and sentence starts
    left out) and words per sentence: the official passages are denser than plain prose."""
    t = [x for x in re.findall(r"[A-Za-z’']+", re.sub(r"</?u>", " ", p)) if not x[0].isupper()]
    s = [x for x in re.split(r"(?<=[.!?”])\s+(?=[A-Z“])", re.sub(r"</?u>", "", p).replace("\n", " ")) if x.strip()]
    if not t:
        return 0.0, 0.0, 0.0
    return statistics.mean(map(len, t)), sum(len(x) >= 9 for x in t) / len(t), len(p.split()) / max(1, len(s))


def key_longest(it: dict) -> bool:
    o = it.get("options") or []
    return len(o) == 4 and it.get("answer_letter") in ("A", "B", "C", "D") and \
        len(o["ABCD".index(it["answer_letter"])]) == max(map(len, o))


def fidelity(slug: str, items: list[dict], cb: list[dict]) -> list[str]:
    """Per tier, ours must be about as dense as the official items: word length and long-word share
    no more than 0.05 chars/word or 1 point below (batch noise over ~8 passages a tier), and no more
    than 0.20 chars/word or 3 points above; sentence length within 15% and
    key-longest rate within 10 points."""
    bad, mean = [], statistics.mean
    for tier in ("easy", "medium", "hard"):
        a = [register(i["passage"]) for i in items if i["tier"] == tier]
        b = [register(i["passage"]) for i in cb if i["tier"] == tier]
        if not a or not b:
            continue
        ours, off = [mean(x[k] for x in a) for k in range(3)], [mean(x[k] for x in b) for k in range(3)]
        print(f"  {tier:6} chars/word {ours[0]:.2f} (CB {off[0]:.2f})  long words {100 * ours[1]:.1f}% "
              f"(CB {100 * off[1]:.1f}%)  words/sentence {ours[2]:.1f} (CB {off[2]:.1f})")
        if ours[0] < off[0] - 0.05 or ours[1] < off[1] - 0.01:
            bad.append(f"{tier} passages plainer than official")
        # two-sided (spec/rw/fidelity/README.md): overshooting density was itself a tell in the blind rounds
        elif ours[0] > off[0] + 0.20 or ours[1] > off[1] + 0.03:      # a warning while the bank is brought down to it
            print(f"  ~ {tier} passages denser than official (longer words than CB writes): aim at CB's figures")
        if abs(ours[2] - off[2]) > 0.15 * off[2]:
            bad.append(f"{tier} sentence length off")
    rate = lambda its: sum(map(key_longest, its)) / len(its)
    if abs(rate(items) - rate(cb)) > 0.10:
        bad.append(f"key longest {100 * rate(items):.0f}% vs official {100 * rate(cb):.0f}%")
    return bad


def official() -> tuple[dict, set]:
    """Official items by skill, and the 6-word runs that are content rather than
    house framing ("a student claims that the ..." recurs across many items)."""
    by_skill, seen = defaultdict(dict), Counter()
    for p in glob.glob(os.path.join(ROOT, "material/rw/transcripts/*.json")):
        d = json.load(open(p))
        by_skill[d["slug"]].update({it["id"]: it for it in d["items"]})
    # every official item in CB's bank, by cb id (band-7 pilot models), and the runs to avoid
    for p in glob.glob(os.path.join(ROOT, "material/rw/cb_api/*.json")):
        d = json.load(open(p))
        by_skill[os.path.basename(p)[:-5]].update({it["cb_id"]: it for it in d["items"]})
        for it in d["items"]:
            seen.update(grams(it["passage"]))
    return by_skill, {g for g, n in seen.items() if n < 3}


def ours() -> dict[tuple, set]:
    """6-word runs of every authored passage, served or staged (satbank/rw, spec/rw/waves), by item id,
    less the house framing that recurs across official items, so two of ours never share a sentence."""
    seen, index = Counter(), defaultdict(set)
    for p in glob.glob(os.path.join(ROOT, "material/rw/cb_api/*.json")):
        for it in json.load(open(p))["items"]:
            seen.update(numless(it["passage"]))
    framing = {g for g, n in seen.items() if n >= 3}
    paths = glob.glob(os.path.join(ROOT, "satbank/rw/*.json")) + glob.glob(os.path.join(ROOT, "spec/rw/waves/**/*.json"), recursive=True)
    for p in paths:
        for it in json.load(open(p)).get("items", []):
            for g in numless(it.get("passage", "")) - framing:
                index[g].add(it.get("id"))
    return index


def numless(s: str) -> set[tuple[str, ...]]:
    """6-word runs with no number in them: "in 2020 a team led by" or "more than 40 percent of the" is
    framing whatever the figures, and content two passages share always has number-free runs too."""
    return {g for g in grams(s) if not any(w.isdigit() for w in g)}


def load(slug: str | None) -> dict[str, list[dict]]:
    """One skill, every file in satbank/rw/, or one file by path (a band-7 pilot)."""
    out = defaultdict(list)
    paths = [slug] if slug and slug.endswith(".json") else sorted(glob.glob(os.path.join(ROOT, "satbank/rw/*.json")))
    slug = None if slug and slug.endswith(".json") else slug
    for p in paths:
        d = json.load(open(p))
        if slug and d["slug"] != slug:
            continue
        out[d["slug"]].extend(d["items"])
    return out


READING = {"central_ideas_and_details", "inferences", "command_of_evidence", "words_in_context",
           "text_structure_and_purpose", "cross_text_connections"}


def problems(it: dict, slug: str, off: dict, off_grams: set) -> list[str]:
    bad = []
    for k in ("id", "template", "tier", "passage", "stem", "options", "answer_letter", "explanation", "distractors"):
        if not it.get(k):
            bad.append(f"missing {k}")
    opts = it.get("options") or []
    if len(opts) != 4 or len(set(opts)) != 4:
        bad.append("options are not 4 distinct strings")
    key = it.get("answer_letter")
    if key not in ("A", "B", "C", "D"):
        bad.append(f"answer_letter {key!r}")
    elif sorted(it.get("distractors", {})) != sorted(set("ABCD") - {key}):
        bad.append("distractors must cover exactly the three wrong letters")
    text = " ".join([it.get("passage", ""), it.get("stem", ""), *opts])
    if "'" in text or '"' in text:
        bad.append("straight quote or apostrophe")
    if re.search(r" — |— | —", it.get("passage", "")):
        bad.append("spaced em dash (CB closes them)")
    blanks = it.get("passage", "").count(BLANK)
    if (slug in BLANK_SKILLS or "______" in it.get("stem", "")) and blanks != 1:
        bad.append(f"{blanks} blanks")
    models = [off[slug][m] for m in it.get("models", []) if m in off.get(slug, {})]
    if not models:
        bad.append("no official models listed")
    else:
        # cb_api passages carry their table rows as "cell | cell |" lines: count prose only
        med = statistics.median(len(" ".join(ln for ln in m["passage"].split("\n") if "|" not in ln).split())
                                for m in models)
        n = len(it["passage"].split()) + len(((it.get("table") or {}).get("title") or "").split())   # as CB prints it
        if n < .9 * med:      # near the models' median, not above it (spec/rw/fidelity/README.md: length was a tell)
            bad.append(f"passage {n} words, below the models' median {med:g}")
    shared = grams(it.get("passage", "")) & off_grams
    if shared:
        bad.append("shares wording with an official passage: " + " ".join(next(iter(shared))))
    # since 2026-10-16 only the reading skills need a source, for their core claim (spec/rw/waves/WAVE.md);
    # the others may use invented names and need none
    if slug in READING and not it.get("sources"):
        bad.append("no source for the core claim (reading skills keep one)")
    if it.get("figure"):
        try:
            render(it["figure"])
        except Exception as e:      # a figure that cannot draw would break the question at serve time
            bad.append(f"figure does not render: {e!r}")
    return bad


def main(argv: list[str]) -> int:
    off, off_grams = official()
    skills = load(argv[0] if argv else None)
    own = ours()
    failed = 0
    for slug, items in skills.items():
        ids = Counter(it.get("id") for it in items)
        dup = [i for i, n in ids.items() if n > 1]
        letters = Counter(it.get("answer_letter") for it in items)
        longest = sum(map(key_longest, items))
        tiers = Counter(it.get("tier") for it in items)
        print(f"\n{slug}: {len(items)} items  tiers {dict(tiers)}  keys {dict(sorted(letters.items()))}  "
              f"key longest {longest}/{len(items)}")
        if dup:
            print(f"  !! duplicate ids: {dup}")
            failed += len(dup)
        # register baselines stay on the transcribed set (ids like 3.11), as they were measured
        for b in fidelity(slug, items, [v for k, v in off.get(slug, {}).items() if "." in k]):
            print(f"  !! {b}")
            failed += 1
        for it in items:
            bad = problems(it, slug, off, off_grams)
            twin = sorted({i for g in numless(it.get("passage", "")) for i in own.get(g, ()) if i != it.get("id")})
            if twin:
                bad.append(f"shares wording with our own item {twin[0]}" + (f" (+{len(twin) - 1})" if len(twin) > 1 else ""))
            if bad:
                failed += 1
                print(f"  {it.get('id')}: " + "; ".join(bad))
    print(f"\n{sum(map(len, skills.values()))} items, {failed} with problems")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
