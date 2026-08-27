"""Fourteen controls, each with three numbered clauses.

Clause structure is what makes a *near-miss* precise: a near-miss document
renders two clauses as met and exactly one as unmet, and the truth file records
which one. Without clauses, "fails exactly one clause" is a claim nobody can
check.

Every clause carries three renderings — met, hedged and unmet — so the same
control can produce a compliant document, a partial one and a gap from one
definition rather than three hand-written files.

Three controls have `evidence_kind = "structured"` (CTRL-ACCESS-EXPORT,
CTRL-TRAINING, CTRL-BACKUP-VERIFY): their evidence is a metrics table and their
thresholds are evaluated in code at S2, never by a model.
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
        id="CTRL-ACCESS-REVIEW",
        title="Quarterly privileged access review",
        frequency="quarterly",
        evidence_kind="document",
        applies_when={"handles_pii": True},
        doc_type="access_review_report",
        wrong_doc_type="training_certificate",
        freshness_days=100,
        severity_weight=3.0,
        clauses=[
            Clause(
                "The owner of each system holding customer PII reviews every"
                " privileged account within the period.",
                "All {n} privileged accounts across the in-scope systems were listed"
                " from the IAM export and reviewed line by line.",
                "A sample of {j} of the {n} privileged accounts was reviewed; the"
                " remainder are queued for a later pass.",
                "No review of privileged accounts was performed in this period and"
                " the IAM export was never pulled.",
                narrow=False,
            ),
            Clause(
                "The name of the reviewer and the date of review are recorded.",
                "Reviewer: {owner}. Review completed on {date} and countersigned by"
                " the {team} lead.",
                "The review date of {date} is recorded but the reviewer field was"
                " left blank.",
                "The report records neither a reviewer name nor a review date.",
            ),
            Clause(
                "Every account no longer required is revoked, or a written"
                " justification for retaining it is recorded.",
                "{k} accounts were found to be no longer required and all {k} were"
                " revoked on {date}, with change tickets attached.",
                "{k} dormant accounts were identified; {j} were revoked and the"
                " remainder are awaiting platform team action.",
                "{k} dormant accounts were identified but revocation is still"
                " pending and no justification has been recorded for them.",
            ),
        ],
    ),
    ControlSpec(
        id="CTRL-ACCESS-EXPORT",
        title="Access review export completeness",
        frequency="quarterly",
        evidence_kind="structured",
        applies_when={"handles_pii": True},
        doc_type="access_review_export",
        wrong_doc_type="access_review_report",
        freshness_days=100,
        severity_weight=2.5,
        thresholds={"reviewed_pct": {"min": 100.0}, "dormant_unresolved": {"max": 0}},
        clauses=[
            Clause(
                "The access review export covers 100% of in-scope accounts.",
                "reviewed_pct at or above 100.",
                "reviewed_pct short of 100.",
                "reviewed_pct materially short of 100.",
            ),
            Clause(
                "No dormant account is left unresolved at period close.",
                "dormant_unresolved at zero.",
                "dormant_unresolved above zero.",
                "dormant_unresolved well above zero.",
            ),
            Clause(
                "The export is produced from the authoritative IAM system.",
                "source recorded as the IAM system of record.",
                "source recorded but not reconciled.",
                "source not recorded.",
            ),
        ],
    ),
    ControlSpec(
        id="CTRL-VENDOR-DD",
        title="Annual vendor due diligence",
        frequency="annual",
        evidence_kind="document",
        applies_when={"has_suppliers": True},
        doc_type="vendor_due_diligence_pack",
        wrong_doc_type="access_review_report",
        freshness_days=400,
        severity_weight=2.5,
        grace_days=30,
        clauses=[
            Clause(
                "Every vendor engaged during the year is assessed for financial,"
                " legal and information security risk.",
                "All {n} vendors engaged in {year} were assessed against the"
                " three-pillar risk model and scored.",
                "{j} of the {n} vendors engaged in {year} were assessed; the"
                " remainder are scheduled for next cycle.",
                "No vendor risk assessments were carried out in {year}.",
                narrow=False,
            ),
            Clause(
                "Vendors scored high risk have a documented mitigation plan.",
                "{k} vendors scored high risk and each has a mitigation plan signed"
                " off by {owner} on {date}.",
                "{k} vendors scored high risk; mitigation plans are drafted but"
                " unsigned.",
                "{k} vendors scored high risk and no mitigation plans exist.",
            ),
            Clause(
                "The assessment is refreshed within twelve months of the previous"
                " one.",
                "The previous assessment closed in {year} and this refresh was"
                " completed on {date}, inside the twelve-month window.",
                "The refresh was completed on {date}, slightly outside the"
                " twelve-month window.",
                "The last assessment predates the twelve-month window and no"
                " refresh has been scheduled.",
            ),
        ],
    ),
    ControlSpec(
        id="CTRL-SUPPLIER-ATTEST",
        title="Supplier security attestation",
        frequency="annual",
        evidence_kind="document",
        applies_when={"has_suppliers": True},
        doc_type="supplier_attestation",
        wrong_doc_type="vendor_due_diligence_pack",
        freshness_days=400,
        severity_weight=2.0,
        grace_days=30,
        clauses=[
            Clause(
                "Each supplier with access to company systems provides a current"
                " security attestation.",
                "All {n} suppliers with system access returned a current attestation"
                " for {year}.",
                "{j} of {n} suppliers returned an attestation; {k} are outstanding.",
                "No supplier attestations were collected for {year}.",
                narrow=False,
            ),
            Clause(
                "Attestations are reviewed and accepted by the owning team.",
                "Each attestation was reviewed and accepted by {owner} on {date}.",
                "Attestations were received but the review by {team} is incomplete.",
                "Attestations on file were never reviewed by {team}.",
            ),
            Clause(
                "Suppliers failing attestation are placed on a remediation plan.",
                "{k} suppliers failed and all {k} are on a tracked remediation plan.",
                "{k} suppliers failed; remediation plans exist for {j} of them.",
                "{k} suppliers failed attestation and none were placed on a plan.",
            ),
        ],
    ),
    ControlSpec(
        id="CTRL-DATA-RETENTION",
        title="Data retention schedule adherence",
        frequency="quarterly",
        evidence_kind="document",
        applies_when={"handles_pii": True},
        doc_type="retention_review",
        wrong_doc_type="incident_postmortem",
        freshness_days=100,
        severity_weight=3.0,
        clauses=[
            Clause(
                "Personal data held beyond its retention period is identified each"
                " quarter.",
                "A retention sweep on {date} identified {k} record sets held beyond"
                " their schedule.",
                "A retention sweep was run on {date} but covered only the primary"
                " store.",
                "No retention sweep was run in this period.",
                narrow=False,
            ),
            Clause(
                "Over-retained data is deleted or its retention is re-justified.",
                "All {k} over-retained record sets were deleted on {date} and the"
                " deletion log is attached.",
                "{j} of the {k} over-retained record sets were deleted; the rest"
                " await legal review.",
                "The {k} over-retained record sets remain in place with no deletion"
                " or re-justification recorded.",
            ),
            Clause(
                "The retention schedule itself is confirmed as current.",
                "The retention schedule was confirmed current by {owner} on {date}.",
                "The retention schedule was reviewed but the confirmation is"
                " unsigned.",
                "The retention schedule has not been confirmed as current.",
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
        wrong_doc_type="retention_review",
        freshness_days=45,
        severity_weight=2.5,
        clauses=[
            Clause(
                "Every severity 1 and 2 incident receives a written post-mortem"
                " within ten working days.",
                "All {n} severity 1 and 2 incidents this month have post-mortems"
                " filed within ten working days.",
                "{j} of {n} severity 1 and 2 incidents have post-mortems filed; {k}"
                " are past the ten-day window.",
                "No post-mortems were filed for the {n} severity 1 and 2 incidents"
                " this month.",
                narrow=False,
            ),
            Clause(
                "Each post-mortem records contributing factors and a corrective"
                " action with a named owner.",
                "Each post-mortem records contributing factors and a corrective"
                " action owned by a named engineer.",
                "Contributing factors are recorded but {k} corrective actions have"
                " no named owner.",
                "Post-mortems record a timeline only, with no contributing factors"
                " and no corrective actions.",
            ),
            Clause(
                "Corrective actions from prior months are tracked to closure.",
                "All {k} corrective actions carried in from prior months were closed"
                " by {date}.",
                "{j} of {k} carried-in corrective actions were closed; the rest"
                " remain open past their due date.",
                "Carried-in corrective actions are not tracked and their status is"
                " unknown.",
            ),
        ],
    ),
    ControlSpec(
        id="CTRL-TRAINING",
        title="Mandatory compliance training completion",
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
                "At least 95% of in-scope staff complete mandatory training each"
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
        id="CTRL-BACKUP-VERIFY",
        title="Backup restore verification",
        frequency="monthly",
        evidence_kind="structured",
        applies_when={"criticality": ["high", "critical"]},
        doc_type="backup_verification_log",
        wrong_doc_type="incident_postmortem",
        freshness_days=45,
        severity_weight=3.0,
        thresholds={"success_pct": {"min": 95.0}, "max_rto_minutes": {"max": 60}},
        clauses=[
            Clause(
                "At least 95% of scheduled restore tests succeed each month.",
                "success_pct at or above 95.",
                "success_pct just below 95.",
                "success_pct well below 95.",
            ),
            Clause(
                "The longest observed restore stays within the 60 minute recovery"
                " time objective.",
                "max_rto_minutes at or under 60.",
                "max_rto_minutes slightly over 60.",
                "max_rto_minutes well over 60.",
            ),
            Clause(
                "Every production data store is covered by at least one test.",
                "all stores covered.",
                "most stores covered.",
                "coverage not established.",
            ),
        ],
    ),
    ControlSpec(
        id="CTRL-CHANGE-MGMT",
        title="Change management approval",
        frequency="monthly",
        evidence_kind="document",
        applies_when={},
        doc_type="change_approval_register",
        wrong_doc_type="backup_verification_log",
        freshness_days=45,
        severity_weight=2.0,
        clauses=[
            Clause(
                "Every production change is approved before deployment.",
                "All {n} production changes this month carry a recorded approval"
                " timestamped before deployment.",
                "{j} of {n} production changes carry a pre-deployment approval; {k}"
                " were approved retrospectively.",
                "Production changes were deployed with no approval records at all.",
                narrow=False,
            ),
            Clause(
                "Emergency changes are reviewed within five working days.",
                "All {k} emergency changes were reviewed within five working days by"
                " {team}.",
                "{k} emergency changes occurred; review is complete for {j} of them.",
                "{k} emergency changes were never reviewed.",
            ),
            Clause(
                "The change register is reconciled against the deployment log.",
                "The register was reconciled against the deployment log on {date}"
                " with no discrepancies.",
                "Reconciliation on {date} left {k} discrepancies open.",
                "No reconciliation against the deployment log was performed.",
            ),
        ],
    ),
    ControlSpec(
        id="CTRL-DPIA",
        title="Data protection impact assessment currency",
        frequency="annual",
        evidence_kind="document",
        applies_when={"handles_pii": True},
        doc_type="dpia_record",
        wrong_doc_type="retention_review",
        freshness_days=400,
        severity_weight=2.5,
        grace_days=30,
        clauses=[
            Clause(
                "Each processing activity involving personal data has a current"
                " impact assessment.",
                "All {n} processing activities have an assessment dated within the"
                " last twelve months.",
                "{j} of {n} processing activities have a current assessment.",
                "No impact assessments are on file for the {n} processing"
                " activities.",
                narrow=False,
            ),
            Clause(
                "Residual high risks are escalated to the data protection officer.",
                "The {k} residual high risks were escalated to the data protection"
                " officer on {date}.",
                "{k} residual high risks are recorded; escalation is pending.",
                "Residual high risks were identified but never escalated.",
            ),
            Clause(
                "Assessments are re-run when the processing activity materially"
                " changes.",
                "{k} activities changed materially in {year} and each assessment was"
                " re-run.",
                "{k} activities changed materially; {j} assessments were re-run.",
                "Activities changed materially in {year} with no assessments re-run.",
            ),
        ],
    ),
    ControlSpec(
        id="CTRL-CUST-COMPLAINTS",
        title="Customer complaint handling SLA",
        frequency="monthly",
        evidence_kind="document",
        applies_when={"customer_facing": True},
        doc_type="complaint_sla_report",
        wrong_doc_type="change_approval_register",
        freshness_days=45,
        severity_weight=1.5,
        clauses=[
            Clause(
                "Complaints are acknowledged within two working days.",
                "All {n} complaints received this month were acknowledged within two"
                " working days.",
                "{j} of {n} complaints were acknowledged within two working days.",
                "Acknowledgement times were not tracked this month.",
                narrow=False,
            ),
            Clause(
                "Complaints are resolved or escalated within twenty working days.",
                "All {n} complaints were resolved or escalated within twenty working"
                " days.",
                "{k} complaints passed twenty working days without resolution or"
                " escalation.",
                "No resolution tracking exists for complaints this month.",
            ),
            Clause(
                "Recurring complaint themes are reported to the area owner monthly.",
                "Themes were reported to {owner} on {date}.",
                "A theme report was produced but not sent to {owner}.",
                "No theme reporting was produced this month.",
            ),
        ],
    ),
    ControlSpec(
        id="CTRL-BCP-TEST",
        title="Business continuity plan test",
        frequency="annual",
        evidence_kind="document",
        applies_when={"criticality": ["high", "critical"]},
        doc_type="bcp_test_report",
        wrong_doc_type="backup_verification_log",
        freshness_days=400,
        severity_weight=3.0,
        grace_days=30,
        clauses=[
            Clause(
                "The continuity plan is exercised at least once per year.",
                "The plan was exercised on {date} with {n} participants from {team}.",
                "A tabletop walkthrough was held on {date} but no full exercise was"
                " run.",
                "The continuity plan was not exercised in {year}.",
                narrow=False,
            ),
            Clause(
                "The exercise covers the recovery of every critical dependency.",
                "All {n} critical dependencies were recovered within target during"
                " the exercise.",
                "{j} of {n} critical dependencies were covered by the exercise.",
                "Critical dependencies were not enumerated for the exercise.",
            ),
            Clause(
                "Findings from the exercise are assigned owners and due dates.",
                "All {k} findings were assigned owners and due dates on {date}.",
                "{k} findings were raised; {j} have owners and the rest do not.",
                "Findings were noted informally with no owners or due dates.",
            ),
        ],
    ),
    ControlSpec(
        id="CTRL-CRYPTO-KEY",
        title="Encryption key rotation",
        frequency="quarterly",
        evidence_kind="document",
        applies_when={"handles_pii": True},
        doc_type="key_rotation_record",
        wrong_doc_type="access_review_export",
        freshness_days=100,
        severity_weight=3.0,
        clauses=[
            Clause(
                "Data encryption keys are rotated on the defined quarterly"
                " schedule.",
                "All {n} data encryption keys were rotated on {date}, on schedule.",
                "{j} of {n} data encryption keys were rotated; {k} slipped the"
                " schedule.",
                "No key rotation was carried out in this period.",
                narrow=False,
            ),
            Clause(
                "Superseded key material is destroyed and the destruction is"
                " witnessed.",
                "Superseded key material was destroyed on {date} and witnessed by"
                " {owner}.",
                "Superseded key material was destroyed but the destruction was not"
                " witnessed.",
                "Superseded key material remains in the key store.",
            ),
            Clause(
                "Rotation failures are alerted on and investigated.",
                "{k} rotation alerts fired and each was investigated and closed.",
                "{k} rotation alerts fired; {j} were investigated.",
                "Rotation alerting is not configured.",
            ),
        ],
    ),
    ControlSpec(
        id="CTRL-THIRD-PARTY-ACCESS",
        title="Third-party access recertification",
        frequency="quarterly",
        evidence_kind="document",
        applies_when={"has_suppliers": True},
        doc_type="third_party_access_review",
        wrong_doc_type="supplier_attestation",
        freshness_days=100,
        severity_weight=2.5,
        clauses=[
            Clause(
                "Every third-party account is recertified by the sponsoring"
                " manager each quarter.",
                "All {n} third-party accounts were recertified by their sponsoring"
                " managers by {date}.",
                "{j} of {n} third-party accounts were recertified this quarter.",
                "No third-party accounts were recertified this quarter.",
                narrow=False,
            ),
            Clause(
                "Accounts belonging to ended engagements are disabled within five"
                " working days.",
                "{k} accounts from ended engagements were disabled within five"
                " working days.",
                "{k} accounts from ended engagements were identified; {j} were"
                " disabled inside the window.",
                "Accounts from ended engagements remain enabled.",
            ),
            Clause(
                "The sponsoring manager for each account is recorded and current.",
                "A current sponsoring manager is recorded for all {n} accounts.",
                "{k} accounts have a sponsoring manager who has since left.",
                "Sponsoring managers are not recorded.",
            ),
        ],
    ),
]

SPECS_BY_ID = {c.id: c for c in CONTROL_SPECS}
CONTROL_DEFINITIONS = [spec.definition() for spec in CONTROL_SPECS]
STRUCTURED_CONTROL_IDS = [
    c.id for c in CONTROL_SPECS if c.evidence_kind == "structured"
]
