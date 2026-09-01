"""The Audit Evidence Pack — reconstructed from the audit log and nothing else.

**The constraint is the product.** This module touches exactly one table,
`audit_events`. It never reads `findings`, `actions`, `check_instances`,
`flags`, `evidence`, `compliance_exceptions` or any other record of current
state, and `tests/test_pack.py` proves it two ways: statically, by asserting
this file names no live-state table and imports no repository; and at runtime,
by copying the audit log into an otherwise empty database and generating a
complete pack from it.

That is not a stylistic preference. A compliance system's claim to have an audit
trail is worth precisely what the trail can be made to produce on its own. If
the pack needed the findings table to show a finding, the trail would be an
index into the real records rather than a record itself — and the first question
an auditor asks is what happens when the records and the log disagree. Here they
cannot: there is one source.

Building it this way immediately found three holes, which is the point of
building it this way:

  * `finding_recorded` stored the *number* of cited spans rather than their
    text, so the log could say a verdict was cited but not what it cited;
  * exceptions that never lapsed produced no event at all, so an approved
    deviation existed only as a row somebody inserted;
  * instances recorded ids but no titles, so the log read in machine.

All three are fixed at source. The pack does not paper over them by reaching
into the tables.
"""

from __future__ import annotations

import html
import json
import sqlite3
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

from .entities import AuditEvent

#: Everything in the pack is derived from these actions. Listed explicitly so
#: that adding a stage without adding it here is a visible omission rather than
#: a quiet one.
KNOWN_ACTIONS = (
    "corpus_seeded",
    "exception_registered",
    "exception_expired",
    "cycle_started",
    "cycle_completed",
    "check_instance_created",
    "check_instance_submitted",
    "check_instance_overdue",
    "check_instance_waived",
    "check_instance_escalated",
    "evidence_bound",
    "remediation_submitted",
    "finding_recorded",
    "finding_superseded",
    "flag_raised",
    "flag_closed",
    "action_raised",
    "action_assigned",
    "action_in_progress",
    "action_remediation_submitted",
    "action_reassessed",
    "action_resolved",
    "action_escalated",
    "notification_logged",
    "prescreen_completed",
    "assessment_completed",
    "flagging_completed",
    "applicability_evaluated",
)


def load_events(
    conn: sqlite3.Connection,
    *,
    since: date | None = None,
    until: date | None = None,
) -> list[AuditEvent]:
    """Read the audit log. The only database access in this module.

    Deliberately raw SQL against one table rather than going through the
    repository layer: the point is that nothing here *can* reach current state,
    and importing a repository factory would make that a matter of discipline
    rather than of structure.
    """
    rows = conn.execute(
        "SELECT seq, ts, actor, owner, action, entity_type, entity_id, detail,"
        " prev_hash, entry_hash FROM audit_events ORDER BY seq"
    ).fetchall()
    events = []
    for row in rows:
        stamp = datetime.fromisoformat(row["ts"])
        if since and stamp.date() < since:
            continue
        if until and stamp.date() > until:
            continue
        events.append(
            AuditEvent(
                id=row["seq"], ts=stamp, actor=row["actor"], owner=row["owner"],
                action=row["action"], entity_type=row["entity_type"],
                entity_id=row["entity_id"], detail=json.loads(row["detail"]),
                seq=row["seq"], prev_hash=row["prev_hash"],
                entry_hash=row["entry_hash"],
            )
        )
    return events


def verify_chain(events: list[AuditEvent]) -> dict[str, Any]:
    """Re-verify the links over the events the pack was built from."""
    from .repositories import GENESIS_HASH, compute_entry_hash

    expected = GENESIS_HASH if not events or events[0].seq == 1 else events[0].prev_hash
    for position, event in enumerate(events):
        if event.prev_hash != expected:
            return {"ok": False, "broken_at": event.seq, "checked": position,
                    "reason": "predecessor link does not match"}
        if compute_entry_hash(event) != event.entry_hash:
            return {"ok": False, "broken_at": event.seq, "checked": position,
                    "reason": "entry contents do not match its hash"}
        expected = event.entry_hash
    return {"ok": True, "broken_at": None, "checked": len(events), "reason": ""}


