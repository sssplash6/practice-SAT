"""The quality gate. A topic ships when this is green, and not before.

Seven checks, in the order a failure is worth hearing about:

  coverage      every official item is either encoded or excluded with a reason
  transcript    the questions were transcribed, and each agrees with the key table
  acceptance    the engine reproduces every official answer it claims to
  audit         generated items survive an independently written solver, at volume
  structure     four distinct options, ascending, key never alone in its form
  prose         no placeholder, no doubled space, no sentence that is not one
  capacity      no template is a one-trick: each can make hundreds of items

The official answers come from `material/keys/<slug>.json`, extracted from the
PDF's own text layer, and the options from `material/transcripts/<slug>.json`.
An author cannot make a wrong template pass by writing down the answer.
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass

from .item import ItemError, norm_text, numeral
from .registry import generate
from .topic import BROKEN, Topic, key_file, load_topics, transcript

__all__ = ["check_topic", "check_all", "Result"]

MIN_CAPACITY = 200          # distinct items a template must be able to make
MAX_EXCLUDED = 0.15         # of a topic's official items
MIN_NAMED_DISTRACTORS = 0.80
MIN_OFFICIAL_OPTIONS = 0.40
FILLER = "near-miss arithmetic slip"


@dataclass
class Result:
    name: str
    ok: bool
    stat: str
    detail: list[str]


# "the table above", "the table shows" -- but not "the graph of the equation
# above", which points at a line of the stem, and not "each of the following
# tables", where the tables are the options themselves
TABLE_REF = re.compile(r"\btables?\b[^.]{0,20}\b(above|below|shown|gives|lists)\b"
                       r"|\b(above|below)\b[^.]{0,12}\btables?\b", re.I)

# a unit printed after the number: "8 cm²", "12 ft", "35 degrees"
UNIT = re.compile(r"(cm|mm|km|inches|inch|feet|foot|yards|yard|units|unit|"
                  r"degrees|degree|°|%|m|in|ft|yd)\d*$")


def norm(s: str) -> str:
    """The engine's one spelling for an answer -- see `item.norm_text`."""
    return norm_text(s)


def _same(a: str, b: str) -> bool:
    if norm(a) == norm(b):
        return True
    try:                                    # 0.5 is 1/2, 7.79 is 7.790
        return abs(_num(a) - _num(b)) <= 1e-9 * max(1.0, abs(_num(a)))
    except (ValueError, ZeroDivisionError, TypeError):
        return False


def _num(s: str) -> float:
    """The number an option carries, unit and all removed."""
    v = numeral(s)
    if v is None:
        raise ValueError(f"{s!r} is not a number")
    return v


def official_answers(rec: dict, key_answer: str) -> list[str]:
    """What the item is allowed to answer. A grid-in may accept several."""
    if rec.get("format") == "spr" or key_answer not in tuple("ABCD"):
        return [a.strip() for a in re.split(r",\s+", key_answer) if a.strip()]
    return [rec["options"]["ABCD".index(key_answer)]]


def engine_answer(item) -> str:
    return item.choices["ABCD".index(item.answer)] if item.fmt == "mcq" else item.answer


# ------------------------------------------------------------------ checks

def _coverage(topic: Topic, key: dict) -> Result:
    ids = [it["id"] for it in key["items"]]
    encoded = {s.id for s in topic.sources}
    excluded = set(topic.excluded)
    missing = [i for i in ids if i not in encoded and i not in excluded]
    both = sorted(encoded & excluded)
    unknown = sorted((encoded | excluded) - set(ids))
    thin = [f"{i}: reason is too thin to review ({topic.excluded[i]!r})"
            for i in sorted(excluded) if len(topic.excluded.get(i, "")) < 20]
    detail = []
    if missing:
        detail.append(f"{len(missing)} official items neither encoded nor excluded: "
                      + ", ".join(missing[:12]) + (" ..." if len(missing) > 12 else ""))
    if both:
        detail += [f"{i} is both encoded and excluded" for i in both]
    if unknown:
        detail += [f"{i} is not in the answer key" for i in unknown]
    detail += thin
    share = len(excluded) / max(len(ids), 1)
    if share > MAX_EXCLUDED:
        detail.append(f"{len(excluded)} of {len(ids)} items excluded "
                      f"({share:.0%}); the ceiling is {MAX_EXCLUDED:.0%}")
    return Result("coverage", not detail,
                  f"{len(encoded)}/{len(ids)} encoded, {len(excluded)} excluded", detail)


