"""The seven metrics of section 6, each computed from what the run left behind.

Nothing here re-derives a verdict or re-runs a stage. Every figure is read out
of the database the pipeline wrote, or out of the truth file, and the two are
joined on the instance key. If a number cannot be computed from the record, it
is not reported.

**Nothing is dropped because it did not match.** Until slice 15z every scorer
here joined on whatever the *run* produced and skipped what it could not place:
a verdict for an instance the truth file did not describe was ignored, a truth
obligation the run never scheduled was invisible, and `missed_checks` accepted
the truth rows and never read them. That is how a scheduler that stopped at
2026 reported a 0.0% missed-check rate over 446 instances while 104 obligations
due in 2027 had never been raised. It is the same defect class as the stale
truth file: a plausible number computed over a quietly smaller set.

So each scorer now does one of two things with every row. It refuses — raises
`UnscorableRows` — when it meets something it cannot place. Or it counts the
row under a named exclusion that the report prints. There is no third option.
"""

from __future__ import annotations

import json
import statistics
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from sentinelops.periods import due_date, period_from_label
from sentinelops.repositories import repositories

TRUTH_DIR = Path(__file__).resolve().parents[1] / "data" / "truth"

#: A verdict counts as "this failed" for gap detection.
POSITIVE = ("gap",)


class UnscorableRows(ValueError):
    """A scorer met rows it could not place. Raised, never skipped."""


class UnscheduledObligations(RuntimeError):
    """The run left obligations that were due unscheduled; the harness will not score it.

    Not a missed check in the product's sense. The automated path claims a
    check cannot fail to be raised, because scheduling is deterministic; if one
    was not raised, what is broken is the scheduler, and scoring the run would
    report a property of the bug as a property of the system.
    """


def load_ground_truth(year: int) -> dict[str, Any]:
    """The only read of the truth file in the entire project.

    `year` is the corpus's first year, which names the file. No default: the
    default used to be 2026, one of the years this slice removed.
    """
    return json.loads((TRUTH_DIR / f"truth_{year}.json").read_text(encoding="utf-8"))


def instance_key(control_id: str, auditable_unit_id: str, period: str) -> str:
    """The pipeline's own instance id scheme, so run and truth join row for row."""
    return (
        f"CHK-{control_id.removeprefix('CTRL-')}-"
        f"{auditable_unit_id.removeprefix('AREA-')}-{period}"
    )


