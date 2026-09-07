"""Section 8, and the promise that none of it goes near a model."""

import ast
from datetime import date
from pathlib import Path

import pytest

from sentinelops import analytics
from sentinelops.synth.calendar import SIMULATED_TODAY
from sentinelops.repositories import repositories
from sentinelops.stages import intelligence
from sentinelops.stages.assess import run as assess
from sentinelops.stages.flag import run as flag_stage
from sentinelops.stages.followup import run as followup
from sentinelops.stages.prescreen import run as prescreen
from sentinelops.stages.remediation import reassess_all
from sentinelops.stages.trigger import run_cycle
from sentinelops.synth import generate_corpus, seed_database

AS_OF = SIMULATED_TODAY
WINDOW = (date(2026, 1, 1), SIMULATED_TODAY)
SRC = Path(__file__).resolve().parents[1] / "src" / "sentinelops"


@pytest.fixture(scope="module")
def corpus():
    return generate_corpus()


@pytest.fixture
def run(conn, corpus):
    """A full replay, so the analytics have both tracks to count."""
    seed_database(conn, corpus)
    cycles = [date(2026, m, 28) for m in range(1, 13)]
    cycles += [d for d in (date(2027, m, 28) for m in range(1, 13))
               if d <= SIMULATED_TODAY]
    for as_of in cycles:
        run_cycle(conn, as_of)
        screen = prescreen(conn, as_of)
        if screen.to_assess:
            assess(conn, screen.to_assess, as_of)
        flag_stage(conn, as_of)
        followup(conn, as_of)
        reassess_all(conn, as_of)
    intelligence.classify(conn, AS_OF)
    intelligence.detect_recurrence(conn, AS_OF)
    return conn


@pytest.fixture
def portfolio(run):
    return run, analytics.portfolio(run, AS_OF, window=WINDOW)


# --- the promise -------------------------------------------------------------

