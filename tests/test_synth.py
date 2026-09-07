"""The corpus must be reproducible, varied, and honest about what it injected."""

import json
from collections import Counter
from datetime import timedelta
from random import Random

import pytest

from sentinelops.entities import InboundSubmission
from sentinelops.synth import (
    COMPLIANCE_EXCEPTIONS,
    CONTROL_SPECS,
    AUDITABLE_UNITS,
    STRUCTURED_CONTROL_IDS,
    generate_corpus,
    periods_for,
    seed_database,
    truth_payload,
)
from sentinelops.synth.controls import SPECS_BY_ID
from sentinelops.synth.documents import _clause_states
from sentinelops.synth.generate import CONSISTENCY_PAIR, applies


@pytest.fixture(scope="module")
def corpus():
    return generate_corpus()


# --- reproducibility -------------------------------------------------------

def test_same_seed_produces_an_identical_corpus():
    a, b = generate_corpus(), generate_corpus()
    assert a.fingerprint() == b.fingerprint()
    assert [s.content for s in a.submissions] == [s.content for s in b.submissions]
    assert a.truth_rows == b.truth_rows


def test_a_different_seed_produces_a_different_corpus():
    assert generate_corpus(seed=1).fingerprint() != generate_corpus(seed=2).fingerprint()


def test_the_generator_never_reads_the_clock():
    """Wall-clock time in a seeded generator would break reproducibility."""
    import inspect

    from sentinelops.synth import generate

    source = inspect.getsource(generate)
    assert "datetime.now" not in source
    assert "date.today" not in source


# --- shape, per section 7 --------------------------------------------------

def test_unit_roster_matches_section_ten(corpus):
    """Six support functions plus three project teams, and two departments.

    The roster the stakeholder described, exactly: IT, Admin, Purchase, HR,
    Finance and Facilities, plus four project teams. The two `department` units
    an earlier version carried are gone — they were ours, not theirs, and a
    corpus that quietly adds units the stakeholder did not name is describing a
    different organisation.
    """
    from collections import Counter

    kinds = Counter(u.kind for u in corpus.areas)
    assert kinds["support_function"] == 6
    assert kinds["project_team"] == 4
    assert len(corpus.areas) == 10
    assert {u.name for u in corpus.areas if u.kind == "support_function"} == {
        "IT", "Admin", "Purchase", "HR", "Finance", "Facilities"
    }


def test_area_count_and_varied_attributes(corpus):
    assert 9 <= len(corpus.areas) <= 11
    for attribute in ("handles_pii", "customer_facing", "has_suppliers"):
        values = {a.attributes[attribute] for a in corpus.areas}
        assert values == {True, False}, f"{attribute} does not vary"
    assert len({a.attributes["region"] for a in corpus.areas}) >= 3
    assert len({a.attributes["criticality"] for a in corpus.areas}) >= 3
    assert all(a.owner_identity and a.kind for a in corpus.areas)


def test_control_count_and_frequency_spread(corpus):
    assert 12 <= len(corpus.controls) <= 15
    frequencies = Counter(c.frequency for c in corpus.controls)
    assert set(frequencies) == {"monthly", "quarterly", "annual"}
    assert all(count >= 3 for count in frequencies.values())


def test_at_least_three_controls_take_structured_evidence(corpus):
    structured = [c for c in corpus.controls if c.evidence_kind == "structured"]
    assert len(structured) >= 3
    assert all(c.thresholds for c in structured), "a structured control needs a threshold"
    assert set(STRUCTURED_CONTROL_IDS) == {c.id for c in structured}


def test_the_calendar_covers_twelve_months():
    assert len(periods_for("monthly", 2026)) == 12
    assert len(periods_for("quarterly", 2026)) == 4
    assert len(periods_for("annual", 2026)) == 1
    assert periods_for("monthly", 2026)[0].start.isoformat() == "2026-01-01"
    assert periods_for("monthly", 2026)[-1].end.isoformat() == "2026-12-31"


