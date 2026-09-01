"""The eight domain entities of section 3, as plain dataclasses.

No behaviour lives here beyond identity and defaults; persistence is the
repositories' job and rules are the stages' job.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Literal

EvidenceKind = Literal["document", "structured"]
Verdict = Literal["compliant", "partial", "gap", "insufficient_evidence"]
CheckStatus = Literal["pending", "submitted", "assessed", "overdue", "waived"]
ActionStatus = Literal[
    "raised",
    "assigned",
    "in_progress",
    "remediation_submitted",
    "reassessed",
    "resolved",
    "escalated",
]
ExceptionStatus = Literal["active", "expired", "revoked"]
Actor = Literal["system", "ai", "user"]
Frequency = Literal["monthly", "quarterly", "annual"]


@dataclass
class ProcessArea:
    id: str
    name: str
    owner_team: str
    owner_name: str
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass
class ControlDefinition:
    id: str
    title: str
    criteria_text: str
    frequency: Frequency
    applies_when: dict[str, Any] = field(default_factory=dict)
    evidence_kind: EvidenceKind = "document"
    required_evidence_types: list[str] = field(default_factory=list)
    freshness_days: int = 365
    severity_weight: float = 1.0
    # Section 4, S2: "evidence_kind == structured with a numeric threshold ->
    # evaluate in code". The threshold has to live on the control.
    # {metric_name: {"min": x} | {"max": y}}
    thresholds: dict[str, Any] = field(default_factory=dict)
    grace_days: int = 15


@dataclass
class CheckInstance:
    id: str
    control_id: str
    process_area_id: str
    period: str
    due_date: date
    status: CheckStatus
    assigned_team: str
    owner_name: str


@dataclass
class Evidence:
    id: str
    check_instance_id: str
    kind: EvidenceKind
    doc_type: str
    content: str
    content_hash: str
    submitted_at: datetime
    author: str
    is_remediation: bool = False


@dataclass
class EvidenceSubmission:
    """Evidence as it arrives, before it is matched to a CheckInstance.

    A team submits against a control for a period; S1 (slice 4) creates the
    instance and S2 (slice 5) binds the submission to it as an `Evidence` row.
    Keyed by (control, area, period) because the synthetic corpus is generated
    before any instance exists — and because an instance with no matching
    submission is exactly what "missed check" means.
    """

    id: str
    control_id: str
    process_area_id: str
    period: str
    kind: EvidenceKind
    doc_type: str
    content: str
    content_hash: str
    submitted_at: datetime
    author: str
    is_remediation: bool = False


@dataclass
class Finding:
    id: str
    check_instance_id: str
    verdict: Verdict
    confidence: float
    rationale: str
    cited_spans: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    recommended_action: str = ""
    needs_human_review: bool = False
    assessed_at: datetime | None = None
    supersedes_finding_id: str | None = None
    # Set when S2 carried this verdict forward from an earlier period because
    # the evidence had not changed. Non-null *is* the carried_forward flag, and
    # it names the finding it came from, so the trail stays followable.
    carried_forward_from: str | None = None
    # Provenance: enough to reproduce and explain any verdict months later.
    # Which criteria text was judged, which prompt asked, which bytes were read.
    criteria_hash: str = ""
    prompt_version: str = ""
    evidence_hash: str = ""
    # Which tier decided: a pre-screen rule name, or "s3_model" once a model
    # has been asked. The share of findings that never say "s3_model" is the
    # cost story.
    decided_by: str = "s3_model"


@dataclass
class Action:
    id: str
    finding_id: str
    title: str
    owner_team: str
    owner_name: str
    due_date: date
    status: ActionStatus = "raised"
    resolution_note: str | None = None
    resolved_at: datetime | None = None


@dataclass
class ComplianceException:
    id: str
    control_id: str
    process_area_id: str
    rationale: str
    approved_by: str
    granted_at: date
    expires_at: date
    status: ExceptionStatus = "active"


@dataclass
class AuditEvent:
    """Append-only. Written as a by-product of every state transition."""

    id: int | None
    ts: datetime
    actor: Actor
    owner: str
    action: str
    entity_type: str
    entity_id: str
    detail: dict[str, Any] = field(default_factory=dict)
