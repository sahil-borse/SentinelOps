"""Every generated date, placed against the corpus window and the vantage point.

The window, `CORPUS_WINDOW` (2026-01-01 to 2027-06-30), is a window of
**obligation periods**: every scheduled period lies inside it. It is not a
bound on every date, and pretending otherwise would be wrong in two named ways:

  - the last periods close on the window's final day, so their evidence is
    filed, and falls due, in the grace days after it — never past the last due
    date a period inside the window can have;
  - a stale document is old by definition, so its *document* date may precede
    the window, though it is filed inside it.

Everything else — what happened (raised, closed, filed, assessed, notified,
logged) and what is planned (audit dates, target dates, exception expiries) —
lies inside the window, and nothing that happened is dated after the vantage
point, `SIMULATED_TODAY` (2027-04-15), which lies inside the window too.

The vantage point was 2027-09-30 in slice 10, after the window; slice 11 moved
it inside. A date that drifts outside these rules is how the evidence filed
before its obligation existed went unnoticed until slice 15z.

Every date-valued column the run writes must be classified below. A new one that
is not fails the test rather than going unchecked.
"""

from __future__ import annotations

import re
from datetime import date

import pytest

from evaluation import harness
from evaluation.metrics import load_ground_truth
from sentinelops import window as schedule_window
from sentinelops.db import connect
from sentinelops.periods import due_date, period_from_label, periods_in
from sentinelops.synth import generate_corpus
from sentinelops.synth.calendar import CORPUS_WINDOW as WINDOW
from sentinelops.synth.calendar import SIMULATED_TODAY as VANTAGE

ISO = re.compile(r"^\d{4}-\d{2}-\d{2}([ T]\d{2}:\d{2}(:\d{2}(\.\d+)?)?)?$")

#: Things that happened: inside the window, and not after the vantage point.
HAPPENED = {
    "assessments.assessed_at",
    "audit_events.ts",
    "audit_events.entity_id",  # a cycle's own date, used as its id
    "compliance_exceptions.granted_at",
    "evidence.submitted_at",
    "evidence_submissions.submitted_at",
    "evidence_submissions.responded_at",
    "findings.raised_at",
    "findings.closed_at",
    "flags.raised_at",
    "gap_categories.derived_at",
    "notifications.sent_at",
    "scheduled_audits.conducted_date",
}
#: Things planned: inside the window, and may lie after the vantage point.
PLANNED = {
    "compliance_exceptions.expires_at",
    "findings.target_date",
    "scheduled_audits.planned_date",
}
#: May pass the window's end, for a period ending on it, up to its due date.
LAST_PERIODS = {
    "check_instances.due_date",
    "inbound_submissions.submitted_at",
}
#: May precede the window, on stale evidence only; never after the filing.
DOCUMENT_DATES = {
    "evidence.document_date",
    "inbound_submissions.document_date",
}
#: The window itself.
WINDOW_RECORD = {"schedule_window.start_date", "schedule_window.end_date"}
#: The token meter's row stamp is wall-clock, not business time. Section 12's
#: simulated-time rule governs audit events and notifications, which are above.
NOT_BUSINESS_TIME = {"token_usage.ts"}

CLASSIFIED = (HAPPENED | PLANNED | LAST_PERIODS | DOCUMENT_DATES | WINDOW_RECORD
              | NOT_BUSINESS_TIME)


@pytest.fixture(scope="module")
def corpus():
    return generate_corpus()


@pytest.fixture(scope="module")
def run(corpus):
    """The full evaluation run to the vantage point, section 8 included."""
    conn = connect(":memory:")
    harness.run_pipeline(conn, corpus)
    harness._section_eight(conn)
    yield conn
    conn.close()


@pytest.fixture(scope="module")
def stored(run) -> dict[str, list[tuple[date, str]]]:
    """Every date-valued cell in the database, by table.column, with its row id."""
    found: dict[str, list[tuple[date, str]]] = {}
    tables = [r[0] for r in run.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )]
    for table in tables:
        columns = [r[1] for r in run.execute(f"PRAGMA table_info({table})")]
        key = "id" if "id" in columns else columns[0]
        for row in run.execute(f"SELECT * FROM {table}"):
            for column in columns:
                value = row[column]
                if isinstance(value, str) and ISO.match(value):
                    found.setdefault(f"{table}.{column}", []).append(
                        (date.fromisoformat(value[:10]), str(row[key]))
                    )
    return found


