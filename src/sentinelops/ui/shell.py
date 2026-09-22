"""What every page shares: the connection, who is acting, and two shared panels.

Layout only, like `app.py` and the screens. Every number, label and date these
functions put on the page comes from `view.py`, and every action from
`service.py`; what is here is arrangement, which is why it may import Streamlit
and those two may not.
"""

from __future__ import annotations

from datetime import date
from typing import Any

import streamlit as st
import streamlit.components.v1 as components

from sentinelops.ui import service, view

#: Pill columns, so severity and response read the same in every table as in
#: every badge: coloured, and always labelled.
SEVERITY_COLUMN = st.column_config.MultiselectColumn(
    "Severity", options=list(view.SEVERITIES),
    color=[view.SEVERITY_PILL[s] for s in view.SEVERITIES], width="small",
)
STATUS_COLUMN = st.column_config.MultiselectColumn(
    "Status", options=["Open", "Closed"], color=["primary", "gray"], width="small",
)
RESPONSE_COLUMN = st.column_config.MultiselectColumn(
    "Response", options=list(view.RESPONSE_LABELS.values()),
    color=["primary", "gray", "gray"], width="small",
)
DATE_FORMAT = "D MMM YYYY"
WHEN_FORMAT = "D MMM YYYY, HH:mm"


@st.cache_resource
def database():
    service.prepare_demo_database()
    conn = service.open_database()
    service.seed(conn)  # a no-op once the snapshot is in place
    return conn


def context():
    """The connection, the simulated date, and the identity being acted as."""
    conn = database()
    identity = st.session_state.get("acting_as") or service.default_identity(conn)
    return conn, service.current_date(conn), service.acting_as(conn, identity)


def html(markup: str) -> None:
    st.markdown(markup, unsafe_allow_html=True)


def post(key: str) -> None:
    """Show a message parked before a rerun, once. Written before st.rerun(), a
    message is discarded, so actions park it in session state instead."""
    posted = st.session_state.pop(key, None)
    if posted:
        (st.success if posted["ok"] else st.error)(posted["message"])


def document(content: str, spans: list[str], *, key: str) -> None:
    """The source document in its own scrolling frame, cited spans highlighted."""
    expanded = st.session_state.get(f"doc_expanded_{key}", False)
    frame = view.document_frame(content, spans, expanded=expanded)
    # An iframe, so the document scrolls inside its own box and the page length
    # never depends on the document length. The evidence is untrusted — filed by
    # the party who benefits from acceptance — so `document_frame` escapes every
    # character of it; the only script in the frame is its own scroll-to-citation.
    st.iframe(frame.html, height=frame.height)
    st.caption(frame.caption())
    if not frame.fits or expanded:
        if st.button("Show less" if expanded else "Show more", key=f"doc_toggle_{key}",
                     help="Makes the panel taller. The document scrolls inside it "
                          "either way — the page does not grow."):
            st.session_state[f"doc_expanded_{key}"] = not expanded
            st.rerun()
    missing = view.unmatched_spans(content, spans)
    if missing:
        st.error(f"Cited text not found in the source: {missing}")


