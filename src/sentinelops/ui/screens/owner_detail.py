"""Unit owner · Finding detail. Progress, evidence, and the auditor's responses.

There is no Close control and no Accept control on this page, for anyone: this
page is only ever registered for a unit owner, and section 7 asks for those
controls to be absent rather than disabled.
"""

import streamlit as st

from sentinelops.ui import service, shell, view

conn, today, actor = shell.context()
unit = view.unit_name(conn, actor["unit"]) or "your unit"

shell.html(view.page_header(
    "Finding detail",
    "Report your progress, file evidence, and follow the auditor's response to "
    "each round. Filing evidence does not close a finding — an auditor does.",
    eyebrow=f"Unit owner · {unit}",
))

# Open findings first, so the page opens on work rather than on history.
rows = sorted(view.my_findings(conn, actor["id"], today, include_closed=True),
              key=lambda r: (r["status"] != "open", r["target"], r["id"]))
if not rows:
    shell.html(view.empty_state(
        f"No findings for {unit}",
        "Once a finding is raised against your unit you can open it here, report "
        "progress and file evidence rounds.",
    ))
else:
    by_id = {row["id"]: row for row in rows}
    ids = list(by_id)
    wanted = st.session_state.get("owner_finding")
    chosen = st.selectbox(
        "Finding", ids, index=ids.index(wanted) if wanted in by_id else 0,
        format_func=lambda fid: (f"{fid} · {by_id[fid]['severity'] or 'Unassigned'} · "
                                 f"{by_id[fid]['timing']}"),
    )
    st.session_state["owner_finding"] = chosen
    shell.finding_detail(conn, chosen, actor=actor, today=today, key="owner")

    row = by_id[chosen]
    if row["status"] == "open":
        progress_col, file_col = st.columns([1, 1.4], gap="large")
        with progress_col:
            with st.container(key="card_progress"):
                st.subheader("Your progress")
                st.caption("Self-reported and advisory. It tells PA/InfoSec where you are; "
                           "it moves nothing.")
                shell.post("progress_result")
                current = row["progress"] if row["progress"] in view.PROGRESS_STEPS else None
                progress = st.segmented_control(
                    "Where are you?", list(view.PROGRESS_STEPS), default=current,
                    format_func=view.PROGRESS_LABELS.get, key=f"progress_{chosen}",
                )
                if st.button("Record progress", disabled=progress in (None, current)):
                    ok, message = service.record_progress(conn, chosen, progress, by=actor["id"])
                    st.session_state["progress_result"] = {"ok": ok, "message": message}
                    st.rerun()
        with file_col:
            with st.container(key="card_file"):
                st.subheader("File evidence for this finding")
                shell.post("round_result")
                if row["latest_response"] == "pending":
                    shell.html(view.empty_state(
                        f"Round {row['rounds']} is with PA/InfoSec",
                        "An auditor answers a round before the next one opens. You will "
                        "get a notification either way.",
                    ))
                else:
                    with st.form(f"file_round_{chosen}", clear_on_submit=True):
                        reference = st.text_input("Evidence reference",
                                                  placeholder="e.g. HR-LEAVERS-2027-03.pdf")
                        uploaded = st.file_uploader("Evidence document",
                                                    type=["txt", "md", "json", "csv", "log"])
                        pasted = st.text_area("…or paste the evidence", height=120)
                        note = st.text_area("Note to the auditor", height=70,
                                            placeholder="What changed, and where to look.")
                        if st.form_submit_button("File evidence round", type="primary"):
                            text = (uploaded.getvalue().decode("utf-8", errors="replace")
                                    if uploaded is not None else pasted)
                            ok, message = service.open_evidence_round(
                                conn, chosen, by=actor["id"],
                                evidence_ref=reference or (uploaded.name if uploaded else ""),
                                evidence_text=text, note=note,
                            )
                            st.session_state["round_result"] = {"ok": ok, "message": message}
                            st.rerun()

with st.container(key="card_upload"):
    st.subheader("Submit evidence")
    st.caption(f"Compliance activities {unit} owes evidence for. Files go into the "
               "same staging table as the generated corpus and through the same "
               "pre-screen and assessment — nothing about an upload is a special case.")
    checks = view.owner_checks(conn, actor["unit"], today) if actor["unit"] else []
    if not checks:
        shell.html(view.empty_state(
            "No evidence due",
            "Checks appear here once a cycle raises them for your unit's controls.",
        ))
    else:
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
        uploaded = st.file_uploader("Evidence file", type=["txt", "md", "json", "csv", "log"],
                                    help="Plain text, markdown, JSON or CSV.")
        typed = st.text_area("…or paste the evidence directly", height=120,
                             placeholder="Paste a report here if you would rather not upload a file.")
        if st.button("Submit evidence", type="primary"):
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
            st.rerun()
        shell.post("upload")
