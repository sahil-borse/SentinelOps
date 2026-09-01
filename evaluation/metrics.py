"""The seven metrics of section 6, each computed from what the run left behind.

Nothing here re-derives a verdict or re-runs a stage. Every figure is read out
of the database the pipeline wrote, or out of the truth file, and the two are
joined on the instance key. If a number cannot be computed from the record, it
is not reported.
"""

from __future__ import annotations

import json
import statistics
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from sentinelops.repositories import repositories

TRUTH_DIR = Path(__file__).resolve().parents[1] / "data" / "truth"

#: A verdict counts as "this failed" for gap detection.
POSITIVE = ("gap",)


def load_ground_truth(year: int = 2026) -> dict[str, Any]:
    """The only read of the truth file in the entire project."""
    return json.loads((TRUTH_DIR / f"truth_{year}.json").read_text(encoding="utf-8"))


def truth_by_instance(truth: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = {}
    for row in truth["rows"]:
        if row["is_remediation"] or row["defect_kind"] == "exception_suppressed":
            continue
        key = (
            f"CHK-{row['control_id'].removeprefix('CTRL-')}-"
            f"{row['process_area_id'].removeprefix('AREA-')}-{row['period']}"
        )
        rows[key] = row
    return rows


@dataclass
class Confusion:
    true_positive: int = 0
    false_positive: int = 0
    true_negative: int = 0
    false_negative: int = 0

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

    Positive class is `gap`. Only instances present in both the run and the
    truth file are scored, so a pipeline is never credited or blamed for
    something it was never shown.
    """
    confusion = Confusion()
    for key, verdict in verdicts.items():
        row = truth_rows.get(key)
        if row is None or row["expected_verdict"] is None:
            continue
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
    return confusion


def missed_checks(conn, truth_rows: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """A check is missed when it was due and nothing ever looked at it.

    For the automated path this is answerable from the record: every due
    instance either has a finding or does not. Note that "no evidence was
    filed" is *not* a missed check — the system raised it, chased it and
    recorded the absence, which is the opposite of missing it.
    """
    repo = repositories(conn)
    instances = repo["instances"].list()
    findings = {f.check_instance_id for f in repo["findings"].list()}
    due = [i for i in instances if i.status != "waived"]
    unexamined = [i for i in due if i.id not in findings]
    return {
        "due": len(due),
        "examined": len(due) - len(unexamined),
        "missed": len(unexamined),
        "rate": len(unexamined) / len(due) if due else 0.0,
    }


def time_to_detection(conn) -> dict[str, Any]:
    """Days from a check falling due to its non-compliance being written down."""
    repo = repositories(conn)
    instances = {i.id: i for i in repo["instances"].list()}
    superseded = {
        f.supersedes_finding_id
        for f in repo["findings"].list()
        if f.supersedes_finding_id
    }
    gaps = []
    for finding in repo["findings"].list():
        if finding.verdict == "compliant" or finding.id in superseded:
            continue
        instance = instances.get(finding.check_instance_id)
        if instance is None or finding.assessed_at is None:
            continue
        gaps.append((finding.assessed_at.date() - instance.due_date).days)
    return _spread(gaps)


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
        f.supersedes_finding_id
        for f in repo["findings"].list()
        if f.supersedes_finding_id
    }
    for finding in repo["findings"].list():
        if finding.id not in superseded:
            findings[finding.check_instance_id] = finding

    instances = {i.id: i for i in repo["instances"].list()}
    groups: dict[tuple[str, str], list[str]] = {}
    for evidence in repo["evidence"].list():
        if evidence.is_remediation:
            continue
        instance = instances.get(evidence.check_instance_id)
        if instance is None:
            continue
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
        f.supersedes_finding_id
        for f in repo["findings"].list()
        if f.supersedes_finding_id
    }
    current = [f for f in repo["findings"].list() if f.id not in superseded]
    by_tier: dict[str, int] = {}
    for finding in current:
        by_tier[finding.decided_by] = by_tier.get(finding.decided_by, 0) + 1
    rules = sum(v for k, v in by_tier.items() if not k.startswith("s3_"))
    return {
        "findings": len(current),
        "decided_by_rules": rules,
        "decided_by_model": len(current) - rules,
        "share": rules / len(current) if current else 0.0,
        "by_tier": dict(sorted(by_tier.items())),
    }


def token_usage(conn) -> dict[str, Any]:
    row = conn.execute(
        "SELECT COUNT(*) calls, COALESCE(SUM(input_tokens),0) input,"
        " COALESCE(SUM(output_tokens),0) output,"
        " COALESCE(SUM(cached_tokens),0) cached,"
        " COALESCE(SUM(cost_usd),0) cost FROM token_usage"
    ).fetchone()
    return {
        "calls": row["calls"],
        "input_tokens": row["input"],
        "output_tokens": row["output"],
        "cached_tokens": row["cached"],
        "total_tokens": row["input"] + row["output"],
        "cost_usd": round(row["cost"], 4),
    }


def action_closure(conn) -> dict[str, Any]:
    """Raised versus resolved, and how long the ones that closed took."""
    repo = repositories(conn)
    actions = repo["actions"].list()
    raised_at = {
        e.entity_id: e.ts
        for e in repo["audit"].read_all()
        if e.action == "action_raised"
    }
    resolved = [a for a in actions if a.status == "resolved"]
    durations = [
        (a.resolved_at - raised_at[a.id]).days
        for a in resolved
        if a.id in raised_at and a.resolved_at
    ]
    return {
        "raised": len(actions),
        "resolved": len(resolved),
        "open": len([a for a in actions if a.status != "resolved"]),
        "escalated": len([a for a in actions if a.status == "escalated"]),
        "resolution_rate": len(resolved) / len(actions) if actions else 0.0,
        "mean_days_to_resolution": (
            round(statistics.mean(durations), 1) if durations else None
        ),
    }


def current_verdicts(conn) -> dict[str, str]:
    """The pipeline's final answer per instance, superseded findings excluded."""
    repo = repositories(conn)
    findings = repo["findings"].list()
    superseded = {f.supersedes_finding_id for f in findings if f.supersedes_finding_id}
    return {
        f.check_instance_id: f.verdict for f in findings if f.id not in superseded
    }
