"""Building a mixed practice set that does not feel repetitive.

The bank can make thousands of distinct items per template, so never repeating
a question is the easy half. The hard half is that sixty questions drawn from
one subtopic can all be distinct and still feel like the same question sixty
times, because they share a shape: the same template with new numbers, the same
opening sentence, the same skill, the same answer form, four multiple choice in
a row, three hard in a row.

So this does not sample. It schedules. Every slot in the set is filled by
scoring a handful of candidates against what the student has just seen and
taking the least similar one. Sameness is counted on seven features at once --
template, skill, opening words, format, difficulty, whether there is a figure,
and the shape of the answer -- each weighted by how much it actually shows, and
faded by how far back it was. A template used earlier in the same set is also
penalised on its own, so the set spreads across every template a topic has
rather than leaning on whichever one happened to come up first.

The student's own history is the outer loop: seeds are walked from a per-learner
offset and never reissued, so a second sitting is not the first one again.
"""

from __future__ import annotations

import functools
import hashlib
import logging
import re
import zlib
from dataclasses import dataclass, field

from satbank.item import ItemError
from satbank.registry import generate, templates, topic_of
from satbank.topic import load_topics

log = logging.getLogger("satf.practice")

# How much each kind of sameness stings. These are not equal: two questions
# from the same template read as the same question, while two that happen to
# both be medium barely register.
WEIGHT = {
    "template": 100,
    "opening": 62,      # the same first words means the same story
    "skill": 38,
    "answer": 9,
    "difficulty": 8,
    "fmt": 6,
    "figure": 5,
}
WINDOW = 8              # how far back sameness is still felt
SPREAD = 46             # penalty per earlier use of the template in this set
CANDIDATES = 7          # templates tried per slot before picking
SEED_TRIES = 60         # how far to walk the seed space for an unused one

_CACHE: dict = {}


def catalogue() -> dict:
    """Template names by topic, plus each topic's domain. Warmed once."""
    if not _CACHE:
        names = templates()                      # also warms the lazy globals
        topics = load_topics()
        by_topic: dict[str, list[str]] = {}
        for n in names:
            by_topic.setdefault(topic_of(n), []).append(n)
        _CACHE["by_topic"] = {k: sorted(v) for k, v in by_topic.items()}
        _CACHE["topics"] = topics
    return _CACHE


# ------------------------------------------------------------------ features

_NUM = re.compile(r"[\d,.]+")
_WORD = re.compile(r"[a-z]+")


def opening(stem: str) -> str:
    """The first few words with numbers flattened, which is the story's face.

    "A photograph in the shape of a square has a side length of 76 units" and
    the same sentence with 91 units are the same question to read, so the
    digits are taken out before comparing.
    """
    flat = _NUM.sub("#", stem.lower())
    return " ".join(_WORD.findall(flat)[:6])


def answer_shape(item) -> str:
    """What the answer looks like, not what it is."""
    sample = item.choices[0] if item.choices else str(item.answer)
    s = sample.replace("−", "-").strip()
    if "√" in s or "sqrt" in s:
        return "radical"
    if "π" in s:
        return "pi"
    if "(" in s and "," in s:
        return "point"
    if "/" in s:
        return "fraction"
    if re.fullmatch(r"-?[\d,]+\.\d+", s):
        return "decimal"
    if re.fullmatch(r"-?[\d,]+", s):
        return "integer"
    return "expression"


@dataclass
class Card:
    """One generated item plus the features the scheduler compares on."""
    key: str
    seed: int
    item: object
    topic: str
    feats: dict = field(default_factory=dict)

    @classmethod
    def of(cls, key: str, seed: int, item, topic: str) -> "Card":
        return cls(key, seed, item, topic, {
            "template": key,
            "opening": opening(item.stem),
            "skill": item.skill,
            "answer": answer_shape(item),
            "difficulty": item.difficulty,
            "fmt": item.fmt,
            "figure": bool(item.figure),
        })


def stem_hash(stem: str) -> str:
    return hashlib.sha1(stem.encode("utf-8")).hexdigest()[:16]


# ------------------------------------------------------------------ ordering

def interleave(basket: dict[str, int]) -> list[str]:
    """Spread the topics out, so a set of three topics is not three blocks.

    Always take from whichever topic has most left, unless that is the one just
    taken and something else remains -- which is the standard way to lay out a
    multiset with no two neighbours alike, and it succeeds whenever no single
    topic holds more than half the slots.
    """
    left = {k: v for k, v in basket.items() if v > 0}
    order: list[str] = []
    prev = None
    while left:
        ranked = sorted(left, key=lambda k: (-left[k], k))
        pick = next((k for k in ranked if k != prev), ranked[0])
        order.append(pick)
        prev = pick
        left[pick] -= 1
        if not left[pick]:
            del left[pick]
    return order


# ------------------------------------------------------------------ scoring

def penalty(card: Card, recent: list[Card], used: dict[str, int]) -> float:
    """How much this card repeats what just went by. Lower is fresher."""
    score = SPREAD * used.get(card.key, 0)
    for back, earlier in enumerate(reversed(recent[-WINDOW:]), start=1):
        fade = (WINDOW - back + 1) / WINDOW
        for feature, w in WEIGHT.items():
            if card.feats[feature] == earlier.feats[feature]:
                score += w * fade
    return score


