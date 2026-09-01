"""S1 — scheduling and trigger. Zero tokens, permanently.

One entry point, `run_cycle(conn, as_of)`, does the whole thing:

    expire lapsed exceptions -> generate instances -> advance the state machine
    -> escalate what is overdue -> route everything to its owning team

Cron, a dashboard button and a shell all call that same function, so there is no
second code path that could drift from the first. `advance_calendar` is a thin
wrapper that works out the next date and calls it. Whether a cycle was started
by a machine or a person is recorded on the cycle's own audit event.

The state machine:

    pending ---- evidence arrives ------> submitted ---- S3 assesses --> assessed
       |                                      ^
       |                                      |
       +---- due date passes ----> overdue ---+
       |                              |
       |                              +--- escalates up the owner chain
       |
       +---- an approved exception covers it ----> waived

Instances are keyed on control x area x period, so running a cycle twice for
the same period is a no-op rather than a duplicate. Nothing is ever sent: a
notification is a logged payload, and that is the whole integration story.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any

from ..entities import CheckInstance, ComplianceException, ControlDefinition, ProcessArea
from ..periods import due_date, periods_for
from .applicability import applicability_matrix, validate_expressions

#: What a cycle can be started by. Recorded on the cycle audit event so the
#: trail distinguishes a scheduled sweep from somebody pressing a button.
TRIGGERS = ("scheduler", "manual", "cli")

#: Terminal for S1's purposes: once assessed or waived, scheduling is done with
#: an instance and only S2/S3/S4 touch it again.
SETTLED = ("assessed", "waived")


@dataclass(frozen=True)
class SchedulePolicy:
    year: int = 2026
    due_soon_days: int = 7
    escalate_after_days: int = 14
    max_escalation_level: int = 2


DEFAULT_POLICY = SchedulePolicy()


@dataclass(frozen=True)
class Notification:
    """A routed alert. Logged, never sent — see section 11, no email."""

    kind: str
    to_team: str
    to_owner: str
    entity_type: str
    entity_id: str
    subject: str
    as_of: date

    def payload(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "to_team": self.to_team,
            "to_owner": self.to_owner,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "subject": self.subject,
            "as_of": self.as_of.isoformat(),
            "delivery": "logged_not_sent",
        }


@dataclass
class CycleResult:
    as_of: date
    trigger: str
    created: list[str] = field(default_factory=list)
    suppressed: list[str] = field(default_factory=list)
    transitions: list[tuple[str, str, str]] = field(default_factory=list)
    escalations: list[tuple[str, int]] = field(default_factory=list)
    expired_exceptions: list[str] = field(default_factory=list)
    notifications: list[Notification] = field(default_factory=list)

    def counts(self) -> dict[str, int]:
        return {
            "created": len(self.created),
            "suppressed": len(self.suppressed),
            "transitions": len(self.transitions),
            "escalations": len(self.escalations),
            "expired_exceptions": len(self.expired_exceptions),
            "notifications": len(self.notifications),
        }


def instance_id(control_id: str, area_id: str, period: str) -> str:
    """Deterministic and readable: the key *is* the identity.

    Because it is derived rather than allocated, generating the same period
    twice produces the same id, and the UNIQUE constraint on
    (control, area, period) is belt to this braces.
    """
    control = control_id.removeprefix("CTRL-")
    area = area_id.removeprefix("AREA-")
    return f"CHK-{control}-{area}-{period}"


def owner_chain(area: ProcessArea) -> list[tuple[str, str]]:
    """Who hears about it, in order. Level 0 owns it; 1 and 2 get escalations."""
    return [
        (area.owner_name, area.owner_team),
        (f"Head of {area.owner_team}", area.owner_team),
        ("Group Compliance", "Group Compliance"),
    ]


def covers(
    exception: ComplianceException, control_id: str, area_id: str, period_end: date
) -> bool:
    """Whether an approved deviation excuses this control, area and period.

    Judged on the granted window, not on today's status, so that flipping an
    exception to `expired` cannot retroactively un-excuse the periods it
    legitimately covered — otherwise the first cycle after EXC-002 lapses would
    backfill Q1 and Q2 instances that were properly waived at the time.
    A revoked exception covers nothing: it was withdrawn, not served out.
    """
    return (
        exception.status in ("active", "expired")
        and exception.control_id == control_id
        and exception.process_area_id == area_id
        and exception.granted_at <= period_end <= exception.expires_at
    )


def _log(repo, notification: Notification, actor: str = "system") -> None:
    repo["audit"].append(
        actor=actor,
        owner=notification.to_owner,
        action="notification_logged",
        entity_type=notification.entity_type,
        entity_id=notification.entity_id,
        detail=notification.payload(),
    )


def _expire_exceptions(repo, as_of: date, result: CycleResult) -> None:
    """A lapsed waiver is news. It raises an alert of its own."""
    for exception in repo["exceptions"].list(status="active"):
        if exception.expires_at >= as_of:
            continue
        exception.status = "expired"
        repo["exceptions"].update(exception)
        result.expired_exceptions.append(exception.id)

        area = repo["areas"].get(exception.process_area_id)
        repo["audit"].append(
            actor="system",
            owner=area.owner_name,
            action="exception_expired",
            entity_type="ComplianceException",
            entity_id=exception.id,
            detail={
                "control_id": exception.control_id,
                "process_area_id": exception.process_area_id,
                "expired_on": exception.expires_at.isoformat(),
                "detected_on": as_of.isoformat(),
                "consequence": "control returns to the schedule from the next period",
            },
        )
        notification = Notification(
            kind="exception_expired",
            to_team=area.owner_team,
            to_owner=area.owner_name,
            entity_type="ComplianceException",
            entity_id=exception.id,
            subject=(
                f"Exception {exception.id} for {exception.control_id} in"
                f" {exception.process_area_id} lapsed on {exception.expires_at}"
                f" — the control is due again"
            ),
            as_of=as_of,
        )
        result.notifications.append(notification)
        _log(repo, notification)


def _open_periods(control: ControlDefinition, policy: SchedulePolicy, as_of: date):
    """Periods that have started by `as_of`. A period generates when it opens."""
    return [
        period
        for period in periods_for(control.frequency, policy.year)
        if period.start <= as_of
    ]


def _generate(
    repo,
    as_of: date,
    policy: SchedulePolicy,
    result: CycleResult,
    controls: dict[str, ControlDefinition],
    areas: dict[str, ProcessArea],
    exceptions: list[ComplianceException],
    existing: dict[str, CheckInstance],
) -> None:
    matrix = applicability_matrix(list(controls.values()), list(areas.values()))
    for area_id, control_ids in matrix.items():
        area = areas[area_id]
        for control_id in control_ids:
            control = controls[control_id]
            for period in _open_periods(control, policy, as_of):
                excuse = next(
                    (e for e in exceptions if covers(e, control_id, area_id, period.end)),
                    None,
                )
                if excuse is not None:
                    result.suppressed.append(
                        instance_id(control_id, area_id, period.label)
                    )
                    continue

                identifier = instance_id(control_id, area_id, period.label)
                if identifier in existing:
                    continue  # already generated in an earlier cycle

                instance = CheckInstance(
                    id=identifier,
                    control_id=control_id,
                    process_area_id=area_id,
                    period=period.label,
                    due_date=due_date(period, control.grace_days),
                    status="pending",
                    assigned_team=area.owner_team,
                    owner_name=area.owner_name,
                )
                repo["instances"].add(instance)
                existing[identifier] = instance
                result.created.append(identifier)

                repo["audit"].append(
                    actor="system",
                    owner=area.owner_name,
                    action="check_instance_created",
                    entity_type="CheckInstance",
                    entity_id=identifier,
                    detail={
                        "control_id": control_id,
                        "process_area_id": area_id,
                        "period": period.label,
                        "due_date": instance.due_date.isoformat(),
                        "frequency": control.frequency,
                    },
                )
                notification = Notification(
                    kind="assigned",
                    to_team=area.owner_team,
                    to_owner=area.owner_name,
                    entity_type="CheckInstance",
                    entity_id=identifier,
                    subject=(
                        f"{control.title} for {area.name} ({period.label}) is due"
                        f" {instance.due_date}"
                    ),
                    as_of=as_of,
                )
                result.notifications.append(notification)
                _log(repo, notification)


def _transition(
    repo, instance: CheckInstance, to: str, actor: str, owner: str, detail: dict
) -> None:
    was = instance.status
    instance.status = to
    repo["instances"].update(instance)
    repo["audit"].append(
        actor=actor,
        owner=owner,
        action=f"check_instance_{to}",
        entity_type="CheckInstance",
        entity_id=instance.id,
        detail={"from_status": was, "to_status": to, **detail},
    )


def _escalated_levels(repo) -> dict[str, int]:
    """Highest level each instance has already been escalated to.

    Read back out of the audit trail rather than stored on the instance: the
    trail is the record of what happened, so a cycle that has already escalated
    to level 2 does not do it again on the next run.
    """
    levels: dict[str, int] = {}
    for event in repo["audit"].read_all():
        if event.action == "check_instance_escalated":
            level = int(event.detail.get("level", 0))
            levels[event.entity_id] = max(levels.get(event.entity_id, 0), level)
    return levels


def _advance_states(
    repo,
    as_of: date,
    policy: SchedulePolicy,
    result: CycleResult,
    areas: dict[str, ProcessArea],
    exceptions: list[ComplianceException],
    instances: dict[str, CheckInstance],
    period_ends: dict[tuple[str, str], date],
) -> None:
    submissions = repo["submissions"].list()
    arrived: dict[tuple[str, str, str], Any] = {}
    for submission in submissions:
        if submission.submitted_at.date() > as_of:
            continue  # not filed yet, as far as this cycle is concerned
        key = (submission.control_id, submission.process_area_id, submission.period)
        prior = arrived.get(key)
        if prior is None or submission.submitted_at < prior.submitted_at:
            arrived[key] = submission

    already = _escalated_levels(repo)

    for instance in sorted(instances.values(), key=lambda i: i.id):
        if instance.status in SETTLED:
            continue
        area = areas[instance.process_area_id]
        key = (instance.control_id, instance.process_area_id, instance.period)
        period_end = period_ends[(instance.control_id, instance.period)]

        excuse = next(
            (
                e
                for e in exceptions
                if covers(e, instance.control_id, instance.process_area_id, period_end)
            ),
            None,
        )
        if excuse is not None:
            _transition(repo, instance, "waived", "system", area.owner_name,
                        {"exception_id": excuse.id, "as_of": as_of.isoformat()})
            result.transitions.append((instance.id, "waived", excuse.id))
            continue

        submission = arrived.get(key)
        if submission is not None and instance.status != "submitted":
            _transition(repo, instance, "submitted", "user", submission.author,
                        {"submission_id": submission.id,
                         "submitted_at": submission.submitted_at.isoformat(),
                         "on_time": submission.submitted_at.date() <= instance.due_date})
            result.transitions.append((instance.id, "submitted", submission.id))
            continue

        if submission is None and as_of > instance.due_date:
            if instance.status != "overdue":
                days = (as_of - instance.due_date).days
                _transition(repo, instance, "overdue", "system", area.owner_name,
                            {"due_date": instance.due_date.isoformat(),
                             "days_overdue": days, "as_of": as_of.isoformat()})
                result.transitions.append((instance.id, "overdue", f"{days}d"))
                notification = Notification(
                    kind="overdue",
                    to_team=instance.assigned_team,
                    to_owner=instance.owner_name,
                    entity_type="CheckInstance",
                    entity_id=instance.id,
                    subject=(
                        f"{instance.control_id} for {instance.process_area_id}"
                        f" ({instance.period}) is {days} day(s) overdue"
                    ),
                    as_of=as_of,
                )
                result.notifications.append(notification)
                _log(repo, notification)
            _escalate(repo, instance, as_of, policy, result, area, already)
            continue

        if instance.status == "pending":
            until_due = (instance.due_date - as_of).days
            if 0 <= until_due <= policy.due_soon_days:
                notification = Notification(
                    kind="due_soon",
                    to_team=instance.assigned_team,
                    to_owner=instance.owner_name,
                    entity_type="CheckInstance",
                    entity_id=instance.id,
                    subject=(
                        f"{instance.control_id} for {instance.process_area_id}"
                        f" ({instance.period}) is due in {until_due} day(s)"
                    ),
                    as_of=as_of,
                )
                result.notifications.append(notification)
                _log(repo, notification)


def _escalate(
    repo,
    instance: CheckInstance,
    as_of: date,
    policy: SchedulePolicy,
    result: CycleResult,
    area: ProcessArea,
    already: dict[str, int],
) -> None:
    """Walk an overdue instance up the owner chain, one level per interval."""
    days_overdue = (as_of - instance.due_date).days
    earned = min(
        days_overdue // policy.escalate_after_days, policy.max_escalation_level
    )
    chain = owner_chain(area)
    for level in range(already.get(instance.id, 0) + 1, earned + 1):
        name, team = chain[min(level, len(chain) - 1)]
        repo["audit"].append(
            actor="system",
            owner=name,
            action="check_instance_escalated",
            entity_type="CheckInstance",
            entity_id=instance.id,
            detail={
                "level": level,
                "escalated_to": name,
                "team": team,
                "days_overdue": days_overdue,
                "threshold_days": policy.escalate_after_days * level,
            },
        )
        notification = Notification(
            kind="escalation",
            to_team=team,
            to_owner=name,
            entity_type="CheckInstance",
            entity_id=instance.id,
            subject=(
                f"Escalation level {level}: {instance.control_id} for"
                f" {instance.process_area_id} ({instance.period}) is"
                f" {days_overdue} day(s) overdue"
            ),
            as_of=as_of,
        )
        result.notifications.append(notification)
        _log(repo, notification)
        result.escalations.append((instance.id, level))
        already[instance.id] = level


def run_cycle(
    conn,
    as_of: date,
    *,
    trigger: str = "scheduler",
    actor: str = "system",
    policy: SchedulePolicy = DEFAULT_POLICY,
) -> CycleResult:
    """The entire scheduling cycle. The only entry point there is."""
    if trigger not in TRIGGERS:
        raise ValueError(f"unknown trigger {trigger!r}; expected one of {TRIGGERS}")

    from ..repositories import repositories

    repo = repositories(conn)
    controls = {c.id: c for c in repo["controls"].list()}
    areas = {a.id: a for a in repo["areas"].list()}

    problems = validate_expressions(list(controls.values()))
    if problems:
        raise ValueError("invalid applies_when expressions: " + "; ".join(problems))

    result = CycleResult(as_of=as_of, trigger=trigger)
    repo["audit"].append(
        actor=actor,
        owner="scheduler" if actor == "system" else actor,
        action="cycle_started",
        entity_type="Cycle",
        entity_id=as_of.isoformat(),
        detail={"as_of": as_of.isoformat(), "trigger": trigger,
                "human_triggered": actor != "system"},
    )

    _expire_exceptions(repo, as_of, result)
    exceptions = repo["exceptions"].list()
    existing = {i.id: i for i in repo["instances"].list()}

    _generate(repo, as_of, policy, result, controls, areas, exceptions, existing)

    period_ends = {
        (control.id, period.label): period.end
        for control in controls.values()
        for period in periods_for(control.frequency, policy.year)
    }
    instances = {i.id: i for i in repo["instances"].list()}
    _advance_states(repo, as_of, policy, result, areas, exceptions, instances,
                    period_ends)

    repo["audit"].append(
        actor=actor,
        owner="scheduler" if actor == "system" else actor,
        action="cycle_completed",
        entity_type="Cycle",
        entity_id=as_of.isoformat(),
        detail={"as_of": as_of.isoformat(), "trigger": trigger,
                "human_triggered": actor != "system", **result.counts()},
    )
    return result


def last_cycle_date(conn) -> date | None:
    """Where the simulated calendar currently stands, read off the trail."""
    from ..repositories import repositories

    completed = [
        e for e in repositories(conn)["audit"].read_all()
        if e.action == "cycle_completed"
    ]
    return date.fromisoformat(completed[-1].detail["as_of"]) if completed else None


def advance_calendar(
    conn,
    days: int,
    *,
    from_date: date | None = None,
    trigger: str = "manual",
    actor: str = "user",
    policy: SchedulePolicy = DEFAULT_POLICY,
) -> CycleResult:
    """Move the simulated clock forward and run one cycle at the new date.

    Contains no scheduling logic of its own — it works out the date and calls
    `run_cycle`. That is the point: the demo's calendar button, a cron entry and
    a shell invocation are the same code path, so none of them can drift.
    """
    start = from_date or last_cycle_date(conn)
    if start is None:
        raise ValueError("no prior cycle; call run_cycle with an explicit date first")
    return run_cycle(
        conn, start + timedelta(days=days), trigger=trigger, actor=actor, policy=policy
    )
