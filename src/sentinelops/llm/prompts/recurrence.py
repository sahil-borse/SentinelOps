"""Use 2 of section 2: is this the same gap we found somewhere else?

**What "recurring" means here** is fixed by the stakeholder, not by us: *the same
type of gap occurring again in a different area, project, or period.* Three
constraints fall straight out of that sentence, and all three are enforced in
code rather than asked of the model:

* different unit **or** different period — the same finding is not a recurrence
  of itself, and a control failing twice running in one team is a persistent
  problem rather than a recurring one;
* the prior finding must be *prior* — recurrence points backwards, and a
  suggestion that a March finding recurs from a September one is nonsense;
* the pair must share a gap category, which is what makes the candidate set
  small enough to put in one call.

**What is left for the model** is the only part a rule cannot do: deciding
whether two descriptions written months apart by different auditors, sharing no
vocabulary, describe the same underlying failure. "Three leavers still held
privileged access to the settlement console" and "contractors whose engagements
ended retained active accounts and VPN access" are the same gap. A keyword rule
sees almost nothing in common; the shared category narrows it to plausible, and
the judgement is genuinely semantic.

This is the use that most needs the eighteen-month corpus. Over a single quarter
there is nothing to find, and the claim in the pitch — that no human holds this
comparison across eighteen months, six functions and several project teams — is
only worth making because the window is long enough for a person to have
forgotten.

**One call per finding, over pre-filtered candidates.** Not one per pair. The
deterministic filter does the elimination; the model reads a shortlist.

**Advisory, with ids.** Section 2: surfaced as a suggestion with prior finding
ids. Nothing here changes a status, and every id returned is checked against the
shortlist that was actually sent — a recurrence pointing at a finding that was
never a candidate is dropped rather than shown.
"""

from __future__ import annotations

from typing import Any

#: Travels onto every recurrence link this prompt proposes.
PROMPT_VERSION = "recurrence_v1"

#: A shortlist longer than this is a sign the category filter is too coarse, and
#: it is also more than a reader would act on. Oldest-first is deliberate: the
#: first occurrence is the one a reader most wants to be pointed at.
MAX_CANDIDATES = 12

RECURRENCE_SYSTEM_V1 = (
    "You decide whether a compliance finding is a recurrence of an earlier "
    "one.\n"
    "\n"
    "You are given one finding and a shortlist of earlier findings from other "
    "units or other periods that share its gap category. Decide which of the "
    "earlier ones — if any — describe the SAME underlying failure.\n"
    "\n"
    "The same failure means the same thing went wrong, not that the same words "
    "were used and not that the same control was involved. Access left with "
    "people who had left, whether they were employees, contractors or a "
    "third-party integration, is one failure described three ways. A review "
    "that was skipped and a review that was performed but not evidenced are "
    "two different failures even though both concern the same review.\n"
    "\n"
    "Be strict. A false recurrence sends somebody to read an unrelated finding "
    "and teaches them to ignore the signal. Returning nothing is the right "
    "answer whenever the shortlist holds nothing that genuinely matches; most "
    "findings are not recurrences.\n"
    "\n"
    "Only use ids from the shortlist. Never invent one. For each match give a "
    "one-sentence reason naming what the two have in common — the shared "
    "failure, not the shared category.\n"
    "\n"
    "Return JSON only, matching the schema you are given."
)


def recurrence_schema_v1() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["recurrences"],
        "properties": {
            "recurrences": {
                "type": "array",
                "maxItems": MAX_CANDIDATES,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["finding_id", "confidence", "reason"],
                    "properties": {
                        "finding_id": {"type": "string"},
                        "confidence": {
                            "type": "number", "minimum": 0, "maximum": 1,
                        },
                        "reason": {"type": "string", "maxLength": 300},
                    },
                },
            },
        },
    }


def _candidate_line(candidate: dict[str, Any]) -> str:
    return (
        f"- {candidate['id']} | {candidate['unit']} | raised "
        f"{candidate['raised_at']} | {candidate['severity']}\n"
        f"  {candidate['description']}"
    )


def recurrence_user_v1(
    finding: dict[str, Any], candidates: list[dict[str, Any]]
) -> str:
    if not candidates:
        return (
            "FINDING\n"
            f"{finding['id']} | {finding['unit']} | raised {finding['raised_at']}\n"
            f"{finding['description']}\n"
            "\nEARLIER FINDINGS\n(none)\n"
        )
    shortlist = "\n".join(_candidate_line(c) for c in candidates)
    return (
        f"FINDING\n"
        f"{finding['id']} | {finding['unit']} | raised {finding['raised_at']} | "
        f"category {finding['category']}\n"
        f"{finding['description']}\n"
        f"\n"
        f"EARLIER FINDINGS (same category, different unit or period)\n"
        f"{shortlist}\n"
    )
