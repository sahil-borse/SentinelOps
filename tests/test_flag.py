"""S4 — three categories kept distinct, and a severity anyone can check."""

from datetime import date, timedelta

import pytest

from sentinelops.entities import ControlDefinition
from sentinelops.repositories import repositories
from sentinelops.stages.assess import run as assess
from sentinelops.stages.flag import (
    ACTION_ESCALATE_AFTER_DAYS,
    ACTION_SLA_DAYS,
    CRITICALITY_WEIGHT,
    OPEN_ACTION_STATUSES,
    OVERDUE_CAP_DAYS,
    VERDICT_WEIGHT,
    categorise,
    explain_severity,
    overdue_multiplier,
    severity_band,
    severity_of,
)
from sentinelops.stages.flag import run as flag_run
from sentinelops.stages.prescreen import run as prescreen
from sentinelops.stages.trigger import run_cycle
from sentinelops.synth import generate_corpus, seed_database

END_OF_STORY = date(2027, 3, 31)
LATER = date(2027, 6, 30)


@pytest.fixture(scope="module")
def corpus():
    return generate_corpus()


@pytest.fixture()
def flagged(conn, corpus):
    seed_database(conn, corpus)
    for month in range(1, 13):
        run_cycle(conn, date(2026, month, 28))
    run_cycle(conn, END_OF_STORY)
    screen = prescreen(conn, END_OF_STORY)
    assess(conn, screen.to_assess, END_OF_STORY)
    return conn, flag_run(conn, END_OF_STORY)


# --- three categories, kept three ------------------------------------------

def test_all_three_categories_are_present(flagged):
    conn, report = flagged
    assert report.by_category["gap"] > 0
    assert report.by_category["exception"] > 0
    assert report.by_category["overdue"] > 0


def test_every_flag_carries_exactly_one_category(flagged):
    conn, report = flagged
    flags = repositories(conn)["flags"].list()
    assert len(flags) == len(report.flags)
    for flag in flags:
        assert flag.category in ("gap", "exception", "overdue")


def test_the_categories_are_distinct_in_the_data(flagged):
    """One instance never appears under two categories at once."""
    conn, _ = flagged
    seen: dict[str, str] = {}
    for flag in repositories(conn)["flags"].list():
        key = flag.check_instance_id or flag.exception_id
        assert key not in seen or seen[key] == flag.category
        seen[key] = flag.category


def test_overdue_means_nothing_was_filed_and_no_model_was_asked(flagged):
    conn, _ = flagged
    repo = repositories(conn)
    findings = {f.id: f for f in repo["findings"].list()}
    overdue = [f for f in repo["flags"].list() if f.category == "overdue"]
    assert overdue
    for flag in overdue:
        finding = findings[flag.finding_id]
        assert finding.decided_by == "no_evidence"
        assert finding.verdict == "insufficient_evidence"
        evidence = repo["evidence"].list(check_instance_id=flag.check_instance_id)
        assert evidence == []


def test_gap_means_content_was_assessed_and_failed(flagged):
    conn, _ = flagged
    repo = repositories(conn)
    findings = {f.id: f for f in repo["findings"].list()}
    gaps = [f for f in repo["flags"].list() if f.category == "gap"]
    assert gaps
    for flag in gaps:
        finding = findings[flag.finding_id]
        assert finding.verdict != "compliant"
        assert finding.decided_by != "no_evidence"


def test_exception_covers_both_the_approved_and_the_lapsed(flagged):
    conn, _ = flagged
    repo = repositories(conn)
    exceptions = [f for f in repo["flags"].list() if f.category == "exception"]
    waived = [f for f in exceptions if f.check_instance_id]
    lapsed = [f for f in exceptions if f.exception_id]

    assert waived, "an instance excused by an approved deviation"
    assert lapsed, "a deviation that has run out"
    assert len(waived) + len(lapsed) == len(exceptions)
    assert all(
        repo["instances"].get(f.check_instance_id).status == "waived" for f in waived
    )
    assert all(
        repo["exceptions"].get(f.exception_id).status == "expired" for f in lapsed
    )


