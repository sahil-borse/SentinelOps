"""Provider boundary.

Everything model-specific lives under this package: retries, JSON parsing and
repair, schema validation, error mapping and token extraction. No provider SDK
type may cross out of it — `tests/test_llm_boundary.py` enforces that.
"""

from .factory import get_client
from .metering import TokenMeter
from .protocol import LlmClient, LlmError, LlmRequest, LlmResponse

__all__ = [
    "LlmClient",
    "LlmError",
    "LlmRequest",
    "LlmResponse",
    "TokenMeter",
    "get_client",
]
