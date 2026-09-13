"""Notifications as records, and the inbox that falls out of them.

Nothing here sends anything. Section 11 rules out real email, so `send` means
*record that somebody needed to be told*, in simulated business time. A delivery
mechanism would sit behind this and read the same rows; none exists, and the
word `send` is kept because it is what the system is doing from its own point of
view.

**Why records rather than log lines.** These were dictionaries written into the
audit trail. The trail knew a notification had happened, which is enough to
prove the system did its job and useless for doing the job: nobody could ask
"what is waiting for D. Ferreira this morning?" without replaying every event
and reassembling payloads. One table later, that question is a query, and the
per-role inbox is the same query with a different identity.

**PA/InfoSec see more than the owning unit.** Section 1 has the audit team
chasing, reviewing and deciding closure, so a notification that only ever
reached the owner would leave them running the follow-up blind. `COPIED_TO_AUDIT`
names the kinds they are copied on — status changes, evidence arriving, anything
going overdue, and any request to close. Copies are separate rows, because
"P. Kaur has read it" and "D. Ferreira has read it" are separate facts.

The audit trail still gets an entry for every notification. The record is the
working copy; the trail is the evidence that it existed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time
from typing import Any

from .directory import Directory
from .entities import Notification, NotificationKind

#: Every kind, in the order a reader would expect to meet them.
KINDS: tuple[str, ...] = (
    "audit_due",
    "activity_due",
    "finding_raised",
    "reminder",
    "evidence_requested",
    "overdue",
    "escalation",
    "evidence_submitted",
    "closure",
    "exception_lapsed",
)

#: Kinds PA/InfoSec are copied on even when the notification is addressed to a
#: unit owner. Section 1: they conduct the audits, chase the findings and decide
#: closure, so these are the events they cannot be the last to hear about.
COPIED_TO_AUDIT: frozenset[str] = frozenset({
    "finding_raised",
    "evidence_submitted",
    "overdue",
    "escalation",
    "closure",
    "exception_lapsed",
})

#: The hour a notification is stamped at, so a day's messages sort in the order
#: they were decided rather than arbitrarily.
SENT_AT = time(8, 0)


@dataclass
class Outbox:
    """What one run of something decided to tell people."""

    sent: list[Notification] = field(default_factory=list)

    def of_kind(self, kind: str) -> list[Notification]:
        return [n for n in self.sent if n.kind == kind]

    def to(self, identity_id: str) -> list[Notification]:
        return [n for n in self.sent if n.recipient_identity == identity_id]

    def summary(self) -> str:
        by_kind: dict[str, int] = {}
        for note in self.sent:
            by_kind[note.kind] = by_kind.get(note.kind, 0) + 1
        return ", ".join(f"{n} {k}" for k, n in sorted(by_kind.items())) or "none"


def _next_id(repo, related_entity: str) -> str:
    existing = len(repo["notifications"].list(related_entity=related_entity))
    return f"NTF-{related_entity}-{existing + 1:03d}"


def send(
    repo,
    people: Directory,
    *,
    to: str,
    kind: NotificationKind,
    subject: str,
    body: str,
    related_entity: str,
    as_of: date,
    escalation_level: int = 0,
    actor_identity: str = "ID-SYSTEM",
    copy_audit: bool | None = None,
    outbox: Outbox | None = None,
) -> list[Notification]:
    """Record that somebody needs to know. Returns every row written.

    `copy_audit` defaults to whether this kind is in `COPIED_TO_AUDIT`, so the
    rule lives in one place rather than at each call site. Pass it explicitly
    only to say something the default gets wrong — a notification already
    addressed to an auditor does not need copying to the auditors.
    """
    from .repositories import simulated_clock

    if kind not in KINDS:
        raise ValueError(f"{kind!r} is not a notification kind")

    stamp = datetime.combine(as_of, SENT_AT)
    recipients = [to]
    if copy_audit is None:
        copy_audit = kind in COPIED_TO_AUDIT
    if copy_audit:
        for auditor in people.by_role("pa_infosec"):
            if auditor.id not in recipients:
                recipients.append(auditor.id)

    written: list[Notification] = []
    with simulated_clock(stamp):
        for recipient in recipients:
            note = Notification(
                id=_next_id(repo, related_entity),
                recipient_identity=recipient,
                kind=kind,
                subject=subject,
                body=body,
                sent_at=stamp,
                related_entity=related_entity,
                escalation_level=escalation_level,
            )
            repo["notifications"].add(note)
            written.append(note)
            if outbox is not None:
                outbox.sent.append(note)

        repo["audit"].append(
            actor="system",
            owner=people.name(to),
            action="notification_sent",
            entity_type="Notification",
            entity_id=written[0].id,
            detail={
                "kind": kind,
                "subject": subject,
                "related_entity": related_entity,
                "recipients": [n.recipient_identity for n in written],
                "copied_to_audit": copy_audit,
                "escalation_level": escalation_level,
                "delivery": "recorded_not_sent",
            },
            actor_identity=actor_identity,
        )
    return written


# --- reading -----------------------------------------------------------------

def inbox(
    conn, identity_id: str, *, unread_only: bool = False, kinds=None,
) -> list[Notification]:
    """One identity's notifications, newest first. This is the per-role inbox."""
    from .repositories import repositories

    rows = repositories(conn)["notifications"].list(
        recipient_identity=identity_id
    )
    if unread_only:
        rows = [n for n in rows if n.unread]
    if kinds:
        wanted = set(kinds)
        rows = [n for n in rows if n.kind in wanted]
    return sorted(rows, key=lambda n: (n.sent_at, n.id), reverse=True)


def history(conn, related_entity: str) -> list[Notification]:
    """Everything anybody was told about one thing, oldest first."""
    from .repositories import repositories

    return sorted(
        repositories(conn)["notifications"].list(related_entity=related_entity),
        key=lambda n: (n.sent_at, n.id),
    )


def unread_count(conn, identity_id: str) -> int:
    return len(inbox(conn, identity_id, unread_only=True))


def mark_read(conn, notification_id: str, *, by: str, as_of: date) -> Notification:
    """The only mutation a notification allows, and only by its recipient."""
    from .repositories import repositories, simulated_clock

    repo = repositories(conn)
    note = repo["notifications"].get(notification_id)
    if note is None:
        raise ValueError(f"no such notification: {notification_id}")
    if note.recipient_identity != by:
        raise PermissionError(
            f"{notification_id} was addressed to {note.recipient_identity}; "
            f"{by} cannot mark it read"
        )
    if note.read_at is not None:
        return note
    stamp = datetime.combine(as_of, time(9, 0))
    with simulated_clock(stamp):
        note.read_at = stamp
        repo["notifications"].update(note)
    return note


def by_recipient(conn, related_entity: str) -> dict[str, list[Notification]]:
    """One thing's notification history, grouped by who was told."""
    grouped: dict[str, list[Notification]] = {}
    for note in history(conn, related_entity):
        grouped.setdefault(note.recipient_identity, []).append(note)
    return grouped
