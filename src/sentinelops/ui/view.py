"""Data shaping for the dashboard. No Streamlit here.

Everything the screen shows is computed by a plain function in this module, so
the parts worth testing are testable and the UI file stays thin enough to read
in one sitting.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from string import Template
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
#:
#: The frame's own window, not `scrollIntoView`: that scrolls every scrollable
#: ancestor, and in a same-origin frame the ancestors include the dashboard —
#: the landing page opened scrolled halfway down, onto the first document in
#: the review queue, instead of on what needs attention.
_FRAME_JS = """
  const first = document.querySelector('mark');
  if (first) {
    const top = first.getBoundingClientRect().top + window.scrollY;
    window.scrollTo(0, Math.max(0, top - window.innerHeight / 2));
  }
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
    """The open findings, oldest target date first — the chase list.

    Kept under its UI name because that is what the screen calls the panel; the
    rows are v3 Findings, with the severity the *auditor* assigned and the
    follow-up count that says how many times this one has been chased.
    """
    repo = repositories(conn)
    people = directory.load(conn)
    units = {u.id: u for u in repo["units"].list()}
    raised = {
        event.entity_id: event.ts
        for event in repo["audit"].read_all()
        if event.action == "finding_raised"
    }
    rows = []
    for finding in repo["findings"].list():
        if finding.status != "open":
            continue
        unit = units.get(finding.auditable_unit_id)
        rows.append({
            "action": finding.id,
            "title": finding.agreed_action_plan or finding.description,
            "team": unit.name if unit else finding.auditable_unit_id,
            "owner": people.name(finding.owner_identity),
            "due": finding.target_date,
            "status": finding.owner_progress or "awaiting acknowledgement",
            "severity": finding.severity or finding.suggested_severity or "",
            "chased": finding.follow_up_count,
            "finding": finding.check_instance_id or finding.audit_id or "",
            "raised": raised.get(finding.id),
        })
    return sorted(rows, key=lambda r: (r["due"], r["action"]))