@dataclass
class CoverageRow:
    area_id: str
    area_name: str
    control_id: str
    control_title: str
    frequency: str
    due: int = 0
    completed: int = 0
    waived: int = 0
    unexamined: int = 0


@dataclass
class AuditPack:
    organisation: str
    period_start: date
    period_end: date
    scope: str
    generated_at: datetime
    events: list[AuditEvent]
    coverage: list[CoverageRow] = field(default_factory=list)
    exceptions: list[dict[str, Any]] = field(default_factory=list)
    findings: list[dict[str, Any]] = field(default_factory=list)
    actions: list[dict[str, Any]] = field(default_factory=list)
    chain: dict[str, Any] = field(default_factory=dict)
    totals: dict[str, int] = field(default_factory=dict)
    unknown_actions: list[str] = field(default_factory=list)


def build(
    events: list[AuditEvent],
    *,
    organisation: str = "Northwind Group (fictional)",
    period_start: date,
    period_end: date,
    scope: str = "All process areas, all applicable controls",
) -> AuditPack:
    """Reconstruct the whole pack from a list of events. Pure; no I/O."""
    pack = AuditPack(
        organisation=organisation,
        period_start=period_start,
        period_end=period_end,
        scope=scope,
        generated_at=datetime.now(),
        events=events,
        chain=verify_chain(events),
    )

    instances: dict[str, dict[str, Any]] = {}
    coverage: dict[tuple[str, str], CoverageRow] = {}
    exceptions: dict[str, dict[str, Any]] = {}
    findings: dict[str, dict[str, Any]] = {}
    actions: dict[str, dict[str, Any]] = {}
    superseded: set[str] = set()
    seen_actions: set[str] = set()

    for event in events:
        seen_actions.add(event.action)
        detail = event.detail

        if event.action == "check_instance_created":
            instances[event.entity_id] = {
                "control_id": detail.get("control_id", "?"),
                "control_title": detail.get("control_title", detail.get("control_id", "?")),
                "area_id": detail.get("process_area_id", "?"),
                "area_name": detail.get("area_name", detail.get("process_area_id", "?")),
                "period": detail.get("period", "?"),
                "due_date": detail.get("due_date", ""),
                "frequency": detail.get("frequency", "?"),
                "owner": event.owner,
                "team": detail.get("assigned_team", ""),
                "status": "pending",
            }
            key = (detail.get("process_area_id", "?"), detail.get("control_id", "?"))
            row = coverage.setdefault(
                key,
                CoverageRow(
                    area_id=key[0],
                    area_name=detail.get("area_name", key[0]),
                    control_id=key[1],
                    control_title=detail.get("control_title", key[1]),
                    frequency=detail.get("frequency", "?"),
                ),
            )
            row.due += 1

        elif event.action == "check_instance_waived":
            if event.entity_id in instances:
                instances[event.entity_id]["status"] = "waived"

        elif event.action in ("check_instance_submitted", "check_instance_overdue"):
            if event.entity_id in instances:
                instances[event.entity_id]["status"] = event.action.removeprefix(
                    "check_instance_"
                )

        elif event.action == "exception_registered":
            exceptions[event.entity_id] = {
                "id": event.entity_id,
                "control_id": detail.get("control_id", "?"),
                "area_id": detail.get("process_area_id", "?"),
                "rationale": detail.get("rationale", ""),
                "approved_by": detail.get("approved_by", event.owner),
                "granted_at": detail.get("granted_at", ""),
                "expires_at": detail.get("expires_at", ""),
                "status": detail.get("status_at_registration", "active"),
                "lapsed_on": None,
                "detected_on": None,
            }

        elif event.action == "exception_expired":
            record = exceptions.setdefault(event.entity_id, {
                "id": event.entity_id, "control_id": detail.get("control_id", "?"),
                "area_id": detail.get("process_area_id", "?"), "rationale": "",
                "approved_by": "", "granted_at": "", "expires_at": "",
                "status": "expired", "lapsed_on": None, "detected_on": None,
            })
            record["status"] = "lapsed"
            record["lapsed_on"] = detail.get("expired_on", "")
            record["detected_on"] = detail.get("detected_on", "")

        elif event.action == "finding_recorded":
            instance_id = detail.get("check_instance_id", "")
            findings[event.entity_id] = {
                "id": event.entity_id,
                "instance_id": instance_id,
                "control_id": detail.get("control_id", ""),
                "area_id": detail.get("process_area_id", ""),
                "period": detail.get("period", ""),
                "verdict": detail.get("verdict", "?"),
                "confidence": detail.get("confidence", ""),
                "rationale": detail.get("rationale", ""),
                "cited_spans": detail.get("cited_spans", []),
                "gaps": detail.get("gaps", []),
                "needs_human_review": detail.get("needs_human_review", False),
                "decided_by": detail.get("decided_by", "?"),
                "model": detail.get("model", ""),
                "prompt_version": detail.get("prompt_version", ""),
                "criteria_hash": detail.get("criteria_hash", ""),
                "evidence_hash": detail.get("evidence_hash", ""),
                "recorded_at": event.ts,
                "owner": event.owner,
                "superseded_by": None,
            }
            if instance_id in instances:
                instances[instance_id]["status"] = "completed"

        elif event.action == "finding_superseded":
            superseded.add(event.entity_id)
            if event.entity_id in findings:
                findings[event.entity_id]["superseded_by"] = detail.get("superseded_by")

        elif event.action == "action_raised":
            actions[event.entity_id] = {
                "id": event.entity_id,
                "instance_id": detail.get("check_instance_id", ""),
                "finding_id": detail.get("finding_id", ""),
                "category": detail.get("category", "?"),
                "severity": detail.get("severity", ""),
                "band": detail.get("severity_band", ""),
                "raised_at": event.ts,
                "owner": event.owner,
                "team": "",
                "due_date": detail.get("due_date", ""),
                "status": "raised",
                "remediation_evidence": None,
                "reassessed_verdict": None,
                "resolution_note": None,
                "resolved_at": None,
                "history": [(event.ts, "raised", event.owner)],
            }

        elif event.action.startswith("action_") and event.entity_id in actions:
            record = actions[event.entity_id]
            state = event.action.removeprefix("action_")
            record["status"] = state
            record["history"].append((event.ts, state, event.owner))
            if state == "assigned":
                record["team"] = detail.get("owner_team", record["team"])
            elif state == "remediation_submitted":
                record["remediation_evidence"] = detail.get("evidence_id")
            elif state == "reassessed":
                record["reassessed_verdict"] = detail.get("verdict")
            elif state == "resolved":
                record["resolution_note"] = detail.get("resolution_note")
                record["resolved_at"] = event.ts

    for instance in instances.values():
        key = (instance["area_id"], instance["control_id"])
        row = coverage.get(key)
        if row is None:
            continue
        if instance["status"] == "waived":
            row.waived += 1
        elif instance["status"] == "completed":
            row.completed += 1
        else:
            row.unexamined += 1

    for finding in findings.values():
        finding["is_current"] = finding["id"] not in superseded

    pack.coverage = sorted(coverage.values(), key=lambda r: (r.area_id, r.control_id))
    pack.exceptions = sorted(exceptions.values(), key=lambda e: e["id"])
    pack.findings = sorted(findings.values(), key=lambda f: f["id"])
    pack.actions = sorted(actions.values(), key=lambda a: a["id"])
    pack.unknown_actions = sorted(seen_actions - set(KNOWN_ACTIONS))
    current = [f for f in pack.findings if f["is_current"]]
    pack.totals = {
        "events": len(events),
        "instances": len(instances),
        "areas": len({i["area_id"] for i in instances.values()}),
        "controls": len({i["control_id"] for i in instances.values()}),
        "due": sum(r.due for r in pack.coverage),
        "completed": sum(r.completed for r in pack.coverage),
        "waived": sum(r.waived for r in pack.coverage),
        "unexamined": sum(r.unexamined for r in pack.coverage),
        "findings": len(pack.findings),
        "current_findings": len(current),
        "superseded_findings": len(superseded),
        "non_compliant": len([f for f in current if f["verdict"] != "compliant"]),
        "human_review": len([f for f in current if f["needs_human_review"]]),
        "decided_without_a_model": len(
            [f for f in current if not str(f["decided_by"]).startswith("s3_")]
        ),
        "exceptions": len(pack.exceptions),
        "actions": len(pack.actions),
        "actions_resolved": len(
            [a for a in pack.actions if a["status"] == "resolved"]
        ),
    }
    return pack


