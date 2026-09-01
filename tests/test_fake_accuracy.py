"""How good the stub actually is, measured rather than assumed.

`FakeModelClient` is not a model. It is a deterministic heuristic that reads
numbered clauses and looks for negation. It exists so the suite runs without a
key and so consistency can be tested against a fixed reference — not so that its
verdicts can be quoted.

This file measures its agreement with the ground truth and pins the number. If
anyone is tempted to present a precision figure produced by the fake, the
docstring here is the answer: run it against the real provider, because the
stub's error profile is known and lopsided.
"""

from datetime import date

import pytest

from sentinelops.repositories import repositories
from sentinelops.stages.assess import run as assess
from sentinelops.stages.prescreen import run as prescreen
from sentinelops.stages.trigger import run_cycle
from sentinelops.synth import generate_corpus, seed_database

END_OF_STORY = date(2027, 3, 31)

EXPECTED = {
    "compliant": "compliant",
    "near_miss": "gap",
    "partial": "partial",
    "non_compliant": "gap",
    "adversarial": "gap",
}


@pytest.fixture(scope="module")
def corpus():
    return generate_corpus()


@pytest.fixture()
def outcomes(conn, corpus):
    """Every S3 verdict paired with the defect the generator injected."""
    seed_database(conn, corpus)
    for month in range(1, 13):
        run_cycle(conn, date(2026, month, 28))
    run_cycle(conn, END_OF_STORY)
    screen = prescreen(conn, END_OF_STORY)
    assess(conn, screen.to_assess, END_OF_STORY)

    truth = {}
    for row in corpus.truth_rows:
        if not row["submission_id"] or row["is_remediation"]:
            continue  # the remediation shares coordinates with what it answers
        key = (
            f"CHK-{row['control_id'].removeprefix('CTRL-')}-"
            f"{row['process_area_id'].removeprefix('AREA-')}-{row['period']}"
        )
        truth[key] = row

    paired = []
    for finding in repositories(conn)["findings"].list():
        if finding.decided_by != "s3_model":
            continue
        row = truth.get(finding.check_instance_id)
        if row and row["defect_kind"] in EXPECTED:
            paired.append((row["defect_kind"], finding.verdict))
    return paired


def _agreement(paired):
    correct = sum(1 for kind, verdict in paired if verdict == EXPECTED[kind])
    return correct / len(paired)


def test_the_stub_is_measured_not_assumed(outcomes):
    assert len(outcomes) > 190
    assert _agreement(outcomes) > 0.85


def test_the_stub_never_misses_a_near_miss(outcomes):
    """The case the whole precision story rests on."""
    near = [(k, v) for k, v in outcomes if k == "near_miss"]
    assert near
    assert all(verdict == "gap" for _, verdict in near)


def test_the_stub_never_calls_a_broken_document_compliant(outcomes):
    """False negatives are the expensive error: a missed gap ships."""
    for kind, verdict in outcomes:
        if kind in ("near_miss", "non_compliant", "adversarial"):
            assert verdict != "compliant", f"{kind} passed as compliant"


def test_the_stub_never_calls_a_clean_document_a_gap(outcomes):
    clean = [(k, v) for k, v in outcomes if k == "compliant"]
    assert clean
    assert all(verdict == "compliant" for _, verdict in clean)


def test_the_known_weakness_is_partial_documents(outcomes):
    """Hedged prose is where the heuristic loses, and only there.

    A document that says work is "queued for a later pass" is doing something a
    keyword rule reads badly. Recorded here so the limitation is documented
    rather than discovered.
    """
    wrong = [(k, v) for k, v in outcomes if v != EXPECTED[k]]
    assert wrong, "if this passes cleanly the heuristic changed; re-measure"
    assert {kind for kind, _ in wrong} == {"partial"}
