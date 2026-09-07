"""Reporting periods and due dates.

Pipeline logic, not synthetic data: S1 needs to know that a quarterly control
covering 2026-Q2 was due fifteen days after 30 June regardless of where its
evidence came from. Slice 2 wrote this inside `synth/` because the generator was
the only caller; `synth.calendar` now re-exports from here so the engine does
not have to import the test-data package to know what a quarter is.

    monthly    2026-01 .. 2026-12   due `grace_days` after month end
    quarterly  2026-Q1 .. 2026-Q4   due `grace_days` after quarter end
    annual     2026                 due `grace_days` after year end

Section 10 asks for eighteen months, which is more than one calendar year, so
`periods_for` also takes a `through` year and returns every period from the
start of `year` to the end of `through`. An annual control over a window that is
not a whole number of years is the awkward case: it yields one period per
calendar year touched, and the final one is short. That is what actually happens
to an annual obligation when you look at a year and a half of it, and rounding it
away would make the eighteen-month corpus quietly disagree with its own calendar.
"""

from __future__ import annotations

from calendar import monthrange
from dataclasses import dataclass
from datetime import date, timedelta


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


def periods_for(
    frequency: str, year: int, through: int | None = None,
    *, last_month: int = 12,
) -> list[Period]:
    """Every period of `frequency` from the start of `year` to the end of the
    window. `through` defaults to `year`, and `last_month` truncates the final
    calendar year — so (2026, through=2027, last_month=6) is eighteen months.
    """
    through = year if through is None else through
    if through < year:
        raise ValueError(f"window ends ({through}) before it starts ({year})")

    periods: list[Period] = []
    for current in range(year, through + 1):
        final = last_month if current == through else 12
        if frequency == "monthly":
            periods += [_month(current, m) for m in range(1, final + 1)]
        elif frequency == "quarterly":
            periods += [
                _quarter(current, q) for q in range(1, 5)
                if 3 * (q - 1) + 1 <= final
            ]
        elif frequency == "annual":
            end_month = final
            periods.append(Period(
                str(current) if end_month == 12 else f"{current}-H1",
                date(current, 1, 1),
                date(current, end_month, monthrange(current, end_month)[1]),
            ))
        else:
            raise ValueError(f"unknown frequency {frequency!r}")
    return periods


def period_from_label(label: str) -> Period:
    """Rebuild a period from its own label, with no window to consult.

    Callers that hold a label and need its dates should not also have to know
    which eighteen-month window it came from. Every label carries its year, so
    the lookup is unnecessary — and the single-year `periods_for(freq, year)`
    call it replaces silently found nothing once the corpus crossed a year end.
    """
    if "-Q" in label:
        year, quarter = label.split("-Q")
        return _quarter(int(year), int(quarter))
    if label.endswith("-H1"):
        year = int(label.removesuffix("-H1"))
        return Period(label, date(year, 1, 1), date(year, 6, 30))
    if "-" in label:
        year, month = label.split("-")
        return _month(int(year), int(month))
    year = int(label)
    return Period(label, date(year, 1, 1), date(year, 12, 31))


def due_date(period: Period, grace_days: int) -> date:
    """Evidence is due `grace_days` after the period it covers has closed."""
    return period.end + timedelta(days=grace_days)


def all_periods(
    year: int, through: int | None = None, *, last_month: int = 12
) -> dict[str, list[Period]]:
    return {
        f: periods_for(f, year, through, last_month=last_month)
        for f in ("monthly", "quarterly", "annual")
    }
