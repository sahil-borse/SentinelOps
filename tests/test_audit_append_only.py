"""The audit trail must not be editable, by construction."""

import pytest

from sentinelops.repositories import AuditLog


@pytest.mark.parametrize("forbidden", ["update", "delete", "remove", "edit", "set"])
def test_audit_log_exposes_no_mutating_methods(forbidden):
    assert not hasattr(AuditLog, forbidden)


def test_audit_log_exposes_only_append_and_reads():
    public = {n for n in dir(AuditLog) if not n.startswith("_")}
    assert public == {"append", "read_all", "read_for"}


def test_append_and_read_back(repo):
    repo["audit"].append("system", "R. Mehta", "check_created", "CheckInstance", "C1")
    repo["audit"].append("ai", "R. Mehta", "finding_recorded", "Finding", "F1")
    events = repo["audit"].read_all()
    assert [e.action for e in events] == ["check_created", "finding_recorded"]
    assert [e.id for e in events] == [1, 2]
    assert repo["audit"].read_for("Finding", "F1")[0].actor == "ai"
