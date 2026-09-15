"""Model cost. Reached only by its address, /cost — no page links here.

Every model call the system has made, read off the response objects as section 9
requires. Kept off the working screens: spend is for whoever runs the system,
not part of a compliance team's morning.
"""

import streamlit as st

from sentinelops.ui import shell, view

conn, today, actor = shell.context()
meter = view.token_meter(conn)

shell.html(view.page_header(
    "Model cost",
    "Every model call made so far, with token counts read off the provider's "
    "response objects — never estimated. Costs use the rates in "
    "`llm/metering.py`; with the stub client those rates are placeholders, so "
    "the shares are the durable figure, not the dollars.",
    eyebrow="Operations",
))
shell.html(view.figures([
    view.Figure("Model calls", f"{meter['calls']:,}", "Since the demo was seeded"),
    view.Figure("Tokens", f"{meter['total_tokens']:,}",
                f"{meter['input_tokens']:,} in · {meter['output_tokens']:,} out"),
    view.Figure("Cached", f"{meter['cached_tokens']:,}", "Input tokens served from cache"),
    view.Figure("Cost", f"${meter['cost_usd']:.4f}", "At the configured rates"),
    view.Figure("Decided without a model", f"{meter['zero_model_share']:.0%}",
                f"{meter['decided_by_rule']} of {meter['assessments']} assessments by rule"),
]))

purpose_col, tier_col = st.columns([1.6, 1], gap="medium")
with purpose_col:
    with st.container(key="card_spend_purpose"):
        st.subheader("By what made the call")
        rows = view.spend_by_purpose(conn)
        if rows:
            st.caption("Each call's label says which part of the system asked.")
            st.dataframe(
                [{"Purpose": r["purpose"], "Calls": r["calls"], "Input": r["input"],
                  "Output": r["output"], "Cached": r["cached"], "Tokens": r["tokens"],
                  "Share": r["share"], "Cost": r["cost"]} for r in rows],
                hide_index=True, width="stretch",
                column_config={
                    "Purpose": st.column_config.TextColumn("Purpose", width="medium"),
                    "Share": st.column_config.ProgressColumn(
                        "Share of tokens", min_value=0, max_value=100, format="%.0f%%",
                        width="medium"),
                    "Cost": st.column_config.NumberColumn("Cost", format="$%.4f"),
                },
            )
        else:
            shell.html(view.empty_state(
                "No model calls yet",
                "Run a cycle. Pre-screen rules decide what they can first; the model "
                "is asked only about what they cannot.",
            ))
with tier_col:
    with st.container(key="card_spend_tier"):
        st.subheader("By tier and model")
        tiers = view.spend_by_tier(conn)
        if tiers:
            st.dataframe(
                [{"Tier": t["tier"], "Model": t["model"], "Calls": t["calls"],
                  "Tokens": t["tokens"], "Cost": t["cost"]} for t in tiers],
                hide_index=True, width="stretch",
                column_config={"Cost": st.column_config.NumberColumn("Cost", format="$%.4f")},
            )
        else:
            shell.html(view.empty_state("No model calls yet",
                                        "Tiers appear once a call has been metered."))
