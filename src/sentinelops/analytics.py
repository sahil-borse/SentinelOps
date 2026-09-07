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


def _units(repo) -> dict[str, str]:
    return {u.id: u.name for u in repo["units"].list()}


def _severity(finding) -> str:
    return finding.severity or finding.suggested_severity or "unassigned"


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
        row["closed_pct"] = round(100 * row["closed"] / total, 1) if total else 0.0

    total = len(findings)
    closed = len([f for f in findings if f.status == "closed"])
    return {
        "total": total,
        "open": total - closed,
        "closed": closed,
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
        "findings": detail,
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
    return {
        "by_unit": dict(sorted(unit_counts.items(), key=lambda kv: -kv[1])),
        "by_category": dict(sorted(category_counts.items(), key=lambda kv: -kv[1])),
        "by_audit_kind": dict(sorted(kind_counts.items(), key=lambda kv: -kv[1])),
    }


def recurring(repo) -> dict[str, Any]:
    """Same gap category in a different unit, project or period.

    A recurrence is a **link** — this finding resembles that earlier one — and
    this reports links, plus a per-category rollup and the notable chains.

    An earlier version merged links transitively into sets, so A→B and B→C
    became one group of three, and on a corpus where a category fails across ten
    units it collapsed into a single "set" of forty-five findings. That is not a
    finding anyone can act on; it is the union-find algorithm reporting that the
    graph is connected. The rollup below says the useful version of the same
    thing — *this category recurred forty-five times across ten units* — without
    pretending it is one incident.

    Chains are still worth showing where they are short: a problem that came
    back twice in different places is a story, and `longest_chains` keeps the
    few that read as one.
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
                "months_apart": max(
                    (finding.raised_at - prior.raised_at).days // 30, 0
                ),
            })
    links.sort(key=lambda link: (-link["months_apart"], link["finding"]))

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
            by_category.items(), key=lambda kv: -kv[1]["links"]
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

    return {
        "links": links,
        "count": len(links),
        "spanning_units": len([link for link in links if link["spans_units"]]),
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
    }


def trend(repo, start: date, end: date) -> list[dict[str, Any]]:
    """Open finding count by month across the corpus window.

    Computed by replaying raise and close dates rather than by sampling state,
    so the line is what was actually true at each month end rather than what is
    true now projected backwards.
    """
    findings = repo["findings"].list()
    months: list[date] = []
    cursor = date(start.year, start.month, 1)
    while cursor <= end:
        months.append(cursor)
        cursor = date(
            cursor.year + (cursor.month == 12),
            1 if cursor.month == 12 else cursor.month + 1,
            1,
        )

    out = []
    for month in months:
        following = date(
            month.year + (month.month == 12),
            1 if month.month == 12 else month.month + 1,
            1,
        )
        month_end = following - timedelta(days=1)
        raised = [f for f in findings if f.raised_at.date() <= month_end]
        closed = [
            f for f in raised
            if f.closed_at is not None and f.closed_at.date() <= month_end
        ]
        out.append({
            "month": f"{month.year}-{month.month:02d}",
            "raised_to_date": len(raised),
            "closed_to_date": len(closed),
            "open": len(raised) - len(closed),
        })
    return out


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
        "audits": sorted(audits, key=lambda a: a["planned"]),
        "activities": sorted(activities, key=lambda a: (a["due"], a["id"]))[:50],
        "activity_total": len(activities),
        "horizon_days": horizon_days,
    }


def portfolio(conn, as_of: date, *, window: tuple[date, date] | None = None):
    """Every figure section 8 asks for, in one call."""
    from .repositories import repositories

    repo = repositories(conn)
    start, end = window or (date(as_of.year - 1, 1, 1), as_of)
    return {
        "as_of": as_of,
        "open_vs_closed": open_vs_closed(repo),
        "severity_mix": severity_mix(repo),
        "overdue_ageing": overdue_ageing(repo, as_of),
        "by_dimension": by_dimension(repo),
        "recurring": recurring(repo),
        "effort": effort_distribution(repo),
        "trend": trend(repo, start, end),
        "closure": closure_performance(repo),
        "upcoming": upcoming(repo, as_of),
    }
