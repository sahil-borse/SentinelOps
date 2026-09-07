"""Closing the loop: remediation evidence, re-assessment, resolution.

    finding raised -> owner acts -> evidence filed -> re-assessed -> closed

`reassess(conn, check_instance_id)` is the on-demand entry point. A team that
fixes something on Tuesday should not wait until the next scheduled cycle to be
told it is fixed, and an auditor watching the demo should not have to either.

Re-assessment is not a special case pretending to be one. The remediation
evidence goes through the same S2 rules and, if they cannot decide it, the same
S3 call as the original — same prompt, same criteria, same citation check. The
only difference is bookkeeping: the new Assessment records `supersedes_assessment_id`,
so the trail keeps both the failure and the fix rather than overwriting one with
the other.

If the new verdict passes, an auditor closes the finding with remarks naming the
assessment that cleared it. If it does not, the finding **stays open** and
`follow_up_count` goes up by one, which is section 4 exactly: the finding remains
open until the auditor is satisfied, and a round that failed is still a round.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

from ..entities import Evidence, Assessment
from ..periods import periods_for
from .assess import assess_one, AssessmentReport
from . import followup, rounds
from .prescreen import bind_evidence, evaluate_thresholds, evidence_age_days

#: Verdicts that count as the problem having been fixed.
PASSING = ("compliant",)


@dataclass
class ReassessmentResult:
    check_instance_id: str
    remediation_evidence_id: str | None = None
    superseded_assessment_id: str | None = None
    new_assessment_id: str | None = None
    verdict: str | None = None
    decided_by: str | None = None
    finding_id: str | None = None
    finding_status: str | None = None
    round_id: str | None = None
    round_number: int | None = None
    auditor_response: str | None = None
    resolved: bool = False
    reason: str = ""


def _reviewing_auditor(people, finding, repo) -> str:
    """Pick a PA/InfoSec identity who is clear to review this finding.

    Section 7's separation rule is not decorative: with two auditors on the
    rota, one of whom filed the evidence, the reviewer must be the other. If
    nobody is clear the caller gets an id that will be refused downstream rather
    than a silently-permitted one, because "no eligible reviewer" is a real
    state and quietly picking somebody ineligible is the bug this prevents.
    """
    from ..authority import separated

    disqualified = rounds.submitters_of(repo, finding.id) | {finding.owner_identity}
    for auditor in people.by_role("pa_infosec"):
        if separated(disqualified, auditor.id, "respond_to_submission"):
            return auditor.id
    auditors = people.by_role("pa_infosec")
    return auditors[0].id if auditors else "ID-SYSTEM"


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
        for s in repo["inbound"].list(
            control_id=instance.control_id,
            auditable_unit_id=instance.auditable_unit_id,
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
    from ..repositories import simulated_clock

    with simulated_clock(datetime.combine(as_of, datetime.min.time().replace(hour=6))):
        return _reassess(conn, check_instance_id, as_of, client=client, year=year)


def _reassess(
    conn,
    check_instance_id: str,
    as_of: date,
    *,
    client=None,
    year: int = 2026,
) -> ReassessmentResult:
    from ..repositories import repositories
    from .prescreen import _write_finding as write_rule_finding

    repo = repositories(conn)
    from .. import directory

    people = directory.load(conn)
    result = ReassessmentResult(check_instance_id=check_instance_id)

    instance = repo["instances"].get(check_instance_id)
    if instance is None:
        result.reason = "no such check instance"
        return result

    control = repo["controls"].get(instance.control_id)
    prior = sorted(
        repo["assessments"].list(check_instance_id=check_instance_id), key=lambda f: f.id
    )
    if not prior:
        result.reason = "nothing to supersede: this instance has no finding yet"
        return result
    superseded = prior[-1]
    result.superseded_assessment_id = superseded.id

    submission = pending_remediation(repo, instance, as_of)
    if submission is None:
        result.reason = "no unbound remediation evidence for this instance"
        return result

    finding_record = repo["findings"].get(
        f"FND-{instance.id.removeprefix('CHK-')}"
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
            "supersedes_assessment_id": superseded.id,
            "submitted_at": submission.submitted_at.isoformat(),
        },
    )
    if finding_record is not None:
        result.finding_id = finding_record.id
        # Owner progress is self-reported and advisory. Filing evidence says the
        # owner believes the work is done; it does not make the finding closed,
        # and section 4 is emphatic that only the auditor moves that.
        followup.set_progress(
            repo, finding_record, "implemented",
            by=finding_record.owner_identity,
            detail={"evidence_id": evidence.id, "submission_id": submission.id},
        )
        # And it opens a review round. The round is the durable record of "we
        # went round on this one N times" — without it the loop happens but
        # leaves nothing behind to count.
        round_record = rounds.open_round(
            repo, people, finding_record,
            by=finding_record.owner_identity,
            evidence_ref=evidence.id,
            note=submission.owner_note if hasattr(submission, "owner_note") else "",
            as_of=as_of,
        )
        result.round_id = round_record.id
        result.round_number = round_record.round_number

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

    finding.supersedes_assessment_id = superseded.id
    repo["assessments"].update(finding)
    repo["audit"].append(
        actor="system",
        owner=instance.owner_name,
        action="assessment_superseded",
        entity_type="Assessment",
        entity_id=superseded.id,
        detail={
            "superseded_by": finding.id,
            "previous_verdict": superseded.verdict,
            "new_verdict": finding.verdict,
            "check_instance_id": instance.id,
        },
    )
    result.new_assessment_id = finding.id
    result.verdict = finding.verdict
    result.decided_by = finding.decided_by

    # --- did it work? The auditor answers the round, always ----------------
    if finding_record is not None:
        auditor = _reviewing_auditor(people, finding_record, repo)
        if finding.verdict in PASSING:
            remarks = (
                f"Remediation accepted. {finding.id} supersedes "
                f"{superseded.id}: {superseded.verdict} -> {finding.verdict}, "
                f"decided by {finding.decided_by}."
            )
            rounds.respond(
                repo, people, round_record, response="accepted",
                by=auditor, remarks=remarks, as_of=as_of,
            )
            followup.close_on_repo(
                repo, finding_record, by=auditor, remarks=remarks, as_of=as_of,
                people=people,
            )
            result.resolved = True
        else:
            # Insufficient. The round is answered and closed, the finding stays
            # open, and round N+1 is expected. This is the transition the
            # stakeholder described in the most detail, so it is the one that
            # leaves the most behind.
            remarks = (
                f"Evidence does not clear the finding: still "
                f"{finding.verdict}. {finding.recommended_action}".strip()
            )
            rounds.respond(
                repo, people, round_record, response="insufficient",
                by=auditor, remarks=remarks, as_of=as_of,
            )
            followup.record_insufficient_round(
                repo, finding_record, by=auditor, remarks=remarks,
                assessment_id=finding.id,
            )
            result.reason = (
                f"remediation did not clear the finding: still {finding.verdict}"
            )
        result.auditor_response = round_record.auditor_response
        result.finding_status = finding_record.status

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
            s.control_id + "|" + s.auditable_unit_id + "|" + s.period
            for s in repo["inbound"].list()
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
        if result.new_assessment_id:
            results.append(result)
    return results