def truth_by_instance(truth: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Truth rows keyed by instance. Two exclusions, both named, and no collisions.

    Remediation rows are excluded because a fix is judged through the finding it
    answers, not as an obligation of its own. Exception-suppressed rows are
    excluded because an excused period never raises a check. Anything else that
    would land on an existing key is refused: a second row for one obligation
    would silently replace the first.
    """
    rows: dict[str, dict[str, Any]] = {}
    for row in truth["rows"]:
        if row["is_remediation"] or row["defect_kind"] == "exception_suppressed":
            continue
        key = instance_key(row["control_id"], row["auditable_unit_id"], row["period"])
        if key in rows:
            raise UnscorableRows(
                f"two truth rows describe {key}; scoring would keep one and "
                f"silently discard the other"
            )
        rows[key] = row
    return rows


def obligations_by_vantage(
    conn, truth_rows: dict[str, dict[str, Any]], as_of: date,
) -> dict[str, set[str]]:
    """Every truth obligation, placed relative to the vantage point.

      due       its due date is before the vantage point; the run must have
                scheduled and examined it
      not_due   its period has opened and it falls due on or after the vantage
                point
      not_open  its period starts after the vantage point

    **On its due date a check is not yet missed.** S1 marks an instance overdue
    only when `as_of > due_date`, and this uses the same boundary. The first
    version counted a check due *on* the vantage point as due, and reported one
    missed check — an unfiled obligation falling due that very day, which S1
    would pick up as overdue on the next.

    Grace days come from the controls in the run's own database. A truth row for
    a control the run does not have is refused rather than guessed at.
    """
    grace = {c.id: c.grace_days for c in repositories(conn)["controls"].list()}
    placed: dict[str, set[str]] = {"due": set(), "not_due": set(), "not_open": set()}
    unknown = sorted({row["control_id"] for row in truth_rows.values()} - set(grace))
    if unknown:
        raise UnscorableRows(
            f"the truth file describes controls this run does not have: {unknown}"
        )
    for key, row in truth_rows.items():
        period = period_from_label(row["period"])
        if period.start > as_of:
            placed["not_open"].add(key)
        elif due_date(period, grace[row["control_id"]]) >= as_of:
            placed["not_due"].add(key)
        else:
            placed["due"].add(key)
    return placed


@dataclass
class Confusion:
    true_positive: int = 0
    false_positive: int = 0
    true_negative: int = 0
    false_negative: int = 0
    #: Truth obligations this path gave no verdict for. Reported, not hidden: a
    #: path that judges less is not thereby more accurate.
    unjudged: int = 0

    @property
    def total(self) -> int:
        return (
            self.true_positive + self.false_positive
            + self.true_negative + self.false_negative
        )

    @property
    def precision(self) -> float:
        called = self.true_positive + self.false_positive
        return self.true_positive / called if called else 0.0

    @property
    def recall(self) -> float:
        actual = self.true_positive + self.false_negative
        return self.true_positive / actual if actual else 0.0

    @property
    def false_positive_rate(self) -> float:
        clean = self.false_positive + self.true_negative
        return self.false_positive / clean if clean else 0.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if (p + r) else 0.0


def score_gap_detection(
    verdicts: dict[str, str], truth_rows: dict[str, dict[str, Any]]
) -> Confusion:
    """Did we call the failing documents failing, and leave the good ones alone?

    Positive class is `gap`. Every verdict is scored against its truth row, and
    a verdict for an instance the truth file does not describe is **refused**:
    it used to be skipped, which is how a join that had drifted would have gone
    on producing a number. Truth rows with no verdict are counted as `unjudged`
    and printed — whether they *should* have had one is the missed-check metric's
    question, which now answers it from the truth file too.
    """
    unknown = sorted(key for key in verdicts if key not in truth_rows)
    if unknown:
        raise UnscorableRows(
            f"{len(unknown)} verdict(s) for instances the truth file does not "
            f"describe, e.g. {unknown[:5]}"
        )
    confusion = Confusion()
    for key, verdict in verdicts.items():
        row = truth_rows[key]
        if row["expected_verdict"] is None:
            raise UnscorableRows(
                f"{key}: the truth row has no expected verdict, so the verdict "
                f"{verdict!r} cannot be marked right or wrong"
            )
        predicted = verdict in POSITIVE
        actual = row["expected_verdict"] in POSITIVE
        if predicted and actual:
            confusion.true_positive += 1
        elif predicted and not actual:
            confusion.false_positive += 1
        elif not predicted and actual:
            confusion.false_negative += 1
        else:
            confusion.true_negative += 1
    confusion.unjudged = len(set(truth_rows) - set(verdicts))
    return confusion


def missed_checks(
    conn, truth_rows: dict[str, dict[str, Any]], *, as_of: date,
) -> dict[str, Any]:
    """A check is missed when it was due and nothing ever looked at it.

    **The denominator comes from the truth file, not from the scheduler.** It
    used to be the instances S1 had created, so an obligation S1 never raised
    was not missed — it was not counted at all. Now every truth obligation due
    by the vantage point is either examined, waived, scheduled-but-unexamined,
    or unscheduled, and the last two are both missed.

    Note that "no evidence was filed" is still *not* a missed check: the system
    raised it, chased it and recorded the absence, which is the opposite of
    missing it. And an instance the truth file does not describe is refused.
    """
    repo = repositories(conn)
    instances = {i.id: i for i in repo["instances"].list()}
    strangers = sorted(set(instances) - set(truth_rows))
    if strangers:
        raise UnscorableRows(
            f"{len(strangers)} scheduled instance(s) the truth file does not "
            f"describe, e.g. {strangers[:5]}"
        )

    placed = obligations_by_vantage(conn, truth_rows, as_of)
    examined_ids = {
        a.check_instance_id for a in repo["assessments"].list() if a.check_instance_id
    }
    waived = {key for key in placed["due"] if key in instances
              and instances[key].status == "waived"}
    unscheduled = sorted(placed["due"] - set(instances))
    unexamined = sorted(
        key for key in placed["due"]
        if key in instances and key not in waived and key not in examined_ids
    )
    due = len(placed["due"]) - len(waived)
    missed = len(unscheduled) + len(unexamined)
    return {
        "due": due,
        "examined": due - missed,
        "missed": missed,
        "rate": missed / due if due else 0.0,
        "waived": len(waived),
        "unscheduled": len(unscheduled),
        "unscheduled_examples": unscheduled[:10],
        "scheduled_unexamined": len(unexamined),
        "not_yet_due": len(placed["not_due"]),
        "not_yet_open": len(placed["not_open"]),
        "truth_obligations": len(truth_rows),
    }


def require_scheduled(missed: dict[str, Any]) -> None:
    """Refuse to score a run that left due obligations unscheduled."""
    if missed["unscheduled"]:
        raise UnscheduledObligations(
            f"{missed['unscheduled']} obligation(s) due by the vantage point were "
            f"never scheduled, e.g. {missed['unscheduled_examples']}. Scoring this "
            f"run would report the scheduler's gap as a property of the system"
        )


def time_to_detection(conn) -> dict[str, Any]:
    """Days from a check falling due to its non-compliance being written down."""
    repo = repositories(conn)
    instances = {i.id: i for i in repo["instances"].list()}
    superseded = {
        f.supersedes_assessment_id
        for f in repo["assessments"].list()
        if f.supersedes_assessment_id
    }
    gaps = []
    for finding in repo["assessments"].list():
        if not finding.check_instance_id:
            # A round assessment judges a finding's evidence and has no due date
            # to measure from. Excluded by kind, not by failing to match.
            continue
        if finding.verdict == "compliant" or finding.id in superseded:
            continue
        instance = instances.get(finding.check_instance_id)
        if instance is None:
            raise UnscorableRows(
                f"{finding.id} judges {finding.check_instance_id}, which does not exist"
            )
        if finding.assessed_at is None:
            raise UnscorableRows(
                f"{finding.id} has no assessment date, so its detection time is unknown"
            )
        gaps.append((finding.assessed_at.date() - instance.due_date).days)
    spread = _spread(gaps)
    # Negative is not an error. With "today" inside the window and cycles run
    # monthly, evidence filed ahead of the deadline is judged on the next cycle
    # — so the gap is written down *before* the check was due. That is the
    # system working, and it is worth reporting rather than clamping away.
    spread["detected_before_due"] = len([g for g in gaps if g < 0])
    spread["detected_after_due"] = len([g for g in gaps if g >= 0])
    return spread


def _spread(values: list[int]) -> dict[str, Any]:
    if not values:
        return {"n": 0, "mean": 0.0, "median": 0.0, "p90": 0, "max": 0}
    ordered = sorted(values)
    return {
        "n": len(ordered),
        "mean": round(statistics.mean(ordered), 1),
        "median": round(statistics.median(ordered), 1),
        "p90": ordered[min(int(len(ordered) * 0.9), len(ordered) - 1)],
        "max": ordered[-1],
    }


def verdict_consistency(conn) -> dict[str, Any]:
    """Where identical evidence was judged twice, did it get the same answer?"""
    repo = repositories(conn)
    findings = {}
    superseded = {
        f.supersedes_assessment_id
        for f in repo["assessments"].list()
        if f.supersedes_assessment_id
    }
    for finding in repo["assessments"].list():
        if not finding.check_instance_id:
            continue  # round assessments: not periodic evidence, not comparable here
        if finding.id not in superseded:
            findings[finding.check_instance_id] = finding

    instances = {i.id: i for i in repo["instances"].list()}
    groups: dict[tuple[str, str], list[str]] = {}
    for evidence in repo["evidence"].list():
        if evidence.is_remediation:
            continue
        instance = instances.get(evidence.check_instance_id)
        if instance is None:
            raise UnscorableRows(
                f"evidence {evidence.id} is bound to {evidence.check_instance_id}, "
                f"which does not exist"
            )
        groups.setdefault(
            (instance.control_id, evidence.content_hash), []
        ).append(instance.id)

    pairs = {k: v for k, v in groups.items() if len(v) > 1}
    disagreements = []
    for key, instance_ids in pairs.items():
        verdicts = {
            findings[i].verdict for i in instance_ids if i in findings
        }
        if len(verdicts) > 1:
            disagreements.append((key, verdicts))
    return {
        "identical_evidence_groups": len(pairs),
        "groups_with_disagreement": len(disagreements),
        "disagreement_rate": len(disagreements) / len(pairs) if pairs else 0.0,
        "examples": [str(d) for d in disagreements[:3]],
    }


def zero_model_share(conn) -> dict[str, Any]:
    """How much of the cycle reached a verdict without a model being asked."""
    repo = repositories(conn)
    superseded = {
        f.supersedes_assessment_id
        for f in repo["assessments"].list()
        if f.supersedes_assessment_id
    }
    current = [f for f in repo["assessments"].list() if f.id not in superseded]
    by_tier: dict[str, int] = {}
    for finding in current:
        by_tier[finding.decided_by] = by_tier.get(finding.decided_by, 0) + 1
    rules = sum(v for k, v in by_tier.items() if not k.startswith("s3_"))
    return {
        "assessments": len(current),
        "decided_by_rules": rules,
        "decided_by_model": len(current) - rules,
        "share": rules / len(current) if current else 0.0,
        "by_tier": dict(sorted(by_tier.items())),
    }


def recover_run_stats(conn) -> dict[str, Any]:
    """The pipeline's own counters, read back off the trail rather than trusted.

    `run_pipeline` accumulates these while it runs, which is fine for a run
    scored in the same process. A saved run scored later recovered them from
    the spend ledger instead, and when that ledger held no completed-replay
    entry — which is every run that was resumed rather than finishing in one
    process — they fell back to zeros and were printed as measurements: "0
    reminders and 0 escalations" over a run that sent 570 and raised 226. A
    plausible wrong number is worse than an obviously broken one; this is the
    stale-truth-file failure wearing different clothes.

    Everything the report quotes is on the audit log, and the two figures it
    quotes most are there twice over: once per cycle in `followup_completed`,
    and once per act as `finding_reminder_sent` and `finding_escalated`. Both
    are read, and a disagreement raises rather than quietly preferring one.

    `remediated` counts instances *re-assessed* after remediation evidence
    arrived — one `assessment_superseded` each. It is not the number of
    remediations the corpus contains, which is a property of the corpus and is
    counted there.
    """
    repo = repositories(conn)
    events = repo["audit"].read_all()

    def total(action: str, key: str) -> int:
        return sum(e.detail.get(key, 0) for e in events if e.action == action)

    def occurrences(action: str) -> int:
        return len([e for e in events if e.action == action])

    reminders, escalations = total("followup_completed", "reminders"), total(
        "followup_completed", "escalations"
    )
    by_event = (occurrences("finding_reminder_sent"), occurrences("finding_escalated"))
    if (reminders, escalations) != by_event:
        raise UnscorableRows(
            f"the trail disagrees with itself about the chase: the cycles report "
            f"{reminders} reminders and {escalations} escalations, the individual "
            f"events {by_event[0]} and {by_event[1]}. One of them is wrong and "
            f"neither is safe to print"
        )
    return {
        "screened": total("prescreen_completed", "considered"),
        "assessed": total("assessment_completed", "assessed"),
        "reminders": reminders,
        "escalations": escalations,
        "remediated": occurrences("assessment_superseded"),
    }


def token_usage(conn) -> dict[str, Any]:
    row = conn.execute(
        "SELECT COUNT(*) calls, COALESCE(SUM(input_tokens),0) input,"
        " COALESCE(SUM(output_tokens),0) output,"
        " COALESCE(SUM(cached_tokens),0) cached,"
        " COALESCE(SUM(cost_usd),0) cost FROM token_usage"
    ).fetchone()
    # Per stage as well as in total, because from slice 19 the stages do not all
    # run on the same model, and "what did this cost" is not answerable from a
    # single sum once that is true. Read from the rows the meter wrote, so it
    # reports what answered rather than what is configured now.
    by_stage = [
        {
            "tier": r["tier"],
            "model": r["model"],
            "calls": r["calls"],
            "input_tokens": r["input"],
            "output_tokens": r["output"],
            "cached_tokens": r["cached"],
            "cost_usd": round(r["cost"], 4),
        }
        for r in conn.execute(
            "SELECT tier, model, COUNT(*) calls,"
            " COALESCE(SUM(input_tokens),0) input,"
            " COALESCE(SUM(output_tokens),0) output,"
            " COALESCE(SUM(cached_tokens),0) cached,"
            " COALESCE(SUM(cost_usd),0) cost FROM token_usage"
            " GROUP BY tier, model ORDER BY tier, model"
        )
    ]
    return {
        "calls": row["calls"],
        "input_tokens": row["input"],
        "output_tokens": row["output"],
        "cached_tokens": row["cached"],
        "total_tokens": row["input"] + row["output"],
        "cost_usd": round(row["cost"], 4),
        "by_stage": by_stage,
    }


def action_closure(conn) -> dict[str, Any]:
    """Findings raised versus closed, and how long the closed ones took.

    Closure means an auditor said so — there is no other way for a finding to
    leave the open set, so this metric is measuring the real decision rather
    than a status a workflow moved on its own.
    """
    repo = repositories(conn)
    findings = repo["findings"].list()
    raised_at = {
        e.entity_id: e.ts
        for e in repo["audit"].read_all()
        if e.action == "finding_raised"
    }
    escalated = {
        e.entity_id for e in repo["audit"].read_all()
        if e.action == "finding_escalated"
    }
    closed = [f for f in findings if f.status == "closed"]
    unrecorded = sorted(f.id for f in closed if f.id not in raised_at)
    if unrecorded:
        raise UnscorableRows(
            f"closed finding(s) with no finding_raised event on the trail, so no "
            f"duration can be computed: {unrecorded[:5]}"
        )
    durations = [(f.closed_at - raised_at[f.id]).days for f in closed if f.closed_at]
    return {
        "raised": len(findings),
        "resolved": len(closed),
        "open": len([f for f in findings if f.status == "open"]),
        "escalated": len(escalated & {f.id for f in findings}),
        "resolution_rate": len(closed) / len(findings) if findings else 0.0,
        "mean_days_to_resolution": (
            round(statistics.mean(durations), 1) if durations else None
        ),
        "mean_follow_ups_to_close": (
            round(statistics.mean([f.follow_up_count for f in closed]), 1)
            if closed else None
        ),
    }


def first_verdicts(conn) -> dict[str, str]:
    """The verdict on the evidence as originally filed.

    This is the one to score gap detection against, and getting it wrong is a
    subtle way to make a working pipeline look broken. The truth file records
    what the *original* submission was — a near-miss, say — and the question
    "did we catch that?" is answered by the assessment of that submission.
    `current_verdicts` answers a different question: what is the state now. Once
    most gaps are remediated the two diverge completely, and scoring recall on
    the current state counts every successful fix as a missed gap.

    That is exactly what happened when the corpus went from six remediations to
    seventy-odd: recall read 12.8% against a pipeline that had in fact caught
    almost everything and then watched it get fixed.

    Round assessments (slice 14) carry no check instance. They used to fall into
    one key, `""`, which the scorer then skipped; they are excluded here by kind.
    """
    repo = repositories(conn)
    first: dict[str, Any] = {}
    for assessment in sorted(repo["assessments"].list(), key=lambda a: a.id):
        if not assessment.check_instance_id:
            continue
        if assessment.supersedes_assessment_id:
            continue  # a re-assessment of a fix, not the original judgement
        first.setdefault(assessment.check_instance_id, assessment.verdict)
    return first


def score_recurrence(conn, truth: dict[str, Any]) -> dict[str, Any]:
    """Mark recurrence detection against the groups the corpus planted.

    Until the truth file carried `recurrence_groups`, this could not be done at
    all: the detector's output could be read and called plausible, which is not
    the same as being right. Two questions, and they pull in opposite
    directions —

      **recall**    of the pairs we planted, how many did it group together? A
                    detector that links nothing scores zero here.
      **precision** of the pairs it grouped, how many were planted? A detector
                    that links everything scores zero here.

    Scored on **connected components**, not on the individual links. The
    detector points each finding at the prior one it resembles, so a set of
    three arrives as a chain A→B→C — two links, not three. Counting links would
    mark the pair (A, C) as missed when the detector has in fact put all three
    in one group, which is what a reader would say it achieved. Direction is
    ignored for the same reason: the corpus says these three are the same gap,
    and which way the arrow points is bookkeeping.

    Scored on pairs within a group rather than whole groups, because a detector
    that finds two of a three-finding set has done most of the job and
    all-or-nothing would call that a total miss.

    **Scored on the audit track only, and that is not a convenience.** Section 2
    justifies a model here on semantic similarity across free text — the
    auditor's own words, with no shared vocabulary. That is exactly what
    audit-raised findings are. Activity-track findings carry a description the
    *system* generated from the control title and the failing clause, so "the
    same gap in a different unit" is derivable there by a rule: same control,
    different unit. Marking the detector wrong for linking those would score it
    against a definition the stakeholder did not give, and scoring it right
    would be crediting a model for arithmetic. Neither is a measurement, so the
    activity track is excluded and the exclusion is stated rather than hidden.

    A planted member the run never raised is refused. It used to be filtered out
    of its group silently, shrinking the set the recall was computed over.
    """
    from itertools import combinations

    repo = repositories(conn)
    findings = {
        f.id: f for f in repo["findings"].list() if f.source == "audit"
    }

    unknown = sorted({
        finding_id
        for group in truth.get("recurrence_groups", [])
        for finding_id in group["finding_ids"]
        if finding_id not in findings
    })
    if unknown:
        raise UnscorableRows(
            f"the truth file plants recurrence members this run never raised as "
            f"audit findings: {unknown}"
        )

    expected: set[frozenset[str]] = set()
    for group in truth.get("recurrence_groups", []):
        expected |= {frozenset(pair) for pair in combinations(group["finding_ids"], 2)}

    # union-find over the detected links, then every pair inside a component
    parent: dict[str, str] = {}

    def root(node: str) -> str:
        parent.setdefault(node, node)
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    links = 0
    for finding in findings.values():
        for prior in finding.recurrence_of:
            if prior not in findings:
                continue  # a link to an activity-track finding: out of scope by kind
            links += 1
            a, b = root(finding.id), root(prior)
            if a != b:
                parent[a] = b

    components: dict[str, list[str]] = {}
    for node in list(parent):
        components.setdefault(root(node), []).append(node)

    detected: set[frozenset[str]] = set()
    for members in components.values():
        detected |= {frozenset(pair) for pair in combinations(sorted(members), 2)}

    hit = expected & detected
    return {
        "planted_groups": len(truth.get("recurrence_groups", [])),
        "planted_pairs": len(expected),
        "links_asserted": links,
        "grouped_pairs": len(detected),
        "found": len(hit),
        "recall": len(hit) / len(expected) if expected else None,
        "precision": len(hit) / len(detected) if detected else None,
        "missed": sorted(tuple(sorted(pair)) for pair in expected - detected),
    }


def current_verdicts(conn) -> dict[str, str]:
    """The pipeline's final answer per instance, superseded findings excluded.

    The state of the world now. For "did we catch it?" use `first_verdicts`.
    """
    repo = repositories(conn)
    findings = repo["assessments"].list()
    superseded = {f.supersedes_assessment_id for f in findings if f.supersedes_assessment_id}
    return {
        f.check_instance_id: f.verdict
        for f in findings
        if f.id not in superseded and f.check_instance_id
    }