def test_categorise_is_a_total_function(corpus):
    from sentinelops.entities import Finding

    for decided_by in ("no_evidence", "wrong_evidence_type", "stale_evidence",
                       "structured_threshold", "s3_model", "carried_forward"):
        finding = Finding(id="F", check_instance_id="I", verdict="gap",
                          confidence=1.0, rationale="r", decided_by=decided_by)
        assert categorise(finding) in ("gap", "overdue")


# --- severity ---------------------------------------------------------------

def test_the_formula_is_exactly_the_documented_product(corpus):
    control = next(c for c in corpus.controls if c.id == "CTRL-ACCESS-REVIEW")
    assert control.severity_weight == 3.0
    # 3.0 weight x gap 1.0 x critical 1.5 x 45 days overdue (1.5) = 6.75
    assert severity_of(control, "critical", "gap", 45) == pytest.approx(6.75)
    assert severity_of(control, "critical", "gap", 45) == pytest.approx(
        control.severity_weight
        * VERDICT_WEIGHT["gap"]
        * CRITICALITY_WEIGHT["critical"]
        * overdue_multiplier(45)
    )


def test_severity_is_deterministic(corpus):
    control = corpus.controls[0]
    first = severity_of(control, "high", "gap", 12)
    for _ in range(5):
        assert severity_of(control, "high", "gap", 12) == first


def test_each_term_moves_severity_in_the_right_direction(corpus):
    control = next(c for c in corpus.controls if c.id == "CTRL-DATA-RETENTION")
    base = severity_of(control, "medium", "partial", 0)
    assert severity_of(control, "critical", "partial", 0) > base   # criticality
    assert severity_of(control, "medium", "gap", 0) > base          # verdict
    assert severity_of(control, "medium", "partial", 30) > base     # duration


def test_the_overdue_multiplier_is_capped(corpus):
    assert overdue_multiplier(0) == 1.0
    assert overdue_multiplier(-5) == 1.0
    assert overdue_multiplier(OVERDUE_CAP_DAYS) == 2.0
    assert overdue_multiplier(OVERDUE_CAP_DAYS * 10) == 2.0


def test_a_compliant_verdict_scores_zero(corpus):
    assert severity_of(corpus.controls[0], "critical", "compliant", 90) == 0.0


def test_bands_partition_the_range():
    assert severity_band(0.1) == "low"
    assert severity_band(2.0) == "medium"
    assert severity_band(4.0) == "high"
    assert severity_band(9.0) == "critical"


def test_the_severity_is_explained_not_just_asserted(corpus, flagged):
    conn, _ = flagged
    control = next(c for c in corpus.controls if c.id == "CTRL-ACCESS-REVIEW")
    text = explain_severity(control, "critical", "gap", 45)
    for fragment in ("severity_weight 3.0", "verdict gap 1.0",
                     "criticality critical 1.5", "overdue 45d 1.50", "= 6.75"):
        assert fragment in text

    for flag in repositories(conn)["flags"].list():
        if flag.category != "exception":
            assert "severity_weight" in flag.rationale
            assert f"= {flag.severity}" in flag.rationale


def test_severity_is_stamped_not_recomputed(flagged):
    """It depends on elapsed time, so it must be frozen when raised."""
    conn, _ = flagged
    before = {f.id: f.severity for f in repositories(conn)["flags"].list()}
    flag_run(conn, LATER)
    after = {f.id: f.severity for f in repositories(conn)["flags"].list()}
    for flag_id, severity in before.items():
        assert after[flag_id] == severity


def test_every_flag_lands_in_a_band(flagged):
    conn, report = flagged
    assert sum(report.by_band.values()) == len(report.flags)
    for flag in repositories(conn)["flags"].list():
        assert flag.severity_band == severity_band(flag.severity)


# --- actions ----------------------------------------------------------------

def test_every_gap_and_overdue_raises_an_action(flagged):
    conn, report = flagged
    expected = report.by_category["gap"] + report.by_category["overdue"]
    assert len(report.actions_raised) == expected


def test_an_approved_deviation_raises_no_action(flagged):
    conn, _ = flagged
    repo = repositories(conn)
    actioned = {a.id for a in repo["actions"].list()}
    for flag in repo["flags"].list():
        if flag.category == "exception" and flag.check_instance_id:
            assert (
                f"ACT-{flag.check_instance_id.removeprefix('CHK-')}" not in actioned
            )