def test_areas_receive_genuinely_different_control_sets(corpus):
    by_area: dict[str, set[str]] = {a.id: set() for a in corpus.areas}
    for control_id, area_id in corpus.applicable_pairs:
        by_area[area_id].add(control_id)

    # Every unit is in scope for something and the sets differ in size as well
    # as membership. AREA-IT legitimately draws all fourteen — it handles
    # PII, faces customers, uses suppliers and is business-critical — so "nobody
    # gets everything" is not the property to assert.
    #
    # Nor is "everybody gets something different": Purchase and Facilities share
    # a risk profile and therefore share their obligations, which is the rules
    # engine being right rather than lazy. See
    # `test_units_that_share_a_profile_share_a_set`.
    # Seven distinct sets across ten units, ranging from seven controls to all
    # fourteen. IT and HR owe the same set, and so do Purchase, Facilities and
    # Beacon — in each case because they genuinely share a risk profile, and an
    # engine that invented a difference would be wrong. What has to hold is that
    # applicability is doing real work, not that every unit is a snowflake.
    assert all(len(s) > 0 for s in by_area.values())
    sets = [frozenset(s) for s in by_area.values()]
    assert len(set(sets)) >= 6, "the sets have collapsed"
    assert len({len(s) for s in sets}) >= 4
    assert max(len(s) for s in sets) - min(len(s) for s in sets) >= 5
    assert by_area["AREA-FINANCE"] != by_area["AREA-PURCHASE"]
    assert by_area["AREA-IT"] > by_area["AREA-FACILITIES"]

    # a unit that handles personal data owes the PII controls; one that does
    # not, does not — and the same for suppliers, on a different pair of units,
    # because IT happens to have both.
    assert "CTRL-ACCESS-REVIEW" in by_area["AREA-IT"]
    assert "CTRL-ACCESS-REVIEW" not in by_area["AREA-PURCHASE"]
    assert "CTRL-VENDOR-DD" in by_area["AREA-PURCHASE"]
    assert "CTRL-VENDOR-DD" not in by_area["AREA-FINANCE"]


def test_applicability_matches_every_generated_pair(corpus):
    """Slice 3's S0 engine must reproduce exactly these pairings."""
    areas = {a.id: a for a in AUDITABLE_UNITS}
    for control_id, area_id in corpus.applicable_pairs:
        spec = SPECS_BY_ID[control_id]
        assert applies(spec.applies_when, areas[area_id].attributes)
    for submission in corpus.submissions:
        assert (submission.control_id, submission.auditable_unit_id) in set(
            corpus.applicable_pairs
        )


# --- evidence quality ------------------------------------------------------

def test_every_quality_is_present(corpus):
    kinds = Counter(row["defect_kind"] for row in corpus.truth_rows)
    for quality in (
        "compliant",
        "near_miss",
        "partial",
        "non_compliant",
        "stale",
        "wrong_type",
        "missing",
        "remediation",
        "exception_suppressed",
        "adversarial",
    ):
        assert kinds[quality] > 0, f"no {quality} evidence in the corpus"


def test_most_of_the_corpus_is_clean(corpus):
    """A corpus that is mostly broken flatters the precision figure."""
    kinds = Counter(row["defect_kind"] for row in corpus.truth_rows)
    assert kinds["compliant"] / len(corpus.truth_rows) > 0.4


@pytest.mark.parametrize("spec", CONTROL_SPECS, ids=lambda s: s.id)
def test_near_miss_fails_exactly_one_clause(spec):
    for seed in range(12):
        states, failing = _clause_states(spec, "near_miss", Random(seed))
        assert states.count("unmet") == 1
        assert states.count("hedged") == 0
        assert states[failing] == "unmet"


@pytest.mark.parametrize("spec", CONTROL_SPECS, ids=lambda s: s.id)
def test_a_near_miss_never_contradicts_itself(spec):
    """The failing clause must be a scoped failure, not "nothing happened".

    A document claiming no review took place while two other clauses describe
    that review in detail is incoherent, and a model is right to be confused by
    it. Near-misses draw only from clauses marked narrow.
    """
    for seed in range(12):
        _, failing = _clause_states(spec, "near_miss", Random(seed))
        assert spec.clauses[failing].narrow


def test_every_control_has_at_least_one_near_miss_candidate():
    for spec in CONTROL_SPECS:
        assert any(c.narrow for c in spec.clauses), spec.id


@pytest.mark.parametrize("spec", CONTROL_SPECS, ids=lambda s: s.id)
def test_partial_hedges_one_clause_and_fails_none(spec):
    for seed in range(12):
        states, _ = _clause_states(spec, "partial", Random(seed))
        assert states.count("hedged") == 1
        assert states.count("unmet") == 0


