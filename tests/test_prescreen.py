"""S2 — the tier that resolves everything resolvable before spending a token."""

import json
import sqlite3
from datetime import date, datetime, timedelta

import pytest

from sentinelops.entities import CheckInstance, ControlDefinition, Evidence, EvidenceSubmission
from sentinelops.repositories import Repository, WriteOnceRepository, repositories
from sentinelops.stages.prescreen import (
    CONSIDERED,
    RULES,
    evaluate_thresholds,
    evidence_age_days,
    evidence_id_for,
)
from sentinelops.stages.prescreen import run as prescreen
from sentinelops.stages.trigger import run_cycle
from sentinelops.synth import generate_corpus, seed_database

END_OF_STORY = date(2027, 3, 31)


@pytest.fixture(scope="module")
def corpus():
    return generate_corpus()


@pytest.fixture()
def scheduled(conn, corpus):
    """A full year run through S1, so S2 has real instances to work on."""
    seed_database(conn, corpus)
    for month in range(1, 13):
        run_cycle(conn, date(2026, month, 28))
    run_cycle(conn, END_OF_STORY)
    return conn


@pytest.fixture()
def screened(scheduled):
    return scheduled, prescreen(scheduled, END_OF_STORY)


# --- rule 1: nothing was filed ---------------------------------------------

def test_no_evidence_resolves_to_insufficient_evidence(screened):
    conn, report = screened
    repo = repositories(conn)
    finding = repo["findings"].list(
        check_instance_id="CHK-CUST-COMPLAINTS-CUSTOPS-2026-07"
    )[0]
    assert finding.verdict == "insufficient_evidence"
    assert finding.decided_by == "no_evidence"
    assert finding.confidence == 1.0
    assert "No evidence was submitted" in finding.rationale
    assert report.exits["no_evidence"] > 0


def test_no_evidence_findings_match_the_corpus_missing_rows(screened, corpus):
    conn, report = screened
    missing = [r for r in corpus.truth_rows if r["defect_kind"] == "missing"]
    # every missing coordinate except the one EXC-004 waived before it was judged
    assert report.exits["no_evidence"] == len(missing) - 1


# --- rule 2: the wrong kind of document ------------------------------------

def test_wrong_evidence_type_never_reaches_a_model(screened, corpus):
    conn, report = screened
    repo = repositories(conn)
    controls = {c.id: c for c in corpus.controls}
    findings = [
        f for f in repo["findings"].list() if f.decided_by == "wrong_evidence_type"
    ]
    assert findings
    assert report.exits["wrong_evidence_type"] == len(findings)
    for finding in findings:
        instance = repo["instances"].get(finding.check_instance_id)
        evidence = repo["evidence"].list(check_instance_id=instance.id)[0]
        assert evidence.doc_type not in controls[instance.control_id].required_evidence_types
        assert finding.verdict == "insufficient_evidence"
        assert evidence.doc_type in finding.rationale


def test_wrong_type_is_checked_before_freshness(conn):
    """Rule order matters: a stale wrong-type document is a type problem."""
    repo = _one_instance(conn, freshness_days=10)
    _stage(repo, doc_type="training_certificate", submitted=datetime(2025, 1, 1, 9, 0))
    report = prescreen(conn, END_OF_STORY)
    assert report.exits["wrong_evidence_type"] == 1
    assert report.exits["stale_evidence"] == 0


# --- rule 3: unchanged since the last assessed period ----------------------

def test_identical_evidence_carries_the_prior_finding_forward(conn):
    """January was assessed by S3; February's evidence is byte-identical.

    The rule is "unchanged since the last *assessed* period", so the prior
    period must genuinely have a verdict. A period still queued for S3 has
    nothing to carry — which is why this needs a settled January, not merely
    an earlier one.
    """
    repo = _one_instance(conn)
    january = _assessed_period(repo, "2026-01", "unchanged report body")
    _extra_instance(repo, period="2026-02")
    _stage(repo, period="2026-02", content="unchanged report body")

    report = prescreen(conn, END_OF_STORY)
    assert report.exits["carried_forward"] == 1

    february = repo["findings"].list(check_instance_id="CHK-X-A-2026-02")[0]
    assert february.carried_forward_from == january.id
    assert february.verdict == january.verdict == "partial"
    assert february.cited_spans == january.cited_spans
    assert february.decided_by == "carried_forward"
    assert "byte-identical to 2026-01" in february.rationale
    assert january.id in february.rationale
    assert report.to_assess == [], "it must not also be sent to S3"


