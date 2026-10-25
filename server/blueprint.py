"""The shape of a digital SAT section (Math, and Reading and Writing), and filling a module to it.

Moved out of tools/build_mocks.py so a section can be built for one student at
the moment they sit it, against their own history, rather than only once onto
a fixed shelf. The tool still builds the shelf, from these same functions.

The numbers are the published ones where College Board publishes them and
stated choices where it does not; tools/build_mocks.py carries the reasoning
for each, and the README the sources.
"""

from __future__ import annotations

import hashlib
from collections import Counter

from . import practice

MODULE_SIZE = 22
MODULE_SECONDS = 35 * 60

# Domain counts per module: 15 / 15 / 7 / 7 over the two, the published
# 35 / 35 / 15 / 15 of a 44-question section.
DOMAIN_SPLIT = {
    1: {"Algebra": 8, "Advanced Math": 7,
        "Problem-Solving and Data Analysis": 4, "Geometry and Trigonometry": 3},
    2: {"Algebra": 7, "Advanced Math": 8,
        "Problem-Solving and Data Analysis": 3, "Geometry and Trigonometry": 4},
}

# Difficulty mixes, each summing to 22. Module 1 is centred; the two second
# modules lean equally far in opposite directions.
TIERS = {
    "module1":       {"easy": 7,  "medium": 8, "hard": 7},
    "module2_lower": {"easy": 11, "medium": 8, "hard": 3},
    "module2_upper": {"easy": 3,  "medium": 8, "hard": 11},
    # Tests' harder and easier module 1: practice, never a score estimate
    "module1_upper": {"easy": 3,  "medium": 8, "hard": 11},
    "module1_lower": {"easy": 11, "medium": 8, "hard": 3},
}
# Reading and Writing: 27 questions in 32 minutes a module, no grid-ins. Domains per module follow the
# published shares (26 / 28 / 20 / 26 per cent of 54); tier mixes are Math's scaled to 27.
RW_MODULE_SIZE = 27
RW_MODULE_SECONDS = 32 * 60
RW_DOMAIN_SPLIT = {
    1: {"Information and Ideas": 7, "Craft and Structure": 8,
        "Expression of Ideas": 5, "Standard English Conventions": 7},
    2: {"Information and Ideas": 7, "Craft and Structure": 7,
        "Expression of Ideas": 6, "Standard English Conventions": 7},
}
RW_TIERS = {
    "module1":       {"easy": 9,  "medium": 9,  "hard": 9},
    "module2_lower": {"easy": 13, "medium": 10, "hard": 4},
    "module2_upper": {"easy": 4,  "medium": 10, "hard": 13},
    "module1_upper": {"easy": 4,  "medium": 10, "hard": 13},
    "module1_lower": {"easy": 13, "medium": 10, "hard": 4},
}
# Skills inside a domain, by College Board Question Bank proportions (the 5k bank plan's split), and
# Bluebook's order: a module runs domain by domain, skill by skill, easiest to hardest inside each.
RW_SKILL_WEIGHT = {
    "rw_words_in_context": 776, "rw_text_structure_and_purpose": 443, "rw_cross_text_connections": 181,
    "rw_central_ideas_and_details": 323, "rw_command_of_evidence": 649, "rw_inferences": 328,
    "rw_boundaries": 658, "rw_form_structure_and_sense": 642,
    "rw_transitions": 487, "rw_rhetorical_synthesis": 513,
}
RW_ORDER = tuple(RW_SKILL_WEIGHT)           # the dict above is written in Bluebook's order

# the id prefix of each form's questions; every module 1 tier is 'm1'
PREFIX = {"module1": "m1", "module1_upper": "m1", "module1_lower": "m1",
          "module2_lower": "m2l", "module2_upper": "m2u"}

# College Board's own answer keys put grid-ins at 6, 7, 13, 14, 20, 21 and 27 of
# 27; scaled to 22 positions that is this.
SPR_AT = (6, 7, 13, 14, 21, 22)
SPR_PULL = 400         # a slot that wants a grid-in really wants one

# One record per subject, so a builder never hard-codes 22, 35 minutes or grid-in slots.
SPEC = {
    "math": {"module_size": MODULE_SIZE, "module_seconds": MODULE_SECONDS, "domain_split": DOMAIN_SPLIT,
             "tiers": TIERS, "spr_at": SPR_AT, "order": None, "skill_weight": None},
    "rw": {"module_size": RW_MODULE_SIZE, "module_seconds": RW_MODULE_SECONDS, "domain_split": RW_DOMAIN_SPLIT,
           "tiers": RW_TIERS, "spr_at": (), "order": RW_ORDER, "skill_weight": RW_SKILL_WEIGHT},
}