@pytest.mark.parametrize("spec", CONTROL_SPECS, ids=lambda s: s.id)
def test_non_compliant_fails_more_than_one_clause(spec):
    for seed in range(12):
        states, _ = _clause_states(spec, "non_compliant", Random(seed))
        assert states.count("unmet") >= 2


def test_near_miss_rows_name_the_clause_that_fails(corpus):
    controls = {c.id: c for c in corpus.controls}
    rows = [r for r in corpus.truth_rows if r["defect_kind"] == "near_miss"]
    assert rows
    for row in rows:
        index = row["failing_clause_index"]
        assert index is not None and 1 <= index <= 3
        clause_texts = SPECS_BY_ID[row["control_id"]].clauses
        assert row["failing_clause_text"] == clause_texts[index - 1].text
        assert row["failing_clause_text"] in controls[row["control_id"]].criteria_text
        assert row["expected_verdict"] == "gap"


def test_structured_near_miss_breaches_exactly_one_threshold(corpus):
    rows = [
        r
        for r in corpus.truth_rows
        if r["defect_kind"] == "near_miss"
        and r["control_id"] in STRUCTURED_CONTROL_IDS
    ]
    assert rows
    by_id = {s.id: s for s in corpus.submissions}
    for row in rows:
        metrics = json.loads(by_id[row["submission_id"]].content)
        thresholds = SPECS_BY_ID[row["control_id"]].thresholds
        breached = [
            name
            for name, rule in thresholds.items()
            if ("min" in rule and metrics[name] < rule["min"])
            or ("max" in rule and metrics[name] > rule["max"])
        ]
        assert len(breached) == 1, f"{row['submission_id']} breached {breached}"


def test_structured_evidence_is_a_parsable_metrics_table(corpus):
    structured = [s for s in corpus.submissions if s.kind == "structured"]
    assert structured
    for submission in structured:
        metrics = json.loads(submission.content)
        assert set(SPECS_BY_ID[submission.control_id].thresholds) <= set(metrics)


def test_wrong_type_evidence_carries_a_doc_type_the_control_rejects(corpus):
    rows = [r for r in corpus.truth_rows if r["defect_kind"] == "wrong_type"]
    by_id = {s.id: s for s in corpus.submissions}
    controls = {c.id: c for c in corpus.controls}
    assert rows
    for row in rows:
        submission = by_id[row["submission_id"]]
        accepted = controls[row["control_id"]].required_evidence_types
        assert submission.doc_type not in accepted
        assert row["expected_verdict"] == "insufficient_evidence"


def test_stale_evidence_predates_its_freshness_window(corpus):
    rows = [r for r in corpus.truth_rows if r["defect_kind"] == "stale"]
    by_id = {s.id: s for s in corpus.submissions}
    assert rows
    for row in rows:
        spec = SPECS_BY_ID[row["control_id"]]
        period = next(
            p for p in periods_for(
                spec.frequency, corpus.year, corpus.through,
                last_month=corpus.last_month,
            )
            if p.label == row["period"]
        )
        age = (period.end - by_id[row["submission_id"]].submitted_at.date()).days
        assert age > spec.freshness_days


def test_missing_evidence_has_no_submission(corpus):
    submitted = {
        (s.control_id, s.auditable_unit_id, s.period) for s in corpus.submissions
    }
    for row in corpus.truth_rows:
        if row["defect_kind"] == "missing":
            assert row["submission_id"] is None
            assert (row["control_id"], row["auditable_unit_id"], row["period"]) not in submitted


# --- the consistency pair --------------------------------------------------

def test_the_same_evidence_is_filed_in_two_areas(corpus):
    # Original filings only. A remediation for either half is a *different*
    # document filed later, and counting it here would turn a test about one
    # document reaching two units into a test about how many documents exist.
    paired = [
        s
        for s in corpus.submissions
        if s.control_id == CONSISTENCY_PAIR["control_id"]
        and s.period == CONSISTENCY_PAIR["period"]
        and s.auditable_unit_id in CONSISTENCY_PAIR["area_ids"]
        and not s.is_remediation
    ]
    assert len(paired) == 2
    assert paired[0].auditable_unit_id != paired[1].auditable_unit_id
    assert paired[0].content == paired[1].content
    assert paired[0].content_hash == paired[1].content_hash


def test_the_consistency_pair_is_recorded_in_the_truth_file(corpus):
    rows = [r for r in corpus.truth_rows if r["consistency_pair_id"]]
    assert len(rows) == 2
    assert {r["expected_verdict"] for r in rows} == {"gap"}
    assert len({r["failing_clause_index"] for r in rows}) == 1


