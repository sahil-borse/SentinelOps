"""S3 assessment prompt, version 1.

The system prompt is a module constant with no interpolation of any kind. It is
sent first and byte-identical on every call, so the provider cache can hit and
so the same evidence judged against the same criteria yields the same verdict
whichever process area it belongs to. Changing it means adding a _V2, not
editing this string.
"""

from __future__ import annotations

from typing import Any

ASSESSMENT_SYSTEM_V1 = (
    "You are a compliance assessor. You are given the text of a control's "
    "criteria and excerpts of evidence submitted against it. Judge only what "
    "the excerpts actually say.\n"
    "Rules:\n"
    "1. Every verdict must be supported by cited_spans quoted verbatim from the "
    "evidence. A verdict with no citation is invalid.\n"
    "2. If the evidence does not address a criterion, that criterion is a gap. "
    "Do not infer compliance from silence.\n"
    "3. If you are not confident, set needs_human_review true and lower "
    "confidence rather than asserting a verdict.\n"
    "4. Reply with JSON only, matching the requested schema exactly."
)


def assessment_user_v1(
    control_title: str, criteria_text: str, evidence_excerpts: list[str]
) -> str:
    """The variable half of the prompt. Kept strictly after the system prefix."""
    excerpts = "\n\n".join(f"[E{i}] {e}" for i, e in enumerate(evidence_excerpts, 1))
    return (
        f"CONTROL: {control_title}\n"
        f"CRITERIA:\n{criteria_text}\n\n"
        f"EVIDENCE EXCERPTS:\n{excerpts}"
    )


def assessment_schema_v1() -> dict[str, Any]:
    return {
        "type": "object",
        "required": [
            "verdict",
            "confidence",
            "rationale",
            "cited_spans",
            "gaps",
            "recommended_action",
            "needs_human_review",
        ],
        "properties": {
            "verdict": {
                "enum": ["compliant", "partial", "gap", "insufficient_evidence"]
            },
            "confidence": {"type": "number"},
            "rationale": {"type": "string"},
            "cited_spans": {"type": "array", "items": {"type": "string"}},
            "gaps": {"type": "array", "items": {"type": "string"}},
            "recommended_action": {"type": "string"},
            "needs_human_review": {"type": "boolean"},
        },
    }
