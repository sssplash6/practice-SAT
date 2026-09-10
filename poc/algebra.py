"""Proof of concept: parameterized SAT Math item generators (Algebra domain).

Each question TYPE is a template made of four parts:

    1. a parameter space        (what can vary: numbers, signs, contexts, wording)
    2. a solver                 (computes the key from the parameters)
    3. distractor strategies    (each wrong option = one real student misconception)
    4. a verifier               (independently re-checks the key before shipping)

No LLM at runtime. Generation is deterministic, seedable, instant, free, and
provably correct. The LLM's job happens offline: turning a source question into
one of these templates.
"""

from __future__ import annotations

import argparse
import random
from dataclasses import dataclass
from fractions import Fraction

# ---------------------------------------------------------------- rendering


def fmt(v) -> str:
    v = Fraction(v)
    return str(v.numerator) if v.denominator == 1 else f"{v.numerator}/{v.denominator}"


def safe_frac(num, den, fallback) -> Fraction:
    """Distractor formulas can hit a zero denominator; fall back rather than crash."""
    return Fraction(num, den) if den else Fraction(fallback)


def poly(terms) -> str:
    """Render [(coef, var|None), ...] as '3x - 4', skipping zero terms."""
    out = ""
    for coef, var in terms:
        c = Fraction(coef)
        if c == 0:
            continue
        mag = abs(c)
        if var and mag == 1:
            body = var
        elif var:
            body = f"{fmt(mag)}{var}"
        else:
            body = fmt(mag)
        if not out:
            out = ("-" if c < 0 else "") + body
        else:
            out += (" - " if c < 0 else " + ") + body
    return out or "0"


# ---------------------------------------------------------------- item model


@dataclass
class Item:
    template_id: str
    skill: str
    seed: int
    stem: str
    choices: list[str]
    answer_index: int
    rationale: str
    reasons: list[str]  # why a student would pick each option; "" for the key

    def pretty(self) -> str:
        lines = [f"[{self.template_id} | {self.skill} | seed={self.seed}]", self.stem]
        for i, ch in enumerate(self.choices):
            mark = "*" if i == self.answer_index else " "
            why = f"   <- {self.reasons[i]}" if self.reasons[i] else "   <- KEY"
            lines.append(f"  {mark} {'ABCD'[i]}) {ch}{why}")
        lines.append(f"    why: {self.rationale}")
        return "\n".join(lines)


def same_format(a, b) -> bool:
    """An integer key hiding among fractional distractors gives itself away."""
    return (Fraction(a).denominator == 1) == (Fraction(b).denominator == 1)


def assemble(rng, key, candidates, render=fmt):
    """Pick 3 distractors: distinct, plausible, and format-matched to the key.

    `candidates` is [(value, reason), ...] in priority order. Misconception-based
    distractors are used first; neutral fillers only patch the gaps.
    """
    picked: list[tuple[Fraction, str]] = []
    seen = {Fraction(key)}
    for val, reason in candidates:
        val = Fraction(val)
        if val in seen or not same_format(val, key):
            continue
        picked.append((val, reason))
        seen.add(val)
        if len(picked) == 3:
            break
    fillers = [Fraction(key) + d for d in (1, -1, 2, -2, 3, -3, 5, -5)]
    for val in fillers:
        if len(picked) == 3:
            break
        if val in seen or not same_format(val, key):
            continue
        picked.append((val, "near-miss arithmetic slip"))
        seen.add(val)

    options = picked + [(Fraction(key), "")]
    rng.shuffle(options)
    choices = [render(v) for v, _ in options]
    reasons = [r for _, r in options]
    return choices, reasons, next(i for i, (_, r) in enumerate(options) if r == "")


# ------------------------------------------------------- T1: linear, one var


