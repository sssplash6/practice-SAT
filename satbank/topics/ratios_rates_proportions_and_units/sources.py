"""The 57 official Ratios, Rates, Proportional Relationships, and Units items,
encoded as the parameters that reproduce them.

No answer appears here. The answers live in
`material/keys/ratios_rates_proportions_and_units.json`, read from the College
Board PDF's own text layer, and the check drives each template with the
numbers below and asks whether the engine lands on them. A template whose
arithmetic is wrong cannot be made to pass by writing the answer down.

The one thing a source item does say about its own options is whether they
carry a unit: 2.9 prints "25 meters per second" on every choice and every
other item in the set leaves the unit in the stem, so `unit=` is set on that
item alone rather than guessed for the template.
"""

from __future__ import annotations

from fractions import Fraction as F

from ...topic import S, Source
from .families.ratios import (chain_unknown, dimension_shift, equivalent,
                              expression, mix_statement, multiple, partner,
                              repeated_factor, similar_rect, simplify,
                              table_constant)
from .families.rates import (TREE_TABLE, exchange_fee, gap, growth_table,
                             rate_convert, rate_product, table_unit_price,
                             unit_rate)
from .families.units import convert, convert_chain, cube_density, pop_density

# --------------------------------------------------------------- the units
# (plural small, singular small, singular big, plural big, factor)
INCH_YARD = ("inches", "inch", "yard", "yards", 36)
FOOT_YARD = ("feet", "foot", "yard", "yards", 3)
GRAM_KILO = ("grams", "gram", "kilogram", "kilograms", 1000)
TSP_TBSP = ("teaspoons", "teaspoon", "tablespoon", "tablespoons", 3)
YARD_MILE = ("yards", "yard", "mile", "miles", 1760)

FURLONG = ("furlongs", "furlong", "yards", "yard", "feet", "foot", 220, 3)
QUART = ("quarts", "quart", "cups", "cup", "fluid ounces", "fluid ounce", 4, 8)

# ------------------------------------------------------------- the contexts
PENS = ("pens", "black pens", "red pens", "box")
CARDS = ("cards", "red cards", "blue cards", "deck")
LIGHTNING = ("m", "miles", "k", "seconds",
             "For a person m miles from a flash of lightning, the length of the "
             "time interval from the moment the person sees the lightning to the "
             "moment the person hears the thunder is k seconds.")
BUTTERFLIES = ("monarch butterflies", "a group of monarch butterflies",
               "Chicago, Illinois", "Michoacán, Mexico", "butterfly")
TURBINE = ("wind turbine", "revolutions")
EVENT = ("Makayla", "an event")
ORANGES = ("oranges", "pound")
GLASS = ("drinking glass", "Jenny")
KANGAROO = ("kangaroo", "mass")
BICYCLE = ("A participant in a bicycle race completes the race with an average "
           "speed of", "average speed")
TRIATHLON = ("A triathlon is a multisport race consisting of three different "
             "legs. A triathlon participant completed the cycling leg with an "
             "average speed of", "average speed")
COMPETITION = ("A competition consisted of four different events. One "
               "participant completed the first event with an average speed of",
               "average speed")
INSECT = ("An insect", "insect")
PARK = ("park", "A certain park")
MUFFINS = ("chocolate", "chocolate muffins", "muffin")
PESOS = ("pesos", "peso", "Marta", "she")
TILLY = ("Tilly", "she")
TANYA = ("Tanya", "she")
CRATES = ("objects", "kilograms")
ISS = ("The International Space Station orbits Earth", "space station")
REVERE = ("On April 18, 1775, Paul Revere set off on his midnight ride from "
          "Charlestown to Lexington. If he had ridden straight to Lexington "
          "without stopping, he would have traveled", "his horse")
BEESWAX = ("Pure beeswax", "beeswax")
EGG_MILK = ("1 large egg", "1 cup of milk", "protein", "grams")
VENUS_JUPITER = ("Venus", "Jupiter")
ICELAND = ("Iceland", 1990, 2014)
WOOD = ("a certain type of wood", "kilograms", "cubic meter", "meter", "meters")
SUBSTANCE = ("a certain solid substance", "kilograms", "cubic meter", "meter",
             "meters")
PUMICE = ("To study fluctuations in composition, samples of pumice were taken "
          "from", "locations", "pumice")
TRUNKS = ("To study the moisture content in a group of trees, samples from the "
          "trunk of each tree were taken from", "trees", "wood")
PAINT = ("green paint", "blue paint", "yellow paint", "ounces", "Anita", "She")
JEREMY = ("Jeremy", "his")