def resolved_actions(conn) -> list[dict[str, Any]]:
    """Closed findings — closed by an auditor, with the remarks that did it."""
    repo = repositories(conn)
    people = directory.load(conn)
    units = {u.id: u for u in repo["units"].list()}
    return sorted(
        (
            {
                "action": f.id,
                "team": (units[f.auditable_unit_id].name
                         if f.auditable_unit_id in units else f.auditable_unit_id),
                "owner": people.name(f.owner_identity),
                "resolved": f.closed_at,
                "closed_by": people.name(f.closed_by) if f.closed_by else "",
                "note": f.closure_remarks,
            }
            for f in repo["findings"].list() if f.status == "closed"
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


# =============================================================================
# The design system (slice 17)
# =============================================================================
#
# One accent, one neutral scale, and one semantic set for severity. Those three
# severities are the only colours on the screen that mean something, and nothing
# else borrows them. Colour is never the only signal: every badge carries its
# label, so the screen reads the same to someone who cannot tell red from amber.

ACCENT = "#0F766E"
ACCENT_FILL = "#E3F3F0"
ACCENT_BORDER = "#A9DCD3"

#: One neutral scale, lightest to darkest.
NEUTRAL: dict[str, str] = {
    "0": "#FFFFFF",
    "50": "#F8FAFB",
    "100": "#F1F4F6",
    "200": "#E3E8EC",
    "300": "#CBD3D9",
    "500": "#64717D",
    "700": "#35404A",
    "900": "#111827",
}

SEVERITIES: tuple[str, ...] = ("Major", "Minor", "Observation")

#: Text, fill and border for each severity.
SEVERITY_STYLE: dict[str, tuple[str, str, str]] = {
    "Major": ("#A11A1A", "#FDE8E8", "#F3B8B8"),
    "Minor": ("#8C4A07", "#FDF0DC", "#EFC88F"),
    "Observation": ("#1E4FB8", "#E7EEFC", "#B9CBF3"),
}

#: The same set, in the names a dataframe pill column accepts.
SEVERITY_PILL: dict[str, str] = {"Major": "red", "Minor": "orange", "Observation": "blue"}

PALETTE: frozenset[str] = frozenset(
    {ACCENT, ACCENT_FILL, ACCENT_BORDER, *NEUTRAL.values()}
    | {colour for style in SEVERITY_STYLE.values() for colour in style}
)

#: The type scale, in pixels. Set explicitly rather than inherited, so the
#: dashboard reads at the same density on any machine: a working screen for a
#: compliance team, not a document.
TYPE_SCALE: dict[str, float] = {
    "title": 24, "section": 16, "body": 14, "small": 12.5, "figure": 28,
}

_CSS = Template("""
<style>
.stApp { background: $n50; color: $n900; font-variant-numeric: tabular-nums; }
.stApp p, .stApp li, .stApp label { font-size: ${body}px; line-height: 1.5; }
[data-testid="stHeader"] { background: transparent; height: 2.25rem; }
[data-testid="stMainBlockContainer"] { padding: 2.1rem 1.75rem 2.5rem 1.75rem; max-width: none; }
[data-testid="stMain"] [data-testid="stVerticalBlock"] { gap: 0.7rem; }
[data-testid="stSidebar"] { background: $n0; border-right: 1px solid $n200; }
[data-testid="stSidebarUserContent"] { padding-top: 0.25rem; padding-bottom: 1rem; }
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: 0.5rem; }
.stApp h1 { font-size: ${title}px; font-weight: 650; letter-spacing: -0.015em; line-height: 1.2; color: $n900; }
.stApp h2 { font-size: ${section}px; font-weight: 640; color: $n900; }
.stApp h3 { font-size: ${section}px; font-weight: 620; letter-spacing: -0.005em; color: $n900; padding: 0; line-height: 1.35; }
[data-testid="stCaptionContainer"] p { color: $n500; font-size: ${small}px; line-height: 1.45; }
.stButton button, .stFormSubmitButton button, .stDownloadButton button { border-radius: 8px; font-weight: 600; min-height: 2.25rem; }
[data-testid="stSidebar"] [data-testid="stColumn"] .stButton button { padding-left: 2px; padding-right: 2px; font-size: 13px; white-space: nowrap; }
[data-testid="stPageLink"] a p { font-size: 13px; font-weight: 600; color: $accent; }
div[class*="st-key-card"] { background: $n0; border: 1px solid $n200; border-radius: 12px; padding: 14px 16px 22px; box-shadow: 0 1px 2px rgba(17, 24, 39, 0.04); }
div[class*="st-key-alert"] { background: $n0; border: 1px solid $n200; border-left: 4px solid $n900; border-radius: 12px; padding: 14px 16px 22px; }
[data-testid="stDataFrame"] { border: 1px solid $n200; border-radius: 8px; }
[data-testid="stExpander"] details { border-radius: 10px; border-color: $n200; background: $n0; }

div[class*="st-key-inbox_table"] [data-testid="stDataFrame"], div[class*="st-key-inbox_table"] [data-testid="stDataFrame"] * { cursor: pointer !important; }
[data-testid="stDialog"] { background: rgba(17, 24, 39, 0.45) !important; cursor: not-allowed; }
[data-testid="stDialog"] > div { cursor: default; border-radius: 14px; box-shadow: 0 20px 48px rgba(17, 24, 39, 0.28); }
[data-testid="stSidebarNavLink"] { position: relative; }
[data-testid="stSidebarNavLink"]::after { margin-left: auto; min-width: 20px; height: 20px; padding: 0 6px; border-radius: 999px; background: $accent; color: $n0; font-size: 11px; font-weight: 700; line-height: 20px; text-align: center; font-variant-numeric: tabular-nums; box-sizing: border-box; }
[data-testid="stSidebar"][aria-expanded="false"] { transform: none !important; width: 64px !important; min-width: 64px !important; max-width: 64px !important; overflow: hidden; }
[data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarUserContent"] { display: none; }
[data-testid="stSidebar"][aria-expanded="false"] [data-testid="stNavSectionHeader"] { display: none; }
[data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarNavLink"] span[label] { display: none; }
[data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarContent"] { padding-left: 0; padding-right: 0; overflow-x: hidden; }
[data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarNavItems"] { padding-left: 0; padding-right: 0; }
[data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarNavLinkContainer"] { display: flex; justify-content: center; }
[data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarNavLink"] { width: 40px; height: 36px; margin: 2px auto; padding: 0; justify-content: center; border-radius: 9px; }
[data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarNavLink"] > span:first-child { margin: 0; }
[data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarNavLink"]::after { position: absolute; top: -3px; right: -7px; min-width: 17px; height: 17px; padding: 0 4px; font-size: 9.5px; line-height: 17px; border: 2px solid $n0; }
[data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarCollapseButton"] { display: none; }

.so-topbar { display: flex; flex-wrap: wrap; gap: 8px; justify-content: space-between; align-items: center; padding-bottom: 10px; margin-bottom: 12px; border-bottom: 1px solid $n200; }
.so-brand { font-weight: 700; font-size: 15px; color: $n900; letter-spacing: -0.01em; }
.so-brand span { font-weight: 500; color: $n500; margin-left: 8px; font-size: 13px; }
.so-chips { display: flex; flex-wrap: wrap; gap: 6px; }
.so-chip { background: $n0; border: 1px solid $n200; border-radius: 999px; padding: 3px 10px; font-size: 12.5px; color: $n700; }
.so-chip b { color: $n900; font-weight: 650; }

.so-eyebrow { font-size: 11px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: $accent; }
.so-title { font-size: ${title}px; font-weight: 650; letter-spacing: -0.015em; color: $n900; margin: 1px 0 2px; line-height: 1.2; }
.so-subtitle { font-size: 13.5px; color: $n500; margin-bottom: 12px; max-width: 110ch; line-height: 1.5; }

.so-figures { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; margin: 0 0 12px; }
.so-figure { background: $n0; border: 1px solid $n200; border-radius: 12px; padding: 11px 14px 10px; }
.so-figure.so-attention { box-shadow: inset 0 3px 0 $accent; }
.so-figure-label { font-size: 11px; font-weight: 650; letter-spacing: 0.06em; text-transform: uppercase; color: $n500; }
.so-figure-value { font-size: ${figure}px; font-weight: 650; color: $n900; line-height: 1.15; margin-top: 3px; }
.so-figure-compare { font-size: ${small}px; color: $n500; margin-top: 2px; }

.so-badge { display: inline-flex; align-items: center; gap: 5px; padding: 1px 8px; border-radius: 999px; font-size: 12px; font-weight: 650; line-height: 18px; border: 1px solid $n300; color: $n700; background: $n100; white-space: nowrap; vertical-align: middle; }
.so-badge::before { content: ""; width: 6px; height: 6px; border-radius: 50%; background: currentColor; }
.so-sev-major { color: $major; background: $major_fill; border-color: $major_border; }
.so-sev-minor { color: $minor; background: $minor_fill; border-color: $minor_border; }
.so-sev-observation { color: $observation; background: $observation_fill; border-color: $observation_border; }
.so-accent { color: $accent; background: $accent_fill; border-color: $accent_border; }
.so-outline { background: $n0; }
.so-ink { color: $n0; background: $n900; border-color: $n900; }

.so-empty { border: 1px dashed $n300; border-radius: 10px; padding: 11px 14px; background: $n50; margin: 8px 0 4px; }
.so-empty-title { font-weight: 650; color: $n700; margin-bottom: 2px; font-size: 13.5px; }
.so-empty-why { color: $n500; font-size: 13px; line-height: 1.5; }

.so-facts { display: grid; grid-template-columns: max-content 1fr max-content 1fr; gap: 4px 16px; margin: 8px 0 10px; font-size: 13.5px; }
@media (max-width: 1100px) { .so-facts { grid-template-columns: max-content 1fr; } }
.so-facts dt { color: $n500; }
.so-facts dd { margin: 0; color: $n900; }
.so-quote { border-left: 3px solid $n300; background: $n50; padding: 7px 12px; border-radius: 0 8px 8px 0; color: $n700; margin: 6px 0; line-height: 1.5; font-size: 13.5px; }
.so-quote-cite { display: block; font-size: 12px; color: $n500; margin-bottom: 2px; font-weight: 600; }
.so-id { font-family: ui-monospace, SFMono-Regular, Consolas, monospace; font-size: 12px; color: $n900; background: $n100; border-radius: 6px; padding: 1px 6px; white-space: nowrap; }
.so-muted { color: $n500; font-size: 12.5px; }
.so-row { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; }
.so-finding-title { font-size: 15px; font-weight: 600; color: $n900; margin: 6px 0 2px; line-height: 1.4; }
.so-item { padding: 8px 0; border-bottom: 1px solid $n100; }
.so-item:last-child { border-bottom: 0; }
.so-line { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; }
.so-line-title { font-size: 13.5px; font-weight: 600; color: $n900; line-height: 1.4; margin-top: 2px; }
.so-line-meta { text-align: right; font-size: 12.5px; color: $n700; white-space: nowrap; }
.so-line-meta span { display: block; color: $n500; }
.so-priority { display: flex; gap: 10px; padding: 8px 0; border-bottom: 1px solid $n100; }
.so-rank { flex: 0 0 24px; height: 24px; border-radius: 7px; background: $accent_fill; color: $accent; font-weight: 700; font-size: 13px; display: flex; align-items: center; justify-content: center; }
.so-reason { margin-top: 2px; color: $n700; font-size: 13.5px; }
.so-cite { font-family: ui-monospace, SFMono-Regular, Consolas, monospace; font-size: 11.5px; background: $n100; border: 1px solid $n200; border-radius: 6px; padding: 0 6px; margin: 4px 4px 0 0; display: inline-block; color: $n700; }
.so-pair { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
@media (max-width: 900px) { .so-pair { grid-template-columns: 1fr; } }
.so-label { font-size: 11px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; color: $n500; margin: 0 0 4px; }
.so-read { background: $n50; border: 1px solid $n200; border-radius: 10px; padding: 10px 12px; }
.so-read-value { font-size: 18px; font-weight: 650; color: $n900; margin: 1px 0; }
.so-advisory { background: $n50; border: 1px solid $n200; border-radius: 10px; padding: 10px 12px; margin: 8px 0; }

.so-who { border: 1px solid $n200; border-radius: 10px; padding: 9px 12px; background: $n50; margin-bottom: 14px; }
.so-who-name { font-weight: 650; color: $n900; font-size: 14px; }
.so-who-line { font-size: 12.5px; color: $n500; margin-top: 2px; line-height: 1.4; }
.so-date { font-size: 15px; font-weight: 650; color: $n900; }
.so-date-sub { font-size: 12px; color: $n500; margin-bottom: 10px; line-height: 1.4; }
.so-meter { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-bottom: 14px; }
.so-meter div { background: $n50; border: 1px solid $n200; border-radius: 8px; padding: 6px 9px; }
.so-meter b { display: block; font-size: 14px; color: $n900; }
.so-meter span { font-size: 10.5px; color: $n500; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 650; }

.pill { display: inline-block; padding: .05rem .5rem; border-radius: 10px; font-size: .78rem; font-weight: 600; }
.stepnav { color: $n500; font-size: 11px; font-weight: 700; letter-spacing: 0.08em; }
.why { background: $n50; border-left: 4px solid $accent; padding: .7rem 1rem; margin: .3rem 0 .7rem 0; font-size: ${body}px; line-height: 1.6; border-radius: 0 10px 10px 0; }
.outcome { background: $accent_fill; border-left: 4px solid $accent; padding: .7rem 1rem; margin: .4rem 0; line-height: 1.6; border-radius: 0 10px 10px 0; }
</style>
""")

CSS = _CSS.substitute(
    accent=ACCENT, accent_fill=ACCENT_FILL, accent_border=ACCENT_BORDER,
    **{name: f"{size:g}" for name, size in TYPE_SCALE.items()},
    **{f"n{step}": colour for step, colour in NEUTRAL.items()},
    **{
        f"{name.lower()}{suffix}": style[index]
        for name, style in SEVERITY_STYLE.items()
        for index, suffix in enumerate(("", "_fill", "_border"))
    },
)


def _e(value: Any) -> str:
    return html.escape(str(value), quote=True)


# --- labels: never a raw enum on screen ---------------------------------------

ROLE_LABELS = {"pa_infosec": "PA/InfoSec", "unit_owner": "Unit owner",
               "management": "Management"}
STATUS_LABELS = {"open": "Open", "closed": "Closed"}
PROGRESS_LABELS = {
    None: "Not acknowledged", "": "Not acknowledged",
    "acknowledged": "Acknowledged", "action_in_progress": "Action in progress",
    "implemented": "Implemented",
}
PROGRESS_STEPS = ("acknowledged", "action_in_progress", "implemented")
RESPONSE_LABELS = {"pending": "Awaiting review", "accepted": "Accepted",
                   "insufficient": "Insufficient"}
VERDICT_LABELS = {
    "compliant": "Compliant", "partial": "Partial", "gap": "Gap",
    "insufficient_evidence": "Insufficient evidence",
    "satisfies": "Satisfies", "partially_satisfies": "Partially satisfies",
    "does_not_satisfy": "Does not satisfy",
}
KIND_LABELS = {
    "audit_due": "Audit due", "activity_due": "Activity due",
    "finding_raised": "Finding raised", "reminder": "Reminder",
    "evidence_requested": "Evidence requested", "overdue": "Overdue",
    "escalation": "Escalation", "evidence_submitted": "Evidence submitted",
    "closure": "Closed", "exception_lapsed": "Exception lapsed",
}
AUDIT_KIND_LABELS = {"internal_audit": "Internal audit", "qarev": "QAREV",
                     "release_audit": "Release audit",
                     "document_review": "Document review"}
CHECK_STATUS_LABELS = {"pending": "Awaiting evidence", "submitted": "Submitted",
                       "assessed": "Assessed", "overdue": "Overdue",
                       "waived": "Waived"}
DECIDED_BY_LABELS = {"s3_model": "Model assessment",
                     "stale_evidence": "Rule · stale evidence",
                     "wrong_evidence_type": "Rule · wrong document type",
                     "structured_threshold": "Rule · threshold",
                     "no_evidence": "Rule · no evidence"}
DIRECTION_LABELS = {"rising": "Rising", "falling": "Falling", "flat": "Flat",
                    "insufficient_history": "Not enough history"}
ACTOR_LABELS = {"system": "System", "ai": "Model", "user": "Person"}


def humanise(name: str) -> str:
    """`finding_escalated` -> `Finding escalated`."""
    return str(name).replace("_", " ").strip().capitalize()


#: The identities the system acts as, named as a reader would say them.
SYSTEM_NAMES = {"ID-SYSTEM": "the scheduler", "ID-ASSESSOR": "automated assessment"}


def person(people, identity_id: str | None) -> str:
    """A person's name, or what the system was doing when it acted."""
    return SYSTEM_NAMES.get(identity_id or "") or people.name(identity_id)


def badge(label: str, tone: str = "neutral") -> str:
    """A label with a colour behind it. The label is always there."""
    return f'<span class="so-badge so-{tone}">{_e(label)}</span>'


def severity_badge(severity: str | None) -> str:
    if severity in SEVERITY_STYLE:
        return badge(severity, f"sev-{severity.lower()}")
    return badge("Unassigned", "outline")


def status_badge(status: str) -> str:
    return badge(STATUS_LABELS.get(status, humanise(status)),
                 "accent" if status == "open" else "neutral")


def progress_badge(progress: str | None) -> str:
    return badge(PROGRESS_LABELS.get(progress, humanise(progress or "")), "outline")


def response_badge(response: str) -> str:
    return badge(RESPONSE_LABELS.get(response, humanise(response)),
                 "accent" if response == "pending" else "outline")


def verdict_badge(verdict: str) -> str:
    return badge(VERDICT_LABELS.get(verdict, humanise(verdict)), "outline")


def chronic_badge() -> str:
    return badge("Chronic", "ink")


def escalation_badge(level: int) -> str:
    return badge(f"Escalated · level {level}", "outline") if level else ""


# --- dates: readable, and always simulated business time ----------------------

def _as_date(value: Any) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value)[:10])


