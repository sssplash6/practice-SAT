"""Decide all four printed options from the printed page, and check only one holds.

`satbank check` asks whether the key is right. It never asks whether a
*distractor* is also right -- and in a topic whose options are sentences, that
is the whole risk: an item that offers both "the sampling method is flawed"
and "the survey sample is biased" under a convenience sample has two correct
answers and passes all seven checks.

It is also the only check that can catch the failure this topic was rejected
for twice. A template that has been *told* the answer and an audit that has
been told the same answer agree with each other forever. This script is not
told: it reads the stem to find out how the units were chosen and what was
reported, reads the four options to find out what each of them claims, and
applies the rules itself.

    PYTHONPATH=. python3 satbank/topics/evaluating_statistical_claims/option_check.py
    PYTHONPATH=. python3 .../option_check.py --draws 800 --template esc.generalize
    PYTHONPATH=. python3 .../option_check.py --selftest   # show the checks can fail

What it takes from the engine: `generate` and `ItemError`, nothing else -- no
template, no solver, no `audit.py`. What it takes from the topic: the study
catalogues, as **vocabulary and containment facts** only (that a school lies
in a county, that this scenario's population is called "all city residents").
Those cannot be recovered from the page by any reader, in the same way that
Two-Variable Data's checker cannot recover a scatterplot's units from its
pixels. Which option a study licenses is decided here, from the page, every
time -- and `--selftest` proves that each of those decisions can fail.
"""

from __future__ import annotations

import argparse
import re
import sys

from satbank.item import ItemError
from satbank.registry import generate
from satbank.topics.evaluating_statistical_claims.families.claims import INFER
from satbank.topics.evaluating_statistical_claims.families.conclude import TRIALS
from satbank.topics.evaluating_statistical_claims.families.method import STUDIES
from satbank.topics.evaluating_statistical_claims.world import SCOPES, TABLES

ROMAN = ("I", "II", "III")


class Unreadable(Exception):
    """The printed item is not something this reader understands.

    Raised rather than swallowed: a reader that quietly stops reading reports
    no defects, which is indistinguishable from an item with none.
    """


class Defect(Exception):
    """The printed item has no single defensible answer, or the wrong one."""


def keyed(item) -> str:
    return item.choices["ABCD".index(item.answer)]


def _one(hits: list, what: str, item) -> str:
    if len(hits) != 1:
        raise Defect(f"{len(hits)} of the four options {what}: {hits}")
    return hits[0]


def _is_key(hit: str, item, why: str) -> None:
    if hit != keyed(item):
        raise Defect(f"the option that {why} is {hit!r}, but the key is "
                     f"{keyed(item)!r}")


def numbers(text: str) -> list[int]:
    return [int(t.replace(",", "")) for t in re.findall(r"\d[\d,]*", text)]


# ------------------------------------------------------------- the scope pair
#
# Read off the page: how the units were chosen, the population they were
# chosen from, and what population each option names. Then the rule --
# random selection reaches the frame, anything else reaches only the units
# measured -- and the answer is the largest option the study reaches.

RANDOM_WORDS = re.compile(r"\bat random\b|\brandomly selected\b|\brandom sample\b")
NOT_RANDOM_WORDS = re.compile(r"\bwas formed\b|\bvolunteered\b")


def _selection(stem: str) -> bool:
    """True when the page says the units were selected at random."""
    yes, no = bool(RANDOM_WORDS.search(stem)), bool(NOT_RANDOM_WORDS.search(stem))
    if yes == no:
        raise Unreadable(f"the stem says neither or both of random and not: {stem!r}")
    return yes


def _rx(frag: str) -> re.Pattern:
    """A fragment as a pattern, with its numeric slot left open.

    The catalogue writes "that scored {hi} or more points"; the page prints a
    number there, and the reader must match what the page printed rather than
    fill the slot in from the parameters.
    """
    return re.compile(re.escape(frag).replace(r"\{hi\}", r"\d+")
                      .replace(r"\{cut\}", r"\d+"))


