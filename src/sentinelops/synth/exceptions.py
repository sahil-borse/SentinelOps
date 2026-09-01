"""Four approved deviations, chosen to exercise every path they can take.

    EXC-001  active all year        -> suppresses its check for every period
    EXC-002  expires 2026-06-30     -> suppresses Q1 and Q2, then the check
                                       comes back for Q3 and Q4
    EXC-003  revoked                -> suppresses nothing; the record survives
    EXC-004  granted 2026-05-11     -> suppresses nothing, because it arrives
                                       after the obligation it excuses is
                                       already open and overdue: it *waives*

EXC-002 is attached to a *quarterly* control on purpose. Hung off an annual one
its expiry would be invisible: a single period ending 2026-12-31 falls outside
the window either way, and nothing would ever come back.

EXC-002 is the one the demo is built on. A team is granted a documented
deviation, the deviation lapses mid-year, and the check silently becomes due
again. That is exactly the kind of thing a spreadsheet forgets.

EXC-004 exists so that `waived` is reachable from the corpus rather than only
from a purpose-built test fixture. Its window, 11 May to 19 June, is chosen to
contain no quarterly period end whatsoever — 31 Mar, 30 Jun, 30 Sep and 31 Dec
all fall outside it — so `suppresses` is false for every period and not one byte
of generated evidence moves. What it does reach is the 2026-Q1 instance, due on
15 April with nothing ever filed against it: open, overdue, and now formally
excused. The distinction it draws, implemented in `stages.trigger`:

    suppression  in force when the period opened     -> no check is ever raised
    waiver       arrives after the check is open     -> the open check is excused
"""

from __future__ import annotations

from datetime import date

from ..entities import ComplianceException

COMPLIANCE_EXCEPTIONS: list[ComplianceException] = [
    ComplianceException(
        id="EXC-001",
        control_id="CTRL-BCP-TEST",
        process_area_id="AREA-PLATFORM",
        rationale=(
            "Continuity exercise deferred while the disaster recovery estate is "
            "migrated to the new region. Migration completes Q1 2027."
        ),
        approved_by="Group Risk Committee",
        granted_at=date(2026, 1, 15),
        expires_at=date(2026, 12, 31),
        status="active",
    ),
    ComplianceException(
        id="EXC-002",
        control_id="CTRL-THIRD-PARTY-ACCESS",
        process_area_id="AREA-MKTG",
        rationale=(
            "Third-party access recertification waived for the agency roster "
            "pending consolidation of marketing suppliers under a single master "
            "agreement. Consolidation was due to complete by 30 June."
        ),
        approved_by="Chief Procurement Officer",
        granted_at=date(2026, 1, 1),
        expires_at=date(2026, 6, 30),
        status="active",
    ),
    ComplianceException(
        id="EXC-003",
        control_id="CTRL-INCIDENT-PM",
        process_area_id="AREA-FINREP",
        rationale=(
            "Post-mortem requirement waived during the reporting platform "
            "freeze. Withdrawn after the audit committee objected."
        ),
        approved_by="Finance Control Board",
        granted_at=date(2026, 2, 1),
        expires_at=date(2026, 12, 31),
        status="revoked",
    ),
    ComplianceException(
        id="EXC-004",
        control_id="CTRL-CRYPTO-KEY",
        process_area_id="AREA-HR",
        rationale=(
            "Q1 key rotation for the HR data store was not carried out before "
            "the payroll platform migration froze the key management service. "
            "Rotation is deferred and the outstanding Q1 obligation waived, on "
            "the compensating control of a manual key inventory signed off by "
            "the platform team. Expires at migration cutover."
        ),
        approved_by="Chief Information Security Officer",
        granted_at=date(2026, 5, 11),
        expires_at=date(2026, 6, 19),
        status="active",
    ),
]


def suppresses(
    exception: ComplianceException, control_id: str, area_id: str, on: date
) -> bool:
    """Whether this exception excuses that control, in that area, on that date.

    Only `active` exceptions suppress, and only inside their granted window.
    A revoked one suppresses nothing; an expired one stops suppressing the day
    after it lapses — and S1 (slice 4) raises an alert of its own at that point.
    """
    return (
        exception.status == "active"
        and exception.control_id == control_id
        and exception.process_area_id == area_id
        and exception.granted_at <= on <= exception.expires_at
    )
