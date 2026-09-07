"""The loop closes: gap -> action -> remediation -> re-assessment -> resolved."""

import json
from datetime import date, datetime

import pytest

from sentinelops.entities import InboundSubmission
from sentinelops.llm.protocol import LlmResponse
from sentinelops.repositories import repositories
from sentinelops.stages.assess import run as assess
from sentinelops.stages.flag import run as flag_run
from sentinelops.stages.prescreen import run as prescreen
from sentinelops.stages.remediation import PASSING, reassess, reassess_all
from sentinelops.stages.trigger import run_cycle
from sentinelops.synth import generate_corpus, seed_database

END_OF_STORY = date(2027, 9, 30)


@pytest.fixture(scope="module")
def corpus():
    return generate_corpus()


@pytest.fixture()
def flagged(conn, corpus):
    seed_database(conn, corpus)
    for month in range(1, 13):
        run_cycle(conn, date(2026, month, 28))
    for month in range(1, 10):
        run_cycle(conn, date(2027, month, 28))
    run_cycle(conn, END_OF_STORY)
    screen = prescreen(conn, END_OF_STORY)
    assess(conn, screen.to_assess, END_OF_STORY)
    flag_run(conn, END_OF_STORY)
    return conn


@pytest.fixture()
def remediated(flagged):
    """Every remediation the corpus filed, put through the loop.

    Run twice: some remediations do not work the first time, and the corpus
    plants those on purpose. The second pass is the owner's next attempt, which
    is what makes a three-round finding reachable here rather than only in a
    hand-built fixture.
    """
    results = reassess_all(flagged, END_OF_STORY)
    results += reassess_all(flagged, END_OF_STORY)
    results += reassess_all(flagged, END_OF_STORY)
    return flagged, results


@pytest.fixture()
def closed_out(remediated):
    """Only the ones that ended in a closure — the happy path, on purpose."""
    conn, results = remediated
    return conn, [r for r in results if r.resolved]


def _first_remediable(conn, *, single_attempt: bool = True):
    """An instance with remediation evidence waiting.

    `single_attempt` picks one the corpus expects to close first time. The
    corpus deliberately contains fixes that do not work, and a test about the
    on-demand entry point should not be silently testing one of those.
    """
    repo = repositories(conn)
    attempts: dict[str, list] = {}
    for submission in sorted(repo["inbound"].list(), key=lambda s: s.id):
        if not submission.is_remediation:
            continue
        instance_id = (
            f"CHK-{submission.control_id.removeprefix('CTRL-')}-"
            f"{submission.auditable_unit_id.removeprefix('AREA-')}-{submission.period}"
        )
        if repo["instances"].get(instance_id):
            attempts.setdefault(instance_id, []).append(submission)
    for instance_id, filings in attempts.items():
        if not single_attempt or len(filings) == 1:
            return instance_id
    raise AssertionError("the corpus has no remediation evidence")


# --- the loop --------------------------------------------------------------

def test_the_corpus_carries_remediations_and_most_of_them_close(remediated):
    """Most fixes work. Not all of them do, and that is the interesting part.

    This used to assert that every remediation closed its finding, which was
    true of a corpus that only ever filed fixes that worked. Section 10 asks for
    findings needing three or more evidence rounds, so the corpus now files some
    that do not — and a test demanding a hundred per cent success would have had
    to be weakened to let them in. It asserts the shape instead: the loop closes
    the majority, and every failure leaves the finding open with the round
    counted.
    """
    conn, results = remediated
    repo = repositories(conn)
    assert len(results) >= 3

    # One row per finding: the loop is run more than once, so a finding that
    # took two attempts appears twice and the last word is the one that counts.
    last: dict[str, object] = {}
    for result in results:
        if result.finding_id:
            last[result.finding_id] = result

    closed = [r for r in last.values() if r.resolved]
    assert len(closed) >= len(last) * 0.6
    assert all(r.verdict in PASSING for r in closed)
    for result in last.values():
        if result.resolved:
            continue
        assert result.verdict not in PASSING
        assert repo["findings"].get(result.finding_id).status == "open"


def test_a_new_finding_supersedes_the_one_that_failed(closed_out):
    conn, results = closed_out
    repo = repositories(conn)
    for result in results:
        new = repo["assessments"].get(result.new_assessment_id)
        old = repo["assessments"].get(result.superseded_assessment_id)
        assert new.supersedes_assessment_id == old.id
        assert new.id != old.id
        assert old.verdict != "compliant"
        assert new.verdict == "compliant"
        # the failure is kept, not overwritten
        assert repo["assessments"].get(old.id).verdict == old.verdict