def test_a_carried_forward_verdict_costs_nothing(conn):
    repo = _one_instance(conn)
    _assessed_period(repo, "2026-01", "unchanged report body")
    _extra_instance(repo, period="2026-02")
    _stage(repo, period="2026-02", content="unchanged report body")

    prescreen(conn, END_OF_STORY)
    assert conn.execute("SELECT COUNT(*) c FROM token_usage").fetchone()["c"] == 0


def test_different_evidence_does_not_carry_forward(conn):
    """One byte of difference and the prior verdict no longer speaks for it."""
    repo = _one_instance(conn)
    _assessed_period(repo, "2026-01", "report body as filed in January")
    _extra_instance(repo, period="2026-02")
    _stage(repo, period="2026-02", content="report body as filed in February")

    report = prescreen(conn, END_OF_STORY)
    assert report.exits["carried_forward"] == 0
    assert report.to_assess == ["CHK-X-A-2026-02"]


def test_identical_evidence_in_another_area_does_not_carry_forward(conn):
    """The consistency pair must be judged twice over, not copied across."""
    from sentinelops.entities import ProcessArea

    repo = _one_instance(conn)
    _assessed_period(repo, "2026-01", "shared report body")
    repo["areas"].add(
        ProcessArea("AREA-B", "Area B", "Team B", "B. Owner",
                    {"handles_pii": True, "customer_facing": False,
                     "has_suppliers": False, "region": "NA", "criticality": "low"})
    )
    repo["instances"].add(
        CheckInstance("CHK-X-B-2026-01", "CTRL-X", "AREA-B", "2026-01",
                      date(2026, 2, 15), "submitted", "Team B", "B. Owner")
    )
    repo["submissions"].add(
        EvidenceSubmission(
            id="SUB-B", control_id="CTRL-X", process_area_id="AREA-B",
            period="2026-01", kind="document", doc_type="report",
            content="shared report body",
            content_hash="hash-of-shared report body",
            submitted_at=datetime(2026, 2, 5, 9, 0), author="B. Owner",
        )
    )

    report = prescreen(conn, END_OF_STORY)
    assert report.exits["carried_forward"] == 0
    assert report.to_assess == ["CHK-X-B-2026-01"]


def test_the_corpus_never_repeats_evidence_across_periods(screened, corpus):
    """Honest zero: the generator varies every document, so nothing carries.

    The rule is exercised by the constructed cases above. If slice 2 ever grows
    repeated filings this assertion is the thing that should change.
    """
    conn, report = screened
    assert report.exits["carried_forward"] == 0
    seen = {}
    for submission in corpus.submissions:
        if submission.is_remediation:
            continue
        key = (submission.control_id, submission.process_area_id,
               submission.content_hash)
        assert key not in seen or seen[key] == submission.period
        seen[key] = submission.period


# --- rule 4: too old to speak for the period -------------------------------

def test_stale_evidence_is_a_gap_by_rule(screened):
    conn, report = screened
    repo = repositories(conn)
    findings = [f for f in repo["findings"].list() if f.decided_by == "stale_evidence"]
    assert findings
    assert report.exits["stale_evidence"] == len(findings)
    for finding in findings:
        assert finding.verdict == "gap"
        assert "freshness window" in finding.rationale
        assert finding.confidence == 1.0


def test_freshness_is_measured_against_period_close(corpus):
    control = next(c for c in corpus.controls if c.id == "CTRL-ACCESS-REVIEW")
    evidence = Evidence(
        id="E", check_instance_id="I", kind="document", doc_type="d",
        content="c", content_hash="h",
        submitted_at=datetime(2026, 1, 1, 9, 0), author="a",
    )
    assert evidence_age_days(evidence, date(2026, 3, 31)) == 89
    assert 89 < control.freshness_days  # inside a 100 day window


