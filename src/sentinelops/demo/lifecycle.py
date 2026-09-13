"""Section 4's lifecycle, walked end to end on one finding.

    python -m sentinelops.demo.lifecycle

Three evidence rounds — two insufficient, one accepted — then closure, printed
with the full audit trail. Then the attempts the system refuses, because a
lifecycle is defined as much by what it will not do as by what it will.

Nothing here is special-cased for the demo. Every call is the same function the
pipeline and the dashboard use, so if this prints, the lifecycle works; and if
somebody weakens a guard, this stops printing what it claims to print.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

from ..authority import AuthorityError
from ..db import connect
from ..directory import load as load_directory
from ..entities import Finding
from ..repositories import repositories, simulated_clock
from ..stages import followup, rounds
from ..synth import generate_corpus, seed_database

RAISED = date(2027, 1, 12)


def _rule(title: str) -> None:
    print(f"\n{title}\n{'-' * len(title)}")


def _trail(repo, finding_id: str) -> None:
    events = list(repo["audit"].read_for("Finding", finding_id))
    for record in repo["rounds"].list(finding_id=finding_id):
        events += repo["audit"].read_for("EvidenceSubmission", record.id)
    events.sort(key=lambda e: e.seq)

    print(f"  {'#':>4}  {'when':<12} {'actor':<6} {'who':<14} {'event':<30} detail")
    print(f"  {'-' * 4}  {'-' * 12} {'-' * 6} {'-' * 14} {'-' * 30} {'-' * 44}")
    for event in events:
        detail = ""
        for key in ("remarks", "auditor_remarks", "closure_remarks", "progress",
                    "response", "evidence_ref", "severity", "note"):
            if event.detail.get(key):
                detail = f"{key}={event.detail[key]}"
                break
        print(
            f"  {event.seq:>4}  {event.ts:%Y-%m-%d}   {event.actor_kind:<6} "
            f"{event.owner[:14]:<14} {event.action:<30} {detail[:44]}"
        )


def build(conn):
    """Seed the register and raise one finding to walk."""
    seed_database(conn, generate_corpus())
    repo, people = repositories(conn), load_directory(conn)
    unit = next(u for u in repo["units"].list() if u.id == "AREA-HR")
    auditors = people.by_role("pa_infosec")

    finding = Finding(
        id="FND-DEMO-LIFECYCLE",
        source="audit",
        auditable_unit_id=unit.id,
        description=(
            "Access for three leavers was not revoked within the five-day "
            "window. The joiners-movers-leavers checklist was completed but "
            "the revocation step is not evidenced for any of the three."
        ),
        raised_by=auditors[0].id,
        raised_at=datetime.combine(RAISED, datetime.min.time().replace(hour=9)),
        owner_identity=unit.owner_identity,
        target_date=RAISED + timedelta(days=7),
        severity="Major",
        severity_assigned_by=auditors[0].id,
        # The AI suggestion sits beside the auditor's decision, never on top of
        # it. Here it disagreed, and the trail keeps both.
        suggested_severity="Minor",
        agreed_action_plan=(
            "Revoke the three accounts and add a monthly reconciliation "
            "between HR leaver records and privileged access holders."
        ),
    )
    with simulated_clock(finding.raised_at):
        repo["findings"].add(finding)
        repo["audit"].append(
            actor="user", owner=people.name(finding.owner_identity),
            action="finding_raised", entity_type="Finding", entity_id=finding.id,
            detail={
                "severity": finding.severity,
                "suggested_severity": finding.suggested_severity,
                "overrode_suggestion": True,
                "owner_identity": finding.owner_identity,
                "target_date": finding.target_date.isoformat(),
                "status": "open",
            },
            actor_identity=auditors[0].id,
        )
    return repo, people, finding, auditors, unit


def walk(conn, repo, people, finding, auditors):
    """Three rounds: insufficient, insufficient, accepted. Then closed."""
    owner, auditor = finding.owner_identity, auditors[1].id

    _rule("THE LOOP")
    print(f"  {finding.id}  ·  {finding.severity} "
          f"(model suggested {finding.suggested_severity})")
    print(f"  owner {people.name(owner)}   auditor {people.name(auditor)}")
    print(f"  raised {RAISED}   target {finding.target_date}")

    script = [
        (9, "acknowledged",
         "EV-JML-EXPORT-JAN",
         "Attaching the joiners-movers-leavers export for January.",
         "insufficient",
         "The export shows the checklist was completed. It does not show the "
         "three accounts being disabled. Please attach the IAM revocation log."),
        (17, "action_in_progress",
         "EV-IAM-REVOCATION-LOG",
         "IAM revocation log attached.",
         "insufficient",
         "The log covers two of the three accounts. The third is still active "
         "in the console as of today."),
        (26, "implemented",
         "EV-IAM-FULL-PLUS-RECONCILIATION",
         "Third account disabled, and the monthly reconciliation is now "
         "running. Both attached.",
         "accepted",
         "All three accounts confirmed disabled and the reconciliation is in "
         "place. This satisfies the agreed action plan."),
    ]

    for days, progress, evidence_ref, note, response, remarks in script:
        when = RAISED + timedelta(days=days)

        followup.record_owner_progress(
            conn, finding.id, progress, by=owner, as_of=when
        )
        record = rounds.open_round(
            repo, people, finding, by=owner, evidence_ref=evidence_ref,
            note=note, as_of=when,
        )
        rounds.respond(
            repo, people, record, response=response, by=auditor,
            remarks=remarks, as_of=when,
        )
        if response == "insufficient":
            followup.record_insufficient_round(
                repo, finding, by=auditor, remarks=remarks,
                owner_name=people.name(auditor), as_of=when,
            )

        current = repo["findings"].get(finding.id)
        print(f"\n  round {record.round_number}  {when}  "
              f"owner says '{progress}'")
        print(f"    filed     {evidence_ref}")
        print(f"    auditor   {response.upper()} — {remarks[:66]}")
        print(f"    finding   status={current.status}  "
              f"follow_up_count={current.follow_up_count}")

    closed = followup.close_finding(
        conn, finding.id, by=auditor,
        remarks=(
            "Closed at round 3. All three accounts confirmed disabled and the "
            "monthly reconciliation is in place."
        ),
        as_of=RAISED + timedelta(days=26),
    )
    print(f"\n  CLOSED    by {people.name(closed.closed_by)} on "
          f"{closed.closed_at:%Y-%m-%d}")
    print(f"    remarks   {closed.closure_remarks}")
    print(f"    rounds    {rounds.round_count(repo, finding.id)} "
          f"({rounds.insufficient_rounds(repo, finding.id)} insufficient)  "
          f"follow_up_count={closed.follow_up_count}")
    return closed


def refusals(conn, repo, people, finding, auditors, unit):
    """What the system will not do. Section 7, and section 1's "only then"."""
    _rule("BLOCKED ATTEMPTS")

    owner = finding.owner_identity
    stranger = next(
        p for p in people.by_role("unit_owner")
        if p.auditable_unit != unit.id
    )

    # A second finding, open, with an unanswered round — for the timing refusal.
    second = Finding(
        id="FND-DEMO-BLOCKED",
        source="audit",
        auditable_unit_id=unit.id,
        description="Training completion tracker cannot be relied on.",
        raised_by=auditors[0].id,
        raised_at=datetime(2027, 2, 1, 9, 0),
        owner_identity=owner,
        target_date=date(2027, 2, 15),
        severity="Minor",
        severity_assigned_by=auditors[0].id,
    )
    with simulated_clock(second.raised_at):
        repo["findings"].add(second)
    pending = rounds.open_round(
        repo, people, second, by=owner, evidence_ref="EV-LMS-EXPORT",
        as_of=date(2027, 2, 3),
    )

    # Ordered so each refusal fires for the reason it claims. The
    # separation-of-duty demonstration mutates who filed the evidence, so it
    # comes last — run earlier, it would shadow the timing refusals and they
    # would pass while proving something else entirely.
    attempts = [
        (
            "the owner closes their own finding",
            "section 7 — only PA/InfoSec closes",
            lambda: followup.close_finding(
                conn, second.id, by=owner, remarks="Done, closing it.",
                as_of=date(2027, 2, 4),
            ),
        ),
        (
            "management closes a finding",
            "section 7 — management reads, it does not decide",
            lambda: followup.close_finding(
                conn, second.id, by=people.by_role("management")[0].id,
                remarks="Close this one.", as_of=date(2027, 2, 4),
            ),
        ),
        (
            "an owner reports progress on another unit's finding",
            "section 7 — own unit only",
            lambda: followup.record_owner_progress(
                conn, second.id, "implemented", by=stranger.id,
                as_of=date(2027, 2, 4),
            ),
        ),
        (
            "an auditor closes it while the evidence sits unanswered",
            "section 1 — open until the auditor is satisfied",
            lambda: followup.close_finding(
                conn, second.id, by=auditors[0].id,
                remarks="Looks fine.", as_of=date(2027, 2, 4),
            ),
        ),
        (
            "an auditor closes it straight after calling the evidence "
            "insufficient",
            "section 1 — insufficient keeps it open",
            lambda: _insufficient_then_closes(
                conn, repo, people, second, pending, auditors
            ),
        ),
        (
            "the auditor who filed the evidence accepts it",
            "section 7 — whoever submitted may never accept",
            lambda: _submitted_then_accepts(repo, people, auditors, second),
        ),
    ]

    for what, rule, attempt in attempts:
        try:
            attempt()
        except (AuthorityError, ValueError) as refused:
            print(f"\n  REFUSED  {what}")
            print(f"    rule     {rule}")
            print(f"    said     {str(refused)[:96]}")
        else:
            raise AssertionError(f"{what!r} was allowed and should not be")

    still = repo["findings"].get(second.id)
    print(f"\n  {second.id} after six refused attempts: status={still.status}")


