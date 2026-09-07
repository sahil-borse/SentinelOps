"""Section 2's remaining model uses: classification, recurrence, and the brief.

The tests that matter here are not "does it return something" but the three the
section is specific about: the category is overridable, a recurrence link points
backwards at a real prior finding and merges nothing, and the brief changes no
state at all.
"""

from datetime import date, datetime, timedelta

import pytest

from sentinelops.synth.calendar import SIMULATED_TODAY
from sentinelops.authority import AuthorityError
from sentinelops.directory import load as load_directory
from sentinelops.entities import Finding
from sentinelops.llm.prompts.triage import GAP_CATEGORIES, SEVERITIES
from sentinelops.repositories import repositories, simulated_clock
from sentinelops.stages import intelligence
from sentinelops.synth import generate_corpus, seed_database

AS_OF = SIMULATED_TODAY


@pytest.fixture(scope="module")
def corpus():
    return generate_corpus()


@pytest.fixture
def seeded(conn, corpus):
    seed_database(conn, corpus)
    return conn


@pytest.fixture
def classified(seeded):
    report = intelligence.classify(seeded, AS_OF)
    return seeded, report


# --- use 1: classify the gap -------------------------------------------------

def test_every_finding_gets_a_category_from_the_closed_set(classified):
    conn, report = classified
    repo = repositories(conn)
    assert report.classified
    for finding in repo["findings"].list():
        assert finding.gap_category in GAP_CATEGORIES


def test_the_taxonomy_is_closed_and_a_stray_label_is_refused(seeded):
    """A free-form label would make recurrence measure the model's vocabulary."""
    class Inventive:
        def complete(self, request):
            import json

            from sentinelops.llm.protocol import LlmResponse
            payload = {
                "category": "access control-ish",
                "suggested_severity": "Major",
                "confidence": 0.9,
                "rationale": "made up",
            }
            return LlmResponse(
                text=json.dumps(payload), parsed_json=payload, input_tokens=1,
                output_tokens=1, cached_tokens=0, model="inventive",
                latency_ms=1, raw={},
            )

    with pytest.raises(ValueError) as refused:
        intelligence.classify(seeded, AS_OF, client=Inventive(), limit=1)
    assert "outside the taxonomy" in str(refused.value)


def test_a_stray_severity_is_refused_too(seeded):
    class Inventive:
        def complete(self, request):
            import json

            from sentinelops.llm.protocol import LlmResponse
            payload = {
                "category": GAP_CATEGORIES[0],
                "suggested_severity": "Catastrophic",
                "confidence": 0.9,
                "rationale": "made up",
            }
            return LlmResponse(
                text=json.dumps(payload), parsed_json=payload, input_tokens=1,
                output_tokens=1, cached_tokens=0, model="inventive",
                latency_ms=1, raw={},
            )

    with pytest.raises(ValueError) as refused:
        intelligence.classify(seeded, AS_OF, client=Inventive(), limit=1)
    assert "outside the enum" in str(refused.value)


def test_classification_never_touches_the_assigned_severity(classified):
    """Section 2, use 4: the auditor assigns; the model advises.

    Every audit-raised finding already carries a severity a person chose. The
    classifier writes `suggested_severity` beside it and must not move it — if
    it did, the override would be invisible and the "advisory only" claim would
    be false.
    """
    conn, _ = classified
    repo = repositories(conn)
    for finding in repo["findings"].list():
        if finding.source != "audit":
            continue
        assert finding.severity in SEVERITIES
        assert finding.severity_assigned_by
        assert finding.severity_assigned_by != "ID-ASSESSOR"


def test_a_disagreement_between_model_and_auditor_is_visible(classified):
    """The point of keeping both: how often the model is overruled."""
    conn, _ = classified
    repo = repositories(conn)
    events = [
        e for e in repo["audit"].read_all() if e.action == "finding_classified"
    ]
    assert events
    for event in events:
        assert "agrees_with_auditor" in event.detail
        assert "suggested_severity" in event.detail
        assert "assigned_severity" in event.detail
    # the corpus has enough variety that at least one disagreement exists
    assert any(e.detail["agrees_with_auditor"] is False for e in events)


def test_low_confidence_is_flagged_rather_than_hidden(classified):
    conn, report = classified
    repo = repositories(conn)
    for finding_id in report.needs_review:
        event = [
            e for e in repo["audit"].read_for("Finding", finding_id)
            if e.action == "finding_classified"
        ][0]
        assert event.detail["needs_human_review"] is True
        assert event.detail["confidence"] < intelligence.CONFIDENCE_FLOOR


def test_the_auditor_can_override_the_category(classified):
    conn, _ = classified
    repo = repositories(conn)
    people = load_directory(conn)
    auditor = people.by_role("pa_infosec")[0]
    finding = repo["findings"].list()[0]
    was = finding.gap_category
    replacement = next(c for c in GAP_CATEGORIES if c != was)

    intelligence.override_category(
        conn, finding.id, replacement, by=auditor.id
    )
    assert repo["findings"].get(finding.id).gap_category == replacement

    event = [
        e for e in repo["audit"].read_for("Finding", finding.id)
        if e.action == "finding_category_overridden"
    ][0]
    assert event.detail["previous"] == was
    assert event.detail["category"] == replacement
    assert event.actor_identity == auditor.id


