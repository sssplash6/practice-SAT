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

# About a quarter of the real section is student-produced response. The bank is
# 19% grid-in overall and thin on easy ones, so this is a target rather than a
# guarantee, and the shortfall is reported rather than papered over.
SPR_TARGET = 6         # a quarter of 22, rounded up
SPR_PULL = 70          # pulls toward a grid-in while short, and away once met


def slots(form: str, module: int) -> list[tuple[str, str]]:
    """The (domain, difficulty) pairs this module has to fill.

    Both totals have to come out exactly: the domain counts and the difficulty
    mix. Dealing the tiers in blocks gets the totals right but leaves whole
    domains at one difficulty -- all the hard ones land in whichever domains
    still had room. So the tiers are laid out interleaved first, using the same
    spreader the practice sets use, and then handed round the domains in turn.
    Every domain then carries a share of the module's difficulty rather than a
    corner of it.
    """
    domains = DOMAIN_SPLIT[module]
    order = practice.interleave(dict(TIERS[form]))       # e m h e m h e m ...
    names = list(domains)
    room = dict(domains)
    out: list[tuple[str, str]] = []

    cyc = 0
    for tier in order:
        for _ in range(len(names)):
            d = names[cyc % len(names)]
            cyc += 1
            if room[d]:
                room[d] -= 1
                out.append((d, tier))
                break
    assert len(out) == MODULE_SIZE, f"{form} module {module}: {len(out)} slots"
    assert not any(room.values()), f"{form} module {module}: {room} unfilled"
    return out


def fill(form_slots, by_domain, b: practice.Builder, log) -> list[practice.Card]:
    """One module. Same spread scoring as practice, plus a grid-in quota."""
    chosen: list[practice.Card] = []
    used: dict[str, int] = {}
    spr = 0

    for want_domain, want_tier in form_slots:
        pool = [t for t in by_domain[want_domain] if t not in b.spent]
        ranked = sorted(pool, key=lambda t: (used.get(t, 0), t))

        cards = []
        for key in ranked:
            card = b.draw(key, practice.topic_of(key))
            if card is None:
                continue
            if card.feats["difficulty"] != want_tier:
                continue                       # this template is not at that tier now
            cards.append(card)
            if len(cards) >= practice.CANDIDATES:
                break

        if not cards:                          # nothing at that tier; take the domain
            for key in ranked:
                card = b.draw(key, practice.topic_of(key))
                if card:
                    cards.append(card)
                    break
        if not cards:
            log(f"    ran out in {want_domain} / {want_tier}")
            continue

        def cost(c):
            p = practice.penalty(c, chosen, used)
            if c.item.fmt == "spr":
                # reach for a grid-in while short of the quarter, and lean off
                # them once it is met, or a module drifts to 40% grid-in
                p += -SPR_PULL if spr < SPR_TARGET else SPR_PULL
            return p

        best = min(cards, key=cost)
        b.keep(best)
        chosen.append(best)
        used[best.key] = used.get(best.key, 0) + 1
        if best.item.fmt == "spr":
            spr += 1

    # a module runs easiest to hardest, as the real one does
    rank = {"easy": 0, "medium": 1, "hard": 2}
    chosen.sort(key=lambda c: rank[c.feats["difficulty"]])
    return chosen


def main() -> int:
    cat = practice.catalogue()
    topics = cat["topics"]
    by_domain: dict[str, list[str]] = {}
    for t, names in cat["by_topic"].items():
        by_domain.setdefault(topics[t].domain, []).extend(names)
    for v in by_domain.values():
        v.sort()

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
            spr = sum(1 for q in qs if q["type"] == "spr")
            tiers = {t: sum(1 for q in qs if q["difficulty"] == t)
                     for t in ("easy", "medium", "hard")}
            print(f"  {form:14} {len(qs):2d} questions  "
                  f"e{tiers['easy']}/m{tiers['medium']}/h{tiers['hard']}  "
                  f"{spr} grid-in  {len({q['topic'] for q in qs})} topics")
        mocks.append({"id": mock_id, "box": BOX, **forms})

    check(mocks)
    OUT.write_text(json.dumps({
        "built": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "blueprint": {"module_size": MODULE_SIZE, "domains": DOMAIN_SPLIT, "tiers": TIERS,
                      "spr_target": SPR_TARGET},
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
