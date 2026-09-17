"""The 85 official Nonlinear Equations and Systems items, encoded as the
parameters that reproduce them.

No answer is written here. The answers live in
`material/keys/nonlinear_equations_and_systems.json`, read from the College Board
PDF's own text layer, and the check drives these templates with the source item's
own numbers and asks whether the engine lands on them. `wrongs` names the three
misconceptions the item writer reached for, in the order they are offered.
"""

from __future__ import annotations

from fractions import Fraction as F

from ...topic import S, Source
from .families.condition import (count_real_solutions, count_system_solutions,
                                 discriminant_constant, integer_roots_constant,
                                 symbolic_intersections, tangent_constant,
                                 tangent_point)
from .families.graph import function_meets, graph_count, graph_solution
from .families.literal import (isolate_bracket, isolate_denominator,
                               isolate_factor, isolate_sum, scale_relation)
from .families.solve import (absolute_equation, cancel_squares, factored_equation,
                             paired_quadratics, product_roots_constant,
                             quadratic_formula, quadratic_solve, radical_equation,
                             rational_combine, rational_linear, rational_quadratic,
                             scaled_quadratic, shared_factor, square_equation)
from .families.system import curve_line_system, secant_slope, spec_terms as T
from .families.system import sum_product

ALL: list[Source] = [
    # ------------------------------------------------------------ easy (22)
    S("1.1", lambda r: scale_relation(r, 0, a=6, b=9, c=12, g=3, op=">",
                                      frame="above",
                                      wrongs=["divide_each", "swap_coefs",
                                              "reverse_terms"])),
    S("1.2", lambda r: graph_solution(r, 0, kind="parabola", a=F(1, 2), h=1,
                                      k=F(7, 2), m=1, x0=2, window=(-2, 9, -2, 9),
                                      step=1, frame="nonlinear",
                                      wrongs=["origin", "y_axis_line",
                                              "y_then_zero"]),
      "the source draws an increasing curve tangent to the line; the template "
      "draws a parabola tangent to it at the same marked point"),
    S("1.3", lambda r: square_equation(r, 0, shape="gathered", a=1, spare=-4, k=0,
                                       ask="which", fmt="mcq",
                                       wrongs=["quarter", "constant"])),
    S("1.4", lambda r: isolate_sum(r, 0, target="q", coef=1, extras=[(-29, "r")],
                                   other=[(1, "s")], frame="relates_positive",
                                   wrongs=["sign", "product", "quotient"])),
    S("1.5", lambda r: curve_line_system(r, 0, curve=T([(1, "y")], [(1, "x2")]),
                                         line=T([(1, "x"), (1, "y")], [(12, "")]),
                                         ask="possible_x", frame="possible_x",
                                         fmt="mcq", branch="hi",
                                         wrongs=["near_down_3", "near_down_2",
                                                 "near_down_1"])),
    S("1.6", lambda r: isolate_factor(
        r, 0, target="W", left=[(1, "P")], k=1, top=["W"], bottom=["t"],
        story="The power P produced by a machine is represented by the equation "
              "above, where W is the work performed during an amount of time t. "
              "Which of the following correctly expresses W in terms of P and t ?",
        wrongs=["divide_instead", "divide_instead_flip", "sum_all"])),
    S("1.7", lambda r: absolute_equation(r, 0, a=1, h=2, k=9, ask="one_possible",
                                         fmt="spr")),
    S("1.8", lambda r: square_equation(r, 0, shape="plain", a=1, k=64,
                                       ask="which_value", fmt="mcq",
                                       sign_rule=False,
                                       wrongs=["half_root", "half_constant",
                                               "double_constant"])),
    S("1.9", lambda r: isolate_factor(
        r, 0, target="Q", left=[(1, "T")], k=1, top=["P", "Q"], bottom=[],
        order=["P", "Q", "T"],
        story="The total revenue from sales of a product can be calculated using "
              "the formula {eq}, where T is the total revenue, P is the price of "
              "the product, and Q is the quantity of the product sold. Which of "
              "the following equations gives the quantity of product sold in "
              "terms of P and T ?",
        wrongs=["invert", "product_all", "difference"])),
    S("1.10", lambda r: isolate_factor(r, 0, target="c", left=[(1, "b")], k=42,
                                       top=["c", "f"], bottom=[],
                                       frame="relates_positive",
                                       wrongs=["coef_subtracted", "product_all",
                                               "subtract_all"])),
    S("1.11", lambda r: square_equation(r, 0, shape="shifted", h=5, k=4, ask="which",
                                        fmt="mcq",
                                        wrongs=["swap_shift", "no_root"])),
    S("1.12", lambda r: radical_equation(r, 0, shape="simple", a=1, b=4, c=11,
                                         ask="what_value", fmt="spr")),
    S("1.13", lambda r: square_equation(r, 0, shape="plain", a=1, k=484,
                                        rhs_style="product", ask="positive",
                                        fmt="spr")),
    S("1.14", lambda r: isolate_sum(r, 0, target="p", coef=1, extras=[(34, "")],
                                    other=[(1, "q"), (1, "r")], frame="relates_vars",
                                    wrongs=["sign", "negate_all_sign",
                                            "negate_all"])),
    S("1.15", lambda r: absolute_equation(r, 0, a=1, h=5, k=10, ask="one_possible",
                                          fmt="spr")),
    S("1.16", lambda r: isolate_sum(r, 0, target="j", coef=8, extras=[],
                                    other=[(1, "k"), (15, "m")],
                                    frame="relates_distinct",
                                    wrongs=["first_only", "last_only", "multiply"])),
    S("1.17", lambda r: isolate_bracket(r, 0, target="m", left=[(7, "m")], c=2,
                                        inner=[(1, "n"), (1, "p")], frame="gives",
                                        wrongs=["no_divide", "subtract_divisor",
                                                "strip_brackets"])),
    S("1.18", lambda r: graph_solution(r, 0, kind="parabola", a=1, h=4, k=1, m=0,
                                       x0=4, window=(0, 13, 0, 12), step=2,
                                       frame="quadratic",
                                       wrongs=["origin", "x_sign", "y_sign"])),
    S("1.19", lambda r: graph_solution(r, 0, kind="absolute", a=1, h=4, k=2, m=1,
                                       x0=1, window=(-3, 10, 0, 10), step=1,
                                       frame="absolute", offsets=[-2, 3],
                                       wrongs=["on_line_1", "y_axis_line",
                                               "vertex"])),
    S("1.20", lambda r: absolute_equation(r, 0, a=5, bare=True, k=45, ask="positive",
                                          fmt="spr")),
    S("1.21", lambda r: curve_line_system(
        r, 0, curve=T([(1, "y")], [(5, "x2"), (4, "")]),
        line=T([(1, "y")], [(5, "x"), (4, "")]), ask="which_pair",
        frame="which_pair", branch="lo", offsets=[8],
        wrongs=["origin", "line_only_1", "swapped"]),
      "the source's fourth option, (8, 84), lies on neither graph"),
    S("1.22", lambda r: count_real_solutions(r, 0, shape="standard", a=3, b=-15,
                                             c=18)),

    # ---------------------------------------------------------- medium (33)
    S("2.1", lambda r: graph_count(r, 0, a=F(1, 4), h=2, k=-4, m=F(1, 4), b=1,
                                   window=(-10, 10, -10, 10), step=5,
                                   wrongs=["zero", "one", "three"])),
    S("2.2", lambda r: curve_line_system(
        r, 0, curve=T([(1, "y")], [(1, "x2"), (1, "x")]),
        line=T([(1, "y")], [(1, "x"), (1, "")]), ask="could_be_x",
        frame="could_be_x", fmt="mcq", branch="lo", sign_rule=False,
        wrongs=["y_instead", "near_up_3", "near_up_4"])),
    S("2.3", lambda r: quadratic_formula(r, 0, a=1, b=-1, c=-1, style="pair",
                                         frame="values",
                                         wrongs=["bracketing_pair", "disc_rounded",
                                                 "sign_b"])),
    S("2.4", lambda r: factored_equation(r, 0, roots=[4, -2, 1], ask="product",
                                         fmt="mcq",
                                         wrongs=["abs_key", "sum_instead",
                                                 "neg_sum"])),
    S("2.5", lambda r: rational_linear(r, 0, p=2, a=1, b=5, r=1, m=1, ask="solution",
                                       fmt="mcq",
                                       wrongs=["zero", "drop_bracket",
                                               "denominator_number"])),
    S("2.6", lambda r: curve_line_system(
        r, 0, curve=T([(1, "y")], [(1, "x2"), (-4, "x"), (4, "")]),
        line=T([(1, "y")], [(4, ""), (-1, "x")]), ask="one_possible_x",
        frame="one_possible_x", fmt="spr")),
    S("2.7", lambda r: isolate_factor(
        r, 0, target="p", left=[(1, "s")], k=F(3, 2), top=["p"], bottom=[],
        story="An oceanographer uses the equation {eq} to model the speed s, in "
              "knots, of an ocean wave, where p represents the period of the wave, "
              "in seconds. Which of the following represents the period of the "
              "wave in terms of the speed of the wave?",
        wrongs=["keep_coef", "recip_added", "coef_added"])),
    S("2.8", lambda r: curve_line_system(
        r, 0, curve=("square", 1), line=T([(1, "y")], [(2, "x"), (-3, "")]),
        ask="y_coordinate", frame="y_coordinate", fmt="spr")),
    S("2.9", lambda r: cancel_squares(r, 0, p=2, r=3, k=10, ask="which", fmt="mcq",
                                      wrongs=["zero", "minus_p", "minus_sum"])),
    S("2.10", lambda r: integer_roots_constant(r, 0, k=12, named="a")),
    S("2.11", lambda r: isolate_sum(
        r, 0, target="T", coef=F(303, 500), extras=[(F(3313, 10), "")],
        other=[(1, "v")], order="target_right", style="dec",
        story="The speed of sound in dry air, v, can be modeled by the formula "
              "{eq}, where T is the temperature in degrees Celsius and v is "
              "measured in meters per second. Which of the following correctly "
              "expresses T in terms of v ?",
        wrongs=["swap_over_sign", "swap_over", "sign"])),
    S("2.12", lambda r: isolate_denominator(
        r, 0, target="H", left=[(1, "V_B")], head=0, top=(1, "V_P"), sigma=-1,
        const=1,
        story="Blood volume, V_B, in a human can be determined using the equation "
              "{eq}, where V_P is the plasma volume and H is the hematocrit (the "
              "fraction of blood volume that is red blood cells). Which of the "
              "following correctly expresses the hematocrit in terms of the blood "
              "volume and the plasma volume?",
        wrongs=["invert", "flip_ratio_plus", "difference"])),
    S("2.13", lambda r: sum_product(r, 0, total=17, product=72,
                                    ask="one_solution_x", fmt="spr")),
    S("2.14", lambda r: curve_line_system(
        r, 0, curve=T([(1, "x2")], [(6, "x"), (1, "y")]),
        line=T([(1, "y")], [(-6, "x"), (36, "")]), ask="possible_xy",
        frame="possible_xy", fmt="mcq", branch="hi",
        wrongs=["x_only", "double_x", "square"])),
    S("2.15", lambda r: quadratic_solve(r, 0, a=1, b=1, c=-12, ask="a_positive",
                                        fmt="spr")),
    S("2.16", lambda r: isolate_bracket(
        r, 0, target="P", left=[(1, "T")], c=F(1, 100),
        inner=[(1, "P"), (-40000, "")], style="dec",
        story="In a city, the property tax T, in dollars, is calculated using the "
              "formula above, where P is the value of the property, in dollars. "
              "Which of the following expresses the value of the property in terms "
              "of the property tax?",
        wrongs=["const_scaled_sign", "const_scaled", "sign"])),
    S("2.17", lambda r: isolate_factor(
        r, 0, target="T", left=("square", "v"), k=1, top=["L", "T"], bottom=["m"],
        order=["m", "v²", "L"],
        story="The formula above expresses the square of the speed v of a wave "
              "moving along a string in terms of tension T, mass m, and length L "
              "of the string. What is T in terms of m, v, and L ?",
        wrongs=["denom_swap", "left_below", "invert"])),
    S("2.18", lambda r: curve_line_system(
        r, 0, curve=T([(1, "y")], [(1, "x2")]), line=("bracket", 2, 6, 2, 3),
        ask="positive_xy", frame="positive_xy", fmt="mcq",
        wrongs=["line_coef", "line_const", "line_const_square"])),
    S("2.19", lambda r: quadratic_formula(r, 0, a=6, b=5, c=-7, style="formula",
                                          frame="solutions",
                                          wrongs=["b_as_a", "disc_sign", "both"])),
    S("2.20", lambda r: curve_line_system(
        r, 0, curve=T([(1, "y")], [(1, "x2"), (-1, "")]),
        line=T([(1, "y")], [(3, "")]), ask="both_pairs", frame="both_pairs",
        wrongs=["no_constant", "y_as_x", "sign_const"])),
    S("2.21", lambda r: square_equation(r, 0, shape="plain", a=38, k=342,
                                        rhs_style="scaled", ask="negative",
                                        fmt="spr")),
    S("2.22", lambda r: symbolic_intersections(r, 0, pair=("a", "c"), sign=-1,
                                               line="sum")),
    S("2.23", lambda r: quadratic_solve(r, 0, a=7, b=-20, c=-32, ask="positive",
                                        fmt="spr")),
    S("2.24", lambda r: isolate_factor(r, 0, target="w", left=[(1, "v")],
                                       k=F(-1, 150), top=["w"], bottom=["x"],
                                       frame="relates_distinct",
                                       wrongs=["divide_instead",
                                               "divide_instead_flip", "coef_sum"])),
    S("2.25", lambda r: rational_quadratic(r, 0, shape="cross", n=55, b=6,
                                           ask="positive", fmt="spr")),
    S("2.26", lambda r: isolate_sum(r, 0, target="k", coef=5, extras=[(14, "j")],
                                    other=[(1, "m")], frame="relates_plain",
                                    wrongs=["first_only_coef", "reversed",
                                            "multiply_first"])),
    S("2.27", lambda r: isolate_denominator(
        r, 0, target="n", left=[(1, "p")], head=9, top=(14, ""),
        story="The given equation relates the numbers p and n, where n is not equal "
              "to 0 and p > 9. Which equation correctly expresses n in terms of p?",
        wrongs=["invert", "split", "split_minus"])),
    S("2.28", lambda r: curve_line_system(
        r, 0, curve=("factored", 2, -4), line=T([(1, "y")], [(6, "x"), (-12, "")]),
        ask="the_pair", frame="the_pair",
        wrongs=["roots_as_pair", "roots_swapped", "zero_and_root"])),
    S("2.29", lambda r: quadratic_solve(r, 0, a=-4, b=-7, c=0, rc=-36, ask="positive",
                                        fmt="mcq",
                                        wrongs=["b_over_a", "other_abs",
                                                "b_itself"])),
    S("2.30", lambda r: isolate_factor(r, 0, target="x", left=[(1, "b"), (-72, "")],
                                       k=1, top=["x"], bottom=["y"], distribute=True,
                                       frame="relates_positive",
                                       wrongs=["no_distribute", "partial",
                                               "partial_over"])),
    S("2.31", lambda r: scaled_quadratic(r, 0, shape="cross", n=42, k=7, fmt="mcq",
                                         wrongs=["x_squared", "coef_itself",
                                                 "product"])),
    S("2.32", lambda r: quadratic_solve(r, 0, a=1, b=-5, c=-24, ask="sum",
                                        fmt="spr")),

    # ------------------------------------------------------------ hard (30)
    S("3.1", lambda r: tangent_constant(r, 0, p=2, height=F(9, 2), a=-4, ask="coef",
                                        named="b")),
    S("3.2", lambda r: curve_line_system(
        r, 0, curve=T([(1, "x"), (1, "y")], [(1, "x2"), (-3, "")]),
        line=T([(1, "x"), (-1, "y")], [(1, "")]), ask="which_pair",
        frame="which_pair_plain", branch="hi",
        wrongs=["curve_only_radical", "line_sign", "line_sign_radical"])),
    S("3.3", lambda r: rational_quadratic(r, 0, shape="square", h=5, k=4, fmt="mcq",
                                          wrongs=["half_shift", "shift_minus",
                                                  "shift_added"])),
    S("3.4", lambda r: isolate_sum(
        r, 0, target="v_f", coef=1, divisor=5, extras=[(-12, "")],
        other=[(1, "a")], order="target_right", fmt="spr",
        story="During a 5-second time interval, the average acceleration a, in "
              "meters per second squared, of an object with an initial velocity of "
              "12 meters per second is defined by the equation {eq}, where v_f is "
              "the final velocity of the object in meters per second. If the "
              "equation is rewritten in the form v_f = xa + y, where x and y are "
              "constants, what is the value of x ?")),
    S("3.5", lambda r: quadratic_formula(r, 0, a=2, b=0, c=-2, rb=2, rc=3,
                                         style="single", frame="which_above",
                                         wrongs=["minus_b", "no_denominator",
                                                 "first_over_only"])),
    S("3.6", lambda r: scaled_quadratic(r, 0, shape="divide", k=3, b=-6, c=-15,
                                        fmt="spr")),
    S("3.7", lambda r: discriminant_constant(r, 0, a=2, b=-4, unknown="t",
                                             slot="constant", condition="none",
                                             side="right", value=-3,
                                             wrongs=["wrong_side_1", "mirror_1",
                                                     "mirror_2"])),
    S("3.8", lambda r: radical_equation(r, 0, shape="linear", a=2, b=6, d=4, e=3,
                                        ask="solution_set",
                                        wrongs=["extraneous_only", "both",
                                                "both_and_zero"])),
    S("3.9", lambda r: function_meets(r, 0, a=F(-1, 2), h=4, k=10, m=-1, b=10,
                                      window=(0, 9, 0, 12), step=1)),
    S("3.10", lambda r: discriminant_constant(r, 0, a=-16, b=-8, unknown="c",
                                              condition="one", fmt="spr")),
    S("3.11", lambda r: count_real_solutions(r, 0, shape="square", h=1, k=-4)),
    S("3.12", lambda r: curve_line_system(
        r, 0, curve=T([(1, "y")], [(1, "x2"), (2, "x"), (1, "")]),
        line=T([(1, "x"), (1, "y"), (1, "")], []), ask="sum_y", frame="sum_y",
        fmt="mcq", sign_rule=False, wrongs=["sum_x", "x_one", "negate"])),
    S("3.13", lambda r: isolate_denominator(
        r, 0, target="t", left=[(1, "u"), (-3, "")], head=0, top=(6, ""), sigma=1,
        const=-2, combine=True, story="If {eq}, what is t in terms of u ?",
        wrongs=["reciprocal_only", "mixed_combine", "unit_numerator"])),
    S("3.14", lambda r: secant_slope(r, 0, a=1, b=0, c=-9, x1=1, x2=5, fmt="mcq",
                                     wrongs=["negate", "sign_first",
                                             "sign_first_neg"])),
    S("3.15", lambda r: isolate_bracket(
        r, 0, target="H", left=[(1, "D")], head=[(1, "T")], c=F(-9, 25),
        inner=[(100, ""), (-1, "H")],
        story="The formula above can be used to approximate the dew point D, in "
              "degrees Fahrenheit, given the temperature T, in degrees Fahrenheit, "
              "and the relative humidity of H percent, where H > 50. Which of the "
              "following expresses the relative humidity in terms of the "
              "temperature and the dew point?",
        wrongs=["sign", "both_signs", "both_signs_sign"])),
    S("3.16", lambda r: curve_line_system(
        r, 0, curve=T([(1, "y")], [(3, "x2"), (-14, "x")]),
        line=T([(1, "y")], [(1, "x")]), ask="meets_at", frame="meets_at",
        fmt="spr")),
    S("3.17", lambda r: quadratic_solve(r, 0, a=1, b=-40, c=-10, ask="sum",
                                        fmt="mcq",
                                        wrongs=["zero_sum", "c_half", "c_abs"])),
    S("3.18", lambda r: count_system_solutions(r, 0, a=1, b=3, c=-7, m=5, d=-8,
                                               labels="sentences")),
    S("3.19", lambda r: rational_combine(r, 0, A=4, B=2, C=1, h=3, fmt="mcq",
                                         wrongs=["excluded", "negate",
                                                 "other_excluded"])),
    S("3.20", lambda r: curve_line_system(
        r, 0, curve=T([(1, "x2"), (1, "y"), (7, "")], [(7, "")]),
        line=T([(20, "x"), (100, ""), (-1, "y")], []), ask="solution_x",
        frame="solution_x", fmt="spr")),
    S("3.21", lambda r: shared_factor(r, 0, a=5, k=7, b=15, m=17, ask="sum",
                                      fmt="spr")),
    S("3.22", lambda r: paired_quadratics(r, 0, b1=6, c1=7, b2=8, c2=8, fmt="spr")),
    S("3.23", lambda r: tangent_constant(r, 0, p=2, a=-2, b=9, ask="height",
                                         named="c")),
    S("3.24", lambda r: curve_line_system(
        r, 0, curve=T([(2, "x2")], [(1, "y"), (341, "")]),
        line=T([(8, "x"), (1, "y")], [(-11, "")]), ask="intersect_x",
        frame="intersect_x", fmt="mcq", branch="lo",
        wrongs=["const", "curve_coef", "line_coef"])),
    S("3.25", lambda r: discriminant_constant(r, 0, a=64, c=25, unknown="b",
                                              slot="middle", condition="more",
                                              value=-91,
                                              wrongs=["boundary_mirror", "root_c",
                                                      "half_boundary"])),
    S("3.26", lambda r: tangent_point(r, 0, a=2, b=-21, c=64, m=3, named="a",
                                      fmt="mcq",
                                      wrongs=["negate", "root_const",
                                              "neg_root_const"])),
    S("3.27", lambda r: absolute_equation(r, 0, a=2, b=3, h=4, reversed_inner=True,
                                          k=25, ask="positive", fmt="spr")),
    S("3.28", lambda r: product_roots_constant(r, 0, p=4, u=3, v=5, g=45, w=2, s=16,
                                               t=6, fmt="spr")),
    S("3.29", lambda r: discriminant_constant(r, 0, a=-2, b=20, unknown="c",
                                              condition="one", fmt="mcq", gap=18,
                                              wrongs=["two_solutions",
                                                      "no_solutions", "zero"])),
    S("3.30", lambda r: square_equation(r, 0, shape="shifted", h=-47, k=1, ask="sum",
                                        fmt="spr")),
]

EXCLUDED = {
    "2.33": "the four options are themselves graphs -- four drawn xy-planes, each "
            "with a parabola and a line -- so the question is which picture the "
            "printed system makes, and an option that is a picture cannot be "
            "generated as an option string or read back as mathematics",
}
