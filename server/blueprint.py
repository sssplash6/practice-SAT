"""The shape of a digital SAT Math section, and filling a module to it.

Moved out of tools/build_mocks.py so a section can be built for one student at
the moment they sit it, against their own history, rather than only once onto
a fixed shelf. The tool still builds the shelf, from these same functions.

The numbers are the published ones where College Board publishes them and
stated choices where it does not; tools/build_mocks.py carries the reasoning
for each, and the README the sources.
"""

from __future__ import annotations

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
}

# College Board's own answer keys put grid-ins at 6, 7, 13, 14, 20, 21 and 27 of
# 27; scaled to 22 positions that is this.
SPR_AT = (6, 7, 13, 14, 21, 22)
SPR_PULL = 400         # a slot that wants a grid-in really wants one


def slots(form: str, module: int) -> list[tuple[str, str, str | None]]:
    """The (domain, difficulty, format) each position carries, in final order.

    Difficulty is sorted -- a module runs easiest to hardest -- and the domains
    are spread across the positions by the practice spreader, so the small ones
    are not all used up early.
    """
    rank = {"easy": 0, "medium": 1, "hard": 2}
    ladder = sorted([t for t, n in TIERS[form].items() for _ in range(n)],
                    key=lambda t: rank[t])
    spread = practice.interleave(dict(DOMAIN_SPLIT[module]))
    out = [(dom, tier, "spr" if i + 1 in SPR_AT else None)
           for i, (dom, tier) in enumerate(zip(spread, ladder))]
    assert len(out) == MODULE_SIZE, f"{form} module {module}: {len(out)} slots"
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


def abilities() -> dict[str, set[tuple[str, str]]]:
    """The survey of every template, made once per process."""
    if not _CAN:
        cat = practice.catalogue()
        _CAN.update(survey(sorted(n for v in cat["by_topic"].values() for n in v)))
    return _CAN


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


def fill(form_slots, domains: dict[str, list[str]], b: practice.Builder,
         can: dict[str, set[tuple[str, str]]], log=print) -> list[practice.Card]:
    """One module: the practice spread scoring, plus the format each slot wants."""
    chosen: list[practice.Card] = []
    used: dict[str, int] = {}
    missed = 0

    for want_domain, want_tier, want_fmt in form_slots:
        wants = (want_tier, want_fmt or "mcq")
        pool = [t for t in domains[want_domain] if t not in b.spent and wants in can.get(t, ())]
        if not pool:                           # no template makes it; widen to the tier
            pool = [t for t in domains[want_domain]
                    if t not in b.spent and any(k[0] == want_tier for k in can.get(t, ()))]
        ranked = sorted(pool, key=lambda t: (used.get(t, 0), t))

        cards = []
        for key in ranked:
            card = draw_matching(b, key, want_tier, want_fmt)
            if card:
                cards.append(card)
            if len(cards) >= practice.CANDIDATES:
                break

        if not cards:                          # take anything in the domain
            for key in sorted(domains[want_domain], key=lambda t: (used.get(t, 0), t)):
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


def module(form: str, b: practice.Builder, log=lambda *_: None) -> list[dict]:
    """A module built now, as stored questions, ids prefixed by the form."""
    num = 1 if form == "module1" else 2
    cards = fill(slots(form, num), by_domain(), b, abilities(), log)
    prefix = {"module1": "m1", "module2_lower": "m2l", "module2_upper": "m2u"}[form]
    out = []
    for i, c in enumerate(cards, 1):
        q = practice.to_question(c, i)
        q["id"] = f"{prefix}q{i:02d}"
        out.append(q)
    return out
