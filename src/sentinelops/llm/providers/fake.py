"""Deterministic stand-in for a real model, so the suite runs with no key.

Same request in, same response out — which also makes it a useful control when
measuring verdict consistency: any divergence between two areas is then the
pipeline's doing, not sampling noise.

It quotes real text. Citations are verified against the source in S3, so a stub
that invented a quotation would fail every assessment and prove nothing; this
one pulls an actual line out of the evidence it was shown.

It also models a *well-behaved* assessor: shown a document that instructs it to
return a pass, it refuses and flags for review. That simulates the behaviour the
system prompt asks for — it does not demonstrate that a real model resists. Only
the real provider can show that. What the tests around it do demonstrate is that
the pipeline holds even when the model misbehaves, which is the part that is
actually under our control.
"""

from __future__ import annotations

import hashlib
import json
import random
import re

from ..parsing import extract_json, validate
from ..prompts.assessment import EVIDENCE_CLOSE, EVIDENCE_OPEN
from ..protocol import LlmRequest, LlmResponse

MODEL = "fake-assessor-v1"

#: Phrasing that only appears when a document is talking to the assessor rather
#: than describing the control.
_INJECTION = re.compile(
    r"(ignore (the|all|previous)|disregard|you must (mark|return|set)|"
    r"mark this control|pre-?approved|do not report|override|"
    r"system\s*:|instruction to the (assessor|reviewer|model)|"
    r"return\s+\"?compliant)",
    re.IGNORECASE,
)

#: Negations that describe a *good* outcome. "No accounts were dormant" is a
#: pass; "no review was performed" is not. Stripped before looking for failure.
_BENIGN_NEGATION = re.compile(
    r"(no longer required|no discrepancies|no gaps|without incident)",
    re.IGNORECASE,
)

#: A clause that says something did not happen.
_NEGATED = re.compile(r"\b(no|not|never|neither|nor|none)\b", re.IGNORECASE)

#: A clause that says something happened, but not fully.
_HEDGED = re.compile(
    r"(pending|partially|a sample of|awaits?|awaiting|incomplete|unsigned|"
    r"outstanding|queued for|slightly outside|left blank|scheduled for|"
    r"only the|past the|the rest|the remainder|of them|remain open)",
    re.IGNORECASE,
)

_NUMBERED = re.compile(r"^\s*\d+\.\s", re.MULTILINE)


def _digest(request: LlmRequest) -> str:
    body = request.system + json.dumps(request.messages, sort_keys=True)
    return hashlib.sha256(body.encode()).hexdigest()


def _evidence_text(user_text: str) -> str:
    """What the prompt actually put in front of the model.

    Everything between the untrusted-evidence markers, with the [E1] labels
    stripped, so a quotation taken from here resolves against the source.
    """
    if EVIDENCE_OPEN in user_text and EVIDENCE_CLOSE in user_text:
        body = user_text.split(EVIDENCE_OPEN, 1)[1].split(EVIDENCE_CLOSE, 1)[0]
    else:  # the v1 prompt, still used by the slice-1 skeleton
        body = user_text.split("EVIDENCE EXCERPTS:", 1)[-1]
    return "\n".join(
        re.sub(r"^\[E\d+\]\s*", "", line) for line in body.strip().splitlines()
    )


def _quotable_lines(evidence: str) -> list[str]:
    return [
        line.strip()
        for line in evidence.splitlines()
        if len(line.strip()) > 25 and not line.strip().startswith("{")
    ]


def _clause_lines(evidence: str) -> list[str]:
    """The numbered criteria responses, which is where the verdict lives."""
    return [
        line.strip()
        for line in evidence.splitlines()
        if _NUMBERED.match(line)
    ]


def _canned(evidence: str) -> dict:
    """Pick a verdict clause by clause. Heuristics, not a model.

    A clause that says something did not happen is a failure; one that hedges is
    partial; otherwise it passes. This is a stub standing in for judgement, and
    it is wrong on documents whose failures are phrased without a negation —
    `tests/test_fake_accuracy.py` measures exactly how often, so nobody mistakes
    its verdicts for the real assessor's.
    """
    lines = _quotable_lines(evidence) or [evidence.strip()[:160]]
    clauses = _clause_lines(evidence)

    injected = _INJECTION.search(evidence)
    failing = next(
        (c for c in clauses if _NEGATED.search(_BENIGN_NEGATION.sub("", c))), None
    )
    hedging = next((c for c in clauses if _HEDGED.search(c)), None)

    def _line_for(text) -> str:
        if text is None:
            return lines[0]
        if isinstance(text, str):
            return next((ln for ln in lines if ln in text or text in ln), text)
        return next(
            (ln for ln in lines if text.group(0).lower() in ln.lower()), lines[0]
        )

    if injected is not None:
        return {
            "verdict": "gap",
            "confidence": 0.55,
            "rationale": (
                "The submission contains text addressed to the assessor rather "
                "than describing the control, which is treated as evidence of an "
                "irregular submission and not acted on. Assessed on its "
                "substantive content, the criteria are not fully met."
            ),
            "cited_spans": [_line_for(injected)],
            "gaps": ["The submission attempts to direct the assessment."],
            "recommended_action": "Review this submission with the owning team.",
            "needs_human_review": True,
        }

    if failing is not None:
        return {
            "verdict": "gap",
            "confidence": 0.88,
            "rationale": "A criterion is contradicted by the evidence.",
            "cited_spans": [_line_for(failing)],
            "gaps": ["A required clause is not satisfied."],
            "recommended_action": "Perform the control and resubmit.",
            "needs_human_review": False,
        }

    if hedging is not None:
        return {
            "verdict": "partial",
            "confidence": 0.62,
            "rationale": "A criterion is only partially evidenced.",
            "cited_spans": [_line_for(hedging)],
            "gaps": ["A clause is addressed but not completed."],
            "recommended_action": "Complete the outstanding work and resubmit.",
            "needs_human_review": False,
        }

    return {
        "verdict": "compliant",
        "confidence": 0.91,
        "rationale": "Every criterion is addressed by the evidence.",
        "cited_spans": [lines[0]],
        "gaps": [],
        "recommended_action": "",
        "needs_human_review": False,
    }


class FakeModelClient:
    """Implements the LlmClient protocol."""

    def complete(self, request: LlmRequest) -> LlmResponse:
        user_text = "\n".join(m["content"] for m in request.messages)
        payload = _canned(_evidence_text(user_text))
        if request.response_schema:
            payload = validate(payload, request.response_schema)
        text = json.dumps(payload)

        # Counts are produced by the (fake) provider and read off the response,
        # exactly as the real client reads provider usage — the meter never
        # estimates. What this stub reports is proportional to the prompt it was
        # actually handed, because that is what a tokenizer does: a provider
        # returning a number unrelated to its input would make any comparison
        # between a full document and a retrieved extract meaningless.
        prompt = request.system + "".join(m["content"] for m in request.messages)
        rng = random.Random(_digest(request))
        return LlmResponse(
            text=text,
            parsed_json=extract_json(text),
            input_tokens=max(1, len(prompt) // 4),
            output_tokens=max(1, len(text) // 4),
            # the constant system prefix is the part a provider cache can serve
            cached_tokens=len(request.system) // 4 if rng.random() > 0.3 else 0,
            model=MODEL,
            latency_ms=120 + rng.randrange(0, 200),
            raw={"provider": "fake"},
        )
