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
from datetime import date, datetime, time, timedelta
from typing import Any

from ..entities import CheckInstance, ComplianceException, ControlDefinition, AuditableUnit
from .. import directory
from ..directory import Directory
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


def owner_chain(unit: AuditableUnit, people: Directory) -> list[tuple[str, str]]:
    """Who hears about it, in order. Level 0 owns it; 1 and 2 get escalations.

    Walks `reports_to` rather than assembling a manager from a team name, so
    every rung is a person who exists. If the reporting line runs out before the
    top rung, the last real person is repeated rather than inventing one.
    """
    chain = [
        (person.name, unit.name if person.auditable_unit else "Group Compliance")
        for person in people.escalation_chain(unit.owner_identity)
    ]
    if not chain:
        chain = [(people.owner_name(unit), unit.name)]
    while len(chain) < 3:
        chain.append(chain[-1])
    return chain


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
        and exception.auditable_unit_id == area_id
        and exception.granted_at <= period_end <= exception.expires_at
    )


def waives(
    exception: ComplianceException,
    control_id: str,
    area_id: str,
    period_end: date,
    as_of: date,
) -> bool:
    """Whether an approved deviation excuses an obligation that is already open.

    The complement of `covers`. Suppression answers "should this check ever have
    been raised?" and is settled at generation; a waiver answers "is this open
    check excused right now?" and is settled every cycle. EXC-004 is the case
    that needs it: granted on 11 May, weeks after the 2026-Q1 rotation fell due
    on 15 April, so there is nothing to suppress — the check is already sitting
    there, overdue.

    An exception waives a period when the exception is in force today
    (`granted_at <= as_of <= expires_at`) and the period closed no later than
    the exception's own expiry. A period ending after the waiver lapses is not
    excused by it: that obligation outlives the deviation.

    Once expired the exception waives nothing further, which is deliberate — a
    temporary deviation running out means the control is due again, exactly as
    it does for EXC-002. Instances already waived stay waived: that period's
    obligation was formally discharged while the waiver held.
    """
    return (
        exception.status == "active"
        and exception.control_id == control_id
        and exception.auditable_unit_id == area_id
        and period_end <= exception.expires_at
        and exception.granted_at <= as_of <= exception.expires_at
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


def _expire_exceptions(
    repo, as_of: date, result: CycleResult, people: Directory
) -> None:
    """A lapsed waiver is news. It raises an alert of its own."""
    for exception in repo["exceptions"].list(status="active"):
        if exception.expires_at >= as_of:
            continue
        exception.status = "expired"
        repo["exceptions"].update(exception)
        result.expired_exceptions.append(exception.id)

        area = repo["units"].get(exception.auditable_unit_id)
        repo["audit"].append(
            actor="system",
            owner=people.owner_name(area),
            action="exception_expired",
            entity_type="ComplianceException",
            entity_id=exception.id,
            detail={
                "control_id": exception.control_id,
                "auditable_unit_id": exception.auditable_unit_id,
                "expired_on": exception.expires_at.isoformat(),
                "detected_on": as_of.isoformat(),
                "consequence": "control returns to the schedule from the next period",
            },
        )
        notification = Notification(
            kind="exception_expired",
            to_team=area.name,
            to_owner=people.owner_name(area),
            entity_type="ComplianceException",
            entity_id=exception.id,
            subject=(
                f"Exception {exception.id} for {exception.control_id} in"
                f" {exception.auditable_unit_id} lapsed on {exception.expires_at}"
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
    people: Directory,
    as_of: date,
    policy: SchedulePolicy,
    result: CycleResult,
    controls: dict[str, ControlDefinition],
    areas: dict[str, AuditableUnit],
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
                    auditable_unit_id=area_id,
                    period=period.label,
                    due_date=due_date(period, control.grace_days),
                    status="pending",
                    assigned_team=area.name,
                    owner_name=people.owner_name(area),
                )
                repo["instances"].add(instance)
                existing[identifier] = instance
                result.created.append(identifier)

                repo["audit"].append(
                    actor="system",
                    owner=people.owner_name(area),
                    action="check_instance_created",
                    entity_type="CheckInstance",
                    entity_id=identifier,
                    detail={
                        "control_id": control_id,
                        "control_title": control.title,
                        "auditable_unit_id": area_id,
                        "area_name": area.name,
                        "period": period.label,
                        "due_date": instance.due_date.isoformat(),
                        "frequency": control.frequency,
                        "assigned_team": area.name,
                    },
                )
                notification = Notification(
                    kind="assigned",
                    to_team=area.name,
                    to_owner=people.owner_name(area),
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
    people: Directory,
    as_of: date,
    policy: SchedulePolicy,
    result: CycleResult,
    areas: dict[str, AuditableUnit],
    exceptions: list[ComplianceException],
    instances: dict[str, CheckInstance],
    period_ends: dict[tuple[str, str], date],
) -> None:
    submissions = repo["submissions"].list()
    arrived: dict[tuple[str, str, str], Any] = {}
    for submission in submissions:
        if submission.submitted_at.date() > as_of:
            continue  # not filed yet, as far as this cycle is concerned
        key = (submission.control_id, submission.auditable_unit_id, submission.period)
        prior = arrived.get(key)
        if prior is None or submission.submitted_at < prior.submitted_at:
            arrived[key] = submission

    already = _escalated_levels(repo)

    # A waiver can arrive after a check has already been closed as failed. The
    # non-compliance was real and stays on the record; the obligation is then
    # formally excused. Without this an approved deviation granted for an
    # outstanding item excuses nothing, because S2 has already settled it.
    current_findings = {}
    for finding in repo["assessments"].list():
        held = current_findings.get(finding.check_instance_id)
        if held is None or finding.id > held.id:
            current_findings[finding.check_instance_id] = finding

    for instance in sorted(instances.values(), key=lambda i: i.id):
        if instance.status == "waived":
            continue
        if instance.status == "assessed":
            finding = current_findings.get(instance.id)
            if finding is None or finding.verdict == "compliant":
                continue
            period_end = period_ends[(instance.control_id, instance.period)]
            excuse = next(
                (
                    e
                    for e in exceptions
                    if waives(
                        e, instance.control_id, instance.auditable_unit_id,
                        period_end, as_of,
                    )
                ),
                None,
            )
            if excuse is None:
                continue
            area = areas[instance.auditable_unit_id]
            _transition(
                repo, instance, "waived", "system", people.owner_name(area),
                {
                    "exception_id": excuse.id,
                    "approved_by": excuse.approved_by,
                    "granted_at": excuse.granted_at.isoformat(),
                    "expires_at": excuse.expires_at.isoformat(),
                    "excused_assessment_id": finding.id,
                    "excused_verdict": finding.verdict,
                    "as_of": as_of.isoformat(),
                    "note": (
                        "the finding stands on the record; the obligation it "
                        "reported is formally excused"
                    ),
                },
            )
            result.transitions.append((instance.id, "waived", excuse.id))
            notification = Notification(
                kind="waived",
                to_team=instance.assigned_team,
                to_owner=instance.owner_name,
                entity_type="CheckInstance",
                entity_id=instance.id,
                subject=(
                    f"{instance.control_id} for {instance.auditable_unit_id}"
                    f" ({instance.period}) — {finding.verdict} excused under"
                    f" {excuse.id}, approved by {excuse.approved_by}"
                ),
                as_of=as_of,
            )
            result.notifications.append(notification)
            _log(repo, notification)
            continue

        area = areas[instance.auditable_unit_id]
        key = (instance.control_id, instance.auditable_unit_id, instance.period)
        period_end = period_ends[(instance.control_id, instance.period)]

        if instance.status in ("pending", "overdue"):
            excuse = next(
                (
                    e
                    for e in exceptions
                    if waives(
                        e, instance.control_id, instance.auditable_unit_id,
                        period_end, as_of,
                    )
                ),
                None,
            )
            if excuse is not None:
                _transition(
                    repo, instance, "waived", "system", people.owner_name(area),
                    {
                        "exception_id": excuse.id,
                        "approved_by": excuse.approved_by,
                        "granted_at": excuse.granted_at.isoformat(),
                        "expires_at": excuse.expires_at.isoformat(),
                        "was_overdue_by_days": max(
                            (as_of - instance.due_date).days, 0
                        ),
                        "as_of": as_of.isoformat(),
                    },
                )
                result.transitions.append((instance.id, "waived", excuse.id))
                notification = Notification(
                    kind="waived",
                    to_team=instance.assigned_team,
                    to_owner=instance.owner_name,
                    entity_type="CheckInstance",
                    entity_id=instance.id,
                    subject=(
                        f"{instance.control_id} for {instance.auditable_unit_id}"
                        f" ({instance.period}) is waived under {excuse.id},"
                        f" approved by {excuse.approved_by}"
                    ),
                    as_of=as_of,
                )
                result.notifications.append(notification)
                _log(repo, notification)
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
                _transition(repo, instance, "overdue", "system", people.owner_name(area),
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
                        f"{instance.control_id} for {instance.auditable_unit_id}"
                        f" ({instance.period}) is {days} day(s) overdue"
                    ),
                    as_of=as_of,
                )
                result.notifications.append(notification)
                _log(repo, notification)
            _escalate(repo, people, instance, as_of, policy, result, area, already)
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
                        f"{instance.control_id} for {instance.auditable_unit_id}"
                        f" ({instance.period}) is due in {until_due} day(s)"
                    ),
                    as_of=as_of,
                )
                result.notifications.append(notification)
                _log(repo, notification)