METHOD_NOTE = """
This pack was assembled from the append-only audit log and from nothing else. No
current-state table was read: not the findings, not the actions, not the check
register. Every figure, register and excerpt below was reconstructed by replaying
the events in sequence. If the log could not support a section, that section
would be missing rather than quietly filled in from elsewhere.

**How checks arise.** Each control carries an applicability expression over
process-area attributes. A control applies to an area when every attribute it
names matches; that decision is deterministic and involves no model. Instances
are generated from the control's frequency across the calendar and keyed on
control x area x period, so a cycle run twice produces no duplicates.

**How evidence is judged.** Four rules resolve what can be resolved before any
model is asked: no evidence, wrong document type, evidence unchanged since a
period already assessed, and evidence older than the control's freshness window.
Structured evidence is measured against numeric thresholds in code. Only
ambiguous prose reaches a model, and then exactly once, with the relevant
sections retrieved rather than the whole document. Every quoted span in a model
verdict is checked back against the source; a verdict citing text the document
does not contain is rejected rather than recorded.

**What is deterministic and what is not.** Applicability, scheduling,
escalation, the pre-screen rules, threshold evaluation, severity and routing are
code and produce the same answer every time. Only the assessment of prose
involves a model. Findings record which tier decided them, and rule-decided
findings carry a confidence of 1.0 because arithmetic against a stated threshold
is certain in a way a reading of a paragraph is not.

**Integrity.** Each log entry carries a sequence number, the hash of the entry
before it, and its own hash covering that link. Altering any entry breaks the
chain at that point and every point after. The verification result is printed on
the cover. This makes tampering evident; it does not make it impossible.

**Scope of the evidence.** This is a demonstration system running on a
synthetic, seeded corpus of a fictional organisation. The controls, areas,
evidence and outcomes are generated, not collected.
"""


