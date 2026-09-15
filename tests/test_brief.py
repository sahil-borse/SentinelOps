"""The prioritisation brief: one call, strict JSON, every claim cited, no state moved.

The brief is the most persuasive thing this system writes and the least
constrained, so the tests attack it: a claim with no citation, an invented
finding, an invented metric, an id mentioned but not cited, a reason that runs
to a paragraph, a reply that is not the shape asked for. Each must withhold the
brief rather than publish it.
"""

import json

import pytest

from sentinelops import analytics, priority, render
from sentinelops.directory import load as load_directory
from sentinelops.llm.prompts.brief import TOP_N
from sentinelops.llm.protocol import LlmResponse
from sentinelops.repositories import repositories
from sentinelops.stages import intelligence, taxonomy
from sentinelops.synth import generate_corpus, seed_database
from sentinelops.synth.calendar import SIMULATED_TODAY

AS_OF = SIMULATED_TODAY


@pytest.fixture(scope="module")
def corpus():
    return generate_corpus()


@pytest.fixture
def ready(conn, corpus):
    seed_database(conn, corpus)
    taxonomy.derive(conn, AS_OF)
    intelligence.classify(conn, AS_OF)
    return conn


class Scripted:
    """A model that says exactly what the test wants it to say."""

    def __init__(self, payload):
        self.payload = payload
        self.calls = 0

    def complete(self, request):
        self.calls += 1
        return LlmResponse(
            text=json.dumps(self.payload), parsed_json=self.payload,
            input_tokens=120, output_tokens=60, cached_tokens=0, model="scripted",
            latency_ms=1, raw={},
        )


def _facts(conn):
    ranked = priority.rank(repositories(conn), load_directory(conn), AS_OF)
    metrics = analytics.named_metrics(analytics.portfolio(conn, AS_OF))
    return [row["id"] for row in ranked[:TOP_N]], metrics


def _valid(ids):
    return {
        "top_priorities": [
            {"finding_id": ids[0], "reason": "Oldest Major past its target."},
        ],
        "emerging_patterns": [
            {"statement": "The top two share an owner.", "finding_ids": ids[:2],
             "metrics": []},
        ],
        "recommended_focus": [
            {"statement": "Work the backlog down first.", "finding_ids": [],
             "metrics": ["open_findings"]},
        ],
    }


def _withheld_because(conn, payload):
    brief = intelligence.prioritisation_brief(conn, AS_OF, client=Scripted(payload))
    assert not brief.published
    assert brief.top_priorities == [] and brief.recommended_focus == []
    assert brief.withheld
    return brief


# --- one call, three sections, everything cited --------------------------------------

def test_one_model_call_for_the_whole_portfolio(ready):
    """Section 9: the brief scales with cycles, not with findings."""
    from sentinelops.llm.providers.fake import FakeModelClient

    class Counting:
        calls = 0

        def complete(self, request):
            Counting.calls += 1
            return FakeModelClient().complete(request)

    brief = intelligence.prioritisation_brief(ready, AS_OF, client=Counting())
    assert Counting.calls == 1
    assert brief.model_calls == 1
    assert len(brief.ranked) > 1


def test_the_brief_has_three_sections_and_every_claim_cites(ready):
    brief = intelligence.prioritisation_brief(ready, AS_OF)
    assert brief.published, brief.withheld

    known = {row["id"] for row in brief.ranked[:TOP_N]}
    assert brief.top_priorities
    for item in brief.top_priorities:
        assert item["finding_id"] in known
        assert item["reason"] and "\n" not in item["reason"]
    assert brief.recommended_focus
    for claim in brief.emerging_patterns + brief.recommended_focus:
        assert claim["finding_ids"] or claim["metrics"], claim
        assert set(claim["finding_ids"]) <= known
        assert set(claim["metrics"]) <= set(brief.metrics)
    assert set(brief.cited_findings) <= known


def test_top_priorities_keep_the_deterministic_order(ready):
    """The model picks and explains; it does not reorder the queue."""
    ids, _ = _facts(ready)
    payload = _valid(ids)
    payload["top_priorities"] = [
        {"finding_id": fid, "reason": "Urgent."} for fid in reversed(ids[:3])
    ]
    brief = intelligence.prioritisation_brief(ready, AS_OF, client=Scripted(payload))
    assert brief.published
    assert [item["finding_id"] for item in brief.top_priorities] == ids[:3]


# --- an unattributable claim is rejected -------------------------------------------

def test_an_uncited_claim_is_rejected(ready):
    ids, _ = _facts(ready)
    payload = _valid(ids)
    payload["emerging_patterns"].append(
        {"statement": "Compliance culture is deteriorating.", "finding_ids": [],
         "metrics": []}
    )
    brief = _withheld_because(ready, payload)
    assert any("uncited claim" in reason for reason in brief.withheld)

    event = [
        e for e in repositories(ready)["audit"].read_all()
        if e.action == "brief_generated"
    ][-1]
    assert event.detail["withheld"] is True
    assert event.detail["withheld_reasons"] == brief.withheld


