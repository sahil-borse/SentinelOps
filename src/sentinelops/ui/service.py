"""Everything the buttons do. No Streamlit here either.

The UI is a thin caller: each control on the screen maps to one function in this
module, so what the dashboard can do is exactly what can be tested. It also
means the demo cannot drift from the engine — "run cycle" here is the same
`run_cycle` cron would call, not a UI-flavoured reimplementation of it.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Any

from ..db import connect
from ..entities import InboundSubmission
from ..pack import build as build_pack
from ..pack import load_events, render_html, render_markdown
from ..repositories import repositories, simulated_clock
from ..stages.assess import run as assess
from ..stages.flag import run as flag_stage
from ..stages.followup import run as followup_stage
from ..stages.prescreen import run as prescreen
from ..stages.remediation import reassess as reassess_instance
from ..stages.remediation import reassess_all
from ..stages.trigger import run_cycle
from ..synth import generate_corpus, seed_database

ROOT = Path(__file__).resolve().parents[3]
DB_PATH = ROOT / "data" / "demo" / "sentinelops.db"
PACK_DIR = ROOT / "data" / "packs"

#: Where the simulated calendar starts when the demo is first opened.
START_DATE = date(2026, 1, 28)


@dataclass
class TickResult:
    as_of: date
    created: int = 0
    suppressed: int = 0
    screened: int = 0
    resolved_by_rule: int = 0
    assessed: int = 0
    model_calls: int = 0
    flags: int = 0
    findings_raised: int = 0
    reminders_sent: int = 0
    escalations: int = 0
    remediations_closed: int = 0

    def summary(self) -> str:
        return (
            f"{self.created} checks raised · {self.suppressed} suppressed by "
            f"exception · {self.resolved_by_rule} decided by rule · "
            f"{self.assessed} assessed by model ({self.model_calls} calls) · "
            f"{self.flags} flagged · {self.findings_raised} findings raised · "
            f"{self.reminders_sent} chased · {self.escalations} escalated · "
            f"{self.remediations_closed} remediations closed"
        )


def open_database(path: Path | None = None, *, fresh: bool = False):
    """A file-backed database, so the demo survives a page reload.

    Thread checking is off because Streamlit reruns the script on a different
    thread for every interaction and the connection is cached across those
    reruns. See `db.connect`.
    """
    target = Path(path or DB_PATH)
    target.parent.mkdir(parents=True, exist_ok=True)
    if fresh and target.exists():
        target.unlink()
    return connect(target, check_same_thread=False)


def is_seeded(conn) -> bool:
    return bool(repositories(conn)["units"].list())


def seed(conn) -> None:
    if not is_seeded(conn):
        seed_database(conn, generate_corpus())


def current_date(conn) -> date:
    """Where the simulated calendar stands, read off the trail."""
    from ..stages.trigger import last_cycle_date

    return last_cycle_date(conn) or START_DATE


def tick(conn, as_of: date, *, client=None) -> TickResult:
    """One full pass of the pipeline: S1 through S4, then close what can close.

    The same functions a scheduler would call, in the same order.
    """
    result = TickResult(as_of=as_of)

    cycle = run_cycle(conn, as_of, trigger="manual", actor="user")
    result.created = len(cycle.created)
    result.suppressed = len(cycle.suppressed)
    result.escalations = len(cycle.escalations)

    screen = prescreen(conn, as_of)
    result.screened = screen.considered
    result.resolved_by_rule = screen.resolved

    if screen.to_assess:
        report = assess(conn, screen.to_assess, as_of, client=client)
        result.assessed = len(report.assessed)
        result.model_calls = report.model_calls

    flags = flag_stage(conn, as_of)
    result.flags = len(flags.flags)
    result.findings_raised = len(flags.findings_raised)

    # The chasing engine. It runs every tick because that is the whole point of
    # it: a system that never forgets to follow up only earns that if it looks
    # every single cycle.
    chase = followup_stage(conn, as_of)
    result.reminders_sent = len(chase.reminded)
    result.escalations += len(chase.escalated)

    result.remediations_closed = len(reassess_all(conn, as_of, client=client))
    return result


def advance(conn, days: int, *, client=None) -> TickResult:
    """Move the calendar forward and run the cycle that falls due."""
    return tick(conn, current_date(conn) + timedelta(days=days), client=client)


def submit_evidence(
    conn,
    *,
    instance_id: str,
    filename: str,
    content: str,
    author: str,
    doc_type: str,
    as_of: date,
    is_remediation: bool = True,
) -> InboundSubmission:
    """File a document against a check, as a team member would.

    Lands in the same staging table the synthetic corpus uses, so an uploaded
    document goes through exactly the same pre-screen and assessment as a
    generated one. Nothing about it is a special case.
    """
    repo = repositories(conn)
    instance = repo["instances"].get(instance_id)
    if instance is None:
        raise ValueError(f"no such check instance: {instance_id}")

    existing = len(repo["inbound"].list()) + 1
    submission = InboundSubmission(
        id=f"SUB-UI-{existing:04d}",
        control_id=instance.control_id,
        auditable_unit_id=instance.auditable_unit_id,
        period=instance.period,
        kind="structured" if doc_type.endswith(("_table", "_log", "_export")) else "document",
        doc_type=doc_type,
        content=content,
        content_hash=hashlib.sha256(content.encode()).hexdigest(),
        submitted_at=datetime.combine(as_of, time(9, 30)),
        author=author,
        is_remediation=is_remediation,
    )
    repo["inbound"].add(submission)
    with simulated_clock(datetime.combine(as_of, time(9, 30))):
        repo["audit"].append(
            actor="user",
            owner=author,
            action="evidence_uploaded",
            entity_type="CheckInstance",
            entity_id=instance_id,
            detail={
                "submission_id": submission.id,
                "filename": filename,
                "doc_type": doc_type,
                "bytes": len(content.encode()),
                "content_hash": submission.content_hash[:12],
                "is_remediation": is_remediation,
                "source": "dashboard upload",
            },
        )
    return submission


def reassess(conn, instance_id: str, as_of: date, *, client=None):
    """Re-check one instance now, rather than waiting for the next cycle."""
    return reassess_instance(conn, instance_id, as_of, client=client)


def doc_types_for(conn, instance_id: str) -> list[str]:
    """What the control accepts, plus the other types, so a mistake is possible.

    Offering only the correct type would hide the wrong-type rule, which is one
    of the things worth showing.
    """
    repo = repositories(conn)
    instance = repo["instances"].get(instance_id)
    accepted = repo["controls"].get(instance.control_id).required_evidence_types
    others = sorted(
        {
            kind
            for control in repo["controls"].list()
            for kind in control.required_evidence_types
        }
        - set(accepted)
    )
    return list(accepted) + others


def generate_pack(conn, *, period_start: date, period_end: date, scope: str):
    """Build the auditor-ready pack from the audit log and write both formats."""
    events = load_events(conn)
    pack = build_pack(
        events, period_start=period_start, period_end=period_end, scope=scope
    )
    PACK_DIR.mkdir(parents=True, exist_ok=True)
    markdown, page = render_markdown(pack), render_html(pack)
    (PACK_DIR / "audit_pack_2026.md").write_text(markdown, encoding="utf-8")
    (PACK_DIR / "audit_pack_2026.html").write_text(page, encoding="utf-8")
    return pack, markdown, page


def verify_chain(conn):
    return repositories(conn)["audit"].verify_chain()


def identities(conn) -> list[dict[str, Any]]:
    """Everyone the identity selector can act as.

    Section 11 is explicit that this is an identity selector and not auth: there
    is no login and nothing is being protected from the person at the keyboard.
    What it is for is making segregation of duties *visible* — pick an owner and
    the Close control is not there.
    """
    from .. import authority, directory

    people = directory.load(conn)
    rows = []
    for identity in sorted(people.all(), key=lambda i: (i.role, i.name)):
        rows.append({
            "id": identity.id,
            "name": identity.name,
            "role": identity.role,
            "unit": identity.auditable_unit or "",
            "may": authority.actions_for(identity.role),
        })
    return rows


def acting_as(conn, identity_id: str) -> dict[str, Any]:
    from .. import authority, directory

    identity = directory.load(conn).get(identity_id)
    role = identity.role if identity else None
    return {
        "id": identity_id,
        "name": identity.name if identity else identity_id,
        "role": role,
        "unit": identity.auditable_unit if identity else "",
        "may_close": bool(authority.permitted(role, "close_finding")),
        "may_respond": bool(authority.permitted(role, "respond_to_submission")),
        "may_submit": bool(authority.permitted(role, "submit_evidence")),
    }


def close_finding(conn, finding_id: str, *, by: str, remarks: str):
    """Close a finding as `by`. Refusals come back as text, not a stack trace."""
    from .. import authority
    from ..repositories import simulated_clock
    from ..stages import followup

    as_of = current_date(conn)
    try:
        with simulated_clock(datetime.combine(as_of, time(12, 0))):
            finding = followup.close_finding(
                conn, finding_id, by=by, remarks=remarks, as_of=as_of
            )
    except (authority.AuthorityError, ValueError) as refusal:
        return False, str(refusal)
    return True, (
        f"{finding.id} closed by {finding.closed_by} after "
        f"{finding.follow_up_count} follow-up(s)."
    )


def open_rounds(conn, finding_id: str) -> list[dict[str, Any]]:
    """The review rounds on a finding, as the screen shows them."""
    from .. import directory
    from ..repositories import repositories
    from ..stages import rounds as rounds_module

    people = directory.load(conn)
    return [
        {
            "id": r.id,
            "round": r.round_number,
            "submitted_by": people.name(r.submitted_by),
            "submitted_at": r.submitted_at,
            "evidence_ref": r.evidence_ref,
            "response": r.auditor_response,
            "remarks": r.auditor_remarks,
            "responded_by": people.name(r.responded_by) if r.responded_by else "",
        }
        for r in rounds_module.rounds_for(repositories(conn), finding_id)
    ]


def counts(conn) -> dict[str, Any]:
    repo = repositories(conn)
    instances = repo["instances"].list()
    findings = repo["assessments"].list()
    superseded = {f.supersedes_assessment_id for f in findings if f.supersedes_assessment_id}
    current = [f for f in findings if f.id not in superseded]
    flags = [f for f in repo["flags"].list() if f.status == "open"]
    return {
        "instances": len(instances),
        "assessed": len([i for i in instances if i.status == "assessed"]),
        "overdue": len([i for i in instances if i.status == "overdue"]),
        "waived": len([i for i in instances if i.status == "waived"]),
        "pending": len([i for i in instances if i.status == "pending"]),
        "assessments": len(current),
        "non_compliant": len([f for f in current if f.verdict != "compliant"]),
        "needs_review": len([f for f in current if f.needs_human_review]),
        "flags_gap": len([f for f in flags if f.category == "gap"]),
        "flags_overdue": len([f for f in flags if f.category == "overdue"]),
        "flags_exception": len([f for f in flags if f.category == "exception"]),
        "actions_open": len(
            [f for f in repo["findings"].list() if f.status == "open"]
        ),
        "actions_resolved": len(
            [f for f in repo["findings"].list() if f.status == "closed"]
        ),
        "audit_events": len(repo["audit"].read_all()),
    }
