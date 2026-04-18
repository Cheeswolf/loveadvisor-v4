"""
LoveAdvisor V3 - S2 Response Parser
Phase 3: S2/S3 Localization Migration

This module parses and validates S2 (signal extraction) LLM responses.
It extracts structured signal data from LLM JSON outputs.

Features:
- Parse raw LLM response string or dictionary
- Extract JSON from text using regex fallback
- Provide default values for missing fields
- Fallback illegal enum values to "无法判断"
- Ensure key_signals is always a list
- Return stable dict structure
"""

import json
import re
from typing import Dict, Any, Union, List
import logging

from app.utils.json_utils import extract_json_from_text

logger = logging.getLogger(__name__)

# Valid enum values for each field (from S2 prompt)
VALID_INITIATIVE = {"A更主动", "B更主动", "双方接近", "无法判断"}
VALID_RESPONSE_LENGTH = {"短", "中", "长", "无法判断"}
VALID_EMOTIONAL_TONE = {"热", "温", "冷", "无法判断"}
VALID_TOPIC_DEPTH = {"浅", "中", "深", "无法判断"}
VALID_INTERACTION_RECIPROCITY = {"正向承接", "弱承接", "明显回避", "无法判断"}

# Default values for each field (used when missing)
DEFAULT_INITIATIVE = "无法判断"
DEFAULT_RESPONSE_LENGTH = "无法判断"
DEFAULT_EMOTIONAL_TONE = "无法判断"
DEFAULT_TOPIC_DEPTH = "无法判断"
DEFAULT_INTERACTION_RECIPROCITY = "无法判断"
DEFAULT_KEY_SIGNALS = []

# Compatibility mapping for legacy or variant values
COMPATIBILITY_MAPPING = {
    # initiative mappings
    "A 更主动": "A更主动",
    "B 更主动": "B更主动",
    "A更主动": "A更主动",  # identity mapping for consistency
    "B更主动": "B更主动",
    "双方接近": "双方接近",
    "无法判断": "无法判断",
    # response_length mappings (if any variants exist)
    "短": "短",
    "中": "中",
    "长": "长",
    # emotional_tone mappings
    "热": "热",
    "温": "温",
    "冷": "冷",
    # topic_depth mappings
    "浅": "浅",
    "中": "中",
    "深": "深",
    # interaction_reciprocity mappings
    "正向承接": "正向承接",
    "弱承接": "弱承接",
    "明显回避": "明显回避",
}


