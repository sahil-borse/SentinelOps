"""Section 6 — the narrative summary of an audit report, and only that.

The report itself is structured data the system already holds: kind, scope,
auditor, dates, and every finding with its description, category, severity,
owner, agreed action plan and target date. None of that needs a model, and none
of it goes through one — rendering is deterministic in `audit_report.py`.

What the model writes is the paragraph a human writes today: three or four
sentences saying what this audit found and where the weight of it sits. One call
per audit, over structured input, and **every statement must cite finding ids**.
That constraint is not stylistic. It is what makes the summary checkable: a
sentence with no ids attached is a sentence nobody can trace back, and this
module rejects the response rather than publishing it.

The auditor reviews and confirms before it is issued. The model drafts; it does
not sign.
"""

from __future__ import annotations

from typing import Any

#: Travels onto the audit report it produces.
PROMPT_VERSION = "audit_report_v1"

AUDIT_REPORT_SYSTEM_V1 = (
    "You draft the summary paragraph of an internal audit report. You are given "
    "structured facts about one audit and the findings raised by it. Write only "
    "what those facts support.\n"
    "\n"
    "RULES.\n"
    "1. Every sentence that makes a claim about what was found must cite the "
    "finding ids it rests on, in square brackets, like [FND-12] or "
    "[FND-12, FND-19]. A sentence with no citation is only permitted if it "
    "states a count or a date given to you in the facts.\n"
    "2. Never introduce a finding id that does not appear in the facts.\n"
    "3. Do not recommend, instruct, or assign. The agreed action plans are "
    "already recorded against each finding and are not yours to restate or "
    "improve.\n"
    "4. Do not assign or revise severities. They were set by the auditor.\n"
    "5. Three to five sentences. Plain professional English, no headings, no "
    "bullet points, no closing pleasantries.\n"
    "6. If the findings show a pattern — the same gap category across several "
    "units, or a unit carrying most of the weight — say so and cite it. That "
    "is the one thing a reader cannot see from the table underneath.\n"
    "\n"
    "Return JSON only, matching the schema you are given."
)


def audit_report_schema_v1() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["summary", "cited_finding_ids"],
        "properties": {
            "summary": {"type": "string", "maxLength": 1200},
            "cited_finding_ids": {
                "type": "array",
                "items": {"type": "string"},
                "maxItems": 40,
            },
        },
    }


def _finding_line(finding: dict[str, Any]) -> str:
    return (
        f"- {finding['id']} | unit: {finding['unit']} | "
        f"severity: {finding['severity']} | category: {finding['category']} | "
        f"owner: {finding['owner']} | target: {finding['target_date']}\n"
        f"  description: {finding['description']}"
        + (
            f"\n  recurrence of: {', '.join(finding['recurrence_of'])}"
            if finding.get("recurrence_of") else ""
        )
    )


def audit_report_user_v1(audit: dict[str, Any], findings: list[dict[str, Any]]) -> str:
    """The facts, and nothing else. No prose for the model to echo back."""
    scope = ", ".join(audit["scope"]) or "no units recorded"
    header = (
        f"AUDIT\n"
        f"id: {audit['id']}\n"
        f"kind: {audit['kind']}\n"
        f"title: {audit['title']}\n"
        f"auditor: {audit['auditor']}\n"
        f"planned: {audit['planned_date']}\n"
        f"conducted: {audit['conducted_date']}\n"
        f"scope: {scope}\n"
        f"findings raised: {len(findings)}\n"
    )
    if not findings:
        return header + "\nFINDINGS\n(none)\n"
    body = "\n".join(_finding_line(f) for f in findings)
    return f"{header}\nFINDINGS\n{body}\n"