def test_evidence_dated_after_the_period_is_never_stale(conn):
    """Filed after close is normal; only *old* evidence fails this rule."""
    repo = _one_instance(conn, freshness_days=30)
    _stage(repo, submitted=datetime(2026, 2, 10, 9, 0))  # after 2026-01 closed
    report = prescreen(conn, END_OF_STORY)
    assert report.exits["stale_evidence"] == 0


# --- rule 5: arithmetic, not judgement -------------------------------------

def test_structured_evidence_is_evaluated_in_code(screened):
    conn, report = screened
    repo = repositories(conn)
    findings = [
        f for f in repo["findings"].list() if f.decided_by == "structured_threshold"
    ]
    assert findings
    assert report.exits["structured_threshold"] == len(findings)
    for finding in findings:
        assert finding.verdict in ("compliant", "gap", "insufficient_evidence")
        assert finding.confidence == 1.0
        assert finding.needs_human_review is False
        assert finding.cited_spans, "a structured verdict must cite its numbers"


def test_a_structured_rationale_names_the_numbers(corpus):
    control = next(c for c in corpus.controls if c.id == "CTRL-TRAINING")
    evidence = _metrics_evidence(
        {"population": 200, "completed": 183, "completion_pct": 91.5,
         "overdue_staff": 3, "source": "HR system of record"}
    )
    verdict, cited, gaps, rationale = evaluate_thresholds(control, evidence)

    assert verdict == "gap"
    assert "91.5" in rationale and "95.0" in rationale
    assert "completion_pct" in rationale
    assert any("91.5" in span for span in cited)
    assert gaps and "91.5" in gaps[0]


def test_a_passing_table_is_compliant_and_still_cites(corpus):
    control = next(c for c in corpus.controls if c.id == "CTRL-TRAINING")
    evidence = _metrics_evidence(
        {"population": 200, "completed": 198, "completion_pct": 99.0,
         "overdue_staff": 2, "source": "HR system of record"}
    )
    verdict, cited, gaps, rationale = evaluate_thresholds(control, evidence)
    assert verdict == "compliant"
    assert gaps == []
    assert len(cited) == len(control.thresholds)
    assert rationale.startswith("All thresholds met")


def test_a_table_missing_a_metric_is_insufficient_not_a_gap(corpus):
    control = next(c for c in corpus.controls if c.id == "CTRL-TRAINING")
    evidence = _metrics_evidence({"population": 200, "completion_pct": 99.0})
    verdict, _, gaps, rationale = evaluate_thresholds(control, evidence)
    assert verdict == "insufficient_evidence"
    assert "overdue_staff" in rationale
    assert gaps


def test_unparsable_structured_evidence_is_insufficient(corpus):
    control = next(c for c in corpus.controls if c.id == "CTRL-TRAINING")
    evidence = Evidence(
        id="E", check_instance_id="I", kind="structured", doc_type="d",
        content="this is prose, not a table", content_hash="h",
        submitted_at=datetime(2026, 4, 1, 9, 0), author="a",
    )
    verdict, _, _, _ = evaluate_thresholds(control, evidence)
    assert verdict == "insufficient_evidence"


def test_both_thresholds_are_checked_not_just_the_first(corpus):
    control = next(c for c in corpus.controls if c.id == "CTRL-BACKUP-VERIFY")
    evidence = _metrics_evidence(
        {"restore_tests": 10, "restore_tests_passed": 10, "success_pct": 100.0,
         "max_rto_minutes": 140, "stores_covered": 5, "stores_total": 5}
    )
    verdict, _, gaps, rationale = evaluate_thresholds(control, evidence)
    assert verdict == "gap"
    assert "max_rto_minutes" in gaps[0] and "140" in gaps[0]
    assert "success_pct was 100.0" in rationale  # the passing one is still reported


# --- what survives ---------------------------------------------------------