def finding_detail(conn, finding_id: str, *, actor: dict[str, Any], today: date,
                   key: str = "detail") -> None:
    """One finding in full: evidence, rounds, recurrence and its audit timeline.

    The Close control is only ever *rendered* for an identity that may close.
    Section 7 asks for it to be absent for everyone else, not disabled.
    """
    record = view.finding_record(conn, finding_id, today)
    if record is None:
        html(view.empty_state(
            "That finding is not on record",
            "It may belong to a database that has since been started over. Pick "
            "another from the list.",
        ))
        return
    finding = record["finding"]
    with st.container(key=f"card_{key}"):
        html(view.finding_heading(record))
        html(view.finding_facts(record))
        if finding.agreed_action_plan:
            html(view.quote(finding.agreed_action_plan, "Agreed action plan"))

        evidence_tab, rounds_tab, recurrence_tab, timeline_tab = st.tabs([
            "Evidence",
            f"Evidence rounds ({len(record['rounds'])})",
            f"Recurrence ({len(record['priors']) + len(record['later'])})",
            "Audit timeline",
        ])
        with evidence_tab:
            activity = record["activity"]
            latest = next((row for row in reversed(record["rounds"])
                           if row["round"].evidence_text), None)
            if activity is not None:
                assessment = activity["finding"]
                html(view.assessment_summary(assessment))
                evidence = activity["evidence"]
                if evidence is None:
                    html(view.empty_state(
                        "No document was ever filed",
                        "No evidence arrived for this check — which is the finding. "
                        "There is nothing to highlight.",
                    ))
                else:
                    st.caption("Source document, with cited spans highlighted · "
                               + view.evidence_line(evidence))
                    document(evidence.content, assessment.cited_spans, key=key)
                with st.expander("Provenance and assessment history"):
                    st.code(
                        f"prompt   {assessment.prompt_version or '—'}\n"
                        f"criteria {assessment.criteria_hash or '—'}\n"
                        f"evidence {assessment.evidence_hash[:16] or '—'}\n"
                        f"assessed {view.fmt_when(assessment.assessed_at)}",
                        language="text",
                    )
                    for item in activity["history"]:
                        marker = "current" if item.id == assessment.id else "superseded"
                        st.caption(f"{item.id} — {view.VERDICT_LABELS.get(item.verdict, item.verdict)} ({marker})")
                if actor["role"] == "pa_infosec":
                    post("recheck")
                    if st.button("Re-assess this check now", key=f"reassess_{key}"):
                        with st.spinner("Binding the latest evidence and re-running the "
                                        "pre-screen and assessment…"):
                            outcome = service.reassess(conn, finding.check_instance_id, today)
                        st.session_state["recheck"] = {
                            "ok": bool(outcome.new_assessment_id),
                            "message": view.reassess_message(outcome),
                        }
                        st.rerun()
            elif latest is not None and actor["role"] == "pa_infosec":
                recommendation = latest["recommendation"]
                html(view.advisory(recommendation))
                st.caption(f"Round {latest['round'].round_number} evidence, with cited "
                           f"spans highlighted · {latest['round'].evidence_ref}")
                document(latest["round"].evidence_text,
                         recommendation.cited_spans if recommendation else [], key=key)
            elif latest is not None:
                # The advisory reading is for the auditor. The owner filed this
                # evidence and benefits from its acceptance; showing them how the
                # model read it would let them write the next round to the model
                # rather than to the requirement. They see what they filed, and
                # the auditor's answer on the rounds tab.
                st.caption(f"Round {latest['round'].round_number} evidence, as filed · "
                           f"{latest['round'].evidence_ref}")
                document(latest["round"].evidence_text, [], key=key)
            else:
                html(view.empty_state(
                    "No evidence on file yet",
                    "Nothing has been filed against this finding. When the owner files "
                    "an evidence round, the document appears here with any cited "
                    "passages highlighted.",
                ))

        with rounds_tab:
            if not record["rounds"]:
                html(view.empty_state(
                    "No evidence rounds yet",
                    "Each time the owner files evidence a numbered round opens, and "
                    "the auditor answers it: accepted, or insufficient with the gaps. "
                    "None has been filed on this finding.",
                ))
            else:
                st.dataframe(
                    view.round_table(record), hide_index=True, width="stretch",
                    column_config={
                        "Round": st.column_config.NumberColumn("Round", width="small"),
                        "Filed": st.column_config.DatetimeColumn("Filed", format=WHEN_FORMAT),
                        "Response": RESPONSE_COLUMN,
                        "Answered": st.column_config.DatetimeColumn("Answered", format=WHEN_FORMAT),
                    },
                )
                for row in record["rounds"]:
                    answer = row["round"]
                    if answer.auditor_remarks:
                        html(view.quote(
                            answer.auditor_remarks,
                            f"Round {answer.round_number} · "
                            f"{view.RESPONSE_LABELS[answer.auditor_response]} by "
                            f"{row['responded_by']} on {view.fmt_date(answer.responded_at)}",
                        ))

        with recurrence_tab:
            if record["priors"] or record["later"]:
                html(view.recurrence_for(record))
            else:
                html(view.empty_state(
                    "No recurrence suggested",
                    "When recurrence detection finds the same kind of gap in another "
                    "unit or period, the earlier occurrence is quoted here beside this "
                    "one. It has found none for this finding.",
                ))

        with timeline_tab:
            st.caption("Audit timeline — every event touching this finding, its "
                       "evidence rounds and notifications, in the order it was written.")
            st.dataframe(
                view.timeline_table(record["timeline"]), hide_index=True, width="stretch",
                height=320,
                column_config={
                    "#": st.column_config.NumberColumn("#", width="small"),
                    "When": st.column_config.DatetimeColumn("When", format=WHEN_FORMAT),
                },
            )

        post("closure")
        if actor["may_close"] and finding.status == "open":
            with st.form(f"close_{key}", clear_on_submit=True):
                html(view.label("Close this finding"))
                st.caption("PA/InfoSec only, with remarks. Refused while an evidence "
                           "round is unanswered or was last found insufficient.")
                remarks = st.text_area("Closure remarks", height=80,
                                       placeholder="What satisfied you, and on what evidence.")
                if st.form_submit_button("Close finding", type="primary"):
                    ok, message = service.close_finding(conn, finding.id, by=actor["id"],
                                                        remarks=remarks)
                    st.session_state["closure"] = {"ok": ok, "message": message}
                    st.rerun()