def _transcript(topic: Topic, key: dict, tr: dict) -> Result:
    if not tr:
        return Result("transcript", False, "missing",
                      [f"no material/transcripts/{topic.slug}.json"])
    detail = []
    for it in key["items"]:
        rec = tr.get(it["id"])
        if rec is None:
            detail.append(f"{it['id']} was never transcribed")
            continue
        if not rec.get("stem", "").strip():
            detail.append(f"{it['id']} has no stem")
        if rec.get("cb_id") and rec["cb_id"] != it["cb_id"]:
            detail.append(f"{it['id']} transcribed under id {rec['cb_id']}, key says {it['cb_id']}")
        letter = it["answer"]
        if letter in tuple("ABCD") and len(letter) == 1:
            if rec.get("format") != "mcq":
                detail.append(f"{it['id']} is keyed {letter} but transcribed as {rec.get('format')}")
            elif len(rec.get("options", [])) != 4:
                detail.append(f"{it['id']} has {len(rec.get('options', []))} options, not four")
            elif rec.get("answer_value") and not _same(
                    rec["answer_value"], rec["options"]["ABCD".index(letter)]):
                detail.append(f"{it['id']}: key {letter} is "
                              f"{rec['options']['ABCD'.index(letter)]!r}, "
                              f"transcript says the answer is {rec['answer_value']!r}")
        elif rec.get("format") != "spr":
            detail.append(f"{it['id']} has a written-in answer but is transcribed as "
                          f"{rec.get('format')}")
        # a stem that sends the reader to a table it does not carry is an item
        # nobody can answer -- the commonest way a transcription goes wrong
        if TABLE_REF.search(rec.get("stem", "")) and not rec.get("table"):
            detail.append(f"{it['id']} points at a table that was not transcribed")
    return Result("transcript", not detail, f"{len(tr)}/{len(key['items'])} items", detail[:20])


def _acceptance(topic: Topic, key: dict, tr: dict) -> Result:
    by_id = {it["id"]: it for it in key["items"]}
    ok = 0
    detail, hit, total, exact, mcq = [], 0, 0, 0, 0
    for s in topic.sources:
        k = by_id.get(s.id)
        if k is None:
            detail.append(f"{s.id} is not in the answer key")
            continue
        rec = tr.get(s.id, {})
        try:
            item = s.build(random.Random(0))
        except Exception as exc:                                    # noqa: BLE001
            detail.append(f"{s.id}: template raised {type(exc).__name__}: {exc}")
            continue
        want = official_answers(rec, k["answer"])
        got = engine_answer(item)
        if any(_same(got, w) for w in want):
            ok += 1
        else:
            detail.append(f"{s.id} ({k['cb_id']}): official {'/'.join(want)!r}, engine {got!r}")
        if rec.get("format") and item.fmt != rec["format"]:
            detail.append(f"{s.id}: source is {rec['format']}, engine built {item.fmt}")
        if rec.get("options") and item.fmt == "mcq":
            mcq += 1
            off = {norm(o) for o in rec["options"]}
            mine = {norm(c) for c in item.choices}
            hit += len(off & mine)
            total += len(off)
            exact += off == mine
    share = hit / max(total, 1)
    stat = (f"{ok}/{len(topic.sources)} answers, {share:.0%} of official options recreated"
            f", {exact}/{max(mcq,1)} option sets exact")
    if mcq and share < MIN_OFFICIAL_OPTIONS:
        detail.append(f"only {share:.0%} of College Board's own options are reproduced; "
                      f"the floor is {MIN_OFFICIAL_OPTIONS:.0%} -- the distractors are "
                      "invented rather than modelled")
    return Result("acceptance", not detail and ok == len(topic.sources), stat, detail[:20])


def _volume(topic: Topic, per_template: int) -> tuple[Result, Result, Result, list]:
    """Generate at volume: the audit, the structure and the prose checks share
    one pass, because generating is the expensive part."""
    audit_bad, struct_bad, prose_bad = [], [], []
    named = total = made = 0
    items = []
    for name in topic.templates:
        for seed in range(per_template):
            try:
                item = generate(name, seed)
            except ItemError:
                continue
            except Exception as exc:                                # noqa: BLE001
                audit_bad.append(f"{name} seed {seed}: {type(exc).__name__}: {exc}")
                if len(audit_bad) > 8:
                    break
                continue
            made += 1
            items.append(item)
            struct_bad += _structure(item, name, seed)
            prose_bad += _prose(item, name, seed)
            if item.fmt == "mcq":
                for r in item.reasons:
                    if r == "":
                        continue
                    total += 1
                    named += r != FILLER
    share = named / max(total, 1)
    if total and share < MIN_NAMED_DISTRACTORS:
        struct_bad.append(f"only {share:.0%} of distractors name a misconception; "
                          f"the floor is {MIN_NAMED_DISTRACTORS:.0%}")
    return (Result("audit", not audit_bad, f"{made:,} items re-derived", audit_bad[:10]),
            Result("structure", not struct_bad,
                   f"{share:.0%} of distractors named", struct_bad[:10]),
            Result("prose", not prose_bad, f"{made:,} items read", prose_bad[:10]),
            items)


