"""The priority score. Deterministic, documented, and printable.

The prioritisation brief (section 2, use 5) is advisory, and the order it reads
must not come from the model: a model that ranked the queue would be making the
prioritisation decision section 2 keeps away from it. So the ranking is
arithmetic over five facts the record already holds, every weight is stated
here, and `formula_table()` prints them — for the same reason section 5's
reminder policy is printable. A weight nobody can read is a weight nobody can
challenge, and a formula written up in a slide deck drifts from the one that
runs.

    score = severity points x unit criticality
          + timing points
          + recurrence points
          + follow-up points

**Why severity is multiplied by criticality.** A Major against a
business-critical unit is not a Major plus a little criticality; it is a larger
exposure. The other three terms add, because they are evidence that a finding is
not being dealt with rather than a measure of how bad it is.

**Nothing is guessed.** A finding with neither an assigned nor a suggested
severity, a unit with no recognised criticality, or a recurrence link pointing at
a finding that does not exist, is refused rather than scored as if it were the
mildest case. A silently defaulted input is how a ranking ends up confidently
wrong.

Imports nothing from the provider boundary; `tests/test_priority.py` asserts it.
"""

from __future__ import annotations

from collections import Counter
from datetime import date
from typing import Any

#: Auditor-assigned severity, or the model's suggestion where none is assigned.
SEVERITY_POINTS: dict[str, int] = {"Major": 40, "Minor": 20, "Observation": 10}

#: The unit's criticality attribute scales the severity term.
CRITICALITY_MULTIPLIER: dict[str, float] = {
    "critical": 1.5,
    "high": 1.25,
    "medium": 1.0,
    "low": 0.75,
}

#: Thirty points on the target date. One more for each day past it, up to ninety
#: days past; one fewer for each day before it, so a finding a month or more from
#: its target carries no timing weight at all.
TIMING_AT_TARGET = 30
TIMING_DAYS_PAST_CAP = 90

#: Per recurrence link, earlier or later: a gap that keeps coming back outranks
#: one that has appeared once.
RECURRENCE_POINTS = 10
RECURRENCE_LINK_CAP = 3

#: Per reminder or insufficient evidence round — `follow_up_count`, which
#: section 5 increments on both.
FOLLOW_UP_POINTS = 3
FOLLOW_UP_CAP = 10


class UnscorableFinding(ValueError):
    """A finding lacks an input the score needs. Refused, never defaulted."""


def timing_points(days_past_target: int) -> int:
    """30 at the target date, climbing past it to a cap, falling to 0 before it."""
    return max(0, TIMING_AT_TARGET + min(days_past_target, TIMING_DAYS_PAST_CAP))


def timing_label(days_past_target: int) -> str:
    if days_past_target > 0:
        return f"{days_past_target}d past target"
    if days_past_target < 0:
        return f"{-days_past_target}d to target"
    return "due today"


def score(
    finding, *, criticality: str | None, recurrence_links: int, as_of: date,
) -> dict[str, Any]:
    """The five inputs, the four components and the total, for one finding."""
    severity = finding.severity or finding.suggested_severity
    identifier = getattr(finding, "id", "?")
    if severity not in SEVERITY_POINTS:
        raise UnscorableFinding(
            f"{identifier} has no assigned or suggested severity to score"
        )
    if criticality not in CRITICALITY_MULTIPLIER:
        raise UnscorableFinding(
            f"{identifier}: unit criticality {criticality!r} is not one of "
            f"{sorted(CRITICALITY_MULTIPLIER)}"
        )
    days = (as_of - finding.target_date).days
    components = {
        "impact": round(
            SEVERITY_POINTS[severity] * CRITICALITY_MULTIPLIER[criticality], 1
        ),
        "timing": timing_points(days),
        "recurrence": min(recurrence_links, RECURRENCE_LINK_CAP) * RECURRENCE_POINTS,
        "follow_ups": min(finding.follow_up_count, FOLLOW_UP_CAP) * FOLLOW_UP_POINTS,
    }
    return {
        "severity": severity,
        "severity_source": "assigned" if finding.severity else "suggested",
        "criticality": criticality,
        "days_past_target": days,
        "timing_label": timing_label(days),
        "recurrence_links": recurrence_links,
        "follow_ups": finding.follow_up_count,
        "components": components,
        "score": round(sum(components.values()), 1),
    }


