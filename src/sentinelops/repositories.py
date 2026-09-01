"""Thin repository layer over sqlite3.

One repository per entity. Each is a plain class holding a connection; the
row <-> dataclass conversion is done by two module-level functions driven by a
per-entity field spec, so there is no inheritance hierarchy to reason about.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, fields
from datetime import date, datetime, timedelta
from typing import Any

from .entities import (
    Action,
    Flag,
    AuditEvent,
    CheckInstance,
    ComplianceException,
    ControlDefinition,
    Evidence,
    EvidenceSubmission,
    Finding,
    ProcessArea,
)

# entity -> (table, {field: storage kind}) for the fields that are not scalars
_SPEC: dict[type, tuple[str, dict[str, str]]] = {
    ProcessArea: ("process_areas", {"attributes": "json"}),
    ControlDefinition: ("control_definitions", {"applies_when": "json",
                        "required_evidence_types": "json", "thresholds": "json"}),
    CheckInstance: ("check_instances", {"due_date": "date"}),
    Evidence: ("evidence", {"submitted_at": "datetime", "is_remediation": "bool"}),
    EvidenceSubmission: ("evidence_submissions", {"submitted_at": "datetime",
                         "is_remediation": "bool"}),
    Finding: ("findings", {"cited_spans": "json", "gaps": "json",
              "needs_human_review": "bool", "assessed_at": "datetime"}),
    Action: ("actions", {"due_date": "date", "resolved_at": "datetime"}),
    Flag: ("flags", {"raised_at": "datetime"}),
    ComplianceException: ("compliance_exceptions", {"granted_at": "date",
                          "expires_at": "date"}),
    AuditEvent: ("audit_events", {"ts": "datetime", "detail": "json"}),
}


def _dump(entity: Any) -> dict[str, Any]:
    """Dataclass -> column dict."""
    kinds = _SPEC[type(entity)][1]
    out: dict[str, Any] = {}
    for f in fields(entity):
        value = getattr(entity, f.name)
        kind = kinds.get(f.name)
        if value is None:
            out[f.name] = None
        elif kind == "json":
            out[f.name] = json.dumps(value)
        elif kind in ("date", "datetime"):
            out[f.name] = value.isoformat()
        elif kind == "bool":
            out[f.name] = int(value)
        else:
            out[f.name] = value
    return out


def _load(cls: type, row: sqlite3.Row) -> Any:
    """Row -> dataclass."""
    kinds = _SPEC[cls][1]
    kwargs: dict[str, Any] = {}
    for f in fields(cls):
        value = row[f.name]
        kind = kinds.get(f.name)
        if value is None:
            kwargs[f.name] = None
        elif kind == "json":
            kwargs[f.name] = json.loads(value)
        elif kind == "date":
            kwargs[f.name] = date.fromisoformat(value)
        elif kind == "datetime":
            kwargs[f.name] = datetime.fromisoformat(value)
        elif kind == "bool":
            kwargs[f.name] = bool(value)
        else:
            kwargs[f.name] = value
    return cls(**kwargs)


class Repository:
    """Insert / fetch / list for one entity type. Update is per-entity, opt-in."""

    def __init__(self, conn: sqlite3.Connection, entity_type: type) -> None:
        self.conn = conn
        self.entity_type = entity_type
        self.table = _SPEC[entity_type][0]

    def add(self, entity: Any) -> Any:
        data = _dump(entity)
        cols = ", ".join(data)
        marks = ", ".join("?" for _ in data)
        self.conn.execute(
            f"INSERT INTO {self.table} ({cols}) VALUES ({marks})", tuple(data.values())
        )
        self.conn.commit()
        return entity

    def get(self, entity_id: str) -> Any | None:
        row = self.conn.execute(
            f"SELECT * FROM {self.table} WHERE id = ?", (entity_id,)
        ).fetchone()
        return _load(self.entity_type, row) if row else None

    def list(self, **where: Any) -> list[Any]:
        sql = f"SELECT * FROM {self.table}"
        params: tuple[Any, ...] = ()
        if where:
            sql += " WHERE " + " AND ".join(f"{k} = ?" for k in where)
            params = tuple(where.values())
        rows = self.conn.execute(sql, params).fetchall()
        return [_load(self.entity_type, r) for r in rows]

    def update(self, entity: Any) -> Any:
        data = _dump(entity)
        entity_id = data.pop("id")
        assignments = ", ".join(f"{k} = ?" for k in data)
        self.conn.execute(
            f"UPDATE {self.table} SET {assignments} WHERE id = ?",
            (*data.values(), entity_id),
        )
        self.conn.commit()
        return entity


class WriteOnceRepository:
    """Insert and read only, for entities that must never be rewritten.

    Deliberately not a subclass of `Repository`: inheriting and then blanking
    `update` would leave the attribute present, and "the method does not exist"
    is a stronger claim than "the method is None". A database trigger refuses an
    UPDATE underneath this, so going around the repository does not help either.

    Evidence is the case in point. A re-submission is a new row with a new id;
    the earlier record stands unchanged, which is what makes an audit possible.
    """

    def __init__(self, conn: sqlite3.Connection, entity_type: type) -> None:
        self.conn = conn
        self.entity_type = entity_type
        self.table = _SPEC[entity_type][0]

    def add(self, entity: Any) -> Any:
        data = _dump(entity)
        cols = ", ".join(data)
        marks = ", ".join("?" for _ in data)
        self.conn.execute(
            f"INSERT INTO {self.table} ({cols}) VALUES ({marks})", tuple(data.values())
        )
        self.conn.commit()
        return entity

    def get(self, entity_id: str) -> Any | None:
        row = self.conn.execute(
            f"SELECT * FROM {self.table} WHERE id = ?", (entity_id,)
        ).fetchone()
        return _load(self.entity_type, row) if row else None

    def list(self, **where: Any) -> list[Any]:
        sql = f"SELECT * FROM {self.table}"
        params: tuple[Any, ...] = ()
        if where:
            sql += " WHERE " + " AND ".join(f"{k} = ?" for k in where)
            params = tuple(where.values())
        rows = self.conn.execute(sql, params).fetchall()
        return [_load(self.entity_type, r) for r in rows]


#: What the first entry links back to. A constant, so an empty log has a
#: defined starting point and entry one is covered like every other.
GENESIS_HASH = "0" * 64


class _Clock:
    """A clock that advances a little with every entry it stamps."""

    def __init__(self, start: datetime, step_seconds: float) -> None:
        self.now = start
        self.step = timedelta(seconds=step_seconds)

    def tick(self) -> datetime:
        stamped, self.now = self.now, self.now + self.step
        return stamped


_CLOCK: ContextVar[_Clock | None] = ContextVar("sentinelops_clock", default=None)


@contextmanager
def simulated_clock(when: datetime, *, step_seconds: float = 1.0):
    """Stamp audit entries with a simulated date rather than wall-clock time.

    A year of scheduled cycles runs here in about three seconds, so without this
    every entry in the trail carries today's date and the audit log's own
    chronology — the thing an audit log exists for — becomes unusable. Inside
    this block, entries are stamped from the cycle's date instead.

    The clock advances one second per entry so a batch sorts readably; a real
    deployment running nightly would use the wall clock and this would never be
    entered. Nothing outside a simulation should call it, and the pack's method
    note says the corpus is generated.
    """
    token = _CLOCK.set(_Clock(when, step_seconds))
    try:
        yield
    finally:
        _CLOCK.reset(token)


def _stamp() -> datetime:
    clock = _CLOCK.get()
    return clock.tick() if clock is not None else datetime.now()


def canonical_payload(event: AuditEvent) -> str:
    """The bytes an entry's hash is taken over.

    Deliberately explicit rather than "whatever json.dumps does today": the
    field list, the ordering and the separators are all pinned, because a
    verification that depends on incidental formatting will start failing for
    reasons that have nothing to do with tampering.

    `id` is excluded — it is a storage detail assigned by SQLite. `seq` is
    included, so an entry cannot be moved to a different position in the log
    without detection.
    """
    return json.dumps(
        {
            "seq": event.seq,
            "ts": event.ts.isoformat(),
            "actor": event.actor,
            "owner": event.owner,
            "action": event.action,
            "entity_type": event.entity_type,
            "entity_id": event.entity_id,
            "detail": event.detail,
        },
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )


def compute_entry_hash(event: AuditEvent) -> str:
    """This entry's hash, covering the link to the one before it."""
    return hashlib.sha256(
        (event.prev_hash + "\n" + canonical_payload(event)).encode()
    ).hexdigest()


