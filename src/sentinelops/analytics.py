"""Section 8, in full. Deterministic, from state and the audit log.

Section 2 lists analytics under **never AI**, and this module is where that
promise is kept: every figure here is arithmetic over rows the pipeline already
wrote. Nothing in it imports the provider boundary, and a test asserts so.

Two of these only became answerable with the eighteen-month corpus. **Trend over
time** needs more months than a quarter to be a trend rather than three points,
and **recurring findings** needs the same gap category to appear in places far
enough apart that a person would not have joined them up. That is the whole
argument for the corpus being the size it is.

The functions return plain dicts and lists rather than dataclasses because every
caller — the dashboard, the audit pack, `results.md` — wants to render them, not
to compute with them further.
"""

from __future__ import annotations

import statistics
from datetime import date, timedelta
from typing import Any

#: Section 8's buckets, exactly.
AGEING_BUCKETS: tuple[tuple[str, int, int], ...] = (
    ("0-30", 0, 30),
    ("31-60", 31, 60),
    ("61-90", 61, 90),
    ("90+", 91, 10_000),
)

SEVERITIES = ("Major", "Minor", "Observation")

#: "The next 30 days" from section 8's last line.
HORIZON_DAYS = 30

#: Below this many open findings a month, in either direction, the fitted line
#: is called flat. At the stakeholder's scale — fifteen to eighteen open at any
#: time — a drift of three findings over a year is one busy audit, not a trend,
#: and a verdict that swings on it would say "rising" about noise.
FLAT_SLOPE_PER_MONTH = 0.25

#: The recent read compares the last three months with the three before them.
#: A quarter against a quarter, because audits run on roughly that cadence and a
#: shorter window mostly measures which week an audit happened to land in.
RECENT_MONTHS = 3

#: A change smaller than this between the two quarters' averages is flat.
RECENT_FLAT_BAND = 1.0


def _units(repo) -> dict[str, str]:
    return {u.id: u.name for u in repo["units"].list()}


def _severity(finding) -> str:
    return finding.severity or finding.suggested_severity or "unassigned"


def _quarter(day: date) -> str:
    """The period a finding belongs to, for "a different period".

    Calendar quarter of the day it was raised. Stated rather than inferred from
    the control's own frequency, because audit-track findings have no control
    and the comparison has to mean the same thing on both tracks.
    """
    return f"{day.year}-Q{(day.month - 1) // 3 + 1}"


def open_vs_closed(repo) -> dict[str, Any]:
    """Count *and percentage*, overall and per unit. Section 8's first line."""
    findings = repo["findings"].list()
    units = _units(repo)
    per_unit: dict[str, dict[str, Any]] = {}
    for finding in findings:
        name = units.get(finding.auditable_unit_id, finding.auditable_unit_id)
        row = per_unit.setdefault(name, {"open": 0, "closed": 0})
        row["open" if finding.status == "open" else "closed"] += 1
    for row in per_unit.values():
        total = row["open"] + row["closed"]
        row["total"] = total
        row["open_pct"] = round(100 * row["open"] / total, 1) if total else 0.0
        row["closed_pct"] = round(100 * row["closed"] / total, 1) if total else 0.0

    total = len(findings)
    closed = len([f for f in findings if f.status == "closed"])
    return {
        "total": total,
        "open": total - closed,
        "closed": closed,
        "open_pct": round(100 * (total - closed) / total, 1) if total else 0.0,
        "closed_pct": round(100 * closed / total, 1) if total else 0.0,
        "by_unit": dict(sorted(per_unit.items())),
    }


def severity_mix(repo) -> dict[str, Any]:
    """Major / Minor / Observation, overall and per unit."""
    units = _units(repo)
    overall = {s: 0 for s in SEVERITIES}
    per_unit: dict[str, dict[str, int]] = {}
    for finding in repo["findings"].list():
        severity = _severity(finding)
        overall[severity] = overall.get(severity, 0) + 1
        name = units.get(finding.auditable_unit_id, finding.auditable_unit_id)
        row = per_unit.setdefault(name, {s: 0 for s in SEVERITIES})
        row[severity] = row.get(severity, 0) + 1
    return {"overall": overall, "by_unit": dict(sorted(per_unit.items()))}