def render_markdown(pack: AuditPack) -> str:
    """The pack as markdown, for a terminal or a diff."""
    lines: list[str] = []
    add = lines.append

    add(f"# Audit Evidence Pack — {pack.organisation}")
    add("")
    add(f"**Period covered** {pack.period_start} to {pack.period_end}  ")
    add(f"**Scope** {pack.scope}  ")
    add(f"**Generated** {pack.generated_at:%Y-%m-%d %H:%M:%S}  ")
    add(f"**Source** append-only audit log, {pack.totals['events']:,} events  ")
    chain = pack.chain
    verdict = (
        f"VERIFIED — {chain['checked']:,} entries, chain intact"
        if chain["ok"]
        else f"FAILED at sequence {chain['broken_at']} — {chain['reason']}"
    )
    add(f"**Chain integrity** {verdict}")
    add("")
    add("| | |")
    add("|---|---|")
    for label, key in (
        ("Process areas", "areas"), ("Controls exercised", "controls"),
        ("Checks due", "due"), ("Checks completed", "completed"),
        ("Checks waived", "waived"), ("Checks not examined", "unexamined"),
        ("Findings recorded", "findings"),
        ("Findings superseded by re-assessment", "superseded_findings"),
        ("Current non-compliant findings", "non_compliant"),
        ("Flagged for human review", "human_review"),
        ("Decided without a model call", "decided_without_a_model"),
        ("Exceptions on register", "exceptions"),
        ("Actions raised", "actions"), ("Actions resolved", "actions_resolved"),
    ):
        add(f"| {label} | {pack.totals[key]:,} |")
    add("")

    add("## 1. Coverage")
    add("")
    add("| Area | Control | Frequency | Due | Completed | Waived | Not examined |")
    add("|---|---|---|---|---|---|---|")
    for row in pack.coverage:
        add(
            f"| {row.area_name} | {row.control_title} | {row.frequency} | {row.due} "
            f"| {row.completed} | {row.waived} | {row.unexamined} |"
        )
    add("")

    add("## 2. Exception register")
    add("")
    add("| Reference | Control | Area | Approved by | Granted | Expires | Status |")
    add("|---|---|---|---|---|---|---|")
    for exception in pack.exceptions:
        add(
            f"| {exception['id']} | {exception['control_id']} | {exception['area_id']} "
            f"| {exception['approved_by']} | {exception['granted_at']} "
            f"| {exception['expires_at']} | {exception['status']} |"
        )
    add("")
    for exception in pack.exceptions:
        add(f"**{exception['id']}** — {exception['rationale']}")
        if exception["lapsed_on"]:
            add(
                f"  Lapsed {exception['lapsed_on']}, detected "
                f"{exception['detected_on']}; the control returned to the schedule."
            )
        add("")

    add("## 3. Findings register")
    add("")
    for finding in pack.findings:
        if not finding["is_current"] and not finding["superseded_by"]:
            continue
        status = (
            f" *(superseded by {finding['superseded_by']})*"
            if finding["superseded_by"] else ""
        )
        add(f"### {finding['id']}{status}")
        add("")
        add(
            f"- **Check** {finding['instance_id']}  \n"
            f"- **Verdict** `{finding['verdict']}` · confidence "
            f"{finding['confidence']} · decided by `{finding['decided_by']}`  \n"
            f"- **Human review** {'yes' if finding['needs_human_review'] else 'no'}  \n"
            f"- **Recorded** {finding['recorded_at']:%Y-%m-%d} by {finding['owner']}"
        )
        if finding["rationale"]:
            add(f"- **Rationale** {finding['rationale']}")
        for span in finding["cited_spans"]:
            add(f"- **Cited evidence** > {span}")
        for gap in finding["gaps"]:
            add(f"- **Gap** {gap}")
        if finding["prompt_version"]:
            add(
                f"- **Provenance** prompt `{finding['prompt_version']}` · criteria "
                f"`{finding['criteria_hash']}` · evidence `{finding['evidence_hash']}`"
            )
        add("")

    add("## 4. Action register")
    add("")
    for action in pack.actions:
        add(f"### {action['id']} — {action['status']}")
        add("")
        add(
            f"- **Raised** {action['raised_at']:%Y-%m-%d} from {action['finding_id']} "
            f"({action['category']}, severity {action['severity']} "
            f"{action['band']})  \n"
            f"- **Owner** {action['owner']} ({action['team']}) · due "
            f"{action['due_date']}"
        )
        if action["remediation_evidence"]:
            add(f"- **Remediation submitted** {action['remediation_evidence']}")
        if action["reassessed_verdict"]:
            add(f"- **Re-assessed** {action['reassessed_verdict']}")
        if action["resolution_note"]:
            add(
                f"- **Closed** {action['resolved_at']:%Y-%m-%d} — "
                f"{action['resolution_note']}"
            )
        add(
            "- **History** "
            + " → ".join(f"{state} ({owner})" for _, state, owner in action["history"])
        )
        add("")

    add("## 5. Method note")
    add(METHOD_NOTE)
    add("")

    add("## 6. Chronological trail")
    add("")
    add(f"{pack.totals['events']:,} events, in the order they were written.")
    add("")
    add("| # | Timestamp | Actor | Owner | Event | Entity |")
    add("|---|---|---|---|---|---|")
    for event in pack.events:
        add(
            f"| {event.seq} | {event.ts:%Y-%m-%d %H:%M:%S} | {event.actor} "
            f"| {event.owner} | {event.action} | {event.entity_type}:{event.entity_id} |"
        )
    return "\n".join(lines)


