"""The audit log is tamper-evident: one edited row shows, and says where."""

from datetime import date, datetime

import pytest

from sentinelops.repositories import (
    GENESIS_HASH,
    canonical_payload,
    compute_entry_hash,
    repositories,
)
from sentinelops.stages.trigger import run_cycle
from sentinelops.synth import generate_corpus, seed_database


@pytest.fixture(scope="module")
def corpus():
    return generate_corpus()


@pytest.fixture()
def busy_log(conn, corpus):
    """A log with real traffic in it, not three hand-written rows."""
    seed_database(conn, corpus)
    run_cycle(conn, date(2026, 6, 30))
    return conn


def _append_a_few(repo, count=5):
    for n in range(count):
        repo["audit"].append(
            actor="system", owner=f"Owner {n}", action="thing_happened",
            entity_type="Thing", entity_id=f"T-{n}", detail={"n": n},
        )


# --- the two the slice asks for --------------------------------------------

def test_an_untouched_log_verifies_clean(busy_log):
    result = repositories(busy_log)["audit"].verify_chain()

    assert result.ok is True
    assert bool(result) is True
    assert result.broken_at is None
    assert result.checked > 100, "a real cycle's worth of entries"
    assert result.describe().startswith("OK")


def test_one_row_edited_in_sqlite_fails_at_that_sequence_number(busy_log):
    """The whole point: change one field and the log says which entry."""
    repo = repositories(busy_log)
    assert repo["audit"].verify_chain().ok

    target = 42
    before = busy_log.execute(
        "SELECT owner FROM audit_events WHERE seq = ?", (target,)
    ).fetchone()["owner"]
    busy_log.execute(
        "UPDATE audit_events SET owner = 'Someone Else' WHERE seq = ?", (target,)
    )
    busy_log.commit()

    result = repo["audit"].verify_chain()

    assert result.ok is False
    assert bool(result) is False
    assert result.broken_at == target
    assert result.checked == target - 1, "everything before it still verified"
    assert "do not match its hash" in result.reason
    assert "altered" in result.reason
    assert before != "Someone Else"


# --- the other shapes a tamper can take ------------------------------------

def test_an_edited_detail_field_is_caught(busy_log):
    repo = repositories(busy_log)
    busy_log.execute(
        "UPDATE audit_events SET detail = '{\"verdict\": \"compliant\"}'"
        " WHERE seq = 7"
    )
    busy_log.commit()

    result = repo["audit"].verify_chain()
    assert result.broken_at == 7
    assert "altered" in result.reason


def test_a_backdated_timestamp_is_caught(busy_log):
    repo = repositories(busy_log)
    busy_log.execute(
        "UPDATE audit_events SET ts = '2020-01-01T00:00:00' WHERE seq = 15"
    )
    busy_log.commit()
    assert repo["audit"].verify_chain().broken_at == 15


def test_a_deleted_entry_is_caught(busy_log):
    """Removing a row breaks the sequence, not just the hashes."""
    repo = repositories(busy_log)
    busy_log.execute("DELETE FROM audit_events WHERE seq = 20")
    busy_log.commit()

    result = repo["audit"].verify_chain()
    assert result.ok is False
    assert result.broken_at == 21
    assert "not contiguous" in result.reason


def test_rewriting_an_entry_and_its_own_hash_still_breaks_the_next_link(busy_log):
    """A tamperer who knows about the hash column has to rebuild the rest."""
    repo = repositories(busy_log)
    row = busy_log.execute("SELECT * FROM audit_events WHERE seq = 30").fetchone()

    from sentinelops.entities import AuditEvent
    from sentinelops.repositories import _load

    event = _load(AuditEvent, row)
    event.owner = "Someone Else"
    forged = compute_entry_hash(event)
    busy_log.execute(
        "UPDATE audit_events SET owner = ?, entry_hash = ? WHERE seq = 30",
        ("Someone Else", forged),
    )
    busy_log.commit()

    result = repo["audit"].verify_chain()
    assert result.ok is False
    assert result.broken_at == 31, "the entry after it no longer links back"
    assert "recorded predecessor" in result.reason


def test_the_first_entry_is_covered_too(conn):
    repo = repositories(conn)
    _append_a_few(repo, 3)
    conn.execute("UPDATE audit_events SET action = 'nothing_happened' WHERE seq = 1")
    conn.commit()

    result = repo["audit"].verify_chain()
    assert result.broken_at == 1
    assert result.checked == 0


