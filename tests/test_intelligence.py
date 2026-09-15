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
from sentinelops.llm.prompts.triage import SEVERITIES
from sentinelops.repositories import repositories, simulated_clock
from sentinelops.stages import intelligence, taxonomy
from sentinelops.synth import generate_corpus, seed_database

AS_OF = SIMULATED_TODAY


@pytest.fixture(scope="module")
def corpus():
    return generate_corpus()


@pytest.fixture
def seeded(conn, corpus):
    seed_database(conn, corpus)
    # The taxonomy is read off the corpus now rather than written into the
    # prompt package, and classification has no fallback list, so deriving it
    # is part of getting a usable database rather than a separate test concern.
    taxonomy.derive(conn, AS_OF)
    return conn


@pytest.fixture
def categories(seeded):
    return taxonomy.names(seeded)


def _batch_reply(entries):
    """One batched triage response, in the shape the caller validates."""
    import json

    from sentinelops.llm.protocol import LlmResponse

    payload = {"findings": entries}
    return LlmResponse(
        text=json.dumps(payload), parsed_json=payload, input_tokens=1,
        output_tokens=1, cached_tokens=0, model="inventive", latency_ms=1,
        raw={},
    )


def _ids_in(request):
    """The finding ids a triage request actually asked about."""
    body = "".join(m["content"] for m in request.messages)
    block = body.split("<<<FINDINGS", 1)[-1].split("FINDINGS>>>", 1)[0]
    return [
        line.split("id: ", 1)[1].strip()
        for line in block.splitlines() if line.startswith("id: ")
    ]


@pytest.fixture
def classified(seeded):
    report = intelligence.classify(seeded, AS_OF)
    return seeded, report


# --- use 1: classify the gap -------------------------------------------------

def test_every_finding_gets_a_category_from_the_closed_set(classified):
    conn, report = classified
    repo = repositories(conn)
    known = taxonomy.names(conn)
    assert report.classified
    for finding in repo["findings"].list():
        assert finding.gap_category in known


def test_the_taxonomy_is_closed_and_a_stray_label_is_refused(seeded):
    """A free-form label would make recurrence measure the model's vocabulary."""
    class Inventive:
        def complete(self, request):
            return _batch_reply([{
                "id": finding_id,
                "category": "access control-ish",
                "suggested_severity": "Major",
                "confidence": 0.9,
                "rationale": "made up",
            } for finding_id in _ids_in(request)])

    with pytest.raises(ValueError) as refused:
        intelligence.classify(seeded, AS_OF, client=Inventive(), limit=1)
    assert "outside the derived taxonomy" in str(refused.value)


def test_a_stray_severity_is_refused_too(seeded, categories):
    class Inventive:
        def complete(self, request):
            return _batch_reply([{
                "id": finding_id,
                "category": categories[0],
                "suggested_severity": "Catastrophic",
                "confidence": 0.9,
                "rationale": "made up",
            } for finding_id in _ids_in(request)])

    with pytest.raises(ValueError) as refused:
        intelligence.classify(seeded, AS_OF, client=Inventive(), limit=1)
    assert "outside the enum" in str(refused.value)


def test_a_batch_that_drops_a_finding_is_refused(seeded, categories):
    """The failure batching introduces, and the reason the caller checks ids.

    A model that answers six of eight leaves two findings looking
    unclassifiable when they are only unanswered — and they would sit
    uncategorised forever, because classify only revisits findings with no
    category.
    """
    class Forgetful:
        def complete(self, request):
            asked = _ids_in(request)
            return _batch_reply([{
                "id": finding_id,
                "category": categories[0],
                "suggested_severity": "Minor",
                "confidence": 0.9,
                "rationale": "partial batch",
            } for finding_id in asked[:-1]])

    with pytest.raises(ValueError) as refused:
        intelligence.classify(seeded, AS_OF, client=Forgetful())
    assert "no answer for" in str(refused.value)


def test_an_answer_about_a_finding_we_never_sent_is_refused(seeded, categories):
    """Otherwise a stray id would be filed against whichever finding it matched."""
    class Confused:
        def complete(self, request):
            return _batch_reply([{
                "id": "FND-NOT-IN-THIS-BATCH",
                "category": categories[0],
                "suggested_severity": "Minor",
                "confidence": 0.9,
                "rationale": "wrong finding",
            }])

    with pytest.raises(ValueError) as refused:
        intelligence.classify(seeded, AS_OF, client=Confused(), limit=1)
    assert "not in the batch" in str(refused.value)


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
    replacement = next(c for c in taxonomy.names(conn) if c != was)

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
            conn, finding.id, taxonomy.names(conn)[0], by=finding.owner_identity
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


# --- use 5: the prioritisation brief ------------------------------------------
#
# Moved to tests/test_brief.py and tests/test_priority.py in slice 16, when the
# ranking became a documented formula and the brief became strict JSON.


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


# --- recurrence does not pay twice for one question ----------------------------

def test_recurrence_does_not_pay_twice_for_the_same_question(classified):
    """It re-asked every unlinked finding on every run until slice 16.

    The harness ran it once, so the bill never showed; the dashboard runs it
    each cycle, and the token cost of one cycle carried every earlier cycle's
    questions again.
    """
    conn, _ = classified
    first = intelligence.detect_recurrence(conn, AS_OF)
    assert first.model_calls > 0
    second = intelligence.detect_recurrence(conn, AS_OF)
    assert second.model_calls == 0
    assert second.skipped_already_examined > 0


def test_a_new_earlier_candidate_is_asked_about(classified):
    """Not asking again is only right while there is nothing new to ask about."""
    conn, _ = classified
    intelligence.detect_recurrence(conn, AS_OF)
    repo = repositories(conn)
    target = next(
        f for f in sorted(repo["findings"].list(), key=lambda f: f.raised_at,
                          reverse=True)
        if f.gap_category and not f.recurrence_of
        and intelligence.candidates_for(repo, f)
    )
    other_unit = next(
        u.id for u in repo["units"].list() if u.id != target.auditable_unit_id
    )
    earliest = min(f.raised_at for f in repo["findings"].list())
    newcomer = Finding(
        id="FND-NEWLY-FOUND-PRIOR",
        source=target.source,
        auditable_unit_id=other_unit,
        description="A sentence about something else entirely.",
        raised_by=target.raised_by,
        raised_at=earliest - timedelta(days=1),
        owner_identity=target.owner_identity,
        target_date=target.target_date,
        gap_category=target.gap_category,
        severity="Minor",
    )
    with simulated_clock(newcomer.raised_at):
        repo["findings"].add(newcomer)

    again = intelligence.detect_recurrence(conn, AS_OF)
    assert target.id in again.examined, (
        "a candidate the finding was never shown appeared, so it is asked again"
    )
