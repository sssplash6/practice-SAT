"""Every One-Variable Data answer, derived a second time.

Written from the definitions in plain floats: a median is found here by
sorting a list and counting in, never by calling the generator's helper. The
statement templates are checked the same way -- the item records the sentence
with the comparison left out, and this file decides, from the data alone,
which way round it goes. A template that keys the wrong sentence fails here.

Nothing in this file imports from `families/` or from `common.py`.
"""

from __future__ import annotations

import math
import random as _random

from ...audit import AuditError

__all__ = ["AUDITS"]


# ------------------------------------------------------- the definitions

def _mean(xs) -> float:
    xs = list(xs)
    if not xs:
        raise AuditError("the mean of no values")
    total = 0.0
    for x in xs:
        total += float(x)
    return total / len(xs)


def _median(xs) -> float:
    s = sorted(float(x) for x in xs)
    n = len(s)
    if n == 0:
        raise AuditError("the median of no values")
    if n % 2:
        return s[(n - 1) // 2]
    return (s[n // 2 - 1] + s[n // 2]) / 2.0


def _mode(xs):
    counts: dict[float, int] = {}
    for x in xs:
        counts[float(x)] = counts.get(float(x), 0) + 1
    top = max(counts.values())
    winners = [v for v, c in counts.items() if c == top]
    if len(winners) != 1:
        raise AuditError("no single most common value")
    return winners[0]


def _spread(xs) -> float:
    s = [float(x) for x in xs]
    return max(s) - min(s)


def _sd(xs) -> float:
    s = [float(x) for x in xs]
    m = _mean(s)
    return math.sqrt(sum((x - m) ** 2 for x in s) / len(s))


def _round(v: float, places: int = 0) -> float:
    f = 10.0 ** places
    return math.floor(v * f + 0.5) / f if v >= 0 else -math.floor(-v * f + 0.5) / f


def _fmt(v: float, places=None) -> str:
    if places is not None:
        return f"{_round(v, places):,.{places}f}"
    if abs(v - round(v)) < 1e-9:
        return f"{int(round(v)):,}"
    return f"{v:g}"


def _expand(values, freqs) -> list[float]:
    out: list[float] = []
    for v, f in zip(values, freqs):
        out += [float(v)] * int(f)
    if not out:
        raise AuditError("an empty frequency table")
    return out


def _stat(xs, which: str) -> float:
    return {"mean": _mean, "median": _median, "mode": _mode,
            "range": _spread}[which](xs)


def _rel(a: float, b: float) -> str:
    return "greater" if a > b else ("less" if a < b else "equal")


def _rel_than(a: float, b: float) -> str:
    return {"greater": "greater than", "less": "less than",
            "equal": "equal to"}[_rel(a, b)]


def _one_two(t1: bool, t2: bool) -> str:
    return {(True, True): "I and II", (True, False): "I only",
            (False, True): "II only", (False, False): "Neither I nor II"}[(t1, t2)]


# ------------------------------------------------------------- centres

def _centre(p: dict):
    if p["stat"] == "pair_sum":
        i, j = p["pair"]
        return float(p["values"][i]) + float(p["values"][j])
    v = _stat(p["values"], p["stat"])
    if p.get("compare_other"):
        v = abs(v - _stat(p["other"], p["stat"]))
    if p.get("reference") is not None:
        v = abs(v - float(p["reference"]))
    if p.get("rounding") is not None:
        v = _round(v, int(p["rounding"]))
    prefix, suffix = p.get("prefix", ""), p.get("suffix", "")
    if prefix or suffix:
        if p.get("places") is None:
            raise AuditError("an option with a unit symbol must fix its decimal places")
        return f"{prefix}{_fmt(v, int(p['places']))}{suffix}"
    return v


def bar_read(p: dict):
    vals = [float(v) for v in p["values"]]
    if p["ask"] == "value":
        return vals[int(p["target"])]
    if p["ask"] == "difference":
        return vals[int(p["target"])] - vals[int(p["other"])]
    return _mean(vals)


# ---------------------------------------------------- frequency tables

def freq_stat(p: dict):
    data = _expand(p["values"], p["freqs"])
    if p["ask"] == "mean_minus_median":
        v = _mean(data) - _median(data)
        if p.get("symbolic"):
            # the claim is that the answer does not depend on a: check it
            twice = _expand(p["values"], [2 * f for f in p["freqs"]])
            if abs((_mean(twice) - _median(twice)) - v) > 1e-9:
                raise AuditError("the answer depends on a, so the item is not well posed")
        return v
    return _stat(data, p["ask"])


def freq_order(p: dict):
    data = _expand(p["values"], p["freqs"])
    named = {"mean": _mean(data), "median": _median(data), "mode": _mode(data)}
    if len({round(v, 9) for v in named.values()}) != 3:
        raise AuditError("two of the three measures are equal")
    return " < ".join(sorted(named, key=lambda k: named[k]))


def freq_two(p: dict):
    A = _expand(p["values"], p["fa"])
    B = _expand(p["values"], p["fb"])
    if p["ask"] == "median_difference":
        return _median(B) - _median(A)
    return p["claim"].format(rel=_rel(_mean(A), _mean(B)))


def _table_text(values, freqs) -> str:
    return ", ".join(f"{_fmt(float(v))} (frequency {int(f)})"
                     for v, f in zip(values, freqs))


def freq_choose(p: dict):
    if p["ask"] == "mean_over_median":
        fits = [lst for lst in p["lists"] if _mean(lst) > _median(lst)]
        if len(fits) != 1:
            raise AuditError(f"{len(fits)} data sets have a mean above the median")
        return ", ".join(_fmt(float(v)) for v in fits[0])
    if p["ask"] == "match_list":
        counts: dict[float, int] = {}
        order: list[float] = []
        for x in p["data"]:
            x = float(x)
            if x not in counts:
                order.append(x)
            counts[x] = counts.get(x, 0) + 1
        return _table_text(order, [counts[v] for v in order])
    tables = [p["rising"], p["flat"], p["cup_a"], p["cup_b"]]
    means = [_mean(_expand(p["values"], t)) for t in tables]
    best = max(range(4), key=lambda i: means[i])
    if sorted(means)[-1] - sorted(means)[-2] < 1e-9:
        raise AuditError("two tables tie for the greatest mean")
    return _table_text(p["values"], tables[best])


# --------------------------------------------------- comparing two sets

WHICH_DIFFER = {
    (False, True): "Only the means are different.",
    (True, False): "Only the medians are different.",
    (False, False): "Both the means and the medians are different.",
}


def compare_sets(p: dict):
    A, B = [float(v) for v in p["a"]], [float(v) for v in p["b"]]
    if p["ask"] == "means_statement":
        return p["claim"].format(rel=_rel(_mean(A), _mean(B)))
    if p["ask"] == "which_differ":
        same = (abs(_mean(A) - _mean(B)) < 1e-9, abs(_median(A) - _median(B)) < 1e-9)
        if same == (True, True):
            raise AuditError("nothing differs, so no statement is true")
        return WHICH_DIFFER[same]
    first, second = p.get("order", ["mean", "median"])
    return _one_two(_stat(A, first) > _stat(B, first),
                    _stat(A, second) > _stat(B, second))


def sd_compare(p: dict):
    if p["presentation"] == "summary":
        ga, gb = p["groups"]
        if abs(p["sd_a"] - p["sd_b"]) < 1e-12:
            raise AuditError("the two standard deviations are equal")
        wide, narrow = (gb, ga) if p["sd_b"] > p["sd_a"] else (ga, gb)
        return p["claim"].format(wide=wide, narrow=narrow)
    edges = [float(e) for e in p["edges"]]
    mids = [(edges[i] + edges[i + 1]) / 2 for i in range(len(edges) - 1)]
    a = _sd(_expand(mids, p["counts_a"]))
    b = _sd(_expand(mids, p["counts_b"]))
    return p["claim"].format(rel=_rel_than(a, b))


def box_read(p: dict):
    s = [float(v) for v in p["summary"]]
    if len(s) != 5 or any(s[i] >= s[i + 1] for i in range(4)):
        raise AuditError("a box plot needs five increasing values")
    return s[{"least": 0, "q1": 1, "median": 2, "q3": 3, "greatest": 4}[p["ask"]]]


def box_compare(p: dict):
    a, b = [float(v) for v in p["first"]], [float(v) for v in p["second"]]
    if abs(a[2] - b[2]) < 1e-12:
        raise AuditError("the two medians are equal, so nothing must be true")
    return p["claim"].format(rel="greater" if a[2] > b[2] else "less")


# ------------------------------------------------------------- an edit

def _apply(edit: str, vals: list[float], k: float) -> list[float]:
    if edit == "correct_low":
        return [vals[0] - k] + vals[1:]
    if edit == "raise_max":
        return vals[:-1] + [vals[-1] + k]
    if edit == "add_constant":
        return [v + k for v in vals]
    med = _median(vals)
    return [v + k if v > med else (v - k if v < med else v) for v in vals]


def measure_effect(p: dict):
    n, k, edit = int(p["n"]), float(p["k"]), p["edit"]
    moved: dict[str, bool] = {}
    for trial in range(4):
        rr = _random.Random(9781 + trial)
        vals = sorted(rr.sample(range(100, 900), n))
        after = _apply(edit, vals, k)
        for name, fn in (("mean", _mean), ("median", _median), ("range", _spread),
                         ("sd", _sd), ("sum", lambda xs: sum(float(x) for x in xs))):
            changed = abs(fn(after) - fn(vals)) > 1e-9
            if name in moved and moved[name] != changed:
                raise AuditError(f"{edit} moves the {name} for some data sets and not "
                                 f"others")
            moved[name] = changed
    want = p["ask"] == "changed"
    fits = [m for m in p["measures"] if moved[m] == want]
    if len(fits) != 1:
        raise AuditError(f"{len(fits)} of the options answer the question, not one")
    return p["labels"][fits[0]]


def odd_measure(p: dict):
    vals = [float(v) for v in p["values"]]
    target = float(p["target"])
    named = {"mean": _mean(vals), "median": _median(vals), "range": _spread(vals),
             "mode": _mode(vals)}
    odd = [m for m in p["measures"] if abs(named[m] - target) > 1e-9]
    if len(odd) != 1:
        raise AuditError(f"{len(odd)} of the measures differ from the stated value")
    return p["labels"][odd[0]]


def new_data_set(p: dict):
    A = [float(v) for v in p["values"]]
    if p["mode"] == "shift":
        B = [v + float(p["c"]) for v in A]
        return p["claim"].format(r1=_rel_than(_median(B), _median(A)),
                                 r2=_rel_than(_spread(B), _spread(A)))
    B = A + [float(p["extra"])]
    first, second = p["order"]
    return _one_two(_stat(B, first) > _stat(A, first),
                    _stat(B, second) > _stat(A, second))


# -------------------------------------------------------- missing values

def unknown_value(p: dict):
    if p["mode"] == "equal_means":
        A, known = [float(v) for v in p["a"]], [float(v) for v in p["known"]]
        n = len(A)
        target = _mean(A) + float(p["d"])
        return target * n - sum(known)
    if p["mode"] == "mean_equals_median":
        k = sorted(float(v) for v in p["values"])
        x = float(p["wrong"])
        if abs(_mean(k + [x]) - _median(k + [x])) < 1e-9:
            raise AuditError(f"{x} does make the mean and the median equal")
        works = [c for c in _solutions(k) if abs(c - x) > 1e-9]
        if len(works) != 3:
            raise AuditError(f"{len(works)} values of x work, not three")
        return x
    vals = [float(v) for v in p["values"]]
    n, S = len(vals) + 1, sum(vals)
    m = S / len(vals)
    fits = [x for x in range(1, int(p["bound"]))
            if abs((S + x) / n - round((S + x) / n)) < 1e-9 and (S + x) / n > m]
    if len(fits) != 1:
        raise AuditError(f"{len(fits)} values of the missing integer fit, not one")
    return max(max(vals), float(fits[0]))


def _solutions(k: list[float]) -> list[float]:
    """Every x making the mean of the five equal their median."""
    out = []
    for x in _candidates(k):
        five = k + [x]
        if abs(_mean(five) - _median(five)) < 1e-9:
            out.append(x)
    return sorted(set(out))


def _candidates(k: list[float]) -> list[float]:
    S = sum(k)
    return [5 * k[1] - S, S / 4.0, 5 * k[2] - S]


def mean_totals(p: dict):
    if p["mode"] == "removed":
        n = int(p["n"])
        return n * float(p["m1"]) - (n - 1) * float(p["m2"])
    n1, n2 = int(p["n1"]), int(p["n2"])
    return (n1 * float(p["m1"]) + n2 * float(p["m2"])) / (n1 + n2)


def mean_identity(p: dict):
    if p["mode"] == "consecutive":
        n = int(p["n"])
        start = 7                       # any run of n consecutive integers will do
        run = [start + i for i in range(n)]
        return abs(_mean(run) - _median(run))
    vals = [float(v) for v in p["values"]]
    total = sum(vals)
    if total == 0:
        raise AuditError("a total of zero has no fraction")
    return _mean(vals) / total


# ----------------------------------------------------------- reasoning

def reason_center(p: dict):
    if p["mode"] == "calculable":
        n, total = int(p["n"]), float(p["total"])
        # two data sets with the same count and total but different medians,
        # least and greatest values: only the average is settled
        one = [total / n] * n
        two = [0.0] * (n - 1) + [total]
        if abs(_mean(one) - _mean(two)) > 1e-9:
            raise AuditError("the two test data sets do not share a mean")
        for fn in (_median, min, max):
            if abs(fn(one) - fn(two)) < 1e-9:
                raise AuditError("a second measure is settled by the total after all")
        return p["claim"].format(word="average")
    counts = [int(c) for c in p["counts"]]
    lo, hi = float(p["bounds"][0]), float(p["bounds"][1])
    N = sum(counts)
    if N % 2 == 0:
        raise AuditError("an even count leaves the median between two values")
    pos = (N + 1) // 2
    band = 0 if pos <= counts[0] else (1 if pos <= counts[0] + counts[1] else 2)
    inside = []
    for v in p["options"]:
        v = float(v)
        ok = (v < lo) if band == 0 else ((lo <= v <= hi) if band == 1 else (v > hi))
        if ok:
            inside.append(v)
    if len(inside) != 1:
        raise AuditError(f"{len(inside)} of the options could be the median, not one")
    return inside[0]


def must_be_true(p: dict):
    if p["mode"] == "two_means":
        n, m1, m2 = int(p["n"]), float(p["m1"]), float(p["m2"])
        if m2 <= m1:
            raise AuditError("the second mean must be the larger one")
        # I and II are settled by exhibiting one pair of data sets with the
        # stated means that breaks them; III by the fact that a data set
        # cannot have a larger mean while every value is smaller.
        eps = m1 / 2.0
        a_hi = [m1 * n - (n - 1) * eps] + [eps] * (n - 1)
        b_lo = [m2 * n - (n - 1) * eps] + [eps] * (n - 1)
        for xs, m in ((a_hi, m1), (b_lo, m2)):
            if abs(_mean(xs) - m) > 1e-9:
                raise AuditError("the counterexample does not have the stated means")
        one_broken = max(a_hi) > min(b_lo)          # a member of A above one of B
        two_broken = _median(b_lo) <= _median([m1] * n)
        three = m2 > m1
        parts = [r for r, t in zip(("I", "II", "III"),
                                   (not one_broken, not two_broken, three)) if t]
        if not parts:
            return "None of the statements must be true"
        if len(parts) == 3:
            return "I, II, and III"
        return " and ".join(parts) + " only" if len(parts) == 2 else parts[0] + " only"
    size, lo, hi = int(p["size"]), float(p["lo"]), float(p["hi"])
    extra = float(p["extra"])
    truth = {}
    for measure in ("mean", "median"):
        holds = True
        for fill in (lo + 1, hi - 1, (lo + hi) / 2):
            F = [fill] * size
            G = F + [extra]
            if not _stat(F, measure) < _stat(G, measure):
                holds = False
        if holds:                       # a mixed data set is the harder test
            F = [lo + 1] * (size // 2) + [hi - 1] * (size - size // 2)
            if not _stat(F, measure) < _stat(F + [extra], measure):
                holds = False
        truth[measure] = holds
    first, second = p["order"]
    return _one_two(truth[first], truth[second])


AUDITS = {
    "ovd_list_stat": _centre,
    "ovd_table_stat": _centre,
    "ovd_bar_read": bar_read,
    "ovd_freq_stat": freq_stat,
    "ovd_freq_order": freq_order,
    "ovd_freq_two": freq_two,
    "ovd_freq_choose": freq_choose,
    "ovd_compare_sets": compare_sets,
    "ovd_sd_compare": sd_compare,
    "ovd_box_read": box_read,
    "ovd_box_compare": box_compare,
    "ovd_measure_effect": measure_effect,
    "ovd_odd_measure": odd_measure,
    "ovd_new_data_set": new_data_set,
    "ovd_unknown_value": unknown_value,
    "ovd_mean_totals": mean_totals,
    "ovd_mean_identity": mean_identity,
    "ovd_reason_center": reason_center,
    "ovd_must_be_true": must_be_true,
}
