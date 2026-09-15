"""Inbox. One identity's notifications — recorded, never emailed."""

import streamlit as st

from sentinelops.ui import shell, view

conn, today, actor = shell.context()
rows = view.inbox_rows(conn, actor["id"], as_of=today)

shell.html(view.page_header(
    "Inbox",
    f"Everything the system decided {actor['name']} needed to know: reminders, "
    "escalations, evidence and closures. Recorded rather than emailed, and stamped "
    "in simulated business time.",
    eyebrow=view.ROLE_LABELS.get(actor["role"], ""),
))
shell.html(view.figures(view.inbox_figures(rows, today)))

with st.container(key="card_inbox"):
    choice = st.segmented_control("Show", list(view.INBOX_FILTERS), default="All",
                                  key="inbox_filter")
    shown = view.filter_inbox(rows, choice or "All")
    shell.post("inbox_result")
    if not shown:
        shell.html(view.empty_state(
            "Nothing here",
            "No notification has been addressed to you yet. Reminders, escalations and "
            "evidence requests arrive as cycles run."
            if not rows else
            "No notification matches this filter. Choose **All** to see everything.",
        ))
    else:
        picked = st.dataframe(
            view.inbox_table(shown), hide_index=True, width="stretch", height=380,
            # Keyed on the filter and a counter the modal bumps on close, so a
            # closed notification is not still selected — and reopened — on the
            # next rerun, and a new filter never inherits an old row index.
            key=f"inbox_table_{choice}_{st.session_state.get('inbox_table_version', 0)}",
            # A click anywhere on a row opens it, not only on a checkbox.
            on_select="rerun", selection_mode="single-cell",
            column_config={
                "Status": st.column_config.MultiselectColumn(
                    "Status", options=["Unread", "Read"], color=["primary", "gray"],
                    width="small"),
                "Sent": st.column_config.DatetimeColumn("Sent", format=shell.WHEN_FORMAT),
                "Kind": st.column_config.MultiselectColumn(
                    "Kind", options=list(view.KIND_LABELS.values()),
                    color=["primary" if kind == "escalation" else "gray"
                           for kind in view.KIND_LABELS]),
                "Subject": st.column_config.TextColumn("Subject", width="large"),
            },
        )
        st.caption("Select a notification to read it in full.")
        if picked.selection.cells:
            shell.notification(conn, shown[picked.selection.cells[0][0]], actor)
