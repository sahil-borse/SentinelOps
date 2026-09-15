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
    if st.button("Run cycle now", type="primary", width="stretch",
                 help="Runs S1 to S4 for the simulated date: raise checks, screen, "
                      "assess, flag and chase."):
        with st.spinner(f"Running the cycle for {view.fmt_date(today)} — S1 to S4…"):
            st.session_state["last_tick"] = service.tick(conn, today).summary()
        st.rerun()
    steps = st.columns(3, gap="small")
    for column, days, label in ((steps[0], 1, "+1 day"), (steps[1], 7, "+1 week"),
                                (steps[2], 30, "+1 month")):
        if column.button(label, width="stretch"):
            with st.spinner(f"Advancing {view.plural(days, 'day')} and running that "
                            f"day's cycle…"):
                st.session_state["last_tick"] = service.advance(conn, days).summary()
            st.rerun()
    shell.html(view.meter_card(view.token_meter(conn)))
    if st.button("Start over", width="stretch",
                 help="Deletes the demo database and seeds the corpus again."):
        conn.close()  # Windows will not delete a file that is still open
        shell.database.clear()
        service.open_database(fresh=True).close()
        st.session_state.clear()
        st.rerun()

shell.html(view.topbar(actor, choices, today))
ticked = st.session_state.pop("last_tick", None)
if ticked:
    st.success(f"Cycle complete · {ticked}")

navigation = {
    section: [
        st.Page(page["path"], title=page["title"], icon=page["icon"],
                default=page["default"])
        for page in pages
    ]
    for section, pages in view.pages_for(actor["role"]).items()
}
st.navigation(navigation, position="sidebar", expanded=True).run()
