"""The eighteen-month simulated calendar, and where "now" sits inside it.

Period arithmetic itself moved to `sentinelops.periods` in slice 4 — S1 needs it
at runtime and must not import the test-data package to get it. This module
re-exports it so the generator's imports read the same as before, and keeps the
one thing that genuinely is corpus configuration: the vantage point.
"""

from __future__ import annotations

from datetime import date

from ..periods import (
    Period, all_periods, due_date, period_from_label, periods_for,
)

#: The simulated "today", and it sits **inside** the eighteen-month window
#: rather than after it.
#:
#: This matters more than it looks. With "today" past the end of the window,
#: every obligation had already fallen due, every open finding was months
#: overdue, and the ageing buckets collapsed into a single 90+ column — which is
#: not what a compliance portfolio looks like on any real Tuesday. Worse, the
#: "due in the next thirty days" panel had nothing to show, because nothing was
#: ever upcoming.
#:
#: Placed here, the corpus has all three states at once: periods that closed and
#: were evidenced, findings raised recently and not yet overdue, and obligations
#: that have not fallen due yet. Fifteen months of history behind it, three
#: months of window still ahead.
SIMULATED_TODAY = date(2027, 4, 15)

__all__ = ["Period", "SIMULATED_TODAY", "all_periods", "due_date",
           "period_from_label", "periods_for"]
