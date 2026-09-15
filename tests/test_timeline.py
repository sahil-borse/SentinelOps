"""Slice 18: the next meaningful moment, jumped to; and the scenario restored exactly."""

import hashlib
from datetime import date, datetime, time, timedelta

import pytest

from sentinelops import directory, timeline
from sentinelops.db import SCHEMA, connect
from sentinelops.entities import Finding
from sentinelops.repositories import repositories, simulated_clock
from sentinelops.stages import followup
from sentinelops.synth import generate_corpus, seed_database
from sentinelops.ui import service


@pytest.fixture(scope="module")
def corpus():
    return generate_corpus()


def _finding(conn, *, severity, target, finding_id="FND-TIMELINE-1", unit_id="AREA-HR"):
    repo = repositories(conn)
    people = directory.load(conn)
    unit = repo["units"].get(unit_id)
    finding = Finding(
        id=finding_id, source="audit", auditable_unit_id=unit_id,
        description="Leavers' accounts were not revoked on the day they left.",
        raised_by=people.by_role("pa_infosec")[0].id,
        raised_at=datetime.combine(target - timedelta(days=14), time(9, 0)),
        owner_identity=unit.owner_identity, target_date=target, severity=severity,
        agreed_action_plan="Revoke on the leaving date and reconcile monthly.",
    )
    with simulated_clock(finding.raised_at):
        repo["findings"].add(finding)
    return finding


# --- the planner reads the engine's own rule --------------------------------------