def spread(counts: dict[str, int]) -> list[str]:
    """The domains laid over the positions, each spread evenly from first to last.

    A module runs easiest to hardest, so where a domain sits decides how hard
    its questions are. Taking whichever domain had most left (the practice
    interleave) put the two small domains at the end, and every one of their
    questions was hard. Here each domain's k-th slot aims for the middle of
    the k-th equal stretch of the module, and the slots are dealt in that order.
    """
    n = sum(counts.values())
    marks = sorted(((k + .5) * n / c, d) for d, c in counts.items() for k in range(c))
    return [d for _, d in marks]


def module_of(form: str) -> int:
    """Which module's domain split a form uses: 2 for either module 2."""
    return 2 if form.startswith("module2") else 1


def ladder(form: str, subject: str = "math") -> list[str]:
    """The public tier of each position (X3's pace budgets): easiest first for Math, easiest first
    inside each skill for R&W."""
    return [tier for _, tier, _ in slots(form, module_of(form), subject)]


def skill_counts(counts: dict[str, int]) -> dict[str, int]:
    """R&W: each domain's count shared among its skills by RW_SKILL_WEIGHT, largest remainder first."""
    domain_of = {t: practice.catalogue()["topics"][t].domain for t in RW_ORDER}
    out: dict[str, int] = {}
    for dom, n in counts.items():
        skills = [t for t in RW_ORDER if domain_of[t] == dom]
        raw = {s: n * RW_SKILL_WEIGHT[s] / sum(RW_SKILL_WEIGHT[x] for x in skills) for s in skills}
        got = {s: int(raw[s]) for s in skills}
        for s in sorted(skills, key=lambda s: got[s] - raw[s])[:n - sum(got.values())]:
            got[s] += 1
        out.update(got)
    return out


def slots(form: str, module: int, subject: str = "math") -> list[tuple[str, str, str | None]]:
    """The (domain, difficulty, format) each position carries, in final order.

    Difficulty is sorted -- a module runs easiest to hardest -- and each domain
    is spread evenly across the positions, so every domain has easy, medium
    and hard questions in proportion.

    R&W runs in Bluebook's question-type order instead: each position is (skill topic, tier, None),
    the skills dealt their tiers from the module's mix the same way, then laid out skill by skill in
    RW_ORDER, easiest to hardest inside each.
    """
    rank = {"easy": 0, "medium": 1, "hard": 2}
    spec = SPEC[subject]
    ladder = sorted([t for t, n in spec["tiers"][form].items() for _ in range(n)],
                    key=lambda t: rank[t])
    if subject == "rw":
        dealt = zip(spread(skill_counts(RW_DOMAIN_SPLIT[module])), ladder)
        out = [(s, t, None) for s, t in sorted(dealt, key=lambda st: (RW_ORDER.index(st[0]), rank[st[1]]))]
    else:
        spread_ = spread(dict(DOMAIN_SPLIT[module]))
        out = [(dom, tier, "spr" if i + 1 in SPR_AT else None)
               for i, (dom, tier) in enumerate(zip(spread_, ladder))]
    assert len(out) == spec["module_size"], f"{subject} {form} module {module}: {len(out)} slots"
    return out


def survey(names: list[str], seeds: int = 18) -> dict[str, set[tuple[str, str]]]:
    """What each template can actually produce, as {(difficulty, format)}.

    A grid-in slot cannot be filled by a template that only makes multiple
    choice, and most make only one or the other.
    """
    from satbank.item import ItemError
    out: dict[str, set[tuple[str, str]]] = {}
    for n in names:
        kinds = set()
        for seed in range(seeds):
            try:
                it = practice.generate(n, seed)
            except (ItemError, Exception):
                continue
            kinds.add((it.difficulty, it.fmt))
        out[n] = kinds
    return out


_CAN: dict[str, set[tuple[str, str]]] = {}
_KINDS: dict[str, dict] = {}


