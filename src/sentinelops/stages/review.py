"""Use 3 of section 2: assess one evidence round, and recommend nothing more.

`assess.py` judges a periodic check's evidence against a control's criteria.
This judges remediation: the owner says the gap the auditor described is fixed,
and the question is whether what they filed shows the *agreed action plan*
actually carried out.

**It recommends. The auditor decides.** Section 2 use 3 and section 7 both say
so, and they say it about different things — section 2 about who may conclude,
section 7 about who may act. Nothing in this module writes `auditor_response`,
moves a finding's status, or closes anything. It files a recommendation beside
the round; `rounds.respond` is still the only way a round is answered, and it
still requires a `pa_infosec` identity who did not file the evidence.

**Citations must resolve.** Every span comes back checked against the submitted
evidence character for character, whitespace normalised and nothing else. A span
that is not there means the model produced text the document does not contain,
and a recommendation resting on invented quotation is worse than none — so the
assessment is recorded as `insufficient_evidence` with `needs_human_review`,
carrying what was claimed and could not be found.

**Evidence is untrusted, and here more than anywhere.** It was written by the
party who benefits from acceptance, in answer to a specific accusation, by
someone who knows what the assessor is looking for.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import date, datetime, time
from typing import Any

from ..entities import Assessment, EvidenceSubmission, Finding
from ..llm import TokenMeter, get_client
from ..llm.parsing import extract_json, validate
from ..llm.prompts.review import (
    MAX_TOKENS,
    PROMPT_VERSION,
    REVIEW_SYSTEM_V1,
    VERDICTS,
    review_schema_v1,
    review_user_v1,
)
from ..llm.protocol import LlmError, LlmRequest

#: Below this the model is guessing, and a guess is routed to a person rather
#: than shown to an auditor as a recommendation. Same floor as S3.
CONFIDENCE_FLOOR = 0.6

#: What each verdict would mean if an auditor agreed with it. Advisory mapping,
#: used only to phrase the recommendation — nothing reads it to decide anything.
SUGGESTS: dict[str, str] = {
    "satisfies": "accepted",
    "partially_satisfies": "insufficient",
    "does_not_satisfy": "insufficient",
    "insufficient_evidence": "insufficient",
}


@dataclass
class ReviewReport:
    as_of: date
    assessed: list[str] = field(default_factory=list)
    needs_review: list[str] = field(default_factory=list)
    model_calls: int = 0
    citation_failures: list[str] = field(default_factory=list)
    by_verdict: dict[str, int] = field(default_factory=dict)

    def summary(self) -> str:
        spread = ", ".join(
            f"{n} {v}" for v, n in sorted(self.by_verdict.items())
        ) or "none"
        return (
            f"{len(self.assessed)} round(s) assessed / {self.model_calls} model "
            f"call(s): {spread}; {len(self.needs_review)} for human review"
        )


def normalise(text: str) -> str:
    """Whitespace folded, nothing else. Case and punctuation are the quotation."""
    return " ".join(text.split())


def unresolved_citations(spans: list[str], evidence: str) -> list[str]:
    """Spans that do not appear in the evidence. Empty is the passing case."""
    haystack = normalise(evidence)
    return [
        span for span in spans
        if span.strip() and normalise(span) not in haystack
    ]


def evidence_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _prior_remarks(rounds: list[EvidenceSubmission], number: int) -> str:
    """What the auditor said about the round before this one.

    Round three answers round two's objection. Assessing it without that reads
    the same evidence as though nothing in particular had been asked for.
    """
    for submission in reversed(rounds):
        if submission.round_number < number and submission.auditor_remarks:
            return submission.auditor_remarks
    return ""


def _ask(conn, client, request: LlmRequest, label: str):
    with TokenMeter(conn, tier="assess", label=f"REVIEW:{label}") as meter:
        response = meter.record(client.complete(request))
    payload = response.parsed_json or extract_json(response.text)
    if payload is None:
        raise LlmError(f"review of {label} returned no readable JSON")
    payload = validate(payload, request.response_schema)

    # Validated against the enum whatever came back. A defence that relies on
    # the model having behaved is not a defence.
    if payload.get("verdict") not in VERDICTS:
        raise LlmError(
            f"verdict {payload.get('verdict')!r} is outside the enum"
        )
    return payload, response


def evaluate(
    conn,
    submission_id: str,
    *,
    client=None,
    as_of: date,
) -> Assessment:
    """Assess one round and file the recommendation. Changes no state but its own.

    Raises rather than guessing if the round carries no evidence text: a
    recommendation about a filename is not a recommendation, and a citation
    cannot be checked against one.
    """
    from ..repositories import repositories, simulated_clock

    repo = repositories(conn)
    submission = repo["rounds"].get(submission_id)
    if submission is None:
        raise ValueError(f"no such evidence round: {submission_id}")
    finding = repo["findings"].get(submission.finding_id)
    if finding is None:
        raise ValueError(f"round {submission_id} points at no finding")
    if not submission.evidence_text.strip():
        raise ValueError(
            f"{submission_id} carries no evidence text, only the reference "
            f"{submission.evidence_ref!r}. There is nothing to read and no way "
            f"to check a citation against it"
        )

    rounds = sorted(
        repo["rounds"].list(finding_id=finding.id),
        key=lambda r: r.round_number,
    )
    request = LlmRequest(
        system=REVIEW_SYSTEM_V1,
        messages=[{
            "role": "user",
            "content": review_user_v1(
                finding_description=finding.description,
                agreed_action_plan=finding.agreed_action_plan,
                round_number=submission.round_number,
                prior_remarks=_prior_remarks(rounds, submission.round_number),
                owner_note=submission.owner_note,
                evidence=submission.evidence_text,
            ),
        }],
        max_tokens=MAX_TOKENS,
        response_schema=review_schema_v1(),
        tier="assess",
    )
    payload, response = _ask(
        conn, client or get_client(), request, submission_id
    )

    spans = [str(s) for s in payload.get("cited_spans", [])]
    unresolved = unresolved_citations(spans, submission.evidence_text)
    verdict = payload["verdict"]
    confidence = float(payload.get("confidence", 0.0))
    rationale = payload.get("rationale", "")
    gaps = [str(g) for g in payload.get("gaps", [])]
    needs_review = bool(payload.get("needs_human_review")) or confidence < CONFIDENCE_FLOOR

    if unresolved:
        # The model quoted something the evidence does not contain. Whatever it
        # concluded rested partly on text that is not there, so the conclusion
        # goes rather than being repaired: an auditor shown a tidied-up version
        # of a fabricated verdict is worse off than one shown nothing.
        verdict = "insufficient_evidence"
        needs_review = True
        gaps = gaps + [
            f"citation did not resolve against the submitted evidence: "
            f"{span[:120]!r}"
            for span in unresolved
        ]
        rationale = (
            f"Discarded: {len(unresolved)} of {len(spans)} cited span(s) do not "
            f"appear in the submitted evidence. Original rationale: {rationale}"
        )
        spans = [span for span in spans if span not in unresolved]

    stamp = datetime.combine(as_of, time(11, 0))
    assessment = Assessment(
        id=f"ASM-{submission_id.removeprefix('SUB-')}",
        submission_id=submission_id,
        verdict=verdict,
        confidence=confidence,
        rationale=rationale,
        cited_spans=spans,
        gaps=gaps,
        recommended_action="",
        needs_human_review=needs_review,
        assessed_at=stamp,
        decided_by="review_model",
        criteria_hash=evidence_hash(
            finding.description + "\n" + finding.agreed_action_plan
        ),
        prompt_version=PROMPT_VERSION,
        evidence_hash=evidence_hash(submission.evidence_text),
    )

    with simulated_clock(stamp):
        repo["assessments"].add(assessment)
        repo["audit"].append(
            actor="ai", owner=finding.owner_identity,
            action="evidence_round_assessed",
            entity_type="EvidenceSubmission", entity_id=submission_id,
            detail={
                "finding_id": finding.id,
                "round_number": submission.round_number,
                "verdict": verdict,
                "confidence": confidence,
                "cited_spans": len(spans),
                "unresolved_citations": len(unresolved),
                "gaps": gaps,
                "needs_human_review": needs_review,
                "would_suggest": SUGGESTS.get(verdict, "insufficient"),
                "prompt_version": PROMPT_VERSION,
                "model": response.model,
                "note": (
                    "recommendation only; the auditor answers the round and "
                    "decides closure"
                ),
            },
        )
    return assessment


def recommendation_for(conn, submission_id: str) -> Assessment | None:
    """What the model said about this round, if it was asked."""
    from ..repositories import repositories

    rows = repositories(conn)["assessments"].list(submission_id=submission_id)
    return rows[0] if rows else None


def run(conn, as_of: date, *, client=None, limit: int | None = None) -> ReviewReport:
    """Assess every unanswered round that has evidence and no recommendation yet.

    Only open rounds. A round the auditor has already answered does not need
    advice, and paying to advise on a settled question is the kind of spending
    nobody notices until the bill arrives.
    """
    from ..repositories import repositories

    repo = repositories(conn)
    report = ReviewReport(as_of=as_of)
    pending = [
        submission for submission in sorted(
            repo["rounds"].list(), key=lambda r: r.id
        )
        if submission.is_open
        and submission.evidence_text.strip()
        and recommendation_for(conn, submission.id) is None
    ]
    if limit is not None:
        pending = pending[:limit]

    model_client = client or get_client()
    for submission in pending:
        assessment = evaluate(
            conn, submission.id, client=model_client, as_of=as_of
        )
        report.model_calls += 1
        report.assessed.append(submission.id)
        report.by_verdict[assessment.verdict] = (
            report.by_verdict.get(assessment.verdict, 0) + 1
        )
        if assessment.needs_human_review:
            report.needs_review.append(submission.id)
        if any("citation did not resolve" in gap for gap in assessment.gaps):
            report.citation_failures.append(submission.id)
    return report
