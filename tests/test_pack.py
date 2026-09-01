"""The pack must be reconstructable from the audit log and nothing else."""

import ast
from datetime import date
from pathlib import Path

import pytest

from sentinelops.db import connect
from sentinelops.pack import (
    KNOWN_ACTIONS,
    build,
    load_events,
    render_html,
    render_markdown,
    verify_chain,
)
from sentinelops.stages.assess import run as assess
from sentinelops.stages.flag import run as flag_stage
from sentinelops.stages.prescreen import run as prescreen
from sentinelops.stages.remediation import reassess_all
from sentinelops.stages.trigger import run_cycle
from sentinelops.synth import generate_corpus, seed_database

SRC = Path(__file__).resolve().parents[1] / "src" / "sentinelops"
PACK_MODULE = SRC / "pack.py"

#: Every table that records current state. The pack may read none of them.
LIVE_STATE_TABLES = (
    "process_areas",
    "control_definitions",
    "check_instances",
    "evidence_submissions",
    "evidence",
    "findings",
    "actions",
    "flags",
    "compliance_exceptions",
    "token_usage",
)

CYCLES = [date(2026, m, 28) for m in range(1, 13)] + [date(2027, 3, 31)]


@pytest.fixture(scope="module")
def corpus():
    return generate_corpus()


@pytest.fixture(scope="module")
def run_conn(corpus):
    conn = connect(":memory:")
    seed_database(conn, corpus)
    for as_of in CYCLES:
        run_cycle(conn, as_of)
        screen = prescreen(conn, as_of)
        if screen.to_assess:
            assess(conn, screen.to_assess, as_of)
        flag_stage(conn, as_of)
        reassess_all(conn, as_of)
    yield conn
    conn.close()


@pytest.fixture(scope="module")
def log_only(run_conn):
    """A database containing the audit log and *nothing else*.

    The strongest form of the constraint: if the pack can be built from this,
    it was genuinely built from the trail.
    """
    bare = connect(":memory:")
    rows = run_conn.execute("SELECT * FROM audit_events ORDER BY seq").fetchall()
    for row in rows:
        bare.execute(
            "INSERT INTO audit_events (ts, actor, owner, action, entity_type,"
            " entity_id, detail, seq, prev_hash, entry_hash)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (row["ts"], row["actor"], row["owner"], row["action"],
             row["entity_type"], row["entity_id"], row["detail"], row["seq"],
             row["prev_hash"], row["entry_hash"]),
        )
    bare.commit()
    yield bare
    bare.close()


@pytest.fixture(scope="module")
def pack(log_only):
    return build(
        load_events(log_only),
        period_start=date(2026, 1, 1),
        period_end=date(2026, 12, 31),
    )


# --- the constraint ---------------------------------------------------------

def _code_only(path: Path) -> str:
    source = path.read_text(encoding="utf-8")
    lines = source.splitlines()
    doc_lines: set[int] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef)):
            body = node.body
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                doc_lines.update(range(body[0].lineno, body[0].end_lineno + 1))
    return "\n".join(
        line for number, line in enumerate(lines, start=1)
        if number not in doc_lines and not line.strip().startswith("#")
    )


def test_the_generator_names_no_live_state_table():
    """No live table appears in SQL position.

    A bare substring scan is useless here — `evidence` is inside `evidence_hash`
    and `evidence_bound`, which are audit *detail keys*, not tables. What must
    not exist is a query against one.
    """
    import re

    code = _code_only(PACK_MODULE)
    for table in LIVE_STATE_TABLES:
        pattern = re.compile(
            r"(?:from|into|update|join)[ ]+" + table + r"(?![a-z_])",
            re.IGNORECASE,
        )
        assert not pattern.search(code), f"pack.py queries the {table} table"
    assert re.search(r"(?i)from[ ]+audit_events", code), "it must read the log"


