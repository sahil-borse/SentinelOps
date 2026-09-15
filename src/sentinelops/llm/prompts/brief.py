"""Use 5 of section 2: one prioritisation brief per cycle.

**Why a model.** Everything the brief is built from is already computed: the
ranking by `sentinelops.priority`, and section 8's figures by
`sentinelops.analytics`. What a person adds when they read that is synthesis —
noticing that four of the five most urgent sit in one unit, that one category
keeps coming back, that the trend has turned. That is the part worth a model
call, and it is a different job from the other four uses, all of which read one
document.

**One call per cycle, over the ranked list and the metrics.** Section 9 says so
in as many words, and it is the single most important cost rule here: the brief
scales with cycles, not with findings.

**Strict JSON, and every claim cites.** Version 1 returned a paragraph of prose
and a list of ids, and a sentence stating a figure could go uncited. Version 2
returns three sections of structured claims, each carrying the finding ids and
named metrics it rests on, validated against the ranked list and the metric
catalogue the call was given. One claim that does not check out withholds the
whole brief.

**Advisory; changes no state.** Nothing in the pipeline reads a brief back.
"""

from __future__ import annotations

from typing import Any

#: Travels onto the brief.
PROMPT_VERSION = "brief_v2"

#: Three short sections for somebody with fifteen minutes. A ceiling on the
#: generation is cost discipline that costs nothing.
MAX_TOKENS = 900

#: How many ranked findings go into the call. The tail of a long queue adds
#: tokens and nothing else.
TOP_N = 12

#: A top priority's reason is one line, not a paragraph.
REASON_MAX = 160

BRIEF_SYSTEM_V2 = (
    "You write a short prioritisation brief for a compliance team. You are given "
    "a METRICS catalogue of named portfolio figures, and a list of open findings "
    "already RANKED by a deterministic priority score. The ranking is not yours "
    "to change.\n"
    "\n"
    "Return three sections.\n"
    "\n"
    "1. top_priorities: the 3 to 5 findings from the ranked list that most need "
    "attention this cycle. For each, give its finding_id and a reason of one "
    f"line, at most {REASON_MAX} characters, saying in plain words why it is "
    "urgent — severity, how long past target, how often chased, whether it "
    "keeps recurring. Do not just repeat the score arithmetic.\n"
    "\n"
    "2. emerging_patterns: up to 3 patterns across the portfolio, such as a "
    "unit carrying disproportionate weight, a gap category recurring across "
    "units, or the trend turning. Omit the section's entries if there is no "
    "real pattern; do not manufacture one.\n"
    "\n"
    "3. recommended_focus: 1 to 3 statements of where the team's attention "
    "would go furthest this cycle.\n"
    "\n"
    "CITATIONS. Every entry in emerging_patterns and recommended_focus carries "
    "finding_ids and metrics: the ids of findings it rests on, and the names of "
    "metrics it rests on, copied exactly from the METRICS catalogue. At least "
    "one of the two must be non-empty. A statement may mention a finding id in "
    "square brackets, like [FND-3], only if that id is also in its finding_ids. "
    "Never cite an id that is not in the ranked list or a metric that is not in "
    "the catalogue. An uncited or unresolvable claim causes the whole brief to "
    "be rejected.\n"
    "\n"
    "LIMITS. This brief is advisory. Do not assign or revise severities, set or "
    "move dates, change owners, or rewrite agreed action plans. If the portfolio "
    "is genuinely quiet, say so briefly rather than inflating it.\n"
    "\n"
    "Return JSON only, matching the schema you are given."
)


def _claim_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["statement", "finding_ids", "metrics"],
        "properties": {
            "statement": {"type": "string", "maxLength": 300},
            "finding_ids": {"type": "array", "items": {"type": "string"}},
            "metrics": {"type": "array", "items": {"type": "string"}},
        },
    }


def brief_schema_v2() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["top_priorities", "emerging_patterns", "recommended_focus"],
        "properties": {
            "top_priorities": {
                "type": "array",
                "maxItems": 5,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["finding_id", "reason"],
                    "properties": {
                        "finding_id": {"type": "string"},
                        "reason": {"type": "string", "maxLength": REASON_MAX},
                    },
                },
            },
            "emerging_patterns": {
                "type": "array", "maxItems": 3, "items": _claim_schema(),
            },
            "recommended_focus": {
                "type": "array", "maxItems": 3, "items": _claim_schema(),
            },
        },
    }


def _row_line(row: dict[str, Any]) -> str:
    return (
        f"- {row['id']} | rank {row['rank']} | score {row['score']:g} | "
        f"{row['unit']} | {row['criticality']} | {row['severity']} | "
        f"{row['category']} | {row['timing_label']} | "
        f"{row['recurrence_links']} recurrence link(s) | chased {row['follow_ups']}x"
        f"\n  why the score: {row['explain']}"
        f"\n  {row['description']}"
    )


def brief_user_v2(
    as_of: str,
    metrics: dict[str, Any],
    ranked: list[dict[str, Any]],
    *,
    total_open: int,
) -> str:
    """The catalogue, then the ranked list. Facts only; nothing to echo back."""
    lines = [
        "PORTFOLIO",
        f"as of: {as_of}",
        "",
        "METRICS (cite by name, exactly as written)",
    ]
    lines += [f"{name} = {value}" for name, value in sorted(metrics.items())]
    lines += [
        "",
        f"RANKED OPEN FINDINGS (deterministic priority score; top {len(ranked)} "
        f"of {total_open})",
    ]
    lines += [_row_line(row) for row in ranked] or ["(none open)"]
    return "\n".join(lines) + "\n"
