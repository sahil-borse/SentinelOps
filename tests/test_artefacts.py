"""`python -m sentinelops.demo.artefacts`, run so it cannot rot.

The demo is the deliverable for slice 16: a brief with its citations, an audit
report that has been confirmed and issued, and the token cost of one cycle
metered on its own. Each of those is asserted rather than eyeballed.
"""

import re


def test_the_demo_shows_a_cited_brief_an_issued_report_and_one_cycles_cost(
    tmp_path, capsys,
):
    from sentinelops.demo import artefacts

    artefacts.main(tmp_path)
    out = capsys.readouterr().out

    for heading in (
        "PRIORITY ORDER - HOW THE RANKING IS BUILT",
        "PRIORITISATION BRIEF",
        "AUDIT REPORT - ",
        "TOKEN COST OF ONE CYCLE",
        "TOKEN COST OF THE AUDIT REPORT",
    ):
        assert heading in out, heading

    assert "brief: published" in out
    assert "## Top priorities" in out and "_cites:" in out
    assert "Findings are ordered by severity band" in out

    assert "report status: issued" in out
    # In order, not adjacent: severity suggestion (slice 14) is also on the trail.
    trail = re.search(r"trail: (.+)", out).group(1).split(" -> ")
    steps = ("audit_conducted", "audit_report_generated", "audit_report_confirmed",
             "audit_report_issued")
    positions = [trail.index(step) for step in steps]
    assert positions == sorted(positions), trail
    assert "Confirmed by" in out, "the summary note states the confirmation"

    brief_row = re.search(r"^\s+BRIEF\s+(\d+)\s", out, re.MULTILINE)
    assert brief_row and brief_row.group(1) == "1", "one brief call per cycle"
    assert re.search(r"^\s+REPORT\s+1\s", out, re.MULTILINE), "one call per report"
    assert "ok=True" in out

    written = {path.name for path in tmp_path.iterdir()}
    assert any(n.startswith("prioritisation_brief_") and n.endswith(".html") for n in written)
    assert any(n.startswith("prioritisation_brief_") and n.endswith(".md") for n in written)
    assert any(n.startswith("audit_report_") and n.endswith(".html") for n in written)
    assert any(n.startswith("audit_report_") and n.endswith(".md") for n in written)