def test_an_owner_cannot_override_a_category(classified):
    conn, _ = classified
    repo = repositories(conn)
    finding = repo["findings"].list()[0]
    with pytest.raises(AuthorityError):
        intelligence.override_category(
            conn, finding.id, GAP_CATEGORIES[0], by=finding.owner_identity
        )


def test_classifying_twice_spends_nothing_the_second_time(classified):
    conn, first = classified
    second = intelligence.classify(conn, AS_OF)
    assert first.model_calls > 0
    assert second.model_calls == 0, "already-classified findings are skipped"


# --- use 2: recurrence -------------------------------------------------------

def test_candidates_are_filtered_deterministically(classified):
    """The stakeholder's definition, enforced in code rather than requested."""
    conn, _ = classified
    repo = repositories(conn)
    for finding in repo["findings"].list():
        for candidate in intelligence.candidates_for(repo, finding):
            assert candidate.id != finding.id
            assert candidate.gap_category == finding.gap_category
            assert candidate.raised_at < finding.raised_at, "recurrence looks back"
            different_unit = (
                candidate.auditable_unit_id != finding.auditable_unit_id
            )
            different_period = (
                intelligence._period_of(candidate)
                != intelligence._period_of(finding)
            )
            assert different_unit or different_period


def test_a_finding_with_no_candidates_costs_nothing(classified):
    conn, _ = classified
    report = intelligence.detect_recurrence(conn, AS_OF)
    assert report.skipped_no_candidates > 0
    assert report.model_calls == len(report.examined) - report.skipped_no_candidates
    assert report.model_calls < len(report.examined), (
        "the deterministic filter must actually be saving calls"
    )


def test_the_planted_recurrence_is_found(classified):
    """Section 10 plants gaps that recur across units and periods on purpose.

    This is the claim the pitch rests on: the same failure, described in
    different words by different auditors months apart, in units that do not
    talk to each other. If the detector cannot find a set that was planted for
    it, it will not find one that was not.
    """
    conn, _ = classified
    repo = repositories(conn)
    intelligence.detect_recurrence(conn, AS_OF)

    linked = [f for f in repo["findings"].list() if f.recurrence_of]
    assert linked, "nothing was linked at all"

    units = {}
    for finding in linked:
        for prior_id in finding.recurrence_of:
            prior = repo["findings"].get(prior_id)
            units.setdefault(finding.id, set()).update(
                {finding.auditable_unit_id, prior.auditable_unit_id}
            )
    # at least one link spans two different units
    assert any(len(u) > 1 for u in units.values()), (
        "every link stayed inside one unit; that is a persistent problem, not "
        "a recurring one"
    )


def test_a_link_points_backwards_at_a_real_finding(classified):
    conn, _ = classified
    repo = repositories(conn)
    intelligence.detect_recurrence(conn, AS_OF)
    for finding in repo["findings"].list():
        for prior_id in finding.recurrence_of:
            prior = repo["findings"].get(prior_id)
            assert prior is not None, f"{finding.id} cites a finding that is gone"
            assert prior.raised_at < finding.raised_at
            assert prior.gap_category == finding.gap_category


def test_an_invented_prior_finding_is_dropped(classified):
    """The audit report's rule, applied here: a fabricated id has authority."""
    conn, _ = classified

    class Fabricating:
        def complete(self, request):
            import json

            from sentinelops.llm.protocol import LlmResponse
            payload = {"recurrences": [{
                "finding_id": "FND-NEVER-EXISTED",
                "confidence": 0.99,
                "reason": "invented",
            }]}
            return LlmResponse(
                text=json.dumps(payload), parsed_json=payload, input_tokens=1,
                output_tokens=1, cached_tokens=0, model="fabricator",
                latency_ms=1, raw={},
            )

    report = intelligence.detect_recurrence(conn, AS_OF, client=Fabricating())
    repo = repositories(conn)
    assert report.linked == []
    for finding in repo["findings"].list():
        assert "FND-NEVER-EXISTED" not in finding.recurrence_of


def test_recurrence_merges_nothing(classified):
    """Advisory. A link is a pointer, and both findings stay open on their own."""
    conn, _ = classified
    repo = repositories(conn)
    before = {f.id: (f.status, f.severity) for f in repo["findings"].list()}
    intelligence.detect_recurrence(conn, AS_OF)
    after = {f.id: (f.status, f.severity) for f in repo["findings"].list()}
    assert before == after


