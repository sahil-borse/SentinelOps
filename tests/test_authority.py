"""Section 7 — segregation of duties, enforced rather than documented.

Two independent rules, tested independently, because they fail in different
ways: a role table that is right but never consulted, and a separation rule that
is consulted but only against the round in hand.

The two blocked paths section 7 names explicitly each have a test here, and each
was checked by removing the guard and watching the test fail — a permission test
that passes because the path was never reachable proves nothing.
"""

from datetime import date, datetime, timedelta

import pytest

from sentinelops import authority
from sentinelops.authority import AuthorityError
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
def seeded(conn, corpus):
    seed_database(conn, corpus)
    return conn


@pytest.fixture
def finding(seeded):
    """One open finding, owned by a real unit owner, with nothing done to it."""
    repo = repositories(seeded)
    people = load_directory(seeded)
    unit = repo["units"].list()[0]
    record = Finding(
        id="FND-SOD-1",
        source="audit",
        auditable_unit_id=unit.id,
        description="Access review for Q2 was not evidenced.",
        raised_by=people.by_role("pa_infosec")[0].id,
        raised_at=datetime(2026, 6, 1, 9, 0),
        owner_identity=unit.owner_identity,
        target_date=date(2026, 6, 15),
        severity="Minor",
        severity_assigned_by=people.by_role("pa_infosec")[0].id,
    )
    with simulated_clock(datetime(2026, 6, 1, 9, 0)):
        repo["findings"].add(record)
    return record


# --- the role table ----------------------------------------------------------

def test_the_table_matches_section_seven():
    """Transcribed, not invented. Each row is a line in the spec."""
    assert authority.PERMISSIONS["raise_finding"] == ("pa_infosec",)
    assert authority.PERMISSIONS["assign_severity"] == ("pa_infosec",)
    assert authority.PERMISSIONS["submit_evidence"] == ("unit_owner",)
    assert authority.PERMISSIONS["respond_to_submission"] == ("pa_infosec",)
    assert authority.PERMISSIONS["close_finding"] == ("pa_infosec",)
    assert set(authority.PERMISSIONS["view_portfolio"]) == {
        "pa_infosec", "management"
    }


def test_no_role_holds_both_sides_of_the_evidence_loop():
    """Whoever submits may not be whoever accepts. True of every role."""
    for role in ("pa_infosec", "unit_owner", "management"):
        submits = bool(authority.permitted(role, "submit_evidence"))
        accepts = bool(authority.permitted(role, "respond_to_submission"))
        assert not (submits and accepts), role


def test_management_reads_and_writes_nothing():
    for action in ("raise_finding", "assign_severity", "submit_evidence",
                   "respond_to_submission", "close_finding"):
        assert not authority.permitted("management", action)
    assert authority.permitted("management", "view_portfolio")


def test_an_unlisted_action_is_a_hard_error_not_a_default():
    """An ungoverned action must fail loudly, not fall through to allowed."""
    with pytest.raises(KeyError):
        authority.permitted("pa_infosec", "delete_everything")


def test_a_refusal_says_why():
    decision = authority.permitted("unit_owner", "close_finding")
    assert not decision
    assert "close finding" in decision.reason
    assert "pa_infosec" in decision.reason


# --- blocked path 1: the owner may not close their own finding ---------------

def test_an_owner_cannot_close_their_own_finding(seeded, finding):
    """The first path section 7 blocks."""
    with pytest.raises(AuthorityError) as refused:
        followup.close_finding(
            seeded, finding.id, by=finding.owner_identity,
            remarks="Looks done to me.", as_of=AS_OF,
        )
    assert "close finding" in str(refused.value)
    assert repositories(seeded)["findings"].get(finding.id).status == "open"


def test_management_cannot_close_a_finding_either(seeded, finding):
    people = load_directory(seeded)
    boss = people.by_role("management")[0]
    with pytest.raises(AuthorityError):
        followup.close_finding(
            seeded, finding.id, by=boss.id, remarks="Close it.", as_of=AS_OF
        )
    assert repositories(seeded)["findings"].get(finding.id).status == "open"


def test_an_auditor_can_close_it(seeded, finding):
    """The guard blocks the wrong people, not everybody."""
    people = load_directory(seeded)
    auditor = people.by_role("pa_infosec")[0]
    closed = followup.close_finding(
        seeded, finding.id, by=auditor.id,
        remarks="Re-certification evidence accepted.", as_of=AS_OF,
    )
    assert closed.status == "closed"
    assert closed.closed_by == auditor.id


# --- blocked path 2: whoever filed the evidence may not accept it ------------

