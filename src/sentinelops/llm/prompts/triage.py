"""Uses 1 and 4 of section 2: classify the gap, and suggest a severity.

**Why a model.** Section 1 is explicit that no standard gap taxonomy exists and
that the auditor describes each gap in their own words. That is the whole
problem. "Three leavers still held privileged access", "contractors retained
active accounts after their engagements ended" and "a partner's API credential
was never revoked" are the same gap written by three people who have never
compared notes. Mapping free text onto a taxonomy the source organisation does
not have is language work, and there is no rule that does it.

**The taxonomy is ours, and that is stated rather than hidden.** The categories
below were derived from the domain, not collected from the stakeholder — they
said there is no taxonomy, and inventing one and then pretending it was theirs
would be dishonest. What matters is that it is a *closed set*: a free-form label
would let the model write "access control" one week and "access management" the
next, and recurrence detection built on that would be measuring the model's
vocabulary rather than the organisation's problems.

**Both outputs are advisory.** The category is overridable by the auditor
(section 2, use 1) and the severity suggestion is exactly that — section 2 use 4
and the domain model both say the auditor assigns the severity that counts.

**One call, two answers.** Sections 2 lists these separately and they are
separate decisions, but they read the same sentence to reach it. Asking twice
would double the bill to re-read one paragraph. The prompt keeps them distinct
in the output so an override of one does not disturb the other.
"""

from __future__ import annotations

from typing import Any

#: Travels onto every finding this prompt classifies.
PROMPT_VERSION = "triage_v1"

#: The closed set. Ten categories, each one a kind of failure rather than a kind
#: of document, because "the manual is out of date" and "the register is out of
#: date" are the same problem and should land in the same bucket.
GAP_CATEGORIES: tuple[str, ...] = (
    "access_not_revoked",
    "access_not_recertified",
    "periodic_review_overdue",
    "evidence_not_retained",
    "control_not_performed",
    "documentation_out_of_date",
    "third_party_due_diligence",
    "change_not_authorised",
    "training_not_completed",
    "data_retention_or_privacy",
)

#: What each one means, sent to the model so it is choosing between defined
#: things rather than guessing at a label. Also what the UI shows a human.
CATEGORY_DEFINITIONS: dict[str, str] = {
    "access_not_revoked": (
        "Access that should have been removed was left in place — leavers, "
        "ended engagements, closed projects, expired credentials."
    ),
    "access_not_recertified": (
        "Access still exists and may well be correct, but nobody confirmed it "
        "within the required period."
    ),
    "periodic_review_overdue": (
        "A review that runs on a cycle — risk register, process, supplier list "
        "— was not carried out when it fell due."
    ),
    "evidence_not_retained": (
        "The work may have been done, but the record of it cannot be produced, "
        "or the record cannot be relied upon."
    ),
    "control_not_performed": (
        "The control itself was not carried out at all in the period."
    ),
    "documentation_out_of_date": (
        "A manual, procedure or controlled document no longer describes the "
        "process actually followed."
    ),
    "third_party_due_diligence": (
        "Checks owed on a supplier or partner were incomplete or missing."
    ),
    "change_not_authorised": (
        "A change, release or deployment went ahead without the approval or "
        "review the process requires."
    ),
    "training_not_completed": (
        "Required training or awareness activity was not completed or cannot "
        "be evidenced."
    ),
    "data_retention_or_privacy": (
        "Personal data held beyond its retention period, or handled without "
        "the assessment or safeguards required."
    ),
}

SEVERITIES: tuple[str, ...] = ("Major", "Minor", "Observation")

TRIAGE_SYSTEM_V1 = (
    "You classify compliance audit findings. You are given one finding written "
    "in an auditor's own words, plus context about the unit it was raised "
    "against.\n"
    "\n"
    "Return two things.\n"
    "\n"
    "1. CATEGORY. Choose exactly one category from the list you are given. "
    "Choose on what went wrong, not on what kind of document is involved: a "
    "register that was never reviewed and a manual that was never reviewed are "
    "both overdue periodic reviews. If two categories both fit, choose the one "
    "describing the failure closest to the actual risk — access left active is "
    "access_not_revoked even when it was found during a recertification.\n"
    "\n"
    "2. SUGGESTED SEVERITY. Major, Minor or Observation. Major is a failure "
    "with realised or immediate exposure — access that was live, data that was "
    "reachable, a control that did not run at all on something critical. Minor "
    "is a real failure with the exposure contained or hypothetical. Observation "
    "is a weakness worth fixing where nothing was actually found wrong. Weigh "
    "what the unit does: the same lapse is more serious where personal data or "
    "payments are involved.\n"
    "\n"
    "Your severity is a SUGGESTION. A human auditor assigns the severity that "
    "counts and may disagree with you; say what you actually think rather than "
    "hedging towards the middle.\n"
    "\n"
    "Give a one-sentence rationale naming the words in the finding that decided "
    "the category. Do not restate the finding. Do not recommend actions.\n"
    "\n"
    "Return JSON only, matching the schema you are given."
)


def triage_schema_v1() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["category", "suggested_severity", "confidence", "rationale"],
        "properties": {
            "category": {"type": "string", "enum": list(GAP_CATEGORIES)},
            "suggested_severity": {"type": "string", "enum": list(SEVERITIES)},
            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "rationale": {"type": "string", "maxLength": 400},
        },
    }


def triage_user_v1(finding: dict[str, Any]) -> str:
    """The finding and its context. No leading question, no examples.

    Deliberately no worked examples: the corpus's own findings would be the
    obvious source for them, and a prompt carrying three of its own answers
    measures how well the model copies rather than how well it reads.
    """
    catalogue = "\n".join(
        f"- {name}: {CATEGORY_DEFINITIONS[name]}" for name in GAP_CATEGORIES
    )
    attributes = finding.get("attributes") or {}
    context = ", ".join(
        f"{key}={value}" for key, value in sorted(attributes.items())
    ) or "none recorded"
    return (
        f"CATEGORIES\n{catalogue}\n"
        f"\n"
        f"UNIT\n"
        f"name: {finding.get('unit', 'unknown')}\n"
        f"kind: {finding.get('unit_kind', 'unknown')}\n"
        f"attributes: {context}\n"
        f"\n"
        f"FINDING\n"
        f"raised by: {finding.get('raised_by', 'unknown')}\n"
        f"source: {finding.get('source', 'unknown')}\n"
        f"description:\n{finding.get('description', '')}\n"
    )
