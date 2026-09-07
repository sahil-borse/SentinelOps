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
from dataclasses import dataclass, field, replace
from datetime import datetime, time, timedelta
from random import Random
from typing import Any

from ..entities import (
    ComplianceException,
    ControlDefinition,
    InboundSubmission,
    AuditableUnit,
)
from .units import AUDITABLE_UNITS, IDENTITIES, IDENTITIES_BY_ID
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
from .programme import (
    AUDIT_CLOSURES, AUDIT_FINDINGS, AUDIT_PROGRAMME, RECURRENCE_GROUPS,
)
from .truth import write_truth_file

DEFAULT_SEED = 20260831
DEFAULT_YEAR = 2026

#: Section 10 asks for eighteen months. The window runs from January 2026 to the
#: end of June 2027, and `SIMULATED_TODAY` sits after it with the grace windows
#: expired, so anything still unmet at "today" is genuinely overdue rather than
#: not-yet-due. Eighteen months is not decoration: recurrence detection is the
#: use that needs the same gap category to reappear in a different unit a long
#: way from the first one, and twelve months does not leave room for that to be
#: distinguishable from coincidence.
DEFAULT_THROUGH = 2027
DEFAULT_LAST_MONTH = 6

#: How the unremarkable majority of submissions are drawn.
#:
#: Section 10 pins the shape: roughly 80-100 findings over eighteen months with
#: 15-18 open at "today". Across ~540 check instances that is a failure rate near
#: one in six, not one in two — and it is the realistic number. A compliance
#: programme where half of everything fails is not a programme in trouble, it is
#: a corpus built to make a detector look good. The old weights predated the
#: volume target and produced 214 findings, all but three of them open, which
#: describes an organisation nobody would recognise.
#:
#: `missing` is deliberately the smallest defect. A missing submission produces
#: a finding that can never be closed by evidence, so every one of them lands in
#: the open count permanently and crowds out the findings that tell a story.
QUALITY_WEIGHTS: dict[str, float] = {
    "compliant": 0.856,
    "near_miss": 0.049,
    "partial": 0.028,
    "non_compliant": 0.024,
    "stale": 0.019,
    "wrong_type": 0.016,
    "missing": 0.008,
}

#: Coordinates pinned by hand so the demo always has the same beats to point at,
#: whatever the seeded draw does elsewhere.
SHOWCASE: dict[tuple[str, str, str], str] = {
    ("CTRL-ACCESS-REVIEW", "AREA-IT", "2026-Q1"): "near_miss",
    ("CTRL-ACCESS-REVIEW", "AREA-HR", "2026-Q2"): "compliant",
    ("CTRL-BACKUP-VERIFY", "AREA-IT", "2026-03"): "near_miss",
    ("CTRL-TRAINING", "AREA-HR", "2026-Q1"): "compliant",
    ("CTRL-CONTROLLED-DOCS", "AREA-ADMIN", "2026-Q2"): "wrong_type",
    ("CTRL-PROCESS-MANUAL", "AREA-PURCHASE", "2026"): "stale",
    ("CTRL-CHANGED-PROCESS", "AREA-FACILITIES", "2026-07"): "missing",
    ("CTRL-INCIDENT-PM", "AREA-IT", "2026-05"): "non_compliant",
    # A document that fails a clause and then tells the assessor to pass it.
    ("CTRL-DATA-RETENTION", "AREA-HR", "2026-Q3"): "adversarial",
    # The second half of the window, so the eighteen months are not a corpus
    # with twelve interesting months and six quiet ones.
    ("CTRL-BACKUP-VERIFY", "AREA-PRJ-ATLAS", "2027-02"): "non_compliant",
    ("CTRL-TRAINING", "AREA-PRJ-CORAL", "2027-Q1"): "near_miss",
    ("CTRL-CHANGED-PROCESS", "AREA-FINANCE", "2027-03"): "missing",
    ("CTRL-RISK-REGISTER", "AREA-PRJ-DELTA", "2027-Q1"): "partial",
    # EXC-004 is granted mid-period against an obligation that is already open
    # and overdue. Pinned rather than drawn, because the waiver has nothing to
    # excuse if the draw happens to file evidence here — and "a waiver arriving
    # after the failure was recorded" is the beat slice 8c exists to show.
    ("CTRL-ACCESS-REVIEW", "AREA-ADMIN", "2026-Q1"): "missing",
}

