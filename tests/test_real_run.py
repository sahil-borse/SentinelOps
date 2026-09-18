"""Slice 19: the cap has to hold, and the meter has to be checkable.

These tests spend nothing. Everything here runs against a stub or a hand-built
response object — which is the point: the machinery that decides whether a paid
run may continue must be testable without a provider, or it only gets exercised
while money is moving.
"""

import pytest

from evaluation import baseline as baseline_module
from evaluation import harness
from evaluation.real_run import (
    Budget, BudgetExceeded, MeteredClient, _guard_provider, _reconcile,
)
from sentinelops.db import connect
from sentinelops.llm import get_client
from sentinelops.llm.protocol import LlmError, LlmRequest, LlmResponse
from sentinelops.synth import generate_corpus, seed_database


@pytest.fixture(scope="module")
def corpus():
    return generate_corpus()


def _response(model="gpt-4.1-mini", inp=1000, out=200, cached=0) -> LlmResponse:
    return LlmResponse(
        text="{}", parsed_json={}, input_tokens=inp, output_tokens=out,
        cached_tokens=cached, model=model, latency_ms=5, raw={},
    )


# --- the cap ---------------------------------------------------------------

def test_the_budget_refuses_the_call_that_would_pass_the_cap():
    """It stops *before* exceeding, not after noticing it has."""
    budget = Budget(limit_usd=0.001)
    budget.charge("assess", _response(inp=100, out=10))
    spent, calls = budget.spent_usd, budget.calls
    with pytest.raises(BudgetExceeded):
        budget.charge("brief", _response(inp=500_000, out=100_000))
    assert (budget.spent_usd, budget.calls) == (spent, calls), (
        "a refused call must leave the ledger untouched"
    )
    assert budget.spent_usd <= budget.limit_usd


def test_the_budget_breaks_spend_down_by_stage():
    budget = Budget(limit_usd=10.0)
    budget.charge("assess", _response(model="gpt-4.1-mini"))
    budget.charge("assess", _response(model="gpt-4.1-mini"))
    budget.charge("brief", _response(model="gpt-4.1"))
    assert budget.calls == 3
    assert budget.by_tier["assess"]["calls"] == 2
    assert budget.by_tier["brief"]["model"] == "gpt-4.1"
    # The writing stage costs more per token than the reading one, so a
    # single brief must not be filed under the same rate as an assessment.
    assert budget.by_tier["brief"]["cost"] > budget.by_tier["assess"]["cost"] / 2
    assert "total" in budget.table()


def test_the_metered_client_charges_every_call_it_passes_on():
    class Inner:
        def __init__(self):
            self.seen = []

        def complete(self, request):
            self.seen.append(request.tier)
            return _response()

    inner = Inner()
    budget = Budget(limit_usd=10.0)
    client = MeteredClient(budget, inner=inner)
    request = LlmRequest(system="s", messages=[{"role": "user", "content": "u"}],
                         tier="triage")
    client.complete(request)
    client.complete(request)
    assert inner.seen == ["triage", "triage"]
    assert budget.calls == 2 and budget.spent_usd > 0


def test_the_metered_client_checkpoints_as_it_goes():
    """A killed process keeps everything up to its last checkpoint.

    The first resume was stopped when its session ended, 225 paid calls in,
    and kept none of them: the database was written only when the stage
    finished, and a killed process runs no exception handler. Checkpointing at
    the metering boundary bounds any such loss to `every` calls, whichever
    stage is running.
    """
    class Inner:
        def complete(self, request):
            return _response()

    saved = []
    client = MeteredClient(Budget(limit_usd=10.0), inner=Inner(), every=3)
    client.checkpoint = lambda: saved.append(client.budget.calls)
    request = LlmRequest(system="s", messages=[{"role": "user", "content": "u"}],
                         tier="assess")
    for _ in range(7):
        client.complete(request)
    assert saved == [3, 6]


def test_a_journaled_answer_is_never_paid_for_twice(tmp_path):
    """An interrupted run is resumed from its journal, not bought again."""
    class Inner:
        def __init__(self):
            self.calls = 0

        def complete(self, request):
            self.calls += 1
            return _response(inp=1234)

    journal = tmp_path / "answers.jsonl"
    inner = Inner()
    request = LlmRequest(system="s", messages=[{"role": "user", "content": "u"}],
                         tier="assess")
    first = MeteredClient(Budget(limit_usd=10.0), inner=inner, journal=journal)
    first.complete(request)

    second = MeteredClient(Budget(limit_usd=10.0), inner=inner, journal=journal)
    again = second.complete(request)
    assert inner.calls == 1, "the provider was asked once"
    assert second.budget.calls == 0 and second.replayed == 1
    assert again.input_tokens == 1234, "the replay carries the original counts"

    other = LlmRequest(system="s", messages=[{"role": "user", "content": "v"}],
                       tier="assess")
    second.complete(other)
    assert inner.calls == 2, "a different request is a different call"


def test_reconciliation_accepts_the_dated_snapshot_name(conn):
    """The provider answers `gpt-4.1-mini-2025-04-14` to a `gpt-4.1-mini` request."""
    budget = Budget(limit_usd=10.0)
    conn.execute(
        "INSERT INTO token_usage (ts, tier, model, input_tokens, output_tokens,"
        " cached_tokens, latency_ms, cost_usd, label)"
        " VALUES ('2027-01-01', 'assess', 'gpt-4.1-mini-2025-04-14', 1, 1, 0, 1, 0.0, '')"
    )
    assert _reconcile(conn, budget)["unexpected_models"] == []