def overdue_ageing(repo, as_of: date) -> dict[str, Any]:
    """Open findings past their target date, bucketed by how far past."""
    buckets = {name: 0 for name, _, _ in AGEING_BUCKETS}
    detail: dict[str, list[str]] = {name: [] for name, _, _ in AGEING_BUCKETS}
    oldest = 0
    for finding in repo["findings"].list():
        if finding.status != "open":
            continue
        days = (as_of - finding.target_date).days
        if days < 0:
            continue
        oldest = max(oldest, days)
        for name, low, high in AGEING_BUCKETS:
            if low <= days <= high:
                buckets[name] += 1
                detail[name].append(finding.id)
                break
    return {
        "buckets": buckets,
        "findings": {name: sorted(ids) for name, ids in detail.items()},
        "total": sum(buckets.values()),
        "oldest_days": oldest,
    }


def by_dimension(repo) -> dict[str, dict[str, int]]:
    """Findings by auditable unit, by gap category, and by audit kind."""
    units = _units(repo)
    audits = {a.id: a.kind for a in repo["audits"].list()}
    unit_counts: dict[str, int] = {}
    category_counts: dict[str, int] = {}
    kind_counts: dict[str, int] = {}
    for finding in repo["findings"].list():
        name = units.get(finding.auditable_unit_id, finding.auditable_unit_id)
        unit_counts[name] = unit_counts.get(name, 0) + 1
        category = finding.gap_category or "unclassified"
        category_counts[category] = category_counts.get(category, 0) + 1
        kind = (
            audits.get(finding.audit_id, "unknown_audit") if finding.audit_id
            else "compliance_activity"
        )
        kind_counts[kind] = kind_counts.get(kind, 0) + 1

    def ranked(counts: dict[str, int]) -> dict[str, int]:
        return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))

    return {
        "by_unit": ranked(unit_counts),
        "by_category": ranked(category_counts),
        "by_audit_kind": ranked(kind_counts),
    }


