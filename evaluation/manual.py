"""A simulated manual compliance process, and an honest account of what it is.

**This is a model, not a measurement.** Nobody ran a spreadsheet-based control
programme alongside this system for a year. Every number below is an assumption
I chose, and the comparison is only worth what the assumptions are worth. They
are all in `ManualAssumptions` so they can be argued with, changed, and their
effect on the headline figures seen immediately — which is the least a claim
like "missed-check rate falls from X to Y" deserves.

The model has three parts, each standing for something the statement names.

**Forgetting.** "Dependent on teams remembering when and what needs to be
reviewed." A check is performed only if somebody remembered it. Recall is
modelled as worse for infrequent controls: a monthly task becomes habit, an
annual one is a diary entry that moves.

**Inconsistency.** "Manual, inconsistent." Two reviewers reading the same
document need not agree, and they disagree most on the documents that are
nearly right — a report satisfying two clauses of three is exactly where
judgement diverges. Reviewers are drawn from a pool and carry a standing
leniency; the same evidence sent to two areas reaches two desks.

**Delay.** "Delayed identification of non-compliance." A manual programme finds
things at its next review point, not when they happen.

Calibration, such as it is: the disagreement rates fall in the range usually
described as moderate inter-rater agreement for subjective document review. No
empirical study of *this* process exists, and results.md says so.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from random import Random

from sentinelops.periods import due_date, periods_for

#: How hard a document is to judge, by the defect that was injected into it.
#: Borderline documents are where reviewers diverge; a blank page is not.
DIFFICULTY: dict[str, float] = {
    "compliant": 0.10,
    "near_miss": 0.80,
    "partial": 0.70,
    "non_compliant": 0.20,
    "adversarial": 0.75,
    "stale": 0.45,
    "wrong_type": 0.25,
    "missing": 0.00,
}


@dataclass(frozen=True)
class ManualAssumptions:
    """Every figure the manual baseline rests on, in one place.

    Change these and re-run: results.md reports whatever they say, and the
    sensitivity table shows how far the headline moves when they are wrong.
    """

    #: Chance a due check is performed at all, by how often it comes round.
    recall_by_frequency: dict[str, float] = field(
        default_factory=lambda: {"monthly": 0.88, "quarterly": 0.76, "annual": 0.62}
    )
    #: How many people share the reviewing.
    reviewer_pool: int = 6
    #: How far a reviewer's judgement sits from the criteria, at the extremes.
    leniency_spread: float = 0.45
    #: Scales difficulty into a chance of reaching the wrong verdict.
    inconsistency: float = 0.55
    #: A manual programme reviews on a cycle; this is that cycle.
    audit_interval_days: int = 90
    #: Time from a review happening to the finding being written up.
    review_lag_days: int = 12
    #: Missed checks surface at the annual audit, if at all.
    annual_audit_lag_days: int = 240

    def describe(self) -> list[tuple[str, str]]:
        return [
            ("recall, monthly control", f"{self.recall_by_frequency['monthly']:.0%}"),
            ("recall, quarterly control", f"{self.recall_by_frequency['quarterly']:.0%}"),
            ("recall, annual control", f"{self.recall_by_frequency['annual']:.0%}"),
            ("reviewer pool", str(self.reviewer_pool)),
            ("leniency spread", f"±{self.leniency_spread}"),
            ("inconsistency factor", str(self.inconsistency)),
            ("review cycle", f"{self.audit_interval_days} days"),
            ("write-up lag", f"{self.review_lag_days} days"),
            ("missed checks surface after", f"{self.annual_audit_lag_days} days"),
        ]


@dataclass
class ManualReview:
    instance_key: str
    control_id: str
    process_area_id: str
    period: str
    performed: bool
    reviewer: str | None
    verdict: str | None
    truth_verdict: str
    due_date: date
    detected_on: date | None
    defect_kind: str


@dataclass
class ManualOutcome:
    reviews: list[ManualReview] = field(default_factory=list)
    assumptions: ManualAssumptions = field(default_factory=ManualAssumptions)

    @property
    def due(self) -> int:
        return len(self.reviews)

    @property
    def missed(self) -> list[ManualReview]:
        return [r for r in self.reviews if not r.performed]

    @property
    def missed_rate(self) -> float:
        return len(self.missed) / self.due if self.due else 0.0

    def days_to_detection(self) -> list[int]:
        return [
            (r.detected_on - r.due_date).days
            for r in self.reviews
            if r.detected_on and r.truth_verdict != "compliant"
        ]


def _verdict_for(rng: Random, leniency: float, truth: str, difficulty: float,
                 assumptions: ManualAssumptions) -> str:
    """One reviewer's reading of one document.

    Wrong readings are not random noise: a lenient reviewer waves a borderline
    document through, a strict one fails an acceptable one. That asymmetry is
    the point — it is what makes two areas reach two answers.
    """
    if rng.random() < 1 - difficulty * assumptions.inconsistency:
        return truth
    if leniency > 0:  # inclined to pass
        return "compliant" if truth != "compliant" else "partial"
    return "gap" if truth == "compliant" else ("gap" if truth == "partial" else "partial")


def simulate(
    corpus,
    *,
    seed: int = 4242,
    year: int = 2026,
    assumptions: ManualAssumptions | None = None,
) -> ManualOutcome:
    """Run the modelled manual programme over the same corpus, deterministically."""
    assumptions = assumptions or ManualAssumptions()
    rng = Random(seed)
    controls = {c.id: c for c in corpus.controls}
    outcome = ManualOutcome(assumptions=assumptions)

    reviewers = [f"Reviewer {chr(65 + n)}" for n in range(assumptions.reviewer_pool)]
    leniency = {
        name: rng.uniform(-assumptions.leniency_spread, assumptions.leniency_spread)
        for name in reviewers
    }

    truth_rows = {
        (r["control_id"], r["process_area_id"], r["period"]): r
        for r in corpus.truth_rows
        if not r["is_remediation"] and r["defect_kind"] != "exception_suppressed"
    }

    for (control_id, area_id, period_label), row in sorted(truth_rows.items()):
        control = controls[control_id]
        period = next(
            p for p in periods_for(control.frequency, year) if p.label == period_label
        )
        deadline = due_date(period, control.grace_days)
        expected = row["expected_verdict"] or "insufficient_evidence"
        kind = row["defect_kind"]

        performed = rng.random() < assumptions.recall_by_frequency[control.frequency]
        if not performed:
            detected = (
                deadline + timedelta(days=assumptions.annual_audit_lag_days)
                if expected != "compliant"
                else None
            )
            outcome.reviews.append(
                ManualReview(
                    instance_key=f"CHK-{control_id.removeprefix('CTRL-')}-"
                                 f"{area_id.removeprefix('AREA-')}-{period_label}",
                    control_id=control_id, process_area_id=area_id,
                    period=period_label, performed=False, reviewer=None,
                    verdict=None, truth_verdict=expected, due_date=deadline,
                    detected_on=detected, defect_kind=kind,
                )
            )
            continue

        reviewer = reviewers[rng.randrange(len(reviewers))]
        verdict = _verdict_for(
            rng, leniency[reviewer], expected, DIFFICULTY.get(kind, 0.4), assumptions
        )
        detected = (
            deadline
            + timedelta(days=assumptions.audit_interval_days
                        + assumptions.review_lag_days)
            if verdict != "compliant"
            else None
        )
        outcome.reviews.append(
            ManualReview(
                instance_key=f"CHK-{control_id.removeprefix('CTRL-')}-"
                             f"{area_id.removeprefix('AREA-')}-{period_label}",
                control_id=control_id, process_area_id=area_id, period=period_label,
                performed=True, reviewer=reviewer, verdict=verdict,
                truth_verdict=expected, due_date=deadline, detected_on=detected,
                defect_kind=kind,
            )
        )
    return outcome


def disagreement_on_identical_evidence(corpus, outcome: ManualOutcome) -> dict:
    """Where the same document reached two desks, did it get the same answer?

    The corpus files one retention report against two areas precisely so this
    question has an answer.
    """
    by_hash: dict[tuple[str, str], list[str]] = {}
    reviews = {r.instance_key: r for r in outcome.reviews}
    for submission in corpus.submissions:
        if submission.is_remediation:
            continue
        key = (submission.control_id, submission.content_hash)
        instance_key = (
            f"CHK-{submission.control_id.removeprefix('CTRL-')}-"
            f"{submission.process_area_id.removeprefix('AREA-')}-{submission.period}"
        )
        by_hash.setdefault(key, []).append(instance_key)

    pairs = {k: v for k, v in by_hash.items() if len(v) > 1}
    disagreements = 0
    for instance_keys in pairs.values():
        verdicts = {
            reviews[k].verdict for k in instance_keys if k in reviews
        }
        if len(verdicts) > 1:
            disagreements += 1
    return {
        "identical_evidence_groups": len(pairs),
        "groups_with_disagreement": disagreements,
        "disagreement_rate": disagreements / len(pairs) if pairs else 0.0,
    }


#: Alternative parameter sets, so the headline can be seen moving. If a claim
#: only holds at one setting of numbers somebody invented, that is worth
#: knowing before it goes on a slide.
VARIANTS: list[tuple[str, ManualAssumptions]] = [
    (
        "as reported",
        ManualAssumptions(),
    ),
    (
        "diligent team (recall +10pp, half the inconsistency)",
        ManualAssumptions(
            recall_by_frequency={"monthly": 0.98, "quarterly": 0.86, "annual": 0.72},
            inconsistency=0.28,
            audit_interval_days=60,
        ),
    ),
    (
        "stretched team (recall -10pp, more drift)",
        ManualAssumptions(
            recall_by_frequency={"monthly": 0.78, "quarterly": 0.66, "annual": 0.52},
            inconsistency=0.70,
            audit_interval_days=120,
        ),
    ),
    (
        "near-perfect recall, inconsistency unchanged",
        ManualAssumptions(
            recall_by_frequency={"monthly": 0.99, "quarterly": 0.99, "annual": 0.99},
        ),
    ),
]


def sensitivity(corpus, *, seed: int = 4242, year: int = 2026) -> list[dict]:
    """Re-run the manual model under other assumptions and report the spread.

    The automated figures do not move: they are a property of the run, not of
    anything assumed. Only the comparison moves, which is the point.
    """
    rows = []
    for label, assumptions in VARIANTS:
        outcome = simulate(corpus, seed=seed, year=year, assumptions=assumptions)
        detected = outcome.days_to_detection()
        rows.append(
            {
                "label": label,
                "missed_rate": outcome.missed_rate,
                "disagreement": disagreement_on_identical_evidence(
                    corpus, outcome
                )["disagreement_rate"],
                "median_detection_days": (
                    sorted(detected)[len(detected) // 2] if detected else 0
                ),
            }
        )
    return rows
