"""The quality gate. A topic ships when this is green, and not before.

Eight checks, in the order a failure is worth hearing about:

  coverage      every official item is either encoded or excluded with a reason
  transcript    the questions were transcribed, and each agrees with the key table
  acceptance    the engine reproduces every official answer it claims to
  audit         generated items survive an independently written solver, at volume
  structure     four distinct options, ascending, key never alone in its form
  prose         no placeholder, no doubled space, no sentence that is not one
  table         a printed table adds up: rows, columns, margins, the stem's total
  capacity      no template is a one-trick: each can make hundreds of items

The official answers come from `material/keys/<slug>.json`, extracted from the
PDF's own text layer, and the options from `material/transcripts/<slug>.json`.
An author cannot make a wrong template pass by writing down the answer.
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass

from .item import ItemError, norm_text, numeral
from .registry import generate
from .topic import BROKEN, Topic, key_file, load_topics, transcript

__all__ = ["check_topic", "check_all", "Result"]

MIN_CAPACITY = 200          # distinct items a template must be able to make
MAX_EXCLUDED = 0.15         # of a topic's official items
MIN_NAMED_DISTRACTORS = 0.80
MIN_OFFICIAL_OPTIONS = 0.40    # of the official DISTRACTORS, key excluded
FILLER = "near-miss arithmetic slip"


@dataclass
class Result:
    name: str
    ok: bool
    stat: str
    detail: list[str]


def _first(bad: list[str], n: int) -> list[str]:
    """The first `n` failures, and how many were not shown.

    A silently truncated list reads as the whole truth. One topic had a
    template failing at ordinary depth for weeks that never once appeared,
    because ten other messages filled every slot -- so the count is part of the
    report, not a nicety.
    """
    if len(bad) <= n:
        return bad
    return bad[:n] + [f"... and {len(bad) - n:,} more not shown"]


# "the table above", "the table shows" -- but not "the graph of the equation
# above", which points at a line of the stem, and not "each of the following
# tables", where the tables are the options themselves
TABLE_REF = re.compile(r"\btables?\b[^.]{0,20}\b(above|below|shown|gives|lists)\b"
                       r"|\b(above|below)\b[^.]{0,12}\btables?\b", re.I)

# a unit printed after the number: "8 cm²", "12 ft", "35 degrees"
UNIT = re.compile(r"(cm|mm|km|inches|inch|feet|foot|yards|yard|units|unit|"
                  r"degrees|degree|°|%|m|in|ft|yd)\d*$")


def norm(s: str) -> str:
    """The engine's one spelling for an answer -- see `item.norm_text`."""
    return norm_text(s)


def _same(a: str, b: str) -> bool:
    if norm(a) == norm(b):
        return True
    try:                                    # 0.5 is 1/2, 7.79 is 7.790
        return abs(_num(a) - _num(b)) <= 1e-9 * max(1.0, abs(_num(a)))
    except (ValueError, ZeroDivisionError, TypeError):
        return False


def _num(s: str) -> float:
    """The number an option carries, unit and all removed."""
    v = numeral(s)
    if v is None:
        raise ValueError(f"{s!r} is not a number")
    return v


def official_answers(rec: dict, key_answer: str) -> list[str]:
    """What the item is allowed to answer. A grid-in may accept several."""
    if rec.get("format") == "spr" or key_answer not in tuple("ABCD"):
        return [a.strip() for a in re.split(r",\s+", key_answer) if a.strip()]
    return [rec["options"]["ABCD".index(key_answer)]]


def engine_answer(item) -> str:
    return item.choices["ABCD".index(item.answer)] if item.fmt == "mcq" else item.answer


# ------------------------------------------------------------------ checks

