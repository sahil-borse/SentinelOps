"""Section 2's remaining model uses: classify, detect recurrence, brief.

Three uses in one module because they share a shape — they read *findings*
rather than evidence, they are all advisory, and none of them may change a
status. S3 (`assess.py`) reads documents and its output drives the lifecycle;
nothing here does. Keeping them apart from S3 keeps that distinction visible in
the file listing, which matters when the claim being made is "the model never
decides anything".

    classify    one call per finding, no taxonomy exists so a rule cannot do it
    recurrence  one call per finding, over a deterministically filtered shortlist
    brief       one call per cycle, over ranked findings and metrics

**What is deterministic here, and it is most of it.** Which findings need
classifying. Which earlier findings are even eligible to be a recurrence — a
different unit or period, raised earlier, sharing a category. The ranking the
brief reads. The ageing buckets. The model is asked exactly three questions it
is uniquely able to answer, and every answer is validated against something the
code already knows before it is written down.

**Everything is overridable and nothing is silent.** A category the auditor
disagrees with can be replaced, and the override is recorded next to the
suggestion. A recurrence link is a pointer, not a merge. The brief changes no
state at all.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime, time
from typing import Any

from .. import authority, directory
from ..directory import Directory
from ..entities import Finding
from ..llm import TokenMeter, get_client
from ..llm.prompts.brief import (
    BRIEF_SYSTEM_V1,
    MAX_TOKENS as BRIEF_MAX_TOKENS,
    TOP_N,
    brief_schema_v1,
    brief_user_v1,
)
from ..llm.prompts.brief import PROMPT_VERSION as BRIEF_PROMPT_VERSION
from ..llm.prompts.recurrence import (
    MAX_CANDIDATES,
    RECURRENCE_SYSTEM_V1,
    recurrence_schema_v1,
    recurrence_user_v1,
)
from ..llm.prompts.recurrence import PROMPT_VERSION as RECURRENCE_PROMPT_VERSION
from ..llm.prompts.triage import (
    GAP_CATEGORIES,
    SEVERITIES,
    TRIAGE_SYSTEM_V1,
    triage_schema_v1,
    triage_user_v1,
)
from ..llm.prompts.triage import PROMPT_VERSION as TRIAGE_PROMPT_VERSION
from ..llm.protocol import LlmRequest

#: Short answers. A classification that needs four hundred tokens to explain
#: itself is not a classification.
TRIAGE_MAX_TOKENS = 260
RECURRENCE_MAX_TOKENS = 500

#: Below this the suggestion is recorded but marked for a human to look at, the
#: same threshold discipline S3 uses on its verdicts.
CONFIDENCE_FLOOR = 0.6

#: `[FND-1]` or `[FND-1, FND-2]`.
CITATION = re.compile(r"\[([A-Z0-9\-]+(?:\s*,\s*[A-Z0-9\-]+)*)\]")

#: Ageing buckets, section 8's exactly.
AGEING_BUCKETS: tuple[tuple[str, int, int], ...] = (
    ("0-30", 0, 30),
    ("31-60", 31, 60),
    ("61-90", 61, 90),
    ("90+", 91, 10_000),
)


@dataclass
class TriageReport:
    as_of: date
    classified: list[str] = field(default_factory=list)
    needs_review: list[str] = field(default_factory=list)
    model_calls: int = 0
    by_category: dict[str, int] = field(default_factory=dict)


@dataclass
class RecurrenceReport:
    as_of: date
    examined: list[str] = field(default_factory=list)
    linked: list[tuple[str, str]] = field(default_factory=list)
    model_calls: int = 0
    skipped_no_candidates: int = 0


@dataclass
class Brief:
    as_of: date
    text: str = ""
    cited: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    ranked: list[dict[str, Any]] = field(default_factory=list)
    model_calls: int = 0
    prompt_version: str = BRIEF_PROMPT_VERSION
    model: str = ""


# --- use 1 and 4: classify the gap, suggest a severity ----------------------

def _finding_context(repo, people: Directory, finding: Finding) -> dict[str, Any]:
    unit = repo["units"].get(finding.auditable_unit_id)
    return {
        "id": finding.id,
        "unit": unit.name if unit else finding.auditable_unit_id,
        "unit_kind": unit.kind if unit else "unknown",
        "attributes": dict(unit.attributes) if unit else {},
        "description": finding.description,
        "raised_by": people.name(finding.raised_by),
        "source": finding.source,
    }


def classify(conn, as_of: date, *, client=None, limit: int | None = None):
    """Give every unclassified finding a gap category and a severity suggestion.

    Runs only on findings that have no category yet, so it is idempotent and a
    second pass over the same corpus spends nothing.
    """
    from ..repositories import repositories, simulated_clock

    repo = repositories(conn)
    people = directory.load(conn)
    report = TriageReport(as_of=as_of)
    pending = [f for f in sorted(repo["findings"].list(), key=lambda f: f.id)
               if not f.gap_category]
    if limit is not None:
        pending = pending[:limit]

    model_client = client or get_client()
    with simulated_clock(datetime.combine(as_of, time(7, 0))):
        for finding in pending:
            payload, response = _ask_triage(
                conn, model_client, _finding_context(repo, people, finding)
            )
            report.model_calls += 1
            _record_triage(repo, people, finding, payload, response, report)
    return report


def _ask_triage(conn, client, context: dict[str, Any]):
    request = LlmRequest(
        system=TRIAGE_SYSTEM_V1,
        messages=[{"role": "user", "content": triage_user_v1(context)}],
        response_schema=triage_schema_v1(),
        max_tokens=TRIAGE_MAX_TOKENS,
        tier="triage",
    )
    with TokenMeter(conn, tier="triage", label=f"TRIAGE:{context['id']}") as meter:
        response = meter.record(client.complete(request))
    payload = response.parsed_json or {}

    # Validated against the enum whatever came back — a defence that relies on
    # the model having behaved is not a defence.
    if payload.get("category") not in GAP_CATEGORIES:
        raise ValueError(
            f"category {payload.get('category')!r} is outside the taxonomy"
        )
    if payload.get("suggested_severity") not in SEVERITIES:
        raise ValueError(
            f"severity {payload.get('suggested_severity')!r} is outside the enum"
        )
    return payload, response


def _record_triage(repo, people, finding: Finding, payload, response, report):
    confidence = float(payload.get("confidence", 0.0))
    finding.gap_category = payload["category"]
    # The severity *suggestion* only. An audit-raised finding already carries
    # the severity its auditor assigned, and this must not touch it — section 2
    # is explicit that the model advises and the auditor decides.
    finding.suggested_severity = payload["suggested_severity"]
    repo["findings"].update(finding)

    report.classified.append(finding.id)
    report.by_category[finding.gap_category] = (
        report.by_category.get(finding.gap_category, 0) + 1
    )
    low = confidence < CONFIDENCE_FLOOR
    if low:
        report.needs_review.append(finding.id)

    repo["audit"].append(
        actor="ai", owner=people.name(finding.owner_identity),
        action="finding_classified", entity_type="Finding", entity_id=finding.id,
        detail={
            "gap_category": finding.gap_category,
            "suggested_severity": finding.suggested_severity,
            "assigned_severity": finding.severity,
            "agrees_with_auditor": (
                finding.severity is None
                or finding.severity == finding.suggested_severity
            ),
            "confidence": confidence,
            "needs_human_review": low,
            "rationale": payload.get("rationale", ""),
            "prompt_version": TRIAGE_PROMPT_VERSION,
            "model": response.model,
            "note": "advisory; the auditor may override the category",
        },
    )


def override_category(conn, finding_id: str, category: str, *, by: str) -> Finding:
    """The auditor disagrees. Section 2, use 1, in as many words.

    The previous value goes on the trail rather than being overwritten quietly,
    because "how often does the classifier get overridden?" is the question that
    tells you whether to keep it.
    """
    from ..repositories import repositories

    repo = repositories(conn)
    people = directory.load(conn)
    identity = people.get(by)
    authority.require(identity.role if identity else None, "assign_severity",
                      actor_id=by)
    if category not in GAP_CATEGORIES:
        raise ValueError(f"{category!r} is not in the taxonomy")

    finding = repo["findings"].get(finding_id)
    if finding is None:
        raise ValueError(f"no such finding: {finding_id}")
    was = finding.gap_category
    finding.gap_category = category
    repo["findings"].update(finding)
    repo["audit"].append(
        actor="user", owner=people.name(by), action="finding_category_overridden",
        entity_type="Finding", entity_id=finding.id,
        detail={"category": category, "previous": was, "overridden_by": by},
        actor_identity=by,
    )
    return finding


# --- use 2: recurrence ------------------------------------------------------

def candidates_for(repo, finding: Finding) -> list[Finding]:
    """Earlier findings that could be a recurrence of this one. Deterministic.

    The stakeholder's definition, enforced rather than requested: same gap type,
    **different area, project or period**, and earlier. Nothing semantic happens
    here — that is the next function's job, and keeping the two apart is what
    makes the model's contribution measurable.
    """
    if not finding.gap_category:
        return []
    same_period = _period_of(finding)
    out = []
    for other in repo["findings"].list():
        if other.id == finding.id or other.gap_category != finding.gap_category:
            continue
        if other.raised_at >= finding.raised_at:
            continue  # recurrence points backwards
        different_unit = other.auditable_unit_id != finding.auditable_unit_id
        different_period = _period_of(other) != same_period
        if not (different_unit or different_period):
            continue
        out.append(other)
    out.sort(key=lambda f: f.raised_at)
    return out[:MAX_CANDIDATES]


def _period_of(finding: Finding) -> str:
    """The period a finding belongs to, for "different period" purposes.

    The month it was raised in. Not the check instance's period: an audit
    finding has no check instance, and the stakeholder's "different period" is
    about when the problem showed up, not which reporting window it maps to.
    """
    return f"{finding.raised_at.year}-{finding.raised_at.month:02d}"


def detect_recurrence(
    conn, as_of: date, *, client=None, limit: int | None = None
) -> RecurrenceReport:
    """One call per finding that has candidates. None at all for the rest."""
    from ..repositories import repositories, simulated_clock

    repo = repositories(conn)
    people = directory.load(conn)
    report = RecurrenceReport(as_of=as_of)
    findings = [
        f for f in sorted(repo["findings"].list(), key=lambda f: f.raised_at)
        if f.gap_category and not f.recurrence_of
    ]
    if limit is not None:
        findings = findings[:limit]

    model_client = client or get_client()
    units = {u.id: u for u in repo["units"].list()}
    with simulated_clock(datetime.combine(as_of, time(7, 30))):
        for finding in findings:
            candidates = candidates_for(repo, finding)
            report.examined.append(finding.id)
            if not candidates:
                # No call at all. Most findings are the first of their kind.
                report.skipped_no_candidates += 1
                continue
            matches, response = _ask_recurrence(
                conn, model_client, finding, candidates, units
            )
            report.model_calls += 1
            _record_recurrence(
                repo, people, finding, matches, candidates, response, report
            )
    return report


def _ask_recurrence(conn, client, finding: Finding, candidates, units):
    def row(f: Finding) -> dict[str, Any]:
        unit = units.get(f.auditable_unit_id)
        return {
            "id": f.id,
            "unit": unit.name if unit else f.auditable_unit_id,
            "raised_at": f.raised_at.date().isoformat(),
            "severity": f.severity or f.suggested_severity or "unassigned",
            "description": f.description,
            "category": f.gap_category,
        }

    request = LlmRequest(
        system=RECURRENCE_SYSTEM_V1,
        messages=[{
            "role": "user",
            "content": recurrence_user_v1(
                row(finding), [row(c) for c in candidates]
            ),
        }],
        response_schema=recurrence_schema_v1(),
        max_tokens=RECURRENCE_MAX_TOKENS,
        tier="recurrence",
    )
    with TokenMeter(
        conn, tier="recurrence", label=f"RECUR:{finding.id}"
    ) as meter:
        response = meter.record(client.complete(request))

    payload = response.parsed_json or {}
    offered = {c.id for c in candidates}
    matches = []
    for entry in payload.get("recurrences", []):
        # An id that was never on the shortlist is dropped, not shown. The same
        # rule the audit report uses: a fabricated reference carries a
        # citation's authority and is worse than no reference at all.
        if entry.get("finding_id") in offered:
            matches.append(entry)
    return matches, response


def _record_recurrence(repo, people, finding, matches, candidates, response, report):
    prior = [m["finding_id"] for m in matches]
    if prior:
        finding.recurrence_of = prior
        repo["findings"].update(finding)
        for match in matches:
            report.linked.append((finding.id, match["finding_id"]))
    repo["audit"].append(
        actor="ai", owner=people.name(finding.owner_identity),
        action="recurrence_examined", entity_type="Finding", entity_id=finding.id,
        detail={
            "candidates_offered": [c.id for c in candidates],
            "recurrence_of": prior,
            "reasons": {m["finding_id"]: m.get("reason", "") for m in matches},
            "confidence": {
                m["finding_id"]: m.get("confidence") for m in matches
            },
            "gap_category": finding.gap_category,
            "prompt_version": RECURRENCE_PROMPT_VERSION,
            "model": response.model,
            "note": "advisory; a link points at a prior finding and merges nothing",
        },
    )


# --- use 5: the prioritisation brief ----------------------------------------

def rank_open_findings(repo, people: Directory, as_of: date) -> list[dict[str, Any]]:
    """The ranking, computed. Section 8's inputs, ordered by urgency.

    Deterministic on purpose: the model is asked to *interpret* a ranking, not
    to produce one. A model that decided the order would be making a
    prioritisation decision, which is exactly what section 2 does not permit it
    to do.
    """
    units = {u.id: u for u in repo["units"].list()}
    escalations: dict[str, int] = {}
    for event in repo["audit"].read_all():
        if event.action == "finding_escalated":
            escalations[event.entity_id] = max(
                escalations.get(event.entity_id, 0),
                int(event.detail.get("level", 0)),
            )
    weight = {"Major": 3, "Minor": 2, "Observation": 1}
    rows = []
    for finding in repo["findings"].list():
        if finding.status != "open":
            continue
        severity = finding.severity or finding.suggested_severity or "Observation"
        days_overdue = (as_of - finding.target_date).days
        rows.append({
            "id": finding.id,
            "unit": (units[finding.auditable_unit_id].name
                     if finding.auditable_unit_id in units
                     else finding.auditable_unit_id),
            "severity": severity,
            "category": finding.gap_category or "unclassified",
            "owner": people.name(finding.owner_identity),
            "days_open": (as_of - finding.raised_at.date()).days,
            "days_overdue": max(days_overdue, 0),
            "follow_ups": finding.follow_up_count,
            "escalation": escalations.get(finding.id, 0),
            "recurrence_of": list(finding.recurrence_of),
            "description": finding.description,
            "_score": (
                weight.get(severity, 1) * 100
                + max(days_overdue, 0)
                + finding.follow_up_count * 5
                + escalations.get(finding.id, 0) * 25
            ),
        })
    rows.sort(key=lambda r: (-r["_score"], r["id"]))
    for row in rows:
        row.pop("_score")
    return rows


def portfolio_metrics(repo, as_of: date, ranked: list[dict[str, Any]]):
    """Section 8's figures, computed from state and the log. No model."""
    findings = repo["findings"].list()
    open_findings = [f for f in findings if f.status == "open"]
    severity_mix: dict[str, int] = {}
    by_unit: dict[str, int] = {}
    by_category: dict[str, int] = {}
    ageing = {name: 0 for name, _, _ in AGEING_BUCKETS}
    units = {u.id: u.name for u in repo["units"].list()}

    for finding in open_findings:
        severity = finding.severity or finding.suggested_severity or "unassigned"
        severity_mix[severity] = severity_mix.get(severity, 0) + 1
        unit = units.get(finding.auditable_unit_id, finding.auditable_unit_id)
        by_unit[unit] = by_unit.get(unit, 0) + 1
        category = finding.gap_category or "unclassified"
        by_category[category] = by_category.get(category, 0) + 1
        overdue = (as_of - finding.target_date).days
        if overdue >= 0:
            for name, low, high in AGEING_BUCKETS:
                if low <= overdue <= high:
                    ageing[name] += 1
                    break

    rounds_per_finding: dict[str, int] = {}
    for record in repo["rounds"].list():
        rounds_per_finding[record.finding_id] = (
            rounds_per_finding.get(record.finding_id, 0) + 1
        )
    return {
        "open": len(open_findings),
        "closed": len([f for f in findings if f.status == "closed"]),
        "severity_mix": dict(sorted(severity_mix.items())),
        "ageing": ageing,
        "overdue": sum(1 for r in ranked if r["days_overdue"] > 0),
        "escalated": sum(1 for r in ranked if r["escalation"]),
        "by_unit": dict(sorted(by_unit.items(), key=lambda kv: -kv[1])),
        "by_category": dict(sorted(by_category.items(), key=lambda kv: -kv[1])),
        "multi_round": sum(1 for n in rounds_per_finding.values() if n > 1),
    }


