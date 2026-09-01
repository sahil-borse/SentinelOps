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
from ..entities import EvidenceSubmission
from ..pack import build as build_pack
from ..pack import load_events, render_html, render_markdown
from ..repositories import repositories, simulated_clock
from ..stages.assess import run as assess
from ..stages.flag import run as flag_stage
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
    actions_raised: int = 0
    actions_escalated: int = 0
    remediations_closed: int = 0

    def summary(self) -> str:
        return (
            f"{self.created} checks raised · {self.suppressed} suppressed by "
            f"exception · {self.resolved_by_rule} decided by rule · "
            f"{self.assessed} assessed by model ({self.model_calls} calls) · "
            f"{self.flags} flagged · {self.actions_raised} actions raised · "
            f"{self.actions_escalated} escalated · "
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
    return bool(repositories(conn)["areas"].list())


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
    result.actions_escalated = len(cycle.escalations)

    screen = prescreen(conn, as_of)
    result.screened = screen.considered
    result.resolved_by_rule = screen.resolved

    if screen.to_assess:
        report = assess(conn, screen.to_assess, as_of, client=client)
        result.assessed = len(report.assessed)
        result.model_calls = report.model_calls

    flags = flag_stage(conn, as_of)
    result.flags = len(flags.flags)
    result.actions_raised = len(flags.actions_raised)
    result.actions_escalated += len(flags.actions_escalated)

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
) -> EvidenceSubmission:
    """File a document against a check, as a team member would.

    Lands in the same staging table the synthetic corpus uses, so an uploaded
    document goes through exactly the same pre-screen and assessment as a
    generated one. Nothing about it is a special case.
    """
    repo = repositories(conn)
    instance = repo["instances"].get(instance_id)
    if instance is None:
        raise ValueError(f"no such check instance: {instance_id}")

    existing = len(repo["submissions"].list()) + 1
    submission = EvidenceSubmission(
        id=f"SUB-UI-{existing:04d}",
        control_id=instance.control_id,
        process_area_id=instance.process_area_id,
        period=instance.period,
        kind="structured" if doc_type.endswith(("_table", "_log", "_export")) else "document",
        doc_type=doc_type,
        content=content,
        content_hash=hashlib.sha256(content.encode()).hexdigest(),
        submitted_at=datetime.combine(as_of, time(9, 30)),
        author=author,
        is_remediation=is_remediation,
    )
    repo["submissions"].add(submission)
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


def counts(conn) -> dict[str, Any]:
    repo = repositories(conn)
    instances = repo["instances"].list()
    findings = repo["findings"].list()
    superseded = {f.supersedes_finding_id for f in findings if f.supersedes_finding_id}
    current = [f for f in findings if f.id not in superseded]
    flags = [f for f in repo["flags"].list() if f.status == "open"]
    return {
        "instances": len(instances),
        "assessed": len([i for i in instances if i.status == "assessed"]),
        "overdue": len([i for i in instances if i.status == "overdue"]),
        "waived": len([i for i in instances if i.status == "waived"]),
        "pending": len([i for i in instances if i.status == "pending"]),
        "findings": len(current),
        "non_compliant": len([f for f in current if f.verdict != "compliant"]),
        "needs_review": len([f for f in current if f.needs_human_review]),
        "flags_gap": len([f for f in flags if f.category == "gap"]),
        "flags_overdue": len([f for f in flags if f.category == "overdue"]),
        "flags_exception": len([f for f in flags if f.category == "exception"]),
        "actions_open": len(
            [a for a in repo["actions"].list() if a.status != "resolved"]
        ),
        "actions_resolved": len(
            [a for a in repo["actions"].list() if a.status == "resolved"]
        ),
        "audit_events": len(repo["audit"].read_all()),
    }