# --- exceptions ------------------------------------------------------------

def test_four_exceptions_covering_every_path(corpus):
    assert len(corpus.exceptions) == 4
    assert {e.status for e in corpus.exceptions} == {"active", "revoked"}
    by_id = {e.id: e for e in corpus.exceptions}

    # EXC-002 is the lapse that returns a control to the schedule mid-year.
    assert by_id["EXC-002"].expires_at.isoformat() == "2026-06-30"
    assert by_id["EXC-002"].status == "active"
    # EXC-003 was withdrawn rather than served out.
    assert by_id["EXC-003"].status == "revoked"


def test_every_exception_is_fully_documented(corpus):
    for exception in corpus.exceptions:
        assert exception.approved_by
        assert len(exception.rationale) > 40
        assert exception.granted_at < exception.expires_at


def test_the_fourth_exception_arrives_after_its_obligation_is_overdue(corpus):
    """EXC-004 waives rather than suppresses, so it must miss every period end."""
    exception = next(e for e in corpus.exceptions if e.id == "EXC-004")
    assert exception.control_id == "CTRL-ACCESS-REVIEW"
    assert exception.auditable_unit_id == "AREA-ADMIN"
    assert exception.granted_at.isoformat() == "2026-05-11"
    assert exception.expires_at.isoformat() == "2026-06-19"

    spec = SPECS_BY_ID[exception.control_id]
    # granted after 2026-Q1 fell due (31 Mar close + 15 days grace = 15 Apr)
    q1 = next(p for p in periods_for(spec.frequency, 2026) if p.label == "2026-Q1")
    assert exception.granted_at > q1.end + timedelta(days=spec.grace_days)
    # and its window contains no period end, so it cannot suppress anything
    for period in periods_for(spec.frequency, 2026):
        assert not (exception.granted_at <= period.end <= exception.expires_at)


def test_the_fourth_exception_leaves_the_corpus_untouched(corpus):
    """Adding it must move no evidence and suppress no period."""
    suppressed = [
        r for r in corpus.truth_rows if r["defect_kind"] == "exception_suppressed"
    ]
    assert len(suppressed) == 3
    assert {r["control_id"] for r in suppressed} == {
        "CTRL-BCP-TEST", "CTRL-CONTROLLED-DOCS"
    }
    # Section 10's eighteen-month window over eleven units. Pinned rather than
    # bounded because this test's whole job is "adding EXC-004 changed nothing
    # else" — a range would let a drift of a dozen submissions through.
    assert len(corpus.submissions) == 795
    assert len(corpus.truth_rows) == 803

    # the obligation it waives is genuinely unevidenced
    filed = {(s.control_id, s.auditable_unit_id, s.period) for s in corpus.submissions}
    assert ("CTRL-ACCESS-REVIEW", "AREA-ADMIN", "2026-Q1") not in filed


def test_an_active_exception_suppresses_its_periods_and_the_lapse_restores_them(corpus):
    suppressed = {
        (r["control_id"], r["auditable_unit_id"], r["period"])
        for r in corpus.truth_rows
        if r["defect_kind"] == "exception_suppressed"
    }
    assert ("CTRL-CONTROLLED-DOCS", "AREA-FACILITIES", "2026-Q1") in suppressed
    assert ("CTRL-CONTROLLED-DOCS", "AREA-FACILITIES", "2026-Q2") in suppressed
    assert ("CTRL-CONTROLLED-DOCS", "AREA-FACILITIES", "2026-Q3") not in suppressed

    filed = {
        (s.control_id, s.auditable_unit_id, s.period) for s in corpus.submissions
    }
    assert ("CTRL-CONTROLLED-DOCS", "AREA-FACILITIES", "2026-Q1") not in filed
    assert ("CTRL-CONTROLLED-DOCS", "AREA-FACILITIES", "2026-Q3") in filed


def test_a_revoked_exception_suppresses_nothing(corpus):
    revoked = next(e for e in corpus.exceptions if e.status == "revoked")
    filed = {(s.control_id, s.auditable_unit_id) for s in corpus.submissions}
    assert (revoked.control_id, revoked.auditable_unit_id) in filed


# --- remediation -----------------------------------------------------------

