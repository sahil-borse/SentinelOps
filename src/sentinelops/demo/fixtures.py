"""The one area, one control and one evidence document slice 1 walks through.

Deliberately hardcoded. Slice 2 replaces these with the seeded synthetic
generator; until then they are the only data the system has ever seen.

The evidence is written as a near-miss on purpose: the review was performed and
recorded, but two dormant accounts are neither revoked nor justified, so the
last clause of the criteria fails. A skeleton that only ever demonstrates the
happy path proves nothing about the assessment step.
"""

from __future__ import annotations

from ..entities import AuditableUnit, ControlDefinition, Identity

DEMO_OWNER = Identity(
    id="ID-MEHTA", name="R. Mehta", role="unit_owner", auditable_unit="AREA-CUSTOPS",
)

DEMO_AREA = AuditableUnit(
    id="AREA-CUSTOPS",
    name="Customer Operations",
    kind="support_function",
    owner_identity=DEMO_OWNER.id,
    attributes={
        "handles_pii": True,
        "customer_facing": True,
        "has_suppliers": False,
        "region": "APAC",
        "criticality": "high",
    },
)

DEMO_CONTROL = ControlDefinition(
    id="CTRL-ACCESS-REVIEW",
    title="Quarterly privileged access review",
    criteria_text=(
        "Every quarter, the owner of each system holding customer PII must review "
        "all privileged accounts, record the reviewer and date, and revoke or "
        "justify every account that is no longer required."
    ),
    frequency="quarterly",
    applies_when={"handles_pii": True},
    evidence_kind="document",
    required_evidence_types=["access_review_report"],
    freshness_days=100,
    severity_weight=3.0,
)

#: Shaped like a corpus document — one numbered response per criterion —
#: because that is what the assessor reads and what `FakeModelClient` judges,
#: clause by clause. Prose that answers the criteria in an unnumbered
#: paragraph gives the stub nothing to fail on, and the skeleton then
#: "proves" a near-miss compliant.
DEMO_EVIDENCE_TEXT = (
    "Privileged Access Review - Customer Operations - Q1\n"
    "Reviewer: R. Mehta. Date: 2026-03-28.\n"
    "1. All 14 privileged accounts were listed from the IAM export and "
    "reviewed against current role assignments.\n"
    "2. The reviewer and the review date are recorded above.\n"
    "3. Two dormant accounts were identified. Revocation is still pending "
    "with the platform team and no justification has been recorded for "
    "either account.\n"
)
