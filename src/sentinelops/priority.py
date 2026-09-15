"""The priority order. Deterministic, documented, and printable in one sentence.

The prioritisation brief (section 2, use 5) is advisory, and the order it reads
must not come from the model: a model that ranked the queue would be making the
prioritisation decision section 2 keeps away from it. So the ranking is
arithmetic over five facts the record already holds, every weight is stated
here, and `formula_table()` prints them — for the same reason section 5's
reminder policy is printable. A weight nobody can read is a weight nobody can
challenge, and a formula written up in a slide deck drifts from the one that
runs.

    Findings are ordered by severity band (Major, then Minor, then Observation;
    a finding more than 365 days past its target counts one band higher), and
    within a band by points = criticality + timing + recurrence + follow-ups.

**Why severity gates rather than weighs.** Severity is the organising concept of
audit practice: the auditor assigns it and the report is written around it. The
first version multiplied severity by criticality and *added* timing, and timing
ran to 120 points while severity x criticality spanned 7.5 to 60 — so lateness
swamped severity, and a long-overdue Observation in Facilities outranked a Major
in HR that was 48 days late. Retuning the weights would only move the crossover.
A band removes it: no amount of lateness, recurrence or chasing lifts a finding
past one of higher severity.

**The one cross-band adjustment, and its bound.** A finding more than
`AGEING_PROMOTION_DAYS` past its target ranks in the band one above its own —
one band only, never above Major, and inside that band it competes on points
like everything else. The threshold is a year because a year is a full annual
audit cycle: the finding has outlived the audit that raised it and will meet the
next one still open. Nothing near section 5's range comes close — escalation is
a week past target — so in the normal course no finding crosses a band.

**Criticality is points within a band.** Critical 30, high 20, medium 10, low 0:
the spread the first version gave within the Major band, so findings raised as
Major keep the order they had.

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

#: Highest first. Auditor-assigned severity, or the model's suggestion where
#: none is assigned — labelled as such on the row.
SEVERITY_BANDS: tuple[str, ...] = ("Major", "Minor", "Observation")

#: More than this many days past target: ranked one band higher, never more.
AGEING_PROMOTION_DAYS = 365

#: The unit's criticality, as points within a band.
CRITICALITY_POINTS: dict[str, int] = {
    "critical": 30,
    "high": 20,
    "medium": 10,
    "low": 0,
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

FORMULA = (
    f"Findings are ordered by severity band ({', then '.join(SEVERITY_BANDS)}; a "
    f"finding more than {AGEING_PROMOTION_DAYS} days past its target counts one "
    f"band higher), and within a band by points = criticality + timing + "
    f"recurrence + follow-ups."
)


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


def band_for(severity: str, days_past_target: int) -> str:
    """The severity's own band, or one higher once it is more than a year late."""
    position = SEVERITY_BANDS.index(severity)
    if days_past_target > AGEING_PROMOTION_DAYS and position > 0:
        position -= 1
    return SEVERITY_BANDS[position]


def order_key(row: dict[str, Any]) -> tuple:
    """Band first, then points, then the earlier target date, then the id."""
    return (SEVERITY_BANDS.index(row["band"]), -row["score"], row["target_date"],
            row["id"])


def score(
    finding, *, criticality: str | None, recurrence_links: int, as_of: date,
) -> dict[str, Any]:
    """The five inputs, the band, the four point components and their total."""
    severity = finding.severity or finding.suggested_severity
    identifier = getattr(finding, "id", "?")
    if severity not in SEVERITY_BANDS:
        raise UnscorableFinding(
            f"{identifier} has no assigned or suggested severity to score"
        )
    if criticality not in CRITICALITY_POINTS:
        raise UnscorableFinding(
            f"{identifier}: unit criticality {criticality!r} is not one of "
            f"{sorted(CRITICALITY_POINTS)}"
        )
    days = (as_of - finding.target_date).days
    band = band_for(severity, days)
    components = {
        "criticality": CRITICALITY_POINTS[criticality],
        "timing": timing_points(days),
        "recurrence": min(recurrence_links, RECURRENCE_LINK_CAP) * RECURRENCE_POINTS,
        "follow_ups": min(finding.follow_up_count, FOLLOW_UP_CAP) * FOLLOW_UP_POINTS,
    }
    aged_up = band != severity
    return {
        "severity": severity,
        "severity_source": "assigned" if finding.severity else "suggested",
        "band": band,
        "aged_up": aged_up,
        "band_label": f"{band} (raised {severity})" if aged_up else band,
        "criticality": criticality,
        "days_past_target": days,
        "timing_label": timing_label(days),
        "recurrence_links": recurrence_links,
        "follow_ups": finding.follow_up_count,
        "components": components,
        "score": sum(components.values()),
    }