def _place_in(sc, stem: str):
    """Which place the stem says the units were drawn from, and where it says it.

    Every place the catalogue knows is looked for; a phrase that sits inside a
    longer one that also matched is not a separate match, and of what is left
    the last one is the one the sampling sentence names.
    """
    dim = sc.dim("place")
    found = []
    for value, val in dim.values.items():
        for m in re.finditer(re.escape(val.stem), stem):
            found.append((m.start(), m.end(), value))
    keep = [f for f in found
            if not any(g is not f and g[0] <= f[0] and f[1] <= g[1] for g in found)]
    if not keep:
        raise Unreadable("the stem names no place this context knows")
    keep.sort()
    return keep[-1][2], keep[-1][0]


def _frame(sc, stem: str) -> dict:
    """The population the stem says the sample was drawn from."""
    place, at = _place_in(sc, stem)
    start = stem.rfind(". ", 0, at) + 1
    window = stem[start:at]
    spec = {"place": place}
    for d in sc.dims:
        if d.slot == "place":
            continue
        hit = [v for v, val in d.values.items()
               if val.frag and _rx(val.frag).search(window)]
        if len(hit) > 1:
            raise Unreadable(f"the stem names two values of {d.name!r}")
        spec[d.name] = hit[0] if hit else next(v for v, val in d.values.items()
                                               if val.parent is None)
    return spec


def _up(dim, value):
    out, v = [], value
    while v is not None:
        out.append(v)
        v = dim.values[v].parent
    return out


def _shut(sc, spec: dict) -> dict:
    out = dict(spec)
    for _ in range(len(sc.dims) + 1):
        was = dict(out)
        for d in sc.dims:
            for other, val in sc.implies.get((d.name, out[d.name]), {}).items():
                if out[other] in _up(sc.dim(other), val):
                    out[other] = val
        if was == out:
            break
    return out


def _in(sc, a: dict, b: dict) -> bool:
    a, b = _shut(sc, a), _shut(sc, b)
    return all(b[d.name] in _up(d, a[d.name]) for d in sc.dims)


def _option_population(sc, text: str):
    """The population an option names, or None when it names measured units.

    The sentence is taken apart: the article, the unit noun and one fragment
    per dimension have to account for every word of it. An option that has
    lost a qualifier parses to a different population; one that gained a word
    leaves a remainder and is refused.
    """
    if not text.startswith(sc.article):
        return None
    rest = text[len(sc.article):]
    if sc.unit not in rest:
        return None
    rest = rest.replace(sc.unit, "", 1)
    spec = {}
    for d in sc.dims:
        hit = [v for v, val in d.values.items()
               if val.frag and _rx(val.frag).search(rest)]
        if len(hit) > 1:
            raise Unreadable(f"{text!r} names two values of {d.name!r}")
        if hit:
            spec[d.name] = hit[0]
            rest = _rx(d.values[hit[0]].frag).sub("", rest, count=1)
        else:
            spec[d.name] = next(v for v, val in d.values.items()
                                if val.parent is None)
    return spec if not rest.strip() else None


def _check_table(item) -> None:
    """The table has to add up, and to report the part of the sample the stem
    says it reports."""
    rows = item.table
    body = [[int(c.replace(",", "")) for c in r[1:]] for r in rows[1:]]
    for r in body:
        if r[-1] != sum(r[:-1]):
            raise Defect(f"a table row does not add up: {r}")
    for j in range(len(body[0])):
        if body[-1][j] != sum(r[j] for r in body[:-1]):
            raise Defect(f"table column {j} does not add up")
    total = body[-1][-1]
    said = re.search(r"information for the ([\d,]+) ", item.stem)
    if said is None or int(said.group(1).replace(",", "")) != total:
        raise Defect("the stem and the table disagree about how many units the "
                     "table reports")


