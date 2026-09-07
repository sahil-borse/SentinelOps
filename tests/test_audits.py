"""The audit track: conducting, raising findings, and the section 6 report."""

from datetime import date, datetime

import pytest

from sentinelops.authority import AuthorityError
from sentinelops.directory import load as load_directory
from sentinelops.entities import ScheduledAudit
from sentinelops.repositories import repositories
from sentinelops.stages import audits
from sentinelops.synth import generate_corpus, seed_database

CONDUCTED = date(2026, 6, 12)

SPECS = [
    (0, "Privileged access for three leavers was not revoked within the SLA.",
     "Major", "access control"),
    (0, "The risk register was last reviewed nine months ago.",
     "Minor", "periodic review"),
    (1, "Vendor due diligence files were missing for two new suppliers.",
     "Major", "access control"),
    (2, "Backup restore test evidence could not be produced for Q1.",
     "Observation", "evidence retention"),
]


@pytest.fixture(scope="module")
def corpus():
    return generate_corpus()


@pytest.fixture
def audited(conn, corpus):
    """One conducted internal audit with four findings under it.

    Deliberately not one of the corpus's own audits: the corpus seeds a real
    eight-audit programme now, and a fixture that reused one of those ids would
    be testing the generator's data rather than this module's behaviour.
    """
    seed_database(conn, corpus)
    repo = repositories(conn)
    people = load_directory(conn)
    auditor = people.by_role("pa_infosec")[0]
    units = repo["units"].list()[:3]
    repo["audits"].add(ScheduledAudit(
        id="AUD-TEST-H1", kind="internal_audit",
        scope=[u.id for u in units], auditor_identity=auditor.id,
        planned_date=date(2026, 6, 1), title="H1 Internal Audit",
    ))
    audits.conduct(conn, "AUD-TEST-H1", by=auditor.id, as_of=CONDUCTED)
    for index, description, severity, category in SPECS:
        audits.raise_finding(
            conn, "AUD-TEST-H1", unit_id=units[index].id,
            description=description, severity=severity, by=auditor.id,
            gap_category=category, agreed_action_plan="Remediate and evidence.",
            as_of=CONDUCTED,
        )
    return conn, repo, people, auditor, units


# --- the audit itself --------------------------------------------------------

def test_conducting_records_the_date_and_who(audited):
    conn, repo, _, auditor, _ = audited
    audit = repo["audits"].get("AUD-TEST-H1")
    assert audit.status == "completed"
    assert audit.conducted_date == CONDUCTED
    event = repo["audit"].read_for("ScheduledAudit", audit.id)[0]
    assert event.action == "audit_conducted"
    assert event.actor_identity == auditor.id
    assert event.detail["kind"] == "internal_audit"


def test_only_pa_infosec_conducts_an_audit(conn, corpus):
    seed_database(conn, corpus)
    repo = repositories(conn)
    people = load_directory(conn)
    owner = people.by_role("unit_owner")[0]
    repo["audits"].add(ScheduledAudit(
        id="AUD-X", kind="qarev", scope=[repo["units"].list()[0].id],
        auditor_identity=people.by_role("pa_infosec")[0].id,
        planned_date=date(2026, 6, 1),
    ))
    with pytest.raises(AuthorityError):
        audits.conduct(conn, "AUD-X", by=owner.id, as_of=CONDUCTED)
    assert repo["audits"].get("AUD-X").status == "planned"


# --- findings are children of audits ----------------------------------------

def test_a_finding_raised_by_an_audit_records_its_parent(audited):
    _, repo, _, auditor, units = audited
    findings = audits.findings_of(repo, "AUD-TEST-H1")
    assert len(findings) == 4
    for finding in findings:
        assert finding.audit_id == "AUD-TEST-H1"
        assert finding.source == "audit"
        assert finding.check_instance_id is None
        assert finding.raised_by == auditor.id


