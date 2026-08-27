"""Slice 1's single path: area -> ... -> finding -> action -> audit -> usage."""

from sentinelops.main import run


def test_one_path_writes_every_record(tmp_path):
    result = run(str(tmp_path / "e2e.db"))
    finding, action = result["finding"], result["action"]

    assert finding.verdict in {"compliant", "partial", "gap", "insufficient_evidence"}
    assert finding.cited_spans, "an uncited compliance verdict is a bug"
    assert action.finding_id == finding.id
    assert action.status == "raised"
    assert action.owner_team == "Customer Operations"

    actions = [e.action for e in result["audit_events"]]
    assert actions == [
        "check_instance_created",
        "evidence_submitted",
        "finding_recorded",
        "action_raised",
    ]
    assert {e.actor for e in result["audit_events"]} == {"system", "user", "ai"}

    usage = result["token_usage"]
    assert len(usage) == 1
    assert usage[0]["input_tokens"] > 0 and usage[0]["output_tokens"] > 0
    result["conn"].close()


def test_the_path_is_reproducible(tmp_path):
    a = run(str(tmp_path / "a.db"))
    b = run(str(tmp_path / "b.db"))
    assert a["finding"].verdict == b["finding"].verdict
    assert a["finding"].cited_spans == b["finding"].cited_spans
    assert dict(a["token_usage"][0])["input_tokens"] == (
        dict(b["token_usage"][0])["input_tokens"]
    )
    a["conn"].close()
    b["conn"].close()