# ------------------------------------------------------------------ building

class Builder:
    """Holds the walk through the seed space for one learner."""

    def __init__(self, learner: str, seen: set[tuple[str, int]], seen_stems: set[str]):
        self.learner = learner
        self.seen = set(seen)
        self.seen_stems = set(seen_stems)
        self.cursor: dict[str, int] = {}
        # Seven templates are offered per slot and one is taken, so six items
        # were generated to be thrown away. Held here instead, they are the
        # candidates for the next slot, and each template generates about once
        # per pass over the pool rather than once per slot. On the topic where
        # fresh stems are hardest to find this took a set from 8.6s to 0.4s.
        self.stash: dict[str, Card] = {}
        # A template whose seeds all lead back to stems already used is spent
        # for this set. Without remembering that, it is retried at every later
        # slot and walks the whole seed budget again each time -- which was
        # three templates turning a sixty-question set into 18,000 generations.
        self.spent: set[str] = set()

    def _start(self, key: str) -> int:
        """Where this learner begins in this template's seed space."""
        return zlib.crc32(f"{self.learner}:{key}".encode()) % 100_000

    def draw(self, key: str, topic: str) -> Card | None:
        """Next item from this template the learner has not had. None if spent."""
        held = self.stash.get(key)
        if held is not None:
            return held
        if key in self.spent:
            return None
        card = self._make(key, topic)
        if card is None:
            self.spent.add(key)
        else:
            self.stash[key] = card
        return card

    def _make(self, key: str, topic: str) -> Card | None:
        base = self._start(key)
        k = self.cursor.get(key, 0)
        for _ in range(SEED_TRIES):
            seed = base + k
            k += 1
            if (key, seed) in self.seen:
                continue
            try:
                item = generate(key, seed)
            except ItemError:
                continue                      # some seeds have no valid item
            except Exception:
                log.exception("template %s failed at seed %d", key, seed)
                return None
            if stem_hash(item.stem) in self.seen_stems:
                continue                      # distinct seeds, same question
            self.cursor[key] = k
            return Card.of(key, seed, item, topic)
        self.cursor[key] = k
        return None

    def keep(self, card: Card) -> None:
        self.seen.add((card.key, card.seed))
        self.seen_stems.add(stem_hash(card.item.stem))
        self.stash.pop(card.key, None)


def build(basket: dict[str, int], learner: str,
          seen: set[tuple[str, int]] | None = None,
          seen_stems: set[str] | None = None) -> list[Card]:
    """The mixed set: one card per question the student asked for."""
    cat = catalogue()
    order = interleave(basket)
    b = Builder(learner, seen or set(), seen_stems or set())

    chosen: list[Card] = []
    used: dict[str, int] = {}
    last_at: dict[str, int] = {}

    for slot, topic in enumerate(order):
        pool = cat["by_topic"].get(topic, [])
        if not pool:
            log.warning("no templates for topic %s", topic)
            continue

        # try the templates this set has leaned on least, and among equals the
        # ones it has not touched for longest
        live = [t for t in pool if t not in b.spent]
        ranked = sorted(live or pool, key=lambda t: (used.get(t, 0), last_at.get(t, -1), t))

        cards = []
        for key in ranked[:CANDIDATES]:
            card = b.draw(key, topic)
            if card:
                cards.append(card)
        if not cards:                          # this topic is spent for them
            for key in ranked[CANDIDATES:]:
                card = b.draw(key, topic)
                if card:
                    cards.append(card)
                    break
        if not cards:
            log.warning("topic %s is exhausted for learner %s", topic, learner[:8])
            continue

        best = min(cards, key=lambda c: penalty(c, chosen, used))
        b.keep(best)
        chosen.append(best)
        used[best.key] = used.get(best.key, 0) + 1
        last_at[best.key] = slot

    return chosen


# ------------------------------------------------------------------ the wire

@functools.lru_cache(maxsize=4096)
def _skill(key: str, seed: int) -> str:
    return generate(key, seed).skill


def skill_of(q: dict) -> str | None:
    """What a question tests, in the bank's words. The stored diagnostic forms
    and shelf mocks predate the field, so for them it is read off the item."""
    if q.get("skill"):
        return q["skill"]
    return _skill(q["key"], q["seed"]) if "key" in q else None


def to_question(card: Card, n: int) -> dict:
    """The stored form: everything, key included. Stripped before it is served."""
    topics = catalogue()["topics"]
    it = card.item
    return {
        "id": f"p{n:03d}",
        "key": card.key,
        "seed": card.seed,
        "topic": card.topic,
        "topic_name": topics[card.topic].name,
        "domain": topics[card.topic].domain,
        "difficulty": it.difficulty,
        "skill": it.skill,
        "type": it.fmt,
        "stem": it.stem,
        "choices": list(it.choices),
        "latex": list(it.latex_choices),
        "figure": it.figure,
        "table": it.table,
        "answer": it.answer,
        "rationale": it.rationale,
        "reasons": list(it.reasons),
    }
