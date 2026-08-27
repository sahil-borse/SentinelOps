"""The one area, one control and one evidence document slice 1 walks through.

Deliberately hardcoded. Slice 2 replaces these with the seeded synthetic
generator; until then they are the only data the system has ever seen.

The evidence is written as a near-miss on purpose: the review was performed and
recorded, but two dormant accounts are neither revoked nor justified, so the
last clause of the criteria fails. A skeleton that only ever demonstrates the
happy path proves nothing about the assessment step.
"""

from __future__ import annotations

from ..entities import ControlDefinition, ProcessArea

DEMO_AREA = ProcessArea(
    id="AREA-CUSTOPS",
    name="Customer Operations",
    owner_team="Customer Operations",
    owner_name="R. Mehta",
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

DEMO_EVIDENCE_TEXT = (
    "Privileged Access Review - Customer Operations - Q1\n"
    "Reviewer: R. Mehta. Date: 2026-03-28.\n"
    "All 14 privileged accounts were listed from the IAM export.\n"
    "Two dormant accounts were identified but revocation is still pending with "
    "the platform team; no justification has been recorded for them."
)
