"""Build the mock sections -- the cassettes in box one.

A mock here is a full DIGITAL SAT MATH SECTION, built to the shape College
Board publishes for it:

  two modules of 22 questions, 35 minutes each, 44 in total;
  the second module chosen from how the first went, harder or easier;
  a section score of 200 to 800.

The domain counts come from the published weights -- Algebra about 35%,
Advanced Math about 35%, Problem-Solving and Data Analysis about 15%,
Geometry and Trigonometry about 15% -- which over 44 questions is 15, 15, 7
and 7. Each module carries roughly half of each domain, so a student who only
reaches module 1 has still met all four.

Difficulty is where the adaptive part lives. College Board says both second
modules contain easy, medium and hard items and differ in the proportions
rather than in kind, but publishes no proportions, so the three mixes below
are a stated choice: module 1 spans the range evenly, and the two second
modules lean the same distance in opposite directions.

What this cannot copy: the real test carries two unscored pretest items per
module and scores the other twenty by item response theory. There is nothing
to pretest here and no calibration to score with, so all 22 count.

    PYTHONPATH=. python3 tools/build_mocks.py
"""

from __future__ import annotations

import datetime as dt
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from server import practice                                   # noqa: E402

OUT = pathlib.Path(__file__).resolve().parent.parent / "server" / "mocks.json"

BOX = 1
CASSETTES = 7
MODULE_SIZE = 22

# Domain counts per module. They add to 15 / 15 / 7 / 7 over the two, which is
# the published 35 / 35 / 15 / 15 of a 44-question section.
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

# Where the grid-ins go. This is not a guess. College Board's own answer keys
# for the linear practice forms put the student-produced responses at positions
# 6, 7, 13, 14, 20, 21 and 27 of 27 -- across seven published tests, fourteen
# modules, without a single exception. They sit in small interleaved clusters
# with one at the very end, not banked up at the finish the way homemade
# sections usually put them. Scaled from 27 positions to 22 that is
#
#     5 MC | 2 SPR | 5 MC | 2 SPR | 6 MC | 2 SPR
#
# which is 6 of 22, or 27%, against the published section figure of about 25%.
SPR_AT = (6, 7, 13, 14, 21, 22)
SPR_PULL = 400         # a slot that wants a grid-in really wants one


def slots(form: str, module: int) -> list[tuple[str, str, str | None]]:
    """The (domain, difficulty, format) each position carries, in final order.

    Three things have to hold at once and they pull against each other: the
    domain counts come out exactly; the module reads easiest to hardest across
    all 22 positions, which is College Board's stated rule for Math and the one
    homemade sections break most often; and the grid-ins land where their own
    answer keys put them.

    Difficulty is therefore simply sorted -- it is the ordering key and nothing
    competes with it. The domains are spread across the 22 positions by the
    same spreader the practice sets use, rather than dealt round-robin, which
    ran the small domains out early and left every hard position to Algebra and
    Advanced Math.
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
    choice, and most of them only make one or the other. Without this the
    builder offered whichever templates were least used and hoped one of them
    happened to be a grid-in, which left half the grid-in slots empty.
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


def draw_matching(b: practice.Builder, key: str, tier: str, fmt: str | None,
                  tries: int = 10) -> practice.Card | None:
    """Walk this template's seeds for a card of the right tier and format.

    A card that is not what the slot needs is kept anyway, which marks it used
    and advances the template to its next seed. The pool is seventeen thousand
    items against the four hundred this build needs, so spending a few is
    cheaper than settling for the wrong shape.
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


def fill(form_slots, by_domain, b: practice.Builder, log) -> list[practice.Card]:
    """One module. Same spread scoring as practice, plus the format each slot wants."""
    chosen: list[practice.Card] = []
    used: dict[str, int] = {}
    missed = 0

    for want_domain, want_tier, want_fmt in form_slots:
        # only templates that can make this shape, least used first
        wants = (want_tier, want_fmt or "mcq")
        pool = [t for t in by_domain[want_domain]
                if t not in b.spent and wants in CAN[t]]
        if not pool:                           # no template makes it; widen to the tier
            pool = [t for t in by_domain[want_domain]
                    if t not in b.spent
                    and any(k[0] == want_tier for k in CAN[t])]
        ranked = sorted(pool, key=lambda t: (used.get(t, 0), t))

        cards = []
        for key in ranked:
            card = draw_matching(b, key, want_tier, want_fmt)
            if card:
                cards.append(card)
            if len(cards) >= practice.CANDIDATES:
                break

        if not cards:                          # take anything in the domain
            for key in sorted(by_domain[want_domain], key=lambda t: (used.get(t, 0), t)):
                card = b.draw(key, practice.topic_of(key))
                if card:
                    cards.append(card)
                    break
        if not cards:
            log(f"    ran out in {want_domain} / {want_tier}")
            continue

        def cost(c):
            # a slot either wants a grid-in or wants to stay multiple choice
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


