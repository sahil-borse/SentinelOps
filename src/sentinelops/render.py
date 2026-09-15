"""The brief and the audit report, rendered for a reader. Deterministic.

Nothing here generates text. The only model-written words on either page are
the brief's claims and the report's summary paragraph, and both arrive already
validated: a brief with an unattributable claim is withheld before it gets here,
and so is a summary. What this module adds is layout, the citations resolved to
what they point at, and the deterministic scaffolding — the ranking and the
formula behind the brief, the structured findings behind the report.

**A withheld draft is never quoted.** When a brief or a summary is rejected the
page says so and how many problems were found, and the reasons go to the audit
trail. Quoting a rejected statement — "cites FND-99, which this audit did not
raise: the audit found a systemic weakness" — would publish the very claim that
was withheld, with a citation's authority.

Markdown for anywhere, and a self-contained HTML page for the screen and the
video: no external stylesheet, no script, nothing fetched.
"""

from __future__ import annotations

import html
from typing import Any

from . import priority

STYLE = """
:root { color-scheme: light; }
body { margin: 0; background: #f6f5f1; color: #1d2330;
       font: 15px/1.55 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; }
main { max-width: 860px; margin: 0 auto; padding: 36px 20px 64px; }
header { border-bottom: 2px solid #1d2330; padding-bottom: 14px; margin-bottom: 26px; }
h1 { font-size: 26px; line-height: 1.2; margin: 0 0 6px; }
h2 { font-size: 17px; margin: 30px 0 10px; letter-spacing: .01em; }
h3 { font-size: 15px; margin: 22px 0 6px; }
.meta { color: #5b6272; font-size: 13px; }
.chip { display: inline-block; font: 12px/1.6 ui-monospace, Consolas, monospace;
        background: #e8e6de; border-radius: 4px; padding: 0 6px; margin: 0 2px 2px 0;
        white-space: nowrap; }
.metric { background: #e3ebf5; }
ol, ul { padding-left: 22px; }
li { margin: 0 0 12px; }
.reason { display: block; margin-top: 2px; }
.cites { display: block; color: #5b6272; font-size: 13px; margin-top: 3px; }
table { border-collapse: collapse; width: 100%; font-size: 14px; margin: 6px 0 12px; }
th, td { text-align: left; padding: 6px 8px; border-bottom: 1px solid #dcd9cf;
         vertical-align: top; }
th { font-weight: 600; color: #3a4150; }
td.num { text-align: right; font-variant-numeric: tabular-nums; }
pre { background: #fff; border: 1px solid #dcd9cf; border-radius: 6px; padding: 12px 14px;
      overflow-x: auto; font: 12.5px/1.5 ui-monospace, Consolas, monospace; }
.note { background: #fff; border-left: 3px solid #8a93a6; padding: 10px 14px; margin: 14px 0; }
.withheld { background: #fdf1ee; border-left: 3px solid #b3472f; padding: 10px 14px; }
.finding { background: #fff; border: 1px solid #dcd9cf; border-radius: 6px;
           padding: 12px 16px; margin: 0 0 12px; }
.table-wrap { overflow-x: auto; }
@media print { body { background: #fff; } .finding, pre { break-inside: avoid; } }
"""


def _e(value: Any) -> str:
    return html.escape(str(value), quote=True)


def page(title: str, body: str) -> str:
    return (
        "<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        f"<title>{_e(title)}</title><style>{STYLE}</style></head>"
        f"<body><main>{body}</main></body></html>\n"
    )


def withheld_note(problems: list[str], what: str) -> str:
    """A rejection stated without repeating what was rejected."""
    return (
        f"The drafted {what} was withheld: {len(problems)} problem(s) were found. "
        f"They are recorded on the audit trail rather than quoted here, because "
        f"quoting a rejected statement would publish it."
    )


# --- the brief ------------------------------------------------------------------

def _rows_by_id(brief) -> dict[str, dict[str, Any]]:
    return {row["id"]: row for row in brief.ranked}


def _timing(row: dict[str, Any]) -> str:
    """The timing, with the chronic flag beside it. The flag never moves a row."""
    return row["timing_label"] + (", chronic" if row.get("chronic") else "")


