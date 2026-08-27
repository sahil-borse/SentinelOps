"""Seven process areas of a fictional organisation.

Attributes are varied deliberately, not randomly: every applies_when expression
in `controls.py` must select a different subset, so S0 (slice 3) has something
visible to prove. No area handles every flag and none handles none.

    area          pii   cust   supp   region   criticality
    CUSTOPS        Y     Y      -     APAC     high
    PAYMENTS       Y     Y      Y     EMEA     critical
    HR             Y     -      Y     NA       medium
    PROCUREMENT    -     -      Y     EMEA     medium
    MARKETING      Y     Y      Y     NA       low
    PLATFORM       -     -      Y     APAC     critical
    FINREP         -     -      -     EMEA     high
"""

from __future__ import annotations

from ..entities import ProcessArea


def _area(
    ident: str,
    name: str,
    team: str,
    owner: str,
    pii: bool,
    customer_facing: bool,
    suppliers: bool,
    region: str,
    criticality: str,
) -> ProcessArea:
    return ProcessArea(
        id=ident,
        name=name,
        owner_team=team,
        owner_name=owner,
        attributes={
            "handles_pii": pii,
            "customer_facing": customer_facing,
            "has_suppliers": suppliers,
            "region": region,
            "criticality": criticality,
        },
    )


PROCESS_AREAS: list[ProcessArea] = [
    _area("AREA-CUSTOPS", "Customer Operations", "Customer Operations",
          "R. Mehta", True, True, False, "APAC", "high"),
    _area("AREA-PAYMENTS", "Payments Processing", "Payments Engineering",
          "L. Okafor", True, True, True, "EMEA", "critical"),
    _area("AREA-HR", "People Operations", "People Operations",
          "D. Ferreira", True, False, True, "NA", "medium"),
    _area("AREA-PROC", "Procurement", "Procurement",
          "S. Haugen", False, False, True, "EMEA", "medium"),
    _area("AREA-MKTG", "Marketing", "Marketing",
          "J. Alvarez", True, True, True, "NA", "low"),
    _area("AREA-PLATFORM", "Platform Engineering", "Platform Engineering",
          "N. Iyer", False, False, True, "APAC", "critical"),
    _area("AREA-FINREP", "Financial Reporting", "Finance",
          "A. Novak", False, False, False, "EMEA", "high"),
]

AREAS_BY_ID = {a.id: a for a in PROCESS_AREAS}