CAN: dict[str, set[tuple[str, str]]] = {}


def main() -> int:
    cat = practice.catalogue()
    topics = cat["topics"]
    by_domain: dict[str, list[str]] = {}
    for t, names in cat["by_topic"].items():
        by_domain.setdefault(topics[t].domain, []).extend(names)
    for v in by_domain.values():
        v.sort()

    print("surveying what each template can make ...")
    CAN.update(survey(sorted(cat["by_topic"] and
                             [n for v in by_domain.values() for n in v])))
    for dom, names in by_domain.items():
        spr = sum(1 for n in names if any(k[1] == "spr" for k in CAN[n]))
        print(f"  {dom:36} {spr:3d} of {len(names):3d} templates make a grid-in")

    # one builder across every mock, so no question appears in two of them
    b = practice.Builder("mockshelf", set(), set())
    mocks = []

    for n in range(1, CASSETTES + 1):
        mock_id = f"{BOX}.{n}"
        print(f"mock {mock_id}")
        forms = {}
        for form, module in (("module1", 1), ("module2_lower", 2), ("module2_upper", 2)):
            cards = fill(slots(form, module), by_domain, b, print)
            qs = []
            for i, c in enumerate(cards, 1):
                q = practice.to_question(c, i)
                q["id"] = f"{form[:2]}{'' if form == 'module1' else form[8:10]}q{i:02d}"
                qs.append(q)
            forms[form] = qs
            at = [i for i, q in enumerate(qs, 1) if q["type"] == "spr"]
            tiers = {t: sum(1 for q in qs if q["difficulty"] == t)
                     for t in ("easy", "medium", "hard")}
            print(f"  {form:14} e{tiers['easy']}/m{tiers['medium']}/h{tiers['hard']}  "
                  f"grid-in at {at}  {len({q['topic'] for q in qs})} topics")
        mocks.append({"id": mock_id, "box": BOX, **forms})

    check(mocks)
    OUT.write_text(json.dumps({
        "built": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "blueprint": {"module_size": MODULE_SIZE, "domains": DOMAIN_SPLIT,
                      "tiers": TIERS, "spr_at": list(SPR_AT)},
        "mocks": mocks,
    }, ensure_ascii=False, indent=1))
    print(f"\nwrote {OUT} ({OUT.stat().st_size // 1024} KB)")
    return 0


def check(mocks: list[dict]) -> None:
    """Refuse to ship a shelf that repeats a question or misses the blueprint."""
    stems: dict[str, str] = {}
    for m in mocks:
        for form in ("module1", "module2_lower", "module2_upper"):
            qs = m[form]
            assert len(qs) == MODULE_SIZE, f"{m['id']} {form}: {len(qs)}"
            module = 1 if form == "module1" else 2
            got = {d: sum(1 for q in qs if q["domain"] == d) for d in DOMAIN_SPLIT[module]}
            assert got == DOMAIN_SPLIT[module], f"{m['id']} {form} domains: {got}"
            rank = {"easy": 0, "medium": 1, "hard": 2}
            order = [rank[q["difficulty"]] for q in qs]
            assert order == sorted(order), f"{m['id']} {form} is out of order"
            at = tuple(i for i, q in enumerate(qs, 1) if q["type"] == "spr")
            assert at == SPR_AT, f"{m['id']} {form}: grid-in at {at}, wanted {SPR_AT}"
            ids = [q["id"] for q in qs]
            assert len(set(ids)) == len(ids), f"{m['id']} {form} has a duplicate id"
            for q in qs:
                where = f"{m['id']} {form}"
                assert q["stem"] not in stems, \
                    f"{where} repeats a stem from {stems[q['stem']]}"
                stems[q["stem"]] = where
                if q["type"] == "mcq":
                    assert len(q["choices"]) == 4 and q["answer"] in "ABCD", q["id"]
                else:
                    assert q["answer"], q["id"]
    print(f"\nchecked: {len(stems)} questions across {len(mocks)} mocks, all distinct")


if __name__ == "__main__":
    sys.exit(main())
