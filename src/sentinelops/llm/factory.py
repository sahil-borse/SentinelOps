"""Provider selection. One env var, no config system."""

from __future__ import annotations

import os

from .protocol import LlmClient, LlmError

ENV_VAR = "SENTINELOPS_LLM_PROVIDER"


def get_client(provider: str | None = None) -> LlmClient:
    name = (provider or os.environ.get(ENV_VAR) or "fake").lower()
    if name == "fake":
        from .providers.fake import FakeModelClient

        return FakeModelClient()
    if name == "openai":
        from .providers.openai import OpenAIClient

        return OpenAIClient()
    raise LlmError(f"unknown provider {name!r}; set {ENV_VAR} to fake or openai")
