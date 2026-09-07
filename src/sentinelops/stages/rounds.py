"""Section 4's review loop, as durable rounds.

The stakeholder described this part more precisely than any other, so it is
modelled literally rather than inferred:

> If evidence is insufficient, PA/InfoSec communicate the gaps and request
> revised evidence. The finding remains Open until the auditor is fully
> satisfied. Only then is it formally closed.

Three consequences, each of which is a function here:

* **Opening a round** is what the owner does. It does not change the finding's
  status, because the owner cannot; it records that they have filed something
  and are now waiting.
* **Answering a round** is what the auditor does, and there are exactly two
  answers. `accepted` closes the finding. `insufficient` returns the gaps,
  increments `follow_up_count`, and leaves the finding open with round N+1
  expected.
* **A round is never edited once answered.** Revised evidence opens a new round.
  That is what makes "this one took four rounds" a fact rather than an estimate.

Both writes go through `authority`, and the separation-of-duty rule is checked
against the finding's whole submission history rather than the round in hand:
whoever filed round 1 may not accept round 2 either.
"""

from __future__ import annotations

from datetime import date, datetime, time

from .. import authority
from ..directory import Directory
from ..entities import EvidenceSubmission, Finding


def rounds_for(repo, finding_id: str) -> list[EvidenceSubmission]:
    """Every round on a finding, oldest first."""
    return sorted(
        repo["rounds"].list(finding_id=finding_id), key=lambda r: r.round_number
    )


def submitters_of(repo, finding_id: str) -> set[str]:
    """Everyone who has filed evidence on this finding.

    The separation-of-duty rule reads this, not the single round being answered
    — otherwise filing round 1 and accepting round 2 would pass.
    """
    return {r.submitted_by for r in rounds_for(repo, finding_id)}


def open_round(
    repo,
    people: Directory,
    finding: Finding,
    *,
    by: str,
    evidence_ref: str,
    note: str = "",
    as_of: date,
) -> EvidenceSubmission:
    """The owner files evidence. The finding does not move.

    Deliberately no `status` change: section 4 is emphatic that the owner's
    actions are advisory. What this does record is that the ball is now with the
    auditor, which is what `is_open` on the round means.
    """
    identity = people.get(by)
    authority.require(identity.role if identity else None, "submit_evidence",
                      actor_id=by)

    existing = rounds_for(repo, finding.id)
    if existing and existing[-1].is_open:
        raise ValueError(
            f"{finding.id} already has an unanswered round "
            f"({existing[-1].id}); the auditor answers before the next one opens"
        )

    number = len(existing) + 1
    submission = EvidenceSubmission(
        id=f"SUB-{finding.id.removeprefix('FND-')}-R{number}",
        finding_id=finding.id,
        round_number=number,
        submitted_by=by,
        submitted_at=datetime.combine(as_of, time(10, 0)),
        evidence_ref=evidence_ref,
        owner_note=note,
        auditor_response="pending",
    )
    repo["rounds"].add(submission)
    repo["audit"].append(
        actor="user", owner=people.name(by), action="evidence_round_opened",
        entity_type="EvidenceSubmission", entity_id=submission.id,
        detail={
            "finding_id": finding.id,
            "round_number": number,
            "evidence_ref": evidence_ref,
            "submitted_by": by,
            "owner_note": note,
            "finding_status": finding.status,
            "note": "filing evidence does not move the finding; the auditor does",
        },
        actor_identity=by,
    )
    return submission


def respond(
    repo,
    people: Directory,
    submission: EvidenceSubmission,
    *,
    response: str,
    by: str,
    remarks: str,
    as_of: date,
) -> EvidenceSubmission:
    """The auditor answers a round. Accepted or insufficient, nothing else.

    Closing the finding is *not* done here — `followup.close_on_repo` owns that,
    and the caller does it after an acceptance. Two functions that can both
    close a finding is one too many.
    """
    if response not in ("accepted", "insufficient"):
        raise ValueError(
            f"{response!r} is not an answer; a round is accepted or insufficient"
        )
    if not remarks.strip():
        raise ValueError(
            "a response without remarks tells the owner nothing; "
            "section 4 requires the gaps to be communicated"
        )
    if not submission.is_open:
        raise ValueError(
            f"{submission.id} was already answered "
            f"({submission.auditor_response}); revised evidence opens a new round"
        )

    identity = people.get(by)
    authority.require(identity.role if identity else None,
                      "respond_to_submission", actor_id=by)
    authority.require_separation(
        submitters_of(repo, submission.finding_id), by, "respond_to_submission"
    )

    submission.auditor_response = response  # type: ignore[assignment]
    submission.auditor_remarks = remarks
    submission.responded_by = by
    submission.responded_at = datetime.combine(as_of, time(11, 0))
    repo["rounds"].update(submission)
    repo["audit"].append(
        actor="user", owner=people.name(by),
        action=(
            "evidence_round_accepted" if response == "accepted"
            else "evidence_round_insufficient"
        ),
        entity_type="EvidenceSubmission", entity_id=submission.id,
        detail={
            "finding_id": submission.finding_id,
            "round_number": submission.round_number,
            "response": response,
            "remarks": remarks,
            "responded_by": by,
            "submitted_by": submission.submitted_by,
        },
        actor_identity=by,
    )
    return submission


def round_count(repo, finding_id: str) -> int:
    return len(rounds_for(repo, finding_id))


def insufficient_rounds(repo, finding_id: str) -> int:
    return sum(
        1 for r in rounds_for(repo, finding_id)
        if r.auditor_response == "insufficient"
    )
