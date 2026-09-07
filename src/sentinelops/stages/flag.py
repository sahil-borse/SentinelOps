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

Every gap and every overdue raises a **Finding** against the owning unit. An
approved deviation does not: there is nothing to remediate about a waiver that
was granted. A lapsed one has already raised its own alert in S1 and the control
has returned to the schedule, which is the remedy.

A finding is Open or Closed and nothing else, and only an auditor closes one
(`stages.followup`). The computed severity here is a *suggestion*; the auditor
assigns the severity that counts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime

from .. import directory
from ..entities import (
    ASSESSOR_IDENTITY, Assessment, CheckInstance, ControlDefinition, Finding,
    Flag,
)
from . import followup

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
    findings_raised: list[str] = field(default_factory=list)
    findings_closed_by_waiver: list[str] = field(default_factory=list)


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


def categorise(finding: Assessment) -> str:
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
    people,
    *,
    category: str,
    control: ControlDefinition,
    area,
    severity: float,
    rationale: str,
    as_of: date,
    instance: CheckInstance | None = None,
    finding: Assessment | None = None,
    exception_id: str | None = None,
    flag_id: str | None = None,
) -> Flag:
    anchor = instance.id if instance is not None else exception_id
    flag = Flag(
        id=flag_id or f"FLG-{category.upper()}-{anchor}",
        category=category,
        control_id=control.id,
        auditable_unit_id=area.id,
        severity=severity,
        severity_band=severity_band(severity),
        rationale=rationale,
        raised_at=datetime.combine(as_of, datetime.min.time()),
        owner_team=area.name,
        owner_name=people.owner_name(area),
        check_instance_id=instance.id if instance is not None else None,
        assessment_id=finding.id if finding is not None else None,
        exception_id=exception_id,
        status="open",
    )
    repo["flags"].add(flag)
    repo["audit"].append(
        actor="system",
        owner=people.owner_name(area),
        action="flag_raised",
        entity_type="Flag",
        entity_id=flag.id,
        detail={
            "category": category,
            "severity": severity,
            "severity_band": flag.severity_band,
            "rationale": rationale,
            "check_instance_id": flag.check_instance_id,
            "assessment_id": flag.assessment_id,
            "exception_id": exception_id,
        },
    )
    return flag


#: The computed severity band maps onto the three severities the auditor works
#: in. It is a *suggestion* — section 3 is explicit that severity is assigned by
#: the auditor and the model's view is advisory. Recording both is what makes an
#: override visible later.
BAND_TO_SEVERITY: dict[str, str] = {
    "critical": "Major",
    "high": "Major",
    "medium": "Minor",
    "low": "Observation",
}


def describe(control: ControlDefinition, instance: CheckInstance,
             assessment: Assessment) -> str:
    """What this finding is, in words that distinguish it from the next one.

    An earlier version used the assessment's rationale alone. That reads fine on
    one finding and is useless across a portfolio: the rationale is generated
    from a small set of phrasings, so eighty findings shared four sentences
    between them. Anything that compares findings — recurrence detection above
    all — was then comparing boilerplate and matching everything to everything.

    So the description names the obligation, the period and the specific gaps
    the assessment recorded. That is what an auditor would have written, and it
    is what makes two findings comparable or not.
    """
    gaps = [g for g in assessment.gaps if g]
    detail = " ".join(gaps) if gaps else assessment.rationale
    return (
        f"{control.title} — {instance.period}, {instance.assigned_team}. "
        f"{detail}".strip()
    )