def _coverage(topic: Topic, key: dict) -> Result:
    ids = [it["id"] for it in key["items"]]
    encoded = {s.id for s in topic.sources}
    excluded = set(topic.excluded)
    missing = [i for i in ids if i not in encoded and i not in excluded]
    both = sorted(encoded & excluded)
    unknown = sorted((encoded | excluded) - set(ids))
    thin = [f"{i}: reason is too thin to review ({topic.excluded[i]!r})"
            for i in sorted(excluded) if len(topic.excluded.get(i, "")) < 20]
    detail = []
    if missing:
        detail.append(f"{len(missing)} official items neither encoded nor excluded: "
                      + ", ".join(missing[:12]) + (" ..." if len(missing) > 12 else ""))
    if both:
        detail += [f"{i} is both encoded and excluded" for i in both]
    if unknown:
        detail += [f"{i} is not in the answer key" for i in unknown]
    detail += thin
    share = len(excluded) / max(len(ids), 1)
    if share > MAX_EXCLUDED:
        detail.append(f"{len(excluded)} of {len(ids)} items excluded "
                      f"({share:.0%}); the ceiling is {MAX_EXCLUDED:.0%}")
    return Result("coverage", not detail,
                  f"{len(encoded)}/{len(ids)} encoded, {len(excluded)} excluded", detail)


def _transcript(topic: Topic, key: dict, tr: dict) -> Result:
    if not tr:
        return Result("transcript", False, "missing",
                      [f"no material/transcripts/{topic.slug}.json"])
    detail = []
    for it in key["items"]:
        rec = tr.get(it["id"])
        if rec is None:
            detail.append(f"{it['id']} was never transcribed")
            continue
        if not rec.get("stem", "").strip():
            detail.append(f"{it['id']} has no stem")
        if rec.get("cb_id") and rec["cb_id"] != it["cb_id"]:
            detail.append(f"{it['id']} transcribed under id {rec['cb_id']}, key says {it['cb_id']}")
        letter = it["answer"]
        if letter in tuple("ABCD") and len(letter) == 1:
            if rec.get("format") != "mcq":
                detail.append(f"{it['id']} is keyed {letter} but transcribed as {rec.get('format')}")
            elif len(rec.get("options", [])) != 4:
                detail.append(f"{it['id']} has {len(rec.get('options', []))} options, not four")
            elif rec.get("answer_value") and not _same(
                    rec["answer_value"], rec["options"]["ABCD".index(letter)]):
                detail.append(f"{it['id']}: key {letter} is "
                              f"{rec['options']['ABCD'.index(letter)]!r}, "
                              f"transcript says the answer is {rec['answer_value']!r}")
        elif rec.get("format") != "spr":
            detail.append(f"{it['id']} has a written-in answer but is transcribed as "
                          f"{rec.get('format')}")
        # a stem that sends the reader to a table it does not carry is an item
        # nobody can answer -- the commonest way a transcription goes wrong
        if TABLE_REF.search(rec.get("stem", "")) and not rec.get("table"):
            detail.append(f"{it['id']} points at a table that was not transcribed")
    return Result("transcript", not detail, f"{len(tr)}/{len(key['items'])} items", _first(detail, 20))


def _acceptance(topic: Topic, key: dict, tr: dict) -> Result:
    by_id = {it["id"]: it for it in key["items"]}
    ok = 0
    detail, hit, total, exact, mcq = [], 0, 0, 0, 0
    for s in topic.sources:
        k = by_id.get(s.id)
        if k is None:
            detail.append(f"{s.id} is not in the answer key")
            continue
        rec = tr.get(s.id, {})
        try:
            item = s.build(random.Random(0))
        except Exception as exc:                                    # noqa: BLE001
            detail.append(f"{s.id}: template raised {type(exc).__name__}: {exc}")
            continue
        want = official_answers(rec, k["answer"])
        got = engine_answer(item)
        if any(_same(got, w) for w in want):
            ok += 1
        else:
            detail.append(f"{s.id} ({k['cb_id']}): official {'/'.join(want)!r}, engine {got!r}")
        if rec.get("format") and item.fmt != rec["format"]:
            detail.append(f"{s.id}: source is {rec['format']}, engine built {item.fmt}")
        if rec.get("options") and item.fmt == "mcq":
            mcq += 1
            off = {norm(o) for o in rec["options"]}
            mine = {norm(c) for c in item.choices}
            # the key is one of the four and acceptance already demands it
            # match, so counting it would put a free 25% under the figure --
            # what is being measured is the wrong answers
            if want:
                off -= {norm(want[0])}
            hit += len(off & mine)
            total += len(off)
            exact += off <= mine
    share = hit / max(total, 1)
    stat = (f"{ok}/{len(topic.sources)} answers, {share:.0%} of official distractors "
            f"recreated, {exact}/{max(mcq, 1)} option sets complete")
    if mcq and share < MIN_OFFICIAL_OPTIONS:
        detail.append(f"only {share:.0%} of College Board's own distractors are "
                      f"reproduced; the floor is {MIN_OFFICIAL_OPTIONS:.0%} -- the wrong "
                      "answers are invented rather than modelled")
    return Result("acceptance", not detail and ok == len(topic.sources), stat, _first(detail, 20))


