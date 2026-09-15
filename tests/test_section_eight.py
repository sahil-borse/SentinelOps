"""Section 8 against the patterns slice 11 planted.

`tests/test_analytics.py` checks that every figure is internally consistent —
counts add up, buckets are section 8's, nothing calls a model. That is necessary
and not enough: a portfolio can be perfectly consistent and still fail to see
the thing it exists to see. These tests read the truth file and ask whether the
analytics find what the corpus deliberately put there — the recurring gap sets,
and the remediations that took more than one round.

Tests may read the truth file; the package may not. `tests/test_truth_isolation.py`
guards the second half of that sentence.
"""

import json
import re
from datetime import date, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

import pytest

from sentinelops import analytics
from sentinelops.demo import section_eight
from sentinelops.repositories import repositories
from sentinelops.stages.trigger import instance_id
from sentinelops.synth import generate_corpus
from sentinelops.synth.calendar import SIMULATED_TODAY

TRUTH = Path(__file__).resolve().parents[1] / "data" / "truth" / "truth_2026.json"


@pytest.fixture(scope="module")
def truth():
    return json.loads(TRUTH.read_text(encoding="utf-8"))


@pytest.fixture
def replayed(conn, monkeypatch):
    """The corpus at today, replayed exactly as the demo and the harness do it."""
    section_eight.replay(conn)
    return conn


@pytest.fixture
def result(replayed):
    return analytics.portfolio(replayed, SIMULATED_TODAY)


def _planted_series(truth):
    """Remediation series from the truth file: original submission -> planned attempts."""
    rows = {row["submission_id"]: row for row in truth["rows"]}
    series: dict[str, dict] = {}
    for row in truth["rows"]:
        original = row.get("remediates_submission_id")
        if not (row.get("is_remediation") and original):
            continue
        match = re.search(r"attempt \d+ of (\d+)", row.get("note") or "")
        entry = series.setdefault(original, {
            "original": rows[original],
            "planned": int(match.group(1)) if match else 1,
            "filed": 0,
        })
        entry["filed"] += 1
    return series


def _finding_for(repo, row):
    """The activity-track finding raised on a check that was due by the vantage point.

    Returns (finding, ripe). A check is ripe when it was scheduled and its due
    date passed before the vantage point. Unripe checks are set aside by the
    callers and counted, never silently dropped.

    Ripeness matters since slice 15z scheduled 2027. A 2027-Q2 check exists from
    1 April and has seen one cycle by 15 April; the remediation loop takes one
    round per cycle, so a two-attempt series on it has had time for one round.
    That is the calendar, not the analytics failing to see a pattern.
    """
    wanted = instance_id(row["control_id"], row["auditable_unit_id"], row["period"])
    instance = repo["instances"].get(wanted)
    if instance is None or instance.due_date >= SIMULATED_TODAY:
        return None, False
    matches = [f for f in repo["findings"].list() if f.check_instance_id == wanted]
    return (matches[0] if matches else None), True


# --- the multi-round findings slice 11 planted -------------------------------

def test_every_planted_multi_attempt_remediation_is_counted_as_multi_round(
    replayed, result, truth,
):
    """Slice 11 files some fixes that do not work first time. Section 8 must see them.

    Only series whose check was actually scheduled can produce rounds, so series
    on periods the pipeline has not scheduled are set aside and counted rather
    than silently dropped.
    """
    repo = repositories(replayed)
    multi = set(result["effort"]["multi_round_findings"])

    realised, unscheduled = [], []
    for original, entry in _planted_series(truth).items():
        if entry["planned"] < 2 or entry["filed"] < 2:
            continue
        finding, scheduled = _finding_for(repo, entry["original"])
        if not scheduled:
            unscheduled.append(original)
            continue
        assert finding is not None, (
            f"{original} planted a failure with {entry['filed']} remediation "
            f"attempts, but no finding was raised on its check"
        )
        realised.append(finding.id)
        assert finding.id in multi, (
            f"{finding.id} took {entry['filed']} planted attempts and section 8 "
            f"does not count it as needing multiple rounds"
        )

    assert len(realised) >= 10, (
        f"only {len(realised)} planted multi-attempt series were realised; "
        f"{len(unscheduled)} sat on unscheduled periods"
    )


