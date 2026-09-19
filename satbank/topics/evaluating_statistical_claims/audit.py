"""An independent solver for every template in this topic.

Each solver is handed the study -- who was sampled, from where, how, and what
was reported -- together with the four sentences that were printed, and works
out for itself which of the four the study supports. It shares no helper with
the generators: the populations are parsed out of the printed options here by
taking each sentence apart word by word, the containment is walked here, and
the statistics of a single sample are written here a second time.

The one thing it takes from `world.py` is the catalogue's containment facts --
that a school lies in a county, that a history professor is a professor. Those
are facts about the world the page assumes, of the same kind as the points of
a scatterplot; which population a study *licenses* is worked out below and is
never read from anywhere.
"""

from __future__ import annotations

import re

from ...audit import AuditError
from .world import SCOPES, TABLES

__all__ = ["AUDITS"]


# ------------------------------------------------------- reading a population

def _worlds(name: str):
    return SCOPES.get(name) or TABLES[name]


def _up(dim, value: str) -> list[str]:
    """A value and every value that contains it, narrowest first."""
    chain, v = [], value
    while v is not None:
        chain.append(v)
        v = dim.values[v].parent
    return chain


def _inside(sc, a: dict, b: dict) -> bool:
    """Is every member of population `a` a member of population `b`?"""
    a, b = _close(sc, a), _close(sc, b)
    return all(b[d.name] in _up(d, a[d.name]) for d in sc.dims)


def _close(sc, spec: dict) -> dict:
    """Drop a qualifier the place already forces: at a middle school, "students"
    and "middle school students" are the same people."""
    out = dict(spec)
    for _ in range(len(sc.dims) + 1):
        was = dict(out)
        for d in sc.dims:
            for dim2, val2 in sc.implies.get((d.name, out[d.name]), {}).items():
                if out[dim2] in _up(sc.dim(dim2), val2):
                    out[dim2] = val2
        if was == out:
            break
    return out


def _population(sc, text: str, extra: dict):
    """The population a printed option names, or None if it names a group of
    measured units rather than a population.

    Every fragment the sentence is made of has to be accounted for. A renderer
    that dropped "fourth-grade" leaves a sentence that parses to a different
    population; one that printed a word from nowhere leaves a remainder, and
    fails here.
    """
    rest = text
    if not rest.startswith(sc.article):
        return None
    rest = rest[len(sc.article):]
    if sc.unit not in rest:
        return None
    rest = rest.replace(sc.unit, "", 1)
    spec = {}
    for d in sc.dims:
        found = [v for v, val in d.values.items()
                 if val.frag and val.frag.format(**extra) in rest]
        if len(found) > 1:
            raise AuditError(f"{text!r} names two values of {d.name!r}")
        if found:
            spec[d.name] = found[0]
            rest = rest.replace(d.values[found[0]].frag.format(**extra), "", 1)
        else:
            spec[d.name] = next(v for v, val in d.values.items()
                                if val.parent is None)
    return spec if not rest.strip() else None


def _count(text: str) -> int:
    m = re.search(r"\d[\d,]*", text)
    if m is None:
        raise AuditError(f"{text!r} names neither a population nor a group of units")
    return int(m.group(0).replace(",", ""))


def _scope(p) -> str:
    """The largest population the study's results reach.

    Random selection reaches the frame; any other way of choosing the units
    reaches only the units themselves. Among the printed options the answer is
    the one that contains every other option the study reaches -- and there
    has to be exactly one of those.
    """
    sc = _worlds(p["scope"])
    extra = p.get("extra", {})
    frame = dict(p["frame"])
    at_random = p["method"] == "random"

    read = []
    for text in p["texts"]:
        spec = _population(sc, text, extra)
        read.append(dict(text=text, spec=spec,
                         size=None if spec else _count(text)))
    measured = [r for r in read if r["spec"] is None]
    if measured and max(r["size"] for r in measured) != p["n"]:
        raise AuditError("no printed group of measured units is the whole sample")

    def reaches(a, b) -> bool:              # is a inside b?
        if a is b:
            return True
        if b["spec"] is None:
            return a["spec"] is None and a["size"] <= b["size"]
        if a["spec"] is None:
            return _inside(sc, frame, b["spec"])
        return _inside(sc, a["spec"], b["spec"])

    live = [r for r in read
            if r["spec"] is None or (at_random and _inside(sc, r["spec"], frame))]
    top = [r for r in live if all(reaches(o, r) for o in live)]
    if len(top) != 1:
        raise AuditError(f"{len(top)} of the printed populations are largest")
    return top[0]["text"]


# --------------------------------------------- what one sample establishes

OF_ALL = re.compile(r"^Of all\b")
ANOTHER = re.compile(r"^If another\b")
DIFFERENT = re.compile(r"^If [\d,]+ .* from a different\b")
SURVEYED = re.compile(r"^Of the ([\d,]+) \w+ surveyed, ([\d,.]+)(%| percent)?(?!\d)")
HALF = re.compile(r"^More than half of the ([\d,]+) \w+ surveyed\b")
ROMAN = ("I", "II", "III")


