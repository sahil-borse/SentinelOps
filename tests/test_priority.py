"""The priority order: severity bands, stated points, checkable arithmetic.

The brief interprets this ranking and must never produce it, so the ranking has
to be something a person can read, recompute and argue with. These tests pin the
order to its documentation rather than to a set of numbers — and, above all, pin
that lateness cannot swamp severity, which the first version let it do.
"""

import ast
from datetime import date, timedelta
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


def _row(criticality="medium", links=0, name="FND-T", **finding):
    row = priority.score(
        _finding(**finding), criticality=criticality, recurrence_links=links,
        as_of=AS_OF,
    )
    row.update({"id": name, "target_date": (AS_OF - timedelta(
        days=finding.get("days_past", 0))).isoformat()})
    return row


def _score(**kwargs):
    return _row(**kwargs)["score"]


def _worst(severity, days_past=priority.AGEING_PROMOTION_DAYS):
    """Every point a finding of this severity can carry, short of ageing up."""
    return _row(severity=severity, criticality="critical", links=10,
                follow_ups=50, days_past=days_past, name=f"FND-WORST-{severity}")


def _mildest(severity):
    return _row(severity=severity, criticality="low", days_past=-60,
                name=f"FND-MILD-{severity}")


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

def test_the_order_is_one_printable_sentence():
    sentence = priority.FORMULA
    assert sentence.endswith(".") and sentence.count(". ") == 0
    assert priority.formula_table().splitlines()[0] == sentence
    for term in ("severity band", "criticality", "timing", "recurrence",
                 "follow-ups", f"{priority.AGEING_PROMOTION_DAYS} days"):
        assert term in sentence


def test_the_table_prints_every_weight_and_the_threshold():
    table = priority.formula_table()
    for name, points in priority.CRITICALITY_POINTS.items():
        assert f"{name} {points}" in table
    assert " > ".join(priority.SEVERITY_BANDS) in table
    assert f"more than {priority.AGEING_PROMOTION_DAYS} days past target" in table
    assert "one band higher, never more" in table


def test_timing_climbs_to_the_target_and_keeps_climbing_past_it():
    assert priority.timing_points(-45) == 0
    assert priority.timing_points(-30) == 0
    assert priority.timing_points(-10) == 20
    assert priority.timing_points(0) == 30
    assert priority.timing_points(15) == 45
    assert priority.timing_points(400) == 30 + priority.TIMING_DAYS_PAST_CAP


def test_each_input_moves_the_points_the_documented_way():
    assert _score(criticality="critical") > _score(criticality="high") > _score(
        criticality="medium"
    ) > _score(criticality="low")
    assert _score(days_past=20) > _score(days_past=5) > _score(days_past=-5)
    assert _score(links=5) == _score(links=3) > _score(links=1) > _score(links=0)
    assert _score(follow_ups=15) == _score(follow_ups=10) > _score(
        follow_ups=2
    ) > _score(follow_ups=0)


# --- severity gates ---------------------------------------------------------------

def test_no_amount_of_points_lifts_a_finding_past_a_higher_band():
    """Every point there is, a year late to the day, still ranks below the
    mildest finding of the band above."""
    pairs = (("Minor", "Major"), ("Observation", "Minor"), ("Observation", "Major"))
    for lower, higher in pairs:
        worst, mildest = _worst(lower), _mildest(higher)
        assert worst["score"] > mildest["score"], "the points alone would invert them"
        assert priority.order_key(mildest) < priority.order_key(worst), (lower, higher)


def test_the_case_that_exposed_the_old_weights():
    """A long-overdue Observation in a low-criticality unit once outranked a
    Major in a high-criticality unit 48 days late."""
    observation = _row(severity="Observation", criticality="low", days_past=202,
                       name="FND-OBS")
    major = _row(severity="Major", criticality="high", days_past=48, name="FND-MAJ")
    assert priority.order_key(major) < priority.order_key(observation)


def test_ageing_up_starts_after_a_full_year_and_moves_one_band_only():
    limit = priority.AGEING_PROMOTION_DAYS
    assert _row(severity="Minor", days_past=limit)["band"] == "Minor"
    over = _row(severity="Minor", days_past=limit + 1)
    assert over["band"] == "Major" and over["aged_up"]
    assert over["band_label"] == "Major (raised Minor)"
    assert _row(severity="Observation", days_past=2000)["band"] == "Minor", (
        "one band, however old"
    )
    major = _row(severity="Major", days_past=2000)
    assert major["band"] == "Major" and not major["aged_up"]


def test_an_aged_up_finding_competes_on_points_inside_its_new_band():
    aged = _row(severity="Minor", criticality="low", days_past=400, name="FND-AGED")
    busy_major = _worst("Major", days_past=30)
    quiet_major = _mildest("Major")
    minor = _worst("Minor")
    order = sorted([minor, quiet_major, aged, busy_major], key=priority.order_key)
    assert [r["id"] for r in order] == [
        busy_major["id"], aged["id"], quiet_major["id"], minor["id"]
    ]


def test_a_suggested_severity_is_used_and_labelled_as_suggested():
    row = priority.score(_finding(severity=None, suggested="Major"),
                         criticality="high", recurrence_links=0, as_of=AS_OF)
    assert row["severity"] == "Major" == row["band"]
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
    assert ranked == sorted(ranked, key=priority.order_key)
    bands = [priority.SEVERITY_BANDS.index(row["band"]) for row in ranked]
    assert bands == sorted(bands), "a band boundary is never crossed"
    for row in ranked:
        assert sum(row["components"].values()) == row["score"]
        assert row["explain"].endswith(f"= {row['score']:g}")
        assert row["aged_up"] == (row["band"] != row["severity"])
        assert row["aged_up"] == (
            row["days_past_target"] > priority.AGEING_PROMOTION_DAYS
            and row["severity"] != priority.SEVERITY_BANDS[0]
        )


def test_the_same_state_ranks_the_same_way_twice(seeded, ranked):
    again = priority.rank(repositories(seeded), load_directory(seeded), AS_OF)
    assert [(r["id"], r["band"], r["score"]) for r in again] == [
        (r["id"], r["band"], r["score"]) for r in ranked
    ]


def test_listed_metrics_count_only_the_rows_they_are_given(ranked):
    top = ranked[:3]
    listed = priority.listed_metrics(top)
    assert listed["listed_findings"] == 3
    assert sum(v for n, v in listed.items() if n.startswith("listed_in_unit:")) == 3
    assert sum(v for n, v in listed.items() if n.startswith("listed_category:")) == 3
    assert all(n.startswith("listed_") for n in listed)


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
