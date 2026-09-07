"""Fourteen controls: the compliance activities section 3 names, and no others.

    periodic risk register review            controlled document review
    internal audit readiness                 closure of prior audit findings
    external audit readiness                 review of changed processes
    process manual and guideline review      security awareness training
    access review                            vendor and supplier due diligence
    incident post-mortem completion          backup and restore verification
    data retention review                    business continuity test

This list is not ours. The stakeholder named these when asked what the auditable
units actually do on a cycle, and an earlier version of this file carried a
plausible-sounding set we had invented instead — access-export completeness,
encryption key rotation, complaint-handling SLAs. They were reasonable controls
and they were not this organisation's, which makes every applicability count
computed over them a statement about a company that does not exist.

Clause structure is what makes a *near-miss* precise: a near-miss document
renders two clauses as met and exactly one as unmet, and the truth file records
which one. Without clauses, "fails exactly one clause" is a claim nobody can
check.

Every clause carries three renderings — met, hedged and unmet — so the same
control can produce a compliant document, a partial one and a gap from one
definition rather than three hand-written files.

Three controls have `evidence_kind = "structured"` (CTRL-TRAINING,
CTRL-BACKUP-VERIFY, CTRL-FINDING-CLOSURE): their evidence is a metrics table and
their thresholds are evaluated in code at S2, never by a model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..entities import ControlDefinition


@dataclass(frozen=True)
class Clause:
    """One numbered requirement, and how evidence for it reads in three states.

    `narrow` says whether the unmet rendering is a *scoped* failure that can sit
    inside an otherwise clean report. Clauses whose unmet text asserts that
    nothing happened at all ("no review was performed") are not narrow: pairing
    one with two satisfied clauses produces a document that contradicts itself,
    which is not a near-miss, it is nonsense. Near-misses draw only from narrow
    clauses; wholesale failures are what `non_compliant` is for.
    """

    text: str
    met: str
    hedged: str
    unmet: str
    narrow: bool = True


@dataclass(frozen=True)
class ControlSpec:
    """A control definition plus the generator-only data used to write evidence."""

    id: str
    title: str
    frequency: str
    evidence_kind: str
    applies_when: dict[str, Any]
    doc_type: str
    wrong_doc_type: str
    clauses: list[Clause]
    freshness_days: int
    severity_weight: float
    thresholds: dict[str, dict[str, float]] = field(default_factory=dict)
    grace_days: int = 15

    def definition(self) -> ControlDefinition:
        criteria = "\n".join(
            f"{i}. {c.text}" for i, c in enumerate(self.clauses, start=1)
        )
        return ControlDefinition(
            id=self.id,
            title=self.title,
            criteria_text=criteria,
            frequency=self.frequency,
            applies_when=dict(self.applies_when),
            evidence_kind=self.evidence_kind,
            required_evidence_types=[self.doc_type],
            freshness_days=self.freshness_days,
            severity_weight=self.severity_weight,
            thresholds=dict(self.thresholds),
            grace_days=self.grace_days,
        )


CONTROL_SPECS: list[ControlSpec] = [
    ControlSpec(
        id="CTRL-RISK-REGISTER",
        title="Periodic risk register review",
        frequency="quarterly",
        evidence_kind="document",
        applies_when={},
        doc_type="risk_register_review",
        wrong_doc_type="risk_heatmap_slide",
        freshness_days=100,
        severity_weight=2.5,
        clauses=[
            Clause(
                "The unit's risk register is reviewed each quarter by the risk"
                " owner.",
                "The register was reviewed on {date} by {owner}.",
                "The register was reviewed late in the quarter by {owner}.",
                "No review of the register took place this quarter.",
                narrow=False,
            ),
            Clause(
                "Every risk rated high or above carries a current mitigation and"
                " a named owner.",
                "All {n} high-rated risks carry a current mitigation and a named"
                " owner.",
                "{j} of {n} high-rated risks carry a current mitigation; the"
                " remainder are being drafted.",
                "{j} of {n} high-rated risks have neither a mitigation nor an"
                " owner recorded.",
            ),
            Clause(
                "Risks closed during the quarter record the evidence for their"
                " closure.",
                "All {k} risks closed this quarter cite closure evidence.",
                "{k} risks were closed; evidence is attached for most of them.",
                "{k} risks were closed with no closure evidence recorded.",
            ),
        ],
    ),
    ControlSpec(
        id="CTRL-INTERNAL-AUDIT-READY",
        title="Internal audit readiness",
        frequency="annual",
        evidence_kind="document",
        applies_when={},
        doc_type="audit_readiness_pack",
        wrong_doc_type="meeting_minutes",
        freshness_days=180,
        severity_weight=2.0,
        clauses=[
            Clause(
                "The unit maintains a current index of the evidence an internal"
                " audit would request.",
                "The evidence index was refreshed on {date} and covers {n}"
                " artefacts.",
                "The evidence index exists but was last refreshed some time ago.",
                "No evidence index is maintained for this unit.",
                narrow=False,
            ),
            Clause(
                "Owners are nominated for each area the audit will cover.",
                "Owners are nominated for all {n} areas in scope.",
                "Owners are nominated for most areas; {j} are still to confirm.",
                "{j} of {n} areas in scope have no nominated owner.",
            ),
            Clause(
                "Findings from the previous internal audit are reflected in the"
                " readiness pack.",
                "All {k} prior findings are reflected with their current status.",
                "Prior findings are listed; {j} lack a current status.",
                "The pack does not reference the previous audit's findings.",
            ),
        ],
    ),
    ControlSpec(
        id="CTRL-EXTERNAL-AUDIT-READY",
        title="External audit readiness",
        frequency="annual",
        evidence_kind="document",
        applies_when={"criticality": ["high", "critical"]},
        doc_type="external_audit_pack",
        wrong_doc_type="audit_readiness_pack",
        freshness_days=180,
        severity_weight=3.0,
        clauses=[
            Clause(
                "Evidence required by the external auditor is assembled before"
                " the fieldwork date.",
                "The pack was assembled on {date}, ahead of fieldwork.",
                "The pack was assembled close to the fieldwork date.",
                "No pack was assembled ahead of fieldwork.",
                narrow=False,
            ),
            Clause(
                "Prior-year external findings are shown as closed or explained.",
                "All {n} prior-year findings are shown as closed with evidence.",
                "{j} of {n} prior-year findings are shown as closed; the rest are"
                " in progress.",
                "{j} of {n} prior-year findings carry no status at all.",
            ),
            Clause(
                "A single point of contact is named for the auditor's requests.",
                "{owner} is named as the point of contact.",
                "A point of contact is named but is not confirmed as available.",
                "No point of contact is named.",
            ),
        ],
    ),
    ControlSpec(
        id="CTRL-PROCESS-MANUAL",
        title="Process manual and guideline review",
        frequency="annual",
        evidence_kind="document",
        applies_when={},
        doc_type="process_manual_review",
        wrong_doc_type="training_certificate",
        freshness_days=180,
        severity_weight=2.0,
        clauses=[
            Clause(
                "The unit's process manual is reviewed at least annually and the"
                " review is recorded.",
                "The manual was reviewed on {date} by {owner}.",
                "The manual was reviewed, though the record is incomplete.",
                "No annual review of the manual was carried out.",
                narrow=False,
            ),
            Clause(
                "The manual matches the process actually followed.",
                "All {n} documented steps match current practice.",
                "{j} of {n} documented steps are ahead of the manual and being"
                " updated.",
                "{j} of {n} documented steps no longer match how the work is"
                " done.",
            ),
            Clause(
                "Superseded versions are withdrawn from circulation.",
                "All {k} superseded versions were withdrawn.",
                "Superseded versions were withdrawn from the main repository"
                " only.",
                "{k} superseded versions remain in circulation.",
            ),
        ],
    ),
    ControlSpec(
        id="CTRL-CONTROLLED-DOCS",
        title="Controlled document review",
        frequency="quarterly",
        evidence_kind="document",
        applies_when={},
        doc_type="controlled_document_register",
        wrong_doc_type="process_manual_review",
        freshness_days=100,
        severity_weight=2.0,
        clauses=[
            Clause(
                "Every controlled document is reviewed before its review date"
                " passes.",
                "All {n} controlled documents are within their review date.",
                "{j} of {n} controlled documents are within days of their review"
                " date.",
                "{j} of {n} controlled documents are past their review date.",
            ),
            Clause(
                "Each document names an owner and an approver.",
                "All {n} documents name an owner and an approver.",
                "{j} documents name an owner but no approver.",
                "{j} of {n} documents name neither an owner nor an approver.",
            ),
            Clause(
                "The register reconciles to the documents actually in use.",
                "The register reconciles to the {n} documents in use.",
                "The register reconciles with {j} unexplained differences.",
                "The register was not reconciled to the documents in use.",
            ),
        ],
    ),
    ControlSpec(
        id="CTRL-FINDING-CLOSURE",
        title="Closure and validation of prior audit findings",
        frequency="quarterly",
        evidence_kind="structured",
        applies_when={},
        doc_type="finding_closure_table",
        wrong_doc_type="audit_readiness_pack",
        freshness_days=100,
        severity_weight=3.0,
        thresholds={"closed_on_time_pct": {"min": 90.0},
                    "overdue_findings": {"max": 2}},
        clauses=[
            Clause(
                "At least 90% of findings due for closure this quarter were"
                " closed on time.",
                "closed_on_time_pct at or above 90.",
                "closed_on_time_pct just below 90.",
                "closed_on_time_pct well below 90.",
            ),
            Clause(
                "No more than two findings remain overdue at quarter close.",
                "overdue_findings at two or fewer.",
                "overdue_findings slightly above two.",
                "overdue_findings well above two.",
            ),
            Clause(
                "Every closure carries the auditor's validation.",
                "all closures validated by the auditor.",
                "closures validated with some remarks outstanding.",
                "closures recorded without auditor validation.",
            ),
        ],
    ),
    ControlSpec(
        id="CTRL-CHANGED-PROCESS",
        title="Review of newly introduced or changed processes",
        frequency="monthly",
        evidence_kind="document",
        applies_when={},
        doc_type="process_change_review",
        wrong_doc_type="controlled_document_register",
        freshness_days=45,
        severity_weight=2.5,
        clauses=[
            Clause(
                "Every new or materially changed process is reviewed before it"
                " goes live.",
                "All {n} changes this month were reviewed before go-live.",
                "{j} of {n} changes were reviewed on the day of go-live.",
                "{j} of {n} changes went live before any review took place.",
            ),
            Clause(
                "The compliance impact of each change is recorded.",
                "Compliance impact is recorded for all {n} changes.",
                "Compliance impact is recorded for most changes.",
                "Compliance impact was not assessed for {j} changes.",
            ),
            Clause(
                "Changes affecting personal data are referred for assessment.",
                "All {k} changes touching personal data were referred.",
                "{k} changes touched personal data; referral is in progress.",
                "{k} changes touching personal data were not referred.",
            ),
        ],
    ),
    ControlSpec(
        id="CTRL-TRAINING",
        title="Security awareness training completion",
        frequency="quarterly",
        evidence_kind="structured",
        applies_when={},
        doc_type="training_completion_table",
        wrong_doc_type="training_certificate",
        freshness_days=100,
        severity_weight=1.5,
        thresholds={"completion_pct": {"min": 95.0}, "overdue_staff": {"max": 5}},
        clauses=[
            Clause(
                "At least 95% of in-scope staff complete awareness training each"
                " quarter.",
                "completion_pct at or above 95.",
                "completion_pct just below 95.",
                "completion_pct well below 95.",
            ),
            Clause(
                "No more than five staff remain overdue at period close.",
                "overdue_staff at five or fewer.",
                "overdue_staff slightly above five.",
                "overdue_staff well above five.",
            ),
            Clause(
                "The population is reconciled against the HR system of record.",
                "population reconciled to HR.",
                "population reconciled with exceptions.",
                "population not reconciled.",
            ),
        ],
    ),
    ControlSpec(
        id="CTRL-ACCESS-REVIEW",
        title="Access review",
        frequency="quarterly",
        evidence_kind="document",
        applies_when={"handles_pii": True},
        doc_type="access_review_report",
        wrong_doc_type="joiner_leaver_log",
        freshness_days=100,
        severity_weight=3.0,
        clauses=[
            Clause(
                "Every account with access to systems holding personal data is"
                " reviewed each quarter.",
                "All {n} accounts were reviewed on {date} by {owner}.",
                "{j} of {n} accounts were reviewed; the remainder are scheduled.",
                "No access review was carried out this quarter.",
                narrow=False,
            ),
            Clause(
                "Accounts belonging to leavers are removed within five working"
                " days.",
                "All {k} leaver accounts were removed inside the window.",
                "{k} leaver accounts were identified; {j} were removed inside the"
                " window.",
                "{k} leaver accounts remained active past the window.",
            ),
            Clause(
                "Access that is no longer required is revoked or justified in"
                " writing.",
                "All {k} unnecessary grants were revoked and recorded.",
                "{k} unnecessary grants were identified; revocation is pending.",
                "{k} unnecessary grants remain in place with no justification.",
            ),
        ],
    ),
    ControlSpec(
        id="CTRL-VENDOR-DD",
        title="Vendor and supplier due diligence",
        frequency="annual",
        evidence_kind="document",
        applies_when={"has_suppliers": True},
        doc_type="vendor_due_diligence_file",
        wrong_doc_type="purchase_order_summary",
        freshness_days=180,
        severity_weight=2.5,
        clauses=[
            Clause(
                "Every supplier onboarded this year has a completed due diligence"
                " file.",
                "All {n} suppliers onboarded this year have complete files.",
                "{j} of {n} supplier files are complete; the rest are in"
                " progress.",
                "{j} of {n} suppliers were onboarded with no due diligence file.",
            ),
            Clause(
                "Suppliers with access to internal systems hold a signed"
                " information security schedule.",
                "All {k} suppliers with system access hold a signed schedule.",
                "{k} suppliers have access; {j} schedules are awaiting"
                " signature.",
                "{k} suppliers hold system access with no signed schedule.",
            ),
            Clause(
                "Financial standing is checked before a supplier is activated.",
                "Financial standing was checked for all {n} suppliers.",
                "Financial standing was checked for most suppliers.",
                "{j} suppliers were activated with no financial standing check.",
            ),
        ],
    ),
    ControlSpec(
        id="CTRL-INCIDENT-PM",
        title="Incident post-mortem completion",
        frequency="monthly",
        evidence_kind="document",
        applies_when={"criticality": ["high", "critical"]},
        doc_type="incident_postmortem",
        wrong_doc_type="incident_ticket_export",
        freshness_days=45,
        severity_weight=2.5,
        clauses=[
            Clause(
                "Every incident of severity two or above receives a written"
                " post-mortem within ten working days.",
                "All {n} qualifying incidents have post-mortems inside the"
                " window.",
                "{j} of {n} post-mortems were completed slightly outside the"
                " window.",
                "{j} of {n} qualifying incidents have no post-mortem.",
            ),
            Clause(
                "Each post-mortem records a root cause rather than a symptom.",
                "All {n} post-mortems record a root cause.",
                "{j} post-mortems record a contributing factor rather than a root"
                " cause.",
                "{j} of {n} post-mortems record no root cause.",
            ),
            Clause(
                "Actions arising are tracked somewhere that survives the incident"
                " ticket being closed.",
                "All {k} actions are tracked in the findings register.",
                "Actions are tracked in the incident tickets, with a migration"
                " planned.",
                "Actions arising are tracked only inside the closed tickets.",
            ),
        ],
    ),
    ControlSpec(
        id="CTRL-BACKUP-VERIFY",
        title="Backup and restore verification",
        frequency="monthly",
        evidence_kind="structured",
        applies_when={"criticality": ["high", "critical"]},
        doc_type="restore_test_metrics",
        wrong_doc_type="backup_job_log",
        freshness_days=45,
        severity_weight=3.0,
        thresholds={"success_pct": {"min": 95.0}, "max_rto_minutes": {"max": 60}},
        clauses=[
            Clause(
                "At least 95% of restore tests succeed.",
                "success_pct at or above 95.",
                "success_pct just below 95.",
                "success_pct well below 95.",
            ),
            Clause(
                "No restore exceeds the sixty-minute recovery time objective.",
                "max_rto_minutes at sixty or below.",
                "max_rto_minutes slightly above sixty.",
                "max_rto_minutes well above sixty.",
            ),
            Clause(
                "Restore logs are retained as evidence of the test.",
                "restore logs retained for every test.",
                "restore logs retained for most tests.",
                "restore logs not retained.",
            ),
        ],
    ),
    ControlSpec(
        id="CTRL-DATA-RETENTION",
        title="Data retention review",
        frequency="quarterly",
        evidence_kind="document",
        applies_when={"handles_pii": True},
        doc_type="retention_review_report",
        wrong_doc_type="data_inventory_export",
        freshness_days=100,
        severity_weight=2.5,
        clauses=[
            Clause(
                "Every data set holding personal data carries a retention"
                " period.",
                "All {n} data sets carry a documented retention period.",
                "{j} of {n} data sets carry a retention period; the rest are"
                " being classified.",
                "{j} of {n} data sets hold personal data with no retention period"
                " recorded.",
            ),
            Clause(
                "Data past its retention period is deleted and the deletion"
                " recorded.",
                "All {k} data sets past retention were deleted and recorded.",
                "{k} data sets are past retention; deletion is scheduled.",
                "{k} data sets remain in place past their retention period.",
            ),
            Clause(
                "Legal holds are recorded where deletion is suspended.",
                "All {j} legal holds are recorded with an expiry.",
                "Legal holds are recorded without expiry dates.",
                "Deletion was suspended with no legal hold recorded.",
            ),
        ],
    ),
    ControlSpec(
        id="CTRL-BCP-TEST",
        title="Business continuity test",
        frequency="annual",
        evidence_kind="document",
        applies_when={"criticality": ["high", "critical"]},
        doc_type="continuity_test_report",
        wrong_doc_type="continuity_plan",
        freshness_days=180,
        severity_weight=3.0,
        clauses=[
            Clause(
                "The continuity plan is exercised at least once a year.",
                "The plan was exercised on {date} with {n} participants.",
                "The plan was exercised late in the year.",
                "The plan was not exercised this year.",
                narrow=False,
            ),
            Clause(
                "The test covers the unit's critical processes.",
                "All {n} critical processes were in scope of the test.",
                "{j} of {n} critical processes were in scope.",
                "{j} of {n} critical processes were out of scope of the test.",
            ),
            Clause(
                "Issues arising from the test are recorded with owners.",
                "All {k} issues arising were recorded with owners.",
                "Issues were recorded; {j} have no owner yet.",
                "{k} issues arose from the test and none were recorded.",
            ),
        ],
    ),
]


SPECS_BY_ID = {c.id: c for c in CONTROL_SPECS}
CONTROL_DEFINITIONS = [spec.definition() for spec in CONTROL_SPECS]
STRUCTURED_CONTROL_IDS = [
    c.id for c in CONTROL_SPECS if c.evidence_kind == "structured"
]