def _cites_text(claim: dict[str, Any], metrics: dict[str, Any]) -> str:
    parts = list(claim["finding_ids"])
    parts += [f"{name} = {metrics.get(name)}" for name in claim["metrics"]]
    return "; ".join(parts)


def _metrics_given(brief) -> str:
    listed = sum(1 for name in brief.metrics if name.startswith("listed_"))
    return (
        f"{len(brief.metrics) - listed} section 8 metrics and {listed} counts over "
        f"the listed rows"
    )


def brief_markdown(brief) -> str:
    rows = _rows_by_id(brief)
    out = [
        f"# Prioritisation brief — {brief.as_of}",
        "",
        f"Advisory; changes no state. {brief.model_calls} model call over the top "
        f"{min(len(brief.ranked), 12)} of {len(brief.ranked)} open findings, "
        f"{_metrics_given(brief)} ({brief.prompt_version}).",
        "",
    ]
    if brief.withheld:
        out += [
            "## Withheld", "",
            withheld_note(brief.withheld, "brief"),
            "The ranking below is unaffected; it came from no model.",
            "",
        ]
    elif brief.published:
        out += ["## Top priorities", ""]
        for item in brief.top_priorities:
            row = rows[item["finding_id"]]
            out.append(
                f"{item['rank']}. **{item['finding_id']}** — {row['unit']}, "
                f"{row['band']}, {_timing(row)} ({item['score']:g} points)"
            )
            out.append(f"   {item['reason']}")
            out.append("")
        for title, claims in (("Emerging patterns", brief.emerging_patterns),
                              ("Recommended focus", brief.recommended_focus)):
            out += [f"## {title}", ""]
            if not claims:
                out += ["_None this cycle._", ""]
                continue
            for claim in claims:
                out.append(f"- {claim['statement']}")
                out.append(f"  _cites: {_cites_text(claim, brief.metrics)}_")
            out.append("")

    out += ["## The ranking", "",
            "| rank | finding | unit | band | timing | points |",
            "|---:|---|---|---|---|---:|"]
    for row in brief.ranked[:10]:
        out.append(
            f"| {row['rank']} | {row['id']} | {row['unit']} | {row['band']} | "
            f"{_timing(row)} | {row['score']:g} |"
        )
    out += ["", "## How the order is built", "", "```text",
            priority.formula_table(), "```", ""]
    return "\n".join(out)


def brief_html(brief) -> str:
    rows = _rows_by_id(brief)
    body = [
        "<header>",
        "<h1>Prioritisation brief</h1>",
        f"<div class=\"meta\">As of {_e(brief.as_of)} · advisory, changes no "
        f"state · {brief.model_calls} model call over the top "
        f"{min(len(brief.ranked), 12)} of {len(brief.ranked)} open findings, "
        f"{_e(_metrics_given(brief))} · {_e(brief.prompt_version)}</div>",
        "</header>",
    ]
    if brief.withheld:
        body.append(
            f"<h2>Withheld</h2><div class=\"withheld\"><p>"
            f"{_e(withheld_note(brief.withheld, 'brief'))}</p><p>The ranking below "
            f"came from no model and is unaffected.</p></div>"
        )
    elif brief.published:
        body.append("<h2>Top priorities</h2><ol>")
        for item in brief.top_priorities:
            row = rows[item["finding_id"]]
            body.append(
                f"<li value=\"{item['rank']}\"><span class=\"chip\">"
                f"{_e(item['finding_id'])}</span> {_e(row['unit'])} · "
                f"{_e(row['band'])} · {_e(_timing(row))} · "
                f"{item['score']:g} points<span class=\"reason\">{_e(item['reason'])}</span>"
                f"<span class=\"cites\">{_e(row['explain'])}</span></li>"
            )
        body.append("</ol>")
        for title, claims in (("Emerging patterns", brief.emerging_patterns),
                              ("Recommended focus", brief.recommended_focus)):
            body.append(f"<h2>{title}</h2>")
            if not claims:
                body.append("<p class=\"meta\">None this cycle.</p>")
                continue
            body.append("<ul>")
            for claim in claims:
                chips = "".join(
                    f"<span class=\"chip\">{_e(i)}</span>" for i in claim["finding_ids"]
                ) + "".join(
                    f"<span class=\"chip metric\">{_e(m)} = "
                    f"{_e(brief.metrics.get(m))}</span>" for m in claim["metrics"]
                )
                body.append(
                    f"<li>{_e(claim['statement'])}<span class=\"cites\">cites "
                    f"{chips}</span></li>"
                )
            body.append("</ul>")

    body.append("<h2>The ranking</h2><div class=\"table-wrap\"><table><tr><th>Rank</th>"
                "<th>Finding</th><th>Unit</th><th>Band</th><th>Timing</th>"
                "<th>Points</th></tr>")
    for row in brief.ranked[:10]:
        body.append(
            f"<tr><td class=\"num\">{row['rank']}</td><td><span class=\"chip\">"
            f"{_e(row['id'])}</span></td><td>{_e(row['unit'])}</td>"
            f"<td>{_e(row['band'])}</td><td>{_e(_timing(row))}</td>"
            f"<td class=\"num\">{row['score']:g}</td></tr>"
        )
    body.append("</table></div>")
    body.append(f"<h2>How the order is built</h2><pre>{_e(priority.formula_table())}</pre>")
    return page(f"Prioritisation brief {brief.as_of}", "\n".join(body))