def parse_s2_response(llm_response: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Parse S2 LLM response into structured signal data.

    Args:
        llm_response: Raw LLM response text or parsed dictionary.

    Returns:
        Parsed signal data dictionary with guaranteed structure.

    Notes:
        - If input is a dict, it's used directly (with validation)
        - If input is a string, JSON is extracted using regex fallback
        - Missing fields are filled with defaults
        - Invalid enum values are replaced with "无法判断"
        - key_signals is always converted to list (empty list if missing)
    """
    parsed_dict = _extract_json_from_response(llm_response)
    normalized = _normalize_s2_data(parsed_dict)
    validated = _validate_and_fix_s2_data(normalized)
    return validated


def validate_s2_signals(parsed_data: Dict[str, Any]) -> bool:
    """
    Validate parsed S2 signal data.

    Args:
        parsed_data: Parsed signal data dictionary.

    Returns:
        True if data passes basic validation, False otherwise.
    """
    required_fields = [
        "initiative",
        "response_length",
        "emotional_tone",
        "topic_depth",
        "interaction_reciprocity",
        "key_signals"
    ]

    # Check presence
    for field in required_fields:
        if field not in parsed_data:
            logger.warning(f"S2 validation: missing field {field}")
            return False

    # Check types
    if not isinstance(parsed_data["key_signals"], list):
        logger.warning("S2 validation: key_signals is not a list")
        return False

    # Check enum values (warning only, not failure)
    if parsed_data["initiative"] not in VALID_INITIATIVE:
        logger.warning(f"S2 validation: invalid initiative value {parsed_data['initiative']}")

    if parsed_data["response_length"] not in VALID_RESPONSE_LENGTH:
        logger.warning(f"S2 validation: invalid response_length value {parsed_data['response_length']}")

    if parsed_data["emotional_tone"] not in VALID_EMOTIONAL_TONE:
        logger.warning(f"S2 validation: invalid emotional_tone value {parsed_data['emotional_tone']}")

    if parsed_data["topic_depth"] not in VALID_TOPIC_DEPTH:
        logger.warning(f"S2 validation: invalid topic_depth value {parsed_data['topic_depth']}")

    if parsed_data["interaction_reciprocity"] not in VALID_INTERACTION_RECIPROCITY:
        logger.warning(f"S2 validation: invalid interaction_reciprocity value {parsed_data['interaction_reciprocity']}")

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


def _normalize_s2_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize data types and structure."""
    normalized = data.copy()

    # Ensure key_signals is a list
    if "key_signals" in normalized:
        if isinstance(normalized["key_signals"], str):
            # Try to parse as JSON array, otherwise wrap as single element list
            try:
                parsed = json.loads(normalized["key_signals"])
                if isinstance(parsed, list):
                    normalized["key_signals"] = parsed
                else:
                    normalized["key_signals"] = [str(parsed)]
            except (json.JSONDecodeError, TypeError):
                normalized["key_signals"] = [normalized["key_signals"]]
        elif not isinstance(normalized["key_signals"], list):
            normalized["key_signals"] = []
    else:
        normalized["key_signals"] = []

    # Convert all key_signal elements to strings
    normalized["key_signals"] = [str(signal) for signal in normalized["key_signals"]]

    return normalized


def _validate_and_fix_s2_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Apply validation rules and fix invalid values."""
    # Normalize values using compatibility mapping
    normalized_data = data.copy()
    for field in ["initiative", "response_length", "emotional_tone", "topic_depth", "interaction_reciprocity"]:
        if field in normalized_data:
            value = normalized_data[field]
            if isinstance(value, str):
                # Apply compatibility mapping if exists, otherwise keep original
                normalized_data[field] = COMPATIBILITY_MAPPING.get(value, value)

    result = {
        "initiative": normalized_data.get("initiative", DEFAULT_INITIATIVE),
        "response_length": normalized_data.get("response_length", DEFAULT_RESPONSE_LENGTH),
        "emotional_tone": normalized_data.get("emotional_tone", DEFAULT_EMOTIONAL_TONE),
        "topic_depth": normalized_data.get("topic_depth", DEFAULT_TOPIC_DEPTH),
        "interaction_reciprocity": normalized_data.get("interaction_reciprocity", DEFAULT_INTERACTION_RECIPROCITY),
        "key_signals": normalized_data.get("key_signals", DEFAULT_KEY_SIGNALS),
    }

    # Fix invalid enum values
    if result["initiative"] not in VALID_INITIATIVE:
        result["initiative"] = DEFAULT_INITIATIVE

    if result["response_length"] not in VALID_RESPONSE_LENGTH:
        result["response_length"] = DEFAULT_RESPONSE_LENGTH

    if result["emotional_tone"] not in VALID_EMOTIONAL_TONE:
        result["emotional_tone"] = DEFAULT_EMOTIONAL_TONE

    if result["topic_depth"] not in VALID_TOPIC_DEPTH:
        result["topic_depth"] = DEFAULT_TOPIC_DEPTH

    if result["interaction_reciprocity"] not in VALID_INTERACTION_RECIPROCITY:
        result["interaction_reciprocity"] = DEFAULT_INTERACTION_RECIPROCITY

    # Ensure key_signals is a list (already normalized, but double-check)
    if not isinstance(result["key_signals"], list):
        result["key_signals"] = DEFAULT_KEY_SIGNALS

    # Remove any extra fields that shouldn't be there
    allowed_fields = set(result.keys())
    for key in list(result.keys()):
        if key not in allowed_fields:
            del result[key]

    # Special restriction:绝对不能包含 relationship_stage 和 interest_level
    result.pop("relationship_stage", None)
    result.pop("interest_level", None)

    return result