"""
LoveAdvisor V3 - JSON Utilities
Phase 1: Engineering Skeleton Initialization

This module provides utilities for working with JSON data,
including safe parsing, extraction from text, and validation.
"""

import json
import re
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class JSONEncodeError(Exception):
    """Exception raised when JSON encoding fails."""
    pass


class JSONDecodeError(Exception):
    """Exception raised when JSON decoding fails."""
    pass


def safe_json_loads(
    json_str: str,
    default: Any = None,
    log_errors: bool = True
) -> Any:
    """
    Safely parse JSON string with error handling.

    Args:
        json_str: JSON string to parse.
        default: Value to return if parsing fails.
        log_errors: Whether to log parsing errors.

    Returns:
        Parsed JSON object or default value.
    """
    if not json_str or not isinstance(json_str, str):
        if log_errors:
            logger.debug(f"Invalid JSON string input: {type(json_str)}")
        return default

    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError) as e:
        if log_errors:
            logger.warning(f"Failed to parse JSON: {e}\nString: {json_str[:200]}")
        return default


def safe_json_dumps(
    obj: Any,
    default: Any = None,
    indent: Optional[int] = None,
    ensure_ascii: bool = False,
    log_errors: bool = True
) -> str:
    """
    Safely serialize object to JSON string.

    Args:
        obj: Object to serialize.
        default: Value to return if serialization fails.
        indent: JSON indentation level.
        ensure_ascii: Whether to escape non-ASCII characters.
        log_errors: Whether to log serialization errors.

    Returns:
        JSON string or default value.
    """
    if default is None:
        default = "{}"

    try:
        return json.dumps(
            obj,
            indent=indent,
            ensure_ascii=ensure_ascii,
            default=_json_serializer
        )
    except (TypeError, ValueError) as e:
        if log_errors:
            logger.warning(f"Failed to serialize to JSON: {e}\nObject type: {type(obj)}")
        return default


def extract_json_from_text(
    text: str,
    max_attempts: int = 3
) -> Optional[Dict[str, Any]]:
    """
    Extract JSON object from text that may contain other content.

    Args:
        text: Text potentially containing JSON.
        max_attempts: Maximum number of extraction attempts.

    Returns:
        Extracted JSON dictionary or None.
    """
    if not text:
        return None

    # Attempt 1: Try parsing the entire text as JSON
    result = safe_json_loads(text, default=None, log_errors=False)
    if result is not None:
        return result

    # Attempt 2: Look for JSON object pattern
    json_pattern = r'\{[^{}]*\{[^{}]*\}[^{}]*\}|\{[^{}]*\}'
    matches = re.findall(json_pattern, text, re.DOTALL)

    for match in matches:
        result = safe_json_loads(match, default=None, log_errors=False)
        if result is not None:
            return result

    # Attempt 3: Look for array pattern
    array_pattern = r'\[[^\[\]]*\[[^\[\]]*\][^\[\]]*\]|\[[^\[\]]*\]'
    matches = re.findall(array_pattern, text, re.DOTALL)

    for match in matches:
        result = safe_json_loads(match, default=None, log_errors=False)
        if result is not None:
            return result

    # Attempt 4: Try to fix common JSON issues
    if max_attempts > 0:
        # Try to fix unescaped quotes
        fixed_text = _fix_json_common_issues(text)
        if fixed_text != text:
            return extract_json_from_text(fixed_text, max_attempts - 1)

    return None


def validate_json_schema(
    data: Dict[str, Any],
    schema: Dict[str, Any],
    strict: bool = False
) -> List[str]:
    """
    Validate JSON data against a simple schema.

    Note: This is a basic schema validator. For complex schemas,
    consider using a dedicated library like jsonschema.

    Args:
        data: JSON data to validate.
        schema: Schema definition.
        strict: Whether to require exact field matches.

    Returns:
        List of validation errors (empty if valid).
    """
    errors = []

    if not isinstance(data, dict):
        return ["Data must be a dictionary"]

    for key, expected_type in schema.items():
        if key not in data:
            errors.append(f"Missing required field: {key}")
            continue

        value = data[key]
        if not _check_type(value, expected_type):
            errors.append(f"Field '{key}' has wrong type. Expected {expected_type}, got {type(value)}")

    if strict:
        extra_keys = set(data.keys()) - set(schema.keys())
        if extra_keys:
            errors.append(f"Unexpected fields: {', '.join(extra_keys)}")

    return errors


def merge_json(
    base: Dict[str, Any],
    overlay: Dict[str, Any],
    overwrite: bool = True
) -> Dict[str, Any]:
    """
    Merge two JSON objects recursively.

    Args:
        base: Base JSON object.
        overlay: Overlay JSON object to merge.
        overwrite: Whether to overwrite existing values.

    Returns:
        Merged JSON object.
    """
    result = base.copy()

    for key, value in overlay.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Recursive merge for nested dictionaries
            result[key] = merge_json(result[key], value, overwrite)
        elif key not in result or overwrite:
            # Add new key or overwrite existing
            result[key] = value
        # If key exists and overwrite=False, keep the existing value

    return result


def _json_serializer(obj: Any) -> Any:
    """
    Custom JSON serializer for unsupported types.

    Args:
        obj: Object to serialize.

    Returns:
        JSON-serializable representation.

    Raises:
        TypeError: If object cannot be serialized.
    """
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        return float(obj)
    elif hasattr(obj, '__dict__'):
        return obj.__dict__
    elif hasattr(obj, 'to_dict'):
        return obj.to_dict()
    else:
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def _check_type(value: Any, expected_type: Any) -> bool:
    """
    Check if value matches expected type.

    Args:
        value: Value to check.
        expected_type: Expected type or type specification.

    Returns:
        True if type matches.
    """
    if expected_type == "any":
        return True

    if isinstance(expected_type, list):
        # Union type (e.g., ["string", "null"])
        return any(_check_type(value, t) for t in expected_type)

    if expected_type == "string":
        return isinstance(value, str)
    elif expected_type == "number":
        return isinstance(value, (int, float))
    elif expected_type == "integer":
        return isinstance(value, int)
    elif expected_type == "boolean":
        return isinstance(value, bool)
    elif expected_type == "array":
        return isinstance(value, list)
    elif expected_type == "object":
        return isinstance(value, dict)
    elif expected_type == "null":
        return value is None
    else:
        # Assume it's a Python type
        return isinstance(value, expected_type)


def _fix_json_common_issues(text: str) -> str:
    """
    Fix common JSON formatting issues.

    Args:
        text: Text with potential JSON issues.

    Returns:
        Fixed text.
    """
    if not text:
        return text

    # Fix unescaped quotes inside strings (basic fix)
    # This is a simple heuristic and may not handle all cases
    lines = text.split('\n')
    fixed_lines = []

    for line in lines:
        # Count quotes to identify potential issues
        quote_count = line.count('"')
        if quote_count % 2 != 0:
            # Odd number of quotes - try to fix
            line = line.replace('"', "'")
        fixed_lines.append(line)

    return '\n'.join(fixed_lines)