def test_only_ambiguous_document_evidence_survives(screened, corpus):
    conn, report = screened
    repo = repositories(conn)
    controls = {c.id: c for c in corpus.controls}
    assert report.to_assess
    for instance_id in report.to_assess:
        instance = repo["instances"].get(instance_id)
        control = controls[instance.control_id]
        evidence = repo["evidence"].list(check_instance_id=instance_id)[0]

        assert control.evidence_kind == "document"
        assert evidence.doc_type in control.required_evidence_types
        assert instance.status == "submitted", "still awaiting a verdict"
        assert repo["findings"].list(check_instance_id=instance_id) == []


def test_no_structured_instance_ever_survives_to_s3(screened, corpus):
    conn, report = screened
    repo = repositories(conn)
    structured = {c.id for c in corpus.controls if c.evidence_kind == "structured"}
    for instance_id in report.to_assess:
        assert repo["instances"].get(instance_id).control_id not in structured


def test_pending_instances_are_not_judged(scheduled):
    """Not yet due is not the same as no evidence."""
    repo = repositories(scheduled)
    run_cycle(scheduled, date(2026, 2, 28))
    report = prescreen(scheduled, date(2026, 2, 28))
    for instance in repo["instances"].list():
        if instance.status == "pending":
            assert repo["findings"].list(check_instance_id=instance.id) == []
    assert report.skipped_not_due >= 0


# --- evidence is write-once ------------------------------------------------

def test_the_evidence_repository_has_no_update_or_delete():
    public = {n for n in dir(WriteOnceRepository) if not n.startswith("_")}
    assert public == {"add", "get", "list"}
    assert not hasattr(WriteOnceRepository, "update")
    assert not hasattr(WriteOnceRepository, "delete")
    # and it is genuinely a different class from the mutable one
    assert not issubclass(WriteOnceRepository, Repository)
    assert hasattr(Repository, "update")


def test_the_wired_up_evidence_repository_is_the_write_once_one(conn):
    assert isinstance(repositories(conn)["evidence"], WriteOnceRepository)


def test_the_database_refuses_to_update_evidence(conn):
    repo = repositories(conn)
    _seed_minimal(repo)
    repo["evidence"].add(_evidence("EV-1", "CHK-X-A-2026-01", "original text"))

    with pytest.raises(sqlite3.IntegrityError, match="write-once"):
        conn.execute("UPDATE evidence SET content = 'tampered' WHERE id = 'EV-1'")
    assert repo["evidence"].get("EV-1").content == "original text"


def test_the_database_refuses_to_delete_evidence(conn):
    repo = repositories(conn)
    _seed_minimal(repo)
    repo["evidence"].add(_evidence("EV-1", "CHK-X-A-2026-01", "original text"))

    with pytest.raises(sqlite3.IntegrityError, match="write-once"):
        conn.execute("DELETE FROM evidence WHERE id = 'EV-1'")
    assert repo["evidence"].get("EV-1") is not None


def test_resubmission_creates_a_new_record_and_leaves_the_first_alone(conn):
    from sentinelops.stages.prescreen import bind_evidence

    repo = _one_instance(conn)
    instance = repo["instances"].get("CHK-X-A-2026-01")
    first = _submission("SUB-1", "first filing", datetime(2026, 2, 5, 9, 0))
    second = _submission("SUB-2", "corrected filing", datetime(2026, 3, 5, 9, 0),
                         is_remediation=True)
    repo["submissions"].add(first)
    repo["submissions"].add(second)

    original = bind_evidence(repo, instance, first)
    replacement = bind_evidence(repo, instance, second)

    stored = repo["evidence"].list(check_instance_id=instance.id)
    assert len(stored) == 2
    assert original.id != replacement.id
    assert {e.content for e in stored} == {"first filing", "corrected filing"}
    # the first record is untouched by the second filing
    assert repo["evidence"].get(original.id).content == "first filing"
    assert repo["evidence"].get(original.id).is_remediation is False


