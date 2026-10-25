"""U6's ordered misconception families over SAT Math reason norms.

No bank item is edited or tagged. The same normalized reason can be used by
Practice, Review, Plan and Compete through this small catalogue.
"""

from __future__ import annotations

import functools
import pathlib
import re
import sys

if __name__ == "__main__" and not __package__:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
    from server import blueprint, progress
else:
    from . import blueprint, progress


FAMILIES = (
    {"id": "formula", "name": "Mixed up two formulas", "tell": "Write the formula before the numbers.",
     "regex": r"\b(formula|radius|diameter|circumference|perimeter|surface area|volume|"
              r"triangle area|circle area|base area|lateral (?:area|surface)|"
              r"degrees? (?:instead|as)|radians? (?:instead|as)|πr|pi r)\b"},
    {"id": "percent", "name": "Percent handling", "tell": "Percent of what? Name the base first.",
     "regex": r"\b(percent(?:age)?|discount|markup|tax|tip|original price|"
              r"percent change|percent increase|percent decrease)\b"},
    {"id": "units", "name": "Units and conversions", "tell": "Circle the unit the answer wants.",
     "regex": r"\b(units?|conver(?:t|sion)|feet|foot|inches?|yards?|miles?|meters?|"
              r"centimeters?|kilometers?|grams?|kilograms?|liters?|gallons?|"
              r"hours?|minutes?|dollars?|cents?|square units?|cubic units?)\b|"
              r"\b(?:per|in|to|from) seconds?\b"},
    {"id": "roots", "name": "Squares and roots",
     "tell": "Did you square, or take the root? Check both ways.",
     "regex": r"\b(squar(?:e|ed|ing)?|square root|root|radical|exponent|power|cube root|cubed)\b"},
    {"id": "inverted", "name": "Inverted a ratio, rate or slope",
     "tell": "Say it as 'per': which quantity is on top?",
     "regex": r"\b(invert(?:ed)?|reciprocal|numerator|denominator|ratio|slope|"
              r"per [a-z]+ (?:instead|rather)|rate (?:of|as)|swapped? (?:the )?(?:rise|run))\b"},
    {"id": "sign", "name": "Flipped a sign or direction",
     "tell": "Check the sign against a rough estimate.",
     "regex": r"\b(sign|negative|positive|minus|subtrac(?:t|ted|tion)|opposite|"
              r"direction|flipped|reversed|greater instead of less|less instead of greater)\b"},
    {"id": "whole_part", "name": "Gave the whole instead of the part",
     "tell": "Is it the part they asked for, or what's left?",
     "regex": r"\b(whole (?:amount|group|total|shape|figure|instead)|"
              r"part (?:asked|instead|of the)|remaining|remainder|the rest|"
              r"what(?:'s| is) left|total instead|entire (?:amount|group|shape)|"
              r"complement|left over|all .* instead of)\b"},
    {"id": "early_late", "name": "Stopped a step early or went too far",
     "tell": "Reread the last line: is this the final quantity?",
     "regex": r"\b(stopp?ed|one step|too early|too late|went .* step|"
              r"forgot to (?:add|divide|multiply|subtract|finish)|"
              r"did not (?:add|divide|multiply|subtract)|before the final|"
              r"intermediate|only the first|first step)\b"},
    {"id": "read", "name": "Read the wrong row, axis or point",
     "tell": "Point at the row or axis before you read it.",
     "regex": r"\b(row|column|axis|axes|graph|table|chart|plot|"
              r"x.coordinate|y.coordinate|frequency|read .* instead of|"
              r"read (?:the )?(?:wrong|other)|wrong (?:point|bar|line))\b"},
    {"id": "different", "name": "Answered a different quantity",
     "tell": "Before you pick, reread what exactly is asked.",
     "regex": r"\b((?:found|gave|reported|answered) .* instead of|"
              r"(?:answer|quantity|value) (?:asked|requested|wanted)|"
              r"answered a different quantity|the wrong (?:value|number|quantity))\b"},
    {"id": "slip", "name": "Arithmetic slip", "tell": "Estimate first; does the answer fit?",
     "regex": r"\b(arithmetic|calculation|miscalculat|miscomputed|slip|"
              r"copied .* incorrectly|added .* incorrectly|multiplied .* incorrectly|"
              r"divided .* incorrectly|off by #)\b"},
)

