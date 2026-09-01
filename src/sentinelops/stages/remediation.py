"""Closing the loop: remediation evidence, re-assessment, resolution.

    finding -> action -> remediation submitted -> re-assessed -> resolved

`reassess(conn, check_instance_id)` is the on-demand entry point. A team that
fixes something on Tuesday should not wait until the next scheduled cycle to be
told it is fixed, and an auditor watching the demo should not have to either.

Re-assessment is not a special case pretending to be one. The remediation
evidence goes through the same S2 rules and, if they cannot decide it, the same
S3 call as the original — same prompt, same criteria, same citation check. The
only difference is bookkeeping: the new Finding records `supersedes_finding_id`,
so the trail keeps both the failure and the fix rather than overwriting one with
the other.

If the new verdict passes, the Action resolves with a note naming the finding
that cleared it. If it does not, the Action stays open and the loop is still
open — a remediation that did not work is not a resolution.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

from ..entities import Action, Evidence, Finding
from ..periods import periods_for
from .assess import assess_one, AssessmentReport
from .flag import resolve, transition
from .prescreen import bind_evidence, evaluate_thresholds, evidence_age_days

#: Verdicts that count as the problem having been fixed.
PASSING = ("compliant",)


@dataclass
class ReassessmentResult:
    check_instance_id: str
    remediation_evidence_id: str | None = None
    superseded_finding_id: str | None = None
    new_finding_id: str | None = None
    verdict: str | None = None
    decided_by: str | None = None
    action_id: str | None = None
    action_status: str | None = None
    resolved: bool = False
    reason: str = ""


def pending_remediation(repo, instance, as_of: date | None = None) -> Any | None:
    """The earliest remediation filing not yet bound to this instance.

    Evidence dated after `as_of` has not been filed yet as far as this run is
    concerned. Without that check a re-assessment run in April would pick up a
    fix submitted in December and resolve the action before the work happened,
    which quietly destroys any mean-time-to-resolution figure.
    """
    bound = {e.id for e in repo["evidence"].list(check_instance_id=instance.id)}
    candidates = [
        s
        for s in repo["submissions"].list(
            control_id=instance.control_id,
            process_area_id=instance.process_area_id,
            period=instance.period,
        )
        if s.is_remediation
        and f"EV-{s.id}" not in bound
        and (as_of is None or s.submitted_at.date() <= as_of)
    ]
    return min(candidates, key=lambda s: s.submitted_at) if candidates else None


def _prescreen_remediation(control, evidence: Evidence, period_end: date):
    """The S2 rules again, on the new evidence. Same rules, same order."""
    if evidence.doc_type not in control.required_evidence_types:
        return (
            "insufficient_evidence",
            f"The remediation is a {evidence.doc_type}, but the control requires "
            f"{' or '.join(control.required_evidence_types)}.",
            [], [f"Wrong evidence type: {evidence.doc_type}."],
            "wrong_evidence_type",
        )
    age = evidence_age_days(evidence, period_end)
    if age > control.freshness_days:
        return (
            "gap",
            f"The remediation is dated {evidence.submitted_at.date()}, {age} days "
            f"before the period closed, outside the {control.freshness_days} day "
            "freshness window.",
            [], [f"Remediation evidence is {age} days old."],
            "stale_evidence",
        )
    if control.evidence_kind == "structured" and control.thresholds:
        verdict, cited, gaps, rationale = evaluate_thresholds(control, evidence)
        return verdict, rationale, cited, gaps, "structured_threshold"
    return None


def reassess(
    conn,
    check_instance_id: str,
    as_of: date,
    *,
    client=None,
    year: int = 2026,
) -> ReassessmentResult:
    """Re-check one instance against its remediation evidence, on demand."""
    from ..repositories import repositories
    from .prescreen import _write_finding as write_rule_finding

    repo = repositories(conn)
    result = ReassessmentResult(check_instance_id=check_instance_id)

    instance = repo["instances"].get(check_instance_id)
    if instance is None:
        result.reason = "no such check instance"
        return result

    control = repo["controls"].get(instance.control_id)
    prior = sorted(
        repo["findings"].list(check_instance_id=check_instance_id), key=lambda f: f.id
    )
    if not prior:
        result.reason = "nothing to supersede: this instance has no finding yet"
        return result
    superseded = prior[-1]
    result.superseded_finding_id = superseded.id

    submission = pending_remediation(repo, instance, as_of)
    if submission is None:
        result.reason = "no unbound remediation evidence for this instance"
        return result

    action = next(
        (a for a in repo["actions"].list(finding_id=superseded.id)), None
    ) or next(
        (
            a
            for a in repo["actions"].list()
            if a.id == f"ACT-{instance.id.removeprefix('CHK-')}"
        ),
        None,
    )

    # --- the owning team files a fix --------------------------------------
    evidence = bind_evidence(repo, instance, submission)
    result.remediation_evidence_id = evidence.id
    instance.status = "submitted"
    repo["instances"].update(instance)
    repo["audit"].append(
        actor="user",
        owner=submission.author,
        action="remediation_submitted",
        entity_type="CheckInstance",
        entity_id=instance.id,
        detail={
            "evidence_id": evidence.id,
            "submission_id": submission.id,
            "supersedes_finding_id": superseded.id,
            "submitted_at": submission.submitted_at.isoformat(),
        },
    )
    if action is not None:
        result.action_id = action.id
        if action.status in ("raised", "assigned"):
            transition(
                repo, action, "in_progress", actor="user", owner=submission.author,
                detail={"trigger": "remediation evidence filed"},
            )
        transition(
            repo, action, "remediation_submitted", actor="user",
            owner=submission.author,
            detail={"evidence_id": evidence.id, "submission_id": submission.id},
        )

    # --- S2 first, then S3 only if the rules cannot decide ----------------
    period_end = next(
        p.end for p in periods_for(control.frequency, year) if p.label == instance.period
    )
    decided = _prescreen_remediation(control, evidence, period_end)
    if decided is not None:
        verdict, rationale, cited, gaps, decided_by = decided
        finding = write_rule_finding(
            repo, instance,
            verdict=verdict, rationale=rationale, cited_spans=cited, gaps=gaps,
            recommended_action="" if verdict == "compliant" else "Resubmit.",
            decided_by=decided_by, as_of=as_of,
        )
    else:
        report = AssessmentReport(as_of=as_of)
        finding = assess_one(
            conn, repo, instance, control, evidence,
            client=client, as_of=as_of, report=report,
        )

    finding.supersedes_finding_id = superseded.id
    repo["findings"].update(finding)
    repo["audit"].append(
        actor="system",
        owner=instance.owner_name,
        action="finding_superseded",
        entity_type="Finding",
        entity_id=superseded.id,
        detail={
            "superseded_by": finding.id,
            "previous_verdict": superseded.verdict,
            "new_verdict": finding.verdict,
            "check_instance_id": instance.id,
        },
    )
    result.new_finding_id = finding.id
    result.verdict = finding.verdict
    result.decided_by = finding.decided_by

    # --- did it work? -----------------------------------------------------
    if action is not None:
        transition(
            repo, action, "reassessed", actor="system", owner=instance.owner_name,
            detail={
                "finding_id": finding.id,
                "verdict": finding.verdict,
                "supersedes_finding_id": superseded.id,
            },
        )
        if finding.verdict in PASSING:
            note = (
                f"Remediation accepted. {finding.id} supersedes {superseded.id}: "
                f"{superseded.verdict} -> {finding.verdict}, decided by "
                f"{finding.decided_by}."
            )
            resolve(repo, action, note, as_of, owner=instance.owner_name)
            result.resolved = True
        else:
            result.reason = (
                f"remediation did not clear the finding: still {finding.verdict}"
            )
        result.action_status = action.status

    for flag in repo["flags"].list(check_instance_id=instance.id):
        if result.resolved and flag.status == "open":
            flag.status = "closed"
            repo["flags"].update(flag)
            repo["audit"].append(
                actor="system",
                owner=instance.owner_name,
                action="flag_closed",
                entity_type="Flag",
                entity_id=flag.id,
                detail={"closed_by": finding.id, "category": flag.category},
            )
    return result


def reassess_all(conn, as_of: date, *, client=None) -> list[ReassessmentResult]:
    """Every instance with remediation evidence waiting. Used by the demo."""
    from ..repositories import repositories

    repo = repositories(conn)
    waiting = sorted(
        {
            s.control_id + "|" + s.process_area_id + "|" + s.period
            for s in repo["submissions"].list()
            if s.is_remediation
        }
    )
    results = []
    for key in waiting:
        control_id, area_id, period = key.split("|")
        instance_id = (
            f"CHK-{control_id.removeprefix('CTRL-')}-"
            f"{area_id.removeprefix('AREA-')}-{period}"
        )
        result = reassess(conn, instance_id, as_of, client=client)
        if result.new_finding_id:
            results.append(result)
    return results
