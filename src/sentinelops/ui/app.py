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
import streamlit.components.v1 as components

# Absolute, not relative: Streamlit executes this file as a top-level
# script, not as a package member, so `from . import ...` fails at the
# first browser connect — after the server has already reported healthy.
from sentinelops.ui import service, story, view

st.set_page_config(page_title="SentinelOps", layout="wide", page_icon="🛡️")

CSS = """
<style>
  .doc { background:#fbfbf9; border:1px solid #ddd; padding:.9rem 1.1rem;
         white-space:pre-wrap; font-size:.86rem; line-height:1.55;
         font-family:ui-monospace,SFMono-Regular,Consolas,monospace;
         max-height:30rem; overflow-y:auto; }
  .elide { color:#999; font-style:italic; background:#f0f0ee; padding:0 .3rem;
           border-radius:2px; }
  .doc mark { background:#ffe680; box-shadow:0 0 0 2px #ffe680; border-radius:2px; }
  .pill { display:inline-block; padding:.05rem .5rem; border-radius:10px;
          font-size:.78rem; font-weight:600; }
  .v-gap,.v-insufficient_evidence { background:#fde8e8; color:#8a1c1c; }
  .v-compliant { background:#e6f4ea; color:#0a6b32; }
  .v-partial { background:#fff4d6; color:#7a5200; }
  .muted { color:#666; font-size:.84rem; }
  .why { background:#f4f6fb; border-left:4px solid #4a6fa5; padding:.8rem 1.1rem;
         margin:.4rem 0 .9rem 0; font-size:.95rem; line-height:1.6; }
  .outcome { background:#eef7f0; border-left:4px solid #2e7d4f; padding:.8rem 1.1rem;
             margin:.5rem 0; line-height:1.6; }
  .stepnav { color:#555; font-size:.85rem; letter-spacing:.02em; }
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

# ------------------------------------------------------------ walkthrough --
step_index = st.session_state.get("step", story.current_step(conn))
step_index = max(0, min(step_index, len(story.STEPS) - 1))
step = story.STEPS[step_index]

with st.container(border=True):
    st.markdown(
        f"<span class='stepnav'>GUIDED WALKTHROUGH · step {step_index + 1} of "
        f"{len(story.STEPS)}</span>", unsafe_allow_html=True,
    )
    st.subheader(step.title)
    st.markdown(f"<div class='why'>{view.rich(step.why)}</div>",
                unsafe_allow_html=True)

    go, back, forward, _ = st.columns([2, 1, 1, 3])
    if go.button(step.button, type="primary", use_container_width=True):
        with st.spinner("Working…"):
            outcome = story.run(conn, step.key)
        st.session_state["outcome"] = {
            "headline": outcome.headline, "detail": outcome.detail,
            "warning": outcome.warning, "step": step_index,
        }
        if outcome.focus:
            st.session_state["selected"] = outcome.focus
        st.session_state["step"] = min(step_index + 1, len(story.STEPS) - 1)
        st.rerun()
    if back.button("Back", use_container_width=True, disabled=step_index == 0):
        st.session_state["step"] = step_index - 1
        st.rerun()
    if forward.button("Skip", use_container_width=True,
                      disabled=step_index == len(story.STEPS) - 1):
        st.session_state["step"] = step_index + 1
        st.rerun()

    shown = st.session_state.get("outcome")
    if shown:
        if shown.get("warning"):
            st.error(shown["warning"])
        st.markdown(
            f"<div class='outcome'>{view.rich(shown['headline'])}<br><br>"
            + "<br><br>".join(view.rich(line) for line in shown["detail"])
            + "</div>",
            unsafe_allow_html=True,
        )

st.divider()
st.markdown("#### Operator console")
st.caption(
    "Everything the walkthrough did, in full detail. Safe to ignore on a first "
    "pass — the walkthrough above drives all of it."
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
if bar[5].button("Start over", use_container_width=True):
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
st.subheader("Assessment detail")
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
                expanded = st.session_state.get("doc_expanded", False)
                frame = view.document_frame(
                    evidence.content, finding.cited_spans, expanded=expanded,
                )
                # An iframe, so the document scrolls inside its own box and the
                # page length never depends on the document length.
                components.html(frame.html, height=frame.height, scrolling=True)
                st.caption(frame.caption())
                if not frame.fits or expanded:
                    if st.button(
                        "Show less" if expanded else "Show more",
                        key="doc_toggle",
                        help="Makes the panel taller. The document scrolls inside "
                             "it either way — the page does not grow.",
                    ):
                        st.session_state["doc_expanded"] = not expanded
                        st.rerun()
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
                st.markdown("**Assessment history**")
                for item in detail["history"]:
                    marker = "current" if item.id == finding.id else "superseded"
                    st.caption(f"{item.id} — {item.verdict} ({marker})")
            recheck = st.session_state.pop("recheck", None)
            if recheck:
                (st.success if recheck["ok"] else st.warning)(recheck["message"])
            if st.button("Re-assess this check now", use_container_width=True):
                with st.spinner("Binding remediation and re-running S2/S3…"):
                    outcome = service.reassess(conn, selected, today)
                if outcome.new_assessment_id:
                    message = (
                        f"Re-checked: **{outcome.verdict}** — "
                        f"{outcome.new_assessment_id} supersedes "
                        f"{outcome.superseded_assessment_id}."
                        + (" The action closed." if outcome.resolved
                           else " The action stayed open.")
                    )
                else:
                    message = outcome.reason
                st.session_state["recheck"] = {
                    "ok": bool(outcome.new_assessment_id), "message": message,
                }
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
        recheck = st.checkbox(
            "Re-check it straight away", True,
            help="Runs the pre-screen and, if the rules cannot decide it, the "
                 "assessment — the same path any other evidence takes.",
        )
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
                st.session_state["upload"] = {
                    "ok": False,
                    "message": "Nothing to submit — upload a file or paste text.",
                }
            else:
                submission = service.submit_evidence(
                    conn, instance_id=target, filename=name, content=content,
                    author=author or "unknown", doc_type=chosen, as_of=today,
                    is_remediation=remediation,
                )
                lines = [
                    f"**{submission.id}** filed against `{target}` — "
                    f"{len(content.encode()):,} bytes, type `{chosen}`."
                ]
                if recheck:
                    outcome = service.reassess(conn, target, today)
                    if outcome.new_assessment_id:
                        lines.append(
                            f"Re-checked: **{outcome.verdict}** "
                            f"(decided by `{outcome.decided_by}`). "
                            f"{outcome.new_assessment_id} supersedes "
                            f"{outcome.superseded_assessment_id}."
                        )
                        lines.append(
                            "**The action closed.**" if outcome.resolved
                            else f"The action stayed open — {outcome.reason}"
                        )
                    else:
                        lines.append(f"Not re-checked: {outcome.reason}")
                else:
                    lines.append(
                        "Press **Re-assess this check now** in Assessment detail "
                        "above to have it judged."
                    )
                st.session_state["selected"] = target
                paragraphs = '\n\n'.join(lines)
                st.session_state["upload"] = {"ok": True, "message": paragraphs}
            st.rerun()

        # Rendered after the rerun, not before it: a message written immediately
        # before st.rerun() is discarded, which is why this used to look like
        # nothing had happened at all.
        posted = st.session_state.pop("upload", None)
        if posted:
            (st.success if posted["ok"] else st.error)(posted["message"])

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
