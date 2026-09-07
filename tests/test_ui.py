"""The dashboard's logic, tested without Streamlit.

Every computation the screen performs lives in `view.py` and every action behind
a button in `service.py`, neither of which imports Streamlit — so the parts that
can be wrong are testable, and `app.py` is layout that either renders or does
not.
"""

import ast
from datetime import date
from pathlib import Path

import pytest

from sentinelops.repositories import repositories
from sentinelops.synth import generate_corpus, seed_database
from sentinelops.ui import service, story, view

SRC = Path(__file__).resolve().parents[1] / "src" / "sentinelops"


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
    assert len(rows) == 11
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
        i for i in view.assessable_instances(live) if "CUST-COMPLAINTS" in i
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
    assert service.current_date(conn) == service.START_DATE


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
    pack, markdown, page = service.generate_pack(
        live, period_start=date(2026, 1, 1), period_end=date(2026, 12, 31),
        scope="test scope",
    )
    assert pack.totals["events"] > 100
    assert (tmp_path / "audit_pack_2026.md").exists()
    assert (tmp_path / "audit_pack_2026.html").exists()
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
    """If logic creeps into app.py it stops being tested. Keep it thin."""
    tree = ast.parse((SRC / "ui" / "app.py").read_text(encoding="utf-8"))
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
    assert len(functions) <= 1, "computation belongs in view.py or service.py"


def test_neither_logic_module_imports_streamlit():
    for name in ("view.py", "service.py"):
        source = (SRC / "ui" / name).read_text(encoding="utf-8")
        assert "streamlit" not in source, f"{name} must stay testable"


def test_every_required_control_is_present_on_the_screen():
    """The slice named twelve things. This asserts each one is wired up."""
    app = (SRC / "ui" / "app.py").read_text(encoding="utf-8")
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
    ):
        assert control in app, f"missing from the dashboard: {control}"


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

def test_the_dashboard_renders_end_to_end(tmp_path, monkeypatch, app_cache_cleared):
    """Runs the real script headlessly, seeds, and checks the screen came up.

    The logic modules are tested above; this is the one that would catch a
    layout call that raises — a mistyped column count, a metric handed the
    wrong type — which no amount of testing `view.py` would find.
    """
    from streamlit.testing.v1 import AppTest

    monkeypatch.setattr(service, "DB_PATH", tmp_path / "demo.db")
    app = AppTest.from_file(str(SRC / "ui" / "app.py"), default_timeout=120)
    app.run()

    assert not app.exception, [str(e) for e in app.exception]
    assert app.title[0].value == "SentinelOps"

    headings = [element.value for element in app.subheader]
    for expected in ("Compliance status by process area",
                     "Overdue and escalation queue", "Assessment detail",
                     "Submit evidence", "Open findings", "Audit"):
        assert expected in headings

    labels = {button.label for button in app.button}
    for expected in ("Run cycle now", "+1 day", "+1 week", "+1 month",
                     "Verify audit chain", "Generate audit pack", "Start over"):
        assert expected in labels

    # the walkthrough leads, with step one offered first
    assert "GUIDED WALKTHROUGH" in " ".join(m.value for m in app.markdown)
    assert story.STEPS[0].button in labels
    assert "1 · Raise this month's checks" in headings

    # the corpus seeded itself on first open, with no cycle run yet
    assert any("Simulated date" == m.label for m in app.metric)
    assert any(m.label == "Cost" for m in app.metric)


def test_the_run_cycle_button_actually_runs_a_cycle(tmp_path, monkeypatch, app_cache_cleared):
    """And the panels that only exist once there is something to show appear."""
    from streamlit.testing.v1 import AppTest

    monkeypatch.setattr(service, "DB_PATH", tmp_path / "demo.db")
    app = AppTest.from_file(str(SRC / "ui" / "app.py"), default_timeout=300)
    app.run()

    before = service.counts(service.open_database(tmp_path / "demo.db"))["instances"]
    next(b for b in app.button if b.label == "Run cycle now").click().run()
    assert not app.exception, [str(e) for e in app.exception]

    after = service.counts(service.open_database(tmp_path / "demo.db"))["instances"]
    assert after > before, "pressing the button raised checks"
    assert any("checks raised" in element.value for element in app.success)

    # the upload form and the re-assess control only exist once checks do
    labels = {button.label for button in app.button}
    assert "Submit evidence" in labels
    assert "Re-assess this check now" in labels
    assert any(u.label == "Evidence file" for u in app.get("file_uploader"))


