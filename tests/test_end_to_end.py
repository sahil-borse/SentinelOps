"""Slice 1's single path: unit -> ... -> assessment -> finding -> audit -> usage."""

from sentinelops.main import run


def test_one_path_writes_every_record(tmp_path):
    result = run(str(tmp_path / "e2e.db"))
    assessment, finding = result["assessment"], result["finding"]

    assert assessment.verdict in {
        "compliant", "partial", "gap", "insufficient_evidence"
    }
    assert assessment.cited_spans, "an uncited compliance verdict is a bug"
    assert finding.check_instance_id == "CHK-0001"
    assert finding.status == "open", "a finding starts open and only an auditor closes it"
    assert finding.auditable_unit_id == "AREA-CUSTOPS"
    assert finding.severity and finding.severity_assigned_by

    actions = [e.action for e in result["audit_events"]]
    assert actions == [
        "check_instance_created",
        "evidence_submitted",
        "assessment_recorded",
        "finding_raised",
    ]
    assert {e.actor_kind for e in result["audit_events"]} == {"system", "user", "ai"}

    usage = result["token_usage"]
    assert len(usage) == 1
    assert usage[0]["input_tokens"] > 0 and usage[0]["output_tokens"] > 0
    result["conn"].close()


def test_the_path_is_reproducible(tmp_path):
    a = run(str(tmp_path / "a.db"))
    b = run(str(tmp_path / "b.db"))
    assert a["assessment"].verdict == b["assessment"].verdict
    assert a["assessment"].cited_spans == b["assessment"].cited_spans
    assert a["finding"].severity == b["finding"].severity
    assert a["finding"].target_date == b["finding"].target_date
    assert dict(a["token_usage"][0])["input_tokens"] == (
        dict(b["token_usage"][0])["input_tokens"]
    )
    a["conn"].close()
    b["conn"].close()
