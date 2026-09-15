"""Section 12: simulated business time on every audit event and notification.

It regressed once. The stages enter the simulated clock, but functions the
dashboard calls directly — opening a round, recording progress — did not, and an
audit entry written outside the clock is stamped with the machine's own date.
Inside a stage that hid; called from a button, it put September's wall-clock
date into a trail that ran through the previous spring.

So this runs a simulated stretch that ends before the real date, through the
scheduler and the calendar jump and then through every action the dashboard
offers, and asserts that nothing written during it is dated outside the stretch.
A wall-clock stamp is today's real date, which lies after the stretch, and is
caught.
"""

from datetime import date

import pytest

from sentinelops import directory
from sentinelops.repositories import repositories
from sentinelops.stages import audits, rounds
from sentinelops.synth import generate_corpus, seed_database
from sentinelops.ui import service

RUN_START = date(2026, 1, 28)


@pytest.fixture(scope="module")
def corpus():
    return generate_corpus()


@pytest.fixture
def run(conn, corpus, tmp_path, monkeypatch):
    """A seeded database, and a marker for what already existed before the run."""
    monkeypatch.setattr(service, "PACK_DIR", tmp_path)
    seed_database(conn, corpus)
    repo = repositories(conn)
    since = max((e.seq for e in repo["audit"].read_all()), default=0)
    known = {n.id for n in repo["notifications"].list()}
    return conn, since, known


def _written_during(conn, since, known):
    """Every audit event and notification stamp the run itself produced."""
    repo = repositories(conn)
    events = [(e.seq, e.action, e.ts) for e in repo["audit"].read_all() if e.seq > since]
    notes = []
    for note in repo["notifications"].list():
        if note.id not in known:
            notes.append((note.id, "sent_at", note.sent_at))
        if note.read_at is not None:
            notes.append((note.id, "read_at", note.read_at))
    return events, notes


def _outside(stamps, until):
    return [stamp for stamp in stamps if not RUN_START <= stamp[2].date() <= until]


def test_nothing_written_during_a_simulated_run_carries_the_wall_clock(run):
    conn, since, known = run
    repo = repositories(conn)
    people = directory.load(conn)

    # the scheduler, and the calendar jump
    for day in (date(2026, 1, 28), date(2026, 2, 28), date(2026, 3, 28)):
        service.tick(conn, day)
    for _ in range(2):
        moment = service.next_event(conn)
        if moment is not None and moment.day <= date(2026, 6, 30):
            service.jump_to_next_event(conn)
    today = service.current_date(conn)
    assert today < date.today(), "the run must end before the real date, or a leak would hide"

    # every action the dashboard offers, as a person at the keyboard takes them
    auditor = service.default_identity(conn)
    finding = next(
        f for f in repo["findings"].list()
        if f.status == "open" and people.get(f.owner_identity)
        and people.get(f.owner_identity).auditable_unit == f.auditable_unit_id
        and not rounds.rounds_for(repo, f.id)
    )
    owner = finding.owner_identity
    assert service.record_progress(conn, finding.id, "action_in_progress", by=owner)[0]
    assert service.open_evidence_round(conn, finding.id, by=owner, evidence_ref="EV-1",
                                       evidence_text="Two of the three accounts are disabled.")[0]
    first = rounds.rounds_for(repo, finding.id)[-1]
    assert service.respond_to_round(conn, first.id, response="insufficient", by=auditor,
                                    remarks="The third account is still live.")[0]
    assert service.open_evidence_round(conn, finding.id, by=owner, evidence_ref="EV-2",
                                       evidence_text="All three disabled; tickets attached.")[0]
    second = rounds.rounds_for(repo, finding.id)[-1]
    assert service.respond_to_round(conn, second.id, response="accepted", by=auditor,
                                    remarks="Confirmed against the tickets.")[0]

    other = next(f for f in repo["findings"].list()
                 if f.status == "open" and f.id != finding.id
                 and not rounds.rounds_for(repo, f.id))
    ok, message = service.close_finding(conn, other.id, by=auditor, remarks="Reviewed in person.")
    assert ok, message

    note = next(n for n in repo["notifications"].list(recipient_identity=auditor) if n.unread)
    assert service.mark_read(conn, note.id, by=auditor)[0]

    instance = next(i for i in repo["instances"].list() if i.status in ("pending", "overdue"))
    service.submit_evidence(
        conn, instance_id=instance.id, filename="review.txt",
        content="Quarterly review completed, reviewer recorded and countersigned.",
        author="R. Baker", doc_type=service.doc_types_for(conn, instance.id)[0], as_of=today,
    )
    service.reassess(conn, instance.id, today)
    service.brief(conn)

    audit = next(a for a in repo["audits"].list()
                 if a.status == "completed" and audits.findings_of(repo, a.id))
    audits.generate_report(conn, audit.id, as_of=today)
    audits.confirm(conn, audit.id, by=audit.auditor_identity, as_of=today)
    audits.issue(conn, audit.id, by=audit.auditor_identity, as_of=today)

    start, end = service.pack_period(conn)
    service.generate_pack(conn, period_start=start, period_end=end, scope="All")

    events, notes = _written_during(conn, since, known)
    assert events and notes, "the run wrote nothing, so this checks nothing"
    leaked_events = _outside(events, today)
    assert not leaked_events, f"audit events outside simulated time: {leaked_events[:5]}"
    leaked_notes = _outside(notes, today)
    assert not leaked_notes, f"notifications outside simulated time: {leaked_notes[:5]}"


def test_the_check_catches_an_event_written_outside_the_clock(run):
    """The guard, verified by planting what it guards against."""
    conn, since, known = run
    repositories(conn)["audit"].append(
        actor="user", owner="nobody", action="planted_without_the_clock",
        entity_type="Cycle", entity_id="planted",
    )
    events, _ = _written_during(conn, since, known)
    assert _outside(events, date(2026, 6, 30)), "a wall-clock stamp must be caught"