def _true_statement(line: str, n: int, p) -> bool:
    """Is this numbered statement true of a survey of `n` that reported `p`%?

    A sample estimates a population; it does not fix it. So a statement about
    the population, about what a second sample would report, or about another
    population at all, does not have to be true whatever the sample said. A
    statement about the sample itself is arithmetic.
    """
    if OF_ALL.match(line) or ANOTHER.match(line) or DIFFERENT.match(line):
        return False
    m = HALF.match(line)
    if m:
        return float(p) > 50
    m = SURVEYED.match(line)
    if m:
        size = int(m.group(1).replace(",", ""))
        value = float(m.group(2).replace(",", ""))
        if m.group(3):                      # a percentage: it restates the report
            return value == float(p)
        return value * 100 == float(p) * size
    raise AuditError(f"no rule for the statement {line!r}")


def _label(sub: tuple, total: int) -> str:
    names = [ROMAN[i] for i in sub]
    if not names:
        return "Neither" if total == 2 else "None"
    if len(names) == total and total == 3:
        return "I, II, and III"
    tail = "" if total == 2 else " only"
    if len(names) == 1:
        return f"{names[0]} only"
    return " and ".join(names) + tail


def _must_be_true(p) -> str:
    lines = p["lines"]
    truth = tuple(i for i, line in enumerate(lines)
                  if _true_statement(line, p["n"], p["p"]))
    want = _label(truth, len(lines))
    if want not in p["texts"]:
        raise AuditError(f"the printed options do not offer {want!r}")
    return want


# ------------------------------------------------------ the drawn inference

MOST = re.compile(r"^Most (?P<pop>.+?) will (?P<verb>.+)\.$")
ATLEAST = re.compile(r"^At least [\d.]+% of (?P<pop>.+?) will (?P<verb>.+)\.$")
EVERY = re.compile(r"^All (?P<pop>.+?) will (?P<verb>.+)\.$")


def _inference(p) -> str:
    """Only a claim about the sampled group, only in the direction the
    majority answered, and only as strong as "most"."""
    said, pct = int(p["said"]), float(p["p"])
    major = p["verbs"][said] if pct > 50 else p["verbs"][1 - said]
    hits = []
    for text in p["texts"]:
        m = MOST.match(text)
        if not (m or ATLEAST.match(text) or EVERY.match(text)):
            raise AuditError(f"{text!r} is not an inference this reader knows")
        if m and m.group("pop") == p["frame"] and m.group("verb") == major:
            hits.append(text)
    if len(hits) != 1:
        raise AuditError(f"{len(hits)} of the four inferences are licensed")
    return hits[0]


# -------------------------------------------------- what the method supports

METHOD_SAYS = (
    ("not_flawed", re.compile(r"^The sampling method is not flawed and is likely to "
                              r"produce an unbiased estimate of ")),
    ("flawed", re.compile(r"^The sampling method is flawed and may produce a biased "
                          r"estimate of ")),
    ("biased", re.compile(r"^The survey sample is biased because it is not "
                          r"representative of ")),
    ("not_random", re.compile(r"^Those who responded to the .+ were not a random "
                              r"sample of ")),
    ("random_remedy", re.compile(r"^The survey sample should have been selected at "
                                 r"random from ")),
)


def _sample_quality(p) -> str:
    """Whether a sample can stand for a population is settled by how it was
    obtained. Only a statement about that can be the answer, and which one it
    is follows from a single fact: was it a random sample of the population?"""
    sound = p["method"] == "random"
    hits = []
    for text in p["statements"]:
        kind = next((k for k, rx in METHOD_SAYS if rx.match(text)), None)
        if kind is None:
            continue                        # says nothing about how units were chosen
        if (kind == "not_flawed") == sound:
            hits.append(text)
    if len(hits) != 1:
        raise AuditError(f"{len(hits)} of the four statements hold of this method")
    if hits[0] not in p["texts"]:
        raise AuditError("the statement that holds was not printed as an option")
    return hits[0]


# ------------------------------------------------- association against cause

CAUSE = re.compile(r"^The (?P<t>.+) causes an increase in (?P<o>.+) for "
                   r"(?P<pop>.+)\.$")
ASSOC = re.compile(r"^There is an association between the (?P<t>.+) and an "
                   r"increase in (?P<o>.+) for (?P<pop>.+)\.$")


def _conclusion(p) -> str:
    """Selection decides who the conclusion is about; assignment decides
    whether it may be a causal one. The answer is the strongest claim the
    design supports, about the widest group it supports it for."""
    reach = 1 if p["selection"] == "random" else 0
    level = {p["sample"]: 0, p["frame"]: 1, p["wider"]: 2}
    read = []
    for text in p["texts"]:
        c, a = CAUSE.match(text), ASSOC.match(text)
        if not (c or a):
            raise AuditError(f"{text!r} is neither a causal nor an associative claim")
        pop = (c or a).group("pop")
        if pop not in level:
            raise AuditError(f"{text!r} is about a group the study never names")
        read.append((1 if c else 0, level[pop], text))
    live = [r for r in read if r[1] <= reach and (p["assignment"] or r[0] == 0)]
    top = [r for r in live if all(r[0] >= o[0] and r[1] >= o[1] for o in live)]
    if len(top) != 1:
        raise AuditError(f"{len(top)} conclusions are maximal")
    return top[0][2]


AUDITS = {
    "esc.generalize": _scope,
    "esc.generalize_table": _scope,
    "esc.must_be_true": _must_be_true,
    "esc.inference": _inference,
    "esc.sample_quality": _sample_quality,
    "esc.conclusion": _conclusion,
}
