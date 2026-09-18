"""Which model answers which stage, and what that model costs.

One table, so the choice is visible and changeable without reading the stages.
Section 2's five uses are not one job: four of them *read* — classify a
description, compare two findings, judge a document against a requirement,
suggest a severity — and two *write* what a person will send on, the
prioritisation brief and the audit report summary. The reading jobs take the
cheapest capable model; the writing jobs, where the words are the product, take
a larger one.

Any stage can be pointed elsewhere without touching code:

    SENTINELOPS_MODEL_ASSESS=gpt-4.1     one stage
    SENTINELOPS_MODEL=gpt-4o-mini        every stage

Prices are OpenAI's published rates, USD per million tokens, and they are what
`metering.cost_usd` charges — so the cost column in the meter is the cost of the
model that actually answered, not a placeholder.
"""

from __future__ import annotations

import os

from .env import load_env

#: USD per 1M tokens: input, cached input, output.
PRICES: dict[str, tuple[float, float, float]] = {
    "gpt-4.1": (2.00, 0.50, 8.00),
    "gpt-4.1-mini": (0.40, 0.10, 1.60),
    "gpt-4.1-nano": (0.10, 0.025, 0.40),
    "gpt-4o": (2.50, 1.25, 10.00),
    "gpt-4o-mini": (0.15, 0.075, 0.60),
}

#: The model each metered stage uses.
MODELS: dict[str, str] = {
    # reading: cheapest capable
    "assess": "gpt-4.1-mini",        # S3 evidence assessment, and evidence rounds
    "triage": "gpt-4.1-mini",        # gap classification, severity, taxonomy
    "recurrence": "gpt-4.1-mini",    # candidate comparison
    "prescreen": "gpt-4.1-nano",     # the pre-screen decides by rule; here for completeness
    # writing: what a person sends on
    "brief": "gpt-4.1",              # the prioritisation brief
    "report": "gpt-4.1",             # the audit report summary
}

#: A tier nobody configured is charged as the assessment tier rather than free.
FALLBACK_TIER = "assess"

#: The stub client is not a model and costs nothing.
FREE_TIERS = frozenset({"fake"})


def model_for(tier: str) -> str:
    """The model this stage uses, after any environment override."""
    load_env()
    override = (
        os.environ.get(f"SENTINELOPS_MODEL_{tier.upper()}")
        or os.environ.get("SENTINELOPS_MODEL")
    )
    return (override or MODELS.get(tier) or MODELS[FALLBACK_TIER]).strip()


def price_for(tier: str) -> tuple[float, float, float]:
    """(input, cached input, output) per 1M tokens, for the model this stage uses."""
    if tier in FREE_TIERS:
        return (0.0, 0.0, 0.0)
    return PRICES.get(model_for(tier), PRICES[MODELS[FALLBACK_TIER]])


def table() -> str:
    """The stage-to-model choice and its prices, printable."""
    lines = [f"{'stage':<12} {'model':<14} {'in':>8} {'cached':>8} {'out':>8}  (USD / 1M)"]
    for tier in MODELS:
        model = model_for(tier)
        rate_in, rate_cached, rate_out = price_for(tier)
        lines.append(
            f"{tier:<12} {model:<14} {rate_in:>8.3f} {rate_cached:>8.3f} {rate_out:>8.3f}"
        )
    return "\n".join(lines)