def fmt_date(value: Any) -> str:
    """15 Apr 2027."""
    day = _as_date(value)
    return f"{day.day} {day:%b %Y}" if day else "—"


def fmt_long_date(value: Any) -> str:
    """Thursday 15 April 2027."""
    day = _as_date(value)
    return f"{day:%A} {day.day} {day:%B %Y}" if day else "—"


def fmt_when(value: datetime | None) -> str:
    """15 Apr 2027, 10:00."""
    return f"{fmt_date(value)}, {value:%H:%M}" if value else "—"


def month_label(month: str) -> str:
    """`2026-03` -> `Mar 2026`."""
    return f"{date.fromisoformat(month + '-01'):%b %Y}"


def plural(count: int, word: str, many: str | None = None) -> str:
    """`3 days`, `1 day`; `many` for the words that do not take an s."""
    return f"{count} {word if count == 1 else (many or word + 's')}"


def due_phrase(days_past_target: int) -> str:
    if days_past_target > 0:
        return f"{plural(days_past_target, 'day')} late"
    if days_past_target == 0:
        return "Due today"
    return f"Due in {plural(-days_past_target, 'day')}"


def delta_phrase(now: int, before: int, since: date) -> str:
    change = now - before
    if change == 0:
        return f"No change since {fmt_date(since)}"
    return f"{change:+d} since {fmt_date(since)}"


# --- building blocks ------------------------------------------------------------

@dataclass
class Figure:
    """One of the few large numbers at the top of a page."""

    label: str
    value: str
    compare: str = ""
    attention: bool = False


def figures(items: list[Figure]) -> str:
    cells = "".join(
        f'<div class="so-figure{" so-attention" if item.attention else ""}">'
        f'<div class="so-figure-label">{_e(item.label)}</div>'
        f'<div class="so-figure-value">{_e(item.value)}</div>'
        f'<div class="so-figure-compare">{_e(item.compare)}</div></div>'
        for item in items
    )
    return f'<div class="so-figures">{cells}</div>'


def page_header(title: str, subtitle: str, eyebrow: str = "") -> str:
    return (
        (f'<div class="so-eyebrow">{_e(eyebrow)}</div>' if eyebrow else "")
        + f'<div class="so-title">{_e(title)}</div>'
        + f'<div class="so-subtitle">{rich(subtitle)}</div>'
    )


def empty_state(title: str, why: str) -> str:
    """What would be here, and why it is not. Never a blank panel."""
    return (
        f'<div class="so-empty"><div class="so-empty-title">{_e(title)}</div>'
        f'<div class="so-empty-why">{rich(why)}</div></div>'
    )


def quote(text: str, cite: str = "") -> str:
    return (
        '<div class="so-quote">'
        + (f'<span class="so-quote-cite">{_e(cite)}</span>' if cite else "")
        + f"{_e(text)}</div>"
    )


def label(text: str) -> str:
    return f'<div class="so-label">{_e(text)}</div>'


def facts(rows: list[tuple[str, str]]) -> str:
    """A definition list. Values are HTML the caller has already escaped."""
    cells = "".join(f"<dt>{_e(name)}</dt><dd>{value}</dd>" for name, value in rows)
    return f'<dl class="so-facts">{cells}</dl>'


def identity_choices(conn) -> list[dict[str, Any]]:
    """Everyone the selector offers, auditors first, each with a readable label."""
    repo = repositories(conn)
    people = directory.load(conn)
    units = {u.id: u.name for u in repo["units"].list()}
    order = {"pa_infosec": 0, "unit_owner": 1, "management": 2}
    rows = []
    for person in people.all():
        if person.role not in order:
            continue
        unit_name = units.get(person.auditable_unit or "", "")
        rows.append({
            "id": person.id, "name": person.name, "role": person.role,
            "role_label": ROLE_LABELS[person.role],
            "unit": person.auditable_unit or "", "unit_name": unit_name,
            "label": " · ".join(
                part for part in (person.name, ROLE_LABELS[person.role], unit_name)
                if part
            ),
        })
    return sorted(rows, key=lambda r: (order[r["role"]], r["unit_name"], r["name"]))


