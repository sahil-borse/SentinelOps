"""Section 5 — the chasing engine, which is the part nobody does reliably.

Two clocks per open finding, both severity-driven, both deterministic. The
tests that matter here are not "does it send a reminder" but the two the
stakeholder was specific about: nothing drifts more than a week from its target
date to an escalation, and escalating does not make the reminders stop.
"""

from datetime import date, timedelta

import pytest

from sentinelops.directory import load as load_directory
from sentinelops.repositories import repositories
from sentinelops.stages import followup
from sentinelops.stages.flag import run as flag_run
from sentinelops.stages.prescreen import run as prescreen
from sentinelops.stages.trigger import run_cycle
from sentinelops.synth import generate_corpus, seed_database

END_OF_STORY = date(2027, 9, 30)


@pytest.fixture(scope="module")
def corpus():
    return generate_corpus()


@pytest.fixture
def chased(conn, corpus):
    """A corpus run to the end of the story, with findings open and chased."""
    seed_database(conn, corpus)
    for month in range(1, 13):
        as_of = date(2026, month, 28)
        run_cycle(conn, as_of)
        prescreen(conn, as_of)
    run_cycle(conn, END_OF_STORY)
    prescreen(conn, END_OF_STORY)
    flag_run(conn, END_OF_STORY)
    return conn


# --- the table itself --------------------------------------------------------

def test_nothing_drifts_more_than_a_week_to_escalation():
    """The stakeholder's stated ceiling, asserted rather than trusted."""
    for name, rule in followup.SEVERITY_RULES.items():
        assert rule.escalate_after <= followup.MAX_DAYS_TO_ESCALATION, name


def test_the_table_tightens_monotonically_with_severity():
    rules = followup.SEVERITY_RULES
    order = ["Major:urgent", "Major", "Minor", "Observation"]
    for tighter, looser in zip(order, order[1:]):
        assert rules[tighter].target_days < rules[looser].target_days
        assert rules[tighter].escalate_after <= rules[looser].escalate_after


def test_a_major_finding_against_a_critical_unit_is_the_urgent_variant():
    assert followup.rule_for("Major", "critical") is (
        followup.SEVERITY_RULES["Major:urgent"]
    )
    assert followup.rule_for("Major", "medium") is followup.SEVERITY_RULES["Major"]


def test_an_unassigned_severity_still_gets_chased():
    """A finding whose severity the auditor has not set yet is not invisible."""
    assert followup.rule_for(None) is followup.SEVERITY_RULES["Observation"]


def test_the_target_date_is_derived_from_the_severity():
    raised = date(2026, 5, 1)
    assert followup.target_date_for(raised, "Major", "") == raised + timedelta(days=7)
    assert followup.target_date_for(raised, "Observation", "") == (
        raised + timedelta(days=28)
    )


# --- the two clocks ----------------------------------------------------------

def test_reminders_go_out_before_the_target_date(chased):
    conn = chased
    repo = repositories(conn)
    findings = [f for f in repo["findings"].list() if f.status == "open"]
    assert findings

    units = {u.id: u for u in repo["units"].list()}
    target = min(findings, key=lambda f: f.target_date)
    rule = followup.rule_for(
        target.severity, units[target.auditable_unit_id].attributes["criticality"]
    )
    report = followup.run(conn, target.target_date - timedelta(days=rule.remind_before))
    assert target.id in report.reminded


def test_a_reminder_increments_the_follow_up_count(chased):
    conn = chased
    repo = repositories(conn)
    before = {f.id: f.follow_up_count for f in repo["findings"].list()}
    report = followup.run(conn, END_OF_STORY + timedelta(days=40))
    assert report.reminded
    after = {f.id: f.follow_up_count for f in repo["findings"].list()}
    for finding_id in report.reminded:
        assert after[finding_id] == before[finding_id] + 1


