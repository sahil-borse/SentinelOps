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
from ..llm.prompts.triage import BATCH_SIZE as TRIAGE_BATCH_SIZE
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

#: No sentence goes uncited, counts included. Section 6 says every statement
#: cites finding ids, and until slice 16 a sentence containing a digit was
#: exempt, on the grounds that a count came from facts the model was given —
#: which is exactly the sentence that is wrong when the model miscounts.


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
    confirmed_at: datetime | None = None
    confirmed_by: str = ""
    #: Why the drafted summary was not published, when it was not.
    summary_withheld: list[str] = field(default_factory=list)

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


def suggest_severities(
    conn,
    audit_id: str,
    *,
    client=None,
    as_of: date | None = None,
) -> dict[str, str]:
    """Section 2, use 4: suggest a severity for every finding this audit raised.

    **Why here and not at classification.** Section 1 says severity is
    *finalised after the audit completes* and communicated to the auditee in the
    report. A suggestion offered earlier is advice about an audit still being
    written; offered here it sits beside the auditor's own assignment at the
    moment the report is drawn up, which is when the two are actually compared.

    **The suggestion never becomes the severity.** `severity` stays exactly as
    the auditor assigned it and `suggested_severity` is written separately, so
    divergence is visible rather than resolved. The trail records whether they
    agreed, because "how often does the model differ from the auditor?" is the
    question that decides whether this capability is worth keeping.

    Batched with classification's call, which reads the same sentence to reach
    both answers — asking twice would pay twice to re-read one paragraph.
    """
    from ..repositories import repositories, simulated_clock
    from . import intelligence, taxonomy

    repo = repositories(conn)
    people = directory.load(conn)
    audit = repo["audits"].get(audit_id)
    if audit is None:
        raise ValueError(f"no such audit: {audit_id}")
    if audit.status != "completed":
        raise ValueError(
            f"{audit_id} is {audit.status}; severity is finalised at audit "
            f"completion, not before"
        )

    findings = [f for f in findings_of(repo, audit_id) if not f.suggested_severity]
    if not findings:
        return {}

    stamp = datetime.combine(
        as_of or audit.conducted_date or audit.planned_date, time(15, 0)
    )
    categories = taxonomy.require(conn)
    names = tuple(c.id for c in categories)
    definitions = {c.id: c.definition for c in categories}
    model_client = client or get_client()

    agreed = 0
    out: dict[str, str] = {}
    with simulated_clock(stamp):
        for group in taxonomy.batches(findings, TRIAGE_BATCH_SIZE):
            answers, response = intelligence._ask_triage(
                conn, model_client,
                [intelligence._finding_context(repo, people, f) for f in group],
                names, definitions,
            )
            for finding in group:
                answer = answers[finding.id]
                finding.suggested_severity = answer["suggested_severity"]
                # The category too, where the auditor left it blank. It comes
                # back in the same reply and dropping it would mean paying for
                # it twice.
                if not finding.gap_category:
                    finding.gap_category = answer["category"]
                repo["findings"].update(finding)
                out[finding.id] = finding.suggested_severity
                same = finding.severity == finding.suggested_severity
                agreed += int(same)
                repo["audit"].append(
                    actor="ai", owner=people.name(finding.owner_identity),
                    action="finding_severity_suggested",
                    entity_type="Finding", entity_id=finding.id,
                    detail={
                        "suggested_severity": finding.suggested_severity,
                        "assigned_severity": finding.severity,
                        "agrees_with_auditor": same,
                        "gap_category": finding.gap_category,
                        "confidence": answer.get("confidence"),
                        "rationale": answer.get("rationale", ""),
                        "audit_id": audit_id,
                        "model": response.model,
                        "note": (
                            "advisory only; the auditor's assignment is "
                            "authoritative and is not changed here"
                        ),
                    },
                )

        repo["audit"].append(
            actor="ai", owner=people.name(audit.auditor_identity),
            action="audit_severities_suggested",
            entity_type="ScheduledAudit", entity_id=audit_id,
            detail={
                "findings": len(out),
                "agreed_with_auditor": agreed,
                "differed": len(out) - agreed,
                "note": "suggestions stored beside the assignments, never over them",
            },
            actor_identity=audit.auditor_identity,
        )
    return out


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
            "recurrence_links": [
                _prior_link(repo, units, prior_id)
                for prior_id in finding.recurrence_of
            ],
        })
    return rows


