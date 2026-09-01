"""The loop closes: gap -> action -> remediation -> re-assessment -> resolved."""

import json
from datetime import date, datetime

import pytest

from sentinelops.entities import EvidenceSubmission
from sentinelops.llm.protocol import LlmResponse
from sentinelops.repositories import repositories
from sentinelops.stages.assess import run as assess
from sentinelops.stages.flag import run as flag_run
from sentinelops.stages.prescreen import run as prescreen
from sentinelops.stages.remediation import PASSING, reassess, reassess_all
from sentinelops.stages.trigger import run_cycle
from sentinelops.synth import generate_corpus, seed_database

END_OF_STORY = date(2027, 3, 31)


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
    flag_run(conn, END_OF_STORY)
    return conn


@pytest.fixture()
def remediated(flagged):
    return flagged, reassess_all(flagged, END_OF_STORY)


def _first_remediable(conn):
    repo = repositories(conn)
    for submission in sorted(repo["submissions"].list(), key=lambda s: s.id):
        if not submission.is_remediation:
            continue
        instance_id = (
            f"CHK-{submission.control_id.removeprefix('CTRL-')}-"
            f"{submission.process_area_id.removeprefix('AREA-')}-{submission.period}"
        )
        if repo["instances"].get(instance_id):
            return instance_id
    raise AssertionError("the corpus has no remediation evidence")


# --- the loop --------------------------------------------------------------

def test_the_corpus_carries_remediations_and_all_of_them_close(remediated):
    conn, results = remediated
    assert len(results) >= 3
    assert all(r.resolved for r in results)
    assert all(r.verdict in PASSING for r in results)


def test_a_new_finding_supersedes_the_one_that_failed(remediated):
    conn, results = remediated
    repo = repositories(conn)
    for result in results:
        new = repo["findings"].get(result.new_finding_id)
        old = repo["findings"].get(result.superseded_finding_id)
        assert new.supersedes_finding_id == old.id
        assert new.id != old.id
        assert old.verdict != "compliant"
        assert new.verdict == "compliant"
        # the failure is kept, not overwritten
        assert repo["findings"].get(old.id).verdict == old.verdict


def test_the_action_resolves_with_a_note_naming_the_finding(remediated):
    conn, results = remediated
    repo = repositories(conn)
    for result in results:
        action = repo["actions"].get(result.action_id)
        assert action.status == "resolved"
        assert action.resolved_at is not None
        assert result.new_finding_id in action.resolution_note
        assert result.superseded_finding_id in action.resolution_note


def test_the_action_walks_the_whole_lifecycle_in_order(remediated):
    conn, results = remediated
    repo = repositories(conn)
    actions = [
        e.action for e in repo["audit"].read_for("Action", results[0].action_id)
    ]
    assert actions == [
        "action_raised",
        "action_assigned",
        "action_in_progress",
        "action_remediation_submitted",
        "action_reassessed",
        "action_resolved",
    ]


def test_remediation_creates_a_new_evidence_record(remediated):
    conn, results = remediated
    repo = repositories(conn)
    for result in results:
        evidence = repo["evidence"].list(check_instance_id=result.check_instance_id)
        assert len(evidence) == 2, "the original filing and the fix, both kept"
        original = [e for e in evidence if not e.is_remediation][0]
        fix = [e for e in evidence if e.is_remediation][0]
        assert original.id != fix.id
        assert original.content != fix.content
        assert fix.id == result.remediation_evidence_id


def test_the_flag_is_closed_when_the_action_resolves(remediated):
    conn, results = remediated
    repo = repositories(conn)
    for result in results:
        flags = repo["flags"].list(check_instance_id=result.check_instance_id)
        assert flags
        assert all(f.status == "closed" for f in flags)


# --- the on-demand entry point ---------------------------------------------

def test_reassess_does_not_wait_for_the_next_cycle(flagged):
    """One instance, re-checked on demand, with no scheduling run in between."""
    conn = flagged
    instance_id = _first_remediable(conn)
    before = len(repositories(conn)["findings"].list())

    result = reassess(conn, instance_id, END_OF_STORY)

    assert result.new_finding_id
    assert result.resolved is True
    assert len(repositories(conn)["findings"].list()) == before + 1


def test_reassess_on_an_unknown_instance_says_so(flagged):
    result = reassess(flagged, "CHK-NOT-A-THING-2026-Q1", END_OF_STORY)
    assert result.new_finding_id is None
    assert result.reason == "no such check instance"


def test_reassess_with_nothing_to_reassess_is_a_clean_no_op(flagged):
    conn = flagged
    repo = repositories(conn)
    before = len(repo["findings"].list())
    result = reassess(conn, "CHK-CUST-COMPLAINTS-CUSTOPS-2026-07", END_OF_STORY)

    assert result.new_finding_id is None
    assert "no unbound remediation evidence" in result.reason
    assert len(repo["findings"].list()) == before


def test_reassess_twice_binds_the_remediation_only_once(flagged):
    conn = flagged
    instance_id = _first_remediable(conn)
    first = reassess(conn, instance_id, END_OF_STORY)
    second = reassess(conn, instance_id, END_OF_STORY)

    assert first.new_finding_id
    assert second.new_finding_id is None
    assert "no unbound remediation evidence" in second.reason
    assert len(
        repositories(conn)["evidence"].list(check_instance_id=instance_id)
    ) == 2


# --- a remediation that does not work --------------------------------------

