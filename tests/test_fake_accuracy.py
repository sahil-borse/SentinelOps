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
            f"{row['auditable_unit_id'].removeprefix('AREA-')}-{row['period']}"
        )
        truth[key] = row

    paired = []
    for finding in repositories(conn)["assessments"].list():
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


def test_the_stub_almost_never_misses_a_near_miss(outcomes):
    """The case the whole precision story rests on — and where it now loses one.

    Measured, not assumed: one near-miss in eighteen slips past, and it is worth
    naming why. The document says "{j} of {k} accounts from ended engagements
    were disabled inside the window". That is a genuine shortfall, and a reader
    sees it instantly — but seeing it requires comparing two numbers, and the
    stub is a keyword heuristic looking for a negation. There is no negation to
    find, so it passes.

    The corpus is not wrong here and neither is the rendering: this is exactly
    the kind of judgement a language model is for, and the stub standing in for
    one cannot do it. Asserting zero misses would mean either weakening the
    corpus until the heuristic could cope, or claiming an accuracy the stub does
    not have. Both would make the number in `results.md` a lie.
    """
    near = [(k, v) for k, v in outcomes if k == "near_miss"]
    assert near
    missed = [v for _, v in near if v != "gap"]
    assert len(missed) <= 1, (
        f"{len(missed)} near-misses slipped past; the stub has got worse, "
        f"or the corpus now hides its failures in prose"
    )


def test_the_stubs_false_negative_rate_is_measured(outcomes):
    """False negatives are the expensive error: a missed gap ships.

    One in the whole corpus, and it is the numeric-shortfall case above. Pinned
    as a ceiling rather than asserted as zero, so a change that lets more
    through fails rather than quietly shipping.
    """
    broken = [
        (k, v) for k, v in outcomes
        if k in ("near_miss", "non_compliant", "adversarial")
    ]
    assert broken
    passed = [(k, v) for k, v in broken if v == "compliant"]
    assert len(passed) <= 1, f"{len(passed)} broken documents passed as compliant"
    assert len(passed) / len(broken) < 0.05


def test_the_adversarial_document_is_never_passed(outcomes):
    """Whatever else slips, the injected one must not.

    A near-miss the heuristic cannot read is a limitation. A document that tells
    the assessor to pass it and is then passed is a different thing entirely.
    """
    injected = [(k, v) for k, v in outcomes if k == "adversarial"]
    assert injected
    assert all(verdict != "compliant" for _, verdict in injected)


def test_the_stub_never_calls_a_clean_document_a_gap(outcomes):
    clean = [(k, v) for k, v in outcomes if k == "compliant"]
    assert clean
    assert all(verdict == "compliant" for _, verdict in clean)


def test_the_known_weaknesses_are_hedged_prose_and_numeric_shortfalls(outcomes):
    """Where the heuristic loses, and only there.

    Two kinds of document defeat a keyword rule. One says work is "queued for a
    later pass" — hedged prose, and the bulk of the errors. The other states a
    shortfall as arithmetic, "3 of 5 were disabled", with no word anywhere in it
    that reads as failure.

    Recorded here so the limitation is documented rather than discovered, and
    kept as an exact set: if a *third* kind starts failing, this test says so
    instead of the agreement figure drifting quietly downwards.
    """
    wrong = [(k, v) for k, v in outcomes if v != EXPECTED[k]]
    assert wrong, "if this passes cleanly the heuristic changed; re-measure"
    assert {kind for kind, _ in wrong} <= {"partial", "near_miss"}
    assert "partial" in {kind for kind, _ in wrong}
    # and the bulk of it is still the prose case
    by_kind = [k for k, _ in wrong]
    assert by_kind.count("partial") > by_kind.count("near_miss")
