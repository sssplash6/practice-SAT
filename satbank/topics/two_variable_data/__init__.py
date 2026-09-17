"""Problem-Solving and Data Analysis -> Two-Variable Data: Models and Scatterplots.

Eighteen templates over the 39 official items. Almost every item is a question
about a picture, so the picture is the thing that has to be right: `charts.py`
draws to a stated window with stated gridlines, `common.fit_scatter` builds the
scatter so that the drawn line really is its least-squares line, and
`option_check.py` reads both back out of the finished SVG and refits.

The two guards that decide whether a chart item is answerable at all live in
`common.py`. `separated` refuses a draw whose options are closer together than
the chart's own gridlines; `closest_guard` refuses one whose true value does
not clearly pick a single printed answer.
"""

from __future__ import annotations

from ...topic import Topic
from .audit import AUDITS
from .families import describe as D
from .families import fit as F
from .families import models as M
from .families import read as R
from .sources import ALL, EXCLUDED

TEMPLATES = {
    "tvdata.point_read": R.point_read,
    "tvdata.interval_change": R.interval_change,
    "tvdata.series_extreme": R.series_extreme,
    "tvdata.curve_read": R.curve_read,
    "tvdata.rate_of_change": R.rate_of_change,
    "tvdata.predict_from_line": F.predict_from_line,
    "tvdata.fit_slope": F.fit_slope,
    "tvdata.fit_equation": F.fit_equation,
    "tvdata.residual": F.residual,
    "tvdata.slope_scaled": F.slope_scaled,
    "tvdata.association": D.association,
    "tvdata.interpret_slope": D.interpret_slope,
    "tvdata.model_type": D.model_type,
    "tvdata.graph_statement": D.graph_statement,
    "tvdata.best_model": M.best_model,
    "tvdata.growth_compare": M.growth_compare,
    "tvdata.invest_compare": M.invest_compare,
    "tvdata.nonlinear_table": M.nonlinear_table,
}

TOPIC = Topic(
    slug="two_variable_data",
    name="Two-Variable Data: Models and Scatterplots",
    domain="Problem-Solving and Data Analysis",
    templates=TEMPLATES,
    audits=AUDITS,
    sources=ALL,
    excluded=EXCLUDED,
)
