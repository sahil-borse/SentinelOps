"""TokenMeter — every model call goes through it, or it did not happen.

Used as a context manager. The caller records the response on the meter; the
meter reads counts off that response object and writes one `token_usage` row.
Counts are never estimated and never computed from character counts.
"""

from __future__ import annotations

import sqlite3
import time
from datetime import datetime

from .protocol import LlmResponse

# USD per 1M tokens, per tier. Placeholder rates until slice 6 picks models.
PRICING: dict[str, tuple[float, float, float]] = {
    #  tier        input   output  cached_input
    "prescreen": (0.15, 0.60, 0.075),
    "assess": (2.50, 10.00, 1.25),
    "fake": (0.0, 0.0, 0.0),
}


def cost_usd(tier: str, response: LlmResponse) -> float:
    rate_in, rate_out, rate_cached = PRICING.get(tier, PRICING["assess"])
    uncached_in = max(response.input_tokens - response.cached_tokens, 0)
    return (
        uncached_in * rate_in
        + response.cached_tokens * rate_cached
        + response.output_tokens * rate_out
    ) / 1_000_000


class TokenMeter:
    def __init__(self, conn: sqlite3.Connection, tier: str, label: str = "") -> None:
        self.conn = conn
        self.tier = tier
        self.label = label
        self.response: LlmResponse | None = None
        self.cost: float = 0.0
        self._started = 0.0

    def __enter__(self) -> "TokenMeter":
        self._started = time.perf_counter()
        return self

    def record(self, response: LlmResponse) -> LlmResponse:
        """Hand the provider's response to the meter."""
        self.response = response
        return response

    def __exit__(self, exc_type, exc, tb) -> bool:
        if self.response is None:
            return False  # a failed call writes no usage row
        wall_ms = int((time.perf_counter() - self._started) * 1000)
        latency = self.response.latency_ms or wall_ms
        self.cost = cost_usd(self.tier, self.response)
        self.conn.execute(
            "INSERT INTO token_usage (ts, tier, model, input_tokens, output_tokens,"
            " cached_tokens, latency_ms, cost_usd, label)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                datetime.now().isoformat(),
                self.tier,
                self.response.model,
                self.response.input_tokens,
                self.response.output_tokens,
                self.response.cached_tokens,
                latency,
                self.cost,
                self.label,
            ),
        )
        self.conn.commit()
        return False