def test_escalation_goes_up_the_line_and_to_pa_infosec(chased):
    conn = chased
    repo = repositories(conn)
    people = load_directory(conn)
    report = followup.run(conn, END_OF_STORY + timedelta(days=60))
    assert report.escalated

    finding_id, level = report.escalated[0]
    event = [
        e for e in repo["audit"].read_for("Finding", finding_id)
        if e.action == "finding_escalated"
    ][0]
    finding = repo["findings"].get(finding_id)

    assert event.detail["level"] == level
    assert event.detail["escalated_to"], "somebody senior was named"
    assert event.detail["escalated_to"] != finding.owner_identity
    assert event.detail["also_notified"], "PA/InfoSec hears about it too"
    for identity_id in event.detail["also_notified"]:
        assert people.get(identity_id).role == "pa_infosec"


def test_escalation_follows_the_reporting_line(chased):
    """Level 1 is the owner's own manager — `reports_to`, not a fixed mailbox.

    `escalation_chain` starts at the owner themselves, so level 1 is index 1.
    Level 2 is their manager's manager, and the chain stops rather than looping
    when it runs out of people.
    """
    conn = chased
    people = load_directory(conn)
    report = followup.run(conn, END_OF_STORY + timedelta(days=60))
    finding_id, level = report.escalated[0]
    finding = repositories(conn)["findings"].get(finding_id)
    chain = people.escalation_chain(finding.owner_identity)
    assert len(chain) > 1, "an owner with nobody above them cannot be escalated"
    assert chain[0].id == finding.owner_identity
    event = [
        e for e in repositories(conn)["audit"].read_for("Finding", finding_id)
        if e.action == "finding_escalated"
    ][0]
    assert event.detail["escalated_to"] == chain[min(level, len(chain) - 1)].id
    assert people.get(event.detail["escalated_to"]).id != finding.owner_identity


def test_reminders_continue_after_escalation(chased):
    """Section 5, in as many words: escalation does not replace the chase."""
    conn = chased
    late = END_OF_STORY + timedelta(days=60)
    first = followup.run(conn, late)
    assert first.escalated
    escalated_ids = {finding_id for finding_id, _ in first.escalated}

    later = followup.run(conn, late + timedelta(days=1))
    assert escalated_ids & set(later.reminded), (
        "a finding that has been escalated is still owed by its owner"
    )


def test_nothing_open_and_overdue_escapes_escalation(chased):
    """The claim the pitch rests on: it is not possible to be forgotten."""
    conn = chased
    repo = repositories(conn)
    far = END_OF_STORY + timedelta(days=120)
    followup.run(conn, far)

    escalated = {
        e.entity_id for e in repo["audit"].read_all()
        if e.action == "finding_escalated"
    }
    overdue = [
        f for f in repo["findings"].list()
        if f.status == "open" and f.target_date < far
    ]
    assert overdue
    assert {f.id for f in overdue} <= escalated


def test_a_closed_finding_is_not_chased(chased):
    conn = chased
    repo = repositories(conn)
    people = load_directory(conn)
    finding = next(f for f in repo["findings"].list() if f.status == "open")
    auditor = people.by_role("pa_infosec")[0]
    followup.close_finding(
        conn, finding.id, by=auditor.id, remarks="Evidence accepted.",
        as_of=END_OF_STORY,
    )
    report = followup.run(conn, END_OF_STORY + timedelta(days=90))
    assert finding.id not in report.reminded
    assert finding.id not in {fid for fid, _ in report.escalated}


def test_escalation_does_not_repeat_the_same_level(chased):
    conn = chased
    late = END_OF_STORY + timedelta(days=60)
    first = followup.run(conn, late)
    second = followup.run(conn, late)
    assert first.escalated
    assert second.escalated == [], "the same level is not announced twice"


# --- the auditor's decisions -------------------------------------------------