def test_an_unmetered_fallback_raises_instead_of_spending(monkeypatch):
    """The guard turns a silent second client into a loud failure.

    A stage that falls back to `get_client()` would build a client the budget
    knows nothing about and spend outside the cap. During a paid run the
    factory is therefore pointed at a provider that does not exist.
    """
    monkeypatch.setenv("SENTINELOPS_LLM_PROVIDER", "fake")
    _guard_provider()
    with pytest.raises(LlmError):
        get_client()


def test_reconciliation_notices_a_call_the_meter_never_saw(conn):
    """Two tallies of the same calls, so one going missing is visible."""
    budget = Budget(limit_usd=10.0)
    budget.charge("assess", _response(inp=100, out=10))
    conn.execute(
        "INSERT INTO token_usage (ts, tier, model, input_tokens, output_tokens,"
        " cached_tokens, latency_ms, cost_usd, label)"
        " VALUES ('2027-01-01', 'assess', 'gpt-4.1-mini', 100, 10, 0, 5, 0.0, '')"
    )
    assert _reconcile(conn, budget)["rows_match_calls"] is True

    budget.charge("assess", _response(inp=100, out=10))  # charged, never metered
    check = _reconcile(conn, budget)
    assert check["rows_match_calls"] is False
    assert check["budget_calls"] == 2 and check["metered_rows"] == 1


def test_reconciliation_names_a_model_nothing_configured(conn):
    budget = Budget(limit_usd=10.0)
    conn.execute(
        "INSERT INTO token_usage (ts, tier, model, input_tokens, output_tokens,"
        " cached_tokens, latency_ms, cost_usd, label)"
        " VALUES ('2027-01-01', 'assess', 'gpt-9-unreleased', 1, 1, 0, 1, 0.0, '')"
    )
    assert _reconcile(conn, budget)["unexpected_models"] == ["gpt-9-unreleased"]


# --- the stages are handed the client, never left to find one --------------

def test_section_eight_uses_the_client_it_is_given(conn, corpus):
    """The bug this guards against returned no error, only a cheaper bill.

    `_section_eight` runs taxonomy, classification and recurrence — three
    stages that call a model. They used to be called with no client at all, so
    on a paid run they would each have built their own, outside the budget. An
    exploding client proves the argument is actually used: if it were ignored,
    the default stub would answer and nothing would raise.
    """
    class Exploding:
        def complete(self, request):
            raise LlmError("the client was threaded through")

    seed_database(conn, corpus)
    with pytest.raises(LlmError):
        harness._section_eight(conn, client=Exploding())


# --- the sampled baseline is not the whole baseline ------------------------

def test_a_sampled_baseline_walks_only_the_sample(corpus, tmp_path, monkeypatch):
    monkeypatch.setattr(baseline_module, "CACHE_DIR", tmp_path)
    result, cached = baseline_module.run(
        corpus, client=get_client("fake"), model="stub-sample",
        sample=40, sample_seed=7,
    )
    assert not cached
    assert result.instances_considered == 40
    assert result.sample_size == 40 and result.sample_seed == 7
    assert "random sample of 40" in result.sample_method
    assert result.model_calls <= 40


def test_a_sampled_result_is_never_served_to_a_caller_wanting_the_whole_thing(
    corpus, tmp_path, monkeypatch
):
    """The quietest way to publish a partial measurement as a complete one."""
    monkeypatch.setattr(baseline_module, "CACHE_DIR", tmp_path)
    baseline_module.run(
        corpus, client=get_client("fake"), model="stub-sample",
        sample=25, sample_seed=3,
    )
    assert baseline_module.load_cached(corpus.fingerprint(), "stub-sample") is None
    assert baseline_module.load_cached(
        corpus.fingerprint(), "stub-sample", 25, 3
    ) is not None


def test_the_sample_is_the_same_sample_every_time(corpus):
    """Seeded, so a sampled figure can be reproduced rather than only believed."""
    first = baseline_module._select(corpus, 30, 11)
    second = baseline_module._select(corpus, 30, 11)
    other = baseline_module._select(corpus, 30, 12)
    assert first == second and len(first) == 30
    assert first != other
    assert baseline_module._select(corpus, None, 11) is None
    # A "sample" of everything is the whole run, and is keyed as such.
    assert baseline_module._select(corpus, 10**6, 11) is None


def test_the_sample_covers_instances_with_no_evidence_too(
    corpus, tmp_path, monkeypatch
):
    """A sample drawn only over instances that have evidence would flatter it.

    The skip rate is part of what the baseline measures — it is one of the two
    things the naive path does competently — so the sample is drawn over the
    whole considered population.
    """
    monkeypatch.setattr(baseline_module, "CACHE_DIR", tmp_path)
    result, _ = baseline_module.run(
        corpus, client=get_client("fake"), model="stub-skips",
        sample=120, sample_seed=5, force=True,
    )
    assert result.skipped_no_evidence > 0
    assert (
        result.model_calls + result.skipped_no_evidence
        + result.served_from_document_cache == 120
    )
