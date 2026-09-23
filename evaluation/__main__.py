"""Run the evaluation on the stub and write results.md.

    python -m evaluation            # refuses to overwrite a measured run
    python -m evaluation --force    # overwrite it anyway
    python -m evaluation --out somewhere.md

This writes a **stub** run. When `results.md` holds a run measured against a
real provider, overwriting it destroys the only record of work that was paid
for — which has happened twice here, once from a test fixture and once from
this command line. It is cheap to regenerate a stub run and expensive to
regenerate a real one, so the asymmetry decides the default: refuse, and say
how to override.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .harness import RESULTS_PATH, evaluate
from .report import headline_table

#: Written into `results.md` by `report.py` whenever the run behind it used a
#: provider rather than the stub.
MEASURED = "These runs used a real provider"


def measured(path: Path) -> bool:
    return path.exists() and MEASURED in path.read_text(encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Score both paths on the stub.")
    parser.add_argument("--out", type=Path, default=RESULTS_PATH)
    parser.add_argument("--force", action="store_true",
                        help="overwrite a results file measured on a real provider")
    args = parser.parse_args(argv)

    if measured(args.out) and not args.force:
        print(
            f"{args.out} holds a run measured against a real provider.\n"
            f"A stub run would replace figures that cost money to produce.\n\n"
            f"  python -m evaluation --out /tmp/stub_results.md   # write elsewhere\n"
            f"  python -m evaluation --force                      # overwrite anyway\n\n"
            f"To rebuild it from the saved run instead:\n"
            f"  python -m evaluation.real_run score --baseline-model gpt-4.1-mini",
            file=sys.stderr,
        )
        return 1

    evaluation, _ = evaluate(results_path=args.out)
    print(headline_table(evaluation))
    print()
    print(f"written: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
