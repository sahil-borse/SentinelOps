"""The auditable units of a fictional organisation, and the people in it.

v3 is explicit that findings are not raised only against support functions: a
project team, a department and IT all qualify, and the subject should be
modelled generically. So a unit now carries a `kind` — and nothing downstream
branches on it, which is the point. It is descriptive, not a switch.

**The roster is deliberately unchanged in this slice.** Same seven units, same
ids, same attributes, so the corpus fingerprint, the 64 applicable pairings and
the 343 check instances all hold and every test that moves is a rename rather
than a recount. Adding project teams and stretching to eighteen months is the
corpus slice; doing it here would hide a vocabulary change inside a data change.

    unit          kind             pii  cust  supp  region  criticality
    CUSTOPS       support_function  Y    Y     -     APAC    high
    PAYMENTS      support_function  Y    Y     Y     EMEA    critical
    HR            support_function  Y    -     Y     NA      medium
    PROCUREMENT   support_function  -    -     Y     EMEA    medium
    MARKETING     support_function  Y    Y     Y     NA      low
    PLATFORM      department        -    -     Y     APAC    critical
    FINREP        department        -    -     -     EMEA    high

The reporting lines matter: escalation walks `reports_to` rather than inventing
a manager by gluing "Head of " onto a team name, so everybody it escalates to
is somebody who exists.
"""

from __future__ import annotations

from ..entities import AuditableUnit, Identity

# --- people -----------------------------------------------------------------

#: Management, at the top of every escalation chain.
DIRECTOR = Identity(id="ID-DIRECTOR", name="H. Lindqvist", role="management")
OPERATIONS_DIRECTOR = Identity(
    id="ID-OPSDIR", name="M. Castellanos", role="management", reports_to="ID-DIRECTOR"
)

#: PA/InfoSec — the people who conduct audits and decide closure. Section 7 is
#: unambiguous that only they may close a finding.
AUDITORS = [
    Identity(id="ID-PA-KAUR", name="P. Kaur", role="pa_infosec",
             reports_to="ID-DIRECTOR"),
    Identity(id="ID-PA-OSEI", name="T. Osei", role="pa_infosec",
             reports_to="ID-DIRECTOR"),
]

#: (identity, display name, the unit they own, who they report to)
_OWNERS = [
    ("ID-MEHTA", "R. Mehta", "AREA-CUSTOPS", "ID-OPSDIR"),
    ("ID-OKAFOR", "L. Okafor", "AREA-PAYMENTS", "ID-OPSDIR"),
    ("ID-FERREIRA", "D. Ferreira", "AREA-HR", "ID-OPSDIR"),
    ("ID-HAUGEN", "S. Haugen", "AREA-PROC", "ID-OPSDIR"),
    ("ID-ALVAREZ", "J. Alvarez", "AREA-MKTG", "ID-OPSDIR"),
    ("ID-IYER", "N. Iyer", "AREA-PLATFORM", "ID-DIRECTOR"),
    ("ID-NOVAK", "A. Novak", "AREA-FINREP", "ID-DIRECTOR"),
]

UNIT_OWNERS = [
    Identity(id=ident, name=name, role="unit_owner", auditable_unit=unit,
             reports_to=manager)
    for ident, name, unit, manager in _OWNERS
]

IDENTITIES: list[Identity] = [DIRECTOR, OPERATIONS_DIRECTOR, *AUDITORS, *UNIT_OWNERS]
IDENTITIES_BY_ID = {i.id: i for i in IDENTITIES}

#: Who owns each unit, for building the roster below.
_OWNER_OF = {unit: ident for ident, _, unit, _ in _OWNERS}


# --- units ------------------------------------------------------------------

def _unit(
    ident: str,
    name: str,
    kind: str,
    pii: bool,
    customer_facing: bool,
    suppliers: bool,
    region: str,
    criticality: str,
) -> AuditableUnit:
    return AuditableUnit(
        id=ident,
        name=name,
        kind=kind,
        owner_identity=_OWNER_OF[ident],
        attributes={
            "handles_pii": pii,
            "customer_facing": customer_facing,
            "has_suppliers": suppliers,
            "region": region,
            "criticality": criticality,
        },
    )


AUDITABLE_UNITS: list[AuditableUnit] = [
    _unit("AREA-CUSTOPS", "Customer Operations", "support_function",
          True, True, False, "APAC", "high"),
    _unit("AREA-PAYMENTS", "Payments Processing", "support_function",
          True, True, True, "EMEA", "critical"),
    _unit("AREA-HR", "People Operations", "support_function",
          True, False, True, "NA", "medium"),
    _unit("AREA-PROC", "Procurement", "support_function",
          False, False, True, "EMEA", "medium"),
    _unit("AREA-MKTG", "Marketing", "support_function",
          True, True, True, "NA", "low"),
    _unit("AREA-PLATFORM", "Platform Engineering", "department",
          False, False, True, "APAC", "critical"),
    _unit("AREA-FINREP", "Financial Reporting", "department",
          False, False, False, "EMEA", "high"),
]

UNITS_BY_ID = {u.id: u for u in AUDITABLE_UNITS}
