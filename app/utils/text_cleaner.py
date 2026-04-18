"""
Text cleaning utilities for LoveAdvisor V3.
Extracted from PreprocessService to avoid circular imports.
"""

import re
from typing import Optional


def clean_chat_text(text: str) -> str:
    """
    Clean chat text while preserving speaker labels (A:/B: and A：/B： formats).

    Args:
        text: Raw chat text.

    Returns:
        Cleaned chat text with speaker labels preserved.
    """
    if not text or not isinstance(text, str):
        return ""

    # Preserve original text but normalize whitespace
    # Remove extra whitespace but keep line breaks
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if line:
            # Check if line starts with speaker pattern (A:, B:, A：, B：)
            # If yes, ensure there's a space after colon if missing
            # This preserves the original format
            cleaned_lines.append(line)

    # Rejoin lines with single newline
    cleaned = '\n'.join(cleaned_lines)

    # If cleaning resulted in empty string, return original text (trimmed)
    if not cleaned:
        return text.strip()

    return cleaned


def clean_text(text: str) -> str:
    """
    Clean and normalize general text.

    Args:
        text: Raw user input text.

    Returns:
        Cleaned text.
    """
    # Remove extra whitespace
    cleaned = re.sub(r'\s+', ' ', text.strip())

    # TODO: Add more cleaning steps (URLs, emojis, special characters, etc.)

    # Ensure we don't delete all text
    if not cleaned:
        return text.strip() if text.strip() else text

    return cleaned


def detect_language(text: str) -> str:
    """
    Detect the language of the input text.

    Args:
        text: Input text.

    Returns:
        Detected language code (e.g., 'zh', 'en').
    """
    # TODO: Implement language detection
    # For now, assume Chinese if Chinese characters present
    if re.search(r'[\u4e00-\u9fff]', text):
        return "zh"
    else:
        return "en"


def check_sensitive_info(text: str) -> bool:
    """
    Check if text contains sensitive personal information.

    Args:
        text: Input text.

    Returns:
        True if sensitive information detected, False otherwise.
    """
    # TODO: Implement sensitive information detection
    # Patterns for phone numbers, IDs, addresses, etc.
    phone_pattern = r'\b\d{3}[-.]?\d{4}[-.]?\d{4}\b'
    if re.search(phone_pattern, text):
        return True

    return False