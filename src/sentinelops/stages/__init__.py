"""The pipeline stages of section 4.

    S0 applicability  zero tokens  <- slice 3, here
    S1 trigger        zero tokens  <- slice 4
    S2 pre-screen     zero tokens  <- slice 5
    S3 assess         model call   <- slice 6
    S4 flag & route   zero tokens  <- slice 7

Only S3 may import from `llm/`. The rest are rules, and a test asserts they
have no path to a model.
"""

from .applicability import (
    Applicability,
    Condition,
    KNOWN_ATTRIBUTES,
    applicability_matrix,
    applicable_controls,
    applicable_pairs,
    evaluate,
    validate_expressions,
)

__all__ = [
    "Applicability",
    "Condition",
    "KNOWN_ATTRIBUTES",
    "applicability_matrix",
    "applicable_controls",
    "applicable_pairs",
    "evaluate",
    "validate_expressions",
]