def _prior_link(repo, units, prior_id: str) -> dict[str, Any]:
    """The earlier finding a recurrence points at, as a reader needs it."""
    prior = repo["findings"].get(prior_id)
    if prior is None:
        raise ValueError(
            f"a recurrence link points at {prior_id}, which does not exist; a "
            f"report must not carry a reference nobody can follow"
        )
    unit = units.get(prior.auditable_unit_id)
    return {
        "id": prior.id,
        "unit": unit.name if unit else prior.auditable_unit_id,
        "raised_on": prior.raised_at.date().isoformat(),
        "category": prior.gap_category,
    }


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
    conn, audit_id: str, *, client=None, as_of: date | None = None,
    suggest_severity: bool = True,
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
    if audit.report_issued_at is not None:
        raise ValueError(
            f"{audit_id}'s report was already issued on "
            f"{audit.report_issued_at:%Y-%m-%d}; an issued report is not regenerated"
        )

    # Section 1: severity is finalised after the audit completes and
    # communicated in the report. So the suggestion is produced here, beside the
    # auditor's own assignment, immediately before the report that carries it.
    if suggest_severity:
        try:
            suggest_severities(conn, audit_id, client=client, as_of=as_of)
        except ValueError:
            # No taxonomy derived yet. The report is deterministic without the
            # suggestion and withholding the whole report over an advisory
            # extra would be the wrong trade.
            pass

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
        summary, cited, model, withheld = _draft_summary(
            conn, audit, findings, people, client=client
        )
        report.summary = summary
        report.summary_cited = cited
        report.model = model
        report.summary_withheld = withheld

    with simulated_clock(datetime.combine(as_of, time(16, 0))):
        report.generated_at = datetime.combine(as_of, time(16, 0))
        audit.report_generated_at = report.generated_at
        # A confirmation is of the version the auditor read. A new version
        # needs a new one.
        confirmation_cleared = audit.report_confirmed_at is not None
        audit.report_confirmed_at = None
        audit.report_confirmed_by = ""
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
                "summary_withheld_reasons": report.summary_withheld,
                "confirmation_cleared": confirmation_cleared,
                "prompt_version": PROMPT_VERSION,
                "model": report.model,
            },
            actor_identity=audit.auditor_identity,
        )
    return report


def _draft_summary(
    conn, audit: ScheduledAudit, findings: list[dict[str, Any]],
    people: Directory, *, client=None,
) -> tuple[str, list[str], str, list[str]]:
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
        return "", [], response.model, ["the model returned no summary"]

    known = {f["id"] for f in findings}
    problems = uncited_claims(summary, known)
    if problems:
        # Not published. Section 6 says every statement cites finding ids, and a
        # summary that does not is worse than none: it reads as authoritative.
        # The reasons travel onto the trail rather than vanishing.
        return "", [], response.model, problems
    cited = sorted({
        part.strip()
        for group in CITATION.findall(summary)
        for part in group.split(",")
    })
    return summary, cited, response.model, []


def confirm(
    conn, audit_id: str, *, by: str, as_of: date, remarks: str = "",
) -> ScheduledAudit:
    """The auditor reads the generated report and confirms it. Only then can it issue.

    Section 6: the auditor reviews and confirms before the report is issued.
    Until slice 16 that was a phrase in `issue`'s trail entry — "reviewed and
    confirmed by the auditor before issue" — written whether or not anybody had
    read a word. Confirmation is now its own act, by the auditor who conducted
    the audit, against the version they read: regenerating clears it.
    """
    from ..repositories import repositories, simulated_clock

    repo = repositories(conn)
    people = directory.load(conn)
    audit = repo["audits"].get(audit_id)
    if audit is None:
        raise ValueError(f"no such audit: {audit_id}")

    identity = people.get(by)
    authority.require(identity.role if identity else None, "conduct_audit",
                      actor_id=by)
    if by != audit.auditor_identity:
        raise authority.AuthorityError(
            f"{people.name(by)} did not conduct {audit_id}; its report is "
            f"confirmed by the auditor who did, {people.name(audit.auditor_identity)}"
        )
    if audit.report_generated_at is None:
        raise ValueError(
            f"{audit_id} has no generated report to confirm; generate it first"
        )
    if audit.report_issued_at is not None:
        raise ValueError(
            f"{audit_id}'s report was issued on {audit.report_issued_at:%Y-%m-%d}; "
            f"there is nothing left to confirm"
        )
    stamp = datetime.combine(as_of, time(16, 30))
    if stamp < audit.report_generated_at:
        raise ValueError(
            f"{audit_id}'s report was generated at {audit.report_generated_at}; it "
            f"cannot be confirmed before it existed"
        )

    with simulated_clock(stamp):
        audit.report_confirmed_at = stamp
        audit.report_confirmed_by = by
        repo["audits"].update(audit)
        repo["audit"].append(
            actor="user", owner=people.name(by), action="audit_report_confirmed",
            entity_type="ScheduledAudit", entity_id=audit.id,
            detail={
                "confirmed_by": by,
                "confirmed_at": stamp.isoformat(),
                "report_generated_at": audit.report_generated_at.isoformat(),
                "remarks": remarks,
            },
            actor_identity=by,
        )
    return audit