def test_the_last_entry_is_covered_too(conn):
    """Nothing points at the final entry, so its own hash has to protect it."""
    repo = repositories(conn)
    _append_a_few(repo, 4)
    conn.execute("UPDATE audit_events SET owner = 'Ghost' WHERE seq = 4")
    conn.commit()

    result = repo["audit"].verify_chain()
    assert result.broken_at == 4


# --- the chain itself -------------------------------------------------------

def test_an_empty_log_verifies_clean(conn):
    result = repositories(conn)["audit"].verify_chain()
    assert result.ok is True
    assert result.checked == 0


def test_the_first_entry_links_to_genesis(conn):
    repo = repositories(conn)
    event = repo["audit"].append(
        actor="system", owner="O", action="a", entity_type="E", entity_id="1"
    )
    assert event.seq == 1
    assert event.prev_hash == GENESIS_HASH
    assert event.entry_hash == compute_entry_hash(event)


def test_sequence_numbers_are_monotonic_with_no_gaps(busy_log):
    events = repositories(busy_log)["audit"].read_all()
    assert [e.seq for e in events] == list(range(1, len(events) + 1))


def test_each_entry_records_the_hash_of_the_one_before(busy_log):
    events = repositories(busy_log)["audit"].read_all()
    assert len(events) > 10
    for previous, current in zip(events, events[1:]):
        assert current.prev_hash == previous.entry_hash


def test_the_hash_covers_the_link_not_only_the_contents(conn):
    """Otherwise re-pointing an entry at a different predecessor would pass."""
    repo = repositories(conn)
    _append_a_few(repo, 2)
    events = repo["audit"].read_all()

    moved = events[1]
    moved.prev_hash = GENESIS_HASH
    assert compute_entry_hash(moved) != events[1].entry_hash


def test_canonical_payload_is_stable_and_excludes_storage_details(conn):
    repo = repositories(conn)
    event = repo["audit"].append(
        actor="system", owner="O", action="a", entity_type="E", entity_id="1",
        detail={"b": 2, "a": 1}, ts=datetime(2026, 5, 1, 9, 30),
    )
    payload = canonical_payload(event)

    assert canonical_payload(event) == payload, "same input, same bytes"
    assert '"a":1' in payload and '"b":2' in payload
    assert payload.index('"a":1') < payload.index('"b":2'), "keys are sorted"
    assert '"id"' not in payload, "the rowid is storage, not evidence"
    assert '"seq":1' in payload, "position is part of what is signed"


def test_two_logs_built_the_same_way_hash_the_same(conn):
    """The chain depends on content, not on when it happened to be written."""
    import sentinelops.db as db_module

    other = db_module.connect(":memory:")
    stamp = datetime(2026, 5, 1, 9, 30)
    for target in (conn, other):
        repo = repositories(target)
        for n in range(3):
            repo["audit"].append(
                actor="system", owner="O", action="a", entity_type="E",
                entity_id=str(n), detail={"n": n}, ts=stamp,
            )
    first = [e.entry_hash for e in repositories(conn)["audit"].read_all()]
    second = [e.entry_hash for e in repositories(other)["audit"].read_all()]
    other.close()
    assert first == second


# --- it changed nothing else ------------------------------------------------

def test_appending_still_returns_the_event_with_its_row_id(conn):
    repo = repositories(conn)
    event = repo["audit"].append(
        actor="user", owner="R. Mehta", action="evidence_submitted",
        entity_type="Evidence", entity_id="EV-1", detail={"k": "v"},
    )
    assert event.id == 1
    assert event.detail == {"k": "v"}
    assert repo["audit"].read_for("Evidence", "EV-1")[0].owner == "R. Mehta"


def test_verification_never_repairs_anything(busy_log):
    """A method that could fix the chain would defeat the point of having one."""
    repo = repositories(busy_log)
    busy_log.execute("UPDATE audit_events SET owner = 'X' WHERE seq = 5")
    busy_log.commit()

    assert repo["audit"].verify_chain().broken_at == 5
    assert repo["audit"].verify_chain().broken_at == 5, "still broken, not healed"
    assert busy_log.execute(
        "SELECT owner FROM audit_events WHERE seq = 5"
    ).fetchone()["owner"] == "X"
