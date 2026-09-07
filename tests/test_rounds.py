"""Section 4's review loop — rounds, and the two answers an auditor may give."""

from datetime import date, datetime, timedelta

import pytest

from sentinelops.synth.calendar import SIMULATED_TODAY
from sentinelops.directory import load as load_directory
from sentinelops.entities import Finding
from sentinelops.repositories import repositories, simulated_clock
from sentinelops.stages import followup, rounds
from sentinelops.synth import generate_corpus, seed_database

AS_OF = date(2026, 6, 30)


@pytest.fixture(scope="module")
def corpus():
    return generate_corpus()


@pytest.fixture
def ctx(conn, corpus):
    seed_database(conn, corpus)
    repo = repositories(conn)
    people = load_directory(conn)
    unit = repo["units"].list()[0]
    auditor = people.by_role("pa_infosec")[0]
    finding = Finding(
        id="FND-ROUNDS-1",
        source="audit",
        auditable_unit_id=unit.id,
        description="The quarterly access review was not evidenced.",
        raised_by=auditor.id,
        raised_at=datetime(2026, 6, 1, 9, 0),
        owner_identity=unit.owner_identity,
        target_date=date(2026, 6, 15),
        severity="Minor",
        severity_assigned_by=auditor.id,
    )
    with simulated_clock(datetime(2026, 6, 1, 9, 0)):
        repo["findings"].add(finding)
    return conn, repo, people, finding, auditor


# --- opening a round ---------------------------------------------------------

def test_filing_evidence_opens_a_numbered_round(ctx):
    _, repo, people, finding, _ = ctx
    first = rounds.open_round(
        repo, people, finding, by=finding.owner_identity,
        evidence_ref="EV-1", note="Tracker attached.", as_of=AS_OF,
    )
    assert first.round_number == 1
    assert first.finding_id == finding.id
    assert first.auditor_response == "pending"
    assert first.is_open
    assert first.owner_note == "Tracker attached."


def test_filing_evidence_does_not_move_the_finding(ctx):
    """The whole point of section 4: the owner cannot close anything."""
    _, repo, people, finding, _ = ctx
    rounds.open_round(
        repo, people, finding, by=finding.owner_identity,
        evidence_ref="EV-1", as_of=AS_OF,
    )
    assert repo["findings"].get(finding.id).status == "open"


def test_a_second_round_cannot_open_while_one_is_unanswered(ctx):
    """Otherwise "round 3" means nothing — three open rounds is not three
    rounds, it is one conversation nobody replied to."""
    _, repo, people, finding, _ = ctx
    rounds.open_round(
        repo, people, finding, by=finding.owner_identity,
        evidence_ref="EV-1", as_of=AS_OF,
    )
    with pytest.raises(ValueError) as refused:
        rounds.open_round(
            repo, people, finding, by=finding.owner_identity,
            evidence_ref="EV-2", as_of=AS_OF + timedelta(days=1),
        )
    assert "unanswered round" in str(refused.value)


# --- answering it ------------------------------------------------------------

def test_insufficient_keeps_the_finding_open_and_counts_the_round(ctx):
    conn, repo, people, finding, auditor = ctx
    first = rounds.open_round(
        repo, people, finding, by=finding.owner_identity,
        evidence_ref="EV-1", as_of=AS_OF,
    )
    rounds.respond(
        repo, people, first, response="insufficient", by=auditor.id,
        remarks="The tracker does not cover March.", as_of=AS_OF,
    )
    followup.record_insufficient_round(
        repo, finding, by=auditor.id, remarks="The tracker does not cover March."
    )

    answered = repo["rounds"].get(first.id)
    assert answered.auditor_response == "insufficient"
    assert answered.responded_by == auditor.id
    assert answered.responded_at is not None
    assert repo["findings"].get(finding.id).status == "open"
    assert repo["findings"].get(finding.id).follow_up_count == 1


