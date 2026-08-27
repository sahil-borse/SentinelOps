"""Writes the ground-truth file. Write-only, on purpose.

This module has no read function and no loader. The truth file lives outside
`src/` entirely, under `data/truth/`, and nothing in the pipeline may reach it —
`tests/test_truth_isolation.py` asserts that no module under `src/sentinelops/`
other than this one so much as mentions it.

The evaluation harness in slice 8 reads the file directly. That is the only
reader there will ever be, and it runs after the pipeline has already decided.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

#: Repo root / data / truth — deliberately outside the package.
TRUTH_DIR = Path(__file__).resolve().parents[3] / "data" / "truth"


def truth_path(year: int) -> Path:
    return TRUTH_DIR / f"truth_{year}.json"


def write_truth_file(payload: dict[str, Any], year: int) -> Path:
    path = truth_path(year)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    return path
