"""What every template in this topic shares: how a question is framed, and how
four expressions are chosen to sit under it.

Options here are expressions, not values, so there is no ascending order to
hide the key in: `assemble_text` shuffles, and the work is entirely in the
list of wrong expressions handed to it. Each one is built in coefficient
space, checked against the key so that a "distractor" can never be the right
answer written differently, and only then printed.
"""

from __future__ import annotations

import random

from ....item import Item, ItemError, Mis, assemble_text
from ..render import MINUS, Q, sent

__all__ = ["Q", "MINUS", "sent", "Item", "ItemError", "Mis", "Slip",
           "choose", "frame_stem", "FRAMES", "SUM_FRAMES", "text_item"]


class Slip:
    """One wrong route, kept as the value it produces rather than as text.

    Comparing in coefficient space is what stops a distractor from being the
    key in a different jacket -- printing first and comparing strings would
    let `5x² − 5x` and `−5x + 5x²` both onto the page.
    """

    __slots__ = ("reason", "value")

    def __init__(self, reason: str, value):
        self.reason = reason
        self.value = value


def choose(key, show, slips: list[Slip], rng: random.Random):
    """Three distinct wrong expressions, then the four shuffled.

    `key` and each slip's value are comparable objects (tuples of
    coefficients, usually); `show` turns one into the string that is printed.
    """
    seen, picked = {key}, []
    for s in slips:
        if s.value is None or s.value in seen:
            continue
        seen.add(s.value)
        picked.append(Mis(s.reason, show(s.value)))
        if len(picked) == 3:
            break
    if len(picked) < 3:
        raise ItemError("could not build three distinct wrong expressions")
    shown = [show(key)] + [m.value for m in picked]
    if len(set(shown)) != 4:
        raise ItemError("two of the options print the same way")
    return assemble_text(show(key), picked, rng)


# ------------------------------------------------------------- the frames
#
# The source wraps an expression in a question in six ways, and half of them
# put the expression on a line of its own above the sentence.

FRAMES = {
    "given": lambda e: f"{e}\nWhich of the following is equivalent to the given expression?",
    "above": lambda e: f"{e}\nWhich of the following is equivalent to the expression above?",
    "above_expressions": lambda e: f"{e}\nWhich of the following expressions is equivalent "
                                   f"to the expression above?",
    "which": lambda e: f"Which expression is equivalent to {e}?",
    "which_sp": lambda e: f"Which expression is equivalent to {e} ?",
    "which_of": lambda e: f"Which of the following is equivalent to {e} ?",
    "which_of_short": lambda e: f"Which of the following is equivalent to {e}?",
    "which_of_expressions": lambda e: f"Which of the following expressions is equivalent "
                                      f"to {e} ?",
    "which_expressions": lambda e: f"Which of the following expressions is equivalent "
                                   f"to {e}?",
    "the_expression": lambda e: f"Which of the following is equivalent to the expression "
                                f"{e} ?",
    "equivalent_form": lambda e: f"Which of the following is an equivalent form of {e} ?",
}
FRAME_NAMES = list(FRAMES)

SUM_FRAMES = {
    "sum_of": lambda a, b: f"Which of the following expressions is equivalent to the sum "
                           f"of {a} and {b} ?",
    "sum_of_short": lambda a, b: f"Which of the following is equivalent to the sum of "
                                 f"{a} and {b}?",
}


def frame_stem(frame: str, expr: str) -> str:
    return sent(FRAMES[frame](expr))


def text_item(template: str, skill: str, difficulty: str, seed: int, stem: str,
              rationale: str, key_repr, show, slips: list[Slip],
              rng: random.Random, params: dict) -> Item:
    """An item whose four options are expressions."""
    from ....exact import E
    choices, reasons, letter = choose(key_repr, show, slips, rng)
    params = dict(params, options=list(choices))
    return Item(template, skill, difficulty, seed, sent(stem), "mcq", E(1), letter,
                sent(rationale), choices, reasons, list(choices), params=params)