def _escalate(
    repo,
    people: Directory,
    instance: CheckInstance,
    as_of: date,
    policy: SchedulePolicy,
    result: CycleResult,
    area: AuditableUnit,
    already: dict[str, int],
) -> None:
    """Walk an overdue instance up the owner chain, one level per interval."""
    days_overdue = (as_of - instance.due_date).days
    earned = min(
        days_overdue // policy.escalate_after_days, policy.max_escalation_level
    )
    chain = owner_chain(area, people)
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
                f" {instance.auditable_unit_id} ({instance.period}) is"
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
    """The entire scheduling cycle. The only entry point there is.

    Everything the cycle records is stamped with the cycle's own date rather
    than the wall clock of a machine replaying a simulated year in seconds —
    see `repositories.simulated_clock`.
    """
    from ..repositories import simulated_clock

    with simulated_clock(datetime.combine(as_of, time(2, 0))):
        return _run_cycle(
            conn, as_of, trigger=trigger, actor=actor, policy=policy
        )


def _run_cycle(
    conn,
    as_of: date,
    *,
    trigger: str,
    actor: str,
    policy: SchedulePolicy,
) -> CycleResult:
    if trigger not in TRIGGERS:
        raise ValueError(f"unknown trigger {trigger!r}; expected one of {TRIGGERS}")

    from ..repositories import repositories

    repo = repositories(conn)
    people = directory.load(conn)
    controls = {c.id: c for c in repo["controls"].list()}
    areas = {a.id: a for a in repo["units"].list()}

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

    _expire_exceptions(repo, as_of, result, people)
    exceptions = repo["exceptions"].list()
    existing = {i.id: i for i in repo["instances"].list()}

    _generate(repo, people, as_of, policy, result, controls, areas, exceptions,
              existing)

    period_ends = {
        (control.id, period.label): period.end
        for control in controls.values()
        for period in periods_for(control.frequency, policy.year)
    }
    instances = {i.id: i for i in repo["instances"].list()}
    _advance_states(repo, people, as_of, policy, result, areas, exceptions,
                    instances, period_ends)

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