def explain(row: dict[str, Any]) -> str:
    """The arithmetic behind one score, in one line."""
    components = row["components"]
    parts = [
        f"{row['severity']} x {row['criticality']} {components['impact']:g}",
        f"{row['timing_label']} {components['timing']}",
    ]
    if components["recurrence"]:
        parts.append(
            f"{row['recurrence_links']} recurrence link(s) {components['recurrence']}"
        )
    if components["follow_ups"]:
        parts.append(f"chased {row['follow_ups']}x {components['follow_ups']}")
    return " + ".join(parts) + f" = {row['score']:g}"


def rank(repo, people, as_of: date) -> list[dict[str, Any]]:
    """Every open finding, scored and ordered. Ties: earlier target date, then id."""
    units = {u.id: u for u in repo["units"].list()}
    findings = repo["findings"].list()
    known = {f.id for f in findings}

    dangling = sorted(
        (f.id, prior)
        for f in findings for prior in f.recurrence_of if prior not in known
    )
    if dangling:
        raise UnscorableFinding(
            f"recurrence links point at findings that do not exist: {dangling[:5]}"
        )
    recurred_from = Counter(prior for f in findings for prior in f.recurrence_of)

    rows = []
    for finding in findings:
        if finding.status != "open":
            continue
        unit = units.get(finding.auditable_unit_id)
        if unit is None:
            raise UnscorableFinding(
                f"{finding.id} is raised against {finding.auditable_unit_id}, "
                f"which is not a unit"
            )
        row = score(
            finding,
            criticality=unit.attributes.get("criticality"),
            recurrence_links=len(finding.recurrence_of) + recurred_from.get(finding.id, 0),
            as_of=as_of,
        )
        row.update({
            "id": finding.id,
            "unit": unit.name,
            "category": finding.gap_category or "unclassified",
            "owner": people.name(finding.owner_identity),
            "target_date": finding.target_date.isoformat(),
            "recurrence_of": list(finding.recurrence_of),
            "description": finding.description,
        })
        row["explain"] = explain(row)
        rows.append(row)

    rows.sort(key=lambda r: (-r["score"], r["target_date"], r["id"]))
    for position, row in enumerate(rows, start=1):
        row["rank"] = position
    return rows


def formula_table() -> str:
    """The formula and every weight, printable. Read from the constants above."""
    lowest = min(SEVERITY_POINTS.values()) * min(CRITICALITY_MULTIPLIER.values())
    highest = (
        max(SEVERITY_POINTS.values()) * max(CRITICALITY_MULTIPLIER.values())
        + TIMING_AT_TARGET + TIMING_DAYS_PAST_CAP
        + RECURRENCE_LINK_CAP * RECURRENCE_POINTS
        + FOLLOW_UP_CAP * FOLLOW_UP_POINTS
    )
    return "\n".join([
        "priority score = severity x criticality + timing + recurrence + follow-ups",
        "",
        "  severity      "
        + " / ".join(f"{name} {points}" for name, points in SEVERITY_POINTS.items()),
        "  criticality   "
        + " / ".join(f"{name} x{m:g}" for name, m in CRITICALITY_MULTIPLIER.items()),
        f"  timing        {TIMING_AT_TARGET} on the target date; +1 a day past it, "
        f"up to {TIMING_DAYS_PAST_CAP} days; -1 a day before it, 0 from "
        f"{TIMING_AT_TARGET} days out",
        f"  recurrence    +{RECURRENCE_POINTS} per link to an earlier or later "
        f"finding, up to {RECURRENCE_LINK_CAP} links",
        f"  follow-ups    +{FOLLOW_UP_POINTS} per reminder or insufficient round, "
        f"up to {FOLLOW_UP_CAP}",
        "",
        f"  range {lowest:g} to {highest:g}; ties go to the earlier target date, "
        f"then the id",
    ])