def test_the_two_tracks_stay_distinguishable(audited):
    """Section 1's whole point. Provenance is recorded, not inferred."""
    conn, repo, _, _, _ = audited
    from sentinelops.stages.flag import run as flag_stage
    from sentinelops.stages.prescreen import run as prescreen
    from sentinelops.stages.trigger import run_cycle

    for as_of in (date(2026, 3, 28), date(2026, 6, 28)):
        run_cycle(conn, as_of)
        prescreen(conn, as_of)
        flag_stage(conn, as_of)

    by_source: dict[str, int] = {}
    for finding in repo["findings"].list():
        by_source[finding.source] = by_source.get(finding.source, 0) + 1
    # The corpus seeds its own programme, so audit-sourced findings are this
    # fixture's four plus the programme's. What matters is that both tracks are
    # populated and that every finding declares which one it came from.
    assert by_source["audit"] >= 4
    assert by_source["activity_assessment"] > 0
    assert len(audits.findings_of(repo, "AUD-TEST-H1")) == 4

    for finding in repo["findings"].list():
        # exactly one parent, never both, never neither
        parents = [finding.audit_id, finding.check_instance_id]
        assert len([p for p in parents if p]) == 1, finding.id


def test_severity_is_the_auditors_with_no_suggestion_to_override(audited):
    _, repo, _, auditor, _ = audited
    for finding in audits.findings_of(repo, "AUD-TEST-H1"):
        assert finding.severity in ("Major", "Minor", "Observation")
        assert finding.severity_assigned_by == auditor.id
        assert finding.suggested_severity is None, (
            "no model was asked, so there is nothing to have overridden"
        )


def test_the_target_date_follows_the_assigned_severity(audited):
    _, repo, _, _, _ = audited
    from sentinelops.stages import followup

    units = {u.id: u for u in repo["units"].list()}
    for finding in audits.findings_of(repo, "AUD-TEST-H1"):
        criticality = units[finding.auditable_unit_id].attributes["criticality"]
        assert finding.target_date == followup.target_date_for(
            CONDUCTED, finding.severity, criticality
        )


def test_a_finding_cannot_be_raised_outside_the_audits_scope(audited):
    conn, repo, _, auditor, units = audited
    outside = next(u for u in repo["units"].list() if u.id not in
                   {x.id for x in units})
    with pytest.raises(ValueError) as refused:
        audits.raise_finding(
            conn, "AUD-TEST-H1", unit_id=outside.id,
            description="Something we did not look at.", severity="Minor",
            by=auditor.id, as_of=CONDUCTED,
        )
    assert "not in the scope" in str(refused.value)


def test_an_owner_cannot_raise_a_finding(audited):
    conn, _, people, _, units = audited
    owner = people.get(units[0].owner_identity)
    with pytest.raises(AuthorityError):
        audits.raise_finding(
            conn, "AUD-TEST-H1", unit_id=units[0].id,
            description="I think we are fine actually.", severity="Observation",
            by=owner.id, as_of=CONDUCTED,
        )


# --- the report --------------------------------------------------------------

def test_the_report_carries_every_field_section_six_asks_for(audited):
    conn, _, _, _, _ = audited
    report = audits.generate_report(conn, "AUD-TEST-H1")
    text = audits.render_markdown(report)

    assert "Internal Audit" in text
    assert "AUD-TEST-H1" in text
    assert "P. Kaur" in text or report.auditor in text
    assert str(CONDUCTED) in text
    for finding in report.findings:
        assert finding["id"] in text
        assert finding["description"] in text
        assert finding["severity"] in text
        assert finding["owner"] in text
        assert finding["target_date"] in text
        assert finding["category"] in text
    assert "Remediate and evidence." in text


def test_the_report_needs_a_completed_audit(conn, corpus):
    seed_database(conn, corpus)
    repo = repositories(conn)
    people = load_directory(conn)
    repo["audits"].add(ScheduledAudit(
        id="AUD-PLANNED", kind="release_audit",
        scope=[repo["units"].list()[0].id],
        auditor_identity=people.by_role("pa_infosec")[0].id,
        planned_date=date(2026, 9, 1),
    ))
    with pytest.raises(ValueError) as refused:
        audits.generate_report(conn, "AUD-PLANNED")
    assert "at audit completion" in str(refused.value)


def test_exactly_one_model_call_per_report(audited):
    """Section 9: one call per report, not one per finding."""
    conn, _, _, _, _ = audited

    class Counting:
        def __init__(self):
            self.calls = 0

        def complete(self, request):
            from sentinelops.llm.providers.fake import FakeModelClient
            self.calls += 1
            return FakeModelClient().complete(request)

    client = Counting()
    report = audits.generate_report(conn, "AUD-TEST-H1", client=client)
    assert client.calls == 1
    assert len(report.findings) == 4


def test_every_statement_in_the_summary_cites_a_finding(audited):
    conn, _, _, _, _ = audited
    report = audits.generate_report(conn, "AUD-TEST-H1")
    assert report.summary
    known = {f["id"] for f in report.findings}
    assert audits.uncited_claims(report.summary, known) == []
    assert set(report.summary_cited) <= known