def test_the_finding_closes_with_remarks_naming_the_assessment(closed_out):
    conn, results = closed_out
    repo = repositories(conn)
    for result in results:
        finding = repo["findings"].get(result.finding_id)
        assert finding.status == "closed"
        assert finding.closed_at is not None
        assert result.new_assessment_id in finding.closure_remarks
        assert result.superseded_assessment_id in finding.closure_remarks


def test_only_an_auditor_closes_the_finding(closed_out):
    """Section 7: closure is a pa_infosec action and nobody else's."""
    conn, results = closed_out
    repo = repositories(conn)
    auditors = {
        i.id for i in repo["identities"].list() if i.role == "pa_infosec"
    }
    for result in results:
        finding = repo["findings"].get(result.finding_id)
        assert finding.closed_by in auditors
        assert finding.closed_by != finding.owner_identity


def test_the_finding_walks_the_whole_lifecycle_in_order(closed_out):
    conn, results = closed_out
    repo = repositories(conn)
    # One that closed on its first attempt, so the sequence is the plain one.
    single = next(
        r for r in results
        if len(repo["rounds"].list(finding_id=r.finding_id)) == 1
    )
    actions = [
        e.action for e in repo["audit"].read_for("Finding", single.finding_id)
    ]
    assert actions == [
        "finding_raised",
        "finding_severity_assigned",
        "finding_progress_recorded",
        "finding_closed",
    ]


def test_owner_progress_never_closes_anything(closed_out):
    """Advisory, and the trail says so in as many words."""
    conn, results = closed_out
    repo = repositories(conn)
    progress = [
        e for e in repo["audit"].read_for("Finding", results[0].finding_id)
        if e.action == "finding_progress_recorded"
    ]
    assert progress
    assert progress[0].detail["status"] == "open"
    assert progress[0].detail["progress"] == "implemented"
    assert "stays open" in progress[0].detail["note"]


def test_remediation_creates_a_new_evidence_record(closed_out):
    conn, results = closed_out
    repo = repositories(conn)
    for result in results:
        evidence = repo["evidence"].list(check_instance_id=result.check_instance_id)
        # The original filing plus every attempt at fixing it. Two for most,
        # three or four where the first fix did not work — all kept, none
        # overwritten, which is the property under test.
        assert len(evidence) >= 2, "the original filing and the fix, both kept"
        assert len([e for e in evidence if not e.is_remediation]) == 1
        original = [e for e in evidence if not e.is_remediation][0]
        fixes = sorted(
            (e for e in evidence if e.is_remediation), key=lambda e: e.submitted_at
        )
        assert fixes
        assert all(original.id != f.id for f in fixes)
        assert all(original.content != f.content for f in fixes)
        assert result.remediation_evidence_id in {f.id for f in fixes}


def test_the_flag_is_closed_when_the_finding_closes(closed_out):
    conn, results = closed_out
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
    before = len(repositories(conn)["assessments"].list())

    result = reassess(conn, instance_id, END_OF_STORY)

    assert result.new_assessment_id
    assert result.resolved is True
    assert len(repositories(conn)["assessments"].list()) == before + 1


def test_reassess_on_an_unknown_instance_says_so(flagged):
    result = reassess(flagged, "CHK-NOT-A-THING-2026-Q1", END_OF_STORY)
    assert result.new_assessment_id is None
    assert result.reason == "no such check instance"


def test_reassess_with_nothing_to_reassess_is_a_clean_no_op(flagged):
    conn = flagged
    repo = repositories(conn)
    before = len(repo["assessments"].list())
    result = reassess(conn, "CHK-CUST-COMPLAINTS-CUSTOPS-2026-07", END_OF_STORY)

    assert result.new_assessment_id is None
    assert "no unbound remediation evidence" in result.reason
    assert len(repo["assessments"].list()) == before


def test_reassess_twice_binds_the_remediation_only_once(flagged):
    conn = flagged
    instance_id = _first_remediable(conn)
    first = reassess(conn, instance_id, END_OF_STORY)
    second = reassess(conn, instance_id, END_OF_STORY)

    assert first.new_assessment_id
    assert second.new_assessment_id is None
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
    for submission in repo["inbound"].list(
        control_id=instance.control_id,
        auditable_unit_id=instance.auditable_unit_id,
        period=instance.period,
    ):
        if submission.is_remediation:
            submission.doc_type = "training_certificate"
            repo["inbound"].update(submission)

    result = reassess(conn, instance_id, END_OF_STORY)

    assert result.resolved is False
    assert result.verdict == "insufficient_evidence"
    assert "did not clear the finding" in result.reason
    finding = repo["findings"].get(result.finding_id)
    assert finding.status == "open", (
        "the finding stays open until the auditor is satisfied"
    )
    assert finding.closure_remarks == ""
    assert finding.closed_at is None
    # A round that did not land is still a round, and it is counted.
    assert finding.follow_up_count >= 1
    insufficient = [
        e for e in repo["audit"].read_for("Finding", finding.id)
        if e.action == "evidence_found_insufficient"
    ]
    assert len(insufficient) == 1
    assert insufficient[0].detail["status"] == "open"


