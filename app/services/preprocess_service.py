"""
LoveAdvisor V3 - Preprocess Service
Phase 1: Engineering Skeleton Initialization

This service cleans and enriches user input before signal extraction.
It handles text normalization, context enrichment, and preparation for
downstream processing.
"""

import re
from typing import Dict, Any

from app.core.runtime_context import RuntimeContext
from app.utils.text_cleaner import clean_text, clean_chat_text, detect_language, check_sensitive_info


class PreprocessService:
    """
    Service for preprocessing user input.

    Responsibilities:
    1. Text cleaning (remove noise, normalize formatting)
    2. Context enrichment (add metadata, infer missing information)
    3. Input validation (check length, language, appropriateness)
    4. Preparation for signal extraction
    """

    async def execute(self, context: RuntimeContext) -> Dict[str, Any]:
        """
        Execute preprocessing on the user input.

        Args:
            context: Runtime context containing user input and configuration.

        Returns:
            Dictionary containing cleaned text and enriched context.
        """
        # TODO: Implement actual preprocessing logic
        cleaned_text = self._clean_text(context.user_input)
        cleaned_chat_text = self._clean_chat_text(context.user_input)
        enriched_context = self._enrich_context(context.user_context)

        return {
            "cleaned_text": cleaned_text,
            "cleaned_chat_text": cleaned_chat_text,  # debug field
            "enriched_context": enriched_context,
            "original_length": len(context.user_input),
            "cleaned_length": len(cleaned_text),
            "language": self._detect_language(context.user_input),
            "contains_sensitive_info": self._check_sensitive_info(context.user_input),
        }

    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text.

        Args:
            text: Raw user input text.

        Returns:
            Cleaned text.
        """
        return clean_text(text)

    def _enrich_context(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich user-provided context with inferred information.

        Args:
            user_context: User-provided context dictionary.

        Returns:
            Enriched context dictionary.
        """
        enriched = user_context.copy()

        # TODO: Infer missing context (gender, age, relationship status, etc.)
        if "gender" not in enriched:
            enriched["gender_inferred"] = "unknown"
        if "age" not in enriched:
            enriched["age_range_inferred"] = "unknown"

        return enriched

    def _detect_language(self, text: str) -> str:
        """
        Detect the language of the input text.

        Args:
            text: Input text.

        Returns:
            Detected language code (e.g., 'zh', 'en').
        """
        return detect_language(text)

    def _check_sensitive_info(self, text: str) -> bool:
        """
        Check if text contains sensitive personal information.

        Args:
            text: Input text.

        Returns:
            True if sensitive information detected, False otherwise.
        """
        return check_sensitive_info(text)

    def _clean_chat_text(self, text: str) -> str:
        """
        Clean chat text while preserving speaker labels (A:/B: and A：/B： formats).

        Args:
            text: Raw chat text.

        Returns:
            Cleaned chat text with speaker labels preserved.
        """
        return clean_chat_text(text)