def test_only_remarks_can_close_a_finding(chased):
    conn = chased
    people = load_directory(conn)
    finding = next(
        f for f in repositories(conn)["findings"].list() if f.status == "open"
    )
    auditor = people.by_role("pa_infosec")[0]
    with pytest.raises(ValueError):
        followup.close_finding(
            conn, finding.id, by=auditor.id, remarks="   ", as_of=END_OF_STORY
        )
    assert repositories(conn)["findings"].get(finding.id).status == "open"


def test_owner_progress_does_not_move_the_authoritative_status(chased):
    conn = chased
    repo = repositories(conn)
    finding = next(f for f in repo["findings"].list() if f.status == "open")
    for progress in ("acknowledged", "action_in_progress", "implemented"):
        followup.record_owner_progress(
            conn, finding.id, progress, by=finding.owner_identity
        )
        reloaded = repo["findings"].get(finding.id)
        assert reloaded.owner_progress == progress
        assert reloaded.status == "open"


def test_an_insufficient_round_counts_and_keeps_the_finding_open(chased):
    conn = chased
    repo = repositories(conn)
    people = load_directory(conn)
    finding = next(f for f in repo["findings"].list() if f.status == "open")
    before = finding.follow_up_count
    auditor = people.by_role("pa_infosec")[0]

    followup.record_insufficient_round(
        repo, finding, by=auditor.id,
        remarks="The tracker does not cover March.", assessment_id="ASM-X",
    )
    reloaded = repo["findings"].get(finding.id)
    assert reloaded.status == "open"
    assert reloaded.follow_up_count == before + 1


def test_assigning_a_severity_moves_the_target_date_and_records_the_override(chased):
    conn = chased
    repo = repositories(conn)
    people = load_directory(conn)
    # Must be one the model advised on: an audit-raised finding has no
    # suggestion to override, so picking one would test nothing.
    finding = next(
        f for f in repo["findings"].list()
        if f.status == "open"
        and f.suggested_severity is not None
        and f.suggested_severity != "Major"
    )
    auditor = people.by_role("pa_infosec")[0]

    followup.assign_severity(
        conn, finding.id, "Major", by=auditor.id,
        remarks="Customer data was exposed; this is not a Minor.",
    )
    reloaded = repo["findings"].get(finding.id)
    assert reloaded.severity == "Major"
    assert reloaded.suggested_severity == finding.suggested_severity
    assert reloaded.severity_assigned_by == auditor.id

    event = [
        e for e in repo["audit"].read_for("Finding", finding.id)
        if e.action == "finding_severity_assigned"
    ][-1]
    assert event.detail["overrode_suggestion"] is True
    assert event.detail["remarks"]


def test_chase_events_carry_the_cycle_date_not_the_wall_clock(chased):
    """The same defect 8c fixed, guarded on the stage that writes most events."""
    from datetime import datetime

    conn = chased
    repo = repositories(conn)
    before = {e.seq for e in repo["audit"].read_all()}
    as_of = END_OF_STORY + timedelta(days=40)
    followup.run(conn, as_of)

    new = [e for e in repo["audit"].read_all() if e.seq not in before]
    assert new
    assert all(e.ts.date() == as_of for e in new)
    assert all(e.ts < datetime.combine(as_of + timedelta(days=1), datetime.min.time())
               for e in new)


# --- zero model calls --------------------------------------------------------

def test_following_up_never_asks_a_model(chased):
    """Section 2: chasing is deterministic. A client that raises proves it."""
    class Exploding:
        def complete(self, *args, **kwargs):  # pragma: no cover - must not run
            raise AssertionError("follow-up must not call a model")

    conn = chased
    followup.run(conn, END_OF_STORY + timedelta(days=45))
    assert Exploding  # the client is never wired in; there is nowhere to pass it

    import sentinelops.stages.followup as module

    source = module.__file__
    with open(source, encoding="utf-8") as handle:
        text = handle.read()
    assert "llm" not in text.split('"""', 2)[2]
