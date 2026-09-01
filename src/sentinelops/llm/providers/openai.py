"""The real provider.

The SDK is imported inside `complete`, so this module is importable — and the
whole suite runs — on a machine with neither the package nor a key. Nothing
provider-shaped escapes: every SDK exception is mapped to `LlmError`, and the
object handed back is a plain `LlmResponse`.

Token counts are read off `response.usage`. They are never estimated, never
derived from character counts, and never guessed when the field is absent — a
missing count is recorded as zero and visible as such rather than invented.

The key comes from the environment (`.env` is loaded into it if present) and is
never logged, never placed in a prompt, and never included in an error message.
"""

from __future__ import annotations

import os
import time
from typing import Any

from ..env import load_env
from ..protocol import LlmError, LlmRequest, LlmResponse

API_KEY_VAR = "OPENAI_API_KEY"
MODEL_VAR = "SENTINELOPS_MODEL"
DEFAULT_MODEL = "gpt-4o-mini"

#: Nothing may run longer than this or cost more than max_tokens allows.
REQUEST_TIMEOUT_SECONDS = 60


def _api_key() -> str:
    load_env()
    key = os.environ.get(API_KEY_VAR, "").strip()
    if not key:
        raise LlmError(
            f"{API_KEY_VAR} is not set. Put it in .env or export it; it is never "
            "read from source."
        )
    return key


def model_name() -> str:
    return os.environ.get(MODEL_VAR, DEFAULT_MODEL)


def _usage(response: Any) -> tuple[int, int, int]:
    """Pull the counts off the response object, or zero if absent.

    Zero is an honest "the provider did not say" and shows up in the meter
    as such. Estimating here would quietly corrupt the one number the cost claim
    rests on.
    """
    usage = getattr(response, "usage", None)
    if usage is None:
        return 0, 0, 0
    details = getattr(usage, "prompt_tokens_details", None)
    cached = getattr(details, "cached_tokens", 0) or 0 if details else 0
    return (
        getattr(usage, "prompt_tokens", 0) or 0,
        getattr(usage, "completion_tokens", 0) or 0,
        int(cached),
    )


class OpenAIClient:
    """Implements the LlmClient protocol."""

    def complete(self, request: LlmRequest) -> LlmResponse:
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - depends on the machine
            raise LlmError(
                "the openai package is not installed; `pip install openai` or run "
                "with SENTINELOPS_LLM_PROVIDER=fake"
            ) from exc

        client = OpenAI(api_key=_api_key(), timeout=REQUEST_TIMEOUT_SECONDS)
        model = model_name()

        # System first and unchanged, so the cached prefix is identical on every
        # call and two areas submitting the same evidence get the same context.
        messages = [{"role": "system", "content": request.system}]
        messages.extend(request.messages)

        started = time.perf_counter()
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=request.max_tokens,
                temperature=0,
                response_format={"type": "json_object"},
            )
        except Exception as exc:  # every SDK failure becomes one boundary error
            raise LlmError(f"{type(exc).__name__} from provider: {exc}") from exc
        latency_ms = int((time.perf_counter() - started) * 1000)

        choices = getattr(response, "choices", None)
        if not choices:
            raise LlmError("provider returned no choices")
        text = choices[0].message.content or ""
        finish = getattr(choices[0], "finish_reason", None)
        if finish == "length":
            raise LlmError(
                f"response hit max_tokens ({request.max_tokens}) and was truncated"
            )

        input_tokens, output_tokens, cached_tokens = _usage(response)

        from ..parsing import extract_json

        return LlmResponse(
            text=text,
            parsed_json=extract_json(text),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_tokens=cached_tokens,
            model=getattr(response, "model", model),
            latency_ms=latency_ms,
            raw={"provider": "openai", "finish_reason": finish},
        )