def brief_panel(conn, today: date) -> None:
    """The prioritisation brief: one model call over the deterministic ranking."""
    with st.container(key="card_brief"):
        written = st.session_state.get("brief")
        stale = written is not None and written.as_of != today
        head, action = st.columns([4, 1.1], vertical_alignment="center")
        with head:
            st.subheader("Prioritisation brief")
        st.caption(
            "Open findings ranked deterministically — severity band first, then "
            "points. A model reads the ranking and the section 8 figures and "
            "says where attention would go furthest. Advisory; it changes nothing."
        )
        if action.button("Write the brief" if written is None or stale else "Write it again",
                         key="write_brief", width="stretch"):
            with st.spinner("Reading the ranking and the section 8 figures…"):
                st.session_state["brief"] = service.brief(conn)
            st.rerun()
        if written is None:
            html(view.empty_state(
                f"No brief written for {view.fmt_date(today)}",
                "Press **Write the brief** to have the ranking read and this "
                "cycle's priorities drafted.",
            ))
            return
        if stale:
            st.caption(f"Written for {view.fmt_date(written.as_of)}; the calendar has "
                       f"moved since.")
        if written.published:
            html(view.brief_priorities(written))
            patterns, focus = st.columns(2, gap="large")
            with patterns:
                html(view.label("Emerging patterns"))
                html(view.claims(written.emerging_patterns, written.metrics,
                                 "No pattern worth naming this cycle."))
            with focus:
                html(view.label("Recommended focus"))
                html(view.claims(written.recommended_focus, written.metrics,
                                 "No focus recommended."))
            st.caption(f"Written for {view.fmt_date(written.as_of)} · every claim cites "
                       f"the findings or figures it rests on")
        elif written.withheld:
            st.warning("The drafted brief made a claim that did not check out, so it "
                       "was withheld: " + "; ".join(written.withheld[:3]))
        with st.expander("The full ranking"):
            st.dataframe(
                view.ranking_table(written.ranked), hide_index=True, width="stretch",
                height=320,
                column_config={
                    "Rank": st.column_config.NumberColumn("Rank", width="small"),
                    "Band": st.column_config.MultiselectColumn(
                        "Band", options=list(view.SEVERITIES),
                        color=[view.SEVERITY_PILL[s] for s in view.SEVERITIES]),
                    "Points": st.column_config.ProgressColumn(
                        "Points", min_value=0, max_value=210, format="%d"),
                    "Chronic": st.column_config.CheckboxColumn("Chronic", width="small"),
                },
            )
        with st.expander("How the order is built"):
            st.code(service.priority_formula(), language="text")


