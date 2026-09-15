"""PA/InfoSec · Today. The landing page: what needs the audit team this morning."""

import streamlit as st

from sentinelops import analytics
from sentinelops.repositories import repositories
from sentinelops.ui import service, shell, view

conn, today, actor = shell.context()

shell.html(view.page_header(
    "Today",
    f"Good morning, {actor['name']} — here is what needs PA/InfoSec on "
    f"{view.fmt_long_date(today)}, in simulated business time.",
    eyebrow="PA/InfoSec",
))
shell.html(view.figures(view.today_figures(conn, today)))

main, rail = st.columns([1.5, 1], gap="medium")

with main:
    with st.container(key="card_review"):
        head, link = st.columns([2, 1], vertical_alignment="center")
        with head:
            st.subheader("Review queue")
        link.page_link("screens/findings.py", label="All findings",
                       icon=":material/arrow_forward:")
        st.caption("Evidence rounds filed by unit owners, oldest first. The advisory "
                   "reading is advice: accepting closes the finding, insufficient "
                   "sends the gaps back.")
        shell.post("review_result")
        queue = view.review_queue(conn, today)
        if not queue:
            shell.html(view.empty_state(
                "Nothing is waiting for review",
                "When a unit owner files evidence against one of their findings it "
                "arrives here with the model's advisory reading beside it.",
            ))
        for position, item in enumerate(queue[:6]):
            with st.expander(
                f"{item['finding_id']} · round {item['round_number']} · "
                f"{item['unit']} · waiting {view.plural(item['waiting_days'], 'day')}",
                expanded=position == 0,
            ):
                details, evidence = st.columns([1, 1.05], gap="medium")
                with details:
                    shell.html(view.review_item(item))
                    if actor["may_respond"]:
                        with st.form(f"respond_{item['id']}", clear_on_submit=True):
                            remarks = st.text_area(
                                "Remarks to the owner", height=76,
                                placeholder="What satisfied you — or exactly what is still missing.",
                            )
                            # Stacked, full width: the column is narrow at laptop
                            # widths, and a truncated decision button is worse
                            # than a taller form.
                            accepted = st.form_submit_button(
                                "Accept and close", type="primary", width="stretch")
                            refused = st.form_submit_button(
                                "Mark insufficient", width="stretch")
                            if accepted or refused:
                                ok, message = service.respond_to_round(
                                    conn, item["id"],
                                    response="accepted" if accepted else "insufficient",
                                    by=actor["id"], remarks=remarks,
                                )
                                st.session_state["review_result"] = {"ok": ok, "message": message}
                                st.rerun()
                with evidence:
                    if item["evidence_text"]:
                        shell.html(view.label("Evidence, cited passages highlighted"))
                        shell.document(
                            item["evidence_text"],
                            item["recommendation"].cited_spans if item["recommendation"] else [],
                            key=f"review_{item['id']}",
                        )
                    else:
                        shell.html(view.empty_state(
                            "Filed without text",
                            "This round names a document but carries no text, so there "
                            "is nothing to read or highlight.",
                        ))
        if len(queue) > 6:
            st.caption(f"{len(queue) - 6} more waiting, oldest shown first.")

    shell.brief_panel(conn, today)

with rail:
    alert = service.chronic_findings(conn)
    with st.container(key="alert_chronic"):
        st.subheader("Chronic findings")
        if alert["findings"]:
            st.caption(f"Open more than {alert['threshold_days']} days past target. "
                       "Flagged on their own; the priority order is unchanged.")
            shell.html(view.chronic_list(alert))
        else:
            shell.html(view.empty_state(
                "No chronic findings",
                f"A finding appears here once it is open more than "
                f"{alert['threshold_days']} days past its target date.",
            ))

    with st.container(key="card_overdue"):
        st.subheader("Overdue and escalation queue")
        rows = view.overdue_rows(conn, today)
        if not rows:
            shell.html(view.empty_state(
                "Nothing is overdue",
                "Open findings appear here once they reach their target date, most "
                "severe first.",
            ))
        else:
            st.caption(f"{view.plural(len(rows), 'open finding')} at or past target, "
                       "most severe first. Select one to open it.")
            picked = st.dataframe(
                view.overdue_table(rows), hide_index=True, width="stretch", height=286,
                key="overdue_table", on_select="rerun", selection_mode="single-row",
                # The compact queue: what, how bad, how late. Escalation level and
                # owner are one click away on the finding itself.
                column_order=["Finding", "Severity", "Late"],
                column_config={
                    # Pixel widths: the rail is narrow at laptop width, and an
                    # auto-sized id column pushes "how late" off the edge.
                    "Finding": st.column_config.TextColumn("Finding", width=190),
                    "Severity": shell.SEVERITY_COLUMN,
                    "Late": st.column_config.NumberColumn("Late", format="%dd", width=64,
                                                          help="Days past the target date"),
                },
            )
            if picked.selection.rows:
                st.session_state["selected_finding"] = rows[picked.selection.rows[0]]["id"]
                st.switch_page("screens/findings.py")

    week = analytics.upcoming(repositories(conn), today, horizon_days=7)
    with st.container(key="card_upcoming"):
        head, link = st.columns([2, 1], vertical_alignment="center")
        with head:
            st.subheader("Coming up")
        link.page_link("screens/schedule.py", label="Schedule",
                       icon=":material/arrow_forward:")
        due = len(week["audits"]) + week["activity_total"]
        if due:
            st.caption(f"{view.plural(len(week['audits']), 'audit')} and "
                       f"{view.plural(week['activity_total'], 'activity', 'activities')} due in the next "
                       f"seven days.")
            shell.html(view.upcoming_list(week, limit=5))
        else:
            shell.html(view.empty_state(
                "Nothing due this week",
                "Planned audits and compliance activities falling due in the next "
                "seven days appear here.",
            ))

    with st.container(key="card_latest"):
        head, link = st.columns([2, 1], vertical_alignment="center")
        with head:
            st.subheader("Latest notifications")
        link.page_link("screens/inbox.py", label="Inbox", icon=":material/arrow_forward:")
        notes = view.inbox_rows(conn, actor["id"], as_of=today)
        if notes:
            shell.html(view.inbox_preview(notes, limit=4))
        else:
            shell.html(view.empty_state(
                "No notifications yet",
                "Reminders, escalations and evidence arriving are recorded here as "
                "cycles run.",
            ))