def _volume(topic: Topic, per_template: int
            ) -> tuple[Result, Result, Result, Result, list]:
    """Generate at volume: the audit, the structure, the prose and the table
    checks share one pass, because generating is the expensive part."""
    audit_bad, struct_bad, prose_bad, table_bad = [], [], [], []
    named = total = made = tables = 0
    items = []
    for name in topic.templates:
        for seed in range(per_template):
            try:
                item = generate(name, seed)
            except ItemError:
                continue
            except Exception as exc:                                # noqa: BLE001
                audit_bad.append(f"{name} seed {seed}: {type(exc).__name__}: {exc}")
                if len(audit_bad) > 8:
                    break
                continue
            made += 1
            items.append(item)
            struct_bad += _structure(item, name, seed)
            prose_bad += _prose(item, name, seed)
            if item.table:
                tables += 1
                # a reader that throws has stopped reading, and a gate that
                # dies on one item reports nothing about the other 5,000
                try:
                    table_bad += [f"{name} seed {seed}: {b}"
                                  for b in _closes(item.table, item.stem)]
                except Exception as exc:                            # noqa: BLE001
                    table_bad.append(f"{name} seed {seed}: the table could not be "
                                     f"read: {type(exc).__name__}: {exc}")
            if item.fmt == "mcq":
                for r in item.reasons:
                    if r == "":
                        continue
                    total += 1
                    named += r != FILLER
    share = named / max(total, 1)
    if total and share < MIN_NAMED_DISTRACTORS:
        struct_bad.append(f"only {share:.0%} of distractors name a misconception; "
                          f"the floor is {MIN_NAMED_DISTRACTORS:.0%}")
    return (Result("audit", not audit_bad, f"{made:,} items re-derived", _first(audit_bad, 10)),
            Result("structure", not struct_bad,
                   f"{share:.0%} of distractors named", _first(struct_bad, 10)),
            Result("prose", not prose_bad, f"{made:,} items read", _first(prose_bad, 10)),
            Result("table", not table_bad,
                   f"{tables:,} tables re-added" if tables else "no item prints a table",
                   _first(table_bad, 10)),
            items)


def _structure(item, name: str, seed: int) -> list[str]:
    out = []
    if item.fmt != "mcq":
        return out
    vals = []
    for c in item.choices:
        try:
            vals.append(_num(c))
        except (ValueError, ZeroDivisionError):
            vals = []
            break
    if vals and vals != sorted(vals):
        out.append(f"{name} seed {seed}: numeric options are not in ascending order: "
                   f"{item.choices}")
    key_i = "ABCD".index(item.answer)
    shapes = [_shape(c) for c in item.choices]
    others = [s for i, s in enumerate(shapes) if i != key_i]
    # A lone integer among radicals is guessable; four options that all look
    # different are not, because then nothing is lone -- every option is the
    # only one of its own shape and the key does not stand out among them. So
    # the key standing alone only tells a student something when the rest form
    # a crowd for it to stand out from.
    if shapes.count(shapes[key_i]) == 1 and max(others.count(s) for s in others) > 1:
        out.append(f"{name} seed {seed}: the key is the only option that looks like "
                   f"{item.choices[key_i]!r} -- guessable without the mathematics")
    return out


# `pi` as a word, not as two letters inside one. `\b` alone still matches
# inside "pi-shaped", so the boundaries are explicit about what may sit beside
# it: no letter either side. A digit may precede it -- 12pi is twelve pi --
# but a letter never can, which is what keeps opinion, hospital and camping out.
_PI_WORD = re.compile(r"(?<![A-Za-z])pi(?![A-Za-z])")