def test_the_verify_button_reports_on_screen(tmp_path, monkeypatch, app_cache_cleared):
    from streamlit.testing.v1 import AppTest

    monkeypatch.setattr(service, "DB_PATH", tmp_path / "demo.db")
    app = AppTest.from_file(str(SRC / "ui" / "app.py"), default_timeout=180)
    app.run()
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
    assert (tmp_path / "audit_pack_2026.html").exists()


def test_step_six_reports_a_tampered_record(live, tmp_path, monkeypatch):
    monkeypatch.setattr(service, "PACK_DIR", tmp_path)
    live.execute("UPDATE audit_events SET owner = 'Nobody' WHERE seq = 12")
    live.commit()
    outcome = story.run(live, "prove")
    assert outcome.warning
    assert "tampered" in outcome.headline


def test_every_step_has_a_reason_a_person_would_recognise():
    for step in story.STEPS:
        assert len(step.why) > 120, f"{step.key} needs a real explanation"
        assert step.button and step.title
        # no identifiers or field names leaking into the narrative
        for jargon in ("decided_by", "CHK-", "CTRL-", "AREA-", "s3_model",
                       "prescreen", "supersedes_assessment_id"):
            assert jargon not in step.why, f"{step.key} leaks jargon: {jargon}"


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
    from streamlit.testing.v1 import AppTest

    monkeypatch.setattr(service, "DB_PATH", tmp_path / "demo.db")
    app = AppTest.from_file(str(SRC / "ui" / "app.py"), default_timeout=300)
    app.run()
    next(b for b in app.button if b.label == "Run cycle now").click().run()

    app.text_area[0].set_value(
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
    from streamlit.testing.v1 import AppTest

    monkeypatch.setattr(service, "DB_PATH", tmp_path / "demo.db")
    app = AppTest.from_file(str(SRC / "ui" / "app.py"), default_timeout=300)
    app.run()
    next(b for b in app.button if b.label == "Run cycle now").click().run()
    next(b for b in app.button if b.label == "Submit evidence").click().run()

    assert not app.exception, [str(e) for e in app.exception]
    assert any("Nothing to submit" in element.value for element in app.error)


def test_no_message_is_written_immediately_before_a_rerun():
    """The class of bug, not just the instance.

    Anything printed on the line before `st.rerun()` never reaches the screen.
    Park it in session state instead.
    """
    source = (SRC / "ui" / "app.py").read_text(encoding="utf-8").splitlines()
    for number, line in enumerate(source):
        if line.strip() != "st.rerun()":
            continue
        window = " ".join(source[max(0, number - 3):number])
        for painter in ("st.success(", "st.error(", "st.warning(", "st.info("):
            assert painter not in window, (
                f"line {number + 1}: {painter} just before st.rerun() is discarded"
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
    """A long document should arrive at its highlight, not at page one."""
    frame = view.document_frame(LONG, ["The reviewer field was left blank."])
    assert "scrollIntoView" in frame.html
    assert "querySelector('mark')" in frame.html


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
    target = view.instances_awaiting_evidence(live)[0]
    huge = "Chat export.\n" + ("Some line of conversation. " * 4000)
    service.submit_evidence(
        live, instance_id=target, filename="export.md", content=huge,
        author="R. Mehta", doc_type=service.doc_types_for(live, target)[0],
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


def test_every_narrative_string_survives_conversion():
    for step in story.STEPS:
        for text in (step.title, step.why, step.button):
            assert "**" not in view.rich(text)


def test_the_show_more_button_is_offered_only_when_it_would_do_something():
    """A five-line report does not need an enlarge control."""
    assert view.document_frame("A short report.\nTwo lines.", []).fits
    assert not view.document_frame("a line of text\n" * 60, []).fits


def test_the_walkthrough_panel_renders_emphasis_on_screen(tmp_path, monkeypatch,
                                                          app_cache_cleared):
    from streamlit.testing.v1 import AppTest

    monkeypatch.setattr(service, "DB_PATH", tmp_path / "demo.db")
    app = AppTest.from_file(str(SRC / "ui" / "app.py"), default_timeout=300)
    app.run()
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