_CSS = """
:root { color-scheme: light; }
body { font: 15px/1.55 -apple-system, Segoe UI, Roboto, Helvetica, sans-serif;
       margin: 0 auto; max-width: 1000px; padding: 2.5rem 1.5rem; color: #1a1a1a; }
h1 { font-size: 1.9rem; margin-bottom: .2rem; }
h2 { margin-top: 2.5rem; border-bottom: 2px solid #1a1a1a; padding-bottom: .3rem; }
h3 { margin-top: 1.6rem; font-size: 1.05rem; font-family: ui-monospace, monospace; }
table { border-collapse: collapse; width: 100%; margin: 1rem 0; font-size: .88rem; }
th, td { border: 1px solid #d4d4d4; padding: .35rem .55rem; text-align: left;
         vertical-align: top; }
th { background: #f2f2f2; font-weight: 600; }
tr:nth-child(even) td { background: #fafafa; }
.cover { background: #f7f7f5; border: 1px solid #ddd; padding: 1rem 1.25rem;
         margin: 1.5rem 0; }
.ok { color: #0a6b32; font-weight: 600; }
.bad { color: #a11; font-weight: 600; }
.cite { border-left: 3px solid #888; background: #f7f7f5; padding: .4rem .7rem;
        margin: .35rem 0; font-family: ui-monospace, monospace; font-size: .84rem;
        white-space: pre-wrap; }
.gap { color: #8a4b00; }
.meta { color: #555; font-size: .84rem; }
.trail { max-height: 30rem; overflow-y: auto; border: 1px solid #ddd; }
.badge { display: inline-block; padding: .05rem .45rem; border-radius: 3px;
         font-size: .78rem; font-family: ui-monospace, monospace; }
.v-gap { background: #fde8e8; } .v-compliant { background: #e6f4ea; }
.v-partial { background: #fff4d6; } .v-insufficient_evidence { background: #ececec; }
.note { white-space: pre-wrap; background: #f7f7f5; border: 1px solid #ddd;
        padding: 1rem 1.25rem; }
"""