def _shape(opt: str) -> tuple:
    """A crude surface signature: what the option looks like at a glance.

    Both signs count as negative. The page prints U+2212 and an author's
    literal may carry the ASCII hyphen; reading only one of them would quietly
    stop this check seeing negatives at all, which is the failure it exists to
    catch -- a lone negative among three positives is the answer.

    `pi` counts only as a word of its own, never as two letters inside another.
    Read as a substring it fires on `participants`, `opinion`, `hospital` and
    `camping`, so a sentence-valued option reads as mathematics and the key
    becomes "the only option of its shape". Three topics worked around this and
    one permanently barred a scenario from a template because of it.
    """
    has_pi = "π" in opt or _PI_WORD.search(opt) is not None
    return (bool(re.search(r"[a-zA-Z]", _PI_WORD.sub("", opt.replace("π", "")))),
            has_pi, "√" in opt or "sqrt" in opt,
            "/" in opt, "." in opt, opt.strip().startswith(("-", "\N{MINUS SIGN}")))


# An unrendered placeholder, and nothing that is merely English. "None of
# these squares shares a side" and "the slope of line l is undefined" are both
# SAT prose; banning the words made an author reword a stem and drop an option
# that the source actually prints.
#
# A brace is a placeholder when it holds a name or a format spec -- "{value}",
# "{0:.2f}", "{}" -- and not when it holds a solution set, which is how the SAT
# writes one: {5}, {−3, 7}, {1/2}. Reading every brace as a placeholder made a
# topic reserve the braced surface for the one source item that asks for it and
# print free draws as grid-ins instead.
_PLACEHOLDER = re.compile(r"\{\s*\}|\{[^}]*[!:][^}]*\}|\{\s*[A-Za-z_]\w*\s*\}"
                          r"|\bTODO\b|\bFIXME\b|\bnan\b"
                          r"|(?<![A-Za-z])None(?=[,.\s]*$)|= *None\b")

# A stem may close on a parenthetical -- College Board prints "(Disregard the
# degree symbol when entering your answer.)" -- so the sentence that ends the
# stem may be the one inside the brackets.
_ENDS_SENTENCE = re.compile(r"[?.:]\s*\)?\s*$")


def _prose(item, name: str, seed: int) -> list[str]:
    out = []
    text = item.stem
    if _PLACEHOLDER.search(text):
        out.append(f"{name} seed {seed}: stem has an unrendered placeholder: {text[:90]!r}")
    if "  " in text:
        out.append(f"{name} seed {seed}: doubled space in the stem")
    if not _ENDS_SENTENCE.search(text):
        out.append(f"{name} seed {seed}: stem does not end a sentence: {text[-40:]!r}")
    if item.fmt == "mcq":
        for c in item.choices:
            if _PLACEHOLDER.search(c):
                out.append(f"{name} seed {seed}: option has a placeholder: {c!r}")
    if not item.rationale.strip():
        out.append(f"{name} seed {seed}: no rationale")
    return out


# ------------------------------------------------------------------- tables

# A printed table is arithmetic the student is expected to trust, and until
# now nothing in the gate added one up. Two topics wrote their own reader
# rather than ship a table that does not close -- `probability`'s `Printed`
# and `sample_statistics_and_margin_of_error`'s `closed_table` -- and this is
# the better of the two promoted: `Printed`'s shape, because it reports rather
# than raises, survives a cell the question hides and does not insist a table
# carry both margins, plus `closed_table`'s check of the body against the
# total the stem names.
#
# It runs over GENERATED draws only, never over the source material. College
# Board's own table for Probability item 1.2 does not add up -- 60 + 35 = 95
# under a printed column total of 90, and 90 + 40 = 130 under a printed grand
# total of 135 -- and that item is answerable and ships. Pointed at the 92
# transcribed tables this reader fails two of them: that one, and One-Variable
# Data 3.9, whose header spans columns and so transcribes ragged. Both are
# faithful transcriptions of a printed page, and a gate that punishes a topic
# for transcribing what College Board printed teaches the author to edit the
# source. The invariant that belongs to the engine is the other one: whatever
# the source did, a table the engine BUILDS must close. Driven with the source
# items' own numbers the engine already satisfies it 85 times out of 85 -- it
# prints item 1.2 without the bad margins -- so the line costs nothing today
# and holds tomorrow.