def test_the_identity_that_submitted_evidence_cannot_accept_it(seeded, finding):
    """The second path, and the one a role table alone cannot express.

    The submitter here holds `pa_infosec`, so the role check passes. Only the
    separation rule stops them, which is exactly why it is a separate rule.
    """
    repo = repositories(seeded)
    people = load_directory(seeded)
    auditor = people.by_role("pa_infosec")[0]

    # they file the evidence themselves
    round_record = rounds.open_round(
        repo, people, finding, by=finding.owner_identity,
        evidence_ref="EV-X", as_of=AS_OF,
    )
    round_record.submitted_by = auditor.id
    repo["rounds"].update(round_record)

    assert authority.permitted(auditor.role, "respond_to_submission"), (
        "the role check must pass, or this test proves the wrong thing"
    )
    with pytest.raises(AuthorityError) as refused:
        rounds.respond(
            repo, people, round_record, response="accepted", by=auditor.id,
            remarks="Fine by me.", as_of=AS_OF,
        )
    assert "submitted evidence" in str(refused.value)
    assert repo["rounds"].get(round_record.id).auditor_response == "pending"


def test_the_identity_that_submitted_evidence_cannot_close_the_finding(
    seeded, finding
):
    repo = repositories(seeded)
    people = load_directory(seeded)
    auditor = people.by_role("pa_infosec")[0]

    round_record = rounds.open_round(
        repo, people, finding, by=finding.owner_identity,
        evidence_ref="EV-X", as_of=AS_OF,
    )
    round_record.submitted_by = auditor.id
    repo["rounds"].update(round_record)

    with pytest.raises(AuthorityError) as refused:
        followup.close_finding(
            seeded, finding.id, by=auditor.id, remarks="Done.", as_of=AS_OF
        )
    assert "submitted evidence" in str(refused.value)
    assert repo["findings"].get(finding.id).status == "open"


def test_separation_looks_at_the_whole_history_not_the_round_in_hand(
    seeded, finding
):
    """Filing round 1 disqualifies you from accepting round 2."""
    repo = repositories(seeded)
    people = load_directory(seeded)
    auditor = people.by_role("pa_infosec")[0]
    other = people.by_role("pa_infosec")[1]

    first = rounds.open_round(
        repo, people, finding, by=finding.owner_identity,
        evidence_ref="EV-1", as_of=AS_OF,
    )
    first.submitted_by = auditor.id
    repo["rounds"].update(first)
    rounds.respond(
        repo, people, first, response="insufficient", by=other.id,
        remarks="The tracker does not cover March.", as_of=AS_OF,
    )

    second = rounds.open_round(
        repo, people, finding, by=finding.owner_identity,
        evidence_ref="EV-2", as_of=AS_OF + timedelta(days=3),
    )
    with pytest.raises(AuthorityError):
        rounds.respond(
            repo, people, second, response="accepted", by=auditor.id,
            remarks="Better.", as_of=AS_OF + timedelta(days=3),
        )
    # the colleague who did not file it still can
    rounds.respond(
        repo, people, second, response="accepted", by=other.id,
        remarks="March is now covered.", as_of=AS_OF + timedelta(days=3),
    )
    assert repo["rounds"].get(second.id).auditor_response == "accepted"


# --- scope: an owner acts on their own unit only -----------------------------

def test_an_owner_cannot_report_progress_on_another_units_finding(
    seeded, finding
):
    people = load_directory(seeded)
    stranger = next(
        p for p in people.by_role("unit_owner")
        if p.auditable_unit != finding.auditable_unit_id
    )
    with pytest.raises(AuthorityError) as refused:
        followup.record_owner_progress(
            seeded, finding.id, "implemented", by=stranger.id
        )
    assert "own unit" in str(refused.value)


def test_the_owner_of_the_unit_can(seeded, finding):
    updated = followup.record_owner_progress(
        seeded, finding.id, "implemented", by=finding.owner_identity
    )
    assert updated.owner_progress == "implemented"
    assert updated.status == "open", "progress still closes nothing"


# --- severity stays with the auditor ----------------------------------------

def test_an_owner_cannot_assign_their_own_severity(seeded, finding):
    with pytest.raises(AuthorityError):
        followup.assign_severity(
            seeded, finding.id, "Observation", by=finding.owner_identity,
            remarks="Not really a big deal.",
        )
    assert repositories(seeded)["findings"].get(finding.id).severity == "Minor"


# --- what the UI is told -----------------------------------------------------

def test_actions_for_drives_an_absent_control_not_a_disabled_one():
    """The UI asks this rather than hard-coding a role check of its own."""
    assert "close_finding" in authority.actions_for("pa_infosec")
    assert "close_finding" not in authority.actions_for("unit_owner")
    assert "submit_evidence" in authority.actions_for("unit_owner")
    assert authority.actions_for(None) == []
