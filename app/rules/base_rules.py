"""
LoveAdvisor V3 - Base Rules
Phase 1: Engineering Skeleton Initialization

This module defines the base interface for business rules.
All rules should follow this structure for consistency.

TODO: Implement concrete rules for signal validation, guardrails, and decision logic.
"""

from typing import Dict, Any, Optional
from abc import ABC, abstractmethod


class RuleEvaluationResult:
    """
    Result of evaluating a rule.

    Attributes:
        passed: Whether the rule passed.
        message: Descriptive message about the evaluation.
        details: Additional details about the evaluation.
        severity: Severity level if rule failed (info, warning, error, critical).
    """

    def __init__(self, passed: bool, message: str = "", details: Optional[Dict[str, Any]] = None, severity: str = "info"):
        self.passed = passed
        self.message = message
        self.details = details or {}
        self.severity = severity


class BaseRule(ABC):
    """
    Abstract base class for all business rules.

    This class defines the interface that all rules must implement.
    It ensures consistent rule evaluation and reporting.
    """

    def __init__(self, name: str, description: str = ""):
        """
        Initialize a rule.

        Args:
            name: Unique name identifying the rule.
            description: Human-readable description of the rule.
        """
        self.name = name
        self.description = description

    @abstractmethod
    async def evaluate(self, context: Dict[str, Any]) -> RuleEvaluationResult:
        """
        Evaluate the rule against the given context.

        Args:
            context: Context data for rule evaluation.

        Returns:
            Rule evaluation result.

        TODO: Implement rule-specific evaluation logic.
        """
        pass

    def get_metadata(self) -> Dict[str, str]:
        """
        Get metadata about this rule.

        Returns:
            Dictionary with rule metadata.
        """
        return {
            "name": self.name,
            "description": self.description,
            "type": self.__class__.__name__
        }