def _choice(actor: dict[str, Any], choices: list[dict[str, Any]]) -> dict[str, Any]:
    return next((c for c in choices if c["id"] == actor["id"]), {
        "name": actor["name"], "role_label": ROLE_LABELS.get(actor["role"], ""),
        "unit_name": "",
    })


def topbar(actor: dict[str, Any], choices: list[dict[str, Any]], today: date) -> str:
    """The header every page shares: who you are acting as, and when it is."""
    who = _choice(actor, choices)
    identity = " · ".join(part for part in (who["role_label"], who["unit_name"]) if part)
    return (
        '<div class="so-topbar"><div class="so-brand">SentinelOps'
        '<span>Compliance findings and follow-up</span></div><div class="so-chips">'
        f'<span class="so-chip">Acting as <b>{_e(who["name"])}</b> · {_e(identity)}</span>'
        f'<span class="so-chip">Simulated date <b>{_e(fmt_date(today))}</b></span>'
        "</div></div>"
    )


def identity_card(actor: dict[str, Any], choices: list[dict[str, Any]]) -> str:
    who = _choice(actor, choices)
    if actor["may_close"]:
        may = "Answers evidence rounds and closes findings."
    elif actor["may_submit"]:
        may = "Files evidence and reports progress for " + (who["unit_name"] or "their unit") + "."
    else:
        may = "Reads the portfolio. Changes nothing."
    unit = f'<div class="so-who-line">{_e(who["unit_name"])}</div>' if who["unit_name"] else ""
    return (
        f'<div class="so-who"><div class="so-row"><span class="so-who-name">'
        f'{_e(who["name"])}</span>{badge(who["role_label"], "accent")}</div>'
        f'{unit}<div class="so-who-line">{_e(may)}</div></div>'
    )


def calendar_card(today: date) -> str:
    return (
        '<div class="so-label">Simulated date</div>'
        f'<div class="so-date">{_e(fmt_long_date(today))}</div>'
        '<div class="so-date-sub">Business time. Every event and notification is '
        "stamped with it.</div>"
    )


def meter_card(meter: dict[str, Any]) -> str:
    cells = (
        ("Model calls", f"{meter['calls']:,}"),
        ("Tokens", f"{meter['total_tokens']:,}"),
        ("Cost", f"${meter['cost_usd']:.4f}"),
        ("No model", f"{meter['zero_model_share']:.0%}"),
    )
    return (
        '<div class="so-label">Model spend</div><div class="so-meter">'
        + "".join(f"<div><span>{_e(k)}</span><b>{_e(v)}</b></div>" for k, v in cells)
        + "</div>"
    )


# --- navigation, scoped by role -------------------------------------------------

def _page(title: str, script: str, icon: str, *, default: bool = False) -> dict[str, Any]:
    return {"title": title, "path": f"screens/{script}.py", "icon": icon,
            "default": default}


#: The pages each role sees, grouped as the sidebar shows them. The first page
#: of each is where that person lands: the one that answers "what needs me today".
PAGES: dict[str, dict[str, list[dict[str, Any]]]] = {
    "pa_infosec": {
        "Work": [
            _page("Today", "today", ":material/wb_sunny:", default=True),
            _page("Findings", "findings", ":material/list_alt:"),
            _page("Schedule", "schedule", ":material/event:"),
            _page("Inbox", "inbox", ":material/inbox:"),
        ],
        "Insight": [
            _page("Portfolio", "portfolio", ":material/monitoring:"),
            _page("Recurrence", "recurrence", ":material/repeat:"),
        ],
        "Assurance": [
            _page("Audit trail", "audit_trail", ":material/verified_user:"),
            _page("Walkthrough", "walkthrough", ":material/play_circle:"),
        ],
    },
    "unit_owner": {
        "My work": [
            _page("My findings", "my_findings", ":material/assignment:", default=True),
            _page("Finding detail", "owner_detail", ":material/description:"),
            _page("Inbox", "inbox", ":material/inbox:"),
        ],
    },
    "management": {
        "Oversight": [
            _page("Overview", "overview", ":material/dashboard:", default=True),
        ],
    },
}


def pages_for(role: str | None) -> dict[str, list[dict[str, Any]]]:
    """An identity with no recognised role gets the read-only view, never more."""
    return PAGES.get(role or "", PAGES["management"])


def page_paths(role: str | None) -> list[str]:
    return [page["path"] for pages in pages_for(role).values() for page in pages]


# --- findings ---------------------------------------------------------------------

AGEING_BANDS: tuple[str, ...] = (
    "Not yet due", "0–30 days", "31–60 days", "61–90 days", "90+ days",
)


def ageing_band(days_past_target: int, status: str = "open") -> str:
    """Section 8's buckets, for one finding. Due today counts as 0–30, as there."""
    from .. import analytics

    if status != "open":
        return "Closed"
    if days_past_target < 0:
        return "Not yet due"
    for name, low, high in analytics.AGEING_BUCKETS:
        if low <= days_past_target <= high:
            return f"{name.replace('-', '–')} days"
    return AGEING_BANDS[-1]


def open_at(finding, day: date) -> bool:
    """Was this finding open at the end of `day`? Replayed from its dates."""
    if finding.raised_at.date() > day:
        return False
    return finding.closed_at is None or finding.closed_at.date() > day


def escalation_levels(repo) -> dict[str, int]:
    """How far each finding has been escalated, read off the trail."""
    levels: dict[str, int] = {}
    for event in repo["audit"].read_all():
        if event.action == "finding_escalated":
            levels[event.entity_id] = max(
                levels.get(event.entity_id, 0), int(event.detail.get("level", 0))
            )
    return levels


def source_label(finding, audits: dict[str, Any]) -> str:
    if finding.audit_id and finding.audit_id in audits:
        audit = audits[finding.audit_id]
        kind = AUDIT_KIND_LABELS.get(audit.kind, humanise(audit.kind))
        return f"{kind} · {audit.title}" if audit.title else kind
    if finding.source == "activity_assessment":
        return "Compliance activity"
    return humanise(finding.source)


def finding_rows(
    conn, as_of: date, *, unit_id: str | None = None, status: str | None = None,
) -> list[dict[str, Any]]:
    """Findings as the tables show them. Unit and status are filtered in the query."""
    from .. import analytics

    repo = repositories(conn)
    people = directory.load(conn)
    where: dict[str, Any] = {}
    if unit_id:
        where["auditable_unit_id"] = unit_id
    if status:
        where["status"] = status
    units = {u.id: u.name for u in repo["units"].list()}
    audits = {a.id: a for a in repo["audits"].list()}
    levels = escalation_levels(repo)
    rounds: dict[str, list[Any]] = {}
    for record in repo["rounds"].list():
        rounds.setdefault(record.finding_id, []).append(record)

    rows = []
    for finding in repo["findings"].list(**where):
        days = (as_of - finding.target_date).days
        is_open = finding.status == "open"
        severity = finding.severity or finding.suggested_severity or ""
        mine = sorted(rounds.get(finding.id, []), key=lambda r: r.round_number)
        rows.append({
            "id": finding.id,
            "description": finding.description,
            "unit": units.get(finding.auditable_unit_id, finding.auditable_unit_id),
            "unit_id": finding.auditable_unit_id,
            "severity": severity,
            "status": finding.status,
            "progress": finding.owner_progress,
            "owner": people.name(finding.owner_identity),
            "owner_id": finding.owner_identity,
            "raised": finding.raised_at.date(),
            "target": finding.target_date,
            "days_past": days,
            "timing": due_phrase(days) if is_open else f"Closed {fmt_date(finding.closed_at)}",
            "ageing": ageing_band(days, finding.status),
            "chased": finding.follow_up_count,
            "rounds": len(mine),
            "latest_response": mine[-1].auditor_response if mine else None,
            "recurrence": len(finding.recurrence_of),
            "chronic": is_open and analytics.is_chronic(days),
            "escalation": levels.get(finding.id, 0) if is_open else 0,
            "source": source_label(finding, audits),
            "category": (finding.gap_category or "unclassified").replace("_", " "),
        })
    return sorted(rows, key=lambda r: (r["status"] != "open", r["target"], r["id"]))


