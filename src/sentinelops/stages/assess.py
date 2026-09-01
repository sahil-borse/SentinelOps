"""S3 — assessment. The only stage that spends a token.

One model call per instance that survived S2, and never more than one unless the
first reply was unreadable. What goes into that call is not the document: it is
the chunks of the document that bear on the criteria, so a fifty-page pack costs
what its three relevant sections cost.

Three things make a verdict here defensible rather than merely plausible.

**Citations must resolve.** `cited_spans` are checked back against the source
character for character (whitespace normalised, nothing else). A span that does
not appear in the evidence means the model produced text the document does not
contain, and a verdict resting on invented quotation is worse than no verdict —
so the assessment fails to `insufficient_evidence` with `needs_human_review`
rather than being recorded.

**Evidence is untrusted.** It was written by the party who benefits from a pass.
It travels inside delimiters, labelled as data; the verdict is validated against
the enum whatever comes back; and an instruction found inside the evidence is
reported, not obeyed.

**Provenance travels with the verdict.** Criteria hash, prompt version and
evidence hash go onto every Finding, so any decision can be reproduced months
later — or shown to have been made against criteria that have since changed.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

from ..entities import CheckInstance, ControlDefinition, Evidence, Finding
from ..llm import TokenMeter, get_client
from ..llm.parsing import extract_json, validate
from ..llm.prompts.assessment import (
    ASSESSMENT_SYSTEM_V2,
    PROMPT_VERSION,
    assessment_schema_v2,
    assessment_user_v2,
)
from ..llm.protocol import LlmError, LlmRequest

#: Hard ceiling on a reply. A compliance verdict that needs more than this is a
#: verdict that has stopped answering the question.
MAX_TOKENS = 700

#: Below this the model is guessing, and a guess must be routed to a person
#: rather than recorded as a finding.
CONFIDENCE_FLOOR = 0.6

#: How much of a document one chunk may carry, and how many chunks may be sent.
CHUNK_CHARS = 600
RETRIEVE_LIMIT = 4

VERDICTS = ("compliant", "partial", "gap", "insufficient_evidence")

_WORD = re.compile(r"[a-z][a-z0-9-]{2,}")
_STOPWORDS = frozenset(
    """the and for are with that this from each every must has have was were
    within their they them there then than when where which who whom whose
    into out over under been being any all not but its his her our your
    control controls evidence period periods report reports""".split()
)


@dataclass(frozen=True)
class Chunk:
    index: int
    text: str


@dataclass
class AssessmentReport:
    as_of: date
    assessed: list[str] = field(default_factory=list)
    findings: list[str] = field(default_factory=list)
    citation_failures: list[str] = field(default_factory=list)
    parse_failures: list[str] = field(default_factory=list)
    flagged_for_review: list[str] = field(default_factory=list)
    model_calls: int = 0
    retries: int = 0
    chunks_sent: int = 0
    chunks_available: int = 0
    characters_sent: int = 0
    characters_available: int = 0

    @property
    def retrieval_ratio(self) -> float:
        """Share of the source text actually put in front of the model."""
        if not self.characters_available:
            return 0.0
        return self.characters_sent / self.characters_available


def chunk_document(content: str, max_chars: int = CHUNK_CHARS) -> list[Chunk]:
    """Split on blank lines, then pack paragraphs up to `max_chars`.

    Paragraph boundaries are where documents already divide themselves, so a
    chunk is a section a person would recognise rather than an arbitrary window.
    """
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", content) if p.strip()]
    chunks: list[Chunk] = []
    buffer = ""
    for paragraph in paragraphs:
        if buffer and len(buffer) + len(paragraph) + 2 > max_chars:
            chunks.append(Chunk(len(chunks), buffer))
            buffer = paragraph
        else:
            buffer = f"{buffer}\n\n{paragraph}" if buffer else paragraph
    if buffer:
        chunks.append(Chunk(len(chunks), buffer))
    return chunks


def _terms(text: str) -> set[str]:
    return {w for w in _WORD.findall(text.lower()) if w not in _STOPWORDS}


def retrieve(
    chunks: list[Chunk], criteria_text: str, limit: int = RETRIEVE_LIMIT
) -> list[Chunk]:
    """The chunks that bear on the criteria, in document order.

    Term overlap, deterministically scored and tie-broken by position — the same
    document and criteria select the same chunks every time, which is a
    precondition for two areas reaching the same verdict.

    A chunk that shares nothing with the criteria is dropped. If nothing matches
    at all, the opening chunks are sent rather than an empty prompt: the model
    should be able to say "this does not address the criteria", which it cannot
    do if it is shown nothing.
    """
    wanted = _terms(criteria_text)
    scored = [(len(wanted & _terms(c.text)), -c.index, c) for c in chunks]
    hits = [entry for entry in scored if entry[0] > 0]
    chosen = sorted(hits, reverse=True)[:limit] or [
        (0, -c.index, c) for c in chunks[:limit]
    ]
    return [entry[2] for entry in sorted(chosen, key=lambda e: e[2].index)]


def normalise(text: str) -> str:
    """Collapse whitespace for citation matching, and nothing else.

    A model that re-wraps a line has still quoted it; a model that changes a
    word has not. Only the former is forgiven.
    """
    return re.sub(r"\s+", " ", text).strip().lower()


def unresolved_citations(spans: list[str], content: str) -> list[str]:
    """Spans that do not actually appear in the evidence."""
    haystack = normalise(content)
    return [s for s in spans if s.strip() and normalise(s) not in haystack]


def criteria_hash(control: ControlDefinition) -> str:
    return hashlib.sha256(control.criteria_text.encode()).hexdigest()[:16]


def build_request(
    control: ControlDefinition, evidence: Evidence, limit: int = RETRIEVE_LIMIT
) -> tuple[LlmRequest, list[Chunk], list[Chunk]]:
    """The one call. Returns the request plus what was sent and what existed."""
    chunks = chunk_document(evidence.content)
    selected = retrieve(chunks, control.criteria_text, limit)
    request = LlmRequest(
        system=ASSESSMENT_SYSTEM_V2,
        messages=[
            {
                "role": "user",
                "content": assessment_user_v2(
                    control.title,
                    control.criteria_text,
                    [chunk.text for chunk in selected],
                ),
            }
        ],
        max_tokens=MAX_TOKENS,
        response_schema=assessment_schema_v2(),
        tier="assess",
    )
    return request, selected, chunks


def _ask(client, conn, request: LlmRequest, label: str) -> tuple[dict[str, Any], Any]:
    """One metered call, with the reply parsed and schema-checked."""
    with TokenMeter(conn, tier="assess", label=label) as meter:
        response = meter.record(client.complete(request))
    payload = response.parsed_json or extract_json(response.text)
    validate(payload, request.response_schema or {})
    if payload["verdict"] not in VERDICTS:
        raise LlmError(f"verdict {payload['verdict']!r} is outside the enum")
    return payload, response


def _finding(
    repo,
    instance: CheckInstance,
    control: ControlDefinition,
    evidence: Evidence,
    *,
    verdict: str,
    confidence: float,
    rationale: str,
    cited_spans: list[str],
    gaps: list[str],
    recommended_action: str,
    needs_human_review: bool,
    decided_by: str,
    as_of: date,
    model: str = "",
) -> Finding:
    sequence = len(repo["findings"].list(check_instance_id=instance.id)) + 1
    finding = Finding(
        id=f"FND-{instance.id.removeprefix('CHK-')}-{sequence}",
        check_instance_id=instance.id,
        verdict=verdict,
        confidence=confidence,
        rationale=rationale,
        cited_spans=cited_spans,
        gaps=gaps,
        recommended_action=recommended_action,
        needs_human_review=needs_human_review,
        assessed_at=datetime.combine(as_of, datetime.min.time()),
        decided_by=decided_by,
        criteria_hash=criteria_hash(control),
        prompt_version=PROMPT_VERSION,
        evidence_hash=evidence.content_hash,
    )
    repo["findings"].add(finding)
    instance.status = "assessed"
    repo["instances"].update(instance)
    repo["audit"].append(
        actor="ai",
        owner=instance.owner_name,
        action="finding_recorded",
        entity_type="Finding",
        entity_id=finding.id,
        detail={
            "check_instance_id": instance.id,
            "verdict": verdict,
            "confidence": confidence,
            "decided_by": decided_by,
            "model": model,
            "model_calls": 0 if decided_by.startswith("s3_") is False else 1,
            "needs_human_review": needs_human_review,
            "criteria_hash": finding.criteria_hash,
            "prompt_version": finding.prompt_version,
            "evidence_hash": finding.evidence_hash[:12],
        },
    )
    return finding


def assess_one(
    conn,
    repo,
    instance: CheckInstance,
    control: ControlDefinition,
    evidence: Evidence,
    *,
    client=None,
    as_of: date,
    report: AssessmentReport,
    limit: int = RETRIEVE_LIMIT,
) -> Finding:
    client = client or get_client()
    request, selected, chunks = build_request(control, evidence, limit)

    report.chunks_sent += len(selected)
    report.chunks_available += len(chunks)
    report.characters_sent += sum(len(c.text) for c in selected)
    report.characters_available += len(evidence.content)

    payload: dict[str, Any] | None = None
    response = None
    for attempt in (1, 2):
        try:
            report.model_calls += 1
            payload, response = _ask(client, conn, request, f"S3:{instance.id}")
            break
        except LlmError as exc:
            if attempt == 2:
                report.parse_failures.append(instance.id)
                report.flagged_for_review.append(instance.id)
                return _finding(
                    repo, instance, control, evidence,
                    verdict="insufficient_evidence",
                    confidence=0.0,
                    rationale=(
                        "The assessment could not be completed: the model's reply "
                        f"was unusable after a retry ({exc}). No verdict is being "
                        "asserted; this needs a person."
                    ),
                    cited_spans=[], gaps=[],
                    recommended_action="Assess this instance manually.",
                    needs_human_review=True,
                    decided_by="s3_unreadable_reply",
                    as_of=as_of,
                )
            report.retries += 1

    spans = [str(s) for s in payload["cited_spans"]]
    missing = unresolved_citations(spans, evidence.content)
    if missing or not spans:
        report.citation_failures.append(instance.id)
        report.flagged_for_review.append(instance.id)
        return _finding(
            repo, instance, control, evidence,
            verdict="insufficient_evidence",
            confidence=0.0,
            rationale=(
                "The assessment was rejected: "
                + (
                    "the model returned no citation at all."
                    if not spans
                    else "cited text does not appear in the evidence — "
                    + "; ".join(repr(m) for m in missing[:3])
                )
                + " An uncited or misquoted verdict is not recorded."
            ),
            cited_spans=[], gaps=[],
            recommended_action="Assess this instance manually.",
            needs_human_review=True,
            decided_by="s3_citation_unresolved",
            as_of=as_of,
        )

    confidence = float(payload["confidence"])
    needs_review = bool(payload["needs_human_review"]) or confidence < CONFIDENCE_FLOOR
    if needs_review:
        report.flagged_for_review.append(instance.id)

    return _finding(
        repo, instance, control, evidence,
        verdict=payload["verdict"],
        confidence=confidence,
        rationale=payload["rationale"],
        cited_spans=spans,
        gaps=[str(g) for g in payload["gaps"]],
        recommended_action=str(payload["recommended_action"]),
        needs_human_review=needs_review,
        decided_by="s3_model",
        as_of=as_of,
        model=getattr(response, "model", ""),
    )


def run(
    conn,
    instance_ids: list[str],
    as_of: date,
    *,
    client=None,
    limit: int = RETRIEVE_LIMIT,
) -> AssessmentReport:
    """Assess exactly the instances S2 could not decide. One call each."""
    from ..repositories import repositories

    repo = repositories(conn)
    controls = {c.id: c for c in repo["controls"].list()}
    client = client or get_client()
    report = AssessmentReport(as_of=as_of)

    for instance_id in instance_ids:
        instance = repo["instances"].get(instance_id)
        if instance is None or instance.status != "submitted":
            continue
        evidence = repo["evidence"].list(check_instance_id=instance_id)
        if not evidence:
            continue
        finding = assess_one(
            conn, repo, instance, controls[instance.control_id],
            sorted(evidence, key=lambda e: e.submitted_at)[0],
            client=client, as_of=as_of, report=report, limit=limit,
        )
        report.assessed.append(instance_id)
        report.findings.append(finding.id)

    repo["audit"].append(
        actor="system",
        owner="assessor",
        action="assessment_completed",
        entity_type="Cycle",
        entity_id=as_of.isoformat(),
        detail={
            "as_of": as_of.isoformat(),
            "assessed": len(report.assessed),
            "model_calls": report.model_calls,
            "retries": report.retries,
            "citation_failures": len(report.citation_failures),
            "parse_failures": len(report.parse_failures),
            "flagged_for_review": len(report.flagged_for_review),
            "retrieval_ratio": round(report.retrieval_ratio, 4),
            "prompt_version": PROMPT_VERSION,
        },
    )
    return report
