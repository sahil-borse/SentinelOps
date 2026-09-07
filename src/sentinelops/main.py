"""Slice 1: one check instance walked end to end.

area -> control -> check instance -> evidence -> metered assessment -> finding
-> action, with an audit event appended at every transition. This is the
skeleton the five stages of section 4 will be hung off; none of those stages
exist yet, so the instance, the evidence and the assessment are wired directly.

The data and the console rendering live in `demo/`; this module is the path.
"""

from __future__ import annotations

import hashlib
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from .db import connect
from .demo import (
    DEMO_AREA, DEMO_CONTROL, DEMO_EVIDENCE_TEXT, DEMO_OWNER, print_run,
)
from .entities import (
    ASSESSOR_IDENTITY, CheckInstance, ControlDefinition, Evidence, Assessment, AuditableUnit, Finding,
)
from .llm import TokenMeter, get_client
from .llm.prompts import ASSESSMENT_SYSTEM_V1, assessment_schema_v1, assessment_user_v1
from .llm.protocol import LlmRequest
from .repositories import repositories

DEFAULT_DB = "sentinelops.db"


def run(
    db_path: str = DEFAULT_DB,
    area: AuditableUnit = DEMO_AREA,
    control: ControlDefinition = DEMO_CONTROL,
    evidence_text: str = DEMO_EVIDENCE_TEXT,
) -> dict[str, Any]:
    conn = connect(db_path)
    repo = repositories(conn)
    audit = repo["audit"]

    repo["units"].add(area)
    repo["controls"].add(control)

    # --- the check exists because the calendar says so, not because anyone
    # --- remembered it. In slice 4 this comes from S1; here it is hardcoded.
    instance = CheckInstance(
        id="CHK-0001",
        control_id=control.id,
        auditable_unit_id=area.id,
        period="2026-Q1",
        due_date=date(2026, 4, 15),
        status="pending",
        assigned_team=area.name,
        owner_name=DEMO_OWNER.name,
    )
    repo["instances"].add(instance)
    audit.append(
        actor="system",
        owner=instance.owner_name,
        action="check_instance_created",
        entity_type="CheckInstance",
        entity_id=instance.id,
        detail={"control": control.id, "period": instance.period},
    )

    # --- evidence arrives from the owning team
    evidence = Evidence(
        id="EV-0001",
        check_instance_id=instance.id,
        kind="document",
        doc_type="access_review_report",
        content=evidence_text,
        content_hash=hashlib.sha256(evidence_text.encode()).hexdigest(),
        submitted_at=datetime(2026, 4, 2, 9, 30),
        author=DEMO_OWNER.name,
        is_remediation=False,
    )
    repo["evidence"].add(evidence)
    instance.status = "submitted"
    repo["instances"].update(instance)
    audit.append(
        actor="user",
        owner=evidence.author,
        action="evidence_submitted",
        entity_type="Evidence",
        entity_id=evidence.id,
        detail={"doc_type": evidence.doc_type, "content_hash": evidence.content_hash[:12]},
    )

    # --- the one model call, metered. System prompt constant and first.
    request = LlmRequest(
        system=ASSESSMENT_SYSTEM_V1,
        messages=[
            {
                "role": "user",
                "content": assessment_user_v1(
                    control.title, control.criteria_text, [evidence.content]
                ),
            }
        ],
        max_tokens=600,
        response_schema=assessment_schema_v1(),
        tier="assess",
    )
    client = get_client()
    with TokenMeter(conn, tier="fake", label=f"S3:{instance.id}") as meter:
        response = meter.record(client.complete(request))
    assessed = response.parsed_json or {}

    finding = Assessment(
        id="ASM-0001",
        check_instance_id=instance.id,
        verdict=assessed["verdict"],
        confidence=assessed["confidence"],
        rationale=assessed["rationale"],
        cited_spans=assessed["cited_spans"],
        gaps=assessed["gaps"],
        recommended_action=assessed["recommended_action"],
        needs_human_review=assessed["needs_human_review"],
        assessed_at=datetime.now(),
        supersedes_assessment_id=None,
    )
    repo["assessments"].add(finding)
    instance.status = "assessed"
    repo["instances"].update(instance)
    audit.append(
        actor="ai",
        owner=instance.owner_name,
        action="assessment_recorded",
        entity_type="Assessment",
        entity_id=finding.id,
        detail={
            "verdict": finding.verdict,
            "model": response.model,
            "cost_usd": round(meter.cost, 6),
        },
    )

    # --- a failing assessment raises a Finding against the owning unit. It is
    # --- Open until an auditor closes it, and nothing else moves that.
    raised = Finding(
        id="FND-0001",
        source="activity_assessment",
        auditable_unit_id=area.id,
        description=finding.rationale,
        raised_by=ASSESSOR_IDENTITY,
        raised_at=datetime(2026, 4, 20, 9, 0),
        owner_identity=area.owner_identity,
        target_date=instance.due_date + timedelta(days=14),
        check_instance_id=instance.id,
        suggested_severity="Minor",
        severity="Minor",
        severity_assigned_by=ASSESSOR_IDENTITY,
        agreed_action_plan=finding.recommended_action or f"Remediate {control.title}",
        status="open",
    )
    repo["findings"].add(raised)
    audit.append(
        actor="ai",
        owner=instance.owner_name,
        action="finding_raised",
        entity_type="Finding",
        entity_id=raised.id,
        detail={
            "assessment_id": finding.id,
            "auditable_unit_id": raised.auditable_unit_id,
            "suggested_severity": raised.suggested_severity,
            "status": "open",
        },
        actor_identity=ASSESSOR_IDENTITY,
    )

    return {
        "assessment": repo["assessments"].get(finding.id),
        "finding": repo["findings"].get(raised.id),
        "audit_events": audit.read_all(),
        "token_usage": conn.execute("SELECT * FROM token_usage").fetchall(),
        "conn": conn,
    }


def main() -> None:
    # The skeleton demo owns its database outright, so re-running is idempotent.
    db = Path(DEFAULT_DB)
    db.unlink(missing_ok=True)
    result = run(str(db))
    print_run(result)
    result["conn"].close()


if __name__ == "__main__":
    main()