def kinds() -> dict[str, dict]:
    """Catalogue survey: output shapes, labels, reasons and whole-item variety."""
    if _KINDS:
        return _KINDS
    from satbank.registry import templates
    from . import progress
    cat = practice.catalogue()
    for name, fn in templates().items():
        shapes: set[tuple[str, str]] = set()
        labels: Counter = Counter()
        reasons: dict[str, str] = {}
        seen: set[str] = set()
        asks: set[str] = set()
        for seed in range(18):
            try:
                item = practice.generate(name, seed)
            except Exception:
                continue
            shapes.add((item.difficulty, item.fmt))
            labels[item.skill] += 1
            seen.add(practice.question_hash(item))
            if getattr(item, "params", None) and item.params.get("ask"):
                asks.add(str(item.params["ask"]))
            for reason in list(item.reasons) + [getattr(m, "reason", "") for m in getattr(item, "spr_mistakes", ())]:
                if reason:
                    reasons.setdefault(progress.norm(reason), reason)
        label = labels.most_common(1)[0][0] if labels else name
        doc = (fn.__doc__ or "").strip().split("\n\n", 1)[0].strip()
        _KINDS[name] = {"kinds": shapes, "labels": labels, "skill": label,
                        "about": doc or label, "reasons": reasons,
                        "variety": len(seen), "axes": {"grid"} if any(f == "spr" for _, f in shapes) else set(),
                        "ask": sorted(asks), "topic": practice.topic_of(name),
                        "domain": cat["topics"][practice.topic_of(name)].domain}
        if len(asks) > 1:
            _KINDS[name]["axes"].add("ask")
    _CAN.update({name: value["kinds"] for name, value in _KINDS.items()})
    return _KINDS


def abilities() -> dict[str, set[tuple[str, str]]]:
    """The survey of every template, made once per process."""
    if not _CAN:
        kinds()
    return _CAN


def lookalikes(template: str, k: int = 3) -> list[str]:
    data = kinds()
    if template not in data:
        return []
    here = set(data[template]["reasons"])
    topic = data[template]["topic"]
    scored = []
    for other, info in data.items():
        if other == template:
            continue
        common = len(here & set(info["reasons"]))
        if common >= (1 if info["topic"] == topic else 2):
            scored.append((info["topic"] != topic, -common, other))
    return [x[2] for x in sorted(scored)[:k]]


def siblings(template: str, step: int) -> list[str]:
    """Adjacent tier alternatives, preferring the same template and skill."""
    if step not in (-1, 1):
        raise ValueError("step is -1 or 1")
    data = kinds()
    if template not in data:
        return []
    current = {t for t, _ in data[template]["kinds"]}
    targets = {("easy", "medium", "hard")[("easy", "medium", "hard").index(t) + step]
               for t in current if 0 <= ("easy", "medium", "hard").index(t) + step < 3}
    if any(t in targets for t, _ in data[template]["kinds"]):
        return [template]
    topic = data[template]["topic"]
    skill = data[template]["skill"]
    norms = set(data[template]["reasons"])
    candidates = []
    for other, info in data.items():
        if other == template or info["topic"] != topic or not any(t in targets for t, _ in info["kinds"]):
            continue
        candidates.append((info["skill"] != skill, -len(norms & set(info["reasons"])), other))
    return [x[2] for x in sorted(candidates)]


def by_domain() -> dict[str, list[str]]:
    cat = practice.catalogue()
    out: dict[str, list[str]] = {}
    for t, names in cat["by_topic"].items():
        out.setdefault(cat["topics"][t].domain, []).extend(names)
    for v in out.values():
        v.sort()
    return out


def draw_matching(b: practice.Builder, key: str, tier: str, fmt: str | None,
                  tries: int = 10) -> practice.Card | None:
    """Walk this template's seeds for a card of the right tier and format.

    A card that is not what the slot needs is kept anyway, which marks it used
    and advances the template to its next seed.
    """
    topic = practice.topic_of(key)
    for _ in range(tries):
        card = b.draw(key, topic)
        if card is None:
            return None
        right_tier = card.feats["difficulty"] == tier
        right_fmt = fmt is None or (card.item.fmt == "spr") == (fmt == "spr")
        if right_tier and right_fmt:
            return card
        b.keep(card)
    return None


def _hash(salt: str, t: str) -> str:
    return hashlib.sha1(f"{salt}:{t}".encode()).hexdigest()


def order_key(order: str, used: dict[str, int], salt: str, exposure: dict[str, int] | None = None):
    """X2: how a slot's pool is ranked before its first CANDIDATES are tried.

    shuffle   (uses in this module, sha1(builder seed + t)): every template that
              can make the slot is equally likely and exposure plays no part.
              Test-day sittings, papers' slot builds, Compete's forms.
    exposure  (uses, the learner's exposure to t, the same hash): Training
              sittings and custom tests bring the types met least.
    name      the old alphabetical key (it leaned to early names), kept only
              so tools/build_mocks.py can rebuild its shelf as it was.
    """
    if order == "name":
        return lambda t: (used.get(t, 0), t)
    if order == "exposure":
        seen = exposure or {}
        return lambda t: (used.get(t, 0), seen.get(t, 0), _hash(salt, t))
    if order != "shuffle":
        raise ValueError("order is shuffle, exposure or name")
    return lambda t: (used.get(t, 0), _hash(salt, t))


