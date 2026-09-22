"""PA/InfoSec · Recurrence. The same kind of gap, somewhere else, some time later."""

import streamlit as st

from sentinelops.repositories import repositories
from sentinelops.ui import service, shell, view

conn, today, actor = shell.context()
recurring = service.portfolio_analytics(conn)["recurring"]
links = service.recurrence_links(conn)

shell.html(view.page_header(
    "Recurrence",
    "The same kind of gap turning up again in a different unit, project or period. "
    "Links are suggested by the model and point at the earlier finding; they merge "
    "nothing. The groupings below them are arithmetic.",
    eyebrow="PA/InfoSec · insight",
))
crossing = [row for row in links if row["crosses_units"]]
shell.html(view.figures([
    view.Figure("Suggested links", str(len(links)),
                f"{len(crossing)} between different units"),
    view.Figure("Recurring categories", str(recurring["by_gap_category"]["count"]),
                "Same category, another unit or quarter"),
    view.Figure("Longest gap", view.plural(max((r["months_apart"] for r in links), default=0), "month"),
                "Between an occurrence and the one it resembles"),
    view.Figure("Findings involved", str(recurring["findings_involved"]),
                "On either end of a link"),
]))

# The rollups come first: the categories that recur, and where, are the
# summary a reader wants before the individual links. Both take the full
# width — the link cards put two findings side by side, and the rollup's
# unit and period lists need room to wrap rather than being cut off.
with st.container(key="card_rollup"):
    by_category_tab, groups_tab = st.tabs(["By category", "Recurring categories"])
    with by_category_tab:
        st.caption("Suggested links, rolled up per gap category.")
        if recurring["by_category"]:
            shell.html(view.wrapping_table(
                ["Category", "Links", "Units", "Longest gap"],
                [[view._e(name.replace("_", " ")), str(row["links"]),
                  view.tags(row["unit_names"]),
                  view._e(view.plural(row["max_months_apart"], "month"))]
                 for name, row in recurring["by_category"].items()],
                numeric={1, 3},
            ))
        else:
            shell.html(view.empty_state(
                "Nothing to roll up",
                "The rollup counts suggested links per category, and there are none yet.",
            ))
    with groups_tab:
        st.caption("Section 8's definition: a category holding findings in more than "
                   "one unit or quarter.")
        groups = recurring["by_gap_category"]["categories"]
        if groups:
            shell.html(view.wrapping_table(
                ["Category", "Findings", "Units", "Periods", "First raised", "Last raised"],
                [[view._e(name.replace("_", " ")), str(row["findings"]),
                  view.tags(row["unit_names"]), view.tags(row["periods"]),
                  view._e(view.fmt_date(row["first_raised"])),
                  view._e(view.fmt_date(row["last_raised"]))]
                 for name, row in groups.items()],
                numeric={1}, nowrap={4, 5},
            ))
        else:
            shell.html(view.empty_state(
                "No category recurs yet",
                "A category recurs once it holds findings in two units or two quarters. "
                "Findings need a gap category first, which classification gives them.",
            ))

with st.container(key="card_pairs"):
    st.subheader("This has happened before")
    if not links:
        shell.html(view.empty_state(
            "No recurrence suggested yet",
            "Findings are classified and compared with earlier ones as they are "
            "raised. Run a cycle — once two findings describe the same kind of gap "
            "in different places, the pair appears here.",
        ))
    else:
        categories = sorted({row["category"] for row in links if row["category"]})
        filter_col, _ = st.columns([1, 2])
        category = filter_col.selectbox(
            "Gap category", [""] + categories,
            format_func=lambda c: c.replace("_", " ") if c else "All categories",
        )
        shown = [row for row in links if not category or row["category"] == category]
        limit = st.session_state.get("recurrence_limit", 8)
        st.caption(f"Showing {min(limit, len(shown))} of "
                   f"{view.plural(len(shown), 'link')}, earlier finding on the left.")
        findings = {f.id: f for f in repositories(conn)["findings"].list()}
        shell.html("".join(
            view.recurrence_pair(findings[row["finding"]], row["unit"],
                                 findings[row["prior"]], row["prior_unit"], row["reason"])
            for row in shown[:limit]
        ))
        if len(shown) > limit:
            if st.button(f"Show {min(8, len(shown) - limit)} more", key="recurrence_more"):
                st.session_state["recurrence_limit"] = limit + 8
                st.rerun()