def test_binding_the_same_submission_twice_is_idempotent(conn):
    from sentinelops.stages.prescreen import bind_evidence

    repo = _one_instance(conn)
    instance = repo["instances"].get("CHK-X-A-2026-01")
    submission = _submission("SUB-1", "one filing", datetime(2026, 2, 5, 9, 0))
    repo["submissions"].add(submission)

    a = bind_evidence(repo, instance, submission)
    b = bind_evidence(repo, instance, submission)
    assert a.id == b.id == evidence_id_for("SUB-1")
    assert len(repo["evidence"].list()) == 1


# --- instrumentation -------------------------------------------------------

def test_the_report_accounts_for_every_considered_instance(screened):
    conn, report = screened
    assert report.resolved + len(report.to_assess) == report.considered
    assert report.considered == 342  # 343 generated, one waived before judgement


def test_the_zero_model_share_is_real(screened):
    conn, report = screened
    repo = repositories(conn)
    decided = [f for f in repo["findings"].list() if f.decided_by in RULES]
    assert len(decided) == report.resolved
    assert report.zero_model_share == pytest.approx(
        report.resolved / report.considered
    )
    assert 0.35 < report.zero_model_share < 0.5


def test_every_rule_is_named_in_the_breakdown(screened):
    conn, report = screened
    names = [row[0] for row in report.breakdown()]
    assert names[:-1] == list(RULES)
    assert names[-1].startswith("to_assess")
    assert sum(row[1] for row in report.breakdown()) == report.considered


def test_the_run_is_recorded_in_the_audit_trail(screened):
    conn, report = screened
    event = [
        e for e in repositories(conn)["audit"].read_all()
        if e.action == "prescreen_completed"
    ][-1]
    assert event.detail["considered"] == report.considered
    assert event.detail["resolved_without_a_model"] == report.resolved
    assert event.detail["exit_structured_threshold"] == report.exits[
        "structured_threshold"
    ]


def test_every_prescreen_finding_records_zero_model_calls(screened):
    conn, _ = screened
    events = [
        e for e in repositories(conn)["audit"].read_all()
        if e.action == "finding_recorded"
    ]
    assert events
    assert all(e.detail["model_calls"] == 0 for e in events)


def test_running_the_pre_screen_twice_decides_nothing_new(screened):
    conn, first = screened
    before = len(repositories(conn)["findings"].list())
    second = prescreen(conn, END_OF_STORY)
    assert second.considered == len(first.to_assess)
    assert second.resolved == 0
    assert len(repositories(conn)["findings"].list()) == before


# --- zero model calls ------------------------------------------------------

@pytest.fixture()
def exploding_llm(monkeypatch):
    def _no(*args, **kwargs):
        raise AssertionError("S2 must never call a model")

    import sentinelops.llm as llm
    import sentinelops.llm.factory as factory
    from sentinelops.llm.providers.fake import FakeModelClient
    from sentinelops.llm.providers.openai import OpenAIClient

    monkeypatch.setattr(factory, "get_client", _no)
    monkeypatch.setattr(llm, "get_client", _no)
    monkeypatch.setattr(FakeModelClient, "complete", _no)
    monkeypatch.setattr(OpenAIClient, "complete", _no)


def test_the_whole_corpus_pre_screens_with_providers_rigged_to_explode(
    scheduled, exploding_llm
):
    report = prescreen(scheduled, END_OF_STORY)
    assert report.resolved > 100
    assert scheduled.execute(
        "SELECT COUNT(*) c FROM token_usage"
    ).fetchone()["c"] == 0


def test_the_prescreen_module_cannot_reach_a_model():
    from pathlib import Path

    from test_applicability import _code_only

    src = Path(__file__).resolve().parents[1] / "src" / "sentinelops"
    assert "llm" not in _code_only(src / "stages" / "prescreen.py")


# --- helpers ---------------------------------------------------------------

def _metrics_evidence(metrics):
    body = json.dumps(metrics, indent=2, sort_keys=True)
    return Evidence(
        id="E", check_instance_id="I", kind="structured", doc_type="d",
        content=body, content_hash="h",
        submitted_at=datetime(2026, 4, 1, 9, 0), author="a",
    )