def test_revised_evidence_opens_round_two_rather_than_editing_round_one(ctx):
    _, repo, people, finding, auditor = ctx
    first = rounds.open_round(
        repo, people, finding, by=finding.owner_identity,
        evidence_ref="EV-1", as_of=AS_OF,
    )
    rounds.respond(
        repo, people, first, response="insufficient", by=auditor.id,
        remarks="March is missing.", as_of=AS_OF,
    )
    second = rounds.open_round(
        repo, people, finding, by=finding.owner_identity,
        evidence_ref="EV-2", as_of=AS_OF + timedelta(days=4),
    )
    assert second.round_number == 2
    # round one is untouched: the failed attempt is still on the record
    assert repo["rounds"].get(first.id).auditor_response == "insufficient"
    assert repo["rounds"].get(first.id).evidence_ref == "EV-1"
    assert rounds.round_count(repo, finding.id) == 2
    assert rounds.insufficient_rounds(repo, finding.id) == 1


def test_an_answered_round_cannot_be_answered_again(ctx):
    _, repo, people, finding, auditor = ctx
    first = rounds.open_round(
        repo, people, finding, by=finding.owner_identity,
        evidence_ref="EV-1", as_of=AS_OF,
    )
    rounds.respond(
        repo, people, first, response="insufficient", by=auditor.id,
        remarks="March is missing.", as_of=AS_OF,
    )
    with pytest.raises(ValueError) as refused:
        rounds.respond(
            repo, people, first, response="accepted", by=auditor.id,
            remarks="Actually fine.", as_of=AS_OF,
        )
    assert "already answered" in str(refused.value)


def test_there_are_exactly_two_answers(ctx):
    _, repo, people, finding, auditor = ctx
    first = rounds.open_round(
        repo, people, finding, by=finding.owner_identity,
        evidence_ref="EV-1", as_of=AS_OF,
    )
    for bogus in ("pending", "maybe", "partially", ""):
        with pytest.raises(ValueError):
            rounds.respond(
                repo, people, first, response=bogus, by=auditor.id,
                remarks="…", as_of=AS_OF,
            )


def test_a_response_without_remarks_is_refused(ctx):
    """"Communicate the gaps" is the requirement; silence does not."""
    _, repo, people, finding, auditor = ctx
    first = rounds.open_round(
        repo, people, finding, by=finding.owner_identity,
        evidence_ref="EV-1", as_of=AS_OF,
    )
    with pytest.raises(ValueError) as refused:
        rounds.respond(
            repo, people, first, response="insufficient", by=auditor.id,
            remarks="   ", as_of=AS_OF,
        )
    assert "gaps" in str(refused.value)


# --- the trail ---------------------------------------------------------------

def test_every_round_transition_is_on_the_trail_with_an_identity(ctx):
    _, repo, people, finding, auditor = ctx
    first = rounds.open_round(
        repo, people, finding, by=finding.owner_identity,
        evidence_ref="EV-1", as_of=AS_OF,
    )
    rounds.respond(
        repo, people, first, response="accepted", by=auditor.id,
        remarks="Complete.", as_of=AS_OF,
    )
    events = repo["audit"].read_for("EvidenceSubmission", first.id)
    assert [e.action for e in events] == [
        "evidence_round_opened", "evidence_round_accepted"
    ]
    assert events[0].actor_identity == finding.owner_identity
    assert events[1].actor_identity == auditor.id
    assert all(e.owner for e in events)
    assert events[0].detail["finding_status"] == "open"


def test_the_number_of_rounds_is_answerable_from_the_data(ctx):
    """Section 8 asks for the distribution of multi-round findings."""
    _, repo, people, finding, auditor = ctx
    for n in range(3):
        record = rounds.open_round(
            repo, people, finding, by=finding.owner_identity,
            evidence_ref=f"EV-{n}", as_of=AS_OF + timedelta(days=n * 5),
        )
        rounds.respond(
            repo, people, record,
            response="accepted" if n == 2 else "insufficient",
            by=auditor.id, remarks=f"Round {n + 1}.",
            as_of=AS_OF + timedelta(days=n * 5),
        )
    assert rounds.round_count(repo, finding.id) == 3
    assert rounds.insufficient_rounds(repo, finding.id) == 2
    assert [r.round_number for r in rounds.rounds_for(repo, finding.id)] == [1, 2, 3]