def raise_finding(
    repo,
    people,
    flag: Flag,
    instance: CheckInstance,
    assessment: Assessment,
    unit,
    as_of: date,
    control: ControlDefinition | None = None,
) -> Finding:
    """Raise the finding, suggest a severity, and let the auditor decide it.

    The finding is the tracked object now, not a task hung off a verdict. It
    carries the description in the words of whoever raised it, the plan agreed
    with the owner, and a target date derived from the severity — and it stays
    open until an auditor says otherwise.
    """
    suggested = BAND_TO_SEVERITY.get(flag.severity_band, "Observation")
    criticality = unit.attributes.get("criticality", "")
    raised_at = datetime.combine(as_of, datetime.min.time().replace(hour=9))
    finding = Finding(
        id=f"FND-{flag.check_instance_id.removeprefix('CHK-')}",
        source="activity_assessment",
        auditable_unit_id=instance.auditable_unit_id,
        description=(
            describe(control, instance, assessment) if control is not None
            else assessment.rationale
            or f"{flag.category} on {instance.control_id} for {instance.period}"
        ),
        raised_by=ASSESSOR_IDENTITY,
        raised_at=raised_at,
        owner_identity=unit.owner_identity,
        target_date=followup.target_date_for(as_of, suggested, criticality),
        check_instance_id=instance.id,
        suggested_severity=suggested,
        agreed_action_plan=assessment.recommended_action,
        status="open",
    )
    repo["findings"].add(finding)
    repo["audit"].append(
        actor="ai",
        owner=people.name(finding.owner_identity),
        action="finding_raised",
        entity_type="Finding",
        entity_id=finding.id,
        detail={
            "flag_id": flag.id,
            "source": finding.source,
            "check_instance_id": instance.id,
            "auditable_unit_id": finding.auditable_unit_id,
            "category": flag.category,
            "description": finding.description,
            "suggested_severity": suggested,
            "computed_severity_score": flag.severity,
            "target_date": finding.target_date.isoformat(),
            "owner_identity": finding.owner_identity,
            "status": "open",
        },
        actor_identity=ASSESSOR_IDENTITY,
    )

    # The suggestion is advice; an auditor puts their name to the severity. In
    # the automated track that is the PA/InfoSec on rota, and the trail records
    # whether they took the suggestion or overrode it.
    auditors = people.by_role("pa_infosec")
    if auditors:
        _assign_inline(repo, finding, suggested, auditors[0].id)
    return finding


def _assign_inline(repo, finding: Finding, severity: str, by: str) -> None:
    """Record the auditor's severity decision without a second connection."""
    finding.severity = severity  # type: ignore[assignment]
    finding.severity_assigned_by = by
    repo["findings"].update(finding)
    repo["audit"].append(
        actor="user",
        owner=by,
        action="finding_severity_assigned",
        entity_type="Finding",
        entity_id=finding.id,
        detail={
            "severity": severity,
            "previous": None,
            "suggested": finding.suggested_severity,
            "overrode_suggestion": False,
            "assigned_by": by,
            "new_target_date": finding.target_date.isoformat(),
            "remarks": "accepted the suggested severity",
        },
        actor_identity=by,
    )


def run(conn, as_of: date) -> FlagReport:
    """Flag everything decided, raise the work, and chase what is late."""
    from ..repositories import simulated_clock

    with simulated_clock(datetime.combine(as_of, datetime.min.time().replace(hour=5))):
        return _run(conn, as_of)