def test_an_action_is_assigned_to_the_owning_team(flagged, corpus):
    conn, _ = flagged
    repo = repositories(conn)
    teams = {a.id: a.owner_team for a in corpus.areas}
    for flag in repo["flags"].list():
        if flag.category == "exception":
            continue
        action = repo["actions"].get(
            f"ACT-{flag.check_instance_id.removeprefix('CHK-')}"
        )
        instance = repo["instances"].get(flag.check_instance_id)
        assert action.owner_team == teams[instance.process_area_id]


def test_the_due_date_tightens_with_severity(flagged):
    conn, _ = flagged
    repo = repositories(conn)
    for flag in repo["flags"].list():
        if flag.category == "exception":
            continue
        action = repo["actions"].get(
            f"ACT-{flag.check_instance_id.removeprefix('CHK-')}"
        )
        assert action.due_date == END_OF_STORY + timedelta(
            days=ACTION_SLA_DAYS[flag.severity_band]
        )
    assert ACTION_SLA_DAYS["critical"] < ACTION_SLA_DAYS["low"]


def test_raising_records_both_raised_and_assigned(flagged):
    conn, report = flagged
    repo = repositories(conn)
    action_id = report.actions_raised[0]
    actions = [
        e.action for e in repo["audit"].read_for("Action", action_id)
    ]
    assert actions[:2] == ["action_raised", "action_assigned"]
    assert repo["actions"].get(action_id).status == "assigned"


def test_actions_escalate_on_their_own_timer(flagged):
    """Separate from the check's escalation, with a different owner."""
    conn, first = flagged
    assert first.actions_escalated == [], "nothing is late on the day it is raised"

    second = flag_run(conn, LATER)
    assert second.actions_escalated

    repo = repositories(conn)
    action_id = second.actions_escalated[0]
    event = [
        e for e in repo["audit"].read_for("Action", action_id)
        if e.action == "action_escalated"
    ][0]
    assert event.owner == "Group Compliance"
    assert event.detail["threshold_days"] == ACTION_ESCALATE_AFTER_DAYS
    assert event.detail["days_past_action_due_date"] >= ACTION_ESCALATE_AFTER_DAYS
    assert "independently of the check" in event.detail["reason"]


def test_an_action_does_not_escalate_before_its_own_deadline(flagged):
    """The tightest SLA plus the grace, less a day: still nothing.

    The shortest SLA governs, not the longest — a critical action due in seven
    days is already nine days late by the time a low-severity one falls due, so
    testing at the 60-day mark would prove the opposite of what it looks like.
    """
    conn, _ = flagged
    soonest = min(ACTION_SLA_DAYS.values())
    just_before = END_OF_STORY + timedelta(
        days=soonest + ACTION_ESCALATE_AFTER_DAYS - 1
    )
    assert flag_run(conn, just_before).actions_escalated == []

    on_the_day = END_OF_STORY + timedelta(days=soonest + ACTION_ESCALATE_AFTER_DAYS)
    escalated = flag_run(conn, on_the_day).actions_escalated
    assert escalated, "the critical-band actions escalate first"


def test_open_action_statuses_exclude_resolved():
    assert "resolved" not in OPEN_ACTION_STATUSES
    assert "escalated" in OPEN_ACTION_STATUSES


# --- idempotency and the trail ----------------------------------------------

def test_running_the_stage_twice_flags_nothing_new(flagged):
    conn, first = flagged
    second = flag_run(conn, END_OF_STORY)
    assert second.flags == []
    assert second.actions_raised == []
    assert len(repositories(conn)["flags"].list()) == len(first.flags)


def test_every_flag_records_its_owner(flagged):
    conn, _ = flagged
    repo = repositories(conn)
    for event in repo["audit"].read_all():
        if event.action in ("flag_raised", "action_raised", "action_assigned"):
            assert event.owner
            assert event.entity_id


