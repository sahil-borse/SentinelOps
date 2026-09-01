"""S0 — deterministic, explainable, and permanently free of model calls."""

import ast
from pathlib import Path

import pytest

from sentinelops.entities import ControlDefinition, ProcessArea
from sentinelops.stages.applicability import (
    KNOWN_ATTRIBUTES,
    applicability_matrix,
    applicable_controls,
    applicable_pairs,
    evaluate,
    run,
    validate_expressions,
)
from sentinelops.synth import PROCESS_AREAS, generate_corpus, seed_database
from sentinelops.synth.generate import applies as generator_applies

SRC = Path(__file__).resolve().parents[1] / "src" / "sentinelops"


def _area(ident="A1", **attributes):
    merged = {
        "handles_pii": False,
        "customer_facing": False,
        "has_suppliers": False,
        "region": "EMEA",
        "criticality": "low",
    }
    merged.update(attributes)
    return ProcessArea(ident, ident, "Team", "Owner", merged)


def _control(ident="C1", applies_when=None):
    return ControlDefinition(
        id=ident,
        title=ident,
        criteria_text="criteria",
        frequency="quarterly",
        applies_when=applies_when or {},
        evidence_kind="document",
        required_evidence_types=["report"],
        freshness_days=100,
        severity_weight=1.0,
    )


@pytest.fixture(scope="module")
def corpus():
    return generate_corpus()


# --- the expression language ----------------------------------------------

def test_an_empty_expression_applies_everywhere():
    control = _control(applies_when={})
    for area in PROCESS_AREAS:
        assert evaluate(control, area).applicable


def test_equality_on_a_boolean_attribute():
    control = _control(applies_when={"handles_pii": True})
    assert evaluate(control, _area(handles_pii=True)).applicable
    assert not evaluate(control, _area(handles_pii=False)).applicable


def test_a_list_means_any_one_of_these_values():
    control = _control(applies_when={"criticality": ["high", "critical"]})
    assert evaluate(control, _area(criticality="high")).applicable
    assert evaluate(control, _area(criticality="critical")).applicable
    assert not evaluate(control, _area(criticality="medium")).applicable


def test_multiple_attributes_must_all_hold():
    control = _control(applies_when={"handles_pii": True, "region": "EMEA"})
    assert evaluate(control, _area(handles_pii=True, region="EMEA")).applicable
    assert not evaluate(control, _area(handles_pii=True, region="APAC")).applicable
    assert not evaluate(control, _area(handles_pii=False, region="EMEA")).applicable


def test_a_missing_attribute_does_not_match():
    control = _control(applies_when={"handles_pii": True})
    area = ProcessArea("A9", "A9", "Team", "Owner", {})
    assert not evaluate(control, area).applicable


# --- determinism -----------------------------------------------------------

def test_the_same_inputs_always_give_the_same_answer(corpus):
    first = applicability_matrix(corpus.controls, corpus.areas)
    for _ in range(5):
        assert applicability_matrix(corpus.controls, corpus.areas) == first


def test_input_order_does_not_change_the_result(corpus):
    forward = applicability_matrix(corpus.controls, corpus.areas)
    backward = applicability_matrix(corpus.controls[::-1], corpus.areas[::-1])
    assert forward == backward


def test_control_sets_come_back_sorted(corpus):
    for control_ids in applicability_matrix(corpus.controls, corpus.areas).values():
        assert control_ids == sorted(control_ids)


# --- the 64 pairings pinned by slice 2 -------------------------------------

def test_the_engine_reproduces_every_pairing_the_corpus_assumes(corpus):
    """The real engine must agree with the generator's reference match exactly.

    `synth.generate.applies` is a separate, deliberately trivial implementation.
    Keeping it means this test compares two independent readings of the same
    expressions rather than comparing the engine to itself.
    """
    assert sorted(applicable_pairs(corpus.controls, corpus.areas)) == sorted(
        corpus.applicable_pairs
    )
    assert len(corpus.applicable_pairs) == 64


def test_the_engine_and_the_generator_agree_on_every_combination(corpus):
    """Not just the applicable ones — the negatives have to match too."""
    for control in corpus.controls:
        for area in corpus.areas:
            assert evaluate(control, area).applicable is generator_applies(
                control.applies_when, area.attributes
            ), f"{control.id} x {area.id}"