def recurring_categories(findings, units: dict[str, str]) -> dict[str, Any]:
    """Section 8's definition, computed: same gap category, different unit or period.

    A category recurs when it holds two or more findings that do not all sit in
    one unit *and* one quarter. Nothing semantic happens here and nothing is
    asked of a model. The category itself was suggested by one and may have been
    overridden by an auditor, but by the time this runs it is a stored field, and
    grouping stored fields is arithmetic.
    """
    groups: dict[str, list[Any]] = {}
    for finding in findings:
        if finding.gap_category:
            groups.setdefault(finding.gap_category, []).append(finding)

    rows: dict[str, dict[str, Any]] = {}
    for category, members in groups.items():
        if len(members) < 2:
            continue
        unit_ids = {m.auditable_unit_id for m in members}
        periods = {_quarter(m.raised_at.date()) for m in members}
        if len(unit_ids) < 2 and len(periods) < 2:
            continue  # the same place at the same time is one problem, not a recurrence
        ordered = sorted(members, key=lambda m: (m.raised_at, m.id))
        first, last = ordered[0].raised_at.date(), ordered[-1].raised_at.date()
        sources: dict[str, int] = {}
        for member in members:
            sources[member.source] = sources.get(member.source, 0) + 1
        rows[category] = {
            "findings": len(members),
            "finding_ids": [m.id for m in ordered],
            "units": len(unit_ids),
            "unit_names": sorted(units.get(u, u) for u in unit_ids),
            "periods": sorted(periods),
            "spans_units": len(unit_ids) > 1,
            "spans_periods": len(periods) > 1,
            "first_raised": first.isoformat(),
            "last_raised": last.isoformat(),
            "months_spanned": max((last - first).days // 30, 0),
            "by_source": dict(sorted(sources.items())),
        }
    ordered_rows = dict(
        sorted(rows.items(), key=lambda kv: (-kv[1]["findings"], kv[0]))
    )
    return {
        "categories": ordered_rows,
        "count": len(ordered_rows),
        "spanning_units": len([r for r in rows.values() if r["spans_units"]]),
        "spanning_periods": len([r for r in rows.values() if r["spans_periods"]]),
        "findings_involved": sum(r["findings"] for r in rows.values()),
    }


def recurring(repo) -> dict[str, Any]:
    """Recurring findings, in two forms that answer different questions.

    **The section 8 figure is `by_gap_category`.** Section 8 defines a recurring
    finding as the same gap category in a different unit, project or period, and
    that is a grouping over stored fields, so it is computed here and nothing
    else. `audit_track` repeats it over audit-raised findings only, because those
    carry an auditor's own words and are where section 1's claim about recurrence
    lives; activity-track descriptions are generated from a control title.

    **The detector's links are reported beside it, not instead of it.** Section 2
    use 2 has a model read descriptions and point a finding at an earlier one it
    resembles. Those pointers are stored state too, so reading them is still
    arithmetic, but what they measure is the detector's judgement. They were this
    function's only output until slice 15, which made the section 8 number a
    function of the stub's vocabulary: the report had to carry a paragraph
    apologising for one category being over-represented.

    Links are not merged into sets. An earlier version did, so A→B and B→C became
    one group, and on this corpus it collapsed into a single "set" of forty-five
    findings — the union-find algorithm reporting that the graph is connected.
    Chains are still shown where they are short, because a problem that came back
    twice in different places reads as one story.
    """
    findings = {f.id: f for f in repo["findings"].list()}
    units = _units(repo)

    links = []
    for finding in findings.values():
        for prior_id in finding.recurrence_of:
            prior = findings.get(prior_id)
            if prior is None:
                continue
            links.append({
                "finding": finding.id,
                "prior": prior.id,
                "category": finding.gap_category,
                "unit": units.get(finding.auditable_unit_id,
                                  finding.auditable_unit_id),
                "prior_unit": units.get(prior.auditable_unit_id,
                                        prior.auditable_unit_id),
                "spans_units": (
                    prior.auditable_unit_id != finding.auditable_unit_id
                ),
                "spans_periods": (
                    _quarter(prior.raised_at.date())
                    != _quarter(finding.raised_at.date())
                ),
                "months_apart": max(
                    (finding.raised_at - prior.raised_at).days // 30, 0
                ),
            })
    links.sort(key=lambda link: (-link["months_apart"], link["finding"], link["prior"]))

    by_category: dict[str, dict[str, Any]] = {}
    for link in links:
        row = by_category.setdefault(
            link["category"] or "unclassified",
            {"links": 0, "units": set(), "max_months": 0},
        )
        row["links"] += 1
        row["units"].update({link["unit"], link["prior_unit"]})
        row["max_months"] = max(row["max_months"], link["months_apart"])
    rollup = {
        name: {
            "links": row["links"],
            "units": len(row["units"]),
            "unit_names": sorted(row["units"]),
            "max_months_apart": row["max_months"],
        }
        for name, row in sorted(
            by_category.items(), key=lambda kv: (-kv[1]["links"], kv[0])
        )
    }

    # Chains, for the few that read as one story rather than a category-wide
    # pattern. Followed backwards from each finding, and capped.
    chains = []
    for finding in findings.values():
        chain = [finding.id]
        cursor = finding
        seen = {finding.id}
        while cursor.recurrence_of:
            prior_id = cursor.recurrence_of[0]
            if prior_id in seen or prior_id not in findings:
                break
            seen.add(prior_id)
            chain.append(prior_id)
            cursor = findings[prior_id]
        if len(chain) >= 3:
            ordered = list(reversed(chain))
            involved = {findings[i].auditable_unit_id for i in ordered}
            chains.append({
                "findings": ordered,
                "category": findings[ordered[0]].gap_category,
                "units": sorted(units.get(u, u) for u in involved),
                "spans_units": len(involved) > 1,
                "months_spanned": max(
                    (findings[ordered[-1]].raised_at
                     - findings[ordered[0]].raised_at).days // 30, 0
                ),
            })
    # keep the longest distinct chains, dropping any that is a prefix of another
    chains.sort(key=lambda c: (-len(c["findings"]), c["findings"][0]))
    kept: list[dict[str, Any]] = []
    covered: set[str] = set()
    for chain in chains:
        if set(chain["findings"]) <= covered:
            continue
        kept.append(chain)
        covered |= set(chain["findings"])

    everything = list(findings.values())
    return {
        "by_gap_category": recurring_categories(everything, units),
        "audit_track": recurring_categories(
            [f for f in everything if f.source == "audit"], units
        ),
        "links": links,
        "count": len(links),
        "spanning_units": len([link for link in links if link["spans_units"]]),
        "spanning_periods": len([link for link in links if link["spans_periods"]]),
        "findings_involved": len({link["finding"] for link in links}
                                 | {link["prior"] for link in links}),
        "by_category": rollup,
        "longest_chains": kept[:5],
    }


def effort_distribution(repo) -> dict[str, Any]:
    """Findings needing multiple evidence rounds or multiple reminders.

    Two different kinds of effort and section 8 asks for both. A finding chased
    six times without a reply is a different problem from one that came back
    three times with the wrong evidence, and averaging them would hide both.
    """
    rounds: dict[str, int] = {}
    for record in repo["rounds"].list():
        rounds[record.finding_id] = rounds.get(record.finding_id, 0) + 1
    reminders: dict[str, int] = {}
    for event in repo["audit"].read_all():
        if event.action == "finding_reminder_sent":
            reminders[event.entity_id] = reminders.get(event.entity_id, 0) + 1

    def histogram(counts: dict[str, int], population: int) -> dict[str, int]:
        out = {"0": population - len(counts)}
        for value in counts.values():
            key = str(value) if value < 5 else "5+"
            out[key] = out.get(key, 0) + 1
        return dict(sorted(out.items()))

    findings = repo["findings"].list()
    return {
        "rounds": histogram(rounds, len(findings)),
        "reminders": histogram(reminders, len(findings)),
        "multi_round": len([n for n in rounds.values() if n > 1]),
        "multi_reminder": len([n for n in reminders.values() if n > 1]),
        "worst_rounds": max(rounds.values(), default=0),
        "worst_reminders": max(reminders.values(), default=0),
        "multi_round_findings": sorted(
            fid for fid, n in rounds.items() if n > 1
        ),
        "three_plus_round_findings": sorted(
            fid for fid, n in rounds.items() if n >= 3
        ),
    }


def _month_starts(start: date, end: date) -> list[date]:
    months: list[date] = []
    cursor = date(start.year, start.month, 1)
    while cursor <= end:
        months.append(cursor)
        cursor = date(
            cursor.year + (cursor.month == 12),
            1 if cursor.month == 12 else cursor.month + 1,
            1,
        )
    return months


def trend(repo, start: date, end: date) -> list[dict[str, Any]]:
    """Open finding count by month across the corpus window.

    Computed by replaying raise and close dates rather than by sampling state,
    so the line is what was actually true at each month end rather than what is
    true now projected backwards. The last point is cut at `end` itself, not at
    the end of its month, because "today" is mid-month and the rest of April has
    not happened yet.
    """
    findings = repo["findings"].list()
    out = []
    for month in _month_starts(start, end):
        following = date(
            month.year + (month.month == 12),
            1 if month.month == 12 else month.month + 1,
            1,
        )
        cut = min(following - timedelta(days=1), end)
        raised = [f for f in findings if f.raised_at.date() <= cut]
        closed = [
            f for f in raised
            if f.closed_at is not None and f.closed_at.date() <= cut
        ]
        out.append({
            "month": f"{month.year}-{month.month:02d}",
            "as_of": cut.isoformat(),
            "raised_to_date": len(raised),
            "closed_to_date": len(closed),
            "open": len(raised) - len(closed),
        })
    return out


def _slope(values: list[int]) -> float:
    """Least-squares slope against month index. Plain arithmetic, no library."""
    count = len(values)
    mean_x = (count - 1) / 2
    mean_y = sum(values) / count
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in enumerate(values))
    denominator = sum((x - mean_x) ** 2 for x in range(count))
    return numerator / denominator if denominator else 0.0