def test_every_three_round_finding_traces_to_a_planted_three_attempt_series(
    replayed, result, truth,
):
    """No invented three-rounders: each one is a failure slice 11 put there.

    The reverse does not hold exactly, and that is measured rather than hidden:
    the stub reads a near-miss as compliant a few per cent of the time, so a
    planted three-attempt series occasionally closes in two. That is the
    assessor's accuracy, scored in `test_fake_accuracy.py`, not the analytics'.
    """
    repo = repositories(replayed)
    planted_three = set()
    for entry in _planted_series(truth).values():
        if entry["planned"] == 3:
            finding, _ = _finding_for(repo, entry["original"])
            if finding is not None:
                planted_three.add(finding.id)

    three_plus = result["effort"]["three_plus_round_findings"]
    assert three_plus, "section 10 asks for several findings needing 3+ rounds"
    assert result["effort"]["worst_rounds"] >= 3
    for finding_id in three_plus:
        assert finding_id in planted_three, (
            f"{finding_id} took three or more rounds without a planted "
            f"three-attempt series behind it"
        )
    assert len(three_plus) >= len(planted_three) - 2, (
        f"{len(planted_three)} planted three-attempt series realised, only "
        f"{len(three_plus)} reached three rounds"
    )


def test_the_distributions_account_for_every_finding(result):
    effort = result["effort"]
    total = result["open_vs_closed"]["total"]
    assert sum(effort["rounds"].values()) == total
    assert sum(effort["reminders"].values()) == total
    assert effort["multi_round"] == len(effort["multi_round_findings"])
    assert set(effort["three_plus_round_findings"]) <= set(
        effort["multi_round_findings"]
    )


# --- the recurring gap sets slice 11 planted ---------------------------------

def test_both_planted_audit_recurrence_groups_are_seen_by_section_eight(
    replayed, result, truth,
):
    """Same gap category, different unit and different period, from state alone.

    A group counts as detected when at least two of its members sit in one
    recurring category that spans units and quarters. Full membership is a
    classification question — whether each description was put in the right
    category — which is section 2 use 1 and is scored in slice 14.
    """
    repo = repositories(replayed)
    categories = result["recurring"]["audit_track"]["categories"]
    assert truth["recurrence_groups"], "the truth file plants recurrence groups"

    for group in truth["recurrence_groups"]:
        members = set(group["finding_ids"])
        best_name, best = None, set()
        for name, row in categories.items():
            overlap = members & set(row["finding_ids"])
            if len(overlap) > len(best):
                best_name, best = name, overlap
        assert len(best) >= 2, (
            f"{group['id']}: no recurring category holds two of "
            f"{sorted(members)}"
        )
        held = [repo["findings"].get(i) for i in best]
        assert len({f.auditable_unit_id for f in held}) >= 2, group["id"]
        assert len({analytics._quarter(f.raised_at.date()) for f in held}) >= 2, (
            group["id"]
        )
        assert categories[best_name]["spans_units"]
        assert categories[best_name]["spans_periods"]


def test_the_access_leavers_group_is_seen_whole(result, truth):
    """Three units, eleven months, two auditors, no shared vocabulary — one category."""
    group = next(
        g for g in truth["recurrence_groups"] if g["id"] == "REC-AUDIT-ACCESS-LEAVERS"
    )
    categories = result["recurring"]["audit_track"]["categories"]
    holding = [
        name for name, row in categories.items()
        if set(group["finding_ids"]) <= set(row["finding_ids"])
    ]
    assert holding, f"no single recurring category holds all of {group['finding_ids']}"
    row = categories[holding[0]]
    assert row["units"] >= 3
    assert row["months_spanned"] >= 10


def test_realised_activity_track_coordinate_sets_recur_together(
    replayed, result, truth,
):
    """The activity-track plants: one control failing in different units and periods."""
    repo = repositories(replayed)
    categories = result["recurring"]["by_gap_category"]["categories"]
    checked = 0
    for coordinate_set in truth["recurrence_coordinate_sets"]:
        found = []
        for coords in coordinate_set["coords"]:
            finding, _ = _finding_for(repo, {
                "control_id": coordinate_set["control_id"], **coords,
            })
            if finding is not None:
                found.append(finding)
        if len(found) < 2:
            continue
        checked += 1
        ids = {f.id for f in found}
        assert any(ids <= set(row["finding_ids"]) for row in categories.values()), (
            f"{coordinate_set['id']}: {sorted(ids)} do not share a recurring category"
        )
    assert checked >= 1, "no planted coordinate set was realised twice"


