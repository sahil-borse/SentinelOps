"""Seeded synthetic corpus — section 7 of the build spec.

    from sentinelops.synth import generate_corpus, seed_database, write_truth

    corpus = generate_corpus()          # same seed, same bytes, every run
    seed_database(conn, corpus)         # areas, controls, exceptions, submissions
    write_truth(corpus)                 # -> the ground-truth file

The truth file is written by this package and read by nothing inside it.
"""

from .areas import PROCESS_AREAS
from .calendar import SIMULATED_TODAY, Period, due_date, periods_for
from .controls import CONTROL_DEFINITIONS, CONTROL_SPECS, STRUCTURED_CONTROL_IDS
from .exceptions import COMPLIANCE_EXCEPTIONS
from .generate import (
    DEFAULT_SEED,
    DEFAULT_YEAR,
    Corpus,
    generate_corpus,
    seed_database,
    truth_payload,
    write_truth,
)

__all__ = [
    "CONTROL_DEFINITIONS",
    "CONTROL_SPECS",
    "COMPLIANCE_EXCEPTIONS",
    "Corpus",
    "DEFAULT_SEED",
    "DEFAULT_YEAR",
    "PROCESS_AREAS",
    "Period",
    "SIMULATED_TODAY",
    "STRUCTURED_CONTROL_IDS",
    "due_date",
    "generate_corpus",
    "periods_for",
    "seed_database",
    "truth_payload",
    "write_truth",
]