def trend_verdict(points: list[dict[str, Any]]) -> dict[str, Any]:
    """Rising, falling or flat — and the rule that decided it, stated.

    Two reads, because they can disagree and both are true. **Across the window**
    is the least-squares slope of open findings against month: robust to one
    spiky month, which a first-against-last comparison is not. **Recently** is
    the last quarter's average against the quarter before it: whether the most
    recent audits are adding faster than closures take away.

    A portfolio can be rising over eighteen months and falling this quarter.
    Reporting only one of those would be choosing which story to tell.
    """
    if len(points) < 2:
        return {
            "direction": "insufficient_history",
            "months": len(points),
            "rule": "a trend needs at least two months",
        }

    values = [p["open"] for p in points]
    slope = _slope(values)
    if slope >= FLAT_SLOPE_PER_MONTH:
        direction = "rising"
    elif slope <= -FLAT_SLOPE_PER_MONTH:
        direction = "falling"
    else:
        direction = "flat"

    peak_index = max(range(len(values)), key=lambda i: (values[i], -i))
    result: dict[str, Any] = {
        "direction": direction,
        "slope_per_month": round(slope, 2),
        "months": len(points),
        "first": {"month": points[0]["month"], "open": values[0]},
        "last": {"month": points[-1]["month"], "open": values[-1]},
        "peak": {"month": points[peak_index]["month"], "open": values[peak_index]},
        "rule": (
            f"least-squares slope of open findings per month; flat within "
            f"+/-{FLAT_SLOPE_PER_MONTH}"
        ),
    }

    if len(values) >= 2 * RECENT_MONTHS:
        last = values[-RECENT_MONTHS:]
        before = values[-2 * RECENT_MONTHS:-RECENT_MONTHS]
        last_mean = sum(last) / RECENT_MONTHS
        before_mean = sum(before) / RECENT_MONTHS
        change = last_mean - before_mean
        if change >= RECENT_FLAT_BAND:
            recent = "rising"
        elif change <= -RECENT_FLAT_BAND:
            recent = "falling"
        else:
            recent = "flat"
        result["recent"] = {
            "direction": recent,
            "last_quarter_mean": round(last_mean, 1),
            "previous_quarter_mean": round(before_mean, 1),
            "change": round(change, 1),
            "months": [p["month"] for p in points[-2 * RECENT_MONTHS:]],
            "rule": (
                f"mean of the last {RECENT_MONTHS} months against the "
                f"{RECENT_MONTHS} before; flat within +/-{RECENT_FLAT_BAND}"
            ),
        }
    else:
        result["recent"] = {
            "direction": "insufficient_history",
            "rule": f"needs {2 * RECENT_MONTHS} months",
        }
    return result


