"""Inbox. One identity's notifications — recorded, never emailed."""

import streamlit as st

from sentinelops.ui import service, shell, view

conn, today, actor = shell.context()
rows = view.inbox_rows(conn, actor["id"])

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
            key="inbox_table", on_select="rerun", selection_mode="single-row",
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
        if picked.selection.rows:
            note = shown[picked.selection.rows[0]]
            with st.container(key="card_note"):
                shell.html(
                    f'<div class="so-row">{view.badge(note["kind_label"], "outline")}'
                    f'{view.badge("Unread", "accent") if note["unread"] else ""}'
                    f'<span class="so-muted">{view.fmt_when(note["sent"])} · about '
                    f'{note["about"]}</span></div>'
                    f'<div class="so-finding-title">{view.rich(note["subject"])}</div>'
                )
                shell.html(view.quote(note["body"]))
                if note["unread"] and st.button("Mark as read", key=f"read_{note['id']}"):
                    ok, message = service.mark_read(conn, note["id"], by=actor["id"])
                    st.session_state["inbox_result"] = {"ok": ok, "message": message}
                    st.rerun()
        else:
            st.caption("Select a notification to read it in full.")
