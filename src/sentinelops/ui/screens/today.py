"""PA/InfoSec · Today. The landing page: what needs the audit team this morning."""

import streamlit as st

from sentinelops.ui import service, shell, view

conn, today, actor = shell.context()

shell.html(view.page_header(
    "Today",
    f"Good morning, {actor['name']}. Here is what needs PA/InfoSec as of "
    f"{view.fmt_long_date(today)}, in simulated business time.",
    eyebrow="PA/InfoSec",
))
shell.html(view.figures(view.today_figures(conn, today)))

left, right = st.columns([1.3, 1.1], gap="large")

with left:
    with st.container(key="card_review"):
        st.subheader("Review queue")
        st.caption("Evidence rounds filed by unit owners and waiting for your "
                   "decision, oldest first. The advisory reading beside each is "
                   "advice; accepting closes the finding, insufficient sends the gaps back.")
        shell.post("review_result")
        queue = view.review_queue(conn, today)
        if not queue:
            shell.html(view.empty_state(
                "Nothing is waiting for review",
                "When a unit owner files evidence against one of their findings it "
                "arrives here with the model's advisory reading beside it. No round "
                "is unanswered right now.",
            ))
        for position, item in enumerate(queue[:6]):
            with st.expander(
                f"{item['finding_id']} · round {item['round_number']} · "
                f"{item['unit']} · waiting {view.plural(item['waiting_days'], 'day')}",
                expanded=position == 0,
            ):
                shell.html(view.review_item(item))
                if item["evidence_text"]:
                    st.caption("The evidence, with any passage the reading cites highlighted")
                    shell.document(
                        item["evidence_text"],
                        item["recommendation"].cited_spans if item["recommendation"] else [],
                        key=f"review_{item['id']}",
                    )
                if actor["may_respond"]:
                    with st.form(f"respond_{item['id']}", clear_on_submit=True):
                        remarks = st.text_area(
                            "Remarks to the owner", height=80,
                            placeholder="What satisfied you — or exactly what is still missing.",
                        )
                        accept, insufficient = st.columns(2)
                        accepted = accept.form_submit_button(
                            "Accept and close", type="primary", width="stretch")
                        refused = insufficient.form_submit_button(
                            "Mark insufficient", width="stretch")
                        if accepted or refused:
                            ok, message = service.respond_to_round(
                                conn, item["id"],
                                response="accepted" if accepted else "insufficient",
                                by=actor["id"], remarks=remarks,
                            )
                            st.session_state["review_result"] = {"ok": ok, "message": message}
                            st.rerun()
        if len(queue) > 6:
            st.caption(f"{len(queue) - 6} more waiting, oldest shown first.")

with right:
    alert = service.chronic_findings(conn)
    with st.container(key="alert_chronic"):
        st.subheader("Chronic findings")
        if alert["findings"]:
            st.caption(f"Open more than {alert['threshold_days']} days past target. "
                       "Flagged on their own — the priority order is not changed by it.")
            shell.html(view.chronic_list(alert))
        else:
            shell.html(view.empty_state(
                "No chronic findings",
                f"A finding appears here once it has been open more than "
                f"{alert['threshold_days']} days past its target date. None has, as "
                f"of {view.fmt_date(today)}.",
            ))

    with st.container(key="card_overdue"):
        st.subheader("Overdue and escalation queue")
        rows = view.overdue_rows(conn, today)
        if not rows:
            shell.html(view.empty_state(
                "Nothing is overdue",
                "Open findings appear here once they reach their target date, most "
                "severe first. Advance the calendar and deadlines start to bite.",
            ))
        else:
            st.caption(f"{view.plural(len(rows), 'open finding')} at or past target, "
                       "most severe first. Select one to open it.")
            picked = st.dataframe(
                view.overdue_table(rows), hide_index=True, width="stretch", height=300,
                key="overdue_table", on_select="rerun", selection_mode="single-row",
                # The compact queue: what, how bad, how late. Escalation level and
                # owner are one click away on the finding itself.
                column_order=["Finding", "Severity", "Late"],
                column_config={
                    "Finding": st.column_config.TextColumn("Finding", width="medium"),
                    "Severity": shell.SEVERITY_COLUMN,
                    "Late": st.column_config.NumberColumn("Late", format="%dd", width="small",
                                                          help="Days past the target date"),
                },
            )
            if picked.selection.rows:
                st.session_state["selected_finding"] = rows[picked.selection.rows[0]]["id"]
                st.switch_page("screens/findings.py")

shell.brief_panel(conn, today)
