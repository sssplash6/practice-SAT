"""Study-design claims for the easy and medium multiple-choice pools.

These are sentence-valued questions, as every official item in this topic is.
"""

from __future__ import annotations

import random

from ....exact import E
from ....item import Item, Mis, assemble_text


def study_conclusion(rng: random.Random, seed: int) -> Item:
    tier = "easy" if seed % 2 == 0 else "medium"
    selected = rng.choice((True, False))
    assigned = not selected if tier == "easy" else selected
    n = rng.choice((80, 120, 160))
    options = {
        (True, True): "The program may have caused the difference, and the result may apply to the school's students.",
        (False, True): "The program may have caused the difference, but school-wide generalization is not supported.",
        (True, False): "The association may apply to the school's students, but causation is not supported.",
        (False, False): "Neither causation nor school-wide generalization is supported.",
    }
    selected_text = (f"selected {n} students at random from the school" if selected
                     else f"recruited {n} students who volunteered")
    assigned_text = ("randomly assigned them to two tutoring programs" if assigned
                     else "let each student choose one of two tutoring programs")
    key_text = options[selected, assigned]
    wrongs = [Mis("confused random selection with random assignment", text)
              for state, text in options.items() if state != (selected, assigned)]
    choices, reasons, letter = assemble_text(key_text, wrongs, rng)
    return Item(
        "esc.study_conclusion_supply", "study design", tier, seed,
        f"Researchers {selected_text} and {assigned_text}. Students in one "
        "program later earned higher scores. Which conclusion is best supported?",
        "mcq", E(0), letter,
        "Random selection supports generalizing an association to the sampled "
        "population; random assignment supports a causal conclusion. "
        f"Here, {key_text}",
        choices, reasons,
        params={"kind": "esc_supply_conclusion", "selected": selected,
                "assigned": assigned, "texts": choices},
    )


def sampling_method(rng: random.Random, seed: int) -> Item:
    tier = "easy" if seed % 2 == 0 else "medium"
    population = rng.choice(("students at a school", "residents of a town"))
    if tier == "easy":
        options = [
            ("random_population", f"Randomly select people from all {population}."),
            ("voluntary", f"Invite all {population} to answer an optional online poll."),
            ("convenience", "Survey the first 100 people to enter a nearby cafe."),
            ("subgroup", f"Survey 100 people from one group within the {population}."),
        ]
    else:
        options = [
            ("stratified_population", f"Randomly select from each part of the {population} in proportion to its size."),
            ("unequal_strata", f"Randomly select the same number from each part of the {population}, despite different sizes."),
            ("voluntary", f"Let any of the {population} reply to a public invitation."),
            ("subgroup", f"Randomly select only from one part of the {population}."),
        ]
    key_text = options[0][1]
    choices, reasons, letter = assemble_text(
        key_text,
        [Mis({"voluntary": "self-selected respondents can differ from the population",
              "convenience": "a cafe sample does not cover the target population",
              "subgroup": "one subgroup cannot represent the whole population",
              "unequal_strata": "equal subgroup counts distort groups of different sizes"}[tag], text)
         for tag, text in options[1:]], rng)
    return Item(
        "esc.sampling_method_supply", "representative samples", tier, seed,
        f"A researcher wants to estimate the opinion of all {population}. "
        "Which method is least likely to produce selection bias?",
        "mcq", E(0), letter,
        "Every member of the target population needs a route into the sample, "
        f"and groups must keep their population weights. {key_text}",
        choices, reasons,
        params={"kind": "esc_supply_method", "methods": [tag for tag, _ in options],
                "texts": choices},
    )