def test_remediation_evidence_answers_a_real_gap(corpus):
    by_id = {s.id: s for s in corpus.submissions}
    rows = [r for r in corpus.truth_rows if r["defect_kind"] == "remediation"]
    assert len(rows) >= 3
    for row in rows:
        remediation = by_id[row["submission_id"]]
        original = by_id[row["remediates_submission_id"]]
        assert remediation.is_remediation is True
        assert original.is_remediation is False
        assert remediation.submitted_at > original.submitted_at
        assert (remediation.control_id, remediation.auditable_unit_id, remediation.period) == (
            original.control_id,
            original.auditable_unit_id,
            original.period,
        )
        # Not every remediation works first time. Section 10 asks for findings
        # needing three or more rounds, which means the corpus has to contain
        # fixes that did not fix it — so the assertion is that a remediation is
        # a genuine later attempt at the same obligation, not that it succeeds.
        assert row["expected_verdict"] in (
            "compliant", "gap", "partial", "insufficient_evidence"
        )


# --- persistence -----------------------------------------------------------

def test_the_corpus_loads_into_sqlite(conn, corpus):
    seed_database(conn, corpus)
    counts = {
        table: conn.execute(f"SELECT COUNT(*) c FROM {table}").fetchone()["c"]
        for table in (
            "auditable_units",
            "control_definitions",
            "compliance_exceptions",
            "inbound_submissions",
        )
    }
    assert counts["auditable_units"] == len(corpus.areas)
    assert counts["control_definitions"] == len(corpus.controls)
    assert counts["compliance_exceptions"] == len(corpus.exceptions)
    assert counts["inbound_submissions"] == len(corpus.submissions)


def test_seeding_produces_no_pipeline_output(conn, corpus):
    """The generator supplies inputs; the pipeline produces judgements.

    The audit track is the one thing seeded that is not an input, and it is
    deliberate: section 1 makes findings the children of audits, and an audit
    that happened last March is a fact about the past rather than something the
    pipeline discovers. Those findings are still *raised* through
    `stages.audits`, so each has a trail behind it — see the test below.
    """
    seed_database(conn, corpus)
    for table in ("check_instances", "evidence", "assessments"):
        assert conn.execute(f"SELECT COUNT(*) c FROM {table}").fetchone()["c"] == 0


def test_seeding_creates_only_audit_track_findings(conn, corpus):
    from sentinelops.repositories import repositories

    seed_database(conn, corpus)
    repo = repositories(conn)
    findings = repo["findings"].list()
    assert findings, "the corpus carries an audit programme"
    for finding in findings:
        assert finding.source == "audit"
        assert finding.audit_id
        assert finding.check_instance_id is None
        # raised through the stage, so it has a history
        events = repo["audit"].read_for("Finding", finding.id)
        assert events and events[0].action == "finding_raised"
        assert events[0].actor_identity


def test_seeding_spends_nothing(conn, corpus):
    """Seeding a database must never call a model.

    Report drafting is the audit track's one paid step, and it is deliberately
    not done here — a fixture that runs hundreds of times must not carry a bill,
    and S0's own tests seed a corpus, so a spending seed would make "S0 never
    calls a model" impossible to assert.
    """
    seed_database(conn, corpus)
    spent = conn.execute("SELECT COUNT(*) c FROM token_usage").fetchone()["c"]
    assert spent == 0


def test_submissions_round_trip_through_the_repository(conn, corpus):
    from sentinelops.repositories import repositories

    seed_database(conn, corpus)
    loaded = repositories(conn)["inbound"].get(corpus.submissions[0].id)
    assert isinstance(loaded, InboundSubmission)
    assert loaded == corpus.submissions[0]


# --- the truth payload -----------------------------------------------------

def test_truth_payload_records_the_scoring_rule(corpus):
    payload = truth_payload(corpus)
    assert payload["seed"] == corpus.seed
    assert payload["quality_to_expected_verdict"]["near_miss"] == "gap"
    assert payload["quality_to_expected_verdict"]["wrong_type"] == "insufficient_evidence"
    assert payload["counts"]["truth_rows"] == len(corpus.truth_rows)
    assert len(payload["rows"]) == len(corpus.truth_rows)
    assert payload["fingerprint"] == corpus.fingerprint()


def test_every_submission_has_exactly_one_truth_row(corpus):
    rows = [r for r in corpus.truth_rows if r["submission_id"]]
    assert len(rows) == len(corpus.submissions)
    assert len({r["submission_id"] for r in rows}) == len(corpus.submissions)