#: Two recurring gap sets, planted on purpose.
#:
#: Section 10 asks for at least two recurring gap-category sets spanning
#: different units and periods, and section 2 makes recurrence detection an AI
#: use precisely because no human holds the comparison across eighteen months,
#: eleven units and several project teams. A detector needs something real to
#: find, and "real" here means the same *kind* of gap appearing in places that
#: have nothing to do with each other, months apart — not the same control
#: failing twice in the same team, which anyone would notice.
#:
#: Both sets deliberately cross the support-function / project-team line, which
#: is the comparison a functional org chart makes hardest to see.
RECURRENCE_SETS: dict[str, dict] = {
    "REC-ACCESS-LEAVERS": {
        "control_id": "CTRL-ACCESS-REVIEW",
        "quality": "near_miss",
        "coords": [
            ("AREA-IT", "2026-Q1"),
            ("AREA-PRJ-ATLAS", "2026-Q4"),
            ("AREA-PRJ-CORAL", "2027-Q1"),
        ],
        "note": "Accounts left active after the people holding them had gone.",
    },
    "REC-SUPPLIER-FILES": {
        "control_id": "CTRL-VENDOR-DD",
        "quality": "non_compliant",
        "coords": [
            ("AREA-PURCHASE", "2026"),
            ("AREA-FACILITIES", "2027-H1"),
            ("AREA-PRJ-BEACON", "2027-H1"),
        ],
        "note": "Supplier files incomplete at the point the supplier went live.",
    },
}

#: Flattened from RECURRENCE_SETS so the draw can look one coordinate up.
RECURRING: dict[tuple[str, str, str], tuple[str, str]] = {
    (spec["control_id"], unit, period): (set_id, spec["quality"])
    for set_id, spec in RECURRENCE_SETS.items()
    for unit, period in spec["coords"]
}


#: The same document filed against the same control in two different areas.
#: A central team runs the retention sweep once and submits the identical
#: report to both — so the two verdicts must match, and any divergence is a
#: consistency failure rather than a difference in the evidence.
CONSISTENCY_PAIR = {
    "id": "PAIR-RETENTION-Q2",
    "control_id": "CTRL-DATA-RETENTION",
    "period": "2026-Q2",
    "area_ids": ("AREA-IT", "AREA-HR"),
    "quality": "near_miss",
}

#: How many gaps get remediation evidence.
#:
#: Most findings in a real programme do get fixed — that is what the programme is
#: for — and section 10's "15-18 open at today" only works if the rest have
#: closed. This is a share of the remediable failures rather than a fixed count,
#: so it survives a reweighting: the ones left unremediated, plus the missing
#: submissions that can never be remediated, are what remains open on the day.
REMEDIATION_SHARE = 1.0

#: Every Nth remediated failure is fixed badly the first time.
#:
#: Section 10 asks for several findings needing three or more evidence rounds,
#: and section 8 reports the distribution of them. Without this the corpus has
#: only accidental multi-round cases — the ones where the stub happens to
#: misjudge a clean document — which is not the same thing at all: those are
#: measurement noise, and these are the real phenomenon the stakeholder
#: described, where the owner files something, the auditor says what is still
#: missing, and the owner files again.
MULTI_ROUND_EVERY = 7

#: And a few take three. Section 10 asks for "several needing 3+ evidence
#: rounds" — the ones that make the follow-up count worth reporting at all.
THREE_ROUND_EVERY = 13


