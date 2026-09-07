"""Prompt templates as versioned functions, never inline f-strings."""

from .assessment import ASSESSMENT_SYSTEM_V1, assessment_user_v1, assessment_schema_v1
from .audit_report import (
    AUDIT_REPORT_SYSTEM_V1, audit_report_schema_v1, audit_report_user_v1,
)

__all__ = [
    "ASSESSMENT_SYSTEM_V1", "assessment_user_v1", "assessment_schema_v1",
    "AUDIT_REPORT_SYSTEM_V1", "audit_report_user_v1", "audit_report_schema_v1",
]
