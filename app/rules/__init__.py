"""
LoveAdvisor V3 - Rules Package
Phase 1: Engineering Skeleton Initialization

This package contains business rules for signal validation, guardrails, and decision logic.
Rules ensure safety, consistency, and quality in the analysis pipeline.

TODO: Import concrete rule implementations as they are developed.
"""

from app.rules.base_rules import BaseRule, RuleEvaluationResult

__all__ = [
    "BaseRule",
    "RuleEvaluationResult",
]