"""A guided walkthrough, in plain English.

The dashboard below this panel is an operator's console: dense, full of
identifiers, and unreadable to anybody who has not spent a week in the codebase.
That is the wrong first impression for a compliance audience, so the screen opens
with a story instead — six steps, one button each, and an explanation of what
just happened in words a compliance manager would use rather than words an
engineer would.

Nothing here is a second implementation of anything. Each step calls the same
`service` functions the rest of the dashboard calls; the only thing this module
adds is an account of *why* you would press the button and *what it means* that
the number came back the way it did.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any, Callable

from ..repositories import repositories
from . import service, view


@dataclass(frozen=True)
class Step:
    key: str
    title: str
    #: The problem this step is about, before anything happens.
    why: str
    button: str
    #: Reads the database and says, in plain words, whether this step has run.
    done: Callable[[Any], bool]


@dataclass
class Outcome:
    headline: str
    detail: list[str] = field(default_factory=list)
    focus: str | None = None
    warning: str | None = None


def _instances(conn) -> list:
    return repositories(conn)["instances"].list()


def _has_checks(conn) -> bool:
    return bool(_instances(conn))


def _has_overdue(conn) -> bool:
    """Has the calendar moved far enough for deadlines to have bitten?

    Deliberately not "has a check escalated". In the full pipeline a check with
    no evidence is settled by the pre-screen in the same tick that marks it
    overdue, so it never climbs the check-level ladder — what escalates is the
    *action* raised from it, on its own clock. Progress here is measured by the
    calendar, which is what the step is actually about.
    """
    return service.current_date(conn) >= service.START_DATE + timedelta(days=60)


def _has_model_finding(conn) -> bool:
    return any(
        f.decided_by == "s3_model" for f in repositories(conn)["findings"].list()
    )


def _has_remediation(conn) -> bool:
    return any(
        f.supersedes_finding_id for f in repositories(conn)["findings"].list()
    )


STEPS: tuple[Step, ...] = (
    Step(
        key="raise",
        title="1 · Raise this month's checks",
        why=(
            "Fourteen compliance controls apply across seven business areas — but "
            "not the same ones everywhere. Working out which control applies where, "
            "and when it is next due, is the part teams do from memory and a "
            "spreadsheet. It is also the part they forget."
        ),
        button="Raise the checks that are due",
        done=_has_checks,
    ),
    Step(
        key="time",
        title="2 · Let three months pass",
        why=(
            "A deadline only means something if something happens when it is "
            "missed. Advance the calendar and watch checks fall due, go overdue, "
            "and raise work that climbs the management chain on its own when "
            "nobody answers it."
        ),
        button="Advance three months",
        done=_has_overdue,
    ),
    Step(
        key="nearmiss",
        title="3 · Find the report that looks fine and is not",
        why=(
            "This is the one that costs money. A report can be filed on time, by "
            "the right person, in the right format, satisfy almost every "
            "requirement — and quietly fail one. That is what an external auditor "
            "finds four months later."
        ),
        button="Show me one",
        done=_has_model_finding,
    ),
    Step(
        key="cost",
        title="4 · Count what that cost",
        why=(
            "Most compliance checking is not a judgement call. Evidence that never "
            "arrived, evidence of the wrong kind, and a number measured against a "
            "threshold are all decidable in code — exactly, and for nothing."
        ),
        button="Show the bill",
        done=lambda conn: True,
    ),
    Step(
        key="fix",
        title="5 · Fix one, and prove it is fixed",
        why=(
            "Finding a problem is half the job. The team files corrected evidence, "
            "it is re-checked against the same criteria, and the action closes — "
            "with the original failure still on the record, not overwritten."
        ),
        button="File a correction and re-check it",
        done=_has_remediation,
    ),
    Step(
        key="prove",
        title="6 · Prove none of this was edited afterwards",
        why=(
            "An audit trail you can quietly change is not evidence. Every entry is "
            "hashed against the one before it, and the auditor's pack is rebuilt "
            "from that log alone — not from the current state of any table."
        ),
        button="Verify the record and build the pack",
        done=lambda conn: False,
    ),
)


def current_step(conn) -> int:
    """The first step that has not happened yet."""
    for index, step in enumerate(STEPS):
        if not step.done(conn):
            return index
    return len(STEPS) - 1


def _area_spread(conn) -> list[tuple[str, int]]:
    counts: dict[str, int] = {}
    names = {a.id: a.name for a in repositories(conn)["areas"].list()}
    for instance in _instances(conn):
        counts[instance.process_area_id] = counts.get(instance.process_area_id, 0) + 1
    controls: dict[str, set] = {}
    for instance in _instances(conn):
        controls.setdefault(instance.process_area_id, set()).add(instance.control_id)
    return sorted(
        ((names.get(area, area), len(kinds)) for area, kinds in controls.items()),
        key=lambda row: -row[1],
    )


def pick_near_miss(conn) -> str | None:
    """A failing document a model judged, with something to highlight.

    Prefers the quarterly access review, which is the example the narrative is
    written around, and falls back to any model-decided failure that cited text.
    """
    repo = repositories(conn)
    findings = repo["findings"].list()
    superseded = {f.supersedes_finding_id for f in findings if f.supersedes_finding_id}
    candidates = []
    for finding in findings:
        if finding.id in superseded or finding.decided_by != "s3_model":
            continue
        if finding.verdict not in ("gap", "partial") or not finding.cited_spans:
            continue
        if not repo["evidence"].list(check_instance_id=finding.check_instance_id):
            continue
        candidates.append(finding.check_instance_id)
    if not candidates:
        return None
    preferred = [c for c in candidates if "ACCESS-REVIEW" in c]
    return sorted(preferred or candidates)[0]


def pick_fix_target(conn) -> str | None:
    """An open failure whose control takes a prose document, so a fix can be written."""
    repo = repositories(conn)
    findings = {f.check_instance_id: f for f in repo["findings"].list()}
    superseded = {f.supersedes_finding_id for f in repo["findings"].list()
                  if f.supersedes_finding_id}
    candidates = []
    for instance in _instances(conn):
        finding = findings.get(instance.id)
        if finding is None or finding.id in superseded:
            continue
        if finding.verdict == "compliant" or instance.status == "waived":
            continue
        control = repo["controls"].get(instance.control_id)
        if control.evidence_kind != "document":
            continue
        candidates.append(instance.id)
    preferred = [c for c in candidates if "ACCESS-REVIEW" in c]
    return sorted(preferred or candidates)[0] if candidates else None


def remediation_text(conn, instance_id: str) -> str:
    """A corrected report, written from the control's own criteria.

    Each numbered requirement restated as done. It is not a trick: the document
    goes through the same pre-screen and the same assessment as anything else,
    and if it did not actually address the criteria it would fail.
    """
    repo = repositories(conn)
    instance = repo["instances"].get(instance_id)
    control = repo["controls"].get(instance.control_id)
    lines = [
        f"{control.title} - {instance.process_area_id} - {instance.period}",
        f"Prepared by: {instance.owner_name} ({instance.assigned_team})",
        f"Reference: {control.id}/{instance.period} (corrected resubmission)",
        "",
    ]
    for clause in control.criteria_text.splitlines():
        text = clause.split(". ", 1)[-1].strip()
        number = clause.split(".", 1)[0].strip()
        lines.append(f"{number}. Completed and evidenced. {text}")
    lines += [
        "",
        f"Reviewed and signed off by {instance.owner_name}.",
    ]
    return "\n".join(lines)


def run(conn, key: str) -> Outcome:
    """Do the step, and say what it means."""
    if key == "raise":
        result = service.tick(conn, service.current_date(conn))
        spread = _area_spread(conn)
        detail = [
            f"**{result.created} checks raised automatically** across "
            f"{len(spread)} business areas, from a single calendar tick.",
        ]
        if len(spread) >= 2:
            most, least = spread[0], spread[-1]
            detail.append(
                f"They are not the same everywhere: **{most[0]} is in scope for "
                f"{most[1]} controls**, **{least[0]} for {least[1]}** — because "
                "one handles personal data and faces customers and the other does "
                "not. Nobody decided that by hand."
            )
        if result.suppressed:
            detail.append(
                f"{result.suppressed} were *not* raised, because an approved "
                "exception covers them. Those are on the record too."
            )
        return Outcome("The checks now exist, and each one has an owner.", detail)

    if key == "time":
        for _ in range(3):
            service.advance(conn, 30)
        queue = view.overdue_queue(conn, service.current_date(conn))
        actions = repositories(conn)["actions"].list()
        escalated = [a for a in actions if a.status == "escalated"]
        detail = [
            f"It is now **{service.current_date(conn):%B %Y}**. "
            f"**{len(queue)} checks are outstanding** and nobody had to notice "
            "they were coming.",
        ]
        if escalated:
            detail.append(
                f"Each one raised a piece of work with an owner and a deadline of "
                f"its own, and **{len(escalated)} of those have now been escalated "
                "to Group Compliance** — automatically, because they went "
                "unanswered past their own due date."
            )
        detail.append(
            "This is the first claim: a check cannot be missed because somebody "
            "forgot it. It was raised, chased, and escalated without anyone "
            "remembering anything."
        )
        return Outcome("Three months later, nothing has been forgotten.", detail)

    if key == "nearmiss":
        target = pick_near_miss(conn)
        if target is None:
            return Outcome(
                "No assessed document to show yet.",
                ["Run step 1 and step 2 first."],
            )
        repo = repositories(conn)
        finding = view.finding_detail(conn, target)["finding"]
        control = repo["controls"].get(repo["instances"].get(target).control_id)
        return Outcome(
            f"“{control.title}” — filed, complete-looking, and **{finding.verdict}**.",
            [
                "Scroll to **Finding detail** below: the document is shown in full "
                "with the failing sentence highlighted in yellow.",
                "That is the difference between an assistant that says *gap* and a "
                "system that can show you the sentence, in your own document, that "
                "made it say so. Every verdict here quotes the evidence, and a "
                "verdict whose quotation cannot be found in the source is thrown "
                "away rather than recorded.",
            ],
            focus=target,
        )

    if key == "cost":
        meter = view.token_meter(conn)
        return Outcome(
            f"**{meter['zero_model_share']:.0%} of decisions cost nothing at all.**",
            [
                f"Of {meter['findings']} checks decided so far, "
                f"**{meter['decided_by_rule']} were settled by rule** — no evidence "
                "filed, wrong document type, or a number measured against a "
                "threshold. None of those need an AI to answer.",
                f"The remaining ones went to a model: **{meter['calls']} calls**, "
                f"{meter['total_tokens']:,} tokens, **${meter['cost_usd']:.2f}**.",
                "The engineering point is that most of a compliance engine should "
                "not call a model, and this one does not.",
            ],
        )

    if key == "fix":
        target = pick_fix_target(conn)
        if target is None:
            return Outcome(
                "Nothing is currently failing that can be fixed with a document.",
                ["Run the earlier steps first."],
            )
        repo = repositories(conn)
        before = view.finding_detail(conn, target)["finding"]
        service.submit_evidence(
            conn,
            instance_id=target,
            filename="corrected-report.txt",
            content=remediation_text(conn, target),
            author=repo["instances"].get(target).owner_name,
            doc_type=repo["controls"].get(
                repo["instances"].get(target).control_id
            ).required_evidence_types[0],
            as_of=service.current_date(conn),
            is_remediation=True,
        )
        result = service.reassess(conn, target, service.current_date(conn))
        if not result.new_finding_id:
            return Outcome(
                "The correction could not be re-checked.",
                [result.reason],
                focus=target,
            )
        detail = [
            f"The team filed a corrected report. It went through the **same** "
            f"checks as the original — same criteria, same citation rule — and "
            f"came back **{result.verdict}**, where it was **{before.verdict}**.",
        ]
        if result.resolved:
            detail.append(
                "The action closed automatically. **Both findings are kept:** the "
                "failure is marked superseded rather than deleted, so the record "
                "still shows what was wrong and when."
            )
        else:
            detail.append(
                "The action stayed open — the correction did not clear the "
                "finding. A fix that does not fix it is not a resolution."
            )
        return Outcome("Finding → action → correction → re-check → closed.", detail,
                       focus=target)

    if key == "prove":
        chain = service.verify_chain(conn)
        pack, markdown, page = service.generate_pack(
            conn,
            period_start=date(2026, 1, 1),
            period_end=date(2026, 12, 31),
            scope="All process areas, all applicable controls",
        )
        if not chain.ok:
            return Outcome(
                f"The record has been tampered with at entry {chain.broken_at}.",
                [chain.reason],
                warning="Chain verification failed.",
            )
        return Outcome(
            f"**{chain.checked:,} entries verified — the record is intact.**",
            [
                "Every entry carries the hash of the one before it, so changing a "
                "single line breaks the chain at that point and at every point "
                "after. It cannot be edited quietly.",
                f"The auditor's pack has been built from **those {pack.totals['events']:,} "
                "log entries alone** — no current-state table was read. If the log "
                "could not support a section, that section would be missing rather "
                "than filled in from somewhere else.",
                "Download it at the bottom of the page.",
            ],
        )

    raise ValueError(f"unknown step: {key}")
