"""Relentless follow-up — the part of v3 that no human does reliably.

Two clocks run on every open finding, both driven by severity and both stated in
section 5. Neither is clever; both are relentless, which is the point. A system
that never forgets to chase is worth more here than one that judges well, because
at fifteen open findings nobody is short of judgement — they are short of
somebody who remembers.

    severity          target      first reminder     escalate
    Major (urgent)    3 days      1 day before       1 day past
    Major             7 days      2 days before      3 days past
    Minor            14 days      3 days before      5 days past
    Observation      28 days      5 days before      7 days past

The stakeholder's stated preference was a maximum of one week from target date
to escalation, and every row above respects it — asserted by test, so a future
edit that lets a finding drift for a fortnight fails rather than ships.

Reminders continue *after* escalation. Escalating is not a way of handing the
problem on and stopping: the owner still owes the evidence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from typing import Any

from .. import directory
from ..directory import Directory
from ..entities import Finding, Severity

@dataclass(frozen=True)
class FollowUpRule:
    """How long the owner gets, when to remind, and when to escalate — in days."""

    target_days: int
    remind_before: int
    escalate_after: int



SEVERITY_RULES: dict[str, FollowUpRule] = {
    "Major:urgent": FollowUpRule(target_days=3, remind_before=1, escalate_after=1),
    "Major": FollowUpRule(target_days=7, remind_before=2, escalate_after=3),
    "Minor": FollowUpRule(target_days=14, remind_before=3, escalate_after=5),
    "Observation": FollowUpRule(target_days=28, remind_before=5, escalate_after=7),
}

#: The stakeholder's stated ceiling. Nothing may drift longer than this between
#: falling due and somebody senior hearing about it.
MAX_DAYS_TO_ESCALATION = 7

#: A Major finding against a business-critical unit is the urgent variant.
#: Section 5 names "Major (urgent)" without saying what makes one urgent, so the
#: rule is stated here rather than left to a judgement call at the call site.
URGENT_CRITICALITY = "critical"


def rule_for(severity: Severity | None, criticality: str = "") -> FollowUpRule:
    if severity == "Major" and criticality == URGENT_CRITICALITY:
        return SEVERITY_RULES["Major:urgent"]
    return SEVERITY_RULES.get(severity or "Observation", SEVERITY_RULES["Observation"])


def target_date_for(
    raised_on: date, severity: Severity | None, criticality: str = ""
) -> date:
    return raised_on + timedelta(days=rule_for(severity, criticality).target_days)


@dataclass
class FollowUpReport:
    as_of: date
    reminded: list[str] = field(default_factory=list)
    escalated: list[tuple[str, int]] = field(default_factory=list)
    notifications: list[dict[str, Any]] = field(default_factory=list)

    def summary(self) -> str:
        return (
            f"{len(self.reminded)} reminders sent · "
            f"{len(self.escalated)} escalations"
        )


def _log(repo, *, kind: str, to: str, finding: Finding, subject: str, as_of: date,
         actor_identity: str, report: FollowUpReport) -> None:
    payload = {
        "kind": kind,
        "to_identity": to,
        "finding_id": finding.id,
        "severity": finding.severity,
        "target_date": finding.target_date.isoformat(),
        "follow_up_count": finding.follow_up_count,
        "subject": subject,
        "as_of": as_of.isoformat(),
        "delivery": "logged_not_sent",
    }
    report.notifications.append(payload)
    repo["audit"].append(
        actor="system", owner=to, action="notification_logged",
        entity_type="Finding", entity_id=finding.id, detail=payload,
        actor_identity=actor_identity,
    )


def _escalation_levels(repo) -> dict[str, int]:
    """How far each finding has already been escalated, read off the trail."""
    levels: dict[str, int] = {}
    for event in repo["audit"].read_all():
        if event.action == "finding_escalated":
            levels[event.entity_id] = max(
                levels.get(event.entity_id, 0), int(event.detail.get("level", 0))
            )
    return levels


def record_reminder(repo, finding: Finding, as_of: date, people: Directory,
                    report: FollowUpReport) -> None:
    """Chase the owner, and count the chase.

    `follow_up_count` is what makes "how much did this one cost to close?"
    answerable later, so it moves here and on every insufficient-evidence round.
    """
    finding.follow_up_count += 1
    repo["findings"].update(finding)
    owner = people.name(finding.owner_identity)
    days = (finding.target_date - as_of).days
    when = f"due in {days} day(s)" if days >= 0 else f"{-days} day(s) overdue"
    repo["audit"].append(
        actor="system", owner=owner, action="finding_reminder_sent",
        entity_type="Finding", entity_id=finding.id,
        detail={
            "follow_up_count": finding.follow_up_count,
            "severity": finding.severity,
            "target_date": finding.target_date.isoformat(),
            "days_to_target": days,
        },
    )
    _log(repo, kind="reminder", to=finding.owner_identity, finding=finding,
         subject=f"{finding.id} is {when}", as_of=as_of,
         actor_identity=finding.owner_identity, report=report)
    report.reminded.append(finding.id)


def escalate(repo, finding: Finding, level: int, as_of: date, people: Directory,
             report: FollowUpReport) -> None:
    """Up the reporting line, and to PA/InfoSec.

    Section 5: escalation goes to the owner's `reports_to` *and* to PA/InfoSec.
    Both, not either — the owning side needs to know their manager has been told,
    and the audit side needs to know the finding is drifting.
    """
    chain = people.escalation_chain(finding.owner_identity)
    manager = chain[min(level, len(chain) - 1)] if chain else None
    auditors = people.by_role("pa_infosec")
    days_late = (as_of - finding.target_date).days

    repo["audit"].append(
        actor="system", owner=manager.name if manager else "unknown",
        action="finding_escalated", entity_type="Finding", entity_id=finding.id,
        detail={
            "level": level,
            "escalated_to": manager.id if manager else "",
            "also_notified": [a.id for a in auditors],
            "days_past_target": days_late,
            "severity": finding.severity,
            "threshold_days": rule_for(finding.severity).escalate_after,
        },
        actor_identity=manager.id if manager else "",
    )
    for recipient in ([manager] if manager else []) + auditors:
        _log(repo, kind="escalation", to=recipient.id, finding=finding,
             subject=(
                 f"Escalation level {level}: {finding.id} is {days_late} day(s) "
                 f"past its target date"
             ),
             as_of=as_of, actor_identity=recipient.id, report=report)
    report.escalated.append((finding.id, level))


def run(conn, as_of: date) -> FollowUpReport:
    """Chase everything open. Reminders and escalation both, every cycle.

    Entered under the simulated clock like every other stage, so a reminder
    dated 14 May reads as 14 May in the trail rather than as the wall-clock
    moment a machine replayed the year.
    """
    from ..repositories import simulated_clock

    with simulated_clock(datetime.combine(as_of, time(5, 30))):
        return _run(conn, as_of)


def _run(conn, as_of: date) -> FollowUpReport:
    from ..repositories import repositories

    repo = repositories(conn)
    people = directory.load(conn)
    units = {u.id: u for u in repo["units"].list()}
    already = _escalation_levels(repo)
    report = FollowUpReport(as_of=as_of)

    for finding in sorted(repo["findings"].list(), key=lambda f: f.id):
        if finding.status != "open":
            continue
        unit = units.get(finding.auditable_unit_id)
        criticality = unit.attributes.get("criticality", "") if unit else ""
        rule = rule_for(finding.severity, criticality)
        days_to_target = (finding.target_date - as_of).days

        if 0 <= days_to_target <= rule.remind_before:
            record_reminder(repo, finding, as_of, people, report)
        elif days_to_target < 0:
            # Reminders continue after escalation; escalating is not a way of
            # handing the problem on and going quiet.
            record_reminder(repo, finding, as_of, people, report)
            overdue = -days_to_target
            if overdue >= rule.escalate_after:
                earned = min(
                    1 + (overdue - rule.escalate_after) // max(rule.escalate_after, 1),
                    2,
                )
                for level in range(already.get(finding.id, 0) + 1, earned + 1):
                    escalate(repo, finding, level, as_of, people, report)
                    already[finding.id] = level

    repo["audit"].append(
        actor="system", owner="follow-up", action="followup_completed",
        entity_type="Cycle", entity_id=as_of.isoformat(),
        detail={
            "as_of": as_of.isoformat(),
            "reminders": len(report.reminded),
            "escalations": len(report.escalated),
        },
    )
    return report


# --- the auditor's decisions -------------------------------------------------

def assign_severity(
    conn, finding_id: str, severity: Severity, *, by: str, remarks: str = ""
) -> Finding:
    """Severity is the auditor's call. The suggestion is only ever advice.

    Recording both means an override is visible in the trail rather than lost:
    "the model said Minor, the auditor said Major, here is who and when".
    """
    from ..repositories import repositories

    repo = repositories(conn)
    finding = repo["findings"].get(finding_id)
    if finding is None:
        raise ValueError(f"no such finding: {finding_id}")

    was, suggested = finding.severity, finding.suggested_severity
    finding.severity = severity
    finding.severity_assigned_by = by
    finding.target_date = target_date_for(finding.raised_at.date(), severity)
    repo["findings"].update(finding)
    repo["audit"].append(
        actor="user", owner=by, action="finding_severity_assigned",
        entity_type="Finding", entity_id=finding.id,
        detail={
            "severity": severity,
            "previous": was,
            "suggested": suggested,
            "overrode_suggestion": suggested is not None and suggested != severity,
            "assigned_by": by,
            "new_target_date": finding.target_date.isoformat(),
            "remarks": remarks,
        },
        actor_identity=by,
    )
    return finding


def set_progress(
    repo, finding: Finding, progress: str, *, by: str,
    detail: dict[str, Any] | None = None,
) -> Finding:
    """Record self-reported owner progress on a finding already in hand."""
    was = finding.owner_progress
    finding.owner_progress = progress  # type: ignore[assignment]
    repo["findings"].update(finding)
    repo["audit"].append(
        actor="user", owner=by, action="finding_progress_recorded",
        entity_type="Finding", entity_id=finding.id,
        detail={
            "progress": progress,
            "previous": was,
            "status": finding.status,
            "note": "self-reported by the owner; the finding stays open",
            **(detail or {}),
        },
        actor_identity=by,
    )
    return finding


def record_insufficient_round(
    repo, finding: Finding, *, by: str, remarks: str, assessment_id: str = "",
) -> Finding:
    """The auditor was not satisfied. Another round is owed.

    This is the transition the stakeholder was most specific about: insufficient
    evidence does not close anything and does not reset anything. The finding
    stays open, the gaps go back to the owner, and the round is counted — the
    same counter the reminders use, because both are the same thing from the
    owner's side: being chased again.
    """
    finding.follow_up_count += 1
    repo["findings"].update(finding)
    repo["audit"].append(
        actor="user", owner=by, action="evidence_found_insufficient",
        entity_type="Finding", entity_id=finding.id,
        detail={
            "remarks": remarks,
            "assessment_id": assessment_id,
            "follow_up_count": finding.follow_up_count,
            "status": finding.status,
            "note": "the finding remains open until the auditor is satisfied",
        },
        actor_identity=by,
    )
    return finding


def record_owner_progress(
    conn, finding_id: str, progress: str, *, by: str
) -> Finding:
    """What the owner says they have done. Advisory, and it closes nothing."""
    from ..repositories import repositories

    repo = repositories(conn)
    finding = repo["findings"].get(finding_id)
    if finding is None:
        raise ValueError(f"no such finding: {finding_id}")
    return set_progress(repo, finding, progress, by=by)


def close_on_repo(
    repo, finding: Finding, *, by: str, remarks: str, as_of: date
) -> Finding:
    """Close a finding a caller already has in hand.

    Same decision as `close_finding`, minus the lookup — S4 holds the finding
    when a waiver settles it and should not go back to the database for it.
    """
    if not remarks.strip():
        raise ValueError("a finding cannot be closed without closure remarks")
    finding.status = "closed"
    finding.closed_by = by
    finding.closed_at = datetime.combine(as_of, time(12, 0))
    finding.closure_remarks = remarks
    repo["findings"].update(finding)
    repo["audit"].append(
        actor="user", owner=by, action="finding_closed",
        entity_type="Finding", entity_id=finding.id,
        detail={
            "closed_by": by,
            "closure_remarks": remarks,
            "follow_up_count": finding.follow_up_count,
            "days_open": (as_of - finding.raised_at.date()).days,
            "owner_progress_at_closure": finding.owner_progress,
        },
        actor_identity=by,
    )
    return finding


def close_finding(
    conn, finding_id: str, *, by: str, remarks: str, as_of: date
) -> Finding:
    """Only ever the auditor, and only ever with remarks.

    Section 4: the finding stays open until the auditor is satisfied. Whether
    `by` is permitted to do this is checked in the next slice; the shape of the
    decision — who, when, and on what grounds — lands here.
    """
    from ..repositories import repositories

    repo = repositories(conn)
    finding = repo["findings"].get(finding_id)
    if finding is None:
        raise ValueError(f"no such finding: {finding_id}")
    if not remarks.strip():
        raise ValueError("a finding cannot be closed without closure remarks")

    finding.status = "closed"
    finding.closed_by = by
    finding.closed_at = datetime.combine(as_of, time(12, 0))
    finding.closure_remarks = remarks
    repo["findings"].update(finding)
    repo["audit"].append(
        actor="user", owner=by, action="finding_closed",
        entity_type="Finding", entity_id=finding.id,
        detail={
            "closed_by": by,
            "closure_remarks": remarks,
            "follow_up_count": finding.follow_up_count,
            "days_open": (as_of - finding.raised_at.date()).days,
            "owner_progress_at_closure": finding.owner_progress,
        },
        actor_identity=by,
    )
    return finding
