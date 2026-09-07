"""The audit programme, and the report it produces at the end.

Section 1 draws a line the rest of the system has to respect: **audits** are
conducted by PA/InfoSec and their output is findings; **compliance activities**
are done by a unit's owner and their output is evidence. Both are scheduled,
which is why they get confused, and both live in this codebase — the activity
track is `trigger.py` through `flag.py`, and this module is the audit track.

Findings are children of audits. A finding raised here carries `audit_id` and
`source="audit"`; one raised from a failed compliance activity carries
`check_instance_id` and `source="activity_assessment"`. They are the same object
because the follow-up, the evidence rounds and the closure decision are the same
work either way — only the provenance differs, and the provenance is recorded
rather than implied.

**The report** (section 6) replaces something written and emailed by hand. Almost
all of it is structured data rendered deterministically. Exactly one paragraph is
generated, over the structured findings, and every statement in it must cite
finding ids — verified here, not trusted. Issuing is a separate act by a human,
and it appends an audit event.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime, time
from typing import Any

from .. import authority, directory
from ..directory import Directory
from ..entities import Finding, ScheduledAudit
from ..llm import get_client
from ..llm.prompts.audit_report import (
    AUDIT_REPORT_SYSTEM_V1,
    PROMPT_VERSION,
    audit_report_schema_v1,
    audit_report_user_v1,
)
from ..llm.protocol import LlmRequest
from . import followup

#: The summary is a paragraph, not an essay. A hard ceiling on a generation that
#: nobody reads past sentence five is cost discipline that costs nothing.
MAX_TOKENS = 500

#: `[FND-1]` or `[FND-1, FND-2]`.
CITATION = re.compile(r"\[([A-Z0-9\-]+(?:\s*,\s*[A-Z0-9\-]+)*)\]")

#: A sentence with no ids is allowed only if it is arithmetic or a date — those
#: come from the facts we handed the model and are checkable directly.
BARE_SENTENCE_OK = re.compile(r"\d")


@dataclass
class AuditReport:
    audit_id: str
    kind: str
    title: str
    auditor: str
    scope: list[str]
    planned_date: date
    conducted_date: date | None
    findings: list[dict[str, Any]] = field(default_factory=list)
    summary: str = ""
    summary_cited: list[str] = field(default_factory=list)
    prompt_version: str = PROMPT_VERSION
    model: str = ""
    generated_at: datetime | None = None
    issued_at: datetime | None = None
    issued_by: str = ""

    @property
    def by_severity(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for finding in self.findings:
            key = finding["severity"] or "unassigned"
            out[key] = out.get(key, 0) + 1
        return out


class UncitedSummary(ValueError):
    """The narrative made a claim it did not attribute. Not publishable."""


def conduct(
    conn,
    audit_id: str,
    *,
    by: str,
    as_of: date,
) -> ScheduledAudit:
    """Mark an audit conducted. PA/InfoSec only."""
    from ..repositories import repositories, simulated_clock

    repo = repositories(conn)
    people = directory.load(conn)
    audit = repo["audits"].get(audit_id)
    if audit is None:
        raise ValueError(f"no such audit: {audit_id}")

    identity = people.get(by)
    authority.require(identity.role if identity else None, "conduct_audit",
                      actor_id=by)

    with simulated_clock(datetime.combine(as_of, time(9, 0))):
        audit.status = "completed"
        audit.conducted_date = as_of
        repo["audits"].update(audit)
        repo["audit"].append(
            actor="user", owner=people.name(by), action="audit_conducted",
            entity_type="ScheduledAudit", entity_id=audit.id,
            detail={
                "kind": audit.kind,
                "scope": audit.scope,
                "planned_date": audit.planned_date.isoformat(),
                "conducted_date": as_of.isoformat(),
                "auditor_identity": by,
            },
            actor_identity=by,
        )
    return audit


def raise_finding(
    conn,
    audit_id: str,
    *,
    unit_id: str,
    description: str,
    severity: str,
    by: str,
    agreed_action_plan: str = "",
    gap_category: str = "",
    as_of: date,
    finding_id: str | None = None,
) -> Finding:
    """A finding raised by an auditor during an audit.

    Severity is assigned here, by the auditor, at the point of raising — section
    1 says it is finalised after the audit completes and communicated in the
    report. There is no suggestion to override because no model was involved:
    this is a person writing down what they found.
    """
    from ..repositories import repositories, simulated_clock

    repo = repositories(conn)
    people = directory.load(conn)
    audit = repo["audits"].get(audit_id)
    if audit is None:
        raise ValueError(f"no such audit: {audit_id}")

    identity = people.get(by)
    authority.require(identity.role if identity else None, "raise_finding",
                      actor_id=by)
    if unit_id not in audit.scope:
        raise ValueError(
            f"{unit_id} is not in the scope of {audit_id} "
            f"({', '.join(audit.scope)}); a finding cannot be raised against a "
            "unit the audit did not look at"
        )
    unit = repo["units"].get(unit_id)
    if unit is None:
        raise ValueError(f"no such auditable unit: {unit_id}")

    existing = len([f for f in repo["findings"].list() if f.audit_id == audit_id])
    criticality = unit.attributes.get("criticality", "")
    with simulated_clock(datetime.combine(as_of, time(10, 0))):
        finding = Finding(
            id=finding_id or f"FND-{audit_id.removeprefix('AUD-')}-{existing + 1:02d}",
            source="audit",
            auditable_unit_id=unit_id,
            description=description,
            raised_by=by,
            raised_at=datetime.combine(as_of, time(10, 0)),
            owner_identity=unit.owner_identity,
            target_date=followup.target_date_for(as_of, severity, criticality),
            audit_id=audit_id,
            gap_category=gap_category,
            severity=severity,  # type: ignore[arg-type]
            severity_assigned_by=by,
            agreed_action_plan=agreed_action_plan,
            status="open",
        )
        repo["findings"].add(finding)
        repo["audit"].append(
            actor="user", owner=people.name(finding.owner_identity),
            action="finding_raised", entity_type="Finding", entity_id=finding.id,
            detail={
                "source": "audit",
                "audit_id": audit_id,
                "auditable_unit_id": unit_id,
                "description": description,
                "severity": severity,
                "suggested_severity": None,
                "gap_category": gap_category,
                "target_date": finding.target_date.isoformat(),
                "owner_identity": finding.owner_identity,
                "raised_by": by,
                "status": "open",
            },
            actor_identity=by,
        )
    return finding


def findings_of(repo, audit_id: str) -> list[Finding]:
    return sorted(
        (f for f in repo["findings"].list() if f.audit_id == audit_id),
        key=lambda f: f.id,
    )


def _structured(repo, people: Directory, audit: ScheduledAudit) -> list[dict[str, Any]]:
    units = {u.id: u for u in repo["units"].list()}
    rows = []
    for finding in findings_of(repo, audit.id):
        unit = units.get(finding.auditable_unit_id)
        rows.append({
            "id": finding.id,
            "unit": unit.name if unit else finding.auditable_unit_id,
            "unit_id": finding.auditable_unit_id,
            "severity": finding.severity or "unassigned",
            "category": finding.gap_category or "uncategorised",
            "owner": people.name(finding.owner_identity),
            "target_date": finding.target_date.isoformat(),
            "description": finding.description,
            "agreed_action_plan": finding.agreed_action_plan,
            "recurrence_of": list(finding.recurrence_of),
        })
    return rows


def uncited_claims(summary: str, known_ids: set[str]) -> list[str]:
    """Sentences that assert something without attributing it.

    Two failure modes, both caught here: a sentence that cites nothing, and one
    that cites an id this audit never raised. The second is the dangerous one —
    a plausible-looking `[FND-47]` in an issued report is a fabricated reference
    with a citation's authority.
    """
    problems = []
    for raw in re.split(r"(?<=[.!?])\s+", summary.strip()):
        sentence = raw.strip()
        if not sentence:
            continue
        cited = CITATION.findall(sentence)
        ids = {
            part.strip() for group in cited for part in group.split(",")
        }
        if not ids:
            if not BARE_SENTENCE_OK.search(sentence):
                problems.append(f"uncited: {sentence}")
            continue
        unknown = ids - known_ids
        if unknown:
            problems.append(
                f"cites {', '.join(sorted(unknown))}, which this audit did not "
                f"raise: {sentence}"
            )
    return problems


def generate_report(
    conn, audit_id: str, *, client=None, as_of: date | None = None
) -> AuditReport:
    """Assemble the report. One model call, for the summary paragraph only.

    Everything else here is a read. If the summary cannot be produced with
    resolvable citations the report is still assembled and still useful — it
    simply carries no narrative, and says so. A report that fails to generate
    because a paragraph would not come out right helps nobody.
    """
    from ..llm import TokenMeter
    from ..repositories import repositories, simulated_clock

    repo = repositories(conn)
    people = directory.load(conn)
    audit = repo["audits"].get(audit_id)
    if audit is None:
        raise ValueError(f"no such audit: {audit_id}")
    if audit.status != "completed":
        raise ValueError(
            f"{audit_id} is {audit.status}; a report is generated at audit "
            "completion, not before"
        )

    as_of = as_of or audit.conducted_date or audit.planned_date
    findings = _structured(repo, people, audit)
    report = AuditReport(
        audit_id=audit.id,
        kind=audit.kind,
        title=audit.title,
        auditor=people.name(audit.auditor_identity),
        scope=[
            (repo["units"].get(u).name if repo["units"].get(u) else u)
            for u in audit.scope
        ],
        planned_date=audit.planned_date,
        conducted_date=audit.conducted_date,
        findings=findings,
    )

    if findings:
        summary, cited, model = _draft_summary(
            conn, audit, findings, people, client=client
        )
        report.summary = summary
        report.summary_cited = cited
        report.model = model

    with simulated_clock(datetime.combine(as_of, time(16, 0))):
        report.generated_at = datetime.combine(as_of, time(16, 0))
        audit.report_generated_at = report.generated_at
        repo["audits"].update(audit)
        repo["audit"].append(
            actor="ai" if report.summary else "system",
            owner=report.auditor, action="audit_report_generated",
            entity_type="ScheduledAudit", entity_id=audit.id,
            detail={
                "findings": len(findings),
                "by_severity": report.by_severity,
                "summary_present": bool(report.summary),
                "summary_cited": report.summary_cited,
                "prompt_version": PROMPT_VERSION,
                "model": report.model,
            },
            actor_identity=audit.auditor_identity,
        )
    return report


def _draft_summary(
    conn, audit: ScheduledAudit, findings: list[dict[str, Any]],
    people: Directory, *, client=None,
) -> tuple[str, list[str], str]:
    """One call. Citations verified against the findings this audit raised."""
    from ..llm import TokenMeter

    model_client = client or get_client()
    request = LlmRequest(
        system=AUDIT_REPORT_SYSTEM_V1,
        messages=[{
            "role": "user",
            "content": audit_report_user_v1(
                {
                    "id": audit.id,
                    "kind": audit.kind,
                    "title": audit.title,
                    "auditor": people.name(audit.auditor_identity),
                    "planned_date": audit.planned_date.isoformat(),
                    "conducted_date": (
                        audit.conducted_date.isoformat()
                        if audit.conducted_date else "not recorded"
                    ),
                    "scope": [f["unit"] for f in findings] or [],
                },
                findings,
            ),
        }],
        response_schema=audit_report_schema_v1(),
        max_tokens=MAX_TOKENS,
        tier="report",
    )
    with TokenMeter(conn, tier="report", label=f"REPORT:{audit.id}") as meter:
        response = meter.record(model_client.complete(request))

    payload = response.parsed_json or {}
    summary = str(payload.get("summary", "")).strip()
    if not summary:
        return "", [], response.model

    known = {f["id"] for f in findings}
    problems = uncited_claims(summary, known)
    if problems:
        # Not published. Section 6 says every statement cites finding ids, and a
        # summary that does not is worse than none: it reads as authoritative.
        return "", [], response.model
    cited = sorted({
        part.strip()
        for group in CITATION.findall(summary)
        for part in group.split(",")
    })
    return summary, cited, response.model


def issue(conn, audit_id: str, *, by: str, as_of: date) -> ScheduledAudit:
    """A human confirms and issues. The model drafted; it does not sign."""
    from ..repositories import repositories, simulated_clock

    repo = repositories(conn)
    people = directory.load(conn)
    audit = repo["audits"].get(audit_id)
    if audit is None:
        raise ValueError(f"no such audit: {audit_id}")
    if audit.report_generated_at is None:
        raise ValueError(
            f"{audit_id} has no generated report to issue; generate it first"
        )

    identity = people.get(by)
    authority.require(identity.role if identity else None, "conduct_audit",
                      actor_id=by)

    with simulated_clock(datetime.combine(as_of, time(17, 0))):
        audit.report_issued_at = datetime.combine(as_of, time(17, 0))
        audit.report_issued_by = by
        repo["audits"].update(audit)
        repo["audit"].append(
            actor="user", owner=people.name(by), action="audit_report_issued",
            entity_type="ScheduledAudit", entity_id=audit.id,
            detail={
                "issued_by": by,
                "issued_at": audit.report_issued_at.isoformat(),
                "findings": len(findings_of(repo, audit.id)),
                "note": "reviewed and confirmed by the auditor before issue",
            },
            actor_identity=by,
        )
    return audit


def render_markdown(report: AuditReport) -> str:
    """The report as it is emailed today, minus the emailing.

    Deterministic. The only generated text in here is `report.summary`, and it
    is clearly labelled as a draft for the auditor to confirm.
    """
    out: list[str] = []
    add = out.append
    kind = report.kind.replace("_", " ").title()
    add(f"# {kind} — {report.title or report.audit_id}")
    add("")
    add(f"| | |")
    add(f"|---|---|")
    add(f"| Audit | `{report.audit_id}` |")
    add(f"| Kind | {kind} |")
    add(f"| Auditor | {report.auditor} |")
    add(f"| Scope | {', '.join(report.scope) or '—'} |")
    add(f"| Planned | {report.planned_date} |")
    add(f"| Conducted | {report.conducted_date or 'not recorded'} |")
    add(f"| Findings | {len(report.findings)} |")
    add("")

    if report.summary:
        add("## Summary")
        add("")
        add(report.summary)
        add("")
        add(
            f"_Drafted from the findings below ({report.prompt_version}); every "
            f"statement cites the findings it rests on. For the auditor to "
            f"review and confirm before issue._"
        )
    else:
        add("## Summary")
        add("")
        add(
            "_No narrative summary is attached. Either this audit raised no "
            "findings, or the drafted summary made a statement it could not "
            "attribute to one and was withheld._"
        )
    add("")

    add("## Findings")
    add("")
    if not report.findings:
        add("None raised.")
        return "\n".join(out) + "\n"

    mix = ", ".join(f"{n} {sev}" for sev, n in sorted(report.by_severity.items()))
    add(f"{len(report.findings)} raised — {mix}.")
    add("")
    for finding in report.findings:
        add(f"### {finding['id']} — {finding['severity']}")
        add("")
        add(f"- **Unit** {finding['unit']}")
        add(f"- **Category** {finding['category']}")
        add(f"- **Owner** {finding['owner']} · **target** {finding['target_date']}")
        add("")
        add(finding["description"])
        add("")
        if finding["agreed_action_plan"]:
            add(f"**Agreed action plan.** {finding['agreed_action_plan']}")
            add("")
        if finding["recurrence_of"]:
            add(
                f"**Recurrence.** This resembles "
                f"{', '.join(finding['recurrence_of'])} raised previously."
            )
            add("")
    return "\n".join(out) + "\n"