def _submitted_then_accepts(repo, people, auditors, finding):
    """The submitter is the one trying to accept.

    Filed by an auditor rather than the owner, so the role check passes and the
    separation rule is the only thing left to stop it. On its own round, so it
    cannot change the answer any other attempt gets.
    """
    auditor = auditors[1].id
    record = rounds.open_round(
        repo, people, finding, by=finding.owner_identity,
        evidence_ref="EV-FILED-BY-THE-AUDITOR", as_of=date(2027, 2, 10),
    )
    record.submitted_by = auditor
    repo["rounds"].update(record)
    rounds.respond(
        repo, people, record, response="accepted", by=auditor,
        remarks="Mine, and fine.", as_of=date(2027, 2, 10),
    )


def _insufficient_then_closes(conn, repo, people, finding, record, auditors):
    """Say it is not good enough, then try to close it anyway."""
    reloaded = repo["rounds"].get(record.id)
    if reloaded.auditor_response == "pending":
        rounds.respond(
            repo, people, reloaded, response="insufficient", by=auditors[0].id,
            remarks="The export does not show completion.",
            as_of=date(2027, 2, 6),
        )
        followup.record_insufficient_round(
            repo, repo["findings"].get(finding.id), by=auditors[0].id,
            remarks="The export does not show completion.",
            owner_name=people.name(auditors[0].id), as_of=date(2027, 2, 6),
        )
    followup.close_finding(
        conn, finding.id, by=auditors[0].id,
        remarks="Closing regardless.", as_of=date(2027, 2, 7),
    )


def main() -> None:
    conn = connect(":memory:")
    repo, people, finding, auditors, unit = build(conn)
    walk(conn, repo, people, finding, auditors)

    _rule("AUDIT TRAIL")
    _trail(repo, finding.id)

    refusals(conn, repo, people, finding, auditors, unit)

    _rule("INTEGRITY")
    print(f"  {repo['audit'].verify_chain()}")
    conn.close()


if __name__ == "__main__":
    main()