def test_analytics_never_reaches_a_model():
    """Section 2 lists analytics under never-AI. This is where that is kept."""
    source = (SRC / "analytics.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        names = []
        if isinstance(node, ast.ImportFrom) and node.module:
            names = [node.module]
        elif isinstance(node, ast.Import):
            names = [a.name for a in node.names]
        for name in names:
            assert "llm" not in name.split("."), f"analytics imports {name}"
    body = source.split('"""', 2)[2]
    assert "llm" not in body
    assert "get_client" not in body


def test_analytics_runs_with_every_provider_rigged_to_explode(run, monkeypatch):
    """The stronger form: not just no import, but no call, even indirectly."""
    import sentinelops.llm as llm_module

    def explode(*args, **kwargs):
        raise AssertionError("analytics must never call a model")

    monkeypatch.setattr(llm_module, "get_client", explode)
    result = analytics.portfolio(run, AS_OF, window=WINDOW)
    assert result["open_vs_closed"]["total"] > 0


def test_analytics_spends_nothing(run):
    before = run.execute("SELECT COUNT(*) c FROM token_usage").fetchone()["c"]
    analytics.portfolio(run, AS_OF, window=WINDOW)
    after = run.execute("SELECT COUNT(*) c FROM token_usage").fetchone()["c"]
    assert after == before


# --- each line of section 8 --------------------------------------------------

def test_open_versus_closed_counts_and_percentages(portfolio):
    conn, result = portfolio
    figures = result["open_vs_closed"]
    findings = repositories(conn)["findings"].list()

    assert figures["total"] == len(findings)
    assert figures["open"] + figures["closed"] == figures["total"]
    assert 0 <= figures["closed_pct"] <= 100
    assert figures["by_unit"], "per unit, not only overall"
    for row in figures["by_unit"].values():
        assert row["open"] + row["closed"] == row["total"]
        assert 0 <= row["closed_pct"] <= 100
    assert sum(r["total"] for r in figures["by_unit"].values()) == figures["total"]


def test_severity_mix_overall_and_per_unit(portfolio):
    _, result = portfolio
    mix = result["severity_mix"]
    assert set(mix["overall"]) >= {"Major", "Minor", "Observation"}
    assert sum(mix["overall"].values()) == result["open_vs_closed"]["total"]
    assert mix["by_unit"]
    for row in mix["by_unit"].values():
        assert set(row) >= {"Major", "Minor", "Observation"}


def test_overdue_findings_are_aged_into_section_eights_buckets(portfolio):
    _, result = portfolio
    ageing = result["overdue_ageing"]
    assert list(ageing["buckets"]) == ["0-30", "31-60", "61-90", "90+"]
    assert ageing["total"] == sum(ageing["buckets"].values())
    assert ageing["total"] == sum(len(v) for v in ageing["findings"].values())
    assert ageing["total"] > 0, "the corpus leaves findings open on purpose"
    assert ageing["oldest_days"] >= 0


def test_findings_by_unit_category_and_audit_kind(portfolio):
    _, result = portfolio
    dims = result["by_dimension"]
    total = result["open_vs_closed"]["total"]
    assert sum(dims["by_unit"].values()) == total
    assert sum(dims["by_category"].values()) == total
    assert sum(dims["by_audit_kind"].values()) == total
    # both tracks are represented, and all four audit kinds appear
    assert "compliance_activity" in dims["by_audit_kind"]
    assert {"internal_audit", "qarev", "release_audit", "document_review"} <= set(
        dims["by_audit_kind"]
    )
    assert "unclassified" not in dims["by_category"], (
        "every finding was classified before the analytics ran"
    )


def test_recurrence_is_reported_as_links_not_a_connected_graph(portfolio):
    """A→B and B→C are two recurrences, not one incident involving three.

    This test previously demanded transitive sets, and on this corpus that
    produced a single "set" of forty-five findings across ten units — which is
    the union-find algorithm reporting that the graph is connected, not
    something a compliance team can act on. Links plus a per-category rollup say
    the useful version of the same fact.
    """
    conn, result = portfolio
    recurring = result["recurring"]
    repo = repositories(conn)

    assert recurring["count"] >= 1
    assert recurring["spanning_units"] >= 1, (
        "section 10 plants gaps that recur across units on purpose"
    )
    for link in recurring["links"]:
        finding = repo["findings"].get(link["finding"])
        prior = repo["findings"].get(link["prior"])
        assert finding is not None and prior is not None
        assert prior.raised_at < finding.raised_at, "recurrence points backwards"
        assert prior.gap_category == finding.gap_category
        assert link["spans_units"] == (
            prior.auditable_unit_id != finding.auditable_unit_id
        )

    rollup = recurring["by_category"]
    assert sum(row["links"] for row in rollup.values()) == recurring["count"]
    for row in rollup.values():
        assert row["units"] >= 1
        assert row["max_months_apart"] >= 0


def test_no_chain_is_a_prefix_of_another(portfolio):
    """Otherwise the same story is reported three times at three lengths."""
    _, result = portfolio
    chains = result["recurring"]["longest_chains"]
    for index, chain in enumerate(chains):
        for other in chains[index + 1:]:
            assert not set(other["findings"]) <= set(chain["findings"])


def test_chains_are_ordered_oldest_first_and_share_a_category(portfolio):
    conn, result = portfolio
    repo = repositories(conn)
    for chain in result["recurring"]["longest_chains"]:
        assert len(chain["findings"]) >= 3
        members = [repo["findings"].get(i) for i in chain["findings"]]
        assert members == sorted(members, key=lambda m: m.raised_at)
        assert len({m.gap_category for m in members}) == 1


def test_effort_distribution_separates_rounds_from_reminders(portfolio):
    """Two different kinds of effort, and section 8 asks for both."""
    _, result = portfolio
    effort = result["effort"]
    total = result["open_vs_closed"]["total"]
    assert sum(effort["rounds"].values()) == total
    assert sum(effort["reminders"].values()) == total
    assert effort["multi_round"] >= 1, "the corpus plants fixes that fail once"
    assert effort["worst_rounds"] >= 3, "section 10 asks for 3+ round findings"
    assert effort["multi_reminder"] >= 1


def test_the_trend_is_a_real_replay_not_todays_state_projected_back(portfolio):
    """Computed from raise and close dates, so it says what was true then."""
    _, result = portfolio
    trend = result["trend"]
    months = (SIMULATED_TODAY.year - 2026) * 12 + SIMULATED_TODAY.month
    assert len(trend) == months, "January 2026 to the vantage point inclusive"
    assert trend[0]["month"] == "2026-01"
    assert trend[-1]["month"] == f"{SIMULATED_TODAY:%Y-%m}"

    for point in trend:
        assert point["open"] == point["raised_to_date"] - point["closed_to_date"]
        assert point["open"] >= 0
    # monotonic cumulative counts — a finding cannot be un-raised
    raised = [p["raised_to_date"] for p in trend]
    assert raised == sorted(raised)
    closed = [p["closed_to_date"] for p in trend]
    assert closed == sorted(closed)
    # and the line moves, or it is not a trend
    assert len({p["open"] for p in trend}) > 3
    assert trend[-1]["open"] == result["open_vs_closed"]["open"]


def test_closure_performance_by_severity(portfolio):
    _, result = portfolio
    closure = result["closure"]
    assert "overall" in closure
    assert closure["overall"]["closed"] > 0
    assert closure["overall"]["mean_days"] is not None
    assert closure["overall"]["median_days"] is not None
    for severity in ("Major", "Minor", "Observation"):
        if severity not in closure:
            continue
        row = closure[severity]
        assert row["closed"] > 0
        assert row["mean_days"] >= 0
        assert row["slowest_days"] >= row["median_days"]
    counted = sum(
        v["closed"] for k, v in closure.items() if k != "overall"
    )
    assert counted == closure["overall"]["closed"]


def test_upcoming_covers_the_next_thirty_days_only(portfolio):
    _, result = portfolio
    upcoming = result["upcoming"]
    assert upcoming["horizon_days"] == 30
    for audit in upcoming["audits"]:
        assert 0 <= audit["days_away"] <= 30
        assert audit["scope"]
    for activity in upcoming["activities"]:
        assert 0 <= activity["days_away"] <= 30
    assert upcoming["audits"], (
        "the corpus keeps one audit planned but not conducted, so the panel "
        "has something genuinely upcoming to show"
    )


# --- stability ---------------------------------------------------------------

def test_the_same_state_gives_the_same_numbers_twice(run):
    first = analytics.portfolio(run, AS_OF, window=WINDOW)
    second = analytics.portfolio(run, AS_OF, window=WINDOW)
    assert first == second


def test_an_empty_database_does_not_crash(conn):
    result = analytics.portfolio(conn, AS_OF, window=WINDOW)
    assert result["open_vs_closed"]["total"] == 0
    assert result["recurring"]["count"] == 0
    assert result["closure"]["overall"]["mean_days"] is None
    assert result["overdue_ageing"]["total"] == 0
