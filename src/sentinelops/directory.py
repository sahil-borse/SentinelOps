"""Who people are, and who they answer to.

An `AuditableUnit` records `owner_identity` — an id, not a name — so every
display of an owner and every escalation has to resolve through here. That is
deliberate: in v2 the owner's name and team were copied onto the unit, which
meant two records to keep in step and no way to ask who someone reports to.

Escalation used to synthesise a manager by gluing "Head of " onto a team name.
Now it walks `reports_to`, so the chain is data rather than string formatting,
and a unit owner who reports to the same director as three others escalates to
a person who actually exists.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .entities import ASSESSOR_IDENTITY, SYSTEM_IDENTITY, AuditableUnit, Identity


@dataclass
class Directory:
    """Everyone the system knows about, indexed."""

    people: dict[str, Identity] = field(default_factory=dict)

    def get(self, identity_id: str | None) -> Identity | None:
        return self.people.get(identity_id or "")

    def name(self, identity_id: str | None) -> str:
        """A display name, or the id if we have never heard of them.

        Never raises: an audit trail that cannot be rendered because somebody
        was deleted is worse than one that shows an unresolved id.
        """
        person = self.get(identity_id)
        return person.name if person else (identity_id or "unknown")

    def owner_of(self, unit: AuditableUnit) -> Identity | None:
        return self.get(unit.owner_identity)

    def owner_name(self, unit: AuditableUnit) -> str:
        return self.name(unit.owner_identity)

    def escalation_chain(self, identity_id: str | None) -> list[Identity]:
        """The owner, then whoever they report to, and so on upwards.

        Cycles are broken rather than followed — a reporting line that loops is
        a data problem, not a reason to hang.
        """
        chain: list[Identity] = []
        seen: set[str] = set()
        current = self.get(identity_id)
        while current is not None and current.id not in seen:
            chain.append(current)
            seen.add(current.id)
            current = self.get(current.reports_to)
        return chain

    def by_role(self, role: str) -> list[Identity]:
        return sorted(
            (p for p in self.people.values() if p.role == role), key=lambda p: p.id
        )


def load(conn) -> Directory:
    """Build the directory from whatever the database holds."""
    from .repositories import repositories

    return Directory({i.id: i for i in repositories(conn)["identities"].list()})


def of(identities: list[Identity]) -> Directory:
    return Directory({i.id: i for i in identities})


#: The two non-people. Every event has an actor; not every actor is a person.
SYSTEM = Identity(id=SYSTEM_IDENTITY, name="SentinelOps scheduler", role="pa_infosec")
ASSESSOR = Identity(id=ASSESSOR_IDENTITY, name="SentinelOps assessor", role="pa_infosec")
