"""
LoveAdvisor V3 - S3 Response Parser
Phase 3: S2/S3 Localization Migration

This module parses and validates S3 (signal summary) LLM responses.
It extracts structured summary data from LLM JSON outputs.

Features:
- Parse raw LLM response string or dictionary
- Extract JSON from text using regex fallback
- Convert all boolean fields to bool type
- Provide default false for missing boolean fields
- Ensure signal_summary is always a list
- Return stable dict structure
"""

import json
import re
from typing import Dict, Any, Union, List
import logging

from app.utils.json_utils import extract_json_from_text

logger = logging.getLogger(__name__)

# Boolean field names (from S3 prompt)
BOOLEAN_FIELDS = {
    "has_intimacy_signal",
    "has_relationship_probe",
    "has_positive_reciprocity",
    "has_rejection_signal",
    "has_push_pull_pattern",
    "has_sustained_coldness"
}

ALL_FIELDS = BOOLEAN_FIELDS | {"signal_summary"}

# Default values
DEFAULT_BOOLEAN = False
DEFAULT_SIGNAL_SUMMARY = []


def parse_s3_response(llm_response: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Parse S3 LLM response into structured summary data.

    Args:
        llm_response: Raw LLM response text or parsed dictionary.

    Returns:
        Parsed summary data dictionary with guaranteed structure.

    Notes:
        - If input is a dict, it's used directly (with validation)
        - If input is a string, JSON is extracted using regex fallback
        - Missing boolean fields default to false
        - All boolean fields are converted to bool type
        - signal_summary is always converted to list (empty list if missing)
    """
    parsed_dict = _extract_json_from_response(llm_response)
    normalized = _normalize_s3_data(parsed_dict)
    validated = _validate_and_fix_s3_data(normalized)
    return validated


def validate_s3_summary(parsed_data: Dict[str, Any]) -> bool:
    """
    Validate parsed S3 summary data.

    Args:
        parsed_data: Parsed summary data dictionary.

    Returns:
        True if data passes basic validation, False otherwise.
    """
    # Check required fields exist
    for field in ALL_FIELDS:
        if field not in parsed_data:
            logger.warning(f"S3 validation: missing field {field}")
            return False

    # Check boolean fields are actually boolean
    for field in BOOLEAN_FIELDS:
        if not isinstance(parsed_data[field], bool):
            logger.warning(f"S3 validation: field {field} is not bool")
            return False

    # Check signal_summary is a list
    if not isinstance(parsed_data["signal_summary"], list):
        logger.warning("S3 validation: signal_summary is not a list")
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


def _normalize_s3_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize data types and structure."""
    normalized = data.copy()

    # Ensure signal_summary is a list
    if "signal_summary" in normalized:
        if isinstance(normalized["signal_summary"], str):
            # Try to parse as JSON array, otherwise wrap as single element list
            try:
                parsed = json.loads(normalized["signal_summary"])
                if isinstance(parsed, list):
                    normalized["signal_summary"] = parsed
                else:
                    normalized["signal_summary"] = [str(parsed)]
            except (json.JSONDecodeError, TypeError):
                normalized["signal_summary"] = [normalized["signal_summary"]]
        elif not isinstance(normalized["signal_summary"], list):
            normalized["signal_summary"] = []
    else:
        normalized["signal_summary"] = []

    # Convert all signal_summary elements to strings
    normalized["signal_summary"] = [str(item) for item in normalized["signal_summary"]]

    return normalized


def _validate_and_fix_s3_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Apply validation rules and fix invalid values."""
    result = {}

    # Process boolean fields
    for field in BOOLEAN_FIELDS:
        value = data.get(field, DEFAULT_BOOLEAN)
        # Convert to bool using Python's truthiness
        if isinstance(value, bool):
            result[field] = value
        elif isinstance(value, (int, float)):
            result[field] = bool(value)
        elif isinstance(value, str):
            value_lower = value.lower()
            if value_lower in ("true", "yes", "1", "是", "真"):
                result[field] = True
            elif value_lower in ("false", "no", "0", "否", "假"):
                result[field] = False
            else:
                # Try to interpret as bool via JSON
                try:
                    parsed = json.loads(value_lower)
                    result[field] = bool(parsed)
                except (json.JSONDecodeError, TypeError):
                    # Default to false for unrecognized strings
                    result[field] = DEFAULT_BOOLEAN
        else:
            result[field] = DEFAULT_BOOLEAN

    # Process signal_summary
    result["signal_summary"] = data.get("signal_summary", DEFAULT_SIGNAL_SUMMARY)
    if not isinstance(result["signal_summary"], list):
        result["signal_summary"] = DEFAULT_SIGNAL_SUMMARY

    # Remove any extra fields that shouldn't be there
    allowed_fields = set(ALL_FIELDS)
    for key in list(result.keys()):
        if key not in allowed_fields:
            del result[key]

    # Special restriction:绝对不能包含 relationship_stage 和 interest_level
    result.pop("relationship_stage", None)
    result.pop("interest_level", None)

    return result