def fill(form_slots, domains: dict[str, list[str]], b: practice.Builder,
         can: dict[str, set[tuple[str, str]]], log=print, order: str = "shuffle",
         exposure: dict[str, int] | None = None) -> list[practice.Card]:
    """One module: the practice spread scoring, plus the format each slot wants."""
    chosen: list[practice.Card] = []
    used: dict[str, int] = {}
    missed = 0
    rank = order_key(order, used, b.learner, exposure)

    for want_domain, want_tier, want_fmt in form_slots:
        wants = (want_tier, want_fmt or "mcq")
        pool = [t for t in domains[want_domain] if t not in b.spent and wants in can.get(t, ())]
        if not pool:                           # no template makes it; widen to the tier
            pool = [t for t in domains[want_domain]
                    if t not in b.spent and any(k[0] == want_tier for k in can.get(t, ()))]
        ranked = sorted(pool, key=rank)

        cards = []
        for key in ranked:
            card = draw_matching(b, key, want_tier, want_fmt)
            if card:
                cards.append(card)
            if len(cards) >= practice.CANDIDATES:
                break

        if not cards:                          # take anything in the domain
            for key in sorted(domains[want_domain], key=rank):
                card = b.draw(key, practice.topic_of(key))
                if card:
                    cards.append(card)
                    break
        if not cards:
            log(f"    ran out in {want_domain} / {want_tier}")
            continue

        def cost(c):
            wrong_shape = (c.item.fmt == "spr") != (want_fmt == "spr")
            return practice.penalty(c, chosen, used) + (SPR_PULL if wrong_shape else 0)

        best = min(cards, key=cost)
        if want_fmt == "spr" and best.item.fmt != "spr":
            missed += 1
        b.keep(best)
        chosen.append(best)
        used[best.key] = used.get(best.key, 0) + 1

    if missed:
        log(f"    {missed} grid-in slots had no grid-in of the right kind to fill them")
    return chosen


def stored(cards: list[practice.Card], prefix: str, start: int = 1, sep: str = "q") -> list[dict]:
    """Cards as stored questions (key included), ids {prefix}q01.."""
    out = []
    for i, c in enumerate(cards, start):
        q = practice.to_question(c, i)
        q["id"] = f"{prefix}{sep}{i:02d}"
        out.append(q)
    return out


def module(form: str, b: practice.Builder, log=lambda *_: None, order: str = "shuffle",
           exposure: dict[str, int] | None = None, subject: str = "math") -> list[dict]:
    """A module built now, as stored questions, ids prefixed by the form. An R&W slot names its
    skill, so its pool is that skill's templates.
    ponytail: R&W items are fixed, so a learner who has seen every item of a skill gets a short
    module; reuse seen items (never this sitting's) if that ever happens."""
    pools = by_domain() if subject == "math" else practice.catalogue()["by_topic"]
    cards = fill(slots(form, module_of(form), subject), pools, b, abilities(), log, order, exposure)
    return stored(cards, PREFIX[form])


def slots_of(questions: list[dict]) -> list[list]:
    """A built module's slot list [[template, tier, fmt]]: what twins and papers keep."""
    return [[q["key"], q["difficulty"], q["type"]] for q in questions]


def _fallback(b: practice.Builder, template: str, tier: str, fmt: str | None,
              used: dict[str, int]) -> practice.Card | None:
    """The least-used template of the same topic that makes this tier and format."""
    want = (tier, fmt or "mcq")
    can = abilities()
    pool = [t for t in practice.catalogue()["by_topic"].get(practice.topic_of(template), [])
            if t != template and t not in b.spent and want in can.get(t, ())]
    for t in sorted(pool, key=order_key("shuffle", used, b.learner)):
        card = draw_matching(b, t, tier, fmt)
        if card:
            return card
    return None


def twin_slots(slot_list: list[list], b: practice.Builder, prefix: str, start: int = 1) -> list[dict]:
    """Each slot's template at its tier and format, on a seed of this learner's
    own (the Builder starts every learner somewhere else in the seed space), so
    everyone sitting the same slots has their own numbers. Positions follow the
    slot list; a template this learner has used up falls back within its topic."""
    cards: list[practice.Card] = []
    used: dict[str, int] = {}
    for template, tier, fmt, *_ in slot_list:
        f = fmt if fmt in ("mcq", "spr") else None
        # an R&W template's items are fixed and few: once its unseen ones at this tier are gone the
        # twin is another template of the same skill (an R&W topic is one skill) at the tier
        card = draw_matching(b, template, tier, f, tries=40) or _fallback(b, template, tier, f, used) \
            or b.draw(template, practice.topic_of(template))
        if card is None:
            raise LookupError(f"no twin for {template} at {tier}")
        b.keep(card)
        used[card.key] = used.get(card.key, 0) + 1
        cards.append(card)
    return stored(cards, prefix, start)