ALL: list[Source] = [
    # ------------------------------------------------------------ set 1
    S("1.1", lambda r: partner(r, 0, a=1, b=5, n=25, given="second",
                               frame="estimate", ctx=LIGHTNING, fmt="mcq")),
    S("1.2", lambda r: unit_rate(r, 0, frame="migration", total=2100, count=120,
                                 ctx=BUTTERFLIES, fmt="mcq")),
    S("1.3", lambda r: partner(r, 0, a=8, b=1, n=40, given="first",
                               frame="objects", ctx=PENS, fmt="mcq")),
    S("1.4", lambda r: pop_density(r, 0, ask="area", density=290, people=92800,
                                   place="Worthington", fmt="mcq")),
    S("1.5", lambda r: unit_rate(r, 0, frame="turbine", total=900, count=50,
                                 ctx=TURBINE, fmt="mcq")),
    S("1.6", lambda r: table_constant(r, 0, ratio=4, xs=[1, 3, 5], last=40,
                                      letters=("x", "y"), fmt="mcq")),
    S("1.7", lambda r: partner(r, 0, a=1, b=2, n=10, given="first",
                               frame="letters", ctx=("t", "u"), fmt="mcq")),
    S("1.8", lambda r: convert(r, 0, n=612, op="div", units=INCH_YARD,
                               frame="bare", fmt="mcq")),
    S("1.9", lambda r: simplify(r, 0, n1=7, n2=28, ctx=CARDS, owner="Shaquan")),
    S("1.10", lambda r: convert(r, 0, n=28, op="mul", units=GRAM_KILO,
                                frame="object", ctx=KANGAROO, fmt="mcq")),
    S("1.11", lambda r: gap(r, 0, frame="planet", base=100, low=F(9, 10),
                            high=F(23, 10), ctx=VENUS_JUPITER, fmt="mcq")),
    S("1.12", lambda r: convert(r, 0, n=34, op="mul", units=FOOT_YARD,
                                frame="bare", fmt="spr")),
    S("1.13", lambda r: rate_product(r, 0, frame="recipe", first=F(5, 2),
                                     second=48, ctx=MUFFINS, fmt="mcq")),
    S("1.14", lambda r: exchange_fee(r, 0, amount=7500, rate=F(75, 1000), fee=2,
                                     ctx=PESOS, fmt="mcq")),
    S("1.15", lambda r: unit_rate(r, 0, frame="room", total=5400, per=8,
                                  ctx=EVENT, fmt="mcq")),
    S("1.16", lambda r: expression(r, 0, form="substitute", n=2, partner=4,
                                   ctx=("t", "u"))),
    S("1.17", lambda r: convert(r, 0, n=44, op="mul", units=TSP_TBSP,
                                frame="bare", stmt="small_first", fmt="mcq")),
    S("1.18", lambda r: unit_rate(r, 0, frame="price", per=11, count=6,
                                  ctx=ORANGES, fmt="spr")),
    S("1.19", lambda r: unit_rate(r, 0, frame="speed", per=6, total=24, fmt="spr")),
    S("1.20", lambda r: convert(r, 0, n=24816, op="div", units=YARD_MILE,
                                frame="rate", ctx=BICYCLE, fmt="spr")),
    S("1.21", lambda r: expression(r, 0, form="scale_pay", n=39, var="p",
                                   partner="w", ctx=TILLY)),
    S("1.22", lambda r: unit_rate(r, 0, frame="speed", per=12, total=108,
                                  fmt="mcq")),
    S("1.23", lambda r: unit_rate(r, 0, frame="buy", per=3, total=27,
                                  ctx=ORANGES, fmt="spr")),

    # ------------------------------------------------------------ set 2
    S("2.1", lambda r: rate_convert(r, 0, frame="rate", value=F(119, 25),
                                    per_from="second", per_to="hour",
                                    unit_from="miles", ctx=ISS, fmt="mcq")),
    S("2.2", lambda r: gap(r, 0, frame="density", base=100250, low=F(5, 2),
                           high=F(33, 10), ctx=ICELAND, fmt="mcq")),
    S("2.3", lambda r: rate_product(r, 0, frame="density_price", first=F(555, 1000),
                                    second=8, ctx=BEESWAX, fmt="spr")),
    S("2.4", lambda r: rate_convert(r, 0, frame="trip", dist=11, time=26,
                                    ctx=REVERE, fmt="spr")),
    S("2.5", lambda r: similar_rect(r, 0, l1=15, l2=20, var="w")),
    S("2.6", lambda r: expression(r, 0, form="hourly", n=3, rate=F(27, 2),
                                  var="z", ctx=TANYA)),
    S("2.7", lambda r: unit_rate(r, 0, frame="fill", per=16, total=128, vol=473,
                                 ctx=GLASS, fmt="mcq")),
    S("2.8", lambda r: gap(r, 0, frame="moons", base=29, low=252, high=287,
                           ctx="a planet", fmt="spr")),
    S("2.9", lambda r: rate_convert(r, 0, frame="rate", value=90, per_from="hour",
                                    per_to="second", factor=1000,
                                    unit_from="kilometers", unit_to="meters",
                                    unit="meters per second", fmt="mcq")),
    S("2.10", lambda r: convert_chain(r, 0, n=61, units=FURLONG, fmt="spr")),
    S("2.11", lambda r: table_unit_price(r, 0, amounts=(6, 8),
                                         costs=(F(36, 100), F(24, 100)),
                                         ctx=EGG_MILK)),
    S("2.12", lambda r: pop_density(r, 0, ask="area", density=230, people=85100,
                                    place="Cedar County", fmt="spr")),
    S("2.13", lambda r: convert_chain(r, 0, n=112, units=FURLONG, fmt="spr")),
    S("2.14", lambda r: equivalent(r, 0, ask="factor", p=11, r=12, n=17,
                                   ctx=("j", "k"), fmt="spr")),
    S("2.15", lambda r: convert(r, 0, n=14, op="div", units=TSP_TBSP,
                                frame="bare", stmt="small_first", fmt="spr")),
    S("2.16", lambda r: convert(r, 0, n=F(197, 10), op="mul", units=YARD_MILE,
                                frame="rate", n_places=3, ctx=TRIATHLON,
                                fmt="spr")),
    S("2.17", lambda r: pop_density(r, 0, ask="density", total=F(921, 10),
                                    water=F(113, 10), people=621000, year=2010,
                                    place="a coastal city", fmt="mcq")),
    S("2.18", lambda r: multiple(r, 0, rate=55, big=9, small=3, var="k")),
    S("2.19", lambda r: convert(r, 0, n=F(203, 10), op="mul", units=YARD_MILE,
                                frame="rate", n_places=3, ctx=COMPETITION,
                                fmt="spr")),
    S("2.20", lambda r: convert_chain(r, 0, n=76, units=QUART, stmt="reverse",
                                      fmt="spr")),
    S("2.21", lambda r: convert(r, 0, n=F(3, 20), op="div", units=FOOT_YARD,
                                frame="rate", stmt="small_first", style="frac",
                                ctx=INSECT, fmt="mcq")),
    S("2.22", lambda r: equivalent(r, 0, ask="term", first=140, c=4, d=28,
                                   fmt="spr")),
    S("2.23", lambda r: dimension_shift(r, 0, length=35, width=10, change=7,
                                        up=True, moved="width")),
    S("2.24", lambda r: expression(r, 0, form="scale_mass", n=146, var="t",
                                   partner="r", ctx=CRATES)),

    # ------------------------------------------------------------ set 3
    S("3.1", lambda r: growth_table(r, 0, fast="Pin oak", slow="White birch",
                                    years=10, feet=1, species=TREE_TABLE)),
    S("3.2", lambda r: repeated_factor(r, 0, total=480, years=4, factor=2,
                                       start_year=2001, ctx=JEREMY, fmt="spr")),
    S("3.3", lambda r: rate_product(r, 0, frame="power_hours", first=4952,
                                    second=24, other=11037, fmt="mcq")),
    S("3.4", lambda r: chain_unknown(r, 0, c=4, first=F(67, 10), second=F(268, 10),
                                     fmt="spr")),
    S("3.5", lambda r: cube_density(r, 0, ask="edge", density=353, mass=345,
                                    places=2, ctx=WOOD, fmt="mcq")),
    S("3.6", lambda r: mix_statement(r, 0, first=2, second=3, again=5, ctx=PAINT)),
    S("3.7", lambda r: cube_density(r, 0, ask="mass", frame="sample", edge=3,
                                    density=F(230, 1000), sites=29, edge_places=3,
                                    density_places=3, ctx=PUMICE, fmt="spr")),
    S("3.8", lambda r: convert(r, 0, n=11863808, op="div", power=2,
                               units=YARD_MILE, frame="area", ctx=PARK,
                               fmt="mcq")),
    S("3.9", lambda r: cube_density(r, 0, ask="mass", frame="solid", density=813,
                                    edge=F(3, 5), places=0, ctx=SUBSTANCE,
                                    fmt="mcq")),
    S("3.10", lambda r: cube_density(r, 0, ask="density", frame="sample", edge=2,
                                     mass=F(256, 100), sites=25, edge_places=2,
                                     ctx=TRUNKS, fmt="spr")),
]

EXCLUDED: dict[str, str] = {}