# --- the audit report ---------------------------------------------------------

def report_html(report) -> str:
    from .stages.audits import report_heading, report_status, summary_note

    kind = report.kind.replace("_", " ").title()
    # Computed outside the f-strings: Python 3.11 allows no backslash escape
    # inside an f-string's braces, and the dash is one.
    scope = ", ".join(report.scope) or "—"
    body = [
        "<header>",
        f"<h1>{_e(report_heading(report))}</h1>",
        f"<div class=\"meta\">{_e(report_status(report))}</div>",
        "</header>",
        "<div class=\"table-wrap\"><table>",
        f"<tr><th>Audit</th><td><span class=\"chip\">{_e(report.audit_id)}</span></td></tr>",
        f"<tr><th>Kind</th><td>{_e(kind)}</td></tr>",
        f"<tr><th>Auditor</th><td>{_e(report.auditor)}</td></tr>",
        f"<tr><th>Scope</th><td>{_e(scope)}</td></tr>",
        f"<tr><th>Planned</th><td>{_e(report.planned_date)}</td></tr>",
        f"<tr><th>Conducted</th><td>{_e(report.conducted_date or 'not recorded')}</td></tr>",
        f"<tr><th>Findings</th><td>{len(report.findings)}</td></tr>",
        "</table></div>",
        "<h2>Summary</h2>",
    ]
    if report.summary:
        body.append(f"<p>{_e(report.summary)}</p>")
        body.append(f"<div class=\"note\">{_e(summary_note(report))}</div>")
    elif report.summary_withheld:
        body.append(
            f"<div class=\"withheld\"><p>"
            f"{_e(withheld_note(report.summary_withheld, 'summary'))}</p></div>"
        )
    else:
        body.append(
            "<div class=\"note\">No narrative summary: this audit raised no "
            "findings.</div>"
        )

    body.append("<h2>Findings</h2>")
    if not report.findings:
        body.append("<p>None raised.</p>")
    for finding in report.findings:
        body.append("<div class=\"finding\">")
        body.append(
            f"<h3><span class=\"chip\">{_e(finding['id'])}</span> "
            f"{_e(finding['severity'])}</h3>"
        )
        body.append(
            f"<div class=\"meta\">{_e(finding['unit'])} · category "
            f"{_e(finding['category'])} · owner {_e(finding['owner'])} · "
            f"target {_e(finding['target_date'])}</div>"
        )
        body.append(f"<p>{_e(finding['description'])}</p>")
        if finding["agreed_action_plan"]:
            body.append(
                f"<p><strong>Agreed action plan.</strong> "
                f"{_e(finding['agreed_action_plan'])}</p>"
            )
        if finding.get("recurrence_links"):
            links = "; ".join(
                f"{link['id']} ({link['unit']}, raised {link['raised_on']})"
                for link in finding["recurrence_links"]
            )
            body.append(f"<p><strong>Recurrence.</strong> Resembles {_e(links)}.</p>")
        body.append("</div>")
    return page(f"{kind} report {report.audit_id}", "\n".join(body))