def filter_findings(
    rows: list[dict[str, Any]], *, severities=None, ageing: str | None = None,
) -> list[dict[str, Any]]:
    return [
        row for row in rows
        if (not severities or row["severity"] in severities)
        and (not ageing or row["ageing"] == ageing)
    ]


def my_findings(
    conn, identity_id: str, as_of: date, *, include_closed: bool = False,
) -> list[dict[str, Any]]:
    """One owner's unit, soonest target first. The unit is the query's filter."""
    identity = directory.load(conn).get(identity_id)
    if identity is None or not identity.auditable_unit:
        return []
    rows = finding_rows(
        conn, as_of, unit_id=identity.auditable_unit,
        status=None if include_closed else "open",
    )
    return sorted(rows, key=lambda r: (r["target"], r["id"]))


def unit_name(conn, unit_id: str | None) -> str:
    unit = repositories(conn)["units"].get(unit_id) if unit_id else None
    return unit.name if unit else ""


def owner_checks(conn, unit_id: str, as_of: date) -> list[dict[str, Any]]:
    """Compliance checks awaiting evidence from one unit, soonest due first."""
    repo = repositories(conn)
    controls = {c.id: c.title for c in repo["controls"].list()}
    rows = [
        {
            "id": instance.id,
            "activity": controls.get(instance.control_id, instance.control_id),
            "period": instance.period,
            "due": instance.due_date,
            "status": instance.status,
            "days_past": (as_of - instance.due_date).days,
        }
        for instance in repo["instances"].list(auditable_unit_id=unit_id)
        if instance.status in ("pending", "overdue", "assessed")
    ]
    return sorted(rows, key=lambda r: (r["due"], r["id"]))


def overdue_rows(conn, as_of: date) -> list[dict[str, Any]]:
    """Open findings at or past target, most severe first, then longest late."""
    rank = {severity: i for i, severity in enumerate(SEVERITIES)}
    rows = [r for r in finding_rows(conn, as_of, status="open") if r["days_past"] >= 0]
    return sorted(rows, key=lambda r: (rank.get(r["severity"], len(rank)),
                                       -r["days_past"], r["id"]))


def escalated_rows(conn, as_of: date) -> list[dict[str, Any]]:
    rows = [r for r in finding_rows(conn, as_of, status="open") if r["escalation"]]
    return sorted(rows, key=lambda r: (-r["escalation"], -r["days_past"], r["id"]))


def review_queue(conn, as_of: date) -> list[dict[str, Any]]:
    """Evidence rounds waiting for an auditor, oldest first, with the advisory reading."""
    from ..stages import review

    repo = repositories(conn)
    people = directory.load(conn)
    units = {u.id: u.name for u in repo["units"].list()}
    findings = {f.id: f for f in repo["findings"].list()}
    rows = []
    for record in repo["rounds"].list(auditor_response="pending"):
        finding = findings.get(record.finding_id)
        if finding is None:
            continue
        recommendation = review.recommendation_for(conn, record.id)
        rows.append({
            "id": record.id,
            "round": record,
            "finding_id": finding.id,
            "description": finding.description,
            "action_plan": finding.agreed_action_plan,
            "unit": units.get(finding.auditable_unit_id, finding.auditable_unit_id),
            "severity": finding.severity or finding.suggested_severity or "",
            "round_number": record.round_number,
            "submitted_by": person(people, record.submitted_by),
            "submitted_at": record.submitted_at,
            "waiting_days": max((as_of - record.submitted_at.date()).days, 0),
            "evidence_ref": record.evidence_ref,
            "evidence_text": record.evidence_text,
            "note": record.owner_note,
            "recommendation": recommendation,
            "suggests": review.SUGGESTS.get(recommendation.verdict) if recommendation else None,
        })
    return sorted(rows, key=lambda r: (-r["waiting_days"], r["id"]))


# --- the figures at the top of each page ----------------------------------------------

def today_figures(conn, as_of: date) -> list[Figure]:
    from .. import analytics

    repo = repositories(conn)
    findings = repo["findings"].list()
    earlier = as_of - timedelta(days=30)
    open_now = [f for f in findings if f.status == "open"]
    open_before = sum(1 for f in findings if open_at(f, earlier))
    overdue_now = [f for f in open_now if f.target_date <= as_of]
    overdue_before = sum(1 for f in findings
                         if open_at(f, earlier) and f.target_date <= earlier)
    pending = repo["rounds"].list(auditor_response="pending")
    oldest_wait = max(((as_of - r.submitted_at.date()).days for r in pending), default=0)
    chronic = analytics.chronic_findings(repo, as_of)
    return [
        Figure("Awaiting your review", str(len(pending)),
               f"Oldest waiting {plural(oldest_wait, 'day')}" if pending
               else "No evidence round is unanswered", attention=bool(pending)),
        Figure("Overdue findings", str(len(overdue_now)),
               delta_phrase(len(overdue_now), overdue_before, earlier),
               attention=bool(overdue_now)),
        Figure("Open findings", str(len(open_now)),
               delta_phrase(len(open_now), open_before, earlier)),
        Figure("Chronic", str(len(chronic)),
               f"Open more than {analytics.CHRONIC_DAYS} days past target"),
    ]


def owner_figures(conn, identity_id: str, as_of: date) -> list[Figure]:
    rows = my_findings(conn, identity_id, as_of)
    ids = {r["id"] for r in rows}
    pending = [r for r in repositories(conn)["rounds"].list(auditor_response="pending")
               if r.finding_id in ids]
    overdue = [r for r in rows if r["days_past"] >= 0]
    soon = [r for r in rows if -14 <= r["days_past"] < 0]
    return [
        Figure("Open findings", str(len(rows)), "Raised against your unit"),
        Figure("Overdue", str(len(overdue)),
               f"Oldest {plural(max(r['days_past'] for r in overdue), 'day')} late"
               if overdue else "Nothing past its target date", attention=bool(overdue)),
        Figure("Due in 14 days", str(len(soon)), "Target date within two weeks"),
        Figure("With PA/InfoSec", str(len(pending)), "Evidence rounds awaiting review"),
    ]


def management_figures(conn, as_of: date) -> list[Figure]:
    from .. import analytics

    repo = repositories(conn)
    findings = repo["findings"].list()
    earlier = as_of - timedelta(days=30)
    rows = finding_rows(conn, as_of, status="open")
    escalated = [r for r in rows if r["escalation"]]
    overdue = [r for r in rows if r["days_past"] >= 0]
    overdue_before = sum(1 for f in findings
                         if open_at(f, earlier) and f.target_date <= earlier)
    split = analytics.open_vs_closed(repo)
    return [
        Figure("Escalated findings", str(len(escalated)),
               f"Highest at level {max(r['escalation'] for r in escalated)}"
               if escalated else "Nothing escalated", attention=bool(escalated)),
        Figure("Overdue findings", str(len(overdue)),
               delta_phrase(len(overdue), overdue_before, earlier)),
        Figure("Open findings", str(split["open"]),
               f"{split['closed_pct']:g}% of {split['total']} raised are closed"),
        Figure("Oldest overdue", plural(max((r["days_past"] for r in overdue), default=0), "day"),
               "Past its target date"),
    ]


def month_cuts(as_of: date, months: int) -> list[date]:
    """Month ends leading up to `as_of`, which stands in for the current month's end."""
    cuts = [as_of]
    cursor = date(as_of.year, as_of.month, 1) - timedelta(days=1)
    while len(cuts) < months:
        cuts.append(cursor)
        cursor = date(cursor.year, cursor.month, 1) - timedelta(days=1)
    return list(reversed(cuts))