def read_scope(item) -> None:
    # which study the page describes, found by its own wording -- the item's
    # parameters are not consulted anywhere in this reader
    _, sc = _context({**SCOPES, **TABLES}, item.stem, lambda d: d.draw)
    at_random = _selection(item.stem)
    frame = _frame(sc, item.stem)
    if item.table:
        _check_table(item)

    _, at = _place_in(sc, item.stem)
    start = item.stem.rfind(". ", 0, at) + 1
    told = numbers(item.stem[start:at])
    read = []
    for text in item.choices:
        spec = _option_population(sc, text)
        size = None
        if spec is None:
            got = numbers(text)
            if not got:
                raise Unreadable(f"{text!r} names neither a population nor a group")
            size = got[0]
        read.append(dict(text=text, spec=spec, size=size))

    same = [_shut(sc, r["spec"]) for r in read if r["spec"]]
    if len(same) != len({tuple(sorted(x.items())) for x in same}):
        raise Defect(f"two options name the same population: {item.choices}")
    measured = [r for r in read if r["spec"] is None]
    if measured and told and max(r["size"] for r in measured) != told[0]:
        raise Defect(f"the largest group of measured units is "
                     f"{max(r['size'] for r in measured)}, but the stem sampled "
                     f"{told[0]}")

    def reaches(a, b) -> bool:
        if a is b:
            return True
        if b["spec"] is None:
            return a["spec"] is None and a["size"] <= b["size"]
        if a["spec"] is None:
            return _in(sc, frame, b["spec"])
        return _in(sc, a["spec"], b["spec"])

    live = [r for r in read
            if r["spec"] is None or (at_random and _in(sc, r["spec"], frame))]
    top = [r["text"] for r in live if all(reaches(o, r) for o in live)]
    _is_key(_one(top, "is the largest population the study reaches", item),
            item, "is the largest population the study reaches")


# ------------------------------------------------- what one sample establishes

OF_ALL = re.compile(r"^Of all\b")
IF_ANOTHER = re.compile(r"^If another\b")
IF_OTHER = re.compile(r"^If [\d,]+ .*\bfrom a different\b")
OF_THE = re.compile(r"^Of the ([\d,]+) \w+ surveyed, ([\d,]+)(%| percent)?[ ,]")
OVER_HALF = re.compile(r"^More than half of the ([\d,]+) \w+ surveyed\b")


def _subset(label: str) -> tuple:
    if label in ("Neither", "None"):
        return ()
    return tuple(sorted(ROMAN.index(r) for r in re.findall(r"\bI+\b", label)))


def read_must_be_true(item) -> None:
    head, *lines = item.stem.split("\n")
    if not lines:
        raise Unreadable("no numbered statements in the stem")
    # not \b after the sign: a per-cent sign is not a word character, so a
    # word boundary after it never matches and the reader would stop reading
    said = re.search(r"(\d[\d,]*)(%| percent)(?!\w)", head)
    if said is None:
        raise Unreadable("the stem reports no percentage")
    pct = int(said.group(1).replace(",", ""))
    sample = numbers(head)
    if not sample:
        raise Unreadable("the stem reports no sample size")
    n = sample[0]

    truth = []
    for i, raw in enumerate(lines):
        line = re.sub(r"^(?:[IV]+|\d+)\.\s*", "", raw)
        if OF_ALL.match(line) or IF_ANOTHER.match(line) or IF_OTHER.match(line):
            holds = False               # a sample estimates; it does not fix
        elif OVER_HALF.match(line):
            holds = pct > 50
        else:
            m = OF_THE.match(line)
            if m is None:
                raise Unreadable(f"no rule for the statement {line!r}")
            if int(m.group(1).replace(",", "")) != n:
                raise Defect(f"statement {ROMAN[i]} reports a sample of "
                             f"{m.group(1)}, but {n} were surveyed")
            value = int(m.group(2).replace(",", ""))
            holds = value == pct if m.group(3) else value * 100 == pct * n
        if holds:
            truth.append(i)
    want = tuple(truth)

    seen = [_subset(c) for c in item.choices]
    if len(set(seen)) != 4:
        raise Defect(f"two options name the same set of statements: {item.choices}")
    hits = [c for c, s in zip(item.choices, seen) if s == want]
    _is_key(_one(hits, "name the statements that must be true", item),
            item, "names exactly the statements that must be true")


# ------------------------------------------------------- the drawn inference

MOST = re.compile(r"^Most (?P<pop>.+?) will (?P<verb>.+)\.$")
ATLEAST = re.compile(r"^At least (?P<p>[\d.]+)% of (?P<pop>.+?) will (?P<verb>.+)\.$")
EVERY = re.compile(r"^All (?P<pop>.+?) will (?P<verb>.+)\.$")


