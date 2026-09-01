"""SentinelOps dashboard.

    streamlit run src/sentinelops/ui/app.py

Once it is up, nothing else needs a terminal: the calendar advances, cycles run,
evidence uploads, checks re-assess, the audit pack generates and the chain
verifies, all from the screen.

This file is deliberately dull. Every computation lives in `view.py` and every
action in `service.py`, both of which are tested; what is left here is layout.
"""

from __future__ import annotations

from datetime import date

import streamlit as st

# Absolute, not relative: Streamlit executes this file as a top-level
# script, not as a package member, so `from . import ...` fails at the
# first browser connect — after the server has already reported healthy.
from sentinelops.ui import service, view

st.set_page_config(page_title="SentinelOps", layout="wide", page_icon="🛡️")

CSS = """
<style>
  .doc { background:#fbfbf9; border:1px solid #ddd; padding:.9rem 1.1rem;
         white-space:pre-wrap; font-size:.86rem; line-height:1.55;
         font-family:ui-monospace,SFMono-Regular,Consolas,monospace; }
  .doc mark { background:#ffe680; box-shadow:0 0 0 2px #ffe680; border-radius:2px; }
  .pill { display:inline-block; padding:.05rem .5rem; border-radius:10px;
          font-size:.78rem; font-weight:600; }
  .v-gap,.v-insufficient_evidence { background:#fde8e8; color:#8a1c1c; }
  .v-compliant { background:#e6f4ea; color:#0a6b32; }
  .v-partial { background:#fff4d6; color:#7a5200; }
  .muted { color:#666; font-size:.84rem; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


@st.cache_resource
def database():
    conn = service.open_database()
    service.seed(conn)
    return conn


conn = database()
today = service.current_date(conn)
totals = service.counts(conn)
meter = view.token_meter(conn)

# ---------------------------------------------------------------- controls --
st.title("SentinelOps")
st.caption(
    "Compliance checks that cannot be forgotten, judged the same way everywhere, "
    "with the audit trail written as it happens."
)

bar = st.columns([1.5, 1, 1, 1, 1, 1.2])
bar[0].metric("Simulated date", today.isoformat())
if bar[1].button("Run cycle now", use_container_width=True, type="primary"):
    with st.spinner("Running S1 → S4…"):
        st.session_state["last_tick"] = service.tick(conn, today).summary()
    st.rerun()
for column, days, label in (
    (bar[2], 1, "+1 day"), (bar[3], 7, "+1 week"), (bar[4], 30, "+1 month"),
):
    if column.button(label, use_container_width=True):
        with st.spinner(f"Advancing {days} days and running the cycle…"):
            st.session_state["last_tick"] = service.advance(conn, days).summary()
        st.rerun()
if bar[5].button("Reset demo", use_container_width=True):
    conn.close()  # Windows will not delete a file that is still open
    database.clear()
    service.open_database(fresh=True).close()
    st.session_state.clear()
    st.rerun()

if st.session_state.get("last_tick"):
    st.success(st.session_state["last_tick"])

# ------------------------------------------------------------------ meters --
row = st.columns(6)
row[0].metric("Checks raised", totals["instances"])
row[1].metric("Open gaps", totals["flags_gap"])
row[2].metric("Overdue", totals["flags_overdue"])
row[3].metric("Exceptions", totals["flags_exception"])
row[4].metric("Actions open", totals["actions_open"],
              delta=f"{totals['actions_resolved']} resolved", delta_color="normal")
row[5].metric("Needs human review", totals["needs_review"])

cost = st.columns(5)
cost[0].metric("Model calls", f"{meter['calls']:,}")
cost[1].metric("Tokens", f"{meter['total_tokens']:,}")
cost[2].metric("Cached", f"{meter['cached_tokens']:,}")
cost[3].metric("Cost", f"${meter['cost_usd']:.4f}")
cost[4].metric("Decided without a model", f"{meter['zero_model_share']:.0%}",
               help="Findings reached by rule at S2 rather than by a model at S3.")

st.divider()

# ------------------------------------------------------- status and queues --
left, right = st.columns([1.15, 1])

with left:
    st.subheader("Compliance status by process area")
    st.dataframe(
        [
            {
                "Area": row.name, "Team": row.team, "Owner": row.owner,
                "Criticality": row.criticality, "Due": row.due,
                "Assessed": row.assessed, "Overdue": row.overdue,
                "Waived": row.waived, "Open gaps": row.gaps,
                "Worst severity": round(row.worst_severity, 2),
            }
            for row in view.status_by_area(conn)
        ],
        use_container_width=True, hide_index=True,
    )

with right:
    st.subheader("Overdue and escalation queue")
    queue = view.overdue_queue(conn, today)
    if not queue:
        st.info("Nothing overdue. Advance the calendar to make checks fall due.")
    else:
        st.dataframe(
            [
                {
                    "Check": row["instance"], "Category": row["category"],
                    "Severity": f"{row['severity']:.2f} {row['band']}",
                    "Days late": row["days_late"], "Escalation": row["escalation"],
                    "Owner": row["owner"], "Team": row["team"],
                }
                for row in queue[:40]
            ],
            use_container_width=True, hide_index=True, height=320,
        )
        st.caption(f"{len(queue)} open, worst first. Escalation 0 = with the owner, "
                   "1 = department head, 2 = Group Compliance.")

st.divider()

# ------------------------------------------------ finding detail + citation --
st.subheader("Finding detail")
pickable = view.assessable_instances(conn)
if not pickable:
    st.info("No checks assessed yet — press **Run cycle now**.")
else:
    default = st.session_state.get("selected", pickable[0])
    selected = st.selectbox(
        "Check instance", pickable,
        index=pickable.index(default) if default in pickable else 0,
    )
    st.session_state["selected"] = selected
    detail = view.finding_detail(conn, selected)

    if detail is None:
        st.info("No finding for that check yet.")
    else:
        finding = detail["finding"]
        head = st.columns([1, 1, 1, 1])
        head[0].markdown(
            f"**Verdict**<br><span class='pill v-{finding.verdict}'>"
            f"{finding.verdict}</span>", unsafe_allow_html=True,
        )
        head[1].metric("Confidence", f"{finding.confidence:.2f}")
        head[2].metric("Decided by", finding.decided_by)
        head[3].metric("Human review", "yes" if finding.needs_human_review else "no")

        st.markdown(f"**Rationale.** {finding.rationale}")
        if finding.gaps:
            for gap in finding.gaps:
                st.markdown(f"- **Gap:** {gap}")
        if finding.recommended_action:
            st.markdown(f"**Recommended action.** {finding.recommended_action}")

        document, meta = st.columns([2, 1])
        with document:
            st.markdown("**Source document, with cited spans highlighted**")
            evidence = detail["evidence"]
            if evidence is None:
                st.warning(
                    "No evidence was ever filed for this check — which is the "
                    "finding. Nothing to highlight."
                )
            else:
                st.markdown(
                    view.highlight(evidence.content, finding.cited_spans),
                    unsafe_allow_html=True,
                )
                missing = view.unmatched_spans(evidence.content, finding.cited_spans)
                if missing:
                    st.error(f"Cited text not found in the source: {missing}")
                st.caption(
                    f"{evidence.id} · {evidence.doc_type} · filed "
                    f"{evidence.submitted_at:%Y-%m-%d} by {evidence.author}"
                    + (" · remediation" if evidence.is_remediation else "")
                )
        with meta:
            st.markdown("**Provenance**")
            st.code(
                f"prompt   {finding.prompt_version or '—'}\n"
                f"criteria {finding.criteria_hash or '—'}\n"
                f"evidence {finding.evidence_hash[:16] or '—'}\n"
                f"assessed {finding.assessed_at:%Y-%m-%d}",
                language="text",
            )
            if len(detail["history"]) > 1:
                st.markdown("**Finding history**")
                for item in detail["history"]:
                    marker = "current" if item.id == finding.id else "superseded"
                    st.caption(f"{item.id} — {item.verdict} ({marker})")
            if st.button("Re-assess this check now", use_container_width=True):
                with st.spinner("Binding remediation and re-running S2/S3…"):
                    outcome = service.reassess(conn, selected, today)
                if outcome.new_finding_id:
                    st.success(
                        f"{outcome.new_finding_id} supersedes "
                        f"{outcome.superseded_finding_id}: {outcome.verdict}"
                        + (" — action resolved" if outcome.resolved else "")
                    )
                else:
                    st.warning(outcome.reason)
                st.rerun()

        with st.expander("Audit timeline for this check", expanded=False):
            st.dataframe(
                [
                    {
                        "#": row["seq"], "When": row["when"].strftime("%Y-%m-%d %H:%M"),
                        "Actor": row["actor"], "Owner": row["owner"],
                        "Event": row["event"], "Entity": row["entity"],
                    }
                    for row in view.timeline(conn, selected)
                ],
                use_container_width=True, hide_index=True, height=300,
            )

st.divider()

# ----------------------------------------------------------------- upload ---
upload, actions = st.columns([1, 1.2])

with upload:
    st.subheader("Submit evidence")
    st.caption(
        "Files uploaded here go into the same staging table as the generated "
        "corpus and through the same pre-screen and assessment. Nothing about "
        "an uploaded document is a special case."
    )
    targets = view.instances_awaiting_evidence(conn)
    if not targets:
        st.info("No checks are open for evidence yet.")
    else:
        target = st.selectbox("Against check", targets, key="upload_target")
        types = service.doc_types_for(conn, target)
        chosen = st.selectbox(
            "Document type", types,
            help="The first entries are what this control accepts. Pick another "
                 "to see the wrong-type rule reject it without a model call.",
        )
        author = st.text_input("Submitted by", value="R. Mehta")
        remediation = st.checkbox("This is remediation for an existing finding", True)
        uploaded = st.file_uploader(
            "Evidence file", type=["txt", "md", "json", "csv", "log"],
            help="Plain text, markdown, JSON or CSV.",
        )
        typed = st.text_area(
            "…or paste the evidence directly", height=120,
            placeholder="Paste a report here if you would rather not upload a file.",
        )
        if st.button("Submit evidence", type="primary", use_container_width=True):
            content = ""
            name = "pasted.txt"
            if uploaded is not None:
                content = uploaded.getvalue().decode("utf-8", errors="replace")
                name = uploaded.name
            elif typed.strip():
                content = typed
            if not content.strip():
                st.error("Nothing to submit — upload a file or paste some text.")
            else:
                submission = service.submit_evidence(
                    conn, instance_id=target, filename=name, content=content,
                    author=author or "unknown", doc_type=chosen, as_of=today,
                    is_remediation=remediation,
                )
                st.session_state["selected"] = target
                st.success(
                    f"{submission.id} filed against {target}. Press **Re-assess "
                    "this check now** above to have it judged."
                )
                st.rerun()

with actions:
    st.subheader("Open actions")
    rows = view.open_actions(conn)
    if not rows:
        st.info("No open actions.")
    else:
        st.dataframe(
            [
                {
                    "Action": r["action"], "Status": r["status"],
                    "Owner": r["owner"], "Team": r["team"],
                    "Due": r["due"].isoformat(), "From": r["finding"],
                }
                for r in rows[:40]
            ],
            use_container_width=True, hide_index=True, height=260,
        )
        st.caption(f"{len(rows)} open. "
                   f"{totals['actions_resolved']} resolved to date.")
    closed = view.resolved_actions(conn)
    if closed:
        with st.expander(f"{len(closed)} resolved", expanded=False):
            for row in closed:
                st.markdown(f"**{row['action']}** — {row['note']}")

st.divider()

# ------------------------------------------------------- audit and integrity --
st.subheader("Audit")
audit = st.columns([1, 1, 2])

if audit[0].button("Verify audit chain", use_container_width=True):
    st.session_state["chain"] = service.verify_chain(conn)
if audit[1].button("Generate audit pack", use_container_width=True):
    with st.spinner("Replaying the log…"):
        pack, markdown, page = service.generate_pack(
            conn, period_start=date(2026, 1, 1), period_end=date(2026, 12, 31),
            scope="All process areas, all applicable controls",
        )
    st.session_state["pack"] = (pack.totals["events"], markdown, page)

chain = st.session_state.get("chain")
if chain is not None:
    if chain.ok:
        audit[2].success(
            f"Chain intact — {chain.checked:,} entries verified, "
            "every entry hashed against the one before it."
        )
    else:
        audit[2].error(f"Chain broken at sequence {chain.broken_at}: {chain.reason}")

if st.session_state.get("pack"):
    events, markdown, page = st.session_state["pack"]
    st.success(f"Pack built from {events:,} audit events — no current-state table "
               "was read.")
    downloads = st.columns(2)
    downloads[0].download_button(
        "Download pack (HTML)", page, file_name="audit_pack_2026.html",
        mime="text/html", use_container_width=True,
    )
    downloads[1].download_button(
        "Download pack (Markdown)", markdown, file_name="audit_pack_2026.md",
        mime="text/markdown", use_container_width=True,
    )

st.caption(
    f"{totals['audit_events']:,} audit events · database "
    f"`{service.DB_PATH}` · corpus is synthetic and seeded."
)
