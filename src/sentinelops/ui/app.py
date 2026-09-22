"""SentinelOps dashboard.

    streamlit run src/sentinelops/ui/app.py

The entry point: the theme, the header every page shares, the identity selector,
the simulated calendar, and navigation scoped to the selected identity's role.
Each page is a script in `screens/`.

Layout only. Every computation lives in `view.py` and every action in
`service.py`, both tested and neither importing Streamlit; `shell.py` holds the
two panels more than one page draws.
"""

from __future__ import annotations

import streamlit as st

# Absolute, not relative: Streamlit executes this file as a top-level script,
# not as a package member, so `from . import ...` fails at the first browser
# connect — after the server has already reported healthy.
from sentinelops.ui import service, shell, view

st.set_page_config(page_title="SentinelOps", layout="wide", page_icon="🛡️",
                   initial_sidebar_state="expanded")
shell.html(view.CSS)

conn = shell.database()
choices = view.identity_choices(conn)
labels = {choice["id"]: choice["label"] for choice in choices}
if st.session_state.get("acting_as") not in labels:
    st.session_state["acting_as"] = service.default_identity(conn)
else:
    # Written back to itself on purpose. A value bound to a widget key belongs to
    # the widget, and Streamlit may clean it up when a page calls `st.switch_page`
    # part-way through a run — which is what My findings does when an owner picks
    # a row. The identity was lost, fell back to the default auditor, and the
    # owner's Finding detail page, not being one of hers, sent her to Today.
    # Reassigning it makes it ordinary session state, which survives the switch.
    st.session_state["acting_as"] = st.session_state["acting_as"]

# Not authentication — section 11 rules that out — an identity selector. Its job
# is to make segregation of duties visible: pick someone and both the pages and
# the permitted actions change. A unit owner's pages have no Close control at all.
with st.sidebar:
    st.selectbox(
        "Acting as", list(labels), key="acting_as", format_func=labels.get,
        help="An identity selector, not a login. Choosing someone changes the pages "
             "you see and the actions you may take.",
    )

conn, today, actor = shell.context()

with st.sidebar:
    shell.html(view.identity_card(actor, choices))
    shell.html(view.calendar_card(today))
    # Named before the jump: the card and the button read the same planner.
    moment = service.next_event(conn)
    shell.html(view.next_event_card(moment, today))
    if moment is not None and st.button(
        "Jump to next event", type="primary", width="stretch",
        help="Moves the simulated clock straight to the milestone named above and "
             "runs that day's cycle — not a fixed step.",
    ):
        with st.spinner(f"Jumping to {view.fmt_date(moment.day)} — "
                        f"{moment.headline.title}…"):
            jumped = service.jump_to_next_event(conn)
        st.session_state["last_tick"] = view.jump_message(jumped)
        st.rerun()
    if st.button("Run cycle now", width="stretch",
                 help="Runs S1 to S4 for the simulated date: raise checks, screen, "
                      "assess, flag and chase."):
        with st.spinner(f"Running the cycle for {view.fmt_date(today)} — S1 to S4…"):
            summary = service.tick(conn, today).summary()
        st.session_state["last_tick"] = f"Cycle complete · {summary}"
        st.rerun()
    steps = st.columns(3, gap="small")
    for column, days, label in ((steps[0], 1, "+1 day"), (steps[1], 7, "+1 week"),
                                (steps[2], 30, "+1 month")):
        if column.button(label, width="stretch"):
            with st.spinner(f"Advancing {view.plural(days, 'day')} and running that "
                            f"day's cycle…"):
                summary = service.advance(conn, days).summary()
            st.session_state["last_tick"] = f"Cycle complete · {summary}"
            st.rerun()
    if st.button("Reset scenario", width="stretch",
                 help="Restores the exact seeded state, so every take starts identically."):
        with st.spinner("Restoring the seeded scenario…"):
            conn.close()  # Windows will not replace a file that is still open
            shell.database.clear()
            service.reset_scenario()
        st.session_state.clear()
        st.rerun()

# A count beside every page with something waiting for this identity.
badges = view.nav_badge_css(actor["role"], view.nav_badges(conn, actor, today))
if badges:
    shell.html(badges)

shell.html(view.topbar(actor, choices, today))
ticked = st.session_state.pop("last_tick", None)
if ticked:
    st.success(ticked)

navigation = {
    section: [
        st.Page(page["path"], title=page["title"], icon=page["icon"],
                default=page["default"])
        for page in pages
    ]
    for section, pages in view.pages_for(actor["role"]).items()
}
# Reachable by its address only — /cost — and linked from nowhere: model spend
# is for whoever runs the system, not part of anyone's working screen.
first_section = next(iter(navigation))
navigation[first_section] += [
    st.Page(page["path"], title=page["title"], icon=page["icon"], visibility="hidden")
    for page in view.HIDDEN_PAGES
]
st.navigation(navigation, position="sidebar", expanded=True).run()