def _fits(text: str, stem: str) -> bool:
    """Does the printed stem carry every slot-free chunk of this wording, in order?

    A stem that drifted from the wording it was built out of matches nothing,
    so the reader refuses it rather than guessing which study it describes.
    """
    chunks = [c.strip() for c in re.split(r"\{\w+\}", text) if len(c.strip()) > 20]
    at = 0
    for c in chunks:
        at = stem.find(c, at)
        if at < 0:
            return False
    return bool(chunks)


def _context(book: dict, stem: str, get=lambda d: d["draw"]):
    """Which catalogue entry the printed stem came from."""
    out = []
    for name, d in book.items():
        texts = get(d)
        texts = texts if isinstance(texts, dict) else {None: texts}
        if any(_fits(t, stem) for t in texts.values()):
            out.append((name, d))
    if len(out) != 1:
        raise Unreadable(f"{len(out)} catalogue entries match this stem")
    return out[0]


def read_inference(item) -> None:
    _, d = _context(INFER, item.stem)
    said = re.search(r"Of those surveyed, (\d+)% said they (.+?)\.", item.stem)
    if said is None:
        raise Unreadable("the stem reports no result")
    pct, phrase = int(said.group(1)), said.group(2)
    if phrase not in d["said"]:
        raise Unreadable(f"{phrase!r} is not a response this study offers")
    reported = d["verb"][d["said"].index(phrase)]
    other = d["verb"][1 - d["said"].index(phrase)]
    major = reported if pct > 50 else other

    hits = []
    for text in item.choices:
        m = MOST.match(text)
        if not (m or ATLEAST.match(text) or EVERY.match(text)):
            raise Unreadable(f"{text!r} is not an inference this reader knows")
        if m and m.group("pop") == d["frame"] and m.group("verb") == major:
            hits.append(text)
    _is_key(_one(hits, "the study licenses", item), item, "the study licenses")


# -------------------------------------------------- what the method supports

SAYS = (
    ("not_flawed", re.compile(r"^The sampling method is not flawed\b")),
    ("flawed", re.compile(r"^The sampling method is flawed\b")),
    ("biased", re.compile(r"^The survey sample is biased\b")),
    ("not_random", re.compile(r"^Those who responded to the \w+ were not a random "
                              r"sample\b")),
    ("random_remedy", re.compile(r"^The survey sample should have been selected at "
                                 r"random\b")),
)
NOT_METHOD = (
    ("pop_value", re.compile(r"^(It shows that the majority of|The mean |The level )")),
    ("too_small", re.compile(r"^A determination about .* the sample size is too "
                             r"small\.$")),
    ("remedy_sub", re.compile(r"^The survey sample should have (included more|"
                              r"consisted entirely of)\b")),
    ("pct_sum", re.compile(r"^The percentages do not add up to 100%")),
    ("not_fifty", re.compile(r"^There were not 50% ")),
    ("more_time", re.compile(r"^The show did not allow viewers enough time\b")),
)


def read_sample_quality(item) -> None:
    name, d = _context(STUDIES, item.stem)
    pop = d["pop_all"]
    # the rule, read off the page: the estimate is unbiased exactly when the
    # page says the units were selected at random from the population asked about
    m = re.search(r"at random from ([^.]*)", item.stem)
    sound = bool(m) and m.group(1).startswith(pop)
    explains = "best explains why the results are unlikely to represent" in item.stem

    hits = []
    for text in item.choices:
        kind = next((k for k, rx in SAYS if rx.match(text)), None)
        if kind is not None:
            if (kind == "not_flawed") == sound:
                hits.append(text)
            continue
        other = next((k for k, rx in NOT_METHOD if rx.match(text)), None)
        if other is None:
            raise Unreadable(f"no rule for the statement {text!r}")
        # true of the responses, and silent about who was asked -- so it can
        # only be printed where the question asks for an explanation
        if other == "not_fifty" and not explains:
            raise Defect(f"{text!r} is true as printed, and the question does not "
                         f"ask for an explanation, so the item has two answers")
    _is_key(_one(hits, "hold of this sampling method", item),
            item, "holds of this sampling method")


# ------------------------------------------------- association against cause

CAUSE = re.compile(r"^The (.+) causes an increase in (.+) for (?P<pop>.+)\.$")
ASSOC = re.compile(r"^There is an association between the (.+) and an increase "
                   r"in (.+) for (?P<pop>.+)\.$")
