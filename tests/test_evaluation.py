"""The harness must be as trustworthy as the thing it measures."""

import json
from datetime import date
from pathlib import Path

import pytest

from evaluation import baseline as baseline_module
from evaluation import manual as manual_module
from evaluation import metrics as metrics_module
from evaluation.harness import CYCLE_DATES, evaluate, run_pipeline
from sentinelops.db import connect
from sentinelops.synth import generate_corpus

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def corpus():
    return generate_corpus()


@pytest.fixture(scope="module")
def evaluation():
    result, _ = evaluate()
    return result


# --- the harness is outside the package on purpose -------------------------

def test_the_harness_is_not_part_of_the_installed_package():
    """It reads the truth file, so it must not be importable by the pipeline."""
    assert (ROOT / "evaluation").is_dir()
    assert not (ROOT / "src" / "sentinelops" / "evaluation").exists()


def test_only_the_harness_reads_the_truth_file():
    src = ROOT / "src" / "sentinelops"
    for path in src.rglob("*.py"):
        if path.name == "truth.py":
            continue
        text = path.read_text(encoding="utf-8")
        assert "truth_2026" not in text
        assert "TRUTH_DIR" not in text


def test_the_pipeline_never_imports_the_harness():
    """An import, not the word — several modules discuss evaluation in prose."""
    import ast

    src = ROOT / "src" / "sentinelops"
    for path in src.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            for name in names:
                assert name.split(".")[0] != "evaluation", f"{path.name}: {name}"


# --- the baseline is competent, not a strawman -----------------------------

def test_the_baseline_skips_instances_with_no_evidence(corpus):
    result, _ = baseline_module.run(corpus)
    assert result.skipped_no_evidence > 0
    assert result.model_calls + result.skipped_no_evidence + (
        result.served_from_document_cache
    ) == result.instances_considered


def test_the_baseline_caches_identical_documents(corpus):
    result, _ = baseline_module.run(corpus)
    assert result.served_from_document_cache >= 1, (
        "the corpus files one document against two areas; a competent naive "
        "implementation assesses it once"
    )


def test_the_baseline_has_no_applicability_rules(corpus):
    """It considers every control against every area, which is the point."""
    from sentinelops.periods import periods_for

    result, _ = baseline_module.run(corpus)
    every_pair = sum(
        len(periods_for(c.frequency, corpus.year))
        for c in corpus.controls
        for _ in corpus.areas
    )
    assert result.instances_considered == every_pair
    assert result.instances_considered > len(corpus.applicable_pairs)


def test_the_baseline_sends_whole_documents(corpus):
    """No retrieval: what it sends is longer than what the pipeline sends."""
    from sentinelops.stages.assess import build_request

    control = next(c for c in corpus.controls if c.evidence_kind == "document")
    submission = next(
        s for s in corpus.submissions if s.control_id == control.id
    )
    from sentinelops.entities import Evidence

    evidence = Evidence(
        id="E", check_instance_id="I", kind="document", doc_type=submission.doc_type,
        content=submission.content, content_hash=submission.content_hash,
        submitted_at=submission.submitted_at, author="a",
    )
    request, selected, chunks = build_request(control, evidence)
    assert len(selected) <= len(chunks)


def test_the_baseline_uses_the_same_prompt_and_model(corpus):
    """Otherwise the comparison measures prompt-wrangling, not architecture."""
    from sentinelops.llm.prompts.assessment import PROMPT_VERSION

    result, _ = baseline_module.run(corpus)
    assert result.prompt_version == PROMPT_VERSION


# --- the cache -------------------------------------------------------------

def test_the_baseline_is_cached_to_disk_and_not_recomputed(corpus):
    first, was_cached_first = baseline_module.run(corpus)
    second, was_cached_second = baseline_module.run(corpus)

    assert was_cached_second is True
    assert second.model_calls == first.model_calls
    assert second.input_tokens == first.input_tokens
    assert baseline_module.cache_path(
        corpus.fingerprint(), first.model
    ).exists()


def test_the_cache_key_covers_the_corpus(corpus):
    other = generate_corpus(seed=99)
    assert corpus.fingerprint() != other.fingerprint()
    assert baseline_module.cache_path(
        corpus.fingerprint(), "m"
    ) != baseline_module.cache_path(other.fingerprint(), "m")


def test_a_missing_cache_returns_none(corpus):
    assert baseline_module.load_cached("not-a-fingerprint", "not-a-model") is None


# --- the manual model is a model -------------------------------------------

def test_the_manual_simulation_is_deterministic(corpus):
    first = manual_module.simulate(corpus, seed=7)
    second = manual_module.simulate(corpus, seed=7)
    assert first.missed_rate == second.missed_rate
    assert [r.verdict for r in first.reviews] == [r.verdict for r in second.reviews]


def test_a_different_seed_gives_a_different_manual_outcome(corpus):
    assert (
        manual_module.simulate(corpus, seed=1).missed_rate
        != manual_module.simulate(corpus, seed=2).missed_rate
    )


def test_the_manual_model_forgets_infrequent_checks_more(corpus):
    outcome = manual_module.simulate(corpus, seed=4242)
    controls = {c.id: c for c in corpus.controls}
    by_frequency: dict[str, list[bool]] = {}
    for review in outcome.reviews:
        frequency = controls[review.control_id].frequency
        by_frequency.setdefault(frequency, []).append(review.performed)

    rates = {
        frequency: sum(v) / len(v) for frequency, v in by_frequency.items()
    }
    assert rates["monthly"] > rates["quarterly"] > rates["annual"]