def _cell(text):
    """The number a printed cell holds, or None when it does not hold one.

    A cell printed `x` or `?` is the question, not a defect; a cell may carry
    a comma, a percent sign, a dollar sign or the typeset minus.
    """
    t = (str(text).strip().replace(",", "").replace("\N{MINUS SIGN}", "-")
         .replace("%", "").replace("$", "").strip())
    if not t:
        return None
    try:
        return int(t)
    except ValueError:
        pass
    try:
        return float(t)
    except ValueError:
        return None


def _is_total(text) -> bool:
    return str(text).strip().rstrip("s").lower() == "total"


# The total a stem names for the table under it. Deliberately narrow: the
# danger is not missing one, it is reading the wrong number as the total and
# failing an item that is right. Every phrase here was measured over 32,211
# generated tables; the ones left out were left out for a reason a draw
# showed:
#
#   "a total of N"        the town has a total of 6,000 voters -- the
#                         population, not the 417 in the table
#   "each of N days"      on each of 3 days ... -- the article is what
#                         separates "each of its 168 employees" from a
#                         sub-unit of the scenario
#   "selected N patients" the study drew 78; the table shows the 48 of them
#                         who recovered in at least four weeks
_STEM_TOTAL = re.compile(
    r"\b(?:each|all) of (?:its|the|these|her|his|their) ([\d,]+)\b"
    r"|\ball ([\d,]+) of (?:its|the|their)\b"
    r"|\bfor the ([\d,]+) [\w\- ]{0,24}?\b"
    r"(?:in|on|at|who|that|enrolled|recorded|surveyed|listed)\b"
    r"|\bsurvey (?:of|taken by) ([\d,]+)\b"
    r"|\bsample of ([\d,]+)\b"
    r"|\bsummarizes (?:all |the )?([\d,]+)\b", re.I)


def _stem_total(stem: str) -> int | None:
    """The one total the stem names, or None when it names none or several.

    Two different numbers both reading as the total means the reader has not
    understood the sentence, and a check that is not sure is worth less than
    no check at all -- so it stands down rather than guess.
    """
    hits = {int(g.replace(",", "")) for m in _STEM_TOTAL.finditer(stem)
            for g in m.groups() if g}
    return hits.pop() if len(hits) == 1 else None


def _closes(rows: list[list[str]], stem: str = "") -> list[str]:
    """Add a printed table up again, from its own printed cells.

    Every row must reach its printed row total, every column its printed
    column total, the two margins must meet at the printed grand total, and a
    body of counts must hold the total the stem names. A table that prints no
    margins has nothing to close and passes; a row or column holding a cell
    the question hides is skipped rather than guessed at, and so is the grand
    total above it.

    Nothing is read from `item.params`: the whole point is to decide the page
    from the page, because a renderer that drops a digit is invisible to any
    check that goes back through the renderer.
    """
    bad: list[str] = []
    if not rows or len(rows) < 2:
        return bad
    width = len(rows[0])
    if width < 2 or any(len(r) != width for r in rows):
        return [f"the table is ragged -- its rows are "
                f"{[len(r) for r in rows]} cells wide"]
    total_col = _is_total(rows[0][-1])
    total_row = _is_total(rows[-1][0])
    body = rows[1:-1] if total_row else rows[1:]
    ncol = width - 1 - (1 if total_col else 0)
    if not body or ncol < 1:
        return bad
    cells = [[_cell(v) for v in r[1:1 + ncol]] for r in body]

    def off(got, printed) -> bool:              # a cell may be 3.0 as well as 3
        return abs(got - printed) > 1e-9 * max(1.0, abs(printed))

    if total_col:
        for i, row in enumerate(body):
            printed = _cell(row[-1])
            if printed is None or any(v is None for v in cells[i]):
                continue
            if off(sum(cells[i]), printed):
                bad.append(f"row {row[0]!r} holds {cells[i]} summing to "
                           f"{sum(cells[i])}, but prints a total of {printed}")
    if total_row:
        for j in range(ncol):
            col = [cells[i][j] for i in range(len(body))]
            printed = _cell(rows[-1][1 + j])
            if printed is None or any(v is None for v in col):
                continue
            if off(sum(col), printed):
                bad.append(f"column {rows[0][1 + j]!r} holds {col} summing to "
                           f"{sum(col)}, but prints a total of {printed}")
    if total_col and total_row:
        grand = _cell(rows[-1][-1])
        rtot = [_cell(r[-1]) for r in body]
        ctot = [_cell(rows[-1][1 + j]) for j in range(ncol)]
        if grand is not None and None not in rtot and off(sum(rtot), grand):
            bad.append(f"the row totals {rtot} sum to {sum(rtot)}, not to the "
                       f"printed grand total {grand}")
        if grand is not None and None not in ctot and off(sum(ctot), grand):
            bad.append(f"the column totals {ctot} sum to {sum(ctot)}, not to the "
                       f"printed grand total {grand}")

    # The stem's own total, and only for a body that counts units: a column of
    # percentages adds to 100 and a column of prices adds to nothing anybody
    # would name in a sentence.
    flat = [v for r in cells for v in r]
    if flat and all(isinstance(v, int) and v >= 0 for v in flat) \
            and not any("%" in str(v) for r in body for v in r[1:1 + ncol]):
        named = _stem_total(stem)
        if named is not None and sum(flat) != named:
            bad.append(f"the body of the table holds {sum(flat)}, but the stem "
                       f"names a total of {named}")
    return bad