def test_a_failed_remediation_leaves_the_action_open(flagged):
    """A fix that does not fix it is not a resolution."""
    conn = flagged
    instance_id = _first_remediable(conn)
    repo = repositories(conn)
    instance = repo["instances"].get(instance_id)

    # replace the pending remediation with one of the wrong document type
    for submission in repo["submissions"].list(
        control_id=instance.control_id,
        process_area_id=instance.process_area_id,
        period=instance.period,
    ):
        if submission.is_remediation:
            submission.doc_type = "training_certificate"
            repo["submissions"].update(submission)

    result = reassess(conn, instance_id, END_OF_STORY)

    assert result.resolved is False
    assert result.verdict == "insufficient_evidence"
    assert "did not clear the finding" in result.reason
    action = repo["actions"].get(result.action_id)
    assert action.status == "reassessed"
    assert action.resolution_note is None
    assert action.resolved_at is None


def test_a_failed_remediation_still_supersedes_and_still_records(flagged):
    conn = flagged
    instance_id = _first_remediable(conn)
    repo = repositories(conn)
    instance = repo["instances"].get(instance_id)
    for submission in repo["submissions"].list(
        control_id=instance.control_id,
        process_area_id=instance.process_area_id,
        period=instance.period,
    ):
        if submission.is_remediation:
            submission.doc_type = "training_certificate"
            repo["submissions"].update(submission)

    result = reassess(conn, instance_id, END_OF_STORY)
    new = repo["findings"].get(result.new_finding_id)
    assert new.supersedes_finding_id == result.superseded_finding_id
    flags = repo["flags"].list(check_instance_id=instance_id)
    assert all(f.status == "open" for f in flags), "the problem is still open"


def test_a_failed_remediation_gets_a_fresh_flag_on_the_next_pass(flagged):
    """The new finding is current; the superseded one is history."""
    conn = flagged
    instance_id = _first_remediable(conn)
    repo = repositories(conn)
    instance = repo["instances"].get(instance_id)
    for submission in repo["submissions"].list(
        control_id=instance.control_id,
        process_area_id=instance.process_area_id,
        period=instance.period,
    ):
        if submission.is_remediation:
            submission.doc_type = "training_certificate"
            repo["submissions"].update(submission)

    result = reassess(conn, instance_id, END_OF_STORY)
    report = flag_run(conn, date(2027, 4, 30))

    new_flags = [
        f for f in repo["flags"].list(check_instance_id=instance_id)
        if f.finding_id == result.new_finding_id
    ]
    assert new_flags, "the current failure must be flagged"
    assert new_flags[0].id in report.flags


# --- re-assessment goes through the same tiers -----------------------------

def test_remediation_is_pre_screened_before_it_is_assessed(flagged):
    """A structured remediation is decided by arithmetic, not by a model."""
    conn = flagged
    repo = repositories(conn)
    structured = [
        r for r in reassess_all(conn, END_OF_STORY)
        if r.decided_by == "structured_threshold"
    ]
    assert structured, "the corpus remediates structured controls too"
    for result in structured:
        assert result.verdict == "compliant"
        assert result.resolved


def test_a_document_remediation_goes_through_the_model(flagged):
    conn = flagged
    results = reassess_all(conn, END_OF_STORY)
    by_model = [r for r in results if r.decided_by == "s3_model"]
    assert by_model
    repo = repositories(conn)
    for result in by_model:
        finding = repo["findings"].get(result.new_finding_id)
        assert finding.cited_spans, "still cited, even on the second pass"
        assert finding.prompt_version


def test_re_assessment_is_metered_like_any_other_call(flagged):
    conn = flagged
    before = conn.execute("SELECT COUNT(*) c FROM token_usage").fetchone()["c"]
    results = reassess_all(conn, END_OF_STORY)
    after = conn.execute("SELECT COUNT(*) c FROM token_usage").fetchone()["c"]
    model_decided = sum(1 for r in results if r.decided_by == "s3_model")
    assert after - before == model_decided


# --- the audit trail --------------------------------------------------------

def test_the_whole_lifecycle_is_reconstructable(remediated):
    conn, results = remediated
    repo = repositories(conn)
    result = results[0]

    instance_events = [
        e.action for e in repo["audit"].read_for("CheckInstance", result.check_instance_id)
    ]
    assert "check_instance_created" in instance_events
    assert "remediation_submitted" in instance_events

    action_events = repo["audit"].read_for("Action", result.action_id)
    assert action_events[-1].action == "action_resolved"
    assert all(e.owner for e in action_events)

    superseded = repo["audit"].read_for("Finding", result.superseded_finding_id)
    assert any(e.action == "finding_superseded" for e in superseded)


def test_every_transition_records_who(remediated):
    conn, results = remediated
    repo = repositories(conn)
    for result in results:
        for event in repo["audit"].read_for("Action", result.action_id):
            assert event.owner
            assert event.actor in ("system", "ai", "user")
            assert "from_status" in event.detail or event.action == "action_raised"


def test_the_person_who_filed_the_fix_is_named(remediated):
    conn, results = remediated
    repo = repositories(conn)
    for result in results:
        submitted = [
            e for e in repo["audit"].read_for("CheckInstance", result.check_instance_id)
            if e.action == "remediation_submitted"
        ]
        assert len(submitted) == 1
        assert submitted[0].actor == "user"
        assert submitted[0].owner
        assert submitted[0].detail["supersedes_finding_id"] == result.superseded_finding_id


def test_actions_raised_versus_resolved_is_answerable(remediated):
    """The metric section 6 asks for, straight out of the data."""
    conn, results = remediated
    actions = repositories(conn)["actions"].list()
    raised = len(actions)
    resolved = len([a for a in actions if a.status == "resolved"])
    assert raised > 0
    assert resolved == len(results)
    assert 0 < resolved / raised < 1
