"""S0 — applicability. Which controls apply to which process areas.

Zero tokens, permanently. This module imports nothing from `llm/` and never
will; `test_applicability.py` asserts both statically and by running the stage
with every provider rigged to explode.

The expression format, in one sentence:

    a control applies to an area when every attribute its `applies_when` names
    matches that area — a list means any one of those values will do, and an
    empty expression means the control applies everywhere.

That is the whole language. It is boolean, it is total, and it has no operator
precedence to explain:

    {}                                    -> every area
    {"handles_pii": True}                 -> areas that handle personal data
    {"criticality": ["high", "critical"]} -> areas at either of those levels
    {"handles_pii": True, "region": "EMEA"}  -> both must hold

Determinism is the point. The same area and the same control produce the same
answer every time, in every order, so a check cannot go missing because nobody
remembered it — and two areas with different attributes visibly receive
different control sets.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..entities import ControlDefinition, ProcessArea

#: Attributes a process area is allowed to carry. An `applies_when` naming
#: anything else is a bug, not an expression that matches nothing — see
#: `validate_expressions`.
KNOWN_ATTRIBUTES = frozenset(
    {"handles_pii", "customer_facing", "has_suppliers", "region", "criticality"}
)


@dataclass(frozen=True)
class Condition:
    """One attribute test, and how it went."""

    attribute: str
    expected: Any
    actual: Any
    matched: bool

    def describe(self) -> str:
        if isinstance(self.expected, list):
            wanted = " or ".join(str(v) for v in self.expected)
        else:
            wanted = str(self.expected)
        verdict = "matches" if self.matched else "does not match"
        return f"{self.attribute}={self.actual!r} {verdict} {wanted}"


@dataclass(frozen=True)
class Applicability:
    """The decision for one control against one area, with its reasoning."""

    control_id: str
    process_area_id: str
    applicable: bool
    conditions: list[Condition]

    def explain(self) -> str:
        if not self.conditions:
            return "applies to every area (no conditions)"
        if self.applicable:
            met = ", ".join(c.describe() for c in self.conditions)
            return f"applies because {met}"
        failed = ", ".join(c.describe() for c in self.conditions if not c.matched)
        return f"does not apply because {failed}"


def _matches(expected: Any, actual: Any) -> bool:
    """Any-of for a list, equality otherwise. No other operators exist."""
    if isinstance(expected, list):
        return actual in expected
    return actual == expected


def evaluate(control: ControlDefinition, area: ProcessArea) -> Applicability:
    """Decide one control against one area. Pure; no I/O, no clock, no model."""
    conditions = [
        Condition(
            attribute=attribute,
            expected=expected,
            actual=area.attributes.get(attribute),
            matched=_matches(expected, area.attributes.get(attribute)),
        )
        # sorted so the explanation reads the same way every time
        for attribute, expected in sorted(control.applies_when.items())
    ]
    return Applicability(
        control_id=control.id,
        process_area_id=area.id,
        applicable=all(c.matched for c in conditions),
        conditions=conditions,
    )


def applicable_controls(
    controls: list[ControlDefinition], area: ProcessArea
) -> list[ControlDefinition]:
    """The control set for one area, in a stable order.

    An area that matches nothing gets an empty list — that is a legitimate
    answer, not an error. It does mean somebody should look at the area's
    attributes, which is why the stage records the count either way.
    """
    return [c for c in sorted(controls, key=lambda c: c.id) if evaluate(c, area).applicable]


def applicability_matrix(
    controls: list[ControlDefinition], areas: list[ProcessArea]
) -> dict[str, list[str]]:
    """area_id -> sorted control ids. The whole of S0's output."""
    return {
        area.id: [c.id for c in applicable_controls(controls, area)]
        for area in sorted(areas, key=lambda a: a.id)
    }


def applicable_pairs(
    controls: list[ControlDefinition], areas: list[ProcessArea]
) -> list[tuple[str, str]]:
    """(control_id, area_id) for every applicable combination."""
    return [
        (control_id, area_id)
        for area_id, control_ids in applicability_matrix(controls, areas).items()
        for control_id in control_ids
    ]


def validate_expressions(controls: list[ControlDefinition]) -> list[str]:
    """Catch expressions that can never match anything.

    A misspelled attribute is the quiet failure this whole system exists to
    prevent: `applies_when={"handles_pii_data": True}` matches no area, so the
    control silently applies nowhere and every one of its checks goes missing
    without anybody being told. Loudly wrong beats silently absent.
    """
    problems = []
    for control in sorted(controls, key=lambda c: c.id):
        for attribute in sorted(control.applies_when):
            if attribute not in KNOWN_ATTRIBUTES:
                problems.append(
                    f"{control.id}: unknown attribute {attribute!r}"
                    f" (known: {', '.join(sorted(KNOWN_ATTRIBUTES))})"
                )
    return problems


def run(conn) -> dict[str, list[str]]:
    """Evaluate applicability across everything in the database.

    Appends one audit event per area recording the control set it received, so
    the trail can answer "why was this area ever expected to run that check?"
    long after the fact.
    """
    from ..repositories import repositories

    repo = repositories(conn)
    controls = repo["controls"].list()
    areas = repo["areas"].list()

    problems = validate_expressions(controls)
    if problems:
        raise ValueError("invalid applies_when expressions: " + "; ".join(problems))

    matrix = applicability_matrix(controls, areas)
    areas_by_id = {a.id: a for a in areas}
    for area_id, control_ids in matrix.items():
        repo["audit"].append(
            actor="system",
            owner=areas_by_id[area_id].owner_name,
            action="applicability_evaluated",
            entity_type="ProcessArea",
            entity_id=area_id,
            detail={
                "applicable_count": len(control_ids),
                "evaluated_count": len(controls),
                "applicable_controls": control_ids,
            },
        )
    return matrix
