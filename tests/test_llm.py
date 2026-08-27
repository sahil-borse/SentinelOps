"""Provider boundary behaviour: protocol, factory, parsing, metering."""

import pytest

from sentinelops.llm import get_client
from sentinelops.llm.metering import TokenMeter, cost_usd
from sentinelops.llm.parsing import extract_json, validate, with_retries
from sentinelops.llm.prompts import (
    ASSESSMENT_SYSTEM_V1,
    assessment_schema_v1,
    assessment_user_v1,
)
from sentinelops.llm.protocol import LlmError, LlmRequest, LlmResponse


def _request(evidence="All accounts were reviewed and signed off."):
    return LlmRequest(
        system=ASSESSMENT_SYSTEM_V1,
        messages=[
            {"role": "user", "content": assessment_user_v1("C", "criteria", [evidence])}
        ],
        response_schema=assessment_schema_v1(),
    )


def test_factory_defaults_to_fake(monkeypatch):
    monkeypatch.delenv("SENTINELOPS_LLM_PROVIDER", raising=False)
    assert type(get_client()).__name__ == "FakeModelClient"


def test_factory_reads_the_env_var(monkeypatch):
    monkeypatch.setenv("SENTINELOPS_LLM_PROVIDER", "openai")
    assert type(get_client()).__name__ == "OpenAIClient"


def test_factory_rejects_unknown_providers(monkeypatch):
    monkeypatch.setenv("SENTINELOPS_LLM_PROVIDER", "gemini")
    with pytest.raises(LlmError):
        get_client()


def test_real_provider_is_stubbed():
    with pytest.raises(NotImplementedError):
        get_client("openai").complete(_request())


def test_fake_client_is_deterministic():
    a = get_client("fake").complete(_request())
    b = get_client("fake").complete(_request())
    assert (a.text, a.input_tokens, a.output_tokens) == (
        b.text,
        b.input_tokens,
        b.output_tokens,
    )


def test_fake_client_always_cites():
    response = get_client("fake").complete(_request())
    assert response.parsed_json["cited_spans"]


def test_system_prompt_has_no_interpolation():
    assert "{" not in ASSESSMENT_SYSTEM_V1 and "%s" not in ASSESSMENT_SYSTEM_V1


def test_extract_json_repairs_fences_and_prose():
    assert extract_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert extract_json('Sure! {"a": 1} hope that helps') == {"a": 1}
    with pytest.raises(LlmError):
        extract_json("no json here")


def test_validate_checks_required_keys_and_enums():
    schema = {"required": ["verdict"], "properties": {"verdict": {"enum": ["gap"]}}}
    assert validate({"verdict": "gap"}, schema)
    with pytest.raises(LlmError):
        validate({}, schema)
    with pytest.raises(LlmError):
        validate({"verdict": "fine"}, schema)


def test_with_retries_maps_errors_and_eventually_succeeds():
    attempts = {"n": 0}

    def flaky():
        attempts["n"] += 1
        if attempts["n"] < 3:
            raise ValueError("provider blew up")
        return "ok"

    assert with_retries(flaky) == "ok"
    with pytest.raises(LlmError):
        with_retries(lambda: (_ for _ in ()).throw(ValueError("always")))


def test_token_meter_writes_counts_from_the_response(conn):
    response = LlmResponse(
        text="{}",
        parsed_json={},
        input_tokens=1000,
        output_tokens=200,
        cached_tokens=400,
        model="test-model",
        latency_ms=321,
        raw={},
    )
    with TokenMeter(conn, tier="assess", label="unit") as meter:
        meter.record(response)
    row = conn.execute("SELECT * FROM token_usage").fetchone()
    assert (row["input_tokens"], row["output_tokens"], row["cached_tokens"]) == (
        1000,
        200,
        400,
    )
    assert row["model"] == "test-model" and row["latency_ms"] == 321
    assert row["cost_usd"] == pytest.approx(cost_usd("assess", response))
    assert row["cost_usd"] == pytest.approx((600 * 2.5 + 400 * 1.25 + 200 * 10) / 1e6)


def test_token_meter_writes_nothing_when_the_call_fails(conn):
    with TokenMeter(conn, tier="assess") as meter:
        assert meter.response is None
    assert conn.execute("SELECT COUNT(*) c FROM token_usage").fetchone()["c"] == 0


def test_token_meter_copies_counts_and_never_measures_the_text(conn):
    """A 40k-character response declaring 12 tokens must record 12."""
    response = LlmResponse(
        text="x" * 40_000,
        parsed_json={},
        input_tokens=12,
        output_tokens=3,
        cached_tokens=0,
        model="test-model",
        latency_ms=10,
        raw={},
    )
    with TokenMeter(conn, tier="assess") as meter:
        meter.record(response)
    row = conn.execute("SELECT * FROM token_usage").fetchone()
    assert (row["input_tokens"], row["output_tokens"]) == (12, 3)


def test_metering_module_does_not_measure_length_anywhere():
    """Guard against a future `len(text) // 4` creeping into the meter."""
    import inspect

    from sentinelops.llm import metering

    source = inspect.getsource(metering)
    body = source[source.index("class TokenMeter") :]
    assert "len(" not in body
