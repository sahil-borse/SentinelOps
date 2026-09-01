"""Thin repository layer over sqlite3.

One repository per entity. Each is a plain class holding a connection; the
row <-> dataclass conversion is done by two module-level functions driven by a
per-entity field spec, so there is no inheritance hierarchy to reason about.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import fields
from datetime import date, datetime
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


class AuditLog:
    """Append-only audit trail.

    Deliberately exposes no update and no delete: the trail is evidence, and
    evidence that can be edited is not evidence. `tests/test_audit_append_only.py`
    asserts those methods are absent.
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
        event = AuditEvent(
            id=None,
            ts=ts or datetime.now(),
            actor=actor,  # type: ignore[arg-type]
            owner=owner,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            detail=detail or {},
        )
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
