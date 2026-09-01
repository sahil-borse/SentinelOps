"""Console rendering of a slice-1 run. Print statements only, no logic.

This is a placeholder for the slice-9 dashboard, which renders the same five
record sets: the finding with its cited spans, the action with its owner, the
audit timeline, and the live token meter.
"""

from __future__ import annotations

from typing import Any


def _rule(title: str) -> None:
    print(f"\n{title}\n{'-' * len(title)}")


def print_run(result: dict[str, Any]) -> None:
    finding = result["finding"]
    action = result["action"]

    _rule("FINDING")
    print(f"  {finding.id}  verdict={finding.verdict}  "
          f"confidence={finding.confidence}  "
          f"needs_human_review={finding.needs_human_review}")
    print(f"  rationale     : {finding.rationale}")
    for span in finding.cited_spans:
        print(f"  cited span    : {span}")
    for gap in finding.gaps:
        print(f"  gap           : {gap}")
    print(f"  supersedes    : {finding.supersedes_finding_id}")

    _rule("ACTION")
    print(f"  {action.id}  status={action.status}  due {action.due_date}")
    print(f"  {action.title}")
    print(f"  assigned to   : {action.owner_team} / {action.owner_name}")
    print(f"  raised from   : {action.finding_id}")

    _rule("AUDIT TRAIL")
    for event in result["audit_events"]:
        print(
            f"  {event.ts:%Y-%m-%d %H:%M:%S}  {event.actor:<6}  {event.owner:<10}"
            f"  {event.action:<24} {event.entity_type}:{event.entity_id}"
        )
        print(f"  {'':>22}{'':>20}detail: {event.detail}")

    _rule("TOKEN USAGE")
    for row in result["token_usage"]:
        data = dict(row)
        print(
            f"  tier={data['tier']}  model={data['model']}  "
            f"input={data['input_tokens']}  output={data['output_tokens']}  "
            f"cached={data['cached_tokens']}"
        )
        print(
            f"  latency_ms={data['latency_ms']}  cost_usd={data['cost_usd']}  "
            f"label={data['label']}"
        )


def print_applicability_comparison(controls, area_a, area_b) -> None:
    """Two areas' control sets side by side — the S0 shot for the video.

    The point is the difference: same catalogue of controls, different
    attributes, visibly different obligations, decided by rules rather than by
    somebody remembering.
    """
    from ..stages.applicability import applicable_controls, evaluate

    sets = {
        area.id: {c.id for c in applicable_controls(controls, area)}
        for area in (area_a, area_b)
    }
    titles = {c.id: c.title for c in controls}
    width = max(len(c.id) for c in controls) + 2

    def _attrs(area):
        flags = [k for k in ("handles_pii", "customer_facing", "has_suppliers")
                 if area.attributes.get(k)]
        return f"{', '.join(flags) or 'no flags'}; {area.attributes['criticality']}"

    _rule(f"S0 APPLICABILITY — {area_a.name} vs {area_b.name}")
    print(f"  {'':<{width}} {area_a.name:<24} {area_b.name}")
    print(f"  {'':<{width}} {_attrs(area_a):<24} {_attrs(area_b)}")
    print()
    for control_id in sorted(titles):
        in_a = "applies" if control_id in sets[area_a.id] else "  -"
        in_b = "applies" if control_id in sets[area_b.id] else "  -"
        print(f"  {control_id:<{width}} {in_a:<24} {in_b}")

    count_a, count_b = len(sets[area_a.id]), len(sets[area_b.id])
    print()
    print(f"  {'TOTAL':<{width}} {count_a:<24} {count_b}")
    print(f"  difference: {abs(count_a - count_b)} controls"
          f" of {len(controls)} in the catalogue")

    only_b = sorted(sets[area_b.id] - sets[area_a.id])
    if only_b:
        print(f"\n  {area_b.name} additionally carries:")
        for control_id in only_b:
            reason = evaluate(
                next(c for c in controls if c.id == control_id), area_b
            ).explain()
            print(f"    {control_id:<{width}} {reason}")


