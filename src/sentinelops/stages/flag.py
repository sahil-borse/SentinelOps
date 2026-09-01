"""S4 — flag, route, and raise the work. Zero tokens.

The statement asks for three categories and this stage keeps them three, in the
data and not only in a report:

    gap       the content was assessed and fails the criteria
    exception an approved deviation, or one that has lapsed
    overdue   nothing was filed by the due date — raised with no model call

Severity, in one sentence: **the control's own weight, multiplied by how badly
the verdict failed, by how critical the area is, and by how long it has been
outstanding.** Every term is a documented constant, so the same instance on the
same day always scores the same, and anybody can check the arithmetic:

    severity = severity_weight x verdict x criticality x overdue

It is stamped onto the Flag rather than recomputed on demand, because the last
term moves with the calendar and an escalation decision has to still be
explicable next month.

Every gap and every overdue raises an Action against the owning team. An
approved deviation does not: there is nothing to remediate about a waiver that
was granted. A lapsed one has already raised its own alert in S1 and the control
has returned to the schedule, which is the remedy.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any

from ..entities import Action, CheckInstance, ControlDefinition, Finding, Flag

#: How badly each verdict failed. Compliant never reaches this stage.
VERDICT_WEIGHT: dict[str, float] = {
    "gap": 1.0,
    "insufficient_evidence": 0.8,
    "partial": 0.6,
    "waived": 0.3,
    "compliant": 0.0,
}

#: What the area is worth protecting.
CRITICALITY_WEIGHT: dict[str, float] = {
    "low": 0.5,
    "medium": 0.75,
    "high": 1.0,
    "critical": 1.5,
}

#: Age multiplier, 1.0 on the due date rising to 2.0 at ninety days late and no
#: further — after three months the problem is the same problem.
OVERDUE_CAP_DAYS = 90

#: Severity bands, for routing and for the dashboard. Upper bound exclusive.
BANDS: tuple[tuple[float, str], ...] = (
    (1.5, "low"),
    (3.0, "medium"),
    (6.0, "high"),
    (float("inf"), "critical"),
)

#: How long the owning team gets, by band. A critical gap does not get a month.
ACTION_SLA_DAYS: dict[str, int] = {
    "critical": 7,
    "high": 14,
    "medium": 30,
    "low": 60,
}

#: An Action runs its own clock, separate from the check that produced it.
ACTION_ESCALATE_AFTER_DAYS = 10

OPEN_ACTION_STATUSES = (
    "raised",
    "assigned",
    "in_progress",
    "remediation_submitted",
    "reassessed",
    "escalated",
)


@dataclass
class FlagReport:
    as_of: date
    flags: list[str] = field(default_factory=list)
    by_category: dict[str, int] = field(
        default_factory=lambda: {"gap": 0, "exception": 0, "overdue": 0}
    )
    by_band: dict[str, int] = field(
        default_factory=lambda: {b: 0 for _, b in BANDS}
    )
    actions_raised: list[str] = field(default_factory=list)
    actions_escalated: list[str] = field(default_factory=list)
    actions_resolved_by_waiver: list[str] = field(default_factory=list)


def overdue_multiplier(days_overdue: int) -> float:
    """1.0 on the day it was due, 2.0 once it is ninety days late."""
    return 1.0 + min(max(days_overdue, 0), OVERDUE_CAP_DAYS) / OVERDUE_CAP_DAYS


def severity_band(severity: float) -> str:
    for ceiling, name in BANDS:
        if severity < ceiling:
            return name
    return BANDS[-1][1]


def severity_of(
    control: ControlDefinition,
    criticality: str,
    verdict: str,
    days_overdue: int,
) -> float:
    """The documented formula, and nothing else."""
    return round(
        control.severity_weight
        * VERDICT_WEIGHT.get(verdict, 0.0)
        * CRITICALITY_WEIGHT.get(criticality, 1.0)
        * overdue_multiplier(days_overdue),
        3,
    )


def explain_severity(
    control: ControlDefinition, criticality: str, verdict: str, days_overdue: int
) -> str:
    """The arithmetic, spelled out, so a number is never just asserted."""
    return (
        f"severity_weight {control.severity_weight}"
        f" x verdict {verdict} {VERDICT_WEIGHT.get(verdict, 0.0)}"
        f" x criticality {criticality} {CRITICALITY_WEIGHT.get(criticality, 1.0)}"
        f" x overdue {days_overdue}d {overdue_multiplier(days_overdue):.2f}"
        f" = {severity_of(control, criticality, verdict, days_overdue)}"
    )


def categorise(finding: Finding) -> str:
    """Which of the three this finding is. Exactly one, never two.

    `no_evidence` is the overdue case and is the only one that reaches this
    stage without a model ever having been asked. Everything else that failed
    is a gap, including evidence of the wrong type or too stale to read: the
    criteria went unmet either way.
    """
    if finding.decided_by == "no_evidence":
        return "overdue"
    return "gap"


def _flag(
    repo,
    *,
    category: str,
    control: ControlDefinition,
    area,
    severity: float,
    rationale: str,
    as_of: date,
    instance: CheckInstance | None = None,
    finding: Finding | None = None,
    exception_id: str | None = None,
    flag_id: str | None = None,
) -> Flag:
    anchor = instance.id if instance is not None else exception_id
    flag = Flag(
        id=flag_id or f"FLG-{category.upper()}-{anchor}",
        category=category,
        control_id=control.id,
        process_area_id=area.id,
        severity=severity,
        severity_band=severity_band(severity),
        rationale=rationale,
        raised_at=datetime.combine(as_of, datetime.min.time()),
        owner_team=area.owner_team,
        owner_name=area.owner_name,
        check_instance_id=instance.id if instance is not None else None,
        finding_id=finding.id if finding is not None else None,
        exception_id=exception_id,
        status="open",
    )
    repo["flags"].add(flag)
    repo["audit"].append(
        actor="system",
        owner=area.owner_name,
        action="flag_raised",
        entity_type="Flag",
        entity_id=flag.id,
        detail={
            "category": category,
            "severity": severity,
            "severity_band": flag.severity_band,
            "rationale": rationale,
            "check_instance_id": flag.check_instance_id,
            "finding_id": flag.finding_id,
            "exception_id": exception_id,
        },
    )
    return flag


def raise_action(
    repo, flag: Flag, instance: CheckInstance, finding: Finding, as_of: date
) -> Action:
    """Create the work, then route it. Two transitions, two events.

    `raised` is the record existing; `assigned` is somebody having been told.
    They are separate because in a real organisation they come apart, and the
    trail should be able to show a week between them.
    """
    sla = ACTION_SLA_DAYS[flag.severity_band]
    action = Action(
        id=f"ACT-{flag.check_instance_id.removeprefix('CHK-')}",
        finding_id=finding.id,
        title=finding.recommended_action
        or f"Remediate {flag.category} on {instance.control_id} ({instance.period})",
        owner_team=flag.owner_team,
        owner_name=flag.owner_name,
        due_date=as_of + timedelta(days=sla),
        status="raised",
    )
    repo["actions"].add(action)
    repo["audit"].append(
        actor="system",
        owner=action.owner_name,
        action="action_raised",
        entity_type="Action",
        entity_id=action.id,
        detail={
            "flag_id": flag.id,
            "finding_id": finding.id,
            "check_instance_id": instance.id,
            "category": flag.category,
            "severity": flag.severity,
            "severity_band": flag.severity_band,
            "sla_days": sla,
            "due_date": action.due_date.isoformat(),
        },
    )
    transition(
        repo, action, "assigned", actor="system", owner=action.owner_name,
        detail={
            "owner_team": action.owner_team,
            "routed_on": as_of.isoformat(),
            "delivery": "logged_not_sent",
        },
    )
    return action


def transition(
    repo, action: Action, to: str, *, actor: str, owner: str, detail: dict[str, Any]
) -> Action:
    """Move an Action, recording who moved it."""
    was = action.status
    action.status = to
    repo["actions"].update(action)
    repo["audit"].append(
        actor=actor,
        owner=owner,
        action=f"action_{to}",
        entity_type="Action",
        entity_id=action.id,
        detail={"from_status": was, "to_status": to, **detail},
    )
    return action


def resolve(
    repo, action: Action, note: str, as_of: date, *, owner: str | None = None
) -> Action:
    action.resolution_note = note
    action.resolved_at = datetime.combine(as_of, datetime.min.time())
    return transition(
        repo, action, "resolved",
        actor="system", owner=owner or action.owner_name,
        detail={"resolution_note": note, "resolved_at": as_of.isoformat()},
    )


def run(conn, as_of: date) -> FlagReport:
    """Flag everything decided, raise the work, and chase what is late."""
    from ..repositories import simulated_clock

    with simulated_clock(datetime.combine(as_of, datetime.min.time().replace(hour=5))):
        return _run(conn, as_of)


def _run(conn, as_of: date) -> FlagReport:
    from ..repositories import repositories

    repo = repositories(conn)
    controls = {c.id: c for c in repo["controls"].list()}
    areas = {a.id: a for a in repo["areas"].list()}
    instances = {i.id: i for i in repo["instances"].list()}
    existing = {f.id for f in repo["flags"].list()}
    actioned = {a.finding_id for a in repo["actions"].list()}
    report = FlagReport(as_of=as_of)

    # --- gaps and overdues, from findings ---------------------------------
    findings = repo["findings"].list()
    # A finding that something else supersedes is history: the re-assessment
    # that replaced it is the current answer, and flagging both would double
    # count one problem. Note the direction — it is the *superseded* one that is
    # skipped, not the one carrying the pointer.
    superseded = {f.supersedes_finding_id for f in findings if f.supersedes_finding_id}
    open_action_ids = {
        a.id for a in repo["actions"].list() if a.status in OPEN_ACTION_STATUSES
    }

    for finding in sorted(findings, key=lambda f: f.id):
        if finding.verdict == "compliant" or finding.id in superseded:
            continue
        instance = instances.get(finding.check_instance_id)
        if instance is None:
            continue
        control, area = controls[instance.control_id], areas[instance.process_area_id]

        category = categorise(finding)
        days_overdue = max((as_of - instance.due_date).days, 0)
        severity = severity_of(
            control, area.attributes["criticality"], finding.verdict, days_overdue
        )
        # Keyed on the finding, not the instance: a failed remediation produces
        # a new finding and deserves a new flag rather than silently reusing the
        # one that was closed.
        flag_id = f"FLG-{category.upper()}-{finding.id}"
        if flag_id in existing:
            continue

        flag = _flag(
            repo, category=category, control=control, area=area, severity=severity,
            rationale=explain_severity(
                control, area.attributes["criticality"], finding.verdict, days_overdue
            ),
            as_of=as_of, instance=instance, finding=finding, flag_id=flag_id,
        )
        report.flags.append(flag.id)
        report.by_category[category] += 1
        report.by_band[flag.severity_band] += 1

        # One open Action per instance. A second failure on the same check is
        # the same piece of work, not a new one.
        action_id = f"ACT-{instance.id.removeprefix('CHK-')}"
        if finding.id not in actioned and action_id not in open_action_ids:
            action = raise_action(repo, flag, instance, finding, as_of)
            open_action_ids.add(action.id)
            report.actions_raised.append(action.id)

    # --- exceptions: approved deviations and lapsed ones -------------------
    for instance in sorted(instances.values(), key=lambda i: i.id):
        if instance.status != "waived":
            continue
        control, area = controls[instance.control_id], areas[instance.process_area_id]
        flag_id = f"FLG-EXCEPTION-{instance.id}"
        if flag_id in existing:
            continue
        severity = severity_of(control, area.attributes["criticality"], "waived", 0)
        flag = _flag(
            repo, category="exception", control=control, area=area,
            severity=severity,
            rationale=(
                "Approved deviation: the obligation was excused rather than met. "
                + explain_severity(control, area.attributes["criticality"], "waived", 0)
            ),
            as_of=as_of, instance=instance,
        )
        report.flags.append(flag.id)
        report.by_category["exception"] += 1
        report.by_band[flag.severity_band] += 1
        _close_out_waived(repo, instance, flag, as_of, report)

    for exception in sorted(repo["exceptions"].list(), key=lambda e: e.id):
        if exception.status != "expired":
            continue
        flag_id = f"FLG-EXCEPTION-{exception.id}"
        if flag_id in existing:
            continue
        control = controls.get(exception.control_id)
        area = areas.get(exception.process_area_id)
        if control is None or area is None:
            continue
        severity = severity_of(
            control, area.attributes["criticality"], "insufficient_evidence", 0
        )
        flag = _flag(
            repo, category="exception", control=control, area=area,
            severity=severity,
            rationale=(
                f"Deviation {exception.id} lapsed on {exception.expires_at}; the "
                "control has returned to the schedule."
            ),
            as_of=as_of, exception_id=exception.id,
        )
        report.flags.append(flag.id)
        report.by_category["exception"] += 1
        report.by_band[flag.severity_band] += 1

    _escalate_actions(repo, as_of, report)
    repo["audit"].append(
        actor="system",
        owner="flagging",
        action="flagging_completed",
        entity_type="Cycle",
        entity_id=as_of.isoformat(),
        detail={
            "as_of": as_of.isoformat(),
            "flags_raised": len(report.flags),
            "actions_raised": len(report.actions_raised),
            "actions_escalated": len(report.actions_escalated),
            "actions_resolved_by_waiver": len(report.actions_resolved_by_waiver),
            **{f"category_{k}": v for k, v in report.by_category.items()},
            **{f"band_{k}": v for k, v in report.by_band.items()},
        },
    )
    return report


def _close_out_waived(
    repo, instance: CheckInstance, exception_flag: Flag, as_of: date,
    report: FlagReport,
) -> None:
    """A waiver settles whatever the failure had already set in motion.

    The gap or overdue flag closes and the action resolves, because the work
    they were chasing is no longer owed. The *finding* is untouched: the
    non-compliance was real when it was recorded, and a waiver excuses an
    obligation rather than rewriting history.
    """
    for flag in repo["flags"].list(check_instance_id=instance.id):
        if flag.category == "exception" or flag.status != "open":
            continue
        flag.status = "closed"
        repo["flags"].update(flag)
        repo["audit"].append(
            actor="system",
            owner=instance.owner_name,
            action="flag_closed",
            entity_type="Flag",
            entity_id=flag.id,
            detail={
                "closed_by": exception_flag.id,
                "reason": "the obligation was waived under an approved deviation",
                "category": flag.category,
            },
        )

    action = repo["actions"].get(f"ACT-{instance.id.removeprefix('CHK-')}")
    if action is not None and action.status not in ("resolved",):
        resolve(
            repo, action,
            f"Closed without remediation: the obligation was waived "
            f"({exception_flag.id}). The finding it arose from stands.",
            as_of, owner=instance.owner_name,
        )
        report.actions_resolved_by_waiver.append(action.id)


def _escalate_actions(repo, as_of: date, report: FlagReport) -> None:
    """An Action runs its own clock.

    A check that went overdue and an action that has since been ignored are two
    different failures with two different owners, so they escalate separately.
    """
    for action in sorted(repo["actions"].list(), key=lambda a: a.id):
        if action.status in ("resolved", "escalated"):
            continue
        late_by = (as_of - action.due_date).days
        if late_by < ACTION_ESCALATE_AFTER_DAYS:
            continue
        transition(
            repo, action, "escalated", actor="system", owner="Group Compliance",
            detail={
                "days_past_action_due_date": late_by,
                "action_due_date": action.due_date.isoformat(),
                "threshold_days": ACTION_ESCALATE_AFTER_DAYS,
                "escalated_to": "Group Compliance",
                "reason": "the remediation itself is late, independently of the check",
            },
        )
        report.actions_escalated.append(action.id)


def open_actions(conn) -> list[Action]:
    from ..repositories import repositories

    return [
        a
        for a in repositories(conn)["actions"].list()
        if a.status in OPEN_ACTION_STATUSES
    ]