def test_a_summary_citing_a_finding_this_audit_never_raised_is_withheld(audited):
    """The dangerous failure: a fabricated reference with a citation's authority.

    The narrative is dropped and the report is still produced — a report that
    fails to exist because a paragraph would not come out right helps nobody —
    but nothing unattributable is ever published.
    """
    conn, _, _, _, _ = audited

    class Fabricating:
        def complete(self, request):
            from sentinelops.llm.protocol import LlmResponse
            import json
            payload = {
                "summary": (
                    "The audit found a systemic weakness in access control "
                    "[FND-NEVER-RAISED-99]."
                ),
                "cited_finding_ids": ["FND-NEVER-RAISED-99"],
            }
            text = json.dumps(payload)
            return LlmResponse(
                text=text, parsed_json=payload, input_tokens=10,
                output_tokens=10, cached_tokens=0, model="fabricator",
                latency_ms=1, raw={},
            )

    report = audits.generate_report(conn, "AUD-TEST-H1", client=Fabricating())
    assert report.summary == "", "an unattributable claim is not published"
    assert report.summary_cited == []
    # the rest of the report survives, because none of it came from the model
    assert len(report.findings) == 4
    text = audits.render_markdown(report)
    assert "FND-NEVER-RAISED-99" not in text
    assert "withheld" in text


def test_an_uncited_claim_is_withheld_too(audited):
    conn, _, _, _, _ = audited

    class Vague:
        def complete(self, request):
            from sentinelops.llm.protocol import LlmResponse
            import json
            payload = {
                "summary": (
                    "Controls across the organisation were found to be weak "
                    "and management attention is required."
                ),
                "cited_finding_ids": [],
            }
            return LlmResponse(
                text=json.dumps(payload), parsed_json=payload, input_tokens=10,
                output_tokens=10, cached_tokens=0, model="vague",
                latency_ms=1, raw={},
            )

    report = audits.generate_report(conn, "AUD-TEST-H1", client=Vague())
    assert report.summary == ""


def test_uncited_claims_allows_a_sentence_that_only_states_a_count():
    """A count came from the facts we supplied, so it is checkable directly."""
    known = {"FND-1"}
    assert audits.uncited_claims(
        "This audit raised 4 findings across 3 units.", known
    ) == []
    assert audits.uncited_claims("Access control is weak.", known) != []


# --- issuing is a human act --------------------------------------------------

def test_issuing_is_separate_from_generating_and_is_on_the_trail(audited):
    conn, repo, _, auditor, _ = audited
    audits.generate_report(conn, "AUD-TEST-H1")
    assert repo["audits"].get("AUD-TEST-H1").report_issued_at is None

    audits.issue(conn, "AUD-TEST-H1", by=auditor.id, as_of=date(2026, 6, 15))
    audit = repo["audits"].get("AUD-TEST-H1")
    assert audit.report_issued_at is not None
    assert audit.report_issued_by == auditor.id

    actions = [e.action for e in repo["audit"].read_for("ScheduledAudit", audit.id)]
    assert actions == [
        "audit_conducted", "audit_report_generated", "audit_report_issued"
    ]


def test_a_report_cannot_be_issued_before_it_is_generated(audited):
    conn, _, _, auditor, _ = audited
    with pytest.raises(ValueError) as refused:
        audits.issue(conn, "AUD-TEST-H1", by=auditor.id, as_of=CONDUCTED)
    assert "no generated report" in str(refused.value)


def test_an_owner_cannot_issue_a_report(audited):
    conn, _, people, _, units = audited
    audits.generate_report(conn, "AUD-TEST-H1")
    owner = people.get(units[0].owner_identity)
    with pytest.raises(AuthorityError):
        audits.issue(conn, "AUD-TEST-H1", by=owner.id, as_of=CONDUCTED)


# --- findings raised by an audit join the same follow-up ---------------------

def test_audit_findings_are_chased_like_any_other(audited):
    """One finding object means one chasing engine, not two."""
    from datetime import timedelta

    from sentinelops.stages import followup

    conn, repo, _, _, _ = audited
    late = CONDUCTED + timedelta(days=45)
    report = followup.run(conn, late)
    raised = {f.id for f in audits.findings_of(repo, "AUD-TEST-H1")}
    assert raised <= set(report.reminded)
    assert raised <= {finding_id for finding_id, _ in report.escalated}