def _structure(item, name: str, seed: int) -> list[str]:
    out = []
    if item.fmt != "mcq":
        return out
    vals = []
    for c in item.choices:
        try:
            vals.append(_num(c))
        except (ValueError, ZeroDivisionError):
            vals = []
            break
    if vals and vals != sorted(vals):
        out.append(f"{name} seed {seed}: numeric options are not in ascending order: "
                   f"{item.choices}")
    key_i = "ABCD".index(item.answer)
    shapes = [_shape(c) for c in item.choices]
    if shapes.count(shapes[key_i]) == 1:
        out.append(f"{name} seed {seed}: the key is the only option that looks like "
                   f"{item.choices[key_i]!r} -- guessable without the mathematics")
    return out


def _shape(opt: str) -> tuple:
    """A crude surface signature: what the option looks like at a glance."""
    return (bool(re.search(r"[a-zA-Z]", opt.replace("pi", "").replace("π", ""))),
            "π" in opt or "pi" in opt, "√" in opt or "sqrt" in opt,
            "/" in opt, "." in opt, opt.strip().startswith("-"))


_PLACEHOLDER = re.compile(r"\{|\}|\bTODO\b|\bFIXME\b|\bNone\b|\bnan\b|\bundefined\b")


def _prose(item, name: str, seed: int) -> list[str]:
    out = []
    text = item.stem
    if _PLACEHOLDER.search(text):
        out.append(f"{name} seed {seed}: stem has an unrendered placeholder: {text[:90]!r}")
    if "  " in text:
        out.append(f"{name} seed {seed}: doubled space in the stem")
    if not text.rstrip().endswith(("?", ".", ":")):
        out.append(f"{name} seed {seed}: stem does not end a sentence: {text[-40:]!r}")
    if item.fmt == "mcq":
        for c in item.choices:
            if _PLACEHOLDER.search(c):
                out.append(f"{name} seed {seed}: option has a placeholder: {c!r}")
    if not item.rationale.strip():
        out.append(f"{name} seed {seed}: no rationale")
    return out


def _capacity(topic: Topic, draws: int) -> Result:
    # the floor is a property of the template, but it cannot be judged from
    # fewer draws than the floor itself, so a short pass asks for less
    floor = MIN_CAPACITY if draws >= MIN_CAPACITY * 4 else max(30, draws // 3)
    detail, counts = [], {}
    for name in topic.templates:
        seen = set()
        for seed in range(draws):
            try:
                it = generate(name, seed, verify=False)
            except Exception:                                       # noqa: BLE001
                # a draw that throws is a draw that makes no item; whether the
                # throw is a bug is the audit's business, and the gate must
                # report rather than crash
                continue
            seen.add((it.stem, it.figure, it.answer))
        counts[name] = len(seen)
        if len(seen) < floor:
            detail.append(f"{name}: only {len(seen)} distinct items in {draws:,} draws "
                          f"(floor {floor})")
    total = sum(counts.values())
    return Result("capacity", not detail, f"{total:,}+ distinct items", detail)


# ------------------------------------------------------------------- driver

def check_topic(slug: str, per_template: int = 300, draws: int = 1200,
                quick: bool = False) -> list[Result]:
    topics = load_topics()
    if slug not in topics:
        exc = BROKEN.get(slug)
        return [Result("import", False, "the topic does not load",
                       [f"{type(exc).__name__}: {exc}" if exc else
                        f"no topic under satbank/topics/ claims the slug {slug!r}"])]
    topic = topics[slug]
    key = key_file(slug)
    tr = transcript(slug)
    results = [_coverage(topic, key), _transcript(topic, key, tr),
               _acceptance(topic, key, tr)]
    a, s, p, _ = _volume(topic, 40 if quick else per_template)
    results += [a, s, p]
    results.append(_capacity(topic, 200 if quick else draws))
    return results


def check_all(slugs: list[str] | None = None, per_template: int = 300,
              draws: int = 1200, quick: bool = False, verbose: bool = True) -> int:
    loaded = load_topics()
    slugs = slugs or sorted(set(loaded) | set(BROKEN))
    worst = 0
    for slug in slugs:
        results = check_topic(slug, per_template, draws, quick)
        ok = all(r.ok for r in results)
        worst |= 0 if ok else 1
        name = loaded[slug].name if slug in loaded else slug
        print(f"\n{name}  [{slug}]  {'PASS' if ok else 'FAIL'}")
        for r in results:
            mark = "  ok  " if r.ok else " FAIL "
            print(f"  {mark} {r.name:<11} {r.stat}")
            if verbose or not r.ok:
                for d in r.detail:
                    print(f"          - {d}")
    return worst