def test_no_submission_in_the_corpus_sits_outside_the_matrix(corpus):
    pairs = set(applicable_pairs(corpus.controls, corpus.areas))
    for submission in corpus.submissions:
        assert (submission.control_id, submission.process_area_id) in pairs


# --- different areas, different obligations --------------------------------

def test_two_areas_with_different_attributes_get_different_control_sets(corpus):
    matrix = applicability_matrix(corpus.controls, corpus.areas)
    procurement = set(matrix["AREA-PROC"])        # no PII, not customer-facing
    payments = set(matrix["AREA-PAYMENTS"])       # PII, customer-facing, critical

    assert procurement != payments
    assert len(payments) > len(procurement)
    assert "CTRL-ACCESS-REVIEW" in payments and "CTRL-ACCESS-REVIEW" not in procurement
    assert "CTRL-VENDOR-DD" in procurement and "CTRL-VENDOR-DD" in payments


def test_every_area_gets_a_distinct_control_set(corpus):
    matrix = applicability_matrix(corpus.controls, corpus.areas)
    fingerprints = {tuple(v) for v in matrix.values()}
    assert len(fingerprints) == len(matrix)


def test_an_area_matching_no_controls_is_handled_cleanly():
    """Empty is a legitimate answer, not a crash and not an error."""
    controls = [
        _control("C-PII", {"handles_pii": True}),
        _control("C-SUP", {"has_suppliers": True}),
        _control("C-CRIT", {"criticality": ["high", "critical"]}),
    ]
    barren = _area("AREA-EMPTY", handles_pii=False, has_suppliers=False,
                   criticality="low")

    assert applicable_controls(controls, barren) == []
    assert applicability_matrix(controls, [barren]) == {"AREA-EMPTY": []}
    assert applicable_pairs(controls, [barren]) == []


def test_an_area_matching_no_controls_still_gets_an_audit_event(conn):
    from sentinelops.repositories import repositories

    repo = repositories(conn)
    repo["areas"].add(_area("AREA-EMPTY", handles_pii=False, has_suppliers=False,
                            criticality="low"))
    repo["controls"].add(_control("C-PII", {"handles_pii": True}))

    assert run(conn) == {"AREA-EMPTY": []}
    event = repo["audit"].read_for("ProcessArea", "AREA-EMPTY")[0]
    assert event.detail["applicable_count"] == 0
    assert event.detail["evaluated_count"] == 1


# --- explanations ----------------------------------------------------------

def test_an_applicable_decision_explains_itself():
    control = _control(applies_when={"handles_pii": True})
    decision = evaluate(control, _area(handles_pii=True))
    assert "applies because" in decision.explain()
    assert "handles_pii" in decision.explain()


def test_a_rejection_names_only_the_conditions_that_failed():
    control = _control(applies_when={"handles_pii": True, "has_suppliers": True})
    decision = evaluate(control, _area(handles_pii=True, has_suppliers=False))
    explanation = decision.explain()
    assert "does not apply because" in explanation
    assert "has_suppliers" in explanation
    assert "handles_pii" not in explanation


def test_an_unconditional_control_says_so():
    assert evaluate(_control(), _area()).explain() == (
        "applies to every area (no conditions)"
    )


# --- expression validation -------------------------------------------------

def test_every_control_in_the_corpus_has_a_valid_expression(corpus):
    assert validate_expressions(corpus.controls) == []


def test_a_misspelled_attribute_is_caught_rather_than_matching_nothing():
    """The quiet failure this system exists to prevent."""
    typo = _control("C-TYPO", {"handles_pii_data": True})
    problems = validate_expressions([typo])
    assert len(problems) == 1
    assert "C-TYPO" in problems[0] and "handles_pii_data" in problems[0]

    # and it would otherwise have silently applied to nobody
    assert applicable_controls([typo], _area(handles_pii=True)) == []


def test_the_stage_refuses_to_run_on_an_invalid_expression(conn):
    from sentinelops.repositories import repositories

    repo = repositories(conn)
    repo["areas"].add(_area("AREA-X", handles_pii=True))
    repo["controls"].add(_control("C-TYPO", {"handles_pii_data": True}))

    with pytest.raises(ValueError, match="handles_pii_data"):
        run(conn)


def test_known_attributes_match_what_the_areas_actually_carry(corpus):
    for area in corpus.areas:
        assert set(area.attributes) == set(KNOWN_ATTRIBUTES)