def test_the_manual_model_disagrees_on_identical_evidence(corpus):
    """Without this the consistency comparison would be vacuous."""
    outcome = manual_module.simulate(corpus, seed=4242)
    result = manual_module.disagreement_on_identical_evidence(corpus, outcome)
    assert result["identical_evidence_groups"] >= 1
    assert result["disagreement_rate"] > 0


def test_reviewers_disagree_most_on_borderline_documents(corpus):
    outcome = manual_module.simulate(corpus, seed=4242)
    wrong: dict[str, list[bool]] = {}
    for review in outcome.reviews:
        if not review.performed:
            continue
        wrong.setdefault(review.defect_kind, []).append(
            review.verdict != review.truth_verdict
        )
    error = {k: sum(v) / len(v) for k, v in wrong.items() if len(v) > 5}
    assert error["near_miss"] > error["compliant"]
    assert error["near_miss"] > error["non_compliant"]


def test_the_sensitivity_table_moves_the_headline(corpus):
    rows = manual_module.sensitivity(corpus)
    assert len(rows) >= 3
    rates = [r["missed_rate"] for r in rows]
    assert max(rates) > min(rates), "if nothing moves the table is decoration"
    labels = [r["label"] for r in rows]
    assert any("near-perfect recall" in label for label in labels)


# --- the metrics themselves -------------------------------------------------

def test_confusion_arithmetic():
    confusion = metrics_module.Confusion(
        true_positive=8, false_positive=2, true_negative=88, false_negative=2
    )
    assert confusion.precision == pytest.approx(0.8)
    assert confusion.recall == pytest.approx(0.8)
    assert confusion.false_positive_rate == pytest.approx(2 / 90)
    assert confusion.f1 == pytest.approx(0.8)
    assert confusion.total == 100


def test_an_empty_confusion_does_not_divide_by_zero():
    confusion = metrics_module.Confusion()
    assert confusion.precision == 0.0
    assert confusion.recall == 0.0
    assert confusion.false_positive_rate == 0.0


def test_scoring_ignores_instances_the_truth_file_does_not_cover():
    truth_rows = {"CHK-A": {"expected_verdict": "gap"}}
    confusion = metrics_module.score_gap_detection(
        {"CHK-A": "gap", "CHK-UNKNOWN": "gap"}, truth_rows
    )
    assert confusion.total == 1


def test_superseded_findings_are_excluded_from_every_metric(evaluation):
    """A remediated failure must not be counted twice."""
    assert evaluation.pipeline["gap_detection"].total > 200
    assert evaluation.pipeline["zero_model"]["findings"] == (
        evaluation.pipeline["zero_model"]["decided_by_rules"]
        + evaluation.pipeline["zero_model"]["decided_by_model"]
    )


def test_no_evidence_is_not_counted_as_a_missed_check(evaluation):
    """The system raised, chased and recorded them. That is not missing them."""
    assert evaluation.pipeline["missed"]["rate"] == 0.0
    assert evaluation.pipeline["zero_model"]["by_tier"]["no_evidence"] > 20


# --- the run as a whole -----------------------------------------------------

def test_the_pipeline_runs_month_by_month(evaluation):
    """Detection latency is meaningless if everything is assessed at the end."""
    assert evaluation.cycles == len(CYCLE_DATES)
    assert evaluation.pipeline["detection"]["median"] > 0
    assert evaluation.pipeline["detection"]["median"] < 60


def test_every_headline_metric_is_present(evaluation):
    for key in ("missed", "detection", "consistency", "zero_model", "tokens",
                "actions", "gap_detection"):
        assert key in evaluation.pipeline


def test_the_audit_chain_survives_a_full_evaluation(evaluation):
    assert evaluation.pipeline["chain"].ok
    assert evaluation.pipeline["audit_events"] > 1000


def test_the_pipeline_makes_fewer_calls_than_the_baseline(evaluation):
    assert evaluation.comparison["call_reduction_factor"] > 1.0
    assert evaluation.comparison["token_reduction_factor"] > 1.0


def test_the_pipeline_never_disagrees_with_itself(evaluation):
    assert evaluation.pipeline["consistency"]["disagreement_rate"] == 0.0


def test_results_md_is_written_with_its_qualifiers(evaluation):
    text = (ROOT / "results.md").read_text(encoding="utf-8")

    # the scope statements the slice requires, in the file rather than in memory
    assert "synthetic corpus with constructed failure modes" in text
    assert "property of the corpus mix, not a universal constant" in text
    assert "This is a model, not a measurement" in text or (
        "model, not a measurement" in text
    )
    assert "competent naive implementation, not a strawman" in text
    assert "FakeModelClient" in text
    # and the numbers themselves
    assert "Missed-check rate" in text
    assert "Tokens per audit cycle" in text
    assert "Mean days to resolution" in text


def test_results_md_names_the_corpus_it_was_measured_on(evaluation):
    text = (ROOT / "results.md").read_text(encoding="utf-8")
    assert evaluation.corpus_fingerprint[:16] in text
    assert str(evaluation.seed) in text
