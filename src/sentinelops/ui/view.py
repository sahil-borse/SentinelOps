"""Data shaping for the dashboard. No Streamlit here.

Everything the screen shows is computed by a plain function in this module, so
the parts worth testing are testable and the UI file stays thin enough to read
in one sitting.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass
from datetime import date
from typing import Any

from .. import directory
from ..repositories import repositories

#: Verdicts and statuses that read as a problem, for colouring.
BAD_VERDICTS = ("gap", "insufficient_evidence")


def citation_ranges(content: str, spans: list[str]) -> list[tuple[int, int]]:
    """Where each cited span sits in the source, tolerant of re-wrapping.

    A model that folds a quoted line differently has still quoted it, so the
    match is built from the span's words joined by "any whitespace". Overlapping
    matches are merged, otherwise a span inside another span would produce
    nested markup.
    """
    found: list[tuple[int, int]] = []
    for span in spans:
        words = [re.escape(word) for word in span.split()]
        if not words:
            continue
        pattern = re.compile(r"\s+".join(words), re.IGNORECASE)
        match = pattern.search(content)
        if match:
            found.append((match.start(), match.end()))

    merged: list[tuple[int, int]] = []
    for start, end in sorted(found):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def highlight(content: str, spans: list[str]) -> str:
    """The source document as HTML, with the cited text marked.

    This is the view the whole demo is built around: not "the model said gap"
    but "the model said gap *because of this sentence, here, in your document*".
    Everything is escaped — the content is submitted evidence and the spans are
    model output, so neither is trusted to be safe markup.
    """
    ranges = citation_ranges(content, spans)
    if not ranges:
        return f"<pre class='doc'>{html.escape(content)}</pre>"

    out: list[str] = []
    cursor = 0
    for start, end in ranges:
        out.append(html.escape(content[cursor:start]))
        out.append(f"<mark>{html.escape(content[start:end])}</mark>")
        cursor = end
    out.append(html.escape(content[cursor:]))
    return f"<pre class='doc'>{''.join(out)}</pre>"


_BOLD = re.compile(r"\*\*(.+?)\*\*", re.DOTALL)
_CODE = re.compile(r"`([^`]+)`")


def rich(text: str) -> str:
    """Markdown emphasis, rendered as HTML.

    Streamlit does not process markdown inside a block it is told contains raw
    HTML, so `**this**` in a styled panel arrives on screen with its asterisks
    showing. The narrative is written in markdown and displayed in styled
    panels, so the conversion has to happen here. Escaped first: some of these
    strings carry data-derived names.
    """
    escaped = html.escape(text)
    escaped = _BOLD.sub(lambda m: f'<strong>{m.group(1)}</strong>', escaped)
    return _CODE.sub(lambda m: f'<code>{m.group(1)}</code>', escaped)


#: Roughly how much text fits in the collapsed frame before it needs scrolling.
#: Used only to decide whether offering "show more" is worth the reader's time.
COLLAPSED_VISIBLE_LINES = 12
ASSUMED_LINE_WIDTH = 110

#: How tall the document panel is, collapsed and expanded, in pixels. Both are
#: fixed: the box scrolls inside itself, so the page never grows with the
#: document. A fifty-page upload and a five-line one occupy the same space.
COLLAPSED_HEIGHT = 260
EXPANDED_HEIGHT = 760

#: A safety valve. Past this the browser, not the layout, is the problem.
MAX_RENDERED_CHARS = 200_000

_FRAME_CSS = """
  html,body { margin:0; padding:0; }
  pre { margin:0; padding:.9rem 1.1rem; white-space:pre-wrap; word-wrap:break-word;
        background:#fbfbf9; font-size:13px; line-height:1.55; color:#1a1a1a;
        font-family:ui-monospace,SFMono-Regular,Consolas,monospace; }
  mark { background:#ffe680; box-shadow:0 0 0 2px #ffe680; border-radius:2px;
         scroll-margin-block:6rem; }
  .capped { display:block; margin-top:1rem; color:#999; font-style:italic; }
"""

#: Scrolls the first highlight into view once the frame paints, so opening a
#: long document lands on the sentence the verdict rests on instead of on its
#: first page. Without it the citation view is only useful for short documents.
_FRAME_JS = """
  const first = document.querySelector('mark');
  if (first) { first.scrollIntoView({block: 'center'}); }
"""


@dataclass
class DocumentFrame:
    html: str
    height: int
    total_chars: int
    passages: int
    expanded: bool
    capped: bool
    #: Whether the document already fits, in which case offering to enlarge the
    #: panel is just another button to ignore.
    fits: bool = False

    def caption(self) -> str:
        parts = [f"{self.total_chars:,} characters"]
        if self.passages:
            parts.append(
                f"{self.passages} cited passage"
                f"{'s' if self.passages != 1 else ''} highlighted"
            )
        if self.capped:
            parts.append(f"first {MAX_RENDERED_CHARS:,} shown")
        parts.append("scroll inside the panel")
        return " · ".join(parts)


def document_frame(
    content: str, spans: list[str], *, expanded: bool = False
) -> DocumentFrame:
    """The whole document, in a box that scrolls on its own.

    Evidence is whatever somebody uploaded, and that can be a fifty-page export.
    Letting it flow into the page turns the one view this demo is built around
    into a scroll measured in metres, with the interesting sentence lost in the
    middle of it.

    So the document goes in a fixed-height frame with its own scrollbar. The
    page length no longer depends on the document length at all; "show more"
    makes the frame taller, not the page longer. On open, the first highlight is
    scrolled to the centre, so a long document arrives at its citation.
    """
    total = len(content)
    capped = total > MAX_RENDERED_CHARS
    body = content[:MAX_RENDERED_CHARS] if capped else content
    ranges = citation_ranges(body, spans)

    out: list[str] = []
    cursor = 0
    for start, end in ranges:
        out.append(html.escape(body[cursor:start]))
        out.append(f"<mark>{html.escape(body[start:end])}</mark>")
        cursor = end
    out.append(html.escape(body[cursor:]))
    if capped:
        out.append(
            f"<span class='capped'>… {total - len(body):,} further characters "
            "not rendered.</span>"
        )

    page = (
        "<!doctype html><html><head><meta charset='utf-8'>"
        f"<style>{_FRAME_CSS}</style></head><body>"
        f"<pre>{''.join(out)}</pre>"
        f"<script>{_FRAME_JS}</script></body></html>"
    )
    wrapped_lines = sum(
        max(1, -(-len(line) // ASSUMED_LINE_WIDTH)) for line in body.splitlines() or [""]
    )
    return DocumentFrame(
        html=page,
        height=EXPANDED_HEIGHT if expanded else COLLAPSED_HEIGHT,
        total_chars=total,
        passages=len(ranges),
        expanded=expanded,
        capped=capped,
        fits=wrapped_lines <= COLLAPSED_VISIBLE_LINES,
    )


def unmatched_spans(content: str, spans: list[str]) -> list[str]:
    """Cited text that could not be located. Should always be empty.

    S3 rejects a verdict whose citation does not resolve, so anything here means
    something got past that — worth showing rather than hiding.
    """
    return [
        span for span in spans
        if not citation_ranges(content, [span]) and span.strip()
    ]


@dataclass
class AreaStatus:
    area_id: str
    name: str
    team: str
    owner: str
    criticality: str
    due: int = 0
    assessed: int = 0
    overdue: int = 0
    waived: int = 0
    pending: int = 0
    gaps: int = 0
    worst_severity: float = 0.0

    @property
    def clean(self) -> bool:
        return self.gaps == 0 and self.overdue == 0


def status_by_area(conn) -> list[AreaStatus]:
    """One row per process area: what is due, what failed, how bad."""
    repo = repositories(conn)
    people = directory.load(conn)
    rows = {
        area.id: AreaStatus(
            area_id=area.id, name=area.name, team=area.name,
            owner=people.owner_name(area),
            criticality=area.attributes.get("criticality", ""),
        )
        for area in repo["units"].list()
    }
    for instance in repo["instances"].list():
        row = rows.get(instance.auditable_unit_id)
        if row is None:
            continue
        row.due += 1
        if instance.status == "assessed":
            row.assessed += 1
        elif instance.status == "overdue":
            row.overdue += 1
        elif instance.status == "waived":
            row.waived += 1
        else:
            row.pending += 1

    for flag in repo["flags"].list():
        row = rows.get(flag.auditable_unit_id)
        if row is None or flag.status != "open":
            continue
        if flag.category in ("gap", "overdue"):
            row.gaps += 1
        row.worst_severity = max(row.worst_severity, flag.severity)
    return sorted(rows.values(), key=lambda r: (-r.worst_severity, r.area_id))


def overdue_queue(conn, as_of: date) -> list[dict[str, Any]]:
    """What is late, worst first, with how far it has escalated."""
    repo = repositories(conn)
    escalation: dict[str, int] = {}
    for event in repo["audit"].read_all():
        if event.action == "check_instance_escalated":
            escalation[event.entity_id] = max(
                escalation.get(event.entity_id, 0), int(event.detail.get("level", 0))
            )
    severity = {
        flag.check_instance_id: flag
        for flag in repo["flags"].list()
        if flag.check_instance_id and flag.status == "open"
    }
    queue = []
    for instance in repo["instances"].list():
        late = (as_of - instance.due_date).days
        if instance.status in ("assessed", "waived") and instance.id not in severity:
            continue
        if late <= 0 and instance.id not in severity:
            continue
        flag = severity.get(instance.id)
        if flag is None or flag.category not in ("gap", "overdue"):
            continue
        queue.append({
            "instance": instance.id,
            "control": instance.control_id,
            "area": instance.auditable_unit_id,
            "period": instance.period,
            "due": instance.due_date,
            "days_late": max(late, 0),
            "team": instance.assigned_team,
            "owner": instance.owner_name,
            "category": flag.category,
            "severity": flag.severity,
            "band": flag.severity_band,
            "escalation": escalation.get(instance.id, 0),
        })
    return sorted(queue, key=lambda r: (-r["severity"], -r["days_late"]))


def open_actions(conn) -> list[dict[str, Any]]:
    repo = repositories(conn)
    raised = {
        event.entity_id: event.ts
        for event in repo["audit"].read_all()
        if event.action == "action_raised"
    }
    rows = []
    for action in repo["actions"].list():
        if action.status == "resolved":
            continue
        rows.append({
            "action": action.id,
            "title": action.title,
            "team": action.owner_team,
            "owner": action.owner_name,
            "due": action.due_date,
            "status": action.status,
            "finding": action.assessment_id,
            "raised": raised.get(action.id),
        })
    return sorted(rows, key=lambda r: (r["due"], r["action"]))


def resolved_actions(conn) -> list[dict[str, Any]]:
    repo = repositories(conn)
    return sorted(
        (
            {
                "action": a.id, "team": a.owner_team, "owner": a.owner_name,
                "resolved": a.resolved_at, "note": a.resolution_note,
            }
            for a in repo["actions"].list() if a.status == "resolved"
        ),
        key=lambda r: r["action"],
    )


def finding_detail(conn, instance_id: str) -> dict[str, Any] | None:
    """The current finding for a check, plus the document it was drawn from."""
    repo = repositories(conn)
    findings = sorted(
        repo["assessments"].list(check_instance_id=instance_id), key=lambda f: f.id
    )
    if not findings:
        return None
    superseded = {f.supersedes_assessment_id for f in findings if f.supersedes_assessment_id}
    current = next((f for f in reversed(findings) if f.id not in superseded), findings[-1])
    evidence = sorted(
        repo["evidence"].list(check_instance_id=instance_id),
        key=lambda e: e.submitted_at,
    )
    source = evidence[-1] if evidence else None
    return {
        "finding": current,
        "history": findings,
        "evidence": source,
        "all_evidence": evidence,
        "instance": repo["instances"].get(instance_id),
    }


def timeline(conn, instance_id: str) -> list[dict[str, Any]]:
    """Every event touching one check, in the order it was written."""
    repo = repositories(conn)
    findings = repo["assessments"].list(check_instance_id=instance_id)
    wanted_ids = {instance_id} | {f.id for f in findings}
    wanted_ids |= {
        f.id for f in repo["flags"].list(check_instance_id=instance_id)
    }
    wanted_ids |= {e.id for e in repo["evidence"].list(check_instance_id=instance_id)}
    wanted_ids.add(f"ACT-{instance_id.removeprefix('CHK-')}")

    rows = []
    for event in repo["audit"].read_all():
        if event.entity_id not in wanted_ids:
            continue
        rows.append({
            "seq": event.seq,
            "when": event.ts,
            "actor": event.actor_kind,
            "owner": event.owner,
            "event": event.action,
            "entity": f"{event.entity_type}:{event.entity_id}",
            "detail": event.detail,
        })
    return rows


def token_meter(conn) -> dict[str, Any]:
    row = conn.execute(
        "SELECT COUNT(*) calls, COALESCE(SUM(input_tokens),0) input,"
        " COALESCE(SUM(output_tokens),0) output,"
        " COALESCE(SUM(cached_tokens),0) cached,"
        " COALESCE(SUM(cost_usd),0) cost FROM token_usage"
    ).fetchone()
    repo = repositories(conn)
    findings = repo["assessments"].list()
    superseded = {f.supersedes_assessment_id for f in findings if f.supersedes_assessment_id}
    current = [f for f in findings if f.id not in superseded]
    by_rule = len([f for f in current if not str(f.decided_by).startswith("s3_")])
    return {
        "calls": row["calls"],
        "input_tokens": row["input"],
        "output_tokens": row["output"],
        "cached_tokens": row["cached"],
        "total_tokens": row["input"] + row["output"],
        "cost_usd": row["cost"],
        "assessments": len(current),
        "decided_by_rule": by_rule,
        "zero_model_share": by_rule / len(current) if current else 0.0,
    }


def assessable_instances(conn) -> list[str]:
    """Checks with a finding, newest period first — the pickable list."""
    repo = repositories(conn)
    with_findings = {f.check_instance_id for f in repo["assessments"].list()}
    return sorted(with_findings, reverse=True)


def instances_awaiting_evidence(conn) -> list[str]:
    repo = repositories(conn)
    return sorted(
        i.id for i in repo["instances"].list()
        if i.status in ("pending", "overdue", "assessed")
    )
