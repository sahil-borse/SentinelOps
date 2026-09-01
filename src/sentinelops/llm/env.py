"""Read `.env` into the environment. Fifteen lines, not a config system.

The API key is read from an environment variable and never appears in source,
in a prompt, or in a log line. `.env` is already gitignored.
"""

from __future__ import annotations

import os
from pathlib import Path

ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


def load_env(path: Path | None = None) -> dict[str, str]:
    """Populate os.environ from a .env file, never overwriting what is set.

    A variable exported in the shell wins over the file, which is what anyone
    debugging expects. Returns the names it set, never the values.
    """
    source = path or ENV_FILE
    loaded: dict[str, str] = {}
    if not source.exists():
        return loaded
    for line in source.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, _, value = line.partition("=")
        name, value = name.strip(), value.strip().strip('"').strip("'")
        if name and name not in os.environ:
            os.environ[name] = value
            loaded[name] = "set"
    return loaded