def test_the_section_eight_figure_does_not_depend_on_the_detectors_links(replayed):
    """Section 8 defines recurrence by category, unit and period. Links are extra.

    Until slice 15 the section 8 number *was* the detector's link count, which
    made it a function of the stub's vocabulary. Clearing every link must now
    leave the section 8 figure exactly where it was.
    """
    before = analytics.portfolio(replayed, SIMULATED_TODAY)["recurring"]
    repo = repositories(replayed)
    for finding in repo["findings"].list():
        if finding.recurrence_of:
            finding.recurrence_of = []
            repo["findings"].update(finding)
    after = analytics.portfolio(replayed, SIMULATED_TODAY)["recurring"]

    assert after["count"] == 0, "the detector's links are gone"
    assert before["count"] > 0
    assert after["by_gap_category"] == before["by_gap_category"]
    assert after["audit_track"] == before["audit_track"]


def _finding(fid, category, unit, raised, source="audit"):
    return SimpleNamespace(
        id=fid, gap_category=category, auditable_unit_id=unit,
        raised_at=datetime.combine(raised, datetime.min.time()), source=source,
    )


def test_recurrence_needs_a_different_unit_or_a_different_period():
    units = {"U1": "One", "U2": "Two"}
    same_place_same_quarter = [
        _finding("A", "cat", "U1", date(2026, 1, 5)),
        _finding("B", "cat", "U1", date(2026, 3, 20)),
    ]
    assert analytics.recurring_categories(same_place_same_quarter, units)["count"] == 0

    other_unit = [
        _finding("A", "cat", "U1", date(2026, 1, 5)),
        _finding("B", "cat", "U2", date(2026, 1, 9)),
    ]
    row = analytics.recurring_categories(other_unit, units)["categories"]["cat"]
    assert row["spans_units"] and not row["spans_periods"]

    other_quarter = [
        _finding("A", "cat", "U1", date(2026, 1, 5)),
        _finding("B", "cat", "U1", date(2026, 4, 1)),
    ]
    row = analytics.recurring_categories(other_quarter, units)["categories"]["cat"]
    assert row["spans_periods"] and not row["spans_units"]

    alone = [_finding("A", "cat", "U1", date(2026, 1, 5))]
    assert analytics.recurring_categories(alone, units)["count"] == 0

    unclassified = [
        _finding("A", "", "U1", date(2026, 1, 5)),
        _finding("B", "", "U2", date(2027, 1, 5)),
    ]
    assert analytics.recurring_categories(unclassified, units)["count"] == 0


# --- the trend and its verdict ------------------------------------------------

def _points(values):
    return [{"month": f"2026-{i + 1:02d}", "open": v} for i, v in enumerate(values)]


def test_a_steady_climb_is_rising_and_a_steady_fall_is_falling():
    assert analytics.trend_verdict(_points([2, 4, 6, 8, 10, 12]))["direction"] == "rising"
    assert analytics.trend_verdict(_points([12, 10, 8, 6, 4, 2]))["direction"] == "falling"


def test_one_spiky_month_does_not_make_a_trend():
    """First-against-last would call this whatever the last month happened to be."""
    verdict = analytics.trend_verdict(_points([10, 10, 10, 30, 10, 10, 10]))
    assert verdict["direction"] == "flat"
    assert verdict["peak"] == {"month": "2026-04", "open": 30}


def test_the_two_reads_can_disagree_and_both_are_reported():
    """Up across the window, down this quarter — reporting one would be choosing.

    Last quarter averages 14.7 against 23.3 the quarter before, while the fitted
    line over all ten months still climbs about 1.5 a month.
    """
    verdict = analytics.trend_verdict(
        _points([2, 5, 8, 11, 20, 24, 26, 18, 14, 12])
    )
    assert verdict["direction"] == "rising"
    assert verdict["slope_per_month"] > 1
    assert verdict["recent"]["direction"] == "falling"
    assert verdict["recent"]["change"] < -5


