"""The twelve-month simulated calendar.

Periods only — not CheckInstances. S1 (slice 4) turns periods into instances;
the generator's job is to say which periods exist and when evidence for each was
due, so that recurrence, overdue and escalation have something to happen to.

    monthly    2026-01 .. 2026-12   due `grace_days` after month end
    quarterly  2026-Q1 .. 2026-Q4   due `grace_days` after quarter end
    annual     2026                 due `grace_days` after year end
"""

from __future__ import annotations

from calendar import monthrange
from dataclasses import dataclass
from datetime import date, timedelta

#: The simulated "today" the corpus is generated against — the vantage point of
#: an auditor reviewing calendar year 2026 from the following spring. It sits
#: after the last period closes *and* after its grace window, so every 2026
#: check has had its chance: anything still unmet by now is genuinely overdue,
#: not merely not-yet-due. Evidence for 2026-Q4 is filed in January 2027 and its
#: remediation later still, which is why "today" is not inside 2026.
SIMULATED_TODAY = date(2027, 3, 31)


@dataclass(frozen=True)
class Period:
    label: str
    start: date
    end: date


def _month(year: int, month: int) -> Period:
    last = monthrange(year, month)[1]
    return Period(f"{year}-{month:02d}", date(year, month, 1), date(year, month, last))


def _quarter(year: int, q: int) -> Period:
    first_month = 3 * (q - 1) + 1
    last_month = first_month + 2
    last_day = monthrange(year, last_month)[1]
    return Period(
        f"{year}-Q{q}",
        date(year, first_month, 1),
        date(year, last_month, last_day),
    )


def periods_for(frequency: str, year: int) -> list[Period]:
    if frequency == "monthly":
        return [_month(year, m) for m in range(1, 13)]
    if frequency == "quarterly":
        return [_quarter(year, q) for q in range(1, 5)]
    if frequency == "annual":
        return [Period(str(year), date(year, 1, 1), date(year, 12, 31))]
    raise ValueError(f"unknown frequency {frequency!r}")


def due_date(period: Period, grace_days: int) -> date:
    """Evidence is due `grace_days` after the period it covers has closed."""
    return period.end + timedelta(days=grace_days)


def all_periods(year: int) -> dict[str, list[Period]]:
    return {f: periods_for(f, year) for f in ("monthly", "quarterly", "annual")}