def uncited_claims(text: str, known: set[str]) -> list[str]:
    """Same rule as the audit report, and for the same reason."""
    problems = []
    for raw in re.split(r"(?<=[.!?])\s+", text.strip()):
        sentence = raw.strip()
        if not sentence:
            continue
        ids = {
            part.strip()
            for group in CITATION.findall(sentence)
            for part in group.split(",")
        }
        if not ids:
            if not re.search(r"\d", sentence):
                problems.append(f"uncited: {sentence}")
            continue
        unknown = ids - known
        if unknown:
            problems.append(f"cites unknown {', '.join(sorted(unknown))}")
    return problems


def prioritisation_brief(conn, as_of: date, *, client=None) -> Brief:
    """One call. Over the ranking and the metrics, not over the findings."""
    from ..repositories import repositories, simulated_clock

    repo = repositories(conn)
    people = directory.load(conn)
    ranked = rank_open_findings(repo, people, as_of)
    metrics = portfolio_metrics(repo, as_of, ranked)
    brief = Brief(as_of=as_of, metrics=metrics, ranked=ranked)
    if not ranked:
        return brief

    top = ranked[:TOP_N]
    request = LlmRequest(
        system=BRIEF_SYSTEM_V1,
        messages=[{
            "role": "user",
            "content": brief_user_v1(as_of.isoformat(), metrics, top),
        }],
        response_schema=brief_schema_v1(),
        max_tokens=BRIEF_MAX_TOKENS,
        tier="brief",
    )
    with simulated_clock(datetime.combine(as_of, time(18, 0))):
        with TokenMeter(
            conn, tier="brief", label=f"BRIEF:{as_of.isoformat()}"
        ) as meter:
            response = meter.record((client or get_client()).complete(request))
        brief.model_calls = 1
        brief.model = response.model

        payload = response.parsed_json or {}
        text = str(payload.get("brief", "")).strip()
        known = {row["id"] for row in top}
        if text and not uncited_claims(text, known):
            brief.text = text
            brief.cited = sorted({
                part.strip()
                for group in CITATION.findall(text)
                for part in group.split(",")
            })

        repo["audit"].append(
            actor="ai", owner="portfolio", action="brief_generated",
            entity_type="Cycle", entity_id=as_of.isoformat(),
            detail={
                "open": metrics["open"],
                "ranked": len(top),
                "cited": brief.cited,
                "withheld": not brief.text,
                "prompt_version": BRIEF_PROMPT_VERSION,
                "model": brief.model,
                "note": "advisory; changes no state",
            },
        )
    return brief
