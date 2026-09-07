"""The auditable units of a fictional organisation, and the people in it.

v3 is explicit that findings are not raised only against support functions: a
project team, a department and IT all qualify, and the subject should be
modelled generically. So a unit now carries a `kind` — and nothing downstream
branches on it, which is the point. It is descriptive, not a switch.

Section 10 asks for six support functions plus three or four project teams, and
the roster now matches. The project teams are the point of `kind` being
descriptive rather than a switch: nothing downstream branches on it, so a
finding against a project team is chased, escalated and closed by exactly the
same code as one against Payments. If it were not, the stakeholder's "model the
subject generically" would be a comment rather than a fact.

    unit          kind             pii  cust  supp  region  criticality
    CUSTOPS       support_function  Y    Y     -     APAC    high
    PAYMENTS      support_function  Y    Y     Y     EMEA    critical
    HR            support_function  Y    -     Y     NA      medium
    PROCUREMENT   support_function  -    -     Y     EMEA    medium
    MARKETING     support_function  Y    Y     Y     NA      low
    ITSVC         support_function  Y    -     Y     APAC    high
    PLATFORM      department        -    -     Y     APAC    critical
    FINREP        department        -    -     -     EMEA    high
    PRJ-ATLAS     project_team      Y    Y     -     EMEA    critical
    PRJ-BEACON    project_team      -    -     Y     NA      medium
    PRJ-CORAL     project_team      Y    -     -     APAC    low

Project teams are short-lived and their owners are engineers rather than
functional heads, which is why they report into Platform Engineering's owner
rather than to the operations director — escalation should follow the line that
exists, not a tidier one.

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
    ("ID-BRENNAN", "C. Brennan", "AREA-ITSVC", "ID-OPSDIR"),
    # Project leads report through Platform Engineering, not to operations.
    ("ID-VASQUEZ", "E. Vasquez", "AREA-PRJ-ATLAS", "ID-IYER"),
    ("ID-TANAKA", "K. Tanaka", "AREA-PRJ-BEACON", "ID-IYER"),
    ("ID-DUBOIS", "M. Dubois", "AREA-PRJ-CORAL", "ID-IYER"),
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
    _unit("AREA-ITSVC", "IT Services", "support_function",
          True, False, True, "APAC", "high"),
    # No suppliers of its own — Atlas buys through Procurement. Without that
    # it would carry byte-identical attributes to Payments and therefore an
    # identical control set, which makes the applicability engine look like it
    # is doing less work than it is.
    _unit("AREA-PRJ-ATLAS", "Project Atlas", "project_team",
          True, True, False, "EMEA", "critical"),
    _unit("AREA-PRJ-BEACON", "Project Beacon", "project_team",
          False, False, True, "NA", "medium"),
    _unit("AREA-PRJ-CORAL", "Project Coral", "project_team",
          True, False, False, "APAC", "low"),
]

UNITS_BY_ID = {u.id: u for u in AUDITABLE_UNITS}
