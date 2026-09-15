"""PA/InfoSec · Schedule. Audits and compliance activities in the next thirty days."""

from collections import Counter
from datetime import timedelta

import streamlit as st

from sentinelops import analytics
from sentinelops.repositories import repositories
from sentinelops.ui import shell, view

conn, today, actor = shell.context()
upcoming = analytics.upcoming(repositories(conn), today)
horizon = upcoming["horizon_days"]

shell.html(view.page_header(
    "Schedule",
    f"Audits planned and compliance activities falling due between "
    f"{view.fmt_date(today)} and the next {horizon} days. Scheduling is "
    "deterministic — no model decides what is due.",
    eyebrow="PA/InfoSec",
))
activities = upcoming["activities"]
next_audit = upcoming["audits"][0] if upcoming["audits"] else None
shell.html(view.figures([
    view.Figure("Audits planned", str(len(upcoming["audits"])),
                f"Next in {view.plural(next_audit['days_away'], 'day')}" if next_audit
                else f"None in the next {horizon} days"),
    view.Figure("Activities due", str(upcoming["activity_total"]),
                f"Across {view.plural(len({a['unit'] for a in activities}), 'unit')}"),
    view.Figure("Next due", view.fmt_date(activities[0]["due"]) if activities else "—",
                activities[0]["control"] if activities else "Nothing falls due"),
    view.Figure("Horizon", view.plural(horizon, "day"),
                f"To {view.fmt_date(today + timedelta(days=horizon))}"),
]))

audits_col, activities_col = st.columns([1, 1.6], gap="large")
with audits_col:
    with st.container(key="card_audits"):
        st.subheader("Audits")
        if upcoming["audits"]:
            shell.html(view.audit_list(upcoming["audits"]))
        else:
            shell.html(view.empty_state(
                f"No audit in the next {horizon} days",
                "Planned internal audits, QAREVs, release audits and document reviews "
                "appear here once they fall inside the horizon.",
            ))
    with st.container(key="card_due_by_unit"):
        st.subheader("Due by unit")
        if activities:
            counts = Counter(activity["unit"] for activity in activities)
            st.caption("Compliance activities falling due in the horizon, per owning unit.")
            st.bar_chart(
                [{"Unit": unit, "Activities": count} for unit, count in counts.most_common()],
                x="Unit", y="Activities", horizontal=True, color=view.ACCENT, sort=False,
                height=260,
            )
        else:
            shell.html(view.empty_state(
                "Nothing due",
                "Once activities fall due inside the horizon they are counted here by unit.",
            ))
with activities_col:
    with st.container(key="card_activities"):
        st.subheader("Compliance activities due")
        if activities:
            if upcoming["activity_total"] > len(activities):
                st.caption(f"The first {len(activities)} of {upcoming['activity_total']}, "
                           "soonest first.")
            else:
                st.caption("Soonest first. Evidence is due from the owning unit.")
            st.dataframe(
                view.activity_table(activities), hide_index=True, width="stretch",
                height=420,
                column_config={
                    "Due": st.column_config.DateColumn("Due", format=shell.DATE_FORMAT),
                    "In": st.column_config.NumberColumn("In", format="%d days", width="small"),
                    "Activity": st.column_config.TextColumn("Activity", width="medium"),
                },
            )
        else:
            shell.html(view.empty_state(
                f"No activity due in the next {horizon} days",
                "Checks appear here once a cycle has raised them and their due date "
                "falls inside the horizon. Run a cycle to raise this month's.",
            ))
