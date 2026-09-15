"""PA/InfoSec · Audit trail. Verify the chain; build the pack from the log."""

import streamlit as st

from sentinelops.ui import service, shell, view

conn, today, actor = shell.context()
meter = view.token_meter(conn)
totals = service.counts(conn)

shell.html(view.page_header(
    "Audit trail",
    "Append-only and hash-chained: every entry carries the hash of the one before "
    "it. Verify it, or build the auditor-ready pack straight from the log.",
    eyebrow="PA/InfoSec · assurance",
))
shell.html(view.figures([
    view.Figure("Audit events", f"{totals['audit_events']:,}", "Written as things happened"),
    view.Figure("Model calls", f"{meter['calls']:,}", f"{meter['total_tokens']:,} tokens"),
    view.Figure("Cost", f"${meter['cost_usd']:.4f}", "Read off each response; placeholder rates"),
    view.Figure("Decided without a model", f"{meter['zero_model_share']:.0%}",
                "Findings reached by a pre-screen rule"),
]))

verify_col, pack_col = st.columns(2, gap="large")
with verify_col:
    with st.container(key="card_verify"):
        st.subheader("Verify the chain")
        st.caption("Recomputes every entry's hash and checks each links to the one "
                   "before it. An edited row breaks the chain at that row.")
        if st.button("Verify audit chain", type="primary"):
            with st.spinner("Recomputing every hash in the chain…"):
                st.session_state["chain"] = service.verify_chain(conn)
        chain = st.session_state.get("chain")
        if chain is None:
            shell.html(view.empty_state(
                "Not verified this session",
                "Press **Verify audit chain** to check every entry against the one "
                "before it.",
            ))
        elif chain.ok:
            st.success(f"Chain intact — {chain.checked:,} entries verified, every entry "
                       "hashed against the one before it.")
        else:
            st.error(f"Chain broken at sequence {chain.broken_at}: {chain.reason}")

with pack_col:
    with st.container(key="card_pack"):
        st.subheader("Audit pack")
        start, end = service.pack_period(conn)
        st.caption(f"Built from the audit log alone, {view.fmt_date(start)} to "
                   f"{view.fmt_date(end)}. No current-state table is read.")
        if st.button("Generate audit pack"):
            with st.spinner("Replaying the audit log into the pack…"):
                pack, markdown, page = service.generate_pack(
                    conn, period_start=start, period_end=end,
                    scope="All process areas, all applicable controls",
                )
            st.session_state["pack"] = (pack.totals["events"], markdown, page)
        if st.session_state.get("pack"):
            events, markdown, page = st.session_state["pack"]
            st.success(f"Pack built from {events:,} audit events.")
            name = service.pack_file_name(conn)
            html_col, md_col = st.columns(2)
            html_col.download_button("Download pack (HTML)", page, file_name=f"{name}.html",
                                     mime="text/html", width="stretch")
            md_col.download_button("Download pack (Markdown)", markdown,
                                   file_name=f"{name}.md", mime="text/markdown",
                                   width="stretch")
        else:
            shell.html(view.empty_state(
                "No pack built this session",
                "Press **Generate audit pack** to replay the log into a pack an "
                "external auditor can read, as HTML and markdown.",
            ))
