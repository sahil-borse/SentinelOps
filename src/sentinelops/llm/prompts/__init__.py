"""Prompt templates as versioned functions, never inline f-strings."""

from .assessment import ASSESSMENT_SYSTEM_V1, assessment_user_v1, assessment_schema_v1

__all__ = ["ASSESSMENT_SYSTEM_V1", "assessment_user_v1", "assessment_schema_v1"]
