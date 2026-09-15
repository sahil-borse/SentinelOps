"""Slice 18: jump through one finding's reminder and escalation timeline, then reset.

    python -m sentinelops.demo.jumps

Replays the corpus to the vantage point, picks the audit finding whose first
reminder comes soonest, and jumps from milestone to milestone on that finding
alone — naming each event before the jump, then printing what the trail
recorded on the day it landed. Then, on a demo database of its own, it resets
the scenario and shows the state digest back where it started.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from .. import timeline
from ..db import connect
from ..periods import monthly_cycles
from ..repositories import repositories
from ..synth import generate_corpus, seed_database
from ..synth.calendar import CORPUS_WINDOW, SIMULATED_TODAY
from ..ui import service


def _rule(title: str) -> None:
    print(f"\n{title}\n{'-' * len(title)}")


def _when(day) -> str:
    return f"{day:%a} {day.day} {day:%b %Y}"


def jump_sequence() -> None:
    conn = connect(":memory:")
    seed_database(conn, generate_corpus())
    for day in monthly_cycles(CORPUS_WINDOW, SIMULATED_TODAY) + [SIMULATED_TODAY]:
        service.tick(conn, day)
    repo = repositories(conn)
    today = service.current_date(conn)

    # The finding whose first reminder comes soonest — an audit finding if one
    # has its whole timeline ahead, since nothing but an auditor closes those.
    starts = [e for e in timeline.upcoming(conn, today) if e.kind == "reminder"]
    if not starts:
        print("  no open finding has its reminder timeline ahead of the calendar")
        conn.close()
        return
    audit_starts = [e for e in starts if repo["findings"].get(e.subject).source == "audit"]
    subject = (audit_starts or starts)[0].subject
    finding = repo["findings"].get(subject)
    _rule(f"JUMP SEQUENCE - {subject}")
    print(f"  {finding.description[:96]}")
    print(f"  severity {finding.severity} · target {_when(finding.target_date)} · "
          f"calendar at {_when(today)}")

    while True:
        now = service.current_date(conn)
        moment = service.next_event(conn, subject=subject)
        if moment is None:
            current = repo["findings"].get(subject)
            if current.status == "closed":
                print(f"\n  closed on {_when(current.closed_at.date())} by "
                      f"{current.closed_by}: {current.closure_remarks[:80]}")
            else:
                print("\n  no further milestone for this finding")
            break
        event = moment.headline
        print(f"\n  next event  {event.title} on {_when(moment.day)} "
              f"(in {(moment.day - now).days} day(s))")
        jumped = service.jump_to_next_event(conn, subject=subject)
        print(f"  jumped      calendar at {_when(service.current_date(conn))} · cycle "
              f"sent {jumped.tick.reminders_sent} reminder(s) across the portfolio")
        for entry in repo["audit"].read_all():
            if entry.entity_id != subject or entry.ts.date() != jumped.day:
                continue
            if entry.action == "finding_reminder_sent":
                print(f"  recorded    reminder, chase #{entry.detail['follow_up_count']} "
                      f"({entry.detail['days_to_target']:+d} days to target)")
            elif entry.action == "finding_escalated":
                print(f"  recorded    escalation level {entry.detail['level']} to "
                      f"{entry.owner}, {entry.detail['days_past_target']} day(s) past target")
        notes = [n for n in repo["notifications"].list(related_entity=subject)
                 if n.sent_at.date() == jumped.day]
        kinds = ", ".join(sorted({n.kind for n in notes})) or "nothing"
        print(f"  notified    {kinds} -> {len(notes)} recipient row(s), dated "
              f"{sorted({n.sent_at.date().isoformat() for n in notes})}")
    conn.close()


def _counts(conn) -> str:
    repo = repositories(conn)
    return (
        f"{len(repo['instances'].list())} checks · "
        f"{len([f for f in repo['findings'].list() if f.status == 'open'])} open findings · "
        f"{len(repo['audit'].read_all())} audit events · "
        f"{len(repo['notifications'].list())} notifications"
    )


def reset_demo() -> None:
    _rule("SCENARIO RESET")
    original = service.DB_PATH
    with tempfile.TemporaryDirectory() as folder:
        service.DB_PATH = Path(folder) / "sentinelops.db"
        try:
            snapshot = service.ensure_snapshot()
            service.reset_scenario()
            conn = service.open_database()
            seeded = service.state_digest(conn)
            print(f"  snapshot    {snapshot.name}")
            print(f"  seeded      digest {seeded[:16]} · {_counts(conn)}")
            for _ in range(3):
                jumped = service.jump_to_next_event(conn)
                event = jumped.moment.headline
                print(f"  jumped      {_when(jumped.day)} · {event.title} · {event.subject}")
            print(f"  after       digest {service.state_digest(conn)[:16]} · {_counts(conn)}")
            conn.close()

            service.reset_scenario()
            conn = service.open_database()
            restored = service.state_digest(conn)
            print(f"  reset       digest {restored[:16]} · {_counts(conn)}")
            print(f"  identical to the seeded state: {restored == seeded}")
            conn.close()
        finally:
            service.DB_PATH = original


def main() -> None:
    jump_sequence()
    reset_demo()


if __name__ == "__main__":
    main()
