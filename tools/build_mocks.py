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

# The blueprint and the filler live in server/blueprint.py, so a section built
# for one student at sitting time and the shelf built here are the same shape.
from server.blueprint import (DOMAIN_SPLIT, MODULE_SIZE, SPR_AT, TIERS,   # noqa: E402
                              fill as _fill, slots, survey)

CAN: dict[str, set[tuple[str, str]]] = {}


def fill(form_slots, by_domain, b: practice.Builder, log) -> list[practice.Card]:
    return _fill(form_slots, by_domain, b, CAN, log)


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