def test_the_generator_imports_no_live_state_repository():
    """It may know what an AuditEvent is; it may not know how to load a Finding."""
    tree = ast.parse(PACK_MODULE.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported = {alias.name for alias in node.names}
            if node.module.endswith("repositories"):
                # only the chain primitives, never a repository or the factory
                assert imported <= {"GENESIS_HASH", "compute_entry_hash"}, imported
            assert "repositories" not in imported
            assert "Repository" not in imported
            assert "WriteOnceRepository" not in imported


def test_a_pack_builds_from_a_database_holding_only_the_log(pack, log_only):
    """Every live-state table is empty. The pack is still complete."""
    for table in LIVE_STATE_TABLES:
        count = log_only.execute(f"SELECT COUNT(*) c FROM {table}").fetchone()["c"]
        assert count == 0, f"{table} is not empty; the test proves nothing"

    assert pack.totals["events"] > 2000
    assert pack.totals["areas"] == 7
    assert pack.totals["controls"] == 14
    assert pack.totals["due"] == 343
    assert pack.coverage and pack.exceptions and pack.findings and pack.actions


def test_the_pack_matches_what_the_live_tables_say(pack, run_conn):
    """Reconstruction is not merely plausible — it agrees with the records."""
    from sentinelops.repositories import repositories

    repo = repositories(run_conn)
    assert pack.totals["due"] == len(repo["instances"].list())
    assert pack.totals["findings"] == len(repo["findings"].list())
    assert pack.totals["actions"] == len(repo["actions"].list())
    assert pack.totals["exceptions"] == len(repo["exceptions"].list())
    assert pack.totals["actions_resolved"] == len(
        [a for a in repo["actions"].list() if a.status == "resolved"]
    )


# --- the sections the pack must contain ------------------------------------

def test_the_cover_states_period_scope_and_source(pack):
    assert pack.period_start == date(2026, 1, 1)
    assert pack.period_end == date(2026, 12, 31)
    assert pack.scope
    assert pack.organisation
    assert pack.generated_at


def test_coverage_accounts_for_every_instance(pack):
    total = sum(r.due for r in pack.coverage)
    settled = sum(r.completed + r.waived + r.unexamined for r in pack.coverage)
    assert total == settled == pack.totals["due"]
    assert len({(r.area_id, r.control_id) for r in pack.coverage}) == len(pack.coverage)


def test_coverage_names_areas_and_controls_in_words(pack):
    """An auditor should not have to read identifiers."""
    for row in pack.coverage:
        assert row.area_name != row.area_id
        assert row.control_title != row.control_id
        assert row.frequency in ("monthly", "quarterly", "annual")


def test_the_exception_register_carries_rationale_and_approver(pack):
    assert len(pack.exceptions) == 4
    for exception in pack.exceptions:
        assert exception["approved_by"]
        assert len(exception["rationale"]) > 40
        assert exception["granted_at"] and exception["expires_at"]
        assert exception["status"] in ("active", "revoked", "lapsed", "expired")


def test_the_exception_register_shows_which_lapsed(pack):
    lapsed = [e for e in pack.exceptions if e["status"] == "lapsed"]
    assert lapsed
    for exception in lapsed:
        assert exception["lapsed_on"]
        assert exception["detected_on"]


def test_findings_carry_the_cited_excerpt_inline(pack):
    """The headline requirement: the log shows what was quoted, not how much."""
    cited = [f for f in pack.findings if f["cited_spans"]]
    assert len(cited) > 100
    for finding in cited:
        assert all(isinstance(span, str) and span.strip() for span in finding["cited_spans"])
    # and not merely a count masquerading as evidence
    assert not any(isinstance(f["cited_spans"], int) for f in pack.findings)


def test_findings_carry_verdict_confidence_and_review_flag(pack):
    for finding in pack.findings:
        assert finding["verdict"] in (
            "compliant", "partial", "gap", "insufficient_evidence"
        )
        assert finding["confidence"] != ""
        assert isinstance(finding["needs_human_review"], bool)
        assert finding["decided_by"]


def test_superseded_findings_are_shown_as_superseded(pack):
    superseded = [f for f in pack.findings if f["superseded_by"]]
    assert len(superseded) == pack.totals["superseded_findings"] == 6
    for finding in superseded:
        assert finding["is_current"] is False
        assert finding["verdict"] != "compliant"


def test_the_action_register_tells_the_whole_story(pack):
    """Two ways an action closes, and the register distinguishes them.

    Most close because somebody fixed the thing and the fix was re-assessed.
    One closes because the obligation was waived — no evidence was submitted,
    none was owed. Demanding remediation evidence of that one would be wrong.
    """
    resolved = [a for a in pack.actions if a["status"] == "resolved"]
    assert resolved

    for action in resolved:
        assert action["finding_id"], "what was found"
        assert action["owner"] and action["team"], "who owned it"
        assert action["raised_at"], "when raised"
        assert action["resolution_note"], "how closed"
        assert action["resolved_at"]

    remediated = [a for a in resolved if a["remediation_evidence"]]
    waived = [a for a in resolved if not a["remediation_evidence"]]
    assert len(remediated) == 6
    assert len(waived) == 1

    for action in remediated:
        assert action["reassessed_verdict"] == "compliant", "when re-assessed"
        assert "supersedes" in action["resolution_note"]
    for action in waived:
        assert "waived" in action["resolution_note"]
        assert "stands" in action["resolution_note"].lower()


def test_action_history_is_a_full_state_sequence(pack):
    resolved = next(a for a in pack.actions if a["status"] == "resolved")
    states = [state for _, state, _ in resolved["history"]]
    assert states == [
        "raised", "assigned", "in_progress", "remediation_submitted",
        "reassessed", "resolved",
    ]
    assert all(owner for _, _, owner in resolved["history"])


def test_the_chronological_trail_is_complete_and_ordered(pack):
    assert len(pack.events) == pack.totals["events"]
    assert [e.seq for e in pack.events] == sorted(e.seq for e in pack.events)
    for event in pack.events:
        assert event.ts and event.actor and event.owner


def test_every_event_type_is_one_the_pack_recognises(pack):
    assert pack.unknown_actions == [], (
        f"the pack does not know how to read {pack.unknown_actions}; a stage was "
        "added without teaching the pack about it"
    )


def test_the_chain_is_verified_from_the_events_themselves(pack):
    assert pack.chain["ok"] is True
    assert pack.chain["checked"] == pack.totals["events"]


def test_a_tampered_log_shows_as_tampered_in_the_pack(log_only):
    events = load_events(log_only)
    events[500].owner = "Somebody Else"
    result = verify_chain(events)
    assert result["ok"] is False
    assert result["broken_at"] == events[500].seq


# --- scoping ---------------------------------------------------------------

def _log_spanning_dates(conn):
    """A log whose entries are stamped across a year.

    Necessary because the pipeline stamps events with wall-clock time — when the
    entry was written — and a demo run writes a whole simulated year inside three
    seconds. Filtering by date is still a real requirement; this exercises it on
    a log that actually spans dates.
    """
    from datetime import datetime

    from sentinelops.repositories import repositories

    repo = repositories(conn)
    for month in range(1, 13):
        repo["audit"].append(
            actor="system", owner="R. Mehta", action="check_instance_created",
            entity_type="CheckInstance", entity_id=f"CHK-X-A-2026-{month:02d}",
            detail={"control_id": "CTRL-X", "control_title": "Control X",
                    "process_area_id": "AREA-A", "area_name": "Area A",
                    "period": f"2026-{month:02d}", "frequency": "monthly",
                    "due_date": "2026-01-15", "assigned_team": "Team A"},
            ts=datetime(2026, month, 15, 9, 0),
        )
    return conn


def test_the_pack_can_be_limited_to_a_date_range(conn):
    _log_spanning_dates(conn)
    early = load_events(conn, until=date(2026, 6, 30))
    everything = load_events(conn)

    assert 0 < len(early) < len(everything)
    assert len(early) == 6
    assert all(e.ts.date() <= date(2026, 6, 30) for e in early)

    late = load_events(conn, since=date(2026, 7, 1))
    assert len(late) == 6
    assert all(e.ts.date() >= date(2026, 7, 1) for e in late)


def test_a_scoped_pack_still_builds(conn):
    _log_spanning_dates(conn)
    scoped = build(
        load_events(conn, since=date(2026, 1, 1), until=date(2026, 6, 30)),
        period_start=date(2026, 1, 1), period_end=date(2026, 6, 30),
        scope="First half only",
    )
    assert scoped.totals["due"] == 6
    assert scoped.scope == "First half only"
    assert "First half only" in render_markdown(scoped)


# --- rendering --------------------------------------------------------------

def test_markdown_contains_every_required_section(pack):
    text = render_markdown(pack)
    for heading in ("# Audit Evidence Pack", "## 1. Coverage",
                    "## 2. Exception register", "## 3. Findings register",
                    "## 4. Action register", "## 5. Method note",
                    "## 6. Chronological trail"):
        assert heading in text
    assert "Cited evidence" in text
    assert "no current-state table" in text or "nothing else" in text


def test_html_is_self_contained_and_renders_the_same_facts(pack):
    page = render_html(pack)
    assert page.startswith("<!doctype html>")
    assert "<style>" in page and "http" not in page.split("<style>")[1][:400]
    for heading in ("1. Coverage", "2. Exception register", "3. Findings register",
                    "4. Action register", "5. Method note",
                    "6. Chronological trail"):
        assert heading in page
    assert "no current-state table was read" in page
    assert "VERIFIED" in page


def test_the_method_note_states_what_is_deterministic(pack):
    text = render_markdown(pack)
    assert "deterministic" in text.lower()
    assert "synthetic" in text.lower(), "the pack must scope its own evidence"
    assert "tamper" in text.lower()


def test_rendering_escapes_content_it_did_not_write(pack):
    """Cited spans are model output; they must not become markup."""
    page = render_html(pack)
    assert "<script" not in page.lower()
