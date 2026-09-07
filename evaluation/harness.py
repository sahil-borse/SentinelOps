"""Run both paths over one corpus and write results.md.

The pipeline is run **month by month**, not once at the end. That costs nothing
extra — every instance is still assessed exactly once — but it is the only way
time-to-detection means anything: assessing a year of checks on 31 December
would report that everything was found instantly, which is an artefact of the
harness rather than a property of the system.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from sentinelops.db import connect
from sentinelops.repositories import repositories
from sentinelops.stages.assess import run as assess
from sentinelops.stages.flag import run as flag_stage
from sentinelops.stages.followup import run as followup
from sentinelops.stages.prescreen import run as prescreen
from sentinelops.stages.remediation import reassess_all
from sentinelops.stages.trigger import run_cycle
from sentinelops.synth import generate_corpus

from . import baseline as baseline_module
from . import manual as manual_module
from . import metrics as metrics_module
from .report import write_results

RESULTS_PATH = Path(__file__).resolve().parents[1] / "results.md"

#: The month-ends a scheduled programme would actually run on, plus a final
#: sweep the following spring once every 2026 period has closed and its grace
#: window with it.
#: One cycle a month across the corpus's eighteen-month window, then the
#: vantage point itself. Month by month rather than all at the end, because
#: time-to-detection measured over a single catch-up run measures the harness.
CYCLE_DATES = (
    [date(2026, month, 28) for month in range(1, 13)]
    + [date(2027, month, 28) for month in range(1, 9)]
    + [date(2027, 9, 30)]
)


@dataclass
class Evaluation:
    corpus_fingerprint: str
    seed: int
    cycles: int
    pipeline: dict[str, Any] = field(default_factory=dict)
    baseline: dict[str, Any] = field(default_factory=dict)
    manual: dict[str, Any] = field(default_factory=dict)
    comparison: dict[str, Any] = field(default_factory=dict)


class StaleGroundTruth(RuntimeError):
    """The truth file on disk does not describe the corpus being scored."""


def _require_matching_truth(corpus, truth: dict[str, Any]) -> None:
    """Refuse to score a corpus against ground truth for a different one.

    Both carry the corpus fingerprint, and a mismatch is not a warning: every
    accuracy figure in `results.md` is computed by joining the run to the truth
    file on (control, unit, period), so a truth file generated before the corpus
    changed will happily line up rows that describe *different documents* and
    produce a precision figure that is simply wrong.

    That is not hypothetical. It happened while the corpus was being reshaped:
    a stale truth file put recall at 12.8% for a pipeline that had caught almost
    everything, and the number was plausible enough to have been believed. A
    loud failure is worth far more here than a plausible one.
    """
    on_disk = truth.get("fingerprint", "")
    actual = corpus.fingerprint()
    if on_disk != actual:
        raise StaleGroundTruth(
            f"the truth file describes corpus {on_disk[:16]} but this run uses "
            f"{actual[:16]}; regenerate it with `python -m sentinelops.synth` "
            f"before trusting any accuracy figure"
        )


def run_pipeline(conn, corpus, *, client=None) -> dict[str, Any]:
    """S0 through S4, once per cycle date, then close the loop."""
    from sentinelops.synth import seed_database

    seed_database(conn, corpus)
    screened = 0
    assessed = 0
    remediated = 0
    reminders = 0
    escalations = 0
    for as_of in CYCLE_DATES:
        run_cycle(conn, as_of)
        screen = prescreen(conn, as_of)
        screened += screen.considered
        if screen.to_assess:
            report = assess(conn, screen.to_assess, as_of, client=client)
            assessed += len(report.assessed)
        flag_stage(conn, as_of)
        # the chase runs every cycle, because a measurement of follow-up that
        # skips the follow-up measures nothing
        chase = followup(conn, as_of)
        reminders += len(chase.reminded)
        escalations += len(chase.escalated)
        # remediation is picked up on the cycle after it is filed, not all at
        # the end — otherwise time-to-resolution measures the harness
        remediated += len(reassess_all(conn, as_of, client=client))
    return {
        "screened": screened, "assessed": assessed, "remediated": remediated,
        "reminders": reminders, "escalations": escalations,
    }


def evaluate(
    *, seed: int | None = None, client=None, force_baseline: bool = False
) -> tuple[Evaluation, str]:
    corpus = generate_corpus() if seed is None else generate_corpus(seed=seed)
    truth = metrics_module.load_ground_truth(corpus.year)
    _require_matching_truth(corpus, truth)
    truth_rows = metrics_module.truth_by_instance(truth)

    conn = connect(":memory:")
    run_stats = run_pipeline(conn, corpus, client=client)

    # Scored on the original judgement, not the state after remediation — see
    # `metrics.first_verdicts`.
    verdicts = metrics_module.first_verdicts(conn)
    pipeline = {
        **run_stats,
        "missed": metrics_module.missed_checks(conn, truth_rows),
        "detection": metrics_module.time_to_detection(conn),
        "consistency": metrics_module.verdict_consistency(conn),
        "zero_model": metrics_module.zero_model_share(conn),
        "tokens": metrics_module.token_usage(conn),
        "actions": metrics_module.action_closure(conn),
        "gap_detection": metrics_module.score_gap_detection(verdicts, truth_rows),
        "chain": repositories(conn)["audit"].verify_chain(),
        "audit_events": len(repositories(conn)["audit"].read_all()),
    }

    baseline_result, was_cached = baseline_module.run(
        corpus, client=client, force=force_baseline
    )
    baseline = {
        "result": baseline_result,
        "cached": was_cached,
        "gap_detection": metrics_module.score_gap_detection(
            baseline_result.verdicts, truth_rows
        ),
    }

    outcome = manual_module.simulate(corpus, seed=4242)
    sensitivity = manual_module.sensitivity(corpus)
    manual_verdicts = {
        r.instance_key: r.verdict for r in outcome.reviews if r.verdict
    }
    manual = {
        "outcome": outcome,
        "missed_rate": outcome.missed_rate,
        "due": outcome.due,
        "missed": len(outcome.missed),
        "detection": metrics_module._spread(outcome.days_to_detection()),
        "consistency": manual_module.disagreement_on_identical_evidence(
            corpus, outcome
        ),
        "gap_detection": metrics_module.score_gap_detection(
            manual_verdicts, truth_rows
        ),
        "sensitivity": sensitivity,
    }

    pipeline_tokens = pipeline["tokens"]["total_tokens"]
    baseline_tokens = baseline_result.total_tokens
    comparison = {
        "token_reduction_factor": (
            baseline_tokens / pipeline_tokens if pipeline_tokens else 0.0
        ),
        "tokens_saved": baseline_tokens - pipeline_tokens,
        "call_reduction_factor": (
            baseline_result.model_calls / pipeline["tokens"]["calls"]
            if pipeline["tokens"]["calls"] else 0.0
        ),
        "missed_check_delta": outcome.missed_rate - pipeline["missed"]["rate"],
        "detection_speedup_days": (
            manual["detection"]["median"] - pipeline["detection"]["median"]
        ),
    }

    evaluation = Evaluation(
        corpus_fingerprint=corpus.fingerprint(),
        seed=corpus.seed,
        cycles=len(CYCLE_DATES),
        pipeline=pipeline,
        baseline=baseline,
        manual=manual,
        comparison=comparison,
    )
    markdown = write_results(evaluation, corpus, truth, RESULTS_PATH)
    conn.close()
    return evaluation, markdown
