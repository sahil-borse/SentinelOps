"""The contract every provider implements. Provider-agnostic types only."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


class LlmError(RuntimeError):
    """Any provider failure, mapped to one type at the boundary."""


@dataclass
class LlmRequest:
    system: str
    messages: list[dict[str, str]]
    max_tokens: int = 1024
    response_schema: dict[str, Any] | None = None
    tier: str = "assess"


@dataclass
class LlmResponse:
    text: str
    parsed_json: dict[str, Any] | None
    input_tokens: int
    output_tokens: int
    cached_tokens: int
    model: str
    latency_ms: int
    raw: dict[str, Any] = field(default_factory=dict)


class LlmClient(Protocol):
    """A single method. Providers are swapped, never subclassed."""

    def complete(self, request: LlmRequest) -> LlmResponse: ...