def test_the_run_is_summarised_in_the_trail(flagged):
    conn, report = flagged
    event = [
        e for e in repositories(conn)["audit"].read_all()
        if e.action == "flagging_completed"
    ][-1]
    assert event.detail["flags_raised"] == len(report.flags)
    assert event.detail["category_gap"] == report.by_category["gap"]
    assert event.detail["category_overdue"] == report.by_category["overdue"]


# --- zero model calls -------------------------------------------------------

def test_flagging_costs_nothing(conn, corpus, monkeypatch):
    def _no(*args, **kwargs):
        raise AssertionError("S4 must never call a model")

    seed_database(conn, corpus)
    for month in range(1, 13):
        run_cycle(conn, date(2026, month, 28))
    run_cycle(conn, END_OF_STORY)
    screen = prescreen(conn, END_OF_STORY)

    import sentinelops.llm as llm
    import sentinelops.llm.factory as factory
    from sentinelops.llm.providers.fake import FakeModelClient

    monkeypatch.setattr(factory, "get_client", _no)
    monkeypatch.setattr(llm, "get_client", _no)
    monkeypatch.setattr(FakeModelClient, "complete", _no)

    before = conn.execute("SELECT COUNT(*) c FROM token_usage").fetchone()["c"]
    report = flag_run(conn, END_OF_STORY)
    after = conn.execute("SELECT COUNT(*) c FROM token_usage").fetchone()["c"]

    assert report.by_category["overdue"] > 0
    assert after == before == 0


def test_the_flag_module_cannot_reach_a_model():
    from pathlib import Path

    from test_applicability import _code_only

    src = Path(__file__).resolve().parents[1] / "src" / "sentinelops"
    assert "llm" not in _code_only(src / "stages" / "flag.py")


# --- a waiver that arrives after the failure was already recorded ----------

def test_a_waiver_after_the_fact_excuses_an_already_assessed_failure(conn, corpus):
    """The case the audit pack exposed.

    S2 closes an overdue check as `no_evidence` and marks it assessed, which is
    terminal. A waiver granted a cycle later used to reach nothing at all, so an
    approved deviation for an outstanding item excused precisely nothing.
    """
    seed_database(conn, corpus)
    repo = repositories(conn)
    target = "CHK-CRYPTO-KEY-HR-2026-Q1"

    for month in (1, 2, 3, 4):
        as_of = date(2026, month, 28)
        run_cycle(conn, as_of)
        prescreen(conn, as_of)
        flag_run(conn, as_of)

    # by April the check is closed as a failure and the work is raised
    assert repo["instances"].get(target).status == "assessed"
    finding = repo["findings"].list(check_instance_id=target)[0]
    assert finding.verdict == "insufficient_evidence"
    assert repo["actions"].get("ACT-CRYPTO-KEY-HR-2026-Q1").status == "assigned"

    # EXC-004 is in force from 11 May
    run_cycle(conn, date(2026, 5, 28))
    flag_run(conn, date(2026, 5, 28))

    assert repo["instances"].get(target).status == "waived"


def test_the_waiver_leaves_the_finding_standing(conn, corpus):
    """A waiver excuses an obligation; it does not rewrite what was found."""
    seed_database(conn, corpus)
    repo = repositories(conn)
    for month in (1, 2, 3, 4, 5):
        as_of = date(2026, month, 28)
        run_cycle(conn, as_of)
        prescreen(conn, as_of)
        flag_run(conn, as_of)

    findings = repo["findings"].list(check_instance_id="CHK-CRYPTO-KEY-HR-2026-Q1")
    assert len(findings) == 1, "no new finding is invented by a waiver"
    assert findings[0].verdict == "insufficient_evidence"
    assert findings[0].supersedes_finding_id is None


def test_the_waiver_closes_the_flag_and_resolves_the_action(conn, corpus):
    seed_database(conn, corpus)
    repo = repositories(conn)
    for month in (1, 2, 3, 4, 5):
        as_of = date(2026, month, 28)
        run_cycle(conn, as_of)
        prescreen(conn, as_of)
        report = flag_run(conn, as_of)

    target = "CHK-CRYPTO-KEY-HR-2026-Q1"
    flags = {f.category: f for f in repo["flags"].list(check_instance_id=target)}
    assert flags["overdue"].status == "closed"
    assert flags["exception"].status == "open"

    action = repo["actions"].get("ACT-CRYPTO-KEY-HR-2026-Q1")
    assert action.status == "resolved"
    assert "waived" in action.resolution_note
    assert "the finding it arose from stands" in action.resolution_note.lower()
    assert report.actions_resolved_by_waiver == [action.id]


