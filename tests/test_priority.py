"""The priority score: five named inputs, stated weights, checkable arithmetic.

The brief interprets this ranking and must never produce it, so the ranking has
to be something a person can read, recompute and argue with. These tests pin the
formula to its documentation rather than to a set of numbers.
"""

import ast
from datetime import timedelta
from pathlib import Path
from types import SimpleNamespace

import pytest

from sentinelops import priority
from sentinelops.directory import load as load_directory
from sentinelops.repositories import repositories
from sentinelops.synth import generate_corpus, seed_database
from sentinelops.synth.calendar import SIMULATED_TODAY

SRC = Path(__file__).resolve().parents[1] / "src" / "sentinelops"
AS_OF = SIMULATED_TODAY


def _finding(severity="Minor", suggested=None, days_past=0, follow_ups=0):
    return SimpleNamespace(
        id="FND-T", severity=severity, suggested_severity=suggested,
        target_date=AS_OF - timedelta(days=days_past), follow_up_count=follow_ups,
    )


def _score(criticality="medium", links=0, **finding):
    return priority.score(
        _finding(**finding), criticality=criticality, recurrence_links=links,
        as_of=AS_OF,
    )["score"]


@pytest.fixture(scope="module")
def corpus():
    return generate_corpus()


@pytest.fixture
def seeded(conn, corpus):
    seed_database(conn, corpus)
    return conn


@pytest.fixture
def ranked(seeded):
    return priority.rank(repositories(seeded), load_directory(seeded), AS_OF)


# --- the formula is the documentation -------------------------------------------

def test_the_formula_prints_all_five_inputs_and_their_weights():
    table = priority.formula_table()
    for term in ("severity", "criticality", "timing", "recurrence", "follow-ups"):
        assert term in table
    for name, points in priority.SEVERITY_POINTS.items():
        assert f"{name} {points}" in table
    for name, multiplier in priority.CRITICALITY_MULTIPLIER.items():
        assert f"{name} x{multiplier:g}" in table


def test_timing_climbs_to_the_target_and_keeps_climbing_past_it():
    assert priority.timing_points(-45) == 0
    assert priority.timing_points(-30) == 0
    assert priority.timing_points(-10) == 20
    assert priority.timing_points(0) == 30
    assert priority.timing_points(15) == 45
    assert priority.timing_points(400) == 30 + priority.TIMING_DAYS_PAST_CAP


def test_each_input_moves_the_score_the_documented_way():
    assert _score(severity="Major") > _score(severity="Minor") > _score(
        severity="Observation"
    )
    assert _score(criticality="critical") > _score(criticality="high") > _score(
        criticality="medium"
    ) > _score(criticality="low")
    assert _score(days_past=20) > _score(days_past=5) > _score(days_past=-5)
    assert _score(links=5) == _score(links=3) > _score(links=1) > _score(links=0)
    assert _score(follow_ups=15) == _score(follow_ups=10) > _score(
        follow_ups=2
    ) > _score(follow_ups=0)


def test_severity_is_scaled_by_criticality_not_added_to_it():
    worst = priority.score(_finding(severity="Major"), criticality="critical",
                           recurrence_links=0, as_of=AS_OF)
    mildest = priority.score(_finding(severity="Observation"), criticality="low",
                             recurrence_links=0, as_of=AS_OF)
    assert worst["components"]["impact"] == 60
    assert mildest["components"]["impact"] == 7.5


def test_a_suggested_severity_is_used_and_labelled_as_suggested():
    row = priority.score(_finding(severity=None, suggested="Major"),
                         criticality="high", recurrence_links=0, as_of=AS_OF)
    assert row["severity"] == "Major"
    assert row["severity_source"] == "suggested"


def test_nothing_is_defaulted():
    """A missing input is refused, not scored as the mildest case."""
    with pytest.raises(priority.UnscorableFinding):
        priority.score(_finding(severity=None, suggested=None),
                       criticality="high", recurrence_links=0, as_of=AS_OF)
    with pytest.raises(priority.UnscorableFinding):
        priority.score(_finding(), criticality="unrated",
                       recurrence_links=0, as_of=AS_OF)


# --- the ranking is the formula, applied -----------------------------------------

def test_the_ranking_is_the_formula_applied(seeded, ranked):
    repo = repositories(seeded)
    open_ids = {f.id for f in repo["findings"].list() if f.status == "open"}
    assert ranked
    assert {row["id"] for row in ranked} == open_ids
    assert [row["rank"] for row in ranked] == list(range(1, len(ranked) + 1))
    assert [row["score"] for row in ranked] == sorted(
        (row["score"] for row in ranked), reverse=True
    )
    for row in ranked:
        assert round(sum(row["components"].values()), 1) == row["score"]
        assert row["explain"].endswith(f"= {row['score']:g}")


def test_the_same_state_ranks_the_same_way_twice(seeded, ranked):
    again = priority.rank(repositories(seeded), load_directory(seeded), AS_OF)
    assert [(r["id"], r["score"]) for r in again] == [
        (r["id"], r["score"]) for r in ranked
    ]


def test_recurrence_links_count_in_both_directions(seeded):
    repo = repositories(seeded)
    findings = sorted(repo["findings"].list(), key=lambda f: f.raised_at)
    target = next(f for f in findings if f.status == "open")
    earlier = next(f for f in findings if f.id != target.id)
    later = next(f for f in findings if f.id not in (target.id, earlier.id))

    target.recurrence_of = [earlier.id]
    repo["findings"].update(target)
    later.recurrence_of = [target.id]
    repo["findings"].update(later)

    row = next(
        r for r in priority.rank(repo, load_directory(seeded), AS_OF)
        if r["id"] == target.id
    )
    assert row["recurrence_links"] == 2
    assert row["components"]["recurrence"] == 2 * priority.RECURRENCE_POINTS


def test_a_dangling_recurrence_link_is_refused(seeded):
    repo = repositories(seeded)
    target = next(f for f in repo["findings"].list() if f.status == "open")
    target.recurrence_of = ["FND-DOES-NOT-EXIST"]
    repo["findings"].update(target)
    with pytest.raises(priority.UnscorableFinding) as refused:
        priority.rank(repo, load_directory(seeded), AS_OF)
    assert "FND-DOES-NOT-EXIST" in str(refused.value)


# --- never AI ----------------------------------------------------------------------

@pytest.mark.parametrize("module", ["priority.py", "render.py"])
def test_the_score_and_the_renderers_never_reach_a_model(module):
    tree = ast.parse((SRC / module).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        names = []
        if isinstance(node, ast.ImportFrom) and node.module:
            names = [node.module]
        elif isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        for name in names:
            assert "llm" not in name.split("."), f"{module} imports {name}"
