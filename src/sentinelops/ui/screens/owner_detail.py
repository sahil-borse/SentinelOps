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
                st.subheader("Evidence for this finding")
                shell.post("round_result")
                if row["latest_response"] == "pending":
                    shell.html(view.empty_state(
                        f"Round {row['rounds']} is with PA/InfoSec",
                        "An auditor answers a round before the next one opens. You will "
                        "get a notification either way.",
                    ))
                else:
                    st.caption("Answers this finding. An auditor accepts it, or returns "
                               "it with what is still missing. Filing closes nothing.")
                    if st.button("File evidence for this finding", type="primary",
                                 key=f"open_round_{chosen}"):
                        shell.open_evidence_form(f"finding:{chosen}")

with st.container(key="card_upload"):
    st.subheader(f"Scheduled checks for {unit}")
    checks = view.owner_checks(conn, actor["unit"], today) if actor["unit"] else []
    st.caption(
        "Separate from the finding above: periodic compliance activities your unit "
        f"owes evidence for — {view.plural(len(checks), 'check')} due. They go through "
        "the pre-screen and assessment, not to an auditor."
    )
    shell.post("upload")
    if st.button("File evidence for a scheduled check", key="open_check_detail"):
        shell.open_evidence_form("check@owner_detail")

shell.evidence_forms(conn, actor=actor, today=today, where="owner_detail",
                     finding_id=st.session_state.get("owner_finding") if rows else None)