def closure_performance(repo) -> dict[str, Any]:
    """Mean and median days from raise to closure, by severity."""
    by_severity: dict[str, list[int]] = {}
    for finding in repo["findings"].list():
        if finding.status != "closed" or finding.closed_at is None:
            continue
        days = (finding.closed_at.date() - finding.raised_at.date()).days
        by_severity.setdefault(_severity(finding), []).append(days)

    out: dict[str, Any] = {}
    for severity, days in sorted(by_severity.items()):
        out[severity] = {
            "closed": len(days),
            "mean_days": round(statistics.mean(days), 1),
            "median_days": round(statistics.median(days), 1),
            "slowest_days": max(days),
        }
    everything = [d for days in by_severity.values() for d in days]
    out["overall"] = {
        "closed": len(everything),
        "mean_days": round(statistics.mean(everything), 1) if everything else None,
        "median_days": (
            round(statistics.median(everything), 1) if everything else None
        ),
        "slowest_days": max(everything, default=None),
    }
    return out


def upcoming(repo, as_of: date, horizon_days: int = HORIZON_DAYS):
    """Audits and compliance activities falling due in the next 30 days."""
    until = as_of + timedelta(days=horizon_days)
    units = _units(repo)
    audits = [
        {
            "id": audit.id,
            "kind": audit.kind,
            "title": audit.title,
            "planned": audit.planned_date,
            "days_away": (audit.planned_date - as_of).days,
            "scope": [units.get(u, u) for u in audit.scope],
        }
        for audit in repo["audits"].list()
        if audit.status != "completed" and as_of <= audit.planned_date <= until
    ]
    controls = {c.id: c.title for c in repo["controls"].list()}
    activities = [
        {
            "id": instance.id,
            "control": controls.get(instance.control_id, instance.control_id),
            "unit": units.get(instance.auditable_unit_id, instance.auditable_unit_id),
            "period": instance.period,
            "due": instance.due_date,
            "days_away": (instance.due_date - as_of).days,
        }
        for instance in repo["instances"].list()
        if instance.status in ("pending", "submitted")
        and as_of <= instance.due_date <= until
    ]
    return {
        "audits": sorted(audits, key=lambda a: (a["planned"], a["id"])),
        "activities": sorted(activities, key=lambda a: (a["due"], a["id"]))[:50],
        "activity_total": len(activities),
        "horizon_days": horizon_days,
    }


