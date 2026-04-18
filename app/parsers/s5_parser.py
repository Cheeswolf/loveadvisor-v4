"""
LoveAdvisor V3 - S5 Response Parser
Phase 5: S5 + Guardrail Integration

This module parses and validates S5 (strategy generation) LLM responses.
It extracts structured strategy data from LLM JSON outputs.

Features:
- Parse raw LLM response string or dictionary
- Extract JSON from text using regex fallback
- Provide default values for missing fields
- Ensure risk_points and suggestions are always lists
- Ensure psychological_analysis and next_step are always strings
- Return stable dict structure
- Remove prohibited fields (relationship_stage, interest_level)
"""

import json
import re
from typing import Dict, Any, Union, List
import logging

from app.utils.json_utils import extract_json_from_text

logger = logging.getLogger(__name__)

# Required fields for S5 output
REQUIRED_FIELDS = {
    "psychological_analysis",
    "risk_points",
    "suggestions",
    "next_step"
}

# Prohibited fields (must be removed)
PROHIBITED_FIELDS = {
    "relationship_stage",
    "interest_level"
}

# Default values for each field
DEFAULT_PSYCHOLOGICAL_ANALYSIS = "基于当前信号分析，用户处于需要谨慎观察的状态。建议保持适度互动，避免过度解读。"
DEFAULT_RISK_POINTS = ["信号有限，难以准确判断对方真实意图"]
DEFAULT_SUGGESTIONS = ["保持轻度互动，观察对方回应模式", "避免过早暴露过多情感需求"]
DEFAULT_NEXT_STEP = "继续观察互动模式，保持适度频率的轻度交流。"


