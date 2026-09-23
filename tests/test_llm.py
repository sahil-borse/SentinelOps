"""Provider boundary behaviour: protocol, factory, parsing, metering."""

import pytest

from sentinelops.llm import get_client
from sentinelops.llm import models
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


def test_the_real_provider_refuses_without_a_key_rather_than_guessing(monkeypatch):
    """No key, no call. It never falls back to the fake behind your back."""
    monkeypatch.setenv("OPENAI_API_KEY", "")
    with pytest.raises(LlmError) as caught:
        get_client("openai").complete(_request())
    # either the SDK is absent or the key is; both are boundary errors, and
    # neither is a silent success
    assert "OPENAI_API_KEY" in str(caught.value) or "openai package" in str(
        caught.value
    )


def test_the_key_is_never_hardcoded():
    from pathlib import Path as _Path

    src = _Path(__file__).resolve().parents[1] / "src" / "sentinelops"
    for path in src.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert "sk-" not in text, f"{path.name} looks like it contains a key"


def test_the_env_loader_never_overwrites_an_exported_variable(tmp_path, monkeypatch):
    from sentinelops.llm.env import load_env

    env_file = tmp_path / ".env"
    env_file.write_text(
        "OPENAI_API_KEY=from-file\nOTHER=from-file\n", encoding="utf-8"
    )
    monkeypatch.setenv("OPENAI_API_KEY", "from-shell")
    monkeypatch.delenv("OTHER", raising=False)

    loaded = load_env(env_file)
    import os

    assert os.environ["OPENAI_API_KEY"] == "from-shell"  # the shell wins
    assert os.environ["OTHER"] == "from-file"
    assert loaded == {"OTHER": "set"}, "it reports names, never values"


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
    rate_in, rate_cached, rate_out = models.price_for("assess")
    assert row["cost_usd"] == pytest.approx(
        (600 * rate_in + 400 * rate_cached + 200 * rate_out) / 1e6
    ), "charged at the published rates of the model that answered"


def test_every_metered_stage_names_a_model_and_a_price():
    """The stage-to-model choice is config, and every stage that spends has one."""
    for tier in ("assess", "triage", "recurrence", "brief", "report"):
        assert tier in models.MODELS
        assert models.model_for(tier) in models.PRICES
        assert all(rate > 0 for rate in models.price_for(tier))
    assert models.price_for("fake") == (0.0, 0.0, 0.0)
    assert "gpt" in models.table()


def test_a_stages_model_is_changeable_without_touching_code(monkeypatch):
    monkeypatch.setenv("SENTINELOPS_MODEL_BRIEF", "gpt-4.1-nano")
    assert models.model_for("brief") == "gpt-4.1-nano"
    assert models.price_for("brief") == models.PRICES["gpt-4.1-nano"]
    monkeypatch.delenv("SENTINELOPS_MODEL_BRIEF")
    monkeypatch.setenv("SENTINELOPS_MODEL", "gpt-4o-mini")
    assert models.model_for("assess") == "gpt-4o-mini"


def test_the_reading_stages_run_on_a_cheaper_model_than_the_writing_ones():
    """Four of section 2's uses read a document; two write what a person sends on."""
    writing = models.price_for("brief")[0]
    for reading in ("assess", "triage", "recurrence"):
        assert models.price_for(reading)[0] < writing


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


# --- a prompt and its schema must agree on the shape -----------------------

def test_the_triage_prompt_shows_the_shape_its_schema_requires():
    """The defect that killed a paid replay, catchable without a provider.

    Triage V1 told the model to answer "keyed by its id" and labelled the
    fields CATEGORY and SUGGESTED SEVERITY, while its schema required
    `{"findings": [{"id", "category", "suggested_severity", ...}]}`. The schema
    is validated locally but **never sent to the provider**, so nothing
    reconciled the two — and `FakeModelClient` always returned the canonical
    shape, so the disagreement could not surface until a real model read the
    words. It returned correct classifications the schema then rejected, at
    every batch size, 900 paid calls into a replay.
    """
    import json as _json

    from sentinelops.llm.prompts.triage import (
        TRIAGE_SHAPE,
        TRIAGE_SYSTEM_V2,
        triage_schema_v1,
    )

    categories = ("access_not_revoked", "training_not_completed")
    schema = triage_schema_v1(categories)
    example = _json.loads(
        TRIAGE_SHAPE.replace("<the id exactly as given>", "FND-1")
        .replace("<one category id from the list>", categories[0])
        .replace("Major|Minor|Observation", "Major")
        .replace("<one sentence>", "because the access was left live")
    )
    assert validate(example, schema), "the prompt's own example must validate"
    assert TRIAGE_SHAPE in TRIAGE_SYSTEM_V2, "the shape is shown, not described"


