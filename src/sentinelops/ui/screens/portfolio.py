"""PA/InfoSec · Portfolio. Section 8, computed from the record and the audit log."""

from datetime import datetime

import streamlit as st

from sentinelops.ui import service, shell, view

conn, today, actor = shell.context()
stats = service.portfolio_analytics(conn)
split = stats["open_vs_closed"]
ageing = stats["overdue_ageing"]
closure = stats["closure"]["overall"]

shell.html(view.page_header(
    "Portfolio",
    "Section 8, computed from the record and the audit log. Arithmetic only — "
    "no model is involved.",
    eyebrow="PA/InfoSec · insight",
))
shell.html(view.figures([
    view.Figure("Open findings", str(split["open"]),
                f"{split['open_pct']:g}% of {view.plural(split['total'], 'finding')} raised"),
    view.Figure("Closed", f"{split['closed_pct']:g}%", f"{split['closed']} closed by an auditor"),
    view.Figure("Overdue", str(ageing["total"]),
                f"Oldest {view.plural(ageing['oldest_days'], 'day')} past target"
                if ageing["total"] else "Nothing past its target"),
    view.Figure("Median days to close",
                f"{closure['median_days']:g}" if closure["median_days"] is not None else "—",
                f"Mean {closure['mean_days']:g}" if closure["mean_days"] is not None
                else "No finding closed yet"),
]))

if not split["total"]:
    shell.html(view.empty_state(
        "No findings yet",
        "Every figure on this page is computed over findings, and none has been "
        "raised. Run a cycle or advance the calendar.",
    ))
    st.stop()

top_left, top_right = st.columns(2, gap="large")
with top_left:
    with st.container(key="card_split"):
        st.subheader("Open and closed by unit")
        st.caption("Count and percentage for every unit that has had a finding.")
        st.dataframe(
            [{"Unit": unit, "Open": row["open"], "Closed": row["closed"],
              "Closed %": row["closed_pct"]}
             for unit, row in split["by_unit"].items()],
            hide_index=True, width="stretch", height=320,
            column_config={"Closed %": st.column_config.ProgressColumn(
                "Closed", min_value=0, max_value=100, format="%.0f%%")},
        )
with top_right:
    with st.container(key="card_severity"):
        st.subheader("Severity mix")
        overall = stats["severity_mix"]["overall"]
        shell.html('<div class="so-row">' + "".join(
            f"{view.severity_badge(severity)}<span class='so-muted'>{overall.get(severity, 0)}</span>"
            for severity in view.SEVERITIES) + "</div>")
        st.dataframe(
            [{"Unit": unit, **{s: row.get(s, 0) for s in view.SEVERITIES},
              "Total": sum(row.get(s, 0) for s in view.SEVERITIES)}
             for unit, row in stats["severity_mix"]["by_unit"].items()],
            hide_index=True, width="stretch", height=280,
        )

trend_col, ageing_col = st.columns([1.35, 1], gap="large")
with trend_col:
    with st.container(key="card_trend"):
        st.subheader("Open findings over time")
        points = stats["trend"]
        st.caption(f"Month by month, {view.month_label(points[0]['month'])} to "
                   f"{view.month_label(points[-1]['month'])}, replayed from raise and "
                   "closure dates rather than sampled from today.")
        # Dates rather than labels, so the axis is time and reads as months in
        # order; month names as strings would be sorted alphabetically.
        st.line_chart(
            [{"Month": datetime.strptime(p["month"], "%Y-%m"), "Open findings": p["open"]}
             for p in points],
            x="Month", y="Open findings", color=view.ACCENT, height=220,
        )
        shell.html(view.trend_reads(stats["trend_verdict"]))
with ageing_col:
    with st.container(key="card_ageing"):
        st.subheader("Overdue ageing")
        st.caption("Open findings past their target date, by how far past.")
        st.bar_chart(
            [{"Days past target": f"{name.replace('-', '–')} days", "Findings": count}
             for name, count in ageing["buckets"].items()],
            x="Days past target", y="Findings", color=view.ACCENT, sort=False, height=260,
        )

by_unit, by_category, by_kind = st.columns(3, gap="large")
dimensions = stats["by_dimension"]
most = max(dimensions["by_category"].values(), default=1)
with by_unit:
    with st.container(key="card_units"):
        st.subheader("By unit")
        st.bar_chart([{"Unit": k, "Findings": v} for k, v in dimensions["by_unit"].items()],
                     x="Unit", y="Findings", horizontal=True, color=view.ACCENT,
                     height=300)
with by_category:
    with st.container(key="card_categories"):
        st.subheader("By gap category")
        st.dataframe(
            [{"Category": k.replace("_", " "), "Findings": v}
             for k, v in dimensions["by_category"].items()],
            hide_index=True, width="stretch", height=300,
            column_config={"Findings": st.column_config.ProgressColumn(
                "Findings", min_value=0, max_value=most, format="%d")},
        )
with by_kind:
    with st.container(key="card_kinds"):
        st.subheader("By audit kind")
        st.dataframe(
            [{"Audit kind": view.AUDIT_KIND_LABELS.get(k, view.humanise(k)), "Findings": v}
             for k, v in dimensions["by_audit_kind"].items()],
            hide_index=True, width="stretch",
        )

closure_col, effort_col = st.columns(2, gap="large")
with closure_col:
    with st.container(key="card_closure"):
        st.subheader("Closure performance")
        st.caption("Days from raise to closure, by severity.")
        st.dataframe(
            [{"Severity": [severity], "Closed": row["closed"], "Median days": row["median_days"],
              "Mean days": row["mean_days"], "Slowest": row["slowest_days"]}
             for severity, row in stats["closure"].items() if severity in view.SEVERITIES],
            hide_index=True, width="stretch",
            column_config={"Severity": shell.SEVERITY_COLUMN,
                           "Slowest": st.column_config.NumberColumn("Slowest", format="%d days")},
        )
with effort_col:
    with st.container(key="card_effort"):
        st.subheader("Rounds and reminders")
        st.caption(f"{stats['effort']['multi_round']} findings needed more than one "
                   f"evidence round; {stats['effort']['multi_reminder']} more than one reminder.")
        counts = sorted(set(stats["effort"]["rounds"]) | set(stats["effort"]["reminders"]))
        st.dataframe(
            [{"How many": count, "Evidence rounds": stats["effort"]["rounds"].get(count, 0),
              "Reminders": stats["effort"]["reminders"].get(count, 0)} for count in counts],
            hide_index=True, width="stretch",
        )

with st.container(key="card_areas"):
    st.subheader("Compliance status by process area")
    st.caption("The compliance-activity track: checks raised per unit, and how they stand.")
    st.dataframe(
        [{"Unit": row.name, "Owner": row.owner, "Criticality": row.criticality.title(),
          "Checks due": row.due, "Assessed": row.assessed, "Overdue": row.overdue,
          "Waived": row.waived, "Open gaps": row.gaps}
         for row in view.status_by_area(conn)],
        hide_index=True, width="stretch",
    )
