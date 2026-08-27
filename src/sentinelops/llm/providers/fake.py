"""Deterministic stand-in for a real model, so slices 1-5 need no API key.

Same request in, same response out — which also makes it a useful control when
measuring verdict consistency later.
"""

from __future__ import annotations

import hashlib
import json
import random

from ..parsing import extract_json, validate
from ..protocol import LlmRequest, LlmResponse

MODEL = "fake-assessor-v1"


def _digest(request: LlmRequest) -> str:
    body = request.system + json.dumps(request.messages, sort_keys=True)
    return hashlib.sha256(body.encode()).hexdigest()


def _canned(user_text: str) -> dict:
    """Pick a verdict from the evidence text. Keyword rules, not a model."""
    lowered = user_text.lower()
    quote = next(
        (line.strip() for line in user_text.splitlines() if line.startswith("[E")),
        "[E1] (no evidence excerpt)",
    )
    if "not performed" in lowered or "no review" in lowered:
        verdict, confidence = "gap", 0.88
    elif "partially" in lowered or "pending" in lowered:
        verdict, confidence = "partial", 0.62
    else:
        verdict, confidence = "compliant", 0.91
    return {
        "verdict": verdict,
        "confidence": confidence,
        "rationale": f"Deterministic fake assessor returned {verdict}.",
        "cited_spans": [quote[:200]],
        "gaps": [] if verdict == "compliant" else ["Criterion not evidenced in full."],
        "recommended_action": (
            "" if verdict == "compliant" else "Re-perform the review and resubmit."
        ),
        "needs_human_review": confidence < 0.7,
    }


class FakeModelClient:
    """Implements the LlmClient protocol."""

    def complete(self, request: LlmRequest) -> LlmResponse:
        user_text = "\n".join(m["content"] for m in request.messages)
        payload = _canned(user_text)
        if request.response_schema:
            payload = validate(payload, request.response_schema)
        text = json.dumps(payload)

        # Token counts are produced by the (fake) provider and read off the
        # response, exactly as the real client reads provider usage. They are
        # never derived from the caller's character counts.
        rng = random.Random(_digest(request))
        input_tokens = 400 + rng.randrange(0, 400)
        cached_tokens = len(request.system) // 4 if rng.random() > 0.3 else 0
        return LlmResponse(
            text=text,
            parsed_json=extract_json(text),
            input_tokens=input_tokens,
            output_tokens=90 + rng.randrange(0, 60),
            cached_tokens=cached_tokens,
            model=MODEL,
            latency_ms=120 + rng.randrange(0, 200),
            raw={"provider": "fake"},
        )