def test_every_examination_is_on_the_trail_even_when_nothing_matched(classified):
    conn, _ = classified
    repo = repositories(conn)
    report = intelligence.detect_recurrence(conn, AS_OF)
    events = {
        e.entity_id for e in repo["audit"].read_all()
        if e.action == "recurrence_examined"
    }
    examined_with_candidates = set(report.examined) - {
        f.id for f in repo["findings"].list()
        if not intelligence.candidates_for(repo, f)
    }
    assert examined_with_candidates <= events


# --- use 5: the prioritisation brief -----------------------------------------

def test_the_brief_is_one_call_for_the_whole_portfolio(classified):
    """Section 9's most important cost rule: it scales with cycles, not findings."""
    conn, _ = classified

    class Counting:
        def __init__(self):
            self.calls = 0

        def complete(self, request):
            from sentinelops.llm.providers.fake import FakeModelClient
            self.calls += 1
            return FakeModelClient().complete(request)

    client = Counting()
    brief = intelligence.prioritisation_brief(conn, AS_OF, client=client)
    assert client.calls == 1
    assert brief.metrics["open"] > 1


def test_the_ranking_is_deterministic_and_not_the_models(classified):
    """A model that ordered the queue would be prioritising, which section 2
    does not permit. It interprets an order the code produced."""
    conn, _ = classified
    repo = repositories(conn)
    people = load_directory(conn)
    first = intelligence.rank_open_findings(repo, people, AS_OF)
    second = intelligence.rank_open_findings(repo, people, AS_OF)
    assert [r["id"] for r in first] == [r["id"] for r in second]
    if len(first) > 1:
        severities = [r["severity"] for r in first]
        assert severities.index(severities[0]) == 0


def test_the_brief_changes_no_state(classified):
    conn, _ = classified
    repo = repositories(conn)
    before = {
        f.id: (f.status, f.severity, f.gap_category, tuple(f.recurrence_of))
        for f in repo["findings"].list()
    }
    intelligence.prioritisation_brief(conn, AS_OF)
    after = {
        f.id: (f.status, f.severity, f.gap_category, tuple(f.recurrence_of))
        for f in repo["findings"].list()
    }
    assert before == after


def test_every_claim_in_the_brief_cites_a_finding(classified):
    conn, _ = classified
    brief = intelligence.prioritisation_brief(conn, AS_OF)
    assert brief.text
    known = {row["id"] for row in brief.ranked}
    assert intelligence.uncited_claims(brief.text, known) == []
    assert set(brief.cited) <= known


def test_an_uncited_brief_is_withheld(classified):
    conn, _ = classified

    class Vague:
        def complete(self, request):
            import json

            from sentinelops.llm.protocol import LlmResponse
            payload = {
                "brief": "Compliance is broadly in a difficult position and "
                         "management attention is required across the board.",
                "cited_finding_ids": [],
            }
            return LlmResponse(
                text=json.dumps(payload), parsed_json=payload, input_tokens=1,
                output_tokens=1, cached_tokens=0, model="vague",
                latency_ms=1, raw={},
            )

    brief = intelligence.prioritisation_brief(conn, AS_OF, client=Vague())
    assert brief.text == ""
    assert brief.cited == []
    # the metrics survive, because none of them came from the model
    assert brief.metrics["open"] > 0
    assert brief.ranked


def test_the_metrics_are_section_eight_and_deterministic(classified):
    conn, _ = classified
    repo = repositories(conn)
    people = load_directory(conn)
    ranked = intelligence.rank_open_findings(repo, people, AS_OF)
    metrics = intelligence.portfolio_metrics(repo, AS_OF, ranked)

    assert metrics["open"] + metrics["closed"] == len(repo["findings"].list())
    assert set(metrics["ageing"]) == {"0-30", "31-60", "61-90", "90+"}
    assert sum(metrics["severity_mix"].values()) == metrics["open"]
    assert sum(metrics["by_unit"].values()) == metrics["open"]
    assert sum(metrics["by_category"].values()) == metrics["open"]


# --- provenance and cost -----------------------------------------------------

def test_every_call_is_metered_with_its_own_tier(classified):
    conn, _ = classified
    intelligence.detect_recurrence(conn, AS_OF)
    intelligence.prioritisation_brief(conn, AS_OF)
    tiers = {
        row["tier"]
        for row in conn.execute("SELECT DISTINCT tier FROM token_usage")
    }
    assert {"triage", "recurrence", "brief"} <= tiers


def test_the_prompt_version_travels_onto_every_suggestion(classified):
    conn, _ = classified
    intelligence.detect_recurrence(conn, AS_OF)
    repo = repositories(conn)
    for event in repo["audit"].read_all():
        if event.action in ("finding_classified", "recurrence_examined",
                            "brief_generated"):
            assert event.detail["prompt_version"]
            assert event.detail["model"]


def test_the_advisory_uses_are_stamped_as_ai(classified):
    conn, _ = classified
    repo = repositories(conn)
    for event in repo["audit"].read_all():
        if event.action in ("finding_classified", "recurrence_examined"):
            assert event.actor_kind == "ai"
