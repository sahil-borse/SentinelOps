"""Notification history for one finding, per recipient.

    python -m sentinelops.demo.inbox

One Major finding that nobody answers: three reminders, then escalation up the
reporting line and to PA/InfoSec. Printed as a timeline, then as the inboxes the
people involved would actually open.

The timing is not invented here. Every date comes from the severity table in
`stages.followup`, printed at the top so the schedule and the outcome can be
read against each other on one screen.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

from .. import notify
from ..db import connect
from ..directory import load as load_directory
from ..entities import Finding
from ..repositories import repositories, simulated_clock
from ..stages import followup
from ..synth import generate_corpus, seed_database

RAISED = date(2027, 2, 2)

#: Three follow-up cycles, chosen to land either side of the target date rather
#: than to produce a tidy number. Major against a non-critical unit is seven days
#: to target with escalation three days past it, so day 5 is the pre-target
#: nudge, day 8 is one day late, and day 11 is four days late — far enough past
#: the threshold that the escalation fires on its own.
CYCLES = [RAISED + timedelta(days=n) for n in (5, 8, 11)]


def _rule(title: str) -> None:
    print(f"\n{title}\n{'-' * len(title)}")


def build(conn):
    seed_database(conn, generate_corpus())
    repo, people = repositories(conn), load_directory(conn)
    unit = next(u for u in repo["units"].list() if u.id == "AREA-HR")
    auditor = people.by_role("pa_infosec")[0]

    finding = Finding(
        id="FND-DEMO-INBOX",
        source="audit",
        auditable_unit_id=unit.id,
        description=(
            "Leaver access was not revoked within the five working day window "
            "for three accounts."
        ),
        raised_by=auditor.id,
        raised_at=datetime.combine(RAISED, datetime.min.time().replace(hour=9)),
        owner_identity=unit.owner_identity,
        # Major against a non-critical unit: seven days to target, escalation
        # three days past it. Straight off the table below.
        target_date=followup.target_date_for(
            RAISED, "Major", unit.attributes.get("criticality", "")
        ),
        severity="Major",
        severity_assigned_by=auditor.id,
        agreed_action_plan="Revoke the three accounts and reconcile monthly.",
    )
    with simulated_clock(finding.raised_at):
        repo["findings"].add(finding)
        notify.send(
            repo, people, to=finding.owner_identity, kind="finding_raised",
            subject=f"{finding.id} raised against {unit.name}",
            body=(
                f"{finding.description}\n\nAgreed action: "
                f"{finding.agreed_action_plan}\nSeverity {finding.severity}. "
                f"Target {finding.target_date}."
            ),
            related_entity=finding.id, as_of=RAISED,
            actor_identity=auditor.id,
        )
    return repo, people, finding, unit


def main() -> None:
    conn = connect(":memory:")
    repo, people, finding, unit = build(conn)

    _rule("SECTION 5 - THE POLICY THAT DRIVES THIS")
    print(followup.policy_table())

    _rule("WHAT HAPPENED")
    print(f"  {finding.id}  |  {finding.severity}  |  {unit.name}")
    print(f"  owner {people.name(finding.owner_identity)}   "
          f"raised {RAISED}   target {finding.target_date}")
    print(f"  nobody files anything, so the two clocks just run\n")

    for as_of in CYCLES:
        report = followup.run(conn, as_of)
        # The cycle chases every open finding in the corpus; this demo is about
        # one of them, so the line below counts only its own post.
        mine = [n for n in report.outbox.sent if n.related_entity == finding.id]
        current = repo["findings"].get(finding.id)
        late = (as_of - finding.target_date).days
        when = f"{late:+d}d vs target" if late else "on target"
        reminders = len([n for n in mine if n.kind == "reminder"])
        levels = [lvl for fid, lvl in report.escalated if fid == finding.id]
        fanout = len([n for n in mine if n.kind == "escalation"])
        posted = f"{reminders} reminder"
        if levels:
            # One escalation *event* becomes several rows, because the manager
            # and each auditor get their own. Printing "3 escalation" here
            # would read as three escalations, which is not what happened.
            posted += f", escalation L{levels[0]} -> {fanout} inboxes"
        print(f"  {as_of}  ({when:>13})  {posted:<36}  "
              f"follow_up_count={current.follow_up_count}")

    _rule("NOTIFICATION HISTORY - ONE FINDING, EVERY RECIPIENT")
    print(f"  {'sent':<12} {'kind':<18} {'lvl':>3}  {'recipient':<16} subject")
    print(f"  {'-' * 12} {'-' * 18} {'-' * 3}  {'-' * 16} {'-' * 46}")
    for note in notify.history(conn, finding.id):
        print(
            f"  {note.sent_at:%Y-%m-%d}   {note.kind:<18} "
            f"{note.escalation_level or '':>3}  "
            f"{people.name(note.recipient_identity)[:16]:<16} "
            f"{note.subject[:46]}"
        )

    _rule("THE SAME HISTORY, AS EACH PERSON'S INBOX")
    grouped = notify.by_recipient(conn, finding.id)
    for identity_id, notes in sorted(
        grouped.items(), key=lambda kv: -len(kv[1])
    ):
        person = people.get(identity_id)
        role = person.role.replace("_", "/") if person else "unknown"
        unread = len([n for n in notes if n.unread])
        print(f"\n  {people.name(identity_id)}  ({role})  "
              f"- {len(notes)} message(s), {unread} unread")
        for note in notes:
            marker = "  " if note.unread else "read"
            print(f"    {marker} {note.sent_at:%Y-%m-%d}  {note.kind:<18} "
                  f"{note.subject[:52]}")

    _rule("READING ONE")
    owner, auditor = finding.owner_identity, people.by_role("pa_infosec")[0].id

    def waiting(identity_id: str) -> int:
        return len([
            n for n in notify.inbox(conn, identity_id, unread_only=True)
            if n.related_entity == finding.id
        ])

    before_owner, before_auditor = waiting(owner), waiting(auditor)
    opened = notify.history(conn, finding.id)[0]
    notify.mark_read(conn, opened.id, by=owner, as_of=CYCLES[-1])
    print(f"  {people.name(owner)} opens {opened.id}: {opened.subject}")
    print(f"    unread for {people.name(owner):<12} "
          f"{before_owner} -> {waiting(owner)}")
    print(f"    unread for {people.name(auditor):<12} "
          f"{before_auditor} -> {waiting(auditor)}"
          f"   (their copy is a separate row, and stays unread)")

    _rule("COST")
    spent = conn.execute("SELECT COUNT(*) c FROM token_usage").fetchone()["c"]
    print(f"  model calls while chasing: {spent}")
    print(f"  delivery: recorded, never sent - section 11 rules out email")
    print(f"  {repo['audit'].verify_chain()}")
    conn.close()


if __name__ == "__main__":
    main()
