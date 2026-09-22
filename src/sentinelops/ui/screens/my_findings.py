"""Unit owner · My findings. Only their own unit, soonest target first."""

import streamlit as st

from sentinelops.ui import shell, view

conn, today, actor = shell.context()
unit = view.unit_name(conn, actor["unit"]) or "your unit"

shell.html(view.page_header(
    "My findings",
    f"Findings raised against {unit}, soonest target date first. Closing is "
    "PA/InfoSec's decision; what is yours is the evidence, and your progress.",
    eyebrow=f"Unit owner · {unit}",
))
shell.html(view.figures(view.owner_figures(conn, actor["id"], today)))

with st.container(key="card_mine"):
    st.subheader("Findings")
    include_closed = st.toggle("Include closed findings", key="include_closed")
    rows = view.my_findings(conn, actor["id"], today, include_closed=include_closed)
    if not rows:
        shell.html(view.empty_state(
            f"No open findings for {unit}",
            "When an audit, or a compliance check whose evidence fails, raises a finding "
            "against your unit it appears here, soonest target date first.",
        ))
    else:
        st.caption("Select a finding to file evidence or report progress on it.")
        picked = st.dataframe(
            view.owner_table(rows), hide_index=True, width="stretch",
            key="mine_table", on_select="rerun", selection_mode="single-row",
            column_config={
                "Severity": shell.SEVERITY_COLUMN,
                "Target": st.column_config.DateColumn("Target", format=shell.DATE_FORMAT),
                "Latest round": st.column_config.MultiselectColumn(
                    "Latest round", options=list(view.RESPONSE_LABELS.values()),
                    color=["primary", "gray", "gray"]),
                "Chased": st.column_config.NumberColumn("Chased", format="%d×", width="small"),
            },
        )
        if picked.selection.rows:
            st.session_state["owner_finding"] = rows[picked.selection.rows[0]]["id"]
            st.switch_page("screens/owner_detail.py")

with st.container(key="card_checks"):
    st.subheader("Evidence due from your unit")
    checks = view.owner_checks(conn, actor["unit"], today) if actor["unit"] else []
    shell.post("upload")
    if checks:
        st.caption("Scheduled compliance activities your unit owes evidence for. "
                   "They are not findings: evidence here goes through the pre-screen "
                   "and assessment rather than to an auditor.")
        if st.button("File evidence for a scheduled check", type="primary",
                     key="open_check_mine"):
            shell.open_evidence_form("check@my_findings")
        st.dataframe(
            view.check_table(checks), hide_index=True, width="stretch", height=260,
            column_config={
                "Activity": st.column_config.TextColumn("Activity", width="large"),
                "Due": st.column_config.DateColumn("Due", format=shell.DATE_FORMAT),
            },
        )
    else:
        shell.html(view.empty_state(
            "No evidence due",
            "Checks appear here once a cycle raises them for your unit's controls. "
            "None is waiting on you.",
        ))

shell.evidence_forms(conn, actor=actor, today=today, where="my_findings")
