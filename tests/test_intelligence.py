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

    report = intelligence.classify(seeded, AS_OF, client=Inventive(), limit=1)
    # Asked again with the permitted names restated, then left uncategorised.
    # What must never happen is the label being written.
    assert report.unclassifiable and not report.classified
    known = taxonomy.names(seeded)
    for finding in repositories(seeded)["findings"].list():
        assert finding.gap_category in ("", *known)


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

    report = intelligence.classify(seeded, AS_OF, client=Inventive(), limit=1)
    assert report.unclassifiable and not report.classified
    for finding in repositories(seeded)["findings"].list():
        assert finding.suggested_severity in ("", None, *SEVERITIES)


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


def test_a_batch_the_model_ignores_is_split_and_asked_again(seeded, categories):
    """The failure that killed a paid replay, and the recovery from it.

    `gpt-4.1-mini` returned a classification batch with an answer for none of
    its eight findings. Refusing was right — those findings must not be
    recorded unanswered — but refusing *fatally* threw away 900 calls already
    paid for. The batch is now halved and asked again, down to single findings,
    and only a finding still unanswered on its own is a real refusal.
    """
    class Overwhelmed:
        """Answers one finding at a time, and ignores anything larger."""

        def __init__(self):
            self.asked = []

        def complete(self, request):
            asked = _ids_in(request)
            self.asked.append(len(asked))
            if len(asked) > 1:
                return _batch_reply([])
            return _batch_reply([{
                "id": asked[0],
                "category": categories[0],
                "suggested_severity": "Minor",
                "confidence": 0.9,
                "rationale": "asked on its own",
            }])

    client = Overwhelmed()
    report = intelligence.classify(seeded, AS_OF, client=client)

    repo = repositories(seeded)
    assert report.classified, "the findings were classified, not abandoned"
    assert all(f.gap_category for f in repo["findings"].list())
    assert report.split_retries > 0, "the split is recorded, not absorbed"
    assert 1 in client.asked, "it narrowed all the way to single findings"
    assert max(client.asked) > 1, "and only after trying a real batch first"


def test_a_finding_unanswered_on_its_own_still_refuses(seeded, categories):
    """The retry must not become a way of giving up quietly.

    Splitting is only a recovery from inattention. A model that will not answer
    about a single finding has refused, and that has to surface rather than
    leave the finding silently uncategorised.
    """
    class Silent:
        def complete(self, request):
            return _batch_reply([])

    with pytest.raises(ValueError) as refused:
        intelligence.classify(seeded, AS_OF, client=Silent(), limit=1)
    assert "no answer for" in str(refused.value)


def test_a_value_outside_the_taxonomy_is_asked_again_before_it_fails(seeded, categories):
    """The refusal was right; being fatal was not.

    `gpt-4.1-mini` answered `observation` — a severity — where a gap category
    belonged, and a replay ended on one wrong word in one field of one finding.
    A closed-set answer outside the set is now asked once more with the
    permitted values restated, which is what a person would do.
    """
    class Slips:
        """Wrong the first time, right once told what the set is."""

        def __init__(self):
            self.asked = []

        def complete(self, request):
            body = "".join(m["content"] for m in request.messages)
            self.asked.append(body)
            category = categories[0] if "CORRECTION" in body else "observation"
            return _batch_reply([{
                "id": finding_id,
                "category": category,
                "suggested_severity": "Minor",
                "confidence": 0.9,
                "rationale": "second time lucky",
            } for finding_id in _ids_in(request)])

    client = Slips()
    report = intelligence.classify(seeded, AS_OF, client=client, limit=3)

    assert report.classified, "the findings were classified, not abandoned"
    assert report.invalid_retries == 1, "the retry is recorded, not absorbed"
    assert len(client.asked) == 2, "asked twice: once wrong, once corrected"
    assert "CORRECTION" in client.asked[1] and categories[0] in client.asked[1], (
        "the second attempt restates the values it may choose from"
    )
    assert "observation" in client.asked[1], "and names what it got wrong"
    assert report.model_calls == 2, "both calls are counted; both were paid for"