def test_a_small_quarter_on_quarter_move_is_flat():
    """18.7 against 18.3 is noise at this scale, and the rule says so."""
    verdict = analytics.trend_verdict(_points([2, 5, 8, 11, 20, 24, 22, 18, 16]))
    assert verdict["recent"]["direction"] == "flat"
    assert abs(verdict["recent"]["change"]) < analytics.RECENT_FLAT_BAND


def test_too_little_history_says_so():
    assert (
        analytics.trend_verdict(_points([5]))["direction"] == "insufficient_history"
    )
    short = analytics.trend_verdict(_points([1, 2, 3]))
    assert short["direction"] == "rising"
    assert short["recent"]["direction"] == "insufficient_history"


def test_the_corpus_trend_covers_the_window_and_carries_a_verdict(result):
    trend = result["trend"]
    start, end = result["window"]
    assert start == date(2026, 1, 1), "read from the first finding, not assumed"
    assert end == SIMULATED_TODAY
    assert trend[0]["month"] == "2026-01"
    assert trend[-1]["month"] == f"{SIMULATED_TODAY:%Y-%m}"
    assert trend[-1]["as_of"] == SIMULATED_TODAY.isoformat(), (
        "today is mid-month; the rest of the month has not happened"
    )
    assert trend[-1]["open"] == result["open_vs_closed"]["open"]

    verdict = result["trend_verdict"]
    assert verdict["direction"] in {"rising", "falling", "flat"}
    assert verdict["slope_per_month"] == round(
        analytics._slope([p["open"] for p in trend]), 2
    )
    assert verdict["recent"]["direction"] in {"rising", "falling", "flat"}


# --- the smaller lines --------------------------------------------------------

def test_open_and_closed_percentages_add_up(result):
    ovc = result["open_vs_closed"]
    assert abs(ovc["open_pct"] + ovc["closed_pct"] - 100) <= 0.1
    for row in ovc["by_unit"].values():
        assert abs(row["open_pct"] + row["closed_pct"] - 100) <= 0.1


def test_the_default_window_is_read_from_state(conn):
    """No findings, no history: the window is today's month and nothing breaks."""
    result = analytics.portfolio(conn, SIMULATED_TODAY)
    assert result["window"] == (date(2027, 4, 1), SIMULATED_TODAY)
    assert result["trend_verdict"]["direction"] == "insufficient_history"


# --- the deliverable ----------------------------------------------------------

def test_the_printed_metric_set_shows_every_line_of_section_eight(capsys):
    """`python -m sentinelops.demo.section_eight`, run so it cannot rot."""
    section_eight.main()
    out = capsys.readouterr().out

    for heading in (
        "1. OPEN VS CLOSED - COUNT AND PERCENTAGE, OVERALL AND PER UNIT",
        "2. SEVERITY MIX - PER UNIT",
        "3. OVERDUE, AGED - DAYS PAST TARGET",
        "4. FINDINGS BY UNIT, BY GAP CATEGORY, BY AUDIT KIND",
        "5. RECURRING - SAME GAP CATEGORY, DIFFERENT UNIT OR PERIOD",
        "6. MULTIPLE EVIDENCE ROUNDS OR MULTIPLE REMINDERS - DISTRIBUTIONS",
        "7. OPEN FINDINGS BY MONTH - AND WHICH WAY IT IS GOING",
        "8. CLOSURE PERFORMANCE - DAYS FROM RAISE TO CLOSURE, BY SEVERITY",
        "9. DUE IN THE NEXT 30 DAYS",
    ):
        assert heading in out, heading

    for bucket in ("0-30 days", "31-60 days", "61-90 days", "90+ days"):
        assert bucket in out
    assert "across the window: " in out and "last quarter: " in out
    assert "three or more rounds: FND-" in out
    assert "audit track (auditors' own words)" in out
    assert "model calls during the analytics: 0" in out
    assert "ok=True" in out

    stamps = re.findall(r"^\s+(20\d\d-\d\d)\s+\d+\s", out, re.MULTILINE)
    assert stamps and all(s.startswith(("2026-", "2027-")) for s in stamps)
