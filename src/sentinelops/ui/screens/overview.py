"""Management · Overview. Escalations, unit trends, and ageing. Read-only."""

import streamlit as st

from sentinelops.ui import service, shell, view

conn, today, actor = shell.context()
ageing = service.portfolio_analytics(conn)["overdue_ageing"]

shell.html(view.page_header(
    "Overview",
    f"What has been escalated, how each unit is trending, and how old the overdue "
    f"work is, as of {view.fmt_long_date(today)}. Read-only: management sees the "
    "portfolio and changes nothing in it.",
    eyebrow="Management",
))
shell.html(view.figures(view.management_figures(conn, today)))

with st.container(key="card_escalated"):
    st.subheader("Escalated findings")
    escalated = view.escalated_rows(conn, today)
    if escalated:
        st.caption("Open findings escalated past their owner, highest level first. "
                   "Level 1 goes to the owner's manager and PA/InfoSec; each later "
                   "level goes further up.")
        st.dataframe(
            [{**row, "Level": finding["escalation"]}
             for row, finding in zip(view.overdue_table(escalated), escalated)],
            hide_index=True, width="stretch", height=300,
            column_order=["Finding", "Severity", "Level", "Unit", "Late", "Owner", "Chased"],
            column_config={
                "Severity": shell.SEVERITY_COLUMN,
                "Level": st.column_config.NumberColumn("Level", format="Level %d", width="small"),
                "Late": st.column_config.NumberColumn("Late", format="%d days", width="small"),
                "Chased": st.column_config.NumberColumn("Chased", format="%d×", width="small"),
            },
        )
    else:
        shell.html(view.empty_state(
            "Nothing escalated",
            "A finding escalates when it runs past its target date without being "
            "closed — within a week at most. None has.",
        ))

trend_col, ageing_col = st.columns([1.5, 1], gap="large")
with trend_col:
    with st.container(key="card_unit_trend"):
        st.subheader("Unit trend")
        rows = view.unit_trend(conn, today)
        if rows:
            st.caption("Open findings per unit at each of the last twelve month ends, "
                       "and the change over the last three.")
            st.dataframe(
                view.unit_trend_table(rows), hide_index=True, width="stretch", height=380,
                column_config={
                    "Last 12 months": st.column_config.LineChartColumn(
                        "Last 12 months", y_min=0, color=view.ACCENT),
                    "3-month change": st.column_config.NumberColumn("3-month change", format="%+d"),
                    "Oldest overdue": st.column_config.NumberColumn("Oldest overdue", format="%d days"),
                    "Closed": st.column_config.ProgressColumn(
                        "Closed", min_value=0, max_value=100, format="%.0f%%"),
                },
            )
        else:
            shell.html(view.empty_state(
                "No unit has a finding yet",
                "Trends are drawn from findings raised and closed over time; none has "
                "been raised.",
            ))
with ageing_col:
    with st.container(key="card_mgmt_ageing"):
        st.subheader("Ageing summary")
        if ageing["total"]:
            st.caption(f"{view.plural(ageing['total'], 'open finding')} past target; the "
                       f"oldest by {view.plural(ageing['oldest_days'], 'day')}.")
            st.bar_chart(
                [{"Days past target": f"{name.replace('-', '–')} days", "Findings": count}
                 for name, count in ageing["buckets"].items()],
                x="Days past target", y="Findings", color=view.ACCENT, sort=False,
                height=300,
            )
        else:
            shell.html(view.empty_state(
                "Nothing overdue",
                "Open findings past their target date are bucketed here by how far past.",
            ))
