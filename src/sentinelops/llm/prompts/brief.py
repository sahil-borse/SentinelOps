"""Use 5 of section 2: one prioritisation brief per cycle.

**Why a model.** Everything the brief is built from is already computed — the
ranking, the ageing buckets, the severity mix, the follow-up counts. What a
person adds when they read that table is synthesis: noticing that four of the
five oldest sit in one unit, that the Majors are all the same category, that the
thing which escalated twice is not the thing which is oldest. That is the part
worth a model call, and it is a genuinely different job from any of the other
four uses, all of which read one document.

**One call per cycle, over ranked findings and metrics.** Section 9 says this in
as many words, and it is the single most important cost rule in the system: the
brief scales with cycles, not with findings, so a portfolio three times the size
costs exactly the same to summarise.

**Advisory; changes no state.** Section 2's own words. The brief is written to a
file and shown on screen. Nothing in the pipeline reads it back, and no finding's
status, severity or owner moves because of it — which is why it is safe for it to
be the one output here that is pure prose.

Every claim still has to cite finding ids, for the same reason the audit report
does: a sentence nobody can trace is a sentence nobody can check.
"""

from __future__ import annotations

from typing import Any

#: Travels onto the brief.
PROMPT_VERSION = "brief_v1"

#: The brief is a short read for somebody with fifteen minutes. A ceiling on the
#: generation is cost discipline that costs nothing, because nobody wanted the
#: extra paragraphs anyway.
MAX_TOKENS = 700

#: How many ranked findings go into the call. The tail of a long queue adds
#: tokens and nothing else — a brief about the fortieth most urgent item is not
#: a brief.
TOP_N = 15

BRIEF_SYSTEM_V1 = (
    "You write a short prioritisation brief for a compliance team, from the "
    "portfolio facts you are given.\n"
    "\n"
    "Say what deserves attention this cycle and why. Three short paragraphs at "
    "most, in this order:\n"
    "1. What is most urgent now, and what makes it urgent — age, severity, how "
    "many times it has been chased, or all three.\n"
    "2. Any pattern across the portfolio: a unit carrying disproportionate "
    "weight, a category recurring across units, findings that keep coming back "
    "for more evidence.\n"
    "3. What is going well, if anything is, in one sentence. Do not manufacture "
    "good news; omit the paragraph if there is none.\n"
    "\n"
    "RULES.\n"
    "- Every claim about a specific finding cites its id in square brackets, "
    "like [FND-3] or [FND-3, FND-9]. Sentences that only state a count or a "
    "figure you were given need no citation.\n"
    "- Never introduce an id that is not in the facts.\n"
    "- Do not assign severities, set dates, or tell anyone what to do. The "
    "action plans are agreed with the owners and are not yours to revise.\n"
    "- No headings, no bullet points, no salutation, no sign-off.\n"
    "- If the portfolio is genuinely quiet, say so briefly rather than "
    "inflating it. A brief that finds a crisis every cycle stops being read.\n"
    "\n"
    "Return JSON only, matching the schema you are given."
)


def brief_schema_v1() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["brief", "cited_finding_ids"],
        "properties": {
            "brief": {"type": "string", "maxLength": 2400},
            "cited_finding_ids": {
                "type": "array",
                "items": {"type": "string"},
                "maxItems": 40,
            },
        },
    }


def _finding_line(row: dict[str, Any]) -> str:
    return (
        f"- {row['id']} | {row['unit']} | {row['severity']} | "
        f"{row['category']} | {row['days_open']}d open | "
        f"{row['days_overdue']}d past target | chased {row['follow_ups']}x"
        + (f" | escalated L{row['escalation']}" if row.get("escalation") else "")
        + (f" | recurs from {', '.join(row['recurrence_of'])}"
           if row.get("recurrence_of") else "")
        + f"\n  {row['description']}"
    )


def brief_user_v1(
    as_of: str, metrics: dict[str, Any], ranked: list[dict[str, Any]]
) -> str:
    lines = [
        "PORTFOLIO",
        f"as of: {as_of}",
        f"open findings: {metrics.get('open', 0)}",
        f"closed to date: {metrics.get('closed', 0)}",
        f"severity mix (open): {metrics.get('severity_mix', {})}",
        f"ageing buckets (open): {metrics.get('ageing', {})}",
        f"overdue: {metrics.get('overdue', 0)}",
        f"escalated: {metrics.get('escalated', 0)}",
        f"by unit (open): {metrics.get('by_unit', {})}",
        f"by category (open): {metrics.get('by_category', {})}",
        f"needing more than one evidence round: {metrics.get('multi_round', 0)}",
        "",
        f"MOST URGENT (ranked, {len(ranked)} of {metrics.get('open', 0)})",
    ]
    lines += [_finding_line(row) for row in ranked] or ["(none open)"]
    return "\n".join(lines) + "\n"