def twin(source: list[dict], b: practice.Builder) -> list[dict]:
    """A parallel form of a built module: the same template in every slot, at
    the same difficulty, position and format, with new seeds and the same ids."""
    out = twin_slots(slots_of(source), b, "x")
    for q, s in zip(out, source):
        q["id"] = s["id"]
    return out


def holds(questions: list[dict], subject: str = "math") -> dict:
    """What a module holds, in public counts only (the lobby's X2 facts)."""
    domains = Counter(q.get("domain") for q in questions)
    return {"subject": subject, "questions": len(questions),
            "domains": {d: domains[d] for d in SPEC[subject]["domain_split"][1] if domains[d]},
            "grid_ins": sum(q.get("type") == "spr" for q in questions)}


def custom_slots(topics: list[str], count: int, tiers: list[str], order: str,
                 formats: str) -> list[tuple[str, str, str]]:
    """A custom test's (topic, tier, fmt) per position: topics dealt with
    practice.interleave; the allowed tiers in equal parts, easiest first for
    'ladder' and interleaved for 'mixed'; grid-ins at SPR_AT scaled to the
    length when formats is 'both'."""
    rank = {"easy": 0, "medium": 1, "hard": 2}
    tiers = sorted(dict.fromkeys(tiers), key=rank.__getitem__)
    per, extra = divmod(count, len(tiers))
    counts = {t: per + (i < extra) for i, t in enumerate(tiers)}
    steps = [t for t in tiers for _ in range(counts[t])] if order == "ladder" else practice.interleave(counts)
    share, left = divmod(count, len(topics))
    dealt = practice.interleave({t: share + (i < left) for i, t in enumerate(topics)})
    spr_at = {max(1, round(k * count / MODULE_SIZE)) for k in SPR_AT}
    fmt = {"both": lambda i: "spr" if i in spr_at else "mcq",
           "mcq": lambda i: "mcq", "spr": lambda i: "spr"}[formats]
    return [(topic, tier, fmt(i)) for i, (topic, tier) in enumerate(zip(dealt, steps), 1)]


def custom(topics: list[str], count: int, tiers: list[str], order: str, formats: str,
           b: practice.Builder, queue: list | None = None, exposure: dict[str, int] | None = None,
           offers=None) -> list[dict]:
    """A custom test under test rules, ids c01..

    From skills, each slot takes the least exposed template of its topic that
    makes its tier and format, the candidates weighed by practice.penalty.
    With a queue (the templates of open mistakes or of a sitting's misses, or
    (template, norm) pairs for a trap test) each entry draws that template on a
    fresh seed; for a norm, `offers(card, norm)` walks up to 40 seeds for one
    whose options offer it.
    """
    chosen: list[practice.Card] = []
    used: dict[str, int] = {}
    if queue is not None:
        for entry in queue:
            template, norm = entry if isinstance(entry, (list, tuple)) else (entry, None)
            card = None
            for _ in range(40 if norm and offers else 1):
                card = b.draw(template, practice.topic_of(template))
                if card is None or not norm or not offers or offers(card, norm):
                    break
                b.keep(card)
                card = None
            if card is not None:
                b.keep(card)
                chosen.append(card)
        return stored(chosen, "c", sep="")
    can = abilities()
    by_topic = practice.catalogue()["by_topic"]
    rank = order_key("exposure" if exposure is not None else "shuffle", used, b.learner, exposure)
    for topic, tier, fmt in custom_slots(topics, count, tiers, order, formats):
        names = [t for t in by_topic.get(topic, []) if t not in b.spent]
        pool = [t for t in names if (tier, fmt) in can.get(t, ())] or \
               [t for t in names if any(k[0] == tier for k in can.get(t, ()))]
        cards = []
        for t in sorted(pool, key=rank):
            card = draw_matching(b, t, tier, "spr" if fmt == "spr" else None)
            if card:
                cards.append(card)
            if len(cards) >= practice.CANDIDATES:
                break
        if not cards:
            continue
        best = min(cards, key=lambda c: practice.penalty(c, chosen, used))
        b.keep(best)
        chosen.append(best)
        used[best.key] = used.get(best.key, 0) + 1
    return stored(chosen, "c", sep="")