def unit_trend(conn, as_of: date, months: int = 12) -> list[dict[str, Any]]:
    """Per unit: open now, open at each month end, and how the last quarter moved."""
    repo = repositories(conn)
    findings = repo["findings"].list()
    cuts = month_cuts(as_of, months)
    rows = []
    for unit in repo["units"].list():
        mine = [f for f in findings if f.auditable_unit_id == unit.id]
        if not mine:
            continue
        series = [sum(1 for f in mine if open_at(f, cut)) for cut in cuts]
        still_open = [f for f in mine if f.status == "open"]
        overdue = [f for f in still_open if f.target_date <= as_of]
        rows.append({
            "unit": unit.name,
            "open": len(still_open),
            "trend": series,
            "change": series[-1] - series[-4] if len(series) >= 4 else 0,
            "overdue": len(overdue),
            "oldest": max(((as_of - f.target_date).days for f in overdue), default=0),
            "closed_pct": round(100 * (len(mine) - len(still_open)) / len(mine), 1),
        })
    return sorted(rows, key=lambda r: (-r["open"], r["unit"]))


# --- the inbox -----------------------------------------------------------------------

INBOX_FILTERS: dict[str, Any] = {
    "All": None,
    "Unread": "unread",
    "Escalations": {"escalation"},
    "Reminders": {"reminder", "overdue"},
    "Evidence": {"evidence_requested", "evidence_submitted"},
    "Closures": {"closure"},
}


def inbox_rows(conn, identity_id: str, as_of: date | None = None) -> list[dict[str, Any]]:
    """One identity's notifications, newest first.

    With `as_of`, nothing sent after it. The seeded audit programme writes its
    closures — and the notifications about them — ahead of the calendar, so at
    the demo's start date an inbox would otherwise open on messages from next
    year.
    """
    from .. import notify

    return [
        {
            "id": note.id, "unread": note.unread, "sent": note.sent_at,
            "kind": note.kind, "kind_label": KIND_LABELS.get(note.kind, humanise(note.kind)),
            "subject": note.subject, "body": note.body, "about": note.related_entity,
            "level": note.escalation_level,
        }
        for note in notify.inbox(conn, identity_id)
        if as_of is None or note.sent_at.date() <= as_of
    ]


def filter_inbox(rows: list[dict[str, Any]], choice: str) -> list[dict[str, Any]]:
    wanted = INBOX_FILTERS.get(choice)
    if wanted is None:
        return rows
    if wanted == "unread":
        return [r for r in rows if r["unread"]]
    return [r for r in rows if r["kind"] in wanted]


def inbox_figures(rows: list[dict[str, Any]], as_of: date) -> list[Figure]:
    week = as_of - timedelta(days=7)
    unread = [r for r in rows if r["unread"]]
    return [
        Figure("Unread", str(len(unread)), f"Of {plural(len(rows), 'notification')}",
               attention=bool(unread)),
        Figure("Escalations", str(sum(1 for r in rows if r["kind"] == "escalation")),
               "Sent to you, all time"),
        Figure("Last 7 days", str(sum(1 for r in rows if r["sent"].date() > week)),
               f"Since {fmt_date(week)}"),
    ]


# --- one finding in full -----------------------------------------------------------------

def finding_timeline(conn, finding_id: str) -> list[dict[str, Any]]:
    """Every event touching a finding, its rounds and notifications — and its check."""
    repo = repositories(conn)
    finding = repo["findings"].get(finding_id)
    if finding is None:
        return []
    wanted = {finding_id} | {r.id for r in repo["rounds"].list(finding_id=finding_id)}
    wanted |= {n.id for n in repo["notifications"].list(related_entity=finding_id)}
    rows = timeline(conn, finding.check_instance_id) if finding.check_instance_id else []
    seen = {row["seq"] for row in rows}
    for event in repo["audit"].read_all():
        if event.seq in seen:
            continue
        if event.entity_id in wanted or (event.detail or {}).get("finding_id") == finding_id:
            rows.append({
                "seq": event.seq, "when": event.ts, "actor": event.actor_kind,
                "owner": event.owner, "event": event.action,
                "entity": f"{event.entity_type}:{event.entity_id}",
                "detail": event.detail,
            })
    return sorted(rows, key=lambda r: r["seq"])


def finding_record(conn, finding_id: str, as_of: date) -> dict[str, Any] | None:
    from .. import analytics
    from ..stages import review
    from ..stages import rounds as rounds_stage

    repo = repositories(conn)
    finding = repo["findings"].get(finding_id)
    if finding is None:
        return None
    people = directory.load(conn)
    units = {u.id: u.name for u in repo["units"].list()}
    audits = {a.id: a for a in repo["audits"].list()}
    everything = {f.id: f for f in repo["findings"].list()}
    days = (as_of - finding.target_date).days
    return {
        "finding": finding,
        "unit": units.get(finding.auditable_unit_id, finding.auditable_unit_id),
        "owner": people.name(finding.owner_identity),
        "raised_by": person(people, finding.raised_by),
        "closed_by": person(people, finding.closed_by) if finding.closed_by else "",
        "source": source_label(finding, audits),
        "days_past": days,
        "chronic": finding.status == "open" and analytics.is_chronic(days),
        "escalation": escalation_levels(repo).get(finding.id, 0),
        "rounds": [
            {
                "round": record,
                "recommendation": review.recommendation_for(conn, record.id),
                "submitted_by": person(people, record.submitted_by),
                "responded_by": person(people, record.responded_by) if record.responded_by else "",
            }
            for record in rounds_stage.rounds_for(repo, finding.id)
        ],
        "activity": (finding_detail(conn, finding.check_instance_id)
                     if finding.check_instance_id else None),
        "priors": [
            {"finding": everything[p], "unit": units.get(everything[p].auditable_unit_id, "")}
            for p in finding.recurrence_of if p in everything
        ],
        "later": [
            {"finding": f, "unit": units.get(f.auditable_unit_id, "")}
            for f in everything.values() if finding.id in f.recurrence_of
        ],
        "timeline": finding_timeline(conn, finding.id),
    }


def finding_heading(record: dict[str, Any]) -> str:
    finding = record["finding"]
    badges = [
        severity_badge(finding.severity or finding.suggested_severity),
        status_badge(finding.status),
        progress_badge(finding.owner_progress),
        chronic_badge() if record["chronic"] else "",
        escalation_badge(record["escalation"]) if finding.status == "open" else "",
    ]
    return (
        f'<div class="so-row"><span class="so-id">{_e(finding.id)}</span>'
        + "".join(badges)
        + f'</div><div class="so-finding-title">{_e(finding.description)}</div>'
    )


def finding_facts(record: dict[str, Any]) -> str:
    finding = record["finding"]
    timing = (due_phrase(record["days_past"]) if finding.status == "open"
              else f"Closed {fmt_date(finding.closed_at)} by {record['closed_by']}")
    rows = [
        ("Unit", _e(record["unit"])),
        ("Owner", _e(record["owner"])),
        ("Raised", _e(f"{fmt_date(finding.raised_at)} by {record['raised_by']}")),
        ("Target", _e(f"{fmt_date(finding.target_date)} · {timing}")),
        ("Source", _e(record["source"])),
        ("Gap category", _e((finding.gap_category or "unclassified").replace("_", " "))),
        ("Chased", _e(plural(finding.follow_up_count, "time"))),
        ("Evidence rounds", _e(len(record["rounds"]))),
    ]
    if finding.severity and finding.suggested_severity and finding.severity != finding.suggested_severity:
        rows.insert(2, ("Severity", _e(f"{finding.severity}, assigned by the auditor · "
                                        f"the model suggested {finding.suggested_severity}")))
    if finding.status == "closed" and finding.closure_remarks:
        rows.append(("Closure remarks", _e(finding.closure_remarks)))
    return facts(rows)


def assessment_summary(assessment) -> str:
    parts = [
        verdict_badge(assessment.verdict),
        f'<span class="so-muted">Confidence {assessment.confidence:.2f}</span>',
        f'<span class="so-muted">{_e(DECIDED_BY_LABELS.get(assessment.decided_by, humanise(assessment.decided_by)))}</span>',
    ]
    if assessment.needs_human_review:
        parts.append(badge("Needs human review", "outline"))
    body = f'<div class="so-row">{"".join(parts)}</div>'
    if assessment.rationale:
        body += f'<div class="so-reason">{_e(assessment.rationale)}</div>'
    if assessment.gaps:
        body += "<ul>" + "".join(f"<li>{_e(gap)}</li>" for gap in assessment.gaps) + "</ul>"
    return body