@st.dialog("Notification", width="medium", dismissible=False)
def notification(conn, note: dict[str, Any], actor: dict[str, Any]) -> None:
    """One notification, read in a modal the page waits behind.

    Not dismissible by clicking outside or pressing Escape: the reader closes it
    or marks it read. Either way the inbox table's selection is reset, because a
    selection that survived the rerun would open the same notification again.
    """
    html(view.notification_header(note))
    html(view.quote(note["body"]))
    close_col, read_col = st.columns(2)
    if close_col.button("Close", width="stretch", key=f"close_{note['id']}"):
        st.session_state["inbox_table_version"] = st.session_state.get("inbox_table_version", 0) + 1
        st.rerun()
    if note["unread"] and read_col.button("Mark as read", type="primary", width="stretch",
                                          key=f"read_{note['id']}"):
        ok, message = service.mark_read(conn, note["id"], by=actor["id"])
        st.session_state["inbox_result"] = {"ok": ok, "message": message}
        st.session_state["inbox_table_version"] = st.session_state.get("inbox_table_version", 0) + 1
        st.rerun()


# --- a finding, opened over the list -----------------------------------------

@st.dialog("Finding", width="large", dismissible=False)
def finding_popup(conn, finding_id: str, *, actor: dict[str, Any], today,
                  version_key: str) -> None:
    """One finding in full, opened over the list rather than below it.

    Open for as long as `selected_finding` is set, which is also how other pages
    deep-link a finding. Closes by its own button, which clears that and bumps
    the table's version: a selection that survived the rerun would reopen it,
    the same trap the inbox modal avoids the same way. An action taken inside —
    closing the finding, re-assessing its check — reruns and reopens it showing
    the new state, so the result of the action is the next thing on screen.
    """
    _, close_col = st.columns([5, 1])
    if close_col.button("Close", width="stretch", key=f"finding_popup_close_{finding_id}"):
        st.session_state.pop("selected_finding", None)
        st.session_state[version_key] = st.session_state.get(version_key, 0) + 1
        st.rerun()
    finding_detail(conn, finding_id, actor=actor, today=today)


# --- the two evidence forms, each in its own modal ---------------------------
#
# An owner files evidence for two different things, and they used to sit on one
# page as two near-identical forms: evidence *answering a finding*, which goes
# to an auditor, and evidence for *a scheduled check*, which goes through the
# pre-screen and assessment. Each now opens from its own labelled button, so
# the page says which is which before anything is filled in.

EVIDENCE_TYPES = ["txt", "md", "json", "csv", "log"]


def open_evidence_form(kind: str) -> None:
    """Remember which evidence form is open, so it survives the reruns inside it.

    A dialog drawn only on the run its button was pressed would vanish the
    moment anything inside it was touched. The open form is parked in session
    state instead and closes by its own Cancel or Submit, the way the
    notification modal closes by its own buttons.
    """
    st.session_state["evidence_form"] = kind


def _close_evidence_form() -> None:
    st.session_state.pop("evidence_form", None)


def evidence_forms(conn, *, actor, today, where: str, finding_id: str | None = None) -> None:
    """Draw whichever evidence form is open on this page, if any.

    Scoped to the page that opened it, so a form left open does not follow the
    owner to the next page they visit.
    """
    kind = st.session_state.get("evidence_form")
    if kind == f"check@{where}":
        check_evidence(conn, actor, today)
    elif finding_id and kind == f"finding:{finding_id}":
        finding_evidence(conn, finding_id, actor)


@st.dialog("File evidence for this finding", width="large", dismissible=False)
def finding_evidence(conn, finding_id: str, actor: dict[str, Any]) -> None:
    """One evidence round on one finding. An auditor answers it; filing closes nothing."""
    st.caption(f"Answers **{finding_id}**. An auditor accepts it, or returns it with "
               "what is still missing. Filing evidence does not close the finding.")
    reference = st.text_input("Evidence reference", placeholder="e.g. HR-LEAVERS-2027-03.pdf",
                              key=f"round_ref_{finding_id}")
    uploaded = st.file_uploader("Evidence document", type=EVIDENCE_TYPES,
                                key=f"round_file_{finding_id}")
    pasted = st.text_area("…or paste the evidence", height=120, key=f"round_text_{finding_id}")
    note = st.text_area("Note to the auditor", height=70, key=f"round_note_{finding_id}",
                        placeholder="What changed, and where to look.")
    cancel_col, file_col = st.columns(2)
    if cancel_col.button("Cancel", width="stretch", key=f"round_cancel_{finding_id}"):
        _close_evidence_form()
        st.rerun()
    if file_col.button("File evidence round", type="primary", width="stretch",
                       key=f"round_submit_{finding_id}"):
        text = (uploaded.getvalue().decode("utf-8", errors="replace")
                if uploaded is not None else pasted)
        ok, message = service.open_evidence_round(
            conn, finding_id, by=actor["id"],
            evidence_ref=reference or (uploaded.name if uploaded else ""),
            evidence_text=text, note=note,
        )
        st.session_state["round_result"] = {"ok": ok, "message": message}
        _close_evidence_form()
        st.rerun()


