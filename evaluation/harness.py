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
from sentinelops.periods import monthly_cycles
from sentinelops.synth.calendar import CORPUS_WINDOW, SIMULATED_TODAY

from . import baseline as baseline_module
from . import manual as manual_module
from . import metrics as metrics_module
from .report import write_results

RESULTS_PATH = Path(__file__).resolve().parents[1] / "results.md"

#: One cycle a month across the corpus window, ending at the vantage point.
#: Month by month rather than all at the end, because time-to-detection measured
#: over a single catch-up run measures the harness. Stops at SIMULATED_TODAY:
#: running cycles past "today" would detect things before they were due and turn
#: the detection latency negative. Derived from the window rather than written
#: out as two lists of years.
CYCLE_DATES = monthly_cycles(CORPUS_WINDOW, SIMULATED_TODAY) + [SIMULATED_TODAY]


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


def _section_eight(
    conn, *, client=None, recurrence_limit: int | None = None,
) -> dict[str, Any]:
    """Section 8's figures over the finished run. The analytics use no model.

    The client is threaded through rather than left to default. These three
    stages do call a model, and a stage that builds its own client is a stage
    outside whatever cap the caller is holding — which, on a paid run, is the
    difference between a budget and a hope.
    """
    from sentinelops import analytics
    from sentinelops.stages import intelligence, taxonomy

    as_of = CYCLE_DATES[-1]
    # Classification and recurrence are what make "by gap category" and
    # "recurring findings" answerable at all, so they run before the analytics
    # rather than being reported as empty. The taxonomy has to come first: it is
    # read off the findings this run produced, and classification has no
    # fallback list to fall back to.
    taxonomy.derive(conn, as_of, client=client)
    intelligence.classify(conn, as_of, client=client)
    intelligence.detect_recurrence(conn, as_of, client=client, limit=recurrence_limit)
    return analytics.portfolio(
        conn, as_of, window=(CYCLE_DATES[0], as_of)
    )


def run_pipeline(
    conn, corpus, *, client=None, on_cycle=None, per_cycle_limit: int | None = None,
) -> dict[str, Any]:
    """S0 through S4, once per cycle date, then close the loop.

    `on_cycle` is called after each cycle with no arguments. It exists so a run
    that costs real money can be checkpointed to disk as it goes: an in-memory
    database that dies at cycle sixteen has to be paid for all over again.
    """
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
        # `per_cycle_limit` is for a smoke run against a paid provider: assess a
        # few instances a cycle rather than every one due. The rest stay
        # pending and are offered again next cycle, so nothing is marked
        # examined that was not. A run using it measures that the path works,
        # never how accurate it is.
        due = screen.to_assess[:per_cycle_limit] if per_cycle_limit else screen.to_assess
        if due:
            report = assess(conn, due, as_of, client=client)
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
        if on_cycle is not None:
            on_cycle()
    return {
        "screened": screened, "assessed": assessed, "remediated": remediated,
        "reminders": reminders, "escalations": escalations,
    }


def evaluate(
    *, seed: int | None = None, client=None, force_baseline: bool = False,
    results_path: Path = RESULTS_PATH,
) -> tuple[Evaluation, str]:
    corpus = generate_corpus() if seed is None else generate_corpus(seed=seed)
    conn = connect(":memory:")
    run_stats = run_pipeline(conn, corpus, client=client)
    return score(
        conn, corpus, run_stats=run_stats, client=client,
        force_baseline=force_baseline, results_path=results_path,
    )


def score(
    conn, corpus, *, run_stats: dict[str, Any], client=None,
    force_baseline: bool = False, results_path: Path = RESULTS_PATH,
    baseline_result=None, baseline_note: str = "",
) -> tuple[Evaluation, str]:
    """Score a finished run and write `results.md`.

    Separate from `evaluate` so a run that cost real money can be scored from
    the database it produced, rather than replayed a second time to be measured.
    `baseline_result` is for the same reason: the naive baseline is run and
    cached by the caller when the budget allows, and passed in here.
    """
    truth = metrics_module.load_ground_truth(corpus.year)
    _require_matching_truth(corpus, truth)
    truth_rows = metrics_module.truth_by_instance(truth)

    # Scored on the original judgement, not the state after remediation — see
    # `metrics.first_verdicts`.
    verdicts = metrics_module.first_verdicts(conn)
    # The trail wins over whatever the caller carried in. A run scored in the
    # same process and one scored from a saved database now report the same
    # counters, because both read them from the same place.
    pipeline = {
        **run_stats,
        **metrics_module.recover_run_stats(conn),
        "missed": metrics_module.missed_checks(conn, truth_rows, as_of=SIMULATED_TODAY),
        "detection": metrics_module.time_to_detection(conn),
        "consistency": metrics_module.verdict_consistency(conn),
        "zero_model": metrics_module.zero_model_share(conn),
        "tokens": metrics_module.token_usage(conn),
        "actions": metrics_module.action_closure(conn),
        "gap_detection": metrics_module.score_gap_detection(verdicts, truth_rows),
        # Kept so two runs can be compared verdict by verdict, not only in total.
        "first_verdicts": dict(sorted(verdicts.items())),
        "analytics": _section_eight(conn, client=client),
        "recurrence": metrics_module.score_recurrence(conn, truth),
        "chain": repositories(conn)["audit"].verify_chain(),
        "audit_events": len(repositories(conn)["audit"].read_all()),
    }
    # Refuse, rather than score, a run that left due obligations unscheduled.
    metrics_module.require_scheduled(pipeline["missed"])

    if baseline_result is None:
        baseline_result, was_cached = baseline_module.run(
            corpus, client=client, force=force_baseline
        )
    else:
        was_cached = True
    baseline = {
        "result": baseline_result,
        "cached": was_cached,
        "note": baseline_note,
        "gap_detection": metrics_module.score_gap_detection(
            baseline_result.verdicts, truth_rows
        ),
    }

    outcome = manual_module.simulate(corpus, seed=4242, as_of=SIMULATED_TODAY)
    sensitivity = manual_module.sensitivity(corpus, as_of=SIMULATED_TODAY)
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
    markdown = write_results(evaluation, corpus, truth, results_path)
    conn.close()
    return evaluation, markdown