def explain(row: dict[str, Any]) -> str:
    """The band and the arithmetic behind the points, in one line."""
    components = row["components"]
    head = f"{row['band']} band"
    if row["aged_up"]:
        head += (
            f" (raised {row['severity']}; more than {AGEING_PROMOTION_DAYS}d past "
            f"target)"
        )
    parts = [
        f"{row['criticality']} {components['criticality']}",
        f"{row['timing_label']} {components['timing']}",
    ]
    if components["recurrence"]:
        parts.append(
            f"{row['recurrence_links']} recurrence link(s) {components['recurrence']}"
        )
    if components["follow_ups"]:
        parts.append(f"chased {row['follow_ups']}x {components['follow_ups']}")
    return f"{head}: " + " + ".join(parts) + f" = {row['score']:g}"


def rank(repo, people, as_of: date) -> list[dict[str, Any]]:
    """Every open finding, banded, scored and ordered."""
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

    rows.sort(key=order_key)
    for position, row in enumerate(rows, start=1):
        row["rank"] = position
    return rows


def listed_metrics(rows: list[dict[str, Any]]) -> dict[str, int]:
    """Counts over exactly the ranked rows a brief is given, and nothing else.

    The brief sees the top of the ranking, not all of it. A statement about
    those rows — "four of them share a category" — needs a figure of the same
    scope to cite, or it ends up resting on a portfolio-wide figure that counts
    something else. Named `listed_*` so the scope is in the name.
    """
    metrics: dict[str, int] = {"listed_findings": len(rows)}
    for prefix, key in (("listed_in_unit", "unit"), ("listed_category", "category"),
                        ("listed_band", "band")):
        for value, count in sorted(Counter(row[key] for row in rows).items()):
            metrics[f"{prefix}:{value}"] = count
    metrics["listed_past_target"] = sum(1 for r in rows if r["days_past_target"] > 0)
    metrics["listed_with_recurrence_links"] = sum(
        1 for r in rows if r["recurrence_links"]
    )
    return metrics


def formula_table() -> str:
    """The sentence and every weight, printable. Read from the constants above."""
    highest = (
        max(CRITICALITY_POINTS.values()) + TIMING_AT_TARGET + TIMING_DAYS_PAST_CAP
        + RECURRENCE_LINK_CAP * RECURRENCE_POINTS + FOLLOW_UP_CAP * FOLLOW_UP_POINTS
    )
    return "\n".join([
        FORMULA,
        "",
        f"  bands         {' > '.join(SEVERITY_BANDS)}; points never lift a finding "
        f"past a higher band",
        f"  aged up       more than {AGEING_PROMOTION_DAYS} days past target (a full "
        f"annual audit cycle): one band higher, never more, never above "
        f"{SEVERITY_BANDS[0]}",
        "  criticality   "
        + " / ".join(f"{name} {points}" for name, points in CRITICALITY_POINTS.items()),
        f"  timing        {TIMING_AT_TARGET} on the target date; +1 a day past it, "
        f"up to {TIMING_DAYS_PAST_CAP} days; -1 a day before it, 0 from "
        f"{TIMING_AT_TARGET} days out",
        f"  recurrence    +{RECURRENCE_POINTS} per link to an earlier or later "
        f"finding, up to {RECURRENCE_LINK_CAP} links",
        f"  follow-ups    +{FOLLOW_UP_POINTS} per reminder or insufficient round, "
        f"up to {FOLLOW_UP_CAP}",
        "",
        f"  points within a band run 0 to {highest}; ties go to the earlier target "
        f"date, then the id",
    ])
