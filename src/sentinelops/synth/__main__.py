"""Regenerate the corpus and write the truth file.

    python -m sentinelops.synth

Prints one sample of each evidence shape so the corpus can be eyeballed without
opening the database.
"""

from __future__ import annotations

import json

from .controls import SPECS_BY_ID
from .generate import generate_corpus, truth_payload, write_truth


def _rule(title: str) -> None:
    print(f"\n{title}\n{'=' * len(title)}")


def _sample(corpus, predicate):
    by_id = {s.id: s for s in corpus.submissions}
    row = next(r for r in corpus.truth_rows if predicate(r))
    return by_id[row["submission_id"]], row


def main() -> None:
    corpus = generate_corpus()
    path = write_truth(corpus)
    payload = truth_payload(corpus)

    _rule("CORPUS")
    print(f"  seed {corpus.seed}   fingerprint {corpus.fingerprint()[:16]}")
    for key, value in payload["counts"].items():
        print(f"  {key:<20} {value}")

    for label, predicate in (
        ("COMPLIANT DOCUMENT", lambda r: r["defect_kind"] == "compliant"
            and SPECS_BY_ID[r["control_id"]].evidence_kind == "document"),
        ("NEAR-MISS DOCUMENT", lambda r: r["defect_kind"] == "near_miss"
            and SPECS_BY_ID[r["control_id"]].evidence_kind == "document"),
        ("STRUCTURED EVIDENCE (clean)", lambda r: r["defect_kind"] == "compliant"
            and SPECS_BY_ID[r["control_id"]].evidence_kind == "structured"),
        ("STRUCTURED EVIDENCE (one threshold breached)",
            lambda r: r["defect_kind"] == "near_miss"
            and SPECS_BY_ID[r["control_id"]].evidence_kind == "structured"),
    ):
        submission, row = _sample(corpus, predicate)
        _rule(f"{label}  ({submission.id})")
        print(f"  {submission.control_id} / {submission.process_area_id} /"
              f" {submission.period}   doc_type={submission.doc_type}")
        print()
        for line in submission.content.splitlines():
            print(f"  | {line}")
        print()
        print(f"  truth: {json.dumps(row, indent=2, default=str)}")

    _rule("EXCEPTIONS")
    for exception in corpus.exceptions:
        print(f"  {exception.id}  {exception.status:<8} {exception.control_id}"
              f" / {exception.process_area_id}")
        print(f"        {exception.granted_at} -> {exception.expires_at}"
              f"   approved by {exception.approved_by}")

    _rule("TRUTH FILE")
    print(f"  {path}")


if __name__ == "__main__":
    main()