def test_every_prompt_names_the_wrapper_key_its_schema_requires():
    """A wrapper the prompt never mentions is a wrapper the model must guess.

    Triage V1 guessed wrong. Recurrence V1 had the identical defect — its
    schema requires a `recurrences` key that its prompt never named — and it is
    the stage that runs straight after classification, so it would have killed
    the *next* replay.

    **Every prompt, not the ones that were caught.** Both taxonomy prompts had
    it too and were not in this list, so a replay died on the consolidation call
    after paying for 453 assessments. That failure was intermittent — an
    unstated shape is one the model guesses right some of the time — which is
    exactly why it needs a test rather than a run.
    """
    from sentinelops.llm.prompts.assessment import (
        ASSESSMENT_SYSTEM_V3,
        assessment_schema_v2,
    )
    from sentinelops.llm.prompts.audit_report import (
        AUDIT_REPORT_SYSTEM_V2,
        audit_report_schema_v1,
    )
    from sentinelops.llm.prompts.brief import BRIEF_SYSTEM_V4, brief_schema_v2
    from sentinelops.llm.prompts.recurrence import (
        RECURRENCE_SYSTEM_V2,
        recurrence_schema_v1,
    )
    from sentinelops.llm.prompts.review import REVIEW_SYSTEM_V2, review_schema_v1
    from sentinelops.llm.prompts.taxonomy import (
        CONSOLIDATE_SYSTEM_V2,
        PROPOSE_SYSTEM_V2,
        consolidate_schema_v1,
        propose_schema_v1,
    )
    from sentinelops.llm.prompts.triage import TRIAGE_SYSTEM_V2, triage_schema_v1

    # All six, not the two that were caught. Every one of these prompts has to
    # name what its schema requires, because the schema itself never reaches
    # the provider.
    cases = [
        ("triage", TRIAGE_SYSTEM_V2, triage_schema_v1(("a_category",))),
        ("recurrence", RECURRENCE_SYSTEM_V2, recurrence_schema_v1()),
        ("brief", BRIEF_SYSTEM_V4, brief_schema_v2()),
        ("assessment", ASSESSMENT_SYSTEM_V3, assessment_schema_v2()),
        ("review", REVIEW_SYSTEM_V2, review_schema_v1()),
        ("audit report", AUDIT_REPORT_SYSTEM_V2, audit_report_schema_v1()),
        ("taxonomy propose", PROPOSE_SYSTEM_V2, propose_schema_v1()),
        ("taxonomy consolidate", CONSOLIDATE_SYSTEM_V2, consolidate_schema_v1()),
    ]
    for name, system, schema in cases:
        for key in schema["required"]:
            assert key in system, f"the {name} prompt never names {key!r}"


def test_the_brief_ceiling_can_hold_a_brief_its_schema_would_accept():
    """A ceiling below the schema's own maximum is a truncation waiting to happen.

    Truncation is a fatal error, not a short answer. The brief's 900-token
    ceiling was set when its entries were thinner; once the prompt asked for a
    `statement` on every cited claim, a full brief no longer fit and the call
    failed outright — the same way recurrence's flat ceiling failed against a
    full shortlist.
    """
    from sentinelops.llm.prompts.brief import MAX_TOKENS, REASON_MAX

    # 4 characters to a token, as a working approximation.
    priorities = 5 * (REASON_MAX // 4 + 15)
    claims = 6 * (300 // 4 + 35)
    assert MAX_TOKENS >= priorities + claims


def test_metering_module_does_not_measure_length_anywhere():
    """Guard against a future `len(text) // 4` creeping into the meter."""
    import inspect

    from sentinelops.llm import metering

    source = inspect.getsource(metering)
    body = source[source.index("class TokenMeter") :]
    assert "len(" not in body
