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
