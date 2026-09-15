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
from .. import analytics, priority
from ..llm.parsing import validate
from ..llm.prompts.brief import (
    BRIEF_SYSTEM_V3,
    MAX_TOKENS as BRIEF_MAX_TOKENS,
    REASON_MAX,
    TOP_N,
    brief_schema_v2,
    brief_user_v3,
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
    BATCH_SIZE,
    SEVERITIES,
    TRIAGE_SYSTEM_V1,
    triage_schema_v1,
    triage_user_v1,
)
from . import taxonomy
from ..llm.prompts.triage import PROMPT_VERSION as TRIAGE_PROMPT_VERSION
from ..llm.protocol import LlmError, LlmRequest

#: Short answers, per finding, times the batch. A classification that needs four
#: hundred tokens to explain itself is not a classification.
TRIAGE_TOKENS_PER_FINDING = 160
TRIAGE_MAX_TOKENS = 260
RECURRENCE_MAX_TOKENS = 500

#: Below this the suggestion is recorded but marked for a human to look at, the
#: same threshold discipline S3 uses on its verdicts.
CONFIDENCE_FLOOR = 0.6

#: `[FND-1]` or `[FND-1, FND-2]`.
CITATION = re.compile(r"\[([A-Z0-9\-]+(?:\s*,\s*[A-Z0-9\-]+)*)\]")


@dataclass
class TriageReport:
    as_of: date
    classified: list[str] = field(default_factory=list)
    needs_review: list[str] = field(default_factory=list)
    model_calls: int = 0
    by_category: dict[str, int] = field(default_factory=dict)
    batches: int = 0
    taxonomy_version: str = ""

    def summary(self) -> str:
        return (
            f"{len(self.classified)} findings classified in {self.batches} "
            f"batch(es) / {self.model_calls} model call(s), "
            f"{len(self.needs_review)} flagged for review"
        )


@dataclass
class RecurrenceReport:
    as_of: date
    examined: list[str] = field(default_factory=list)
    linked: list[tuple[str, str]] = field(default_factory=list)
    model_calls: int = 0
    skipped_no_candidates: int = 0
    #: Already asked about exactly these candidates, or more, and found no link.
    skipped_already_examined: int = 0


