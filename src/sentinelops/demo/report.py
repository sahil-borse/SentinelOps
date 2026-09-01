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
