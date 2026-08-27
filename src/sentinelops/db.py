"""SQLite connection and schema. Plain sqlite3, no ORM.

One table per entity of section 3, plus `token_usage` for the TokenMeter.
Columns are packed several to a line to keep the schema readable on one screen.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS process_areas (
    id TEXT PRIMARY KEY, name TEXT NOT NULL, owner_team TEXT NOT NULL,
    owner_name TEXT NOT NULL, attributes TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS control_definitions (
    id TEXT PRIMARY KEY, title TEXT NOT NULL, criteria_text TEXT NOT NULL,
    frequency TEXT NOT NULL, applies_when TEXT NOT NULL, evidence_kind TEXT NOT NULL,
    required_evidence_types TEXT NOT NULL, freshness_days INTEGER NOT NULL,
    severity_weight REAL NOT NULL, thresholds TEXT NOT NULL,
    grace_days INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS check_instances (
    id TEXT PRIMARY KEY, control_id TEXT NOT NULL REFERENCES control_definitions(id),
    process_area_id TEXT NOT NULL REFERENCES process_areas(id), period TEXT NOT NULL,
    due_date TEXT NOT NULL, status TEXT NOT NULL, assigned_team TEXT NOT NULL,
    owner_name TEXT NOT NULL, UNIQUE (control_id, process_area_id, period));
CREATE TABLE IF NOT EXISTS evidence (
    id TEXT PRIMARY KEY, check_instance_id TEXT NOT NULL REFERENCES check_instances(id),
    kind TEXT NOT NULL, doc_type TEXT NOT NULL, content TEXT NOT NULL,
    content_hash TEXT NOT NULL, submitted_at TEXT NOT NULL, author TEXT NOT NULL,
    is_remediation INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS evidence_submissions (
    id TEXT PRIMARY KEY, control_id TEXT NOT NULL REFERENCES control_definitions(id),
    process_area_id TEXT NOT NULL REFERENCES process_areas(id), period TEXT NOT NULL,
    kind TEXT NOT NULL, doc_type TEXT NOT NULL, content TEXT NOT NULL,
    content_hash TEXT NOT NULL, submitted_at TEXT NOT NULL, author TEXT NOT NULL,
    is_remediation INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS findings (
    id TEXT PRIMARY KEY, check_instance_id TEXT NOT NULL REFERENCES check_instances(id),
    verdict TEXT NOT NULL, confidence REAL NOT NULL, rationale TEXT NOT NULL,
    cited_spans TEXT NOT NULL, gaps TEXT NOT NULL, recommended_action TEXT NOT NULL,
    needs_human_review INTEGER NOT NULL, assessed_at TEXT,
    supersedes_finding_id TEXT REFERENCES findings(id));
CREATE TABLE IF NOT EXISTS actions (
    id TEXT PRIMARY KEY, finding_id TEXT NOT NULL REFERENCES findings(id),
    title TEXT NOT NULL, owner_team TEXT NOT NULL, owner_name TEXT NOT NULL,
    due_date TEXT NOT NULL, status TEXT NOT NULL, resolution_note TEXT,
    resolved_at TEXT);
CREATE TABLE IF NOT EXISTS compliance_exceptions (
    id TEXT PRIMARY KEY, control_id TEXT NOT NULL REFERENCES control_definitions(id),
    process_area_id TEXT NOT NULL REFERENCES process_areas(id),
    rationale TEXT NOT NULL, approved_by TEXT NOT NULL, granted_at TEXT NOT NULL,
    expires_at TEXT NOT NULL, status TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS audit_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, actor TEXT NOT NULL,
    owner TEXT NOT NULL, action TEXT NOT NULL, entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL, detail TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS token_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, tier TEXT NOT NULL,
    model TEXT NOT NULL, input_tokens INTEGER NOT NULL, output_tokens INTEGER NOT NULL,
    cached_tokens INTEGER NOT NULL, latency_ms INTEGER NOT NULL,
    cost_usd REAL NOT NULL, label TEXT NOT NULL);
"""


def connect(path: str | Path = "sentinelops.db") -> sqlite3.Connection:
    """Open a connection with the schema applied and foreign keys on."""
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    conn.commit()
    return conn
