"""
LoveAdvisor V3 - Output Builder Service
Phase 1: Engineering Skeleton Initialization

This service formats analysis results and applies presentation rules.
It transforms raw strategy data into user-friendly output formats.
"""

from typing import Dict, Any, List, Optional

from app.core.runtime_context import RuntimeContext
from app.core.enums import OutputFormat


class OutputBuilder:
    """
    Service for building and formatting analysis outputs.

    Responsibilities:
    1. Transform raw strategy data into structured output formats
    2. Apply presentation rules and templates
    3. Generate user-friendly summaries and action items
    4. Adapt output to requested format (structured, concise, actionable, debug)
    5. Ensure consistency and readability of final output
    """

    async def execute(self, context: RuntimeContext) -> Dict[str, Any]:
        """
        Build final output from pipeline results.

        Args:
            context: Runtime context containing all pipeline stage outputs.

        Returns:
            Dictionary containing formatted analysis results.
        """
        # TODO: Implement actual output building logic
        # This stub returns example output for skeleton purposes

        # Get outputs from previous stages
        preprocess_data = context.get_stage_output("preprocess") or {}
        signal_data = context.get_stage_output("signal_extraction") or {}
        strategy_data = context.get_stage_output("strategy_generation") or {}

        # Determine output format (default to structured)
        output_format = context.config_overrides.get("output_format", OutputFormat.STRUCTURED)

        # Build output based on requested format
        if output_format == OutputFormat.STRUCTURED:
            output = self._build_structured_output(preprocess_data, signal_data, strategy_data)
        elif output_format == OutputFormat.CONCISE:
            output = self._build_concise_output(preprocess_data, signal_data, strategy_data)
        elif output_format == OutputFormat.ACTIONABLE:
            output = self._build_actionable_output(preprocess_data, signal_data, strategy_data)
        elif output_format == OutputFormat.DEBUG:
            output = self._build_debug_output(context, preprocess_data, signal_data, strategy_data)
        else:
            output = self._build_structured_output(preprocess_data, signal_data, strategy_data)

        # Add metadata
        output["metadata"] = {
            "request_id": context.request_id,
            "pipeline_version": "v3",
            "output_format": output_format,
            "processing_time_ms": context.get_processing_time(),
            "timestamp": context.created_at.isoformat(),
        }

        return output

    def _build_structured_output(
        self,
        preprocess_data: Dict[str, Any],
        signal_data: Dict[str, Any],
        strategy_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Build detailed structured output.

        Args:
            preprocess_data: Preprocessing stage output.
            signal_data: Signal extraction stage output.
            strategy_data: Strategy generation stage output.

        Returns:
            Structured output dictionary.
        """
        return {
            "summary": {
                "main_issue": self._extract_main_issue(signal_data),
                "key_insight": self._extract_key_insight(strategy_data),
                "overall_recommendation": self._extract_overall_recommendation(strategy_data),
            },
            "signals": signal_data.get("emotional_signals", []) + signal_data.get("relational_signals", []),
            "strategies": strategy_data.get("primary_strategies", []),
            "action_plan": self._build_action_plan(strategy_data),
            "safety_notes": self._extract_safety_notes(strategy_data),
            "additional_resources": self._suggest_additional_resources(signal_data, strategy_data),
        }

    def _build_concise_output(
        self,
        preprocess_data: Dict[str, Any],
        signal_data: Dict[str, Any],
        strategy_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Build concise output for quick consumption.

        Args:
            preprocess_data: Preprocessing stage output.
            signal_data: Signal extraction stage output.
            strategy_data: Strategy generation stage output.

        Returns:
            Concise output dictionary.
        """
        return {
            "main_issue": self._extract_main_issue(signal_data),
            "key_advice": self._extract_key_advice(strategy_data),
            "first_step": self._extract_first_step(strategy_data),
            "urgency_level": self._assess_urgency(signal_data),
        }

    def _build_actionable_output(
        self,
        preprocess_data: Dict[str, Any],
        signal_data: Dict[str, Any],
        strategy_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Build actionable output with step-by-step instructions.

        Args:
            preprocess_data: Preprocessing stage output.
            signal_data: Signal extraction stage output.
            strategy_data: Strategy generation stage output.

        Returns:
            Actionable output dictionary.
        """
        return {
            "goal": self._define_goal(signal_data),
            "steps": self._build_step_by_step_plan(strategy_data),
            "timeline": self._suggest_timeline(strategy_data),
            "potential_challenges": self._identify_challenges(signal_data),
            "success_metrics": self._define_success_metrics(signal_data),
        }

    def _build_debug_output(
        self,
        context: RuntimeContext,
        preprocess_data: Dict[str, Any],
        signal_data: Dict[str, Any],
        strategy_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Build debug output with full pipeline details.

        Args:
            context: Runtime context.
            preprocess_data: Preprocessing stage output.
            signal_data: Signal extraction stage output.
            strategy_data: Strategy generation stage output.

        Returns:
            Debug output dictionary.
        """
        return {
            "context": context.to_dict(),
            "preprocess_output": preprocess_data,
            "signal_output": signal_data,
            "strategy_output": strategy_data,
            "pipeline_trace": list(context.stage_outputs.keys()),
        }

    # Helper methods (stubs for now)
    def _extract_main_issue(self, signal_data: Dict[str, Any]) -> str:
        """Extract main issue from signals."""
        # TODO: Implement
        return "沟通模式需要改善"

    def _extract_key_insight(self, strategy_data: Dict[str, Any]) -> str:
        """Extract key insight from strategies."""
        # TODO: Implement
        return "积极倾听可以显著减少误解"

    def _extract_overall_recommendation(self, strategy_data: Dict[str, Any]) -> str:
        """Extract overall recommendation."""
        # TODO: Implement
        return "专注于改善沟通质量，逐步建立信任"

    def _build_action_plan(self, strategy_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build action plan from strategies."""
        # TODO: Implement
        return []

    def _extract_safety_notes(self, strategy_data: Dict[str, Any]) -> List[str]:
        """Extract safety notes."""
        # TODO: Implement
        return []

    def _suggest_additional_resources(self, signal_data: Dict[str, Any], strategy_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest additional resources."""
        # TODO: Implement
        return []

    def _extract_key_advice(self, strategy_data: Dict[str, Any]) -> str:
        """Extract key advice."""
        # TODO: Implement
        return "尝试每天进行10分钟积极倾听练习"

    def _extract_first_step(self, strategy_data: Dict[str, Any]) -> str:
        """Extract first step."""
        # TODO: Implement
        return "今晚与伴侣进行一次不受干扰的对话"

    def _assess_urgency(self, signal_data: Dict[str, Any]) -> str:
        """Assess urgency level."""
        # TODO: Implement
        return "medium"

    def _define_goal(self, signal_data: Dict[str, Any]) -> str:
        """Define goal."""
        # TODO: Implement
        return "建立更健康的沟通模式"

    def _build_step_by_step_plan(self, strategy_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build step-by-step plan."""
        # TODO: Implement
        return []

    def _suggest_timeline(self, strategy_data: Dict[str, Any]) -> Dict[str, str]:
        """Suggest timeline."""
        # TODO: Implement
        return {"short_term": "2周", "medium_term": "1个月", "long_term": "3个月"}

    def _identify_challenges(self, signal_data: Dict[str, Any]) -> List[str]:
        """Identify potential challenges."""
        # TODO: Implement
        return []

    def _define_success_metrics(self, signal_data: Dict[str, Any]) -> List[str]:
        """Define success metrics."""
        # TODO: Implement
        return []


# ============================================================================
# Simplified output builder for Phase 6 API integration
# ============================================================================

def build_analysis_result(
    r1_result: Dict[str, Any],
    s5_result: Dict[str, Any],
    debug_info: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Build final analysis result from R1 and S5 outputs.

    This is a lightweight output builder that formats the final result
    for API responses. It does not contain business logic or complex formatting.

    Args:
        r1_result: R1 rule inference result (must contain relationship_stage, interest_level)
        s5_result: S5 strategy result after guardrail (must contain psychological_analysis,
                  risk_points, suggestions, next_step)
        debug_info: Optional debug information to include

    Returns:
        Dictionary with final analysis result structure:
        - relationship_stage (str)
        - interest_level (str)
        - psychological_analysis (str)
        - risk_points (List[str])
        - suggestions (List[str])
        - next_step (str)
        - debug (Optional[Dict[str, Any]]): if debug_info provided
    """
    result = {
        "relationship_stage": r1_result.get("relationship_stage", "无法判断"),
        "interest_level": r1_result.get("interest_level", "无法判断"),
        "psychological_analysis": s5_result.get("psychological_analysis", ""),
        "risk_points": s5_result.get("risk_points", []),
        "suggestions": s5_result.get("suggestions", []),
        "next_step": s5_result.get("next_step", ""),
    }

    # Add debug info if provided
    if debug_info is not None:
        result["debug"] = debug_info

    return result