def _capacity(topic: Topic, draws: int) -> Result:
    # the floor is a property of the template, but it cannot be judged from
    # fewer draws than the floor itself, so a short pass asks for less
    floor = MIN_CAPACITY if draws >= MIN_CAPACITY * 4 else max(30, draws // 3)
    detail, counts = [], {}
    for name in topic.templates:
        seen = set()
        for seed in range(draws):
            try:
                it = generate(name, seed, verify=False)
            except Exception:                                       # noqa: BLE001
                # a draw that throws is a draw that makes no item; whether the
                # throw is a bug is the audit's business, and the gate must
                # report rather than crash
                continue
            seen.add((it.stem, it.figure, it.answer, str(it.table)))
        counts[name] = len(seen)
        if len(seen) < floor:
            detail.append(f"{name}: only {len(seen)} distinct items in {draws:,} draws "
                          f"(floor {floor})")
    total = sum(counts.values())
    return Result("capacity", not detail, f"{total:,}+ distinct items", detail)


# ------------------------------------------------------------------- driver

def check_topic(slug: str, per_template: int = 300, draws: int = 1200,
                quick: bool = False) -> list[Result]:
    topics = load_topics()
    if slug not in topics:
        exc = BROKEN.get(slug)
        return [Result("import", False, "the topic does not load",
                       [f"{type(exc).__name__}: {exc}" if exc else
                        f"no topic under satbank/topics/ claims the slug {slug!r}"])]
    topic = topics[slug]
    key = key_file(slug)
    tr = transcript(slug)
    results = [_coverage(topic, key), _transcript(topic, key, tr),
               _acceptance(topic, key, tr)]
    a, s, p, t, _ = _volume(topic, 40 if quick else per_template)
    results += [a, s, p, t]
    results.append(_capacity(topic, 200 if quick else draws))
    return results


def check_all(slugs: list[str] | None = None, per_template: int = 300,
              draws: int = 1200, quick: bool = False, verbose: bool = True) -> int:
    loaded = load_topics()
    slugs = slugs or sorted(set(loaded) | set(BROKEN))
    worst = 0
    for slug in slugs:
        results = check_topic(slug, per_template, draws, quick)
        ok = all(r.ok for r in results)
        worst |= 0 if ok else 1
        name = loaded[slug].name if slug in loaded else slug
        print(f"\n{name}  [{slug}]  {'PASS' if ok else 'FAIL'}")
        for r in results:
            mark = "  ok  " if r.ok else " FAIL "
            print(f"  {mark} {r.name:<11} {r.stat}")
            if verbose or not r.ok:
                for d in r.detail:
                    print(f"          - {d}")
    return worst
