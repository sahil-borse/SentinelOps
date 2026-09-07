"""The eighteen-month simulated calendar, and where "now" sits in it.

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

#: The simulated "today" the corpus is generated against — the vantage point of
#: an auditor looking back over eighteen months, from January 2026 to the end of
#: June 2027. It sits after the last period closes *and* after its grace window,
#: so every check in the window has had its chance: anything still unmet by now
#: is genuinely overdue rather than merely not-yet-due. Evidence for 2027-Q2 is
#: filed in July and its remediation later still, which is why "today" is well
#: clear of the window's end rather than on it.
SIMULATED_TODAY = date(2027, 9, 30)

__all__ = ["Period", "SIMULATED_TODAY", "all_periods", "due_date",
           "period_from_label", "periods_for"]