def render_html(pack: AuditPack) -> str:
    """The pack as a self-contained page, for the screen."""
    e = html.escape
    chain = pack.chain
    chain_html = (
        f'<span class="ok">VERIFIED — {chain["checked"]:,} entries, chain intact</span>'
        if chain["ok"]
        else f'<span class="bad">FAILED at sequence {chain["broken_at"]} — '
             f'{e(chain["reason"])}</span>'
    )
    out: list[str] = [
        "<!doctype html><html><head><meta charset='utf-8'>",
        f"<title>Audit Evidence Pack — {e(pack.organisation)}</title>",
        f"<style>{_CSS}</style></head><body>",
        f"<h1>Audit Evidence Pack</h1>",
        f"<p class='meta'>{e(pack.organisation)}</p>",
        "<div class='cover'>",
        f"<div><strong>Period covered</strong> {pack.period_start} to {pack.period_end}</div>",
        f"<div><strong>Scope</strong> {e(pack.scope)}</div>",
        f"<div><strong>Generated</strong> {pack.generated_at:%Y-%m-%d %H:%M:%S}</div>",
        f"<div><strong>Source</strong> append-only audit log, "
        f"{pack.totals['events']:,} events — no current-state table was read</div>",
        f"<div><strong>Chain integrity</strong> {chain_html}</div>",
        "</div>",
        "<table>",
    ]
    for label, key in (
        ("Process areas", "areas"), ("Controls exercised", "controls"),
        ("Checks due", "due"), ("Checks completed", "completed"),
        ("Checks waived", "waived"), ("Checks not examined", "unexamined"),
        ("Findings recorded", "findings"),
        ("Findings superseded by re-assessment", "superseded_findings"),
        ("Current non-compliant findings", "non_compliant"),
        ("Flagged for human review", "human_review"),
        ("Decided without a model call", "decided_without_a_model"),
        ("Exceptions on register", "exceptions"),
        ("Actions raised", "actions"), ("Actions resolved", "actions_resolved"),
    ):
        out.append(f"<tr><th>{label}</th><td>{pack.totals[key]:,}</td></tr>")
    out.append("</table>")

    out.append("<h2>1. Coverage</h2><table><tr><th>Area</th><th>Control</th>"
               "<th>Frequency</th><th>Due</th><th>Completed</th><th>Waived</th>"
               "<th>Not examined</th></tr>")
    for row in pack.coverage:
        out.append(
            f"<tr><td>{e(row.area_name)}</td><td>{e(row.control_title)}</td>"
            f"<td>{row.frequency}</td><td>{row.due}</td><td>{row.completed}</td>"
            f"<td>{row.waived}</td><td>{row.unexamined}</td></tr>"
        )
    out.append("</table>")

    out.append("<h2>2. Exception register</h2><table><tr><th>Reference</th>"
               "<th>Control</th><th>Area</th><th>Approved by</th><th>Granted</th>"
               "<th>Expires</th><th>Status</th><th>Rationale</th></tr>")
    for exception in pack.exceptions:
        lapsed = (
            f"<br><span class='meta'>lapsed {exception['lapsed_on']}, detected "
            f"{exception['detected_on']}</span>" if exception["lapsed_on"] else ""
        )
        out.append(
            f"<tr><td>{e(exception['id'])}</td><td>{e(exception['control_id'])}</td>"
            f"<td>{e(exception['area_id'])}</td><td>{e(exception['approved_by'])}</td>"
            f"<td>{exception['granted_at']}</td><td>{exception['expires_at']}</td>"
            f"<td>{e(exception['status'])}{lapsed}</td>"
            f"<td>{e(exception['rationale'])}</td></tr>"
        )
    out.append("</table>")

    out.append("<h2>3. Findings register</h2>")
    for finding in pack.findings:
        if not finding["is_current"] and not finding["superseded_by"]:
            continue
        superseded = (
            f" <span class='meta'>superseded by {e(str(finding['superseded_by']))}</span>"
            if finding["superseded_by"] else ""
        )
        out.append(f"<h3>{e(finding['id'])}{superseded}</h3>")
        out.append(
            f"<p><span class='badge v-{e(str(finding['verdict']))}'>"
            f"{e(str(finding['verdict']))}</span> "
            f"confidence {finding['confidence']} · decided by "
            f"<code>{e(str(finding['decided_by']))}</code> · human review "
            f"<strong>{'yes' if finding['needs_human_review'] else 'no'}</strong>"
            f"<br><span class='meta'>{e(finding['instance_id'])} · recorded "
            f"{finding['recorded_at']:%Y-%m-%d} by {e(finding['owner'])}</span></p>"
        )
        if finding["rationale"]:
            out.append(f"<p>{e(finding['rationale'])}</p>")
        for span in finding["cited_spans"]:
            out.append(f"<div class='cite'>{e(str(span))}</div>")
        for gap in finding["gaps"]:
            out.append(f"<p class='gap'>Gap: {e(str(gap))}</p>")
        if finding["prompt_version"]:
            out.append(
                f"<p class='meta'>prompt <code>{e(finding['prompt_version'])}</code> · "
                f"criteria <code>{e(finding['criteria_hash'])}</code> · evidence "
                f"<code>{e(finding['evidence_hash'])}</code></p>"
            )
    out.append("<h2>4. Action register</h2><table><tr><th>Action</th><th>Found</th>"
               "<th>Owner</th><th>Raised</th><th>Due</th><th>Remediation</th>"
               "<th>Re-assessed</th><th>Closed</th></tr>")
    for action in pack.actions:
        out.append(
            f"<tr><td>{e(action['id'])}<br><span class='meta'>{e(action['status'])}"
            f"</span></td>"
            f"<td>{e(action['category'])} · severity {action['severity']}"
            f"<br><span class='meta'>{e(action['finding_id'])}</span></td>"
            f"<td>{e(action['owner'])}<br><span class='meta'>{e(action['team'])}</span></td>"
            f"<td>{action['raised_at']:%Y-%m-%d}</td><td>{action['due_date']}</td>"
            f"<td>{e(str(action['remediation_evidence'] or '—'))}</td>"
            f"<td>{e(str(action['reassessed_verdict'] or '—'))}</td>"
            f"<td>{e(str(action['resolution_note'] or '—'))}</td></tr>"
        )
    out.append("</table>")

    out.append(f"<h2>5. Method note</h2><div class='note'>{e(METHOD_NOTE.strip())}</div>")

    out.append(f"<h2>6. Chronological trail</h2><p class='meta'>"
               f"{pack.totals['events']:,} events, in the order they were written."
               f"</p><div class='trail'><table><tr><th>#</th><th>Timestamp</th>"
               f"<th>Actor</th><th>Owner</th><th>Event</th><th>Entity</th></tr>")
    for event in pack.events:
        out.append(
            f"<tr><td>{event.seq}</td><td>{event.ts:%Y-%m-%d %H:%M:%S}</td>"
            f"<td>{e(event.actor)}</td><td>{e(event.owner)}</td>"
            f"<td>{e(event.action)}</td>"
            f"<td>{e(event.entity_type)}:{e(event.entity_id)}</td></tr>"
        )
    out.append("</table></div></body></html>")
    return "\n".join(out)
