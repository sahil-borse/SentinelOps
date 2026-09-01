"""S2 — pre-screen. Zero tokens, and the reason the cost story is true.

Most compliance checking is not a judgement call. Evidence that never arrived,
evidence of the wrong kind, evidence identical to last period's, evidence too
old to speak to the period it covers, and a metrics table measured against a
numeric threshold are all decidable in code, exactly and repeatably. Sending any
of them to a model would be spending money to be less certain.

The rules run in this order, first match wins:

    1. no evidence            -> insufficient_evidence
    2. wrong document type    -> insufficient_evidence
    3. content hash unchanged -> carry the prior finding forward
    4. older than freshness   -> gap, by rule
    5. structured + threshold -> evaluate the numbers directly

Only ambiguous document evidence — something that arrived, of the right type,
new, fresh, and prose rather than arithmetic — survives to S3. Everything the
pre-screen decides carries `decided_by` naming the rule, so the share of the
corpus that never reached a model is a query rather than a claim.

Confidence for a rule-decided finding is 1.0. That is not bravado: arithmetic
against a stated threshold is certain in a way a language model's reading of a
paragraph is not, and pretending otherwise would make the two incomparable.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

from ..entities import CheckInstance, ControlDefinition, Evidence, Finding
from ..periods import periods_for

#: Statuses S2 will look at. `pending` means not yet due — there is nothing to
#: decide. `assessed` and `waived` are already settled.
CONSIDERED = ("submitted", "overdue")

#: Rule names, in evaluation order. `to_assess` is not a rule; it is what is
#: left when none of them fire.
RULES = (
    "no_evidence",
    "wrong_evidence_type",
    "carried_forward",
    "stale_evidence",
    "structured_threshold",
)


@dataclass
class PrescreenReport:
    """What the tier did, so the cost claim can be checked rather than asserted."""

    as_of: date
    considered: int = 0
    skipped_not_due: int = 0
    exits: dict[str, int] = field(default_factory=lambda: {r: 0 for r in RULES})
    to_assess: list[str] = field(default_factory=list)
    findings: list[str] = field(default_factory=list)

    @property
    def resolved(self) -> int:
        return sum(self.exits.values())

    @property
    def zero_model_share(self) -> float:
        """Share of considered instances resolved without any model call."""
        return self.resolved / self.considered if self.considered else 0.0

    def breakdown(self) -> list[tuple[str, int, float]]:
        rows = [
            (rule, count, count / self.considered if self.considered else 0.0)
            for rule, count in self.exits.items()
        ]
        rows.append(
            (
                "to_assess (survives to S3)",
                len(self.to_assess),
                len(self.to_assess) / self.considered if self.considered else 0.0,
            )
        )
        return rows


def evidence_id_for(submission_id: str) -> str:
    """One evidence record per submission, derived so binding is idempotent."""
    return f"EV-{submission_id}"


def finding_id_for(instance_id: str, sequence: int) -> str:
    return f"FND-{instance_id.removeprefix('CHK-')}-{sequence}"


def bind_evidence(repo, instance: CheckInstance, submission) -> Evidence:
    """Materialise a staged submission as evidence against an instance.

    Write-once: a second submission for the same instance produces a second
    record with its own id. Nothing is ever rewritten, so the history of what
    was filed and when survives intact.
    """
    identifier = evidence_id_for(submission.id)
    existing = repo["evidence"].get(identifier)
    if existing is not None:
        return existing

    evidence = Evidence(
        id=identifier,
        check_instance_id=instance.id,
        kind=submission.kind,
        doc_type=submission.doc_type,
        content=submission.content,
        content_hash=submission.content_hash,
        submitted_at=submission.submitted_at,
        author=submission.author,
        is_remediation=submission.is_remediation,
    )
    repo["evidence"].add(evidence)
    repo["audit"].append(
        actor="user",
        owner=evidence.author,
        action="evidence_bound",
        entity_type="Evidence",
        entity_id=evidence.id,
        detail={
            "check_instance_id": instance.id,
            "submission_id": submission.id,
            "doc_type": evidence.doc_type,
            "content_hash": evidence.content_hash[:12],
            "is_remediation": evidence.is_remediation,
        },
    )
    return evidence


def evidence_age_days(evidence: Evidence, period_end: date) -> int:
    """How old the evidence is relative to the period it claims to cover.

    Measured against period close, not against today: a report written in
    January cannot speak for a December period however recently it was filed.
    """
    return (period_end - evidence.submitted_at.date()).days


def evaluate_thresholds(
    control: ControlDefinition, evidence: Evidence
) -> tuple[str, list[str], list[str], str]:
    """Check a metrics table against the control's numeric thresholds.

    Returns (verdict, cited_spans, gaps, rationale). The rationale names the
    numbers, because "the training completion check failed" is not a finding
    anybody can act on and "completion_pct was 91.4 against a required minimum
    of 95.0" is.
    """
    try:
        metrics = json.loads(evidence.content)
    except json.JSONDecodeError:
        return (
            "insufficient_evidence",
            [],
            ["Evidence is declared structured but is not parsable as a table."],
            "The submitted evidence could not be read as a metrics table.",
        )

    lines = evidence.content.splitlines()
    cited: list[str] = []
    gaps: list[str] = []
    checked: list[str] = []
    missing: list[str] = []

    for metric, rule in sorted(control.thresholds.items()):
        if metric not in metrics:
            missing.append(metric)
            continue
        actual = metrics[metric]
        span = next(
            (line.strip().rstrip(",") for line in lines if f'"{metric}"' in line),
            f'"{metric}": {actual}',
        )
        cited.append(span)
        if "min" in rule:
            limit, ok, wording = rule["min"], actual >= rule["min"], "at least"
        else:
            limit, ok, wording = rule["max"], actual <= rule["max"], "at most"
        checked.append(f"{metric} was {actual} against a required {wording} {limit}")
        if not ok:
            gaps.append(
                f"{metric} was {actual}, outside the required {wording} {limit}."
            )

    if missing:
        return (
            "insufficient_evidence",
            cited,
            [f"The table does not report {m}." for m in missing],
            "The metrics table omits "
            + ", ".join(missing)
            + ", so the threshold cannot be evaluated.",
        )

    verdict = "gap" if gaps else "compliant"
    lead = "Threshold evaluation failed" if gaps else "All thresholds met"
    rationale = f"{lead}: " + "; ".join(checked) + "."
    return verdict, cited, gaps, rationale


def _write_finding(
    repo,
    instance: CheckInstance,
    *,
    verdict: str,
    rationale: str,
    decided_by: str,
    cited_spans: list[str] | None = None,
    gaps: list[str] | None = None,
    recommended_action: str = "",
    confidence: float = 1.0,
    needs_human_review: bool = False,
    carried_forward_from: str | None = None,
    as_of: date | None = None,
) -> Finding:
    sequence = len(repo["findings"].list(check_instance_id=instance.id)) + 1
    finding = Finding(
        id=finding_id_for(instance.id, sequence),
        check_instance_id=instance.id,
        verdict=verdict,
        confidence=confidence,
        rationale=rationale,
        cited_spans=cited_spans or [],
        gaps=gaps or [],
        recommended_action=recommended_action,
        needs_human_review=needs_human_review,
        assessed_at=datetime.combine(as_of, datetime.min.time()) if as_of else datetime.now(),
        supersedes_finding_id=None,
        carried_forward_from=carried_forward_from,
        decided_by=decided_by,
    )
    repo["findings"].add(finding)
    instance.status = "assessed"
    repo["instances"].update(instance)
    repo["audit"].append(
        actor="system",
        owner=instance.owner_name,
        action="finding_recorded",
        entity_type="Finding",
        entity_id=finding.id,
        # The trail carries the citation *text*, not a count of citations. An
        # auditor reading the log alone has to be able to see what was quoted;
        # "3 spans were cited" is not evidence of anything.
        detail={
            "check_instance_id": instance.id,
            "control_id": instance.control_id,
            "process_area_id": instance.process_area_id,
            "period": instance.period,
            "verdict": verdict,
            "confidence": confidence,
            "rationale": rationale,
            "cited_spans": [s[:300] for s in finding.cited_spans],
            "gaps": finding.gaps,
            "recommended_action": finding.recommended_action,
            "needs_human_review": needs_human_review,
            "decided_by": decided_by,
            "model_calls": 0,
            "carried_forward_from": carried_forward_from,
        },
    )
    return finding


def _prior_findings_by_hash(repo, instances: dict[str, CheckInstance]) -> dict:
    """Index assessed periods by (control, area, content hash).

    Used by rule 3: if this period's evidence is byte-identical to evidence
    already judged for the same control in the same area, the answer cannot
    have changed, so the prior finding is carried forward instead of being
    bought again.
    """
    index: dict[tuple[str, str, str], tuple[str, Finding]] = {}
    evidence_by_instance: dict[str, Evidence] = {}
    for evidence in repo["evidence"].list():
        evidence_by_instance.setdefault(evidence.check_instance_id, evidence)

    for finding in repo["findings"].list():
        instance = instances.get(finding.check_instance_id)
        evidence = evidence_by_instance.get(finding.check_instance_id)
        if instance is None or evidence is None:
            continue
        key = (instance.control_id, instance.process_area_id, evidence.content_hash)
        held = index.get(key)
        if held is None or instance.period < held[0]:
            index[key] = (instance.period, finding)
    return index


def _remember(carried: dict, instance: CheckInstance, evidence: Evidence, finding: Finding) -> None:
    """Index a finding so a later period with identical evidence can reuse it.

    Updated as the loop writes findings, not only from what was already on disk:
    otherwise January's verdict would be invisible to February within the same
    run, and the rule would only ever fire across separate cycles.
    """
    key = (instance.control_id, instance.process_area_id, evidence.content_hash)
    held = carried.get(key)
    if held is None or instance.period < held[0]:
        carried[key] = (instance.period, finding)


def run(conn, as_of: date, *, year: int = 2026) -> PrescreenReport:
    """Pre-screen every instance that is due a decision.

    Returns the report; the instances named in `to_assess` are the only ones
    S3 will ever be asked about.
    """
    from ..repositories import simulated_clock

    with simulated_clock(datetime.combine(as_of, datetime.min.time().replace(hour=3))):
        return _run(conn, as_of, year=year)


def _run(conn, as_of: date, *, year: int = 2026) -> PrescreenReport:
    from ..repositories import repositories

    repo = repositories(conn)
    controls = {c.id: c for c in repo["controls"].list()}
    instances = {i.id: i for i in repo["instances"].list()}
    report = PrescreenReport(as_of=as_of)

    period_ends = {
        (control.id, period.label): period.end
        for control in controls.values()
        for period in periods_for(control.frequency, year)
    }

    submissions: dict[tuple[str, str, str], list] = {}
    for submission in repo["submissions"].list():
        if submission.is_remediation:
            continue  # slice 7 re-assesses these through the action loop
        if submission.submitted_at.date() > as_of:
            continue
        key = (submission.control_id, submission.process_area_id, submission.period)
        submissions.setdefault(key, []).append(submission)
    for filings in submissions.values():
        filings.sort(key=lambda s: s.submitted_at)

    carried = _prior_findings_by_hash(repo, instances)

    for instance in sorted(instances.values(), key=lambda i: (i.period, i.id)):
        if instance.status not in CONSIDERED:
            if instance.status == "pending":
                report.skipped_not_due += 1
            continue
        report.considered += 1
        control = controls[instance.control_id]
        period_end = period_ends[(instance.control_id, instance.period)]
        key = (instance.control_id, instance.process_area_id, instance.period)
        filings = submissions.get(key, [])

        # 1 — nothing was ever filed
        if not filings:
            finding = _write_finding(
                repo, instance,
                verdict="insufficient_evidence",
                rationale=(
                    f"No evidence was submitted for {instance.period} against"
                    f" {control.title}. The check fell due on {instance.due_date}."
                ),
                gaps=[f"No evidence on file for {instance.period}."],
                recommended_action=(
                    f"Submit {' or '.join(control.required_evidence_types)} for"
                    f" {instance.period}."
                ),
                decided_by="no_evidence",
                as_of=as_of,
            )
            report.exits["no_evidence"] += 1
            report.findings.append(finding.id)
            continue

        evidence = bind_evidence(repo, instance, filings[0])

        # 2 — filed, but not the kind of document the control asks for
        if evidence.doc_type not in control.required_evidence_types:
            finding = _write_finding(
                repo, instance,
                verdict="insufficient_evidence",
                rationale=(
                    f"The submission is a {evidence.doc_type}, but"
                    f" {control.title} requires"
                    f" {' or '.join(control.required_evidence_types)}."
                    " The criteria cannot be assessed against it."
                ),
                gaps=[f"Wrong evidence type: {evidence.doc_type}."],
                recommended_action=(
                    f"Resubmit as {' or '.join(control.required_evidence_types)}."
                ),
                decided_by="wrong_evidence_type",
                as_of=as_of,
            )
            report.exits["wrong_evidence_type"] += 1
            report.findings.append(finding.id)
            _remember(carried, instance, evidence, finding)
            continue

        # 3 — byte-identical to evidence already judged for this control here
        prior = carried.get(
            (instance.control_id, instance.process_area_id, evidence.content_hash)
        )
        if prior is not None and prior[0] != instance.period:
            prior_period, prior_finding = prior
            finding = _write_finding(
                repo, instance,
                verdict=prior_finding.verdict,
                rationale=(
                    f"Evidence is byte-identical to {prior_period} (hash"
                    f" {evidence.content_hash[:12]}), so the verdict from"
                    f" {prior_finding.id} is carried forward unchanged:"
                    f" {prior_finding.rationale}"
                ),
                cited_spans=list(prior_finding.cited_spans),
                gaps=list(prior_finding.gaps),
                recommended_action=prior_finding.recommended_action,
                confidence=prior_finding.confidence,
                needs_human_review=prior_finding.needs_human_review,
                carried_forward_from=prior_finding.id,
                decided_by="carried_forward",
                as_of=as_of,
            )
            report.exits["carried_forward"] += 1
            report.findings.append(finding.id)
            _remember(carried, instance, evidence, finding)
            continue

        # 4 — too old to speak for the period it covers
        age = evidence_age_days(evidence, period_end)
        if age > control.freshness_days:
            finding = _write_finding(
                repo, instance,
                verdict="gap",
                rationale=(
                    f"Evidence is dated {evidence.submitted_at.date()}, {age} days"
                    f" before {instance.period} closed, exceeding the"
                    f" {control.freshness_days} day freshness window for"
                    f" {control.title}."
                ),
                gaps=[
                    f"Evidence is {age} days old against a"
                    f" {control.freshness_days} day limit."
                ],
                recommended_action=(
                    f"Perform the control for {instance.period} and submit current"
                    " evidence."
                ),
                decided_by="stale_evidence",
                as_of=as_of,
            )
            report.exits["stale_evidence"] += 1
            report.findings.append(finding.id)
            _remember(carried, instance, evidence, finding)
            continue

        # 5 — arithmetic, not judgement
        if control.evidence_kind == "structured" and control.thresholds:
            verdict, cited, gaps, rationale = evaluate_thresholds(control, evidence)
            finding = _write_finding(
                repo, instance,
                verdict=verdict,
                rationale=rationale,
                cited_spans=cited,
                gaps=gaps,
                recommended_action=(
                    "" if verdict == "compliant"
                    else f"Bring the reported metrics within threshold for"
                         f" {instance.period} and resubmit."
                ),
                decided_by="structured_threshold",
                as_of=as_of,
            )
            report.exits["structured_threshold"] += 1
            report.findings.append(finding.id)
            _remember(carried, instance, evidence, finding)
            continue

        # nothing decided it: this is a judgement call, and S3 gets it
        report.to_assess.append(instance.id)

    repo["audit"].append(
        actor="system",
        owner="prescreen",
        action="prescreen_completed",
        entity_type="Cycle",
        entity_id=as_of.isoformat(),
        detail={
            "as_of": as_of.isoformat(),
            "considered": report.considered,
            "resolved_without_a_model": report.resolved,
            "to_assess": len(report.to_assess),
            "zero_model_share": round(report.zero_model_share, 4),
            **{f"exit_{rule}": count for rule, count in report.exits.items()},
        },
    )
    return report
