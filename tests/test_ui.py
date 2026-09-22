"""The dashboard's logic, tested without Streamlit.

Every computation the screen performs lives in `view.py` and every action behind
a button in `service.py`, neither of which imports Streamlit — so the parts that
can be wrong are testable, and `app.py` is layout that either renders or does
not.
"""

import ast
import re
from datetime import date, datetime
from pathlib import Path

import pytest

from sentinelops.repositories import repositories
from sentinelops.synth import generate_corpus, seed_database
from sentinelops.ui import service, story, view

SRC = Path(__file__).resolve().parents[1] / "src" / "sentinelops"
SCREENS = sorted((SRC / "ui" / "screens").glob("*.py"))
LAYOUT = (SRC / "ui" / "app.py", SRC / "ui" / "shell.py", *SCREENS)


@pytest.fixture(scope="module")
def corpus():
    return generate_corpus()


@pytest.fixture()
def live(conn, corpus):
    """A demo database a few cycles in, as the screen would find it."""
    seed_database(conn, corpus)
    for month in (1, 2, 3, 4, 5):
        service.tick(conn, date(2026, month, 28))
    return conn


# --- the citation highlight, which the demo is built around ----------------

def test_a_cited_span_is_marked_in_the_source():
    content = "Line one.\nThe report records neither a reviewer nor a date.\nLine three."
    marked = view.highlight(content, ["The report records neither a reviewer nor a date."])
    assert "<mark>The report records neither a reviewer nor a date.</mark>" in marked
    assert "Line one." in marked and "Line three." in marked


def test_highlighting_survives_a_rewrapped_quotation():
    """A model that folds a line differently has still quoted it."""
    content = "All fourteen privileged\naccounts were reviewed line by line."
    marked = view.highlight(
        content, ["All fourteen privileged accounts were reviewed line by line."]
    )
    assert "<mark>" in marked
    assert marked.count("<mark>") == 1


def test_a_reworded_quotation_is_not_marked():
    content = "All accounts were reviewed line by line."
    assert "<mark>" not in view.highlight(content, ["All accounts were checked"])


def test_overlapping_spans_do_not_nest():
    content = "the quick brown fox jumps"
    marked = view.highlight(content, ["quick brown fox", "brown fox jumps"])
    assert marked.count("<mark>") == 1, "overlaps merge into one region"
    assert "<mark>quick brown fox jumps</mark>" in marked


def test_several_separate_spans_are_all_marked():
    content = "First fact here.\nSomething else.\nSecond fact here."
    marked = view.highlight(content, ["First fact here.", "Second fact here."])
    assert marked.count("<mark>") == 2


def test_the_document_and_the_citation_are_both_escaped():
    """Evidence is submitted input and spans are model output. Neither is markup."""
    content = "<script>alert(1)</script> and a <b>bold</b> claim"
    marked = view.highlight(content, ["<script>alert(1)</script>"])
    assert "<script>" not in marked
    assert "&lt;script&gt;" in marked
    assert "<mark>" in marked


def test_a_document_with_no_citations_still_renders():
    marked = view.highlight("Just a document.", [])
    assert "Just a document." in marked
    assert "<mark>" not in marked


def test_unmatched_spans_are_reported_not_hidden():
    content = "The review was completed."
    assert view.unmatched_spans(content, ["The review was completed."]) == []
    assert view.unmatched_spans(content, ["Something invented"]) == ["Something invented"]


def test_every_citation_the_screen_shows_resolves_in_the_document_it_shows(live):
    """The panel pairs the *current* finding with the *latest* evidence.

    A superseded finding cites the document it was drawn from, not the
    remediation that replaced it, so pairing every finding with the latest
    evidence would be comparing the wrong two things. What matters is that the
    pair the screen actually renders always lines up.
    """
    checked = 0
    for instance_id in view.assessable_instances(live):
        detail = view.finding_detail(live, instance_id)
        finding, evidence = detail["finding"], detail["evidence"]
        if evidence is None or not finding.cited_spans:
            continue
        assert view.unmatched_spans(evidence.content, finding.cited_spans) == [], (
            f"{finding.id} cites text absent from {evidence.id}"
        )
        checked += 1
    assert checked > 20


def test_a_superseded_citation_still_resolves_in_its_own_source(live):
    """Nothing is orphaned: every citation resolves in some filed document."""
    repo = repositories(live)
    for finding in repo["assessments"].list():
        if not finding.cited_spans:
            continue
        documents = repo["evidence"].list(check_instance_id=finding.check_instance_id)
        assert any(
            view.unmatched_spans(evidence.content, finding.cited_spans) == []
            for evidence in documents
        ), f"{finding.id} cites text in none of its evidence"


# --- the panels -------------------------------------------------------------

def test_status_by_area_accounts_for_every_check(live):
    rows = view.status_by_area(live)
    assert len(rows) == 10
    total = sum(r.due for r in rows)
    assert total == len(repositories(live)["instances"].list())
    for row in rows:
        assert row.due == row.assessed + row.overdue + row.waived + row.pending
        assert row.name and row.team and row.owner


def test_areas_are_ordered_worst_first(live):
    severities = [row.worst_severity for row in view.status_by_area(live)]
    assert severities == sorted(severities, reverse=True)


def test_the_overdue_queue_is_worst_first(live):
    queue = view.overdue_queue(live, date(2026, 5, 28))
    assert queue
    assert [r["severity"] for r in queue] == sorted(
        (r["severity"] for r in queue), reverse=True
    )
    for row in queue:
        assert row["category"] in ("gap", "overdue")
        assert row["owner"] and row["team"]
        assert 0 <= row["escalation"] <= 2


def test_open_findings_carry_owner_target_severity_and_chase_count(live):
    rows = view.open_actions(live)
    assert rows
    for row in rows:
        assert row["owner"] and row["team"] and row["due"]
        assert row["severity"] in ("Major", "Minor", "Observation")
        assert row["chased"] >= 0
        assert row["finding"]
    assert [r["due"] for r in rows] == sorted(r["due"] for r in rows)


def test_closed_findings_name_the_auditor_who_closed_them(live):
    for row in view.resolved_actions(live):
        assert row["closed_by"], "a closure without a name is not a decision"
        assert row["note"]


def test_finding_detail_returns_the_current_finding_not_a_superseded_one(live):
    repo = repositories(live)
    findings = repo["assessments"].list()
    superseded = {f.supersedes_assessment_id for f in findings if f.supersedes_assessment_id}
    for instance_id in view.assessable_instances(live)[:25]:
        detail = view.finding_detail(live, instance_id)
        assert detail["finding"].id not in superseded


def test_finding_detail_is_none_for_an_unassessed_check(live):
    assert view.finding_detail(live, "CHK-NOT-A-THING-2026-Q1") is None


def test_the_timeline_covers_the_whole_check(live):
    instance_id = next(
        i for i in view.assessable_instances(live) if "CHANGED-PROCESS" in i
    )
    rows = view.timeline(live, instance_id)
    events = [r["event"] for r in rows]
    assert "check_instance_created" in events
    assert any(e == "assessment_recorded" for e in events)
    assert [r["seq"] for r in rows] == sorted(r["seq"] for r in rows)
    for row in rows:
        assert row["actor"] in ("system", "ai", "user")
        assert row["owner"]