def advisory(recommendation, suggests: str | None = None) -> str:
    """The model's reading of a round. Shown as advice, because it is advice."""
    if recommendation is None:
        return empty_state(
            "No advisory reading",
            "This round was not read by the model — it may have been filed without "
            "text to read. The decision is the auditor's either way.",
        )
    suggestion = suggests or ""
    body = (
        f'<div class="so-advisory">{label("Advisory reading")}'
        f'<div class="so-row">{verdict_badge(recommendation.verdict)}'
        + (f'<span class="so-muted">suggests {_e(RESPONSE_LABELS.get(suggestion, suggestion)).lower()}</span>'
           if suggestion else "")
        + f'<span class="so-muted">confidence {recommendation.confidence:.2f}</span></div>'
    )
    if recommendation.rationale:
        body += f'<div class="so-reason">{_e(recommendation.rationale)}</div>'
    if recommendation.gaps:
        body += "<ul>" + "".join(f"<li>{_e(gap)}</li>" for gap in recommendation.gaps) + "</ul>"
    return body + '<div class="so-muted">The auditor decides.</div></div>'


def review_item(item: dict[str, Any]) -> str:
    round_badge = badge(f"Round {item['round_number']}", "outline")
    return (
        f'<div class="so-row"><span class="so-id">{_e(item["finding_id"])}</span>'
        f'{severity_badge(item["severity"])}{round_badge}'
        f'<span class="so-muted">{_e(item["unit"])}</span></div>'
        f'<div class="so-finding-title">{_e(item["description"])}</div>'
        f'<div class="so-muted">Filed by {_e(item["submitted_by"])} on '
        f'{_e(fmt_date(item["submitted_at"]))} · waiting {_e(plural(item["waiting_days"], "day"))}'
        f' · {_e(item["evidence_ref"])}</div>'
        + (quote(item["note"], "Note from the owner") if item["note"] else "")
        + (quote(item["action_plan"], "Agreed action plan") if item["action_plan"] else "")
        + advisory(item["recommendation"], item["suggests"])
    )


def recurrence_for(record: dict[str, Any]) -> str:
    """This finding beside the ones it resembles, earlier on the left of time."""
    finding = record["finding"]
    blocks = []
    for prior in record["priors"]:
        blocks.append(recurrence_pair(
            finding, record["unit"], prior["finding"], prior["unit"]))
    for later in record["later"]:
        blocks.append(recurrence_pair(
            later["finding"], later["unit"], finding, record["unit"]))
    return "".join(f'<div class="so-item">{block}</div>' for block in blocks)


def recurrence_pair(new, new_unit: str, earlier, earlier_unit: str, reason: str = "") -> str:
    months = max((new.raised_at - earlier.raised_at).days // 30, 0)

    def side(title: str, finding, unit: str) -> str:
        return (
            f'<div>{label(title)}<div class="so-row"><span class="so-id">{_e(finding.id)}</span>'
            f'{severity_badge(finding.severity or finding.suggested_severity)}'
            f'<span class="so-muted">{_e(unit)} · raised {_e(fmt_date(finding.raised_at))}</span></div>'
            f'{quote(finding.description)}</div>'
        )

    earlier_title = f"Earlier occurrence · {plural(months, 'month')} before"
    return (
        f'<div class="so-pair">{side("New occurrence", new, new_unit)}'
        f'{side(earlier_title, earlier, earlier_unit)}</div>'
        + (f'<div class="so-muted">Why they were linked: {_e(reason)}</div>' if reason else "")
    )


def chronic_list(alert: dict[str, Any]) -> str:
    return "".join(
        f'<div class="so-item"><div class="so-row"><span class="so-id">{_e(row["id"])}</span>'
        f'{severity_badge(row["severity"])}{chronic_badge()}</div>'
        f'<div class="so-muted">{_e(row["unit"])} · {_e(plural(row["days_past_target"], "day"))} '
        f'past its target of {_e(fmt_date(row["target_date"]))} · chased '
        f'{_e(plural(row["follow_ups"], "time"))} · {_e(row["owner"])}</div></div>'
        for row in alert["findings"]
    )


def audit_list(audits: list[dict[str, Any]]) -> str:
    return "".join(
        f'<div class="so-item"><div class="so-row">{badge(AUDIT_KIND_LABELS.get(a["kind"], humanise(a["kind"])), "outline")}'
        f'<span class="so-id">{_e(a["id"])}</span></div>'
        f'<div class="so-finding-title">{_e(a["title"] or AUDIT_KIND_LABELS.get(a["kind"], a["kind"]))}</div>'
        f'<div class="so-muted">{_e(fmt_long_date(a["planned"]))} · in {_e(plural(a["days_away"], "day"))}'
        f' · {_e(", ".join(a["scope"]))}</div></div>'
        for a in audits
    )


def trend_reads(verdict: dict[str, Any]) -> str:
    """Section 8's two reads of the trend, side by side, each with its rule."""
    whole = verdict.get("direction", "insufficient_history")
    if whole == "insufficient_history":
        across = "Needs at least two months of findings."
    else:
        across = (
            f"{verdict['slope_per_month']:+.2f} open findings a month · "
            f"{month_label(verdict['first']['month'])} {verdict['first']['open']} → "
            f"{month_label(verdict['last']['month'])} {verdict['last']['open']}"
        )
    recent = verdict.get("recent", {})
    latest = recent.get("direction", "insufficient_history")
    if latest == "insufficient_history":
        quarter = "Needs six months of findings."
    else:
        quarter = (
            f"Mean {recent['last_quarter_mean']:g} open, against "
            f"{recent['previous_quarter_mean']:g} the quarter before"
        )
    return (
        '<div class="so-pair">'
        f'<div class="so-read">{label("Across the window")}'
        f'<div class="so-read-value">{_e(DIRECTION_LABELS.get(whole, humanise(whole)))}</div>'
        f'<div class="so-muted">{_e(across)}</div></div>'
        f'<div class="so-read">{label("Last quarter")}'
        f'<div class="so-read-value">{_e(DIRECTION_LABELS.get(latest, humanise(latest)))}</div>'
        f'<div class="so-muted">{_e(quarter)}</div></div></div>'
    )


def brief_priorities(brief) -> str:
    rows = {row["id"]: row for row in brief.ranked}
    items = []
    for item in brief.top_priorities:
        row = rows.get(item["finding_id"], {})
        items.append(
            f'<div class="so-priority"><div class="so-rank">{item["rank"]}</div><div>'
            f'<div class="so-row"><span class="so-id">{_e(item["finding_id"])}</span>'
            f'{severity_badge(row.get("band"))}{chronic_badge() if row.get("chronic") else ""}'
            f'<span class="so-muted">{_e(row.get("unit", ""))} · {_e(row.get("timing_label", ""))}'
            f' · {item["score"]:g} points</span></div>'
            f'<div class="so-reason">{rich(item["reason"])}</div></div></div>'
        )
    return "".join(items)


def claims(entries: list[dict[str, Any]], metrics: dict[str, Any], empty: str) -> str:
    if not entries:
        return f'<div class="so-muted">{_e(empty)}</div>'
    return "".join(
        f'<div class="so-item">{rich(claim["statement"])}<div>'
        + "".join(f'<span class="so-cite">{_e(i)}</span>' for i in claim["finding_ids"])
        + "".join(f'<span class="so-cite">{_e(m)} = {_e(metrics.get(m))}</span>'
                  for m in claim["metrics"])
        + "</div></div>"
        for claim in entries
    )


def reassess_message(outcome) -> str:
    if outcome.new_assessment_id:
        return (
            f"Re-checked: **{outcome.verdict}** — {outcome.new_assessment_id} "
            f"supersedes {outcome.superseded_assessment_id}."
            + (" The finding closed." if outcome.resolved else " The finding stayed open.")
        )
    return outcome.reason


def evidence_line(evidence) -> str:
    return (
        f"{evidence.id} · {evidence.doc_type.replace('_', ' ')} · filed "
        f"{fmt_date(evidence.submitted_at)} by {evidence.author}"
        + (" · remediation" if evidence.is_remediation else "")
    )


# --- tables: one row shape per table, with labels rather than enums ------------------------

def findings_table(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "Finding": r["id"], "Severity": [r["severity"]] if r["severity"] else [],
            "Status": [STATUS_LABELS[r["status"]]], "Unit": r["unit"],
            "Owner": r["owner"], "Target": r["target"], "Timing": r["timing"],
            "Ageing": r["ageing"], "Progress": PROGRESS_LABELS.get(r["progress"], ""),
            "Chased": r["chased"], "Rounds": r["rounds"], "Chronic": r["chronic"],
        }
        for r in rows
    ]


