"""Run the evaluation and write results.md.

    python -m evaluation
"""

from __future__ import annotations

from .harness import RESULTS_PATH, evaluate
from .report import headline_table


def main() -> None:
    evaluation, _ = evaluate()
    print(headline_table(evaluation))
    print()
    print(f"written: {RESULTS_PATH}")


if __name__ == "__main__":
    main()