@dataclass
class Corpus:
    seed: int
    year: int
    areas: list[AuditableUnit]
    controls: list[ControlDefinition]
    exceptions: list[ComplianceException]
    submissions: list[InboundSubmission]
    through: int = DEFAULT_THROUGH
    last_month: int = DEFAULT_LAST_MONTH
    truth_rows: list[dict[str, Any]] = field(default_factory=list)
    applicable_pairs: list[tuple[str, str]] = field(default_factory=list)
    recurrence_groups: list[dict[str, Any]] = field(default_factory=list)
    audits: list[Any] = field(default_factory=list)
    audit_findings: list[Any] = field(default_factory=list)
    audit_closures: list[tuple[str, int, int]] = field(default_factory=list)

    def fingerprint(self) -> str:
        """A hash of everything that must not drift between runs."""
        parts = [f"{s.id}|{s.content_hash}|{s.submitted_at.isoformat()}"
                 for s in self.submissions]
        parts += [repr(sorted(r.items())) for r in self.truth_rows]
        return hashlib.sha256("\n".join(parts).encode()).hexdigest()


def _owner_name(unit) -> str:
    owner = IDENTITIES_BY_ID.get(unit.owner_identity)
    return owner.name if owner else unit.owner_identity


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
        "auditable_unit_id": None,
        "period": None,
        "defect_kind": None,
        "expected_verdict": None,
        "failing_clause_index": None,
        "failing_clause_text": None,
        "is_remediation": False,
        "remediates_submission_id": None,
        "consistency_pair_id": None,
        "recurrence_set_id": None,
        "note": "",
    }
    row.update(kwargs)
    return row


def _window(spec, corpus) -> list:
    """Every period this control covers, across the whole eighteen months."""
    return periods_for(
        spec.frequency, corpus.year, corpus.through, last_month=corpus.last_month
    )


