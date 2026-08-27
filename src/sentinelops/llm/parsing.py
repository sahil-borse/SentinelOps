"""JSON extraction, repair and schema validation. Boundary-internal."""

from __future__ import annotations

import json
import re
from typing import Any

from .protocol import LlmError

_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


def extract_json(text: str) -> dict[str, Any]:
    """Parse model text into a dict, repairing the usual damage.

    Handles a bare object, a fenced block, and prose wrapped around an object.
    Anything else is a provider error, not a caller error.
    """
    candidates = [text.strip()]
    fenced = _FENCE.search(text)
    if fenced:
        candidates.append(fenced.group(1).strip())
    first, last = text.find("{"), text.rfind("}")
    if first != -1 and last > first:
        candidates.append(text[first : last + 1])
    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    raise LlmError(f"no JSON object in response: {text[:200]!r}")


def validate(payload: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    """Check required keys and enum membership. Deliberately shallow."""
    missing = [k for k in schema.get("required", []) if k not in payload]
    if missing:
        raise LlmError(f"response missing required keys: {missing}")
    for key, spec in schema.get("properties", {}).items():
        if "enum" in spec and key in payload and payload[key] not in spec["enum"]:
            raise LlmError(f"{key}={payload[key]!r} not in {spec['enum']}")
    return payload


def with_retries(call, attempts: int = 3):
    """Retry a provider call, mapping the final failure to LlmError."""
    last: Exception | None = None
    for _ in range(attempts):
        try:
            return call()
        except LlmError as exc:
            last = exc
        except Exception as exc:  # provider SDK exceptions are mapped here
            last = LlmError(str(exc))
    raise last if isinstance(last, LlmError) else LlmError("call failed")
