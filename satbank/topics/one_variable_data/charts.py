"""Where this topic's paired charts went.

Both moved into `satbank/plot.py` as `boxplots` and `histograms`: drawing two
distributions to one scale is not a One-Variable Data problem, it is what any
topic comparing two distributions needs, and Two-Variable Data will want it
next. Kept as names so this topic's templates read the way they were written.
"""

from ...plot import boxplots as paired_boxplot, histograms as paired_histogram

__all__ = ["paired_boxplot", "paired_histogram"]