def generate_corpus(
    seed: int = DEFAULT_SEED,
    year: int = DEFAULT_YEAR,
    through: int = DEFAULT_THROUGH,
    last_month: int = DEFAULT_LAST_MONTH,
) -> Corpus:
    rng = Random(seed)
    areas_by_id = {a.id: a for a in AUDITABLE_UNITS}

    corpus = Corpus(
        seed=seed,
        year=year,
        through=through,
        last_month=last_month,
        areas=list(AUDITABLE_UNITS),
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
        for area in sorted(AUDITABLE_UNITS, key=lambda a: a.id):
            if not applies(spec.applies_when, area.attributes):
                continue
            corpus.applicable_pairs.append((spec.id, area.id))

            for period in _window(spec, corpus):
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
                            auditable_unit_id=area.id,
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
                recurring = RECURRING.get(coords)
                quality = (
                    CONSISTENCY_PAIR["quality"] if is_pair
                    else recurring[1] if recurring
                    else SHOWCASE.get(coords) or _weighted_quality(spec, rng)
                )

                if quality == "missing":
                    corpus.truth_rows.append(
                        _truth_row(
                            control_id=spec.id,
                            auditable_unit_id=area.id,
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
                submission = InboundSubmission(
                    id=f"SUB-{sequence:04d}",
                    control_id=spec.id,
                    auditable_unit_id=area.id,
                    period=period.label,
                    kind=evidence.kind,
                    doc_type=evidence.doc_type,
                    content=evidence.content,
                    content_hash=hashlib.sha256(evidence.content.encode()).hexdigest(),
                    submitted_at=datetime.combine(filed, time(9, 30)),
                    author=_owner_name(area),
                    is_remediation=False,
                )
                corpus.submissions.append(submission)
                corpus.truth_rows.append(
                    _truth_row(
                        submission_id=submission.id,
                        control_id=spec.id,
                        auditable_unit_id=area.id,
                        period=period.label,
                        defect_kind=quality,
                        expected_verdict=evidence.expected_verdict,
                        failing_clause_index=evidence.failing_clause_index,
                        failing_clause_text=evidence.failing_clause_text,
                        consistency_pair_id=CONSISTENCY_PAIR["id"] if is_pair else None,
                        recurrence_set_id=recurring[0] if recurring else None,
                        note=(
                            f"Filed {filed.isoformat()}, due "
                            f"{due_date(period, spec.grace_days).isoformat()}."
                        ),
                    )
                )

    _add_remediations(corpus, rng)
    _add_programme(corpus)
    return corpus


def _add_programme(corpus: Corpus) -> None:
    """The audit track. Findings here are raised by a person, not a pipeline.

    They are held as plain tuples rather than `Finding` objects because the
    seeding path drives them through `stages.audits`, which is what writes the
    audit trail. A generator that inserted findings straight into the table
    would produce a corpus whose findings have no history — and the trail is the
    product here, not a by-product.
    """
    from ..entities import ScheduledAudit

    for ident, kind, planned, conducted, auditor, scope, title in AUDIT_PROGRAMME:
        corpus.audits.append(ScheduledAudit(
            id=ident, kind=kind, scope=list(scope), auditor_identity=auditor,
            planned_date=planned, conducted_date=conducted, title=title,
            status="completed" if conducted else "planned",
        ))
    corpus.audit_findings = list(AUDIT_FINDINGS)
    corpus.audit_closures = list(AUDIT_CLOSURES)
    corpus.recurrence_groups = _recurrence_truth(corpus)


def _recurrence_truth(corpus: Corpus) -> list[dict[str, Any]]:
    """Resolve the intended recurrence groups to the finding ids they become.

    `programme.RECURRENCE_GROUPS` names its members by (audit, index) so that it
    survives a renumbering. The truth file needs the ids, because that is what a
    detector's output is expressed in — so the resolution happens once, here,
    using exactly the id scheme `stages.audits.raise_finding` will use.

    If that scheme ever changes, this goes wrong loudly: the ids in the truth
    file stop matching any finding, and the recurrence score drops to zero
    rather than quietly measuring nothing.
    """
    per_audit: dict[str, int] = {}
    ids: dict[tuple[str, int], str] = {}
    for audit_id, *_ in corpus.audit_findings:
        index = per_audit.get(audit_id, 0)
        per_audit[audit_id] = index + 1
        ids[(audit_id, index)] = (
            f"FND-{audit_id.removeprefix('AUD-')}-{index + 1:02d}"
        )

    groups = []
    for set_id, spec in RECURRENCE_GROUPS.items():
        members = [ids[key] for key in spec["members"] if key in ids]
        units = []
        for audit_id, index in spec["members"]:
            matches = [f for f in corpus.audit_findings if f[0] == audit_id]
            if index < len(matches):
                units.append(matches[index][1])
        groups.append({
            "id": set_id,
            "gap": spec["gap"],
            "finding_ids": members,
            "auditable_unit_ids": units,
            "spans_units": len(set(units)) > 1,
            "note": spec["note"],
        })
    return groups


def _add_remediations(corpus: Corpus, rng: Random) -> None:
    """Follow-up evidence that fixes an earlier gap, so the loop can close.

    Submitted against the same control, area and period as the failure it
    answers — remediation resolves the check that failed, it does not open a
    new one.
    """
    specs_by_id = {s.id: s for s in CONTROL_SPECS}
    areas_by_id = {a.id: a for a in AUDITABLE_UNITS}
    by_id = {s.id: s for s in corpus.submissions}

    remediable = [
        row
        for row in corpus.truth_rows
        if row["expected_verdict"] in ("gap", "partial", "insufficient_evidence")
        and row["defect_kind"] in (
            "near_miss", "non_compliant", "partial", "stale", "wrong_type"
        )
        and row["submission_id"] is not None
    ]
    candidates = remediable[:round(len(remediable) * REMEDIATION_SHARE)]

    sequence = len(corpus.submissions)
    for index, row in enumerate(candidates):
        original = by_id[row["submission_id"]]
        spec = specs_by_id[original.control_id]
        area = areas_by_id[original.auditable_unit_id]
        period = next(
            p for p in _window(spec, corpus) if p.label == original.period
        )
        # Some fixes do not fix it the first time. The owner files again, and
        # the finding stays open in between — which is section 4's loop with
        # something actually going round it.
        if index % THREE_ROUND_EVERY == 0:
            attempts = ["near_miss", "near_miss", "compliant"]
        elif index % MULTI_ROUND_EVERY == 0:
            attempts = ["near_miss", "compliant"]
        else:
            attempts = ["compliant"]
        # Dated from the original submission, not from the period, so a late
        # filing still gets a remediation that lands after it.
        filed = original.submitted_at.date() + timedelta(days=rng.randrange(14, 40))

        for attempt, quality in enumerate(attempts, start=1):
            evidence = render(spec, area, period, quality, rng)
            sequence += 1
            if attempt > 1:
                filed = filed + timedelta(days=rng.randrange(10, 30))
            if filed > SIMULATED_TODAY:
                # The next attempt would land after "today", so it has not
                # happened yet. The finding stays open with the rounds it has —
                # which is the truthful state for a failure late in the window,
                # and better than back-dating a fix into a future the corpus
                # cannot see.
                break
            submission = InboundSubmission(
                id=f"SUB-{sequence:04d}",
                control_id=spec.id,
                auditable_unit_id=area.id,
                period=period.label,
                kind=evidence.kind,
                doc_type=evidence.doc_type,
                content=evidence.content,
                content_hash=hashlib.sha256(evidence.content.encode()).hexdigest(),
                submitted_at=datetime.combine(filed, time(16, 0)),
                author=_owner_name(area),
                is_remediation=True,
            )
            corpus.submissions.append(submission)
            corpus.truth_rows.append(
                _truth_row(
                    submission_id=submission.id,
                    control_id=spec.id,
                    auditable_unit_id=area.id,
                    period=period.label,
                    defect_kind="remediation",
                    expected_verdict=evidence.expected_verdict,
                    failing_clause_index=evidence.failing_clause_index,
                    failing_clause_text=evidence.failing_clause_text,
                    is_remediation=True,
                    remediates_submission_id=original.id,
                    note=(
                        f"Remediation attempt {attempt} of {len(attempts)} for "
                        f"{original.id}, filed {filed.isoformat()}."
                    ),
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
            if suppresses(exception, exception.control_id, exception.auditable_unit_id,
                          period.end)
        ]
        if spec
        else []
    )
    return {
        "id": exception.id,
        "control_id": exception.control_id,
        "auditable_unit_id": exception.auditable_unit_id,
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
        # What the corpus intends to be the same gap, so recurrence detection
        # can be scored rather than eyeballed. Two sets from the audit track,
        # named by finding id, plus the activity-track sets named by coordinate.
        "recurrence_groups": corpus.recurrence_groups,
        "recurrence_coordinate_sets": [
            {
                "id": set_id,
                "control_id": spec["control_id"],
                "coords": [
                    {"auditable_unit_id": unit, "period": period}
                    for unit, period in spec["coords"]
                ],
                "note": spec["note"],
            }
            for set_id, spec in RECURRENCE_SETS.items()
        ],
        "exceptions": [_exception_truth(e, corpus) for e in corpus.exceptions],
        "fingerprint": corpus.fingerprint(),
        "rows": corpus.truth_rows,
    }


def write_truth(corpus: Corpus):
    return write_truth_file(truth_payload(corpus), corpus.year)


def seed_database(conn, corpus: Corpus) -> None:
    """Load the corpus into SQLite.

    Units, identities, controls, exceptions and inbound submissions are written
    directly — they are the register, and it exists before anything happens to
    it. CheckInstances, Evidence, Assessments and activity-track Findings are
    produced by the pipeline, never by the generator.

    The audit programme is the exception that proves the rule: its audits are
    written directly, but its *findings* are driven through `stages.audits` so
    that each one is raised by an identity, at a date, with an audit-trail entry
    behind it. Inserting them into the table would give the corpus findings with
    no history, and the history is the product.
    """
    from datetime import date as _date

    from ..repositories import repositories, simulated_clock

    repo = repositories(conn)
    # The register exists from the first day of the year under audit.
    with simulated_clock(datetime.combine(_date(corpus.year, 1, 1), time(0, 0))):
        _seed(repo, corpus)
    _seed_programme(conn, repo, corpus)


def _seed_programme(conn, repo, corpus: Corpus) -> None:
    """Conduct each audit, raise its findings, and close the ones that closed."""
    from ..stages import audits as audit_stage
    from ..stages import followup

    for audit in corpus.audits:
        # Stored as planned; `conduct` is what completes it and writes the event.
        stored = replace(audit, status="planned", conducted_date=None)
        repo["audits"].add(stored)

    raised: dict[str, list] = {}
    for audit in corpus.audits:
        if audit.conducted_date is None:
            continue
        audit_stage.conduct(
            conn, audit.id, by=audit.auditor_identity, as_of=audit.conducted_date
        )
        for audit_id, unit_id, severity, description, plan in corpus.audit_findings:
            if audit_id != audit.id:
                continue
            finding = audit_stage.raise_finding(
                conn, audit.id, unit_id=unit_id, description=description,
                severity=severity, by=audit.auditor_identity,
                agreed_action_plan=plan, as_of=audit.conducted_date,
            )
            raised.setdefault(audit.id, []).append(finding)
        # Deliberately *not* generating the reports here. Report drafting is the
        # one part of the audit track that costs tokens, and seeding a database
        # is something the tests do hundreds of times — an eight-call bill every
        # time a fixture runs would be indefensible, and it would make "S0 never
        # calls a model" untestable because S0's own tests seed a corpus. The
        # report is generated when somebody asks for it, which is also when a
        # real auditor would ask.

    by_audit = {a.id: a for a in corpus.audits}
    for audit_id, index, days in corpus.audit_closures:
        findings = raised.get(audit_id, [])
        if index >= len(findings):
            continue
        finding = findings[index]
        audit = by_audit[audit_id]
        # Closed by the auditor who did *not* raise it, so the corpus exercises
        # the section 7 separation rather than merely satisfying it by accident.
        closer = next(
            i.id for i in [
                *(x for x in _AUDITORS() if x.id != audit.auditor_identity),
                *(x for x in _AUDITORS()),
            ]
        )
        closed_on = audit.conducted_date + timedelta(days=days)
        followup.close_finding(
            conn, finding.id, by=closer,
            remarks=(
                "Evidence reviewed and accepted; the agreed action plan was "
                "completed and verified."
            ),
            as_of=closed_on,
        )


def _AUDITORS():
    from .units import AUDITORS

    return AUDITORS


def _seed(repo, corpus: Corpus) -> None:
    # Identities first: a unit points at its owner, and the audit trail
    # attributes everything to somebody, so the roster has to exist before
    # anything can reference it.
    for identity in IDENTITIES:
        repo["identities"].add(identity)
    for area in corpus.areas:
        repo["units"].add(area)
    for control in corpus.controls:
        repo["controls"].add(control)
    for exception in corpus.exceptions:
        repo["exceptions"].add(exception)
        # Granting a waiver is a decision somebody made and has to answer for.
        # Recorded here so the audit pack can show the register without reading
        # the exceptions table.
        repo["audit"].append(
            actor="user",
            owner=exception.approved_by,
            action="exception_registered",
            entity_type="ComplianceException",
            entity_id=exception.id,
            detail={
                "control_id": exception.control_id,
                "auditable_unit_id": exception.auditable_unit_id,
                "rationale": exception.rationale,
                "approved_by": exception.approved_by,
                "granted_at": exception.granted_at.isoformat(),
                "expires_at": exception.expires_at.isoformat(),
                "status_at_registration": exception.status,
            },
        )
    for submission in corpus.submissions:
        repo["inbound"].add(submission)
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
            "audits": len(corpus.audits),
            "audit_findings": len(corpus.audit_findings),
            "fingerprint": corpus.fingerprint()[:16],
        },
    )
