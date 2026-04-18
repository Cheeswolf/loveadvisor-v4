"""
LoveAdvisor V3 - R1 Service
Phase 4: R1 Local Rule Engine Integration

This module provides a lightweight service layer for the R1 local rule engine.
It wraps the existing rule functions in app/rules/rules.py with minimal
safeguards and error handling.
"""

import logging
from typing import Dict, Any, Optional

from app.rules import rules
from app.schemas.result_models import R1Result

logger = logging.getLogger(__name__)


def infer_r1(s2: Optional[Dict[str, Any]], s3: Optional[Dict[str, Any]], debug: bool = False) -> Dict[str, Any]:
    """
    Infer relationship stage and interest level using local rule engine.

    This is the primary interface for R1 rule engine integration.
    It calls the rule functions with minimal safeguards and returns
    a stable dictionary with guaranteed fields.

    Args:
        s2: S2 signal extraction result (dict or None)
        s3: S3 signal summary result (dict or None)

    Returns:
        Dictionary with keys:
            - relationship_stage: 初识期 / 暧昧期 / 拉扯期 / 冷淡期 / 无法判断
            - interest_level: 低 / 中 / 高 / 无法判断
            - next_step_action: action code (e.g., "observe", "light_reply")

    Example:
        >>> s2 = {"initiative": "A更主动", "response_length": "短", ...}
        >>> s3 = {"has_intimacy_signal": False, ...}
        >>> result = infer_r1(s2, s3)
        >>> print(result["relationship_stage"], result["interest_level"])
    """
    try:
        # Call the appropriate rule engine based on debug flag
        if debug:
            result = rules.infer_r1_with_debug(s2, s3)
            # Ensure debug fields are present
            if "r1_debug_flags" not in result:
                result["r1_debug_flags"] = {}
            if "r1_stage_reason" not in result:
                result["r1_stage_reason"] = "未知原因"
            if "r1_interest_reason" not in result:
                result["r1_interest_reason"] = "未知原因"
        else:
            result = rules.infer_r1(s2, s3)

        # Ensure all required fields are present
        required_fields = ["relationship_stage", "interest_level", "next_step_action"]
        for field in required_fields:
            if field not in result:
                logger.warning(f"R1 result missing field '{field}', using default")
                result[field] = "无法判断" if field != "next_step_action" else "observe"

        return result

    except Exception as e:
        logger.error(f"R1 rule engine failed: {e}", exc_info=True)
        # Minimal fallback: return safe defaults
        return {
            "relationship_stage": "无法判断",
            "interest_level": "无法判断",
            "next_step_action": "observe",
        }


def infer_r1_as_model(s2: Optional[Dict[str, Any]], s3: Optional[Dict[str, Any]]) -> R1Result:
    """
    Infer relationship stage and interest level and return as Pydantic model.

    This is a convenience wrapper that returns a validated R1Result model.
    It uses the same rule engine as infer_r1 but converts the result to
    the structured model.

    Args:
        s2: S2 signal extraction result (dict or None)
        s3: S3 signal summary result (dict or None)

    Returns:
        R1Result model instance with relationship_stage and interest_level.
        Note: next_step_action is not included in the model.
    """
    result_dict = infer_r1(s2, s3, debug=False)
    # Extract only fields relevant to R1Result
    return R1Result(
        relationship_stage=result_dict["relationship_stage"],
        interest_level=result_dict["interest_level"],
    )


# Optional: Provide a synchronous version if needed (already synchronous)
# This module is designed to be imported and used directly.