# --- zero model calls, permanently -----------------------------------------

@pytest.fixture()
def exploding_llm(monkeypatch):
    """Rig every route to a provider so any model call fails loudly."""

    class Exploding:
        def complete(self, request):
            raise AssertionError("S0 must never call a model")

    def _no(*args, **kwargs):
        raise AssertionError("S0 must never ask for a model client")

    import sentinelops.llm as llm
    import sentinelops.llm.factory as factory
    from sentinelops.llm.providers.fake import FakeModelClient
    from sentinelops.llm.providers.openai import OpenAIClient

    monkeypatch.setattr(factory, "get_client", _no)
    monkeypatch.setattr(llm, "get_client", _no)
    monkeypatch.setattr(FakeModelClient, "complete", Exploding.complete)
    monkeypatch.setattr(OpenAIClient, "complete", Exploding.complete)
    return Exploding()


def test_the_stage_runs_with_every_provider_rigged_to_explode(conn, corpus, exploding_llm):
    seed_database(conn, corpus)
    matrix = run(conn)
    assert len(matrix) == len(corpus.areas)
    assert sum(len(v) for v in matrix.values()) == 64


def test_the_stage_records_no_token_usage(conn, corpus, exploding_llm):
    seed_database(conn, corpus)
    run(conn)
    assert conn.execute("SELECT COUNT(*) c FROM token_usage").fetchone()["c"] == 0


def test_the_pure_functions_touch_no_provider(corpus, exploding_llm):
    assert applicability_matrix(corpus.controls, corpus.areas)
    assert evaluate(corpus.controls[0], corpus.areas[0]) is not None


def _code_only(path: Path) -> str:
    """Source with docstrings and comments removed.

    The prose in these modules talks *about* `llm/` deliberately; only the code
    is under scrutiny.
    """
    source = path.read_text(encoding="utf-8")
    lines = source.splitlines()
    doc_lines: set[int] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef)):
            body = node.body
            if (
                body
                and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)
            ):
                doc_lines.update(range(body[0].lineno, body[0].end_lineno + 1))
    return "\n".join(
        line
        for number, line in enumerate(lines, start=1)
        if number not in doc_lines and not line.strip().startswith("#")
    )


def test_no_stage_module_can_reach_a_model_yet():
    """S3 will import llm/. Until then, no stage may."""
    for path in (SRC / "stages").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            elif isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            for name in names:
                assert "llm" not in name.split("."), f"{path.name} imports {name}"
        assert "llm" not in _code_only(path), f"{path.name} references llm in code"


def test_that_guard_would_actually_fire(tmp_path):
    """Negative control: a planted import must be caught."""
    planted = tmp_path / "sneaky.py"
    planted.write_text(
        '"""A docstring mentioning llm/ is fine."""\nfrom ..llm import get_client\n',
        encoding="utf-8",
    )
    assert "llm" in _code_only(planted)
    assert "llm" not in _code_only(planted).replace("from ..llm import get_client", "")


# --- the audit trail -------------------------------------------------------

def test_each_area_gets_one_audit_event_naming_its_control_set(conn, corpus):
    from sentinelops.repositories import repositories

    seed_database(conn, corpus)
    matrix = run(conn)
    repo = repositories(conn)

    for area in corpus.areas:
        events = [
            e
            for e in repo["audit"].read_for("ProcessArea", area.id)
            if e.action == "applicability_evaluated"
        ]
        assert len(events) == 1
        detail = events[0].detail
        assert detail["applicable_controls"] == matrix[area.id]
        assert detail["applicable_count"] == len(matrix[area.id])
        assert detail["evaluated_count"] == len(corpus.controls)
        assert events[0].owner == area.owner_name
        assert events[0].actor == "system"


# --- the demo rendering ----------------------------------------------------

def test_the_side_by_side_report_renders(corpus, capsys):
    from sentinelops.demo.report import print_applicability_comparison

    areas = {a.id: a for a in corpus.areas}
    print_applicability_comparison(
        corpus.controls, areas["AREA-PROC"], areas["AREA-PAYMENTS"]
    )
    out = capsys.readouterr().out
    assert "S0 APPLICABILITY" in out
    assert "difference: 9 controls" in out
    assert "CTRL-ACCESS-REVIEW" in out
