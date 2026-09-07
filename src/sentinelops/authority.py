"""Section 7 — who may do what, and the two things nobody may do.

Two separate rules, and conflating them is how segregation of duties quietly
stops working:

**Role permissions** are the table in section 7. A `unit_owner` submits evidence
and reports progress; a `pa_infosec` raises findings, assigns severity, answers
rounds and closes; `management` reads. This is a lookup, and a lookup is all it
is.

**Separation of duty** is the rule the table cannot express: *the identity that
submitted a round may never be the identity that accepts it or closes the
finding it belongs to.* An auditor with a `pa_infosec` role still fails this
check if they are the person who filed the evidence. It is a rule about the
history of a particular finding, not about a role, which is exactly why it needs
its own function and its own test.

Both are enforced where the state changes, not at the UI, because a rule that
only exists in a screen is not a control. The screen honours it too — section 7
asks for the owner's Close button to be **absent, not disabled** — but that is a
courtesy on top, not the enforcement.
"""

from __future__ import annotations

from dataclasses import dataclass

from .entities import Role

#: The section 7 table, transcribed. Keys are the actions the system actually
#: performs; a stage calling `require` with an action not listed here fails
#: loudly, because an unlisted action is an ungoverned one.
PERMISSIONS: dict[str, tuple[Role, ...]] = {
    "conduct_audit": ("pa_infosec",),
    "raise_finding": ("pa_infosec",),
    "assign_severity": ("pa_infosec",),
    "set_owner_progress": ("unit_owner",),
    "submit_evidence": ("unit_owner",),
    "respond_to_submission": ("pa_infosec",),
    "close_finding": ("pa_infosec",),
    "view_escalations": ("pa_infosec", "management"),
    "view_portfolio": ("pa_infosec", "management"),
}

#: The system acts for itself during a scheduled cycle — creating instances,
#: sending reminders. It is not a person and holds no role, so it is named here
#: rather than given a role that would also let it close findings.
SYSTEM_ACTIONS = frozenset({"raise_finding"})


class AuthorityError(PermissionError):
    """A blocked action. Raised, never returned — a refusal that can be ignored
    by a caller who forgot to check the return value is not a control."""


@dataclass(frozen=True)
class Decision:
    allowed: bool
    reason: str = ""

    def __bool__(self) -> bool:
        return self.allowed


def permitted(role: str | None, action: str) -> Decision:
    """Does this role hold this permission? Section 7's table, and only that."""
    if action not in PERMISSIONS:
        raise KeyError(
            f"{action!r} is not in the section 7 permission table; "
            "add it there rather than letting it run ungoverned"
        )
    allowed = PERMISSIONS[action]
    if role in allowed:
        return Decision(True)
    return Decision(
        False,
        f"a {role or 'roleless identity'} may not {action.replace('_', ' ')}; "
        f"section 7 reserves it for {' or '.join(allowed)}",
    )


def separated(submitter_ids, actor_id: str, action: str) -> Decision:
    """Is this actor clear of the evidence they are about to judge?

    `submitter_ids` is every identity that filed a round on the finding. The
    rule is about the finding's whole history and not just the round in hand:
    somebody who filed round 1 may not accept round 2 either.
    """
    if actor_id in set(submitter_ids):
        return Decision(
            False,
            f"{actor_id} submitted evidence on this finding and may not also "
            f"{action.replace('_', ' ')} it",
        )
    return Decision(True)


def require(role: str | None, action: str, *, actor_id: str = "") -> None:
    """Permit the action or raise. The form every stage should call."""
    if actor_id and actor_id.startswith("ID-SYSTEM") and action in SYSTEM_ACTIONS:
        return
    decision = permitted(role, action)
    if not decision:
        raise AuthorityError(decision.reason)


def require_separation(submitter_ids, actor_id: str, action: str) -> None:
    decision = separated(submitter_ids, actor_id, action)
    if not decision:
        raise AuthorityError(decision.reason)


def actions_for(role: str | None) -> list[str]:
    """What this role may do. Used by the UI to omit controls rather than
    disable them — a greyed-out Close button still tells the owner that closing
    is a thing they nearly can do."""
    return sorted(a for a, roles in PERMISSIONS.items() if role in roles)