ASSIGNED = re.compile(r"\brandomly assigned them to two groups\b")
CHOSEN = re.compile(r"\bselected [\d,]+ \w+ at random from\b")


def read_conclusion(item) -> None:
    _, d = _context(TRIALS, item.stem)
    assigned = bool(ASSIGNED.search(item.stem))
    at_random = bool(CHOSEN.search(item.stem))
    reach = 1 if at_random else 0
    n = numbers(item.stem)[0]
    level = {d["sample"].format(n=n): 0, d["frame"]: 1, d["wider"]: 2}

    read = []
    for text in item.choices:
        c, a = CAUSE.match(text), ASSOC.match(text)
        if not (c or a):
            raise Unreadable(f"{text!r} is neither a causal nor an associative claim")
        pop = (c or a).group("pop")
        if pop not in level:
            raise Unreadable(f"{text!r} is about a group the stem never names")
        read.append((1 if c else 0, level[pop], text))
    live = [r for r in read if r[1] <= reach and (assigned or r[0] == 0)]
    top = [r[2] for r in live if all(r[0] >= o[0] and r[1] >= o[1] for o in live)]
    _is_key(_one(top, "is the strongest conclusion the design supports", item),
            item, "is the strongest conclusion the design supports")


READERS = {
    "esc.generalize": (read_scope, "the largest population the study reaches"),
    "esc.generalize_table": (read_scope, "the same, with the table read back"),
    "esc.must_be_true": (read_must_be_true, "which statements a sample establishes"),
    "esc.inference": (read_inference, "the inference the frame and majority allow"),
    "esc.sample_quality": (read_sample_quality, "what the sampling method supports"),
    "esc.conclusion": (read_conclusion, "association or cause, and for whom"),
}


# ----------------------------------------------------------------- the driver

def sweep(name: str, draws: int, verbose: bool = False) -> tuple[int, list[str]]:
    reader = READERS[name][0]
    made, bad = 0, []
    for seed in range(draws):
        try:
            item = generate(name, seed)
        except ItemError:
            continue
        made += 1
        try:
            reader(item)
        except (Defect, Unreadable) as exc:
            bad.append(f"seed {seed}: {type(exc).__name__}: {exc}\n"
                       + item.pretty(show_reasons=False))
    return made, bad


def sources() -> tuple[int, list[str]]:
    """The eleven official items, read the same way.

    The sweep above covers what a free draw can reach, and one configuration
    it cannot: `check._prose` reads a bare "None" as an unrendered
    placeholder, so a free three-statement draw never lands on the empty
    answer, and item 2.3 -- whose three statements are all false -- would
    otherwise go unread.
    """
    import random as _r
    from satbank.topic import load_topics
    topic = load_topics()["evaluating_statistical_claims"]
    bad = []
    for src in topic.sources:
        item = src.build(_r.Random(0))
        try:
            READERS[item.template][0](item)
        except (Defect, Unreadable) as exc:
            bad.append(f"{src.id}: {type(exc).__name__}: {exc}")
    return len(topic.sources), bad


def _prove(label: str, build) -> bool:
    """Run a reader over a deliberately broken item and report what it caught."""
    try:
        build()
    except (Defect, Unreadable) as exc:
        print(f"  ok   {label}\n         caught: {exc}")
        return True
    print(f"  FAIL {label}\n         the reader passed an item it should refuse")
    return False