def issue(conn, audit_id: str, *, by: str, as_of: date) -> ScheduledAudit:
    """Issue a confirmed report. A PA/InfoSec act, never before confirmation."""
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
    if audit.report_confirmed_at is None:
        raise ValueError(
            f"{audit_id}'s report has not been confirmed by its auditor, "
            f"{people.name(audit.auditor_identity)}; it cannot be issued"
        )
    if audit.report_issued_at is not None:
        raise ValueError(
            f"{audit_id}'s report was already issued on "
            f"{audit.report_issued_at:%Y-%m-%d}"
        )
    stamp = datetime.combine(as_of, time(17, 0))
    if stamp < audit.report_confirmed_at:
        raise ValueError(
            f"{audit_id}'s report cannot be issued before it was confirmed "
            f"({audit.report_confirmed_at})"
        )

    with simulated_clock(stamp):
        audit.report_issued_at = stamp
        audit.report_issued_by = by
        repo["audits"].update(audit)
        repo["audit"].append(
            actor="user", owner=people.name(by), action="audit_report_issued",
            entity_type="ScheduledAudit", entity_id=audit.id,
            detail={
                "issued_by": by,
                "issued_at": stamp.isoformat(),
                "confirmed_by": audit.report_confirmed_by,
                "confirmed_at": audit.report_confirmed_at.isoformat(),
                "findings": len(findings_of(repo, audit.id)),
            },
            actor_identity=by,
        )
    return audit


def attach_status(conn, report: AuditReport) -> AuditReport:
    """Copy confirmation and issue off the record onto a report being rendered."""
    from ..repositories import repositories

    audit = repositories(conn)["audits"].get(report.audit_id)
    people = directory.load(conn)
    report.confirmed_at = audit.report_confirmed_at
    report.confirmed_by = (
        people.name(audit.report_confirmed_by) if audit.report_confirmed_by else ""
    )
    report.issued_at = audit.report_issued_at
    report.issued_by = (
        people.name(audit.report_issued_by) if audit.report_issued_by else ""
    )
    return report


def report_status(report: AuditReport) -> str:
    if report.issued_at:
        return (
            f"issued {report.issued_at:%Y-%m-%d} by {report.issued_by}, after "
            f"confirmation by {report.confirmed_by} on {report.confirmed_at:%Y-%m-%d}"
        )
    if report.confirmed_at:
        return (
            f"confirmed by {report.confirmed_by} on {report.confirmed_at:%Y-%m-%d}; "
            f"not yet issued"
        )
    return "draft, awaiting confirmation by the auditor"


def report_heading(report: AuditReport) -> str:
    """The title, prefixed with the audit kind only when it does not already say it."""
    kind = report.kind.replace("_", " ").title()
    title = report.title or report.audit_id
    return title if kind.lower() in title.lower() else f"{kind} — {title}"


def summary_note(report: AuditReport) -> str:
    """What the summary is, stated from the record rather than assumed.

    Until slice 16 this read "for the auditor to review and confirm before issue"
    on a report already issued, and the HTML page said "reviewed and confirmed"
    on one nobody had confirmed. It now says which of the three it is.
    """
    base = (
        f"Drafted from the findings below ({report.prompt_version}); every "
        f"statement cites the findings it rests on."
    )
    if report.issued_at:
        return f"{base} Confirmed by {report.confirmed_by} before issue."
    if report.confirmed_at:
        return f"{base} Confirmed by {report.confirmed_by}; not yet issued."
    return f"{base} A draft: the auditor reviews and confirms it before it can issue."


def render_markdown(report: AuditReport) -> str:
    """The report as it is emailed today, minus the emailing.

    Deterministic. The only generated text in here is `report.summary`, and it
    is labelled with whether the auditor has confirmed it.
    """
    out: list[str] = []
    add = out.append
    kind = report.kind.replace("_", " ").title()
    add(f"# {report_heading(report)}")
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
    add(f"| Report | {report_status(report)} |")
    add("")

    if report.summary:
        add("## Summary")
        add("")
        add(report.summary)
        add("")
        add(f"_{summary_note(report)}_")
    else:
        add("## Summary")
        add("")
        add(
            "_No narrative summary is attached. Either this audit raised no "
            "findings, or the drafted summary made a statement it could not "
            "attribute to one and was withheld._"
        )
        if report.summary_withheld:
            # Counted, not quoted: repeating a rejected statement here would
            # publish the claim that was withheld. The reasons are on the trail.
            add("")
            add(
                f"_{len(report.summary_withheld)} problem(s) were found with the "
                f"draft. They are recorded on the audit trail rather than quoted "
                f"here, because quoting a rejected statement would publish it._"
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
        if finding["recurrence_links"]:
            add(
                "**Recurrence.** Resembles "
                + "; ".join(
                    f"{link['id']} ({link['unit']}, raised {link['raised_on']})"
                    for link in finding["recurrence_links"]
                )
                + "."
            )
            add("")
    return "\n".join(out) + "\n"
