"""Assembles the corpus. Same seed in, same bytes out.

Nothing here reaches for the clock or the global `random` module: every draw
comes from one seeded `Random`, and every loop iterates in a fixed sorted order,
so two runs a week apart produce byte-identical evidence and an identical truth
file. `test_synth.py` asserts that by hashing the whole corpus twice.

What the generator does *not* do is decide which checks are due — that is S1,
and it arrives in slice 4. The corpus stops at periods and submissions.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from random import Random
from typing import Any

from ..entities import (
    ComplianceException,
    ControlDefinition,
    EvidenceSubmission,
    ProcessArea,
)
from .areas import PROCESS_AREAS
from .calendar import SIMULATED_TODAY, due_date, periods_for
from .controls import CONTROL_SPECS, SPECS_BY_ID, ControlSpec
from .documents import (
    EXPECTED_VERDICT,
    QUALITIES,
    STRUCTURED_QUALITIES,
    build_context,
    render,
    submitted_at,
)
from .exceptions import COMPLIANCE_EXCEPTIONS, suppresses
from .truth import write_truth_file

DEFAULT_SEED = 20260831
DEFAULT_YEAR = 2026

#: How the unremarkable majority of submissions are drawn. Weighted so that
#: roughly half the corpus is clean — a corpus that is mostly broken makes a
#: precision figure look good for the wrong reason.
QUALITY_WEIGHTS: dict[str, float] = {
    "compliant": 0.52,
    "near_miss": 0.13,
    "partial": 0.09,
    "non_compliant": 0.07,
    "stale": 0.05,
    "wrong_type": 0.04,
    "missing": 0.10,
}

#: Coordinates pinned by hand so the demo always has the same beats to point at,
#: whatever the seeded draw does elsewhere.
SHOWCASE: dict[tuple[str, str, str], str] = {
    ("CTRL-ACCESS-REVIEW", "AREA-CUSTOPS", "2026-Q1"): "near_miss",
    ("CTRL-ACCESS-REVIEW", "AREA-PAYMENTS", "2026-Q2"): "compliant",
    ("CTRL-BACKUP-VERIFY", "AREA-PLATFORM", "2026-03"): "near_miss",
    ("CTRL-TRAINING", "AREA-HR", "2026-Q1"): "compliant",
    ("CTRL-CRYPTO-KEY", "AREA-PAYMENTS", "2026-Q2"): "wrong_type",
    ("CTRL-DPIA", "AREA-MKTG", "2026"): "stale",
    ("CTRL-CUST-COMPLAINTS", "AREA-CUSTOPS", "2026-07"): "missing",
    ("CTRL-INCIDENT-PM", "AREA-PLATFORM", "2026-05"): "non_compliant",
}

#: The same document filed against the same control in two different areas.
#: A central team runs the retention sweep once and submits the identical
#: report to both — so the two verdicts must match, and any divergence is a
#: consistency failure rather than a difference in the evidence.
CONSISTENCY_PAIR = {
    "id": "PAIR-RETENTION-Q2",
    "control_id": "CTRL-DATA-RETENTION",
    "period": "2026-Q2",
    "area_ids": ("AREA-CUSTOPS", "AREA-HR"),
    "quality": "near_miss",
}

#: How many gaps get remediation evidence, so slice 7 has a loop to close.
REMEDIATION_COUNT = 6


@dataclass
class Corpus:
    seed: int
    year: int
    areas: list[ProcessArea]
    controls: list[ControlDefinition]
    exceptions: list[ComplianceException]
    submissions: list[EvidenceSubmission]
    truth_rows: list[dict[str, Any]] = field(default_factory=list)
    applicable_pairs: list[tuple[str, str]] = field(default_factory=list)

    def fingerprint(self) -> str:
        """A hash of everything that must not drift between runs."""
        parts = [f"{s.id}|{s.content_hash}|{s.submitted_at.isoformat()}"
                 for s in self.submissions]
        parts += [repr(sorted(r.items())) for r in self.truth_rows]
        return hashlib.sha256("\n".join(parts).encode()).hexdigest()


def applies(applies_when: dict[str, Any], attributes: dict[str, Any]) -> bool:
    """A deliberately trivial applicability match.

    The real S0 rules engine lands in slice 3 and must reproduce exactly these
    pairings — `test_synth.py` pins them so the two cannot silently diverge.
    An empty expression applies everywhere.
    """
    for key, expected in applies_when.items():
        actual = attributes.get(key)
        if isinstance(expected, list):
            if actual not in expected:
                return False
        elif actual != expected:
            return False
    return True


def _weighted_quality(spec: ControlSpec, rng: Random) -> str:
    allowed = (
        STRUCTURED_QUALITIES if spec.evidence_kind == "structured" else QUALITIES
    )
    weights = [QUALITY_WEIGHTS[q] for q in allowed]
    total = sum(weights)
    draw = rng.random() * total
    running = 0.0
    for quality, weight in zip(allowed, weights):
        running += weight
        if draw <= running:
            return quality
    return allowed[0]


def _truth_row(**kwargs: Any) -> dict[str, Any]:
    row: dict[str, Any] = {
        "submission_id": None,
        "control_id": None,
        "process_area_id": None,
        "period": None,
        "defect_kind": None,
        "expected_verdict": None,
        "failing_clause_index": None,
        "failing_clause_text": None,
        "is_remediation": False,
        "remediates_submission_id": None,
        "consistency_pair_id": None,
        "note": "",
    }
    row.update(kwargs)
    return row


def generate_corpus(seed: int = DEFAULT_SEED, year: int = DEFAULT_YEAR) -> Corpus:
    rng = Random(seed)
    areas_by_id = {a.id: a for a in PROCESS_AREAS}

    corpus = Corpus(
        seed=seed,
        year=year,
        areas=list(PROCESS_AREAS),
        controls=[spec.definition() for spec in CONTROL_SPECS],
        exceptions=list(COMPLIANCE_EXCEPTIONS),
        submissions=[],
    )

    # The shared retention report, rendered once and filed against two areas.
    pair_spec = next(s for s in CONTROL_SPECS if s.id == CONSISTENCY_PAIR["control_id"])
    pair_period = next(
        p for p in periods_for(pair_spec.frequency, year)
        if p.label == CONSISTENCY_PAIR["period"]
    )
    pair_rng = Random(seed + 1)
    pair_context = build_context(
        pair_spec, areas_by_id[CONSISTENCY_PAIR["area_ids"][0]], pair_period, pair_rng
    )
    pair_context["owner"] = "J. Whitfield"
    pair_context["team"] = "Group Shared Services"
    pair_context["area"] = "Group Shared Services"
    pair_evidence = render(
        pair_spec,
        areas_by_id[CONSISTENCY_PAIR["area_ids"][0]],
        pair_period,
        CONSISTENCY_PAIR["quality"],
        pair_rng,
        context=pair_context,
    )

    sequence = 0
    for spec in sorted(CONTROL_SPECS, key=lambda s: s.id):
        for area in sorted(PROCESS_AREAS, key=lambda a: a.id):
            if not applies(spec.applies_when, area.attributes):
                continue
            corpus.applicable_pairs.append((spec.id, area.id))

            for period in periods_for(spec.frequency, year):
                coords = (spec.id, area.id, period.label)
                excused = next(
                    (
                        exc
                        for exc in COMPLIANCE_EXCEPTIONS
                        if suppresses(exc, spec.id, area.id, period.end)
                    ),
                    None,
                )
                if excused is not None:
                    corpus.truth_rows.append(
                        _truth_row(
                            control_id=spec.id,
                            process_area_id=area.id,
                            period=period.label,
                            defect_kind="exception_suppressed",
                            note=f"Suppressed by {excused.id}, expires "
                                 f"{excused.expires_at}.",
                        )
                    )
                    continue

                is_pair = (
                    spec.id == CONSISTENCY_PAIR["control_id"]
                    and period.label == CONSISTENCY_PAIR["period"]
                    and area.id in CONSISTENCY_PAIR["area_ids"]
                )
                quality = (
                    CONSISTENCY_PAIR["quality"]
                    if is_pair
                    else SHOWCASE.get(coords) or _weighted_quality(spec, rng)
                )

                if quality == "missing":
                    corpus.truth_rows.append(
                        _truth_row(
                            control_id=spec.id,
                            process_area_id=area.id,
                            period=period.label,
                            defect_kind="missing",
                            expected_verdict=EXPECTED_VERDICT["missing"],
                            note="No evidence was ever submitted for this period.",
                        )
                    )
                    continue

                evidence = (
                    pair_evidence if is_pair else render(spec, area, period, quality, rng)
                )
                sequence += 1
                filed = submitted_at(spec, period, quality, rng)
                submission = EvidenceSubmission(
                    id=f"SUB-{sequence:04d}",
                    control_id=spec.id,
                    process_area_id=area.id,
                    period=period.label,
                    kind=evidence.kind,
                    doc_type=evidence.doc_type,
                    content=evidence.content,
                    content_hash=hashlib.sha256(evidence.content.encode()).hexdigest(),
                    submitted_at=datetime.combine(filed, time(9, 30)),
                    author=area.owner_name,
                    is_remediation=False,
                )
                corpus.submissions.append(submission)
                corpus.truth_rows.append(
                    _truth_row(
                        submission_id=submission.id,
                        control_id=spec.id,
                        process_area_id=area.id,
                        period=period.label,
                        defect_kind=quality,
                        expected_verdict=evidence.expected_verdict,
                        failing_clause_index=evidence.failing_clause_index,
                        failing_clause_text=evidence.failing_clause_text,
                        consistency_pair_id=CONSISTENCY_PAIR["id"] if is_pair else None,
                        note=(
                            f"Filed {filed.isoformat()}, due "
                            f"{due_date(period, spec.grace_days).isoformat()}."
                        ),
                    )
                )

    _add_remediations(corpus, rng)
    return corpus


def _add_remediations(corpus: Corpus, rng: Random) -> None:
    """Follow-up evidence that fixes an earlier gap, so the loop can close.

    Submitted against the same control, area and period as the failure it
    answers — remediation resolves the check that failed, it does not open a
    new one.
    """
    specs_by_id = {s.id: s for s in CONTROL_SPECS}
    areas_by_id = {a.id: a for a in PROCESS_AREAS}
    by_id = {s.id: s for s in corpus.submissions}

    candidates = [
        row
        for row in corpus.truth_rows
        if row["expected_verdict"] == "gap"
        and row["defect_kind"] in ("near_miss", "non_compliant")
        and row["submission_id"] is not None
    ][:REMEDIATION_COUNT]

    sequence = len(corpus.submissions)
    for row in candidates:
        original = by_id[row["submission_id"]]
        spec = specs_by_id[original.control_id]
        area = areas_by_id[original.process_area_id]
        period = next(
            p for p in periods_for(spec.frequency, corpus.year) if p.label == original.period
        )
        evidence = render(spec, area, period, "compliant", rng)
        sequence += 1
        # Dated from the original submission, not from the period, so a late
        # filing still gets a remediation that lands after it.
        filed = original.submitted_at.date() + timedelta(days=rng.randrange(14, 40))
        assert filed <= SIMULATED_TODAY
        submission = EvidenceSubmission(
            id=f"SUB-{sequence:04d}",
            control_id=spec.id,
            process_area_id=area.id,
            period=period.label,
            kind=evidence.kind,
            doc_type=evidence.doc_type,
            content=evidence.content,
            content_hash=hashlib.sha256(evidence.content.encode()).hexdigest(),
            submitted_at=datetime.combine(filed, time(16, 0)),
            author=area.owner_name,
            is_remediation=True,
        )
        corpus.submissions.append(submission)
        corpus.truth_rows.append(
            _truth_row(
                submission_id=submission.id,
                control_id=spec.id,
                process_area_id=area.id,
                period=period.label,
                defect_kind="remediation",
                expected_verdict="compliant",
                is_remediation=True,
                remediates_submission_id=original.id,
                note=f"Remediation for {original.id}, filed {filed.isoformat()}.",
            )
        )


def _exception_truth(
    exception: ComplianceException, corpus: Corpus
) -> dict[str, Any]:
    """What an exception is expected to do, so slice 8 can score it.

    An exception in force when a period opens suppresses it and no check is ever
    raised. One granted after the obligation is already open cannot suppress
    anything — it waives the open check instead. Recording which is which here
    means the harness scores against a stated expectation rather than against
    whatever the pipeline happened to do.
    """
    spec = SPECS_BY_ID.get(exception.control_id)
    suppressed = (
        [
            period.label
            for period in periods_for(spec.frequency, corpus.year)
            if suppresses(exception, exception.control_id, exception.process_area_id,
                          period.end)
        ]
        if spec
        else []
    )
    return {
        "id": exception.id,
        "control_id": exception.control_id,
        "process_area_id": exception.process_area_id,
        "status": exception.status,
        "approved_by": exception.approved_by,
        "granted_at": exception.granted_at.isoformat(),
        "expires_at": exception.expires_at.isoformat(),
        "expected_effect": "suppression" if suppressed else (
            "none" if exception.status == "revoked" else "waiver"
        ),
        "suppresses_periods": suppressed,
    }


def truth_payload(corpus: Corpus) -> dict[str, Any]:
    """Everything the slice-8 harness needs to score the pipeline."""
    kinds: dict[str, int] = {}
    for row in corpus.truth_rows:
        kinds[row["defect_kind"]] = kinds.get(row["defect_kind"], 0) + 1
    return {
        "seed": corpus.seed,
        "year": corpus.year,
        "generated_by": "sentinelops.synth.generate",
        "simulated_today": SIMULATED_TODAY.isoformat(),
        "quality_to_expected_verdict": dict(EXPECTED_VERDICT),
        "counts": {
            "areas": len(corpus.areas),
            "controls": len(corpus.controls),
            "applicable_pairs": len(corpus.applicable_pairs),
            "submissions": len(corpus.submissions),
            "truth_rows": len(corpus.truth_rows),
            "by_defect_kind": dict(sorted(kinds.items())),
        },
        "consistency_pairs": [dict(CONSISTENCY_PAIR)],
        "exceptions": [_exception_truth(e, corpus) for e in corpus.exceptions],
        "fingerprint": corpus.fingerprint(),
        "rows": corpus.truth_rows,
    }


def write_truth(corpus: Corpus):
    return write_truth_file(truth_payload(corpus), corpus.year)


def seed_database(conn, corpus: Corpus) -> None:
    """Load the corpus into SQLite.

    Areas, controls, exceptions and submissions only. CheckInstances, Evidence,
    Findings and Actions are produced by the pipeline, never by the generator.
    """
    from ..repositories import repositories

    repo = repositories(conn)
    for area in corpus.areas:
        repo["areas"].add(area)
    for control in corpus.controls:
        repo["controls"].add(control)
    for exception in corpus.exceptions:
        repo["exceptions"].add(exception)
    for submission in corpus.submissions:
        repo["submissions"].add(submission)
    repo["audit"].append(
        actor="system",
        owner="synthetic generator",
        action="corpus_seeded",
        entity_type="Corpus",
        entity_id=str(corpus.seed),
        detail={
            "areas": len(corpus.areas),
            "controls": len(corpus.controls),
            "submissions": len(corpus.submissions),
            "fingerprint": corpus.fingerprint()[:16],
        },
    )