@dataclass
class Brief:
    """One prioritisation brief. Advisory: nothing reads it back to decide anything.

    `ranked` and `metrics` are deterministic and always present. The three
    sections are the model's, and they are empty unless every claim in the
    drafted brief checked out; `withheld` says why when one did not.
    """

    as_of: date
    top_priorities: list[dict[str, Any]] = field(default_factory=list)
    emerging_patterns: list[dict[str, Any]] = field(default_factory=list)
    recommended_focus: list[dict[str, Any]] = field(default_factory=list)
    ranked: list[dict[str, Any]] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    withheld: list[str] = field(default_factory=list)
    model_calls: int = 0
    prompt_version: str = BRIEF_PROMPT_VERSION
    model: str = ""
    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def published(self) -> bool:
        return bool(self.model_calls and not self.withheld and self.top_priorities)

    @property
    def cited_findings(self) -> list[str]:
        cited = {item["finding_id"] for item in self.top_priorities}
        for claim in self.emerging_patterns + self.recommended_focus:
            cited.update(claim["finding_ids"])
        return sorted(cited)

    @property
    def cited_metrics(self) -> list[str]:
        return sorted({
            name for claim in self.emerging_patterns + self.recommended_focus
            for name in claim["metrics"]
        })


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

    **Batched.** The system prompt and the category catalogue are most of the
    tokens in a classification call, so sending them once per finding pays for
    the same paragraph over and over. Findings travel
    `BATCH_SIZE` at a time and each keeps its own answer.

    Runs only on findings that have no category yet, so it is idempotent and a
    second pass over the same corpus spends nothing.

    The taxonomy must already have been derived. There is deliberately no
    fallback list: a silent default is exactly what this stage stopped doing.
    """
    from ..repositories import repositories, simulated_clock

    repo = repositories(conn)
    people = directory.load(conn)
    categories = taxonomy.require(conn)
    report = TriageReport(as_of=as_of, taxonomy_version=categories[0].taxonomy_version)
    pending = [f for f in sorted(repo["findings"].list(), key=lambda f: f.id)
               if not f.gap_category]
    if limit is not None:
        pending = pending[:limit]

    names = tuple(c.id for c in categories)
    definitions = {c.id: c.definition for c in categories}
    model_client = client or get_client()

    with simulated_clock(datetime.combine(as_of, time(7, 0))):
        for group in taxonomy.batches(pending, BATCH_SIZE):
            answers, response = _ask_triage(
                conn, model_client,
                [_finding_context(repo, people, f) for f in group],
                names, definitions,
            )
            report.model_calls += 1
            report.batches += 1
            for finding in group:
                _record_triage(
                    repo, people, finding, answers[finding.id], response, report,
                )
    return report


def _ask_triage(conn, client, contexts: list[dict[str, Any]], names, definitions):
    """One call, many findings. Returns the answers keyed by finding id."""
    request = LlmRequest(
        system=TRIAGE_SYSTEM_V1,
        messages=[{"role": "user", "content": triage_user_v1(contexts, definitions)}],
        response_schema=triage_schema_v1(names),
        max_tokens=TRIAGE_TOKENS_PER_FINDING * len(contexts),
        tier="triage",
    )
    label = f"TRIAGE:{contexts[0]['id']}+{len(contexts) - 1}"
    with TokenMeter(conn, tier="triage", label=label) as meter:
        response = meter.record(client.complete(request))
    payload = response.parsed_json or {}

    # Validated whatever came back — a defence that relies on the model having
    # behaved is not a defence. Three separate things can go wrong with a batch
    # and each is named rather than collapsed into "bad response".
    answers: dict[str, dict[str, Any]] = {}
    asked = {context["id"] for context in contexts}
    for entry in payload.get("findings", []):
        if entry.get("id") not in asked:
            raise ValueError(
                f"triage answered for {entry.get('id')!r}, which was not in the "
                f"batch; an answer about a finding we did not send cannot be "
                f"filed against one we did"
            )
        if entry.get("category") not in names:
            raise ValueError(
                f"category {entry.get('category')!r} is outside the derived "
                f"taxonomy"
            )
        if entry.get("suggested_severity") not in SEVERITIES:
            raise ValueError(
                f"severity {entry.get('suggested_severity')!r} is outside the enum"
            )
        answers[entry["id"]] = entry

    missing = sorted(asked - set(answers))
    if missing:
        raise ValueError(
            f"triage returned no answer for {', '.join(missing)}; a batch that "
            f"silently drops findings leaves them looking unclassifiable when "
            f"they are only unanswered"
        )
    return answers, response


def _record_triage(repo, people, finding: Finding, payload, response, report):
    finding_taxonomy_version = report.taxonomy_version
    confidence = float(payload.get("confidence", 0.0))
    finding.gap_category = payload["category"]
    # The severity suggestion is *not* written here for audit-raised findings.
    # Section 1 says severity is finalised after the audit completes and
    # communicated in the report, so `audits.suggest_severities` owns it and
    # produces it there, beside the auditor's own assignment at the moment the
    # two are actually compared. Writing it here would mean the suggestion
    # existed before the audit it belongs to had finished.
    #
    # Activity-track findings have no audit to complete, so there is no later
    # moment to wait for and the suggestion is recorded now.
    if finding.source != "audit":
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
            "taxonomy_version": finding_taxonomy_version,
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
    known = taxonomy.names(conn)
    if category not in known:
        raise ValueError(
            f"{category!r} is not in the derived taxonomy "
            f"({', '.join(known) or 'none derived'})"
        )

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

    # Same track first, then oldest.
    #
    # The shortlist is capped, and it used to be capped on age alone. That is an
    # arbitrary tiebreak, and after a full run the activity track wins it on
    # volume: it produces hundreds of findings a year against the audit track's
    # dozens, so twelve slots fill with system-generated descriptions and the
    # auditor-written prior that is the actual recurrence never reaches the
    # model. The effect was invisible while the taxonomy was hardcoded, because
    # activity findings piled into a category the audit track barely used;
    # deriving the categories from the corpus redistributed them and the
    # crowding surfaced as recall falling from 50% to 16.7%.
    #
    # Same-track-first rather than same-track-only: an auditor finding the same
    # gap that a periodic check also caught is a real link and worth keeping.
    # But it competes for the leftover slots instead of taking them by weight of
    # numbers. This is also the pairing the score is computed over, so the
    # shortlist and the measurement now agree about what is being compared.
    out.sort(key=lambda f: (f.source != finding.source, f.raised_at))
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
    # What each finding has already been asked about. This used to re-ask every
    # unlinked finding on every run, paying again for answers already on the
    # trail — the harness ran it once so it never showed, but the dashboard runs
    # it each cycle. A finding is asked again only when a candidate it was never
    # shown has appeared since.
    offered_before: dict[str, set[str]] = {}
    for event in repo["audit"].read_all():
        if event.action == "recurrence_examined":
            offered_before.setdefault(event.entity_id, set()).update(
                event.detail.get("candidates_offered", [])
            )
    if limit is not None:
        findings = findings[:limit]

    model_client = client or get_client()
    units = {u.id: u for u in repo["units"].list()}
    with simulated_clock(datetime.combine(as_of, time(7, 30))):
        for finding in findings:
            candidates = candidates_for(repo, finding)
            if not candidates:
                report.examined.append(finding.id)
                # No call at all. Most findings are the first of their kind.
                report.skipped_no_candidates += 1
                continue
            if {c.id for c in candidates} <= offered_before.get(finding.id, set()):
                # Asked already, about these candidates or more, and the answer
                # was no link. Nothing new to ask.
                report.skipped_already_examined += 1
                continue
            report.examined.append(finding.id)
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

def _inline_ids(text: str) -> set[str]:
    return {
        part.strip()
        for group in CITATION.findall(text)
        for part in group.split(",")
        if part.strip()
    }


def _claim(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "statement": str(entry.get("statement", "")).strip(),
        "finding_ids": [str(i) for i in entry.get("finding_ids") or []],
        "metrics": [str(m) for m in entry.get("metrics") or []],
    }


def validate_brief(
    payload: Any, *, known_ids: set[str], metric_names: set[str],
) -> list[str]:
    """Every problem with a drafted brief, or an empty list when there are none.

    A claim is checkable only if it says what it rests on. So: every top
    priority names a finding from the ranked list the call was given, with a
    one-line reason; every pattern and focus statement lists finding ids or
    named metrics, and at least one of them; every id and every metric name
    resolves; and an id mentioned inline in a statement is also listed. One
    failure withholds the whole brief — a brief with one invented figure in it
    reads exactly as authoritative as one without.
    """
    if not isinstance(payload, dict):
        return ["the reply is not a JSON object"]
    try:
        validate(payload, brief_schema_v2())
    except LlmError as error:
        return [f"the reply does not match the schema: {error}"]

    problems: list[str] = []
    tops = payload.get("top_priorities") or []
    if not isinstance(tops, list) or not tops:
        problems.append("no top priorities were named")
        tops = tops if isinstance(tops, list) else []
    seen: set[str] = set()
    for entry in tops:
        if not isinstance(entry, dict):
            problems.append("a top priority is not an object")
            continue
        finding_id = str(entry.get("finding_id", ""))
        reason = str(entry.get("reason", "")).strip()
        if finding_id not in known_ids:
            problems.append(
                f"top priority {finding_id!r} is not in the ranked list the brief "
                f"was given"
            )
        if finding_id in seen:
            problems.append(f"top priority {finding_id} is named twice")
        seen.add(finding_id)
        if not reason:
            problems.append(f"top priority {finding_id} gives no reason")
        elif "\n" in reason or len(reason) > REASON_MAX:
            problems.append(
                f"the reason for {finding_id} is not one line of at most "
                f"{REASON_MAX} characters"
            )
        stray = _inline_ids(reason) - known_ids
        if stray:
            problems.append(
                f"the reason for {finding_id} cites {', '.join(sorted(stray))}, "
                f"which the brief was not given"
            )

    for section in ("emerging_patterns", "recommended_focus"):
        entries = payload.get(section) or []
        if not isinstance(entries, list):
            problems.append(f"{section} is not a list")
            continue
        if section == "recommended_focus" and not entries:
            problems.append("no recommended focus was given")
        for entry in entries:
            if not isinstance(entry, dict):
                problems.append(f"{section}: an entry is not an object")
                continue
            claim = _claim(entry)
            label = claim["statement"][:90] or "(empty statement)"
            if not claim["statement"]:
                problems.append(f"{section}: an entry has no statement")
            if not claim["finding_ids"] and not claim["metrics"]:
                problems.append(f"{section}: uncited claim: {label}")
            unknown_ids = set(claim["finding_ids"]) - known_ids
            if unknown_ids:
                problems.append(
                    f"{section}: cites {', '.join(sorted(unknown_ids))}, which the "
                    f"brief was not given: {label}"
                )
            unknown_metrics = set(claim["metrics"]) - metric_names
            if unknown_metrics:
                problems.append(
                    f"{section}: cites metric(s) {', '.join(sorted(unknown_metrics))} "
                    f"that are not in the catalogue: {label}"
                )
            unlisted = _inline_ids(claim["statement"]) - set(claim["finding_ids"])
            if unlisted:
                problems.append(
                    f"{section}: the statement mentions "
                    f"{', '.join(sorted(unlisted))} without citing them: {label}"
                )
    return problems


def prioritisation_brief(conn, as_of: date, *, client=None) -> Brief:
    """One call per cycle, over the deterministic ranking and section 8's figures.

    The order comes from `sentinelops.priority`; the figures from
    `sentinelops.analytics`, under the names in `analytics.named_metrics`. The
    model chooses which ranked findings to put first and says why, and names
    patterns and a focus — but top priorities are always shown in the ranking's
    order, so it can explain the queue without reordering it.
    """
    from ..repositories import repositories, simulated_clock

    repo = repositories(conn)
    people = directory.load(conn)
    ranked = priority.rank(repo, people, as_of)
    top = ranked[:TOP_N]
    # Two scopes, kept apart in the prompt and together for validation and
    # rendering: portfolio figures from section 8, and counts over exactly the
    # rows the call is shown. A claim about those rows needs the second kind.
    portfolio = analytics.named_metrics(analytics.portfolio(conn, as_of))
    listed = priority.listed_metrics(top)
    metrics = {**portfolio, **listed}
    brief = Brief(as_of=as_of, ranked=ranked, metrics=metrics)
    if not ranked:
        return brief

    request = LlmRequest(
        system=BRIEF_SYSTEM_V3,
        messages=[{
            "role": "user",
            "content": brief_user_v3(
                as_of.isoformat(), portfolio, listed, top, total_open=len(ranked)
            ),
        }],
        response_schema=brief_schema_v2(),
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
        brief.input_tokens = response.input_tokens
        brief.output_tokens = response.output_tokens

        payload = response.parsed_json or {}
        by_id = {row["id"]: row for row in top}
        problems = validate_brief(
            payload, known_ids=set(by_id), metric_names=set(metrics),
        )
        if problems:
            brief.withheld = problems
        else:
            brief.top_priorities = sorted(
                (
                    {
                        "finding_id": entry["finding_id"],
                        "reason": str(entry["reason"]).strip(),
                        "rank": by_id[entry["finding_id"]]["rank"],
                        "band": by_id[entry["finding_id"]]["band_label"],
                        "score": by_id[entry["finding_id"]]["score"],
                    }
                    for entry in payload["top_priorities"]
                ),
                key=lambda item: item["rank"],
            )
            brief.emerging_patterns = [
                _claim(entry) for entry in payload.get("emerging_patterns") or []
            ]
            brief.recommended_focus = [
                _claim(entry) for entry in payload.get("recommended_focus") or []
            ]

        repo["audit"].append(
            actor="ai", owner="portfolio", action="brief_generated",
            entity_type="Cycle", entity_id=as_of.isoformat(),
            detail={
                "open": metrics["open_findings"],
                "ranked": len(top),
                "top_priorities": [i["finding_id"] for i in brief.top_priorities],
                "cited_findings": brief.cited_findings,
                "cited_metrics": brief.cited_metrics,
                "withheld": bool(brief.withheld),
                "withheld_reasons": brief.withheld,
                "prompt_version": BRIEF_PROMPT_VERSION,
                "model": brief.model,
                "note": "advisory; changes no state",
            },
        )
    return brief