def test_the_token_meter_matches_the_usage_table(live):
    meter = view.token_meter(live)
    row = live.execute(
        "SELECT COUNT(*) c, COALESCE(SUM(input_tokens),0) i FROM token_usage"
    ).fetchone()
    assert meter["calls"] == row["c"]
    assert meter["input_tokens"] == row["i"]
    assert 0 < meter["zero_model_share"] < 1


# --- the buttons ------------------------------------------------------------

def test_a_tick_runs_the_whole_pipeline(conn, corpus):
    seed_database(conn, corpus)
    result = service.tick(conn, date(2026, 4, 28))

    assert result.created > 0
    assert result.screened > 0
    assert result.resolved_by_rule > 0
    assert result.assessed > 0
    assert result.flags > 0
    assert result.findings_raised > 0
    assert "checks raised" in result.summary()


def test_a_tick_uses_the_same_entry_points_as_a_scheduler():
    """The demo must not be a second implementation of the pipeline."""
    source = (SRC / "ui" / "service.py").read_text(encoding="utf-8")
    for entry in ("run_cycle", "prescreen", "assess", "flag_stage", "reassess_all"):
        assert entry in source


def test_advancing_the_calendar_moves_the_simulated_date(conn, corpus):
    seed_database(conn, corpus)
    service.tick(conn, date(2026, 2, 28))
    assert service.current_date(conn) == date(2026, 2, 28)

    service.advance(conn, 30)
    assert service.current_date(conn) == date(2026, 3, 30)


def test_the_calendar_starts_somewhere_sensible_before_any_cycle(conn, corpus):
    seed_database(conn, corpus)
    from sentinelops.synth.calendar import CORPUS_WINDOW

    assert service.current_date(conn) == service.start_date(conn)
    assert service.start_date(conn) == CORPUS_WINDOW.start.replace(day=28)


def test_uploaded_evidence_goes_through_the_normal_path(live):
    """An uploaded document is not a special case anywhere downstream."""
    repo = repositories(live)
    target = next(
        i.id for i in repo["instances"].list()
        if i.status == "assessed"
        and repo["assessments"].list(check_instance_id=i.id)[0].verdict != "compliant"
        and repo["controls"].get(i.control_id).evidence_kind == "document"
    )
    control = repo["controls"].get(repo["instances"].get(target).control_id)

    submission = service.submit_evidence(
        live, instance_id=target, filename="fix.txt",
        content=(
            f"{control.title} - remediation\n\n"
            "1. All privileged accounts were listed from the IAM export and "
            "reviewed line by line.\n"
            "2. Reviewer: R. Mehta. Review completed and countersigned.\n"
            "3. All accounts no longer required were revoked, with tickets "
            "attached.\n"
        ),
        author="R. Mehta", doc_type=control.required_evidence_types[0],
        as_of=date(2026, 6, 28), is_remediation=True,
    )

    assert submission.id.startswith("SUB-UI-")
    assert submission.is_remediation
    assert submission.content_hash
    stored = repo["inbound"].get(submission.id)
    assert stored == submission

    outcome = service.reassess(live, target, date(2026, 6, 28))
    assert outcome.new_assessment_id
    assert outcome.superseded_assessment_id
    new = repo["assessments"].get(outcome.new_assessment_id)
    assert new.supersedes_assessment_id == outcome.superseded_assessment_id


def test_an_upload_is_recorded_in_the_audit_trail(live):
    repo = repositories(live)
    target = view.instances_awaiting_evidence(live)[0]
    service.submit_evidence(
        live, instance_id=target, filename="note.txt", content="Some evidence.",
        author="D. Ferreira", doc_type=service.doc_types_for(live, target)[0],
        as_of=date(2026, 6, 28),
    )
    event = [
        e for e in repo["audit"].read_for("CheckInstance", target)
        if e.action == "evidence_uploaded"
    ][-1]
    assert event.actor_kind == "user"
    assert event.owner == "D. Ferreira"
    assert event.detail["filename"] == "note.txt"
    assert event.detail["source"] == "dashboard upload"


def test_uploading_against_an_unknown_check_is_refused(live):
    with pytest.raises(ValueError, match="no such check instance"):
        service.submit_evidence(
            live, instance_id="CHK-NOPE", filename="x.txt", content="x",
            author="a", doc_type="report", as_of=date(2026, 6, 28),
        )


def test_the_wrong_document_type_can_be_chosen_on_purpose(live):
    """Offering only the right type would hide the wrong-type rule."""
    target = view.instances_awaiting_evidence(live)[0]
    options = service.doc_types_for(live, target)
    control = repositories(live)["controls"].get(
        repositories(live)["instances"].get(target).control_id
    )
    assert options[0] in control.required_evidence_types
    assert len(options) > len(control.required_evidence_types)


def test_generating_the_pack_writes_both_renderings(live, tmp_path, monkeypatch):
    monkeypatch.setattr(service, "PACK_DIR", tmp_path)
    from sentinelops.pack import pack_filename

    start, end = service.pack_period(live)
    pack, markdown, page = service.generate_pack(
        live, period_start=start, period_end=end, scope="test scope",
    )
    assert pack.totals["events"] > 100
    name = pack_filename(start, end)
    assert (tmp_path / f"{name}.md").exists()
    assert (tmp_path / f"{name}.html").exists()
    assert page.startswith("<!doctype html>")
    assert "test scope" in markdown


def test_the_verify_button_reports_an_intact_chain(live):
    result = service.verify_chain(live)
    assert result.ok
    assert result.checked > 100


def test_the_verify_button_reports_a_broken_chain(live):
    live.execute("UPDATE audit_events SET owner = 'Nobody' WHERE seq = 20")
    live.commit()
    result = service.verify_chain(live)
    assert not result.ok
    assert result.broken_at == 20


def test_counts_agree_with_the_records(live):
    totals = service.counts(live)
    repo = repositories(live)
    assert totals["instances"] == len(repo["instances"].list())
    assert totals["actions_open"] + totals["actions_resolved"] == len(
        repo["findings"].list()
    )
    assert totals["audit_events"] == len(repo["audit"].read_all())


# --- the app file itself ----------------------------------------------------

