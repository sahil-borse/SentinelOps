"""Demo scaffolding: the hardcoded slice-1 fixtures and the console report.

Nothing here is part of the compliance engine. It exists so `main.py` holds the
pipeline and nothing else, and so slice 2's synthetic generator has an obvious
place to displace.
"""

from .fixtures import DEMO_AREA, DEMO_CONTROL, DEMO_EVIDENCE_TEXT
from .report import print_run

__all__ = ["DEMO_AREA", "DEMO_CONTROL", "DEMO_EVIDENCE_TEXT", "print_run"]
