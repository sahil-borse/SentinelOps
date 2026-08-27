"""Round-trip every entity through SQLite."""

from datetime import date, datetime

from sentinelops.entities import (
    Action,
    CheckInstance,
    ComplianceException,
    ControlDefinition,
    Evidence,
    Finding,
    ProcessArea,
)

AREA = ProcessArea("A1", "Payments", "Finance Ops", "K. Rao", {"handles_pii": True})
CONTROL = ControlDefinition(
    "C1", "Access review", "Review privileged accounts.", "quarterly",
    {"handles_pii": True}, "document", ["access_review_report"], 100, 3.0,
)


def _seed(repo):
    repo["areas"].add(AREA)
    repo["controls"].add(CONTROL)
    instance = CheckInstance(
        "I1", "C1", "A1", "2026-Q1", date(2026, 4, 15), "pending", "Finance Ops", "K. Rao"
    )
    repo["instances"].add(instance)
    return instance


def test_process_area_round_trip(repo):
    repo["areas"].add(AREA)
    assert repo["areas"].get("A1") == AREA
    assert repo["areas"].get("A1").attributes["handles_pii"] is True


def test_control_round_trip_keeps_json_fields(repo):
    repo["controls"].add(CONTROL)
    loaded = repo["controls"].get("C1")
    assert loaded == CONTROL
    assert loaded.required_evidence_types == ["access_review_report"]


def test_check_instance_dates_and_update(repo):
    instance = _seed(repo)
    assert repo["instances"].get("I1").due_date == date(2026, 4, 15)
    instance.status = "assessed"
    repo["instances"].update(instance)
    assert repo["instances"].get("I1").status == "assessed"


def test_evidence_and_finding_and_action_round_trip(repo):
    _seed(repo)
    evidence = Evidence(
        "E1", "I1", "document", "access_review_report", "text", "abc123",
        datetime(2026, 4, 2, 9, 30), "K. Rao", True,
    )
    repo["evidence"].add(evidence)
    assert repo["evidence"].get("E1") == evidence
    assert repo["evidence"].get("E1").is_remediation is True

    finding = Finding(
        "F1", "I1", "gap", 0.8, "why", ["span"], ["gap"], "fix it", False,
        datetime(2026, 4, 3, 10, 0), None,
    )
    repo["findings"].add(finding)
    assert repo["findings"].get("F1") == finding

    superseding = Finding(
        "F2", "I1", "compliant", 0.95, "fixed", ["span"], [], "", False,
        datetime(2026, 5, 1, 10, 0), "F1",
    )
    repo["findings"].add(superseding)
    assert repo["findings"].get("F2").supersedes_finding_id == "F1"

    action = Action("ACT1", "F1", "Revoke", "Finance Ops", "K. Rao", date(2026, 5, 15))
    repo["actions"].add(action)
    assert repo["actions"].get("ACT1") == action
    assert repo["actions"].get("ACT1").resolved_at is None


def test_compliance_exception_round_trip(repo):
    repo["areas"].add(AREA)
    repo["controls"].add(CONTROL)
    exc = ComplianceException(
        "X1", "C1", "A1", "Legacy system retiring", "CFO",
        date(2026, 1, 1), date(2026, 6, 30), "active",
    )
    repo["exceptions"].add(exc)
    assert repo["exceptions"].get("X1") == exc
    assert repo["exceptions"].list(status="active") == [exc]
    assert repo["exceptions"].list(status="revoked") == []