def t1_linear_one_variable(rng, seed) -> Item:
    """a(bx + c) + d = ex + f   ->   solve for x."""
    while True:
        x0 = rng.choice([v for v in range(-9, 10) if v != 0])
        a = rng.choice([v for v in range(-5, 6) if v != 0])
        b = rng.choice([v for v in range(-5, 6) if v != 0])
        c, d = rng.randint(-9, 9), rng.randint(-9, 9)
        e = rng.randint(-6, 6)
        if a * b == e or c == 0:
            continue
        f = a * b * x0 + a * c + d - e * x0
        if abs(f) > 120:
            continue
        break

    key = Fraction(f - a * c - d, a * b - e)
    assert key == x0, "solver disagrees with construction"
    assert a * (b * x0 + c) + d == e * x0 + f, "key fails substitution"

    coef = {1: "", -1: "-"}.get(a, fmt(a))  # "-(3x - 6)", never "-1(3x - 6)"
    lhs = f"{coef}({poly([(b, 'x'), (c, None)])})"
    if d:
        lhs += (" - " if d < 0 else " + ") + fmt(abs(d))
    stem = f"If {lhs} = {poly([(e, 'x'), (f, None)])}, what is the value of x?"

    cands = [
        (safe_frac(f - c - d, a * b - e, key + 1), "distributed a to bx but not to c"),
        (safe_frac(f + a * c + d, a * b - e, key + 2), "sign error moving constants across ="),
        (safe_frac(f - a * c - d, a * b + e, key + 3), "added the x-terms instead of subtracting"),
        (-key, "solved correctly, then dropped the sign"),
    ]
    choices, reasons, ai = assemble(rng, key, cands)
    return Item(
        "ALG.LIN1V.distribute",
        "Linear equations in one variable",
        seed,
        stem,
        choices,
        ai,
        f"Distribute: {poly([(a*b,'x'),(a*c+d,None)])} = {poly([(e,'x'),(f,None)])}; "
        f"collect x: {poly([(a*b-e,'x')])} = {fmt(f-a*c-d)}; so x = {fmt(key)}.",
        reasons,
    )


# ------------------------------------------------- T2: system of two linears


def t2_system_two_linears(rng, seed) -> Item:
    while True:
        x0, y0 = rng.randint(-8, 8), rng.randint(-8, 8)
        a1, b1 = rng.choice([-4, -3, -2, -1, 1, 2, 3, 4]), rng.choice([-4, -3, -2, -1, 1, 2, 3, 4])
        a2, b2 = rng.choice([-4, -3, -2, -1, 1, 2, 3, 4]), rng.choice([-4, -3, -2, -1, 1, 2, 3, 4])
        det = a1 * b2 - a2 * b1
        if det == 0 or (x0 == 0 and y0 == 0):
            continue
        break

    c1, c2 = a1 * x0 + b1 * y0, a2 * x0 + b2 * y0
    assert Fraction(c1 * b2 - c2 * b1, det) == x0 and Fraction(a1 * c2 - a2 * c1, det) == y0

    ask, key = rng.choice([("x", x0), ("y", y0), ("x + y", x0 + y0)])
    stem = (
        "The system of equations below has solution (x, y).\n"
        f"      {poly([(a1,'x'),(b1,'y')])} = {c1}\n"
        f"      {poly([(a2,'x'),(b2,'y')])} = {c2}\n"
        f"  What is the value of {ask}?"
    )
    cands = [
        ({"x": y0, "y": x0, "x + y": x0 - y0}[ask], "swapped x and y / wrong combination"),
        (-key, "sign error during elimination"),
        (x0 - y0 if ask != "x + y" else y0 - x0, "subtracted where the setup called for adding"),
        (x0 + y0 if ask != "x + y" else x0 * y0, "answered a different quantity than asked"),
    ]
    choices, reasons, ai = assemble(rng, key, cands)
    return Item(
        "ALG.SYS2V.elimination",
        "Systems of two linear equations",
        seed,
        stem,
        choices,
        ai,
        f"Solving gives x = {x0}, y = {y0}, so {ask} = {fmt(key)}.",
        reasons,
    )


# -------------------------------------------------------------- T3: slope


def t3_slope_from_points(rng, seed) -> Item:
    while True:
        den = rng.choice([1, 1, 1, 2, 3])
        num = rng.choice([v for v in range(-9, 10) if v != 0])
        m = Fraction(num, den)
        dx = den * rng.choice([-3, -2, -1, 1, 2, 3])
        x1, y1 = rng.randint(-9, 9), rng.randint(-9, 9)
        x2, y2 = x1 + dx, y1 + int(m * dx)
        if dx == 0 or abs(y2) > 30:
            continue
        break

    key = Fraction(y2 - y1, x2 - x1)
    assert key == m, "slope solver disagrees with construction"

    stem = (
        f"In the xy-plane, line ℓ passes through the points ({x1}, {y1}) and ({x2}, {y2}). "
        "What is the slope of line ℓ?"
    )
    cands = [
        (safe_frac(x2 - x1, y2 - y1, key + 1), "computed run over rise (reciprocal)"),
        (-key, "subtracted the coordinates in inconsistent order"),
        (safe_frac(y2 + y1, x2 + x1, key + 2), "added coordinates instead of subtracting"),
        (Fraction(y2 - y1), "used the rise only, ignoring the run"),
    ]
    choices, reasons, ai = assemble(rng, key, cands)
    return Item(
        "ALG.LINFN.slope_two_points",
        "Linear functions",
        seed,
        stem,
        choices,
        ai,
        f"slope = (y2 - y1)/(x2 - x1) = ({y2} - {y1})/({x2} - {x1}) = {fmt(key)}.",
        reasons,
    )