def test_a_failed_remediation_still_supersedes_and_still_records(flagged):
    conn = flagged
    instance_id = _first_remediable(conn)
    repo = repositories(conn)
    instance = repo["instances"].get(instance_id)
    for submission in repo["inbound"].list(
        control_id=instance.control_id,
        auditable_unit_id=instance.auditable_unit_id,
        period=instance.period,
    ):
        if submission.is_remediation:
            submission.doc_type = "training_certificate"
            repo["inbound"].update(submission)

    result = reassess(conn, instance_id, END_OF_STORY)
    new = repo["assessments"].get(result.new_assessment_id)
    assert new.supersedes_assessment_id == result.superseded_assessment_id
    flags = repo["flags"].list(check_instance_id=instance_id)
    assert all(f.status == "open" for f in flags), "the problem is still open"


def test_a_failed_remediation_gets_a_fresh_flag_on_the_next_pass(flagged):
    """The new finding is current; the superseded one is history."""
    conn = flagged
    instance_id = _first_remediable(conn)
    repo = repositories(conn)
    instance = repo["instances"].get(instance_id)
    for submission in repo["inbound"].list(
        control_id=instance.control_id,
        auditable_unit_id=instance.auditable_unit_id,
        period=instance.period,
    ):
        if submission.is_remediation:
            submission.doc_type = "training_certificate"
            repo["inbound"].update(submission)

    result = reassess(conn, instance_id, END_OF_STORY)
    report = flag_run(conn, date(2027, 4, 30))

    new_flags = [
        f for f in repo["flags"].list(check_instance_id=instance_id)
        if f.assessment_id == result.new_assessment_id
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
    # Some structured fixes fail on the first attempt by design; what the rule
    # tier must guarantee is that it decided them without a model either way.
    assert any(r.resolved for r in structured)
    for result in structured:
        assert result.decided_by == "structured_threshold"
        assert (result.verdict == "compliant") == result.resolved


def test_a_document_remediation_goes_through_the_model(flagged):
    conn = flagged
    results = reassess_all(conn, END_OF_STORY)
    by_model = [r for r in results if r.decided_by == "s3_model"]
    assert by_model
    repo = repositories(conn)
    for result in by_model:
        finding = repo["assessments"].get(result.new_assessment_id)
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

def test_the_whole_lifecycle_is_reconstructable(closed_out):
    conn, results = closed_out
    repo = repositories(conn)
    result = results[0]

    instance_events = [
        e.action for e in repo["audit"].read_for("CheckInstance", result.check_instance_id)
    ]
    assert "check_instance_created" in instance_events
    assert "remediation_submitted" in instance_events

    finding_events = repo["audit"].read_for("Finding", result.finding_id)
    assert finding_events[-1].action == "finding_closed"
    assert all(e.owner for e in finding_events)

    superseded = repo["audit"].read_for("Assessment", result.superseded_assessment_id)
    assert any(e.action == "assessment_superseded" for e in superseded)


def test_every_transition_records_who(closed_out):
    conn, results = closed_out
    repo = repositories(conn)
    for result in results:
        for event in repo["audit"].read_for("Finding", result.finding_id):
            assert event.owner
            assert event.actor_kind in ("system", "ai", "user")
            assert event.actor_identity, "every transition names an identity"


def test_the_person_who_filed_the_fix_is_named(closed_out):
    conn, results = closed_out
    repo = repositories(conn)
    for result in results:
        submitted = [
            e for e in repo["audit"].read_for("CheckInstance", result.check_instance_id)
            if e.action == "remediation_submitted"
        ]
        # One per attempt: a finding that took three rounds filed three times,
        # and every one of them names who filed it.
        assert submitted
        for event in submitted:
            assert event.actor_kind == "user"
            assert event.owner
            assert event.detail["supersedes_assessment_id"]
        assert result.superseded_assessment_id in {
            e.detail["supersedes_assessment_id"] for e in submitted
        }


def test_findings_open_versus_closed_is_answerable(remediated):
    """The metric section 8 asks for, straight out of the data.

    Not `closed == len(results)` any more: the corpus seeds an audit programme
    whose findings were closed by an auditor long before this loop ran, and
    those are just as real. The property is that both counts are answerable and
    that the loop accounts for the activity-track half of the closed set.
    """
    conn, results = remediated
    findings = repositories(conn)["findings"].list()
    closed = [f for f in findings if f.status == "closed"]
    assert findings
    assert 0 < len(closed) / len(findings) < 1

    from_loop = {r.finding_id for r in results if r.resolved}
    activity_closed = {
        f.id for f in closed if f.source == "activity_assessment"
    }
    assert from_loop == activity_closed
