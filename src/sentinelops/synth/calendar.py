"""The twelve-month simulated calendar, and where "now" sits in it.

Period arithmetic itself moved to `sentinelops.periods` in slice 4 — S1 needs it
at runtime and must not import the test-data package to get it. This module
re-exports it so the generator's imports read the same as before, and keeps the
one thing that genuinely is corpus configuration: the vantage point.
"""

from __future__ import annotations

from datetime import date

from ..periods import Period, all_periods, due_date, periods_for

#: The simulated "today" the corpus is generated against — the vantage point of
#: an auditor reviewing calendar year 2026 from the following spring. It sits
#: after the last period closes *and* after its grace window, so every 2026
#: check has had its chance: anything still unmet by now is genuinely overdue,
#: not merely not-yet-due. Evidence for 2026-Q4 is filed in January 2027 and its
#: remediation later still, which is why "today" is not inside 2026.
SIMULATED_TODAY = date(2027, 3, 31)

__all__ = ["Period", "SIMULATED_TODAY", "all_periods", "due_date", "periods_for"]