def test_an_invented_finding_is_rejected(ready):
    ids, _ = _facts(ready)
    payload = _valid(ids)
    payload["top_priorities"][0]["finding_id"] = "FND-INVENTED-1"
    brief = _withheld_because(ready, payload)
    assert any("FND-INVENTED-1" in reason for reason in brief.withheld)


def test_an_invented_metric_is_rejected(ready):
    ids, _ = _facts(ready)
    payload = _valid(ids)
    payload["recommended_focus"][0]["metrics"] = ["team_morale_index"]
    brief = _withheld_because(ready, payload)
    assert any("team_morale_index" in reason for reason in brief.withheld)


def test_an_id_mentioned_but_not_cited_is_rejected(ready):
    ids, _ = _facts(ready)
    payload = _valid(ids)
    payload["emerging_patterns"][0] = {
        "statement": f"The pattern starts with [{ids[2]}].",
        "finding_ids": ids[:1], "metrics": [],
    }
    brief = _withheld_because(ready, payload)
    assert any("without citing" in reason for reason in brief.withheld)


def test_a_reason_must_be_one_line(ready):
    ids, _ = _facts(ready)
    payload = _valid(ids)
    payload["top_priorities"][0]["reason"] = "First line.\nSecond line."
    brief = _withheld_because(ready, payload)
    assert any("not one line" in reason for reason in brief.withheld)


def test_a_malformed_reply_is_withheld_not_raised(ready):
    brief = _withheld_because(ready, {"top_priorities": "the usual suspects"})
    assert brief.withheld


# --- advisory ----------------------------------------------------------------------

def test_the_brief_changes_no_state(ready):
    repo = repositories(ready)

    def snapshot():
        return (
            sorted((f.id, f.status, f.severity, f.gap_category, f.target_date,
                    tuple(f.recurrence_of), f.follow_up_count)
                   for f in repo["findings"].list()),
            sorted((i.id, i.status) for i in repo["instances"].list()),
            sorted((r.id, r.auditor_response) for r in repo["rounds"].list()),
        )

    before = snapshot()
    intelligence.prioritisation_brief(ready, AS_OF)
    assert snapshot() == before


def test_the_named_metrics_are_section_eights_figures(ready):
    portfolio = analytics.portfolio(ready, AS_OF)
    metrics = analytics.named_metrics(portfolio)
    assert metrics["open_findings"] == portfolio["open_vs_closed"]["open"]
    assert metrics["overdue_90_plus"] == portfolio["overdue_ageing"]["buckets"]["90+"]
    assert metrics["trend_direction"] == portfolio["trend_verdict"]["direction"]
    assert metrics["multi_round_findings"] == portfolio["effort"]["multi_round"]
    assert metrics["upcoming_activities"] == portfolio["upcoming"]["activity_total"]


def test_the_brief_is_metered_and_its_tokens_are_read_from_the_response(ready):
    brief = intelligence.prioritisation_brief(ready, AS_OF)
    row = ready.execute(
        "SELECT input_tokens, output_tokens, tier FROM token_usage "
        "WHERE label = ?", (f"BRIEF:{AS_OF.isoformat()}",)
    ).fetchone()
    assert row["tier"] == "brief"
    assert (brief.input_tokens, brief.output_tokens) == (
        row["input_tokens"], row["output_tokens"]
    )


# --- rendering ---------------------------------------------------------------------

def test_both_renderings_carry_every_citation_and_the_formula(ready):
    brief = intelligence.prioritisation_brief(ready, AS_OF)
    markdown, page = render.brief_markdown(brief), render.brief_html(brief)
    assert page.startswith("<!doctype html>")
    for text in (markdown, page):
        for finding_id in brief.cited_findings:
            assert finding_id in text
        for name in brief.cited_metrics:
            assert name in text
        assert "priority score = severity x criticality" in text


def test_a_withheld_brief_says_so_without_quoting_what_was_rejected(ready):
    """The rejected claim goes to the trail. Quoting it on the page publishes it."""
    ids, _ = _facts(ready)
    payload = _valid(ids)
    payload["recommended_focus"][0]["metrics"] = ["team_morale_index"]
    brief = intelligence.prioritisation_brief(ready, AS_OF, client=Scripted(payload))
    for text in (render.brief_markdown(brief), render.brief_html(brief)):
        assert "Withheld" in text
        assert "recorded on the audit trail" in text
        assert "team_morale_index" not in text
        assert "Work the backlog down first." not in text
        assert ids[0] in text, "the deterministic ranking is still shown"
