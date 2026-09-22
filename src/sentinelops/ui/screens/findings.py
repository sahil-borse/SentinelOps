"""PA/InfoSec · Findings. The full list, filtered, with one finding in detail."""

import streamlit as st

from sentinelops.ui import shell, view

conn, today, actor = shell.context()

shell.html(view.page_header(
    "Findings",
    "Every finding on record. Narrow the list, then select a finding to see its "
    "evidence with cited spans highlighted, its rounds, recurrence and audit timeline.",
    eyebrow="PA/InfoSec",
))

units = {choice["unit"]: choice["unit_name"]
         for choice in view.identity_choices(conn) if choice["unit"]}
with st.container(key="card_filters"):
    unit_col, severity_col, ageing_col, status_col = st.columns([1.2, 1.4, 1, 1])
    unit = unit_col.selectbox(
        "Unit", [""] + sorted(units, key=units.get),
        format_func=lambda unit_id: units.get(unit_id, "All units"),
    )
    severities = severity_col.pills(
        "Severity", list(view.SEVERITIES), selection_mode="multi",
        default=list(view.SEVERITIES),
    )
    ageing = ageing_col.selectbox("Ageing band", ["All bands", *view.AGEING_BANDS, "Closed"])
    status = status_col.segmented_control(
        "Status", ["Open", "Closed", "All"], default="Open",
    )

rows = view.finding_rows(
    conn, today, unit_id=unit or None,
    status={"Open": "open", "Closed": "closed"}.get(status or "All"),
)
shown = view.filter_findings(
    rows, severities=severities,
    ageing=None if ageing == "All bands" else ageing,
)

st.subheader("On record")
if not shown:
    shell.html(view.empty_state(
        "No findings match",
        "Nothing on record fits every filter above. Widen the severity, band or "
        "status to see more."
        if rows else
        "No finding has been raised yet. Audits raise them, and so does a compliance "
        "check whose evidence fails assessment.",
    ))
else:
    st.caption(f"Showing {len(shown)} of {view.plural(len(rows), 'finding')}. "
               "Select a row to open it.")
    version = st.session_state.get("findings_table_version", 0)
    picked = st.dataframe(
        view.findings_table(shown), hide_index=True, width="stretch", height=360,
        key=f"findings_table_{version}", on_select="rerun", selection_mode="single-row",
        column_config={
            "Finding": st.column_config.TextColumn("Finding", width="medium"),
            "Severity": shell.SEVERITY_COLUMN,
            "Status": shell.STATUS_COLUMN,
            "Target": st.column_config.DateColumn("Target", format=shell.DATE_FORMAT),
            "Chased": st.column_config.NumberColumn("Chased", format="%d×", width="small"),
            "Rounds": st.column_config.NumberColumn("Rounds", width="small"),
            "Chronic": st.column_config.CheckboxColumn("Chronic", width="small"),
        },
    )
    if picked.selection.rows:
        st.session_state["selected_finding"] = shown[picked.selection.rows[0]]["id"]

# The finding opens over the list, in a modal, rather than below it.
selected = st.session_state.get("selected_finding")
if selected:
    shell.finding_popup(conn, selected, actor=actor, today=today,
                        version_key="findings_table_version")