@pytest.fixture(scope="module")
def last_due_date(corpus) -> date:
    """The latest due date any period inside the window can have."""
    return max(
        due_date(period, control.grace_days)
        for control in corpus.controls
        for period in periods_in(control.frequency, WINDOW)
    )


def _outside(cells, low, high):
    return sorted((str(d), ident) for d, ident in cells if not low <= d <= high)


# --- the two reference points --------------------------------------------------

def test_the_vantage_point_lies_inside_the_window():
    assert WINDOW.start <= VANTAGE <= WINDOW.end


def test_the_database_records_the_same_window(run):
    assert schedule_window.load(run) == WINDOW


def test_every_scheduled_period_lies_inside_the_window(run, corpus):
    periods = {row["period"] for row in run.execute("SELECT period FROM check_instances")}
    periods |= {s.period for s in corpus.submissions}
    assert periods
    outside = sorted(p for p in periods if not WINDOW.contains(period_from_label(p)))
    assert not outside, outside


# --- every stored date, by what it is ---------------------------------------------

def test_every_date_the_run_writes_is_classified(stored):
    assert stored, "the scan found no dates at all"
    unclassified = sorted(set(stored) - CLASSIFIED)
    assert not unclassified, (
        f"date columns with no rule: {unclassified}; say where they may fall"
    )


def test_what_happened_happened_inside_the_window_by_the_vantage_point(stored):
    for column in sorted(HAPPENED & set(stored)):
        outside = _outside(stored[column], WINDOW.start, VANTAGE)
        assert not outside, (column, len(outside), outside[-3:])


def test_what_is_planned_is_planned_inside_the_window(stored):
    for column in sorted(PLANNED & set(stored)):
        outside = _outside(stored[column], WINDOW.start, WINDOW.end)
        assert not outside, (column, len(outside), outside[-3:])


def test_only_the_last_periods_fall_due_after_the_window(run, last_due_date):
    assert WINDOW.end < last_due_date
    rows = run.execute("SELECT id, period, due_date FROM check_instances").fetchall()
    for row in rows:
        due = date.fromisoformat(row["due_date"])
        assert WINDOW.start <= due <= last_due_date, (row["id"], due)
        if due > WINDOW.end:
            assert period_from_label(row["period"]).end == WINDOW.end, row["id"]


def test_only_the_last_periods_are_filed_after_the_window(corpus, last_due_date):
    grace = {c.id: c.grace_days for c in corpus.controls}
    after = 0
    for submission in corpus.submissions:
        filed = submission.submitted_at.date()
        assert WINDOW.start <= filed <= last_due_date, (submission.id, filed)
        if filed > WINDOW.end:
            after += 1
            period = period_from_label(submission.period)
            assert period.end == WINDOW.end, (submission.id, submission.period)
            assert filed <= due_date(period, grace[submission.control_id]), submission.id
    assert after, "the last periods' evidence is expected in their grace days"


def test_a_document_older_than_the_window_is_stale_evidence(corpus):
    truth = load_ground_truth(corpus.year)
    kind = {
        (r["control_id"], r["auditable_unit_id"], r["period"], r["is_remediation"]):
            r["defect_kind"]
        for r in truth["rows"]
    }
    early = 0
    for submission in corpus.submissions:
        assert submission.document_date <= submission.submitted_at.date(), (
            f"{submission.id} is dated after it was filed"
        )
        if submission.document_date < WINDOW.start:
            early += 1
            key = (submission.control_id, submission.auditable_unit_id,
                   submission.period, submission.is_remediation)
            assert kind[key] == "stale", (submission.id, kind[key])
    assert early, "the stale documents that predate the window are the ones checked"


def test_stored_document_dates_follow_the_same_rule(stored):
    for column in sorted(DOCUMENT_DATES & set(stored)):
        late = [(str(d), i) for d, i in stored[column] if d > WINDOW.end]
        if column.startswith("evidence."):
            # evidence is only what the run used, all of it filed by the vantage point
            assert not late, (column, late[-3:])


def test_nothing_filed_after_the_vantage_point_was_used(run):
    latest = run.execute("SELECT MAX(submitted_at) m FROM evidence").fetchone()["m"]
    assert date.fromisoformat(latest[:10]) <= VANTAGE
    pending = run.execute(
        "SELECT COUNT(*) c FROM inbound_submissions WHERE submitted_at > ?",
        (VANTAGE.isoformat() + "T23:59:59",),
    ).fetchone()["c"]
    assert pending, "future filings exist in the inbox and are left alone"