def _run(conn, as_of: date) -> FlagReport:
    from ..repositories import repositories

    repo = repositories(conn)
    people = directory.load(conn)
    controls = {c.id: c for c in repo["controls"].list()}
    areas = {a.id: a for a in repo["units"].list()}
    instances = {i.id: i for i in repo["instances"].list()}
    existing = {f.id for f in repo["flags"].list()}
    report = FlagReport(as_of=as_of)

    # --- gaps and overdues, from findings ---------------------------------
    findings = repo["assessments"].list()
    # A finding that something else supersedes is history: the re-assessment
    # that replaced it is the current answer, and flagging both would double
    # count one problem. Note the direction — it is the *superseded* one that is
    # skipped, not the one carrying the pointer.
    superseded = {f.supersedes_assessment_id for f in findings if f.supersedes_assessment_id}
    # Every finding ever raised, open or closed. The id is derived from the
    # check instance, so this is also the "has this obligation already been
    # written up?" question: a finding stays open across evidence rounds and a
    # second failure on the same check is the same piece of work.
    raised_already = {f.id for f in repo["findings"].list()}

    for finding in sorted(findings, key=lambda f: f.id):
        if finding.verdict == "compliant" or finding.id in superseded:
            continue
        instance = instances.get(finding.check_instance_id)
        if instance is None:
            continue
        control, area = controls[instance.control_id], areas[instance.auditable_unit_id]

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
            repo, people, category=category, control=control, area=area, severity=severity,
            rationale=explain_severity(
                control, area.attributes["criticality"], finding.verdict, days_overdue
            ),
            as_of=as_of, instance=instance, finding=finding, flag_id=flag_id,
        )
        report.flags.append(flag.id)
        report.by_category[category] += 1
        report.by_band[flag.severity_band] += 1

        finding_id = f"FND-{instance.id.removeprefix('CHK-')}"
        if finding_id not in raised_already:
            raised = raise_finding(
                repo, people, flag, instance, finding, area, as_of,
                control=control,
            )
            raised_already.add(raised.id)
            report.findings_raised.append(raised.id)

    # --- exceptions: approved deviations and lapsed ones -------------------
    for instance in sorted(instances.values(), key=lambda i: i.id):
        if instance.status != "waived":
            continue
        control, area = controls[instance.control_id], areas[instance.auditable_unit_id]
        flag_id = f"FLG-EXCEPTION-{instance.id}"
        if flag_id in existing:
            continue
        severity = severity_of(control, area.attributes["criticality"], "waived", 0)
        flag = _flag(
            repo, people, category="exception", control=control, area=area,
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
        _close_out_waived(repo, people, instance, flag, as_of, report)

    for exception in sorted(repo["exceptions"].list(), key=lambda e: e.id):
        if exception.status != "expired":
            continue
        flag_id = f"FLG-EXCEPTION-{exception.id}"
        if flag_id in existing:
            continue
        control = controls.get(exception.control_id)
        area = areas.get(exception.auditable_unit_id)
        if control is None or area is None:
            continue
        severity = severity_of(
            control, area.attributes["criticality"], "insufficient_evidence", 0
        )
        flag = _flag(
            repo, people, category="exception", control=control, area=area,
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

    repo["audit"].append(
        actor="system",
        owner="flagging",
        action="flagging_completed",
        entity_type="Cycle",
        entity_id=as_of.isoformat(),
        detail={
            "as_of": as_of.isoformat(),
            "flags_raised": len(report.flags),
            "findings_raised": len(report.findings_raised),
            "findings_closed_by_waiver": len(report.findings_closed_by_waiver),
            **{f"category_{k}": v for k, v in report.by_category.items()},
            **{f"band_{k}": v for k, v in report.by_band.items()},
        },
    )
    return report


def _close_out_waived(
    repo, people, instance: CheckInstance, exception_flag: Flag, as_of: date,
    report: FlagReport,
) -> None:
    """A waiver settles whatever the failure had already set in motion.

    The gap or overdue flag closes and the finding closes, because the
    obligation is no longer owed. The *assessment* is untouched: the
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
            owner=people.owner_name(
                next(u for u in repo["units"].list()
                     if u.id == instance.auditable_unit_id)
            ),
            action="flag_closed",
            entity_type="Flag",
            entity_id=flag.id,
            detail={
                "closed_by": exception_flag.id,
                "reason": "the obligation was waived under an approved deviation",
                "category": flag.category,
            },
        )

    finding = repo["findings"].get(f"FND-{instance.id.removeprefix('CHK-')}")
    if finding is not None and finding.status == "open":
        auditors = people.by_role("pa_infosec")
        followup.close_on_repo(
            repo, finding,
            by=auditors[0].id if auditors else "ID-SYSTEM",
            remarks=(
                f"Closed without remediation: the obligation was waived "
                f"({exception_flag.id}). The assessment it arose from stands."
            ),
            as_of=as_of,
        )
        report.findings_closed_by_waiver.append(finding.id)


def open_findings(conn) -> list:
    from ..repositories import repositories

    return [f for f in repositories(conn)["findings"].list() if f.status == "open"]