def parse_s5_response(llm_response: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Parse S5 LLM response into structured strategy data.

    Args:
        llm_response: Raw LLM response text or parsed dictionary.

    Returns:
        Parsed strategy data dictionary with guaranteed structure.

    Notes:
        - If input is a dict, it's used directly (with validation)
        - If input is a string, JSON is extracted using regex fallback
        - Missing fields are filled with defaults
        - risk_points and suggestions are always converted to list
        - psychological_analysis and next_step are always strings
        - Prohibited fields (relationship_stage, interest_level) are removed
    """
    parsed_dict = _extract_json_from_response(llm_response)
    normalized = _normalize_s5_data(parsed_dict)
    validated = _validate_and_fix_s5_data(normalized)
    return validated


def validate_s5_strategies(parsed_data: Dict[str, Any]) -> bool:
    """
    Validate parsed S5 strategy data.

    Args:
        parsed_data: Parsed strategy data dictionary.

    Returns:
        True if data passes validation, False otherwise.
    """
    # Check required fields exist
    for field in REQUIRED_FIELDS:
        if field not in parsed_data:
            logger.warning(f"S5 validation: missing field {field}")
            return False

    # Check types
    if not isinstance(parsed_data["psychological_analysis"], str):
        logger.warning("S5 validation: psychological_analysis is not a string")
        return False

    if not isinstance(parsed_data["risk_points"], list):
        logger.warning("S5 validation: risk_points is not a list")
        return False

    if not isinstance(parsed_data["suggestions"], list):
        logger.warning("S5 validation: suggestions is not a list")
        return False

    if not isinstance(parsed_data["next_step"], str):
        logger.warning("S5 validation: next_step is not a string")
        return False

    # Check prohibited fields are not present
    for field in PROHIBITED_FIELDS:
        if field in parsed_data:
            logger.warning(f"S5 validation: prohibited field {field} found")
            return False

    return True


# Helper functions
def _extract_json_from_response(llm_response: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Extract JSON dictionary from LLM response (string or dict)."""
    if isinstance(llm_response, dict):
        return llm_response.copy()

    if not isinstance(llm_response, str):
        logger.error(f"Unexpected response type: {type(llm_response)}")
        return {}

    # Try to extract JSON using utility function
    extracted = extract_json_from_text(llm_response)
    if extracted is not None:
        return extracted

    # Fallback: try to find JSON block with regex
    json_match = re.search(r'```json\s*(.*?)\s*```', llm_response, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass

    # Fallback: try to parse entire text as JSON
    try:
        return json.loads(llm_response)
    except json.JSONDecodeError:
        logger.warning("Failed to extract JSON from LLM response")
        return {}


def _normalize_s5_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize data types and structure."""
    normalized = data.copy()

    # Ensure risk_points is a list
    if "risk_points" in normalized:
        if isinstance(normalized["risk_points"], str):
            # Try to parse as JSON array, otherwise wrap as single element list
            try:
                parsed = json.loads(normalized["risk_points"])
                if isinstance(parsed, list):
                    normalized["risk_points"] = parsed
                else:
                    normalized["risk_points"] = [str(parsed)]
            except (json.JSONDecodeError, TypeError):
                normalized["risk_points"] = [normalized["risk_points"]]
        elif not isinstance(normalized["risk_points"], list):
            normalized["risk_points"] = []
    else:
        normalized["risk_points"] = []

    # Ensure suggestions is a list
    if "suggestions" in normalized:
        if isinstance(normalized["suggestions"], str):
            # Try to parse as JSON array, otherwise wrap as single element list
            try:
                parsed = json.loads(normalized["suggestions"])
                if isinstance(parsed, list):
                    normalized["suggestions"] = parsed
                else:
                    normalized["suggestions"] = [str(parsed)]
            except (json.JSONDecodeError, TypeError):
                normalized["suggestions"] = [normalized["suggestions"]]
        elif not isinstance(normalized["suggestions"], list):
            normalized["suggestions"] = []
    else:
        normalized["suggestions"] = []

    # Ensure psychological_analysis is a string
    if "psychological_analysis" in normalized:
        if not isinstance(normalized["psychological_analysis"], str):
            normalized["psychological_analysis"] = str(normalized["psychological_analysis"])
    else:
        normalized["psychological_analysis"] = ""

    # Ensure next_step is a string
    if "next_step" in normalized:
        if not isinstance(normalized["next_step"], str):
            normalized["next_step"] = str(normalized["next_step"])
    else:
        normalized["next_step"] = ""

    # Convert all risk_points and suggestions elements to strings
    normalized["risk_points"] = [str(item) for item in normalized["risk_points"]]
    normalized["suggestions"] = [str(item) for item in normalized["suggestions"]]

    return normalized


def _validate_and_fix_s5_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Apply validation rules and fix invalid values."""
    result = {}

    # Process psychological_analysis
    psychological_analysis = data.get("psychological_analysis", DEFAULT_PSYCHOLOGICAL_ANALYSIS)
    if not psychological_analysis or not isinstance(psychological_analysis, str):
        psychological_analysis = DEFAULT_PSYCHOLOGICAL_ANALYSIS
    result["psychological_analysis"] = psychological_analysis.strip()

    # Process risk_points
    risk_points = data.get("risk_points", DEFAULT_RISK_POINTS)
    if not isinstance(risk_points, list):
        risk_points = DEFAULT_RISK_POINTS
    # Ensure at least one risk point
    if not risk_points:
        risk_points = DEFAULT_RISK_POINTS
    result["risk_points"] = [str(item).strip() for item in risk_points if str(item).strip()]

    # Process suggestions
    suggestions = data.get("suggestions", DEFAULT_SUGGESTIONS)
    if not isinstance(suggestions, list):
        suggestions = DEFAULT_SUGGESTIONS
    # Ensure at least two suggestions
    if len(suggestions) < 2:
        suggestions = DEFAULT_SUGGESTIONS
    result["suggestions"] = [str(item).strip() for item in suggestions if str(item).strip()]

    # Process next_step
    next_step = data.get("next_step", DEFAULT_NEXT_STEP)
    if not next_step or not isinstance(next_step, str):
        next_step = DEFAULT_NEXT_STEP
    result["next_step"] = next_step.strip()

    # Remove prohibited fields
    for field in PROHIBITED_FIELDS:
        result.pop(field, None)

    # Remove any extra fields that shouldn't be there
    allowed_fields = set(REQUIRED_FIELDS)
    for key in list(result.keys()):
        if key not in allowed_fields:
            del result[key]

    return result