def _evidence(identifier, instance_id, content):
    return Evidence(
        id=identifier, check_instance_id=instance_id, kind="document",
        doc_type="report", content=content, content_hash="h",
        submitted_at=datetime(2026, 2, 5, 9, 0), author="A. Owner",
    )


def _submission(identifier, content, submitted, is_remediation=False,
                doc_type="report", period="2026-01", control_id="CTRL-X"):
    return EvidenceSubmission(
        id=identifier, control_id=control_id, process_area_id="AREA-A",
        period=period, kind="document", doc_type=doc_type, content=content,
        content_hash=f"hash-of-{content}", submitted_at=submitted,
        author="A. Owner", is_remediation=is_remediation,
    )


def _seed_minimal(repo, freshness_days=100, control_id="CTRL-X"):
    from sentinelops.entities import ProcessArea

    if repo["areas"].get("AREA-A") is None:
        repo["areas"].add(
            ProcessArea("AREA-A", "Area A", "Team A", "A. Owner",
                        {"handles_pii": True, "customer_facing": False,
                         "has_suppliers": False, "region": "EMEA",
                         "criticality": "high"})
        )
    if repo["controls"].get(control_id) is None:
        repo["controls"].add(
            ControlDefinition(
                id=control_id, title="Control X", criteria_text="1. Do the thing.",
                frequency="monthly", applies_when={}, evidence_kind="document",
                required_evidence_types=["report"], freshness_days=freshness_days,
                severity_weight=1.0,
            )
        )
    if repo["instances"].get("CHK-X-A-2026-01") is None:
        repo["instances"].add(
            CheckInstance("CHK-X-A-2026-01", control_id, "AREA-A", "2026-01",
                          date(2026, 2, 15), "submitted", "Team A", "A. Owner")
        )


def _one_instance(conn, freshness_days=100, period="2026-01", control_id="CTRL-X"):
    repo = repositories(conn)
    _seed_minimal(repo, freshness_days, control_id)
    return repo


def _assessed_period(repo, period, content, control_id="CTRL-X"):
    """A period S3 has already judged, with its evidence on file."""
    from sentinelops.entities import Finding

    instance_id = f"CHK-X-A-{period}"
    instance = repo["instances"].get(instance_id)
    if instance is None:
        instance = CheckInstance(instance_id, control_id, "AREA-A", period,
                                 date(2026, 2, 15), "assessed", "Team A", "A. Owner")
        repo["instances"].add(instance)
    else:
        instance.status = "assessed"
        repo["instances"].update(instance)
    repo["evidence"].add(
        Evidence(id=f"EV-SUB-{period}", check_instance_id=instance_id,
                 kind="document", doc_type="report", content=content,
                 content_hash=f"hash-of-{content}",
                 submitted_at=datetime(2026, 2, 5, 9, 0), author="A. Owner")
    )
    finding = Finding(
        id=f"FND-X-A-{period}-1", check_instance_id=instance_id,
        verdict="partial", confidence=0.72,
        rationale="Clause 2 is only partially evidenced.",
        cited_spans=["the reviewer field was left blank"],
        gaps=["Reviewer not recorded."],
        recommended_action="Record the reviewer and resubmit.",
        needs_human_review=False, assessed_at=datetime(2026, 2, 20, 9, 0),
        decided_by="s3_model",
    )
    repo["findings"].add(finding)
    return finding


def _extra_instance(repo, period, control_id="CTRL-X"):
    repo["instances"].add(
        CheckInstance(f"CHK-X-A-{period}", control_id, "AREA-A", period,
                      date(2026, 3, 15), "submitted", "Team A", "A. Owner")
    )


def _stage(repo, period="2026-01", content="A report.", doc_type="report",
           submitted=datetime(2026, 2, 5, 9, 0), control_id="CTRL-X"):
    repo["submissions"].add(
        _submission(f"SUB-{period}-{doc_type}", content, submitted,
                    doc_type=doc_type, period=period, control_id=control_id)
    )
