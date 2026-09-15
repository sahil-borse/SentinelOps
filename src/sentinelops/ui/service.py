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
from ..stages import intelligence, taxonomy
from ..stages.prescreen import run as prescreen
from ..stages.remediation import reassess as reassess_instance
from ..stages.remediation import reassess_all
from ..stages.trigger import run_cycle
from ..synth import generate_corpus, seed_database

ROOT = Path(__file__).resolve().parents[3]
DB_PATH = ROOT / "data" / "demo" / "sentinelops.db"
PACK_DIR = ROOT / "data" / "packs"

#: Where the simulated calendar starts when the demo is first opened is now
#: `start_date(conn)`, read from the schedule window. It used to be
#: `START_DATE = date(2026, 1, 28)`, a year written into the dashboard.


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
    classified: int = 0
    recurrences_found: int = 0
    remediations_closed: int = 0

    def summary(self) -> str:
        return (
            f"{self.created} checks raised · {self.suppressed} suppressed by "
            f"exception · {self.resolved_by_rule} decided by rule · "
            f"{self.assessed} assessed by model ({self.model_calls} calls) · "
            f"{self.flags} flagged · {self.findings_raised} findings raised · "
            f"{self.classified} classified · "
            f"{self.recurrences_found} recurrence link(s) · "
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


def start_date(conn) -> date:
    """The first monthly cycle in the schedule window the corpus recorded."""
    from .. import window as schedule_window
    from ..periods import monthly_cycles

    window = schedule_window.load(conn)
    return monthly_cycles(window, window.end)[0]


def current_date(conn) -> date:
    """Where the simulated calendar stands, read off the trail."""
    from ..stages.trigger import last_cycle_date

    return last_cycle_date(conn) or start_date(conn)


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

    # Section 2's advisory uses, last, because nothing downstream reads them.
    # Both are idempotent: a finding already classified is skipped, and one
    # already linked is not re-examined, so a second tick on the same day
    # spends nothing on either.
    # The taxonomy is derived from the corpus, not hardcoded, so it has to
    # exist before anything can be classified against it. Idempotent: a second
    # press of the button spends nothing.
    taxonomy.derive(conn, as_of, client=client)
    triage = intelligence.classify(conn, as_of, client=client)
    result.classified = len(triage.classified)
    result.model_calls += triage.model_calls

    recurrence = intelligence.detect_recurrence(conn, as_of, client=client)
    result.recurrences_found = len(recurrence.linked)
    result.model_calls += recurrence.model_calls
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


def pack_period(conn) -> tuple[date, date]:
    """From the start of the schedule window to where the calendar stands.

    Replaces `date(2026, 1, 1)` to `date(2026, 12, 31)`, which the dashboard and
    the walkthrough both passed whatever the calendar said.
    """
    from .. import window as schedule_window

    return schedule_window.load(conn).start, current_date(conn)


def pack_file_name(conn) -> str:
    """The download name for the pack the dashboard offers, without an extension."""
    from ..pack import pack_filename

    return pack_filename(*pack_period(conn))


def generate_pack(conn, *, period_start: date, period_end: date, scope: str):
    """Build the auditor-ready pack from the audit log and write both formats."""
    from ..pack import pack_filename

    events = load_events(conn)
    pack = build_pack(
        events, period_start=period_start, period_end=period_end, scope=scope
    )
    PACK_DIR.mkdir(parents=True, exist_ok=True)
    markdown, page = render_markdown(pack), render_html(pack)
    name = pack_filename(period_start, period_end)
    (PACK_DIR / f"{name}.md").write_text(markdown, encoding="utf-8")
    (PACK_DIR / f"{name}.html").write_text(page, encoding="utf-8")
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


def brief(conn, *, client=None):
    """The prioritisation brief for the current cycle. One call, advisory."""
    from ..stages import intelligence as intel

    return intel.prioritisation_brief(conn, current_date(conn), client=client)


def default_identity(conn) -> str:
    """Who the dashboard opens as: the first PA/InfoSec auditor.

    The landing page is their morning screen, so the demo starts there. Anyone
    else is one choice away in the identity selector.
    """
    from .. import directory

    people = directory.load(conn)
    auditors = people.by_role("pa_infosec")
    return auditors[0].id if auditors else people.all()[0].id


def open_evidence_round(
    conn, finding_id: str, *, by: str, evidence_ref: str, evidence_text: str,
    note: str = "",
) -> tuple[bool, str]:
    """A unit owner files evidence on one of their unit's findings.

    The round is opened through `stages.rounds`, which checks the role; the unit
    is checked here too, because "own unit only" is a scope rule the role table
    cannot express. An advisory reading is attached for the auditor straight
    away. If that reading cannot be made, the filing still stands — the owner's
    evidence is not lost because a model call failed — and the message says so.
    """
    from .. import authority, directory
    from ..stages import review
    from ..stages import rounds as rounds_stage

    repo = repositories(conn)
    people = directory.load(conn)
    as_of = current_date(conn)
    finding = repo["findings"].get(finding_id)
    if finding is None:
        return False, f"No such finding: {finding_id}."
    identity = people.get(by)
    if identity is None or identity.auditable_unit != finding.auditable_unit_id:
        return False, (
            f"{people.name(by)} does not own the unit {finding.id} was raised "
            f"against. Evidence is filed by the owning unit."
        )
    if not evidence_text.strip():
        return False, "Nothing to submit — upload a file or paste the evidence."
    try:
        submission = rounds_stage.open_round(
            repo, people, finding, by=by, evidence_ref=evidence_ref or finding.id,
            evidence_text=evidence_text, note=note, as_of=as_of,
        )
    except (authority.AuthorityError, ValueError) as refusal:
        return False, str(refusal)

    lines = [
        f"**{submission.id}** filed as round {submission.round_number} on "
        f"{finding.id}. It is with PA/InfoSec for review; the finding stays open "
        f"until an auditor is satisfied."
    ]
    try:
        review.evaluate(conn, submission.id, as_of=as_of)
    except Exception as error:  # the filing stands without advice; say why
        lines.append(f"No advisory reading could be attached for the auditor: {error}")
    return True, "\n\n".join(lines)


def respond_to_round(
    conn, submission_id: str, *, response: str, by: str, remarks: str,
) -> tuple[bool, str]:
    """PA/InfoSec answer a round: accepted closes the finding, insufficient does not.

    The same pairing the remediation stage uses. Acceptance closes through
    `followup.close_on_repo`, which re-checks role, separation of duty and that
    the auditor is satisfied; the separation check is made *before* the round is
    answered too, so a refusal cannot leave a round accepted and its finding
    still open.
    """
    from .. import authority, directory
    from ..stages import followup
    from ..stages import rounds as rounds_stage

    repo = repositories(conn)
    people = directory.load(conn)
    as_of = current_date(conn)
    submission = repo["rounds"].get(submission_id)
    if submission is None:
        return False, f"No such evidence round: {submission_id}."
    finding = repo["findings"].get(submission.finding_id)
    try:
        if response == "accepted":
            authority.require_separation(
                rounds_stage.submitters_of(repo, finding.id) | {finding.owner_identity},
                by, "close_finding",
            )
        rounds_stage.respond(
            repo, people, submission, response=response, by=by, remarks=remarks,
            as_of=as_of,
        )
        if response == "accepted":
            followup.close_on_repo(
                repo, finding, by=by, remarks=remarks, as_of=as_of, people=people,
            )
            return True, (
                f"Round {submission.round_number} accepted and **{finding.id}** "
                f"closed by {people.name(by)}."
            )
        followup.record_insufficient_round(
            repo, finding, by=by, remarks=remarks, owner_name=people.name(by),
            as_of=as_of,
        )
    except (authority.AuthorityError, ValueError) as refusal:
        return False, str(refusal)
    return True, (
        f"Round {submission.round_number} marked insufficient. **{finding.id}** "
        f"stays open, and {people.name(finding.owner_identity)} has been asked "
        f"for more evidence."
    )


def record_progress(conn, finding_id: str, progress: str, *, by: str) -> tuple[bool, str]:
    """What the owner says they have done. Advisory; it moves no status."""
    from .. import authority
    from ..stages import followup

    try:
        finding = followup.record_owner_progress(
            conn, finding_id, progress, by=by, as_of=current_date(conn)
        )
    except (authority.AuthorityError, ValueError) as refusal:
        return False, str(refusal)
    return True, (
        f"Progress on **{finding.id}** recorded as "
        f"{progress.replace('_', ' ')}. The finding stays open until an auditor "
        f"is satisfied."
    )


def mark_read(conn, notification_id: str, *, by: str) -> tuple[bool, str]:
    """The one change a notification allows, and only by its recipient."""
    from .. import notify

    try:
        notify.mark_read(conn, notification_id, by=by, as_of=current_date(conn))
    except (PermissionError, ValueError) as refusal:
        return False, str(refusal)
    return True, "Marked as read."


def chronic_findings(conn) -> dict[str, Any]:
    """Open findings more than a year past target, for PA/InfoSec.

    Beside the priority order, never in it: the order is severity first, and a
    finding's age does not overrule the auditor's severity.
    """
    from .. import analytics, directory

    people = directory.load(conn)
    rows = analytics.chronic_findings(repositories(conn), current_date(conn))
    for row in rows:
        row["owner"] = people.name(row.pop("owner_identity"))
    return {"threshold_days": analytics.CHRONIC_DAYS, "findings": rows}


def priority_formula() -> str:
    """The priority score's formula and weights, for the brief panel to print."""
    from .. import priority

    return priority.formula_table()


def recurrence_links(conn) -> list[dict[str, Any]]:
    """Findings that resemble something raised earlier somewhere else."""
    from .. import directory
    from ..repositories import repositories

    repo = repositories(conn)
    people = directory.load(conn)
    units = {u.id: u.name for u in repo["units"].list()}
    reasons: dict[str, dict[str, str]] = {}
    for event in repo["audit"].read_all():
        if event.action == "recurrence_examined":
            reasons[event.entity_id] = event.detail.get("reasons", {}) or {}

    rows = []
    for finding in repo["findings"].list():
        for prior_id in finding.recurrence_of:
            prior = repo["findings"].get(prior_id)
            if prior is None:
                continue
            rows.append({
                "finding": finding.id,
                "unit": units.get(finding.auditable_unit_id, ""),
                "raised": finding.raised_at.date(),
                "category": finding.gap_category,
                "description": finding.description,
                "prior": prior.id,
                "prior_unit": units.get(prior.auditable_unit_id, ""),
                "prior_raised": prior.raised_at.date(),
                "prior_description": prior.description,
                "months_apart": max(
                    (finding.raised_at - prior.raised_at).days // 30, 0
                ),
                "reason": reasons.get(finding.id, {}).get(prior_id, ""),
                "crosses_units": (
                    prior.auditable_unit_id != finding.auditable_unit_id
                ),
            })
    return sorted(rows, key=lambda r: (-r["months_apart"], r["finding"]))


def portfolio_analytics(conn) -> dict[str, Any]:
    """Section 8 in one call. Deterministic — no model is involved."""
    from .. import analytics
    from .. import window as schedule_window

    as_of = current_date(conn)
    return analytics.portfolio(
        conn, as_of, window=(schedule_window.load(conn).start, as_of)
    )


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