# ------------------------------------- T4: linear model in context (wording)

CONTEXTS = [
    ("A technician", "charges a one-time service fee of", "and", "per hour of labor", "hours", "h", "total charge, in dollars,"),
    ("A rental company", "charges a base fee of", "plus", "per mile driven", "miles", "m", "total cost, in dollars,"),
    ("A caterer", "charges a fixed setup cost of", "and an additional", "per guest served", "guests", "g", "total cost, in dollars,"),
    ("A print shop", "charges a design fee of", "plus", "per poster printed", "posters", "p", "total cost, in dollars,"),
    ("A gym", "charges a registration fee of", "and", "per month of membership", "months", "t", "total amount paid, in dollars,"),
]


def t4_linear_model_in_context(rng, seed) -> Item:
    base = rng.choice([15, 20, 25, 30, 35, 40, 45, 50, 60, 75])
    rate = rng.choice([3, 4, 5, 6, 8, 9, 12, 15, 18, 20])
    who, fee_phrase, joiner, per_phrase, unit_plural, var, quantity = rng.choice(CONTEXTS)
    mode = rng.choice(["evaluate", "solve"])

    if mode == "evaluate":
        n = rng.randint(3, 14)
        key = Fraction(base + rate * n)
        stem = (
            f"{who} {fee_phrase} ${base} {joiner} ${rate} {per_phrase}. "
            f"What is the {quantity} for {n} {unit_plural}?"
        )
        cands = [
            (rate * n, "left out the fixed fee"),
            (base * n + rate, "swapped the roles of the fee and the rate"),
            (base + rate + n, "added all three numbers"),
            (base * rate, "multiplied the fee by the rate"),
        ]
        rationale = f"C = {base} + {rate}({n}) = {fmt(key)}."
    else:
        n = rng.randint(3, 14)
        total = base + rate * n
        key = Fraction(n)
        stem = (
            f"{who} {fee_phrase} ${base} {joiner} ${rate} {per_phrase}. "
            f"If the {quantity} was ${total}, how many {unit_plural} were billed?"
        )
        cands = [
            (safe_frac(total, rate, key + 1), "divided by the rate without removing the fixed fee"),
            (safe_frac(total - rate, base, key + 2), "divided by the fee instead of the rate"),
            (total - base - rate, "subtracted the rate instead of dividing by it"),
            (safe_frac(total + base, rate, key + 3), "added the fixed fee instead of subtracting it"),
        ]
        rationale = f"{base} + {rate}{var} = {total}, so {rate}{var} = {total - base} and {var} = {fmt(key)}."

    choices, reasons, ai = assemble(rng, key, cands, render=lambda v: f"${fmt(v)}" if mode == "evaluate" else fmt(v))
    return Item(
        f"ALG.LINMODEL.{mode}",
        "Linear functions in context",
        seed,
        stem,
        choices,
        ai,
        rationale,
        reasons,
    )


TEMPLATES = [
    t1_linear_one_variable,
    t2_system_two_linears,
    t3_slope_from_points,
    t4_linear_model_in_context,
]


def generate(template, seed: int) -> Item:
    """Same seed -> byte-identical item. Different seed -> a new variation."""
    return template(random.Random(seed), seed)


def validate(item: Item) -> None:
    assert len(item.choices) == 4, "must have 4 options"
    assert len(set(item.choices)) == 4, f"duplicate options: {item.choices}"
    assert 0 <= item.answer_index < 4
    assert item.reasons[item.answer_index] == ""
    ints = [("/" not in c) for c in item.choices]
    assert len(set(ints)) == 1, f"format leak - the odd one out is guessable: {item.choices}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=2, help="variations to show per template")
    ap.add_argument("--fuzz", type=int, default=20000, help="items to generate-and-verify")
    args = ap.parse_args()

    for template in TEMPLATES:
        for k in range(args.n):
            print(generate(template, 1000 + k * 7919).pretty())
            print()

    bad = 0
    for seed in range(args.fuzz):
        item = generate(TEMPLATES[seed % len(TEMPLATES)], seed)
        try:
            validate(item)
        except AssertionError as exc:
            bad += 1
            if bad <= 3:
                print(f"FAIL seed={seed}: {exc}")
    print(f"verified {args.fuzz} generated items across {len(TEMPLATES)} templates: "
          f"{args.fuzz - bad} passed, {bad} failed")

    seen = {t.__name__: set() for t in TEMPLATES}
    for seed in range(20000):
        t = TEMPLATES[seed % len(TEMPLATES)]
        seen[t.__name__].add(generate(t, seed).stem)
    print("distinct stems from 5,000 seeds per template: "
          + ", ".join(f"{k.split('_',1)[1]}={len(v)}" for k, v in seen.items()))


if __name__ == "__main__":
    main()
