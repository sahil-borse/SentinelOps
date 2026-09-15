"""PA/InfoSec · Walkthrough. The guided demo, step by step, driven by the data."""

import streamlit as st

from sentinelops.ui import shell, story, view

conn, today, actor = shell.context()

shell.html(view.page_header(
    "Walkthrough",
    "Six steps through what the system does, each run for real against the demo "
    "database. Progress is read from the data, so a reload resumes where the work is.",
    eyebrow="Assurance · guided demo",
))

step_index = st.session_state.get("step", story.current_step(conn))
step_index = max(0, min(step_index, len(story.STEPS) - 1))
step = story.STEPS[step_index]

with st.container(key="card_walkthrough"):
    shell.html(f"<span class='stepnav'>GUIDED WALKTHROUGH · step {step_index + 1} of "
               f"{len(story.STEPS)}</span>")
    st.subheader(step.title)
    shell.html(f"<div class='why'>{view.rich(story.why_for(step, conn))}</div>")

    go, back, forward, _ = st.columns([2, 1, 1, 3])
    if go.button(step.button, type="primary", width="stretch"):
        with st.spinner("Working through the step…"):
            outcome = story.run(conn, step.key)
        st.session_state["outcome"] = {
            "headline": outcome.headline, "detail": outcome.detail,
            "warning": outcome.warning, "step": step_index,
        }
        if outcome.focus:
            st.session_state["selected"] = outcome.focus
        st.session_state["step"] = min(step_index + 1, len(story.STEPS) - 1)
        st.rerun()
    if back.button("Back", width="stretch", disabled=step_index == 0):
        st.session_state["step"] = step_index - 1
        st.rerun()
    if forward.button("Skip", width="stretch", disabled=step_index == len(story.STEPS) - 1):
        st.session_state["step"] = step_index + 1
        st.rerun()

    shown = st.session_state.get("outcome")
    if shown:
        if shown.get("warning"):
            st.error(shown["warning"])
        shell.html(
            f"<div class='outcome'>{view.rich(shown['headline'])}<br><br>"
            + "<br><br>".join(view.rich(line) for line in shown["detail"])
            + "</div>"
        )