def test_the_waiver_records_who_approved_it_on_the_transition(conn, corpus):
    seed_database(conn, corpus)
    repo = repositories(conn)
    for month in (1, 2, 3, 4, 5):
        as_of = date(2026, month, 28)
        run_cycle(conn, as_of)
        prescreen(conn, as_of)
        flag_run(conn, as_of)

    event = [
        e for e in repo["audit"].read_for("CheckInstance", "CHK-CRYPTO-KEY-HR-2026-Q1")
        if e.action == "check_instance_waived"
    ][0]
    assert event.detail["exception_id"] == "EXC-004"
    assert event.detail["approved_by"] == "Chief Information Security Officer"
    assert event.detail["excused_verdict"] == "insufficient_evidence"
    assert event.detail["excused_finding_id"]


def test_a_compliant_check_is_never_waived(conn, corpus):
    """There is nothing to excuse about a check that passed."""
    seed_database(conn, corpus)
    repo = repositories(conn)
    for month in range(1, 13):
        as_of = date(2026, month, 28)
        run_cycle(conn, as_of)
        prescreen(conn, as_of)
        flag_run(conn, as_of)

    findings = {f.check_instance_id: f for f in repo["findings"].list()}
    for instance in repo["instances"].list():
        if instance.status == "waived":
            finding = findings.get(instance.id)
            assert finding is None or finding.verdict != "compliant"


def test_waiving_is_idempotent_across_cycles(conn, corpus):
    seed_database(conn, corpus)
    repo = repositories(conn)
    for month in range(1, 13):
        as_of = date(2026, month, 28)
        run_cycle(conn, as_of)
        prescreen(conn, as_of)
        flag_run(conn, as_of)

    events = [
        e for e in repo["audit"].read_for("CheckInstance", "CHK-CRYPTO-KEY-HR-2026-Q1")
        if e.action == "check_instance_waived"
    ]
    assert len(events) == 1


# --- the audit trail carries simulated dates, not wall-clock ---------------

def test_events_are_stamped_with_the_cycle_date_not_today(conn, corpus):
    """Otherwise the audit log's own chronology is unusable."""
    from datetime import datetime

    seed_database(conn, corpus)
    run_cycle(conn, date(2026, 3, 28))
    prescreen(conn, date(2026, 3, 28))
    flag_run(conn, date(2026, 3, 28))

    stamps = [
        e.ts for e in repositories(conn)["audit"].read_all()
        if e.action != "exception_registered" and e.action != "corpus_seeded"
    ]
    assert stamps
    assert all(s.date() == date(2026, 3, 28) for s in stamps)
    assert all(s.year == 2026 for s in stamps)
    assert max(stamps) < datetime(2026, 3, 29)


def test_the_trail_sorts_chronologically_within_a_run(conn, corpus):
    seed_database(conn, corpus)
    for month in (1, 2, 3):
        as_of = date(2026, month, 28)
        run_cycle(conn, as_of)
        prescreen(conn, as_of)
        flag_run(conn, as_of)

    events = repositories(conn)["audit"].read_all()
    stamps = [e.ts for e in events]
    assert stamps == sorted(stamps), "sequence order and time order agree"
    assert stamps[0].date() < stamps[-1].date()


def test_the_clock_is_restored_when_a_cycle_fails(conn, corpus):
    """A leaked context variable would silently misdate every later entry."""
    import pytest as _pytest

    from sentinelops.repositories import _CLOCK

    seed_database(conn, corpus)
    with _pytest.raises(ValueError):
        run_cycle(conn, date(2026, 3, 28), trigger="not-a-trigger")
    assert _CLOCK.get() is None

    repositories(conn)["audit"].append(
        actor="system", owner="o", action="a", entity_type="E", entity_id="1"
    )
    assert repositories(conn)["audit"].read_all()[-1].ts.year >= 2026