def test_a_finding_that_cannot_be_classified_is_left_alone_and_named(seeded, categories):
    """The label is refused; the finding is recorded; the run continues.

    Killing the run was the old behaviour and it cost a paid replay over a
    dropped prefix — `gpt-4.1-mini` answered
    `reliable_or_inadequate_record_keeping` where the taxonomy held
    `unreliable_or_inadequate_record_keeping`. Refusing the label is right.
    Refusing to finish is not: the finding stays uncategorised, is named in the
    report, and a later cycle asks again.
    """
    class Insists:
        def __init__(self):
            self.calls = 0

        def complete(self, request):
            self.calls += 1
            return _batch_reply([{
                "id": finding_id,
                "category": "access control-ish",
                "suggested_severity": "Minor",
                "confidence": 0.9,
                "rationale": "no",
            } for finding_id in _ids_in(request)])

    client = Insists()
    report = intelligence.classify(seeded, AS_OF, client=client, limit=1)

    assert client.calls == 2, "asked again before giving up, and only once"
    assert report.unclassifiable, "the finding is named, not silently skipped"
    assert not report.classified, "and nothing was recorded against it"
    repo = repositories(seeded)
    assert not repo["findings"].get(report.unclassifiable[0]).gap_category, (
        "no label outside the taxonomy was ever written"
    )


def test_a_severity_outside_the_enum_is_retried_the_same_way(seeded, categories):
    class Slips:
        def __init__(self):
            self.calls = 0

        def complete(self, request):
            self.calls += 1
            body = "".join(m["content"] for m in request.messages)
            severity = "Minor" if "CORRECTION" in body else "Catastrophic"
            return _batch_reply([{
                "id": finding_id,
                "category": categories[0],
                "suggested_severity": severity,
                "confidence": 0.9,
                "rationale": "fixed",
            } for finding_id in _ids_in(request)])

    client = Slips()
    report = intelligence.classify(seeded, AS_OF, client=client, limit=2)
    assert report.classified and client.calls == 2
    assert report.invalid_retries == 1


def test_a_stage_with_nothing_to_do_needs_no_client(seeded, monkeypatch):
    """Doing nothing must not require a provider.

    Both stages built their client before looking at whether there was any
    work. Scoring a finished run re-enters them with every finding classified
    and every candidate already examined, and constructing a client there fails
    against the guard that stands in for a provider during a paid run — so the
    run could be paid for and then not scored.
    """
    from sentinelops.llm import get_client
    from sentinelops.llm.protocol import LlmError

    intelligence.classify(seeded, AS_OF, client=get_client("fake"))
    intelligence.detect_recurrence(seeded, AS_OF, client=get_client("fake"))

    def explode(*args, **kwargs):
        raise LlmError("no client may be built when there is nothing to ask")

    monkeypatch.setattr(intelligence, "get_client", explode)
    again = intelligence.classify(seeded, AS_OF)
    assert again.model_calls == 0 and not again.classified
    once_more = intelligence.detect_recurrence(seeded, AS_OF)
    assert once_more.model_calls == 0


def test_a_recurrence_answer_has_room_for_every_candidate_offered():
    """A truncated reply is a fatal error, so the ceiling must fit the ask.

    `RECURRENCE_MAX_TOKENS` was a flat 500 while the schema allows one entry per
    candidate — up to `MAX_CANDIDATES` — each carrying a reason of up to 300
    characters. The stub answered briefly and usually found no links at all, so
    the ceiling was never reached. A real model filled the shortlist, the reply
    was cut off mid-JSON, and the resulting `LlmError` ended a replay 1,016 paid
    calls in.
    """
    from sentinelops.llm.prompts.recurrence import MAX_CANDIDATES
    from sentinelops.stages.intelligence import recurrence_max_tokens

    # 300 characters of reason is roughly 75 tokens, before the id and number.
    per_entry = 300 // 4
    assert recurrence_max_tokens(MAX_CANDIDATES) >= MAX_CANDIDATES * per_entry
    assert recurrence_max_tokens(1) < recurrence_max_tokens(MAX_CANDIDATES)
    assert recurrence_max_tokens(0) > 0, "an empty answer still needs room"
    assert recurrence_max_tokens(MAX_CANDIDATES) > 500, (
        "the flat ceiling that truncated a real model's answer"
    )


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