@st.dialog("File evidence for a scheduled check", width="large", dismissible=False)
def check_evidence(conn, actor: dict[str, Any], today) -> None:
    """Evidence for a compliance activity the unit owes, judged by the pipeline.

    Files go into the same staging table as the generated corpus and through the
    same pre-screen and assessment — nothing about an upload is a special case.
    """
    unit = view.unit_name(conn, actor["unit"]) or "your unit"
    st.caption(f"A periodic obligation {unit} owes evidence for — not a finding. It goes "
               "through the same pre-screen and assessment as every other submission.")
    checks = view.owner_checks(conn, actor["unit"], today) if actor["unit"] else []
    if not checks:
        html(view.empty_state(
            "No evidence due",
            "Checks appear here once a cycle raises them for your unit's controls.",
        ))
        if st.button("Close", width="stretch", key="check_close"):
            _close_evidence_form()
            st.rerun()
        return

    labels = {c["id"]: f"{c['activity']} · {c['period']} · {view.due_phrase(c['days_past'])}"
              for c in checks}
    target = st.selectbox("Against check", list(labels), format_func=labels.get,
                          key="upload_target")
    chosen_type = st.selectbox(
        "Document type", service.doc_types_for(conn, target),
        format_func=lambda kind: kind.replace("_", " "),
        help="The first entries are what this control accepts. Pick another to see "
             "the wrong-type rule reject it before any model is asked.",
    )
    remediation = st.checkbox("This is remediation for an existing finding", True)
    recheck = st.checkbox(
        "Re-check it straight away", True,
        help="Runs the pre-screen and, if the rules cannot decide it, the "
             "assessment — the same path any other evidence takes.",
    )
    uploaded = st.file_uploader("Evidence file", type=EVIDENCE_TYPES,
                                help="Plain text, markdown, JSON or CSV.")
    typed = st.text_area("…or paste the evidence directly", height=120,
                         placeholder="Paste a report here if you would rather not upload a file.")
    cancel_col, submit_col = st.columns(2)
    if cancel_col.button("Cancel", width="stretch", key="check_cancel"):
        _close_evidence_form()
        st.rerun()
    if submit_col.button("Submit evidence", type="primary", width="stretch"):
        content, name = "", "pasted.txt"
        if uploaded is not None:
            content = uploaded.getvalue().decode("utf-8", errors="replace")
            name = uploaded.name
        elif typed.strip():
            content = typed
        if not content.strip():
            st.session_state["upload"] = {
                "ok": False, "message": "Nothing to submit — upload a file or paste text.",
            }
        else:
            with st.spinner("Filing the evidence and re-checking it…"):
                submission = service.submit_evidence(
                    conn, instance_id=target, filename=name, content=content,
                    author=actor["name"], doc_type=chosen_type, as_of=today,
                    is_remediation=remediation,
                )
                lines = [f"**{submission.id}** filed against {labels[target]} — "
                         f"{len(content.encode()):,} bytes, {chosen_type.replace('_', ' ')}."]
                if recheck:
                    outcome = service.reassess(conn, target, today)
                    lines.append(view.reassess_message(outcome) if outcome.new_assessment_id
                                 else f"Not re-checked: {outcome.reason}")
                else:
                    lines.append("It will be judged on the next cycle.")
            st.session_state["upload"] = {"ok": True, "message": "\n\n".join(lines)}
        _close_evidence_form()
        st.rerun()