def print_prescreen_breakdown(report) -> None:
    """Where the pre-screen resolved things, and what it cost — which is nothing.

    The bottom line is the one the video quotes: the share of the audit cycle
    that reached a verdict without a model ever being asked.
    """
    _rule(f"S2 PRE-SCREEN — exit rate by rule, as of {report.as_of}")
    print(f"  {'rule':<30} {'count':>6}  {'share':>7}")
    print(f"  {'-' * 30} {'-' * 6}  {'-' * 7}")
    for name, count, share in report.breakdown():
        marker = " " if name.startswith("to_assess") else "*"
        print(f"  {marker} {name:<28} {count:>6}  {share:>6.1%}")
    print(f"  {'-' * 30} {'-' * 6}  {'-' * 7}")
    print(f"  {'considered':<30} {report.considered:>6}")
    print(f"  {'* resolved with no model call':<30} {report.resolved:>6}"
          f"  {report.zero_model_share:>6.1%}")
    print(f"  {'  sent to S3':<30} {len(report.to_assess):>6}"
          f"  {1 - report.zero_model_share:>6.1%}")


def print_finding(finding, evidence=None) -> None:
    """One finding in full, with its citations shown against the source."""
    _rule(f"FINDING {finding.id}")
    print(f"  instance   {finding.check_instance_id}")
    print(f"  verdict    {finding.verdict}   confidence {finding.confidence}"
          f"   decided_by {finding.decided_by}")
    print(f"  review?    {finding.needs_human_review}")
    print(f"  rationale  {finding.rationale}")
    for span in finding.cited_spans:
        print(f"  cites      {span}")
    for gap in finding.gaps:
        print(f"  gap        {gap}")
    if finding.recommended_action:
        print(f"  action     {finding.recommended_action}")
    if finding.carried_forward_from:
        print(f"  carried    forward from {finding.carried_forward_from}")
    if evidence is not None:
        print(f"\n  source evidence {evidence.id} ({evidence.doc_type}):")
        for line in evidence.content.splitlines():
            hit = any(span in line for span in finding.cited_spans)
            print(f"    {'>>' if hit else '  '} {line}")


def print_lifecycle(conn, check_instance_id: str) -> None:
    """One check's whole story, in the order it happened.

    Reads only the audit trail plus the records it points at — which is the
    claim worth making on camera: the timeline is not assembled by a reporting
    job, it is what the system wrote down as it went.
    """
    from ..repositories import repositories

    repo = repositories(conn)
    instance = repo["instances"].get(check_instance_id)
    findings = sorted(
        repo["findings"].list(check_instance_id=check_instance_id), key=lambda f: f.id
    )
    actions = [
        a for a in repo["actions"].list()
        if a.id == f"ACT-{check_instance_id.removeprefix('CHK-')}"
    ]

    _rule(f"LIFECYCLE — {check_instance_id}")
    print(f"  {instance.control_id} / {instance.process_area_id} / {instance.period}")
    print(f"  due {instance.due_date}   owner {instance.assigned_team}"
          f" / {instance.owner_name}   status {instance.status}")

    events = list(repo["audit"].read_for("CheckInstance", check_instance_id))
    for finding in findings:
        events += repo["audit"].read_for("Finding", finding.id)
    for action in actions:
        events += repo["audit"].read_for("Action", action.id)
    for flag in repo["flags"].list(check_instance_id=check_instance_id):
        events += repo["audit"].read_for("Flag", flag.id)
    for evidence in repo["evidence"].list(check_instance_id=check_instance_id):
        events += repo["audit"].read_for("Evidence", evidence.id)

    print()
    print(f"  {'#':>3}  {'actor':<6} {'owner':<22} {'event':<28} detail")
    print(f"  {'-' * 3}  {'-' * 6} {'-' * 22} {'-' * 28} {'-' * 40}")
    for number, event in enumerate(sorted(events, key=lambda e: e.id), start=1):
        print(f"  {number:>3}  {event.actor:<6} {event.owner:<22}"
              f" {event.action:<28} {_summarise(event)}")

    print()
    for finding in findings:
        marker = "superseded by " + (
            next((f.id for f in findings if f.supersedes_finding_id == finding.id), "-")
        ) if any(f.supersedes_finding_id == finding.id for f in findings) else "current"
        print(f"  {finding.id:<44} {finding.verdict:<22} {marker}")
    for action in actions:
        print(f"  {action.id:<44} {action.status:<22} due {action.due_date}")
        if action.resolution_note:
            print(f"      resolution: {action.resolution_note}")


def _summarise(event) -> str:
    d = event.detail
    for key in ("subject", "rationale", "resolution_note", "verdict", "category",
                "superseded_by", "to_status", "evidence_id", "due_date"):
        if key in d:
            value = str(d[key])
            return value if len(value) <= 60 else value[:57] + "..."
    return ", ".join(f"{k}={v}" for k, v in list(d.items())[:2])[:60]