# Exact normalized reasons are applied before the ordered expressions when a
# bank phrase happens to contain another family's keyword.
OVERRIDES: dict[str, str] = {
    "left pi out of the calculation": "formula",
}
_COMPILED = tuple((row, re.compile(row["regex"], re.IGNORECASE)) for row in FAMILIES)


def families(subject: str = "math") -> list[dict]:
    """Public ordered descriptors; future R&W families can be added by subject."""
    return [{**row, "subject": "math"} for row in FAMILIES] if subject == "math" else []


def family_of(reason: str) -> dict | None:
    normalized = progress.norm(reason)
    override = OVERRIDES.get(normalized)
    if override:
        return next((row for row in families() if row["id"] == override), None)
    return next((dict(row, subject="math") for row, pattern in _COMPILED
                 if pattern.search(normalized)), None)


def family(reason: str) -> dict | None:
    """Compatibility name used by P6 and V7."""
    return family_of(reason)


@functools.lru_cache(maxsize=1)
def norm_index() -> dict[str, tuple[str, ...]]:
    return {template: tuple(sorted({progress.norm(reason) for reason in data["reasons"].values()
                                    if reason}))
            for template, data in blueprint.kinds().items()}


def members(family_id: str) -> list[dict]:
    """Every surveyed template/norm match, with its topic for cross-skill drills."""
    if family_id not in {row["id"] for row in FAMILIES}:
        raise ValueError(f"unknown habit family: {family_id}")
    kinds = blueprint.kinds()
    return [{"template": template, "topic": kinds[template]["topic"], "norm": norm}
            for template, norms in norm_index().items() for norm in norms
            if (found := family_of(norm)) and found["id"] == family_id]


def of_learner(learner: str) -> list[dict]:
    """Today's "By habit" view (api_today): the learner's habit families over the last 28 days, the
    same list Me shows. Math only: R&W misses go unnamed, so no R&W miss has a family."""
    from . import api_profile
    return api_profile._habits(learner)


def regex_for(family_id: str) -> str:
    return next(row["regex"] for row in FAMILIES if row["id"] == family_id)


def _check() -> None:
    assert len(FAMILIES) == 11 and len({row["id"] for row in FAMILIES}) == 11
    examples = {"used the diameter instead of the radius": "formula",
                "used the wrong percent base": "percent",
                "converted feet to inches": "units",
                "squared instead of taking the root": "roots",
                "inverted the ratio": "inverted",
                "flipped the sign": "sign",
                "gave the whole instead of the part": "whole_part",
                "stopped one step early": "early_late",
                "read the wrong row": "read",
                "answered a different quantity than asked": "different",
                "near-miss arithmetic slip": "slip"}
    assert all(family_of(reason)["id"] == fid for reason, fid in examples.items())
    all_norms = {norm for norms in norm_index().values() for norm in norms}
    tagged = {norm for norm in all_norms if family_of(norm)}
    for row in FAMILIES:
        rows = members(row["id"])
        topics = {match["topic"] for match in rows}
        reasons = sorted({match["norm"] for match in rows})
        print(f"{row['id']}: {len(reasons)} reasons, {len(rows)} template matches,"
              f" {len(topics)} topics; e.g. {', '.join(reasons[:5])}")
        assert len(topics) >= 3, (row["id"], topics)
    print(f"untagged: {len(all_norms - tagged)} of {len(all_norms)}"
          f" ({len(all_norms - tagged) / len(all_norms):.1%});"
          f" e.g. {', '.join(sorted(all_norms - tagged)[:10])}")


if __name__ == "__main__":
    _check()
