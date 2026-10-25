"""What a topic is, and how one is found.

A topic is a self-contained plug-in: its own templates, its own independently
written solvers, and its own list of the official items it was learned from.
Nothing outside `topics/<slug>/` has to change to add one, which is what lets
topics be built in parallel without two authors editing the same file.

The official answers are never typed into a topic. They are read from
`material/keys/<slug>.json`, which is extracted from the College Board PDF's
own text layer, and from `material/transcripts/<slug>.json`, the transcription
of the question images. A template that gets the mathematics wrong therefore
cannot be made to pass by restating the answer -- the answer is not the
author's to state.
"""

from __future__ import annotations

import importlib
import json
import os
import pkgutil
from dataclasses import dataclass, field
from typing import Callable

__all__ = ["Topic", "Source", "S", "TOPICS", "load_topics", "key_file", "transcript",
           "MATERIAL"]

MATERIAL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "material")


@dataclass
class Source:
    """One official item, encoded as the parameters that reproduce it.

    `build` takes a Random and returns the Item. It carries no answer: the
    answer comes from the material, and the check asks whether the engine
    lands on it.
    """
    id: str
    build: Callable
    note: str = ""


def S(id: str, build: Callable, note: str = "") -> Source:
    return Source(id, build, note)


@dataclass
class Topic:
    slug: str                       # matches material/keys/<slug>.json
    name: str                       # "Right Triangles and Trigonometry"
    domain: str                     # the College Board domain it sits in
    templates: dict[str, Callable] = field(default_factory=dict)
    audits: dict[str, Callable] = field(default_factory=dict)
    sources: list[Source] = field(default_factory=list)
    excluded: dict[str, str] = field(default_factory=dict)   # source id -> why

    def template_names(self) -> list[str]:
        return list(self.templates)


TOPICS: dict[str, Topic] = {}
BROKEN: dict[str, Exception] = {}


def load_topics() -> dict[str, Topic]:
    """Import every module under `satbank.topics` and collect its TOPIC.

    A topic that will not import is recorded in BROKEN and skipped rather than
    taken down the engine with it: topics are written side by side, and one
    author's half-finished file must not break everybody else's check run.
    `check` reports it as a failure of that topic alone.
    """
    if TOPICS or BROKEN:
        return TOPICS
    from . import topics as pkg
    for mod in pkgutil.iter_modules(pkg.__path__):
        try:
            m = importlib.import_module(f"{pkg.__name__}.{mod.name}")
        except Exception as exc:                                    # noqa: BLE001
            BROKEN[mod.name] = exc
            continue
        # one TOPIC per module, or a TOPICS list (the Reading and Writing bank, satbank/topics/rw.py)
        for topic in getattr(m, "TOPICS", None) or [getattr(m, "TOPIC", None)]:
            if topic is None:
                continue
            if topic.slug in TOPICS:
                raise RuntimeError(f"two topics claim the slug {topic.slug!r}")
            TOPICS[topic.slug] = topic
    return TOPICS


def key_file(slug: str) -> dict:
    """The official answer key, straight from the PDF's text layer."""
    path = os.path.join(MATERIAL, "keys", f"{slug}.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"no answer key for {slug!r}: run tools/extract_material.py")
    with open(path) as fh:
        return json.load(fh)


def transcript(slug: str) -> dict[str, dict]:
    """The transcribed question images, keyed by item id. {} when absent."""
    path = os.path.join(MATERIAL, "transcripts", f"{slug}.json")
    if not os.path.exists(path):
        return {}
    with open(path) as fh:
        data = json.load(fh)
    return {it["id"]: it for it in data["items"]}
