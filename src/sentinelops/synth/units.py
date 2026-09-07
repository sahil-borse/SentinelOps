"""The auditable units of a fictional organisation, and the people in it.

The roster the stakeholder described: **six support functions** — IT, Admin,
Purchase, HR, Finance and Facilities — plus **four project teams**, two
PA/InfoSec auditors and two managers with real reporting lines.

Project teams matter more than they look. Section 1 says the auditable subject
is not only a support function and should be modelled generically, and `kind` is
how that is recorded. Nothing downstream branches on it: a finding against
Project Atlas is classified, chased, escalated and closed by exactly the same
code as one against Finance. If any of that forked on `kind`, "model the subject
generically" would be a comment rather than a fact.

    unit          kind             pii  cust  supp  region  criticality
    IT            support_function  Y    -     Y     APAC    critical
    ADMIN         support_function  Y    -     Y     EMEA    medium
    PURCHASE      support_function  -    -     Y     EMEA    medium
    HR            support_function  Y    -     Y     NA      high
    FINANCE       support_function  -    -     -     EMEA    high
    FACILITIES    support_function  -    -     Y     NA      low
    PRJ-ATLAS     project_team      Y    Y     -     EMEA    critical
    PRJ-BEACON    project_team      -    Y     Y     NA      medium
    PRJ-CORAL     project_team      Y    -     -     APAC    low
    PRJ-DELTA     project_team      -    -     -     APAC    medium

Purchase and Facilities draw the same control set, and that is the rules engine
being right rather than lazy: neither handles personal data, neither faces
customers, both use suppliers, and neither is business-critical. Two units with
the same risk profile owe the same obligations, and an engine that invented a
difference between them would be wrong.

**Reporting lines are two-deep and not uniform.** Finance and Purchase report to
the director directly, as a financial control line usually does; everyone else
goes through the operations director. Escalation walks `reports_to`, so an
escalation from Finance reaches a different person at level one than an
escalation from IT — which is the point of walking the line rather than gluing
"Head of" onto a team name.
"""

from __future__ import annotations

from ..entities import AuditableUnit, Identity

# --- people -----------------------------------------------------------------

#: The two managers. Top of every escalation chain.
DIRECTOR = Identity(id="ID-DIRECTOR", name="H. Lindqvist", role="management")
OPERATIONS_DIRECTOR = Identity(
    id="ID-OPSDIR", name="M. Castellanos", role="management",
    reports_to="ID-DIRECTOR",
)
MANAGERS = [DIRECTOR, OPERATIONS_DIRECTOR]

#: The two PA/InfoSec auditors — the people who conduct audits and decide
#: closure. Section 7 is unambiguous that only they may close a finding, and
#: there are two of them so that the separation-of-duty rule has somewhere to
#: go: whoever filed the evidence cannot accept it, and with one auditor that
#: rule would simply deadlock.
AUDITORS = [
    Identity(id="ID-PA-KAUR", name="P. Kaur", role="pa_infosec",
             reports_to="ID-DIRECTOR"),
    Identity(id="ID-PA-OSEI", name="T. Osei", role="pa_infosec",
             reports_to="ID-DIRECTOR"),
]

#: (identity, display name, the unit they own, who they report to)
_OWNERS = [
    ("ID-NAKAMURA", "Y. Nakamura", "AREA-IT", "ID-OPSDIR"),
    ("ID-BAKER", "R. Baker", "AREA-ADMIN", "ID-OPSDIR"),
    # Purchase and Finance report to the director, not through operations.
    ("ID-HAUGEN", "S. Haugen", "AREA-PURCHASE", "ID-DIRECTOR"),
    ("ID-FERREIRA", "D. Ferreira", "AREA-HR", "ID-OPSDIR"),
    ("ID-NOVAK", "A. Novak", "AREA-FINANCE", "ID-DIRECTOR"),
    ("ID-OKONKWO", "C. Okonkwo", "AREA-FACILITIES", "ID-OPSDIR"),
    ("ID-VASQUEZ", "E. Vasquez", "AREA-PRJ-ATLAS", "ID-OPSDIR"),
    ("ID-TANAKA", "K. Tanaka", "AREA-PRJ-BEACON", "ID-OPSDIR"),
    ("ID-DUBOIS", "M. Dubois", "AREA-PRJ-CORAL", "ID-OPSDIR"),
    ("ID-MBEKI", "L. Mbeki", "AREA-PRJ-DELTA", "ID-OPSDIR"),
]

UNIT_OWNERS = [
    Identity(id=ident, name=name, role="unit_owner", auditable_unit=unit,
             reports_to=manager)
    for ident, name, unit, manager in _OWNERS
]

IDENTITIES: list[Identity] = [*MANAGERS, *AUDITORS, *UNIT_OWNERS]
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
    _unit("AREA-IT", "IT", "support_function",
          True, False, True, "APAC", "critical"),
    _unit("AREA-ADMIN", "Admin", "support_function",
          True, False, True, "EMEA", "medium"),
    _unit("AREA-PURCHASE", "Purchase", "support_function",
          False, False, True, "EMEA", "medium"),
    _unit("AREA-HR", "HR", "support_function",
          True, False, True, "NA", "high"),
    _unit("AREA-FINANCE", "Finance", "support_function",
          False, False, False, "EMEA", "high"),
    _unit("AREA-FACILITIES", "Facilities", "support_function",
          False, False, True, "NA", "low"),
    _unit("AREA-PRJ-ATLAS", "Project Atlas", "project_team",
          True, True, False, "EMEA", "critical"),
    _unit("AREA-PRJ-BEACON", "Project Beacon", "project_team",
          False, True, True, "NA", "medium"),
    _unit("AREA-PRJ-CORAL", "Project Coral", "project_team",
          True, False, False, "APAC", "low"),
    _unit("AREA-PRJ-DELTA", "Project Delta", "project_team",
          False, False, False, "APAC", "medium"),
]

UNITS_BY_ID = {u.id: u for u in AUDITABLE_UNITS}

SUPPORT_FUNCTIONS = [u for u in AUDITABLE_UNITS if u.kind == "support_function"]
PROJECT_TEAMS = [u for u in AUDITABLE_UNITS if u.kind == "project_team"]