def overdue_table(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "Finding": r["id"], "Severity": [r["severity"]] if r["severity"] else [],
            "Unit": r["unit"], "Late": r["days_past"],
            "Escalation": f"Level {r['escalation']}" if r["escalation"] else "Not escalated",
            "Owner": r["owner"], "Chased": r["chased"],
        }
        for r in rows
    ]


def owner_table(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "Finding": r["id"], "Severity": [r["severity"]] if r["severity"] else [],
            "Target": r["target"], "Timing": r["timing"],
            "Your progress": PROGRESS_LABELS.get(r["progress"], ""),
            "Latest round": ([RESPONSE_LABELS[r["latest_response"]]]
                             if r["latest_response"] else []),
            "Chased": r["chased"],
        }
        for r in rows
    ]


def ranking_table(ranked: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {"Rank": r["rank"], "Finding": r["id"], "Band": [r["band"]], "Unit": r["unit"],
         "Points": r["score"], "Timing": r["timing_label"], "Chronic": r["chronic"]}
        for r in ranked
    ]


def round_table(record: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "Round": row["round"].round_number, "Filed": row["round"].submitted_at,
            "Filed by": row["submitted_by"], "Evidence": row["round"].evidence_ref,
            "Response": [RESPONSE_LABELS[row["round"].auditor_response]],
            "Answered by": row["responded_by"] or "—",
            "Answered": row["round"].responded_at,
        }
        for row in record["rounds"]
    ]


def timeline_table(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {"#": r["seq"], "When": r["when"], "Event": humanise(r["event"]),
         "Actor": ACTOR_LABELS.get(r["actor"], humanise(r["actor"])),
         "By": r["owner"], "Record": r["entity"]}
        for r in rows
    ]


def inbox_table(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {"Status": ["Unread" if r["unread"] else "Read"], "Sent": r["sent"],
         "Kind": [r["kind_label"]],
         "Subject": r["subject"], "About": r["about"]}
        for r in rows
    ]


def unit_trend_table(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {"Unit": r["unit"], "Open": r["open"], "Last 12 months": r["trend"],
         "3-month change": r["change"], "Overdue": r["overdue"],
         "Oldest overdue": r["oldest"], "Closed": r["closed_pct"]}
        for r in rows
    ]


def activity_table(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {"Due": r["due"], "In": r["days_away"], "Activity": r["control"],
         "Unit": r["unit"], "Period": r["period"]}
        for r in rows
    ]


def check_table(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {"Activity": r["activity"], "Period": r["period"], "Due": r["due"],
         "Status": CHECK_STATUS_LABELS.get(r["status"], humanise(r["status"])),
         "Timing": due_phrase(r["days_past"])}
        for r in rows
    ]


def upcoming_list(upcoming: dict[str, Any], limit: int = 5) -> str:
    """Audits and activities falling due soonest, as one short list."""
    entries = [
        (audit["planned"], 0,
         audit["title"] or AUDIT_KIND_LABELS.get(audit["kind"], humanise(audit["kind"])),
         AUDIT_KIND_LABELS.get(audit["kind"], humanise(audit["kind"]))
         + " · " + ", ".join(audit["scope"]),
         audit["days_away"])
        for audit in upcoming["audits"]
    ] + [
        (activity["due"], 1, activity["control"],
         "Evidence due · " + activity["unit"] + " · " + activity["period"],
         activity["days_away"])
        for activity in upcoming["activities"]
    ]
    entries.sort(key=lambda entry: (entry[0], entry[1], entry[2]))
    rows = []
    for day, _, title, where, days in entries[:limit]:
        when = "today" if days == 0 else "in " + plural(days, "day")
        rows.append(
            f'<div class="so-item so-line"><div><div class="so-line-title">{_e(title)}</div>'
            f'<div class="so-muted">{_e(where)}</div></div><div class="so-line-meta">'
            f'{_e(fmt_date(day))}<span>{_e(when)}</span></div></div>'
        )
    return "".join(rows)


def inbox_preview(rows: list[dict[str, Any]], limit: int = 5) -> str:
    """The newest few notifications, for a side panel."""
    items = []
    for row in rows[:limit]:
        unread = badge("Unread", "accent") if row["unread"] else ""
        items.append(
            f'<div class="so-item so-line"><div><div class="so-row">'
            f'{badge(row["kind_label"], "outline")}{unread}</div>'
            f'<div class="so-line-title">{_e(row["subject"])}</div></div>'
            f'<div class="so-line-meta">{_e(fmt_date(row["sent"]))}'
            f'<span>{row["sent"]:%H:%M}</span></div></div>'
        )
    return "".join(items)


# --- sidebar badges: something here is waiting for you ---------------------------------

#: A badge stops counting here. Past it the number is not information.
BADGE_CAP = 99


def nav_badges(conn, actor: dict[str, Any], as_of: date) -> dict[str, int]:
    """Per page, how many things on it are waiting for this identity.

    Only what asks something of the person: rounds waiting for a decision,
    findings past target, work falling due this week, unread messages. A badge
    that counts things nobody has to act on teaches people to ignore badges.
    """
    from .. import analytics

    repo = repositories(conn)
    unread = sum(1 for row in inbox_rows(conn, actor["id"], as_of=as_of) if row["unread"])
    if actor["role"] == "pa_infosec":
        week = analytics.upcoming(repo, as_of, horizon_days=7)
        return {
            "screens/today.py": len(repo["rounds"].list(auditor_response="pending")),
            "screens/findings.py": len(overdue_rows(conn, as_of)),
            "screens/schedule.py": len(week["audits"]) + week["activity_total"],
            "screens/inbox.py": unread,
        }
    if actor["role"] == "unit_owner":
        mine = my_findings(conn, actor["id"], as_of)
        return {
            "screens/my_findings.py": sum(1 for row in mine if row["days_past"] >= 0),
            "screens/owner_detail.py": sum(
                1 for row in mine if row["latest_response"] == "insufficient"
            ),
            "screens/inbox.py": unread,
        }
    return {"screens/overview.py": len(escalated_rows(conn, as_of))}


def nav_badge_css(role: str | None, counts: dict[str, int]) -> str:
    """A count beside each sidebar page that has something waiting.

    Streamlit's navigation renders page names as plain text, so the badge is a
    pseudo-element keyed on each link's address: the default page is served at
    the root, every other page at its script's name. Only digits ever reach the
    stylesheet, so nothing a record contains can.
    """
    rules = []
    for pages in pages_for(role).values():
        for page in pages:
            count = int(counts.get(page["path"], 0))
            if count <= 0:
                continue
            text = f"{BADGE_CAP}+" if count > BADGE_CAP else str(count)
            stem = page["path"].rsplit("/", 1)[-1].removesuffix(".py")
            suffix = "/" if page["default"] else f"/{stem}"
            rules.append(
                f'[data-testid="stSidebarNavLink"][href$="{suffix}"]::after '
                f'{{ content: "{text}"; }}'
            )
    return f"<style>{''.join(rules)}</style>" if rules else ""


def notification_header(note: dict[str, Any]) -> str:
    """Kind, read state, when and about what — then the subject."""
    unread = badge("Unread", "accent") if note["unread"] else ""
    return (
        f'<div class="so-row">{badge(note["kind_label"], "outline")}{unread}'
        f'<span class="so-muted">{_e(fmt_when(note["sent"]))} · about {_e(note["about"])}'
        f'</span></div><div class="so-finding-title">{_e(note["subject"])}</div>'
    )