def test_the_app_is_layout_and_nothing_else():
    """If logic creeps into the pages it stops being tested. Keep them thin.

    The entry point and every screen define no functions at all; the shared
    panels live in `shell.py`, and every computation in `view.py` or `service.py`.
    """
    for path in (SRC / "ui" / "app.py", *SCREENS):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        functions = [n for n in ast.walk(tree)
                     if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        assert not functions, f"{path.name}: computation belongs in view.py or service.py"


def test_neither_logic_module_imports_streamlit():
    for name in ("view.py", "service.py"):
        source = (SRC / "ui" / name).read_text(encoding="utf-8")
        assert "streamlit" not in source, f"{name} must stay testable"


def test_every_required_control_is_present_on_the_screen():
    """The controls the slices named, each still wired up somewhere on a page."""
    source = " ".join(
        path.read_text(encoding="utf-8") for path in (*LAYOUT, SRC / "ui" / "view.py")
    )
    for control in (
        "Compliance status by process area",
        "Overdue and escalation queue",
        "cited spans highlighted",
        "Open findings",
        "Audit timeline",
        "Run cycle now",
        "Re-assess this check now",
        "Submit evidence",
        "Generate audit pack",
        "Verify audit chain",
        "Cost",
        "+1 month",
        "Chronic findings",
        "Review queue",
        "Prioritisation brief",
        "Reset scenario",
        "Jump to next event",
    ):
        assert control in source, f"missing from the dashboard: {control}"


def test_chronic_findings_are_the_open_ones_more_than_a_year_past_target(conn, corpus):
    """The PA/InfoSec alert: its own list, from the record, at the current date."""
    from sentinelops.analytics import CHRONIC_DAYS
    from sentinelops.stages.trigger import run_cycle
    from sentinelops.synth.calendar import SIMULATED_TODAY

    seed_database(conn, corpus)
    run_cycle(conn, SIMULATED_TODAY)
    assert service.current_date(conn) == SIMULATED_TODAY

    alert = service.chronic_findings(conn)
    assert alert["threshold_days"] == CHRONIC_DAYS == 365
    expected = sorted(
        f.id for f in repositories(conn)["findings"].list()
        if f.status == "open"
        and (SIMULATED_TODAY - f.target_date).days > CHRONIC_DAYS
    )
    assert expected, "the corpus has a finding open more than a year at today"
    assert sorted(r["id"] for r in alert["findings"]) == expected
    days = [r["days_past_target"] for r in alert["findings"]]
    assert days == sorted(days, reverse=True)
    assert all(r["owner"] for r in alert["findings"])


# --- the app actually renders ----------------------------------------------

@pytest.fixture()
def app_cache_cleared():
    """Streamlit's resource cache is process-global.

    Without this, the second headless run reuses the first one's cached
    connection and quietly operates on the wrong database. That is correct
    behaviour for a deployed app — one process, one connection — and a hazard
    only for tests that stand several apps up in a row.
    """
    import streamlit as st

    st.cache_resource.clear()
    yield
    st.cache_resource.clear()

def _dashboard(tmp_path, monkeypatch, *, timeout=300):
    """The real entry point, headless, on a demo database of its own."""
    from streamlit.testing.v1 import AppTest

    monkeypatch.setattr(service, "DB_PATH", tmp_path / "demo.db")
    app = AppTest.from_file(str(SRC / "ui" / "app.py"), default_timeout=timeout)
    app.run()
    return app


def _act_as(app, identity_id):
    app.sidebar.selectbox(key="acting_as").set_value(identity_id).run()


def _open(app, page):
    app.switch_page(f"screens/{page}.py").run()
    assert not app.exception, [e.message for e in app.exception]


def _buttons(app):
    return {button.label for button in app.button}


def _open_check_form(app):
    """The scheduled-check form lives in a modal now, opened by its own button."""
    next(b for b in app.button
         if b.label == "File evidence for a scheduled check").click().run()
    assert not app.exception, [e.message for e in app.exception]


def _owner_with_checks(tmp_path):
    """A unit owner whose unit owes evidence on the demo database right now."""
    db = service.open_database(tmp_path / "demo.db")
    try:
        today = service.current_date(db)
        return next(
            choice["id"] for choice in view.identity_choices(db)
            if choice["role"] == "unit_owner"
            and view.owner_checks(db, choice["unit"], today)
        )
    finally:
        db.close()


def test_the_dashboard_renders_end_to_end(tmp_path, monkeypatch, app_cache_cleared):
    """Runs the real entry point headlessly, and every page PA/InfoSec can reach.

    The logic modules are tested above; this is the one that would catch a
    layout call that raises — a mistyped column count, a metric handed the
    wrong type — which no amount of testing `view.py` would find. Slice 17 made
    the dashboard multi-page, so each panel this used to find on one long page
    is now checked on the page it lives on.
    """
    app = _dashboard(tmp_path, monkeypatch, timeout=120)
    assert not app.exception, [str(e) for e in app.exception]

    shown = " ".join(m.value for m in app.markdown)
    assert "SentinelOps" in shown
    assert "Simulated date" in shown
    for spend in ("Model spend", "Model calls", "Tokens"):
        assert spend not in shown, "model spend lives on /cost, not the working screens"

    # PA/InfoSec land on Today: what needs them, first
    headings = [element.value for element in app.subheader]
    for expected in ("Review queue", "Chronic findings",
                     "Overdue and escalation queue", "Prioritisation brief"):
        assert expected in headings
    for expected in ("Run cycle now", "+1 day", "+1 week", "+1 month",
                     "Reset scenario", "Jump to next event", "Write the brief"):
        assert expected in _buttons(app)

    for page, heading in (
        ("findings", "On record"),
        ("schedule", "Compliance activities due"),
        ("portfolio", "Compliance status by process area"),
        ("recurrence", "This has happened before"),
        ("audit_trail", "Verify the chain"),
    ):
        _open(app, page)
        assert heading in [e.value for e in app.subheader], page
    assert {"Verify audit chain", "Generate audit pack"} <= _buttons(app)

    _open(app, "inbox")
    assert "Inbox" in " ".join(m.value for m in app.markdown)

    # reachable by its address, though no page links to it
    _open(app, "cost")
    assert "By what made the call" in [e.value for e in app.subheader]

    # the walkthrough, with step one offered first on a fresh demo
    _open(app, "walkthrough")
    assert "GUIDED WALKTHROUGH" in " ".join(m.value for m in app.markdown)
    assert story.STEPS[0].button in _buttons(app)
    assert story.STEPS[0].title in [e.value for e in app.subheader]


def test_the_run_cycle_button_actually_runs_a_cycle(tmp_path, monkeypatch, app_cache_cleared):
    """And the controls that only exist once there is something to act on appear."""
    app = _dashboard(tmp_path, monkeypatch)

    before = service.counts(service.open_database(tmp_path / "demo.db"))["instances"]
    next(b for b in app.button if b.label == "Run cycle now").click().run()
    assert not app.exception, [str(e) for e in app.exception]

    after = service.counts(service.open_database(tmp_path / "demo.db"))["instances"]
    assert after > before, "pressing the button raised checks"
    assert any("checks raised" in element.value for element in app.success)

    # the upload form exists once checks do, for the unit that owes the evidence
    _act_as(app, _owner_with_checks(tmp_path))
    _open(app, "owner_detail")
    assert "Submit evidence" not in _buttons(app), "the form is not inline any more"
    _open_check_form(app)
    assert "Submit evidence" in _buttons(app)
    assert any(u.label == "Evidence file" for u in app.get("file_uploader"))

    # The re-assess control lives in a finding raised from a check, so it exists
    # once a check has been *judged* and failed. On the first cycle, 28 January,
    # nothing can have been: no period has closed. A month on, January's
    # evidence has been filed and assessed.
    next(b for b in app.button if b.label == "+1 month").click().run()
    assert not app.exception, [str(e) for e in app.exception]
    db = service.open_database(tmp_path / "demo.db")
    try:
        finding = next((f for f in repositories(db)["findings"].list()
                        if f.check_instance_id), None)
        auditor = service.default_identity(db)
    finally:
        db.close()
    assert finding is not None, "a month of judged checks raises an activity finding"
    _act_as(app, auditor)
    app.session_state["selected_finding"] = finding.id
    _open(app, "findings")
    assert "Re-assess this check now" in _buttons(app)


def test_the_verify_button_reports_on_screen(tmp_path, monkeypatch, app_cache_cleared):
    app = _dashboard(tmp_path, monkeypatch, timeout=180)
    _open(app, "audit_trail")
    next(b for b in app.button if b.label == "Verify audit chain").click().run()

    assert not app.exception, [str(e) for e in app.exception]
    assert any("Chain intact" in element.value for element in app.success)


# --- the guided walkthrough -------------------------------------------------

def test_the_walkthrough_starts_at_step_one_on_a_fresh_demo(conn, corpus):
    seed_database(conn, corpus)
    assert story.current_step(conn) == 0
    assert story.STEPS[0].key == "raise"


def test_the_walkthrough_advances_as_the_work_actually_happens(conn, corpus):
    """Progress is read from the database, not from a click counter.

    Reload the page mid-demo and it picks up where the *data* is, not where a
    session variable thinks it is.
    """
    seed_database(conn, corpus)
    assert story.current_step(conn) == 0

    story.run(conn, "raise")
    assert story.current_step(conn) == 1

    story.run(conn, "time")
    assert story.current_step(conn) >= 2


def test_step_one_explains_why_areas_differ(conn, corpus):
    seed_database(conn, corpus)
    outcome = story.run(conn, "raise")
    joined = " ".join(outcome.detail)
    assert "checks raised automatically" in joined
    assert "in scope for" in joined, "it must say the areas differ, and by how much"


def test_step_two_reports_escalations_that_actually_happened(live):
    """It must describe the ladder that fires, not the one that does not.

    A check with no evidence is settled by the pre-screen in the same tick that
    marks it overdue, so it never climbs the check-level ladder. The action
    raised from it escalates instead, on its own clock — which is what the
    narrative says.
    """
    outcome = story.run(live, "time")
    joined = " ".join(outcome.detail)
    assert "outstanding" in joined
    assert "escalated" in joined and "PA/InfoSec" in joined

    escalated = {
        e.entity_id for e in repositories(live)["audit"].read_all()
        if e.action == "finding_escalated"
    }
    assert escalated, "the claim in the narrative must be true of the data"
    assert str(len(escalated)) in joined


def test_step_three_finds_something_worth_showing(live):
    target = story.pick_near_miss(live)
    assert target is not None
    detail = view.finding_detail(live, target)
    assert detail["finding"].decided_by == "s3_model"
    assert detail["finding"].verdict in ("gap", "partial")
    assert detail["finding"].cited_spans
    assert detail["evidence"] is not None

    outcome = story.run(live, "nearmiss")
    assert outcome.focus == target
    assert "highlighted" in " ".join(outcome.detail)


def test_step_four_quotes_the_real_meter(live):
    outcome = story.run(live, "cost")
    meter = view.token_meter(live)
    assert f"{meter['zero_model_share']:.0%}" in outcome.headline
    assert str(meter["calls"]) in " ".join(outcome.detail)


def test_step_five_actually_closes_the_loop(live):
    target = story.pick_fix_target(live)
    assert target is not None
    before = view.finding_detail(live, target)["finding"]

    outcome = story.run(live, "fix")

    after = view.finding_detail(live, outcome.focus)["finding"]
    assert after.id != before.id
    assert after.supersedes_assessment_id == before.id
    assert "same" in " ".join(outcome.detail)


def test_the_correction_it_writes_is_judged_not_waved_through(live):
    """The generated document goes through the real assessment, not a shortcut."""
    target = story.pick_fix_target(live)
    text = story.remediation_text(live, target)
    control = repositories(live)["controls"].get(
        repositories(live)["instances"].get(target).control_id
    )
    for clause in control.criteria_text.splitlines():
        assert clause.split(". ", 1)[-1].strip() in text

    story.run(live, "fix")
    finding = view.finding_detail(live, target)["finding"]
    assert finding.decided_by in ("s3_model", "structured_threshold",
                                  "wrong_evidence_type", "stale_evidence")
    assert finding.cited_spans or finding.decided_by != "s3_model"


def test_step_six_verifies_and_builds(live, tmp_path, monkeypatch):
    monkeypatch.setattr(service, "PACK_DIR", tmp_path)
    outcome = story.run(live, "prove")
    assert "verified" in outcome.headline
    assert outcome.warning is None
    from sentinelops.pack import pack_filename

    assert (tmp_path / f"{pack_filename(*service.pack_period(live))}.html").exists()


def test_step_six_reports_a_tampered_record(live, tmp_path, monkeypatch):
    monkeypatch.setattr(service, "PACK_DIR", tmp_path)
    live.execute("UPDATE audit_events SET owner = 'Nobody' WHERE seq = 12")
    live.commit()
    outcome = story.run(live, "prove")
    assert outcome.warning
    assert "tampered" in outcome.headline


def test_every_step_has_a_reason_a_person_would_recognise(live):
    """Read through `why_for`, the way the screen does.

    A step's copy may be a callable where it quotes a number — "fourteen
    controls across seven business areas" was written when there were seven,
    survived a roster change to ten and was still on screen being wrong. Testing
    the raw attribute would skip exactly the steps that count.
    """
    for step in story.STEPS:
        why = story.why_for(step, live)
        assert len(why) > 120, f"{step.key} needs a real explanation"
        assert step.button and step.title
        # no identifiers or field names leaking into the narrative
        for jargon in ("decided_by", "CHK-", "CTRL-", "AREA-", "s3_model",
                       "prescreen", "supersedes_assessment_id"):
            assert jargon not in why, f"{step.key} leaks jargon: {jargon}"


def test_copy_that_quotes_a_number_counts_it(live):
    """The counts in the narrative match the register, not a memory of it."""
    from sentinelops.repositories import repositories

    repo = repositories(live)
    why = story.why_for(story.STEPS[0], live)
    assert str(len(repo["controls"].list())) in why
    assert str(len(repo["units"].list())) in why


def test_an_unknown_step_is_refused(live):
    with pytest.raises(ValueError, match="unknown step"):
        story.run(live, "not-a-step")


def test_submitting_evidence_reports_back_on_screen(tmp_path, monkeypatch,
                                                    app_cache_cleared):
    """The bug this test exists for: it worked, and said nothing.

    `st.success(...)` written immediately before `st.rerun()` is discarded by
    the rerun, so a successful upload looked like a dead button. Messages are
    now parked in session state and rendered on the way back.
    """
    app = _dashboard(tmp_path, monkeypatch)
    next(b for b in app.button if b.label == "Run cycle now").click().run()
    _act_as(app, _owner_with_checks(tmp_path))
    _open(app, "owner_detail")
    _open_check_form(app)

    next(t for t in app.text_area if t.label == "…or paste the evidence directly").set_value(
        "Quarterly review - corrected resubmission\n\n"
        "1. Every privileged account was listed and reviewed line by line.\n"
        "2. Reviewer recorded and countersigned.\n"
        "3. Accounts no longer required were revoked, with tickets attached.\n"
    ).run()
    next(b for b in app.button if b.label == "Submit evidence").click().run()

    assert not app.exception, [str(e) for e in app.exception]
    said = " ".join(element.value for element in app.success)
    assert "SUB-UI-" in said, "the screen must confirm what was filed"
    assert "bytes" in said
    assert "Re-checked" in said or "Not re-checked" in said


def test_submitting_nothing_says_so(tmp_path, monkeypatch, app_cache_cleared):
    app = _dashboard(tmp_path, monkeypatch)
    next(b for b in app.button if b.label == "Run cycle now").click().run()
    _act_as(app, _owner_with_checks(tmp_path))
    _open(app, "owner_detail")
    _open_check_form(app)
    next(b for b in app.button if b.label == "Submit evidence").click().run()

    assert not app.exception, [str(e) for e in app.exception]
    assert any("Nothing to submit" in element.value for element in app.error)


def test_the_acting_identity_survives_an_in_page_switch():
    """The identity is session state, not the selectbox's, and here is why.

    My findings calls `st.switch_page` part-way through a run when an owner
    picks a row. A value belonging to a widget key can be cleaned up by that
    switch: the identity fell back to the default auditor, and the owner's
    Finding detail page — not one of the auditor's — bounced her to Today.
    Writing the key back to itself each run makes it ordinary session state,
    which the switch leaves alone.

    Checked as source because the harness switches pages by a different route
    and never reproduced it; the browser did.
    """
    source = (SRC / "ui" / "app.py").read_text(encoding="utf-8")
    assert 'st.session_state["acting_as"] = st.session_state["acting_as"]' in source


def test_a_finding_opens_over_the_list_and_closes_by_its_own_button(
    tmp_path, monkeypatch, app_cache_cleared
):
    """The finding is read in a modal over the list, not scrolled to below it.

    Its own Close clears the selection *and* resets the table: a row selection
    that survived the rerun would put the finding straight back on screen.
    """
    app = _dashboard(tmp_path, monkeypatch)
    next(b for b in app.button if b.label == "Run cycle now").click().run()
    db = service.open_database(tmp_path / "demo.db")
    try:
        finding = repositories(db)["findings"].list()[0]
    finally:
        db.close()

    app.session_state["selected_finding"] = finding.id
    _open(app, "findings")
    assert finding.id in " ".join(m.value for m in app.markdown), "it opened"
    assert "Close" in _buttons(app)

    version = app.session_state["findings_table_version"] if (
        "findings_table_version" in app.session_state) else 0
    next(b for b in app.button if b.label == "Close").click().run()
    assert not app.exception, [e.message for e in app.exception]
    assert "selected_finding" not in app.session_state, "Close forgets the selection"
    assert app.session_state["findings_table_version"] == version + 1, (
        "and resets the table, so the row does not reopen it"
    )
    assert "Close" not in _buttons(app)


def test_both_evidence_forms_open_in_modals_from_labelled_buttons(
    tmp_path, monkeypatch, app_cache_cleared
):
    """Two forms, two destinations, and neither sits inline to be mistaken for the other.

    Evidence answering a finding goes to an auditor; evidence for a scheduled
    check goes through the pre-screen and assessment. They used to be two
    near-identical forms on one page. Each now opens from its own labelled
    button, and the scheduled one is reachable from My findings too, where an
    owner looks first.
    """
    app = _dashboard(tmp_path, monkeypatch)
    next(b for b in app.button if b.label == "Run cycle now").click().run()
    _act_as(app, _owner_with_checks(tmp_path))

    _open(app, "my_findings")
    assert "Submit evidence" not in _buttons(app), "no form inline on My findings"
    _open_check_form(app)
    assert "Submit evidence" in _buttons(app), "the button opens the form"
    next(b for b in app.button if b.label == "Cancel").click().run()
    assert not app.exception, [e.message for e in app.exception]
    assert "Submit evidence" not in _buttons(app), "Cancel closes it"

    _open(app, "owner_detail")
    labels = _buttons(app)
    assert "Submit evidence" not in labels and "File evidence round" not in labels, (
        "neither form sits inline on Finding detail"
    )
    assert "File evidence for a scheduled check" in labels


def test_no_message_is_written_immediately_before_a_rerun():
    """The class of bug, not just the instance.

    Anything printed on the line before `st.rerun()` never reaches the screen.
    Park it in session state instead. Checked across every page.
    """
    for path in LAYOUT:
        source = path.read_text(encoding="utf-8").splitlines()
        for number, line in enumerate(source):
            if line.strip() != "st.rerun()":
                continue
            window = " ".join(source[max(0, number - 3):number])
            for painter in ("st.success(", "st.error(", "st.warning(", "st.info("):
                assert painter not in window, (
                    f"{path.name} line {number + 1}: {painter} just before "
                    f"st.rerun() is discarded"
                )


# --- long documents must not become an endless scroll ----------------------

LONG = (
    ("preamble text. " * 500)
    + "\nThe reviewer field was left blank.\n"
    + ("appendix text. " * 800)
)


def test_the_page_height_does_not_depend_on_the_document(live):
    """The whole point: a fifty-page upload occupies the same space as a note."""
    short = view.document_frame("A short report.", [])
    long_one = view.document_frame(LONG, ["The reviewer field was left blank."])
    assert short.height == long_one.height == view.COLLAPSED_HEIGHT


def test_show_more_makes_the_panel_taller_not_the_page_longer():
    collapsed = view.document_frame(LONG, [])
    expanded = view.document_frame(LONG, [], expanded=True)
    assert expanded.height > collapsed.height
    assert expanded.height == view.EXPANDED_HEIGHT
    assert expanded.total_chars == collapsed.total_chars, "same document, taller box"


def test_the_whole_document_is_present_in_both_states():
    """Nothing is elided away — it is all there, just inside a scrollbox."""
    for expanded in (False, True):
        frame = view.document_frame(LONG, ["The reviewer field was left blank."],
                                    expanded=expanded)
        assert "preamble text." in frame.html
        assert "appendix text." in frame.html
        assert "<mark>The reviewer field was left blank.</mark>" in frame.html


def test_the_frame_scrolls_to_the_first_citation():
    """A long document should arrive at its highlight, not at page one — and
    move only its own frame.

    It used `scrollIntoView`, which scrolls every scrollable ancestor. In a
    same-origin frame that includes the dashboard, and slice 17's landing page
    opened scrolled halfway down, onto the first document in the review queue.
    """
    frame = view.document_frame(LONG, ["The reviewer field was left blank."])
    assert "querySelector('mark')" in frame.html
    assert "window.scrollTo" in frame.html
    assert "scrollIntoView" not in frame.html


def test_the_frame_is_a_self_contained_page():
    frame = view.document_frame(LONG, [])
    assert frame.html.startswith("<!doctype html>")
    assert "<style>" in frame.html
    assert "overflow" not in frame.html, "the iframe scrolls, not an inner div"


def test_the_caption_says_what_is_on_screen():
    frame = view.document_frame(LONG, ["The reviewer field was left blank."])
    caption = frame.caption()
    assert f"{frame.total_chars:,} characters" in caption
    assert "1 cited passage highlighted" in caption
    assert "scroll inside the panel" in caption


def test_a_document_with_no_citation_still_renders_whole():
    frame = view.document_frame(LONG, [])
    assert frame.passages == 0
    assert "<mark>" not in frame.html
    assert "appendix text." in frame.html


def test_the_frame_escapes_everything():
    content = ("x " * 400) + "<script>alert(1)</script>" + ("y " * 400)
    frame = view.document_frame(content, ["<script>alert(1)</script>"])
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in frame.html
    # the only real script tag is the one the frame itself adds to scroll
    assert frame.html.count("<script>") == 1


def test_an_absurd_upload_is_capped_before_the_browser_suffers():
    enormous = "line of text. " * 40_000
    frame = view.document_frame(enormous, [])
    assert frame.capped
    assert "further characters" in frame.html
    assert len(frame.html) < view.MAX_RENDERED_CHARS * 1.4
    assert "first 200,000 shown" in frame.caption()


def test_a_very_large_upload_stays_readable(live):
    """An uploaded chat export should not produce a page metres long."""
    # One that has already fallen due, so re-assessing it actually judges
    # something. Taking the first instance awaiting evidence would now take a
    # period that has not closed yet, and the re-assessment would find nothing
    # to do — which is a fair thing for it to do and a useless thing to test.
    from sentinelops.repositories import repositories

    instances = repositories(live)["instances"]
    target = next(
        i for i in view.instances_awaiting_evidence(live)
        if instances.get(i).due_date <= date(2026, 6, 28)
    )
    huge = "Chat export.\n" + ("Some line of conversation. " * 4000)
    service.submit_evidence(
        live, instance_id=target, filename="export.md", content=huge,
        author=instances.get(target).owner_name,
        doc_type=service.doc_types_for(live, target)[0],
        as_of=date(2026, 6, 28),
    )
    service.reassess(live, target, date(2026, 6, 28))

    detail = view.finding_detail(live, target)
    frame = view.document_frame(
        detail["evidence"].content, detail["finding"].cited_spans
    )
    assert frame.total_chars > 100_000
    assert frame.height == view.COLLAPSED_HEIGHT, "the page stays the same length"


# --- markdown inside styled panels -----------------------------------------

def test_emphasis_renders_rather_than_showing_its_asterisks():
    """Streamlit skips markdown inside a raw-HTML block, so we convert it."""
    assert view.rich("**725 entries verified**") == "<strong>725 entries verified</strong>"
    assert view.rich("decided by `s3_model`") == "decided by <code>s3_model</code>"
    assert "**" not in view.rich("**bold** and `code`")


def test_the_narrative_is_escaped_before_it_is_emphasised():
    assert view.rich("<script>alert(1)</script>") == (
        "&lt;script&gt;alert(1)&lt;/script&gt;"
    )
    assert view.rich("**<b>x</b>**") == "<strong>&lt;b&gt;x&lt;/b&gt;</strong>"


def test_every_narrative_string_survives_conversion(live):
    for step in story.STEPS:
        for text in (step.title, story.why_for(step, live), step.button):
            assert "**" not in view.rich(text)


def test_the_show_more_button_is_offered_only_when_it_would_do_something():
    """A five-line report does not need an enlarge control."""
    assert view.document_frame("A short report.\nTwo lines.", []).fits
    assert not view.document_frame("a line of text\n" * 60, []).fits


def test_the_walkthrough_panel_renders_emphasis_on_screen(tmp_path, monkeypatch,
                                                          app_cache_cleared):
    app = _dashboard(tmp_path, monkeypatch)
    _open(app, "walkthrough")
    next(b for b in app.button
         if b.label == story.STEPS[0].button).click().run()

    # Streamlit *does* render markdown at the top level, even alongside inline
    # HTML — the asterisks only survive inside an HTML block element. So the
    # check is on the styled panels specifically, not on every string.
    panels = [
        m.value for m in app.markdown
        if "class='why'" in m.value or "class='outcome'" in m.value
    ]
    assert panels, "the walkthrough panels must be on screen"
    joined = " ".join(panels)
    assert "<strong>" in joined, "emphasis must be converted to HTML"
    assert "**" not in joined, "raw asterisks inside an HTML block reach the screen"


# --- slice 17: pages scoped by role, and the controls an owner never gets -------------

def test_pages_are_scoped_to_the_role():
    pa = view.page_paths("pa_infosec")
    owner = view.page_paths("unit_owner")
    management = view.page_paths("management")

    assert pa[0] == "screens/today.py", "PA/InfoSec land on Today"
    assert {"screens/today.py", "screens/portfolio.py", "screens/recurrence.py",
            "screens/findings.py", "screens/schedule.py", "screens/inbox.py"} <= set(pa)
    assert owner == ["screens/my_findings.py", "screens/owner_detail.py",
                     "screens/inbox.py"]
    assert management == ["screens/overview.py"]
    assert not (set(owner) - {"screens/inbox.py"}) & set(pa)
    assert not set(management) & (set(pa) | set(owner))

    for role in view.PAGES:
        defaults = [page for pages in view.pages_for(role).values()
                    for page in pages if page["default"]]
        assert len(defaults) == 1 and defaults[0]["path"] == view.page_paths(role)[0]
    for path in {*pa, *owner, *management}:
        assert (SRC / "ui" / path).exists(), path
    assert view.pages_for(None) == view.PAGES["management"], "no role, read-only"


def test_close_and_accept_are_absent_for_a_unit_owner(tmp_path, monkeypatch,
                                                      app_cache_cleared):
    """Section 7: the owner's Close control is absent, not disabled — Accept too.

    Set up so both have something to act on: an open finding with an evidence
    round waiting. PA/InfoSec see both controls, so their absence for the owner
    is a statement about the owner rather than about an empty screen. Absent
    means not in the element tree Streamlit sends to the browser, which is what
    becomes the DOM; and the stylesheet hides nothing, so a control cannot be
    present but hidden instead.
    """
    from sentinelops import directory
    from sentinelops.stages import rounds

    db = service.open_database(tmp_path / "demo.db")
    service.seed(db)
    repo, people = repositories(db), directory.load(db)
    finding = next(
        f for f in repo["findings"].list()
        if f.status == "open" and people.get(f.owner_identity)
        and people.get(f.owner_identity).role == "unit_owner"
        and people.get(f.owner_identity).auditable_unit == f.auditable_unit_id
    )
    rounds.open_round(
        repo, people, finding, by=finding.owner_identity, evidence_ref="EV-TEST",
        evidence_text="All three leavers' accounts were disabled; tickets attached.",
        as_of=service.current_date(db),
    )
    db.close()

    forbidden = {"Accept and close", "Mark insufficient", "Close finding"}
    app = _dashboard(tmp_path, monkeypatch)
    assert {"Accept and close", "Mark insufficient"} <= _buttons(app)
    app.session_state["selected_finding"] = finding.id
    _open(app, "findings")
    assert "Close finding" in _buttons(app)
    assert "dvisory reading" in " ".join(m.value for m in app.markdown), (
        "the auditor sees how the model read the round"
    )

    _act_as(app, finding.owner_identity)
    app.session_state["owner_finding"] = finding.id
    for path in view.page_paths("unit_owner"):
        app.switch_page(path).run()
        assert not app.exception, [e.message for e in app.exception]
        assert not forbidden & _buttons(app), path
        if path.endswith("owner_detail.py"):
            shown = " ".join(m.value for m in app.markdown)
            assert finding.id in shown, (
                "the owner is looking at the very finding PA/InfoSec could close"
            )
            assert "dvisory reading" not in shown, (
                "the model's reading of a round is the auditor's, not the filer's"
            )

    # nor can an owner reach an auditor's page by naming it
    with pytest.raises(ValueError):
        app.switch_page("screens/today.py")

    # The stylesheet hides nothing except the collapsed sidebar's labels, so a
    # control cannot be present-but-hidden on a page.
    hidden = _hiding_selectors(view.CSS)
    assert all(selector.startswith(COLLAPSED_SIDEBAR) for selector in hidden), hidden


def test_my_findings_are_filtered_in_the_query_not_the_display(live, monkeypatch):
    from sentinelops import directory
    from sentinelops.repositories import Repository

    repo, people = repositories(live), directory.load(live)
    owner = next(
        p for p in people.by_role("unit_owner")
        if any(f.auditable_unit_id == p.auditable_unit for f in repo["findings"].list())
    )
    asked: list[dict] = []
    real = Repository.list

    def spy(self, **where):
        if self.table == "findings":
            asked.append(dict(where))
        return real(self, **where)

    monkeypatch.setattr(Repository, "list", spy)
    rows = view.my_findings(live, owner.id, date(2026, 5, 28), include_closed=True)

    assert {"auditable_unit_id": owner.auditable_unit} in asked
    assert rows and {r["unit_id"] for r in rows} == {owner.auditable_unit}
    assert [r["target"] for r in rows] == sorted(r["target"] for r in rows)


# --- slice 17: the design system -----------------------------------------------------

def test_severity_is_never_colour_alone():
    for severity in view.SEVERITIES:
        markup = view.severity_badge(severity)
        assert f">{severity}<" in markup
        assert f"so-sev-{severity.lower()}" in markup
    assert ">Unassigned<" in view.severity_badge(None)
    for markup, text in (
        (view.status_badge("open"), "Open"),
        (view.progress_badge(None), "Not acknowledged"),
        (view.progress_badge("action_in_progress"), "Action in progress"),
        (view.response_badge("pending"), "Awaiting review"),
        (view.chronic_badge(), "Chronic"),
    ):
        assert f">{text}<" in markup, "a badge is a label with a colour, never a raw enum"


def test_the_stylesheet_uses_one_accent_one_neutral_scale_and_the_severity_set():
    colours = {c.upper() for c in re.findall(r"#[0-9A-Fa-f]{6}", view.CSS)}
    assert colours <= {c.upper() for c in view.PALETTE}
    assert view.ACCENT.upper() in colours
    for text, _, _ in view.SEVERITY_STYLE.values():
        assert text.upper() in colours
    assert "tabular-nums" in view.CSS
    for size in view.TYPE_SCALE.values():
        assert f"font-size: {size:g}px" in view.CSS, "the type scale is set explicitly"


def test_dates_read_as_business_dates():
    assert view.fmt_date(date(2027, 4, 15)) == "15 Apr 2027"
    assert view.fmt_date(datetime(2027, 4, 15, 10, 0)) == "15 Apr 2027"
    assert view.fmt_long_date(date(2027, 4, 15)) == "Thursday 15 April 2027"
    assert view.fmt_when(datetime(2027, 4, 15, 10, 0)) == "15 Apr 2027, 10:00"
    assert view.fmt_date(None) == "—"
    assert view.due_phrase(3) == "3 days late"
    assert view.due_phrase(1) == "1 day late"
    assert view.due_phrase(0) == "Due today"
    assert view.due_phrase(-2) == "Due in 2 days"


def test_an_empty_state_says_what_would_be_there_and_why():
    markup = view.empty_state("Nothing is waiting for review",
                              "When an owner files **evidence** it arrives here.")
    assert "Nothing is waiting for review" in markup
    assert "<strong>evidence</strong>" in markup
    assert "<script>" not in view.empty_state("<script>", "<script>")


def test_system_identities_are_named_not_shown_as_ids(live):
    from sentinelops import directory

    people = directory.load(live)
    assert view.person(people, "ID-ASSESSOR") == "automated assessment"
    assert view.person(people, "ID-SYSTEM") == "the scheduler"


# --- slice 17: the actions the new pages call ------------------------------------------

def _pending_round(conn):
    from sentinelops import directory
    from sentinelops.stages import rounds

    repo, people = repositories(conn), directory.load(conn)
    finding = next(
        f for f in repo["findings"].list()
        if f.status == "open" and people.get(f.owner_identity)
        and people.get(f.owner_identity).auditable_unit == f.auditable_unit_id
        and not any(r.is_open for r in rounds.rounds_for(repo, f.id))
    )
    ok, message = service.open_evidence_round(
        conn, finding.id, by=finding.owner_identity, evidence_ref="EV-1",
        evidence_text="Both accounts were disabled on 2 April; the tickets are attached.",
        note="Done.",
    )
    assert ok, message
    return finding, rounds.rounds_for(repo, finding.id)[-1]


def test_an_owner_files_a_round_and_it_joins_the_review_queue(live):
    finding, submission = _pending_round(live)
    assert submission.auditor_response == "pending"
    assert repositories(live)["findings"].get(finding.id).status == "open"
    queue = view.review_queue(live, service.current_date(live))
    item = next(i for i in queue if i["id"] == submission.id)
    assert item["recommendation"] is not None, "an advisory reading waits beside it"


def test_an_owner_cannot_file_on_another_units_finding(live):
    from sentinelops import directory

    repo, people = repositories(live), directory.load(live)
    finding = next(f for f in repo["findings"].list() if f.status == "open")
    stranger = next(p for p in people.by_role("unit_owner")
                    if p.auditable_unit != finding.auditable_unit_id)
    ok, message = service.open_evidence_round(
        live, finding.id, by=stranger.id, evidence_ref="EV", evidence_text="text",
    )
    assert not ok and "does not own" in message


def test_accepting_a_round_closes_the_finding(live):
    finding, submission = _pending_round(live)
    ok, message = service.respond_to_round(
        live, submission.id, response="accepted", by=service.default_identity(live),
        remarks="Accounts confirmed disabled against the tickets.",
    )
    assert ok, message
    assert repositories(live)["findings"].get(finding.id).status == "closed"


def test_an_insufficient_round_keeps_the_finding_open_and_counts_the_chase(live):
    finding, submission = _pending_round(live)
    before = repositories(live)["findings"].get(finding.id).follow_up_count
    ok, message = service.respond_to_round(
        live, submission.id, response="insufficient", by=service.default_identity(live),
        remarks="The tickets are not attached.",
    )
    assert ok, message
    after = repositories(live)["findings"].get(finding.id)
    assert after.status == "open"
    assert after.follow_up_count == before + 1


def test_an_owner_cannot_answer_a_round_and_nothing_moves(live):
    finding, submission = _pending_round(live)
    ok, _ = service.respond_to_round(
        live, submission.id, response="accepted", by=finding.owner_identity,
        remarks="Fine.",
    )
    assert not ok
    assert repositories(live)["rounds"].get(submission.id).auditor_response == "pending"
    assert repositories(live)["findings"].get(finding.id).status == "open"


def test_owner_progress_is_recorded_and_moves_nothing(live):
    from sentinelops import directory

    repo, people = repositories(live), directory.load(live)
    finding = next(
        f for f in repo["findings"].list()
        if f.status == "open" and people.get(f.owner_identity)
        and people.get(f.owner_identity).auditable_unit == f.auditable_unit_id
    )
    ok, message = service.record_progress(live, finding.id, "implemented",
                                          by=finding.owner_identity)
    assert ok, message
    after = repo["findings"].get(finding.id)
    assert after.owner_progress == "implemented" and after.status == "open"
    refused, _ = service.record_progress(live, finding.id, "implemented",
                                         by=service.default_identity(live))
    assert not refused, "PA/InfoSec do not report an owner's progress for them"


def test_only_the_recipient_marks_a_notification_read(live):
    auditor = service.default_identity(live)
    rows = view.inbox_rows(live, auditor)
    assert rows
    note = rows[0]
    other = next(c["id"] for c in view.identity_choices(live) if c["id"] != auditor)
    assert not service.mark_read(live, note["id"], by=other)[0]
    assert service.mark_read(live, note["id"], by=auditor)[0]
    assert not next(r for r in view.inbox_rows(live, auditor)
                    if r["id"] == note["id"])["unread"]


COLLAPSED_SIDEBAR = '[data-testid="stSidebar"][aria-expanded="false"]'


def _hiding_selectors(css: str) -> list[str]:
    """Every selector whose rule hides what it matches."""
    selectors = []
    for rule in css.split("}"):
        if "{" not in rule:
            continue
        selector, body = rule.rsplit("{", 1)
        compact = body.replace(" ", "")
        if "display:none" in compact or "visibility:hidden" in compact:
            selectors.append(selector.replace("<style>", "").strip())
    return selectors


# --- sidebar badges and the collapsed rail ---------------------------------------------

def test_sidebar_badges_count_what_is_waiting_for_pa_infosec(live):
    from sentinelops import analytics

    today = service.current_date(live)
    actor = service.acting_as(live, service.default_identity(live))
    badges = view.nav_badges(live, actor, today)
    repo = repositories(live)
    week = analytics.upcoming(repo, today, horizon_days=7)

    assert badges["screens/today.py"] == len(repo["rounds"].list(auditor_response="pending"))
    assert badges["screens/findings.py"] == len(view.overdue_rows(live, today))
    assert badges["screens/schedule.py"] == len(week["audits"]) + week["activity_total"]
    assert badges["screens/inbox.py"] == sum(
        1 for row in view.inbox_rows(live, actor["id"], as_of=today) if row["unread"]
    )
    assert set(badges) <= set(view.page_paths("pa_infosec"))


def test_sidebar_badges_for_an_owner_stay_inside_their_own_pages(live):
    today = service.current_date(live)
    owner = next(c for c in view.identity_choices(live) if c["role"] == "unit_owner")
    actor = service.acting_as(live, owner["id"])
    badges = view.nav_badges(live, actor, today)
    assert set(badges) <= set(view.page_paths("unit_owner"))
    mine = view.my_findings(live, owner["id"], today)
    assert badges["screens/my_findings.py"] == sum(1 for r in mine if r["days_past"] >= 0)


def test_the_badge_stylesheet_keys_on_each_page_address_and_carries_only_digits():
    css = view.nav_badge_css("pa_infosec", {
        "screens/today.py": 3, "screens/findings.py": 0, "screens/inbox.py": 318,
    })
    assert '[href$="/"]::after { content: "3"; }' in css, "the landing page lives at the root"
    assert '[href$="/inbox"]::after { content: "99+"; }' in css
    assert "/findings" not in css, "nothing waiting, no badge"
    assert re.findall(r'content: "([^"]*)"', css) == ["3", "99+"]
    assert view.nav_badge_css("pa_infosec", {}) == ""


def test_the_collapsed_sidebar_keeps_an_icon_rail_rather_than_vanishing():
    assert COLLAPSED_SIDEBAR in view.CSS
    rail = [rule for rule in view.CSS.split("}") if COLLAPSED_SIDEBAR in rule]
    assert any("transform: none" in rule and "width: 64px" in rule for rule in rail)
    assert any("stSidebarUserContent" in rule for rule in rail), "only the icons remain"


def test_the_next_event_is_named_before_the_jump_and_the_jump_lands_on_it(
    tmp_path, monkeypatch, app_cache_cleared
):
    app = _dashboard(tmp_path, monkeypatch)
    db = service.open_database(tmp_path / "demo.db")
    try:
        moment = service.next_event(db)
    finally:
        db.close()
    assert moment is not None

    shown = " ".join(m.value for m in app.markdown)
    assert "Next event" in shown
    assert moment.headline.title in shown and moment.headline.subject in shown

    next(b for b in app.button if b.label == "Jump to next event").click().run()
    assert not app.exception, [str(e) for e in app.exception]
    assert any("Jumped to" in element.value for element in app.success)
    db = service.open_database(tmp_path / "demo.db")
    try:
        assert service.current_date(db) == moment.day
    finally:
        db.close()


def test_reset_scenario_restores_the_exact_seeded_state(tmp_path, monkeypatch,
                                                        app_cache_cleared):
    app = _dashboard(tmp_path, monkeypatch)
    db = service.open_database(tmp_path / "demo.db")
    seeded = service.state_digest(db)
    db.close()

    next(b for b in app.button if b.label == "Run cycle now").click().run()
    db = service.open_database(tmp_path / "demo.db")
    assert service.state_digest(db) != seeded
    db.close()

    next(b for b in app.button if b.label == "Reset scenario").click().run()
    assert not app.exception, [str(e) for e in app.exception]
    db = service.open_database(tmp_path / "demo.db")
    try:
        assert service.state_digest(db) == seeded
    finally:
        db.close()


def test_model_cost_is_reachable_only_by_its_address():
    """Registered for everyone, in nobody's navigation, and linked from nowhere."""
    hidden = [page["path"] for page in view.HIDDEN_PAGES]
    assert hidden == ["screens/cost.py"]
    for role in view.PAGES:
        assert "screens/cost.py" not in view.page_paths(role)
    app_source = (SRC / "ui" / "app.py").read_text(encoding="utf-8")
    assert 'visibility="hidden"' in app_source
    assert "meter_card" not in app_source, "no spend in the sidebar"
    for path in LAYOUT:
        if path.name in ("cost.py", "app.py"):
            continue
        text = path.read_text(encoding="utf-8")
        assert "cost.py" not in text and '"/cost"' not in text, (
            f"{path.name} links to the cost page"
        )


def test_spend_is_grouped_by_what_made_the_call(live):
    rows = view.spend_by_purpose(live)
    meter = view.token_meter(live)
    assert rows, "a few cycles in, the model has been asked something"
    assert sum(r["calls"] for r in rows) == meter["calls"]
    assert sum(r["tokens"] for r in rows) == meter["total_tokens"]
    assert abs(sum(r["share"] for r in rows) - 100) < 1
    assert sum(t["calls"] for t in view.spend_by_tier(live)) == meter["calls"]


def test_a_notification_opens_in_a_modal_the_reader_must_close():
    """Clicked, a notification opens over a darkened page that waits for it.

    Not dismissible from outside, and closing resets the table's selection: a
    selection that survived the rerun would open the same notification again.
    """
    shell_source = (SRC / "ui" / "shell.py").read_text(encoding="utf-8")
    assert '@st.dialog("Notification"' in shell_source
    assert "dismissible=False" in shell_source
    assert shell_source.count('st.session_state["inbox_table_version"]') == 2, (
        "both ways out of the modal reset the selection"
    )
    inbox = (SRC / "ui" / "screens" / "inbox.py").read_text(encoding="utf-8")
    assert "shell.notification(" in inbox
    assert 'selection_mode="single-cell"' in inbox, "a click anywhere on the row opens it"
    assert "inbox_table_version" in inbox and "{choice}" in inbox
    assert "cursor: pointer" in view.CSS


def test_the_notification_header_names_the_kind_time_and_subject():
    markup = view.notification_header({
        "kind_label": "Escalation", "unread": True, "about": "FND-1",
        "sent": datetime(2027, 4, 15, 8, 0), "subject": "<b>Level 2</b> escalation",
    })
    assert ">Escalation<" in markup and ">Unread<" in markup
    assert "15 Apr 2027, 08:00" in markup and "FND-1" in markup
    assert "&lt;b&gt;Level 2&lt;/b&gt;" in markup, "the subject is escaped"


def test_the_inbox_shows_nothing_sent_after_the_simulated_date(conn, corpus):
    """At the demo's start date the seeded audit programme has already written
    closure notices dated next year. A morning screen must not open on them."""
    seed_database(conn, corpus)
    start = service.current_date(conn)
    auditor = service.default_identity(conn)

    everything = view.inbox_rows(conn, auditor)
    shown = view.inbox_rows(conn, auditor, as_of=start)

    assert any(row["sent"].date() > start for row in everything), (
        "the seeded programme writes ahead of the calendar; without that this "
        "test checks nothing"
    )
    assert all(row["sent"].date() <= start for row in shown)
