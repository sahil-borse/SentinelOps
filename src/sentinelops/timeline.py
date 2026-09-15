"""The simulated calendar's next meaningful moment. Deterministic.

Section 2 puts scheduling and reminder and escalation timing on the never-AI
list, and this is timing: arithmetic over each open finding's section 5 rule and
the audit programme's planned dates.

**Milestones, not every reminder.** Once a finding is inside its reminder
window, the chase reminds its owner on every cycle until it closes — so "the
next reminder" is always tomorrow, and a jump to it would be a fixed one-day
step in disguise. The events here are the moments something *changes*:

    reminder     the first day the chase starts reminding
    target       the target date itself
    escalation   the first day each escalation level is earned
    audit        a planned audit's date

**The planner reads the engine's own rule.** Escalation dates come from
`followup.escalation_on`, which is defined as the first day
`followup.escalation_level_earned` — the function the chase itself calls —
reaches a level. A planner with its own copy of the arithmetic would one day
promise an escalation the engine does not deliver.

A jump is a normal cycle run on the named day, so whatever else falls due that
day happens too. What cannot be planned is not listed: a finding raised because
evidence fails assessment exists only once the cycle that assesses it has run.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .stages import followup

#: On one day, the more serious event is named first.
KIND_ORDER: tuple[str, ...] = ("escalation", "target", "reminder", "audit")


@dataclass(frozen=True)
class Event:
    day: date
    kind: str
    subject: str
    title: str
    detail: str
    level: int = 0


@dataclass(frozen=True)
class Moment:
    """The earliest day with something on it, and everything on that day."""

    day: date
    events: tuple[Event, ...]

    @property
    def headline(self) -> Event:
        return self.events[0]


def _day(value: date) -> str:
    return f"{value.day} {value:%b %Y}"


def upcoming(conn, after: date, *, subject: str | None = None) -> list[Event]:
    """Every milestone strictly after `after`, soonest first."""
    from .repositories import repositories

    repo = repositories(conn)
    units = {unit.id: unit for unit in repo["units"].list()}
    reached = followup.escalation_levels(repo)
    events: list[Event] = []

    for finding in repo["findings"].list(status="open"):
        if subject and finding.id != subject:
            continue
        unit = units.get(finding.auditable_unit_id)
        criticality = unit.attributes.get("criticality", "") if unit else ""
        rule = followup.rule_for(finding.severity, criticality)
        detail = (
            f"{unit.name if unit else finding.auditable_unit_id} · "
            f"{finding.severity or 'Unassigned'} · target {_day(finding.target_date)}"
        )
        first = followup.first_reminder_on(finding.target_date, rule)
        if after < first < finding.target_date:
            events.append(Event(first, "reminder", finding.id, "First reminder", detail))
        if finding.target_date > after:
            events.append(
                Event(finding.target_date, "target", finding.id, "Target date reached", detail)
            )
        for level in range(reached.get(finding.id, 0) + 1, followup.MAX_ESCALATION_LEVEL + 1):
            on = followup.escalation_on(finding.target_date, rule, level)
            if on > after:
                events.append(
                    Event(on, "escalation", finding.id, f"Escalation, level {level}", detail, level)
                )

    for audit in repo["audits"].list():
        if audit.status == "completed" or audit.planned_date <= after:
            continue
        if subject and audit.id != subject:
            continue
        scope = ", ".join(units[u].name if u in units else u for u in audit.scope)
        events.append(Event(
            audit.planned_date, "audit", audit.id, "Audit due",
            f"{audit.title or audit.kind.replace('_', ' ')} · {scope}",
        ))

    return sorted(events, key=lambda e: (e.day, KIND_ORDER.index(e.kind), e.subject, e.level))


def next_moment(conn, after: date, *, subject: str | None = None) -> Moment | None:
    """The earliest day after `after` with a milestone, or None if there is none."""
    events = upcoming(conn, after, subject=subject)
    if not events:
        return None
    day = events[0].day
    return Moment(day, tuple(event for event in events if event.day == day))