# --- the corpus exercises the loop, not just the tests -----------------------

def test_the_remediation_loop_writes_real_rounds(conn, corpus):
    """A round that only exists in a unit test proves nothing about the run.

    Runs the whole pipeline, S3 included — an earlier version of this test
    skipped assessment, which meant most instances never reached a verdict and
    it was asserting against three rounds instead of the corpus's real ones.
    """
    from sentinelops.stages.assess import run as assess
    from sentinelops.stages.flag import run as flag_stage
    from sentinelops.stages.prescreen import run as prescreen
    from sentinelops.stages.remediation import reassess_all
    from sentinelops.stages.trigger import run_cycle

    seed_database(conn, corpus)
    cycles = [date(2026, m, 28) for m in range(1, 13)] + [SIMULATED_TODAY]
    results = []
    for as_of in cycles:
        run_cycle(conn, as_of)
        screen = prescreen(conn, as_of)
        if screen.to_assess:
            assess(conn, screen.to_assess, as_of)
        flag_stage(conn, as_of)
        results += reassess_all(conn, as_of)

    repo = repositories(conn)
    all_rounds = repo["rounds"].list()
    assert all_rounds, "the corpus must exercise the loop it is meant to show"

    # one round per remediation the corpus actually filed
    assert len(all_rounds) == len([r for r in results if r.finding_id])
    assert all(r.auditor_response in ("accepted", "insufficient")
               for r in all_rounds), "no round is left hanging"

    # and every accepted round belongs to a finding that is now closed, by
    # somebody other than whoever filed it
    for record in all_rounds:
        if record.auditor_response != "accepted":
            continue
        finding = repo["findings"].get(record.finding_id)
        assert finding.status == "closed"
        assert finding.closed_by == record.responded_by
        assert finding.closed_by != record.submitted_by


def test_the_corpus_exercises_multi_round_findings(conn, corpus):
    """Section 10 asks for several findings needing three or more rounds.

    This test used to assert the opposite — that every corpus round was a
    first-round acceptance — and said in its docstring that fixing it was the
    corpus slice's business. It is now that slice's test: the reshape plants
    remediations that fail the first time, so the loop the stakeholder described
    actually goes round, and `follow_up_count` measures something.
    """
    from collections import Counter

    from sentinelops.stages.assess import run as assess
    from sentinelops.stages.flag import run as flag_stage
    from sentinelops.stages.prescreen import run as prescreen
    from sentinelops.stages.remediation import reassess_all
    from sentinelops.stages.trigger import run_cycle

    seed_database(conn, corpus)
    cycles = [date(2026, m, 28) for m in range(1, 13)]
    cycles += [date(2027, m, 28) for m in range(1, 10)]
    for as_of in cycles:
        run_cycle(conn, as_of)
        screen = prescreen(conn, as_of)
        if screen.to_assess:
            assess(conn, screen.to_assess, as_of)
        flag_stage(conn, as_of)
        reassess_all(conn, as_of)

    repo = repositories(conn)
    all_rounds = repo["rounds"].list()
    assert all_rounds

    per_finding = Counter(r.finding_id for r in all_rounds)
    assert max(per_finding.values()) >= 3, (
        "section 10 asks for several findings needing 3+ evidence rounds"
    )
    assert sum(1 for n in per_finding.values() if n >= 3) >= 3, "several, not one"
    assert sum(1 for n in per_finding.values() if n >= 2) >= 5

    responses = {r.auditor_response for r in all_rounds}
    assert responses == {"accepted", "insufficient"}, (
        "both answers occur in the corpus, not just the happy one"
    )

    # and an insufficient round always leaves the finding open at the time
    for record in all_rounds:
        if record.auditor_response != "insufficient":
            continue
        later = [
            r for r in all_rounds
            if r.finding_id == record.finding_id
            and r.round_number > record.round_number
        ]
        finding = repo["findings"].get(record.finding_id)
        assert later or finding.status == "open", (
            f"{record.finding_id} was found insufficient with no later round, "
            f"so it cannot be closed"
        )