@dataclass(frozen=True)
class ChainVerification:
    """The result of walking the log."""

    ok: bool
    checked: int
    broken_at: int | None = None
    reason: str = ""

    def __bool__(self) -> bool:
        return self.ok

    def describe(self) -> str:
        if self.ok:
            return f"OK - {self.checked} entries, chain intact"
        return f"BROKEN at seq {self.broken_at} - {self.reason}"


class AuditLog:
    """Append-only audit trail, and tamper-evident with it.

    Exposes no update and no delete: the trail is evidence, and evidence that
    can be edited is not evidence. `tests/test_audit_append_only.py` asserts
    those methods are absent.

    Absence of a method only binds callers who go through this class, so the
    entries are also chained — see `verify_chain`. Someone with the database
    file can still rewrite it; they cannot do so without it showing.
    """

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def append(
        self,
        actor: str,
        owner: str,
        action: str,
        entity_type: str,
        entity_id: str,
        detail: dict[str, Any] | None = None,
        ts: datetime | None = None,
    ) -> AuditEvent:
        tail = self.conn.execute(
            "SELECT seq, entry_hash FROM audit_events ORDER BY seq DESC LIMIT 1"
        ).fetchone()
        event = AuditEvent(
            id=None,
            ts=ts or _stamp(),
            actor=actor,  # type: ignore[arg-type]
            owner=owner,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            detail=detail or {},
            seq=(tail["seq"] + 1) if tail else 1,
            prev_hash=tail["entry_hash"] if tail else GENESIS_HASH,
        )
        event.entry_hash = compute_entry_hash(event)
        data = _dump(event)
        data.pop("id")
        cols = ", ".join(data)
        marks = ", ".join("?" for _ in data)
        cur = self.conn.execute(
            f"INSERT INTO audit_events ({cols}) VALUES ({marks})", tuple(data.values())
        )
        self.conn.commit()
        event.id = cur.lastrowid
        return event

    def read_all(self) -> list[AuditEvent]:
        rows = self.conn.execute("SELECT * FROM audit_events ORDER BY id").fetchall()
        return [_load(AuditEvent, r) for r in rows]

    def verify_chain(self) -> ChainVerification:
        """Walk the log and report the first broken link, if any.

        Three ways an entry can fail, checked in the order they would show up:
        its sequence number is not where it should be, its own hash no longer
        matches its contents, or its recorded predecessor is not the entry that
        actually precedes it. Any single edited row trips at least one.

        An empty log verifies clean — there is nothing to have been altered.
        """
        rows = self.conn.execute("SELECT * FROM audit_events ORDER BY seq").fetchall()
        expected_previous = GENESIS_HASH

        for position, row in enumerate(rows, start=1):
            event = _load(AuditEvent, row)

            if event.seq != position:
                return ChainVerification(
                    ok=False, checked=position - 1, broken_at=event.seq,
                    reason=(
                        f"sequence is not contiguous: expected {position},"
                        f" found {event.seq} (an entry was removed or reordered)"
                    ),
                )
            if event.prev_hash != expected_previous:
                return ChainVerification(
                    ok=False, checked=position - 1, broken_at=event.seq,
                    reason=(
                        "recorded predecessor does not match the entry before it:"
                        f" expected {expected_previous[:16]},"
                        f" found {event.prev_hash[:16]}"
                    ),
                )
            recomputed = compute_entry_hash(event)
            if recomputed != event.entry_hash:
                return ChainVerification(
                    ok=False, checked=position - 1, broken_at=event.seq,
                    reason=(
                        "entry contents do not match its hash:"
                        f" stored {event.entry_hash[:16]},"
                        f" recomputed {recomputed[:16]} (this entry was altered)"
                    ),
                )
            expected_previous = event.entry_hash

        return ChainVerification(ok=True, checked=len(rows))

    def read_for(self, entity_type: str, entity_id: str) -> list[AuditEvent]:
        rows = self.conn.execute(
            "SELECT * FROM audit_events WHERE entity_type = ? AND entity_id = ?"
            " ORDER BY id",
            (entity_type, entity_id),
        ).fetchall()
        return [_load(AuditEvent, r) for r in rows]


def repositories(conn: sqlite3.Connection) -> dict[str, Any]:
    """Every repository for a connection, in one call."""
    return {
        "areas": Repository(conn, ProcessArea),
        "controls": Repository(conn, ControlDefinition),
        "instances": Repository(conn, CheckInstance),
        "evidence": WriteOnceRepository(conn, Evidence),
        "submissions": Repository(conn, EvidenceSubmission),
        "findings": Repository(conn, Finding),
        "actions": Repository(conn, Action),
        "flags": Repository(conn, Flag),
        "exceptions": Repository(conn, ComplianceException),
        "audit": AuditLog(conn),
    }
