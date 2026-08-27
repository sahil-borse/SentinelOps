"""Real provider. Wired up in slice 6; deliberately inert until then.

When implemented, the SDK import goes inside `complete` so no provider type is
importable from this module at module scope, and usage counts are read from
`response.usage`, never estimated.
"""

from __future__ import annotations

import os

from ..protocol import LlmRequest, LlmResponse

MODEL = os.environ.get("SENTINELOPS_MODEL", "gpt-4o-mini")


class OpenAIClient:
    """Implements the LlmClient protocol."""

    def complete(self, request: LlmRequest) -> LlmResponse:
        raise NotImplementedError("Real provider lands in slice 6.")