def default_window(repo, as_of: date) -> tuple[date, date]:
    """From the month the first finding was raised to `as_of`.

    Read from state rather than assumed. The previous default was "January of
    the year before `as_of`", which happened to match the corpus and would have
    silently cut or padded the trend for any other vantage point.
    """
    findings = repo["findings"].list()
    if not findings:
        return (date(as_of.year, as_of.month, 1), as_of)
    first = min(f.raised_at.date() for f in findings)
    return (date(first.year, first.month, 1), as_of)


def portfolio(conn, as_of: date, *, window: tuple[date, date] | None = None):
    """Every figure section 8 asks for, in one call."""
    from .repositories import repositories

    repo = repositories(conn)
    start, end = window or default_window(repo, as_of)
    points = trend(repo, start, end)
    return {
        "as_of": as_of,
        "window": (start, end),
        "open_vs_closed": open_vs_closed(repo),
        "severity_mix": severity_mix(repo),
        "overdue_ageing": overdue_ageing(repo, as_of),
        "by_dimension": by_dimension(repo),
        "recurring": recurring(repo),
        "effort": effort_distribution(repo),
        "trend": points,
        "trend_verdict": trend_verdict(points),
        "closure": closure_performance(repo),
        "upcoming": upcoming(repo, as_of),
    }


def named_metrics(p: dict[str, Any]) -> dict[str, Any]:
    """Section 8's figures under stable names a brief can cite.

    The prioritisation brief may rest a claim on a finding or on a figure, and a
    figure is only checkable if it has a name that resolves to one value. This is
    that catalogue: every name here comes straight out of `portfolio`, nothing is
    recomputed, and a claim citing a name that is not in it is rejected.
    """
    ovc = p["open_vs_closed"]
    ageing = p["overdue_ageing"]
    buckets = ageing["buckets"]
    effort = p["effort"]
    recurring_block = p["recurring"]
    verdict = p["trend_verdict"]
    overall_closure = p["closure"]["overall"]
    mix = p["severity_mix"]["overall"]
    metrics: dict[str, Any] = {
        "open_findings": ovc["open"],
        "closed_findings": ovc["closed"],
        "closed_pct": ovc["closed_pct"],
        "overdue_total": ageing["total"],
        "overdue_0_30": buckets["0-30"],
        "overdue_31_60": buckets["31-60"],
        "overdue_61_90": buckets["61-90"],
        "overdue_90_plus": buckets["90+"],
        "oldest_overdue_days": ageing["oldest_days"],
        "severity_major": mix.get("Major", 0),
        "severity_minor": mix.get("Minor", 0),
        "severity_observation": mix.get("Observation", 0),
        "recurring_categories": recurring_block["by_gap_category"]["count"],
        "recurring_categories_audit_track": recurring_block["audit_track"]["count"],
        "recurrence_links": recurring_block["count"],
        "multi_round_findings": effort["multi_round"],
        "multi_reminder_findings": effort["multi_reminder"],
        "worst_rounds": effort["worst_rounds"],
        "trend_direction": verdict["direction"],
        "trend_slope_per_month": verdict.get("slope_per_month"),
        "trend_recent_direction": verdict.get("recent", {}).get("direction"),
        "closure_mean_days": overall_closure["mean_days"],
        "closure_median_days": overall_closure["median_days"],
        "upcoming_audits": len(p["upcoming"]["audits"]),
        "upcoming_activities": p["upcoming"]["activity_total"],
    }
    for unit, row in ovc["by_unit"].items():
        metrics[f"open_in_unit:{unit}"] = row["open"]
    for category, row in recurring_block["by_gap_category"]["categories"].items():
        metrics[f"recurring_category:{category}"] = row["findings"]
    return metrics