def _as_it_was(rule, overdue):
    """The arithmetic `_run` held inline before it was named."""
    if overdue < rule.escalate_after:
        return 0
    return min(1 + (overdue - rule.escalate_after) // max(rule.escalate_after, 1), 2)


def test_the_named_rule_is_the_one_the_chase_always_used():
    for rule in followup.SEVERITY_RULES.values():
        for overdue in range(-40, 60):
            assert followup.escalation_level_earned(rule, overdue) == _as_it_was(rule, overdue)
            days_to_target = -overdue
            assert followup.reminder_due(rule, days_to_target) == (
                0 <= days_to_target <= rule.remind_before or days_to_target < 0
            )


def test_each_escalation_date_is_the_first_day_its_level_is_earned():
    target = date(2027, 4, 1)
    for rule in followup.SEVERITY_RULES.values():
        for level in range(1, followup.MAX_ESCALATION_LEVEL + 1):
            overdue = (followup.escalation_on(target, rule, level) - target).days
            assert followup.escalation_level_earned(rule, overdue) == level
            assert followup.escalation_level_earned(rule, overdue - 1) == level - 1
        first = followup.first_reminder_on(target, rule)
        assert followup.reminder_due(rule, (target - first).days)
        assert not followup.reminder_due(rule, (target - first).days + 1)


def test_a_findings_milestones_are_its_rule_applied(conn, corpus):
    seed_database(conn, corpus)
    target = date(2027, 6, 10)
    finding = _finding(conn, severity="Minor", target=target)

    mine = [e for e in timeline.upcoming(conn, date(2027, 5, 1)) if e.subject == finding.id]
    assert [(e.kind, e.day, e.level) for e in mine] == [
        ("reminder", target - timedelta(days=3), 0),
        ("target", target, 0),
        ("escalation", target + timedelta(days=5), 1),
        ("escalation", target + timedelta(days=10), 2),
    ]
    later = [e for e in timeline.upcoming(conn, target) if e.subject == finding.id]
    assert [e.kind for e in later] == ["escalation", "escalation"], "nothing on or before the date"


def test_closed_findings_and_levels_already_reached_are_not_events(conn, corpus):
    seed_database(conn, corpus)
    repo = repositories(conn)
    finding = _finding(conn, severity="Major", target=date(2027, 6, 10))
    with simulated_clock(datetime(2027, 6, 13, 5, 30)):
        repo["audit"].append(
            actor="system", owner="follow-up", action="finding_escalated",
            entity_type="Finding", entity_id=finding.id, detail={"level": 1},
        )
    levels = [e.level for e in timeline.upcoming(conn, date(2027, 5, 1))
              if e.subject == finding.id and e.kind == "escalation"]
    assert levels == [2]

    finding.status = "closed"
    repo["findings"].update(finding)
    assert not [e for e in timeline.upcoming(conn, date(2027, 5, 1)) if e.subject == finding.id]


def test_a_planned_audit_is_an_event_on_its_planned_date(conn, corpus):
    seed_database(conn, corpus)
    audit = next(a for a in repositories(conn)["audits"].list() if a.status != "completed")
    events = timeline.upcoming(conn, audit.planned_date - timedelta(days=1), subject=audit.id)
    assert [(e.kind, e.day) for e in events] == [("audit", audit.planned_date)]


def test_the_next_moment_is_the_earliest_day_with_everything_on_it(conn, corpus):
    seed_database(conn, corpus)
    after = date(2027, 4, 15)
    events = timeline.upcoming(conn, after)
    moment = timeline.next_moment(conn, after)
    assert moment.day == events[0].day and moment.day > after
    assert list(moment.events) == [e for e in events if e.day == moment.day]
    ranks = [timeline.KIND_ORDER.index(e.kind) for e in moment.events]
    assert ranks == sorted(ranks), "the more serious event is named first"


# --- the jump lands where it said, and the named event happens -------------------------

def test_jumping_walks_one_findings_reminder_and_escalation_timeline(conn, corpus):
    seed_database(conn, corpus)
    service.tick(conn, date(2026, 1, 28))
    repo = repositories(conn)
    finding = _finding(conn, severity="Minor", target=date(2026, 3, 16),
                       finding_id="FND-TIMELINE-JUMP")

    sequence = []
    while (jumped := service.jump_to_next_event(conn, subject=finding.id)) is not None:
        sequence.append(jumped)
        assert service.current_date(conn) == jumped.day, "the jump lands where it said"
        trail = [e for e in repo["audit"].read_all()
                 if e.entity_id == finding.id and e.ts.date() == jumped.day]
        for event in jumped.moment.events:
            if event.kind in ("reminder", "target"):
                assert any(e.action == "finding_reminder_sent" for e in trail), event
            if event.kind == "escalation":
                assert any(e.action == "finding_escalated" and e.detail["level"] == event.level
                           for e in trail), event
        assert len(sequence) < 10, "the planner must run out of milestones"

    assert [(j.moment.headline.kind, j.day) for j in sequence] == [
        ("reminder", date(2026, 3, 13)),
        ("target", date(2026, 3, 16)),
        ("escalation", date(2026, 3, 21)),
        ("escalation", date(2026, 3, 26)),
    ]
    gaps = [(later.day - earlier.day).days for earlier, later in zip(sequence, sequence[1:])]
    assert gaps == [3, 5, 5], "the calendar moves to the next milestone, not by a fixed step"


def test_nothing_ahead_means_no_jump(conn, corpus):
    seed_database(conn, corpus)
    assert service.jump_to_next_event(conn, subject="FND-DOES-NOT-EXIST") is None


# --- the scenario resets to exactly what was seeded -------------------------------------

def test_seeding_the_scenario_is_deterministic(corpus):
    first, second = connect(":memory:"), connect(":memory:")
    seed_database(first, corpus)
    seed_database(second, generate_corpus())
    assert service.state_digest(first) == service.state_digest(second)


def test_reset_restores_the_exact_seeded_state(tmp_path, monkeypatch, corpus):
    monkeypatch.setattr(service, "DB_PATH", tmp_path / "demo.db")
    service.reset_scenario()
    conn = service.open_database()
    seeded = service.state_digest(conn)

    fresh = connect(":memory:")
    seed_database(fresh, corpus)
    assert seeded == service.state_digest(fresh), "the snapshot is the seeded state"

    service.tick(conn, date(2026, 1, 28))
    assert service.state_digest(conn) != seeded
    conn.close()

    service.reset_scenario()
    conn = service.open_database()
    assert service.state_digest(conn) == seeded
    assert not repositories(conn)["instances"].list()
    conn.close()


def test_the_snapshot_is_keyed_on_the_corpus_and_the_schema(tmp_path, monkeypatch, corpus):
    monkeypatch.setattr(service, "DB_PATH", tmp_path / "demo.db")
    name = service.snapshot_path(corpus).name
    assert corpus.fingerprint()[:12] in name
    assert hashlib.sha256(SCHEMA.encode("utf-8")).hexdigest()[:8] in name
    path = service.ensure_snapshot()
    assert path.exists() and path.parent == tmp_path
    assert service.ensure_snapshot().stat().st_mtime == path.stat().st_mtime, "built once"