def selftest() -> int:
    """Eight injected faults. A check nobody has seen fail is worth nothing."""
    ok = True
    SCHOOL = dict(ctx="announcements", n=40, k=32, method="random",
                  wrongs=["sample", "any,school", "fourth,county"])

    def keyed_to(item, pick):
        item.answer = "ABCD"[next(i for i, c in enumerate(item.choices) if pick(c))]
        return item

    def swap(item, pick, text):
        item.choices = list(item.choices)
        item.choices[next(i for i, c in enumerate(item.choices) if pick(c))] = text
        return item

    # 1 -- the error this topic exists to test, keyed: past the sampling frame
    ok &= _prove("a scope item keyed to the population past the frame",
                 lambda: read_scope(keyed_to(generate("esc.generalize", 0, **SCHOOL),
                                             lambda c: "county" in c)))

    # 2 -- the stem's sampling method rewritten, the key left where it was
    def convenience_stem():
        item = generate("esc.generalize", 0, **SCHOOL)
        item.stem = item.stem.replace(
            "was selected at random from a certain school",
            "was formed from the students who arrived earliest at a certain school")
        read_scope(item)
    ok &= _prove("a scope item whose stem no longer samples at random",
                 convenience_stem)

    # 3 -- an option loses the qualifier that made it a different population
    ok &= _prove("a scope option that lost its qualifier in the rendering",
                 lambda: read_scope(swap(generate("esc.generalize", 0, **SCHOOL),
                                         lambda c: c == "All fourth-grade students "
                                                        "at the school",
                                         "All students at the school")))

    # 4 -- a headcount in a numbered statement that no longer matches the report
    def bad_count():
        item = generate("esc.must_be_true", 0, ctx="concession", n=200, p=87,
                        stmts=["population_exact", "count_sample"])
        item.stem = item.stem.replace("174 said", "176 said")
        read_must_be_true(item)
    ok &= _prove("a must-be-true item whose printed count stopped matching",
                 bad_count)

    # 5 -- two statements about the method that are both true
    ok &= _prove("a method item with two true verdicts on the page",
                 lambda: read_sample_quality(
                     swap(generate("esc.sample_quality", 0, ctx="playground", n=20,
                                   mean=24),
                          lambda c: c.startswith("A determination"),
                          "The survey sample is biased because it is not "
                          "representative of all the households in the community.")))

    # 6 -- a statement that is true of the responses and silent about the
    # method, on a page that asks which statement must be true
    ok &= _prove("a second true statement smuggled into a must-be-true item",
                 lambda: read_sample_quality(
                     swap(generate("esc.sample_quality", 0, ctx="playground", n=20,
                                   mean=24),
                          lambda c: c.startswith("A determination"),
                          "There were not 50% \u201cYes\u201d responses and 50% "
                          "\u201cNo\u201d responses.")))

    # 7 -- an observational study, keyed to the causal claim: the page never
    # says anything was randomly assigned
    ok &= _prove("a causal conclusion keyed where nothing was randomly assigned",
                 lambda: read_conclusion(keyed_to(
                     generate("esc.conclusion", 0, ctx="sleep_app", n=80, weeks=6,
                              selection="random", assignment=False,
                              wrongs=["cause_frame", "cause_wider",
                                      "association_wider"]),
                     lambda c: c == "The sleep app causes an increase in "
                                    "nightly sleep for the members of the health "
                                    "center.")))

    # 9 -- a table that no longer reports what the stem says it reports
    def bent_table():
        item = generate("esc.generalize_table", 0, ctx="trivia", n=55, cut=3,
                        cut2=5, lo=6, mid=13, hi=14, counts=(6, 4, 4, 26),
                        wrongs=["high,tournament", "sample", "subsample"])
        item.table = [list(r) for r in item.table]
        item.table[1][1] = "9"
        read_scope(item)
    ok &= _prove("a two-way table whose cells stopped adding up", bent_table)

    # 8 -- an inference keyed to the option that fixes the population's value
    ok &= _prove("an inference keyed to the option that fixes the population value",
                 lambda: read_inference(keyed_to(
                     generate("esc.inference", 0, ctx="book_movie", n=200, p=95,
                              said=0, wrongs=["frame_strong", "read_strong",
                                              "opposite_group"]),
                     lambda c: c.startswith("At least 95% of people who like"))))
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--draws", type=int, default=400)
    ap.add_argument("--template", default=None)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()

    names = [args.template] if args.template else list(READERS)
    worst = 0
    for name in names:
        made, bad = sweep(name, args.draws)
        note = READERS[name][1]
        print(f"  {'ok ' if not bad else 'FAIL'}  {name:24} {made:5,} items, "
              f"{len(bad)} defects   ({note})")
        for b in bad[:3]:
            print("\n" + b + "\n")
        worst |= 1 if bad else 0
    if not args.template:
        made, bad = sources()
        print(f"  {'ok ' if not bad else 'FAIL'}  {'the official items':24} "
              f"{made:5,} items, {len(bad)} defects   (read the same way)")
        for b in bad:
            print("         - " + b)
        worst |= 1 if bad else 0
    return worst


if __name__ == "__main__":
    sys.exit(main())
